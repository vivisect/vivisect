"""
Regression tests for the aarch64 integer-subtraction width bug.

The shared helper `intSubBase()` (in envi/archs/aarch64/emu.py) previously
hardcoded a 32-bit ("size=4") width for the unsigned/signed masking of its
operands.  For the AArch64 64-bit data-processing instructions (sub, subs,
cmp, cmps, neg) this silently truncates the result to 32 bits, dropping the
high 32 bits of any 64-bit subtraction.

These tests use operands whose correct 64-bit result EXCEEDS 32 bits, so the
old code fails and the corrected code passes -> they guard against regression.
"""

import unittest

import vivisect
import envi
from envi.archs.aarch64.regs import *


class Aarch64SubRegressionTest(unittest.TestCase):

    def setUp(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "a64")
        vw.setEndian(envi.ENDIAN_LSB)
        vw.addMemoryMap(0, 7, 'firmware', b'\xff' * 16384 * 1024)
        self.emu = vw.getEmulator()
        self.emu.setMeta('forrealz', True)
        self.emu._forrealz = True
        self.emu.logread = self.emu.logwrite = False

    # --- helpers ---------------------------------------------------------

    def _exec(self, bytez):
        """Parse + execute a raw little-endian instruction hex string."""
        op = self.emu.vw.arch.archParseOpcode(bytes.fromhex(bytez), 0, 0)
        self.emu.executeOpcode(op)
        return op

    def _get(self, name):
        return self.emu.getRegisterByName(name)

    # --- regression: 64-bit subtract MUST NOT truncate -------------------

    def test_sub_64bit_no_truncation(self):
        """
        sub x19, x26, x23   (0x530317cb)
        x26 = 0x1122334455667788, x23 = 0x0000000055667788
        Correct 64-bit result: 0x1122334400000000   (exceeds 32 bits)
        Old code truncated to 0x0 -> regression guard.
        """
        self.emu.setRegister(REG_X26, 0x1122334455667788)
        self.emu.setRegister(REG_X23, 0x0000000055667788)
        self._exec('530317cb')   # sub x19, x26, x23
        self.assertEqual(self._get('x19'), 0x1122334400000000)

    def test_sub_64bit_crosses_high_bit(self):
        """
        sub x19, x26, x23
        x26 = 0x100000000 (2^32), x23 = 1
        Correct result: 0xffffffff (2^32 - 1) -- still 64-bit, must NOT be 0.
        """
        self.emu.setRegister(REG_X26, 0x100000000)
        self.emu.setRegister(REG_X23, 1)
        self._exec('530317cb')   # sub x19, x26, x23
        self.assertEqual(self._get('x19'), 0xffffffff)

    def test_sub_64bit_negative_result(self):
        """
        sub x19, x26, x23
        x26 = 1, x23 = 0x100000000  ->  1 - 2^32 = -0xffffffff
        Stored as full 64-bit unsigned: 0xffffffffffffff01 - ... 
        correct = (0 - 0xffffffff) mod 2^64 = 0xffffffffffffff01
        """
        self.emu.setRegister(REG_X26, 1)
        self.emu.setRegister(REG_X23, 0x100000000)
        self._exec('530317cb')   # sub x19, x26, x23
        # 1 - 0x100000000 = -4294967295 ; mod 2^64:
        correct = (1 - 0x100000000) & 0xffffffffffffffff
        self.assertEqual(self._get('x19'), correct)

    def test_neg_64bit(self):
        """
        neg x4, x4   (0xe40304cb, from the aarch64 test corpus)
        x4 = 1  ->  x4 = 0xffffffffffffffff  (0 - 1 at 64 bits)
        Exercises the newly-added i_neg handler (was dead i_rsb / missing).
        """
        self.emu.setRegister(REG_X4, 1)
        self._exec('e40304cb')   # neg x4, x4
        self.assertEqual(self._get('x4'), 0xffffffffffffffff)

    def test_neg_64bit_large(self):
        """
        neg x4, x4
        x4 = 0x64  ->  x4 = 0xffffffffffffff9c  (0 - 0x64 at 64 bits)
        """
        self.emu.setRegister(REG_X4, 0x64)
        self._exec('e40304cb')   # neg x4, x4
        self.assertEqual(self._get('x4'), 0xffffffffffffff9c)


if __name__ == '__main__':
    unittest.main()
