"""
rxv2 module
"""
import envi

from envi.archs.rxv2.regs import *
from envi.archs.rxv2.disasm import *
from envi.archs.rxv2.const import *

class RXv2Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "rxv2", maxinst=4)
        self._arch_dis = RXv2Disasm()

    def archGetRegCtx(self):
        return RXv2RegisterContext()

    def archGetNopInstr(self):
        return '\x03\x43' # NOP is emulated with: MOV #0, R3

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)
        general= ('general', registers, )
        groups.append(general)
        return groups

    def getPointerSize(self):
        return 2

    def pointerString(self, va):
        return '0x{:04x}'.format(va)

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return RXv2Emulator()

    def getArchDefaultCall(self):
        return 'rxv2call'

# NOTE: This one must be after the definition of RXv2Module
from envi.archs.rxv2.emu import *
