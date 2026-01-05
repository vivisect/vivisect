


MODE_ARM        = 0
MODE_THUMB      = 1
MODE_JAZELLE    = 2
MODE_THUMBEE    = 3


#Support for different ARM Instruction set versions

# name          bitmask                    decimal         hex
REV_ARMv4   =   0b0000000000000000000001 #        1        0x1
REV_ARMv4T  =   0b0000000000000000000010 #        2        0x2
REV_ARMv5   =   0b0000000000000000000100 #        4        0x4
REV_ARMv5T  =   0b0000000000000000001000 #        8        0x8
REV_ARMv5E  =   0b0000000000000000010000 #       16        0x10
REV_ARMv5J  =   0b0000000000000000100000 #       32        0x20
REV_ARMv5TE =   0b0000000000000001000000 #       64        0x40
REV_ARMv6   =   0b0000000000000010000000 #      128        0x80
REV_ARMv6M  =   0b0000000000000100000000 #      256        0x100
REV_ARMv6T2 =   0b0000000000001000000000 #      512        0x200
REV_ARMv7A  =   0b0000000000010000000000 #     1024        0x400
REV_ARMv7R  =   0b0000000000100000000000 #     2048        0x800
REV_ARMv7M  =   0b0000000001000000000000 #     4096        0x1000
REV_ARMv7EM =   0b0000000010000000000000 #     8192        0x2000
REV_ARMv8A  =   0b0000000100000000000000 #    16384        0x4000
REV_ARMv8R  =   0b0000001000000000000000 #    32768        0x8000
REV_ARMv8M  =   0b0000010000000000000000 #    65536        0x10000

REV_ALL_ARMv4  = (REV_ARMv4 | REV_ARMv4T)
REV_ALL_ARMv5  = (REV_ARMv5 | REV_ARMv5T | REV_ARMv5E | REV_ARMv5J | REV_ARMv5TE)
REV_ALL_ARMv6  = (REV_ARMv6 | REV_ARMv6T2 | REV_ARMv6M)
REV_ALL_ARMv7  = (REV_ARMv7A | REV_ARMv7R | REV_ARMv7M | REV_ARMv7EM) 
REV_ALL_ARMv8  = (REV_ARMv8A | REV_ARMv8R | REV_ARMv8M)

#Todo - For easy instruction filtering add more like:
REV_ALL_TO_ARMv6 = REV_ALL_ARMv4 | REV_ALL_ARMv5 | REV_ALL_ARMv6
REV_ALL_FROM_ARMv6 = REV_ALL_ARMv6 | REV_ALL_ARMv7 | REV_ALL_ARMv8
#Note: since arm must be backwards compatible any depreciated commands
#Would be noted but not removed with the REV_ALL_TO_* if this is even used.
#These are put here for suggestion and comment for now

REV_ALL_ARM = (REV_ALL_ARMv4 | REV_ALL_ARMv5 | REV_ALL_ARMv6 | REV_ALL_ARMv7 | REV_ALL_ARMv8)

#Will be set below, THUMB16 up through v6 except v6T2, THUMB2 from v6T2 up, THUMBEE from v7 up.
REV_THUMB16 = REV_THUMB2  = REV_THUMBEE = 0   

ARCH_REVS = {}
#Iterate through all REV_ARM values and setup related combo values 
for name, val in list(globals().items()):
    if (not name.startswith('REV_ARM')):
        continue
    shortName = name[4:]
    #add to lookup dictionary
    ARCH_REVS[shortName] = val
    #setup thumb versions to Architecture versions
    if (int(shortName[4]) > 6 or shortName == 'ARMv6T2'):
        REV_THUMB2 = REV_THUMB2 | val
        if int(shortName[4])!= 6:
            REV_THUMBEE = REV_THUMBEE | val
    else:
        REV_THUMB16 = REV_THUMB16 | val
#Added thumbs to dictionary
ARCH_REVS['thumb16'] = REV_THUMB16
ARCH_REVS['thumb'] = REV_THUMB2
ARCH_REVS['thumbee'] = REV_THUMBEE
ARCH_REVSLEN = len(ARCH_REVS)

# The supported types of operand shifts (by the 2 bit field)
S_LSL = 0
S_LSR = 1
S_ASR = 2
S_ROR = 3
S_RRX = 4 # FIXME HACK XXX add this

opShifts = ('lsl', 'lsr', 'asr', 'ror', 'rrx')
movSuffixes = ('n', '', 'z', 'k')

extrepr = (
    'UXTB',
    'UXTH',
    'UXTW',
    'UXTX',
    'SXTB',
    'SXTH',
    'SXTW',
    'SXTX',
    'LSL',
)

EXT_UXTB    = 0
EXT_UXTH    = 1
EXT_UXTW    = 2
EXT_UXTX    = 3
EXT_SXTB    = 4
EXT_SXTH    = 5
EXT_SXTW    = 6
EXT_SXTX    = 7
EXT_LSL     = 8

ENDIAN_LSB = 0
ENDIAN_MSB = 1

iencs = (
    'IENC_DATA_SIMD',
    'IENC_LS_EXCL',
    'IENC_LS_NAPAIR_OFFSET',
    'IENC_LS_REGPAIR_POSTI',
    'IENC_LS_REGPAIR_OFFSET',
    'IENC_LS_REGPAIR_PREI',
    'IENC_LOG_SHFT_REG',
    'IENC_ADDSUB_SHFT_REG',
    'IENC_ADDSUB_EXT_REG',
    'IENC_SIMD_LS_MULTISTRUCT',
    'IENC_SIMD_LS_MULTISTRUCT_POSTI',
    'IENC_SIMD_LS_ONESTRUCT',
    'IENC_SIMD_LS_ONESTRUCT_POSTI',
    'IENC_PC_ADDR',
    'IENC_ADDSUB_IMM',
    'IENC_LOG_IMM',
    'IENC_MOV_WIDE_IMM',
    'IENC_BITFIELD',
    'IENC_EXTRACT',
    'IENC_CMP_BRANCH_IMM',
    'IENC_BRANCH_UNCOND_IMM',
    'IENC_BRANCH_COND_IMM',
    'IENC_EXCP_GEN',
    'IENC_SYS',
    'IENC_SME',
    'IENC_TEST_BRANCH_IMM',
    'IENC_BRANCH_UNCOND_REG',
    'IENC_LOAD_REG_LIT',
    'IENC_LS_REG_US_IMM',
    'IENC_LS_REG_UNSC_IMM',
    'IENC_LS_REG_IMM_POSTI',
    'IENC_LS_REG_UNPRIV',
    'IENC_LS_REG_IMM_PREI',
    'IENC_LS_REG_OFFSET',
    'IENC_LS_ATOMIC_MEM',
    'IENC_ADDSUB_CARRY',
    'IENC_COND_CMP_REG',
    'IENC_COND_CMP_IMM',
    'IENC_COND_SEL',
    'IENC_DATA_PROC_3',
    'IENC_DATA_PROC_2',
    'IENC_DATA_PROC_1',
    'IENC_FP_FP_CONV',
    'IENC_FP_COND_COMPARE',
    'IENC_FP_DP2',
    'IENC_FP_COND_SELECT',
    'IENC_FP_IMMEDIATE',
    'IENC_FP_COMPARE',
    'IENC_FP_DP1',
    'IENC_FP_INT_CONV',
    'IENC_FP_DP3',
    'IENC_SIMD_THREE_SAME',
    'IENC_SIMD_THREE_DIFF',
    'IENC_SIMD_TWOREG_MISC',
    'IENC_SIMD_ACROSS_LANES',
    'IENC_SIMD_COPY',
    'IENC_SIMD_VECTOR_IE',
    'IENC_SIMD_MOD_SHIFT_IMM',
    'IENC_SIMD_TBL_TBX',
    'IENC_SIMD_ZIP_UZP_TRN',
    'IENC_SIMD_EXT',
    'IENC_SIMD_SCALAR_THREE_SAME',
    'IENC_SIMD_SCALAR_THREE_DIFF',
    'IENC_SIMD_SCALAR_TWOREG_MISC',
    'IENC_SIMD_SCALAR_PAIRWISE',
    'IENC_SIMD_SCALAR_COPY',
    'IENC_SIMD_SCALAR_IE',
    'IENC_SIMD_SCALAR_SHIFT_IMM',
    'IENC_CRPYTO_AES',
    'IENC_CRYPTO_THREE_SHA',
    'IENC_CRYPTO_TWO_SHA',
    'IENC_SME_OUTER_PRODUCT_64_BIT',
    'IENC_SME_FP_OUTER_PRODUCT_32_BIT',
    'IENC_SME2_BINARY_OUTER_PRODUCT_32_BIT',
    'IENC_SME_INTEGER_OUTER_PRODUCT_32_BIT',
    'IENC_SME2_MULTI_VECTOR_MEMORY_CONTIGUOUS',
    'IENC_SME2_MULTI_VECTOR_MEMORY_STRIDED',
    'IENC_SME_MOVE_INTO_ARRAY',
    'IENC_SME_MOVE_FROM_ARRAY',
    'IENC_SME_ADD_VECTOR_TO_ARRAY',
    'IENC_SME_ZERO',
    'IENC_SME2_ZERO_LOOKUP_TABLE',
    'IENC_SME2_MOVE_LOOKUP_TABLE',
    'IENC_SME2_E0PAND_LOOKUP_TABLE_CONTIGUOUS',
    'IENC_SME2_MULTI_VECTOR_INDE0ED_ONE_REGISTER',
    'IENC_SME2_MULTI_VECTOR_INDE0ED_TWO_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_INDE0ED_FOUR_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_SVE_SELECT',
    'IENC_SME2_MULTI_VECTOR_SVE_CONSTRUCTIVE_BINARY',
    'IENC_SME2_MULTI_VECTOR_SVE_CONSTRUCTIVE_UNARY',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_VECTORS_SVE_DESTRUCTIVE_TWO_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_VECTORS_SVE_DESTRUCTIVE_FOUR_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_AND_SINGLE_SVE_DESTRUCTIVE_TWO_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_AND_SINGLE_SVE_DESTRUCTIVE_FOUR_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_AND_SINGLE_ARRAY_VECTORS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_ARRAY_VECTORS_TWO_REGISTERS',
    'IENC_SME2_MULTI_VECTOR_MULTIPLE_ARRAY_VECTORS_FOUR_REGISTERS',
    'IENC_SME_MEMORY',
    'IENC_SVE_INT_MULTADD_PRED',
    'IENC_SVE_INT_BINARITH_PRED',
    'IENC_SVE_INT_REDUCTION',
    'IENC_SVE_BIT_SHIFT_PRED',
    'IENC_SVE_INT_ADDSUB_VEC_UNPRED',
    'IENC_SVE_BIT_LOG_UNPRED',
    'IENC_SVE_INDEX_GEN',
    'IENC_SVE_STACK_ALLOC',
    'IENC_SVE2_INT_MULT_UNPRED',
    'IENC_SVE_BIT_SHIFT_UNPRED',
    'IENC_SVE_ADDR_GEN',
    'IENC_SVE_INT_MISC_UNPRED',
    'IENC_SVE_ELEMENT_COUNT',
    'IENC_SVE_BIT_IMM',
    'IENC_SVE_INT_WIDE_IMM_UNPRED',
    'IENC_SVE_DUP_INDEXED',
    'IENC_SVE_UNALLOC',
    'IENC_SVE_TABLE_LOOKUP_THREE',
    'IENC_TBL_ENC',
    'IENC_SVE_PERMUTE_VEC_UNPRED',
    'IENC_SVE_PERMUTE_PRED',
    'IENC_SVE_PERMUTE_VEC_ELEMENTS',
    'IENC_SVE_PERMUTE_VEC_PRED',
    'IENC_SEL_VECTORS',
    'IENC_SVE_PERMUTE_VEC_EXTRACT',
    'IENC_SVE_PERMUTE_VEC_SEGMENTS',
    'IENC_SVE_INT_COMPARE_VEC',
    'IENC_SVE_INT_COMPARE_UNSIGNED_IMM',
    'IENC_SVE_INT_COMPARE_SIGNED_IMM',
    'IENC_SVE_PRED_LOGICAL_OPS',
    'IENC_SVE_PROP_BREAK',
    'IENC_SVE_PART_BREAK',
    'IENC_SVE_PRED_MISC',
    'IENC_SVE_INT_COMPARE_SCALARS',
    'IENC_SVE_BROAD_PRED_ELEMENT',
    'IENC_SVE_SCALAR_INT_COMPARE_PRED_CTR',
    'IENC_SVE_PRED_COUNT',
    'IENC_SVE_INC_DEC_PRED_CNT',
    'IENC_SVE_WRITE_FFR',
    'IENC_SVE_INT_MULTADD_UNPRED',
    'IENC_SVE2_INT_UNPRED',
    'IENC_SVE_INT_CLAMP',
    'IENC_SVE_MULT_INDEXED',
    'IENC_SVE_INT_TWO_WAY_DOT_PROD',
    'IENC_SVE_INT_TWO_WAY_DOT_PROD_INDEXED',
    'IENC_SVE2_WIDEN_INT_ARITH',
    'IENC_SVE_MISC',
    'IENC_SVE2_ACCUM',
    'IENC_SVE2_NARROWING',
    'IENC_SVE2_CHAR_MATCH',
    'IENC_SVE2_HIST_COMP_SEG',
    'IENC_HISTCNT',
    'IENC_SVE2_CRYPTO_EXT',
    'IENC_FCMLA_VEC',
    'IENC_FCADD',
    'IENC_SVE_FLOAT_CVT_PREC_ODD_ELEMENTS',
    'IENC_SVE2_FLOAT_PAIR_OPS',
    'IENC_SVE_FLOAT_MULTADD_INDEXED',
    'IENC_SVE_FLOAT_COMPLEX_MULTADD_INDEXED',
    'IENC_SVE_FLOAT_MULT_INDEXED',
    'IENC_FCLAMP',
    'IENC_SVE_FLOAT_WIDENING_MULTADD_INDEXED',
    'IENC_SVE_FLOAT_WIDENING_MULTADD',
    'IENC_SVE_FLOAT_MATRIX_MULT_ACC',
    'IENC_SVE_FLOAT_COMPARE_VECTORS',
    'IENC_SVE_FLOAT_ARITH_UNPRED',
    'IENC_SVE_FLOAT_ARITH_PRED',
    'IENC_SVE_FLOAT_UNARY_PRED',
    'IENC_SVE_FLOAT_RECURSE_REDUCTION',
    'IENC_SVE_FLOAT_UNARY_UNPRED',
    'IENC_SVE_FLOAT_COMPARE_ZERO',
    'IENC_SVE_FLOAT_ACC_REDUCTION',
    'IENC_SVE_FLOAT_MULTADD',
    'IENC_SVE_MEM_32GATHER_UNSIZED_CONTIG',
    'IENC_SVE_MEM_CONTIG_LOAD',
    'IENC_SVE_MEM_64GATHER',
    'IENC_SVE_MEM_CONTIG_STORE_UNSIZED_CONTIG',
    'IENC_SVE_MEM_NONTEMP_QUAD_SCATTER_STORE',
    'IENC_SVE_MEM_NONTEMP_MULTIREG_CONTIG_STORE',
    'IENC_SVE_MEM_SCATTER_OPT_SIGN_EXT',
    'IENC_SVE_MEM_SCATTER',
    'IENC_SVE_MEM_CONTIG_STORE_IMM_OFF',
    'IENC_RESERVED',
    'IENC_UNDEF',
)

IENC_MAX = len(iencs)

for ieidx, enc in enumerate(iencs):
    globals()[enc] = ieidx

instrnames = [
    'ADR',
    'ADRP',
    'ADD',
    'ADDS',
    'SUB',
    'SUBS',
    'CMP',
    'CMN',
    'AND',
    'ORR',
    'EOR',
    'ANDS',
    'MOV',
    'BFM',
    'EXTR',
    'B',
    'BL',
    'ST',
    'LD',
    'SVC',
    'HVC',
    'SMC',
    'BRK',
    'HLT',
    'DCPS1',
    'DCPS2',
    'DCPS3',
    'MSR',
    'HINT',
    'CSDB',
    'PSB',
    'CLREX',
    'DSB',
    'DMB',
    'ISB',
    'SYS',
    'SB',
    'MRS',
    'BR',
    'BLR',
    'RET',
    'ERET',
    'DRPS',
    'STXRB',
    'STLXRB',
    'LDXRB',
    'LDAXRB',
    'STLRB',
    'LDARB',
    'STXRH',
    'STLXRH',
    'LDXRH',
    'LDAXRH',
    'STLRH',
    'LDARH',
    'STXR',
    'STLXR',
    'STXP',
    'STLXP',
    'LDXR',
    'LDAXR',
    'LDXP',
    'LDAXP',
    'STLR',
    'LDAR',
    'LDR',
    'LDRSW',
    'PRFM',
    'STNP',
    'LDNP',
    'STGP',
    'STP',
    'LDP',
    'LDPSW',
    'LDUR',
    'STUR',
    'PRFUM',
    'STTR',
    'LDTR',
    'STR',
    'LDR',
    'ST4',
    'ST1',
    'LD4',
    'LD1',
    'ST3',
    'LD3',
    'ST2',
    'LD2',
    'BIC',
    'EO',
    'OR',
    'ADC',
    'SBC',
    'CCM',
    'CSEL',
    'CSINC',
    'CINC',
    'CSINV',
    'CINV',
    'CSET',
    'CSETM',
    'CSNEG',
    'CNEG',
    'MADD',
    'MSUB',
    'MNEG',
    'SMADDL',
    'SMULL',
    'SMSUBL',
    'SMNEGL',
    'UMADDL',
    'UMULL',
    'UMSUBL',
    'SMULH',
    'UMULH',
    'UDIV',
    'SDIV',
    'LSLV',
    'LSRV',
    'ASRV',
    'RORV',
    'ASR',
    'LSL',
    'LSR',
    'BFI',
    'BFXIL',
    'SBFX',
    'UBFX',
    'SBFIZ',
    'UBFIZ',
    'XTB',
    'XTH',
    'XTW',
    'SXTB',
    'UXTB',
    'SXTH',
    'UXTH',
    'SXTW',
    'UXTW',
    'LDADD',
    'LDADDA',
    'LDADDAL',
    'LDADDL',
    'LDADDB',
    'LDADDAB',
    'LDADDALB',
    'LDADDLB',
    'LDADDH',
    'LDADDAH',
    'LDADDALH',
    'LDADDLH',
    'LDCLR',
    'LDCLRA',
    'LDCLRAL',
    'LDCLRL',
    'LDCLRB',
    'LDCLRAB',
    'LDCLRALB',
    'LDCLRLB',
    'LDCLRH',
    'LDCLRAH',
    'LDCLRALH',
    'LDCLRLH',
    'LDEOR',
    'LDEORA',
    'LDEORAL',
    'LDEORL',
    'LDEORB',
    'LDEORAB',
    'LDEORALB',
    'LDEORLB',
    'LDEORH',
    'LDEORAH',
    'LDEORALH',
    'LDEORLH',
    'LDSET',
    'LDSETA',
    'LDSETAL',
    'LDSETL',
    'LDSETB',
    'LDSETAB',
    'LDSETALB',
    'LDSETLB',
    'LDSETH',
    'LDSETAH',
    'LDSETALH',
    'LDSETLH',
    'LDSMAX',
    'LDSMAXA',
    'LDSMAXAL',
    'LDSMAXL',
    'LDSMAXB',
    'LDSMAXAB',
    'LDSMAXALB',
    'LDSMAXLB',
    'LDSMAXH',
    'LDSMAXAH',
    'LDSMAXALH',
    'LDSMAXLH',
    'LDSMIN',
    'LDSMINA',
    'LDSMINAL',
    'LDSMINL',
    'LDSMINB',
    'LDSMINAB',
    'LDSMINALB',
    'LDSMINLB',
    'LDSMINH',
    'LDSMINAH',
    'LDSMINALH',
    'LDSMINLH',
    'LDUMAX',
    'LDUMAXA',
    'LDUMAXAL',
    'LDUMAXL',
    'LDUMAXB',
    'LDUMAXAB',
    'LDUMAXALB',
    'LDUMAXLB',
    'LDUMAXH',
    'LDUMAXAH',
    'LDUMAXALH',
    'LDUMAXLH',
    'LDUMIN',
    'LDUMINA',
    'LDUMINAL',
    'LDUMINL',
    'LDUMINB',
    'LDUMINAB',
    'LDUMINALB',
    'LDUMINLB',
    'LDUMINH',
    'LDUMINAH',
    'LDUMINALH',
    'LDUMINLH',
    'STADD',
    'STADDL',
    'STADDB',
    'STADDLB',
    'STADDH',
    'STADDLH',
    'STCLR',
    'STCLRL',
    'STCLRB',
    'STCLRLB',
    'STCLRH',
    'STCLRLH',
    'STEOR',
    'STEORL',
    'STEORB',
    'STEORLB',
    'STEORH',
    'STEORLH',
    'STSET',
    'STSETL',
    'STSETB',
    'STSETLB',
    'STSETH',
    'STSETLH',
    'STSMAX',
    'STSMAXL',
    'STSMAXB',
    'STSMAXLB',
    'STSMAXH',
    'STSMAXLH',
    'STSMIN',
    'STSMINL',
    'STSMINB',
    'STSMINLB',
    'STSMINH',
    'STSMINLH',
    'STUMAX',
    'STUMAXL',
    'STUMAXB',
    'STUMAXLB',
    'STUMAXH',
    'STUMAXLH',
    'LD64B',
    'ST64B',
    'ST64BV',
    'ST64BV0',
    'ST64B',
    'STUMIN',
    'STUMINL',
    'STUMINB',
    'STUMINLB',
    'STUMINH',
    'STUMINLH',
    'SWP',
    'SWPL',
    'SWPA',
    'SWPAL',
    'SWPB',
    'SWPAB',
    'SWPALB',
    'SWPLB',
    'SWPH',
    'SWPLH',
    'SWPAH',
    'SWPALH',
    'SWPLH',
    'CAS',
    'CASL',
    'CASA',
    'CASAL',
    'CASB',
    'CASLB',
    'CASAB',
    'CASALB',
    'CASH',
    'CASAH',
    'CASALH',
    'CASLH',
    'CASP',
    'CASPA',
    'CASPAL',
    'CASPL',
    'CRC32',
    'RBIT',
    'REV',
    'CL',
    'SCVTF',
    'UCVTF',
    'FCVTZS',
    'FCVTZU',
    'FCCMP',
    'FMUL',
    'FDIV',
    'FADD',
    'FSUB',
    'FMAX',
    'FMIN',
    'FMAXNM',
    'FMINNM',
    'FNMUL',
    'FCSEL',
    'FMADD',
    'FMSUB',
    'FNMADD',
    'FNMSUB',
    'FCMP',
    'FMOV',
    'FABS',
    'FNEG',
    'FSQRT',
    'FCVT',
    'FRINT',
    'CM',
    'SHL',
    'MUL',
    'AC',
    'ABD',
    'RECP',
    'SQRT',
    'ML',
    'ABS',
    'NEG',
    'NEGS',
    'XT',
    'CVT',
    'MAX',
    'MIN',
    'DUP',
    'MLA',
    'MLS',
    'SHR',
    'SRA',
    'SLI',
    'SHA1C',
    'SHA1P',
    'SHA1M',
    'SHA1SU0',
    'SHA256H',
    'SHA256H2',
    'SHA256SU1',
    'SHA1H',
    'SHA1SU1',
    'SHA256SU0',
    'AESE',
    'AESD',
    'AESMC',
    'AESIMC',
    'ADDHN',
    'SUBHN',
    'MUL',
    'ABA',
    'ABD',
    'UZP1',
    'TRN1',
    'ZIP1',
    'UZP2',
    'TRN2',
    'ZIP2',
    'CBZ',
    'CBNZ',
    'TBZ',
    'TBNZ',
    'AT',
    'DC',
    'IC',
    'TLBI',
    'BCC',
    'UDF',
    'NOP',
    'YIELD',
    'WFE',
    'WFI',
    'SEV',
    'SEVL',
    'DGH',
    'TST',
    'XPACI',
    'XPACD',
    'XPACLRI',
    'FMINNMP',
    'UQSHL',
]

ins_index = 85
for instr in instrnames:
    globals()['INS_' + instr] = ins_index
    ins_index += 1

#IFLAGS
IF_LE = 1 << 56
IF_HS = 1 << 55
IF_GE = 1 << 54
IF_HI = 1 << 53
IF_EQ = 1 << 52
IF_LT = 1 << 51
IF_GT = 1 << 50
IF_2 = 1 << 49
IF_C = 1 << 48
IF_32 = 1 << 44
IF_16 = 1 << 43
IF_P = 1 << 42
IF_PSR_S = 1 << 41
IF_N = 1 << 40
IF_Z = 1 << 39
IF_K = 1 << 38
IF_L = 1 << 37
IF_A = 1 << 36
IF_X = 1 << 35
IF_R = 1 << 34
IF_P = 1 << 33
IF_B = 1 << 32
IF_H = 1 << 15
IF_SW = 1 << 14
IF_S = 1 << 13
IF_W = 1 << 12
IF_E = 1 << 11
IF_M = 1 << 10
IF_I = 1 << 9
IF_U = 1 << 8

IFP_UQ = 1 << 62
IFP_U = 1 << 61
IFP_S = 1 << 60
IFP_P = 1 << 59
IFP_QD = 1 << 58
IFP_R = 1 << 57

IFS = (
    None,
    '.8b',
    '.16b',
    '.4h',
    '.8h',
    '.2s',
    '.4s',
    '.1d',
    '.2d',
)

for ifx in range(1, len(IFS)):
    ifs = IFS[ifx]
    gblname = "IFS" + ifs.upper().replace('.', '_')
    globals()[gblname] = ifx

PM_usr = 0b10000
PM_fiq = 0b10001
PM_irq = 0b10010
PM_svc = 0b10011
PM_mon = 0b10110
PM_abt = 0b10111
PM_hyp = 0b11010
PM_und = 0b11011
PM_sys = 0b11111

# reg stuff stolen from regs.py to support proc_modes
# these are in context of reg_table, not reg_data.  
#  ie. these are indexes into the lookup table.
REG_OFFSET_USR = 17 * (PM_usr&0xf)
REG_OFFSET_FIQ = 17 * (PM_fiq&0xf)
REG_OFFSET_IRQ = 17 * (PM_irq&0xf)
REG_OFFSET_SVC = 17 * (PM_svc&0xf)
REG_OFFSET_MON = 17 * (PM_mon&0xf)
REG_OFFSET_ABT = 17 * (PM_abt&0xf)
REG_OFFSET_HYP = 17 * (PM_hyp&0xf)
REG_OFFSET_UND = 17 * (PM_und&0xf)
REG_OFFSET_SYS = 17 * (PM_sys&0xf)
#REG_OFFSET_CPSR = 17 * 16
REG_OFFSET_CPSR = 16                    # CPSR is available in every mode, and PM_usr and PM_sys don't have an SPSR.

REG_SPSR_usr = REG_OFFSET_USR + 17
REG_SPSR_fiq = REG_OFFSET_FIQ + 17
REG_SPSR_irq = REG_OFFSET_IRQ + 17
REG_SPSR_svc = REG_OFFSET_SVC + 17
REG_SPSR_mon = REG_OFFSET_MON + 17
REG_SPSR_abt = REG_OFFSET_ABT + 17
REG_SPSR_hyp = REG_OFFSET_HYP + 17
REG_SPSR_und = REG_OFFSET_UND + 17
REG_SPSR_sys = REG_OFFSET_SYS + 17

REG_PC = 0xf
REG_SP = 0xd
REG_BP = None
REG_CPSR = REG_OFFSET_CPSR
REG_FLAGS = REG_OFFSET_CPSR    #same location, backward-compat name

proc_modes = { # mode_name, short_name, description, offset, mode_reg_count, PSR_offset, privilege_level
    PM_usr: ("User Processor Mode", "usr", "Normal program execution mode", REG_OFFSET_USR, 15, REG_SPSR_usr, 0),
    PM_fiq: ("FIQ Processor Mode", "fiq", "Supports a high-speed data transfer or channel process", REG_OFFSET_FIQ, 8, REG_SPSR_fiq, 1),
    PM_irq: ("IRQ Processor Mode", "irq", "Used for general-purpose interrupt handling", REG_OFFSET_IRQ, 13, REG_SPSR_irq, 1),
    PM_svc: ("Supervisor Processor Mode", "svc", "A protected mode for the operating system", REG_OFFSET_SVC, 13, REG_SPSR_svc, 1),
    PM_mon: ("Monitor Processor Mode", "mon", "Secure Monitor Call exception", REG_OFFSET_MON, 13, REG_SPSR_mon, 1),
    PM_abt: ("Abort Processor Mode", "abt", "Implements virtual memory and/or memory protection", REG_OFFSET_ABT, 13, REG_SPSR_abt, 1),
    PM_hyp: ("Hyp Processor Mode", "hyp", "Hypervisor Mode", REG_OFFSET_HYP, 13, REG_SPSR_hyp, 2),
    PM_und: ("Undefined Processor Mode", "und", "Supports software emulation of hardware coprocessor", REG_OFFSET_UND, 13, REG_SPSR_und, 1),
    PM_sys: ("System Processor Mode", "sys", "Runs privileged operating system tasks (ARMv4 and above)", REG_OFFSET_SYS, 15, REG_SPSR_sys, 1),
}

VFP_QWORD_REG_COUNT = 32    # ARMv8-A docs

'''
from envi.archs.aarch64.disasm import A64PreFetchOper
#Supported PRFOP options
prfop = (
    A64PreFetchOper(PLD, L1, KEEP),
    A64PreFetchOper(PLD, L1, STRM),
    A64PreFetchOper(PLD, L2, KEEP),
    A64PreFetchOper(PLD, L2, STRM),
    A64PreFetchOper(PLD, L3, KEEP),
    A64PreFetchOper(PLD, L3, STRM),
    '#uimm5',
    '#uimm5',
    A64PreFetchOper(PLI, L1, KEEP),
    A64PreFetchOper(PLI, L1, STRM),
    A64PreFetchOper(PLI, L2, KEEP),
    A64PreFetchOper(PLI, L2, STRM),
    A64PreFetchOper(PLI, L3, KEEP),
    A64PreFetchOper(PLI, L3, STRM),
    '#uimm5',
    '#uimm5',
    A64PreFetchOper(PST, L1, KEEP),
    A64PreFetchOper(PST, L1, STRM),
    A64PreFetchOper(PST, L2, KEEP),
    A64PreFetchOper(PST, L2, STRM),
    A64PreFetchOper(PST, L3, KEEP),
    A64PreFetchOper(PST, L3, STRM),
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
    '#uimm5',
)
'''

sys_op_table = (
    (0b00001111000000, 'at', INS_AT),
    (0b10001111000000, 'at', INS_AT),
    (0b11001111000000, 'at', INS_AT),
    (0b00001111000001, 'at', INS_AT),
    (0b10001111000001, 'at', INS_AT),
    (0b11001111000001, 'at', INS_AT),
    (0b00001111000010, 'at', INS_AT),
    (0b00001111000011, 'at', INS_AT),
    (0b10001111000100, 'at', INS_AT),
    (0b10001111000101, 'at', INS_AT),
    (0b10001111000110, 'at', INS_AT),
    (0b10001111000111, 'at', INS_AT),
    (0b01101110100001, 'dc', INS_DC),
    (0b00001110110001, 'dc', INS_DC),
    (0b00001110110010, 'dc', INS_DC),
    (0b01101111010001, 'dc', INS_DC),
    (0b00001111010010, 'dc', INS_DC),
    (0b01101111011001, 'dc', INS_DC),
    (0b01101111110001, 'dc', INS_DC),
    (0b00001111110010, 'dc', INS_DC),
    (0b00001110001000, 'ic', INS_IC),
    (0b00001110101000, 'ic', INS_IC),
    (0b01101110101001, 'ic', INS_IC),
    (0b10010000000001, 'tlbi', INS_TLBI),
    (0b10010000000101, 'tlbi', INS_TLBI),
    (0b00010000011000, 'tlbi', INS_TLBI),
    (0b10010000011000, 'tlbi', INS_TLBI),
    (0b11010000011000, 'tlbi', INS_TLBI),
    (0b00010000011001, 'tlbi', INS_TLBI),
    (0b10010000011001, 'tlbi', INS_TLBI),
    (0b11010000011001, 'tlbi', INS_TLBI),
    (0b00010000011010, 'tlbi', INS_TLBI),
    (0b00010000011011, 'tlbi', INS_TLBI),
    (0b10010000011100, 'tlbi', INS_TLBI),
    (0b00010000011101, 'tlbi', INS_TLBI),
    (0b10010000011101, 'tlbi', INS_TLBI),
    (0b11010000011101, 'tlbi', INS_TLBI),
    (0b10010000011110, 'tlbi', INS_TLBI),
    (0b00010000011111, 'tlbi', INS_TLBI),
    (0b10010000100001, 'tlbi', INS_TLBI),
    (0b10010000100101, 'tlbi', INS_TLBI),
    (0b00010000111000, 'tlbi', INS_TLBI),
    (0b10010000111000, 'tlbi', INS_TLBI),
    (0b11010000111000, 'tlbi', INS_TLBI),
    (0b00010000111001, 'tlbi', INS_TLBI),
    (0b10010000111001, 'tlbi', INS_TLBI),
    (0b11010000111001, 'tlbi', INS_TLBI),
    (0b00010000111010, 'tlbi', INS_TLBI),
    (0b00010000111011, 'tlbi', INS_TLBI),
    (0b10010000111100, 'tlbi', INS_TLBI),
    (0b00010000111101, 'tlbi', INS_TLBI),
    (0b10010000111101, 'tlbi', INS_TLBI),
    (0b11010000111101, 'tlbi', INS_TLBI),
    (0b10010000111110, 'tlbi', INS_TLBI),
    (0b00010000111111, 'tlbi', INS_TLBI),
)

# AT instruction names, encoded as op1:CRm<0>:op2
at_op_table = {
    0b0000000: 'S1E1R',
    0b0000001: 'S1E1W',
    0b0000010: 'S1E0R',
    0b0000011: 'S1E0W',
    0b1000000: 'S1E2R',
    0b1000001: 'S1E2W',
    0b1000100: 'S12E1R',
    0b1000101: 'S12E1W',
    0b1000110: 'S12E0R',
    0b1000111: 'S12E0W',
    0b1100000: 'S1E3R',
    0b1100001: 'S1E3W',
    # Following require FEAT_PAN2:
    0b0001000: 'S1E1RP',
    0b0001001: 'S1E1WP'   
}

# DC instruction names, encoded as op1:crm:op2 
dc_op_table = {
    0b0000110001: 'IVAC',
    0b0000110010: 'ISW',
    0b0001010010: 'CSW',
    0b0001110010: 'CISW',
    0b0110100001: 'ZVA',
    0b0111010001: 'CVAC',
    0b0111011001: 'CVAU',
    0b0111110001: 'CIVAC',
    # Following require FEAT_MTE2:
    0b0000110011: 'IGVAC',
    0b0000110100: 'IGSW',
    0b0000110101: 'IGDVAC',
    0b0000110110: 'IGDSW',
    0b0001010100: 'CGSW',
    0b0001010110: 'CGDSW',
    0b0001110100: 'CIGSW',
    0b0001110110: 'CIGDSW ',
    # Following require FEAT_MTE:
    0b0110100011: 'GVA',
    0b0110100100: 'GZVA',
    0b0111010011: 'CGVAC',
    0b0111010101: 'CGDVAC',
    0b0111100011: 'CGVAP',
    0b0111100101: 'CGDVAP',
    0b0111101011: 'CGVADP',
    0b0111101101: 'CGDVADP',
    0b0111110011: 'CIGVAC',
    0b0111110101: 'CIGDVAC',
    # Following require FEAT_DPB:
    0b0111100001: 'CVAP',
    # Following require FEAT_DPB2:
    0b0111101001: 'CVADP',
    # Following require FEAT_MEC:
    0b1001110000: 'CIPAE',
    0b1001110111: 'CIGDPAE',
    # Following require FEAT_RME:
    0b1101110001: 'CIPAPA',
    0b1101110101: 'CIGDPAPA',
}

# IC instruction names, encoded as op1:crm:op2 
ic_op_table = {
    0b0000001000: 'IALLUIS',
    0b0000101000: 'IALLU',
    0b0110101001: 'IVAU'
}

# TLBI instruction names, encoded as op1:crn:crm:op2 
tlbi_op_table = {
    0b00010000011000: 'VMALLE1IS',
    0b00010000011001: 'VAE1IS',
    0b00010000011010: 'ASIDE1IS',
    0b00010000011011: 'VAAE1IS',
    0b00010000011101: 'VALE1IS',
    0b00010000011111: 'VAALE1IS',
    0b00010000111000: 'VMALLE1',
    0b00010000111001: 'VAE1',
    0b00010000011111: 'VAALE1IS',
    0b00010000111000: 'VMALLE1',
    0b00010000111001: 'VAE1',
    0b00010000111010: 'ASIDE1',
    0b00010000111011: 'VAAE1',
    0b00010000111101: 'VALE1',
    0b00010000111111: 'VAALE1',
    0b10010000000001: 'IPAS2E1IS',
    0b10010000000101: 'IPAS2LE1IS',
    0b10010000011000: 'ALLE2IS',
    0b10010000011001: 'VAE2IS',
    0b10010000011100: 'ALLE1IS',
    0b10010000011101: 'VALE2IS',
    0b10010000011110: 'VMALLS12E1IS',
    0b10010000100001: 'IPAS2E1',
    0b10010000100101: 'IPAS2LE1',
    0b10010000111000: 'ALLE2',
    0b10010000111001: 'VAE2',
    0b10010000111100: 'ALLE1',
    0b10010000111101: 'VALE2',
    0b10010000111110: 'VMALLS12E1',
    0b11010000011000: 'ALLE3IS',
    0b11010000011001: 'VAE3IS',
    0b11010000011101: 'VALE3IS',
    0b11010000111000: 'ALLE3',
    0b11010000111001: 'VAE3',
    0b11010000111101: 'VALE3',
    # Following require FEAT_TLBIOS:
    0b00010000001000: 'VMALLE1OS',
    0b00010000001001: 'VAE1OS',
    0b00010000001010: 'ASIDE1OS',
    0b00010000001011: 'VAAE1OS',
    0b00010000001101: 'VALE1OS',
    0b00010000001111: 'VAALE1OS',
    0b10010000001000: 'ALLE2OS',
    0b10010000001001: 'VAE2OS',
    0b10010000001100: 'ALLE1OS',
    0b10010000001100: 'VALE2OS',
    0b10010000011101: 'VMALLS12E1OS',
    0b10010000100000: 'IPAS2E1OS',
    0b10010000100100: 'IPAS2LE1OS',
    0b11010000001000: 'ALLE3OS',
    0b11010000001001: 'VAE3OS',
    0b11010000001101: 'VALE3OS',
    # Following requires FEAT_TLBIRANGE
    0b00010000010001: 'RVAE1IS',
    0b00010000010011: 'RVAAE1IS',
    0b00010000010101: 'RVALE1IS',
    0b00010000010111: 'RVAALE1IS',
    0b00010000101001: 'RVAE1OS',
    0b00010000101011: 'RVAAE1OS',
    0b00010000101101: 'RVALE1OS',
    0b00010000101111: 'RVAALE1OS',
    0b00010000110001: 'RVAE1',
    0b00010000110011: 'RVAAE1',
    0b00010000110101: 'RVALE1',
    0b00010000110111: 'RVAALE1',
    0b10010000000010: 'RIPAS2E1IS',
    0b10010000000110: 'RIPAS2LE1IS',
    0b10010000010001: 'RVAE2IS',
    0b10010000010101: 'RVALE2IS',
    0b10010000100010: 'RIPAS2E1',
    0b10010000100011: 'RIPAS2E1OS',
    0b10010000100110: 'RIPAS2LE1',
    0b10010000100111: 'RIPAS2LE1OS',
    0b10010000101001: 'RVAE20S',
    0b10010000101101: 'RVALE2OS',
    0b10010000110001: 'RVAE2',
    0b10010000110101: 'RVALE2',
    0b11010000010001: 'RVAE3IS',
    0b11010000010101: 'RVALE3IS',
    0b11010000101001: 'RVAE3OS',
    0b11010000101101: 'RVALE3OS',
    0b11010000110001: 'RAVE3',
    0b11010000110101: 'RVALE3',
    # Following require FEAT_XS:
    0b00010010001000: 'VMALLE1OSNXS',
    0b00010010001001: 'VAE1OSNXS',
    0b00010010001010: 'ASIDE1OSNXS',
    0b00010010001011: 'VAAESNXS',
    0b00010010001101: 'VALE1OSNXS',
    0b00010010001111: 'VAALE1OSNXS',
    0b00010010010001: 'RVAE1ISNXS',
    0b00010010010011: 'RVAAE1ISNXS',
    0b00010010010101: 'RVALE1ISNXS',
    0b00010010010111: 'RVAALE1ISNXS',
    0b00010010011000: 'VMALLE1ISNXS',
    0b00010010011001: 'VAE1ISNXS',
    0b00010010011010: 'ASIDE1ISNXS',
    0b00010010011011: 'VAAE1ISNXS',
    0b00010010011101: 'VALE1ISNXS',
    0b00010010011111: 'VAALE1ISNXS',
    0b00010010101001: 'RVAE1OSNXS',
    0b00010010101011: 'RVAAE1OSNXS',
    0b00010010101101: 'RVALE1OSNXS',
    0b00010010101111: 'RVAALE1OSNXS',
    0b00010010110001: 'RVAE1NXS',
    0b00010010110011: 'RVAAE1NXS',
    0b00010010110101: 'RVALE1NXS',
    0b00010010110111: 'RVAALE1NXS',
    0b00010010111000: 'VMALLE1NXS',
    0b00010010111001: 'VAE1NXS',
    0b00010010111010: 'ASIDE1NXS',
    0b00010010111011: 'VAAE1NXS',
    0b00010010111101: 'VALE1NXS',
    0b00010010111111: 'VAALE1NXS',
    0b10010010000001: 'IPAS2E1ISNXS',
    0b10010010000010: 'RIPAS2E1ISNXS',
    0b10010010000101: 'IPAS2LE1ISNXS',
    0b10010010000110: 'RIPAS2LE1ISNXS',
    0b10010010001000: 'ALLE2OSNXS',
    0b10010010001001: 'VAE2OSNXS',
    0b10010010001100: 'ALLE1OSNXS',
    0b10010010001101: 'VALE20SNXS',
    0b10010010001110: 'VMALLS12E1OSNXS',
    0b10010010010001: 'RVAE2ISNXS',
    0b10010010010101: 'RVALE2ISNXS',
    0b10010010011000: 'ALLE2ISNXS',
    0b10010010011001: 'VAE2ISNXS',
    0b10010010011100: 'ALLE1ISNXS',
    0b10010010011101: 'VALE2ISNXS',
    0b10010010011110: 'VMALLS12E1ISNXS',
    0b10010010100000: 'IPAS2E1OSNXS',
    0b10010010100001: 'IPAS2E1NXS',
    0b10010010100010: 'RIPAS2LE1NXS',
    0b10010010100011: 'RIPAS2E1OSNXS',
    0b10010010100100: 'IPAS2LE1OSNXS',
    0b10010010100101: 'IPAS2LE1NXS',
    0b10010010100110: 'RIPAS2LE1NXS',
    0b10010010100111: 'RIPAS2LE1OSNXS',
    0b10010010101001: 'RVAE2OSNXS',
    0b10010010101101: 'RVALE2OSNXS',
    0b10010010110001: 'RVAE2NXS',
    0b10010010110101: 'RAVLE2NXS',
    0b10010010111000: 'ALLE2NXS',
    0b10010010111001: 'VAE2NXS',
    0b10010010111100: 'ALLE1NXS',
    0b10010010111101: 'VALE2NXS',
    0b10010010111110: 'VMALLS12E1NXS',
    0b11010010001000: 'ALLE3OSNXS',
    0b11010010001001: 'VAE3OSNXS',
    0b11010010001101: 'VALE3OSNXS',
    0b11010010010001: 'RVAE3ISNXS',
    0b11010010010101: 'RVALE3ISNXS',
    0b11010010011000: 'ALLE3ISNXS',
    0b11010010011001: 'VAE3ISNXS',
    0b11010010011101: 'VALE3ISNXS',
    0b11010010101001: 'RVAE3OSNXS',
    0b11010010101101: 'RVALE3OSNXS',
    0b11010010110001: 'RVAE3NXS',
    0b11010010110101: 'RVALE3NXS',
    0b11010010111000: 'ALLE3NXS',
    0b11010010111001: 'VAE3NXS',
    0b11010010111101: 'VALE3NXS',
    # Following require FEAT_RME:
    0b11010000001100: 'PAALLOS',
    0b11010000100011: 'RPAOS',
    0b11010000100111: 'RPALOS',
    0b11010000111100: 'PAALL'
}

# Barrier operation assembler symbols, encoded in crm
bar_ops_table = {
    0b1111: 'sy',
    0b1110: 'st',
    0b1101: 'ld',
    0b1011: 'ish',
    0b1010: 'ishst',
    0b1001: 'ishld',
    0b0111: 'nsh',
    0b0110: 'nshst',
    0b0101: 'nshld',
    0b0011: 'osh',
    0b0010: 'oshst',
    0b0001: 'oshld'
}

psb_op = {
    0b0: 'csync'
}


sys_alias_op_tables = (
    at_op_table,
    dc_op_table,
    ic_op_table,
    tlbi_op_table,
    bar_ops_table,
    psb_op, 
)

barrier_option_table = (
    0,
    'OSHLD',
    'OSHST',
    'OSH',
    4,
    'NSHLD',
    'NSHST',
    'NSH',
    8,
    'ISHLD',
    'ISHST',
    'ISH',
    12,
    'LD',
    'ST',
    'SY',
)

b_cond_table = (
    ('b.eq', INS_BCC),
    ('b.ne', INS_BCC),
    ('b.hs', INS_BCC),
    ('b.lo', INS_BCC),
    ('b.mi', INS_BCC),
    ('b.pl', INS_BCC),
    ('b.vs', INS_BCC),
    ('b.vc', INS_BCC),
    ('b.hi', INS_BCC),
    ('b.ls', INS_BCC),
    ('b.ge', INS_BCC),
    ('b.lt', INS_BCC),
    ('b.gt', INS_BCC),
    ('b.le', INS_BCC),
    ('b.al', INS_BCC),
    ('b.nv^B', INS_BCC),
)

cond_table = (
    'EQ',
    'NE',
    'CS',
    'CC',
    'MI',
    'PL',
    'VS',
    'VC',
    'HI',
    'LS',
    'GE',
    'LT',
    'GT',
    'LE',
    'AL',
    'NV',
)

COND_EQ = 0
COND_NE = 1
COND_CS = 2
COND_CC = 3
COND_MI = 4
COND_PL = 5
COND_VS = 6
COND_VC = 7
COND_HI = 8
COND_LS = 9
COND_GE = 10
COND_LT = 11
COND_GT = 12
COND_LE = 13
COND_AL = 14
COND_NV = 15

inv_cond_table = (
        COND_NE,
        COND_EQ,
        COND_CC,
        COND_CS,
        COND_PL,
        COND_MI,
        COND_VC,
        COND_VS,
        COND_LS,
        COND_HI,
        COND_LT,
        COND_GE,
        COND_LE,
        COND_GT,
        COND_NV,
        COND_AL,
)


prefetchTypes = ["pld", "pli", "pst"]   
prefetchTargets = ["l1", "l2", "l3"]
prefetchPolicy = ["keep", "strm"]

# Pstatefield names for MSR using the "op1:op2:CRm" encoding
pstatefield_names = {
    0b0000110000: 'uao',
    0b0000110001: 'uao',
    0b0000110010: 'uao',
    0b0000110011: 'uao',
    0b0000110100: 'uao',
    0b0000110101: 'uao',
    0b0000110110: 'uao',
    0b0000110111: 'uao',
    0b0000111000: 'uao',
    0b0000111001: 'uao',
    0b0000111010: 'uao',
    0b0000111011: 'uao',
    0b0000111100: 'uao',
    0b0000111101: 'uao',
    0b0000111110: 'uao',
    0b0000111111: 'uao',
    0b0001000000: 'pan',
    0b0001000001: 'pan',
    0b0001000010: 'pan',
    0b0001000011: 'pan',
    0b0001000100: 'pan',
    0b0001000101: 'pan',
    0b0001000110: 'pan',
    0b0001000111: 'pan',
    0b0001001000: 'pan',
    0b0001001001: 'pan',
    0b0001001010: 'pan',
    0b0001001011: 'pan',
    0b0001001100: 'pan',
    0b0001001101: 'pan',
    0b0001001110: 'pan',
    0b0001001111: 'pan',
    0b0001010000: 'spsel',
    0b0001010001: 'spsel',
    0b0001010010: 'spsel',
    0b0001010011: 'spsel',
    0b0001010100: 'spsel',
    0b0001010101: 'spsel',
    0b0001010110: 'spsel',
    0b0001010111: 'spsel',
    0b0001011000: 'spsel',
    0b0001011001: 'spsel',
    0b0001011010: 'spsel',
    0b0001011011: 'spsel',
    0b0001011100: 'spsel',
    0b0001011101: 'spsel',
    0b0001011110: 'spsel',
    0b0001011111: 'spsel',
    0b0010000000: 'allint',
    0b0010000001: 'allint',
    0b0110100000: 'dit',
    0b0110100001: 'dit',
    0b0110100010: 'dit',
    0b0110100011: 'dit',
    0b0110100100: 'dit',
    0b0110100101: 'dit',
    0b0110100110: 'dit',
    0b0110100111: 'dit',
    0b0110101000: 'dit',
    0b0110101001: 'dit',
    0b0110101010: 'dit',
    0b0110101011: 'dit',
    0b0110101100: 'dit',
    0b0110101101: 'dit',
    0b0110101110: 'dit',
    0b0110101111: 'dit',
    0b0110110010: 'svcrsm',
    0b0110110011: 'svcrsm',
    0b0110110100: 'svcrza',
    0b0110110101: 'svcrza',
    0b0110110110: 'svcrsmza',
    0b0110110111: 'svcrsmza',
    0b0111000000: 'tco',
    0b0111000001: 'tco',
    0b0111000010: 'tco',
    0b0111000011: 'tco',
    0b0111000100: 'tco',
    0b0111000101: 'tco',
    0b0111000110: 'tco',
    0b0111000111: 'tco',
    0b0111001000: 'tco',
    0b0111001001: 'tco',
    0b0111001010: 'tco',
    0b0111001011: 'tco',
    0b0111001100: 'tco',
    0b0111001101: 'tco',
    0b0111001110: 'tco',
    0b0111001111: 'tco',
    0b0111100000: 'daifset',
    0b0111100001: 'daifset',
    0b0111100010: 'daifset',
    0b0111100011: 'daifset',
    0b0111100100: 'daifset',
    0b0111100101: 'daifset',
    0b0111100110: 'daifset',
    0b0111100111: 'daifset',
    0b0111101000: 'daifset',
    0b0111101001: 'daifset',
    0b0111101010: 'daifset',
    0b0111101011: 'daifset',
    0b0111101100: 'daifset',
    0b0111101101: 'daifset',
    0b0111101110: 'daifset',
    0b0111101111: 'daifset',
    0b0111110000: 'daifclr',
    0b0111110001: 'daifclr',
    0b0111110010: 'daifclr',
    0b0111110011: 'daifclr',
    0b0111110100: 'daifclr',
    0b0111110101: 'daifclr',
    0b0111110110: 'daifclr',
    0b0111110111: 'daifclr',
    0b0111111000: 'daifclr',
    0b0111111001: 'daifclr',
    0b0111111010: 'daifclr',
    0b0111111011: 'daifclr',
    0b0111111100: 'daifclr',
    0b0111111101: 'daifclr',
    0b0111111110: 'daifclr',
    0b0111111111: 'daifclr',
    0b0110010000: 'ssbs',
    0b0110010001: 'ssbs',
    0b0110010010: 'ssbs',
    0b0110010011: 'ssbs',
    0b0110010100: 'ssbs',
    0b0110010101: 'ssbs',
    0b0110010110: 'ssbs',
    0b0110010111: 'ssbs',
    0b0110011000: 'ssbs',
    0b0110011001: 'ssbs',
    0b0110011010: 'ssbs',
    0b0110011011: 'ssbs',
    0b0110011100: 'ssbs',
    0b0110011101: 'ssbs',
    0b0110011110: 'ssbs',
    0b0110011111: 'ssbs',
}

# Atomic operations mnem and opcode, encoded as size|v|a|r|o3|opc
ls_atomic_mem_table = {
    # Atomic add
    0b100000000: ['ldadd', INS_LDADD],
    0b100100000: ['ldadda', INS_LDADDA],
    0b100110000: ['ldaddal', INS_LDADDAL],
    0b100010000: ['ldaddl', INS_LDADDL],
    0b110000000: ['ldadd', INS_LDADD],
    0b110100000: ['ldadda', INS_LDADDA],
    0b110110000: ['ldaddal', INS_LDADDAL],
    0b110010000: ['ldaddl', INS_LDADDL],
    # Atomic add on byte
    0b000100000: ['ldaddab', INS_LDADDAB],
    0b000110000: ['ldaddalb', INS_LDADDALB],
    0b000000000: ['ldaddb', INS_LDADDB],
    0b000010000: ['ldaddlb', INS_LDADDLB],
    # Atomic add on halfword
    0b010100000: ['ldaddah', INS_LDADDAH],
    0b010110000: ['ldaddalh', INS_LDADDALH],
    0b010000000: ['ldaddh', INS_LDADDH],
    0b010010000: ['ldaddlh', INS_LDADDLH],
    # Atomic bit clear
    0b100000001: ['ldclr', INS_LDCLR],
    0b100100001: ['ldclra', INS_LDCLRA],
    0b100110001: ['ldclral', INS_LDCLRAL],
    0b100010001: ['ldclrl', INS_LDCLRL],
    0b110000001: ['ldclr', INS_LDCLR],
    0b110100001: ['ldclra', INS_LDCLRA],
    0b110110001: ['ldclral', INS_LDCLRAL],
    0b110010001: ['ldclrl', INS_LDCLRL],
    # Atomic bit clear on byte
    0b000100001: ['ldclrab', INS_LDCLRAB],
    0b000110001: ['ldclralb', INS_LDCLRALB],
    0b000000001: ['ldclrb', INS_LDCLRB],
    0b000010001: ['ldclrlb', INS_LDCLRLB],
    # Atomic bit clear on halfword
    0b010100001: ['ldclrah', INS_LDCLRAH],
    0b000110001: ['ldclralh', INS_LDCLRALH],
    0b000000001: ['ldclrh', INS_LDCLRH],
    0b000010001: ['ldclrlh', INS_LDCLRLH],
    # Atomic exclusive OR
    0b100000010: ['ldeor', INS_LDEOR],
    0b100100010: ['ldeora', INS_LDEORA],
    0b100110010: ['ldeoral', INS_LDEORAL],
    0b100010010: ['ldeorl', INS_LDEORL],
    0b110000010: ['ldeor', INS_LDEOR],
    0b110100010: ['ldeora', INS_LDEORA],
    0b110110010: ['ldeoral', INS_LDEORAL],
    0b110010010: ['ldeorl', INS_LDEORL],
    # Atomic exclusive OR on byte
    0b000100010: ['ldeorab', INS_LDEORAB],
    0b000110010: ['ldeoralb', INS_LDEORALB],
    0b000000010: ['ldeorb', INS_LDEORB],
    0b000010010: ['ldeorlb', INS_LDEORLB],
    # Atomic exclusive OR on halfword
    0b010100010: ['ldeorah', INS_LDEORAH],
    0b010110010: ['ldeoralh', INS_LDEORALH],
    0b010000010: ['ldeorh', INS_LDEORH],
    0b010010010: ['ldeorlh', INS_LDEORLH],
    # Atomic bit set
    0b100000011: ['ldset', INS_LDSET],
    0b100100011: ['ldseta', INS_LDSETA],
    0b100110011: ['ldsetal', INS_LDSETAL],
    0b100010011: ['ldsetl', INS_LDSETL],
    0b110000011: ['ldset', INS_LDSET],
    0b110100011: ['ldseta', INS_LDSETA],
    0b110110011: ['ldsetal', INS_LDSETAL],
    0b110010011: ['ldsetl', INS_LDSETL],
    # Atomic bit set on byte
    0b000100011: ['ldsetab', INS_LDSETAB],
    0b000110011: ['ldsetalb', INS_LDSETALB],
    0b000000011: ['ldsetb', INS_LDSETB],
    0b000010011: ['ldsetlb', INS_LDSETLB],
    # Atomic bit set on halfword
    0b010100011: ['ldsetah', INS_LDSETAH],
    0b010110011: ['ldsetalh', INS_LDSETALH],
    0b010000011: ['ldseth', INS_LDSETH],
    0b010010011: ['ldsetlh', INS_LDSETLH],
    # Atomic signed maximum
    0b100000100: ['ldsmax', INS_LDSMAX],
    0b100100100: ['ldsmaxa', INS_LDSMAXA],
    0b100110100: ['ldsmaxal', INS_LDSMAXAL],
    0b100010100: ['ldsmaxl', INS_LDSMAXL],
    0b110000100: ['ldsmax', INS_LDSMAX],
    0b110100100: ['ldsmaxa', INS_LDSMAXA],
    0b110110100: ['ldsmaxal', INS_LDSMAXAL],
    0b110010100: ['ldsmaxl', INS_LDSMAXL],
    # Atomic signed maximum on byte
    0b000000100: ['ldsmaxb', INS_LDSMAXB],
    0b000100100: ['ldsmaxab', INS_LDSMAXAB],
    0b000110100: ['ldsmaxalb', INS_LDSMAXALB],
    0b000010100: ['ldsmaxlb', INS_LDSMAXLB],
    # Atomic signed maximum on halfword
    0b010000100: ['ldsmaxh', INS_LDSMAXH],
    0b010100100: ['ldsmaxah', INS_LDSMAXAH],
    0b010110100: ['ldsmaxalh', INS_LDSMAXALH],
    0b010010100: ['ldsmaxlh', INS_LDSMAXLH],
    # Atomic signed minimum
    0b100000101: ['ldsmin', INS_LDSMIN],
    0b100100101: ['ldsmina', INS_LDSMINA],
    0b100110101: ['ldsminal', INS_LDSMINAL],
    0b100010101: ['ldsminl', INS_LDSMINL],
    0b110000101: ['ldsmin', INS_LDSMIN],
    0b110100101: ['ldsmina', INS_LDSMINA],
    0b110110101: ['ldsminal', INS_LDSMINAL],
    0b110010101: ['ldsminl', INS_LDSMINL],
    # Atomic signed minimum on byte
    0b000000101: ['ldsminb', INS_LDSMINB],
    0b000100101: ['ldsminab', INS_LDSMINAB],
    0b000110101: ['ldsminalb', INS_LDSMINALB],
    0b000010101: ['ldsminlb', INS_LDSMINLB],
    # Atomic signed minimum on halfword
    0b010000101: ['ldsminh', INS_LDSMINH],
    0b010100101: ['ldsminah', INS_LDSMINAH],
    0b010110101: ['ldsminalh', INS_LDSMINALH],
    0b010010101: ['ldsminlh', INS_LDSMINLH],
    # Atomic unsigned maximum
    0b100000110: ['ldumax', INS_LDUMAX],
    0b100100110: ['ldumaxa', INS_LDUMAXA],
    0b100110110: ['ldumaxal', INS_LDUMAXAL],
    0b100010110: ['ldumaxl', INS_LDUMAXL],
    0b110000110: ['ldumax', INS_LDUMAX],
    0b110100110: ['ldumaxa', INS_LDUMAXA],
    0b110110110: ['ldumaxal', INS_LDUMAXAL],
    0b110010110: ['ldumaxl', INS_LDUMAXL],
    # Atomic unsigned maximum on byte
    0b000000110: ['ldumaxb', INS_LDUMAXB],
    0b000100110: ['ldumaxab', INS_LDUMAXAB],
    0b000110110: ['ldumaxalb', INS_LDUMAXALB],
    0b000010110: ['ldumaxlb', INS_LDUMAXLB],
    # Atomic unsigned maximum on halfword
    0b010000110: ['ldumaxh', INS_LDUMAXH],
    0b010100110: ['ldumaxah', INS_LDUMAXAH],
    0b010110110: ['ldumaxalh', INS_LDUMAXALH],
    0b010010110: ['ldumaxlh', INS_LDUMAXLH],
    # Atomic unsigned minimum
    0b100000111: ['ldumin', INS_LDUMIN],
    0b100100111: ['ldumina', INS_LDUMINA],
    0b100110111: ['lduminal', INS_LDUMINAL],
    0b100010111: ['lduminl', INS_LDUMINL],
    0b110000111: ['ldumin', INS_LDUMIN],
    0b110100111: ['ldumina', INS_LDUMINA],
    0b110110111: ['lduminal', INS_LDUMINAL],
    0b110010111: ['lduminl', INS_LDUMINL],
    # Atomic unsigned minimum on byte
    0b000000111: ['lduminb', INS_LDUMINB],
    0b000100111: ['lduminab', INS_LDUMINAB],
    0b000110111: ['lduminalb', INS_LDUMINALB],
    0b000010111: ['lduminlb', INS_LDUMINLB],
    # Atomic unsigned minimum on halfword
    0b010000111: ['lduminh', INS_LDUMINH],
    0b010100111: ['lduminah', INS_LDUMINAH],
    0b010110111: ['lduminalh', INS_LDUMINALH],
    0b010010111: ['lduminlh', INS_LDUMINLH],
    # Single-copy Atomic 64-byte load
    0b110001101: ['ld64b', INS_LD64B],
    # Single-copy Atomic 64-byte store
    0b110001001: ['st64b', INS_ST64B],
    # Single-copy Atomic 64-byte Store with return
    0b110001011: ['st64bv', INS_ST64BV],
    # Single-copy Atomic 64-byte EL0 Store with Return 
    0b110001010: ['st64bv0', INS_ST64BV0],
    # Swap word or doubleword
    0b100001000: ['swp', INS_SWP],
    0b100101000: ['swpa', INS_SWPA],
    0b100111000: ['swpal', INS_SWPAL],
    0b100011000: ['swpl', INS_SWPL],
    0b110001000: ['swp', INS_SWP],
    0b110101000: ['swpa', INS_SWPA],
    0b110111000: ['swpal', INS_SWPAL],
    0b110011000: ['swpl', INS_SWPL],
    # Swap byte
    0b000001000: ['swpb', INS_SWPB],
    0b000101000: ['swpab', INS_SWPAB],
    0b000111000: ['swpalb', INS_SWPALB],
    0b000011000: ['swplb', INS_SWPLB],
    # Swap halfword
    0b010001000: ['swpb', INS_SWPH],
    0b010101000: ['swpab', INS_SWPAH],
    0b010111000: ['swpalb', INS_SWPALH],
    0b010011000: ['swplb', INS_SWPLH],
}

# Aliased Atomic operation mnem and opcode, encoded as size|v|a|r|o3|opc
ls_atomic_mem_alias_table = {
    # Atomic add, without return 
    0b100000000: ['stadd', INS_STADD],
    0b100010000: ['staddl', INS_STADDL],
    0b110000000: ['stadd', INS_STADD],
    0b110010000: ['staddl', INS_STADDL],
    # Atomic add on byte, without return
    0b000000000: ['staddb', INS_STADDB],
    0b000010000: ['staddlb', INS_STADDLB],
    # Atomic add on halfword, without return
    0b010000000: ['staddh', INS_STADDH],
    0b010010000: ['staddlh', INS_STADDLH],
    # Atomic bit clear, without return
    0b100000001: ['stclr', INS_STCLR],
    0b100010001: ['stclrl', INS_STCLRL],
    0b110000001: ['stclr', INS_STCLR],
    0b110010001: ['stclrl', INS_STCLRL],
    # Atomic bit clear on byte, without return
    0b000000001: ['stclrb', INS_STCLRB],
    0b000010001: ['stclrlb', INS_STCLRLB],
    # Atomic bit clear on halfword, without return
    0b010000001: ['stclrh', INS_STCLRH],
    0b010010001: ['stclrlh', INS_STCLRLH],
    # Atomic exclusive-OR, without return 
    0b100000010: ['steor', INS_STEOR],
    0b100010010: ['steorl', INS_STEORL],
    0b110000010: ['steor', INS_STEOR],
    0b110010010: ['steorl', INS_STEORL],
    # Atomic exclusive-OR on byte, without return 
    0b000000010: ['steorb', INS_STEORB],
    0b000010010: ['steorlb', INS_STEORLB],
    # Atomic exclusive-OR on halfword, without return
    0b010000010: ['steorh', INS_STEORH],
    0b010010010: ['steorlh', INS_STEORLH],
    # Atomic signed maximum, without return
    0b100000100: ['stsmax', INS_STSMAX],
    0b100010100: ['stsmaxl', INS_STSMAXL],
    0b110000100: ['stsmax', INS_STSMAX],
    0b110010100: ['stsmaxl', INS_STSMAXL],
    # Atomic signed maximum on byte, without return
    0b000000100: ['stsmaxb', INS_STSMAXB],
    0b000010100: ['stsmaxlb', INS_STSMAXLB],
    # Atomic signed maximum on halfword, without return
    0b010000100: ['stsmaxh', INS_STSMAXH],
    0b010010100: ['stsmaxlh', INS_STSMAXLH],
    # Atomic signed minimum, without return
    0b100000101: ['stsmin', INS_STSMIN],
    0b100010101: ['stsminl', INS_STSMINL],
    0b110000101: ['stsmin', INS_STSMIN],
    0b110010101: ['stsminl', INS_STSMINL],
    # Atomic signed minimum on byte, without return
    0b000000101: ['stsminb', INS_STSMINB],
    0b000010101: ['stsminlb', INS_STSMINLB],
    # Atomic signed minimum on halfword, without return
    0b010000101: ['stsminh', INS_STSMINH],
    0b010010101: ['stsminlh', INS_STSMINLH],
    # Atomic unsigned maximum, without return 
    0b100000110: ['stumax', INS_STUMAX],
    0b100010110: ['stumaxl', INS_STUMAXL],
    0b110000110: ['stumax', INS_STUMAX],
    0b110010110: ['stumaxl', INS_STUMAXL],
    # Atomic unsigned maximum on byte, without return 
    0b000000110: ['stumaxb', INS_STUMAXB],
    0b000010110: ['stumaxlb', INS_STUMAXLB],
    # Atomic unsigned maximum on halfword, without return 
    0b010000110: ['stumaxh', INS_STUMAXH],
    0b010010110: ['stumaxlh', INS_STUMAXLH],
    # Atomic unsigned minimum, without return
    0b100000111: ['stumin', INS_STUMIN],
    0b100010111: ['stuminl', INS_STUMINL],
    0b110000111: ['stumin', INS_STUMIN],
    0b110010111: ['stuminl', INS_STUMINL],
    # Atomic unsigned minimum on byte, without return
    0b000000111: ['stuminb', INS_STUMINB],
    0b000010111: ['stuminlb', INS_STUMINLB],
    # Atomic unsigned minimum on halfword, without return
    0b010000111: ['stuminh', INS_STUMINH],
    0b010010111: ['stuminlh', INS_STUMINLH],
}


# Compare and Swap operation mnem and opcode, encoded as size|v|a|r|o3|opc
ls_comp_swap_table = {
    # Compare and Swap word or doubleword
    0b100100111: ['cas', INS_CAS],
    0b100110111: ['casa', INS_CASA],
    0b100111111: ['casal', INS_CASAL],
    0b100101111: ['casl', INS_CASL],
    0b110100111: ['cas', INS_CAS],
    0b110110111: ['casa', INS_CASA],
    0b110111111: ['casal', INS_CASAL],
    0b110101111: ['casl', INS_CASL],
    # Compare and Swap byte
    0b000100111: ['casb', INS_CASB],
    0b000110111: ['casab', INS_CASAB],
    0b000111111: ['casalb', INS_CASALB],
    0b000101111: ['caslb', INS_CASLB],
    # Compare and Swap halfword
    0b010100111: ['cash', INS_CASH],
    0b010110111: ['casah', INS_CASAH],
    0b010111111: ['casalh', INS_CASALH],
    0b010101111: ['caslh', INS_CASLH],
    # Compare and Swap Pair of words or doublewords
    0b000000111: ['casp', INS_CASP],
    0b000010111: ['caspa', INS_CASPA],
    0b000011111: ['caspal', INS_CASPAL],
    0b000001111: ['caspl', INS_CASPL],
    0b010000111: ['casp', INS_CASP],
    0b010010111: ['caspa', INS_CASPA],
    0b010011111: ['caspal', INS_CASPAL],
    0b010001111: ['caspl', INS_CASPL],
}
