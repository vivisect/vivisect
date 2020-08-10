import unittest

from vivisect.symboliks.common import Var, Const, cnot
from vivisect.symboliks.effects import ConstrainPath
import vivisect.symboliks.analysis as v_s_analysis

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
