import unittest

import vstruct
import vstruct.primitives as p

class NNestedStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.alpha = p.v_uint64()
        self.beta = vstruct.VStruct()

class NestedStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.foo = p.v_bytes(size=3)
        self.bar = p.v_uint32()
        self.baz = p.v_bytes(size=256)
        self.faz = NNestedStruct()

class TestStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.one = p.v_uint32()
        self.two = NestedStruct()
        self.three = p.v_uint32()
        self.four = p.v_bytes(size=100)

class VStructTests(unittest.TestCase):
    def setUp(self):
        self.s = TestStruct()

    def test_vsGetFieldByOffset_start(self):
        fname, fobj = self.s.vsGetFieldByOffset(0)
        self.assertEqual(fname, 'one')
        self.assertIs(fobj, self.s.vsGetField('one'))

    def test_vsGetFieldByOffset_end(self):
        fname, fobj = self.s.vsGetFieldByOffset(len(self.s) - 1)
        self.assertEqual(fname, 'four')
        self.assertIs(fobj, self.s.vsGetField('four'))

    def test_vsGetFieldByOffset_maxval_neg(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            tup = self.s.vsGetFieldByOffset(-1)

    def test_vsGetFieldByOffset_maxval_pos(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            tup = self.s.vsGetFieldByOffset(0xffffffff)

    def test_vsGetFieldByOffset_maxval_plus1_pos(self):
        with self.assertRaisesRegexp(Exception, 'Invalid Offset Specified'):
            tup = self.s.vsGetFieldByOffset(len(self.s))

    def test_vsGetFieldByOffset_nested1(self):
        fname, fobj = self.s.vsGetFieldByOffset(5)
        self.assertEqual(fname, 'two.foo')
        self.assertIs(fobj, self.s.two.vsGetField('foo'))

    def test_vsGetFieldByOffset_nested2(self):
        fname, fobj = self.s.vsGetFieldByOffset(8)
        self.assertEqual(fname, 'two.bar')
        self.assertIs(fobj, self.s.two.vsGetField('bar'))

    def test_vsGetFieldByOffset_nested3(self):
        fname, fobj = self.s.vsGetFieldByOffset(12)
        self.assertEqual(fname, 'two.baz')
        self.assertIs(fobj, self.s.two.vsGetField('baz'))

    def test_vsGetFieldByOffset_nested4(self):
        fname, fobj = self.s.vsGetFieldByOffset(267)
        self.assertEqual(fname, 'two.faz.alpha')
        self.assertIs(fobj, self.s.two.faz.vsGetField('alpha'))

# TODO: could use envi.bits, but do we really want envi dep by default?
blkup = {}
bwidths = (8, 16, 24, 32, 64, )
for bwidth in bwidths:
    umax = (2**bwidth) - 1
    umin = 0

    smax = (2**(bwidth-1)) - 1
    smin = -(2**(bwidth-1))

    blkup[bwidth] = (umin, umax, smin, smax)

class IntegerStruct(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

class VStructTypeTests(unittest.TestCase):
    def setUp(self):
        self.s = IntegerStruct()

def getTestFunc(name, vsval, val, expval):

    def func(self):
        self.s.vsAddField(name, vsval)

        setattr(self.s, name, val)

        rval = getattr(self.s, name)
        self.assertEqual(rval, expval)

    return func

tdefs = []

# dynamically generate the test definitions
# width, pname, vtype, test value, expected value
for bwidth in bwidths:
    umin, umax, smin, smax = blkup[bwidth]

    for ttype, mmin, mmax in ( ('u', umin, umax), ('', smin, smax), ):
        pname = '{}int{}'.format(ttype, bwidth)
        vtype = 'v_{}int{}'.format(ttype, bwidth)
        vtype = getattr(p, vtype)

        tup = (bwidth, pname, vtype, mmin, mmin)
        tdefs.append(tup)

        tup = (bwidth, pname, vtype, mmax, mmax)
        tdefs.append(tup)

        tup = (bwidth, pname, vtype, mmin-1, mmax)
        tdefs.append(tup)

        tup = (bwidth, pname, vtype, mmin-2, mmax-1)
        tdefs.append(tup)

        tup = (bwidth, pname, vtype, mmax+1, mmin)
        tdefs.append(tup)

        tup = (bwidth, pname, vtype, mmax+2, mmin+1)
        tdefs.append(tup)

# generate unittest functions based on the test definitions
for width, pname, vtype, val, expval in tdefs:
    tfunc = getTestFunc(pname, vtype(), val, expval)
    tname = 'test_{}_{}_{}'.format(pname, val, expval)
    setattr(VStructTypeTests, tname, tfunc)
