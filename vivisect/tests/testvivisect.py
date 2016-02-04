import os
import unittest

from cStringIO import StringIO

import vivisect
import vivisect.vector as viv_vector
import vivisect.tools.graphutil as viv_graph

from vivisect.const import *

import vivisect.tests.vivbins as vivbins
from vivisect.tests.vivbins import getTestWorkspace, getAnsWorkspace

class VivisectTest(unittest.TestCase):

    maxDiff = None
    #def setUp(self):
        #pass

    #def tearDown(self):
        #pass

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

        vw.loadFromFd(fd,fmtname='blob')

        self.assertEqual( vw.castPointer(0x22220000), 0x41424344 )
        self.assertEqual( vw.parseNumber(0x22220000, 2), 0x4142 )

    #def test_impapi_windows(self):
        #imp = viv_impapi.getImportApi('windows','i386')
        #self.assertEqual( imp.getImpApiCallConv('ntdll.RtlAllocateHeap'), 'stdcall')

    #def test_impapi_posix(self):
        #imp = viv_impapi.getImpApi('windows','i386')

    #def test_impapi_winkern(self):
        #imp = viv_impapi.getImportApi('winkern','i386')
        #self.assertEqual( imp.getImpApiCallConv('ntoskrnl.ObReferenceObjectByHandle'), 'stdcall')
