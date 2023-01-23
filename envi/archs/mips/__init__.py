"""
MIPS module
"""

############
# Author: Jaime Lightfoot
# Started: 11/24/2021
# mee-meee-meEEeep

# TODO
# - Figure out privileged modes MIPS32/64 primarily differs from MIPS I–V by defining the privileged kernel mode System Control Coprocessor in addition to the user mode architecture.
# - I am currently doing nothing with flags
# - I have not implemented branching
# - Need to set endianness in __init__?
# - Only doing 32-bits now, how to extend to 64?
# - Need to figure out how to handle HI,LO for mult instructions
# - pseudo-instructions like "move"?
# - read symbol table out?

import envi

from envi.archs.mips.disasm import *

class MipsModule(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "mips")
        self._arch_dis = MipsDisasm()

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def archGetBreakInstr(self):
        return b'\x00\x00\x00\x0D'

    def archGetNopInstr(self):
        return b'\x00\x00\x00\x00'

    def archGetRegCtx(self):
        return MipsRegisterContext()

    def getEndian(self):
        # JL MIPS can be either le or be
        return self.endian

    def setEndian(self, endian):
        '''
        set endianness for the architecture.
        ENDIAN_LSB and ENDIAN_MSB are appropriate arguments
        '''
        self.endian = endian
        self.fmt = ("<I", ">I")[endian]

    def getPointerSize(self):
        """
        Get the size of a pointer in memory on this architecture.
        """
        return 4 # unit is bytes, presumably?

    def pointerString(self, va):
        """
        Return a string representation for a pointer on this arch
        """
        raise ArchNotImplemented("pointerString")

    def getEmulator(self):
        return MipsEmulator()
