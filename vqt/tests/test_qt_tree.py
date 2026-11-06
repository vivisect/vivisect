'''
Tests for vqt.tree — VQTreeItem, VQTreeModel, VQTreeView.
'''
import unittest

from PyQt6 import QtCore

from vqt.tree import VQTreeItem, VQTreeModel, VQTreeView
from vqt.tests.qt_testbase import VQtTestCase


class TestVQTreeItem(unittest.TestCase):

    def test_create(self):
        item = VQTreeItem(('a', 'b'), None)
        self.assertEqual(item.rowdata, ['a', 'b'])
        self.assertIsNone(item.parent)
        self.assertEqual(item.childCount(), 0)

    def test_append_child(self):
        root = VQTreeItem(('root',), None)
        child = root.append(('child1',))
        self.assertEqual(root.childCount(), 1)
        self.assertIs(child.parent, root)
        self.assertEqual(child.rowdata, ['child1'])

    def test_child_access(self):
        root = VQTreeItem(('root',), None)
        root.append(('a',))
        root.append(('b',))
        self.assertEqual(root.child(0).rowdata, ['a'])
        self.assertEqual(root.child(1).rowdata, ['b'])

    def test_data(self):
        item = VQTreeItem(('hello', 'world'), None)
        self.assertEqual(item.data(0), 'hello')
        self.assertEqual(item.data(1), 'world')
        self.assertIsNone(item.data(5))

    def test_column_count(self):
        item = VQTreeItem(('a', 'b', 'c'), None)
        self.assertEqual(item.columnCount(), 3)

    def test_row_number(self):
        root = VQTreeItem(('root',), None)
        root.append(('first',))
        root.append(('second',))
        self.assertEqual(root.child(0).row(), 0)
        self.assertEqual(root.child(1).row(), 1)

    def test_delete_child(self):
        root = VQTreeItem(('root',), None)
        root.append(('a',))
        root.append(('b',))
        removed = root.delete(['a'])
        self.assertEqual(root.childCount(), 1)
        self.assertEqual(removed.rowdata, ['a'])


class TestVQTreeModel(VQtTestCase):

    def test_create_default_columns(self):
        model = VQTreeModel()
        self.assertEqual(model.columnCount(), 2)

    def test_create_custom_columns(self):
        model = VQTreeModel(columns=('Name', 'Value', 'Type'))
        self.assertEqual(model.columnCount(), 3)

    def test_append_and_row_count(self):
        model = VQTreeModel(columns=('A', 'B'))
        self.assertEqual(model.rowCount(), 0)
        model.append(('val1', 'val2'))
        self.assertEqual(model.rowCount(), 1)
        model.append(('val3', 'val4'))
        self.assertEqual(model.rowCount(), 2)

    def test_data_display_role(self):
        model = VQTreeModel(columns=('A',))
        model.append(('hello',))
        idx = model.index(0, 0, QtCore.QModelIndex())
        val = model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertEqual(val, 'hello')

    def test_data_user_role(self):
        model = VQTreeModel(columns=('A',))
        node = model.append(('hello',))
        idx = model.index(0, 0, QtCore.QModelIndex())
        item = model.data(idx, QtCore.Qt.ItemDataRole.UserRole)
        self.assertIs(item, node)

    def test_header_data(self):
        model = VQTreeModel(columns=('Name', 'Value'))
        h = model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                             QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertEqual(h, 'Name')

    def test_sort(self):
        model = VQTreeModel(columns=('A',))
        model.append(('cherry',))
        model.append(('apple',))
        model.append(('banana',))
        model.sort(0, 0)  # ascending
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, QtCore.Qt.ItemDataRole.DisplayRole), 'apple')

    def test_flags_default_not_editable(self):
        model = VQTreeModel(columns=('A', 'B'))
        model.append(('x', 'y'))
        idx = model.index(0, 0, QtCore.QModelIndex())
        flags = model.flags(idx)
        self.assertFalse(flags & QtCore.Qt.ItemFlag.ItemIsEditable)

    def test_set_data(self):
        model = VQTreeModel(columns=('A',))
        model.editable = [True]
        node = model.append(('original',))
        idx = model.index(0, 0, QtCore.QModelIndex())
        model.setData(idx, 'modified', QtCore.Qt.ItemDataRole.EditRole)
        self.assertEqual(node.rowdata[0], 'modified')

    def test_nested_tree(self):
        model = VQTreeModel(columns=('Name',))
        parent_node = model.append(('parent',))
        model.append(('child',), parent=parent_node)
        self.assertEqual(parent_node.childCount(), 1)


class TestVQTreeView(VQtTestCase):

    def test_create_with_columns(self):
        view = VQTreeView(cols=('Col1', 'Col2'))
        self.assertTrue(view.isSortingEnabled())
        self.assertIsNotNone(view.model())
        self.assertEqual(view.model().columnCount(), 2)

    def test_create_without_columns(self):
        view = VQTreeView()
        self.assertIsNone(view.model())

    def test_append_via_model(self):
        view = VQTreeView(cols=('A', 'B'))
        model = view.model()
        model.append(('x', 'y'))
        self.assertEqual(model.rowCount(), 1)


if __name__ == '__main__':
    unittest.main()
