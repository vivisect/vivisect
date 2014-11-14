import os
from PyQt4 import QtCore, QtGui

import envi.cli as e_cli
import envi.qt.memory as e_q_memory
import envi.qt.memcanvas as e_q_memcanvas

#from envi.threads import firethread

import vqt.colors as vq_colors
import vqt.hotkeys as vq_hotkeys
#import vqt.shortcut as vq_shortcut

from vqt.basics import *
from vqt.main import idlethread,workthread

class VQInput(vq_hotkeys.HotKeyMixin, QtGui.QLineEdit):

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent=parent)
        vq_hotkeys.HotKeyMixin.__init__(self)

        self.history = []
        self.histidx = 0

        self.addHotKey('up','cli:history:prev')
        self.addHotKey('down','cli:history:next')

    def useHistory(self, delta):

        if delta < 0 and self.histidx == 0:
            return

        if delta > 0 and len(self.history) <= self.histidx+delta:
            self.histidx = len(self.history)
            self.clear()
            return

        self.histidx += delta
        htext = self.history[self.histidx]
        self.setText(htext)

    def addHistory(self, histcmd):
        if histcmd:
            self.history.append(histcmd)
            self.histidx = len(self.history)

    @vq_hotkeys.hotkey('cli:history:prev')
    def keyCodeUp(self,*args):
        self.useHistory(-1)

    @vq_hotkeys.hotkey('cli:history:next')
    def keyCodeDown(self):
        self.useHistory(1)

    def loadHistory(self, filename):
        if os.path.isfile(filename):
            hist = file(filename, 'r').readlines()[-1000:]
            self.history = [ x.strip() for x in hist ]
            self.histidx = len(self.history)

    def saveHistory(self, filename):
        histbuf = '\n'.join( self.history[-1000:] )
        file(filename, 'w').write( histbuf )


class VQCli(QtGui.QWidget):
    '''
    A Qt class to wrap and emulate a Cmd object.
    '''

    sigCliQuit = QtCore.pyqtSignal()

    def __init__(self, cli, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        self.cli = cli

        self.input = VQInput(self)

        # Create our output window...
        self.output = QtGui.QTextEdit(self)
        # If it's an EnviCli, let's over-ride the canvas right away.
        if isinstance(cli, e_cli.EnviCli):
            self.output.close()
            self.output = self.initMemoryCanvas(cli.memobj, syms=cli.symobj)
            self.output.setScrolledCanvas(True)
            cli.setCanvas(self.output)

        self.setStyleSheet( vq_colors.getDefaultColors() )

        self.setLayout( self.getCliLayout() )

        self.connect(self.input,  QtCore.SIGNAL('returnPressed()'), self.returnPressedSlot)

        #FIXME: these events should probably be made to work better with the new Qt Event model
        # perhaps this should inherit from HotKeyMixin as well?
        #vq_shortcut.addShortCut(self.input, QtCore.Qt.Key_Up, self.keyCodeUp)
        #vq_shortcut.addShortCut(self.input, QtCore.Qt.Key_Down, self.keyCodeDown)

        self.resize(250, 150)

    def initMemoryCanvas(self, memobj, syms=None):
        return e_q_memcanvas.VQMemoryCanvas(memobj, syms=syms, parent=self)

    def getCliLayout(self):
        return VBox( self.output, self.input )

    def returnPressedSlot(self):
        cmd = str(self.input.text())
        self.input.clear()
        self.input.addHistory(cmd)
        self.output.addText('> %s\n' % cmd)
        workthread(self.onecmd)(cmd)

    def onecmd(self, cmdline):
        if self.cli.onecmd( cmdline ):
            self._emit_quit()

    @idlethread
    def _emit_quit(self):
        # A way to emit the "quit" signal from threads other than the
        # qt main thread.
        self.sigCliQuit.emit()

