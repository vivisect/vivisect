import io
import unittest

from ..types import *

class S1(VStruct):

    def __init__(self):
        VStruct.__init__(self)

        self.i8     = int8()
        self.i16    = int16()
        self.i32    = int32()
        self.i64    = int64()

        self.u8     = uint8()
        self.u16    = uint16()
        self.u32    = uint32()
        self.u64    = uint64()

        self.by6    = vbytes(6)
        self.cs6    = cstr(6)
        self.zs     = zstr()

s1bytes = b'\xff' * 36 + b'qwerty' + b'asdf\x00\x00\x00\x00'

class S2(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        self.size   = uint16().vsOnset( self.setBytesSize )
        self.string = cstr()

    def setBytesSize(self):
        self['string'].vsResize( self.size )

class S3(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.x      = uint8()
        self.y      = vbytes(6)

class S4(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.w      = uint8()
        self.x      = vbytes(3)
        self.y      = zstr()
        self.z      = uint16()

class TypesTest(unittest.TestCase):

    def test_vstruct_basic(self):
        s1 = S1()
        s1.vsParse(s1bytes)

        self.assertEqual( s1.i8,  -1 )
        self.assertEqual( s1.i16, -1 )
        self.assertEqual( s1.i32, -1 )
        self.assertEqual( s1.i64, -1 )

        self.assertEqual( s1.u8,  0xff)
        self.assertEqual( s1.u16, 0xffff)
        self.assertEqual( s1.u32, 0xffffffff)
        self.assertEqual( s1.u64, 0xffffffffffffffff)

        self.assertEqual( s1.by6, b'\xff' * 6 )
        self.assertEqual( s1.cs6, 'qwerty')
        self.assertEqual( s1.zs,  'asdf')

        self.assertEqual( len(s1['zs']), 5 )

    def test_vstruct_resize_onparse(self):

        s2 = S2()
        s2.vsParse(b'\x04\x00ASDFGGGGGGGGGGGGG')

        self.assertEqual( s2.size, 4 )
        self.assertEqual( s2.string, 'ASDF' )

    def test_vstruct_resize_onset(self):

        s2 = S2()
        self.assertEqual( s2.vsEmit(), b'\x00\x00')

        s2.size = 3
        self.assertEqual( s2.vsEmit(), b'\x03\x00\x00\x00\x00')

    def test_vstruct_lazy(self):

        s1 = S1()
        s1.vsParse(s1bytes)

        self.assertIsNone( s1['i8']._vs_value )
        self.assertIsNone( s1['u8']._vs_value )
        self.assertIsNone( s1['by6']._vs_value )
        self.assertIsNone( s1['cs6']._vs_value )

    def test_vstruct_writeback(self):

        buf = bytearray(b'\x00' * 8)

        s3 = S3()
        s3.vsParse( buf, writeback=True )

        s3.x = 20
        self.assertEqual( bytes(buf), b'\x14' + b'\x00' * 7)

    def test_vstruct_load(self):
        s4 = S4()

        fd = io.BytesIO(b'\xffQQQabcd\x00VV')
        off = s4.vsLoad(fd, writeback=True)

        self.assertEqual(s4.w, 0xff)
        self.assertEqual(s4.x, b'QQQ')
        self.assertEqual(s4.y, 'abcd')
        self.assertEqual(s4.z, 0x5656)

        self.assertEqual(off,11)

        s4.x = b'RRR'
        fd.seek(0)

        self.assertEqual( fd.read(), b'\xffRRRabcd\x00VV')

