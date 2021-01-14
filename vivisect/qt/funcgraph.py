import vqt.hotkeys as vq_hotkey
import vqt.saveable as vq_save
import envi.qt.memory as e_mem_qt
import envi.memcanvas as e_memcanvas
import envi.qt.memory as e_qt_memory
import envi.qt.memcanvas as e_qt_memcanvas

import visgraph.layouts.dynadag as vg_dynadag

import vivisect.base as viv_base
import vivisect.renderers as viv_rend
import vivisect.qt.memory as vq_memory
import vivisect.qt.ctxmenu as vq_ctxmenu
import vivisect.tools.graphutil as viv_graphutil

try:
    from PyQt5.QtCore   import pyqtSignal, QPoint, PYQT_VERSION_STR
    from PyQt5          import QtCore, QtGui, QtWebKit
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtCore   import pyqtSignal, QPoint, PYQT_VERSION_STR
    from PyQt4          import QtCore, QtGui, QtWebKit
    from PyQt4.QtGui    import *

from vqt.main       import idlethread, idlethreadsync, eatevents, vqtconnect, workthread, vqtevent

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

    def wheelEvent(self, event):
        mods = QApplication.keyboardModifiers()
        if mods == QtCore.Qt.ShiftModifier:
            delta = event.angleDelta().y()
            factord = delta / 1000.0
            self.setZoomFactor( self.zoomFactor() + factord )
            event.accept()
            return
        
        return e_qt_memcanvas.VQMemoryCanvas.wheelEvent(self, event)

    def mouseMoveEvent (self, event):
        mods = QApplication.keyboardModifiers()
        if mods == QtCore.Qt.ShiftModifier:
            x = event.globalX()
            y = event.globalY()
            if self.lastpos:
                dx = -(x - self.lastpos[0])
                dy = -(y - self.lastpos[1])
                #dx = x - self.lastpos[0]
                #dy = y - self.lastpos[1]
                self.page().mainFrame().scroll(dx,dy)

                self.curs.setPos(*self.basepos)
            else:
                self.lastpos = (x,y)
                self.basepos = (x,y)

            event.accept()
            return
        self.lastpos = None
        return e_qt_memcanvas.VQMemoryCanvas.mouseMoveEvent(self, event)

    def renderMemory(self, va, size, rend=None):
        # For the funcgraph canvas, this will be called once per code block

        # Check if we have a codeblock element already...
        frame = self.page().mainFrame()
        canvelem = frame.findFirstElement('#memcanvas')

        elem = frame.findFirstElement('#codeblock_%.8x' % va)
        if elem.isNull():
            # Lets add a codeblock element for this
            canvelem.appendInside('<div class="codeblock" id="codeblock_%.8x"></div>' % va)

        self._canv_rendtagid = '#codeblock_%.8x' % va

        ret = e_memcanvas.MemoryCanvas.renderMemory(self, va, size, rend=rend)

        self._canv_rendtagid = '#memcanvas'

        return ret

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
        self.refreshSignal.emit()

    @idlethread
    def setScrollPosition(self, x, y):
        '''
        Sets the view reticle to an absolute scroll position
        '''
        point = QPoint(x, y)
        self.page().mainFrame().setScrollPosition(point)

funcgraph_js = '''
svgns = "http://www.w3.org/2000/svg";

function createSvgElement(ename, attrs) {
    var elem = document.createElementNS(svgns, ename);
    for (var aname in attrs) {
        elem.setAttribute(aname, attrs[aname]);
    }
    return elem
}

function svgwoot(parentid, svgid, width, height) {

    var elem = document.getElementById(parentid);

    var svgelem = createSvgElement("svg", { "height":height.toString(), "width":width.toString() })
    svgelem.setAttribute("id", svgid);

    elem.appendChild(svgelem);
}

function addSvgForeignObject(svgid, foid, width, height) {
    var foattrs = {
        "class":"node",
        "id":foid,
        "width":width,
        "height":height
    };

    var foelem = createSvgElement("foreignObject", foattrs);

    var svgelem = document.getElementById(svgid);
    svgelem.appendChild(foelem);
}

function addSvgForeignHtmlElement(foid, htmlid) {

    var foelem = document.getElementById(foid);
    var htmlelem = document.getElementById(htmlid);
    htmlelem.parentNode.removeChild(htmlelem);

    //foelem.appendChild(htmlid);

    var newbody = document.createElement("body");
    newbody.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");
    newbody.appendChild( htmlelem );

    foelem.appendChild(newbody);
}

function moveSvgElement(elemid, xpos, ypos) {
    var elem = document.getElementById(elemid);
    elem.setAttribute("x", xpos);
    elem.setAttribute("y", ypos);
}

function plineover(pline) {
    pline.setAttribute("style", "fill:none;stroke:yellow;stroke-width:2")
}

function plineout(pline) {
    pline.setAttribute("style", "fill:none;stroke:green;stroke-width:2")
}


function drawSvgLine(svgid, lineid, points) {
    var plineattrs = {
        "id":lineid,
        "points":points,
        "style":"fill:none;stroke:green;stroke-width:2",
        "onmouseover":"plineover(this)",
        "onmouseout":"plineout(this)"
    };

    var lelem = createSvgElement("polyline", plineattrs);
    var svgelem = document.getElementById(svgid);

    //var rule = "polyline." + lineclass + ":hover { stroke: red; }";
    //document.styleSheets[0].insertRule(rule, 0);

    svgelem.appendChild(lelem);
}
'''

def compat_getFrameDimensions(frame, cbname):
    if PYQT_VERSION_STR.startswith('4'):
        girth, ok = frame.evaluateJavaScript('document.getElementById("%s").offsetWidth;' % cbname).toInt()
        height, ok = frame.evaluateJavaScript('document.getElementById("%s").offsetHeight;' % cbname).toInt()
    else:
        girth = int(frame.evaluateJavaScript('document.getElementById("%s").offsetWidth;' % cbname))
        height = frame.evaluateJavaScript('document.getElementById("%s").offsetHeight;' % cbname)
    return girth, height


import itertools
import collections

class VQVivFuncgraphView(vq_hotkey.HotKeyMixin, e_qt_memory.EnviNavMixin, QWidget, vq_save.SaveableWidget, viv_base.VivEventCore):
    _renderDoneSignal = pyqtSignal()

    viewidx = itertools.count()

    def __init__(self, vw, vwqgui):
        self.vw = vw
        self.fva = None
        self.graph = None
        self.vwqgui = vwqgui
        self._last_viewpt = None
        self.history = collections.deque((),100)

        QWidget.__init__(self, parent=vwqgui)
        vq_hotkey.HotKeyMixin.__init__(self)
        viv_base.VivEventCore.__init__(self, vw)
        e_qt_memory.EnviNavMixin.__init__(self)
        self.setEnviNavName('FuncGraph%d' % self.viewidx.next())

        self._renderDoneSignal.connect(self._refresh_cb)

        self.top_box = QWidget(parent=self)
        hbox = QHBoxLayout(self.top_box)
        hbox.setContentsMargins(2, 2, 2, 2)
        hbox.setSpacing(4)

        self.histmenu = QMenu(parent=self)
        self.histmenu.aboutToShow.connect( self._histSetupMenu )

        self.hist_button = QPushButton('History', parent=self.top_box)
        self.hist_button.setMenu(self.histmenu)

        self.addr_entry  = QLineEdit(parent=self.top_box)

        self.mem_canvas = VQVivFuncgraphCanvas(vw, syms=vw, parent=self)
        self.mem_canvas.setNavCallback(self.enviNavGoto)
        self.mem_canvas.refreshSignal.connect(self.refresh)
        self.mem_canvas.paintUp.connect(self._hotkey_paintUp)
        self.mem_canvas.paintDown.connect(self._hotkey_paintDown)
        self.mem_canvas.paintMerge.connect(self._hotkey_paintMerge)

        self.loadDefaultRenderers()

        self.addr_entry.returnPressed.connect(self._renderMemory)

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
        vwqgui.vivMemColorSignal.connect( self.mem_canvas._applyColorMap )

        self.addHotKey('esc', 'mem:histback')
        self.addHotKeyTarget('mem:histback', self._hotkey_histback)
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

    def _hotkey_histback(self):
        if len(self.history) >= 2:
            self.history.pop()
            expr = self.history.pop()
            self.enviNavGoto(expr)

    def _hotkey_resetzoom(self):
        self.mem_canvas.setZoomFactor( 1 )

    def _hotkey_inczoom(self):
        newzoom = self.mem_canvas.zoomFactor()
        if 1 > newzoom > .75:
            newzoom = 1
        elif newzoom < .5:
            newzoom += .125
        else:
            newzoom += .25

        if newzoom < 0: return

        #self.vw.vprint("NEW ZOOM    %f" % newzoom)
        self.mem_canvas.setZoomFactor(newzoom)

    def _hotkey_deczoom(self):
        newzoom = self.mem_canvas.zoomFactor()
        if newzoom <= .5:
            newzoom -= .125
        else:
            newzoom -= .25

        #self.vw.vprint("NEW ZOOM    %f" % newzoom)
        self.mem_canvas.setZoomFactor(newzoom)

    def refresh(self):
        '''
        Cause the Function Graph to redraw itself.
        This is particularly helpful because comments and name changes don't
        immediately display.  Perhaps someday this will update only the blocks
        that have changed since last update, and be fast, so we can update
        after every change.  
        '''
        self._last_viewpt = self.mem_canvas.page().mainFrame().scrollPosition()
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

            history.append( (menustr, expr) )

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

    def updateWindowTitle(self):
        ename = self.getEnviNavName()
        expr = str(self.addr_entry.text())
        try:
            va = self.vw.parseExpression(expr)
            smartname = self.vw.getName(va, smart=True)
            self.setWindowTitle('%s: %s (0x%x)' % (ename, smartname, va))
        except:
            self.setWindowTitle('%s: %s (0x----)' % (ename, expr))


    def _buttonSaveAs(self):
        frame = self.mem_canvas.page().mainFrame()
        elem = frame.findFirstElement('#mainhtml')
        h = elem.toOuterXml()
        #h = frame.toHtml()
        with open('test.html', 'wb') as f:
            f.write(str(h))

    def renderFunctionGraph(self, fva, graph=None):

        self.fva = fva
        #self.graph = self.vw.getFunctionGraph(fva)
        if graph is None:
            try:
                graph = viv_graphutil.buildFunctionGraph(self.vw, fva, revloop=True)
            except Exception as e:
                import sys
                sys.excepthook(*sys.exc_info())
                return

        self.graph = graph

        # Go through each of the nodes and render them so we know sizes
        for node in self.graph.getNodes():
            #cbva,cbsize = self.graph.getCodeBlockBounds(node)
            cbva = node[1].get('cbva')
            cbsize = node[1].get('cbsize')
            self.mem_canvas.renderMemory(cbva, cbsize)

        # Let the renders complete...
        eatevents()

        frame = self.mem_canvas.page().mainFrame()
        frame.evaluateJavaScript(funcgraph_js)

        for nid,nprops in self.graph.getNodes():
            cbva = nprops.get('cbva')

            cbname = 'codeblock_%.8x' % cbva
            #girth, ok = frame.evaluateJavaScript('document.getElementById("%s").offsetWidth;' % cbname).toInt()
            #girth = int(frame.evaluateJavaScript('document.getElementById("%s").offsetWidth;' % cbname))
            #height, ok = frame.evaluateJavaScript('document.getElementById("%s").offsetHeight;' % cbname).toInt()
            #height = frame.evaluateJavaScript('document.getElementById("%s").offsetHeight;' % cbname)
            girth, height = compat_getFrameDimensions(frame, cbname)
            self.graph.setNodeProp((nid,nprops), "size", (girth, height))

        self.dylayout = vg_dynadag.DynadagLayout(self.graph)
        self.dylayout._barry_count = 20
        self.dylayout.layoutGraph()

        width, height = self.dylayout.getLayoutSize()

        svgid = 'funcgraph_%.8x' % fva
        frame.evaluateJavaScript('svgwoot("vbody", "%s", %d, %d);' % (svgid, width+18, height))

        for nid,nprops in self.graph.getNodes():

            cbva = nprops.get('cbva')
            if cbva is None:
                continue

            xpos, ypos = nprops.get('position')
            girth, height = nprops.get('size')

            foid = 'fo_cb_%.8x' % cbva
            cbid = 'codeblock_%.8x' % cbva

            frame.evaluateJavaScript('addSvgForeignObject("%s", "%s", %d, %d);' % (svgid, foid, girth+16, height))
            frame.evaluateJavaScript('addSvgForeignHtmlElement("%s", "%s");' % (foid, cbid))
            frame.evaluateJavaScript('moveSvgElement("%s", %d, %d);' % (foid, xpos, ypos))

        # Draw in some edge lines!
        for eid, n1, n2, einfo in self.graph.getEdges():
            points = einfo.get('edge_points')
            pointstr = ' '.join(['%d,%d' % (x,y) for (x,y) in points ])

            frame.evaluateJavaScript('drawSvgLine("%s", "edge_%.8s", "%s");' % (svgid, eid, pointstr))

        self.updateWindowTitle()

    # FIXME
    #def closeEvent(self, event):
        # FIXME this doesn't actually do anything...
        #self.parentWidget().delEventCore(self)
        #return e_mem_qt.VQMemoryWindow.closeEvent(self, event)


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

            if fva == self.fva:
                self.mem_canvas.page().mainFrame().scrollToAnchor('viv:0x%.8x' % addr)
                vqtevent('viv:colormap', {addr: 'orange'})
                self.updateWindowTitle()
                return

            # if we're rendering a different function, get to work!
            self.clearText()
            self.renderFunctionGraph(fva)
            self.mem_canvas.page().mainFrame().scrollToAnchor('viv:0x%.8x' % addr)
            self.updateWindowTitle()
            self.mem_canvas.page().mainFrame().scrollToAnchor('viv:0x%.8x' % addr)
            vqtevent('viv:colormap', {addr: 'orange'})
            self.updateWindowTitle()

            self._renderDoneSignal.emit()
        except Exception as e:
            self.vw.vprint('_renderMemory hit exception: %s' % str(e))
            self.vw.vprint('%s' % traceback.format_exc())

    def loadDefaultRenderers(self):
        vivrend = viv_rend.WorkspaceRenderer(self.vw)
        self.mem_canvas.addRenderer('Viv', vivrend)
        self.mem_canvas.setRenderer('Viv')

    def clearText(self):
        # Pop the svg and reset #memcanvas
        frame = self.mem_canvas.page().mainFrame()
        if self.fva is not None:
            svgid = '#funcgraph_%.8x' % self.fva
            svgelem = frame.findFirstElement(svgid)
            svgelem.removeFromDocument()

        memelem = frame.findFirstElement('#memcanvas')
        memelem.setInnerXml(' ')

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
        #TODO: make overlapping colors available for multiple paintings

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

#@idlethread
#def showFunctionGraph(fva, vw, vwqgui):
    #view = VQVivFuncgraphView(fva, vw, vwqgui)
    #view.show()

