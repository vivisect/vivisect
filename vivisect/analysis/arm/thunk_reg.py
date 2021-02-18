import envi
import vivisect.impemu.monitor as viv_monitor

import logging

from vivisect.const import REF_DATA
from envi.archs.arm.regs import PSR_T_bit

logger = logging.getLogger(__name__)
MAX_INIT_OPCODES = 30


class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.reg = vw.getFunctionMeta(fva, 'PIE_reg')
        self.tracker = {}

    def posthook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.posthook(self, emu, op, starteip)
        if len(op.opers) > 1:
            oper = op.opers[1]
            if (hasattr(oper, 'reg') and oper.reg == self.reg) \
                    or (hasattr(oper, 'base_reg') and oper.base_reg == self.reg):
                # first (dest) operand has the register we're interested in for this function
                tgt = op.getOperValue(0, emu)
                if tgt is None:
                    logger.warning("0x%x: %s   tgt is None!", op.va, op)
                    return

                self.tracker[op.va] = tgt


def analyzeFunction(vw, fva):
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
    if got is None:
        return

    # roll through the first few opcodes looking for one to load a register with .got's address
    success = 0
    tva = fva
    emu = vw.getEmulator()
    emu._prep(tva)

    for x in range(MAX_INIT_OPCODES):
        op = emu.parseOpcode(tva)

        tmode = emu.getFlag(PSR_T_bit)

        emu.executeOpcode(op)

        newtmode = emu.getFlag(PSR_T_bit)
        if newtmode != tmode:
            emu.setFlag(PSR_T_bit, tmode)

        if op.iflags & (envi.IF_BRANCH_COND) == (envi.IF_BRANCH_COND):
            break

        if not len(op.opers):
            continue

        operval = op.getOperValue(0, emu)
        if operval == got:
            success = True

            reg = op.opers[0].reg
            vw.setVaSetRow('thunk_reg', (fva, reg))

            if vw.getFunctionMeta(fva, 'PIE_reg') is None:
                vw.setFunctionMeta(fva, 'PIE_reg', reg)
                vw.setComment(op.va, 'Position Indendent Code Register Set: %s' % vw.arch._arch_reg.getRegisterName(reg))

            if vw.getMeta('PIE_GOT') is None:
                vw.setMeta('PIE_GOT', got)
            break

        tva += len(op)
        if op.isReturn():
            logger.debug("thunk_reg: returning before finding PIE data")
            break

    if not success:
        return

    logger.debug('funcva 0x%x using thunk_reg for PIE', fva)

    # now check through all the functions and track references
    emumon = AnalysisMonitor(vw, fva)
    emu.setEmulationMonitor(emumon)
    try:
        emu.runFunction(fva, maxhit=1)
    except Exception:
        logger.exception("Error emulating function 0x%x\n\t%r", fva, emumon.emuanom)

    # now roll through tracked references and make xrefs/comments
    items = list(emumon.tracker.items())
    items.sort()
    for va, tgt in items:
        # if we already have xrefs, don't make more...
        if vw.getLocation(tgt) is None:
            try:
                vw.followPointer(tgt)
            except envi.SegmentationViolation:
                logger.debug("SegV: %x (va:0x%x)", tgt, va)
                emumon.emuanom.append("SegV: %x (va:0x%x)" % (tgt, va))
                continue

        nogo = False
        for xfr, xto, xtype, xflag in vw.getXrefsFrom(va):
            if xto == tgt:
                nogo = True
        if not nogo:
            logger.debug("PIE XREF: 0x%x -> 0x%x", va, tgt)
            try:
                vw.addXref(va, tgt, REF_DATA, 0)
            except Exception as e:
                logger.exception('error adding XREF: %s', e)
            ## FIXME: force analysis of the xref.  very likely string for current example code.

        # set comment.  if existing comment, by default, don't... otherwise prepend the info before the existing comment
        curcmt = vw.getComment(va)
        cmt = "0x%x: %s" % (tgt, vw.reprPointer(tgt))
        if curcmt is None or not len(curcmt):
            vw.setComment(va, cmt)
        elif cmt not in curcmt:
            cmt = "0x%x: %s ;\n %s" % (tgt, vw.reprPointer(tgt), curcmt)
            vw.setComment(va, cmt)

        logger.debug("PIE XREF: %x  %s", va, cmt)

    logger.debug("ANOMS: \n%r", emumon.emuanom)


def analyze(vw):
    '''
    run analysis on each function
    '''
    for fva in vw.getFunctions():
        try:
            analyzeFunction(vw, fva)
        except:
            logger.exception('thunk_reg analysis error:')


if globals().get('vw') is not None:
    if len(argv) > 1:
        va = vw.parseExpression(argv[1])
        logger.warning("analyzing workspace function %x for thunk_reg", va)
        analyzeFunction(vw, va)
    else:
        logger.warning("analyzing workspace for thunk_reg")
        analyze(vw)
    logger.warning("done")
