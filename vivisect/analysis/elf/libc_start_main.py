import sys
import logging

import envi
import vivisect
import vivisect.impemu.monitor as viv_imp_monitor

logger = logging.getLogger(__name__)


def analyzeFunction(vw, funcva):
    '''
    search through all calls, looking for a call to an import named __libc_start_main
    then check for arg0
    '''
    try:
        emu = vw.getEmulator()
        emumon = AnalysisMonitor(vw, funcva)

        emu.setEmulationMonitor(emumon)
        emu.runFunction(funcva, maxhit=1)

        if not emumon.success:
            logger.info("  emumon failure: %r", vars(emumon))
            return
        try:
            api = vw.getFunctionApi(emumon.startmain)
            cconv = emu.getCallingConvention(api[vivisect.API_CCONV])
        except:
            ccname = vw.getMeta('DefaultCall')
            cconv = emu.getCallingConvention(ccname)

        args = cconv.getCallArgs(emu, 1)
        mainva = args[0]

        vw.addEntryPoint(mainva)
        vw.makeFunction(mainva)

        curname = vw.getName(mainva)
        if curname in (None, "sub_%.8x" % mainva):
            vw.makeName(mainva, 'main', True)

    except Exception as e:
        sys.excepthook(*sys.exc_info())


def analyze(vw):
    logger.info('analyze()')

    for va, name in vw.getNames():
        lcsm = '__libc_start_main_%.8x' % va
        if name in (lcsm, "*."+lcsm):
            for xfr, xto, xtype, xtinfo in vw.getXrefsTo(va):
                if xtype != vivisect.REF_CODE:
                    continue

                logger.info("0x%x -> 0x%x (%r)", xfr, xto, xtype)
                funcva = vw.getFunction(xfr)
                if funcva is None:
                    continue

                analyzeFunction(vw, funcva)


class AnalysisMonitor(viv_imp_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        self.success = False
        self.emu = None
        self.startmain = None
        viv_imp_monitor.AnalysisMonitor.__init__(self, vw, fva)

        for va, name in vw.getNames():
            lcsm = '__libc_start_main_%.8x' % va
            if name in (lcsm, '*.' + lcsm):
                self.startmain = va

    def prehook(self, emu, op, starteip):

        if op.iflags & envi.IF_CALL:
            # it's a call, get the target
            branches = [br for br in op.getBranches(emu) if not (br[1] & envi.BR_FALL)]
            logger.debug('libc_start_main: 0x%x\ttgts: %r', self.startmain, branches)

            # check if it matches what we believe to be __libc_start_main
            for branch in branches:
                tgt, flags = branch
                if tgt == self.startmain:
                    self.success = True
                    self.emu = emu
                    emu.stopEmu()
