from enum import Enum
import envi.archs.mips.regs as mips_regs
from collections import namedtuple

import envi

######################################################################
# This enum will be used in conjunction with the formatParsers
# array in parsers.py to quickly lookup the parsing function
# for each type of instruction
######################################################################
class FormatType(Enum):
    ARITHLOG   = 0
    ARITHLOG_I = 1
    DIVMULT    = 2
    SHIFT      = 3
    SHIFT_V    = 4
    LOAD_I     = 5
    BRANCH     = 6
    BRANCH_Z   = 7
    JUMP       = 8
    JUMP_R     = 9
    LOADSTORE  = 10
    MOVEFROM   = 11
    MOVETO     = 12
    TRAP       = 13
    SYSCALL    = 14

######################################################################

R_OPCODE = 0b000000

'''
# R instr, type, opcode, shamt, funct, formatType
'''

MipsRInstr = namedtuple('MipsRInstr', ['name', 'opcode', 'shamt', 'funct', 'formatType', 'flags'])

# TODO Not sure if this is the best approach for splitting instructions up...
# Are instructions unique if we look them up by opcode+funct combined?
r_instr = [
    MipsRInstr('sll',  R_OPCODE, 0b00000, 0x00, FormatType.SHIFT, 0),
    None,
    MipsRInstr('srl',  R_OPCODE, 0b00000, 0x02, FormatType.SHIFT, 0),
    MipsRInstr('sra',  R_OPCODE, 0b00000, 0x03, FormatType.SHIFT, 0),
    MipsRInstr('sllv', R_OPCODE, 0b00000, 0x04, FormatType.SHIFT_V, 0),
    None,
    MipsRInstr('srlv', R_OPCODE, 0b00000, 0x06, FormatType.SHIFT_V, 0),
    MipsRInstr('srav', R_OPCODE, 0b00000, 0x07, FormatType.SHIFT_V, 0),
    MipsRInstr('jr',   R_OPCODE, 0b00000, 0x08, FormatType.JUMP_R, envi.IF_CALL | envi.IF_NOFALL),
    MipsRInstr('jalr', R_OPCODE, 0b00000, 0x09, FormatType.JUMP_R, envi.IF_CALL),
    None,
    None,
    MipsRInstr('syscall', R_OPCODE, 0b00000, 0x0c, FormatType.SYSCALL, envi.IF_CALL), # may be privileged?
    None,
    None,
    None,
    MipsRInstr('mfhi',  R_OPCODE, 0b00000, 0x10, FormatType.MOVEFROM, 0),
    MipsRInstr('mthi',  R_OPCODE, 0b00000, 0x11, FormatType.MOVETO, 0),
    MipsRInstr('mflo',  R_OPCODE, 0b00000, 0x12, FormatType.MOVEFROM, 0),
    MipsRInstr('mtlo',  R_OPCODE, 0b00000, 0x13, FormatType.MOVETO, 0),
    None,
    None,
    None,
    None,
    MipsRInstr('mult',  R_OPCODE, 0b00000, 0x18, FormatType.DIVMULT, 0),
    MipsRInstr('multu', R_OPCODE, 0b00000, 0x19, FormatType.DIVMULT, 0),
    MipsRInstr('div',   R_OPCODE, 0b00000, 0x1a, FormatType.DIVMULT, 0),
    MipsRInstr('divu',  R_OPCODE, 0b00000, 0x1b, FormatType.DIVMULT, 0),
    None,
    None,
    None,
    None,
    MipsRInstr('add',   R_OPCODE, 0b00000, 0x20, FormatType.ARITHLOG, 0),
    MipsRInstr('addu',  R_OPCODE, 0b00000, 0x21, FormatType.ARITHLOG, 0),
    MipsRInstr('sub',   R_OPCODE, 0b00000, 0x22, FormatType.ARITHLOG, 0),
    MipsRInstr('subu',  R_OPCODE, 0b00000, 0x23, FormatType.ARITHLOG, 0),
    MipsRInstr('and',   R_OPCODE, 0b00000, 0x24, FormatType.ARITHLOG, 0),
    MipsRInstr('or',    R_OPCODE, 0b00000, 0x25, FormatType.ARITHLOG, 0),
    MipsRInstr('xor',   R_OPCODE, 0b00000, 0x26, FormatType.ARITHLOG, 0),
    MipsRInstr('nor',   R_OPCODE, 0b00000, 0x27, FormatType.ARITHLOG, 0),
    None,
    None,
    MipsRInstr('slt',   R_OPCODE, 0b00000, 0x2a, FormatType.ARITHLOG, 0),
    MipsRInstr('sltu',  R_OPCODE, 0b00000, 0x2b, FormatType.ARITHLOG, 0),
]

# TODO can the I and J instruction arrays be condensed?

MipsIInstr = namedtuple('MipsIInstr', ['name', 'opcode', 'formatType', 'flags'])
MipsJInstr = namedtuple('MipsJInstr', ['name', 'opcode', 'formatType', 'flags'])

# TODO Missing 'bgez', 'bgezal', 'bltz', 'bltzal', 'break', 'mfc0', 'mtc0'
# TODO some of these branch opcodes have hardcoded registers

i_instr = [
    None,
    None,
    None,
    None,
    MipsIInstr('beq',   0x4, FormatType.BRANCH, envi.IF_BRANCH | envi.IF_COND),
    MipsIInstr('bne',   0x5, FormatType.BRANCH, envi.IF_BRANCH | envi.IF_COND),
    MipsIInstr('blez',  0x6, FormatType.BRANCH_Z, envi.IF_BRANCH | envi.IF_COND),
    MipsIInstr('bgtz',  0x7, FormatType.BRANCH_Z, envi.IF_BRANCH | envi.IF_COND),
    MipsIInstr('addi',  0x8, FormatType.ARITHLOG_I, 0),
    MipsIInstr('addiu', 0x9, FormatType.ARITHLOG_I, 0),
    MipsIInstr('slti',  0xA,  FormatType.ARITHLOG_I, 0),
    MipsIInstr('sltiu', 0xB,  FormatType.ARITHLOG_I, 0),
    MipsIInstr('andi',  0xc, FormatType.ARITHLOG_I, 0),
    MipsIInstr('ori',   0xd, FormatType.ARITHLOG_I, 0),
    MipsIInstr('xori',  0xe, FormatType.ARITHLOG_I, 0),
    MipsIInstr('lui',   0xf, FormatType.LOAD_I, 0),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    MipsIInstr('llo',   0x18, FormatType.LOAD_I, 0),
    MipsIInstr('lhi',   0x19, FormatType.LOAD_I, 0),
    None,
    None,
    None,
    None,
    None,
    None,
    MipsIInstr('lb',  0x20, FormatType.LOADSTORE, 0),
    MipsIInstr('lh',  0x21, FormatType.LOADSTORE, 0),
    None,
    MipsIInstr('lw',  0x23, FormatType.LOADSTORE, 0),
    MipsIInstr('lbu', 0x24, FormatType.LOADSTORE, 0),
    MipsIInstr('lhu', 0x25, FormatType.LOADSTORE, 0),
    None,
    None,
    MipsIInstr('sb',  0x28, FormatType.LOADSTORE, 0),
    MipsIInstr('sh',  0x29, FormatType.LOADSTORE, 0),
    None,
    MipsIInstr('sw',   0x2b, FormatType.LOADSTORE, 0),
]


j_instr = [
    (0),
    (1),
    MipsJInstr('j',   0x2, FormatType.JUMP, envi.IF_CALL | envi.IF_NOFALL),
    MipsJInstr('jal', 0x3, FormatType.JUMP, envi.IF_CALL),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    MipsJInstr('trap', 0x1a, FormatType.TRAP, envi.IF_NOFALL) # JL TODO
]
