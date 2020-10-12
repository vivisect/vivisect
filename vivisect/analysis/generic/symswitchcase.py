'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases from Microsoft and GCC, and theoretically others,
which use pointer arithetic to determine code path for each case.

This will not connect switch cases which are actually explicit cmp/jz in the code.
'''
import sys

import logging
logger = logging.getLogger(__name__)
#logger.setLevel(logging.WARN)
#logger.setLevel(logging.DEBUG)
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())

import envi
import envi.bits as e_bits
import envi.archs.i386 as e_i386

import vivisect
import vivisect.exc as v_exc
import vivisect.cli as viv_cli
import vivisect.tools.graphutil as viv_graph
import vivisect.symboliks.emulator as vs_emu
import vivisect.symboliks.analysis as vs_anal
import vivisect.symboliks.substitution as vs_sub
import vivisect.analysis.generic.codeblocks as vagc

from vivisect.symboliks.common import *
from vivisect.tools.graphutil import PathForceQuitException


'''
this analysis module takes a two stage approach to identifying and wiring up switch cases.

the first phase is to identify the index range for the switch-case.  many switch cases are
split into logically grouped cases, such as if the case statements are "1,2,3,4,5,6,7,10,1000,
1001,1002,1005,2000,...." the compiler might break this up into three distinct dynamic branches,
one to handle the cases 1-10, another for the 1001-1005, and another to handle the 2000's.  this
first "discovery" phase identifies how many cases are handled in a given dynamic branch, as well
as the offset.  thus, for the 1000's, there may be 5 cases, and their offset would be 1001.

the second phase actually wires up the switch case instance, providing new codeflow analysis where
necessary, new codeblocks, and xrefs from the dynamic branch to the case handling code.  at the
end, names are applied as appropriate.
'''

# FIXME: some cases set the non-index reg much higher up the chain, so we don't identify the case index
# TODO: make all switchcase analysis for a given function cohesive (ie. don't finish up with naming until the entire function has been analyzed).  this will break cohesion if we use the CLI to add switchcases, but so be it.
# TODO: overlapping case names...  doublecheck the naming algorithm.  ahh... different switch-cases colliding on handlers?  is this legit?  or is it because we don't stop correctly?
# CHECK: are the algorithms for "stopping" correct?  currently getting 1 switch case for several cases in libc-32
# TODO: regrange description of Symbolik Variables... normalize so "eax" and "eax+4" make sense.
# TODO: complete documentation
MAX_INSTR_COUNT  = 10
MAX_CASES   = 500
CASE_FAILURE = 5000
MIN_FUNC_INSTR_SIZE = 10


class SymIdxNotFoundException(Exception):
    def __repr__(self):
        return "getSymIdx cannot determine the Index register"


class TrackingSymbolikEmulator(vs_anal.SymbolikFunctionEmulator):
    '''
    TrackingSymbolikEmulator tracks reads.  where they occur, where they read from, and
    returns as much info as possible if not discrete data.

    If a read is from a real memory map, return that memory.
    '''
    def __init__(self, vw):
        vs_anal.SymbolikFunctionEmulator.__init__(self, vw)
        self.__width__ = vw.psize
        self.clear()

    def clear(self):
        self._trackReads = []
        
    def track(self, va, addrval, val):
        self._trackReads.append((va, addrval, val))
        
    def getTrackInfo(self):
        return self._trackReads

    def setupFunctionCall(self, fva, args=None):
        logger.warn("setupFunctionCall: SKIPPING!")
        pass
        
    def readSymMemory(self, symaddr, symsize, vals=None):
        '''
        The readSymMemory API is designed to read from the given
        symbolik address for the specified symbolik length.  If the
        current symbolik emulator has no knowledge of the state of
        the given memory symbol, None is returned.
        '''
        addrval = symaddr.update(self).solve(emu=self, vals=vals)
        logger.debug('   TSE.readSymMemory: symaddr:%r  addrval:0x%x symsize:%s',symaddr, addrval, symsize)
        
        # check for a previous write first...
        symmem = self._sym_mem.get(addrval)
        if symmem is not None:
            symaddr, symval = symmem
            self.track(self.getMeta('va'), symaddr, symval)
            return symval

        # If we have a workspace, check it for meaningful symbols etc...
        if self._sym_vw is not None:
            # Make a special check for imports...
            loc = self._sym_vw.getLocation(addrval)
            if loc is not None:
                lva, lsize, ltype, linfo = loc
                if ltype == vivisect.LOC_IMPORT:
                    # return name of import
                    symval = Var(linfo, self.__width__)
                    self.track(self.getMeta('va'), symaddr, symval)
                    return symval
            
            if self._sym_vw.isValidPointer(addrval):        
                if symsize.isDiscrete():
                    size = symsize.solve()
                else:
                    size = symsize
                    
                if size in (1, 2, 4, 8):
                    # return real number from memory
                    fmt = e_bits.getFormat(size, self._sym_vw.getEndian(), signed=True)
                    val, = self._sym_vw.readMemoryFormat(addrval, fmt)
                    self.track(self.getMeta('va'), symaddr, val)
                    return Const(val, size)
                
                # return string  (really?)
                symval = self._sym_vw.readMemory(addrval, size)
                self.track(self.getMeta('va'), symaddr, symval)
                return symval

        return Mem(symaddr, symsize)


def contains(symobj, subobj):
    '''
    search through an AST looking for a particular type of thing.

    args:
        symobj - the AST to walk through
        subobj - the value to compare against (symobj.solve())

    returns:
        contains - whether or not the AST contains the sought value
        path - the operator path to get to that object (last one seen)
    '''
    def _cb_contains(path, symobj, ctx):
        '''
        walkTree callback for determining presence within an AST
        '''
        symsolve = symobj.solve()
        # print "==--==", repr(symobj), symsolve, ctx['compare']
        if symsolve == ctx['compare']:
            ctx['contains'] = True
            ctx['path'] = tuple(path)

        return symobj

    ctx = {'compare':   subobj.solve(),
           'contains':  False,
           'path':      []
           }

    symobj.walkTree(_cb_contains, ctx)
    return ctx.get('contains'), ctx['path']


def getMemTargets(symvar):
    # determine locations read from
    def _cb_grab_mem(path, symobj, ctx):
        '''
        walkTree callback for grabbing Var objects
        '''
        logger.debug("... memtgt: %r", symobj)
        if symobj.symtype == SYMT_MEM:
            tgt = symobj.kids[0]
            if tgt not in ctx:
                ctx.append(tgt)

    unks = []
    symvar.walkTree(_cb_grab_mem, unks)
    return unks


def getUnknowns(symvar):
    '''
    determine unknown registers in this symbolik object
    '''
    def _cb_grab_vars(path, symobj, ctx):
        '''
        walkTree callback for grabbing Var objects
        '''
        logging.debug("... unk: %r", symobj)
        if symobj.symtype == SYMT_VAR:
            if symobj.name not in ctx:
                ctx.append(symobj.name)

    unks = []
    symvar.walkTree(_cb_grab_vars, unks)
    return unks


def peelIdxOffset(symobj):
    '''
    Peel back ignorable wrapped layers of a symbolik Index register, and track
    offset in the process.  Once we've skipped out of the ignorable 
    '''
    offset = 0
    while True:
        # peel off o_subs and size-limiting o_ands and o_sextends
        if isinstance(symobj, o_and) and symobj.kids[1].isDiscrete() and symobj.kids[1].solve() in e_bits.u_maxes:
            # this wrapper is a size-limiting bitmask
            pass

        elif isinstance(symobj, o_sub):
            # this is an offset, used to rebase the index into a different pointer array
            offset += symobj.kids[1].solve()

        elif isinstance(symobj, o_add):
            # this is an offset, used to rebase the index into a different pointer array
            offset -= symobj.kids[1].solve()

        elif isinstance(symobj, o_sextend):
            # sign-extension is irrelevant for indexes
            pass

        # anything else and we're done peeling
        else:
            break

        # this algorithm depends on only taking left turns
        symobj = symobj.kids[0]

    return symobj, offset

def targetNewFunctions(vw, fva):
    '''
    scan through all direct calls in this function and force analysis of called functions
    if this is too cumbersome, we'll just do the first one, or any in the first codeblock
    '''
    done = []
    todo = list(vw.getFunctionBlocks(fva))

    while len(todo):
        cbva, cbsz, cbfva = todo.pop()
        endva = cbva + cbsz
        while cbva < endva:
            try:
                op = vw.parseOpcode(cbva)

            except:
                logger.warn('failed to parse opcode within function at 0x%x (fva: 0x%x)', cbva, fva)
                cbva += 1
                continue

            for xrfr, xrto, xrt, xrflag in vw.getXrefsFrom(cbva):
                if not (op.iflags & envi.IF_CALL):
                    continue

                tgtva = op.getOperValue(0)
                #logger.debug("-- 0x%x", tgtva)
                if not vw.isValidPointer(tgtva):
                    continue

                if vw.getFunction(tgtva) is not None:
                    continue

                if tgtva in done:
                    continue
                done.append(tgtva)

                logger.warn('Making new function: 0x%x (from 0x%x)', tgtva, xrfr)
                vw.makeFunction(tgtva)

            cbva += len(op)



def thunk_bx(emu, fname, symargs):
    vw = emu._sym_vw
    rctx = vw.arch.archGetRegCtx()
    ebxval = emu.getMeta('calling_va')
    oploc = vw.getLocation(ebxval)
    if oploc is None:
        ebxval += 5
    else:
        ebxval += oploc[L_SIZE]

    ebx = Const(ebxval, vw.psize)
    reg = rctx.getRealRegisterName('ebx')
    logger.debug("YAY!  Thunk_bx is being called! %s\t%s\t%s\t%s", emu, symargs, reg, ebx)
    emu.setSymVariable(reg, ebx)

UNINIT_CASE_INDEX = -2

class SwitchCase:
    # FIXME: enhance "don't analyze" checks (like, already analyzed?)  or no?
    # FIXME: collisions in named targets... shared between jmp's in same switch/function
    # FIXME: thunk_bx needs to already be called on the thunk_bx functions *before* switchcase analysis can occur.  current setup doesn't guarantee that. ordering?  or we need to rewrite thunk_bx analysis to run during calling-function's analysis pass (during codeflow?) to analyze the functions being called...
    def __init__(self, vw, jmpva):
        self.vw = vw
        self.jmpva = jmpva
        self.op = vw.parseOpcode(jmpva)
        logger.info('=== 0x%x: %r ===' % (jmpva, self.op))

        self.sctx = vs_anal.getSymbolikAnalysisContext(vw)
        self.xlate = self.sctx.getTranslator()

        # 32-bit i386 thunk_bx handling.  this should be the only oddity for this architecture
        #if vw.getMeta('PIE_ebx'):
        try:
            for tva, in vw.getVaSetRows('thunk_bx'):
                fname = vw.getName(tva, True)
                self.sctx.addSymFuncCallback(fname, thunk_bx)
                logger.debug( "sctx.addSymFuncCallback(%s, thunk_bx)" % fname)
        except AttributeError:
            pass
        except v_exc.InvalidVaSet:
            pass


        self._sgraph = None
        self._codepath = None
        self._codepathgen = None

        self.clearCache()



    def clearCache(self):
        self.cspath = None
        self.aspath = None
        self.fullpath = None

        self.upper = None
        self.lower = None
        self.count = None
        self.baseoff = None
        self.baseIdx = None

        # 
        '''
        self.longSemu = TrackingSymbolikEmulator(vw)
        self.shortSemu = TrackingSymbolikEmulator(vw)

        self.idxregidx = None
        self.idxregname = None
        self.idxregsymbx = None

        self.jmpregidx = None
        self.jmpregname = None
        '''
        self.jmpregsymbx = None


    def analyze(self):
        self.makeSwitch()

    #### primitives for switchcase analysis ####
    def getJmpSymVar(self):
        '''
        returns the Simple Symbolik state of the dynamic target of the branch/jmp
        this is the symbolik register at the start of the last codeblock.
        '''
        if self.jmpregsymbx is not None:
            return self.jmpregsymbx

        op = self.vw.parseOpcode(self.jmpva)

        self.jmpregsymbx = self.xlate.getOperObj(op, 0)
        return self.jmpregsymbx

    def getSymTarget(self, short=True):
        '''
        Returns the Symbolik state of the dynamic target of the branch/jmp
        short indicates just in the context of the last codeblock.
        not short indicates the context at the start of the last codeblock (from funcva)
        '''
        jmpsymvar = self.getJmpSymVar()

        cspath, aspath, fullpath = self.getSymbolikParts()
        emu = (cspath[0], aspath[0])[short]
        tgtsym = jmpsymvar.update(emu)
        return tgtsym


    def getSymIdx(self):
        '''
        returns the symbolik index register
        '''
        symtgt = self.getSymTarget()
        unks = getUnknowns(symtgt)

        cspath, aspath, fullpath = self.getSymbolikParts()

        potentials = []
        for unk in unks:
            unkvar = cspath[0].getSymVariable(unk)
            if unkvar.isDiscrete():
                continue
            potentials.append(unk)

        if not len(potentials):
            #logger.critical('=-=-=-= failed to getSymIdx: unks: %r\n\nCSPATH:\n%s\n\nASPATH:\n%s\n\n',
            #        unks, 
            #        '\n'.join([repr(x) for x in cspath[1]]), 
            #        '\n'.join([repr(x) for x in aspath[1]]))
            raise SymIdxNotFoundException(cspath, aspath)
            
        return potentials[0]

    def getCountOffset(self):
        '''
        Limited value function.
        '''
        lower, upper, offset = self.getBounds()
        if None in (lower, upper): 
            logger.info("something odd in count/offset calculation... skipping 0x%x...", self.jmpva)
            return
        return (upper-lower+1), offset+lower


    def getConstraints(self):
        csp, asp, fullp = self.getSymbolikParts()

        cons = [eff for eff in fullp[1] if eff.efftype==EFFTYPE_CONSTRAIN]
        [con.reduce() for con in cons]
        return cons

    def getSymbolikParts(self, next=False):
        '''
        Puts together a path from the start of the function to the jmpva, breaking off the last 
        codeblock, and returning the symbolik path for both sections:
        cspath = (emu, effs) for the "context" path (from function start)
        aspath = (emu, effs) for the last codeblock

        if "next" isn't False, the next iteration is returned.  otherwise, the current iteration is (same as last call).
        this allows the Symbolik Parts to be easily accessible from various parts of the algorithm without handing around
        a lot of state as function args.
        '''
        if not next and self.cspath is not None and self.aspath is not None and self.fullpath is not None:
            return self.cspath, self.aspath, self.fullpath
        
        self.clearCache()

        vw = self.vw
        sctx = self.sctx
        jmpva = self.jmpva

        fva = vw.getFunction(jmpva)
        cb = vw.getCodeBlock(jmpva)
        if cb is None:
            raise Exception("Dynamic Branch is not currently part of a CodeBlock!")
        cbva, cbsz, cbfva = cb

        if self._sgraph is None:
            self._sgraph = sctx.getSymbolikGraph(fva)

        if self._codepathgen is None:
            #self._codepathgen = viv_graph.getCodePathsTo(self._sgraph, cbva)
            pathGenFactory = viv_graph.PathGenerator(self._sgraph)
            self._codepathgen = pathGenFactory.getFuncCbRoutedPaths(fva, cbva, 1, timeout=20)

        self._codepath = self._codepathgen.next()
        contextpath = self._codepath[:-1]
        analpath = self._codepath[-1:]

        self.cspath = sctx.getSymbolikPaths(fva, graph=self._sgraph, args=None, paths=[contextpath]).next()
        self.aspath = sctx.getSymbolikPaths(fva, graph=self._sgraph, args=[], paths=[analpath]).next()
        if len(self.cspath[1]) == 0:
            self.cspath = self.aspath
        self.fullpath = sctx.getSymbolikPaths(fva, graph=self._sgraph, args=None, paths=[self._codepath]).next()


        return self.cspath, self.aspath, self.fullpath

    def getComplexIdx(self):
        smplIdx = self.getSymIdx()

        (csemu, cseffs), asp, fullp = self.getSymbolikParts()
        cplxIdx = csemu.getSymVariable(smplIdx)
        return cplxIdx

    #### higher level functionality ####

    def getBoundingCons(self, cplxIdx):
        return [con for con in self.getConstraints() if contains(con, cplxIdx)[0] ]

    def getNormalizedConstraints(self):
        '''
        takes in a complex index symbolik state
        returns a list of tuples of (SYMT_CON_??, offset)
        '''
        retcons = []
        baseIdx, baseoff = self.getBaseSymIdx()

        for con in self.getBoundingCons(baseIdx): # merge the two
            cons = con.cons

            if not cons.symtype in (SYMT_CON_GT, SYMT_CON_GE, SYMT_CON_LT, SYMT_CON_LE): 
                #logger.debug("SKIPPING NON-LIMITING: cons = %s", repr(cons))
                #return None, None, None
                continue
            
            if cons.kids[1].symtype == SYMT_CONST:
                symvar = cons.kids[0]
                symcmp = cons.kids[1]
            
            elif cons.kids[0].symtype == SYMT_CONST:
                symcmp = cons.kids[0]
                symvar = cons.kids[1]
            
            else:
                # neither side of the constraint is a CONST.  this constraint does 
                # not set static bounds on idx
                #logger.debug("SKIPPING (non-discrete): cons = %s", repr(cons))
                continue

            if not contains(symvar, baseIdx):
                logger.debug("Constraint not based on Index: %r" % cons)
                continue

            if cons.symtype == SYMT_CON_LT and symcmp.solve() == 0:
                #logger.debug("SKIPPING Constraint Checking for Zero: %r" % cons)
                continue

            conthing, consoff = peelIdxOffset(symvar)

            if conthing != baseIdx:
                logging.info("FAIL: %r  != %r" % (conthing, baseIdx))
                #raw_input("FAIL: %r  != %r" % (conthing, baseIdx))
                continue

            logger.debug("GOOD: %r\n\t%r\n\t%r\t%r + %r" % (cons, symvar, conthing, consoff, symcmp))
            retcons.append((con, cons.symtype, consoff+symcmp.solve()))

        return retcons

    def getBounds(self):
        '''
        Determine the lower index, the upper index, and the offset.
        lower and upper are inclusive.
        '''
        if None not in (self.lower, self.upper, self.baseoff):
            return self.lower, self.upper, self.baseoff

        (csemu, cseffs), asp, fullp = self.getSymbolikParts()

        lower = 0       # the smallest index used.  most often wants to be 0
        upper = None    # the largest index used.  max=MAX_CASES
        count = 0
        baseoff = None
       
        try:
            while lower is None or (lower == 0 and upper is None) or upper <= lower: # FIXME: this will fail badly when it fails.  make this dependent on the codepathgen
                # get the index we'll be looking for in constraints
                lower = 0           # the smallest index used.  most often wants to be 0
                upper = None        # the largest index used.  max=MAX_CASES

                if count != 0:
                    (csemu, cseffs), asp, fullp = self.getSymbolikParts(next=True)

                count += 1

                ##### PEAL the cplxIdx #####
                baseIdx, baseoff = self.getBaseSymIdx()
                logger.debug("baseIdx: %r", baseIdx)

                # there are two important offsets: constraint offsets and index offsets
                #   index offsets are mostly subtractions from the actual number used (eg. index 1500 would be idx-1500 for an offset of 1500)
                #   constraint offsets are subtractions from the index at the point of the constraint check.  these are accounted for by getNormalizedConstraints()
                for con, stype, offset in self.getNormalizedConstraints():

                    #conthing, consoff = peelIdxOffset(symvar)
                    if stype == SYMT_CON_GT: # this is setting the lower bound
                        newlower = offset + 1
                        if newlower > lower: 
                            logger.info("==setting a lower bound:  %s -> %s", lower, newlower)
                            lower = newlower
                        
                    elif stype == SYMT_CON_GE: # this is setting the lower bound
                        newlower = offset
                        if newlower > lower: 
                            logger.info("==setting a lower bound:  %s -> %s", lower, newlower)
                            lower = newlower
                        
                    elif stype == SYMT_CON_LT: # this is setting the upper bound
                        newupper = offset - 1
                        if upper is None or newupper < upper and newupper > 0:
                            logger.info("==setting a upper bound:  %s -> %s", upper, newupper)
                            upper = newupper
                        
                    elif stype == SYMT_CON_LE: # this is setting the upper bound
                        newupper = offset
                        if upper is None or newupper < upper and newupper > 0:
                            logger.info("==setting a upper bound:  %s -> %s", upper, newupper)
                            upper = newupper

                    else:
                        logger.info("Unhandled comparator:  %s\n", repr(cons))

                logger.info("Done.. %r %r ...\n" % (lower, upper))
        except StopIteration:
            pass

        # if upper is None:  we need to exercize upper until something doesn't make sense.  
        # we also need to make sure we don't analyze non-Switches.  
        if upper is None:
            upper = MAX_CASES

        if lower < baseoff:
            # assume the compiler doesn't adjust the index below 0
            lower = baseoff

        #logger.info("Lower: %r\tUpper: %r\tOffset: %r\tIndex: %r", lower, upper, baseoff, smplIdx)
        self.upper = upper
        self.lower = lower
        self.baseoff = baseoff

        #################
        return self.lower, self.upper, self.baseoff

    def makeSwitch(self):
        '''
        DIFFERENT TYPES OF SWITCH CASES:
        * VS's multidimensional
        * VS's single-dimension
        * Posix single dimension
        * Any of them with offset (EBX for Posix PIE, VS's base reg (typically 0x10000))

        What we need:
        * Resultant location for xrefs (iterative)
        * Index symboliks (for Constraint checking, addition/subtraction)
        * potentially, base va offset?  if only to identify the others.... but maybe not.

        How do we get from jmpreg (which is a very limited scope symboliks) to full scope symboliks run (from funcva)?
        * va effect comparison?
        '''

        vw = self.vw

        # only support branching switch-cases (ie, not calls)
        if not (self.op.iflags & envi.IF_BRANCH):
            logger.info("makeSwitch: exiting: not a branch opcode: 0x%x: %r", self.op.va, self.op)
            return

        if len(vw.getXrefsFrom(self.jmpva)):
            logger.info('skipping existing switchcase: 0x%x', self.jmpva)
            return

        funcva = self.vw.getFunction(self.jmpva)
        if funcva is None:
            logger.error("ERROR getting function for jmpva 0x%x", self.jmpva)
            return

        if funcva == self.jmpva:
            logger.error("ERROR function va IS jmpva 0x%x", self.jmpva)
            return

        instrcount = vw.getFunctionMeta(funcva, 'InstructionCount')
        if instrcount < MIN_FUNC_INSTR_SIZE:
            logger.error("Ignoring jmp in too small a function: %d instructions", instrcount)
            return

        try:
            # relying on getBounds() to bail on non-switch-cases
            lower, upper, baseoff = self.getBounds()
            if None in (lower, ): 
                logger.info("something odd in count/offset calculation...(%r,%r,%r) skipping 0x%x...", 
                            lower, upper, baseoff, self.jmpva)
                return

            count = upper - lower + 1
            if count > MAX_CASES:
                if count > CASE_FAILURE:
                    logger.warn("TOO many switch cases detected: %d.  FAILURE.  Skipping this dynamic branch", count)
                    return
                
                logger.warn("too many switch cases during analysis: %d   limiting to %d", count, MAX_CASES)
                count = MAX_CASES

            # determine deref-ops...  uses TrackingSymbolikEmulator
            # iterCases
            cases = {}
            memrefs = []
            for idx, addr in self.iterCases():
                logger.info("0x%x analyzeSwitch: idx: %s \t address: 0x%x", self.jmpva, idx, addr)
                
                # determining when to stop identifying switch-cases can be tough.  we assume that we have the 
                # correct number handed into this function in "count", but currently we'll stop analyzing
                # if we run into trouble.
                if not vw.isValidPointer(addr):
                    logger.info("found invalid pointer.  quitting.  (0x%x)" % addr)
                    break
                
                tloc = vw.getLocation(addr)
                if tloc is not None and tloc[0] != addr:
                    # pointing at something not right.  must be done.
                    logger.info("found overlapping location.  quitting.")
                    break
             
                if len(cases):
                    xrefsto = vw.getXrefsTo(addr)
                    # if there is an xref to this target from within this function, we're still ok... ish?
                    if len(xrefsto):
                        good = True
                        for xrfr, xrto, xrt, xrtinfo in xrefsto:
                            xrfrfunc = vw.getFunction(xrfr)
                            if xrfrfunc == funcva:
                                continue

                            # this one is *not* in the same function
                            good = False

                        if not good:
                            logger.info("target location (0x%x) has xrefs.", addr)
                            break
                
                # this is a valid thing, we have locations...  match them up
                caselist = cases.get(addr)
                if caselist is None:
                    caselist = []
                    cases[addr] = caselist
                caselist.append( idx )

                # make the connections
                vw.addXref(self.jmpva, addr, vivisect.REF_CODE)
                nloc = vw.getLocation(addr)
                if nloc is None:
                    vw.makeCode(addr)

            # makeNames (done separately because some indexes may be combined)
            makeNames(vw, self.jmpva, cases, baseoff)

            # store some metadata in a VaSet
            vw.setVaSetRow('SwitchCases', (self.jmpva, self.jmpva, count) )

            if baseoff is not None:
                lower += baseoff
                upper += baseoff
            
            vw.setComment(self.jmpva, "lower: 0x%x, upper: 0x%x" % (lower, upper))

            vagc.analyzeFunction(vw, funcva)
        except SymIdxNotFoundException as e:
            logger.info("!@#$!@#$!@#$!@#$ BOMBED OUT (SymIdx) 0x%x  !@#$!@#$!@#$!@#$ \n%r" % (self.jmpva, e))

        except PathForceQuitException as e:
            logger.info("!@#$!@#$!@#$!@#$ BOMBED OUT (Path Timeout!) 0x%x  !@#$!@#$!@#$!@#$ \n%r" % (self.jmpva, e))

        except Exception as e:
            logger.exception("!@#$!@#$!@#$!@#$ BOMBED OUT 0x%x  !@#$!@#$!@#$!@#$ \n%r", self.jmpva, e)


    def getDerefs(self):
        '''
        roll through effects and look for EFF_READMEM
        '''
        derefs = []

        csp, asp, fullp = self.getSymbolikParts()
        csemu, cseffs = csp
        asemu, aseffs = asp

        # create a tracking emulator and populate with with current "csp" state
        semu = TrackingSymbolikEmulator(self.vw)
        semu.setSymSnapshot(csemu.getSymSnapshot())

        symIdx = self.getSymIdx()

        # set our index to 0, to get the base of pointer/offset arrays
        semu.setSymVariable(symIdx, Const(0, 8))

        for eff in aseffs:
            startlen = len(semu.getTrackInfo())

            if eff.efftype == EFFTYPE_READMEM:
                if eff.va == self.jmpva:
                    continue

                symaddr = eff.symaddr.update(emu=semu)
                if symaddr.isDiscrete():
                    solution = symaddr.solve()
                    logger.info("0x%x->0x%x" % (eff.va, solution))

                    if not self.vw.isValidPointer(solution):
                        logger.warn(("ARRRG: Non-pointer in ReadMemory???"))

                    target = semu.readSymMemory(eff.symaddr, eff.symsize)
                    size = target.getWidth()
                    derefs.append((eff.va, symaddr, solution, target.solve(), size))

            endlen = len(semu.getTrackInfo())

        return derefs

    def getBaseSymIdx(self):
        '''
        (cached)
        returns the baseIdx and greatest index offset (ie.  the offset at the point of jmp).
        '''
        if None not in (self.baseIdx, self.baseoff):
            return self.baseIdx, self.baseoff

        def _cb_peel_idx(path, symobj, ctx):
            logger.debug( ' PATH: %r\n SYMOBJ: %r\n CTX: %r\n' % (path, symobj, ctx))

        def _cb_mark_longpath(path, symobj, ctx):
            #logger.debug( ' PATH: %r\n SYMOBJ: %r\n CTX: %r\n' % (path, symobj, ctx))
            longpath = ctx.get('longpath')
            if longpath is None:
                ctx['longpath'] = list(path)
            elif len(path) > len(longpath):
                ctx['longpath'] = list(path)

        (csemu, cseff), aspath, fullpath = self.getSymbolikParts()

        #idx = self.getComplexIdx().update(csemu).reduce()
        idx = self.getComplexIdx().reduce()

        # peel it back
        ctx = {}
        idx.walkTree(_cb_mark_longpath, ctx)
        longpath = ctx.get('longpath')

        # now compare the long path against constraints that contain it.  find sweet spot
        count = last = None
        which = None
        offset = 0

        # peel back the constraints to remove any incidental modifications to the index variable
        #  some compilers separate disparate groupings of cases into multiple dynamic branches.
        #  in order to make all pointer/offset arrays 0-based, the index gets modified (subtracted)


        # HACK: this is left-handed, and based on the longpath.  it may also benefit from actual comparing with the 
        # known index.
        logging.info("LONGPATH: " + '\n'.join([repr(x) for x in longpath]))
        for symobj in longpath:
            last = count
            count = len(self.getBoundingCons(symobj))
            logger.debug(" lp %d: %r" % (count, symobj))

            # peel off o_subs and size-limiting o_ands and o_sextends
            if isinstance(symobj, o_and) and symobj.kids[1].isDiscrete() and symobj.kids[1].solve() in e_bits.u_maxes:
                mask = symobj.kids[1].solve()
                pass    # this wrapper is a size-limiting bitmask

            elif isinstance(symobj, o_sub):
                offset += symobj.kids[1].solve() # this is an offset, used to rebase the index into a different pointer array

            elif isinstance(symobj, o_add):
                offset -= symobj.kids[1].solve() # this is an offset, used to rebase the index into a different pointer array

            elif isinstance(symobj, o_sextend):
                pass # sign-extension is irrelevant for indexes

            # anything else and we're done peeling
            else:
                break

        logger.debug(" lp DONE: (%r) %r" % (offset, symobj))
        # now figure what was cut, and what impact it has.
        self.baseIdx = symobj
        self.baseoff = offset

        return symobj, offset
        

    def markDerefs(self):
        lower, upper, offset = self.getBounds()

        for va, symaddr, addr, tgt, sz in self.getDerefs():
            # first make the xref from opcode to data:
            self.vw.addXref(va, addr, REF_DATA)

            if sz == self.vw.psize and self.vw.isValidPointer(tgt):
                for count in range(upper-lower+1):
                    self.vw.makePointer(addr + (sz*count))

            else:
                for count in range(upper-lower+1):
                    self.vw.makeNumber(addr + (sz*count), sz)

    def iterCases(self):
        '''
        Generator which yields the case index and the target address
        '''
        vw = self.vw

        (csemu, cseffs), aspath, fullpath = self.getSymbolikParts()

        symidx = self.getSymIdx()
        logger.info('getSymIdx: %r', symidx)

        jmptgt = self.getSymTarget()
        lower, upper, offset = self.getBounds()
        logger.debug( " itercases: %r %r %r %r", symidx, lower, upper, offset)

        # use a TrackingSymbolikEmulator so we get the "readSymMemory()" function actually hitting 
        # the r/o data from our VivWorkspace
        symemu = TrackingSymbolikEmulator(vw)
        symemu.setSymSnapshot(csemu.getSymSnapshot())

        symemu.setSymVariable(symidx, None) # don't want to update this out of the symbolik state
        #workJmpTgt = jmptgt.update(emu=symemu)


        for idx in range(lower-offset, upper-offset+1):
            symemu.setSymVariable(symidx, Const(idx, 8))
            workJmpTgt = jmptgt.update(emu=symemu)
            logger.info(" itercases: workJmpTgt: %r", workJmpTgt)
            coderef = workJmpTgt.solve(emu=symemu, vals={symidx:idx})
            #coderef = jmptgt.update(emu=symemu)
            logger.debug(" itercases: %r, %r", idx, hex(coderef))
            yield idx + offset, coderef

def makeNames(vw, jmpva, cases, baseoff=0):
    '''
    Create names and xrefs for each identified case.
    '''
    for addr, indexes in cases.items():
        outstrings = []
        combined = False
        start = last = UNINIT_CASE_INDEX
        for case in indexes:
            if case == last+1:
                if not combined:
                    combined = True
                    start = last
            else:
                if combined:
                    combined = False
                    outstrings.append("%Xto%X" % (start+baseoff, last+baseoff))
                elif last != UNINIT_CASE_INDEX:
                    outstrings.append("%X" % (last+baseoff))
            last = case

        # catch the last one if highest cases are combined
        if combined:
            combined = False
            outstrings.append("%Xto%X" % (start+baseoff, last+baseoff))
        else:
            outstrings.append("%X" % (case+baseoff))

        logger.info("OUTSTRINGS: %s", repr(outstrings))

        idxs = '_'.join(outstrings)
        casename = "case_%s_%x" % (idxs, addr)

        curname = vw.getName(addr) 
        if curname is not None:
            ## FIXME NOW!:   if already labeled, chances are good this is other cases in the same function.
            ## either simply add the new outstrings to the current one or we need to keep track of what
            ## calls each and with what switchcase/index info.  VaSet?  or do we want this to only expect
            ## the same function to call each one, and all part of the same Switchcase?
            logger.warn("%s is already labeled %s", casename, curname)

        vw.makeName(addr, casename)
        logger.info(casename)

    vw.makeName(jmpva, "switch_%.8x" % jmpva)
    logger.info("making switchname: switch_%.8x", jmpva)
       


def link_up(vw, jmpva, array, count, baseoff, baseva=None, itemsize=None):
    '''
    Manually link up a switchcase for which we have a pointer/offset array

    If baseva is None, the array is treated as a pointer array
    Otherwise, the numbers in the array are treated as offset from baseva

    If itemsize is not None, itemsize is treats as the size of each item 
        in the array (in bytes.. ie. 2, 4, 8 bytes)
    '''
    funcva = vw.getFunction(jmpva)
    lower = 0
    upper = count

    logger.info("link_up(0x%x, 0x%x, %d, 0x%x, %r, %r)", jmpva, array, count, baseoff, baseva, itemsize)

    cases = {}
    memrefs = []
    for idx in range(count):
        # handle specific itemsize if not pointer sized

        if itemsize is not None:
            idxloc = array + (idx * itemsize)
            fmt = e_bits.getFormat(itemsize, big_endian=vw.getEndian())
            addr, = vw.readMemoryFormat(idxloc, fmt)
        else:
            itemsize = vw.psize
            idxloc = array + (idx * itemsize)
            addr = vw.readMemoryPtr(idxloc)

        # sign-extend if an offset (many are negative)
        if itemsize < vw.psize:
            addr = e_bits.sign_extend(addr, itemsize, vw.psize)

        # handle base-va calculation
        if baseva is not None:
            addr = e_bits.unsigned(baseva + addr, vw.psize)

        logger.info("0x%x manalyzeSwitch: idx: %s \t address: 0x%x", jmpva, idx, addr)
        
        # determining when to stop identifying switch-cases can be tough.  we assume that we have the 
        # correct number handed into this function in "count", but currently we'll stop analyzing
        # if we run into trouble.
        if not vw.isValidPointer(addr):
            logger.info("found invalid pointer.  quitting.  (0x%x)" % addr)
            break
        
        tloc = vw.getLocation(addr)
        if tloc is not None and tloc[0] != addr:
            # pointing at something not right.  must be done.
            logger.info("found overlapping location.  quitting.")
            break
     
        if len(cases):
            xrefsto = vw.getXrefsTo(addr)
            # if there is an xref to this target from within this function, we're still ok... ish?
            if len(xrefsto):
                good = True
                for xrfr, xrto, xrt, xrtinfo in xrefsto:
                    xrfrfunc = vw.getFunction(xrfr)
                    if xrfrfunc in (funcva, None):
                        continue

                    # this one is *not* in the same function
                    logger.info("thisfunc: %r  otherfunc: %r", funcva, xrfrfunc)
                    #good = False

                if not good:
                    logger.info("target location (0x%x) has xrefs.", addr)
                    break
        
        # this is a valid thing, we have locations...  match them up
        caselist = cases.get(addr)
        if caselist is None:
            caselist = []
            cases[addr] = caselist
        caselist.append( idx )

        # make the connections
        vw.addXref(jmpva, addr, vivisect.REF_CODE)
        nloc = vw.getLocation(addr)
        if nloc is None:
            vw.makeCode(addr)

        # make pointers/numbers from the ptr/offset locations
        if baseva is not None:
            vw.makeNumber(idxloc, itemsize)
        else:
            vw.makePointer(idxloc)

    # makeNames (done separately because some indexes may be combined)
    makeNames(vw, jmpva, cases, baseoff)

    # store some metadata in a VaSet
    vw.setVaSetRow('SwitchCases', (jmpva, jmpva, count) )

    if baseoff is not None:
        lower += baseoff
        upper += baseoff
    
    vw.setComment(jmpva, "lower: 0x%x, upper: 0x%x" % (lower, upper))


def analyzeFunction(vw, fva):
    '''
    Function analysis module.
    This is inserted right after codeblock analysis
    '''
    if vw.verbose:
        logger.setLevel(logging.DEBUG)

    targetNewFunctions(vw, fva)

    lastdynlen = 0
    dynbranches = vw.getVaSet('DynamicBranches')
    done = vw.getMeta('analyzedDynBranches')
    if done is None:
        done = []
    
    # because the VaSet is often updated during analysis, we have to check to see if there are new 
    # dynamic branches to analyze.
    while lastdynlen != len(dynbranches):
        lastdynlen = len(dynbranches)
        for jmpva, (none, oprepr, bflags) in dynbranches.items():
            if bflags & envi.BR_PROC:   # skip calls
                continue

            funcva = vw.getFunction(jmpva)
            if funcva != fva:
                # jmp_indir is for the entire VivWorkspace.  
                # we're just filtering to this function here.
                # this should be checked again when codeblocks are allowed to 
                #   be part of multiple functions.
                continue

            if vw.getVaSetRow('SwitchCases', jmpva) is not None:
                logger.warn("...skipping 0x%x - SwitchCases already has it?", jmpva)
                continue

            if jmpva in done:
                logger.warn("...skipping 0x%x - already done", jmpva)
                continue
            done.append(jmpva)

            sc = SwitchCase(vw, jmpva)
            sc.analyze()
            
            '''
            inp = raw_input("PRESS ENTER TO CONTINUE...")
            while len(inp):
                try:
                    print(repr(eval(inp, globals(), locals())))
                except:
                    logger.exception('error')

                inp = raw_input("PRESS ENTER TO CONTINUE...")
            '''
            #import envi.interactive as ei; ei.dbg_interact(locals(), globals())

        dynbranches = vw.getVaSet('DynamicBranches')
    vw.setMeta('analyzedDynBranches', done)
    # FIXME: we need a better way to store changing lists/dicts, that don't show up in the UI.  VaSet would be great, but ugly



# for use as vivisect script
if globals().get('vw'):
    verbose = vw.verbose
    vw.verbose = True

    vw.vprint("Starting...")
    jmpva = vw.parseExpression(argv[1])

    sc = SwitchCase(vw, jmpva)
    sc.analyze()

    vw.vprint("Done")
    
    vw.verbose = verbose
   



'''  SCRATCH NOTES for determining characteristics of the switch case '''
#  basically, trace into the symobj of fullcons[-1] grabbing stuff before first memory access.
#  or rather, identify what wraps our index symobj... index symobj is the most complete symobj following a o_mul that appears in the last constraint (hack?)

#[str(x) for x in ctx]

#['arg0',
#'mem[(arg0 + 1544):8]',
#'mem[(mem[(arg0 + 1544):8] + 66):2]',
#'mem[((((mem[(mem[(arg0 + 1544):8] + 66):2] & 0xffffffff) << 3) + (mem[(arg0 + 1544):8] * 1)) + 64):4]',
#'mem[((0x00010000 + (((mem[((((mem[(mem[(arg0 + 1544):8] + 66):2] & 0xffffffff) << 3) + (mem[(arg0 + 1544):8] * 1)) + 64):4] & 0xffffffff) - 1) * 1)) + 0x00010a0c):1]',
#'mem[((0x00010000 + (mem[((0x00010000 + (((mem[((((mem[(mem[(arg0 + 1544):8] + 66):2] & 0xffffffff) << 3) + (mem[(arg0 + 1544):8] * 1)) + 64):4] & 0xffffffff) - 1) * 1)) + 0x00010a0c):1] * 4)) + 0x000109fc):4]']
#
## wax Consts
#
## take leftovers, assign unknowns as variable names
#
## find least common denominator for unknowns...  
#
##  ACTUALLY... we only are looking for the index (Constraints on the kid of a o_mul) and subtractions to the index :)
#
###  inner most o_mul, if it matters...

'''
    In [97]: [eff for eff in aeffs if eff.efftype == EFFTYPE_CONSTRAIN]
    Out[97]: 
        [ConstrainPath( 0x000134a9, Const(0x000134af,8), ne(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),o_add(Arg(0,width=8),Const(0x00000608,8),8)) ),
         ConstrainPath( 0x00013581, Const(0x000134bd,8), ne(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),o_add(Arg(0,width=8),Const(0x00000608,8),8)) ),
         ConstrainPath( 0x000134d0, Const(0x000134d6,8), ne(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000040,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x0000000b,8)) ),
         ConstrainPath( 0x000134d9, Const(0x0001393d,8), ne(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000040,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000006,8)) ),
         ConstrainPath( 0x00013940, Const(0x00013946,8), ne(o_and(o_sub(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000040,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000006,8),4),Const(0xffffffff,4),4),Const(0x00000001,8)) ),
         ConstrainPath( 0x00013949, Const(0x000134df,8), eq(o_and(o_sub(o_and(o_sub(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000040,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000006,8),4),Const(0xffffffff,4),4),Const(0x00000001,8),4),Const(0xffffffff,4),4),o_and(Const(0x00000002,8),Const(0xffffffff,4),4)) ),
         ConstrainPath( 0x000134e6, Const(0x000134ec,8), eq(o_and(Mem(o_add(Arg(0,width=8),Const(0x00000260,8),8), Const(0x00000001,8)),Const(0x00000080,8),1),Const(0x00000000,8)) ),
         ConstrainPath( 0x0001350c, Const(0x00013512,8), eq(Mem(o_add(Arg(0,width=8),Const(0x00000108,8),8), Const(0x00000008,8)),Const(0x00013440,8)) ),
         ConstrainPath( 0x00013515, Const(0x0001351b,8), le(Const(0x0000001c,8),o_and(o_sub(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000028,8),8), Const(0x00000004,8)),Const(0xffffffff,4),4),o_and(o_lshift(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000042,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000003,8),4),Const(0xffffffff,4),4),4),Const(0xffffffff,4),4)) ),
         ConstrainPath( 0x00013520, Const(0x00013526,8), le(Const(0x0000006b,8),o_and(Mem(o_add(o_add(o_lshift(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000042,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000003,8),4),o_mul(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0x00000040,8),8), Const(0x00000004,8)),Const(0xffffffff,4),4)) ),
         ConstrainPath( 0x00013529, Const(0x00020767,8), ge(o_and(Mem(o_add(o_add(o_lshift(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000042,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000003,8),4),o_mul(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0x00000040,8),8), Const(0x00000004,8)),Const(0xffffffff,4),4),Const(0x0000006f,8)) ),
         ConstrainPath( 0x0002076c, Const(0x00020772,8), le(o_and(o_sub(o_and(Mem(o_add(o_add(o_lshift(o_and(Mem(o_add(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000042,8),8), Const(0x00000002,8)),Const(0xffffffff,4),4),Const(0x00000003,8),4),o_mul(Mem(o_add(Arg(0,width=8),Const(0x00000608,8),8), Const(0x00000008,8)),Const(0x00000001,8),8),8),Const(0x00000040,8),8), Const(0x00000004,8)),Const(0xffffffff,4),4),Const(0x00000001,8),4),Const(0xffffffff,4),4),Const(0x00000078,8)) )]

'''
'''
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), Const(0x7ff38880000,8)]
SYMOBJ: Const(0x7ff38880000,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)), o_and(Var("rdx", width=8),Const(0xffffffff,4),4), Var("rdx", width=8)]
SYMOBJ: Var("rdx", width=8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)), o_and(Var("rdx", width=8),Const(0xffffffff,4),4), Const(0xffffffff,4)]
SYMOBJ: Const(0xffffffff,4)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)), o_and(Var("rdx", width=8),Const(0xffffffff,4),4)]
SYMOBJ: o_and(Var("rdx", width=8),Const(0xffffffff,4),4)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)), Const(0x00000004,8)]
SYMOBJ: Const(0x00000004,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8))]
SYMOBJ: o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8))
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8), Const(0x00000004,8)]
SYMOBJ: Const(0x00000004,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8), o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8)]
SYMOBJ: o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8)]
SYMOBJ: o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x0003027c,8)]
SYMOBJ: Const(0x0003027c,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8)]
SYMOBJ: o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)), Const(0x00000004,8)]
SYMOBJ: Const(0x00000004,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8))]
SYMOBJ: Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8))
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8), Const(0x7ff38880000,8)]
SYMOBJ: Const(0x7ff38880000,8)
CTX: {}
PATH: [o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8)]
SYMOBJ: o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8)
CTX: {}
Out[14]: o_add(Mem(o_add(o_add(Const(0x7ff38880000,8),o_mul(o_sextend(o_and(Var("rdx", width=8),Const(0xffffffff,4),4),Const(0x00000004,8)),Const(0x00000004,8),8),8),Const(0x0003027c,8),8), Const(0x00000004,8)),Const(0x7ff38880000,8),8)

'''



'''
# libc-2.13.so



path=[0x205ac40, 0x205ac41, 0x205ac43, 0x205ac44, 0x205ac45, 0x205ac46, 0x205ac49, 0x205ac4c, 0x205ac4f, 0x205ac54, 0x205ac5a, 0x205ac5d, 0x205ac60, 0x205ac64, 0x205ac6b, 0x205ac72, 0x205ac75, 0x205ac78, 0x205ac7b, 0x205ac7f, 0x205ac82, 0x205ac85, 0x205ac88, 0x205ac8b, 0x205ac8d, 0x205ac90, 0x205ac93, 0x205ac96, 0x205ac98, 0x205ac9b, 0x205ac9e, 0x205aca1, 0x205aca4, 0x205aca7, 0x205acaa, 0x205acac, 0x205acaf, 0x205acb0, 0x205acb3, 0x205acb6, 0x205acb9, 0x205acbb, 0x205acbe, 0x205acc1, 0x205acc3, 0x205acc6, 0x205acc9, 0x205accb, 0x205accd, 0x205acd1, 0x205acd7, 0x205acda, 0x205acdd, 0x205acdf, 0x205ace2, 0x205ace5, 0x205aceb, 0x205acee, 0x205acf2, 0x205acf4, 0x205acfb, 0x205ad02, 0x205ad09, 0x205ad0b, 0x205ad0e, 0x205b178, 0x205b17b, 0x205b17d, 0x205b180, 0x205b183, 0x205b186, 0x205b188, 0x205b18b, 0x205b18e, 0x205b191, 0x205b194, 0x205b197, 0x205b19a, 0x205b19c, 0x205b19f, 0x205b1a0, 0x205b1a3, 0x205b1a6, 0x205b1a9, 0x205b1ab, 0x205b1ae, 0x205b1b1, 0x205b1b3, 0x205b1b6, 0x205b1b9, 0x205b1bb, 0x205b1bd, 0x205b1c1, 0x205b41c, 0x205b41f, 0x205b422, 0x205b425, 0x205b427, 0x205b429, 0x205b42c, 0x205b42f, 0x205b432, 0x205b434, 0x205b437, 0x205b43a, 0x205b43c, 0x205b1c8, 0x205b1cb, 0x205b1ce, 0x205b1d5, 0x205b1d8, 0x205b1db, 0x205b1de, 0x205ad5b, 0x205ad62, 0x205ad68, 0x205ad6b, 0x205b1e8, 0x205b1eb, 0x205b1ed, 0x205b1f0, 0x205b1f3, 0x205b360, 0x205b363, 0x205b365, 0x205b368, 0x205b36b, 0x205b36e, 0x205b374, 0x205b377, 0x205b37a, 0x205b37d, 0x205b380, 0x205b383, 0x205b386, 0x205b388, 0x205b38b, 0x205b38e, 0x205b390, 0x205b393, 0x205b395, 0x205b398, 0x205b39b, 0x205b39e, 0x205b3a1, 0x205b3a3, 0x205b3a6, 0x205b3a9, 0x205b3ab, 0x205b3ad, 0x205b3b0, 0x205b3b2, 0x205b3b5, 0x205b3b8, 0x205b3bb, 0x205b3bd, 0x205b3bf, 0x205b3c2, 0x205b3c4, 0x205b3c7, 0x205b3ca, 0x205b3cd, 0x205b3cf, 0x205b3d2, 0x205b3f8, 0x205b3fb, 0x205b3ff, 0x205b402, 0x205b405, 0x205b408, 0x205b40b, 0x205ad71, 0x205ad75, 0x205ad79, 0x205ad7f, 0x205ad85, 0x205ad87, 0x205b450, 0x205b452, 0x205b456, 0x205b45c, 0x205b45f, 0x205b463, 0x205b466, 0x205b46b, 0x205b46d, 0x205ae81, 0x205ae84, 0x205ae86, 0x205ae89, 0x205ae90, 0x205ae96, 0x205ae99, 0x205ae9c, 0x205aea3, 0x205aea5, 0x205b4a0, 0x205b4a6, 0x205b4ac, 0x205b4b2, 0x205b4b5, 0x205b4b7, 0x205aeab, 0x205aeae, 0x205aeb1, 0x205aeb8, 0x205b040, 0x205b042, 0x205b049 ]
#print '\n'.join([x for x in dir(vw) if 'olor' in x])

from vqt.main       import vqtevent
vqtevent('viv:colormap', {x:'green' for x in path})

#vw.addColorMap('thispath',{x:'green' for x in path})
#vw._viv_gui.setColorMap()



print ("DONE")
'''
