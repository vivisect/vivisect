'''
Tests for vqt.basics — BasicModel, BasicTreeView, VBox, HBox, ACT.
'''
import unittest

from PyQt6 import QtCore
from PyQt6.QtWidgets import QLabel

from vqt.basics import BasicModel, BasicTreeView, VBox, HBox, ACT
from vqt.tests.qt_testbase import VQtTestCase


class TestBasicModel(VQtTestCase):

    def test_create_empty(self):
        model = BasicModel()
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 0)
        self.assertEqual(model.columnCount(QtCore.QModelIndex()), 2)

    def test_create_with_rows(self):
        rows = [('a', '1'), ('b', '2'), ('c', '3')]
        model = BasicModel(rows=rows)
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 3)

    def test_data_display_role(self):
        rows = [('hello', 'world')]
        model = BasicModel(rows=rows)
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, 0), 'hello')
        idx = model.index(0, 1, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, 0), 'world')

    def test_data_non_display_role(self):
        rows = [('a', 'b')]
        model = BasicModel(rows=rows)
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertIsNone(model.data(idx, 1))

    def test_header_data(self):
        model = BasicModel()
        h = model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                             QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertEqual(h, 'one')
        h = model.headerData(1, QtCore.Qt.Orientation.Horizontal,
                             QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertEqual(h, 'two')

    def test_header_data_wrong_role(self):
        model = BasicModel()
        h = model.headerData(0, QtCore.Qt.Orientation.Vertical,
                             QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertIsNone(h)

    def test_sort_ascending(self):
        rows = [('c', '3'), ('a', '1'), ('b', '2')]
        model = BasicModel(rows=rows)
        model.sort(0, QtCore.Qt.SortOrder.AscendingOrder)
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, 0), 'a')

    def test_sort_descending(self):
        rows = [('a', '1'), ('b', '2'), ('c', '3')]
        model = BasicModel(rows=rows)
        model.sort(0, QtCore.Qt.SortOrder.DescendingOrder)
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, 0), 'c')

    def test_parent_always_invalid(self):
        model = BasicModel(rows=[('x', 'y')])
        idx = model.index(0, 0, QtCore.QModelIndex())
        parent = model.parent(idx)
        self.assertFalse(parent.isValid())


class TestBasicTreeView(VQtTestCase):

    def test_create(self):
        view = BasicTreeView()
        self.assertTrue(view.isSortingEnabled())
        self.assertTrue(view.alternatingRowColors())

    def test_set_model(self):
        view = BasicTreeView()
        model = BasicModel(rows=[('a', 'b'), ('c', 'd')])
        view.setModel(model)
        self.assertIs(view.model(), model)


class TestLayouts(VQtTestCase):

    def test_vbox(self):
        layout = VBox(QLabel('one'), QLabel('two'))
        self.assertEqual(layout.count(), 2)

    def test_vbox_with_stretch(self):
        layout = VBox(QLabel('one'), None, QLabel('two'))
        # 2 widgets + 1 stretch = 3 items
        self.assertEqual(layout.count(), 3)

    def test_hbox(self):
        layout = HBox(QLabel('one'), QLabel('two'))
        self.assertEqual(layout.count(), 2)


class TestACT(VQtTestCase):

    def test_act_call(self):
        results = []
        act = ACT(lambda x, y: results.append(x + y), 3, 4)
        act()
        self.assertEqual(results, [7])

    def test_act_with_kwargs(self):
        results = []
        def cb(x, key=None):
            results.append((x, key))
        act = ACT(cb, 1, key='val')
        act()
        self.assertEqual(results, [(1, 'val')])


if __name__ == '__main__':
    unittest.main()
