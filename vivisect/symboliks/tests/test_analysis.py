import sys
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


import vivisect.tests.vivbins as vivbins
from vivisect.tests.vivbins import getAnsWorkspace
def cb_astNodeCount(path, obj, ctx):
    ctx['count'] += 1
    if len(path) > ctx['depth']:
        ctx['depth'] = len(path)
    # print("\n\t%r\n\t\t%s" % (obj, '\n\t\t'.join([repr(x) for x in path])))


class WalkTreeTest(unittest.TestCase):

    @vivbins.require
    def test_symbolik_maneuvers(self):
        try:
            vw = getAnsWorkspace('test_kernel32_32bit-5.1.2600.5781.dll')
            walkTreeDoer(vw)
        except Exception as e:
            sys.excepthook(*sys.exc_info())

        try:
            vw = getAnsWorkspace('test_elf_i386')
            walkTreeDoer(vw)
        except Exception:
            sys.excepthook(*sys.exc_info())

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


def walkTreeDoer(vw):
    sctx = vsym_analysis.getSymbolikAnalysisContext(vw)

    count = 0
    for fva in vw.getFunctions():
        ctx = {'depth': 0, 'count': 0}
        count += 1
        #print "(%d) 0x%x done" % (count, fva)
        #raw_input("============================================================")

        for spath in sctx.getSymbolikPaths(fva, maxpath=1):
            effs = spath[-1]
            if not len(effs):
                continue
            eff = effs[-1]

            # print("=====\n %r \n=====" % (eff))
            # this is ugly
            symast = getattr(eff, 'symobj', None)

            if symast is None:
                symast = getattr(eff, 'addrsym', None)

            if symast is None:
                symast = getattr(eff, 'cons', None)

            if symast is None:
                symast = getattr(eff, 'funcsym', None)
            if symast is None:
                symast = getattr(eff, 'argsyms', None)

            if symast is None:
                symast = getattr(eff, 'symaddr', None)
            if symast is None:
                symast = getattr(eff, 'symval', None)


            if symast == None:
                #print "CRAP!  skipping"
                continue

            eff.walkTree(cb_astNodeCount, ctx); ctx
