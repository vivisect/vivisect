# Generated from:
#   b'https://github.com/riscv/riscv-isa-manual'
#   b'tags/draft-20221004-28b46de'
#   b'28b46de77ca7fb94ffcf6cf669cc27269f6013de'

import enum
from collections import namedtuple


class RISCV_FORM(enum.IntEnum):
    R_TYPE = 0
    I_TYPE = 1
    S_TYPE = 2
    B_TYPE = 3
    U_TYPE = 4
    J_TYPE = 5
    R4_TYPE = 6
    CR = 7
    CI = 8
    CSS = 9
    CIW = 10
    CL = 11
    CS = 12
    CA = 13
    CB = 14
    CJ = 15


class RISCV_FIELD(enum.IntEnum):
    REG = 0
    C_REG = 1
    F_REG = 2
    CSR_REG = 3
    MEM = 4
    MEM_SP = 5
    IMM = 6
    RM = 7


class RISCV_INS(enum.IntEnum):
    ADD = 0
    AMOADD = 1
    AMOAND = 2
    AMOMAX = 3
    AMOMIN = 4
    AMOOR = 5
    AMOSWAP = 6
    AMOXOR = 7
    AND = 8
    AUIPC = 9
    BEQ = 10
    BGE = 11
    BLT = 12
    BNE = 13
    CSRRC = 14
    CSRRS = 15
    CSRRW = 16
    C_ADD = 17
    C_ADDI16SP = 18
    C_ADDI4SPN = 19
    C_AND = 20
    C_BEQZ = 21
    C_BNEZ = 22
    C_EBREAK = 23
    C_J = 24
    C_JAL = 25
    C_JALR = 26
    C_JR = 27
    C_LI = 28
    C_LUI = 29
    C_MV = 30
    C_OR = 31
    C_SL = 32
    C_SR = 33
    C_SUB = 34
    C_XOR = 35
    DIV = 36
    EBREAK = 37
    ECALL = 38
    FADD = 39
    FCLASS = 40
    FCVT = 41
    FDIV = 42
    FENCE = 43
    FENCE_I = 44
    FENCE_TSO = 45
    FEQ = 46
    FLE = 47
    FLT = 48
    FMADD = 49
    FMAX = 50
    FMIN = 51
    FMSUB = 52
    FMUL = 53
    FMV = 54
    FNMADD = 55
    FNMSUB = 56
    FSGNJ = 57
    FSGNJN = 58
    FSGNJX = 59
    FSQRT = 60
    FSUB = 61
    HFENCE_GVMA = 62
    HFENCE_VVMA = 63
    HINVAL_GVMA = 64
    HINVAL_VVMA = 65
    J = 66
    JAL = 67
    JALR = 68
    JR = 69
    LOAD = 70
    LR = 71
    LUI = 72
    MNRET = 73
    MRET = 74
    MUL = 75
    MULH = 76
    NOP = 77
    OR = 78
    PAUSE = 79
    REM = 80
    SC = 81
    SFENCE_INVAL_IR = 82
    SFENCE_VMA = 83
    SFENCE_W_INVAL = 84
    SINVAL_VMA = 85
    SL = 86
    SLT = 87
    SR = 88
    SRET = 89
    STORE = 90
    SUB = 91
    WFI = 92
    XOR = 93


# Additional RiscV-specific instruction flags
class RISCV_IF(enum.IntFlag):
    # Indicate normal load/store instructions
    LOAD        = 1 << 8
    STORE       = 1 << 9

    # Indicate this is a compressed load/store instruction that uses the SP (x2)
    # as the base register
    LOAD_SP     = 1 << 10
    STORE_SP    = 1 << 11

    # acquire or release spinlock flags
    AQ          = 1 << 12
    RL          = 1 << 13

    # This instruction is a hint form
    HINT        = 1 << 14


# RiscV operand flags
class RISCV_OF(enum.IntFlag):
    # Restriction flags
    SRC         = 1 << 1
    DEST        = 1 << 2
    NOT_ZERO    = 1 << 3
    NOT_TWO     = 1 << 4
    HINT_ZERO   = 1 << 5  # Indicates that if this operand has a value of zero,
                          # this instruction is a HINT and not an actual
                          # instruction to execute
    SIGNED      = 1 << 6
    UNSIGNED    = 1 << 7

    # Register is "compressed"
    CREG        = 1 << 8

    # Flags used to indicate size these definitions match those used in the
    # RiscV manual
    BYTE        = 1 << 9   # 1 byte
    HALFWORD    = 1 << 10  # 2 bytes
    WORD        = 1 << 11  # 4 bytes
    DOUBLEWORD  = 1 << 12  # 8 bytes
    QUADWORD    = 1 << 13  # 16 bytes

# Standard types used in the generated instruction list
RiscVInsCat = namedtuple('RiscVInsCat', ['xlen', 'cat'])
RiscVIns = namedtuple('RiscVIns', ['name', 'opcode', 'form', 'cat', 'mask', 'value', 'fields', 'flags'])

# A simple field where the field value can be masked and shifted out of the
# instruction value.
RiscVField = namedtuple('RiscVField', ['name', 'type', 'bits', 'args', 'flags'])

# Many RiscV instructions have complex immediate values like:
#   BEQ  imm[12,10:5] | rs2 | rs1 | imm[4:1,11]
#
# This field type contains a list of mask and shift operations that can be used
# to re-assemble the correct immediate from the instruction value
RiscVImmField = namedtuple('RiscVImmField', ['name', 'type', 'bits', 'args', 'flags'])

# RiscV load/store instructions use an immediate value to define an offset from
# a source/base register This field contains the arguments necessary to extract
# the source register value and immediate offset value from the instruction
# value
#   LWU  imm[11:0] | rs1 | rd
RiscVMemField = namedtuple('RiscVMemField', ['name', 'type', 'bits', 'args', 'flags'])

# RiscV compressed load/store instructions are like normal load/store
# instructions but they always use the x2 (the stack pointer) register as the
# base register
RiscVMemSPField = namedtuple('RiscVMemSPField', ['name', 'type', 'bits', 'args', 'flags'])

# A field type to hold mask/shift arguments for IMM and MEM fields
RiscVFieldArgs = namedtuple('RiscVFieldArgs', ['mask', 'shift'])
