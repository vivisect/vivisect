
from vivisect.symboliks.common import *

class Constraint:
    '''
    A class to represent algebraic constraints that are tracked by a given
    polynomial.
    '''
    revclass = None
    operstr = None

    def __init__(self, v1, v2):
        self._strval = None
        self._v1 = v1
        self._v2 = v2

        # FIXME consider making constraints into operators...
        # Their APIs and internals are basically the same!

    def clearCache(self):
        self._v1.clearCache()
        self._v2.clearCache()

    def walkTree(self, cb, ctx=None, once=True):
        self._v1 = self._v1.walkTree(cb, ctx=ctx, once=once)
        self._v2 = self._v2.walkTree(cb, ctx=ctx, once=once)

    def getWidth(self):
        return self._v1.getWidth()

    def setSymSolverContext(self, slvctx):
        self._v1.setSymSolverContext(slvctx)
        self._v2.setSymSolverContext(slvctx)

    def __repr__(self):
        return '%s(%s,%s)' % (self.__class__.__name__, repr(self._v1), repr(self._v2))

    def __str__(self):
        if self._strval:
            return self._strval

        self._strval = '%s %s %s' % (str(self._v1), self.operstr, str(self._v2))
        return self._strval

    def render(self, canvas, vw):
        self._v1.render(canvas, vw)
        canvas.addText(' ')
        canvas.addNameText(self.operstr)
        canvas.addText(' ')
        self._v2.render(canvas, vw)

    def __eq__(self, con):
        '''
        Is this constraint the same as some other?
        '''
        if not isinstance(con, Constraint):
            return False

        c1v1 = self._v1.solve()
        c1v2 = self._v2.solve()
        c2v1 = con._v1.solve()
        c2v2 = con._v2.solve()

        if c1v1 == c2v1 and c1v2 == c2v2 and self.__class__ == con.__class__:
            return True

        if c1v1 == c2v2 and c1v2 == c2v1 and self.__class__ == con.revclass:
            return True

        return False

    def reverse(self):
        if self.revclass == None:
            raise Exception('Constraints Must Define revclass!')
        return self.revclass(self._v1, self._v2)

    def reduce(self, emu=None):
        v1 = self._v1.reduce(emu=emu)
        v2 = self._v2.reduce(emu=emu)
        # FIXME transfer discrete values to one side...
        return self.__class__(v1, v2)

    def update(self, emu):
        v1 = self._v1.update(emu)
        v2 = self._v2.update(emu)
        return self.__class__(v1, v2)

    def clone(self):
        v1 = self._v1.clone()
        v2 = self._v2.clone()
        return self.__class__(v1, v2)

    def prove(self, emu=None,vals=None):
        v1 = self._v1.solve(emu=emu,vals=vals)
        v2 = self._v2.solve(emu=emu,vals=vals)
        return self.testTruth(v1, v2)

    def solve(self, emu=None, vals=None):
        # A "solution" for a condition is it's boolean state as int...
        return int(self.prove(emu=emu,vals=vals))

    def testTruth(self, v1, v2):
        #raise Exception('Constraint %s must implement testTruth!' % self.__class__.__name__)
        return True

    def isDiscrete(self, emu=None):
        return self._v1.isDiscrete(emu=emu) and self._v2.isDiscrete(emu=emu)

def opose(c1, c2):
    c1.revclass = c2
    c2.revclass = c1

class eq(Constraint):
    operstr = '=='
    symtype = SYMT_CON_EQ
    def testTruth(self, v1, v2):
        return v1 == v2

class ne(Constraint):
    operstr = '!='
    symtype = SYMT_CON_NE
    def testTruth(self, v1, v2):
        return v1 != v2

class le(Constraint):
    operstr = '<='
    symtype = SYMT_CON_LE
    def testTruth(self, v1, v2):
        return v1 <= v2

class gt(Constraint):
    operstr = '>'
    symtype = SYMT_CON_GT
    def testTruth(self, v1, v2):
        return v1 > v2

class lt(Constraint):
    operstr = '<'
    symtype = SYMT_CON_LT
    def testTruth(self, v1, v2):
        return v1 < v2

class ge(Constraint):
    operstr = '>='
    symtype = SYMT_CON_GE
    def testTruth(self, v1, v2):
        return v1 >= v2

class UNK(Constraint): 
    operstr = 'UNK'
    symtype = SYMT_CON_UNK
class NOTUNK(Constraint): 
    operstr = '!UNK'
    symtype = SYMT_CON_NOTUNK

# Create our oposing constraints
opose(ne, eq)
opose(le, gt)
opose(lt, ge)
opose(UNK, NOTUNK)

