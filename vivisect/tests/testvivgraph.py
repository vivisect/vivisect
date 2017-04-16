import os
import unittest
import vivisect
import vivisect.tests.vivbins as vivbins
import vivisect.tools.graphutil as viv_graph
from vivisect.tests.vivbins import getTestWorkspace, getAnsWorkspace

class VivGraphTest(unittest.TestCase):

    def getTestWorkspace(self, fname, analyze=True):
        fpath = os.path.join('vivisect','bins',fname)
        vw = vivisect.VivWorkspace()
        vw.loadFromFile(fpath)
        if analyze:
            vw.analyze()
        return vw

    def getAnsWorkspace(self, fname):
        fpath = os.path.join('vivisect','bins','%s.viv' % fname)
        vw = vivisect.VivWorkspace()
        vw.loadWorkspace(fpath)
        return vw

    def checkGetCodePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva )
        paths = [ path for path in viv_graph.getCodePaths(graph) ]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkGetCodePathsThru(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva )
        paths = [ path for path in viv_graph.getCodePathsThru(graph, cbva) ]
        self.codepathsthru = paths
        self.assertGreater(len(self.codepaths), len(self.codepathsthru))

        paths = [ path for path in graph.getHierPathsThru((cbva,)) ]
        self.hiercodepathsthru = paths
        self.assertGreater(len(self.codepaths), len(self.hiercodepathsthru))

    def checkGetCodePathsFrom(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva )
        paths = [ path for path in viv_graph.getCodePathsFrom(graph, cbva) ]
        self.codepathsfrom = paths
        self.assertGreater(len(self.codepaths), 150)

        paths = [ path for path in graph.getHierPathsFrom,((cbva,)) ]
        self.hierpathsfrom = paths
        self.assertGreater(len(self.codepaths), len(self.hierpathsfrom))

    def checkGetCodePathsTo(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva )
        paths = [ path for path in viv_graph.getCodePathsTo(graph, cbva) ]
        self.codepathsto = paths
        self.assertGreater(len(self.codepaths), len(self.codepathsto))

        paths = [ path for path in graph.getHierPathsTo((cbva,)) ]
        self.hierpathsto = paths
        self.assertGreater(len(self.codepaths), len(self.hierpathsto))

    def checkGetLoopPaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva )
        paths = [ path for path in viv_graph.getLoopPaths(graph) ]
        self.looppaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkGetLongPath(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [ path for path in viv_graph.getLongPath(graph) ]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkPathGenGetCodePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [ path for path in viv_graph.getCodePathsThru(graph) ]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkCoveragePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [ path for path in viv_graph.getCoveragePaths(graph, 150) ]
        self.codepaths = paths
        self.assertEqual(len(self.codepaths), 22)

    @vivbins.require
    def test_viv_graph_paths(self):
        # one file
        fname = 'testexe_amd64.exe'
        fva = 0x1400060ac
        cbva = 0x1400061bf
        vw = getAnsWorkspace(fname)

        self.checkGetCodePaths(vw, fva)
        self.checkGetCodePathsThru(vw, fva, cbva)
        self.checkGetCodePathsFrom(vw, fva, cbva)
        self.checkGetCodePathsTo(vw, fva, cbva)
        self.checkGetLoopPaths(vw, fva)
        self.checkGetLongPath(vw, fva)
        self.checkCoveragePaths(vw, fva)

