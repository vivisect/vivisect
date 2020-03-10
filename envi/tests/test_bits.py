import unittest
import envi.bits as e_bits


class EnviBitsTest(unittest.TestCase):
    def test_envi_bits_masktest(self):
        self.assertTrue(e_bits.masktest('11001100')(0xcc))
        self.assertTrue(e_bits.masktest('1100110011001100')(0xcccc))
        self.assertTrue(e_bits.masktest('1100xxxx1100xxxx')(0xc2c2))
        self.assertFalse(e_bits.masktest('110011xx110011xx')(0xc2c2))

    def test_ieee_754_decode(self):
        valu = 0x3fff8000000000000000
        decoded = e_bits.intel_float_decode(valu)
        self.assertEquals(decoded, 1.0)

        valu = 0xbfff8000000000000000
        decoded = e_bits.intel_float_decode(valu)
        self.assertEquals(decoded, -1.0)

        valu = 0x4000d49a784bcd1b8afe
        decoded = e_bits.intel_float_decode(valu)
        self.assertAlmostEquals(decoded, 3.32192809488736234781)

        valu = 0x4000c90fdaa22168c235
        decoded = e_bits.intel_float_decode(valu)
        self.assertAlmostEquals(decoded, 3.14159265358979323851)
