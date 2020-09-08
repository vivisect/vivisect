"""
Finds functions containing specific instructions to determine if
their operands should be a  pointer locations.
This module should be run after codeblocks analyis pass.
"""

import envi
import vivisect.exc as v_exc
import vivisect.impemu.monitor as viv_imp_monitor

STOS = ('stosb', 'stosw', 'stosd', 'stosq')


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
        self.arch = vw.getMeta('Architecture')

    def prehook(self, emu, op, eip):
        if op in self.badops:
            emu.stopEmu()
            raise v_exc.BadOpBytes(op.va)

        if op.mnem in STOS:
            if self.arch == 'i386':
                reg = emu.getRegister(envi.archs.i386.REG_EDI)
            elif self.arch == 'amd64':
                reg = emu.getRegister(envi.archs.amd64.REG_RDI)
            if self.vw.isValidPointer(reg) and self.vw.getLocation(reg) is None:
                self.vw.makePointer(reg, follow=True)


def analyzeFunction(vw, fva):

    emulate = False
    dist = vw.getFunctionMeta(fva, 'MnemDist', default=[])

    for s in STOS:
        if s in dist:
            emulate = True
            break

    if emulate:
        emu = vw.getEmulator()
        instrwat = instrhook_watcher(vw, fva)
        emu.setEmulationMonitor(instrwat)
        try:
            emu.runFunction(fva, maxhit=1)
        except Exception:
            pass
