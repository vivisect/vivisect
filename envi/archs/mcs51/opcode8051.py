import envi

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



table_main = (
    ( INS_NOP, "nop", "No operation", 0x0, 1, 1, ( OP_None, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0x1, 2, 3, ( OP_ADDR11, ) ),
    ( INS_LJMP, "ljmp", "Long jump", 0x2, 3, 4, ( OP_ADDR16, ) ),
    ( INS_RR, "rr", "Rotate accumulator right", 0x3, 1, 1, ( OP_A, ) ),
    ( INS_INC, "inc", "Increment accumulator", 0x4, 1, 1, ( OP_A, ) ),
    ( INS_INC, "inc", "Increment direct byte", 0x5, 2, 3, ( OP_DIRECT, ) ),
    ( INS_INC, "inc", "Increment indirect RAM", 0x6, 1, 3, ( OP_REG_INDIRECT | R0, ) ),
    ( INS_INC, "inc", "Increment indirect RAM", 0x7, 1, 3, ( OP_REG_INDIRECT | R1, ) ),
    ( INS_INC, "inc", "Increment register", 0x8, 1, 2, ( OP_REGISTER | R0, ) ),
    ( INS_INC, "inc", "Increment register", 0x9, 1, 2, ( OP_REGISTER | R1, ) ),
    ( INS_INC, "inc", "Increment register", 0xa, 1, 2, ( OP_REGISTER | R2, ) ),
    ( INS_INC, "inc", "Increment register", 0xb, 1, 2, ( OP_REGISTER | R3, ) ),
    ( INS_INC, "inc", "Increment register", 0xc, 1, 2, ( OP_REGISTER | R4, ) ),
    ( INS_INC, "inc", "Increment register", 0xd, 1, 2, ( OP_REGISTER | R5, ) ),
    ( INS_INC, "inc", "Increment register", 0xe, 1, 2, ( OP_REGISTER | R6, ) ),
    ( INS_INC, "inc", "Increment register", 0xf, 1, 2, ( OP_REGISTER | R7, ) ),
    ( INS_JBC, "jbc", "Jump if direct bit is set and clear bit", 0x10, 3, 4, ( OP_bit,OP_DIRECT,OP_REL, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0x11, 2, 6, ( OP_ADDR11, ) ),
    ( INS_LCALL, "lcall", "Long subroutine call", 0x12, 3, 6, ( OP_ADDR16, ) ),
    ( INS_RRC, "rrc", "Rotate accumulator right through carry", 0x13, 1, 1, ( OP_A, ) ),
    ( INS_DEC, "dec", "Decrement accumulator", 0x14, 1, 1, ( OP_A, ) ),
    ( INS_DEC, "dec", "Decrement direct byte", 0x15, 2, 3, ( OP_DIRECT, ) ),
    ( INS_DEC, "dec", "Decrement indirect RAM", 0x16, 1, 3, ( OP_REG_INDIRECT | R0, ) ),
    ( INS_DEC, "dec", "Decrement indirect RAM", 0x17, 1, 3, ( OP_REG_INDIRECT | R1, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x18, 1, 2, ( OP_REGISTER | R0, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x19, 1, 2, ( OP_REGISTER | R1, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1a, 1, 2, ( OP_REGISTER | R2, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1b, 1, 2, ( OP_REGISTER | R3, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1c, 1, 2, ( OP_REGISTER | R4, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1d, 1, 2, ( OP_REGISTER | R5, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1e, 1, 2, ( OP_REGISTER | R6, ) ),
    ( INS_DEC, "dec", "Decrement register", 0x1f, 1, 2, ( OP_REGISTER | R7, ) ),
    ( INS_JB, "jb", "Jump if direct bit is set", 0x20, 3, 4, ( OP_bit,OP_REL, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0x21, 2, 3, ( OP_ADDR11, ) ),
    ( INS_RET, "ret", "Return from subroutine", 0x22, 1, 4, ( OP_None, ) ),
    ( INS_RL, "rl", "Rotate accumulator left", 0x23, 1, 1, ( OP_A, ) ),
    ( INS_ADD, "add", "Add immediate data to accumulator", 0x24, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ADD, "add", "Add direct byte to accumulator", 0x25, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_ADD, "add", "Add indirect RAM to accumulator", 0x26, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_ADD, "add", "Add indirect RAM to accumulator", 0x27, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x28, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x29, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_ADD, "add", "Add register to accumulator", 0x2f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_JNB, "jnb", "Jump if direct bit is not set", 0x30, 3, 4, ( OP_bit,OP_REL, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0x31, 2, 6, ( OP_ADDR11, ) ),
    ( INS_RETI, "reti", "Return from interrupt", 0x32, 1, 4, ( OP_None, ) ),
    ( INS_RLC, "rlc", "Rotate accumulator left through carry", 0x33, 1, 1, ( OP_A, ) ),
    ( INS_ADDC, "addc", "Add immediate data to A with carry flag", 0x34, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ADDC, "addc", "Add direct byte to A with carry flag", 0x35, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_ADDC, "addc", "Add indirect RAM to A with carry flag", 0x36, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_ADDC, "addc", "Add indirect RAM to A with carry flag", 0x37, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x38, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x39, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_ADDC, "addc", "Add register to accumulator with carry flag", 0x3f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_JC, "jc", "Jump if carry flag is set", 0x40, 2, 3, ( OP_REL, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0x41, 2, 3, ( OP_ADDR11, ) ),
    ( INS_ORL, "orl", "OR accumulator to direct byte", 0x42, 2, 3, ( OP_DIRECT,OP_A, ) ),
    ( INS_ORL, "orl", "OR immediate data to direct byte", 0x43, 3, 4, ( OP_DIRECT,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ORL, "orl", "OR immediate data to accumulator", 0x44, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ORL, "orl", "OR direct byte to accumulator", 0x45, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_ORL, "orl", "OR indirect RAM to accumulator", 0x46, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_ORL, "orl", "OR indirect RAM to accumulator", 0x47, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x48, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x49, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_ORL, "orl", "OR register to accumulator", 0x4f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_JNC, "jnc", "Jump if carry flag is not set", 0x50, 2, 3, ( OP_None, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0x51, 2, 6, ( OP_ADDR11, ) ),
    ( INS_ANL, "anl", "AND accumulator to direct byte", 0x52, 2, 3, ( OP_DIRECT,OP_A, ) ),
    ( INS_ANL, "anl", "AND immediate data to direct byte", 0x53, 3, 4, ( OP_DIRECT,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ANL, "anl", "AND immediate data to accumulator", 0x54, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_ANL, "anl", "AND direct byte to accumulator", 0x55, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_ANL, "anl", "AND indirect RAM to accumulator", 0x56, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_ANL, "anl", "AND indirect RAM to accumulator", 0x57, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x58, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x59, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_ANL, "anl", "AND register to accumulator", 0x5f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_JZ, "jz", "Jump if accumulator is zero", 0x60, 2, 3, ( OP_REL, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0x61, 2, 3, ( OP_ADDR11, ) ),
    ( INS_XRL, "xrl", "Exclusive OR accumulator to direct byte", 0x62, 2, 3, ( OP_DIRECT,OP_A, ) ),
    ( INS_XRL, "xrl", "Exclusive OR immediate data to direct byte", 0x63, 3, 4, ( OP_DIRECT,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_XRL, "xrl", "Exclusive OR immediate data to accumulator", 0x64, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_XRL, "xrl", "Exclusive OR direct byte to accumulator", 0x65, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_XRL, "xrl", "Exclusive OR indirect RAM to accumulator", 0x66, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_XRL, "xrl", "Exclusive OR indirect RAM to accumulator", 0x67, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x68, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x69, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_XRL, "xrl", "Exclusive OR register to accumulator", 0x6f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_JNZ, "jnz", "Jump if accumulator is not zero", 0x70, 2, 3, ( OP_REL, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0x71, 2, 6, ( OP_ADDR11, ) ),
    ( INS_ORL, "orl", "OR direct bit to carry flag", 0x72, 2, 2, ( OP_C,OP_bit, ) ),
    ( INS_JMP, "jmp", "Jump indirect relative to the DPTR", 0x73, 1, 2, ( OP_ACC_DPTR_INDIRECT, ) ),
    ( INS_MOV, "mov", "Move immediate data to accumulator", 0x74, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to direct byte", 0x75, 3, 3, ( OP_DIRECT,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to indirect RAM", 0x76, 2, 3, ( OP_REG_INDIRECT | R0,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to indirect RAM", 0x77, 2, 3, ( OP_REG_INDIRECT | R1,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x78, 2, 2, ( OP_REGISTER | R0,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x79, 2, 2, ( OP_REGISTER | R1,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7a, 2, 2, ( OP_REGISTER | R2,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7b, 2, 2, ( OP_REGISTER | R3,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7c, 2, 2, ( OP_REGISTER | R4,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7d, 2, 2, ( OP_REGISTER | R5,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7e, 2, 2, ( OP_REGISTER | R6,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_MOV, "mov", "Move immediate data to register", 0x7f, 2, 2, ( OP_REGISTER | R7,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_SJMP, "sjmp", "Short jump (relative addr.)", 0x80, 2, 3, ( OP_REL, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0x81, 2, 3, ( OP_ADDR11, ) ),
    ( INS_ANL, "anl", "AND direct bit to carry flag", 0x82, 2, 2, ( OP_C,OP_bit, ) ),
    ( INS_MOVC, "movc", "Move code byte relative to PC to accumulator", 0x83, 1, 3, ( OP_A,OP_ACC_PC_INDIRECT, ) ),
    ( INS_DIV, "div", "Divide A by B", 0x84, 1, 5, ( OP_None, ) ),
    ( INS_MOV, "mov", "Move direct byte to direct byte", 0x85, 3, 4, ( OP_DIRECT | OP_W,OP_DIRECT | OP_R, ) ),
    ( INS_MOV, "mov", "Move indirect RAM to direct byte", 0x86, 2, 4, ( OP_DIRECT,OP_REG_INDIRECT | R0, ) ),
    ( INS_MOV, "mov", "Move indirect RAM to direct byte", 0x87, 2, 4, ( OP_DIRECT,OP_REG_INDIRECT | R1, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x88, 2, 3, ( OP_DIRECT,OP_REGISTER | R0, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x89, 2, 3, ( OP_DIRECT,OP_REGISTER | R1, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8a, 2, 3, ( OP_DIRECT,OP_REGISTER | R2, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8b, 2, 3, ( OP_DIRECT,OP_REGISTER | R3, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8c, 2, 3, ( OP_DIRECT,OP_REGISTER | R4, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8d, 2, 3, ( OP_DIRECT,OP_REGISTER | R5, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8e, 2, 3, ( OP_DIRECT,OP_REGISTER | R6, ) ),
    ( INS_MOV, "mov", "Move register to direct byte", 0x8f, 2, 3, ( OP_DIRECT,OP_REGISTER | R7, ) ),
    ( INS_MOV, "mov", "Load data pointer with a 16-bit constant", 0x90, 3, 3, ( OP_DPTR,OP_IMMEDIATE | OPERANDSIZE_16, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0x91, 2, 6, ( OP_ADDR11, ) ),
    ( INS_MOV, "mov", "Move carry flag to direct bit", 0x92, 2, 3, ( OP_bit,OP_C, ) ),
    ( INS_MOVC, "movc", "Move code byte relative to DPTR to accumulator", 0x93, 1, 3, ( OP_A,OP_ACC_DPTR_INDIRECT, ) ),
    ( INS_SUBB, "subb", "Subtract immediate data from A with borrow", 0x94, 2, 2, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8, ) ),
    ( INS_SUBB, "subb", "Subtract direct byte from A with borrow", 0x95, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_SUBB, "subb", "Subtract indirect RAM from A with borrow", 0x96, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_SUBB, "subb", "Subtract indirect RAM from A with borrow", 0x97, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x98, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x99, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9a, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9b, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9c, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9d, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9e, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_SUBB, "subb", "Subtract register from A with borrow", 0x9f, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_ORL, "orl", "OR complement of direct bit to carry", 0xa0, 2, 2, ( OP_C,OP_comp_bit, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0xa1, 2, 3, ( OP_ADDR11, ) ),
    ( INS_MOV, "mov", "Move direct bit to carry flag", 0xa2, 2, 2, ( OP_C,OP_bit, ) ),
    ( INS_INC, "inc", "Increment data pointer", 0xa3, 1, 1, ( OP_DPTR, ) ),
    ( INS_MUL, "mul", "Multiply A and B", 0xa4, 1, 5, ( OP_A,OP_B, ) ),
    ( INS_None, "reserved", "reserved instruction", 0xa5, 1, 0, () ),
    ( INS_MOV, "mov", "Move direct byte to indirect RAM", 0xa6, 2, 5, ( OP_REG_INDIRECT | R0,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to indirect RAM", 0xa7, 2, 5, ( OP_REG_INDIRECT | R1,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xa8, 2, 4, ( OP_REGISTER | R0,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xa9, 2, 4, ( OP_REGISTER | R1,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xaa, 2, 4, ( OP_REGISTER | R2,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xab, 2, 4, ( OP_REGISTER | R3,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xac, 2, 4, ( OP_REGISTER | R4,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xad, 2, 4, ( OP_REGISTER | R5,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xae, 2, 4, ( OP_REGISTER | R6,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move direct byte to register", 0xaf, 2, 4, ( OP_REGISTER | R7,OP_DIRECT, ) ),
    ( INS_ANL, "anl", "AND complement of direct bit to carry", 0xb0, 2, 2, ( OP_C,OP_comp_bit, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0xb1, 2, 6, ( OP_ADDR11, ) ),
    ( INS_CPL, "cpl", "Complement direct bit", 0xb2, 2, 3, ( OP_bit, ) ),
    ( INS_CPL, "cpl", "Complement carry flag", 0xb3, 1, 1, ( OP_C, ) ),
    ( INS_CJNE, "cjne", "Compare immediate to A and jump if not equal", 0xb4, 3, 4, ( OP_A,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare direct byte to A and jump if not equal", 0xb5, 3, 4, ( OP_A,OP_DIRECT,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to ind. and jump if not equal", 0xb6, 3, 4, ( OP_REG_INDIRECT | R0,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to ind. and jump if not equal", 0xb7, 3, 4, ( OP_REG_INDIRECT | R1,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xb8, 3, 4, ( OP_REGISTER | R0,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xb9, 3, 4, ( OP_REGISTER | R1,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xba, 3, 4, ( OP_REGISTER | R2,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xbb, 3, 4, ( OP_REGISTER | R3,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xbc, 3, 4, ( OP_REGISTER | R4,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xbd, 3, 4, ( OP_REGISTER | R5,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xbe, 3, 4, ( OP_REGISTER | R6,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_CJNE, "cjne", "Compare immed. to reg. and jump if not equal", 0xbf, 3, 4, ( OP_REGISTER | R7,OP_IMMEDIATE | OPERANDSIZE_8,OP_REL, ) ),
    ( INS_PUSH, "push", "Push direct byte onto stack", 0xc0, 2, 4, ( OP_DIRECT, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0xc1, 2, 3, ( OP_ADDR11, ) ),
    ( INS_CLR, "clr", "Clear direct bit", 0xc2, 2, 3, ( OP_bit, ) ),
    ( INS_CLR, "clr", "Clear carry flag", 0xc3, 1, 1, ( OP_C, ) ),
    ( INS_SWAP, "swap", "Swap nibbles within the accumulator", 0xc4, 1, 1, ( OP_A, ) ),
    ( INS_XCH, "xch", "Exchange direct byte with accumulator", 0xc5, 2, 3, ( OP_A,OP_DIRECT, ) ),
    ( INS_XCH, "xch", "Exchange indirect RAM with accumulator", 0xc6, 1, 3, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_XCH, "xch", "Exchange indirect RAM with accumulator", 0xc7, 1, 3, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xc8, 1, 2, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xc9, 1, 2, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xca, 1, 2, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xcb, 1, 2, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xcc, 1, 2, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xcd, 1, 2, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xce, 1, 2, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_XCH, "xch", "Exchange register with accumulator", 0xcf, 1, 2, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_POP, "pop", "Pop direct byte from stack", 0xd0, 2, 3, ( OP_DIRECT, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0xd1, 2, 6, ( OP_ADDR11, ) ),
    ( INS_SETB, "setb", "Set direct bit", 0xd2, 2, 3, ( OP_bit, ) ),
    ( INS_SETB, "setb", "Set carry flag", 0xd3, 1, 1, ( OP_C, ) ),
    ( INS_DA, "da", "Decimal adjust accumulator", 0xd4, 1, 1, ( OP_A, ) ),
    ( INS_DJNZ, "djnz", "Decrement direct byte and jump if not zero", 0xd5, 3, 4, ( OP_DIRECT,OP_REL, ) ),
    ( INS_XCHD, "xchd", "Exchange low-order nibble indirect RAM with A", 0xd6, 1, 3, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_XCHD, "xchd", "Exchange low-order nibble indirect RAM with A", 0xd7, 1, 3, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xd8, 2, 3, ( OP_REGISTER | R0,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xd9, 2, 3, ( OP_REGISTER | R1,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xda, 2, 3, ( OP_REGISTER | R2,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xdb, 2, 3, ( OP_REGISTER | R3,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xdc, 2, 3, ( OP_REGISTER | R4,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xdd, 2, 3, ( OP_REGISTER | R5,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xde, 2, 3, ( OP_REGISTER | R6,OP_REL, ) ),
    ( INS_DJNZ, "djnz", "Decrement register and jump if not zero", 0xdf, 2, 3, ( OP_REGISTER | R7,OP_REL, ) ),
    ( INS_MOVX, "movx", "Move external RAM (16-bit addr.) to A", 0xe0, 1, 03-10, ( OP_A,OP_DPTR_INDIRECT, ) ),
    ( INS_AJMP, "ajmp", "Absolute jump", 0xe1, 2, 3, ( OP_ADDR11, ) ),
    ( INS_MOVX, "movx", "Move external RAM (8-bit addr.) to A", 0xe2, 1, 03-10, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_MOVX, "movx", "Move external RAM (8-bit addr.) to A", 0xe3, 1, 03-10, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_CLR, "clr", "Clear accumulator", 0xe4, 1, 1, ( OP_A, ) ),
    ( INS_MOV, "mov", "Move direct byte to accumulator", 0xe5, 2, 2, ( OP_A,OP_DIRECT, ) ),
    ( INS_MOV, "mov", "Move indirect RAM to accumulator", 0xe6, 1, 2, ( OP_A,OP_REG_INDIRECT | R0, ) ),
    ( INS_MOV, "mov", "Move indirect RAM to accumulator", 0xe7, 1, 2, ( OP_A,OP_REG_INDIRECT | R1, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xe8, 1, 1, ( OP_A,OP_REGISTER | R0, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xe9, 1, 1, ( OP_A,OP_REGISTER | R1, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xea, 1, 1, ( OP_A,OP_REGISTER | R2, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xeb, 1, 1, ( OP_A,OP_REGISTER | R3, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xec, 1, 1, ( OP_A,OP_REGISTER | R4, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xed, 1, 1, ( OP_A,OP_REGISTER | R5, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xee, 1, 1, ( OP_A,OP_REGISTER | R6, ) ),
    ( INS_MOV, "mov", "Move register to accumulator", 0xef, 1, 1, ( OP_A,OP_REGISTER | R7, ) ),
    ( INS_MOVX, "movx", "Move A to external RAM (16-bit addr.)", 0xf0, 1, 04-11, ( OP_DPTR_INDIRECT,OP_A, ) ),
    ( INS_ACALL, "acall", "Absolute subroutine call", 0xf1, 2, 6, ( OP_ADDR11, ) ),
    ( INS_MOVX, "movx", "Move A to external RAM (8-bit addr.)", 0xf2, 1, 04-11, ( OP_REG_INDIRECT | R0,OP_A, ) ),
    ( INS_MOVX, "movx", "Move A to external RAM (8-bit addr.)", 0xf3, 1, 04-11, ( OP_REG_INDIRECT | R1,OP_A, ) ),
    ( INS_CPL, "cpl", "Complement accumulator", 0xf4, 1, 1, ( OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to direct byte", 0xf5, 2, 3, ( OP_DIRECT,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to indirect RAM", 0xf6, 1, 3, ( OP_REG_INDIRECT | R0,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to indirect RAM", 0xf7, 1, 3, ( OP_REG_INDIRECT | R1,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xf8, 1, 2, ( OP_REGISTER | R0,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xf9, 1, 2, ( OP_REGISTER | R1,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xfa, 1, 2, ( OP_REGISTER | R2,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xfb, 1, 2, ( OP_REGISTER | R3,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xfc, 1, 2, ( OP_REGISTER | R4,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xfd, 1, 2, ( OP_REGISTER | R5,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xfe, 1, 2, ( OP_REGISTER | R6,OP_A, ) ),
    ( INS_MOV, "mov", "Move accumulator to register", 0xff, 1, 2, ( OP_REGISTER | R7,OP_A, ) ),
    )
