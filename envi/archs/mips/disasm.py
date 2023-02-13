import struct
import binascii
import enum
import envi

import envi.archs.mips.opcode as mips_opcode
import envi.archs.mips.regs as mips_regs
import envi.archs.mips.parsers as mips_parsers


OP_MASK    = 0xFC000000 # 0b11111100000000000000000000000000
RS_MASK    = 0x03E00000 # 0b00000011111000000000000000000000
RT_MASK    = 0x001F0000 # 0b00000000000111110000000000000000
RD_MASK    = 0x0000F800 # 0b00000000000000001111100000000000
SHAMT_MASK = 0x000007C0 # 0b00000000000000000000011111000000
FUNCT_MASK = 0x0000003F # 0b00000000000000000000000000111111
IMM_MASK   = 0x0000FFFF # 0b00000000000000001111111111111111
ADDR_MASK  = 0x03FFFFFF # 0b00000011111111111111111111111111

class OpType(enum.Enum):
    R_TYPE = enum.auto()
    J_TYPE = enum.auto()
    I_TYPE = enum.auto()

class MipsDisasm:
    def __init__(self):
        pass

    def disasm(self, bytez, offset, va):
        val, = struct.unpack_from('>I', bytez, offset)

        op = (val & OP_MASK) >> 26

        if (op == 0): # if op = 0, probably an R type (until we add in FP)
            op, rs, rt, rd, shamt, funct = self.mipsRformat(val)

            mnem = mips_opcode.r_instr[funct].name
            flags = mips_opcode.r_instr[funct].flags

            return MipsOpcode(va=va, opcode=op, optype=OpType.R_TYPE, mnem=mnem,
                              opers=[MipsRegOperand(rs), MipsRegOperand(rt), MipsRegOperand(rd)],
                              iflags=flags, shamt=shamt, funct=funct, size=4)

        else:
            # j, jal or trap (will need to refactor this if the list grows)
            if (op == 0x2 or op == 0x3 or op == 0x1a):
                op, addr = self.mipsJformat(val)

                mnem = mips_opcode.j_instr[op].name
                flags = mips_opcode.j_instr[op].flags

                return MipsOpcode(va=va, opcode=op, optype=OpType.J_TYPE, mnem=mnem,
                                  opers=[addr],
                                  iflags=flags, size=4)

            else:
                op, rs, rt, imm = self.mipsIformat(val)

                mnem = mips_opcode.i_instr[op].name
                flags = mips_opcode.i_instr[op].flags

                return MipsOpcode(va=va, opcode=op, optype=OpType.I_TYPE, mnem=mnem,
                                  opers=[MipsRegOperand(rs), MipsRegOperand(rt), MipsImmOperand(imm)],
                                  iflags=flags, size=4)

    def mipsRformat(self,val):
        op = (val & OP_MASK) >> 26
        rs = (val & RS_MASK) >> 21
        rt = (val & RT_MASK) >> 16
        rd = (val & RD_MASK) >> 11
        shamt = (val & SHAMT_MASK) >> 6
        funct = (val & FUNCT_MASK)

        return op, rs, rt, rd, shamt, funct

    def mipsIformat(self, val):
        op = (val & OP_MASK) >> 26
        rs = (val & RS_MASK) >> 21
        rt = (val & RT_MASK) >> 16
        imm = (val & IMM_MASK)

        return op, rs, rt, imm

    def mipsJformat(self, val):
        op = (val & OP_MASK) >> 26
        addr = (val & ADDR_MASK)

        return op,addr

class MipsOpcode(envi.Opcode):
    def __init__(self, va, opcode, optype, mnem, opers, iflags=0, size=0, shamt=None, funct=None):
        self.va = va
        self.opcode = opcode
        self.optype = optype
        self.mnem = mnem
        self.opers = opers
        self.iflags = iflags | envi.ARCH_MIPS # JL this is how Vivisect can "know" that it's looking at MSP430 because it supports multiple arches in a single workspace
        self.size = size

        self.shamt = shamt
        self.funct = funct


    def __len__(self):
        return int(self.size)

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """

        if (self.optype is OpType.R_TYPE):
            format_type_idx = mips_opcode.i_instr[self.opcode].formatType
            renderFunc = mips_parsers.renderParsers[format_type_idx.value]
            renderFunc(mcanv, self.opcode, self.opers, self.shamt, self.mnem)
        elif (self.optype is OpType.I_TYPE):
            format_type_idx = mips_opcode.i_instr[self.opcode].formatType
            renderFunc = mips_parsers.renderParsers[format_type_idx.value]
            renderFunc(mcanv, self.opcode, self.opers, self.mnem)
        elif (self.optype is OpType.J_TYPE):
            format_type_idx = mips_opcode.j_instr[self.opcode].formatType
            renderFunc = mips_parsers.renderParsers[format_type_idx.value]
            renderFunc(mcanv, self.opcode, self.opers, self.mnem)
        else:
            return "ERROR"

    def __repr__(self):
        if (self.optype is OpType.R_TYPE):
            format_type_idx = mips_opcode.r_instr[self.funct].formatType
            parser = mips_parsers.formatParsers[format_type_idx.value]
            return parser(self.opcode, self.opers, self.shamt, self.mnem)
        elif (self.optype is OpType.I_TYPE):
            format_type_idx = mips_opcode.i_instr[self.opcode].formatType
            parser = mips_parsers.formatParsers[format_type_idx.value]
            return parser(self.opcode, self.opers, self.mnem)
        elif (self.optype is OpType.J_TYPE):
            format_type_idx = mips_opcode.j_instr[self.opcode].formatType
            parser = mips_parsers.formatParsers[format_type_idx.value]
            return parser(self.opcode, self.opers, self.mnem)
        else:
            return "ERROR"

    def getBranches(self, emu=None):
        ret = []

        flags = 0

        # if self.iflags & (envi.IF_COND):
        #     flags |= envi.BR_COND
        #     addb = True
        #
        # if not self.iflags & (envi.IF_NOFALL | envi.IF_RET | envi.IF_BRANCH) or self.iflags & envi.IF_COND:
        #     ret.append((self.va + self.size, flags|envi.BR_FALL))
        #
        # if len(self.opers) == 0:
        #     if self.iflags & envi.IF_CALL:
        #         ret.append(None, flags | envi.BR_PROC)
        #     return ret
        #
        # if self.iflags & envi.IF_CALL:
        #     flags |= envi.BR_PROC
        #     addb = True
        #
        # elif (self.iflags & envi.IF_CALLCC) == envi.IF_CALLCC:
        #     flags |= (envi.BR_PROC | envi.BR_COND)
        #     addb = True
        #
        # elif self.iflags & envi.IF_BRANCH:
        #     addb = True

        return ret

class MipsRegOperand(envi.RegisterOper):
    def __init__(self, val, va=0):
        self.reg = val
        self.va = va

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va

        if emu is None:
            return None

        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return

        emu.setRegister(self.reg, val)

    def isReg(self):
        return True

    def repr(self):
        return "$" + mips_regs.registers[self.reg]

    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText("$"+rname, typename='registers')


class MipsImmOperand(envi.ImmedOper):
    def __init__(self, val, va=0, oflags=0):
        self.val = val
        self.va = va
        self.oflags = oflags # JL do I need this?

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def getOperValue(self, op, emu=None):
        return self.val

    def repr(self):
        if abs(self.val) >= 4096:
            return str(hex(self.val))
        else:
            return str(self.val)

    def render(self, mcanv, op, idx):
        return 'todo'

# index operand? address operand? 
