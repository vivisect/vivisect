import struct

import envi.bits
import envi.exc as e_exc
import envi.archs.dotnet.opcodes as e_opcodes

class DotNetOperand(envi.Operand):
    pass

class DotNetStackOperand(envi.Operand):
    pass

class DotNetOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, prefixes, size, operands, push, pop, iflags=0):
        super().__init__(va, opcode, mnem, prefixes, size, operands, iflags)
        self.push = push
        self.pop = pop

class DotNetDisasm:
    def __init__(self):
        pass

    def disasm(self, bytez, offset, va):
        startoff = offset
        tabl = e_opcodes.MAIN_OPCODES
        obyt = bytez[offset]
        offset += 1
        if obyt == 0xFE:
            obyt = bytz[offset]
            offset += 1
            tabl = e_opcodes.EXT_OPCODES

        odef = tabl.get(obyt)
        if not odef:
            raise e_exc.InvalidInstruction(bytez=bytez[offset:offset+8], va=va)
        ins, params, pops, pushes, name = odef
        opers = [DotNetOperand(oper) for oper in params]
        poppers = [DotNetStackOperand(oper) for oper in pops]
        pushers = [DotNetStackOperand(oper) for oper in pushes]

        return DotNetOpcode(va, ins, name, 0, operands, 0, pushers, poppers, iflags=0)