MODE_ARM        = 0
MODE_THUMB      = 1
MODE_JAZELLE    = 2
MODE_THUMBEE    = 3


# Support for different ARM Instruction set versions

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

# Todo - For easy instruction filtering add more like:
REV_ALL_TO_ARMv6 = REV_ALL_ARMv4 | REV_ALL_ARMv5 | REV_ALL_ARMv6
REV_ALL_FROM_ARMv6 = REV_ALL_ARMv6 | REV_ALL_ARMv7 | REV_ALL_ARMv8
# Note: since arm must be backwards compatible any depreciated commands
# Would be noted but not removed with the REV_ALL_TO_* if this is even used.
# These are put here for suggestion and comment for now

REV_ALL_ARM = (REV_ALL_ARMv4 | REV_ALL_ARMv5 | REV_ALL_ARMv6 | REV_ALL_ARMv7 | REV_ALL_ARMv8)

# Will be set below, THUMB16 up through v6 except v6T2, THUMB2 from v6T2 up, THUMBEE from v7 up.
REV_THUMB16 = REV_THUMB2 = REV_THUMBEE = 0

ARM_MASK_TO_NAME = {
    0x1: 'REV_ARMv4',
    0x2: 'REV_ARMv4T',
    0x4: 'REV_ARMv5',
    0x8: 'REV_ARMv5T',
    0x10: 'REV_ARMv5E',
    0x20: 'REV_ARMv5J',
    0x40: 'REV_ARMv5TE',
    0x80: 'REV_ARMv6',
    0x100: 'REV_ARMv6',
    0x200: 'REV_ARMv6T2',
    0x400: 'REV_ARMv7A',
    0x800: 'REV_ARMv7R',
    0x1000: 'REV_ARMv7M',
    0x2000: 'REV_ARMv7EM',
    0x4000: 'REV_ARMv8A',
    0x8000: 'REV_ARMv8R',
    0x10000: 'REV_ARMv8M',
}

ARCH_REVS = {}
# Iterate through all REV_ARM values and setup related combo values 
# for name, val in globals().items():
for mask, name in ARM_MASK_TO_NAME.items():
    shortName = name[4:]
    # add to lookup dictionary
    ARCH_REVS[shortName] = mask
    # setup thumb versions to Architecture versions
    if (int(shortName[4]) > 6 or shortName == 'ARMv6T2'):
        REV_THUMB2 = REV_THUMB2 | mask
        if shortName[4] != '6':
            REV_THUMBEE = REV_THUMBEE | mask
    else:
        REV_THUMB16 = REV_THUMB16 | mask
# Added thumbs to dictionary
ARCH_REVS['thumb16'] = REV_THUMB16
ARCH_REVS['thumb'] = REV_THUMB2
ARCH_REVS['thumbee'] = REV_THUMBEE
ARCH_REVSLEN = len(ARCH_REVS)

# IFLAGS - keep bottom 8-bits for cross-platform flags like envi.IF_NOFALL and envi.IF_BRFALL
IF_PSR_S     = 1 << 32    # This DP instruciton can update CPSR  (as in, add vs. adds)
IF_B         = 1 << 33    # Byte
IF_H         = 1 << 35    # HalfWord
IF_S         = 1 << 36    # Signed    #(not to be confused with IF_PSR_S which is the "update status" flag.
IF_D         = 1 << 37    # Dword
IF_L         = 1 << 38    # Long-store (eg. Dblword Precision) for STC
IF_T         = 1 << 39    # Translate for strbt - denotes ldr/str command runs in user mode
IF_W         = 1 << 40    # Write Back for STM/LDM (!)
IF_UM        = 1 << 41    # User Mode Registers for STM/LDM (^) (obviously no R15)
IF_PSR_S_SIL = 1 << 42    # Flag for Silent S. Related to IF_PSR_S and will prevent S from being rendered. TST, TEQ, CMN, CMP commands.
IF_IE        = 1 << 43    # Interrupt Enable flag (used for CPS instruction)
IF_ID        = 1 << 44    # Interrupt Disable flag (used for CPS instruction)

IF_THUMB32   = 1 << 50    # thumb32
IF_ADV_SIMD  = 1 << 51    # Advanced SIMD instructions...  it matters
IF_SYS_MODE  = 1 << 52

IF_DAIB_SHFT = 56         # shift-bits to get DAIB bits down to 0.  this chops off the "is DAIB present" bit that the following store.
IF_DAIB_MASK = 7 << (IF_DAIB_SHFT - 1)
IF_DA        = 1 << (IF_DAIB_SHFT - 1)  # Decrement After
IF_IA        = 3 << (IF_DAIB_SHFT - 1)  # Increment After
IF_DB        = 5 << (IF_DAIB_SHFT - 1)  # Decrement Before
IF_IB        = 7 << (IF_DAIB_SHFT - 1)  # Increment Before
IF_DAIB_B    = 5 << (IF_DAIB_SHFT - 1)  # Before mask
IF_DAIB_I    = 3 << (IF_DAIB_SHFT - 1)  # Before mask


# NOTE: unlike IF_*, IFS_* are *NOT* flags.  they are indices into the IFS list.
# thus, opcode.simdflags is *not* flags, but one index.  only one can be used at a time.
IFS = [
    None,
    '.f32.s32',
    '.f64.s32',
    '.f32.u32',
    '.f64.u32',
    '.f32.64',
    '.f64.32',
    '.f32.16',
    '.f16.32',
    '.f64.f32',
    '.s32.f64',
    '.s32.f32',
    '.u32.f64',
    '.u32.f32',
    '.s8',
    '.s16',
    '.s32',
    '.s64',
    '.u8',
    '.u16',
    '.u32',
    '.u64',
    '.i8',
    '.i16',
    '.i32',
    '.i64',
    '.8',
    '.16',
    '.32',
    '.64',
    '.f8',
    '.f16',
    '.f32',
    '.f64',
    '.p8',
    '.p16',
    '.p32',
    '.p64',
    '.f32.s16',
    '.f32.u16',
    '.f64.s16',
    '.f64.u16',
    '.s16.f32',
    '.u16.f32',
    '.s16.f64',
    '.u16.f64',
    '.f32.f64',
    '.f64.f32',
    '.f32.f16',
    '.f16.f32',
    ]

for ifx in range(1, len(IFS)):
    ifs = IFS[ifx]
    gblname = "IFS" + ifs.upper().replace('.','_')
    globals()[gblname] = ifx


OF_W         = 1<<8     # Write back to 
OF_UM        = 1<<9     # Usermode, or if r15 included set current SPSR -> CPSR


OSZFMT_BYTE = "B"
OSZFMT_HWORD = "<H"  # Introduced in ARMv4
OSZFMT_WORD = "<I"
OSZ_BYTE = 1
OSZ_HWORD = 2
OSZ_WORD = 4

fmts = [None, OSZ_BYTE, OSZ_HWORD, None, OSZ_WORD]

COND_EQ     = 0x0        # z==1  (equal)
COND_NE     = 0x1        # z==0  (not equal)
COND_CS     = 0x2        # c==1  (carry set/unsigned higher or same)
COND_CC     = 0x3        # c==0  (carry clear/unsigned lower)
COND_MI     = 0x4        # n==1  (minus/negative)
COND_PL     = 0x5        # n==0  (plus/positive or zero)
COND_VS     = 0x6        # v==1  (overflow)
COND_VC     = 0x7        # v==0  (no overflow)
COND_HI     = 0x8        # c==1 and z==0  (unsigned higher)
COND_LS     = 0x9        # c==0  or z==1  (unsigned lower or same)
COND_GE     = 0xA        # n==v  (signed greater than or equal)  (n==1 and v==1) or (n==0 and v==0)
COND_LT     = 0xB        # n!=v  (signed less than)  (n==1 and v==0) or (n==0 and v==1)
COND_GT     = 0xC        # z==0 and n==v (signed greater than)
COND_LE     = 0xD        # z==1 and n!=v (signed less than or equal)
COND_AL     = 0xE        # always
COND_EXTENDED = 0xF        # special case - see conditional 0b1111

cond_codes = {
    COND_EQ: "eq", # Equal Z set 
    COND_NE: "ne", # Not equal Z clear 
    COND_CS: "cs", #/HS Carry set/unsigned higher or same C set 
    COND_CC: "cc", #/LO Carry clear/unsigned lower C clear 
    COND_MI: "mi", # Minus/negative N set 
    COND_PL: "pl", # Plus/positive or zero N clear 
    COND_VS: "vs", # Overflow V set 
    COND_VC: "vc", # No overflow V clear 
    COND_HI: "hi", # Unsigned higher C set and Z clear 
    COND_LS: "ls", # Unsigned lower or same C clear or Z set 
    COND_GE: "ge", # Signed greater than or equal N set and V set, or N clear and V clear (N == V) 
    COND_LT: "lt", # Signed less than N set and V clear, or N clear and V set (N!= V) 
    COND_GT: "gt", # Signed greater than Z clear, and either N set and V set, or N clear and V clear (Z == 0,N == V) 
    COND_LE: "le", # Signed less than or equal Z set, or N set and V clear, or N clear and V set (Z == 1 or N!= V) 
    COND_AL: "", # Always (unconditional) - could be "al" but "" seems better...
    COND_EXTENDED: "", # See extended opcode table
}

cond_map = {
    COND_EQ: 0,      # Equal Z set 
    COND_NE: 1, # Not equal Z clear 
    COND_CS: 2, #/HS Carry set/unsigned higher or same C set 
    COND_CC: 3, #/LO Carry clear/unsigned lower C clear 
    COND_MI: 4, # Minus/negative N set 
    COND_PL: 5, # Plus/positive or zero N clear 
    COND_VS: 6, # Overflow V set 
    COND_VC: 7, # No overflow V clear 
    COND_HI: 8, # Unsigned higher C set and Z clear 
    COND_LS: 9, # Unsigned lower or same C clear or Z set 
    COND_GE: 10, # Signed greater than or equal N set and V set, or N clear and V clear (N == V) 
    COND_LT: 11, # Signed less than N set and V clear, or N clear and V set (N!= V) 
    COND_GT: 12, # Signed greater than Z clear, and either N set and V set, or N clear and V clear (Z == 0,N == V) 
    COND_LE: 13, # Signed less than or equal Z set, or N set and V clear, or N clear and V set (Z == 1 or N!= V) 
    COND_AL: "", # Always (unconditional) - could be "al" but "" seems better...
    COND_EXTENDED: "2", # See extended opcode table
}

PUxWL_SUB   = 0x00
PUxWL_ADD   = 0x08

PUxWL_UNIdx     = 0x00
PUxWL_POST_Idx  = 0x02
PUxWL_OFFSET    = 0x10
PUxWL_PRE_Idx   = 0x12

PUxWL_DFLT  = PUxWL_OFFSET | PUxWL_ADD

PM_usr = 0b10000
PM_fiq = 0b10001
PM_irq = 0b10010
PM_svc = 0b10011
PM_mon = 0b10110
PM_abt = 0b10111
PM_hyp = 0b11010
PM_und = 0b11011
PM_sys = 0b11111

REGS_PER_MODE = 18

# reg stuff stolen from regs.py to support proc_modes
# these are in context of reg_table, not reg_data.  
#  ie. these are indexes into the lookup table.
REG_OFFSET_USR = REGS_PER_MODE * (PM_usr&0xf)
REG_OFFSET_FIQ = REGS_PER_MODE * (PM_fiq&0xf)
REG_OFFSET_IRQ = REGS_PER_MODE * (PM_irq&0xf)
REG_OFFSET_SVC = REGS_PER_MODE * (PM_svc&0xf)
REG_OFFSET_MON = REGS_PER_MODE * (PM_mon&0xf)
REG_OFFSET_ABT = REGS_PER_MODE * (PM_abt&0xf)
REG_OFFSET_HYP = REGS_PER_MODE * (PM_hyp&0xf)
REG_OFFSET_UND = REGS_PER_MODE * (PM_und&0xf)
REG_OFFSET_SYS = REGS_PER_MODE * (PM_sys&0xf)
#REG_OFFSET_CPSR = REGS_PER_MODE * 16
REG_OFFSET_CPSR = 16                    # CPSR is available in every mode, and PM_usr and PM_sys don't have an SPSR.

REG_SPSR_usr = REG_OFFSET_USR + REGS_PER_MODE
REG_SPSR_fiq = REG_OFFSET_FIQ + REGS_PER_MODE
REG_SPSR_irq = REG_OFFSET_IRQ + REGS_PER_MODE
REG_SPSR_svc = REG_OFFSET_SVC + REGS_PER_MODE
REG_SPSR_mon = REG_OFFSET_MON + REGS_PER_MODE
REG_SPSR_abt = REG_OFFSET_ABT + REGS_PER_MODE
REG_SPSR_hyp = REG_OFFSET_HYP + REGS_PER_MODE
REG_SPSR_und = REG_OFFSET_UND + REGS_PER_MODE
REG_SPSR_sys = REG_OFFSET_SYS + REGS_PER_MODE

REG_PC = 0xf
REG_LR = 0xe
REG_SP = 0xd
REG_BP = None
REG_CPSR = REG_OFFSET_CPSR
REG_FLAGS = REG_OFFSET_CPSR    #same location, backward-compat name
REG_EXT_S_FLAG = 0x200000
REG_EXT_D_FLAG = 0x400000

VFP_QWORD_REG_COUNT = 16    # VFPv4-D32

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

PM_LNAME =  0
PM_SNAME =  1
PM_DESC =   2
PM_REGOFF = 3
PM_REGCNT = 4
PM_PSROFF   = 5
PM_PRIVLVL  = 6

PSR_APSR    = 2
PSR_SPSR    = 1
PSR_CPSR    = 0

INST_ENC_DP_IMM = 0 # Data Processing Immediate Shift
INST_ENC_MISC   = 1 # Misc Instructions

# Instruction encodings in arm v5
iencs = (\
    'IENC_DP_IMM_SHIFT',    #   Data processing immediate shift
    'IENC_MISC',            #   Miscellaneous instructions
    'IENC_MISC1',           #   Miscellaneous instructions again
    'IENC_DP_REG_SHIFT',    #   Data processing register shift
    'IENC_MULT',            #   Multiplies & Extra load/stores
    'IENC_UNDEF',           #   Undefined instruction
    'IENC_MOV_IMM_STAT',    #   Move immediate to status register
    'IENC_DP_IMM',          #   Data processing immediate
    'IENC_LOAD_IMM_OFF',    #   Load/Store immediate offset
    'IENC_LOAD_REG_OFF',    #   Load/Store register offset
    'IENC_ARCH_UNDEF',      #   Architecturally undefined
    'IENC_MEDIA',           #   Media instructions
    'IENC_LOAD_MULT',       #   Load/Store Multiple
    'IENC_BRANCH',          #   Branch
    'IENC_COPROC_RREG_XFER',#   mrrc/mcrr
    'IENC_COPROC_LOAD',     #   Coprocessor load/store and double reg xfers
    'IENC_COPROC_DP',       #   Coprocessor data processing
    'IENC_COPROC_REG_XFER', #   Coprocessor register transfers
    'IENC_COPROC_SIMD',     #   Coprocessor SIMD
    'IENC_MCR',             #   Move to Corprocessor from ARM Regs and vice versa
    'IENC_SWINT',           #   Sofware interrupts
    'IENC_UNCOND',          #   unconditional wacko instructions
    'IENC_EXTRA_LOAD',      #   extra load/store (swp)
    'IENC_DP_MOVW',         #   move wide
    'IENC_DP_MOVT',         #   move top
    'IENC_DP_MSR_IMM',      #    
    'IENC_LOAD_STORE_WORD_UBYTE',   #
    'IENC_FP_DP',           #
    'IENC_ADVSIMD',         #   
    'IENC_64_EXT_XFERS',    #   
    'IENC_VSTM',            #
    'IENC_VSTR',            #
    'IENC_VPUSH',           #
    'IENC_VLDM',            #
    'IENC_VLDR',            #
    'IENC_VPOP',            #
    'IENC_VMSR',            #
    'IENC_VDUP',            #
    'IENC_VMOV_DOUBLE',     #
    'IENC_VMOV_SINGLE',     #
    'IENC_VMOV_2SINGLE',    #
    'IENC_VMOV_SCALAR',     #
)

IENC_MAX        = len(iencs)
for ieidx, ienc in enumerate(iencs):
    globals()[ienc] = ieidx

# The supported types of operand shifts (by the 2 bit field)
S_LSL = 0
S_LSR = 1
S_ASR = 2
S_ROR = 3
S_RRX = 4 # FIXME HACK XXX add this

shift_names = ("lsl", "lsr", "asr", "ror", "rrx")

SOT_REG = 0
SOT_IMM = 1
#ia was removed as it is not UAL
daib = ("da", "", "db", "ib")

instrnames = [
        'AND',
        'EOR',
        'SUB',
        'RSB',
        'ADD',
        'ADC',
        'SBC',
        'RSC',
        'TST',
        'TEQ',
        'CMP',
        'CMN',
        'ORR',
        'MOV',
        'BIC',
        'MVN',
        'ORN',
        'ADR',
        'B',
        'BL',
        'BCC',
        'BX',
        'BXJ',
        'BLX',
        'POP',
        'PUSH',
        'DBG',
        'MOVT',
        'MOVW',
        'LDR',
        'LDRH',
        'LDRB',
        'LDRD',
        'LDREX',
        'LDRSB',
        'LDRSH',
        'LDREX',
        'LDM',
        'STR',
        'STREX',
        'STRH',
        'STRB',
        'STRD',
        'STM',
        'STC',
        'STC2',
        'LDC',
        'LDC2',
        'VHADD',
        'VQADD',
        'VRHADD',
        'VAND',
        'VBIC',
        'VORR',
        'VORN',
        'VEOR',
        'VBIF',
        'VBIT',
        'VBSL',
        'VHSUB',
        'VQSUB',
        'VCGT',
        'VCGE',
        'VCEQ',
        'VSHL',
        'VQSHL',
        'VRSHL',
        'VQRSHL',
        'VMAX',
        'VMIN',
        'VABD',
        'VABA',
        'VADD',
        'VSUB',
        'VTST',
        'VMLA',
        'VMLS',
        'VMUL',
        'VPMAX',
        'VPMIN',
        'VQMULH',
        'VQDMULH',
        'VQRDMULH',
        'VPADD',
        'VPSUB',
        'VFMA',
        'VFMS',
        'VACGE',
        'VACGT',
        'VRECPS',
        'VRSQRTS',
        'VMOV',
        'VMVN',
        'VSHR',
        'VSRA',
        'VRSHR',
        'VRSRA',
        'VSLI',
        'VSRI',
        'VQSHLU',
        'VSHRN',
        'VRSHRN',
        'VQSHRN',
        'VQSHRUN',
        'VQRSHRN',
        'VQRSHRUN',
        'VSHLL',
        'VCVT',
        'MUL',
        'SMUL',
        'MUL',  
        'MLA',  
        'UMAAL',
        'UMULL',
        'UMLAL',
        'SMULL',
        'SMLAL',
        'SMLABB', 
        'SMLATB', 
        'SMLABT', 
        'SMLATT', 
        'SMULWB', 
        'SMULWT', 
        'SMLAWB', 
        'SMLAWT', 
        'SMLALBB',
        'SMLALTB',
        'SMLALBT',
        'SMLALTT',
        'SMULBB', 
        'SMULTB', 
        'SMULBT', 
        'SMULTT', 
        'SMUAD', 
        'SMUADX', 
        'SMUSD', 
        'SMUSDX', 
        'SMLAD', 
        'SMLADX', 
        'SMLSD', 
        'SMLSDX', 
        'SMLALD', 
        'SMLALDX',
        'SMLSLD', 
        'SMLSLDX',
        'SMMLA', 
        'SMMLAR', 
        'SMMLS', 
        'SMMLSR', 
        'UADD16',
        'UADD8',
        'USUB16',
        'USUB8',
        'UASX',
        'USAX',
        'NOP',
        'YIELD',
        'WFE',
        'WFI',
        'WFR',
        'SEV',
        'CPS',
        'CBZ',
        'CBNZ',
        'LEAVEX',
        'ENTERX',
        'TBB',
        'TBH',
        'ORN',
        'PKH',
        'LSL',
        'LSR',
        'ASR',
        'ROR',
        'RRX',
        'DBG',
        'BKPT',
        'BFI',
        'BFC',
        'UBFX',
        'SBFX',
        'CLREX',
        'DMB',
        'DSB',
        'ISB',
        'USAD8',
        'USADA8',
        'PLD',
        'PLDW',
        'PLI',
        'IT',
        'MLA',
        'MLS',
        'SXTAH',
        'SXTH',
        'SXTAB16',
        'SXTAB',
        'SXTB16',
        'SXTB',
        'UXTAH',
        'UXTH',
        'UXTAB16',
        'UXTAB',
        'UXTB16',
        'UXTB',
        'VADDL',
        'VADDW',
        'VSUBL',
        'VSUBW',
        'VADDHN',
        'VRADDHN',
        'VSUBHN',
        'VRSUBHN',
        'VABAL',
        'VABDL',
        'VMLAL',
        'VMLSL',
        'VQDMLAL',
        'VQDMLSL',
        'VMULL',
        'VQDMULL',
        'VEXT',
        'VREV16',
        'VREV32',
        'VREV64',
        'VPADDL',
        'VCLS',
        'VCLZ',
        'VCNT',
        'VPADAL',
        'VQABS',
        'VQNEG',
        'VCLE',
        'VCLT',
        'VABS',
        'VNEG',
        'VDUP',
        'VTBL',
        'VTBX',
        'SMLABB',
        'SMLABT',
        'SMLATB',
        'SMLATT',
        'SMLALBB',
        'SMLALBT',
        'SMLALTB',
        'SMLALTT',
        'SMLAWB',
        'SMLAWT',
        'SMULBB',
        'SMULBT',
        'SMULTB',
        'SMULTT',
        'SMULWB',
        'SMULWT',
        'QADD',
        'QSUB',
        'QDADD',
        'QDSUB',
        'MSR',
        'MRS',
        'CDP',
        'CDP2',
        'MCR',
        'MRC',
        'MCR2',
        'MRC2',
        'MCRR',
        'MRRC',
        'MCRR2',
        'MRRC2',
        'VNMLA',
        'VNMLS',
        'VNMUL',
        'VDIV',
        'VFNMS',
        'VFNMA',
        'CLZ',
        'SMMUL',
        'SMMULR',
        'SMUAD',
        'SMUADX',
        'SMUSD',
        'SMUSDX',
        'SXTAB16',
        'SXTAB',
        'SXTAH',
        'SXTB16',
        'SXTB',
        'SXTH',
        'UXTAB16',
        'UXTAB',
        'UXTAH',
        'UXTB16',
        'UXTB',
        'UXTH',
        'SDIV',
        'UDIV',
        'SWP',
        'SWPB',
        'SEL',
        'SADD16',
        'SASX',
        'SSAX',
        'SSUB16',
        'SADD8',
        'SSUB8',
        'QADD16',
        'QASX',
        'QSAX',
        'QSUB16',
        'QADD8',
        'QSUB8',
        'SHADD16',
        'SHASX',
        'SHSAX',
        'SHSUB16',
        'SHADD8',
        'SHSUB8',
        'UQADD16',
        'UQASX',
        'UQSAX',
        'UQSUB16',
        'UQADD8',
        'UQSUB8',
        'UHADD16',
        'UHASX',
        'UHSAX',
        'UHSUB16',
        'UHADD8',
        'UHSUB8',
        'PKHBT',
        'PKHTB',
        'SSAT',
        'SSAT16',
        'USAT',
        'USAT16',
        'RBIT',
        'REV',
        'REVSH',
        'REV16',
        'VCMP',
        'VCMPE',
        'VSWP',
        'VTRN',
        'VUZP',
        'VZIP',
        'VMOVN',
        'VQMOVN',
        'VQMOVUN',
        'VRECPE',
        'VRSQRTE',
        'VSQRT',
        'VCVTR',
        'VMSR',
        'VMRS',
        'VSTM',
        'VSTR',
        'VPUSH',
        'VLDM',
        'VLDR',
        'VPOP',
        'SVC',
        'SETEND',
        'RFE',
        'SRS',
        'HINT',
        'UNDEF',
]

for ins_index, instr in enumerate(instrnames):
    globals()['INS_' + instr] = ins_index

no_update_Rd = (INS_TST, INS_TEQ, INS_CMP, INS_CMN, )
