from const_gen import *

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
TYPE_SIMM = 4
TYPE_MEM =  5
TYPE_JMP =  6
TYPE_CR =   7

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
E_IA16 =  14
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
E_MASK_IA16 = 0x03FF07FF
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

OEMODE_LEGACY = 0
OEMODE_ADDSUBNEG = 1
OEMODE_MULDIV = 2

# VLE opcode types #FIXME: coordinate between VLE and const_gen
opcodetypes = (
    'ILL',

    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'SHR',
    'SHL',
    'ROR',

    'AND',
    'OR',
    'XOR',
    'NOR',
    'NOT',

    'IO',
    'LOAD',
    'STORE',
    'MOV',

    'CMP',
    'JMP',
    'CJMP',
    'CALL',
    'CCALL',
    'RJMP',
    'RCALL',
    'RET',

    'SYNC',
    'SWI',
    'TRAP',
    )
VLE_INST_OFFSET = 0x1000
for octidx in range(len(opcodetypes)):
    octype = opcodetypes[octidx]
    label = "INS_" + octype
    globals()[label] = octidx + VLE_INST_OFFSET


# special instruction aliases:
INS_VMR = inscounter ; inscounter += 1

# flag bit numbers and masks
FLAGS_LT_bitnum = 3-0   # noted to tie back to the manual's referencing this as bit 0
FLAGS_GT_bitnum = 3-1
FLAGS_EQ_bitnum = 3-2
FLAGS_SO_bitnum = 3-3

FLAGS_LT = 1 << FLAGS_LT_bitnum
FLAGS_GT = 1 << FLAGS_GT_bitnum
FLAGS_EQ = 1 << FLAGS_EQ_bitnum
FLAGS_SO = 1 << FLAGS_SO_bitnum

XERFLAG_SO_bitnum = 2-0
XERFLAG_OV_bitnum = 2-1
XERFLAG_CA_bitnum = 2-2

XERFLAG_SO_LOW = 1 << XERFLAG_SO_bitnum
XERFLAG_OV_LOW = 1 << XERFLAG_OV_bitnum
XERFLAG_CA_LOW = 1 << XERFLAG_CA_bitnum
XERFLAG_SO = 1 << (XERFLAG_SO_bitnum + 29)
XERFLAG_OV = 1 << (XERFLAG_OV_bitnum + 29)
XERFLAG_CA = 1 << (XERFLAG_CA_bitnum + 29)

# roll-up architecture CATEGORIES
CAT_PPC_SERVER = CAT_ALTIVEC =   CAT_NONE | CAT_EMBEDDED | CAT_E | CAT_V | CAT_64 | CAT_E_ED | CAT_WT | CAT_E_PD | CAT_E_CL | CAT_E_PC | CAT_FP | CAT_FP_R | CAT_E_PM | CAT_ER | CAT_EM_TM
CAT_PPC_EMBEDDED =   CAT_SPE =       CAT_NONE | CAT_E | CAT_E_ED | CAT_E_HV | CAT_E_PD | CAT_E_CL | CAT_E_PC | CAT_E_DC | CAT_E_PM | CAT_SP | CAT_SP_FV | CAT_SP_FS | CAT_SP_FD | CAT_ER | CAT_EM_TM | CAT_DS | CAT_FP | CAT_DEO | CAT_FP_R | CAT_WT | CAT_64 | CAT_EMBEDDED | CAT_ISAT

# mask to clear out a 4-bit part of the 32-bit CR register about to be written
cr_mask = [(0xffffffff & ~(0xf<<(4*x))) for x in range(8)]

