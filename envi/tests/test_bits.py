import unittest
import envi.bits as e_bits


class EnviBitsTest(unittest.TestCase):
    def test_envi_bits_masktest(self):
        self.assertTrue(e_bits.masktest('11001100')(0xcc))
        self.assertTrue(e_bits.masktest('1100110011001100')(0xcccc))
        self.assertTrue(e_bits.masktest('1100xxxx1100xxxx')(0xc2c2))
        self.assertFalse(e_bits.masktest('110011xx110011xx')(0xc2c2))

    def test_ieee754_encode(self):
        pass

    def test_byteswap(self):
        self.assertEqual(0x12345678, e_bits.byteswap(0x78563412, 4))

    def test_msb(self):
        self.assertEqual(1, e_bits.msb(0x80, 1))
        self.assertEqual(0, e_bits.msb(0x7f, 1))
        self.assertEqual(1, e_bits.msb(0x8000, 2))
        self.assertEqual(0, e_bits.msb(0x7fff, 2))
        self.assertEqual(1, e_bits.msb(0x80000000, 4))
        self.assertEqual(0, e_bits.msb(0x7fffffff, 4))
        self.assertEqual(1, e_bits.msb(0x8000000000000000, 8))
        self.assertEqual(0, e_bits.msb(0x7fffffffffffffff, 8))

        self.assertEqual(1, e_bits.msb_minus_one(0x40, 1))
        self.assertEqual(0, e_bits.msb_minus_one(0xbf, 1))
        self.assertEqual(1, e_bits.msb_minus_one(0x4000, 2))
        self.assertEqual(0, e_bits.msb_minus_one(0xbfff, 2))
        self.assertEqual(1, e_bits.msb_minus_one(0x40000000, 4))
        self.assertEqual(0, e_bits.msb_minus_one(0xbfffffff, 4))
        self.assertEqual(1, e_bits.msb_minus_one(0x4000000000000000, 8))
        self.assertEqual(0, e_bits.msb_minus_one(0xbfffffffffffffff, 8))
