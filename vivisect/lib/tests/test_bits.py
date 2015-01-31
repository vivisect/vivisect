import unittest
import vivisect.lib.bits as v_bits

class TestLibBits(unittest.TestCase):

    def test_bits_h2b(self):
        self.assertEqual(v_bits.h2b('41414141'),b'AAAA')

    def test_bits_b2h(self):
        self.assertEqual(v_bits.b2h(b'AAAA'),'41414141')

    def test_bits_hex2bits(self):
        b = '0000000100100011010001010110011110001001101010111100110111101111'
        self.assertEqual(v_bits.hex2bits('0123456789abcdef'),b)

    def test_bits_signext(self):
        self.assertEqual(v_bits.signext(0xff,8,16),0xffff)
        self.assertEqual(v_bits.signext(0xff,9,16),0xff)
        self.assertEqual(v_bits.signext(-2,24,32),0xfffffffe)

    def test_bits_signed(self):
        self.assertEqual(v_bits.signed(0xff,8),-1)
        self.assertEqual(v_bits.signed(0x0f,8),0x0f)

    def test_bits_unsigned(self):
        self.assertEqual(v_bits.unsigned(-1,8),0xff)
        self.assertEqual(v_bits.unsigned(0xff,8),0xff)

    def test_bits_bitparser(self):
        p = v_bits.bitparser('1aaabb.cc.......')
        b = p( v_bits.bits2bytes('0000100010000000') )
        self.assertEqual( b['a'], 0)
        self.assertEqual( b['b'], 2)
        self.assertEqual( b['c'], 1)
