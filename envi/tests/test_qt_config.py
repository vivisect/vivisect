'''
Tests for envi.qt.config — EnviConfigBool, EnviConfigInt, EnviConfigString.
'''
import os
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from vqt.tests.qt_testbase import VQtTestCase
from envi.qt.config import EnviConfigBool, EnviConfigInt, EnviConfigString


class TestEnviConfigBool(VQtTestCase):

    def test_create_true(self):
        cfg = {}
        w = EnviConfigBool(cfg, 'flag', True)
        self.assertTrue(w.isChecked())

    def test_create_false(self):
        cfg = {}
        w = EnviConfigBool(cfg, 'flag', False)
        self.assertFalse(w.isChecked())

    def test_toggle_updates_config(self):
        cfg = {}
        w = EnviConfigBool(cfg, 'flag', False)
        w.setChecked(True)
        self.assertTrue(cfg['flag'])


class TestEnviConfigInt(VQtTestCase):

    def test_create(self):
        cfg = {}
        w = EnviConfigInt(cfg, 'count', 42)
        self.assertEqual(w.text(), '42')

    def test_create_large_shows_hex(self):
        cfg = {}
        w = EnviConfigInt(cfg, 'addr', 0x41414141)
        self.assertEqual(w.text(), '0x41414141')

    def test_parse_updates_config(self):
        cfg = {}
        w = EnviConfigInt(cfg, 'count', 0)
        w.setText('100')
        w.parseEnviValue()
        self.assertEqual(cfg['count'], 100)

    def test_parse_hex(self):
        cfg = {}
        w = EnviConfigInt(cfg, 'addr', 0)
        w.setText('0x1000')
        w.parseEnviValue()
        self.assertEqual(cfg['addr'], 0x1000)


class TestEnviConfigString(VQtTestCase):

    def test_create(self):
        cfg = {}
        w = EnviConfigString(cfg, 'name', 'hello')
        self.assertEqual(w.text(), 'hello')

    def test_parse_updates_config(self):
        cfg = {}
        w = EnviConfigString(cfg, 'name', '')
        w.setText('world')
        w.parseEnviValue()
        self.assertEqual(cfg['name'], 'world')


if __name__ == '__main__':
    unittest.main()
