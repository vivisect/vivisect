import sys
import logging
import traceback

# Some common GUI helpers
try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QTreeView
except:
    from PyQt4 import QtCore
    from PyQt4.QtGui import QTreeView

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())



class ACT:
    def __init__(self, meth, *args, **kwargs):
        self.meth = meth
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        try:
            return self.meth( *self.args, **self.kwargs )
        except:
            logger.warn("error in ACT(%s, %s, %s)", str(self.meth), str(self.args), str(self.kwargs))
            logger.debug(''.join(traceback.format_exception(*sys.exc_info())))


class VqtModel(QtCore.QAbstractItemModel):

    columns = ('one','two')
    editable = None
    dragable = False

    def __init__(self, rows=()):
        QtCore.QAbstractItemModel.__init__(self)
        # Make sure the rows are lists ( so we can mod them )
        self.rows = [ list(row) for row in rows ]
        if self.editable is None:
            self.editable = [False,] * len(self.columns)

    def index(self, row, column, parent):
        return self.createIndex(row, column, self.rows[row])

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, index):
        if index.internalPointer() in self.rows:
            return 0
        return len(self.rows)

    def data(self, index, role):
        if role == 0: 
            row = index.row()
            col = index.column()
            return self.rows[row][col]

        else:
            return None

    def columnCount(self, index):
        return len(self.columns)

    def headerData(self, column, orientation, role):

        if ( orientation == QtCore.Qt.Horizontal and
             role == QtCore.Qt.DisplayRole):

            return self.columns[column]

        return None

    def flags(self, index):
        if not index.isValid():
            return 0
        flags = QtCore.QAbstractItemModel.flags(self, index)
        col = index.column()
        if self.editable[col]:
            flags |= QtCore.Qt.ItemIsEditable

        if self.dragable:
            flags |= QtCore.Qt.ItemIsDragEnabled# | QtCore.Qt.ItemIsDropEnabled

        return flags

    #def data(self, index, role):
        #if not index.isValid():
            #return None
        #item = index.internalPointer()
        #if role == QtCore.Qt.DisplayRole:
            #return item.data(index.column())
        #if role == QtCore.Qt.UserRole:
            #return item
        #return None

    #def _vqt_set_data(self, row, col, value):
        #return False

    #def appends(self, rows):

    def append(self, row, parent=QtCore.QModelIndex()):
        #pidx = self.createIndex(parent.row(), 0, parent)
        i = len(self.rows)
        self.beginInsertRows(parent, i, i)
        self.rows.append( row )
        #node = parent.append(rowdata)
        self.endInsertRows()
        self.layoutChanged.emit()

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if not index.isValid():
            return False

        # If this is the edit role, fire the vqEdited thing
        if role == QtCore.Qt.EditRole:
            #value = self.vqEdited(node, index.column(), value)
            #if value is None:
                #return False

            row = index.row()
            col = index.column()
            if not self._vqt_set_data( row, col, value ):
                return False

        return True

    def pop(self, row, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row+1)
        self.rows.pop(row)
        self.endRemoveRows()

    #def mimeTypes(self):
        #types = QtCore.QStringList()
        #types.append('vqt/row')
        #return types

    #def mimeData(self, idx):
        #nodes = [ self.rows[i.row()][-1] for i in idx ]
        #mdata = QtCore.QMimeData()
        #mdata.setData('vqt/rows',json.dumps(nodes))
        #return mdata

class VqtView(QTreeView):

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent=parent)
        self.setAlternatingRowColors( True )
        self.setSortingEnabled( True )

    def getSelectedRows(self):
        ret = []
        rdone = {}
        model = self.model()
        for idx in self.selectedIndexes():

            if rdone.get(idx.row()):
                continue

            rdone[idx.row()] = True
            ret.append( model.mapToSource(idx).internalPointer() )

        return ret

    def setModel(self, model):
        smodel = QtCore.QSortFilterProxyModel(parent=self)
        smodel.setSourceModel(model)
        ret = QTreeView.setModel(self, smodel)
        c = len(model.columns)
        for i in range(c):
            self.resizeColumnToContents(i)
        return ret

    def getModelRows(self):
        return self.model().sourceModel().rows

    def getModelRow(self, idx):
        idx = self.model().mapToSource(idx)
        return idx.row(),idx.internalPointer()
