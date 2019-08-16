import unittest
import visgraph.graphcore as vs_graphcore
import vivisect.tools.graphutil as viv_graph


class VivGraphTest(unittest.TestCase):

    def setUp(self):
        g = vs_graphcore.HierGraph()
        g.addHierRootNode('Rooty')

        g.addNode('Righty')
        g.addNode('SonOfRighty')
        g.addNode('RightyStrikesBack')
        g.addNode('TheEnd')
        g.addNode('OrIsIt')
        g.addNode('TheReboot')
        g.addNode('Nobody')
        g.addNode('Wanted')

        g.addNode('Lefty')
        g.addNode('SonOfLefty')
        g.addNode('LeftysRevenge')
        g.addNode('LeftyTheReboot')

        g.addNode('Backtracker')
        g.addNode('LeftyClone')
        g.addNode('RightyClone')

        g.addEdgeByNids('Rooty', 'Lefty')
        g.addEdgeByNids('Rooty', 'Righty')

        g.addEdgeByNids('Lefty', 'SonOfLefty')
        g.addEdgeByNids('SonOfLefty', 'LeftysRevenge')
        g.addEdgeByNids('LeftysRevenge', 'LeftyTheReboot')
        g.addEdgeByNids('LeftyTheReboot', 'Backtracker')

        g.addEdgeByNids('Backtracker', 'LeftyClone')
        g.addEdgeByNids('Backtracker', 'RightyClone')
        g.addEdgeByNids('Backtracker', 'RightyStrikesBack')

        g.addEdgeByNids('Righty', 'SonOfRighty')
        g.addEdgeByNids('SonOfRighty', 'RightyStrikesBack')
        g.addEdgeByNids('RightyStrikesBack', 'TheEnd')
        g.addEdgeByNids('TheEnd', 'OrIsIt')
        g.addEdgeByNids('OrIsIt', 'Backtracker')
        g.addEdgeByNids('OrIsIt', 'TheReboot')
        g.addEdgeByNids('TheReboot', 'Nobody')
        g.addEdgeByNids('Nobody', 'Wanted')

        self.graph = g

    def test_longpath(self):
        longpath = [
            'Rooty',
            'Lefty',
            'SonOfLefty',
            'LeftysRevenge',
            'LeftyTheReboot',
            'Backtracker',
            'RightyStrikesBack',
            'TheEnd',
            'OrIsIt',
            'TheReboot',
            'Nobody',
            'Wanted',
        ]
        pathgenr = viv_graph.getLongPath(self.graph)
        path = map(lambda k: k[0], pathgenr.next())
        self.assertEqual(longpath, path)

    def test_weights(self):
        '''
        Note: Weights are defined as the maximum length of all the paths to a node from the rootnodes
        So if a node A is the child of rootnode B, but it's also 7 hops from rootnode C, it's weight
        is going to be 7
        '''
        weights = self.graph.getHierNodeWeights()
        self.assertEqual(weights['Rooty'], 0)
        self.assertEqual(weights['Lefty'], 1)
        self.assertEqual(weights['SonOfLefty'], 2)
        self.assertEqual(weights['LeftysRevenge'], 3)
        self.assertEqual(weights['LeftyTheReboot'], 4)
        self.assertEqual(weights['Backtracker'], 6)
        self.assertEqual(weights['LeftyClone'], 7)
        self.assertEqual(weights['RightyClone'], 7)

        self.assertEqual(weights['Righty'], 1)
        self.assertEqual(weights['SonOfRighty'], 2)
        self.assertEqual(weights['RightyStrikesBack'], 3)
        self.assertEqual(weights['TheEnd'], 4)
        self.assertEqual(weights['OrIsIt'], 5)
        self.assertEqual(weights['TheReboot'], 6)
        self.assertEqual(weights['Nobody'], 7)
        self.assertEqual(weights['Wanted'], 8)
