import unittest
import vivisect.tools.graphutil as viv_graph
import visgraph.graphcore as vs_graphcore


class VivGraphTest(unittest.TestCase):

    def setUp(self):
        self.graphjson = '{"nodes": {"A": {"rootnode": true}, "C": {}, "B": {}, "E": {}, "D": {}, "G": {}, "F": {}, "I": {}, "H": {}, "K": {}, "J": {}, "M": {}, "L": {}, "O": {}, "N": {}, "P": {}}, "edges": [["A_B", "A", "B", {}], ["A_C", "A", "C", {}], ["C_E", "C", "E", {}], ["E_G", "E", "G", {}], ["G_I", "G", "I", {}], ["I_K", "I", "K", {}], ["K_N", "K", "N", {}], ["N_P", "N", "P", {}], ["K_J", "K", "J", {}], ["J_L", "J", "L", {}], ["J_M", "J", "M", {}], ["P_O", "P", "O", {}], ["J_G", "J", "G", {}], ["B_D", "B", "D", {}], ["D_F", "D", "F", {}], ["F_H", "F", "H", {}], ["H_J", "H", "J", {}]]}'
        self.graph = vs_graphcore.HierGraph.fromJsonBuf(self.graphjson)

    def checkGetCodePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCodePaths(graph)]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkGetCodePathsThru(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCodePathsThru(graph, cbva)]
        self.codepathsthru = paths
        self.assertGreater(len(self.codepaths), len(self.codepathsthru))

        paths = [path for path in graph.getHierPathsThru((cbva,))]
        self.hiercodepathsthru = paths
        self.assertGreater(len(self.codepaths), len(self.hiercodepathsthru))

    def checkGetCodePathsFrom(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCodePathsFrom(graph, cbva)]
        self.codepathsfrom = paths
        self.assertGreater(len(self.codepaths), 150)

        paths = [path for path in graph.getHierPathsFrom((cbva,))]
        self.hierpathsfrom = paths
        self.assertGreater(len(self.codepaths), len(self.hierpathsfrom))

    def checkGetCodePathsTo(self, vw, fva, cbva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCodePathsTo(graph, cbva)]
        self.codepathsto = paths
        self.assertGreater(len(self.codepaths), len(self.codepathsto))

        paths = [path for path in graph.getHierPathsTo((cbva,))]
        self.hierpathsto = paths
        self.assertGreater(len(self.codepaths), len(self.hierpathsto))

    def checkGetLoopPaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getLoopPaths(graph)]
        self.looppaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkGetLongPath(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getLongPath(graph)]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkPathGenGetCodePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCodePathsThru(graph)]
        self.codepaths = paths
        self.assertGreater(len(self.codepaths), 150)

    def checkCoveragePaths(self, vw, fva):
        graph = viv_graph.buildFunctionGraph(vw, fva)
        paths = [path for path in viv_graph.getCoveragePaths(graph, 150)]
        self.codepaths = paths
        self.assertEqual(len(self.codepaths), 22)

    def test_longpath(self):
        weights = self.graph.getHierNodeWeights()
        path_gen = viv_graph.getLongPath(self.graph)
        long_path = path_gen.next()
