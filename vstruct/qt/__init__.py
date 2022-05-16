'''
Some utils for QT code which uses vstruct...
'''
import vqt.tree as vq_tree

from PyQt5.QtWidgets import *

from vqt.main import idlethreadsync

class VQStructNamespacesView(vq_tree.VQTreeView):

    def __init__(self, parent=None):
        vq_tree.VQTreeView.__init__(self, parent=parent)
        #model = vq_tree.VTreeView(parent=self, columns=('Namespace', 'Structure'))

class VQStructSelectView(vq_tree.VQTreeView):

    def __init__(self, vsbuilder, parent=None):
        vq_tree.VQTreeView.__init__(self, parent=parent)
        self.vsbuilder = vsbuilder

        model = vq_tree.VQTreeModel(parent=self, columns=('Namespace', 'Structure'))
        for nsname in vsbuilder.getVStructNamespaceNames():
            pnode = model.append((nsname, ''))
            pnode.structname = None
            for sname in vsbuilder.getVStructNames(namespace=nsname):
                spnode = model.append(('', sname), parent=pnode)
                spnode.structname = '%s.%s' % (nsname, sname)

        for sname in vsbuilder.getVStructNames():
            node = model.append( ('', sname ) )
            node.structname = sname

        self.setModel(model)

class VQStructSelectDialog(QDialog):

    def __init__(self, vsbuilder, parent=None):
        QDialog.__init__(self, parent=parent)
        self.structname = None

        self.setWindowTitle('Select a structure...')

        vlyt = QVBoxLayout()
        hlyt = QHBoxLayout()

        self.structtree = VQStructSelectView(vsbuilder, parent=self)

        hbox = QWidget(parent=self)

        ok = QPushButton("Ok", parent=hbox)
        cancel = QPushButton("Cancel", parent=hbox)

        self.structtree.doubleClicked.connect( self.dialog_activated )

        ok.clicked.connect(self.dialog_ok)
        cancel.clicked.connect(self.dialog_cancel)

        hlyt.addStretch(1)
        hlyt.addWidget(cancel)
        hlyt.addWidget(ok)
        hbox.setLayout(hlyt)

        vlyt.addWidget(self.structtree)
        vlyt.addWidget(hbox)
        self.setLayout(vlyt)

        self.resize(500, 500)

    def dialog_activated(self, idx):
        if idx.isValid():
            pnode = idx.internalPointer()
            self.structname = pnode.structname
        self.accept()

    def dialog_ok(self):
        for idx in self.structtree.selectedIndexes():
            pnode = idx.internalPointer()
            self.structname = pnode.structname
        self.accept()

    def dialog_cancel(self):
        self.reject()

@idlethreadsync
def selectStructure(vsbuilder, parent=None):
    d = VQStructSelectDialog(vsbuilder, parent=parent)
    r = d.exec_()
    return d.structname

class VQStructNamespacesView(vq_tree.VQTreeView):

    def __init__(self, parent=None):
        vq_tree.VQTreeView.__init__(self, parent=parent)

        model = vq_tree.VQTreeModel(parent=self, columns=('Subsystem', 'Module Name'))

        win = model.append(('windows', ''))
        xp_i386_user = model.append(('Windows XP i386 Userland', ''), parent=win)
        xp_i386_ntdll = model.append(('','ntdll'), parent=xp_i386_user)
        xp_i386_ntdll.modinfo = ('ntdll','vstruct.defs.windows.win_5_1_i386.ntdll')

        xp_i386_kern = model.append(('Windows XP i386 Kernel', ''), parent=win)
        xp_i386_nt = model.append(('','nt'), parent=xp_i386_kern)
        xp_i386_nt.modinfo = ('nt','vstruct.defs.windows.win_5_1_i386.ntoskrnl')
        xp_i386_win32k = model.append(('','win32k'), parent=xp_i386_kern)
        xp_i386_win32k.modinfo = ('win32k','vstruct.defs.windows.win_5_1_i386.win32k')

        win7_amd64_user = model.append(('Windows 7 amd64 Userland', ''), parent=win)
        win7_amd64_ntdll = model.append(('','ntdll'), parent=win7_amd64_user)
        win7_amd64_ntdll.modinfo = ('ntdll','vstruct.defs.windows.win_6_1_amd64.ntdll')

        pos = model.append(('posix',''))
        pos_elf = model.append(('', 'Elf'), parent=pos)
        pos_elf.modinfo = ('elf', 'vstruct.defs.elf')

        self.setModel(model)

class VQStructNamespaceDialog(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        self.modinfo = None

        self.setWindowTitle('Select a module...')

        vlyt = QVBoxLayout()
        hlyt = QHBoxLayout()

        self.structtree = VQStructNamespacesView(parent=self)

        hbox = QWidget(parent=self)

        ok = QPushButton("Ok", parent=hbox)
        cancel = QPushButton("Cancel", parent=hbox)

        self.structtree.doubleClicked.connect( self.dialog_activated )

        ok.clicked.connect(self.dialog_ok)
        cancel.clicked.connect(self.dialog_cancel)

        hlyt.addStretch(1)
        hlyt.addWidget(cancel)
        hlyt.addWidget(ok)
        hbox.setLayout(hlyt)

        vlyt.addWidget(self.structtree)
        vlyt.addWidget(hbox)
        self.setLayout(vlyt)

        self.resize(500, 500)

    def dialog_activated(self, idx):
        if idx.isValid():
            pnode = idx.internalPointer()
            self.modinfo = getattr(pnode, 'modinfo', None)
        self.accept()

    def dialog_ok(self):
        for idx in self.structtree.selectedIndexes():
            pnode = idx.internalPointer()
            self.modinfo = getattr(pnode, 'modinfo', None)
        self.accept()

    def dialog_cancel(self):
        self.reject()

@idlethreadsync
def selectStructNamespace(parent=None):
    d = VQStructNamespaceDialog(parent=parent)
    r = d.exec_()
    return d.modinfo

