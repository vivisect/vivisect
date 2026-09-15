import envi

SEG_FLASH = 0
SEG_XRAM = 1
SEG_IRAM = 2
SEG_SFR = 3
SEG_IRAM2 = 4		# funky CC1110 splits IRAM in two parts.

SEG_FLASH_BASE      = 0
#SEG_XRAM_BASE       = 0x10000
SEG_XRAM_BASE       = 0
SEG_IRAM_BASE       = SEG_XRAM_BASE  + 0xff00
SEG_SFR_BASE        = SEG_XRAM_BASE  + 0xdf00
SEG_f00barRAM_BASE  = SEG_XRAM_BASE  + 0xf000

seglist_8051 = ( 
    (0x0,0x104,SEG_IRAM_BASE, "IRAM"),
    (0x0,0x100,SEG_SFR_BASE, "SFR"),  #sfr is really 0x80-0xff, 0-0x80 are "Hardware RADIO/I2S Registers"
)

seglist_1110 = ( 
    (0x0,0x2000,SEG_FLASH_BASE, "FLASH-PROG-MEM"), 
    (0x0,0x10004,SEG_XRAM_BASE, "XRAM"), 
    (0x0,0x104,SEG_IRAM_BASE, "IRAM"),
    (0x0,0x100,SEG_SFR_BASE, "SFR"),  #sfr is really 0x80-0xff, 0-0x80 are "Hardware RADIO/I2S Registers"
    (0x0,0x300,SEG_f00barRAM_BASE, "f00barRAM"),  #wtf?  really?  frick.
)

seglist_2430 = ( 
    (0x0,0xdf00,SEG_FLASH_BASE, "FLASH-PROG-MEM"), 
    (0x0,0x10004,SEG_XRAM_BASE, "XRAM"), 
    (0x0,0x104,SEG_IRAM_BASE, "IRAM"),
    (0x0,0x100,SEG_SFR_BASE, "SFR"),  #sfr is really 0x80-0xff, 0-0x80 are "Hardware RADIO/I2S Registers"
)


IV_RESET = 0
IV_IE0 = 1
IV_TF0 = 2
IV_IE1 = 3
IV_TF1 = 4
IV_RTIO = 5
IV_TF2 = 6

interrupt_vectors = {
    IV_RESET:   0x0,
    IV_IE0:     0x3,    # External Interrupt 0
    IV_TF0:     0xb,    # Timer 0 overflow
    IV_IE1:     0x13,   # External Interrupt 1
    IV_TF1:     0x1b,   # Timer 1 overflow
    IV_RTIO:    0x23,   # Serial Channel 0
    IV_TF2:     0x2b,   # Timer 2 overflow / ext. reload
    }

# OPCODE TYPE NUMBER COMPONENTS
OPTYPE_MASK                       = 0x00000F00
OPTYPE_Boolean_Manipulations      = 0x00000100
OPTYPE_Program_Branches           = 0x00000200
OPTYPE_Data_Transfer_Operations   = 0x00000300
OPTYPE_Logic_Operations           = 0x00000400
OPTYPE_Arithmetic_Operations      = 0x00000500

# OPERAND NUMBER COMPONENTS
OPERANDMASK      = 0xFFFFF
OPERANDREGMASK   = 0x0F000
OPERANDREGLOC    = 12
OPERANDFLAGMASK  = 0x00F00
OPERANDFLAGLOC   = 8
OPERANDTYPEMASK  = 0x000FF

OPERANDSIZE_8    = 0x00100
OPERANDSIZE_16   = 0x00200
OP_W             = 0x00400
OP_R             = 0x00800

ADDRMODE_DATA    = 0x10000
ADDRMODE_CODE    = 0x20000

### FIXME: THIS IS TEH CRAP.  Better Registers in regs.py, but these are required for this table.
R0   = 0x0<<OPERANDREGLOC
R1   = 0x1<<OPERANDREGLOC
R2   = 0x2<<OPERANDREGLOC
R3   = 0x3<<OPERANDREGLOC
R4   = 0x4<<OPERANDREGLOC
R5   = 0x5<<OPERANDREGLOC
R6   = 0x6<<OPERANDREGLOC
R7   = 0x7<<OPERANDREGLOC
A    = 0x8<<OPERANDREGLOC
B    = 0x9<<OPERANDREGLOC
DPTR = 0xa<<OPERANDREGLOC
bits = 0xb<<OPERANDREGLOC
PC   = 0xc<<OPERANDREGLOC
SP   = 0xd<<OPERANDREGLOC
BP   = 0xe<<OPERANDREGLOC

REGISTERS = [       # each register represents one byte in a register bank.  reg-banks are stored at memlocs 0h, 8h, 10h, and 18h, and are selectable by the RS0 and RS1 bits in the PSW
    "R0", #0
    "R1", #1
    "R2", #2
    "R3", #3
    "R4", #4
    "R5", #5
    "R6", #6
    "R7", #7
    "A",    # e0h
    "B",    #
    "DPTR",
    "bits",
    "PC",
    "SP",
    "BP",
    ]

FLAGS = [   # as defined by the Program Status Word (PSW)
    "P",
    "user-def-flag",
    "OV",   # Overflow
    "RS0",  # register bank select bit 0
    "RS1",  # register bank select bit 1
    "F",    # "general purpose status flag"
    "AC",   # AC
    "C",    # Carry Bit
    ]

# flags
P       = 0
OV      = 2
RS0     = 3
RS1     = 4
F       = 5
AC      = 6
C       = 7

# Program Memory Addressing Types (used with o.scale to indicate relative addressing or not)
ADDR_DIRECT = 1
ADDR_REL    = 2


OPERANDS = { # ( ADDRMODE_TYPE, OP_str, extralines, extrabytes, target_size)    (This was used to generate these tables)
    "Rn":       (ADDRMODE_DATA, "OP_REGISTER", 7, 0, 1),
    "direct":   (ADDRMODE_DATA, "OP_DIRECT", 0, 1, 1),
    "@Ri":      (ADDRMODE_DATA, "OP_REG_INDIRECT", 1, 0, 1),       # OP_REGMEM
    "#data":    (ADDRMODE_DATA, "OP_IMMEDIATE | OPERANDSIZE_8", 0, 1, 1),
    "#data16":  (ADDRMODE_DATA, "OP_IMMEDIATE | OPERANDSIZE_16", 0, 2, 2),
    "bit":      (ADDRMODE_DATA, "OP_bit", 0, 1, 1),
    "A":        (ADDRMODE_DATA, "OP_A", 0, 0, 1),                  # OP_REG
    "B":        (ADDRMODE_DATA, "OP_B", 0, 0, 1),                  # OP_REG
    "C":        (ADDRMODE_DATA, "OP_C", 0, 0, 1),                  # Carry flag    OP_FLAGS
    "/bit":     (ADDRMODE_DATA, "OP_comp_bit", 0, 1, 1),           # Complement of bit
    "DPTR":     (ADDRMODE_DATA, "OP_DPTR", 0, 0, 2),               #??????
    "@A+DPTR":  (ADDRMODE_DATA, "OP_ACC_DPTR_INDIRECT", 0, 0, 2),  # OP_SIBMEM???
    "@A+PC":    (ADDRMODE_DATA, "OP_ACC_PC_INDIRECT", 0, 0, 2),    # OP_SIBMEM???
    "@DPTR":    (ADDRMODE_DATA, "OP_DPTR_INDIRECT", 0, 0, 1),      # OP_REGMEM???
    "addr16":   (ADDRMODE_CODE, "OP_ADDR16", 8, 1, 1),             # OP_
    "addr11":   (ADDRMODE_CODE, "OP_ADDR11", 8, 1, 1),
    "rel":      (ADDRMODE_CODE, "OP_REL", 0, 1, 1),
    }

OP_None                           = 0x0
OP_A                              = 0x00000060
OP_C                              = 0x00000061
OP_B                              = 0x00000062
OP_REL                            = 0x00000063
OP_DPTR                           = 0x00000064
OP_ADDR16                         = 0x00000065
OP_ADDR11                         = 0x00000066
OP_DPTR_INDIRECT                  = 0x00000067
OP_DIRECT                         = 0x00000068
OP_ACC_DPTR_INDIRECT              = 0x00000069
OP_comp_bit                       = 0x0000006a
OP_REGISTER                       = 0x0000006b
OP_REG_INDIRECT                   = 0x0000006c
OP_bit                            = 0x0000006d
OP_ACC_PC_INDIRECT                = 0x0000006e
OP_IMMEDIATE                      = 0x0000006f
OP_IMM8                           = OP_IMMEDIATE | OPERANDSIZE_8
OP_IMM16                          = OP_IMMEDIATE | OPERANDSIZE_16

OPERANDS_BY_OP = {}
for o in OPERANDS.values():
    #print o
    OPERANDS_BY_OP[eval(o[1])&OPERANDTYPEMASK ] = o





INS_None                          = 0x00000000
INS_ACALL                         = OPTYPE_Program_Branches           | 0x1
INS_ADD                           = OPTYPE_Arithmetic_Operations      | 0x1
INS_ADDC                          = OPTYPE_Arithmetic_Operations      | 0x2
INS_AJMP                          = OPTYPE_Program_Branches           | 0x2
INS_ANL                           = OPTYPE_Logic_Operations           | 0x1
INS_CJNE                          = OPTYPE_Program_Branches           | 0x3
INS_CLR                           = OPTYPE_Boolean_Manipulations      | 0x1
INS_CPL                           = OPTYPE_Boolean_Manipulations      | 0x2
INS_DA                            = OPTYPE_Arithmetic_Operations      | 0x3
INS_DEC                           = OPTYPE_Arithmetic_Operations      | 0x4
INS_DIV                           = OPTYPE_Arithmetic_Operations      | 0x5
INS_DJNZ                          = OPTYPE_Program_Branches           | 0x4
INS_INC                           = OPTYPE_Arithmetic_Operations      | 0x6
INS_JB                            = OPTYPE_Program_Branches           | 0x5
INS_JBC                           = OPTYPE_Program_Branches           | 0x6
INS_JC                            = OPTYPE_Program_Branches           | 0x7
INS_JMP                           = OPTYPE_Program_Branches           | 0x8
INS_JNB                           = OPTYPE_Program_Branches           | 0x9
INS_JNC                           = OPTYPE_Program_Branches           | 0xa
INS_JNZ                           = OPTYPE_Program_Branches           | 0xb
INS_JZ                            = OPTYPE_Program_Branches           | 0xc
INS_LCALL                         = OPTYPE_Program_Branches           | 0xd
INS_LJMP                          = OPTYPE_Program_Branches           | 0xe
INS_MOV                           = OPTYPE_Data_Transfer_Operations   | 0x1
INS_MOVC                          = OPTYPE_Data_Transfer_Operations   | 0x2
INS_MOVX                          = OPTYPE_Data_Transfer_Operations   | 0x3
INS_MUL                           = OPTYPE_Arithmetic_Operations      | 0x7
INS_NOP                           = OPTYPE_Program_Branches           | 0xf
INS_ORL                           = OPTYPE_Logic_Operations           | 0x2
INS_POP                           = OPTYPE_Data_Transfer_Operations   | 0x4
INS_PUSH                          = OPTYPE_Data_Transfer_Operations   | 0x5
INS_RET                           = OPTYPE_Program_Branches           | 0x10
INS_RETI                          = OPTYPE_Program_Branches           | 0x11
INS_RL                            = OPTYPE_Logic_Operations           | 0x3
INS_RLC                           = OPTYPE_Logic_Operations           | 0x4
INS_RR                            = OPTYPE_Logic_Operations           | 0x5
INS_RRC                           = OPTYPE_Logic_Operations           | 0x6
INS_SETB                          = OPTYPE_Boolean_Manipulations      | 0x3
INS_SJMP                          = OPTYPE_Program_Branches           | 0x12
INS_SUBB                          = OPTYPE_Arithmetic_Operations      | 0x8
INS_SWAP                          = OPTYPE_Logic_Operations           | 0x7
INS_XCH                           = OPTYPE_Data_Transfer_Operations   | 0x6
INS_XCHD                          = OPTYPE_Data_Transfer_Operations   | 0x7
INS_XRL                           = OPTYPE_Logic_Operations           | 0x8


nofall_types = [
    INS_AJMP,
    INS_LJMP,
    INS_RET,
    INS_RETI,
    INS_JMP,
]
branch_types = [    # if not also in nofall, it's a conditional branch
    INS_NOP,
    INS_AJMP,
    INS_LJMP,
    INS_JBC,
    INS_JB,
    INS_RET,
    INS_JNB,
    INS_RETI,
    INS_JC,
    INS_JNC,
    INS_JZ,
    INS_JNZ,
    INS_JMP,
    INS_SJMP,
    INS_CJNE,
    INS_DJNZ,
]
call_types = [
    INS_ACALL,
    INS_LCALL,
]

brnofall_types = [op for op in nofall_types if op in branch_types]

op_flags = {}
op_flags.update({op: envi.IF_CALL for op in call_types})
op_flags.update({op: envi.IF_NOFALL for op in nofall_types})
op_flags.update({op: envi.IF_BRANCH | envi.IF_COND for op in branch_types})
op_flags.update({op: envi.IF_BRANCH | envi.IF_NOFALL for op in brnofall_types})

sizenames = (None, "BYTE ","WORD ",None,"DWORD ")

OPTYPE_REG = 0x0
OPTYPE_IMM = 0x1
OPTYPE_INDEXED = 0x2
OPTYPE_INDIRECT = 0x3
OPTYPE_DIRECT = 0x4
OPTYPE_ADDR = 0x5
OPTYPE_PCREL = 0x6
OPTYPE_BIT = 0x7

