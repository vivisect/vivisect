import functools
import itertools
import traceback
import collections

import vqt.hotkeys as vq_hotkey
import vqt.saveable as vq_save
import envi.memcanvas as e_memcanvas
import envi.qt.memory as e_qt_memory
import envi.qt.memcanvas as e_qt_memcanvas

import visgraph.layouts.dynadag as vg_dynadag

import vivisect.base as viv_base
import vivisect.renderers as viv_rend
import vivisect.qt.memory as vq_memory
import vivisect.qt.ctxmenu as vq_ctxmenu
import vivisect.tools.graphutil as viv_graphutil

from PyQt5 import Qt, QtCore, QtGui, QtWebEngine, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from vqt.main import idlethread, eatevents, workthread, vqtevent

from vqt.common import *
from vivisect.const import *

class VQVivFuncgraphCanvas(vq_memory.VivCanvasBase):
    paintUp = pyqtSignal()
    paintDown = pyqtSignal()
    paintMerge = pyqtSignal()
    refreshSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        vq_memory.VivCanvasBase.__init__(self, *args, **kwargs)
        self.curs = QtGui.QCursor()

    # These have changed because QtWebEngine suxxs: https://bugreports.qt.io/browse/QTBUG-43602
    def event(self, evt):
        if evt.type() == Qt.QEvent.ChildAdded:
            evt.child().installEventFilter(self)
        elif evt.type() == Qt.QEvent.ChildRemoved:
            evt.child().removeEventFilter(self)
        return vq_memory.VivCanvasBase.event(self, evt)

    def eventFilter(self, src, evt):
        if evt.type() == Qt.QEvent.Wheel:
            return self._wheelEvent(evt)
        if evt.type() == Qt.QEvent.MouseMove:
            # Intercept mouse movements because frickin qt broke those for our shift scrolling,
            # but return False so we don't block the event from propagating to other event handlers
            # (this was the cause of the edge lines not highlighting on mouse over)
            self._mouseMoveEvent(evt)
            return False
        return vq_memory.VivCanvasBase.eventFilter(self, src, evt)

    def _wheelEvent(self, event):
        mods = QApplication.keyboardModifiers()
        if mods == QtCore.Qt.ShiftModifier:
            delta = event.angleDelta().y()
            factord = delta / 1000.0
            self.setZoomFactor(self.zoomFactor() + factord)
            event.accept()
            return True

        # e_qt_memcanvas.VQMemoryCanvas.wheelEvent(self, event)
        return False

    def _setMousePos(self, data):
        self.curs.setPos(*self.basepos)

    def _mouseMoveEvent(self, event):
        mods = QApplication.keyboardModifiers()
        if mods == QtCore.Qt.ShiftModifier:
            x = event.globalX()
            y = event.globalY()
            if self.lastpos:
                dx = -(x - self.lastpos[0])
                dy = -(y - self.lastpos[1])
                # dx = x - self.lastpos[0]
                # dy = y - self.lastpos[1]
                # TODO: Just use scrollPosition()
                self.page().runJavaScript(f'window.scrollBy({dx}, {dy});', self._setMousePos)
            else:
                self.lastpos = (x, y)
                self.basepos = (x, y)

            event.accept()
            return
        self.lastpos = None
        return e_qt_memcanvas.VQMemoryCanvas.mouseMoveEvent(self, event)

    def _renderMemoryFinish(self, cb, data):
        self._canv_rendtagid = '#memcanvas'
        cb(data)

    def _renderMemoryCallback(self, cb, data):
        if not data:
            return
        va = int(data[0])
        size = int(data[1])
        self._canv_rendtagid = '#codeblock_%.8x' % va
        # DEV: this cannot be partialmethod. It *has* to be callable
        runner = functools.partial(self._renderMemoryFinish, cb)
        e_memcanvas.MemoryCanvas.renderMemory(self, va, size, cb=runner)

    def renderMemory(self, va, size, cb):
        # For the funcgraph canvas, this will be called once per code block
        selector = 'codeblock_%.8x' % va
        js = '''var node = document.querySelector("#%s");
        if (node == null) {
            canv = document.querySelector("#memcanvas");
            if (canv != null) {
                canv.innerHTML += '<div class="codeblock" id="%s"></div>'
            }
        }
        [%d, %d]
        ''' % (selector, selector, va, size)
        runner = functools.partial(self._renderMemoryCallback, cb)
        self.page().runJavaScript(js, runner)

    def contextMenuEvent(self, event):
        if self._canv_curva is not None:
            menu = vq_ctxmenu.buildContextMenu(self.vw, va=self._canv_curva, parent=self)
        else:
            menu = QMenu(parent=self)

        self.viewmenu = menu.addMenu('view   ')
        self.viewmenu.addAction("Save frame to HTML", ACT(self._menuSaveToHtml))
        self.viewmenu.addAction("Refresh", ACT(self.refresh))
        self.viewmenu.addAction("Paint Up", ACT(self.paintUp.emit))
        self.viewmenu.addAction("Paint Down", ACT(self.paintDown.emit))
        self.viewmenu.addAction("Paint Down until remerge", ACT(self.paintMerge.emit))

        menu.exec_(event.globalPos())

    def _navExpression(self, expr):
        if self._canv_navcallback:
            self._canv_navcallback(expr)

    def refresh(self):
        '''
        Redraw the function graph (actually, tells the View to do it)
        '''
        self.reload()

    @idlethread
    def setScrollPosition(self, x, y):
        '''
        Sets the view reticle to an absolute scroll position
        '''
        self.page().runJavaScript(f'window.scroll({x}, {y})')
        eatevents()


class VQVivFuncgraphView(vq_hotkey.HotKeyMixin, e_qt_memory.EnviNavMixin, QWidget, vq_save.SaveableWidget, viv_base.VivEventCore):
    _renderDoneSignal = pyqtSignal()

    viewidx = itertools.count()

    def __init__(self, vw, vwqgui):
        self.vw = vw
        self.fva = None
        self.graph = None
        self.nodes = []
        self.vwqgui = vwqgui
        self._last_viewpt = None
        self.history = collections.deque((), 100)

        QWidget.__init__(self, parent=vwqgui)
        vq_hotkey.HotKeyMixin.__init__(self)
        viv_base.VivEventCore.__init__(self, vw)
        e_qt_memory.EnviNavMixin.__init__(self)
        self.setEnviNavName('FuncGraph%d' % next(self.viewidx))

        self._renderDoneSignal.connect(self._refresh_cb)

        self.top_box = QWidget(parent=self)
        hbox = QHBoxLayout(self.top_box)
        hbox.setContentsMargins(2, 2, 2, 2)
        hbox.setSpacing(4)

        self.histmenu = QMenu(parent=self)
        self.histmenu.aboutToShow.connect(self._histSetupMenu)

        self.hist_button = QPushButton('History', parent=self.top_box)
        self.hist_button.setMenu(self.histmenu)

        self.addr_entry = QLineEdit(parent=self.top_box)

        self.mem_canvas = VQVivFuncgraphCanvas(vw, syms=vw, parent=self)
        self.mem_canvas.setNavCallback(self.enviNavGoto)
        self.mem_canvas.refreshSignal.connect(self.refresh)
        self.mem_canvas.paintUp.connect(self._hotkey_paintUp)
        self.mem_canvas.paintDown.connect(self._hotkey_paintDown)
        self.mem_canvas.paintMerge.connect(self._hotkey_paintMerge)

        self.loadDefaultRenderers()

        self.addr_entry.returnPressed.connect(self._nav_expr)

        hbox.addWidget(self.hist_button)
        hbox.addWidget(self.addr_entry)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(4)
        vbox.addWidget(self.top_box)
        vbox.addWidget(self.mem_canvas, stretch=100)

        self.top_box.setLayout(hbox)

        self.setLayout(vbox)
        self.updateWindowTitle()

        # Do these last so we are all setup...
        vwqgui.addEventCore(self)
        vwqgui.vivMemColorSignal.connect(self.mem_canvas._applyColorMap)

        QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self, activated=self._hotkey_histback, context=3)

        # TODO: Transition theses to the above pattern (since escape/ctrl-c
        # See: https://stackoverflow.com/questions/56890831/qwidget-cannot-catch-escape-backspace-or-c-x-key-press-events
        self.addHotKey('ctrl+0', 'funcgraph:resetzoom')
        self.addHotKeyTarget('funcgraph:resetzoom', self._hotkey_resetzoom)
        self.addHotKey('ctrl+=', 'funcgraph:inczoom')
        self.addHotKeyTarget('funcgraph:inczoom', self._hotkey_inczoom)
        self.addHotKey('ctrl+-', 'funcgraph:deczoom')
        self.addHotKeyTarget('funcgraph:deczoom', self._hotkey_deczoom)
        self.addHotKey('f5', 'funcgraph:refresh')
        self.addHotKeyTarget('funcgraph:refresh', self.refresh)
        self.addHotKey('ctrl+u', 'funcgraph:paintup')
        self.addHotKeyTarget('funcgraph:paintup', self._hotkey_paintUp)
        self.addHotKey('ctrl+d', 'funcgraph:paintdown')
        self.addHotKeyTarget('funcgraph:paintdown', self._hotkey_paintDown)
        self.addHotKey('ctrl+m', 'funcgraph:paintmerge')
        self.addHotKeyTarget('funcgraph:paintmerge', self._hotkey_paintMerge)

    def _nav_expr(self):
        expr = self.addr_entry.text()
        self.history.append(expr)
        self._renderMemory()

    def _hotkey_histback(self):
        if len(self.history) >= 2:
            self.history.pop()
            expr = self.history.pop()
            self.enviNavGoto(expr)

    def _hotkey_resetzoom(self):
        self.mem_canvas.setZoomFactor(1)

    def _hotkey_inczoom(self):
        newzoom = self.mem_canvas.zoomFactor()
        if 1 > newzoom > .75:
            newzoom = 1
        elif newzoom < .5:
            newzoom += .125
        else:
            newzoom += .25

        if newzoom < 0:
            return

        self.mem_canvas.setZoomFactor(newzoom)

    def _hotkey_deczoom(self):
        newzoom = self.mem_canvas.zoomFactor()
        if newzoom <= .5:
            newzoom -= .125
        else:
            newzoom -= .25

        self.mem_canvas.setZoomFactor(newzoom)

    def refresh(self):
        '''
        Cause the Function Graph to redraw itself.
        This is particularly helpful because comments and name changes don't
        immediately display.  Perhaps someday this will update only the blocks
        that have changed since last update, and be fast, so we can update
        after every change.
        '''
        self._last_viewpt = self.mem_canvas.page().scrollPosition()
        # FIXME: history should track this as well and return to the same place
        self.clearText()
        self.fva = None
        self._renderMemory()

    @workthread
    def _refresh_cb(self):
        '''
        This is a hack to make sure that when _renderMemory() completes,
        _refresh_3() gets run after all other rendering events yet to come.
        '''
        if self._last_viewpt is None:
            return

        self.mem_canvas.setScrollPosition(self._last_viewpt.x(), self._last_viewpt.y())
        self._last_viewpt = None

    def _histSetupMenu(self):
        self.histmenu.clear()

        history = []
        for expr in self.history:
            addr = self.vw.parseExpression(expr)
            menustr = '0x%.8x' % addr
            sym = self.vw.getSymByAddr(addr)
            if sym is not None:
                menustr += ' - %s' % repr(sym)

            history.append((menustr, expr))

        history.reverse()
        for menustr,expr in history:
            self.histmenu.addAction(menustr, ACT(self._histSelected, expr))

    def _histSelected(self, expr):
        while self.history.pop() != expr:
            pass
        self.enviNavGoto(expr)

    def enviNavGoto(self, expr, sizeexpr=None):
        self.addr_entry.setText(expr)
        self.history.append( expr )
        self.updateWindowTitle()
        self._renderMemory()

    def vqGetSaveState(self):
        return { 'expr':str(self.addr_entry.text()), }

    def vqSetSaveState(self, state):
        expr = state.get('expr','')
        self.enviNavGoto(expr)

    def setMemWindowName(self, mwname):
        '''
        Set the memory window name/title prefix to the given string.
        '''
        self.setEnviNavName(mwname)
        self.updateWindowTitle()

    def updateWindowTitle(self, data=None):
        ename = self.getEnviNavName()
        expr = str(self.addr_entry.text())
        try:
            va = self.vw.parseExpression(expr)
            smartname = self.vw.getName(va, smart=True)
            self.setWindowTitle('%s: %s (0x%x)' % (ename, smartname, va))
            return va
        except:
            self.setWindowTitle('%s: %s (0x----)' % (ename, expr))

    # DEV: None of these methods are meant to be called directly by anybody but themselves,
    # since they're setup in a way to make renderFunctionGraph play nicely with pyqt5
    def _finishFuncRender(self, data):
        '''
        Update the window title and emit the renderDoneSignal so other things can run that
        are sitting on that signal
        '''
        addr = self.updateWindowTitle()
        if addr is not None:
            vqtevent('viv:colormap', {addr: 'orange'})
        self._renderDoneSignal.emit()

    def _edgesDone(self, data):
        '''
        Almost done. All this does is scroll the selected virtual address into view.
        '''
        addr = self.updateWindowTitle()
        if addr is None:
            return
        self.mem_canvas.page().runJavaScript('''
        var node = document.getElementsByName("viv:0x%.8x")[0];
        if (node != null) {
            node.scrollIntoView();
        }
        ''' % addr, self._finishFuncRender)

    def _layoutEdges(self, data):
        '''
        So...before this, we would only highlight part of the edge lines. That's because
        The dynadag layout class shoves a bunch of ghost nodes and edges into the graph
        class member, and each of those end up getting their own html polyline element.

        It'd be a massive change to the Dynadag class to rip those out, and those edges are necessary.
        So instead, we take care of things here. What the edges/nodes end up looking like in
        the graph after the dynadag layout is:
        (VA1, VA2)
        (VA3, GHOST_NODE1)
        (GHOST_NODE1, GHOST_NODE2)
        (GHOST_NODE2, GHOST_NODE3)
        (GHOST_NODE3, VA3)

        Where a bunch of ghost edges for layout purposes were inserted between the codeblocks for
        VA3 and VA4. So this function deals with that via creating a bunch of paths, keeping
        in mind the possibility that an edge line can possibly split for things like switch
        statements, and links all the points on the edge paths together to make one big
        polyline.

        This is done in two stages. First loop is to identify the possible series of ghost edges,
        and only graph the starting point, where we have (Actual_VA1, Ghost_Node). The other
        cases, like (Ghost_Node, Actual_VA2), (Ghost_Node, Ghost_Node) are ignored, since the
        second loop picks those up, and the (Actual_VA1, Actual_VA2) is dealt with since that's the
        base, super easy just do the thing case.

        The second loop just follows all the edge lines and ghost edges to make the one big polyline
        for each edge so the entire thing can be highlighted via the plineover function we've got
        stashed in envi/qt/html.py
        '''
        edgejs = ''
        svgid = 'funcgraph_%.8x' % self.fva
        graph = self.graph
        todo = []
        for eid, n1, n2, einfo in graph.getEdges():
            src = graph.getNode(n1)
            dst = graph.getNode(n2)
            points = einfo.get('edge_points')

            # if neither are ghosts, cool. just make the edge
            if not src[1].get('ghost', False) and not dst[1].get('ghost', False):
                pointstr = ' '.join(['%d,%d' % (x, y) for (x, y) in points])
                edgejs += f'drawSvgLine("{svgid}", "edge_%.8s", "{pointstr}");' % eid
                continue

            # if both are ghosts, w/e. skip it. we'll pick it up later
            if src[1].get('ghost', False) and dst[1].get('ghost', False):
                continue

            # if n1 is a ghost and n2 is not, that's fine. We'll pick it up later
            if src[1].get('ghost', False) and not dst[1].get('ghost', False):
                continue

            # ok. juicy case
            # if n1 is not a ghost and n2 is, we gotta build all the possible paths from this guy out
            todo.append((eid, n1, n2, einfo))

        # Build out the pointstr lines starting from the concrete n1, following the ghost n2's
        for edge in todo:
            eid, n1, n2, einfo = edge
            points = einfo.get('edge_points')
            splits = [([n1, n2], points)]

            while splits:
                path, points = splits.pop()
                node = graph.getNode(path[-1])

                # we've hit the end of this chain, finish the points chain
                # and add the completed points to a done list
                if not node[1].get('ghost', False):
                    pointstr = ' '.join(['%d,%d' % (x, y) for (x, y) in points])
                    edgejs += f'drawSvgLine("{svgid}", "edge_%.8s", "{pointstr}");' % eid
                    continue

                # Otherwise, deal with splits
                for ref in graph.getRefsFrom(node):
                    eid, n1, n2, einfo = ref
                    newpoints = einfo.get('edge_points')
                    path.append(n2)
                    points.extend(newpoints)
                    splits.append((path, points))

        self.mem_canvas.page().runJavaScript(edgejs, self._edgesDone)

    def _layoutDynadag(self, data):
        '''
        This actually lays codeblocks out on the memory canvas where they should be
        '''
        for nid, nprops in self.graph.getNodes():
            width, height = data[str(nid)]
            self.graph.setNodeProp((nid, nprops), "size", (width, height+7))
        self.dylayout = vg_dynadag.DynadagLayout(self.graph, barry=20)
        self.dylayout.layoutGraph()

        width, height = self.dylayout.getLayoutSize()

        svgid = 'funcgraph_%.8x' % self.fva
        svgjs = f'svgwoot("vbody", "{svgid}", {width+18}, {height});'
        for nid, nprops in self.graph.getNodes():
            cbva = nprops.get('cbva')
            if cbva is None:
                continue

            xpos, ypos = nprops.get('position')

            foid = 'fo_cb_%.8x' % cbva
            cbid = 'codeblock_%.8x' % cbva

            js = f'''
            var node = document.getElementById("{cbid}");
            addSvgForeignObject("{svgid}", "{foid}", node.offsetWidth+16, node.offsetHeight+7);
            addSvgForeignHtmlElement("{foid}", "{cbid}");
            moveSvgElement("{foid}", {xpos}, {ypos});
            '''
            svgjs += js

        self.mem_canvas.page().runJavaScript(svgjs, self._layoutEdges)

    def _getNodeSizes(self):
        '''
        Actually grab all the sizes of the codeblocks that we renderd in the many calls to
        _renderCodeBlock. runJavaScript has some limited ability to return values from
        javascript land to python town, so in this case, we're shoving the offsetWidth
        and offsetHeight of each of the codeblocks into a dictionary that _layoutDynadag
        can reach into to get the sizes so it can set them for use in the line layout stuff
        '''
        js = 'var sizes = {};'

        for nid, nprops in self.graph.getNodes():
            try:
                cbname = 'codeblock_%.8x' % nid
            except Exception as e:
                self.vw.vprint('Failed to build cbname during funcgraph building: %s' % str(e))
                return
            js += f'''
            sizes[{nid}] = [document.getElementById("{cbname}").offsetWidth, document.getElementById("{cbname}").offsetHeight];
            '''
        js += 'sizes;'
        self.mem_canvas.page().runJavaScript(js, self._layoutDynadag)

    def _renderCodeBlock(self, data):
        '''
        Render a codeblock to the canvas. self.mem_canvas.renderMemory ends up having
        to run a bunch of javascript to render the block to the screen. So we do them
        one at a time, chaining callbacks together with some state in self.nodes to let us
        know when we've rendered all the codeblocks in the function.

        One day we'll optimize this to be one big blob of JS. But not today. But this could use
        some safety rails if the user switches functions in the middle of rendering
        '''
        if len(self.nodes):
            node = self.nodes.pop(0)
            cbva = node[1].get('cbva')
            cbsize = node[1].get('cbsize')
            self.mem_canvas.renderMemory(cbva, cbsize, self._renderCodeBlock)
        else:
            self._getNodeSizes()

    def renderFunctionGraph(self, fva=None, graph=None):
        '''
        Begins the process of drawing the function graph to the canvas.

        So, this is a bit of complicated mess due to how PyQt5's runJavaScript method works.
        runJavaScript is asynchronous, but not like actual python async, but Qt's async variant
        with their event loop. The only way to get some level of a guarantee that the
        javascript ran (which we need for getting the size of codeblocks and line layouts) is
        via the secondary parameter, which is a callback that gets run when the javascript
        completes. That being said, technically according to their docs, the callback is guaranteed
        to be run, but it might be during page destruction. In practice it's somewhat responsive.
        runJavascript also doesn't check if the DOM has been created. So...yea. In practice
        that doesn't matter too much, but something to keep in mind.

        So the general method is to build up a bunch of javascript that we need to run in order
        to render the codeblocks to get their sizes, layout the graph lines, realign everything
        nicely, etc. And it's all callbacks, all the way down.
        '''
        if fva is not None:
            self.fva = fva

        if graph is None:
            try:
                graph = viv_graphutil.buildFunctionGraph(self.vw, fva, revloop=True)
            except Exception as e:
                self.vw.vprint(f'Error building function graph for {fva} ({str(e)}')
                self.vw.vprint(traceback.format_exc())
                return

        self.graph = graph

        # Go through each of the nodes and render them so we know sizes
        self.nodes = self.graph.getNodes()
        if len(self.nodes):
            node = self.nodes.pop(0)
            cbva = node[1].get('cbva')
            cbsize = node[1].get('cbsize')
            self.mem_canvas.renderMemory(cbva, cbsize, self._renderCodeBlock)

    def _renderedSameFva(self, data):
        addr = self.updateWindowTitle()
        if addr is not None:
            vqtevent('viv:colormap', {addr: 'orange'})

    @idlethread
    def _renderMemory(self):
        try:

            expr = str(self.addr_entry.text())
            if not expr:
                return

            try:
                addr = self.vw.parseExpression(expr)
            except Exception as e:
                self.mem_canvas.addText('Invalid Address: %s (%s)' % (expr, e))
                return

            # get a location anchor if one exists, otherwise, we may end up in no-man's land,
            # since we rely on labels, which only exist for the base of a location.
            loc = self.vw.getLocation(addr)
            if loc is not None:
                addr = loc[L_VA]

            # check if we're already rendering this function. if so, just scroll to addr
            fva = self.vw.getFunction(addr)
            if fva is None:
                self.vw.vprint('0x%.8x is not in a function!' % addr)
                return

            page = self.mem_canvas.page()
            if fva == self.fva:
                page.runJavaScript('''
                document.getElementsByName("viv:0x%.8x")[0].scrollIntoView();
                %d;
                ''' % (addr, addr), self._renderedSameFva)
                return
            # if we're rendering a different function, get to work!
            self.clearText()
            self.renderFunctionGraph(fva)

        except Exception as e:
            self.vw.vprint('_renderMemory hit exception: %s' % str(e))
            self.vw.vprint('%s' % traceback.format_exc())

    def loadDefaultRenderers(self):
        vivrend = viv_rend.WorkspaceRenderer(self.vw)
        self.mem_canvas.addRenderer('Viv', vivrend)
        self.mem_canvas.setRenderer('Viv')

    def clearText(self):
        # Pop the svg and reset #memcanvas
        js = ''
        if self.fva is not None:
            svgid = 'funcgraph_%.8x' % self.fva
            js += '''
            var node = document.getElementById("%s");
            if (node != null) {
                node.remove();
            }
            ''' % svgid

        js += '''
        var canv = document.querySelector("#memcanvas");
        if (canv != null) {
            canv.innerHTML = "";
        }
        '''
        self.mem_canvas.page().runJavaScript(js)

    def _hotkey_paintUp(self, va=None):
        '''
        Paint the VA's from the selected basic block up to all possible
        non-looping starting points.
        '''
        graph = viv_graphutil.buildFunctionGraph(self.vw, self.fva, revloop=True)
        startva = self.mem_canvas._canv_curva
        if startva is None:
            return

        viv_graphutil.preRouteGraphUp(graph, startva, mark='hit')

        count = 0
        colormap = {}
        for node in graph.getNodesByProp('hit'):
            count += 1
            off = 0
            cbsize = node[1].get('cbsize')
            if cbsize is None:
                raise Exception('node has no cbsize: %s' % repr(node))

            # step through opcode for a node
            while off < cbsize:
                op = self.vw.parseOpcode(node[0] + off)
                colormap[op.va] = 'orange'
                off += len(op)

        self.vw.vprint("Colored Blocks: %d" % count)
        vqtevent('viv:colormap', colormap)
        return colormap

    def _hotkey_paintDown(self, va=None):
        '''
        Paint the VA's from the selected basic block down to all possible
        non-looping blocks.  This is valuable for determining what code can
        execute from any starting basic block, without a loop.
        '''
        # TODO: make overlapping colors available for multiple paintings

        graph = viv_graphutil.buildFunctionGraph(self.vw, self.fva, revloop=True)
        startva = self.mem_canvas._canv_curva
        if startva is None:
            return

        viv_graphutil.preRouteGraphDown(graph, startva, mark='hit')

        count = 0
        colormap = {}
        for node in graph.getNodesByProp('hit'):
            count += 1
            off = 0
            cbsize = node[1].get('cbsize')
            if cbsize is None:
                raise Exception('node has no cbsize: %s' % repr(node))

            # step through opcode for a node
            while off < cbsize:
                op = self.vw.parseOpcode(node[0] + off)
                colormap[op.va] = 'brown'
                off += len(op)

        self.vw.vprint("Colored Blocks: %d" % count)
        vqtevent('viv:colormap', colormap)
        return colormap

    def _hotkey_paintMerge(self, va=None):
        '''
        same as paintdown but only until the graph remerges
        '''

        graph = viv_graphutil.buildFunctionGraph(self.vw, self.fva, revloop=True)
        startva = self.mem_canvas._canv_curva
        if startva is None:
            return

        viv_graphutil.findRemergeDown(graph, startva)

        count = 0
        colormap = {}
        for node in graph.getNodesByProp('hit'):
            count += 1
            off = 0
            cbsize = node[1].get('cbsize')
            if cbsize is None:
                raise Exception('node has no cbsize: %s' % repr(node))

            # step through opcode for a node
            while off < cbsize:
                op = self.vw.parseOpcode(node[0] + off)
                colormap[op.va] = 'brown'
                off += len(op)

        self.vw.vprint("Colored Blocks: %d" % count)
        vqtevent('viv:colormap', colormap)
        return colormap
