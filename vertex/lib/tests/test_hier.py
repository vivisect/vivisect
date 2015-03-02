import unittest

import vertex.lib.hier as v_hier

class HierGraphTest(unittest.TestCase):

    def test_graph_hier(self):

        g = v_hier.HierGraph()

        n1 = g.addNode(foo=10,root=True)
        n2 = g.addNode(foo=20)
        n3 = g.addNode(foo=30)
        n4 = g.addNode(foo=40)
        n5 = g.addNode(foo=50)
        n6 = g.addNode(foo=60)
        n7 = g.addNode(foo=70)

        g.addEdge(n1,n2)
        g.addEdge(n1,n3)

        g.addEdge(n2,n4)
        g.addEdge(n2,n5)

        g.addEdge(n4,n6)
        g.addEdge(n5,n6)

        g.addEdge(n6,n7)
        g.addEdge(n6,n2)    # loop back

        g.addEdge(n3,n7)

        g.calcNodeTiers()

        self.assertEqual( n1[1].get('tier'), 0 )
        self.assertEqual( n2[1].get('tier'), 1 )
        self.assertEqual( n3[1].get('tier'), 1 )
        self.assertEqual( n4[1].get('tier'), 2 )
        self.assertEqual( n5[1].get('tier'), 2 )
        self.assertEqual( n6[1].get('tier'), 3 )
        self.assertEqual( n7[1].get('tier'), 4 )

        self.assertTrue( n7[1].get('leaf') )
        self.assertEqual( g.getGraphInfo('maxtier'), 4 )

        g.calcPathHints()
        self.assertEqual( n1[1].get('maxpath'), 4 )
        self.assertEqual( n1[1].get('minpath'), 2 )
