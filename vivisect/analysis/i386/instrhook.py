"""
Finds functions containing specific instructions to determine if
their operands should be a  pointer locations.
This module works should be run after codeblocks analyis pass.
"""

import envi
import vivisect.impemu.monitor as viv_imp_monitor

verbose = False


class instrhook_watcher (viv_imp_monitor.EmulationMonitor):

    def __init__(self, vw, tryva):
        viv_imp_monitor.EmulationMonitor.__init__(self)
        self.vw = vw
        self.tryva = tryva
        self.hasret = False
        self.mndist = {}
        self.insn_count = 0
        self.lastop = None
        self.badcode = False
        self.badops = vw.arch.archGetBadOps()

    def prehook(self, emu, op, eip):
        # Not sure if we need to stop emulation altogether, since we're only looking for specific instructions anyway?
        if op in self.badops:
            emu.stopEmu()
            raise Exception("Hit known BADOP at 0x%.8x %s" % (eip, repr(op)))

        if op.mnem == 'stosb' or op.mnem == 'stosd':
            edi = emu.getRegister(envi.archs.i386.REG_EDI)
            if self.vw.isValidPointer(edi):
                self.vw.makePointer(edi, follow=True)


def analyzeFunction(vw, fva):

    dist = vw.getFunctionMeta(fva, 'MnemDist')

    if 'stosb' in dist or 'stosd' in dist:
        emu = vw.getEmulator()
        instrwat = instrhook_watcher(vw, fva)
        emu.setEmulationMonitor(instrwat)
        try:
            emu.runFunction(fva, maxhit=1)
        except Exception:
            pass
