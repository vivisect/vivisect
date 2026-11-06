'''
Tests for visgraph.renderers — Qt-based graph rendering widgets.
'''
import os
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from vqt.tests.qt_testbase import VQtTestCase
import visgraph.graphcore as vg_graphcore


class TestQGraphTreeImport(VQtTestCase):

    def test_import_qgraphtree(self):
        import visgraph.renderers.qgraphtree as qgt
        self.assertTrue(hasattr(qgt, 'QGraphTreeView'))

    def test_import_qtrend(self):
        import visgraph.renderers.qtrend as qtr
        self.assertTrue(hasattr(qtr, 'QtGraphRenderer'))


class TestGraphCoreWithRenderers(VQtTestCase):

    def test_create_graph(self):
        g = vg_graphcore.Graph()
        g.addNode(nid='node1', ninfo={'name': 'A'})
        g.addNode(nid='node2', ninfo={'name': 'B'})
        g.addEdge('node1', 'node2', eid='e1')
        self.assertIsNotNone(g.getNode('node1'))
        self.assertIsNotNone(g.getNode('node2'))


if __name__ == '__main__':
    unittest.main()
