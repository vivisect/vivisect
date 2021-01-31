"""
rxv2 module
"""
import envi

from . import regs
from . import const
from . import disasm

class RXv2Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "rxv2", maxinst=4)
        self._arch_dis = disasm.RxDisasm()

    def archGetRegCtx(self):
        return regs.RXv2RegisterContext()

    def archGetNopInstr(self):
        return '\x03'

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        general= ('general', registers, )
        groups.append(general)

        return groups

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return '0x{:04x}'.format(va)

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return emu.RXv2Emulator()

    def getArchDefaultCall(self):
        return 'rxv2call'

# NOTE: This one must be after the definition of RXv2Module
from . import emu
