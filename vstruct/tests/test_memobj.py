import unittest

import PE
import vstruct
import vivisect.tests.helpers as vt_help

class MemObjPe(unittest.TestCase):
    def setUp(self):
        self.vw = vt_help.getTestWorkspace_nocache('windows','amd64','helloworld.exe', analyze=False)
        baseva = 0x140000000
        self.pe = PE.peFromMemoryObject(self.vw, baseva)

    def test_pe_from_memobj(self):
        self.assertEqual(self.pe.fd.getSize(), 0xf800)
        self.assertEqual(self.pe.fd.getMemSize(), 0x11400)
        self.pe.fd.seek(0)
        self.assertEqual(len(self.pe.fd.read()), 0xf800)

