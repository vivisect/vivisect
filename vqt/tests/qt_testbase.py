'''
Base class for headless PyQt6 unit tests.

Sets QT_QPA_PLATFORM=offscreen and provides a shared QApplication
instance for all test cases.

Usage:
    QT_QPA_PLATFORM=offscreen python -m unittest discover -v

Or use run_gui_tests.sh which sets the env var for you.
'''
import os
import sys
import unittest

# Force offscreen rendering before any Qt imports
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt6.QtWidgets import QApplication

# Singleton QApplication — PyQt6 requires exactly one per process
_qapp = None

def get_qapp():
    global _qapp
    if _qapp is None:
        _qapp = QApplication.instance()
        if _qapp is None:
            _qapp = QApplication(sys.argv)
    return _qapp


class VQtTestCase(unittest.TestCase):
    '''
    Base test case that ensures a QApplication exists and pumps
    the event loop around each test.
    '''

    @classmethod
    def setUpClass(cls):
        cls.qapp = get_qapp()

    def setUp(self):
        self.qapp.processEvents()

    def tearDown(self):
        self.qapp.processEvents()
