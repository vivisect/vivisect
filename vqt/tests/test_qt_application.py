'''
Tests for vqt.application — VQDockWidget, dock options.
'''
import unittest

from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QLabel

from vqt.application import VQDockWidget
from vqt.tests.qt_testbase import VQtTestCase


class TestVQDockWidget(VQtTestCase):

    def test_create(self):
        parent = QMainWindow()
        dock = VQDockWidget(parent)
        self.assertIsNotNone(dock)
        areas = dock.allowedAreas()
        self.assertEqual(areas, QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)

    def test_set_widget_copies_title(self):
        parent = QMainWindow()
        dock = VQDockWidget(parent)
        child = QLabel('content')
        child.setWindowTitle('My Widget')
        dock.setWidget(child)
        self.assertEqual(dock.windowTitle(), 'My Widget')

    def test_hotkey_target_registered(self):
        parent = QMainWindow()
        dock = VQDockWidget(parent)
        self.assertTrue(dock.isHotKeyTarget('mem:undockmaximize'))

    def test_undock_maximize_toggle(self):
        parent = QMainWindow()
        parent.show()
        dock = VQDockWidget(parent)
        dock.setWidget(QLabel('test'))
        parent.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, dock)
        dock.show()

        self.assertFalse(dock.isFloating())
        dock._hotkey_undock_maximize()
        self.assertTrue(dock.isFloating())


class TestDockOptions(VQtTestCase):

    def test_dock_options_set(self):
        '''Verify scoped enum DockOption is accepted.'''
        win = QMainWindow()
        win.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks |
            QMainWindow.DockOption.AllowTabbedDocks
        )
        opts = win.dockOptions()
        self.assertTrue(opts & QMainWindow.DockOption.AnimatedDocks)
        self.assertTrue(opts & QMainWindow.DockOption.AllowTabbedDocks)


if __name__ == '__main__':
    unittest.main()
