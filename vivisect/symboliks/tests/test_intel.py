import unittest

import vivisect.symboliks.archs.i386 as i386sym
import vivisect.symboliks.analysis as v_s_analysis

from vivisect.symboliks.common import Var, Const, cnot
from vivisect.symboliks.effects import ConstrainPath

import vivisect.tests.helpers as helpers


class IntelSymTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i386_vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')

    def test_constraints(self):
        fva = 0x080509e0
        vw = self.i386_vw
        ctx = v_s_analysis.getSymbolikAnalysisContext(vw, consolve=True)
        g = ctx.getSymbolikGraph(fva)
        constraints = {
            0x080509e0: {
                0x8050a42: ConstrainPath(0x080509ef, Const(0x08050a42, 4), Var("eflags_eq", width=4)),
                0x80509f1: ConstrainPath(0x080509ef, Const(0x080509f1, 4), cnot(Var("eflags_eq", width=4))),
            },

            0x8050a20: {
                0x8050a26: ConstrainPath(0x08050a24, Const(0x08050a26, 4), cnot(Var("eflags_eq", width=4))),
                0x8050a42: ConstrainPath(0x08050a24, Const(0x08050a42, 4), Var("eflags_eq", width=4)),
            },
            0x8050a26: {
                0x8050a20: ConstrainPath(0x08050a3e, Const(0x08050a20, 4), cnot(Var("eflags_eq", width=4))),
                0x8050a40: ConstrainPath(0x08050a3e, Const(0x08050a40, 4), cnot(cnot(Var("eflags_eq", width=4)))),
            },

            0x80509f1: {
                0x8050a44: ConstrainPath(0x08050a0c, Const(0x08050a44, 4), Var("eflags_eq", width=4)),
                0x8050a0e: ConstrainPath(0x08050a0c, Const(0x08050a0e, 4), cnot(Var("eflags_eq", width=4)))
            },
        }

        for eid, xfrom, xto, props in g.getEdges():
            if xfrom not in constraints:
                self.assertEqual(0, len(props))
                continue
            self.assertTrue('symbolik_constraints' in props)
            self.assertEqual(1, len(props['symbolik_constraints']))
            pcon = props['symbolik_constraints'][0]
            self.assertEqual(pcon, constraints[xfrom][xto])

    def test_emulator(self):
        fva = 0x08051e10
        vw = self.i386_vw
        ctx = v_s_analysis.getSymbolikAnalysisContext(vw, consolve=True)

        retn = [
            '((mem[(arg0 + 24):4](edx,mem[(arg0 + 8):4],mem[0xbfbfefec:4],mem[0xbfbfeff0:4]) * 8) + mem[arg0:4])',
            '0x08049a80()',
        ]

        esps = [
            Const(0xbfbfeff4, 4),
            Const(0xbfbff004, 4),
        ]
        for emu, effects in ctx.walkSymbolikPaths(fva):
            self.assertTrue(str(emu.getFunctionReturn().reduce(foo=True)) in retn)
            esp = emu.getSymVariable('esp').reduce(foo=True)
            self.assertTrue(esp in esps)
            self.assertEqual(emu.getSymVariable('ecx'), Var('arg0', 4))

    def _cconv_test(self, caller, callee, argc, retn):
        # some setup and other fun things
        vw = self.i386_vw

        # Note: The function itself isn't important, we just need a real Symbolik emulator
        # instance that we can pass to setSymbolikArgs so that we can monkey with things
        # from there
        fva = 0x08051e10
        ctx = v_s_analysis.getSymbolikAnalysisContext(vw, consolve=True)
        argv = [Var('arg%d' % i, 4) for i in range(argc)]
        emu = ctx.getFuncEmu(fva)
        callee.setSymbolikArgs(emu, argv)
        caller.setSymbolikArgs(emu, argv)
        emu.setSymVariable('eax', retn)

        self.assertEqual(caller.getSymbolikReturn(emu), retn)
        self.assertEqual(caller.getSymbolikReturn(emu), callee.getSymbolikReturn(emu))

        # if the callee cleans it up, the stack point is automatically assumed to be
        # delta'd by 20 bytes for bfastcall (argc == 7, 3 are registers, so 4 stack args
        # plus the return address makes 5 dwords to clean up for 20 bytes
        bytes_cleaned = (1 + callee.getNumStackArgs(emu, argc)) * 4
        self.assertEqual(callee.deallocateCallSpace(emu, argc).reduce(), Const(bytes_cleaned, 4))
        # if the caller cleans things up, the instructions after are going to do it
        # (since we're currently looking at things from a precall perspective), and so
        # the only thing that is going to get cleaned up is the return address
        self.assertEqual(caller.deallocateCallSpace(emu, argc).reduce(), Const(4, 4))

    def test_ccconv_diff(self):
        # msfastcall
        # thiscall
        # bfastcall
        retval = Const(0xdeadbeef, 4)
        self._cconv_test(i386sym.BFastCall_Caller(), i386sym.BFastCall(), 9, retval)
        self._cconv_test(i386sym.ThisCall_Caller(), i386sym.ThisCall(), 27, retval)
        self._cconv_test(i386sym.MsFastCall_Caller(), i386sym.MsFastCall(), 1, retval)
