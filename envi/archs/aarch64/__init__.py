
"""
The initial aarch64 module.
"""

import envi

from envi.archs.aarch64.regs import *
from envi.archs.aarch64.disasm import *

class A64Module(envi.ArchitectureModule):

    def __init__(self, name='a64'):
        # these are required for setEndian() which is called from ArchitectureModule.__init__()
        self._arch_dis = A64Disasm()

        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()

    def archGetRegCtx(self):
        return A64RegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")
        return

    def archGetNopInstr(self):
        return '\x00'
 
    def getPointerSize(self):
        return 8

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0, extra=None):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return A64Emulator()

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)

    def archModifyFuncAddr(self, va, info):
        return va, {}

    def archModifyXrefAddr(self, tova, reftype, rflags):
        return tova, reftype, rflags

    def initRegGroups(self):
        envi.ArchitectureModule.initRegGroups(self)
        self._regGrps.update({'general': aarch64_regs})




#from envi.archs.aarch64.emu import *
