
import vqt.tree as vq_tree
import vqt.basics as vq_basics
import vivisect.base as viv_base
import envi.qt.memory as e_q_memory
import visgraph.pathcore as vg_path
import envi.qt.memcanvas as e_q_memcanvas
import vivisect.qt.ctxmenu as v_q_ctxmenu

try:
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QMenu
    from PyQt5.QtCore import QSortFilterProxyModel
except:
    from PyQt4 import QtGui
    from PyQt4.QtGui import QMenu
    from PyQt4.QtCore import QSortFilterProxyModel

from vqt.main import *
from vqt.common import *
from vivisect.const import *

class VivFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent=parent)
        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(-1)

    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)

class VivNavModel(e_q_memory.EnviNavModel):
    pass

class VivView(VqtView, viv_base.VivEventCore):
    '''
    In any vivisect list/tree view, the first column will be
    an address expression.  Other than that, all bets are off.
    '''
    def __init__(self, vw, parent=None):
        VqtView.__init__(self, parent=parent)
        viv_base.VivEventCore.__init__(self, vw)
        self.vw = vw
        self.vivgui = vw.getVivGui()
        self.vivgui.addEventCore(self)

class VivLocModel(VqtModel):
    columns = ('Address','Location')

class VivLocView(VivView):

    def __init__(self, vw, loctypes, parent=None):
        VivView.__init__(self, vw, parent=parent)
        self.loctypes = loctypes

        locs = []
        for ltype in self.loctypes:
            locs.extend( vw.getLocations(ltype) )

        rows = [ ('0x%.8x' % loc[0], vw.reprLocation(loc), loc) for loc in locs ]

        model = VivLocModel(rows=rows)
        self.setModel(model)

    def VWE_ADDLOCATION(self, vw, event, loc):
        lva, lsize, ltype, linfo = loc
        if ltype in self.loctypes:
            self.model().sourceModel().append( ('0x%.8x' % lva, self.vw.reprLocation(loc), loc) )

    def VWE_DELLOCATION(self, vw, event, einfo):
        lva, lsize, ltype, linfo = einfo
        if ltype in self.loctypes:
            print 'DEL ONE!'

def getLocView(vw, loctypes, title, parent=None):
    view = VivLocView( vw, loctypes, parent=parent)
    view.setWindowTitle(title)
    return vw.getVivGui().vqDockWidget( view, floating=True )

class VQVivTreeView(vq_tree.VQTreeView, viv_base.VivEventCore):

    window_title = "VivTreeView"
    _viv_navcol = 0

    def __init__(self, vw=None, vwqgui=None, **kwargs):
        vq_tree.VQTreeView.__init__(self, parent=vwqgui, **kwargs)
        viv_base.VivEventCore.__init__(self, vw)

        self.vw = vw
        self.vwqgui = vwqgui
        self._viv_va_nodes = {}

        vwqgui.addEventCore(self)

        self.setWindowTitle(self.window_title)
        self.setSortingEnabled(True)
        self.setDragEnabled( True )

        self.doubleClicked.connect( self.doubleClickedSignal )

    def doubleClickedSignal(self, idx):
        if idx.isValid() and self._viv_navcol != None:
            # we need to access the selected navcol, but the current index will be the cell double-clicked
            expr = idx.sibling(idx.row(), self._viv_navcol).data()
            vqtevent('envi:nav:expr', ('viv',expr,None))
            return True

    def contextMenuEvent(self, event):
        menu = QMenu(parent=self)
        idxlist = self.selectedIndexes()
        if not idxlist:
            return

        idx = idxlist[0]
        if idx.isValid() and self._viv_navcol != None:
            pnode = idx.internalPointer()
            expr = pnode.rowdata[self._viv_navcol]
            v_q_ctxmenu.buildContextMenu(self.vw, expr=expr, menu=menu)

        menu.exec_(event.globalPos())

    def vivAddRow(self, va, *row):
        node = self.model().append(row)
        node.va = va
        self._viv_va_nodes[va] = node
        return node

    def vivDelRow(self, va):
        node = self._viv_va_nodes.pop(va, None)
        if node:
            self.model().vqDelRow(node)

    def vivSetData(self, va, col, val):
        '''
        Set a row/col in the data model.  This will quietly fail
        if we don't contain a row for the va (makes users not need
        to check...)

        Example: view.vivSetData(0x41414141, 2, 'Woot Function')

        NOTE: This is for use by the VWE_ event callback handlers!
        '''
        pnode = self._viv_va_nodes.get(va)
        if not pnode:
            return

        idx = self.model().sourceModel().createIndex(pnode.row(), col, pnode)
        # We are *not* the edit role...
        self.model().sourceModel().setData(idx, val, role=QtCore.Qt.DisplayRole)

    def vivGetData(self, va, col):
        pnode = self._viv_va_nodes.get(va)
        if not pnode:
            return None
        return pnode.rowdata[col]

class VivFilterView(QWidget):
    '''
    This is the primary window for the VQViv*Views if they want to include filtering
    '''
    window_title = '__undefined__'
    view_type = None

    def __init__(self, vw, vwqgui, *args, **kwargs):
        QWidget.__init__(self)
        
        self.view = self.view_type(vw, vwqgui, *args, **kwargs)
        self.ffilt = VQFilterWidget(self)

        layout = vq_basics.VBox(self.view, self.ffilt)
        self.setLayout(layout)

        self.ffilt.filterChanged.connect(self.textFilterChanged)
        self.setWindowTitle(self.view.window_title)

    def textFilterChanged(self):
        regExp = QtCore.QRegExp(self.ffilt.text(), 
                                self.ffilt.caseSensitivity(),
                                self.ffilt.patternSyntax())

        self.view.filterModel.setFilterRegExp(regExp)

    def __getattr__(self, name):
        return getattr(self.view, name)

class VQVivLocView(VQVivTreeView):

    loctypes = ()

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        # whether we use it or not, include a sort/filter proxy model
        self.navModel = VivNavModel(self._viv_navcol, parent=self, columns=self.columns)
        self.filterModel = VivFilterModel()
        self.filterModel.setSourceModel(self.navModel)
        self.setModel(self.filterModel)
        self.vqLoad()
        self.vqSizeColumns()

    def vqLoad(self):

        for l in self.loctypes:
            for lva, lsize, ltype, linfo in self.vw.getLocations(l):
                self.vivAddLocation(lva, lsize, ltype, linfo)

    def VWE_DELLOCATION(self, vw, event, einfo):
        lva, lsize, ltype, linfo = einfo
        self.vivDelRow(lva)

    def VWE_ADDLOCATION(self, vw, event, einfo):
        lva, lsize, ltype, linfo = einfo
        if ltype in self.loctypes:
            self.vivAddLocation(lva, lsize, ltype, linfo)

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        print "FIXME OVERRIDE"

class VQVivStringsViewPart(VQVivLocView):

    columns = ('Address','String')
    loctypes = (LOC_STRING, LOC_UNI)
    window_title = 'Strings'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        s = self.vw.readMemory(lva, lsize)
        if ltype == LOC_UNI:
            s = s.decode('utf-16le', 'ignore')
        self.vivAddRow(lva, '0x%.8x' % lva, repr(s))

class VQVivImportsViewPart(VQVivLocView):

    columns = ('Address', 'Library', 'Function')
    loctypes = (LOC_IMPORT,)
    window_title = 'Imports'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        libname, funcname = linfo.split('.', 1)
        self.vivAddRow(lva, '0x%.8x' % lva, libname, funcname)

class VQVivStructsViewPart(VQVivLocView):
    columns = ('Address', 'Structure', 'Loc Name')
    loctypes = (LOC_STRUCT,)
    window_title = 'Structures'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        sym = self.vw.getSymByAddr(lva)
        self.vivAddRow(lva, '0x%.8x' % lva, linfo, str(sym))

class VQVivExportsViewPart(VQVivTreeView):

    window_title = 'Exports'
    columns = ('Address', 'File', 'Export')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.navModel = VivNavModel(self._viv_navcol, self, columns=self.columns)
        self.filterModel = VivFilterModel()
        self.filterModel.setSourceModel(self.navModel)
        self.setModel(self.filterModel)
        self.vqLoad()
        self.vqSizeColumns()

    def vqLoad(self):
        for va, etype, ename, fname in self.vw.getExports():
            self.vivAddExport(va, etype, ename, fname)

    def vivAddExport(self, va, etype, ename, fname):
        self.vivAddRow(va, '0x%.8x' % va, fname, ename)

    def VWE_ADDEXPORT(self, vw, event, einfo):
        va, etype, ename, fname = einfo
        self.vivAddExport(va, etype, ename, fname)

class VQVivSegmentsView(VQVivTreeView):

    _viv_navcol = 2
    window_title = 'Segments'
    columns = ('Module','Section', 'Address', 'Size')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.setModel( VivNavModel(self._viv_navcol, self, columns=self.columns) )
        self.vqLoad()
        self.vqSizeColumns()

    def vqLoad(self):
        for va, size, sname, fname in self.vw.getSegments():
            self.vivAddRow(va, fname, sname, '0x%.8x' % va, str(size))


class VQFilterWidget(QLineEdit):
    filterChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent=parent)

        self.setClearButtonEnabled(True)
        self.m_patternGroup = QActionGroup(self)
        self.textChanged.connect(self.filterChanged)

        self.menu = QMenu(self)
        self.m_caseSensitivityAction = self.menu.addAction("Case Sensitive")
        self.m_caseSensitivityAction.setCheckable(True)
        self.m_caseSensitivityAction.toggled.connect(self.filterChanged)


        self.menu.addSeparator();
        self.m_patternGroup.setExclusive(True);

        self.patternAction = self.menu.addAction("Fixed String");
        self.patternAction.setData(QtCore.QVariant(int(QtCore.QRegExp.FixedString)));
        self.patternAction.setCheckable(True);
        self.patternAction.setChecked(True);
        self.m_patternGroup.addAction(self.patternAction);

        self.patternAction = self.menu.addAction("Regular Expression");
        self.patternAction.setCheckable(True);
        self.patternAction.setData(QtCore.QVariant(int(QtCore.QRegExp.RegExp2)));
        self.m_patternGroup.addAction(self.patternAction);

        self.patternAction = self.menu.addAction("Wildcard");
        self.patternAction.setCheckable(True);
        self.patternAction.setData(QtCore.QVariant(int(QtCore.QRegExp.Wildcard)));
        self.m_patternGroup.addAction(self.patternAction);
        
        self.m_patternGroup.triggered.connect(self.filterChanged);

        self.icon = QtGui.QIcon(QtGui.QPixmap(":/images/find.png"))
        self.optionsButton = QToolButton()
        self.optionsButton.setCursor(QtCore.Qt.ArrowCursor)
        self.optionsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.optionsButton.setStyleSheet("* { border: none; }")
        self.optionsButton.setIcon(self.icon)
        self.optionsButton.setMenu(self.menu)
        self.optionsButton.setPopupMode(QToolButton.InstantPopup)

        self.optionsAction = QWidgetAction(self)
        self.optionsAction.setDefaultWidget(self.optionsButton)
        self.addAction(self.optionsAction, QLineEdit.LeadingPosition)

    def caseSensitivity(self):
        return  (QtCore.Qt.CaseInsensitive, QtCore.Qt.CaseSensitive)[self.m_caseSensitivityAction.isChecked()]

    def setCaseSensitivity(self, cs):
        self.m_caseSensitivityAction.setChecked(cs == QtCore.Qt.CaseSensitive)

    def patternSyntax(self):
        return self.patternSyntaxFromAction(self.m_patternGroup.checkedAction())

    def setPatternSyntax(self, s):
        for a in self.m_patternGroup.actions():
            if (self.patternSyntaxFromAction(a) == s):
                a.setChecked(True)
                break

    def patternSyntaxFromAction(self, a):
        return int(a.data())

class VQVivFunctionsViewPart(VQVivTreeView):

    _viv_navcol = 0
    window_title = 'Functions'
    columns = ('Name','Address', 'Size', 'Ref Count')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui, withfilter=True)
        
        self.navModel = VivNavModel(self._viv_navcol, self, columns=self.columns)
        self.filterModel = VivFilterModel()
        self.filterModel.setSourceModel(self.navModel)
        self.setModel(self.filterModel)

        self.vqLoad()
        self.vqSizeColumns()

    def vqLoad(self):
        for fva in self.vw.getFunctions():
            self.vivAddFunction(fva)

    def VWE_ADDFUNCTION(self, vw, event, einfo):
        fva, fmeta = einfo
        self.vivAddFunction(fva)

    def VWE_DELFUNCTION(self, vw, event, fva):
        self.vivDelRow(fva)

    def VWE_SETNAME(self, vw, event, einfo):
        va, name = einfo
        self.vivSetData(va, 0, name)

    def vivAddFunction(self, fva):

        size   = self.vw.getFunctionMeta(fva, "Size", -1)
        fname  = self.vw.getName(fva)
        xcount = len(self.vw.getXrefsTo(fva))
        self.vivAddRow(fva, fname, '0x%.8x' % fva, size, xcount)

    def VWE_ADDXREF(self, vw, event, einfo):
        fromva, tova, rtype, rflag = einfo
        cnt = self.vivGetData(tova, 3)
        if cnt == None:
            return
        self.vivSetData(tova, 3, cnt + 1)

    def VWE_DELXREF(self, vw, event, einfo):
        fromva, tova, rtype, rflag = einfo
        cnt = self.vivGetData(tova, 3)
        if cnt == None:
            return
        self.vivSetData(tova, 3, cnt - 1)

    def VWE_SETFUNCMETA(self, vw, event, einfo):
        funcva, key, value = einfo
        if key == "Size":
            self.vivSetData(funcva, 2, value)

vaset_coltypes = {
    VASET_STRING:str,
    VASET_ADDRESS:long,
    VASET_INTEGER:long,
}


def reprAddress(vw, item):
    return "0x%x (%s)" % (item, vw.reprPointer(item))

def reprString(vw, item):
    return item

def reprIntLong(vw, item):
    if item > 1024:
        return hex(item)
    return item

def reprHextup(vw, item):
    return [hex(x) for x in item]

def reprSmart(vw, item):
    ptype = type(item)
    if ptype in (int, long):
        if -1024 < item < 1024 :
            return str(item)
        elif vw.isValidPointer(item):
            return vw.reprPointer(item)
        else:
            return hex(item)

    elif ptype in (list, tuple):
        return reprComplex(vw, item) # recurse

    elif ptype == dict:
        return '{%s}' % ','.join(["%s:%s" % (reprSmart(vw,k), reprSmart(vw,v)) for k,v in item.items()])

    else:
        return repr(item)

def reprComplex(vw, item):
    retval = []
    for part in item:
        retval.append(reprSmart(vw, part))

    return ', '.join(retval)


vaset_reprHandlers = {
    VASET_ADDRESS:  reprAddress,
    VASET_STRING:   reprString,
    VASET_INTEGER:  reprIntLong,
    VASET_HEXTUP:   reprHextup,
    VASET_COMPLEX:  reprComplex,
}

class VQVivVaSetViewPart(VQVivTreeView):

    window_title = 'Va Set'
    _viv_navcol = 0

    def __init__(self, vw, vwqgui, setname):
        self._va_setname = setname
        self.window_title = 'Va Set: %s' % setname

        setdef = vw.getVaSetDef( setname )
        cols = [ cname for (cname,ctype) in setdef ]

        VQVivTreeView.__init__(self, vw, vwqgui)

        self.setModel( VivNavModel(self._viv_navcol, self, columns=cols) )
        self.vqLoad()
        self.vqSizeColumns()

    def VWE_SETVASETROW(self, vw, event, einfo):
        setname, row = einfo
        if setname == self._va_setname:
            va = row[0]
            self.vivAddRow( va, *self.reprRow(row) )

    def vqLoad(self):
        setdef = self.vw.getVaSetDef( self._va_setname )
        rows = self.vw.getVaSetRows( self._va_setname )
        for row in rows:
            va = row[0]
            self.vivAddRow(va, *self.reprRow(row))

    def reprRow(self, row):
        row = [item for item in row]
        setdef = self.vw.getVaSetDef( self._va_setname )
        
        row[0] = hex(row[0])
        for idx in range(1,len(row)):
            item = row[idx]
            itype = setdef[idx][1]

            handler = vaset_reprHandlers.get(itype)

            if handler == None:
                row[idx] = repr(row[idx])
            else:
                row[idx] = handler(self.vw, item)

        return row

class VQXrefViewPart(VQVivTreeView):

    _viv_navcol = 0

    def __init__(self, vw, vwqgui, xrefs=(), title='Xrefs'):

        self.window_title = title

        VQVivTreeView.__init__(self, vw, vwqgui)
        model = VivNavModel(self._viv_navcol, self, columns=('Xref From', 'Xref Type', 'Xref Flags', 'Func Name'))
        self.setModel(model)

        for fromva, tova, rtype, rflags in xrefs:
            fva = vw.getFunction(fromva)
            funcname = ''
            if fva != None:
                funcname = vw.getName(fva)
            self.vivAddRow(fromva, '0x%.8x' % fromva, rtype, rflags, funcname)

        self.vqSizeColumns()

class VQVivNamesViewPart(VQVivTreeView):

    _viv_navcol = 0
    window_title = 'Workspace Names'
    columns = ('Address', 'Name')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.navModel = VivNavModel(self._viv_navcol, self, columns=self.columns)
        self.filterModel = VivFilterModel()
        self.filterModel.setSourceModel(self.navModel)
        self.setModel(self.filterModel)
        self.vqLoad()
        self.vqSizeColumns()

    def vqLoad(self):
        for name in self.vw.getNames():
            self.vivAddName(name)

    def VWE_SETNAME(self, vw, event, einfo):
        va, name = einfo
        #self.vivSetData(va, 1, name)
        self.vivAddName(einfo)

    def vivAddName(self, nifo):
        va, name = nifo
        if self.vivGetData(va, 0) == None:
            self.vivAddRow(va, '0x%.8x' % va, name)
        else:
            self.vivSetData(va, 1, name)


#FIXME: is this a good time to use a @decorator?
# Filtering VQTreeViews
class VQVivFunctionsView(VivFilterView):
    view_type = VQVivFunctionsViewPart

class VQVivNamesView(VivFilterView):
    view_type = VQVivNamesViewPart

class VQVivExportsView(VivFilterView):
    view_type = VQVivExportsViewPart

class VQVivVaSetView(VivFilterView):
    view_type = VQVivVaSetViewPart

class VQXrefView(VivFilterView):
    view_type = VQXrefViewPart


# Filtering VQVivLocViews
class VQVivStringsView(VivFilterView):
    view_type = VQVivStringsViewPart

class VQVivImportsView(VivFilterView):
    view_type = VQVivImportsViewPart

class VQVivStructsView(VivFilterView):
    view_type = VQVivStructsViewPart

