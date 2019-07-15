import sys
import envi
import logging

import vivisect
import vivisect.impemu.monitor as viv_imp_monitor

logger = logging.getLogger(__name__)


def analyzeFunction(vw, funcva):
    '''
    search through all calls, looking for a call to an import named __libc_start_main
    then check for arg0
    '''
    global emu, emumon, cconv
    try:
        emu = vw.getEmulator()
        emumon = AnalysisMonitor(vw, funcva)

        emu.setEmulationMonitor(emumon)
        emu.runFunction(funcva, maxhit=1)

        if not emumon.success:
            return

        api = vw.getFunctionApi(emumon.startmain)
        cconv = emu.getCallingConvention(api[vivisect.API_CCONV])

        args = cconv.getCallArgs(emu, 6)
        vw.addEntryPoint(args[0])
        vw.makeFunction(args[0])

    except Exception as e:
        sys.excepthook(*sys.exc_info())



def analyze(vw):
    global emu, emumon
    cg = vw.getCallGraph()

    for va, name in vw.getNames():
        if name == '__libc_start_main_%.8x' % va:
            for xfr, xto, xtype, xtinfo in vw.getXrefsTo(va):
                logger.info("0x%x -> 0x%x", xfr, xto)
                arg0va = vw.getLocation(xfr-1)[0]
                op0 = vw.parseOpcode(arg0va)

                arg1va = vw.getLocation(arg0va-1)[0]
                op1 = vw.parseOpcode(arg1va)

                arg2va = vw.getLocation(arg1va-1)[0]
                op2 = vw.parseOpcode(arg2va)

                try:    # attempt to use emulation to setup call, requires accurate calling convention
                    emu = vw.getEmulator()
                    emu.setProgramCounter(arg2va)
                except Exception as e:
                    logger.warn(repr(e))

                main = op0.opers[-1].getOperValue(op0)
                logger.info("main = 0x%x", main)
                vw.addEntryPoint(main)
                vw.makeFunction(main)
                vw.makeName(main, 'main', True)



class AnalysisMonitor(viv_imp_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        self.success = False
        self.emu = None
        self.startmain = None
        viv_imp_monitor.AnalysisMonitor.__init__(self, vw, fva)
        for va, name in vw.getNames():
            if name == '__libc_start_main_%.8x' % va:
                self.startmain = va

    def prehook(self, emu, op, starteip):
        viv_imp_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        if op.iflags & envi.IF_CALL:
            # it's a call, get the target
            tgt = [br for br in op.getBranches(emu) if br[0] != op.va + len(op)]

            # check if it matches what we believe to be __libc_start_main
            if tgt[0][0] == self.startmain:
                self.success = True
                self.emu = emu
                self.stop()




