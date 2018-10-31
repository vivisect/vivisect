from const_gen import *

ENDIAN_LSB = 0
ENDIAN_MSB = 1

TYPE_NONE = 0
TYPE_REG =  1
TYPE_IMM =  2
TYPE_MEM =  3
TYPE_JMP =  4
TYPE_CR =   5

E_NONE =  0
E_X =     1
E_XL =    2
E_D =     3
E_D8 =    4
E_I16A =  5
E_SCI8 =  6
E_SCI8I = 7
E_I16L =  8
E_I16LS = 9
E_BD24 =  10
E_BD15 =  11
E_IA16 =  12
E_LI20 =  13
E_M =     14
E_XCR =   15
E_XLSP =  16
E_XRA =   17

E_MASK_X =    0x03FFF800
E_MASK_XL =   0x03FFF801
E_MASK_D =    0x01FFFFFF
E_MASK_D8 =   0x03FF00FF
E_MASK_I16A = 0x03FF07FF
E_MASK_SCI8 = 0x03FF07FF
E_MASK_I16L = 0x03FF07FF
E_MASK_BD24 = 0x03FFFFFE
E_MASK_BD15 = 0x000CFFFE
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


F_MASK_X =     0x03FFF800
F_MASK_XO =    0x03FFF800
F_MASK_EVX =   0x03FFF800
F_MASK_CMP =   0x039FF800
F_MASK_DCBF =  0x00FFF800
F_MASK_DCBL =  0x01FFF800
F_MASK_DCI =   0x00FFF800
F_MASK_EXT =   0x03FF0000
F_MASK_A =     0x01FFFFC0
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

for octidx in range(len(opcodetypes)):
    octype = opcodetypes[octidx]
    label = "INS_" + octype
    globals()[label] = octidx


FLAGS_LT_bitnum = 0
FLAGS_GT_bitnum = 1
FLAGS_EQ_bitnum = 2
FLAGS_SO_bitnum = 3

FLAGS_LT = 1 << FLAGS_LT_bitnum
FLAGS_GT = 1 << FLAGS_GT_bitnum
FLAGS_EQ = 1 << FLAGS_EQ_bitnum
FLAGS_SO = 1 << FLAGS_SO_bitnum
