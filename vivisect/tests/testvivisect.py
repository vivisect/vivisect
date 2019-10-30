import unittest

from cStringIO import StringIO

import vivisect
import vivisect.tests.helpers as helpers


class VivisectTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.chgrp_vw = helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')
        cls.vdir_vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')

    def test_consecutive_jump_table(self):
        primaryJumpOpVa = 0x804c9b6
        secondJumpOpVa = 0x804ca2b

        pfva = self.chgrp_vw.getFunction(primaryJumpOpVa)
        sfva = self.chgrp_vw.getFunction(secondJumpOpVa)
        self.assertEqual(pfva, sfva)
        self.assertTrue(pfva is not None)

        # 2 actual codeblocks and 1 xref to the jumptable itself
        prefs = self.chgrp_vw.getXrefsFrom(primaryJumpOpVa)
        self.assertEqual(len(prefs), 3)
        cmnt = self.chgrp_vw.getComment(0x804c9bd)
        self.assertEqual(cmnt, 'Other Case(s): 2, 6, 8, 11, 15, 20, 21, 34, 38, 40, 47')
        # 13 actual codeblocks and 1 xref to the jumptable itself
        srefs = self.chgrp_vw.getXrefsFrom(secondJumpOpVa)
        self.assertEqual(len(srefs), 14)
        cmnt = self.chgrp_vw.getComment(0x804ca4a)
        self.assertEqual(cmnt, 'Other Case(s): 41')

    def test_jumptable_adjacent_strings(self):
        jmpop = 0x804abc7
        cases = list(map(lambda k: k[1], self.chgrp_vw.getXrefsFrom(jmpop)))
        self.assertEqual(len(cases), 11)

        casevas = [
            0x804ac76,
            0x804ac88,
            0x804ac98,
            0x804ac86,
            0x804ac8a,
            0x804b671,
            0x804ac56,
            0x804acd6,
            0x804abce,
            0x804abf4,
            0x805162c
        ]
        self.assertEqual(casevas, cases)

        strlocs = [
            (0x8051930, 8, 2, 'literal\x00'),
            (0x8051938, 6, 2, 'shell\x00'),
            (0x805193e, 13, 2, 'shell-always\x00'),
            (0x805194b, 13, 2, 'shell-escape\x00'),
            (0x8051958, 20, 2, 'shell-escape-always\x00'),
            (0x805196c, 8, 2, 'c-maybe\x00'),
            (0x8051974, 8, 2, 'clocale\x00'),
        ]
        for lva, lsize, ltype, lstr in strlocs:
            loctup = self.chgrp_vw.getLocation(lva)
            self.assertEqual(loctup[0], lva)
            self.assertEqual(lsize, loctup[1])
            self.assertEqual(ltype, loctup[2])
            self.assertEqual(lstr, self.chgrp_vw.readMemory(lva, lsize))

    def test_libfunc_meta_equality(self):
        '''
        both vdir and chgrp have a bunch of library ufunctions in common, and while the addresses
        may be off, other information like # of blocks, # of xrefs from each block, etc.
        '''
        vdir_fva = 0x8055bb0
        chgp_fva = 0x804ab30

        vmeta = self.vdir_vw.getFunctionMetaDict(vdir_fva)
        cmeta = self.chgrp_vw.getFunctionMetaDict(chgp_fva)

        self.assertEqual(vmeta['InstructionCount'], cmeta['InstructionCount'])
        self.assertEqual(vmeta['InstructionCount'], 868)

        self.assertEqual(vmeta['BlockCount'], cmeta['BlockCount'])
        self.assertEqual(vmeta['BlockCount'], 261)

        self.assertEqual(vmeta['Size'], cmeta['Size'])
        self.assertEqual(vmeta['Size'], 3154)  # or 877?

        self.assertEqual(vmeta['MnemDist'], cmeta['MnemDist'])

        self.assertEqual(vmeta['Recursive'], cmeta['Recursive'])
        self.assertTrue(vmeta['Recursive'])

    def test_non_codeblock(self):
        '''
        So these VAs used to be recognized as codeblocks, which is not correct.
        <va> should be actually be a VA in the middle of a string
        <strtbl> should be a table of *string* pointers, not code block pointers
        '''
        badva = 0x0805b6f2
        loctup = self.vdir_vw.getLocation(badva)
        self.assertEqual((134592163, 86, 2, None), loctup)

        strtbl = 0x805e75c
        loctup = self.vdir_vw.getLocation(strtbl)
        self.assertEqual(loctup, (strtbl, 4, 4, None))

    def test_consecutive_jump_table_diff_func(self):
        jumptabl = [
            0x8059718,
            0x8059b68,
            0x8059b78,
            0x8059b90,
            0x8059ba4,
            0x8059bb8,
            0x8059d9c,
            0x8059e30,
            0x8059fac
        ]

        # list of tuples of (xref addr, func addr, number of xrefs from xref addr)
        ans = [
            (0x804a468, 0x804a210, 62),
            (0x804ad21, 0x804a210, 5),
            (0x804b00a, 0x804a210, 7),  # 0x8059b78
            (0x804beee, 0x804bee0, 6),
            (0x804d1c9, 0x804d1a0, 6),
            (0x804d28f, 0x804d1a0, 15),  # 0x8059bb8
            (0x804d1e7, 0x804d1a0, 6),
            (0x804d95b, 0x804d820, 3),
            (0x804fd01, 0x804fc70, 9)  # 0x8059fac
        ]

        for i, tablva in enumerate(jumptabl):
            refva = self.vdir_vw.getXrefsTo(tablva)
            self.assertEqual(len(refva), 1)
            refva = refva[0]
            func = self.vdir_vw.getFunction(refva[0])
            refs = self.vdir_vw.getXrefsFrom(refva[0])
            test = ans[i]
            self.assertEqual(refva[0], test[0])
            self.assertEqual(func, test[1])
            self.assertEqual(len(refs), test[2])

    def _exe_generics(self, vw):
        globstr = [ loc for loc in vw.getLocations(LOC_STRING) if vw.readMemory(loc[0], loc[1]-1) == 'A Global String' ]
        self.assertTrue(globstr)
        self.assertTrue( vw.getImportCallers('kernel32.CreateFileA') )

    def checkTestWorkspace(self, vw, ans):
        self.assertEqual( vw.getMeta('Platform'), ans.getMeta('Platform') )
        self.assertEqual( vw.getMeta('Architecture'), ans.getMeta('Architecture') )

        self.assertEqual( sorted( vw.getFunctions() ), sorted( ans.getFunctions() ) )
        self.assertEqual( sorted( vw.getLibraryDependancies() ), sorted( ans.getLibraryDependancies() ) )
        self.assertEqual( sorted( vw.getRelocations() ), sorted( ans.getRelocations() ) )
        self.assertEqual( sorted( vw.getImports() ), sorted( ans.getImports() ) )
        self.assertEqual( sorted( vw.getExports() ), sorted( ans.getExports() ) )
        self.assertEqual( sorted( vw.getSegments() ), sorted( ans.getSegments() ) )
        #self.assertEqual( sorted( vw.getCodeBlocks() ), sorted( ans.getCodeBlocks() ) )
        #self.assertEqual( sorted( vw.getLocations() ), sorted( ans.getLocations() ) )
        #self.assertEqual( sorted( vw.getNames() ), sorted( ans.getNames() ) )
        self.assertEqual( sorted( vw.getFiles() ), sorted( ans.getFiles() ) )

        for fva in ans.getFunctions():
            self.assertEqual(vw.getFunction(fva), ans.getFunction(fva))
            vwfgraph = viv_graph.buildFunctionGraph(vw, fva)
            ansfgraph = viv_graph.buildFunctionGraph(ans, fva)
            vwnodes = vwfgraph.nodes.keys()
            ansnodes = ansfgraph.nodes.keys()
            self.assertEqual( sorted( vwnodes ), sorted( ansnodes ) )
            vwedges = [(x, y) for w, x, y, z in vwfgraph.getEdges()]
            ansedges = [(x, y) for w, x, y, z in ansfgraph.getEdges()]
            self.assertEqual( sorted( vwedges ), sorted( ansedges ) )


    def getAndTestWorkspace(self, fname):
        vw = getTestWorkspace(fname)
        ans = getAnsWorkspace(fname)
        self.checkTestWorkspace(vw, ans)
        return vw

    @vivbins.require
    def test_viv_elf_i386(self):
        vw = self.getAndTestWorkspace('test_elf_i386')

    @vivbins.require
    def test_viv_elf_arm(self):
        vw = self.getAndTestWorkspace('test_elf_arm')

    #def test_macho_i386(self):
        #vw = self.getAndTestWorkspace('test_macho_i386')

    #def test_macho_amd64(self):
        #vw = self.getAndTestWorkspace('test_macho_amd64')

    @vivbins.require
    def test_viv_testexe_i386(self):
        vw = self.getAndTestWorkspace('testexe_i386.exe')
        self._exe_generics(vw)

        # This is actually a fairly thorough test of the impemu subsystem...
        cfa_callers = vw.getImportCallers('kernel32.CreateFileA')
        cmnt = vw.getComment(cfa_callers[0])
        self.assertEqual(cmnt,'kernel32.CreateFileA(64,65,66,67,68,69,70)')

    @vivbins.require
    def test_viv_testexe_amd64(self):
        vw = self.getAndTestWorkspace('testexe_amd64.exe')
        self._exe_generics(vw)

    @vivbins.require
    def test_viv_vector_getImportCallers(self):
        vw = self.getTestWorkspace('testexe_i386.exe')
        cargs = [64, 65, 66, 67, 68, 69, 70]
        argvs = [ argv for (va,argv) in viv_vector.trackImportInputs(vw, 'kernel32.CreateFileA') ]

        # Make sure we found our silly call...
        self.assertTrue( cargs in argvs )

    def test_viv_bigend(self):
        fd = StringIO('ABCDEFG')

        vw = vivisect.VivWorkspace()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.bigend = True
        vw.config.viv.parsers.blob.baseaddr = 0x22220000

        vw.loadFromFd(fd, fmtname='blob')

        self.assertEqual(vw.castPointer(0x22220000), 0x41424344)
        self.assertEqual(vw.parseNumber(0x22220000, 2), 0x4142)

    def test_posix_impapi(self):
        pass
