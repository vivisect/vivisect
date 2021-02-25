from .const import *
tbl_6 = (\
    (None, FORM_RD_LD_RS_L, 0xfffcff00, 0x6a00000, INS_SBB, 'sbb', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200200, INS_ADC, 'adc', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200800, INS_DIV, 'div', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200900, INS_DIVU, 'divu', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200600, INS_EMUL, 'emul', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200700, INS_EMULU, 'emulu', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6201100, INS_ITOF, 'itof', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200400, INS_MAX, 'max', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200500, INS_MIN, 'min', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, None, 0xff3cff00, 0x6200c00, INS_TST, 'tst', ((O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6201500, INS_UTOF, 'utof', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6201000, INS_XCHG, 'xchg', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3cff00, 0x6200d00, INS_XOR, 'xor', ((O_RD, ((0, 0xf),)), (O_LDS, ((16, 0x3),)), (O_MI, ((22, 0x3),)), (O_RS, ((4, 0xf),)), ), 4, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x60800, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x61000, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x60400, INS_CMP, 'cmp', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x60c00, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x61400, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_MI_RS, 0xff3c00, 0x60000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_MI, ((14, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
)


tbl_3f = (\
    (None, FORM_RTSD, 0xff0000, 0x3f0000, INS_RTSD, 'rtsd', ((O_RD, ((12, 0xf),)), (O_UIMM, ((0, 0xff),)), (O_RD2, ((8, 0xf),)), ), 3, IF_RET | IF_NOFALL),
    (None, None, 0xfc0000, 0x3c0000, INS_MOV, 'mov', ((O_RD, ((12, 0x7),)), (O_SZ, ((16, 0x3),)), (O_IMM, ((0, 0xff),)), (O_DSPD, ((11, 0x10), (8, 0xf),)), ), 3, IF_NONE),
)


tbl_74 = (\
    (None, FORM_RD_LI, 0xfcf0, 0x7420, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RS2_LI, 0xfcf0, 0x7400, INS_CMP, 'cmp', ((O_RS2, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7410, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7430, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
)


tbl_75 = (\
    (None, None, 0xfffff0, 0x757000, INS_MVTIPL, 'mvtipl', ((O_IMM, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0x756000, INS_INT, 'int', ((O_IMM, ((0, 0xff),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0x755000, INS_CMP, 'cmp', ((O_UIMM, ((0, 0xff),)), (O_RS2, ((8, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0x754000, INS_MOV, 'mov', ((O_RD, ((8, 0xf),)), (O_UIMM, ((0, 0xff),)), ), 3, IF_LONG),
    (None, FORM_RD_LI, 0xfcf0, 0x7420, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RS2_LI, 0xfcf0, 0x7400, INS_CMP, 'cmp', ((O_RS2, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7410, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7430, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
)


tbl_76 = (\
    (None, FORM_RD_LI, 0xfcf0, 0x7420, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RS2_LI, 0xfcf0, 0x7400, INS_CMP, 'cmp', ((O_RS2, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7410, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7430, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
)


tbl_77 = (\
    (None, FORM_RD_LI, 0xfcf0, 0x7420, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RS2_LI, 0xfcf0, 0x7400, INS_CMP, 'cmp', ((O_RS2, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7410, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, FORM_RD_LI, 0xfcf0, 0x7430, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
)


tbl_7e = (\
    (None, None, 0xfff0, 0x7e20, INS_ABS, 'abs', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7e10, INS_NEG, 'neg', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7e00, INS_NOT, 'not', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7eb0, INS_POP, 'pop', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7ee0, INS_POPC, 'popc', ((O_CR, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7ec0, INS_PUSHC, 'pushc', ((O_CR, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7e50, INS_ROLC, 'rolc', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7e40, INS_RORC, 'rorc', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7e30, INS_SAT, 'sat', ((O_RD, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xffc0, 0x7e80, INS_PUSH, 'push', ((O_SZ, ((4, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
)


tbl_7f = (\
    (None, None, 0xffff, 0x7f95, INS_RTE, 'rte', (), 2, IF_RET | IF_NOFALL),
    (None, None, 0xffff, 0x7f94, INS_RTFI, 'rtfi', (), 2, IF_RET | IF_NOFALL),
    (None, None, 0xffff, 0x7f93, INS_SATR, 'satr', (), 2, IF_NONE),
    (None, None, 0xffff, 0x7f83, INS_SCMPU, 'scmpu', (), 2, IF_NONE),
    (None, None, 0xffff, 0x7f8b, INS_SMOVB, 'smovb', (), 2, IF_REPEAT),
    (None, None, 0xffff, 0x7f8f, INS_SMOVF, 'smovf', (), 2, IF_REPEAT),
    (None, None, 0xffff, 0x7f87, INS_SMOVU, 'smovu', (), 2, IF_REPEAT),
    (None, None, 0xffff, 0x7f96, INS_WAIT, 'wait', (), 2, IF_PRIV),
    (None, None, 0xfffc, 0x7f8c, INS_RMPA, 'rmpa', ((O_SZ, ((0, 0x3),)), ), 2, IF_NONE),
    (None, None, 0xfffc, 0x7f88, INS_SSTR, 'sstr', ((O_SZ, ((0, 0x3),)), ), 2, IF_REPEAT),
    (None, None, 0xfffc, 0x7f80, INS_SUNTIL, 'suntil', ((O_SZ, ((0, 0x3),)), ), 2, IF_REPEAT),
    (None, None, 0xfffc, 0x7f84, INS_SWHILE, 'swhile', ((O_SZ, ((0, 0x3),)), ), 2, IF_REPEAT),
    (None, None, 0xfff0, 0x7f40, INS_BRA, 'bra', ((O_RS, ((0, 0xf),)), ), 2, IF_BRANCH | IF_NOFALL | IF_LONG),
    (None, None, 0xfff0, 0x7f50, INS_BSR, 'bsr', ((O_RS, ((0, 0xf),)), ), 2, IF_CALL | IF_LONG),
    (None, None, 0xfff0, 0x7fb0, INS_CLRPSW, 'clrpsw', ((O_CB, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfff0, 0x7f00, INS_JMP, 'jmp', ((O_RS, ((0, 0xf),)), ), 2, IF_BRANCH | IF_NOFALL),
    (None, None, 0xfff0, 0x7f10, INS_JSR, 'jsr', ((O_RS, ((0, 0xf),)), ), 2, IF_CALL),
    (None, None, 0xfff0, 0x7fa0, INS_SETPSW, 'setpsw', ((O_CB, ((0, 0xf),)), ), 2, IF_NONE),
)


tbl_b0 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b1 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b2 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b3 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b4 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b5 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b6 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b7 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
)


tbl_b8 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_b9 = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_ba = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_bb = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_bc = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_bd = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_be = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_bf = (\
    (None, None, 0xf000, 0xb000, INS_MOVU, 'movu', ((O_RD, ((0, 0x7),)), (O_SZ, ((11, 0x1),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
)


tbl_c3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_c7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_cb = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_cc = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_cd = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ce = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_cf = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_d3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_d7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_db = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_dc = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_dd = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_de = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_df = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_e3 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_e7 = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_eb = (\
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ec = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ed = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ee = (\
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ef = (\
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f0 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f1 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f2 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f3 = (\
    (None, None, 0xfc08, 0xf008, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f4 = (\
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', ((O_SZ, ((0, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', ((O_LDS, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f5 = (\
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', ((O_SZ, ((0, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', ((O_LDS, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f6 = (\
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', ((O_SZ, ((0, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', ((O_LDS, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f7 = (\
    (None, None, 0xfc0c, 0xf408, INS_PUSH, 'push', ((O_SZ, ((0, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfc08, 0xf400, INS_BTST, 'btst', ((O_LDS, ((8, 0x3),)), (O_IMM, ((0, 0x7),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f8 = (\
    (None, FORM_MOV_RD_SZ_LD_LI, 0xfc00, 0xf800, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((0, 0x3),)), (O_LDD, ((8, 0x3),)), (O_LI, ((2, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_f9 = (\
    (None, FORM_MOV_RD_SZ_LD_LI, 0xfc00, 0xf800, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((0, 0x3),)), (O_LDD, ((8, 0x3),)), (O_LI, ((2, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_fa = (\
    (None, FORM_MOV_RD_SZ_LD_LI, 0xfc00, 0xf800, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((0, 0x3),)), (O_LDD, ((8, 0x3),)), (O_LI, ((2, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_fb = (\
    (None, FORM_RD_LI, 0xff03, 0xfb02, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_LI, ((2, 0x3),)), ), 2, IF_LONG),
    (None, FORM_MOV_RD_SZ_LD_LI, 0xfc00, 0xf800, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((0, 0x3),)), (O_LDD, ((8, 0x3),)), (O_LI, ((2, 0x3),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_fc = (\
    (None, None, 0xffff00, 0xfc0f00, INS_ABS, 'abs', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfc0700, INS_NEG, 'neg', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfc3b00, INS_NOT, 'not', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfc0300, INS_SBB, 'sbb', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfc4f00, INS_STNZ, 'stnz', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_COND),
    (None, None, 0xffff00, 0xfc4b00, INS_STZ, 'stz', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_COND),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc0800, INS_ADC, 'adc', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc6400, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc6400, INS_BCLR, 'bclr', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_B, 0xfffc00, 0xfc6c00, INS_BNOT, 'bnot', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_B, 0xfffc00, 0xfc6c00, INS_BNOT, 'bnot', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_B, 0xfffc00, 0xfc6000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_B, 0xfffc00, 0xfc6000, INS_BSET, 'bset', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6800, INS_BTST, 'btst', ((O_LDS2, ((8, 0x3),)), (O_RS2, ((4, 0xf),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfffc00, 0xfc6800, INS_BTST, 'btst', ((O_LDS2, ((8, 0x3),)), (O_RS2, ((4, 0xf),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc2000, INS_DIV, 'div', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc2400, INS_DIVU, 'divu', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc1800, INS_EMUL, 'emul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc1c00, INS_EMULU, 'emulu', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc8800, INS_FADD, 'fadd', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_LD_RS2_RS_L, 0xfffc00, 0xfc8400, INS_FCMP, 'fcmp', ((O_LDS, ((8, 0x3),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc9000, INS_FDIV, 'fdiv', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc8c00, INS_FMUL, 'fmul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfca000, INS_FSQRT, 'fsqrt', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc8000, INS_FSUB, 'fsub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc9400, INS_FTOI, 'ftoi', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfca400, INS_FTOU, 'ftou', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc4400, INS_ITOF, 'itof', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc1000, INS_MAX, 'max', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc1400, INS_MIN, 'min', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS_L, 0xfffc00, 0xfc9800, INS_ROUND, 'round', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_LD_RS2_RS_UB, 0xfffc00, 0xfc3000, INS_TST, 'tst', ((O_LDS, ((8, 0x3),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc5400, INS_UTOF, 'utof', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc4000, INS_XCHG, 'xchg', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfffc00, 0xfc3400, INS_XOR, 'xor', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_SCCND, 0xfff000, 0xfcd000, INS_SCCND, 'sccnd', ((O_RD, ((4, 0xf),)), (O_SZ, ((10, 0x3),)), (O_LDD, ((8, 0x3),)), (O_CD, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffe00f, 0xfce00f, INS_BNOT, 'bnot', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((10, 0x7),)), ), 3, IF_NONE),
    (None, FORM_BMCND, 0xffe000, 0xfce000, INS_BMCND, 'bmcnd', ((O_RD, ((4, 0xf),)), (O_LDD, ((8, 0x3),)), (O_IMM, ((10, 0x7),)), (O_CD, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_fd = (\
    (None, FORM_RD_IMM, 0xfffff000000000, 0xfd722000000000, INS_FADD, 'fadd', ((O_RD, ((32, 0xf),)), (O_IMM, ((0, 0xffffffff),)), ), 7, IF_NONE),
    (None, None, 0xfffff000000000, 0xfd721000000000, INS_FCMP, 'fcmp', ((O_IMM, ((0, 0xffffffff),)), (O_RS, ((32, 0xf),)), ), 7, IF_NONE),
    (None, FORM_RD_IMM, 0xfffff000000000, 0xfd724000000000, INS_FDIV, 'fdiv', ((O_RD, ((32, 0xf),)), (O_IMM, ((0, 0xffffffff),)), ), 7, IF_NONE),
    (None, FORM_RD_IMM, 0xfffff000000000, 0xfd723000000000, INS_FMUL, 'fmul', ((O_RD, ((32, 0xf),)), (O_IMM, ((0, 0xffffffff),)), ), 7, IF_NONE),
    (None, FORM_RD_IMM, 0xfffff000000000, 0xfd720000000000, INS_FSUB, 'fsub', ((O_RD, ((32, 0xf),)), (O_IMM, ((0, 0xffffffff),)), ), 7, IF_NONE),
    (None, FORM_IMM1, 0xffff6f, 0xfd1900, INS_RACL, 'racl', ((O_A, ((7, 0x1),)), (O_IMM, ((4, 0x1),)), ), 3, IF_NONE),
    (None, FORM_IMM1, 0xffff6f, 0xfd1800, INS_RACW, 'racw', ((O_A, ((7, 0x1),)), (O_IMM, ((4, 0x1),)), ), 3, IF_NONE),
    (None, FORM_IMM1, 0xffff6f, 0xfd1940, INS_RDACL, 'rdacl', ((O_A, ((7, 0x1),)), (O_IMM, ((4, 0x1),)), ), 3, IF_NONE),
    (None, FORM_IMM1, 0xffff6f, 0xfd1840, INS_RDACW, 'rdacw', ((O_A, ((7, 0x1),)), (O_IMM, ((4, 0x1),)), ), 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1730, INS_MVTACGU, 'mvtacgu', ((O_A, ((7, 0x1),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1700, INS_MVTACHI, 'mvtachi', ((O_A, ((7, 0x1),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff70, 0xfd1710, INS_MVTACLO, 'mvtaclo', ((O_A, ((7, 0x1),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd2700, INS_MOVCO, 'movco', ((O_RD, ((4, 0xf),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_MOVLI, 0xffff00, 0xfd2f00, INS_MOVLI, 'movli', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6a00, INS_MVFC, 'mvfc', ((O_RD, ((0, 0xf),)), (O_CR, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6800, INS_MVTC, 'mvtc', ((O_CR, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6700, INS_REVL, 'revl', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6500, INS_REVW, 'revw', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6600, INS_ROTL, 'rotl', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6400, INS_ROTR, 'rotr', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6100, INS_SHAR, 'shar', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6200, INS_SHLL, 'shll', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffff00, 0xfd6000, INS_SHLR, 'shlr', ((O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_MVFA, 0xfffe30, 0xfd1e30, INS_MVFACGU, 'mvfacgu', ((O_A, ((7, 0x1),)), (O_RD, ((0, 0xf),)), (O_IMM, ((6, 0x1), (7, 0x2),)), ), 3, IF_NONE),
    (None, FORM_MVFA, 0xfffe30, 0xfd1e00, INS_MVFACHI, 'mvfachi', ((O_A, ((7, 0x1),)), (O_RD, ((0, 0xf),)), (O_IMM, ((6, 0x1), (7, 0x2),)), ), 3, IF_NONE),
    (None, FORM_MVFA, 0xfffe30, 0xfd1e10, INS_MVFACLO, 'mvfaclo', ((O_A, ((7, 0x1),)), (O_RD, ((0, 0xf),)), (O_IMM, ((6, 0x1), (7, 0x2),)), ), 3, IF_NONE),
    (None, FORM_MVFA, 0xfffe30, 0xfd1e20, INS_MVFACMI, 'mvfacmi', ((O_A, ((7, 0x1),)), (O_RD, ((0, 0xf),)), (O_IMM, ((6, 0x1), (7, 0x2),)), ), 3, IF_NONE),
    (None, FORM_RD_IMM, 0xfffe00, 0xfd6e00, INS_ROTL, 'rotl', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 3, IF_NONE),
    (None, FORM_RD_IMM, 0xfffe00, 0xfd6c00, INS_ROTR, 'rotr', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 3, IF_NONE),
    (None, FORM_AD, 0xfff800, 0xfd2000, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((8, 0x3),)), (O_ADD, ((10, 0x1),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, FORM_AD, 0xfff800, 0xfd2800, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((8, 0x3),)), (O_ADS, ((10, 0x1),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7020, INS_ADC, 'adc', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7080, INS_DIV, 'div', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7090, INS_DIVU, 'divu', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7060, INS_EMUL, 'emul', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7070, INS_EMULU, 'emulu', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7040, INS_MAX, 'max', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd7050, INS_MIN, 'min', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, None, 0xfff3f0, 0xfd7300, INS_MVTC, 'mvtc', ((O_CR, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd70f0, INS_STNZ, 'stnz', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_COND),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd70e0, INS_STZ, 'stz', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_COND),
    (None, FORM_RS2_LI, 0xfff3f0, 0xfd70c0, INS_TST, 'tst', ((O_RS2, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_RD_LI, 0xfff3f0, 0xfd70d0, INS_XOR, 'xor', ((O_RD, ((0, 0xf),)), (O_LI, ((10, 0x3),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0700, INS_EMACA, 'emaca', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd4700, INS_EMSBA, 'emsba', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0300, INS_EMULA, 'emula', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0400, INS_MACHI, 'machi', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0600, INS_MACLH, 'maclh', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0500, INS_MACLO, 'maclo', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd4400, INS_MSBHI, 'msbhi', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd4600, INS_MSBLH, 'msblh', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd4500, INS_MSBLO, 'msblo', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0000, INS_MULHI, 'mulhi', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0200, INS_MULLH, 'mullh', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_A_RS2_RS, 0xfff700, 0xfd0100, INS_MULLO, 'mullo', ((O_A, ((11, 0x1),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_AD, 0xfff200, 0xfd3000, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((8, 0x1),)), (O_ADS, ((10, 0x3),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_RD_IMM, 0xffe0f0, 0xfde0f0, INS_BNOT, 'bnot', ((O_RD, ((0, 0xf),)), (O_IMM, ((8, 0x1f),)), ), 3, IF_NONE),
    (None, FORM_BMCND, 0xffe000, 0xfde000, INS_BMCND, 'bmcnd', ((O_RD, ((0, 0xf),)), (O_IMM, ((8, 0x1f),)), (O_CD, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffe000, 0xfda000, INS_SHAR, 'shar', ((O_RD, ((0, 0xf),)), (O_IMM, ((8, 0x1f),)), (O_RS2, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffe000, 0xfdc000, INS_SHLL, 'shll', ((O_RD, ((0, 0xf),)), (O_IMM, ((8, 0x1f),)), (O_RS2, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xffe000, 0xfd8000, INS_SHLR, 'shlr', ((O_RD, ((0, 0xf),)), (O_IMM, ((8, 0x1f),)), (O_RS2, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_fe = (\
    (None, FORM_MOV_RI_RB, 0xffe000, 0xfec000, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x1),)), (O_RI, ((8, 0xf),)), (O_RB, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_MOV_RI_RB, 0xffc000, 0xfe4000, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_RI, ((8, 0xf),)), (O_RB, ((4, 0xf),)), ), 3, IF_NONE),
    (None, FORM_MOV_RI_RB, 0xffc000, 0xfe0000, INS_MOV, 'mov', ((O_SZ, ((12, 0x3),)), (O_RI, ((8, 0xf),)), (O_RB, ((4, 0xf),)), (O_RS, ((0, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tbl_ff = (\
    (None, None, 0xfff000, 0xff2000, INS_ADD, 'add', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xff4000, INS_AND, 'and', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xffa000, INS_FADD, 'fadd', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xffb000, INS_FMUL, 'fmul', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xff8000, INS_FSUB, 'fsub', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xff3000, INS_MUL, 'mul', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xff5000, INS_OR, 'or', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfff000, 0xff0000, INS_SUB, 'sub', ((O_RD, ((8, 0xf),)), (O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xcf00, 0xcf00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xcc00, 0xcc00, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xc300, 0xc300, INS_MOV, 'mov', ((O_RD, ((4, 0xf),)), (O_SZ, ((12, 0x3),)), (O_LDD, ((10, 0x3),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
)


tblmain = (\
    (None, None, 0xff, 0x0, INS_BRK, 'brk', (), 1, IF_NONE),
    None,
    (None, None, 0xff, 0x2, INS_RTS, 'rts', (), 1, IF_RET | IF_NOFALL),
    (None, None, 0xff, 0x3, INS_NOP, 'nop', (), 1, IF_NONE),
    (None, FORM_PCDSP, 0xff000000, 0x4000000, INS_BRA, 'bra', ((O_PCDSP, ((0, 0xffffff),)), ), 4, IF_BRANCH | IF_NOFALL | IF_24BIT),
    (None, FORM_PCDSP, 0xff000000, 0x5000000, INS_BSR, 'bsr', ((O_PCDSP, ((0, 0xffffff),)), ), 4, IF_CALL | IF_24BIT),
    (tbl_6, None, 0, 1, None, None, None, None, IF_NONE),
    None,
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x8, INS_BRA, 'bra', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_NOFALL | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x10, INS_BZ, 'bz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xf8, 0x18, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0x7),)), ), 1, IF_BRANCH | IF_COND | IF_SMALL),
    (None, FORM_PCDSP, 0xff00, 0x2000, INS_BZ, 'bz', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2100, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2200, INS_BGEU, 'bgeu', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2300, INS_BLTU, 'bltu', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2400, INS_BGTU, 'bgtu', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2500, INS_BLEU, 'bleu', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2600, INS_BPZ, 'bpz', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2700, INS_BN, 'bn', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2800, INS_BGE, 'bge', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2900, INS_BLT, 'blt', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2a00, INS_BGT, 'bgt', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2b00, INS_BLE, 'ble', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2c00, INS_BO, 'bo', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2d00, INS_BNO, 'bno', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_COND | IF_BYTE),
    (None, FORM_PCDSP, 0xff00, 0x2e00, INS_BRA, 'bra', ((O_PCDSP, ((0, 0xff),)), ), 2, IF_BRANCH | IF_NOFALL | IF_BYTE),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    (None, FORM_PCDSP, 0xff0000, 0x380000, INS_BRA, 'bra', ((O_PCDSP, ((0, 0xffff),)), ), 3, IF_BRANCH | IF_NOFALL | IF_WORD),
    (None, FORM_PCDSP, 0xff0000, 0x390000, INS_BSR, 'bsr', ((O_PCDSP, ((0, 0xffff),)), ), 3, IF_CALL | IF_WORD),
    (None, FORM_PCDSP, 0xff0000, 0x3a0000, INS_BZ, 'bz', ((O_PCDSP, ((0, 0xffff),)), ), 3, IF_BRANCH | IF_COND | IF_WORD),
    (None, FORM_PCDSP, 0xff0000, 0x3b0000, INS_BNZ, 'bnz', ((O_PCDSP, ((0, 0xffff),)), ), 3, IF_BRANCH | IF_COND | IF_WORD),
    (None, None, 0xfc0000, 0x3c0000, INS_MOV, 'mov', ((O_RD, ((12, 0x7),)), (O_SZ, ((16, 0x3),)), (O_IMM, ((0, 0xff),)), (O_DSPD, ((11, 0x10), (8, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfc0000, 0x3c0000, INS_MOV, 'mov', ((O_RD, ((12, 0x7),)), (O_SZ, ((16, 0x3),)), (O_IMM, ((0, 0xff),)), (O_DSPD, ((11, 0x10), (8, 0xf),)), ), 3, IF_NONE),
    (None, None, 0xfc0000, 0x3c0000, INS_MOV, 'mov', ((O_RD, ((12, 0x7),)), (O_SZ, ((16, 0x3),)), (O_IMM, ((0, 0xff),)), (O_DSPD, ((11, 0x10), (8, 0xf),)), ), 3, IF_NONE),
    (tbl_3f, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4400, INS_CMP, 'cmp', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4400, INS_CMP, 'cmp', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4400, INS_CMP, 'cmp', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4400, INS_CMP, 'cmp', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4800, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4800, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4800, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4800, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4c00, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4c00, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4c00, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x4c00, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5000, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5000, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5000, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5000, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5400, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5400, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5400, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_LD_RS, 0xfc00, 0x5400, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xf800, 0x5800, INS_MOVU, 'movu', ((O_RD, ((0, 0xf),)), (O_SZ, ((10, 0x1),)), (O_LDS, ((8, 0x3),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6000, INS_SUB, 'sub', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xff00, 0x6100, INS_CMP, 'cmp', ((O_IMM, ((4, 0xf),)), (O_RS2, ((0, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6200, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6300, INS_MUL, 'mul', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6400, INS_AND, 'and', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6500, INS_OR, 'or', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xff00, 0x6600, INS_MOV, 'mov', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0xf),)), ), 2, IF_LONG),
    (None, FORM_RTSD, 0xff00, 0x6700, INS_RTSD, 'rtsd', ((O_UIMM, ((0, 0xff),)), ), 2, IF_RET | IF_NOFALL),
    (None, FORM_RD_IMM, 0xfe00, 0x6800, INS_SHLR, 'shlr', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x6800, INS_SHLR, 'shlr', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x6a00, INS_SHAR, 'shar', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x6a00, INS_SHAR, 'shar', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x6c00, INS_SHLL, 'shll', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x6c00, INS_SHLL, 'shll', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, None, 0xff00, 0x6e00, INS_PUSHM, 'pushm', ((O_RS2, ((0, 0xf),)), (O_RS, ((4, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xff00, 0x6f00, INS_POPM, 'popm', ((O_RD, ((4, 0xf),)), (O_RD2, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_RS2, ((4, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_RS2, ((4, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_RS2, ((4, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (None, None, 0xfc00, 0x7000, INS_ADD, 'add', ((O_RD, ((0, 0xf),)), (O_RS2, ((4, 0xf),)), (O_LI, ((8, 0x3),)), ), 2, IF_NONE),
    (tbl_74, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_75, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_76, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_77, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x7800, INS_BSET, 'bset', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x7800, INS_BSET, 'bset', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x7a00, INS_BCLR, 'bclr', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, FORM_RD_IMM, 0xfe00, 0x7a00, INS_BCLR, 'bclr', ((O_RD, ((0, 0xf),)), (O_IMM, ((4, 0x1f),)), ), 2, IF_NONE),
    (None, None, 0xfe00, 0x7c00, INS_BTST, 'btst', ((O_IMM, ((4, 0x1f),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (None, None, 0xfe00, 0x7c00, INS_BTST, 'btst', ((O_IMM, ((4, 0x1f),)), (O_RS, ((0, 0xf),)), ), 2, IF_NONE),
    (tbl_7e, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_7f, None, 0, 1, None, None, None, None, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8000, INS_MOV, 'mov', ((O_RD, ((4, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPD, ((3, 0x1), (6, 0x1e),)), (O_RS, ((0, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
    (None, None, 0xc800, 0x8800, INS_MOV, 'mov', ((O_RD, ((0, 0x7),)), (O_SZ, ((12, 0x3),)), (O_DSPS, ((3, 0x1), (6, 0x1e),)), (O_RS, ((4, 0x7),)), ), 2, IF_NONE),
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
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_c3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_c7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_cb, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_ce, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_cf, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_d3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_d7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_db, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_dc, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_dd, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_de, None, 0, 1, None, None, None, None, IF_NONE),
    (tbl_df, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_e3, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (tbl_e7, None, 0, 1, None, None, None, None, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
    (None, FORM_GOOGOL, 0xc000, 0xc000, INS_MOV, 'mov', ((O_LDS, ((8, 0x3),)), (O_SZ, ((12, 0x3),)), (O_RD, ((0, 0xf),)), (O_RS, ((4, 0xf),)), (O_LDD, ((10, 0x3),)), ), 2, IF_NONE),
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

