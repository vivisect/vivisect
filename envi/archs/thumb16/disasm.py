
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
        return (ret), None

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
    return (ArmRegOper(rd, va=va),ArmRegOper(rm, va=va)), None

def rm_rn_rt(va, value):
    rt = shmaskval(value, 0, 0x7) # target
    rn = shmaskval(value, 3, 0x7) # base
    rm = shmaskval(value, 6, 0x7) # offset
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmRegOffsetOper(rn, rm, va, pubwl=0x18)
    return (oper0,oper1), None

def imm54_rn_rt(va, value):
    imm = shmaskval(value, 4, 0x7c)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return (oper0,oper1), None

def imm55_rn_rt(va, value):
    imm = shmaskval(value, 5, 0x3e)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return (oper0,oper1), None

def imm56_rn_rt(va, value):
    imm = shmaskval(value, 6, 0x1f)
    rn = shmaskval(value, 3, 0x7)
    rt = shmaskval(value, 0, 0x7)
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return (oper0,oper1), None

def rd_sp_imm8(va, value): # add
    rd = shmaskval(value, 8, 0x7)
    imm = shmaskval(value, 0, 0xff) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOffsetOper(REG_SP, imm, (va&0xfffffffc)+4, pubwl=0x18)
    return (oper0,oper1), None

def rd_pc_imm8(va, value):  # add
    rd = shmaskval(value, 8, 0x7)
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 4
    oper0 = ArmRegOper(rd, va=va)
    # pre-compute PC relative addr
    oper1 = ArmImmOper((va&0xfffffffc) + 4 + imm)
    return (oper0,oper1), None

def rt_pc_imm8(va, value): # ldr
    rt = shmaskval(value, 8, 0x7)
    imm = e_bits.signed((value & 0xff), 1) << 2
    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(REG_PC, imm, (va&0xfffffffc))
    return (oper0,oper1), None


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
        1: (INS_YIELD, 'yielD',),
        2: (INS_WFE, 'wfe',),
        3: (INS_WFI, 'wfi',),
        4: (INS_SEV, 'sev',),
        }

def branch_misc(va, val, val2): # bl and misc control
    op = (val >> 4) & 0b1111111
    op1 = (val2 >> 12) & 0b111
    op2 = (val2 >> 8) & 0b1111
    imm8 = val2 & 0b1111

    print hex(va), hex(val), hex(val2), bin(op), bin(op1), bin(op2)

    if (op1 & 0b101 == 0):
        if not (op & 0b111000) == 0b111000: # T3 encoding - conditional
            cond = (val>>6) & 0xf
            opcode, mnem, nflags = bcc_ops.get(cond)
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
            return opcode, mnem, (oper0, ), flags, 0

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
                return None, 'msr', opers, None, 0

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
                return None, 'mrs', opers, None, 0

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
                    return None, 'sub', opers, IF_PSR_S, 0

                return None, 'eret', tuple(), IF_RET, 0    # should this have some other flag?
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
                return None, 'msr', opers, None, 0


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
                        mnem = "CPS Hint...  no clue yet.  fix me"
                        
                    if imod & 2:
                        opers = [
                            ArmCPSFlagsOper(aif)    # if mode is set...
                        ]
                    else:
                        opers = []
                    if m:
                        opers.append(ArmImmOper(mode))

                else:
                    opcode, mnem = cpsh_mnems.get(op2, (INS_DEBUGHINT, 'dbg'))

                #raise Exception("FIXME:  Change processor state ad hints p A6-234")
                return opcode, mnem, opers, flags, 0

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
                return None, 'sub', opers, IF_PSR_S, 0

            elif op == 0b0111110:
                Rd = (val2 >> 8) & 0xf
                opers = (
                        ArmRegOper(Rd),
                        ArmRegOper(REG_OFFSET_CPSR),
                        )
                return None, 'mrs', opers, None, 0

            elif op == 0b0111111:
                Rd = (val2 >> 8) & 0xf
                R = (val >> 4) & 1
                opers = (
                        ArmRegOper(Rd),
                        ArmRegOper(REG_OFFSET_CPSR),
                        )

                raise Exception("FIXME:  MRS(register) p B9-1962 - how is R used?")
                return None, 'mrs', opers, None, 0

            elif op == 0b1111110:
                if op1 == 0:
                    imm4 = val & 0xf
                    imm12 = val2 & 0xfff
                    oper0 = ArmImmOper((imm4<<12)|imm12)
                    return None, 'hvc', (oper0,), None, 0

                raise InvalidInstruction(
                    mesg="branch_misc subsection 1",
                    bytez=struct.pack("<HH", val, val2), va=va-4)


            elif op == 0b1111111:
                if op1 == 0:
                    imm4 = val & 0xf
                    oper0 = ArmImmOper(imm4)
                    return None, 'smc', (oper0,), None, 0

                raise InvalidInstruction(
                    mesg="branch_misc subsection 1",
                    bytez=struct.pack("<HH", val, val2), va=va-4)



    elif op1 & 0b101 == 1:  # T4 encoding
        opcode = INS_B
        flags = envi.IF_BRANCH | IF_W

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
        return opcode, 'b', (oper0, ), flags, 0

    elif op1 == 0b010:
        if op == 0b1111111:
            raise Exception("FIXME:  UDF (permanently undefined) p B9-1972")
        raise InvalidInstruction(
            mesg="branch_misc subsection 6",
            bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)

    elif op1 & 0b100:
        # bl/blx
        x = (val2>>12) & 1
        s = (val>>10) & 1
        mnem = ('blx','bl')[x]
        opcode = (INS_BLX,INS_BL)[x]
        flags = envi.IF_CALL | IF_W

        # need next two bytes
        j1 = not ((val2>>13)&1 ^ s)
        j2 = not ((val2>>11)&1 ^ s)

        imm = (s<<24) | (j1<<23) | (j2<<22) | ((val&0x3ff) << 12) | ((val2&0x7ff) << 1)

        #sign extend a 23-bit number
        if s:
            imm |= 0xff000000

        oper0 = ArmPcOffsetOper(e_bits.signed(imm,4), va=va)

        return opcode, mnem, (oper0, ), flags, 0
        


    
    raise InvalidInstruction(
        mesg="branch_misc Branches and Miscellaneous Control: Failed to match",
        bytez=struct.pack("<H", val)+struct.pack("<H", val2), va=va-4)


def pc_imm11(va, value): # b
    imm = e_bits.signed(((value & 0x7ff)<<1), 3)
    oper0 = ArmPcOffsetOper(imm, va=va)
    return (oper0,), None

def pc_imm8(va, value): # b
    imm = e_bits.signed(shmaskval(value, 0, 0xff), 1) * 2
    oper0 = ArmPcOffsetOper(imm, va=va)
    return (oper0,), None

def ldmia(va, value): 
    rd = shmaskval(value, 8, 0x7)
    reg_list = value & 0xff
    oper0 = ArmRegOper(rd, va=va)
    oper1 = ArmRegListOper(reg_list)
    oper0.oflags |= OF_W
    return (oper0,oper1), None

def sp_sp_imm7(va, value):
    imm = shmaskval(value, 0, 0x7f)
    o0 = ArmRegOper(REG_SP)
    o1 = ArmRegOper(REG_SP)
    o2 = ArmImmOper(imm*4)
    return (o0,o1,o2), None

def rm_reglist(va, value):
    rm = shmaskval(value, 8, 0x7)
    reglist = value & 0xff
    oper0 = ArmRegOper(rm, va=va)
    oper1 = ArmRegListOper(reglist)
    oper0.oflags |= OF_W
    return (oper0,oper1), None

def pop_reglist(va, value):
    flags = 0
    reglist = (value & 0xff) | ((value & 0x100)<<7)
    oper0 = ArmRegListOper(reglist)
    if reglist & 0x8000:
        flags |= envi.IF_NOFALL
    
    return (oper0,), flags

def push_reglist(va, value):
    reglist = (value & 0xff) | ((value & 0x100)<<6)
    oper0 = ArmRegListOper(reglist)
    return (oper0,), None

def imm5_rm_rd(va, value):
    rd = value & 0x7
    rm = (value >> 3) & 0x7
    imm5 = (value >> 6) & 0x1f

    stype = value >> 11

    oper0 = ArmRegOper(rd, va)
    oper1 = ArmRegShiftImmOper(rm, stype, imm5, va)
    return (oper0, oper1,), None


def i_imm5_rn(va, value):
    imm5 = shmaskval(value, 3, 0x40) | shmaskval(value, 2, 0x3e)
    rn = value & 0x7
    oper0 = ArmRegOper(rn, va)
    oper1 = ArmPcOffsetOper(imm5, va)
    return (oper0, oper1,), None

def ldm16(va, value):
    raise Exception("32bit wrapping of 16bit instruction... and it's not implemented")

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
    return opcode, mnem, opers, flags, 0


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
    return opcode, mnem, opers, flags, 0

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

    return ( opcode, mnem, olist, flags, 0 )

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
            None, # orr
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
    const = val2 & 0xff

    if S:
        flags |= IF_PSR_S

    const,carry = ThumbExpandImm_C(imm4, const, 0)
    
    if Rd==15 and S:
        #raise Exception("dp_mod_imm_32 - FIXME: secondary dp encoding")
        dpop = (val1>>5) & 0xf
        mnem = dp_secondary[dpop]
        if mnem == None:
            raise Exception("dp_mod_imm_32: Rd==15, S, but dpop doesn't have a secondary! va:%x, %x%x" % (va, val1, val2))

        oper1 = ArmRegOper(Rn)
        oper2 = ArmImmOper(const)
        opers = (oper1, oper2)
        return 0, mnem, opers, flags, 0

    oper0 = ArmRegOper(Rd)
    oper1 = ArmRegOper(Rn)
    oper2 = ArmImmOper(const)
    opers = (oper0, oper1, oper2)
    return None, None, opers, flags, 0

def shift_or_ext_32(va, val1, val2):
    if (val2 & 0xf000) != 0xf000:
        raise Exception("pdp_32 needs to hand off for val2 & 0xf000 != 0xf000 at va 0x%x: val1:%.4x val2:%.4x" % (va, val1, val2))

    op2 = (val2>>4) & 0xf
    if (op2):
        raise Exception("Implement Me: Extended and Add stuff")

    else:
        # lsl/lsr/asr/ror
        flags = 0
        op1 = (val1>>4) & 0xf
        opcode, mnem, nothing = mov_ris_ops[op1>>1]

        rn = (val1 & 0xf)
        rd = (val2 >> 8) & 0xf
        rm = (val2 & 0xf)

        opers = (
                ArmRegOper(rd),
                ArmRegOper(rn),
                ArmRegOper(rm),
                )

        if (op1 & 1):
            flags |= IF_PSR_S
        return opcode, mnem, opers, flags, 0



def pdp_32(va, val1, val2):
    # saturated instructions
    raise Exception("Implement Me: pdp32: Saturated Instrs")
    pass

    return None, None, None, None, None

def dp_bin_imm_32(va, val1, val2):
    if val2 & 0x8000:
        return branch_misc(va, val1,val2)

    flags = IF_THUMB32
    # FIXME: decoding incorrectly
    Rd = (val2 >> 8) & 0xf

    Rn = val1 & 0xf
    imm4 = val1 & 0xf
    i = (val1 >> 10) & 1
    imm3 = (val2 >> 12) & 0x7
    const = val2 & 0xff
    if Rn==15 and (val1 & 0b111110000) in (0,0b1010):   # add/sub
        # adr
        return None, 'adr', opers, None, 0


    const |= (imm4 << 12) | (i << 11) | (imm3 << 8)
    
    oper0 = ArmRegOper(Rd)
    oper1 = ArmRegOper(Rd)
    oper2 = ArmImmOper(const)
    opers = (oper0, oper1, oper2)
    return None, None, opers, flags, 0

def ldm_reg_mode_32(va, val1, val2):
    rn = val1 & 0xf
    mode = val2 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    oper1 = ArmModeOper(mode, wback)
    opers = (oper0, oper1)
    return None, None, opers, None, 0

def ldm_reg_32(va, val1, val2):
    rn = val1 & 0xf
    wback = (val1 >> 5) & 1

    oper0 = ArmRegOper(rn, va=va)
    if wback:
        oper0.oflags = OF_W
    opers = (oper0,)
    return None, None, opers, None, 0

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
    return None, None, opers, None, 0

def pop_32(va, val1, val2):
    if val2 & 0x2000:
        raise InvalidInstruction("LDM instruction with stack indicated: 0x%x: 0x%x, 0x%x" % (va, val1, val2))
        # PC not ok on some instructions...  
    oper0 = ArmRegListOper(val2)
    opers = (oper0, )
    return None, None, opers, None, 0

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
    return None, None, opers, flags, 0

def ldr_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm12 = val2 & 0xfff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm12, va=va)

    opers = (oper0, oper1)
    return None, None, opers, None, 0

def ldr_puw_32(va, val1, val2):
    b11 = (val2>>11) & 1
    if not b11:
        raise Exception("ldr_puw_32 parsing non-ldrb")

    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    puw = (val2>>8) & 0x7
    pubwl = ((puw&1) | ((puw&0x6)<<1)) << 1

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8, va=va, pubwl=pubwl)

    opers = (oper0, oper1)
    return None, None, opers, None, 0

def ldrex_32(va, val1, val2):
    rn = val1 & 0xf
    rt = (val2 >> 12) & 0xf
    imm8 = val2 & 0xff

    oper0 = ArmRegOper(rt, va=va)
    oper1 = ArmImmOffsetOper(rn, imm8<<2, va=va)

    opers = (oper0, oper1)
    flags = 0
    return None, None, opers, flags, 0

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
    return None, None, opers, flags, 0

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
    return 0, mnem, opers, flags, 0

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
    return None, mnem, opers, None, 0

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

        oper0 = ArmRegOper(rn, va=va)
        oper1 = ArmRegOper(rm, va=va)
        opers = (oper0, oper1)

    return opcode, mnem, opers, flags, 0

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

    return opcode, mnem, opers, flags, 0


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
    flags = 0
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

    return opcode, mnem, opers, flags, 0

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

    return opcode, mnem, opers, flags, 0

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
            CRn =       val2 & 0xf
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
            
            # FIXME: DO WE WANT ALL adv_simd to be decoded in the adv_simd_32 function?  or individual functions?  not here.
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
            imm32 = (val2 & 0xff) << 2

            # size = 0/1 for 32-bit and 64-bit accordingly
            size = (val2>>8) & 1    # TODO: Check next three bits must be 0b101

            pudwl = op1 & 0b11111

            # starting extended register
            D = (pudwl>>2) & 1
            Vd = val2>>12
            d = (Vd << 1) | D

            # vpush/vpop
            if (op1 & 0b11011) in (0b01011, 0b10010) and Rn == REG_SP:
                mnem = ('vpush', 'vpop')[l]
                opers = (
                        ArmExtRegListOper(d, imm32, size),
                        )

            else:
                oflags = 0

                mnemidx = l | (indiv<<1)
                mnem = ('vstm','vldm','vstr','vldr')[mnemidx]
                # figure out IA/DB/etc...  and Writeback

                # inc-after or dec-before?
                ia = (pudwl>>3) & 3       # PU determine IA/DB
                iflags |= (0, IF_IA, IF_DB, 0)[ia]

                # write-back to original reg?
                w = (pudwl >> 1) & 1
                if w:
                    oflags |= OF_W   # writeback flag for ArmRegOper

                if indiv:
                    rbase = ('S%d', 'D%d')[size]
                    VRd = rctx.getRegisterIndex(rbase % d)
                    opers = (
                            ArmRegOper(VRd, va=va, oflags=oflags),
                            ArmImmOffsetOper(Rn, imm32, va=va, pubwl=pudwl),
                            )

                else:
                    opers = (
                            ArmRegOper(Rn, va=va, oflags=oflags),
                            ArmExtRegListOper(d, imm32, size),
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

    return (opcode, mnem, opers, iflags, simdflags)

def fp_dp(va, val1, val2):
    opcode = 0
    iflags = 0
    simdflags = 0

    opc1 = (val1>>4) & 0xf
    opc2 = val1 & 0xf
    opc3 = (val2>>6) & 3
    opc4 = val2 & 0xf

    opc1sub = opc1 & 0b1011

    D = (val1 >> 6) & 1
    N = (val2 >> 7) & 1
    M = (val2 >> 5) & 1
    Vd = (val2 >> 12) & 0xf
    Vn = opc2 #val1 & 0xf
    Vm = opc4 #val2 & 0xf

    sz = (val2 >> 8) & 1

    if opc1sub != 0b1011:
        op = (opc1sub & 0b1000) | ((opc1sub & 0b11)<<1) | (opc3 & 1)
        mnem = ('vmla','vmls','vnmla','vnmls','vnmul','vmul','vadd','vsub','vdiv','vfnms','vfnma','vfms','vfma',)[op]

        

        if sz:
            d = (D<<4) | Vd
            m = (M<<4) | Vm
            n = (N<<4) | opc2 #Vn
        else:
            d = (Vd<<1) | D
            m = (Vm<<1) | M
            n = (opc2<<1) | N

        # D and S, depending on sz
        rbase = ("S%d","D%d")[sz]
        simdflags |= (IFS_F32, IFS_F64)[sz]

        # VMLA, VMLS p930
        # VNMLA, VNMLS T1/A1, VNMUL T2/A2, p 968
        # VMUL p958 - T2/A2 encoding
        # VADD p 828
        # VSUB p1084
        # VDIV p880
        # VFNMA, VFNMS p892
        # VFMA, VFMS p890
        opers = (   
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmRegOper(rctx.getRegisterIndex(rbase%n)),
                ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                )

    else:
        # VMOV p934
        D = (val1 >> 6) & 1
        Vd = (val2 >> 12) & 0xf
        imm4h = val1 & 0xf
        imm4l = val2 & 0xf

        if sz:
            d = (D<<4) | Vd
            m = (M<<4) | Vm
            imm = imm4h<<4 | imm4l
            simdflags |= IFS_F64
            rbase = "D%d"
        else:
            d = (Vd<<1) | D
            m = (Vm<<1) | M
            imm = imm4h<<4 | imm4l
            simdflags |= IFS_F32
            rbase = "S%d"

        if opc3 & 1 == 0:
            mnem = 'vmov'
            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmImmOper(imm),
                    )

        elif opc2 == 0:
            # VMOV p935 with reg/reg
            if opc3 & 1:
                mnem = 'vmov'

            # VABS p822 T2/A2
            elif opc3 == 3:
                mnem = 'vabs'

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        elif opc2 == 1:
            # VNEG p966 T2/A2
            if opc3 == 0x1:
                mnem = 'vneg'

            # VSQRT p1056
            elif opc3 == 0x3:
                mnem = 'vsqrt'

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        # VCVTB, VCVTT p878
        elif opc2 in (2,3) and opc3 in (1,3):
            T = N
            simdflags |= (IFS_F1632, IFS_F3216)[val1&1]
            mnem = ('vcvtb','vcvtt')[T]

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        # VCMP, VCMPE p862
        elif opc2 in (4,5) and opc3 in (1,3):
            E = N
            mnem = ('vcmp','vcmpe')[E]
            
            if opc2 == 4:
                opers = (
                        ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                        ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                        )
            else:
                opers = (
                        ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                        ArmImmFPOper(0.0),
                        )

        # VCVT p874
        elif opc2 == 7 and opc3 == 3:
            mnem = 'vcvt'
            if sz:
                d = (Vd<<1) | D
                m = (M<<4) | Vm
                simdflags |= IFS_F32F64
                rbase1 = "S%d"
                rbase2 = "D%d"
            else:
                d = (D<<4) | Vd
                m = (Vm<<1) | M
                simdflags |= IFS_F64F32
                rbase1 = "D%d"
                rbase2 = "S%d"

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase1%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase2%m)),
                    )

        # VCVT, VCVTR p868
        elif opc2 in (0b1000,0b1100,0b1101) and opc3 & 1:
            op = opc3>>1
            # S32F64, S32F32, U32F64, U32F32, F64TM, F32TM??
            to_int = opc2 & 0b100
            if to_int:
                mnem = 'vcvtr'
                signed = opc2&1
                round_zero = op

                d = (Vd<<1) | D
                if sz:
                    m = (M<<4) | Vm
                    simdflags |= (IFS_U32F64, IFS_S32F64)[signed]
                    rbase1 = "S%d"
                    rbase2 = "D%d"
                else:
                    m = (Vm<<1) | M
                    simdflags |= (IFS_U32F32, IFS_S32F32)[signed]
                    rbase1 = "S%d"
                    rbase2 = "S%d"

            else:
                mnem = 'vcvt'
                signed = op
                round_nearest = False
                m = (Vm<<1) | M
                if sz:
                    d = (D<<4) | Vd
                    simdflags |= (IFS_F64U32, IFS_F64S32)[signed]
                    rbase1 = "D%d"
                    rbase2 = "S%d"
                else:
                    d = (Vd<<1) | D
                    simdflags |= (IFS_F32U32, IFS_F32S32)[signed]
                    rbase1 = "S%d"
                    rbase2 = "S%d"

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase1%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase2%m)),
                    )

        # VCVT p872
        elif opc2 in (0b1010,0b1011,0b1110,0b1111) and opc3&1:
            mnem = 'vcvt'
            U = (val1>>12) & 1 # thumb only.  arm gets U from bit 22
            imm6 = val1 & 0x3f
            op = sz
            Q = opc3

            if imm6 & 0b000111:
                raise InvalidInstruction('fp/adv simd parsing error.  alternate encoding p267.',va=va, bytez=bytez)
            if imm6 & 0b011111:
                raise InvalidInstruction('fp/adv simd parsing error.  undefined behavior.',va=va, bytez=bytez)

            if op:      # FIXME: not sure what to do with these.
                #round_zero = True  - like, what does this mean?
                if U:
                    simdflags |= IFS_U32F32
                else:
                    simdflags |= IFS_S32F32
            else:
                #round_nearest = True
                if U:
                    simdflags |= IFS_F32U32
                else:
                    simdflags |= IFS_F32S32

            #esize = 32
            frac_bits = 64 - imm6
            #elements = 2

            d = (D<<4) | Vd
            m = (M<<4) | Vm

            if Q:
                rbase = "Q%d"
            else:
                rbase = "D%d"

            #regs = Q + 1


            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    ArmImmOper(frac_bits),
                    )

    return (opcode, mnem, opers, iflags, simdflags)

from envi.archs.arm.disasm import _do_adv_simd_32

def adv_simd_32(va, val1, val2):
    val = (val1 << 16) | val2
    u = (val1 >> 12) & 1
    return _do_adv_simd_32(val, va, u)

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

        rbase = ('D%d', 'Q%d')[q]

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

        return opcode, mnem, opers, 0, simdflags


bcc_ops = {
    0b0000:    (INS_BCC,'beq',  envi.IF_COND),
    0b0001:    (INS_BCC,'bn',   envi.IF_COND),
    0b0010:    (INS_BCC,'bhs',  envi.IF_COND),
    0b0011:    (INS_BCC,'blo',  envi.IF_COND),
    0b0100:    (INS_BCC,'bmi',  envi.IF_COND),
    0b0101:    (INS_BCC,'bpl',  envi.IF_COND),
    0b0110:    (INS_BCC,'bvs',  envi.IF_COND),
    0b0111:    (INS_BCC,'bvc',  envi.IF_COND),
    0b1000:    (INS_BCC,'bhi',  envi.IF_COND),
    0b1001:    (INS_BCC,'bls',  envi.IF_COND),
    0b1010:    (INS_BCC,'bge',  envi.IF_COND),
    0b1011:    (INS_BCC,'blt',  envi.IF_COND),
    0b1100:    (INS_BCC,'bgt',  envi.IF_COND),
    0b1101:    (INS_BCC,'ble',  envi.IF_COND),
    0b1110:    (INS_B,'b',      envi.IF_NOFALL),
    }


# opinfo is:
# ( <mnem>, <operdef>, <flags> )
# operdef is:
# ( (otype, oshift, omask), ...)

# FIXME: thumb and arm opcode numbers don't line up. - FIX
thumb_base = [
    ('00000',       ( 0,'lsl',     imm5_rm_rd, 0)), # LSL<c> <Rd>,<Rm>,#<imm5>
    ('00001',       ( 1,'lsr',     imm5_rm_rd, 0)), # LSR<c> <Rd>,<Rm>,#<imm>
    ('00010',       ( 2,'asr',     imm5_rm_rd, 0)), # ASR<c> <Rd>,<Rm>,#<imm>
    ('0001100',     ( INS_ADD,'add',     rm_rn_rd,   0)), # ADD<c> <Rd>,<Rn>,<Rm>
    ('0001101',     ( INS_SUB,'sub',     rm_rn_rd,   0)), # SUB<c> <Rd>,<Rn>,<Rm>
    ('0001110',     ( INS_ADD,'add',     imm3_rn_rd, 0)), # ADD<c> <Rd>,<Rn>,#<imm3>
    ('0001111',     ( INS_SUB,'sub',     imm3_rn_rd, 0)), # SUB<c> <Rd>,<Rn>,#<imm3>
    ('00100',       ( 7,'mov',     imm8_rd,    0)), # MOV<c> <Rd>,#<imm8>
    ('00101',       ( 8,'cmp',     imm8_rd,    0)), # CMP<c> <Rn>,#<imm8>
    ('00110',       ( INS_ADD,'add',     imm8_rd,    0)), # ADD<c> <Rdn>,#<imm8>
    ('00111',       (INS_SUB,'sub',     imm8_rd,    0)), # SUB<c> <Rdn>,#<imm8>
    # Data processing instructions
    ('0100000000',  (11,'and',     rm_rdn,     0)), # AND<c> <Rdn>,<Rm>
    ('0100000001',  (12,'eor',     rm_rdn,     0)), # EOR<c> <Rdn>,<Rm>
    ('0100000010',  (13,'lsl',     rm_rdn,     0)), # LSL<c> <Rdn>,<Rm>
    ('0100000011',  (14,'lsr',     rm_rdn,     0)), # LSR<c> <Rdn>,<Rm>
    ('0100000100',  (15,'asr',     rm_rdn,     0)), # ASR<c> <Rdn>,<Rm>
    ('0100000101',  (16,'adc',     rm_rdn,     0)), # ADC<c> <Rdn>,<Rm>
    ('0100000110',  (17,'sbc',     rm_rdn,     0)), # SBC<c> <Rdn>,<Rm>
    ('0100000111',  (18,'ror',     rm_rdn,     0)), # ROR<c> <Rdn>,<Rm>
    ('0100001000',  (19,'tst',     rm_rd,      0)), # TST<c> <Rn>,<Rm>
    ('0100001001',  (20,'rsb',     rm_rd_imm0, 0)), # RSB<c> <Rd>,<Rn>,#0
    ('0100001010',  (21,'cmp',     rm_rd,      0)), # CMP<c> <Rn>,<Rm>
    ('0100001011',  (22,'cmn',     rm_rd,      0)), # CMN<c> <Rn>,<Rm>
    ('0100001100',  (23,'orr',     rm_rdn,     0)), # ORR<c> <Rdn>,<Rm>
    ('0100001101',  (24,'mul',     rn_rdm,     0)), # MUL<c> <Rdm>,<Rn>,<Rdm>
    ('0100001110',  (25,'bic',     rm_rdn,     0)), # BIC<c> <Rdn>,<Rm>
    ('0100001111',  (26,'mvn',     rm_rd,      0)), # MVN<c> <Rd>,<Rm>
    # Special data in2tructions and branch and exchange
    ('0100010000',  (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('0100010001',  (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('010001001',   (INS_ADD,'add',     d1_rm4_rd3, 0)), # ADD<c> <Rdn>,<Rm>
    ('010001010',   (30,'cmp',     d1_rm4_rd3, 0)), # CMP<c> <Rn>,<Rm>
    ('010001011',   (31,'cmp',     d1_rm4_rd3, 0)), # CMP<c> <Rn>,<Rm>
    ('01000110',    (34,'mov',     d1_rm4_rd3, 0)), # MOV<c> <Rd>,<Rm>
    ('010001110',   (35,'bx',      rm4_shift3, envi.IF_NOFALL)), # BX<c> <Rm>
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
    ('10110110011', (58,'cps',     simpleops(),0)), # CPS<effect> <iflags> FIXME
    ('10110001',    (59,'cbz',     i_imm5_rn,  0)), # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111001',    (60,'cbnz',    i_imm5_rn,  0)), # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
    ('10110011',    (59,'cbz',     i_imm5_rn,  0)), # CBZ{<q>} <Rn>, <label>    # label must be positive, even offset from PC
    ('10111011',    (60,'cbnz',    i_imm5_rn,  0)), # CBNZ{<q>} <Rn>, <label>   # label must be positive, even offset from PC
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
    ('11010000',    (INS_BCC,'beq',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010001',    (INS_BCC,'bn',      pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010010',    (INS_BCC,'bhs',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010011',    (INS_BCC,'blo',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010100',    (INS_BCC,'bmi',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010101',    (INS_BCC,'bpl',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010110',    (INS_BCC,'bvs',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11010111',    (INS_BCC,'bvc',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011000',    (INS_BCC,'bhi',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011001',    (INS_BCC,'bls',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011010',    (INS_BCC,'bge',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011011',    (INS_BCC,'blt',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011100',    (INS_BCC,'bgt',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011101',    (INS_BCC,'ble',     pc_imm8,       envi.IF_BRANCH|envi.IF_COND)),
    ('11011110',    (INS_B,'b',       pc_imm8,       envi.IF_BRANCH|envi.IF_NOFALL)),
    ('11011111',    (INS_BCC,'bfukt',   pc_imm8,       envi.IF_BRANCH|0)),
    # Software Interru2t
    ('11011111',    (INS_SWI,'svc',     imm8,       0)), # SWI <blahblah>
    ('1011111100000000',    (89,'nopHint',    imm8,       0)), #unnecessary instruction
    ('1011111100010000',    (90,'yieldHint',  imm8,       0)), #unnecessary instruction
    ('1011111100100000',    (91,'wfrHint',    imm8,       0)), #unnecessary instruction
    ('1011111100110000',    (92,'wfiHint',    imm8,       0)), #unnecessary instruction
    ('1011111101000000',    (93,'sevHint',    imm8,       0)), #unnecessary instruction
    ('101111110000',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110001',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110010',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110011',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110100',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110101',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110110',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111110111',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111000',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111001',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111010',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111011',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111100',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111101',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111110',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ('101111111111',       (94,'if-then-Hint',    imm8,       0)), #unnecessary instruction
    ]

thumb1_extension = [
    ('11100',       (INS_B,  'b',       pc_imm11,           envi.IF_BRANCH|envi.IF_NOFALL)),        # B <imm11>
    ('1111',        (INS_BL, 'bl',      branch_misc,       envi.IF_CALL | IF_THUMB32)),   # BL/BLX <addr25> 
]

###  holy crap, this is so wrong and imcomplete....
# FIXME: need to take into account ThumbEE 
# 32-bit Thumb instructions start with:
# 0b11101
# 0b11110
# 0b11111
thumb2_extension = [
    ('11100',       (85,'ldm',      ldm16,     0)),     # 16-bit instructions
    #('11101',       (86,'blah32',   thumb32_01,   IF_THUMB32)),         # can't do thumb32 in tree-fashion
    #('11110',       (86,'blah32',   thumb32_10,   IF_THUMB32)),         # op2 is sparse and op is part of 
    #('11111',       (86,'blah32',   thumb32_11,   IF_THUMB32)),         # second halfword
    # awww heck, let's use the tree for as much as possible.

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
    ('1110100010111101',(85,'pop',      pop_32,     IF_THUMB32|IF_W)), # 111101 - pop

    ('111010010000',    (85,'stm',  ldm_32,     IF_THUMB32)),   # stmdb/stmfd
    ('111010010001',    (85,'ldm',  ldm_32,     IF_THUMB32)),   # ldmdb/ldmea
    ('1110100100100',   (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('11101001001010',  (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('111010010010111', (85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('1110100100101100',(85,'stm',  ldm_32,     IF_THUMB32|IF_W|IF_DB)), # not 101101
    ('1110100100101101',(85,'push',     pop_32,     IF_THUMB32|IF_W)), # 101101 - push
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
    ('11101100',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),   # FIXME: not fully implemented
    ('11101101',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),   # FIXME: not fully implemented
    ('11101110',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),   # FIXME: not fully implemented
    ('11101111',            (85,'adv simd', adv_simd_32,        IF_THUMB32)),   # FIXME: not fully implemented
    ('11111110',            (85,'coproc simd', coproc_simd_32,  IF_THUMB32)),   # FIXME: not fully implemented
    ('11111111',            (85,'adv simd', adv_simd_32,        IF_THUMB32)),   # FIXME: not fully implemented

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
    ('1111001000',          (85,'add',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # adr if rn=1111
    ('1111001001',          (85,'mov',      dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('1111001010',          (85,'sub',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # adr if rn=1111
    ('1111001011',          (85,'movt',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110011000',         (85,'ssat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110011001',         (85,'ssat16',   dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110011010',         (85,'sbfx',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110011011',         (85,'bfi',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # bfc if rn=1111
    ('11110011100',         (85,'usat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110011101',         (85,'usat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),  # usat16 if val2=0000xxxx00xxxxxx
    ('1111001111',          (85,'ubfx',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('1111011000',          (85,'add',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # adr if rn=1111
    ('1111011001',          (85,'mov',      dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('1111011010',          (85,'sub',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # adr if rn=1111
    ('1111011011',          (85,'movt',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111000',         (85,'ssat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111001',         (85,'ssat16',   dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111010',         (85,'sbfx',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111011',         (85,'bfi',      dp_bin_imm_32,      IF_W | IF_THUMB32)),  # bfc if rn=1111
    ('11110111100',         (85,'usat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111101',         (85,'usat',     dp_bin_imm_32,      IF_W | IF_THUMB32)),  # usat16 if val2=0000xxxx00xxxxxx
    ('11110111110',         (85,'ubfx',     dp_bin_imm_32,      IF_W | IF_THUMB32)),
    ('11110111111',         (85,'branchmisc', branch_misc,      IF_THUMB32)),
    ('111110001001',        (INS_LDRB, 'ldrb', ldr_32,          IF_THUMB32)),
    ('111110001000',        (INS_STRB, 'strb', ldr_32,          IF_THUMB32)),
    ('111110000000',        (INS_STRB, 'strb', ldr_puw_32,      IF_THUMB32)),
    ('11111010001',         (INS_LSL, 'lsl', shift_or_ext_32,      IF_THUMB32)),
    ('11111010010',         (INS_LSR, 'lsr', shift_or_ext_32,      IF_THUMB32)),
    ('11111010011',         (INS_ASR, 'asr', shift_or_ext_32,      IF_THUMB32)),
    ('11111010100',         (INS_ROR, 'ror', shift_or_ext_32,      IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),    # FIXME: overlapping with saturating instructions
    ('111110101010',        (INS_UASX, 'uasx', pdp_32,         IF_THUMB32)),
    ('111110101110',        (INS_USAX, 'usax', pdp_32,         IF_THUMB32)),
    ('111110101101',        (INS_USUB16, 'usub16', pdp_32,         IF_THUMB32)),
    ('111110101000',        (INS_UADD8, 'uadd8', pdp_32,         IF_THUMB32)),
    ('111110101100',        (INS_USUB8, 'usub8', pdp_32,         IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),
    ('111110101001',        (INS_UADD16, 'uadd16', pdp_32,         IF_THUMB32)),
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
            # print opcode, mnem, opermkr, flags
        except TypeError:
            raise envi.InvalidInstruction(
                    mesg="disasm parser cannot find instruction",
                    bytez=bytez[offset:offset+2], va=va)

        #print "FLAGS: ", hex(va),hex(flags)
        if flags & IF_THUMB32:
            val2, = struct.unpack_from(self.hfmt, bytez, offset+2)
            nopcode, nmnem, olist, nflags, simdflags = opermkr(va+4, val, val2)

            if nmnem != None:   # allow opermkr to set the mnem
                mnem = nmnem
                opcode = nopcode
            if nflags != None:
                flags = nflags
            oplen = 4
            # print "OPLEN: ", oplen

        else:
            olist, nflags = opermkr(va+4, val)
            if nflags != None:
                flags = nflags
                print "FLAGS: ", repr(olist), repr(flags)
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

        op = ThumbOpcode(va, opcode, mnem, 0xe, oplen, olist, flags, simdflags)
        #print hex(va), oplen, len(op), op.size
        return op

class Thumb16Disasm ( ThumbDisasm ):
    _tree = ttree
    _optype = envi.ARCH_THUMB16
    _opclass = Thumb16Opcode

if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( Thumb16Disasm() )
