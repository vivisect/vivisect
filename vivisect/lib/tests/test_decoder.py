import unittest
import vivisect.lib.bits as v_bits
import vivisect.lib.decoder as v_decoder

class DecoderTest(unittest.TestCase):

    def test_decoder_lookup(self):
        d = v_decoder.DecodeNode()
        d.addBitMask('0000000011111111','foo')
        d.addBitMask('1111111100000000','bar')
        self.assertEqual( d.getByBytes(b'\x00\xff'), 'foo')
        self.assertEqual( d.getByBytes(b'\xff\x00'), 'bar')

    def test_decoder_overlap(self):
        d = v_decoder.DecodeNode()
        # leaving these in this order also tests precedence
        d.addBitMask(v_bits.hex2bits('f0aa0a') + '1111....','foo')
        d.addBitMask(v_bits.hex2bits('f0aa0a') + '111110..','bar')
        self.assertEqual( d.getByBytes(b'\xf0\xaa\x0a\xf3'), 'foo')
        self.assertEqual( d.getByBytes(b'\xf0\xaa\x0a\xf8'), 'bar')

    def test_decoder_decode(self):
        d = v_decoder.Decoder()

        testdata = {}
        def callback(info):
            testdata.update(info)
            return 'nailedit'

        d.addDecodeMask('11110000ssssbbbb',callback,woot='woot')

        b = v_bits.h2b('0000f023')
        ret = d.runDecodeMask(b,offset=2,foo='foo')

        self.assertEqual(ret,'nailedit')
        self.assertEqual(testdata['off'],2)
        self.assertEqual(testdata['foo'],'foo')
        self.assertEqual(testdata['woot'],'woot')
        self.assertEqual(testdata['bits']['s'],2)
        self.assertEqual(testdata['bits']['b'],3)
        self.assertEqual(testdata['mask'],'11110000ssssbbbb')
