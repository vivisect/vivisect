import unittest
import vivisect.tests.helpers as helpers
from vivisect.parsers.dwarf import leb128ToInt


class HelperTest(unittest.TestCase):

    def test_helper_pathjoin(self):
        # retrieve a known vivtestfiles path ( or skip )
        helpers.getTestPath('windows', 'i386', 'helloworld.exe')

    def test_uleb(self):
        teststr = '\x00\xFF\xFF'
        self.assertEqual((0, 1), leb128ToInt(teststr))

        teststr = '\x11\x00'
        self.assertEqual((17, 1), leb128ToInt(teststr))

        teststr = '\x02\xFF\xFF'
        self.assertEqual((2, 1), leb128ToInt(teststr))

        teststr = '\x7f\xFF\xFF'
        self.assertEqual((127, 1), leb128ToInt(teststr))

        teststr = '\x81\x01\xFF\xFF'
        self.assertEqual((129, 2), leb128ToInt(teststr))

        teststr = '\x82\x01\xFF\xFF'
        self.assertEqual((130, 2), leb128ToInt(teststr))

        teststr = '\xb9\x64\xFF\xFF'
        self.assertEqual((12857, 2), leb128ToInt(teststr))

    def test_sleb(self):
        teststr = '\x02\xff\xff\xff'
        self.assertEqual((2, 1), leb128ToInt(teststr, signed=True))

        teststr = '\x7e\xff\xff\xff'
        self.assertEqual((-2, 1), leb128ToInt(teststr, signed=True))

        teststr = '\xff\x00\xff\xff'
        self.assertEqual((127, 2), leb128ToInt(teststr, signed=True))

        teststr = '\x81\x7f\xff\xff'
        self.assertEqual((-127, 2), leb128ToInt(teststr, signed=True))

        teststr = '\x80\x01\xff\xff'
        self.assertEqual((128, 2), leb128ToInt(teststr, signed=True))

        teststr = '\x80\x7f\xff\xff'
        self.assertEqual((-128, 2), leb128ToInt(teststr, signed=True))

        teststr = '\x81\x01\xff\xff'
        self.assertEqual((129, 2), leb128ToInt(teststr, signed=True))

        teststr = '\xff\x7e\xff\xff'
        self.assertEqual((-129, 2), leb128ToInt(teststr, signed=True))
