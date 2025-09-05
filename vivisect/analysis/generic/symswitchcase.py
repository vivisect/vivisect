'''
Finds and connects Switch Cases from Microsoft and GCC, and theoretically others,
which use pointer arithetic to determine code path for each case.

This will not connect switch cases which are actually explicit cmp/jz in the code.
'''
import sys
import time

import logging
logger = logging.getLogger(__name__)

import envi
import envi.exc as e_exc
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

# TODO: make all switchcase analysis for a given function cohesive (ie. don't finish up with naming until the entire function has been analyzed).  this will break cohesion if we use the CLI to add switchcases, but so be it.  (collisions in named targets... shared between jmp's in same switch/function)
# TODO: overlapping case names...  doublecheck the naming algorithm.  ahh... different switch-cases colliding on handlers?  is this legit?  or is it because we don't stop correctly?
# CHECK: are the algorithms for "stopping" correct?  currently getting 1 switch case for several cases in libc-32.  (enhance "don't analyze" checks (like, already analyzed?)  or no?)
# TODO: regrange description of Symbolik Variables... normalize so "eax" and "eax+4" make sense.


class TrackingSymbolikEmulator(vs_anal.SymbolikFunctionEmulator):
    '''
    TrackingSymbolikEmulator has two modifications from a standard SymbolikEmulator:
    * It tracks reads.  where they occur, where they read from, and
    returns as much info as possible if not discrete data.

    * If a read is from a real memory map, return that memory.

    These are both very useful for analyzing switchcases, to determine where in
    memory a read occurs and the data comes from.
    '''
    def __init__(self, vw):
        vs_anal.SymbolikFunctionEmulator.__init__(self, vw)
        self.__width__ = vw.psize
        self.clear()

    def clear(self):
        '''
        Clear read-tracker to start another analysis
        '''
        self._trackReads = []

    def track(self, va, addrval, val):
        '''
        Track reads in this SymbolikEmulator for later analysis
        '''
        self._trackReads.append((va, addrval, val))

    def getTrackInfo(self):
        '''
        Retrieve reads so far, for analysis
        '''
        return self._trackReads

    def setupFunctionCall(self, fva, args=None):
        logger.info("setupFunctionCall: SKIPPING!")

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
        # logger.debug("==--== %r   %r   %r", repr(symobj), symsolve, ctx['compare'])
        if symsolve == ctx['compare']:
            ctx['contains'] = True
            ctx['path'] = tuple(path)

        return symobj

    ctx = {'compare':   subobj.solve(),
           'contains':  False,
           'path':      ()
           }

    symobj.walkTree(_cb_contains, ctx)
    return ctx['contains'], ctx['path']

def getUnknowns(symvar):
    '''
    determine unknown registers in this symbolik object
    '''
    def _cb_grab_vars_n_mems(path, symobj, ctx):
        '''
        walkTree callback for grabbing Var objects
        '''
        #logging.debug("... unk: %r", symobj)
        if symobj.symtype == SYMT_VAR:
            varlist = ctx.get(SYMT_VAR)
            if symobj.name not in varlist:
                varlist.append(symobj.name)

        # sometimes the index comes from a global or local variable...
        if symobj.symtype == SYMT_MEM:
            memlist = ctx.get(SYMT_MEM)
            if symobj not in memlist:
                memlist.append(symobj)

    unks = {SYMT_VAR:[], SYMT_MEM:[]}
    symvar.walkTree(_cb_grab_vars_n_mems, unks)
    return unks

def replaceObj(ast, symobj, symreplacement):
    '''
    Walk the AST looking for symobj, replace with symreplacement
    '''
    def _cb_check_and_replace(path, symobj, ctx):
        searchobj = ctx.get('searchobj')
        for kidx, kid in enumerate(symobj.kids):
            if searchobj == kid:
                replacement = ctx.get('replacewith')
                symobj.setSymKid(kidx, replacement)
                ctx['success'] = True

    ctx = {
        'searchobj': symobj,
        'replacewith': symreplacement,
        'success': False,
    }

    ast.walkTree(_cb_check_and_replace, ctx)
    return ctx.get('success')

def hasMul(symobj):
    '''
    Returns True or False based on whether the symobj AST has a "Mul" object
    '''
    def _cb_check_for_mul(path, symobj, ctx):
        if symobj.symtype == SYMT_OPER_MUL:
            ctx['inthere'] = True

    ctx = {'inthere': False}
    symobj.walkTree(_cb_check_for_mul, ctx)
    return ctx['inthere']

def peelIdxOffset(symobj):
    '''
    Peel back ignorable wrapped layers of a symbolik Index register, and track
    offset in the process.  Once we've skipped out of the ignorable symobj's we
    should end up with something normalized-ish.
    '''
    offset = 0
    while True:
        # peel off o_subs and size-limiting o_ands and o_sextends
        if isinstance(symobj, o_and) and symobj.kids[1].isDiscrete() and symobj.kids[1].solve() in e_bits.u_maxes:
            # this wrapper is a size-limiting bitmask
            pass

        elif isinstance(symobj, o_sub):
            # this is an offset, used to rebase the index into a different pointer array
            if symobj.kids[1].isDiscrete():
                offset += symobj.kids[1].solve()

        elif isinstance(symobj, o_add):
            # this is an offset, used to rebase the index into a different pointer array
            if symobj.kids[1].isDiscrete():
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

# TODO: possibly only take calls in the first codeblock?
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
                logger.warning('failed to parse opcode within function at 0x%x (fva: 0x%x)', cbva, fva)
                cbva += 1
                continue

            for xrfr, xrto, xrt, xrflag in vw.getXrefsFrom(cbva):
                if not (op.iflags & envi.IF_CALL):
                    continue

                # TODO: improve upon determination of call
                tgtva = op.getOperValue(0)
                #logger.debug("-- 0x%x", tgtva)
                if tgtva is None or not vw.isValidPointer(tgtva):
                    continue

                if vw.getFunction(tgtva) is not None:
                    continue

                if tgtva in done:
                    continue
                done.append(tgtva)

                logger.info('Making new function: 0x%x (from 0x%x)', tgtva, xrfr)
                vw.makeFunction(tgtva)

            cbva += len(op)


THUNK_BX_CALL_LEN = 5


class ThunkReg:
    def __init__(self, regname, tgtval):
        self.regname = regname
        self.tgtval = tgtval

    def thunk_reg(self, emu, fname, symargs):
        '''
        These thunk_reg functions return the "RETURN" address, which the calling
        function then adds the appropriate amount to obtain the .got.plt base

        This simply applies the RET address to the appropriate register for 
        symbolik analysis
        '''
        vw = emu._sym_vw
        rctx = vw.arch.archGetRegCtx()
        regval = emu.getMeta('calling_va')
        oploc = vw.getLocation(regval)
        if oploc is None:
            regval += THUNK_BX_CALL_LEN 
        else:
            regval += oploc[L_SIZE]

        regobj = Const(regval, vw.psize)
        reg = rctx.getRealRegisterName(self.regname)
        logger.debug("thunk_%s is being called! %s\t%s\t%s", reg, emu, symargs, regobj)
        emu.setSymVariable(reg, regobj)


UNINIT_CASE_INDEX = -2


class SwitchCase:
    '''
    Actually do the analysis for each dynamic branch.
    * First, for analysis: target addresses, case-offset, number of cases
    * Second, to wire things up.

    Tracks the state of analysis so each component can easily do it's part
    without handing a ton of variables around between functions.
    '''
    def __init__(self, vw, jmpva, timeout=180):
        self.vw = vw
        self.jmpva = jmpva
        self.timeout = timeout
        self.jmpop = vw.parseOpcode(jmpva)
        logger.info('=== analyzing SwitchCase branch at 0x%x: %r ===' % (jmpva, self.jmpop))

        self.sctx = vs_anal.getSymbolikAnalysisContext(vw)
        if self.sctx is None:
            raise e_exc.ArchNotImplemented("Current architecture has no SymbolikTranslator")

        self.xlate = self.sctx.getTranslator()

        # 32-bit i386 thunk_reg handling.  this should be the only oddity for this architecture
        for tva, regname, tgtval in vw.getVaSetRows('thunk_reg'):
            fname = vw.getName(tva, True)
            trobj = ThunkReg(regname, tgtval)
            self.sctx.addSymFuncCallback(fname, trobj.thunk_reg)
            logger.debug( "sctx.addSymFuncCallback(%s, thunk_reg)" % fname)


        self._sgraph = None
        self._codepath = None
        self._codepathgen = None


        try:
            self.max_instr_count = vw.config.viv.analysis.symswitchcase.max_instr_count
            self.max_cases = vw.config.viv.analysis.symswitchcase.max_cases
            self.case_failure = vw.config.viv.analysis.symswitchcase.case_failure
            self.min_func_instr_size = vw.config.viv.analysis.symswitchcase.min_func_instr_size

        except AttributeError as e:
            logger.warning('configuration failure, using defaults: %r', e)
            self.max_instr_count  = 10
            self.max_cases   = 500
            self.case_failure = 5000
            self.min_func_instr_size = 10

        self.clearCache()



    def clearCache(self):
        '''
        While analyzing a switchcase, we end up caching several calculated items.
        This function clears them, so we can reset the state, like to skip
        inappropriate paths (eg.   if x> 3 and if x == 0
        '''
        self.cspath = None
        self.aspath = None
        self.fullpath = None

        self.upper = None
        self.lower = None
        self.count = None
        self.baseoff = None
        self.baseIdx = None

        self.jmpsymvar = None


    def analyze(self):
        '''
        Generic "analyze" function, which simply calls makeSwitch()
        '''
        self.makeSwitch()

    #### primitives for switchcase analysis ####
    def getJmpSymVar(self):
        '''
        returns the Simple Symbolik state of the dynamic target of the branch/jmp
        this is the symbolik register at the start of the last codeblock.
        '''
        if self.jmpsymvar is not None:
            return self.jmpsymvar

        self.jmpsymvar = self.xlate.getOperObj(self.jmpop, 0)
        return self.jmpsymvar

    def getSymTarget(self):
        '''
        Returns the Symbolik state of the dynamic target of the branch/jmp
        short indicates just in the context of the last codeblock.
        not short indicates the context at the start of the last codeblock (from funcva)
        '''
        jmpsymvar = self.getJmpSymVar()

        cspath, aspath, fullpath = self.getSymbolikParts()
        emu = aspath[0]
        tgtsym = jmpsymvar.update(emu)
        return tgtsym


    def getSymIdx(self):
        '''
        returns the symbolik index register, and the type of object
        returns first one found, first checking SYMT_VAR's and only
        then looking at SYMT_MEM symbolic indexes
        '''
        symtgt = self.getSymTarget()
        unks = getUnknowns(symtgt)

        cspath, aspath, fullpath = self.getSymbolikParts()

        for unk in unks.get(SYMT_VAR):
            unkvar = cspath[0].getSymVariable(unk)
            if unkvar.isDiscrete():
                continue
            return (SYMT_VAR, unk)

        for unk in unks.get(SYMT_MEM):
            unkvar = cspath[0].getSymVariable(unk)
            if unkvar.isDiscrete():
                continue
            return (SYMT_MEM, unk)

        raise v_exc.SymIdxNotFoundException(cspath, aspath)

    def getConstraints(self):
        '''
        Returns a list of Constraint objects from the current codepath.
        Some of these constraints should have checks for boundaries against our
        index variable which will prove helpful determining case-offset and
        case-count.
        '''
        csp, asp, fullp = self.getSymbolikParts()

        cons = [eff for eff in fullp[1] if eff.efftype==EFFTYPE_CONSTRAIN]
        [con.reduce() for con in cons]
        return cons

    def getBoundingCons(self, cplxIdx):
        return [con for con in self.getConstraints() if contains(con, cplxIdx)[0] ]

    def getSymbolikJmpBlock(self, emuclass=vs_anal.SymbolikFunctionEmulator):
        '''
        Returns symbolik effects for the last codeblock, which should never change.
        This should be small and does not require a path be generated, so it should
        be safe for early analysis and vetting of the dynamic branch (if it's not
        a switchcase, don't do all the heavy lifting)
        '''
        vw = self.vw
        sctx = self.sctx
        jmpva = self.jmpva

        fva = vw.getFunction(jmpva)
        cb = vw.getCodeBlock(jmpva)
        if cb is None:
            raise v_exc.InvalidCodeBlock("Dynamic Branch is not currently part of a CodeBlock!")
        cbva, cbsz, cbfva = cb

        if self._sgraph is None:
            self._sgraph = sctx.getSymbolikGraph(fva)

        jnva, jnode = self._sgraph.getNode(cbva)

        symemu = emuclass(vw)
        aeffs = symemu.applyEffects(jnode.get('symbolik_effects'))

        #TODO: ? cache these?  depends on how widely we use this function.
        return jnode, symemu, aeffs

    def getSymbolikParts(self, doNext=False):
        '''
        Puts together a path from the start of the function to the jmpva, breaking off the last 
        codeblock, and returning the symbolik path for both sections:
        cspath = (emu, effs) for the "context" path (from function start)
        aspath = (emu, effs) for the last codeblock

        if "next" isn't False, the next iteration is returned.  otherwise, the current iteration is (same as last call).
        this allows the Symbolik Parts to be easily accessible from various parts of the algorithm without handing around
        a lot of state as function args.
        '''
        if not doNext and self.cspath is not None and self.aspath is not None and self.fullpath is not None:
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
            pathGenFactory = viv_graph.PathGenerator(self._sgraph)
            self._codepathgen = pathGenFactory.getFuncCbRoutedPaths(fva, cbva, 1, timeout=self.timeout)

        self._codepath = next(self._codepathgen)
        contextpath = self._codepath[:-1]
        analpath = self._codepath[-1:]

        self.cspath = next(sctx.getSymbolikPaths(fva, graph=self._sgraph, args=None, paths=[contextpath]))
        self.aspath = next(sctx.getSymbolikPaths(fva, graph=self._sgraph, args=[], paths=[analpath]))

        if len(self.cspath[1]) == 0:
            self.cspath = self.aspath

        self.fullpath = next(sctx.getSymbolikPaths(fva, graph=self._sgraph, args=None, paths=[self._codepath]))

        return self.cspath, self.aspath, self.fullpath

    def getComplexIdx(self):
        '''
        Complex Index is the Applied Symboliks state (of the context-path) for
        the simple index returned by getSymIdx()

        eg.  if the simple symbolik index is `Var('edx', 4)` but the
            complex could be `Arg(2, 4)` or something similar
        '''
        symtype, smplIdx = self.getSymIdx()

        (csemu, cseffs), asp, fullp = self.getSymbolikParts()
        if symtype == SYMT_VAR:
            cplxIdx = csemu.getSymVariable(smplIdx)

        elif symtype == SYMT_MEM:
            symloc, symsz = smplIdx.kids
            cplxIdx = csemu.readSymMemory(symloc.update(csemu), symsz)

        return cplxIdx

    #### mid-level functionality ####
    def getBaseSymIdx(self):
        '''
        (cached)
        returns the baseIdx and greatest index offset (ie.  the offset at the point of jmp).
        BETTER EXPLAIN WHAT BaseSymIdx is.
        '''
        if None not in (self.baseIdx, self.baseoff):
            return self.baseIdx, self.baseoff

        def _cb_peel_idx(path, symobj, ctx):
            '''
            This is for troubleshooting and analysis only.
            '''
            logger.debug( ' PATH: %r\n SYMOBJ: %r\n CTX: %r\n' % (path, symobj, ctx))

        def _cb_mark_longpath(path, symobj, ctx):
            '''
            Determine a long path through an AST.
            Long paths mean we have the most complete subcomponent
            '''
            #logger.debug( ' PATH: %r\n SYMOBJ: %r\n CTX: %r\n' % (path, symobj, ctx))
            longpath = ctx.get('longpath')
            if longpath is None:
                ctx['longpath'] = list(path)
            elif len(path) > len(longpath):
                ctx['longpath'] = list(path)

        (csemu, cseff), aspath, fullpath = self.getSymbolikParts()

        idx = self.getComplexIdx()
        if idx is None:
            raise v_exc.NoComplexSymIdxException(self)

        idx.reduce()

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
        #logging.info("LONGPATH: " + '\n'.join([repr(x) for x in longpath]))
        for symobj in longpath:
            last = count
            count = len(self.getBoundingCons(symobj))
            logger.debug(" longpath constraints %d: %r" % (count, symobj))

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

        logger.debug(" longpath DONE: (%r) %r" % (offset, symobj))
        # now figure what was cut, and what impact it has.
        self.baseIdx = symobj
        self.baseoff = offset

        return symobj, offset

    def getNormalizedConstraints(self):
        '''
        takes in a complex index symbolik state
        returns a list of tuples of (SYMT_CON_??, offset)
        '''
        retcons = []
        baseIdx, baseoff = self.getBaseSymIdx()
        SKIPS = (SYMT_CON_GT, SYMT_CON_GE, SYMT_CON_LT, SYMT_CON_LE)

        for con in self.getBoundingCons(baseIdx): # merge the two
            cons = con.cons

            if not cons.symtype in SKIPS:
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
                logger.debug("Ignoring Constraint not based on Index: %r" % cons)
                continue

            if cons.symtype == SYMT_CON_LT and symcmp.solve() == 0:
                #logger.debug("SKIPPING Constraint Checking for Zero: %r" % cons)
                continue

            conthing, consoff = peelIdxOffset(symvar)

            if conthing != baseIdx:
                logger.debug("Constraint not bound-limiting for our index: %r  != %r" % (conthing, baseIdx))
                continue

            logger.debug("Valid bound-limiting Constraint: %r\n\t%r\n\t%r\t%r + %r" % (cons, symvar, conthing, consoff, symcmp))
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
        upper = None    # the largest index used.  max=self.max_cases
        count = 0
        baseoff = None

        try:
            while lower is None or (lower == 0 and upper is None) or (upper is not None and upper <= lower): # note: this will fail badly when it fails.  make this dependent on the codepathgen
                # get the index we'll be looking for in constraints
                lower = 0           # the smallest index used.  most often wants to be 0
                upper = None        # the largest index used.  max=self.max_cases

                if count != 0:
                    (csemu, cseffs), asp, fullp = self.getSymbolikParts(doNext=True)

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

                logger.info("Determined bounds: %r %r\n" % (lower, upper))
        except StopIteration:
            pass

        # if upper is None:  we need to exercise upper until something doesn't make sense.  
        # we also need to make sure we don't analyze non-Switches.  
        if upper is None:
            upper = self.max_cases

        if lower < baseoff:
            # assume the compiler doesn't adjust the index below 0
            lower = baseoff

        #logger.info("Lower: %r\tUpper: %r\tOffset: %r\tIndex: %r", lower, upper, baseoff, smplIdx)
        self.upper = upper
        self.lower = lower
        self.baseoff = baseoff

        return self.lower, self.upper, self.baseoff

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

        idxtype, symIdx = self.getSymIdx()

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
                    logger.info("analyzing ptr: 0x%x->0x%x" % (eff.va, solution))

                    if not self.vw.isValidPointer(solution):
                        logger.warning(("ARRRG: Non-pointer in ReadMemory???"))

                    target = semu.readSymMemory(eff.symaddr, eff.symsize)
                    size = target.getWidth()
                    derefs.append((eff.va, symaddr, solution, target.solve(), size))

            endlen = len(semu.getTrackInfo())

        return derefs



    #### higher level functionality
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
        start = time.time()

        # only support branching switch-cases (ie, not calls)
        if not (self.jmpop.iflags & envi.IF_BRANCH):
            logger.info("makeSwitch: exiting: not a branch opcode: 0x%x: %r", self.jmpop.va, self.jmpop)
            return

        # skip any that already have xrefs away from (already been discovered?)
        if len(vw.getXrefsFrom(self.jmpva)):
            logger.info('skipping existing switchcase: 0x%x', self.jmpva)
            return

        # if we aren't a part of a function, where are we?
        funcva = self.vw.getFunction(self.jmpva)
        if funcva is None:
            logger.error("ERROR getting function for jmpva 0x%x", self.jmpva)
            return

        # skip when the function is the first instruction (PLT?)
        if funcva == self.jmpva:
            logger.info("skipping: function va IS jmpva 0x%x (PLT?)", self.jmpva)
            return

        # skip if insufficient instructions in the function to have an interesting switchcase.
        instrcount = vw.getFunctionMeta(funcva, 'InstructionCount')
        if instrcount < self.min_func_instr_size:
            logger.info("Ignoring jmp in too small a function: %d instructions (0x%x)", instrcount, self.jmpva)
            return

        # skip if we don't have a multiply in the jmpva calculation (always going to be an offset 
        # into a pointer array, most often of size 2+)
        jnode, jemu, jaeffs = self.getSymbolikJmpBlock()
        jmptgt = self.getJmpSymVar()
        if not hasMul(jmptgt.update(jemu)):
            logger.info("skipping: JmpSymVar doesn't have multiplication! (0x%x)", self.jmpva)
            return


        # create a tracking emulator and populate with with current "csp" state
        try:
            # relying on getBounds() to bail on non-switch-cases
            lower, upper, baseoff = self.getBounds()
            if None in (lower, ):
                logger.info("something odd in count/offset calculation...(%r,%r,%r) skipping 0x%x...",
                            lower, upper, baseoff, self.jmpva)
                return

            count = upper - lower + 1
            if count > self.max_cases:
                if count > self.case_failure:
                    logger.warning("TOO many switch cases detected: %d.  FAILURE.  Skipping this dynamic branch (0x%x)", count, self.jmpva)
                    return

                logger.warning("too many switch cases during analysis: %d   limiting to %d (0x%x)", count, self.max_cases, self.jmpva)
                count = self.max_cases

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
                    logger.info("found invalid pointer.  quitting.  (0x%x in 0x%x)", addr, self.jmpva)
                    break

                tloc = vw.getLocation(addr)
                if tloc is not None and tloc[0] != addr:
                    # pointing at something not right.  must be done.
                    logger.info("found overlapping location at 0x%x (cur: 0x%x).  quitting. (0x%x)", \
                            addr, tloc[0], self.jmpva)
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
                            logger.info("target location (0x%x) has xrefs. (0x%x)", addr, self.jmpva)
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

        except StopIteration as e:
            logger.info("Switchcase Analysis BOMBED OUT (Couldn't Find Valid Path) 0x%x\n%r", self.jmpva, e)

        except v_exc.SymIdxNotFoundException as e:
            logger.info("Switchcase Analysis BOMBED OUT (SymIdx) 0x%x\n%r", self.jmpva, e)

        except v_exc.NoComplexSymIdxException as e:
            logger.info("Switchcase Analysis BOMBED OUT (SymIdx=%r \t ComplexIdx=None) 0x%x\n%r", e.sc.getSymIdx(), self.jmpva, e)

        except PathForceQuitException as e:
            logger.warning("Switchcase Analysis BOMBED OUT (Path Timeout!) 0x%x\n%r", self.jmpva, e)
            vw.setVaSetRow('SwitchCases_TimedOut', (self.jmpva, self.timeout) )

        except RuntimeError as e:
            if 'StopIteration' in repr(e):
                logger.info("Switchcase Analysis BOMBED OUT (Couldn't Find Valid Path) 0x%x", self.jmpva)
            else:
                logger.warning("Switchcase Analysis BOMBED OUT 0x%x\n%r", self.jmpva, e, exc_info=1)

        except Exception as e:
            logger.warning("Switchcase Analysis BOMBED OUT 0x%x\n%r", self.jmpva, e, exc_info=1)

        logger.debug("Symswitchcase took %.3f for jump at virtual address 0x%x", time.time() - start, self.jmpva)


    def markDerefs(self):
        '''
        Apply xrefs for derefs (the tables) and mark pointers or numbers (for offset-based switches)
        '''
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

        idxtype, symidx = self.getSymIdx()
        logger.info('getSymIdx: %r/%r (0x%x)', idxtype, symidx, self.jmpva)

        jmptgt = self.getSymTarget()
        lower, upper, offset = self.getBounds()
        logger.debug( " itercases: %r %r %r %r (0x%x)", symidx, lower, upper, offset, self.jmpva)

        # use a TrackingSymbolikEmulator so we get the "readSymMemory()" function actually hitting 
        # the r/o data from our VivWorkspace
        symemu = TrackingSymbolikEmulator(vw)
        symemu.setSymSnapshot(csemu.getSymSnapshot())

        logger.debug("jmpva: 0x%x\t\tsymidx: %r", self.jmpva, symidx)   # TODO: we return either a Var name string or a SymObj (for Mem types)... should we just stick with the symbolik object?  since we're removing the ties to getSymVariable() and moving to replaceObj() and our nifty 'jmpidx' variable.
        if idxtype == SYMT_VAR:
            symidx = Var(symidx, self.vw.psize)
        replaceObj(jmptgt, symidx, Var('jmpidx', symidx.getWidth()))
        #workJmpTgt = jmptgt.update(emu=symemu)


        for idx in range(lower-offset, upper-offset+1):
            symemu.setSymVariable('jmpidx', Const(idx, 8))
            workJmpTgt = jmptgt.update(emu=symemu)  # would "jmptgt.solve(vals={'jmpidx': idx})" work?
            logger.info(" itercases: workJmpTgt: %r (0x%x)", workJmpTgt, self.jmpva)
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

        logger.info("OUTSTRINGS: %s (0x%x)", repr(outstrings), jmpva)

        idxs = '_'.join(outstrings)
        casename = "case_%s_%x" % (idxs, addr)

        curname = vw.getName(addr)
        if curname is not None:
            ## TODO:   if already labeled, chances are good this is other cases in the same function.
            ## either simply add the new outstrings to the current one or we need to keep track of what
            ## calls each and with what switchcase/index info.  VaSet?  or do we want this to only expect
            ## the same function to call each one, and all part of the same Switchcase?
            logger.info("%s is already labeled %s", casename, curname)

        vw.makeName(addr, casename)
        logger.info(casename)

    vw.makeName(jmpva, "switch_%.8x" % jmpva)
    logger.info("making switchname: switch_%.8x", jmpva)


def link_up(vw, jmpva, array, count, baseoff, baseva=None, itemsize=None):
    '''
    Manually link up a switchcase for which we have a pointer/offset array

    If baseva is None, the array is treated as a pointer array
    Otherwise, the numbers in the array are treated as offset from baseva

    If itemsize is not None, itemsize is treated as the size of each item
        in the array (in bytes. ie. 2, 4, 8 bytes)
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

        logger.info("0x%x analyzeSwitch: idx: %s \t address: 0x%x", jmpva, idx, addr)

        # determining when to stop identifying switch-cases can be tough.  we assume that we have the 
        # correct number handed into this function in "count", but currently we'll stop analyzing
        # if we run into trouble.
        if not vw.isValidPointer(addr):
            logger.info("found invalid pointer.  quitting.  (0x%x in 0x%x)" % addr, jmpva)
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


def analyzeFunction(vw, fva, timeout=None):
    '''
    Function analysis module.
    This is inserted right after codeblock analysis
    '''
    targetNewFunctions(vw, fva)

    lastdynlen = 0
    dynbranches = vw.getVaSet('DynamicBranches')
    done = vw.getMeta('analyzedDynBranches')
    if done is None:
        done = []

    if not timeout:
        timeout = vw.config.viv.analysis.symswitchcase.timeout_secs

    # because the VaSet is often updated during analysis, we have to check to see if there are new 
    # dynamic branches to analyze.
    while lastdynlen != len(dynbranches):
        lastdynlen = len(dynbranches)
        for jmpva, (none, oprepr, bflags) in list(dynbranches.items()):
            if bflags & envi.BR_PROC:   # skip calls
                continue

            try:
                funcva = vw.getFunction(jmpva)
                if funcva != fva:
                    # jmp_indir is for the entire VivWorkspace.  
                    # we're just filtering to this function here.
                    # this should be checked again when codeblocks are allowed to 
                    #   be part of multiple functions.
                    continue

                if jmpva in done:
                    logger.info("...skipping 0x%x - already done", jmpva)
                    continue

                done.append(jmpva)
                analyzeJmp(vw, jmpva, timeout)
            except:
                logger.info('Exception processing SwitchCase in function 0x%x', fva, exc_info=1)

        dynbranches = vw.getVaSet('DynamicBranches')
    vw.setMeta('analyzedDynBranches', done)
    # TODO: we need a better way to store changing lists/dicts, that don't show up in the UI.  VaSet would be great, but ugly

def analyzeJmp(vw, jmpva, timeout=None):
    if vw.getVaSetRow('SwitchCases', jmpva) is not None:
        logger.info("...skipping 0x%x - SwitchCases already has it?", jmpva)
        return

    if vw.getVaSetRow('SwitchCases_TimedOut', jmpva) is not None:
        logger.warning("Reanalyzing TimedOut SwitchCase: 0x%x (timeout=%r secs)", jmpva, timeout)
        logger.debug("Removing 0x%x from VaSet SwitchCases_TimedOut", jmpva)
        vw.delVaSetRow('SwitchCases_TimedOut', jmpva)

    try:
        sc = SwitchCase(vw, jmpva, timeout)
        sc.analyze()
    except e_exc.ArchNotImplemented:
        logger.info("... skipping.  Current architecture has no SymbolikTranslator")



