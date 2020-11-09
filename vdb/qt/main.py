import cmd
import logging
import collections

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

import envi.cli
import vtrace.qt
import envi.qt.config

import vdb.qt.memory
import vdb.qt.threads
import vdb.qt.memwrite
import vdb.qt.registers

import vqt.cli
import vqt.main
import vqt.colors
import vqt.qpython
import vqt.hotkeys as vq_hotkeys
import vqt.application as vq_app

from vqt.main import *
from vqt.basics import *
from vqt.common import *
from vtrace.const import *


logger = logging.getLogger(__name__)


class VdbCmdWidget(vqt.cli.VQCli, vtrace.qt.VQTraceNotifier):

    def __init__(self, db, parent=None):

        vqt.cli.VQCli.__init__(self, db, parent)
        vtrace.qt.VQTraceNotifier.__init__(self, trace=db.gui._db_t)
        self._db_t = db.gui._db_t

        self.setAcceptDrops(True)
        self.output.dragEnterEvent = self.dragEnterEvent
        self.output.dropEvent = self.canvasDropEvent

        self.resize(250, 150)

        # set the initial state
        trace = self._db_t
        if trace.isAttached():
            self.notify(NOTIFY_ATTACH, None)
        elif not trace.isAttached():
            self.notify(NOTIFY_DETACH, None)
        elif trace.isRunning():
            self.notify(NOTIFY_CONTINUE, None)
        elif trace.hasExited():
            self.notify(NOTIFY_EXIT, None)
        else:
            self.notify(NOTIFY_CONTINUE, None)

    def getCliLayout(self):
        self.status = QLabel(self)
        self.status.setMinimumWidth(75)
        self.status.setMaximumWidth(75)
        self.status.setFrameStyle(1)
        hbox = HBox(self.status, self.input)
        vbox = VBox(self.output)
        vbox.addLayout(hbox)
        return vbox

    @vqt.main.idlethreadsync
    def notify(self, event, args):

        if not self._db_t.runagain:
            self.status.setText('Paused')
            self.status.setStyleSheet('color:red')

        if event == NOTIFY_ATTACH:
            self.status.setText('Attached')
        elif event in (NOTIFY_BREAK, NOTIFY_SIGNAL):
            self.status.setText('Paused')
            self.status.setStyleSheet('color:red')
        elif event == NOTIFY_CONTINUE:
            self.status.setText('Running')
            self.status.setStyleSheet('color:#00ff00')
        elif event == NOTIFY_DETACH:
            self.status.setText('Detached')
            self.status.setStyleSheet('color:yellow')
        elif event == NOTIFY_EXIT:
            self.status.setText('Exited')
            self.status.setStyleSheet('color:red')

    def returnPressedSlot(self):
        '''
        Override VQCli returnPressedSlot so we submit to the vdb transaction
        queue instead of firing a thread.
        '''
        command = str(self.input.text())
        self.input.clear()
        self.input.setText('')
        self.input.addHistory(command)
        self.output.addText('> %s\n' % command)

        workthread(self.onecmd)(command)

    def onecmd(self, line):
        '''
        Override VQCli onecmd so we can handle exceptions other than
        explicit exiting or keyboard interrupts.
        '''
        lines = line.split('&&')
        try:
            for line in lines:
                line = self.cli.aliascmd(line)
                cmd.Cmd.onecmd(self.cli, line)
        except (KeyboardInterrupt, SystemExit):
            raise

        if self.cli.shutdown.isSet():
            self._emit_quit()

    def isValidDrag(self, event):
        urls = event.mimeData().urls()
        if len(urls) != 1:
            return False

        url = urls[0]
        if not url.isValid() or url.scheme() != 'file':
            return False

        return True

    def dragEnterEvent(self, event):
        if not self.isValidDrag(event):
            event.ignore()
            return

        event.accept()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]

        self.input.setText('%s"%s"' % (self.input.text(), url.toLocalFile()))

    def canvasDropEvent(self, event):
        url = event.mimeData().urls()[0]

        self.input.setText('exec "%s"' % url.toLocalFile())

class VdbToolBar(vtrace.qt.VQTraceToolBar):
    '''
    Subclass so we get access to the db object not proxied through VdbTrace.
    '''
    def __init__(self, db, trace, parent=None):
        vtrace.qt.VQTraceToolBar.__init__(self, trace, parent=parent)
        self.db = db

    def actAttach(self, *args, **kwargs):
        pid = vtrace.qt.getProcessPid(trace=self.trace)
        if pid is not None:
            workthread(self.trace.attach)(pid)

    @workthread
    def actDetach(self, thing):
        if self.trace.isAttached():
            self.db.do_detach('')

    @workthread
    def actContinue(self, thing):
        self.db.do_go('')

    @workthread
    def actBreak(self, thing):
        self.db.do_break('')

    @workthread
    def actStepi(self, thing):
        self.db.do_stepi('')

    @workthread
    def actStepover(self, thing):
        self.db.do_stepo('')

class VdbWindow(vq_app.VQMainCmdWindow):

    __cli_widget_class__ = VdbCmdWidget

    def __init__(self, db):
        # Gui constructor needs these set...
        self._db = db
        self._db_t = vdb.VdbTrace(db)

        # stores named window names.
        self.namedWindowsCount = collections.Counter()

        db.gui = self # This must go before VQMainCmdWindow
        vq_app.VQMainCmdWindow.__init__(self, 'Vdb', db)

        tbar = VdbToolBar(db, self._db_t, parent=self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, tbar)

        self.vqAddMenuField('&File.&Open', self.menuFileOpen)
        self.vqAddMenuField('&File.&Quit', self.menuFileQuit)
        self.vqAddMenuField('&Edit.&Preferences', self.menuEditPrefs)
        self.vqAddMenuField('&View.&Memory', self.menuViewMemory)
        self.vqAddMenuField('&View.&Memory Maps', self.menuViewMemMaps)
        self.vqAddMenuField('&View.&Threads', self.menuViewThreads)
        self.vqAddMenuField('&View.&Registers', self.menuViewRegisters)
        self.vqAddMenuField('&View.&Memory Write', self.menuViewMemWrite)
        self.vqAddMenuField('&View.&File Descriptors', self.menuViewFileDesc)
        self.vqAddMenuField('&View.&Layouts.&Load', self.menuViewLayoutsLoad)
        self.vqAddMenuField('&View.&Layouts.&Save', self.menuViewLayoutsSave)
        self.vqAddMenuField('&View.&Layouts.&Clear', self.menuViewLayoutsClear)
        self.vqAddMenuField('&Tools.&Python', self.menuToolsPython)

        # Map some default keys
        self.addHotKey('f5','debug:go')
        self.addHotKey('f6','debug:attach')
        self.addHotKey('f7','debug:stepi')
        self.addHotKey('f8','debug:stepover')
        self.addHotKey('ctrl+b','debug:break')
        self.addHotKey('ctrl+p','vdb:view:python')

        # Get hotkey overrides
        self.loadHotKeys(self._vq_settings)

        db.registerCmdExtension(self.hotkeys)

        vqtconnect( self.buildMemoryWindow, 'vdb:view:memory' )
        vqtconnect( self.buildMemWriteWindow, 'vdb:view:writemem' )

    def vdbUIEvent(self, event, einfo):
        vqtevent(event,einfo)

    def buildMemoryWindow(self, event, einfo):
        expr, esize, rend = einfo
        dock, view = self.vqBuildDockWidget('VdbMemoryWindow', floating=True)
        view.enviNavGoto(expr, esize, rend)

    def buildMemWriteWindow(self, event, einfo):
        expr, esize = einfo
        dock, view = self.vqBuildDockWidget('VdbMemWriteWindow', floating=True)
        view.enviNavGoto(expr, esize)

    def hotkeys(self, db, line):
        '''
        Manipulate gui hotkeys.

        Usage: hotkeys [target=keyname]
        '''
        argv = envi.cli.splitargs(line)
        for arg in argv:

            if arg.find('=') == -1:
                return db.do_help('hotkeys')

            target,keyname = arg.split('=',1)
            if not self.isHotKeyTarget(target):
                db.vprint('Invalid Hotkey Target: %s' % target)
                return

            db.vprint('Setting: %s = %s' % (target,keyname))

            self.addHotKey(keyname,target)
            self._vq_settings.setValue('hotkey:%s' % target,keyname)

        db.vprint('Hotkeys:')
        lookup = dict([ (targname, keystr) for (keystr,targname) in self.getHotKeys() ])
        targets = self.getHotKeyTargets()
        targets.sort()

        for targname in targets:
            db.vprint('%s: %s' % (targname.ljust(20),lookup.get(targname,'')))

    @vq_hotkeys.hotkey('debug:attach')
    def _hotkey_attach(self):
        trace = self._db.getTrace()
        pid = vtrace.qt.getProcessPid(trace=trace, parent=self)
        workthread(trace.attach)(pid)

    @workthread
    @vq_hotkeys.hotkey('debug:detach')
    def _hotkey_detach(self):
        self._db.do_detach('')

    @workthread
    @vq_hotkeys.hotkey('debug:go')
    def _hotkey_go(self):
        self._db.do_go('')

    @boredthread
    @vq_hotkeys.hotkey('debug:stepi')
    def _hotkey_stepi(self):
        self._db.do_stepi('')

    @boredthread
    @vq_hotkeys.hotkey('debug:stepover')
    def _hotkey_stepover(self):
        self._db.do_stepo('')

    @boredthread
    @vq_hotkeys.hotkey('debug:break')
    def _hotkey_break(self):
        self._db.do_break('')

    def vqInitDockWidgetClasses(self):
        self.vqAddDockWidgetClass(vdb.qt.memory.VdbMemoryWindow, args=(self._db, self._db_t))
        self.vqAddDockWidgetClass(vtrace.qt.VQMemoryMapView, args=(self._db_t, self))
        self.vqAddDockWidgetClass(vtrace.qt.VQFileDescView, args=(self._db_t, self))
        self.vqAddDockWidgetClass(vdb.qt.threads.VdbThreadsWindow, args=(self._db, self._db_t,))
        self.vqAddDockWidgetClass(vqt.qpython.VQPythonView, args=(self._db.getExpressionLocals(),))

        self.vqAddDockWidgetClass(vdb.qt.registers.VdbRegistersWindow, args=(self._db, self._db_t))
        self.vqAddDockWidgetClass(vdb.qt.memwrite.VdbMemWriteWindow, args=(self._db, self._db_t,))

    def menuEditPrefs(self):

        trace = self._db.getTrace()

        config = self._db.config.vdb
        configs = []
        configs.append(('vdb', config))

        arch = trace.getMeta('Architecture').lower()
        platform = trace.getMeta('Platform').lower()

        pconfig = config.getSubConfig( platform, add=False )
        if pconfig is not None:
            configs.append(('vdb:%s' % platform, pconfig))

        aconfig = config.getSubConfig( arch, add=False )
        if aconfig is not None:
            configs.append(('vdb:%s' % arch, aconfig))

        self._cfg_widget = envi.qt.config.EnviConfigTabs( configs )
        self._cfg_widget.show()

    @vq_hotkeys.hotkey('vdb:view:python')
    def menuToolsPython(self):
        self.vqBuildDockWidget('VQPythonView')

    @vq_hotkeys.hotkey('vdb:view:filedesc')
    def menuViewFileDesc(self):
        self.vqBuildDockWidget('VQFileDescView')

    @vq_hotkeys.hotkey('vdb:view:memmaps')
    def menuViewMemMaps(self):
        self.vqBuildDockWidget('VQMemoryMapView')

    @vq_hotkeys.hotkey('vdb:view:memory')
    def menuViewMemory(self):
        self.vqBuildDockWidget('VdbMemoryWindow', floating=True)

    @vq_hotkeys.hotkey('vdb:view:memwrite')
    def menuViewMemWrite(self):
        self.vqBuildDockWidget('VdbMemWriteWindow', floating=True)

    @vq_hotkeys.hotkey('vdb:view:threads')
    def menuViewThreads(self):
        self.vqBuildDockWidget('VdbThreadsWindow', area=QtCore.Qt.RightDockWidgetArea)

    @vq_hotkeys.hotkey('vdb:view:registers')
    def menuViewRegisters(self):
        self.vqBuildDockWidget('VdbRegistersWindow', area=QtCore.Qt.RightDockWidgetArea)

    def menuViewLayoutsLoad(self):
        fname = getOpenFileName(self, 'Load Layout')
        if fname is None:
            return

        self.vqClearDockWidgets()

        settings = QtCore.QSettings(str(fname), QtCore.QSettings.IniFormat)
        self.vqRestoreGuiSettings(settings)

    def menuViewLayoutsSave(self):
        fname = getSaveFileName(self, 'Save Layout')
        if fname is None:
            return

        settings = QtCore.QSettings(str(fname), QtCore.QSettings.IniFormat)
        self.vqSaveGuiSettings(settings)

    def menuViewLayoutsClear(self):
        self.vqClearDockWidgets()

    def menuFileOpen(self, *args, **kwargs):
        fname = str(getOpenFileName(parent=self, caption='File to execute and attach to'))
        if fname != '':
            self._vq_cli.onecmd('exec "%s"' % fname)

    def menuFileQuit(self, *args, **kwargs):
        self.close()

    def closeEvent(self, event):
        try:
            t = self._db.trace

            if t.isAttached():
                if self._db.config.vdb.KillOnQuit:
                    t.kill()

                elif t.isRunning():
                    t.sendBreak()
                    t.detach()

                else:
                    t.detach()

        except Exception as e:
            logger.warning('Error Detaching: %s', e)

        return vq_app.VQMainCmdWindow.closeEvent(self, event)
