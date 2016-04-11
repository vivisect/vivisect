import vivisect
import vivisect.impemu.monitor as viv_monitor

def reprPointer(self, va):
    """
    Do your best to create a humon readable name for the
    value of this pointer.
    """
    if va == 0:
        return "NULL"

    loc = vw.getLocation(va)
    if loc != None:
        locva, locsz, lt, ltinfo = loc
        if lt in (LOC_STRING, LOC_UNICODE):
            return vw.reprVa(locva)

    mbase,msize,mperm,mfile = self.memobj.getMemoryMap(va)
    ret = mfile
    sym = self.getName(va, exact=False)
    if sym != None:
        ret = "%s + %d" % (repr(sym),va-long(sym))
    return ret

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.reg = vw.getMeta('PIE_reg')

    def prehook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

    def posthook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.posthook(self, emu, op, starteip)
        if len(op.opers) > 1:
            oper = op.opers[1]
            if hasattr(oper, 'reg') and oper.reg == self.reg:
                # THING!  what now?
                tgt = op.getOperValue(0)
                #vw.setComment(op.va, reprPointer(tgt))
                #vw.setComment(op.va, reprVa(tgt))
                vw.vprint("%x  %s" % (op.va, reprVa(tgt)))
                print("%x  %s" % (op.va, reprVa(tgt)))


def analyzeFunction(vw, fva):
    '''
    this analysis module will identify thunk_bx functions, which take the return value and place 
    it into EBX.  this is done for position-independent code in i386 elf binaries.  a call to this
    function will be followed by an immediate add to find the start of the module.  that value is
    then used with fixed offsets to access resources within the binary.  it's a bit like the old
    shellcode trick.

    store funcva in "thunk_bx" VaSet in case we identify multiples (not likely) or misidentify 
    something.

    then store the module base in metadata as "PIE_ebx", accessible by other analysis modules.
    '''
    got = None
    for segva, segsz, segnm, segimg in vw.getSegments():
        if segnm == '.got':
            got = segva
            break

    # if we don't have a segment named ".got" we fail.
    if got == None: 
        return

    # roll through the first few opcodes looking for one to load a register with .got's address
    success = 0
    tva = fva
    emu = vw.getEmulator()

    for x in range(10):
        op = vw.parseOpcode(tva)
        emu.executeOpcode(op)
        if not len(op.opers):
            continue

        operval = op.getOperValue(0, emu)
        #print hex (operval)
        if operval == got:
            success == True
            print "WIN!"

            reg = op.opers[0].reg
            vw.setVaSetRow('thunk_reg', (fva, reg))
            if vw.getMeta('PIE_reg') == None:
                vw.setMeta('PIE_reg', reg)
                vw.setMeta('PIE_GOT', got)
            break

        tva += len(op)

    if not success: 
        return

    # now check through all the functions and autocomment
    emumon = AnalysisMonitor(vw, fva)
    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)






    '''
    if vw.readMemory(fva, 4) == thunk_bx_sig:

        # have we already recorded this thunk_bx?
        if vw.getVaSetRow('thunk_bx', fva) != None:
            if vw.verbose: print("ditching thunk_bx: %s")
            return
        
        vw.setVaSetRow('thunk_bx', (fva,))


        # determine where ebx ends up pointing to
        # this requires checking the calling function's next instruction
        refs = vw.getXrefsTo(fva)
        if refs == None or not len(refs):
            return

        va = refs[0][0]
        op = vw.parseOpcode(va)
        op2 = vw.parseOpcode(va + len(op))
        if op2.mnem != "add":
            if vw.verbose: print("call to thunk_bx not followed by an add: %s" % op2)
            return
        
        addt = op2.opers[1].getOperValue(op2)
        ebx = op2.va + addt
        if vw.getMeta('PIE_ebx') != None:
            return

        if vw.verbose: print("__x86.get_pc_thunk.bx:  ", hex(ebx))
        curname = vw.getName(fva)
        if curname == None or curname == "sub_%.8x"%fva:
            vw.makeName(fva, "thunk_bx_%.8x"%fva)

        vw.setMeta('PIE_ebx', ebx)
        '''
