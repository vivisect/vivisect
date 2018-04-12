try:
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtGui import *

import vqt.main as vq_main
import vqt.tree as vq_tree

import envi.threads as e_threads
import cobra.remoteapp as c_remoteapp
import vivisect.remote.server as viv_server

from vqt.basics import *

class WorkspaceListModel(vq_tree.VQTreeModel):
    columns = ('Name',)

class WorkspaceListView(vq_tree.VQTreeView):
    def __init__(self, workspaces, parent=None):
        vq_tree.VQTreeView.__init__(self, parent=parent)
        model = WorkspaceListModel(parent=self)
        self.setModel(model)
        for wsname in workspaces:
            model.append((wsname,))

class VivServerDialog(QDialog):

    def __init__(self, workspaces, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setWindowTitle('Select a workspace...')

        self.wsname = None
        self.wslist = WorkspaceListView(workspaces, parent=self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        layout = VBox()
        layout.addWidget(self.wslist)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.wslist.doubleClicked.connect( self.workspaceActivated )

    def getWorkspaceName(self):
        self.exec_()
        return self.wsname

    def workspaceActivated(self, idx):
        self.accept()

    def accept(self):
        for idx in self.wslist.selectedIndexes():
            row = idx.internalPointer()
            if row:
                self.wsname = row.rowdata[0]
                break

        return QDialog.accept(self)

class VivSaveServerDialog(QDialog):

    def __init__(self, vw, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setWindowTitle('Save to Workspace Server...')
        self.vw = vw
        try:
            server = vw.config.remote.server
        except AttributeError:
            server = "visi.kenshoto.com"

        self.wsname = QLineEdit(vw.getMeta('StorageName',''), parent=self)
        self.wsserver = QLineEdit(server, parent=self)
        self.setdef = QCheckBox(parent=self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        serverlayout = QHBoxLayout()
        serverlayout.addWidget(self.wsserver)
        serverlayout.addWidget(QLabel('Make Default:'))
        serverlayout.addWidget(self.setdef)

        layout = QFormLayout()
        layout.addRow('Workspace Name', self.wsname)
        layout.addRow('Workspace Server', serverlayout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def getNameAndServer(self):
        if not self.exec_():
            return (None,None)
        wsname = str(self.wsname.text())
        wsserver = str(self.wsserver.text())
        return (wsname,wsserver)

    def accept(self, *args, **kwargs):
        QDialog.accept(self, *args, **kwargs)
        if self.setdef.isChecked():
            cfg = self.vw.config.getSubConfig("remote")
            cfg['server'] = str(self.wsserver.text())
            self.vw.config.saveConfigFile()

# FIXME: should we combine the VivConnectServerDialog with the VivSaveServerDialog?  there are like 10 lines different.
class VivConnectServerDialog(QDialog):

    def __init__(self, vw, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setWindowTitle('Workspace Server...')
        self.vw = vw
        try:
            server = vw.config.remote.server
        except AttributeError:
            server = "visi.kenshoto.com"

        self.wsserver = QLineEdit(server, parent=self)
        self.setdef = QCheckBox(parent=self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        serverlayout = QHBoxLayout()
        serverlayout.addWidget(self.wsserver)
        serverlayout.addWidget(QLabel('Make Default:'))
        serverlayout.addWidget(self.setdef)

        layout = QFormLayout()
        layout.addRow('Workspace Server', serverlayout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def getServer(self):
        if not self.exec_():
            return None
        wsserver = str(self.wsserver.text())
        return wsserver

    def accept(self, *args, **kwargs):
        QDialog.accept(self, *args, **kwargs)
        if self.setdef.isChecked():
            cfg = self.vw.config.getSubConfig("remote")
            cfg['server'] = str(self.wsserver.text())
            self.vw.config.saveConfigFile()


@vq_main.idlethread
def openServerAndWorkspace(vw, parent=None):
    dia = VivConnectServerDialog(vw, parent=parent)
    host = dia.getServer()
    if host == None:
        return

    connServerAndWorkspace(vw, str(host), parent=parent)

@vq_main.workthread
def connServerAndWorkspace(vw, host,parent=None):
    # NOTE: do *not* touch parent (or qt) in here!
    try:
        server = viv_server.connectToServer(host)
        wslist = server.listWorkspaces()
        selectServerWorkspace(vw, server, wslist, parent=parent)
    except Exception, e:
        vw.vprint('Server Error: %s' % e)
        return

@vq_main.idlethread
def selectServerWorkspace(vw, server, workspaces, parent=None):
    dia = VivServerDialog(workspaces, parent=parent)
    workspace = dia.getWorkspaceName()
    if workspace == None:
        return

    loadServerWorkspace(vw, server, workspace)

@vq_main.workthread
def loadServerWorkspace(oldvw, server, workspace):
    oldvw.vprint('Loading Workspace: %s' % workspace)
    vw = viv_server.getServerWorkspace(server, workspace)
    import vivisect.qt.main as viv_q_main
    viv_q_main.runqt(vw, closeme=oldvw.getVivGui())

@vq_main.idlethread
def saveToServer(vw, parent=None):
    dia = VivSaveServerDialog(vw, parent=parent)
    wsname,wsserver = dia.getNameAndServer()
    vw.vprint('Saving to Workspace Server: %s (%s)' % (wsserver,wsname))
    sendServerWorkspace(vw, wsname, wsserver)

@e_threads.firethread
def sendServerWorkspace(vw, wsname, wsserver):
    try:
        events = vw.exportWorkspace()
        server = viv_server.connectToServer(wsserver)
        server.addNewWorkspace(wsname, events)
    except Exception, e:
        vw.vprint('Workspace Server Error: %s' % e)
        return

    vw.setMeta('WorkspaceServer', wsserver)

def openSharedWorkspace(vw, parent=None):
    '''
    Open a workspace shared by a vivisect peer.
    '''
    hostport, ok = QInputDialog.getText(parent, 'Shared Workspace...', 'host:port')
    if not ok:
        return

    uri = 'cobra://%s/vivisect.remote.client?msgpack=1' % hostport
    c_remoteapp.execRemoteApp(uri)

