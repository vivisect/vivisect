import html

from PyQt5 import QtCore, QtGui, QtWebEngine, QtWebEngineWidgets
from PyQt5.QtCore import QObject, qInstallMessageHandler
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

import envi.exc as e_exc
import envi.common as e_common
import envi.memcanvas as e_memcanvas

import envi.qt.html as e_q_html
import envi.qt.jquery as e_q_jquery

qt_horizontal = 1
qt_vertical = 2

from vqt.main import *
from vqt.common import *


class LoggerPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, line, source):
        print('------------------------------------------------------------------')
        print(f'JSconsole message = {msg}; line: {line};')
        print('------------------------------------------------------------------')


class VQMemoryCanvas(e_memcanvas.MemoryCanvas, QWebEngineView):

    #syncSignal = QtCore.pyqtSignal()
    def __init__(self, mem, syms=None, parent=None, **kwargs):
        e_memcanvas.MemoryCanvas.__init__(self, mem=mem, syms=syms)
        QWebEngineView.__init__(self, parent=parent, **kwargs)

        self._canv_cache = None
        self._canv_curva = None
        self._canv_rendtagid = '#memcanvas'
        self._canv_rend_middle = False
        self.fname = None

        # DEV: DO NOT DELETE THIS REFERENCE TO THESE
        # Otherwise they'll get garbage collected and things like double click
        # to navigate and logging won't work
        # (but pyqt5 won't throw an exception, because ugh).
        self._log_page = LoggerPage()
        self.setPage(self._log_page)
        # https://stackoverflow.com/questions/58906917/warnings-when-instantiating-qwebchannel-object-in-javascript
        # silence all the "property <foo>  of object <bar> has no notify signal messages
        qInstallMessageHandler(lambda *args: None)
        self.channel = QWebChannel()
        self.page().setWebChannel(self.channel)
        self.channel.registerObject('vnav', self)

        htmlpage = e_q_html.template.replace('{{{jquery}}}', e_q_jquery.jquery_2_1_0)
        page = self.page()
        page.setHtml(htmlpage)
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

            def callScroll(data):
                self._selectVa(origva)
            ret = e_memcanvas.MemoryCanvas.renderMemory(self, va, size, rend=rend, cb=callScroll)
        else:
            ret = e_memcanvas.MemoryCanvas.renderMemory(self, va, size, rend=rend)

        return ret

    def _frameContentsSizeChanged(self, size):
        if self._canv_scrolled:
            page = self.page()
            page.runJavaScript('window.scrollTo(1, 0x0fffffff);')

    @idlethread
    def _scrollToVa(self, va, cb=None):
        page = self.page()
        selector = 'viv:0x%.8x' % va
        js = f'''
        var nodes = document.getElementsByName("{selector}");
        if (nodes != null && nodes.length > 0) {{
            nodes[0].scrollIntoView()
        }}
        '''
        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

    @idlethread
    def _selectVa(self, va, cb=None):
        page = self.page()
        js = '''
        selectva("0x%.8x");
        scrolltoid("a_%.8x");
        ''' % (va, va)
        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

    def _beginRenderMemory(self, va, size, rend):
        self._canv_cache = ''

    def _endRenderMemory(self, va, size, rend, cb=None):
        self._appendInside(self._canv_cache, cb)
        self._canv_cache = None

    def _beginRenderVa(self, va, cb=None):
        self._add_raw('<a name="viv:0x%.8x" id="a_%.8x">' % (va, va), cb)

    def _endRenderVa(self, va, cb=None):
        self._add_raw('</a>', cb)

    def _beginUpdateVas(self, valist, cb=None):
        self._canv_cache = ''

        page = self.page()

        selector = 'a#a_%.8x' % valist[0][0]
        js = f'''
        node = document.querySelector("{selector}");
        node.outerHTML = '<update id="updatetmp"></update>' + node.outerHTML;
        '''

        for va, size in valist:
            selector = 'a#a_%.8x' % va
            js += f'''
            var node = document.querySelector("{selector}");
            if (node != null) {{
                node.remove();
            }}
            '''

        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

    def _endUpdateVas(self, cb=None):
        self._canv_cache = self._canv_cache.replace('`', r'\`')
        js = f'''
        var node = document.querySelector('update#updatetmp');
        node.outerHTML = `{self._canv_cache}` + node.outerHTML;
        '''
        if cb:
            self.page().runJavaScript(js, cb)
        else:
            self.page().runJavaScript(js)

        self._canv_cache = None

    def _beginRenderPrepend(self):
        self._canv_cache = ''
        self._canv_ppjump = self._canv_rendvas[0][0]

    def _endRenderPrepend(self, cb=None):
        selector = 'viv:0x%.8x' % self._canv_ppjump
        self._canv_cache = self._canv_cache.replace('`', r'\`')
        js = f'''
        var node = document.querySelector("{self._canv_rendtagid}");
        node.innerHTML = `{self._canv_cache}` + node.innerHTML

        var snode = document.getElementsByName("{selector}");
        if (snode != null && snode.length > 0) {{
            snode[0].scrollIntoView()
        }}
        '''
        self._canv_cache = None
        if cb:
            self.page().runJavaScript(js, cb)
        else:
            self.page().runJavaScript(js)

    def _beginRenderAppend(self):
        self._canv_cache = ''

    def _endRenderAppend(self, cb=None):
        page = self.page()
        self._canv_cache = self._canv_cache.replace('`', r'\`')
        js = f'''
        document.querySelector("{self._canv_rendtagid}").innerHTML += `{self._canv_cache}`;
        '''
        self._canv_cache = None
        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

    def getNameTag(self, name, typename='name'):
        '''
        Return a "tag" for this memory canvas.  In the case of the
        qt tags, they are a tuple of html text (<opentag>, <closetag>)
        '''
        clsname = 'envi-%s' % typename
        namehex = e_common.hexify(name.lower())
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
    def _appendInside(self, text, cb=None):
        page = self.page()
        text = text.replace('`', r'\`')
        js = f'''
        document.querySelector("{self._canv_rendtagid}").innerHTML += `{text}`;
        '''
        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

    def _add_raw(self, text, cb=None):
        # If we are in a call to renderMemory, cache til the end.
        if self._canv_cache is not None:
            self._canv_cache += text
            return

        self._appendInside(text, cb)

    def addText(self, text, tag=None, cb=None):
        text = html.escape(text)
        #text = text.replace('\n', '<br>')
        if tag is not None:
            otag, ctag = tag
            text = otag + text + ctag
        self._add_raw(text, cb)

    @idlethreadsync
    def clearCanvas(self, cb=None):
        page = self.page()
        js = f'''
        var node = document.querySelector("{self._canv_rendtagid}");
        if (node != null) {{
            node.innerHTML = "";
        }}
        '''
        if cb:
            page.runJavaScript(js, cb)
        else:
            page.runJavaScript(js)

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
            self.fname = None

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
