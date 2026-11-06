'''
Tests for vqt.saveable — SaveableWidget, compat_isNone.
'''
import unittest

from PyQt6 import QtCore

from vqt.saveable import SaveableWidget, compat_isNone
from vqt.tests.qt_testbase import VQtTestCase


class TestCompatIsNone(unittest.TestCase):

    def test_none(self):
        self.assertTrue(compat_isNone(None))

    def test_empty_bytearray(self):
        self.assertTrue(compat_isNone(QtCore.QByteArray()))

    def test_nonempty_bytearray(self):
        self.assertFalse(compat_isNone(QtCore.QByteArray(b'data')))

    def test_empty_string(self):
        self.assertTrue(compat_isNone(''))

    def test_nonempty_string(self):
        self.assertFalse(compat_isNone('hello'))

    def test_empty_list(self):
        self.assertTrue(compat_isNone([]))

    def test_nonempty_list(self):
        self.assertFalse(compat_isNone([1, 2]))


class MySaveable(SaveableWidget):
    def __init__(self):
        self.state = None

    def vqGetSaveState(self):
        return self.state

    def vqSetSaveState(self, state):
        self.state = state


class TestSaveableWidget(VQtTestCase):

    def test_default_state_is_none(self):
        w = SaveableWidget()
        self.assertIsNone(w.vqGetSaveState())

    def test_round_trip(self):
        w = MySaveable()
        w.state = {'key': 'value', 'num': 42}

        settings = QtCore.QSettings()
        w.vqSaveState(settings, 'testwidget')

        w2 = MySaveable()
        w2.vqRestoreState(settings, 'testwidget')
        self.assertEqual(w2.state, {'key': 'value', 'num': 42})

    def test_restore_missing_key(self):
        w = MySaveable()
        settings = QtCore.QSettings()
        w.vqRestoreState(settings, 'nonexistent_key_xyz')
        self.assertIsNone(w.state)


if __name__ == '__main__':
    unittest.main()
