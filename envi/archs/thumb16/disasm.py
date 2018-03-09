import envi.bits as e_bits
import envi.bintree as e_btree

from envi.bits import binary
from envi import InvalidInstruction

from envi.archs.arm.disasm import *
armd = ArmDisasm()

#thumb_32 = [
        #binary('11101'),
        #binary('11110'),
        #binary('11111'),
#]

#FIXME: check to make sure ldrb/ldrh are handled consistently, wrt: IF_B and IF_H.  emulation would like all the same.



O_REG = 0
O_IMM = 1
O_OFF = 2

OperType = (
    ArmRegOper,
    ArmImmOper,
    ArmPcOffsetOper,
    )
def shmaskval(value, shval, mask):  #FIXME: unnecessary to make this another fn call.  will be called a bajillion times.
    return (value >> shval) & mask

class simpleops:
    def __init__(self, *operdef):
        self.operdef = operdef

    def __call__(self, va, value):
        ret = []
        for otype, shval, mask in self.operdef:
            oval = shmaskval(value, shval, mask)
            oper = OperType[otype]((value >> shval) & mask, va=va)
            ret.append( oper )
        return COND_AL, (ret), None

#imm5_rm_rd  = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 6, 0x1f))
rm_rn_rd    = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_REG, 6, 0x7))
imm3_rn_rd  = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 6, 0x7))
imm8_rd     = simpleops((O_REG, 8, 0x7), (O_IMM, 0, 0xff))
rm_rd       = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rn_rdm      = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rdn      = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7))
rm_rd_imm0  = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_IMM, 0, 0))
rm4_shift3  = simpleops((O_REG, 3, 0xf))
rm_rn_rt    = simpleops((O_REG, 0, 0x7), (O_REG, 3, 0x7), (O_REG, 6, 0x7))
imm8        = simpleops((O_IMM, 8, 0xff))
#imm11       = simpleops((O_IMM, 11, 0x7ff))

sh4_imm1    = simpleops((O_IMM, 3, 0x1))

def d1_rm4_rd3(va, value):
    # 0 1 0 0 0 1 0 0 DN(1) Rm(4) Rdn(3)
    rdbit = shmaskval(value, 4, 0x8)
    rd = shmaskval(value, 0, 0x7) + rdbit
    rm = shmaskval(value, 3, 0xf)
    return COND_AL,(ArmRegOper(rd, va=va),ArmRegOper(rm, va=va)), None

def rm_rn_rt(va, value):
    rt = shmaskval(value, 0, 0x7) # target
    rn = shmaskval(value, 3, 0x7) # base
    rm = shmaskval(value, 6, 0x7) # offset
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOffsetOper(rn, rm, va, pubwl=0x18)
    return COND_AL,(oper0,oper1), None

def imm54_rn_rt(va, value):
    imm = shmaskval(value, 4, 0x7c)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return COND_AL,(oper0,oper1), None

def imm55_rn_rt(va, value):
    imm = shmaskval(value, 5, 0x3e)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return COND_AL,(oper0,oper1), None

def imm56_rn_rt(va, value):
    imm = shmaskval(value, 6, 0x1f)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return COND_AL,(oper0,oper1), None

def rd_sp_imm8(va, value): # add
    rd = shmaskval(value, 8, 0x7)
    imm = shmaskval(value, 0, 0xff) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOffsetOper(REG_SP, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return COND_AL,(oper0,oper1), None

def rd_pc_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOper((va&0xfffffffc) + 4 + imm)
    return COND_AL,(oper0,oper1), None

def rt_pc_imm8(va, value): # ldr
    rt = shmaskval(value, 8, 0x7)
    imm = e_bits.unsigned((value & 0xff), 1) << 2
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(REG_PC, imm, (va&0xfffffffc))
    return COND_AL,(oper0,oper1), None


banked_regs = (
        ( REG_OFFSET_USR + 8, ),
        ( REG_OFFSET_USR + 9, ),
        ( REG_OFFSET_USR + 10,),
        ( REG_OFFSET_USR + 12,),
        ( REG_OFFSET_USR + 11,),
        ( REG_OFFSET_USR + 13,),
        ( REG_OFFSET_USR + 14,),
        ( None,),
        ( REG_OFFSET_FIQ + 8, ),
        ( REG_OFFSET_FIQ + 9, ),
        ( REG_OFFSET_FIQ + 10,),
        ( REG_OFFSET_FIQ + 11,),
        ( REG_OFFSET_FIQ + 12,),
        ( REG_OFFSET_FIQ + 13,),
        ( REG_OFFSET_FIQ + 14,),
        ( None,),
        ( REG_OFFSET_IRQ + 14, ),
        ( REG_OFFSET_IRQ + 13, ),
        ( REG_OFFSET_SVC + 14,),
        ( REG_OFFSET_SVC + 13,),
        ( REG_OFFSET_ABT + 14,),
        ( REG_OFFSET_ABT + 13,),
        ( REG_OFFSET_UND + 14,),
        ( REG_OFFSET_UND + 13,),
        ( None ),
        ( None ),
        ( None ),
        ( None ),
        ( REG_OFFSET_MON + 14,),
        ( REG_OFFSET_MON + 13,),
        ( REG_OFFSET_HYP + 14,),
        ( REG_OFFSET_HYP + 13,),
        )

cpsh_mnems = {
        0: (INS_NOP, 'nop',),
        1: (INS_YIELD, 'yield',),
        2: (INS_WFE, 'wfe',),
        3: (INS_WFI, 'wfi',),
        4: (INS_SEV, 'sev',),
        }

misc_ctl_instrs = (
        (INS_LEAVEX, 'leavex', False),
        (INS_ENTERX, 'enterx', False),
        (INS_CLREX, 'clrex', False),
        None,
        (INS_DSB, 'dsb', True),
        (INS_DMB, 'dmb', True),
        (INS_ISB, 'isb', True),
        None,
)


def branch_misc(va, val, val2): # bl and misc control
    op = (val >> 4) & 0b1111111
    op1 = (val2 >> 12) & 0b111
    op2 = (val2 >> 8) & 0b1111
    imm8 = val2 & 0b1111
    
    if (op1 & 0b101 == 0):
        if not (op & 0b0111000) == 0b0111000: # T3 encoding - conditional
            cond = (val>>6) & 0xf
            opcode, mnem, nflags, cond = bcc_ops.get(cond)
            flags = envi.IF_BRANCH | nflags
            
            # break down the components
            S = (val>>10)&1
            j1 = (val2>>13)&1
            j2 = (val2>>11)&1
            i1 = ~ (j1 ^ S) & 0x1
            i2 = ~ (j2 ^ S) & 0x1

            imm = (S<<24) | (i1<<23) | (i2<<22) | ((val&0x3ff) << 12) | ((val2&0x7ff) << 1)

            #sign extend a 23-bit number
            if S:
                imm |= 0xff100000

            oper0 = ArmPcOffsetOper(e_bits.signed(imm,4), va=va)
            return cond, opcode, 'b', (oper0, ), flags, 0

        if op & 0b111 == 0b011:
            # miscellaneous control instructions
            op = (val2>>4) & 0xf
            opcode, mnem, barrier = misc_ctl_instrs[op]

            if barrier:
                option = val2 & 0xf
                opers = (
                        ArmBarrierOption(option),
                        )

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
                    opers = (
                            ArmRegOper(spsr),
                            ArmRegOper(Rn),
                            )
                else:
                    treg, = banked_regs[SYSm]
                    opers = (
                            ArmRegOper(treg),
                            ArmRegOper(Rn),
                            )
                return COND_AL ,None, 'msr', opers, None, 0

            elif (op & 0b1111110 == 0b0111110): # MRS (banked)
                R = (val >> 4) & 1
                Rn = val & 0xf
                m = val2 & 0x10     # leave it in place
                m1 = (val2 >> 8) & 0xf
                SYSm = m1 | m

                if R:
                    spsr = proc_modes.get(SYSm)[PM_PSROFF]
                    opers = (
                            ArmRegOper(Rn),
                            ArmRegOper(spsr),
                            )
                else:
                    treg, = banked_regs[SYSm]
                    opers = (
                            ArmRegOper(Rn),
                            ArmRegOper(treg),
                            )
                return COND_AL, None, 'mrs', opers, None, 0

            raise InvalidInstruction(
                mesg="branch_misc subsection 2",
                bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)

        else:
            if imm8 == 0 and op == 0b0111101:
                imm8 = val2 & 0xff
                if imm8:
                    opers = (
                            ArmRegOper(REG_PC),
                            ArmRegOper(REG_LR),
                            ArmImmOper(imm8),
                            )
                    return COND_AL, None, 'sub', opers, IF_PSR_S, 0

                return COND_AL, None, 'eret', tuple(), envi.IF_RET | envi.IF_NOFALL, 0
            print "TEST ME: branch_misc subsection 3"
##### FIXME!  THIS NEEDS TO ALSO HIT MSR BELOW....
            #raise InvalidInstruction(
            #    mesg="branch_misc subsection 3",
            #    bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)

            # xx0xxxxx and others
            if op == 0b0111000:
                print "HIT"
                tmp = op2 & 3

                Rn = val & 0xf
                mask = (val2>>8) & 0xf
                if tmp == 0:
                    R = PSR_APSR
                    #raise Exception("FIXME:  MSR(register) p A8-498")

                else:
                    R = (val >> 4) & 1

                    #raise Exception("FIXME:  MSR(register) p B9-1968")
                opers = (
                        ArmPgmStatRegOper(R, mask),
                        ArmRegOper(Rn)
                        )
                return COND_AL, None, 'msr', opers, None, 0


            elif op == 0b0111001:
                # coalesce with previous
                raise Exception("FIXME:  MSR(register) p B9-1968")

            elif op == 0b0111010:
                flags = 0

                op1 = (val2>>8) & 7
                op2 = val2 & 0xff
                if op1:
                    opcode = INS_CPS
                    mnem = 'cps'

                    imod = (val2>>9) & 3    # enable = 0b10, disable = 0b11
                    m = (val2>>8) & 1   # change mode
                    aif = (val2>>5) & 7
                    mode = val2 & 0x1f

                    if (mode and m==0):
                            raise Exception("CPS with invalid flags set:  UNPREDICTABLE (mode and not m)")

                    if ((imod & 2) and not (aif)) or \
                        (not (imod & 2) and (aif)):
                            raise Exception("CPS with invalid flags set:  UNPREDICTABLE imod enable but not a/i/f")

                    if not (imod or m):
                        # hint
                        mnem = "CPS Hint...  fix me"
                        
                    if imod & 2:
                        opers = [
                            ArmCPSFlagsOper(aif)    # if mode is set...
                        ]
                        flags |= (IF_IE, IF_ID)[imod&1]

                    else:
                        opers = []
                    if m:
                        opers.append(ArmImmOper(mode))

                else:
                    opcode, mnem = cpsh_mnems.get(op2, (INS_DEBUGHINT, 'dbg'))

                #raise Exception("FIXME:  Change processor state ad hints p A6-234")
                return COND_AL, opcode, mnem, opers, flags, 0

            elif op == 0b0111011:
                raise Exception("FIXME:  Misc control instrs p A6-235")

            elif op == 0b0111100:
                raise Exception("FIXME:  BXJ p A8-352")

            elif op == 0b0111101:   # subs PC, LR, #imm (see special case ERET above)
                imm8 = val2 & 0xff
                opers = (
                        ArmRegOper(REG_PC),
                        ArmRegOper(REG_LR),
                        ArmImmOper(imm8),
                        )
                return COND_AL, None, 'sub', opers, IF_PSR_S, 0

            elif op == 0b0111110:
                Rd = (val2 >> 8) & 0xf
                opers = (
                        ArmRegOper(Rd),
                        ArmRegOper(REG_OFFSET_CPSR),
                        )
                return COND_AL, None, 'mrs', opers, None, 0

            elif op == 0b0111111:
                Rd = (val2 >> 8) & 0xf
                R = (val >> 4) & 1
                opers = (
                        ArmRegOper(Rd),
                        ArmRegOper(REG_OFFSET_CPSR),
                        )

                raise Exception("FIXME:  MRS(register) p B9-1962 - how is R used?")
                return COND_AL, None, 'mrs', opers, None, 0

            elif op == 0b1111110:
                if op1 == 0:
                    imm4 = val & 0xf
                    imm12 = val2 & 0xfff
                    oper0 = ArmImmOper((imm4<<12)|imm12)
                    return COND_AL, None, 'hvc', (oper0,), None, 0

                raise InvalidInstruction(
                    mesg="branch_misc subsection 1",
                    bytez=struct.pack("<HH", val, val2), va=va-4)


            elif op == 0b1111111:
                if op1 == 0:
                    imm4 = val & 0xf
                    oper0 = ArmImmOper(imm4)
                    return COND_AL, None, 'smc', (oper0,), None, 0

                raise InvalidInstruction(
                    mesg="branch_misc subsection 1",
                    bytez=struct.pack("<HH", val, val2), va=va-4)



    elif op1 & 0b101 == 1:  # T4 encoding
        opcode = INS_B
        flags = envi.IF_BRANCH | IF_THUMB32 | envi.IF_NOFALL

        # need next two bytes
        S = (val>>10)&1
        j1 = (val2>>13)&1
        j2 = (val2>>11)&1
        i1 = not (j1 ^ S)
        i2 = not (j2 ^ S)

        imm = (S<<20) | (i1<<18) | (i2<<19) | ((val&0x3f) << 12) | ((val2&0x7ff) << 1)

        #sign extend a 20-bit number
        if S:
            imm |= 0xfff00000

        oper0 = ArmPcOffsetOper(e_bits.signed(imm,4), va=va)
        return COND_AL, opcode, 'b', (oper0, ), flags, 0

    elif op1 == 0b010:
        if op == 0b1111111:
            raise Exception("FIXME:  UDF (permanently undefined) p B9-1972")
        raise InvalidInstruction(
            mesg="branch_misc subsection 6",
            bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)

    elif op1 & 0b100:
        # bl/blx
        notx = (val2>>12) & 1
        s = (val>>10) & 1
        mnem = ('blx','bl')[notx]
        opcode = (INS_BLX,INS_BL)[notx]
        flags = envi.IF_CALL | IF_W

        # need next two bytes
        j1 = not ((val2>>13)&1 ^ s)
        j2 = not ((val2>>11)&1 ^ s)

        imm = (s<<24) | (j1<<23) | (j2<<22) | ((val&0x3ff) << 12) | ((val2&0x7ff) << 1)

        #sign extend a 25-bit number
        if s:
            imm |= 0xff000000

        vamask = (
                0xfffffffc,
                0xfffffffe
                )

        va &= vamask[notx]

        oper0 = ArmPcOffsetOper(e_bits.signed(imm,4), va=va)

        return COND_AL, opcode, mnem, (oper0, ), flags, 0
        


    
    raise InvalidInstruction(
        mesg="branch_misc Branches and Miscellaneous Control: Failed to match",
        bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)


def pc_imm11(va, value): # b
    imm = e_bits.bsign_extend(((value & 0x7ff)<<1), 12, 32)
    imm = e_bits.signed(imm, 4)
    oper0 = ArmPcOffsetOper(imm, va=va)
    return COND_AL,(oper0,), None

def pc_imm8(va, value): # b
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 2
    cond = (value >> 8) & 0xf
    oper0 = ArmPcOffsetOper(imm, va=va)
    return cond,(oper0,), None

def ldmia(va, value): 
    rd = shmaskval(value, 8, 0x7)
    reg_list = value & 0xff
    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegListOper(reg_list)
    oper0.oflags |= OF_W
    return COND_AL,(oper0,oper1), None

def sp_sp_imm7(va, value):
    imm = shmaskval(value, 0, 0x7f)
    o0 = ArmRegOper(REG_SP)
    o1 = ArmRegOper(REG_SP)
    o2 = ArmImmOper(imm*4)
    return COND_AL,(o0,o1,o2), None

def rm_reglist(va, value):
    rm = shmaskval(value, 8, 0x7)
    reglist = value & 0xff
    oper0 = ArmRegOper(rm, va=va)
    oper1 = ArmRegListOper(reglist)
    oper0.oflags |= OF_W
    return COND_AL,(oper0,oper1), None

def pop_reglist(va, value):
    flags = 0
    reglist = (value & 0xff) | ((value & 0x100)<<7)
    oper0 = ArmRegListOper(reglist)
    if reglist & 0x8000:
        flags |= envi.IF_NOFALL | envi.IF_RET
    
    return COND_AL,(oper0,), flags

def push_reglist(va, value):
    reglist = (value & 0xff) | ((value & 0x100)<<6)
    oper0 = ArmRegListOper(reglist)
    return COND_AL,(oper0,), None

def imm5_rm_rd(va, value):
    rd = value & 0x7
    rm = (value >> 3) & 0x7
    imm5 = (value >> 6) & 0x1f

    stype = value >> 11

    oper0 = ArmRegOper(rd, va)
    oper1 = ArmRegOper(rm, va)
    oper2 = ArmImmOper(imm5)
    return COND_AL,(oper0, oper1, oper2), None


def i_imm5_rn(va, value):
    imm5 = shmaskval(value, 3, 0x40) | shmaskval(value, 2, 0x3e)
    rn = value & 0x7
    oper0 = ArmRegOper(rn, va)
    oper1 = ArmPcOffsetOper(imm5, va)
    return COND_AL,(oper0, oper1,), None

def ldm16(va, value):
    raise Exception("32bit wrapping of 16bit instruction... and it's not implemented")

def cps16(va, value):
    im = (value>>4) & 1
    aif = value & 0x7
    
    opers = (
            ArmCPSFlagsOper(aif),
            )
    return COND_AL,opers, (IF_IE, IF_ID)[im]

def itblock(va, val):
    mask = val & 0xf
    firstcond = (val>>4) & 0xf
    return COND_AL,(ThumbITOper(mask, firstcond),), None

class ThumbITOper(ArmOperand):
    def __init__(self, mask, firstcond):
        self.mask = mask
        self.firstcond = firstcond

    def repr(self, op):
        mask = self.mask
        cond = self.firstcond

        fcond = cond_codes.get(cond)

        itbytes = []

        go = 0
        cond0 = cond & 1
        for idx in range(4):
            mbit = (mask>>idx) & 1
            if go:
                if mbit == cond0:
                    itbytes.append('t')
                else:
                    itbytes.append('e')

            if mbit: 
                go = 1
        nextfew = ''.join(itbytes)
        return "%s %s" % (nextfew, fcond)

    def render(self, mcanv, op, idx):
        mask = self.mask
        cond = self.firstcond

        fcond = cond_codes.get(cond)

        itbytes = []

        go = 0
        cond0 = cond & 1
        for idx in range(4):
            mbit = (mask>>idx) & 1
            if go:
                if mbit == cond0:
                    itbytes.append('t')
                else:
                    itbytes.append('e')

            if mbit: 
                go = 1

        nextfew = ''.join(itbytes)
        mcanv.addText("%s %s" % (nextfew, fcond))

    def getOperValue(self, idx, emu=None):
        return None

'''
def thumb32_01(va, val, val2):
    op =  (val2>>15)&1
    op2 = (val>>4) & 0x7f
    op1 = (val>>11) & 0x3
    flags = 0
    
    if (op2 & 0x64) == 0:
        raise Exception('# Load/Store Multiples')
        op3 = (val>>7) & 3
        W = (val>>5)&1
        L = (val>>4)&1
        mode = (val&0xf)

        mnem, opcode = (('srs', INS_SRS), ('rfe',INS_RFE))[L]
        iadb = (val>>7)&3
        flags |= ( IF_DB, 0, 0, IF_IA ) [ iadb ]
        olist = ( ArmRegOper(REG_SP), ArmImmOper(mode) )

    elif (op2 & 0x64) == 4:
        raise Exception('# Load/Store Dual, Load/Store Exclusive, table branch')

    elif (op2 & 0x60) == 0x20:
        raise Exception('# Data Processing (shifted register)')

    elif (op2 & 0x40) == 0x40:
        raise Exception('# Coprocessor, Advanced SIMD, Floating point instrs')
    else:
        raise InvalidInstruction(
                mesg="Thumb32 failure",
                bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va)
    return COND_AL, opcode, mnem, opers, flags, 0


def thumb32_10(va, val, val2):
    op =  (val2>>15)&1
    op2 = (val>>4) & 0x7f
    op1 = (val>>11) & 0x3
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
                bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va)
    return COND_AL, opcode, mnem, opers, flags, 0

def thumb32_11(va, val, val2):
    op =  (val2>>15)&1
    op2 = (val>>4) & 0x7f
    op1 = (val>>11) & 0x3
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

    return COND_AL, ( opcode, mnem, olist, flags, 0 )
'''

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
        imm8 |= 0x80 # 1bcdefg
        off = (a | (imm4<<1) )
        return ROR_C(imm8, 32, off)

dp_secondary = (
            'tst',# and
            None, # bic
            'mov', # orr
            'mvn', # orn
            'teq', # eor
            None, #
            None, #
            None, # pkh
            'cmn', #add
            None, # adc
            None, # sbc
            None,
            None,
            'cmp', #sub
            None,
            None,
            )

dp_sec_silS = (0,4,8,13)
# IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
DP_SEC_PSR_S = [IF_PSR_S for x in range(17)]
for x in dp_sec_silS:
    DP_SEC_PSR_S[x] |= IF_PSR_S_SIL 

def dp_mod_imm_32(va, val1, val2):
    if val2 & 0x8000:
        return branch_misc(va, val1,val2)

    flags = 0
    Rd = (val2 >> 8) & 0xf
    S = (val1>>4) & 1

    Rn = val1 & 0xf

    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    imm4 = imm3 | (i<<3)
    const = (val2 & 0xff)

    dpop = (val1>>5) & 0xf

    const,carry = ThumbExpandImm_C(imm4, const, 0)
    
    if Rd==15 and S:
        #raise Exception("dp_mod_imm_32 - FIXME: secondary dp encoding")
        mnem = dp_secondary[dpop]
        if mnem == None:
            raise Exception("dp_mod_imm_32: Rd==15, S, but dpop doesn't have a secondary! va:%x, %x%x" % (va, val1, val2))

        if S:
            flags |= DP_SEC_PSR_S[dpop]
        oper1 = ArmRegOper(Rn)
        oper2 = ArmImmOper(const)
        opers = (oper1, oper2)
        return COND_AL, None, mnem, opers, flags, 0

    elif Rn == 15 and (val1 & 0xfbc0 == 0xf040):
        dpop = (val1>>5) & 0xf
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
        raise InvalidInstruction(mesg="shift_or_ext_32 needs to hand off for val2 & 0xf000 != 0xf000 at va 0x%x: val1:%.4x val2:%.4x" % (va, val1, val2), va=va)


    op1 = (val1>>4) & 0xf
    op2 = (val2>>4) & 0xf
    rn = (val1 & 0xf)
    rd = (val2 >> 8) & 0xf
    rm = (val2 & 0xf)
    flags = 0

    if (op2):
        if op1 > 5:
            raise InvalidInstruction(
                    mesg="shift_or_ext_32 parsing an unsupported instruction encoding",
                    bytez=struct.pack("<H", val1)+struct.pack("<H", val2), va=va)

        rotate = (val2>>4) & 0x3

        if rn == 0xf:
            # sxth and the like
            opcode, mnem, = sxt_mnem_2[op1]
            if rotate == 0:
                opers = (
                        ArmRegOper(rd),
                        ArmRegOper(rm),
                        )
            else:
                opers = (
                        ArmRegOper(rd),
                        ArmRegOper(rm),
                        ArmImmOper(rotate),
                        )
        else:
            # sxtah and the like
            opcode, mnem, = sxt_mnem[op1]
            if rotate == 0:
                opers = (
                        ArmRegOper(rd),
                        ArmRegOper(rm),
                        )
            else:
                opers = (
                        ArmRegOper(rd),
                        ArmRegOper(rn),
                        ArmRegOper(rm),
                        ArmImmOper(rotate),
                        )


    else:
        # lsl/lsr/asr/ror
        op1 = (val1>>4) & 0xf
        opcode, mnem, nothing = mov_ris_ops[op1>>1]

        opers = (
                ArmRegOper(rd),
                ArmRegOper(rn),
                ArmRegOper(rm),
                )

        if (op1 & 1):
            flags |= IF_PSR_S

    return COND_AL, opcode, mnem, opers, flags, 0



def pdp_32(va, val1, val2):
    # saturated instructions
    raise Exception("Implement Me: pdp32: Saturated Instrs")
    pass

    return COND_AL, None, None, None, None, None

def ubfx_32(va, val1, val2):
    rd = (val2>>8) & 0xf
    rn = val1 & 0xf
    imm3 = (val2>>12) & 0x7
    imm2 = (val2>>6) & 0x3
    widthm1 = val2 & 0x1f
    lsbit = (imm3 << 2) | imm2

    opers = (
            ArmRegOper(rd),
            ArmRegOper(rn),
            ArmImmOper(lsbit),
            ArmImmOper(widthm1 + 1),
            )
    return COND_AL, None, None, opers, None, 0

def dp_bin_imm_32(va, val1, val2):  # p232
    flags = IF_THUMB32
    if val2 & 0x8000:
        return branch_misc(va, val1,val2)

    Rd = (val2 >> 8) & 0xf

    imm4 = val1 & 0xf
    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    const = val2 & 0xff

    op = (val1>>4) & 0x1f
    const |= (imm4 << 12) | (i << 11) | (imm3 << 8)

    oper0 = ArmRegOper(Rd)
    oper2 = ArmImmOper(const)
    opers = [oper0, oper2]

    if op in (0b00100, 0b01100):    # movw, movt
        return COND_AL, None, None, opers, 0, 0

    Rn = val1 & 0xf
    if Rn==15 and op in (0,0b1010):   # add/sub
        # adr
        return COND_AL, None, 'adr', opers, None, 0

    oper1 = ArmRegOper(Rn)
    opers.insert(1, oper1)

    return COND_AL, None, None, opers, flags, 0


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
    rd = (val2 >> 8)  & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegOper(rt, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8<<2, va=va)

    opers = (oper0, oper1, oper2)
    flags = 0
    return COND_AL, None, None, opers, flags, 0

def ldr_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm12 = val2 & 0xfff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm12, va=va)

    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0

ldrb_instrs = (
        (INS_LDR, 'ldr', IF_B|IF_THUMB32),
        (INS_LDR, 'ldr', IF_B|IF_S|IF_THUMB32),
        )
memh_instrs = (
        (INS_PLD, 'pld', IF_THUMB32),
        (INS_PLI, 'pli', IF_THUMB32),
        )

def ldrb_memhints_32(va, val1, val2):
    op1 = (val1>>7) & 3
    op2 = (val2>>6) & 0x3f
    rn = val1 & 0xf
    rt = (val2>>12) & 0xf

    Sbit = op1>>1


    if rn == 0xf:
        if rt == 0xf:
            # PLD(literal)
            opcode, mnem, flags = memh_instrs[Sbit]
            rm = val2 & 0xf
            imm2 = (val2>>4) & 3
            opers = (
                    ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va),
                    )
        else:
            # LDRB (literal)
            opcode, mnem, flags = ldrb_instrs[Sbit]
            imm12 = val2 & 0xfff
            opers = (
                    ArmRegOper(rt),
                    ArmPcOffsetOper(imm12, va),
                    )

    else:
        if op1&1:
            # ldrb (immediate):T2, ldrsb:T1
            opcode, mnem, flags = ldrb_instrs[Sbit]
            imm12 = val2 & 0xfff
            opers = (
                    ArmRegOper(rt),
                    ArmImmOffsetOper(rn, imm12, va),
                    )

        elif not op1:
            if not op2 and rt == 0xf:
                # pld/pldw (p526)
                opcode, mnem, flags = memh_instrs[Sbit]
                rm = val2 & 0xf
                imm2 = (val2>>4) & 3
                opers = (
                        ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va),
                        )

            elif (val2>>11) & 1:
                # LDRB (register)
                opcode, mnem, flags = ldrb_instrs[Sbit]
                imm8 = val2 & 0xff
                pubwl = ((val2 >> 6) & 0x18) | ((val2 >> 7) & 2)
                opers = (
                        ArmRegOper(rt),
                        ArmImmOffsetOper(rn, imm8, va, pubwl)
                        )


        else:
            # LDRB (register)
            opcode, mnem, flags = ldrb_instrs[Sbit]
            rm = val2 & 0xf
            imm2 = (val2>>4) & 3
            opers = (
                    ArmRegOper(rt),
                    ArmScaledOffsetOper(rn, rm, S_LSL, imm2, va),
                    )

        #else:
        #    raise envi.InvalidInstruction(
        #            mesg="ldrb_memhints_32: fall 1", va=va)


    return COND_AL, opcode, mnem, opers, flags, 0


def ldr_puw_32(va, val1, val2):
    #b11 = (val2>>11) & 1
    #if not b11:
    #    raise Exception("ldr_puw_32 parsing non-ldrb")

    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    puw = (val2>>8) & 0x7
    pubwl = ((puw&1) | ((puw&0x6)<<1)) << 1

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8, va=va, pubwl=pubwl)

    opers = (oper0, oper1)
    return COND_AL, None, None, opers, None, 0

def ldrex_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8<<2, va=va)

    opers = (oper0, oper1)
    flags = 0
    return COND_AL, None, None, opers, flags, 0

def ldrd_imm_32(va, val1, val2):
    pubwl = (val1 >> 4) & 0x1f
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    rt2= (val2 >> 8)  & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOper(rt2, va=va)
    oper2 = ArmImmOffsetOper(rn, imm8<<2, va=va, pubwl=pubwl)

    opers = (oper0, oper1, oper2)
    flags = 0
    return COND_AL, None, None, opers, flags, 0

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

    opers = (
            ArmRegOper(rd, va=va),
            ArmRegOper(rn, va=va),
            ArmRegOper(rm, va=va),
            ArmRegOper(ra, va=va),
            )

    return COND_AL, None, mnem, opers, None, 0

def smul_32(va, val1, val2):
    rn = val1 & 0xf
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf

    nm = (val2 >> 4) & 0x3
    mnem = ('smulbb','smulbt','smultb','smultt')[nm]

    opers = (
            ArmRegOper(rd, va=va),
            ArmRegOper(rn, va=va),
            ArmRegOper(rm, va=va),
            )
    return COND_AL, None, mnem, opers, None, 0

def tb_ldrex_32(va, val1, val2):
    op3 = (val2 >> 4) & 0xf

    rn = val1 & 0xf
    rm = val2 & 0xf
    rt = (val2 >> 12) & 0xf
    flags = IF_THUMB32 | (IF_B, IF_H, 0, IF_D)[op3&3]

    if op3 & 4: # ldrex#
        mnem = 'ldrex'
        opcode = INS_LDREX

        oper0 = ArmRegOper(rt, va=va)
        oper1 = ArmRegOper(rn, va=va)
        opers = (oper0, oper1)
    else:       # tbb/tbh
        mnem = 'tb'
        opcode = INS_TB
        isH = op3 & 1
        flags |= envi.IF_BRANCH

        oper0 = ArmScaledOffsetOper(rn, rm, S_LSL, isH, va, pubwl=0x18)
        opers = (oper0,)

    return COND_AL, opcode, mnem, opers, flags, 0


mov_ris_ops = (
                (INS_LSL, 'lsl',3),
                (INS_LSR, 'lsr',3),
                (INS_ASR, 'asr',3),
                (INS_ROR, 'ror',3),
                )
mov_ris_alt = (
                (INS_MOV, 'mov',2),
                (INS_LSR, 'lsr',3),
                (INS_ASR, 'asr',3),
                (INS_RRX, 'rrx',2),
                )
def mov_reg_imm_shift_32(va, val1, val2):
    optype = (val2>>4) & 3
    imm = ((val2>>10)&0x1c) | ((val2>>6)&3)
    rm = val2 & 0xf
    rd = (val2 >> 8) & 0xf
    s = (val1 >> 4) & 1

    if imm == 0 and optype in (0,3):
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
                (INS_RSB, 'rsb', 3),
                )
dp_shift_alt1= ((INS_TST, 'tst', 2),
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
dp_shift_alt2= ((INS_AND, 'and', 3),
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

def dp_mod_imm_32_deprecated(va, val1, val2):
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
        flags = IF_PSR_S
    else:
        flags = 0

    return COND_AL, opcode, mnem, opers, flags, 0

def coproc_simd_32(va, val1, val2):
    # p249 of ARMv7-A and ARMv7-R arch ref manual, parts 2 and 3 (not top section)

    val32 = (val1 << 16) | val2
    #print "coproc_simd_32"
    ### return armd.doDecode(va, val32, 'THUMB2', 0)            lol!  trying to leverage Arm code that just aint there!  CONSIDER: finish this, then move it into ARM, then call there....
    # FIXME: coalesce ARM/Thumb32 decoding schemes so they can use the same decoders  (ie.  they return the same things:  opcode, mnem, olist, flags)
    # FIXME: MANY THUMB2 instruction encodings model their "Always Execute" ARM equivalents.
    coproc = (val2>>8) & 0xf
    op1 =    (val1>>4) & 0x3f
    op =     (val2>>4) & 1

    iflags = 0
    simdflags = 0

    if op1 & 0b110000 == 0b110000:
        return adv_simd_32(va, val1, val2)

    if coproc & 0b1110 != 0b1010:   # apparently coproc 10 and 11 are not allowed...
        if op1 == 0b000100: 
            # mcrr/mcrr2 (a8-476)
            mnem = ('mcrr','mcrr2')[(val1>12)&1]
            
            Rt2 = val1 & 0xf
            Rt = (val2>>12) & 0xf
            opc1 = (val2>>4) & 0xf
            CRm = val2 & 0xf

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocOpcodeOper(opc1),
                ArmRegOper(Rt, va=va),
                ArmRegOper(Rt2, va=va),
                ArmCoprocRegOper(CRm),
            )
            opcode = IENC_COPROC_RREG_XFER<<16

        elif op1 == 0b000101:
            # mrrc/mrrc2 (a8-492)
            mnem = ('mcrr','mcrr2')[(val1>12)&1]
            
            Rt2 = val1 & 0xf
            Rt = (val2>>12) & 0xf
            opc1 = (val2>>4) & 0xf
            CRm = val2 & 0xf

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocOpcodeOper(opc1),
                ArmRegOper(Rt, va=va),
                ArmRegOper(Rt2, va=va),
                ArmCoprocRegOper(CRm),
            )
            opcode = IENC_COPROC_RREG_XFER<<16

        elif op1 & 0b100000 == 0:
            # stc/stc2 (a8-660)
            # ldc/ldc2 immediate/literal (if Rn == 0b1111) (a8-390/392)
            mnem = ('stc','ldc','stc2','ldc2')[((val1>>11)&2) | (op1 & 1)]
            
            pudwl = (val1>>4) & 0x1f
            Rn = (val1) & 0xf
            CRd = (val2>>12) & 0xf
            offset = val2 & 0xff

            if pudwl & 4:   # L
                iflags = IF_L
            else:
                iflags = 0

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocRegOper(CRd),
                ArmImmOffsetOper(Rn, offset*4, va, pubwl=pudwl),
            )
            
            opcode = (IENC_COPROC_LOAD << 16)

        elif op1 & 0b110000 == 0b100000 and op == 0:
            # cdp/cdp2 (a8-356)
            opc1 =      (val1>>4) & 0xf
            CRn =       val1 & 0xf
            CRd =       (val2>>12) & 0xf
            opc2 =      (val2>>5) & 0x7
            CRm =       val2 & 0xf
            mnem =      cdp_mnem[(val1>>12)&1]

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocOpcodeOper(opc1),
                ArmCoprocRegOper(CRd),
                ArmCoprocRegOper(CRn),
                ArmCoprocRegOper(CRm),
                ArmCoprocOpcodeOper(opc2),
            )
            
            opcode = (IENC_COPROC_DP << 16)

        elif op1 & 0b110000 == 0b100000 and op == 1:    # 10xxx0 and 10xxx1
            # mcr/mcr2 (a8-474)
            # mrc/mrc2 (a8-490)
            load =      (val1>>4) & 1
            two =       (val1>>11) & 2
            opc1 =      (val1>>5) & 0x7
            CRn =       val1 & 0xf
            Rd =        (val2>>12) & 0xf
            opc2 =      (val2>>5) & 0x7
            CRm =       val2 & 0xf
            mnem =      ('mcr','mrc','mcr2','mrc2')[load | two]

            opers = (
                ArmCoprocOper(coproc),
                ArmCoprocOpcodeOper(opc1),
                ArmRegOper(Rd, va=va),
                ArmCoprocRegOper(CRn),
                ArmCoprocRegOper(CRm),
                ArmCoprocOpcodeOper(opc2),
            )
            
            opcode = (IENC_COPROC_REG_XFER << 16)

    else:
        # FIXME: REMOVE WHEN DONE IMPLEMENTING
        opcode = 0
        iflags = 0
        opers = []
        
        if op1 & 0b111110 == 0b000100:
            # adv simd fp (A7-277)
            return adv_simd_32(va, val1, val2)

        elif op1 & 0b100000 == 0:
            Rn = val1 & 0xf

            # adv simd fp (a7-272)
            tmop1 = op1 & 0b11011
            
            if op1 & 0b11110 == 0b00100:
                # 64 bit transverse between ARM core and extension registers (a7-277)
                raise envi.InvalidInstruction(      #FIXME!!!!
                        mesg="IMPLEMENT: 64-bit transverse between ARM core and extension registers",
                        bytez=bytez[offset:offset+4], va=va)


            # EXPECT TO NOT REACH HERE UNLESS WE MEAN BUSINESS.  otherwise this needs to be in an else:
            if (op1 & 0b11010) in (0b10, 0b11010):
                raise InvalidInstruction(mesg="INVALID ENCODING", bytez=bytez[offset:offset+4], va=va)

            l = op1 & 1 # vldm or vstm
            indiv = (op1 & 0b10010) == 0b10000
            # writeback should be handled by operand
            imm8 = (val2 & 0xff) >>1
            imm32 = imm8 <<3

            # size = 0/1 for 32-bit and 64-bit accordingly
            size = (val2>>8) & 1    # TODO: Check next three bits must be 0b101

            pudwl = op1 & 0b11111

            # starting extended register
            D = (pudwl>>2) & 1
            Vd = val2>>12
            d = (Vd << 1) | D

            # vpush/vpop
            if (op1 & 0b11011) in (0b01011, 0b10010) and Rn == REG_SP:
                mnem, opcode = (('vpush',INS_VPUSH), ('vpop',INS_VPOP))[l]
                opers = (
                        ArmExtRegListOper(d>>size, imm8, size),
                        )

            else:
                oflags = 0

                mnemidx = l | (indiv<<1)
                mnem, opcode = (('vstm',INS_VSTM),('vldm',INS_VLDM),('vstr',INS_VSTR),('vldr',INS_VLDR))[mnemidx]
                # figure out IA/DB/etc...  and Writeback

                # inc-after or dec-before?
                ia = (pudwl>>3) & 3       # PU determine IA/DB
                iflags |= (0, IF_IA, IF_DB, 0)[ia]

                # write-back to original reg?
                w = (pudwl >> 1) & 1
                if w:
                    oflags |= OF_W   # writeback flag for ArmRegOper

                if indiv:
                    rbase = ('s%d', 'd%d')[size]
                    VRd = rctx.getRegisterIndex(rbase % d)
                    opers = (
                            ArmRegOper(VRd, va=va, oflags=oflags),
                            ArmImmOffsetOper(Rn, imm32, va=va, pubwl=pudwl),
                            )

                else:
                    opers = (
                            ArmRegOper(Rn, va=va, oflags=oflags),
                            ArmExtRegListOper(d, imm32>>size, size),
                            )

        elif op1 & 0b110000 == 0b100000:
            if op == 0:
                # fp dp (a7-270)
                mnem = 'UNIMPL: FP DP' # FIXME!!!
                return fp_dp(va, val1, val2)

            else:
                # adv simd fp (a7-276)
                mnem = 'UNIMPL: adv simd'       # FIXME
                return adv_simd_32(va, val1, val2)

    return COND_AL, opcode, mnem, opers, iflags, simdflags

from envi.archs.arm.disasm import _do_adv_simd_32, _do_fp_dp

def fp_dp(va, val1, val2):
    opcode, mnem, opers, iflags, simdflags = _do_fp_dp(va, val1, val2)
    return COND_AL, opcode, mnem, opers, iflags, simdflags
   
def adv_simd_32(va, val1, val2):
    val = (val1 << 16) | val2
    u = (val1 >> 12) & 1
    opcode, mnem, opers, iflags, simdflags = _do_adv_simd_32(val, va, u)
    return COND_AL, opcode, mnem, opers, iflags, simdflags

def _adv_simd_32(va, val1, val2):
    # aside from u and the first 8 bits, ARM and Thumb2 decode identically (A7-259)
    u = (val1>>12) & 1
    a = (val1>>3) & 0x1f
    b = (val2>>8) & 0xf
    c = (val2>>4) & 0xf

    print "a=%x\tb=%x\tu=%x\tc=%x" % (a, b, u, c)
    if not (a & 0x10):
        # three registers of the same length
        a = (val2>>8) & 0xf
        b = (val2>>4) & 1
        c = (val1>>4) & 3

        #print " adv simd: 3 same: a=%x\tb=%x\tu=%x\tc=%x" % (a, b, u, c)
        index = c | (u<<2) | (b<<3) | (a<<4)
        #print " adv simd: 3 same: %x" % index
        mnem, opcode, simdflags, handler = adv_simd_3_regs[index]

        d = (val1 >> 2) & 0x10
        d |= ((val2 >> 12) & 0xf)

        n = (val2 >> 3) & 0x10
        n |= (val1 & 0xf)

        m = (val2 >> 1) & 0x10
        m |= (val2 & 0xf)

        q = (val2 >> 2) & 0x10

        rbase = ('d%d', 'q%d')[q]

        opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
            ArmRegOper(rctx.getRegisterIndex(rbase%n)),
            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
            )

        if handler != None:
            nmnem, nopcode, nflags, nopers = handler(val, va, mnem, opcode, simdflags, opers)
            if nmnem != None:
                mnem = nmnem
                opcode = nopcode
            if nflags != None:
                simdflags = nflags
            if nopers != None:
                opers = nopers

        return COND_AL, opcode, mnem, opers, 0, simdflags




bcc_ops = {
    0b0000:    (INS_BCC,'beq',  envi.IF_COND, COND_EQ),
    0b0001:    (INS_BCC,'bne',  envi.IF_COND, COND_NE),
    0b0010:    (INS_BCC,'bcs',  envi.IF_COND, COND_CS),
    0b0011:    (INS_BCC,'bcc',  envi.IF_COND, COND_CC),
    0b0100:    (INS_BCC,'bmi',  envi.IF_COND, COND_MI),
    0b0101:    (INS_BCC,'bpl',  envi.IF_COND, COND_PL),
    0b0110:    (INS_BCC,'bvs',  envi.IF_COND, COND_VS),
    0b0111:    (INS_BCC,'bvc',  envi.IF_COND, COND_VC),
    0b1000:    (INS_BCC,'bhi',  envi.IF_COND, COND_HI),
    0b1001:    (INS_BCC,'bls',  envi.IF_COND, COND_LS),
    0b1010:    (INS_BCC,'bge',  envi.IF_COND, COND_GE),
    0b1011:    (INS_BCC,'blt',  envi.IF_COND, COND_LT),
    0b1100:    (INS_BCC,'bgt',  envi.IF_COND, COND_GT),
    0b1101:    (INS_BCC,'ble',  envi.IF_COND, COND_LE),
    0b1110:    (INS_B,'b',      envi.IF_NOFALL, COND_AL),
    }


# opinfo is:
# ( <mnem>, <operdef>, <flags> )
# operdef is:
# ( (otype, oshift, omask), ...)

# FIXME: thumb and arm opcode numbers don't line up. - FIX
thumb_base = [
    ('00000',       ( INS_LSL,'lsl',     imm5_rm_rd, IF_PSR_S)), # LSL<c> <Rd>,<Rm>,#<imm5>
    ('00001',       ( INS_LSR,'lsr',     imm5_rm_rd, IF_PSR_S)), # LSR<c> <Rd>,<Rm>,#<imm>
    ('00010',       ( INS_ASR,'asr',     imm5_rm_rd, IF_PSR_S)), # ASR<c> <Rd>,<Rm>,#<imm>
    ('0001100',     ( INS_ADD,'add',     rm_rn_rd,   IF_PSR_S)), # ADD<c> <Rd>,<Rn>,<Rm>
    ('0001101',     ( INS_SUB,'sub',     rm_rn_rd,   IF_PSR_S)), # SUB<c> <Rd>,<Rn>,<Rm>
    ('0001110',     ( INS_ADD,'add',     imm3_rn_rd, IF_PSR_S)), # ADD<c> <Rd>,<Rn>,#<imm3>
    ('0001111',     ( INS_SUB,'sub',     imm3_rn_rd, IF_PSR_S)), # SUB<c> <Rd>,<Rn>,#<imm3>
    ('00100',       ( INS_MOV,'mov',     imm8_rd,    IF_PSR_S)), # MOV<c> <Rd>,#<imm8>
    ('00101',       ( INS_CMP,'cmp',     imm8_rd,    0)), # CMP<c> <Rn>,#<imm8>
    ('00110',       ( INS_ADD,'add',     imm8_rd,    IF_PSR_S)), # ADD<c> <Rdn>,#<imm8>
    ('00111',       (INS_SUB,'sub',     imm8_rd,    IF_PSR_S)), # SUB<c> <Rdn>,#<imm8>
    # Data processing instructions
    ('0100000000',  (INS_AND,'and',     rm_rdn,     IF_PSR_S)), # AND<c> <Rdn>,<Rm>
    ('0100000001',  (INS_EOR,'eor',     rm_rdn,     IF_PSR_S)), # EOR<c> <Rdn>,<Rm>
    ('0100000010',  (INS_LSL,'lsl',     rm_rdn,     IF_PSR_S)), # LSL<c> <Rdn>,<Rm>
    ('0100000011',  (INS_LSR,'lsr',     rm_rdn,     IF_PSR_S)), # LSR<c> <Rdn>,<Rm>
    ('0100000100',  (INS_ASR,'asr',     rm_rdn,     IF_PSR_S)), # ASR<c> <Rdn>,<Rm>
    ('0100000101',  (INS_ADC,'adc',     rm_rdn,     IF_PSR_S)), # ADC<c> <Rdn>,<Rm>
    ('0100000110',  (INS_SBC,'sbc',     rm_rdn,     IF_PSR_S)), # SBC<c> <Rdn>,<Rm>
    ('0100000111',  (INS_ROR,'ror',     rm_rdn,     IF_PSR_S)), # ROR<c> <Rdn>,<Rm>
    ('0100001000',  (INS_TST,'tst',     rm_rd,      0)), # TST<c> <Rn>,<Rm>
    ('0100001001',  (INS_RSB,'rsb',     rm_rd_imm0, IF_PSR_S)), # RSB<c> <Rd>,<Rn>,#0
    ('0100001010',  (INS_CMP,'cmp',     rm_rd,      0)), # CMP<c> <Rn>,<Rm>
    ('0100001011',  (INS_CMN,'cmn',     rm_rd,      0)), # CMN<c> <Rn>,<Rm>
    ('0100001100',  (INS_ORR,'orr',     rm_rdn,     IF_PSR_S)), # ORR<c> <Rdn>,<Rm>
    ('0100001101',  (INS_MUL,'mul',     rn_rdm,     IF_PSR_S)), # MUL<c> <Rdm>,<Rn>,<Rdm>
    ('0100001110',  (INS_BIC,'bic',     rm_rdn,     0)), # BIC<c> <Rdn>,<Rm>
    ('0100001111',  (INS_MVN,'mvn',     rm_rd,      0)), # MVN<c> <Rd>,<Rm>
    # Special data in2tructions and branch and exchange
    ('0100010000',  (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('0100010001',  (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('010001001',   (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('010001010',   (30,'cmp',     d1_rm4_rd3, 0)), # CMP<c> <Rn>,<Rm>
    ('010001011',   (31,'cmp',     d1_rm4_rd3, 0)), # CMP<c> <Rn>,<Rm>
    ('01000110',    (34,'mov',     d1_rm4_rd3, 0)), # MOV<c> <Rd>,<Rm>
    ('010001110',   (35,'bx',      rm4_shift3, envi.IF_NOFALL)), # BX<c> <Rm>       # FIXME: check for IF_RET
    ('010001111',   (36,'blx',     rm4_shift3, envi.IF_CALL)), # BLX<c> <Rm>
    # Load from Litera7 Pool
    ('01001',       (37,'ldr',     rt_pc_imm8, 0)), # LDR<c> <Rt>,<label>
    # Load/Stor single data item
    ('0101000',     (38,'str',     rm_rn_rt,   0)), # STR<c> <Rt>,[<Rn>,<Rm>]
    ('0101001',     (39,'strh',    rm_rn_rt,   0)), # STRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101010',     (40,'strb',    rm_rn_rt,   0)), # STRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101011',     (41,'ldrsb',   rm_rn_rt,   0)), # LDRSB<c> <Rt>,[<Rn>,<Rm>]
    ('0101100',     (42,'ldr',     rm_rn_rt,   0)), # LDR<c> <Rt>,[<Rn>,<Rm>]
    ('0101101',     (43,'ldrh',    rm_rn_rt,   0)), # LDRH<c> <Rt>,[<Rn>,<Rm>]
    ('0101110',     (44,'ldrb',    rm_rn_rt,   0)), # LDRB<c> <Rt>,[<Rn>,<Rm>]
    ('0101111',     (45,'ldrsh',   rm_rn_rt,   0)), # LDRSH<c> <Rt>,[<Rn>,<Rm>]
    ('01100',       (46,'str',     imm54_rn_rt, 0)), # STR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01101',       (47,'ldr',     imm54_rn_rt, 0)), # LDR<c> <Rt>, [<Rn>{,#<imm5>}]
    ('01110',       (48,'strb',    imm56_rn_rt, 0)), # STRB<c> <Rt>,[<Rn>,#<imm5>]
    ('01111',       (49,'ldrb',    imm56_rn_rt, 0)), # LDRB<c> <Rt>,[<Rn>{,#<imm5>}]
    ('10000',       (50,'strh',    imm55_rn_rt, 0)), # STRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10001',       (51,'ldrh',    imm55_rn_rt, 0)), # LDRH<c> <Rt>,[<Rn>{,#<imm>}]
    ('10010',       (52,'str',     rd_sp_imm8, 0)), # STR<c> <Rt>, [<Rn>{,#<imm>}]
    ('10011',       (53,'ldr',     rd_sp_imm8, 0)), # LDR<c> <Rt>, [<Rn>{,#<imm>}]
    # Generate PC relative address
    ('10100',       (INS_ADD,'add',     rd_pc_imm8, 0)), # ADD<c> <Rd>,<label>
    # Generate SP rel5tive address
    ('10101',       (INS_ADD,'add',     rd_sp_imm8, 0)), # ADD<c> <Rd>,SP,#<imm>
    # Miscellaneous in6tructions
    ('1011001000',  (561,'sxth',    rm_rd,      0)), # SXTH<c> <Rd>, <Rm>
    ('1011001001',  (561,'sxtb',    rm_rd,      0)), # SXTB<c> <Rd>, <Rm>
    ('1011001010',  (561,'uxth',    rm_rd,      0)), # UXTH<c> <Rd>, <Rm>
    ('1011001011',  (561,'uxtb',    rm_rd,      0)), # UXTB<c> <Rd>, <Rm>
    ('1011010',     (56,'push',    push_reglist,    0)), # PUSH <reglist>
    ('10110110010', (57,'setend',  sh4_imm1,   0)), # SETEND <endian_specifier>
    ('10110110011', (58,'cps',     cps16,0)), # CPS<effect> <iflags>
    ('10110001',    (INS_CBZ,'cbz',     i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)), # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111001',    (INS_CBNZ,'cbnz',    i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)), # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('10110011',    (INS_CBZ,'cbz',     i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)), # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111011',    (INS_CBNZ,'cbnz',    i_imm5_rn,  envi.IF_COND | envi.IF_BRANCH)), # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('1011101000',  (61,'rev',     rn_rdm,     0)), # REV Rd, Rn
    ('1011101001',  (62,'rev16',   rn_rdm,     0)), # REV16 Rd, Rn
    ('1011101011',  (63,'revsh',   rn_rdm,     0)), # REVSH Rd, Rn
    ('101100000',   (INS_ADD,'add',     sp_sp_imm7, 0)), # ADD<c> SP,SP,#<imm>
    ('101100001',   (INS_SUB,'sub',     sp_sp_imm7, 0)), # SUB<c> SP,SP,#<imm>
    ('1011110',     (66,'pop',     pop_reglist,  0)), # POP<c> <registers>
    ('10111110',    (67,'bkpt',    imm8,       0)), # BKPT <blahblah>
    # Load / Store Mu64iple
    ('11000',       (68,'stm',   rm_reglist, IF_IA|IF_W)), # LDMIA Rd!, reg_list
    ('11001',       (69,'ldm',   rm_reglist, IF_IA|IF_W)), # STMIA Rd!, reg_list
    # Conditional Bran6hes
    ('11010000',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010001',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010010',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010011',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010100',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010101',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010110',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010111',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011000',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011001',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011010',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011011',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011100',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011101',    (INS_BCC,'b',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011110',    (INS_B,'b',       pc_imm8,       envi.IF_BRANCH|envi.IF_NOFALL)),
    ('11011111',    (INS_BCC,'bfukt', pc_imm8,       envi.IF_BRANCH|0)),
    # Software Interrupt
    ('11011111',    (INS_SWI,'svc',     imm8,       0)), # SWI <blahblah>
    ('1011111100000000',    (89,'nopHint',    imm8,       0)),
    ('1011111100010000',    (90,'yieldHint',  imm8,       0)),
    ('1011111100100000',    (91,'wfrHint',    imm8,       0)),
    ('1011111100110000',    (92,'wfiHint',    imm8,       0)),
    ('1011111101000000',    (93,'sevHint',    imm8,       0)),
    ('10111111',       (INS_IT, 'it',    itblock,       envi.IF_COND)),
    ]

thumb1_extension = [
    ('11100',       (INS_B,  'b',       pc_imm11,           envi.IF_BRANCH|envi.IF_NOFALL)),        # B <imm11>
    ('1111',        (INS_BL, 'bl',      branch_misc,       envi.IF_CALL | IF_THUMB32)),   # BL/BLX <addr25> 
]

# FIXME: need to take into account ThumbEE 
# 32-bit Thumb instructions start with:
# 0b11101
# 0b11110
# 0b11111
thumb2_extension = [
    ('11100',       (85,'ldm',      ldm16,     0)),     # 16-bit instructions
    # load/store multiple (A6-235 in ARM DDI 0406C)

    ('111010000000',    (85,'srs',    ldm_reg_mode_32,    IF_THUMB32|IF_DB)), # next bits shoud be: 110111000000000mode
    ('111010000010',    (85,'srs',    ldm_reg_mode_32,    IF_THUMB32|IF_DB)), # next bits shoud be: 110111000000000mode
    ('111010000001',    (85,'rfe',    ldm_reg_32,         IF_THUMB32|IF_DB)),
    ('111010000011',    (85,'rfe',    ldm_reg_32,         IF_THUMB32|IF_DB)),

    ('111010001000',    (85,'stm',  ldm_32,     IF_THUMB32|IF_IA)),    # stm(stmia/stmea)
    ('111010001001',    (85,'ldm',  ldm_32,     IF_THUMB32|IF_IA)),    # ldm/ldmia/ldmfd
    ('111010001010',    (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_IA)),    # stm(stmia/stmea)
    ('1110100010110',   (85,'ldm',  ldm_32,     IF_THUMB32|IF_W|IF_IA)), # not 111101
    ('11101000101110',  (85,'ldm',  ldm_32,     IF_THUMB32|IF_W|IF_IA)), # not 111101
    ('111010001011111', (85,'ldm',  ldm_32,     IF_THUMB32|IF_W|IF_IA)), # not 111101
    ('1110100010111100',(85,'ldm',  ldm_32,     IF_THUMB32|IF_W|IF_IA)), # not 111101
    ('1110100010111101',(85,'pop',  pop_32,     IF_THUMB32|IF_W)), # 111101 - pop

    ('111010010000',    (85,'stm',  ldm_32,     IF_THUMB32)),   # stmdb/stmfd
    ('111010010001',    (85,'ldm',  ldm_32,     IF_THUMB32)),   # ldmdb/ldmea
    ('1110100100100',   (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('11101001001010',  (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('111010010010111', (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('1110100100101100',(85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('1110100100101101',(85,'push', push_32,    IF_THUMB32|IF_W)), # 101101 - push
    ('111010010011',    (85,'ldm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)),   # ldmdb/ldmea

    ('111010011000',    (85,'srs',    ldm_reg_mode_32,    IF_THUMB32|IF_IA)),
    ('111010011010',    (85,'srs',    ldm_reg_mode_32,    IF_THUMB32|IF_IA)),
    ('111010011001',    (85,'rfe',    ldm_reg_32,         IF_THUMB32|IF_IA)),
    ('111010011011',    (85,'rfe',    ldm_reg_32,         IF_THUMB32|IF_IA)),

    # load/store dual, load/store exclusive, table branch
    ('111010000100',    (85,'strex',    strex_32,    IF_THUMB32)),
    ('111010000101',    (85,'ldrex',    ldrex_32,    IF_THUMB32)),

    ('111010000110',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010001110',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010010100',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010010110',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010011100',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),
    ('111010011110',    (85,'strd',    ldrd_imm_32,    IF_THUMB32)),

    ('111010000111',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010001111',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010010101',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010010111',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010011101',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),
    ('111010011111',    (85,'ldrd',    ldrd_imm_32,     IF_THUMB32)),

    ('111010001100',    (85,'strex',   strexn_32,       IF_THUMB32)),
    ('111010001101',    (85,'tb',      tb_ldrex_32,     IF_THUMB32)),   # FIXME: these are jmp tables.  mark them!

    # data-processing (shifted register)
    #('1110101',             (85,'dp_sr',    dp_shift_32,         IF_THUMB32)),
    ('11101010000',         (85,'and',      dp_shift_32,        IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11101010001',         (85,'bic',      dp_shift_32,        IF_THUMB32)),
    
    ('1110101001000',       (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('11101010010010',      (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('111010100100110',     (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001001110',    (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001001111',    (85,'mov_reg_sh', mov_reg_imm_shift_32,         IF_THUMB32)),  # mov_imm if rn=1111
    ('1110101001010',       (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('11101010010110',      (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('111010100101110',     (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001011110',    (85,'orr',      dp_shift_32,        IF_THUMB32)),
    ('1110101001011111',    (85,'mov_reg_sh', mov_reg_imm_shift_32,         IF_THUMB32)),  # mov_imm if rn=1111

    ('11101010011',         (85,'orn',      dp_shift_32,        IF_THUMB32)),  # mvn if rn=1111
    ('11101010100',         (85,'eor',      dp_shift_32,        IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11101010110',         (85,'pkh',      dp_shift_32,        IF_THUMB32)),
    ('11101011000',         (85,'add',      dp_shift_32,        IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11101011010',         (85,'adc',      dp_shift_32,        IF_THUMB32)),
    ('11101011011',         (85,'sbc',      dp_shift_32,        IF_THUMB32)),
    ('11101011101',         (85,'sub',      dp_shift_32,        IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11101011110',         (85,'rsb',      dp_shift_32,        IF_THUMB32)),

    # coproc, adv simd, fp-instrs #ed9f 5a31
    ('11101100',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101101',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101110',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11101111',            (85,'adv simd', adv_simd_32,        IF_THUMB32)),
    ('1111110',             (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11111110',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),
    ('11111111',            (85,'adv simd', adv_simd_32,        IF_THUMB32)),

    # data-processing (modified immediate)
    ('11110000000',         (85,'and',      dp_mod_imm_32,      IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110000001',         (85,'bic',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000010',         (85,'orr',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110000011',         (85,'orn',      dp_mod_imm_32,      IF_THUMB32)),  # mvn if rn=1111
    ('11110000100',         (85,'eor',      dp_mod_imm_32,      IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110001000',         (85,'add',      dp_mod_imm_32,      IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110001010',         (85,'adc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001011',         (85,'sbc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110001101',         (85,'sub',      dp_mod_imm_32,      IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110001110',         (85,'rsb',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100000',         (85,'and',      dp_mod_imm_32,      IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110100001',         (85,'bic',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100010',         (85,'orr',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110100011',         (85,'orn',      dp_mod_imm_32,      IF_THUMB32)),  # mvn if rn=1111
    ('11110100100',         (85,'eor',      dp_mod_imm_32,      IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110101000',         (85,'add',      dp_mod_imm_32,      IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110101010',         (85,'adc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101011',         (85,'sbc',      dp_mod_imm_32,      IF_THUMB32)),
    ('11110101101',         (85,'sub',      dp_mod_imm_32,      IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110101110',         (85,'rsb',      dp_mod_imm_32,      IF_THUMB32)),
    ('1111001000',          (85,'add',      dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111001001',          (85,'movw',     dp_bin_imm_32,      IF_THUMB32)),
    ('1111001010',          (85,'sub',      dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111001011',          (85,'movt',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110011000',         (85,'ssat',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110011001',         (85,'ssat16',   dp_bin_imm_32,      IF_THUMB32)),
    ('11110011010',         (85,'sbfx',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110011011',         (85,'bfi',      dp_bin_imm_32,      IF_THUMB32)),  # bfc if rn=1111
    ('11110011100',         (85,'usat',     dp_bin_imm_32,      IF_THUMB32)),
    ('111100111010',        (85,'usat',     dp_bin_imm_32,      IF_THUMB32)),  # usat16 if val2=0000xxxx00xxxxxx
    ('111100111011',        (85,'usat',     dp_bin_imm_32,      IF_THUMB32)),  # usat16 if val2=0000xxxx00xxxxxx
    ('1111001111',          (85,'ubfx',     ubfx_32,      IF_THUMB32)),
    ('1111011000',          (85,'add',      dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111011001',          (85,'movw',     dp_bin_imm_32,      IF_THUMB32)),
    ('1111011010',          (85,'sub',      dp_bin_imm_32,      IF_THUMB32)),  # adr if rn=1111
    ('1111011011',          (85,'movt',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110111000',         (85,'ssat',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110111001',         (85,'ssat16',   dp_bin_imm_32,      IF_THUMB32)),
    ('11110111010',         (85,'sbfx',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110111011',         (85,'bfi',      dp_bin_imm_32,      IF_THUMB32)),  # bfc if rn=1111
    ('11110111100',         (85,'usat',     dp_bin_imm_32,      IF_THUMB32)),
    ('11110111101',         (85,'usat',     dp_bin_imm_32,      IF_THUMB32)),  # usat16 if val2=0000xxxx00xxxxxx
    ('11110111110',         (85,'ubfx',     ubfx_32,      IF_THUMB32)),
    ('11110111111',         (85,'branchmisc', branch_misc,      IF_THUMB32)),
    ('111110000000',        (INS_STR, 'str', ldr_puw_32,        IF_B | IF_THUMB32)),
    ('111110000001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110000010',        (INS_STR,  'str',  ldr_puw_32,      IF_H | IF_THUMB32)),
    ('111110000011',        (INS_LDR,  'ldr',  ldr_puw_32,      IF_H | IF_THUMB32)),
    ('111110000100',        (INS_STR,  'str',  ldr_puw_32,      IF_THUMB32)),   # T4 encoding
    ('111110000101',        (INS_LDR,  'ldr',  ldr_puw_32,      IF_THUMB32)),   # T4 encoding
    #('111110001001',        (INS_LDRB, 'ldrb', ldr_32,          IF_THUMB32)),
    ('111110001001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110001010',        (INS_STR, 'str', ldr_32,            IF_H | IF_THUMB32)),
    ('111110001011',        (INS_LDR, 'ldr', ldr_32,            IF_H | IF_THUMB32)),
    ('111110001100',        (INS_STR,  'str',  ldr_32,      IF_THUMB32)),
    ('111110001101',        (INS_LDR,  'ldr',  ldr_32,          IF_THUMB32)), # T3
    ('111110001000',        (INS_STR, 'str', ldr_32,            IF_B | IF_THUMB32)),
    ('111110010001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),
    ('111110011001',        (None, 'ldrb_memhints32', ldrb_memhints_32,  IF_THUMB32)),

    # data-processing (register)
    ('111110100',           (None, 'shift_or_extend', shift_or_ext_32,   IF_THUMB32)),
    #('111110101',           (None, 'parallel_misc', parallel_misc_32,   IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110101010',        (INS_UASX, 'uasx', pdp_32,          IF_THUMB32)),
    ('111110101110',        (INS_USAX, 'usax', pdp_32,          IF_THUMB32)),
    ('111110101101',        (INS_USUB16, 'usub16', pdp_32,      IF_THUMB32)),
    ('111110101000',        (INS_UADD8, 'uadd8', pdp_32,        IF_THUMB32)),
    ('111110101100',        (INS_USUB8, 'usub8', pdp_32,        IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,      IF_THUMB32)),
    ('111110110000',        (INS_MLA,  'mla',  mla_32,          IF_THUMB32)),
    ('111110110001',        (INS_SMUL, 'smul', smul_32,         IF_THUMB32)),
    #('11111',               (85,'branchmisc', branch_misc,            IF_THUMB32)),
    #('11111',         (85,'SOMETHING WICKED THIS WAY',      dp_bin_imm_32,         IF_THUMB32)),

    ('11100',       (INS_B,  'b',       pc_imm11,           envi.IF_BRANCH|envi.IF_NOFALL)),        # B <imm11>
    # blx is covered by special exceptions in dp_bin_imm_32 and dp_mod_imm_32
    #('11110',       (INS_BL, 'bl',      branch_misc,       envi.IF_CALL | IF_THUMB32)),   # BL/BLX <addr25>
    ]
''' whoa... they changed it all up.
    ('11110010000',         (85,'and',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110010001',         (85,'bic',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110010010',       (85,'orr',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110010011',         (85,'orn',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # mvn if rn=1111
    ('11110010100',         (85,'eor',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110010110',         (85,'movt',     dp_bin_imm_32,        IF_W | IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110011000',         (85,'add',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110011010',         (85,'adc',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110011011',         (85,'sbc',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110011101',         (85,'sub',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110011110',         (85,'rsb',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110110000',         (85,'and',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # tst if rd=1111 and s=1
    ('11110110001',         (85,'bic',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110110010',       (85,'orr',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110110011',         (85,'orn',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # mvn if rn=1111
    ('11110110100',         (85,'eor',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110110110',         (85,'movt',     dp_bin_imm_32,        IF_W | IF_THUMB32)),  # teq if rd=1111 and s=1
    ('11110111000',         (85,'add',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # cmn if rd=1111 and s=1
    ('11110111010',         (85,'adc',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110111011',         (85,'sbc',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110111101',         (85,'sub',      dp_bin_imm_32,        IF_W | IF_THUMB32)),  # cmp if rd=1111 and s=1
    ('11110111110',         (85,'rsb',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
    ('11110111111',         (85,'',      dp_bin_imm_32,        IF_W | IF_THUMB32)),
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
thumb32min  = binary('11100')

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
    def __init__(self, doModeSwitch=True, endian=ENDIAN_LSB):
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
            #print opcode, mnem, opermkr, flags
        except TypeError:
            raise envi.InvalidInstruction(
                    mesg="disasm parser cannot find instruction",
                    bytez=bytez[offset:offset+2], va=va)

        #print "FLAGS: ", hex(va),hex(flags)
        if flags & IF_THUMB32:
            val2, = struct.unpack_from(self.hfmt, bytez, offset+2)
            cond, nopcode, nmnem, olist, nflags, simdflags = opermkr(va+4, val, val2)

            if nmnem != None:   # allow opermkr to set the mnem
                mnem = nmnem
                opcode = nopcode
            if nflags != None:
                flags = nflags
                #print "FLAGS: ", repr(olist), repr(flags)
            oplen = 4
            # print "OPLEN: ", oplen

        else:
            cond, olist, nflags = opermkr(va+4, val)
            if nflags != None:
                flags = nflags
                #print "FLAGS: ", repr(olist), repr(flags)
            oplen = 2
            # print "OPLEN (16bit): ", oplen

        # since our flags determine how the instruction is decoded later....  
        # performance-wise this should be set as the default value instead of 0, but this is cleaner
        if not (flags & envi.ARCH_MASK):
            flags |= self._optype

        #print opcode, mnem, olist, flags
        if (olist != None and 
                len(olist) and 
                isinstance(olist[0], ArmRegOper) and
                olist[0].involvesPC() and 
                opcode not in no_update_Rd ):
            
            showop = True
            flags |= envi.IF_NOFALL

        if mnem == None or type(mnem) == int:
            raise Exception("mnem == %r!  0x%xi (thumb)" % (mnem, opval))

        op = ThumbOpcode(va, opcode, mnem, cond, oplen, olist, flags, simdflags)
        #print hex(va), oplen, len(op), op.size, hex(op.iflags)
        return op

class Thumb16Disasm ( ThumbDisasm ):
    _tree = ttree
    _optype = envi.ARCH_THUMB16
    _opclass = Thumb16Opcode

if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( Thumb16Disasm() )
