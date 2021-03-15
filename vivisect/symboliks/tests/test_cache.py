import unittest

from vivisect.const import *
from vivisect.symboliks.common import *
from vivisect.symboliks.expression import symexp

class TestSymbolikCache(unittest.TestCase):
    '''
    tests the reduction of asts consisting of add's and sub's if widths are
    the same.
    '''
    def test_symboliks_cache_solve_vars(self):
        s = symexp('x + 20')

        self.assertEqual(s.solve(vals={'x':10}), 30)
        self.assertEqual(s.solve(vals={'x':20}), 40)

        self.assertIsNone(s.cache.get('solve'))
        s.solve()
        self.assertIsNotNone(s.cache.get('solve'))

    def test_symboliks_cache_walktree(self):

        s = symexp('x + 30')

        solved1 = s.solve()

        self.assertIsNotNone(s.cache.get('solve'))

        def swapx(path,sym,ctx):
            if sym.symtype == SYMT_VAR and sym.name == 'x':
                return Var('y',4)

        s = s.walkTree(swapx)

        # check the partial cache clear
        self.assertIsNone(s.cache.get('solve'))
        self.assertIsNone(s.kids[0].cache.get('solve'))
        self.assertIsNotNone(s.kids[1].cache.get('solve'))

        solved2 = s.solve()
        self.assertEqual(str(s), '(y + 30)')

        self.assertNotEqual(solved1, solved2)

        # be *really* mean and manually slice a kid
        # then confirm that the cache still hits..
        s.kids[0] = Var('x', 4)
        self.assertEqual(s.solve(), solved2)
