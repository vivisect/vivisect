'''
Views related to information about a given function.
'''
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMenu, QWidget

import vivisect.qt.ctxmenu as viv_q_ctxmenu
import visgraph.renderers.qgraphtree as vg_qgraphtree

from vqt.basics import *


class FuncBlockModel(BasicModel):
    columns = ('Base Address', 'Size')


class FunctionBlocksView(BasicTreeView):

    _sig_BlockSelected = QtCore.pyqtSignal(object)

    def __init__(self, vw, parent=None):
        self.vw = vw

        BasicTreeView.__init__(self, parent=parent)
        self.setModel(FuncBlockModel())
        self.setWindowTitle('Code Blocks: ')

    def selectionChanged(self, selected, unselected):

        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            row = self.model().rows[index.row()]

            block = row[-1]
            self._sig_BlockSelected.emit(block)

            cmap = {}
            bva, bsize, fva = block
            for i in range(bsize):
                cmap[bva + i] = 'yellow'

            # Since we have a reference to the GUI, lets also
            # send a coloration signal.
            vwgui = self.vw.getVivGui()
            vwgui.vivMemColorSignal.emit(cmap)

        return BasicTreeView.selectionChanged(self, selected, unselected)

    def closeEvent(self, event):
        # On close, remove any color mappings...
        vwgui = self.vw.getVivGui()
        vwgui.vivMemColorSignal.emit({})
        return BasicTreeView.closeEvent(self, event)

    def functionSelected(self, fva):
        self.setWindowTitle('Code Blocks: %s' % self.vw.getName(fva))
        blocks = self.vw.getFunctionBlocks(fva)
        rows = [('0x%.8x' % block[0], block[1], block) for block in blocks]
        model = FuncBlockModel(rows=rows)
        self.setModel(model)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)


class FuncCallsView(QWidget):

    def __init__(self, vw, parent=None):
        self.vw = vw
        QWidget.__init__(self, parent=parent)

        self.graphview = vg_qgraphtree.QGraphTreeView(None, (), parent=self)
        self.graphview._sig_NodeContextMenu.connect(self.nodeContextMenu)
        self.setLayout(VBox(self.graphview))

    def functionSelected(self, fva):
        self.setWindowTitle('Call Graph: %s' % self.vw.getName(fva))
        nprops = self.vw._call_graph.getNodeProps(fva)
        self.graphview.loadNewGraph(self.vw._call_graph, ((fva, nprops), ))

    def nodeContextMenu(self, pos, nid, nprops):
        menu = QMenu(parent=self)
        viv_q_ctxmenu.buildContextMenu(self.vw, va=nid, menu=menu)
        menu.exec_(pos)
