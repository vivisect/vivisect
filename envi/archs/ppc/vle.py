#!/usr/bin/env python
'''
tables and logic adapted from:
    https://github.com/wargio/libvle
    https://github.com/ehntoo/libvle

special thanks to wargio and ehntoo for their hard work

adapted by atlas <atlas@r4780y.com>
'''

from vle_ops import *
from regs import *
import envi
import struct
from disasm_classes import *

import envi.bits as e_bits


operands = (
        None,
        PpcRegOper,
        PpcImmOper,
        PpcMemOper,
        PpcJmpOper,
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
    #print types, hex(data)
    val0 = (data & 0x3E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16;
    op1 = operands[types[1]]
    val2 = (data & 0xF800) >> 11;
    op2 = operands[types[2]]

    #print "E_XL", op0, val0, op1, val1, op2, val2
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
    
    if types[1] == TYPE_MEM:
        opers = ( op0(val0, va), op1(val1, val2, va) )  # holy crap, this table is a mess.  too C-ish, not Pythonic.
    else:
        op2 = operands[types[2]]
        opers = ( op0(val0, va), op1(val1, va), op2(val2, va) )  # holy crap, this table is a mess.  too C-ish, not Pythonic.

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

def case_E_I16A(types, data, va):
    val1 = (data & 0x3E00000) >> 10;
    op1 = operands[types[0]]
    val0 = (data & 0x1F0000) >> 16;
    op0 = operands[types[1]]
    val1 |= (data & 0x7FF);
    if (val1 & 0x8000):
        val1 = 0xFFFF0000 | val1;
    

    opers = ( op0(val0, va), op1(val1, va) )
    #print "E_I16/A", opers
    return opers

case_E_IA16 = case_E_I16A


SCI_mask = (0xffffff00, 0xffff00ff, 0xff00ffff, 0x00ffffff)
def case_E_SCI8(types, data, va):
    val0 = (data & 0x3E00000) >> 21;
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
    switch (scl) {
            case 0:
                    val2 = ui8 | (f ? 0xffffff00 : 0);
                    break;
            case 1:
                    val2 = (ui8 << 8) | (f ? 0xffff00ff : 0);
                    break;
            case 2:
                    val2 = (ui8 << 16) | (f ? 0xff00ffff : 0);
                    break;
            default:
                    val2 = (ui8 << 24) | (f ? 0x00ffffff : 0);
                    break;
    }
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
    val0 = data & 0x1FFFFFE;
    if (val0 & 0x100000):
        val0 |= 0xFE000000;

    op0 = operands[types[0]]

    opers = ( op0(val0, va), )
    return opers

def case_E_BD15(types, data, va):
    val0 = (data & 0xC0000) >> 18;
    op0 = operands[types[0]]
    val1 = data & 0xFFFE;
    if (val1 & 0x8000):
        val1 |= 0xFFFF0000;
    
    op1 = operands[types[1]]

    opers = ( op0(val0, va), op1(val1, va) )
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
        #print types[1]
        val1 = (data & 0x1F0000) >> 16;
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
        #print types[1]
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
        val0 = (data & 0x1E00000) >> 21;
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if types[1] != TYPE_NONE:
        val1 = (data & 0x1F0000) >> 16;
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

    if types[2] != TYPE_NONE:
        val2 = (data & 0xF800) >> 11;
        op2 = operands[types[2]]
        opers.append(op2(val2, va))

    if types[3] != TYPE_NONE:
        val3 = (data & 0x7C0) >> 6;
        op3 = operands[types[3]]
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
    val0 = (data & 0x1E00000) >> 21;
    op0 = operands[types[0]]
    val1 = (data & 0x1F0000) >> 16
    val1 |= (data &  0xF800) >> 6
    val1 += REG_OFFSET_SPR
    op1 = operands[types[1]]
    #print op0, val0, op1, val1
    opers = ( op0(val0, va), op1(val1, va))
    return opers

def case_F_MTPR(types, data, va):
    #inverted
    opers = []
    if types[0] != TYPE_NONE:
        val0 = (data & 0x001F0000) >> 16
        val0 |= (data &  0x00F800) >> 6
        val0 += REG_OFFSET_SPR
        op0 = operands[types[0]]
        opers.append(op0(val0, va))

    if types[1] != TYPE_NONE:
        val1 = (data & 0x1E00000) >> 21;
        op1 = operands[types[1]]
        opers.append(op1(val1, va))

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
        E_I16A: case_E_I16A,
        E_IA16: case_E_IA16,
        E_SCI8: case_E_SCI8,
        E_SCI8I: case_E_SCI8I,
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
        #print mnem, op, mask, type
        if (op & data) == op and (mask & data) == data:
            #print mnem, form, opcode, types, hex(data)
            size = 4

            handler = ppc_handlers[form]
            if handler == None:
                raise Exception("Unknown FORM handler: %x" % form)

            opers = handler(types, data, va)

            iflags |= envi.ARCH_VLE
            return PpcOpcode(va, 0, mnem, size=size, operands=opers, iflags=iflags)



def find_e(buf, offset, endian=True, va=0):
    fmt = ('<I', '>I')[endian]
    data, = struct.unpack_from(fmt, buf, offset)


    for mnem, op, mask, form, opcode, cond, types, iflags in e_ops:
        #print mnem, hex(op), hex(mask), types, hex(data)
        if (op & data) == op and (mask & data) == data:
            #print mnem, form, opcode, types, hex(data)
            size = 4

            handler = e_handlers[form]
            if handler == None:
                raise Exception("Unknown FORM handler: %x" % form)

            opers = handler(types, data, va)

            iflags |= envi.ARCH_VLE
            return PpcOpcode(va, 0, mnem, size=size, operands=opers, iflags=iflags)


def find_se(buf, offset, endian=True, va=0):
    fmt = ('<H', '>H')[endian]
    data, = struct.unpack_from(fmt, buf, offset)

    opers = None
    for mnem, op, mask, n, opcode, cond, fields, iflags in se_ops:
        #print mnem, op, mask, type
        if (op & data) == op and (mask & data) == data:
            #print "LOCK: ", mnem, op, hex(mask), fields, hex(data), n
            # prefill the array since this wonky thing likes to build backwards?
            opieces = [None for x in range(n)]

            skip = 0
            for k in range(n):
                #print "field: ", fields[k]
                mask, shr, shl, add, idx, ftype = fields[k]
                #print(repr(opieces))
                #raw_input("k: %x   " % (k) +  "mask: %x  shr: %x  shl: %x  add: %x  idx: %x, ftype: %x" % fields[k])
                #print("k: %x   " % (k) +  "mask: %x  shr: %x  shl: %x  add: %x  idx: %x, ftype: %x" % fields[k])
                value = (data & mask)
                value >>= shr
                value <<= shl
                value += add

                handler = operands[ftype]
                if ftype == TYPE_JMP and value & 0x100:
                    value = e_bits.signed(value | 0xfffffe00, 4)
                elif ftype == TYPE_REG and value & 8:
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
                    if ft2 != TYPE_MEM:
                        print "PROBLEM! ft2 is not TYPE_MEM!"

                    opers.append(handler(value, val2, va))
                else:
                    opers.append(handler(value, va))

                k += 1

            iflags |= envi.ARCH_VLE
            return PpcOpcode(va, 0, mnem, size=2, operands=opers, iflags=iflags)

class VleDisasm:
    def __init__(self, endian=True):
        # any speedy stuff here
        self._dis_regctx = PpcRegisterContext()
        self.endian = endian
        #self.setEndian(endian)  # FIXME: when Endianness is dragged through Viv.


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




'''
tests
'''

example_1  = ''.join(['%c'%x for x in (0x00, 0x80, 0x18, 0x21, 0x06, 0xF0, 0xD5, 0x01, 0x79, 0xFF, 0xAF, 0x09, 0xC5, 0x01, 0x00, 0xD3, 0x00, 0x90, 0x20, 0xF1, 0x00, 0x04)])
example_2  = ''.join(['%c'%x for x in (0x2D, 0x07, 0x70, 0xD8, 0xE3, 0xFE, 0x70, 0x0B, 0x02, 0xF0, 0x6D, 0xC3, 0x44, 0x30, 0x1C, 0xC6, 0xC0, 0x00, 0xD1, 0x06, 0x44, 0x30, 0x02, 0x78, 0xD1, 0x06, 0xC0, 0x06, 0x66, 0x40, 0xE2, 0xFE, 0x00, 0x04)])
se_only    = ''.join(['%c'%x for x in (0x04, 0x7f, 0x21, 0xec, 0x46, 0x10, 0x47, 0x01, 0x45, 0x32, 0x2f, 0x14, 0xe8, 0xfa, 0xe9, 0x00, 0xe7, 0x14, 0x61, 0x2b, 0x00, 0x06, 0x00, 0x07, 0x63, 0x17, 0x00, 0x04, 0x00, 0x05, 0x2c, 0x06, 0x64, 0x10, 0x66, 0x74, 0x0c, 0x10, 0x0e, 0xcf, 0x0f, 0x91, 0x2b, 0x63, 0x0d, 0x76, 0x22, 0xbc, 0x00, 0xd1, 0x00, 0xf2, 0x00, 0xce, 0x00, 0xe8, 0x00, 0x00, 0x00, 0x01, 0x88, 0x18, 0xa9, 0x84, 0x4c, 0xf4, 0xcf, 0x60, 0x03, 0x07, 0x00, 0xa3, 0x00, 0x84, 0x01, 0x0f, 0x02, 0x2f, 0x00, 0xb6, 0x00, 0x9f, 0x05, 0x43, 0x00, 0x38, 0x00, 0x29, 0x44, 0x10, 0x00, 0x09, 0x00, 0x0a, 0x00, 0x08, 0x00, 0x02, 0x42, 0x65, 0x6c, 0x77, 0x41, 0xe6, 0x6a, 0x89, 0x40, 0x0e, 0x69, 0x9d, 0x9a, 0x02, 0xb6, 0x1e, 0xd0, 0x7d, 0x06, 0x21, 0x07, 0xad, 0x25, 0x77, 0x27, 0x29, 0xe9, 0xc2)])
e_only     = ''.join(['%c'%x for x in (0x1c, 0x83, 0x00, 0x1b, 0x70, 0xc0, 0x8c, 0x56, 0x71, 0x01, 0x93, 0x21, 0x18, 0x46, 0x88, 0x37, 0x18, 0x65, 0x81, 0x37, 0x18, 0x84, 0x9a, 0x37, 0x18, 0xe8, 0x93, 0x37, 0x71, 0x3f, 0xce, 0xed, 0x71, 0x40, 0xe8, 0x05, 0x19, 0xab, 0xc8, 0x39, 0x19, 0xec, 0xc2, 0x37, 0x78, 0x00, 0x00, 0xec, 0x78, 0x00, 0x00, 0x01, 0x7a, 0x03, 0xff, 0xcc, 0x7a, 0x1f, 0x00, 0x01, 0x70, 0xc2, 0x9b, 0x33, 0x18, 0x46, 0xa9, 0x37, 0x7c, 0x87, 0x58, 0x1c, 0x73, 0xec, 0xb5, 0xef, 0x7c, 0x06, 0x40, 0x5c, 0x70, 0x4d, 0xba, 0x34, 0x73, 0xe1, 0xae, 0xe0, 0x18, 0xa3, 0xab, 0x37, 0x7f, 0xa3, 0x02, 0x02, 0x7c, 0x02, 0xe9, 0x02, 0x7d, 0xf0, 0x8a, 0x42, 0x7d, 0xe0, 0x19, 0xc2, 0x7d, 0xe0, 0x18, 0x42, 0x7d, 0x8d, 0x73, 0x82, 0x7e, 0x72, 0x8b, 0x42, 0x7c, 0x00, 0x01, 0x82, 0x30, 0xe3, 0xcc, 0x0d, 0x18, 0xe5, 0x00, 0xcc, 0x39, 0x0a, 0x01, 0xff, 0x19, 0x01, 0x03, 0xff, 0x58, 0xe0, 0x18, 0x38, 0x18, 0xe0, 0x01, 0x3e, 0x70, 0x06, 0x1b, 0x33, 0x70, 0x26, 0xe3, 0x33, 0x18, 0xa3, 0x08, 0x18, 0x50, 0xa3, 0x27, 0x28, 0x18, 0xc2, 0x02, 0x72, 0x7c, 0x98, 0x00, 0x20, 0x19, 0x2a, 0xa0, 0x37, 0x70, 0x01, 0xa6, 0x68, 0x70, 0xa4, 0xc3, 0x45, 0x70, 0xb4, 0xd3, 0x45, 0x19, 0x27, 0xd8, 0x37, 0x19, 0x07, 0xd1, 0x37, 0x7e, 0xd2, 0x02, 0x30, 0x7c, 0x48, 0x02, 0x31, 0x7c, 0x74, 0xaa, 0x70, 0x7c, 0x62, 0xaa, 0x71, 0x76, 0x64, 0x6a, 0x1e, 0x74, 0x24, 0x68, 0x63, 0x7e, 0x6c, 0x30, 0x70, 0x7d, 0x4c, 0xa0, 0x71, 0x7c, 0x20, 0x84, 0x70, 0x7c, 0x20, 0x5c, 0x71, 0x34, 0x61, 0x55, 0xf0, 0x1a, 0x76, 0x04, 0xfc, 0x5c, 0x15, 0x02, 0x9a, 0x18, 0x37, 0x05, 0xff, 0x18, 0x03, 0x09, 0x04, 0x54, 0x60, 0x3f, 0x21, 0x1a, 0xc4, 0x06, 0xee, 0x18, 0x15, 0xb2, 0x37, 0x1a, 0xc0, 0xbb, 0x37, 0x18, 0x75, 0xe1, 0x37, 0x1a, 0x80, 0xe8, 0x37, 0x79, 0xff, 0xff, 0x82, 0x79, 0xff, 0xfe, 0x67)]) 

# Regression tests for the reported issue #1
#  Tested on Freescale Codewarrior 5.9.0 IDE, Compiler: PPC_eabi v4.3.0.224
#  Proved by HW: MPC5643L(PPCe200)
testcase_1  = ''.join(['%c'%x for x in (
0x7C, 0xC0, 0x23, 0x78, #   or  r6,r0,r4  32bit Common
0x7C, 0xC0, 0x23, 0x79  #   or. r6,r0,r4  32bit Common
)])
testcase_2  = ''.join(['%c'%x for x in (
0x44, 0x70				#   se_or  r0, r7  16bit VLE
)])
testcase_3  = ''.join(['%c'%x for x in (
0x7C, 0x64, 0x18, 0xF8 #   not  r4,r3 | nor r4,r3,r3
)])
testcase_4  = ''.join(['%c'%x for x in (
0x7C, 0xC0, 0x20, 0xF8, #   nor  r6 r0 r4
0x7C, 0xC0, 0x20, 0xF9  #   nor. r6 r0 r4
)])

testcase_5  = ''.join(['%c'%x for x in (
0x7C, 0x80, 0x00, 0xA6, #  mfmsr r4
0x7C, 0x80, 0x01, 0x24, #  mtmsr r4
0x7C, 0x60, 0x82, 0xA6, #  mfspr r3,0x200 gives:0x10 error!
0x7C, 0x60, 0x83, 0xA6, #  mtspr 0x200, r3 gives 0x10 error!
0x7C, 0xA0, 0x00, 0x26, #  mfcr r5
0x7C, 0x00, 0x04, 0xAC, #  msync
0x7C, 0x00, 0x07, 0x64, #  tlbre
0x7C, 0x00, 0x07, 0xA4  #  tlbwe
)])

testcase_6  = ''.join(['%c'%x for x in (
0x1C, 0xC3, 0xFF, 0xFF,  #  e_add16i r6 r3 0xffffffff ''.join(['%c'%x for x in (ok)
0x1D, 0x81, 0x00, 0x10,  #  e_add16i r12 r1 0x10 ''.join(['%c'%x for x in (ok)
0x1F, 0xFF, 0x58, 0x00   #  e_add16i r31 r31 0x5800
)])

testcase_7  =''.join(['%c'%x for x in (
0x55,0xCB,0xFF,0xB8, #   e_stw r14 0xffffffb8(r11) (ok)
0x55,0xEB,0xFF,0xBC, #   e_stw r15 0xffffffbc(r11) (ok)
0x56,0x0B,0xFF,0xC0, #   e_stw r16 0xffffffc0(r11)
0x56,0x2B,0xFF,0xC4, #   e_stw r17 0xffffffc4(r11)
0x56,0x4B,0xFF,0xC8, #   e_stw r18 0xffffffc8(r11)
0x56,0x6B,0xFF,0xCC, #   e_stw r19 0xffffffcc(r11)
0x56,0x8B,0xFF,0xD0, #   e_stw r20 0xffffffd0(r11)
0x56,0xAB,0xFF,0xD4, #   e_stw r21 0xffffffd4(r11)
0x56,0xCB,0xFF,0xD8, #   e_stw r22 0xffffffd8(r11)
0x56,0xEB,0xFF,0xDC, #   e_stw r23 0xffffffdc(r11)
0x57,0x0B,0xFF,0xE0, #   e_stw r24 0xffffffe0(r11)
0x57,0x2B,0xFF,0xE4, #   e_stw r25 0xffffffe4(r11)
0x57,0x4B,0xFF,0xE8, #   e_stw r26 0xffffffe8(r11)
0x57,0x6B,0xFF,0xEC, #   e_stw r27 0xffffffec(r11)
0x57,0x8B,0xFF,0xF0, #   e_stw r28 0xfffffff0(r11)
0x57,0xAB,0xFF,0xF4, #   e_stw r29 0xfffffff4(r11)
0x57,0xCB,0xFF,0xF8, #   e_stw r30 0xfffffff8(r11)
0x57,0xEB,0xFF,0xFC  #   e_stw r31 0xfffffffc(r11)
)])

testcase_8  =''.join(['%c'%x for x in (
0x7C,0x64,0x29,0x2E, #  stwx r3,r4,r5
0x7D,0x28,0x01,0x2E, #  stwx  r9,r8,r0
0x25,0x77,			 #  se_subi  r7,18
0x27,0x77,			 #  se_subi. r7,18
0x63,0x17			 #  se_bgeni r7,11
)])

testcase_9  =''.join(['%c'%x for x in (
0x51, 0xE3, 0x27, 0x28, #  e_lwz r15 0x2728(r3)
0x52, 0x03, 0x27, 0x28, #  e_lwz r16 0x2728(r3)
# 0x7C,0x00,0x81,0x46, #  ?? 5000011e
# 0x55,0x0d #  ?? 40001396
)])


def TEST(tbytez,z):
    count = 0
    x = 0
    print " ==== %s ====" % (tbytez.encode('hex'))
    while x < len(tbytez):
        d = VleDisasm()
        op = d.disasm(tbytez, x, 0)
        if len(op) == 2:
            print '%.2X %.2X\t\t%r' % (ord(tbytez[x]), ord(tbytez[x+1]), op)
        else:
            print '%.2X %.2X %.2X %.2X\t%r' % (ord(tbytez[x]), ord(tbytez[x+1]), ord(tbytez[x+2]), ord(tbytez[x+3]), op)
        x += len(op)
        count += 1

    print "Decoded Opcodes: %d" % count

def doTests():
    TEST(example_1,9);                          
    TEST(example_2, 14);
    TEST(se_only, 63);             
    TEST(e_only, 72);
                                       
    TEST(testcase_1, 2);
    TEST(testcase_2, 1);
    TEST(testcase_3, 1);
    TEST(testcase_4, 2);
    TEST(testcase_5, 8);
    TEST(testcase_6, 3);
    TEST(testcase_7, 18);
    TEST(testcase_8, 5);
    TEST(testcase_9, 2);

if __name__ == '__main__':
    doTests()
