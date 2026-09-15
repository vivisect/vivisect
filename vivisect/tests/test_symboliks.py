import unittest
from binascii import unhexlify

import vivisect
import vivisect.symboliks.analysis as vs_anal
from vivisect.symboliks.common import *

class GenericSymboliksTest(unittest.TestCase):

    def test_vivisect_symboliks_amd64_movsxd(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture', 'amd64')
        vw.addMemoryMap(0x41410000, 0xff, 'none', unhexlify('4c8d055ef91e000fb6c9496304884c01c0ffe0'))
        #vw.addMemoryMap(0x41410000, 0xff, 'none', unhexlify'49630488'))
        #vw.addMemoryMap(0x41410000, 0xff, 'none', unhexlify('496304884c01c0ffe0'))
        vw.addMemoryMap(0x41420000, 0xff, 'none', unhexlify('371303ff031337'))
        vw.addMemoryMap(0x31336, 0xff, 'none', unhexlify('371303ff031337'))

        sctx = vs_anal.getSymbolikAnalysisContext(vw)
        xlate = sctx.getTranslator()

        off = 0
        for x in range(5):
            op = vw.parseOpcode(0x41410000 + off)
            xlate.translateOpcode(op)
            off += len(op)

        semu = vivisect.symboliks.emulator.SymbolikEmulator(vw)

        semu.setSymVariable('r8', Const(0x31337, 8))
        semu.setSymVariable('rcx', Const(0, 8))
        semu.writeSymMemory(Const(0x31337, 8), Const(0xffffffff, 8))
        semu.writeSymMemory(Const(0x31336, 8), Const(0x47145, 8))

        semu.applyEffects(xlate.getEffects())
        rax = semu.getSymVariable('rax')
        print(rax)
        print(hex(rax.solve()))
