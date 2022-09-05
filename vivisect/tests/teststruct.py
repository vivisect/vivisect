import io
import unittest

import vivisect


class StructTest(unittest.TestCase):
    def test_read_struct(self):
        vw = vivisect.VivWorkspace()
        src = 'struct foo { int bar; char baz; unsigned int biz[40]; }; // test struct'
        vw.setUserStructSource(src)

        usrc = vw.getUserStructSource('foo')
        self.assertEqual(1, len(vw.getUserStructNames()))
        self.assertEqual(usrc, src)

    def test_make_struct(self):
        fd = io.BytesIO(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xfc\xfd\xfe\xff')
        vw = vivisect.VivWorkspace()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.bigend = False
        vw.config.viv.parsers.blob.baseaddr = 0x22220000
        vw.loadFromFd(fd, fmtname='blob')

        src = 'struct allint {int foo; int bar; int baz; int biz;};'
        vw.setUserStructSource(src)
        vs = vw.makeStructure(0x22220000, 'allint')
        self.assertEqual(vs.foo, 0x03020100)
        self.assertEqual(vs.bar, 0x07060504)
        self.assertEqual(vs.baz, 0x0b0a0908)
        self.assertEqual(vs.biz, -0x010204)

        fd.seek(0)
        self.assertEqual(vs.vsEmit(), fd.read())
