import io
import struct
import unittest

import vstruct.primitives as p

class v_enumTests(unittest.TestCase):
    def setUp(self):
        self.vs = p.v_enum()

    def test_setattr(self):
        self.vs.FOO = 1

        self.assertEqual(self.vs.FOO, 1)

    def test_vsLookup(self):
        self.vs.BAR = 0xdeadbeef

        val = self.vs.vsLookup(0xdeadbeef)
        self.assertEqual(val, 'BAR')

class v_bitmaskTests(unittest.TestCase):
    def setUp(self):
        self.vs = p.v_bitmask()

    # TODO: need tests

class v_baseTests(unittest.TestCase):
    def setUp(self):
        self.vs = p.v_base()

    def test_vsGetTypeName(self):
        name = self.vs.vsGetTypeName()

        self.assertEqual(name, 'v_base')

    def test_vsSetMeta_vsGetMeta(self):
        self.vs.vsSetMeta('foo', 'bar')
        val = self.vs.vsGetMeta('foo')

        self.assertEqual(val, 'bar')

    def test_vsCalculate(self):
        self.vs.vsCalculate()

    def test_vsParse(self):
        with self.assertRaises(NotImplementedError):
            self.vs.vsParse(b'')

    def test_vsIsPrim(self):
        with self.assertRaises(NotImplementedError):
            self.vs.vsIsPrim()

class v_primTests(unittest.TestCase):
    def setUp(self):
        self.vs = p.v_prim()

    def test_vsIsPrim(self):
        isprim = self.vs.vsIsPrim()

        self.assertTrue(isprim)

    def test_vsParseFd(self):
        bytez = io.BytesIO(b'asdf')
        with self.assertRaisesRegex(Exception, 'Not enough data'):
            self.vs.vsParseFd(bytez)

    def test_vsEmit(self):
        with self.assertRaises(NotImplementedError):
            self.vs.vsEmit()

    def test_vsSetValue_vsGetValue(self):
        self.vs.vsSetValue(123)
        val = self.vs.vsGetValue()

        self.assertEqual(val, 123)

    def test_vsSetLength(self):
        with self.assertRaises(NotImplementedError):
            self.vs.vsSetLength(1024)

    def test_repr(self):
        self.vs.vsSetValue(0xdeadbeef)
        val = repr(self.vs)

        self.assertEqual(val, repr(0xdeadbeef))

    def test_str(self):
        self.vs.vsSetValue(0xdeadbeef)
        val = str(self.vs)

        self.assertEqual(val, str(0xdeadbeef))

    def test_bytes(self):
        with self.assertRaises(NotImplementedError):
            bytes(self.vs)

    def test_len(self):
        self.vs.vsSetValue(0xdeadbeef)
        # no updating of the length on assignment is done in this class.
        with self.assertRaisesRegex(TypeError, 'interpreted as an integer'):
            val = len(self.vs)

class v_numberTests(unittest.TestCase):
    def setUp(self):
        self.vs = p.v_number()

    def test_vsParse_vsEmit_fmt_123_le(self):
        bytez = struct.pack('<B', 123)

        vs = p.v_number(bigend=False)
        off = vs.vsParse(bytez)
        self.assertEqual(off, 1)

        val = vs.vsGetValue()

        self.assertEqual(val, 123)

        ebytez = vs.vsEmit()
        self.assertEqual(ebytez, bytez)

    def test_vsParse_vsEmit_fmt_123_be(self):
        bytez = struct.pack('>B', 123)

        vs = p.v_number(bigend=True)
        off = vs.vsParse(bytez)
        self.assertEqual(off, 1)

        val = vs.vsGetValue()

        self.assertEqual(val, 123)

        ebytez = vs.vsEmit()
        self.assertEqual(ebytez, bytez)

    def test_vsParse_vsEmit_fmt_123_le_smash_fmt(self):
        bytez = struct.pack('<B', 123)

        vs = p.v_number(bigend=False)

        # smash fmt to force vsParse/vsEmit code down other path
        vs._vs_fmt = None

        off = vs.vsParse(bytez)
        self.assertEqual(off, 1)

        val = vs.vsGetValue()

        self.assertEqual(val, 123)

        ebytez = vs.vsEmit()
        self.assertEqual(ebytez, bytez)

    def test_vsParse_vsEmit_fmt_123_be_smash_fmt(self):
        bytez = struct.pack('>B', 123)

        vs = p.v_number(bigend=True)

        # smash fmt to force vsParse/vsEmit code down other path
        vs._vs_fmt = None

        off = vs.vsParse(bytez)
        self.assertEqual(off, 1)

        val = vs.vsGetValue()

        self.assertEqual(val, 123)

        ebytez = vs.vsEmit()
        self.assertEqual(ebytez, bytez)

    def test_vsEmit_ctor(self):
        vs = p.v_number(value=123, bigend=False)
        val = vs.vsEmit()

        self.assertEqual(val, b'\x7b')

    # covered in tests_vstructs.py for all the u(int) types
    #def test_vsSetValue_vsGetValue(self):
    #    pass

    # TODO: add tests for number api
    def test_numberApi(self):
        pass

# v_snumber is covered in tests_vstructs.py for all the u(int) types

# TODO: add tests for size_t, ptr, float

class v_bytesTests(unittest.TestCase):
    def test_ctor_size_bytes(self):
        with self.assertRaisesRegex(Exception, 'specify size or bytez, not'):
            p.v_bytes(size=5, bytez=b'12345')

    def test_ctor_none(self):
        vs = p.v_bytes()
        self.assertEqual(0, len(vs))

        val = vs.vsGetValue()
        self.assertEqual(b'', val)

    def test_ctor_size(self, size=9):
        vs = p.v_bytes(size=size)
        self.assertEqual(size, len(vs))

        val = vs.vsGetValue()
        self.assertEqual(b'\x00' * size, val)

    def test_ctor_bytez(self, bytez=b'12345'):
        vs = p.v_bytes(bytez=bytez)
        self.assertEqual(len(bytez), len(vs))

        val = vs.vsGetValue()
        self.assertEqual(bytez, val)

    def test_ctor_bytez_invalid(self, bytez='12345'):
        with self.assertRaisesRegex(Exception, 'pass object of type bytes'):
            vs = p.v_bytes(bytez=bytez)

    def test_vsSetValue_invalid(self):
        vs = p.v_bytes()
        with self.assertRaisesRegex(Exception, 'field set to wrong length'):
            vs.vsSetValue(b'12345')

    def test_vsSetValue_invalid_type(self):
        vs = p.v_bytes(size=5)
        with self.assertRaisesRegex(Exception, 'pass object of type bytes'):
            vs.vsSetValue('12345')

    def test_vsSetValue_valid(self, bytez=b'12345'):
        vs = p.v_bytes(size=5)
        vs.vsSetValue(bytez)
        val = vs.vsGetValue()

        self.assertEqual(bytez, val)

    def test_vsParse(self, bytez=b'0123456789'):
        vs = p.v_bytes(size=10)
        off = vs.vsParse(bytez)
        self.assertEqual(off, 10)
        val = vs.vsGetValue()

        self.assertEqual(bytez, val)

    def test_vsParse_offset(self, size=2, bytez=b'0123456789', offset=3):
        vs = p.v_bytes(size=2)
        off = vs.vsParse(bytez, offset=offset)
        self.assertEqual(off, 5)
        val = vs.vsGetValue()

        self.assertEqual(bytez[offset:offset+size], val)

    def test_vsEmit(self, bytez=b'1234'):
        vs = p.v_bytes(bytez=bytez)
        ebytez = vs.vsEmit()

        self.assertEqual(ebytez, bytez)

    def test_vsSetLength_neg(self, size=-1):
        vs = p.v_bytes()
        with self.assertRaisesRegex(Exception, 'lengths must be > 0'):
            vs.vsSetLength(size)

    def test_vsSetLength_expand(self, size=10, bytez=b'12345'):
        vs = p.v_bytes(bytez=bytez)
        vs.vsSetLength(size)
        val = vs.vsGetValue()
        evval = vs.vsEmit()

        self.assertEqual(size, len(vs))
        self.assertEqual(val, b'12345' + bytes(5))
        self.assertEqual(evval, b'12345' + bytes(5))

    def test_vsSetLength_chop(self, size=2, bytez=b'12345'):
        vs = p.v_bytes(bytez=bytez)
        vs.vsSetLength(size)
        val = vs.vsGetValue()
        evval = vs.vsEmit()

        self.assertEqual(size, len(vs))
        self.assertEqual(val, b'12')
        self.assertEqual(evval, b'12')

    def test_repr(self, bytez=b'12345'):
        vs = p.v_bytes(bytez=bytez)

        self.assertEqual(repr(bytez), repr(vs))
