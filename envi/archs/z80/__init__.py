import envi
import envi.archs.z80.disasm as e_z_disasm

class Z80Module(envi.ArchitectureModule):
    def __init__(self):
        self._arch_dis = e_z_disasm.z80Disasm()

    def archGetNopInstr(self):
        return b'\x00'

    def archGetBreakInstr(self):
        pass

    def archParseOpcode(self, bytez, offset=0, va=0, extra=None):
        pass

    def archGetRegCtx(self):
        pass

    def getPointerSize(self):
        return 2

    def pointerString(self, va):
        pass

    def initRegGroups(self):
        pass

    def archGetPointerAlignment(self):
        pass

    def getEmulator(self):
        pass
