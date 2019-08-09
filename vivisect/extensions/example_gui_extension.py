try:
    from PyQt5.QtWidgets import QToolBar, QLabel, QPushButton, QTextEdit
except:
    from PyQt4.QtGui import QToolBar, QLabel, QPushButton, QTextEdit

from vqt.main import idlethread
from vqt.basics import VBox

'''
This is an example of a vivisect GUI extension module.
Set the environment variable VIV_EXT_PATH to point at a
directory full of python modules such as this to extend
and implement your own vivisect features.
'''

class ExampleToolbar(QToolBar):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QToolBar.__init__(self, parent=vwgui)
        self.addWidget( QLabel('Example Toolbar:', parent=self) )
        self.addAction('ONE', self.doOne)

    def doOne(self):
        self.vw.vprint('did one!')

class ExampleWindow(QWidget):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QWidget.__init__(self, parent=vwgui)
        self.setWindowTitle('Example Window!')
        button = QPushButton('My Button!', parent=self)
        textedit = QTextEdit('WOOT! Some text!', parent=self)
        self.setLayout( VBox(button, textedit) )

def earlyLoad(vw):
    vw.vprint('hook immediately after workspace creation')

def preFileLoadHook(vw, fname, bytez, fd):
    '''
    this hook is called just before parseFrom(Fd, File, Memory).

    NOTE:
    vw will always be the Viv Workspace, but the other args can all be None.
    parseFromFd will only include the fname and fd.
    parseFromFile will only include fname
    parseFromMemory will only include fname and bytez.
    '''
    vw.vprint('preFileLoadHook(vw, %r, %s..., %r)' % fname, repr(bytez)[:20], fd)

@idlethread
def vivExtension(vw, vwgui):
    toolbar = ExampleToolbar(vw, vwgui)
    vwgui.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    window = ExampleWindow(vw, vwgui)
    d = vwgui.vqDockWidget(window, floating=True)
    d.resize(300,200)
