import envi

from envi.archs.dotnet.disasm import *


class dotnetModule(envi.ArchitectureModule):
    def __init__(self):
        envi.ArchitectureModule(self, 'dotnet')
        self._arch_dis = DotnetDisasm()

    def archGetRegCtx(self):
        return dotnetRegisterContext()

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

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return DotNetEmulator()
