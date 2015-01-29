import string

import envi.memory as e_mem
import envi.memcanvas as e_canvas
import envi.memcanvas.renderers as e_render

from PyQt4 import QtGui, QtCore

class MemSearchDialog(QtGui.QDialog):
    '''
    gui for search cli command.
    '''
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.modes = ['ascii', 'hex', 'regex', 'utf-8', 'utf-16-le',
                        'utf-16-be']
        self.pattern = None
        self.filename = None

        rend = e_render.ByteRend()
        self.canvas = e_canvas.StringMemoryCanvas(None)
        self.canvas.addRenderer('bytes', rend)

        hbox1 = QtGui.QHBoxLayout()
        mode_label = QtGui.QLabel('Input: ')
        self.mode_combo = QtGui.QComboBox()
        self.mode_combo.addItems(self.modes)
        self.mode_combo.currentIndexChanged.connect(self.encodingChanged)
        hbox1.addWidget(mode_label)
        hbox1.addWidget(self.mode_combo, alignment=QtCore.Qt.AlignLeft)
        hbox1.addStretch(1)

        hbox2 = QtGui.QHBoxLayout()
        data_label = QtGui.QLabel('Bytes: ')
        self.data_edit = QtGui.QLineEdit()
        hbox2.addWidget(data_label)
        hbox2.addWidget(self.data_edit)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)

        gbox1 = QtGui.QGroupBox('Search Criteria')
        gbox1.setLayout(vbox1)

        hbox3 = QtGui.QHBoxLayout()
        vbox_hex_label = QtGui.QVBoxLayout() # for align to top.
        hex_label = QtGui.QLabel('Hex:   ')
        vbox_hex_label.addWidget(hex_label, alignment=QtCore.Qt.AlignTop)
        self.hex_edit = QtGui.QPlainTextEdit()
        self.hex_edit.setReadOnly(True)
        font = QtGui.QFont('Courier') # should use actual memcanvas.
        self.hex_edit.setFont(font)
        hbox3.addLayout(vbox_hex_label)
        hbox3.addWidget(self.hex_edit)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addLayout(hbox3)

        gbox2 = QtGui.QGroupBox('Bytes to Search For')
        gbox2.setLayout(vbox2)

        hbox4 = QtGui.QHBoxLayout()
        save_check = QtGui.QCheckBox('Save Search Results')
        save_check.stateChanged.connect(self.checkChanged)
        self.fname_label = QtGui.QLabel('')
        buttons = QtGui.QDialogButtonBox()
        buttons.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.okClicked)
        buttons.rejected.connect(self.cancelClicked)
        hbox4.addWidget(save_check)
        hbox4.addWidget(self.fname_label)
        hbox4.addWidget(buttons)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(gbox1)
        vbox.addWidget(gbox2)
        vbox.addLayout(hbox4)

        self.setLayout(vbox)

        self.setWindowTitle('Memory Search')
        self.resize(650, 300)
        self.data_edit.setFocus()

    def keyReleaseEvent(self, event):
        encoding = self.mode_combo.currentText()
        self.encodingChanged(None)

    def checkChanged(self, state):
        if state == QtCore.Qt.Checked:
            self.showSaveAsDialog()
        else:
            self.fname_label.setText('')

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

        txt = str(self.data_edit.text())
        txt_encoded = self.encodeData(txt, encoding)
        self.updateHexPreview(txt_encoded)

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

    def updateHexPreview(self, bytez):
        if bytez == None:
            self.hex_edit.setPlainText('')
            return

        self.canvas.clearCanvas()
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0, e_mem.MM_READ, '', bytez)
        self.canvas.mem = mem
        self.canvas.renderMemory(0, len(bytez))
        self.hex_edit.setPlainText(str(self.canvas))

    def showSaveAsDialog(self):
        fname = str(QtGui.QFileDialog.getSaveFileName(caption='Select file to save results to'))
        self.fname_label.setText(fname)

    def cancelClicked(self):
        self.close()

    def okClicked(self):
        self.pattern = (self.data_edit.text())
        self.filename = str(self.fname_label.text())

        self.accept()
        self.close()

    def getResults(self):
        return self.pattern, self.filename

def main():
    app = QtGui.QApplication([])
    dlg = MemSearchDialog()
    font = QtGui.QFont('Courier')#'Consolas', 10)#'Courier New', 10)
    dlg.hex_edit.setFont(font)
    if dlg.exec_() == QtGui.QDialog.Accepted:
        print(dlg.pattern)
        print(dlg.filename)

if __name__ == '__main__':
    main()
