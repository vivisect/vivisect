'''
Some utilities for adding shortcut keys to widgets...
'''

from PyQt5 import QtCore, QtGui, QtWidgets

def addShortCut(widget, keycode, callback):
    if isinstance(keycode, str):
        keycode = ord(keycode)
    keyseq = QtGui.QKeySequence(keycode)
    short = QtWidgets.QShortcut(keyseq, widget)
    short.activated.connect(callback)

