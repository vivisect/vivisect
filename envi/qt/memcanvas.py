import cgi
try:
    from PyQt5 import QtCore, QtGui, QtWebKit, QtWebKitWidgets
    from PyQt5.QtWebKitWidgets import *
    from PyQt5.QtWidgets import *
except:
    from PyQt4 import QtCore, QtGui, QtWebKit
    from PyQt4.QtWebKit import *
    from PyQt4.QtGui import *


import vqt.main as vq_main
import vqt.colors as vq_colors
import vqt.hotkeys as vq_hotkey
import envi.qt.html as e_q_html
import envi.qt.jquery as e_q_jquery
import envi.memcanvas as e_memcanvas

qt_horizontal = 1
qt_vertical = 2

from vqt.main import *
from vqt.common import *

class LoggerPage(QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        print('%s line %d: %s' % (source, line, msg))

class VQMemoryCanvas(e_memcanvas.MemoryCanvas, QWebView):

    def __init__(self, mem, syms=None, parent=None, **kwargs):
        e_memcanvas.MemoryCanvas.__init__(self, mem=mem, syms=syms)
        QWebView.__init__(self, parent=parent, **kwargs)

        self._canv_cache = None
        self._canv_curva = None
        self._canv_rendtagid = '#memcanvas'
        self._canv_rend_middle = False

        self.setPage(LoggerPage())

        htmlpage = e_q_html.template.replace('{{{jquery}}}', e_q_jquery.jquery_2_1_0)
        self.setContent(htmlpage)

        frame = self.page().mainFrame()
        frame.evaluateJavaScript(e_q_jquery.jquery_2_1_0)
        frame.addToJavaScriptWindowObject('vnav', self)
        frame.contentsSizeChanged.connect(self._frameContentsSizeChanged)

        # Allow our parent to handle these...
        self.setAcceptDrops(False)

    @QtCore.pyqtSlot(str)
    def showMessage(self, message):
        print "Message from website:", message

    def renderMemory(self, va, size, rend=None):

        if self._canv_rend_middle:
            vmap = self.mem.getMemoryMap(va)
            if vmap == None:
                raise Exception('Invalid Address:%s' % hex(va))

            origva = va
            va, szdiff = self._loc_helper(max(va - size, vmap[0]))
            size += size + szdiff

        ret = e_memcanvas.MemoryCanvas.renderMemory(self, va, size, rend=rend)

        if self._canv_rend_middle:
            self._scrollToVa(origva)

        return ret

    def _frameContentsSizeChanged(self, size):
        if self._canv_scrolled:
            frame = self.page().mainFrame()
            frame.setScrollBarValue(qt_vertical, 0x0fffffff)

    @idlethread
    def _scrollToVa(self, va):
        vq_main.eatevents()  # Let all render events go first
        self.page().mainFrame().scrollToAnchor('viv:0x%.8x' % va)
        # self._selectVa(va)

    @idlethread
    def _selectVa(self, va):
        frame = self.page().mainFrame()
        frame.evaluateJavaScript('selectva("0x%.8x")' % va)
        frame.evaluateJavaScript('scrolltoid("a_%.8x")' % va)

    def _beginRenderMemory(self, va, size, rend):
        self._canv_cache = ''

    def _endRenderMemory(self, va, size, rend):
        self._appendInside(self._canv_cache)
        self._canv_cache = None

    def _beginRenderVa(self, va):
        self._add_raw('<a name="viv:0x%.8x" id="a_%.8x">' % (va, va))

    def _endRenderVa(self, va):
        self._add_raw('</a>')

    def _beginUpdateVas(self, valist):

        self._canv_cache = ''
        frame = self.page().mainFrame()
        elem = frame.findFirstElement('a#a_%.8x' % valist[0][0])
        elem.prependOutside('<update id="updatetmp"></update>')

        for va, size in valist:
            elem = frame.findFirstElement('a#a_%.8x' % va)
            elem.removeFromDocument()

    def _endUpdateVas(self):
        elem = self.page().mainFrame().findFirstElement('update#updatetmp')
        elem.appendOutside(self._canv_cache)
        elem.removeFromDocument()
        self._canv_cache = None

    def _beginRenderPrepend(self):
        self._canv_cache = ''
        self._canv_ppjump = self._canv_rendvas[0][0]

    def _endRenderPrepend(self):
        frame = self.page().mainFrame()
        elem = frame.findFirstElement(self._canv_rendtagid)
        elem.prependInside(self._canv_cache)
        self._canv_cache = None
        self._scrollToVa(self._canv_ppjump)

    def _beginRenderAppend(self):
        self._canv_cache = ''

    def _endRenderAppend(self):
        frame = self.page().mainFrame()
        elem = frame.findFirstElement(self._canv_rendtagid)
        elem.appendInside(self._canv_cache)
        self._canv_cache = None

    def getNameTag(self, name, typename='name'):
        '''
        Return a "tag" for this memory canvas.  In the case of the
        qt tags, they are a tuple of html text (<opentag>, <closetag>)
        '''
        clsname = 'envi-%s' % typename
        namehex = name.lower().encode('hex')
        subclsname = 'envi-%s-%s' % (typename,namehex)
        return ('<span class="%s %s" envitag="%s" envival="%s" onclick="nameclick(this)">' % (clsname,subclsname,typename,namehex), '</span>')

    def getVaTag(self, va):
        # The "class" will be the same that we get back from goto event
        return ('<span class="envi-va envi-va-0x%.8x" va="0x%.8x" ondblclick="vagoto(this)" oncontextmenu="vaclick(this)" onclick="vaclick(this)">' % (va,va), '</span>')

    @QtCore.pyqtSlot(str)
    def _jsGotoExpr(self, expr):
        # The routine used by the javascript code to trigger nav events
        if self._canv_navcallback:
            self._canv_navcallback(expr)

    @QtCore.pyqtSlot(str)
    def _jsSetCurVa(self, vastr):
        self._canv_curva = int(str(vastr), 0)

    # NOTE: doing append / scroll seperately allows render to catch up
    @idlethread
    def _appendInside(self, text):
        frame = self.page().mainFrame()
        elem = frame.findFirstElement(self._canv_rendtagid)
        elem.appendInside(text)

    def _add_raw(self, text):
        # If we are in a call to renderMemory, cache til the end.
        if self._canv_cache is not None:
            self._canv_cache += text
            return

        self._appendInside(text)

    def addText(self, text, tag=None):
        text = cgi.escape(text)

        if tag is not None:
            otag, ctag = tag
            text = otag + text + ctag

        self._add_raw(text)

    @idlethreadsync
    def clearCanvas(self):
        frame = self.page().mainFrame()
        elem = frame.findFirstElement(self._canv_rendtagid)
        elem.setInnerXml('')

    def contextMenuEvent(self, event):

        va = self._canv_curva
        menu = QMenu()
        if self._canv_curva is not None:
            self.initMemWindowMenu(va, menu)

        viewmenu = menu.addMenu('view   ')
        viewmenu.addAction("Save frame to HTML", ACT(self._menuSaveToHtml))

        menu.exec_(event.globalPos())

    def initMemWindowMenu(self, va, menu):
        initMemSendtoMenu('0x%.8x' % va, menu)

    def _menuSaveToHtml(self):
        fname = getSaveFileName(self, 'Save As HTML...')
        if fname is not None:
            fname = str(fname)
            if len(fname):
                html = self.page().mainFrame().toHtml()
                file(fname, 'w').write(html)


def getNavTargetNames():
    '''
    Returns a list of Memory View names.
    Populated by vqt in a seperate thread, thus is time-sensitive.  If the
    list is accessed too quickly, some valid names may not yet be inserted.
    '''
    ret = []
    vqtevent('envi:nav:getnames', ret)
    return ret


def initMemSendtoMenu(expr, menu):
    for name in set(getNavTargetNames()):
        args = (name, expr, None)
        menu.addAction('sendto: %s' % name, ACT(vqtevent, 'envi:nav:expr', args))
