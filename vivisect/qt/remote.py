from PyQt5.QtWidgets import *

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


class BaseServerDialog(QDialog):

    def __init__(self, workspaces, parent=None):
        QDialog.__init__(self, parent=parent)
        self.setWindowTitle('Select a workspace...')

        self.wsname = None
        self.wslist = WorkspaceListView(workspaces, parent=self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

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


class VivServerDialog(QDialog):
    def __init__(self, vw, parent=None):
        QDialog.__init__(self, parent=parent)
        self.vw = vw
        try:
            server = vw.config.remote.server
        except AttributeError:
            server = "visi.kenshoto.com"

        self.wsserver = QLineEdit(server, parent=self)
        self.setdef = QCheckBox(parent=self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        serverlayout = QHBoxLayout()
        serverlayout.addWidget(self.wsserver)
        serverlayout.addWidget(QLabel('Make Default:'))
        serverlayout.addWidget(self.setdef)

        layout = QFormLayout()
        layout.addRow('Workspace Server', serverlayout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def accept(self, *args, **kwargs):
        QDialog.accept(self, *args, **kwargs)
        if self.setdef.isChecked():
            cfg = self.vw.config.getSubConfig("remote")
            cfg['server'] = str(self.wsserver.text())
            self.vw.config.saveConfigFile()

class VivSaveServerDialog(VivServerDialog):

    def __init__(self, vw, parent=None):
        VivServerDialog.__init__(self, vw, parent=parent)
        self.wsname = QLineEdit(vw.getMeta('StorageName', ''), parent=self)
        self.setWindowTitle('Save to Workspace Server...')

    def getNameAndServer(self):
        if not self.exec_():
            return (None, None)
        wsname = str(self.wsname.text())
        wsserver = str(self.wsserver.text())
        return (wsname, wsserver)


class VivConnectServerDialog(VivServerDialog):
    def __init__(self, vw, parent=None):
        VivServerDialog.__init__(self, vw, parent=parent)
        self.setWindowTitle('Workspace Server...')

    def getServer(self):
        if not self.exec_():
            return None
        wsserver = str(self.wsserver.text())
        return wsserver


def openServerAndWorkspace(vw, parent=None):
    dia = VivConnectServerDialog(vw, parent=parent)
    host = dia.getServer()
    if host is None:
        return
    port = viv_server.viv_port
    if ':' in host:
        host, port = host.split(':')

    connServerAndWorkspace(vw, str(host), int(port), parent=parent)


def connServerAndWorkspace(vw, host, port=viv_server.viv_port, parent=None):
    # NOTE: do *not* touch parent (or qt) in here!
    try:
        server = viv_server.connectToServer(host, port=port)
        wslist = server.listWorkspaces()
        selectServerWorkspace(vw, server, wslist, parent=parent)
    except Exception as e:
        vw.vprint('Server Error: %s' % e)
        return

def selectServerWorkspace(vw, server, workspaces, parent=None):
    dia = BaseServerDialog(workspaces, parent=parent)
    workspace = dia.getWorkspaceName()
    if workspace is None:
        return

    loadServerWorkspace(vw, server, workspace)

@vq_main.workthread
def loadServerWorkspace(oldvw, server, workspace):
    oldvw.vprint('Loading Workspace: %s' % workspace)
    vw = viv_server.getServerWorkspace(server, workspace)
    import vivisect.qt.main as viv_q_main
    viv_q_main.runqt(vw, closeme=oldvw.getVivGui())

def saveToServer(vw, parent=None):
    dia = VivSaveServerDialog(vw, parent=parent)
    wsname, wsserver = dia.getNameAndServer()
    vw.vprint('Saving to Workspace Server: %s (%s)' % (wsserver,wsname))
    sendServerWorkspace(vw, wsname, wsserver)

@e_threads.firethread
def sendServerWorkspace(vw, wsname, wsserver):
    try:
        events = vw.exportWorkspace()
        server = viv_server.connectToServer(wsserver)
        server.addNewWorkspace(wsname, events)
    except Exception as e:
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

