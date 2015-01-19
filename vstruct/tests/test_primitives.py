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

    def test_hasFmt(self):
        if not hasattr(self.vs, '_vs_fmt'):
            raise Exception('vstruct primitives must have _vs_fmt attr')

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
        #with self.assertRaisesRegex(Exception, 'specify size or bytez, not'):
        p.v_bytes(size=5, bytez=b'12345')
        # TODO:

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

class v_strTests(unittest.TestCase):
    def test_ctor_none(self):
        vs = p.v_str()
        self.assertEqual(1, len(vs))

        val = vs.vsGetValue()
        self.assertEqual(b'', val)

    def test_ctor_size(self, size=131):
        vs = p.v_str(size=size)
        self.assertEqual(size, len(vs))

        val = vs.vsGetValue()
        self.assertEqual(b'', val)

    def test_ctor_bytez(self, bytez=b'12345\x00'):
        vs = p.v_str(bytez=bytez)
        self.assertEqual(len(bytez), len(vs))

        val = vs.vsGetValue()
        self.assertEqual(bytez[:-1], val)

        val = vs.vsEmit()
        self.assertEqual(bytez, val)

    def test_ctor_bytez_size(self, size=10, bytez=b'12345'):
        vs = p.v_str(size=size, bytez=bytez)
        self.assertEqual(size, len(vs))

        val = vs.vsGetValue()
        self.assertEqual(bytez, val)

        val = vs.vsEmit()
        self.assertEqual(bytez + b'\x00' * 5, val)

    def test_vsSetValue_vsGetValue(self, bytez=b'12345\x00\x00'):
        vs = p.v_str()
        vs.vsSetValue(bytez)

        val = vs.vsGetValue()

        self.assertEqual(bytez[:-2], val)

    def test_vsGetValue_nonull(self, bytez=b'12345'):
        vs = p.v_str(bytez=bytez)
        val = vs.vsGetValue()
        self.assertEqual(bytez, val)

class AlignmentMixinTests(unittest.TestCase):
    def test_ctor(self):
        am = p.AlignmentMixin()
        am.fillbyte = b'\x00'
        self.assertEqual(am._vs_align, 1)

    def tmpl_test_vsGetPadding(self, _vs_length):
        am = p.AlignmentMixin()
        am.fillbyte = b'\x00'
        am._vs_length = _vs_length

        padc = am.vsGetPadding()

        return padc

    def test_vsGetPadding_012(self):
        for i in range(3):
            padc = self.tmpl_test_vsGetPadding(i)
            self.assertEqual(len(padc), 0)

    def test_vsAlign(self):
        for i in range(3):
            am = p.AlignmentMixin()
            am.fillbyte = b'\x00'
            am._vs_length = i
            vsval = b'A' * am._vs_length
            am._vs_value = vsval

            am.vsAlign()

            self.assertEqual(vsval, am._vs_value)
            self.assertEqual(len(am._vs_value), am._vs_length)

    def test_vsAlign_2(self, align=2):
        for idx, answer in enumerate( (b'', b'A\x00', b'AA') ):
            am = p.AlignmentMixin(align=align)
            am.fillbyte = b'\x00'
            am._vs_length = idx
            am._vs_value = b'A' * am._vs_length

            am.vsAlign()

            self.assertEqual(answer, am._vs_value)
            self.assertEqual(len(am._vs_value), am._vs_length)

    def test_vsAlign_4(self, align=4):
        for idx, answer in enumerate( (b'', b'A\x00\x00\x00', b'AA\x00\x00') ):
            am = p.AlignmentMixin(align=align)
            am.fillbyte = b'\x00'
            am._vs_length = idx
            am._vs_value = b'A' * am._vs_length

            am.vsAlign()

            self.assertEqual(answer, am._vs_value)
            self.assertEqual(len(am._vs_value), am._vs_length)

class v_zstrTests(unittest.TestCase):
    def test_ctor_none(self):
        vs = p.v_zstr()
        self.assertEqual(len(vs), 0)

    def test_ctor_bytez(self, bytez=b'12345'):
        vs = p.v_zstr(bytez=bytez)
        self.assertEqual(len(vs), len(bytez))

    def test_vsSetValue_vsGetValue(self, bytez=b'12345\x00\x00'):
        vs = p.v_zstr()
        vs.vsSetValue(bytez)

        val = vs.vsGetValue()

        self.assertEqual(bytez[:-2], val)

    def test_vsSetLength(self):
        vs = p.v_zstr()
        with self.assertRaisesRegex(Exception, 'cannot vsSetLength on'):
            vs.vsSetLength(64)

    def test_vsParse_invalid(self, bytez='12345'):
        vs = p.v_zstr()
        with self.assertRaisesRegex(Exception, 'pass object of type bytes'):
            vs.vsParse(bytez)

    def test_vsParse_nonull(self, bytez=b'12345'):
        vs = p.v_zstr()
        with self.assertRaisesRegex(Exception, 'found no NULL term'):
            vs.vsParse(bytez)

    def test_vsParse(self, bytez=b'12345\x00789abcdefghi'):
        vs = p.v_zstr()
        off = vs.vsParse(bytez)
        self.assertEqual(off, 6)

        # TODO: test type equality
        #print(type(vs))
        #self.assertEqual(vs, b'12345')
        val = vs.vsGetValue()
        self.assertEqual(len(val), len(b'12345'))

        val = vs.vsEmit()
        self.assertEqual(val, b'12345\x00')

    def test_zstr_vsParse_vsEmit_ctor(self):
        bytez = b'123\x00456\x00789\x00\x00'
        import vstruct
        class ZstrTest(vstruct.VStruct):
            def __init__(self):
                vstruct.VStruct.__init__(self)

                self.one = p.v_zstr()
                self.two = p.v_zstr()
                self.three = p.v_zstr()
                self.four = p.v_zstr()

        vs1 = ZstrTest()
        idx = vs1.vsParse(bytez)
        self.assertEqual(len(bytez), idx)

        val = vs1.one
        self.assertEqual(b'123', val)

        val = vs1.vsGetField('one').vsEmit()
        self.assertEqual(b'123\x00', val)

        val = vs1.vsEmit()
        self.assertEqual(bytez, val)

    def test_ctor_vsSetValue_vsParse_nonull(self, bytez=b'12345'):
        vs1 = p.v_zstr(bytez=bytez)
        self.assertEqual(vs1.vsGetValue(), bytez)
        self.assertEqual(vs1.vsEmit(), bytez)

        vs2 = p.v_zstr()
        vs2.vsSetValue(bytez)
        self.assertEqual(vs2.vsGetValue(), bytez)
        self.assertEqual(vs2.vsEmit(), bytez)

        vs3 = p.v_zstr()
        with self.assertRaisesRegex(Exception, 'found no NULL'):
            vs3.vsParse(bytez)

    def test_ctor_vsSetValue_vsParse_vsEmit_null(self, bytez=b'1234\x00'):
        vs1 = p.v_zstr(bytez=bytez)
        self.assertEqual(vs1.vsGetValue(), bytez[:-1])
        self.assertEqual(vs1.vsEmit(), bytez)

        vs2 = p.v_zstr()
        vs2.vsSetValue(bytez)
        self.assertEqual(vs2.vsGetValue(), bytez[:-1])
        self.assertEqual(vs2.vsEmit(), bytez)

        vs3 = p.v_zstr()
        vs3.vsParse(bytez)
        self.assertEqual(vs3.vsGetValue(), bytez[:-1])
        self.assertEqual(vs3.vsEmit(), bytez)

    def test_ctor_vsSetValue_vsParse_vsEmit_null_align2(self, bytez=b'1234\x00\xab\xcd', align=2):
        vs1 = p.v_zstr(bytez=bytez, align=2)
        self.assertEqual(vs1.vsGetValue(), b'1234')
        self.assertEqual(vs1.vsEmit(), bytez + b'\x00')

        vs2 = p.v_zstr(align=2)
        vs2.vsSetValue(bytez)
        self.assertEqual(vs2.vsGetValue(), b'1234')
        self.assertEqual(vs2.vsEmit(), bytez + b'\x00')

        # note the difference in the vsEmit for vsParse case vs the ctor
        # and vsSetValue.  vsParse consumes next byte in stream for the padding
        # whereas ctor and vsSetValue use vsAlign and the fillbyte.
        vs3 = p.v_zstr(align=2)
        vs3.vsParse(bytez)
        self.assertEqual(vs3.vsGetValue(), b'1234')
        self.assertEqual(vs3.vsEmit(), b'1234\x00\xab')

# TODO: add tests for fastparse with all the types deriving from v_prim

class v_wstrTests(unittest.TestCase):
    def test_ctor_none(self):
        vs = p.v_wstr()
        self.assertEqual(2, len(vs))

        vval = vs.vsGetValue()
        self.assertEqual('', vval)

        bytez = vs.vsEmit()
        self.assertEqual(b'\x00\x00', bytez)

    def test_ctor_size(self, size=131):
        vs = p.v_wstr(size=size)
        self.assertEqual(size*2, len(vs))

        vval = vs.vsGetValue()
        self.assertEqual('', vval)

        bytez = vs.vsEmit()
        self.assertEqual(b'\x00\x00'*size, bytez)

    def test_ctor_val(self, val='12345'):
        vs = p.v_wstr(val=val)
        self.assertEqual(len(val)*2, len(vs))

        vval = vs.vsGetValue()
        self.assertEqual(val, vval)

        vval = vs.vsEmit()
        self.assertEqual(val.encode('utf-16le'), vval)

    def test_ctor_val_size(self, size=20, val='12345'):
        vs = p.v_wstr(size=size, val=val)
        self.assertEqual(40, len(vs))

        vval = vs.vsGetValue()
        self.assertEqual(val, vval)

        vval = vs.vsEmit()
        self.assertEqual('12345'.encode('utf-16le') + b'\x00'*30, vval)

    def test_vsSetValue_vsGetValue(self, val='12345'):
        vs = p.v_wstr()
        vs.vsSetValue(val)

        # default size is 1.
        vval = vs.vsGetValue()
        self.assertEqual('1', vval)

        vval = vs.vsEmit()
        self.assertEqual(vval, '1'.encode('utf-16le'))

    def test_ctor_size_fill_vsSetValue_vsGetValue(self, val='12345'):
        vs = p.v_wstr(size=30)
        vs.vsSetValue(val)

        vval = vs.vsGetValue()
        self.assertEqual(val, vval)

        vval = vs.vsEmit()
        self.assertEqual(val.encode('utf-16le') + b'\x00'*25*2, vval)

    def test_ctor_size_chop_vsSetValue_vsGetValue(self, val='12345'):
        vs = p.v_wstr(size=2)
        vs.vsSetValue(val)
        self.assertEqual(4, len(vs))

        # TODO: create unicodedecodeerror due to chop
        vval = vs.vsGetValue()
        self.assertEqual('12', vval)

        vval = vs.vsEmit()
        self.assertEqual('12'.encode('utf-16le'), vval)
        self.assertEqual(4, len(vval))

    def test_vsGetValue_nonull(self, val='12345'):
        vs = p.v_wstr(val=val)
        vval = vs.vsGetValue()
        self.assertEqual(vval, val)
