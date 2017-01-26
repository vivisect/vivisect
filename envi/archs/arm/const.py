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
#Itterate through all REV_ARM values and setup related combo values 
for name, val in globals().items():
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

#IFLAGS - keep bottom 8-bits for cross-platform flags like envi.IF_NOFALL and envi.IF_BRFALL
IF_PSR_S     = 1<<32     # This DP instruciton can update CPSR  (as in, add vs. adds)
IF_B         = 1<<33     # Byte
IF_H         = 1<<35    # HalfWord
IF_S         = 1<<36    # Signed    #(not to be confused with IF_PSR_S which is the "update status" flag.
IF_D         = 1<<37    # Dword
IF_L         = 1<<38    # Long-store (eg. Dblword Precision) for STC
IF_T         = 1<<39    # Translate for strbt - denotes ldr/str command runs in user mode
IF_W         = 1<<40    # Write Back for STM/LDM (!)
IF_UM        = 1<<41    # User Mode Registers for STM/LDM (^) (obviously no R15)
IF_PSR_S_SIL = 1<<42    # Flag for Silent S. Related to IF_PSR_S and will prevent S from being rendered. TST, TEQ, CMN, CMP commands.
IF_IE        = 1<<43    # Interrupt Enable flag (used for CPS instruction)
IF_ID        = 1<<44    # Interrupt Disable flag (used for CPS instruction)

IF_THUMB32   = 1<<50    # thumb32

IF_DAIB_SHFT = 56       # shift-bits to get DAIB bits down to 0.  this chops off the "is DAIB present" bit that the following store.
IF_DAIB_MASK = 7<<(IF_DAIB_SHFT-1)
IF_DA        = 1<<(IF_DAIB_SHFT-1)  # Decrement After
IF_IA        = 3<<(IF_DAIB_SHFT-1)  # Increment After
IF_DB        = 5<<(IF_DAIB_SHFT-1)  # Decrement Before
IF_IB        = 7<<(IF_DAIB_SHFT-1)  # Increment Before
IF_DAIB_B    = 5<<(IF_DAIB_SHFT-1)  # Before mask
IF_DAIB_I    = 3<<(IF_DAIB_SHFT-1)  # Before mask

IFS_VQ        = 1<<1    # Adv SIMD: operation uses saturating arithmetic
IFS_VR        = 1<<2    # Adv SIMD: operation performs rounding
IFS_VD        = 1<<3    # Adv SIMD: operation doubles the result
IFS_VH        = 1<<4    # Adv SIMD: operation halves the result
IFS_SYS_MODE  = 1<<8    # instruction is encoded to be executed in SYSTEM mode, not USER mode

IFS_SFUI_START = 9
IFS_F32       = 1<<9    # F64 SIMD
IFS_F64       = 1<<10    # F64 SIMD
IFS_F32S32    = 1<<11    # F64 SIMD
IFS_F64S32    = 1<<12    # F64 SIMD
IFS_F32U32    = 1<<13    # F64 SIMD
IFS_F64U32    = 1<<14    # F64 SIMD
IFS_F3264     = 1<<15    # F64 SIMD
IFS_F6432     = 1<<16    # F64 SIMD
IFS_F3216     = 1<<17    # F64 SIMD
IFS_F1632     = 1<<18    # F64 SIMD
IFS_S32F64    = 1<<19    # F64 SIMD
IFS_S32F32    = 1<<20    # F64 SIMD
IFS_U32F64    = 1<<21    # F64 SIMD
IFS_U32F32    = 1<<22    # F64 SIMD
IFS_S8        = 1<<23    # F64 SIMD
IFS_S16       = 1<<24    # F64 SIMD
IFS_S32       = 1<<25    # F64 SIMD
IFS_S64       = 1<<26    # F64 SIMD
IFS_U8        = 1<<27    # F64 SIMD
IFS_U16       = 1<<28    # F64 SIMD
IFS_U32       = 1<<29    # F64 SIMD
IFS_U64       = 1<<30    # F64 SIMD
IFS_I8        = 1<<81    # F64 SIMD
IFS_I16       = 1<<32    # F64 SIMD
IFS_I32       = 1<<33    # F64 SIMD
IFS_I64       = 1<<34    # F64 SIMD
IFS_8         = 1<<35    # F64 SIMD
IFS_16        = 1<<36    # F64 SIMD
IFS_32        = 1<<37    # F64 SIMD
IFS_64        = 1<<38    # F64 SIMD
IFS_F8        = 1<<39
IFS_F16       = 1<<40
IFS_F32       = 1<<41
IFS_F64       = 1<<42

IFS_SFUI_STOP = 39

IFS_SFUI_MASK = 0
for x in range(IFS_SFUI_START, IFS_SFUI_STOP):
    IFS_SFUI_MASK |= (1<<x)

IFS_SFUI_MASK << IFS_SFUI_START

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
COND_LO     = 0x9        # c==0  or z==1  (unsigned lower or same)
COND_GE     = 0xA        # n==v  (signed greater than or equal)  (n==1 and v==1) or (n==0 and v==0)
COND_LT     = 0xB        # n!=v  (signed less than)  (n==1 and v==0) or (n==0 and v==1)
COND_GT     = 0xC        # z==0 and n==v (signed greater than)
COND_LE     = 0xD        # z==1 and n!=v (signed less than or equal)
COND_AL     = 0xE        # always
COND_EXTENDED = 0xF        # special case - see conditional 0b1111

cond_codes = {
COND_EQ:"eq", # Equal Z set 
COND_NE:"ne", # Not equal Z clear 
COND_CS:"cs", #/HS Carry set/unsigned higher or same C set 
COND_CC:"cc", #/LO Carry clear/unsigned lower C clear 
COND_MI:"mi", # Minus/negative N set 
COND_PL:"pl", # Plus/positive or zero N clear 
COND_VS:"vs", # Overflow V set 
COND_VC:"vc", # No overflow V clear 
COND_HI:"hi", # Unsigned higher C set and Z clear 
COND_LO:"lo", # Unsigned lower or same C clear or Z set 
COND_GE:"ge", # Signed greater than or equal N set and V set, or N clear and V clear (N == V) 
COND_LT:"lt", # Signed less than N set and V clear, or N clear and V set (N!= V) 
COND_GT:"gt", # Signed greater than Z clear, and either N set and V set, or N clear and V clear (Z == 0,N == V) 
COND_LE:"le", # Signed less than or equal Z set, or N set and V clear, or N clear and V set (Z == 1 or N!= V) 
COND_AL:"", # Always (unconditional) - could be "al" but "" seems better...
COND_EXTENDED:"", # See extended opcode table
}
cond_map = {
COND_EQ:0,      # Equal Z set 
COND_NE:1, # Not equal Z clear 
COND_CS:2, #/HS Carry set/unsigned higher or same C set 
COND_CC:3, #/LO Carry clear/unsigned lower C clear 
COND_MI:4, # Minus/negative N set 
COND_PL:5, # Plus/positive or zero N clear 
COND_VS:6, # Overflow V set 
COND_VC:7, # No overflow V clear 
COND_HI:8, # Unsigned higher C set and Z clear 
COND_LO:9, # Unsigned lower or same C clear or Z set 
COND_GE:10, # Signed greater than or equal N set and V set, or N clear and V clear (N == V) 
COND_LT:11, # Signed less than N set and V clear, or N clear and V set (N!= V) 
COND_GT:12, # Signed greater than Z clear, and either N set and V set, or N clear and V clear (Z == 0,N == V) 
COND_LE:13, # Signed less than or equal Z set, or N set and V clear, or N clear and V set (Z == 1 or N!= V) 
COND_AL:"", # Always (unconditional) - could be "al" but "" seems better...
COND_EXTENDED:"2", # See extended opcode table
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
IENC_DP_IMM_SHIFT = 0 # Data processing immediate shift
IENC_MISC         = 1 # Miscellaneous instructions
IENC_MISC1        = 2 # Miscellaneous instructions again
IENC_DP_REG_SHIFT = 3 # Data processing register shift
IENC_MULT         = 4 # Multiplies & Extra load/stores
IENC_UNDEF        = 5 # Undefined instruction
IENC_MOV_IMM_STAT = 6 # Move immediate to status register
IENC_DP_IMM       = 7 # Data processing immediate
IENC_LOAD_IMM_OFF = 8 # Load/Store immediate offset
IENC_LOAD_REG_OFF = 9 # Load/Store register offset
IENC_ARCH_UNDEF   = 10 # Architecturally undefined
IENC_MEDIA        = 11 # Media instructions
IENC_LOAD_MULT    = 12 # Load/Store Multiple
IENC_BRANCH       = 13 # Branch
IENC_COPROC_RREG_XFER = 14  # mrrc/mcrr
IENC_COPROC_LOAD  = 15 # Coprocessor load/store and double reg xfers
IENC_COPROC_DP    = 16 # Coprocessor data processing
IENC_COPROC_REG_XFER = 17 # Coprocessor register transfers
IENC_SWINT        = 18 # Sofware interrupts
IENC_UNCOND       = 19 # unconditional wacko instructions
IENC_EXTRA_LOAD   = 20 # extra load/store (swp)
IENC_DP_MOVW      = 21 # Not sure it exists?
IENC_DP_MOVT      = 22 # move top
IENC_DP_MSR_IMM   = 23 # 
IENC_LOAD_STORE_WORD_UBYTE = 24

IENC_MAX        = 25

# offchutes
IENC_MEDIA_PARALLEL = ((IENC_MEDIA << 8) + 1) << 8
IENC_MEDIA_SAT      = ((IENC_MEDIA << 8) + 2) << 8
IENC_MEDIA_REV      = ((IENC_MEDIA << 8) + 3) << 8
IENC_MEDIA_SEL      = ((IENC_MEDIA << 8) + 4) << 8
IENC_MEDIA_USAD8    = ((IENC_MEDIA << 8) + 5) << 8
IENC_MEDIA_USADA8   = ((IENC_MEDIA << 8) + 6) << 8
IENC_MEDIA_EXTEND   = ((IENC_MEDIA << 8) + 7) << 8
IENC_MEDIA_PACK     = ((IENC_MEDIA << 8) + 8) << 8
IENC_MEDIA_SBFX     = IENC_MEDIA_PACK #FIXME
IENC_MEDIA_PDIV     = IENC_MEDIA_PACK #FIXME
IENC_UNCOND_CPS     = ((IENC_UNCOND << 8) + 1) << 8
IENC_UNCOND_SETEND  = ((IENC_UNCOND << 8) + 2) << 8
IENC_UNCOND_PLD     = ((IENC_UNCOND << 8) + 3) << 8
IENC_UNCOND_PLI     = IENC_UNCOND_PLD #FIXME
IENC_UNCOND_BLX     = ((IENC_UNCOND << 8) + 4) << 8
IENC_UNCOND_RFE     = ((IENC_UNCOND << 8) + 5) << 8
IENC_UNCOND_CLREX   = IENC_UNCOND_PLD #FIXME
IENC_UNCOND_DMB     = IENC_UNCOND_PLD #FIXME
IENC_UNCOND_DSB     = IENC_UNCOND_PLD #FIXME
IENC_UNCOND_ISB     = IENC_UNCOND_PLD #FIXME


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


def instrenc(encoding, index):
    return (encoding << 16) + index

INS_AND = IENC_DP_IMM_SHIFT << 16
INS_EOR = (IENC_DP_IMM_SHIFT << 16) + 1
INS_SUB = (IENC_DP_IMM_SHIFT << 16) + 2
INS_RSB = (IENC_DP_IMM_SHIFT << 16) + 3
INS_ADD = (IENC_DP_IMM_SHIFT << 16) + 4
INS_ADC = (IENC_DP_IMM_SHIFT << 16) + 5
INS_SBC = (IENC_DP_IMM_SHIFT << 16) + 6
INS_RSC = (IENC_DP_IMM_SHIFT << 16) + 7
INS_TST = (IENC_DP_IMM_SHIFT << 16) + 8
INS_TEQ = (IENC_DP_IMM_SHIFT << 16) + 9
INS_CMP = (IENC_DP_IMM_SHIFT << 16) + 10
INS_CMN = (IENC_DP_IMM_SHIFT << 16) + 11
INS_ORR = (IENC_DP_IMM_SHIFT << 16) + 12
INS_MOV = (IENC_DP_IMM_SHIFT << 16) + 13
INS_BIC = (IENC_DP_IMM_SHIFT << 16) + 14
INS_MVN = (IENC_DP_IMM_SHIFT << 16) + 15
INS_ORN = (IENC_DP_IMM_SHIFT << 16) + 12
INS_ADR = (IENC_DP_IMM_SHIFT << 16) + 16


INS_B       = instrenc(IENC_BRANCH, 0)
INS_BL      = instrenc(IENC_BRANCH, 1)
INS_BCC     = instrenc(IENC_BRANCH, 2)
INS_BX      = instrenc(IENC_MISC, 3)
INS_BXJ     = instrenc(IENC_MISC, 5)
INS_BLX     = IENC_UNCOND_BLX

INS_SWI     = IENC_SWINT
 

#Opcodes still needed - put here as todo with others
#dbg, movt, movw


INS_LDR = instrenc(IENC_LOAD_IMM_OFF,  0)
INS_STR = instrenc(IENC_LOAD_IMM_OFF,  1)


no_update_Rd = (INS_TST, INS_TEQ, INS_CMP, INS_CMN, )

instrnames = [
        'INS_VHADD',
        'INS_VQADD',
        'INS_VRHADD',
        'INS_VAND',
        'INS_VBIC',
        'INS_VORR',
        'INS_VORN',
        'INS_VEOR',
        'INS_VBIF',
        'INS_VBIT',
        'INS_VBSL',
        'INS_VHSUB',
        'INS_VQSUB',
        'INS_VCGT',
        'INS_VCGE',
        'INS_VCEQ',
        'INS_VSHL',
        'INS_VQSHL',
        'INS_VRSHL',
        'INS_VQRSHL',
        'INS_VMAX',
        'INS_VMIN',
        'INS_VABD',
        'INS_VABA',
        'INS_VADD',
        'INS_VSUB',
        'INS_VTST',
        'INS_VMLA',
        'INS_VMLS',
        'INS_VMUL',
        'INS_VPMAX',
        'INS_VPMIN',
        'INS_VQMULH',
        'INS_VQDMULH',
        'INS_VQRDMULH',
        'INS_VPADD',
        'INS_VPSUB',
        'INS_VFMA',
        'INS_VFMS',
        'INS_VACGE',
        'INS_VACGT',
        'INS_VRECPS',
        'INS_VRSQRTS',
        'INS_VMOV',
        'INS_VMVN',
        'INS_VSHR',
        'INS_VSRA',
        'INS_VRSHR',
        'INS_VRSRA',
        'INS_VSLI',
        'INS_VSRI',
        'INS_VQSHLU',
        'INS_VSHRN',
        'INS_VRSHRN',
        'INS_VQSHRN',
        'INS_VQSHRUN',
        'INS_VQRSHRN',
        'INS_VQRSHRUN',
        'INS_VSHLL',
        'INS_VCVT',
        #'INS_LDRB',
        #'INS_STRB',
        'INS_SMUL',
        'INS_UADD16',
        'INS_UADD8',
        'INS_USUB16',
        'INS_USUB8',
        'INS_UASX',
        'INS_USAX',
        'INS_NOP',
        'INS_YIELD',
        'INS_WFE',
        'INS_WFI',
        'INS_SEV',
        'INS_CPS',
        'INS_CBZ',
        'INS_CBNZ',
        'INS_STRH',
        #'INS_LDRH',
        'INS_LEAVEX',
        'INS_ENTERX',
        'INS_TB',
        'INS_LDREX',
        'INS_ORN',
        'INS_PKH',
        'INS_LSL',
        'INS_LSR',
        'INS_ASR',
        'INS_ROR',
        'INS_RRX',
        'INS_DBG',
        'INS_BF',
        'INS_CLREX',
        'INS_DMB',
        'INS_DSB',
        'INS_ISB',
        #'INS_LDRSB',
        'INS_PLD',
        'INS_PLI',
        'INS_IT',
]

ins_index = 85
for instr in instrnames:
    globals()[instr] = ins_index
    ins_index += 1
