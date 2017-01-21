import sys
import struct
import traceback

import envi
import envi.bits as e_bits

from envi.bits import binary

#import sys
#import struct
#import traceback

#import envi
#import envi.bits as e_bits
#from envi.bits import binary

from envi.archs.arm.const import *
from envi.archs.arm.regs import *

# FIXME: TODO
# FIXME:   codeflow currently misses all switchcases
# FIXME:   codeflow needs to identify the following pattern as a call with fallthrough
#          (currently identifying the xref and making the fallthrough into a function):
#           mov lr, pc
#           sub pc, <blah>

# FIXME ldm sp, { pc } seems to not get marked NOFALL
# FIXME ldm sp, { pc } should probably be marked IF_RET too...
# FIXME b lr / bx lr should be marked IF_RET as well!
# FIXME some arm opcode values are ENC << and some are ENC and some are etc..
#       (make all be ENC_FOO << 16 + <their index>

# FIXME the following things dont decode correctly
# 5346544e    cmppl   r6, #1308622848

#
# Possible future extensions: 
#   * VectorPointFloat subsystem (coproc 10+11)
#   * Debug subsystem (coproc 14)
#   * other 'default' coprocs we can handle and add value?

def chopmul(opcode):
    op1 = (opcode >> 20) & 0xff
    a = (opcode >> 16) & 0xf
    b = (opcode >> 12) & 0xf
    c = (opcode >> 8)  & 0xf
    d = (opcode >> 4)  & 0xf
    e = opcode & 0xf
    return (op1<<4)+d,(a,b,c,d,e)

# FIXME this seems to be universal...
def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym != None:
        return repr(sym)
    return "0x%.8x" % va

# The keys in this table are made of the
# concat of bits 27-21 and 7-4 (only when
# ienc == mul!
iencmul_codes = {
    # Basic multiplication opcodes
    binary("000000001001"): ("mul",(0,4,2), 0),
    binary("000000011001"): ("mul",(0,4,2), IF_PSR_S),
    binary("000000101001"): ("mla",(0,4,2,1), 0),
    binary("000000111001"): ("mla",(0,4,2,1), IF_PSR_S),
    binary("000001001001"): ("umaal",(1,0,4,2), 0),
    binary("000010001001"): ("umull",(1,0,4,2), 0),
    binary("000010011001"): ("umull",(1,0,4,2), IF_PSR_S),
    binary("000010101001"): ("umlal",(1,0,4,2), 0),
    binary("000010111001"): ("umlal",(1,0,4,2), IF_PSR_S),
    binary("000011001001"): ("smull",(1,0,4,2), 0),
    binary("000011011001"): ("smull",(1,0,4,2), IF_PSR_S),
    binary("000011101001"): ("smlal",(1,0,4,2), 0),
    binary("000011111001"): ("smlal",(1,0,4,2), IF_PSR_S),

    # multiplys with <x><y>
    # "B"
    binary("000100001000"): ("smlabb", (0,4,2,1), 0),
    binary("000100001010"): ("smlatb", (0,4,2,1), 0),
    binary("000100001100"): ("smlabt", (0,4,2,1), 0),
    binary("000100001110"): ("smlatt", (0,4,2,1), 0),
    binary("000100101010"): ("smulwb", (0,4,2), 0),
    binary("000100101110"): ("smulwt", (0,4,2), 0),
    binary("000100101000"): ("smlawb", (0,4,2), 0),
    binary("000100101100"): ("smlawt", (0,4,2), 0),
    binary("000101001000"): ("smlalbb", (1,0,4,2), 0),
    binary("000101001010"): ("smlaltb", (1,0,4,2), 0),
    binary("000101001100"): ("smlalbt", (1,0,4,2), 0),
    binary("000101001110"): ("smlaltt", (1,0,4,2), 0),
    binary("000101101000"): ("smulbb", (0,4,2), 0),
    binary("000101101010"): ("smultb", (0,4,2), 0),
    binary("000101101100"): ("smulbt", (0,4,2), 0),
    binary("000101101110"): ("smultt", (0,4,2), 0),

    # type 2 multiplys

    binary("011100000001"): ("smuad", (0,4,2), 0),
    binary("011100000011"): ("smuadx", (0,4,2), 0),
    binary("011100000101"): ("smusd", (0,4,2), 0),
    binary("011100000111"): ("smusdx", (0,4,2), 0),
    binary("011100000001"): ("smlad", (0,4,2,1), 0),
    binary("011100000011"): ("smladx", (0,4,2,1), 0),
    binary("011100000101"): ("smlsd", (0,4,2,1), 0),
    binary("011100000111"): ("smlsdx", (0,4,2,1), 0),
    binary("011101000001"): ("smlald", (1,0,4,2), 0),
    binary("011101000011"): ("smlaldx", (1,0,4,2), 0),
    binary("011101000101"): ("smlsld", (1,0,4,2), 0),
    binary("011101000111"): ("smlsldx", (1,0,4,2), 0),
    binary("011101010001"): ("smmla", (0,4,2,1), 0),
    binary("011101010011"): ("smmlar", (0,4,2,1), 0),
    binary("011101011101"): ("smmls", (0,4,2,1), 0),
    binary("011101011111"): ("smmlsr", (0,4,2,1), 0),
    #note for next two must check that Ra = 1111 otherwise is smmla
    #hard coding values until find better solution
    #binary("011101010001"): ("smmul", (0,4,2), 0),
    #binary("011101010011"): ("smmulr", (0,4,2), 0),
}

def sh_lsl(num, shval):
    return (num&0xffffffff) << shval

def sh_lsr(num, shval):
    return (num&0xffffffff) >> shval

def sh_asr(num, shval):
    return num >> shval

def sh_ror(num, shval):
    return (((num&0xffffffff) >> shval) | (num<< (32-shval))) & 0xffffffff

def sh_rrx(num, shval, emu=None):
    half1 = (num&0xffffffff) >> shval
    half2 = num<<(33-shval)
    newC = (num>>(shval-1)) & 1
    if emu != None:
        flags = emu.getFlags()
        oldC = (flags>>PSR_C) & 1
        emu.setFlags(flags & PSR_C_mask | newC)     #part of the change
    else:
        oldC = 0        # FIXME: 
    retval = (half1 | half2 | (oldC << (32-shval))) & 0xffffffff
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
dp_mnem = ("and","eor","sub","rsb","add","adc","sbc","rsc","tst","teq","cmp","cmn","orr","mov","bic","mvn",
        "adr")  # added
dp_shift_mnem = (
    "lsl",
    "lsr",
    "asr",
    "ror",
    "rrx"
)

# FIXME: THIS IS FUGLY but sadly it works
dp_noRn = (13,15)
dp_noRd = (8,9,10,11)
dp_silS = (8,9,10,11)

# FIXME: dp_MOV was supposed to be a tuple of opcodes that could be converted to MOV's if offset from PC.
# somehow this list has vanished into the ether.  add seems like the right one here.
dp_ADR = (2, 4,)


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
    if (shtype==3) & (shval ==0): # is it an rrx?
        shtype = 4
    mnem = dp_mnem[ocode]
    if ocode in dp_noRn:# FIXME: FUGLY (and slow...)
        #is it a mov? Only if shval is a 0, type is lsl, and ocode = 13
        if  (ocode == 13) and ((shval != 0) or (shtype != 0)):
            mnem = dp_shift_mnem[shtype]
            if shtype!= 4: #if not rrx
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
    opcode = (IENC_DP_IMM_SHIFT << 16) + ocode
    if sflag > 0:
        # IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
        if ocode in dp_silS:
            iflags = IF_PSR_S | IF_PSR_S_SIL
        else:
            iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, mnem, olist, iflags, 0)

# specialized mnemonics for p_misc
qop_mnem = ('qadd','qsub','qdadd','qdsub') # used in misc1
smla_mnem = ('smlabb','smlatb','smlabt','smlatt',)
smlal_mnem = ('smlalbb','smlaltb','smlalbt','smlaltt',)
smul_mnem = ('smulbb','smultb','smulbt','smultt',)
smlaw_mnem = ('smlawb','smlawt',)
smulw_mnem = ('smulwb','smulwt',)

def p_misc(opval, va):  
    # 0x0f900000 = 0x01000000 or 0x01000010 (misc and misc1 are both parsed at the same time.  see the footnote [2] on dp instructions in the Atmel AT91SAM7 docs

    #Including SBO and SBZ - rearranged for most exclusive to least
    #updated reference names to match v7 reference ie Rm Rn Rd Rs m n etc
    
    #if opval & 0x0ff000f0 == 0x01200020:
    if opval & 0x0FFFFFF0 == 0x012FFF20:  
        opcode = (IENC_MISC << 16) + 5
        mnem = 'bxj'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        
    #elif opval & 0x0fb002f0 == 0x01200000:
    elif opval & 0x0DB0F000 == 0x0120F000:
        opcode = (IENC_MISC << 16) + 2
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
        opcode = (IENC_MISC << 16) + 9
        mn = (opval>>5)&3
        mnem = smla_mnem[mn]
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
        opcode = (IENC_MISC << 16) + 10
        m = (opval>>6)&1
        mnem = smlaw_mnem[m]
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
        opcode = (IENC_MISC << 16) + 11
        m = (opval>>6)&1
        mnem = smulw_mnem[m]
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
        opcode = (IENC_MISC << 16) + 12
        mn = (opval>>5)&3
        mnem = smlal_mnem[mn]
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
        opcode = (IENC_MISC << 16) + 13
        mn = (opval>>5)&3
        mnem = smul_mnem[mn]
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
        opcode = (IENC_MISC << 16) + 1
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


#### these actually belong to the media section, and already exist there. FIXME: DELETE
#misc1_mnem = ("pkhbt", "pkhtb", "rev", "rev16", "revsh", "sel", "ssat", "ssat16", "usat", "usat16", )

def p_misc1(opval, va): # 
    #R = (opval>>22) & 1
    #Rn = (opval>>16) & 0xf
    #Rd = (opval>>12) & 0xf
    #rot_imm = (opval>>8) & 0xf
    #imm = opval & 0xff
    #Rm = opval & 0xf
    iflags = 0

    if opval & 0x0ff000f0 == 0x01200010:
        opcode = INS_BX
        mnem = 'bx'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        if Rm == REG_LR:
            iflags |= envi.IF_RET
        
    elif opval & 0x0ff000f0 == 0x01600010:  
        opcode = (IENC_MISC << 16) + 4
        mnem = 'clz'
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )
    elif opval & 0x0ff000f0 == 0x01200030:
        #opcode = (IENC_MISC << 16) + 6
        opcode = INS_BLX
        mnem = 'blx'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        iflags |= envi.IF_CALL
        
    elif opval & 0x0f9000f0 == 0x01000050:  #all qadd/qsub's
        opcode = (IENC_MISC << 16) + 7
        qop = (opval>>21)&3
        mnem = qop_mnem[qop]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rn, va=va),
        )
        
    elif opval & 0x0ff000f0 == 0x01200070:
        opcode = (IENC_MISC << 16) + 8
        mnem = 'bkpt'
        immed = ((opval>>4)&0xfff0) + (opval&0xf)
        olist = ( ArmImmOper(immed), )
    elif opval & 0xfff00f0 == 0x32000f0:
        opcode = (IENC_MISC << 16) + 8 #FIXME - Done in CM.4
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
swap_mnem = ("swp","swpb",)
#strex_mnem = ("strex","ldrex",)  # actual full instructions - keeping in case was mistake
strex_mnem = ("strex","ldrex","","d","b","h")  # full instruction then suffix - missed in merge?
strh_mnem = (("str",IF_H,2),("ldr",IF_H,2),)          # IF_H
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
    tvariant = bool ((pubwl & 0x12)==2)
    if opval&0x0fb000f0==0x01000090:# swp/swpb
        idx = (pubwl>>2)&1
        opcode = (IENC_EXTRA_LOAD << 16) + idx
        mnem = swap_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmImmOffsetOper(Rn, 0, va, pubwl, psize=psize),
        )
    elif opval&0x0f800ff0==0x01800f90:# strex/ldrex
        idx = pubwl&1
        opcode = (IENC_EXTRA_LOAD << 16) + 2 + idx
        itype = (opval >> 21) & 3
        mnem = strex_mnem[idx]+strex_mnem[2+itype]
        if (idx==0) & (itype !=1): #strex has 1 more entry than ldrex
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
        opcode = (IENC_EXTRA_LOAD << 16) + 4 + idx
        mnem,iflags,tsize = strh_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize, force_tsize=2),
        )
    elif opval&0x0e4000f0==0x004000b0:# strh/ldrh immoffset
        idx = pubwl&1
        opcode = (IENC_EXTRA_LOAD << 16) + 6 + idx
        mnem,iflags,tsize= strh_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn,(Rs<<4)+Rm, va, pubwl, psize=psize),
        )
    elif opval&0x0e5000d0==0x005000d0:# ldrsh/b immoffset
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 8 + idx
        mnem,iflags,tsize = ldrs_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl, psize=psize),
        )
    elif opval&0x0e5000d0==0x001000d0:# ldrsh/b regoffset
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 10 + idx
        mnem,iflags,tsize = ldrs_mnem[idx]
        if tvariant:
            iflags |= IF_T
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize, force_tsize=tsize),
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
        opcode = (IENC_EXTRA_LOAD << 16) + 12 + idx
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rd+1, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl, psize=psize),
        )
    elif opval&0x0e5000d0==0x004000d0:# ldrd/strd immoffset
        if (Rd == 14) or (Rd % 2 != 0):
            raise envi.InvalidInstruction(
                mesg="extra_load_store: invalid Rt argument",
                bytez=struct.pack("<I", opval), va=va)
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 14 + idx
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rd+1, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl, psize=psize),
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
    
    opcode = (IENC_LOAD_STORE_WORD_UBYTE << 16)
    return (opcode, ldr_mnem[pubwl&1], olist, iflags, 0)

def p_dp_reg_shift(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    Rm = opval & 0xf
    shtype = (opval >> 5) & 0x3
    Rs = (opval >> 8) & 0xf
    mnem = dp_mnem[ocode]
    if ocode in dp_noRn:# FIXME: FUGLY
        #no register shift displayed with mov
        if  (ocode == 13):
            mnem = dp_shift_mnem[shtype]
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

    opcode = (IENC_DP_REG_SHIFT << 16) + ocode
    if sflag > 0:
        # IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
        if ocode in dp_silS:
            iflags = IF_PSR_S | IF_PSR_S_SIL
        else:
            iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, mnem, olist, iflags, 0)

multfail = (None, None, None,)

iencmul_r15_codes = {
    # Basic multiplication opcodes
    binary("011101010001"): ("smmul", (0,4,2), 0),
    binary("011101010011"): ("smmulr", (0,4,2), 0),
    binary("011100000001"): ("smuad", (0,4,2), 0),
    binary("011100000011"): ("smuadx", (0,4,2), 0),
    binary("011100000101"): ("smusd", (0,4,2), 0),
    binary("011100000111"): ("smusdx", (0,4,2), 0),
}

def p_mult(opval, va):
    ocode, vals = chopmul(opval)
    mnem, opindexes, flags = iencmul_codes.get(ocode, multfail)
    #work around because masks match up - should be a cleaner way to do this?
    #if Ra = 15 then smmul
    if vals[1] == 15:
        newset = iencmul_r15_codes.get(ocode)
        if newset != None:
            mnem, opindexes, flags = newset
    if mnem == None:
        raise envi.InvalidInstruction(
                mesg="p_mult: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
    olist = []
    for i in opindexes:
        olist.append(ArmRegOper(vals[i], va=va))
    opcode = (IENC_MULT << 16) + ocode
    return (opcode, mnem, olist, flags, 0)

def p_dp_imm(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    imm = opval & 0xff
    #FIXME: Original was (opval>> 7) & 0x1f which grabs top 5 bits
    #supposed to be top 4 bits. Temp fix mask out wrong bit
    #should be (opval >> 8) & 0xf
    #need to find where rot / 2 and fix that.
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
    elif ocode in dp_noRn:# FIXME: FUGLY
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

    opcode = (IENC_DP_IMM << 16) + ocode
    if sflag > 0:
        # IF_PSR_S_SIL is silent s for tst, teq, cmp cmn
        if ocode in dp_silS:
            iflags = IF_PSR_S | IF_PSR_S_SIL
        else:
            iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, dp_mnem[ocode], olist, iflags, 0)

def p_undef(opval, va):
    # FIXME: make this an actual opcode with the opval as an imm oper
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
            0: 'Nop',
            1: 'yield',
            2: 'wfe',
            3: 'wfi',
            4: 'sev',
            }

def p_mov_imm_stat(opval, va):      # only one instruction: "msr"
    iflags = 0
    imm = opval & 0xff
    rot = (opval>>8) & 0xf
    r = (opval>>22) & 1
    mask = (opval>>16) & 0xf
    opcode = (IENC_MOV_IMM_STAT << 16)

    if mask == 0:
        opcode += 1
        # it's a NOP or some hint instruction
        if imm>>16:
            mnem = 'dbg'
            option = opval & 0xf
            olist = ( ArmDbgHintOption(option), )

        else:
            mnem = hint_mnem.get(imm)
            if mnem == None:
                raise envi.InvalidInstruction(
                        mesg="MSR/Hint illegal encoding",
                        bytez=struct.pack("<I", opval), va=va)
            olist = tuple()

    else:
        # it's an MSR <immediate>
        mnem = 'msr'
        immed = ((imm>>rot) + (imm<<(32-rot))) & 0xffffffff

        #if mask & 3:    # USER mode these will be 0
        #    iflags |= IF_SYS_MODE  - only mention of IF_SYS_MODE, causing errors.  does need fixing?
        
        olist = (
            ArmPgmStatRegOper(r, mask),
            ArmImmOper(immed),
        )
    
    return (opcode, mnem, olist, iflags, 0)
    
ldr_mnem = ("str", "ldr")
tsizes = (4, 1,)
def p_load_imm_off(opval, va, psize=4):
    # FIXME: handle STRT and others introduced in ARMv7 (p206)
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
    mnem = ldr_mnem[pubwl&1]
    iflags = 0
    if pubwl & 4:   # B   
        iflags = IF_B
    if (pubwl & 0x12) == 2:
        iflags |= IF_T
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
            ArmImmOffsetOper(Rn, imm, va, pubwl=pubwl, psize=psize)    # u=-/+, b=word/byte
        )
    opcode = (IENC_LOAD_IMM_OFF << 16)
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
    
    opcode = (IENC_LOAD_REG_OFF << 16) 
    return (opcode, ldr_mnem[pubwl&1], olist, iflags, 0)

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
    media_parsers_tmp[7] = p_media_smul
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
    if p_routine == None:
        raise envi.InvalidInstruction(
        mesg="p_media: can not find command! Definer = "+str(definer)+ " op = " +str(opval),
        bytez=struct.pack("<I", opval), va=va)
    return media_parsers[p_routine](opval, va)
    ''' Prototype stops here. From here to end of comment is original code
    if   (definer & 0xf8) == 0x60:
        return p_media_parallel(opval, va)
    elif (definer & 0xf8) == 0x68:
        return p_media_pack_sat_rev_extend(opval, va)
    elif (definer & 0xfb) == 0x70:
        return p_mult(opval, va)
    elif definer == 0x71:
        return p_div(opval, va)
    elif (definer & 0xfe) == 0x78:
        return p_media_usada(opval, va)
    elif (definer & 0xfe) == 0x7a:
        return p_media_sbfx(opval, va)
    else:
        raise envi.InvalidInstruction(
        mesg="p_media: can not find command! Definer = "+str(definer),
        bytez=struct.pack("<I", opval), va=va)'''

#generate mnemonics for parallel instructions (could do manually like last time...)
parallel_mnem = []
par_suffixes = ("add16", "asx", "sax", "sub16", "add8", "", "", "sub8")
par_prefixes = ("","s","q","sh","","u","uq","uh")
for pre in par_prefixes:
    for suf in par_suffixes:
        if not (len(pre) and len(suf)):
            parallel_mnem.append(None)
        else:
            parallel_mnem.append(pre+suf)

parallel_mnem = tuple(parallel_mnem)

def p_media_parallel(opval, va):
    
    opc1 = (opval>>17) & 0x38
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    opc1 += (opval>>5) & 7
    Rm = opval & 0xf
    mnem = parallel_mnem[opc1]
    olist = (
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmRegOper(Rm, va=va),
    )
    opcode = IENC_MEDIA_PARALLEL + opc1
    return (opcode, mnem, olist, 0, 0)


xtnd_mnem = []
xtnd_suffixes = ("xtab16", "","xtab", "xtah","xtb16", "", "xtb","xth",)
#xtnd_suffixes = ("xtab16","xtab","xtah","xtb16","xtb","xth",)  #old ones left here in case I merged wrong ones
xtnd_prefixes = ("s","u")
for pre in xtnd_prefixes:
    for suf in xtnd_suffixes:
        xtnd_mnem.append(pre+suf)
        
xtnd_mnem = tuple(xtnd_mnem)

pkh_mnem = ('pkhbt', 'pkhtb',)
sat_mnem = ('ssat','usat')
sat16_mnem = ('ssat16','usat16')    
rev_mnem = ('rev','rev16','rbit','revsh',)

#Routine is too complicated, needs to be redone
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
        mnem = pkh_mnem[idx]
        shift_type = shifter[idx]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        shift_imm = (opval>>7) & 0x1f
        Rm = opval & 0xf
        opcode = IENC_MEDIA_PACK + idx
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
            mnem = sat16_mnem[opidx]
            olist = (
                ArmRegOper(Rd, va=va),
                ArmImmOper(sat_imm),
                ArmRegOper(Rm, va=va),
            )
            opcode = IENC_MEDIA_SAT + opidx
        else:
            mnem = sat_mnem[opidx]
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
            opcode = IENC_MEDIA_SAT + 2 + opidx
            
    elif (opc1 & 3) == 2 and opc2 == 3:     #ssat16
        opidx = (opval>>22)&1
        sat_imm = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        mnem = sat16_mnem[opidx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOper(sat_imm),
            ArmRegOper(Rm, va=va),
        )
        opcode = IENC_MEDIA_SAT + opidx
        
    
    elif (opc1 > 0) and (opc2 & 7) == 3:           # byte rev word
        opidx = ((opval>>21) & 2) + ((opval>>7) & 1)
        mnem = rev_mnem[opidx]
        if mnem == None:
            raise envi.InvalidInstruction(
                    mesg="p_media_pack_sat_rev_extend: invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
 
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
        )
        opcode = IENC_MEDIA_REV + opidx
    #elif opc1 == 3 and opc2 == 0xb:         # byte rev pkt halfword
    #elif opc1 == 7 and opc2 == 0xb:         # byte rev signed halfword
    elif opc1 == 0 and opc2 == 0xb:         # select bytes
        mnem = "sel"
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegOper(Rm, va=va),
        )
        opcode = IENC_MEDIA_SEL
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
        mnem = xtnd_mnem[idx]
        opcode = IENC_MEDIA_EXTEND + opc1
    else:
        raise envi.InvalidInstruction(
                mesg="p_media_extend: invalid instruction"+opc1+"."+opc2,
                bytez=struct.pack("<I", opval), va=va)

    return (opcode, mnem, olist, 0, 0)

#smult3_mnem = ('smlad','smlsd',,,'smlald')
def p_media_smul(opval, va):
    raise envi.InvalidInstruction(
            mesg="Should not reach here.  If we reach here, we'll have to implement MEDIA_SMUL extended multiplication (type 3)",
            bytez=struct.pack("<I", opval), va=va)
    # hmmm, is this already handled?
    
bf_mnem = ("bfi", "ubfx", "bfc")
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
    opcode = INS_BF
    mnem = bf_mnem[idx]
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
        opcode = IENC_MEDIA_USAD8
    else:
        mnem = "usada8"
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
            ArmRegOper(Rn, va=va),
        )
        opcode = IENC_MEDIA_USADA8

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
    opcode = IENC_MEDIA_SBFX
    return (opcode, mnem, olist, 0, 0)

div_mnem= ("sdiv","udiv")
def p_div(opval, va):
    Rd = (opval>>16) & 0xf
    Rm = (opval>>8) & 0xf
    Rn = opval & 0xf
    mnem = div_mnem[(opval>>21) & 1]
    olist = (
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmRegOper(Rm, va=va),
    )
    opcode = IENC_MEDIA_PDIV
    return (opcode, mnem, olist, 0, 0)

def p_arch_undef(opval, va):
    print ("p_arch_undef: invalid instruction (by definition in ARM spec): %.8x:\t%.8x"%(va,opval))
    raise envi.InvalidInstruction(
            mesg="p_arch_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
    return (IENC_ARCH_UNDEF, 'arch undefined', (ArmImmOper(opval),), 0, 0)

ldm_mnem = ("stm", "ldm")

def p_load_mult(opval, va):
    puswl = (opval>>20) & 0x1f
    mnem_idx = puswl & 1
    mnem = ldm_mnem[(mnem_idx)]
    flags = ((puswl>>3)<<(IF_DAIB_SHFT)) | IF_DA     # store bits for decoding whether to dec/inc before/after between ldr/str.  IF_DA tells the repr to print the the DAIB extension after the conditional.  right shift necessary to clear lower three bits, and align us with IF_DAIB_SHFT
    Rn = (opval>>16) & 0xf
    reg_list = opval & 0xffff
    if (opval&0x0fff0000) == 0x8bd0000:
        mnem = "pop"
        olist = (
            ArmRegListOper(reg_list, puswl),
        )
    elif (opval&0x0fff0000) == 0x92d0000:
        mnem = "push"
        olist = (
            ArmRegListOper(reg_list, puswl),
        )
    else:     
        olist = (
            ArmRegOper(Rn, va=va),
            ArmRegListOper(reg_list, puswl),
        )

    # If we are a load multi (ldm), and we load PC, we are NOFALL
    # (FIXME unless we are conditional... ung...)
    if mnem_idx == 1 and reg_list & (1 << REG_PC):
        flags |= envi.IF_NOFALL
        # If the load is from the stack, call it a "return"
        if Rn == REG_SP:
            flags |= envi.IF_RET
    if puswl & 2:       # W (mnemonic: "!")
        flags |= IF_W
        olist[0].oflags |= OF_W

    if puswl & 4:       # UM - usermode, or mov current SPSR -> CPSR if r15 included
        flags |= IF_UM
        olist[1].oflags |= OF_UM
    opcode = (IENC_LOAD_MULT << 16)
    return (opcode, mnem, olist, flags, 0)

b_mnem = ("b", "bl",)
def p_branch(opval, va):        # primary branch encoding.  others were added later in the media section
    off = e_bits.signed(opval, 3)
    off <<= 2
    link = (opval>>24) & 1

    #FIXME this assumes A1 branch encoding.
    
    olist = ( ArmPcOffsetOper(off, va),)
    if link:
        flags = envi.IF_CALL
    else:
        flags = envi.IF_BRANCH
    
    opcode = (IENC_BRANCH << 16) + link
    return (opcode, b_mnem[link], olist, flags, 0)

ldc_mnem = ("stc", "ldc",)
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
    opcode = (IENC_COPROC_LOAD << 16)
    return (opcode, ldc_mnem[punwl&1], olist, iflags, 0)

mcrr_mnem = ("mcrr", "mrrc")
def p_coproc_dbl_reg_xfer(opval, va):
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    opcode = (opval>>4) & 0xf
    CRm = opval & 0xf
    mnem = mcrr_mnem[(opval>>20) & 1]
    
    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(opcode),
        ArmRegOper(Rd, va=va),
        ArmRegOper(Rn, va=va),
        ArmCoprocRegOper(CRm),
    )
    opcode = IENC_COPROC_RREG_XFER<<16
    return (opcode, mnem, olist, 0, 0)
    
cdp_mnem = ("cdp", "cdp2")

def p_coproc_dp(opval, va):
    opcode1 = (opval>>20) & 0xf
    CRn = (opval>>16) & 0xf
    CRd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    opcode2 = (opval>>5) & 0x7
    CRm = opval & 0xf
    mnem = cdp_mnem[(opval>>28)&1]

    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(opcode1),
        ArmCoprocRegOper(CRd),
        ArmCoprocRegOper(CRn),
        ArmCoprocRegOper(CRm),
        ArmCoprocOpcodeOper(opcode2),
    )
    
    opcode = (IENC_COPROC_DP << 16)
    return (opcode, mnem, olist, 0, 0)
mcr_mnem = ("mcr", "mrc")
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
    
    opcode = (IENC_COPROC_REG_XFER << 16)
    return (opcode, mcr_mnem[load], olist, 0, 0)

#swi has been changed to svc in latest ref
def p_swint(opval, va):
    swint = opval & 0xffffff
    
    olist = ( ArmImmOper(swint), )
    opcode = IENC_SWINT << 16 + 1
    return (opcode, "svc", olist, 0, 0)

cps_mnem = ("cps","cps FAIL-bad encoding","cpsie","cpsid")
mcrr2_mnem = ("mcrr2", "mrrc2")
ldc2_mnem = ("stc2", "ldc2",)
mcr2_mnem = ("mcr2", "mrc2")
pld_mnem = ("pldw", "pld")
pl_opcode = (IENC_UNCOND_PLI, IENC_UNCOND_PLD)
def p_uncond(opval, va, psize = 4):
    if opval & 0x0f000000 == 0x0f000000:
        # FIXME THIS IS HORKED
        opcode = IENC_SWINT << 16 + 2
        immval = opval & 0x00ffffff
        return (opcode, 'swi', (ArmImmOper(immval),), 0, 0)

    optop = ( opval >> 26 ) & 0x3
    if optop == 0:
        if opval & 0xfff10020 == 0xf1000000:
            #cps
            imod = (opval>>18)&3
            mmod = (opval>>17)&1
            aif = (opval>>5)&7
            mode = opval&0x1f
            mnem = cps_mnem[imod]
            
            if imod & 2:
                olist = [
                    ArmCPSFlagsOper(aif)    # if mode is set...
                ]
            else:
                olist = []
            if mmod:
                olist.append(ArmImmOper(mode))
            
            opcode = IENC_UNCOND_CPS + imod
            return (opcode, mnem, olist, 0, 0)
        elif (opval & 0xffff00f0) == 0xf1010000:
            #setend
            e = (opval>>9) & 1
            mnem = "setend"
            olist = ( ArmEndianOper(e), )
            opcode = IENC_UNCOND_SETEND
            return (opcode, mnem, olist, 0, 0)

        elif (opval & 0xfe000000 == 0xf2000000):
            #print "handing off to adv_simd_32"
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
            opcode = pl_opcode[pl]
            if pl==0:
                mnem = "pli"
            else:
                mnem = pld_mnem[R]
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
            opcode = IENC_UNCOND_SRS
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
            opcode = IENC_UNCOND_RFE
            return (opcode, mnem, olist, flags, 0)

        elif (opval & 0xfe000000) == 0xfa000000:
            #blx
            mnem = "blx"
            h = (opval>>23) & 2
            imm_offset = (e_bits.signed(opval, 3) << 2) | h
            
            olist = (
                ArmPcOffsetOper(imm_offset, va),
            )
            
            opcode = INS_BLX
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
            mnem = mcrr2_mnem[(opval>>20) & 1]
                
            olist = (
                ArmCoprocOper(cp_num),
                ArmCoprocOpcodeOper(opcode),
                ArmRegOper(Rd, va=va),
                ArmRegOper(Rn, va=va),
                ArmCoprocRegOper(CRm),
            )
            opcode = IENC_COPROC_RREG_XFER<<16
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
            
            opcode = (IENC_COPROC_LOAD << 16)
            return (opcode, ldc2_mnem[punwl&1], olist, iflags, 0)

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
            
            opcode = (IENC_COPROC_REG_XFER << 16)
            return (opcode, mcr2_mnem[load], olist, 0, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=3): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    


def p_advsimd_secondary(val, va, mnem, opcode, flags, opers):

    if opcode == INS_VORR:
        pass


adv_simd_3_regs = (  # ABUC fields slammed together
        # a=0000 b=0
        ('vhadd', INS_VHADD, IFS_S8, None),
        ('vhadd', INS_VHADD, IFS_S16, None),
        ('vhadd', INS_VHADD, IFS_S32, None),
        (None, INS_VHADD, 0, None),
        ('vhadd', INS_VHADD, IFS_U8, None),
        ('vhadd', INS_VHADD, IFS_U16, None),
        ('vhadd', INS_VHADD, IFS_U32, None),
        (None, INS_VHADD, 0, None),

        # a=0000 b=1
        ('vqadd', INS_VQADD, IFS_S8, None),
        ('vqadd', INS_VQADD, IFS_S16, None),
        ('vqadd', INS_VQADD, IFS_S32, None),
        ('vqadd', INS_VQADD, IFS_S64, None),
        ('vqadd', INS_VQADD, IFS_U8, None),
        ('vqadd', INS_VQADD, IFS_U16, None),
        ('vqadd', INS_VQADD, IFS_U32, None),
        ('vqadd', INS_VQADD, IFS_U64, None),

        # a=0001 b=0
        ('vrhadd', INS_VRHADD, IFS_S8, None),
        ('vrhadd', INS_VRHADD, IFS_S16, None),
        ('vrhadd', INS_VRHADD, IFS_S32, None),
        (None, INS_VRHADD, 0, None),
        ('vrhadd', INS_VRHADD, IFS_U8, None),
        ('vrhadd', INS_VRHADD, IFS_U16, None),
        ('vrhadd', INS_VRHADD, IFS_U32, None),
        (None, INS_VRHADD, 0, None),

        # a=0001 b=1
        ('vand', INS_VAND, 0, None),
        ('vbic', INS_VBIC, 0, None),
        ('vorr', INS_VORR, 0, p_advsimd_secondary),    # vmov if source registers identical
        ('vorn', INS_VORN, 0, None),
        ('veor', INS_VEOR, 0, None),
        ('vbif', INS_VBIF, 0, None),
        ('vbit', INS_VBIT, 0, None),
        ('vbsl', INS_VBSL, 0, None),

        # a=0010 b=0
        ('vhsub', INS_VHSUB, IFS_S8, None),
        ('vhsub', INS_VHSUB, IFS_S16, None),
        ('vhsub', INS_VHSUB, IFS_S32, None),
        (None, INS_VHSUB, 0, None),
        ('vhsub', INS_VHSUB, IFS_U8, None),
        ('vhsub', INS_VHSUB, IFS_U16, None),
        ('vhsub', INS_VHSUB, IFS_U32, None),
        (None, INS_VHSUB, 0, None),

        # a=0010 b=1
        ('vqsub', INS_VQSUB, IFS_S8, None),
        ('vqsub', INS_VQSUB, IFS_S16, None),
        ('vqsub', INS_VQSUB, IFS_S32, None),
        ('vqsub', INS_VQSUB, IFS_S64, None),
        ('vqsub', INS_VQSUB, IFS_U8, None),
        ('vqsub', INS_VQSUB, IFS_U16, None),
        ('vqsub', INS_VQSUB, IFS_U32, None),
        ('vqsub', INS_VQSUB, IFS_U64, None),

        # a=0011 b=0
        ('vcgt', INS_VCGT, IFS_S8, None),
        ('vcgt', INS_VCGT, IFS_S16, None),
        ('vcgt', INS_VCGT, IFS_S32, None),
        (None, INS_VCGT, 0, None),
        ('vcgt', INS_VCGT, IFS_U8, None),
        ('vcgt', INS_VCGT, IFS_U16, None),
        ('vcgt', INS_VCGT, IFS_U32, None),
        (None, INS_VCGT, 0, None),

        # a=0011 b=1
        ('vcge', INS_VCGE, IFS_S8, None),
        ('vcge', INS_VCGE, IFS_S16, None),
        ('vcge', INS_VCGE, IFS_S32, None),
        (None, INS_VCGE, 0, None),
        ('vcge', INS_VCGE, IFS_U8, None),
        ('vcge', INS_VCGE, IFS_U16, None),
        ('vcge', INS_VCGE, IFS_U32, None),
        (None, INS_VCGE, 0, None),

        # a=0100 b=0
        ('vshl', INS_VSHL, IFS_S8, None),
        ('vshl', INS_VSHL, IFS_S16, None),
        ('vshl', INS_VSHL, IFS_S32, None),
        ('vshl', INS_VSHL, IFS_S64, None),
        ('vshl', INS_VSHL, IFS_U8, None),
        ('vshl', INS_VSHL, IFS_U16, None),
        ('vshl', INS_VSHL, IFS_U32, None),
        ('vshl', INS_VSHL, IFS_U64, None),

        # a=0100 b=1
        ('vqshl', INS_VQSHL, IFS_S8, None),
        ('vqshl', INS_VQSHL, IFS_S16, None),
        ('vqshl', INS_VQSHL, IFS_S32, None),
        ('vqshl', INS_VQSHL, IFS_S64, None),
        ('vqshl', INS_VQSHL, IFS_U8, None),
        ('vqshl', INS_VQSHL, IFS_U16, None),
        ('vqshl', INS_VQSHL, IFS_U32, None),
        ('vqshl', INS_VQSHL, IFS_U64, None),

        # a=0101 b=0
        ('vrshl', INS_VRSHL, IFS_S8, None),
        ('vrshl', INS_VRSHL, IFS_S16, None),
        ('vrshl', INS_VRSHL, IFS_S32, None),
        ('vrshl', INS_VRSHL, IFS_S64, None),
        ('vrshl', INS_VRSHL, IFS_U8, None),
        ('vrshl', INS_VRSHL, IFS_U16, None),
        ('vrshl', INS_VRSHL, IFS_U32, None),
        ('vrshl', INS_VRSHL, IFS_U64, None),

        # a=0101 b=1
        ('vqrshl', INS_VQRSHL, IFS_S8, None),
        ('vqrshl', INS_VQRSHL, IFS_S16, None),
        ('vqrshl', INS_VQRSHL, IFS_S32, None),
        ('vqrshl', INS_VQRSHL, IFS_S64, None),
        ('vqrshl', INS_VQRSHL, IFS_U8, None),
        ('vqrshl', INS_VQRSHL, IFS_U16, None),
        ('vqrshl', INS_VQRSHL, IFS_U32, None),
        ('vqrshl', INS_VQRSHL, IFS_U64, None),

        # a=0110 b=0
        ('vmax', INS_VMAX, IFS_S8, None),
        ('vmax', INS_VMAX, IFS_S16, None),
        ('vmax', INS_VMAX, IFS_S32, None),
        (None, INS_VMAX, 0, None),
        ('vmax', INS_VMAX, IFS_U8, None),
        ('vmax', INS_VMAX, IFS_U16, None),
        ('vmax', INS_VMAX, IFS_U32, None),
        (None, INS_VMAX, 0, None),

        # a=0110 b=1
        ('vmin', INS_VMIN, IFS_S8, None),
        ('vmin', INS_VMIN, IFS_S16, None),
        ('vmin', INS_VMIN, IFS_S32, None),
        (None, INS_VMIN, 0, None),
        ('vmin', INS_VMIN, IFS_U8, None),
        ('vmin', INS_VMIN, IFS_U16, None),
        ('vmin', INS_VMIN, IFS_U32, None),
        (None, INS_VMIN, 0, None),

        # a=0111 b=0
        ('vabd', INS_VABD, IFS_S8, None),
        ('vabd', INS_VABD, IFS_S16, None),
        ('vabd', INS_VABD, IFS_S32, None),
        (None, INS_VABD, 0, None),
        ('vabd', INS_VABD, IFS_U8, None),
        ('vabd', INS_VABD, IFS_U16, None),
        ('vabd', INS_VABD, IFS_U32, None),
        (None, INS_VABD, 0, None),

        # a=0111 b=1
        ('vaba', INS_VABA, IFS_S8, None),
        ('vaba', INS_VABA, IFS_S16, None),
        ('vaba', INS_VABA, IFS_S32, None),
        (None, INS_VABA, 0, None),
        ('vaba', INS_VABA, IFS_U8, None),
        ('vaba', INS_VABA, IFS_U16, None),
        ('vaba', INS_VABA, IFS_U32, None),
        (None, INS_VABA, 0, None),

        # a=1000 b=0
        ('vadd', INS_VADD, IFS_I8, None),
        ('vadd', INS_VADD, IFS_I16, None),
        ('vadd', INS_VADD, IFS_I32, None),
        (None, INS_VADD, 0, None),
        ('vsub', INS_VSUB, IFS_I8, None),
        ('vsub', INS_VSUB, IFS_I16, None),
        ('vsub', INS_VSUB, IFS_I32, None),
        (None, INS_VSUB, 0, None),

        # a=1000 b=1
        ('vtst', INS_VTST, IFS_I8, None),
        ('vtst', INS_VTST, IFS_I16, None),
        ('vtst', INS_VTST, IFS_I32, None),
        (None, INS_VTST, 0, None),
        ('vceq', INS_VCEQ, IFS_I8, None),
        ('vceq', INS_VCEQ, IFS_I16, None),
        ('vceq', INS_VCEQ, IFS_I32, None),
        (None, INS_VCEQ, 0, None),

        # a=1001 b=0        # DOUBLECHECK THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ('vmla', INS_VMLA, IFS_I8, None),
        ('vmla', INS_VMLA, IFS_I16, None),
        ('vmla', INS_VMLA, IFS_I32, None),
        (None, INS_VMLA, 0, None),
        ('vmls', INS_VMLS, IFS_I8, None),
        ('vmls', INS_VMLS, IFS_I16, None),
        ('vmls', INS_VMLS, IFS_I32, None),
        (None, INS_VMLS, 0, None),

        # a=1001 b=1
        ('vmul', INS_VMUL, IFS_S8, None),
        ('vmul', INS_VMUL, IFS_S16, None),
        ('vmul', INS_VMUL, IFS_S32, None),
        (None, INS_VMUL, 0, None),
        ('vmul', INS_VMUL, IFS_U8, None),
        ('vmul', INS_VMUL, IFS_U16, None),
        ('vmul', INS_VMUL, IFS_U32, None),
        (None, INS_VMUL, 0, None),

        # a=1010 b=0
        ('vpmax', INS_VPMAX, IFS_S8, None),
        ('vpmax', INS_VPMAX, IFS_S16, None),
        ('vpmax', INS_VPMAX, IFS_S32, None),
        (None, INS_VPMAX, 0, None),
        ('vpmax', INS_VPMAX, IFS_U8, None),
        ('vpmax', INS_VPMAX, IFS_U16, None),
        ('vpmax', INS_VPMAX, IFS_U32, None),
        (None, INS_VPMAX, 0, None),

        # a=1010 b=1
        ('vpmin', INS_VPMIN, IFS_S8, None),
        ('vpmin', INS_VPMIN, IFS_S16, None),
        ('vpmin', INS_VPMIN, IFS_S32, None),
        (None, INS_VPMIN, 0, None),
        ('vpmin', INS_VPMIN, IFS_U8, None),
        ('vpmin', INS_VPMIN, IFS_U16, None),
        ('vpmin', INS_VPMIN, IFS_U32, None),
        (None, INS_VPMIN, 0, None),

        # a=1011 b=0
        (None, INS_VHADD, 0, None),
        ('vqdmulh', INS_VQDMULH, IFS_S16, None),
        ('vqdmulh', INS_VQDMULH, IFS_S32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        ('vqrdmulh', INS_VQRDMULH, IFS_S16, None),
        ('vqrdmulh', INS_VQRDMULH, IFS_S32, None),
        (None, INS_VHADD, 0, None),

        # a=1011 b=1
        ('vpadd', INS_VPADD, IFS_I8, None),
        ('vpadd', INS_VPADD, IFS_I16, None),
        ('vpadd', INS_VPADD, IFS_I32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),

        # a=1100 b=0
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),

        # a=1100 b=1
        ('vfma', INS_VFMA, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vfms', INS_VFMS, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),

        # a=1101 b=0
        ('vadd', INS_VADD, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vsub', INS_VSUB, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vpadd', INS_VPADD, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vabd', INS_VABD, IFS_F32, None),
        (None, INS_VHADD, 0, None),

        # a=1101 b=1
        ('vmla', INS_VMLA, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vmls', INS_VMLS, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vmul', INS_VMUL, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),

        # a=1110 b=0
        ('vceq', INS_VCEQ, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        ('vcge', INS_VCGE, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vcgt', INS_VCGT, IFS_F32, None),
        (None, INS_VHADD, 0, None),

        # a=1110 b=1
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        ('vacge', INS_VACGE, IFS_F32, None), # check if all instructions code this way: Q==0 means Dx Regs, Q==1 means Qx Regs
        (None, INS_VHADD, 0, None),
        ('vacgt', INS_VACGT, IFS_F32, None),
        (None, INS_VHADD, 0, None),

        # a=1111 b=0
        ('vmax', INS_VMAX, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vmin', INS_VMIN, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vpmax', INS_VPMAX, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vpmin', INS_VPMIN, IFS_F32, None),
        (None, INS_VHADD, 0, None),

        # a=1111 b=1
        ('vrecps', INS_VRECPS, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        ('vrsqrts', INS_VRSQRTS, IFS_F32, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),
        (None, INS_VHADD, 0, None),

    )

adv_simd_1modimm = (
        # op = 0
        # 0xx0 and 0xx1
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        # 10x0 and 10x1
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vorr', INS_VORR, 0, None),
        # 11xx
        ('vmov', INS_VMOV, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vmov', INS_VMOV, 0, None),
        ('vmov', INS_VMOV, 0, None),

        # op = 1
        # 0xx0 and 0xx1
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        # 10x0 and 10x1
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        ('vmvn', INS_VMVN, 0, None),
        ('vbic', INS_VBIC, 0, None),
        # 110x
        ('vmvn', INS_VMVN, 0, None),
        ('vmvn', INS_VMVN, 0, None),
        # 1110
        ('vmov', INS_VMOV, 0, None),
        # 1111 undef
        ('vector UNDEF', None, 0, None),
    )

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
    rbase = ('d%d', 'q%d')[q]

    d = (val >> 18) & 0x10
    d |= ((val >> 12) & 0xf)
    d >>= q

    if not (a & 0x10):
        # three registers of the same length
        a = (val>>8) & 0xf
        b = (val>>4) & 1
        c = (val>>20) & 3

        index = c | (u<<2) | (b<<3) | (a<<4)
        mnem, opcode, simdflags, handler = adv_simd_3_regs[index]

        n = (val >> 3) & 0x10
        n |= ((val >> 16) & 0xf)
        n >>= q

        m = (val >> 1) & 0x10
        m |= (val & 0xf)
        m >>= q

        opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
            ArmRegOper(rctx.getRegisterIndex(rbase%n)),
            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
            )

        if handler != None:
            nmnem, nopcode, nflags, nopers = handler(val, va, mnem, opcode, flags, opers)
            if nmnem != None:
                mnem = nmnem
                opcode = nopcode
            if nflags != None:
                flags = nflags
            if nopers != None:
                opers = nopers

        return opcode, mnem, opers, 0, simdflags    # no iflags, only simdflags for this one

    elif (a & 0x17) == 0x10 and (c & 0x9) == 1:
        # one register and modified immediate
        op = (c>>1) & 1
        cmode = b
        index = (op<<4) | cmode

        mnem, opcode, simdflags, handler = adv_simd_1modimm[index]

        abcdefgh = (u<<7) | ((val>>12) & 0x70) | (val & 0xf)

        dt, val = adv_simd_modifiers[index](abcdefgh)

        opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
            ArmImmOper(val),
            )

        return opcode, mnem, opers, 0, dt    # no iflags, only simdflags for this one

        # must be ordered after previous, since this mask collides
    elif ((a & 0x10) == 0x10 and (c & 0x9) in (1, 9)):
        # two registers and a shift amount
        a = (val>>8) & 0xf
        b = (val>>6) & 1
        l = (val>>7) & 1
        
        index = (a<<3) | (u<<2) | (b<<1) | l

        mnem, opcode, enctype = adv_2regs[index]

        m = (val>>1) & 0x10   # bit 5 but wants to be bit 4
        m |= (val & 0xf)
        m >>= q

        imm = (val >> 16) & 0x3f

        #### REMOVE WHEN COMPLETE WITH DECODING
        shift_amount = 0
        simdflags = 0
        ####

        if enctype == 0:    # VSHR used as test
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                elements = 1
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                elements = 2
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                elements = 4
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                elements = 8
                shift_amount = 16-imm

            simdflags = adv_2_vqshl_typesize.get(esize)[u+2]

        elif enctype == 1:  # VSRI
            limm = (l<<6) | imm
            if limm & 0b1000000:
                esize = 64
                elements = 1
                shift_amount = 64-imm
            elif limm & 0b0100000:
                esize = 32
                elements = 2
                shift_amount = 64-imm
            elif limm & 0b0010000:
                esize = 16
                elements = 4
                shift_amount = 32-imm
            elif limm & 0b0001000:
                esize = 8
                elements = 8
                shift_amount = 16-imm

            simdflags = { 8: IFS_8, 16: IFS_16, 32: IFS_32, 64: IFS_64 }[esize]

        elif enctype == 2:    # VQSHLU used as test
            limm = (l<<6) | imm

            op = a & 1

            if limm & 0b1000000:
                esize = 64
                elements = 1
                shift_amount = imm
            elif limm & 0b0100000:
                esize = 32
                elements = 2
                shift_amount = imm-32
            elif limm & 0b0010000:
                esize = 16
                elements = 4
                shift_amount = imm-16
            elif limm & 0b0001000:
                esize = 8
                elements = 8
                shift_amount = imm-8

            uop = (u<<1) | op
            simdflags = adv_2_vqshl_typesize.get(esize)[uop]

        elif enctype == 3:
            raise Exception('adv_simd 2 reg shift imm, enctype:3 NOT IMPLEMENTED!')
        elif enctype == 4:
            pass
        elif enctype == 5:
            pass

        opers = (
            ArmRegOper(rctx.getRegisterIndex(rbase%d)),
            ArmRegOper(rctx.getRegisterIndex(rbase%m)),
            ArmImmOper(shift_amount),
            )

        return opcode, mnem, opers, 0, simdflags

################################ FIXME: CONTINUE WORKING AdvSIMD HERE #######################3
    elif (a < 0x16):
        print "AdvSIMD: HIT a<0x16"
        if (c & 0x5) == 0:
            # three registers of different lengths
            pass

        elif (c & 0x5) == 0x4:
            # two registers and a scalar
            pass

    elif (a & 0x16) == 0x16:
        print "AdvSIMD: HIT a & 0x16 == 0x16"
        if u == 0:
            # vector extract VEXT
            pass

        else:
            if (c & 1) == 0:
                if (b & 0x8) == 0:
                    # two registers, miscellaneous
                    pass

                elif (b & 0xc) == 8:
                    # vector table lookup VTBL, VTBX
                    pass

                elif (b == 0xc):
                    # vector duplicate VDUP (scalar)
                    pass
    return 0, 'NO VECTOR ENCODING COMPLETED', (), 0, 0

################### FIXME ABOVE: NOT COMPLETE DECODING  #######################

adv_2_vqshl_typesize = {
    8: ( None, IFS_S8, IFS_S8, IFS_U8),
    16: ( None, IFS_S16, IFS_S16, IFS_U16),
    32: ( None, IFS_S32, IFS_S32, IFS_U32),
    64: ( None, IFS_S64, IFS_S64, IFS_U64),
    }

# one register and modified immediate modifiers...
def adv_simd_mod_000x(abcdefgh):
    return IFS_I32, (abcdefgh << 32) | abcdefgh

def adv_simd_mod_001x(abcdefgh):
    return IFS_I32,(abcdefgh << 40) | (abcdefgh << 8)

def adv_simd_mod_010x(abcdefgh):
    return IFS_I32, (abcdefgh << 48) | (abcdefgh << 16)

def adv_simd_mod_011x(abcdefgh):
    return IFS_I32, (abcdefgh << 56) | (abcdefgh << 24)

def adv_simd_mod_100x(abcdefgh):
    return IFS_I16, (abcdefgh << 48) | (abcdefgh << 32) | (abcdefgh << 16) | abcdefgh

def adv_simd_mod_101x(abcdefgh):
    return IFS_I16, (abcdefgh << 56) | (abcdefgh << 40) | (abcdefgh << 24) | (abcdefgh << 8)

def adv_simd_mod_1100(abcdefgh):
    return IFS_I32, (abcdefgh << 40) | (abcdefgh << 8) | 0xf000f

def adv_simd_mod_1101(abcdefgh):
    return IFS_I32, (abcdefgh << 48) | (abcdefgh << 16) | 0xff00ff

def adv_simd_mod_0_1110(abcdefgh):
    return IFS_I8, (abcdefgh << 48) | (abcdefgh << 32) | (abcdefgh << 16) | abcdefgh | (abcdefgh << 56) | (abcdefgh << 40) | (abcdefgh << 24) | (abcdefgh << 8)

def adv_simd_mod_0_1111(abcdefgh):
    a = (abcdefgh & 0b10000000) << 24
    b = (abcdefgh >> 6) & 1
    B = (b | (b<<1) | (b<<2) | (b<<3) | (b<<4) | (b<<5)) <<25
    cdefgh = (abcdefgh << 19) & 0x1f80000
    single = a | B | cdefgh
    full = (single << 32) | single
    return IFS_F32, full

def adv_simd_mod_1_1110(abcdefgh):
    a = abcdefgh >> 7
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
    return IFS_I64, ALL


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
    )

adv_2regs = (
    # 0000
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    ('vshr', INS_VSHR, 0),
    # 0001
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    ('vsra', INS_VSRA, 0),
    # 0010
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    ('vrshr', INS_VRSHR, 0),
    # 0011
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    ('vrsra', INS_VRSRA, 0),
    # 0100
    ('ERROR vsri', INS_VSRI, 1),
    ('ERROR vsri', INS_VSRI, 1),
    ('ERROR vsri', INS_VSRI, 1),
    ('ERROR vsri', INS_VSRI, 1),
    ('vsri', INS_VSRI, 1),
    ('vsri', INS_VSRI, 1),
    ('vsri', INS_VSRI, 1),
    ('vsri', INS_VSRI, 1),
    # 0101
    ('vshl', INS_VSHL, 1),
    ('vshl', INS_VSHL, 1),
    ('vshl', INS_VSHL, 1),
    ('vshl', INS_VSHL, 1),
    ('vsli', INS_VSLI, 1),
    ('vsli', INS_VSLI, 1),
    ('vsli', INS_VSLI, 1),
    ('vsli', INS_VSLI, 1),
    # 0110
    ('ERROR vqshl', INS_VQSHL, 2), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2), # U=0, op=0
    ('ERROR vqshl', INS_VQSHL, 2), # U=0, op=0
    ('vqshlu', INS_VQSHLU, 2), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2), # U=1, op=0
    ('vqshlu', INS_VQSHLU, 2), # U=1, op=0
    # 0111
    ('vqshl', INS_VQSHL, 2), # U=0, op=1
    ('vqshl', INS_VQSHL, 2), # U=0, op=1
    ('vqshl', INS_VQSHL, 2), # U=0, op=1
    ('vqshl', INS_VQSHL, 2), # U=0, op=1
    ('vqshl', INS_VQSHL, 2), # U=1, op=1
    ('vqshl', INS_VQSHL, 2), # U=1, op=1
    ('vqshl', INS_VQSHL, 2), # U=1, op=1
    ('vqshl', INS_VQSHL, 2), # U=1, op=1
    # 1000
    ('vshrn', INS_VSHRN, 3),        # I16-64
    ('vshrn', INS_VSHRN, 3),        # None
    ('vrshrn', INS_VRSHRN, 3),      # I16-64
    ('vrshrn', INS_VRSHRN, 3),      # None
    ('vqshrn', INS_VQSHRN, 3),
    ('vqshrun', INS_VQSHRUN, 3),
    ('vqrshrn', INS_VQRSHRN, 3),
    ('vqrshrun', INS_VQRSHRUN, 3),
    # 1001
    ('vqshrn', INS_VQSHRN, 3),  # hold on, u is not specified... does it parse correctly with 3?
    ('ERROR vqshrn', INS_VQSHRN, 3),  # hold on, u is not specified...
    ('vqrshrn', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR vqrshrn', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('vqshrn', INS_VQSHRN, 3),  # hold on, u is not specified...
    ('ERROR vqshrn', INS_VQSHRN, 3),  # hold on, u is not specified...
    ('vqrshrn', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR vqrshrn', INS_VQRSHRN, 3),  # hold on, u is not specified...
    # 1010
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    ('vshll', INS_VSHLL, 4),    # vmovl if imm6 ends in 0b000
    # 1011
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1011', INS_VQRSHRN, 3),  # hold on, u is not specified...
    # 1100
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1100', INS_VQRSHRN, 3),  # hold on, u is not specified...
    # 1101
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    ('ERROR advsimd-2rs-1101', INS_VQRSHRN, 3),  # hold on, u is not specified...
    # 1110
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    # 1111
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),
    ('vcvt', INS_VCVT, 5),


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
ienc_parsers_tmp[IENC_SWINT] =    p_swint
ienc_parsers_tmp[IENC_UNCOND] = p_uncond
ienc_parsers_tmp[IENC_DP_MOVT] = p_dp_movt
ienc_parsers_tmp[IENC_DP_MOVW] = p_dp_movw

ienc_parsers = tuple(ienc_parsers_tmp)

####################################################################

# the primary table is index'd by the 3 bits following the
# conditional and are structured as follows:
# ( ENC, nexttable )
# If ENC != None, those 3 bits were enough for us to know the
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
    (0b00001111111000000000000000000000, 0b00001100010000000000000000000000, IENC_COPROC_RREG_XFER),
    (0b00001110000000000000000000000000, 0b00001100000000000000000000000000, IENC_COPROC_LOAD),
)

s_7_table = (
    (0b00000001000000000000000000000000, 0b00000001000000000000000000000000, IENC_SWINT),
    (0b00000001000000000000000000010000, 0b00000000000000000000000000010000, IENC_COPROC_REG_XFER),
    (0, 0, IENC_COPROC_DP),
)

# Initial 3 (non conditional) primary table
inittable = [
    (None, s_0_table),
    (None, s_1_table),
    (IENC_LOAD_IMM_OFF, None), # Load or store an immediate
    (None, s_3_table),
    (IENC_LOAD_MULT, None),
    (IENC_BRANCH, None),
    (None, s_6_table),
    (None, s_7_table),
    (IENC_UNCOND, None), # may wish to make this it's own table...
]

endian_names = ("le","be")

class ArmOpcode(envi.Opcode):
    _def_arch = envi.ARCH_ARMV7

    def __init__(self, va, opcode, mnem, prefixes, size, operands, iflags=0, simdflags=0):
        """
        constructor for the basic Envi Opcode object.  Arguments as follows:

        opcode   - An architecture specific numerical value for the opcode
        mnem     - A humon readable mnemonic for the opcode
        prefixes - a bitmask of architecture specific instruction prefixes
        size     - The size of the opcode in bytes
        operands - A list of Operand objects for this opcode
        iflags   - A list of Envi (architecture independant) instruction flags (see IF_FOO)
        va       - The virtual address the instruction lives at (used for PC relative immediates etc...)

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

        # FIXME if this is a move to PC god help us...
        flags = 0

        if self.prefixes != COND_AL:
            flags |= envi.BR_COND

        if self.opcode in ( INS_B, INS_BX, INS_BL, INS_BLX, INS_BCC ):
            oper = self.opers[0]

            # check for location being ODD
            operval = oper.getOperValue(self)
            if operval == None:
                # probably a branch to a register.  just return.
                return ret

            if self.opcode in (INS_BLX, INS_BX):
                if operval & 3:
                    flags |= envi.ARCH_THUMB16
                else:
                    flags |= envi.ARCH_ARMV7

            # if we don't know that it's thumb, default to "ARCH_DEFAULT"
            else:
                flags |= self._def_arch


            #operval &= 0xfffffffe           # this has to work for both arm and thumb
            if self.iflags & envi.IF_CALL:
                flags |= envi.BR_PROC
            ret.append((operval, flags))

        return ret

    def getOperValue(self, idx, emu=None):
        oper = self.opers[idx]
        return oper.getOperValue(self, emu=emu)

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
        elif daib_flags > 0:
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

            if self.simdflags:
                if self.simdflags & IFS_S32F64:
                    mnem += '.s32.f64'
                elif self.simdflags & IFS_S32F32:
                    mnem += '.s32.f32'
                elif self.simdflags & IFS_U32F64:
                    mnem += '.u32.f64'
                elif self.simdflags & IFS_U32F32:
                    mnem += '.u32.f32'
                elif self.simdflags & IFS_F64S32:
                    mnem += '.f64.s32'
                elif self.simdflags & IFS_F64U32:
                    mnem += '.f64.u32'
                elif self.simdflags & IFS_F32S32:
                    mnem += '.f32.s32'
                elif self.simdflags & IFS_F32U32:
                    mnem += '.f32.u32'
                elif self.simdflags & IFS_F3264:
                    mnem += '.f32.f64'
                elif self.simdflags & IFS_F6432:
                    mnem += '.f64.f32'
                elif self.simdflags & IFS_F1632:
                    mnem += '.f16.f32'
                elif self.simdflags & IFS_F3216:
                    mnem += '.f32.f16'
                elif self.simdflags & IFS_F64:
                    mnem += '.f64'
                elif self.simdflags & IFS_S64:
                    mnem += '.s64'
                elif self.simdflags & IFS_U64:
                    mnem += '.u64'
                elif self.simdflags & IFS_I64:
                    mnem += '.i64'
                elif self.simdflags & IFS_F32:
                    mnem += '.f32'
                elif self.simdflags & IFS_S32:
                    mnem += '.s32'
                elif self.simdflags & IFS_U32:
                    mnem += '.u32'
                elif self.simdflags & IFS_I32:
                    mnem += '.i32'
                elif self.simdflags & IFS_F16:
                    mnem += '.f16'
                elif self.simdflags & IFS_S16:
                    mnem += '.s16'
                elif self.simdflags & IFS_U16:
                    mnem += '.u16'
                elif self.simdflags & IFS_I16:
                    mnem += '.i16'
                elif self.simdflags & IFS_F8:
                    mnem += '.f8'
                elif self.simdflags & IFS_S8:
                    mnem += '.s8'
                elif self.simdflags & IFS_U8:
                    mnem += '.u8'
                elif self.simdflags & IFS_I8:
                    mnem += '.i8'
                elif self.simdflags & IFS_8:
                    mnem += '.8'
                elif self.simdflags & IFS_16:
                    mnem += '.16'
                elif self.simdflags & IFS_32:
                    mnem += '.32'
                elif self.simdflags & IFS_64:
                    mnem += '.64'

        #FIXME: Advanced SIMD modifiers (IF_V*)
        if self.iflags & IF_THUMB32:
            mnem += ".w"

        mcanv.addNameText(mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in xrange(imax):
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
        elif (daib_flags > 0) & (mnem != "push"):
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
            if self.iflags & IF_T: #removed el
                mnem += 't'

            if self.simdflags:
                if self.simdflags & IFS_S32F64:
                    mnem += '.s32.f64'
                elif self.simdflags & IFS_S32F32:
                    mnem += '.s32.f32'
                elif self.simdflags & IFS_U32F64:
                    mnem += '.u32.f64'
                elif self.simdflags & IFS_U32F32:
                    mnem += '.u32.f32'
                elif self.simdflags & IFS_F64S32:
                    mnem += '.f64.s32'
                elif self.simdflags & IFS_F64U32:
                    mnem += '.f64.u32'
                elif self.simdflags & IFS_F32S32:
                    mnem += '.f32.s32'
                elif self.simdflags & IFS_F32U32:
                    mnem += '.f32.u32'
                elif self.simdflags & IFS_F3264:
                    mnem += '.f32.f64'
                elif self.simdflags & IFS_F6432:
                    mnem += '.f64.f32'
                elif self.simdflags & IFS_F1632:
                    mnem += '.f16.f32'
                elif self.simdflags & IFS_F3216:
                    mnem += '.f32.f16'
                elif self.simdflags & IFS_F64:
                    mnem += '.f64'
                elif self.simdflags & IFS_S64:
                    mnem += '.s64'
                elif self.simdflags & IFS_U64:
                    mnem += '.u64'
                elif self.simdflags & IFS_I64:
                    mnem += '.i64'
                elif self.simdflags & IFS_F32:
                    mnem += '.f32'
                elif self.simdflags & IFS_S32:
                    mnem += '.s32'
                elif self.simdflags & IFS_U32:
                    mnem += '.u32'
                elif self.simdflags & IFS_I32:
                    mnem += '.i32'
                elif self.simdflags & IFS_F16:
                    mnem += '.f16'
                elif self.simdflags & IFS_S16:
                    mnem += '.s16'
                elif self.simdflags & IFS_U16:
                    mnem += '.u16'
                elif self.simdflags & IFS_I16:
                    mnem += '.i16'
                elif self.simdflags & IFS_F8:
                    mnem += '.f8'
                elif self.simdflags & IFS_S8:
                    mnem += '.s8'
                elif self.simdflags & IFS_U8:
                    mnem += '.u8'
                elif self.simdflags & IFS_I8:
                    mnem += '.i8'
                elif self.simdflags & IFS_8:
                    mnem += '.8'
                elif self.simdflags & IFS_16:
                    mnem += '.16'
                elif self.simdflags & IFS_32:
                    mnem += '.32'
                elif self.simdflags & IFS_64:
                    mnem += '.64'

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

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va  # FIXME: is this modified?  or do we need to att # to this?

        if emu == None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None
        emu.setRegister(self.reg, val)

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

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None
        return shifters[self.shtype](emu.getRegister(self.reg), emu.getRegister(self.shreg))

    def render(self, mcanv, op, idx):
        rname = arm_regs[self.reg][0]
        mcanv.addNameText(rname, typename='registers')
        mcanv.addText(', ')
        mcanv.addNameText(shift_names[self.shtype])
        mcanv.addText(' ')
        mcanv.addNameText(arm_regs[self.shreg][0], typename='registers')

    def repr(self, op):
        rname = arm_regs[self.reg][0]+", "
        rname+=shift_names[self.shtype] #Changed to remove extra spaces
        rname+= arm_regs[self.shreg][0]
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

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return shifters[self.shtype](self.va, self.shimm)

        if emu == None:
            return None
        return shifters[self.shtype](emu.getRegister(self.reg), self.shimm)

    def render(self, mcanv, op, idx):
        rname = arm_regs[self.reg][0]
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
        rname = arm_regs[self.reg][0]
        retval = [ rname ]
        if self.shimm != 0:
            retval.append(", "+shift_names[self.shtype])
            retval.append("#%d"%self.shimm)
        elif self.shtype == S_RRX:
            retval.append(shift_names[self.shtype])
        return " ".join(retval)

class ArmImmOper(ArmOperand):
    ''' register operand.  see "addressing mode 1 - data processing operands - immediate" '''


    def __init__(self, val, shval=0, shtype=S_ROR, va=0):
        self.val = val
        self.shval = shval
        self.shtype = shtype

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

    def isDiscrete(self):
        return True

    def getOperValue(self, op, emu=None):
        return shifters[self.shtype](self.val, self.shval)

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addNameText('#0x%.2x' % (val))

    def repr(self, op):
        val = self.getOperValue(op)
        return '#0x%.2x' % (val)

class ArmImmFPOper(ArmImmOper):
    def __init__(self, val, precision=0):
        self.val = val
        self.precision = precision

    def getOperValue(self, op, emu=None):
        return float(self.val)

    def render(self, mcanv, op, idx):
        val = self.getOperValue(op)
        mcanv.addNameText('#%.2f' % (val))

    def repr(self, op):
        val = self.getOperValue(op)
        return '#%.2f' % (val)


class ArmScaledOffsetOper(ArmOperand):
    ''' scaled offset operand.  see "addressing mode 2 - load and store word or unsigned byte - scaled register *" '''
    def __init__(self, base_reg, offset_reg, shtype, shval, va, pubwl=0, psize=4):
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

        b = (self.pubwl >> 2) & 1
        self.tsize = (4,1)[b]
        #print "TESTME: ArmScaledOffsetOper at 0x%x" % va

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

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.readMemValue(addr, self.tsize)

    def setOperValue(self, op, emu=None, val=None):
        # can't survive without an emulator
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        emu.writeMemValue(addr, val, self.tsize)

    def getOperAddr(self, op, emu=None):
        if emu == None:
            return None

        base = emu.getRegister(self.base_reg)

        pom = (-1, 1)[(self.pubwl>>3)&1]
        addval = shifters[self.shtype]( emu.getRegister( self.offset_reg ), self.shval )
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

        if (self.pubwl & 0x2):  # write-back
            if (emu != None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

        if (self.pubwl & 0x10 == 0): # not indexed
            return base

        return addr

    def render(self, mcanv, op, idx):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]
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
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]
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
    def __init__(self, base_reg, offset_reg, va, pubwl=0, psize=4, force_tsize=None):
        self.base_reg = base_reg
        self.offset_reg = offset_reg
        self.pubwl = pubwl
        self.psize = psize

        if force_tsize == None:
            b = (self.pubwl >> 2) & 1
            self.tsize = (4,1)[b]
        else:
            self.tsize = force_tsize

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
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        return emu.readMemValue(addr, self.tsize)

    def getOperAddr(self, op, emu=None):
        if emu == None:
            return None

        pom = (-1, 1)[(self.pubwl>>3)&1]
        base = emu.getRegister( self.base_reg )
        rm = emu.getRegister( self.offset_reg )

        addr = base + (pom*rm) & e_bits.u_maxes[self.psize]

        if (self.pubwl & 0x2):  # write-back
            if (emu != None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

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
    def __init__(self, base_reg, offset, va, pubwl=PUxWL_DFLT, psize=4):
        '''
        psize is pointer-size, since we want to increment base_reg that size when indexing
        tsize is the target size (4 or 1 bytes)
        '''
        self.base_reg = base_reg
        self.offset = offset
        self.pubwl = pubwl
        self.psize = psize
        self.va = va

        b = (pubwl >> 2) & 1
        self.tsize = (4,1)[b]

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
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)
        val &= e_bits.u_maxes[self.tsize]

        emu.writeMemValue(addr, val, self.tsize)

    def getOperValue(self, op, emu=None):
        # can't survive without an emulator
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)

        ret = emu.readMemValue(addr, self.tsize)
        return ret

    def getOperAddr(self, op, emu=None):
        # there are certain circumstances where we can survive without an emulator
        pubwl = self.pubwl >> 3
        u = pubwl & 1
        # if we don't have an emulator, we must be PC-based since we know it
        if self.base_reg == REG_PC:
            base = self.va
        elif emu == None:
            return None
        else:
            base = emu.getRegister(self.base_reg)

        if u:
            addr = (base + self.offset) & e_bits.u_maxes[self.psize]
        else:
            addr = (base - self.offset) & e_bits.u_maxes[self.psize]


        if (self.pubwl & 0x2):  # write-back
            if (emu != None) and (emu.getMeta('forrealz', False)): emu.setRegister( self.base_reg, addr)

        if (self.pubwl & 0x10 == 0): # not indexed
            return base

        return addr

    def render(self, mcanv, op, idx):
        u = (self.pubwl>>3)&1
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg][0]
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
            if value != None:
                mcanv.addText("\t; ")
                if mcanv.mem.isValidPointer(value):
                    name = addrToName(mcanv, value)
                    mcanv.addVaText(name, value)
                else:
                    mcanv.addNameText("0x%x" % value)

            if idxing != 0x2:
                print "OMJ! WRITING to program counter! -1"
        else:
            pom = ('-','')[u]
            mcanv.addText('[')
            mcanv.addNameText(basereg, typename='registers')
            if self.offset == 0:
                mcanv.addText(']')
            else:
                if (idxing&0x10) == 0:
                    mcanv.addText('] ')
                else:
                    mcanv.addText(', ')

                mcanv.addNameText('#%s0x%x' % (pom,self.offset))

                if idxing == 0x10:
                    mcanv.addText(']')
                elif idxing != 0:
                    mcanv.addText(']!')

    def repr(self, op):
        u = (self.pubwl>>3)&1
        idxing = (self.pubwl) & 0x12
        basereg = arm_regs[self.base_reg][0]
        if self.base_reg == REG_PC:
            addr = self.getOperAddr(op)    # only works without an emulator because we've already verified base_reg is PC
            tname = "[#0x%x]" % addr
            # FIXME: is there any chance of us doing indexing on PC?!?
            # ldcl literal trips this in some cases
            if idxing != 0x2:
                print "OMJ! WRITING to the program counter!"
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

    def isDeref(self):
        return False

    def isDiscrete(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.va + self.val

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        if mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addVaText('0x%.8x' % value, value)

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

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        mode = emu.getProcMode()
        if self.psr == PSR_SPSR: # SPSR
            psr = emu.getSPSR(mode)
        else:
            psr = emu.getCPSR()

        return psr

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None
        mode = emu.getProcMode()
        #SPSR does not work - fails in emu.getSPSR
        if self.psr == PSR_SPSR:    # SPSR
            psr = emu.getSPSR(mode)
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setSPSR(mode, newpsr)

        #elif self.psr == PSR_APSR:    # APSR is an alias for CPSR
        #    psr = emu.getCPSR()
        #    newpsr = psr & (~self.mask) | (val & self.mask)
        #    emu.setCPSR(newpsr)

        else:           # CPSR
            psr = emu.getCPSR()
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setCPSR(newpsr)

        return newpsr

    def render(self, mcanv, op, idx):
        field = fields[self.val]
        if field != None:
            psrstr = psrs[self.psr] + '_' + fields[self.val]
        else:
            psrstr = psrs[self.psr]

        mcanv.addNameText(psrstr, typename='registers')

    def repr(self, op):
        field = fields[self.val]
        if field != None:
            return psrs[self.psr] + '_' + fields[self.val]
        return psrs[self.psr]

    
class ArmEndianOper(ArmImmOper):
    def repr(self, op):
        return endian_names[self.val]

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
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

    def isDeref(self):
        return False

    def render(self, mcanv, op, idx):
        mcanv.addText('{')
        regs = [arm_regs[l][0] for l in range(16) if (self.val & (1<<l))]
        for regidx in range(len(regs) - 1):
            reg = regs[regidx]
            mcanv.addNameText(reg, typename='registers')
            mcanv.addText(', ')
        mcanv.addNameText(regs[-1], typename='registers')
        mcanv.addText('}')
        if self.oflags & OF_UM:
            mcanv.addText('^')

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None
        reglist = []
        for regidx in xrange(16):
            #FIXME: check processor mode (abort, system, user, etc... use banked registers?)
            if self.val & (1<<regidx):
                reg = emu.getRegister(regidx)
                reglist.append(reg)
        return reglist

    def repr(self, op):
            #fixed register list. Should be {r1, r2, r3 ..} not { r1 r2 r3 ..}
            s = [ "{" ]
            regs = [arm_regs[l][0] for l in range(16) if (self.val & (1<<l))]
            s.append(', '.join(regs))
            s.append('}')
            if self.oflags & OF_UM:
                s.append('^')
            return "".join(s)
    
class ArmExtRegListOper(ArmOperand):
    def __init__(self, firstreg, count, size):
        self.firstreg = firstreg
        self.count = count
        self.size = size    # 0 or 1, meaning 32bit or 64bit

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.firstreg != oper.firstreg:
            return False
        if self.count != oper.count:
            return False
        if self.size != oper.size:
            return False
        return True

    def isDeref(self):
        return True

    def render(self, mcanv, op, idx):
        regbase = ("S%d", "D%d")[self.size]
        mcanv.addText('{')
        for l in xrange(self.count):
            #vreg = REGS_VECTOR_BASE_IDX + self.firstreg + l
            #mcanv.addNameText(arm_regs[l][0], typename='registers')
            vreg = self.firstreg + l
            mcanv.addNameText(regbase % vreg, typename='registers')
            mcanv.addText(', ')

        mcanv.addText('}')

    def getOperValue(self, op, emu=None):
        '''
        Returns a list of the values in the targeted Extension Registers
        '''
        if emu == None:
            return None
        reglist = []
        for regidx in xrange(self.firstreg, self.firstreg + self.count):
            reg = emu.getRegister(REGS_VECTOR_BASE_IDX + regidx)
            reglist.append(reg)
        return reglist

    def setOperValue(self, op, vals, emu=None):
        '''
        Takes a list of values and places them in the targeted Extension Registers
        '''
        if emu == None:
            return None
        
        base = REGS_VECTOR_BASE_IDX + self.firstreg
        for vidx in range(len(vals)):
            emu.setRegister(base + vidx, vals[vidx])

    def repr(self, op):
        regbase = ("S%d", "D%d")[self.size]
        s = [ "{" ]
        for l in xrange(self.count):
            vreg = self.firstreg + l
            s.append(regbase % vreg)
            s.append(', ')

        s.append('}')
        return " ".join(s)
    
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

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None
        raise Exception("FIXME: Implement ArmPSRFlagsOper.getOperValue() (does it want to be a bitmask? or the actual value according to the PSR?)")
        return None # FIXME

    def repr(self, op):
        return aif_flags[self.flags]

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

    def getOperValue(self, op, emu=None):
        return self.val

    def repr(self, op):
        return "%d"%self.val

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

    def getOperValue(self, op, emu=None):
        return self.val

    def repr(self, op):
        return "p%d"%self.val

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

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None
        raise Exception("FIXME: Implement ArmCoprocRegOper.getOperValue()")
        return None # FIXME

    def repr(self, op):
        return "cr%d"%self.val

class ArmCoprocOption(ArmImmOffsetOper):
    def __init__(self, base_reg, offset, va, pubwl=8):
        self.base_reg = base_reg
        self.offset = offset
        self.pubwl = pubwl
        self.va = va
        b = (pubwl >> 2) & 1
        self.tsize = (4,1)[b]

    def render(self, mcanv, op, idx):
        basereg = arm_regs[self.base_reg][0]
        mcanv.addText('[')
        mcanv.addNameText(basereg, typename='registers')
        mcanv.addVaText('], {%s}' % self.offset)
    def repr(self, op):
        return '[%s], {%s}' % (arm_regs[self.base_reg][0],self.offset)

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

    def getOperValue(self, op, emu=None):
        return None

    def repr(self, op):
        return proc_modes[0x10 | self.mode][PM_SNAME]

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

    def getOperValue(self, op, emu=None):
        return self.val

    def repr(self, op):
        return "#%d"%self.val

class ArmBarrierOption(ArmOperand):
    options = ("","","oshst","osh","","","nshst","nsh","","","ishst","ish","","","st","sy")
    def __init__(self, option):
        self.option = option

    def retOption(self):
        return self.options[self.option]

    def repr(self, op):
        return self.retOption()
        


ENDIAN_LSB = 0
ENDIAN_MSB = 1

class ArmDisasm:
    _optype = envi.ARCH_ARMV7
    _opclass = ArmOpcode
    fmt = None
    #This holds the current running Arm instruction version and mask
    _archVersionMask = ARCH_REVS['ARMv7A']

    def __init__(self, endian=ENDIAN_LSB, mask = 'ARMv7A'):
        self.setArchMask(mask)
        self.setEndian(endian)

    def setArchMask(self, key = 'ARMv7R'):
        ''' set arch version mask '''
        self._archVersionMask = ARCH_REVS.get(key,0)

    def getArchMask(self):
        return self._archVersionMask

    def setEndian(self, endian):
        self.endian = endian
        self.fmt = ("<I", ">I")[endian]

    def getEndian(self):
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

        # since our flags determine how the instruction is decoded later....  
        # performance-wise this should be set as the default value instead of 0, but this is cleaner
        #flags |= envi.ARCH_ARMV7
        # Ok...  if we're a non-conditional branch, *or* we manipulate PC unconditionally,
        # lets call ourself envi.IF_NOFALL
        if cond == COND_AL:                             # FIXME: this could backfire if COND_EXTENDED...
            if opcode in (INS_B, INS_BX):
                flags |= envi.IF_NOFALL

            elif (  len(olist) and 
                    isinstance(olist[0], ArmRegOper) and
                    olist[0].involvesPC() and 
                    (opcode & 0xffff) not in no_update_Rd ):       # FIXME: only want IF_NOFALL if it *writes* to PC!
                
                showop = True
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
            if nexttab != None: # we have to sub-parse...
                for mask,val,penc in nexttab:
                    #print "penc", penc
                    if (opval & mask) == val:
                        enc = penc
                        break

        # If we don't know the encoding by here, we never will ;)
        if enc == None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        #print "ienc_parser index, routine: %d, %s" % (enc, ienc_parsers[enc])
        opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
        return opcode, mnem, olist, flags, simdflags


if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( ArmDisasm() )
