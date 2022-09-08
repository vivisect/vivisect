import binascii
import unittest

import vstruct
import vstruct.cparse as s_cparse
from vstruct.primitives import *
from vstruct.bitfield import *

from io import BytesIO


class woot(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.lenfield = v_uint8()
        self.strfield = v_str(size=0x20)

    def pcb_lenfield(self):
        self.vsGetField('strfield').vsSetLength(self.lenfield)


class AwesomeTest(s_cparse.CVStruct):
    '''
    struct awesome {
        int x,z;
        char stuff[20];
        int y;
        struct haha {
            int blah;
        } s;
        int *q;
    };
    '''


class VStructTest(unittest.TestCase):

    def test_autoparse(self):
        awe = AwesomeTest()
        awe.vsParse(b'XXXXZZZZhow cool is this?\x00\x00\x00YYYYblahQQQQ')
        self.assertEqual(awe.x, 0x58585858)
        self.assertEqual(awe.z, 0x5A5A5A5A)
        self.assertEqual(awe.stuff, 'how cool is this?')
        self.assertEqual(awe.y, 0x59595959)
        self.assertEqual(awe.s.blah, 0x68616c62)
        self.assertEqual(awe.q, 0x51515151)

    def test_vstruct_basicstruct(self):

        v = vstruct.VStruct()
        v.uint8 = v_uint8(1)
        v.uint16 = v_uint16(2)
        v.uint24 = v_uint24(3)
        v.uint32 = v_uint32(4)
        v.uint64 = v_uint64(5)
        v.vbytes = v_bytes(vbytes=b'ABCD')

        answer = binascii.unhexlify(b'01020003000004000000050000000000000041424344')
        self.assertEqual( v.vsEmit(), answer )


    def test_vstruct_basicreassign(self):
        v = vstruct.VStruct()
        v.uint8 = v_uint8(1)
        v.uint16 = v_uint16(2)
        v.uint24 = v_uint24(3)
        v.uint32 = v_uint32(4)
        v.uint64 = v_uint64(5)
        v.vbytes = v_bytes(vbytes=b'ABCD')

        v.uint8 = 99
        v.uint16 = 100
        v.uint24 = 101
        v.uint32 = 102
        v.uint64 = 103
        v.vbytes = b'\x00\x00\x00\x00'

        answer = binascii.unhexlify('63640065000066000000670000000000000000000000')
        self.assertEqual( v.vsEmit(), answer )


    def test_vstruct_fieldalign(self):
        v = vstruct.VStruct()
        v._vs_field_align = True
        v.uint8 = v_uint8(0x42, bigend=True)
        v.uint16 = v_uint16(0x4243, bigend=True)
        v.uint24 = v_uint24(0x424344, bigend=True)
        v.uint32 = v_uint32(0x42434445, bigend=True)
        v.uint64 = v_uint64(0x4243444546474849, bigend=True)

        answer = binascii.unhexlify('420042430000424344000000424344454243444546474849')
        self.assertEqual( v.vsEmit(), answer )

    def test_vstruct_fixedpartialasign(self):
        v = vstruct.VStruct()
        v.strfield = v_str(size=30)
        v.unifield = v_wstr(size=30)

        v.strfield = 'wootwoot!'
        v.unifield = 'bazbaz'

        answer = binascii.unhexlify('776f6f74776f6f7421000000000000000000000000000000000000000000620061007a00620061007a00000000000000000000000000000000000000')
        self.assertEqual(v.vsEmit(), answer)

    def test_vstruct_lengthcallback(self):

        def updatelen(vs):
            vs.vsGetField('strfield').vsSetLength(vs.lenfield)

        v = vstruct.VStruct()
        v.lenfield = v_uint8(0x30)
        v.strfield = v_str(size=30)
        v.vsAddParseCallback('lenfield', updatelen)

        v.vsParse(b'\x01' + b'A' * 30)
        self.assertEqual( v.vsEmit(), binascii.unhexlify('0141') )


    def test_vstruct_classcallback(self):
        v = woot()
        v.vsParse(b'\x01' + b'A'*30)
        self.assertEqual( v.vsEmit(), binascii.unhexlify('0141') )

    def test_vstruct_parsefd(self):
        v = woot()
        sio = BytesIO((b'\x01' + b'A' * 30))
        v.vsParseFd(sio)
        self.assertEqual( v.vsEmit(), binascii.unhexlify('0141') )

    def test_vstruct_insertfield(self):
        v = woot()
        v.vsInsertField('ifield', v_uint8(), 'strfield')
        v.vsParse(b'\x01BAAAAA')
        self.assertEqual( v.vsEmit(), binascii.unhexlify('014241') )

    def test_vstruct_floats(self):

        v = vstruct.VStruct()
        v.float4 = v_float()
        v.float8 = v_double()

        v.float4 = 99.3
        v.float8 = -400.2

        self.assertEqual(v.vsEmit(), binascii.unhexlify('9a99c64233333333330379c0'))

    def test_vstruct_fastparse(self):
        v = vstruct.VStruct()
        v.x = v_uint8()
        v.y = v_str(size=4)
        v.z = v_uint32()

        v.vsParse(b'BAAAAABCD', fast=True)

        self.assertEqual( v.x, 0x42 )
        self.assertEqual( v.y, 'AAAA' )
        self.assertEqual( v.z, 0x44434241 )

    def test_vstruct_fastparse_bigend(self):
        v = vstruct.VStruct()
        v.x = v_uint8()
        v.y = v_str(size=4)
        v.z = v_uint32(bigend=True)

        v.vsParse(b'BAAAAABCD', fast=True)

        self.assertEqual( v.x, 0x42 )
        self.assertEqual( v.y, 'AAAA' )
        self.assertEqual( v.z, 0x41424344 )

    def test_vstruct_varray(self):
        v = vstruct.VArray( [ v_uint8(i) for i in range(20) ] )
        self.assertEqual(v[2], 2)
        self.assertTrue(v[5] <= 5)
        self.assertTrue(v[5] > 2)
        self.assertTrue(v[19] >= 19)
        v.vsParse(b'A' * 20)
        self.assertEqual( v[2], 0x41 )

    def test_bitfield(self):
        v = VBitField()
        v.vsAddField('w', v_bits(2))
        v.vsAddField('x', v_bits(3))
        v.vsAddField('y', v_bits(3))
        v.vsAddField('z', v_bits(11))
        v.vsAddField('a', v_bits(3))

        v.vsAddField('stuff', v_bits(23))
        v.vsAddField('pad', v_bits(3))
        v.vsAddField('pad2', v_bits(6))
        v.vsAddField('pad3', v_bits(2))

        v.vsParse(b'AAAAAAA')
        self.assertEqual(1, v.w)
        self.assertEqual(0, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x20a, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x282828, v.stuff)
        self.assertEqual(1, v.pad)
        self.assertEqual(16, v.pad2)
        self.assertEqual(1, v.pad3)

        self.assertEqual(b'AAAAAAA', v.vsEmit())

        v.vsParse(b'ABCDEFG')
        self.assertEqual(1, v.w)
        self.assertEqual(0, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x212, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x6888a8, v.stuff)
        self.assertEqual(6, v.pad)
        self.assertEqual(17, v.pad2)
        self.assertEqual(3, v.pad3)

        self.assertEqual(b'ABCDEFG', v.vsEmit())

        v.vsParse(b'zxcvbnm')
        self.assertEqual(1, v.w)
        self.assertEqual(7, v.x)
        self.assertEqual(2, v.y)
        self.assertEqual(0x3c3, v.z)
        self.assertEqual(0, v.a)
        self.assertEqual(0x6ecc4d, v.stuff)
        self.assertEqual(6, v.pad)
        self.assertEqual(0x1b, v.pad2)
        self.assertEqual(1, v.pad3)

        self.assertEqual(b'zxcvbnm', v.vsEmit())

        v.vsParse(b'asdfghj')
        self.assertEqual(1, v.w)
        self.assertEqual(4, v.x)
        self.assertEqual(1, v.y)
        self.assertEqual(0x39b, v.z)
        self.assertEqual(1, v.a)
        self.assertEqual(0xccced, v.stuff)
        self.assertEqual(0, v.pad)
        self.assertEqual(0x1a, v.pad2)
        self.assertEqual(2, v.pad3)

        self.assertEqual(b'asdfghj', v.vsEmit())

    def test_guid(self):
        guid = GUID()
        self.assertEqual(guid.vsGetValue(), '{00000000-0000-0000-0000-000000000000}')

        othr = '{ae03101c-b34a-19cf-9ef3-6d1d62b299a2}'
        guid.vsSetValue(othr)
        self.assertEqual(guid.vsGetValue(), othr)

        gstr = '{59e22249-ffff-0123-f15d-9582e708191e}'
        guid = GUID(guidstr=gstr)
        self.assertEqual(guid.vsGetValue(), gstr)

        bytez = b'I"\xe2Y\xb3\xdb\xa8\x1c\xf1]\x95\x82\xe7\x08\x19\x1e'
        guid.vsParse(bytez)
        self.assertEqual(guid.vsGetValue(), '{59e22249-dbb3-1ca8-f15d-9582e708191e}')
        self.assertEqual(guid.vsEmit(), bytez)

    def test_str(self):
        bytez = b'aquickbrowndog\x00didnotgetfooledbyafox'
        s = v_str(size=100)
        s.vsParse(bytez)
        self.assertEqual(s.vsGetValue(), 'aquickbrowndog')

        s.vsSetLength(128)
        self.assertEqual(s.vsGetValue(), 'aquickbrowndog')
        self.assertEqual(s.vsEmit(), bytez + b'\x00' * (128-len(bytez)))

        s.vsSetLength('6')
        self.assertEqual(s.vsGetValue(), 'aquick')
        self.assertEqual(s.vsEmit(), b'aquick')
        # it doesn't come back
        s.vsSetLength(64)
        self.assertEqual(s.vsGetValue(), 'aquick')
        self.assertEqual(s.vsEmit(), b'aquick' + b'\x00' * 58)

    def test_zstr(self):
        bytez = b'swish\x00\x00swoosh'
        s = v_zstr()
        s.vsParse(bytez)
        self.assertEqual(s.vsGetValue(), 'swish')

        self.assertEqual(s.vsEmit(), b'swish\x00')

    def test_wstr(self):
        bytez = b'a\x00c\x00c\x00e\x00l\x00e\x00r\x00a\x00t\x00o\x00r\x00.\x00d\x00l\x00l\x00\x00\x00'
        s = v_wstr(size=100)
        s.vsParse(bytez)
        self.assertEqual(s.vsGetValue(), "accelerator.dll")
        self.assertEqual(s.vsEmit(), bytez)

    def test_zwstr(self):
        # Very similar to the above, but with slight tweaks to show the use case differences
        bytez = b'a\x00c\x00c\x00e\x00l\x00e\x00r\x00a\x00t\x00o\x00r\x00.\x00d\x00l\x00l\x00\x00\x00y\x00e\x00e\x00t\x00\x00'
        s = v_zwstr()
        s.vsParse(bytez)
        self.assertEqual(s.vsGetValue(), "accelerator.dll")
        self.assertEqual(s.vsEmit(), b'a\x00c\x00c\x00e\x00l\x00e\x00r\x00a\x00t\x00o\x00r\x00.\x00d\x00l\x00l\x00\x00\x00')

    def test_unsigned(self):
        s = v_uint16(value=17)
        byts = s.vsEmit()
        self.assertEqual(b'\x11\x00', byts)

        new = v_uint16()
        new.vsParse(byts)
        self.assertEqual(new.vsEmit(), s.vsEmit())

        # test class that skips by having a real format
        class v_silly(v_number):
            _vs_builder = True
            _vs_length = 5

        num = v_silly(value=1947824, bigend=True)
        byts = num.vsEmit()
        self.assertEqual(b'\x00\x00\x1d\xb8\xb0', byts)

        othr = v_silly(bigend=True)
        othr.vsParse(byts)
        self.assertEqual(othr, num)

    def test_signed(self):
        s = v_int16(value=-1)
        self.assertEqual(b'\xff\xff', s.vsEmit())

        s.vsSetValue(1)
        self.assertEqual(b'\x01\x00', s.vsEmit())

        s = v_int16(value=-1, bigend=True)
        self.assertEqual(b'\xff\xff', s.vsEmit())

        s.vsSetValue(1)
        self.assertEqual(b'\x00\x01', s.vsEmit())

        s = v_int32(value=32)
        self.assertEqual(b'\x20\x00\x00\x00', s.vsEmit())

        s = v_int32(value=-32)
        self.assertEqual(b'\xe0\xff\xff\xff', s.vsEmit())
