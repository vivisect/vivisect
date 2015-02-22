import unittest

import vertex.model as v_model

class ModelTest(unittest.TestCase):

    def test_model_basic(self):
        g = v_model.GraphModel()
        self.assertRaises( v_model.DataModelProtests, g.formNodeByNoun, 'woot', 'foo' )

        g.initModelNoun('woot')
        g.initModelProp('lol',indexes=['keyval'])

        g.bumpDataModel()

        props = {'woot:test':33,'vanish':3}
        node1 = g.formNodeByNoun('woot','foo',**props)
        node2 = g.formNodeByNoun('woot','bar')

        self.assertEqual( node1[1].get('woot:test'), 33 )
        self.assertIsNone( node1[1].get('vanish') )

        g.setNodeProp(node1,'lol','hehe')
        g.setNodeProp(node2,'lol','haha')

        self.assertEqual( len( g.getNodesByProp('lol') ), 2 )
        self.assertEqual( len( g.getNodesByProp('lol', valu='hehe') ), 1 )
        self.assertEqual( len( g.getNodesByProp('lol', valu='haha') ), 1 )

        # since it's a ram graph, we should get the same instance back
        self.assertEqual( id(node1), id(g.formNodeByNoun('woot','foo')) )
