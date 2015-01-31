import unittest
from synapse.lib.apistack import *

class Woot(ApiStack):

    def __init__(self):
        ApiStack.__init__(self)

    @stackable
    def foo(self, x, y, z=None):
        return (x,y,z)

    def bar(self, x, y, z=None):
        return (x,y,z)

class ApiStackTest(unittest.TestCase):

    def test_apistack_noapi(self):
        w = Woot()
        self.assertRaises(NoSuchApi, w.addApiHook, 'gronk',None)

    def test_apistack_cantstack(self):
        w = Woot()
        self.assertRaises(ApiCantStack, w.addApiHook, 'bar',None)

    def test_apistack_passive(self):
        d = dict()
        def callback(o, x, y, z=None):
            d['args'] = (x,y,z)

        w = Woot()
        w.addApiHook('foo',callback)
        retval = w.foo(3,4,z=5)

        self.assertEqual( retval, (3,4,5) )
        self.assertEqual( d.get('args'), (3,4,5) )

    def test_apistack_hookcall(self):
        def callback(o, x, y, z=None):
            return hookcall('a','b',z='z')

        w = Woot()
        w.addApiHook('foo',callback)
        retval = w.foo(3,4,z=5)

        self.assertEqual( retval, ('a','b','z') )

    def test_apistack_hookret(self):
        def callback(o, x, y, z=None):
            return hookret('blah')

        w = Woot()
        w.addApiHook('foo',callback)
        retval = w.foo(3,4,z=5)

        self.assertEqual( retval, 'blah')
