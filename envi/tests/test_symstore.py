import envi.symstore.resolver as e_sym_resolv

import unittest

class SymResolverTests(unittest.TestCase):
    def setUp(self):
        self.symres = e_sym_resolv.SymbolResolver()

    def test_sym(self):
        fname, base, size, width = ('foo', 0x1234, 0x5678, 4)
        fres = e_sym_resolv.FileSymbol(fname, base, size, width)
        # check Symbol vars
        assert(fres.name == fname)
        assert(fres.value == base)
        assert(fres.size == size)
        #assert(fres.fname == fname)

        # check SymbolResolver vars
        assert(fres.width == width)
        assert(fres.baseaddr == base)

    def test_resolver_fname_none(self):
        with self.assertRaises(Exception):
            fresolv = e_sym_resolv.FileSymbol(None, 0, 0, 4)

    def test_resolver(self):
        fname, base, size, width = ('foo', 0x0, 0, 4)
        fres = e_sym_resolv.FileSymbol(fname, base, size, width)

        self.symres.addSymbol(fres)
        self.assertIn(fname, self.symres.symobjsbyname)
        self.assertIsInstance(self.symres.symobjsbyname[fname], e_sym_resolv.SymbolResolver)

        fnsym = e_sym_resolv.FunctionSymbol('TestFooFuncSym', 0x123456, size=4, fname=fname)
        self.symres.addSymbol(fnsym)
        secsym = e_sym_resolv.SectionSymbol('TestFooSectionSym', 0x123456, size=400, fname=fname)
        self.symres.addSymbol(secsym)

        self.symres.delSymbol(fnsym)
        self.assertNotIn(fnsym, self.symres.symobjsbyname)

    def test_getSymByAddr_exact_false(self):
        '''
        test for bug that was replacing symresolvers with symbol objects.
        '''
        fname, base, size, width = ('foo', 0x0, 0, 4)
        fres = e_sym_resolv.FileSymbol(fname, base, size, width)
        self.symres.addSymbol(fres)

        # now symobjsbyname['foo'] = FileSymbol

        symcache = [(0x16001, 0, 'alpha', e_sym_resolv.SYMSTOR_SYM_SYMBOL)]
        self.symres.impSymCache(symcache, symfname='foo')

        # look up the FileSymbol as a 'Symbol' (not a resolver)
        # this causes the symobjsbyname to smash in a Symbol instead of a
        # SymbolResolver (symobjsbyname['foo'] = Symbol)
        sym = self.symres.getSymByAddr(0x10, exact=False)
        assert(sym is not None)

        # now symobjsbyname['foo'] = Symbol

        # force return of a sym that has a fname set
        # causes a .get on symobjsbyname, retrieves Symbol, but then tries
        # to cache since it should be a resolver since we have an fname.
        # boom.
        sym = self.symres.getSymByAddr(0x16010, exact=False)
        assert(sym is not None)

    #def test_import
