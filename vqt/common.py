import logging

# Some common GUI helpers
from PyQt5 import QtCore 
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QTreeView, QDialog, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QLabel, QMessageBox
from vqt.main import idlethread

logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.warning("error in ACT(%s, %s, %s)", str(self.meth), str(self.args), str(self.kwargs))
            logger.warning(str(e))


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
        if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
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
            ret.append(model.mapToSource(idx).internalPointer())

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
        return idx.row(), idx.internalPointer()


class DynamicDialog(QDialog):
    '''
    Pop up and ask the questions.  If "OK", returns a dict with answers.  
    Intended for easy access by extensions, and possibly for envi.Config items.
    eg:

    >>> dynd = vcmn.DynamicDialog('Test Dialog')
    >>> dynd.addComboBox('testbox', ["a", 'b', 'c'], dfltidx=2)
    >>> dynd.addTextField('foo', dflt="blah blah")
    >>> dynd.addIntHexField('bar', dflt=47145)
    >>> results = dynd.prompt()
        <when returns, after user clicks OK>
    >>> print(results)
    {'testbox': 'c', 'foo': 'blah blah', 'bar': 47145}

            or...

    >>> results = dynd.prompt()
        <if user hits cancel>
    >>> print(results)
    {}

    '''
    _TEXT = 0
    _COMBO = 1
    _INTHEX = 2

    def __init__(self, title, height=100, width=300, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.items = {}
        self.resize(width, height)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel);
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def addComboBox(self, fieldname, itemlist, dfltidx=None, title=None):
        '''
        Adds a Combo Box to the dialog.  The returned value will be one of the 
        options provided in itemlist.

        dfltidx is the index in the itemlist which should start out selected.
        default is the first item.
        '''
        if fieldname in self.items:
            raise Exception("ComboBox: Adding field to DynamicDialog twice: %r (existing: %r)"\
                    % (fieldname, self.items.get(fieldname)))

        cb = QComboBox()
        cb.addItems(itemlist)
        self.items[fieldname] = (self._COMBO, cb)

        if dfltidx is not None:
            cb.setCurrentIndex(dfltidx)
        if title is None:
            title = fieldname

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(title))
        hbox.addWidget(cb)
        self.vbox.addLayout(hbox)

    def addTextField(self, fieldname, dflt=None, title=None):
        '''
        Adds a standard Text Box (QLineEdit) to the dialog.
        Return value is basically untouched.
        '''
        if fieldname in self.items:
            raise Exception("Text: Adding field to DynamicDialog twice: %r (existing: %r)"\
                    % (fieldname, self.items.get(fieldname)))

        le = QLineEdit()
        self.items[fieldname] = (self._TEXT, le)

        if dflt is not None:
            le.setText(dflt)
        if title is None:
            title = fieldname

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(title))
        hbox.addWidget(le)
        self.vbox.addLayout(hbox)

    def addIntHexField(self, fieldname, dflt=None, title=None):
        '''
        Adds a number field to the dialog.  It's a QLineEdit field with a 
        QRegExpValidator, using regex for Hexidecimal numbers, which also
        allows for Decimal.  
        Returned value is an int.
        The value is interpreted as decimal (ie. int(foo)) unless non-numeric digits 
        encountered, in which case it's interpreted as hex (ie. int(foo, 16))
        '''
        if fieldname in self.items:
            raise Exception("IntHex: Adding field to DynamicDialog twice: %r (existing: %r)"\
                    % (fieldname, self.items.get(fieldname)))

        le = QLineEdit()
        le.setValidator(QRegExpValidator(QtCore.QRegExp("^(-)?(0x)?[0-9a-fA-F]+$")))
        self.items[fieldname] = (self._INTHEX, le)

        if dflt is not None:
            le.setText(str(dflt))
        if title is None:
            title = fieldname

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(title))
        hbox.addWidget(le)
        self.vbox.addLayout(hbox)

    def prompt(self):
        '''
        Temporarily adds a ButtonBox with "OK" and "Cancel", and shows the 
        dialog to the user.  Then removes the buttonBox.
        '''
        self.vbox.addWidget(self.buttonBox);
        res = self.exec_()
        self.vbox.removeWidget(self.buttonBox);

        retval = {}
        if res:
            for key, (ftype, field) in self.items.items():
                if ftype == self._INTHEX:
                    val = field.text()
                    if len(val):
                        try:
                            val = int(val)
                        except ValueError:
                            val = int(val, 16)
                    else:
                        val = 0

                elif ftype == self._TEXT:
                    val = field.text()

                elif ftype == self._COMBO:
                    val = field.currentText()

                retval[key] = val

        return retval

@idlethread
def warning(msg, info):
    msgbox = QMessageBox()
    msgbox.setWindowTitle('Warn: %s' % msg)
    msgbox.setText('Warn: %s' % msg)
    msgbox.setInformativeText(info)
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.exec_()

@idlethread
def information(msg, info):
    msgbox = QMessageBox()
    msgbox.setWindowTitle('%s' % msg)
    msgbox.setText('%s' % msg)
    msgbox.setInformativeText(info)
    msgbox.setIcon(QMessageBox.Information)
    msgbox.exec_()

@idlethread
def scripterr(msg, info):
    msgbox = QMessageBox()
    msgbox.setWindowTitle('Script Error: %s' % msg)
    msgbox.setText('Script Error: %s' % msg)
    msgbox.setInformativeText(info)
    msgbox.exec_()

