
from envi import *

IF_NONE = 0
SZ = [
    IF_BYTE,
    IF_WORD,
    IF_LONG,
    IF_UWORD,
    ]


tbl_6 = (\
    (None, None, 0xff3cff00, 0x6200200, INS_ADC, 'adc', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3c00, 0x60800, INS_ADD, 'add', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('mi', ((14, 3),)), ('rs', ((4, 15),))], 3, IF_CALL),
    (None, None, 0xff3c00, 0x61000, INS_AND, 'and', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('mi', ((14, 3),)), ('rs', ((4, 15),))], 3, IF_CALL),
    (None, None, 0xff3c00, 0x60400, INS_CMP, 'cmp', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('mi', ((14, 3),)), ('rs', ((4, 15),))], 3, IF_CALL),
    (None, None, 0xff3cff00, 0x6200800, INS_DIV, 'div', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200900, INS_DIVU, 'divu', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200600, INS_EMUL, 'emul', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200700, INS_EMULU, 'emulu', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6201100, INS_ITOF, 'itof', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200400, INS_MAX, 'max', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200500, INS_MIN, 'min', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3c00, 0x60c00, INS_MUL, 'mul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('mi', ((14, 3),)), ('rs', ((4, 15),))], 3, IF_CALL),
    (None, None, 0xff3c00, 0x61400, INS_OR, 'or', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('mi', ((14, 3),)), ('rs', ((4, 15),))], 3, IF_CALL),
    (None, None, 0xfffcff00, 0x6a00000, INS_SBB, 'sbb', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200c00, INS_TST, 'tst', [('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6201500, INS_UTOF, 'utof', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6201000, INS_XCHG, 'xchg', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
    (None, None, 0xff3cff00, 0x6200d00, INS_XOR, 'xor', [('rd', ((0, 15),)), ('ld', ((16, 3),)), ('mi', ((22, 3),)), ('rs', ((4, 15),))], 4, IF_CALL),
)


tbl_3f = (\
    (None, None, 0xfc00, 0x3c00, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((8, 3),)), ('dsp', ((7, 16), (0, 15)))], 2, IF_NONE),
    (None, None, 0xff00, 0x3f00, INS_RTSD, 'rtsd', [('rd', ((4, 15),)), ('rd2', ((0, 15),))], 2, IF_NONE),
)


tbl_74 = (\
    (None, None, 0xfcf0, 0x7420, INS_AND, 'and', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7400, INS_CMP, 'cmp', [('rs2', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7410, INS_MUL, 'mul', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7430, INS_OR, 'or', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
)


tbl_75 = (\
    (None, None, 0xfcf0, 0x7420, INS_AND, 'and', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7550, INS_CMP, 'cmp', [('rs2', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7400, INS_CMP, 'cmp', [('rs2', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xffff, 0x7560, INS_INT, 'int', [], 2, IF_NONE),
    (None, None, 0xfff0, 0x7540, INS_MOV, 'mov', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7410, INS_MUL, 'mul', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfffff0, 0x757000, INS_MVTIPL, 'mvtipl', [('imm', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfcf0, 0x7430, INS_OR, 'or', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
)


tbl_76 = (\
    (None, None, 0xfcf0, 0x7420, INS_AND, 'and', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7400, INS_CMP, 'cmp', [('rs2', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7410, INS_MUL, 'mul', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7430, INS_OR, 'or', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
)


tbl_77 = (\
    (None, None, 0xfcf0, 0x7420, INS_AND, 'and', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7400, INS_CMP, 'cmp', [('rs2', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7410, INS_MUL, 'mul', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfcf0, 0x7430, INS_OR, 'or', [('rd', ((0, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
)


tbl_7e = (\
    (None, None, 0xfff0, 0x7e20, INS_ABS, 'abs', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7e10, INS_NEG, 'neg', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7e00, INS_NOT, 'not', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7eb0, INS_POP, 'pop', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7ee0, INS_POPC, 'popc', [('cr', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xffc0, 0x7e80, INS_PUSH, 'push', [('sz', ((4, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7ec0, INS_PUSHC, 'pushc', [('cr', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7e50, INS_ROLC, 'rolc', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7e40, INS_RORC, 'rorc', [('rd', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7e30, INS_SAT, 'sat', [('rd', ((0, 15),))], 2, IF_NONE),
)


tbl_7f = (\
    (None, None, 0xfff0, 0x7f40, INS_BRA, 'bra', [('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7f50, INS_BSR, 'bsr', [('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7fb0, INS_CLRPSW, 'clrpsw', [('cb', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7f00, INS_JMP, 'jmp', [('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfff0, 0x7f10, INS_JSR, 'jsr', [('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfffc, 0x7f8c, INS_RMPA, 'rmpa', [('sz', ((0, 3),))], 2, IF_NONE),
    (None, None, 0xffff, 0x7f95, INS_RTE, 'rte', [], 2, IF_NONE),
    (None, None, 0xffff, 0x7f94, INS_RTFI, 'rtfi', [], 2, IF_NONE),
    (None, None, 0xffff, 0x7f93, INS_SATR, 'satr', [], 2, IF_NONE),
    (None, None, 0xffff, 0x7f83, INS_SCMPU, 'scmpu', [], 2, IF_NONE),
    (None, None, 0xfff0, 0x7fa0, INS_SETPSW, 'setpsw', [('cb', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xffff, 0x7f8b, INS_SMOVB, 'smovb', [], 2, IF_NONE),
    (None, None, 0xffff, 0x7f8f, INS_SMOVF, 'smovf', [], 2, IF_NONE),
    (None, None, 0xffff, 0x7f87, INS_SMOVU, 'smovu', [], 2, IF_NONE),
    (None, None, 0xfffc, 0x7f88, INS_SSTR, 'sstr', [('sz', ((0, 3),))], 2, IF_NONE),
    (None, None, 0xfffc, 0x7f80, INS_SUNTIL, 'suntil', [('sz', ((0, 3),))], 2, IF_NONE),
    (None, None, 0xfffc, 0x7f84, INS_SWHILE, 'swhile', [('sz', ((0, 3),))], 2, IF_NONE),
    (None, None, 0xffff, 0x7f96, INS_WAIT, 'wait', [], 2, IF_NONE),
)


tbl_b0 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b1 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b2 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b3 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b4 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b5 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b6 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b7 = (\
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b8 = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_b9 = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_ba = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_bb = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_bc = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_bd = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_be = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_bf = (\
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', [('rd', ((0, 7),)), ('sz', ((11, 1),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
)


tbl_c3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_c7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_cb = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_cc = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_cd = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_ce = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_cf = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_d3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_d7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_db = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_dc = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_dd = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_de = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_df = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_e3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_e7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_eb = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_ec = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_ed = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_ee = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_ef = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f0 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f1 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f2 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f3 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f4 = (\
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', [('ld', ((8, 3),)), ('imm', ((0, 7),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', [('sz', ((0, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
)


tbl_f5 = (\
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', [('ld', ((8, 3),)), ('imm', ((0, 7),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', [('sz', ((0, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
)


tbl_f6 = (\
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', [('ld', ((8, 3),)), ('imm', ((0, 7),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', [('sz', ((0, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
)


tbl_f7 = (\
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', [('ld', ((8, 3),)), ('imm', ((0, 7),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', [('sz', ((0, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
)


tbl_f8 = (\
    (None, None, 0xfc00, 0xf800, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((0, 3),)), ('ld', ((8, 3),)), ('li', ((2, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_f9 = (\
    (None, None, 0xfc00, 0xf800, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((0, 3),)), ('ld', ((8, 3),)), ('li', ((2, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_fa = (\
    (None, None, 0xfc00, 0xf800, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((0, 3),)), ('ld', ((8, 3),)), ('li', ((2, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_fb = (\
    (None, None, 0xff03, 0xfb02, INS_MOV, 'mov', [('rd', ((4, 15),)), ('li', ((2, 3),))], 2, IF_NONE),
    (None, None, 0xfc00, 0xf800, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((0, 3),)), ('ld', ((8, 3),)), ('li', ((2, 3),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
)


tbl_fc = (\
    (None, None, 0xffff00, 0xfc0f00, INS_ABS, 'abs', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc0800, INS_ADC, 'adc', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6400, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6400, INS_BCLR, 'bclr', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffe000, 0xfce000, INS_BMCND, 'bmcnd', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((10, 7),)), ('cd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffe00f, 0xfce00f, INS_BNOT, 'bnot', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('imm', ((10, 7),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6c00, INS_BNOT, 'bnot', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6c00, INS_BNOT, 'bnot', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6000, INS_BSET, 'bset', [('rd', ((4, 15),)), ('ld', ((8, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6800, INS_BTST, 'btst', [('ld', ((8, 3),)), ('rs2', ((4, 15),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6800, INS_BTST, 'btst', [('ld', ((8, 3),)), ('rs2', ((4, 15),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc2000, INS_DIV, 'div', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc2400, INS_DIVU, 'divu', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc1800, INS_EMUL, 'emul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc1c00, INS_EMULU, 'emulu', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc8800, INS_FADD, 'fadd', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc8400, INS_FCMP, 'fcmp', [('ld', ((8, 3),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc9000, INS_FDIV, 'fdiv', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc8c00, INS_FMUL, 'fmul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfca000, INS_FSQRT, 'fsqrt', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc8000, INS_FSUB, 'fsub', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc9400, INS_FTOI, 'ftoi', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfca400, INS_FTOU, 'ftou', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc4400, INS_ITOF, 'itof', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc1000, INS_MAX, 'max', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc1400, INS_MIN, 'min', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xffff00, 0xfc3b00, INS_NOT, 'not', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc9800, INS_ROUND, 'round', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc0000, INS_SBB, 'sbb', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xfcd000, INS_SCCND, 'sccnd', [('rd', ((4, 15),)), ('sz', ((10, 3),)), ('ld', ((8, 3),)), ('cd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfc4b00, INS_STNZ, 'stnz', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfc4b00, INS_STZ, 'stz', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc3000, INS_TST, 'tst', [('ld', ((8, 3),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc5400, INS_UTOF, 'utof', [('ld', ((8, 3),)), ('brd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc4000, INS_XCHG, 'xchg', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc3400, INS_XOR, 'xor', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
)


tbl_fd = (\
    (None, None, 0xfff3f0, 0xfd7020, INS_ADC, 'adc', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xffe000, 0xfde000, INS_BMCND, 'bmcnd', [('rd', ((0, 15),)), ('imm', ((8, 31),)), ('cd', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffe0f0, 0xfde0f0, INS_BNOT, 'bnot', [('rd', ((0, 15),)), ('imm', ((8, 31),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7080, INS_DIV, 'div', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7090, INS_DIVU, 'divu', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0700, INS_EMACA, 'emaca', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd4700, INS_EMSBA, 'emsba', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7060, INS_EMUL, 'emul', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0300, INS_EMULA, 'emula', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7070, INS_EMULU, 'emulu', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfffff0, 0xfd7220, INS_FADD, 'fadd', [('rd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffff0, 0xfd7210, INS_FCMP, 'fcmp', [('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffff0, 0xfd7240, INS_FDIV, 'fdiv', [('rd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffff0, 0xfd7230, INS_FMUL, 'fmul', [('rd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfffff0, 0xfd7200, INS_FSUB, 'fsub', [('rd', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0400, INS_MACHI, 'machi', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0600, INS_MACLH, 'maclh', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0500, INS_MACLO, 'maclo', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7040, INS_MAX, 'max', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7050, INS_MIN, 'min', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfff000, 0xfd2000, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((8, 3),)), ('ad', ((10, 3),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xfd2000, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((8, 3),)), ('ad', ((10, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd2700, INS_MOVCO, 'movco', [('rd', ((4, 15),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd2f00, INS_MOVLI, 'movli', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff200, 0xfd3000, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((8, 1),)), ('ad', ((10, 3),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd4400, INS_MSBHI, 'msbhi', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd4600, INS_MSBLH, 'msblh', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd4500, INS_MSBLO, 'msblo', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0000, INS_MULHI, 'mulhi', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0200, INS_MULLH, 'mullh', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff700, 0xfd0100, INS_MULLO, 'mullo', [('a', ((11, 1),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffe30, 0xfd1e30, INS_MVFACGU, 'mvfacgu', [('a', ((7, 1),)), ('rd', ((0, 15),)), ('imm', ((6, 1), (8, 2)))], 3, IF_NONE),
    (None, None, 0xfffe30, 0xfd1e00, INS_MVFACHI, 'mvfachi', [('a', ((7, 1),)), ('rd', ((0, 15),)), ('imm', ((6, 1), (8, 2)))], 3, IF_NONE),
    (None, None, 0xfffe30, 0xfd1e10, INS_MVFACLO, 'mvfaclo', [('a', ((7, 1),)), ('rd', ((0, 15),)), ('imm', ((6, 1), (8, 2)))], 3, IF_NONE),
    (None, None, 0xfffe30, 0xfd1e20, INS_MVFACMI, 'mvfacmi', [('a', ((7, 1),)), ('rd', ((0, 15),)), ('imm', ((6, 1), (8, 2)))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6a00, INS_MVFC, 'mvfc', [('rd', ((0, 15),)), ('cr', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1730, INS_MVTACGU, 'mvtacgu', [('a', ((7, 1),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1700, INS_MVTACHI, 'mvtachi', [('a', ((7, 1),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1710, INS_MVTACLO, 'mvtaclo', [('a', ((7, 1),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7300, INS_MVTC, 'mvtc', [('cr', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6800, INS_MVTC, 'mvtc', [('cr', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff6f, 0xfd1900, INS_RACL, 'racl', [('a', ((7, 1),)), ('imm', ((4, 1),))], 3, IF_NONE),
    (None, None, 0xffffef, 0xfd1800, INS_RACW, 'racw', [('imm', ((4, 1),))], 3, IF_NONE),
    (None, None, 0xffff6f, 0xfd1940, INS_RDACL, 'rdacl', [('a', ((7, 1),)), ('imm', ((4, 1),))], 3, IF_NONE),
    (None, None, 0xffff6f, 0xfd1840, INS_RDACW, 'rdacw', [('a', ((7, 1),)), ('imm', ((4, 1),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6700, INS_REVL, 'revl', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6500, INS_REVW, 'revw', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffe00, 0xfd6e00, INS_ROTL, 'rotl', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6600, INS_ROTL, 'rotl', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfffe00, 0xfd6c00, INS_ROTR, 'rotr', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6400, INS_ROTR, 'rotr', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6100, INS_SHAR, 'shar', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffe000, 0xfda000, INS_SHAR, 'shar', [('rd', ((0, 15),)), ('imm', ((8, 31),)), ('rs2', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6200, INS_SHLL, 'shll', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffe000, 0xfdc000, INS_SHLL, 'shll', [('rd', ((0, 15),)), ('imm', ((8, 31),)), ('rs2', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6000, INS_SHLR, 'shlr', [('rd', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffe000, 0xfd8000, INS_SHLR, 'shlr', [('rd', ((0, 15),)), ('imm', ((8, 31),)), ('rs2', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd70f0, INS_STNZ, 'stnz', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd70e0, INS_STZ, 'stz', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd70c0, INS_TST, 'tst', [('rs2', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd70d0, INS_XOR, 'xor', [('rd', ((0, 15),)), ('li', ((10, 3),))], 3, IF_NONE),
)


tbl_fe = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xffc000, 0xfe4000, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ri', ((8, 15),)), ('rb', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xffc000, 0xfe0000, INS_MOV, 'mov', [('sz', ((12, 3),)), ('ri', ((8, 15),)), ('rb', ((4, 15),)), ('rs', ((0, 15),))], 3, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xffe000, 0xfec000, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((12, 1),)), ('ri', ((8, 15),)), ('rb', ((4, 15),))], 3, IF_NONE),
)


tbl_ff = (\
    (None, None, 0xfff000, 0xff2000, INS_ADD, 'add', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xff4000, INS_AND, 'and', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xffb000, INS_FMUL, 'fmul', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xff8000, INS_FSUB, 'fsub', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', [('rd', ((0, 15),)), ('sz', ((12, 3),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', [('rd', ((4, 15),)), ('sz', ((12, 3),)), ('ld', ((10, 3),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xfff000, 0xff3000, INS_MUL, 'mul', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xff5000, INS_OR, 'or', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
    (None, None, 0xfff000, 0xff0000, INS_SUB, 'sub', [('rd', ((8, 15),)), ('rs2', ((0, 15),)), ('rs', ((4, 15),))], 3, IF_NONE),
)


tblmain = (\
    (None, None, 0xff, 0x0, INS_BRK, 'brk', [], 1, IF_NONE),
    None,
    (None, None, 0xff, 0x2, INS_RTS, 'rts', [], 1, IF_RET | IF_NOFALL),
    (None, None, 0xff, 0x3, INS_NOP, 'nop', [], 1, IF_NONE),
    (None, None, 0xff000000, 0x4000000, INS_BRA, 'bra', [('pcdsp', ((0, 16777215),))], 4, IF_BRANCH | IF_NOFALL),
    (None, None, 0xff000000, 0x5000000, INS_BSR, 'bsr', [('pcdsp', ((0, 16777215),))], 4, IF_CALL),
    (tbl_6, None, 0, 1, None, None, None, None, IF_NONE),
    None,
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x8, INS_BRA, 'bra', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_NOFALL),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x10, INS_BZ, 'bz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xf8, 0x18, INS_BNZ, 'bnz', [('dsp', ((0, 7),))], 1, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2000, INS_BZ, 'bz', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2100, INS_BNZ, 'bnz', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2200, INS_BGEU, BC, 'bgeu, bc', [('pcdsp', ((0, 255),))], 2, IF_NONE),
    (None, None, 0xff00, 0x2300, INS_BLTU, BNC, 'bltu, bnc', [('pcdsp', ((0, 255),))], 2, IF_NONE),
    (None, None, 0xff00, 0x2400, INS_BGTU, 'bgtu', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2500, INS_BLEU, 'bleu', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2600, INS_BPZ, 'bpz', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2700, INS_BN, 'bn', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2800, INS_BGE, 'bge', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2900, INS_BLT, 'blt', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2a00, INS_BGT, 'bgt', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2b00, INS_BLE, 'ble', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2c00, INS_BO, 'bo', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2d00, INS_BNO, 'bno', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_COND),
    (None, None, 0xff00, 0x2e00, INS_BRA, 'bra', [('pcdsp', ((0, 255),))], 2, IF_BRANCH | IF_NOFALL),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    (None, None, 0xff0000, 0x380000, INS_BRA, 'bra', [('pcdsp', ((0, 65535),))], 3, IF_BRANCH | IF_NOFALL),
    (None, None, 0xff0000, 0x390000, INS_BSR, 'bsr', [('pcdsp', ((0, 65535),))], 3, IF_CALL),
    (None, None, 0xff0000, 0x3a0000, INS_BZ, 'bz', [('pcdsp', ((0, 65535),))], 3, IF_BRANCH | IF_COND),
    (None, None, 0xff0000, 0x3b0000, INS_BNZ, 'bnz', [('pcdsp', ((0, 65535),))], 3, IF_BRANCH | IF_COND),
    (None, None, 0xfc00, 0x3c00, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((8, 3),)), ('dsp', ((7, 16), (0, 15)))], 2, IF_NONE),
    (None, None, 0xfc00, 0x3c00, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((8, 3),)), ('dsp', ((7, 16), (0, 15)))], 2, IF_NONE),
    (None, None, 0xfc00, 0x3c00, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((8, 3),)), ('dsp', ((7, 16), (0, 15)))], 2, IF_NONE),
    (tbl_3f, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xfc00, 0x4000, INS_SUB, 'sub', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4000, INS_SUB, 'sub', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4000, INS_SUB, 'sub', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4000, INS_SUB, 'sub', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4400, INS_CMP, 'cmp', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4400, INS_CMP, 'cmp', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4400, INS_CMP, 'cmp', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4400, INS_CMP, 'cmp', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4800, INS_ADD, 'add', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4800, INS_ADD, 'add', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4800, INS_ADD, 'add', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4800, INS_ADD, 'add', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4c00, INS_MUL, 'mul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4c00, INS_MUL, 'mul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4c00, INS_MUL, 'mul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x4c00, INS_MUL, 'mul', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5000, INS_AND, 'and', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5000, INS_AND, 'and', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5000, INS_AND, 'and', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5000, INS_AND, 'and', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5400, INS_OR, 'or', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5400, INS_OR, 'or', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5400, INS_OR, 'or', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x5400, INS_OR, 'or', [('rd', ((0, 15),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', [('rd', ((0, 15),)), ('sz', ((10, 1),)), ('ld', ((8, 3),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6000, INS_SUB, 'sub', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6100, INS_CMP, 'cmp', [('imm', ((4, 15),)), ('rs2', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6200, INS_ADD, 'add', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6300, INS_MUL, 'mul', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6400, INS_AND, 'and', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6500, INS_OR, 'or', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6600, INS_MOV, 'mov', [('rd', ((0, 15),)), ('imm', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff, 0x67, INS_RTSD, 'rtsd', [], 1, IF_RET | IF_NOFALL),
    (None, None, 0xfe00, 0x6800, INS_SHLR, 'shlr', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x6800, INS_SHLR, 'shlr', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x6a00, INS_SHAR, 'shar', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x6a00, INS_SHAR, 'shar', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x6c00, INS_SHLL, 'shll', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x6c00, INS_SHLL, 'shll', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6e00, INS_PUSHM, 'pushm', [('rs2', ((0, 15),)), ('rs', ((4, 15),))], 2, IF_NONE),
    (None, None, 0xff00, 0x6f00, INS_POPM, 'popm', [('rd', ((4, 15),)), ('rd2', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', [('rd', ((0, 15),)), ('rs2', ((4, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', [('rd', ((0, 15),)), ('rs2', ((4, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', [('rd', ((0, 15),)), ('rs2', ((4, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', [('rd', ((0, 15),)), ('rs2', ((4, 15),)), ('li', ((8, 3),))], 2, IF_NONE),
    (tbl_74, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_75, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_76, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_77, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xfe00, 0x7800, INS_BSET, 'bset', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x7800, INS_BSET, 'bset', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x7a00, INS_BCLR, 'bclr', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x7a00, INS_BCLR, 'bclr', [('rd', ((0, 15),)), ('imm', ((4, 31),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x7c00, INS_BTST, 'btst', [('imm', ((4, 31),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (None, None, 0xfe00, 0x7c00, INS_BTST, 'btst', [('imm', ((4, 31),)), ('rs', ((0, 15),))], 2, IF_NONE),
    (tbl_7e, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_7f, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', [('rd', ((4, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((0, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', [('rd', ((0, 7),)), ('sz', ((12, 3),)), ('dsp', ((3, 1), (7, 30))), ('rs', ((4, 7),))], 2, IF_NONE),
    (tbl_b0, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b1, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b2, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b3, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b4, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b5, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b6, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b7, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b8, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_b9, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ba, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_bb, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_bc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_bd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_be, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_bf, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_c3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_c7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_cb, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ce, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cf, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_d3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_d7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_db, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_dc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_dd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_de, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_df, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_e3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_e7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (None, None, 0xc000, 0xc000, INS_MOV, 'mov', [('lds', ((8, 3),)), ('sz', ((12, 3),)), ('rd', ((0, 15),)), ('rs', ((4, 15),)), ('ldd', ((10, 3),))], 2, IF_NONE),
    (tbl_eb, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ec, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ed, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ee, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ef, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f0, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f1, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f2, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f3, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f4, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f5, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f6, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f7, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f8, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_f9, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_fa, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_fb, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_fc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_fd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_fe, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ff, None, 0, 1, None, None, None, None, IF_NONE),
)

