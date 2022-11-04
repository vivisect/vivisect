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
        self.instrs = {True: {}, False: {}}
        for entry in instructions:
            if any(c.xlen == self.xlen and c.cat & self.categories for c in entry.cat):
                instr_size = entry.cat[0].cat != RISCV_CAT.C
                if entry.mask not in self.instrs[instr_size]:
                    self.instrs[instr_size][entry.mask] = {}
                if entry.value in self.instrs[instr_size][entry.mask]:
                    raise Exception('ERROR: duplicate mask/value combination in RiscV instruction table %d/%x/%x: %s, %s' % (instr_size, entry.mask, entry.value, self.instrs[instr_size][entry.mask][entry.value].name, entry.name))
                self.instrs[instr_size][entry.mask][entry.value] = entry

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

                    flags = found.flags
                    # If any of the operands indicate this instruction is a hint
                    # set the flag now, this lets the instructions decode
                    # properly but helps prevent accidentally executing an
                    # invalid instruction
                    if any(o.hint for o in opers):
                        flags |= RISCV_IF.HINT

                    return RiscVOpcode(va, found.opcode, found.name, opcode_size, opers, flags)

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
