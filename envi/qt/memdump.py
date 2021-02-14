from PyQt5.QtWidgets import *

from vqt.main import getSaveFileName

class MemDumpDialog(QDialog):
    '''
    gui for memdump cli command.
    '''
    def __init__(self, va, filename='', size=256):
        QDialog.__init__(self)

        self.va = va
        self.filename = filename
        self.size = size

        hbox1 = QHBoxLayout()
        fname_label = QLabel('Filename: ')
        self.fname_edit = QLineEdit()
        self.fname_edit.setText(self.filename)
        browse_button = QPushButton('...')
        browse_button.clicked.connect(self.showSaveAsDialog)
        hbox1.addWidget(fname_label)
        hbox1.addWidget(self.fname_edit)
        hbox1.addWidget(browse_button)

        hbox2 = QHBoxLayout()
        size_label = QLabel('Size: ')
        self.size_edit = QLineEdit()
        self.size_edit.setText(str(self.size))
        hbox2.addWidget(size_label)
        hbox2.addWidget(self.size_edit)

        hbox3 = QHBoxLayout()
        ok_button = QPushButton('&OK')
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.okClicked)
        cancel_button = QPushButton('&Cancel')
        cancel_button.clicked.connect(self.cancelClicked)
        hbox3.addWidget(ok_button)
        hbox3.addWidget(cancel_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        self.setLayout(vbox)

        title = 'Dump memory at va 0x%x to a file' % self.va
        self.setWindowTitle(title)

    def showSaveAsDialog(self):
        fname = str(getSaveFileName(caption='Select file to dump memory to'))
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
