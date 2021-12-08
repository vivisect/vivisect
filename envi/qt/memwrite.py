import string
import binascii

import envi.common as e_common
import envi.memory as e_memory
import envi.memcanvas as e_canvas
import envi.memcanvas.renderers as e_render

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *


class VQLineEdit(QLineEdit):
    '''
    Has an additional signal to emit a signal on release of every keypress.
    '''
    keyReleased = QtCore.pyqtSignal(QtGui.QKeyEvent)

    def keyReleaseEvent(self, event):
        self.keyReleased.emit(event)
        QLineEdit.keyReleaseEvent(self, event)


class MemNavWidget(QWidget):
    userChanged = QtCore.pyqtSignal(str, str)

    def __init__(self):
        QWidget.__init__(self)

        self.expr_entry = QLineEdit()
        self.esize_entry = QLineEdit()

        hbox1 = QHBoxLayout()
        hbox1.setContentsMargins(2, 2, 2, 2)
        hbox1.setSpacing(4)
        hbox1.addWidget(self.expr_entry)
        hbox1.addWidget(self.esize_entry)

        self.setLayout(hbox1)

        self.expr_entry.returnPressed.connect(self.emitUserChangedSignal)
        self.esize_entry.returnPressed.connect(self.emitUserChangedSignal)

    def emitUserChangedSignal(self):
        '''
        Emits signal when user manually enters new expressions in the expr or
        size field and presses enter.
        '''
        expr = str(self.expr_entry.text())
        size = str(self.esize_entry.text())
        self.userChanged.emit(expr, size)

    def setValues(self, expr, esize):
        '''
        Called externally to allow programmatic way to update the expr or size
        field. Does not emit the changed signal.
        '''
        self.expr_entry.setText(expr)
        self.esize_entry.setText(esize)

    def getValues(self):
        return str(self.expr_entry.text()), str(self.esize_entry.text())

class MemWriteWindow(QWidget):
    '''
    gui for writemem cli command.
    '''
    renderRequest = QtCore.pyqtSignal(str, str)

    # button to write memory was clicked (va, bytez)
    writeToMemory = QtCore.pyqtSignal(str, str)

    def __init__(self, expr='', esize='', emu=None, parent=None):
        QWidget.__init__(self, parent=parent)

        self.modes = ['ascii', 'hex', 'regex', 'utf-8', 'utf-16-le',
                        'utf-16-be']

        rend_orig = e_render.ByteRend()
        self.canvas_orig = e_canvas.StringMemoryCanvas(None)
        self.canvas_orig.addRenderer('bytes', rend_orig)

        rend_new = e_render.ByteRend()
        self.canvas_new = e_canvas.StringMemoryCanvas(None)
        self.canvas_new.addRenderer('bytes', rend_new)

        hbox1 = QHBoxLayout()
        self.nav = MemNavWidget()
        self.nav.userChanged.connect(self.renderMemory)
        self.renderRequest.connect(self.nav.setValues)
        hbox1.addWidget(self.nav)

        hbox2 = QHBoxLayout()
        self.hex_edit = QPlainTextEdit()
        self.hex_edit.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.hex_edit.setReadOnly(True)
        font = QtGui.QFont('Courier') # should use actual memcanvas
        self.hex_edit.setFont(font)
        hbox2.addWidget(self.hex_edit)

        vbox1 = QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        gbox1 = QGroupBox('Original Bytes')
        gbox1.setLayout(vbox1)

        hbox3 = QHBoxLayout()
        mode_label = QLabel('Input:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.modes)
        self.mode_combo.currentIndexChanged.connect(self.encodingChanged)
        hbox3.addWidget(mode_label)
        hbox3.addWidget(self.mode_combo, alignment=QtCore.Qt.AlignLeft)
        hbox3.addStretch(1)

        hbox4 = QHBoxLayout()
        data_label = QLabel('Bytes:')
        self.data_edit = VQLineEdit()
        self.data_edit.keyReleased.connect(self.keyReleasedSlot)
        hbox4.addWidget(data_label)
        hbox4.addWidget(self.data_edit)

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox3)
        vbox2.addLayout(hbox4)
        gbox2 = QGroupBox('New Bytes')
        gbox2.setLayout(vbox2)

        hbox5 = QHBoxLayout()
        self.hex_preview = QPlainTextEdit()
        self.hex_preview.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.hex_preview.setReadOnly(True)
        self.hex_preview.setFont(font)
        hbox5.addWidget(self.hex_preview)

        vbox3 = QVBoxLayout()
        vbox3.addLayout(hbox5)
        gbox3 = QGroupBox('Result Preview')
        gbox3.setLayout(vbox3)

        hbox6 = QHBoxLayout()
        button = QPushButton('Write Memory')
        button.clicked.connect(self.buttonClicked)
        hbox6.addWidget(button)

        vbox = QVBoxLayout()
        vbox.addWidget(gbox1)
        vbox.addWidget(gbox2)
        vbox.addWidget(gbox3)
        vbox.addLayout(hbox6)
        self.setLayout(vbox)

        self.setWindowTitle('Memory Write')
        self.resize(650, 500)
        self.data_edit.setFocus()
        self.emu = emu
        self.renderMemory(expr, esize)

    def renderMemory(self, expr=None, esize=None, emu=None):
        if emu is not None:
            self.emu = emu

        curexpr, cur_esize = self.nav.getValues()
        if expr is None:
            expr = curexpr
        if esize is None:
            esize = cur_esize

        self.renderRequest.emit(expr, esize)

        try:
            # str() for QString -> ascii strings
            va = self.emu.parseExpression(str(expr))
            size = self.emu.parseExpression(str(esize))
            bytez = self.emu.readMemory(va, size)

            self.updateHexOrig(va, bytez)

            encoding = str(self.mode_combo.currentText())
            rbytes = str(self.data_edit.text())
            erbytes = self.encodeData(rbytes, encoding)

            # encoded bytes is bigger than the amount we are displaying.
            if len(erbytes) > len(bytez):
                self.hex_preview.setPlainText('too many bytes, change size, encoding or input')
                return

            bytez = erbytes + bytez[len(erbytes):]
            self.updateHexPreview(va, bytez)
        except Exception as e:
            self.hex_preview.setPlainText(str(e))

    def keyReleasedSlot(self, event):
        encoding = self.mode_combo.currentText()
        self.encodingChanged(None)

    def encodingChanged(self, idx):
        encoding = str(self.mode_combo.currentText())

        validator = None
        if encoding == 'hex':
            # only clear the box if there are non-hex chars
            # before setting the validator.
            txt = str(self.data_edit.text())
            if not all(c in string.hexdigits for c in txt):
                self.data_edit.setText('')

            regex = QtCore.QRegExp('^[0-9A-Fa-f]+$')
            validator = QtGui.QRegExpValidator(regex)

        self.data_edit.setValidator(validator)

        self.renderMemory()

    def encodeData(self, txt, encoding):
        if encoding == 'hex' and (len(txt) % 2) != 0:
            txt = txt[:-1] # trim last if odd length

        if encoding == 'hex':
            if not all(c in string.hexdigits for c in txt):
                return None

            return txt.decode(encoding)

        elif encoding == 'regex':
            return None

        return txt.encode(encoding)

    def updateHexOrig(self, va, bytez):
        if bytez is None:
            self.hex_edit.setPlainText('')
            return

        self.canvas_orig.clearCanvas()
        mem = e_memory.MemoryObject()
        mem.addMemoryMap(va, e_memory.MM_READ, b'', bytez)
        self.canvas_orig.mem = mem
        self.canvas_orig.renderMemory(va, len(bytez))
        self.hex_edit.setPlainText(str(self.canvas_orig))

    def updateHexPreview(self, va, bytez):
        if bytez is None:
            self.hex_preview.setPlainText('')
            return

        self.canvas_new.clearCanvas()
        mem = e_memory.MemoryObject()
        mem.addMemoryMap(va, e_memory.MM_READ, b'', bytez)
        self.canvas_new.mem = mem
        self.canvas_new.renderMemory(va, len(bytez))
        self.hex_preview.setPlainText(str(self.canvas_new))

    def buttonClicked(self):
        curexpr, cur_esize = self.nav.getValues()
        encoding = str(self.mode_combo.currentText())
        rbytes = str(self.data_edit.text())
        erbytes = self.encodeData(rbytes, encoding)

        hexbytes = e_common.hexify(erbytes)
        self.writeToMemory.emit(curexpr, hexbytes)

    def getValues(self):
        return self.nav.getValues()

    def setValues(self, expr, esize):
        self.nav.setValues(expr, esize)

class MockEmu(object):
    def parseExpression(self, expr):
        return int(eval(expr, {}, {}))

    def readMemory(self, va, size):
        return '\x90' * size

def main():
    import sys

    app = QApplication([])
    w = MemWriteWindow('0x1234', '0xff', emu=MockEmu())
    w.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
