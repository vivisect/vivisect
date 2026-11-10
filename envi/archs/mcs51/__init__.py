"""
i8051 Architecture:

Big-Endian
8-bit
Harvard Architecture
5 memory spaces: FLASH, IRAM, XRAM, SFR, Config
"""

import copy
import struct

import envi
import envi.bits as e_bits
from . import  opcode8051 as optable
from envi.archs.mcs51.disasm import *
from envi.archs.mcs51.regs import *


general = ['r%d' % x for x in range(32)]
general.append('eip')

class Mcs51Module(envi.ArchitectureModule):
    def __init__(self):
        envi.ArchitectureModule.__init__(self, "mcs51")
        self._arch_reg = self.archGetRegCtx()
        self._arch_dis = Mcs51Disasm()

    def archGetRegCtx(self):
        return Mcs51RegisterContext()

    def archGetBreakInstr(self):
        return None

    def archGetNopInstr(self):
        return '\x00'

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)
        groups.append(('general', general))
        return groups

    def getPointerSize(self):
        return 1

    def pointerString(self, va):
        return "%xh" % va

    def prdisp(self, o):
        # Just a displacement print helper
        dabs = abs(o.disp)
        if dabs > 4096:
            if o.disp < 0:
                return "- 0x%.8x" % dabs
            else:
                return "+ 0x%.8x" % dabs
        else:
            if o.disp < 0:
                return "- %d" % dabs
            else:
                return "+ %d" % dabs

    def archParseOpcode(self, bytes, offset=0, va=0, extra=None):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return Mcs51Emulator()


#must stay after Mcs51Module
from envi.archs.mcs51.emu import *
