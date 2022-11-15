#!/usr/bin/env python
'''
Decoding updated based on vle_mnems.py and a newer approach.

Original tuples and logic adapted from:
    https://github.com/wargio/libvle
    https://github.com/ehntoo/libvle

special thanks to wargio and ehntoo for their hard work

adapted by atlas <atlas@r4780y.com>, bugfixes and unit tests by @sprout42.
'''

from typing import Dict, Tuple, Callable, Optional, List
from .vle_ops import *
from .regs import *
import envi
import struct
from .disasm_classes import *
from .disasm import Ppc32EmbeddedDisasm

import envi.bits as e_bits


operands = (
    None,
    PpcERegOper,
    PpcERegOper,
    PpcImmOper,
    PpcSImm16Oper,
    PpcSImm20Oper,
    PpcSImm32Oper,
    PpcMemOper,
    PpcSEMemOper,
    PpcJmpRelOper,
    PpcCRegOper,
    PpcCBRegOper,
)

def case_E_X(types, data, va):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11
    op2 = operands[types[2]]
    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_XL(types, data, va):
    #print(types, hex(data))
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11
    op2 = operands[types[2]]

    #print("E_XL", op0, val0, op1, val1, op2, val2)
    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_D(types, data, va, tsize):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]
    val2 = data & 0xFFFF
    if (val2 & 0x8000) :
        val2 = 0xFFFF0000 | val2

    # holy crap, this table is a mess.  too C-ish, not Pythonic.
    if types[1] == TYPE_MEM:
        if types[2] == TYPE_REG and val1 == 0:
            opers = ( op0(val0, va), PpcImmOper(val2, va) )
        else:
            opers = ( op0(val0, va), op1(val1, val2, va, tsize=tsize) )
    else:
        op2 = operands[types[2]]
        opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )

    return opers

def case_E_D8(types, data, va, tsize):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]

    val2 = data & 0xFF
    if (val2 & 0x80):
        val2 = 0xFFFFFF00 | val2

    opers = ( op0(val0, va), op1(val1, val2, va, tsize=tsize) )
    return opers

# Handles the new multiple load/store VLE instructions
def case_E_D8VLS(types, data, va, tsize):
    val0 = (data & 0x1F0000) >> 16
    op0 = operands[types[1]]

    val1 = data & 0xFF
    if (val1 & 0x80):
        val1 = 0xFFFFFF00 | val1

    opers = ( op0(val0, val1, va, tsize=tsize), )
    return opers

def case_E_I16A(types, data, va):
    val0 = (data & 0x1F0000) >> 16
    op0 = operands[types[1]]
    val1 = ((data & 0x3E00000) >> 10) | (data & 0x7FF)
    op1 = operands[types[0]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers


SCI_mask = (0xffffff00, 0xffff00ff, 0xff00ffff, 0x00ffffff)
def case_E_SCI8(types, data, va):
    opers = []
    if (types[0] != TYPE_NONE):
        val0 = (data & 0x3E00000) >> 21
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if (types[1] != TYPE_NONE):
        val1 = (data & 0x1F0000) >> 16
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

    if (types[2] != TYPE_NONE):
        ui8 = data & 0xFF
        scl = (data & 0x300) >> 8
        f = bool(data & 0x400)

        val2 = (ui8 << (8*scl)) | (f * SCI_mask[scl])
        '''
        if scl == 0:
            val2 = ui8 | (f ? 0xffffff00 : 0);
        elif scl == 1:
            val2 = (ui8 << 8) | (f ? 0xffff00ff : 0);
        elif scl == 2:
            val2 = (ui8 << 16) | (f ? 0xff00ffff : 0);
        else:
            val2 = (ui8 << 24) | (f ? 0x00ffffff : 0);
        '''

        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    return opers

# Handles SCI8 form instructions with rA and rS inverted
def case_E_SCI8I(types, data, va):
    val1 = (data & 0x3E00000) >> 21
    op1 = operands[types[0]]
    val0 = (data & 0x1F0000) >> 16
    op0 = operands[types[1]]
    ui8 = data & 0xFF
    scl = (data & 0x300) >> 8
    f = bool(data & 0x400)

    val2 = (ui8 << (8*scl)) | (f * SCI_mask[scl])
    '''
    if scl == 0:
        val2 = ui8 | (f ? 0xffffff00 : 0);
    elif scl == 1:
        val2 = (ui8 << 8) | (f ? 0xffff00ff : 0);
    elif scl == 2:
        val2 = (ui8 << 16) | (f ? 0xff00ffff : 0);
    else:
        val2 = (ui8 << 24) | (f ? 0x00ffffff : 0);
    '''

    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

# Handles SCI8 form compare instructions with a smaller register field
def case_E_SCI8CR(types, data, va):
    val0 = (data & 0x0600000) >> 21
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]
    ui8 = data & 0xFF
    scl = (data & 0x300) >> 8
    f = bool(data & 0x400)

    val2 = (ui8 << (8*scl)) | (f * SCI_mask[scl])
    '''
    if scl == 0:
        val2 = ui8 | (f ? 0xffffff00 : 0);
    elif scl == 1:
        val2 = (ui8 << 8) | (f ? 0xffff00ff : 0);
    elif scl == 2:
        val2 = (ui8 << 16) | (f ? 0xff00ffff : 0);
    else:
        val2 = (ui8 << 24) | (f ? 0x00ffffff : 0);
    '''

    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_I16L(types, data, va):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 5
    val1 |= (data & 0x7FF)
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_I16LS(types, data, va):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 5
    val1 |= (data & 0x7FF)
    # this is technically incorrect, but makes disassembly prettier to look at.
    val1 <<= 16

    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_BD24(types, data, va):
    val0 = data & 0x01FFFFFE
    offset = e_bits.bsigned(val0, 25)

    op0 = operands[types[0]]

    opers = ( op0(offset, va), )
    return opers

def case_E_BD15(types, data, va):
    val1 = data & 0xFFFE
    offset = e_bits.bsigned(val1, 16)

    op1 = operands[types[1]]

    if (data & 0x00200000) == 0x00200000:
        # If this is a CTR related branch conditional, the register to check
        # the value for is always the CTR SPR (SPR 9).
        #val0 = 9 + REG_OFFSET_SPR
        #op0 = operands[types[0]]

        #opers = ( op0(val0, va), op1(offset, va) )
        opers = ( op1(offset, va), )
    else:
        val0 = (data & 0xC0000) >> 18
        op0 = operands[types[0]]

        # if the CR field is 0 then it can be dropped
        if val0 == 0:
            opers = ( op1(offset, va), )
        else:
            opers = ( op0(val0, va), op1(offset, va) )

    return opers

def case_E_LI20(types, data, va):
    val0 = (data & 0x3E00000) >> 21
    op0 = operands[types[0]]
    val1 = ((data & 0x1F0000) >> 5)
    val1 |= ((data & 0x7800) << 5)
    val1 |= (data & 0x7FF)
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_M(types, data, va):
    val1 = (data & 0x3E00000) >> 21
    op1 = operands[types[1]]
    val0 = (data & 0x1F0000) >> 16
    op0 = operands[types[0]]
    val2 = (data & 0xF800) >> 11
    op2 = operands[types[2]]
    val3 = (data & 0x7C0) >> 6
    op3 = operands[types[3]]
    val4 = (data & 0x3E) >> 1
    op4 = operands[types[4]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va), op3(val3, va), op4(val4, va) )
    return opers

def case_E_XCR(types, data, va):
    val0 = (data & 0x3800000) >> 23
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11
    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_XLSP(types, data, va):
    val0 = (data & 0x3800000) >> 23
    op0 = operands[types[0]]
    val1 = (data & 0x1C0000) >> 18
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_NONE(types, data, va):
    opers = tuple()
    return opers


# e_ instructions also use the same break-down (formerly case_F_XRA)
def case_E_XRA(types, data, va):
    val1 = (data & 0x3E00000) >> 21
    op1 = operands[types[0]]

    val0 = (data & 0x1F0000) >> 16
    op0 = operands[types[1]]

    val2 = (data & 0xF800) >> 11
    op2 = operands[types[2]]

    opers = (op0(val0, va), op1(val1, va), op2(val2, va))
    return opers

e_handlers: Dict[int, Callable] = {
    E_X: case_E_X,
    E_XL: case_E_XL,
    E_XRA: case_E_XRA,
    E_D: case_E_D,
    E_D8: case_E_D8,
    E_D8VLS: case_E_D8VLS,
    E_I16A: case_E_I16A,
    E_SCI8: case_E_SCI8,
    E_SCI8I: case_E_SCI8I,
    E_SCI8CR: case_E_SCI8CR,
    E_I16L: case_E_I16L,
    E_I16LS: case_E_I16LS,
    E_BD24: case_E_BD24,
    E_BD15: case_E_BD15,
    E_LI20: case_E_LI20,
    E_M: case_E_M,
    E_XCR: case_E_XCR,
    E_XLSP: case_E_XLSP,
    E_NONE: case_E_NONE,
}

tsizes = {
    INS_STB: 1,
    INS_STH: 2,
    INS_STW: 4,
    INS_LBZ: 1,
    INS_LHZ: 2,
    INS_LWZ: 4,
    INS_LBZU: 1,
    INS_LHZU: 2,
    INS_LWZU: 4,
    INS_LHAU: 2,
    INS_STBU: 1,
    INS_STHU: 2,
    INS_STWU: 4,
    INS_LMW: 4,
    INS_STMW: 4,
    INS_E_LDMVGPRW: 4,
    INS_E_STMVGPRW: 4,
    INS_E_LDMVSPRW: 4,
    INS_E_STMVSPRW: 4,
    INS_E_LDMVSRRW: 4,
    INS_E_STMVSRRW: 4,
    INS_E_LDMVCSRRW: 4,
    INS_E_STMVCSRRW: 4,
    INS_E_LDMVDSRRW: 4,
    INS_E_STMVDSRRW: 4,
    INS_LBZ: 1,
    INS_STB: 1,
    INS_LHA: 2,
    INS_LWZ: 4,
    INS_STW: 4,
    INS_LHZ: 2,
    INS_STH: 2,
    INS_ADD: 4, # not used but needs to be present since it's E_D
}


# Simplified mnemonic transformation functions
def simpleE_ORI(ival, mnem, opcode, opers, iflags):
    if len(opers) == 3 and \
            opers[0].isReg() and opers[0].reg == 0 and \
            opers[1].isReg() and opers[1].reg == 0 and \
            opers[2].isImmed() and opers[2].val == 0 and \
            iflags == IFLAGS_NONE:
        return 'e_nop', INS_NOP, tuple(), iflags
    elif len(opers) == 3 and \
            opers[0].isReg() and opers[1].isReg() and \
            opers[0].reg == opers[1].reg and \
            opers[2].isImmed() and opers[2].val == 0 and \
            iflags == IFLAGS_NONE:
        return 'e_mr', INS_MR, opers[:2], iflags
    else:
        return mnem, INS_ORI, opers, iflags


# this generates the handler table for any function starting with simple*
DISASM32_SIMPLIFIEDS = {}
for k, v in list(globals().items()):
    if k.startswith('simpleE'):
        capmnem = k[6:]
        DISASM32_SIMPLIFIEDS[eval('INS_' + capmnem)] = v

DISASM16_SIMPLIFIEDS = {}
for k, v in list(globals().items()):
    if k.startswith('simpleSE'):
        capmnem = k[6:]
        DISASM16_SIMPLIFIEDS[eval('INS_' + capmnem)] = v


def is_opcode_32bit(first_short: int) -> bool:
    # From "VLE 16-bit and 32-bit Instruction Length Decode Algorithm" pg.5
    # Modified to check just the first byte of the Big Endian VLE opcode
    if (first_short & 0x90) == 0x10:
        return True
    else:
        return False


class VleDisasm(Ppc32EmbeddedDisasm):
    __ARCH__ = envi.ARCH_PPCVLE
    def __init__(self, endian=ENDIAN_MSB, options=CAT_PPC_EMBEDDED, psize=4):
        # any speedy stuff here
        self.psize = psize
        self._dis_regctx = Ppc64RegisterContext()
        self.endian = endian
        self.fmt = ('<I', '>I')[endian]
        self.short_fmt = ('<H', '>H')[endian]
        # Needed for fallback-to-PPC disasm
        self.setCategories(options)

    def disasm16(self, bytez: bytes, offset: int, va: int) -> PpcOpcode:
        # first 4 bits have a value of 0,2,4,6,8,9,A,B,C,D,E (and F, but F is reserved)
        inst_data: int = struct.unpack_from(self.short_fmt, bytez, offset)[0]

        for form_mask, mask_dict in se_ops.items():
            candidate_opcode = inst_data & form_mask
            candidate_instruction = mask_dict.get(candidate_opcode, None)
            if candidate_instruction:
                mnem, num_fields, opcode, fields, iflags = candidate_instruction
                # TODO: this field calculation step seems like it should be precomputed
                opieces: List[tuple] = [()] * num_fields

                for k in range(num_fields):
                    field_mask, shr, shl, add, idx, ftype = fields[k]
                    value = (inst_data & field_mask)
                    value >>= shr
                    value <<= shl
                    value += add

                    if ftype == TYPE_JMP:
                        value = e_bits.bsigned(value, 9)
                    elif ftype in (TYPE_MEM, TYPE_SE_MEM, TYPE_REG_SE):
                        if value & 8:
                            value = (value & 0x7) + 24

                    opieces[idx] = (ftype, value)

                k = 0
                opers = []
                while k < num_fields:
                    ftype, value = opieces[k]
                    handler = operands[ftype]
                    if handler is None:
                        raise Exception(f'Instruction {inst_data:04x} opiece {k} ftype {ftype} had no handler')

                    if ftype in (TYPE_MEM, TYPE_SE_MEM):
                        k += 1
                        ft2, val2 = opieces[k]
                        if ft2 != TYPE_IMM:
                            print("PROBLEM! ft2 is not TYPE_IMM!")

                        opers.append(handler(value, val2, va, tsize=tsizes.get(opcode)))
                    else:
                        opers.append(handler(value, va))

                    k += 1

                simpleMnemFunc = DISASM16_SIMPLIFIEDS.get(opcode)
                if simpleMnemFunc is not None:
                    mnem, opcode, opers, iflags = simpleMnemFunc(inst_data, mnem, opcode, opers, iflags)

                iflags |= envi.ARCH_PPCVLE
                return PpcOpcode(va, opcode, mnem, size=2, operands=opers, iflags=iflags)

        raise envi.InvalidInstruction(bytez[offset:offset+4], 'No matching 16-bit instruction: 0x%04x' % inst_data, va)


    def disasm32(self, bytez: bytes, offset: int, va: int) -> PpcOpcode:
        inst_data: int = struct.unpack_from(self.fmt, bytez, offset)[0]

        for form_mask, mask_dict in e_ops.items():
            candidate_opcode = inst_data & form_mask
            candidate_instruction = mask_dict.get(candidate_opcode, None)
            if candidate_instruction:
                mnem, form, opcode, types, iflags = candidate_instruction

                handler = e_handlers[form]
                if handler == None:
                    raise Exception("Unknown FORM handler: %x" % form)

                # Special-case certain forms as we work out when to pass tsize
                if form in (E_D, E_D8, E_D8VLS):
                    opers = handler(types, inst_data, va, tsize=tsizes[opcode])
                else:
                    opers = handler(types, inst_data, va)

                simpleMnemFunc = DISASM32_SIMPLIFIEDS.get(opcode)
                if simpleMnemFunc is not None:
                    mnem, opcode, opers, iflags = simpleMnemFunc(inst_data, mnem, opcode, opers, iflags)

                iflags |= envi.ARCH_PPCVLE
                return PpcOpcode(va, opcode, mnem, size=4, operands=opers, iflags=iflags)

        # Didn't parse as an e_op, so fall back to PpcDisasm
        return super(Ppc32EmbeddedDisasm, self).disasm_booke(bytez, offset, va)


    def disasm(self, bytez: bytes, offset: int, va: int) -> PpcOpcode:
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        This handles VLE decoding, which includes 32-bit Book E instructions
        """

        # Ensure that the target address is 2-byte aligned
        if offset & 0x1:
            raise envi.InvalidAddress(va)

        if is_opcode_32bit(bytez[offset]):
            ppc_opcode = self.disasm32(bytez, offset, va)
        else:
            ppc_opcode = self.disasm16(bytez, offset, va)

        return ppc_opcode
