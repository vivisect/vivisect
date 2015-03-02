import unittest

import vertex.graph as v_graph

class GraphTest(unittest.TestCase):

    def test_graph_basic(self):
        g = v_graph.Graph()
        node1 = g.addNode(woot=10,keep='keep')
        node2 = g.addNode(woot=20,keep='keep')
        edge = g.addEdge(node1,node2,woot=30,keep='keep')

        self.assertEqual( g.getNodeById(node1[0])[1].get('woot'), 10 )
        self.assertEqual( g.getNodeById(node2[0])[1].get('woot'), 20 )
        self.assertEqual( g.getEdgesByProp('_:n1',node1[0])[0],edge )
        self.assertEqual( g.getEdgesByProp('_:n2',node2[0])[0],edge )

        node1 = g.delNodeProp(node1,'woot')
        node2 = g.delNodeProp(node2,'woot')

        self.assertIsNone( g.getNodeById(node1[0])[1].get('woot') )
        self.assertIsNone( g.getNodeById(node2[0])[1].get('woot') )

        g.delNode(node1)

        self.assertIsNone( g.getEdgeById(edge[0]) )
        self.assertIsNone( g.getNodeById(node1[0]) )

        g.synShutDown()

    def test_graph_n1byn2(self):
        g = v_graph.Graph()
        node1 = g.addNode(woot=10,keep='keep')
        node2 = g.addNode(woot=20,keep='keep')
        edge = g.addEdge(node1,node2,woot=30,keep='keep')

        self.assertEqual( list(g.getN1NodesByN2(node2))[0][0], node1[0] )

    def test_graph_n2byn1(self):
        g = v_graph.Graph()
        node1 = g.addNode(woot=10,keep='keep')
        node2 = g.addNode(woot=20,keep='keep')
        edge = g.addEdge(node1,node2,woot=30,keep='keep')

        self.assertEqual( list(g.getN2NodesByN1(node1))[0][0], node2[0] )
