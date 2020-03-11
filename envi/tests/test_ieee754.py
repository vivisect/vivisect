import unittest
import envi.ieee754 as e_float


class FloatingPointTest(unittest.TestCase):
    def test_ieee_754_decode(self):
        # 32 bits
        valu = 0x40e00000
        decoded = e_float.float_decode(valu, 32)

        # intel's "extended" format that uses 80 bits
        valu = 0x3fff8000000000000000
        decoded = e_float.float_decode(valu, 80)
        self.assertEquals(decoded, 1.0)

        valu = 0xbfff8000000000000000
        decoded = e_float.float_decode(valu, 80)
        self.assertEquals(decoded, -1.0)

        valu = 0x4000d49a784bcd1b8afe
        decoded = e_float.float_decode(valu, 80)
        self.assertAlmostEquals(decoded, 3.32192809488736234781)

        valu = 0x4000c90fdaa22168c235
        decoded = e_float.float_decode(valu, 80)
        self.assertAlmostEquals(decoded, 3.14159265358979323851)

    def test_ieee_754_encode(self):
        valu = 0.26
        encoded = e_float.float_encode(valu, 16)
        encoded = e_float.float_encode(valu, 32)
        encoded = e_float.float_encode(valu, 64)
        encoded = e_float.float_encode(valu, 80)
        encoded = e_float.float_encode(valu, 128)

        valu = 3.14159

        valu = 1

        valu = 2

        valu = 12738.248976
