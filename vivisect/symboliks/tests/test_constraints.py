import unittest

from vivisect.tests.helpers import MockVw

from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp
from vivisect.symboliks.tests.helpers import MockEmulator


class TestConstraints(unittest.TestCase):
    '''
    Tests that symbolik constraints work the way we think
    '''
    def assertTruth(self, s1):
        v1 = symexp(s1).solve()
        self.assertTrue(v1 == 1)

    def assertReduce(self, s1, s2):
        sym1 = symexp(s1).reduce()
        sym2 = symexp(s2)
        self.assertEqual(str(sym1), str(sym2))

    def test_const(self):
        self.assertTruth('0 < 1')
        self.assertTruth('0xab == 0xab')
        self.assertTruth('0xf00 > 0xabc')
        self.assertTruth('10 >= 9')
        self.assertTruth('9 <= 9')
        self.assertTruth('4 != 5')

    def test_op(self):
        self.assertTruth('foo == foo')

    def test_reduce(self):
        s1 = '((0 & ((foo * 4) >> 2)) == 0)'
        v1 = symexp('((0 & ((foo * 4) >> 2)) == 0)')
        self.assertTrue(s1 == str(v1))
        self.assertReduce(s1, '1')
        self.assertTrue(v1.getWidth() == 4)  # default width

        s2 = '((((foo * bar) * baz) + (131 | 40)) == (((foo * bar) * baz) + 171))'
        v2 = symexp(s2)
        self.assertTrue(s2 == str(v2))
        self.assertReduce(s2, '(((foo * bar) * baz) + 171) == (((foo * bar) * baz) + 171)')
        self.assertTrue(v2.getWidth() == 4)  # default width

        s2 = '(((((foo - bar) + bar) + (131 | 40)) - 171) == foo)'
        v2 = symexp(s2)
        self.assertTrue(s2 == str(v2))
        self.assertReduce(s2, 'foo == foo')
        self.assertTrue(v2.getWidth() == 4)  # default width

    def test_rev(self):
        v1 = symexp('4 < 5')
        v2 = symexp('4 >= 5')
        self.assertTrue(v1.isDiscrete())
        self.assertTrue(v2.isDiscrete())
        self.assertTrue(str(v1.reverse()) == str(v2))

        v1 = symexp('foo > bar')
        v2 = symexp('foo <= bar')
        self.assertFalse(v1.isDiscrete())
        self.assertFalse(v2.isDiscrete())
        self.assertTrue(str(v1.reverse()) == str(v2))

        v1 = symexp('foo == bar')
        v2 = symexp('foo > bar')
        self.assertFalse(v1.isDiscrete())
        self.assertFalse(v2.isDiscrete())
        self.assertFalse(str(v1.reverse()) == str(v2))

    def test_eq(self):
        v1 = symexp('10 != 5')
        v2 = symexp('2 * 5 != 3 + 2')
        self.assertTrue(v1 == v2)

        v1 = symexp('foo < bar')
        v2 = symexp('bar >= foo')
        self.assertTrue(v1 == v2)

    def test_walktree(self):
        v1 = symexp('((foo ** 2) << 1) + (bar * 3) - 4 > 0')

        def walker(path, kid, ctx):
            order.append(kid)
        order = []
        v1.walkTree(walker, ctx=order)
        correct = ['foo',
                   '2',
                   '(foo ** 2)',
                   '1',
                   '((foo ** 2) << 1)',
                   'bar',
                   '3',
                   '(bar * 3)',
                   '(((foo ** 2) << 1) + (bar * 3))',
                   '4',
                   '((((foo ** 2) << 1) + (bar * 3)) - 4)',
                   '0',
                   '(((((foo ** 2) << 1) + (bar * 3)) - 4) > 0)']
        if len(order) != len(correct):
            self.fail('test_walktree, visit produced unexpected results')

        for i in xrange(len(order)):
            self.assertTrue(str(order[i]) == correct[i])

    def test_update(self):
        v1 = symexp('foo * bar > bar << baz')
        self.assertFalse(v1.isDiscrete())
        emu = MockEmulator(MockVw())
        emu.setSymVariable('foo', Const(5, emu.__width__))
        emu.setSymVariable('bar', Const(2, emu.__width__))
        emu.setSymVariable('baz', Const(6, emu.__width__))
        v1 = v1.update(emu)
        self.assertTrue(v1.isDiscrete(emu))
        self.assertTrue(v1.solve(emu) == 0)

    def test_mixed(self):
        v1 = symexp('(foo ** 2) << (1 > 0)')
        emu = MockEmulator(MockVw())
        emu.setSymVariable('foo', Const(5, emu.__width__))
        v1 = v1.update(emu).reduce()
        self.assertTrue(v1.value == 50)
