'''
Some utilities for adding shortcut keys to widgets...
'''

from PyQt4 import QtCore, QtGui

def addShortCut(widget, keycode, callback):
    if isinstance(keycode, str):
        keycode = ord(keycode)
    keyseq = QtGui.QKeySequence(keycode)
    short = QtGui.QShortcut(keyseq, widget)
    widget.connect(short, QtCore.SIGNAL('activated()'), callback)

