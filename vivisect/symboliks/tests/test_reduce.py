import unittest

from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp

class TestReduceCase(unittest.TestCase):
    '''
    tests basic algebraic reductions
    '''
    def assertReduce(self, s1, s2):
        sym1 = symexp(s1).reduce(foo=True)
        sym2 = symexp(s2)
        self.assertEqual(str(sym1), str(sym2))

    def assertNotReduce(self, s1, s2):
        sym1 = symexp(s1).reduce()
        sym2 = symexp(s2)
        self.assertNotEqual(str(sym1), str(sym2))

    def test_symboliks_reduce_and_consts(self):
        self.assertReduce('255 & 255', '255')
        self.assertReduce('0xff & 0xf0', '0xf0')

    def test_symboliks_reduce_op_and(self):
        self.assertReduce('(foo & 0xff) & 0xff', 'foo & 0xff')
        self.assertReduce('(0xff & foo) & 0xff', 'foo & 0xff')
        self.assertReduce('0xff & (foo & 0xff)', 'foo & 0xff')
        self.assertReduce('0xff & (0xff & foo)', 'foo & 0xff')

        self.assertReduce('foo & 0', '0')
        self.assertReduce('0 & foo', '0')

        # reduce & with 0 regardless of width
        self.assertReduce('foo[5] & 0', '0')
        # we only support slices on memory
        # self.assertReduce('foo[2:4] & 0', '0')
        self.assertReduce('mem[2:4] & 0', '0')
        self.assertReduce('0[1] & foo', '0')

        # reduce & umax of foo to just foo
        self.assertReduce('foo[1] & 0xff', 'foo')
        self.assertReduce('foo[2] & 0xffff', 'foo')
        self.assertReduce('foo[4] & 0xffffffff', 'foo')

        self.assertNotReduce('foo[4] & 0xff', 'foo')
        self.assertNotReduce('foo[4] & 0xffff', 'foo')

    def test_symboliks_reduce_op_xor(self):
        self.assertReduce('foo ^ foo', '0')
        self.assertReduce('foo ^ 0', 'foo')

    def test_symboliks_reduce_op_mul(self):
        self.assertReduce('foo * 0', '0')
        self.assertReduce('foo * 1', 'foo')
        self.assertReduce('(foo * 10) / 2', 'foo * 5')
        self.assertReduce('(foo * 10) * 2', 'foo * 20')

    @unittest.skip('Need to implement more reducers')
    def test_symboliks_reduce_op_divmul(self):
        self.assertReduce('(foo / 2) * 2', 'foo')
        self.assertReduce('(foo / 2) * 10', 'foo * 5')

    def test_symboliks_reduce_op_div(self):
        self.assertReduce('0 / foo', '0')
        self.assertReduce('foo / foo', '1')

    def test_symboliks_reduce_op_rshift(self):
        self.assertReduce('0 >> foo', '0')
        self.assertReduce('foo >> 0', 'foo')
        self.assertReduce('3 >> 1', '1')
        self.assertReduce('5347 >> 6', '83')

    def test_symboliks_reduce_op_lshift(self):
        self.assertReduce('0 << foo', '0')
        self.assertReduce('foo << 0', 'foo')
        self.assertReduce('2 << 2', '8')
        self.assertReduce('7 << 2', '28')
        self.assertReduce('1 << 2', '4')

    def test_symboliks_reduce_op_pow(self):
        self.assertReduce('0 ** foo', '0')
        self.assertReduce('1 ** foo', '1')
        self.assertReduce('foo ** 0', '1')

    def test_symboliks_reduce_op_addsub(self):
        self.assertReduce('(foo + 255) + 10', 'foo + 265')
        self.assertReduce('(255 + foo) + 10', 'foo + 265')
        self.assertReduce('(255 + foo) + 10', 'foo + 265')
        self.assertReduce('(foo - 10) + 255', 'foo + 245')
        self.assertReduce('(255 - foo) + 10', '(0 - foo) + 265')
        self.assertReduce('(foo + 255) - 10', 'foo + 245')
        self.assertReduce('(foo - 255) - 10', 'foo - 265')
        self.assertReduce('255 - (foo - 10)', '265 - foo')
        self.assertReduce('255 - (foo + 10)', '245 - foo')
        self.assertReduce('255 - (10 - foo)', 'foo + 245')
        self.assertReduce('(foo + 255) + (bar + 10)', '(foo + bar) + 265')
        self.assertReduce('(foo - 10) + (bar + 255)', '(bar + foo) + 245')
        self.assertReduce('(foo - 255) + (bar - 10)', '(foo + bar) - 265')
        self.assertReduce('20 - (10 - eax)', 'eax + 10')
        self.assertReduce('(foo + 255) - (bar + 10)', '(foo - bar) + 245')
        self.assertReduce('(foo + 255) - (10 + bar)', '(foo - bar) + 245')
        self.assertReduce('(foo + 255) + (bar - 10)', '(foo + bar) + 245')
        self.assertReduce('(foo + 255) + (10 - bar)', '(foo - bar) + 265')
        self.assertReduce('(foo - 255) - (bar + 10)', '(foo - bar) - 265')
        self.assertReduce('(255 - foo) - (bar + 10)', '(( 0 - foo ) - bar) + 245')
        self.assertReduce('(foo + 255) - (bar - 10)', '(foo - bar) + 265')
        self.assertReduce('(foo - 255) - (bar - 275)', '(foo - bar) + 20')
        self.assertReduce('foo + 0', 'foo')
        self.assertReduce('0 + foo', 'foo')
        self.assertReduce('0 + 0', '0')
        self.assertReduce('2 + 2', '4')
        self.assertReduce('2 - 2', '0')
        self.assertReduce('foo + (0 - bar)', 'foo - bar')
        self.assertReduce('foo + (0 + bar)', 'foo + bar')
        self.assertReduce('foo - (0 + bar)', 'foo - bar')
        # TODO: More generic ast reducer
        # self.assertReduce('(foo + bar) - (bar + baz)', 'foo - baz')
        self.assertReduce('0 - (0 - foo)', 'foo')
        self.assertReduce('0 + (0 + foo)', 'foo')
        self.assertReduce('0 - (0 + foo)', '0 - foo')

    def test_symboliks_reduce_varsub(self):
        esp = Var('esp', width=4)
        for i in range(100):
            esp -= Const(4, width=4)
        self.assertEqual(str(esp.reduce()), '(esp - 400)')

    def test_symboliks_reduce_funcargs_multipass(self):
        op = (Const(0x1000, 8) - Const(0xb90, 8)) - Const(0x60, 8)
        arg = (Mem(Const(0x14000, 8), Const(8, 8)) ^ op) ^ op
        expr = Call(Const(0x400, 8), Const(8, 8), argsyms=[arg,])

        expr = expr.reduce()
        self.assertEqual(str(expr), '1024(mem[0x00014000:8])')

        op = (Const(0x1000, 8) - Const(0xb90, 8)) - Const(0x60, 8)
        arg = (Mem(Const(0x14000, 8), Const(8, 8)) ^ op) ^ op
        expr = Call(Const(0x400, 8), Const(8, 8), argsyms=[arg,])
        expr = expr.reduce(foo=True)
        self.assertEqual(str(expr), '1024(mem[0x00014000:8])')
