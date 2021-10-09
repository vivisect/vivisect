from envi.archs.dotnet.opconst import *

MAIN_OPCODES = {
    # General format is (type, args, pops, pushes, name)
    # More specific Format is (type, (args,), (pop_mask,), (push_mask,), name)
    # So each element should be of length 5, with elements 1, 2, 3, being tuples of various length
    0x0: (INS_NOP,     (), (), (), 'nop'),
    0x1: (INS_BREAK,   (), (), (), 'break'),
    0x2: (INS_LOADARG, (), (), (TYPE_ANY,), 'ldarg.0'),
    0x3: (INS_LOADARG, (), (), (TYPE_ANY,), 'ldarg.1'),
    0x4: (INS_LOADARG, (), (), (TYPE_ANY,), 'ldarg.2'),
    0x5: (INS_LOADARG, (), (), (TYPE_ANY,), 'ldarg.3'),
    0x6: (INS_LOADLOC, (), (), (TYPE_ANY,), 'lodloc.0'),
    0x7: (INS_LOADLOC, (), (), (TYPE_ANY,), 'lodloc.1'),
    0x8: (INS_LOADLOC, (), (), (TYPE_ANY,), 'lodloc.2'),
    0x9: (INS_LOADLOC, (), (), (TYPE_ANY,), 'lodloc.3'),

    0xA: (INS_STLOC, (), (), (), 'stloc.0'),
    0xB: (INS_STLOC, (), (), (), 'stloc.1'),
    0xC: (INS_STLOC, (), (), (), 'stloc.2'),
    0xD: (INS_STLOC, (), (), (), 'stloc.3'),

    0xE: (INS_LOADARG, (TYPE_UINT8,), (), (TYPE_ANY,), 'ldarg.s'),
    0xF: (INS_LOADARG, (TYPE_UINT8,), (), (TYPE_REF,), 'ldarga.s'),

    0x10: (INS_LOADLOC, (TYPE_UINT8,), (TYPE_ANY,), (), 'starg.s'),

    0x11: (INS_LOADLOC, (TYPE_UINT8,), (), (TYPE_ANY,), 'ldloc.s'),
    0x12: (INS_LOADLOC, (TYPE_UINT8,), (), (TYPE_REF,), 'ldloca.s'),

    0x13: (INS_STLOC, (TYPE_UINT8,), (TYPE_ANY,), (), 'stloc.s'),

    # So yes, this loads a ref. That ref is null though  
    0x14: (INS_LDNULL, (), (), (TYPE_REF,), 'ldnull'),

    0x15: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.m1'),
    0x16: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.0'),
    0x17: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.1'),
    0x18: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.2'),
    0x19: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.3'),
    0x1A: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.4'),
    0x1B: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.5'),
    0x1C: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.6'),
    0x1D: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.7'),
    0x1E: (INS_LDC, (), (), (TYPE_INT32,), 'ldc.i4.8'),
    0x1F: (INS_LDC, (TYPE_INT8,), (), (TYPE_INT32,), 'ldc.i4.s'),

    0x20: (INS_LDC, (TYPE_INT32,), (), (TYPE_INT32,), 'ldc.i4'),
    0x21: (INS_LDC, (TYPE_INT64,), (), (TYPE_INT64,), 'ldc.i8'),

    0x22: (INS_LDC, (TYPE_FLOAT32,), (), (TYPE_FLOAT80,), 'ldc.r4'),
    0x23: (INS_LDC, (TYPE_FLOAT64,), (), (TYPE_FLOAT80,), 'ldc.r8'),

    # yes there is a gap here where 0x24 should be
    0x25: (INS_DUP, (), (TYPE_ANY,), (TYPE_ANY, TYPE_ANY), 'dup'),
    0x26: (INS_POP, (), (TYPE_ANY,), (), 'pop'),

    0x27: (INS_JMP,  (TYPE_METHOD,), (), (), 'jmp'),
    0x28: (INS_CALL, (TYPE_METHOD,), (TYPE_MULTI,), (TYPE_RETVAL,), 'call'),
    0x29: (INS_CALLI, (TYPE_SIG,), (TYPE_MULTI,), (TYPE_RETVAL,), 'calli'),
    0x2A: (INS_RET, (), (TYPE_ANY,), (), 'ret'),

    0x2B: (INS_BR | INS_SHORTENED, (TYPE_INT8,), (), (), 'br.s'),
    # TODO: also brnull/brzero. How to differentiate?
    0x2C: (INS_BRFALSE | INS_SHORTENED, (TYPE_INT8,), (TYPE_INT32,), (), 'brfalse.s'),
    # TODO: also brinst.s how to differentiate?
    0x2D: (INS_BRTRUE | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'brtrue.s'),
    0x2E: (INS_BEQ | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'beq.s'),
    0x2F: (INS_BGE | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'bge.s'),
    0x30: (INS_BGT | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'bgt.s'),
    0x31: (INS_BLE | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'ble.s'),
    0x32: (INS_BLT | INS_SHORTENED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'blt.s'),
    0x33: (INS_BNE | INS_SHORTENED | INS_UNORDERED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'bne.un.s'),
    0x34: (INS_BGE | INS_SHORTENED | INS_UNORDERED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'bge.un.s'),
    0x35: (INS_BGT | INS_SHORTENED | INS_UNORDERED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'bgt.un.s'),
    0x36: (INS_BLE | INS_SHORTENED | INS_UNORDERED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'ble.un.s'),
    0x37: (INS_BLT | INS_SHORTENED | INS_UNORDERED, (TYPE_INT8,), (TYPE_ANY, TYPE_ANY), (), 'blt.un.s'),

    0x38: (INS_BR, (TYPE_INT32,), (), (), 'br'),
    0x39: (INS_BRFALSE, (TYPE_INT32,), (TYPE_INT32,), (), 'brfalse'),
    0x3A: (INS_BRTRUE, (TYPE_INT32,), (TYPE_INT32,), (), 'brtrue'),
    0x3B: (INS_BEQ, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'beq'),
    0x3C: (INS_BGE, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'bge'),
    0x3D: (INS_BGT, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'bgt'),
    0x3E: (INS_BLE, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'ble'),
    0x3F: (INS_BLT, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'blt'),

    0x40: (INS_BNE | INS_UNORDERED, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'bne.un'),
    0x41: (INS_BGE | INS_UNORDERED, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'bge.un'),
    0x42: (INS_BGT | INS_UNORDERED, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'bgt.un'),
    0x43: (INS_BLE | INS_UNORDERED, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'ble.un'),
    0x44: (INS_BLT | INS_UNORDERED, (TYPE_INT32,), (TYPE_ANY, TYPE_ANY), (), 'blt.un'),

    0x45: (INS_SWITCH, (TYPE_INT32, TYPE_INT32), (TYPE_INT32,), (), 'switch'),  # TODO
    0x46: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.i1'),
    0x47: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.u1'),
    0x48: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.i2'),
    0x49: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.u2'),
    0x4A: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.i4'),
    0x4B: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.u4'),
    # also ldind.u8
    0x4C: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT64,), 'ldind.i8'),
    0x4D: (INS_LDIND, (), (TYPE_REF,), (TYPE_INT32,), 'ldind.i'),
    0x4E: (INS_LDIND, (), (TYPE_REF,), (TYPE_FLOAT80,), 'ldind.r4'),
    0x4F: (INS_LDIND, (), (TYPE_REF,), (TYPE_FLOAT80,), 'ldind.r8'),
    0x50: (INS_LDIND, (), (TYPE_REF,), (TYPE_REF,), 'ldind.ref'),

    0x51: (INS_STIND, (), (TYPE_REF, TYPE_REF),   (), 'stind.ref'),
    0x52: (INS_STIND, (), (TYPE_INT32, TYPE_REF), (), 'stdind.i1'),
    0x53: (INS_STIND, (), (TYPE_INT32, TYPE_REF), (), 'stdind.i2'),
    0x54: (INS_STIND, (), (TYPE_INT32, TYPE_REF), (), 'stdind.i4'),
    0x55: (INS_STIND, (), (TYPE_INT32, TYPE_REF), (), 'stdind.i8'),
    0x56: (INS_STIND, (), (TYPE_FLOAT80, TYPE_REF), (), 'stdind.r4'),
    0x57: (INS_STIND, (), (TYPE_FLOAT80, TYPE_REF), (), 'stdind.r8'),
    0x58: (INS_ADD, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'add'),
    0x59: (INS_SUB, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'sub'),
    0x5A: (INS_MUL, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'mul'),
    0x5B: (INS_DIV, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'div'),
    0x5C: (INS_DIV | INS_UNORDERED, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'div.un'),
    0x5D: (INS_REM, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'rem'),
    0x5E: (INS_REM | INS_UNORDERED, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'rem.un'),
    0x5F: (INS_AND, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'and'),
    0x60: (INS_OR,  (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'or'),
    0x61: (INS_XOR, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'xor'),
    0x62: (INS_SHL, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'shl'),
    0x63: (INS_SHR, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'shr'),
    0x64: (INS_SHR | INS_UNORDERED, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'shr.un'),
    0x65: (INS_NEG, (), (TYPE_ANY,), (TYPE_ANY, TYPE_ANY), 'neg'),
    0x66: (INS_NOT, (), (TYPE_ANY,), (TYPE_ANY, TYPE_ANY), 'not'),

    0x67: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.i1'),
    0x68: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.i2'),
    0x69: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.i4'),
    0x6A: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.i8'),
    0x6B: (INS_CONV, (), (TYPE_ANY,), (TYPE_FLOAT80,), 'conv.r4'),
    0x6C: (INS_CONV, (), (TYPE_ANY,), (TYPE_FLOAT80,), 'conv.r8'),
    0x6D: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.u4'),
    0x6E: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.u8'),

    0x6F: (INS_CALLVIRT, (TYPE_METHOD,), (TYPE_MULTI,), (TYPE_REF,), 'callvirt'),

    0x70: (INS_CPOBJ, (TYPE_TYPE,), (TYPE_POINTER, TYPE_POINTER), (), 'cpobj'),
    0x71: (INS_LDOBJ, (TYPE_TYPE,), (TYPE_POINTER,), (TYPE_ANY,), 'ldobj'),
    0x72: (INS_LDSTR, (TYPE_STRING,), (), (TYPE_ANY,), 'ldstr'),
    0x73: (INS_NEWOBJ, (TYPE_METHOD,), (TYPE_MULTI,), (TYPE_REF,), 'newobj'),
    0x74: (INS_CAST, (TYPE_TYPE,), (TYPE_REF,), (TYPE_REF,), 'castclass'),
    0x75: (INS_ISINST, (TYPE_TYPE,), (TYPE_REF,), (TYPE_INT32,), 'isinst'),
    0x76: (INS_CONV, (), (TYPE_ANY,), (TYPE_FLOAT80,), 'conv.r.un'),
    # Yes there is another weird gap here 
    0x79: (INS_UNBOX, (TYPE_TYPE,), (TYPE_REF,), (TYPE_POINTER,), 'unbox'),
    0x7A: (INS_THROW, (), (TYPE_REF,), (), 'throw'),
    0x7B: (INS_LDFLD, (TYPE_FIELD,), (TYPE_REF_OR_POINTER,), (TYPE_ANY,), 'ldfld'),
    0x7C: (INS_LDFLD, (TYPE_FIELD,), (TYPE_REF_OR_POINTER,), (TYPE_POINTER,), 'ldflda'),
    0x7D: (INS_STFLD, (TYPE_FIELD,), (TYPE_REF_OR_POINTER, TYPE_ANY), (), 'stfld'),
    0x7E: (INS_LDSFLD, (TYPE_FIELD,), (), (TYPE_ANY,), 'ldsfld'),
    0x7F: (INS_LDSFLD, (TYPE_FIELD,), (), (TYPE_POINTER,), 'ldsflda'),
    0x80: (INS_STSFLD, (TYPE_FIELD,), (TYPE_ANY,), (), 'stsfld'),
    0x81: (INS_STOBJ, (TYPE_TYPE,), (TYPE_POINTER, TYPE_ANY), (), 'stobj'),

    0x82: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i1.un'),
    0x83: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i2.un'),
    0x84: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i4.un'),
    0x85: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.ovf.i8.un'),
    0x86: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u1.un'),
    0x87: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u2.un'),
    0x88: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u4.un'),
    0x89: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.ovf.u8.un'),
    0x8A: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i.un'),
    0x8B: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.ovf.u.un'),

    0x8C: (INS_BOX, (), (TYPE_ANY,), (TYPE_REF,), 'box'),
    0x8D: (INS_NEWARR, (), (TYPE_INT32,), (TYPE_REF,), 'newarr'),
    0x8E: (INS_LDLEN,  (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldlen'),
    0x8F: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_REF,), 'ldelema'),
    0x90: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.i1'),
    0x91: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.u1'),
    0x92: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.i2'),
    0x93: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.u2'),
    0x94: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.i4'),
    0x95: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.u4'),
    0x96: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT64,), 'ldelem.i8'), # also ldelem.u8
    0x97: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_INT32,), 'ldelem.i'),
    0x98: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_FLOAT80,), 'ldelem.r4'),
    0x99: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_FLOAT80,), 'ldelem.r8'),
    0x9A: (INS_LDELEM, (), (TYPE_INT32, TYPE_REF), (TYPE_REF_OR_POINTER,), 'ldelem.ref'),

    0x9B: (INS_STELEM, (), (TYPE_INT32, TYPE_INT32, TYPE_REF), (), 'stelem.i'),
    0x9C: (INS_STELEM, (), (TYPE_INT32, TYPE_INT32, TYPE_REF), (), 'stelem.i1'),
    0x9D: (INS_STELEM, (), (TYPE_INT32, TYPE_INT32, TYPE_REF), (), 'stelem.i2'),
    0x9E: (INS_STELEM, (), (TYPE_INT32, TYPE_INT32, TYPE_REF), (), 'stelem.i4'),
    0x9F: (INS_STELEM, (), (TYPE_INT64, TYPE_INT32, TYPE_REF), (), 'stelem.i8'),
    0xA0: (INS_STELEM, (), (TYPE_FLOAT80, TYPE_INT32, TYPE_REF), (), 'stelem.r4'),
    0xA1: (INS_STELEM, (), (TYPE_FLOAT80, TYPE_INT32, TYPE_REF), (), 'stelem.r8'),
    0xA2: (INS_STELEM, (), (TYPE_REF_OR_POINTER, TYPE_INT32, TYPE_REF), (), 'stelem.ref'),

    0xA3: (INS_LDELEM, (TYPE_TYPE,), (TYPE_INT32, TYPE_REF), (TYPE_ANY,), 'ldelem.any'),
    0xA4: (INS_STELEM, (TYPE_TYPE,), (TYPE_REF_OR_POINTER, TYPE_INT32, TYPE_REF), (TYPE_ANY,), 'stelem.any'),

    0xA5: (INS_UNBOX, (TYPE_TYPE,), (TYPE_REF,), (TYPE_ANY,), 'unbox'),
    # Yup. Another gap. Much larger this time too

    0xB3: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i1'),
    0xB4: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u1'),
    0xB5: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i2'),
    0xB6: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u2'),
    0xB7: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i4'),
    0xB8: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u4'),
    0xB9: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.ovf.i8'),
    0xBA: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT64,), 'conv.ovf.u8'),

    # Yea another gap
    0xC2: (INS_REFANY, (TYPE_TYPE,), (TYPE_ANY,), (TYPE_POINTER,), 'refanyval'),
    0xC3: (INS_CK, (), (TYPE_ANY,), (TYPE_FLOAT80,), 'ckfinite'),
    # gap
    0xC6: (INS_MKREF, (TYPE_TYPE,), (TYPE_POINTER,), (TYPE_POINTER,), 'mkrefany'),

    0xD0: (INS_LDTOKEN, (TYPE_TFM,), (), (TYPE_POINTER,), 'ldtoken'),
    0xD1: (INS_CONV, (), (TYPE_ANY, ), (TYPE_INT32,), 'conv.u2'),
    0xD2: (INS_CONV, (), (TYPE_ANY, ), (TYPE_INT32,), 'conv.u1'),
    0xD3: (INS_CONV, (), (TYPE_ANY, ), (TYPE_INT32,), 'conv.i'),
    0xD4: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.i'),
    0xD5: (INS_CONV | INS_OVERFLOW, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.ovf.u'),

    0xD6: (INS_ADD | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'add.ovf'),
    0xD7: (INS_ADD | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'add.ovf.un'),
    0xD8: (INS_MUL | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'mul.ovf'),
    0xD9: (INS_MUL | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'mul.ovf.un'),
    0xDA: (INS_SUB | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'sub.ovf'),
    0xDB: (INS_SUB | INS_OVERFLOW, (), (TYPE_ANY, TYPE_ANY), (TYPE_ANY,), 'sub.ovf.un'),

    0xDC: (INS_END, (), (), (), 'endfinally'),
    0xDD: (INS_LEAVE, (TYPE_INT32,), (), (), 'leave'),
    0xDE: (INS_LEAVE, (TYPE_INT8,), (), (), 'leave.s'),

    0xDF: (INS_STIND, (), (TYPE_INT32, TYPE_POINTER), (), 'stind.i'),
    0xE0: (INS_CONV, (), (TYPE_ANY,), (TYPE_INT32,), 'conv.u'),
}


# All of these are two byte opcodes, but have 0xFE as their first byte
EXT_OPCODES = {
    0x00: (INS_ARGLIST, (), (TYPE_ANY,), (TYPE_POINTER,), 'arglist'),
    0x01: (INS_CEQ, (), (TYPE_ANY, TYPE_ANY), (TYPE_INT32,), 'ceq'),
    0x02: (INS_CGT, (), (TYPE_ANY, TYPE_ANY), (TYPE_INT32,), 'cgt'),
    0x03: (INS_CGT | INS_UNORDERED, (), (TYPE_ANY, TYPE_ANY), (TYPE_INT32,), 'cgt.un'),
    0x04: (INS_CLT, (), (TYPE_ANY, TYPE_ANY), (TYPE_INT32,), 'clt'),
    0x05: (INS_CLT | INS_UNORDERED, (), (TYPE_ANY, TYPE_ANY), (TYPE_INT32), 'clt.un'),

    0x06: (INS_LDFN, (TYPE_METHOD,), (TYPE_REF, TYPE_POINTER), (TYPE_POINTER,), 'ldftn'),
    0x07: (INS_LDFN, (TYPE_METHOD,), (TYPE_REF, ), (TYPE_POINTER), 'ldvirtfn'),

    0x09: (INS_LOADARG, (TYPE_INT32, ), (), (TYPE_ANY, ), 'ldarg'),
    0x0A: (INS_LOADARG, (TYPE_INT32, ), (), (TYPE_POINTER, ), 'ldarga'),
    0x0B: (INS_STARG, (TYPE_INT32, ), (TYPE_ANY, ), (), 'starg'),
    0x0C: (INS_LOADLOC, (TYPE_INT32, ), (), (TYPE_ANY, ), 'ldloc'),
    0x0D: (INS_LOADLOC, (TYPE_INT32, ), (), (TYPE_POINTER, ), 'ldloca'),
    0x0E: (INS_STLOC, (TYPE_INT32, ), (TYPE_ANY, ), (), 'stloc'),

    0x0F: (INS_LOCALLOC, (), (TYPE_INT32,), (TYPE_POINTER,), 'localloc'),
    0x11: (INS_ENDFILTER, (), (TYPE_INT32,), (), 'endfilter'),
    0x12: (INS_UNALIGNED, (TYPE_INT8,), (), (), 'unaligned'),
    0x13: (INS_VOLATILE, (), (), (), 'volatile'),
    0x14: (INS_TAIL, (), (), (), 'tail'),
    0x15: (INS_INITOBJ, (TYPE_TYPE,), (TYPE_POINTER,), (), 'initobj'),
    0x16: (INS_CONSTRAINED, (TYPE_TYPE,), (), (), 'constrained'),

    0x17: (INS_CPBLK, (), (TYPE_INT32, TYPE_POINTER, TYPE_POINTER), (), 'cpblk'),
    0x18: (INS_INITBLK, (), (TYPE_INT32, TYPE_INT32, TYPE_POINTER), (), 'initblk'),
    0x1A: (INS_RETHROW, (), (), (), 'rethrow'),
    0x1C: (INS_SIZEOF, (TYPE_TYPE,), (), (TYPE_INT32,), 'sizeof'),
    0x1D: (INS_REFANY, (), (TYPE_ANY,), (TYPE_POINTER,), 'refanytype'),
    0x1E: (INS_READONLY, (), (), (), 'readonly'),
}