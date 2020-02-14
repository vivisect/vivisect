import unittest

import envi.memory as e_mem

import vivisect as viv
import vivisect.const as viv_const
import vivisect.symboliks.common as vsc
import vivisect.symboliks.archind as vsym_archind
import vivisect.symboliks.analysis as vsym_analysis


class TestArchind(unittest.TestCase):

    def test_wipeAstArch(self):
        vw = viv.VivWorkspace()
        vw.addMemoryMap(0x00, e_mem.MM_RWX, 'code', [0 for x in range(256)])
        vw.addLocation(0x40, 47, viv_const.LOC_POINTER)
        vw.setMeta('Architecture', 'i386')
        symctx = vsym_analysis.SymbolikAnalysisContext(vw)

        func = vsc.Var('eax', 4)
        call = vsc.Call(func, 4)
        addr = vsc.Var('arg0', 4) + call
        mem = vsc.Mem(addr, vsc.Const(4, 4))

        op = mem + vsc.Var('edx', 4)
        final = op * vsc.Var('edx', 4)
        wiped = vsym_archind.wipeAstArch(symctx, [final])
        self.assertEquals(1, len(wiped))
        self.assertEquals('((mem[(arg0 + 1indreg()):4] + 0indreg) * 0indreg)', str(wiped[0]))

    def test_wipeAstArch_wipeva(self):
        vw = viv.VivWorkspace()
        vw.addMemoryMap(0x410000, e_mem.MM_RWX, 'code', [0 for x in range(0xFFFF)])
        vw.addLocation(0x41b2ac, 47, viv_const.LOC_POINTER)
        vw.addLocation(0x4149b3, 28, viv_const.LOC_POINTER)
        vw.addLocation(0x41ac93, 83, viv_const.LOC_POINTER)
        vw.setMeta('Architecture', 'i386')
        symctx = vsym_analysis.SymbolikAnalysisContext(vw)

        cons = vsc.Const(0x41b2ac, 4)
        func1 = vsc.Call(cons, 4, argsyms=[vsc.Var('edx', 4)])
        func2 = vsc.Call(vsc.Const(0x4149b3, 4), 4, argsyms=[vsc.Const(0, 4), vsc.Const(1, 4), vsc.Const(0x41b2ac, 4)])
        func3 = vsc.Call(vsc.Const(0x41ac93, 4), 4, argsyms=[vsc.Const(0, 4), vsc.Var('ecx', 4)])
        wiped = vsym_archind.wipeAstArch(symctx, [func1 + func2, func3], wipeva=True)
        self.assertEquals(2, len(wiped))
        self.assertEquals('(2archindva(1indreg) + 1archindva(0,1,2archindva))', str(wiped[0]))
        self.assertEquals('0archindva(0,0indreg)', str(wiped[1]))
