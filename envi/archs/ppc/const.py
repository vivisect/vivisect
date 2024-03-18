from .const_gen import *

ENDIAN_LSB = 0
ENDIAN_MSB = 1

TYPE_NONE = 0
TYPE_REG =  1

# The "se_" instructions have register fields that are only 4 bits wide instead
# of 5 bits wide, so normally register values 0-15 refer to registers
# r0-r7,r24-r31. But there are some "alternate register" instructions where 0-15
# refers to r8-r23. the TYPE_REG_SE helps to distinguish between these different
# fields when parsing "se_" VLE instructions.
TYPE_REG_SE = 2

TYPE_IMM =  3
TYPE_SIMM16 = 4
TYPE_SIMM20 = 5
TYPE_SIMM32 = 6
TYPE_MEM =  7
TYPE_SE_MEM =  8
TYPE_JMP =  9
TYPE_CR =   10
TYPE_CRB =  11

E_NONE =  0
E_X =     1
E_XL =    2
E_D =     3
E_D8 =    4

# This form is a variation of the E_D8 parser that is used for parsing the new
# "e_ldmv*" and "e_stmv*" ISR vector load/store instructions. E_D8 is close to
# what is needed to parse these instructions, but it is not quite right.  The rA
# field is smaller than a normal E_D8 instruction.
E_D8VLS = 5

E_I16A =  6
E_SCI8 =  7
E_SCI8I = 8

# There are some compare instructions that use the SCI8 form, but the CRD32
# field is not formed like the normal rD field in an SCI8 instruction
E_SCI8CR = 9

E_I16L =  10
E_I16LS = 11
E_BD24 =  12
E_BD15 =  13
# Removed typo form: E_IA16 =  14
E_LI20 =  15
E_M =     16
E_XCR =   17
E_XLSP =  18
E_XRA =   19

E_MASK_X =    0x03FFF800
E_MASK_XL =   0x03FFF801
E_MASK_D =    0x03FFFFFF
E_MASK_D8 =   0x03FF00FF
E_MASK_D8VLS = 0x001F00FF  # Mask for the D8 "volatile" load/store instructions
E_MASK_I16A = 0x03FF07FF
E_MASK_SCI8 = 0x03FF07FF
E_MASK_SCI8CR = 0x007F07FF # Mask for the SCI8 form "e_cmpi", and "e_cmpli" instructions
E_MASK_SCI8_2 = 0x03FF0700 # Special SCI8 mask for the "e_mr" alias of "e_ori"
E_MASK_I16L = 0x03FF07FF
E_MASK_BD24 = 0x03FFFFFE
E_MASK_BD15 = 0x000CFFFE
E_MASK_BD15CTR = 0x000FFFFE
E_MASK_LI20 = 0x03FF7FFF
E_MASK_M =    0x03FFFFFE

F_NONE =  0
F_X =     1
F_XO =    2
F_EVX =   3
F_CMP =   4
F_DCBF =  5
F_DCBL =  6
F_DCI =   7
F_EXT =   8
F_A =     9
F_XFX =  10
F_XER =  11
F_MFPR = 12
F_MTPR = 13
F_XRA =  14
F_X_2 =  15

# The "wrteei" instruction is a normal PPC instruction but it gets parsed in
# it's own special way
F_X_WRTEEI = 16

# The "mtcrf" instruction is a normal PPC instruction but it gets parsed in it's
# own special way
F_X_MTCRF = 17

# For some of the normal PPC form X instructions the second register argument
# (rA) when rA is 0 it is interpreted as a constant 0 rather than r0.
F_X_Z = 18


F_MASK_X =     0x03FFF800
F_MASK_XO =    0x03FFF800
F_MASK_EVX =   0x03FFF800
F_MASK_CMP =   0x039FF800
F_MASK_DCBF =  0x00FFF800
F_MASK_DCBL =  0x01FFF800
F_MASK_DCI =   0x00FFF800
F_MASK_EXT =   0x03FF0000
F_MASK_A =     0x01FFFFC0
F_MASK_A_ISEL = 0x03FFFF00
F_MASK_XFX =   0x03FFF800
F_MASK_XER =   0x03FFF800
F_MASK_MFPR =  0x03FFF800
F_MASK_MTPR =  0x03FFF800

COND_AL = 0
COND_GE = 1
COND_LE = 2
COND_NE = 3
COND_VC = 4
COND_LT = 5
COND_GT = 6
COND_EQ = 7
COND_VS = 8
COND_NV = 9

IFLAGS_NONE = 0
IF_CAT64 = 1 << 8

OEMODE_LEGACY = 0
OEMODE_ADDSUBNEG = 1
OEMODE_MULDIV = 2

# special instruction aliases:
INS_VMR = inscounter ; inscounter += 1

# Constants used for checking ESR values
ESR_PIL_MASK    = 0x08000000
ESR_PPR_MASK    = 0x04000000
ESR_PTR_MASK    = 0x02000000
ESR_FP_MASK     = 0x01000000
ESR_ST_MASK     = 0x00800000
ESR_DLK_MASK    = 0x00200000
ESR_ILK_MASK    = 0x00100000
ESR_AP_MASK     = 0x00080000
ESR_PUO_MASK    = 0x00040000
ESR_BO_MASK     = 0x00020000
ESR_PIE_MASK    = 0x00010000
ESR_SPE_MASK    = 0x00000080
ESR_VLEMI_MASK  = 0x00000020
ESR_MIF_MASK    = 0x00000002

# Constants used for checking MSR values, this is all possible PowerPC MSR
# masks, most PPC processors only support a subset of these flags
MSR_CM_MASK     = 0x80000000  # Computation Mode (CAT_64)
MSR_GS_MASK     = 0x80000000  # Guest State (CAT_HV)
MSR_UCLE_MASK   = 0x04000000  # User-mode cache lock enable (E.CL)
MSR_SPE_MASK    = 0x02000000  # Enables SPE, SP.FD, SP.FV instructions (CAT_SP)
MSR_VECTOR_MASK = 0x02000000  # Enables Vector (Altivec) instructions (CAT_V)
MSR_WE_MASK     = 0x00040000  # Wait State Enable (deprecated) (CAT_WT)
MSR_CE_MASK     = 0x00020000  # Critical Enable
MSR_EE_MASK     = 0x00008000  # External Enable
MSR_PR_MASK     = 0x00004000  # User Mode (Problem State) (CAT_EM?)
MSR_FP_MASK     = 0x00002000  # Floating-Point Enable (CAT_FP)
MSR_ME_MASK     = 0x00001000  # Machine-Check Enable
MSR_FE0_MASK    = 0x00000800  # Floating-Point Exception Mode 0 (CAT_FP)
MSR_DE_MASK     = 0x00000200  # Debug Interrupt Enable
MSR_FE1_MASK    = 0x00000100  # Floating-Point Exception Mode 1 (CAT_FP)
MSR_IS_MASK     = 0x00000020  # Instruction Address Space (CAT_E)
MSR_DS_MASK     = 0x00000010  # Data Address Space (CAT_E)
MSR_PMM_MASK    = 0x00000004  # Performance Monitor Mark (CAT_E.PM)
MSR_RI_MASK     = 0x00000002  # Recoverable Interrupt

# Some shift amounts used for accessing specific MSR bits
MSR_IS_SHIFT    = 5
MSR_DS_SHIFT    = 4

# flag bit numbers and masks
FLAGS_LT_bitnum = 3-0   # noted to tie back to the manual's referencing this as bit 0
FLAGS_GT_bitnum = 3-1
FLAGS_EQ_bitnum = 3-2
FLAGS_SO_bitnum = 3-3

FLAGS_LT = 1 << FLAGS_LT_bitnum
FLAGS_GT = 1 << FLAGS_GT_bitnum
FLAGS_EQ = 1 << FLAGS_EQ_bitnum
FLAGS_SO = 1 << FLAGS_SO_bitnum

# XER-agnostic CA and OV flags
FLAGS_XER_SO_bitnum = 3-0
FLAGS_XER_OV_bitnum = 3-1
FLAGS_XER_CA_bitnum = 3-2

FLAGS_XER_SO = 1 << FLAGS_XER_SO_bitnum
FLAGS_XER_OV = 1 << FLAGS_XER_OV_bitnum
FLAGS_XER_CA = 1 << FLAGS_XER_CA_bitnum

# XER-specific bit offsets

# The amount to shift the non-XER positioned flags to fit them into the correct
# positions
XERFLAGS_shift = 28
XERFLAGS_MASK = 0b1110 << XERFLAGS_shift

# The SO, OV, and CA bit positions in the XER (which the documentation and
# PowerISA specify is a 64 bit SPR but only the lower 32 bits are used)
XERFLAGS_SO_bitnum = 63-32
XERFLAGS_OV_bitnum = 63-33
XERFLAGS_CA_bitnum = 63-34

# XER flags
XERFLAGS_SO = 1 << XERFLAGS_SO_bitnum
XERFLAGS_OV = 1 << XERFLAGS_OV_bitnum
XERFLAGS_CA = 1 << XERFLAGS_CA_bitnum

# roll-up architecture CATEGORIES
CAT_PPC_SERVER = CAT_ALTIVEC =   CAT_NONE | CAT_EMBEDDED | CAT_E | CAT_V | CAT_64 | CAT_E_ED | CAT_WT | CAT_E_PD | CAT_E_CL | CAT_E_PC | CAT_FP | CAT_FP_R | CAT_E_PM | CAT_ER | CAT_EM_TM
CAT_PPC_EMBEDDED =   CAT_SPE =       CAT_NONE | CAT_E | CAT_E_ED | CAT_E_HV | CAT_E_PD | CAT_E_CL | CAT_E_PC | CAT_E_DC | CAT_E_PM | CAT_SP | CAT_SP_FV | CAT_SP_FS | CAT_SP_FD | CAT_ER | CAT_EM_TM | CAT_DS | CAT_FP | CAT_DEO | CAT_FP_R | CAT_WT | CAT_64 | CAT_EMBEDDED | CAT_ISAT

# mask to clear out a 4-bit part of the 32-bit CR register about to be written
cr_mask = [(0xffffffff & ~(0xf<<(4*x))) for x in range(8)[::-1]]

# mask to clear out a 3-bit part of the 32-bit CR register about to be written
cr_cmp_mask = [(0xffffffff & ~(0xe<<(4*x))) for x in range(8)[::-1]]


# Branch BO field values
#
# Table 5-27. BO Operand Encodings
# page 319 of EREF_RM.pdf
#
#   BO    | Description
#   ------+------------
#   0000z | Decrement the CTR, then branch if the decremented CTR ≠ 0 and the condition is FALSE.
#   0001z | Decrement the CTR, then branch if the decremented CTR = 0 and the condition is FALSE.
#   001at | Branch if the condition is FALSE.
#   0100z | Decrement the CTR, then branch if the decremented CTR ≠ 0 and the condition is TRUE.
#   0101z | Decrement the CTR, then branch if the decremented CTR = 0 and the condition is TRUE.
#   011at | Branch if the condition is TRUE.
#   1a00t | Decrement the CTR, then branch if the decremented CTR ≠ 0.
#   1a01t | Decrement the CTR, then branch if the decremented CTR = 0.
#   1z1zz | Branch always.
#
#   z  == don't care
#   at == branch prediction bits
FLAGS_BO_CHECK_CTR_ZERO = 0b00010
FLAGS_BO_DECREMENT      = 0b00100
FLAGS_BO_COND           = 0b01000
FLAGS_BO_CHECK_COND     = 0b10000


# FPSCR combined C & FPCC flags for results
#
#   C < > = ? | Result Value Class
#   ----------+-------------------
#   1 0 0 0 1 | Quiet NaN
#   0 1 0 0 1 | –Infinity
#   0 1 0 0 0 | –Normalized number
#   1 1 0 0 0 | –Denormalized number
#   1 0 0 1 0 | –Zero
#   0 0 0 1 0 | +Zero
#   1 0 1 0 0 | +Denormalized number
#   0 0 1 0 0 | +Normalized number
#   0 0 1 0 1 | +Infinity
C_FPCC_SIGNALING_NAN    = 0b00001
C_FPCC_QUIET_NAN        = 0b10001
C_FPCC_NEG_INFINITY     = 0b01001
C_FPCC_NEG_NORMALIZED   = 0b01000
C_FPCC_NEG_DENORMALIZED = 0b11000
C_FPCC_NEG_ZERO         = 0b10010
C_FPCC_POS_ZERO         = 0b00010
C_FPCC_POS_DENORMALIZED = 0b10100
C_FPCC_POS_NORMALIZED   = 0b00100
C_FPCC_POS_INFINITY     = 0b00101

# FPSCR-agnostic C and FPCC (floating point condition flags) bits
FLAGS_FPSCR_C_bitnum  = 4-0
FLAGS_FPSCR_FL_bitnum = 4-1
FLAGS_FPSCR_FG_bitnum = 4-2
FLAGS_FPSCR_FE_bitnum = 4-3
FLAGS_FPSCR_FU_bitnum = 4-4

FLAGS_FPSCR_C  = 1 << FLAGS_FPSCR_C_bitnum
FLAGS_FPSCR_FL = 1 << FLAGS_FPSCR_FL_bitnum
FLAGS_FPSCR_FG = 1 << FLAGS_FPSCR_FG_bitnum
FLAGS_FPSCR_FE = 1 << FLAGS_FPSCR_FE_bitnum
FLAGS_FPSCR_FU = 1 << FLAGS_FPSCR_FU_bitnum

# The C and FPCC positions in the FPSCR
FPSCRFLAGS_C_bitnum  = 63-47
FPSCRFLAGS_FL_bitnum = 63-48
FPSCRFLAGS_FG_bitnum = 63-49
FPSCRFLAGS_FE_bitnum = 63-50
FPSCRFLAGS_FU_bitnum = 63-51

# FPSCR flags
FPSCRFLAGS_C  = 1 << FPSCRFLAGS_C_bitnum
FPSCRFLAGS_FL = 1 << FPSCRFLAGS_FL_bitnum
FPSCRFLAGS_FG = 1 << FPSCRFLAGS_FG_bitnum
FPSCRFLAGS_FE = 1 << FPSCRFLAGS_FE_bitnum
FPSCRFLAGS_FU = 1 << FPSCRFLAGS_FU_bitnum

# The amount to shift the non-XER positioned flags to fit them into the correct
# positions
FPSCRFLAGS_C_FPCC_shift = 16

FPSCRFLAGS_MASK = 0b11111 << FPSCRFLAGS_C_FPCC_shift

# This mask is for [.] instructions that set cr1.  FPSCR will be touched after every
# floating point instruction but cr1 will only be touched if the RC bit is set.  This
# behaves similarly to "if op.iflags & IF_RC: self.setFlags(result)" but with cr1.
# In [.] instructions cr1 is set to equal what the FX || FEX ||  VX || OX bits in FPSCR

FPSCR_FLOAT_RC_MASK = 0xF0000000

# Shift for moving FPSCR 0xF0000000 to 0xf to put in cr1 for setFloatCr()
FPSCR_FLOAT_RC_SHIFT = 28

# Mask to convert the combined C_FPCC flags into the standard flags to store in
# CR1 (just drop the 'C' class descriptor)
C_FPCC_TO_CR1_MASK      = 0x01111

# Constants used to check against floating point results
# Taken from section 4.4.3.2.2 of EREF_RM.pdf
FP_SINGLE_NORMALIZED_MIN = 1.2 * (10 ** -38)
FP_SINGLE_NORMALIZED_MAX = 3.4 * (10 ** 38)
FP_DOUBLE_NORMALIZED_MIN = 2.2 * (10 ** -308)
FP_DOUBLE_NORMALIZED_MAX = 1.8 * (10 ** 308)

# Floating point numbers are "denormalized" when the exponent component is 0.
# Here are some masks for working with floating point numbers that can be used
# to check if floating-point numbers are denormalized. The sign bits can be
# checked with the normal envi.bits.is_signed() function.
FP_SINGLE_EXP_MASK   = 0x7F80_0000
FP_SINGLE_FRACT_MASK = 0x007F_FFFF

FP_DOUBLE_EXP_MASK   = 0x7FF8_0000_0000_0000
FP_DOUBLE_FRACT_MASK = 0x0007_FFFF_FFFF_FFFF

FP_EXP_MASK = {
    8: FP_DOUBLE_EXP_MASK,
    4: FP_SINGLE_EXP_MASK,
}

FP_FRACT_MASK = {
    8: FP_DOUBLE_FRACT_MASK,
    4: FP_SINGLE_FRACT_MASK,
}

# The NaN values produced in python by struct.pack('>f', float('NaN')) are quiet
# NaNs, but for some reason the least significant bit of the fractional
# component is 0 instead of 1.  Most commonly IEEE754 NaN vs Inf is indicated
# using the LSB and the MSB of the fractional component is used to indicate
# quiet vs. signalling NaN.  In python it appears that the MSB is used to
# indicate NaN vs. Inf.
#
# Thankfully struct.unpack() correctly the PPC encoded NaN values correctly to
# the float('NaN') value.
FP_DOUBLE_NEG_PYNAN = 0xFFFC_0000_0000_0000
FP_DOUBLE_POS_PYNAN = 0x7FFC_0000_0000_0000

FP_SINGLE_NEG_PYNAN = 0xFFC0_0000
FP_SINGLE_POS_PYNAN = 0x7FC0_0000

FP_DOUBLE_NEG_QNAN  = 0xFFFC_0000_0000_0001
FP_DOUBLE_POS_QNAN  = 0x7FFC_0000_0000_0001
FP_DOUBLE_NEG_SNAN  = 0xFFF8_0000_0000_0001
FP_DOUBLE_POS_SNAN  = 0x7FF8_0000_0000_0001
FP_DOUBLE_NEG_INF   = 0xFFF0_0000_0000_0000
FP_DOUBLE_POS_INF   = 0x7FF0_0000_0000_0000
FP_DOUBLE_NEG_MAX   = 0xFFEF_FFFF_FFFF_FFFF
FP_DOUBLE_POS_MAX   = 0x7FEF_FFFF_FFFF_FFFF

FP_SINGLE_NEG_QNAN  = 0xFFC0_0001
FP_SINGLE_POS_QNAN  = 0x7FC0_0001
FP_SINGLE_NEG_SNAN  = 0xFF80_0001
FP_SINGLE_POS_SNAN  = 0x7F80_0001
FP_SINGLE_NEG_INF   = 0xFF80_0000
FP_SINGLE_POS_INF   = 0x7F80_0000
FP_SINGLE_NEG_MAX   = 0xFF7F_FFFF
FP_SINGLE_POS_MAX   = 0x7F7F_FFFF

FP_HALF_NEG_QNAN = 0xFE01
FP_HALF_POS_QNAN = 0x7C01
FP_HALF_NEG_SNAN = 0xFC01
FP_HALF_POS_SNAN = 0x7C01
FP_HALF_POS_INF  = 0xFC00
FP_HALF_NEG_INF  = 0x7C00
FP_HALF_NEG_MAX  = 0xFBFF
FP_HALF_POS_MAX  = 0x7BFF

FP_DOUBLE_NEG_ZERO  = 0x8000_0000_0000_0000
FP_DOUBLE_POS_ZERO  = 0x0000_0000_0000_0000

FP_SINGLE_NEG_ZERO  = 0x8000_0000
FP_SINGLE_POS_ZERO  = 0x0000_0000

FP_HALF_NEG_ZERO = 0x8000
FP_HALF_POS_ZERO = 0x0000

FNAN_ALL_TUP = (FP_DOUBLE_NEG_PYNAN,FP_DOUBLE_POS_PYNAN,FP_SINGLE_NEG_PYNAN,\
    FP_SINGLE_POS_PYNAN,FP_DOUBLE_NEG_QNAN,FP_DOUBLE_POS_QNAN,FP_DOUBLE_NEG_SNAN,\
    FP_DOUBLE_POS_SNAN,FP_SINGLE_NEG_QNAN,FP_SINGLE_POS_QNAN,FP_SINGLE_NEG_SNAN,\
FP_SINGLE_POS_SNAN, FP_HALF_NEG_QNAN, FP_HALF_NEG_SNAN, FP_HALF_POS_QNAN, FP_HALF_NEG_SNAN)

FNAN_HALF_TUP = (FP_HALF_NEG_QNAN, FP_HALF_POS_QNAN, FP_HALF_NEG_SNAN, FP_HALF_POS_SNAN, \
FP_HALF_NEG_INF, FP_HALF_POS_INF)

FNAN_SINGLE_TUP = (FP_SINGLE_NEG_PYNAN, FP_SINGLE_POS_PYNAN, FP_SINGLE_NEG_QNAN, \
FP_SINGLE_POS_QNAN, FP_SINGLE_NEG_SNAN, FP_SINGLE_POS_SNAN)

FNAN_DOUBLE_TUP = (FP_DOUBLE_NEG_PYNAN, FP_DOUBLE_POS_PYNAN, FP_DOUBLE_NEG_QNAN, \
FP_DOUBLE_POS_QNAN, FP_DOUBLE_NEG_SNAN, FP_DOUBLE_POS_SNAN)

FNAN_SNAN_TUP = (FP_DOUBLE_NEG_SNAN, FP_DOUBLE_POS_SNAN, FP_SINGLE_NEG_SNAN, FP_SINGLE_POS_SNAN,\
FP_HALF_NEG_SNAN, FP_HALF_POS_SNAN)

FNAN_SINGLE_SNAN_TUP = (FP_SINGLE_NEG_SNAN, FP_SINGLE_POS_SNAN)

FNAN_DOUBLE_SNAN_TUP = (FP_DOUBLE_NEG_SNAN, FP_DOUBLE_POS_SNAN)

FNAN_POS_TUP = (FP_DOUBLE_POS_SNAN, FP_SINGLE_POS_SNAN, FP_DOUBLE_POS_QNAN, FP_SINGLE_POS_QNAN)

FNAN_HALF_POS_TUP =  (FP_HALF_POS_QNAN, FP_HALF_POS_SNAN)

FNAN_SINGLE_POS_TUP = (FP_SINGLE_POS_SNAN, FP_SINGLE_POS_QNAN)

FNAN_DOUBLE_POS_TUP = (FP_DOUBLE_POS_SNAN, FP_DOUBLE_POS_QNAN)

FNAN_NEG_TUP = (FP_DOUBLE_NEG_SNAN, FP_SINGLE_NEG_SNAN, FP_DOUBLE_NEG_QNAN, FP_SINGLE_NEG_QNAN)

FNAN_HALF_NEG_TUP = (FP_HALF_NEG_QNAN, FP_HALF_NEG_SNAN)

FNAN_SINGLE_NEG_TUP = (FP_SINGLE_NEG_SNAN, FP_SINGLE_NEG_QNAN)

FNAN_DOUBLE_NEG_TUP = (FP_DOUBLE_NEG_SNAN, FP_DOUBLE_NEG_QNAN)

FNAN_POS_SNAN_TUP = (FP_DOUBLE_POS_SNAN, FP_SINGLE_POS_SNAN)

FNAN_NEG_SNAN_TUP = (FP_DOUBLE_NEG_SNAN, FP_SINGLE_NEG_SNAN)

FNAN_QNAN_TUP = (FP_DOUBLE_NEG_QNAN,FP_DOUBLE_POS_QNAN,FP_SINGLE_NEG_QNAN,FP_SINGLE_POS_QNAN,)

FNAN_HALF_QNAN_TUP = (FP_HALF_NEG_QNAN, FP_HALF_POS_QNAN)

FNAN_SINGLE_QNAN_TUP = (FP_SINGLE_NEG_QNAN, FP_SINGLE_POS_QNAN)

FNAN_DOUBLE_QNAN_TUP = (FP_DOUBLE_NEG_QNAN, FP_DOUBLE_POS_QNAN)

FNAN_POS_QNAN_TUP = (FP_DOUBLE_POS_QNAN, FP_SINGLE_POS_QNAN, FP_HALF_POS_QNAN)

FNAN_NEG_QNAN_TUP = (FP_DOUBLE_NEG_QNAN, FP_SINGLE_NEG_QNAN, FP_HALF_NEG_QNAN)

FNAN_PYNAN_TUP = (FP_DOUBLE_NEG_PYNAN,FP_DOUBLE_POS_PYNAN,FP_SINGLE_NEG_PYNAN,FP_SINGLE_POS_PYNAN,)

FNAN_SINGLE_PYNAN_TUP = (FP_SINGLE_NEG_PYNAN, FP_SINGLE_POS_PYNAN, )

FNAN_DOUBLE_PYNAN_TUP = (FP_DOUBLE_NEG_PYNAN, FP_DOUBLE_POS_PYNAN)

F_INF_TUP = (FP_DOUBLE_NEG_INF, FP_DOUBLE_POS_INF, FP_SINGLE_NEG_INF, FP_SINGLE_POS_INF,\
FP_HALF_POS_INF, FP_HALF_NEG_INF)

F_HALF_INF_TUP = (FP_HALF_NEG_INF, FP_HALF_POS_INF)

F_SINGLE_INF_TUP = (FP_SINGLE_NEG_INF, FP_SINGLE_POS_INF)

F_DOUBLE_INF_TUP = (FP_DOUBLE_NEG_INF, FP_DOUBLE_POS_INF)

F_POS_INF_TUP = (FP_DOUBLE_POS_INF, FP_SINGLE_POS_INF, FP_HALF_POS_INF, FP_HALF_NEG_INF)

F_NEG_INF_TUP = (FP_DOUBLE_NEG_INF, FP_SINGLE_NEG_INF)

F_ZERO_TUP = (FP_DOUBLE_NEG_ZERO,FP_DOUBLE_POS_ZERO,FP_SINGLE_POS_ZERO,FP_SINGLE_NEG_ZERO,)

F_SINGLE_ZERO_TUP = (FP_SINGLE_POS_ZERO, FP_SINGLE_NEG_ZERO)

F_DOUBLE_ZERO_TUP = (FP_DOUBLE_NEG_ZERO, FP_DOUBLE_POS_ZERO)

F_POS_ZERO_TUP = (FP_DOUBLE_POS_ZERO, FP_SINGLE_POS_ZERO)

F_NEG_ZERO_TUP = (FP_DOUBLE_NEG_ZERO, FP_SINGLE_NEG_ZERO)

# A dictionary for setting the C_FPCC flags based on a floating-point
# calculation when the value is in the "unordered" category.  This isn't as fast
# as a purely algorithm way to do this but should be faster than a large
# if-elif-else case.
#
# The first layer is indexed by the FP size: 8 (double precision) or 4 (single
# precision).  If a match is not found in this list then a denormalized value
# check will be necessary.
#
# Although not really an "unordered" value class, signed and unsigned zero are
# also checked here because it's easy to do so.
FP_FLAGS = {
    8: {
        FP_DOUBLE_NEG_QNAN: C_FPCC_QUIET_NAN,
        FP_DOUBLE_POS_QNAN: C_FPCC_QUIET_NAN,
        FP_DOUBLE_NEG_SNAN: C_FPCC_SIGNALING_NAN,
        FP_DOUBLE_POS_SNAN: C_FPCC_SIGNALING_NAN,
        FP_DOUBLE_NEG_INF:  C_FPCC_NEG_INFINITY,
        FP_DOUBLE_POS_INF:  C_FPCC_POS_INFINITY,
        FP_DOUBLE_NEG_ZERO: C_FPCC_NEG_ZERO,
        FP_DOUBLE_POS_ZERO: C_FPCC_POS_ZERO,
    },
    4: {
        FP_SINGLE_NEG_QNAN: C_FPCC_QUIET_NAN,
        FP_SINGLE_POS_QNAN: C_FPCC_QUIET_NAN,
        FP_SINGLE_NEG_SNAN: C_FPCC_SIGNALING_NAN,
        FP_SINGLE_POS_SNAN: C_FPCC_SIGNALING_NAN,
        FP_SINGLE_NEG_INF:  C_FPCC_NEG_INFINITY,
        FP_SINGLE_POS_INF:  C_FPCC_POS_INFINITY,
        FP_SINGLE_NEG_ZERO: C_FPCC_NEG_ZERO,
        FP_SINGLE_POS_ZERO: C_FPCC_POS_ZERO,
    },
}

# Ordered flag lookup, lookup by normalized (0)/denormalized (1) first, then
# unsigned (0)/signed (1) next.

FP_ORDERED_FLAGS = (
    (C_FPCC_POS_NORMALIZED, C_FPCC_NEG_NORMALIZED),
    (C_FPCC_POS_DENORMALIZED, C_FPCC_NEG_DENORMALIZED),
)

# On 64-bit systems single-precision floating point values aren't represented
# with normal 32-bit IEEE754 values, but instead the hardware appears to use the
# full 64-bit register and masks off the lower 29 bits of the fraction portion.
# This is the mask to use to generate accurate single-precision floating-point
# values for emulating 64-bit PPC systems.
PPC_64BIT_SINGLE_PRECISION_MASK = 0xFFFFFFFFE0000000

# For more easily identifying load and store instructions
STORE_INSTRS = (
    INS_STBX,
    INS_STHX,
    INS_STWX,
    INS_STDX,
    INS_STBUX,
    INS_STHUX,
    INS_STWUX,
    INS_STDUX,
    INS_STFDX,
    INS_STFIWX,
    INS_STFDEPX,
    INS_STFDUX,
    INS_STVEBX,
    INS_STVEHX,
    INS_STVEWX,
    INS_STVEXBX,
    INS_STVEXHX,
    INS_STVEXWX,
    INS_STVFLX,
    INS_STVFLXL,
    INS_STVFRX,
    INS_STVFRXL,
    INS_STVX,
    INS_STVXL,
    INS_STVEPX,
    INS_STVEPXL,
    INS_EVSTDDEPX,
    INS_EVSTDD,
    INS_EVSTDDX,
    INS_EVSTDH,
    INS_EVSTDHX,
    INS_EVSTDW,
    INS_EVSTDWX,
    INS_EVSTWHE,
    INS_EVSTWHO,
    INS_EVSTWHEX,
    INS_EVSTWHOX,
    INS_EVSTWWE,
    INS_EVSTWWO,
    INS_EVSTWWEX,
    INS_EVSTWWOX,
    INS_STW,
    INS_STWU,
    INS_STB,
    INS_STBU,
    INS_STH,
    INS_STHU,
    INS_STMW,
    INS_STFS,
    INS_STFSU,
    INS_STFD,
    INS_STFDU,
    INS_STD,
    INS_STDU,
)

LOAD_INSTRS = (
    INS_LBZX,
    INS_LHZX,
    INS_LWZX,
    INS_LDX,
    INS_LHAX,
    INS_LWAX,
    INS_LHAUX,
    INS_LWAUX,
    INS_LBZUX,
    INS_LHZUX,
    INS_LWZUX,
    INS_LDUX,
    INS_LFSUX,
    INS_LFSX,
    INS_LVEBX,
    INS_LVEHX,
    INS_LVEPX,
    INS_LVEPXL,
    INS_LVEWX,
    INS_LVEXBX,
    INS_LVEXHX,
    INS_LVEXWX,
    INS_LVX,
    INS_LVXL,
    INS_LVSL,
    INS_LVSM,
    INS_LVSR,
    INS_LVSWX,
    INS_LVSWXL,
    INS_LVTLX,
    INS_LVTLXL,
    INS_LVTRX,
    INS_LVTRXL,
    INS_EVLDDEPX,
    INS_EVLDD,
    INS_EVLDDX,
    INS_EVLDH,
    INS_EVLDHX,
    INS_EVLDW,
    INS_EVLDWX,
    INS_EVLHHESPLAT,
    INS_EVLHHESPLATX,
    INS_EVLHHOSSPLAT,
    INS_EVLHHOSSPLATX,
    INS_EVLHHOUSPLAT,
    INS_EVLHHOUSPLATX,
    INS_EVLWHE,
    INS_EVLWHEX,
    INS_EVLWHOS,
    INS_EVLWHOSX,
    INS_EVLWHOU,
    INS_EVLWHOUX,
    INS_EVLWHSPLAT,
    INS_EVLWHSPLATX,
    INS_EVLWWSPLAT,
    INS_EVLWWSPLATX,
    INS_LWZ,
    INS_LWZU,
    INS_LBZ,
    INS_LBZU,
    INS_LHZ,
    INS_LHZU,
    INS_LHA,
    INS_LHAU,
    INS_LMW,
    INS_LFS,
    INS_LFSU,
    INS_LFD,
    INS_LFDU,
    INS_LD,
    INS_LDU,
    INS_LWA,
)
