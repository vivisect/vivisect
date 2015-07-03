import unittest

from vertex.lib.common import tufo

import vivisect.hal.cpu as v_cpu
import vivisect.hal.memory as v_mem

from vivisect.lib.bits import *

class CpuTest(unittest.TestCase):

    def test_cpu_mmaps(self):
        cpu = v_cpu.Cpu()
        cpu.initMemoryMap(0x41420000,4096)
        self.assertIsNotNone( cpu.getMemoryMap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420004], h2b('0000') )

    def test_cpu_addbytes(self):
        cpu = v_cpu.Cpu()
        cpu.initMemoryMap(0x41420000, 4096, init=h2b('5656565641414141'))
        self.assertIsNotNone( cpu.getMemoryMap(0x41420001) )
        self.assertEqual( cpu[0x41420002:0x41420006], h2b('56564141') )

    def test_cpu_snaprest(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.initMemoryMap(0x41410000, 4096, init=b'A'*4096)

        cpu['cl'] = 30
        cpu['bx'] = 40
        cpu['eax'] = 50

        snap = cpu.getCpuSnap()

        cpu['cl'] =  0
        cpu['bx'] =  0
        cpu['eax'] = 0

        cpu.setCpuSnap(snap)

        self.assertEqual( cpu.cl, 30 )
        self.assertEqual( cpu.bx, 40 )
        self.assertEqual( cpu.eax, 50 )
        self.assertEqual( cpu[0x41410010:0x41410020], b'A' * 16)

    def test_cpu_terse_mem(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.initMemoryMap(0x41410000, 4096)
        cpu[0x41410000:] = b'VVVV'

        self.assertEqual( cpu.readMemory(0x41410000, 4), b'VVVV')
        self.assertEqual( cpu[0x41410000:0x41410004], b'VVVV')

    def test_cpu_terse_regs(self):
        cpu = v_cpu.getArchCpu('i386')

        cpu['eax'] = 0x41414141
        cpu['ax']  = 0x4242
        cpu['al']  = 0x43

        self.assertEqual( cpu.getReg('eax'), 0x41414243 )

    def test_cpu_thread_regs(self):
        cpu = v_cpu.getArchCpu('i386',threads=2)
        cpu.switchThread(0)
        cpu['eax'] = 0x41414141

        cpu.switchThread(1)
        self.assertEqual( cpu.eax, 0 )

        cpu.switchThread(0)
        self.assertEqual( cpu.eax, 0x41414141 )

    def test_cpu_thread_valid(self):
        cpu = v_cpu.getArchCpu('i386')
        self.assertRaises( v_cpu.InvalidThread, cpu.switchThread, 99 )


    def test_cpu_lib_load_free(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu._initLib( tufo(0x41410000, name='woot', path='/foo/bar/baz') )


        self.assertEqual( len( cpu.libs() ), 1 )
        self.assertIsNotNone( cpu.getLibByName('woot') )

        cpu._finiLib( cpu.getLibByName('woot') )

        self.assertIsNone( cpu.getLibByName('woot') )

    def test_cpu_lib_defaults(self):
        cpu = v_cpu.getArchCpu('i386')
        lib = cpu._initLib( tufo(0x41410000, name='woot', path='/foo/bar/baz') )

        self.assertEqual( lib[1].get('parsed'), False )

    def test_cpu_eval_reg(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.setReg('eax', 20)
        cpu.setReg('ebx', 30)

        self.assertEqual( cpu.eval('eax'), 20 )
        self.assertEqual( cpu.eval('ebx'), 30 )
        self.assertEqual( cpu.eval('eax + ebx'), 50 )

    def test_cpu_setregskw(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.setRegsKw(eax=20,ebx=30)
        self.assertEqual( cpu.getReg('eax'), 20 )
        self.assertEqual( cpu.getReg('ebx'), 30 )

    def test_cpu_eval_lib(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu._initLib( tufo(0x41410000, name='woot', path='/foo/bar/baz') )

        self.assertEqual( cpu.eval('woot'), 0x41410000 )
        self.assertEqual( cpu.eval('woot + 0x20'), 0x41410020 )

    def test_cpu_eval_meth(self):
        cpu = v_cpu.getArchCpu('i386')
        cpu.setReg('eax', 20)

        self.assertEqual( cpu.eval('eax + 20'), 40 )

    def test_cpu_eval_nosuch(self):
        cpu = v_cpu.getArchCpu('i386')
        self.assertIsNone( cpu.eval('yermom') )

    def test_cpu_print(self):
        cpu = v_cpu.getArchCpu('i386')
        data ={}
        def doprint(event):
            data['msg'] = event[1].get('msg')

        cpu.on('cpu:print', doprint)
        cpu.print('hehe')


        self.assertEqual( data.get('msg'), 'hehe' )

    def test_cpu_error(self):
        cpu = v_cpu.getArchCpu('i386')
        data ={}
        def doerror(event):
            data['msg'] = event[1].get('msg')

        cpu.on('cpu:error', doerror)
        cpu.error('hehe')

        self.assertEqual( data.get('msg'), 'hehe' )

