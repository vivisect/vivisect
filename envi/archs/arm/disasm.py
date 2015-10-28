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
# FIXME ldm sp, { pc } seems to not get marked NOFALL
# FIXME ldm sp, { pc } should probably be marked IF_RET too...
# FIXME b lr / bx lr should be marked IF_RET as well!
# FIXME encoding for swi instruction ( <4 cond> 1111 <24 bytes immediate> ) is totally horked (it's in p_uncond)
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
    binary("011100000001"): ("smlad", (0,4,2), 0),
    binary("011100000011"): ("smladx", (0,4,2), 0),
    binary("011100000101"): ("smlsd", (0,4,2), 0),
    binary("011100000111"): ("smlsdx", (0,4,2), 0),
    binary("011101000001"): ("smlald", (0,4,2), 0),
    binary("011101000011"): ("smlaldx", (0,4,2), 0),
    binary("011101000101"): ("smlsld", (0,4,2), 0),
    binary("011101000111"): ("smlsldx", (0,4,2), 0),
    binary("011101010001"): ("smmla", (0,4,2,1), 0),
    binary("011101010011"): ("smmlar", (0,4,2,1), 0),
    binary("011101011101"): ("smmls", (0,4,2,1), 0),
    binary("011101011111"): ("smmlsr", (0,4,2,1), 0),
    binary("011101010001"): ("smmul", (0,4,2), 0),
    binary("011101010011"): ("smmulr", (0,4,2), 0),
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

# FIXME: THIS IS FUGLY but sadly it works
dp_noRn = (13,15)
dp_noRd = (8,9,10,11)

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
    shval = (opval >> 7) & 0x1e   # effectively, rot*2

    if ocode in dp_noRn:# FIXME: FUGLY (and slow...)
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
        iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, dp_mnem[ocode], olist, iflags)

# specialized mnemonics for p_misc
qop_mnem = ('qadd','qsub','qdadd','qdsub')
smla_mnem = ('smlabb','smlabt','smlatb','smlatt',)
smlal_mnem = ('smlalbb','smlalbt','smlaltb','smlaltt',)
smul_mnem = ('smulbb','smulbt','smultb','smultt',)
smlaw_mnem = ('smlawb','smlawt',)
smulw_mnem = ('smulwb','smulwt',)

def p_misc(opval, va):  
    # 0x0f900000 = 0x01000000 or 0x01000010 (misc and misc1 are both parsed at the same time.  see the footnote [2] on dp instructions in the Atmel AT91SAM7 docs
    if   opval & 0x0fc00000 == 0x01000000:
        opcode = (IENC_MISC << 16) + 1
        mnem = 'mrs'
        r = (opval>>22) & 1
        Rd = (opval>>12) & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmPgmStatRegOper(r),
        )
    elif opval & 0x0fb002f0 == 0x01200000:
        opcode = (IENC_MISC << 16) + 2
        mnem = 'msr'        # register.   immediate has it's own parser in the 001 section
        r = (opval>>22) & 1
        Rd = (opval) & 0xf
        olist = (
            ArmPgmStatRegOper(r),
            ArmRegOper(Rd, va=va),
        )
    elif opval & 0x0ff000f0 == 0x01200020:
        opcode = (IENC_MISC << 16) + 5
        mnem = 'bxj'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        
    elif opval & 0x0ff00090 == 0x01000080:
        opcode = (IENC_MISC << 16) + 9
        xy = (opval>>5)&3
        mnem = smla_mnem[xy]
        Rd = (opval>>16) & 0xf
        Rn = (opval>>12) & 0xf 
        Rs = (opval>>8) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
            ArmRegOper(Rn, va=va),
        )
    elif opval & 0x0ff000b0 == 0x01200080:
        opcode = (IENC_MISC << 16) + 10
        y = (opval>>6)&1
        mnem = smlaw_mnem[y]
        Rd = (opval>>16) & 0xf
        Rn = (opval>>12) & 0xf 
        Rs = (opval>>8) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
            ArmRegOper(Rn, va=va),
        )
    elif opval & 0x0ff000b0 == 0x012000a0:
        opcode = (IENC_MISC << 16) + 11
        y = (opval>>6)&1
        mnem = smulw_mnem[y]
        Rd = (opval>>16) & 0xf
        Rs = (opval>>8) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
        )
    elif opval & 0x0ff00090 == 0x01400080:
        opcode = (IENC_MISC << 16) + 12
        xy = (opval>>5)&3
        mnem = smlal_mnem[xy]
        Rdhi = (opval>>16) & 0xf
        Rdlo = (opval>>12) & 0xf 
        Rs = (opval>>8) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rdlo, va=va),
            ArmRegOper(Rdhi, va=va),
            ArmRegOper(Rs, va=va),
            ArmRegOper(Rn, va=va),
        )
    elif opval & 0x0ff00090 == 0x01600080:
        opcode = (IENC_MISC << 16) + 13
        xy = (opval>>5)&3
        mnem = smul_mnem[xy]
        Rd = (opval>>16) & 0xf
        Rs = (opval>>8) & 0xf
        Rm = opval & 0xf
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rs, va=va),
        )
        mnem = 'smul'   #xy
    #elif opval & 0x0fc00000 == 0x03200000:
        #mnem = 'msr'
    else:
        raise envi.InvalidInstruction(
                mesg="p_misc: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction",
        olist = ()
        
    return (opcode, mnem, olist, 0)


#### these actually belong to the media section, and already exist there. FIXME: DELETE
#misc1_mnem = ("pkhbt", "pkhtb", "rev", "rev16", "revsh", "sel", "ssat", "ssat16", "usat", "usat16", )

def p_misc1(opval, va): # 
    #R = (opval>>22) & 1
    #Rn = (opval>>16) & 0xf
    #Rd = (opval>>12) & 0xf
    #rot_imm = (opval>>8) & 0xf
    #imm = opval & 0xff
    #Rm = opval & 0xf
    if opval & 0x0ff000f0 == 0x01200010:
        opcode = INS_BX
        mnem = 'bx'
        Rm = opval & 0xf
        olist = ( ArmRegOper(Rm, va=va), )
        
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

    else:
        raise envi.InvalidInstruction(
                mesg="p_misc1: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)
        
    return (opcode, mnem, olist, 0)



swap_mnem = ("swp","swpb",)
strex_mnem = ("strex","ldrex",)  # actual full instructions
strh_mnem = (("str",IF_H),("ldr",IF_H),)          # IF_H
ldrs_mnem = (("ldr",IF_S|IF_B),("ldr",IF_S|IF_H),)      # IF_SH, IF_SB
ldrd_mnem = (("ldr",IF_D),("str",IF_D),)        # IF_D

def p_extra_load_store(opval, va):
    pubwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    Rs = (opval>>8) & 0xf
    op1 = (opval>>5) & 0x3
    Rm = opval & 0xf
    iflags = 0

    if opval&0x0fb000f0==0x01000090:# swp/swpb
        idx = (pubwl>>2)&1
        opcode = (IENC_EXTRA_LOAD << 16) + idx
        mnem = swap_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmImmOffsetOper(Rn, 0, va, pubwl),
        )
    elif opval&0x0fe000f0==0x01800090:# strex/ldrex
        idx = pubwl&1
        opcode = (IENC_EXTRA_LOAD << 16) + 2 + idx
        mnem = strex_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rm, va=va),
            ArmRegOper(Rn, va=va),
        )
    elif opval&0x0e4000f0==0x000000b0:# strh/ldrh regoffset
        # 000pu0w0-Rn--Rt-SBZ-1011-Rm-  - STRH
        # 0000u110-Rn--Rt-imm41011imm4  - STRHT (v7+)
        idx = pubwl&1
        opcode = (IENC_EXTRA_LOAD << 16) + 4 + idx
        mnem,iflags = strh_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl),
        )
    elif opval&0x0e4000f0==0x004000b0:# strh/ldrh immoffset
        idx = pubwl&1
        opcode = (IENC_EXTRA_LOAD << 16) + 6 + idx
        mnem,iflags = strh_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn,(Rs<<4)+Rm, va, pubwl),
        )
    elif opval&0x0e5000d0==0x005000d0:# ldrsh/b immoffset
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 8 + idx
        mnem,iflags = ldrs_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl),
        )
    elif opval&0x0e5000d0==0x001000d0:# ldrsh/b regoffset
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 10 + idx
        mnem,iflags = ldrs_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl),
        )
    elif opval&0x0e5000d0==0x000000d0:# ldrd/strd regoffset
        # 000pu0w0-Rn--Rt-SBZ-1101-Rm-  ldrd regoffset
        # 0001u1001111-Rt-imm41101imm4  ldrd regoffset (literal, v7+)
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 12 + idx
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOffsetOper(Rn, Rm, va, pubwl),
        )
    elif opval&0x0e5000d0==0x004000d0:# ldrd/strd immoffset
        idx = (opval>>5)&1
        opcode = (IENC_EXTRA_LOAD << 16) + 14 + idx
        mnem,iflags = ldrd_mnem[idx]
        olist = (
            ArmRegOper(Rd, va=va),
            ArmImmOffsetOper(Rn, (Rs<<4)+Rm, va, pubwl),
        )
    else:
        raise envi.InvalidInstruction(
                mesg="extra_load_store: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)

    return (opcode, mnem, olist, iflags)


def p_dp_reg_shift(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    Rm = opval & 0xf
    shtype = (opval >> 5) & 0x3
    Rs = (opval >> 8) & 0xf

    if ocode in dp_noRn:# FIXME: FUGLY
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
        iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, dp_mnem[ocode], olist, iflags)

multfail = (None, None, None,)
def p_mult(opval, va):
    ocode, vals = chopmul(opval)
                             
    mnem, opindexes, flags = iencmul_codes.get(ocode, multfail)
    if mnem == None:
        raise envi.InvalidInstruction(
                mesg="p_mult: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)

    olist = []
    for i in opindexes:
        olist.append(ArmRegOper(vals[i], va=va))

    opcode = (IENC_MULT << 16) + ocode
    return (opcode, mnem, olist, flags)

def p_dp_imm(opval, va):
    ocode,sflag,Rn,Rd = dpbase(opval)
    imm = opval & 0xff
    rot = (opval >> 7) & 0x1e   # effectively, rot*2
    
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
        iflags = IF_PSR_S
    else:
        iflags = 0
    return (opcode, dp_mnem[ocode], olist, iflags)

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
        
    return (opcode, mnem, olist, 0)

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

        if mask & 3:    # USER mode these will be 0
            iflags |= IF_SYS_MODE
        
        olist = (
            ArmPgmStatRegOper(r, mask),
            ArmImmOper(immed),
        )
    
    return (opcode, mnem, olist, iflags)
    
ldr_mnem = ("str", "ldr")
tsizes = (4, 1,)
def p_load_imm_off(opval, va):
    pubwl = (opval>>20) & 0x1f
    Rn = (opval>>16) & 0xf
    Rd = (opval>>12) & 0xf
    imm = opval & 0xfff

    if pubwl & 4:   # B   
        iflags = IF_B
        if (pubwl & 0x12) == 2:
            iflags |= IF_T
    else:
        iflags = 0

    olist = (
        ArmRegOper(Rd, va=va),
        ArmImmOffsetOper(Rn, imm, va, pubwl=pubwl)    # u=-/+, b=word/byte
    )
    
    opcode = (IENC_LOAD_IMM_OFF << 16)
    return (opcode, ldr_mnem[pubwl&1], olist, iflags)

def p_load_reg_off(opval, va):
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
        ArmScaledOffsetOper(Rn, Rm, shtype, shval, va, pubwl),  # u=-/+, b=word/byte
    )
    
    opcode = (IENC_LOAD_REG_OFF << 16) 
    return (opcode, ldr_mnem[pubwl&1], olist, iflags)

    
def p_media(opval, va):
    """
    27:20, 7:4
    """
    # media is a parent for the following:
    #  parallel add/sub                         01100
    #  pkh, ssat, ssat16, usat, usat16, sel     01101
    #  rev, rev16, revsh                        01101
    #  smlad, smlsd, smlald, smusd              01110
    #  usad8, usada8                            01111
    definer = (opval>>23) & 0x1f
    if   definer == 0xc:
        return p_media_parallel(opval, va)
    elif definer == 0xd:
        return p_media_pack_sat_rev_extend(opval, va)
    elif definer == 0xe:
        return p_mult(opval, va)
        return p_media_smul(opval, va)
    else:
        return p_media_usada(opval, va)

#generate mnemonics for parallel instructions (could do manually like last time...)
parallel_mnem = []
par_suffixes = ("add16", "addsubx", "subaddx", "sub16", "add8", "sub8", "", "")
par_prefixes = ("","s","q","sh","","u","uq","uh")
for pre in par_prefixes:
    for suf in par_suffixes:
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
    return (opcode, mnem, olist, 0)


xtnd_mnem = []
xtnd_suffixes = ("xtab16","xtab","xtah","xtb16","xtb","xth",)
xtnd_prefixes = ("s","u")
for pre in xtnd_prefixes:
    for suf in xtnd_suffixes:
        xtnd_mnem.append(pre+suf)
        
xtnd_mnem = tuple(xtnd_mnem)

pkh_mnem = ('pkhbt', 'pkhtb',)
sat_mnem = ('ssat','usat')
sat16_mnem = ('ssat16','usat16')    
rev_mnem = ('rev','rev16',None,'revsh',)

def p_media_pack_sat_rev_extend(opval, va):
    ## part of p_media
    # assume bit 23 == 1
    opc1 = (opval>>20) & 7
    opc2 = (opval>>4) & 0xf
    opc25 = opc2 & 3
    opcode = 0
    
    if opc1 == 0 and opc25 == 1:   #pkh
        idx = (opval>>6)&1
        mnem = pkh_mnem[idx]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        shift_imm = (opval>>7) & 0x1f
        Rm = opval & 0xf

        opcode = IENC_MEDIA_PACK + idx
        
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegShiftImmOper(Rm, S_LSL, shift_imm, va),
        )

    elif (opc1 & 2) and opc25 == 1: #word sat
        opidx = (opval>>22)&1
        sat_imm = 1 + (opval>>16) & 0xf
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
            shift_imm = (opval>>7) & 0x1f
            sh = (opval>>5) & 2
            olist = (
                ArmRegOper(Rd, va=va),
                ArmImmOper(sat_imm),
                ArmRegShiftImmOper(Rm, sh, shift_imm, va),
            )
            opcode = IENC_MEDIA_SAT + 2 + opidx
            
    elif (opc1 & 3) == 2 and opc2 == 3:     #parallel half-word sat
        # FIXME: implement this instruction!
        raise envi.InvalidInstruction(
                mesg="WTF! Parallel Half-Word Saturate...  what is that instruction?",
                bytez=struct.pack("<I", opval), va=va)
    
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
        mnem = xtnd_mnem[opc1]
        Rn = (opval>>16) & 0xf
        Rd = (opval>>12) & 0xf
        rot = (opval>>10) & 3
        Rm = opval & 0xf
        
        olist = (
            ArmRegOper(Rd, va=va),
            ArmRegOper(Rn, va=va),
            ArmRegShiftImmOper(Rm, S_ROR, rot, va),
        )
        opcode = IENC_MEDIA_EXTEND + opc1
    else:
        raise envi.InvalidInstruction(
                mesg="p_media_extend: invalid instruction",
                bytez=struct.pack("<I", opval), va=va)

    return (opcode, mnem, olist, 0)

#smult3_mnem = ('smlad','smlsd',,,'smlald')
def p_media_smul(opval, va):
    raise envi.InvalidInstruction(
            mesg="Should not reach here.  If we reach here, we'll have to implement MEDIA_SMUL extended multiplication (type 3)",
            bytez=struct.pack("<I", opval), va=va)
    # hmmm, is this already handled?
    
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

    return (opcode, mnem, olist, 0)

def p_arch_undef(opval, va):
    print ("p_arch_undef: invalid instruction (by definition in ARM spec): %.8x:\t%.8x"%(va,opval))
    raise envi.InvalidInstruction(
            mesg="p_arch_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
    return (IENC_ARCH_UNDEF, 'arch undefined', (ArmImmOper(opval),), 0)

ldm_mnem = ("stm", "ldm")

def p_load_mult(opval, va):
    puswl = (opval>>20) & 0x1f
    mnem_idx = puswl & 1
    mnem = ldm_mnem[(mnem_idx)]
    flags = ((puswl>>3)<<(IF_DAIB_SHFT)) | IF_DA     # store bits for decoding whether to dec/inc before/after between ldr/str.  IF_DA tells the repr to print the the DAIB extension after the conditional.  right shift necessary to clear lower three bits, and align us with IF_DAIB_SHFT
    Rn = (opval>>16) & 0xf
    reg_list = opval & 0xffff
    
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
    return (opcode, mnem, olist, flags)

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
    return (opcode, b_mnem[link], olist, flags)

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

    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocRegOper(CRd),
        ArmImmOffsetOper(Rn, offset*4, va, pubwl=punwl),
    )
    
    opcode = (IENC_COPROC_LOAD << 16)
    return (opcode, ldc_mnem[punwl&1], olist, iflags)

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
    return (opcode, mnem, olist, 0)
    
cdp_mnem = ["cdp" for x in range(15)]
cdp_mnem.append("cdp2")

def p_coproc_dp(opval, va):
    opcode1 = (opval>>20) & 0xf
    CRn = (opval>>16) & 0xf
    CRd = (opval>>12) & 0xf
    cp_num = (opval>>8) & 0xf
    opcode2 = (opval>>5) & 0x7
    CRm = opval & 0xf
    mnem = cdp_mnem[opval>>28]

    olist = (
        ArmCoprocOper(cp_num),
        ArmCoprocOpcodeOper(opcode1),
        ArmCoprocRegOper(CRd),
        ArmCoprocRegOper(CRn),
        ArmCoprocRegOper(CRm),
        ArmCoprocOpcodeOper(opcode2),
    )
    
    opcode = (IENC_COPROC_DP << 16)
    return (opcode, mnem, olist, 0)       #FIXME: CDP2 (cond = 0b1111) also needs handling.

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
    return (opcode, mcr_mnem[load], olist, 0)

def p_swint(opval, va):
    swint = opval & 0xffffff
    
    olist = ( ArmImmOper(swint), )
    opcode = IENC_SWINT << 16 + 1
    return (opcode, "swi", olist, 0)

cps_mnem = ("cps","cps FAIL-bad encoding","cpsie","cpsid")
mcrr2_mnem = ("mcrr2", "mrrc2")
ldc2_mnem = ("stc2", "ldc2",)
mcr2_mnem = ("mcr2", "mrc2")
def p_uncond(opval, va):

    if opval & 0x0f000000 == 0x0f000000:
        # FIXME THIS IS HORKED
        opcode = IENC_SWINT << 16 + 2
        immval = opval & 0x00ffffff
        return (opcode, 'swi', (ArmImmOper(immval),), 0)

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
            return (opcode, mnem, olist, 0)
        elif (opval & 0xffff00f0) == 0xf1010000:
            #setend
            e = (opval>>9) & 1
            mnem = "setend"
            olist = ( ArmEndianOper(e), )
            opcode = IENC_UNCOND_SETEND
            return (opcode, mnem, olist, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=0): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    elif optop == 1:
        if (opval & 0xf570f000) == 0xf550f000:
            #cache preload  -  also known as a nop on most platforms... does nothing except prefetch instructions from cache.
            # i'm tempted to cut the parsing of it and just return a canned something.
            mnem = "pld"
            I = (opval>>25) & 1     # what the freak am i supposed to do with "i"???
            Rn = (opval>>16) & 0xf
            U = (opval>>23) & 1
            opcode = IENC_UNCOND_PLD
            if I:
                immoffset = opval & 0xfff
                olist = (ArmImmOffsetOper(Rn, immoffset, va, U<<3),)
            else:
                Rm = opval & 0xf
                shtype = (opval>>5) & 3
                shval = (opval>>7) & 0x1f
                olist = (ArmScaledOffsetOper(Rn, Rm, shtype, shval, va, pubwl), )
            return (opcode, mnem, olist, 0)
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
            if pu_w_ & 2:    # base_reg writeback
                flags |= IF_W
           
            # base_reg = R13
            # reg_list = R14 and SPSR
            olist = (
                #ArmRegListOper(reg_list, pu_w_),
                ArmModeOper(mode, (pu_w_>>1)&1),
            )
            opcode = IENC_UNCOND_SRS
            return (opcode, mnem, olist, flags)
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
            return (opcode, mnem, olist, flags)

        elif (opval & 0xfe000000) == 0xfa000000:
            #blx
            mnem = "blx"
            h = (opval>>23) & 2
            imm_offset = e_bits.signed(opval, 3) + h
            
            olist = (
                ArmPcOffsetOper(imm_offset, va),
            )
            
            opcode = INS_BLX           #should this be IENC_UNCOND_BLX?
            return (opcode, mnem, olist, 0)
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
            return (opcode, mnem, olist, 0)
            
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
                ArmImmOffsetOper(Rn, offset*4, va, pubwl=punwl),
            )
            
            opcode = (IENC_COPROC_LOAD << 16)
            return (opcode, ldc2_mnem[punwl&1], olist, iflags)

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
            return (opcode, mcr2_mnem[load], olist, 0)
        else:
            raise envi.InvalidInstruction(
                    mesg="p_uncond (ontop=3): invalid instruction",
                    bytez=struct.pack("<I", opval), va=va)
    
####################################################################
# Table of the parser functions
ienc_parsers_tmp = [None for x in range(21)]

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
ienc_parsers_tmp[IENC_MEDIA] =   p_media
ienc_parsers_tmp[IENC_LOAD_MULT] =   p_load_mult
ienc_parsers_tmp[IENC_BRANCH] =   p_branch
ienc_parsers_tmp[IENC_COPROC_RREG_XFER] = p_coproc_dbl_reg_xfer
ienc_parsers_tmp[IENC_COPROC_LOAD] =   p_coproc_load
ienc_parsers_tmp[IENC_COPROC_DP] =   p_coproc_dp
ienc_parsers_tmp[IENC_COPROC_REG_XFER] =   p_coproc_reg_xfer
ienc_parsers_tmp[IENC_SWINT] =    p_swint
ienc_parsers_tmp[IENC_UNCOND] = p_uncond

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
    (0b00001111101100000000000000000000, 0b00000011001000000000000000000000, IENC_MOV_IMM_STAT),
    (0b00001110000000000000000000000000, 0b00000010000000000000000000000000, IENC_DP_IMM),
    (0, 0, IENC_UNDEF),
)

s_3_table = (
    (0b00000001111100000000000011110000, 0b00000001111100000000000011110000, IENC_ARCH_UNDEF),
    (0b00000000000000000000000000010000, 0b00000000000000000000000000010000, IENC_MEDIA),
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
    (IENC_UNCOND, None),
]

# FIXME for emulation...
#def s_lsl(val, shval):
    #pass

#def s_lsr(val, shval):
    #pass

# These are indexed by the 2 bit "shift" value in some DP encodings
#shift_handlers = (
    #s_lsl,
    #s_lsr,
    #s_asr,
    #s_ror,
#)

endian_names = ("le","be")

#FIXME IF_NOFALL (and other envi flags)

class ArmOpcode(envi.Opcode):
    _def_arch = envi.ARCH_ARMV7

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

        if not self.iflags & envi.IF_NOFALL:
            ret.append((self.va + self.size, envi.BR_FALL | self._def_arch))

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
                    flags |= envi.ARCH_ARM

            # if we don't know that it's thumb, default to "ARCH_DEFAULT"
            else:
                flags |= self._def_arch


            #operval &= 0xfffffffe           # this has to work for both arm and thumb
            if self.iflags & envi.IF_CALL:
                flags |= envi.BR_PROC
            ret.append((operval, flags))

        return ret

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        mnem = self.mnem + cond_codes.get(self.prefixes)
        daib_flags = self.iflags & IF_DAIB_MASK
        if self.iflags & IF_L:
            mnem += 'l'
        elif self.iflags & IF_PSR_S:
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
            elif self.iflags & IF_T:
                mnem += 't'
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
        elif self.iflags & IF_PSR_S:
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
            elif self.iflags & IF_T:
                mnem += 't'
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
        rname = arm_regs[self.reg][0]
        mcanv.addNameText(rname, typename='registers')
        if self.oflags & OF_W:
            mcanv.addText( "!" )


    def repr(self, op):
        rname = arm_regs[self.reg][0]
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
        return shifters[self.shtype](emu.getRegister(self.reg), emu.getRegister(shreg))

    def render(self, mcanv, op, idx):
        rname = arm_regs[self.reg][0]
        mcanv.addNameText(rname, typename='registers')
        mcanv.addText(', ')
        mcanv.addNameText(shift_names[self.shtype])
        mcanv.addText(' ')
        mcanv.addNameText(arm_regs[self.shreg][0], typename='registers')

    def repr(self, op):
        rname = arm_regs[self.reg][0]+","
        return " ".join([rname, shift_names[self.shtype], arm_regs[self.shreg][0]])

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


class ArmScaledOffsetOper(ArmOperand):
    ''' scaled offset operand.  see "addressing mode 2 - load and store word or unsigned byte - scaled register *" '''
    def __init__(self, base_reg, offset_reg, shtype, shval, va, pubwl=0):
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
        self.va = va

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
        return True

    def involvesPC(self):
        return self.base_reg == 15

    def isDeref(self):
        return True

    def getOperValue(self, op, emu=None, writeback=False):
        if emu == None:
            return None

        retval = 0

        addr = self.getOperAddr( op, emu )
        rn = emu.getRegister( self.base_reg )
        # FIXME: THIS IS COMPLETELY BORKED AND WRONG!
        # if pre-indexed, we incremement/decrement the register before determining the OperAddr
        if (self.pubwl & 0x12 == 0x12):
            # pre-indexed...
            if writeback: emu.setRegister( self.base_reg, addr )
            return emu.readMemValue(addr, self.tsize)

        elif (self.pubwl & 0x12 == 0):
            # post-indexed... still write it but return the original value
            if writeback: emu.setRegister( self.base_reg, addr )
            return emu.readMemValue(addr, self.tsize)

        # plain jane just return the calculated address... no updates are necessary
        return addr



    def getOperAddr(self, op, emu=None):
        if emu == None:
            return None

        if self.basereg == REG_PC:
            addr = self.va
        elif emu != None:
            addr = emu.getRegister(self.basereg)
        else:
            return None

        addval = shifters[self.shtype]( emu.getRegister( self.offset_reg ), self.shval )
        # if U==0, subtract
        addval *= (-1, 1)[(self.pubwl>>3)&1]

        return addr + addval


    def render(self, mcanv, op, idx):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]
        shname = shift_names[self.shtype]

        mcanv.addText('[')
        mcanv.addNameText(basereg, typename='registers')
        if (idxing&0x10) == 0:
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
        if idxing == 0x10:
            mcanv.addText(']')
        elif idxing != 0:
            mcanv.addText(']!')

    def repr(self, op):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]
        shname = shift_names[self.shtype]
        if self.shval != 0:
            shval = "%s #%d"%(shname,self.shval)
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
    def __init__(self, base_reg, offset_reg, va, pubwl=0):
        self.base_reg = base_reg
        self.offset_reg = offset_reg
        self.pubwl = pubwl

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset_reg != oper.offset_reg:
            return False
        if self.pubwl != oper.pubwl:
            return False
        return True

    def involvesPC(self):
        return self.base_reg == 15

    def isDeref(self):
        return True

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        rn = emu.getRegister( self.base_reg )
        addr = self.getOperAddr( op, emu, rn )

        # if pre-indexed, we incremement/decrement the register before determining the OperAddr
        if (self.pubwl & 0x12 == 0x12):
            # pre-indexed...
            if writeback: emu.setRegister( self.base_reg, addr )
            return addr

        elif (self.pubwl & 0x12 == 0):
            # post-indexed... still write it but return the original value
            if writeback: emu.setRegister( self.base_reg, addr )
            return rn

        # plain jane just return the calculated address... no updates are necessary
        return addr


    def getOperAddr(self, op, emu=None, rn=None):
        if emu == None:
            return None

        if rn == None:
            rn = emu.getRegister( self.base_reg )

        rm = emu.getRegister( self.offset_reg )

        return rn + rm



    def render(self, mcanv, op, idx):
        pom = ('-','')[(self.pubwl>>3)&1]
        idxing = self.pubwl & 0x12
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]

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
        basereg = arm_regs[self.base_reg][0]
        offreg = arm_regs[self.offset_reg][0]
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
    def __init__(self, base_reg, offset, va, pubwl=8):
        self.base_reg = base_reg
        self.offset = offset
        self.pubwl = pubwl
        self.va = va

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset != oper.offset:
            return False
        if self.pubwl != oper.pubwl:
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

        pubwl = self.pubwl >> 2
        b = pubwl & 1

        addr = self.getOperAddr(op, emu)

        fmt = ("<I", "B")[b]
        emu.writeMemoryFormat(addr, fmt, val)

    def getOperValue(self, op, emu=None):
        # can't survive without an emulator
        if emu == None:
            return None

        pubwl = self.pubwl >> 2
        b = pubwl & 1

        addr = self.getOperAddr(op, emu)

        fmt = ("<I", "B")[b]
        ret, = emu.readMemoryFormat(addr, fmt)
        return ret

    def getOperAddr(self, op, emu=None):
        # there are certain circumstances where we can survive without an emulator
        pubwl = self.pubwl >> 3
        u = pubwl & 1

        # if we don't have an emulator, we must be PC-based since we know it
        if self.base_reg == REG_PC:
            addr = self.va
        elif emu == None:
            return None
        else:
            addr = emu.getRegister(self.base_reg)

        if u:
            addr += self.offset
        else:
            addr -= self.offset

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

            # FIXME: is there any chance of us doing indexing on PC?!?
            if idxing != 0x10:
                print "OMJ! indexing on the program counter!"
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
            if idxing != 0x10:
                print "OMJ! indexing on the program counter!"
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
        tname = "#0x%.8x" % targ
        return tname


psrs = ("CPSR", "SPSR", 'inval', 'inval', 'inval', 'inval', 'inval', 'inval',)
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
        if self.psr: # SPSR
            psr = emu.getSPSR(mode)
        else:
            psr = emu.getCPSR()

        return psr

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None
        mode = emu.getProcMode()
        if self.psr:    # SPSR
            psr = emu.getSPSR(mode)
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setSPSR(mode, newpsr)

        else:           # CPSR
            psr = emu.getCPSR()
            newpsr = psr & (~self.mask) | (val & self.mask)
            emu.setCPSR(newpsr)

        return newpsr

    def repr(self, op):
        return psrs[self.psr] + '_' + fields[self.val]
    
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
        return self.val & 0x80 == 0x80

    def isDeref(self):
        return False

    def render(self, mcanv, op, idx):
        mcanv.addText('{')
        for l in xrange(16):
            if self.val & 1<<l:
                mcanv.addNameText(arm_regs[l][0], typename='registers')
                mcanv.addText(', ')
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
            s = [ "{" ]
            for l in xrange(16):
                if (self.val & (1<<l)):
                    s.append(arm_regs[l][0])
            s.append('}')
            if self.oflags & OF_UM:
                s.append('^')
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
        return "c%d"%self.val

class ArmModeOper(ArmOperand):
    def __init__(self, mode, writeback=False):
        self.mode = mode
        self.writeback = writeback

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.mode != oper.mode:
            return False
        if self.writeback != oper.writeback:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        return None

    def repr(self, op):
        return (proc_modes % self.mode)[PM_SNAME]

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


ENDIAN_LSB = 0
ENDIAN_MSB = 1

class ArmDisasm:
    fmt = None
    def __init__(self, endian=ENDIAN_LSB):
        self.setEndian(endian)
        
    def setEndian(self, endian):
        self.fmt = ("<I", ">I")[endian]

    def disasm(self, bytez, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        opbytes = bytez[offset:offset+4]
        opval, = struct.unpack(self.fmt, opbytes)
        
        cond = opval >> 28

        # Begin the table lookup sequence with the first 3 non-cond bits
        encfam = (opval >> 25) & 0x7
        if cond == COND_EXTENDED:
            enc = IENC_UNCOND

        else:

            enc,nexttab = inittable[encfam]
            if nexttab != None: # we have to sub-parse...
                for mask,val,penc in nexttab:
                    if (opval & mask) == val:
                        enc = penc
                        break

        # If we don't know the encoding by here, we never will ;)
        if enc == None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        opcode, mnem, olist, flags = ienc_parsers[enc](opval, va+8)

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
        op = ArmOpcode(va, opcode, mnem, cond, 4, olist, flags)
        op.encoder = enc    #FIXME: DEBUG CODE

        return op

if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain( ArmDisasm() )
