#!/usr/bin/env python
'''
tables and logic adapted from:
    https://github.com/wargio/libvle
    https://github.com/ehntoo/libvle

special thanks to wargio and ehntoo for their hard work

adapted by atlas <atlas@r4780y.com>, bugfixes and unit tests by @sprout42.
'''

from .vle_ops import *
from .regs import *
import envi
import struct
from .disasm_classes import *

import envi.bits as e_bits


operands = (
        None,
        PpcRegOper,
        PpcRegOper,
        PpcImmOper,
        PpcSImm32Oper,
        PpcMemOper,
        PpcJmpRelOper,
        PpcCrOper,
        )

def case_E_X(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]
    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_XL(types, data, va):
    #print(types, hex(data))
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    #print("E_XL", op0, val0, op1, val1, op2, val2)
    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_D(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = data & 0xFFFF;
    if (val2 & 0x8000) :
        val2 = 0xFFFF0000 | val2;

    # holy crap, this table is a mess.  too C-ish, not Pythonic.
    if types[1] == TYPE_MEM:
        if types[2] == TYPE_REG and val1 == 0:
            opers = ( op0(val0, va), PpcImmOper(val2, va) )
        else:
            opers = ( op0(val0, va), op1(val1, val2, va) )
    else:
        op2 = operands[types[2]]
        opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )

    return opers

def case_E_D8(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]

    val2 = data & 0xFF;
    if (val2 & 0x80):
            val2 = 0xFFFFFF00 | val2;

    opers = ( op0(val0, va), op1(val1, val2, va) )
    return opers

# Handles the new multiple load/store VLE instructions
def case_E_D8VLS(types, data, va):
    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[0]]

    val1 = data & 0xFF;
    if (val1 & 0x80):
        val1 = 0xFFFFFF00 | val1;

    opers = ( op0(val0, val1, va), )
    return opers

def case_E_I16A(types, data, va):
    val1 = (data & 0x3E00000) >> 10;
    op1 = operands[types[0]]
    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[1]]
    val1 |= (data & 0x7FF);

    opers = ( op0(val0, va), op1(val1, va) )
    #print("E_I16/A", opers)
    return opers

case_E_IA16 = case_E_I16A


SCI_mask = (0xffffff00, 0xffff00ff, 0xff00ffff, 0x00ffffff)
def case_E_SCI8(types, data, va):
    opers = []
    if (types[0] != TYPE_NONE):
        val0 = (data & 0x3E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if (types[1] != TYPE_NONE):
        val1 = (data & 0x1F0000) >> 16;
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

    if (types[2] != TYPE_NONE):
        ui8 = data & 0xFF;
        scl = (data & 0x300) >> 8;
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
    val1 = (data & 0x3E00000) >> 21;
    op1 = operands[types[0]]
    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[1]]
    ui8 = data & 0xFF;
    scl = (data & 0x300) >> 8;
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
    val0 = (data & 0x0600000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    ui8 = data & 0xFF;
    scl = (data & 0x300) >> 8;
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
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 5;
    val1 |= (data & 0x7FF);
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_I16LS(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]

    val1 = (data & 0x1F0000) >> 5;
    val1 |= (data & 0x7FF);
    # this is technically incorrect, but makes disassembly prettier to look at.
    val1 <<= 16

    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_BD24(types, data, va):
    val0 = data & 0x01FFFFFE;
    offset = e_bits.bsigned(val0, 25)

    op0 = operands[types[0]]

    opers = ( op0(offset, va), )
    return opers

def case_E_BD15(types, data, va):
    val1 = data & 0xFFFE;
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
        val0 = (data & 0xC0000) >> 18;
        op0 = operands[types[0]]

        # if the CR field is 0 then it can be dropped
        if val0 == 0:
            opers = ( op1(offset, va), )
        else:
            opers = ( op0(val0, va), op1(offset, va) )

    return opers

def case_E_LI20(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = ((data & 0x1F0000) >> 5);
    val1 |= ((data & 0x7800) << 5);
    val1 |= (data & 0x7FF);
    op1 = operands[types[1]]
    if (val1 & 0x80000) :
            val1 = 0xFFF00000 | val1;

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_M(types, data, va):
    val1 = (data & 0x3E00000) >> 21;
    op1 = operands[types[1]]
    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[0]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]
    val3 = (data & 0x7C0) >> 6;
    op3 = operands[types[3]]
    val4 = (data & 0x3E) >> 1;
    op4 = operands[types[4]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va), op3(val3, va), op4(val4, va) )
    return opers

def case_E_XCR(types, data, va):
    val0 = (data & 0x3000000) >> 24;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_E_XLSP(types, data, va):
    val0 = (data & 0x3800000) >> 23;
    op0 = operands[types[0]]
    val1 = (data & 0x1C0000) >> 18;
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
    return opers

def case_E_NONE(types, data, va):
    opers = tuple()
    return opers

def case_F_EVX(types, data, va):
    opers = []
    if (types[0] != TYPE_NONE):
        val0 = (data & 0x3E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if (types[1] != TYPE_NONE):
        #print(types[1])
        val1 = (data & 0x1F0000) >> 16;
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

    if (types[2] != TYPE_NONE):
        val2 = (data & 0xF800) >> 11;
        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    return opers

def case_F_X_Z(types, data, va):
    opers = []
    if (types[0] != TYPE_NONE):
        val0 = (data & 0x3E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if (types[1] != TYPE_NONE):
        val1 = (data & 0x1F0000) >> 16;
        if types[1] == TYPE_REG and val1 == 0:
            opers.append(PpcImmOper(val1, va))
        else:
            op1 = operands[types[1]]
            opers.append(op1(val1, va))

    if (types[2] != TYPE_NONE):
        val2 = (data & 0xF800) >> 11;
        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    return opers

case_F_X    = case_F_EVX
case_F_XO   = case_F_EVX

def case_F_X_2(types, data, va):
    opers = []
    if (types[0] != TYPE_NONE):
        #print(types[1])
        val1 = (data & 0x1F0000) >> 16;
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

    if (types[1] != TYPE_NONE):
        val0 = (data & 0x3E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if (types[2] != TYPE_NONE):
        val2 = (data & 0xF800) >> 11;
        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    return opers

def case_F_X_WRTEEI(types, data, va):
    # Can't figure out a good generic way to do this with the F_X handler
    val0 = (data & 0x00008000) >> 15
    op0 = operands[types[0]]
    opers = ( op0(val0, va), )
    return opers

def case_F_X_MTCRF(types, data, va):
    # Can't figure out a good generic way to do this with the F_X or F_XFX or
    # F_XO handlers
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]

    val1 = (data & 0x000FF000) >> 12
    op1 = operands[types[1]]

    # mtcrf fields should be reversed
    opers = ( op1(val1, va), op0(val0, va) )
    return opers

def case_F_XRA(types, data, va):
    val1 = (data & 0x3E00000) >> 21;
    op1 = operands[types[0]]

    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[1]]

    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    opers = (op0(val0, va), op1(val1, va), op2(val2, va))
    return opers

# e_ instructions also use the same break-down.
case_E_XRA = case_F_XRA

def case_F_CMP(types, data, va):
    val0 = (data & 0x3800000) >> 23;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    # if the first operand is 0 then it can be dropped
    if val0 == 0:
        opers = ( op1(val1, va), op2(val2, va) )
    else:
        opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_F_DCBF(types, data, va):
    val0 = (data & 0x0E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_F_DCBL(types, data, va):
    val0 = (data & 0x1E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_F_DCI(types, data, va):
    val0 = (data & 0xE00000) >> 21;
    op0 = operands[types[0]]

    opers = ( op0(val0, va), )
    return opers

def case_F_EXT(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va), )
    return opers

def case_F_A(types, data, va):
    opers = []
    if types[0] != TYPE_NONE:
        val0 = (data & 0x3E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if types[1] != TYPE_NONE:
        # If this type is REG and the value is 0, add a constant 0 instead
        val1 = (data & 0x1F0000) >> 16;
        if types[1] == TYPE_REG and val1 == 0:
            opers.append(PpcImmOper(val1, va))
        else:
            op1 = operands[types[1]]
            opers.append(op1(val1, va))

    if types[2] != TYPE_NONE:
        val2 = (data & 0xF800) >> 11;
        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    if types[3] != TYPE_NONE:
        op3 = operands[types[3]]
        # If the type is CR, then use only the upper 3 bits
        if types[3] == TYPE_CR:
            val3 = (data & 0x700) >> 8;
            # unless the upper 3 bits are 0 then this operand can just be
            # dropped
            if val3 != 0:
                opers.append(op3(val3, va))
        else:
            val3 = (data & 0x7C0) >> 6;
            opers.append(op3(val3, va))

    return opers

def case_F_XFX(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]

    opers = ( op0(val0, va), )
    return opers

def case_F_XER(types, data, va):
    val0 = (data & 0x3800000) >> 23;
    op0 = operands[types[0]]

    opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )
    return opers

def case_F_MFPR(types, data, va):
    # From register is first arg
    val0 = (data & 0x03E00000) >> 21;
    op0 = operands[types[0]]

    # To SPR is second arg
    val1 =  (data & 0x001F0000) >> 16
    val1 |= (data & 0x0000F800) >> 6
    val1 += REG_OFFSET_SPR
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va))
    return opers

def case_F_MTPR(types, data, va):
    # To SPR is first arg
    val0 =  (data & 0x001F0000) >> 16
    val0 |= (data & 0x0000F800) >> 6
    val0 += REG_OFFSET_SPR
    op0 = operands[types[0]]

    # From register is second arg
    val1 = (data & 0x03E00000) >> 21;
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va))
    return opers

def case_F_NONE(types, data, va):
    opers = tuple()
    return opers


e_handlers = {
        E_X: case_E_X,
        E_XL: case_E_XL,
        E_XRA: case_E_XRA,
        E_D: case_E_D,
        E_D8: case_E_D8,
        E_D8VLS: case_E_D8VLS,
        E_I16A: case_E_I16A,
        E_IA16: case_E_IA16,
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

ppc_handlers = {
        F_X: case_F_X,
        F_XO: case_F_XO,
        F_XRA: case_F_XRA,
        F_X_2: case_F_X_2,
        F_X_WRTEEI: case_F_X_WRTEEI,
        F_X_MTCRF: case_F_X_MTCRF,
        F_X_Z: case_F_X_Z,
        F_EVX: case_F_EVX,
        F_CMP: case_F_CMP,
        F_DCBF: case_F_DCBF,
        F_DCBL: case_F_DCBL,
        F_DCI: case_F_DCI,
        F_EXT: case_F_EXT,
        F_A: case_F_A,
        F_XFX: case_F_XFX,
        F_XER: case_F_XER,
        F_MFPR: case_F_MFPR,
        F_MTPR: case_F_MTPR,
        F_NONE: case_F_NONE,
        }


def find_ppc(buf, offset, endian=True, va=0):
    fmt = ('<I', '>I')[endian]
    data, = struct.unpack_from(fmt, buf, offset)

    for mnem, op, mask, form, opcode, cond, types, iflags in ppc_ops:
        #print(mnem, op, mask, type)
        if (op & data) == op and (mask & data) == data:
            #print(mnem, form, opcode, types, hex(data))
            size = 4

            handler = ppc_handlers[form]
            if handler == None:
                raise Exception("Unknown FORM handler: %x" % form)

            opers = handler(types, data, va)

            # Some instrucions have aliases that depend on some of the
            # instruction parameters matching and can't be identified with
            # static masks
            mnem_alises = {
                'or': 'mr',
                'or.': 'mr.',
                'nor': 'not',
                'nor.': 'not.',
            }
            if mnem in mnem_alises:
                # For this to be valid there must be 3 register arguments and
                # the last two must match.
                if len(opers) == 3 and \
                        isinstance(opers[1], PpcRegOper) and \
                        isinstance(opers[2], PpcRegOper) and \
                        opers[1].reg == opers[2].reg:
                    mnem = mnem_alises[mnem]
                    opers = opers[0:-1]

            iflags |= envi.ARCH_PPCVLE
            return PpcOpcode(va, 0, mnem, size=size, operands=opers, iflags=iflags)



def find_e(buf, offset, endian=True, va=0):
    fmt = ('<I', '>I')[endian]
    data, = struct.unpack_from(fmt, buf, offset)


    for mnem, op, mask, form, opcode, cond, types, iflags in e_ops:
        #print(mnem, hex(op), hex(mask), types, hex(data))
        if (op & data) == op and (mask & data) == data:
            #print(mnem, form, opcode, types, hex(data))
            size = 4

            handler = e_handlers[form]
            if handler == None:
                raise Exception("Unknown FORM handler: %x" % form)

            opers = handler(types, data, va)

            iflags |= envi.ARCH_PPCVLE
            return PpcOpcode(va, 0, mnem, size=size, operands=opers, iflags=iflags)


def find_se(buf, offset, endian=True, va=0):
    fmt = ('<H', '>H')[endian]
    data, = struct.unpack_from(fmt, buf, offset)

    opers = None
    for mnem, op, mask, n, opcode, cond, fields, iflags in se_ops:
        #print(mnem, op, mask, type)
        if (op & data) == op and (mask & data) == data:
            #print("LOCK: ", mnem, op, hex(mask), fields, hex(data), n)
            # prefill the array since this wonky thing likes to build backwards?
            opieces = [None for x in range(n)]

            skip = 0
            for k in range(n):
                #print("field: ", fields[k])
                mask, shr, shl, add, idx, ftype = fields[k]
                #print(repr(opieces))
                #raw_input("k: %x   " % (k) +  "mask: %x  shr: %x  shl: %x  add: %x  idx: %x, ftype: %x" % fields[k])
                #print("k: %x   " % (k) +  "mask: %x  shr: %x  shl: %x  add: %x  idx: %x, ftype: %x" % fields[k])
                value = (data & mask)
                value >>= shr
                value <<= shl
                value += add
                #print(data, value)

                if ftype == TYPE_JMP:
                    value = e_bits.bsigned(value, 9)
                elif ftype in [TYPE_MEM, TYPE_REG_SE]:
                    if value & 8:
                        value = (value & 0x7) + 24

                opieces[idx] = (ftype, value)
                k += 1

            k = 0
            skip = 0
            opers = []
            while k < n:
                ftype, value = opieces[k]
                handler = operands[ftype]

                if ftype == TYPE_MEM:
                    k += 1
                    ft2, val2 = opieces[k]
                    if ft2 != TYPE_IMM:
                        print("PROBLEM! ft2 is not TYPE_IMM!")

                    opers.append(handler(value, val2, va))
                else:
                    opers.append(handler(value, va))

                k += 1

            iflags |= envi.ARCH_PPCVLE
            return PpcOpcode(va, 0, mnem, size=2, operands=opers, iflags=iflags)

class VleDisasm:
    def __init__(self, endian=True):
        # any speedy stuff here
        self._dis_regctx = Ppc64RegisterContext()
        self.endian = endian

    def disasm(self, bytes, offset, va):
        '''
        straw man.  make all in one from the ppc, e, se decodings..
        '''
        op = None

        bytelen = len(bytes)
        if bytelen >= offset + 4:
            op = find_ppc(bytes, offset, self.endian, va)

            if op == None:
                op = find_e(bytes, offset, self.endian, va)

        if op == None and bytelen >= offset + 2:
            op = find_se(bytes, offset, self.endian, va)

        if op == None:
            raise envi.InvalidInstruction(bytes[offset:offset+4], 'No Instruction Matched', va)

        return op

