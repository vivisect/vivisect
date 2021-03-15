import logging

from PyQt5 import Qt
from PyQt5.QtWidgets import *

import envi.qt.memory as e_mem_qt
import envi.qt.memcanvas as e_mem_canvas

import vqt.hotkeys as vq_hotkey

import vivisect.base as viv_base
import vivisect.renderers as viv_rend
import vivisect.qt.views as viv_q_views
import vivisect.qt.ctxmenu as viv_q_ctxmenu

from vqt.main import *
from vivisect.const import *

logger = logging.getLogger(__name__)


# FIXME HACK where do these really live?
qt_horizontal   = 1
qt_vertical     = 2


class VivCanvasBase(vq_hotkey.HotKeyMixin, e_mem_canvas.VQMemoryCanvas):

    def __init__(self, *args, **kwargs):

        e_mem_canvas.VQMemoryCanvas.__init__(self, *args, **kwargs)
        vq_hotkey.HotKeyMixin.__init__(self)

        self.vw = self.mem
        self._last_sname = None

        self.addHotKey('c', 'viv:make:code')
        self.addHotKey('f', 'viv:make:function')
        self.addHotKey('s', 'viv:make:string')
        self.addHotKey('p', 'viv:make:pointer')
        self.addHotKey('u', 'viv:make:unicode')
        self.addHotKey('n', 'viv:setname')
        self.addHotKey('g', 'viv:getlocation')
        self.addHotKey(';', 'viv:comment')
        self.addHotKey('S', 'viv:make:struct')
        self.addHotKey('ctrl+S', 'viv:make:struct:again')
        self.addHotKey('ctrl+meta+S', 'viv:make:struct:multi')
        self.addHotKey('U', 'viv:undefine')
        self.addHotKey('ctrl+p', 'viv:preview:instr')
        self.addHotKey('B', 'viv:bookmark')
        self.addHotKey('ctrl+meta+J', 'viv:javascript')

        self.addHotKey('ctrl+1', 'viv:make:number:one')
        self.addHotKey('ctrl+2', 'viv:make:number:two')
        self.addHotKey('ctrl+4', 'viv:make:number:four')
        self.addHotKey('ctrl+6', 'viv:make:number:sixteen')
        self.addHotKey('ctrl+8', 'viv:make:number:eight')

        self.addHotKey('down', 'viv:nav:nextva')
        self.addHotKey('up', 'viv:nav:prevva')
        self.addHotKey('ctrl+down', 'viv:nav:nextundef')
        self.addHotKey('ctrl+up', 'viv:nav:prevundef')

        self.loadHotKeys(self.vw._viv_gui._vq_settings)

        # All extenders must implement vivColorMap
        vqtconnect(self.vivColorMap, 'viv:colormap')

    def event(self, evt):
        if evt.type() == Qt.QEvent.ChildAdded:
            evt.child().installEventFilter(self)
        elif evt.type() == Qt.QEvent.ChildRemoved:
            evt.child().removeEventFilter(self)
        return e_mem_canvas.VQMemoryCanvas.event(self, evt)

    def eventFilter(self, src, evt):
        if evt.type() == Qt.QEvent.KeyPress:
            return self.eatKeyPressEvent(evt)
        return False

    def vivColorMap(self, event, einfo):
        self._applyColorMap(einfo)

    def _applyColorMap(self, cmap):

        page = self.page()
        inner = ''
        for va, color in cmap.items():
            inner += '.envi-va-0x%.8x { color: #000000; background-color: %s }\n' % (va, color)
        inner = inner.replace('`', r'\`')
        js = 'var node = document.querySelector("#cmapstyle"); node.innerHTML = `%s`;' % inner
        page.runJavaScript(js)

    @vq_hotkey.hotkey('viv:nav:nextva')
    def _hotkey_nav_nextva(self):
        if self._canv_curva is None:
            return

        loc = self.vw.getLocation(self._canv_curva)
        if loc is None:
            loc = (self._canv_curva, 1, None, None)

        nextva = loc[0] + loc[1]
        self._selectVa(nextva)

    @vq_hotkey.hotkey('viv:nav:prevva')
    def _hotkey_nav_prevva(self):
        if self._canv_curva is None:
            return

        loc = self.vw.getPrevLocation(self._canv_curva)
        if loc is None:
            loc = (self._canv_curva - 1, 1, None, None)

        self._selectVa(loc[0])

    @vq_hotkey.hotkey('viv:nav:nextundef')
    def _hotkey_nav_nextundef(self):
        if self._canv_curva is None:
            return

        vw = self.vw
        va = self._canv_curva
        loc = vw.getLocation(va)

        if loc is None:
            # find next defined location
            while loc is None and vw.isValidPointer(va):
                va += 1
                loc = vw.getLocation(va)
            va -= 1
            lastloc = (va, 1, 0, 0)
        else:
            # find next undefined location
            while loc is not None:
                va = loc[0]
                lastloc = loc
                loc = vw.getLocation(va + loc[1])

        # if we didn't fall off the map
        if vw.isValidPointer(va+lastloc[1]):
            va += lastloc[1]
        self._navExpression(hex(va))

    @vq_hotkey.hotkey('viv:nav:prevundef')
    def _hotkey_nav_prevundef(self):
        if self._canv_curva is None:
            return

        vw = self.vw
        va = self._canv_curva
        loc = vw.getLocation(va)

        if loc is None:
            # find previous defined location
            while loc is None and vw.isValidPointer(va):
                va -= 1
                loc = vw.getLocation(va)
            if loc is not None:
                va = loc[0]
        else:
            # find previous undefined location
            while loc is not None:
                va = loc[0]
                loc = vw.getLocation(va-1)

            # if we fell off the end of a map
            if vw.isValidPointer(va-1):
                va -= 1

        self._navExpression(hex(va))

    @vq_hotkey.hotkey('viv:make:code')
    def _hotkey_make_code(self):
        if self._canv_curva is not None:
            self.vw.makeCode(self._canv_curva)

    @vq_hotkey.hotkey('viv:make:function')
    def _hotkey_make_function(self):
        if self._canv_curva is not None:
            logger.debug('new function (manual): 0x%x', self._canv_curva)
            self.vw.makeFunction(self._canv_curva)

    @vq_hotkey.hotkey('viv:make:string')
    def _hotkey_make_string(self):
        if self._canv_curva is not None:
            self.vw.makeString(self._canv_curva)

    @vq_hotkey.hotkey('viv:make:pointer')
    def _hotkey_make_pointer(self):
        if self._canv_curva is not None:
            self.vw.makePointer(self._canv_curva)

    @vq_hotkey.hotkey('viv:make:unicode')
    def _hotkey_make_unicode(self):
        if self._canv_curva is not None:
            self.vw.makeUnicode(self._canv_curva)

    @vq_hotkey.hotkey('viv:undefine')
    def _hotkey_undefine(self):
        if self._canv_curva is not None:
            self.vw.delLocation(self._canv_curva)

    @vq_hotkey.hotkey('viv:getlocation')
    def _hotkey_getlocation(self):
        if self._canv_curva is not None:
            self.vw.getVivGui().getLocation(self._canv_curva)

    @vq_hotkey.hotkey('viv:setname')
    def _hotkey_setname(self):
        if self._canv_curva is not None:
            self.vw.getVivGui().setVaName(self._canv_curva, parent=self)

    @vq_hotkey.hotkey('viv:bookmark')
    def _hotkey_bookmark(self):
        if self._canv_curva is not None:
            self.vw.getVivGui().addBookmark(self._canv_curva, parent=self)

    @vq_hotkey.hotkey('viv:comment')
    def _hotkey_comment(self):
        if self._canv_curva is not None:
            self.vw.getVivGui().setVaComment(self._canv_curva, parent=self)

    @vq_hotkey.hotkey('viv:make:struct')
    def _hotkey_make_struct(self):
        if self._canv_curva is not None:
            sname = self.vw.getVivGui().makeStruct(self._canv_curva)
            if sname is not None:
                self._last_sname = sname

    @vq_hotkey.hotkey('viv:make:struct:again')
    def _hotkey_make_struct_again(self):
        if self._canv_curva is not None:
            if self._last_sname is not None:
                self.vw.makeStructure(self._canv_curva, self._last_sname)

    @vq_hotkey.hotkey('viv:make:struct:multi')
    def _hotkey_make_struct_multi(self, parent=None):
        if self._canv_curva is not None:
            if self._last_sname is not None:
                number, ok = QInputDialog.getText(parent, 'Make Multiple Consecutive Structs', 'Number of Structures')
                if ok:
                    curva = self._canv_curva
                    number = int(str(number), 0)
                    for count in range(number):
                        vs = self.vw.makeStructure(curva, self._last_sname)
                        curva += len(vs)

    @vq_hotkey.hotkey('viv:javascript')
    def _hotkey_dbg_runjavascript(self, parent=None):
        js, ok = QInputDialog.getText(parent, 'Run Javascript', 'code:')
        if ok:
            self.page().runJavaScript(js)

    def makeStructAgainMulti(self, va, parent=None):
        if parent is None:
            parent = self

        curcomment = self.vw.getComment(va)
        if curcomment is None:
            curcomment = ''

        comment, ok = QInputDialog.getText(parent, 'Enter...', 'Comment', text=curcomment)
        if ok:
            self.vw.setComment(va, str(comment))

    @vq_hotkey.hotkey('viv:make:number:one')
    def _hotkey_make_number_one(self):
        if self._canv_curva is not None:
            self.vw.makeNumber(self._canv_curva, 1)

    @vq_hotkey.hotkey('viv:make:number:two')
    def _hotkey_make_number_two(self):
        if self._canv_curva is not None:
            self.vw.makeNumber(self._canv_curva, 2)

    @vq_hotkey.hotkey('viv:make:number:four')
    def _hotkey_make_number_four(self):
        if self._canv_curva is not None:
            self.vw.makeNumber(self._canv_curva, 4)

    @vq_hotkey.hotkey('viv:make:number:eight')
    def _hotkey_make_number_eight(self):
        if self._canv_curva is not None:
            self.vw.makeNumber(self._canv_curva, 8)

    @vq_hotkey.hotkey('viv:make:number:sixteen')
    def _hotkey_make_number_sixteen(self):
        if self._canv_curva is not None:
            self.vw.makeNumber(self._canv_curva, 16)

    @vq_hotkey.hotkey('viv:preview:instr')
    def _hotkey_preview_instr(self):
        if self._canv_curva is not None:
            self.vw.previewCode(self._canv_curva)

    def getVaTag(self, va):
        loc = self.mem.getLocation(va)
        if loc is not None:
            va = loc[L_VA]
        return e_mem_canvas.VQMemoryCanvas.getVaTag(self, va)


class VQVivMemoryCanvas(VivCanvasBase):

    def _wheelEventCallback(self, data):
        '''
        Ugh. Yes. I know this sucks.
        But we have to do this because QtWebEngine does't natively let you get the max scroll size.
        You *have* to go through javascript to get those elements, and the only way to be sure of
        the function finishing (and being able to get a value outta js) is via this callback
        mechanism they set up.
        '''
        if not data:
            return
        smin = data[0]
        spos = data[1]
        smax = data[2]
        if not len(self._canv_rendvas):
            pass

        elif spos >= smax:
            lastva, lastsize = self._canv_rendvas[-1]
            mapva, mapsize, mperm, mfname = self.vw.getMemoryMap(lastva)
            sizeremain = (mapva + mapsize) - (lastva + lastsize)
            if sizeremain:
                self.renderMemoryAppend(min(sizeremain, 128))

        elif spos == smin:
            firstva, firstsize = self._canv_rendvas[0]
            mapva, mapsize, mperm, mfname = self.vw.getMemoryMap(firstva)
            sizeremain = firstva - mapva
            if sizeremain:
                self.renderMemoryPrepend(min(sizeremain, 128))

    def wheelEvent(self, event):
        page = self.page()
        page.runJavaScript('''
        var pcur = window.innerHeight + window.pageYOffset
        var scrollMaxY = Math.max(
            document.body.scrollHeight, document.documentElement.scrollHeight,
            document.body.offsetHeight, document.documentElement.offsetHeight,
            document.body.clientHeight, document.documentElement.clientHeight,
        );
        [window.innerHeight, pcur, scrollMaxY];
        ''', self._wheelEventCallback)

        return e_mem_canvas.VQMemoryCanvas.wheelEvent(self, event)

    def _clearColorMap(self):
        page = self.page()
        page.runJavaScript('var node = document.querySelector("#cmapstyle"); node.innerHTML = "";')

    def _navExpression(self, expr):
        if self._canv_navcallback:
            self._canv_navcallback(expr)

    def initMemWindowMenu(self, va, menu):
        nav = self.parent()  # our parent is always a VQVivMemoryWindow (nav target)
        viv_q_ctxmenu.buildContextMenu(self.vw, va=va, menu=menu, nav=nav)

    def _loc_helper(self, va):
        '''
        we assume we're being handed a valid va since renderMemory checks for valid MemoryMap
        '''
        nloc = self.mem.getLocation(va)
        if nloc is None:
            return va, 0

        nva, nvsz, nvt, nvti = nloc
        return (nva, va-nva)


class VQVivMemoryView(e_mem_qt.VQMemoryWindow, viv_base.VivEventCore):

    def __init__(self, vw, vwqgui):
        self.vw = vw
        self.vwqgui = vwqgui

        self._leading = False
        self._following = None
        self._follow_menu = None  # init'd in handler below

        e_mem_qt.VQMemoryWindow.__init__(self, vw, syms=vw, parent=vwqgui, mwname='viv')
        viv_base.VivEventCore.__init__(self, vw)

        vwqgui.addEventCore(self)
        self.mem_canvas._canv_rend_middle = True

        self.addHotKeyTarget('viv:xrefsto', self._viv_xrefsto)
        self.addHotKey('x', 'viv:xrefsto')

    def getRendToolsMenu(self):
        menu = e_mem_qt.VQMemoryWindow.getRendToolsMenu(self)
        if self.vw.server:

            leadact = QAction('lead', menu, checkable=True)

            def leadToggle():
                self._leading = not self._leading
                # We can only follow if not leading... (deep huh? ;) )
                self._follow_menu.setEnabled(not self._leading)
                if self._leading:
                    self._following = None
                    self.vw.iAmLeader(self.mwname)
                self.updateMemWindowTitle()

            def clearFollow():
                self._following = None
                self.updateMemWindowTitle()

            leadact.toggled.connect(leadToggle)
            menu.addAction(leadact)
            self._follow_menu = menu.addMenu('Follow..')
            self._follow_menu.addAction('(disable)', clearFollow)

        return menu

    def getExprTitle(self):
        title = str(self.addr_entry.text())

        try:

            va = self.vw.parseExpression(title)
            name = self.vw.getName(va)
            if name is not None:
                title = name

        except Exception:
            title = 'expr error'

        if self._leading:
            title += ' (leading)'

        if self._following is not None:
            user, window = self._following
            title += ' (following %s %s)' % (user, window)

        return title

    def _getRenderVaSize(self):
        '''
        Vivisect steps in and attempts to map to locations when they exist.

        since we have a location database, let's use that to make sure we get a
        real location if it exists.  otherwise, we end up in no-man's land,
        since we rely on labels, which only exist for the base of a location.
        '''
        addr, size = e_mem_qt.VQMemoryWindow._getRenderVaSize(self)
        if addr is None:
            return addr, size

        loc = self.vw.getLocation(addr)
        if loc is None:
            return addr, size

        return loc[L_VA], size

    def initMemoryCanvas(self, memobj, syms=None):
        return VQVivMemoryCanvas(memobj, syms=syms, parent=self)

    def _viv_xrefsto(self):

        if self.mem_canvas._canv_curva is not None:
            xrefs = self.vw.getXrefsTo(self.mem_canvas._canv_curva)
            if len(xrefs) == 0:
                self.vw.vprint('No xrefs found!')
                return

            title = 'Xrefs To: 0x%.8x' % self.mem_canvas._canv_curva
            view = viv_q_views.VQXrefView(self.vw, self.vwqgui, xrefs=xrefs, title=title)
            dock = self.vwqgui.vqDockWidget(view, floating=True)
            dock.resize(800, 600)

    def loadDefaultRenderers(self):

        import envi.memcanvas.renderers as e_render

        # FIXME check endianness
        self.mem_canvas.addRenderer("bytes",    e_render.ByteRend())
        self.mem_canvas.addRenderer("u_int_16", e_render.ShortRend())
        self.mem_canvas.addRenderer("u_int_32", e_render.LongRend())
        self.mem_canvas.addRenderer("u_int_64", e_render.QuadRend())

        vivrend = viv_rend.WorkspaceRenderer(self.vw)
        self.mem_canvas.addRenderer('Viv', vivrend)
        self.mem_canvas.setRenderer('Viv')

    def _updateFunction(self, fva):
        for cbva, cbsize, cbfva in self.vw.getFunctionBlocks(fva):
            self.mem_canvas.renderMemoryUpdate(cbva, cbsize)

    def VTE_IAMLEADER(self, vw, event, einfo):
        user, followname = einfo

    def VWE_SYMHINT(self, vw, event, einfo):
        va, idx, hint = einfo
        self.mem_canvas.renderMemoryUpdate(va, 1)

    def VWE_ADDLOCATION(self, vw, event, einfo):
        va, size, ltype, tinfo = einfo
        self.mem_canvas.renderMemoryUpdate(va, size)

    def VWE_DELLOCATION(self, vw, event, einfo):
        va, size, ltype, tinfo = einfo
        self.mem_canvas.renderMemoryUpdate(va, size)

    def VWE_ADDFUNCTION(self, vw, event, einfo):
        va, meta = einfo
        self.mem_canvas.renderMemoryUpdate(va, 1)

    def VWE_SETFUNCMETA(self, vw, event, einfo):
        fva, key, val = einfo
        self._updateFunction(fva)

    def VWE_SETFUNCARGS(self, vw, event, einfo):
        fva, fargs = einfo
        self._updateFunction(fva)

    def VWE_COMMENT(self, vw, event, einfo):
        va, cmnt = einfo
        self.mem_canvas.renderMemoryUpdate(va, 1)

    @idlethread
    def VWE_SETNAME(self, vw, event, einfo):
        va, name = einfo
        self.mem_canvas.renderMemoryUpdate(va, 1)
        for fromva, tova, rtype, rflag in self.vw.getXrefsTo(va):
            self.mem_canvas.renderMemoryUpdate(fromva, 1)

    @idlethread
    def VTE_IAMLEADER(self, vw, event, einfo):
        user, fname = einfo

        def setFollow():
            self._following = einfo
            self.updateMemWindowTitle()

        self._follow_menu.addAction('%s - %s' % (user, fname), setFollow)

    @idlethread
    def VTE_FOLLOWME(self, vw, event, einfo):
        user, fname, expr = einfo
        if self._following != (user, fname):
            return
        self.enviNavGoto(expr)

    @idlethread
    def enviNavGoto(self, expr, sizeexpr='256', rend=''):
        if self._leading:
            self.vw.followTheLeader(str(self.mwname), str(expr))
        return e_mem_qt.VQMemoryWindow.enviNavGoto(self, expr, sizeexpr=sizeexpr, rend=rend)
