import os
import sys

import vstruct.qt as vs_qt
import envi.expression as e_expr
import envi.qt.config as e_q_config

import vqt.cli as vq_cli
import vqt.main as vq_main
import vqt.colors as vq_colors
import vqt.qpython as vq_python
import vqt.application as vq_app

import vivisect.cli as viv_cli
import vivisect.base as viv_base
import vivisect.vdbext as viv_vdbext
import vivisect.qt.tips as viv_q_tips
import vivisect.qt.views as viv_q_views
import vivisect.qt.memory as viv_q_memory
import vivisect.qt.remote as viv_q_remote
import vivisect.qt.ustruct as viv_q_ustruct
import vivisect.extensions as viv_extensions
import vivisect.qt.funcgraph as viv_q_funcgraph
import vivisect.qt.funcviews as viv_q_funcviews
import vivisect.qt.symboliks as viv_q_symboliks
import vivisect.remote.share as viv_share

from PyQt5 import QtCore
from PyQt5.QtWidgets import QInputDialog

from vqt.common import *
from vivisect.const import *
from vqt.main import getOpenFileName, getSaveFileName
from vqt.saveable import compat_isNone

dock_top = QtCore.Qt.TopDockWidgetArea
dock_right = QtCore.Qt.RightDockWidgetArea


class VQVivMainWindow(viv_base.VivEventDist, vq_app.VQMainCmdWindow):

    # Child windows may emit this on "navigate" requests...
    # vivNavSignal = QtCore.pyqtSignal(str, name='vivNavSignal')
    vivMemColorSignal = QtCore.pyqtSignal(dict, name='vivMemColorSignal')

    def __init__(self, vw):
        self.vw = vw
        vw._viv_gui = self
        # DEV: hijack the workspace's vprint so that they get routed to the UI canvas
        # and not out to the stdout
        vw.vprint = self.vprint
        viv_base.VivEventDist.__init__(self, vw=vw)
        vq_app.VQMainCmdWindow.__init__(self, 'Vivisect', vw)

        self.vqAddMenuField('&File.Open', self._menuFileOpen)
        self.vqAddMenuField('&File.Save', self._menuFileSave)
        self.vqAddMenuField('&File.Save As', self._menuFileSaveAs)
        self.vqAddMenuField('&File.Save to Server', self._menuFileSaveServer)

        self.vqAddMenuField('&File.Quit', self.close)
        self.vqAddMenuField('&Edit.&Preferences', self._menuEditPrefs)

        self.vqAddMenuField('&View.&Exports', self._menuViewExports)
        self.vqAddMenuField('&View.&Functions', self._menuViewFunctions)
        self.vqAddMenuField('&View.&Imports', self._menuViewImports)
        self.vqAddMenuField('&View.&Names', self._menuViewNames)
        self.vqAddMenuField('&View.&Memory', self._menuViewMemory)
        self.vqAddMenuField('&View.&Function Graph', self._menuViewFuncGraph)
        self.vqAddMenuField('&View.&Strings', self._menuViewStrings)
        self.vqAddMenuField('&View.&Structures', self._menuViewStructs)
        self.vqAddMenuField('&View.&Segments', self._menuViewSegments)
        self.vqAddMenuField('&View.&Symboliks', self._menuViewSymboliks)
        self.vqAddMenuField('&View.&Layouts.&Set Default', self._menuViewLayoutsSetDefault)
        self.vqAddMenuField('&View.&Layouts.&Save', self._menuViewLayoutsSave)
        self.vqAddMenuField('&View.&Layouts.&Load', self._menuViewLayoutsLoad)

        self.vqAddMenuField('&Share.Share Workspace', self._menuShareWorkspace)
        self.vqAddMenuField('&Share.Connect to Shared Workspace', self._menuShareConnect)
        self.vqAddMenuField('&Share.Connect To Workspace Server', self._menuShareConnectServer)

        self.vqAddMenuField('&Tools.&Python', self._menuToolsPython)
        self.vqAddMenuField('&Tools.&Debug', self._menuToolsDebug)
        self.vqAddMenuField('&Tools.&Structures.Add Namespace', self._menuToolsStructNames)
        self.vqAddMenuField('&Tools.&Structures.New', self._menuToolsUStructNew)
        self.vqAddDynMenu('&Tools.&Structures.&Edit', self._menuToolsUStructEdit)

        self.vqAddDynMenu('&Tools.&Va Sets', self._menuToolsVaSets)

        self.vqAddMenuField('&Window.&Fullscreen', self._menuWindowFullscreen)
        self.vqAddMenuField('&Window.&Maximized', self._menuWindowMaximize)
        self.vqAddMenuField('&Window.&Normal', self._menuWindowNormal)

        self.vw.vprint('Welcome to Vivisect (Qt Edition)!')
        self.vw.vprint('Random Tip: %s' % viv_q_tips.getRandomTip())

        if len(self.vqGetDockWidgets()) == 0:
            self.vw.vprint('\n')
            #self.vw.vprint('&#10;')
            self.vw.vprint('Looks like you have an empty layout!')
            self.vw.vprint('Use View->Layouts->Load and select vivisect/qt/default.lyt')

        fname = os.path.basename(self.vw.getMeta('StorageName', 'Unknown'))
        self.setWindowTitle('Vivisect: %s' % fname)
        self.windowState = QtCore.Qt.WindowNoState

        self.addHotKey('ctrl+o', 'file:open')
        self.addHotKeyTarget('file:open', self._menuFileOpen)
        self.addHotKey('ctrl+s', 'file:save')
        self.addHotKeyTarget('file:save', self._menuFileSave)
        self.addHotKey('ctrl+w', 'file:quit')
        self.addHotKeyTarget('file:quit', self.close)

    def vprint(self, msg, addnl=True):
        # ripped and modded from envi/cli.py
        self.vw.canvas.write(msg)
        if addnl:
            self.vw.canvas.write('\n')

    def getLocation(self, va):
        loctup = self.vw.getLocation(va)

        if loctup is None:
            self.vw.vprint('Location not found!')
        else:
            name = loc_type_names.get(loctup[L_LTYPE], 'Unspecified')
            self.vw.vprint('\nVA: %s' % hex(loctup[L_VA]))
            self.vw.vprint('    Size: %d' % loctup[L_SIZE])
            self.vw.vprint('    Type: %s' % name)
            self.vw.vprint('    Info: %s' % str(loctup[L_TINFO]))
            self.vw.vprint('    Repr: %s' % self.vw.reprLocation(loctup)[:64])

    def setVaName(self, va, parent=None):
        if parent is None:
            parent = self

        curname = self.vw.getName(va)
        if curname is None:
            curname = ''

        name, ok = QInputDialog.getText(parent, 'Enter...', 'Name', text=curname)
        if ok:
            name = str(name)
            if self.vw.vaByName(name):
                raise Exception('Duplicate Name: %s' % name)

            self.vw.makeName(va, name)

    def setVaComment(self, va, parent=None):
        if parent is None:
            parent = self

        curcomment = self.vw.getComment(va)
        if curcomment is None:
            curcomment = ''

        comment, ok = QInputDialog.getText(parent, 'Enter...', 'Comment', text=curcomment)
        if ok:
            self.vw.setComment(va, str(comment))

    def addVaXref(self, va, parent=None):
        if parent is None:
            parent = self
        xtova, ok = QInputDialog.getText(parent, 'Enter...', 'Make Code Xref 0x%x -> ' % va)
        if ok:
            try:
                val = self.vw.parseExpression(str(xtova))
                if self.vw.isValidPointer(val):
                    self.vw.addXref(va, val, REF_CODE)
                else:
                    self.vw.vprint("Invalid Expression: %s   (%s)" % (xtova, val))
            except Exception as e:
                self.vw.vprint(repr(e))

    def setFuncLocalName(self, fva, offset, atype, aname):
        newname, ok = QInputDialog.getText(self, 'Enter...', 'Local Name')
        if ok:
            self.vw.setFunctionLocal(fva, offset, LSYM_NAME, (atype, str(newname)))

    def setFuncArgName(self, fva, idx, atype, aname):
        newname, ok = QInputDialog.getText(self, 'Enter...', 'Argument Name')
        if ok:
            self.vw.setFunctionArg(fva, idx, atype, str(newname))

    def showFuncCallGraph(self, fva):
        callview = viv_q_funcviews.FuncCallsView(self.vw)
        callview.functionSelected(fva)
        callview.show()
        self.vqDockWidget(callview, floating=True)

    def makeStruct(self, va, parent=None):
        if parent is None:
            parent = self
        sname = vs_qt.selectStructure(self.vw.vsbuilder, parent=parent)
        if sname is not None:
            self.vw.makeStructure(va, sname)
        return sname

    def addBookmark(self, va, parent=None):
        if parent is None:
            parent = self
        bname, ok = QInputDialog.getText(parent, 'Enter...', 'Bookmark Name')
        if ok:
            self.vw.setVaSetRow('Bookmarks', (va, str(bname)))

    def getMemoryWidgets(self):
        return self.views.get('VQVivMemoryView', [])

    def getMemWidgetsByName(self, name='viv', firstonly=True):
        '''
        Returns a list of Memory View Widgets with the given name.
        If "firstonly" is True, only return the first one or None(not a list)

        Returns a tuple of (Widget, DockWidget).  The "Widget" is obtained from
        the DockWidget, but they both have different powers.
        '''
        logger.debug("getWindowsByName(%r, firstonly=%r)", name, firstonly)
        out = []

        for vqDW in self.getMemoryWidgets():
            w = vqDW.widget()
            if w.getEnviNavName() == name:
                if firstonly:
                    return w, vqDW

                out.append((w,vqDW))

        if firstonly:   # if firstonly and we don't have one, return None
            return None

        return out

    def getFuncGraphs(self):
        return self.views.get('VQVivFuncgraphView', [])

    def getFuncGraphsByName(self, name='FuncGraph0', firstonly=True):
        '''
        Returns a list of Dock Widgets which have a "getEnviNavName"
        This includes MemoryViews and FuncGraphs
        '''
        logger.debug("getFuncGraphsByName()")

        out = []
        for vqDW in self.getFuncGraphs():
            w = vqDW.widget()
            if name != w.getEnviNavName():
                continue

            if firstonly:
                return w, vqDW

            out.append((w, vqDW))

        if firstonly:   # if firstonly and we don't have one, return None
            return None

        return out

    def sendMemWidgetTo(self, va, wname='viv', firstonly=False):
        '''
        Tells the named Envi Nav Widget to navigate to the given VA
        '''
        logger.debug("sendMemWidgetsTo(0x%x, wname=%r)", va, wname)
        for win in self.getMemWidgetsByName(wname, firstonly=False):
            w, vqFW = win

            logger.debug("sending %r to %r", w, hex(va))
            w.enviNavGoto(hex(va))
            if firstonly:
                break
        return True

    def sendFuncGraphTo(self, va, wname='FuncGraph0', firstonly=False):
        '''
        Tells the named Envi Nav Widget to navigate to the given VA
        '''
        logger.debug("sendFuncGraphTo(0x%x, wname=%r)", va, wname)
        for win in self.getFuncGraphsByName(wname, firstonly=False):
            w, vqFW = win

            logger.debug("sending %r to %r", w, hex(va))
            w.enviNavGoto(hex(va))
            if firstonly:
                break
        return True

    def getCliBar(self):
        '''
        Returns the CLI Bar object
        '''
        for c in self.children():
            if isinstance(c, vq_cli.VQCli):
                return c

    def getCliText(self):
        '''
        Get the text from the GUI's CLI Bar (at the bottom)
        '''
        cli = self.getCliBar()
        return cli.input.text()

    def setCliText(self, text):
        '''
        Set the text in the GUI's CLI Bar (at the bottom)
        '''
        logger.debug("setCliText(%r)" % text)
        cli = self.getCliBar()
        cli.input.setText(text)

    def _menuEditPrefs(self):
        configs = []
        configs.append(('Vivisect', self.vw.config.viv))
        configs.append(('Vdb', self.vw.config.vdb))
        self._cfg_widget = e_q_config.EnviConfigTabs(configs)
        self._cfg_widget.show()

    def _menuToolsUStructNew(self):
        u = viv_q_ustruct.UserStructEditor(self.vw)
        w = self.vqDockWidget(u, floating=True)
        w.resize(600, 600)

    def _menuToolsUStructEdit(self, name=None):
        if name is None:
            return self.vw.getUserStructNames()
        u = viv_q_ustruct.UserStructEditor(self.vw, name=name)
        w = self.vqDockWidget(u, floating=True)
        w.resize(600, 600)

    def _menuToolsVaSets(self, name=None):
        if name is None:
            return self.vw.getVaSetNames()
        view = viv_q_views.VQVivVaSetView(self.vw, self, name)
        self.vqDockWidget(view)

    def delFunction(self, fva, parent=None):
        if parent is None:
            parent = self

        yn, ok = QInputDialog.getItem(self, 'Delete Function', 'Confirm:', ('No', 'Yes'), 0, False)
        if ok and yn == 'Yes':
            self.vw.delFunction(fva)

    def vqInitDockWidgetClasses(self):

        exprloc = e_expr.MemoryExpressionLocals(self.vw, symobj=self.vw)
        exprloc['vw'] = self.vw
        exprloc['vwqgui'] = self
        exprloc['vprint'] = self.vw.vprint

        self.vqAddDockWidgetClass(viv_q_views.VQVivExportsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivFunctionsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivNamesView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivImportsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivSegmentsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivStringsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_views.VQVivStructsView, args=(self.vw, self))
        self.vqAddDockWidgetClass(vq_python.VQPythonView, args=(exprloc, self))
        self.vqAddDockWidgetClass(viv_q_memory.VQVivMemoryView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_funcgraph.VQVivFuncgraphView, args=(self.vw, self))
        self.vqAddDockWidgetClass(viv_q_symboliks.VivSymbolikFuncPane, args=(self.vw, self))

    def vqRestoreGuiSettings(self, settings):
        guid = self.vw.getVivGuid()
        dwcls = settings.value('%s/DockClasses' % guid)
        state = settings.value('%s/DockState' % guid)
        geom = settings.value('%s/DockGeometry' % guid)
        stub = '%s/' % guid

        if compat_isNone(dwcls):
            names = list(self.vw.filemeta.keys())
            names.sort()
            name = '+'.join(names)
            dwcls = settings.value('%s/DockClasses' % name)
            state = settings.value('%s/DockState' % name)
            geom = settings.value('%s/DockGeometry' % name)
            stub = '%s/' % name

        if compat_isNone(dwcls):
            dwcls = settings.value('DockClasses')
            state = settings.value('DockState')
            geom = settings.value('DockGeometry')
            stub = ''

        if not compat_isNone(dwcls):
            for i, clsname in enumerate(dwcls):
                name = 'VQDockWidget%d' % i
                try:
                    tup = self.vqBuildDockWidget(str(clsname), floating=False)
                    if tup is not None:
                        d, obj = tup
                        d.setObjectName(name)
                        d.vqRestoreState(settings, name, stub)
                        d.show()
                except Exception as e:
                    self.vw.vprint('Error Building: %s: %s' % (clsname, e))

        # Once dock widgets are loaded, we can restoreState
        if not compat_isNone(state):
            self.restoreState(state)

        if not compat_isNone(geom):
            self.restoreGeometry(geom)

        # Just get all the resize activities done...
        vq_main.eatevents()
        for w in self.vqGetDockWidgets():
            w.show()

        return True

    def vqSaveGuiSettings(self, settings):

        dock_classes = []
        guid = self.vw.getVivGuid()
        names = list(self.vw.filemeta.keys())
        names.sort()
        vivname = '+'.join(names)

        # Enumerate the current dock windows and set
        # their names by their list order...
        for i, w in enumerate(self.vqGetDockWidgets()):
            widget = w.widget()
            dock_classes.append(widget.__class__.__name__)
            name = 'VQDockWidget%d' % i
            w.setObjectName(name)
            w.vqSaveState(settings, '%s/%s' % (guid, name))
            w.vqSaveState(settings, '%s/%s' % (vivname, name))

        geom = self.saveGeometry()
        state = self.saveState()

        # first store for this specific workspace
        settings.setValue('%s/DockClasses' % guid, dock_classes)
        settings.setValue('%s/DockGeometry' % guid, geom)
        settings.setValue('%s/DockState' % guid, state)

        # next store for this filename
        settings.setValue('%s/DockClasses' % vivname, dock_classes)
        settings.setValue('%s/DockGeometry' % vivname, geom)
        settings.setValue('%s/DockState' % vivname, state)
        # don't store the default.  that should be saved manually

    def vqGetDockWidgetsByName(self, name='viv', firstonly=False):
        '''
        Get list of DockWidgets matching a given name (default is 'viv').

        Returns a list of tuples (window, DockWidget)
        If firstonly==True, returns the first tuple, not a list.
        '''
        out = []
        for vqDW in self.vqGetDockWidgets():
            w = vqDW.widget()
            if hasattr(w, 'getEnviNavName') and w.getEnviNavName() == name:
                if firstonly:
                    return w, vqDW
                out.append((w,vqDW))
        return out

    def _menuToolsDebug(self):
        viv_vdbext.runVdb(self)

    def _menuFileOpen(self):
        # TODO: Add something to change the workspace storage name,
        # and also to list the currently loaded files
        # Right now it'll successively create storage files
        fname = getOpenFileName(self, 'Open...')
        if fname is None or not len(fname):
            return
        self.vw.vprint('Opening %s' % fname)
        self.setWindowTitle('Vivisect: %s' % fname)
        self.vw.loadFromFile(str(fname))
        self.vw.vprint('Analyzing %s' % fname)
        self.vw.analyze()
        self.vw.vprint('%s is ready!' % fname)

    @vq_main.workthread
    def _menuFileSave(self, fullsave=False):
        self.vw.vprint('Saving workspace...')
        try:
            self.vw.saveWorkspace(fullsave=fullsave)
        except Exception as e:
            self.vw.vprint(str(e))
        else:
            self.vw.vprint('complete!')

    def _menuFileSaveAs(self):
        fname = getSaveFileName(self, 'Save As...')
        if fname is None or not len(fname):
            return
        self.vw.setMeta('StorageName', fname)
        self._menuFileSave(fullsave=True)

    def _menuFileSaveServer(self):
        viv_q_remote.saveToServer(self.vw, parent=self)

    def _menuViewLayoutsLoad(self):
        fname = getOpenFileName(self, 'Load Layout')
        if fname is None:
            return

        settings = QtCore.QSettings(fname, QtCore.QSettings.IniFormat)
        self.vqRestoreGuiSettings(settings)

    def _menuViewLayoutsSave(self):
        fname = getSaveFileName(self, 'Save Layout')
        if fname is None or not len(fname):
            return

        settings = QtCore.QSettings(fname, QtCore.QSettings.IniFormat)
        self.vqSaveGuiSettings(settings)

    def _menuViewLayoutsSetDefault(self):
        vq_app.VQMainCmdWindow.vqSaveGuiSettings(self, self._vq_settings)

    def _menuToolsStructNames(self):
        nsinfo = vs_qt.selectStructNamespace()
        if nsinfo is not None:
            nsname, modname = nsinfo
            self.vw.vprint('Adding struct namespace: %s' % nsname)
            self.vw.addStructureModule(nsname, modname)

    def _menuShareWorkspace(self):
        self.vw.vprint('Sharing workspace...')
        daemon = viv_share.shareWorkspace(self.vw)
        self.vw.vprint('Workspace Listening Port: %d' % daemon.port)
        self.vw.vprint('Clients may now connect to your host on port %d' % daemon.port)

    def _menuShareConnect(self):
        viv_q_remote.openSharedWorkspace(self.vw, parent=self)

    def _menuShareConnectServer(self):
        viv_q_remote.openServerAndWorkspace(self.vw, parent=self)

    def _menuToolsPython(self):
        self.vqBuildDockWidget('VQPythonView', area=QtCore.Qt.RightDockWidgetArea)

    def _menuViewStrings(self):
        self.newStringsView()
    def _menuViewStructs(self):
        self.newStructsView()
    def _menuViewSegments(self):
        self.newSegmentsView()
    def _menuViewImports(self):
        self.newImportsView()
    def _menuViewExports(self):
        self.newExportsView()
    def _menuViewFunctions(self):
        self.newFunctionsView()
    def _menuViewNames(self):
        self.newNamesView()
    def _menuViewMemory(self):
        self.newMemoryView()
    def _menuViewFuncGraph(self):
        self.newFuncGraphView()
    def _menuViewSymboliks(self):
        self.newSymbolikFuncView()

    @idlethread
    def newPythonView(self, floating=False):
        self.vqBuildDockWidget('VQPythonView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newStringsView(self, floating=False):
        self.vqBuildDockWidget('VQVivStringsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newStructsView(self, floating=False):
        self.vqBuildDockWidget('VQVivStructsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newSegmentsView(self, floating=False):
        self.vqBuildDockWidget('VQVivSegmentsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newImportsView(self, floating=False):
        self.vqBuildDockWidget('VQVivImportsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newExportsView(self, floating=False):
        self.vqBuildDockWidget('VQVivExportsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newFunctionsView(self, floating=False):
        self.vqBuildDockWidget('VQVivFunctionsView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newNamesView(self, floating=False):
        self.vqBuildDockWidget('VQVivNamesView', floating=floating, area=QtCore.Qt.RightDockWidgetArea)

    @idlethread
    def newMemoryView(self, name='viv', floating=False):
        dock, widget = self.vqBuildDockWidget('VQVivMemoryView', floating=floating, area=QtCore.Qt.TopDockWidgetArea)
        widget.setMemWindowName(name)

    @idlethread
    def newFuncGraphView(self, name=None, floating=False):
        dock, widget = self.vqBuildDockWidget('VQVivFuncgraphView', floating=floating, area=QtCore.Qt.TopDockWidgetArea)
        if name is not None:
            widget.setMemWindowName(name)

    @idlethread
    def newSymbolikFuncView(self, floating=False):
        self.vqBuildDockWidget('VivSymbolikFuncPane', floating=floating, area=QtCore.Qt.TopDockWidgetArea)


    def _menuWindowFullscreen(self):
        if not self.windowState & QtCore.Qt.WindowFullScreen:
            self.windowState = QtCore.Qt.WindowFullScreen
            self.showFullScreen()
        else:
            self._menuWindowNormal()

    def _menuWindowMaximize(self):
        if not self.windowState & QtCore.Qt.WindowMaximized:
            self.windowState = QtCore.Qt.WindowMaximized
            self.showMaximized()

    def _menuWindowNormal(self):
        if not self.windowState & QtCore.Qt.WindowNoState:
            self.windowState = QtCore.Qt.WindowNoState
            self.showNormal()

    @vq_main.idlethread
    def _ve_fireEvent(self, event, edata):
        return viv_base.VivEventDist._ve_fireEvent(self, event, edata)

@vq_main.idlethread
def runqt(vw, closeme=None):
    '''
    Use this API to instantiate a QT main window and show it when
    there is already a main thread running...
    '''
    mw = VQVivMainWindow(vw)
    viv_extensions.loadExtensions(vw, mw)
    mw.show()

    if closeme:
        closeme.close()

    return mw

def main(vw):
    vq_main.startup(css=vq_colors.qt_matrix)
    mw = VQVivMainWindow(vw)
    viv_extensions.loadExtensions(vw, mw)
    mw.show()
    vq_main.main()


if __name__ == '__main__':
    vw = viv_cli.VivCli()
    if len(sys.argv) == 2:
        vw.loadWorkspace(sys.argv[1])
    main(vw)
