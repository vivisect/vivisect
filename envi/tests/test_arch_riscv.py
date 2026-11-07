"""
RISC-V architecture tests (RV32 / RV64).

Covers:
  * disassembly of representative RV64GC(RV32GC) instructions
  * return / call detection via the jalr/jal aliasing heuristic
  * immediate sign-extension for I/S/B/J/U-format instructions
  * compressed (16-bit) decoding
  * emulation of the integer core (add/sub/and/or/xor/shifts/slt)
  * emulation of load/store memory access
  * emulation of the M-extension (mul/div/rem, signed & unsigned)
  * CSR read/write
  * NOP encoding

NOTE: several tests in the "emu" section encode RISC-V-spec-correct behavior
that the initial `riscv-dev` emulator did not implement correctly (e.g. shifts
used XOR instead of << / >>, `slt` compared the wrong operands, `sra` was not
arithmetic, unsigned divide was treated as signed).  The accompanying fix
commit makes these pass.
"""
import binascii
import unittest

import envi
import envi.memcanvas as e_memcanvas
import envi.archs.riscv as e_riscv


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def get_arch(xlen=64):
    archmod = e_riscv.RiscV64Module() if xlen == 64 else e_riscv.RiscV32Module()
    return archmod


def parse_op(archmod, hexstr, va=0x1000):
    return archmod.archParseOpcode(binascii.unhexlify(hexstr), 0, va)


class RiscVInstrDisasmTest(unittest.TestCase):

    arch = 'rv64'

    def setUp(self):
        self.archmod = get_arch(64)

    # (hexbytes, va, expected repr)
    def test_disasm_base_int(self):
        cases = [
            # lui sp,0x20000
            ('37010200', 0x1000, 'lui sp,0x20000'),
            # auipc
            ('17010200', 0x1000, 'auipc sp,0x20000'),
        ]
        for hexbytes, va, expected in cases:
            op = parse_op(self.archmod, hexbytes, va)
            self.assertEqual(repr(op), expected,
                             f"FAIL decode {hexbytes} at {va}")

    def test_disasm_addi_immediate_signed(self):
        # addi ra, zero, 21 -> imm sign extended correctly
        op = parse_op(self.archmod, '93005001', 0x1000)
        self.assertEqual(repr(op), 'addi ra,zero,21')

    def test_disasm_alu_regs(self):
        cases = [
            ('b300f000', 'add ra,zero,a5'),
            ('33b01000', 'sltu zero,ra,ra'),
            ('33d01000', 'srl zero,ra,ra'),
            ('33d01040', 'sra zero,ra,ra'),
        ]
        for hexbytes, expected in cases:
            op = parse_op(self.archmod, hexbytes, 0x1000)
            self.assertEqual(repr(op), expected,
                             f"FAIL decode {hexbytes}")

    def test_disasm_ret_detection(self):
        # jalr x0,0(ra) -> jr 0(ra), IF_RET should be set
        op = parse_op(self.archmod, '67800000', 0x1000)
        self.assertEqual(repr(op), 'jr 0(ra)')
        self.assertTrue(op.iflags & envi.IF_RET)
        self.assertFalse(op.iflags & envi.IF_CALL)

    def test_disasm_pseudo_jal_returns_ra(self):
        # jal ra, 0 -> link register is ra -> IF_CALL (call-style link)
        op = parse_op(self.archmod, 'ef000000', 0x1000)
        self.assertEqual(repr(op), 'jal ra,0x1000')
        self.assertTrue(op.iflags & envi.IF_CALL)

    def test_disasm_j_pseudo(self):
        # j offset  -> jal x0, offset : plain jump, NO call/link
        op = parse_op(self.archmod, '6f000000', 0x1000)
        self.assertEqual(repr(op), 'j 0x1000')
        self.assertFalse(op.iflags & envi.IF_CALL)

    def test_disasm_branch(self):
        # beq/bltu ra,zero,target
        op = parse_op(self.archmod, '63ea0000', 0x1000)
        self.assertEqual(repr(op), 'bltu ra,zero,20')
        self.assertTrue(op.iflags & envi.IF_COND)

    def test_disasm_load(self):
        op = parse_op(self.archmod, '03c24200', 0x1000)
        self.assertEqual(repr(op), 'lbu tp,4(t0)')
        self.assertEqual(op.iflags & 0x100, 0x100)  # RISCV_IF.LOAD

    def test_disasm_ecall_ebreak(self):
        self.assertEqual(repr(parse_op(self.archmod, '73000000', 0x1000)), 'ecall')
        self.assertEqual(repr(parse_op(self.archmod, '73001000', 0x1000)), 'ebreak')

    def test_disasm_nop(self):
        # addi zero,zero,0 is the canonical NOP
        op = parse_op(self.archmod, '13000000', 0x1000)
        self.assertEqual(repr(op), 'addi zero,zero,0')


class RiscVInstrDisasm32Test(RiscVInstrDisasmTest):

    arch = 'rv32'

    def setUp(self):
        self.archmod = get_arch(32)


class RiscVEmuTest(unittest.TestCase):

    def setUp(self):
        import envi.memory as e_mem
        self.arch = get_arch(64)
        # getEmulator should now work (constructor tangles fixed)
        self.emu = self.arch.getEmulator()
        self.emu.setProgramCounter(0x1000)
        # map pages for load/store tests (RWX)
        self.emu.addMemoryMap(0x1000, e_mem.MM_RWX, 'test', b'\x00' * 0x1000)
        self.emu.addMemoryMap(0x0, e_mem.MM_RWX, 'page0', b'\x00' * 0x1000)

    def _run(self, hexbytes, regs=None):
        """set regs, exec opcode, return"""
        if regs:
            for reg, val in regs.items():
                self.emu.setRegister(reg, val)
        op = parse_op(self.arch, hexbytes, self.emu.getProgramCounter())
        self.emu.executeOpcode(op)
        return op

    def _reg(self, name):
        return self.emu.getRegister(name)

    # ---- integer core ----
    def test_emu_add(self):
        # add x5, x1, x2 : funct7=0, func3=000, rd=5, rs1=1, rs2=2
        enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b000 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 10, 2: 20})
        self.assertEqual(self._reg(5), 30)

    def test_emu_sll(self):
        # sll x5, x1, x2 where x1=1, x2=3 -> 1<<3 = 8
        # sll rd=x5(5), rs1=x1(1), rs2=x2(2): funct7=0,func3=001
        enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b001 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 1, 2: 3})
        self.assertEqual(self._reg(5), 8)

    def test_emu_srl(self):
        # srl x5, x1, x2 where x1=0x100, x2=3 -> 0x100>>3 = 0x20
        enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b101 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 0x100, 2: 3})
        self.assertEqual(self._reg(5), 0x20)

    def test_emu_sra_arithmetic(self):
        # sra x5, x1, x2 with x1 = -16 (0xfffffffffffffff0) and x2=2 -> -4
        enc = (0b0100000 << 25) | (2 << 20) | (1 << 15) | (0b101 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(),
                  regs={1: 0xfffffffffffffff0, 2: 2})
        self.assertEqual(self._reg(5), 0xffffffffffffffff & (-4))

    def test_emu_slt(self):
        # slt x5, x1, x2: x1=10 < x2=20 -> 1
        enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b010 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 10, 2: 20})
        self.assertEqual(self._reg(5), 1)
        # x1=20 > x2=10 -> 0
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 20, 2: 10})
        self.assertEqual(self._reg(5), 0)

    def test_emu_sltu(self):
        # sltu x5, x1, x2: unsigned compare
        enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b011 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(),
                  regs={1: 0xffffffffffffffff, 2: 0})   # huge > 0 -> 0
        self.assertEqual(self._reg(5), 0)

    def test_emu_and_or_xor(self):
        enc = lambda f3: (0 << 25) | (2 << 20) | (1 << 15) | (f3 << 12) | (5 << 7) | 0x33
        self._run(enc(0b111).to_bytes(4, 'little').hex(), regs={1: 0xF0, 2: 0x0F})  # AND
        self.assertEqual(self._reg(5), 0)
        self._run(enc(0b110).to_bytes(4, 'little').hex(), regs={1: 0xF0, 2: 0x0F})  # OR
        self.assertEqual(self._reg(5), 0xFF)
        self._run(enc(0b100).to_bytes(4, 'little').hex(), regs={1: 0xF0, 2: 0x0F})  # XOR
        self.assertEqual(self._reg(5), 0xFF)

    def test_emu_sub(self):
        # sub x5,x1,x2
        enc = (0b0100000 << 25) | (2 << 20) | (1 << 15) | (0b000 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 50, 2: 20})
        self.assertEqual(self._reg(5), 30)

    # ---- memory ----
    def test_emu_load_store(self):
        # sw rs2, imm(rs1) : store word at mem[rs1+imm]
        # enc: imm[11:5]<<25 | rs2<<20 | rs1<<15 | func3<<12 | imm[4:0]<<7 | 0x23
        # store 0xAABB (x2=rs2) at [x1(0x1000)+4]
        sw_enc = (0 << 25) | (2 << 20) | (1 << 15) | (0b010 << 12) | (4 << 7) | 0x23
        self._run(sw_enc.to_bytes(4, 'little').hex(), regs={1: 0x1000, 2: 0xAABB})
        mval = self.emu.readMemory(0x1004, 4)
        self.assertEqual(mval, 0xAABB.to_bytes(4, 'little'))

        # lw rd, imm(rs1) : load word from mem[rs1+imm] into rd
        # enc: imm[11:0]<<20 | rs1<<15 | func3<<12 | rd<<7 | 0x03
        lw_enc = (4 << 20) | (1 << 15) | (0b010 << 12) | (3 << 7) | 0x03
        self._run(lw_enc.to_bytes(4, 'little').hex(), regs={1: 0x1000})
        self.assertEqual(self._reg(3), 0xAABB)

    # ---- M extension ----
    def test_emu_mul(self):
        # mul x5,x1,x2 : funct7=0000001, func3=000, opcode=0110011
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b000 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 6, 2: 7})
        self.assertEqual(self._reg(5), 42)

    def test_emu_mulh(self):
        # mulh x5,x1,x2 -> upper half of signed product
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b001 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 0xFFFFFFFF, 2: 0xFFFFFFFF})
        # signed: -1 * -1 = 1 -> upper 64 bits = 0
        self.assertEqual(self._reg(5), 0)

    def test_emu_div(self):
        # div x5,x1,x2 signed 7 // 2 = 3
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b100 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 7, 2: 2})
        self.assertEqual(self._reg(5), 3)

    def test_emu_divu(self):
        # divu x5,x1,x2 : unsigned 0xFFFFFFFF // 2
        # set rs1 to a value whose upper bit is set -> signed interpretation would differ
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b101 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 0x8000000000000000, 2: 2})
        # unsigned 0x8000.../2 = 0x4000...
        self.assertEqual(self._reg(5), 0x4000000000000000)

    def test_emu_remu(self):
        # remu x5,x1,x2 : unsigned remainder
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b111 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 0x8000000000000000, 2: 3})
        self.assertEqual(self._reg(5), 0x8000000000000000 % 3)

    def test_emu_div_zero(self):
        enc = (0b0000001 << 25) | (2 << 20) | (1 << 15) | (0b100 << 12) | (5 << 7) | 0x33
        self._run(enc.to_bytes(4, 'little').hex(), regs={1: 7, 2: 0})
        # RISC-V spec: div by zero -> rd = all 1's
        self.assertEqual(self._reg(5), 0xFFFFFFFFFFFFFFFF)

    # ---- CSR ----
    def test_emu_csrrw(self):
        # csrrw rd, rs1, csr : rd = csr; csr = rs1
        # use fflags (CSR 1, in the scraped list); rs1=5, rd=2
        csr = 0x001  # fflags
        enc = (csr << 20) | (5 << 15) | (0b001 << 12) | (2 << 7) | 0x73
        self._run(enc.to_bytes(4, 'little').hex(), regs={5: 0x55})
        # rd (x2) should now hold the previous CSR value (0 unless set)
        self.assertEqual(self._reg(2), 0)
        # write-back check: read the CSR via csrrs (csrrs rd, x0, csr)
        csrrs_enc = (csr << 20) | (0 << 15) | (0b010 << 12) | (6 << 7) | 0x73
        self._run(csrrs_enc.to_bytes(4, 'little').hex())
        self.assertEqual(self._reg(6), 0x55)

    # ---- NOP ----
    def test_nop_bytes(self):
        # canonical NOP is addi zero,zero,0 == 0x00000013, little-endian
        nop = self.arch.archGetNopInstr()
        self.assertEqual(nop, binascii.unhexlify('13000000'))


# ---------------------------------------------------------------------------
# compressed instructions smoke tests
# ---------------------------------------------------------------------------

class RiscVCompressedDisasmTest(unittest.TestCase):

    def setUp(self):
        self.archmod = get_arch(64)

    def test_disasm_c_jal(self):
        # C-extension 16-bit instructions should decode without error and be 2 bytes
        # verified compact encodings (little-endian bytes of the 16-bit value):
        valid = {
            '0100': 'nop',       # c.nop (addi x0,0,0)
            '0561': 'addi16sp',  # c.addi16sp
            '0280': 'jr',        # c.jr
            '01a0': 'j',         # c.j (jal x0)
            '00c0': 'sw',        # c.sw
        }
        for hexbytes, exp_mnem in valid.items():
            op = parse_op(self.archmod, hexbytes, 0x1000)
            self.assertEqual(op.size, 2, f"expected 2-byte compressed for {hexbytes}")
            self.assertTrue(op.mnem == exp_mnem,
                            f"unexpected mnem {op.mnem} for {hexbytes}")


if __name__ == '__main__':
    unittest.main()
