'''
Regression tests for the PyQt5 → PyQt6 enum migration.

Verifies that all scoped enum patterns used throughout the codebase
actually resolve correctly at runtime.
'''
import unittest

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QMessageBox, QDialog,
    QDialogButtonBox, QSplitter, QTreeView, QWidget,
)
from PyQt6.QtCore import Qt, QEvent

from vqt.tests.qt_testbase import VQtTestCase


class TestQtNamespaceEnums(VQtTestCase):

    def test_dock_widget_areas(self):
        self.assertIsNotNone(Qt.DockWidgetArea.TopDockWidgetArea)
        self.assertIsNotNone(Qt.DockWidgetArea.RightDockWidgetArea)
        self.assertIsNotNone(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.assertIsNotNone(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.assertIsNotNone(Qt.DockWidgetArea.AllDockWidgetAreas)

    def test_orientation(self):
        s = QSplitter(Qt.Orientation.Horizontal)
        self.assertEqual(s.orientation(), Qt.Orientation.Horizontal)
        s.setOrientation(Qt.Orientation.Vertical)
        self.assertEqual(s.orientation(), Qt.Orientation.Vertical)

    def test_item_data_role(self):
        self.assertIsNotNone(Qt.ItemDataRole.DisplayRole)
        self.assertIsNotNone(Qt.ItemDataRole.UserRole)
        self.assertIsNotNone(Qt.ItemDataRole.EditRole)

    def test_item_flags(self):
        self.assertIsNotNone(Qt.ItemFlag.ItemIsEditable)
        self.assertIsNotNone(Qt.ItemFlag.ItemIsSelectable)
        self.assertIsNotNone(Qt.ItemFlag.ItemIsEnabled)
        self.assertIsNotNone(Qt.ItemFlag.ItemIsDragEnabled)

    def test_sort_order(self):
        self.assertIsNotNone(Qt.SortOrder.AscendingOrder)
        self.assertIsNotNone(Qt.SortOrder.DescendingOrder)

    def test_alignment_flag(self):
        self.assertIsNotNone(Qt.AlignmentFlag.AlignLeft)
        self.assertIsNotNone(Qt.AlignmentFlag.AlignRight)
        self.assertIsNotNone(Qt.AlignmentFlag.AlignCenter)
        self.assertIsNotNone(Qt.AlignmentFlag.AlignTop)

    def test_check_state(self):
        self.assertIsNotNone(Qt.CheckState.Checked)
        self.assertIsNotNone(Qt.CheckState.Unchecked)

    def test_keyboard_modifier(self):
        self.assertIsNotNone(Qt.KeyboardModifier.ShiftModifier)
        self.assertIsNotNone(Qt.KeyboardModifier.ControlModifier)
        self.assertIsNotNone(Qt.KeyboardModifier.MetaModifier)
        self.assertIsNotNone(Qt.KeyboardModifier.NoModifier)

    def test_mouse_button(self):
        self.assertIsNotNone(Qt.MouseButton.LeftButton)
        self.assertIsNotNone(Qt.MouseButton.RightButton)

    def test_drop_action(self):
        self.assertIsNotNone(Qt.DropAction.CopyAction)
        self.assertIsNotNone(Qt.DropAction.MoveAction)

    def test_window_state(self):
        self.assertIsNotNone(Qt.WindowState.WindowNoState)
        self.assertIsNotNone(Qt.WindowState.WindowFullScreen)
        self.assertIsNotNone(Qt.WindowState.WindowMaximized)

    def test_shortcut_context(self):
        self.assertIsNotNone(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.assertIsNotNone(Qt.ShortcutContext.WindowShortcut)

    def test_toolbar_area(self):
        self.assertIsNotNone(Qt.ToolBarArea.TopToolBarArea)
        self.assertIsNotNone(Qt.ToolBarArea.BottomToolBarArea)


class TestQEventEnums(VQtTestCase):

    def test_event_types(self):
        self.assertIsNotNone(QEvent.Type.ChildAdded)
        self.assertIsNotNone(QEvent.Type.ChildRemoved)
        self.assertIsNotNone(QEvent.Type.Wheel)
        self.assertIsNotNone(QEvent.Type.MouseMove)
        self.assertIsNotNone(QEvent.Type.KeyPress)


class TestWidgetEnums(VQtTestCase):

    def test_messagebox_icon(self):
        self.assertIsNotNone(QMessageBox.Icon.Warning)
        self.assertIsNotNone(QMessageBox.Icon.Information)
        self.assertIsNotNone(QMessageBox.Icon.Critical)

    def test_messagebox_buttons(self):
        self.assertIsNotNone(QMessageBox.StandardButton.Ok)
        self.assertIsNotNone(QMessageBox.StandardButton.Cancel)
        self.assertIsNotNone(QMessageBox.StandardButton.Yes)
        self.assertIsNotNone(QMessageBox.StandardButton.No)

    def test_dialog_code(self):
        self.assertIsNotNone(QDialog.DialogCode.Accepted)
        self.assertIsNotNone(QDialog.DialogCode.Rejected)

    def test_dialog_button_box(self):
        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.assertIsNotNone(bb.button(QDialogButtonBox.StandardButton.Ok))
        self.assertIsNotNone(bb.button(QDialogButtonBox.StandardButton.Cancel))

    def test_mainwindow_dock_options(self):
        self.assertIsNotNone(QMainWindow.DockOption.AnimatedDocks)
        self.assertIsNotNone(QMainWindow.DockOption.AllowTabbedDocks)
        self.assertIsNotNone(QMainWindow.DockOption.AllowNestedDocks)


class TestQFontEnums(VQtTestCase):

    def test_font_weight(self):
        self.assertIsNotNone(QtGui.QFont.Weight.Normal)
        self.assertIsNotNone(QtGui.QFont.Weight.Bold)


class TestQTextOptionEnums(VQtTestCase):

    def test_wrap_mode(self):
        self.assertIsNotNone(QtGui.QTextOption.WrapMode.NoWrap)
        self.assertIsNotNone(QtGui.QTextOption.WrapMode.WrapAnywhere)


class TestQSettingsEnums(VQtTestCase):

    def test_format(self):
        self.assertIsNotNone(QtCore.QSettings.Format.IniFormat)
        self.assertIsNotNone(QtCore.QSettings.Format.NativeFormat)


class TestQEventLoopEnums(VQtTestCase):

    def test_process_events_flag(self):
        self.assertIsNotNone(QtCore.QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)


class TestModifierIntConversion(VQtTestCase):
    '''Verify that .value works for bitwise comparisons (the hotkeys fix).'''

    def test_no_modifier_value(self):
        val = Qt.KeyboardModifier.NoModifier.value
        self.assertIsInstance(val, int)
        self.assertEqual(val, 0)

    def test_shift_modifier_value(self):
        val = Qt.KeyboardModifier.ShiftModifier.value
        self.assertIsInstance(val, int)
        from vqt.hotkeys import QMOD_SHIFT
        self.assertEqual(val, QMOD_SHIFT)

    def test_control_modifier_value(self):
        val = Qt.KeyboardModifier.ControlModifier.value
        self.assertIsInstance(val, int)
        from vqt.hotkeys import QMOD_CTRL
        self.assertEqual(val, QMOD_CTRL)

    def test_meta_modifier_value(self):
        val = Qt.KeyboardModifier.MetaModifier.value
        self.assertIsInstance(val, int)
        from vqt.hotkeys import QMOD_META
        self.assertEqual(val, QMOD_META)

    def test_modifier_from_key_event(self):
        event = QtGui.QKeyEvent(
            QEvent.Type.KeyPress, ord('S'),
            Qt.KeyboardModifier.ControlModifier
        )
        mods = event.modifiers().value
        self.assertIsInstance(mods, int)
        from vqt.hotkeys import QMOD_CTRL
        self.assertTrue(mods & QMOD_CTRL)


class TestQActionImportLocation(VQtTestCase):
    '''QAction moved from QtWidgets to QtGui in PyQt6.'''

    def test_qaction_from_qtgui(self):
        from PyQt6.QtGui import QAction
        action = QAction('test')
        self.assertEqual(action.text(), 'test')

    def test_qshortcut_from_qtgui(self):
        from PyQt6.QtGui import QShortcut
        w = QWidget()
        sc = QShortcut(QtGui.QKeySequence('Ctrl+T'), w)
        self.assertIsNotNone(sc)


class TestContextMenuVsMouseEvent(VQtTestCase):
    '''contextMenuEvent receives QContextMenuEvent which uses globalPos(),
       NOT globalPosition() (which is QMouseEvent-only in PyQt6).'''

    def test_context_menu_event_has_globalPos(self):
        from PyQt6.QtGui import QContextMenuEvent
        evt = QContextMenuEvent(
            QContextMenuEvent.Reason.Mouse,
            QtCore.QPoint(10, 20),
            QtCore.QPoint(100, 200),
        )
        pos = evt.globalPos()
        self.assertEqual(pos.x(), 100)
        self.assertEqual(pos.y(), 200)

    def test_context_menu_event_no_globalPosition(self):
        from PyQt6.QtGui import QContextMenuEvent
        evt = QContextMenuEvent(
            QContextMenuEvent.Reason.Mouse,
            QtCore.QPoint(10, 20),
            QtCore.QPoint(100, 200),
        )
        self.assertFalse(hasattr(evt, 'globalPosition'))


if __name__ == '__main__':
    unittest.main()
