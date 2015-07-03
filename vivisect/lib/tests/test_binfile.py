import io
import unittest

import vivisect.lib.binfile as v_binfile

from vivisect.vstruct.types import *

class BinFileTest(unittest.TestCase):

    def test_binfile_info(self):

        class FakeBin(v_binfile.BinFile):

            def __init__(self,x):
                v_binfile.BinFile.__init__(self,x)
                self.info.addKeyCtor('woot', self._getWoot )

            def _getWoot(self):
                return 10

        bf = FakeBin(None)
        self.assertEqual( bf.getInfo('woot'), 10 )

    def test_binfile_baseaddr(self):

        class FakeBin(v_binfile.BinFile):
            def _getBaseAddr(self):
                return 10

        bf = FakeBin(None)
        self.assertEqual( bf.getBaseAddr(), 10 )

    def test_binfile_dict(self):

        # make sure it only gets called once
        data = {'value':30}
        def woot():
            ret = data['value']
            data['value'] += 1
            return ret

        b = v_binfile.BinDict()
        b.addKeyCtor('woot', woot)

        self.assertEqual( b.cog('woot'), 30 )
        self.assertEqual( b.cog('woot'), 30 )
        self.assertEqual( data.get('value'), 31 )

    def test_binfile_struct(self):
        class WootHeader(VStruct):
            def __init__(self):
                VStruct.__init__(self)
                self.foo = uint8()
                self.bar = uint8()

        bf = v_binfile.getBinFile(b'ASDFQWER',format='blob',arch='i386')

        w = bf.getStruct(0, WootHeader)
        self.assertEqual(w.foo, 0x41)
        self.assertEqual(w.bar, 0x53)

        for o,w in bf.getStructs(0, 8, WootHeader):
            self.assertEqual(w.foo, 0x41)
            self.assertEqual(w.bar, 0x53)
            break

    def test_binfile_blob(self):

        bf = v_binfile.getBinFile(b'ASDFQWER',format='blob',arch='i386')

        self.assertEqual( bf.getArch(), 'i386')
        self.assertEqual( bf.getFormat(), 'blob')
        self.assertEqual( bf.getPtrSize(), 4 )
        self.assertEqual( bf.readAtOff(0,3), b'ASD')

