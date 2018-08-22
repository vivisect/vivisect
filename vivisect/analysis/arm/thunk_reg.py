import sys
import envi
import vivisect
import vivisect.impemu.monitor as viv_monitor

from vivisect import LOC_STRING, LOC_UNI, REF_DATA

MAX_INIT_OPCODES = 30

def reprPointer(vw, va):
    """
    Do your best to create a humon readable name for the
    value of this pointer.
    """
    if va == 0:
        return "NULL"

    loc = vw.getLocation(va)
    if loc != None:
        locva, locsz, lt, ltinfo = loc
        if lt in (LOC_STRING, LOC_UNI):
            return vw.reprVa(locva)

    mbase,msize,mperm,mfile = vw.memobj.getMemoryMap(va)
    ret = mfile
    sym = vw.getName(va)
    if sym != None:
        ret = sym
    return ret

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.reg = vw.getFunctionMeta(fva, 'PIE_reg')
        self.tracker = {}

    def prehook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

    def posthook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.posthook(self, emu, op, starteip)
        if len(op.opers) > 1:
            # TODO: future: make this getRegister() for the registers... look for .GOT
            oper = op.opers[1]
            if (hasattr(oper, 'reg') and oper.reg == self.reg) \
                    or (hasattr(oper, 'base_reg') and oper.base_reg == self.reg):
                # second operand has the register we're interested in for this function
                tgt = op.getOperValue(0, emu)
                if tgt == None:
                    print "0x%x: %s   tgt == None!" % (op.va, op)
                    return

                self.tracker[op.va] = tgt
                #print("%x  %s" % (op.va, self.vw.reprVa(tgt)))


def analyzeFunction(vw, fva, prepend=False):
    '''
    this analysis module will identify thunk_reg functions, which place the .GOT pointer
    into some register which is then accessed later.  
    doing so allows for position-independent code.

    store funcva in "thunk_reg" VaSet in case we identify multiples (not likely) or misidentify 
    something.

    then store the module base in metadata as "PIE_GOT", accessible by other analysis modules.
    then store the register used in this function in function metadata as "PIE_reg"
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

    for x in range(MAX_INIT_OPCODES):
        op = vw.parseOpcode(tva)
        emu.executeOpcode(op)

        if op.iflags & (envi.IF_BRANCH | envi.IF_COND) == (envi.IF_BRANCH | envi.IF_COND):
            break

        if not len(op.opers):
            continue

        operval = op.getOperValue(0, emu)
        if operval == got:
            success = True

            reg = op.opers[0].reg
            vw.setVaSetRow('thunk_reg', (fva, reg))

            if vw.getFunctionMeta(fva, 'PIE_reg') == None:
                vw.setFunctionMeta(fva, 'PIE_reg', reg)
                vw.setComment(op.va, 'Position Indendent Code Register Set: %s' % \
                        vw.arch._arch_reg.getRegisterName(reg))

            if vw.getMeta('PIE_GOT') == None:
                vw.setMeta('PIE_GOT', got)
            break

        tva += len(op)

    if not success: 
        return

    if vw.verbose: vw.vprint('funcva 0x%x using thunk_reg for PIE' % fva)

    # now check through all the functions and track references
    emumon = AnalysisMonitor(vw, fva)
    emu.setEmulationMonitor(emumon)
    try:
        emu.runFunction(fva, maxhit=1)
    except:
        vw.vprint("Error emulating function 0x%x\n\t%s" % (fva, repr(emumon.emuanom)))

    if vw.verbose: sys.stderr.write('=')

    # now roll through tracked references and make xrefs/comments
    items = emumon.tracker.items()
    items.sort()
    for va, tgt in items:
        # if we already have xrefs, don't make more...
        if vw.getLocation(tgt) == None:
            try:
                vw.followPointer(tgt)
            except envi.SegmentationViolation:
                if vw.verbose: vw.vprint("SegV: %x (va:0x%x)" % (tgt,va))
                emumon.emuanom.append("SegV: %x (va:0x%x)" % (tgt,va))
                continue

        nogo = False
        for xfr,xto,xtype,xflag in vw.getXrefsFrom(va):
            if xto == tgt:
                nogo = True
        if not nogo:
            #vw.vprint("PIE XREF: 0x%x -> 0x%x" % (va, tgt))
            try:
                vw.addXref(va, tgt, REF_DATA, 0)
            except:
                sys.excepthook(*sys.exc_info())
            ## FIXME: force analysis of the xref.  very likely string for current example code.

        # set comment.  if existing comment, by default, don't... otherwise prepend the info before the existing comment
        curcmt = vw.getComment(va)
        cmt = "0x%x: %s" % (tgt, reprPointer(vw, tgt))
        if curcmt == None or not len(curcmt):
            vw.setComment(va, cmt)
        elif not cmt in curcmt:
            cmt = "0x%x: %s ;\n %s" % (tgt, reprPointer(vw, tgt), curcmt)
            vw.setComment(va, cmt)

        if vw.verbose: vw.vprint("PIE XREF: %x  %s" % (va, cmt))

    if vw.verbose: vw.vprint("ANOMS: \n", repr(emumon.emuanom))

def analyze(vw):
    # don't want to run this multiple times on the same function... comments get outa hand.
    for fva in vw.getFunctions():
        #if vw.getFunctionMeta(fva, 'PIE_reg'):
        #    continue

        try:
            analyzeFunction(vw, fva)
        except:
            pass

if globals().get('vw') != None:
    if len(argv) > 1:
        va = vw.parseExpression(argv[1])
        vw.vprint("analyzing workspace function %x for thunk_reg", va)
        analyzeFunction(vw, va)
    else:
        vw.vprint("analyzing workspace for thunk_reg")
        analyze(vw)
    vw.vprint("done")
