import struct

import envi
import envi.bits as e_bits
import envi.encoding as e_enc

from envi.archs.mips import MipsModule
from envi.archs.mips.regs import *
from envi.archs.mips.const import *

class MipsCall(envi.CallingConvention):
    # TODO look at MIPS calling convention
    arg_def = [(CC_REG, REG_A0), (CC_REG, REG_A1), (CC_REG, REG_A2), (CC_REG, REG_A3), (CC_STACK_INF, 4)]
    retaddr_def = (CC_REG, REG_RA)
    retval_def = (CC_REG, REG_V0)    # technically can also go into v1 in some cases
    flags = CC_CALLEE_CLEANUP # more complicated than this (callee restores the saved $s* registers, caller restores the $t* registers)
    align = 2  # always needs to be 8-bit aligned
    pad = 0

mipscall = MipsCall()

class MipsEmulator(MipsRegisterContext, envi.Emulator):

    def __init__(self, regarray=None):
        self.archmod = MipsModule()

        envi.Emulator.__init__(self, self.archmod)
        MipsRegisterContext.__init__(self)

        self._emu_segments = [(0, 0xffff)]
        self.addCallingConvention('mipscall', mipscall)

    def getArchModule(self):
        return self.archmod
