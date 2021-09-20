
MASK_A          = 0x20000000            # 00100000 00000000 00000000 00000000
MASK_ASI        = 0x00001fe0            # 00000000 00000000 00011111 11100000
MASK_COND       = 0x1e000000            # 00011110 00000000 00000000 00000000
MASK_DISP22     = 0x003fffff            # 00000000 00111111 11111111 11111111
MASK_IMM22      = 0x003fffff            # 00000000 00111111 11111111 11111111
MASK_DISP30     = 0x3fffffff            # 00111111 11111111 11111111 11111111
MASK_I          = 0x00002000            # 00000000 00000000 00100000 00000000
MASK_OP         = 0xc0000000            # 11000000 00000000 00000000 00000000
MASK_OP2        = 0x01c00000            # 00000001 11000000 00000000 00000000
MASK_OP3        = 0x01f80000            # 00000001 11111000 00000000 00000000
MASK_OPC        = 0x00003fe0            # 00000000 00000000 00111111 11100000
MASK_OPF        = 0x00003fe0            # 00000000 00000000 00111111 11100000
MASK_RD         = 0x3e000000            # 00111110 00000000 00000000 00000000
MASK_RS1        = 0x0007c000            # 00000000 00000111 11000000 00000000
MASK_RS2        = 0x0000001f            # 00000000 00000000 00000000 00011111
MASK_SHCNT      = 0x0000001f            # 00000000 00000000 00000000 00011111
MASK_SIMM13     = 0x00001fff            # 00000000 00000000 00011111 11111111


SHIFT_A          = 29
SHIFT_ASI        = 5
SHIFT_COND       = 25
SHIFT_DISP22     = 0
SHIFT_DISP30     = 0
SHIFT_I          = 13
SHIFT_OP         = 30
SHIFT_OP2        = 22
SHIFT_OP3        = 19
SHIFT_OPC        = 5
SHIFT_OPF        = 5
SHIFT_RD         = 25
SHIFT_RS1        = 14
SHIFT_RS2        = 0
SHIFT_SHCNT      = 0
SHIFT_SIMM13     = 0

OP2_SETHI = 4

m_op2_sethi_mnemonic = "sethi {imm22}, {regrd}"

# Memory Load/Store instructions, OP = 3, Format 3a or 3b

M_OP3_LD = 0
M_OP3_LDA = 16
M_OP3_LDC = 48
M_OP3_LDCSR = 49
M_OP3_LDD = 3
M_OP3_LDDA = 19
M_OP3_LDDC = 51
M_OP3_LDDF = 35
M_OP3_LDF = 32
M_OP3_LDFSR = 33
M_OP3_LDSB = 9
M_OP3_LDSBA = 25
M_OP3_LDSH = 10
M_OP3_LDSHA = 26
M_OP3_LDSTUB = 13
M_OP3_LDSTUBA = 29
M_OP3_LDUB = 1
M_OP3_LDUBA = 17
M_OP3_LDUH = 2
M_OP3_LDUHA = 18
M_OP3_ST = 4
M_OP3_STA = 20
M_OP3_STB = 5
M_OP3_STBA = 21
M_OP3_STC = 52
M_OP3_STCSR = 53
M_OP3_STD = 7
M_OP3_STDA = 23
M_OP3_STDC = 55
M_OP3_STDCQ = 54
M_OP3_STDF = 39
M_OP3_STDFQ = 38
M_OP3_STF = 36
M_OP3_STFSR = 37
M_OP3_STH = 6
M_OP3_STHA = 22
M_OP3_SWAP = 15
M_OP3_SWAPA = 31

m_op3_table = {
    0 : "LD",
    1 : "LDUB",
    2 : "LDUH",
    3 : "LDD",
    4 : "ST",
    5 : "STB",
    6 : "STH",
    7 : "STD",
    9 : "LDSB",
    10 : "LDSH",
    13 : "LDSTUB",
    15 : "SWAP", 
    16 : "LDA",
    17 : "LDUBA",
    18 : "LDUHA",
    19 : "LDDA",
    20 : "STA",
    21 : "STBA",
    22 : "STHA",
    23 : "STDA",
    25 : "LDSBA",
    26 : "LDSHA",
    29 : "LDSTUBA",
    31 : "SWAPA",
    32 : "LDF",
    33 : "LDFSR",
    35 : "LDDF",
    36 : "STF",
    37 : "STFSR",
    38 : "STDFQ",
    39 : "STDF",
    48 : "LDC",
    49 : "LDCSR",
    51 : "LDDC", 
    52 : "STC",
    53 : "STCSR",
    54 : "STDCQ",
    55 : "STDC",
}

m_op3_mnemonic = {
    0 : "ld [{address}], {regrd}",
    1 : "ldub [{address}], {regrd}",
    2 : "lduh [{address}], {regrd}",
    3 : "ldd [{address}], {regrd}",
    4 : "st {regrd}, [{address}]",
    5 : "stb {regrd}, [{address}]",
    6 : "sth {regrd}, [{address}]",
    7 : "std {regrd}, [{address}]",
    9 : "ldsb [{address}], {regrd}",
    10 : "ldsh [{address}], {regrd}",
    13 : "ldstub [{address}], {regrd}",
    15 : "swap [{address}], {regrd}", 
    16 : "lda [{address}] {asi}, {regrd}",
    17 : "lduba [{address}] {asi}, {regrd}",
    18 : "lduha [{address}] {asi}, {regrd}",
    19 : "ldda [{address}] {asi}, {regrd}",
    20 : "sta {regrd}, [{address}] {asi}",
    21 : "stba {regrd}, [{address}] {asi}",
    22 : "stha {regrd}, [{address}] {asi}",
    23 : "stda {regrd}, [{address}] {asi}",
    25 : "ldsba [{address}] {asi}, {regrd}",
    26 : "ldsha [{address}] {asi}, {regrd}",
    29 : "ldstuba [{address}] {asi}, {regrd}",
    31 : "swapa [{address}] {asi}, {regrd}",
    32 : "ld [{address}], {fregrd}",
    33 : "ld [{address}], %fsr",
    35 : "ldd [{address}], {fregrd}",
    36 : "stf {fregrd}, [{address}]",
    37 : "stfsr %fsr, [{address}]",
    38 : "stdfq %fq, [{address}]",
    39 : "stdf {fregrd}, [{address}]",
    48 : "ldc [{address}], {cregrd} ",
    49 : "ldd [{address}], %csr",
    51 : "ld [{address}], {cregrd}", 
    52 : "stc {cregd}, [{address}]",
    53 : "stcsr %csr, [{address}]",
    54 : "stdcq %cq, [{address}]",
    55 : "stdc {cregd}, [{address}]", 
    }

# OP = 2 Arithmetic, register/register instructions. Format 3c

# NOTE: RDY/RDASR, WRY/WRASR, FPOP1, FPOP2, and STBAR inconsistencies not handled yet.

A_OP3_ADD = 0
A_OP3_ADDCC = 16
A_OP3_ADDX = 8
A_OP3_ADDXCC = 24
A_OP3_AND = 1
A_OP3_ANDCC = 17
A_OP3_ANDN = 5
A_OP3_ANDNCC = 21
A_OP3_JMPL = 56
A_OP3_MULScc = 36
A_OP3_OR = 2
A_OP3_ORCC = 18
A_OP3_ORN = 6
A_OP3_ORNCC = 22
A_OP3_RESTORE = 61
A_OP3_RETT = 57
A_OP3_SAVE = 60
A_OP3_SDIV = 15
A_OP3_SDIVCC = 31
A_OP3_SLL = 37
A_OP3_SMUL = 11
A_OP3_SMULCC = 27
A_OP3_SRA = 39
A_OP3_SRL = 38
A_OP3_SUB = 4
A_OP3_SUBCC = 20
A_OP3_SUBX = 12
A_OP3_SUBXCC = 28
A_OP3_TADDcc = 32
A_OP3_TADDccTV = 34
A_OP3_TSUBcc = 33
A_OP3_TSUBccTV = 35
A_OP3_UDIV = 14
A_OP3_UDIVCC = 30
A_OP3_UMUL = 10
A_OP3_UMULCC = 26
A_OP3_XNOR = 7
A_OP3_XNORCC = 23
A_OP3_XOR = 3
A_OP3_XORCC = 19
A_OP3_RDY = 40
A_OP3_RDPSR = 41
A_OP3_RDWIM = 42
A_OP3_RDTBR = 43
A_OP3_WRY = 48
A_OP3_WRPSR = 49
A_OP3_WRWIM = 50
A_OP3_WRTBR = 51
A_OP3_FLUSH = 59
A_OP3_FPOP1 = 52
A_OP3_FPOP2 = 53

a_op3_table = {
    0 : "ADD",
    1 : "AND",
    2 : "OR",
    3 : "XOR",
    4 : "SUB",
    5 : "ANDN",
    6 : "ORN",
    7 : "XNOR",
    8 : "ADDX",
    10 : "UMUL",
    11 : "SMUL",
    12 : "SUBX",
    14 : "UDIV",
    15 : "SDIV",
    16 : "ADDCC",
    17 : "ANDCC",
    18 : "ORCC",
    19 : "XORCC",
    20 : "SUBCC",
    21 : "ANDNCC",
    22 : "ORNCC",
    23 : "XNORCC",
    24 : "ADDXCC",
    26 : "UMULCC",
    27 : "SMULCC",
    28 : "SUBXCC",
    30 : "UDIVCC",
    31 : "SDIVCC",
    32 : "TADDcc",
    33 : "TSUBcc",
    34 : "TADDccTV",
    35 : "TSUBccTV",
    36 : "MULScc", 
    37 : "SLL",
    38 : "SRL",
    39 : "SRA",
    40 : "RDY",
    41 : "RDPSR",
    42 : "RDWIM",
    43 : "RDTBR",
    48 : "WRY",
    49 : "WRPSR",
    50 : "WRWIM",
    51 : "WRTBR",
    52 : "FPOP1",
    53 : "FPOP2",
    56 : "JMPL",
    57 : "RETT",
    59 : "FLUSH",
    60 : "SAVE",
    61 : "RESTORE",
    }

a_op3_mnemonic = {
    0 : "add {regrs1}, {reg_or_imm}, {regrd}",
    1 : "and {regrs1}, {reg_or_imm}, {regrd}",
    2 : "or {regrs1}, {reg_or_imm}, {regrd}",
    3 : "xor {regrs1}, {reg_or_imm}, {regrd}",
    4 : "sub {regrs1}, {reg_or_imm}, {regrd}",
    5 : "andn {regrs1}, {reg_or_imm}, {regrd}",
    6 : "orn {regrs1}, {reg_or_imm}, {regrd}",
    7 : "xnor {regrs1}, {reg_or_imm}, {regrd}",
    8 : "addx {regrs1}, {reg_or_imm}, {regrd}",
    10 : "umul {regrs1}, {reg_or_imm}, {regrd}",
    11 : "smul {regrs1}, {reg_or_imm}, {regrd}",
    12 : "subx {regrs1}, {reg_or_imm}, {regrd}",
    14 : "udiv {regrs1}, {reg_or_imm}, {regrd}",
    15 : "sdiv {regrs1}, {reg_or_imm}, {regrd}",
    16 : "addcc {regrs1}, {reg_or_imm}, {regrd}",
    17 : "andcc {regrs1}, {reg_or_imm}, {regrd}",
    18 : "orcc {regrs1}, {reg_or_imm}, {regrd}",
    19 : "xorcc {regrs1}, {reg_or_imm}, {regrd}",
    20 : "subcc {regrs1}, {reg_or_imm}, {regrd}",
    21 : "andncc {regrs1}, {reg_or_imm}, {regrd}",
    22 : "orncc {regrs1}, {reg_or_imm}, {regrd}",
    23 : "xnorcc {regrs1}, {reg_or_imm}, {regrd}",
    24 : "addxcc {regrs1}, {reg_or_imm}, {regrd}",
    26 : "umulcc {regrs1}, {reg_or_imm}, {regrd}",
    27 : "smulcc {regrs1}, {reg_or_imm}, {regrd}",
    28 : "subxcc {regrs1}, {reg_or_imm}, {regrd}",
    30 : "udivcc {regrs1}, {reg_or_imm}, {regrd}",
    31 : "sdivcc {regrs1}, {reg_or_imm}, {regrd}",
    32 : "taddcc {regrs1}, {reg_or_imm}, {regrd}",
    33 : "tsubcc {regrs1}, {reg_or_imm}, {regrd}",
    34 : "taddcctv {regrs1}, {reg_or_imm}, {regrd}",
    35 : "tsubcctv {regrs1}, {reg_or_imm}, {regrd}",
    36 : "mulscc {regrs1}, {reg_or_imm}, {regrd}",
    37 : "sll {regrs1}, {reg_or_imm}, {regrd}",
    38 : "srl {regrs1}, {reg_or_imm}, {regrd}",
    39 : "sra {regrs1}, {reg_or_imm}, {regrd}",
    40 : "rd {aregrs1}, {regrd}",
    41 : "rd %psr, {regrd}",
    42 : "rd %wim, {regrd}",
    43 : "rd %tbr, {regrd}",
    48 : "wr {regrs1}, {reg_or_imm}, {asregrd}",
    49 : "wrpsr {regrs1}, {reg_or_imm}, %psr",
    50 : "wrwim {regrs1}, {reg_or_imm}, %wim",
    51 : "wrtbr {regrs1}, {reg_or_imm}, %tbr",
    52 : "fpop1",
    53 : "fpop2",
    56 : "jmpl {address}, {regrd}",
    59 : "flush {address}",
    60 : "save {regrs1}, {reg_or_imm}, {regrd}",
    61 : "restore {regrs1}, {reg_or_imm}, {regrd}",
}


# Branch instructions, OP = 0, Format 2a, 2b

B_OP2_INT = 2
B_OP2_FLOAT = 6
B_OP2_CPROC = 7


COND_BA         =  8			# Branch Always 1
COND_BCC        = 13			# Branch on Carry Clear (Greater than or Equal, Unsigned) not C
COND_BCS        =  5			# Branch on Carry Set (Less than, Unsigned) C
COND_BE         =  1			# Branch on Equal Z
COND_BG         = 10			# Branch on Greater not (Z or (N xor V))
COND_BGE        = 11			# Branch on Greater or Equal not (N xor V)
COND_BGU        = 12			# Branch on Greater Unsigned not (C or Z)
COND_BL         =  3			# Branch on Less N xor V
COND_BLE        =  2			# Branch on Less or Equal Z or (N xor V)
COND_BLEU       =  4			# Branch on Less or Equal Unsigned (C or Z)
COND_BN         =  0			# Branch Never 0
COND_BNE        =  9			# Branch on Not Equal not Z
COND_BNEG       =  6			# Branch on Negative N
COND_BPOS       = 14			# Branch on Positive not N
COND_BVC        = 15			# Branch on Overflow Clear not V
COND_BVS        =  7			# Branch on Overflow Set V

branch_cond_int_mnemonic = {
    0: 'bn', 1: 'be', 2: 'ble', 3: 'bl', 4: 'bleu', 5: 'bcs', 6: 'bneg', 7: 'bvs',
    8: 'ba', 9: 'bne', 10: 'bg', 11: 'bge', 12: 'bgu', 13: 'bcc', 14: 'bpos', 15: 'bvc',
    }


COND_FBA        =  8            # Branch Always 1
COND_FBN        =  0            # Branch Never 0
COND_FBU        =  7            # Branch on Unordered U
COND_FBG        =  6            # Branch on Greater G
COND_FBUG       =  5            # Branch on Unordered or Greater G or U
COND_FBL        =  4            # Branch on Less L
COND_FBUL       =  3            # Branch on Unordered or Less L or U
COND_FBLG       =  2            # Branch on Less or Greater L or G
COND_FBNE       =  1            # Branch on Not Equal L or G or U
COND_FBE        =  9            # Branch on Equal E
COND_FBUE       = 10            # Branch on Unordered or Equal E or U
COND_FBGE       = 11            # Branch on Greater or Equal E or G
COND_FBUGE      = 12            # Branch on Unordered or Greater or Equal E or G or U
COND_FBLE       = 13            # Branch on Less or Equal E or L
COND_FBULE      = 14            # Branch on Unordered or Less or Equal E or L or U
COND_FBO        = 15            # Branch on Ordered E or L or G


branch_cond_float_mnemonic = {
        0: 'fbn', 1: 'fbne', 2: 'fblg', 3: 'fbul', 4: 'fbl', 5: 'fbug', 6: 'fbg', 7: 'fbu',
        8: 'fba', 9: 'fbe', 10: 'fbue', 11: 'fbge', 12: 'fbuge', 13: 'fble', 14: 'fbule', 15: 'fbo' 
        }


COND_CBA        =  8            # Always
COND_CBN        =  0            # Never
COND_CB3        =  7            # 3
COND_CB2        =  6            # 2
COND_CB23       =  5            # 2 or 3
COND_CB1        =  4            # 1
COND_CB13       =  3            # 1 or 3
COND_CB12       =  2            # 1 or 2
COND_CB123      =  1            # 1 or 2 or 3
COND_CB0        =  9            # 0
COND_CB03       = 10            # 0 or 3
COND_CB02       = 11            # 0 or 2
COND_CB023      = 12            # 0 or 2 or 3
COND_CB01       = 13            # 0 or 1
COND_CB013      = 14            # 0 or 1 or 3
COND_CB012      = 15            # 0 or 1 or 2

branch_cond_cproc_mnemonic = {
        0: 'cbn', 1: 'cb123', 2: 'cb12', 3: 'cb13', 4: 'cb1', 5: 'cb23', 6: 'cb2', 7: 'cb3',
        8: 'cba', 9: 'cb0', 10: 'cb03', 11: 'cb02', 12: 'cb023', 13: 'cb01', 14: 'cb013', 15: 'cb012',
        }

COND_TA         =  8            # Trap Always 1
COND_TCC        = 13            # Trap on Carry Clear (Greater than or Equal, Unsigned) not C
COND_TCS        =  5            # Trap on Carry Set (Less Than, Unsigned) C
COND_TE         =  1            # Trap on Equal Z
COND_TG         = 10            # Trap on Greater not (Z or (N xor V))
COND_TGE        = 11            # Trap on Greater or Equal not (N xor V)
COND_TGU        = 12            # Trap on Greater Unsigned not (C or Z)
COND_TL         =  3            # Trap on Less N xor V
COND_TLE        =  2            # Trap on Less or Equal Z or (N xor V)
COND_TLEU       =  4            # Trap on Less or Equal Unsigned (C or Z)
COND_TN         =  0            # Trap Never 0
COND_TNE        =  9            # Trap on Not Equal not Z
COND_TNEG       =  6            # Trap on Negative N
COND_TPOS       = 14            # Trap on Positive not N
COND_TVC        = 15            # Trap on Overflow Clear not V
COND_TVS        =  7            # Trap on Overflow Set V

branch_cond_traps_mnemonic = {
        0: 'tn', 1: 'te', 2: 'tle', 3: 'tl', 4: 'tleu', 5: 'tcs', 6: 'tneg', 7: 'tvs',
        8: 'ta', 9: 'tne', 10: 'tg', 11: 'tge', 12: 'tgu', 13: 'tcc', 14: 'tpos', 15: 'tvc',
        }

register_label = [
        '%g0', '%g1', '%g2', '%g3', '%g4', '%g5', '%g6', '%g7', 
        '%o0', '%o1', '%o2', '%o3', '%o4', '%o5', '%sp', '%o7', # note, %sp is equivalent to %o6, equivalent to %r14
        '%l0', '%l1', '%l2', '%l3', '%l4', '%l5', '%l6', '%l7', 
        '%i0', '%i1', '%i2', '%i3', '%i4', '%i5', '%fp', '%i7'] # note, %fp is equivalent to %i6, equivalent to %r30

freg_label = ['%f0', '%f1', '%f2', '%f3', '%f4', '%f5', '%f6', '%f7', '%f8', 
            '%f9', '%f10', '%f11', '%f12', '%f13', '%f14', '%f15', '%f16', 
            '%f17', '%f18', '%f19', '%f20', '%f21', '%f22', '%f23', '%f24', 
            '%f25', '%f26', '%f27', '%f28', '%f29', '%f30', '%f31']

creg_label = ['%c0', '%c1', '%c2', '%c3', '%c4', '%c5', '%c6', '%c7', 
              '%c8', '%c9', '%c10', '%c11', '%c12', '%c13', '%c14', '%c15', 
              '%c16', '%c17', '%c18', '%c19', '%c20', '%c21', '%c22', '%c23', 
              '%c24', '%c25', '%c26', '%c27', '%c28', '%c29', '%c30', '%c31']
