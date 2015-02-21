import unittest

import vivisect.hal.cpu as v_cpu
import vivisect.symboliks.symstate as v_symstate

class SymStateTest(unittest.TestCase):

    def test_symstate_builder(self):
        cpu = v_cpu.getArchCpu('i386')
        sym = cpu.getSymBuilder()

        sym['eax'] = sym.eax + sym.ax

    def test_symstate_bits(self):
        cpu = v_cpu.getArchCpu('i386')
        sym = cpu.getSymBuilder()

        self.assertEqual( sym.al.bits(), 8 )
        self.assertEqual( sym.ax.bits(), 16 )
        self.assertEqual( sym.eax.bits(), 32 )

    def test_symstate_value(self):
        cpu = v_cpu.getArchCpu('i386')
        sym = cpu.getSymBuilder()

        cpu['eax'] = 30
        cpu['ebx'] = 30

        self.assertTrue( ((sym.eax + sym.ebx).cast(32) == 60).value() )
        self.assertEqual( (sym.eax + sym.ebx).cast(32).value(), 60 )

    def test_symstate_cache(self):
        cpu = v_cpu.getArchCpu('i386')
        sym = cpu.getSymBuilder()

        cpu['eax'] = 10
        cpu['ebx'] = 20

        # a little invasive, but we dont need an API for checking
        # the cache if it happens transparently...

        eax = sym.eax
        self.assertEqual( eax.value(), 10 )

        sid = eax.state[3]['sid']
        self.assertEqual( cpu.symcache.get(sid), 10 )

        # set reg should clear cache..
        cpu['eax'] = 99 # red baloons...

        self.assertIsNone( cpu.symcache.get(sid) )
        self.assertEqual( eax.value(), 99 )
        self.assertEqual( cpu.symcache.get(sid), 99 )

    def test_symstate_str(self):
        cpu = v_cpu.getArchCpu('i386')
        sym = cpu.getSymBuilder()

        self.assertEqual( str((sym.eax + sym.ecx) * 30), '((eax + ecx) * 30)')


    #def test_symstate_effects_basic(self):
        #cpu = v_cpu.getArchCpu('i386')
        #sym = cpu.getSymBuilder()

        # assert raises

        #sym['eax'] = ( sym.ebx + 30 )
        #sym[ sym[sym.esp:4] ] = sym.esi + sym[

        #eax = eax + 2
        #esp -= 32
        #mem[esp:4] = 

