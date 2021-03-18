from envi.archs.arm.disasm import _do_adv_simd_32, _do_fp_dp, _do_adv_simd_ldst_32
import envi.bits as e_bits
import envi.bintree as e_btree

from envi.bits import binary
from envi import InvalidInstruction

from envi.archs.arm.disasm import *
armd = ArmDisasm()


O_REG = 0
O_IMM = 1
O_OFF = 2

OperType = (ArmRegOper,
            ArmImmOper,
            ArmPcOffsetOper)


def shmaskval(value, shval, mask):
    return (value >> shval) & mask


class simpleops:
    def __init__(self, *operdef):
        self.operdef = operdef

    def __call__(self, va, value):
        ret = []
        for otype, shval, mask in self.operdef:
            oper = OperType[otype]((value >> shval) & mask, va=va)
            ret.append(oper)
        return COND_AL, ret, None


rm_rn_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_REG, 6, 0x7))
imm3_rn_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 6, 0x7))
imm8_rd = simpleops((O_REG, 8, 0x7), (O_IMM, 0, 0xff))
rm_rd = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rn_rdm = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rdn = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rd_imm0 = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 0, 0))
imm8 = simpleops((O_IMM, 8, 0xff))
sh4_imm1 = simpleops((O_IMM, 3, 0x1))


def d1_rm4_rd3(va, value):
    # 0 1 0 0 0 1 0 0 DN(1) Rm(4) Rdn(3)
    rdbit = shmaskval(value, 4, 0x8)
    rd = shmaskval(value, 0, 0x7) + rdbit
    rm = shmaskval(value, 3, 0xf)
    return COND_AL, (ArmRegOper(rd, va=va), ArmRegOper(rm, va=va)), None


def rm_rn_rt(va, value):
    tsize = (4, 2, 1, 1, 4, 2, 1, 2)[(value >> 9) & 7]
    rt = shmaskval(value, 0, 0x7)  # target
    rn = shmaskval(value, 3, 0x7)  # base
    rm = shmaskval(value, 6, 0x7)  # offset
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOffsetOper(rn, rm, va, pubwl=0x18, tsize=tsize)
    return COND_AL, (oper0, oper1), None


def imm54_rn_rt(va, value):
    imm = shmaskval(value, 4, 0x7c)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc)+4, pubwl=0x18, tsize=4)
    return COND_AL, (oper0, oper1), None


def imm55_rn_rt(va, value):
    imm = shmaskval(value, 5, 0x3e)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc)+4, pubwl=0x18, tsize=2)
    return COND_AL, (oper0, oper1), None


def imm56_rn_rt(va, value):
    imm = shmaskval(value, 6, 0x1f)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va & 0xfffffffc)+4, pubwl=0x18, tsize=1)
    return COND_AL, (oper0, oper1), None


def rd_sp_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = shmaskval(value, 0, 0xff) * 4
    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(REG_SP, va=va)
    oper2 = ArmImmOper(imm, va=va)
    return COND_AL, (oper0, oper1, oper2), None


def rd_sp_imm8d(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = shmaskval(value, 0, 0xff) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOffsetOper(REG_SP, imm, (va & 0xfffffffc)+4, pubwl=0x18)
    return COND_AL, (oper0, oper1), None


def rd_pc_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOper((va & 0xfffffffc) + 4 + imm)
    return COND_AL, (oper0, oper1), None


def rd_pc_imm8d(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOffsetOper(REG_PC, imm, (va & 0xfffffffc)+4, pubwl=0x18)
    return COND_AL, (oper0, oper1), None


def rt_pc_imm8d(va, value):  # ldr
    rt = shmaskval(value, 8, 0x7)
    imm = e_bits.unsigned((value & 0xff), 1) << 2
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(REG_PC, imm, (va & 0xfffffffc))
    return COND_AL, (oper0, oper1), None

bx_flag_opts = (
        envi.IF_BRANCH | envi.IF_NOFALL,
        envi.IF_RET | envi.IF_NOFALL, 
        envi.IF_CALL, 
        envi.IF_CALL,
        )

def rm4_shift3(va, value):  # bx/blx
    iflags = None
    otype, shval, mask = O_REG, 3, 0xf
    oval = shmaskval(value, shval, mask)
    oper = ArmRegOper((value >> shval) & mask, va=va)
    
    isLR = (oval == REG_LR) & 1 # convert to bit 0
    l = (value >> 6) & 2   # store in bit 1

    iflags = bx_flag_opts[(isLR | l)]

    return COND_AL, (oper,), iflags


banked_regs = ((REG_OFFSET_USR + 8, ),
               (REG_OFFSET_USR + 9, ),
               (REG_OFFSET_USR + 10,),
               (REG_OFFSET_USR + 12,),
               (REG_OFFSET_USR + 11,),
               (REG_OFFSET_USR + 13,),
               (REG_OFFSET_USR + 14,),
               (None,),
               (REG_OFFSET_FIQ + 8, ),
               (REG_OFFSET_FIQ + 9, ),
               (REG_OFFSET_FIQ + 10,),
               (REG_OFFSET_FIQ + 11,),
               (REG_OFFSET_FIQ + 12,),
               (REG_OFFSET_FIQ + 13,),
               (REG_OFFSET_FIQ + 14,),
               (None,),
               (REG_OFFSET_IRQ + 14,),
               (REG_OFFSET_IRQ + 13,),
               (REG_OFFSET_SVC + 14,),
               (REG_OFFSET_SVC + 13,),
               (REG_OFFSET_ABT + 14,),
               (REG_OFFSET_ABT + 13,),
               (REG_OFFSET_UND + 14,),
               (REG_OFFSET_UND + 13,),
               (None),
               (None),
               (None),
               (None),
               (REG_OFFSET_MON + 14,),
               (REG_OFFSET_MON + 13,),
               (REG_OFFSET_HYP + 14,),
               (REG_OFFSET_HYP + 13,))

cpsh_mnems = {0: (INS_NOP, 'nop'),
              1: (INS_YIELD, 'yield'),
              2: (INS_WFE, 'wfe'),
              3: (INS_WFI, 'wfi'),
              4: (INS_SEV, 'sev')}

misc_ctl_instrs = ((INS_LEAVEX, 'leavex', False),
                   (INS_ENTERX, 'enterx', False),
                   (INS_CLREX, 'clrex', False),
                   None,
                   (INS_DSB, 'dsb', True),
                   (INS_DMB, 'dmb', True),
                   (INS_ISB, 'isb', True),
                   None)


def branch_misc(va, val, val2):  # bl and misc control
    op = (val >> 4) & 0b1111111
    op1 = (val2 >> 12) & 0b111
    op2 = (val2 >> 8) & 0b1111
    imm8 = val2 & 0b1111

    if (op1 & 0b101 == 0):
        if not (op & 0b0111000) == 0b0111000:  # T3 encoding - conditional
            cond = (val >> 6) & 0xf
            opcode, mnem, nflags, cond = bcc_ops.get(cond)
            flags = envi.IF_BRANCH | nflags

            # break down the components
            S = (val >> 10) & 1
            j1 = (val2 >> 13) & 1
            j2 = (val2 >> 11) & 1
            i1 = ~ (j1 ^ S) & 0x1
            i2 = ~ (j2 ^ S) & 0x1

            imm = (S << 24) | (i1 << 23) | (i2 << 22) | (
                (val & 0x3ff) << 12) | ((val2 & 0x7ff) << 1)

            # sign extend a 23-bit number
            if S:
                imm |= 0xff100000

            oper0 = ArmPcOffsetOper(e_bits.signed(imm, 4), va=va)
            return cond, opcode, 'b', (oper0, ), flags, 0

        if op & 0b111 == 0b011:
            # miscellaneous control instructions
            op = (val2 >> 4) & 0xf
            opcode, mnem, barrier = misc_ctl_instrs[op]

            if barrier:
                option = val2 & 0xf
                opers = (ArmBarrierOption(option),)

            else:
                opers = ()

            return COND_AL, opcode, mnem, opers, None, 0

        if imm8 & 0b100000:     # xx1xxxxx
            if (op & 0b1111110) == 0b0111000:   # MSR (banked)
                R = (val >> 4) & 1
                Rn = val & 0xf
                m = val2 & 0x10     # leave it in place
                m1 = (val2 >> 8) & 0xf
                SYSm = m1 | m

                if R:
                    spsr = proc_modes.get(SYSm)[PM_PSROFF]
                    opers = (ArmRegOper(spsr), ArmRegOper(Rn))
                else:
                    treg, = banked_regs[SYSm]
                    opers = (ArmRegOper(treg), ArmRegOper(Rn))
                return COND_AL, None, 'msr', opers, None, 0

            elif (op & 0b1111110 == 0b0111110):  # MRS (banked)
                R = (val >> 4) & 1
                Rn = val & 0xf
                m = val2 & 0x10     # leave it in place
                m1 = (val2 >> 8) & 0xf
                SYSm = m1 | m

                if R:
                    spsr = proc_modes.get(SYSm)[PM_PSROFF]
                    opers = (ArmRegOper(Rn),
                             ArmRegOper(spsr))
                else:
                    treg, = banked_regs[SYSm]
                    opers = (ArmRegOper(Rn),
                             ArmRegOper(treg))
                return COND_AL, None, 'mrs', opers, None, 0

            raise InvalidInstruction(mesg="branch_misc subsection 2",
                                     bytez=struct.pack("<H", val)+struct.pack("<H", val2),
                                     va=va-4)

        if imm8 == 0 and op == 0b0111101:
            # original imm8 was imm4!
            imm8 = val2 & 0xff
            if imm8:
                opers = (ArmRegOper(REG_PC),
                         ArmRegOper(REG_LR),
                         ArmImmOper(imm8))
                return COND_AL, None, 'sub', opers, IF_PSR_S, 0

            return COND_AL, None, 'eret', tuple(), envi.IF_RET | envi.IF_NOFALL, 0

        # xx0xxxxx and others
        if op & 0b1111110 == 0b0111000:
            tmp = op2 & 3

            Rn = val & 0xf
            mask = (val2 >> 8) & 0xf
            if not (op & 1) and tmp == 0:
                # MSR(register) p A8-498
                R = PSR_APSR

            else:   # op==0111000 and op2==01/10/11 or op==0111001
                # MSR(register) p B9-1968
                R = (val >> 4) & 1
                # System Level Only...

            opers = (ArmPgmStatRegOper(R, mask),
                     ArmRegOper(Rn))
            return COND_AL, None, 'msr', opers, None, 0

        elif op == 0b0111010:
            flags = 0

            op1 = (val2 >> 8) & 7
            op2 = val2 & 0xff
            if op1:
                opcode = INS_CPS
                mnem = 'cps'

                imod = (val2 >> 9) & 3    # enable = 0b10, disable = 0b11
                m = (val2 >> 8) & 1   # change mode
                aif = (val2 >> 5) & 7
                mode = val2 & 0x1f

                if (mode and m == 0):
                    raise Exception("CPS with invalid flags set:  UNPREDICTABLE (mode and not m)")

                if ((imod & 2) and not (aif)) or (not (imod & 2) and (aif)):
                    raise Exception("CPS with invalid flags set:  UNPREDICTABLE imod enable but not a/i/f")

                if not (imod or m):
                    # hint
                    mnem = "CPS Hint"

                if imod & 2:
                    opers = [
                        ArmCPSFlagsOper(aif)    # if mode is set...
                    ]
                    flags |= (IF_IE, IF_ID)[imod & 1]

                else:
                    opers = []
                if m:
                    opers.append(ArmImmOper(mode))

            else:
                opcode, mnem = cpsh_mnems.get(op2, (INS_HINT, 'dbg'))
                opers = []

            return COND_AL, opcode, mnem, opers, flags, 0

        elif op == 0b0111100:
            raise Exception("FIXME:  BXJ p A8-352")

        # subs PC, LR, #imm (see special case ERET above)...
        elif op == 0b0111101:
            imm8 = val2 & 0xff
            opers = (ArmRegOper(REG_PC),
                     ArmRegOper(REG_LR),
                     ArmImmOper(imm8))
            return COND_AL, None, 'sub', opers, IF_PSR_S, 0

        elif op == 0b0111110:
            Rd = (val2 >> 8) & 0xf
            opers = (ArmRegOper(Rd),
                     ArmPgmStatRegOper(PSR_CPSR),)
            return COND_AL, None, 'mrs', opers, None, 0

        elif op == 0b0111111:
            Rd = (val2 >> 8) & 0xf
            R = (val >> 4) & 1
            opers = (ArmRegOper(Rd),
                     ArmPgmStatRegOper(R))

            return COND_AL, None, 'mrs', opers, None, 0

        elif op == 0b1111110:
            if op1 == 0:
                imm4 = val & 0xf
                imm12 = val2 & 0xfff
                oper0 = ArmImmOper((imm4 << 12) | imm12)
                return COND_AL, None, 'hvc', (oper0,), None, 0

            raise InvalidInstruction(mesg="branch_misc subsection 1",
                                     bytez=struct.pack("<HH", val, val2),
                                     va=va-4)

        elif op == 0b1111111:
            if op1 == 0:
                imm4 = val & 0xf
                oper0 = ArmImmOper(imm4)
                return COND_AL, None, 'smc', (oper0,), None, 0

            raise InvalidInstruction(mesg="branch_misc subsection 1",
                                     bytez=struct.pack("<HH", val, val2),
                                     va=va-4)

        raise InvalidInstruction(mesg="branch_misc subsection 3",
                                 bytez=struct.pack("<H", val)+struct.pack("<H", val2),
                                 va=va-4)

    elif op1 & 0b101 == 1:  # T4 encoding
        opcode = INS_B
        flags = envi.IF_BRANCH | IF_THUMB32 | envi.IF_NOFALL

        # need next two bytes
        S = (val >> 10) & 1
        j1 = (val2 >> 13) & 1
        j2 = (val2 >> 11) & 1
        i1 = not (j1 ^ S)
        i2 = not (j2 ^ S)

        imm = (S << 20) | (i1 << 18) | (i2 << 19) | (
            (val & 0x3f) << 12) | ((val2 & 0x7ff) << 1)

        # sign extend a 20-bit number
        if S:
            imm |= 0xfff00000

        oper0 = ArmPcOffsetOper(e_bits.signed(imm, 4), va=va)
        return COND_AL, opcode, 'b', (oper0, ), flags, 0

    elif op1 == 0b010:
        if op == 0b1111111:
            flags = 0
            imm4 = val & 0xf
            imm12 = val2 & 0xfff
            immval = (imm4 << 12) | imm12
            oper0 = ArmImmOper(immval)
            return COND_AL, INS_UDF, 'udf', (oper0, ), flags, 0

        raise InvalidInstruction(mesg="branch_misc subsection 6",
                                 bytez=struct.pack("<H", val)+struct.pack("<H", val2),
                                 va=va-4)

    elif op1 & 0b100:
        # bl/blx
        notx = (val2 >> 12) & 1
        s = (val >> 10) & 1
        mnem = ('blx', 'bl')[notx]
        opcode = (INS_BLX, INS_BL)[notx]
        flags = envi.IF_CALL | IF_W

        # need next two bytes
        j1 = not ((val2 >> 13) & 1 ^ s)
        j2 = not ((val2 >> 11) & 1 ^ s)

        imm = (s << 24) | (j1 << 23) | (j2 << 22) | ((val & 0x3ff) << 12) | ((val2 & 0x7ff) << 1)

        # sign extend a 25-bit number
        if s:
            imm |= 0xff000000

        vamask = (0xfffffffc,
                  0xfffffffe)

        va &= vamask[notx]

        oper0 = ArmPcOffsetOper(e_bits.signed(imm, 4), va=va)

        return COND_AL, opcode, mnem, (oper0, ), flags, 0

    raise InvalidInstruction(mesg="branch_misc Branches and Miscellaneous Control: Failed to match",
                             bytez=struct.pack("<H", val)+struct.pack("<H", val2),
                             va=va-4)


def pc_imm11(va, value):  # b
    imm = e_bits.bsign_extend(((value & 0x7ff) << 1), 12, 32)
    imm = e_bits.signed(imm, 4)
    oper0 = ArmPcOffsetOper(imm, va=va)
    return COND_AL, (oper0,), None


def pc_imm8(va, value):  # b
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 2
    cond = (value >> 8) & 0xf
    oper0 = ArmPcOffsetOper(imm, va=va)
    return cond, (oper0,), None


def ldmia(va, value):
    rd = shmaskval(value, 8, 0x7)
    reg_list = value & 0xff
    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegListOper(reg_list)
    oper0.oflags |= OF_W
    return COND_AL, (oper0, oper1), None


def sp_sp_imm7(va, value):
    imm = shmaskval(value, 0, 0x7f)
    o0 = ArmRegOper(REG_SP)
    o1 = ArmRegOper(REG_SP)
    o2 = ArmImmOper(imm*4)
    return COND_AL, (o0, o1, o2), None


def rm_reglist(va, value):
    rm = shmaskval(value, 8, 0x7)
    reglist = value & 0xff
    oper0 = ArmRegOper(rm, va=va)
    oper1 = ArmRegListOper(reglist)
    oper0.oflags |= OF_W
    return COND_AL, (oper0, oper1), None


def pop_reglist(va, value):
    flags = 0
    reglist = (value & 0xff) | ((value & 0x100) << 7)
    oper0 = ArmRegListOper(reglist)
    if reglist & 0x8000:
        flags |= envi.IF_NOFALL | envi.IF_RET

    return COND_AL, (oper0,), flags


def push_reglist(va, value):
    reglist = (value & 0xff) | ((value & 0x100) << 6)
    oper0 = ArmRegListOper(reglist)
    return COND_AL, (oper0,), None


def imm5_rm_rd(va, value):
    rd = value & 0x7
    rm = (value >> 3) & 0x7
    imm5 = (value >> 6) & 0x1f

    stype = value >> 11

    if imm5 == 0:
        imm5 = 0x20

    oper0 = ArmRegOper(rd, va)
    oper1 = ArmRegOper(rm, va)
    oper2 = ArmImmOper(imm5)
    return COND_AL, (oper0, oper1, oper2), None


def i_imm5_rn(va, value):
    imm5 = shmaskval(value, 3, 0x40) | shmaskval(value, 2, 0x3e)
    rn = value & 0x7
    oper0 = ArmRegOper(rn, va)
    oper1 = ArmPcOffsetOper(imm5, va)
    return COND_AL, (oper0, oper1,), None


def ldm16(va, value):
    raise Exception("32bit wrapping of 16bit instruction... and it's not implemented")


def cps16(va, value):
    im = (value >> 4) & 1
    aif = value & 0x7

    opers = (
        ArmCPSFlagsOper(aif),
    )
    return COND_AL, opers, (IF_IE, IF_ID)[im]


it_hints_others = (
    (INS_NOP,   'nop'),
    (INS_YIELD, 'yield'),
    (INS_WFR,   'wfr'),
    (INS_WFI,   'wfi'),
    (INS_SEV,   'sev'),
)


def it_hints(va, val):
    mask = val & 0xf
    firstcond = (val >> 4) & 0xf
    if mask != 0:
        # this is the IT instruction
        itoper = ThumbITOper(mask, firstcond)
        count, cond, data = itoper.getCondData()
        nextfew = it_strs[count][data]
        mnem = 'it' + nextfew   # as much as it pains me to strcat here.

        return COND_AL, (itoper,), 0, INS_IT, mnem

    opcode, mnem = it_hints_others[firstcond]

    return COND_AL, (), 0, opcode, mnem


it_strs_0 = ['']
it_strs_1 = ['e', 't']
it_strs_2 = ['ee', 'et', 'te', 'tt']
it_strs_3 = ['eee', 'tee', 'ete', 'tte', 'eet', 'tet', 'ett', 'ttt']
it_strs = (it_strs_0, it_strs_1, it_strs_2, it_strs_3)


class ThumbITOper(ArmOperand):
    def __init__(self, mask, firstcond):
        self.mask = mask
        self.firstcond = firstcond

    def getCondInstrCount(self):
        mask = self.mask
        for x in range(4, 0, -1):
            if mask & 1:
                break
            mask >>= 1
        return x - 1

    def getFlags(self):
        fiz = self.firstcond & 1
        flags = 1
        count = self.getCondInstrCount()
        for x in range(count):
            bit = bool(((self.mask >> (3-x)) & 1) == fiz)
            flags |= (bit << (x+1))

        return flags

    def getCondData(self):
        '''
        deprecated: 2020-06-24
        '''
        mask = self.mask
        cond = self.firstcond
        count = 0
        go = 0
        cond0 = cond & 1
        data = 0

        for idx in range(4):
            mbit = (mask >> idx) & 1
            if go:
                bit = bool(mbit == cond0)
                data <<= 1
                data |= bit
                count += 1

            if mbit:
                go = 1

        return count, self.firstcond, data

    def getITSTATEdata(self):
        '''
        this is the data to put into the ITSTATE register (1 byte of the CPSR)
        '''
        return self.firstcond, self.mask

    def repr(self, op):
        mask = self.mask

        count, cond, data = self.getCondData()

        fcond = cond_codes.get(cond)
        return "%s" % (fcond)

    def render(self, mcanv, op, idx):
        mask = self.mask

        count, cond, data = self.getCondData()

        fcond = cond_codes.get(cond)
        mcanv.addText("%s" % (fcond))

    def getOperValue(self, idx, emu=None):
        return None


def ROR_C(imm, bitcount, shift):
    m = shift % bitcount
    result = (imm >> m) | (imm << (bitcount-m))
    carry = result >> (bitcount-1)
    return result, carry


def ThumbExpandImm_C(imm4, imm8, carry):
    if imm4 & 0xc == 0:
        ducky = imm4 & 3
        if ducky == 0:
            return imm8, carry
        if ducky == 1:
            return (imm8 << 16) | imm8, carry
        if ducky == 2:
            return (imm8 << 24) | (imm8 << 8), carry
        if ducky == 3:
            return imm8 | (imm8 << 8) | (imm8 << 16) | (imm8 << 24), carry
    else:
        a = imm8 >> 7
        imm8 |= 0x80  # 1bcdefg
        off = (a | (imm4 << 1))
        return ROR_C(imm8, 32, off)


dp_secondary = (
    'tst',  # and
    None,  # bic
    'mov',  # orr
    'mvn',  # orn
    'teq',  # eor
    None,
    None,
    None,  # pkh
    'cmn',  # add
    None,  # adc
    None,  # sbc
    None,
    None,
    'cmp',  # sub
    None,
    None,
)

dp_sec_silS = (0, 4, 8, 13)
# IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
DP_SEC_PSR_S = [IF_PSR_S for x in range(17)]
for x in dp_sec_silS:
    DP_SEC_PSR_S[x] |= IF_PSR_S_SIL


def dp_mod_imm_32(va, val1, val2):
    if val2 & 0x8000:
        return branch_misc(va, val1, val2)

    flags = IF_THUMB32
    Rd = (val2 >> 8) & 0xf
    S = (val1 >> 4) & 1

    Rn = val1 & 0xf

    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    imm4 = imm3 | (i << 3)
    const = (val2 & 0xff)

    dpop = (val1 >> 5) & 0xf

    const, carry = ThumbExpandImm_C(imm4, const, 0)

    if Rd == 15 and S:
        #raise Exception("dp_mod_imm_32 - FIXME: secondary dp encoding")
        mnem = dp_secondary[dpop]
        if mnem is None:
            raise Exception("dp_mod_imm_32: Rd==15, S, but dpop doesn't have a secondary! va:%x, %x%x" % (va, val1, val2))

        if S:
            flags |= DP_SEC_PSR_S[dpop]
        oper1 = ArmRegOper(Rn)
        oper2 = ArmImmOper(const)
        opers = (oper1, oper2)
        return COND_AL, None, mnem, opers, flags, 0

    elif Rn == 15 and (val1 & 0xfbc0 == 0xf040):
        dpop = (val1 >> 5) & 0xf
        mnem = dp_secondary[dpop]
        if S:
            flags |= DP_SEC_PSR_S[dpop]
        oper1 = ArmRegOper(Rd)
        oper2 = ArmImmOper(const)
        opers = (oper1, oper2)
        return COND_AL, None, mnem, opers, flags, 0

    if S:
        flags |= IF_PSR_S

    oper0 = ArmRegOper(Rd)
    oper1 = ArmRegOper(Rn)
    oper2 = ArmImmOper(const)
    opers = (oper0, oper1, oper2)
    return COND_AL, None, None, opers, flags, 0


sxt_mnem = (
    (INS_SXTAH, 'sxtah',),
    (INS_UXTAH, 'uxtah',),
    (INS_SXTAB16, 'sxtab16',),
    (INS_UXTAB16, 'uxtab16',),
    (INS_SXTAB, 'sxtab',),
    (INS_UXTAB, 'uxtab',),
)

sxt_mnem_2 = (
    (INS_SXTH, 'sxth',),
    (INS_UXTH, 'uxth',),
    (INS_SXTB16, 'sxtb16',),
    (INS_UXTB16, 'uxtb16',),
    (INS_SXTB, 'sxtb',),
    (INS_UXTB, 'uxtb',),
)


def shift_or_ext_32(va, val1, val2):
    if (val2 & 0xf000) != 0xf000:
        raise InvalidInstruction(mesg="UNDEFINED: shift_or_ext_32: val2 & 0xf000 != 0xf000 at va 0x%x: val1:%.4x val2:%.4x" % (va, val1, val2), va=va)

    op1 = (val1 >> 4) & 0xf
    op2 = (val2 >> 4) & 0xf
    rn = (val1 & 0xf)
    rd = (val2 >> 8) & 0xf
    rm = (val2 & 0xf)
    flags = 0

    if (op1 & 0b1000):  # page 245
        if not (op2 & 0b1100):
            # parallel addition/subtraction: signed
            raise InvalidInstruction(mesg="shift_or_ext_32 implementme: parallel add/sub signed",
                                     bytez=struct.pack("<H", val1)+struct.pack("<H", val2), va=va)

        elif not (op2 & 0b1000):
            # parallel addition/subtraction: unsigned
            raise InvalidInstruction(mesg="shift_or_ext_32 implementme: parallel add/sub unsigned",
                                     bytez=struct.pack("<H", val1)+struct.pack("<H", val2),
                                     va=va)

        elif (op1 & 0b1100) == 0b1000 and (op2 & 0b1100) == 0b1000:
            # misc instructions
            raise InvalidInstruction(mesg="shift_or_ext_32 implementme: misc instructions",
                                     bytez=struct.pack("<H", val1)+struct.pack("<H", val2),
                                     va=va)

    if (op2):
        if op1 > 5:
            raise InvalidInstruction(mesg="shift_or_ext_32 parsing an unsupported instruction encoding",
                                     bytez=struct.pack("<H", val1)+struct.pack("<H", val2),
                                     va=va)

        rotate = (val2 >> 4) & 0x3

        if rn == 0xf:
            # sxth and the like
            opcode, mnem, = sxt_mnem_2[op1]
            if rotate == 0:
                opers = (ArmRegOper(rd),
                         ArmRegOper(rm))
            else:
                opers = (ArmRegOper(rd),
                         ArmRegOper(rm),
                         ArmImmOper(rotate))
        else:
            # sxtah and the like
            opcode, mnem, = sxt_mnem[op1]
            if rotate == 0:
                opers = (ArmRegOper(rd),
                         ArmRegOper(rm))
            else:
                opers = (ArmRegOper(rd),
                         ArmRegOper(rn),
                         ArmRegOper(rm),
                         ArmImmOper(rotate))

    else:
        # lsl/lsr/asr/ror
        op1 = (val1 >> 4) & 0xf
        opcode, mnem, nothing = mov_ris_ops[op1 >> 1]

        opers = (ArmRegOper(rd),
                 ArmRegOper(rn),
                 ArmRegOper(rm))

        if (op1 & 1):
            flags |= IF_PSR_S

    return COND_AL, opcode, mnem, opers, flags, 0


parallel_misc_info = (
    {
        0b000:        (INS_UADD8,   'uadd8',                IF_THUMB32),
        0b001:        (INS_UADD16,  'uadd16',              IF_THUMB32),
        0b010:        (INS_UASX,    'uasx',                  IF_THUMB32),
        0b110:        (INS_USAX,    'usax',                  IF_THUMB32),
        0b101:        (INS_USUB16,  'usub16',              IF_THUMB32),
        0b100:        (INS_USUB8,   'usub8',                IF_THUMB32),

        0b1000:        (INS_UQADD8, 'uqadd8',                IF_THUMB32),
        0b1001:        (INS_UQADD16, 'uqadd16',              IF_THUMB32),
        0b1010:        (INS_UQASX,  'uqasx',                  IF_THUMB32),
        0b1110:        (INS_UQSAX,  'uqsax',                  IF_THUMB32),
        0b1101:        (INS_UQSUB16, 'uqsub16',              IF_THUMB32),
        0b1100:        (INS_UQSUB8, 'uqsub8',                IF_THUMB32),

        0b10000:        (INS_UHADD8, 'uhadd8',                IF_THUMB32),
        0b10001:        (INS_UHADD16, 'uhadd16',              IF_THUMB32),
        0b10010:        (INS_UHASX, 'uhasx',                  IF_THUMB32),
        0b10110:        (INS_UHSAX, 'uhsax',                  IF_THUMB32),
        0b10101:        (INS_UHSUB16, 'uhsub16',              IF_THUMB32),
        0b10100:        (INS_UHSUB8, 'uhsub8',                IF_THUMB32),
    },
    {
        0b000:        (INS_SADD8, 'sadd8',                IF_THUMB32),
        0b001:        (INS_SADD16, 'sadd16',              IF_THUMB32),
        0b010:        (INS_SASX, 'sasx',                  IF_THUMB32),
        0b110:        (INS_SSAX, 'ssax',                  IF_THUMB32),
        0b101:        (INS_SSUB16, 'ssub16',              IF_THUMB32),
        0b100:        (INS_SSUB8, 'ssub8',                IF_THUMB32),

        0b1000:        (INS_QADD8, 'qadd8',                IF_THUMB32),
        0b1001:        (INS_QADD16, 'qadd16',              IF_THUMB32),
        0b1010:        (INS_QASX, 'qasx',                  IF_THUMB32),
        0b1110:        (INS_QSAX, 'qsax',                  IF_THUMB32),
        0b1101:        (INS_QSUB16, 'qsub16',              IF_THUMB32),
        0b1100:        (INS_QSUB8, 'qsub8',                IF_THUMB32),

        0b10000:        (INS_SHADD8, 'shadd8',                IF_THUMB32),
        0b10001:        (INS_SHADD16, 'shadd16',              IF_THUMB32),
        0b10010:        (INS_SHASX, 'shasx',                  IF_THUMB32),
        0b10110:        (INS_SHSAX, 'shsax',                  IF_THUMB32),
        0b10101:        (INS_SHSUB16, 'shsub16',              IF_THUMB32),
        0b10100:        (INS_SHSUB8, 'shsub8',                IF_THUMB32),
    },
    {
        0b00000:        (INS_QADD,  'qadd',                IF_THUMB32),
        0b01000:        (INS_QDADD, 'qdadd',                IF_THUMB32),
        0b10000:        (INS_QADD,  'qsub',                IF_THUMB32),
        0b11000:        (INS_QDADD, 'qdsub',                IF_THUMB32),

        0b00001:        (INS_REV,   'rev',                IF_THUMB32),
        0b01001:        (INS_REV16,   'rev16',                IF_THUMB32),
        # rd, rm
        0b10001:        (INS_RBIT,   'rbit',                IF_THUMB32),
        0b11001:        (INS_REVSH,   'revsh',                IF_THUMB32),

        # rd, rn, rm
        0b00010:        (INS_SEL,  'sel',                IF_THUMB32),
        0b00011:        (INS_CLZ,  'clz',                IF_THUMB32),

    },
)


def parallel_misc_32(va, val1, val2):

    # signed/unsigned parallel instructions
    opidx = (val1 >> 4) & 7
    opidx |= (val2 >> 1) & 0x18
    signed_misc = (val2 >> 6) & 3

    pardata = parallel_misc_info[signed_misc].get(opidx)

    if pardata is None:
        return shift_or_ext_32(va, val1, val2)

    opcode, mnem, flags = pardata
    rn = (val1 & 0xf)
    rd = (val2 >> 8) & 0xf
    rm = (val2 & 0xf)

    opers = (ArmRegOper(rd),
             ArmRegOper(rn),
             ArmRegOper(rm))

    return COND_AL, opcode, mnem, opers, flags, 0


def ubfx_32(va, val1, val2):
    if val2 & 0x8000:
        return branch_misc(va, val1, val2)

    rd = (val2 >> 8) & 0xf
    rn = val1 & 0xf
    imm3 = (val2 >> 12) & 0x7
    imm2 = (val2 >> 6) & 0x3
    widthm1 = val2 & 0x1f
    lsbit = (imm3 << 2) | imm2

    opers = (ArmRegOper(rd),
             ArmRegOper(rn),
             ArmImmOper(lsbit),
             ArmImmOper(widthm1 + 1))
    return COND_AL, None, None, opers, None, 0


def dp_bin_imm_32(va, val1, val2):  # p232
    if val2 & 0x8000:
        return branch_misc(va, val1, val2)

    flags = IF_THUMB32
    Rd = (val2 >> 8) & 0xf

    imm4 = val1 & 0xf
    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    const = val2 & 0xff

    op = (val1 >> 4) & 0x1f
    const |= (imm4 << 12) | (i << 11) | (imm3 << 8)

    oper0 = ArmRegOper(Rd)
    oper2 = ArmImmOper(const)
    opers = [oper0, oper2]

    if op in (0b00100, 0b01100):    # movw, movt
        return COND_AL, None, None, opers, 0, 0

    Rn = val1 & 0xf
    if Rn == 15 and op in (0, 0b1010):   # add/sub
        # adr
        return COND_AL, None, 'adr', opers, None, 0

    oper1 = ArmRegOper(Rn)
    opers.insert(1, oper1)

    return COND_AL, None, None, opers, flags, 0


def dp_bfi_imm_32(va, val1, val2):  # p232
    if val2 & 0x8000:
        return branch_misc(va, val1, val2)

    flags = IF_THUMB32
    Rd = (val2 >> 8) & 0xf

    imm4 = val1 & 0xf
    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    const = val2 & 0xff

    op = (val1 >> 4) & 0x1f
    const |= (imm4 << 12) | (i << 11) | (imm3 << 8)

    oper0 = ArmRegOper(Rd)
    oper2 = ArmImmOper(const)

    if op in (0b00100, 0b01100):    # movw, movt
        return COND_AL, None, None, (oper0, oper2), 0, 0

    Rn = val1 & 0xf
    if Rn == 15:
        if op in (0, 0b1010):   # add/sub
            # adr
            return COND_AL, None, 'adr', (oper0, oper2), None, 0

    oper1 = ArmRegOper(Rn)

    if op == 0b10110:
        imm2 = (val2 >> 6) & 0x3
        msb = val2 & 0x1f
        lsb = (imm3 << 2) | imm2
        width = msb - lsb + 1

        if Rn == 15:
            # bfc
            mnem = 'bfc'
            opers = (oper0, ArmImmOper(lsb), ArmImmOper(width))
        else:
            # bfi
            mnem = 'bfi'
            opers = (oper0, oper1, ArmImmOper(lsb), ArmImmOper(width))

        return COND_AL, None, mnem, opers, None, 0

    return COND_AL, None, None, (oper0, oper1, oper2), flags, 0


def ldm_reg_mode_32(va, val1, val2):
    rn = val1 & 0xf
    mode = val2 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    oper1 = ArmModeOper(mode, wback)
    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0


def ldm_reg_32(va, val1, val2):
    rn = val1 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    opers = (oper0,)
    return COND_AL, None, None, opers, None, 0


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

    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0


def pop_32(va, val1, val2):
    if val2 & 0x2000:
        raise InvalidInstruction("LDM instruction with stack indicated: 0x%x: 0x%x, 0x%x" % (va, val1, val2))
        # PC not ok on some instructions...
    oper0 = ArmRegListOper(val2)
    opers = (oper0, )
    flags = IF_THUMB32
    if val2 & 0x8000:
        flags |= envi.IF_NOFALL | envi.IF_RET

    return COND_AL, None, None, opers, flags, 0


def push_32(va, val1, val2):
    if val2 & 0x2000:
        raise InvalidInstruction("LDM instruction with stack indicated: 0x%x: 0x%x, 0x%x" % (va, val1, val2))
        # PC not ok on some instructions...
    oper0 = ArmRegListOper(val2)
    opers = (oper0, )
    return COND_AL, None, None, opers, None, 0


def strex_32(va, val1, val2):
    rn = val1 & 0xf
    rd = (val2 >> 8) & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rt, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8 << 2, va=va)

    opers = (oper0, oper1, oper2)
    flags = 0
    return COND_AL, None, None, opers, flags, 0


def ldr_32(va, val1, val2):
    bitsbits = (val1 >> 4) & 0x7
    tsize = (1, 0, 2, 2, 4, 4, 0, 0)[bitsbits]

    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm12 = val2 & 0xfff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm12, va=va, tsize=tsize)

    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0


ldrb_instrs = (
    (INS_LDR, 'ldr', IF_B | IF_THUMB32),
    (INS_LDR, 'ldr', IF_B | IF_S | IF_THUMB32),
)
memh_instrs = (
    (INS_PLD, 'pld', IF_THUMB32),
    (INS_PLI, 'pli', IF_THUMB32),
)


def ldrb_memhints_32(va, val1, val2):
    op1 = (val1 >> 7) & 3
    op2 = (val2 >> 6) & 0x3f
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf

    Sbit = op1 >> 1

    if rn == 0xf:
        if rt == 0xf:
            # PLD(literal)
            opcode, mnem, flags = memh_instrs[Sbit]
            rm = val2 & 0xf
            imm2 = (val2 >> 4) & 3
            opers = (ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va),)
            return COND_AL, opcode, mnem, opers, flags, 0

        else:
            # LDRB (literal)
            opcode, mnem, flags = ldrb_instrs[Sbit]
            imm12 = val2 & 0xfff
            opers = (ArmRegOper(rt),
                     ArmPcOffsetOper(imm12, va, tsize=1))
            return COND_AL, opcode, mnem, opers, flags, 0

    else:
        if op1 & 1:
            # ldrb (immediate):T2, ldrsb:T1
            opcode, mnem, flags = ldrb_instrs[Sbit]
            imm12 = val2 & 0xfff
            opers = (ArmRegOper(rt),
                     ArmImmOffsetOper(rn, imm12, va, tsize=1))
            return COND_AL, opcode, mnem, opers, flags, 0

        elif not op1:
            if not op2 and rt == 0xf:
                # pld/pldw (p526)
                opcode, mnem, flags = memh_instrs[Sbit]
                rm = val2 & 0xf
                imm2 = (val2 >> 4) & 3
                opers = (ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va),)
                return COND_AL, opcode, mnem, opers, flags, 0

            elif (val2 >> 11) & 1:
                # LDRB (register)
                opcode, mnem, flags = ldrb_instrs[Sbit]
                imm8 = val2 & 0xff
                pubwl = ((val2 >> 6) & 0x18) | ((val2 >> 7) & 2)
                opers = (ArmRegOper(rt),
                         # ArmImmOffsetOper(rn, imm8, va, pubwl)  # FIXME: deprecated
                         ArmImmOffsetOper(rn, imm8, va, tsize=1)
                )
                return COND_AL, opcode, mnem, opers, flags, 0

            else:
                # LDRB (register)
                opcode, mnem, flags = ldrb_instrs[Sbit]
                rm = val2 & 0xf
                imm2 = (val2 >> 4) & 3
                opers = (ArmRegOper(rt),
                         ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va, tsize=1))
                return COND_AL, opcode, mnem, opers, flags, 0

        raise envi.InvalidInstruction(mesg="ldrb_memhints_32: fall 1", va=va)

    return COND_AL, opcode, mnem, opers, flags, 0


def ldr_shift_32(va, val1, val2):
    #b11 = (val2>>11) & 1
    # if not b11:
    #    raise Exception("ldr_shift_32 parsing non-ldrb")
    bitsbits = (val1 >> 4) & 0x7
    tsize = (1, 0, 2, 2, 4, 4, 0, 0)[bitsbits]

    rn = val1 & 0xf
    rm = val2 & 0xf
    rt = (val2 >> 12) & 0xf
    imm2 = (val2 >> 4) & 3

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va=va, tsize=tsize)

    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0


def ldrex_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8 << 2, va=va, tsize=4)

    opers = (oper0, oper1)
    flags = 0
    return COND_AL, None, None, opers, flags, 0


def ldrd_imm_32(va, val1, val2):
    pubwl = (val1 >> 4) & 0x1f
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    rt2 = (val2 >> 8) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOper(rt2, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8 << 2, va=va, pubwl=pubwl, tsize=8)

    opers = (oper0, oper1, oper2)
    flags = 0
    return COND_AL, None, None, opers, flags, 0


def strexn_32(va, val1, val2):
    op3 = (val1 >> 4) & 0xf
    if (op3 & 0xc != 0x10):
        raise InvalidInstruction(mesg="strexn_32 failure",
                                 bytez=struct.pack("<HH", val, val2), va=va-4)

    tsize = op3 & 4
    mnem = ('strexb', 'strexh', None, 'strexd')[tsize]
    rn = val1 & 0xf
    rd = val2 & 0xf
    rt = (val2 >> 12) & 0xf

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rt, va=va)
    oper2 = ArmRegOper(rn, va=va)

    olist = (oper0, oper1, oper2)
    flags = 0
    return COND_AL, None, mnem, opers, flags, 0


def mla_32(va, val1, val2):
    rn = val1 & 0xf
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf
    ra = (val2 >> 12) & 0xf

    mnem = 'mla'
    opcode = INS_MLA

    opers = (ArmRegOper(rd, va=va),
             ArmRegOper(rn, va=va),
             ArmRegOper(rm, va=va),
             ArmRegOper(ra, va=va))

    return COND_AL, None, mnem, opers, None, 0


def smul_32(va, val1, val2):
    rn = val1 & 0xf
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf

    nm = (val2 >> 4) & 0x3
    opcode, mnem = ((INS_SMULBB, 'smulbb'),
                    (INS_SMULBT, 'smulbt'),
                    (INS_SMULTB, 'smultb'),
                    (INS_SMULTT, 'smultt'))[nm]

    opers = (ArmRegOper(rd, va=va),
             ArmRegOper(rn, va=va),
             ArmRegOper(rm, va=va))
    return COND_AL, opcode, mnem, opers, None, 0


smulls_info = {
    0: {0x0: (INS_SMULL, 'smull',)},
    1: {0xf: (INS_SDIV, 'sdiv',)},
    2: {0x0: (INS_UMULL, 'umull',)},
    3: {0xf: (INS_UDIV, 'udiv',)},
    4: {0x0: (INS_SMLAL, 'smlal',),
        0x8: (INS_SMLAL, 'smlalbb',),
        0x9: (INS_SMLAL, 'smlalbt',),
        0xa: (INS_SMLAL, 'smlaltb',),
        0xb: (INS_SMLAL, 'smlaltt',),
        0xc: (INS_SMLALD, 'smlald',),
        0xd: (INS_SMLALDX, 'smlaldx',)},
    5: {0xc: (INS_SMLSLD, 'smlsld',),
        0xd: (INS_SMLSLDX, 'smlsldx',)},
    6: {0x0: (INS_UMLAL, 'umlal',),
        0x6: (INS_UMAAL, 'umaal',)},
}


def smull_32(va, val1, val2):
    # TODO: does this exist in thumb?
    rn = val1 & 0xf
    rm = val2 & 0xf
    rdhi = (val2 >> 8) & 0xf
    rdlo = (val2 >> 12) & 0xf

    op1 = (val1 >> 4) & 0x7
    op2 = (val2 >> 4) & 0xf

    secondary = smulls_info.get(op1)
    if secondary is None:
        # FIXME!!!!
        raise envi.InvalidInstruction(mesg="smull invalid decode: op1 (secondary is None)",
                                      bytez=struct.pack("<HH", val1, val2),
                                      va=va-4)

    secout = secondary.get(op2)
    if secout is None:
        # FIXME!!!!
        raise envi.InvalidInstruction(mesg="smull invalid decode: op2 (secout is None)",
                                      bytez=struct.pack("<HH", val1, val2),
                                      va=va-4)

    opers = (ArmRegOper(rdhi, va=va),
             ArmRegOper(rdlo, va=va),
             ArmRegOper(rn, va=va),
             ArmRegOper(rm, va=va))
    return COND_AL, opcode, mnem, opers, None, 0


def tb_ldrex_32(va, val1, val2):
    op3 = (val2 >> 4) & 0xf

    rn = val1 & 0xf
    rm = val2 & 0xf
    rt = (val2 >> 12) & 0xf
    flags = IF_THUMB32

    if op3 & 4:  # ldrex#
        mnem = 'ldrex'
        opcode = INS_LDREX
        flags |= (IF_B, IF_H, 0, IF_D)[op3 & 3]
        tsize = [1, 2, 0, 8][op3 & 3]

        oper0 = ArmRegOper(rt, va=va)
        oper1 = ArmImmOffsetOper(rn, 0, va=va, tsize=tsize)
        opers = (oper0, oper1)

    else:       # tbb/tbh
        isH = op3 & 1
        mnem, opcode, tsize = (('tbb', INS_TBB, 1), ('tbh', INS_TBH, 2))[isH]
        flags |= envi.IF_BRANCH | envi.IF_NOFALL

        oper0 = ArmScaledOffsetOper(
            rn, rm, S_LSL, isH, va, pubwl=0x18, tsize=tsize)
        opers = (oper0,)

    return COND_AL, opcode, mnem, opers, flags, 0


mov_ris_ops = ((INS_LSL, 'lsl', 3),
               (INS_LSR, 'lsr', 3),
               (INS_ASR, 'asr', 3),
               (INS_ROR, 'ror', 3))
mov_ris_alt = ((INS_MOV, 'mov', 2),
               (INS_LSR, 'lsr', 3),
               (INS_ASR, 'asr', 3),
               (INS_RRX, 'rrx', 2))


def mov_reg_imm_shift_32(va, val1, val2):
    optype = (val2 >> 4) & 3

    # imm is made of bits ((val2>>12)&7) concat'd with ((val2>>6)&3)
    # the shifting is different to reduce the number of operations
    imm = ((val2 >> 10) & 0x1c) | ((val2 >> 6) & 3)
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf
    s = (val1 >> 4) & 1

    # there are two types of encodings, one with imm == 0
    if imm == 0:
        opcode, mnem, opcnt = mov_ris_alt[optype]
    else:
        opcode, mnem, opcnt = mov_ris_ops[optype]

    if s:
        flags = IF_PSR_S
    else:
        flags = 0

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rm, va=va)
    oper2 = ArmImmOper(imm)
    opers = (oper0, oper1, oper2)[:opcnt]

    return COND_AL, opcode, mnem, opers, flags, 0


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
                (INS_RSB, 'rsb', 3))
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
                 (INS_RSB, 'rsb', 3))
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
                 (INS_RSB, 'rsb', 3))


def dp_shift_32(va, val1, val2):
    flags = IF_THUMB32
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
            flags = IF_PSR_S

    return COND_AL, opcode, mnem, opers, flags, 0


def coproc_simd_32(va, val1, val2):
    # p249 of ARMv7-A and ARMv7-R arch ref manual, parts 2 and 3 (not top section)

    val32 = (val1 << 16) | val2
    # return armd.doDecode(va, val32, 'THUMB2', 0)            lol!  trying to leverage Arm code that just aint there!  CONSIDER: finish this, then move it into ARM, then call there....
    # FIXME: coalesce ARM/Thumb32 decoding schemes so they can use the same decoders  (ie.  they return the same things:  opcode, mnem, olist, flags)
    # NOTE: MANY THUMB2 instruction encodings model their "Always Execute" ARM equivalents.
    coproc = (val2 >> 8) & 0xf
    op1 = (val1 >> 4) & 0x3f
    op = (val2 >> 4) & 1

    iflags = 0
    simdflags = 0

    if op1 & 0b110000 == 0b110000:
        return adv_simd_32(va, val1, val2)

    if op1 & 0b111110 == 0:
        bytez = struct.pack("<HH", val1, val2)
        raise envi.InvalidInstruction(mesg="CoprocSIMD: UNDEFINED instructions",
                                      bytez=struct.pack("<HH", val, val2),
                                      va=va-4)

    if coproc & 0b1110 != 0b1010:   # apparently coproc 10 and 11 are not allowed...
        if op1 == 0b000100:
            # mcrr/mcrr2 (a8-476)
            mnem, opcode = (('mcrr', INS_MCRR), ('mcrr2', INS_MCRR2))[
                (val1 > 12) & 1]

            Rt2 = val1 & 0xf
            Rt = (val2 >> 12) & 0xf
            opc1 = (val2 >> 4) & 0xf
            CRm = val2 & 0xf

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocOpcodeOper(opc1),
                ArmRegOper(Rt, va=va),
                ArmRegOper(Rt2, va=va),
                ArmCoprocRegOper(CRm),
            )

        elif op1 == 0b000101:
            # mrrc/mrrc2 (a8-492)
            mnem, opcode = (('mrrc', INS_MRRC), ('mrrc2', INS_MRRC2))[(val1 > 12) & 1]

            Rt2 = val1 & 0xf
            Rt = (val2 >> 12) & 0xf
            opc1 = (val2 >> 4) & 0xf
            CRm = val2 & 0xf

            opers = (ArmCoprocOper(coproc),
                     ArmCoprocOpcodeOper(opc1),
                     ArmRegOper(Rt, va=va),
                     ArmRegOper(Rt2, va=va),
                     ArmCoprocRegOper(CRm))

        elif op1 & 0b100000 == 0 and not (op1 & 0b111010 == 0):
            # stc/stc2 (a8-660)
            # ldc/ldc2 immediate/literal (if Rn == 0b1111) (a8-390/392)
            mnem, opcode = (('stc', INS_STC), ('ldc', INS_LDC), ('stc2', INS_STC2), ('ldc2', INS_LDC2))[((val1 >> 11) & 2) | (op1 & 1)]

            pudwl = (val1 >> 4) & 0x1f
            Rn = (val1) & 0xf
            CRd = (val2 >> 12) & 0xf
            offset = val2 & 0xff

            if pudwl & 4:   # L
                iflags = IF_L
            else:
                iflags = 0

            opers = (ArmCoprocOper(coproc),
                     ArmCoprocRegOper(CRd),
                     ArmImmOffsetOper(Rn, offset*4, va, pubwl=pudwl))

        elif op1 & 0b110000 == 0b100000 and op == 0:
            # cdp/cdp2 (a8-356)
            opc1 = (val1 >> 4) & 0xf
            CRn = val1 & 0xf
            CRd = (val2 >> 12) & 0xf
            opc2 = (val2 >> 5) & 0x7
            CRm = val2 & 0xf
            mnem, opcode = cdp_mnem[(val1 >> 12) & 1]

            opers = (ArmCoprocOper(coproc),
                     ArmCoprocOpcodeOper(opc1),
                     ArmCoprocRegOper(CRd),
                     ArmCoprocRegOper(CRn),
                     ArmCoprocRegOper(CRm),
                     ArmCoprocOpcodeOper(opc2))

        elif op1 & 0b110000 == 0b100000 and op == 1:    # 10xxx0 and 10xxx1
            # mcr/mcr2 (a8-474)
            # mrc/mrc2 (a8-490)
            load = (val1 >> 4) & 1
            two = (val1 >> 11) & 2
            opc1 = (val1 >> 5) & 0x7
            CRn = val1 & 0xf
            Rd = (val2 >> 12) & 0xf
            opc2 = (val2 >> 5) & 0x7
            CRm = val2 & 0xf
            mnem, opcode = (('mcr', INS_MCR), ('mrc', INS_MRC), ('mcr2', INS_MCR2), ('mrc2', INS_MRC2))[load | two]

            opers = (ArmCoprocOper(coproc),
                     ArmCoprocOpcodeOper(opc1),
                     ArmRegOper(Rd, va=va),
                     ArmCoprocRegOper(CRn),
                     ArmCoprocRegOper(CRm),
                     ArmCoprocOpcodeOper(opc2))

        else:
            bytez = struct.pack("<HH", val1, val2)
            raise envi.InvalidInstruction(mesg="CoprocSIMD: Fell of the end of decoding (coproc not 0xa or 0xb",
                                          bytez=bytez,
                                          va=va)

    else:
        # coproc = 0b101x   - ARM7A/M p251
        opcode = 0
        iflags = 0
        opers = []

        if op1 & 0b110000 == 0b100000:
            if op == 0:
                # fp dp (a7-270)
                return fp_dp(va, val1, val2)

            else:
                # adv simd fp (a7-276)
                return adv_xfer_arm_ext_32(va, val1, val2)

        elif op1 & 0b111110 == 0b000100:
            # adv simd fp (A7-277)
            # 64-bit transfers between ARM core and extension registers on page A7-279

            return adv_xfer_arm_ext_64(va, val1, val2)

        elif op1 & 0b100000 == 0 and not (op1 & 0b111010 == 0):
            # extension register load/store instructions A7-274
            Rn = val1 & 0xf

            # adv simd fp (a7-272)
            tmop1 = op1 & 0b11011

            if (op1 & 0b11010) in (0b10, 0b11010):
                bytez = struct.pack("<HH", val1, val2)
                raise InvalidInstruction(mesg="INVALID ENCODING", bytez=bytez, va=va)

            l = op1 & 1  # vldm or vstm
            indiv = (op1 & 0b10010) == 0b10000

            # writeback should be handled by operand
            imm8 = (val2 & 0xff) >> 1
            imm32 = imm8 << 3

            # size = 0/1 for 32-bit and 64-bit accordingly
            # TODO: Check next three bits must be 0b101
            size = (val2 >> 8) & 1

            pudwl = op1 & 0b11111

            # starting extended register
            D = (pudwl >> 2) & 1
            Vd = val2 >> 12
            d = (Vd << 1) | D

            # vpush/vpop
            if (op1 & 0b11011) in (0b01011, 0b10010) and Rn == REG_SP:
                mnem, opcode = (('vpush', INS_VPUSH), ('vpop', INS_VPOP))[l]
                opers = (ArmExtRegListOper(d >> size, imm8, size),)

            else:
                oflags = 0

                mnemidx = l | (indiv << 1)
                mnem, opcode = (('vstm', INS_VSTM),
                                ('vldm', INS_VLDM),
                                ('vstr', INS_VSTR),
                                ('vldr', INS_VLDR))[mnemidx]
                # figure out IA/DB/etc...  and Writeback

                # inc-after or dec-before?
                ia = (pudwl >> 3) & 3       # PU determine IA/DB
                iflags |= (0, IF_IA, IF_DB, 0)[ia]

                # write-back to original reg?
                w = (pudwl >> 1) & 1
                if w:
                    oflags |= OF_W   # writeback flag for ArmRegOper

                if indiv:
                    rbase = ('s%d', 'd%d')[size]
                    VRd = rctx.getRegisterIndex(rbase % d)
                    tsize = 4 + (size*4)

                    opers = (ArmRegOper(VRd, va=va, oflags=oflags),
                             ArmImmOffsetOper(Rn, imm8, va=va, pubwl=pudwl, tsize=tsize))

                else:
                    opers = (ArmRegOper(Rn, va=va, oflags=oflags),
                             ArmExtRegListOper(d, (2*imm8) >> size, size))
        else:
            bytez = struct.pack("<HH", val1, val2)
            raise InvalidInstruction(mesg="INVALID ENCODING: coproc_advsimd_fp", bytez=bytez, va=va)

    return COND_AL, opcode, mnem, opers, iflags, simdflags


def fp_dp(va, val1, val2):
    opcode, mnem, opers, iflags, simdflags = _do_fp_dp(va, val1, val2)
    return COND_AL, opcode, mnem, opers, iflags, simdflags


def adv_simd_ldst_32(va, val1, val2):
    val = (val1 << 16) | val2
    u = (val1 >> 12) & 1
    opcode, mnem, opers, iflags, simdflags = _do_adv_simd_ldst_32(val, va, u)
    return COND_AL, opcode, mnem, opers, iflags, simdflags


def adv_simd_32(va, val1, val2):
    val = (val1 << 16) | val2
    u = (val1 >> 12) & 1
    opcode, mnem, opers, iflags, simdflags = _do_adv_simd_32(val, va, u)
    return COND_AL, opcode, mnem, opers, iflags, simdflags


def adv_xfer_arm_ext_32(va, val1, val2):
    val = (val1 << 16) | val2
    if val & 0x0f000e10 != 0x0e000a10:
        bytez = struct.pack("<I", val)
        raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_32", bytez=bytez, va=va)

    a = (val >> 21) & 7
    l = (val >> 20) & 1
    c = (val >> 8) & 1
    b = (val >> 5) & 3

    iflags = 0
    simdflags = 0
    opers = None

    if l == 0:
        if c == 0:
            if a == 0:
                # p.A8-944
                mnem, opcode = 'vmov', INS_VMOV
                rt = val2 >> 12
                vn = val1 & 0xf
                Vreg = rctx.getRegisterIndex('s%d' % vn)
                opers = (ArmRegOper(Vreg, va),
                         ArmRegOper(rt, va))
            elif a == 7:
                # p.A8-956
                mnem, opcode = 'vmsr', INS_VMSR
                fpscr = REG_FPSCR
                rt = val2 >> 12
                opers = (ArmRegOper(fpscr, va),
                         ArmRegOper(rt, va))
            else:
                bytez = struct.pack("<I", val)
                raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_32: l=0. c=0, a != (0, 7)", bytez=bytez, va=va)

        else:   # c == 1
            if (a & 0b100) == 0:
                # p.A8-940
                mnem, opcode = 'vmov', INS_VMOV
                return p_vmov_scalar(val, va)   # from the ARM code....

            else:
                if b & 2:
                    raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_32: b & 2", bytez=bytez, va=va)
                # p.A8-886
                mnem, opcode = 'vdup', INS_VDUP
                b = (val1 >> 6) & 1
                q = (val1 >> 5) & 1
                d = (val2 >> 7) & 1
                e = (val2 >> 5) & 1

                # regs = (1, 2)[bool(q)]  # not necessary until emu, and not encoding specifically here
                vd = (d << 4) | (val1 & 0xf)
                rt = val2 >> 12
                be = (b << 1) | e

                simdflags = 0
                if be == 0b00:
                    simdflags = IFS_32
                elif be == 0b01:
                    esize = IFS_16
                elif be == 0b10:
                    esize = IFS_8
                else:
                    bytez = struct.pack("<I", val)
                    raise InvalidInstruction(mesg="UNDEFINED ENCODING: adv_xfer_arm_ext_32: vdup: be=3", bytez=bytez, va=va)

                opers = (ArmRegOper(vd, va),
                         ArmRegOper(rt, va))

    else:   # l == 1
        if c == 0:
            if a == 0:
                # p.A8-944
                mnem, opcode = 'vmov', INS_VMOV
                rt = val2 >> 12
                vn = val1 & 0xf
                Vreg = rctx.getRegisterIndex('s%d' % vn)

                opers = (ArmRegOper(rt, va),
                         ArmRegOper(Vreg, va),
                )

            elif a == 7:
                # p.A8-954 & B9-2012
                mnem, opcode = 'vmrs', INS_VMRS
                fpscr = REG_FPSCR
                rt = val2 >> 12
                opers = (ArmRegOper(rt, va),
                         ArmRegOper(fpscr, va))

            else:
                bytez = struct.pack("<I", val)
                raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_32: l=1. c=0, a != (0, 7)", bytez=bytez, va=va)

        else:   # c == 1
            # p.A8-942
            mnem, opcode = 'vmov', INS_VMOV
            return p_vmov_scalar(val, va)   # from the ARM code....

    return COND_AL, opcode, mnem, opers, iflags, simdflags


def adv_xfer_arm_ext_64(va, val1, val2):
    # VMOV instruction decoding
    # except: for coprocs 10 and 11. MRRC and MCRR
    val = (val1 << 16) | val2

    if (val1 >> 12) & 0xf == 0b1111:
        bytez = struct.pack("<I", val)
        raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_64: cannot be T==1 in Thumb, or cond=0b1111 in ARM",
                                 bytez=bytez,
                                 va=va)

    op = (val2 >> 4) & 0xf
    C = (val2 >> 8) & 1

    if op & 0b1101 == 1:
        # the decoding for both directions is mostly the same
        op = (val1 >> 4) & 1

        rt2 = val1 & 0xf
        rt = (val2 >> 12) & 0xf

        vm = val2 & 0xf
        m = (val2 >> 5) & 1
        Vm = (vm << 1) | m

        if C == 0:
            # 2xARM <-> 2xSinglePrecision registers
            Vm = rctx.getRegisterIndex('s%d' % Vm)

            if op == 0:
                # from ARM to Ext regs
                opers = (ArmRegOper(Vm, va),
                         ArmRegOper(Vm + 1, va),
                         ArmRegOper(rt, va),
                         ArmRegOper(rt2, va))

            else:
                # from Ext to ARM regs
                opers = (ArmRegOper(rt, va),
                         ArmRegOper(rt2, va),
                         ArmRegOper(Vm, va),
                         ArmRegOper(Vm + 1, va))

        else:
            # 2xARM <-> 1xDoublePrecision register
            Vm = rctx.getRegisterIndex('d%d' % Vm)

            if op == 0:
                # from ARM to Ext regs
                opers = (ArmRegOper(Vm, va),
                         ArmRegOper(rt, va),
                         ArmRegOper(rt2, va))

            else:
                # from Ext to ARM regs
                opers = (ArmRegOper(rt, va),
                         ArmRegOper(rt2, va),
                         ArmRegOper(Vm, va))

    else:
        bytez = struct.pack("<I", val)
        raise InvalidInstruction(mesg="INVALID ENCODING: adv_xfer_arm_ext_64: op is not '00x1'", bytez=bytez, va=va)

    '''
    In [8]: ad.disasm(binascii.unhexlify('345b46ec'), 0, 0)
    Out[8]: vmov d9, r5, r6
    '''
    return COND_AL, INS_VMOV, 'vmov', opers, 0, 0


bcc_ops = {
    0b0000:    (INS_BCC, 'beq',  envi.IF_COND, COND_EQ),
    0b0001:    (INS_BCC, 'bne',  envi.IF_COND, COND_NE),
    0b0010:    (INS_BCC, 'bcs',  envi.IF_COND, COND_CS),
    0b0011:    (INS_BCC, 'bcc',  envi.IF_COND, COND_CC),
    0b0100:    (INS_BCC, 'bmi',  envi.IF_COND, COND_MI),
    0b0101:    (INS_BCC, 'bpl',  envi.IF_COND, COND_PL),
    0b0110:    (INS_BCC, 'bvs',  envi.IF_COND, COND_VS),
    0b0111:    (INS_BCC, 'bvc',  envi.IF_COND, COND_VC),
    0b1000:    (INS_BCC, 'bhi',  envi.IF_COND, COND_HI),
    0b1001:    (INS_BCC, 'bls',  envi.IF_COND, COND_LS),
    0b1010:    (INS_BCC, 'bge',  envi.IF_COND, COND_GE),
    0b1011:    (INS_BCC, 'blt',  envi.IF_COND, COND_LT),
    0b1100:    (INS_BCC, 'bgt',  envi.IF_COND, COND_GT),
    0b1101:    (INS_BCC, 'ble',  envi.IF_COND, COND_LE),
    0b1110:    (INS_B, 'b',      envi.IF_NOFALL, COND_AL),
}


# opinfo is:
# ( <mnem>, <operdef>, <flags> )
# operdef is:
# ( (otype, oshift, omask), ...)

thumb_base = [
    # LSL<c> <Rd>,<Rm>,#<imm5>
    ('0000000001',  (INS_LSL, 'lsl',     imm5_rm_rd, IF_PSR_S)),
    ('0000000000',  (INS_MOV, 'mov',     rm_rd, IF_PSR_S)),      # MOVS<c> <Rd>,<Rm>
    # LSL<c> <Rd>,<Rm>,#<imm5>
    ('000000001',   (INS_LSL, 'lsl',     imm5_rm_rd, IF_PSR_S)),
    # LSL<c> <Rd>,<Rm>,#<imm5>
    ('00000001',    (INS_LSL, 'lsl',     imm5_rm_rd, IF_PSR_S)),
    # LSL<c> <Rd>,<Rm>,#<imm5>
    ('0000001',     (INS_LSL, 'lsl',     imm5_rm_rd, IF_PSR_S)),
    # LSL<c> <Rd>,<Rm>,#<imm5>
    ('000001',      (INS_LSL, 'lsl',     imm5_rm_rd, IF_PSR_S)),
    # LSR<c> <Rd>,<Rm>,#<imm>
    ('00001',       (INS_LSR, 'lsr',     imm5_rm_rd, IF_PSR_S)),
    # ASR<c> <Rd>,<Rm>,#<imm>
    ('00010',       (INS_ASR, 'asr',     imm5_rm_rd, IF_PSR_S)),
    # ADD<c> <Rd>,<Rn>,<Rm>
    ('0001100',     (INS_ADD, 'add',     rm_rn_rd,   IF_PSR_S)),
    # SUB<c> <Rd>,<Rn>,<Rm>
    ('0001101',     (INS_SUB, 'sub',     rm_rn_rd,   IF_PSR_S)),
    # ADD<c> <Rd>,<Rn>,#<imm3>
    ('0001110',     (INS_ADD, 'add',     imm3_rn_rd, IF_PSR_S)),
    # SUB<c> <Rd>,<Rn>,#<imm3>
    ('0001111',     (INS_SUB, 'sub',     imm3_rn_rd, IF_PSR_S)),
    ('00100',       (INS_MOV, 'mov',     imm8_rd,    IF_PSR_S)),  # MOV<c> <Rd>,#<imm8>
    ('00101',       (INS_CMP, 'cmp',     imm8_rd,    0)),        # CMP<c> <Rn>,#<imm8>
    # ADD<c> <Rdn>,#<imm8>
    ('00110',       (INS_ADD, 'add',     imm8_rd,    IF_PSR_S)),
    # SUB<c> <Rdn>,#<imm8>
    ('00111',       (INS_SUB, 'sub',     imm8_rd,    IF_PSR_S)),
    # Data processing instructions
    ('0100000000',  (INS_AND, 'and',     rm_rdn,     IF_PSR_S)),  # AND<c> <Rdn>,<Rm>
    ('0100000001',  (INS_EOR, 'eor',     rm_rdn,     IF_PSR_S)),  # EOR<c> <Rdn>,<Rm>
    ('0100000010',  (INS_LSL, 'lsl',     rm_rdn,     IF_PSR_S)),  # LSL<c> <Rdn>,<Rm>
    ('0100000011',  (INS_LSR, 'lsr',     rm_rdn,     IF_PSR_S)),  # LSR<c> <Rdn>,<Rm>
    ('0100000100',  (INS_ASR, 'asr',     rm_rdn,     IF_PSR_S)),  # ASR<c> <Rdn>,<Rm>
    ('0100000101',  (INS_ADC, 'adc',     rm_rdn,     IF_PSR_S)),  # ADC<c> <Rdn>,<Rm>
    ('0100000110',  (INS_SBC, 'sbc',     rm_rdn,     IF_PSR_S)),  # SBC<c> <Rdn>,<Rm>
    ('0100000111',  (INS_ROR, 'ror',     rm_rdn,     IF_PSR_S)),  # ROR<c> <Rdn>,<Rm>
    ('0100001000',  (INS_TST, 'tst',     rm_rd,      0)),        # TST<c> <Rn>,<Rm>
    ('0100001001',  (INS_RSB, 'rsb',     rm_rd_imm0, IF_PSR_S)),  # RSB<c> <Rd>,<Rn>,#0
    ('0100001010',  (INS_CMP, 'cmp',     rm_rd,      0)),        # CMP<c> <Rn>,<Rm>
    ('0100001011',  (INS_CMN, 'cmn',     rm_rd,      0)),        # CMN<c> <Rn>,<Rm>
    ('0100001100',  (INS_ORR, 'orr',     rm_rdn,     IF_PSR_S)),  # ORR<c> <Rdn>,<Rm>
    # MUL<c> <Rdm>,<Rn>,<Rdm>
    ('0100001101',  (INS_MUL, 'mul',     rn_rdm,     IF_PSR_S)),
    ('0100001110',  (INS_BIC, 'bic',     rm_rdn,     IF_PSR_S)),  # BIC<c> <Rdn>,<Rm>
    ('0100001111',  (INS_MVN, 'mvn',     rm_rd,      0)),        # MVN<c> <Rd>,<Rm>
    # Special data in2tructions and branch and exchange
    ('0100010000',  (INS_ADD, 'add',     d1_rm4_rd3, 0)),        # ADD<c> <Rdn>,<Rm>
    ('0100010001',  (INS_ADD, 'add',     d1_rm4_rd3, 0)),        # ADD<c> <Rdn>,<Rm>
    ('010001001',   (INS_ADD, 'add',     d1_rm4_rd3, 0)),        # ADD<c> <Rdn>,<Rm>
    ('010001010',   (INS_CMP, 'cmp',     d1_rm4_rd3, 0)),        # CMP<c> <Rn>,<Rm>
    ('010001011',   (INS_CMP, 'cmp',     d1_rm4_rd3, 0)),        # CMP<c> <Rn>,<Rm>
    ('01000110',    (INS_MOV, 'mov',     d1_rm4_rd3, 0)),        # MOV<c> <Rd>,<Rm>
    # BX<c> <Rm>       # FIXME: check for IF_RET
    ('010001110',   (INS_BX, 'bx',      rm4_shift3, 0)),
    ('010001111',   (INS_BLX, 'blx',     rm4_shift3, envi.IF_CALL)),  # BLX<c> <Rm>
    # Load from Litera7 Pool
    ('01001',       (INS_LDR, 'ldr',     rt_pc_imm8d, 0)),       # LDR<c> <Rt>,<label>
    # Load/Stor single data item
    # STR<c> <Rt>,[<Rn>,<Rm>]
    ('0101000',     (INS_STR, 'str',     rm_rn_rt,   0)),
    # STRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101001',     (INS_STRH, 'str',    rm_rn_rt,   IF_H)),
    # STRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101010',     (INS_STRB, 'str',    rm_rn_rt,   IF_B)),
    # LDRSB<c> <Rt>,[<Rn>,<Rm>]
    ('0101011',     (INS_LDRSB, 'ldr',   rm_rn_rt,  IF_S | IF_B)),
    # LDR<c> <Rt>,[<Rn>,<Rm>]
    ('0101100',     (INS_LDR, 'ldr',     rm_rn_rt,   0)),
    # LDRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101101',     (INS_LDRH, 'ldr',    rm_rn_rt,   IF_H)),
    # LDRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101110',     (INS_LDRB, 'ldr',    rm_rn_rt,   IF_B)),
    # LDRSH<c> <Rt>,[<Rn>,<Rm>]
    ('0101111',     (INS_LDRSH, 'ldr',   rm_rn_rt,   IF_S | IF_H)),
    # STR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01100',       (INS_STR, 'str',     imm54_rn_rt, 0)),
    # LDR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01101',       (INS_LDR, 'ldr',     imm54_rn_rt, 0)),
    # STRB<c> <Rt>,[<Rn>,#<imm5>]
    ('01110',       (INS_STRB, 'str',    imm56_rn_rt, IF_B)),
    # LDRB<c> <Rt>,[<Rn>{,#<imm5>}]
    ('01111',       (INS_LDRB, 'ldr',    imm56_rn_rt, IF_B)),
    # STRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10000',       (INS_STRH, 'str',    imm55_rn_rt, IF_H)),
    # LDRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10001',       (INS_LDRH, 'ldr',    imm55_rn_rt, IF_H)),
    # STR<c> <Rt>, [<Rn>{,#<imm>}]
    ('10010',       (INS_LDR, 'str',     rd_sp_imm8d, 0)),
    # LDR<c> <Rt>, [<Rn>{,#<imm>}]
    ('10011',       (INS_LDR, 'ldr',     rd_sp_imm8d, 0)),
    # Generate PC relative address
    ('10100',       (INS_ADD, 'add',     rd_pc_imm8, 0)),        # ADD<c> <Rd>,<label>
    # Generate SP rel5tive address
    # ADD<c> <Rd>,SP,#<imm>
    ('10101',       (INS_ADD, 'add',     rd_sp_imm8, 0)),
    # Miscellaneous in6tructions
    ('1011001000',  (INS_SXTH, 'sxth',    rm_rd,      0)),       # SXTH<c> <Rd>, <Rm>
    ('1011001001',  (INS_SXTB, 'sxtb',    rm_rd,      0)),       # SXTB<c> <Rd>, <Rm>
    ('1011001010',  (INS_UXTH, 'uxth',    rm_rd,      0)),       # UXTH<c> <Rd>, <Rm>
    ('1011001011',  (INS_UXTB, 'uxtb',    rm_rd,      0)),       # UXTB<c> <Rd>, <Rm>
    ('1011010',     (INS_PUSH, 'push',    push_reglist,    0)),  # PUSH <reglist>
    # SETEND <endian_specifier>
    ('10110110010', (INS_SETEND, 'setend',  sh4_imm1,   0)),
    # CPS<effect> <iflags>
    ('10110110011', (INS_CPS, 'cps',     cps16, 0)),
    ('1011011000',  (INS_PUSH, 'push',    push_reglist,    0)),  # PUSH <reglist>
    ('101101101',   (INS_PUSH, 'push',    push_reglist,    0)),  # PUSH <reglist>
    ('10110111',    (INS_PUSH, 'push',    push_reglist,    0)),  # PUSH <reglist>
    # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10110001',    (INS_CBZ, 'cbz',     i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)),
    # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('10111001',    (INS_CBNZ, 'cbnz',    i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)),
    # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10110011',    (INS_CBZ, 'cbz',     i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)),
    # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('10111011',    (INS_CBNZ, 'cbnz',    i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)),
    ('1011101000',  (INS_REV, 'rev',     rn_rdm,     0)),  # REV Rd, Rn
    ('1011101001',  (INS_REV16, 'rev16',   rn_rdm,     0)),  # REV16 Rd, Rn
    ('1011101011',  (INS_REVSH, 'revsh',   rn_rdm,     0)),  # REVSH Rd, Rn
    ('101100000',   (INS_ADD, 'add',     sp_sp_imm7, 0)),  # ADD<c> SP,SP,#<imm>
    ('101100001',   (INS_SUB, 'sub',     sp_sp_imm7, 0)),  # SUB<c> SP,SP,#<imm>
    ('1011110',     (INS_POP, 'pop',     pop_reglist,  0)),  # POP<c> <registers>
    ('10111110',    (INS_BKPT, 'bkpt',    imm8,       0)),  # BKPT <blahblah>
    # Load / Store Mu64iple
    # LDMIA Rd!, reg_list
    ('11000',       (INS_STM, 'stm',   rm_reglist, IF_IA | IF_W)),
    # STMIA Rd!, reg_list
    ('11001',       (INS_LDM, 'ldm',   rm_reglist, IF_IA | IF_W)),
    # Conditional Bran6hes
    ('11010000',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010001',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010010',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010011',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010100',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010101',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010110',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11010111',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011000',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011001',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011010',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011011',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011100',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011101',    (INS_BCC, 'b',     pc_imm8,       envi.IF_BRANCH | envi.IF_COND)),
    ('11011110',    (INS_B, 'b',       pc_imm8,       envi.IF_BRANCH | envi.IF_NOFALL)),
    ('11011111',    (INS_BCC, 'bfukt', pc_imm8,       envi.IF_BRANCH | 0)),
    # Software Interrupt
    ('11011111',    (INS_SVC, 'svc',     imm8,       0)),  # SWI <blahblah>
    ('1011111100000000',    (INS_NOP,  'nop',   it_hints,       0)),
    ('1011111100010000',    (INS_YIELD, 'yield', it_hints,       0)),
    ('1011111100100000',    (INS_WFR,  'wfr',   it_hints,       0)),
    ('1011111100110000',    (INS_WFI,  'wfi',   it_hints,       0)),
    ('1011111101000000',    (INS_SEV,  'sev',   it_hints,       0)),
    ('10111111',            (INS_IT,   'it',    it_hints, envi.IF_COND)),
]

thumb1_extension = [
    ('11100',       (INS_B,  'b',       pc_imm11,
                     envi.IF_BRANCH | envi.IF_NOFALL)),        # B <imm11>
    ('1111',        (INS_BL, 'bl',      branch_misc,
                     envi.IF_CALL | IF_THUMB32)),   # BL/BLX <addr25>
]

# FIXME: need to take into account ThumbEE
# 32-bit Thumb instructions start with:
# 0b11101
# 0b11110
# 0b11111
thumb2_extension = [
    ('11100',       (INS_LDM, 'LDM',      ldm16,     0)),     # 16-bit instructions
    # load/store multiple (A6-235 in ARM DDI 0406C)

    # next bits shoud be: 110111000000000mode
    ('111010000000',    (INS_SRS, 'srs',    ldm_reg_mode_32,    IF_THUMB32 | IF_DB)),
    # next bits shoud be: 110111000000000mode
    ('111010000010',    (INS_SRS, 'srs',    ldm_reg_mode_32,    IF_THUMB32 | IF_DB)),
    ('111010000001',    (INS_RFE, 'rfe',    ldm_reg_32,         IF_THUMB32 | IF_DB)),
    ('111010000011',    (INS_RFE, 'rfe',    ldm_reg_32,         IF_THUMB32 | IF_DB)),

    ('111010001000',    (INS_STM, 'stm',  ldm_32,
                         IF_THUMB32 | IF_IA)),    # stm(stmia/stmea)
    ('111010001001',    (INS_LDM, 'ldm',  ldm_32,
                         IF_THUMB32 | IF_IA)),    # ldm/ldmia/ldmfd
    ('111010001010',    (INS_STM, 'stm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_IA)),    # stm(stmia/stmea)
    ('1110100010110',   (INS_LDM, 'ldm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('11101000101110',  (INS_LDM, 'ldm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('111010001011111', (INS_LDM, 'ldm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('1110100010111100', (INS_LDM, 'ldm',  ldm_32,
                          IF_THUMB32 | IF_W | IF_IA)),  # not 111101
    ('1110100010111101', (INS_POP, 'pop',  pop_32,
                          IF_THUMB32 | IF_W)),  # 111101 - pop

    ('111010010000',    (INS_STM, 'stm',  ldm_32,     IF_THUMB32)),   # stmdb/stmfd
    ('111010010001',    (INS_LDM, 'ldm',  ldm_32,     IF_THUMB32)),   # ldmdb/ldmea
    ('1110100100100',   (INS_STM, 'stm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('11101001001010',  (INS_STM, 'stm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('111010010010111', (INS_STM, 'stm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('1110100100101100', (INS_STM, 'stm',  ldm_32,
                          IF_THUMB32 | IF_W | IF_DB)),  # not 101101
    ('1110100100101101', (INS_PUSH, 'push', push_32,
                          IF_THUMB32 | IF_W)),  # 101101 - push
    ('111010010011',    (INS_LDM, 'ldm',  ldm_32,
                         IF_THUMB32 | IF_W | IF_DB)),   # ldmdb/ldmea

    ('111010011000',    (INS_SRS, 'srs',    ldm_reg_mode_32,    IF_THUMB32 | IF_IA)),
    ('111010011010',    (INS_SRS, 'srs',    ldm_reg_mode_32,    IF_THUMB32 | IF_IA)),
    ('111010011001',    (INS_RFE, 'rfe',    ldm_reg_32,         IF_THUMB32 | IF_IA)),
    ('111010011011',    (INS_RFE, 'rfe',    ldm_reg_32,         IF_THUMB32 | IF_IA)),

    # load/store dual, loAD/STORE exclusive, table branch
    ('111010000100',    (INS_STREX, 'strex',    strex_32,    IF_THUMB32)),
    ('111010000101',    (INS_LDREX, 'ldrex',    ldrex_32,    IF_THUMB32)),

    ('111010000110',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010001110',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010010100',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010010110',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010011100',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010011110',    (INS_STRD, 'strd',    ldrd_imm_32,    IF_THUMB32)),

    ('111010000111',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010001111',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010010101',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010010111',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010011101',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010011111',    (INS_LDRD, 'ldrd',    ldrd_imm_32,     IF_THUMB32)),

    ('111010001100',    (INS_STREX, 'strex',   strexn_32,       IF_THUMB32)),
    # FIXME: these are jmp tables.  mark them!
    ('111010001101',    (None,      'tb',      tb_ldrex_32,     IF_THUMB32)),

    # data-processing (shifted register)
    #('1110101',             (85,'dp_sr',    dp_shift_32,         IF_THUMB32)),
    # tst if rd=1111 and s=1
    ('11101010000',         (INS_AND, 'and',      dp_shift_32,        IF_THUMB32)),
    ('11101010001',         (INS_BIC, 'bic',      dp_shift_32,        IF_THUMB32)),

    ('1110101001000',       (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('11101010010010',      (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('111010100100110',     (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001001110',    (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001001111',    (INS_MOV, 'mov_reg_sh',
                             mov_reg_imm_shift_32,         IF_THUMB32)),  # mov_imm if rn=1111
    ('1110101001010',       (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('11101010010110',      (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('111010100101110',     (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001011110',    (INS_ORR, 'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001011111',    (INS_MOV, 'mov_reg_sh',
                             mov_reg_imm_shift_32,         IF_THUMB32)),  # mov_imm if rn=1111

    ('11101010011',         (INS_ORN, 'orn',
                             dp_shift_32,        IF_THUMB32)),  # mvn if rn=1111
    # teq if rd=1111 and s=1
    ('11101010100',         (INS_EOR, 'eor',      dp_shift_32,        IF_THUMB32)),
    ('11101010110',         (INS_PKH, 'pkh',      dp_shift_32,        IF_THUMB32)),
    # cmn if rd=1111 and s=1
    ('11101011000',         (INS_ADD, 'add',      dp_shift_32,        IF_THUMB32)),
    ('11101011010',         (INS_ADC, 'adc',      dp_shift_32,        IF_THUMB32)),
    ('11101011011',         (INS_SBC, 'sbc',      dp_shift_32,        IF_THUMB32)),
    # cmp if rd=1111 and s=1
    ('11101011101',         (INS_SUB, 'sub',      dp_shift_32,        IF_THUMB32)),
    ('11101011110',         (INS_RSB, 'rsb',      dp_shift_32,        IF_THUMB32)),

    # coproc, adv simd, fp-instrs #ed9f 5a31
    ('11101100',            (IENC_COPROC_SIMD,
                             'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101101',            (IENC_COPROC_SIMD,
                             'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101110',            (IENC_COPROC_SIMD,
                             'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101111',            (IENC_ADVSIMD, 'adv simd', adv_simd_32,        IF_THUMB32)),
    ('1111110',             (IENC_COPROC_SIMD,
                             'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('111110010000',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110010010',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110010100',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110010110',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110011000',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110011010',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110011100',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('111110011110',        (IENC_ADVSIMD, 'adv simd ld/st',
                             adv_simd_ldst_32,        IF_THUMB32)),
    ('11111110',            (IENC_COPROC_SIMD,
                             'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11111111',            (IENC_ADVSIMD, 'adv simd', adv_simd_32,        IF_THUMB32)),

    # data-processing (modified immediate) (branches mostly redirected from dp_mod_imm_32)
    # tst if rd=1111 and s=1
    ('11110000000',         (INS_AND, 'and',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000001',         (INS_BIC, 'bic',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000010',         (INS_ORR, 'orr',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000011',         (INS_ORN, 'orn',
                             dp_mod_imm_32,      IF_THUMB32)),  # mvn if rn=1111
    # teq if rd=1111 and s=1
    ('11110000100',         (INS_EOR, 'eor',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000110',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    # cmn if rd=1111 and s=1
    ('11110001000',         (INS_ADD, 'add',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001001',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    ('11110001010',         (INS_ADC, 'adc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001011',         (INS_SBC, 'sbc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001100',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    # cmp if rd=1111 and s=1
    ('11110001101',         (INS_SUB, 'sub',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001110',         (INS_RSB, 'rsb',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001111',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    # skip 1111001* - see data processing below.
    # tst if rd=1111 and s=1
    ('11110100000',         (INS_AND, 'and',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100001',         (INS_BIC, 'bic',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100010',         (INS_ORR, 'orr',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100011',         (INS_ORN, 'orn',
                             dp_mod_imm_32,      IF_THUMB32)),  # mvn if rn=1111
    # teq if rd=1111 and s=1
    ('11110100100',         (INS_EOR, 'eor',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100101',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    ('11110100110',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    ('11110100111',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    # cmn if rd=1111 and s=1
    ('11110101000',         (INS_ADD, 'add',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101001',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    ('11110101010',         (INS_ADC, 'adc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101011',         (INS_SBC, 'sbc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101100',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary
    # cmp if rd=1111 and s=1
    ('11110101101',         (INS_SUB, 'sub',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101110',         (INS_RSB, 'rsb',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101111',         (INS_BLX, 'blx',
                             branch_misc,        IF_THUMB32)),    # necessary

    # data processing (plain binary immediate)
    ('1111001000',          (INS_ADD, 'add',
                             dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111001001',          (INS_MOVW, 'movw',    dp_bin_imm_32,      IF_THUMB32)),
    ('1111001010',          (INS_SUB, 'sub',
                             dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111001011',          (INS_MOVT, 'movt',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110011000',         (INS_SSAT, 'ssat',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110011001',         (INS_SSAT16, 'ssat16', dp_bin_imm_32,      IF_THUMB32)),
    ('11110011010',         (INS_SBFX, 'sbfx',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110011011',         (INS_BFI, 'bfi',
                             dp_bfi_imm_32,      IF_THUMB32)),  # bfc if rn=1111
    ('11110011100',         (INS_USAT, 'usat',    dp_bin_imm_32,      IF_THUMB32)),
    # usat16 if val2=0000xxxx00xxxxxx
    ('111100111010',        (INS_USAT, 'usat',    dp_bin_imm_32,      IF_THUMB32)),
    # usat16 if val2=0000xxxx00xxxxxx
    ('111100111011',        (INS_USAT, 'usat',    dp_bin_imm_32,      IF_THUMB32)),
    ('1111001111',          (INS_UBFX, 'ubfx',    ubfx_32,            IF_THUMB32)),
    ('1111011000',          (INS_ADD, 'add',
                             dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111011001',          (INS_MOVW, 'movw',    dp_bin_imm_32,      IF_THUMB32)),
    ('1111011010',          (INS_SUB, 'sub',
                             dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111011011',          (INS_MOVT, 'movt',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110111000',         (INS_SSAT, 'ssat',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110111001',         (INS_SSAT16, 'ssat16', dp_bin_imm_32,      IF_THUMB32)),
    ('11110111010',         (INS_SBFX, 'sbfx',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110111011',         (INS_BFI, 'bfi',
                             dp_bfi_imm_32,      IF_THUMB32)),  # bfc if rn=1111
    ('11110111100',         (INS_USAT, 'usat',    dp_bin_imm_32,      IF_THUMB32)),
    # usat16 if val2=0000xxxx00xxxxxx
    ('11110111101',         (INS_USAT, 'usat',    dp_bin_imm_32,      IF_THUMB32)),
    ('11110111110',         (INS_UBFX, 'ubfx',    ubfx_32,            IF_THUMB32)),
    ('11110111111',         (None, 'branchmisc',
                             branch_misc,        IF_THUMB32)),    # necessary

    # stores, loads, etc...
    ('111110000000',        (INS_STR, 'str', ldr_shift_32,        IF_B | IF_THUMB32)),
    ('111110000001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110000010',        (INS_STR,  'str',  ldr_shift_32,      IF_H | IF_THUMB32)),
    ('111110000011',        (INS_LDR,  'ldr',  ldr_shift_32,      IF_H | IF_THUMB32)),
    ('111110000100',        (INS_STR,  'str',
                             ldr_shift_32,      IF_THUMB32)),   # T4 encoding
    ('111110000101',        (INS_LDR,  'ldr',
                             ldr_shift_32,      IF_THUMB32)),   # T4 encoding
    ('111110001000',        (INS_STR, 'str', ldr_32,            IF_B | IF_THUMB32)),
    ('111110001001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110001010',        (INS_STR, 'str', ldr_32,            IF_H | IF_THUMB32)),
    ('111110001011',        (INS_LDR, 'ldr', ldr_32,            IF_H | IF_THUMB32)),
    ('111110001100',        (INS_STR,  'str',  ldr_32,      IF_THUMB32)),
    ('111110001101',        (INS_LDR,  'ldr',  ldr_32,          IF_THUMB32)),  # T3
    ('111110010001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110011001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110011011',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    # see adv simd as well

    # data-processing (register)
    ('111110100',           (None, 'shift_or_extend', shift_or_ext_32,   IF_THUMB32)),
    ('111110101',           (None, 'parallel_misc', parallel_misc_32,   IF_THUMB32)),

    # multiply/mul-accumulate/absdiff
    ('111110110000',        (INS_MLA,  'mla',  mla_32,          IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110110001',        (INS_SMUL, 'smul', smul_32,         IF_THUMB32)),

    # long multiply/long mul-accumulate/divide
    # stopped on page 249 of ARM A and M
    ('111110111000',        (INS_SMULL, 'smull', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111001',        (INS_SDIV, 'sdiv', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111010',        (INS_UMULL, 'umull', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111011',        (INS_UDIV, 'udiv', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111100',        (INS_SMLAL, 'smlal', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111101',        (INS_SMLSLD, 'smlsld', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111110',        (INS_UMLAL, 'umlal', smull_32,         IF_THUMB32)),
    # stopped on page 249 of ARM A and M
    ('111110111111',        (INS_SMULL, 'smull', smull_32,         IF_THUMB32)),

    ('11100',               (INS_B,  'b',       pc_imm11,
                             envi.IF_BRANCH | envi.IF_NOFALL)),        # B <imm11>
]


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


class Thumb16Opcode(ArmOpcode):
    _def_arch = envi.ARCH_THUMB16
    pass


class ThumbOpcode(ArmOpcode):
    _def_arch = envi.ARCH_THUMB
    pass


class ThumbDisasm:
    _tree = ttree2
    _optype = envi.ARCH_THUMB
    _opclass = ThumbOpcode

    def __init__(self, doModeSwitch=True, endian=envi.ENDIAN_LSB):
        self._doModeSwitch = doModeSwitch
        self.setEndian(endian)

    def setEndian(self, endian):
        self.endian = endian
        self.hfmt = ("<H", ">H")[endian]

    def getEndian(self):
        return self.endian

    def disasm(self, bytez, offset, va, trackMode=True):
        oplen = None
        flags = 0
        simdflags = 0
        va &= -2
        offset &= -2
        val, = struct.unpack_from(self.hfmt, bytez, offset)

        try:
            opcode, mnem, opermkr, flags = self._tree.getInt(val, 16)
        except TypeError:
            raise envi.InvalidInstruction(mesg="disasm parser cannot find instruction",
                                          bytez=bytez[offset:offset+2],
                                          va=va)

        if flags & IF_THUMB32:
            val2, = struct.unpack_from(self.hfmt, bytez, offset+2)
            cond, nopcode, nmnem, olist, nflags, simdflags = opermkr(va+4, val, val2)

            if nmnem is not None:   # allow opermkr to set the mnem
                mnem = nmnem
                opcode = nopcode
            if nflags is not None:
                flags = nflags
            oplen = 4

        else:
            opnuggets = opermkr(va+4, val)
            if len(opnuggets) == 5:
                cond, olist, nflags, opcode, mnem = opnuggets
            else:
                cond, olist, nflags = opnuggets

            if nflags is not None:
                flags = nflags
            oplen = 2

        # since our flags determine how the instruction is decoded later....
        # performance-wise this should be set as the default value instead of 0, but this is cleaner
        if not (flags & envi.ARCH_MASK):
            flags |= self._optype

        if (olist is not None and len(olist) and isinstance(olist[0], ArmRegOper) and olist[0].involvesPC() and opcode not in no_update_Rd):

            showop = True
            flags |= envi.IF_NOFALL

        if mnem is None or type(mnem) == int:
            raise Exception("mnem == %r!  0x%xi (thumb)" % (mnem, opval))

        op = ThumbOpcode(va, opcode, mnem, cond, oplen,
                         olist, flags, simdflags)
        return op


class Thumb16Disasm(ThumbDisasm):
    _tree = ttree
    _optype = envi.ARCH_THUMB16
    _opclass = Thumb16Opcode


if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain(Thumb16Disasm())
