import os
import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

import vqt.cli as vq_cli
import vqt.main as vq_main
import vqt.saveable as vq_save
import vqt.hotkeys as vq_hotkeys
import vqt.menubuilder as vq_menu
from vqt.saveable import compat_isNone

logger = logging.getLogger(__name__)

class VQDockWidget(vq_hotkeys.HotKeyMixin, QDockWidget):

    def __init__(self, parent):
        QDockWidget.__init__(self, parent)
        vq_hotkeys.HotKeyMixin.__init__(self)
        self.addHotKey('ctrl+enter', 'mem:undockmaximize')
        self.addHotKeyTarget('mem:undockmaximize', self._hotkey_undock_maximize)
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)

    def vqSaveState(self, settings, name, stub=''):
        wid = self.widget()
        if isinstance(wid, vq_save.SaveableWidget):
            return wid.vqSaveState(settings, name, stub)

    def vqRestoreState(self, settings, name, stub=''):
        wid = self.widget()
        if isinstance(wid, vq_save.SaveableWidget):
            return wid.vqRestoreState(settings, name, stub)

    def setWidget(self, widget):
        # If he sets his window title, we want to...
        self.setWindowTitle(widget.windowTitle())
        widget.setWindowTitle = self.setWindowTitle
        QDockWidget.setWidget(self, widget)

    def closeEvent(self, event):

        self.hide()
        parent = self.parent()

        w = self.widget()

        # remove widget from the views dict
        clsname = w.__class__.__name__
        dwidgets = parent.views.get(clsname)
        if self in dwidgets:
            dwidgets.remove(self)

        w.setParent(None)
        w.close()

        # remove widget from main _vq_dockwidgets list
        parent.vqRemoveDockWidget(self)

        event.accept()

    def _hotkey_undock_maximize(self):
        # if docked, undock
        if not self.isFloating():
            self.setFloating(1)
            # if not maximized, maximize
            if not self.isMaximized():
                self.showMaximized()
            else:
                # else dock
                self.showNormal()
                self.setFloating(False)
        else:
            # else dock
            self.showNormal()
            self.setFloating(False)

        self.show()
        self.raise_()

class VQMainCmdWindow(vq_hotkeys.HotKeyMixin, QMainWindow):
    '''
    A base class for application window's to inherit from.
    '''

    __cli_widget_class__ = vq_cli.VQCli

    def __init__(self, appname, cmd, **kwargs):

        super(QMainWindow, self).__init__(**kwargs)
        vq_hotkeys.HotKeyMixin.__init__(self)

        self._vq_appname = appname
        self._vq_dockwidgets = []
        self.views = {}

        self._vq_settings = QtCore.QSettings('invisigoth', application=appname, parent=self)
        self._vq_histfile = os.path.join(os.path.expanduser('~'), '.%s_history' % appname)

        self._dock_classes = {}

        self.vqInitDockWidgetClasses()

        self._vq_mbar = vq_menu.VQMenuBar()
        self.setMenuBar(self._vq_mbar)

        # AnimatedDocks, AllowNestedDocks, AllowTabbedDocks, ForceTabbedDocks, VerticalTabs
        self.setDockOptions(self.AnimatedDocks | self.AllowTabbedDocks)

        self._vq_cli = self.__cli_widget_class__(cmd)
        self._vq_cli.input.loadHistory(self._vq_histfile)
        self._vq_cli.sigCliQuit.connect( self.close )

        self.setCentralWidget(self._vq_cli)
        self.vqRestoreGuiSettings(self._vq_settings)

    def vqAddMenuField(self, fname, callback, args=()):
        self._vq_mbar.addField(fname, callback, args=args)

    def vqAddDynMenu(self, fname, callback):
        self._vq_mbar.addDynMenu(fname, callback)

    def vqInitDockWidgetClasses(self):
        # apps can over-ride
        pass

    def vqAddDockWidgetClass(self, cls, args=()):
        self._dock_classes[cls.__name__] = (cls, args)

    def vqBuildDockWidget(self, clsname, floating=False, area=QtCore.Qt.TopDockWidgetArea):
        res = self._dock_classes.get(clsname)
        if res is None:
            logger.warning('vqBuildDockWidget Failed For: %s (No class constructor found)', clsname)
            return
        cls, args = res
        obj = cls(*args)
        return (self.vqDockWidget(obj, area, floating=floating), obj)

    def vqRestoreGuiSettings(self, settings, stub=''):
        dwcls = settings.value('DockClasses')

        if not compat_isNone(dwcls):
            for i, clsname in enumerate(dwcls):
                name = 'VQDockWidget%d' % i
                try:
                    # we haven't loaded the extensions yet, so all we'll have is the base clases
                    if str(clsname) not in self._dock_classes:
                        continue
                    tup = self.vqBuildDockWidget(str(clsname), floating=False)
                    if tup is not None:
                        d, obj = tup
                        d.setObjectName(name)
                        d.vqRestoreState(settings, name, stub)
                        d.show()
                except Exception as e:
                    logger.error('Error Building: %s: %s', clsname, e)

        # Once dock widgets are loaded, we can restoreState
        state = settings.value('DockState')
        if not compat_isNone(state):
            self.restoreState(state)

        geom = settings.value('DockGeometry')
        if not compat_isNone(geom):
            self.restoreGeometry(geom)

        # Just get all the resize activities done...
        vq_main.eatevents()
        for w in self.vqGetDockWidgets():
            w.show()

        return True

    def vqSaveGuiSettings(self, settings, stub=''):

        dock_classes = []

        # Enumerate the current dock windows and set
        # their names by their list order...
        for i, w in enumerate(self.vqGetDockWidgets()):
            widget = w.widget()
            dock_classes.append(widget.__class__.__name__)
            name = 'VQDockWidget%d' % i
            w.setObjectName(name)
            w.vqSaveState(settings,name,stub)

        settings.setValue('DockClasses', dock_classes)
        settings.setValue('DockGeometry', self.saveGeometry())
        settings.setValue('DockState', self.saveState())

    def closeEvent(self, event):
        self.vqSaveGuiSettings(self._vq_settings)
        self._vq_cli.input.saveHistory(self._vq_histfile)
        QMainWindow.closeEvent(self, event)

    def vqGetDockWidgets(self):
        return list(self._vq_dockwidgets)

    def vqClearDockWidgets(self):
        for wid in self.vqGetDockWidgets():
            wid.close()

    def vqRemoveDockWidget(self, widget):
        self._vq_dockwidgets.remove(widget)
        self.removeDockWidget(widget)

    def vqDockWidget(self, widget, area=QtCore.Qt.TopDockWidgetArea, floating=False):
        d = VQDockWidget(self)
        d.setWidget(widget)
        d.setFloating(floating)
        self.addDockWidget(area, d)
        self._vq_dockwidgets.append(d)

        # store the widget by classname
        clsname = widget.__class__.__name__
        dwidgets = self.views.get(clsname)
        if dwidgets is None:
            dwidgets = []
            self.views[clsname] = dwidgets
        dwidgets.append(d)

        self.restoreDockWidget(d)
        d.show()
        return d
