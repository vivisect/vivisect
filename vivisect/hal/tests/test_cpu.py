import unittest

from vertex.lib.common import tufo

import vivisect.hal.cpu as v_cpu
from vivisect.lib.bits import *

class CpuTest(unittest.TestCase):

    def test_cpu_mmaps(self):
        mmaps = [ tufo(0x41420000, size=4096) ]
        cpu = v_cpu.Cpu(mmaps=mmaps)
        self.assertIsNotNone( cpu.mmap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420004], h2b('0000') )

    def test_cpu_addbytes(self):
        mmaps = [ tufo(0x41420000, init=h2b('5656565641414141')) ]
        cpu = v_cpu.Cpu(mmaps=mmaps)
        self.assertIsNotNone( cpu.mmap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420006], h2b('56564141') )

    def test_cpu_snaprest(self):
        mmaps = [ tufo(0x41410000, init=b'A' * 4096) ]
        cpu = v_cpu.getArchCpu('i386',mmaps=mmaps)

        cpu['cl'] = 30
        cpu['bx'] = 40
        cpu['eax'] = 50

        snap = cpu.snapshot()

        cpu['cl'] =  0
        cpu['bx'] =  0
        cpu['eax'] = 0

        #cpu = v_cpu.getArchCpu('i386')
        cpu.restore(snap)

        self.assertEqual( cpu.cl, 30 )
        self.assertEqual( cpu.bx, 40 )
        self.assertEqual( cpu.eax, 50 )
        self.assertEqual( cpu[0x41410010:0x41410020], b'A' * 16)

    def test_cpu_terse_mem(self):
        mmaps = [ tufo(0x41410000, size=4096, perm=7) ]
        cpu = v_cpu.getArchCpu('i386',mmaps=mmaps)
        cpu[0x41410000:] = b'VVVV'

        self.assertEqual( cpu.peek(0x41410000, 4), b'VVVV')
        self.assertEqual( cpu[0x41410000:0x41410004], b'VVVV')

    def test_cpu_terse_regs(self):
        cpu = v_cpu.getArchCpu('i386')

        cpu['eax'] = 0x41414141
        cpu['ax']  = 0x4242
        cpu['al']  = 0x43

        self.assertEqual( cpu.reg('eax'), 0x41414243 )

    def test_cpu_thread_regs(self):
        cpu = v_cpu.getArchCpu('i386',threads=2)
        cpu.switch(0)
        cpu['eax'] = 0x41414141

        cpu.switch(1)
        self.assertEqual( cpu.eax, 0 )

        cpu.switch(0)
        self.assertEqual( cpu.eax, 0x41414141 )

    def test_cpu_thread_valid(self):
        cpu = v_cpu.getArchCpu('i386')
        self.assertRaises( v_cpu.InvalidThread, cpu.switch, 99 )

