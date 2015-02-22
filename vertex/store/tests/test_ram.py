import unittest

import vertex.store.ram as v_s_ram
import vertex.store.common as v_common
import synapse.lib.common as s_common

class RamStorageTest(unittest.TestCase):

    def test_ram_store(self):
        g = v_s_ram.GraphStore()

        nid = s_common.guid()
        eid = s_common.guid()

        node = (nid,{'woot':10})
        edge = (eid,{'woot':20})

        g.addNode(node)
        g.addEdge(edge)

        self.assertEqual( g.getNodeById(nid), node)
        self.assertEqual( g.getEdgeById(eid), edge)

    def test_ram_index_keyval(self):

        g = v_s_ram.GraphStore()

        g.initNodeIndex('woot','keyval')
        g.initEdgeIndex('woot','keyval')

        g.initNodeIndex('keep','keyval')
        g.initEdgeIndex('keep','keyval')

        nid = s_common.guid()
        eid = s_common.guid()

        node = (nid,{'woot':'foo','keep':'keep'})
        edge = (eid,{'woot':'bar','keep':'keep'})

        g.addNode(node)
        g.addEdge(edge)

        self.assertEqual( g.getNodesByProp('woot')[0], node)
        self.assertEqual( g.getNodesByProp('woot',valu='foo')[0], node)

        self.assertEqual( g.getEdgesByProp('woot')[0], edge)
        self.assertEqual( g.getEdgesByProp('woot',valu='bar')[0], edge)

        g.setNodeProp(node,'woot','baz')
        g.setEdgeProp(edge,'woot','faz')

        self.assertEqual( g.getNodeById(nid)[1].get('woot'), 'baz' )
        self.assertEqual( g.getEdgeById(eid)[1].get('woot'), 'faz' )

        self.assertEqual( g.getNodesByProp('woot')[0], node)
        self.assertEqual( g.getEdgesByProp('woot')[0], edge)

        self.assertFalse( g.getNodesByProp('woot',valu='foo') )
        self.assertFalse( g.getEdgesByProp('woot',valu='bar') )
        self.assertEqual( g.getNodesByProp('woot',valu='baz')[0], node)
        self.assertEqual( g.getEdgesByProp('woot',valu='faz')[0], edge)

        self.assertEqual( g.getNodeById(nid), node)
        self.assertEqual( g.getEdgeById(eid), edge)

        g.delNodeProp(node,'woot')
        g.delEdgeProp(edge,'woot')

        self.assertIsNone( g.getNodeById(nid)[1].get('woot') )
        self.assertIsNone( g.getEdgeById(eid)[1].get('woot') )

        self.assertFalse( g.getNodesByProp('woot') )
        self.assertFalse( g.getEdgesByProp('woot') )
        self.assertFalse( g.getNodesByProp('woot',valu='baz') )
        self.assertFalse( g.getEdgesByProp('woot',valu='faz') )

        g.delNode(node)
        g.delEdge(edge)

        self.assertIsNone( g.getNodeById(nid) )
        self.assertIsNone( g.getEdgeById(eid) )

        self.assertFalse( g.getNodesByProp('keep') )
        self.assertFalse( g.getEdgesByProp('keep') )
        self.assertFalse( g.getNodesByProp('keep',valu='keep') )
        self.assertFalse( g.getEdgesByProp('keep',valu='keep') )

        g.synShutDown()

    def test_ram_index_uniq(self):

        g = v_s_ram.GraphStore()
        g.initNodeIndex('woot','uniq')

        node1 = (s_common.guid(), {'woot':'foo','size':1})
        node2 = (s_common.guid(), {'woot':'bar','size':2})
        node3 = (s_common.guid(), {'woot':'foo','size':3})

        g.addNode(node1)
        g.addNode(node2)

        self.assertRaises( v_common.IndexProtests, g.addNode, node3 )
        self.assertRaises( v_common.IndexProtests, g.setNodeProp, node2, 'woot', 'foo' )

        self.assertEqual( g.getNodesByProp('woot','foo',index='uniq')[0][0], node1[0] )
        self.assertEqual( g.getNodesByProp('woot','bar',index='uniq')[0][0], node2[0] )

