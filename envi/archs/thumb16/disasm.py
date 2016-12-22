import envi.bits as e_bits
import envi.bintree as e_btree

from envi.bits import binary

from envi.archs.arm.disasm import *

# thumb_32 = [
# binary('11101'),
# binary('11110'),
# binary('11111'),
# ]


O_REG = 0
O_IMM = 1
O_OFF = 2

OperType = (
    ArmRegOper,
    ArmImmOper,
    ArmPcOffsetOper,
)


def shmaskval(value, shval,
              mask):  # FIXME: unnecessary to make this another fn call.  will be called a bajillion times.
    return (value >> shval) & mask


class simpleops:
    def __init__(self, *operdef):
        self.operdef = operdef

    def __call__(self, va, value):
        ret = []
        for otype, shval, mask in self.operdef:
            oval = shmaskval(value, shval, mask)
            oper = OperType[otype]((value >> shval) & mask, va=va)
            ret.append(oper)
        return ret


# imm5_rm_rd  = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 6, 0x1f))
rm_rn_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_REG, 6, 0x7))
imm3_rn_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 6, 0x7))
imm8_rd = simpleops((O_REG, 8, 0x7), (O_IMM, 0, 0xff))
rm_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rn_rdm = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rdn = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rd_imm0 = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 0, 0))
rm4_shift3 = simpleops((O_REG, 3, 0xf))
rm_rn_rt = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_REG, 6, 0x7))
imm8 = simpleops((O_IMM, 8, 0xff))
# imm11       = simpleops((O_IMM, 11, 0x7ff))

sh4_imm1 = simpleops((O_IMM, 3, 0x1))


def d1_rm4_rd3(va, value):
    # 0 1 0 0 0 1 0 0 DN(1) Rm(4) Rdn(3)
    rdbit = shmaskval(value, 4, 0x8)
    rd = shmaskval(value, 0, 0x7) + rdbit
    rm = shmaskval(value, 3, 0xf)
    return ArmRegOper(rd, va=va), ArmRegOper(rm, va=va)


def rm_rn_rt(va, value):
    rt = shmaskval(value, 0, 0x7)  # target
    rn = shmaskval(value, 3, 0x7)  # base
    rm = shmaskval(value, 6, 0x7)  # offset
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOffsetOper(rn, rm, va, pubwl=0x18)
    return oper0, oper1


def imm54_rn_rt(va, value):
    imm = shmaskval(value, 4, 0x7c)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc) + 4, pubwl=0x18)
    return oper0, oper1


def imm55_rn_rt(va, value):
    imm = shmaskval(value, 5, 0x3e)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc) + 4, pubwl=0x18)
    return oper0, oper1


def imm56_rn_rt(va, value):
    imm = shmaskval(value, 6, 0x1f)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc) + 4, pubwl=0x18)
    return oper0, oper1


def rd_sp_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = shmaskval(value, 0, 0xff) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOffsetOper(REG_SP, imm, (va & 0xfffffffc) + 4, pubwl=0x18)
    return oper0, oper1


def rd_pc_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOper((va & 0xfffffffc) + 4 + imm)
    return oper0, oper1


def rt_pc_imm8(va, value):  # ldr
    rt = shmaskval(value, 8, 0x7)
    imm = e_bits.signed((value & 0xff), 1) << 2
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(REG_PC, imm, (va & 0xfffffffc))
    return oper0, oper1


def bl_imm23(va, val, val2):  # bl
    opcode = INS_BL
    flags = envi.IF_CALL
    # need next two bytes
    imm = (val & 0x7ff) << 12
    imm |= ((val2 & 0x7ff) << 1)

    # break down the components
    S = (val >> 10) & 1
    j1 = (val2 >> 13) & 1
    j2 = (val2 >> 11) & 1
    i1 = ~ (j1 ^ S) & 0x1
    i2 = ~ (j2 ^ S) & 0x1
    X = (val2 >> 12) & 1
    mnem = ('blx', 'bl')[X]

    imm = (S << 24) | (i1 << 23) | (i2 << 22) | ((val & 0x3ff) << 12) | ((val2 & 0x7ff) << 1)

    # sign extend a 23-bit number
    if S:
        imm |= 0xff000000

    oper0 = ArmPcOffsetOper(e_bits.signed(imm, 4), va=va)
    return ((oper0,), mnem, opcode, flags)


def pc_imm11(va, value):  # b
    imm = e_bits.signed(((value & 0x7ff) << 1), 3)
    oper0 = ArmPcOffsetOper(imm, va=va)
    return oper0,


def pc_imm8(va, value):  # b
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 2
    oper0 = ArmPcOffsetOper(imm, va=va)
    return oper0,


def ldmia(va, value):
    rd = shmaskval(value, 8, 0x7)
    reg_list = value & 0xff
    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegListOper(reg_list)
    oper0.oflags |= OF_W
    return oper0, oper1


def sp_sp_imm7(va, value):
    imm = shmaskval(value, 0, 0x7f)
    o0 = ArmRegOper(REG_SP)
    o1 = ArmRegOper(REG_SP)
    o2 = ArmImmOper(imm * 4)
    return o0, o1, o2


def rm_reglist(va, value):
    rm = shmaskval(value, 8, 0x7)
    reglist = value & 0xff
    oper0 = ArmRegOper(rm, va=va)
    oper1 = ArmRegListOper(reglist)
    oper0.oflags |= OF_W
    return oper0, oper1


def pop_reglist(va, value):
    reglist = (value & 0xff) | ((value & 0x100) << 7)
    oper0 = ArmRegListOper(reglist)
    return (oper0,)


def push_reglist(va, value):
    reglist = (value & 0xff) | ((value & 0x100) << 6)
    oper0 = ArmRegListOper(reglist)
    return (oper0,)


def imm5_rm_rd(va, value):
    rd = value & 0x7
    rm = (value >> 3) & 0x7
    imm5 = (value >> 6) & 0x1f

    stype = value >> 11

    oper0 = ArmRegOper(rd, va)
    oper1 = ArmRegShiftImmOper(rm, stype, imm5, va)
    return (oper0, oper1,)


def i_imm5_rn(va, value):
    imm5 = shmaskval(value, 3, 0x40) | shmaskval(value, 2, 0x3e)
    rn = value & 0x7
    oper0 = ArmRegOper(rn, va)
    oper1 = ArmImmOffsetOper(REG_PC, imm5, va)
    return (oper0, oper1,)


def ldm16(va, value):
    raise Exception("32bit wrapping of 16bit instruction... and it's not implemented")


def thumb32_01(va, val, val2):
    op = (val2 >> 15) & 1
    op2 = (val >> 4) & 0x7f
    op1 = (val >> 11) & 0x3
    flags = 0

    if (op2 & 0x64) == 0:
        raise Exception('# Load/Store Multiples')
        op3 = (val >> 7) & 3
        W = (val >> 5) & 1
        L = (val >> 4) & 1
        mode = (val & 0xf)

        mnem, opcode = (('srs', INS_SRS), ('rfe', INS_RFE))[L]
        iadb = (val >> 7) & 3
        flags |= (IF_DB, 0, 0, IF_IA)[iadb]
        olist = (ArmRegOper(REG_SP), ArmImmOper(mode))

    elif (op2 & 0x64) == 4:
        raise Exception('# Load/Store Dual, Load/Store Exclusive, table branch')

    elif (op2 & 0x60) == 0x20:
        raise Exception('# Data Processing (shifted register)')

    elif (op2 & 0x40) == 0x40:
        raise Exception('# Coprocessor, Advanced SIMD, Floating point instrs')
    else:
        raise InvalidInstruction(
            mesg="Thumb32 failure",
            bytez=struct.pack("<H", val) + struct.pack("<H", val2), va=va)
    return (olist, mnem, opcode, flags)


def thumb32_10(va, val, val2):
    op = (val2 >> 15) & 1
    op2 = (val >> 4) & 0x7f
    op1 = (val >> 11) & 0x3
    flags = 0

    if (op2 & 0x20) == 0 and op == 0:
        raise Exception('# Data Processing (modified immediate)')

    elif (op2 & 0x20) == 1 and op == 0:
        raise Exception('# Data Processing (plain binary immediate)')

    elif op == 1:
        raise Exception('# Branches and miscellaneous control')

    else:
        raise InvalidInstruction(
            mesg="Thumb32 failure",
            bytez=struct.pack("<H", val) + struct.pack("<H", val2), va=va)
    return (olist, mnem, opcode, flags)


def thumb32_11(va, val, val2):
    op = (val2 >> 15) & 1
    op2 = (val >> 4) & 0x7f
    op1 = (val >> 11) & 0x3
    flags = 0
    if (op2 & 0x71) == 0:
        raise Exception('# Store single data item')

    if (op2 & 0x67) == 1:
        raise Exception('# Load byte, memory hints')

    if (op2 & 0x67) == 3:
        raise Exception('# Load half-word, memory hints')

    if (op2 & 0x71) == 0x10:
        raise Exception('# Advanced SIMD element or structure load/store instructions')

    if (op2 & 0x70) == 0x20:
        raise Exception('# Data Processing (register)')

    if (op2 & 0x78) == 0x30:
        raise Exception('# Multiply, multiply accumulate, and absolute difference')

    if (op2 & 0x78) == 0x38:
        raise Exception('# Long multiply, long multiply accumulate, and divide')

    if (op2 & 0x40) == 0x40:
        raise Exception('# Coprocessor, Advanced SIMD, Floating Point instrs')

    return (olist, mnem, opcode, flags)


def dp_mod_imm_32(va, val1, val2):
    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    const = val2 & 0xff
    a = const >> 7

    if i == 0:
        if imm3 & 4:
            const |= 0x80  # 1bcdefg
            off = (a | (imm3 << 1)) & 7
            const <<= (24 - off)
        elif imm3 == 1:
            const |= (const << 16)
        elif imm3 == 2:
            const <<= 8
            const |= (const << 16)
        elif imm3 == 3:
            const |= (const << 8) | (const << 16) | (const << 24)
    else:
        # see above for imm3 & 4
        const |= 0x80  # 1bcdefg
        off = (a | (imm3 << 1)) & 7
        const <<= (16 - off)

    oper0 = ArmImmOper(const)
    return (oper0, oper1), None, None, 0


def dp_plain_imm_32(va, val1, val2):
    pass


def ldm_reg_mode_32(va, val1, val2):
    rn = val1 & 0xf
    mode = val2 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    oper1 = ArmModeOper(mode, wback)
    return (oper0, oper1), None, None, 0


def ldm_reg_32(va, val1, val2):
    rn = val1 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    return (oper0,), None, None, 0


def ldm_32(va, val1, val2):
    rn = val1 & 0xf
    if val2 & 0x2000:
        raise InvalidInstruction("LDM instruction with stack indicated: 0x%x: 0x%x, 0x%x" % (va, val1, val2))
        # PC not ok on some instructions...  
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    oper1 = ArmRegListOper(val2)
    if wback:
        oper0.oflags = OF_W

    return (oper0, oper1), None, None, 0


def pop_32(va, val1, val2):
    if val2 & 0x2000:
        raise InvalidInstruction("LDM instruction with stack indicated: 0x%x: 0x%x, 0x%x" % (va, val1, val2))
        # PC not ok on some instructions...  
    oper0 = ArmRegListOper(val2)
    return (oper0,), None, None, 0


def dp_plain_imm_32(va, val1, val2):
    pass


def strex_32(va, val1, val2):
    rn = val1 & 0xf
    rd = (val2 >> 8) & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rt, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8 << 2, va=va)

    return (oper0, oper1, oper2), None, None, 0


def ldrex_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8 << 2, va=va)

    return (oper0, oper1), None, None, 0


def ldrd_imm_32(va, val1, val2):
    pubwl = (val1 >> 4) & 0x1f
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    rt2 = (val2 >> 8) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOper(rt2, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8 << 2, va=va, pubwl=pubwl)

    return (oper0, oper1, oper2), None, None, 0


def strexn_32(va, val1, val2):
    op3 = (val1 >> 4) & 0xf
    if (op3 & 0xc != 0x10):
        bytez = struct.pack("<HH", val1, val2)
        raise InvalidInstruction(bytez=bytez, va=va)

    tsize = op3 & 4
    mnem = ('strexb', 'strexh', None, 'strexd')[tsize]
    rn = val1 & 0xf
    rd = val2 & 0xf
    rt = (val2 >> 12) & 0xf

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rt, va=va)
    oper2 = ArmRegOper(rn, va=va)

    return (oper0, oper1, oper2), mnem, opcode, 0


def tb_ldrex_32(va, val1, val2):
    op3 = (val2 >> 4) & 0xf

    rn = val1 & 0xf
    rm = val2 & 0xf
    rt = (val2 >> 12) & 0xf
    flags = IF_THUMB32 | (IF_B, IF_H, 0, IF_D)[op3 & 3]

    if op3 & 4:  # ldrex#
        mnem = 'ldrex'
        opcode = INS_LDREX

        oper0 = ArmRegOper(rt, va=va)
        oper1 = ArmRegOper(rn, va=va)
        opers = (oper0, oper1)
    else:  # tbb/tbh
        mnem = 'tb'
        opcode = INS_TB

        oper0 = ArmRegOper(rn, va=va)
        oper1 = ArmRegOper(rm, va=va)
        opers = (oper0, oper1)

    return opers, mnem, opcode, flags


mov_ris_ops = (
    (INS_LSL, 'lsl', 3),
    (INS_LSR, 'lsr', 3),
    (INS_ASR, 'asr', 3),
    (INS_ROR, 'ror', 3),
)
mov_ris_alt = (
    (INS_MOV, 'mov', 2),
    (INS_LSR, 'lsr', 3),
    (INS_ASR, 'asr', 3),
    (INS_RRX, 'rrx', 2),
)


def mov_reg_imm_shift_32(va, val1, val2):
    optype = (val2 >> 4) & 3
    imm = ((val2 >> 10) & 0x1c) | ((val2 >> 6) & 3)
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf
    s = (val1 >> 4) & 1

    if imm == 0 and optype in (0, 3):
        opcode, mnem, opcnt = mov_ris_alt[optype]
    else:
        opcode, mnem, opcnt = mov_ris_ops[optype]
    if s:
        flags = IF_S
    else:
        flags = 0

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rm, va=va)
    oper2 = ArmImmOper(imm)
    opers = (oper0, oper1, oper2)[:opcnt]

    return opers, mnem, opcode, flags


dp_shift_ops = ((INS_AND, 'and', 3),
                (INS_BIC, 'bic', 3),
                (INS_ORR, 'orr', 3),
                (INS_ORN, 'orn', 3),
                (INS_EOR, 'eor', 3),
                (0, 'inval', 0),
                (INS_PKH, 'pkh', 3),
                (0, 'inval', 0),
                (INS_ADD, 'add', 3),
                (0, 'inval', 0),
                (INS_ADC, 'adc', 3),
                (INS_SBC, 'sbc', 3),
                (0, 'inval', 0),
                (INS_SUB, 'sub', 3),
                (INS_RSB, 'rsb', 3),
                )
dp_shift_alt1 = ((INS_TST, 'tst', 2),
                 (INS_BIC, 'bic', 3),
                 (INS_ORR, 'orr', 3),
                 (INS_ORN, 'orn', 3),
                 (INS_TEQ, 'teq', 2),
                 (0, 'inval', 0),
                 (INS_PKH, 'pkh', 3),
                 (0, 'inval', 0),
                 (INS_CMN, 'cmn', 2),
                 (0, 'inval', 0),
                 (INS_ADC, 'adc', 3),
                 (INS_SBC, 'sbc', 3),
                 (0, 'inval', 0),
                 (INS_CMP, 'cmp', 2),
                 (INS_RSB, 'rsb', 3),
                 )
dp_shift_alt2 = ((INS_AND, 'and', 3),
                 (INS_BIC, 'bic', 3),
                 (INS_ORR, 'orr', 3),
                 (INS_MVN, 'mvn', 2),
                 (INS_EOR, 'eor', 3),
                 (0, 'inval', 0),
                 (INS_PKH, 'pkh', 3),
                 (0, 'inval', 0),
                 (INS_ADD, 'add', 3),
                 (0, 'inval', 0),
                 (INS_ADC, 'adc', 3),
                 (INS_SBC, 'sbc', 3),
                 (0, 'inval', 0),
                 (INS_SUB, 'sub', 3),
                 (INS_RSB, 'rsb', 3),
                 )


def dp_shift_32(va, val1, val2):
    op = (val1 >> 5) & 0xf
    rn = val1 & 0xf
    rd = (val2 >> 8) & 0xf
    rm = val2 & 0xf
    imm = ((val2 >> 10) & 0x1c) | ((val2 >> 6) & 3)
    shtype = (val2 >> 4) & 0x3
    s = (val1 >> 4) & 1

    oper2 = ArmRegShiftImmOper(rm, shtype, imm, va=va)

    if rd == 0xf and s:
        opcode, mnem, opcnt = dp_shift_alt1[op]
        oper1 = ArmRegOper(rn, va=va)
        if opcnt == 3:
            oper0 = ArmRegOper(rd, va=va)
            opers = (oper0, oper1, oper2)
        else:
            opers = (oper1, oper2)

    elif rn == 0xf:
        opcode, mnem, opcnt = dp_shift_alt2[op]
        oper0 = ArmRegOper(rd, va=va)
        if opcnt == 3:
            oper1 = ArmRegOper(rn, va=va)
            opers = (oper0, oper1, oper2)
        else:
            opers = (oper0, oper2)

    else:
        opcode, mnem, opcnt = dp_shift_ops[op]
        oper0 = ArmRegOper(rd, va=va)
        oper1 = ArmRegOper(rn, va=va)
        opers = (oper0, oper1, oper2)

    if s:
        flags = IF_S
    else:
        flags = 0

    return opers, mnem, opcode, flags


def dp_mod_imm_32(va, val1, val2):
    op = (val1 >> 5) & 0xf
    rn = val1 & 0xf
    rd = (val2 >> 8) & 0xf
    imm = ((val1 >> 10) & 1) | ((val2 >> 4) & 0xf00) | (val2 & 0xff)
    s = (val1 >> 4) & 1

    oper2 = ArmImmOper(imm)

    if rd == 0xf and s:
        opcode, mnem, opcnt = dp_shift_alt1[op]
        oper1 = ArmRegOper(rn, va=va)
        if opcnt == 3:
            oper0 = ArmRegOper(rd, va=va)
            opers = (oper0, oper1, oper2)
        else:
            opers = (oper1, oper2)

    elif rn == 0xf:
        opcode, mnem, opcnt = dp_shift_alt2[op]
        oper0 = ArmRegOper(rd, va=va)
        if opcnt == 3:
            oper1 = ArmRegOper(rn, va=va)
            opers = (oper0, oper1, oper2)
        else:
            opers = (oper0, oper2)

    else:
        opcode, mnem, opcnt = dp_shift_ops[op]
        oper0 = ArmRegOper(rd, va=va)
        oper1 = ArmRegOper(rn, va=va)
        opers = (oper0, oper1, oper2)

    if s:
        flags = IF_S
    else:
        flags = 0

    return opers, mnem, opcode, flags


def coproc_simd_32(va, val1, val2):
    pass


def adv_simd_32(va, val1, val2):
    # aside from u and the first 8 bits, ARM and Thumb2 decode identically (A7-259)
    u = (val1 >> 12) & 1
    a = (val1 >> 3) & 0x1f
    b = (val2 >> 8) & 0xf
    c = (val2 >> 4) & 0xf

    if not (a & 0x10):
        # three registers of the same length
        a = (val2 >> 8) & 0xf
        b = (val2 >> 4) & 1
        c = (val1 >> 4) & 3
        if a == 0:
            if b == 0:
                # vhadd/vhsub
                size = (val1 >> 4) & 3

                d = (val1 >> 2) & 0x10
                d |= ((val2 >> 12) & 0xf)

                n = (val2 >> 3) & 0x10
                n |= (val1 & 0xf)

                m = (val2 >> 1) & 0x10
                m |= (val2 & 0xf)

                q = (val2 >> 2) & 0x10

                op = (val2 >> 9) & 1

                opcode, mnem = ((INS_VHADD, 'vhadd'), (INS_VHSUB, 'vhsub'))[op]
                flags = (IF_S8, IF_S16, IF_S32, 0, IF_U8, IF_U16, IF_U32)[(u << 2) | size]
                return opers, mnem, opcode, flags

        elif a == 1:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 2:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 3:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 4:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 5:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 6:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 7:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 8:
            raise Exception("Advanced SIMD instructions not all implemented")
            midx = (b << 1) | u
            opcode, mnem = ((INS_VADD, 'vadd'), (INS_VSUB, 'vsub'), (INS_VTST, 'vtst'), (INS_VCEQ, 'vceq'))[midx]
        elif a == 9:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 10:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 11:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 12:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 13:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 14:
            raise Exception("Advanced SIMD instructions not all implemented")
        elif a == 15:
            raise Exception("Advanced SIMD instructions not all implemented")


# opinfo is:
# ( <mnem>, <operdef>, <flags> )
# operdef is:
# ( (otype, oshift, omask), ...)

# FIXME: thumb and arm opcode numbers don't line up. - FIX
thumb_base = [
    ('00000', (0, 'lsl', imm5_rm_rd, 0)),  # LSL<c> <Rd>,<Rm>,#<imm5>
    ('00001', (1, 'lsr', imm5_rm_rd, 0)),  # LSR<c> <Rd>,<Rm>,#<imm>
    ('00010', (2, 'asr', imm5_rm_rd, 0)),  # ASR<c> <Rd>,<Rm>,#<imm>
    ('0001100', (INS_ADD, 'add', rm_rn_rd, 0)),  # ADD<c> <Rd>,<Rn>,<Rm>
    ('0001101', (INS_SUB, 'sub', rm_rn_rd, 0)),  # SUB<c> <Rd>,<Rn>,<Rm>
    ('0001110', (INS_ADD, 'add', imm3_rn_rd, 0)),  # ADD<c> <Rd>,<Rn>,#<imm3>
    ('0001111', (INS_SUB, 'sub', imm3_rn_rd, 0)),  # SUB<c> <Rd>,<Rn>,#<imm3>
    ('00100', (7, 'mov', imm8_rd, 0)),  # MOV<c> <Rd>,#<imm8>
    ('00101', (8, 'cmp', imm8_rd, 0)),  # CMP<c> <Rn>,#<imm8>
    ('00110', (INS_ADD, 'add', imm8_rd, 0)),  # ADD<c> <Rdn>,#<imm8>
    ('00111', (INS_SUB, 'sub', imm8_rd, 0)),  # SUB<c> <Rdn>,#<imm8>
    # Data processing instructions
    ('0100000000', (11, 'and', rm_rdn, 0)),  # AND<c> <Rdn>,<Rm>
    ('0100000001', (12, 'eor', rm_rdn, 0)),  # EOR<c> <Rdn>,<Rm>
    ('0100000010', (13, 'lsl', rm_rdn, 0)),  # LSL<c> <Rdn>,<Rm>
    ('0100000011', (14, 'lsr', rm_rdn, 0)),  # LSR<c> <Rdn>,<Rm>
    ('0100000100', (15, 'asr', rm_rdn, 0)),  # ASR<c> <Rdn>,<Rm>
    ('0100000101', (16, 'adc', rm_rdn, 0)),  # ADC<c> <Rdn>,<Rm>
    ('0100000110', (17, 'sbc', rm_rdn, 0)),  # SBC<c> <Rdn>,<Rm>
    ('0100000111', (18, 'ror', rm_rdn, 0)),  # ROR<c> <Rdn>,<Rm>
    ('0100001000', (19, 'tst', rm_rd, 0)),  # TST<c> <Rn>,<Rm>
    ('0100001001', (20, 'rsb', rm_rd_imm0, 0)),  # RSB<c> <Rd>,<Rn>,#0
    ('0100001010', (21, 'cmp', rm_rd, 0)),  # CMP<c> <Rn>,<Rm>
    ('0100001011', (22, 'cmn', rm_rd, 0)),  # CMN<c> <Rn>,<Rm>
    ('0100001100', (23, 'orr', rm_rdn, 0)),  # ORR<c> <Rdn>,<Rm>
    ('0100001101', (24, 'mul', rn_rdm, 0)),  # MUL<c> <Rdm>,<Rn>,<Rdm>
    ('0100001110', (25, 'bic', rm_rdn, 0)),  # BIC<c> <Rdn>,<Rm>
    ('0100001111', (26, 'mvn', rm_rd, 0)),  # MVN<c> <Rd>,<Rm>
    # Special data in2tructions and branch and exchange
    ('0100010000', (INS_ADD, 'add', d1_rm4_rd3, 0)),  # ADD<c> <Rdn>,<Rm>
    ('0100010001', (INS_ADD, 'add', d1_rm4_rd3, 0)),  # ADD<c> <Rdn>,<Rm>
    ('010001001', (INS_ADD, 'add', d1_rm4_rd3, 0)),  # ADD<c> <Rdn>,<Rm>
    ('010001010', (30, 'cmp', d1_rm4_rd3, 0)),  # CMP<c> <Rn>,<Rm>
    ('010001011', (31, 'cmp', d1_rm4_rd3, 0)),  # CMP<c> <Rn>,<Rm>
    ('01000110', (34, 'mov', d1_rm4_rd3, 0)),  # MOV<c> <Rd>,<Rm>
    ('010001110', (35, 'bx', rm4_shift3, envi.IF_NOFALL)),  # BX<c> <Rm>
    ('010001111', (36, 'blx', rm4_shift3, 0)),  # BLX<c> <Rm>
    # Load from Litera7 Pool
    ('01001', (37, 'ldr', rt_pc_imm8, 0)),  # LDR<c> <Rt>,<label>
    # Load/Stor single data item
    ('0101000', (38, 'str', rm_rn_rt, 0)),  # STR<c> <Rt>,[<Rn>,<Rm>]
    ('0101001', (39, 'strh', rm_rn_rt, 0)),  # STRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101010', (40, 'strb', rm_rn_rt, 0)),  # STRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101011', (41, 'ldrsb', rm_rn_rt, 0)),  # LDRSB<c> <Rt>,[<Rn>,<Rm>]
    ('0101100', (42, 'ldr', rm_rn_rt, 0)),  # LDR<c> <Rt>,[<Rn>,<Rm>]
    ('0101101', (43, 'ldrh', rm_rn_rt, 0)),  # LDRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101110', (44, 'ldrb', rm_rn_rt, 0)),  # LDRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101111', (45, 'ldrsh', rm_rn_rt, 0)),  # LDRSH<c> <Rt>,[<Rn>,<Rm>]
    ('01100', (46, 'str', imm54_rn_rt, 0)),  # STR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01101', (47, 'ldr', imm54_rn_rt, 0)),  # LDR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01110', (48, 'strb', imm56_rn_rt, 0)),  # STRB<c> <Rt>,[<Rn>,#<imm5>]
    ('01111', (49, 'ldrb', imm56_rn_rt, 0)),  # LDRB<c> <Rt>,[<Rn>{,#<imm5>}]
    ('10000', (50, 'strh', imm55_rn_rt, 0)),  # STRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10001', (51, 'ldrh', imm55_rn_rt, 0)),  # LDRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10010', (52, 'str', rd_sp_imm8, 0)),  # STR<c> <Rt>, [<Rn>{,#<imm>}]
    ('10011', (53, 'ldr', rd_sp_imm8, 0)),  # LDR<c> <Rt>, [<Rn>{,#<imm>}]
    # Generate PC relative address
    ('10100', (INS_ADD, 'add', rd_pc_imm8, 0)),  # ADD<c> <Rd>,<label>
    # Generate SP rel5tive address
    ('10101', (INS_ADD, 'add', rd_sp_imm8, 0)),  # ADD<c> <Rd>,SP,#<imm>
    # Miscellaneous in6tructions
    ('1011001000', (561, 'sxth', rm_rd, 0)),  # SXTH<c> <Rd>, <Rm>
    ('1011001001', (561, 'sxtb', rm_rd, 0)),  # SXTB<c> <Rd>, <Rm>
    ('1011001000', (561, 'uxth', rm_rd, 0)),  # UXTH<c> <Rd>, <Rm>
    ('1011001001', (561, 'uxtb', rm_rd, 0)),  # UXTB<c> <Rd>, <Rm>
    ('1011010', (56, 'push', push_reglist, 0)),  # PUSH <reglist>
    ('10110110010', (57, 'setend', sh4_imm1, 0)),  # SETEND <endian_specifier>
    ('10110110011', (58, 'cps', simpleops(), 0)),  # CPS<effect> <iflags> FIXME
    ('10110001', (59, 'cbz', i_imm5_rn, 0)),  # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111001', (60, 'cbnz', i_imm5_rn, 0)),  # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('10110011', (59, 'cbz', i_imm5_rn, 0)),  # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111011', (60, 'cbnz', i_imm5_rn, 0)),  # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('1011101000', (61, 'rev', rn_rdm, 0)),  # REV Rd, Rn
    ('1011101001', (62, 'rev16', rn_rdm, 0)),  # REV16 Rd, Rn
    ('1011101011', (63, 'revsh', rn_rdm, 0)),  # REVSH Rd, Rn
    ('101100000', (INS_ADD, 'add', sp_sp_imm7, 0)),  # ADD<c> SP,SP,#<imm>
    ('101100001', (INS_SUB, 'sub', sp_sp_imm7, 0)),  # SUB<c> SP,SP,#<imm>
    ('1011110', (66, 'pop', pop_reglist, 0)),  # POP<c> <registers>
    ('10111110', (67, 'bkpt', imm8, 0)),  # BKPT <blahblah>
    # Load / Store Mu64iple
    ('11000', (68, 'stm', rm_reglist, IF_IA | IF_W)),  # LDMIA Rd!, reg_list
    ('11001', (69, 'ldm', rm_reglist, IF_IA | IF_W)),  # STMIA Rd!, reg_list
    # Conditional Bran6hes
    ('11010000', (INS_BCC, 'beq', pc_imm8, envi.IF_COND)),
    ('11010001', (INS_BCC, 'bn', pc_imm8, envi.IF_COND)),
    ('11010010', (INS_BCC, 'bhs', pc_imm8, envi.IF_COND)),
    ('11010011', (INS_BCC, 'blo', pc_imm8, envi.IF_COND)),
    ('11010100', (INS_BCC, 'bmi', pc_imm8, envi.IF_COND)),
    ('11010101', (INS_BCC, 'bpl', pc_imm8, envi.IF_COND)),
    ('11010110', (INS_BCC, 'bvs', pc_imm8, envi.IF_COND)),
    ('11010111', (INS_BCC, 'bvc', pc_imm8, envi.IF_COND)),
    ('11011000', (INS_BCC, 'bhi', pc_imm8, envi.IF_COND)),
    ('11011001', (INS_BCC, 'bls', pc_imm8, envi.IF_COND)),
    ('11011010', (INS_BCC, 'bge', pc_imm8, envi.IF_COND)),
    ('11011011', (INS_BCC, 'blt', pc_imm8, envi.IF_COND)),
    ('11011100', (INS_BCC, 'bgt', pc_imm8, envi.IF_COND)),
    ('11011101', (INS_BCC, 'ble', pc_imm8, envi.IF_COND)),
    ('11011110', (INS_B, 'b', pc_imm8, envi.IF_NOFALL)),
    ('11011111', (INS_BCC, 'bfukt', pc_imm8, 0)),
    # Software Interru2t
    ('11011111', (INS_SWI, 'swi', imm8, 0)),  # SWI <blahblah>
    ('1011111100000000', (89, 'nopHint', imm8, 0)),  # unnecessary instruction
    ('1011111100010000', (90, 'yieldHint', imm8, 0)),  # unnecessary instruction
    ('1011111100100000', (91, 'wfrHint', imm8, 0)),  # unnecessary instruction
    ('1011111100110000', (92, 'wfiHint', imm8, 0)),  # unnecessary instruction
    ('1011111101000000', (93, 'sevHint', imm8, 0)),  # unnecessary instruction
    ('101111110000', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110001', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110010', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110011', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110100', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110101', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110110', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111110111', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111000', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111001', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111010', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111011', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111100', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111101', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111110', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
    ('101111111111', (94, 'if-then-Hint', imm8, 0)),  # unnecessary instruction
]

thumb1_extension = [
    ('11100', (INS_B, 'b', pc_imm11, envi.IF_NOFALL)),  # B <imm11>
    ('1111', (INS_BL, 'bl', bl_imm23, envi.IF_CALL | IF_THUMB32)),  # BL/BLX <addr25>
]

# ##  holy crap, this is so wrong and incomplete....
# FIXME: need to take into account ThumbEE 
thumb2_extension = [
    ('11100', (85, 'ldm', ldm16, 0)),  # 16-bit instructions
    # ('11101',       (86,'blah32',   thumb32_01,   IF_THUMB32)),         # can't do thumb32 in tree-fashion
    # ('11110',       (86,'blah32',   thumb32_10,   IF_THUMB32)),         # op2 is sparse and op is part of
    # ('11111',       (86,'blah32',   thumb32_11,   IF_THUMB32)),         # second halfword

    # load/store multiple (A6-235 in ARM DDI 0406C)
    ('111010000000', (85, 'srsdb', ldm_reg_mode_32, IF_THUMB32 | IF_DB)),  # 110111000000000mode
    ('111010000001', (85, 'rfedb', ldm_reg_32, IF_THUMB32 | IF_DB)),
    ('111010000010', (85, 'srsia', ldm_reg_mode_32, IF_THUMB32 | IF_DB)),
    ('111010000011', (85, 'rfeia', ldm_reg_32, IF_THUMB32 | IF_DB)),

    ('111010001000', (85, 'stm', ldm_32, IF_THUMB32 | IF_IA)),  # stm(stmia/stmea)
    ('111010001001', (85, 'ldm', ldm_32, IF_THUMB32 | IF_IA)),  # ldm/ldmia/ldmfd
    ('111010001010', (85, 'stm', ldm_32, IF_THUMB32 | IF_W | IF_IA)),  # stm(stmia/stmea)
    ('1110100010110', (85, 'ldm', ldm_32, IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('11101000101110', (85, 'ldm', ldm_32, IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('111010001011111', (85, 'ldm', ldm_32, IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('1110100010111100', (85, 'ldm', ldm_32, IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('1110100010111101', (85, 'pop', pop_32, IF_THUMB32 | IF_W)),  # 111101 - pop

    ('111010010000', (85, 'stm', ldm_32, IF_THUMB32)),  # stmdb/stmfd
    ('111010010001', (85, 'ldm', ldm_32, IF_THUMB32)),  # ldmdb/ldmea
    ('1110100100100', (85, 'stm', ldm_32, IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('11101001001010', (85, 'stm', ldm_32, IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('111010010010111', (85, 'stm', ldm_32, IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('1110100100101100', (85, 'stm', ldm_32, IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('1110100100101101', (85, 'push', pop_32, IF_THUMB32 | IF_W)),  # 101101 - push
    ('111010010011', (85, 'ldm', ldm_32, IF_THUMB32 | IF_W | IF_DB)),  # ldmdb/ldmea

    ('111010011000', (85, 'srs', ldm_reg_mode_32, IF_THUMB32 | IF_IA)),
    ('111010011001', (85, 'rfe', ldm_reg_32, IF_THUMB32 | IF_IA)),
    ('111010011010', (85, 'srs', ldm_reg_mode_32, IF_THUMB32 | IF_IA)),
    ('111010011011', (85, 'rfe', ldm_reg_32, IF_THUMB32 | IF_IA)),

    # load/store dual, load/store exclusive, table branch
    ('111010000100', (85, 'strex', strex_32, IF_THUMB32)),
    ('111010000101', (85, 'ldrex', ldrex_32, IF_THUMB32)),

    ('111010000110', (85, 'strd', ldrd_imm_32, IF_THUMB32)),
    ('111010001110', (85, 'strd', ldrd_imm_32, IF_THUMB32)),
    ('111010010100', (85, 'strd', ldrd_imm_32, IF_THUMB32)),
    ('111010010110', (85, 'strd', ldrd_imm_32, IF_THUMB32)),
    ('111010011100', (85, 'strd', ldrd_imm_32, IF_THUMB32)),
    ('111010011110', (85, 'strd', ldrd_imm_32, IF_THUMB32)),

    ('111010000111', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),
    ('111010001111', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),
    ('111010010101', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),
    ('111010010111', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),
    ('111010011101', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),
    ('111010011111', (85, 'ldrd', ldrd_imm_32, IF_THUMB32)),

    ('111010001100', (85, 'strex', strexn_32, IF_THUMB32)),
    ('111010001101', (85, 'tb', tb_ldrex_32, IF_THUMB32)),

    # data-processing (shifted register)
    # ('1110101',             (85,'dp_sr',    dp_shift_32,         IF_THUMB32)),
    ('1110101001001111', (85, 'mov_reg_sh', mov_reg_imm_shift_32, IF_THUMB32)),  # mov_imm if rn=1111
    ('1110101001011111', (85, 'mov_reg_sh', mov_reg_imm_shift_32, IF_THUMB32)),  # mov_imm if rn=1111
    ('11101010000', (85, 'and', dp_shift_32, IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11101010001', (85, 'bic', dp_shift_32, IF_THUMB32)),

    ('1110101001000', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('11101010010010', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('111010100100110', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('1110101001001110', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('1110101001010', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('11101010010110', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('111010100101110', (85, 'orr', dp_shift_32, IF_THUMB32)),
    ('1110101001011110', (85, 'orr', dp_shift_32, IF_THUMB32)),

    ('11101010011', (85, 'orn', dp_shift_32, IF_THUMB32)),  # mvn if rn=1111
    ('11101010100', (85, 'eor', dp_shift_32, IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11101010110', (85, 'pkh', dp_shift_32, IF_THUMB32)),
    ('11101011000', (85, 'add', dp_shift_32, IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11101011010', (85, 'adc', dp_shift_32, IF_THUMB32)),
    ('11101011011', (85, 'sbc', dp_shift_32, IF_THUMB32)),
    ('11101011101', (85, 'sub', dp_shift_32, IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11101011110', (85, 'rsb', dp_shift_32, IF_THUMB32)),

    # coproc, adv simd, fp-instrs
    ('11101111', (85, 'adv simd', adv_simd_32, IF_THUMB32)),  # not fully implemented :)
    ('11111111', (85, 'adv simd', adv_simd_32, IF_THUMB32)),  # FIXME: not implemented
    ('11101110', (85, 'coproc simd', coproc_simd_32, IF_THUMB32)),  # FIXME: not implemented
    ('11111110', (85, 'coproc simd', coproc_simd_32, IF_THUMB32)),  # FIXME: not implemented

    # data-processing (modified immediate)
    # ('1111000',         (85,'rsb',      dp_mod_imm_32,        IF_THUMB32)),
    # ('1111010',         (85,'rsb',      dp_mod_imm_32,        IF_THUMB32)),

    ('11110000000', (85, 'and', dp_mod_imm_32, IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110000001', (85, 'bic', dp_mod_imm_32, IF_THUMB32)),
    ('11110000010', (85, 'orr', dp_mod_imm_32, IF_THUMB32)),
    ('11110000011', (85, 'orn', dp_mod_imm_32, IF_THUMB32)),  # mvn if rn=1111
    ('11110000100', (85, 'eor', dp_mod_imm_32, IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110001000', (85, 'add', dp_mod_imm_32, IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110001010', (85, 'adc', dp_mod_imm_32, IF_THUMB32)),
    ('11110001011', (85, 'sbc', dp_mod_imm_32, IF_THUMB32)),
    ('11110001101', (85, 'sub', dp_mod_imm_32, IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110001110', (85, 'rsb', dp_mod_imm_32, IF_THUMB32)),
    ('11110100000', (85, 'and', dp_mod_imm_32, IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110100001', (85, 'bic', dp_mod_imm_32, IF_THUMB32)),
    ('11110100010', (85, 'orr', dp_mod_imm_32, IF_THUMB32)),
    ('11110100011', (85, 'orn', dp_mod_imm_32, IF_THUMB32)),  # mvn if rn=1111
    ('11110100100', (85, 'eor', dp_mod_imm_32, IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110101000', (85, 'add', dp_mod_imm_32, IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110101010', (85, 'adc', dp_mod_imm_32, IF_THUMB32)),
    ('11110101011', (85, 'sbc', dp_mod_imm_32, IF_THUMB32)),
    ('11110101101', (85, 'sub', dp_mod_imm_32, IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110101110', (85, 'rsb', dp_mod_imm_32, IF_THUMB32)),
    ('11100', (INS_B, 'b', pc_imm11, envi.IF_NOFALL)),  # B <imm11>
    ('1111', (INS_BL, 'bl', bl_imm23, envi.IF_CALL | IF_THUMB32)),  # BL/BLX <addr25>
]
'''
'''
thumb_table = list(thumb_base)
thumb_table.extend(thumb1_extension)

thumb2_table = list(thumb_base)
thumb2_table.extend(thumb2_extension)

ttree = e_btree.BinaryTree()
for binstr, opinfo in thumb_table:
    ttree.addBinstr(binstr, opinfo)

ttree2 = e_btree.BinaryTree()
for binstr, opinfo in thumb2_table:
    ttree2.addBinstr(binstr, opinfo)

thumb32mask = binary('11111')
thumb32min = binary('11100')


def is_thumb32(val):
    '''
    Take a 16 bit integer (opcode) value and determine
    if it is really the first 16 bits of a 32 bit
    instruction.
    '''
    bval = val >> 11
    return (bval & thumb32mask) > thumb32min


class ThumbOpcode(ArmOpcode):
    _def_arch = envi.ARCH_THUMB16
    pass


class Thumb2Opcode(ArmOpcode):
    _def_arch = envi.ARCH_THUMB2
    pass


class Thumb16Disasm:
    _tree = ttree
    _optype = envi.ARCH_THUMB16
    _opclass = ThumbOpcode

    def disasm(self, bytez, offset, va, trackMode=True):
        flags = 0
        va &= -2
        val, = struct.unpack("<H", bytez[offset:offset + 2])
        try:
            opcode, mnem, opermkr, flags = self._tree.getInt(val, 16)
        except TypeError:
            raise envi.InvalidInstruction(
                mesg="disasm parser cannot find instruction",
                bytez=bytez[offset:offset + 2], va=va)

        if flags & IF_THUMB32:
            val2, = struct.unpack("<H", bytez[offset + 2:offset + 4])
            olist, nmnem, nopcode, nflags = opermkr(va + 4, val, val2)
            if nmnem != None:  # allow opermkr to set the mnem
                mnem = nmnem
                opcode = nopcode
            if nflags != None:
                flags = nflags
            oplen = 4
        else:
            olist = opermkr(va + 4, val)
            oplen = 2

        # since our flags determine how the instruction is decoded later....  
        # performance-wise this should be set as the default value instead of 0, but this is cleaner
        flags |= self._optype

        if (len(olist) and
                isinstance(olist[0], ArmRegOper) and
                olist[0].involvesPC() and
                    opcode not in no_update_Rd):
            showop = True
            flags |= envi.IF_NOFALL

        op = ThumbOpcode(va, opcode, mnem, 0xe, oplen, olist, flags)
        return op


class Thumb2Disasm(Thumb16Disasm):
    _tree = ttree2
    _optype = envi.ARCH_THUMB2
    _opclass = Thumb2Opcode


if __name__ == '__main__':
    import envi.archs

    envi.archs.dismain(Thumb16Disasm())
