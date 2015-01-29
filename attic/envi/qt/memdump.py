from PyQt4 import QtGui, QtCore

class MemDumpDialog(QtGui.QDialog):
    '''
    gui for memdump cli command.
    '''
    def __init__(self, va, filename='', size=256):
        QtGui.QDialog.__init__(self)

        self.va = va
        self.filename = filename
        self.size = size

        hbox1 = QtGui.QHBoxLayout()
        fname_label = QtGui.QLabel('Filename: ')
        self.fname_edit = QtGui.QLineEdit()
        self.fname_edit.setText(self.filename)
        browse_button = QtGui.QPushButton('...')
        browse_button.clicked.connect(self.showSaveAsDialog)
        hbox1.addWidget(fname_label)
        hbox1.addWidget(self.fname_edit)
        hbox1.addWidget(browse_button)

        hbox2 = QtGui.QHBoxLayout()
        size_label = QtGui.QLabel('Size: ')
        self.size_edit = QtGui.QLineEdit()
        self.size_edit.setText(str(self.size))
        hbox2.addWidget(size_label)
        hbox2.addWidget(self.size_edit)

        hbox3 = QtGui.QHBoxLayout()
        ok_button = QtGui.QPushButton('&OK')
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.okClicked)
        cancel_button = QtGui.QPushButton('&Cancel')
        cancel_button.clicked.connect(self.cancelClicked)
        hbox3.addWidget(ok_button)
        hbox3.addWidget(cancel_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)

        title = 'Dump memory at va 0x%x to a file' % self.va
        self.setWindowTitle(title)

    def showSaveAsDialog(self):
        fname = str(QtGui.QFileDialog.getSaveFileName(caption='Select file to dump memory to'))
        self.fname_edit.setText(fname)

    def cancelClicked(self):
        self.close()

    def okClicked(self):
        self.filename = self.fname_edit.text()
        self.size = int(self.size_edit.text())

        self.accept()
        self.close()

    def getResults(self):
        return self.filename, self.size

def main():
    app = QtGui.QApplication([])
    dlg = MemDumpDialog(0x1234, '5678', 0x9ab)
    if dlg.exec_() == QtGui.QDialog.Accepted:
        print(dlg.filename)
        print(dlg.size)

if __name__ == '__main__':
    main()
