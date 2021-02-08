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
        self.assertEqual(decoded, 1.0)

        valu = 0xbfff8000000000000000
        decoded = e_float.float_decode(valu, 80)
        self.assertEqual(decoded, -1.0)

        valu = 0x4000d49a784bcd1b8afe
        decoded = e_float.float_decode(valu, 80)
        self.assertAlmostEqual(decoded, 3.32192809488736234781)

        valu = 0x4000c90fdaa22168c235
        decoded = e_float.float_decode(valu, 80)
        self.assertAlmostEqual(decoded, 3.14159265358979323851)

    def _encoding_test(self, valu, answers):
        for i, length in enumerate([16, 32, 64, 80, 128]):
            encoded = e_float.float_encode(valu, length)
            try:
                self.assertEqual(encoded, answers[i])
            except:
                self.fail("%s failed to encode properly (produced: 0x%x, test: 0x%x)" % (valu, encoded, answers[i]))

    def test_ieee_754_encode(self):
        pass
        # TODO: double check these and expand them
        #self._encoding_test(1, [0x3c00,
        #                        0x3f800000,
        #                        0x3ff0000000000000,
        #                        0x3fff8000000000000000])

        #self._encoding_test(0.26, [0x3428,
        #                           0x3e851eb8,
        #                           0x3ffd851eb851eb851eb8,
        #                           0x1ffe851eb851eb851ea0L])
