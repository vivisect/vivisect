import envi
import envi.bits as e_bits
import struct

from disasm import H8ImmOper, H8RegDirOper, H8RegIndirOper, H8AbsAddrOper, H8PcOffsetOper
from regs import *
from const import *

bcc = [
        ('bt', envi.IF_NOFALL | envi.IF_BRANCH),
        ('bf',  envi.IF_BRANCH | envi.IF_COND),
        ('bhi', envi.IF_BRANCH | envi.IF_COND),
        ('bls', envi.IF_BRANCH | envi.IF_COND),
        ('bhs', envi.IF_BRANCH | envi.IF_COND),
        ('blo', envi.IF_BRANCH | envi.IF_COND),
        ('bne', envi.IF_BRANCH | envi.IF_COND),
        ('beq', envi.IF_BRANCH | envi.IF_COND),
        ('bvc', envi.IF_BRANCH | envi.IF_COND),
        ('bvs', envi.IF_BRANCH | envi.IF_COND),
        ('bpl', envi.IF_BRANCH | envi.IF_COND),
        ('bmi', envi.IF_BRANCH | envi.IF_COND),
        ('bge', envi.IF_BRANCH | envi.IF_COND),
        ('blt', envi.IF_BRANCH | envi.IF_COND),
        ('bgt', envi.IF_BRANCH | envi.IF_COND),
        ('ble', envi.IF_BRANCH | envi.IF_COND),
    ]

def p_CCR_Rd(va, val, buf, off, tsize):
    # stc
    iflags = 0
    op = val>>4
    rd = val & 0xf
    opers = (
            H8RegDirOper(REG_FLAGS, 4, va),
            H8RegDirOper(rd, tsize, va),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_CCR(va, val, buf, off, tsize):
    # ldc
    iflags = 0
    op = val>>4
    rs = metaFrom8(val & 0xf)
    opers = (
            H8RegDirOper(rs, tsize, va),
            H8RegDirOper(REG_FLAGS, tsize, va),
            )
    return (op, None, opers, iflags, 2)

def p_aAA8_Rd(va, val, buf, off, tsize):
    # mov 0x2###
    iflags = 0
    op = val>>12
    Rd = (val >> 8) & 0xf
    aAA8 = val & 0xf

    opers = (
            H8RegDirOper(Rd, tsize, va, 0),
            H8AbsAddrOper(aAA8),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_aAA8(va, val, buf, off, tsize):
    # mov 0x3###
    iflags = 0
    op = val>>12
    Rs = (val >> 8) & 0xf
    aAA8 = val & 0xf

    opers = (
            H8AbsAddrOper(aAA8),
            H8RegDirOper(Rs, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_i2(va, val, buf, off, tsize):
    # trapa
    iflags = 0
    op = 0x57
    i2 = (val >> 4) & 0x3

    opers = (
            H8ImmOper(i2),
            )
    return (op, None, opers, iflags, 2)

def p_i3_Rd(va, val, buf, off, tsize):
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    iflags = 0
    op = val >> 7
    i3 = (val >> 4) & 0x7
    Rd = val & 0xf

    opers = (
            H8ImmOper(i3),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_i3_aERd(va, val, buf, off, tsize): 
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((((val >> 3)&0xfff0) | (val&0xf))<<13) | ((val2>>3)&0xfff0) | (val&0xf)
    i3 = (val2 >> 4) & 0x7
    ERd = (val >> 4) & 0x7

    opers = (
            H8ImmOper(i3),
            H8RegIndirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_i3_aAA8(va, val, buf, off, tsize): 
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val >> 16) | (val&0xf) | (val2>>15) | (val&0xf)
    i3 = (val2 >> 4) & 0x7
    aa = val & 0xff

    opers = (
            H8ImmOper(i3),
            H8AbsAddrOper(aa),
            )
    return (op, None, opers, iflags, 4)

def p_i8_CCR(va, val, buf, off, tsize): 
    # andc
    iflags = 0
    op = val >> 8
    i8 = val & 0xff

    opers = (
            H8ImmOper(i8),
            )
    return (op, None, opers, iflags, 2)

def p_i8_Rd(va, val, buf, off, tsize): 
    # add.b, addx, and.b, cmp.b
    iflags = 0
    op = val >> 4
    i8 = val & 0xff
    Rd = (val >> 8) & 0xf

    opers = (
            H8ImmOper(i8),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_i16_Rd(va, val, buf, off, tsize): 
    # add.w, and.w, cmp.w
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    i16 = val2
    Rd = val & 0xf

    opers = (
            H8ImmOper(i16),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_i32_ERd(va, val, buf, off, tsize): 
    # add.l, and.l, cmp.l
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 3
    i32 = val2
    ERd = val & 0x7

    opers = (
            H8ImmOper(i32),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 6)

def p_Rd(va, val, buf, off, tsize): 
    # daa, das, dec.b, exts.w, extu.w, inc.b
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_Rd(va, val, buf, off, tsize):  
    # add.b, add.w, addx, and.b, and.w, cmp.b, cmp.w, divxu.b
    iflags = 0
    op = val >> 16
    Rs = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rs, tsize, va, 0),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_Rd_4b(va, val, buf, off, tsize):  
    # divxs.b, mulxs.b
    val2, = struct.unpack('>H', buf[off+2: off+4])
    oszbit = (val2 >> 9) & 1
    iflags = (IF_B, IF_W)[oszbit]
    stsize, dtsize = ((1,2),(2,4))[oszbit]

    op = (val << 8) | (val2 >> 8)
    Rs = (val2 >> 4) & 0xf
    Rd = val2 & 0xf

    opers = (
            H8RegDirOper(Rs, stsize, va, 0),
            H8RegDirOper(Rd, dtsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_Rs_ERd(va, val, buf, off, tsize):  
    # mulxu.w, divxu.w
    iflags = 0
    op = ((val >> 8) << 1) | ((val >> 3) & 1)
    Rs = (val >> 4) & 0xf
    ERd = val & 0x7

    # FIXME: make sure ER# and R# have correct metaregister values
    opers = (
            H8RegDirOper(Rs, tsize, va, 0),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_ERs_ERd(va, val, buf, off, tsize):  
    # add.l, cmp.l
    iflags = IF_L
    op = ((val >> 6)&0xfffe) | ((val >> 3)&1) # first byte, and bits 3 and 7 of second byte
    ERs = (val >> 4) & 0x7
    ERd = val & 0x7

    opers = (
            H8RegDirOper(ERs, tsize, va, 0),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_Rs_ERd_4b(va, val, buf, off, tsize):  
    # divxs.w
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op = (val << 8) | (val2 >> 8)
    Rs = (val2 >> 4) & 0xf
    ERd = val2 & 0x7

    opers = (
            H8RegDirOper(Rs, tsize, va, 0),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)


def p_ERd(va, val, buf, off, tsize):  
    # exts.l, extu.l
    iflags = 0
    op = val >> 4
    ERd = val & 0x7

    opers = (
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_ERs_ERd_4b_unused(va, val, buf, off, tsize):  
    # and.l, or.l
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val << 2) | ((val2 >> 6)&2) | ((val2 >> 3)&1)
    ERs = (val2 >> 4) & 0x7
    ERd = val2 & 0x7

    opers = (
            H8RegDirOper(ERs, tsize, va, 0),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_Rn_Rd(va, val, buf, off, tsize):  
    # bclr, bset, btst
    iflags = 0
    op = val >> 8
    Rn = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            H8RegDirOper(Rn, tsize, va, 0),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_aERs_Rd(va, val, buf, off, tsize):  
    # mov 0x68
    iflags = 0
    op = (val >> 7)
    aERs = (val >> 4) & 0x7
    Rd = (val) & 0xf

    opers = (
            H8RegIndirOper(aERs, tsize, va, disp=0, oflags=0),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_aERsp_Rd(va, val, buf, off, tsize):  
    # mov 0x6c
    iflags = OSZ_FLAGS[tsize]
    op = (val >> 7)
    aERs = (val >> 4) & 0x7
    Rd = (val) & 0xf

    opers = (
            H8RegIndirOper(aERs, tsize, va, disp=0, oflags=OF_POSTINC),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)

def p_Rs_aERdm(va, val, buf, off, tsize):  
    # mov 0x6c
    iflags = OSZ_FLAGS[tsize]
    op = (val >> 7)
    aERd = (val >> 4) & 0x7
    Rs = (val) & 0xf

    opers = (
            H8RegDirOper(Rs, tsize, va, 0),
            H8RegIndirOper(aERd, tsize, va, disp=0, oflags=OF_PREDEC),
            )
    return (op, None, opers, iflags, 4)

def p_Rn_aERd(va, val, buf, off, tsize):  
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((val >> 12)&0xfff0) | (val&0xf) | ((val2>>4)&0xfff0) | (val2&0xf)
    aERd = (val >> 4) & 0x7
    Rn = (val2 >> 4) & 0xf

    opers = (
            H8RegDirOper(Rn, tsize, va, 0),
            H8RegIndirOper(aERd, tsize, va, disp=0, oflags=0),
            )
    return (op, None, opers, iflags, 4)

def p_Rn_aAA8(va, val, buf, off, tsize):  
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val & 0xff00) | ((val2 >> 4)&0xff0) | (val2&0xf)
    Rn = (val2 >> 4) & 0xf
    aAA8 = val & 0xff

    opers = (
            H8RegDirOper(Rn, tsize, va, 0),
            H8AbsAddrOper(aAA8),
            )
    return (op, None, opers, iflags, 4)

def p_aERn(va, val, buf, off, tsize):  
    # jmp, jsr
    iflags = 0
    op = ((val >> 3)&0xfff0) | (val&0xf)
    aERn = (val >> 4) & 0x7

    opers = (
            H8RegIndirOper(aERn, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)

def p_aAA24(va, val, buf, off, tsize):  
    # jmp, jsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 8
    aAA24 = ((val&0xf) << 16) | val2

    opers = (
            H8AbsAddrOper(aAA24),
            )
    return (op, None, opers, iflags, 2)

def p_aaAA8(va, val, buf, off, tsize):  
    # jmp, jsr
    iflags = 0
    op = val >> 8
    aaAA8 = val & 0xff

    opers = (
            H8MemIndirOper(aaAA8),
            )
    return (op, None, opers, iflags, 2)

def p_disp8(va, val, buf, off, tsize):  
    # bcc, bsr
    iflags = 0
    op = val >> 8
    disp8 = e_bits.signed(val & 0xff, 1)

    opers = (
            H8PcOffsetOper(disp8, va),
            )
    return (op, None, opers, iflags, 2)

def p_disp16(va, val, buf, off, tsize):  
    # bcc, bsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val
    disp16 = e_bits.signed(val2, 2)
    
    mnem = None
    if (op & 0xf00 == 0x800):
        opnibble = (val>>4) & 0xf
        mnem, iflags = bcc[opnibble]

    opers = (
            H8PcOffsetOper(disp16, va),
            )
    return (op, mnem, opers, iflags, 4)

def p_Rs_aAA16(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA16 = val2

    opers = (
            H8RegDirOper(Rs, tsize, va),
            H8AbsAddrOper(aAA16),
            )
    return (op, None, opers, iflags, 4)

def p_Rs_aAA24(va, val, buf, off, tsize):
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA24 = val2 & 0xffffff

    opers = (
            H8RegDirOper(Rs, tsize, va),
            H8AbsAddrOper(aAA24),
            )
    return (op, None, opers, iflags, 6)

def p_aAA16_Rd(va, val, buf, off, tsize):  
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA16 = val2

    opers = (
            H8AbsAddrOper(aAA16),
            H8RegDirOper(Rd, tsize, va),
            )
    return (op, None, opers, iflags, 4)

def p_aAA24_Rd(va, val, buf, off, tsize):  
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA16 = val2 & 0xffffff

    opers = (
            H8AbsAddrOper(aAA16),
            H8RegDirOper(Rd, tsize, va),
            )
    return (op, None, opers, iflags, 6)

def p_nooperands(va, val, buf, off, tsize):  
    # eepmov.b, eepmov.w, 
    iflags = 0
    op = val

    opers = ()
    return (op, None, opers, iflags, 2)

def _p_BccDoubles(va, vak, buf, off, tsize):
    # Bcc
    disp, = struct.unpack('>H', buf[off+2: off+4])
    op = val

    opnibble = (val>>4) & 0xf
    mnem, iflags = bcc[opnibble]

    opers = (
            H8PcOffsetOper(),
            )
    return (op, mnem, opers, iflags, 4)

bit_dbles = [
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('error', 0),
        ('bst', 0),
        ('bist', 0),
        ('bor', 0),
        ('bior', 0),
        ('bxor', 0),
        ('bixor', 0),
        ('band', 0),
        ('biand', 0),
        ('bld', 0),
        ('bild', 0),
        ]

def getBitDbl_OpMnem(val, bitlist=bit_dbles):
    op = val >> 7
    mnem, flags = bitlist[(op & 0x1f)]
    return op, mnem, flags

def p_Bit_Doubles(va, val, buf, off, tsize):
    op, mnem, iflags = getBitDbl_OpMnem(val)
    
    i3 = (val>>4) & 0x7
    Rd = val & 0xf

    opers = (
            H8ImmOper(i3),
            H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, mnem, opers, iflags, 2)


def p_01(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])
    mnem = None
    iflags = 0
    isz = 4
    op = (val << 9) | (val2 >> 7)
    opers = None

    diff = (val>>4) & 0xf

    if diff == 0:
        mnem = 'mov'

        # all 0100#### opcodes share these:
        tsize = 4
        iflags |= IF_L

        d2 = val2>>8

        # mov   0100##... where ## is basically another mov encoding with different register sizes
        if d2 == 0x69:
            if val2 & 0x80:
                erd = (val2>>4) & 7
                ers = val2 & 7
                opers = (
                        H8RegDirOper(ers, tsize, va),
                        H8RegIndirOper(erd, tsize, va),
                        )

        elif d2 == 0x6b:
            if val2 & 0x20:
                isz = 8
                val3, = struct.unpack(">I", buf[off+4:off+8])
                if val2 & 0x80:
                    # a
                    erd = val2 & 7
                    aa  = val3 & 0xfff
                    opers = (
                            H8RegDirOper(erd, tsize, va),
                            H8AbsAddrOper(aa),
                            )
                else:
                    # 2
                    ers = val2 & 7
                    aa  = val3 & 0xfff
                    opers = (
                            H8AbsAddrOper(aa),
                            H8RegDirOper(ers, tsize, va),
                            )
            else:
                val3, = struct.unpack(">H", buf[off+4:off+6])
                isz = 6
                if val2 & 0x80:
                    # 8
                    erd = val2 & 7
                    aa  = val3 & 0xff
                    opers = (
                            H8RegDirOper(erd, tsize, va),
                            H8AbsAddrOper(aa),
                            )
                else:
                    # 0
                    ers = val2 & 7
                    aa  = val3 & 0xff
                    opers = (
                            H8AbsAddrOper(aa),
                            H8RegDirOper(ers, tsize, va),
                            )

        elif d2 == 0x6d:    # TODO: test me!!
            er0 = val2 & 7
            er1 = (val2>>4) & 7

            if val2 & 0x80:
                # mov ERs, @-ERd
                if val2 & 0xf0 == 0xf0:
                    # push
                    mnem = 'push'
                    opers = (
                            H8RegDirOper(er0, tsize, va),
                            )
                else:   
                    # mov 
                    opers = (
                            H8RegDirOper(er0, tsize, va),
                            H8RegIndirOper(er1, tsize, va, 0, OF_PREDEC),
                            )
            else:
                # mov @ERs+,ERd
                if val2 & 0xf0 == 0x70:
                    # pop
                    mnem = 'pop'
                    opers = (
                            H8RegDirOper(er0, tsize, va),
                            )
                else:
                    # mov
                    opers = (
                            H8RegIndirOper(er1, tsize, va, 0, OF_POSTINC),
                            H8RegDirOper(er0, tsize, va),
                            )

        elif d2 == 0x6f:
            disp, = struct.unpack('>H', buf[off+4:off+6])
            isz = 6
            er0 = val2 & 7
            er1 = (val2>>4) & 7
            if val2 & 0x80:
                # mov.l ERs, @(d:16,ERd)
                opers = (
                        H8RegDirOper(er1, tsize, va),
                        H8RegIndirOper(er0, tsize, va, disp),
                        )
            else:
                # mov.l @(d:16,ERs), ERd
                opers = (
                        H8RegIndirOper(er1, tsize, va, disp),
                        H8RegDirOper(er0, tsize, va),
                        )

        elif d2 == 0x78:
            val3, disp = struct.unpack(">HI", buf[off+4:off+10])
            if val3 & 0xff20 != 0x6b2: raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

            er0 = val3 & 7
            er1 = (val2>>4) & 7
            if (val3 & 0x80):
                # mov.l ERs, @(d:24,ERd)
                opers = (
                        H8RegDirOper(er0, tsize, va),
                        H8RegIndirOper(er1, tsize, va, disp),
                        )

            else:
                # mov.l @(d:24,ERs), ERd
                opers = (
                        H8RegIndirOper(er1, tsize, va, disp),
                        H8RegDirOper(er0, tsize, va),
                        )

    elif diff == 4:
        # ldc/stc
        # we'll build it for ldc, and reverse it if it's stc
        d2 = val2>>8
        isStc = (val2>>7) & 1
        oflags = 0
        tsize = 2

        if d2 in (0x69, 0x6d):    #@ERs,CCR / @ERs+,CCR
            if d2 == 0x6d:
                oflags = OF_POSTINC
            ers = (val2>>4) & 0x7
            opers = (
                    H8RegIndirOper(ers, tsize, va, oflags=oflags),
                    H8RegDirOper(REG_CCR, 4, va)
                    )

        elif d2 in (0x6f, 0x78):  #@(d:16,ERs),CCR / @(d:24,ERs)
            if d2 == 0x78:
                val3, disp = struct.unpack('>HI', buf[off+4:off+10])
                isStc = (val3>>7) & 1
                isz = 10
            else:
                disp, = struct.unpack('>H', buf[off+4:off+6])
                isz = 6
            ers = (val2>>4) & 0x7
            opers = (
                    H8RegIndirOper(ers, tsize, va, disp),
                    H8RegDirOper(REG_CCR, 4, va)
                    )

        elif d2 == 0x6b:    #@aa:16,CCR / @aa:24,CCR
            if val2 & 0x20:
                aa, = struct.unpack(">I", buf[off+4:off+8])
                isz = 8
            else:
                aa, = struct.unpack(">H", buf[off+4:off+6])
                isz = 6
            isStc = (val2>>7) & 1
            opers = (
                    H8AbsAddrOper(aa),
                    H8RegDirOper(REG_CCR, 4, va)
                    )

        # after all the decisions...
        mnem = ('ldc','stc')[isStc]
        if isStc:
            opers = opers[::-1]

    elif diff == 8:
        # sleep
        op = 0x0180
        mnem = 'sleep'
        opers = tuple()

    elif diff == 0xc:
        if val2 & 0xfd00 == 0x5000:
            # mulxs
            mnem = 'mulxs'
            op, nmnem, opers, iflags, isz =  p_Rs_Rd_4b(va, val, buf, off, tsize=1)
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 0xd:
        if val2 & 0xfd00 == 0x5100:
            mnem = 'divxs'
            # divxs
            op, nmnem, opers, iflags, isz =  p_Rs_Rd_4b(va, val, buf, off, tsize)
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 0xf:
        if val2 & 0xfc00 == 0x6400:
            # or/xor/and
            nop, nmnem, opers, iflags, isz = p_ERs_ERd(va, val2, buf, off, tsize=4)
            op = (val << 8) | (val2 >> 8)
            mnembits = (val2 >> 8) & 3
            mnem = ('or', 'xor', 'and')[mnembits]
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return (op, mnem, opers, iflags, isz)

def p_0a_1a(va, val, buf, off, tsize):

    diff = (val >> 12)
    if val & 0xf0 == 0:
        mnem = ('inc', 'dec')[diff]
        op, nmnem, opers, iflags, isz = p_Rd(va, val, buf, off, tsize=1)
        iflags = IF_B

    elif val & 0xf0 >= 0x80:
        mnem = ('add', 'sub')[diff]
        op, nmnem, opers, iflags, isz = p_ERs_ERd(va, val, buf, off, tsize=4)

    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return (op, mnem, opers, iflags, isz)


data_0b = (
        (4, 0, 1, 'adds'),
        None,
        None,
        None,
        None,
        (2, IF_W, 1, 'inc'),
        None,
        (4, IF_L, 1, 'inc'),
        (4, 0, 2, 'adds'),
        (4, 0, 4, 'adds'),
        None,
        None,
        None,
        (2, IF_W, 2, 'inc'),
        None,
        (4, IF_L, 2, 'inc'),
        )

data_1b = (
        (4, 0, 1, 'subs'),
        None,
        None,
        None,
        None,
        (2, IF_W, 1, 'dec'),
        None,
        (4, IF_L, 1, 'dec'),
        (4, 0, 2, 'subs'),
        (4, 0, 4, 'subs'),
        None,
        None,
        None,
        (2, IF_W, 2, 'dec'),
        None,
        (4, IF_L, 2, 'dec'),
        )

def p_0b_1b(va, val, buf, off, tsize):
    table = (data_0b, data_1b)[val>>12]
    diff = (val>>4)&0xf
    tsize, iflags, imm, mnem = table[diff]

    op = val >> 4
    ERd = val & 0xf

    opers = (
            H8ImmOper(imm),
            H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, mnem, opers, iflags, 2)

def p_0f_1f(va, val, buf, off, tsize):
    aors = val >> 12
    diff = val & 0xf0
    if diff == 0:
        op = val >> 4
        mnem = ('daa', 'das')[aors]
        iflags = 0
        rd = val & 0xf
        opers = (
                H8RegDirOper(rd, 1, va=va, oflags=0),
                )
    elif diff >= 0x80:
        mnem = ('mov', 'cmp')[aors]
        op, nmnem, opers, iflags, isz = p_ERs_ERd(va, val, buf, off, tsize)
    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return (op, mnem, opers, iflags, 2)


shift_info = []
for name in ('shll','shal','shal','shar','rotxl','rotl','rotxr','rotr'):
    shift_info.append( (name, 1) )
    shift_info.append( (name, 2) )
    shift_info.append( None )
    shift_info.append( (name, 4) )
    shift_info.append( None )
    shift_info.append( None )
    shift_info.append( None )
    shift_info.append( None )

for nothing in range(0x14, 0x17):
    for xnothing in range(16):
        shift_info.append(None)

for name1,name2 in (('not','extu'), ('neg', 'exts')):
    shift_info.append( (name1, 1) )
    shift_info.append( (name1, 2) )
    shift_info.append( None )
    shift_info.append( (name1, 4) )
    shift_info.append( None )
    shift_info.append( (name2, 2) )
    shift_info.append( None )
    shift_info.append( (name2, 4) )

def p_shift_10_11_12_13_17(va, val, buf, off, tsize):
    op = val >> 4

    mnem, osz = shift_info[(val>>4)&0xff]
    iflags = OSZ_FLAGS[osz]
    
    # if 32bit (ERd), top bit should always be 0 anyway
    rd = val & 0xf
    opers = (
        H8RegDirOper(rd, osz, va, 0),
        )

    return (op, mnem, opers, iflags, 2)

def p_Mov_6A(va, val, buf, off, tsize):
    op = val >> 4
    if op & 0x8:
        # Rs, @aa:16/24
        if op & 0x2:
            return p_Rs_aAA24(va, val, buf, off, tsize)
        return p_Rs_aAA16(va, val, buf, off, tsize)

    else:
        # @aa:16/24, Rd
        if op & 0x2:
            return p_aAA24_Rd(va, val, buf, off, tsize)

        return p_aAA16_Rd(va, val, buf, off, tsize)

def p_Mov_6C(va, val, buf, off, tsize):
    op = val >> 7
    if op & 0x1:
        # @ERs+, Rd
        return p_aERsp_Rd(va, val, buf, off, tsize)

    else:
        # Rs, @ERd
        return p_Rs_aERdm(va, val, buf, off, tsize)

def p_6c_6d_0100(va, val, buf, off, tsize):
    op = val >> 7
    iflags = OSZ_FLAGS[tsize]
    isz = 4
    mnem = None

    er0 = val & 7
    er1 = (val>>4) & 7

    if val & 0x80:
        # mov ERs, @-ERd
        if val & 0xf0 == 0xf0:
            # push
            mnem = 'push'
            opers = (
                    H8RegDirOper(er0, tsize, va),
                    )
        else:   
            # mov 
            opers = (
                    H8RegDirOper(er0, tsize, va),
                    H8RegIndirOper(er1, tsize, va, 0, OF_PREDEC),
                    )
    else:
        # mov @ERs+,ERd
        if val & 0xf0 == 0x70:
            # pop
            mnem = 'pop'
            opers = (
                    H8RegDirOper(er0, tsize, va),
                    )
        else:
            # mov
            opers = (
                    H8RegIndirOper(er1, tsize, va, 0, OF_POSTINC),
                    H8RegDirOper(er0, tsize, va),
                    )
    return (op, mnem, opers, iflags, isz)


def p_Mov_78(va, val, buf, off, tsize):
    val2, val3_4 = struct.unpack(">HI", buf[off+2:off+8])

    op = (val3_4 >> 24) | ((val2&0xfff0)<<4) | ((val&0xff80)<<(20+1)) | ((val&0xf)<<20)
    #FIXME: complex and ugly.  do we even need these in this impl?

    mnem = None
    disp = val3_4 & 0xffffff

    # tsize is all over the map.  must determine here.
    tsz_opt = (val2 >> 8) & 1
    tsize = (1, 2)[tsz_opt]

    if (val2 & 8):
        ers = (val>>4) & 0x7
        rd  = val2 & 0xf
        opers = (
                H8RegIndirOper(ers, tsize, va, disp=disp, oflags=0),
                H8RegOper(rd),
                )
    else:
        erd = (val>>4) & 0x7
        rs  = val2 & 0xf
        opers = (
                H8RegOper(rs),
                H8RegIndirOper(erd, tsize, va, disp=disp, oflags=0),
                )

    return (op, mnem, opers, iflags, 2)

mnem_79a = (
        'mov',
        'add',
        'cmp',
        'sub',
        'or',
        'xor',
        'and',
        )

def p_79(va, val, buf, off, tsize):
    op, m, opers, iflags, isz = p_i16_Rd(va, val, buf, off, tsize)
    mnem = mnem_79a[(val>>4)&0xf]
    return op, mnem, opers, iflags, isz

def p_7a(va, val, buf, off, tsize):
    op, m, opers, iflags, isz = p_i32_ERd(va, val, buf, off, tsize)
    mnem = mnem_79a[(val>>4)&0xf]
    return op, mnem, opers, iflags, isz

def p_eepmov(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])
    op = (val<<8) | val2
    tsize = (1,2)[ (val>>7)&1]
    return op, None, (), 0, 4

def p_7c(va, val, buf, off, tsize):
    # btst, bor, bior, bxor, bixor, band, biand, bid, bild (erd)
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op, mnem, flags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80)<<9)

    telltale = (val2>>8) 
    
    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        rn = (val2>>4) & 0xf
        opers = (
                H8RegDirOper(rn, tsize=tsize),
                H8RegIndirOper(erd, tsize, va),
                )

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        erd = (val>>4) & 0x7
        imm = (val2>>4) & 0x7
        opers = (
                H8ImmOper(imm),
                H8RegIndirOper(erd, tsize, va),
                )

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        i3 = (val2>>4) & 0x7
        erd = (val >>4) & 0x7

        opers = (
                H8ImmOper(i3),
                H8RegIndirOper(erd, tsize, va, 0),
                )
    
    return op, mnem, opers, iflags, 4

bit_dble7df = [
        ('bset', 0),
        ('bset', 0),
        ('bnot', 0),
        ('bnot', 0),
        ('bclr', 0),
        ('bclr', 0),
        None, 
        None, 
        None, 
        None,
        None, 
        None, 
        None, 
        None,
        ('bst', 0),
        ('bist', 0),
        ]
bit_dble7df.extend(bit_dble7df)

def p_7d(va, val, buf, off, tsize):
    # bset, bnor, bclr, bst/bist
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2, bit_dble7df)
    op |= ((val & 0xff80)<<9)

    erd = (val>>4) & 0x7
    imm = (val2>>4) & 0x7
    opers = (
            H8ImmOper(imm),
            H8RegIndirOper(erd, tsize, va)
            )

    return op, mnem, opers, iflags, 4

def p_7e(va, val, buf, off, tsize):
    # btst, bor, bior, bxor, bixor, band, biand, bid, bild (erd)
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80)<<9)
    aa = val & 0xff

    telltale = (val2>>8) 
    
    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        rn = (val2>>4) & 0xf
        opers = (
                H8RegDirOper(rn, tsize, va, 0),
                H8AbsAddrOper(aa, tsize=tsize),
                )

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        i3 = (val2>>4) & 0x7
        opers = (
                H8ImmOper(i3, tsize=tsize),
                H8AbsAddrOper(aa, tsize=tsize),
                )

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        i3 = (val2>>4) & 0x7

        opers = (
                H8ImmOper(i3),
                H8AbsAddrOper(aa, tsize=tsize),
                )
    
    return op, mnem, opers, iflags, 4

def p_7f(va, val, buf, off, tsize):
    # bset, bnor, bclr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2, bit_dble7df)
    op |= ((val & 0xff80)<<9)

    erd = (val>>4) & 0x7
    imm = (val2>>4) & 0x7
    opers = (
            H8ImmOper(imm),
            H8RegIndirOper(erd, tsize, va)
            )

    return op, mnem, opers, iflags, 4

