from PyQt5 import QtCore, QtGui, QtWidgets

import vtrace.qt
import vdb.qt.base

class VdbThreadsWindow(vdb.qt.base.VdbWidgetWindow):
    def __init__(self, db, dbt, parent=None):
        vdb.qt.base.VdbWidgetWindow.__init__(self, db, dbt, parent=parent)

        self.threadWidget = vtrace.qt.VQThreadsView(trace=dbt, parent=parent)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.threadWidget)
        self.setLayout(vbox)

        self.setWindowTitle('Threads')

    def vqLoad(self):
        '''
        the widgets in VQThreadsView already register for notifications.
        '''
        self.threadWidget.vqLoad()
