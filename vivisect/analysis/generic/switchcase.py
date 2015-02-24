'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases from Microsoft and GCC, and theoretically others,
which use pointer arithetic to determine code path for each case.

This will not connect switch cases which are actually explicit cmp/jz in the code.
'''

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
# TODO: Clean up isinstance() calls to use symtype
# TODO: ARCHITECTURE ABSTRACTION: 
#       ibvars = ('rdi','rsi', 'r8', 'r9', 'r10')
#       i386RegOper (architecture-specific list of operands which would be used by switch-cases
#       regidx_sets (list of register indexes)
# TODO: check offsets/pointers used to calculate jmp targets and either makeNumber or makePointer
# TODO: complete documentation
# TODO: try codeblock-granularity and see if that's good enough, rather than backing up by instruction
# TODO: figure out why KernelBase has switches which are not being discovered
MAX_INSTR_COUNT  = 10
MAX_CASES   = 3600

regidx_sets = {
    'amd64': range(16),
    'i386':  range(8),
}
    
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
                    symval = self._sym_vw.readMemValue(addrval, size)
                    self.track(self.getMeta('va'), symaddr, symval)
                    return Const(symval, size)
                
                # return string  (really?)
                symval = self._sym_vw.readMemory(addrval, size)
                self.track(self.getMeta('va'), symaddr, symval)
                return symval

        return Mem(symaddr, symsize)

            
def _cb_grab_vars(path, symobj, ctx):
    '''
    walkTree callback for grabbing Var objects
    '''
    if isinstance(symobj, Var):
        if symobj.name not in ctx:
            ctx.append(symobj.name)

def _cb_grab_unks(path, symobj, ctx):
    '''
    walkTree callback for grabbing unknown primitives: Var, Arg, Mem
    '''
    if symobj.isDiscrete():
        pass

    elif isinstance(symobj, Var):
        if symobj not in ctx:
            ctx.append(symobj)

    elif isinstance(symobj, Arg):
        if symobj not in ctx:
            ctx.append(symobj)
        
    elif isinstance(symobj, Mem):
        if symobj not in ctx:
            ctx.append(symobj)
        
    return symobj
    
def _cb_grab_muls(path, symobj, ctx):
    '''
    walkTree callback to grab Mul objects
    '''
    if isinstance(symobj, o_mul):
        if (path,symobj) not in ctx:
            ctx.append((path, symobj))
        
    return symobj

def _cb_contains(path, symobj, ctx):
    '''
    walkTree callback for determining presence within an AST
    '''
    if symobj.solve() == ctx['compare']:
        ctx['contains'] = True

    # FIXME: this needs to have some way to back up the path (chop) when 
    # AST ascention occurs
    if isinstance(symobj, Operator):
        if not ctx['contains']:
            ctx['path'].append(symobj)

    return symobj

def contains(symobj, subobj):
    '''
    search through an AST looking for a particular type of thing.
    '''
    ctx = { 'compare'  : subobj,
            'contains' : False,
            'path'     : []
          }
    symobj.walkTree(_cb_contains, ctx)
    return ctx.get('contains'), ctx

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
        print("ERROR getting function for jmpva 0x%x" % jmpva)
        return

    if count > MAX_CASES:
        print("too many switch cases during analysis: %d   limiting to %d" % (count, MAX_CASES))
        count = MAX_CASES

    # build opcode and check initial requirements
    op = vw.parseOpcode(jmpva)
    if not (op.iflags & envi.IF_BRANCH):    # basically, not isCall() is what we're after.  
        return
    if len(op.opers) != 1:
        return
    oper = op.opers[0]

    validOper = False
    # make sure we have an approved register for switch cases for the architecture
    validOperands = vw.arch.archGetValidSwitchcaseOperand()
    for voper in validOperands:
        if isinstance(oper, voper):
            validOper = True
            break

    if not validOper:
        return

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
            if vw.verbose: print("PIE_ebx but jmp ebx.  bailing!")
            # is this even valid?  are we caring if they ditch ebx?  could be wrong.
            return
        special_vals['ebx'] = ebx
        
    oplist = [op]

    found, satvals, rname, jmpreg, deref_ops, debug  = zero_in(vw, jmpva, oplist, special_vals)
   
    if not found:
        if vw.verbose: print("Switch Analysis FAILURE")
        return debug
    

    cases, memrefs, interval = iterCases(vw, satvals, jmpva, jmpreg, rname, count, special_vals) 
    # should we analyze for derefs here too?  should that be part of the SysEmu?
    if vw.verbose:
        print("cases:       ", repr(cases))
        print("deref ops:   ", repr(deref_ops))
        #print("reads:       ", repr(symemu._trackReads))

    # the difference between success and failure...
    if not len(cases):
        if vw.verbose: print("no cases found... doesn't look like a switch case.")
        return
   
    makeNames(vw, jmpva, offset, cases, deref_ops, memrefs, interval)

    # store some metadata in a VaSet
    vw.setVaSetRow('SwitchCases', (jmpva, oplist[0].va, len(cases)) )

    vagc.analyzeFunction(vw, funcva)

def zero_in(vw, jmpva, oplist, special_vals={}):
    '''
    track the ideal instructions to symbolikally analyze for the switch case.
    '''
    # setup symboliks/register context objects
    import vivisect.symboliks.analysis as vs_anal
    rctx = vw.arch.archGetRegCtx()
    op = vw.parseOpcode(jmpva)
    oper = op.opers[0]
    reg = oper.reg
    regname = rctx.getRegisterName(reg)
    sctx = vs_anal.getSymbolikAnalysisContext(vw)
    xlate = sctx.getTranslator()
    
    icount = 0
    xreflen = 0
    nva = jmpva
    # first loop...  back up the truck  until we hit some change in basic block
    ###  NOTE: we are backing up past significant enough complexity to get the jmp data, 
    ###     next we'll zero in on the "right" ish starting point
    deref_ops = []
    while not xreflen and icount < MAX_INSTR_COUNT:
        loc = vw.getLocation(nva-1)
        if loc == None:
            # we've reached the beginning of whatever blob of code we know about
            # if we hit this, likely we're at the beginning of a code chunk we've
            # manually called code.
            break
        
        nva = loc[0]
        xrefs = vw.getXrefsTo(nva, vivisect.REF_CODE)
        xrefs.extend(vw.getXrefsFrom(nva, vivisect.REF_CODE))
        xreflen = len(xrefs)
        icount += 1
        
        op = vw.parseOpcode(nva)
        oplist.insert(0, op)
        for oper in op.opers:
            if oper.isDeref():
                deref_ops.append(op)


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
            if vw.verbose: print("%x %s"% (xop.va, xop))
            xlate.translateOpcode(xop)

        effs = xlate.getEffects()
        found, rname, jmpreg, val, satvals = determineCaseIndex(vw, jmpva, regname, special_vals, effs, debug)

        if vw.verbose: 
            print(hex(val), satvals, deref_ops)
            if vw.verbose > 1: 
                print("\n".join([str(op) for op in oplist]))

        if not found:
            oplist.pop(0)

    return found, satvals, rname, jmpreg, deref_ops, debug

def determineCaseIndex(vw, jmpva, regname, special_vals, effs, debug, verbose=False):
    '''
    determine what the switch case index register is, basically from the jmpva and 
    previously discovered info
    '''
    print "\n%s\n%s\n%s\n%s\n%s\n"%(jmpva, regname, special_vals, effs, debug)

    archname = vw.getMeta("Architecture")
    satvals = None

    rctx = vw.arch.archGetRegCtx()
    rnames = [rctx.getRegisterName(x) for x in regidx_sets[archname]]

    found = False
    semu = TrackingSymbolikEmulator(vw)
    aeffs = semu.applyEffects(effs)

    # grab the JMP register we're solving for
    jmpreg = semu.getSymVariable(regname)
    jmpreg.reduce(semu)
   

    # Ideally, we will be able to "just do" this, not worrying about compiler-specific versions...
    # However, to get to that ideal (if possible), let's break down what we need from a C perspective
    # as well as what types we currently need to deal with to get there...

    # determine unknown registers
    unks = []
    jmpreg.walkTree(_cb_grab_vars, unks)
    if vw.verbose>1: print("unknown regs: %s" % unks)
    
    # this solving model only accounts for two regs being fabricated:  the index reg, and the module baseva (optional)
    if len(unks) > 2:
        return False, 0, 0, 0

    # cycle through possible case regs, check for valid location by providing index 0
    #### ARG! NASTIEST THING EVAR.  i feel dirty
    for rname in unks:
        if rname not in rnames:
            continue

        # check for case 0 (should always work)
        vals = { rname:0 }
        
        if rname in special_vals:
            continue

        vals.update(special_vals)
            
        if vw.verbose: print("vals: ", repr(vals))

        # fix up for windows base - why PE only?
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
        if vw.verbose: print(repr(jmpreg))
        val = jmpreg.solve(emu=semu, vals=vals)
        
        if vw.isValidPointer(val):
            found = True
            satvals = vals
            break

        debug.append((semu.getSymSnapshot(), jmpreg))

    return found, rname, jmpreg, val, satvals

def getRegRange(count, rname, satvals, special_vals, terminator_addr, start=0, interval=1, verbose=False):
    regrange = vs_sub.srange(rname, int(count), imin=start, iinc=interval)
    for reg,val in satvals.items():
        if val == 0: continue

        #FIXME: REMOVE
        if verbose > 1:
            print(repr(vars(regrange)))
            print(repr(vars(vs_sub.sset(reg, [val]))))
        regrange *= vs_sub.sset(reg, [val])
        terminator_addr.append(val)
        
    for sreg, sval in special_vals.items():
        regrange *= vs_sub.sset(sreg, [sval])
        terminator_addr.append(sval)

    return regrange

def iterCases(vw, satvals, jmpva, jmpreg, rname, count, special_vals):
    '''
    let's exercize the correct number of instances, as provided by "count"
    '''
    terminator_addr = []
    symemu = TrackingSymbolikEmulator(vw)
    jmpreg.reduce()
    cases = {}
    memrefs = []
   
    # check once through to see if our index reg moves by 1, 4, or 8
    interval = 1
    regrange = getRegRange(2, rname, satvals, special_vals, [], interval=interval, verbose=vw.verbose)
    testaddrs = []
    testemu = TrackingSymbolikEmulator(vw)
    for vals in regrange:
        testemu.setMeta('va', jmpva)
        memsymobj = symemu._trackReads[-1][1]
        addr = memsymobj.solve(emu=testemu, vals=vals)
        testaddrs.append(addr)

    # check for periodic changes:
    if vw.verbose>1: print("finished interval test: %s" % repr(testaddrs))

    # SPECIAL_ONE_OFF: sometimes the index reg moves by "ptrsize" for each case
    delta = testaddrs[1] - testaddrs[0]
    if delta == 1:
        interval = vw.psize

    if vw.verbose>1: print("== %s / %s means interval of %s " % (repr(vw.psize), repr(delta), repr(interval)))
    
    # now we iterate through the index register values to identify case handlers
    regrange = getRegRange(count*interval, rname, satvals, special_vals, terminator_addr, interval=interval)
    for vals in regrange:
        symemu.setMeta('va', jmpva)
        addr = jmpreg.solve(emu=symemu, vals=vals)
        
        memsymobj = symemu._trackReads[-1][1]
        memtgt = memsymobj.solve(emu=symemu, vals=vals)
        
        if vw.verbose: print(hex(jmpva), "analyzeSwitch: vals: ", vals, "\taddr: ", hex(addr), "\t tgt address: 0x%x" % (memtgt))
        
        # determining when to stop identifying switch-cases can be tough.  we assume that we have the 
        # correct number handed into this function in "count", but currently we'll stop analyzing
        # if we run into trouble.
        if not vw.isValidPointer(addr):
            if vw.verbose: print("found invalid pointer.  quitting.")
            break
        
        tloc = vw.getLocation(addr)
        if tloc != None and tloc[0] != addr:
            # pointing at something not right.  must be done.
            if vw.verbose: print("found overlapping location.  quitting.")
            break
     
        if addr in terminator_addr:
            if vw.verbose: print("found terminator_addr.  quitting.")
            break
        
        if len(cases) and len(vw.getXrefsTo(memtgt)):
            if vw.verbose: print("target location (0x%x) has xrefs." % memtgt)
            break
        
        # this is a valid thing, we have locations...  match them up
        memrefs.append((memtgt, addr))
        l = cases.get(addr, [])
        l.append( vals[rname]/interval )
        cases[addr] = l
        # FIXME: make the target locations numbers?  pointers? based on size of read.

    return cases, memrefs, interval


UNINIT_CASE_INDEX = -2

def makeNames(vw, jmpva, offset, cases, deref_ops, memrefs, interval):
    # creating names for each case
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

        if vw.verbose: print("OUTSTRINGS: ", repr(outstrings))

        idxs = '_'.join(outstrings)
        # FIXME: check for existing name (this might possibly be part of another switchcase)?
        vw.makeName(addr, "case_%s_%x" % (idxs, addr))
        if vw.verbose:  print((addr, "case_%s_%x" % (idxs, addr)))
   
    # link the dereferncing opcode to the base of deref points.
    if len(deref_ops):
        memop = deref_ops[-1]   # FIXME: Hack.  if we have two, one will get all xrefs
        for memref,tgt in memrefs:
            vw.addXref(memop.va, memref, vivisect.REF_DATA)
            vw.addXref(memref, tgt, vivisect.REF_PTR)
    
    # let's make switches easily findable.
    vw.makeName(jmpva, "switch_%.8x" % jmpva)
    vw.vprint("making switchname: switch_%.8x" % jmpva)

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
    semu, aeffs = spaths.next()

    # FIXME: one path using this method may allow for layered opposing constraints, potentially
    #        giving imposible results.  this shouldn't cause a problem, but it's possible.

    operobj = xlate.getOperObj(op, 0)
    if operobj.symtype != SYMT_VAR:
        if vw.verbose > 1: 
            print('\nBAILING - not a VAR memory location')
            return None,None,None

    acon = semu.getSymVariable(operobj.name)

    # grab all the constraints from start of function to here.
    fullcons = [eff for eff in aeffs if eff.efftype==EFFTYPE_CONSTRAIN]
    if vw.verbose > 1: print('\nFULLCONS: \n','\n\t'.join([repr(con) for con in fullcons]))

    # grab all the multiplication effects in the operand ast.  muls will be 
    # used to calculate a pointer into some offset/address array
    muls = []
    acon.walkTree(_cb_grab_muls, muls)
    if vw.verbose > 1: print('\nMULS: \n'+repr(muls))

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
            if vw.verbose>2: print("SKIPPING: cons = %s" % (repr(cons)))
            continue

        if vw.verbose > 2: print(repr(cons))


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
            baseoff = peel(idx)


        # check the sanity of this constraint's symvar against our idx.
        d = 0
        if idx != symvar:
            d = idx.solve() - symvar.solve()
            if abs(d) > 1000:
                continue

        if vw.verbose: print("* "+ repr(cons._v2)+ "\t"+repr(cons._v1)+"\t"+ repr(cons))


        # FIXME: probably don't want to reset things once they're set.  this could be some other indicator for a nested switchcase...  need to get one of those for testing.
        if cons.symtype == SYMT_CON_GT:
            # this is setting the lower bound
            if lower != 0:
                if vw.verbose: print("==we're resetting a lower bound:  %s -> %s" % (lower, symcmp))
            lower = symcmp.solve() + 1
            
        elif cons.symtype == SYMT_CON_GE:
            # this is setting the lower bound
            if lower != 0:
                if vw.verbose: print("==we're resetting a lower bound:  %s -> %s" % (lower, symcmp))
            lower = symcmp.solve()
            
        elif cons.symtype == SYMT_CON_LT:
            # this is setting the upper bound
            if upper != None:
                if vw.verbose: print("==we're resetting a upper bound:  %s -> %s" % (upper, symcmp))
            upper = symcmp.solve() - 1
            
        elif cons.symtype == SYMT_CON_LE:
            # this is setting the upper bound
            if upper != None:
                if vw.verbose: print("==we're resetting a upper bound:  %s -> %s" % (upper, symcmp))
            upper = symcmp.solve()

        else:
            if vw.verbose: print("Unhandled comparator:  %s\n" % repr(cons))

    # if we failed to identify the index, the upper bound, or the offset, 
    if None in (idx, upper):
        if vw.verbose: print("NON-SWITCH analysis terminated: 0x%x" % jmpva)
        return (None, None, None)

    if vw.verbose: print("Lower: %d\tUpper: %d\tOffset: %d\tIndex: %s" % (lower, upper, baseoff, idx))

    return lower, upper, baseoff

def peel(symobj):
    offset = 0
    while True:
        # peel off o_subs and size-limiting o_ands and o_sextends
        if isinstance(symobj, o_and) and symobj.kids[1].isDiscrete() and symobj.kids[1].solve() in e_bits.u_maxes:
            pass

        elif isinstance(symobj, o_sub):
            offset += symobj.kids[1].solve()

        elif isinstance(symobj, o_sextend):
            pass

        # anything else and we're done peeling
        else:
            break

        # this algorithm depends on only taking left turns
        symobj = symobj.kids[0]

    return offset

def analyzeFunction(vw, fva):
    '''
    This is inserted as a function analysis module, right after codeblock analysis

    '''

    lastdynlen = 0
    dynbranches = vw.getVaSet('DynamicBranches')
    
    # because the VaSet is often updated during analysis, we have to check to see if there are new 
    # dynamic branches to analyze.
    while lastdynlen != len(dynbranches):
        lastdynlen = len(dynbranches)
        for jmpva, (none, oprepr, bflags) in dynbranches.items():
            funcva = vw.getFunction(jmpva)
            if funcva != fva:
                # jmp_indir is for the entire VivWorkspace.  
                # we're just filtering to this function here.
                continue

            lower, upper, baseoff = determineCountOffset(vw, jmpva)
            if None in (lower, upper): 
                if vw.verbose: print("something odd in count/offset calculation... skipping 0x%x..." % jmpva)
                continue

            count = (upper - lower) + 1
            makeSwitch(vw, jmpva, count, baseoff, funcva=fva)

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
