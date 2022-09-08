import sys
import struct
import traceback

import envi
import envi.bits as e_bits

from envi.archs.arm.const import *
from envi.archs.arm.regs import *

# FIXME:   codeflow needs to identify the following pattern as a call with fallthrough
#          (currently identifying the xref and making the fallthrough into a function):
#           mov lr, pc
#           sub pc, <blah>

# Possible future extensions: 
#   * VectorPointFloat subsystem (coproc 10+11)
#   * Debug subsystem (coproc 14)
#   * other 'default' coprocs we can handle and add value?

# FIXME this seems to be universal...
def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym is not None:
        return repr(sym)
    return "0x%.8x" % va


# The keys in this table are made of the
# concat of bits 27-21 and 7-4 (only when
# ienc == mul!
iencmul_codes = {
    # Basic multiplication opcodes
    0b000000001001: ("mul",   INS_MUL,  (0, 4, 2), 0),
    0b000000011001: ("mul",   INS_MUL,  (0, 4, 2), IF_PSR_S),
    0b000000101001: ("mla",   INS_MLA,  (0, 4, 2, 1), 0),
    0b000000111001: ("mla",   INS_MLA,  (0, 4, 2, 1), IF_PSR_S),
    0b000001101001: ("mls",   INS_MLS,  (0, 4, 2, 1), 0),
    0b000001001001: ("umaal", INS_UMAAL,(1, 0, 4, 2), 0),
    0b000010001001: ("umull", INS_UMULL, (1, 0, 4, 2), 0),
    0b000010011001: ("umull", INS_UMULL, (1, 0, 4, 2), IF_PSR_S),
    0b000010101001: ("umlal", INS_UMLAL, (1, 0, 4, 2), 0),
    0b000010111001: ("umlal", INS_UMLAL, (1, 0, 4, 2), IF_PSR_S),
    0b000011001001: ("smull", INS_SMULL, (1, 0, 4, 2), 0),
    0b000011011001: ("smull", INS_SMULL, (1, 0, 4, 2), IF_PSR_S),
    0b000011101001: ("smlal", INS_SMLAL, (1, 0, 4, 2), 0),
    0b000011111001: ("smlal", INS_SMLAL, (1, 0, 4, 2), IF_PSR_S),

    # multiplys with <x><y>
    # "B
    0b000100001000: ("smlabb", INS_SMLABB, (0, 4, 2, 1), 0),
    0b000100001010: ("smlatb", INS_SMLATB, (0, 4, 2, 1), 0),
    0b000100001100: ("smlabt", INS_SMLABT, (0, 4, 2, 1), 0),
    0b000100001110: ("smlatt", INS_SMLATT, (0, 4, 2, 1), 0),
    0b000100101010: ("smulwb", INS_SMULWB, (0, 4, 2), 0),
    0b000100101110: ("smulwt", INS_SMULWT, (0, 4, 2), 0),
    0b000100101000: ("smlawb", INS_SMLAWB, (0, 4, 2), 0),
    0b000100101100: ("smlawt", INS_SMLAWT, (0, 4, 2), 0),
    0b000101001000: ("smlalbb",INS_SMLALBB, (1, 0, 4, 2), 0),
    0b000101001010: ("smlaltb",INS_SMLALTB, (1, 0, 4, 2), 0),
    0b000101001100: ("smlalbt",INS_SMLALBT, (1, 0, 4, 2), 0),
    0b000101001110: ("smlaltt",INS_SMLALTT, (1, 0, 4, 2), 0),
    0b000101101000: ("smulbb", INS_SMULBB, (0, 4, 2), 0),
    0b000101101010: ("smultb", INS_SMULTB, (0, 4, 2), 0),
    0b000101101100: ("smulbt", INS_SMULBT, (0, 4, 2), 0),
    0b000101101110: ("smultt", INS_SMULTT, (0, 4, 2), 0),

    # type 2 multiplys

    0b011100000001: ("smuad",  INS_SMUAD, (0, 4, 2), 0),
    0b011100000011: ("smuadx", INS_SMUADX, (0, 4, 2), 0),
    0b011100000101: ("smusd",  INS_SMUSD, (0, 4, 2), 0),
    0b011100000111: ("smusdx", INS_SMUSDX, (0, 4, 2), 0),
    0b011100000001: ("smlad",  INS_SMLAD, (0, 4, 2, 1), 0),
    0b011100000011: ("smladx", INS_SMLADX, (0, 4, 2, 1), 0),
    0b011100000101: ("smlsd",  INS_SMLSD, (0, 4, 2, 1), 0),
    0b011100000111: ("smlsdx", INS_SMLSDX, (0, 4, 2, 1), 0),
    0b011101000001: ("smlald", INS_SMLALD, (1, 0, 4, 2), 0),
    0b011101000011: ("smlaldx",INS_SMLALDX, (1, 0, 4, 2), 0),
    0b011101000101: ("smlsld", INS_SMLSLD, (1, 0, 4, 2), 0),
    0b011101000111: ("smlsldx",INS_SMLSLDX, (1, 0, 4, 2), 0),
    0b011101010001: ("smmla",  INS_SMMLA, (0, 4, 2, 1), 0),
    0b011101010011: ("smmlar", INS_SMMLAR, (0, 4, 2, 1), 0),
    0b011101011101: ("smmls",  INS_SMMLS, (0, 4, 2, 1), 0),
    0b011101011111: ("smmlsr", INS_SMMLSR, (0, 4, 2, 1), 0),
    #note for next two must check that Ra = 1111 otherwise is smmla
    #hard coding values until find better solution
    #0b011101010001: ("smmul", (0,4,2), 0),
    #0b011101010011: ("smmulr", (0,4,2), 0),
}

def sh_lsl(num, shval, size=4, emu=None):
    return (num&e_bits.u_maxes[size]) << shval

def sh_lsr(num, shval, size=4, emu=None):
    return (num&e_bits.u_maxes[size]) >> shval

def sh_asr(num, shval, size=4, emu=None):
    return num >> shval

def sh_ror(num, shval, size=4, emu=None):
    return ((num >> shval) | (num << ((8*size)-shval))) & e_bits.u_maxes[size]

def sh_rrx(num, shval, size=4, emu=None):
    # shval should always be 0
    newC = num & 1

    if emu is not None:
        oldC = emu.getFlag(PSR_C_bit)
        if emu.getMeta('forrealz', False):
            emu.setFlag(PSR_C_bit, newC)
    else:
        # total hack!  should we just bomb here without an emu?
        oldC = 0

    half1 = (num&e_bits.u_maxes[size]) >> 1
    half2 = oldC<<(31)

    retval = (half1 | half2 | (oldC << (32-shval))) & e_bits.u_maxes[size]
    return retval

shifters = (
    sh_lsl,
    sh_lsr,
    sh_asr,
    sh_ror,
    sh_rrx,
)


####################################################################
# Mnemonic tables for opcode based mnemonic lookup

# Dataprocessing mnemonics
dp_mnem = (
    ("and", INS_AND),
    ("eor", INS_EOR),
    ("sub", INS_SUB),
    ("rsb", INS_RSB),
    ("add", INS_ADD),
    ("adc", INS_ADC),
    ("sbc", INS_SBC),
    ("rsc", INS_RSC),
    ("tst", INS_TST),
    ("teq", INS_TEQ),
    ("cmp", INS_CMP),
    ("cmn", INS_CMN),
    ("orr", INS_ORR),
    ("mov", INS_MOV),
    ("bic", INS_BIC),
    ("mvn", INS_MVN),
    ("adr", INS_ADR)  # added
)

dp_shift_mnem = (
    ("lsl", INS_LSL),
    ("lsr", INS_LSR),
    ("asr", INS_ASR),
    ("ror", INS_ROR),
    ("rrx", INS_RRX),
)

dp_noRn = (INS_MOV,INS_MVN)
dp_noRd = (INS_TST,INS_TEQ,INS_CMP,INS_CMN)
dp_silS = dp_noRd

# IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
DP_PSR_S = [IF_PSR_S for x in range(17)]
for x in dp_silS:
    DP_PSR_S[x] |= IF_PSR_S_SIL 

# somehow this list has vanished into the ether.  add seems like the right one here.
dp_ADR = (INS_SUB, INS_ADD,)


# FIXME: !!! Don't make SBZ and SBO's part of the list of opers !!!
#  first parm SBZ:   mov,mvn
#  second parm SBZ:  tst,teq,cmp,cmn,
def dpbase(opval):
    """
    Parse and return opcode,sflag,Rn,Rd for a standard
    dataprocessing instruction.
    """
    ocode = (opval >> 21) & 0xf
    sflag = (opval >> 20) & 0x1
    Rn = (opval >> 16) & 0xf
    Rd = (opval >> 12) & 0xf
    #print "DPBASE:",ocode,sflag,Rn,Rd
    return ocode,sflag,Rn,Rd

####################################################################
# Parser functions for each of the instruction encodings

def p_dp_imm_shift(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    Rm = opval & 0xf
    shtype = (opval >> 5) & 0x3
    shval = (opval >> 7) & 0x1f   # effectively, rot*2
    if (shtype==S_ROR) & (shval ==0): # is it an rrx?
        shtype = S_RRX
    mnem, opcode = dp_mnem[ocode]

    iflags = 0
    if ocode in dp_noRn:
        #is it a mov? Only if shval is a 0, type is lsl, and ocode = 13
        if  (ocode == INS_MOV) and ((shval != 0) or (shtype != S_LSL)):
            mnem, opcode = dp_shift_mnem[shtype]
            if shtype != S_RRX: #if not rrx
                if shtype in (S_ASR, S_LSR) and shval == 0:
                    shval = 32

                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegOper(Rm, va=va),
                    ArmImmOper(shval, va=va),
                )
            else:
                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegOper(Rm, va=va),
                )
        else:
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegShiftImmOper(Rm, shtype, shval, va),
            )
            # case: mov pc, lr
            if Rd == REG_PC:
                if Rm == REG_LR:
                    iflags |= envi.IF_RET | envi.IF_NOFALL

                else:
                    iflags |= envi.IF_BRANCH

    elif ocode in dp_noRd:
        olist = (
            ArmRegOper(Rn, va=va),
            ArmRegShiftImmOper(Rm, shtype, shval, va),
        )
    else:
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegShiftImmOper(Rm, shtype, shval, va),
        )

    if sflag > 0:
        iflags |= DP_PSR_S[ocode]

    return (opcode, mnem, olist, iflags, 0)

# specialized mnemonics for p_misc
qop_mnem = (('qadd', INS_QADD),('qsub', INS_QSUB),('qdadd', INS_QDADD),('qdsub', INS_QDSUB)) # used in misc1
smla_mnem = (('smlabb', INS_SMLABB),('smlatb', INS_SMLATB),('smlabt', INS_SMLATB),('smlatt', INS_SMLATB),)
smlal_mnem = (('smlalbb', INS_SMLALBB),('smlaltb', INS_SMLALTB),('smlalbt', INS_SMLALTB),('smlaltt', INS_SMLALTB),)
smul_mnem = (('smulbb', INS_SMULBB),('smultb', INS_SMULTB),('smulbt', INS_SMULTB),('smultt', INS_SMULTB),)
smlaw_mnem = (('smlawb', INS_SMLAWB),('smlawt', INS_SMLAWT),)
smulw_mnem = (('smulwb', INS_SMULWB),('smulwt', INS_SMULWT),)

def p_misc(opval, va):  
    # 0x0f900000 = 0x01000000 or 0x01000010 (misc and misc1 are both parsed at the same time.  see the footnote [2] on dp instructions in the Atmel AT91SAM7 docs

    #Including SBO and SBZ - rearranged for most exclusive to least
    #updated reference names to match v7 reference ie Rm Rn Rd Rs m n etc
    
    #if opval & 0x0ff000f0 == 0x01200020:
    if opval & 0x0FFFFFF0 == 0x012FFF20:  
        opcode = INS_BXJ
        mnem = 'bxj'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        
    #elif opval & 0x0fb002f0 == 0x01200000:
    elif opval & 0x0DB0F000 == 0x0120F000:
        opcode = INS_MSR
        mnem = 'msr'        # register.   immediate has it's own parser in the 001 section
        r = (opval>>22) & 1
        Rn = (opval) & 0xf
        mask = (opval>>16) & 0xf
        olist = (
            ArmPgmStatRegOper(r, mask),
            ArmRegOper(Rn, va=va),
        )

    #smla 
    #Mask and value are OK
    elif opval & 0x0FF00090 == 0x01000080:
        mn = (opval>>5)&3
        mnem, opcode = smla_mnem[mn]
        Rd = (opval>>16) & 0xf
        Ra = (opval>>12) & 0xf 
        Rm = (opval>>8) & 0xf
        Rn = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Ra, va=va),
        )
    #smlaw
    #mask and value are OK
    elif opval & 0x0ff000b0 == 0x01200080:
        m = (opval>>6)&1
        mnem, opcode = smlaw_mnem[m]
        Rd = (opval>>16) & 0xf
        Ra = (opval>>12) & 0xf 
        Rm = (opval>>8) & 0xf
        Rn = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Ra, va=va),
        )
    #smulw
    #mask and value are ok
    elif opval & 0x0ff000b0 == 0x012000a0:
        m = (opval>>6)&1
        mnem, opcode = smulw_mnem[m]
        Rd = (opval>>16) & 0xf
        Rm = (opval>>8) & 0xf
        Rn = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
        )
    #smlal
    #mask and value are ok
    elif opval & 0x0ff00090 == 0x01400080:
        mn = (opval>>5)&3
        mnem, opcode = smlal_mnem[mn]
        Rdhi = (opval>>16) & 0xf
        Rdlo = (opval>>12) & 0xf 
        Rm = (opval>>8) & 0xf
        Rn = opval & 0xf
        olist = (
            ArmRegOper(Rdlo, va=va),
            ArmRegOper(Rdhi, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
        )
    #smul
    #elif opval & 0x0ff00090 == 0x01600080:
    elif opval & 0x0ff0f090 == 0x01600080:
        mn = (opval>>5)&3
        mnem, opcode = smul_mnem[mn]
        Rd = (opval>>16) & 0xf
        Rm = (opval>>8) & 0xf
        Rn = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
        )
    #if opval & 0x0fc00000 == 0x01000000:
    elif opval & 0x0FB00C0F == 0x01000000:
        opcode = INS_MRS
        mnem = 'mrs'
        r = (opval>>22) & 1
        Rd = (opval>>12) & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmPgmStatRegOper(r),
        )
    else:
        raise envi.InvalidInstruction(
                mesg="p_misc: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction",
        olist = ()
        
    return (opcode, mnem, olist, 0, 0)


def p_misc1(opval, va): # 
    iflags = 0

    if opval & 0x0ff000f0 == 0x01200010:
        opcode = INS_BX
        mnem = 'bx'
        Rm = opval & 0xf
        cond = (opval >> 28) & 0xf

        olist = ( ArmRegOper(Rm, va=va), )

        if Rm == REG_LR:
            if cond < 0xe:
                iflags |= envi.IF_RET | envi.IF_COND
            else:
                iflags |= envi.IF_RET | envi.IF_NOFALL

        else:
            if cond < 0xe:
                iflags |= envi.IF_BRANCH | envi.IF_COND
            else:
                iflags |= envi.IF_BRANCH

    elif opval & 0x0ff000f0 == 0x01600010:
        opcode = INS_CLZ
        mnem = 'clz'
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )
    elif opval & 0x0ff000f0 == 0x01200030:
        # blx
        opcode = INS_BLX
        mnem = 'blx'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        iflags |= envi.IF_CALL
        
    elif opval & 0x0f9000f0 == 0x01000050:  #all qadd/qsub's
        qop = (opval>>21)&3
        mnem, opcode = qop_mnem[qop]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rn, va=va),
        )
        
    elif opval & 0x0ff000f0 == 0x01200070:
        opcode = INS_BKPT
        mnem = 'bkpt'
        immed = ((opval>>4)&0xfff0) + (opval&0xf)
        olist = ( ArmImmOper(immed), )
    elif opval & 0xfff00f0 == 0x32000f0:
        opcode = INS_DBG
        mnem = "dbg"
        immed = opval & 0xf
        olist = (ArmImmOper(immed),)
    else:
        raise envi.InvalidInstruction(
                mesg="p_misc1: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
        
    return (opcode, mnem, olist, iflags, 0)


'''
NOTES: For 'T' Variant (T = unpriveleged - must be accessible in user mode)
When P = 0 and W = 1 then add T to following
LDR (imm) & (reg)
LDRB (imm) & (reg)
LDRH (imm) & (lit) & (reg)
LDRSB (imm) & (reg)
LDRSH (imm) & (reg)
STR (imm) & (reg)
STRB (imm) & (reg)
STRH (imm) & (reg)

'''
swap_mnem = (("swp", INS_SWP, 4), ("swpb", INS_SWPB, 1),)
strex_mnem = (("strex", INS_STREX), ("ldrex", INS_LDREX))  # FIXME: full instruction then suffix
strex_flags = (0, IF_D, IF_B, IF_H)
strh_mnem = (("str",INS_STR, IF_H,2),("ldr",INS_LDR, IF_H,2),)          # IF_H
ldrs_mnem = (("ldr",IF_S|IF_B,1),("ldr",IF_S|IF_H,2),)      # IF_SH, IF_SB
ldrd_mnem = (("ldr",IF_D),("str",IF_D),)        # IF_D

def p_extra_load_store(opval, va, psize=4):
    pubwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    Rs = (opval>>8) & 0xf
    op1 = (opval>>5) & 0x3
    Rm = opval & 0xf
    iflags = 0
    tvariant = ((pubwl & 0x12)==2)
    if opval&0x0fb000f0==0x01000090:# swp/swpb
        idx = (pubwl>>2)&1
        opcode = INS_SWP
        mnem, opcode, tsize = swap_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmImmOffsetOper(Rn, 0, va, pubwl, psize=psize, tsize=tsize),
        )
    elif opval&0x0f800ff0==0x01800f90:# strex/ldrex
        idx = pubwl&1
        itype = (opval >> 21) & 3
        mnem, opcode = strex_mnem[idx]
        iflags |= strex_flags[itype]
        if (idx==0) & (itype != 1): #strex has 1 more entry than ldrex
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rm, va=va),
                ArmRegOper(Rn, va=va),
            )
        elif idx==0: #special case
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rm, va=va),
                ArmRegOper(Rm+1, va=va),
                ArmRegOper(Rn, va=va),
            )
        elif (idx==1) & (itype != 1):
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rn, va=va),
            )
        else: #special case
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rd+1, va=va),
                ArmRegOper(Rn, va=va),
            )

    elif opval&0x0e4000f0==0x000000b0:# strh/ldrh regoffset
        # 000pu0w0-Rn--Rt-SBZ-1011-Rm-  - STRH
        # 0000u110-Rn--Rt-imm41011imm4  - STRHT (v7+)
        idx = pubwl&1
        mnem, opcode, iflags, tsize = strh_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize, tsize=tsize),
        )
    elif opval&0x0e4000f0==0x004000b0:# strh/ldrh immoffset
        idx = pubwl&1
        mnem, opcode, iflags, tsize = strh_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn,(Rs<<4)+Rm, va, pubwl, psize=psize, tsize=tsize),
        )
    elif opval&0x0e5000d0==0x005000d0:# ldrsh/b immoffset
        idx = (opval>>5)&1
        opcode = INS_LDR
        mnem,iflags,tsize = ldrs_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl, psize=psize, tsize=tsize),
        )
    elif opval&0x0e5000d0==0x001000d0:# ldrsh/b regoffset
        idx = (opval>>5)&1
        opcode = INS_LDR
        mnem,iflags,tsize = ldrs_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize, tsize=tsize),
        )
    elif opval&0x0e5000d0==0x000000d0:# ldrd/strd regoffset
        # 000pu0w0-Rn--Rt-SBZ-1101-Rm-  ldrd regoffset
        # 0001u1001111-Rt-imm41101imm4  ldrd regoffset (literal, v7+)
        # Rt = Rd and must be even and not 14 per A8.8.72/A8.8.210
        # Rt2 = R(t+1)
        if (Rd == 14) or (Rd % 2 !=0):
            raise envi.InvalidInstruction(
                mesg="extra_load_store: invalid Rt argument",
                bytez=struct.pack("<I", opval), va=va)
        idx = (opval>>5)&1
        opcode = INS_LDR
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rd+1, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize, tsize=8),
        )
    elif opval&0x0e5000d0==0x004000d0:# ldrd/strd immoffset
        if (Rd == 14) or (Rd % 2 != 0):
            raise envi.InvalidInstruction(
                mesg="extra_load_store: invalid Rt argument",
                bytez=struct.pack("<I", opval), va=va)
        idx = (opval>>5)&1
        opcode = INS_LDR
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rd+1, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl, psize=psize, tsize=8),
        )
    else:
        raise envi.InvalidInstruction(
                mesg="extra_load_store: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
    return (opcode, mnem, olist, iflags, 0)


def p_load_store_word_ubyte(opval, va, psize=4):
    # p206
    #STR(register) pA8-672
    #STRT  A8-704
    #LDR(register) pA8-412
    #LDRT A8-464
    #STRB(imm) A8-678
    #STRBT A8-682
    #LDRB(reg) A8-420
    #LDRBT A8-422
    pubwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    Rm = opval & 0xf
    shval = (opval>>7) & 0x1f
    shtype = (opval>>5) & 3

    iflags = 0
    if pubwl & 4:   # B   
        iflags = IF_B

    if (pubwl & 0x12) == 2:
        iflags |= IF_T

    olist = (
        ArmRegOper(Rd, va=va),
        ArmScaledOffsetOper(Rn, Rm, shtype, shval, va, pubwl, psize=psize)    # u=-/+, b=word/byte
    )
    if Rd == REG_PC:
        iflags |= envi.IF_BRANCH
    
    mnem, opcode = ldr_mnem[pubwl&1]
    return (opcode, mnem, olist, iflags, 0)

def p_dp_reg_shift(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    Rm = opval & 0xf
    shtype = (opval >> 5) & 0x3
    Rs = (opval >> 8) & 0xf
    mnem, opcode = dp_mnem[ocode]
    if ocode in dp_noRn:
        #no register shift displayed with mov
        if  (ocode == 13):
            mnem, opcode = dp_shift_mnem[shtype]
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rm, va=va),
                ArmRegOper(Rs, va=va),
            )
        else:
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegShiftRegOper(Rm, shtype, Rs),
            )
    elif ocode in dp_noRd:
        olist = (
            ArmRegOper(Rn, va=va),
            ArmRegShiftRegOper(Rm, shtype, Rs),
        )
    else:
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegShiftRegOper(Rm, shtype, Rs),
        )

    if sflag > 0:
        # IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
        iflags = DP_PSR_S[ocode] 

    else:
        iflags = 0
    return (opcode, mnem, olist, iflags, 0)


multfail = (None, None, None, None)


iencmul_r15_codes = {
    # Basic multiplication opcodes
    0b011101010001: ("smmul",  INS_SMMUL,  (0,4,2), 0),
    0b011101010011: ("smmulr", INS_SMMULR, (0,4,2), 0),
    0b011100000001: ("smuad",  INS_SMUAD,  (0,4,2), 0),
    0b011100000011: ("smuadx", INS_SMUADX, (0,4,2), 0),
    0b011100000101: ("smusd",  INS_SMUSD,  (0,4,2), 0),
    0b011100000111: ("smusdx", INS_SMUSDX, (0,4,2), 0),
}


def chopmul(opcode):
    op1 = (opcode >> 20) & 0xff
    a = (opcode >> 16) & 0xf
    b = (opcode >> 12) & 0xf
    c = (opcode >> 8)  & 0xf
    d = (opcode >> 4)  & 0xf
    e = opcode & 0xf
    return (op1<<4)+d,(a,b,c,d,e)


def p_mult(opval, va):
    ocode, vals = chopmul(opval)
    mnem, opcode, opindexes, flags = iencmul_codes.get(ocode, multfail)

    #work around because masks match up - should be a cleaner way to do this?
    #if Ra = 15 then smmul
    if vals[1] == 15:
        newset = iencmul_r15_codes.get(ocode)
        if newset is not None:
            mnem, opcode, opindexes, flags = newset
    if mnem is None:
        raise envi.InvalidInstruction(
                mesg="p_mult: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
    olist = []
    for i in opindexes:
        olist.append(ArmRegOper(vals[i], va=va))
    return (opcode, mnem, olist, flags, 0)


def p_dp_imm(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    imm = opval & 0xff
    # ARMExpandImm_C():   Shift_C(unrotated_value, SRType_ROR, 2*UInt(imm12<11:8>), carry_in);
    rot = ((opval >> 7) & 0x1e)

    # hack to make add/sub against PC more readable (also legit for ADR instruction)
    if Rn == REG_PC and ocode in dp_ADR:    # we know PC
        if ocode == 2:  # and this is a subtraction
            ocode = 16
            olist = (
                ArmRegOper(Rd, va=va), 
                ArmPcOffsetOper( - shifters[S_ROR](imm, rot), va=va),
            )
        elif ocode == 4:    # this is addition
            ocode = 16
            olist = (
                ArmRegOper(Rd, va=va), 
                ArmPcOffsetOper( shifters[S_ROR](imm, rot), va=va),
            )

    # or just normal decode
    elif ocode in dp_noRn:
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOper(imm, rot, S_ROR),
        )
    elif ocode in dp_noRd:
        olist = (
            ArmRegOper(Rn, va=va),
            ArmImmOper(imm, rot, S_ROR),
        )
    else:
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmImmOper(imm, rot, S_ROR),
        )

    if sflag > 0:
        iflags = DP_PSR_S[ocode]
    else:
        iflags = 0

    mnem, opcode = dp_mnem[ocode]
    return (opcode, mnem, olist, iflags, 0)

def p_undef(opval, va):
    # FIXME: make this an actual opcode with the opval as an imm oper?
    raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
    opcode = IENC_UNDEF
    mnem = "undefined instruction"
    olist = (
        ArmImmOper(opval),
    )
        
    return (opcode, mnem, olist, 0, 0)

def p_dp_movw(opval, va):
    iflags = 0
    imm =  ((opval >>4) &0xf000) + (opval & 0xfff)
    Rd = (opval >> 12) & 0xf
    opcode = INS_MOV
    olist = (
        ArmRegOper(Rd, va=va),
        ArmImmOper(imm),
    )
    return(opcode, "movw", olist, iflags, 0)

def p_dp_movt(opval, va):
    iflags = 0
    imm =  ((opval >>4) &0xf000) + (opval & 0xfff)
    Rd = (opval >> 12) & 0xf
    opcode = INS_MOV
    olist = (
        ArmRegOper(Rd, va=va),
        ArmImmOper(imm),
    )
    return(opcode, "movt", olist, iflags, 0)

hint_mnem = {
            0: ('nop',INS_NOP),
            1: ('yield',INS_YIELD),
            2: ('wfe',INS_WFE),
            3: ('wfi',INS_WFI),
            4: ('sev',INS_SEV),
            }

def p_mov_imm_stat(opval, va):      # only one instruction: "msr"
    iflags = 0
    imm = opval & 0xff
    rot = (opval>>8) & 0xf
    r = (opval>>22) & 1
    mask = (opval>>16) & 0xf

    if mask == 0:
        # it's a NOP or some hint instruction
        if imm>>16:
            mnem = 'dbg'
            opcode = INS_DBG
            option = opval & 0xf
            olist = ( ArmDbgHintOption(option), )

        else:
            hint = hint_mnem.get(imm)
            if hint is None:
                raise envi.InvalidInstruction(
                        mesg="MSR/Hint illegal encoding",
                        bytez=struct.pack("<I", opval), va=va)
            mnem, opcode = hint
            olist = tuple()

    else:
        # it's an MSR <immediate>
        mnem = 'msr'
        opcode = INS_MSR
        immed = ((imm>>rot) + (imm<<(32-rot))) & 0xffffffff

        if mask & 3:    # USER mode these will be 0
            iflags |= IF_SYS_MODE
        
        olist = (
            ArmPgmStatRegOper(r, mask),
            ArmImmOper(immed),
        )
    
    return (opcode, mnem, olist, iflags, 0)
    
def p_mcr(opval, va):
    op = (opval>>20) & 1
    opcode, mnem = ((INS_MCR, 'mcr'), (INS_MRC, 'mrc'))[op]
    opc1 = (opval>>21) & 7
    opc2 = (opval>>5) & 7
    coproc = (opval>>8) & 0xf
    crn = (opval>>16) & 0xf
    rt = (opval>>12) & 0xf
    crm = (opval & 0xf)

    if opc2:
        opers = (
            ArmCoprocOper(coproc),
            ArmCoprocOpcodeOper(opc1),
            ArmRegOper(rt, va=va),
            ArmCoprocRegOper(crn),
            ArmCoprocRegOper(crm),
            ArmCoprocOpcodeOper(opc2),
        )
    else:
        opers = (
            ArmCoprocOper(coproc),
            ArmCoprocOpcodeOper(opc1),
            ArmRegOper(rt, va=va),
            ArmCoprocRegOper(crn),
            ArmCoprocRegOper(crm),
        )
    return (opcode, mnem, opers, 0, 0)

ldr_mnem = (("str", INS_STR), ("ldr", INS_LDR))
tsizes = (4, 1,)
def p_load_imm_off(opval, va, psize=4):
    # * STR(imm) A8-672
    # * STRT A8-704
    # * LDR(imm) A8-406
    # * LDRT A8-464
    # * STRB(imm) A8-678
    # * STRBT A8-672
    # * LDRB(imm/literal) A8-416-418
    # * LDRBT A8-422
    pubwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    imm = opval & 0xfff
    mnem, opcode = ldr_mnem[pubwl&1]
    iflags = 0

    tsize = 4
    if pubwl & 4:   # B   
        iflags = IF_B
        tsize = 1

    if (pubwl & 0x12) == 2:
        iflags |= IF_T

    if Rd == REG_PC:
        iflags |= envi.IF_BRANCH

    if (opval & 0xfff0fff) == 0x52D0004:
        mnem = "push"
        olist = (
            ArmRegOper(Rd, va=va),
        )
    elif (opval & 0xfff0fff) == 0x49d0004:
        mnem = "pop"
        olist = (
            ArmRegOper(Rd, va=va),
        )
    else: 
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn, imm, va, pubwl=pubwl, psize=psize, tsize=tsize)    # u=-/+, b=word/byte
        )
    return (opcode, mnem, olist, iflags, 0)

def p_load_reg_off(opval, va, psize=4):
    pubwl = (opval>>20) & 0x1f
    Rd = (opval>>12) & 0xf
    Rn = (opval>>16) & 0xf
    Rm = opval & 0xf
    shtype = (opval>>5) & 0x3
    shval = (opval>>7) & 0x1f

    if pubwl & 4:   # B   
        iflags = IF_B
        if (pubwl & 0x12) == 2:
            iflags |= IF_T
    else:
        iflags = 0

    olist = (
        ArmRegOper(Rd, va=va),
        ArmScaledOffsetOper(Rn, Rm, shtype, shval, va, pubwl, psize=psize),  # u=-/+, b=word/byte
    )
    
    mnem, opcode = ldr_mnem[pubwl&1]
    return (opcode, mnem, olist, iflags, 0)

def p_media(opval, va):
    """
    27:20, 7:4
    """
    # media is a parent for the following:
    #  parallel add/sub                         01100000    0x60
    #  pkh, ssat, ssat16, usat, usat16, sel     01101000    0x68
    #  rev, rev16, rbit, revsh                  01101000    0x68
    #  smlad, smlsd, smlald, smusd              01110000    0x70
    #  sdiv                                     01110001    0x71
    #  usad8, usada8                            01111000    0x78
    #  sbfx                                     01111010    0x7a
    #  had to add additional bits to fields to properly decode new commands.
    #  note added masks to reflect this.

    #Prototype for new structure. Left working structure in place but commented out until receive comments.
    MEDIA_MAX = 10
    media_parsers_tmp = [None for x in range(MEDIA_MAX)]

    media_parsers_tmp[0] = p_media_parallel
    media_parsers_tmp[1] = p_media_pack_sat_rev_extend
    media_parsers_tmp[2] = p_div
    media_parsers_tmp[3] = p_mult
    media_parsers_tmp[4] = p_media_usada
    media_parsers_tmp[5] = p_media_sbfx
    media_parsers_tmp[6] = p_media_bf
    #media_parsers_tmp[7] = p_media_smul
    media_parsers = tuple(media_parsers_tmp)

    media_codes = (
        (0b11111000, 0b01100000, 0),
        (0b11111000, 0b01101000, 1),
        (0b01111111, 0b01110001, 2),
        (0b01111111, 0b01110011, 2),
        (0b11111010, 0b01110000, 3),
        (0b11111110, 0b01111000, 4),
        (0b11111110, 0b01111010, 5),
        (0b11111100, 0b01111100, 6),
    )
    p_routine = None
    definer = (opval>>20) & 0xff
    for mask,val,idx in media_codes:
        if (definer & mask) == val:
            p_routine = idx
            break
    if p_routine is None:
        raise envi.InvalidInstruction(
        mesg="p_media: can not find command! Definer = "+str(definer)+ " op = " +str(opval),
        bytez=struct.pack("<I", opval), va=va)
    return media_parsers[p_routine](opval, va)

#generate mnemonics for parallel instructions (could do manually like last time...)
parallel_mnem = []
par_suffixes = ("add16", "asx", "sax", "sub16", "add8", "", "", "sub8")
par_prefixes = ("","s","q","sh","","u","uq","uh")
for pre in par_prefixes:
    for suf in par_suffixes:
        if not (len(pre) and len(suf)):
            parallel_mnem.append((None, None))
        else:
            mnem = pre + suf
            opname = "INS_" + mnem.upper()
            opcode = globals()[opname]
            parallel_mnem.append((mnem, opcode))

parallel_mnem = tuple(parallel_mnem)

def p_media_parallel(opval, va):
    
    opc1 = (opval>>17) & 0x38
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    opc1 += (opval>>5) & 7
    Rm = opval & 0xf
    mnem, opcode = parallel_mnem[opc1]
    olist = (
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmRegOper(Rm, va=va),
    )
    return (opcode, mnem, olist, 0, 0)


xtnd_mnem = []
xtnd_suffixes = ("xtab16", None,"xtab", "xtah","xtb16", None, "xtb","xth",)
xtnd_prefixes = ("s","u")
for pre in xtnd_prefixes:
    for suf in xtnd_suffixes:
        if suf is None:
            xtnd_mnem.append((None, None))
        else:
            mnem = pre+suf
            opname = 'INS_' + mnem.upper()
            opcode = globals()[opname]
            xtnd_mnem.append((mnem, opcode))
        
xtnd_mnem = tuple(xtnd_mnem)

pkh_mnem = (('pkhbt', INS_PKHBT), ('pkhtb', INS_PKHTB),)
sat_mnem = (('ssat', INS_SSAT), ('usat', INS_USAT))
sat16_mnem = (('ssat16', INS_SSAT16),('usat16', INS_USAT16))
rev_mnem = (('rev', INS_REV),('rev16', INS_REV16),('rbit', INS_RBIT),('revsh', INS_REVSH),)

#FIXME: too complicated, can be reduced?
def p_media_pack_sat_rev_extend(opval, va):
    ## part of p_media
    # assume bit 23 == 1
    opc1 = (opval>>20) & 7
    opc2 = (opval>>4) & 0xf
    opc25 = opc2 & 3
    opcode = 0
    if opc1 == 0 and opc25 == 1:   #pkh
        #pkhtb = asr, pkhbt = lsl
        shifter = (S_LSL, S_ASR)
        idx = (opval>>6)&1
        mnem, opcode = pkh_mnem[idx]
        shift_type = shifter[idx]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        shift_imm = (opval>>7) & 0x1f
        Rm = opval & 0xf
        #don't have to have a shift
        if shift_imm > 0:
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rn, va=va),
                ArmRegShiftImmOper(Rm, shift_type, shift_imm, va),
            )
        else:
            olist = (
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rn, va=va),
                ArmRegOper(Rm, va=va),
            )
            
    elif (opc1 & 2) and opc25 == 1: #word sat
        opidx = (opval>>22)&1
        sat_imm = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        if opc1 & 0x10: # ?sat16
            mnem, opcode = sat16_mnem[opidx]
            olist = (
                ArmRegOper(Rd, va=va),
                ArmImmOper(sat_imm),
                ArmRegOper(Rm, va=va),
            )
        else:
            mnem, opcode = sat_mnem[opidx]
            #Only add 1 for SSAT
            if opidx == 0:
                sat_imm += 1
            shift_imm = (opval>>7) & 0x1f
            sh = (opval>>5) & 2
            olist = (
                ArmRegOper(Rd, va=va),
                ArmImmOper(sat_imm),
                ArmRegShiftImmOper(Rm, sh, shift_imm, va),
            )
            
    elif (opc1 & 3) == 2 and opc2 == 3:     #ssat16
        opidx = (opval>>22)&1
        sat_imm = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        mnem, opcode = sat16_mnem[opidx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOper(sat_imm),
            ArmRegOper(Rm, va=va),
        )
        
    
    elif (opc1 > 0) and (opc2 & 7) == 3:           # byte rev word
        opidx = ((opval>>21) & 2) + ((opval>>7) & 1)
        mnem, opcode = rev_mnem[opidx]
        if mnem is None:
            raise envi.InvalidInstruction(
                    mesg="p_media_pack_sat_rev_extend: invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
 
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )

    elif opc1 == 3 and opc2 == 0xb:         # byte rev pkt halfword
        mnem = 'rev16'
        opcode = INS_REV16

        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )

    elif opc1 == 7 and opc2 == 0xb:         # byte rev signed halfword
        mnem = 'revsh'
        opcode = INS_REVSH

        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )

    elif opc1 == 0 and opc2 == 0xb:         # select bytes
        mnem = "sel"
        opcode = INS_SEL
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
        )

    elif opc2 == 7:                         # sign extend
        idx = (opc1&3) + 8 * ((opval>>22) &1)
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        shift_imm = (opval>>7) & 0x1f
        Rm = opval & 0xf
        if Rn == 0xf:
            idx +=4
            if (shift_imm != 0): # Needed or will show rrx when shift_imm == 0 which is wrong
                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegShiftImmOper(Rm, S_ROR, shift_imm, va), ###
                )
            else:
                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegOper(Rm, va=va),
                )
        else:
            if (shift_imm != 0): # Needed or will show rrx when shift_imm == 0 which is wrong 
                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegOper(Rn, va=va),
                    ArmRegShiftImmOper(Rm, S_ROR, shift_imm, va), ###
                )
            else:
                olist = (
                    ArmRegOper(Rd, va=va),
                    ArmRegOper(Rn, va=va),
                    ArmRegOper(Rm, va=va),
                )
        mnem, opcode = xtnd_mnem[idx]

    else:
        raise envi.InvalidInstruction(
                mesg="p_media_extend: invalid instruction %r.%r" % (opc1, opc2),
                bytez=struct.pack("<I", opval), va=va)

    return (opcode, mnem, olist, 0, 0)

bf_mnem = (("bfi", INS_BFI), ("ubfx", INS_UBFX), ("bfc", INS_BFC))
def p_media_bf(opval, va):
    idx = (opval>>21) & 1
    width = (opval>>16) & 0x1f
    Rd = (opval>>12) & 0xf
    lsb = (opval>>7) & 0x1f
    Rn = opval &0xf
    if Rn == 0xf:
        idx += 2
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOper(lsb),
            ArmImmOper(width)
        )
    else:
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmImmOper(lsb),
            ArmImmOper(width)
        )
    mnem, opcode = bf_mnem[idx]
    return (opcode, mnem, olist, 0, 0)

def p_media_usada(opval, va):
    Rd = (opval>>16) & 0xf
    Rn = (opval>>12) & 0xf
    Rs = (opval>>8) & 0xf
    Rm = opval & 0xf
    if Rn == 0xf:
        mnem = "usad8"
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
        )
        opcode = INS_USAD8
    else:
        mnem = "usada8"
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
            ArmRegOper(Rn, va=va),
        )
        opcode = INS_USADA8

    return (opcode, mnem, olist, 0, 0)

def p_media_sbfx(opval, va):
    Rd = (opval>>12) & 0xf
    Rn = opval & 0xf
    width = (opval>>16) & 0x1f
    lsb= (opval>>7) & 0x1f
    mnem = "sbfx"
    olist = (
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmImmOper(lsb, 0, va=va),
        ArmImmOper(width, 0, va=va),
    )
    opcode = INS_SBFX
    return (opcode, mnem, olist, 0, 0)

div_mnem= (("sdiv", INS_SDIV),("udiv", INS_UDIV))
def p_div(opval, va):
    Rd = (opval>>16) & 0xf
    Rm = (opval>>8) & 0xf
    Rn = opval & 0xf
    mnem, opcode = div_mnem[(opval>>21) & 1]
    olist = (
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmRegOper(Rm, va=va),
    )
    return (opcode, mnem, olist, 0, 0)

def p_arch_undef(opval, va):
    raise envi.InvalidInstruction(mesg="p_arch_undef: invalid instruction (by definition in ARM spec)",
                                  bytez=struct.pack("<I", opval), va=va)

ldm_mnem = (("stm", INS_STM), ("ldm", INS_LDM))

def p_load_mult(opval, va):
    puswl = (opval>>20) & 0x1f
    mnem_idx = puswl & 1
    mnem, opcode = ldm_mnem[(mnem_idx)]

    # store bits for decoding whether to dec/inc before/after between ldr/str.  
    # IF_DA tells the repr to print the the DAIB extension after the conditional.  
    # right shift necessary to clear lower three bits, and align us with IF_DAIB_SHFT
    flags = ((puswl>>3)<<(IF_DAIB_SHFT)) | IF_DA     
    Rn = (opval>>16) & 0xf
    reg_list = opval & 0xffff
    if (opval&0x0fff0000) == 0x8bd0000:
        mnem = "pop"
        opcode = INS_POP
        olist = (
            ArmRegListOper(reg_list, puswl),
        )
    elif (opval&0x0fff0000) == 0x92d0000:
        mnem = "push"
        opcode = INS_PUSH
        olist = (
            ArmRegListOper(reg_list, puswl),
        )
    else:     
        olist = (
            ArmRegOper(Rn, va=va),
            ArmRegListOper(reg_list, puswl),
        )

    # If we are a load multi (ldm), and we load PC, we are NOFALL
    # unless we are conditional... 
    cond = opval>>28
    if mnem_idx == 1 and reg_list & (1 << REG_PC) and cond >= 0xe:
        flags |= envi.IF_NOFALL
        # If the load is from the stack, call it a "return"
        if Rn == REG_SP:
            flags |= envi.IF_RET | envi.IF_NOFALL
        else:
            flags |= envi.IF_BRANCH

    if puswl & 2:       # W (mnemonic: "!")
        flags |= IF_W
        olist[0].oflags |= OF_W

    if puswl & 4:       # UM - usermode, or mov current SPSR -> CPSR if r15 included
        flags |= IF_UM
        olist[1].oflags |= OF_UM
    return (opcode, mnem, olist, flags, 0)

b_mnem = (("b", INS_B), ("bl", INS_BL))
def p_branch(opval, va):        # primary branch encoding.  others were added later in the media section
    # A1 encoding.
    
    off = e_bits.signed(opval, 3)
    off <<= 2
    link = (opval>>24) & 1

    olist = ( ArmPcOffsetOper(off, va),)
    if link:
        flags = envi.IF_CALL
    else:
        flags = envi.IF_BRANCH
    
    mnem, opcode = b_mnem[link]
    return (opcode, mnem, olist, flags, 0)

ldc_mnem = (("stc", INS_STC), ("ldc", INS_LDC))
def p_coproc_load(opval, va):
    punwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    CRd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    offset = opval & 0xff

    if punwl & 4:   # L
        iflags = IF_L
    else:
        iflags = 0
    #check for index. Non-index is option
    #print "punwl: 0x%x" % punwl
    if (punwl & 0x1a) != 8:
        olist = (
            ArmCoprocOper(cp_num),
            ArmCoprocRegOper(CRd),
            ArmImmOffsetOper(Rn, offset*4, va, pubwl=punwl),
        )
    else:
        #Non indexed
        olist = (
            ArmCoprocOper(cp_num),
            ArmCoprocRegOper(CRd),
            ArmCoprocOption(Rn, offset, va, pubwl=punwl),
        )
    mnem, opcode = ldc_mnem[punwl&1]
    return (opcode, mnem, olist, iflags, 0)

mcrr_mnem = (("mcrr", INS_MCRR), ("mrrc", INS_MRRC))
def p_coproc_dbl_reg_xfer(opval, va):
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    copcode = (opval>>4) & 0xf
    CRm = opval & 0xf
    
    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(copcode),
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmCoprocRegOper(CRm),
    )
    mnem, opcode = mcrr_mnem[(opval>>20) & 1]
    return (opcode, mnem, olist, 0, 0)
    
cdp_mnem = (("cdp", INS_CDP), ("cdp2", INS_CDP2))

def p_coproc_dp(opval, va):
    opcode1 = (opval>>20) & 0xf
    CRn = (opval>>16) & 0xf
    CRd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    opcode2 = (opval>>5) & 0x7
    CRm = opval & 0xf

    cdp2bit = (opval>>28)&1
    mnem, opcode = cdp_mnem[cdp2bit]

    if cdp2bit == 0 and (cp_num & 0b1110) == 0b1010:
        return p_fp_dp(opval, va)

    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(opcode1),
        ArmCoprocRegOper(CRd),
        ArmCoprocRegOper(CRn),
        ArmCoprocRegOper(CRm),
        ArmCoprocOpcodeOper(opcode2),
    )
    
    return (opcode, mnem, olist, 0, 0)

mcr_mnem = (("mcr", INS_MCR), ("mrc", INS_MRC))
def p_coproc_reg_xfer(opval, va):
    opcode1 = (opval>>21) & 0x7
    load = (opval>>20) & 1
    CRn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    opcode2 = (opval>>5) & 0x7
    CRm = opval & 0xf

    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(opcode1),
        ArmRegOper(Rd, va=va),
        ArmCoprocRegOper(CRn),
        ArmCoprocRegOper(CRm),
        ArmCoprocOpcodeOper(opcode2),
    )
    
    mnem, opcode = mcr_mnem[load]
    return (opcode, mnem, olist, 0, 0)

#swi has been changed to svc in latest ref
def p_swint(opval, va):
    swint = opval & 0xffffff
    
    olist = ( ArmImmOper(swint), )
    opcode = INS_SVC
    return (opcode, "svc", olist, 0, 0)

def p_vmov_single(opval, va):   # p944
    op = (val >> 20) & 1

    n = (opval >> 7) & 1
    vn = (opval >> 15) & 0x1e | n
    
    rt = (opval >> 12) & 0xf

    if op:
        opers = (
            ArmRegOper(rt, va),
            ArmRegOper(rctx.getRegisterIndex('s%d' % vn)),
                )
    else:
        opers = (
            ArmRegOper(rctx.getRegisterIndex('s%d' % vn)),
            ArmRegOper(rt, va),
                )
    return opcode, mnem, opers, 0, 0

def p_vmov_2single(opval, va):  # p944 (946?)
    op = (val >> 20) & 1

    rt2 = (opval >> 16) & 0xf
    rt = (opval >> 12) & 0xf

    m = (opval >> 5) & 1
    vm = ((opval << 1) & 0x1e) | m

    if op:
        opers = (
            ArmRegOper(rt, va),
            ArmRegOper(rt2, va),
            ArmRegOper(rctx.getRegisterIndex('s%d' % vm)),
            ArmRegOper(rctx.getRegisterIndex('s%d' % (vm+1))),
                )
    else:
        opers = (
            ArmRegOper(rctx.getRegisterIndex('s%d' % vm)),
            ArmRegOper(rctx.getRegisterIndex('s%d' % (vm+1))),
            ArmRegOper(rt, va),
            ArmRegOper(rt2, va),
                )
    return opcode, mnem, opers, 0, 0

def p_vmov_double(opval, va):
    opcode = INS_VMOV
    mnem = 'vmov'

    op = (opval >> 20) & 1

    rt2 = (opval >> 16) & 0xf
    rt = (opval >> 12) & 0xf

    m = (opval >> 5) & 1
    vm = ((opval << 1) & 0x1e) | m

    if op:
        opers = (
            ArmRegOper(rt, va),
            ArmRegOper(rt2, va),
            ArmRegOper(rctx.getRegisterIndex('d%d' % vm)),
                )
    else:
        opers = (
            ArmRegOper(rctx.getRegisterIndex('d%d' % vm)),
            ArmRegOper(rt, va),
            ArmRegOper(rt2, va),
                )

    return opcode, mnem, opers, 0, 0

def p_vmov_scalar(opval, va):
    op = (val >> 20) & 1

    opc1 = (opval >> 21) & 7
    opc2 = (opval >> 5) & 3

    rt = (opval >> 12) & 0xf

    d = (opval >> 3) & 0x10
    vd = ((opval >> 16) & 0xf) | d
    u = (opval >> 23) & 1

    if (opc1 & 2):  # 1xxx
        index = ((opc1 & 1) << 2) | opc2
        simdflags = (IFS_S8, IFS_U8)[u]

    elif (opc2 & 1):# 0xx1
        index = ((opc1 & 1) << 1) | (opc2 >> 1)
        simdflags = (IFS_S16, IFS_U16)[u]

    else:           # 0xx0
        index = (opc1 & 1) << 1
        simdflags = IFS_32

    if op:
        opers = (
            ArmRegOper(rt, va),
            ArmRegScalarOper(rctx.getRegisterIndex('d%d' % vd), index),
            )
    else:
        opers = (
            ArmRegScalarOper(rctx.getRegisterIndex('d%d' % vd), index),
            ArmRegOper(rt, va),
            )

    return INS_VMOV, 'vmov', opers, 0, simdflags

def p_vstm(opval, va):      #p1078
    pudwl = (opval >> 20) & 0x1f
    rn = (opval >> 16) & 0xf
    vd = (opval >> 12) & 0xf
    imm8 = (opval & 0xff)

    flags = (0, IF_IA, IF_DB, 0)[pudwl>>3]

    if pudwl & 2:   # W==1
        oflags = OF_W
    else:
        oflags = 0

    op = (opval>>8) & 1
    regsize = imm8 >> op
    simdflags = (IFS_32, IFS_64)[op]

    opers = (
            ArmRegOper(rn, va, oflags=oflags),
            ArmExtRegListOper(vd, regsize, op),
            )

    return opcode, mnem, opers, flags, simdflags

def p_vstr(opval, va):
    pudwl = (opval >> 20) & 0x8
    rn = (opval >> 16) & 0xf
    vd = (opval >> 12) & 0xf
    imm = (opval & 0xff) << 2

    sz = (opval>>8) & 1
    simdflags = (IFS_32, IFS_64)[sz]

    rbase = ("s%d","d%d")[sz]
    tsize = 4 + (4*sz)
    opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase % vd)),
            ArmImmOffsetOper(rn, imm, va, pubwl=pudwl, tsize=tsize)
            )

    return INS_VSTR, 'vstr', opers, 0, 0


def p_vpush(opval, va):
    pudwl = (opval >> 20) & 0x1f
    vd = (opval >> 12) & 0xf
    imm8 = (opval & 0xff)

    op = (opval>>8) & 1
    regsize = imm8 >> op
    simdflags = (IFS_32, IFS_64)[op]

    opers = (
            ArmExtRegListOper(vd, regsize, op),
            )

    return INS_VPUSH, 'vpush', opers, 0, simdflags

def p_vldm(opval, va):      #p920
    pudwl = (opval >> 20) & 0x1f
    rn = (opval >> 16) & 0xf
    vd = (opval >> 12) & 0xf
    imm8 = (opval & 0xff)

    flags = (0, IF_IA, IF_DB, 0)[pudwl>>3]

    if pudwl & 2:   # W==1
        oflags = OF_W
    else:
        oflags = 0

    op = (opval>>8) & 1
    regsize = imm8 >> op
    simdflags = (IFS_32, IFS_64)[op]

    opers = (
            ArmRegOper(rn, oflags=oflags),
            ArmExtRegListOper(vd, regsize, op),
            )

    return INS_VLDM, 'vldm', opers, flags, simdflags

def p_vldr(opval, va):
    pudwl = (opval >> 20) & 0x8
    rn = (opval >> 16) & 0xf
    vd = (opval >> 12) & 0xf
    imm = (opval & 0xff) << 2

    sz = (opval>>8) & 1
    simdflags = (IFS_32, IFS_64)[sz]

    rbase = ("s%d","d%d")[sz]
    tsize = 4 + (4*sz)
    opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase % vd)),
            ArmImmOffsetOper(rn, imm, va, pubwl=pudwl, tsize=tsize)
            )

    return INS_VLDR, 'vldr', opers, 0, simdflags

def p_vpop(opval, va):
    pudwl = (opval >> 20) & 0x1f
    vd = (opval >> 12) & 0xf
    imm8 = (opval & 0xff)

    op = (opval>>8) & 1
    regsize = imm8 >> op
    simdflags = (IFS_32, IFS_64)[op]

    opers = (
            ArmExtRegListOper(vn, regsize, op),
            )

    return INS_VPUSH, 'vpush', opers, 0, simdflags

def p_vdup(opval, va):
    q = (opva >> 21) & 1
    b = (opva >> 22) & 1
    d = ((opva >> 3) & 0x10)
    vd = (opva >> 16) & 0xf | d
    rt = (opva >> 12) & 0xf
    e = (opva >> 5) & 1


    # q# regs are two d# regs
    d >>= q
    rbase = ("s%d","d%d")[q]

    opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase % vd)),
            ArmRegOper(rt, va=va),
            )

    be = (b<<1) | e
    simdflags = (IFS_32, IFS_16, IFS_8, None)[be]

    return INS_VDUP, 'vdup', opers, 0, simdflags

def p_vmsr(opval, va):
    # vmsr/vmrs
    l = (opval >> 20) & 1
    rt = (opval >> 12) & 0xf
    opcode, mnem = ((INS_VMSR, 'vmsr'), (INS_VMRS, 'vmrs'))[l]

    opers = (
            ArmRegOper(rt, va=va),
            )

    return opcode, mnem, opers, 0, 0


mcrr2_mnem = (("mcrr2", INS_MCRR2), ("mrrc2", INS_MRRC2))
ldc2_mnem = (("stc2", INS_STC2), ("ldc2", INS_LDC2))
mcr2_mnem = (("mcr2", INS_MCR2), ("mrc2", INS_MRC2))
pld_mnem =  (("pldw", INS_PLDW), ("pld", INS_PLD))
pl_opcode = (INS_PLI, INS_PLD)
def p_uncond(opval, va, psize = 4):
    if opval & 0x0f000000 == 0x0f000000:
        opcode = INS_UNDEF
        immval = opval & 0x00ffffff
        return (opcode, 'undefined', (ArmImmOper(immval),), 0, 0)

    optop = ( opval >> 26 ) & 0x3
    if optop == 0:
        if opval & 0xfff10020 == 0xf1000000:
            #cps
            iflags = 0
            mnem = 'cps'
            opcode = INS_CPS

            imod = (opval>>18)&3
            mmod = (opval>>17)&1
            aif = (opval>>6)&7
            mode = opval&0x1f

            if imod & 2:
                olist = [
                    ArmCPSFlagsOper(aif)    # if mode is set...
                ]

                # interrupt enable/disable (imod & 1 == Disable)
                iflags |= (IF_IE, IF_ID,)[imod&1]

            else:
                olist = []

            if mmod:
                olist.append(ArmImmOper(mode))
            
            return (opcode, mnem, olist, iflags, 0)
        elif (opval & 0xffff00f0) == 0xf1010000:
            #setend
            e = (opval>>9) & 1
            mnem = "setend"
            olist = ( ArmEndianOper(e), )
            opcode = INS_SETEND
            return (opcode, mnem, olist, 0, 0)

        elif (opval & 0xfe000000 == 0xf2000000):
            # handing off to adv_simd_32
            return adv_simd_32(opval, va)
            
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=0): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    elif optop == 1:
        if (opval & 0xfc30f000) == 0xf410f000: #pld/pldw/pli
            pl = (opval>>24)&1
            R = (opval>>22)&1 # For w. Is pldw if R is 1
            U = (opval>>23) & 1
            Rn = (opval>>16) & 0xf
            I = (opval>>25) & 1

            if pl==0:
                mnem = "pli"
                opcode = pl_opcode[pl]
            else:
                mnem, opcode = pld_mnem[R]

            if not I:
                immoffset = opval & 0xfff
                olist = (ArmImmOffsetOper(Rn, immoffset, va, (U<<3) | 0x10, psize=psize),)
            else:
                Rm = opval & 0xf
                shtype = (opval>>5) & 3
                shval = (opval>>7) & 0x1f
                olist = (ArmScaledOffsetOper(Rn, Rm, shtype, shval, va, (U<<3) | 0x10, psize=psize), )
            return (opcode, mnem, olist, 0, 0)

        elif (opval & 0xff000f0) == 0x5700010:
            #clrex
            mnem = "clrex"
            olist =()
            opcode = INS_CLREX
            return (opcode, mnem, olist, 0, 0)
        elif (opval & 0xff000e0) == 0x5700040:
            #dmb/dsb
            option = opval & 0xf
            if (opval & 0x10 )== 0x10:
                mnem = 'dmb'
                opcode = INS_DMB
            else:
                mnem = 'dsb'
                opcode = INS_DSB
            olist = (ArmBarrierOption(option),)
            return (opcode, mnem, olist, 0, 0)
        elif (opval & 0xff000f0) == 0x5700060:
            #isb
            option = opval & 0xf
            mnem = 'isb'
            olist = (ArmBarrierOption(option),)
            opcode = INS_ISB
            return (opcode, mnem, olist, 0, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=1): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    elif optop == 2:
        if (opval & 0xfe5f0f00) == 0xf84d0500:
            #save return state (basically, store LR and SPSR to the stack that R13 points to)
            pu_w_ = (opval>>20) & 0x1f
            mnem = "srs"
            flags = ((pu_w_>>3)<<(IF_DAIB_SHFT)) | IF_DA
            mode = opval & 0x1f
            #reg_list = ( 1<<14 | 1<<SPSR )
            if pu_w_ & 2:    # base_reg update
                flags |= IF_W
           
            # base_reg = R13
            # reg_list = R14 and SPSR
            olist = (
                #ArmRegListOper(reg_list, pu_w_),
                ArmModeOper(mode, (pu_w_>>1)&1),
            )
            opcode = INS_SRS
            return (opcode, mnem, olist, flags, 0)
        #elif (opval & 0xfe500f00) == 0xf8100a00:       # this is too restrictive, although does weed out oddballs.  what does "Should Be Zero" really *want* to mean?
        elif (opval & 0xfe500000) == 0xf8100000:
            #rfe
            pu = (opval>>23) & 3
            mnem = "rfe"
            flags = (pu<<(IF_DAIB_SHFT)) | IF_DA
            Rn = (opval>>16) & 0xf
            
            olist = (
                ArmRegOper(Rn, va=va),
            )
            opcode = INS_RFE
            return (opcode, mnem, olist, flags, 0)

        elif (opval & 0xfe000000) == 0xfa000000:
            #blx
            opcode = INS_BLX
            mnem = "blx"
            h = (opval>>23) & 2
            imm_offset = (e_bits.signed(opval, 3) << 2) | h | 1 #this encoding forces THUMB
            
            olist = (
                ArmPcOffsetOper(imm_offset, va),
            )
            
            return (opcode, mnem, olist, envi.IF_CALL, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=2): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    else:
        if (opval & 0xffe00000) == 0xfc400000:
            #MRCC2/MRRC2
            Rn = (opval>>16) & 0xf
            Rd = (opval>>12) & 0xf
            cp_num = (opval>>8) & 0xf
            opcode = (opval>>4) & 0xf
            CRm = opval & 0xf
                
            olist = (
                ArmCoprocOper(cp_num),
                ArmCoprocOpcodeOper(opcode),
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rn, va=va),
                ArmCoprocRegOper(CRm),
            )
            mnem, opcode = mcrr2_mnem[(opval>>20) & 1]
            return (opcode, mnem, olist, 0, 0)
            
        elif (opval & 0xfe000000) == 0xfc000000:
            #stc2/ldc2
            punwl = (opval>>20) & 0x1f
            Rn = (opval>>16) & 0xf
            CRd = (opval>>12) & 0xf
            cp_num = (opval>>8) & 0xf
            offset = opval & 0xff

            if punwl & 4:   # L
                iflags = IF_L
            else:
                iflags = 0

            olist = (
                ArmCoprocOper(cp_num),
                ArmCoprocRegOper(CRd),
                ArmImmOffsetOper(Rn, offset*4, va, pubwl=punwl, psize=psize),
            )
            mnem, opcode = ldc2_mnem[punwl&1]
            return (opcode, mnem, olist, iflags, 0)

        elif (opval & 0xff000010) == 0xfe000000:
            #coproc dp (cdp2)
            return p_coproc_dp(opval, va)

        elif (opval & 0xff000010) == 0xfe000010:
            #mcr2/mrc2
            opcode1 = (opval>>21) & 0x7
            load = (opval>>20) & 1
            CRn = (opval>>16) & 0xf
            Rd = (opval>>12) & 0xf
            cp_num = (opval>>8) & 0xf
            opcode2 = (opval>>5) & 0x7
            CRm = opval & 0xf

            olist = (
                ArmCoprocOper(cp_num),
                ArmCoprocOpcodeOper(opcode1),
                ArmRegOper(Rd, va=va),
                ArmCoprocRegOper(CRn),
                ArmCoprocRegOper(CRm),
                ArmCoprocOpcodeOper(opcode2),
            )
            
            mnem, opcode = mcr2_mnem[load]
            return (opcode, mnem, olist, 0, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=3): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    
vmul_mnems = (
            ('vmla', INS_VMLA),
            ('vmls', INS_VMLS),
            ('vnmla', INS_VNMLA),
            ('vnmls', INS_VNMLS),
            ('vmul', INS_VMUL),
            ('vnmul', INS_VNMUL),
            ('vadd', INS_VADD),
            ('vsub', INS_VSUB),
            ('vdiv', INS_VDIV),
            (None, None),
            ('vfnms', INS_VFNMS),
            ('vfnma', INS_VFNMA),
            ('vfma', INS_VFMA),
            ('vfms', INS_VFMS),
            )
def p_fp_dp(opval, va):
    val1 = opval >> 16
    val2 = opval & 0xffff
    return _do_fp_dp(va, val1, val2)

def _do_fp_dp(va, val1, val2):
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

    # D and S, depending on sz
    rbase = ("s%d","d%d")[sz]

    if opc1sub != 0b1011:
        op = (opc1sub & 0b1000) | ((opc1sub & 0b11)<<1) | (opc3 & 1)
        mnem, opcode = vmul_mnems[op]

        if sz:
            d = (D<<4) | Vd
            m = (M<<4) | Vm
            n = (N<<4) | opc2 #Vn
        else:
            d = (Vd<<1) | D
            m = (Vm<<1) | M
            n = (opc2<<1) | N

        simdflags = (IFS_F32, IFS_F64)[sz]

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
        # VMOV p934     Q#, D#, QQ, DD, DD, SS
        D = (val1 >> 6) & 1
        Vd = (val2 >> 12) & 0xf
        imm4h = val1 & 0xf
        imm4l = val2 & 0xf

        if sz:
            d = (D<<4) | Vd
            m = (M<<4) | Vm
            imm = imm4h<<4 | imm4l
            simdflags = IFS_F64
            rbase = "d%d"
        else:
            d = (Vd<<1) | D
            m = (Vm<<1) | M
            imm = imm4h<<4 | imm4l
            simdflags = IFS_F32
            rbase = "s%d"

        if opc3 & 1 == 0:   # p934
            mnem = 'vmov'
            opcode = INS_VMOV
            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmImmOper(imm),
                    )

        elif opc2 == 0:
            # VABS p822 T2/A2
            if opc3 == 3:
                mnem = 'vabs'
                opcode = INS_VABS

            # VMOV p936 with reg/reg
            elif opc3 & 1:
                mnem = 'vmov'
                opcode = INS_VMOV

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        elif opc2 == 1:
            # VNEG p966 T2/A2
            if opc3 == 0x1:
                mnem = 'vneg'
                opcode = INS_VNEG

            # VSQRT p1056
            elif opc3 == 0x3:
                mnem = 'vsqrt'
                opcode = INS_VSQRT

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        # VCVTB, VCVTT p878
        elif opc2 in (2,3) and opc3 in (1,3):
            T = N
            simdflags = (IFS_F16_32, IFS_F32_16)[val1&1]
            mnem = ('vcvtb','vcvtt')[T]

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                    )

        # VCMP, VCMPE p862
        elif opc2 in (4,5) and opc3 in (1,3):
            E = N
            mnem, opcode = (('vcmp', INS_VCMP),('vcmpe', INS_VCMPE))[E]
            
            if opc2 == 4:
                opers = (
                        ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                        ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                        )
            else:
                opers = (
                        ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                        ArmFloatOper(0.0),
                        )

        # VCVT p874
        elif opc2 == 7 and opc3 == 3:
            mnem = 'vcvt'
            opcode = INS_VCVT
            if sz:
                d = (Vd<<1) | D
                m = (M<<4) | Vm
                simdflags = IFS_F32_F64
                rbase1 = "s%d"
                rbase2 = "d%d"
            else:
                d = (D<<4) | Vd
                m = (Vm<<1) | M
                simdflags = IFS_F64_F32
                rbase1 = "d%d"
                rbase2 = "s%d"

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase1%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase2%m)),
                    )

        # VCVT, VCVTR p868
        elif opc2 in (0b1000,0b1100,0b1101) and opc3 & 1:
            op = opc3>>1
            # S32F64, S32F32, U32F64, U32F32, F64TM, F32TM??
            if op:
                mnem = 'vcvt'
                opcode = INS_VCVT
            else:
                mnem = 'vcvtr'
                opcode = INS_VCVTR

            to_int = opc2 & 0b100
            if to_int:
                signed = opc2&1
                round_zero = op

                d = (Vd<<1) | D
                if sz:
                    m = (M<<4) | Vm
                    simdflags = (IFS_U32_F64, IFS_S32_F64)[signed]
                    rbase1 = "s%d"
                    rbase2 = "d%d"
                else:
                    m = (Vm<<1) | M
                    simdflags = (IFS_U32_F32, IFS_S32_F32)[signed]
                    rbase1 = "s%d"
                    rbase2 = "s%d"

            else:

                signed = op
                round_nearest = False
                m = (Vm<<1) | M
                if sz:
                    d = (D<<4) | Vd
                    simdflags = (IFS_F64_U32, IFS_F64_S32)[signed]
                    rbase1 = "d%d"
                    rbase2 = "s%d"
                else:
                    d = (Vd<<1) | D
                    simdflags = (IFS_F32_U32, IFS_F32_S32)[signed]
                    rbase1 = "s%d"
                    rbase2 = "s%d"

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase1%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase2%m)),
                    )

        # VCVT p872
        elif opc2 in (0b1010,0b1011,0b1110,0b1111) and opc3&1:
            mnem = 'vcvt'
            opcode = INS_VCVT

            U = val1 & 1
            imm4 = val2 & 0xf
            sf = (val2>>8) & 1
            sx = (val2>>7) & 1
            i = (val2>>5) & 1

            dp_op = sf

            op = (val1>>2) & 1

            Q = opc3

            sfidx = (op << 3) | (sf << 2) | (sx << 1) | U
            simdflags = (
                    IFS_F32_S16, IFS_F32_U16, IFS_F32_S32, IFS_F32_U32,
                    IFS_F64_S16, IFS_F64_U16, IFS_F64_S32, IFS_F64_U32,
                    IFS_S16_F32, IFS_U16_F32, IFS_S32_F32, IFS_U32_F32,
                    IFS_S16_F64, IFS_U16_F64, IFS_S32_F64, IFS_U32_F64,
                    ) [sfidx]

            size = (16, 32)[sx]
            frac_bits = size - ((imm4<<1) | i)

            if dp_op:
                d = (D<<4) | Vd
            else:
                d = D | (Vd << 1)

            rbase = ('s%d', 'd%d')[sf]

            opers = (
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                    ArmImmOper(frac_bits),
                    )

    return (opcode, mnem, opers, iflags, simdflags)

def p_advsimd_secondary(val, va, mnem, opcode, flags, opers):
    if opcode == INS_VORR:
        src1 = (val>>16) & 0xf
        src2 = (val) & 0xf

        if src1 == src2:
            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmRegOper(rctx.getRegisterIndex(rbase%n)),
            )
            return 'vmov', INS_VMOV, None, opers
    return None, None, None, None

adv_simd_dts = (IFS_S8, IFS_S16, IFS_S32, IFS_S64, 
                IFS_U8, IFS_U16, IFS_U32, IFS_U64, 
                IFS_I8, IFS_I16, IFS_I32, IFS_I64,
                IFS_P8, IFS_P16, IFS_P32, IFS_P64,
                IFS_F8, IFS_F16, IFS_F32, IFS_F64,
                IFS_8,  IFS_16,  IFS_32,  IFS_64,
                0,0,0,0,
                IFS_F16_32, IFS_F32_16, 0,0,
                IFS_F32_S32, IFS_F32_U32, IFS_S32_F32, IFS_U32_F32,
                )
ADV_SIMD_S8     = 0
ADV_SIMD_U8     = 4
ADV_SIMD_I8     = 8
ADV_SIMD_P8     = 12
ADV_SIMD_F8     = 16
ADV_SIMD_8      = 20
ADV_SIMD_NONE   = 24
ADV_SIMD_F16F32 = 28
ADV_SIMD_F32S32 = 32

adv_simd_3_regs = (  # ABUC fields slammed together
        # a=0000 b=0
        ('vhadd',       INS_VHADD, IFS_S8, None),
        ('vhadd',       INS_VHADD, IFS_S16, None),
        ('vhadd',       INS_VHADD, IFS_S32, None),
        (None,          None, 0, None),
        ('vhadd',       INS_VHADD, IFS_U8, None),
        ('vhadd',       INS_VHADD, IFS_U16, None),
        ('vhadd',       INS_VHADD, IFS_U32, None),
        (None,          None, 0, None),

        # a=0000 b=1
        ('vqadd',       INS_VQADD, IFS_S8, None),
        ('vqadd',       INS_VQADD, IFS_S16, None),
        ('vqadd',       INS_VQADD, IFS_S32, None),
        ('vqadd',       INS_VQADD, IFS_S64, None),
        ('vqadd',       INS_VQADD, IFS_U8, None),
        ('vqadd',       INS_VQADD, IFS_U16, None),
        ('vqadd',       INS_VQADD, IFS_U32, None),
        ('vqadd',       INS_VQADD, IFS_U64, None),

        # a=0001 b=0
        ('vrhadd',      INS_VRHADD, IFS_S8, None),
        ('vrhadd',      INS_VRHADD, IFS_S16, None),
        ('vrhadd',      INS_VRHADD, IFS_S32, None),
        (None,          None, 0, None),
        ('vrhadd',      INS_VRHADD, IFS_U8, None),
        ('vrhadd',      INS_VRHADD, IFS_U16, None),
        ('vrhadd',      INS_VRHADD, IFS_U32, None),
        (None,          None, 0, None),

        # a=0001 b=1
        ('vand',        INS_VAND, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        ('vorr',        INS_VORR, 0, p_advsimd_secondary),    # vmov if source registers identical
        ('vorn',        INS_VORN, 0, None),
        ('veor',        INS_VEOR, 0, None),
        ('vbsl',        INS_VBSL, 0, None),
        ('vbit',        INS_VBIT, 0, None),
        ('vbif',        INS_VBIF, 0, None),

        # a=0010 b=0
        ('vhsub',       INS_VHSUB, IFS_S8, None),
        ('vhsub',       INS_VHSUB, IFS_S16, None),
        ('vhsub',       INS_VHSUB, IFS_S32, None),
        (None,          None, 0, None),
        ('vhsub',       INS_VHSUB, IFS_U8, None),
        ('vhsub',       INS_VHSUB, IFS_U16, None),
        ('vhsub',       INS_VHSUB, IFS_U32, None),
        (None,          None, 0, None),

        # a=0010 b=1
        ('vqsub',       INS_VQSUB, IFS_S8, None),
        ('vqsub',       INS_VQSUB, IFS_S16, None),
        ('vqsub',       INS_VQSUB, IFS_S32, None),
        ('vqsub',       INS_VQSUB, IFS_S64, None),
        ('vqsub',       INS_VQSUB, IFS_U8, None),
        ('vqsub',       INS_VQSUB, IFS_U16, None),
        ('vqsub',       INS_VQSUB, IFS_U32, None),
        ('vqsub',       INS_VQSUB, IFS_U64, None),

        # a=0011 b=0
        ('vcgt',        INS_VCGT, IFS_S8, None),
        ('vcgt',        INS_VCGT, IFS_S16, None),
        ('vcgt',        INS_VCGT, IFS_S32, None),
        (None,          None, 0, None),
        ('vcgt',        INS_VCGT, IFS_U8, None),
        ('vcgt',        INS_VCGT, IFS_U16, None),
        ('vcgt',        INS_VCGT, IFS_U32, None),
        (None,          None, 0, None),

        # a=0011 b=1
        ('vcge',        INS_VCGE, IFS_S8, None),
        ('vcge',        INS_VCGE, IFS_S16, None),
        ('vcge',        INS_VCGE, IFS_S32, None),
        (None,          None, 0, None),
        ('vcge',        INS_VCGE, IFS_U8, None),
        ('vcge',        INS_VCGE, IFS_U16, None),
        ('vcge',        INS_VCGE, IFS_U32, None),
        (None,          None, 0, None),

        # a=0100 b=0
        ('vshl',        INS_VSHL, IFS_S8, None),           # d, m, n, not d, n, m like all the others in this category
        ('vshl',        INS_VSHL, IFS_S16, None),
        ('vshl',        INS_VSHL, IFS_S32, None),
        ('vshl',        INS_VSHL, IFS_S64, None),
        ('vshl',        INS_VSHL, IFS_U8, None),
        ('vshl',        INS_VSHL, IFS_U16, None),
        ('vshl',        INS_VSHL, IFS_U32, None),
        ('vshl',        INS_VSHL, IFS_U64, None),

        # a=0100 b=1
        ('vqshl',       INS_VQSHL, IFS_S8, None),
        ('vqshl',       INS_VQSHL, IFS_S16, None),
        ('vqshl',       INS_VQSHL, IFS_S32, None),
        ('vqshl',       INS_VQSHL, IFS_S64, None),
        ('vqshl',       INS_VQSHL, IFS_U8, None),
        ('vqshl',       INS_VQSHL, IFS_U16, None),
        ('vqshl',       INS_VQSHL, IFS_U32, None),
        ('vqshl',       INS_VQSHL, IFS_U64, None),

        # a=0101 b=0
        ('vrshl',       INS_VRSHL, IFS_S8, None),
        ('vrshl',       INS_VRSHL, IFS_S16, None),
        ('vrshl',       INS_VRSHL, IFS_S32, None),
        ('vrshl',       INS_VRSHL, IFS_S64, None),
        ('vrshl',       INS_VRSHL, IFS_U8, None),
        ('vrshl',       INS_VRSHL, IFS_U16, None),
        ('vrshl',       INS_VRSHL, IFS_U32, None),
        ('vrshl',       INS_VRSHL, IFS_U64, None),

        # a=0101 b=1
        ('vqrshl',      INS_VQRSHL, IFS_S8, None),
        ('vqrshl',      INS_VQRSHL, IFS_S16, None),
        ('vqrshl',      INS_VQRSHL, IFS_S32, None),
        ('vqrshl',      INS_VQRSHL, IFS_S64, None),
        ('vqrshl',      INS_VQRSHL, IFS_U8, None),
        ('vqrshl',      INS_VQRSHL, IFS_U16, None),
        ('vqrshl',      INS_VQRSHL, IFS_U32, None),
        ('vqrshl',      INS_VQRSHL, IFS_U64, None),

        # a=0110 b=0
        ('vmax',        INS_VMAX, IFS_S8, None),
        ('vmax',        INS_VMAX, IFS_S16, None),
        ('vmax',        INS_VMAX, IFS_S32, None),
        (None,          None, 0, None),
        ('vmax',        INS_VMAX, IFS_U8, None),
        ('vmax',        INS_VMAX, IFS_U16, None),
        ('vmax',        INS_VMAX, IFS_U32, None),
        (None,          None, 0, None),

        # a=0110 b=1
        ('vmin',        INS_VMIN, IFS_S8, None),
        ('vmin',        INS_VMIN, IFS_S16, None),
        ('vmin',        INS_VMIN, IFS_S32, None),
        (None,          None, 0, None),
        ('vmin',        INS_VMIN, IFS_U8, None),
        ('vmin',        INS_VMIN, IFS_U16, None),
        ('vmin',        INS_VMIN, IFS_U32, None),
        (None,          None, 0, None),

        # a=0111 b=0
        ('vabd',        INS_VABD, IFS_S8, None),
        ('vabd',        INS_VABD, IFS_S16, None),
        ('vabd',        INS_VABD, IFS_S32, None),
        (None,          None, 0, None),
        ('vabd',        INS_VABD, IFS_U8, None),
        ('vabd',        INS_VABD, IFS_U16, None),
        ('vabd',        INS_VABD, IFS_U32, None),
        (None,          None, 0, None),

        # a=0111 b=1
        ('vaba',        INS_VABA, IFS_S8, None),
        ('vaba',        INS_VABA, IFS_S16, None),
        ('vaba',        INS_VABA, IFS_S32, None),
        (None,          None, 0, None),
        ('vaba',        INS_VABA, IFS_U8, None),
        ('vaba',        INS_VABA, IFS_U16, None),
        ('vaba',        INS_VABA, IFS_U32, None),
        (None,          None, 0, None),

        # a=1000 b=0
        ('vadd',        INS_VADD, IFS_I8, None),
        ('vadd',        INS_VADD, IFS_I16, None),
        ('vadd',        INS_VADD, IFS_I32, None),
        ('vadd',        INS_VADD, IFS_I64, None),
        ('vsub',        INS_VSUB, IFS_I8, None),
        ('vsub',        INS_VSUB, IFS_I16, None),
        ('vsub',        INS_VSUB, IFS_I32, None),
        ('vsub',        INS_VSUB, IFS_I64, None),

        # a=1000 b=1
        ('vtst',        INS_VTST, IFS_8, None),
        ('vtst',        INS_VTST, IFS_16, None),
        ('vtst',        INS_VTST, IFS_32, None),
        (None,          None, 0, None),
        ('vceq',        INS_VCEQ, IFS_I8, None),
        ('vceq',        INS_VCEQ, IFS_I16, None),
        ('vceq',        INS_VCEQ, IFS_I32, None),
        (None,          None, 0, None),

        # a=1001 b=0
        ('vmla',        INS_VMLA, IFS_I8, None),
        ('vmla',        INS_VMLA, IFS_I16, None),
        ('vmla',        INS_VMLA, IFS_I32, None),
        (None,          None, 0, None),
        ('vmls',        INS_VMLS, IFS_I8, None),
        ('vmls',        INS_VMLS, IFS_I16, None),
        ('vmls',        INS_VMLS, IFS_I32, None),
        (None,          None, 0, None),

        # a=1001 b=1
        ('vmul',        INS_VMUL, IFS_I8, None),
        ('vmul',        INS_VMUL, IFS_I16, None),
        ('vmul',        INS_VMUL, IFS_I32, None),
        (None,          None, 0, None),
        ('vmul',        INS_VMUL, IFS_P8, None),
        ('vmul',        INS_VMUL, IFS_P16, None),
        ('vmul',        INS_VMUL, IFS_P32, None),
        (None,          None, 0, None),

        # a=1010 b=0
        ('vpmax',       INS_VPMAX, IFS_S8, None),
        ('vpmax',       INS_VPMAX, IFS_S16, None),
        ('vpmax',       INS_VPMAX, IFS_S32, None),
        (None,          None, 0, None),
        ('vpmax',       INS_VPMAX, IFS_U8, None),
        ('vpmax',       INS_VPMAX, IFS_U16, None),
        ('vpmax',       INS_VPMAX, IFS_U32, None),
        (None,          None, 0, None),

        # a=1010 b=1
        ('vpmin',       INS_VPMIN, IFS_S8, None),
        ('vpmin',       INS_VPMIN, IFS_S16, None),
        ('vpmin',       INS_VPMIN, IFS_S32, None),
        (None,          None, 0, None),
        ('vpmin',       INS_VPMIN, IFS_U8, None),
        ('vpmin',       INS_VPMIN, IFS_U16, None),
        ('vpmin',       INS_VPMIN, IFS_U32, None),
        (None,          None, 0, None),

        # a=1011 b=0
        (None,          None, 0, None),
        ('vqdmulh',     INS_VQDMULH, IFS_S16, None),
        ('vqdmulh',     INS_VQDMULH, IFS_S32, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        ('vqrdmulh',    INS_VQRDMULH, IFS_S16, None),
        ('vqrdmulh',    INS_VQRDMULH, IFS_S32, None),
        (None,          None, 0, None),

        # a=1011 b=1
        ('vpadd',       INS_VPADD, IFS_I8, None),
        ('vpadd',       INS_VPADD, IFS_I16, None),
        ('vpadd',       INS_VPADD, IFS_I32, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),

        # a=1100 b=0
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),
        (None, None, 0, None),

        # a=1100 b=1
        ('vfma',        INS_VFMA, IFS_F32, None),
        (None,          None, 0, None),
        ('vfms',        INS_VFMS, IFS_F32, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),

        # a=1101 b=0
        ('vadd',        INS_VADD, IFS_F32, None),
        (None,          None, 0, None),
        ('vsub',        INS_VSUB, IFS_F32, None),
        (None,          None, 0, None),
        ('vpadd',       INS_VPADD, IFS_F32, None),
        (None,          None, 0, None),
        ('vabd',        INS_VABD, IFS_F32, None),
        (None,          None, 0, None),

        # a=1101 b=1
        ('vmla',        INS_VMLA, IFS_F32, None),
        (None,          None, 0, None),
        ('vmls',        INS_VMLS, IFS_F32, None),
        (None,          None, 0, None),
        ('vmul',        INS_VMUL, IFS_F32, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),

        # a=1110 b=0
        ('vceq',        INS_VCEQ, IFS_F32, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        ('vcge',        INS_VCGE, IFS_F32, None),
        (None,          None, 0, None),
        ('vcgt',        INS_VCGT, IFS_F32, None),
        (None,          None, 0, None),

        # a=1110 b=1
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        ('vacge',       INS_VACGE, IFS_F32, None),
        (None,          None, 0, None),
        ('vacgt',       INS_VACGT, IFS_F32, None),
        (None,          None, 0, None),

        # a=1111 b=0
        ('vmax',        INS_VMAX, IFS_F32, None),
        (None,          None, 0, None),
        ('vmin',        INS_VMIN, IFS_F32, None),
        (None,          None, 0, None),
        ('vpmax',       INS_VPMAX, IFS_F32, None),
        (None,          None, 0, None),
        ('vpmin',       INS_VPMIN, IFS_F32, None),
        (None,          None, 0, None),

        # a=1111 b=1
        ('vrecps',      INS_VRECPS, IFS_F32, None),
        (None,          None, 0, None),
        ('vrsqrts',     INS_VRSQRTS, IFS_F32, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),
        (None,          None, 0, None),

    )

adv_simd_1modimm = (
        # op = 0
        # 0xx0 and 0xx1
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        # 10x0 and 10x1
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vorr',        INS_VORR, 0, None),
        # 11xx
        ('vmov',        INS_VMOV, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vmov',        INS_VMOV, 0, None),
        ('vmov',        INS_VMOV, 0, None),

        # op = 1
        # 0xx0 and 0xx1
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        # 10x0 and 10x1
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        ('vmvn',        INS_VMVN, 0, None),
        ('vbic',        INS_VBIC, 0, None),
        # 110x
        ('vmvn',        INS_VMVN, 0, None),
        ('vmvn',        INS_VMVN, 0, None),
        # 1110
        ('vmov',        INS_VMOV, 0, None),
        # 1111 undef
        ('vector UNDEF', None, 0, None),
    )

adv_simd_3diffregs = (
        # a=0, u=0
        ('vaddl',       INS_VADDL, ADV_SIMD_S8, 1, 0, 0),
        ('vaddl',       INS_VADDL, ADV_SIMD_U8, 1, 0, 0),
        ('vaddw',       INS_VADDW, ADV_SIMD_S8, 1, 1, 0),
        ('vaddw',       INS_VADDW, ADV_SIMD_U8, 1, 1, 0),
        ('vsubl',       INS_VSUBL, ADV_SIMD_S8, 1, 0, 0),
        ('vsubl',       INS_VSUBL, ADV_SIMD_U8, 1, 0, 0),
        ('vsubw',       INS_VSUBW, ADV_SIMD_S8, 1, 1, 0),
        ('vsubw',       INS_VSUBW, ADV_SIMD_U8, 1, 1, 0),
        # a=4, u=0/1
        ('vaddhn',      INS_VADDHN, ADV_SIMD_I8+1, 0, 1, 1),
        ('vraddhn',     INS_VRADDHN, ADV_SIMD_I8+1, 0, 1, 1),
        # a=5, u=0/1
        ('vabal',       INS_VABAL, ADV_SIMD_S8, 1, 0, 0),
        ('vabal',       INS_VABAL, ADV_SIMD_U8, 1, 0, 0),
        # a=6
        ('vsubhn',      INS_VSUBHN, ADV_SIMD_I8+1, 0, 1, 1),
        ('vrsubhn',     INS_VRSUBHN, ADV_SIMD_I8+1,0, 1, 1),
        # a=7
        ('vabdl',       INS_VABDL, ADV_SIMD_S8, 1, 0, 0),
        ('vabdl',       INS_VABDL, ADV_SIMD_U8, 1, 0, 0),
        # a=8
        ('vmlal',       INS_VMLAL, ADV_SIMD_S8, 1, 0, 0),
        ('vmlal',       INS_VMLAL, ADV_SIMD_U8, 1, 0, 0),
        # a=9
        ('vqdmlal',     INS_VQDMLAL, ADV_SIMD_S8, 1, 0, 0),
        (None, None, None, 1, 0, 0),
        # a=0xa
        ('vmlsl',       INS_VMLSL, ADV_SIMD_S8, 1, 0, 0),
        ('vmlsl',       INS_VMLSL, ADV_SIMD_U8, 1, 0, 0),
        # a=0xb
        ('vqdmlsl',     INS_VQDMLSL, ADV_SIMD_S8, 1, 0, 0),
        (None, None, 0, 1, 0, 0),
        # a=0xc
        ('vmull',       INS_VMULL, ADV_SIMD_S8, 1, 0, 0),
        ('vmull',       INS_VMULL, ADV_SIMD_U8, 1, 0, 0),
        # a=0xd
        ('vqdmull',     INS_VQDMULL, ADV_SIMD_S8, 1, 0, 0),
        (None, None, 0, 1, 0, 0),
        # a=0xe
        ('vmull',       INS_VMULL, ADV_SIMD_P8,1, 0, 0),
        ('vmull',       INS_VMULL, ADV_SIMD_P8,1, 0, 0),
        # a=0xf  - nothing...
        (None, 0, 0,0,0,0),
        (None, 0, 0,0,0,0),
        )

adv_simd_2regs_scalar = (
        # a=0
        ('vmla',        INS_VMLA, ADV_SIMD_I8, 0,0,0),    # enc t1/a1
        ('vmla',        INS_VMLA, ADV_SIMD_I8, 1,1,0),   
        # a=1
        ('vmla',        INS_VMLA, ADV_SIMD_F8, 0,0,0),    # enc t1/a1 fp
        ('vmla',        INS_VMLA, ADV_SIMD_F8, 1,1,0),    # fp
        # a=2
        ('vmlal',       INS_VMLAL, ADV_SIMD_S8, 1,0,0),     # enc t2/a2
        ('vmlal',       INS_VMLAL, ADV_SIMD_U8, 1,0,0),     
        # a=3
        ('vqdmlal',     INS_VQDMLAL, 0, 1,0,0),
        (None, None, None, None, None, None),
        # a=4
        ('vmls',        INS_VMLS, ADV_SIMD_I8, 0,0,0),    # enc t1/a1
        ('vmls',        INS_VMLS, ADV_SIMD_I8, 1,1,0),
        # a=5
        ('vmls',        INS_VMLS, ADV_SIMD_F8, 0,0,0),   # enc t1/a1
        ('vmls',        INS_VMLS, ADV_SIMD_F8, 1,1,0),
        # a=6
        ('vmlsl',       INS_VMLSL, ADV_SIMD_S8, 1,0,0),  # enc t2/a2
        ('vmlsl',       INS_VMLSL, ADV_SIMD_U8, 1,0,0),
        # a=7
        ('vqdmlsl',     INS_VQDMLSL, ADV_SIMD_S8, 1,0,0),
        (None, None, None, None, None, None),
        # a=8
        ('vmul',        INS_VMUL, ADV_SIMD_I8, 0,0,0),     # enc t1/a1
        ('vmul',        INS_VMUL, ADV_SIMD_I8, 1,1,0),
        # a=9
        ('vmul',        INS_VMUL, ADV_SIMD_F8, 0,0,0),
        ('vmul',        INS_VMUL, ADV_SIMD_F8, 1,1,0),
        # a=0xa
        ('vmull',       INS_VMULL, ADV_SIMD_S8, 1,0,0),
        ('vmull',       INS_VMULL, ADV_SIMD_U8, 1,0,0),
        # a=0xb
        ('vqdmull',     INS_VQDMULL, ADV_SIMD_S8, 1,0,0),  # enc t2/a2
        (None, None, None, None, None, None),
        # a=0xc
        ('vqdmulh',     INS_VQDMULH, ADV_SIMD_S8, 0,0,0),  # enc t2/a2
        ('vqdmulh',     INS_VQDMULH, ADV_SIMD_S8, 1,1,0),
        # a=0xd
        ('vqrdmulh',    INS_VQRDMULH, ADV_SIMD_S8, 0,0,0),   # enc t2/a2
        ('vqrdmulh',    INS_VQRDMULH, ADV_SIMD_S8, 1,1,0),
        # a=0xe
        (None, None, None, None, None, None),
        (None, None, None, None, None, None),
        # a=0xf
        (None, None, None, None, None, None),
        (None, None, None, None, None, None),
)

adv_simd_2regs_misc = (
        # a=0 b=000xx
        ('vrev64',      INS_VREV64, ADV_SIMD_8, 0,0, 0),
        ('vrev64',      INS_VREV64, ADV_SIMD_8, 1,1, 0),
        ('vrev32',      INS_VREV32, ADV_SIMD_8, 0,0, 0),
        ('vrev32',      INS_VREV32, ADV_SIMD_8, 1,1, 0),
        # a=0 b=001xx
        ('vrev16',      INS_VREV16, ADV_SIMD_8, 0,0, 0),
        ('vrev16',      INS_VREV16, ADV_SIMD_8, 1,1, 0),
        (None, None, ADV_SIMD_S8, 0,0, 0),
        (None, None, ADV_SIMD_S8, 1,1, 0),
        # a=0 b=010xx
        ('vpaddl',      INS_VPADDL, ADV_SIMD_S8, 0,0, 0),
        ('vpaddl',      INS_VPADDL, ADV_SIMD_S8, 1,1, 0),
        ('vpaddl',      INS_VPADDL, ADV_SIMD_U8, 0,0, 0),
        ('vpaddl',      INS_VPADDL, ADV_SIMD_U8, 1,1, 0),
        # a=0 b=011xx
        (None,          None, 0, 0,0, 0),
        (None,          None, 0, 0,0, 0),
        (None,          None, 0, 0,0, 0),
        (None,          None, 0, 0,0, 0),
        # a=0 b=100xx
        ('vcls',        INS_VCLS, ADV_SIMD_S8, 0,0, 0),
        ('vcls',        INS_VCLS, ADV_SIMD_S8, 1,1, 0),
        ('vclz',        INS_VCLZ, ADV_SIMD_I8, 0,0, 0),
        ('vclz',        INS_VCLZ, ADV_SIMD_I8, 1,1, 0),
        # a=0 b=1010x
        ('vcnt',        INS_VCNT, ADV_SIMD_8, 0,0, 0),
        ('vcnt',        INS_VCNT, ADV_SIMD_8, 1,1, 0),
        ('vmvn',        INS_VMVN, ADV_SIMD_NONE, 0,0, 0),
        ('vmvn',        INS_VMVN, ADV_SIMD_NONE, 1,1, 0),
        # a=0 b=110xx
        ('vpadal',      INS_VPADAL, ADV_SIMD_S8, 0,0, 0),
        ('vpadal',      INS_VPADAL, ADV_SIMD_S8, 1,1, 0),
        ('vpadal',      INS_VPADAL, ADV_SIMD_U8, 0,0, 0),
        ('vpadal',      INS_VPADAL, ADV_SIMD_U8, 1,1, 0),
        # a=0 b=1110x
        ('vqabs',       INS_VQABS, ADV_SIMD_S8, 0,0, 0),
        ('vqabs',       INS_VQABS, ADV_SIMD_S8, 1,1, 0),
        # a=0 b=1111x
        ('vqneg',       INS_VQNEG, ADV_SIMD_S8, 0,0, 0),
        ('vqneg',       INS_VQNEG, ADV_SIMD_S8, 1,1, 0),
        # a=1 b=000xx
        ('vcgt',        INS_VCGT, ADV_SIMD_S8, 0,0, 0), # , #0
        ('vcgt',        INS_VCGT, ADV_SIMD_S8, 1,1, 0), # , #0
        ('vcge',        INS_VCGE, ADV_SIMD_S8, 0,0, 0), # , #0
        ('vcge',        INS_VCGE, ADV_SIMD_S8, 1,1, 0), # , #0
        # a=1 b=001xx
        ('vceq',        INS_VCEQ, ADV_SIMD_I8, 0,0, 0), # , #0
        ('vceq',        INS_VCEQ, ADV_SIMD_I8, 1,1, 0), # , #0
        ('vcle',        INS_VCLE, ADV_SIMD_I8, 0,0, 0), # , #0
        ('vcle',        INS_VCLE, ADV_SIMD_I8, 1,1, 0), # , #0
        # a=1 b=010xx
        ('vclt',        INS_VCLT, ADV_SIMD_S8, 0,0, 0), # , #0
        ('vclt',        INS_VCLT, ADV_SIMD_S8, 1,1, 0), # , #0
        (None,  None, ADV_SIMD_S8, 0,0, 0),
        (None,  None, ADV_SIMD_S8, 1,1, 0),
        # a=1 b=011xx
        ('vabs',        INS_VABS, ADV_SIMD_S8, 0,0, 0),
        ('vabs',        INS_VABS, ADV_SIMD_S8, 1,1, 0),
        ('vneg',        INS_VNEG, ADV_SIMD_S8, 0,0, 0),
        ('vneg',        INS_VNEG, ADV_SIMD_S8, 1,1, 0),
        # a=1 b=100xx
        ('vcgt',        INS_VCGT, ADV_SIMD_F8, 0,0, 0), # , #0
        ('vcgt',        INS_VCGT, ADV_SIMD_F8, 1,1, 0), # , #0
        ('vcge',        INS_VCGE, ADV_SIMD_F8, 0,0, 0), # , #0
        ('vcge',        INS_VCGE, ADV_SIMD_F8, 1,1, 0), # , #0
        # a=1 b=101xx
        ('vceq',        INS_VCEQ, ADV_SIMD_F8, 0,0, 0), # , #0
        ('vceq',        INS_VCEQ, ADV_SIMD_F8, 1,1, 0), # , #0
        ('vcle',        INS_VCLE, ADV_SIMD_F8, 0,0, 0), # , #0
        ('vcle',        INS_VCLE, ADV_SIMD_F8, 1,1, 0), # , #0
        # a=1 b=110xx
        ('vclt',        INS_VCLT, ADV_SIMD_F8, 0,0, 0),
        ('vclt',        INS_VCLT, ADV_SIMD_F8, 1,1, 0),
        (None,  None, ADV_SIMD_F8, 0,0, 0),
        (None,  None, ADV_SIMD_F8, 1,1, 0),
        # a=1 b=111xx
        ('vabs',        INS_VABS, ADV_SIMD_F8, 0,0, 0),
        ('vabs',        INS_VABS, ADV_SIMD_F8, 1,1, 0),
        ('vneg',        INS_VNEG, ADV_SIMD_F8, 0,0, 0),
        ('vneg',        INS_VNEG, ADV_SIMD_F8, 1,1, 0),

        ############## 
        # a=10 b=0000x
        ('vswp',        INS_VSWP, ADV_SIMD_NONE, 0,0, 0),
        ('vswp',        INS_VSWP, ADV_SIMD_NONE, 1,1, 0),
        ('vtrn',        INS_VTRN, ADV_SIMD_8, 0,0, 0),
        ('vtrn',        INS_VTRN, ADV_SIMD_8, 1,1, 0),
        # a=10 b=001xx
        ('vuzp',        INS_VUZP, ADV_SIMD_8, 0,0, 0),
        ('vuzp',        INS_VUZP, ADV_SIMD_8, 1,1, 0),
        ('vzip',        INS_VZIP, ADV_SIMD_8, 0,0, 0),
        ('vzip',        INS_VZIP, ADV_SIMD_8, 1,1, 0),
        # a=10 b=010xx
        ('vmovn',       INS_VMOVN, ADV_SIMD_I8+1, 0,1, 0),
        ('vqmovun',         INS_VQMOVUN, ADV_SIMD_S8+1, 0,1, 0),
        ('vqmovn',      INS_VQMOVN, ADV_SIMD_S8+1, 0,1, 0),
        ('vqmovn',      INS_VQMOVN, ADV_SIMD_U8+1, 0,1, 0),
        # a=10 b=011xx
        ('vshll',       INS_VSHLL, ADV_SIMD_I8, 1,0, 0),      # Qd, Dm, #imm.... one of these is not like the others...
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=10 b=100xx
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=10 b=1010x
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=10 b=110xx
        ('vcvt',        INS_VCVT, ADV_SIMD_F16F32-1, 0,1, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=10 b=111xx
        ('vcvt',        INS_VCVT, ADV_SIMD_F16F32, 1,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=11 b=000xx
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=11 b=001xx
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=11 b=010xx
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=11 b=011xx
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        (None,  0, 0, 0,0, 0),
        # a=11 b=100xx
        ('vrecpe',      INS_VRECPE, ADV_SIMD_S8, 0,0, 0),
        ('vrecpe',      INS_VRECPE, ADV_SIMD_S8, 0,0, 0),
        ('vrsqrte',     INS_VRSQRTE, ADV_SIMD_S8, 0,0, 0),
        ('vrsqrte',     INS_VRSQRTE, ADV_SIMD_S8, 0,0, 0),
        # a=11 b=101xx
        ('vrecpe',      INS_VRECPE, ADV_SIMD_S8, 0,0, 0),
        ('vrecpe',      INS_VRECPE, ADV_SIMD_S8, 0,0, 0),
        ('vrsqrte',     INS_VRSQRTE, ADV_SIMD_S8, 0,0, 0),
        ('vrsqrte',     INS_VRSQRTE, ADV_SIMD_S8, 0,0, 0),
        # a=11 b=110xx
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32-2, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32-2, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32-1, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32-1, 0,0, 0),
        # a=11 b=111xx
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32+1, 0,0, 0),
        ('vcvt',        INS_VCVT, ADV_SIMD_F32S32+1, 0,0, 0),
)


def adv_simd_ldst_32(val, va):
    u = (val>>24) & 1
    return _do_adv_simd_ldst_32(val, va, u)

def _do_adv_simd_ldst_32(val, va, u):
    a = (val >> 23) & 1
    l = (val >> 21) & 1

    optype = (val >> 8) & 0xf

    d = (val >> 22) & 1
    rn = (val >> 16) & 0xf
    vd = (val >> 12) & 0xf
    rm = val & 0xf
    dd = vd | (d << 4)

    sflag, size =  ((IFS_8,1), (IFS_16,2), (IFS_32,4), (IFS_64,8))[(val >> 6) & 3]
    align = (1,8,16,32)[(val >> 4) & 3]

    simdflags = sflag
    writeback = (rm != 15)
    pubwl = PUxWL_DFLT | (writeback<<1)
    iflags = (0, IF_W)[writeback]
    opers = ()

    if l == 0:
        # store
        if a == 0:
            count = (1,2,4,2,3,3,3,1,1,1,2) [ optype ]

            # multiple elements
            if optype in (0b0010, 0b0110, 0b0111, 0b1010):
                # vst1
                mnem = 'vst1'
                opers = (
                        ArmExtRegListOper(dd, count, 1),    # size in this context means use "D#" registers
                        ArmImmOffsetOper(rn, 0, va, pubwl=pubwl, psize=size, tsize=size),
                        )

            elif optype in (0b0011, 0b1000, 0b1001):
                # vst2
                mnem = 'vst2'
            elif optype in (0b0100, 0b0101):
                # vst3
                mnem = 'vst3'
                inc = 1 + (optype&1)
                opers = (
                        ArmExtRegListOper(dd, count, 1, inc),
                        ArmImmOffsetOper(rn, 0, va, pubwl=pubwl, psize=size, tsize=size),
                        )

            elif optype in (0b0000, 0b0001):
                # vst4
                mnem = 'vst4'

        else:
            # single elements
            index_align = (val >> 4) & 0xf
            size = (val >> 10) & 3

            if optype in (0b0000, 0b0100, 0b1000):
                # vst1
                mnem = 'vst1'
                opers = (
                        ArmExtRegListOper(dd, count, 1),
                        ArmImmOffsetOper(rn, 0, va, pubwl=pubwl, psize=size, tsize=size),
                        )
            elif optype in (0b0001, 0b0101, 0b1001):
                # vst2
                mnem = 'vst2'
            elif optype in (0b0010, 0b0110, 0b1010):
                # vst3
                mnem = 'vst3'
            elif optype in (0b0011, 0b0111, 0b1011):
                # vst4
                mnem = 'vst4'

    else:
        # load
        if a:
            # multiple elements
            if optype in (0b0010, 0b0110, 0b0111, 0b1010):
                # vld1  multiple single element
                mnem = 'vld1'
            elif optype in (0b0011, 0b1000, 0b1001):
                # vld2  multiple 2-element structures
                mnem = 'vld2'
            elif optype in (0b0100, 0b0101):
                # vld3  multiple 3-element structures
                mnem = 'vld3'
            elif optype in (0b0000, 0b0001):
                # vld4  multiple 4-element structures
                mnem = 'vld4'

        else:
            # single elements
            if optype in (0b0000, 0b0100, 0b1000):
                # vld1  single element to one lane
                mnem = 'vld1'
            elif optype == 0b1100:
                # vld1  single element to all lanes
                mnem = 'vld1'
            elif optype in (0b0001, 0b0101, 0b1001):
                # vld2  single 2-element structure to one lane
                mnem = 'vld2'
            elif optype == 0b1101:
                # vld2  single 2-element structure to all lanes
                mnem = 'vld2'
            elif optype in (0b0010, 0b0110, 0b1010):
                # vld3  single 3-element structure to one lane
                mnem = 'vld3'
            elif optype == 0b1110:
                # vld3  single 3-element structure to all lanes
                mnem = 'vld3'
            elif optype in (0b0011, 0b0111, 0b1011):
                # vld4  single 4-element structure to one lane
                mnem = 'vld4'
            elif optype == 0b1111:
                # vld4  single 4-element structure to all lanes
                mnem = 'vld4'

    return opcode, mnem, opers, iflags, simdflags    # no iflags, only simdflags for this one

def adv_simd_32(val, va):
    u = (val>>24) & 1
    return _do_adv_simd_32(val, va, u)

def _do_adv_simd_32(val, va, u):
    # aside from u and the first 8 bits, ARM and Thumb2 decode identically (A7-259)

    # initial breakdown (to find the right type of instruction)
    a = (val>>19) & 0x1f
    b = (val>>8) & 0xf
    c = (val>>4) & 0xf

    # shared 
    q = (val >> 6) & 0x1

    d = (val >> 18) & 0x10
    d |= ((val >> 12) & 0xf)

    n = (val >> 3) & 0x10
    n |= ((val >> 16) & 0xf)
    
    m = (val >> 1) & 0x10
    m |= (val & 0xf)

    rbase = ('d%d', 'q%d')[q]

    if not (a & 0x10):
        # three registers of the same length
        a = (val>>8) & 0xf
        b = (val>>4) & 1
        c = (val>>20) & 3

        index = c | (u<<2) | (b<<3) | (a<<4)
        mnem, opcode, simdflags, handler = adv_simd_3_regs[index]

        d >>= q
        n >>= q
        m >>= q

        if (a & 0xe) == 4:
            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                ArmRegOper(rctx.getRegisterIndex(rbase%n)),
                )
        else:
            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmRegOper(rctx.getRegisterIndex(rbase%n)),
                ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                )

        if handler is not None:
            nmnem, nopcode, nflags, nopers = handler(val, va, mnem, opcode, simdflags, opers)
            if nmnem is not None:
                mnem = nmnem
                opcode = nopcode
            if nflags is not None:
                simdflags = nflags
            if nopers is not None:
                opers = nopers

        if mnem is None:
            raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding (3reg): a:%x b:%x u:%x c:%x" %\
                    (a, b, u, c),
                    bytez=struct.pack('<L', val), va=va)

        return opcode, mnem, opers, IF_ADV_SIMD, simdflags

    elif (a & 0x17) == 0x10 and (c & 0x9) == 1:
        # one register and modified immediate
        op = (c>>1) & 1
        cmode = b

        index = (op<<4) | cmode
        mnem, opcode, simdflags, handler = adv_simd_1modimm[index]
        if mnem is None:
            raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding",
                    bytez=struct.pack('<L', val), va=va)

        abcdefgh = (u<<7) | ((val>>12) & 0x70) | (val & 0xf)

        handler = adv_simd_modifiers[index]
        if handler is None:
            raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding: modified immediate out of range",
                    bytez=struct.pack('<L', val), va=va)
        simdflags, size, val = handler(abcdefgh)

        d >>= q

        if simdflags in (IFS_F8, IFS_F16, IFS_F32, IFS_F64):
            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmFloatOper(val, size=size),
                )
        else:
            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmImmOper(val, size=size),
                )

        return opcode, mnem, opers, IF_ADV_SIMD, simdflags

        # must be ordered after previous, since this mask collides
    elif ((a & 0x10) == 0x10 and (c & 0x9) in (1, 9)):
        # two registers and a shift amount
        a = (val>>8) & 0xf
        b = (val>>6) & 1
        l = (val>>7) & 1
        
        index = (a<<3) | (u<<2) | (b<<1) | l
        mnem, opcode, enctype, foffset = adv_2regs_shift[index]
        if mnem is None:
            raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding (2reg_shift)",
                    bytez=struct.pack('<L', val), va=va)

        d >>= q
        m >>= q

        imm = (val >> 16) & 0x3f
        if not (imm & 0b111000) and not l:
            raise Exception("AdvSIMD: decoding as 2reg_shift and should be 1regModImm")

        shift_amount = 0
        simdflags = 0

        if enctype == 0:    # VSHR used as test
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                shift_amount = 16-imm

            simdflags = adv_2_vqshl_typesize.get(esize)[u+2]

        elif enctype == 1:  # VSRI
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                shift_amount = 16-imm

            simdflags = { 8: IFS_8, 16: IFS_16, 32: IFS_32, 64: IFS_64 }[esize]

        elif enctype == 2:    # VQSHLU used as test
            limm = (l<<6) | imm

            op = a & 1

            if limm & 0b1000000:
                esize = 64
                shift_amount = imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = imm - 32
            elif limm & 0b0010000:
                esize = 16
                shift_amount = imm - 16
            elif limm & 0b0001000:
                esize = 8
                shift_amount = imm - 8

            uop = (u<<1) | op
            simdflags = adv_2_vqshl_typesize.get(esize)[uop]

        elif enctype == 3:      # VSHRN needs different simdflags...
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                shift_amount = 16-imm

            idx = {8:1, 16:2, 32:3, 64:4}[esize]
            simdflags = adv_simd_dts[(idx) + foffset]

        elif enctype == 4:
            limm = (l<<6) | imm

            if not (limm & 0b111):
                raise Exception("MUST MAKE THIS DO vmovl ENCODING")

            op = a & 1

            if limm & 0b1000000:
                esize = 64
                shift_amount = imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = imm - 32
            elif limm & 0b0010000:
                esize = 16
                shift_amount = imm - 16
            elif limm & 0b0001000:
                esize = 8
                shift_amount = imm - 8

            uop = (u<<1) | op
            #print "uop: %x" % uop
            simdflags = adv_2_vqshl_typesize.get(esize)[uop]
            #print "enctype4: simdflags: %r" % simdflags

        elif enctype == 5: # VCVT
            limm = (l<<6) | imm

            if not (limm & 0b1111000):
                raise Exception("2reg_shift/enc==5 but should be decoding as oneRegModImm 0x%x" % val)

            op = a & 1
            uop = (u<<1) | op
            simdflags = (IFS_F32_S32, IFS_S32_F32, IFS_F32_U32, IFS_U32_F32)[uop]

            # fbits 
            shift_amount = 64 - imm

        elif enctype == 6:    # VQSHLU used as test
            limm = (l<<6) | imm

            op = a & 1

            if limm & 0b1000000:
                esize = 64
                shift_amount = imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = imm - 32
            elif limm & 0b0010000:
                esize = 16
                shift_amount = imm - 16
            elif limm & 0b0001000:
                esize = 8
                shift_amount = imm - 8

            #simdflags = { 8: IFS_8, 16: IFS_16, 32: IFS_32, 64: IFS_64 }[esize]
            idx = {8:0, 16:1, 32:2, 64:3}[esize]
            simdflags = adv_simd_dts[20 + (idx) + foffset]
            #print "simdflags: %r" % simdflags

        elif enctype == 7:      # VSHRN needs different simdflags...
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                shift_amount = 16-imm

            if u:
                foffset += 4

            idx = {8:1, 16:2, 32:3, 64:4}[esize]
            simdflags = adv_simd_dts[(idx) + foffset]


        opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
            ArmImmOper(shift_amount),
        )

        return opcode, mnem, opers, IF_ADV_SIMD, simdflags

    elif ((a & 0x16) < 0x16):
        a = (val >> 8) & 0xf
        sz = (val >> 20) & 0x3
        if (c & 0x5) == 0:
            # three registers of different lengths

            idx = (a<<1) | u
            mnem, opcode, flagoff, dt, nt, mt = adv_simd_3diffregs[idx]
            if mnem is None:
                raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding",
                        bytez=struct.pack('<L', val), va=va)

            op = a & 1

            d >>= dt
            n >>= nt
            m >>= mt

            base = ('d%d', 'q%d')
            dbase = base[dt]
            mbase = base[mt]
            nbase = base[nt]

            opers = (
                ArmRegOper(rctx.getRegisterIndex(dbase%d)),
                ArmRegOper(rctx.getRegisterIndex(nbase%n)),
                ArmRegOper(rctx.getRegisterIndex(mbase%m)),
            )

            szu = sz + flagoff
            simdflags = adv_simd_dts[szu]

            return opcode, mnem, opers, IF_ADV_SIMD, simdflags


        elif (c & 0x5) == 0x4:
            # two registers and a scalar
            idx = (a<<1) | u
            mnem, opcode, flagoff, dt, nt, mt = adv_simd_2regs_scalar[idx]
            if mnem is None:
                raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding",
                        bytez=struct.pack('<L', val), va=va)

            if sz == 1:
                index = m >> 3
                m &= 7
            elif sz == 2:
                index = m >> 4
                m &= 0xf
            else:
                raise envi.InvalidInstruction(mesg="%s with invalid size!" % mnem,
                        bytez=struct.pack('<L', val), va=va)

            d >>= dt
            n >>= nt
            m >>= mt

            base = ('d%d', 'q%d')
            dbase = base[dt]
            nbase = base[nt]
            mbase = base[mt]

            opers = (
                ArmRegOper(rctx.getRegisterIndex(dbase%d)),
                ArmRegOper(rctx.getRegisterIndex(nbase%n)),
                ArmRegScalarOper(rctx.getRegisterIndex(mbase%m), index),
            )

            szu = sz + flagoff
            simdflags = adv_simd_dts[szu]

            return opcode, mnem, opers, IF_ADV_SIMD, simdflags


    elif (a & 0x16) == 0x16:
        if u == 0:
            # vector extract VEXT
            mnem = 'vext'
            opcode = INS_VEXT

            imm4 = (val >> 8) & 0xf

            d >>= q
            n >>= q
            m >>= q

            opers = (
                ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                ArmRegOper(rctx.getRegisterIndex(rbase%n)),
                ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                ArmImmOper(imm4),
            )

            simdflags = IFS_8
            return opcode, mnem, opers, IF_ADV_SIMD, simdflags

        else:
            if (c & 1) == 0:
                if (b & 0x8) == 0:
                    # two registers, miscellaneous
                    a = (val>>16) & 0x3     # size
                    b = (val>>6) & 0x1f

                    idx = (a<<5) | b
                    datatup = adv_simd_2regs_misc[idx]
                    mnem, opcode, flagoff, dt, nt, mod = datatup
                    if mnem is None:
                        raise envi.InvalidInstruction(mesg="Invalid AdvSIMD Opcode Encoding",
                                bytez=struct.pack('<L', val), va=va)

                    d >>= q
                    m >>= q

                    if (a==1) and ((b&0b1100) != 0b1100):
                        opers = (
                            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                            ArmImmOper(0),
                        )
                    else:
                        opers = (
                            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
                        )

                    sz = (val>>18) & 0x3
                    szu = sz + flagoff
                    #print "2reg_misc: 0x%x  (a: 0x%x  b: 0x%x  idx: %d)" % (val, a,b,szu)
                    simdflags = adv_simd_dts[szu]

                    return opcode, mnem, opers, IF_ADV_SIMD, simdflags

                elif (b & 0xc) == 8:
                    # vector table lookup VTBL, VTBX
                    ln = (val>>8) & 3
                    op = (val>>6) & 1

                    mnem, opcode = (('vtbl', INS_VTBL),('vtbx', INS_VTBX))[op]

                    opers = (
                            ArmRegOper(rctx.getRegisterIndex('d%d'%d)),
                            ArmExtRegListOper(n, ln+1, 1),
                            ArmRegOper(rctx.getRegisterIndex('d%d'%m)),
                            )

                    simdflags = IFS_8
                    return opcode, mnem, opers, IF_ADV_SIMD, simdflags

                elif (b == 0xc):
                    # vector duplicate VDUP (scalar)
                    opcode = INS_VDUP
                    mnem = 'vdup'
                    imm4 = n

                    d >>= q

                    if imm4 & 1:
                        index = imm4 >> 1
                        simdflags = IFS_8
                    elif imm4 & 2:
                        index = imm4 >> 2
                        simdflags = IFS_16
                    elif imm4 & 4:
                        index = imm4 >> 3
                        simdflags = IFS_32
                    else:
                        raise envi.InvalidInstruction(mesg="VDUP with invalid imm4!",
                                bytez=struct.pack('<L', val), va=va)

                    opers = (
                        ArmRegOper(rctx.getRegisterIndex(rbase%d)),
                        ArmRegScalarOper(rctx.getRegisterIndex('d%d'%m), index),
                    )

                    return opcode, mnem, opers, IF_ADV_SIMD, simdflags

    return 0, 'NO VECTOR ENCODING COMPLETED', (), 0, 0


adv_2_vqshl_typesize = {
    8: ( None, IFS_S8, IFS_S8, IFS_U8),
    16: ( None, IFS_S16, IFS_S16, IFS_U16),
    32: ( None, IFS_S32, IFS_S32, IFS_U32),
    64: ( None, IFS_S64, IFS_S64, IFS_U64),
    }

# one register and modified immediate modifiers...
def adv_simd_mod_000x(abcdefgh):
    return IFS_I32, 4, abcdefgh
    #return IFS_I32, (abcdefgh << 32) | abcdefgh

def adv_simd_mod_001x(abcdefgh):
    return IFS_I32, 4, (abcdefgh << 8)
    #return IFS_I32,(abcdefgh << 40) | (abcdefgh << 8)

def adv_simd_mod_010x(abcdefgh):
    return IFS_I32, 4, (abcdefgh << 16)
    #return IFS_I32, (abcdefgh << 48) | (abcdefgh << 16)

def adv_simd_mod_011x(abcdefgh):
    return IFS_I32, 4, (abcdefgh << 24)
    #return IFS_I32, (abcdefgh << 56) | (abcdefgh << 24)

def adv_simd_mod_100x(abcdefgh):
    #print hex(abcdefgh)
    return IFS_I16, 2, abcdefgh
    #return IFS_I16, (abcdefgh << 48) | (abcdefgh << 32) | (abcdefgh << 16) | abcdefgh

def adv_simd_mod_101x(abcdefgh):
    return IFS_I16, 2, (abcdefgh << 8)
    #return IFS_I16, (abcdefgh << 56) | (abcdefgh << 40) | (abcdefgh << 24) | (abcdefgh << 8)

def adv_simd_mod_1100(abcdefgh):
    return IFS_I32, 4, (abcdefgh << 8) | 0xff
    #return IFS_I32, (abcdefgh << 40) | (abcdefgh << 8) | 0xf000f

def adv_simd_mod_1101(abcdefgh):
    return IFS_I32, 4, (abcdefgh << 16) | 0xffff
    #return IFS_I32, (abcdefgh << 48) | (abcdefgh << 16) | 0xff00ff

def adv_simd_mod_0_1110(abcdefgh):
    return IFS_I8, 1, abcdefgh
    #return IFS_I8, (abcdefgh << 48) | (abcdefgh << 32) | (abcdefgh << 16) | abcdefgh | (abcdefgh << 56) | (abcdefgh << 40) | (abcdefgh << 24) | (abcdefgh << 8)

def adv_simd_mod_0_1111(abcdefgh):
    a = (abcdefgh & 0b10000000) << 24
    b = (abcdefgh >> 6) & 1
    B = (b | (b<<1) | (b<<2) | (b<<3) | (b<<4) | ((b^1)<<5)) <<25
    cdefgh = (abcdefgh << 19) & 0x1f80000
    single = a | B | cdefgh
    #full = (single << 32) | single
    full = single
    return IFS_F32, 4, full

def adv_simd_mod_1_1110(abcdefgh):
    a = (abcdefgh >> 7) & 1
    b = (abcdefgh >> 6) & 1
    c = (abcdefgh >> 5) & 1
    d = (abcdefgh >> 4) & 1
    e = (abcdefgh >> 3) & 1
    f = (abcdefgh >> 2) & 1
    g = (abcdefgh >> 1) & 1
    h = (abcdefgh) & 1
    A = a | (a<<1) | (a<<2) | (a<<3) | (a<<4) | (a<<5) | (a<<6) | (a<<7)
    B = b | (b<<1) | (b<<2) | (b<<3) | (b<<4) | (b<<5) | (b<<6) | (b<<7)
    C = c | (c<<1) | (c<<2) | (c<<3) | (c<<4) | (c<<5) | (c<<6) | (c<<7)
    D = d | (d<<1) | (d<<2) | (d<<3) | (d<<4) | (d<<5) | (d<<6) | (d<<7)
    E = e | (e<<1) | (e<<2) | (e<<3) | (e<<4) | (e<<5) | (e<<6) | (e<<7)
    F = f | (f<<1) | (f<<2) | (f<<3) | (f<<4) | (f<<5) | (f<<6) | (f<<7)
    G = g | (g<<1) | (g<<2) | (g<<3) | (g<<4) | (g<<5) | (g<<6) | (g<<7)
    H = h | (h<<1) | (h<<2) | (h<<3) | (h<<4) | (h<<5) | (h<<6) | (h<<7)
    ALL = (A<<56) | (B<<48) | (C<<40) | (D<<32) | (E<<24) | (F<<16) | (G<<8) | H
    return IFS_I64, 8, ALL


adv_simd_modifiers = (
        adv_simd_mod_000x,
        adv_simd_mod_000x,
        adv_simd_mod_001x,
        adv_simd_mod_001x,
        adv_simd_mod_010x,
        adv_simd_mod_010x,
        adv_simd_mod_011x,
        adv_simd_mod_011x,
        adv_simd_mod_100x,
        adv_simd_mod_100x,
        adv_simd_mod_101x,
        adv_simd_mod_101x,
        adv_simd_mod_1100,
        adv_simd_mod_1101,
        adv_simd_mod_0_1110,
        adv_simd_mod_0_1111,
        adv_simd_mod_000x,
        adv_simd_mod_000x,
        adv_simd_mod_001x,
        adv_simd_mod_001x,
        adv_simd_mod_010x,
        adv_simd_mod_010x,
        adv_simd_mod_011x,
        adv_simd_mod_011x,
        adv_simd_mod_100x,
        adv_simd_mod_100x,
        adv_simd_mod_101x,
        adv_simd_mod_101x,
        adv_simd_mod_1100,
        adv_simd_mod_1101,
        adv_simd_mod_1_1110,
        None,
        None,
    )

adv_2regs_shift = (
    # 0000
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    ('vshr', INS_VSHR, 0, 0),
    # 0001
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    ('vsra', INS_VSRA, 0, 0),
    # 0010
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    ('vrshr', INS_VRSHR, 0, 0),
    # 0011
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    ('vrsra', INS_VRSRA, 0, 0),
    # 0100
    ('ERROR vsri', INS_VSRI, 1, 0),
    ('ERROR vsri', INS_VSRI, 1, 0),
    ('ERROR vsri', INS_VSRI, 1, 0),
    ('ERROR vsri', INS_VSRI, 1, 0),
    ('vsri', INS_VSRI, 1, 0),
    ('vsri', INS_VSRI, 1, 0),
    ('vsri', INS_VSRI, 1, 0),
    ('vsri', INS_VSRI, 1, 0),
    # 0101
    ('vshl', INS_VSHL, 2, 0),
    ('vshl', INS_VSHL, 2, 0),
    ('vshl', INS_VSHL, 2, 0),
    ('vshl', INS_VSHL, 2, 0),
    ('vsli', INS_VSLI, 6, 0),
    ('vsli', INS_VSLI, 6, 0),
    ('vsli', INS_VSLI, 6, 0),
    ('vsli', INS_VSLI, 6, 0),
    # 0110
    ('ERROR vqshl', INS_VQSHL, 2, 0), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2, 0), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2, 0), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2, 0), # U=0, op=0
    ('vqshlu', INS_VQSHLU, 2, 0), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2, 0), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2, 0), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2, 0), # U=1, op=0
    # 0111
    ('vqshl', INS_VQSHL, 2, 0), # U=0, op=1
    ('vqshl', INS_VQSHL, 2, 0), # U=0, op=1
    ('vqshl', INS_VQSHL, 2, 0), # U=0, op=1
    ('vqshl', INS_VQSHL, 2, 0), # U=0, op=1
    ('vqshl', INS_VQSHL, 2, 16), # U=1, op=1
    ('vqshl', INS_VQSHL, 2, 16), # U=1, op=1
    ('vqshl', INS_VQSHL, 2, 16), # U=1, op=1
    ('vqshl', INS_VQSHL, 2, 16), # U=1, op=1
    # 1000
    ('vshrn', INS_VSHRN, 3, 8),        # I16-64
    ('vshrn', INS_VSHRN, 3, 8),        # None
    ('vrshrn', INS_VRSHRN, 3, 8),      # I16-64
    ('vrshrn', INS_VRSHRN, 3, 8),      # None
    ('vqshrun', INS_VQSHRUN, 3, 0),
    ('vqshrun', INS_VQSHRUN, 3, 0),
    ('vqrshrun', INS_VQRSHRUN, 3, 0),
    ('vqrshrun', INS_VQRSHRUN, 3, 0),
    # 1001
    ('vqshrn', INS_VQSHRN, 7, 0),  # hold on, u is not specified... does it parse correctly with 3?
    (None,      None, 3, 0),  # hold on, u is not specified...
    ('vqrshrn', INS_VQRSHRN, 7, 0),  # hold on, u is not specified...
    (None,      None, 3, 0),  # hold on, u is not specified...
    ('vqshrn', INS_VQSHRN, 7, 0),  # hold on, u is not specified...
    (None,      None, 3, 0),  # hold on, u is not specified...
    ('vqrshrn', INS_VQRSHRN, 7, 0),  # hold on, u is not specified...
    (None,      None, 3, 0),  # hold on, u is not specified...
    # 1010
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4, 0),    # vmovl if imm6 ends in 0b000
    # 1011
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    # 1100
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    # 1101
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3, 0),  # hold on, u is not specified...
    # 1110
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    # 1111
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),
    ('vcvt', INS_VCVT, 5, 0),


    )

####################################################################
# Table of the parser functions
ienc_parsers_tmp = [None for x in range(IENC_MAX)]

ienc_parsers_tmp[IENC_DP_IMM_SHIFT] =  p_dp_imm_shift
ienc_parsers_tmp[IENC_MISC] =   p_misc
ienc_parsers_tmp[IENC_MISC1] =   p_misc1
ienc_parsers_tmp[IENC_EXTRA_LOAD] =   p_extra_load_store
ienc_parsers_tmp[IENC_DP_REG_SHIFT] =   p_dp_reg_shift
ienc_parsers_tmp[IENC_MULT] =   p_mult
ienc_parsers_tmp[IENC_UNDEF] =   p_undef
ienc_parsers_tmp[IENC_MOV_IMM_STAT] =   p_mov_imm_stat
ienc_parsers_tmp[IENC_DP_IMM] =   p_dp_imm
ienc_parsers_tmp[IENC_LOAD_IMM_OFF] =   p_load_imm_off
ienc_parsers_tmp[IENC_LOAD_REG_OFF] =   p_load_reg_off
ienc_parsers_tmp[IENC_ARCH_UNDEF] =   p_arch_undef
ienc_parsers_tmp[IENC_LOAD_STORE_WORD_UBYTE] =   p_load_store_word_ubyte
ienc_parsers_tmp[IENC_MEDIA] =   p_media
ienc_parsers_tmp[IENC_LOAD_MULT] =   p_load_mult
ienc_parsers_tmp[IENC_BRANCH] =   p_branch
ienc_parsers_tmp[IENC_COPROC_RREG_XFER] = p_coproc_dbl_reg_xfer
ienc_parsers_tmp[IENC_COPROC_LOAD] =   p_coproc_load
ienc_parsers_tmp[IENC_COPROC_DP] =   p_coproc_dp
ienc_parsers_tmp[IENC_COPROC_REG_XFER] =   p_coproc_reg_xfer
ienc_parsers_tmp[IENC_FP_DP] =   p_fp_dp
ienc_parsers_tmp[IENC_ADVSIMD] = adv_simd_32
ienc_parsers_tmp[IENC_SWINT] =   p_swint
ienc_parsers_tmp[IENC_UNCOND] =  p_uncond
ienc_parsers_tmp[IENC_DP_MOVT] = p_dp_movt
ienc_parsers_tmp[IENC_DP_MOVW] = p_dp_movw
ienc_parsers_tmp[IENC_VMOV_DOUBLE] = p_vmov_double
ienc_parsers_tmp[IENC_VMOV_SINGLE] = p_vmov_single
ienc_parsers_tmp[IENC_VMOV_2SINGLE] = p_vmov_2single
ienc_parsers_tmp[IENC_VSTM] = p_vstm
ienc_parsers_tmp[IENC_VSTR] = p_vstr
ienc_parsers_tmp[IENC_VPUSH] = p_vpush
ienc_parsers_tmp[IENC_VLDM] = p_vldm
ienc_parsers_tmp[IENC_VLDR] = p_vldr
ienc_parsers_tmp[IENC_VPOP] = p_vpop
ienc_parsers_tmp[IENC_VMSR] = p_vmsr
ienc_parsers_tmp[IENC_VMOV_SCALAR] = p_vmov_scalar
ienc_parsers_tmp[IENC_VDUP] = p_vdup
ienc_parsers_tmp[IENC_MCR] = p_mcr


ienc_parsers = tuple(ienc_parsers_tmp)

####################################################################

# the primary table is index'd by the 3 bits following the
# conditional and are structured as follows:
# ( ENC, nexttable )
# If ENC is not None, those 3 bits were enough for us to know the
# encoding type, otherwise move on to the second table.

# The secondary tables have the format:
# (mask, value, ENC).  If the opcode is masked with "mask"
# resulting in "value" we have found the instruction encoding.
# NOTE: All entries in these tables *must* be from most specific
# to least!

# Table for initial 3 bit == 0
s_0_table = (
    # Order is critical here...
    (0b00000001100100000000000000010000, 0b00000001000000000000000000000000, IENC_MISC),
    (0b00000000000000000000000000010000, 0b00000000000000000000000000000000, IENC_DP_IMM_SHIFT),
    (0b00000001100100000000000010010000, 0b00000001000000000000000000010000, IENC_MISC1),
    (0b00000001000000000000000011110000, 0b00000000000000000000000010010000, IENC_MULT),
    (0b00000001001000000000000010010000, 0b00000001001000000000000010010000, IENC_EXTRA_LOAD),
    (0b00000000000000000000000010010000, 0b00000000000000000000000010010000, IENC_EXTRA_LOAD),
    (0b00000000000000000000000010010000, 0b00000000000000000000000000010000, IENC_DP_REG_SHIFT),
    (0,0, IENC_UNDEF),   #catch-all
)

s_1_table = (
    (0b00001111111111110000000011110000, 0b00000011001000000000000011110000, IENC_MISC1), #dbg command
    (0b00001111101100000000000000000000, 0b00000011001000000000000000000000, IENC_MOV_IMM_STAT),
    (0b00001111111100000000000000000000, 0b00000011000000000000000000000000, IENC_DP_MOVW),
    (0b00001111111100000000000000000000, 0b00000011010000000000000000000000, IENC_DP_MOVT),
    (0b00001111101100000000000000000000, 0b00000011001000000000000000000000, IENC_DP_MSR_IMM),
    (0b00001110000000000000000000000000, 0b00000010000000000000000000000000, IENC_DP_IMM),
    (0, 0, IENC_UNDEF),
)

s_3_table = (
    (0b00000001111100000000000011110000, 0b00000001111100000000000011110000, IENC_ARCH_UNDEF),
    (0b00001110000000000000000000010000, 0b00000110000000000000000000000000, IENC_LOAD_STORE_WORD_UBYTE),
    (0b00001110000000000000000000010000, 0b00000110000000000000000000010000, IENC_MEDIA),
    (0,0, IENC_LOAD_REG_OFF),
)

s_6_table = (
    (0b00001111111000000000111111010000, 0b00001100010000000000101000010000, IENC_VMOV_2SINGLE),
    (0b00001111111000000000111111010000, 0b00001100010000000000101100010000, IENC_VMOV_DOUBLE),
    (0b00001111100100000000111000000000, 0b00001100100000000000101000000000, IENC_VSTM),
    (0b00001111101111110000111000000000, 0b00001101001011010000101000000000, IENC_VPUSH),
    (0b00001111101100000000111000000000, 0b00001101001000000000101000000000, IENC_VSTM),
    (0b00001111001100000000111000000000, 0b00001101000000000000101000000000, IENC_VSTR),
    (0b00001111100100000000111000000000, 0b00001100100100000000101000000000, IENC_VLDM),
    (0b00001111101111110000111000000000, 0b00001101001111010000101000000000, IENC_VPOP),
    (0b00001111101100000000111000000000, 0b00001101001100000000101000000000, IENC_VLDM),
    (0b00001111001100000000111000000000, 0b00001101000100000000101000000000, IENC_VLDR),
    (0b00001111111000000000000000000000, 0b00001100010000000000000000000000, IENC_COPROC_RREG_XFER),
    (0b00001110000000000000000000000000, 0b00001100000000000000000000000000, IENC_COPROC_LOAD),

)

s_7_table = (
    (0b00000001000000000000000000000000, 0b00000001000000000000000000000000, IENC_SWINT),
    (0b00001111111100000000111100010000, 0b00001110000000000000101000010000, IENC_VMOV_SINGLE),
    (0b00001111111100000000111100010000, 0b00001110111000000000101000010000, IENC_VMSR),
    (0b00001111100100000000111100010000, 0b00001110000000000000101100010000, IENC_VMOV_SCALAR),
    (0b00001111100100000000111101010000, 0b00001110100000000000101100010000, IENC_VDUP),
    (0b00001111111100000000111100010000, 0b00001110000100000000101000010000, IENC_VMOV_SINGLE),
    (0b00001111111100000000111100010000, 0b00001110111100000000101000010000, IENC_VMSR),
    (0b00001111000100000000111100010000, 0b00001110000100000000101100010000, IENC_VMOV_SCALAR),
    (0b00000001000000000000111000010000, 0b00000000000000000000101000000000, IENC_FP_DP),
    (0b00000001000000000000111000010000, 0b00000000000000000000101000010000, IENC_ADVSIMD),
    (0b00001111000000000000000000010000, 0b00001000000000000000000000000000, IENC_COPROC_REG_XFER),
    (0b00001111000000000000000000010000, 0b00001110000000000000000000010000, IENC_MCR),
    (0b00001111000000000000000000010000, 0b00001110000000000000000000000000, IENC_COPROC_DP),
)

# Initial 3 (non conditional) primary table (UNCOND handled separately)
inittable = [
    (None, s_0_table),
    (None, s_1_table),
    (IENC_LOAD_IMM_OFF, None), # Load or store an immediate
    (None, s_3_table),
    (IENC_LOAD_MULT, None),
    (IENC_BRANCH, None),
    (None, s_6_table),
    (None, s_7_table),
]

endian_names = ("le","be")

class ArmOpcode(envi.Opcode):
    _def_arch = envi.ARCH_ARMV7

    def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0, simdflags=0):
        """
        (constructor for the basic Envi Opcode object, plus simdflags)
        Arguments as follows:

        va       - The virtual address the instruction lives at (used for PC relative immediates etc...)
        opcode   - An architecture specific numerical value for the opcode
        mnem     - A humon readable mnemonic for the opcode
        prefixes - a bitmask of architecture specific instruction prefixes
        size     - The size of the opcode in bytes
        operands - A list of Operand objects for this opcode
        iflags   - A list of Envi (architecture independant) instruction flags (see IF_FOO)
        simdflags - extra set of flags to store SIMD/vector information without killing iflags

        NOTE: If you want to create an architecture spcific opcode, I'd *highly* recommend you
              just copy/paste in the following simple initial code rather than calling the parent
              constructor.  The extra
        """
        self.opcode = opcode
        self.mnem = mnem
        self.prefixes = prefixes
        self.size = size
        self.opers = operands
        self.repr = None
        self.iflags = iflags
        self.simdflags = simdflags
        self.va = va

    def __hash__(self):
        return int(hash(self.mnem) ^ (self.size << 4))

    def __len__(self):
        return int(self.size)

    def genRefOpers(self, emu=None):
        '''
        Operand generator, yielding an (oper-index, operand) tuple from this 
        Opcode... but only for operands which make sense for XREF analysis.  
        Override when architecture makes use of odd operands like the program 
        counter, which returns a real value even without an emulator.
        '''
        for oidx, o in enumerate(self.opers):
            if o.isReg() and o.reg == REG_PC:
                continue
            yield (oidx, o)

    def getBranches(self, emu=None):
        """
        Return a list of tuples.  Each tuple contains the target VA of the
        branch, and a possible set of flags showing what type of branch it is.

        See the BR_FOO types for all the supported envi branch flags....
        Example: for bva,bflags in op.getBranches():
        """
        ret = []

        # if we aren't a NOFALL instruction, add the fallthrough branch
        if not self.iflags & envi.IF_NOFALL:
            ret.append((self.va + self.size, envi.BR_FALL | self._def_arch))
            #print "getBranches: next...", hex(self.va), self.size

        flags = 0

        if self.prefixes != COND_AL:
            flags |= envi.BR_COND

        if self.iflags & (envi.IF_BRANCH | envi.IF_CALL):
            oper = self.opers[-1]

            # check for location being ODD
            operval = oper.getOperValue(self, emu)

            if self.opcode in (INS_BLX, INS_BX):
                if operval is not None and operval & 3:
                    flags |= envi.ARCH_THUMB
                    operval &= -2
                else:
                    flags |= envi.ARCH_ARMV7

            # if we don't know that it's thumb, default to "ARCH_DEFAULT"
            else:
                flags |= self._def_arch

            if self.iflags & envi.IF_CALL:
                flags |= envi.BR_PROC

            if self.opcode in (INS_TBB, INS_TBH):
                pass
                '''
                base = self.opers[0]._getOperBase(emu)
                if base is not None:
                    ret.append((base, flags | envi.BR_DEREF | envi.BR_TABLE))
                else:
                    print "0x%x:  %r      getBranches() with no emulator" % (self.va, self)
                    '''
            else:
                # actually add the branch here...
                # if we are a deref, add the DEREF
                if oper.isDeref():
                    ref = oper.getOperAddr(self, emu)
                    ret.append((ref, flags | envi.BR_DEREF))

                # if we point to a valid address, add that branch as well:
                ret.append((operval, flags))
            #print "getBranches: (0x%x) add  0x%x   %x"% (self.va, operval, flags)

        return ret

    def getOperValue(self, idx, emu=None, codeflow=False):
        oper = self.opers[idx]
        return oper.getOperValue(self, emu=emu, codeflow=codeflow)

    S_FLAG_MASK = IF_PSR_S | IF_PSR_S_SIL
    
    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        mnem = self.mnem + cond_codes.get(self.prefixes)
        daib_flags = self.iflags & IF_DAIB_MASK
        if self.iflags & IF_L:
            mnem += 'l'
        elif (self.iflags & self.S_FLAG_MASK) == IF_PSR_S:
            mnem += 's'
        elif daib_flags > 0 and (mnem != "push"):
            idx = ((daib_flags)>>(IF_DAIB_SHFT)) 
            mnem += daib[idx]
        else:
            if self.iflags & IF_S:
                mnem += 's'
            if self.iflags & IF_D:
                mnem += 'd'
            if self.iflags & IF_B:
                mnem += 'b'
            if self.iflags & IF_H:
                mnem += 'h'
            if self.iflags & IF_T: # removed el
                mnem += 't'
            if self.iflags & IF_IE:
                mnem += 'ie'
            elif self.iflags & IF_ID:
                mnem += 'id'

            if self.simdflags:
                mnem += IFS[self.simdflags]

        #FIXME: Advanced SIMD modifiers (IF_V*)
        if self.iflags & IF_THUMB32:
            mnem += ".w"

        mcanv.addNameText(mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in range(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")
        #if self.iflags & IF_W:     # handled in operand.  still keeping flag to indicate this instruction writes back
        #    mcanc.addText(" !")

    def __repr__(self):
        mnem = self.mnem + cond_codes.get(self.prefixes)
        daib_flags = self.iflags & IF_DAIB_MASK
        if self.iflags & IF_L:
            mnem += 'l'
        elif (self.iflags & self.S_FLAG_MASK) == IF_PSR_S:
            mnem += 's'
        elif (daib_flags > 0) and (mnem != "push"):
            idx = ((daib_flags) >> (IF_DAIB_SHFT))
            mnem += daib[idx]
        else:
            if self.iflags & IF_S:
                mnem += 's'
            if self.iflags & IF_D:
                mnem += 'd'
            if self.iflags & IF_B:
                mnem += 'b'
            if self.iflags & IF_H:
                mnem += 'h'
            if self.iflags & IF_T: #removed el
                mnem += 't'
            if self.iflags & IF_IE:
                mnem += 'ie'
            elif self.iflags & IF_ID:
                mnem += 'id'

            if self.simdflags:
                mnem += IFS[self.simdflags]

        if self.iflags & IF_THUMB32:
            mnem += ".w"
        x = []
        for o in self.opers:
            x.append(o.repr(self))
        #if self.iflags & IF_W:     # handled in operand.  still keeping flag to indicate this instruction writes back
        #    x[-1] += " !"      
        return mnem + " " + ", ".join(x)

class ArmOperand(envi.Operand):
    tsize = 4
    def involvesPC(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None

class ArmRegOper(ArmOperand):
    ''' register operand.  see "addressing mode 1 - data processing operands - register" '''

    def __init__(self, reg, va=0, oflags=0):
        if reg is None:
            raise envi.InvalidInstruction(mesg="None Reg Type!",
                    bytez='f00!', va=va)
        self.va = va
        self.reg = reg
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.oflags != oper.oflags:
            return False
        return True
    
    def involvesPC(self):
        return self.reg == 15

    def isReg(self):
        return True

    def getWidth(self):
        return rctx.getRegisterWidth(self.reg) / 8

    def getOperValue(self, op, emu=None, codeflow=False):
        if self.reg == REG_PC and not codeflow:
            return self.va

        if emu is None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None
        emu.setRegister(self.reg, val)

    def getFloatValue(self, emu, elmtsz=None, elmtidx=None):
        '''
        Return the Float value from an element of a FP/SIMD register.
        If elmtsz is None, uses the register width as a guide (ie. one element)
        If elmtsz is provided, elmtidx should also be provided.

        elmtsz is in *bytes*.

        we store Floats as X-bit integers and double-convert
        '''
        if elmtsz is None:
            elmtsz = self.getWidth()

        # TODO: signed?
        ifmt = e_bits.getFormat(elmtsz, big_endian=emu.getEndian()==ENDIAN_MSB)
        ffmt = e_bits.getFloatFormat(elmntsz, big_endian=emu.getEndian()==ENDIAN_MSB)

        # get the 16-/32-/64-bit integer value
        metaval = emu.getRegister(self.reg)
        if elmtidx is not None:
            shiftsz = elmtidx * elmtsz * 8
            elmtmask = e_bits.u_maxes[elmtsz]
            metaval = (metaval >> shiftsz) & elmtmask

        # convert it to the appropriate float
        metastr = struct.pack(ifmt, metaval)
        fval = struct.unpack(ffmt, metastr)

        return fval

    def setFloatValue(self, emu, val, elmtsz=None, elmtidx=None):
        '''
        Store a Float value to an element of a FP/SIMD register.
        If elmtsz is None, uses the register width as a guide (ie. one element)
        If elmtsz is provided, elmtidx should also be provided.

        we store Floats as X-bit integers and double-convert

        returns the integer value
        '''
        if elmtsz is None:
            elmtsz = self.getWidth()

        ifmt = e_bits.getFormat(emu.getEndian(), elmtsz)
        ffmt = e_bits.getFloatFormat(emu.getEndian(), elmtsz)

        # convert float to integer to store
        metastr = struct.pack(ffmt, val)
        ival = struct.unpack(ifmt, metastr)

        if elmtidx is not None:
            # get current regsiter values, mask out the part we're about to write
            regval = emu.getRegister(self.reg)
            shiftsz = elmtidx * elmtsz * 8
            mask = -1 ^ (e_bits.u_maxes[elmtsz] << shiftsz)
            regval &= mask

            # now shift the value to the right element slot and OR with regval
            ival <<= shiftsz
            regval |= ival

        emu.setRegister(self.reg, regval)
        
        return regval

    def render(self, mcanv, op, idx):
        rname = rctx.getRegisterName(self.reg)
        mcanv.addNameText(rname, typename='registers')
        if self.oflags & OF_W:
            mcanv.addText( "!" )


    def repr(self, op):
        rname = rctx.getRegisterName(self.reg)
        if self.oflags & OF_W:
            rname += "!"
        return rname

class ArmRegScalarOper(ArmRegOper):
    def __init__(self, reg, index, va=0, oflags=0):
        self.index = index
        ArmRegOper.__init__(self, reg, va, oflags)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.oflags != oper.oflags:
            return False
        if self.index != oper.index:
            return False
        return True
    
    def involvesPC(self):
        return False

    def isDeref(self):
        return True

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None

        raise Exception("Scalar Accessors Not Implemented")
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None

        raise Exception("Scalar Accessors Not Implemented")
        emu.setRegister(self.reg, val)

    def render(self, mcanv, op, idx):
        rname = rctx.getRegisterName(self.reg)
        mcanv.addNameText(rname, typename='registers')
        mcanv.addNameText('[%d]' % self.index, typename='scalars')

    def repr(self, op):
        rname = rctx.getRegisterName(self.reg)
        rname += '[%d]' % self.index
        return rname

class ArmRegShiftRegOper(ArmOperand):
    ''' register shift operand.  see "addressing mode 1 - data processing operands - * shift * by register" '''

    def __init__(self, reg, shtype, shreg):
        self.reg = reg
        self.shtype = shtype
        self.shreg = shreg

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.shtype != oper.shtype:
            return False
        if self.shreg != oper.shreg:
            return False
        return True

    def involvesPC(self):
        return self.reg == 15

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None
        return shifters[self.shtype](emu.getRegister(self.reg), emu.getRegister(self.shreg), emu=emu)

    def render(self, mcanv, op, idx):
        rname = arm_regs[self.reg]
        mcanv.addNameText(rname, typename='registers')
        mcanv.addText(', ')
        mcanv.addNameText(shift_names[self.shtype])
        mcanv.addText(' ')
        mcanv.addNameText(arm_regs[self.shreg], typename='registers')

    def repr(self, op):
        rname = "%s, %s %s" % (arm_regs[self.reg], \
                shift_names[self.shtype],arm_regs[self.shreg])
        return rname

class ArmRegShiftImmOper(ArmOperand):
    ''' register shift immediate operand.  see "addressing mode 1 - data processing operands - * shift * by immediate" '''

    def __init__(self, reg, shtype, shimm, va):
        if shimm == 0:
            if shtype == S_ROR:
                shtype = S_RRX
            elif shtype == S_LSR or shtype == S_ASR:
                shimm = 32
        self.reg = reg
        self.shtype = shtype
        self.shimm = shimm
        self.va = va

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.shtype != oper.shtype:
            return False
        if self.shimm != oper.shimm:
            return False
        return True

    def involvesPC(self):
        return self.reg == 15

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        if self.reg == REG_PC:
            return shifters[self.shtype](self.va, self.shimm, emu=emu)

        if emu is None:
            return None
        return shifters[self.shtype](emu.getRegister(self.reg), self.shimm, emu=emu)

    def render(self, mcanv, op, idx):
        rname = arm_regs[self.reg]
        mcanv.addNameText(rname, typename='registers')
        if self.shimm != 0:
            mcanv.addText(', ')
            mcanv.addNameText(shift_names[self.shtype])
            mcanv.addText(' ')
            mcanv.addNameText('#%d' % self.shimm)
        elif self.shtype == S_RRX:
            mcanv.addText(', ')
            mcanv.addNameText(shift_names[self.shtype])

    def repr(self, op):
        rname = arm_regs[self.reg]
        retval = [ rname ]
        if self.shimm != 0:
            retval.append(", "+shift_names[self.shtype])
            retval.append("#%d"%self.shimm)
        elif self.shtype == S_RRX:
            retval.append(shift_names[self.shtype])
        return " ".join(retval)

class ArmImmOper(ArmOperand):
    ''' register operand.  see "addressing mode 1 - data processing operands - immediate" '''


    def __init__(self, val, shval=0, shtype=S_ROR, va=0, size=4):
        self.val = val
        self.shval = shval
        self.shtype = shtype
        self.size = size

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False

        if self.getOperValue(None) != oper.getOperValue(None):
            return False

        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def isImmed(self):
        return True

    def isDiscrete(self):
        return True

    def getOperValue(self, op, emu=None, codeflow=False):
        return shifters[self.shtype](self.val, self.shval, self.size, emu=emu)

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addText('#')
        mcanv.addNameText('0x%.2x' % (val))

    def repr(self, op):
        val = self.getOperValue(op)
        return '#0x%.2x' % (val)

class ArmFloatOper(ArmImmOper):
    '''
    float operand (of a particular byte-width)
    internal storage as N-bit bitfield (like the architecture would)
    repr/render provides the appropriate floating point value
    '''
    def __init__(self, val, size=4, endian=envi.ENDIAN_LSB):
        self.size = size
        self.endian = endian
        self.intfmt = e_bits.fmt_chars[self.endian][self.size]
        self.floatfmt = e_bits.fmt_floats[self.endian][self.size]

        if type(val) == float:
            self.setByFloat(val)
        else:
            self.setByBitField(val)

    def setByFloat(self, val):
        val = struct.pack(self.floatfmt, val)
        self.val, = struct.unpack(self.intfmt, val)

    def setByBitField(self, val):
        self.val = val

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.val

    def getFloatValue(self, op, emu=None):
        '''
        helper function to deal with the float values (getOperValue returns a bitfield)
        '''
        bytez = struct.pack(self.intfmt, self.val)
        retval = struct.unpack(self.floatfmt, bytez)[0]
        return retval

    def render(self, mcanv, op, idx):
        val = self.getFloatValue(op)
        mcanv.addNameText('#%f' % (val))

    def repr(self, op):
        val = self.getFloatValue(op)

        return '#%f' % (val)

class ArmScaledOffsetOper(ArmOperand):
    ''' scaled offset operand.  see "addressing mode 2 - load and store word or unsigned byte - scaled register *" '''
    def __init__(self, base_reg, offset_reg, shtype, shval, va, pubwl=PUxWL_DFLT, psize=4, tsize=None):
        if shval == 0:
            if shtype == S_ROR:
                shtype = S_RRX
            elif shtype == S_LSR or shtype == S_ASR:
                shval = 32
        self.base_reg = base_reg
        self.offset_reg = offset_reg
        self.shtype = shtype
        self.shval = shval
        self.pubwl = pubwl
        self.psize = psize
        self.va = va

        if tsize is not None:
            self.tsize = tsize
        else:
            b = (self.pubwl >> 2) & 1
            self.tsize = (4,1)[b]

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset_reg != oper.offset_reg:
            return False
        if self.shtype != oper.shtype:
            return False
        if self.shval != oper.shval:
            return False
        if self.pubwl != oper.pubwl:
            return False
        if self.psize != oper.psize:
            return False
        return True

    def involvesPC(self):
        return self.base_reg == 15

    def isDeref(self):
        return True

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.readMemValue(addr, self.tsize)

    def setOperValue(self, op, emu=None, val=None):
        # can't survive without an emulator
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        emu.writeMemValue(addr, val, self.tsize)

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None

        base = self._getOperBase(emu)

        pom = (-1, 1)[(self.pubwl>>3)&1]
        addval = shifters[self.shtype](emu.getRegister(self.offset_reg), self.shval, emu=emu)
        # if U==0, subtract
        addval *= pom

        addr = (base + addval) & e_bits.u_maxes[self.psize]


        # unindexed = 0
        # offset = 0x2
        # postindexed = 0x10
        # preindexed = 0x12

        # w = write-back
        # p = indexed
        # u = add

        if (self.pubwl & 0x2 or not self.pubwl & 0x10):  # write-back if (P==0 || W==1)
            if (emu is not None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

        if (self.pubwl & 0x10 == 0): # not indexed
            return base

        return addr

    def _getOperBase(self, emu):
        if self.base_reg == REG_PC:
            return self.va

        if emu is None:
            return None

        return emu.getRegister(self.base_reg)

    def render(self, mcanv, op, idx):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg]
        offreg = arm_regs[self.offset_reg]
        shname = shift_names[self.shtype]

        mcanv.addText('[')
        mcanv.addNameText(basereg, typename='registers')
        if (idxing&0x10) == 0:  # indexing
            mcanv.addText('], ')
        else:
            mcanv.addText(', ')
        mcanv.addText(pom)
        mcanv.addNameText(offreg, typename='registers')
        mcanv.addText(' ')
        if self.shval != 0:
            mcanv.addNameText(shname)
            mcanv.addText(' ')
            mcanv.addNameText('#%d' % self.shval)
        if idxing == 0x10:      # no write-back
            mcanv.addText(']')
        elif idxing != 0:       # pre-indexing (with write-back)
            mcanv.addText(']!')

    def repr(self, op):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg]
        offreg = arm_regs[self.offset_reg]
        shname = shift_names[self.shtype]
        if self.shval != 0:
            shval = ", %s #%d"%(shname,self.shval)
        elif self.shtype == S_RRX:
            shval = shname
        else:
            shval = ""
        if (idxing&0x10) == 0:         # post-indexed
            tname = '[%s], %s%s %s' % (basereg, pom, offreg, shval)
        elif idxing == 0x10:
            tname = '[%s, %s%s %s]' % (basereg, pom, offreg, shval)
        else:               # pre-indexed
            tname = '[%s, %s%s %s]!' % (basereg, pom, offreg, shval)
        return tname

class ArmRegOffsetOper(ArmOperand):
    ''' register offset operand.  see "addressing mode 2 - load and store word or unsigned byte - register *" 
    dereference address mode using the combination of two register values '''
    def __init__(self, base_reg, offset_reg, va, pubwl=PUxWL_DFLT, psize=4, tsize=None):
        self.base_reg = base_reg
        self.offset_reg = offset_reg
        self.pubwl = pubwl
        self.psize = psize

        if tsize is None:
            b = (self.pubwl >> 2) & 1
            self.tsize = (4,1)[b]
        else:
            self.tsize = tsize

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset_reg != oper.offset_reg:
            return False
        if self.pubwl != oper.pubwl:
            return False
        if self.psize != oper.psize:
            return False
        return True

    def involvesPC(self):
        return self.base_reg == 15

    def isDeref(self):
        return True

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.readMemValue(addr, self.tsize)

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None

        pom = (-1, 1)[(self.pubwl>>3)&1]
        base = emu.getRegister( self.base_reg )
        rm = emu.getRegister( self.offset_reg )

        addr = base + (pom*rm) & e_bits.u_maxes[self.psize]

        if (self.pubwl & 0x2 or not self.pubwl & 0x10):  # write-back if (P==0 || W==1)
            if (emu is not None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

        if (self.pubwl & 0x10 == 0): # not indexed
            return base

        return addr

    def render(self, mcanv, op, idx):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = rctx.getRegisterName(self.base_reg)
        offreg = rctx.getRegisterName(self.offset_reg)

        mcanv.addText('[')
        mcanv.addNameText(basereg, typename='registers')
        if (idxing&0x10) == 0:
            mcanv.addText('] ')
        else:
            mcanv.addText(', ')
        mcanv.addText(pom)
        mcanv.addNameText(offreg, typename='registers')
        if idxing == 0x10:
            mcanv.addText(']')
        elif idxing&0x10 != 0:
            mcanv.addText(']!')

    def repr(self, op):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = rctx.getRegisterName(self.base_reg)
        offreg = rctx.getRegisterName(self.offset_reg)
        if (idxing&0x10) == 0:         # post-indexed
            tname = '[%s], %s%s' % (basereg, pom, offreg)
        elif idxing == 0x10:  # offset addressing, not updated
            tname = '[%s, %s%s]' % (basereg, pom, offreg)
        else:               # pre-indexed
            tname = '[%s, %s%s]!' % (basereg, pom, offreg)
        return tname

class ArmImmOffsetOper(ArmOperand):
    ''' immediate offset operand.  see "addressing mode 2 - load and store word or unsigned byte - immediate *" 

    [ base_reg, offset ]

    possibly with indexing, pre/post for faster rolling through arrays and such
    if the base_reg is PC, we'll dig in and hopefully grab the data being referenced.
    '''
    def __init__(self, base_reg, offset, va, pubwl=PUxWL_DFLT, psize=4, tsize=None):
        '''
        psize is pointer-size, since we want to increment base_reg that size when indexing
        tsize is the target size (4 or 1 bytes)
        '''
        self.base_reg = base_reg
        self.offset = offset
        self.pubwl = pubwl
        self.psize = psize
        self.va = va

        if tsize is None:
            b = (pubwl >> 2) & 1
            self.tsize = (4,1)[b]
        else:
            self.tsize = tsize

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset != oper.offset:
            return False
        if self.pubwl != oper.pubwl:
            return False
        if self.psize != oper.psize:
            return False
        return True

    def involvesPC(self):
        return self.base_reg == REG_PC

    def isDeref(self):
        return True

    def setOperValue(self, op, emu=None, val=None):
        # can't survive without an emulator
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)
        val &= e_bits.u_maxes[self.tsize]

        emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None, codeflow=False):
        # can't survive without an emulator
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)

        ret = emu.readMemValue(addr, self.tsize)
        return ret

    def getOperAddr(self, op, emu=None):
        # there are certain circumstances where we can survive without an emulator
        # if we don't have an emulator, we must be PC-based since we know it
        if self.base_reg == REG_PC:
            base = self.va
        elif emu is None:
            return None
        else:
            base = emu.getRegister(self.base_reg)

        pubwl = self.pubwl >> 3
        u = pubwl & 1
        if u:
            addr = (base + self.offset) & e_bits.u_maxes[self.psize]
        else:
            addr = (base - self.offset) & e_bits.u_maxes[self.psize]


        if (self.pubwl & 0x2 or not self.pubwl & 0x10):  # write-back if (P==0 || W==1)
            if (emu is not None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

        if (self.pubwl & 0x10 == 0): # not indexed
            return base

        return addr

    def render(self, mcanv, op, idx):
        u = (self.pubwl>>3)&1
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg]
        if self.base_reg == REG_PC:

            mcanv.addText('[')

            addr = self.getOperAddr(op, mcanv.mem)    # only works without an emulator because we've already verified base_reg is PC

            if mcanv.mem.isValidPointer(addr):
                name = addrToName(mcanv, addr)
                mcanv.addVaText(name, addr)
            else:
                mcanv.addVaText('#0x%.8x' % addr, addr)
            mcanv.addText(']')

            value = self.getOperValue(op, mcanv.mem)
            if value is not None:
                mcanv.addText("\t; ")
                if mcanv.mem.isValidPointer(value):
                    name = addrToName(mcanv, value)
                    mcanv.addVaText(name, value)
                else:
                    mcanv.addNameText("0x%x" % value)

        else:
            pom = ('-','')[u]
            mcanv.addText('[')
            mcanv.addNameText(basereg, typename='registers')
            if self.offset == 0:
                mcanv.addText(']')

            else:
                if (idxing&0x10) == 0:
                    mcanv.addText(']')

                mcanv.addText(', #%s' % (pom))
                mcanv.addNameText('0x%x' % (self.offset))

                if idxing == 0x10:
                    mcanv.addText(']')
                elif idxing &0x10 != 0:
                    mcanv.addText(']!')

    def repr(self, op):
        u = (self.pubwl>>3)&1
        idxing = (self.pubwl) & 0x12
        basereg = arm_regs[self.base_reg]
        if self.base_reg == REG_PC:
            addr = self.getOperAddr(op)    # only works without an emulator because we've already verified base_reg is PC
            tname = "[#0x%x]" % addr

        else:
            pom = ('-','')[u]
            if self.offset != 0:
                offset = ", #%s0x%x"%(pom,self.offset)
            else:
                offset = ""
                
            if (idxing&0x10) == 0:         # post-indexed
                tname = '[%s]%s' % (basereg, offset)
            else:
                if idxing == 0x10:  # offset addressing, not updated
                    tname = '[%s%s]' % (basereg,offset)
                else:               # pre-indexed
                    tname = '[%s%s]!' % (basereg,offset)
        return tname

class ArmPcOffsetOper(ArmOperand):
    '''
    PC + imm_offset

    ArmImmOper but for Branches, not a dereference.  perhaps we can have ArmImmOper do all the things... but for now we have this.
    '''
    def __init__(self, val, va):
        self.val = val # depending on mode, this is reg/imm
        self.va = va

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.va != oper.va:
            return False
        return True

    def involvesPC(self):
        return True

    def isImmed(self):
        return True

    def isDeref(self):
        return False

    def isDiscrete(self):
        return True

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.va + self.val

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        va = value & -2
        if mcanv.mem.isValidPointer(va):
            name = addrToName(mcanv, va)
            mcanv.addVaText(name, va)
        else:
            mcanv.addVaText('0x%.8x' % va, va)

    def repr(self, op):
        targ = self.getOperValue(op)
        tname = "0x%.8x" % targ
        return tname


psrs = ("CPSR", "SPSR", 'APSR', 'inval', 'inval', 'inval', 'inval', 'inval',)
fields = (None, 'c', 'x', 'cx', 's', 'cs', 'xs', 'cxs',  'f', 'fc', 'fx', 'fcx', 'fs', 'fcs', 'fxs', 'fcxs')

class ArmPgmStatRegOper(ArmOperand):
    def __init__(self, r, val=0, mask=0xffffffff):
        self.mask = mask
        self.val = val
        self.psr = r

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.r != oper.r:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None

        mode = emu.getProcMode()
        if self.psr == PSR_SPSR: # SPSR
            psr = emu.getSPSR(mode)
        else:
            psr = emu.getCPSR()

        return psr

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None
        mode = emu.getProcMode()
        #SPSR does not work - fails in emu.getSPSR
        if self.psr == PSR_SPSR:    # SPSR
            psr = emu.getSPSR(mode)
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setSPSR(mode, newpsr)

        else:           # CPSR (APSR is an alias for CPSR)
            psr = emu.getCPSR()
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setCPSR(newpsr)

        return newpsr

    def render(self, mcanv, op, idx):
        field = fields[self.val]
        if field is not None:
            psrstr = psrs[self.psr] + '_' + fields[self.val]
        else:
            psrstr = psrs[self.psr]

        mcanv.addNameText(psrstr, typename='registers')

    def repr(self, op):
        field = fields[self.val]
        if field is not None:
            return psrs[self.psr] + '_' + fields[self.val]
        return psrs[self.psr]

    
class ArmEndianOper(ArmImmOper):
    def repr(self, op):
        return endian_names[self.val]

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.val

class ArmRegListOper(ArmOperand):
    def __init__(self, val, oflags=0):
        self.val = val
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def involvesPC(self):
        return self.val & 0x8000 == 0x8000

    def render(self, mcanv, op, idx):
        mcanv.addText('{')
        regs = [arm_regs[l] for l in range(16) if (self.val & (1<<l))]
        for regidx in range(len(regs) - 1):
            reg = regs[regidx]
            mcanv.addNameText(reg, typename='registers')
            mcanv.addText(', ')
        mcanv.addNameText(regs[-1], typename='registers')
        mcanv.addText('}')
        if self.oflags & OF_UM:
            mcanv.addText('^')

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None
        reglist = []
        for regidx in range(16):
            #FIXME: check processor mode (abort, system, user, etc... use banked registers?)
            if self.val & (1<<regidx):
                reg = emu.getRegister(regidx)
                reglist.append(reg)
        return reglist

    def repr(self, op):
            s = [ "{" ]
            regs = [arm_regs[l] for l in range(16) if (self.val & (1<<l))]
            s.append(', '.join(regs))
            s.append('}')
            if self.oflags & OF_UM:
                s.append('^')
            return "".join(s)
    
class ArmExtRegListOper(ArmOperand):
    '''
    extended register list: Vector/FP registers
    '''
    def __init__(self, firstreg, count, size, inc=1):
        self.firstreg = firstreg
        self.count = count
        self.size = size    # 0 or 1, meaning 32bit or 64bit
        self.inc = inc

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.firstreg != oper.firstreg:
            return False
        if self.count != oper.count:
            return False
        if self.size != oper.size:
            return False
        if self.inc != oper.inc:
            return False
        return True

    def isDeref(self):
        return False

    def render(self, mcanv, op, idx):
        regbase = ("s%d", "d%d")[self.size]
        mcanv.addText('{')
        top = self.count-1
        for l in range(0, self.count, self.inc):
            vreg = self.firstreg + l
            mcanv.addNameText(regbase % vreg, typename='registers')
            if l < top:
                mcanv.addText(', ')

        mcanv.addText('}')

    def getOperValue(self, op, emu=None, codeflow=False):
        '''
        Returns a list of the values in the targeted Extension Registers
        '''
        if emu is None:
            return None
        reglist = []
        for regidx in range(self.firstreg, self.firstreg + self.count):
            reg = emu.getRegister(REGS_VECTOR_TABLE_IDX + regidx)
            reglist.append(reg)
        return reglist

    def setOperValue(self, op, vals, emu=None):
        '''
        Takes a list of values and places them in the targeted Extension Registers
        '''
        if emu is None:
            return None
        
        base = REGS_VECTOR_TABLE_IDX + self.firstreg
        for vidx in range(len(vals)):
            emu.setRegister(base + vidx, vals[vidx])

    def repr(self, op):
        regbase = ("s%d", "d%d")[self.size]
        s = [ "{" ]
        top = self.count - 1

        for l in range(self.count):
            vreg = self.firstreg + l
            s.append(regbase % vreg)
            if l < top:
                s.append(', ')

        s.append('}')
        return "".join(s)

    def getRegCount(self):
        return self.count

    def getRegSize(self):
        return (4, 8)[self.size]
    
aif_flags = (None, 'f','i','if','a','af','ai','aif')
class ArmPSRFlagsOper(ArmOperand):
    def __init__(self, flags):
        self.flags = flags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.flags != oper.flags:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None
        raise Exception("FIXME: Implement ArmPSRFlagsOper.getOperValue() (does it want to be a bitmask? or the actual value according to the PSR?)")
        return None # FIXME

    def repr(self, op):
        return aif_flags[self.flags]

    def render(self, mcanv, op, idx):
        mcanv.addNameText(aif_flags[self.flags], typename='flags')

class ArmCoprocOpcodeOper(ArmOperand):
    def __init__(self, val):
        self.val = val
        
    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.val

    def repr(self, op):
        return "%d"%self.val

    def render(self, mcanv, op, idx):
        mcanv.addNameText('%d' % self.val, typename='coprocreg')

class ArmCoprocOper(ArmOperand):
    def __init__(self, val):
        self.val = val
        
    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.val

    def repr(self, op):
        return "p%d"%self.val

    def render(self, mcanv, op, idx):
        mcanv.addNameText('p%d' % self.val, typename='coproc')

class ArmCoprocRegOper(ArmOperand):
    def __init__(self, val, shtype=None, shval=None):
        self.val = val # depending on mode, this is reg/imm
        self.shval = shval
        self.shtype = shtype

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.shval != oper.shval:
            return False
        if self.shtype != oper.shtype:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        if emu is None:
            return None
        raise Exception("FIXME: Implement ArmCoprocRegOper.getOperValue()")
        return None # FIXME

    def repr(self, op):
        return "cr%d"%self.val

    def render(self, mcanv, op, idx):
        mcanv.addNameText('cr%d' % self.val, typename='coprocreg')

class ArmCoprocOption(ArmImmOffsetOper):
    def __init__(self, base_reg, offset, va, pubwl=8):
        ArmImmOffsetOper.__init__(self, base_reg, offset, va, pubwl)
        self.base_reg = base_reg
        self.offset = offset
        self.pubwl = pubwl
        self.va = va
        b = (pubwl >> 2) & 1
        self.tsize = (4,1)[b]

    def render(self, mcanv, op, idx):
        basereg = arm_regs[self.base_reg]
        mcanv.addText('[')
        mcanv.addNameText(basereg, typename='registers')
        mcanv.addText('], {%s}' % self.offset)

    def repr(self, op):
        return '[%s], {%s}' % (arm_regs[self.base_reg],self.offset)

class ArmModeOper(ArmOperand):
    def __init__(self, mode, update=False):
        self.mode = mode
        self.update = update

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.mode != oper.mode:
            return False
        if self.update != oper.update:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        return None

    def repr(self, op):
        return proc_modes[0x10 | self.mode][PM_SNAME]

    def render(self, mcanv, op, idx):
        mcanv.addNameText(proc_modes[0x10 | self.mode][PM_SNAME], typename='mode')

class ArmDbgHintOption(ArmOperand):
    def __init__(self, option):
        self.val = option

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None, codeflow=False):
        return self.val

    def repr(self, op):
        return "#%d"%self.val

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addText('#')
        mcanv.addNameText('0x%.2x' % (val))


class ArmBarrierOption(ArmOperand):
    options = ("","","oshst","osh","","","nshst","nsh","","","ishst","ish","","","st","sy")
    def __init__(self, option):
        self.option = option

    def retOption(self):
        return self.options[self.option]

    def repr(self, op):
        return self.retOption()

    def render(self, mcanv, op, idx):
        mcanv.addText(self.retOption())

    def getOperValue(self, idx, emu=None, codeflow=False):
        return None
        
class ArmCPSFlagsOper(ArmOperand):
    def __init__(self, flags):
        self.flags = flags

    def repr(self, op):
        flags = [AIF_FLAGS[x] for x in range(3) if self.flags & (1<<x)]
        return ','.join(flags)

    def render(self, mcanv, op, idx):
        flags = [AIF_FLAGS[x] for x in range(3) if self.flags & (1<<x)]
        mcanv.addNameText(','.join(flags), typename='cpsflags')

    def getOperValue(self, idx, emu=None, codeflow=False):
        return None
        

AIF_FLAGS = ('a','i','f')[::-1]

class ArmDisasm:
    _optype = envi.ARCH_ARMV7
    _opclass = ArmOpcode
    fmt = None
    #This holds the current running Arm instruction version and mask
    _archVersionMask = ARCH_REVS['ARMv7A']

    def __init__(self, endian=envi.ENDIAN_LSB, mask = 'ARMv7A'):
        self.setArchMask(mask)
        self.setEndian(endian)

    def setArchMask(self, key = 'ARMv7R'):
        ''' 
        set arch version mask 
        '''
        self._archVersionMask = ARCH_REVS.get(key,0)

    def getArchMask(self):
        ''' 
        set arch version mask 
        '''
        return self._archVersionMask

    def setEndian(self, endian):
        '''
        set endianness for the architecture.
        ENDIAN_LSB and ENDIAN_MSB are appropriate arguments
        '''
        self.endian = endian
        self.fmt = ("<I", ">I")[endian]

    def getEndian(self):
        '''
        get endianness for the architecture.
        ENDIAN_LSB and ENDIAN_MSB are appropriate return values
        '''
        return self.endian

    def disasm(self, bytez, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        opbytes = bytez[offset:offset+4]
        opval, = struct.unpack(self.fmt, opbytes)

        cond = opval >> 28

        #Get opcode, base mnem, operator list and flags
        opcode, mnem, olist, flags, simdflags = self.doDecode(va, opval, bytez, offset)
        if mnem is None or type(mnem) == int:
            raise Exception("mnem == %r!  0x%x" % (mnem, opval))

        # Ok...  if we're a non-conditional branch, *or* we manipulate PC unconditionally,
        # lets call ourself envi.IF_NOFALL
        if cond == COND_AL:                             # FIXME: this could backfire if COND_EXTENDED...
            if opcode in (INS_B, INS_BX):
                flags |= envi.IF_NOFALL

            elif (  len(olist) and 
                    isinstance(olist[0], ArmRegOper) and
                    olist[0].involvesPC() and 
                    (opcode & 0xffff) not in no_update_Rd ):       # FIXME: only want IF_NOFALL if it *writes* to PC!
                
                flags |= envi.IF_NOFALL

        else:
            flags |= envi.IF_COND

        # FIXME conditionals are currently plumbed as "prefixes".  Perhaps normalize to that...
        if not (flags & envi.ARCH_MASK):
            flags |= self._optype

        op = ArmOpcode(va, opcode, mnem, cond, 4, olist, flags, simdflags)
        return op
        
    def doDecode(self, va, opval, bytez, offset):
        '''
        Actually do the parsing.  This function uses opval for all parsing.
        '''
        cond = opval >> 28

        # Begin the table lookup sequence with the first 3 non-cond bits
        encfam = (opval >> 25) & 0x7
        #print "encode family = %s  (0x%x)" % (encfam, opval)
        if cond == COND_EXTENDED:
            enc = IENC_UNCOND

        else:
            enc,nexttab = inittable[encfam]
            if nexttab is not None: # we have to sub-parse...
                for mask,val,penc in nexttab:
                    #print "penc", penc
                    if (opval & mask) == val:
                        enc = penc
                        break

        # If we don't know the encoding by here, we never will ;)
        if enc is None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        #print "ienc_parser index, routine: %d, %s" % (enc, ienc_parsers[enc])
        opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
        return opcode, mnem, olist, flags, simdflags


if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( ArmDisasm() )
