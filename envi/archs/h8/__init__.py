
"""
Renasas H8 module.
MSB
8-bit
16-bit fixed instruction size (except when EA field, then 32-bit)
"""

import envi

from envi.archs.h8.regs import *
from envi.archs.h8.disasm import *

class H8Module(envi.ArchitectureModule):

    def __init__(self, name='h8'):
        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()
        self._arch_dis = H8Disasm()

    def archGetRegCtx(self):
        return H8RegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  h8 has a complex breakpoint instruction")
        return

    def archGetNopInstr(self):
        return '\x00'

    def getPointerSize(self):
        return 2

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return H8Emulator()

from envi.archs.h8.emu import *
