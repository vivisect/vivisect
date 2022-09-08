import envi
import envi.bits as e_bits
import struct

# from disasm import H8ImmOper, H8RegDirOper, H8RegIndirOper, H8AbsAddrOper, H8PcOffsetOper, H8RegMultiOper, H8MemIndirOper

import envi.archs.h8.regs as e_regs
import envi.archs.h8.const as e_const
import envi.archs.h8.operands as h8_operands

bcc = [
        ('bra', envi.IF_NOFALL | envi.IF_BRANCH),
        ('brn', envi.IF_BRANCH | envi.IF_COND),
        ('bhi', envi.IF_BRANCH | envi.IF_COND),
        ('bls', envi.IF_BRANCH | envi.IF_COND),
        ('bcc', envi.IF_BRANCH | envi.IF_COND),
        ('bcs', envi.IF_BRANCH | envi.IF_COND),
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
    op = val >> 4
    rd = val & 0xf
    exr = op & 1
    opers = (
            h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, va),
            h8_operands.H8RegDirOper(rd, tsize, va),
            )
    return (op, None, opers, iflags, 2)


def p_Rs_CCR(va, val, buf, off, tsize):
    # ldc
    iflags = 0
    op = val >> 4
    rs = val & 0xf
    exr = op & 1
    opers = (
            h8_operands.H8RegDirOper(rs, tsize, va),
            h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, va),
            )
    return (op, None, opers, iflags, 2)


def p_aAA8_Rd(va, val, buf, off, tsize):
    # mov 0x2###
    iflags = 0
    op = val >> 12
    Rd = (val >> 8) & 0xf
    aAA8 = val & 0xff

    opers = (
            h8_operands.H8AbsAddrOper(aAA8, tsize, aasize=1),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_Rs_aAA8(va, val, buf, off, tsize):
    # mov 0x3###
    iflags = 0
    op = val >> 12
    Rs = (val >> 8) & 0xf
    aAA8 = val & 0xff

    opers = (
            h8_operands.H8RegDirOper(Rs, tsize, va, 0),
            h8_operands.H8AbsAddrOper(aAA8, tsize, aasize=1),
            )
    return (op, None, opers, iflags, 2)


def p_i2(va, val, buf, off, tsize):
    # trapa
    iflags = 0
    op = 0x57
    i2 = (val >> 4) & 0x3

    opers = (
            h8_operands.H8ImmOper(i2, tsize),
            )
    return (op, None, opers, iflags, 2)


def p_i3_Rd(va, val, buf, off, tsize):
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    iflags = 0
    op = val >> 7
    i3 = (val >> 4) & 0x7
    Rd = val & 0xf

    opers = (
            h8_operands.H8ImmOper(i3, tsize),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_i3_aERd(va, val, buf, off, tsize):
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((((val >> 3) & 0xfff0) | (val & 0xf)) << 13) | ((val2 >> 3) & 0xfff0) | (val & 0xf)
    i3 = (val2 >> 4) & 0x7
    ERd = (val >> 4) & 0x7

    opers = (
            h8_operands.H8ImmOper(i3, tsize),
            h8_operands.H8RegIndirOper(ERd, tsize, va),
            )
    return (op, None, opers, iflags, 4)


def p_i3_aAA8(va, val, buf, off, tsize):
    # band, bclr, biand, bild, bior, bist, bixor, bld, bnot, bor, bset, bst, btst, bxor
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val >> 16) | (val & 0xf) | (val2 >> 15) | (val & 0xf)
    i3 = (val2 >> 4) & 0x7
    aa = val & 0xff

    opers = (
            h8_operands.H8ImmOper(i3, tsize),
            h8_operands.H8AbsAddrOper(aa, tsize, aasize=1),
            )
    return (op, None, opers, iflags, 4)


def p_i8_CCR(va, val, buf, off, tsize, exr=0):
    # andc
    iflags = 0
    op = val >> 8
    i8 = val & 0xff

    opers = (
            h8_operands.H8ImmOper(i8, 1),
            h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, 0),
            )
    return (op, None, opers, iflags, 2)


def p_i8_Rd(va, val, buf, off, tsize):
    # add.b, addx, and.b, cmp.b
    iflags = 0
    op = val >> 4
    i8 = val & 0xff
    Rd = (val >> 8) & 0xf

    opers = (
            h8_operands.H8ImmOper(i8, 1),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
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
            h8_operands.H8ImmOper(i16, 2),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
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
            h8_operands.H8ImmOper(i32, 4),
            h8_operands.H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 6)


def p_Rd(va, val, buf, off, tsize):
    # daa, das, dec.b, exts.w, extu.w, inc.b
    iflags = 0
    op = val >> 4
    Rd = val & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_Rs_Rd(va, val, buf, off, tsize):
    # add.b, add.w, addx, and.b, and.w, cmp.b, cmp.w, divxu.b
    iflags = 0
    op = val >> 16
    Rs = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rs, tsize, va, 0),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_Rs_Rd_mul(va, val, buf, off, tsize):
    iflags = 0
    op = val >> 16
    Rs = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rs, 1, va, 0),
            h8_operands.H8RegDirOper(Rd, 2, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_Rs_Rd_4b(va, val, buf, off, tsize):
    # divxs.b, mulxs.b
    val2, = struct.unpack('>H', buf[off+2: off+4])
    oszbit = (val2 >> 9) & 1
    iflags = (e_const.IF_B, e_const.IF_W)[oszbit]
    stsize, dtsize = ((1, 2), (2, 4))[oszbit]

    op = (val << 8) | (val2 >> 8)
    Rs = (val2 >> 4) & 0xf
    Rd = val2 & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rs, stsize, va, 0),
            h8_operands.H8RegDirOper(Rd, dtsize, va, 0),
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
            h8_operands.H8RegDirOper(Rs, tsize, va, 0),
            h8_operands.H8RegDirOper(ERd, 4, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_ERs_ERd(va, val, buf, off, tsize):
    # add.l, cmp.l
    iflags = e_const.IF_L
    op = ((val >> 6) & 0xfffe) | ((val >> 3) & 1)  # first byte, and bits 3 and 7 of second byte
    ERs = (val >> 4) & 0x7
    ERd = val & 0x7

    opers = (
            h8_operands.H8RegDirOper(ERs, tsize, va, 0),
            h8_operands.H8RegDirOper(ERd, tsize, va, 0),
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
            h8_operands.H8RegDirOper(Rs, tsize, va, 0),
            h8_operands.H8RegDirOper(ERd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 4)


def p_ERd(va, val, buf, off, tsize):
    # exts.l, extu.l
    iflags = 0
    op = val >> 4
    ERd = val & 0x7

    opers = (h8_operands.H8RegDirOper(ERd, tsize, va, 0),)
    return (op, None, opers, iflags, 2)


def p_Rn_Rd(va, val, buf, off, tsize):
    # bclr, bset, btst
    iflags = 0
    op = val >> 8
    Rn = (val >> 4) & 0xf
    Rd = val & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rn, tsize, va, 0),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_68_69_6e_6f(va, val, buf, off, tsize):
    # mov 0x68, 0x69, 0x6e, 0x6f
    iflags = 0
    op = (val >> 7)
    aERs = (val >> 4) & 0x7
    Rd = (val) & 0xf

    if (val & 0x600):
        disp, = struct.unpack('>H', buf[off+2: off+4])
        dispsz = 2
        isz = 4
    else:
        disp, dispsz = 0, 0
        isz = 2

    if val & 0x80:  # reverse operand order
        opers = (
                h8_operands.H8RegDirOper(Rd, tsize, va, 0),
                h8_operands.H8RegIndirOper(aERs, tsize, va, disp=disp, dispsz=dispsz, oflags=0),
                )
    else:
        opers = (
                h8_operands.H8RegIndirOper(aERs, tsize, va, disp=disp, dispsz=dispsz, oflags=0),
                h8_operands.H8RegDirOper(Rd, tsize, va, 0),
                )
    return (op, None, opers, iflags, isz)


def p_Rn_aERd(va, val, buf, off, tsize):
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = ((val >> 12) & 0xfff0) | (val & 0xf) | ((val2 >> 4) & 0xfff0) | (val2 & 0xf)
    aERd = (val >> 4) & 0x7
    Rn = (val2 >> 4) & 0xf

    opers = (
            h8_operands.H8RegDirOper(Rn, tsize, va, 0),
            h8_operands.H8RegIndirOper(aERd, tsize, va, disp=0, oflags=0),
            )
    return (op, None, opers, iflags, 4)


def p_Rn_aAA8(va, val, buf, off, tsize):
    # bclr, bset, btst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = (val & 0xff00) | ((val2 >> 4) & 0xff0) | (val2 & 0xf)
    Rn = (val2 >> 4) & 0xf
    aAA8 = val & 0xff

    opers = (
            h8_operands.H8RegDirOper(Rn, tsize, va, 0),
            h8_operands.H8AbsAddrOper(aAA8, tsize, aasize=1),
            )
    return (op, None, opers, iflags, 4)


def p_aERn(va, val, buf, off, tsize):
    # jmp, jsr
    iflags = 0
    op = ((val >> 3) & 0xfff0) | (val & 0xf)
    aERn = (val >> 4) & 0x7

    opers = (
            h8_operands.H8RegIndirOper(aERn, tsize, va, 0),
            )
    return (op, None, opers, iflags, 2)


def p_aAA24(va, val, buf, off, tsize):
    # jmp, jsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 8
    aAA24 = ((val & 0xf) << 16) | val2

    opers = (
            h8_operands.H8AbsAddrOper(aAA24, tsize, aasize=3),
            )
    return (op, None, opers, iflags, 4)


def p_aaAA8(va, val, buf, off, tsize):
    # jmp, jsr
    iflags = 0
    op = val >> 8
    aaAA8 = val & 0xff

    opers = (
            h8_operands.H8MemIndirOper(aaAA8),
            )
    return (op, None, opers, iflags, 2)


def p_disp8(va, val, buf, off, tsize):
    # bcc, bsr
    iflags = 0
    op = val >> 8
    disp8 = e_bits.signed(val & 0xfe, 1)

    opers = (
            h8_operands.H8PcOffsetOper(disp8, va, 1),
            )
    return (op, None, opers, iflags, 2)


def p_disp16(va, val, buf, off, tsize):
    # bcc, bsr
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val
    disp16 = e_bits.signed(val2 & 0xfffffe, 2)

    mnem = None
    if (op & 0xf00 == 0x800):
        opnibble = (val >> 4) & 0xf
        mnem, iflags = bcc[opnibble]

    opers = (
            h8_operands.H8PcOffsetOper(disp16, va, 2),
            )
    return (op, mnem, opers, iflags, 4)


def p_Rs_aAA16(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA16 = val2

    opers = (
            h8_operands.H8RegDirOper(Rs, tsize, va),
            h8_operands.H8AbsAddrOper(aAA16, tsize, aasize=2),
            )
    return (op, None, opers, iflags, 4)


def p_Rs_aAA24(va, val, buf, off, tsize):
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rs = val & 0xf
    aAA24 = val2 & 0xffffff

    opers = (
            h8_operands.H8RegDirOper(Rs, tsize, va),
            h8_operands.H8AbsAddrOper(aAA24, tsize, aasize=4),
            )
    return (op, None, opers, iflags, 6)


def p_aAA16_Rd(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA16 = val2

    opers = (
            h8_operands.H8AbsAddrOper(aAA16, tsize, aasize=2),
            h8_operands.H8RegDirOper(Rd, tsize, va),
            )
    return (op, None, opers, iflags, 4)


def p_aAA24_Rd(va, val, buf, off, tsize):
    val2, = struct.unpack('>I', buf[off+2: off+6])

    iflags = 0
    op = val >> 4
    Rd = val & 0xf
    aAA24 = val2 & 0xffffff

    opers = (
            h8_operands.H8AbsAddrOper(aAA24, tsize, aasize=4),
            h8_operands.H8RegDirOper(Rd, tsize, va),
            )
    return (op, None, opers, iflags, 6)


def p_nooperands(va, val, buf, off, tsize):
    # eepmov.b, eepmov.w,
    iflags = 0
    op = val

    opers = tuple()
    return (op, None, opers, iflags, 2)


# 60-67, 70-77, 7d, 7f, 7c, 7e  (converge?)
bit_dbles = [
        ('bset', 0),
        ('bset', 0),
        ('bnot', 0),
        ('bnot', 0),
        ('bclr', 0),
        ('bclr', 0),
        ('btst', 0),
        ('bist', 0),
        ('bor', 0),
        ('bior', 0),
        ('bxor', 0),
        ('bixor', 0),
        ('band', 0),
        ('biand', 0),
        ('bst', 0),
        ('bist', 0),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        ]
bit_dbles.extend(bit_dbles)
bit_dbles[0x2e] = ('bld', 0)
bit_dbles[0x2f] = ('bild', 0)


def getBitDbl_OpMnem(val, bitlist=bit_dbles):
    op = val >> 7
    mnem, flags = bitlist[(op & 0x3f)]
    return op, mnem, flags


def p_Bit_Doubles(va, val, buf, off, tsize):
    op, mnem, iflags = getBitDbl_OpMnem(val)

    i3 = (val >> 4) & 0x7
    Rd = val & 0xf

    opers = (
            h8_operands.H8ImmOper(i3, tsize),
            h8_operands.H8RegDirOper(Rd, tsize, va, 0),
            )
    return (op, mnem, opers, iflags, 2)


def p_01(va, val, buf, off, tsize):
    mnem = None
    iflags = 0
    opers = None

    diff = (val >> 4) & 0xf

    if diff == 8:
        # sleep
        op = 0x0180
        mnem = 'sleep'
        opers = tuple()
        return op, mnem, opers, iflags, 2

    val2, = struct.unpack('>H', buf[off+2: off+4])
    isz = 4
    op = (val << 9) | (val2 >> 7)
    if diff == 0:
        mnem = 'mov'

        # all 0100#### opcodes share these:
        tsize = 4
        iflags |= e_const.IF_L

        d2 = val2 >> 8

        # mov   0100##... where ## is basically another mov encoding with different register sizes
        if d2 == 0x69:
            erd = (val2 >> 4) & 7
            ers = val2 & 7
            if val2 & 0x80:
                opers = (
                        h8_operands.H8RegDirOper(ers, tsize, va),
                        h8_operands.H8RegIndirOper(erd, tsize, va),
                        )
            else:
                opers = (
                        h8_operands.H8RegIndirOper(erd, tsize, va),
                        h8_operands.H8RegDirOper(ers, tsize, va),
                        )

        elif d2 == 0x6b:
            if val2 & 0x20:
                isz = 8
                val3, = struct.unpack('>I', buf[off+4:off+8])
                if val2 & 0x80:
                    # a
                    erd = val2 & 7
                    aa = val3 & 0xffffffff
                    opers = (
                            h8_operands.H8RegDirOper(erd, tsize, va),
                            h8_operands.H8AbsAddrOper(aa, tsize, aasize=4),
                            )
                else:
                    # 2
                    ers = val2 & 7
                    aa = val3 & 0xffffffff
                    opers = (
                            h8_operands.H8AbsAddrOper(aa, tsize, aasize=4),
                            h8_operands.H8RegDirOper(ers, tsize, va),
                            )
            else:
                val3, = struct.unpack('>H', buf[off+4:off+6])
                isz = 6
                if val2 & 0x80:
                    # 8
                    erd = val2 & 7
                    aa = val3 & 0xffff
                    opers = (
                            h8_operands.H8RegDirOper(erd, tsize, va),
                            h8_operands.H8AbsAddrOper(aa, tsize, aasize=2),
                            )
                else:
                    # 0
                    ers = val2 & 7
                    aa = val3 & 0xffff
                    opers = (
                            h8_operands.H8AbsAddrOper(aa, tsize, aasize=2),
                            h8_operands.H8RegDirOper(ers, tsize, va),
                            )

        elif d2 == 0x6d:    # TODO: test me!!
            newop, mnem, opers, iflags, nisz = p_6c_6d_0100(va, val2, buf, off+2, 4)
            isz = nisz + 2
            op = newop | (0x01000000)

        elif d2 == 0x6f:
            disp, = struct.unpack('>H', buf[off+4:off+6])
            isz = 6
            er0 = val2 & 7
            er1 = (val2 >> 4) & 7
            if val2 & 0x80:
                # mov.l ERs, @(d:16,ERd)
                opers = (
                        h8_operands.H8RegDirOper(er0, tsize, va),
                        h8_operands.H8RegIndirOper(er1, tsize, va, disp, dispsz=2),
                        )
            else:
                # mov.l @(d:16,ERs), ERd
                opers = (
                        h8_operands.H8RegIndirOper(er1, tsize, va, disp, dispsz=2),
                        h8_operands.H8RegDirOper(er0, tsize, va),
                        )

        elif d2 == 0x78:
            isz = 10
            val3, disp = struct.unpack('>HI', buf[off + 4:off + 10])
            if val3 & 0xff20 != 0x6b20:
                raise envi.InvalidInstruction(bytez=buf[off:off + 16], va=va)

            er0 = val3 & 7
            er1 = (val2 >> 4) & 7
            if (val3 & 0x80):
                # mov.l ERs, @(d:24,ERd)
                opers = (
                        h8_operands.H8RegDirOper(er0, tsize, va),
                        h8_operands.H8RegIndirOper(er1, tsize, va, disp, dispsz=4),
                        )

            else:
                # mov.l @(d:24,ERs), ERd
                opers = (
                        h8_operands.H8RegIndirOper(er1, tsize, va, disp, dispsz=4),
                        h8_operands.H8RegDirOper(er0, tsize, va),
                        )

    elif diff in (1, 2, 3):
        # ldm/stm (ERn-ERn+diff), @-SP
        iflags = e_const.IF_L

        tsize = 4
        optest = val2 & 0xfff8
        rn = val2 & 0x7

        rcount = diff + 1
        if optest == 0x6df0:
            mnem = 'stm'
            opers = (
                    h8_operands.H8RegMultiOper(rn, rcount),
                    h8_operands.H8RegIndirOper(e_const.REG_SP, tsize, va, 0, oflags=e_const.OF_PREDEC),
                    )

        elif optest == 0x6d70:
            mnem = 'ldm'
            opers = (
                    h8_operands.H8RegIndirOper(e_const.REG_SP, tsize, va, 0, oflags=e_const.OF_POSTINC),
                    h8_operands.H8RegMultiOper(rn-diff, rcount),
                    )

        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 4:
        # ldc/stc - anything that touches ccr or exr
        # we'll build it for ldc, and reverse it if it's stc
        d2 = val2 >> 8
        isStc = (val2 >> 7) & 1
        oflags = 0
        tsize = 2

        exr = val & 0x1

        if d2 == 6:
            op, nmnem, opers, iflags, nisz = p_i8_CCR(va, val2, buf, off, tsize, exr)
            return op, 'andc', opers, iflags, isz

        elif d2 == 5:
            op, nmnem, opers, iflags, nisz = p_i8_CCR(va, val2, buf, off, tsize, exr)
            return op, 'xorc', opers, iflags, isz

        else:
            iflags = e_const.IF_W
            tsize = 2

            if d2 == 0x04:              # xx:8, EXR
                op, nmnem, opers, iflags, nisz = p_i8_CCR(va, val2, buf, off, tsize, exr)
                return op, 'orc', opers, iflags, isz

            elif d2 == 0x07:              # xx:8, EXR
                op, nmnem, opers, niflags, nisz = p_i8_CCR(va, val2, buf, off, tsize, exr)
                iflags = e_const.IF_B
                return op, 'ldc', opers, iflags, isz

            elif d2 in (0x69, 0x6d):    # @ERs,CCR / @ERs+,CCR
                if d2 == 0x6d:
                    oflags = e_const.OF_POSTINC
                ers = (val2 >> 4) & 0x7
                opers = (
                        h8_operands.H8RegIndirOper(ers, tsize, va, oflags=oflags),
                        h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, va)
                        )

            elif d2 in (0x6f, 0x78):  # @(d:16,ERs),CCR / @(d:24,ERs)
                if d2 == 0x78:
                    val3, disp = struct.unpack('>HI', buf[off+4:off+10])
                    isStc = (val3 >> 7) & 1
                    isz = 10
                    dispsz = 4
                else:
                    disp, = struct.unpack('>H', buf[off+4:off+6])
                    isz = 6
                    dispsz = 2
                ers = (val2 >> 4) & 0x7
                opers = (
                        h8_operands.H8RegIndirOper(ers, tsize, va, disp, dispsz),
                        h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, va)
                        )

            elif d2 == 0x6b:    # @aa:16,CCR / @aa:24,CCR
                if val2 & 0x20:
                    aa, = struct.unpack('>I', buf[off+4:off+8])
                    isz = 8
                    aasize = 4
                else:
                    aa, = struct.unpack('>H', buf[off+4:off+6])
                    isz = 6
                    aasize = 2
                isStc = (val2 >> 7) & 1
                opers = (
                        h8_operands.H8AbsAddrOper(aa, tsize, aasize),
                        h8_operands.H8RegDirOper(e_regs.REG_CCR + exr, 4, va)
                        )

            # after all the decisions...
            mnem = ('ldc', 'stc')[isStc]
            if isStc:
                opers = opers[::-1]

    elif diff == 0xc:
        if val2 & 0xfd00 == 0x5000:
            # mulxs
            mnem = 'mulxs'
            op, nmnem, opers, iflags, nisz = p_Rs_Rd_4b(va, val, buf, off, tsize=1)
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 0xd:
        if val2 & 0xfd00 == 0x5100:
            mnem = 'divxs'
            # divxs
            op, nmnem, opers, iflags, nisz = p_Rs_Rd_4b(va, val, buf, off, tsize)
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 0xe:
        if val2 & 0xff00 == 0x7b00:
            mnem = 'tas'        # FIXME: check out what this decodes to
            tsize = 1
            erd = (val2 >> 4) & 7
            opers = (h8_operands.H8RegIndirOper(erd, tsize, va, oflags=0),)

        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    elif diff == 0xf:
        if val2 & 0xfc00 == 0x6400:
            # or/xor/and
            nop, nmnem, opers, iflags, nisz = p_ERs_ERd(va, val2, buf, off, tsize=4)
            op = (val << 8) | (val2 >> 8)
            mnembits = (val2 >> 8) & 3
            mnem = ('or', 'xor', 'and')[mnembits]
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return (op, mnem, opers, iflags, isz)


def p_0a_1a(va, val, buf, off, tsize):

    diff = (val >> 12)
    if val & 0xf0 == 0:
        mnem = ('inc', 'dec')[diff]
        op, nmnem, opers, iflags, isz = p_Rd(va, val, buf, off, tsize=1)
        iflags = e_const.IF_B

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
        (2, e_const.IF_W, 1, 'inc'),
        None,
        (4, e_const.IF_L, 1, 'inc'),
        (4, 0, 2, 'adds'),
        (4, 0, 4, 'adds'),
        None,
        None,
        None,
        (2, e_const.IF_W, 2, 'inc'),
        None,
        (4, e_const.IF_L, 2, 'inc'),
        )

data_1b = (
        (4, 0, 1, 'subs'),
        None,
        None,
        None,
        None,
        (2, e_const.IF_W, 1, 'dec'),
        None,
        (4, e_const.IF_L, 1, 'dec'),
        (4, 0, 2, 'subs'),
        (4, 0, 4, 'subs'),
        None,
        None,
        None,
        (2, e_const.IF_W, 2, 'dec'),
        None,
        (4, e_const.IF_L, 2, 'dec'),
        )


def p_0b_1b(va, val, buf, off, tsize):
    table = (data_0b, data_1b)[val >> 12]
    diff = (val >> 4) & 0xf
    tsize, iflags, imm, mnem = table[diff]

    op = val >> 4
    ERd = val & 0xf

    opers = (
            h8_operands.H8ImmOper(imm, tsize),
            h8_operands.H8RegDirOper(ERd, tsize, va, 0),
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
        opers = (h8_operands. H8RegDirOper(rd, 1, va=va, oflags=0),)
    elif diff >= 0x80:
        mnem = ('mov', 'cmp')[aors]
        op, nmnem, opers, iflags, isz = p_ERs_ERd(va, val, buf, off, tsize=4)
    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return (op, mnem, opers, iflags, 2)


shift_info = []
for name in ('shll', 'shal', 'shlr', 'shar', 'rotxl', 'rotl', 'rotxr', 'rotr'):
    shift_info.append((name, 1, 0))
    shift_info.append((name, 2, 0))
    shift_info.append(None)
    shift_info.append((name, 4, 0))
    shift_info.append((name, 1, 2))
    shift_info.append((name, 2, 2))
    shift_info.append(None)
    shift_info.append((name, 4, 2))

for nothing in range(0x14, 0x17):
    for xnothing in range(16):
        shift_info.append(None)

for name1, name2 in (('not', 'extu'), ('neg', 'exts')):
    shift_info.append((name1, 1, 0))
    shift_info.append((name1, 2, 0))
    shift_info.append(None)
    shift_info.append((name1, 4, 0))
    shift_info.append(None)
    shift_info.append((name2, 2, 0))
    shift_info.append(None)
    shift_info.append((name2, 4, 0))


def p_shift_10_11_12_13_17(va, val, buf, off, tsize):
    op = val >> 4

    mnem, osz, xtra = shift_info[(val >> 4) & 0xff]
    iflags = e_const.OSZ_FLAGS[osz]

    # if 32bit (ERd), top bit should always be 0 anyway
    rd = val & 0xf
    if xtra:
        opers = (
                h8_operands.H8ImmOper(xtra, osz),
                h8_operands.H8RegDirOper(rd, osz, va, 0),
                )
    else:
        opers = (h8_operands.H8RegDirOper(rd, osz, va, 0),)

    return (op, mnem, opers, iflags, 2)


def p_6A_6B(va, val, buf, off, tsize):
    op = val >> 4
    diff = op & 0xf
    osz = 1 + ((val >> 8) & 1)

    if op & 0x8:
        # Rs, @aa:16/24
        if diff == 0xa:
            op, mnem, opers, iflags, isz = p_Rs_aAA24(va, val, buf, off, tsize)
            iflags |= e_const.OSZ_FLAGS[osz]
            return op, mnem, opers, iflags, isz
        elif diff == 0x8:
            op, mnem, opers, iflags, isz = p_Rs_aAA16(va, val, buf, off, tsize)
            iflags |= e_const.OSZ_FLAGS[osz]
            return op, mnem, opers, iflags, isz
        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    else:
        # @aa:16/24, Rd
        if diff == 0x2:
            op, mnem, opers, iflags, isz = p_aAA24_Rd(va, val, buf, off, tsize)
            iflags |= e_const.OSZ_FLAGS[osz]
            return op, mnem, opers, iflags, isz

        elif diff == 0x0:
            op, mnem, opers, iflags, isz = p_aAA16_Rd(va, val, buf, off, tsize)
            iflags |= e_const.OSZ_FLAGS[osz]
            return op, mnem, opers, iflags, isz

        elif val in (0x6a10, 0x6a18, 0x6a30, 0x6a38):
            # non-MOV instructions
            isz, aasize, fmt = (None, (6, 2, '>HH'), None, (8, 4, '>IH'))[(val >> 4) & 3]

            aa, val2 = struct.unpack(fmt, buf[off+2:off+isz])
            op, mnem, niflags = getBitDbl_OpMnem(val2)

            if val2 & 0x1c00:
                i3 = (val2 >> 4) & 7
                opers = (
                        h8_operands.H8ImmOper(i3, tsize),
                        h8_operands.H8AbsAddrOper(aa, tsize, aasize),
                        )
            else:
                rn = (val2 >> 4) & 0xf
                opers = (
                        h8_operands.H8RegDirOper(rn, tsize, va, ),
                        h8_operands.H8AbsAddrOper(aa, tsize, aasize),
                        )
            return op, mnem, opers, 0, isz

        else:
            raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)


def p_6c_6d_0100(va, val, buf, off, tsize):
    op = val >> 7
    iflags = e_const.OSZ_FLAGS[tsize]
    isz = 2
    mnem = None

    er0 = val & 0xf
    er1 = (val >> 4) & 7

    if val & 0x80:
        # mov ERs, @-ERd
        if val & 0xf0 == 0xf0:
            # push
            mnem = 'push'
            opers = (h8_operands.H8RegDirOper(er0, tsize, va),)
        else:
            # mov
            mnem = 'mov'
            opers = (
                    h8_operands.H8RegDirOper(er0, tsize, va),
                    h8_operands.H8RegIndirOper(er1, tsize, va, 0, oflags=e_const.OF_PREDEC),
                    )
    else:
        # mov @ERs+,ERd
        if val & 0xf0 == 0x70:
            # pop
            mnem = 'pop'
            opers = (h8_operands.H8RegDirOper(er0, tsize, va),)
        else:
            # mov
            mnem = 'mov'
            opers = (
                    h8_operands.H8RegIndirOper(er1, tsize, va, 0, oflags=e_const.OF_POSTINC),
                    h8_operands.H8RegDirOper(er0, tsize, va),
                    )
    return (op, mnem, opers, iflags, isz)


def p_Mov_78(va, val, buf, off, tsize):
    val2, val3_4 = struct.unpack('>HI', buf[off+2:off+8])

    op = (val3_4 >> 24) | ((val2 & 0xfff0) << 4) | ((val & 0xff80) << (20 + 1)) | ((val & 0xf) << 20)
    # FIXME: complex and ugly.  do we even need these in this impl?

    mnem = None
    disp = val3_4 & 0xffffffff

    # tsize is all over the map.  must determine here.
    tsz_opt = (val2 >> 8) & 1
    tsize = (1, 2)[tsz_opt]

    iflags = e_const.OSZ_FLAGS[tsize]

    if (val2 & 0x80):
        erd = (val >> 4) & 0x7
        rs = val2 & 0xf
        opers = (
                h8_operands.H8RegDirOper(rs, tsize),
                h8_operands.H8RegIndirOper(erd, tsize, va, disp=disp, dispsz=4, oflags=0),
                )
    else:
        ers = (val >> 4) & 0x7
        rd = val2 & 0xf
        opers = (
                h8_operands.H8RegIndirOper(ers, tsize, va, disp=disp, dispsz=4, oflags=0),
                h8_operands.H8RegDirOper(rd, tsize),
                )

    return (op, mnem, opers, iflags, 8)


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
    mnem = mnem_79a[(val >> 4) & 0xf]
    return op, mnem, opers, iflags, isz


def p_7a(va, val, buf, off, tsize):
    op, m, opers, iflags, isz = p_i32_ERd(va, val, buf, off, tsize)
    mnem = mnem_79a[(val >> 4) & 0xf]
    return op, mnem, opers, iflags, isz


def p_eepmov(va, val, buf, off, tsize):
    val2, = struct.unpack('>H', buf[off+2: off+4])
    op = (val << 8) | val2
    # tsize = (1, 2)[(val >> 7) & 1]
    diff = val & 0xff
    if diff == 0x5c:
        iflags = e_const.IF_B
    elif diff == 0xd4:
        iflags = e_const.IF_W
    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return op, None, (), iflags, 4


def p_7c(va, val, buf, off, tsize):
    # btst, bor, bior, bxor, bixor, band, biand, bid, bild (erd)
    val2, = struct.unpack('>H', buf[off+2: off+4])
    iflags = 0
    op, mnem, flags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80) << 9)

    telltale = (val2 >> 8)

    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        erd = (val >> 4) & 0x7
        rn = (val2 >> 4) & 0xf
        opers = (
                h8_operands.H8RegDirOper(rn, tsize=tsize),
                h8_operands.H8RegIndirOper(erd, tsize, va),
                )

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        erd = (val >> 4) & 0x7
        imm = (val2 >> 4) & 0x7
        opers = (
                h8_operands.H8ImmOper(imm, tsize),
                h8_operands.H8RegIndirOper(erd, tsize, va),
                )

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        i3 = (val2 >> 4) & 0x7
        erd = (val >> 4) & 0x7

        opers = (
                h8_operands.H8ImmOper(i3, tsize),
                h8_operands.H8RegIndirOper(erd, tsize, va),
                )

    return op, mnem, opers, iflags, 4


def p_7d(va, val, buf, off, tsize):
    # bset, bnor, bclr, bst/bist
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80) << 9)

    erd = (val >> 4) & 0x7
    immreg = (val2 >> 4) & 0x7

    if val2 & 0x1c00:
        opers = (
                h8_operands.H8ImmOper(immreg, tsize),
                h8_operands.H8RegIndirOper(erd, tsize, va),
                )
    else:
        opers = (
                h8_operands.H8RegDirOper(immreg, tsize, va),
                h8_operands.H8RegIndirOper(erd, tsize, va),
                )
    return op, mnem, opers, iflags, 4


def p_7e(va, val, buf, off, tsize):
    # btst, bor, bior, bxor, bixor, band, biand, bid, bild (erd)
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff80) << 9)
    aa = val & 0xff

    telltale = (val2 >> 8)

    # FIXME: is any of this redundant with previous encodings?
    if telltale == 0x63:
        # btst (0x####63##
        mnem = 'btst'
        rn = (val2 >> 4) & 0xf
        opers = (
                h8_operands.H8RegDirOper(rn, tsize, va, 0),
                h8_operands.H8AbsAddrOper(aa, tsize=tsize, aasize=1),
                )

    elif telltale == 0x73:
        # btst (0x####73##
        mnem = 'btst'
        i3 = (val2 >> 4) & 0x7
        opers = (
                h8_operands.H8ImmOper(i3, tsize),
                h8_operands.H8AbsAddrOper(aa, tsize=tsize, aasize=1),
                )

    elif 0x78 > telltale > 0x73:
        # other bit-halves:
        tsize = 1
        i3 = (val2 >> 4) & 0x7

        opers = (
                h8_operands.H8ImmOper(i3, tsize),
                h8_operands.H8AbsAddrOper(aa, tsize=tsize, aasize=1),
                )
    else:
        raise envi.InvalidInstruction(bytez=buf[off:off+16], va=va)

    return op, mnem, opers, iflags, 4


def p_7f(va, val, buf, off, tsize):
    # bset, bnor, bclr, bist, bst
    val2, = struct.unpack('>H', buf[off+2: off+4])

    op, mnem, iflags = getBitDbl_OpMnem(val2)
    op |= ((val & 0xff00) << 8)

    aa = val & 0xff
    immreg = (val2 >> 4) & 0x7

    if val2 & 0x1c00:
        opers = (
                h8_operands.H8ImmOper(immreg, tsize),
                h8_operands.H8AbsAddrOper(aa, tsize, 1),
                )
    else:
        opers = (
                h8_operands.H8RegDirOper(immreg, tsize, va),
                h8_operands.H8AbsAddrOper(aa, tsize, 1),
                )

    return op, mnem, opers, iflags, 4


'''
8DII    add.b immediate             2 states
08SD    add.b regdir                2 states

791DIIII    add.w imm               4 states
09SD    add.w regdir                2 states

7a1EIIII    add.l imm               6 states
0aSD        add.l regdir            2 states

0b0D    adds #1, ERd                2 states
0b8D    adds #2, ERd                2 states
0b9D    adds #4, ERd                2 states

9DII    addx #xx:8, Rd              2 states
0eSD    addx Rs, Rd                 2 states

eDII    and.b #xx:8, Rd             2 states
16SD    and.b Rs, Rd                2 states

796DIIII    and.w #xx:16, Rd        4 states
66SD        and.w Rs, Rd            2 states

7a6DIIIIIIII    and.l #xx:32, ERd   6 states
01f066SD        and.l Rs, ERd       4 states

06II    andc #xx:8, CCR             2 states

76ID    band #xx:3, Rd              2 states
7cD076I0    band #xx:3, @ERd        6 states
7eAb76I0    band #xx:3, @aa:8       6 states

4CDS    bcc d:8             4 states
58C0DISP    bcc d:16        6 states
'''
# table: ( subtable, mnem, decoder, tsize, iflags)
main_table = [(None, 'DECODE_ERROR', 0, 0, 0) for x in range(256)]
main_table[0x0] = (False, 'nop', None, 0, 0)
main_table[0x1] = (False, None, p_01, 0, 0)
main_table[0xa] = (False, None, p_0a_1a, 0, 0)
main_table[0xb] = (False, None, p_0b_1b, 0, 0)
main_table[0xf] = (False, None, p_0f_1f, 0, 0)
main_table[0x10] = (False, None, p_shift_10_11_12_13_17, 0, 0)
main_table[0x11] = (False, None, p_shift_10_11_12_13_17, 0, 0)
main_table[0x12] = (False, None, p_shift_10_11_12_13_17, 0, 0)
main_table[0x13] = (False, None, p_shift_10_11_12_13_17, 0, 0)
main_table[0x17] = (False, None, p_shift_10_11_12_13_17, 0, 0)
main_table[0x1a] = (False, None, p_0a_1a, 0, 0)
main_table[0x1b] = (False, None, p_0b_1b, 0, 0)
main_table[0x1f] = (False, None, p_0f_1f, 0, 0)

main_table[0x02] = (False, 'stc', p_CCR_Rd, 1, e_const.IF_B)
main_table[0x03] = (False, 'ldc', p_Rs_CCR, 1, e_const.IF_B)
main_table[0x04] = (False, 'orc', p_i8_CCR, 1, 0)
main_table[0x05] = (False, 'xorc', p_i8_CCR, 1, 0)
main_table[0x06] = (False, 'andc', p_i8_CCR, 1, 0)
main_table[0x07] = (False, 'ldc', p_i8_CCR, 1, e_const.IF_B)
main_table[0x08] = (False, 'add', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x09] = (False, 'add', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x0c] = (False, 'mov', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x0d] = (False, 'mov', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x0e] = (False, 'addx', p_Rs_Rd, 1, 0)

main_table[0x14] = (False, 'or', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x15] = (False, 'xor', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x16] = (False, 'and', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x18] = (False, 'sub', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x19] = (False, 'sub', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x1c] = (False, 'cmp', p_Rs_Rd, 1, e_const.IF_B)
main_table[0x1d] = (False, 'cmp', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x1e] = (False, 'subx', p_Rs_Rd, 1, 0)

# mov.b set
for opbyte in range(0x20, 0x30):
    main_table[opbyte] = (False, 'mov', p_aAA8_Rd, 1, e_const.IF_B)

for opbyte in range(0x30, 0x40):
    main_table[opbyte] = (False, 'mov', p_Rs_aAA8, 1, e_const.IF_B)

# generate Bcc opcodes
for opbyte in range(16):
    mnem, iflags = bcc[opbyte]
    main_table[0x40 + opbyte] = (False, mnem, p_disp8, 1, iflags)

main_table[0x50] = (False, 'mulxu', p_Rs_Rd_mul, 1, e_const.IF_B)
main_table[0x51] = (False, 'divxu', p_Rs_Rd_mul, 1, e_const.IF_B)
main_table[0x52] = (False, 'mulxu', p_Rs_ERd, 2, e_const.IF_W)
main_table[0x53] = (False, 'divxu', p_Rs_ERd, 2, e_const.IF_W)

main_table[0x54] = (False, 'rts', None, 0, envi.IF_RET | envi.IF_NOFALL)   # 5470
main_table[0x55] = (False, 'bsr', p_disp8, 0, envi.IF_CALL)
main_table[0x56] = (False, 'rte', None, 0, envi.IF_RET | envi.IF_NOFALL)   # 5670
main_table[0x57] = (False, 'trapa', p_i2, 0, envi.IF_NOFALL)
main_table[0x58] = (False, 'error', p_disp16, 2, 0)
main_table[0x59] = (False, 'jmp', p_aERn,  3, envi.IF_BRANCH | envi.IF_NOFALL)
main_table[0x5a] = (False, 'jmp', p_aAA24, 0, envi.IF_BRANCH | envi.IF_NOFALL)
main_table[0x5b] = (False, 'jmp', p_aaAA8, 0, envi.IF_BRANCH | envi.IF_NOFALL)
main_table[0x5c] = (False, 'bsr', p_disp16, 0, envi.IF_CALL)
main_table[0x5d] = (False, 'jsr', p_aERn, 3, envi.IF_CALL)
main_table[0x5e] = (False, 'jsr', p_aAA24, 0, envi.IF_CALL)
main_table[0x5f] = (False, 'jsr', p_aaAA8, 0, envi.IF_CALL)

# all bit instructions are B. may set 0->1
main_table[0x60] = (False, 'bset', p_Rn_Rd, 1, 0)
main_table[0x70] = (False, 'bset', p_i3_Rd, 1, 0)
main_table[0x61] = (False, 'bnot', p_Rn_Rd, 1, 0)
main_table[0x71] = (False, 'bnot', p_i3_Rd, 1, 0)
main_table[0x62] = (False, 'bclr', p_Rn_Rd, 1, 0)
main_table[0x72] = (False, 'bclr', p_i3_Rd, 1, 0)
main_table[0x63] = (False, 'btst', p_Rn_Rd, 1, 0)
main_table[0x73] = (False, 'btst', p_i3_Rd, 1, 0)

main_table[0x64] = (False, 'or', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x65] = (False, 'xor', p_Rs_Rd, 2, e_const.IF_W)
main_table[0x66] = (False, 'and', p_Rs_Rd, 2, e_const.IF_W)

main_table[0x67] = (False, 'bitdoubles', p_Bit_Doubles, 1, 0)

main_table[0x68] = (False, 'mov', p_68_69_6e_6f, 1, e_const.IF_B)
main_table[0x69] = (False, 'mov', p_68_69_6e_6f, 2, e_const.IF_W)
main_table[0x6a] = (False, 'mov', p_6A_6B, 1, 0)
main_table[0x6b] = (False, 'mov', p_6A_6B, 2, e_const.IF_W)
# main_table[0x6c] = (False, 'mov', p_Mov_6C, 1, IF_B)
# main_table[0x6d] = (False, 'mov', p_Mov_6C, 2, IF_W)
main_table[0x6c] = (False, 'mov', p_6c_6d_0100, 1, e_const.IF_B)
main_table[0x6d] = (False, 'mov', p_6c_6d_0100, 2, e_const.IF_W)
main_table[0x6e] = (False, 'mov', p_68_69_6e_6f, 1, e_const.IF_B)
main_table[0x6f] = (False, 'mov', p_68_69_6e_6f, 2, e_const.IF_W)

for opbyte in range(0x74, 0x78):
    main_table[opbyte] = (False, 'bitdoubles', p_Bit_Doubles, 1, 0)

main_table[0x78] = (False, 'mov', p_Mov_78, 1, 0)
main_table[0x79] = (False, 'p79', p_79, 2, e_const.IF_W)
main_table[0x7a] = (False, 'p7a', p_7a, 4, e_const.IF_L)
main_table[0x7b] = (False, 'eepmov', p_eepmov, 0, 0)
main_table[0x7c] = (False, '7Cmnem', p_7c, 1, 0)
main_table[0x7d] = (False, '7Dmnem', p_7d, 1, 0)
main_table[0x7e] = (False, '7Emnem', p_7e, 1, 0)
main_table[0x7f] = (False, '7Fmnem', p_7f, 1, 0)


for opbyte in range(0x80, 0x90):
    main_table[opbyte] = (False, 'add', p_i8_Rd, 1, e_const.IF_B)

for opbyte in range(0x90, 0xa0):
    main_table[opbyte] = (False, 'addx', p_i8_Rd, 1, 0)

for opbyte in range(0xa0, 0xb0):
    main_table[opbyte] = (False, 'cmp', p_i8_Rd, 1, e_const.IF_B)

for opbyte in range(0xb0, 0xc0):
    main_table[opbyte] = (False, 'subx', p_i8_Rd, 1, 0)

for opbyte in range(0xc0, 0xd0):
    main_table[opbyte] = (False, 'or', p_i8_Rd, 1, e_const.IF_B)

for opbyte in range(0xd0, 0xe0):
    main_table[opbyte] = (False, 'xor', p_i8_Rd, 1, e_const.IF_B)

for opbyte in range(0xe0, 0xf0):
    main_table[opbyte] = (False, 'and', p_i8_Rd, 1, e_const.IF_B)

for opbyte in range(0xf0, 0x100):
    main_table[opbyte] = (False, 'mov', p_i8_Rd, 1, e_const.IF_B)
