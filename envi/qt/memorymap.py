from PyQt5 import QtCore
from PyQt5.QtWidgets import *

import envi.common as e_common
import envi.memory as e_memory
import envi.memcanvas
import envi.qt.memdump
import envi.qt.memsearch
import envi.cli as e_cli
from vqt.common import ACT
import vqt.tree as vq_tree

class VQMemoryMapView(vq_tree.VQTreeView):

    def __init__(self, mem, parent=None):
        self.cols = ('Address', 'Size', 'Perms', 'Filename')
        vq_tree.VQTreeView.__init__(self, parent=parent, cols=self.cols)
        self.mem = mem
        self.memmaps = []
        self.parent = parent

        # instantiate envicli so we can re-use some of the commands
        self.cli = e_cli.EnviCli(mem)
        self.canvas = envi.memcanvas.StringMemoryCanvas(mem)
        self.cli.setCanvas(self.canvas)

        self.vqLoad()
        self.vqSizeColumns()
        self.setWindowTitle('Memory Maps')

    def buildContextMenu(self, va, size):
        menu = QMenu()
        menu.addAction('Copy Bytes To Clipboard', ACT(self.menuCopyBytesToClipboard, va, size))
        menu.addAction('Save Bytes To File', ACT(self.menuSaveBytesToFile, va, size))
        menu.addAction('Search Selected Memory Map', ACT(self.menuSearchMaps, va, size, allmaps=False))
        menu.addAction('Search All Memory Maps', ACT(self.menuSearchMaps, va, size, allmaps=True))
        return menu

    def vqLoad(self):
        model = vq_tree.VQTreeModel(parent=self.parent, columns=self.cols)
        for mva, msize, mperm, mfile in self.mem.getMemoryMaps():
            pstr = e_memory.reprPerms(mperm)
            model.append(('0x%.8x' % mva, msize, pstr, mfile))

        self.setModel(model)

    def getSelectedData(self):
        index = self.currentIndex()

        pindex = index.parent()
        va_index = self.model().index(index.row(), 0, pindex)
        size_index = self.model().index(index.row(), 1, pindex)
        va = self.mem.parseExpression(self.model().data(va_index, QtCore.Qt.DisplayRole))
        size = self.mem.parseExpression(self.model().data(size_index, QtCore.Qt.DisplayRole))

        return va, size

    def contextMenuEvent(self, event):
        va, size = self.getSelectedData()
        menu = self.buildContextMenu(va, size)
        menu.exec_(event.globalPos())

    def menuCopyBytesToClipboard(self, va, size):
        bytez = self.mem.readMemory(va, size)

        clipboard = QApplication.clipboard()
        clipboard.setText(e_common.hexify(bytez))

    def menuSaveBytesToFile(self, va, size):
        dlg = envi.qt.memdump.MemDumpDialog(va, size=size)
        if dlg.exec_() != QDialog.Accepted:
            return

        filename, size = dlg.getResults()
        bytez = self.mem.readMemory(va, size)
        with open(filename, 'wb') as f:
            f.write(bytez)

    def menuSearchMaps(self, va, size, allmaps=False):
        dlg = envi.qt.memsearch.MemSearchDialog()
        if dlg.exec_() != QDialog.Accepted:
            return

        pattern, fname = dlg.getResults()

        if allmaps == True:
            self.do_searchall(pattern, fname=fname)
        else:
            va, size, perms, mname = self.mem.getMemoryMap(va)
            self.do_searchmap(va, size, pattern, fname=fname)

    def do_searchmap(self, va, size, pattern, switch='', fname=''):
        line = '%s -R %s:%s -c %s' % (switch, va, size, pattern)
        self.do_search(line, fname=fname)

    def do_searchall(self, pattern, switch='', fname=''):
        line = '%s -c %s' % (switch, pattern)
        self.do_search(line, fname=fname)

    def do_search(self, line, fname=''):
        if fname == '':
            self.parent._db.do_search(line)
        else:
            line = '%s search %s' % (fname, line)
            self.parent._db.do_saveout(line)

    def selectRow(self, row):
        idx = self.model().index(row, 0, QtCore.QModelIndex())
        self.setCurrentIndex(idx)
