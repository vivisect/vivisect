import struct

import envi
import envi.bits as e_bits

from envi.archs.sparc.const import *

#from exceptions import *


# Some discussion:

# Three instruction formats:
# 
# Format 1, op == 1:
#
# Used for CALL
#
#  +--+------------------------------+
#  |op|           disp30             |
#  +--+------------------------------+
#
# struct format1 {
#    unsigned int op:2; 
#    int disp30:30; // sign extended
# };
#
# Format 2, op == 0:
#
# Used for SETHI, Branches. Two variants, chosen by op2.
#
#  +--+-----+---+----------------------+
#  +op+ rd  +op2+         imm22        +
#  +--+-----+---+----------------------+
#
# struct format2_a {
#    unsigned int op:2;
#    unsigned int rd:5;
#    unsigned int op2:3;
#    unsigned int imm22:22;
#    }
#
#  +--+-+----+---+----------------------+
#  +op+a+cond+op2+         disp22       +
#  +--+-+----+---+----------------------+
#
# struct format2_b {
#    unsigned int op:2;
#    unsigned int a:1;
#    unsigned int cond:4;
#    unsigned int op2:3;
#    int disp22:22; // sign extended 
#    }
#
# Format 3, op == 2 || op == 3:
#
# Used for remaining instructions, largely arithmetic. three variants, chosen by op3.
#
# i == 0
# +--+-----+------+-----+-+--------+-----+
# +op+ rd  +  op3 + rs1 +i+   asi  + rs2 +
# +--+-----+------+-----+-+--------+-----+
#
# struct format3_a {
#    unsigned int op:2;
#    unsigned int rd:5;
#    unsigned int op3:6;
#    unsigned int rs1:5;
#    unsigned int i:1;
#    unsigned int asi:8;
#    unsigned int rs2:5;
# }
#
# i == 1
# +--+-----+------+-----+-+-------------+
# +op+ rd  +  op3 + rs1 +1+    simm13   +
# +--+-----+------+-----+-+-------------+
#
# struct format3_b {
#    unsigned int op:2;
#    unsigned int rd:5;
#    unsigned int op3:6;
#    unsigned int rs1:5;
#    unsigned int i:1;
#    int simm13:13;
# }
#
#
# +--+-----+------+-----+---------+-----+
# +op+ rd  +  op3 + rs1 +   opf   + rs2 +
# +--+-----+------+-----+---------+-----+
#
# struct format3_c {
#    unsigned int op:2;
#    unsigned int rd:5;
#    unsigned int op3:6;
#    unsigned int rs1:5;
#    unsigned int opf:9;
#    unsigned int rs2:5;
# }
#



def simm13_extend(value):
    return (value & (4095)) - (value & 4096)

def sign_extend(value, bits):
    highest_bit_mask = 1 << (bits - 1)
    remainder = 0
    for i in xrange(bits - 1):
        remainder = (remainder << 1) + 1

    if value & highest_bit_mask == highest_bit_mask:
        value = (value & remainder) - highest_bit_mask
    else:
        value = value & remainder
    return value


class SparcOp:
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va
    
    def __repr__(self):
        return "undefined"

class SparcOpCall(SparcOp):
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        super().__init__(instr, offset, va, endian)

        self.disp30 = (instr & MASK_DISP30) >> SHIFT_DISP30

    def __repr__(self):
        return "call "

#class SparcOpSetHi:
#class SparcOpBranch:
class SparcOpLoadStore(SparcOp):
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va
 
        self.rd = (instr & MASK_RD) >> SHIFT_RD
        self.op3 = (instr & MASK_OP3) >> SHIFT_OP3
        self.rs1 = (instr & MASK_RS1) >> SHIFT_RS1
        self.i = (instr & MASK_I) >> SHIFT_I
        self.asi = (instr & MASK_ASI) >> SHIFT_ASI
        self.rs2 = (instr & MASK_RS2) >> SHIFT_RS2
        self.simm13 = simm13_extend((instr & MASK_SIMM13) >> SHIFT_SIMM13)

        self.mnemonic_format = m_op3_mnemonic[self.op3]

    def __repr__(self):
        address = "%s" % register_label[self.rs1]
        if self.i == 0 and self.rs2 > 0:
            address += " + %s" % register_label[self.rs2]
        elif self.i == 1 and self.simm13 != 0:
            address += " + %d" % self.simm13

        regrd = register_label[self.rd]
        cregrd = creg_label[self.rd]
        asi = "ASI_%d" % self.asi

        return self.mnemonic_format.format(address=address, asi=asi, regrd=regrd, cregrd=cregrd)
 
class SparcOpArithmetic:
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va
 
        self.rd = (instr & MASK_RD) >> SHIFT_RD
        self.op3 = (instr & MASK_OP3) >> SHIFT_OP3
        self.rs1 = (instr & MASK_RS1) >> SHIFT_RS1
        self.i = (instr & MASK_I) >> SHIFT_I
        self.rs2 = (instr & MASK_RS2) >> SHIFT_RS2
        self.simm13 = simm13_extend((instr & MASK_SIMM13) >> SHIFT_SIMM13)

        self.mnemonic_format = a_op3_mnemonic[self.op3]

    def __repr__(self):
        
        regrs1 = register_label[self.rs1]

        if self.i == 0:
            reg_or_imm = register_label[self.rs2]
        else:
            reg_or_imm = "%d" % self.simm13

        regrd = register_label[self.rd]

        cregrd = creg_label[self.rd]

        return self.mnemonic_format.format(regrs1=regrs1, reg_or_imm = reg_or_imm, regrd=regrd, cregrd=cregrd)


class SparcDisasm:

    def __init__(self, endian=envi.ENDIAN_MSB):
        self.endian = endian
    

    def disasm(self, bytecode, offset, va):
        opcode = None
        if isinstance(bytecode, bytes):
            if len(bytecode) != 4:
                raise ValueError("instruction must be four bytes long")

            opcode = struct.unpack(">I", bytecode)[0]
        elif isinstance(bytecode, long):
            opcode = int(bytecode)
        else:
            opcode = bytecode


        # field decoding
        op = (opcode & MASK_OP) >> SHIFT_OP
        if op == 0: 
            pass 
        elif op == 1:
            # CALL
            pass

        elif op == 2:
            # Arithmetic, logical, shift, and remaining
            return SparcOpArithmetic(opcode, offset, va)

        elif op == 3:
            # Memory
            return SparcOpLoadStore(opcode, offset, va)

        else:
            raise ValueError("op field may not exceed 3")
            




