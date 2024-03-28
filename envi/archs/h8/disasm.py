import struct

import envi
import envi.common as e_common

import envi.archs.h8.operands as h8_operands

import envi.archs.h8.regs as h8_regs
import envi.archs.h8.parsers as h8_parsers


class H8Disasm:
    fmt = '>H'

    def __init__(self):
        self._dis_regctx = h8_regs.H8RegisterContext()
        self._dis_oparch = envi.ARCH_H8
        self.ptrsize = 4

    def disasm(self, bytez, offset, va):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        opval, = struct.unpack_from('>H', bytez, offset)

        prim = opval >> 8
        opdata = h8_parsers.main_table[prim]

        if opdata is None:
            raise envi.InvalidInstruction(bytez=bytez[offset:offset+16], va=va)

        subtable, mnem, decoder, tsize, iflags = opdata

        if subtable:
            raise Exception("NEED subtable at 0x%x:  %s" % (va, e_common.hexify(bytez[offset:offset+16])))

        elif decoder is not None:
            opcode, nmnem, olist, flags, isize = decoder(va, opval, bytez, offset, tsize)
            # print opcode, nmnem, olist, flags, isize, decoder
            if nmnem is not None:
                mnem = nmnem
            iflags |= flags

        else:
            opcode = opval
            isize = 2
            olist = tuple()

        if olist is None:
            raise envi.InvalidInstruction(mesg='Operand list cannot be None for instruction "%s"' % mnem, bytez=bytez[offset:offset+16], va=va)
        op = h8_operands.H8Opcode(va, opcode, mnem, None, isize, olist, iflags)

        if op.opers is not None:
            # following the nasty little hack from other modules.  "everybody's doing it!"
            for oper in op.opers:
                oper._dis_regctx = self._dis_regctx

        return op


if __name__ == '__main__':
    import envi.archs
    envi.archs.dismain(H8Disasm())
