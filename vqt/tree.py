from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeView


class VQTreeItem(object):

    def __init__(self, rowdata, parent):
        self.parent = parent
        self.rowdata = list(rowdata)
        self.children = []

    def append(self, rowdata):
        child = VQTreeItem(rowdata, self)
        self.children.append(child)
        return child

    def delete(self, rowdata):
        idx = 0
        for child in self.children:
            if child.rowdata == rowdata:
                return self.children.pop(idx)

            idx += 1

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.rowdata)

    def data(self, column):
        if column > len(self.rowdata):
            return None
        return str(self.rowdata[column])

    def row(self):
        '''
        Retrieve our row number.
        '''
        if self.parent:
            return self.parent.children.index(self)
        return 0

class VQTreeModel(QtCore.QAbstractItemModel):
    '''
    A QT tree model that uses the tree API from visgraph
    to hold the data...
    '''

    columns = ('A first column!', 'The Second Column!')
    editable = None
    dragable = False

    def __init__(self, parent=None, columns=None):

        if columns is not None:
            self.columns = columns

        QtCore.QAbstractItemModel.__init__(self, parent=parent)
        self.rootnode = VQTreeItem((), None)

        if self.editable is None:
            self.editable = [False,] * len(self.columns)

    def vqEdited(self, pnode, col, value):
        return value

    def append(self, rowdata, parent=None):
        if parent is None:
            parent = self.rootnode

        pidx = self.createIndex(parent.row(), 0, parent)
        i = len(parent.children)
        self.beginInsertRows(pidx, i, i)
        node = parent.append(rowdata)
        self.endInsertRows()
        self.layoutChanged.emit()
        return node

    def vqDelRow(self, rowdata, parent=None):
        if parent is None:
            parent = self.rootnode

        parent.delete(rowdata)

    def sort(self, colnum, order=0):
        self.layoutAboutToBeChanged.emit()
        self.rootnode.children.sort(key=lambda k: k.rowdata[colnum], reverse=bool(order))
        self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = QtCore.QAbstractItemModel.flags(self, index)
        col = index.column()
        if self.editable[col]:
            flags |= QtCore.Qt.ItemIsEditable
        if self.dragable:
            flags |= QtCore.Qt.ItemIsDragEnabled
        return flags

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())

        if role == QtCore.Qt.UserRole:
            return item

        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        node = index.internalPointer()
        if not node:
            return False

        # If this is the edit role, fire the vqEdited thing
        if role == QtCore.Qt.EditRole:
            value = self.vqEdited(node, index.column(), value)
            if value is None:
                return False

        node.rowdata[index.column()] = value
        self.dataChanged.emit(index, index)

        return True

    def headerData(self, column, orientation, role):
        if ( orientation == QtCore.Qt.Horizontal and
             role == QtCore.Qt.DisplayRole):

            return self.columns[column]

        return None

    def index(self, row, column, parent):

        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        pitem = parent.internalPointer()
        if not pitem:
            pitem = self.rootnode

        item = pitem.child(row)
        if not item:
            return QtCore.QModelIndex()

        return self.createIndex(row, column, item)

    def parent(self, index):

        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer()
        if not item:
            return QtCore.QModelIndex()

        pitem = item.parent

        if pitem == self.rootnode:
            return QtCore.QModelIndex()

        if pitem is None:
            return QtCore.QModelIndex()

        return self.createIndex(pitem.row(), 0, pitem)

    def rowCount(self, parent=QtCore.QModelIndex()):

        if parent.column() > 0:
            return 0

        pitem = parent.internalPointer()
        if not pitem:
            pitem = self.rootnode

        return len(pitem.children)

class VQTreeView(QTreeView):

    def __init__(self, parent=None, cols=None, **kwargs):
        QTreeView.__init__(self, parent=parent, **kwargs)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)

        if cols is not None:
            model = VQTreeModel(parent=self, columns=cols)
            self.setModel(model)

    def vqSizeColumns(self):
        c = self.model().columnCount()
        for i in range(c):
            self.resizeColumnToContents(i)

    def setModel(self, model):
        model.dataChanged.connect( self.dataChanged )
        model.rowsInserted.connect( self.rowsInserted )
        return QTreeView.setModel(self, model)
