import unittest
from vstruct.defs.dwarf import leb128ToInt

class VstructDwarfTests(unittest.TestCase):
    def test_uleb(self):
        teststr = b'\x00\xFF\xFF'
        self.assertEqual((0, 1), leb128ToInt(teststr))

        teststr = b'\x11\x00'
        self.assertEqual((17, 1), leb128ToInt(teststr))

        teststr = b'\x02\xFF\xFF'
        self.assertEqual((2, 1), leb128ToInt(teststr))

        teststr = b'\x7f\xFF\xFF'
        self.assertEqual((127, 1), leb128ToInt(teststr))

        teststr = b'\x81\x01\xFF\xFF'
        self.assertEqual((129, 2), leb128ToInt(teststr))

        teststr = b'\x82\x01\xFF\xFF'
        self.assertEqual((130, 2), leb128ToInt(teststr))

        teststr = b'\xb9\x64\xFF\xFF'
        self.assertEqual((12857, 2), leb128ToInt(teststr))

    def test_sleb(self):
        teststr = b'\x02\xff\xff\xff'
        self.assertEqual((2, 1), leb128ToInt(teststr, signed=True))

        teststr = b'\x7e\xff\xff\xff'
        self.assertEqual((-2, 1), leb128ToInt(teststr, signed=True))

        teststr = b'\xff\x00\xff\xff'
        self.assertEqual((127, 2), leb128ToInt(teststr, signed=True))

        teststr = b'\x81\x7f\xff\xff'
        self.assertEqual((-127, 2), leb128ToInt(teststr, signed=True))

        teststr = b'\x80\x01\xff\xff'
        self.assertEqual((128, 2), leb128ToInt(teststr, signed=True))

        teststr = b'\x80\x7f\xff\xff'
        self.assertEqual((-128, 2), leb128ToInt(teststr, signed=True))

        teststr = b'\x81\x01\xff\xff'
        self.assertEqual((129, 2), leb128ToInt(teststr, signed=True))

        teststr = b'\xff\x7e\xff\xff'
        self.assertEqual((-129, 2), leb128ToInt(teststr, signed=True))
