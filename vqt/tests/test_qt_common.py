'''
Tests for vqt.common — VqtModel, VqtView, DynamicDialog, ACT.
'''
import unittest

from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialogButtonBox

from vqt.common import ACT, VqtModel, VqtView, DynamicDialog
from vqt.tests.qt_testbase import VQtTestCase


class TestACT(VQtTestCase):

    def test_basic_call(self):
        results = []
        act = ACT(lambda: results.append(1))
        act()
        self.assertEqual(results, [1])

    def test_with_args(self):
        results = []
        act = ACT(results.append, 42)
        act()
        self.assertEqual(results, [42])

    def test_exception_handled(self):
        act = ACT(lambda: 1 / 0)
        act()  # should not raise


class TestVqtModel(VQtTestCase):

    def test_create_empty(self):
        model = VqtModel()
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 0)
        self.assertEqual(model.columnCount(QtCore.QModelIndex()), 2)

    def test_create_with_rows(self):
        model = VqtModel(rows=[('a', 'b'), ('c', 'd')])
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 2)

    def test_rows_are_lists(self):
        model = VqtModel(rows=[('a', 'b')])
        self.assertIsInstance(model.rows[0], list)

    def test_append(self):
        model = VqtModel()
        model.append(('x', 'y'))
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 1)

    def test_pop(self):
        model = VqtModel(rows=[('a', 'b'), ('c', 'd')])
        model.pop(0)
        self.assertEqual(model.rowCount(QtCore.QModelIndex()), 1)

    def test_data(self):
        model = VqtModel(rows=[('hello', 'world')])
        idx = model.index(0, 0, QtCore.QModelIndex())
        self.assertEqual(model.data(idx, 0), 'hello')

    def test_header_data(self):
        model = VqtModel()
        h = model.headerData(0, QtCore.Qt.Orientation.Horizontal,
                             QtCore.Qt.ItemDataRole.DisplayRole)
        self.assertEqual(h, 'one')

    def test_flags_not_editable_by_default(self):
        model = VqtModel(rows=[('a', 'b')])
        idx = model.index(0, 0, QtCore.QModelIndex())
        flags = model.flags(idx)
        self.assertFalse(flags & QtCore.Qt.ItemFlag.ItemIsEditable)

    def test_flags_editable(self):
        model = VqtModel(rows=[('a', 'b')])
        model.editable = [True, False]
        idx = model.index(0, 0, QtCore.QModelIndex())
        flags = model.flags(idx)
        self.assertTrue(flags & QtCore.Qt.ItemFlag.ItemIsEditable)


class TestVqtView(VQtTestCase):

    def test_create(self):
        view = VqtView()
        self.assertTrue(view.isSortingEnabled())
        self.assertTrue(view.alternatingRowColors())

    def test_set_model_wraps_in_proxy(self):
        view = VqtView()
        model = VqtModel(rows=[('a', 'b')])
        view.setModel(model)
        proxy = view.model()
        self.assertIsNot(proxy, model)
        self.assertIs(proxy.sourceModel(), model)

    def test_get_model_rows(self):
        view = VqtView()
        model = VqtModel(rows=[('a', 'b'), ('c', 'd')])
        view.setModel(model)
        self.assertEqual(len(view.getModelRows()), 2)


class TestDynamicDialog(VQtTestCase):

    def test_create(self):
        dlg = DynamicDialog('Test')
        self.assertEqual(dlg.windowTitle(), 'Test')

    def test_add_text_field(self):
        dlg = DynamicDialog('Test')
        dlg.addTextField('name', dflt='hello')
        self.assertIn('name', dlg.items)
        ftype, widget = dlg.items['name']
        self.assertEqual(ftype, DynamicDialog._TEXT)
        self.assertEqual(widget.text(), 'hello')

    def test_add_combo_box(self):
        dlg = DynamicDialog('Test')
        dlg.addComboBox('choice', ['opt1', 'opt2', 'opt3'], dfltidx=1)
        self.assertIn('choice', dlg.items)
        ftype, widget = dlg.items['choice']
        self.assertEqual(ftype, DynamicDialog._COMBO)
        self.assertEqual(widget.currentText(), 'opt2')

    def test_add_int_hex_field(self):
        dlg = DynamicDialog('Test')
        dlg.addIntHexField('addr', dflt=0x1000)
        self.assertIn('addr', dlg.items)
        ftype, widget = dlg.items['addr']
        self.assertEqual(ftype, DynamicDialog._INTHEX)

    def test_duplicate_field_raises(self):
        dlg = DynamicDialog('Test')
        dlg.addTextField('name')
        with self.assertRaises(Exception):
            dlg.addTextField('name')

    def test_combo_duplicate_raises(self):
        dlg = DynamicDialog('Test')
        dlg.addComboBox('x', ['a', 'b'])
        with self.assertRaises(Exception):
            dlg.addComboBox('x', ['c', 'd'])

    def test_inthex_duplicate_raises(self):
        dlg = DynamicDialog('Test')
        dlg.addIntHexField('x')
        with self.assertRaises(Exception):
            dlg.addIntHexField('x')

    def test_button_box_has_ok_cancel(self):
        dlg = DynamicDialog('Test')
        bb = dlg.buttonBox
        self.assertIsNotNone(bb.button(QDialogButtonBox.StandardButton.Ok))
        self.assertIsNotNone(bb.button(QDialogButtonBox.StandardButton.Cancel))


if __name__ == '__main__':
    unittest.main()
