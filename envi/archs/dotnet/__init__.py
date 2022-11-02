import envi.archs.dotnet.emu as e_emu
import envi.archs.dotnet.disasm as e_dotnet

from envi.archs.dotnet.disasm import *


class DotNetModule(envi.ArchitectureModule):
    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'dotnet')

        self._arch_dis = e_dotnet.DotNetDisasm(metadata=self.extrainfo.get('metadata'))

    def archGetRegCtx(self):
        return None

    def archGetBreakInstr(self):
        return b'\x01'

    def archGetNopInstr(self):
        return b'\x00'

    def archGetRegisterGroups(self):
        pass

    def getPointerSize(self):
        pass

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytez, offset=0, va=0):
        return self._arch_dis.disasm(bytez, offset, va)

    def getEmulator(self):
        return e_emu.DotNetEmulator()