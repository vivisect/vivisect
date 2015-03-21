import unittest

import vivisect.hal.cpu as v_cpu
from vivisect.lib.bits import *

class CpuTest(unittest.TestCase):

    def test_cpu_addmap(self):
        cpu = v_cpu.Cpu(addmap=(0x41420000,7,4096))
        self.assertIsNotNone( cpu.getMemoryMap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420004], h2b('0000') )

    def test_cpu_addbytes(self):
        cpu = v_cpu.Cpu(addbytes=(0x41420000,7,h2b('5656565641414141')))
        self.assertIsNotNone( cpu.getMemoryMap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420006], h2b('56564141') )

    def test_cpu_snaprest(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.addMemoryMap(0x41410000,7,'',b'A' * 4096)
        cpu['cl'] = 30
        cpu['bx'] = 40
        cpu['eax'] = 50

        snap = cpu.snapshot()

        cpu = v_cpu.getArchCpu('i386')
        cpu.restore(snap)

        self.assertEqual( cpu.cl, 30 )
        self.assertEqual( cpu.bx, 40 )
        self.assertEqual( cpu.eax, 50 )
        self.assertEqual( cpu[0x41410010:0x41410020], b'A' * 16)

    def test_cpu_terse_mem(self):
        cpu = v_cpu.getArchCpu('i386',addmap=(0x41410000,7,4096))
        cpu[0x41410000:] = b'VVVV'

        self.assertEqual( cpu.readMemory(0x41410000, 4), b'VVVV')
        self.assertEqual( cpu[0x41410000:0x41410004], b'VVVV')

    def test_cpu_terse_regs(self):
        cpu = v_cpu.getArchCpu('i386')

        cpu['eax'] = 0x41414141
        cpu['ax']  = 0x4242
        cpu['al']  = 0x43

        self.assertEqual( cpu.get('eax'), 0x41414243 )

    def test_cpu_thread_regs(self):
        cpu = v_cpu.getArchCpu('i386',threads=2)
        cpu.setThread(0)
        cpu['eax'] = 0x41414141

        cpu.setThread(1)
        self.assertEqual( cpu.eax, 0 )

        cpu.setThread(0)
        self.assertEqual( cpu.eax, 0x41414141 )

    def test_cpu_thread_valid(self):
        cpu = v_cpu.getArchCpu('i386')
        self.assertRaises( v_cpu.InvalidThread, cpu.setThread, 99 )

