import unittest

import vstruct
import vstruct.primitives as p

class NNestedStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.alpha = p.v_uint64()
        self.beta = vstruct.VStruct()

class NestedStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.foo = p.v_bytes(size=3)
        self.bar = p.v_uint32()
        self.baz = p.v_bytes(size=256)
        self.faz = NNestedStruct()

class TestStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.one = p.v_uint32()
        self.two = NestedStruct()
        self.three = p.v_uint32()
        self.four = p.v_bytes(size=100)

class VStructTests(unittest.TestCase):
    def setUp(self):
        self.s = TestStruct()

    def test_vsGetFieldByOffset_start(self):
        fname = self.s.vsGetFieldByOffset(0)
        self.assertEqual(fname, 'one')

    def test_vsGetFieldByOffset_end(self):
        fname = self.s.vsGetFieldByOffset(len(self.s) - 1)
        self.assertEqual(fname, 'four')

    def test_vsGetFieldByOffset_invalid1(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            fname = self.s.vsGetFieldByOffset(-1)

    def test_vsGetFieldByOffset_invalid2(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            fname = self.s.vsGetFieldByOffset(0xffffffff)

    def test_vsGetFieldByOffset_invalid3(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            fname = self.s.vsGetFieldByOffset(len(self.s))

    def test_vsGetFieldByOffset_nested1(self):
        fname = self.s.vsGetFieldByOffset(5)
        self.assertEqual(fname, 'two.foo')

    def test_vsGetFieldByOffset_nested2(self):
        fname = self.s.vsGetFieldByOffset(8)
        self.assertEqual(fname, 'two.bar')

    def test_vsGetFieldByOffset_nested3(self):
        fname = self.s.vsGetFieldByOffset(12)
        self.assertEqual(fname, 'two.baz')

    def test_vsGetFieldByOffset_nested4(self):
        fname = self.s.vsGetFieldByOffset(267)
        self.assertEqual(fname, 'two.faz.alpha')
