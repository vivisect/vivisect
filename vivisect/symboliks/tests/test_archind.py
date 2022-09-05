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
        self.assertEqual(1, len(wiped))
        self.assertEqual('((mem[(arg0 + 1indreg()):4] + 0indreg) * 0indreg)', str(wiped[0]))

    def test_wipeAstArch_wipeva(self):
        vw = viv.VivWorkspace()
        vw.addMemoryMap(0x410000, e_mem.MM_RWX, 'code', [0 for x in range(0x10000)])
        vw.addLocation(0x41b2ac, 47, viv_const.LOC_POINTER)
        vw.addLocation(0x4149b3, 28, viv_const.LOC_POINTER)
        vw.addLocation(0x41ac93, 83, viv_const.LOC_POINTER)
        vw.setMeta('Architecture', 'i386')
        symctx = vsym_analysis.SymbolikAnalysisContext(vw)

        cons = vsc.Const(0x41b2ac, 4)
        func1 = vsc.Call(cons, 4, argsyms=[vsc.Var('edx', 4)])
        func2 = vsc.Call(vsc.Const(0x4149b3, 4), 4, argsyms=[
                         vsc.Const(0, 4), vsc.Const(1, 4), vsc.Const(0x41b2ac, 4)])
        func3 = vsc.Call(vsc.Const(0x41ac93, 4), 4, argsyms=[
                         vsc.Const(0, 4), vsc.Var('ecx', 4)])
        wiped = vsym_archind.wipeAstArch(symctx, [func1 + func2, func3], wipeva=True)
        self.assertEqual(2, len(wiped))
        self.assertEqual('(2archindva(1indreg) + 1archindva(0,1,2archindva))', str(wiped[0]))
        self.assertEqual('0archindva(0,0indreg)', str(wiped[1]))

    def test_basic(self):
        vw = viv.VivWorkspace()
        vw.addMemoryMap(0x56560000, 7, 'woot', b'A'*8192)
        vw.setMeta('Architecture', 'i386')
        symctx = vsym_analysis.getSymbolikAnalysisContext(vw)

        base = vsc.Mem(vsc.Const(0x56560020,4),vsc.Const(4,4)) - (vsc.Var('arg0',4) + vsc.Var('ecx',4) ) * ( vsc.Var('ebx',4) + vsc.Var('ebx',4) ) + vsc.Const(9999,4)
        eqs = [
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ebx', 4)) * (vsc.Var('ecx', 4) + vsc.Var('ecx', 4)) + vsc.Const(9999, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('eax', 4) + vsc.Var('eax', 4)) * (vsc.Var('edx', 4) + vsc.Var('arg0', 4)) + vsc.Const(9999, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ecx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ebx', 4)) + vsc.Const(9999, 4),
            vsc.Mem(vsc.Const(0x56560056, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ecx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ebx', 4)) + vsc.Const(9999, 4),
        ]

        nes = [
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ebx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ecx', 4)) + vsc.Const(9999, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('eax', 4)  + vsc.Var('arg1', 4)) *(vsc.Var('edx', 4) + vsc.Var('arg0', 4))+ vsc.Const(9999, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ecx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ebx', 4)) + vsc.Const(8888, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ecx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ebx', 4)) + vsc.Const(0x56560020, 4),
            vsc.Mem(vsc.Const(0x56560020, 4), vsc.Const(4, 4)) - (vsc.Var('arg0', 4) + vsc.Var('ecx', 4)) * (vsc.Var('ebx', 4) + vsc.Var('ebx', 4)) + vsc.Const(0x56560040, 4),
        ]

        post_eqs = [
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 0x0000270f)',
            '((mem[0archindva:4] - ((1indreg + 1indreg) * (0indreg + arg0))) + 0x0000270f)',
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 0x0000270f)',
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 0x0000270f)',
        ]

        post_nes = [
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (0indreg + 1indreg))) + 0x0000270f)',
            '((mem[0archindva:4] - ((1indreg + arg1) * (0indreg + arg0))) + 0x0000270f)',
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 0x000022b8)',
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 0archindva)',
            '((mem[0archindva:4] - ((arg0 + 0indreg) * (1indreg + 1indreg))) + 1archindva)',
        ]

        for i in range(len(post_eqs)):
            eq = vsym_archind.wipeAstArch(symctx, [eqs[i]], wipeva=True)[0]
            self.assertEqual(post_eqs[i], str(eq))

        for i in range(len(post_nes)):
            ne = vsym_archind.wipeAstArch(symctx, [nes[i]], wipeva=True)[0]
            self.assertEqual(post_nes[i], str(ne))

        base = vsym_archind.wipeAstArch(symctx, [base, ], wipeva=True)[0]
        baseval = base.solve(emu=None)
        for match in eqs:
            self.assertEqual(match.solve(emu=None), baseval)

        for nonmatch in nes:
            self.assertNotEqual(nonmatch.solve(emu=None), baseval)
