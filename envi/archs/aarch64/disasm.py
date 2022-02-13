'''
A disasm file for the AArch64 Architecture, ARMv8.
'''
from envi.archs.aarch64.const import *
from envi.archs.aarch64.regs import *
import envi
import struct
import envi.bits as e_bits

#-----------------------------data-----------------------------------------|

'''
All the various tables inittable references
'''
s_0_table = (   # undefined and unallcated
    (0b11111111111111110000000000000000, 0b00000000000000000000000000000000, IENC_RESERVED),
    (0,0,IENC_UNDEF),#catch-all
)

s_4_table = (   # loads and stores
    (0b00111111000000000000000000000000, 0b00001000000000000000000000000000, IENC_LS_EXCL),
    (0b00111111100000000000000000000000, 0b00101000000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
    (0b00111111100000000000000000000000, 0b00101000100000000000000000000000, IENC_LS_REGPAIR_POSTI),
    (0b00111111100000000000000000000000, 0b00101001000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
    (0b00111111100000000000000000000000, 0b00101001100000000000000000000000, IENC_LS_REGPAIR_PREI),
    (0,0,IENC_UNDEF),#catch-all
)

s_5_table = (   # data processing - registers
    (0b00011111000000000000000000000000, 0b00001010000000000000000000000000, IENC_LOG_SHFT_REG),
    (0b00011111001000000000000000000000, 0b00001011000000000000000000000000, IENC_ADDSUB_SHFT_REG),
    (0b00011111001000000000000000000000, 0b00001011001000000000000000000000, IENC_ADDSUB_EXT_REG),
    (0,0, IENC_UNDEF),#catch-all
)

s_6_table = (   # loads and stores
    (0b10111111101111110000000000000000, 0b00001100000000000000000000000000, IENC_SIMD_LS_MULTISTRUCT),
    (0b10111111101000000000000000000000, 0b00001100100000000000000000000000, IENC_SIMD_LS_MULTISTRUCT_POSTI),
    (0b10111111100111110000000000000000, 0b00001100000000000000000000000000, IENC_SIMD_LS_ONESTRUCT),
    (0b10111111100000000000000000000000, 0b00001100000000000000000000000000, IENC_SIMD_LS_ONESTRUCT_POSTI),
    (0b00111111100000000000000000000000, 0b00101100000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
    (0b00111111100000000000000000000000, 0b00101100100000000000000000000000, IENC_LS_REGPAIR_POSTI),
    (0b00111111100000000000000000000000, 0b00101101000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
    (0b00111111100000000000000000000000, 0b00101101100000000000000000000000, IENC_LS_REGPAIR_PREI),
    (0,0,IENC_UNDEF), #catch-all
)

s_8_table = (   # data processing - immediates
    (0b00011111000000000000000000000000, 0b00010000000000000000000000000000, IENC_PC_ADDR),
    (0b00011111000000000000000000000000, 0b00010001000000000000000000000000, IENC_ADDSUB_IMM),
    (0b00011111100000000000000000000000, 0b00010000000000000000000000000000, IENC_LOG_IMM),
    (0b00011111100000000000000000000000, 0b00010000100000000000000000000000, IENC_MOV_WIDE_IMM),
    (0,0,IENC_UNDEF), #catch-all
)

s_9_table = (   # data processing - immediates
    (0b00011111100000000000000000000000, 0b00010010000000000000000000000000, IENC_LOG_IMM),
    (0b00011111100000000000000000000000, 0b00010010100000000000000000000000, IENC_MOV_WIDE_IMM),
    (0b00011111100000000000000000000000, 0b00010011000000000000000000000000, IENC_BITFIELD),
    (0b00011111100000000000000000000000, 0b00010011100000000000000000000000, IENC_EXTRACT),
    (0b11111111110000000000000000000000, 0b11010011000000000000000000000000, IENC_SYS),
    (0,0,IENC_UNDEF),#catch-all
)

s_a_table = (   # branches, exception generating and system instructions
    (0b01111110000000000000000000000000, 0b00110100000000000000000000000000, IENC_CMP_BRANCH_IMM),
    (0b01111110000000000000000000000000, 0b00010100000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
    (0b11111110000000000000000000000000, 0b01010100000000000000000000000000, IENC_BRANCH_COND_IMM),
    (0b11111111000000000000000000000000, 0b11010100000000000000000000000000, IENC_EXCP_GEN),
    (0b11111111110000000000000000000000, 0b11010101000000000000000000000000, IENC_SYS),
    (0,0,IENC_UNDEF),#catch-all
)

s_b_table = (   # branches, exception generating and system instructions
    (0b01111110000000000000000000000000, 0b00110110000000000000000000000000, IENC_TEST_BRANCH_IMM),
    (0b11111110000000000000000000000000, 0b11010110000000000000000000000000, IENC_BRANCH_UNCOND_REG),
    (0b01111110000000000000000000000000, 0b00010110000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
    (0,0,IENC_UNDEF),#catch-all
)

s_ce_table = (  # loads and stores
    (0b00111011000000000000000000000000, 0b00011000000000000000000000000000, IENC_LOAD_REG_LIT),
    (0b00111011000000000000000000000000, 0b00111001000000000000000000000000, IENC_LS_REG_US_IMM),
    (0b00111011001000000000110000000000, 0b00111000000000000000000000000000, IENC_LS_REG_UNSC_IMM),
    (0b00111011001000000000110000000000, 0b00111000000000000000010000000000, IENC_LS_REG_IMM_POSTI),
    (0b00111011001000000000110000000000, 0b00111000000000000000100000000000, IENC_LS_REG_UNPRIV),
    (0b00111011001000000000110000000000, 0b00111000000000000000110000000000, IENC_LS_REG_IMM_PREI),
    (0b00111011001000000000110000000000, 0b00111000001000000000100000000000, IENC_LS_REG_OFFSET),
    (0,0,IENC_UNDEF),#catch-all
)

s_d_table = (   # data processing - registers
    (0b00011111111000000000000000000000, 0b00011010000000000000000000000000, IENC_ADDSUB_CARRY),
    (0b00011111111000000000100000000000, 0b00011010010000000000000000000000, IENC_COND_CMP_REG),
    (0b00011111111000000000100000000000, 0b00011010010000000000100000000000, IENC_COND_CMP_IMM),
    (0b00011111111000000000000000000000, 0b00011010100000000000000000000000, IENC_COND_SEL),
    (0b00011111000000000000000000000000, 0b00011011000000000000000000000000, IENC_DATA_PROC_3),
    (0b01011111111000000000000000000000, 0b00011010110000000000000000000000, IENC_DATA_PROC_2),
    (0b01011111111000000000000000000000, 0b01011010110000000000000000000000, IENC_DATA_PROC_1),
    (0,0,IENC_UNDEF),#catch-all
)

#Init table to help us find encfam. Either returns an enc, or a mask-val table with an enc
inittable = (
    ( None, s_0_table ), #0 - reserved
    ( None, None ), #1
    ( None, None ), #2 - future home of SVE decoding
    ( None, None ), #3
    ( None, s_4_table ), #4
    ( None, s_5_table ), #5
    ( None, s_6_table ), #6
    (IENC_DATA_SIMD, None), #7
    ( None, s_8_table ), #8
    ( None, s_9_table ), #9
    ( None, s_a_table ), #a
    ( None, s_b_table ), #b
    ( None, s_ce_table ), #c
    ( None, s_d_table ), #d
    ( None, s_ce_table ), #e
    (IENC_DATA_SIMD, None), #f
)

#--------------------instruction parsing functions----------------------------|

def p_udf(opval, va):
    if opval & 0xffff0000 == 0:
        return INS_UDF, 'udf', (), envi.IF_NOFALL, 0
   
    p_undef(opval, va)


def p_pc_addr(opval,va):
    '''
    Get the A64Opcode parameters for a PC release address instruction
    '''
    op = opval >> 31
    rd = opval & 0xf
    immhi = opval >> 5 & 0x3ffff
    immlo = opval >> 29 & 0x3
    #Both instructions share the mnemonic 'adr', but if op == 1
    #then mnemonic becomes 'adrp' via iflag IF_P
    mnem = 'adr'
    opcode = INS_ADR
    if op == 1:
        iflag = IF_P
    else:
        iflag = 0
    olist = (
        A64RegOper(rd, va=va, size=8),
        A64ImmOper((immhi + immlo), va=va)
    )


    return opcode, mnem, olist, iflag, 0

def p_addsub_imm(opval, va):
    '''
    Get the A64Opcode parameters for an Add/Subtract (immediate) instruction
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    shift = opval >> 22 & 0x3
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    imm = opval >> 10 & 0xfff
    #all mnemonics are either add or sub, depending on op's value
    if op == 0b0:
        mnem = 'add'
        opcode = INS_ADD
    else:
        mnem = 'sub'
        opcode = INS_SUB
    #if the value of s is 1, then the iflag should be set to PSR_S, becoming adds or subs
    if s == 0b0:
        iflag = 0
    else:
        iflag |= IF_PSR_S
    #if shift's value is 01, set shift amount to 12. else, shift is either
        #explicitly assigned to 0 (shift = 00) or defaults to 0 (shift = 1x)
    if shift == 0b01:
        shiftX = 12
    else:
        shiftX = 0
    #sf determines whether the register size corresponds to the 32 or 64-bit variant
    if sf == 0b0:
        size = 4
        rd += meta_reg_bases[size]
        rn += meta_reg_bases[size]
    else:
        size = 8
    olist = (
        A64RegOper(rd, va=va, size=size),
        A64RegOper(rn, va=va, size=size),
        A64ImmOper(imm, shiftX, S_LSL, va)
    )        
    return opcode, mnem, olist, iflag, 0

def p_log_imm(opval, va):
    '''
    Get the A64Opcode parameters for a logical (immediate) instruction
    '''
    iflags = 0
    sf = opval >> 31
    opc = opval >> 29 & 0x3
    n = opval >> 22
    immr = opval >> 16 & 0x3f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f


    #depending on whether opc is equal to 0, 1, 2, or 3, mnem is set to and, orr, eor, or ands
    if opc == 0x00:
        mnem = 'and'
        opcode = INS_AND
    elif opc == 0x01:
        mnem = 'orr'
        opcode = INS_ORR
    elif opc == 0x10:
        mnem = 'eor'
        opcode = INS_EOR
    else:
        mnem = 'and'
        opcode = INS_AND
        iflags = IF_PSR_S

    #sf and n determine whether the register size corresponds to the 32 or 64-bit variant
    if sf == 0b0 and n == 0b0:
        size = 4
        rd += meta_reg_bases[size]
        rn += meta_reg_bases[size]
    elif sf == 0b1:
        size = 8
    else:
        return p_undef(opval, va)

    olist = (
        A64RegOper(rn, va, size=size),
        A64RegOper(rd, va, size=size),
        A64ImmOper((n + imms + immr), 0, S_LSL, va),
    )
    
    return opcode, mnem, olist, iflags, 0

mov_w_flags = (IF_N, 0, IF_Z, IF_K)


def p_mov_wide_imm(opval, va):
    '''
    Get the A64Opcode parameters for a Move Wide (immediate) instruction
    '''
    sf = opval >> 31
    opc = (opval >> 29) & 0x3
    hw = (opval >> 21) & 0x3
    imm16 = (opval >> 5) & 0xffff
    rd = opval & 0x1f

    if opc == 1:
        return p_undef(opval, va)

    #sf determines whether the register size corresponds to the 32 or 64-bit variant
    if sf == 0b0:
        size = 4
    else:
        size = 8
    olist = (
        A64RegOper(rd, va, size=size),
        A64ImmOper(imm16, hw*0b10000, S_LSL, va),
    )
    #all instrs share the mnem 'mov', but have one of three potential flags set
    #based on opc (00 -> IF_N, 01 -> undefined, 10 -> IF_Z, 11 -> IF_K)
    mnem = 'mov'
    opcode = INS_MOV
    iflag = mov_w_flags[opc]

    return opcode, mnem, olist, iflag, 0


def p_bitfield(opval, va):
    '''
    Get the parameters for an A64Opcode for a bitfield instruction
    '''
    sf = opval >> 31
    opc = opval >> 29 & 0x3
    n = opval >> 22
    immr = opval >> 16 & 0x3f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval >> 5 & 0x1f
    #all instrs share mnem 'bfm', but have different 
    mnem = 'bfm'
    opcode = INS_BFM
    iflag = (IFP_S, 0, IFP_U, None)[opc]
    #if iflag is none, the instruction is undefined. Otherwise, determine variant
    #based on sf and n and assign olist
    if iflag != None:
        if sf == 0b0 and n == 0b0:
            size = 4
            rd += meta_reg_bases[size]
            rn += meta_reg_bases[size]
        elif sf == 0b1 and n == 0b1:
            size = 8
        else:
            return p_undef(opval, va)
        olist = (
            A64RegOper(rd, va, size=size),
            A64RegOper(rn, va, size=size),
            A64ImmOper(immr, va=va),
            A64ImmOper(imms, va=va),
        )
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0




def p_extract(opval, va):
    '''
    Get the parameters for an A64Opcode for a extract instruction
    '''
    sf = opval >> 31
    n = opval >> 22 & 0x1
    rm = opval >> 16 & 0x1f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    #both instrs have mnem 'extr'. the if-else just determines 32 or 64-bit variant
    
    mnem = 'extr'
    opcode = INS_EXTR
    if sf == 0b0 and n == 0b0 and imms & 0x100000 == 0x000000:
        size = 4
        rd += meta_reg_bases[size]
        rm += meta_reg_bases[size]
        rn += meta_reg_bases[size]
    elif sf == 0b0 and n == 0b1:
        size = 8
    else:
        return p_undef(opval, va)
    olist = (
        A64RegOper(rd, va, size=size),
        A64RegOper(rn, va, size=size),
        A64RegOper(rm, va, size=size),
        A64ImmOper(imms, 0, S_LSL, va),
    )
    return opcode, mnem, olist, 0, 0

def p_branch_uncond_imm(opval, va):
    '''
    Get the parameters for an A64Opcode for a Branch Unconditional (immediate) instruction
    '''
    op = opval >> 31
    imm26 = opval & 0x3ffffffff
    #determines mnemonic
    if op == 0:
        mnem = 'b'
        opcode = INS_B
    else:
        mnem = 'bl'
        opcode = INS_BL
        
    olist = (
        A64ImmOper(imm26*0x100, va=va),
    )

    return opcode, mnem, olist, 0, 0

def p_cmp_branch_imm(opval, va):
    '''
    Get the parameters for an A64Opcode for a Compare Branch (immediate) instruction
    '''
    sf = opval >> 31
    op = opval >> 24 & 0x1
    imm19 = opval >> 5 & 0x7ffff
    rt = opval & 0x1f

    #mnem is determined based on op, variant is determined based on sf
    if op == 0:
        mnem = 'cbz'
        opcode = INS_CBZ
    else:
        mnem = 'cbnz'
        opcode = INS_CBNZ
    if sf == 0b0:
        size = 4
        rt += meta_reg_bases[size]
    else:
        size = 8
    olist = (
        A64RegOper(rt, va, size=size),
        A64ImmOper(imm19*0b100, 0, S_LSL, va),
    )

    return opcode, mnem, olist, 0, 0

def p_test_branch_imm(opval, va):
    '''
    Test branch (immediate) instruction
    '''
    b5 = opval >> 31 & 0x1
    op = opval >> 24 & 0x1
    b40 = opval >> 20 & 0x1f
    imm14 = opval >> 5 & 0x3fff
    rt = opval & 0x1f

    #mnem is determined based on op, size is based on b5
    if op == 0b0:
        mnem = 'tbz'
        opcode = INS_TBZ
    else:
        mnem = 'tbnz'
        opcode = INS_TBNZ
    if b5 == 0b0:
        size = 4
        rt += meta_reg_bases[size]
    else:
        size = 8
    olist = (
        A64RegOper(rt, va, size=size),
        A64ImmOper(b5+b40, va=va),
        A64ImmOper(imm14*0x100, va=va),
    )

    return opcode, mnem, olist, 0, 0

def p_branch_cond_imm(opval, va):
    '''
    Conditional branch (immediate) instruction
    '''
    imm19 = opval >> 5 & 0x7ffff
    cond = opval & 0xf
    mnem = 'B.'
    opcode = INS_BCC
    olist = (
        A64CondOper(cond),
        A64ImmOper(imm19*0x100, va=va),
    )
    return opcode, mnem, olist, 0, 0

def p_excp_gen(opval, va):
    '''
    Exception generation instruction
    '''
    opc = opval >> 21 & 0x7
    imm16 = opval >> 5 & 0xffff
    op2 = opval >> 2 & 0x7
    ll = opval & 0x3

    olist = (
        A64ImmOper(imm16, 0, S_LSL, va),
    )
    if op2 != 0b000:
        return p_undef(opval, va)

    #parses mnem. Basically just making it slightly more efficient through
    #a treeish structure
    if opc == 0b000:
        if ll == 0b01:
            mnem = 'sbc'
            opcode = INS_SVC
        elif ll == 0b10:
            mnem = 'hvc'
            opcode = INS_HVC
        elif ll == 0b11:
            mnem = 'smc'
            opcode = INS_SMC
        else:
            return p_undef(opval, va)
    elif opc == 0b001:
        mnem = 'brk'
        opcode = INS_BRK
    elif opc == 0b010:
        mnem = 'hlt'
        opcode = INS_HLT
    elif opc == 0x101:
        if ll == 0b01:
            mnem = 'dcps1'
            opcode = INS_DCPS1
        elif ll == 0b10:
            mnem = 'dcps2'
            opcode = INS_DCPS2
        elif ll == 0b11:
            mnem = 'dcps3'
            opcode = INS_DCPS3
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)
    
    return (opcode, mnem, olist, 0, 0)

def p_sys(opval, va):
    '''
    Returns parameters for an A64Opcode for a system instruction
    '''
    l = opval >> 21 & 0x1
    op0 = opval >> 19 & 0x3
    op1 = opval >> 16 & 0x7
    crn = opval >> 12 & 0xf
    crm = opval >> 8 & 0xf
    op2 = opval >> 5 & 0x3
    rt = opval & 0x1f
    relevant = opval & 0x3fffff

    #this is legitimately ugly as sin. hopefully can come back and fix, though
    #since it has 6 relevant decode fields, it won't be that improvable

    if relevant & 0b1110001111000000011111 == 0b0000000100000000011111:
        opcode = INS_MSR
        mnem = 'msr'
        olist = (
            #FIXME pstatefield
            A64ImmOper(crm, va=va),
        )
        iflag = 0
        
    elif relevant & 0b1111111111000000011111 == 0b00001100100000000011111:
        opcode = INS_HINT
        mnem = 'hint'
        olist = (
            A64ImmOper(crm + op2, 0, S_LSL, va)
        )
        iflag = 0
        
    elif relevant & 0b1111111111000011111111 == 0b00001100110000001011111:
        opcode = INS_CLREX
        mnem = 'clrex'
        olist = (
            A64ImmOper(crm, 0, S_LSL, va)
        )
        iflag = 0
        
    elif relevant & 0b1111111111000011111111 == 0b00001100110000010011111:
        opcode = INS_DSB
        mnem = 'dsb'
        olist = (
            A64BarrierOptionOper(crm),
            A64ImmOper(crm, va=va),
        )
        iflag = 0

    elif relevant & 0b1111111111000011111111 == 0b00001100110000010111111:
        opcode = INS_DMB
        mnem = 'dmb'
        olist = (
            A64BarrierOptionOper(crm),
            A64ImmOper(crm, va=va),
        )
        iflag = 0

    elif relevant & 0b1111111111000011111111 == 0b00001100110000011011111:
        opcode = INS_ISB
        mnem = 'isb'
        olist = (
            A64BarrierOptionOper(crm),
            A64ImmOper(crm, va=va),
        )
        iflag = 0

    elif (l + op0) == 0x001:
        opcode = INS_SYS
        mnem = 'sys'
        if crn == 0b0111 or crn == 0b1000:
            sysop_concat = op1+crn+crm+op2
            for bits, mnemonic, ocode in sys_op_table:
                if sysop_concat == bits:
                    mnem = mnemonic
                    opcode = ocode
                    break
        olist = (
            A64ImmOper(op1, 0, S_LSL, va),
            A64NameOper(crn),
            A64NameOper(crm),
            A64ImmOper(op2, 0, S_LSL, va),
            A64RegOper(rt, va, size=8), #optional operand
        )
        iflag = 0

    elif (l + op0) & 0b110 == 0b010:
        opcode = INS_MSR
        mnem = 'msr'
        olist = (
            #A64RegOper(opval >> 5 & 0x7fff, va), system register?
            A64RegOper(rt, va, size=8),
        )
        iflag = 0

    elif (l + op0) & 0b111 == 0b101:
        opcode = INS_SYS
        mnem = 'sys'
        olist = (
            A64RegOper(rt, va, size=8),
            A64ImmOper(op1, 0, S_LSL, va),
            A64NameOper(crn),
            A64NameOper(crm),
            A64ImmOper(op2, 0, S_LSL, va),
        )
        iflag = IF_L

    elif (l + op0) & 0b110 == 0b110:
        opcode = INS_MRS
        mnem = 'mrs'
        olist = (
            A64RegOper(rt, va, size=8),
            #A64RegOper(opval >> 5 & 0x7fff, va) system register? see msrr
        )
        iflag = 0

    else:
        return p_undef(opval, va)
    
    return opcode, mnem, olist, iflag, 0

def p_branch_uncond_reg(opval, va):
    '''
    Return A64Opcode parameters for an Unconditional Branch (register) instruction
    '''
    opc = opval >> 21 & 0xf
    op2 = opval >> 16 & 0x1f
    op3 = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    op4 = opval & 0x1f
    #all the defined instructions share ops 2, 3, and 4 being 11111, 000000, and 00000
    if op2 == 0b11111 and op3 == 0b000000 and op4 == 0b00000:
        #the first 3 instructions share this olist. The last 2 have an empty olist,
        #redefined when their mnemonics are determined
        olist = (
            A64RegOper(rn, va, size=8),
        )
        #determine opcode/mnemonic
        if opc == 0b0000:
            opcode = INS_BR
            mnem = 'br'
            iflag = envi.IF_BRANCH

        elif opc == 0b0001:
            opcode = INS_BLR
            mnem = 'blr'
            iflag = envi.IF_CALL

        elif opc == 0b0010:
            opcode = INS_RET
            mnem = 'ret'
            olist = () #empty olist
            iflag = envi.IF_RET | envi.IF_NOFALL

        elif opc == 0b0100 and rn == 0b11111:
            opcode = INS_ERET
            mnem = 'eret'
            olist = () #empty olist
            iflag = envi.IF_RET | envi.IF_NOFALL

        elif opc == 0b0101 and rn == 0b11111:
            opcode = INS_DRPS
            mnem = 'drps'
            olist = () #empty olist
            iflag = envi.IF_NOFALL
        else:
            return p_undef(opval, va)          
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0   

def p_ls_excl(opval, va):
    '''
    Load/store exclusive instruction
    '''
    size = opval >> 30 & 0x3
    o2 = opval >> 23 & 0x1
    l = opval >> 22 & 0x1
    o1 = opval >> 21 & 0x1
    rs = opval >> 16 & 0x1f
    o0 = opval >> 15 & 0x1
    rt2 = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    #all mnemonics are some variation on 'st' or 'ld'
    #if l is 0, mnemonic is 'st' and it's possible the IF_L iflag could be assigned
    #otherwise, mnemonic is 'ld' and it's possible the IF_A iflag could be assigned
    if l == 0b0:
        mnem = 'st'
        opcode = INS_ST
        optional_iflag = IF_L
    else:
        mnem = 'ld'
        opcode = INS_LD
        optional_iflag = IF_A
    #all instructions with o0 equal to 1 have the optional iflag added to the mnem
    if o0 == 0b1:
        iflag |= optional_iflag
    #all instructions with o2 equal to 0 have an X added to the mnem
    if o2 == 0b0:
        iflag |= IF_X
    #all instructions with o1 equal to 0 have an R added to the mnem
    #otherwise, p is added to the mnem
    if o1 == 0b0:
        iflag |= IF_R
    else:
        iflag |= IF_P
    #all instructions with size equal to 0 have a B added to the mnem,
    #otherwise, all instructions with size equal to 1 have a H added to mnem
    #otherwise, nothing
    if size == 0b00:
        iflag |= IF_B
    elif size == 0b01:
        iflag |= IF_H
    
    if size == 0b00 or size == 0b01: #instructions with IF_B or IF_H set
        if o2 == 0b0: #instructions with IF_X set
            if l == 0b0:
                olist = (
                    A64RegOper(rs, va, size=4),
                    A64RegOper(rt, va, size=4),
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(0, va=va),
                )
            else: #L == 1
                olist = (
                    A64RegOper(rt, va, size=4),
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(0, va=va),
                )
        else: #o2 == 1, or instructions without IF_X set
            olist = (
                A64RegOper(rt, va, size=4),
                A64RegOper(rn, va, size=8),
                A64ImmOper(0, va=va),
            )
    else:  #size == 10 or 11, or instructions without IF_B or IF_H set
        #determines 32 or 64-bit variant
        if size == 0b10:
            regsize = 4
        else:
            regsize = 8
        if o2 == 0b0: #IF_X set
            if l == 0b0:
                if o1 == 0b0: #IF_R set
                    olist = (
                        A64RegOper(rs, va, size=4),
                        A64RegOper(rt, va, size=regsize),
                        A64RegOper(rn, va, size=8),
                    )                        
                else: #IF_R not set
                    olist = (
                        A64RegOper(rs, va, size=4),
                        A64RegOper(rt, va, size=regsize),
                        A64RegOper(rt2, va, size=regsize),
                        A64RegOper(rn, va, size=8),
                    )                     
            else: #L == 1
                if o1 == 0b0: #IF_R set
                    olist = (
                        A64RegOper(rt, va, size=regsize),
                        A64RegOper(rn, va, size=8),
                    ) 
                else: #o1 == 1x0110 IF_R not set
                    olist = (
                        A64RegOper(rt, va, size=regsize),
                        A64RegOper(rt2, va, size=regsize),
                        A64RegOper(rn, va, size=8),
                    )                                       
        else: #o2 == 1 #IF_X not set
            olist = (
                A64RegOper(rt, va, size=regsize),
                A64RegOper(rn, va, size=8),
            )

    return opcode, mnem, olist, iflag, 0

def p_load_reg_lit(opval, va):
    '''
    Load register (literal) instruction
    '''
    iflag = 0
    opc = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    imm19 = opval >> 5 & 0x7ffff
    rt = opval & 0x1f
    #all instructions but prfm have mnemonic 'ldr'
    opcode = INS_LDR
    mnem = 'ldr'

    #determine if the instruction is actually an 'ldr' and if so, which variant
    if opc == 0b00: #32-bit variants of normal and SIMD versions
        olist = (
            A64RegOper(rt, va, size=4),
            A64ImmOper(imm19*0b100, 0, S_LSL, va),
        )

    elif opc == 0b01: #64-bit variants of normal and SIMD versions
        olist = (
            A64RegOper(rt, va, size=8),
            A64ImmOper(imm19*0b100, 0, S_LSL, va),
        )

    elif opc == 0b10: #128-bit SIMD variant, and the unique 'ldrsw'
        if v == 0b0:
            iflag = IF_SW
            regsize = 8
        else:
            regsize = 16
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64ImmOper(imm19*0b100, 0, S_LSL, va),
        )

    else: #prfm and undefined instruction
        if v == 0b0:
            mnem = 'prfm'
            opcode = INS_PRFM
            olist = (
                prfop[rt],
                A64ImmOper(imm19*0b100, 0, S_LSL, va),
            )

        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0


def p_ls_napair_offset(opval, va):
    '''
    Load/store no-allocate pair (offset)
    '''
    opc = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    l = opval >> 22 & 0x1
    imm7 = opval >> 15 & 0x7f
    rt2 = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f

    if l == 0b0:
        mnem = 'stnp'
        opcode = INS_STNP
    else:
        mnem = 'ldnp'
        opcode = INS_LDNP
    if v == 0b1:
        if opc == 0b00:
            regsize = 4
            imm = imm7*0b100
        elif opc == 0b01:
            regsize = 8
            imm = imm7*0b1000
        elif opc == 0b10:
            regsize = 16
            imm = imm7*0b10000
        else:
            return p_undef(opval, va)
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rt2, va, size=regsize),                
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm, 0, S_LSL, va),
        )
            
    else:
        if opc == 0b00:
            regsize = 4
            imm = imm7*0b100
        elif opc == 0b10:
            regsize = 8
            imm = imm7*0b1000
        else:
            return p_undef(opval, va)
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rt2, va, size=regsize),
            A64ImmOper(imm, 0, S_LSL, va),
        )
    return opcode, mnem, olist, 0, 0


def p_ls_regpair(opval, va):
    '''
    Load/store register pair (pre-indexed, post-indexed or offset)
    '''
    opc = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    l = opval >> 22 & 0x1
    imm7 = opval >> 15 & 0x7f
    rt2 = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f

    vl = v + l
    if opc == 0b00: #32-bit variant
        mnem, opcode = ls_regpair_table[vl]
        olist = (
            A64RegOper(rt, va, size=4),
            A64RegOper(rt2,va, size=4),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm7*0b100, va=va),
        )
    elif opc == 0b01:
        if vl == 0b00:
            return p_undef(opval, va)
        elif vl == 0b01:
            mnem = 'ldpsw'
            opcode = INS_LDPSW
            imm = imm7*0b100
        else:
            mnem, opcode = ls_regpair_table[VL]
            imm = imm7*0b1000
        olist = (
            A64RegOper(rt, va, size=8),
            A64RegOper(rt2,va, size=8),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm, va),
        )            
    elif opc == 0b10:
        mnem, opcode = ls_regpair_table[vl]
        if v == 0b0:
            regsize = 8
            imm = imm7*0b1000
        else:
            regsize = 16
            imm = imm7*0b10000
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rt2, va, size=regsize),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm, va=va),
        )
    else:
        return p_undef(opval, va)
    
    return opcode, mnem, olist, 0, 0


ls_regpair_table = (
    ('stp', INS_STP),
    ('ldp', INS_LDP),
    ('stp', INS_STP),
    ('ldp', INS_LDP),    
)


def p_ls_reg_unsc_imm(opval, va):
    '''
    Load/store register (unscaled immediate)
    '''
    iflag = 0
    size = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    opc = opval >> 22 & 0x3
    imm9 = opval >> 12 & 0x1ff
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
       
    if opc == 0b00 or opc == 0b01:
        if opc == 0b01:
            opcode = INS_LDUR
            mnem = 'ldur'
        else:
            opcode = INS_STUR
            mnem = 'stur'
        if v == 0b0:
            if size == 0b11:
                regsize = 8
            else:
                regsize = 4
                if size == 0b00:
                    iflag |= IF_B
                elif size == 0b01:
                    iflag |= IF_H
            olist = (
                A64RegOper(rt, va, size=regsize),
                A64RegOper(rn, va, size=8),
                A64ImmOper(imm9, va=va),
            )
        else:
            if size == 0b00:
                regsize = 8
            elif size == 0b01:
                regsize = 16
            elif size == 0b10:
                regsize = 4
            else:
                regsize = 8
            olist = (
                A64RegOper(rt, va, size=regsize),
                A64RegOper(rn, va, size=8),
                A64ImmOper(imm9, va=va),
            )
    else:
        if v == 0b1:
            if opc == 0b10:
                opcode = INS_STUR
                mnem = 'stur'
            else:
                opcode = INS_LDUR
                mnem = 'ldur'
            olist = (
                A64RegOper(rt, va, size=16),
                A64RegOper(rn, va, size=8),
                A64ImmOper(imm9, va=va),
            )
        else:
            if size == 0b11:
                mnem == 'prfum'
                opcode = INS_PRFUM
                olist = (
                    prfop[rt],
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(imm9, va=va),
                )
            else:
                if opc == 0b10:
                    regsize = 8
                else:
                    regsize = 4
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(imm9, va=va),
                )
                mnem = 'ldur'
                opcode = INS_LDUR
                iflag |= IF_S
                if size == 0b00:
                    iflag |= IF_B
                elif size == 0b01:
                    iflag |= IF_H
                elif size == 0b10:
                    iflag |= IF_W

    return opcode, mnem, olist, iflag, 0

def p_ls_reg_unpriv(opval, va):
    '''
    Load/store register (unprivileged)
    '''
    iflag = 0
    size = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    opc = opval >> 22 & 0x3
    imm9 = opval >> 12 & 0x1ff
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if v == 0b0:
        if opc == 0b00:
            mnem = 'sttr'
            opcode = INS_STTR
        else:
            mnem = 'ldtr'
            opcode = INS_LDTR
            if opc == 0b10 or opc == 0b11:
                iflag |= IF_S
                if size == 10:
                    iflag |= IF_W
        if size == 0b00:
            iflag |= IF_B
        elif size == 0b01:
            iflag |= IF_H
        if size != 0b11 and opc != 0b10:
            regsize = 4
        else:
            regsize = 8
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm9, va),
        )
    else:
        return p_undef(opval, va)
        
    return (opcode, mnem, olist, iflag, 0)        
            
def p_ls_reg_imm(opval, va):
    '''
    Load/store register (immediate post and pre-indexed)
    '''
    iflag = 0
    size = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    opc = opval >> 22 & 0x3
    imm9 = opval >> 12 & 0x1ff
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if v == 0b0:
        if opc == 0b00:
            mnem = 'str'
            opcode = INS_STR
        else:
            mnem = 'ldr'
            opcode = INS_LDR
        if opc == 0b10 or opc == 0b11:
            iflag |= IF_S
            if size == 0b10:
                iflag |= IF_W
        if size == 0b00:
            iflag |= IF_B
        elif size == 0b01:
            iflag |= IF_H
        if opc == 0b10 or size == 0b11:
            regsize = 8
        else:
            regsize = 4
    else:
        if opc == 0b00 or opc == 0b10:
            mnem = 'str'
            opcode = INS_STR
        else:
            mnem = 'ldr'
            opcode = INS_LDR
        if size == 0b00:
            if opc == 0b00 or opc == 0b01:
                regsize = 8
            else:
                regsize = 16
        elif size == 0b01:
            regsize = 16
        elif size == 0b10:
            regsize = 4
        else:
            regsize = 8
    olist = (
        A64RegOper(rt, va, size=regsize),
        A64RegOper(rn, va, size=8),
        A64ImmOper(imm9, va=va),
    )

    return opcode, mnem, olist, iflag, 0
        


def p_ls_reg_offset(opval, va):
    '''
    Load/store register (register offset)
    '''
    iflag = 0
    size = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    opc = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    option = opval >> 13 & 0x7
    s = opval >> 12 & 0x1
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f

    if v == 0b0:
        if opc == 0b00:
            mnem = 'str'
            opcode = INS_STR
        else:
            if size == 0b11 and opc == 0b10:
                mnem =  'prfm'
                opcode = INS_PRFM
                if option & 0b011 == 0b011:
                    regsize = 4
                elif option & 0b011 == 0b010:
                    regsize = 8
                else:
                    return p_undef(opval)
                olist = (
                    prfop[rt],
                    A64RegOper(rn, va, size=8),
                    A64RegOper(rm, va, size=regsize),
                    #FIXME extend
                    #FIXME amount
                )
                return opcode, mnem, olist, 0, 0
            else:
                mnem = 'ldr'
                opcode = INS_LDR
        if opc == 0b10 or opc == 0b11:
            iflag |= IF_S
            if size == 0b10:
                iflag |= IF_W
        if size == 0b00:
            iflag |= IF_B
        elif size == 0b01:
            iflag |= IF_H
        if opc == 0b10 or size == 0b11:
            regsize = 8
        else:
            regsize = 4
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rn, va, size=8),
            #FIXME rm, extend, amount
        )
        
    else:
        if opc == 0b10 or opc == 0b00:
            mnem = 'str'
            opcode = INS_STR
        else:
            mnem = 'ldr'
            opcode = INS_LDR
        if size == 0b00:
            if opc == 0b00 or opc == 0b01:
                regsize = 8
            else:
                regsize = 16
        elif size == 0b01:
            regsize = 16
        elif size == 0b10:
            regsize = 4
        else:
            regsize = 8
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rn, va, size=8),
            #FIXME rm, extend, amount
        )

    return opcode, mnem, olist, iflag, 0

def p_ls_reg_us_imm(opval, va):
    '''
    Load/store register (unsigned immediate)
    '''
    iflag = 0
    size = opval >> 30 & 0x3
    v = opval >> 26 & 0x1
    opc = opval >> 22 & 0x3
    imm12 = opval >> 10 & 0xfff
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if v == 0b0:
        if opc == 0b00:
            mnem = 'str'
            opcode = INS_STR
        else:
            if size == 0b11 and opc == 0b10:
                mnem =  'prfm'
                opcode = INS_PRFM
                olist = (
                    prfop[rt],
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(imm12*0b1000, va=va),
                )
                return opcode, mnem, olist, 0, 0
            else:
                mnem = 'ldr'
                opcode = INS_LDR
        if opc == 0b10 or opc == 0b11:
            iflag |= IF_S
            if size == 0b10:
                iflag |= IF_W
        if size == 0b00:
            iflag |= IF_B
        elif size == 0b01:
            iflag |= IF_H
        if opc == 0b10 or size == 0b11:
            regsize = 8
        else:
            regsize = 4
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm12, va=va),
        )
        
    else:
        if opc == 0b10 or opc == 0b00:
            mnem = 'str'
            opcode = INS_STR
        else:
            mnem = 'ldr'
            opcode = INS_LDR
        if size == 0b00:
            if opc == 0b00 or opc == 0b01:
                regsize = 8
                imm = imm12
            else:
                regsize = 16
                imm = imm12*0b10000
        elif size == 0b01:
            regsize = 16
            imm = imm12*0b10
        elif size == 0b10:
            regsize = 4
            imm = imm12*0b100
        else:
            regsize = 8
            imm = imm12*0b1000
        olist = (
            A64RegOper(rt, va, size=regsize),
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm, va=va),
        )

    return opcode, mnem, olist, iflag, 0

def p_simd_ls_multistruct(opval, va):
    '''
    AdvSIMD Load/store multiple structures
    '''
    q = opval >> 30 & 0x1
    l = opval >> 22 & 0x1
    opc = opval >> 12 & 0xf
    size = opval >> 10 & 0x3
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if opc == 0b0000 or opc == 0b0010:
        if l == 0b0:
            if opc == 0b0000:
                mnem = 'st4'
                opcode = INS_ST4
                version = 0
            else:
                mnem = 'st1'
                opcode = INS_ST1
                version = 1
        else:
            if opc == 0b0000:
                mnem = 'ld4'
                opcode = INS_LD4
                version = 0
            else:
                mnem = 'ld1'
                opcode = INS_LD1
                version = 1
        sizeq = size + q
        if opc & 0b0010 == 0b0000:
            olist = (
                A64RegOper(rt, va, oflag=t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=t_table[sizeq]),
                A64RegOper((rt+2)%32, va, oflag=t_table[sizeq]),
                A64RegOper((rt+3)%32, va, oflag=t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
        else:
            olist = (
                A64RegOper(rt, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+2)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+3)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
    elif opc == 0b0100 or opc == 0b0110:
        if l == 0b0:
            if opc == 0b0100:
                mnem = 'st3'
                opcode = INS_ST3
                version = 0
            else:
                mnem = 'st1'
                opcode = INS_ST1
                version = 1
        else:
            if opc == 0b0100:
                mnem = 'ld3'
                opcode = INS_LD3
                version = 0
            else:
                mnem = 'ld1'
                opcode = INS_LD1
                version = 1
        if opc & 0b0010 == 0b0000:
            olist = (
                A64RegOper(rt, va, oflag=t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=t_table[sizeq]),
                A64RegOper((rt+2)%32, va, oflag=t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
        else:
            olist = (
                A64RegOper(rt, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+2)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
    elif opc == 0b0111:
        if l == 0b0:
            mnem = 'st1'
            opcode = INS_ST1
            version =  1
        else:
            mnem = 'ld1'
            opcode = INS_LD1
            version = 1
        olist = (
            A64RegOper(rt, va, oflag=t_table[sizeq]),
            A64RegOper(rn, va, size=8),
        )

    elif opc == 0b1000 or opc == 0b1010:
        if l == 0b0:
            if opc == 0b1000:
                mnem = 'st2'
                opcode = INS_ST2
                version = 0
            else:
                mnem = 'st1'
                opcode = INS_ST1
                version = 1
        else:
            if opc == 0b1000:
                mnem = 'ld2'
                opcode = INS_LD2
                version = 0
            else:
                mnem = 'ld1'
                opcode = INS_LD1
                version = 1
        if opc & 0b0010 == 0b0000:
            olist = (
                A64RegOper(rt, va, oflag=t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
        else:
            olist = (
                A64RegOper(rt, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper((rt+1)%32, va, oflag=unreserved_t_table[sizeq]),
                A64RegOper(rn, va, size=8),
            )
    else:
        return p_undef(opval, va)
        
    return (opcode, mnem, olist, 0, 0)

def p_simd_ls_multistruct_posti(opval, va):
    '''
    AdvSIMD load/store multiple structures (post-indexed)
    '''
    iflag = 0
    #FIXME olists
    q = opval >> 30 & 0x1
    l = opval >> 22 & 0x1
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0xf
    size = opval >> 10 & 0x3
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if opc & 0b0010 == 0b0010:
        if l == 0b0:
            mnem = 'st1'
            opcode = INS_ST1
        else:
            mnem = 'ld1'
            opcode = INS_LD1
    if l == 0b0:
        if opc == 0b0000:
            mnem = 'st4'
            opcode = INS_ST4
        elif opc == 0b0100:
            mnem = 'st3'
            opcode = INS_ST3
        elif opc == 0b1000:
            mnem = 'st2'
            opcode = INS_ST2
    else:
        if opc == 0b0000:
            mnem = 'ld4'
            opcode = INS_LD4
        elif opc == 0b0100:
            mnem = 'ld3'
            opcode = INS_LD3
        elif opc == 0b1000:
            mnem = 'ld2'
            opcode = INS_LD2
    if opc & 0b0000 == 0b0010:
        t = unreserved_t_table[size+q]
    else:
        t = t_table[size+q]
    if rm != 0b11111:
        if opc == 0b0000 or opc == 0b0010:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper((rt+2)%32, va, oflag=t),
                A64RegOper((rt+3)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8), #FIXME excluding XZR
            )
        elif opc == 0b0100 or opc == 0b0110:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper((rt+2)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8), #FIXME excluding XZR
            )
        elif opc == 0b0111:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8), #FIXME excluding XZR
            )
        elif opc == 0b1000 or opc == 0b1010:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8), #FIXME excluding XZR
            )
        else:
            return p_undef(opval, va)
    else:
        if opc == 0b0000 or opc == 0b0010:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper((rt+2)%32, va, oflag=t),
                A64RegOper((rt+3)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64ImmOper((0x32, 0x64)[q], va=va), #FIXME probably wrong
            )
        elif opc == 0b0100 or opc == 0b0110:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper((rt+2)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64ImmOper((0x24, 0x48)[q], va=va), #FIXME probably wrong
            )
        elif opc == 0b0111:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64ImmOper((0x16, 0x32)[q], va=va), #FIXME probably wrong
            )
        elif opc == 0b1000 or opc == 0b1010:
            olist = (
                A64RegOper(rt, va, oflag=t),
                A64RegOper((rt+1)%32, va, oflag=t),
                A64RegOper(rn, va, size=8),
                A64ImmOper((0x8, 0x16)[q], va=va), #FIXME probably wrong
            )
        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0

t_table = (
    IFS_8B,
    IFS_16B,
    IFS_4H,
    IFS_8H,
    IFS_2S,
    IFS_4S,
    'RESERVED',
    IFS_2D,
)

def p_simd_ls_onestruct(opval, va):
    '''
    AdvSIMD load/store one structure
    '''
    q = opval >> 30 & 0x1
    l = opval >> 22 & 0x1
    r = opval >> 21 & 0x1
    opc = opval >> 13 & 0x7
    s = opval >> 12 & 0x1
    size = opval >> 10 & 0x3
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f
    if l == 0b0:
        if r == 0b0:
            if opc & 0b001 == 0b000:
                mnem = 'st1'
                opcode = INS_ST1
                if opc == 0b000:
                    simdOper = 8
                    index = q + s + size
                elif opc == 0b010:
                    simdOper = 16
                    index = q + s + (opval >> 10 & 0x1)
                elif opc == 0b100:
                    if size == 0b00:
                        simdOper = 4
                        index = q + s
                    elif size == 0b01:
                        simdOper = 8
                        index = q
                olist = (
                    A64RegOper(rt, va, size=simdOper),
                    A64ImmOper(index, va=va),
                    A64RegOper(rn, va, size=8),
                )
            else:
                mnem = 'st3'
                opcode = INS_ST3
                if opc == 0b000:
                    simdOper = 8
                    index = q + s + size
                elif opc == 0b010:
                    simdOper = 16
                    index = q + s + (opval >> 10 & 0x1)
                elif opc == 0b100:
                    if size == 0b00:
                        simdOper = 4
                        index = q + s
                    elif size == 0b01:
                        simdOper = 8
                        index = q
                olist = (
                    A64RegOper(rt, va, size=simdOper),
                    A64RegOper((rt + 1) % 32, va, size=simdOper),
                    A64RegOper((rt + 2) % 32, va, size=simdOper),
                    A64ImmOper(index, va=va),
                    A64RegOper(rn, va, size=8),
                )
        else:
            if opc & 0b001 == 0b000:
                mnem = 'st2'
                opcode = INS_ST2
                if opc == 0b000:
                    simdOper = 8
                    index = q + s + size
                elif opc == 0b010:
                    simdOper = 16
                    index = q + s + (opval >> 10 & 0x1)
                elif opc == 0b100:
                    if size == 0b00:
                        simdOper = 4
                        index = q + s
                    elif size == 0b01:
                        simdOper = 8
                        index = q
                olist = (
                    A64RegOper(rt, va, size=simdOper),
                    A64RegOper((rt + 1) % 32, va, size=simdOper),
                    A64ImmOper(index, va=va),
                    A64RegOper(rn, va, size=8),
                )
            else:
                mnem = 'st4'
                opcode = INS_ST4
                if opc == 0b000:
                    simdOper = 8
                    index = q + s + size
                elif opc == 0b010:
                    simdOper = 16
                    index = q + s + (opval >> 10 & 0x1)
                elif opc == 0b100:
                    if size == 0b00:
                        simdOper = 4
                        index = q + s
                    elif size == 0b01:
                        simdOper = 8
                        index = q
                olist = (
                    A64RegOper(rt, va, size=simdOper),
                    A64RegOper((rt + 1) % 32, va, size=simdOper),
                    A64RegOper((rt + 2) % 32, va, size=simdOper),
                    A64RegOper((rt + 3) % 32, va, size=simdOper),
                    A64ImmOper(index, va=va),
                    A64RegOper(rn, va, size=8),
                )
    else:
        if r == 0b0:
            if opc & 0b001 == 0b000:
                mnem = 'ld1'
                opcode = INS_LD1
                if opc != 0b110:
                    if opc == 0b000:
                        simdOper = 8
                        index = q + s + size
                    elif opc == 0b010:
                        simdOper = 16
                        index = q + s + (opval >> 10 & 0x1)
                    elif opc == 0b100:
                        if size == 0b00:
                            simdOper = 4
                            index = q + s
                        elif size == 0b01:
                            simdOper = 8
                            index = q
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64ImmOper(index, va=va),
                        A64RegOper(rn, va, size=8),
                    )
                else:
                    iflag |= IF_R
                    olist = (
                        A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                        A64RegOper(rn, va, size=8),
                    )
            else:
                mnem = 'ld3'
                opcode = INS_LD3
                if opc != 0b111:
                    if opc == 0b000:
                        simdOper = 8
                        index = q + s + size
                    elif opc == 0b010:
                        simdOper = 16
                        index = q + s + (opval >> 10 & 0x1)
                    elif opc == 0b100:
                        if size == 0b00:
                            simdOper = 4
                            index = q + s
                        elif size == 0b01:
                            simdOper = 8
                            index = q
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt + 1) % 32, va, size=simdOper),
                        A64RegOper((rt + 2) % 32, va, size=simdOper),
                        A64ImmOper(index, va=va),
                        A64RegOper(rn, va, size=8),
                    )
                else:
                    iflag |= IF_R
                    simdOper = unreserved_t_table[size+q]
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt+1) % 32, va, size=simdOper),
                        A64RegOper((rt+2) % 32, va, size=simdOper),
                        A64RegOper(rn, va, size=8),
                    )
                    
        else:
            if opc & 0b001 == 0b000:
                mnem = 'ld2'
                opcode = INS_LD2
                if opc != 0b110:
                    if opc == 0b000:
                        simdOper = 8
                        index = q + s + size
                    elif opc == 0b010:
                        simdOper = 16
                        index = q + s + (opval >> 10 & 0x1)
                    elif opc == 0b100:
                        if size == 0b00:
                            simdOper = 4
                            index = q + s
                        elif size == 0b01:
                            simdOper = 8
                            index = q
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt + 1) % 32, va, size=simdOper),
                        A64ImmOper(index, va=va),
                        A64RegOper(rn, va, size=8),
                    )
                else:
                    iflag |= IF_R
                    simdOper = onestruct_t_table[size+q]
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt+1) % 32, va, size=simdOper),
                        A64RegOper(rn, va, size=8),
                    )
            else:
                mnem = 'ld4'
                opcode = INS_LD4
                if opc != 0b111:
                    if opc == 0b000:
                        simdOper = 8
                        index = q + s + size
                    elif opc == 0b010:
                        simdOper = 16
                        index = q + s + (opval >> 10 & 0x1)
                    elif opc == 0b100:
                        if size == 0b00:
                            simdOper = 4
                            index = q + s
                        elif size == 0b01:
                            simdOper = 8
                            index = q
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt + 1) % 32, va, size=simdOper),
                        A64RegOper((rt + 2) % 32, va, size=simdOper),
                        A64RegOper((rt + 3) % 32, va, size=simdOper),
                        A64ImmOper(index, va=va),
                        A64RegOper(rn, va, size=8),
                    )
                else:
                    iflag |= IF_R
                    simdOper = unreserved_t_table[size+q]
                    olist = (
                        A64RegOper(rt, va, size=simdOper),
                        A64RegOper((rt+1) % 32, va, size=simdOper),
                        A64RegOper((rt+2) % 32, va, size=simdOper),
                        A64RegOper((rt+3) % 32, va, size=simdOper),
                        A64RegOper(rn, va, size=8),
                    )
                    
    return opcode, mnem, olist, iflag, 0
    

def p_simd_ls_onestruct_posti(opval, va):
    '''
    AdvSIMD load/store one structure (post-indexed)
    '''
    iflag = 0
    q = opval >> 30 & 0x1
    l = opval >> 22 & 0x1
    r = opval >> 21 & 0x1
    rm = opval >> 16 & 0x1f
    opc = opval >> 13 & 0x7
    s = opval >> 12 & 0x1
    size = opval >> 10 & 0x3
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f

    if opc == 0b000:
        imm = q+s+size
        regsize = 8
    elif opc == 0b010:
        imm = q+s+(size & 0b01)
        regsize = 16
    elif opc == 0b100:
        if size == 0b00:
            imm = q+s
            regsize = 4
        elif size == 0b01:
            imm = q
            regsize = 8

    if r == 0b0:
        if opc & 0b001 == 0b000:
            if l == 0b0:
                mnem = 'st1'
                opcode = INS_ST1
            else:
                mnem = 'ld1'
                opcode = INS_LD1
            if opc == 0b110:
                if l == 0b0:
                    return p_undef(opval, va)
                else:
                    iflag |= IF_R
                    if rm != 0b11111:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                        )
                    else:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            ('#1', '#2', '#4', '#8')[size] #FIXME
                        )

                return opcode, mnem, olist, iflag, 0
            if rm != 0b11111:
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64ImmOper(imm, va=va),
                    A64RegOper(rn, va, size=8),
                    A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                )
            else:
                if opc == 0b000:
                    var = '#1'
                elif opc == 0b010:
                    var = '#2'
                elif opc == 0b100:
                    if size == 0b00:
                        var = '#4'
                    elif size == 0b01:
                        var = '#8'
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64ImmOper(q, va=va),
                    A64RegOper(rn, va, size=8),
                    var #FIXME
                )
        else:
            if l == 0b0:
                opcode = INS_ST3
                mnem = 'st3'
            else:
                opcode = INS_LD3
                mnem = 'ld3'
            if opc == 0b111:
                if l == 0b0:
                    return p_undef(opval, va)
                else:
                    iflag |= IF_R
                    if rm != 0b11111:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+2) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                        )
                    else:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+2) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            ('#3', '#6', '#12', '#24')[size] #FIXME
                        )

                return opcode, mnem, olist, iflag, 0    
            if rm != 0b11111:
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64RegOper((rt+1) % 32, va, size=regsize),
                    A64RegOper((rt+2) % 32, va, size=regsize),
                    A64ImmOper(imm, va=va),
                    A64RegOper(rn, va, size=8),
                    A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                )
            else:
                if opc == 0b001:
                    var = '#3'
                elif opc == 0b011:
                    var = '#6'
                elif opc == 0b101:
                    if size == 0b00:
                        var = '#12'
                    elif size == 0b01:
                        var = '#24'
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64RegOper((rt+1) % 32, va, size=regsize),
                    A64RegOper((rt+2) % 32, va, size=regsize),
                    A64ImmOper(q, va=va),
                    A64RegOper(rn, va, size=8),
                    var #FIXME
                )
    else:
        if opc & 0b001 == 0b000:
            if l == 0b0:
                mnem = 'st2'
                opcode = INS_ST2
            else:
                mnem = 'ld2'
                opcode = INS_LD2
            if opc == 0b110:
                if l == 0b0:
                    return p_undef(opval, va)
                else:
                    iflag |= IF_R
                    if rm != 0b11111:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                        )
                    else:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            ('#2', '#4', '#8','#16')[size] #FIXME
                        )
            if rm != 0b11111:
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64RegOper((rt+1) % 32, va, size=regsize),
                    A64ImmOper(imm, va=va),
                    A64RegOper(rn, va, size=8),
                    A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                )
            else:
                if opc == 0b000:
                    var = '#2'
                elif opc == 0b010:
                    var = '#4'
                elif opc == 0b100:
                    if size == 0b00:
                        var = '#8'
                    elif size == 0b01:
                        var = '#16'
                olist = (
                    A64RegOper(rt, va, size=regsize),
                    A64RegOper((rt+1) % 32, va, size=regsize),
                    A64ImmOper(q, va=va),
                    A64RegOper(rn, va, size=8),
                    var #FIXME
                )
        else:
            if l == 0b0:
                opcode = INS_ST4
                mnem = 'st4'
            else:
                opcode = INS_LD4
                mnem = 'ld4'
            if opc == 0b111:
                if opcode == INS_ST4:
                    return p_undef(opval, va)
                else:   
                    iflag |= IF_R
                    if rm != 0b11111:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+2) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+3) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            A64RegOper(rm, va, size=8), #FIXME excluding XZR?
                        )
                    else:
                        olist = (
                            A64RegOper(rt, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+1) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+2) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper((rt+3) % 32, va, size=unreserved_t_table[size+q]),
                            A64RegOper(rn, va, size=8),
                            ('#4', '#8', '#16', '#32')[size] #FIXME
                        )

                    return opcode, mnem, olist, iflag, 0
        if rm != 0b11111:
            olist = (
                A64RegOper(rt, va, size=regsize),
                A64RegOper((rt+1) % 32, va, size=regsize),
                A64RegOper((rt+2) % 32, va, size=regsize),
                A64RegOper((rt+3) % 32, va, size=regsize),
                A64ImmOper(imm, va=va),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8), #FIXME excluding XZR?
            )
        else:
            if opc == 0b000:
                var = '#4'
            elif opc == 0b010:
                var = '#8'
            elif opc == 0b100:
                if size == 0b00:
                    var = '#16'
                elif size == 0b01:
                    var = '#32'
            olist = (
                A64RegOper(rt, va, size=regsize),
                A64RegOper((rt+1) % 32, va, size=regsize),
                A64RegOper((rt+2) % 32, va, size=regsize),
                A64RegOper((rt+3) % 32, va, size=regsize),
                A64ImmOper(imm, va=va),
                A64RegOper(rn, va, size=8),
                var #FIXME
            )
                        
    return opcode, mnem, olist, iflag, 0

unreserved_t_table = (
    IFS_8B,
    IFS_16B,
    IFS_4H,
    IFS_8H,
    IFS_2S,
    IFS_4S,
    IFS_1D,
    IFS_2D,
)

def p_log_shft_reg(opval, va):
    '''
    Logical (shifted register)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    opc = opval >> 29 & 0x3
    shift = opval >> 22 & 0x3
    n = opval >> 21 & 0x1
    rm = opval >> 16 & 0x1f
    imm6 = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if sf == 0b0:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=4),
            #FIXME
        )
    else:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=8),
            A64RegOper(rm, va, size=8),
            #FIXME
        )
    if opc == 0b00 or opc == 0b11:
        if n == 0b0:
            mnem = 'and'
            opcode = INS_AND
        else:
            mnem = 'bic'
            opcode = INS_BIC
        if opc == 0b11:
            iflag |= IF_PSR_S
    elif opc == 0b01:
        mnem = 'or'
        opcode = INS_OR
        if n == 0b0:
            iflag |= IF_R
        else:
            iflag |= IF_N
    else:
        mnem = 'eo'
        opcode = INS_EO
        if n == 0b0:
            iflag |= IF_R
        else:
            iflag |= IF_N

    return opcode, mnem, olist, iflag, 0

def p_addsub_shft_reg(opval, va):
    '''
    Add/sub (shifted register)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    shift = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    imm6 = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if op ==  0b0:
        mnem = 'add'
        opcode = INS_ADD
    else:
        mnem = 'sub'
        opcode = INS_SUB
    if s == 0b1:
        iflag |= IF_PSR_S
    if shift == 0b00:
        shtype = S_LSL
    elif shift == 0b01:
        shtype = S_LSR
    elif shift == 0b10:
        shtype = S_ASR
    else:
        #FIXME
        shtype = 0
        
    if sf == 0b0:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=4),
            A64ShiftOper(rm, shtype, imm6),
        )
    else:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=8),
            A64RegOper(rm, va, size=8),
            A64ShiftOper(rm, shtype, imm6),
        )

    return opcode, mnem, olist, 0, 0

def p_addsub_ext_reg(opval, va):
    '''
    Add/sub (extended register)
    '''
    #FIXME this is unclear and almost certainly wrong
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    opt = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    option = opval >> 13 & 0x7
    imm3 = opval >> 10 & 0x7
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    
    if op ==  0b0:
        mnem = 'add'
        opcode = INS_ADD
    else:
        mnem = 'sub'
        opcode = INS_SUB
    if s == 0b1:
        iflag |= IF_PSR_S
    if option & 0b011 == 0b011:
        sizeRM = 8
    else:
        sizeRM = 4
    if rd == 0b11111 or rn ==  0b11111:
        if option == 0b010:
            extoper = 'LSL'
    else:
        extoper = exttable[option]

    if sf == 0b0:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=4),
            A64ExtendOper(rm, extoper, imm3),
        )
    else:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=8),
            A64RegOper(rm, va, size=sizeRM),
            
        )

    return opcode, mnem, olist, iflag, 0

exttable = (
    'UXTB',
    'UXTH',
    'UXTW',
    'UXTX',
    'SXTB',
    'SXTH',
    'SXTW',
    'SXTX',
)


        
def p_addsub_carry(opval, va):
    '''
    Add/sub (with carry)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    rm = opval >> 16 & 0x1f
    opcode2 = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if opcode2 == 0b000000:
        if op ==  0b0:
            mnem = 'adc'
            opcode = INS_ADC
        else:
            mnem = 'sbc'
            opcode = INS_SBC
        if s == 0b1:
            iflag |= IF_PSR_S
        if sf == 0b0:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
            )
        else:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
            )
    else:
        return p_undef(opval, va)

        
    return opcode, mnem, olist, iflag, 0

def p_cond_cmp_imm(opval, va):
    '''
    Conditional compare (immediate)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    imm5 = opval >> 16 & 0x1f
    cond = opval >> 12 & 0xf
    o2 = opval >> 10 & 0x1
    rn = opval >> 5 & 0x1f
    o3 = opval >> 4 & 0x1
    nzcv = opval & 0xf
    
    mnem = 'ccm'
    opcode = INS_CCM
    if op == 0b0:
        iflag |= IF_N
    else:
        iflag |= IF_P

    if sf == 0b0:
        olist = (
            A64RegOper(rn, va, size=4),
            A64ImmOper(imm5, va=va),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )
    else:
        olist = (
            A64RegOper(rn, va, size=8),
            A64ImmOper(imm5, va=va),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )

    return opcode, mnem, olist, iflag, 0

def p_cond_cmp_reg(opval, va):
    '''
    Conditional compare (register)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    op = opval >> 30 & 0x1
    s = opval >> 29 & 0x1
    rm = opval >> 16 & 0x1f
    cond = opval >> 12 & 0xf
    o2 = opval >> 10 & 0x1
    rn = opval >> 5 & 0x1f
    o3 = opval >> 4 & 0x1
    nzcv = opval & 0xf
    
    mnem = 'ccm'
    opcode = INS_CCM
    if op == 0b0:
        iflag |= IF_N
    else:
        iflag |= IF_P

    if sf == 0b0:
        olist = (
            A64RegOper(rn, va, size=64),
            A64RegOper(rm, va, size=64),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )
    else:
        olist = (
            A64RegOper(rn, va, size=64),
            A64RegOper(rm, va, size=64),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )
    return opcode, mnem, olist, iflag, 0

def p_cond_sel(opval, va):
    '''
    Conditional select
    '''
    iflag = 0

    opcode = INS_CS
    mnem = 'cs'
    if op == 0b0:
        if op2 == 0b00:
            iflag |= IF_EL
        elif op2 == 0b01:
            iflag |= IF_INC
        else:
            return p_undef(opval, va)
    else:
        if op2 == 0b00:
            iflag |= IF_INV
        elif op2 == 0b01:
            iflag |= IF_NEG
        else:
            return p_undef(opval, va)
    #FIXME: cond opers
    if sf == 0b0:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=4),
        )
    else:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=8),
            A64RegOper(rm, va, size=8),
        )
    return opcode, mnem, olist, iflag, 0
        
        
    

def p_data_proc_3(opval, va):
    '''
    Data processing (3 source)
    '''
    sf = opval >> 31 & 0x1
    op54 = opval >> 29 & 0x3
    op31 = opval >> 21 & 0x7
    rm = opval >> 16 & 0x1f
    o0 = opval >> 15 & 0x1
    ra = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if op31 == 0b000:
        if o0 == 0b0:
            opcode = INS_MADD
            mnem = 'madd'
        else:
            opcode = INS_MSUB
            mnem = 'msub'
        if sf == 0b0:
            olist = (
                A64RegOper(rd, va, size = 4),
                A64RegOper(rn, va, size = 4),
                A64RegOper(rm, va, size = 4),
                A64RegOper(ra, va, size = 4),
            )
        else:
            olist = (
                A64RegOper(rd, va, size = 8),
                A64RegOper(rn, va, size = 8),
                A64RegOper(rm, va, size = 8),
                A64RegOper(ra, va, size = 8),
            )
    else:
        if op31 & 0b011 == 0b001:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
                A64RegOper(ra, va, size=8),
            )
            if op31 == 0b001:
                if o0 == 0b0:
                    mnem = 'smaddl'
                    opcode = INS_SMADDL
                else:
                    mnem = 'smsubl'
                    opcode = INS_SMSUBL
            elif op31 == 0b101:
                if o0 == 0b0:
                    mnem = 'umaddl'
                    opcode = INS_UMADDL
                else:
                    mnem = 'umsubl'
                    opcode = INS_UMSUBL
        elif op31 & 0b011 == 0b010:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
            )
            if op31 == 0b010:
                mnem = 'smulh'
                opcode = INS_SMULH
            else:
                mnem = 'umulh'
                opcode = INS_UMULH
        else:
            return p_undef(opval, va)
    return opcode, mnem, olist, 0, 0
            
def p_data_proc_2(opval, va):
    '''
    Data processing (2 source)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    s = opval >> 29 & 0x1
    rm = opval >> 16 & 0x1f
    opc = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if opc >> 4 & 0b1 == 0b0:
        if opc >> 3 & 0b1 == 0b0:
            if opc & 0b0 == 0b0:
                opcode = INS_UDIV
                mnem = 'udiv'
            else:
                opcode = INS_SDIV
                mnem = 'sdiv'
        else:
            if opc >> 1 & 0b1 == 0b0:
                if opc & 0b0 == 0b0:
                    opcode = INS_LSLV
                    mnem = 'lslv'
                else:
                    opcode = INS_LSRV
                    mnem = 'lsrv'
            else:
                if opc & 0b0 == 0b0:
                    opcode = INS_ASRV
                    mnem = 'asrv'
                else:
                    opcode = INS_RORV
                    mnem = 'rorv'
    if opc >> 2 & 0x1 == 0b1:
        iflag |= IF_C
    if sf == 0b0:
        #FIXME register shift encoded in rm
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=4),
        )
        if opc >> 4 & 0b1 != 0b0:
            opcode = INS_CRC32
            mnem = 'crc32'
            if opc & 0x3 == 0b00:
                iflag |= IF_B
            elif opc & 0x3 == 0b01:
                iflag |= IF_H
            elif opc & 0x3 == 0b10:
                iflag |= IF_W
    else:
        if opc >> 4 & 0b1 == 0b0:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
            )
        else:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=8),
            )
            opcode = INS_CRC32
            mnem = 'crc32'
            iflag |= IF_X

    return opcode, mnem, olist, 0, 0

def p_data_proc_1(opval, va):
    '''
    Data processing (1 source)
    '''
    iflag = 0
    sf = opval >> 31 & 0x1
    s = opval >> 29 & 0x1
    opcode2 = opval >> 16 & 0x1f
    opc = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if sf == 0b0:
        if opc & 0b111000 == 0b000000:
            opcode, mnem, iflag = data_proc_1_table_a[opc]
            if opcode != IENC_UNDEF:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=4),
                )
            else:
                olist = (
                    A64ImmOper(opval),
                )
        else:
            return p_undef(opval, va)
    else:
        if opc & 0b111000 == 0b000000:
            opcode, mnem, iflag = data_proc_1_table_b[opc]
            if opcode != IENC_UNDEF:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=8),
                )
            else:
                olist = (
                    A64ImmOper(opval),
                )
        else:
            return p_undef(opval, va)
    return opcode, mnem, olist, iflag, 0


data_proc_1_table_a = (
    (INS_RBIT, 'rbit', 0),
    (INS_REV, 'rev', IF_16),
    (INS_REV, 'rev', 0),
    (IENC_UNDEF, 'undefined instruction', 0),
    (INS_CL, 'cl', IF_Z),
    (INS_CL, 'cl', IF_S),
    (IENC_UNDEF, 'undefined instruction', 0),
    (IENC_UNDEF, 'undefined instruction', 0),   
)

data_proc_1_table_b = (
    (INS_RBIT, 'rbit', 0),
    (INS_REV, 'rev', IF_16),
    (INS_REV, 'rev', IF_32),
    (INS_REV, 'rev', 0),
    (INS_CL, 'cl', IF_Z),
    (INS_CL, 'cl', IF_S),
    (IENC_UNDEF, 'undefined instruction', 0),
    (IENC_UNDEF, 'undefined instruction', 0),   
)

datasimdtable = (   # FIXME: Fascinating.... 
    (0x5f200000, 0x1e000000, IENC_FP_FP_CONV), #p_fp_fp_conv
    (0x5f200c00, 0x1e200400, IENC_FP_COND_COMPARE), #p_fp_cond_compare
    (0x5f200c00, 0x1e200800, IENC_FP_DP2), #p_fp_dp2
    (0x5f200c00, 0x1e200c00, IENC_FP_COND_SELECT), #p_fp_cond_select
    (0x5f201c00, 0x1e201000, IENC_FP_IMMEDIATE), #p_fp_immediate
    (0x5f203c00, 0x1e202000, IENC_FP_COMPARE), #p_fp_compare
    (0x5f207c00, 0x1e204000, IENC_FP_DP1), #p_fp_dp1
    (0x5f20fc00, 0x1e200000, IENC_FP_INT_CONV), #p_fp_int_conv
    (0x5f000000, 0x1f000000, IENC_FP_DP3), #p_fp_dp3
    (0x9f200400, 0x0e200400, IENC_SIMD_THREE_SAME), #p_simd_three_same
    (0x9f200c00, 0x0e200000, IENC_SIMD_THREE_DIFF), #p_simd_three_diff
    (0x9f3e0c00, 0x0e200800, IENC_SIMD_TWOREG_MISC), #p_simd_tworeg_misc
    (0x9f3e0c00, 0x0e300800, IENC_SIMD_ACROSS_LANES), #p_simd_across_lanes
    (0x9fe08400, 0x0e000400, IENC_SIMD_COPY), #p_simd_copy
    (0x9f000400, 0x0f000000, IENC_SIMD_VECTOR_IE), #p_simd_vector_ie
    (0x9f800400, 0x0f000400, IENC_SIMD_MOD_SHIFT_IMM), #p_simd_mod_shift_imm
    (0xbf208c00, 0x0e000000, IENC_SIMD_TBL_TBX), #p_simd_tbl_tbx
    (0xbf208c00, 0x0e000800, IENC_SIMD_ZIP_UZP_TRN), #p_simd_zip_uzp_trn
    (0xbf208400, 0x2e000000, IENC_SIMD_EXT), #p_simd_ext
    (0xdf200400, 0x5e200400, IENC_SIMD_SCALAR_THREE_SAME), #p_simd_scalar_three_same
    (0xdf200c00, 0x5e200000, IENC_SIMD_SCALAR_THREE_DIFF), #p_simd_scalar_three_diff
    (0xdf3e0c00, 0x5e200800, IENC_SIMD_SCALAR_TWOREG_MISC), #p_simd_scalar_tworeg_misc
    (0xdf3e0c00, 0x5e300800, IENC_SIMD_SCALAR_PAIRWISE), #p_simd_scalar_pairwise
    (0xdfe08400, 0x5e300800, IENC_SIMD_SCALAR_COPY), #p_simd_scalar_copy
    (0xdf000400, 0x5f000000, IENC_SIMD_SCALAR_IE), #p_simd_scalar_ie
    (0xdf800400, 0x5f000400, IENC_SIMD_SCALAR_SHIFT_IMM), #p_simd_scalar_shift_imm
    (0xff3e0c00, 0x4e280800, IENC_CRPYTO_AES), #p_crypto_aes
    (0xff208c00, 0x5e000000, IENC_CRYPTO_THREE_SHA), #p_crypto_three_sha
    (0xff3e0c00, 0x5e280800, IENC_CRYPTO_TWO_SHA), #p_crypto_two_sha
)
def p_data_simd(opval, va):
    for mask,val,penc in datasimdtable:
        if (opval & mask) == val:
            enc = penc
            break
    opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va)
    return opcode, mnem, olist, flags, simdflags

def p_fp_fp_conv(opval, va):
    '''
    Floating-point<->fixed-point conversions
    '''
    sf = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    mode = opval >> 19 & 0x3
    opcode = opval >> 16 & 0x7
    scale = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    relevant = s + mode + opcode
    #First get the mnem and opcode
    if relevant == 0b00000010:
        mnem = 'scvtf'
        opcode = INS_SCVTF
    elif relevant == 0b00000011:
        mnem = 'ucvtf'
        opcode = INS_UCVTF
    elif relevant == 0b00011000:
        mnem = 'fcvtzs'
        opcode = INS_FCVTZS
    elif relevant == 0b00011001:
        mnem = 'fcvtzu'
        opcode = INS_FCVTZU
    else:
        return p_undef(opval, va)

    if sf == 0 and typ == 0b00:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
            A64ImmOper(64-scale),
        )
    elif sf == 0 and typ == 0b01:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=4),
            A64ImmOper(64-scale),
        )
    elif sf == 1 and typ == 0b00:
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=8),
            A64ImmOper(64-scale),
        )
    elif sf == 1 and typ == 0b01:
        olist = (
            A64RegOper(rd, va, size=8),
            A64RegOper(rn, va, size=8),
            A64ImmOper(64-scale),
        )
    else:
        return p_undef(opval, va)
    return opcode, mnem, olist, 0, 0

def p_fp_cond_compare(opval, va):
    '''
    Floating-point conditional compare
    '''
    iflag = 0
    m = opval >> 31 & 0x1
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    cond = opval >> 12 & 0xf
    rn = opval >> 5 & 0x1f
    op = opval >> 4 & 0x1
    nzcv = opval & 0xf
    mnem = 'fccmp'
    opcode = INS_FCCMP
    if m == 0 and s == 0 and op == 0:
        iflags |= 0
    elif m == 0 and s == 0 and op == 1:
        iflags |= IF_E
    else:
        return p_undef(opval, va)
    if typ == 0b00:
        olist = (
            A64RegOper(rn, va, size=32),
            A64RegOper(rm, va, size=32),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )
    elif typ == 0b01:
        olist = (
            A64RegOper(rn, va, size=64),
            A64RegOper(rm, va, size=64),
            A64nzcvOper(nzcv),
            A64CondOper(cond),
        )
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflags, 0

fp_dp2_table = (
    (INS_FMUL, 'fmul'),
    (INS_FDIV, 'fdiv'),
    (INS_FADD, 'fadd'),
    (INS_FSUB, 'fsub'),
    (INS_FMAX, 'fmax'),
    (INS_FMIN, 'fmin'),
    (INS_FMAXNM, 'fmaxnm'),
    (INS_FMINNM, 'fminnm'),
    (INS_FNMUL, 'fnmul'),
    (0, 0),
)
def p_fp_dp2(opval, va):
    '''
    Floating-point data processing (2 source)
    '''
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if m + s == 0:
        opcode, mnem = fp_dp2_table[opc]
        if typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
            )
        elif typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
            )
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)
    return opcode, mnem, olist, 0, 0

def p_fp_cond_select(opval, va):
    '''
    Floating-point conditional select
    '''
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    cond = opval >> 12 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    mnem = 'fcsel'
    opcode = INS_FCSEL
    if m == 0 and s == 0:
        if typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
                #cond
            )
        elif typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
                #cond
            )
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)
    return opcode, mnem, olist, 0, 0

def p_fp_immediate(opval, va):
    '''
    Floating-point immediate
    '''
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    o1 = opval >> 21 & 0x1
    rm = opval >> 16 & 0x1f
    o0 = opval >> 15 & 0x1
    ra = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if o0 == 0:
        if o1 == 0:
            mnem = 'fmadd'
            opcode = INS_FMADD
        else:
            mnem = 'fnmadd'
            opcode = INS_FNMADD
    else:
        if o1 == 0:
            mnem = 'fmsub'
            opcode = INS_FMSUB
        else:
            mnem = 'fnmsub'
            opcode = INS_FNMSUB
    if m == 0 and s == 0:
        if typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
                A64RegOper(ra, va, size=4),
            )
        elif typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
                A64RegOper(rm, va, size=8),
                A64RegOper(ra, va, size=8),
            )
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)
    
    return opcode, mnem, olist, 0, 0

def p_fp_compare(opval, va):
    '''
    Floating-point compare
    '''
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    op = opval >> 14 & 0x3
    rn = opval >> 5 & 0x1f
    opcode2 = opval & 0x1f
    mnem = 'fcmp'
    opcode = INS_FCMP
    if m == 0 and s == 0 and op == 0b00:
        if typ == 0b00:
            if opcode2 == 0b00000 or opcode2 == 0b10000:
                olist = (
                    A64RegOper(rn, va, size=4),
                    A64RegOper(rm, va, size=4),
                )
            elif opcode2 == 0b01000 or opcode2 == 0b11000:
                olist = (
                    A64RegOper(rn, va, size=4),
                    A64ImmOper(0, va=va),
                )
            else:
                return p_undef(opval, va)
        elif typ == 0b01:
            if opcode2 == 0b00000 or opcode2 == 0b10000:
                olist = (
                    A64RegOper(rn, va, size=8),
                    A64RegOper(rm, va, size=8),
                )
            elif opcode2 == 0b01000 or opcode2 == 0b11000:
                olist = (
                    A64RegOper(rn, va, size=8),
                    A64ImmOper(0, va=va),
                )
            else:
                return p_undef(opval, va)
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)
    if opcode2 >> 4 == 1:
        iflags |= IF_E
    return opcode, mnem, olist, iflags, 0

fp_dp1_table = (
    ('fmov', INS_FMOV, 0),
    ('fabs', INS_FABS, 0),
    ('fneg', INS_FNEG, 0),
    ('fsqrt', INS_FSQRT, 0),
    (0, 0, 0), #Missing instr
    ('fcvt', INS_FCVT, 0),
    (0, 0, 0), #Missing instr
    ('fcvt', INS_FCVT, 0),
    ('frint', INS_FRINT, IF_N),
    ('frint', INS_FRINT, IF_P),
    ('frint', INS_FRINT, IF_M),
    ('frint', INS_FRINT, IF_Z),
    ('frint', INS_FRINT, IF_A),
    ('frint', INS_FRINT, IF_X),
    (0, 0, 0), #Missing instr
    ('frint', INS_FRINT, IF_I),
    (0, 0, 0), #Catch-all
)
def p_fp_dp1(opval, va):
    '''
    Floating-point data processing (1 source)
    '''
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    opc = opval >> 15 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    mnem, opcode, iflags = fp_dp1_table[opc]
    if mnem == 0:
        return p_undef(opval, va)
    elif m == 0 and s == 0:
        if typ == 0b00:
            if opc == 0b000101:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=4),
                )
            elif opc == 0b000111:
                olist = (
                    #16 Register (rd)
                    A64RegOper(rn, va, size=4)
                )
            else:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=4),
                )
        elif typ == 0b01:
            if opc == 0b000100:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=8),
                )
            elif opc == 0b000111:
                olist = (
                    #16 Register (rd)
                    A64RegOper(rn, va, size=8),
                )
            else:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=8),
                )
        elif typ == 0b11:
            if opc == 0b000100:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=2),
                )
            elif opc == 0b000111:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=2),
                )
            else:
                return p_undef(opval, va)
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflags, 0

def p_fp_int_conv(opval, va):
    '''
    Floating-point<->integer conversions
    '''
    iflag = 0
    sf = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    rmode = opval >> 19 & 0x3
    opc = opval >> 16 & 0x7
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if opc >> 1 & 0x1 == 0:
        mnem = 'fcvt'
        opcode = INS_FCVT
        if rmode == 0b00:
            if opc >> 2 & 0x1 == 0:
                iflags |= IF_N
            else:
                iflags |= IF_A
        elif rmode == 0b01:
            iflags |= IF_P
        elif rmode == 0b10:
            iflags |= IF_M
        else:
            iflags |= IF_Z
        if opc >> 0 & 0x1 == 0:
            iflags |= IF_S
        else:
            iflags |= IF_U
        
        if sf == 0 and typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
            )
        elif sf == 0 and typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=8),
            )
        elif sf == 1 and typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=4),
            )
        elif sf == 1 and typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=8),
                A64RegOper(rn, va, size=8),
            )
        else:
            return p_undef(opval, va)
    else:
        if opc >> 2 & 0x1 == 0:
            if opc >> 0 & 0x1 == 0:
                mnem = 'scvtf'
                opcode = INS_SCVTF
                iflags = 0
            else:
                mnem = 'ucvtf'
                opcode = INS_UCVTF
                iflags = 0
            if sf == 0 and typ == 0b00:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=4),
                )
            elif sf == 0 and typ == 0b01:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=4),
                )
            elif sf == 1 and typ == 0b00:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rn, va, size=8),
                )
            elif sf == 1 and typ == 0b01:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=8),
                )
        else:
            mnem = 'fmov'
            opcode = INS_FMOV
            iflags = 0
            if sf == 0 and typ == 0b00 and rmode == 0b00 and opc & 0x1 == 1:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rd, va, size=4),
                )
            elif sf == 0 and typ == 0b00 and rmode == 0b00 and opc & 0x1 == 0:
                olist = (
                    A64RegOper(rd, va, size=4),
                    A64RegOper(rd, va, size=4),
                )
            elif sf == 1 and typ == 0b01 and rmode == 0b00 and opc & 0x1 == 1:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=8),
                )
            elif sf == 1 and typ == 0b10 and rmode == 0b01 and opc & 0x1 == 1:
                olist = (
                    #top half of 128-bit reg (rd)
                    A64RegOper(rn, va, size=8),
                )
            elif sf == 1 and typ == 0b01 and rmode == 0b00 and opc & 0x1 == 0:
                olist = (
                    A64RegOper(rd, va, size=8),
                    A64RegOper(rn, va, size=8),
                )
            elif sf == 1 and typ == 0b10 and rmode == 0b01 and opc & 0x1 == 1:
                olist = (
                    A64RegOper(rd, va, size=8),
                    #top half of 128-bit reg (rn)
                )
            else:
                return p_undef(opval, va)
    return opcode, mnem, olist, iflags, 0

def p_fp_dp3(opval, va):
    '''
    Floating-point data processing (3 source)
    '''
    iflag = 0
    m = opval >> 31
    s = opval >> 29 & 0x1
    typ = opval >> 22 & 0x3
    o1 = opval >> 21 & 0x1
    rm = opval >> 16 & 0x1f
    o0 = opval >> 15 & 0x1
    ra = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if m == 0 and s == 0:
        if o1 == 0 and o0 == 0:
            mnem = 'fmadd'
            opcode = INS_FMADD
        elif o1 == 0 and o0 == 1:
            mnem = 'fmsub'
            opcode = INS_FMSUB
        elif o1 == 1 and o0 == 0:
            mnem = 'fnmadd'
            opcode = INS_FNMADD
        else:
            mnem = 'fnmsub'
            opcode = INS_FNMSUB
        if typ == 0b00:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
                A64RegOper(ra, va, size=4),
            )
        elif typ == 0b01:
            olist = (
                A64RegOper(rd, va, size=4),
                A64RegOper(rn, va, size=4),
                A64RegOper(rm, va, size=4),
                A64RegOper(ra, va, size=4),
            )
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0

def p_simd_three_same(opval, va):
    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 11 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if u == 0:
        if opc == 0b00000:
            mnem = 'shadd'
            opcode = INS_SHADD
            olist = (
                #FIXME
            )
        elif opc == 0b00001:
            mnem = 'sqadd'
            opcode = INS_SQADD
            olist = (
                #FIXME
            )
        elif opc == 0b00010:
            mnem = 'srhadd'
            opcode = INS_SRHADD
            olist = (
                #FIXME
            )
        elif opc == 0b00100:
            mnem = 'shsub'
            opcode = INS_SHSUB
            olist = (
                #FIXME
            )
        elif opc == 0b00101:
            mnem = 'sqsub'
            opcode = INS_SQSUB
            olist = (
                #FIXME
            )
        elif opc == 0b00110:
            mnem = 'cmgt'
            opcode = INS_CMGT
            olist = (
                #FIXME
            )
        elif opc == 0b00111:
            mnem = 'cmge'
            opcode = INS_CMGE
            olist = (
                #FIXME
            )
        elif opc == 0b01000:
            mnem = 'sshl'
            opcode = INS_SSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01001:
            mnem = 'sqshl'
            opcode = INS_SQSHL
            olist = (
                #FIXME
            )
        elif opc == 0b1010:
            mnem = 'srshl'
            opcode = INS_SRSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01011:
            mnem = 'sqrshl'
            opcode = INS_SQRSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01100:
            mnem = 'smax'
            opcode = INS_SMAX
            olist = (
                #FIXME
            )
        elif opc == 0b01101:
            mnem = 'smin'
            opcode = INS_SMIN
            olist = (
                #FIXME
            )
        elif opc == 0b01110:
            mnem = 'sabd'
            opcode = INS_SABD
            olist = (
                #FIXME
            )
        elif opc == 0b01111:
            mnem = 'saba'
            opcode = INS_SABA
            olist = (
                #FIXME
            )
        elif opc == 0b10000:
            mnem = 'add'
            opcode = INS_ADD
            olist = (
                #FIXME
            )
        elif opc == 0b10001:
            mnem = 'cmtst'
            opcode = INS_CMTST
            olist = (
                #FIXME
            )
        elif opc == 0b10010:
            mnem = 'mla'
            opcode = INS_MLA
            olist = (
                #FIXME
            )
        elif opc == 0b10011:
            mnem = 'mul'
            opcode = INS_MUL
            olist = (
                #FIXME
            )
        elif opc == 0b10100:
            mnem = 'smaxp'
            opcode = INS_SMAXP
            olist = (
                #FIXME
            )
        elif opc == 0b10101:
            mnem = 'sminp'
            opcode = INS_SMINP
            olist = (
                #FIXME
            )
        elif opc == 0b10110:
            mnem = 'sqdmulh'
            opcode = INS_SQDMULH
            olist = (
                #FIXME
            )
        elif opc == 0b10111:
            mnem = 'addp'
            opcode = INS_ADDP
            olist = (
                #FIXME
            )
        if size == 0b00 or size == 0b01:
            if opc == 0b11000:
                mnem = 'fmaxnm'
                opcode = INS_FMAXNM
                olist = (
                    #FIXME
                )
            elif opc == 0b11001:
                mnem = 'fmla'
                opcode = INS_FMLA
                olist = (
                    #FIXME
                )
            elif opc == 0b11010:
                mnem = 'fadd'
                opcode = INS_FADD
                olist = (
                    #FIXME
                )
            elif opc == 0b11011:
                mnem = 'fmulx'
                opcode = INS_FMULX
                olist = (
                    #FIXME
                )
            elif opc == 0b11100:
                mnem = 'fcmeq'
                opcode = INS_FCMEQ
                olist = (
                    #FIXME
                )
            elif opc == 0b11110:
                mnem = 'fmax'
                opcode = INS_FMAX
                olist = (
                    #FIXME
                )
            elif opc == 0b11111:
                mnem = 'frecps'
                opcode = INS_FRECPS
                olist = (
                    #FIXME
                )
            if size == 0b00 and opc == 0b00011:
                mnem = 'and'
                opcode = INS_AND
                olist = (
                    #FIXME
                )
            elif size == 0b01 and opc == 0b00011:
                mnem = 'bic'
                opcode = INS_BIC
                olist = (
                    #FIXME
                )
        elif size == 0b10 or size == 0b11:
            if opc == 0b11000:
                mnem = 'fminnm'
                opcode = INS_FMINNM
                olist = (
                    #FIXME
                )
            elif opc == 0b11001:
                mnem = 'fmls'
                opcode = INS_FMLS
                olist = (
                    #FIXME
                )
            elif opc == 0b11010:
                mnem = 'fsub'
                opcode = INS_FSUB
                olist = (
                    #FIXME
                )
            elif opc == 0b11110:
                mnem = 'fmin'
                opcode = INS_FMIN
                olist = (
                    #FIXME
                )
            elif opc == 0b11111:
                mnem = 'frsqrts'
                opcode = INS_FRSQRTS
                olist = (
                    #FIXME
                )
            if size == 0b10 and opc == 0b00011:
                mnem = 'orr'
                opcode = INS_ORR
                olist = (
                    #FIXME
                )
            elif size == 0b11 and opc == 0b00011:
                mnem = 'orn'
                opcode = INS_ORN
                olist = (
                    #FIXME
                )
    else:
        if opc == 0b00000:
            mnem = 'uhadd'
            opcode = INS_UHADD
            olist = (
                #FIXME
            )
        elif opc == 0b00001:
            mnem = 'uqadd'
            opcode = INS_UQADD
            olist = (
                #FIXME
            )
        elif opc == 0b00010:
            mnem = 'urhadd'
            opcode = INS_URHADD
            olist = (
                #FIXME
            )
        elif opc == 0b00100:
            mnem = 'uhsub'
            opcode = INS_UHSUB
            olist = (
                #FIXME
            )
        elif opc == 0b00101:
            mnem = 'uqsub'
            opcode = INS_UQSUB
            olist = (
                #FIXME
            )
        elif opc == 0b00110:
            mnem = 'cmhi'
            opcode = INS_CMHI
            olist = (
                #FIXME
            )
        elif opc == 0b00111:
            mnem = 'cmhs'
            opcode = INS_CMHS
            olist = (
                #FIXME
            )
        elif opc == 0b01000:
            mnem = 'uhsl'
            opcode = INS_UHSL
            olist = (
                #FIXME
            )
        elif opc == 0b01001:
            mnem = 'uqshl'
            opcode = INS_UQSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01010:
            mnem = 'urshl'
            opcode = INS_URSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01011:
            mnem = 'uqrshl'
            opcode = INS_UQRSHL
            olist = (
                #FIXME
            )
        elif opc == 0b01100:
            mnem = 'umax'
            opcode = INS_UMAX
            olist = (
                #FIXME
            )
        elif opc == 0b01101:
            mnem = 'umin'
            opcode = INS_UMIN
            olist = (
                #FIXME
            )
        elif opc == 0b01110:
            mnem = 'uabd'
            opcode = INS_UABD
            olist = (
                #FIXME
            )
        elif opc == 0b01111:
            mnem = 'uaba'
            opcode = INS_UABA
            olist = (
                #FIXME
            )
        elif opc == 0b10000:
            mnem = 'sub'
            opcode = INS_SUB
            olist = (
                #FIXME
            )
        elif opc == 0b10001:
            mnem = 'cmeq'
            opcode = INS_CMEQ
            olist = (
                #FIXME
            )
        elif opc == 0b10010:
            mnem = 'mls'
            opcode = INS_MLS
            olist = (
                #FIXME
            )
        elif opc == 0b10011:
            mnem = 'pmul'
            opcode = INS_PMUL
            olist = (
                #FIXME
            )
        elif opc == 0b10100:
            mnem = 'umaxp'
            opcode = INS_UMAXP
            olist = (
                #FIXME
            )
        elif opc == 0b10101:
            mnem = 'uminp'
            opcode = INS_UMINP
            olist = (
                #FIXME
            )
        elif opc == 0b10110:
            mnem = 'sqrdmulh'
            opcode = INS_URHADD
            olist = (
                #FIXME
            )
        if size == 0b00 or size == 0b01:
            if opc == 0b11000:
                mnem = 'fmaxnmp'
                opcode = INS_FMAXNMP
                olist = (
                    #FIXME
                )
            if opc == 0b11010:
                mnem = 'faddp'
                opcode = INS_FADDP
                olist = (
                    #FIXME
                )
            if opc == 0b11011:
                mnem = 'fmul'
                opcode = INS_FMUL
                olist = (
                    #FIXME
                )
            if opc == 0b11100:
                mnem = 'fcmge'
                opcode = INS_fcmge
                olist = (
                    #FIXME
                )
            if opc == 0b11101:
                mnem = 'facge'
                opcode = INS_FACGE
                olist = (
                    #FIXME
                )
            if opc == 0b11110:
                mnem = 'fmaxp'
                opcode = INS_FMAXP
                olist = (
                    #FIXME
                )
            if opc == 0b11111:
                mnem = 'fdiv'
                opcode = INS_FDIV
                olist = (
                    #FIXME
                )
            if opc == 0b11000:
                mnem = 'fmaxnmp'
                opcode = INS_FMAXNMP
                olist = (
                    #FIXME
                )
            if size == 0b00 and opc == 0b00011:
                mnem = 'eor'
                opcode = INS_EOR
                olist = (
                    #FIXME
                )
            if size == 0b01 and opc == 0b00011:
                mnem = 'bsl'
                opcode = INS_BSL
                olist = (
                    #FIXME
                )
        elif size == 0b10 or size == 0b11:
            if opc == 0b11000:
                mnem = 'fminnmp'
                opcode = INS_FMINNMP
                olist = (
                    #FIXME
                )
            if opc == 0b11010:
                mnem = 'fabd'
                opcode = INS_FABD
                olist = (
                    #FIXME
                )
            if opc == 0b11100:
                mnem = 'fcmgt'
                opcode = INS_FMAXNMP
                olist = (
                    #FIXME
                )
            if opc == 0b11101:
                mnem = 'facgt'
                opcode = INS_FCMGT
                olist = (
                    #FIXME
                )
            if opc == 0b11110:
                mnem = 'fminp'
                opcode = INS_FMAXNMP
                olist = (
                    #FIXME
                )
            if size == 0b10 and opc == 0b00011:
                mnem = 'bit'
                opcode = INS_BIT
                olist = (
                    #FIXME
                )
            if size == 0b11 and opc == 0b00011:
                mnem = 'bif'
                opcode = INS_BIF
                olist = (
                    #FIXME
                )
    return opcode, mnem, olist, 0, 0

simd_three_diff_table = (
    (INS_ADD, 'add', (IF_L,), 'abb'),
    (INS_ADD, 'add', (IF_W,), 'aab'),
    (INS_SUB, 'sub', (IF_L,), 'abb'),
    (INS_SUB, 'sub', (IF_W,), 'aab'),
    (INS_ADDHN, 'addhn', (), 'baa'),
    (INS_ABA, 'aba', (IF_L,), 'abb'),
    (INS_SUBHN, 'subhn', (), 'baa'),
    (INS_ABD, 'abd', (IF_L,), 'abb'),
    (INS_MLA, 'mla', (IF_L,), 'abb'),
    (INS_MLA, 'mla', (IFP_QD, IF_L,), 'abb'), 
    (INS_MLS, 'mls', (IF_L,), 'abb'),
    (INS_MLS, 'mls', (IFP_QD, IF_L,), 'abb'),
    (INS_MUL, 'mul', (IF_L,), 'abb'),
    (INS_MUL, 'mul', (IFP_QD, IF_L,), 'abb'),
    (INS_MUL, 'mul', (IF_L,), 'abb'),
    
)
def p_simd_three_diff(opval, va):
    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if q == 1:
        iflags |= IF_2
    opcode, mnem, flags, pattern = simd_three_diff_table[opc]
    for flag in flags:
        iflags |= flag
    if (opcode == INS_ADDHN or opcode == INS_SUBHN) and u == 1:
        iflags |= IFP_R
    elif opc == 0b1110:
        iflags |= IFP_P
    else:
        if u == 0:
            iflags |= IFP_S
        else:
            iflags |= IFP_U
    ta = 0
    tb = 0
    if size == 0b00:
        ta = IFS_8H
        if q == 0:
            tb = IFS_8B
        else:
            tb = IFS_16B
    elif size == 0b01:
        ta = IFS_4S
        if q == 0:
            tb = IFS_4H
        else:
            tb = IFS_8H
    elif size == 0b10:
        ta = IFS_2D
        if q == 0:
            tb = IFS_2S
        else:
            tb = IFS_4S
    if pattern == 'abb':
        olist = (
            A64RegOper(rd, oflags=ta),
            A64RegOper(rn, oflags=tb),
            A64RegOper(rm, oflags=tb),
        )
    if pattern == 'aab':
        olist = (
            A64RegOper(rd, oflags=ta),
            A64RegOper(rn, oflags=ta),
            A64RegOper(rm, oflags=tb),
        )
    if pattern == 'baa':
        olist = (
            A64RegOper(rd, oflags=tb),
            A64RegOper(rn, oflags=ta),
            A64RegOper(rm, oflags=ta),
        )
    return opcode, mnem, olist, iflags, 0

def p_simd_tworeg_misc(opval, va):
    iflag = 0
    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if u == 0:
        if opc == 0b00000: #1
            opcode = INS_REV64
            mnem = 'rev64'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00001: #2
            opcode = INS_REV16
            mnem = 'rev16'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00010: #3
            if size == 0b00 and q == 0:
                ta = IFS_4H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_2S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_1D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            opcode = INS_ADDL
            mnem = 'addl'
            iflag |= IFP_S
            iflag |= IF_P
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif opc == 0b00011: #4
            opcode = INS_UQADD
            mnem = 'uqadd'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            iflag |= IFP_S
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00100: #1
            opcode = INS_CLS
            mnem = 'cls'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00101: #2
            opcode = INS_CNT
            mnem = 'cnt'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00110: #3
            opcode = INS_CLS
            mnem = 'cls'
            if size == 0b00 and q == 0:
                ta = IFS_4H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_2S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_1D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            iflag |= IF_P
            iflag |= IF_L
            iflag |= IFP_S
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif opc == 0b00111: #4
            opcode = INS_qabs
            mnem = 'qabs'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            iflag |= IFP_S
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b01000: #4
            opcode = INS_CMGT
            mnem = 'cmgt'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
                A64ImmOper(0),
            )
        elif opc == 0b01001: #4
            opcode = INS_CMEQ
            mnem = 'cmeq'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
                A64ImmOper(0),
            )
        elif opc == 0b01010: #4
            opcode = INS_CMLT
            mnem = 'cmlt'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
                A64ImmOper(0),
            )
        elif opc == 0b01011: #4
            opcode = INS_ABS
            mnem = 'abs'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b10010: #5
            if q == 1:
                iflag |= IF_2
            opcode = INS_XTN
            mnem = 'xtn'
            if size == 0b00 and q == 0:
                ta = IFS_8H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_4S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_2D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif opc == 0b10100: #5
            if q == 1:
                iflag |= IF_2
            iflag |= IFP_S
            opcode = INS_QXTN
            mnem = 'qxtn'
            if size == 0b00 and q == 0:
                ta = IFS_8H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_4S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_2D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif size == 0b00 or size == 0b01: 
            if opc == 0b10110: #6
                if q == 1:
                    iflag |= IF_2
                iflag |= IF_N
                iflag |= IFP_F
                opcode = INS_CVT
                mnem = 'cvt'
                if size == 0b00 and q == 0:
                    ta = IFS_4S
                    tb = IFS_4H
                elif size == 0b00 and q == 1:
                    ta = IFS_4S
                    tb = IFS_8H
                elif size == 0b01 and q == 0:
                    ta = IFS_2D
                    tb = IFS_2S
                elif size == 0b01 and q == 1:
                    ta = IFS_2D
                    tb = IFS_4S
                olist = (
                    A64RegOper(rd, oflags=tb),
                    A64RegOper(rn, oflags=ta),
                )
            elif opc == 0b10111: #6
                if q == 1:
                    iflag |= IF_2
                iflag |= IFP_F
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IF_L
                if size == 0b00 and q == 0:
                    ta = IFS_4S
                    tb = IFS_4H
                elif size == 0b00 and q == 1:
                    ta = IFS_4S
                    tb = IFS_8H
                elif size == 0b01 and q == 0:
                    ta = IFS_2D
                    tb = IFS_2S
                elif size == 0b01 and q == 1:
                    ta = IFS_2D
                    tb = IFS_4S
                olist = (
                    A64RegOper(rd, oflags=ta),
                    A64RegOper(rn, oflags=tb),
                )
            elif opc == 0b11000: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_N
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11001: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_M
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11010: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_N
                iflag |= IF_S
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11011: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_M
                iflag |= IF_S
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11100: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_A
                iflag |= IF_S
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11101: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IF_F
                iflag |= IFP_S
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
        elif size == 0b10 or size == 0b11:
            if opc == 0b01100: #7
                opcode = INS_CMGT
                mnem = 'cmgt'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                    A64ImmOper(0),
                )
            elif opc == 0b01101: #7
                opcode = INS_CMEQ
                mnem = 'cmeq'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                    A64ImmOper(0),
                )
            elif opc == 0b01110: #7
                opcode = INS_CMLT
                mnem = 'cmlt'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                    A64ImmOper(0),
                )
            elif opc == 0b01111: #7
                opcode = INS_ABS
                mnem = 'abs'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11000: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_P
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11001: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_Z
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11010: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_P
                iflag |= IF_S
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11011: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_P
                iflag |= IF_S
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11100: #8
                opcode = INS_RECPE
                mnem = 'recpe'
                iflag |= IFP_U
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11101: #7
                opcode = INS_RECPE
                mnem = 'recpe'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
    else: #u == 1
        if opc == 0b00000: #9 
            opcode = INS_REV32
            mnem = 'rev32'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00010: #3
            opcode = INS_ADDL
            mnem = 'addl'
            iflag |= IFP_U
            iflag |= IF_P
            if size == 0b00 and q == 0:
                ta = IFS_4H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_2S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_1D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif opc == 0b00011: #4
            opcode = INS_SQADD
            mnem = 'sqadd'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            iflag |= IFP_U
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00100: #1
            opcode = INS_CLZ
            mnem = 'clz'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            iflag |= IFP_U
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b00110: #3
            opcode = INS_ADAL
            mnem = 'adal'
            iflag |= IFP_U
            iflag |= IF_P
            if size == 0b00 and q == 0:
                ta = IFS_4H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_2S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_1D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
            )
        elif opc == 0b00111: #4
            opcode = INS_SQNEG
            mnem = 'sqneg'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b01000: #4
            opcode = INS_CMGE
            mnem = 'cmge'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
                A64ImmOper(0),
            )
        elif opc == 0b01001: #4
            opcode = INS_CMLE
            mnem = 'cmle'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
                A64ImmOper(0),
            )
        elif opc == 0b01011: #4
            opcode = INS_NEG
            mnem = 'neg'
            if size == 0b00 and q == 0:
                t = IFS_8B
            elif size == 0b00 and q == 1:
                t = IFS_16B
            elif size == 0b01 and q == 0:
                t = IFS_4H
            elif size == 0b01 and q == 1:
                t = IFS_8H
            elif size == 0b10 and q == 0:
                t = IFS_2S
            elif size == 0b10 and q == 1:
                t = IFS_4S
            elif size == 0b11 and q == 1:
                t = IFS_2D
            olist = (
                A64RegOper(rd, oflags=t),
                A64RegOper(rn, oflags=t),
            )
        elif opc == 0b10010: #5
            opcode = INS_QXTUN
            mnem = 'qxtun'
            if q == 1:
                iflag |= IF_2
            iflag |= IFP_S
            if size == 0b00 and q == 0:
                ta = IFS_8H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_4S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_2D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=tb),
                A64RegOper(rn, oflags=ta),
            )
        elif opc == 0b10011: #5 WITH EXTRA OLIST OPER
            opcode = INS_SHL
            mnem = 'shl'
            if q == 1:
                iflag |= IF_2
            iflag |= IF_L
            if size == 0b00 and q == 0:
                ta = IFS_8H
                tb = IFS_8B
                shift = 8
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
                shift = 8
            elif size == 0b01 and q == 0:
                ta = IFS_4S
                tb = IFS_4H
                shift = 16
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
                shift = 16
            elif size == 0b10 and q == 0:
                ta = IFS_2D
                tb = IFS_2S
                shift = 32
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
                shift = 32
            olist = (
                A64RegOper(rd, oflags=ta),
                A64RegOper(rn, oflags=tb),
                A64RegOper(shift),
            )
        elif opc == 0b10100: #5
            opcode = INS_QXTN
            mnem = 'qxtn'
            if q == 1:
                iflag |= IF_2
            iflag |= IFP_U
            if size == 0b00 and q == 0:
                ta = IFS_8H
                tb = IFS_8B
            elif size == 0b00 and q == 1:
                ta = IFS_8H
                tb = IFS_16B
            elif size == 0b01 and q == 0:
                ta = IFS_4S
                tb = IFS_4H
            elif size == 0b01 and q == 1:
                ta = IFS_4S
                tb = IFS_8H
            elif size == 0b10 and q == 0:
                ta = IFS_2D
                tb = IFS_2S
            elif size == 0b10 and q == 1:
                ta = IFS_2D
                tb = IFS_4S
            olist = (
                A64RegOper(rd, oflags=tb),
                A64RegOper(rn, oflags=ta),
            )
        elif size == 0b00 or size == 0b01:
            if opc == 0b10110: #9
                opcode = INS_CVT
                mnem = 'cvt'
                if q == 1:
                    iflag |= IF_2
                iflag |= IFP_F
                iflag |= IF_X
                iflag |= IF_N
                if size == 0b01 and q == 0:
                    tb = IFS_2S
                    ta = IFS_2D
                if size == 0b01 and q == 1:
                    tb = IFS_4S
                    ta = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=tb),
                    A64RegOper(rn, oflags=ta),
                )
            elif opc == 0b11000: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_A
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11001: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_X
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11010: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_N
                iflag |= IF_U
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11011: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_M
                iflag |= IF_U
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11100: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_A
                iflag |= IF_U
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b11101: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_U
                iflag |= IF_F
                if size == 0b00 and q == 0:
                    t = IFS_2S
                elif size == 0b00 and q == 1:
                    t = IFS_4S
                elif size == 0b01 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b00101 and size == 0b00: #10
                opcode = INS_NOT
                mnem = 'not'
                if q == 0:
                    t = IFS_8B
                elif q == 1:
                    t = IFS_16Bs
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            elif opc == 0b00101 and size == 0b01: #10
                opcode = INS_RBIT
                mnem = 'rbit'
                if q == 0:
                    t = IFS_8B
                elif q == 1:
                    t = IFS_16Bs
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
        elif size == 0b10 or size == 0b11:
            if opc == 0b01100: #7
                opcode = INS_CMGE
                mnem = 'cmge'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                    A64ImmOper(0),
                )
            if opc == 0b01101: #7
                opcode = INS_CMLE
                mnem = 'cmle'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                    A64ImmOper(0),
                )
            if opc == 0b01111: #7
                opcode = INS_NEG
                mnem = 'neg'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11001: #7
                opcode = INS_RINT
                mnem = 'rint'
                iflag |= IFP_F
                iflag |= IF_I
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11010: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_P
                iflag |= IF_U
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11011: #7
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_Z
                iflag |= IF_U
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11100: #11
                opcode = INS_SQRT
                mnem = 'sqrt'
                iflag |= IFP_U
                iflag |= IFP_R
                iflag |= IF_E
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11101: #7
                opcode = INS_SQRT
                mnem = 'sqrt'
                iflag |= IFP_F
                iflag |= IFP_R
                iflag |= IF_E
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
            if opc == 0b11111: #7
                opcode = INS_SQRT
                mnem = 'sqrt'
                iflag |= IFP_F
                if size == 0b10 and q == 0:
                    t = IFS_2S
                elif size == 0b10 and q == 1:
                    t = IFS_4S
                elif size == 0b11 and q == 1:
                    t = IFS_2D
                olist = (
                    A64RegOper(rd, oflags=t),
                    A64RegOper(rn, oflags=t),
                )
    return opcode, mnem, olist, iflag, 0

def p_simd_across_lanes(opval, va):
    iflag = 0
    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    if opc == 0b00011:
        opcode = INS_ADDL
        mnem = 'addl'
        if u == 0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
        iflag |= IF_V
        if size == 0b00 and q == 0:
            t = IFS_8B
        elif size == 0b00 and q == 1:
            t = IFS_16B
        elif size == 0b01 and q == 0:
            t = IFS_4H
        elif size == 0b01 and q == 1:
            t = IFS_8H
        elif size == 0b10 and q == 1:
            t = IFS_4S
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    elif opc == 0b01010:
        opcode = INS_MAX
        mnem = 'max'
        if u == 0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
        iflag |= IF_V
        if size == 0b00 and q == 0:
            t = IFS_8B
        elif size == 0b00 and q == 1:
            t = IFS_16B
        elif size == 0b01 and q == 0:
            t = IFS_4H
        elif size == 0b01 and q == 1:
            t = IFS_8H
        elif size == 0b10 and q == 1:
            t = IFS_4S
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    elif opc == 0b11010:
        opcode = INS_MIN
        mnem = 'min'
        if u == 0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
        iflag |= IF_V
        if size == 0b00 and q == 0:
            t = IFS_8B
        elif size == 0b00 and q == 1:
            t = IFS_16B
        elif size == 0b01 and q == 0:
            t = IFS_4H
        elif size == 0b01 and q == 1:
            t = IFS_8H
        elif size == 0b10 and q == 1:
            t = IFS_4S
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    elif opc == 0b11011:
        opcode = INS_ADD
        mnem = 'add'
        iflag |= IF_V
        if size == 0b00 and q == 0:
            t = IFS_8B
        elif size == 0b00 and q == 1:
            t = IFS_16B
        elif size == 0b01 and q == 0:
            t = IFS_4H
        elif size == 0b01 and q == 1:
            t = IFS_8H
        elif size == 0b10 and q == 1:
            t = IFS_4S
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    elif opc == 0b01100:
        if size >> 1 & 0x1 == 0:
            opcode = INS_MAX
            mnem = 'max'
        else:
            opcocde = INS_MIN
            mnem = 'min'
        iflag |= IFP_F
        iflag |= IF_N
        iflag |= IF_M
        iflag |= IF_V
        if size >> 1 & 0x1f == 0 and q == 1:
            t = IFS_4S
        else:
            t = 0
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    elif opc == 0b01111:
        if size >> 1 & 0x1 == 0:
            opcode = INS_MAX
            mnem = 'max'
        else:
            opcocde = INS_MIN
            mnem = 'min'
        iflag |= IFP_F
        iflag |= IF_V
        if size >> 1 & 0x1f == 0 and q == 1:
            t = IFS_4S
        else:
            t = 0
        olist = (
            #FIXME <V><d>
            A64RegOper(rn, oflags=t),
        )
    return opcode, mnem, olist, iflag, 0

def p_simd_copy(opval, va):
    '''
    AdvSIMD copy
    '''
    iflag = 0

    q = opval >> 30 & 0x1
    op = opval >> 29 & 0x1
    imm5 = opval >> 16 & 0x1f
    imm4 = opval >> 11 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if op == 0b0:               # FIXME SIMD REGISTER MADNESS
        if imm4 & 0b1110 == 0b0000:
            mnem = 'dup'
            opcode = INS_DUP
            if imm5 & 0x0f == 0b00000:
                width_spec1 = 'RESERVED'
                width_spec2 = 'RESERVED'
                index = 'RESERVED'
            elif imm5 & 0b00001 == 0b00001:
                width_spec2 = dup_table[0][imm4 & 0x1]
                index = imm5[4:1]
                if q == 0b0:
                    width_spec1 = IFS_8B
                else:
                    width_spec1 = IFS_16B
            elif imm5 & 0b00010 == 0b00010:
                width_spec2 = dup_table[1][imm4 & 0x1]
                index = imm5[4:2]
                if q == 0b0:
                    width_spec1 = IFS_4H
                else:
                    width_spec1 = IFS_8H
            elif imm5 & 0b00100 == 0b00100:
                width_spec2 = dup_table[2][imm4 & 0x1]
                index = imm5[4:3]
                if q == 0b0:
                    width_spec1 = IFS_2S
                else:
                    width_spec1 = IFS_4S
            else:
                width_spec2 = dup_table[3][imm4 & 0x1]
                index = imm5[4]
                if q == 0b0:
                    width_spec1 = 'RESERVED'
                else:
                    width_spec1 = IFS_2D
            if imm4 & 0x1 == 0b0:
                olist = (
                    A64RegOper(rd, va, oflag=width_spec1),
                    A64RegOper(rn, va, size=width_spec2),
                    A64ImmOper(index, va=va),
                )
            else:
                olist = (
                    A64RegOper(rd, va, oflag=width_spec1),
                    A64RegOper(rn, va, size=width_spec2),
                )
        elif imm4 == 0b0011:
            mnem = 'ins'
            opcode = INS_INS
            if imm5 & 0x0f == 0b00000:
                width_spec1 = 'RESERVED'
                width_spec2 = 'RESERVED'
                index = 'RESERVED'
            elif imm5 & 0b00001 == 0b00001:
                width_spec1 = dup_table[0][0]
                width_spec2 = dup_table[0][1]
                index = imm5[4:1]
            elif imm5 & 0b00010 == 0b00010:
                width_spec1 = dup_table[1][0]
                width_spec2 = dup_table[1][1]
                index = imm5[4:2]
            elif imm5 & 0b00100 == 0b00100:
                width_spec1 = dup_table[2][0]
                width_spec2 = dup_table[2][1]
                index = imm5[4:3]
            else:
                width_spec1 = dup_table[3][0]
                width_spec2 = dup_table[3][1]
                index = imm5[4]
            olist = (
                A64RegOper(rd, va, size=width_spec1),
                A64ImmOper(index, va=va),
                A64RegOper(rn, va, size=width_spec2),
            )
        elif imm4 & 0b1101 == 0b0101:
            mnem = 'mov'
            opcode = INS_MOV
            if imm4 & 0b0010 == 0b0000:
                iflag |= IFP_S
                index32 = imm5 & 0x3
                index64 = imm5 & 0x7
                if q == 0b0:
                    regsize = 4
                    rd += meta_reg_bases[size]
                    rn += meta_reg_bases[size]

                    if index32 == 0b00:
                        index = 'RESERVED'
                        width_spec = 'RESERVED'
                    elif index32 == 0b10:
                        index = imm5[4:2]
                        width_spec = 'H'
                    else:
                        index = imm5[4:1]
                        width_spec = 'B'        # FIXME: WTF?
                else:
                    regsize = 8
                    if index64 == 0b000:
                        width_spec = 'RESERVED'
                        index = 'RESERVED'
                    elif index64 == 0b100:
                        width_spec = 'S'
                        index = imm5[4:3]
                    elif index64 & 0b010 == 0b010:
                        width_spec = 'H'
                        index = imm5[4:2]
                    else:
                        width_spec = 'B'
                        index = imm5[4:1]
            else:
                iflag |= IFP_U
                index32 = imm5 & 0x7
                if q == 0b0:
                    regsize = 4
                    rd += meta_reg_bases[size]
                    rn += meta_reg_bases[size]
                    if index32 == 0b000:
                        width_spec = 'RESERVED'
                        index = 'RESERVED'
                    elif index32 == 0b100:
                        width_spec = 'S'
                        index = imm5[4:3]
                    elif index32 & 0b010 == 0b010:
                        width_spec = 'H'
                        index = imm5[4:2]
                    else:
                        width_spec = 'B'
                        index = imm5[4:1]
                else:
                    regsize = 8
                    index = imm5[4]
                    if imm5 & 0b01000 == 0b01000:
                        width_spec = 'D'
                    else:
                        width_spec = 'RESERVED'
            olist = (
                A64RegOper(rd, va, size=regsize),
                A64RegOper(rn, va, size=width_spec),
                A64ImmOper(index, va)
            )
    else:
        mnem = 'ins'
        opcode = INS_INS
        if imm5 & 0x0f == 0b00000:
            width_spec = 'RESERVED'
            index1 = 'RESERVED'
            index2 = 'RESERVED'
        elif imm5 & 0b00001 == 0b00001:
            width_spec = dup_table[0][0]
            index1 = imm5[4:1]
            index2 = imm5[3:0]
        elif imm5 & 0b00010 == 0b00010:
            width_spec = dup_table[1][0]
            index1 = imm5[4:2]
            index2 = imm5[3:1]
        elif imm5 & 0b00100 == 0b00100:
            width_spec = dup_table[2][0]
            index1 = imm5[4:3]
            index2 = imm5[3:2]
        else:
            width_spec = dup_table[3][0]
            index = imm5[4]
            index2 = imm5[3]
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64ImmOper(index1, va=va),
            A64RegOper(rn, va, size=width_spec),
            A64ImmOper(index2, va=va),
        )

    return opcode, mnem, olist, iflag, 0

dup_table = (
    ( 'B', 'W'),
    ( 'H', 'W'),
    ( 'S', 'W'),
    ( 'D', 'X'),
)

def p_simd_vector_ie(opval, va):
    '''
    AdvSIMD vector x indexed element
    '''
    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    l = opval >> 21 & 0x1
    m = opval >> 20 & 0x1
    rm = opval >> 16 & 0xf
    opc = opval >> 12 & 0xf
    h = opval >> 11 & 0x1
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    
    if opc & 0b0010 == 0b0010: #any instruction with IF_L at the end (long flag)
        iflag |= IF_L
        if size == 0b00:
            ta = 'RESERVED'
            tb = 'RESERVED'
            ts = 'RESERVED'
            vm = 'RESERVED'
            index = 'RESERVED'
        elif size == 0b01:
            ta = IFS_4S
            ts = 'H'
            vm = rm
            index = h+l+m
            if q == 0b0:
                tb = IFS_4H
            else:
                tb = IFS_8H
        elif size == 0b10:
            ta = IFS_2D
            ts = 'S'
            vm = m+rm
            index = h+l
            if q == 0b0:
                tb = IFS_2S
            else:
                tb = IFS_4S
        else:
            ta = 'RESERVED'
            tb = 'RESERVED'
            ts = 'RESERVED'
            vm = 'RESERVED'
            index = 'RESERVED'
        olist = (
            A64RegOper(rd, va, oflag=ta),
            A64RegOper(rn, va, oflag=tb),
            A64RegOper(vm, va, size=ts),
            A64ImmOper(index, va=va),
        )
    else:
        if opc & 0b0001 == 0b0000 or opc == 0b1101: #any remaining instruction without a floating point flag (IFP_F)
            if size == 0b00:
                t = 'RESERVED'
                ts = 'RESERVED'
                vm = 'RESERVED'
                index = 'RESERVED'
            elif size == 0b01:
                ts = 'H'
                vm = rm
                index = h+l+m
                if q == 0b0:
                    t = IFS_4H
                else:
                    t = IFS_8H
            elif size == 0b10:
                ts = 'S'
                vm = m+rm
                index = h+l
                if q == 0b0:
                    t = IFS_2S
                else:
                    t = IFS_4S
            else:
                t = 'RESERVED'
                ts = 'RESERVED'
                vm = 'RESERVED'
                index = 'RESERVED'
        else: #instructions with a floating point flag
            if size & 0b10 == 0b00:
                return p_undef(opval, va)
            if u == 0b1:
                iflag |= IF_X
            vm = m+rm
            if size == 0b00:
                t = IFS_2S
                ts = 'S'
                index = h+l
            elif size == 0b01:
                t = 'RESERVED'
                ts = 'D'
                if l == 0b0:
                    index = h
                else:
                    index = 'RESERVED'
            elif size == 0b10:
                t = IFS_4S
                ts = 'S'
                index = h+l
            else:
                t = IFS_2D
                ts = 'D'
                if l == 0b0:
                    index = h
                else:
                    index = 'RESERVED'
        olist = (
            A64RegOper(rd, va, oflag=t),
            A64RegOper(rn, va, oflag=t),
            A64RegOper(vm, va, size=ts),
            A64ImmOper(index, va=va),
        )
    if opc & 0x3 == 0b10:
        if u == 0b0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
    if u == 0b0 and opc & 0x3 == 0b11:
        iflag |= IFP_SQ
        iflag |= IFP_D
    if opc & 0b1000 == 0b1000:
        #all instructions with opc beginning with 1 have an opcode of MUL
        mnem = 'mul'
        opcode = INS_MUL
        if opc & 0b0100 == 0b0100:
            iflag |= IFP_SQ
            iflag |= IFP_D
            iflag |= IF_H
            if opc & 0b0010 == 0b0010 or u == 0b1:
                return p_undef(opval, va)
            if opc & 0x1 == 0b0001:
                iflag |= IFP_R
    elif opc & 0b0100 == 0b0100:
        #all other instructions with the second bit opc as 1 have an opcode of MLS
        mnem = 'mls'
        opcode = INS_MLS
    else:
        #all remaining instructions have an opcode of 'mla'
        mnem = 'mla'
        opcode = INS_MLA

    return opcode, mnem, olist, iflag, 0

def p_simd_mod_shift_imm(opval, va):
    '''
    Chooses between AdvSIMD modified immediate and shift by immediate
    Modified immediate: bits 19-22 == 0b0000
    Shift by immediate: bits 19-22 != 0b0000
    '''
    if opval >> 19 & 0xf == 0b0000:
        return p_simd_mod_imm(opval, va)
    else:
        return p_simd_shift_imm(opval, va)

def p_simd_mod_imm(opval, va):
    '''
    AdvSIMD modified immediate
    '''
    q = opval >> 30 & 0x1
    op = opval >> 29 & 0x1
    a = opval >> 18 & 0x1
    b = opval >> 17 & 0x1
    c = opval >> 16 & 0x1
    cmode = opval >> 12 & 0xf
    o2 = opval >> 11 & 0x1
    d = opval >> 9 & 0x1
    e = opval >> 8 & 0x1
    f = opval >> 7 & 0x1
    g = opval >> 6 & 0x1
    h = opval >> 5 & 0x1
    rd = opval & 0x1f

    if o2 == 0b0:
        if cmode & 0b1000 == 0b0000 or cmode & 0b0100 == 0b0000:
            if cmode & 0b1000 == 0b0000:
                shift = cmode[2:1]
                if q == 0b0:
                    width_spec = IFS_2S              
                else:
                    width_spec = IFS_4S
            else:
                shift = cmode[1]
                if q == 0b0:
                    width_spec = IFS_4H              
                else:
                    width_spec = IFS_8H
            olist = (
                A64RegOper(rd, va, oflag=width_spec),
                A64ImmOper(a+b+c+d+e+f+g+h, va=va),
                #shift equal to mod_imm_table[shift] LSL
            )
            if cmode & 0x1 == 0b0:
                iflag |= IF_I
                if op == 0b0:
                    mnem = 'mov'
                    opcode = INS_MOV
                else:
                    mnem = 'mv'
                    opcode = INS_MV
                    iflag |= IF_N                   
            else:
                if op == 0b0:
                    mnem = 'orr'
                    opcode = INS_ORR
                else:
                    mnem = 'bic'
                    opcode = INS_BIC
        elif cmode & 0b0010 == 0b0000:
            iflag |= IF_I
            if op == 0b0:
                mnem = 'mov'
                opcode = INS_MOV
            else:
                mnem = 'mv'
                opcode = INS_MV
                iflag |= IF_N
            shift = (8,16)[cmode[0]]
            if q == 0b0:
                width_spec = IFS_2S              
            else:
                width_spec = IFS_4S
            olist = (
                A64RegOper(rd, va, oflag=width_spec),
                A64ImmOper(a+b+c+d+e+f+g+h, va=va),
                #shift amount MSL
            )
        elif cmode == 0b1111:
            mnem = 'mov'
            opcode = INS_MOV
            iflag |= IFP_F
            if op == 0b0:
                width_spec = (IFS_4S, IFS_2S)[q]
            elif q == 0b1:
                width_spec = IFS_2D
            else:
                return p_undef(opval, va)
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64ImmOper(a+b+c+d+e+f+g+h, va=va),
            )
        else:
            mnem = 'mov'
            opcode = INS_MOV
            iflag |= IF_I
            if op == 0b0:
                olist = (
                    A64RegOper(rd, va, oflag=(IFS_8B,IFS_16B)[q]),
                    A64ImmOper(a+b+c+d+e+f+g+h, va=va),
                    #FIXME shift == 0x0
                )
            else:
                if q == 0b0:
                    olist = (
                        A64RegOper(rd, va, size=8),
                        A64ImmOper(a+b+c+d+e+f+g+h, va=va),
                    )
                else:
                    olist = (
                        A64RegOper(rd, va, oflag=IFS_2D),
                        A64ImmOper(a+b+c+d+e+f+g+h, va=va),
                    ) 
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0

mod_imm_table = (
    0, 8, 16, 24,
)


def p_simd_shift_imm(opval, va):
    '''
    AdvSIMD shift by immediate
    '''
    iflag = 0

    q = opval >> 30 & 0x1
    u = opval >> 29 & 0x1
    immh = opval >> 19 & 0xf
    immb = opval >> 16 & 0x7
    opc = opval >> 11 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if opc & 0b11000 == 0b00000:
        if immh & 0b1000 == 0b1000:
            shift = 16 - (immh+immb)
            if q == 0b0:
                width_spec = IFS_8B
            else:
                width_spec = IFS_16B
        elif immh & 0b0100 == 0b0100:
            shift = 32 - (immh+immb)
            if q == 0b0:
                 width_spec = IFS_4H
            else:
                width_spec = IFS_8H
        elif immh & 0b0010 == 0b0010:
            shift = 8 - (immh+immb)
            if q == 0b0:
                width_spec = IFS_2S
            else:
                width_spec = IFS_4S
        elif immh == 0b0001:
            shift = 128 - (immh+immb)
            if q == 0b0:
                width_spec = 'RESERVED'
            else:
                width_spec = IFS_2D
        else:
            pass
            #FIXME see modified immediate?
        olist = (
            A64RegOper(rd, va, oflag=width_spec),
            A64RegOper(rn, va, oflag=width_spec),
            #FIXME shift = variable shift specified above
        )
        if u == 0b0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
        if opc & 0b00011== 0b00000:
            mnem = 'shr'
            opcode = INS_SHR
        else:
            mnem = 'sra'
            opcode = INS_SRA
        if opcode & 0b00100 == 0b00100:
            iflag |= IFP_R
        
    elif opc & 0b11000 == 0b01000:
        if opc == 0b01000:
            if u == 0b0:
                return p_undef(opval, va)
            else:
                mnem = 'sri'
                opcode = INS_SRI
        elif opc == 0b01010:
            if u == 0b0:
                mnem = 'shl'
                opcode = INS_SHL
            else:
                mnem = 'sli'
                opcode = INS_SLI
        elif opc == 0b01100:
            if u == 0b0:
                return p_undef(opval, va)
            else:
                mnem = 'shl'
                opcode = INS_SHL
                iflag |= IF_U
                iflag |= IFP_SQ
        elif opc == 0b01110:
            mnem = 'shl'
            opcode = INS_SHL
            if u == 0b0:
                iflag |= IFP_SQ
            else:
                iflag |= IFP_UQ
        else:
            return p_undef(opval, va)
        if immh & 0b1000 == 0b1000:
            if mnem != 'sri':
                shift = (immh+immb) - 64
            else:
                shift = 128 - (immh+immb)
            if q == 0b0:
                width_spec = IFS_8B
            else:
                width_spec = IFS_16B
        elif immh & 0b0100 == 0b0100:
            if mnem != 'sri':
                shift = (immh+immb) - 32
            else:
                shift = 64 - (immh+immb)
            if q == 0b0:
                 width_spec = IFS_4H
            else:
                width_spec = IFS_8H
        elif immh & 0b0010 == 0b0010:
            if mnem != 'sri':
                shift = (immh+immb) - 16
            else:
                shift = 32 - (immh+immb)
            if q == 0b0:
                width_spec = IFS_2S
            else:
                width_spec = IFS_4S
        elif immh == 0b0001:
            if mnem != 'sri':
                shift = (immh+immb) - 8
            else:
                shift = 16 - (immh+immb)
            if q == 0b0:
                width_spec = 'RESERVED'
            else:
                width_spec = IFS_2D
        else:
            pass
            #FIXME see modified immediate?
        olist = (
            A64RegOper(rd, va, oflag=width_spec),
            A64RegOper(rn, va, oflag=width_spec),
            #FIXME shift = variable shift specified above
        )
    elif opc & 0b11000 == 0b10000:
        if immh & 0b1000 == 0b1000:
            width_spec = 'RESERVED'
            width_spec2 = 'RESERVED'
            shift = 'RESERVED'
        elif immh &0b0100 == 0b0100:
            width_spec2 = IFS_2D
            if opc & 0x4 == 0b00000:
                shift = 64 - (immh+immb)
            else:
                shift = (immh+immb) - 32
            if q == 0b0:
                width_spec = IFS_2S
            else:
                width_spec = IFS_4S
        elif immh & 0b0010 == 0b0010:
            width_spec2 = IFS_4S
            if opc & 0x4 == 0b00000:
                shift = 32 - (immh+immb)
            else:
                shift = (immh+immb) - 16
            if q == 0b0:
                width_spec = IFS_4H
            else:
                width_spec = IFS_8H
        elif immh == 0b0001:
            width_spec2 = IFS_8H
            if opc & 0x4 == 0b00000:
                shift = 16 - (immh+immb)
            else:
                shift = (immh+immb) - 8
            if q == 0b0:
                width_spec = IFS_8B
            else:
                width_spec = IFS_16B
        else:
            #FIXME see AdvSIMD modified immediate?
            pass
        if opc & 0x4 == 0b00000:
            olist = (
                A64RegOper(rd, va, oflag=width_spec),
                A64RegOper(rn, va, oflag=width_spec2),
                #FIXME shift, variable shift specified above
            )
            mnem = 'shr'
            opcode = INS_SHR
            iflag |= IF_N
            if opc & 0x1 == 0b1:
                iflag |= IFP_R
            if u == 0b0:
                if opc & 0x2 == 0b00010:
                    iflag |= IFP_SQ
            else:
                if opc & 0x2 == 0b00010:
                    iflag |= IFP_UQ
                else:
                    iflag |= IFP_SQ
                    iflag |= IF_U
        else:
            olist = (
                A64RegOper(rd, va, oflag=width_spec2),
                A64RegOper(rn, va, oflag=width_spec),
                #FIXME shift, variable shift specified above
            )
            mnem = 'shl'
            opcode = INS_SHL
            iflag |= IF_L
            if u == 0b0:
                iflag |= IFP_S
            else:
                iflag |= IFP_U
    else:
        mnem = 'cvt'
        opcode = INS_CVT
        #FIXME
        if immh & 0b1000 == 0b1000:
            fbits = 128 - (immh+immb)
            if q == 0b0:
                width_spec = 'RESERVED'
            else:
                width_spec = IFS_2D
        elif immh & 0b0100 == 0b0100:
            fbits = 64 - (immh+immb)
            if q == 0b0:
                width_spec = IFS_2S
            else:
                width_spec = IFS_4S
        elif immh == 0b0000:
            pass
            #FIXME see AdvSIMD modified immediate
        else:
            width_spec = 'RESERVED'
            fbits = 128 - (immh + immb)
        olist = (
            A64RegOper(rd, va, oflag=width_spec),
            A64RegOper(rn, va, oflag=width_spec),
            #FIXME fractional bits?
        )
        if opc & 0x7 == 0b100:
            iflag |= IF_F
            if u == 0b0:
                iflag |= IFP_S
            else:
                iflag |= IFP_U
        elif opc & 0x7 == 0b111:
            iflag |= IFP_F
            iflag |= IF_Z
            if u == 0b0:
                iflag |= IF_S
            else:
                iflag |= IF_U
        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0
        

def p_simd_tbl_tbx(opval, va):
    '''
    AdvSIMD TBL/TBX
    '''
    q = opval >> 30 & 0x1
    op2 = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    length = opval >> 13 & 0x3
    op = opval >> 12 & 0x1
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if op2 == 0b00:
        #FIXME mnem, opcode choices w/ iflags           # REGISTERS ARE F*D UP.  size can't equal strings
        if op == 0b0:
            mnem = 'tbl'
            opcode = INS_TBL
        else:
            mnem = 'tbx'
            opcode = INS_TBX
        if q == 0b0:
            regsize = '8B'
        else:
            regsize = '16B'
        if length == 0b00:
            olist = (
                A64RegOper(rd, va, oflag=regsize),
                A64RegOper(rn, va, oflag=IFS_16B),
                A64RegOper(rm, va, oflag=regsize),
            )
        elif length == 0b01:
            olist = (
                A64RegOper(rd, va, oflag=regsize),
                A64RegOper(rn, va, oflag=IFS_16B),
                A64RegOper((rn + 1) % 32, va, oflag=IFS_16B),
                A64RegOper(rm, va, oflag=regsize),
            )            
        elif length == 0b10:
            olist = (
                A64RegOper(rd, va, oflag=regsize),
                A64RegOper(rn, va, oflag=IFS_16B),
                A64RegOper((rn + 1) % 32, va, oflag=IFS_16B),
                A64RegOper((rn + 2) % 32, va, oflag=IFS_16B),
                A64RegOper(rm, va, oflag=regsize),
            ) 
        else:
            olist = (
                A64RegOper(rd, va, oflag=regsize),
                A64RegOper(rn, va, oflag=IFS_16B),
                A64RegOper((rn + 1) % 32, va, oflag=IFS_16B),
                A64RegOper((rn + 2) % 32, va, oflag=IFS_16B),
                A64RegOper((rn + 3) % 32, va, oflag=IFS_16B),
                A64RegOper(rm, va, oflag=regsize),
            ) 
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0

def p_simd_zip_uzp_trn(opval, va):
    '''
    AdvSIMD ZIP/UZP/TRN
    '''
    q = opval >> 30 & 0x1
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0x7
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    opcode, mnem = zip_uzp_trn_table[opc]
    if opcode != IENC_UNDEF:
        size1 = size+q
        olist = (
            A64RegOper(rd, va, size=t_table[sizeq]),
            A64RegOper(rn, va, size=t_table[sizeq]),
            A64RegOper(rm, va, size=t_table[sizeq]),
        )
    else:
        olist = (
            A64ImmOper(opval),
        )

    return opcode, mnem, olist, 0, 0


zip_uzp_trn_table = (
    (IENC_UNDEF, 'undefined instruction'),
    (INS_UZP1, 'uzp1'),
    (INS_TRN1, 'trn1'),
    (INS_ZIP1, 'zip1'),
    (IENC_UNDEF, 'undefined instruction'),
    (INS_UZP2, 'uzp2'),
    (INS_TRN2, 'trn2'),
    (INS_ZIP2, 'zip2'),
)

def p_simd_ext(opval, va):
    '''
    AdvSIMD EXT
    '''
    q = opval >> 30 & 0x1
    op2 = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    imm4 = opval >> 11 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    iflag = 0

    if op2 == 0b00:
        if q == 0b0:
            oflag = IFS_8B
            size = 8
            if imm4[3] == 0b0:
                index = imm4[0:2]
            else:
                index = 'RESERVED'
        else:
            oflag = IFS_16B
            size = 16
            index = imm4
        olist = (
            A64RegOper(rd, va, oflag=regsize),
            A64RegOper(rn, va, oflag=regsize),
            A64RegOper(rm, va, oflag=regsize),
            A64ImmOper(index, va=va),
        )
        return INS_EXT, 'ext', olist, 0, 0
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0


def p_simd_scalar_three_same(opval, va):
    '''
    AdvSIMD scalar three same
    '''
    iflag = 0
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 11 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    subopc = opc & 0b11000

    if subopc == 0b00000:
        if opc & 0b00010 == 0b00000:
            if opc & 0b00100 == 0b00000:
                mnem = 'add'
                opcode = INS_ADD
            else:
                mnem = 'sub'
                opcode = INS_SUB
            if u == 0b0:
                iflag |= IFP_SQ
            else:
                iflag |= IFP_UQ
            width_spec = bhsd_table[size]
        else:
            mnem = 'cm'
            opcode = INS_CM
            iflag |= three_same_cm_table[opval & 0x1][u]
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'
    elif subopc == 0b01000:
        if opc & 0x4 == 0b100:
            return p_undef(opval, va)
        mnem = 'shl'
        opcode = INS_SHL
        if opc & 0x1 == 0b0:
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'                
            if u == 0b0:
                iflag |= IFP_S
            else:
                iflag |= IFP_U
        else:
            width_spec = bhsd_table[size]
            if u == 0b0:
                iflag |= IFP_SQ
            else:
                iflag |= IFP_UQ
        if opc & 0x2 == 0b10:
            iflag |= IFP_R
    elif subopc == 0b10000:
        if opc & 0x7 == 0b00000:
            if u == 0b0:
                mnem = 'add'
                opcode = INS_ADD
            else:
                mnem = 'sub'
                opcode = INS_SUB
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'
        elif opc & 0x7 == 0b00001:
            mnem = 'cm'
            opcode = INS_CM
            if u == 0b0:
                iflag |= IF_TST
            else:
                iflag |= IF_EQ
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'
        elif opc & 0x7 == 0b00110:
            opcode = INS_MUL
            mnem = 'mul'
            iflag |= IFP_SQ
            if u == 0b1:
                iflag |= IFP_R
            iflag |= IFP_D
            iflag |= IF_H
            width_spec = three_diff_table[size][1]
        else:
            return p_undef(opval, va)
    else:
        iflag |= IFP_F
        if size & 0b01 == 0b00:
            width_spec = 'S'
        else:
            width_spec = 'D'
        if opc & 0b00110 == 0b00100:
            if opc & 0x1 == 0b0:
                mnem = 'cm'
                opcode = INS_CM
            else:
                mnem = 'ac'
                opcode = INS_AC
            if size & 0b10 == 0b00:
                if u == 0b0:
                    iflag |= IF_EQ
                else:
                    iflag |= IF_GE
            else:
                if u == 0b0:
                    return p_undef(opval, va)
                else:
                    iflag |= IF_GT
        elif u == 0b1:
            if size & 0b10 == 0b10 and opc & 0x7 == 0b010:
                mnem = 'abd'
                opcode = INS_ABD
            else:
                return p_undef(opval, va)
        else:
            if opc & 0x7 == 0b00111:
                iflag |= IF_S
                if size & 0b10 == 0b00:
                    mnem = 'recp'
                    opcode = INS_RECP
                else:
                    iflag |= IFP_R
                    mnem = 'sqrt'
                    opcode = INS_SQRT
            elif opc & 0x7 == 0b00011:
                if size & 0b10 == 0b00:
                    mnem = 'mul'
                    opcode = INS_MUL
                    iflag |= IF_X
                else:
                    return p_undef(opval, va)
            else:
                return p_undef(opval, va)
    olist = (
        A64RegOper(rd, va, size=width_spec),
        A64RegOper(rn, va, size=width_spec),
        A64RegOper(rm, va, size=width_spec),
    )

    return opcode, mnem, olist, iflag, 0

three_same_cm_table = (
    (IF_GT, IF_HI),
    (IF_GE, IF_HS),
)

def p_simd_scalar_three_diff(opval, va):
    '''
    AdvSIMD scalar three different
    '''
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    iflag = 0
    
    if u == 0b0:
        iflag |= IFP_SQ
        iflag |= IFP_D
        iflag |= IF_L
        width_spec = three_diff_table[size][0]
        width_spec1 = three_diff_table[size][1]
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec2),
            A64RegOper(rm, va, size=width_spec2),
        )
        if opc == 0b1001:
            opcode = INS_ML
            mnem = 'ml'
            iflag |= IF_A
        elif opc == 0b1011:
            opcode = INS_ML
            mnem = 'ml'
            iflag |= IF_S            
        elif opc == 0b1101:
            opcode = INS_MUL
            mnem = 'mul'
        else:
            return p_undef(opval, va)
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0


three_diff_table = (
    ('RESERVED', 'RESERVED'),
    ('S', 'H'),
    ('D', 'S'),
    ('RESERVED', 'RESERVED'),
)

def p_simd_scalar_tworeg_misc(opval, va):
    '''
    AdvSIMD scalar two-reg misc
    '''
    iflag = 0
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if opc & 0b11100 == 0b00000:
        mnem = 'add'
        opcode = INS_ADD
        #FIXME unsigned and signed clash
        if u == 0b0:
            iflag |= IFP_SUQ
        else:
            iflag |= IFP_USQ
    elif opc & 0x3 == 0b11 and opc & 0b10000 == 0b00000:
        if u == 0b0:
            opcode = INS_ABS
            mnem = 'abs'
        else:
            opcode = INS_NEG
            mnem = 'neg'
        if opc & 0b01100 == 0b00100:
            iflag |= IFP_SQ
            olist = (
                A64RegOper(rd, va, size=bhsd_table[size]),
                A64RegOper(rn, va, size=bhsd_table[size]),
            )
        elif opc & 0b01100 == 0b01000:
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64RegOper(rn, va, size=width_spec),
            )
        else:
            return p_undef(opval, va)
    elif opc & 0b11000 == 0b01000:
        opcode = INS_CM
        mnem = 'cm'
        if opc & 0b00100 == 0b00100:
            iflag |= IFP_F
            if size & 0b01 == 0b00:
                width_spec = 'S'
            else:
                width_spec = 'D'
        else:
            if size == 0b11:
                width_spec = 'D'
            else:
                width_spec = 'RESERVED'
        iflag |= cm_table[opval & 0x3][u]
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec),
            #FIXME #0
        )
    elif opc & 0b11000 == 0b10000:
        subcode = opc & 0b00111
        iflag |= IF_N
        if u == 0b0:
            if subcode == 0b00100:
                mnem = 'xt'
                opcode = INS_XT
                iflag |= IFP_SQ
            else:
                return p_undef(opval, va)
        else:
            if subcode == 0b00010:
                mnem = 'xt'
                opcode = INS_XT
                iflag |= IFP_SQ
                iflag |= IF_U
            elif subcode == 0b00100:
                mnem = 'xt'
                opcode = INS_XT
                iflag |= IFP_UQ
            elif subcode == 0b00110:
                opcode = INS_CVT
                mnem = 'cvt'
                iflag |= IFP_F
                iflag |= IF_X
            else:
                return p_undef(opval, va)
        if subcode == 0b00010 or 0b00100:
            width_spec = bhsd_table[size]
            width_spec2 = bhsd_table[size + 1]
            if size == 0b11:
                width_spec = 'RESERVED'
        else:
            if size & 0b01 == 0b00:
                width_spec = 'RESERVED'
                width_spec2 = 'RESERVED'
            else:
                width_spec = 'S'
                width_spec2 = 'D'               
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec2),               
        )
    else:
        if size & 0b10 == 0b00:
            if size & 0b01 == 0b01:
                width_spec = 'S'
            else:
                width_spec = 'D'
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64RegOper(rn, va, size=width_spec),
            )
            mnem = 'cvt'
            opcode = INS_CVT
            if opc != 0b11101:
                iflag |= IFP_F
                if u == 0b0:
                    iflag |= IF_S
                else:
                    iflag |= IF_U
            else:
                iflag |= IF_F
                if u == 0b0:
                    iflag |= IFP_S
                else:
                    iflag |= IFP_U
            if opc & 0x3 == 0b00010:
                iflag |= IF_N
            elif opc & 0x3 == 0b00011:
                iflag |= IF_M
            elif opc & 0x3 == 0b00100:
                iflag |= IF_A
        else:
            if size & 0b01 == 0b01:
                width_spec = 'S'
            else:
                width_spec = 'D'
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64RegOper(rn, va, size=width_spec),
            )
            iflag |= IFP_F
            if opc & 0b00100 == 0b00000:
                mnem = 'cvt'
                opcode = INS_CVT
                if u == 0b0:
                    iflag |= IF_S
                else:
                    iflag |= IF_U
                if opc & 0x3 == 0b10:
                    iflag |= IF_P
                elif opc & 0x3 == 0b11:
                    iflag |= IF_Z
                else:
                    return p_undef(opval, va)
            else:
                if opc & 0x3 == 0b01:
                    iflag |= IF_E
                if u == 0b0:
                    mnem = 'recp'
                    opcode = INS_RECP
                    if opc & 0x3 == 0b11:
                        iflag |= IF_X
                    elif opc & 0x3 != 0b01:
                        return p_undef(opval, va)                   
                else:
                    iflag |= IFP_R
                    mnem = 'sqrt'
                    opcode = INS_SQRT
                    
    return opcode, mnem, olist, iflag, 0

bhsd_table = (
    'B',
    'H',
    'S',
    'D',
    'RESERVED',
)

#FIXME maybe
cm_table = (
    (IF_GT, IF_GE),
    (IF_EQ, IF_LE),
    (IF_LT),
)


def p_simd_scalar_pairwise(opval, va):
    '''
    AdvSIMD scalar pairwise
    '''
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    iflag = IF_P
    if u == 0b0:
        if opc == 0b11011:
            mnem = 'add'
            opcode = INS_ADD
            if size == 0b11:
                width_spec = 'D'
                width_spec2 = IFS_2D
            else:
                width_spec = 'RESERVED'
                width_spec2 = 'RESERVED'
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64RegOper(rn, va, oflag=width_spec2),
            )
        else:
            return p_undef(opval, va)
    else:
        iflag |= IFP_F
        if opc & 0b11100 == 0b01100:
            if size & 0x1 == 0b0:
                width_spec = 'S'
                width_spec2 = IFS_2S
            else:
                width_spec = 'D'
                width_spec2 = IFS_2D                
            olist = (
                A64RegOper(rd, va, size=width_spec),
                A64RegOper(rn, va, size=width_spec2),
            )
            if size & 0b10 == 0b00:
                if opc & 0x3 == 0b00000:
                    mnem = 'max'
                    opcode = INS_MAX
                    iflag |= IF_NM
                elif opc & 0x3 == 0b00001:
                    mnem = 'add'
                    opcode = INS_ADD
                elif opc & 0x3 == 0b00011:
                    mnem = 'max'
                    opcode = INS_MAX
                else:
                    return p_undef(opval, va)
            else:
                mnem = 'min'
                opcode = INS_MIN
                if opc & 0x3 == 0b00000:
                    iflag |= IF_NM
                elif opc & 0x3 != 0b00011:
                    return p_undef(opval, va)
        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0


def p_simd_scalar_copy(opval, va):
    '''
    AdvSIMD scalar copy
    '''
    op = opval >> 29 & 0x1
    imm5 = opval >> 16 & 0x1f
    imm4 = opval >> 11 & 0xf
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    #FIXME width_spec
    if op == 0b0 and imm4 == 0b0000:
        mnem = 'dup'
        opcode =  INS_DUP
        if imm5 & 0b00001 == 0b00001:
            width_spec = 'B'
            index = imm5[:4]
        elif imm5 & 0b00010 == 0b00010:
            width_spec = 'H'
            index = imm5[:3]
        elif imm5 & 0b00100 == 0b00100:
            width_spec = 'S'
            index = imm5[:2]
        elif imm5 & 0b01000 == 0b01000:
            width_spec = 'D'
            index = imm5[:1]
        else:
            width_spec = 'RESERVED'
            index = 'RESERVED'
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec),
            A64ImmOper(index, va=va), #FIXME probably wrong, slicing
        )
    else:
        return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0

        
def p_simd_scalar_ie(opval, va):
    '''
    AdvSIMD scalar x indexed element
    '''
    iflag = 0
    u = opval >> 29 & 0x1
    size = opval >> 22 & 0x3
    l = opval >> 21 & 0x1
    m = opval >> 20 & 0x1
    rm = opval >> 16 & 0xf
    opc = opval >> 12 & 0xf
    h = opval >> 11 & 0x1
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if opc & 0b0010 == 0b0000:
        if size & 0x1 == 0b0:
            width_spec = 'S'
            index = h + l
        else:
            width_spec = 'D'
            if l == 0b0:
                index = h
            else:
                index = 'RESERVED'
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec),
            A64RegOper(m+rm, va, size=width_spec),
            A64ImmOper(index, va=va), #FIXME probably wrong
        )
    else:
        if size == 0b00:
            width_spec = 'RESERVED'
            width_spec2 = 'RESERVED'
            vm = 'RESERVED'
            index = 'RESERVED'
        elif size == 0b01:
            width_spec = 'S'
            width_spec2 = 'H'
            vm = 0 + rm
            index = h + l + m
        elif size == 0b10:
            width_spec = 'D'
            width_spec2 = 'S'
            vm = m + rm
            index = h + l
        else:
            width_spec = 'RESERVED'
            width_spec2 = 'RESERVED'
            vm = 'RESERVED'
            index = 'RESERVED'
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec2),
            A64RegOper(vm, va, size=width_spec2),
            A64ImmOper(index, va), #FIXME probably wrong
        )

    if u == 0b0:
        subopc = opc & 0b1100
        if subopc != 0b1100:
            if opc & 0x3 == 0b01:
                iflag |= IFP_F
            elif opc & 0x3 == 0b11:
                iflag |= IFP_SQ
                iflag |= IFP_D
                iflag |= IF_L
            else:
                return p_undef(opval, va)
        if subopc == 0b0000:
            mnem = 'mla'
            opcode = INS_MLA
        elif subopc == 0b0100:
            mnem = 'mls'
            opcode = INS_MLS
        elif subopc == 0b1000:
            mnem = 'mul'
            opcode = INS_MUL
        else:
            mnem = 'mul'
            opcode = INS_MUL
            iflag |= IFP_SQ
            iflag |= IFP_D
            iflag |= IF_H
            if opc & 0x3 == 0b01:
                iflag |= IFP_R
    else:
        if opc == 0b1001 and size & 0b10 == 0b10:
            iflag |= IF_X
            iflag |= IFP_F
            opcode = INS_MUL
        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0

        
def p_simd_scalar_shift_imm(opval, va):
    '''
    AdvSIMD scalar shift by immediate
    '''
    iflag = 0
    u = opval >> 29 & 0x1
    immh = opval >> 19 & 0xf
    immb = opval >> 16 & 0x7
    opc = opval >> 11 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if immh == 0b0000:
        return p_undef(opval, va)

    if opc & 0b11000 == 0b00000:
        if immh & 0b1000 == 0b0:
            width_spec = 'RESERVED'
            shift = 'RESERVED'
        else:
            width_spec = 8
            shift = 128-(immh+immb)
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec),
            #FIXME shift = variable shift specified above
        )
        if u == 0b0:
            iflag |= IFP_S
        else:
            iflag |= IFP_U
        if opc & 0b00011== 0b00000:
            mnem = 'shr'
            opcode = INS_SHR
        else:
            mnem = 'sra'
            opcode = INS_SRA
        if opcode & 0b00100 == 0b00100:
            iflag |= IFP_R
        
    elif opc & 0b11000 == 0b01000:
        if opc == 0b01000:
            if u == 0b0:
                return p_undef(opval, va)
            else:
                mnem = 'sri'
                opcode = INS_SRI
                if immh & 0b1000 == 0b0:
                    width_spec = 'RESERVED'
                    shift = 'RESERVED'
                else:
                    width_spec = 8
                    shift = 128-(immh+immb)
        elif opc == 0b01010:
            if u == 0b0:
                mnem = 'shl'
                opcode = INS_SHL
            else:
                mnem = 'sli'
                opcode = INS_SLI
            if immh & 0b1000 == 0b0:
                width_spec = 'RESERVED'
                shift = 'RESERVED'
            else:
                width_spec = 8
                shift = (immh+immb) - 64
        elif opc == 0b01100:
            if u == 0b0:
                return p_undef(opval, va)
            else:
                mnem = 'shl'
                opcode = INS_SHL
                iflag |= IF_U
                iflag |= IFP_SQ
                if immh & 0b1000 == 0b1000:
                    width_spec = 'D'
                    shift = (immh+immb)-64
                elif immh & 0b0100 == 0b0100:
                    width_spec = 'S'
                    shift = (immh+immb)-32
                elif immh & 0b0010 == 0b0010:
                    width_spec = 'H'
                    shift = (immh+immb)-16
                elif immh == 0b0001:
                    width_spec = 'B'
                    shift = (immh+immb)-8
                else:
                    width_spec = 'RESERVED'
                    shift = 'RESERVED'
        elif opc == 0b01110:
            mnem = 'shl'
            opcode = INS_SHL
            if u == 0b0:
                iflag |= IFP_SQ
            else:
                iflag |= IFP_UQ
            if immh & 0b1000 == 0b1000:
                width_spec = 'D'
                shift = (immh+immb)-64
            elif immh & 0b0100 == 0b0100:
                width_spec = 'S'
                shift = (immh+immb)-32
            elif immh & 0b0010 == 0b0010:
                width_spec = 'H'
                shift = (immh+immb)-16
            elif immh == 0b0001:
                width_spec = 'B'
                shift = (immh+immb)-8
            else:
                width_spec = 'RESERVED'
                shift = 'RESERVED'
        else:
            return p_undef(opval, va)
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, size=width_spec),
            #FIXME shift = variable shift specified above
        )
    elif opc & 0b11000 == 0b10000:
        #FIXME
        if immh == 0b0000:
            width_spec = 'RESERVED'
            width_spec2 = 'RESERVED'
            shift = 'RESERVED'
        elif immh == 0b0001:
            width_spec = 'B'
            width_spec2 = 'H'
            shift = 16 - (immh+immb)
        elif immh & 0b1110 == 0b0010:
            width_spec = 'H'
            width_spec2 = 'S'
            shift = 32 - (immh+immb)
        elif immh & 0b1100 == 0b0100:
            width_spec = 'S'
            width_spec2 = 'D'
            shift = 64 - (immh+immb)
        else:
            width_spec = 'RESERVED'
            width_spec2 = 'RESERVED'
            shift = 'RESERVED'
        olist = (
            A64RegOper(rd, va, size=width_spec),
            A64RegOper(rn, va, oflag=width_spec2),
            #FIXME shift specified above
        )
        mnem = 'shr'
        opcode = INS_SHR
        iflag |= IF_N
        if opc & 0b1 == 0b1:
            iflag |= IFP_R
        if opval >> 1 & 0b1 == 0b0:
            iflag |= IF_U
            iflag |= IFP_SQ
        else:
            if u == 0b0:
                iflag |= IFP_SQ
            else:
                iflag |= IFP_UQ
    else:
        mnem = 'cvt'            # FIXME: NEEDS WORK
        opcode = INS_CVT
        #FIXME
        if immh & 0b1100 == 0b0000:
            width_spec = 'RESERVED'
            fbits = 'RESERVED'
        elif immh & 0b1100 == 0b0100:
            width_spec = 'S'
            fbits = 64 - (immh+immb)
        else:
            width_spec = 'D'
            fbits = 128 - (immh + immb)
        olist = (
            A64RegOper(rd, va, size=size),
            A64RegOper(rn, va, size=size),
            #FIXME fractional bits?
        )
        if opc & 0x7 == 0b100:
            iflag |= IF_F
            if u == 0b0:
                iflag |= IFP_S
            else:
                iflag |= IFP_U
        elif opc & 0x7 == 0b111:
            iflag |= IFP_F
            iflag |= IF_Z
            if u == 0b0:
                iflag |= IF_S
            else:
                iflag |= IF_U
        else:
            return p_undef(opval, va)

    return opcode, mnem, olist, iflag, 0
            
        
def p_crypto_aes(opval, va):
    '''
    Crypto AES
    '''
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    opcode, mnem = aes_table[opc & 0x3]
    olist = (
        A64RegOper(rd, va, size=16),
        A64RegOper(rn, va, size=16),
    )
    if size != 0b00 or opc & 0b11100 != 0b00100:
        return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0

aes_table = (
    (INS_AESE, 'aese'),
    (INS_AESD, 'aesd'),
    (INS_AESMC, 'aesmc'),
    (INS_AESIMC, 'aesimc'),
)


def p_crypto_three_sha(opval, va):
    '''
    Crypto three-reg SHA
    '''
    size = opval >> 22 & 0x3
    rm = opval >> 16 & 0x1f
    opc = opval >> 12 & 0x7
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    opcode, mnem = crypto_3sha_table[opc]

    if opc & 0b100 == 0b100 or opc == 0b011:
        olist = (
            A64RegOper(rd, va, size=16),
            A64RegOper(rn, va, size=16),
            A64RegOper(rm, va, size=16),
        )
    else:
        olist = (
            A64RegOper(rd, va, size=16),
            A64RegOper(rn, va, size=4),
            A64RegOper(rm, va, size=16),
        )

    if size != 0b00 or opc == 0b111:
        return p_undef(opval, va)

        
    return opcode, mnem, olist, 0, 0


crypto_3sha_table = (
    (INS_SHA1C, 'sha1c'),
    (INS_SHA1P, 'sha1p'),
    (INS_SHA1M, 'sha1m'),
    (INS_SHA1SU0, 'sha1su0'),
    (INS_SHA256H, 'sha256h'),
    (INS_SHA256H2, 'sha256h2'),
    (INS_SHA256SU1, 'sha256su1'),
)


def p_crypto_two_sha(opval, va):
    '''
    Crypto two-reg SHA
    '''
    size = opval >> 22 & 0x3
    opc = opval >> 12 & 0x1f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    if opc == 0b00000:
        mnem = 'sha1h'
        opcode = INS_SHA1H
        olist = (
            A64RegOper(rd, va, size=4),
            A64RegOper(rn, va, size=4),
        )
    elif opc == 0b00001:
        mnem = 'sha1su1'
        opcode = INS_SHA1SU1
        olist = (
            A64RegOper(rd, va, size=16),
            A64RegOper(rn, va, size=16),
        )
    elif opc == 0b00010:
        mnem = 'sha256su0'
        opcode = INS_SHA256SU0
        olist = (
            A64RegOper(rd, va, size=16),
            A64RegOper(rn, va, size=16),
        )
    else:
        return p_undef(opval, va)

    if size != 0b00:
        return p_undef(opval, va)

    return opcode, mnem, olist, 0, 0
    

def p_undef(opval, va):
    '''
    Undefined encoding family
    '''
    # FIXME: make this an actual opcode with the opval as an imm oper
    #raise envi.InvalidInstruction(
    #        mesg="p_undef: invalid instruction (by definition in ARM spec)",
    #        bytez=struct.pack("<I", opval), va=va)
    opcode = IENC_UNDEF
    mnem = "undefined instruction"
    olist = (
        A64ImmOper(opval),
    )
        
    return (opcode, mnem, olist, 0, 0)


'''
ienc_parsers_tmp will be put into a tuple that will contain all iencs and their corresponding function
'''
ienc_parsers_tmp = [None for x in range(IENC_MAX)]

ienc_parsers_tmp[IENC_DATA_SIMD] = p_data_simd
ienc_parsers_tmp[IENC_LS_EXCL] = p_ls_excl
ienc_parsers_tmp[IENC_LS_NAPAIR_OFFSET] = p_ls_napair_offset
ienc_parsers_tmp[IENC_LS_REGPAIR_POSTI] = p_ls_regpair
ienc_parsers_tmp[IENC_LS_REGPAIR_OFFSET] = p_ls_regpair
ienc_parsers_tmp[IENC_LS_REGPAIR_PREI] = p_ls_regpair
ienc_parsers_tmp[IENC_LOG_SHFT_REG] = p_log_shft_reg
ienc_parsers_tmp[IENC_ADDSUB_SHFT_REG] = p_addsub_shft_reg
ienc_parsers_tmp[IENC_ADDSUB_EXT_REG] = p_addsub_ext_reg
ienc_parsers_tmp[IENC_SIMD_LS_MULTISTRUCT] = p_simd_ls_multistruct
ienc_parsers_tmp[IENC_SIMD_LS_MULTISTRUCT_POSTI] = p_simd_ls_multistruct_posti
ienc_parsers_tmp[IENC_SIMD_LS_ONESTRUCT] = p_simd_ls_onestruct
ienc_parsers_tmp[IENC_SIMD_LS_ONESTRUCT_POSTI] = p_simd_ls_onestruct_posti
ienc_parsers_tmp[IENC_PC_ADDR] = p_pc_addr
ienc_parsers_tmp[IENC_ADDSUB_IMM] = p_addsub_imm
ienc_parsers_tmp[IENC_LOG_IMM] = p_log_imm
ienc_parsers_tmp[IENC_MOV_WIDE_IMM] = p_mov_wide_imm
ienc_parsers_tmp[IENC_BITFIELD] = p_bitfield
ienc_parsers_tmp[IENC_EXTRACT] = p_extract
ienc_parsers_tmp[IENC_CMP_BRANCH_IMM] = p_cmp_branch_imm
ienc_parsers_tmp[IENC_BRANCH_UNCOND_IMM] = p_branch_uncond_imm
ienc_parsers_tmp[IENC_BRANCH_COND_IMM] = p_branch_cond_imm
ienc_parsers_tmp[IENC_EXCP_GEN] = p_excp_gen
ienc_parsers_tmp[IENC_SYS] = p_sys
ienc_parsers_tmp[IENC_TEST_BRANCH_IMM] = p_test_branch_imm
ienc_parsers_tmp[IENC_BRANCH_UNCOND_REG] = p_branch_uncond_reg
ienc_parsers_tmp[IENC_LOAD_REG_LIT] = p_load_reg_lit
ienc_parsers_tmp[IENC_LS_REG_US_IMM] = p_ls_reg_us_imm
ienc_parsers_tmp[IENC_LS_REG_UNSC_IMM] = p_ls_reg_unsc_imm
ienc_parsers_tmp[IENC_LS_REG_IMM_POSTI] = p_ls_reg_imm
ienc_parsers_tmp[IENC_LS_REG_UNPRIV] = p_ls_reg_unpriv
ienc_parsers_tmp[IENC_LS_REG_IMM_PREI] = p_ls_reg_imm
ienc_parsers_tmp[IENC_LS_REG_OFFSET] = p_ls_reg_offset
ienc_parsers_tmp[IENC_ADDSUB_CARRY] = p_addsub_carry
ienc_parsers_tmp[IENC_COND_CMP_REG] = p_cond_cmp_reg
ienc_parsers_tmp[IENC_COND_CMP_IMM] = p_cond_cmp_imm
ienc_parsers_tmp[IENC_COND_SEL] = p_cond_sel
ienc_parsers_tmp[IENC_DATA_PROC_3] = p_data_proc_3
ienc_parsers_tmp[IENC_DATA_PROC_2] = p_data_proc_2
ienc_parsers_tmp[IENC_DATA_PROC_1] = p_data_proc_1
ienc_parsers_tmp[IENC_FP_FP_CONV] = p_fp_fp_conv
ienc_parsers_tmp[IENC_FP_COND_COMPARE] = p_fp_cond_compare
ienc_parsers_tmp[IENC_FP_DP2] = p_fp_dp2
ienc_parsers_tmp[IENC_FP_COND_SELECT] = p_fp_cond_select
ienc_parsers_tmp[IENC_FP_IMMEDIATE] = p_fp_immediate
ienc_parsers_tmp[IENC_FP_COMPARE] = p_fp_compare
ienc_parsers_tmp[IENC_FP_DP1] = p_fp_dp1
ienc_parsers_tmp[IENC_FP_INT_CONV] = p_fp_int_conv
ienc_parsers_tmp[IENC_FP_DP3] = p_fp_dp3
ienc_parsers_tmp[IENC_SIMD_THREE_SAME] = p_simd_three_same
ienc_parsers_tmp[IENC_SIMD_THREE_DIFF] = p_simd_three_diff
ienc_parsers_tmp[IENC_SIMD_TWOREG_MISC] = p_simd_tworeg_misc
ienc_parsers_tmp[IENC_SIMD_ACROSS_LANES] = p_simd_across_lanes
ienc_parsers_tmp[IENC_SIMD_COPY] = p_simd_copy
ienc_parsers_tmp[IENC_SIMD_VECTOR_IE] = p_simd_vector_ie
ienc_parsers_tmp[IENC_SIMD_MOD_SHIFT_IMM] = p_simd_mod_shift_imm
ienc_parsers_tmp[IENC_SIMD_TBL_TBX] = p_simd_tbl_tbx
ienc_parsers_tmp[IENC_SIMD_ZIP_UZP_TRN] = p_simd_zip_uzp_trn
ienc_parsers_tmp[IENC_SIMD_EXT] = p_simd_ext
ienc_parsers_tmp[IENC_SIMD_SCALAR_THREE_SAME] = p_simd_scalar_three_same
ienc_parsers_tmp[IENC_SIMD_SCALAR_THREE_DIFF] = p_simd_scalar_three_diff
ienc_parsers_tmp[IENC_SIMD_SCALAR_TWOREG_MISC] = p_simd_scalar_tworeg_misc
ienc_parsers_tmp[IENC_SIMD_SCALAR_PAIRWISE] = p_simd_scalar_pairwise
ienc_parsers_tmp[IENC_SIMD_SCALAR_COPY] = p_simd_scalar_copy
ienc_parsers_tmp[IENC_SIMD_SCALAR_IE] = p_simd_scalar_ie
ienc_parsers_tmp[IENC_SIMD_SCALAR_SHIFT_IMM] = p_simd_scalar_shift_imm
ienc_parsers_tmp[IENC_CRPYTO_AES] = p_crypto_aes
ienc_parsers_tmp[IENC_CRYPTO_THREE_SHA] = p_crypto_three_sha
ienc_parsers_tmp[IENC_CRYPTO_TWO_SHA] = p_crypto_two_sha
ienc_parsers_tmp[IENC_UNDEF] = p_undef


ienc_parsers = tuple(ienc_parsers_tmp)

#------------------------------classes---------------------------------------|







class A64Operand(envi.Operand):
    '''
    Superclass for all types of A64 instruction operands
    '''
    tsize = 8
    def involvesPC(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None


class A64RegOper(A64Operand, envi.RegisterOper):
    '''
    Subclass of A64Operand. X-bit Register operand class
    '''
    def __init__(self, reg, va=0, oflags=0, size=8):
        if reg == None:
            raise Exception("ArmRegOper: None Reg Type!")
            raise envi.InvalidInstruction(mesg="None Reg Type!",
                    bytez='f00!', va=va)

        self.va = va
        self.reg = reg
        self.oflags = oflags
        self.size = size

    def repr(self, op):
        return rctx.getRegisterName(self.reg)

    def getOperValue(self, op, emu=None):
        if emu is None:
            return None # This operand type requires an emulator
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu, value):
        emu.setRegister(self.reg, value)

    def render(self, mcanv, op, idx):
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint is not None:
            mcanv.addNameText(name, typename="registers")
        else:
            name = rctx.getRegisterName(self.reg)
            rname = rctx.getRegisterName(self.reg&RMETA_NMASK)
            mcanv.addNameText(name, name=rname, typename="registers")


def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym is not None:
        return repr(sym)
    return "0x%.8x" % va


class A64ImmOper(A64Operand, envi.ImmedOper):
    '''
    Subclass of A64Operand. Immediate operand class
    '''
    def __init__(self, val=0, shval=0, shtype=S_ROR, va=0, size=4):
        self.val = val
        self.shval = shval
        self.shtype = shtype
        self.size = size

    def repr(self, op):
        ival = self.getOperValue(op)
        if self.tsize == 6:
            return "0x%.4x:0x%.8x" % (ival>>32, ival&0xffffffff)
        if ival > 4096:
            return "0x%.8x" % ival
        return str(ival)

    def getOperValue(self, op, emu=None):
        return shifters[self.shtype](self.val, self.shval, self.size, emu)

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint is not None:
            if mcanv.mem.isValidPointer(value):
                mcanv.addVaText(hint, value)
            else:
                mcanv.addNameText(hint)
        elif mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:

            if self.tsize == 6:
                mcanv.addNameText("0x%.4x:0x%.8x" % (value>>32, value&0xffffffff))
            elif value >= 4096:
                mcanv.addNameText('0x%.8x' % value)
            else:
                mcanv.addNameText(str(value))


class A64BarrierOptionOper(A64Operand):
    '''
    Subclass of A64Operand. 4-bit immediate or barrier option
    '''
    def __init__(self, val=0):
        self.val = val
        self.option = barrier_option_table[val]

class A64nzcvOper(A64Operand):
    '''
    Subclass of A64Operand. 4-bit immediate that sets N,Z,C, and V flags
    '''
    def __init__(self, val=0):
        self.val = val

class A64CondOper(A64Operand):
    '''
    Subclass of A64Operand. 4-bit cond encoding
    '''
    def __init__(self, val=0):
        self.val = val
        self.mnem = cond_table[val]

class A64NameOper(A64Operand):
    '''
    Subclass of A64Operand. Name operand class
    '''
    def __init__(self, val=0):
        self.val = val

class A64PreFetchOper(A64Operand):
    '''
    Subclass of A64Operand. prfop operand class (pre-fetch operation)
    '''
    def __init__(self, prfoptype, target, policy):
        self.type = prfoptype
        self.target = target
        self.policy = policy


class A64ShiftOper(A64Operand):
    '''
    Subclass of A64Operand. Shift applied to an operand/register
    '''
    def __init__(self, register, shtype, shval):
        self.register = register
        self.shtype = shtype
        self.shval = shval


class A64ExtendOper(A64Operand):
    '''
    Subclass of A64Operand. Extension applied to an operand/register
    '''
    def __init__(self, register, exttype, shval=0):
        self.register = register
        self.exttype = exttype
        if exttype == 'LSL':
            self.shval = shval
        else:
            self.shval = 0


class A64Opcode(envi.Opcode):
    _def_arch = envi.ARCH_A64

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
    
    def __repr__(self):
        x = []
        for op in self.opers:
            x.append(op.repr(self))
        return self.mnem + " " + ", ".join(x)

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
            #print("getBranches: next...", hex(self.va), self.size)

        flags = 0

        if self.iflags & envi.IF_COND:
            flags |= envi.BR_COND

        if self.iflags & (envi.IF_BRANCH | envi.IF_CALL):
            oper = self.opers[-1]

            # check for location being ODD
            operval = oper.getOperValue(self, emu)

            flags |= self._def_arch

            if self.iflags & envi.IF_CALL:
                flags |= envi.BR_PROC

            # actually add the branch here...
            # if we are a deref, add the DEREF
            if oper.isDeref():
                ref = oper.getOperAddr(self, emu)
                ret.append((ref, flags | envi.BR_DEREF))

            # if we point to a valid address, add that branch as well:
            ret.append((operval, flags))
            #print("getBranches: (0x%x) add  0x%x   %x"% (self.va, operval, flags))

        return ret


class A64Disasm:
    #weird thing in envi/__init__. Figure out later
    _optype = envi.ARCH_A64
    _opclass = A64Opcode
    fmt = None
    #This holds the current running Arm instruction version and mask
    #ARCH_REVS is a file containing all masks for various versions of ARM. In const.py
    _archVersionMask = ARCH_REVS['ARMv8A']

    def __init__(self, endian=ENDIAN_MSB, mask = 'a64'):
        self.setArchMask(mask)
        self.setEndian(endian)


    def setArchMask(self, key = 'ARMv8R'):
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
        '''
        Parse a series of bytes into an envi.Opcode instance
        ''' 
        opbytes = bytez[offset:offset+4]
        opval, = struct.unpack(self.fmt, opbytes)

        cond = 0

        opcode, mnem, olist, flags, simdflags = self.doDecode(va, opval, bytez, offset)

        if mnem == None or type(mnem) == int:
            raise Exception("mnem == %r!  0x%x" % (mnem, opval))

        #FIXME insert some stuff in here. Check out ArmV7 for better idea. Flag modification


        op = A64Opcode(va, opcode, mnem, cond, 4, olist, flags, simdflags)
        return op

    def doDecode(self, va, opval, bytez, offset):
        encfam = (opval >> 25) & 0xf

        '''
        Using encfam,find encoding. If we can't find an encoding (enc == None),
        then throw an exception.
        '''
        enc,nexttab = inittable[encfam]
        #print("opval: 0x%x   - encfam: 0x%x  (enc/nexttab: %r/%r)" % (opval, encfam, enc, nexttab))
        if nexttab != None: # we have to sub-parse...
            for mask,val,penc in nexttab:
                #print("penc", penc, iencs[penc])
                if (opval & mask) == val:
                    enc = penc
                    #print("- found: %r" % enc)
                    break

        # If we don't know the encoding by here, we never will ;)
        if enc == None:
            raise envi.InvalidInstruction(mesg="No encoding found!",
                    bytez=bytez[offset:offset+4], va=va)

        '''
        ienc_parsers is a dictionary of encoding names mapped to corresponding functions
        i.e. ienc_parsers[IENC_UNCOND] = p_uncond
        therefore calling ienc_parsers[enc](opval, va+8) calls the corresponding function with parameters
        opval and va+8
        '''
        opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
        return opcode, mnem, olist, flags, simdflags

######## helper functions #########
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

if __name__=="__main__":
    import envi.archs
    from envi.tests.test_arch_aarch64 import instrs
    #envi.archs.dismain( AArch64Disasm() )
    #for i in instrs:
    #    op = AArch64Disasm().disasm(i[1], 0, 0)
    #    print(op)
    op = A64Disasm().disasm('54abcdef'.decode('hex'), 0, 0)
    print(op)
    
