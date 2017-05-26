from parsers import *
from envi import *

'''



8DII    add.b immediate             2 states
08SD    add.b regdir                2 states

791DIIII    add.w imm               4 states
09SD    add.w regdir                2 states

7a1EIIII    add.l imm               6 states
0aSD        add.l regdir            2 states

0b0D    adds #1, ERd                2 states
0b8D    adds #2, ERd                2 states
0b9D    adds #4, ERd                2 states

9DII    addx #xx:8, Rd              2 states
0eSD    addx Rs, Rd                 2 states

eDII    and.b #xx:8, Rd             2 states
16SD    and.b Rs, Rd                2 states

796DIIII    and.w #xx:16, Rd        4 states
66SD        and.w Rs, Rd            2 states

7a6DIIIIIIII    and.l #xx:32, ERd   6 states
01f066SD        and.l Rs, ERd       4 states

06II    andc #xx:8, CCR             2 states

76ID    band #xx:3, Rd              2 states
7cD076I0    band #xx:3, @ERd        6 states
7eAb76I0    band #xx:3, @aa:8       6 states

4CDS    bcc d:8             4 states
58C0DISP    bcc d:16        6 states
'''
# table: ( subtable, mnem, decoder, tsize, iflags)
main_table = [(None, 'DECODE_ERROR',0,0,0) for x in range(256)]
main_table[0x0] = (False, 'nop', None, 0,0)
main_table[0x1] = (False, None, p_01, 0,0)
main_table[0xa] = (False, None, p_0a_1a, 0,0)
main_table[0xb] = (False, None, p_0b_1b, 0,0)
main_table[0xf] = (False, None, p_0f_1f, 0,0)
main_table[0x10] = (False, None, p_shift_10_11_12_13_17, 0,0)
main_table[0x11] = (False, None, p_shift_10_11_12_13_17, 0,0)
main_table[0x12] = (False, None, p_shift_10_11_12_13_17, 0,0)
main_table[0x13] = (False, None, p_shift_10_11_12_13_17, 0,0)
main_table[0x17] = (False, None, p_shift_10_11_12_13_17, 0,0)
main_table[0x1a] = (False, None, p_0a_1a, 0,0)
main_table[0x1b] = (False, None, p_0b_1b, 0,0)
main_table[0x1f] = (False, None, p_0f_1f, 0,0)

main_table[0x02] = (False, 'stc', p_CCR_Rd, 1, IF_B)
main_table[0x03] = (False, 'ldc', p_Rs_CCR, 1, IF_B)
main_table[0x04] = (False, 'orc', p_i8_CCR, 1, 0)
main_table[0x05] = (False, 'xorc', p_i8_CCR, 1, 0)
main_table[0x06] = (False, 'andc', p_i8_CCR, 1, 0)
main_table[0x07] = (False, 'ldc', p_i8_CCR, 1, IF_B)
main_table[0x08] = (False, 'add', p_Rs_Rd, 1, IF_B)
main_table[0x09] = (False, 'add', p_Rs_Rd, 2, IF_W)
main_table[0x0c] = (False, 'mov', p_Rs_Rd, 1, IF_B)
main_table[0x0d] = (False, 'mov', p_Rs_Rd, 2, IF_W)
main_table[0x0e] = (False, 'addx', p_Rs_Rd, 1, 0)

main_table[0x14] = (False, 'or', p_Rs_Rd, 1, IF_B)
main_table[0x15] = (False, 'xor', p_Rs_Rd, 1, IF_B)
main_table[0x16] = (False, 'and', p_Rs_Rd, 1, IF_B)
main_table[0x18] = (False, 'sub', p_Rs_Rd, 1, IF_B)
main_table[0x19] = (False, 'sub', p_Rs_Rd, 2, IF_W)
main_table[0x1c] = (False, 'cmp', p_Rs_Rd, 1, IF_B)
main_table[0x1d] = (False, 'cmp', p_Rs_Rd, 2, IF_W)
main_table[0x1e] = (False, 'subx', p_Rs_Rd, 1, 0)

# mov.b set
for opbyte in range(0x20, 0x30):
    main_table[opbyte] = (False, 'mov', p_aAA8_Rd, 1, IF_B)

for opbyte in range(0x30, 0x40):
    main_table[opbyte] = (False, 'mov', p_Rs_aAA8, 1, IF_B)

# generate Bcc opcodes
for opbyte in range(16):
    mnem, iflags = bcc[opbyte]
    main_table[0x40 + opbyte] = (False, mnem, p_disp8, 1, iflags)

main_table[0x50] = (False, 'mulxu', p_Rs_Rd_mul, 1, IF_B)
main_table[0x51] = (False, 'divxu', p_Rs_Rd_mul, 1, IF_B)
main_table[0x52] = (False, 'mulxu', p_Rs_ERd, 2, IF_W)
main_table[0x53] = (False, 'divxu', p_Rs_ERd, 2, IF_W)

main_table[0x54] = (False, 'rts', None, 0, IF_RET | IF_NOFALL)   # 5470
main_table[0x55] = (False, 'bsr', p_disp8, 0, IF_CALL)
main_table[0x56] = (False, 'rte', None, 0, IF_RET | IF_NOFALL)   # 5670
main_table[0x57] = (False, 'trapa', p_i2, 0, IF_NOFALL)
main_table[0x58] = (False, 'error', p_disp16, 2, 0)
main_table[0x59] = (False, 'jmp', p_aERn,  3, IF_BRANCH | IF_NOFALL)
main_table[0x5a] = (False, 'jmp', p_aAA24, 0, IF_BRANCH | IF_NOFALL)
main_table[0x5b] = (False, 'jmp', p_aaAA8, 0, IF_BRANCH | IF_NOFALL)
main_table[0x5c] = (False, 'bsr', p_disp16, 0, IF_CALL)
main_table[0x5d] = (False, 'jsr', p_aERn, 3, IF_CALL)
main_table[0x5e] = (False, 'jsr', p_aAA24, 0, IF_CALL)
main_table[0x5f] = (False, 'jsr', p_aaAA8, 0, IF_CALL)

# all bit instructions are B. may set 0->1
main_table[0x60] = (False, 'bset', p_Rn_Rd, 1, 0)   
main_table[0x70] = (False, 'bset', p_i3_Rd, 1, 0)
main_table[0x61] = (False, 'bnot', p_Rn_Rd, 1, 0)
main_table[0x71] = (False, 'bnot', p_i3_Rd, 1, 0)
main_table[0x62] = (False, 'bclr', p_Rn_Rd, 1, 0)
main_table[0x72] = (False, 'bclr', p_i3_Rd, 1, 0)
main_table[0x63] = (False, 'btst', p_Rn_Rd, 1, 0)
main_table[0x73] = (False, 'btst', p_i3_Rd, 1, 0)

main_table[0x64] = (False, 'or', p_Rs_Rd, 2, IF_W)
main_table[0x65] = (False, 'xor', p_Rs_Rd, 2, IF_W)
main_table[0x66] = (False, 'and', p_Rs_Rd, 2, IF_W)

main_table[0x67] = (False, 'bitdoubles', p_Bit_Doubles, 1, 0)

main_table[0x68] = (False, 'mov', p_68_69_6e_6f, 1, IF_B)
main_table[0x69] = (False, 'mov', p_68_69_6e_6f, 2, IF_W)
main_table[0x6a] = (False, 'mov', p_6A_6B, 1, 0)
main_table[0x6b] = (False, 'mov', p_6A_6B, 2, IF_W)
#main_table[0x6c] = (False, 'mov', p_Mov_6C, 1, IF_B)
#main_table[0x6d] = (False, 'mov', p_Mov_6C, 2, IF_W)
main_table[0x6c] = (False, 'mov', p_6c_6d_0100, 1, IF_B)
main_table[0x6d] = (False, 'mov', p_6c_6d_0100, 2, IF_W)
main_table[0x6e] = (False, 'mov', p_68_69_6e_6f, 1, IF_B)
main_table[0x6f] = (False, 'mov', p_68_69_6e_6f, 2, IF_W)

for opbyte in range(0x74, 0x78):
    main_table[opbyte] = (False, 'bitdoubles', p_Bit_Doubles, 1, 0)

main_table[0x78] = (False, 'mov', p_Mov_78, 1, 0)
main_table[0x79] = (False, 'p79', p_79, 2, IF_W)
main_table[0x7a] = (False, 'p7a', p_7a, 4, IF_L)
main_table[0x7b] = (False, 'eepmov', p_eepmov, 0, 0)
main_table[0x7c] = (False, '7Cmnem', p_7c, 1, 0)
main_table[0x7d] = (False, '7Dmnem', p_7d, 1, 0)
main_table[0x7e] = (False, '7Emnem', p_7e, 1, 0)
main_table[0x7f] = (False, '7Fmnem', p_7f, 1, 0)


for opbyte in range(0x80, 0x90):
    main_table[opbyte] = (False, 'add', p_i8_Rd, 1, IF_B)

for opbyte in range(0x90, 0xa0):
    main_table[opbyte] = (False, 'addx', p_i8_Rd, 1, 0)

for opbyte in range(0xa0, 0xb0):
    main_table[opbyte] = (False, 'cmp', p_i8_Rd, 1, IF_B)

for opbyte in range(0xb0, 0xc0):
    main_table[opbyte] = (False, 'subx', p_i8_Rd, 1, 0)

for opbyte in range(0xc0, 0xd0):
    main_table[opbyte] = (False, 'or', p_i8_Rd, 1, IF_B)

for opbyte in range(0xd0, 0xe0):
    main_table[opbyte] = (False, 'xor', p_i8_Rd, 1, IF_B)

for opbyte in range(0xe0, 0xf0):
    main_table[opbyte] = (False, 'and', p_i8_Rd, 1, IF_B)

for opbyte in range(0xf0, 0x100):
    main_table[opbyte] = (False, 'mov', p_i8_Rd, 1, IF_B)

