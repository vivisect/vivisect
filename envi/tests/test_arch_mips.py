import binascii
import unittest

import envi
from envi.archs.mips.disasm import *

# to run: `$ python -m unittest envi.tests.test_arch_mips`

# Missing:
# lhi, llo
# break - https://opencores.org/projects/plasma/opcodes
# bgez, bgezal, bgtz, blez, bltz, bltzal
# mfc0, mtc0

# beq will need to be updated to have labels instead of addresses

class MipsInstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("mips")

    def test_core_instr_set(self):
        archmod = envi.getArchModule("mips")

        instrs = [
            ('02538820', 0, 'add $s1, $s2, $s3'),
            ('014B6020', 0, 'add $t4, $t2, $t3'),
            ('01495020', 0, 'add $t2, $t2, $t1'),
            ('011C4020', 0, 'add $t0, $t0, $gp'),
            ('238a001c', 0, 'addi $t2, $gp, 28'),
            ('21290001', 0, 'addi $t1, $t1, 1'),
            ('21290003', 0, 'addi $t1, $t1, 3'),
            ('254900DD', 0, 'addiu $t1, $t2, 221'),

            ('014B4821', 0, 'addu $t1, $t2, $t3'),

            ('010A4024', 0, 'and $t0, $t0, $t2'),
            ('3129FF00', 0, 'andi $t1, $t1, 0xff00'),
            ('3109FF00', 0, 'andi $t1, $t0, 0xff00'),
            ('12751234', 0, 'beq $s3, $s5, 0x1234'),
            ('1120BEEF', 0, 'beq $t1, $zero, 0xbeef'),
            ('16755678', 0, 'bne $s3, $s5, 0x5678'),
            ('1520BEEF', 0, 'bne $t1, $zero, 0xbeef'),
            ('0110001A', 0, 'div $t0, $s0'),
            ('0210001A', 0, 'div $s0, $s0'),
            ('0110001B', 0, 'divu $t0, $s0'),
            ('0ac51462', 0, 'j 0xb145188'),
            ('08000004', 0, 'j 0x10'),
            ('0c10000c', 0, 'jal 0x400030'),
            ('02000009', 0, 'jalr $s0'),
            ('02000008', 0, 'jr $s0'),
            ('83880000', 0, 'lb $t0, 0($gp)'),
            ('83880424', 0, 'lb $t0, 1060($gp)'),
            ('83890004', 0, 'lb $t1, 4($gp)'),
            ('93880000', 0, 'lbu $t0, 0($gp)'),
            ('93880424', 0, 'lbu $t0, 1060($gp)'),
            ('93890004', 0, 'lbu $t1, 4($gp)'),
            ('86680001', 0, 'lh $t0, 1($s3)'),
            ('96680001', 0, 'lhu $t0, 1($s3)'),
            ('3C09DEAD', 0, 'lui $t1, 0xdead'),
            ('8f880000', 0, 'lw $t0, 0($gp)'),
            ('8f890004', 0, 'lw $t1, 4($gp)'),
            ('8f880004', 0, 'lw $t0, 4($gp)'),
            ('8f880424', 0, 'lw $t0, 1060($gp)'),
            ('8d290000', 0, 'lw $t1, 0($t1)'),
            ('8f880000', 0, 'lw $t0, 0($gp)'),
            ('00004010', 0, 'mfhi $t0'),
            ('00004812', 0, 'mflo $t1'),
            ('01000011', 0, 'mthi $t0'),
            ('01000013', 0, 'mtlo $t0'),
            ('01290018', 0, 'mult $t1, $t1'),
            ('01080018', 0, 'mult $t0, $t0'),
            ('012A0018', 0, 'mult $t1, $t2'),
            ('01290019', 0, 'multu $t1, $t1'),
            ('014B4827', 0, 'nor $t1, $t2, $t3'),
            ('01094025', 0, 'or $t0, $t0, $t1'),

            ('340A0003', 0, 'ori $t2, $zero, 3'),
            ('354A00FF', 0, 'ori $t2, $t2, 255'),
            # ('3C0AFFFF', 0, 'lui $t2, 0xffff'),
            ('A1490002', 0, 'sb $t1, 2($t2)'),
            ('A2090000', 0, 'sb $t1, 0($s0)'),
            ('A5490002', 0, 'sh $t1, 2($t2)'),
            ('A6090000', 0, 'sh $t1, 0($s0)'),
            ('016A4804', 0, 'sllv $t1, $t2, $t3'),
            ('00095083', 0, 'sra $t2, $t1, 2'),
            ('0211402B', 0, 'sltu $t0, $s0, $s1'),
            ('02538822', 0, 'sub $s1, $s2, $s3'),
            ('014B6822', 0, 'sub $t5, $t2, $t3'),
            ('af8a0000', 0, 'sw $t2, 0($gp)'),
            ('ad490000', 0, 'sw $t1, 0($t2)'),
            ('ad00001c', 0, 'sw $zero, 28($t0)'),
            ('af890000', 0, 'sw $t1, 0($gp)'),
            ('0000000C', 0, 'syscall'),
            ('00084080', 0, 'sll $t0, $t0, 2'),
            ('00094880', 0, 'sll $t1, $t1, 2'),
            ('0109482A', 0, 'slt $t1, $t0, $t1'),
            ('292800EE', 0, 'slti $t0, $t1, 238'),
            ('2E08ABCD', 0, 'sltiu $t0, $s0, 0xabcd'),
            ('016A4807', 0, 'srav $t1, $t2, $t3'),
            ('00084042', 0, 'srl $t0, $t0, 1'),
            ('016A4806', 0, 'srlv $t1, $t2, $t3'),
            ('014B4823', 0, 'subu $t1, $t2, $t3'),
            ('014B4826', 0, 'xor $t1, $t2, $t3'),
            ('394900FF', 0, 'xori $t1, $t2, 255'),
        ]

        for bytez, va, reprOp in instrs:
            op = archmod.archParseOpcode(binascii.unhexlify(bytez), 0, va)
            result = repr(op)
            self.assertEqual(result, reprOp)

    def test_parse_R_format(self):
        disas = MipsDisasm()

        # 'add' example
        # 000000 10010 10011 10001 00000 100000
        input = 39028768
        expected = 0,18,19,17,0,32
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'sub' example
        # 000000 10010 10011 10001 00000 100010
        input = 39028770
        expected = 0,18,19,17,0,34
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'and' example
        # 000000 10010 10011 10001 00000 100100
        input = 39028772
        expected = 0,18,19,17,0,36
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'or' example
        # 000000 10010 10011 10001 00000 100101
        input = 39028773
        expected = 0,18,19,17,0,37
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'sll' example
        # 000000 00000 10010 10001 01010 000000
        input = 1215104
        expected = 0,0,18,17,10,0
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'srl' example
        # 000000 00000 10010 10001 01010 000010
        input = 1215106
        expected = 0,0,18,17,10,2
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

        # 'slt' example
        # 000000 10010 10011 10001 00000 101010
        input = 39028778
        expected = 0,18,19,17,0,42
        result = disas.mipsRformat(input)
        self.assertEqual(result, expected)

    def test_parse_I_format(self):
        disas = MipsDisasm()

        # 'lw' example
        # 100011 10010 10001 0000000001100100
        input = 2387673188
        expected = 35,18,17,100
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

        # 'sw' example
        # 101011 10010 10001 0000000001100100
        input = 2924544100
        expected = 43,18,17,100
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

        # 'andi' example
        # 010110 10010 10001 0000000001100100
        input = 1515257956
        expected = 22,18,17,100
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

        # 'ori' example
        # 001101 10010 10001 0000000001100100
        input = 911278180
        expected = 13,18,17,100
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

        # 'beq' example
        # 000100 10001 10010 0000000000011001
        input = 305266713
        expected = 4,17,18,25
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

        # 'bne' assertEqual
        # 000101 10001 10010 0000000000011001
        input = 372375577
        expected = 5,17,18,25
        result = disas.mipsIformat(input)
        self.assertEqual(result, expected)

    def test_parse_J_format(self):
        disas = MipsDisasm()

        # 'j 10000' example
        # 000010 00000000000000100111000100
        input = 134220228
        expected = 2, 2500
        result = disas.mipsJformat(input)
        self.assertEqual(result, expected)
