import logging

import envi
import envi.exc as e_exc
import envi.bits as e_bits
import envi.archs.dotnet.opcodes as e_opcodes

from envi.archs.dotnet.opconst import *

logger = logging.getLogger(__name__)

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

class DotNetOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, prefixes, size, operands, push, pop, iflags=0):
        super().__init__(va, opcode, mnem, prefixes, size, operands, iflags)
        self.push = push
        self.pop = pop

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
    def __init__(self, psize=4, bigend=False, metadata=None):
        self.bigend = bigend
        self.psize = psize
        self.metadata = metadata

    def disasm(self, byts, offset, va):
        startoff = offset
        tabl = e_opcodes.MAIN_OPCODES
        obyt = byts[offset]
        offset += 1

        prefixes = []
        while obyt == 0xFE:
            obyt = byts[offset]
            offset += 1

            pref = e_opcodes.EXT_OPCODES.get(obyt)
            if not pref:
                continue
            ins, _, _, _, _ = pref

            prefixes.append(ins ^ INS_PREFIX)

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

        poppers = []
        for pop in pops:
            ctor = _oper_ctors.get(pop)
            if not ctor:
                continue
            poppers.append(ctor(pop, byts[offset:], self.bigend, self.metadata))

        pushers = []
        for push in pushes:
            ctor = _oper_ctors.get(push)
            if not ctor:
                continue
            pushers.append(ctor(push, byts[offset:], self.bigend, self.metadata))

        return DotNetOpcode(va, ins, name, prefixes, 5, args, pushers, poppers, iflags=0)
