from PyQt4 import QtGui,QtCore
from vqt.main import idlethread
from vqt.basics import VBox

'''
This is an example of a vivisect GUI extension module.
Set the environment variable VIV_EXT_PATH to point at a
directory full of python modules such as this to extend
and implement your own vivisect features.
'''

class ExampleToolbar(QtGui.QToolBar):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QtGui.QToolBar.__init__(self, parent=vwgui)
        self.addWidget( QtGui.QLabel('Example Toolbar:', parent=self) )
        self.addAction('ONE', self.doOne)

    def doOne(self):
        self.vw.vprint('did one!')

class ExampleWindow(QtGui.QWidget):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QtGui.QWidget.__init__(self, parent=vwgui)
        self.setWindowTitle('Example Window!')
        button = QtGui.QPushButton('My Button!', parent=self)
        textedit = QtGui.QTextEdit('WOOT! Some text!', parent=self)
        self.setLayout( VBox(button, textedit) )

@idlethread
def vivExtension(vw, vwgui):
    toolbar = ExampleToolbar(vw, vwgui)
    vwgui.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    window = ExampleWindow(vw, vwgui)
    d = vwgui.vqDockWidget(window, floating=True)
    d.resize(300,200)
