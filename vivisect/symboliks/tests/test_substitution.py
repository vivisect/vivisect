import unittest

import vivisect.symboliks.common as vsc
import vivisect.symboliks.substitution as vss


class TestSubstitution(unittest.TestCase):
    '''
    symobj = (Var('x',4) * Const(3, 4) ) + Var('y',4)
    print(str(symobj))

    x = srange('x', 3)
    y = sset('y', [1,9,0xffffffff])

    for i in (x+y):
        print('solved: %s %d' % (repr(i),symobj.solve(vals=i),))

    for i in (x*y):
        print('solved: %s %d' % (repr(i),symobj.solve(vals=i),))
    '''
    def test_basic_substitution(self):
        symobj = vsc.Var('x', 4) + vsc.Const(3,4) + vsc.Var('y', 4)
        x = vss.srange('x', 4)
        y = vss.sset('y', [1, 2, 4, 7, 99])

        #addAnswers = []
        # TODO: The nature of AddSubState feels completely wrong
        # also, x+y and y+x produce *very* different results that don't really line up
        #for idx, vals in enumerate((x + y)):
        #for idx, vals in enumerate((y + x)):
            #self.assertEqual(symobj.solve(vals=vals), addAnswers[idx])
            #print(vals, str(symobj), symobj.solve(vals=vals))

        mulAnswers = [4, 5, 6, 7,
                      5, 6, 7, 8,
                      7, 8, 9, 10,
                      10, 11, 12, 13,
                      102, 103, 104, 105]
        for vals in (x * y):
            self.assertEqual(symobj.solve(vals=vals), mulAnswers.pop(0))
        self.assertEqual(len(mulAnswers), 0)
