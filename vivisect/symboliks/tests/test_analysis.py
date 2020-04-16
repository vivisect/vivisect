import unittest

import vivisect.symboliks.common as vsc
import vivisect.symboliks.analysis as vsym_analysis

from vivisect.tests.helpers import MockVw


class MockVar(object):
    def __init__(self, va):
        self.va = va

    def solve(self, *args, **kwargs):
        return self.va


def nop(*args, **kwargs):
    pass


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.sfe = vsym_analysis.SymbolikFunctionEmulator(MockVw())
        self.sfe.setStackCounter = nop

    def test_getStackOffset_above(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr+1))

        self.assertIs(offset, None)

    def test_getStackOffset_inside(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr-1))

        self.assertIs(int(offset), -1)

    def test_getStackOffset_below(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr-size))

        self.assertIs(offset, None)


def cb_astNodeCount(path, obj, ctx):
    ctx['count'] += 1
    if len(path) > ctx['depth']:
        ctx['depth'] = len(path)
    # print("\n\t%r\n\t\t%s" % (obj, '\n\t\t'.join([repr(x) for x in path])))


class WalkTreeTest(unittest.TestCase):

    def test_coverage(self):
        '''
        ((mem[piva_global(0xbfbfee08):1] | (mem[(arg0 + 72):4] & 0xffffff00)) + piva_global())
        '''
        ids = []
        piva1 = vsc.Var('piva_global', 4)
        ids.append(piva1._sym_id)
        arg = vsc.Const(0xbfbfee08, 4)
        ids.append(arg._sym_id)
        call = vsc.Call(piva1, 4, argsyms=[arg])
        ids.append(call._sym_id)
        con = vsc.Const(1, 4)
        ids.append(con._sym_id)
        mem1 = vsc.Mem(call, con)
        ids.append(mem1._sym_id)

        arg = vsc.Arg(0, 4)
        ids.append(arg._sym_id)
        addop = vsc.Const(72, 4)
        ids.append(addop._sym_id)
        add = vsc.o_add(arg, addop, 4)
        ids.append(add._sym_id)
        con = vsc.Const(4, 4)
        ids.append(con._sym_id)
        memac = vsc.Mem(add, con)
        ids.append(memac._sym_id)
        andop = vsc.Const(0xffffff00, 4)
        ids.append(andop._sym_id)
        mem2 = vsc.o_and(memac, andop, 4)
        ids.append(mem2._sym_id)
        memor = vsc.o_or(mem1, mem2, 4)
        ids.append(memor._sym_id)

        piva2 = vsc.Var('piva_global', 4)
        ids.append(piva2._sym_id)
        call2 = vsc.Call(piva2, 4, argsyms=[])
        ids.append(call2._sym_id)
        add = vsc.o_add(memor, call2, 4)
        ids.append(add._sym_id)

        traveled_ids = []
        def walkerTest(path, symobj, ctx):
            traveled_ids.append(symobj._sym_id)

        add.walkTree(walkerTest)
        self.assertEqual(traveled_ids, ids)
        self.assertEqual('((mem[piva_global(0xbfbfee08):1] | (mem[(arg0 + 72):4] & 0xffffff00)) + piva_global())', str(add))

    def test_cleanwalk(self):
        '''
        test that we don't accidentally populate the solver cache while walking the tree
        '''
        symstr = "o_add(o_xor(o_sub(Var('eax', 4), Const(98, 4), 4), Const(127, 4), 4), Const(4, 4), 4)"
        symobj = vsc.evalSymbolik(symstr)
        objs = []
        def walker(path, symobj, ctx):
            objs.append(symobj)
        symobj.walkTree(walker)

        self.assertEquals(len(objs), 7)
        for obj in objs:
            self.assertEquals(obj.cache, {})
