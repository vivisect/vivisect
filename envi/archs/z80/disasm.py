
import envi
import envi.bits as e_bits
import envi.bytesig as e_bsig

from envi.archs.z80.regs import *
from envi.archs.z80.const import *

import envi.archs.z80.z80opcode as z80_opcode

sigtree = e_bsig.SignatureTree()

for row in z80_opcode.z80table:
    sighex, maskhex = row[0]

    sig = binascii.unhexlify(sighex)
    mask = binascii.unhexlify(maskhex)

    sigtree.addSignature(sig, masks=mask, val=row)


class z80RegOper(envi.RegisterOper):
    def __init__(self, reg):
        self.reg = reg

class z80ImmOper(envi.ImmedOper):
    def __init__(self, imm):
        self.imm = imm

    def repr(self, op):
        return '%.4xH' % self.imm

class z80ConstOper(z80ImmOper):
    pass

class z80RegMem(envi.DerefOper):
    def __init__(self, reg, disp = 0):
        self.reg = reg
        self.disp = disp

    def repr(self, op):
        rname = regctx.getRegisterName(self.reg)
        if self.disp > 0:
            return '(%s + %d)' % (rname, self.disp)
        if self.disp < 0:
            return '(%s - %d)' % (rname, abs(self.disp))
        return '(%s)' % rname

class z80Opcode(envi.Opcode):
    pass

class z80Disasm:

    def __init__(self):
        # NOTE: For eventual things like "modes" etc...
        pass

    def disasm(self, bytez, offset, va):
        row = sigtree.getSignature(bytez, offset)
        if row is None:
            raise envi.InvalidInstruction(bytez=bytez[offset:offset+8], va=va)
        sigmask, mnem, o1type, o1info, o2type, o2info, oplen, immoff, iflags = row
        #ret = i386Opcode(va, optype, mnem, prefixes, (offset-startoff)+operoffset, operands, iflags)
        opers = []
        if o1type is not None:
            opers.append(self._buildOper(bytez, offset, immoff, o1type, o1info))
        if o2type is not None:
            opers.append(self._buildOper(bytez, offset, immoff, o2type, o2info))
        return z80Opcode(va, 0, mnem, 0, oplen, opers, iflags)

    def _buildOper(self, bytez, offset, immoff, otype, oinfo):

        if otype == OPTYPE_Reg:
            return z80RegOper(oinfo)

        elif otype == OPTYPE_RegMem:
            return z80RegMem(oinfo)

        elif otype == OPTYPE_const:
            return z80ConstOper(oinfo)

        elif otype == OPTYPE_imm8:
            imm = e_bits.parsebytes(bytez, offset+immoff, 1)
            return z80ImmOper(imm)

        elif otype == OPTYPE_imm16:
            imm = e_bits.parsebytes(bytez, offset+immoff, 2)
            return z80ImmOper(imm)

        elif otype == OPTYPE_RegAlt:
            return z80RegOper(oinfo)

        elif otype == OPTYPE_Ind:
            pass

        elif otype == OPTYPE_RegMemDisp:
            disp = e_bits.parsebytes(bytez, offset+immoff, 1, sign=True)
            return z80RegMem(oinfo, disp)

        else:
            raise Exception('Unknown z80 operand type: %d' % otype)
