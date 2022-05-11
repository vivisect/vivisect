from collections import deque

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *

import envi.qt.memcanvas as e_memcanvas_qt
import envi.memcanvas.renderers as e_render

import vqt.tree as vq_tree
import vqt.hotkeys as vq_hotkey
import vqt.saveable as vq_save

from vqt.main import *
from vqt.common import *

class EnviNavMixin:
    '''
    Classes may inerhit from this mixin to help out with envi
    nav events.

    Implement enviNavGoto() which will only be called when your
    envi nav name (setEnviNavName()) matches the nav event.
    '''

    def __init__(self):
        self._envi_navname = 'mem'
        vqtconnect(self.enviNavGetnames, 'envi:nav:getnames')
        vqtconnect(self.enviNavExpr, 'envi:nav:expr')
        self.setAcceptDrops(True)

    def enviNavFini(self):
        '''
        Called when it's time to explicitly cleanup our event
        subscriptions.

        NOTE: this should be called by closeEvent handlers.
        '''
        vqtdisconnect(self.enviNavGetnames, 'envi:nav:getnames')
        vqtdisconnect(self.enviNavExpr, 'envi:nav:expr')

    def enviNavGoto(self, expr, sizeexpr=None, rend=None):
        pass

    def enviNavExpr(self, event, einfo):
        name, expr, sizeexpr = einfo
        if self._envi_navname == name:
            self.enviNavGoto(expr,sizeexpr=sizeexpr)

    def enviNavGetnames(self, event, einfo):
        einfo.append( self._envi_navname )

    def setEnviNavName(self, name):
        self._envi_navname = name

    def getEnviNavName(self):
        return self._envi_navname

    def dragEnterEvent(self, e):
        mdata = e.mimeData()
        if mdata.hasFormat('envi/expression'):
            e.accept()
            return
        e.ignore()

    def dropEvent(self, e):
        mdata = e.mimeData()
        if mdata.hasFormat('envi/expression'):
            expr = mdata.data('envi/expression').data().decode('utf-8')
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            self.enviNavGoto(expr)
            return
        e.ignore()

class EnviNavModel(vq_tree.VQTreeModel):

    dragable = True

    def __init__(self, navcol, parent=None, columns=None):
        vq_tree.VQTreeModel.__init__(self, parent=parent, columns=columns)
        self.navcol = navcol

    def mimeData(self, idx):
        pnode = idx[0].internalPointer()
        expr = pnode.rowdata[self.navcol]
        mdata = QtCore.QMimeData()
        mdata.setData('envi/expression', expr.encode('utf-8'))
        return mdata

class VQMemoryWindow(vq_hotkey.HotKeyMixin, EnviNavMixin, vq_save.SaveableWidget, QWidget):

    def __init__(self, memobj, syms=None, parent=None, mwname='mem'):

        QWidget.__init__(self, parent=parent)
        vq_hotkey.HotKeyMixin.__init__(self)
        vq_save.SaveableWidget.__init__(self)
        EnviNavMixin.__init__(self)
        self.setEnviNavName(mwname)

        self._mem_obj = memobj
        self.mwname = mwname
        self.mwlocked = False

        self.top_box = QWidget(parent=self)
        hbox = QHBoxLayout(self.top_box)
        hbox.setContentsMargins(2, 2, 2, 2)
        hbox.setSpacing(4)

        self.histmenu = QMenu(parent=self)
        self.histmenu.aboutToShow.connect( self.setupMemHistMenu )

        self.hist_button = QPushButton('History', parent=self.top_box)
        self.hist_button.setMenu(self.histmenu)

        self.addr_entry  = QLineEdit(parent=self.top_box)
        self.size_entry  = QLineEdit(parent=self.top_box)
        self.size_entry.setText('256')
        self.rend_select = QComboBox(parent=self.top_box)

        self.rend_tools = QPushButton('Opts', parent=self.top_box)
        self.rend_tools.setMenu( self.getRendToolsMenu() )

        self.mem_history = deque()
        self.mem_canvas = self.initMemoryCanvas(memobj, syms=syms)
        self.mem_canvas.setNavCallback(self.enviNavGoto)

        # https://doc.qt.io/qt-5/qt.html#ShortcutContext-enum
        QShortcut(QtGui.QKeySequence("Escape"), self, activated=self._hotkey_histback, context=3)

        self.loadDefaultRenderers()
        self.loadRendSelect()

        self.addr_entry.returnPressed.connect(self._renderMemory)
        self.size_entry.returnPressed.connect(self._renderMemory)

        self.rend_select.currentIndexChanged['QString'].connect(self._renderMemory)

        hbox.addWidget(self.hist_button)
        hbox.addWidget(self.addr_entry)
        hbox.addWidget(self.size_entry)
        hbox.addWidget(self.rend_select)
        hbox.addWidget(self.rend_tools)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)
        vbox.addWidget(self.top_box)
        vbox.addWidget(self.mem_canvas, stretch=100)

        self.top_box.setLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle('%s: None' % self.mwname)

    def closeEvent(self, event):
        self.enviNavFini()

    def initMemoryCanvas(self, memobj, syms=None):
        return e_memcanvas_qt.VQMemoryCanvas(memobj, syms=syms, parent=self)

    def setMemWindowName(self, mwname):
        '''
        Set the memory window name/title prefix to the given string.
        '''
        self.mwname = mwname
        self.setEnviNavName(mwname)
        self.updateMemWindowTitle()

    def getExprTitle(self):
        return str(self.addr_entry.text())

    def updateMemWindowTitle(self):
        expr = self.getExprTitle()

        title = '%s: %s' % (self.mwname, expr)
        if self.mwlocked:
            title += ' (locked)'

        self.setWindowTitle(title)

    def getRendToolsMenu(self):
        menu = QMenu(parent=self.rend_tools)
        menu.addAction('set name', self.rendToolsSetName)

        lockact = QAction('locked', menu, checkable=True)
        lockact.setChecked(self.mwlocked)

        def lockToggle():
            self.mwlocked = not self.mwlocked
            self.updateMemWindowTitle()

        lockact.toggled.connect(lockToggle)
        menu.addAction(lockact)

        return menu

    def rendToolsSetName(self):
        mwname, ok = QInputDialog.getText(self, 'Set Mem Window Name', 'Name')
        if ok:
            self.setMemWindowName(str(mwname))

    def rendToolsMenu(self, event):
        menu = self.getRendToolsMenu()
        menu.exec_(self.mapToGlobal(self.rend_tools.pos()))

    #def setRendererByName(self, rname):
        # FIXME implement...

    def _hotkey_histback(self):
        if len(self.mem_history) >= 2:
            hinfo = self.mem_history.popleft()
            hinfo = self.mem_history.popleft()
            self._histSelected( hinfo )

    def _histSelected(self, hinfo):
        addrexpr, sizeexpr, rendname = hinfo
        self.addr_entry.setText(addrexpr)
        self.size_entry.setText(sizeexpr)
        self.mem_canvas.setRenderer(rendname)
        self._renderMemory()

    def setupMemHistMenu(self):
        self.histmenu.clear()

        for hinfo in self.mem_history:
            addrexpr, sizeexpr, rendname = hinfo
            addr = self._mem_obj.parseExpression(addrexpr)
            menustr = '0x%.8x' % addr
            sym = self._mem_obj.getSymByAddr(addr)
            if sym is not None:
                menustr += ' - %s' % repr(sym)

            self.histmenu.addAction(menustr, ACT(self._histSelected, hinfo))

    @idlethread
    def enviNavGoto(self, expr, sizeexpr='256', rend=''):

        if self.mwlocked:
            return

        # Used by nav event generators to make us render
        self.addr_entry.setText(expr)
        if sizeexpr is not None:
            self.size_entry.setText(sizeexpr)

        if rend is not None:
            idx = self.rend_select.findText(str(rend))
            if idx >= 0:
                self.rend_select.setCurrentIndex(idx)

        self._renderMemory()

    def loadRendSelect(self):
        self.rend_select.clear()
        for name in self.mem_canvas.getRendererNames():
            self.rend_select.addItem(name)

    def loadDefaultRenderers(self):
        self.mem_canvas.addRenderer("bytes",    e_render.ByteRend())
        self.mem_canvas.addRenderer("u_int_16", e_render.ShortRend())
        self.mem_canvas.addRenderer("u_int_32", e_render.LongRend())
        self.mem_canvas.addRenderer("u_int_64", e_render.QuadRend())

    def _getRenderVaSize(self):

        expr = str(self.addr_entry.text())
        sizeexpr = str(self.size_entry.text())

        if not expr:
            return None, None

        if not sizeexpr:
            return None, None

        try:
            addr = self._mem_obj.parseExpression(expr)
        except Exception as e:
            self.mem_canvas.addText('Invalid Address: %s (%s)' % (expr, e))
            return None, None

        try:
            size = self._mem_obj.parseExpression(sizeexpr)
        except Exception as e:
            self.mem_canvas.addText('Invalid Size: %s (%s)' % (expr, e))
            return None, None

        self.updateMemWindowTitle()
        return addr, size

    @idlethread
    def _renderMemory(self, *args, **kwargs):

        self.clearText()

        addr, size = self._getRenderVaSize()
        if addr is None:
            return

        expr = str(self.addr_entry.text())
        rname = str(self.rend_select.currentText())
        sizeexpr = str(self.size_entry.text())

        mhist = (expr, sizeexpr, rname)
        if mhist not in self.mem_history:
            self.mem_history.appendleft(mhist)
            while len(self.mem_history) > 100:
                self.mem_history.pop()

        self.mem_canvas.setRenderer(rname)
        try:
            self.mem_canvas.renderMemory(addr, size)
        except Exception as e:
            self.mem_canvas.addText('Render Exception: 0x%x (%s)' % (addr, e))

    def clearText(self):
        self.mem_canvas.clearCanvas()

    def vqGetSaveState(self):
        state = {}
        state['addr_entry'] = str(self.addr_entry.text())
        state['rend_select'] = str(self.rend_select.currentText())
        state['size_entry'] = str(self.size_entry.text())
        state['name'] = self.mwname
        return state

    def vqSetSaveState(self, state):
        self.addr_entry.setText(state.get('addr_entry',''))
        self.size_entry.setText(state.get('size_entry',''))
        self.setMemWindowName( str(state.get('name','mem')) )

        rendname = state.get('rend_select')
        if rendname:
            index = self.rend_select.findText(rendname)
            self.rend_select.setCurrentIndex(index)
