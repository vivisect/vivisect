'''
Tests for vqt.hotkeys — HotKeyMixin with synthesized key events.
'''
import unittest

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QEvent, Qt

from vqt.hotkeys import HotKeyMixin, QMOD_CTRL, QMOD_SHIFT, QMOD_META
from vqt.tests.qt_testbase import VQtTestCase


class HotKeyWidget(HotKeyMixin, QWidget):
    '''Minimal widget mixing in HotKeyMixin for testing.'''
    def __init__(self):
        QWidget.__init__(self)
        HotKeyMixin.__init__(self)
        self.fired = []

    def on_test(self):
        self.fired.append('test')

    def on_save(self):
        self.fired.append('save')


def _make_key_event(key, modifiers=Qt.KeyboardModifier.NoModifier):
    return QtGui.QKeyEvent(QEvent.Type.KeyPress, key, modifiers)


class TestHotKeyMixin(VQtTestCase):

    def test_add_target(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        self.assertIn('test', w.getHotKeyTargets())

    def test_add_hotkey(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        w.addHotKey('t', 'test')
        keys = dict(w.getHotKeys())
        self.assertEqual(keys['t'], 'test')

    def test_del_hotkey(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        w.addHotKey('t', 'test')
        w.delHotKey('t')
        keys = dict(w.getHotKeys())
        self.assertNotIn('t', keys)

    def test_is_hotkey_target(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        self.assertTrue(w.isHotKeyTarget('test'))
        self.assertFalse(w.isHotKeyTarget('nonexistent'))


class TestGetHotKeyFromEvent(VQtTestCase):

    def test_plain_letter(self):
        w = HotKeyWidget()
        event = _make_key_event(ord('A'))
        self.assertEqual(w.getHotKeyFromEvent(event), 'a')

    def test_shift_letter(self):
        w = HotKeyWidget()
        event = _make_key_event(ord('S'), Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(w.getHotKeyFromEvent(event), 'S')

    def test_ctrl_letter(self):
        w = HotKeyWidget()
        event = _make_key_event(ord('S'), Qt.KeyboardModifier.ControlModifier)
        self.assertEqual(w.getHotKeyFromEvent(event), 'ctrl+s')

    def test_ctrl_meta_letter(self):
        w = HotKeyWidget()
        mods = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier
        event = _make_key_event(ord('X'), mods)
        self.assertEqual(w.getHotKeyFromEvent(event), 'ctrl+meta+x')

    def test_escape_key(self):
        w = HotKeyWidget()
        event = _make_key_event(Qt.Key.Key_Escape)
        self.assertEqual(w.getHotKeyFromEvent(event), 'esc')

    def test_enter_key(self):
        w = HotKeyWidget()
        event = _make_key_event(Qt.Key.Key_Return)
        self.assertEqual(w.getHotKeyFromEvent(event), 'enter')

    def test_f1_key(self):
        w = HotKeyWidget()
        event = _make_key_event(Qt.Key.Key_F1)
        self.assertEqual(w.getHotKeyFromEvent(event), 'f1')

    def test_unknown_key(self):
        w = HotKeyWidget()
        event = _make_key_event(0x1ffffff)
        self.assertIsNone(w.getHotKeyFromEvent(event))


class TestEatKeyPressEvent(VQtTestCase):

    def test_hotkey_fires_callback(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        w.addHotKey('t', 'test')
        event = _make_key_event(ord('T'))
        self.assertTrue(w.eatKeyPressEvent(event))
        self.assertIn('test', w.fired)

    def test_unbound_key_not_eaten(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('test', w.on_test)
        event = _make_key_event(ord('X'))
        self.assertFalse(w.eatKeyPressEvent(event))
        self.assertEqual(w.fired, [])

    def test_ctrl_s_hotkey(self):
        w = HotKeyWidget()
        w.addHotKeyTarget('save', w.on_save)
        w.addHotKey('ctrl+s', 'save')
        event = _make_key_event(ord('S'), Qt.KeyboardModifier.ControlModifier)
        self.assertTrue(w.eatKeyPressEvent(event))
        self.assertIn('save', w.fired)


if __name__ == '__main__':
    unittest.main()
