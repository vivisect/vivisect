
"""
The initial arm module.
"""

import envi

from envi.archs.arm.regs import *
from envi.archs.arm.disasm import *

class ArmModule(envi.ArchitectureModule):

    def __init__(self, name='armv6'):
        import envi.archs.thumb16.disasm as eatd
        # these are required for setEndian() which is called from ArchitectureModule.__init__()
        self._arch_dis = ArmDisasm()
        self._arch_thumb_dis = eatd.Thumb2Disasm()

        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()

    def archGetRegCtx(self):
        return ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")
        return

    def archGetNopInstr(self):
        return '\x00'
 
    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        if va & 3:
            return self._arch_thumb_dis.disasm(bytes, offset, va)

        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return ArmEmulator()

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)
        self._arch_thumb_dis.setEndian(endian)



from envi.archs.arm.emu import *
