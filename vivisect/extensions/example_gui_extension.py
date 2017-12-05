from PyQt5 import QtCore, QtGui, QtWidgets
from vqt.main import idlethread
from vqt.basics import VBox

'''
This is an example of a vivisect GUI extension module.
Set the environment variable VIV_EXT_PATH to point at a
directory full of python modules such as this to extend
and implement your own vivisect features.
'''

class ExampleToolbar(QtWidgets.QToolBar):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QtWidgets.QToolBar.__init__(self, parent=vwgui)
        self.addWidget( QtWidgets.QLabel('Example Toolbar:', parent=self) )
        self.addAction('ONE', self.doOne)

    def doOne(self):
        self.vw.vprint('did one!')

class ExampleWindow(QtWidgets.QWidget):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QtWidgets.QWidget.__init__(self, parent=vwgui)
        self.setWindowTitle('Example Window!')
        button = QtWidgets.QPushButton('My Button!', parent=self)
        textedit = QtWidgets.QTextEdit('WOOT! Some text!', parent=self)
        self.setLayout( VBox(button, textedit) )

@idlethread
def vivExtension(vw, vwgui):
    toolbar = ExampleToolbar(vw, vwgui)
    vwgui.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    window = ExampleWindow(vw, vwgui)
    d = vwgui.vqDockWidget(window, floating=True)
    d.resize(300,200)
