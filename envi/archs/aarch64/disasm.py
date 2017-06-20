
#Init table to help us find encfam. Either returns an enc, or a mask-val table with an enc
inittable = [
    ( None, None ), #0
    ( None, None ), #1
    ( None, None ), #2
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
    (IENC_DATA_SIMD, None) #f
]

'''
All the various tables inittable references
'''
s_4_table = [
    (0b00100001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LS_EXCL),
    (0b00100001100000000000000000000000, 0b00100000000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
    (0b00100001100000000000000000000000, 0b00100000100000000000000000000000, IENC_LS_REGPAIR_POSTI),
    (0b00100001100000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
    (0b00100001100000000000000000000000, 0b00100001100000000000000000000000, IENC_LS_REGPAIR_PREI),
    (0,0,IENC_UNDEF)#catch-all
]

s_5_table = [
    (0b00000001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LOG_SHFT_REG),
    (0b00000001001000000000000000000000, 0b00000001000000000000000000000000, IENC_ADDSUB_SHFT_REG),
    (0b00000001001000000000000000000000, 0b00000001001000000000000000000000, IENC_ADDSUB_EXT_REG),
    (0,0, IENC_UNDEF)#catch-all
    
]

s_6_table = [
    (0b10100001101111110000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_MULTISTRUCT)
    (0b10100001101000000000000000000000, 0b00000000100000000000000000000000, IENC_SIMD_LS_MULTISTRUCT_POSTI),
    (0b10100001100111110000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_ONESTRUCT),
    (0b10100001100000000000000000000000, 0b00000000000000000000000000000000, IENC_SIMD_LS_ONESTRUCT_POSTI),
    (0b00100001100000000000000000000000, 0b00100000000000000000000000000000, IENC_LS_NAPAIR_OFFSET),
    (0b00100001100000000000000000000000, 0b00100000100000000000000000000000, IENC_LS_REGPAIR_POSTI),
    (0b00100001100000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REGPAIR_OFFSET),
    (0b00100001100000000000000000000000, 0b00100001100000000000000000000000, IENC_LS_REGPAIR_PREI),
    (0,0,IENC_UNDEF) #catch-all
]

s_8_table = [
    (0b00000011000000000000000000000000, 0b00000000000000000000000000000000, IENC_PC_ADDR),
    (0b00000011000000000000000000000000, 0b00000001000000000000000000000000, IENC_ADDSUB),
    (0,0,IENC_UNDEF) #catch-all
]

s_9_table = [
    (0b00000011100000000000000000000000, 0b00000010000000000000000000000000, IENC_LOG_IMM),
    (0b00000011100000000000000000000000, 0b00000010100000000000000000000000, IENC_MOV_WIDE),
    (0b00000011100000000000000000000000, 0b00000011000000000000000000000000, IENC_BITFIELD),
    (0b00000011100000000000000000000000, 0b00000011100000000000000000000000, IENC_EXTRACT),
    (0,0,IENC_UNDEF)#catch-all
]

s_a_table = [
    (0b01100000000000000000000000000000, 0b00100000000000000000000000000000, IENC_CMP_BRANCH_IMM),
    (0b01100000000000000000000000000000, 0b00000000000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
    (0b11100000000000000000000000000000, 0b01000000000000000000000000000000, IENC_BRANCH_COND_IMM),
    (0b11100001000000000000000000000000, 0b11000000000000000000000000000000, IENC_EXCP_GEN),
    (0b11100001110000000000000000000000, 0b11000001000000000000000000000000, IENC_SYS)
    (0,0,IENC_UNDEF)#catch-all
]

s_b_table = [
    (0b01100000000000000000000000000000, 0b00100000000000000000000000000000, IENC_TEST_BRANCH_IMM),
    (0b11100000000000000000000000000000, 0b11000000000000000000000000000000, IENC_BRANCH_UNCOND_REG),
    (0b01100000000000000000000000000000, 0b00000000000000000000000000000000, IENC_BRANCH_UNCOND_IMM),
    (0,0,IENC_UNDEF)#catch-all
]

s_ce_table = [
    (0b00100001000000000000000000000000, 0b00000000000000000000000000000000, IENC_LOAD_REG_LIT),
    (0b00100001000000000000000000000000, 0b00100001000000000000000000000000, IENC_LS_REG_US_IMM),
    (0b00100001001000000000110000000000, 0b00100000000000000000000000000000, IENC_LS_REG_UNSC_IMM),
    (0b00100001001000000000110000000000, 0b00100000000000000000010000000000, IENC_LS_REG_IMM_POSTI),
    (0b00100001001000000000110000000000, 0b00100000000000000000100000000000, IENC_LS_REG_UNPRIV),
    (0b00100001001000000000110000000000, 0b00100000000000000000110000000000, IENC_LS_REG_IMM_PREI),
    (0b00100001001000000000110000000000, 0b00100000001000000000100000000000, IENC_LS_REG_OFFSET),
    (0,0,IENC_UNDEF)#catch-all
]

s_d_table = [
    (0b00000001111000000000000000000000, 0b00000000000000000000000000000000, IENC_ADDSUB_CARRY),
    (0b00000001111000000000100000000000, 0b00000000010000000000000000000000, IENC_COND_CMP_REG),
    (0b00000001111000000000100000000000, 0b00000000010000000000100000000000, IENC_COND_CMP_IMM),
    (0b00000001111000000000000000000000, 0b00000000100000000000000000000000, IENC_COND_SEL),
    (0b00000001000000000000000000000000, 0b00000001000000000000000000000000, IENC_DATA_PROC_3),
    (0b01000001111000000000000000000000, 0b00000000110000000000000000000000, IENC_DATA_PROC_2),
    (0b01000001111000000000000000000000, 0b01000000110000000000000000000000, IENC_DATA_PROC_1),
    (0,0,IENC_UNDEF)#catch-all
]


'''
ienc_parsers_tmp will be put into a tuple that will contain all iencs and their corresponding function
'''
ienc_parsers_tmp = [None for x in range(IENC_MAX)]

ienc_parsers_tmp[IENC_DATA_SIMD] = p_data_simd
ienc_parsers_tmp[IENC_LS_EXCL] = p_ls_excl
ienc_parsers_tmp[IENC_LS_NAPAIR_OFFSET] = p_ls_napair_offset
ienc_parsers_tmp[IENC_LS_REGPAIR_POSTI] = p_ls_regpair_posti
ienc_parsers_tmp[IENC_LS_REGPAIR_OFFSET] = p_ls_regpair_offset
ienc_parsers_tmp[IENC_LS_REGPAIR_PREI] = p_ls_regpair_prei
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
ienc_parsers_tmp[IENC_LS_REG_UNPRIV] = p_ls_reg_unpriv
ienc_parsers_tmp[IENC_LS_REG_IMM_PREI] = p_ls_reg_imm_prei
ienc_parsers_tmp[IENC_LS_REG_OFFSET] = p_ls_reg_offset
ienc_parsers_tmp[IENC_ADDSUB_CARRY] = p_addsub_carry
ienc_parsers_tmp[IENC_COND_CMP_REG] = p_cond_cmp_reg
ienc_parsers_tmp[IENC_COND_CMP_IMM] = p_cond_cmp_imm
ienc_parsers_tmp[IENC_COND_SEL] = p_cond_sel
ienc_parsers_tmp[IENC_DATA_PROC_3] = p_data_proc_3
ienc_parsers_tmp[IENC_DATA_PROC_2] = p_data_proc_2
ienc_parsers_tmp[IENC_DATA_PROC_1] = p_data_proc_1
ienc_parsers_tmp[IENC_UNDEF] = p_undef

ienc_parsers = tuple(ienc_parsers_tmp)


def p_pc_addr(opval,va):
    '''
    Get the A64Opcode parameters for a PC release address instruction
    '''
    op = opval >> 31
    rd = opval & 0xf
    immhi = opval >> 5 & 0x3ffff
    immlo = opval >> 29 & 0x3
    if op == 1:
        mnem = 'adrp'
        opcode = INS_ADRP
        olist = [
            A64RegOper(rd, va),
            A64ImmOper((immhi + immlo)*0x1000, 0, S_LSL, va)
        ]
    else:
        mnem = 'adr'
        opcode = INS_ADR
        olist = [
            A64RegOper(rd, va=va),
            A64ImmOper((immhi + immlo), 0, S_LSL, va)
        ]

    return opcode, mnem, olist, 0, 0

def p_addsub_imm(opval, va):
    '''
    Get the A64Opcode parameters for an Add/Subtract (immediate) instruction
    '''
    cond = opval >> 29
    mnem, opcode = addsub_table[cond]
    shift = opval >> 22 & 0x3
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f
    imm = opval >> 10 & 0xfff
    if shift == 0x00:
        olist = [
            A64RegOper(rd, va=va),
            A64RegOper(rn, va=va),
            A64ImmOper(imm, 0, S_LSL, va)
        ]
    elif shift == 0x01:
        olist = [
            A64RegOper(rd, va=va),
            A64RegOper(rn, va=va),
            A64ImmOper(imm, 12, S_LSL, va)
        ]
    else:
        raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction"
        olist = (
            A64ImmOper(opval)
        )
        
    return opcode, mnem, olist, 0, 0

addsub_imm_table = [
    ('add', INS_ADD),
    ('adds', INS_ADDS),
    ('sub', INS_SUB),
    ('subs', INS_SUBS),
    ('add', INS_ADD),
    ('adds', INS_ADDS),
    ('sub', INS_SUB),
    ('subs', INS_SUBS)
]

def p_log_imm(opval, va):
    '''
    Get the A64Opcode parameters for a logical (immediate) instruction
    '''
    sf = opval >> 31
    opc = opval >> 29 & 0x3
    N = opval >> 22
    immr = opval >> 16 & 0x3f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    flags = 0
    
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
        mnem = 'ands'
        opcode = INS_ANDS
        #FIXME flags

    olist = [
        A64RegOper(rn, va),
        A64RegOper(rd, va),
        A64ImmOper((N + imms + immr), 0, S_LSL, va)
        
    ]

    return opcode, mnem, olist, flags, 0

def p_mov_wide_imm(opval, va):
    '''
    Get the A64Opcode parameters for a Move Wide (immediate) instruction
    '''
    sf = opval >> 31
    opc = opval >> 29 & 0x3
    hw = opval >> 21 & 0x3
    imm16 = opval >> 5 & 0xffff
    rd = opval & 0x1f

    olist = [
        A64RegOper(rd, va),
        A64ImmOper(imm16, hw*0xf, S_LSL, va)
    ]

    if opc == 0x00:
        mnem = 'movn'
        opcode = INS_MOVN
    elif opc == 0x10:
        mnem = 'movz'
        opcode = INS_MOVZ
    elif opc == 0x11:
        mnem = 'movk'
        opcode = INS_MOVK
    else:
        raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction"
        olist = (
            A64ImmOper(opval)
        )        

    return opcode, mnem, olist, 0,0

def p_bitfield(opval, va):
    '''
    Get the parameters for an A64Opcode for a bitfield instruction
    '''
    sf = opval >> 31
    opc = opval >> 29 & 0x3
    N = opval >> 22
    immr = opval >> 16 & 0x3f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval >> 5 & 0x1f
    olist = [
        A64ImmOper(opval)
    ]
    mnem, opcode, flags = bitfield_table[opc]
    if opcode != IENC_UNDEF:
        olist = [
            A64RegOper(rd, va),
            A64RegOper(rn, va),
            A64ImmOper(immr, 0, S_LSL, va),
            A64ImmOper(imms, 0, S_LSL, va)
        ]

    return opcode, mnem, olist, flags, 0


bitfield_table = [
    ('sbfm', INS_SBFM, (1,1)),
    ('bfm', INS_BFM, (0,0)),
    ('ubfm', INS_UBFM, (1,0))
    ('undefined instruction', IENC_UNDEF, (0,0))
]

def p_extract(opval, va):
    '''
    Get the parameters for an A64Opcode for a extract instruction
    '''
    sf = opval >> 31
    rm = opval >> 16 & 0x1f
    imms = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    rd = opval & 0x1f

    mnem = 'extr'
    opcode = INS_EXTR
    olist = [
        A64RegOper(rd, va),
        A64RegOper(rn, va),
        A64RegOper(rm, va),
        A64ImmOper(imms, 0, S_LSL, va)
    ]

    return opcode, mnem, olist, 0, 0

def p_branch_uncond_imm(opval, va):
    '''
    Get the parameters for an A64Opcode for a Branch Unconditional (immediate) instruction
    '''
    op = opval >> 31
    imm26 = opval & 0x3ffffffff
    if op == 0:
        mnem = 'b'
        opcode = INS_B
    else:
        mnem = 'bl'
        opcode = INS_BL

    olist = [
        A64ImmOper(imm26*0x100, 0, S_LSL, va)
    ]

    return opcode, mnem, olist, 0, 0

def p_cmp_branch_imm(opval, va):
    '''
    Get the parameters for an A64Opcode for a Compare Branch (immediate) instruction
    '''
    sf = opval >> 31
    op = opval >> 24 & 0x1
    imm19 = opval >> 5 & 0x7ffff
    rt = opval & 0x1f

    if op == 0:
        mnem = 'cbz'
        opcode = INS_CBZ
    else:
        mnem = 'cbnz'
        opcode = INS_CBNZ

    olist = [
        A64RegOper(rt, va),
        A64ImmOper(imm19*0x100, 0, S_LSL, va)
    ]

    return opcode, mnem, olist, 0, 0

def p_test_branch_imm(opval, va):
    '''
    Test branch (immediate) instruction
    '''
    #FIXME

def p_branch_cond_imm(opval, va):
    '''
    Conditional branch (immediate) instruction
    '''
    #FIXME

def p_excp_gen(opval, va):
    '''
    Exception generation instruction
    '''
    opc = opval >> 21 & 0x7
    imm16 = opval >> 5 & 0xffff
    op2 = opval >> 2 & 0x7
    LL = opval & 0x3

    olist = [
        A64ImmOper(imm16, 0, S_LSL, va)
    ]
    
    if opc == 0x000:
        if LL == 0x01:
            mnem = 'sbc'
            opcode = INS_SVC
        elif LL == 0x10:
            mnem = 'hvc'
            opcode = INS_HVC
        elif LL == 0x11:
            mnem = 'smc'
            opcode = INS_SMC
        else:
            raise envi.InvalidInstruction(
                mesg="p_undef: invalid instruction (by definition in ARM spec)",
                bytez=struct.pack("<I", opval), va=va)
            opcode = IENC_UNDEF
            mnem = "undefined instruction"
            olist = (
                A64ImmOper(opval)
            )
    elif opc == 0x001:
        mnem = 'brk'
        opcode = INS_BRK
    elif opc == 0x010:
        mnem = 'hlt'
        opcode = INS_HLT
    elif opc == 0x101:
        if LL == 0x01:
            mnem = 'dcps1'
            opcode = INS_DCPS1
        elif LL == 0x10:
            mnem = 'dcps2'
            opcode = INS_DCPS2
        elif LL == 0x11:
            mnem = 'dcps3'
            opcode = INS_DCPS3
        else:
            raise envi.InvalidInstruction(
                mesg="p_undef: invalid instruction (by definition in ARM spec)",
                bytez=struct.pack("<I", opval), va=va)
            opcode = IENC_UNDEF
            mnem = "undefined instruction"
            olist = (
                A64ImmOper(opval)
            )
    else:
        raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction"
        olist = (
            A64ImmOper(opval)
        )
    return (opcode, mnem, olist, 0, 0)

def p_sys(opval, va):
    '''
    Returns parameters for an A64Opcode for a system instruction
    '''
    L = opval >> 21 & 0x1
    op0 = opval >> 19 & 0x3
    op1 = opval >> 16 & 0x7
    crn = opval >> 12 & 0xf
    crm = opval >> 8 & 0xf
    op2 = opval >> 5 & 0x3
    rt = opval & 0x1f
    relevant = opval & 0x3fffff

    if relevant & 0b1110001111000000011111 == 0b0000000100000000011111:
        opcode = INS_MSRI
        mnem = 'msr'
        olist = [
            #FIXME
        ]
        #FIXME flags =
        #FIXME simdflags =
        
    elif relevant & 0b1111111111000000011111 == 0b00001100100000000011111:
        opcode = INS_HINT
        mnem = 'hint'
        olist = [
            A64ImmOper(crm + op2, 0, S_LSL, va)
        ]
        flags = 0
        simdflags = 0
        
    elif relevant & 0b1111111111000011111111 == 0b00001100110000001011111:
        opcode = INS_CLREX
        mnem = 'clrex'
        olist = [
            A64ImmOper(crm, 0, S_LSL, va)
        ]
        flags = 0
        simdflags = 0

    elif relevant & 0b1111111111000011111111 == 0b00001100110000010011111:
        opcode = INS_DSB
        mnem = 'dsb'
        olist = [
            #FIXME
        ]
        #FIXME flags
        #FIXME simdflags

    elif relevant & 0b1111111111000011111111 == 0b00001100110000010111111:
        opcode = INS_DMB
        mnem = 'dmb'
        olist = [
            #FIXME
        ]
        #FIXME flags
        #FIXME simdflags

    elif relevant & 0b1111111111000011111111 == 0b00001100110000011011111:
        opcode = INS_ISB
        mnem = 'isb'
        olist = [
            #FIXME
        ]
        #FIXME flags
        #FIXME simdflags

    elif (L + op0) == 0x001:
        opcode = INS_SYS
        mnem = 'sys'
        olist = [
            A64ImmOper(op1, 0, S_LSL, va),
            #FIXME cn name oper?
            #FIXME cm name oper?
            A64ImmOper(0p2, 0, S_LSL, va),
            A64RegOper(rt, va) #optional operand
        ]
        flags = 0
        simdflags = 0

    elif (L + op0) & 0b110 == 0b010:
        opcode = INS_MSRR
        mnem = 'msr'
        olist = [
            A64RegOper(opval >> 5 & 0x7fff, va),
            A64RegOper(rt, va)
        ]
        flags = 0
        simdflags = 0

    elif (L + op0) & 0b111 == 0b101:
        opcode = INS_SYSL
        mnem = 'sysl'
        olist = [
            A64RegOper(rt, va),
            A64ImmOper(op1, 0, S_LSL, va),
            #FIXME name oper?
            #FIXME name oper?
            A64ImmOper(op2, 0 S_LSL, va)
        ]
        flags = 0
        simdflags = 0

    elif (L + op0) & 0b110 == 0b110:
        opcode = INS_MRS
        mnem = 'mrs'
        olist = [
            A64RegOper(rt, va),
            A64RegOper(opval >> 5 & 0x7fff, va)
        ]
        flags = 0
        simdflags = 0

    else:
        raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction"
        olist = (
            A64ImmOper(opval)
        )
        flags = 0
        simdflags = 0
    
    return opcode, mnem, olist, flags, simdflags

p_branch_uncond_reg(opval, va):
    '''
    Return A64Opcode parameters for an Unconditional Branch (register) instruction
    '''
    opc = opval >> 21 & 0xf
    op2 = opval >> 16 & 0x1f
    op3 = opval >> 10 & 0x3f
    rn = opval >> 5 & 0x1f
    op4 = opval & 0x1f
    if op2 == 0b11111 && op3 == 0b000000 && op4 == 0b00000:
        if opc == 0b0000:
            opcode = INS_BR
            mnem = 'br'
            olist = [
                A64RegOper(rn, va)
            ]
        elif opc == 0b0001:
            opcode = INS_BLR
            mnem = 'blr'
            olist = [
                A64RegOper(rn, va)
            ]
        elif opc == 0b0010:
            opcode = INS_RET
            mnem = 'ret'
            olist = [
                A64RegOper(rn, va)
            ]
        elif opc == 0b0100 && rn == 0b11111:
            opcode = INS_ERET
            mnem = 'eret'
            olist = [] #NOT A FIXME, EMPTY LIST
        elif opc == 0b0101 && rn == 0b11111:
            opcode = INS_DRPS
            mnem = 'drps'
            olist = [] #NOT A FIXME
        else:
            raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
                opcode = IENC_UNDEF
                mnem = "undefined instruction"
            olist = (
                A64ImmOper(opval)
            )           
    else:
        raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
        opcode = IENC_UNDEF
        mnem = "undefined instruction"
        olist = (
            A64ImmOper(opval)
        )

    return opcode, mnem, olist, 0,0   

def p_ls_excl(opval, va):
    '''
    Load/store exclusive instruction
    '''
    size = opval >> 30 & 0x3
    o2 = opval >> 23 & 0x1
    L = opval >> 22 & 0x1
    01 = opval >> 21 & 0x1
    rs = opval >> 16 & 0x1f
    o0 = opval >> 15 & 0x1
    rt2 = opval >> 10 & 0x1f
    rn = opval >> 5 & 0x1f
    rt = opval & 0x1f

    if size == 0b00 || size == 0b01:
        if o2 == 0b0:
            if L == 0b0:
                olist = [
                    A64RegOper(rs, va),
                    A64RegOper(rt, va),
                    A64RegOper(rn, va) #FIXME 64-bit
                ]
                if (o1 + o0) == 0b00:
                    opcode = INS_STXRB
                    mnem = 'stxr'
                elif (o1 + o0) == 0b01:
                    opcode = INS_STLXRB
                    mnem = 'stlxr'
                else:
                    raise envi.InvalidInstruction(
                        mesg="p_undef: invalid instruction (by definition in ARM spec)",
                        bytez=struct.pack("<I", opval), va=va)
                    opcode = IENC_UNDEF
                    mnem = "undefined instruction"
                    olist = (
                        A64ImmOper(opval),
                    )
                    return opcode, mnem, olist, 0,0
            else:
                olist = [
                    A64RegOper(rt, va),
                    A64RegOper(rn, va) #FIXME 64-bit
                ]
                if (o1 + o0) == 0b00:
                    opcode = INS_LDXRB
                    mnem = 'ldxr'
                elif (o1 + o0) == 0b01:
                    opcode = INS_LDAXRB
                    mnem = 'ldaxr'
                else:
                    raise envi.InvalidInstruction(
                        mesg="p_undef: invalid instruction (by definition in ARM spec)",
                        bytez=struct.pack("<I", opval), va=va)
                    opcode = IENC_UNDEF
                    mnem = "undefined instruction"
                    olist = (
                        A64ImmOper(opval),
                    )
                    return opcode, mnem, olist, 0,0
        else:
            olist = [
                A64RegOper(rt, va),
                A64RegOper(rn, va) #FIXME 64-bit
            ]
            if (L + o1 + o0) == 0b001:
                opcode = INS_STLRB
                mnem = 'stlr'
            elif (L + o1 + o0) == 0b101:
                opcode = INS_LDARB
                mnem = 'ldar'
            else:
                raise envi.InvalidInstruction(
                    mesg="p_undef: invalid instruction (by definition in ARM spec)",
                    bytez=struct.pack("<I", opval), va=va)
                opcode = IENC_UNDEF
                mnem = "undefined instruction"
                olist = (
                    A64ImmOper(opval),
                )
                return opcode, mnem, olist, 0,0
        if size == 0b00:
            mnem = mnem + 'b'
            opcode = opcode + 'B'
        else:
            mnem = mnem + 'h'
            opcode = opcode + 'H'
    elif size == 0b10:

    else:

    return opcode, mnem, olist, #FIXME flags?
        
    

def p_undef(opval, va):
    '''
    Undefined encoding family
    '''
    # FIXME: make this an actual opcode with the opval as an imm oper
    raise envi.InvalidInstruction(
            mesg="p_undef: invalid instruction (by definition in ARM spec)",
            bytez=struct.pack("<I", opval), va=va)
    opcode = IENC_UNDEF
    mnem = "undefined instruction"
    olist = (
        A64ImmOper(opval),
    )
        
    return (opcode, mnem, olist, 0, 0)

class A64Operand(envi.Operand):
    '''
    Superclass for all types of A64 instruction operands
    '''
    tsize = 4
    def involvesPC(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None

class A64RegOper(A64Operand):
    '''
    Subclass of A64Operand. Register operand class
    '''
    def __init__(self, reg, va=0, oflags=0):
        if reg == None:
            raise Exception("ArmRegOper: None Reg Type!")
            raise envi.InvalidInstruction(mesg="None Reg Type!",
                    bytez='f00!', va=va)
        self.va = va
        self.reg = reg
        self.oflags = oflags

class A64ImmOper(A64Operand):
    '''
    Subclass of A64Operand. Immediate operand class
    '''
    def __init__(self, val, shval=0, shtype=S_ROR, va=0, size=4):
        self.val = val
        self.shval = shval
        self.shtype = shtype
        self.size = size

         
class A64Opcode(envi.Opcode):
    _def_arch = envi.ARCH_ARMV8

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
    

class AArch64Disasm:
    #weird thing in envi/__init__. Figure out later
    _optype = envi.ARCH_ARMV8
    _opclass = A64Opcode
    fmt = None
    #This holds the current running Arm instruction version and mask
    #ARCH_REVS is a file containing all masks for various versions of ARM. In const.py
    _archVersionMask = ARCH_REVS['ARMv8A']

    def __init__(self, endian=ENDIAN_LSB, mask = 'ARMv8A'):
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
        opval = struct.unpack(self.fmt, opbytes)

        cond = opval >> 29 & 0x7

        opcode, mnem, olist, flags, smdflags = self.doDecode(va, opval, bytez, offset)

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

        '''
        ienc_parsers is a dictionary of encoding names mapped to corresponding functions
        i.e. ienc_parsers[IENC_UNCOND] = p_uncond
        therefore calling ienc_parsers[enc](opval, va+8) calls the corresponding function with parameters
        opval and va+8
        '''
        opcode, mnem, olist, flags, simdflags = ienc_parsers[enc](opval, va+8)
        return opcode, mnem, olist, flags, simdflags


        


        


if __name__=="__main__":
    import envi.archs
    envi.archs.dismain( AArch64Disasm() )
    
