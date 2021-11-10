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



def simm13_to_signed_int(value):
    value &= 8191
    return (value & (4095)) - (value & 4096)

def disp22_to_signed_int(value):
    value &= 4194303
    return (value & (2097151)) - (value & 2097152)

def disp30_to_signed_int(value):
    value &= 1073741823
    return (value & (536870911)) - (value & 536870912)


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

class SparcOpBranch:
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va

        self.a = (instr & MASK_A) >> SHIFT_A
        self.cond = (instr & MASK_COND) >> SHIFT_COND
        self.disp22 = (instr & MASK_DISP22)
        self.op2 = (instr & MASK_OP2) >> SHIFT_OP2
        

    def __repr__(self):
        annul = ",a" if self.a else ""
        disp22 = disp22_to_signed_int(self.disp22)*4
        if self.op2 == B_OP2_INT:
           instruction = branch_cond_int_mnemonic[self.cond]
           return "{instruction}{annul} {disp22}".format(instruction=instruction, annul=annul, disp22=disp22)
        elif self.op2 == B_OP2_FLOAT:
           instruction = branch_cond_float_mnemonic[self.cond]
           return "{instruction}{annul} {disp22}".format(instruction=instruction, annul=annul, disp22=disp22)
        elif self.op2 == B_OP2_CPROC:
           instruction = branch_cond_cproc_mnemonic[self.cond]
           return "{instruction}{annul} {disp22}".format(instruction=instruction, annul=annul, disp22=disp22)

        raise ValueError("Instruction 0x{opcode:08x} at address {address} is invalid.".format(opcode=self.instr, address="0x{:08x}".format(self.va) if self.va is not None else "None"))


 
class SparcOpSetHi:
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va

        self.rd = (instr & MASK_RD) >> SHIFT_RD
        self.op = (instr & MASK_OP) >> SHIFT_OP
        self.op2 = (instr & MASK_OP2) >> SHIFT_OP2
        self.imm22 = (instr & MASK_IMM22)
        
    def __repr__(self):
        regrd = register_label[self.rd]
        imm22 = "0x%8x" % (self.imm22<<10)

        if self.op2 == 4: 
            return m_op2_sethi_mnemonic.format(regrd=regrd, imm22=imm22)

        return "undefined"
 
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
        self.simm13 = simm13_to_signed_int((instr & MASK_SIMM13) >> SHIFT_SIMM13)

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
        self.simm13 = simm13_to_signed_int((instr & MASK_SIMM13) >> SHIFT_SIMM13)
        self.cond = (instr & MASK_COND) >> SHIFT_COND

    def __repr__(self):
        if not self.op3 in a_op3_mnemonic:
            print("instruction: {instr:08x}".format(instr=self.instr))
            print("rd: {rd} op3: {op3} rs1: {rs1} i: {i} rs2: {rs2} simm13: {simm13} cond: {cond}".format(rd=self.rd, op3=self.op3, rs1=self.rs1,
                i=self.i, rs2=self.rs2, simm13=self.simm13, cond=self.cond))
            raise ValueError("unrecognized op3 value: {op3}".format(op3=self.op3))

        regrs1 = register_label[self.rs1]
        regrs2 = register_label[self.rs2]
        
        mnemonic_format = a_op3_mnemonic[self.op3]
        icccond = branch_cond_traps_mnemonic[self.cond].upper()

        # reg_or_imm or address both depend on the value of i, but are otherwise unrelated and both are never used
        if self.i == 0:
            reg_or_imm = register_label[self.rs2]
            self.address = "{rs1} + {rs2}".format(rs1=regrs1, rs2=regrs2)
        else:
            reg_or_imm = int(self.simm13)
            self.address = "{rs1} + {simm13}".format(rs1=regrs1, simm13=self.simm13)

        regrd = register_label[self.rd]
        cregrd = creg_label[self.rd]
        asregrd = asreg_label[self.rd]
        asregrs1 = asreg_label[self.rs1]

        return mnemonic_format.format(regrs1=regrs1, reg_or_imm=reg_or_imm, regrd=regrd, cregrd=cregrd, 
                address=self.address, icccond=icccond, asregrd=asregrd, asregrs1=asregrs1)

class SparcOpCall:
    def __init__(self, instr, offset, va, endian=envi.ENDIAN_MSB):
        self._endian = endian
        self.instr = instr
        self.offset = offset
        self.va = va
 
        self.disp30 = (instr & MASK_DISP30)
        self.disp30 = disp30_to_signed_int(self.disp30)*4

    def __repr__(self):
        
        return "call {disp30} (pc+{disp30})".format(disp30=self.disp30)



class SparcDisasm:

    def __init__(self, endian=envi.ENDIAN_MSB):
        self.endian = endian
    

    def disasm(self, bytecode, offset, va):
        opcode = None
        if isinstance(bytecode, bytes):
            if len(bytecode) != 4:
                raise ValueError("instruction must be four bytes long")

            opcode = struct.unpack(">I", bytecode)[0]
        else:
            opcode = bytecode


        # field decoding
        op = (opcode & MASK_OP) >> SHIFT_OP
        if op == 0: 
            # Branches and SETHI
            op2 = (opcode & MASK_OP2) >> SHIFT_OP2
            if op2 == OP2_SETHI:
                return SparcOpSetHi(opcode, offset, va)
            else:
                return SparcOpBranch(opcode, offset, va)

        elif op == 1:
            # CALL
            return SparcOpCall(opcode, offset, va)

        elif op == 2:
            # Arithmetic, logical, shift, and remaining
            return SparcOpArithmetic(opcode, offset, va)

        elif op == 3:
            # Memory
            return SparcOpLoadStore(opcode, offset, va)
        else:
            raise ValueError("op field may not exceed 3")
            
