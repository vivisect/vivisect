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

The extension should be a python module, either in the 
form of a .py file or a directory with a __init__.py
file.  Either way, the module will be loaded into 
memory and the "vivExtension" function called.

After vivExtention() is executed, the file will be 
discarded from memory, so any hooks into the VivWorkspace
or VivGui should be from a supporting module imported
here.
'''

class ExampleToolbar(QToolBar):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QToolBar.__init__(self, parent=vwgui)
        # Add a label to the toolbar
        self.addWidget( QLabel('Example Toolbar:', parent=self) )

        # Add an action button to the toolbar
        self.addAction('ONE', self.doOne)

    def doOne(self):
        self.vw.vprint('did one!')

class ExampleWindow(QWidget):
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

        QWidget.__init__(self, parent=vwgui)

        # Set the window title
        self.setWindowTitle('Example Window!')

        # Add a Button and a Text Edit object in a basic VBox layout
        button = QPushButton('My Button!', parent=self)
        textedit = QTextEdit('WOOT! Some text!', parent=self)
        self.setLayout( VBox(button, textedit) )

@idlethread
def vivExtension(vw, vwgui):
    # Create a toolbar and add it to the GUI
    toolbar = ExampleToolbar(vw, vwgui)
    vwgui.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    # Create a new Vivisect Dock Window (based on a QWidget)
    window = ExampleWindow(vw, vwgui)
    d = vwgui.vqDockWidget(window, floating=True)
    d.resize(300,200)
