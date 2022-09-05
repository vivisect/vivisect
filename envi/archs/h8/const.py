from envi.const import *

REG_PC = 8
REG_SP = 7
REG_FLAGS = 9


# opcode flags
IF_B = 0x100
IF_W = 0x200
IF_L = 0x400

OSZ_FLAGS = (
        None,
        IF_B,
        IF_W,
        None,
        IF_L,
        )

# operand flags
OF_PREDEC = 1
OF_POSTINC = 2
