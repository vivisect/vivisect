import struct

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.archs.dotnet.opcodes as e_opcodes

from envi.archs.dotnet.opconst import *

# TODO: Faster as a list, dictionary for dev ease during POC
_imm_valus = {
    TYPE_INT8: (1, True),
    TYPE_UINT8: (1, False),
    TYPE_INT32: (4, True),
    TYPE_UINT32: (4, False),
    TYPE_INT64: (8, True),

    TYPE_FLOAT32: (4, True),
    TYPE_FLOAT64: (8, True),
    TYPE_FLOAT80: (10, True),
}

class DotNetImmOper(envi.Operand):
    def __init__(self, typ, byts, bigend, md):
        info = _imm_valus.get(typ)
        if not info:
            raise e_exc.InvalidOperand('Type: %s on DotNetImmOper??')
        size, sign = info
        self.valu = e_bits.parsebytes(byts, 0, size, sign=sign, bigend=bigend)

    def getOperAddr(self, op, emu=None):
        return self.valu

    def isImmed(self):
        return True

    def isDiscrete(self):
        return True

    def repr(self, op):
        return str(self.valu)

class DotNetMethod(envi.Operand):
    def __init__(self, typ, byts, bigend, md):
        self.mname = ''

    def isImmed(self):
        return True

    def isDiscrete(self):
        return True

class DotNetOperand(envi.Operand):
    def __init__(self, typ, byts, bigend, md):
        pass

class DotNetStackOperand(envi.Operand):
    def __init__(self, typ, byts, bigend, md):
        pass

class DotNetOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, prefixes, size, operands, push, pop, iflags=0):
        super().__init__(va, opcode, mnem, prefixes, size, operands, iflags)
        self.push = push
        self.pop = pop

    def __repr__(self):
        pass

    def render(self, mcanv):
        pass

# TODO: This would be faster as just a list
_oper_ctors = {
    #TYPE_ANY
    TYPE_INT8: DotNetImmOper,
    TYPE_UINT8: DotNetImmOper,
    TYPE_INT32: DotNetImmOper,
    TYPE_UINT32: DotNetImmOper,
    TYPE_INT64: DotNetImmOper,
    TYPE_METHOD: DotNetMethod,
    #TYPE_SIG
    #TYPE_FIELD
    #TYPE_TYPE
    #TYPE_STRING
    #TYPE_FLOAT32
    #TYPE_FLOAT64
    #TYPE_FLOAT80
    #TYPE_MULTI
    #TYPE_POINTER
    #TYPE_REF
    #TYPE_REF_OR_POINTER
    #TYPE_RETVAL
    #TYPE_TFM
}

class DotNetDisasm:
    def __init__(self, psize=4, bigend=False, metadata={}):
        self.bigend = bigend
        self.psize = psize
        self.metadata = metadata

    def disasm(self, byts, offset, va):
        startoff = offset
        tabl = e_opcodes.MAIN_OPCODES
        obyt = byts[offset]
        offset += 1

        # TODO: This is actually prefixes
        if obyt == 0xFE:
            obyt = byts[offset]
            offset += 1
            tabl = e_opcodes.EXT_OPCODES

        odef = tabl.get(obyt)
        if not odef:
            raise e_exc.InvalidInstruction(bytez=byts[offset:offset+8], va=va)
        ins, params, pops, pushes, name = odef

        args = []
        for param in params:
            ctor = _oper_ctors.get(param)
            if not ctor:
                continue
            args.append(ctor(param, byts[offset:], self.bigend, self.metadata))

        poppers = [DotNetStackOperand(oper) for oper in pops]
        pushers = [DotNetStackOperand(oper) for oper in pushes]

        return DotNetOpcode(va, ins, name, 0, 1, args, pushers, poppers, iflags=0)
