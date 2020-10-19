import html
import binascii

from PyQt5 import QtCore, QtGui, QtWebEngine, QtWebEngineWidgets
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

import vqt.main as vq_main
import envi.exc as e_exc
import envi.qt.html as e_q_html
import envi.qt.jquery as e_q_jquery
import envi.memcanvas as e_memcanvas

qt_horizontal = 1
qt_vertical = 2

from vqt.main import *
from vqt.common import *


class LoggerPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, source):
        print('[%s]: %s line %d: %s' % (level, source, line, msg))


class VQMemoryCanvas(e_memcanvas.MemoryCanvas, QWebEngineView):

    #syncSignal = QtCore.pyqtSignal()
    def __init__(self, mem, syms=None, parent=None, **kwargs):
        e_memcanvas.MemoryCanvas.__init__(self, mem=mem, syms=syms)
        QWebEngineView.__init__(self, parent=parent, **kwargs)

        self._canv_cache = None
        self._canv_curva = None
        self._canv_rendtagid = '#memcanvas'
        self._canv_rend_middle = False
        self._log_page = LoggerPage()
        self.setPage(self._log_page)
        self.fname = None

        htmlpage = e_q_html.template.replace('{{{jquery}}}', e_q_jquery.jquery_2_1_0)
        page = self.page()
        page.setHtml(htmlpage)
        channel = QWebChannel()
        channel.registerObject('vnav', self)
        page.setWebChannel(channel)
        loop = QtCore.QEventLoop()
        page.loadFinished.connect(loop.quit)
        loop.exec()
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers)
        page.runJavaScript(e_q_jquery.jquery_2_1_0)
        self.forceSync()

        page.contentsSizeChanged.connect(self._frameContentsSizeChanged)

        # Allow our parent to handle these...
        self.setAcceptDrops(False)

    def forceSync(self):
        cthr = QtCore.QThread.currentThread()
        loop = QtCore.QThread.eventDispatcher(cthr)
        loop.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers | QtCore.QEventLoop.WaitForMoreEvents)

    def renderMemory(self, va, size, rend=None):

        if self._canv_rend_middle:
            vmap = self.mem.getMemoryMap(va)
            if vmap is None:
                raise e_exc.InvalidAddress(va)

            origva = va
            va, szdiff = self._loc_helper(max(va - size, vmap[0]))
            size += size + szdiff

        ret = e_memcanvas.MemoryCanvas.renderMemory(self, va, size, rend=rend)

        if self._canv_rend_middle:
            self._scrollToVa(origva)

        return ret

    def _frameContentsSizeChanged(self, size):
        if self._canv_scrolled:
            page = self.page()
            page.runJavaScript('window.scrollTo(1, 0x0fffffff);')

    @idlethread
    def _scrollToVa(self, va):
        vq_main.eatevents()  # Let all render events go first
        page = self.page()
        selector = 'viv:0x%.8x' % va
        page.runJavaScript(f'node = document.querySelector({selector}); node.scrollIntoView()')

    @idlethread
    def _selectVa(self, va):
        page = self.page()
        page.runJavaScript('selectva("0x%.8x")' % va)
        page.runJavaScript('scrolltoid("a_%.8x")' % va)

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

        page = self.page()
        selector = 'a#a_%.8x' % valist[0][0]
        page.runJavaScript(f'''node = document.querySelector({selector});
        node.outerHTML = '<update id="updatetmp"></update>' + node.outerHTML;
        ''')

        for va, size in valist:
            selector = 'a#a_%.8x' % va
            page.runJavaScript(f'document.querySelector({selector}).remove()')

    def _endUpdateVas(self):
        page = self.page()
        page.runJavaScript('''node = document.querySelector('update#updatetmp');
        node.outerHTML = {self._canv_cache} + node.outerHTML;
        ''')
        self._canv_cache = None

    def _beginRenderPrepend(self):
        self._canv_cache = ''
        self._canv_ppjump = self._canv_rendvas[0][0]

    def _endRenderPrepend(self):
        page = self.page()
        page.runJavaScript(f'''node = document.querySelector({self._canv_rendtagid});
        node.innerHTML = self._canv_cache + node.innerHTML
        ''')

        self._canv_cache = None
        self._scrollToVa(self._canv_ppjump)

    def _beginRenderAppend(self):
        self._canv_cache = ''

    def _endRenderAppend(self):
        page = self.page()
        js = f'document.querySelector("{self._canv_rendtagid}").innerHTML += "{self._canv_cache}";'
        page.runJavaScript(js)
        self._canv_cache = None

    def getNameTag(self, name, typename='name'):
        '''
        Return a "tag" for this memory canvas.  In the case of the
        qt tags, they are a tuple of html text (<opentag>, <closetag>)
        '''
        clsname = 'envi-%s' % typename
        namehex = binascii.hexlify(name.lower())
        subclsname = 'envi-%s-%s' % (typename, namehex)
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
        page = self.page()
        js = f'document.querySelector("{self._canv_rendtagid}").innerHTML += "{text}";'
        page.runJavaScript(js)

    def _add_raw(self, text):
        # If we are in a call to renderMemory, cache til the end.
        if self._canv_cache is not None:
            self._canv_cache += text
            return

        self._appendInside(text)

    def addText(self, text, tag=None):
        text = html.escape(text)
        text = text.replace('\n', '<br>')

        if tag is not None:
            otag, ctag = tag
            text = otag + text + ctag
        self._add_raw(text)

    @idlethreadsync
    def clearCanvas(self):
        page = self.page()
        page.runJavaScript('document.querySelector("{self._canv_rendtagid}").innerHTML = "";')

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

    def dumpHtml(self, data):
        if self.fname:
            with open(self.fname, 'w') as f:
                f.write(data)
            self.fname = Nonee

    def _menuSaveToHtml(self):
        fname = getSaveFileName(self, 'Save As HTML...')
        if fname is not None:
            fname = str(fname)
            if len(fname):
                self.fname = fname
                self.page().toHtml(self.dumpHtml)


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
