"""
msp430 module
"""

############
# Author: Don C. Weber
# Started: 05/23/2009

import envi

from envi.archs.msp430.regs import *
from envi.archs.msp430.disasm import *
from envi.archs.msp430.const import *

class Msp430Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "msp430", maxinst=4)
        self._arch_dis = Msp430Disasm()

    def archGetRegCtx(self):
        return Msp430RegisterContext()

    def archGetNopInstr(self):
        return b'\x03\x43' # NOP is emulated with: MOV #0, R3

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
        return Msp430Emulator()

    def getArchDefaultCall(self):
        return 'msp430call'

# NOTE: This one must be after the definition of Msp430Module
from envi.archs.msp430.emu import *
