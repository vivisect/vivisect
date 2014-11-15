import unittest

import visgraph.graphcore as v_graphcore
import visgraph.layouts.dynadag as v_dynadag

class GraphLayoutTest(unittest.TestCase):

    def sampGraph1(self):
        g = v_graphcore.HierGraph()

        g.addNode('a',rootnode=True)
        g.addNode('b')
        g.addNode('c')
        g.addNode('d')

        g.addEdgeByNids('a','b')
        g.addEdgeByNids('a','c')
        g.addEdgeByNids('c','a') # loop...
        g.addEdgeByNids('c','d')

        return g

    def sampGraph2(self):
        g = v_graphcore.HierGraph()

        g.addNode('a',rootnode=True)
        g.addNode('b')
        g.addNode('c')
        g.addNode('d')
        g.addNode('e')

        #       a
        #     / | \
        #   b  +c  |
        #      | \ /
        #      |  d
        #      |  |
        #      |  e
        #      +--+

        g.addEdgeByNids('a','b')
        g.addEdgeByNids('a','c')
        g.addEdgeByNids('a','d') # skip layer
        g.addEdgeByNids('c','d')
        g.addEdgeByNids('d','e')
        g.addEdgeByNids('e','c') # loop skip

        return g

    def test_visgraph_weights(self):

        g1 = self.sampGraph1()
        g1weights = {'a':0,'b':1,'c':1,'d':2}
        self.assertEqual(g1.getHierNodeWeights(), g1weights)

        for nid,nprops in g1.getNodes():
            self.assertEqual(nprops.get('weight'),g1weights.get(nid))

        g2 = self.sampGraph2()
        g2weights = {'a':0,'b':1,'c':3,'d':2,'e':3}
        self.assertEqual(g2.getHierNodeWeights(), g2weights)

        for nid,nprops in g2.getNodes():
            self.assertEqual(nprops.get('weight'),g2weights.get(nid))

    def test_visgraph_dynadag(self):
        g1 = self.sampGraph1()
        lyt = v_dynadag.DynadagLayout(g1)
        lyt.layoutGraph()

        self.assertEqual(g1.getNode('a')[1].get('position'),(20,0))
        self.assertEqual(g1.getNode('b')[1].get('position'),(20,40))
        self.assertEqual(g1.getNode('c')[1].get('position'),(40,40))
        self.assertEqual(g1.getNode('d')[1].get('position'),(20,80))

        g2 = self.sampGraph2()
        lyt = v_dynadag.DynadagLayout(g2)
        lyt.layoutGraph()

        self.assertEqual(g2.getNode('a')[1].get('position'),(20,0))
        self.assertEqual(g2.getNode('b')[1].get('position'),(20,40))
        self.assertEqual(g2.getNode('c')[1].get('position'),(40,120))
        self.assertEqual(g2.getNode('d')[1].get('position'),(20,80))
        self.assertEqual(g2.getNode('e')[1].get('position'),(20,120))

