'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases from Microsoft and GCC, and theoretically others,
which use pointer arithetic to determine code path for each case.

This will not connect switch cases which are actually explicit cmp/jz in the code.
'''
import envi
import envi.archs.i386 as e_i386

import vivisect
import vivisect.tools.graphutil as viv_graph
import vivisect.symboliks.analysis as vs_anal
import vivisect.analysis.generic.codeblocks as vagc

import envi
import envi.archs.i386 as e_i386
import vivisect
import vivisect.cli as viv_cli

import vivisect.symboliks.emulator as vs_emu
import vivisect.symboliks.substitution as vs_sub
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

MAX_ICOUNT  = 10
MAX_CASES   = 3600

regidx_sets = {
    'amd64': range(16),
    'i386':  range(8),
}
    
class SymEmu(vs_emu.SymbolikEmulator):
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
    if isinstance(symobj, Var):
        if symobj.name not in ctx:
            ctx.append(symobj.name)

def _cb_grab_unks(path, symobj, ctx):
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
    if isinstance(symobj, o_mul):
        if (path,symobj) not in ctx:
            ctx.append((path, symobj))
        
    return symobj

def _cb_contains(path, symobj, ctx):
    if symobj.solve() == ctx['compare']:
        ctx['contains'] = True

    # FIXME: this needs to have some way to back up the path (chop) when 
    # AST ascention occurs
    if isinstance(symobj, Operator):
        if not ctx['contains']:
            ctx['path'].append(symobj)

    return symobj

def contains(symobj, subobj):
    ctx = { 'compare'  : subobj,
            'contains' : False,
            'path'     : []
          }
    symobj.walkTree(_cb_contains, ctx)
    return ctx.get('contains'), ctx


    
# Command Line Analysis and Linkage of Switch Cases - Microsoft and Posix - taking arguments "count" and "offset"
def makeSwitch(vw, jmpva, count, offset, funcva=None):
    '''
    Determine jmp's and wire codeblocks together at a switch case based on 
    provided count and offset data.

        count   - number of sequential switch cases this jmp handles (iterates)
        offset  - offset from the start of the function 
                    (eg. sometimes "index -= 25" on the way to jmpva)
    '''
    icount = 0
    xreflen = 0
    nva = va = jmpva
    if funcva == None:
        funcva = vw.getFunction(jmpva)

    if funcva == None:
        print "ERROR getting function for jmpva 0x%x" % jmpva
        return

    # build opcode and check initial requirements
    op = vw.parseOpcode(jmpva)
    if not (op.iflags & envi.IF_BRANCH):
        return
    if len(op.opers) != 1:
        return
    oper = op.opers[0]
    if not isinstance(oper, e_i386.i386RegOper):   # i386/amd64
        return
    
    oplist = [op]
    
    # setup symboliks/register context objects
    import vivisect.symboliks.analysis as vs_anal
    rctx = vw.arch.archGetRegCtx()
    sctx = vs_anal.getSymbolikAnalysisContext(vw)
    xlate = sctx.getTranslator()
    archname = vw.getMeta("Architecture")
    
    # get jmp reg
    reg = oper.reg
    regname = rctx.getRegisterName(reg)

    # this requires that PIE_ebx be set up from previous analysis 
    #   (see vivisect.analysis.i386.thunk_bx)
    ebx = vw.getMeta("PIE_ebx")
    if ebx and archname == 'i386':
        if regname == 'ebx':
            if vw.verbose: print "PIE_ebx but jmp ebx.  bailing!"
            # is this even valid?  are we caring if they ditch ebx?  could be wrong.
            return
        
    # first loop...  back up the truck  until we hit some change in basic block
    ###  NOTE: we are backing up past significant enough complexity to get the jmp data, 
    ###     next we'll zero in on the "right" ish starting point
    deref_ops = []
    while not xreflen and icount < MAX_ICOUNT:
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
    found = False
    rnames = [rctx.getRegisterName(x) for x in regidx_sets[archname]]
    satvals = None

    # analyze current opcodes.  if we don't solve symreg, pop earliest opcode and try again
    oplist.insert(0,None)
    debug = []
    while len(oplist) and not found:
        oplist.pop(0)
        
        # get effects for the "current suspect" opcodes
        xlate.clearEffects()
        for xop in oplist:
            if vw.verbose: print "%x %s"% (xop.va, xop)
            xlate.translateOpcode(xop)
            
        semu = SymEmu(vw)
        effs = xlate.getEffects()
        aeffs = semu.applyEffects(effs)
   
        # grab the JMP register we're solving for
        jmpreg = semu.getSymVariable(regname)
        jmpreg.reduce(semu)
        
        # determine unknown registers
        unks = []
        jmpreg.walkTree(_cb_grab_vars, unks)
        if vw.verbose: print "unknown regs: %s" % unks
        
        # our models only account for two regs being fabricated
        if len(unks) > 2:
            continue

        # cycle through possible case regs, check for valid location by providing index 0
        #### ARG! NASTIEST THING EVAR.  i feel dirty
        for rname in unks:
            if rname not in rnames:
                continue

            # check for case 0 (should always work)
            vals = { rname:0 }
            
            # fix up for PIE_ebx (POSIX Position Independent Exe)
            if ebx != None:
                if rname == 'ebx': continue
                vals['ebx'] = ebx
                
            if vw.verbose: print "vals: ", repr(vals)

            # fix up for windows base
            if vw.getMeta('Format') == 'pe':
                imagename = vw.getFileByVa(jmpva)
                imagebase = vw.filemeta[imagename]['imagebase']
               
                # FIXME: abstract this out by architecture
                if archname == 'amd64':
                    kvars = ('rdi','rsi', 'r8', 'r9', 'r10')
                elif archname == 'i386':
                    kvars = ('edi', 'esi')
                    
                for kvar in kvars:
                    if rname == kvar:
                        continue
                    vals[kvar] = imagebase
                
            # magic happens
            if vw.verbose: print repr(jmpreg)
            val = jmpreg.solve(emu=semu, vals=vals)
            
            if vw.isValidPointer(val):
                if vw.verbose: print hex(val), vals, deref_ops
                found = True
                satvals = vals
                if vw.verbose: print "\n".join([str(op) for op in oplist])
                break
            debug.append((semu.getSymSnapshot(), jmpreg))
    
    # Ideally, we will be able to "just do" this, not worrying about compiler-specific versions...
    # However, to get to that ideal (if possible), let's break down what we need from a C perspective
    # as well as what types we currently need to deal with to get there...

    # DIFFERENT TYPES:
    # * VS's multidimensional
    # * VS's single-dimension
    # * Posix single dimension
    # * Any of them with offset (EBX for Posix PIE, VS's base reg (typically 0x10000))

    # What we need:
    # * Resultant location for xrefs (iterative)
    # * Index symboliks (for Constraint checking, addition/subtraction)
    # * potentially, base va offset?  if only to identify the others.... but maybe not.


    # How do we get from jmpreg (which is a very limited scope symboliks) to full scope symboliks run (from funcva)?
    #   * va effect comparison?

    if not found:
        if vw.verbose: print "Switch Analysis FAILURE"
        return debug
    

    ############################################################################
    ### let's exercize the correct number of instances, as provided by "count"
    terminator_addr = []
    
    if count > MAX_CASES:
        print "too many switch cases during analysis: %d   limiting to %d" % (count, MAX_CASES)
        count = MAX_CASES

    regrange = vs_sub.srange(rname, int(count))
    for reg,val in satvals.items():
        if val == 0: continue

        regrange *= vs_sub.sset(reg, [val])
        terminator_addr.append(val)
        
    if ebx:
        regrange *= vs_sub.sset('ebx', [ebx])
        terminator_addr.append(ebx)

    symemu = SymEmu(vw)
    jmpreg.reduce()
    cases = {}
    memrefs = []
    
    for vals in regrange:
        symemu.setMeta('va', va)
        addr = jmpreg.solve(emu=symemu, vals=vals)
        
        memsymobj = symemu._trackReads[-1][1]
        memtgt = memsymobj.solve(emu=symemu, vals=vals)
        
        if vw.verbose: print hex(va), "analyzeSwitch: vals: ", vals, "\taddr: ", hex(addr), "\t tgt address: 0x%x" % (memtgt)
        
        if not vw.isValidPointer(addr):
            if vw.verbose: print "found invalid pointer.  quitting."
            break
        
        tloc = vw.getLocation(addr)
        if tloc != None and tloc[0] != addr:
            # pointing at something not right.  must be done.
            if vw.verbose: print "found overlapping location.  quitting."
            break
     
        if addr in terminator_addr:
            if vw.verbose: print "found terminator_addr.  quitting."
            break
        
        if len(cases) and len(vw.getXrefsTo(memtgt)):
            if vw.verbose: print "target location (0x%x) has xrefs." % memtgt
            break
        
        # this is a valid thing, we have locations...  match them up
        memrefs.append((memtgt, addr))
        l = cases.get(addr, [])
        l.append(vals[rname])
        cases[addr] = l
        # FIXME: make the target locations numbers?  pointers? based on size of read.
        
    # should we analyze for derefs here too?  should that be part of the SysEmu?
    if vw.verbose:
        print "cases:       ", repr(cases)
        print "deref ops:   ", repr(deref_ops)
        #print "reads:       ", repr(symemu._trackReads)

    # the difference between success and failure...
    if not len(cases):
        if vw.verbose: print "no cases found... doesn't look like a switch case."
        return
    
    # creating names for each case
    for addr, l in cases.items():
        # make the connections (REF_CODE) and ensure the cases continue as code.
        vw.addXref(va, addr, vivisect.REF_CODE)
        nloc = vw.getLocation(addr)
        if nloc == None:
            vw.makeCode(addr)

        outstrings = []
        combined = False
        start = last = -1
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
                elif last != -1:
                    outstrings.append("%X" % last)
            last = case

        # catch the last one if highest cases are combined
        if combined:
            combined = False
            outstrings.append("%Xto%X" % (start, last))
        else:
            outstrings.append("%X" % case)

        if vw.verbose: print "OUTSTRINGS: ", repr(outstrings)

        idxs = '_'.join(outstrings)
        vw.makeName(addr, "case_%s_%x" % (idxs, addr))
        if vw.verbose:  print (addr, "case_%s_%x" % (idxs, addr))
   
    # link the dereferncing opcode to the base of deref points.
    if len(deref_ops):
        memop = deref_ops[-1]   # FIXME: Hack.  if we have two, one will get all xrefs
        for memref,tgt in memrefs:
            vw.addXref(memop.va, memref, vivisect.REF_DATA)
            vw.addXref(memref, tgt, vivisect.REF_PTR)
    
    # let's make switches easily findable.
    vw.makeName(va, "switch_%.8x" % va)
    vw.vprint("making switchname: switch_%.8x" % va)
    
    # store some metadata so we can know where to analyze later for naming
    if 'switch_cases' not in vw.getVaSetNames():
        vw.addVaSet('switch_cases', (('jmp_va', vivisect.VASET_ADDRESS),
                                     ('setup_va',vivisect.VASET_ADDRESS)) )
    vw.setVaSetRow('switch_cases', (va, oplist[0].va, len(cases)) )
    vagc.analyzeFunction(vw, funcva)

def determineCountOffset(vw, jmpva):
    '''
    Analyze instructions (symboliks) leading up to a "jmp reg" to determine which switch cases are 
    handled here.

    we start out with 
    '''
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

    # hack... give the jmp reg someplace to go so symboliks can help us
    choppt = len(vw._event_list)
    vw.addXref(jmpva, jmpcb[0], REF_CODE, rflags=op.iflags)

    if vw.verbose > 1: print op

    seffs = xlate.translateOpcode(op)
    if vw.verbose > 1: print seffs

    cons = xlate.getConstraints()
    if vw.verbose > 1: print "cons: ", repr(cons)

    ajmp = semu.applyEffects([cons[0]])
    if vw.verbose > 1: print ajmp

    vw.delXref((jmpva, jmpcb[0], REF_CODE, op.iflags))
    vw._event_list = vw._event_list[:choppt]                # FIXME: THIS IS JUST WRONG.  some better way?
                                                            # should we just hack this xref directly into the vw.xrefs_by_from?
                                                            # it's required to use symboliks on the final jmp reg

    acon = ajmp[0].cons._v1
    fullcons = [eff for eff in aeffs if eff.efftype==EFFTYPE_CONSTRAIN]
    if vw.verbose > 1: print '\nFULLCONS: \n','\n\t'.join([repr(con) for con in fullcons])

    muls = []
    acon.walkTree(_cb_grab_muls, muls)
    if vw.verbose > 1: print '\nMULS: \n',repr(muls)

    # this algorithm depends on the index variable being in the last Const comparison.  
    # these options may be best used with a heuristic (if one doesn't make us happy, 
    # fall through to a different one).

    # loop through fullcons looking for comparisons of symidx against Consts.  last one should be our index?!?
    idx = None
    upper = None
    lower = 0
    delta = None
    
    for cons in fullcons[::-1]:
        if not hasattr(cons.cons, 'operstr'): continue
        if vw.verbose > 2: print repr(cons)
        comparator = cons.cons.operstr
        symvar = cons.cons._v1
        symcmp = cons.cons._v2
        if symcmp.symtype != SYMT_CONST:
            continue

        if idx == None:
            idx = symvar
            baseoff = peel(idx)

        # once we identify idx, stick with it.  we only care about that.
        #### FIXME: how do we get the base...  probably need to peel back just the sub's, ignoring ands.
        d = 0
        if idx != symvar:
            d = idx.solve() - symvar.solve()
            if abs(d) > 1000:
                continue
        

        delta = baseoff + d
        if vw.verbose: print "* ", repr(cons.cons._v2), "\t",repr(cons.cons._v1),"\t", repr(cons), "\tdelta: ",delta


        # FIXME: probably don't want to reset things once they're set.  this could be some other indicator for a nested switchcase...  need to get one of those for testing.
        if comparator == ">":
            # this is setting the lower bound
            if lower != 0:
                if vw.verbose: print "==we're resetting a lower bound:  %s -> %s" % (lower, symcmp)
            lower = symcmp.solve() + 1# + delta
            
        elif comparator == ">=":
            # this is setting the lower bound
            if lower != 0:
                if vw.verbose: print "==we're resetting a lower bound:  %s -> %s" % (lower, symcmp)
            lower = symcmp.solve()# + delta
            
        elif comparator == "<":
            # this is setting the upper bound
            if upper != None:
                if vw.verbose: print "==we're resetting a upper bound:  %s -> %s" % (upper, symcmp)
            upper = symcmp.solve() - 1# + delta
            
        elif comparator == "<=":
            # this is setting the upper bound
            if upper != None:
                if vw.verbose: print "==we're resetting a upper bound:  %s -> %s" % (upper, symcmp)
            upper = symcmp.solve()# + delta

        else:
            if vw.verbose: print "Unhandled comparator:  %s\n" % repr(comparator)

    if None in (idx, upper, delta):
        if vw.verbose: print "NON-SWITCH analysis terminated: 0x%x" % jmpva
        return (None, None, None)

    if vw.verbose: print "Lower: %d\tUpper: %d\tOffset: %d\tIndex: %s" % (lower, upper, baseoff, idx)

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
    jmp_indir = vw.getMeta('jmp_indir')
    if not jmp_indir:
        return

    for jmpva in jmp_indir:
        funcva = vw.getFunction(jmpva)
        if funcva != fva:
            # jmp_indir is for the entire VivWorkspace.  
            # we're just filtering to this function here.
            continue

        lower, upper, baseoff = determineCountOffset(vw, jmpva)
        if None in (lower, upper): 
            if vw.verbose: print "something odd in count/offset calculation... skipping 0x%x..." % jmpva
            continue

        count = (upper - lower) + 1
        makeSwitch(vw, jmpva, count, baseoff, funcva=fva)    


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
