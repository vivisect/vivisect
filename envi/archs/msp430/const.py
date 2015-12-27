from envi.const import *
from envi import IF_NOFALL, IF_PRIV, IF_CALL, IF_BRANCH, IF_RET, IF_COND

IF_BYTE = 1<<8

# No operand instructions
nocode = [
    '.word' # Something is wrong, so return the dirty word
]

# Single operand intructions
scode = [
    ('rrc', 0),          # RRC Rotate right through carry
    ('swpb', 0),         # SWPB Swap bytes
    ('rra', 0),          # RRA Rotate right arithmetic
    ('sxt', 0),          # SXT Sign extend byte to word
    ('push', 0),         # PUSH Push value onto stack
    ('call', IF_CALL),   # CALL Subroutine call; push PC and move source to PC
    ('reti', IF_NOFALL), # RETI Return from interrupt; pop SR then pop PC
]

# Jump conditions
jcode = [
    ('jnz', IF_BRANCH | IF_COND),   # JNE/JNZ Jump if not equal/zero
    ('jz', IF_BRANCH | IF_COND),    # JEQ/JZ Jump if equal/zero
    ('jnc', IF_BRANCH | IF_COND),   # JNC/JLO Jump if no carry/lower
    ('jc', IF_BRANCH | IF_COND),    # JC/JHS Jump if carry/higher or same
    ('jn', IF_BRANCH | IF_COND),    # JN Jump if negative
    ('jge', IF_BRANCH | IF_COND),   # JGE Jump if greater or equal
    ('jl', IF_BRANCH | IF_COND),    # JL Jump if less
    ('jmp', IF_BRANCH | IF_NOFALL), # JMP Jump (unconditionally)
]

# Double operand instrucitons
dcode = [
    'mov',  # MOV Move source to destination
    'add',  # ADD Add source to destination
    'addc', # ADDC Add source and carry to destination
    'subc', # SUBC Subtract source from destination (with carry)
    'sub',  # SUB Subtract source from destination
    'cmp',  # CMP Compare (pretend to subtract) source from destination
    'dadd', # Decimal add source to destination (with carry)
    'bit',  # BIT Test bits of source AND destination
    'bic',  # BIC Bit clear (dest &= ~src)
    'bis',  # BIS Bit set (logical OR)
    'xor',  # XOR Exclusive or source with destination
    'and'   # AND Logical AND source with destination (dest &= src)
]

# Double special operand instructions
dspcode = [
    ('nop', 0),                  # No Operation - MOV
    ('pop', 0),                  # POP stackpointer - MOV
    ('br', IF_BRANCH|IF_NOFALL), # Branch - MOV
    ('ret', IF_NOFALL),          # Return - MOV
    ('clr', 0),                  # Clear destination - MOV
    ('rla', 0),                  # Shift and rotate left - ADD
    ('inc', 0),                  # Increment by one - ADD
    ('incd', 0),                 # Increment by two - ADD
    ('rlc', 0),                  # Shift and rotate left - ADDC
    ('adc', 0),                  # Adding only the carry bit - ADDC
    ('sbc', 0),                  # Subtracting only the carry bit - SUBC
    ('dec', 0),                  # Decrement by one - SUB
    ('decd', 0),                 # Decrement by two - SUB
    ('tst', 0),                  # Test - CMP
    ('dadc', 0),                 # Decimal adding only the carry bit - DADD
    ('clrc', 0),                 # Status register operation - BIC
    ('setc', 0),                 # Status register operation - BIS
    ('clrz', 0),                 # Status register operation - BIC
    ('setz', 0),                 # Status register operation - BIS
    ('clrn', 0),                 # Status register operation - BIC
    ('setn', 0),                 # Status register operation - BIS
    ('dint', 0),                 # Status register operation - BIC
    ('eint', 0),                 # Status register operation - BIC
    ('inv', 0),                  # Invert value - XOR
]

# Operand Type
SINGLE_OPCODE_TYPE = 0
JUMP_OPCODE_TYPE   = 1
DOUBLE_OPCODE_TYPE = 2
SP_OPCODE_TYPE     = 3

# Register Modes
REG_DIRECT      = 0x0
REG_INDEX       = 0x1
REG_INDIRECT    = 0x2
REG_IND_AUTOINC = 0x3
JUMP_MODE       = 0x4

# Masks
TEST_MASKS       = 0xF000 # Test operands
SINGLE_MASKS     = 0xE000 # ID single operands
JUMP_MASKS       = 0xC000 # ID jumps
JUMP_OFFSET      = 0x3FF  # Jump offset
SOURCE_REG       = 0xF    # Single op reg
DSOURCE_REG      = 0xF00  # Double source reg
DEST_REG         = 0xF    # Double dest reg
BYTE_WORD        = 0x40   # Byte or word
SOURCE_ADDR_MODE = 0x30   # Addressing mode source
DEST_ADDR_MODE   = 0x80   # Addressing mode destination
RETI_MASK        = 0x1300 # Return 'reti'
REG_BYTE         = 0x00FF # Clear the most significant byte
REG_FLAGS        = 0x01FF # Clear most significant 7 bits to get Status Register flags

# Compare to get the proper Opcode
SINGLE_OPCODE   = 0xF80   # Single opcode - rotate right 7
DOUBLE_OPCODE   = 0xF000  # Double opcode - rotate right 12
JUMP_OPCODE     = 0x1c00  # Jump condition - rotate right 10

# Sizes
BYTE = 1 # bytes
WORD = 2 # bytes
