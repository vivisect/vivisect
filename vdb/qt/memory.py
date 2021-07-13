import vtrace.qt
import envi.common as e_common

import envi.qt.memory
import envi.qt.memcanvas

from vqt.main import *
from vqt.common import *

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

class VDBACT:

    def __init__(self, db, cmdline):
        self.db = db
        self.cmdline = cmdline

    def __call__(self, *args, **kwargs):
        workthread(self.db.onecmd)(self.cmdline)

class VdbMemoryCanvas(envi.qt.memcanvas.VQMemoryCanvas):
    # We get self.db set by our memory window smash...
    def initMemWindowMenu(self, va, menu):

        t = self.db.getTrace()

        menu.addAction('Run To Here', VDBACT(self.db, 'go 0x%.8x' % va))
        menu.addAction('Add Breakpoint', VDBACT(self.db, 'bp 0x%.8x' % va))

        bp = t.getBreakpointByAddr(va)
        if bp is not None:
            bpid = bp.getId()
            menu.addAction('Remove Breakpoint', VDBACT(self.db, 'bp -r %d' % bpid))

            if bp.enabled:
                menu.addAction('Disable Breakpoint', VDBACT(self.db, 'bp -d %d' % bpid))
            else:
                menu.addAction('Enable Breakpoint', VDBACT(self.db, 'bp -e %d' % bpid))

        smenu_patch = menu.addMenu('Bytes')
        nop = t.archGetNopInstr()
        # yuck...need to fix this on gui re-architecture.
        currend = self.vdb_memwin.rend_select.currentText()
        if nop is not None and 'asm' in currend:
            smenu_patch.addAction('Set Bytes To NOP', ACT(self._menuSetOpTo, va, nop))

        if 'asm' in currend:
            smenu_patch.addAction('Set Bytes To NULL', ACT(self._menuSetOpTo, va, '\x00'))

        if 'asm' in currend or 'bytes' in currend:
            smenu_patch.addAction('Modify Bytes', ACT(self._menuWriteMem, va))

        smenu_patch.addAction('Copy Bytes To Clipboard', ACT(self._menuCopyBytesToClipBoard, va, currend, False))
        smenu_patch.addAction('Copy Bytes To Clipboard (All Window Bytes)', ACT(self._menuCopyBytesToClipBoard, va, currend, True))

        return envi.qt.memcanvas.VQMemoryCanvas.initMemWindowMenu(self, va, menu)

    def menuLeftClick(self):
        '''
        handles left clicking on the 'open in current renderer'.
        '''
        self._menuFollow(self._canv_curva)

    def mouseDoubleClickEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return

        self._menuFollow(self._canv_curva)
        clipboard = QApplication.clipboard()
        clipboard.setText(hex(self._canv_curva))

    def _menuSetOpTo(self, va, byte):
        # TODO: this should be a helper func somewhere, nopInstruction?
        t = self.db.getTrace()
        op = t.parseOpcode(va)
        oplen = len(op)
        nlen = len(byte)

        if oplen % nlen != 0:
            raise Exception('cannot nop all bytes, mismatch')

        bytez = byte * (oplen / nlen)
        self.db.do_writemem('%s %s' % (va, bytez))

    def _menuCopyBytesToClipBoard(self, va, currend, all_window_bytes):
        t = self.db.getTrace()
        if all_window_bytes:
            va = self._canv_beginva
            size = self._canv_endva - va

        else:
            if 'asm' in currend:
                op = t.parseOpcode(va)
                size = len(op)
            else:
                size = t.getPointerSize()

        bytez = t.readMemory(va, size)

        clipboard = QApplication.clipboard()
        clipboard.setText(e_common.hexify(bytez))

    def _menuFollow(self, va, rend='', newWindow=False):
        totalsize = self._canv_endva - self._canv_beginva

        if newWindow:
            vqtevent('vdb:view:memory', (hex(va), '256', rend))
            return

        if self._canv_navcallback:
            self._canv_navcallback(hex(va), str(totalsize), rend)

    def _menuWriteMem(self, va):
        vqtevent('vdb:view:writemem', (hex(va), '256'))

    def reRender(self):
        '''
        Forces the canvas to refresh everything it's currently displaying.
        '''
        if self._canv_endva is None or self._canv_beginva is None:
            # not rendered yet.
            return

        totalsize = self._canv_endva - self._canv_beginva

        self.renderMemory(self._canv_beginva, totalsize)

class VdbMemoryWindow(envi.qt.memory.VQMemoryWindow, vtrace.qt.VQTraceNotifier):

    def __init__(self, db, dbt, parent=None, expr=None, sizeexpr=None, rend=None, **kwargs):
        vtrace.qt.VQTraceNotifier.__init__(self, trace=dbt)
        envi.qt.memory.VQMemoryWindow.__init__(self, dbt, syms=dbt, parent=parent, **kwargs)

        for rname in db.canvas.getRendererNames():
            self.mem_canvas.addRenderer(rname, db.canvas.getRenderer(rname))

        self.mem_canvas.db = db
        self.mem_canvas.vdb_memwin = self

        self.loadRendSelect()

        if not dbt.isAttached():
            self.setEnabled(False)
        elif dbt.isRunning():
            self.setEnabled(False)
        else:
            self._renderMemory()

        vqtconnect(self._renderMemory, 'vdb:stopped')
        vqtconnect(self._renderMemory, 'vdb:writemem')
        vqtconnect(self._renderMemory, 'vdb:delbreak')
        vqtconnect(self._renderMemory, 'vdb:addbreak')

        vqtconnect(ACT(self.setEnabled, True), 'vdb:attached')
        vqtconnect(ACT(self.setEnabled, False), 'vdb:detached')

    def initMemoryCanvas(self, memobj, syms=None):
        return VdbMemoryCanvas(memobj, syms=syms, parent=self)

    def vqLoad(self):
        self._renderMemory()
