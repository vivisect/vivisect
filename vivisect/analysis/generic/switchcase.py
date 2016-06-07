'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases from Microsoft and GCC, and theoretically others,
which use pointer arithetic to determine code path for each case.

This will not connect switch cases which are actually explicit cmp/jz in the code.
'''
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

import envi
import envi.archs.i386 as e_i386

import vivisect
import vivisect.cli as viv_cli
import vivisect.tools.graphutil as viv_graph
import vivisect.symboliks.emulator as vs_emu
import vivisect.symboliks.analysis as vs_anal
import vivisect.symboliks.substitution as vs_sub
import vivisect.analysis.generic.codeblocks as vagc

from vivisect.symboliks.common import *



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
# FIXME: make all switchcase analysis for a given function cohesive (ie. don't finish up with naming until the entire function has been analyzed).  this will break cohesion if we use the CLI to add switchcases, but so be it.
# FIXME: overlapping case names...  doublecheck the naming algorithm.  ahh... different switch-cases colliding on handlers?  is this legit?  or is it because we don't stop correctly?
# CHECK: are the algorithms for "stopping" correct?  currently getting 1 switch case for several cases in libc-32
# FIXME: cycle multiple paths until getting a good one.
# TODO: regrange description of Symbolik Variables... normalize so "eax" and "eax+4" make sense.
# FIXME: libc 64bit doesn't work at all.  why?
# TODO: complete documentation
MAX_INSTR_COUNT  = 10
MAX_CASES   = 5000


signed_fmts = (
    None,
    '<b',
    '<h',
    None,
    '<i',
    None,
    None,
    None,
    '<q',
    )

class TrackingSymbolikEmulator(vs_emu.SymbolikEmulator):
    '''
    TrackingSymbolikEmulator tracks reads.  where they occur, where they read from, and
    returns as much info as possible if not discrete data.
    '''
    _trackReads = []
    def __init__(self, vw):
        vs_emu.SymbolikEmulator.__init__(self, vw)
        self.__width__ = vw.psize
    
    def clear(self):
        self._trackReads = []
        
    def track(self, va, addrval, val):
        self._trackReads.append((va, addrval, val))
        
    def getTrackInfo(self):
        return self._trackReads
        
    def readSymMemory(self, symaddr, symsize, vals=None):
        '''
        The readSymMemory API is designed to read from the given
        symbolik address for the specified symbolik length.  If the
        current symbolik emulator has no knowledge of the state of
        the given memory symbol, None is returned.
        '''
        addrval = symaddr.solve(emu=self, vals=vals)
        
        # check for a previous write first...
        symmem = self._sym_mem.get(addrval)
        if symmem != None:
            symaddr, symval = symmem
            self.track(self.getMeta('va'), symaddr, symval)
            return symval

        # If we have a workspace, check it for meaningful symbols etc...
        if self._sym_vw != None:
            # Make a special check for imports...
            loc = self._sym_vw.getLocation(addrval)
            if loc != None:
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
                    
                if size in (1,2,4,8):
                    # return real number from memory
                    val, = self._sym_vw.readMemoryFormat(addrval, signed_fmts[size])
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
        if symobj.solve() == ctx['compare']:
            ctx['contains'] = True
            ctx['path'] = tuple(path)

        return symobj

    ctx = { 'compare'  : subobj,
            'contains' : False,
            'path'     : []
          }
    symobj.walkTree(_cb_contains, ctx)
    return ctx.get('contains'), ctx['path']

# Command Line Analysis and Linkage of Switch Cases - Microsoft and Posix - taking arguments "count" and "offset"
def makeSwitch(vw, jmpva, count, offset, funcva=None):
    '''
    Determine jmp targets's and wire codeblocks together at a switch case based on 
    provided count and offset data.

        count   - number of sequential switch cases this jmp handles (iterates)
        offset  - offset from the start of the function 
                    (eg. sometimes "index -= 25" on the way to jmpva)

    algorithm goes a little like this:
    * start at the dynamic branch (jmp reg)
    * back up instruction at a time until we hit a CODE xref to or from that instruction, 
            or we run out of instructions, or we cross a max-instruction threshold.
    * walk forward, evaluating the dynamic branch symbolikally, until we have only the 
            switch/case index
    * iterate "count" times through the switch case indexes starting from 0
    * wire dynamic branch to next code snippits
    * make sure codeblocks exist for any new code / trigger codeflow analysis
    * name switches and cases


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
    special_vals = {}
    archname = vw.getMeta("Architecture")

    if funcva == None:
        funcva = vw.getFunction(jmpva)

    if funcva == None:
        logger.error("ERROR getting function for jmpva 0x%x", jmpva)
        return

    if count > MAX_CASES:
        logger.warn("too many switch cases during analysis: %d   limiting to %d", count, MAX_CASES)
        count = MAX_CASES

    # build opcode and check initial requirements
    op = vw.parseOpcode(jmpva)

    if not (op.iflags & envi.IF_BRANCH):    # basically, not isCall() is what we're after.  
        return
    if len(op.opers) != 1:
        return

    oper = op.opers[0]

    # get jmp reg
    rctx = vw.arch.archGetRegCtx()
    reg = oper.reg
    regname = rctx.getRegisterName(reg)

    # fix up for PIE_ebx (POSIX Position Independent Exe)
    # this requires that PIE_ebx be set up from previous analysis 
    #   (see vivisect.analysis.i386.thunk_bx)
    ebx = vw.getMeta("PIE_ebx")
    if ebx and archname == 'i386':
        if regname == 'ebx':
            logger.warn("PIE_ebx but jmp ebx.  bailing!")
            # is this even valid?  are we caring if they ditch ebx?  could be wrong.
            return
        special_vals['ebx'] = ebx
        
    oplist = [op]

    # zero in on the details of the switch
    found, satvals, rname, jmpreg, deref_ops, debug  = \
            zero_in(vw, jmpva, oplist, special_vals)
   
    if not found:
        logger.info("Switch Analysis failure, couldn't zero-in on constraints/values for dynamic branch")
        return debug
    
    # iterate through switch cases
    cases, memrefs, interval = \
            iterCases(vw, satvals, jmpva, jmpreg, rname, count, special_vals) 

    # should we analyze for derefs here too?  should that be part of the SysEmu?
    logger.info("cases:       %s", repr(cases))
    logger.info("deref ops:   %s", repr(deref_ops))
    #logger.info("reads:       %s", repr(symemu._trackReads))

    # the difference between success and failure...
    if not len(cases):
        logger.info("no cases found... doesn't look like a switch case.")
        return
    
    # mark names and make appropriate xrefs
    #FIXME: make all switchcase analysis for a given function cohesive.  this will break if we use the CLI to add switchcases, but so be it.
    makeNames(vw, jmpva, offset, cases, deref_ops, memrefs, interval)

    # store some metadata in a VaSet
    vw.setVaSetRow('SwitchCases', (jmpva, oplist[0].va, len(cases)) )

    vagc.analyzeFunction(vw, funcva)

def zero_in(vw, jmpva, oplist, special_vals={}):
    '''
    track the ideal instructions to symbolikally analyze for the switch case.
    
        jmpva - the va of the jmp <reg> opcode
        oplist - the list of opcodes occuring in this analysis
        special_vals - dict of "reg":val pairs which must be (eg.  EBX for PIE binaries)
    '''
    # setup symboliks/register context objects
    rctx = vw.arch.archGetRegCtx()
    op = vw.parseOpcode(jmpva)
    oper = op.opers[0]
    reg = oper.reg
    regname = rctx.getRegisterName(reg)
    sctx = vs_anal.getSymbolikAnalysisContext(vw)
    xlate = sctx.getTranslator()
    
    # first loop...  back up the truck to the start of the codeblock
    ###  NOTE: we are backing up past significant enough complexity to get the jmp data, 
    ###     next we'll zero in on the "right" ish starting point

    oplist = []
    deref_ops = []

    #raw_input("ABOUT TO START: oplist: \n    %s" % '\n    '.join([repr(op) for op in oplist]))
    icount = 0
    xreflen = 0
    nva = jmpva

    #FIXME:  this relies on backing up, but not intelligently.  this may need to have a codeblock-aware intelligent pather.
    try:

        while not xreflen and icount < MAX_INSTR_COUNT:
            loc = vw.getLocation(nva-1)
            if loc == None:
                # we've reached the beginning of whatever blob of code we know about
                # if we hit this, likely we're at the beginning of a code chunk we've
                # manually called code.
                break
            
            nva = loc[0]
            xrefs = vw.getXrefsTo(nva, vivisect.REF_CODE)
            xrefs.extend(vw.getXrefsFrom(nva, vivisect.REF_CODE))       # FIXME: broken for libc.
            xreflen = len(xrefs)
            icount += 1
            
            op = vw.parseOpcode(nva)
            oplist.insert(0, op)
            for oper in op.opers:
                if oper.isDeref():
                    deref_ops.append(op)

        #raw_input("oplist: \n    %s\n" % '\n    '.join([repr(op) for op in oplist]))
    except Exception, e:
        print "ERROR: %s" % repr(e)
        sys.excepthook(*sys.exc_info())
    '''


    cbva = vw.getCodeBlock(jmpva)
    nva = cbva[vivisect.CB_VA]

    while nva <= jmpva:
        op = vw.parseOpcode(nva)
        oplist.append(op)
        for oper in op.opers:
            if oper.isDeref():
                deref_ops.insert(0, op)

        nva += len(op)
    '''

    # now go forward until we have a lock
    # this next section tells us where we can resolve the jmp target, and what reg is used
    # to determine switch case.
    satvals = None

    # analyze current opcodes.  if we don't solve symreg, pop earliest opcode and try again
    debug = []
    found = False
    while len(oplist) and not found:
        
        # get effects for the "current suspect" opcodes
        xlate.clearEffects()
        for xop in oplist:
            logger.info("%x %s", xop.va, xop)
            xlate.translateOpcode(xop)

        effs = xlate.getEffects()

        # determine which reg is the switch case index (and other details)
        found, rname, jmpreg, val, satvals = \
                determineCaseIndex(vw, jmpva, regname, special_vals, effs, debug)

        logger.info("0x%x %s %s", val, satvals, deref_ops)
        logger.debug("\n".join([str(op) for op in oplist]))

        if not found:
            oplist.pop(0)

    return found, satvals, rname, jmpreg, deref_ops, debug

def getUnknowns(symvar):
    # determine unknown registers in this symbolik object
    def _cb_grab_vars(path, symobj, ctx):
        '''
        walkTree callback for grabbing Var objects
        '''
        if symobj.symtype == SYMT_VAR:
            if symobj.name not in ctx:
                ctx.append(symobj.name)

    unks = []
    symvar.walkTree(_cb_grab_vars, unks)
    return unks

def determineCaseIndex(vw, jmpva, regname, special_vals, effs, debug):
    '''
    determine what the switch case index register is, basically from the jmpva and 
    previously discovered info
    
    args:
        jmpva - the va of the jmp <reg> opcode
        regname - the <reg> from jmp <reg>.  must be string as it would appear in SymEmu
        special_vals - dict of "reg":val pairs which must be (eg.  EBX for PIE binaries)
        effs - symbolik effects of the opcodes for this analysis
        debug - list to store debugging data [deprecated]

    returns:
        found - whether we found the case index or not
        rname - index register name
        satvals - dict of register/value pairs 
    '''
    logger.info("\njmpva: %r\nregname: %r\nspecial_vals: %r\neffs: %r\ndebug: %r\n",\
            jmpva, regname, special_vals, effs, debug)

    rnames = vw.arch.archGetRegisterGroup('general')

    found = False
    satvals = None
    semu = TrackingSymbolikEmulator(vw)
    aeffs = semu.applyEffects(effs)

    # grab the JMP register we're solving for
    jmpreg = semu.getSymVariable(regname)
    jmpreg.reduce(semu)
   

    # Ideally, we will be able to "just do" this, not worrying about compiler-specific versions...
    # However, to get to that ideal (if possible), let's break down what we need from a C perspective
    # as well as what types we currently need to deal with to get there...

    unks = getUnknowns(jmpreg)
    logger.debug("unknown regs: %s", unks)
    
    # this solving model only accounts for two regs being fabricated:  
    #       the index reg, and the module baseva (optional)
    if len(unks) > 2:
        logger.debug("bailing on this dynamic branch: more than 2 unknowns in this AST")
        return False, 0, 0, 0

    # cycle through possible case regs, check for valid location by providing index 0
    for rname in unks:
        if rname not in rnames:
            continue

        # check for case 0 (should always work, when we have the right index reg)
        vals = { rname:0 }
        
        if rname in special_vals:
            continue

        vals.update(special_vals)
            
        logger.info("vals: %s", repr(vals))

        # fix up for windows base - why PE only?  FIXME: CAN THIS HAPPEN ELSEWHERE?  like when PIE_ebx is set and added to special_vals?
        if vw.getMeta('Format') == 'pe':
            imagename = vw.getFileByVa(jmpva)
            imagebase = vw.filemeta[imagename]['imagebase']
            
            # variables known to hold  imagebase  (this is compiler-specific as much as arch)
            ibvars = vw.arch.archGetRegisterGroup('switch_mapbase')
            if ibvars == None:
                return

            for kvar in ibvars:
                if rname == kvar:
                    continue
                vals[kvar] = imagebase
            
        # magic happens
        logger.info(repr(jmpreg))
        val = jmpreg.solve(emu=semu, vals=vals)
        
        if vw.isValidPointer(val):
            found = True
            satvals = vals
            break

        if not found:
            # try method 2:  this could potentially replace previous method.
            #   use a small "run" (from just before the jmpva) to determine our interesting regs
            #   and a long "run" (from funcva to jmpva) to determine values of regs
            fva = vw.getFunction(jmpva)
            sctx = vs_anal.getSymbolikAnalysisContext(vw)
            fgraph = sctx.getSymbolikGraph(fva)
            cb = vw.getCodeBlock(jmpva)
            paths = viv_graph.getCodePathsTo(fgraph, cb[0])
            sympaths = sctx.getSymbolikPaths(fva, graph=fgraph, paths=paths)
            
            symemu, symeffs = sympaths.next()   # FIXME: take all paths?

            vals = {}
            for reg in unks:
                regobj = symemu.getSymVariable(reg)
                if not regobj.isDiscrete():
                    vals[reg] = 0
                    continue
                if not vw.isValidPointer(regobj.solve()):
                    continue
                vals[reg] = regobj.solve()

            print '\n'.join([str(x) for x in symeffs])
            print symemu.getSymSnapshot()[2]
            semu.setSymSnapshot(({},{},{},''))
            val = jmpreg.solve(emu=semu, vals=vals) & e_bits.u_maxes[jmpreg.getWidth()]
            print jmpreg, " = ", hex(val),
            print '\n\t' + '\n\t'.join(["%s: %s" % (reg, repr(symemu.getSymVariable(reg).reduce())) for reg in unks])
            raw_input("PRESS ENTER")
            print '\n'

            # if we have a Const, it's a base of some sort.
            # the other unknown should be the index.

            # not finished here.
            if vw.isValidPointer(val):
                for reg in unks:
                    if vals.get(reg) == None:
                        rname = reg
                        break
                found = True
                satvals = vals
                break

            debug.append((symemu.getSymSnapshot(), jmpreg))

    # we don't find all switch cases this way.  gcc amd64 can set the image base higher in the code.  should we skip this and just use the output address delta to determine index?  see crunchtime from ctf quals 2016.



    logger.info("\ndebug: %r\n", debug)
    return found, rname, jmpreg, val, satvals

def getRegRange(count, rname, satvals, special_vals, terminator_addr, start=0, interval=1):
    '''

    '''
    regrange = vs_sub.srange(rname, int(count), imin=start, iinc=interval)
    for reg,val in satvals.items():
        if val == 0: continue

        regrange *= vs_sub.sset(reg, [val])
        terminator_addr.append(val)
        
    for sreg, sval in special_vals.items():
        regrange *= vs_sub.sset(sreg, [sval])
        terminator_addr.append(sval)

    return regrange

def iterCases(vw, satvals, jmpva, jmpreg, rname, count, special_vals):
    '''
    let's exercize the correct number of instances, as provided by "count"

        satvals - 
        jmpva - the va of the jmp <reg> opcode
        jmpreg - symbolik state of jmp <reg> register
        rname - string name of jmp <reg> register (as found in SymEmu)
        count - identified number of cases handled by this dynbranch
        special_vals - dict of "reg":val pairs which must be (eg.  EBX for PIE binaries)
    '''
    fva = vw.getFunction(jmpva)
    cases = {}
    memrefs = []
    testaddrs = []
    terminator_addr = []
    interval = 1
    
    # simplify the symbolik jmpreg
    jmpreg.reduce()

    # play toys
    symemu = TrackingSymbolikEmulator(vw)
    testemu = TrackingSymbolikEmulator(vw)

    # check once through to see if our index reg moves by 1, 4, or 8
    regrange = getRegRange(2, rname, satvals, special_vals, [], interval=interval)

    # ratchet through the regrange set to determine index interval
    for vals in regrange:
        testemu.setMeta('va', jmpva)
        memsymobj = symemu._trackReads[-1][1]
        addr = memsymobj.solve(emu=testemu, vals=vals)
        testaddrs.append(addr)

    # check for periodic changes:
    logger.info("finished interval test: %s", repr(testaddrs))

    # SPECIAL_ONE_OFF: sometimes the index reg moves by "ptrsize" for each case
    delta = testaddrs[1] - testaddrs[0]
    if delta == 1:
        logger.info("SPECIAL: Register Index increases by <ptrsize>, not incremental")
        interval = vw.psize
    elif delta == vw.psize:
        logger.debug("Register Index is incremental")
    else:
        logger.critical("REGISTER INDEX increments by ptrsize/2??!?")
        print repr(testaddrs)
    #FIXME: does this ever end up being psize/2?  (ie.  4-bytes on a 64-bin binary?)  if so, then what?

    logger.debug("== %s / %s means interval of %s ", repr(vw.psize), repr(delta), repr(interval))
    
    # now we iterate through the index register values to identify case handlers
    regrange = getRegRange(count*interval, rname, satvals, special_vals, terminator_addr, interval=interval)

    for vals in regrange:
        symemu.setMeta('va', jmpva)
        addr = jmpreg.solve(emu=symemu, vals=vals)
        
        memsymobj = symemu._trackReads[-1][1]
        memtgt = memsymobj.solve(emu=symemu, vals=vals)
        
        logger.info("0x%x analyzeSwitch: vals: %s \taddr: 0x%x \t tgt address: 0x%x", jmpva, vals, addr, memtgt)
        
        # determining when to stop identifying switch-cases can be tough.  we assume that we have the 
        # correct number handed into this function in "count", but currently we'll stop analyzing
        # if we run into trouble.
        if not vw.isValidPointer(addr):
            logger.info("found invalid pointer.  quitting.")
            break
        
        tloc = vw.getLocation(addr)
        if tloc != None and tloc[0] != addr:
            # pointing at something not right.  must be done.
            logger.info("found overlapping location.  quitting.")
            break
     
        if addr in terminator_addr:
            logger.info("found terminator_addr.  quitting.")
            break
        
        if len(cases):
            xrefsto = vw.getXrefsTo(memtgt)
            # if there is an xref to this target from within this function, we're still ok... ish?
            if len(xrefsto):
                good = True
                for xrfr,xrto,xrt,xrtinfo in xrefsto:
                    xrfrfunc = vw.getFunction(xrfr)
                    if xrfrfunc == fva:
                        continue

                    # this one is *not* in the same function
                    good = False

                if not good:
                    logger.info("target location (0x%x) has xrefs.", memtgt)
                    break
        
        # this is a valid thing, we have locations...  match them up
        memrefs.append((memtgt, addr, delta))
        l = cases.get(addr, [])
        l.append( vals[rname]/interval )
        cases[addr] = l

    return cases, memrefs, interval


UNINIT_CASE_INDEX = -2

def makeNames(vw, jmpva, offset, cases, deref_ops, memrefs, interval):
    '''
    Create names and xrefs for each identified case.
    '''
    # FIXME:  use memrefs to tie xrefs for the dynamic ptr/offsets and make ptr/numbers

    logger.info("memrefs: %r", memrefs)

    for addr, l in cases.items():
        # make the connections (REF_CODE) and ensure the cases continue as code.
        vw.addXref(jmpva, addr, vivisect.REF_CODE)
        nloc = vw.getLocation(addr)
        if nloc == None:
            vw.makeCode(addr)

        outstrings = []
        combined = False
        start = last = UNINIT_CASE_INDEX
        for x in l:
            # we make the case numbers into their originally intended form here:
            case = x + offset

            if case == last+1:
                if not combined:
                    combined = True
                    start = last
            else:
                if combined:
                    combined = False
                    outstrings.append("%Xto%X" % (start, last))
                elif last != UNINIT_CASE_INDEX:
                    outstrings.append("%X" % last)
            last = case

        # catch the last one if highest cases are combined
        if combined:
            combined = False
            outstrings.append("%Xto%X" % (start, last))
        else:
            outstrings.append("%X" % case)

        logger.info("OUTSTRINGS: %s", repr(outstrings))

        idxs = '_'.join(outstrings)
        casename = "case_%s_%x" % (idxs, addr)

        curname = vw.getName(addr) 
        if curname != None:
            logger.warn("%s is already labeled %s", casename, curname)

        vw.makeName(addr, casename)
        logger.info(casename)
   
    # link the dereferencing opcode to the base of deref points.
    dropslen = len(deref_ops)
    if dropslen:
        if dropslen > 1:
            logger.warn("deref_ops has more than one option (using last): %r", deref_ops)

        # make xrefs and numbers/pointer
        memop = deref_ops[-1]   # FIXME: Hack.  if we have two, one will get all xrefs
        for memref,tgt,delta in memrefs:
            vw.addXref(memop.va, memref, vivisect.REF_DATA)
            vw.addXref(memref, tgt, vivisect.REF_PTR)

            if delta == vw.psize:
                vw.makePointer(memref)
            else:
                vw.makeNumber(memref, delta)
    
    # let's make switches easily findable.
    vw.makeName(jmpva, "switch_%.8x" % jmpva)
    logger.info("making switchname: switch_%.8x", jmpva)

def getMuls(symvar):
    def _cb_grab_muls(path, symobj, ctx):
        '''
        walkTree callback to grab Mul objects
        '''
        if symobj.symtype == SYMT_OPER_MUL:
            if (path,symobj) not in ctx:
                ctx.append((path, symobj))
            
        return symobj

    muls = []
    symvar.walkTree(_cb_grab_muls, muls)
    return muls

def determineCountOffset(vw, jmpva):
    '''
    Analyze instructions (symboliks) leading up to a "jmp reg" to determine which switch cases are 
    handled here.

    we start out with symbolik analysis of routed paths from the start of the function to the dynamic jmp.

    this function is also used to weed out a lot of non-switch case dynamic branches
    '''
    #FIXME: some switch-cases (ELF PIE, libc:sub_020bbec0) use indexes that increment by ptrsize, not by 1.  back up farther?  identify that?
    sctx = vs_anal.getSymbolikAnalysisContext(vw)
    funcva = vw.getFunction(jmpva)

    op = vw.parseOpcode(jmpva)
    xlate = sctx.getTranslator()
    graph = viv_graph.buildFunctionGraph(vw, funcva)
    jmpcb = vw.getCodeBlock(jmpva)

    sctx.getSymbolikGraph(funcva, graph)

    pathGenFactory = viv_graph.PathGenerator(graph)

    pathGen=pathGenFactory.getFuncCbRoutedPaths(funcva, jmpcb[0], 1, maxsec=20)

    # get symbolik paths
    spaths = sctx.getSymbolikPaths(funcva, pathGen, graph=graph)

    lower = upper = -1
    while lower >= upper:
        #############

        semu, aeffs = spaths.next()

        # FIXME: one path using this method may allow for layered opposing constraints, potentially
        #        giving imposible results.  this shouldn't cause a problem, but it's possible.
        # FIXME: TODO: regrange type of constraints calculation :)

        operobj = xlate.getOperObj(op, 0)
        if operobj.symtype != SYMT_VAR:
            logger.debug('\nBAILING - not a VAR memory location')
            return None,None,None

        acon = semu.getSymVariable(operobj.name)

        # grab all the constraints from start of function to here.
        fullcons = [eff for eff in aeffs if eff.efftype==EFFTYPE_CONSTRAIN]
        logger.debug('\nFULLCONS: \n%s','\n\t'.join([repr(con) for con in fullcons]))

        # grab all the multiplication effects in the operand ast.  muls will be 
        # used to calculate a pointer into some offset/address array
        #muls = getMuls(acon)
        #logger.debug('\nMULS: \n'+repr(muls))

        lower, upper, baseoff = getBoundsFromConstraints(fullcons)
    return lower, upper, baseoff

def getBoundsFromConstraints(fullcons):
    # this algorithm depends on the index variable being in the last Const comparison.  
    # these options may be best used with a heuristic (if one doesn't make us happy, 
    # fall through to a different one).

    # loop through fullcons looking for comparisons of symidx against Consts.  last one should be our index.
    idx = None
    upper = None
    lower = 0
    
    for constraint in fullcons[::-1]:
        cons = constraint.cons
        # skip constraints that aren't bounding index
        if not cons.symtype in (SYMT_CON_GT, SYMT_CON_GE, SYMT_CON_LT, SYMT_CON_LE): 
            logger.debug("SKIPPING: cons = %s", repr(cons))
            continue

        logger.debug(repr(cons))


        if cons._v1.symtype == SYMT_CONST:
            symcmp = cons._v1
            symvar = cons._v2
        elif cons._v2.symtype == SYMT_CONST:
            symvar = cons._v1
            symcmp = cons._v2
        else:
            # neither side of the constraint is a CONST.  this constraint does 
            # not set static bounds on idx
            continue

        # once we identify idx, stick with it.
        if idx == None:
            idx = symvar
            baseoff = peelIndexOffset(idx)

        # check the sanity of this constraint's symvar against our idx.
        d = 0
        if idx != symvar:
            d = idx.solve() - symvar.solve()
            if abs(d) > 1000:
                continue

        logger.info("* "+ repr(cons._v2)+ "\t"+repr(cons._v1)+"\t"+ repr(cons))

        # FIXME: probably don't want to reset things once they're set.  this could be some other indicator for a nested switchcase...  need to get one of those for testing.
        if cons.symtype == SYMT_CON_GT:
            # this is setting the lower bound
            if lower != 0:
                logger.info("==we're resetting a lower bound:  %s -> %s", lower, symcmp)
            lower = symcmp.solve() + 1
            
        elif cons.symtype == SYMT_CON_GE:
            # this is setting the lower bound
            if lower != 0:
                logger.info("==we're resetting a lower bound:  %s -> %s", lower, symcmp)
            lower = symcmp.solve()
            
        elif cons.symtype == SYMT_CON_LT:
            # this is setting the upper bound
            if upper != None:
                logger.info("==we're resetting a upper bound:  %s -> %s", upper, symcmp)
            upper = symcmp.solve() - 1
            
        elif cons.symtype == SYMT_CON_LE:
            # this is setting the upper bound
            if upper != None:
                logger.info("==we're resetting a upper bound:  %s -> %s", upper, symcmp)
            upper = symcmp.solve()

        else:
            logger.info("Unhandled comparator:  %s\n", repr(cons))

    # if upper is None:  we need to exercize upper until something doesn't make sense.  
    # we also need to make sure we don't analyze non-Switches.  
    if upper == None:
        upper = MAX_CASES

    # if we failed to identify the index, the upper bound, or the offset, 
    if idx == None:
        logger.info("NON-SWITCH analysis terminated: 0x%x", jmpva)
        return None, None, None

    logger.info("Lower: %r\tUpper: %r\tOffset: %r\tIndex: %r", lower, upper, baseoff, idx)

    #################
    return lower, upper, baseoff

def peelIndexOffset(symobj):
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

        elif isinstance(symobj, o_sextend):
            # sign-extension is irrelevant for indexes
            pass

        # anything else and we're done peeling
        else:
            break

        # this algorithm depends on only taking left turns
        symobj = symobj.kids[0]

    return offset

def analyzeFunction(vw, fva):
    '''
    Function analysis module.
    This is inserted right after codeblock analysis
    '''

    lastdynlen = 0
    dynbranches = vw.getVaSet('DynamicBranches')
    
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

            lower, upper, baseoff = determineCountOffset(vw, jmpva)
            if None in (lower, ): 
                logger.info("something odd in count/offset calculation... skipping 0x%x...", jmpva)
                continue

            count = (upper - lower) + 1
            makeSwitch(vw, jmpva, count, baseoff, funcva=fva)

        dynbranches = vw.getVaSet('DynamicBranches')

def analyzeFunction_new(vw, fva):
    '''
    Function analysis module.
    This is inserted right after codeblock analysis
    '''

    lastdynlen = 0
    dynbranches = vw.getVaSet('DynamicBranches')
    
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

            sc = SwitchCase(vw, jmpva)
            sc.analyze()

        dynbranches = vw.getVaSet('DynamicBranches')



# for use as vivisect script
if globals().get('vw'):
    verbose = vw.verbose
    vw.verbose = True

    vw.vprint("Starting...")
    jmpva = int(argv[1],16)
    count = int(argv[2])
    offset = 0
    if len(argv) > 3:
        offset = int(argv[3])

    makeSwitch(vw, jmpva, count, offset)

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

class SwitchCase:
    def __init__(self, vw, jmpva):
        self.vw = vw
        self.jmpva = jmpva

        self.cspath = None
        self.aspath = None
        self.fullpath = None

        self._sgraph = None
        self._codepath = None
        self._codepathgen = None

        self.upper = None
        self.lower = None
        self.count = None
        self.baseoff = None

        self.sctx = vs_anal.getSymbolikAnalysisContext(vw)
        self.xlate = self.sctx.getTranslator()

        # ??
        self.longSemu = TrackingSymbolikEmulator(vw)
        self.shortSemu = TrackingSymbolikEmulator(vw)

        self.idxregidx = None
        self.idxregname = None
        self.idxregsymbx = None

        self.jmpregidx = None
        self.jmpregname = None
        self.jmpregsymbx = None


    def analyze(self):
        self.count, self.baseoff = self.determineCountOffset()
        if None in (lower, ): 
            logger.info("something odd in count/offset calculation... skipping 0x%x...", self.jmpva)
            return

        self.makeSwitch(vw, jmpva, count, baseoff, funcva=fva)

    def getJmpSymVar(self):
        '''
        returns the Simple Symbolik state of the dynamic target of the branch/jmp
        '''
        if self.jmpregsymbx != None:
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
            if cspath[0].getSymVariable(unk).isDiscrete():
                continue
            potentials.append(unk)
            
        raw_input(repr(potentials))
        return potentials[0]

    def getCountOffset(self):
        '''
        Limited value function.
        '''
        lower, upper, offset = self.getBounds()
        return (upper-lower), offset


    def getConstraints(self):
        csp, asp, fullp = self.getSymbolikParts()

        cons = [eff for eff in fullp[1] if eff.efftype==EFFTYPE_CONSTRAIN]
        [con.reduce() for con in cons]
        return cons

    def getBounds(self):
        csp, asp, fullp = self.getSymbolikParts()

        smplIdx = self.getSymIdx()
        logger.debug("smplIdx: %r", smplIdx)
        lower = self.lower
        upper = self.upper
        baseoff = self.baseoff
       
        try:
            while upper <= lower: # FIXME: this will fail badly when it fails.  make this dependent on the codepathgen
                # get the index we'll be looking for in constraints
                cplxIdx = csp[0].getSymVariable(smplIdx)
                logger.debug("cplxIdx: %r", cplxIdx)

                # identify constraints which contain our index
                boundingcons = [con for con in self.getConstraints() if contains(con, cplxIdx)[0] ]
                logger.debug("%r", boundingcons)

                lower = 0
                upper = None
                baseoff = None

                for con in boundingcons:
                    cons = con.cons

                    if not cons.symtype in (SYMT_CON_GT, SYMT_CON_GE, SYMT_CON_LT, SYMT_CON_LE): 
                        logger.debug("SKIPPING: cons = %s", repr(cons))
                        return None, None, None

                    logger.debug(repr(cons))


                    if cons._v1.symtype == SYMT_CONST:
                        symcmp = cons._v1
                        symvar = cons._v2
                    elif cons._v2.symtype == SYMT_CONST:
                        symvar = cons._v1
                        symcmp = cons._v2
                    else:
                        # neither side of the constraint is a CONST.  this constraint does 
                        # not set static bounds on idx
                        continue

                    # once we identify idx, stick with it.
                    if baseoff == None:
                        baseoff = peelIndexOffset(symvar)
                        # try peeling until it we're left with cplxIdx
                        # can this be a separate function?  doesn't seem likely

                    ## check the sanity of this constraint's symvar against our idx.
                    #d = 0
                    #if idx != symvar:
                        #d = idx.solve() - symvar.solve()
                        #if abs(d) > 1000:
                            #continue

                    logger.info("* "+ repr(cons._v2)+ "\t"+repr(cons._v1)+"\t"+ repr(cons))

                    # FIXME: probably don't want to reset things once they're set.  this could be some other indicator for a nested switchcase...  need to get one of those for testing.
                    if cons.symtype == SYMT_CON_GT:
                        # this is setting the lower bound
                        if lower != 0: logger.info("==we're resetting a lower bound:  %s -> %s", lower, symcmp)
                        lower = symcmp.solve() + 1
                        
                    elif cons.symtype == SYMT_CON_GE:
                        # this is setting the lower bound
                        if lower != 0: logger.info("==we're resetting a lower bound:  %s -> %s", lower, symcmp)
                        lower = symcmp.solve()
                        
                    elif cons.symtype == SYMT_CON_LT:
                        # this is setting the upper bound
                        if upper != None: logger.info("==we're resetting a upper bound:  %s -> %s", upper, symcmp)
                        upper = symcmp.solve() - 1
                        
                    elif cons.symtype == SYMT_CON_LE:
                        # this is setting the upper bound
                        if upper != None: logger.info("==we're resetting a upper bound:  %s -> %s", upper, symcmp)
                        upper = symcmp.solve()

                    else:
                        logger.info("Unhandled comparator:  %s\n", repr(cons))

                csp, asp, fullp = self.getSymbolikParts(next=True)

                smplIdx = self.getSymIdx()
                #print "smplIdx: %r" % smplIdx
               
        except StopIteration:
            pass

        # if upper is None:  we need to exercize upper until something doesn't make sense.  
        # we also need to make sure we don't analyze non-Switches.  
        if upper == None:
            upper = MAX_CASES

        logger.info("Lower: %r\tUpper: %r\tOffset: %r\tIndex: %r", lower, upper, baseoff, smplIdx)
        self.upper = upper
        self.lower = lower
        self.baseoff = baseoff

        #################
        return self.lower, self.upper, self.baseoff





        '''  parse this out...
smplIdx: 'rax'

cplxIdx: o_sub(o_and(o_or(o_sub(Mem(Const(0xbfbfefdc,8), Const(0x00000001,8)),Const(0x00000030,8),1),o_and(Call(Const(0x02000a20,8),8, argsyms=[]),Const(0xffffffffffffff00,8),8),1),Const(0xffffffff,4),4),Const(0x00000001,8),4)

[ConstrainPath( 0x02000bf5, Const(0x02000bfc,8), eq(o_and(Call(Const(0x02000a50,8),8, argsyms=[]),Const(0xffffffff,4),4),Const(0x00000000,8)) ), ConstrainPath( 0x02000c68, Const(0x02000c6a,8), le(o_and(o_sub(o_and(o_or(o_sub(Mem(Const(0xbfbfefdc,8), Const(0x00000001,8)),Const(0x00000030,8),1),o_and(Call(Const(0x02000a20,8),8, argsyms=[]),Const(0xffffffffffffff00,8),8),1),Const(0xffffffff,4),4),Const(0x00000001,8),4),Const(0x000000ff,1),1),Const(0x00000004,8)) )]

            '''

    def getSymbolikParts(self, next=False):
        '''
        Puts together a path from the start of the function to the jmpva, breaking off the last 
        codeblock, and returning the symbolik path for both sections:
        cspath = (emu, effs) for the "context" path (from function start)
        aspath = (emu, effs) for the last codeblock

        FIXME: this needs to be able to handle things like "thunk_bx" calls.
        '''
        if not next and self.cspath != None and self.aspath != None:
            return self.cspath, self.aspath, self.fullpath
        
        vw = self.vw
        sctx = self.sctx
        jmpva = self.jmpva

        fva = vw.getFunction(jmpva)
        cb = vw.getCodeBlock(jmpva)
        if cb == None:
            return None
        cbva, cbsz, cbfva = cb

        if self._sgraph == None:
            self._sgraph = sctx.getSymbolikGraph(fva)

        if self._codepathgen == None:
            self._codepathgen = viv_graph.getCodePathsTo(self._sgraph, cbva)

        self._codepath = self._codepathgen.next()
        contextpath = self._codepath[:-1]
        analpath = self._codepath[-1:]

        self.cspath = sctx.getSymbolikPaths(fva, graph=self._sgraph, paths=[contextpath]).next()
        self.aspath = sctx.getSymbolikPaths(fva, graph=self._sgraph, paths=[analpath]).next()
        self.fullpath = sctx.getSymbolikPaths(fva, graph=self._sgraph, paths=[self._codepath]).next()


        return self.cspath, self.aspath, self.fullpath

