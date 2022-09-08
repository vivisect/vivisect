import unittest

from vivisect.symboliks.tests.helpers import MockEmulator
import vivisect.const as vcon

from vivisect.tests.helpers import MockVw


class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.se = MockEmulator(MockVw())

    def test_variables(self):
        self.se.parseExpression('foo = 3 * 2')
        self.se.parseExpression('bar = 4 * 9')
        self.se.parseExpression('biz = foo * bar')
        self.se.parseExpression('biz = biz << 2')
        self.se.parseExpression('wat = foo * buzz')
        svar = self.se.getSymVariables()

        self.assertTrue(len(svar) == 4)
        self.se.setSymVariable('x', 'foobar')
        self.assertTrue(len(self.se.getSymVariables()) == 5)

        foo = self.se.getSymVariable('foo')
        bar = self.se.getSymVariable('bar')
        biz = self.se.getSymVariable('biz')
        wat = self.se.getSymVariable('wat')
        buz = self.se.getSymVariable('buzz')
        bad = self.se.getSymVariable('bad', create=False)
        self.assertTrue(str(foo) == '(3 * 2)')
        self.assertTrue(str(bar) == '(4 * 9)')
        self.assertTrue(str(biz) == '(((3 * 2) * (4 * 9)) << 2)')
        self.assertTrue(str(wat) == '((3 * 2) * buzz)')
        self.assertTrue(str(buz) == 'buzz')
        self.assertIsNone(bad)

    def test_memory(self):
        self.se.parseExpression('foo = 5 * bar')
        foo = self.se.getSymVariable('foo')
        mem = self.se.readSymMemory(foo, 1024, vals={'bar': 20})
        self.assertIsNone(mem)

        self.se._sym_vw._addLocation(100, 1024, vcon.LOC_IMPORT, 'vivisectvivisectvivisect')
        mem = self.se.readSymMemory(foo, 1024, vals={'bar': 20})
        self.assertTrue(str(mem) == 'vivisectvivisectvivisect')

        # check that the symmem shadows the vw mem
        self.se.writeSymMemory(foo, 'test_memory', vals={'bar': 20})
        mem = self.se.readSymMemory(foo, 1024, vals={'bar': 20})
        self.assertTrue(str(mem) == 'test_memory')

    def test_seed(self):
        self.assertTrue(self.se.getRandomSeed() == '')
        self.se.addRandomSeed()
        self.assertTrue(self.se.getRandomSeed() != '')
