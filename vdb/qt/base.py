from PyQt5.QtWidgets import QWidget

import vqt.saveable as vq_save

import vtrace.qt

class VdbWidgetWindow(QWidget, vq_save.SaveableWidget, vtrace.qt.VQTraceNotifier):
    '''
    a base window class for widgets to inherit from for vdb.
    this gives your window/widget access to the vdb instance (self.db), the gui
    instance (self.db.gui), and the persistent trace object (self.dbt).

    implement vqLoad for tracer events.
    implement vdbUIEvent for events caused by user interaction.
    state between runs of the debugger.
    '''
    def __init__(self, db, dbt, parent=None):
        QWidget.__init__(self, parent=parent)
        vq_save.SaveableWidget.__init__(self)
        vtrace.qt.VQTraceNotifier.__init__(self, trace=dbt)

        self.db = db
        self.dbt = dbt

    def keyPressEvent(self, event):
        '''
        handle the global hotkeys.
        '''
        self.db.gui.keyPressEvent(event)
