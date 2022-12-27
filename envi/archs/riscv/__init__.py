"""
riscv module
"""

import envi

from envi.archs.riscv.regs import *
from envi.archs.riscv.disasm import *
from envi.archs.riscv.const import *
from envi.archs.riscv.info import *

__all__ = [
    'RiscVModule',
    'RiscV32Module',
    'RiscV64Module',

    # Also export the objects exported from envi.archs.riscv.emu
    'RiscVCall',
    'RiscVEmulator',
    'RiscV32Emulator',
    'RiscV64Emulator',
]


class RiscVModule(envi.ArchitectureModule):
    def __init__(self, archname, description, endian=envi.ENDIAN_LSB):
        envi.ArchitectureModule.__init__(self, archname, endian=endian)

        self.description = description
        self.xlen = getRiscVXLEN(self.description)
        self.psize = self.xlen // 8

        self._arch_dis = RiscVDisasm(endian, description)

    def archGetRegCtx(self, description=None):
        if description is None:
            description = self.description
        return RiscVRegisterContext(description)

    def archGetNopInstr(self):
        return b'\x00\x00\x00\x13' # NOP is emulated with addi x0, x0, 0

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        # Add in the different register groups from regs.py
        groups['general'] = earr.general_registers
        groups['float'] = earr.float_registers

        return groups

    def getPointerSize(self):
        return self.psize

    def pointerString(self, va):
        if self.psize == 8:
            return '0x%.16x' % va
        elif self.psize == 4:
            return '0x%.8x' % va
        else:
            return None

    def archParseOpcode(self, data, offset=0, va=0):
        return self._arch_dis.disasm(data, offset, va)

    def getEmulator(self, endian=None, description=None):
        if endian is None:
            endian = self.endian
        if description is None:
            description = self.description
        return RiscVEmulator(self, archname=self.getArchName(), description=description, endian=endian)


class RiscV32Module(RiscVModule):
    def __init__(self, endian=envi.ENDIAN_LSB):
        RiscVModule.__init__(self, archname='rv32', description='RV32GC', endian=endian)


class RiscV64Module(RiscVModule):
    def __init__(self, endian=envi.ENDIAN_LSB):
        RiscVModule.__init__(self, archname='rv64', description='RV64GC', endian=endian)


# NOTE: This one must be after the definition of RiscvModule
from envi.archs.riscv.emu import *
