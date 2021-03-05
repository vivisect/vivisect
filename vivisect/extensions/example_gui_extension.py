'''
This is an example of a vivisect GUI extension module.
Set the environment variable VIV_EXT_PATH to point at a
directory full of python modules such as this to extend
and implement your own vivisect features.

The extension should be a python module, either in the
form of a .py file or a directory with a __init__.py
file.  Either way, the module will be loaded into
memory and the "vivExtension" function called.
'''
from PyQt5.QtWidgets import QToolBar, QLabel, QPushButton, QTextEdit, QWidget, QInputDialog
from PyQt5 import QtCore

from vqt.main import idlethread
from vqt.basics import VBox
from vqt.common import ACT

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


def vprint(vw, s, *args, **kwargs):
    vw.vprint(s % args)
    print(s % args)


def ctxMenuHook(vw, va, expr, menu, parent, nav):
    '''
    Context Menu handler (adds options as we wish)
    '''
    try:
        if va == 0x41414141:
            menu.addAction('WAT?',   ACT(vw.vprint, "We're at AAAA!"))
        menu.addAction('bookmark (B)',   ACT(vw.getVivGui().addBookmark, va))
        menu.addAction('YEEE HAH',   ACT(vw.vprint, "YEE HAH %x  %r %r %r %r" % (va, expr, menu, parent, nav)))
        menu.addAction('YEEE HAH1',   ACT(vprint, vw, "YEE HAH %x  %r %r %r %r", va, expr, menu, parent, nav))

    except Exception as e:
        import traceback
        traceback.print_exc()


class Crap:
    '''
    This is a helpful class for storing vw and vwgui and "doing the thing"
    Currently Vivisect's Hot Keys are tied to the many gui widgets, so 
    vw and vwgui are not available when the "thing" is called.
    '''
    def __init__(self, vw, vwgui):
        self.vw = vw
        self.vwgui = vwgui

    def thing(self):
        vprint(self.vw, "Blah Blah Blah")

    def printUserInput(self):
        # ok is whether the "OK" button was pressed, utext is the user text
        utext, ok = QInputDialog.getText(self.vwgui, 'Enter...', 'User Text')
        vprint(self.vw, '%r:  %r', ok, utext)



@idlethread
def vivExtension(vw, vwgui):
    # Create a toolbar and add it to the GUI
    toolbar = ExampleToolbar(vw, vwgui)
    vwgui.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)

    # Create a new Vivisect Dock Window (based on a QWidget)
    window = ExampleWindow(vw, vwgui)
    d = vwgui.vqDockWidget(window, floating=True)
    d.resize(300,200)

    # Add a menu item
    vwgui.vqAddMenuField('&Example.&FooBar.&PrintDiscoveredStats', vw.printDiscoveredStats, ())

    # hook context menu
    vw.addCtxMenuHook('example', ctxMenuHook)

    # add HotKeyTargets and HotKeys
    tempmod = Crap(vw, vwgui)
    vwgui.addHotKey('ctrl+p', 'file:hackme')
    vwgui.addHotKeyTarget('file:hackme', tempmod.thing)

    # Popups/Dialogs - add a menu entry to ask for input and print the output
    vwgui.vqAddMenuField("&Example.&FooBar.&PrintUserInput", tempmod.printUserInput, ())

    # get Dock Windows by name
    for w, vqDW in vwgui.vqGetDockWidgetsByName('viv'):
        vprint(vw, "Window: %r    DockWidget: %r (%r)", w, vqDW, w.getEnviNavName())
