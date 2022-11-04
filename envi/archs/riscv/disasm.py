import sys
import struct
import traceback

import envi
import envi.bits as e_bits

from envi.archs.riscv.const import *
from envi.archs.riscv.regs import *
from envi.archs.riscv.instr_table import *
from envi.archs.riscv.operands import *
from envi.archs.riscv.info import *


OPCODE_SIZE = (2, 4)


def count_ones(value):
    try:
        # Only works in python 3.10+
        return value.bit_count()
    except AttributeError:
        return format(value, 'b').count('1')


class RiscVDisasm:
    def __init__(self, endian=envi.ENDIAN_LSB, description=None):
        if description is None:
            self.description = DEFAULT_RISCV_DESCR
        else:
            self.description = description

        self.setEndian(endian)
        self.xlen = getRiscVXLEN(self.description)
        self.psize = self.xlen // 8
        self.setCategories()

    def setCategories(self):
        self.categories = getRiscVCategories(self.description)

        # True = 32 bit
        # False = 16 bit
        instrs = {True: {}, False: {}}
        for entry in instructions:
            if any(c.xlen == self.xlen and c.cat & self.categories for c in entry.cat):
                encoding = entry.cat[0].cat != RISCV_CAT.C
                if entry.mask not in instrs[encoding]:
                    instrs[encoding][entry.mask] = {}
                if entry.value in instrs[encoding][entry.mask]:
                    raise Exception('ERROR: duplicate mask/value combination in RiscV instruction table %d/%x/%x: %s, %s' % \
                            (encoding, entry.mask, entry.value, instrs[encoding][entry.mask][entry.value].name, entry.name))
                instrs[encoding][entry.mask][entry.value] = entry

        # Reorganize the masks to have the entries with the most bits set first,
        # this will help any simplified mnemonics or specializations to be
        # decoded first, and the more generic instruction last.
        self.instrs = {}
        for encoding in instrs:
            self.instrs[encoding] = {}
            for mask in reversed(sorted(instrs[encoding], key=count_ones)):
                self.instrs[encoding][mask] = instrs[encoding][mask]

    def setEndian(self, endian):
        self.endian = endian
        self.fmt = {
            # True is 32 bit
            # False is 16 bit
            True: ('<I', '>I')[endian],
            False: ('<H', '>H')[endian]
        }

    def disasm(self, data, offset, va):
        # TODO: If RiscV ever supports Big Endian this may change
        opcode_encoding = data[offset] & 0x3 == 0x3
        opcode_size = OPCODE_SIZE[opcode_encoding]

        ival = struct.unpack_from(self.fmt[opcode_encoding], data, offset)[0]

        for mask in self.instrs[opcode_encoding]:
            masked_value = ival & mask
            found = self.instrs[opcode_encoding][mask].get(masked_value)
            if found is not None:
                try:
                    opers = tuple(OPERCLASSES[f.type](ival=ival, bits=f.bits, args=f.args, va=va, oflags=f.flags) for f in found.fields)
                    return RiscVOpcode(va, found.opcode, found.name, opcode_size, opers, found.flags)

                except envi.InvalidOperand:
                    # One of the operands has a restricted value so the
                    # instruction doesn't decode properly, try a different one
                    pass
        else:
            raise envi.InvalidInstruction(data[offset:offset+opcode_size], 'No Instruction Matched: %x' % ival, va)


OPERCLASSES = {
    RISCV_FIELD.REG: RiscVRegOper,
    RISCV_FIELD.F_REG: RiscVFRegOper,
    RISCV_FIELD.CSR_REG: RiscVCSRRegOper,
    RISCV_FIELD.MEM: RiscVMemOper,
    RISCV_FIELD.MEM_SP: RiscVMemSPOper,
    RISCV_FIELD.JMP: RiscVJmpOper,
    RISCV_FIELD.IMM: RiscVImmOper,
    RISCV_FIELD.REL_JMP: RiscVRelJmpOper,
    RISCV_FIELD.RM: RiscVRMOper,
    RISCV_FIELD.ORDER: RiscVOrderOper,
}
