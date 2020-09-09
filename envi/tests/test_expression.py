import unittest

import envi.expression as e_expr

import vivisect
import vivisect.cli

class EnviExpressionTest(unittest.TestCase):

    def test_viv_parseExpression(self):
        vw = vivisect.cli.VivCli()
        vw.makeName(0xfffffffe, 'foo(bar)')

        self.assertEqual(vw.parseExpression('foo(bar) + 5'), 0x100000003)

    def test_envi_MemoryExpressionLocals(self):
        vw = vivisect.cli.VivCli()
        vw.makeName(0xfffffffe, 'foo(bar)')

        mel = e_expr.MemoryExpressionLocals(vw, symobj=vw)
        self.assertEqual(mel.sym('foo(bar)'), 4294967294)

    def test_envi_expr_evaluate(self):
        x={'foo(bar)': 0x40, 'foo':0x60}

        self.assertEqual(e_expr.evaluate('foo(bar) + 1', x), 65)
        self.assertEqual(e_expr.evaluate('foo + 1', x), 97)
        self.assertEqual(e_expr.evaluate('32 + 1', x), 33)
