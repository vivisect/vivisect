'''
Some utilities for adding shortcut keys to widgets...
'''
try:
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QShortcut
except:
    from PyQt4 import QtGui
    from PyQt4.QtGui import QShortcut

def addShortCut(widget, keycode, callback):
    if isinstance(keycode, str):
        keycode = ord(keycode)
    keyseq = QtGui.QKeySequence(keycode)
    short = QShortcut(keyseq, widget)
    short.activated.connect(callback)

