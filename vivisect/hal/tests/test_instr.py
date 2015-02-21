import unittest

import vivisect.hal.cpu as v_cpu
import vivisect.lib.bits as v_bits

class InstrTests(unittest.TestCase):

    def _get_dis(self, hexstr):
        cpu = v_cpu.getArchCpu('i386',addmap=(0x41410000,7,4096))
        cpu[0x41410000:] = v_bits.h2b(hexstr)
        return cpu.disasm(0x41410000)

    def test_instr_size(self):
        self.assertEqual( self._get_dis('6639d8').size(), 3)

    def test_instr_mnem(self):
        self.assertEqual( self._get_dis('6639d8').mnem(),'cmp')

    def test_instr_hex(self):
        self.assertEqual( self._get_dis('6639d8').hex(),'6639d8')

    def test_instr_text(self):
        self.assertEqual( self._get_dis('6639d8').text(),'cmp ax,bx')
