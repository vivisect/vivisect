


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

ENDIAN_LSB = 0
ENDIAN_MSB = 1

iencs = (\
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
    'IENC_RESERVED',
    'IENC_UNDEF',
)

IENC_MAX = len(iencs)

for ieidx in range(IENC_MAX):
    globals()[iencs[ieidx]] = ieidx

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
    'CLREX',
    'DSB',
    'DMB',
    'ISB',
    'SYS',
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
    'CS',
    'MADD',
    'MSUB',
    'SMADDL',
    'SMULL',
    'SMSUBL',
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
    'TBLI',
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
IF_NEG = 1 << 48
IF_INV = 1 << 47
IF_INC = 1 << 46
IF_EL = 1 << 45
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
    (0b10010000000001, 'tlbi', INS_TBLI),
    (0b10010000000101, 'tlbi', INS_TBLI),
    (0b00010000011000, 'tlbi', INS_TBLI),
    (0b10010000011000, 'tlbi', INS_TBLI),
    (0b11010000011000, 'tlbi', INS_TBLI),
    (0b00010000011001, 'tlbi', INS_TBLI),
    (0b10010000011001, 'tlbi', INS_TBLI),
    (0b11010000011001, 'tlbi', INS_TBLI),
    (0b00010000011010, 'tlbi', INS_TBLI),
    (0b00010000011011, 'tlbi', INS_TBLI),
    (0b10010000011100, 'tlbi', INS_TBLI),
    (0b00010000011101, 'tlbi', INS_TBLI),
    (0b10010000011101, 'tlbi', INS_TBLI),
    (0b11010000011101, 'tlbi', INS_TBLI),
    (0b10010000011110, 'tlbi', INS_TBLI),
    (0b00010000011111, 'tlbi', INS_TBLI),
    (0b10010000100001, 'tlbi', INS_TBLI),
    (0b10010000100101, 'tlbi', INS_TBLI),
    (0b00010000111000, 'tlbi', INS_TBLI),
    (0b10010000111000, 'tlbi', INS_TBLI),
    (0b11010000111000, 'tlbi', INS_TBLI),
    (0b00010000111001, 'tlbi', INS_TBLI),
    (0b10010000111001, 'tlbi', INS_TBLI),
    (0b11010000111001, 'tlbi', INS_TBLI),
    (0b00010000111010, 'tlbi', INS_TBLI),
    (0b00010000111011, 'tlbi', INS_TBLI),
    (0b10010000111100, 'tlbi', INS_TBLI),
    (0b00010000111101, 'tlbi', INS_TBLI),
    (0b10010000111101, 'tlbi', INS_TBLI),
    (0b11010000111101, 'tlbi', INS_TBLI),
    (0b10010000111110, 'tlbi', INS_TBLI),
    (0b00010000111111, 'tlbi', INS_TBLI),
)

# AT instruction names, encoded as op1:CRm<0>:op2
at_op_table = (
    (0B0000000, 'S1E1R'),
    (0B0000001, 'S1E1W'),
    (0B0000010, 'S1E0R'),
    (0B0000011, 'S1E0W'),
    (0B1000000, 'S1E2R'),
    (0B1000001, 'S1E2W'),
    (0B1000100, 'S12E1R'),
    (0B1000101, 'S12E1W'),
    (0B1000110, 'S12E0R'),
    (0B1000111, 'S12E0W'),
    (0B1100000, 'S1E3R'),
    (0B1100001, 'S1E3W'),
    # Following require FEAT_PAN2:
    (0B0001000, 'S1E1RP'),
    (0B0001001, 'S1E1WP')
)

# DC instruction names, encoded as op1:crm:op2 
dc_op_table = (
    (0b0000110001, 'IVAC'),
    (0b0000110010, 'ISW'),
    (0b0001010010, 'CSW'),
    (0b0001110010, 'CISW'),
    (0b0110100001, 'ZVA'),
    (0b0111010001, 'CVAC'),
    (0b0111011001, 'CVAU'),
    (0b0111110001, 'CIVAC'),
    # Following require FEAT_MTE2:
    (0b0000110011, 'IGVAC'),
    (0b0000110100, 'IGSW'),
    (0b0000110101, 'IGDVAC'),
    (0b0000110110, 'IGDSW'),
    (0b0001010100, 'CGSW'),
    (0b0001010110, 'CGDSW'),
    (0b0001110100, 'CIGSW'),
    (0b0001110110, 'CIGDSW '),
    # Following require FEAT_MTE:
    (0b0110100011, 'GVA'),
    (0b0110100100, 'GZVA'),
    (0b0111010011, 'CGVAC'),
    (0b0111010101, 'CGDVAC'),
    (0b0111100011, 'CGVAP'),
    (0b0111100101, 'CGDVAP'),
    (0b0111101011, 'CGVADP'),
    (0b0111101101, 'CGDVADP'),
    (0b0111110011, 'CIGVAC'),
    (0b0111110101, 'CIGDVAC'),
    # Following require FEAT_DPB:
    (0b0111100001, 'CVAP'),
    # Following require FEAT_DPB2:
    (0b0111101001, 'CVADP'),
    # Following require FEAT_MEC:
    (0b1001110000, 'CIPAE'),
    (0b1001110111, 'CIGDPAE'),
    # Following require FEAT_RME:
    (0b1101110001, 'CIPAPA'),
    (0b1101110101, 'CIGDPAPA'),
)

# IC instruction names, encoded as op1:crm:op2 
ic_op_table = (
    (0b0000001000, 'IALLUIS'),
    (0b0000101000, 'IALLU'),
    (0b0110101001, 'IVAU')
)

# TLBI instruction names, encoded as op1:crn:crm:op2 
tlbi_op_table = (
    (0b00010000011000, 'VMALLE1IS'),
    (0b00010000011001, 'VAE1IS'),
    (0b00010000011010, 'ASIDE1IS'),
    (0b00010000011011, 'VAAE1IS'),
    (0b00010000011101, 'VALE1IS'),
    (0b00010000011111, 'VAALE1IS'),
    (0b00010000111000, 'VMALLE1'),
    (0b00010000111001, 'VAE1'),
    (0b00010000011101, 'VALE1IS'),
    (0b00010000011111, 'VAALE1IS'),
    (0b00010000111000, 'VAMLLE1'),
    (0b00010000111001, 'VAE1'),
    (0b00010000111010, 'ASIDE1'),
    (0b00010000111011, 'VAAE1'),
    (0b00010000111101, 'VALE1'),
    (0b00010000111111, 'VAALE1'),
    (0b10010000000001, 'IPAS2E1IS'),
    (0b10010000000101, 'IPAS2LE1IS'),
    (0b10010000011000, 'ALLE2IS'),
    (0b10010000011001, 'VAE2IS'),
    (0b10010000011100, 'ALLE1IS'),
    (0b10010000011101, 'VALE2IS'),
    (0b10010000011110, 'VMALLS12E1IS'),
    (0b10010000100001, 'IPAS2E1'),
    (0b10010000100101, 'IPAS2LE1'),
    (0b10010000111000, 'ALLE2'),
    (0b10010000111001, 'VAE2'),
    (0b10010000111100, 'ALLE1'),
    (0b10010000111101, 'VALE2'),
    (0b10010000111110, 'VMALLS12E1'),
    (0b11010000011000, 'ALLE3IS'),
    (0b11010000011001, 'VAE3IS'),
    (0b11010000011101, 'VALE3IS'),
    (0b11010000111000, 'ALLE3'),
    (0b11010000111001, 'VAE3'),
    (0b11010000111101, 'VALE3'),
    # Following require FEAT_TLBIOS:
    (0b00010000001000, 'VMALLE1OS'),
    (0b00010000001001, 'VAE1OS'),
    (0b00010000001010, 'ASIDE1OS'),
    (0b00010000001011, 'VAAE1OS'),
    (0b00010000001101, 'VALE1OS'),
    (0b00010000001111, 'VAALE1OS'),
    (0b10010000001000, 'ALLE2OS'),
    (0b10010000001001, 'VAE2OS'),
    (0b10010000001100, 'ALLE1OS'),
    (0b10010000001100, 'VALE2OS'),
    (0b00010000011101, 'VMALLS12E1OS'),
    (0b10010000100000, 'IPAS2E1OS'),
    (0b10010000100100, 'IPAS2LE1OS'),
    (0b11010000001000, 'ALLE3OS'),
    (0b11010000001001, 'VAE3OS'),
    (0b11010000001101, 'VALE3OS'),
    # Following requires FEAT_TLBIRANGE
    (0b00010000010001, 'RVAE1IS'),
    (0b00010000010011, 'RVAAE1IS'),
    (0b00010000010101, 'RVALE1IS'),
    (0b00010000010111, 'RVAALE1IS'),
    (0b00010000101001, 'RVAE1OS'),
    (0b00010000101011, 'RVAAE1OS'),
    (0b00010000101101, 'RVALE1OS'),
    (0b00010000101111, 'RVAALE1OS'),
    (0b00010000110001, 'RVAE1'),
    (0b00010000110011, 'RVAAE1'),
    (0b00010000110101, 'RVALE1'),
    (0b00010000110111, 'RVAALE1'),
    (0b10010000000010, 'RIPAS2E1IS'),
    (0b10010000000110, 'RIPAS2LE1IS'),
    (0b10010000010001, 'RVAE2IS'),
    (0b10010000010101, 'RVALE2IS'),
    (0b10010000100010, 'RIPAS2E1'),
    (0b10010000100011, 'RIPAS2E1OS'),
    (0b10010000100110, 'RIPAS2LE1'),
    (0b10010000100111, 'RIPAS2LE1OS'),
    (0b10010000101001, 'RVAE20S'),
    (0b10010000101101, 'RVALE2OS'),
    (0b10010000110001, 'RVAE2'),
    (0b10010000110101, 'RVALE2'),
    (0b11010000010001, 'RVAE3IS'),
    (0b11010000010101, 'RVALE3IS'),
    (0b11010000101001, 'RVAE3OS'),
    (0b11010000101101, 'RVALE3OS'),
    (0b11010000110001, 'RAVE3'),
    (0b11010000110101, 'RVALE3'),
    # Following require FEAT_XS:
    (0b00010010001000, 'VMALLE1OSNXS'),
    (0b00010010001001, 'VAE1OSNXS'),
    (0b00010010001010, 'ASIDE1OSNXS'),
    (0b00010010001011, 'VAAESNXS'),
    (0b00010010001101, 'VALE1OSNXS'),
    (0b00010010001111, 'VAALE1OSNXS'),
    (0b00010010010001, 'RVAE1ISNXS'),
    (0b00010010010011, 'RVAAE1ISNXS'),
    (0b00010010010101, 'RVALE1ISNXS'),
    (0b00010010010111, 'RVAALE1ISNXS'),
    (0b00010010011000, 'VMALLE1ISNXS'),
    (0b00010010011001, 'VAE1ISNXS'),
    (0b00010010011010, 'ASIDE1ISNXS'),
    (0b00010010011011, 'VAAE1ISNXS'),
    (0b00010010011101, 'VALE1ISNXS'),
    (0b00010010011111, 'VAALE1ISNXS'),
    (0b00010010101001, 'RVAE1OSNXS'),
    (0b00010010101011, 'RVAAE1OSNXS'),
    (0b00010010101101, 'RVALE1OSNXS'),
    (0b00010010101111, 'RVAALE1OSNXS'),
    (0b00010010110001, 'RVAE1NXS'),
    (0b00010010110011, 'RVAAE1NXS'),
    (0b00010010110101, 'RVALE1NXS'),
    (0b00010010110111, 'RVAALE1NXS'),
    (0b00010010111000, 'VMALLE1NXS'),
    (0b00010010111001, 'VAE1NXS'),
    (0b00010010111010, 'ASIDE1NXS'),
    (0b00010010111011, 'VAAE1NXS'),
    (0b00010010111101, 'VALE1NXS'),
    (0b00010010111111, 'VAALE1NXS'),
    (0b10010010000001, 'IPAS2E1ISNXS'),
    (0b10010010000010, 'RIPAS2E1ISNXS'),
    (0b10010010000101, 'IPAS2LE1ISNXS'),
    (0b10010010000110, 'RIPAS2LE1ISNXS'),
    (0b10010010001000, 'ALLE2OSNXS'),
    (0b10010010001001, 'VAE2OSNXS'),
    (0b10010010001100, 'ALLE1OSNXS'),
    (0b10010010001101, 'VALE20SNXS'),
    (0b10010010001110, 'VMALLS12E1OSNXS'),
    (0b10010010010001, 'RVAE2ISNXS'),
    (0b10010010010101, 'RVALE2ISNXS'),
    (0b10010010011000, 'ALLE2ISNXS'),
    (0b10010010011001, 'VAE2ISNXS'),
    (0b10010010011100, 'ALLE1ISNXS'),
    (0b10010010011101, 'VALE2ISNXS'),
    (0b10010010011110, 'VMALLS12E1ISNXS'),
    (0b10010010100000, 'IPAS2E1OSNXS'),
    (0b10010010100001, 'IPAS2E1NXS'),
    (0b10010010100010, 'RIPAS2LE1NXS'),
    (0b10010010100011, 'RIPAS2E1OSNXS'),
    (0b10010010100100, 'IPAS2LE1OSNXS'),
    (0b10010010100101, 'IPAS2LE1NXS'),
    (0b10010010100110, 'RIPAS2LE1NXS'),
    (0b10010010100111, 'RIPAS2LE1OSNXS'),
    (0b10010010101001, 'RVAE2OSNXS'),
    (0b10010010101101, 'RVALE2OSNXS'),
    (0b10010010110001, 'RVAE2NXS'),
    (0b10010010110101, 'RAVLE2NXS'),
    (0b10010010111000, 'ALLE2NXS'),
    (0b10010010111001, 'VAE2NXS'),
    (0b10010010111100, 'ALLE1NXS'),
    (0b10010010111101, 'VALE2NXS'),
    (0b10010010111110, 'VMALLS12E1NXS'),
    (0b11010010001000, 'ALLE3OSNXS'),
    (0b11010010001001, 'VAE3OSNXS'),
    (0b11010010001101, 'VALE3OSNXS'),
    (0b11010010010001, 'RVAE3ISNXS'),
    (0b11010010010101, 'RVALE3ISNXS'),
    (0b11010010011000, 'ALLE3ISNXS'),
    (0b11010010011001, 'VAE3ISNXS'),
    (0b11010010011101, 'VALE3ISNXS'),
    (0b11010010101001, 'RVAE3OSNXS'),
    (0b11010010101101, 'RVALE3OSNXS'),
    (0b11010010110001, 'RVAE3NXS'),
    (0b11010010110101, 'RVALE3NXS'),
    (0b11010010111000, 'ALLE3NXS'),
    (0b11010010111001, 'VAE3NXS'),
    (0b11010010111101, 'VALE3NXS'),
    # Following require FEAT_RME:
    (0b11010000001100, 'PAALLOS'),
    (0b11010000100011, 'RPAOS'),
    (0b11010000100111, 'RPALOS'),
    (0b11010000111100, 'PAALL')
)

sys_alias_op_tables = (
    at_op_table,
    dc_op_table,
    ic_op_table,
    tlbi_op_table 
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
    ('b.cs', INS_BCC),
    ('b.cc', INS_BCC),
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
    'NV^b', #FIXME
)

prefetchTypes = ["pld", "pli", "pst"]   
prefetchTargets = ["l1", "l2", "l3"]
prefetchPolicy = ["keep", "strm"]

def getpstatefieldname(op1, op2, crm):
    '''
    Returns pstatefield names for use with MSR (imm) opers, assumes all exts are implemented
    '''

    encoding = op1 << 3 | op2

    match encoding:
        case 0b000011: return 'uao'
        case 0b000100: return 'pan'
        case 0b000101: return 'spsel'
        case 0b001000: 
            if crm >> 1 == 0:
                return 'allint'
            else: return 'UNDEFINED'
        case 0b011010:
            return 'dit'
        case 0b011011:
            if crm >> 1 == 0b001:
                return 'svcrsm'
            elif crm >> 1 == 0b010:
                return 'svcrza'
            elif crm >> 1 == 0b011:
                return 'svcrsmza'
            else: return 'UNDEFINED'
        case 0b011100: return 'tco'
        case 0b011110: return 'daifset'
        case 0b011111: return 'daifclr'
        case 0b011001: return 'ssbs'
        case _: return 'UNDEFINED' 


# Returns system register name based on 1:o0:op1:CRn:CRm:op2 encoding
def getsysregname(encoding):
    match encoding:
        case 32770: return "osdtrrx_el1"
        case 32772: return "dbgbvr0_el1"
        case 32773: return "dbgbcr0_el1"
        case 32774: return "dbgwvr0_el1"
        case 32775: return "dbgwcr0_el1"
        case 32780: return "dbgbvr1_el1"
        case 32781: return "dbgbcr1_el1"
        case 32782: return "dbgwvr1_el1"
        case 32783: return "dbgwcr1_el1"
        case 32784: return "mdccint_el1"
        case 32786: return "mdscr_el1"
        case 32788: return "dbgbvr2_el1"
        case 32789: return "dbgbcr2_el1"
        case 32790: return "dbgwvr2_el1"
        case 32791: return "dbgwcr2_el1"
        case 32794: return "osdtrtx_el1"
        case 32796: return "dbgbvr3_el1"
        case 32797: return "dbgbcr3_el1"
        case 32798: return "dbgwvr3_el1"
        case 32799: return "dbgwcr3_el1"
        case 32804: return "dbgbvr4_el1"
        case 32805: return "dbgbcr4_el1"
        case 32806: return "dbgwvr4_el1"
        case 32807: return "dbgwcr4_el1"
        case 32812: return "dbgbvr5_el1"
        case 32813: return "dbgbcr5_el1"
        case 32814: return "dbgwvr5_el1"
        case 32815: return "dbgwcr5_el1"
        case 32818: return "oseccr_el1"
        case 32820: return "dbgbvr6_el1"
        case 32821: return "dbgbcr6_el1"
        case 32822: return "dbgwvr6_el1"
        case 32823: return "dbgwcr6_el1"
        case 32828: return "dbgbvr7_el1"
        case 32829: return "dbgbcr7_el1"
        case 32830: return "dbgwvr7_el1"
        case 32831: return "dbgwcr7_el1"
        case 32836: return "dbgbvr8_el1"
        case 32837: return "dbgbcr8_el1"
        case 32838: return "dbgwvr8_el1"
        case 32839: return "dbgwcr8_el1"
        case 32844: return "dbgbvr9_el1"
        case 32845: return "dbgbcr9_el1"
        case 32846: return "dbgwvr9_el1"
        case 32847: return "dbgwcr9_el1"
        case 32852: return "dbgbvr10_el1"
        case 32853: return "dbgbcr10_el1"
        case 32854: return "dbgwvr10_el1"
        case 32855: return "dbgwcr10_el1"
        case 32860: return "dbgbvr11_el1"
        case 32861: return "dbgbcr11_el1"
        case 32862: return "dbgwvr11_el1"
        case 32863: return "dbgwcr11_el1"
        case 32868: return "dbgbvr12_el1"
        case 32869: return "dbgbcr12_el1"
        case 32870: return "dbgwvr12_el1"
        case 32871: return "dbgwcr12_el1"
        case 32876: return "dbgbvr13_el1"
        case 32877: return "dbgbcr13_el1"
        case 32878: return "dbgwvr13_el1"
        case 32879: return "dbgwcr13_el1"
        case 32884: return "dbgbvr14_el1"
        case 32885: return "dbgbcr14_el1"
        case 32886: return "dbgwvr14_el1"
        case 32887: return "dbgwcr14_el1"
        case 32892: return "dbgbvr15_el1"
        case 32893: return "dbgbcr15_el1"
        case 32894: return "dbgwvr15_el1"
        case 32895: return "dbgwcr15_el1"
        case 32900: return "oslar_el1"
        case 32924: return "osdlr_el1"
        case 32932: return "dbgprcr_el1"
        case 33734: return "dbgclaimset_el1"
        case 33742: return "dbgclaimclr_el1"
        case 34817: return "trctraceidr"
        case 34818: return "trcvictlr"
        case 34820: return "trcseqevr0"
        case 34821: return "trccntrldvr0"
        case 34823: return "trcimspec0"
        case 34824: return "trcprgctlr"
        case 34825: return "trcqctlr"
        case 34826: return "trcviiectlr"
        case 34828: return "trcseqevr1"
        case 34829: return "trccntrldvr1"
        case 34831: return "trcimspec1"
        case 34832: return "trcprocselr"
        case 34834: return "trcvissctlr"
        case 34836: return "trcseqevr2"
        case 34837: return "trccntrldvr2"
        case 34839: return "trcimspec2"
        case 34842: return "trcvipcssctlr"
        case 34845: return "trccntrldvr3"
        case 34847: return "trcimspec3"
        case 34848: return "trcconfigr"
        case 34853: return "trccntctlr0"
        case 34855: return "trcimspec4"
        case 34861: return "trccntctlr1"
        case 34863: return "trcimspec5"
        case 34864: return "trcauxctlr"
        case 34868: return "trcseqrstevr"
        case 34869: return "trccntctlr2"
        case 34871: return "trcimspec6"
        case 34876: return "trcseqstr"
        case 34877: return "trccntctlr3"
        case 34879: return "trcimspec7"
        case 34880: return "trceventctl0r"
        case 34882: return "trcvdctlr"
        case 34884: return "trcextinselr"
        case 34885: return "trccntvr0"
        case 34888: return "trceventctl1r"
        case 34890: return "trcvdsacctlr"
        case 34892: return "trcextinselr1"
        case 34893: return "trccntvr1"
        case 34896: return "trcrsr"
        case 34898: return "trcvdarcctlr"
        case 34900: return "trcextinselr2"
        case 34901: return "trccntvr2"
        case 34904: return "trcstallctlr"
        case 34908: return "trcextinselr3"
        case 34909: return "trccntvr3"
        case 34912: return "trctsctlr"
        case 34920: return "trcsyncpr"
        case 34928: return "trcccctlr"
        case 34936: return "trcbbctlr"
        case 34945: return "trcrsctlr16"
        case 34946: return "trcssccr0"
        case 34947: return "trcsspcicr0"
        case 34948: return "trcoslar"
        case 34953: return "trcrsctlr17"
        case 34954: return "trcssccr1"
        case 34955: return "trcsspcicr1"
        case 34960: return "trcrsctlr2"
        case 34961: return "trcrsctlr18"
        case 34962: return "trcssccr2"
        case 34963: return "trcsspcicr2"
        case 34968: return "trcrsctlr3"
        case 34969: return "trcrsctlr19"
        case 34970: return "trcssccr3"
        case 34971: return "trcsspcicr3"
        case 34976: return "trcrsctlr4"
        case 34977: return "trcrsctlr20"
        case 34978: return "trcssccr4"
        case 34979: return "trcsspcicr4"
        case 34980: return "trcpdcr"
        case 34984: return "trcrsctlr5"
        case 34985: return "trcrsctlr21"
        case 34986: return "trcssccr5"
        case 34987: return "trcsspcicr5"
        case 34992: return "trcrsctlr6"
        case 34993: return "trcrsctlr22"
        case 34994: return "trcssccr6"
        case 34995: return "trcsspcicr6"
        case 35000: return "trcrsctlr7"
        case 35001: return "trcrsctlr23"
        case 35002: return "trcssccr7"
        case 35003: return "trcsspcicr7"
        case 35008: return "trcrsctlr8"
        case 35009: return "trcrsctlr24"
        case 35010: return "trcsscsr0"
        case 35016: return "trcrsctlr9"
        case 35017: return "trcrsctlr25"
        case 35018: return "trcsscsr1"
        case 35024: return "trcrsctlr10"
        case 35025: return "trcrsctlr26"
        case 35026: return "trcsscsr2"
        case 35032: return "trcrsctlr11"
        case 35033: return "trcrsctlr27"
        case 35034: return "trcsscsr3"
        case 35040: return "trcrsctlr12"
        case 35041: return "trcrsctlr28"
        case 35042: return "trcsscsr4"
        case 35048: return "trcrsctlr13"
        case 35049: return "trcrsctlr29"
        case 35050: return "trcsscsr5"
        case 35056: return "trcrsctlr14"
        case 35057: return "trcrsctlr30"
        case 35058: return "trcsscsr6"
        case 35064: return "trcrsctlr15"
        case 35065: return "trcrsctlr31"
        case 35066: return "trcsscsr7"
        case 35072: return "trcacvr0"
        case 35073: return "trcacvr8"
        case 35074: return "trcacatr0"
        case 35075: return "trcacatr8"
        case 35076: return "trcdvcvr0"
        case 35077: return "trcdvcvr4"
        case 35078: return "trcdvcmr0"
        case 35079: return "trcdvcmr4"
        case 35088: return "trcacvr1"
        case 35089: return "trcacvr9"
        case 35090: return "trcacatr1"
        case 35091: return "trcacatr9"
        case 35104: return "trcacvr2"
        case 35105: return "trcacvr10"
        case 35106: return "trcacatr2"
        case 35107: return "trcacatr10"
        case 35108: return "trcdvcvr1"
        case 35109: return "trcdvcvr5"
        case 35110: return "trcdvcmr1"
        case 35111: return "trcdvcmr5"
        case 35120: return "trcacvr3"
        case 35121: return "trcacvr11"
        case 35122: return "trcacatr3"
        case 35123: return "trcacatr11"
        case 35136: return "trcacvr4"
        case 35137: return "trcacvr12"
        case 35138: return "trcacatr4"
        case 35139: return "trcacatr12"
        case 35140: return "trcdvcvr2"
        case 35141: return "trcdvcvr6"
        case 35142: return "trcdvcmr2"
        case 35143: return "trcdvcmr6"
        case 35152: return "trcacvr5"
        case 35153: return "trcacvr13"
        case 35154: return "trcacatr5"
        case 35155: return "trcacatr13"
        case 35168: return "trcacvr6"
        case 35169: return "trcacvr14"
        case 35170: return "trcacatr6"
        case 35171: return "trcacatr14"
        case 35172: return "trcdvcvr3"
        case 35173: return "trcdvcvr7"
        case 35174: return "trcdvcmr3"
        case 35175: return "trcdvcmr7"
        case 35184: return "trcacvr7"
        case 35185: return "trcacvr15"
        case 35186: return "trcacatr7"
        case 35187: return "trcacatr15"
        case 35200: return "trccidcvr0"
        case 35201: return "trcvmidcvr0"
        case 35202: return "trccidcctlr0"
        case 35210: return "trccidcctlr1"
        case 35216: return "trccidcvr1"
        case 35217: return "trcvmidcvr1"
        case 35218: return "trcvmidcctlr0"
        case 35226: return "trcvmidcctlr1"
        case 35232: return "trccidcvr2"
        case 35233: return "trcvmidcvr2"
        case 35248: return "trccidcvr3"
        case 35249: return "trcvmidcvr3"
        case 35264: return "trccidcvr4"
        case 35265: return "trcvmidcvr4"
        case 35280: return "trccidcvr5"
        case 35281: return "trcvmidcvr5"
        case 35296: return "trccidcvr6"
        case 35297: return "trcvmidcvr6"
        case 35312: return "trccidcvr7"
        case 35313: return "trcvmidcvr7"
        case 35716: return "trcitctrl"
        case 35782: return "trcclaimset"
        case 35790: return "trcclaimclr"
        case 35814: return "trclar"
        case 36864: return "teecr32_el1"
        case 36992: return "teehbr32_el1"
        case 38944: return "dbgdtr_el0"
        case 38952: return "dbgdtrtx_el0"
        case 41016: return "dbgvcr32_el2"
        case 49280: return "sctlr_el1"
        case 49281: return "actlr_el1"
        case 49282: return "cpacr_el1"
        case 49285: return "rgsr_el1"
        case 49286: return "gcr_el1"
        case 49297: return "trfcr_el1"
        case 49408: return "ttbr0_el1"
        case 49409: return "ttbr1_el1"
        case 49410: return "tcr_el1"
        case 49416: return "apiakeylo_el1"
        case 49417: return "apiakeyhi_el1"
        case 49418: return "apibkeylo_el1"
        case 49419: return "apibkeyhi_el1"
        case 49424: return "apdakeylo_el1"
        case 49425: return "apdakeyhi_el1"
        case 49426: return "apdbkeylo_el1"
        case 49427: return "apdbkeyhi_el1"
        case 49432: return "apgakeylo_el1"
        case 49433: return "apgakeyhi_el1"
        case 49664: return "spsr_el1"
        case 49665: return "elr_el1"
        case 49672: return "sp_el0"
        case 49680: return "spsel"
        case 49682: return "currentel"
        case 49683: return "pan"
        case 49684: return "uao"
        case 49712: return "icc_pmr_el1"
        case 49800: return "afsr0_el1"
        case 49801: return "afsr1_el1"
        case 49808: return "esr_el1"
        case 49817: return "errselr_el1"
        case 49825: return "erxctlr_el1"
        case 49826: return "erxstatus_el1"
        case 49827: return "erxaddr_el1"
        case 49829: return "erxpfgctl_el1"
        case 49830: return "erxpfgcdn_el1"
        case 49832: return "erxmisc0_el1"
        case 49833: return "erxmisc1_el1"
        case 49834: return "erxmisc2_el1"
        case 49835: return "erxmisc3_el1"
        case 49839: return "erxts_el1"
        case 49840: return "tfsr_el1"
        case 49841: return "tfsre0_el1"
        case 49920: return "far_el1"
        case 50080: return "par_el1"
        case 50376: return "pmscr_el1"
        case 50378: return "pmsicr_el1"
        case 50379: return "pmsirr_el1"
        case 50380: return "pmsfcr_el1"
        case 50381: return "pmsevfr_el1"
        case 50382: return "pmslatfr_el1"
        case 50383: return "pmsidr_el1"
        case 50384: return "pmblimitr_el1"
        case 50385: return "pmbptr_el1"
        case 50387: return "pmbsr_el1"
        case 50391: return "pmbidr_el1"
        case 50392: return "trblimitr_el1"
        case 50393: return "trbptr_el1"
        case 50394: return "trbbaser_el1"
        case 50395: return "trbsr_el1"
        case 50396: return "trbmar_el1"
        case 50398: return "trbtrg_el1"
        case 50417: return "pmintenset_el1"
        case 50418: return "pmintenclr_el1"
        case 50422: return "pmmir_el1"
        case 50448: return "mair_el1"
        case 50456: return "amair_el1"
        case 50464: return "lorsa_el1"
        case 50465: return "lorea_el1"
        case 50466: return "lorn_el1"
        case 50467: return "lorc_el1"
        case 50472: return "mpam1_el1"
        case 50473: return "mpam0_el1"
        case 50688: return "vbar_el1"
        case 50690: return "rmr_el1"
        case 50697: return "disr_el1"
        case 50753: return "icc_eoir0_el1"
        case 50755: return "icc_bpr0_el1"
        case 50756: return "icc_ap0r0_el1"
        case 50757: return "icc_ap0r1_el1"
        case 50758: return "icc_ap0r2_el1"
        case 50759: return "icc_ap0r3_el1"
        case 50760: return "icc_ap1r0_el1"
        case 50761: return "icc_ap1r1_el1"
        case 50762: return "icc_ap1r2_el1"
        case 50763: return "icc_ap1r3_el1"
        case 50777: return "icc_dir_el1"
        case 50781: return "icc_sgi1r_el1"
        case 50782: return "icc_asgi1r_el1"
        case 50783: return "icc_sgi0r_el1"
        case 50785: return "icc_eoir1_el1"
        case 50787: return "icc_bpr1_el1"
        case 50788: return "icc_ctlr_el1"
        case 50789: return "icc_sre_el1"
        case 50790: return "icc_igrpen0_el1"
        case 50791: return "icc_igrpen1_el1"
        case 50792: return "icc_seien_el1"
        case 50817: return "contextidr_el1"
        case 50820: return "tpidr_el1"
        case 50823: return "scxtnum_el1"
        case 50952: return "cntkctl_el1"
        case 53248: return "csselr_el1"
        case 55824: return "nzcv"
        case 55825: return "daifset"
        case 55829: return "dit"
        case 55830: return "ssbs"
        case 55831: return "tco"
        case 55840: return "fpcr"
        case 55841: return "fpsr"
        case 55848: return "dspsr_el0"
        case 55849: return "dlr_el0"
        case 56544: return "pmcr_el0"
        case 56545: return "pmcntenset_el0"
        case 56546: return "pmcntenclr_el0"
        case 56547: return "pmovsclr_el0"
        case 56548: return "pmswinc_el0"
        case 56549: return "pmselr_el0"
        case 56552: return "pmccntr_el0"
        case 56553: return "pmxevtyper_el0"
        case 56554: return "pmxevcntr_el0"
        case 56557: return "daifclr"
        case 56560: return "pmuserenr_el0"
        case 56563: return "pmovsset_el0"
        case 56962: return "tpidr_el0"
        case 56963: return "tpidrro_el0"
        case 56967: return "scxtnum_el0"
        case 56976: return "amcr_el0"
        case 56979: return "amuserenr_el0"
        case 56980: return "amcntenclr0_el0"
        case 56981: return "amcntenset0_el0"
        case 56984: return "amcntenclr1_el0"
        case 56985: return "amcntenset1_el0"
        case 56992: return "amevcntr00_el0"
        case 56993: return "amevcntr01_el0"
        case 56994: return "amevcntr02_el0"
        case 56995: return "amevcntr03_el0"
        case 57056: return "amevcntr10_el0"
        case 57057: return "amevcntr11_el0"
        case 57058: return "amevcntr12_el0"
        case 57059: return "amevcntr13_el0"
        case 57060: return "amevcntr14_el0"
        case 57061: return "amevcntr15_el0"
        case 57062: return "amevcntr16_el0"
        case 57063: return "amevcntr17_el0"
        case 57064: return "amevcntr18_el0"
        case 57065: return "amevcntr19_el0"
        case 57066: return "amevcntr110_el0"
        case 57067: return "amevcntr111_el0"
        case 57068: return "amevcntr112_el0"
        case 57069: return "amevcntr113_el0"
        case 57070: return "amevcntr114_el0"
        case 57071: return "amevcntr115_el0"
        case 57072: return "amevtyper10_el0"
        case 57073: return "amevtyper11_el0"
        case 57074: return "amevtyper12_el0"
        case 57075: return "amevtyper13_el0"
        case 57076: return "amevtyper14_el0"
        case 57077: return "amevtyper15_el0"
        case 57078: return "amevtyper16_el0"
        case 57079: return "amevtyper17_el0"
        case 57080: return "amevtyper18_el0"
        case 57081: return "amevtyper19_el0"
        case 57082: return "amevtyper110_el0"
        case 57083: return "amevtyper111_el0"
        case 57084: return "amevtyper112_el0"
        case 57085: return "amevtyper113_el0"
        case 57086: return "amevtyper114_el0"
        case 57087: return "amevtyper115_el0"
        case 57088: return "cntfrq_el0"
        case 57104: return "cntp_tval_el0"
        case 57105: return "cntp_ctl_el0"
        case 57106: return "cntp_cval_el0"
        case 57112: return "cntv_tval_el0"
        case 57113: return "cntv_ctl_el0"
        case 57114: return "cntv_cval_el0"
        case 57152: return "pmevcntr0_el0"
        case 57153: return "pmevcntr1_el0"
        case 57154: return "pmevcntr2_el0"
        case 57155: return "pmevcntr3_el0"
        case 57156: return "pmevcntr4_el0"
        case 57157: return "pmevcntr5_el0"
        case 57158: return "pmevcntr6_el0"
        case 57159: return "pmevcntr7_el0"
        case 57160: return "pmevcntr8_el0"
        case 57161: return "pmevcntr9_el0"
        case 57162: return "pmevcntr10_el0"
        case 57163: return "pmevcntr11_el0"
        case 57164: return "pmevcntr12_el0"
        case 57165: return "pmevcntr13_el0"
        case 57166: return "pmevcntr14_el0"
        case 57167: return "pmevcntr15_el0"
        case 57168: return "pmevcntr16_el0"
        case 57169: return "pmevcntr17_el0"
        case 57170: return "pmevcntr18_el0"
        case 57171: return "pmevcntr19_el0"
        case 57172: return "pmevcntr20_el0"
        case 57173: return "pmevcntr21_el0"
        case 57174: return "pmevcntr22_el0"
        case 57175: return "pmevcntr23_el0"
        case 57176: return "pmevcntr24_el0"
        case 57177: return "pmevcntr25_el0"
        case 57178: return "pmevcntr26_el0"
        case 57179: return "pmevcntr27_el0"
        case 57180: return "pmevcntr28_el0"
        case 57181: return "pmevcntr29_el0"
        case 57182: return "pmevcntr30_el0"
        case 57184: return "pmevtyper0_el0"
        case 57185: return "pmevtyper1_el0"
        case 57186: return "pmevtyper2_el0"
        case 57187: return "pmevtyper3_el0"
        case 57188: return "pmevtyper4_el0"
        case 57189: return "pmevtyper5_el0"
        case 57190: return "pmevtyper6_el0"
        case 57191: return "pmevtyper7_el0"
        case 57192: return "pmevtyper8_el0"
        case 57193: return "pmevtyper9_el0"
        case 57194: return "pmevtyper10_el0"
        case 57195: return "pmevtyper11_el0"
        case 57196: return "pmevtyper12_el0"
        case 57197: return "pmevtyper13_el0"
        case 57198: return "pmevtyper14_el0"
        case 57199: return "pmevtyper15_el0"
        case 57200: return "pmevtyper16_el0"
        case 57201: return "pmevtyper17_el0"
        case 57202: return "pmevtyper18_el0"
        case 57203: return "pmevtyper19_el0"
        case 57204: return "pmevtyper20_el0"
        case 57205: return "pmevtyper21_el0"
        case 57206: return "pmevtyper22_el0"
        case 57207: return "pmevtyper23_el0"
        case 57208: return "pmevtyper24_el0"
        case 57209: return "pmevtyper25_el0"
        case 57210: return "pmevtyper26_el0"
        case 57211: return "pmevtyper27_el0"
        case 57212: return "pmevtyper28_el0"
        case 57213: return "pmevtyper29_el0"
        case 57214: return "pmevtyper30_el0"
        case 57215: return "pmccfiltr_el0"
        case 57344: return "vpidr_el2"
        case 57349: return "vmpidr_el2"
        case 57472: return "sctlr_el2"
        case 57473: return "actlr_el2"
        case 57480: return "hcr_el2"
        case 57481: return "mdcr_el2"
        case 57482: return "cptr_el2"
        case 57483: return "hstr_el2"
        case 57487: return "hacr_el2"
        case 57489: return "trfcr_el2"
        case 57497: return "sder32_el2"
        case 57600: return "ttbr0_el2"
        case 57601: return "ttbr1_el2"
        case 57602: return "tcr_el2"
        case 57608: return "vttbr_el2"
        case 57610: return "vtcr_el2"
        case 57616: return "vncr_el2"
        case 57648: return "vsttbr_el2"
        case 57650: return "vstcr_el2"
        case 57728: return "dacr32_el2"
        case 57856: return "spsr_el2"
        case 57857: return "elr_el2"
        case 57864: return "sp_el1"
        case 57880: return "spsr_irq"
        case 57881: return "spsr_abt"
        case 57882: return "spsr_und"
        case 57883: return "spsr_fiq"
        case 57985: return "ifsr32_el2"
        case 57992: return "afsr0_el2"
        case 57993: return "afsr1_el2"
        case 58000: return "esr_el2"
        case 58003: return "vsesr_el2"
        case 58008: return "fpexc32_el2"
        case 58032: return "tfsr_el2"
        case 58112: return "far_el2"
        case 58116: return "hpfar_el2"
        case 58568: return "pmscr_el2"
        case 58640: return "mair_el2"
        case 58648: return "amair_el2"
        case 58656: return "mpamhcr_el2"
        case 58657: return "mpamvpmv_el2"
        case 58664: return "mpam2_el2"
        case 58672: return "mpamvpm0_el2"
        case 58673: return "mpamvpm1_el2"
        case 58674: return "mpamvpm2_el2"
        case 58675: return "mpamvpm3_el2"
        case 58676: return "mpamvpm4_el2"
        case 58677: return "mpamvpm5_el2"
        case 58678: return "mpamvpm6_el2"
        case 58679: return "mpamvpm7_el2"
        case 58880: return "vbar_el2"
        case 58882: return "rmr_el2"
        case 58889: return "vdisr_el2"
        case 58944: return "ich_ap0r0_el2"
        case 58945: return "ich_ap0r1_el2"
        case 58946: return "ich_ap0r2_el2"
        case 58947: return "ich_ap0r3_el2"
        case 58952: return "ich_ap1r0_el2"
        case 58953: return "ich_ap1r1_el2"
        case 58954: return "ich_ap1r2_el2"
        case 58955: return "ich_ap1r3_el2"
        case 58956: return "ich_vseir_el2"
        case 58957: return "icc_sre_el2"
        case 58968: return "ich_hcr_el2"
        case 58970: return "ich_misr_el2"
        case 58975: return "ich_vmcr_el2"
        case 58976: return "ich_lr0_el2"
        case 58977: return "ich_lr1_el2"
        case 58978: return "ich_lr2_el2"
        case 58979: return "ich_lr3_el2"
        case 58980: return "ich_lr4_el2"
        case 58981: return "ich_lr5_el2"
        case 58982: return "ich_lr6_el2"
        case 58983: return "ich_lr7_el2"
        case 58984: return "ich_lr8_el2"
        case 58985: return "ich_lr9_el2"
        case 58986: return "ich_lr10_el2"
        case 58987: return "ich_lr11_el2"
        case 58988: return "ich_lr12_el2"
        case 58989: return "ich_lr13_el2"
        case 58990: return "ich_lr14_el2"
        case 58991: return "ich_lr15_el2"
        case 59009: return "contextidr_el2"
        case 59010: return "tpidr_el2"
        case 59015: return "scxtnum_el2"
        case 59139: return "cntvoff_el2"
        case 59144: return "cnthctl_el2"
        case 59152: return "cnthp_tval_el2"
        case 59153: return "cnthp_ctl_el2"
        case 59154: return "cnthp_cval_el2"
        case 59160: return "cnthv_tval_el2"
        case 59161: return "cnthv_ctl_el2"
        case 59162: return "cnthv_cval_el2"
        case 59168: return "cnthvs_tval_el2"
        case 59169: return "cnthvs_ctl_el2"
        case 59170: return "cnthvs_cval_el2"
        case 59176: return "cnthps_tval_el2"
        case 59177: return "cnthps_ctl_el2"
        case 59178: return "cnthps_cval_el2"
        case 59520: return "sctlr_el12"
        case 59522: return "cpacr_el12"
        case 59537: return "trfcr_el12"
        case 59648: return "ttbr0_el12"
        case 59649: return "ttbr1_el12"
        case 59650: return "tcr_el12"
        case 59904: return "spsr_el12"
        case 59905: return "elr_el12"
        case 60040: return "afsr0_el12"
        case 60041: return "afsr1_el12"
        case 60048: return "esr_el12"
        case 60080: return "tfsr_el12"
        case 60160: return "far_el12"
        case 60616: return "pmscr_el12"
        case 60688: return "mair_el12"
        case 60696: return "amair_el12"
        case 60712: return "mpam1_el12"
        case 60928: return "vbar_el12"
        case 61057: return "contextidr_el12"
        case 61063: return "scxtnum_el12"
        case 61192: return "cntkctl_el12"
        case 61200: return "cntp_tval_el02"
        case 61201: return "cntp_ctl_el02"
        case 61202: return "cntp_cval_el02"
        case 61208: return "cntv_tval_el02"
        case 61209: return "cntv_ctl_el02"
        case 61210: return "cntv_cval_el02"
        case 61568: return "sctlr_el3"
        case 61569: return "actlr_el3"
        case 61576: return "scr_el3"
        case 61577: return "sder32_el3"
        case 61578: return "cptr_el3"
        case 61593: return "mdcr_el3"
        case 61696: return "ttbr0_el3"
        case 61698: return "tcr_el3"
        case 61952: return "spsr_el3"
        case 61953: return "elr_el3"
        case 61960: return "sp_el2"
        case 62088: return "afsr0_el3"
        case 62089: return "afsr1_el3"
        case 62096: return "esr_el3"
        case 62128: return "tfsr_el3"
        case 62208: return "far_el3"
        case 62736: return "mair_el3"
        case 62744: return "amair_el3"
        case 62760: return "mpam3_el3"
        case 62976: return "vbar_el3"
        case 62978: return "rmr_el3"
        case 63076: return "icc_ctlr_el3"
        case 63077: return "icc_sre_el3"
        case 63079: return "icc_igrpen1_el3"
        case 63106: return "tpidr_el3"
        case 63111: return "scxtnum_el3"
        case 65296: return "cntps_tval_el1"
        case 65297: return "cntps_ctl_el1"
        case 65298: return "cntps_cval_el1"
        case 65299: return "spsel"
        case _: return 'invalid'