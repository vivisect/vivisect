import vqt.tree as vq_tree
import vivisect.base as viv_base
import envi.qt.memory as e_q_memory
import vivisect.qt.ctxmenu as v_q_ctxmenu

from PyQt5.QtWidgets import QMenu

from vqt.main import *
from vqt.common import *
from vivisect.const import *

class VivNavModel(e_q_memory.EnviNavModel):
    pass

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
        if idx.isValid() and self._viv_navcol is not None:
            pnode = idx.internalPointer()
            expr = pnode.rowdata[self._viv_navcol]
            vqtevent('envi:nav:expr', ('viv', expr, None))
            return True

    def contextMenuEvent(self, event):
        menu = QMenu(parent=self)
        idxlist = self.selectedIndexes()
        if not idxlist:
            return

        idx = idxlist[0]
        if idx.isValid() and self._viv_navcol is not None:
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

        idx = self.model().createIndex(pnode.row(), col, pnode)
        # We are *not* the edit role...
        self.model().setData(idx, val, role=None)

    def vivGetData(self, va, col):
        pnode = self._viv_va_nodes.get(va)
        if not pnode:
            return None
        return pnode.rowdata[col]

class VQVivLocView(VQVivTreeView):

    loctypes = ()

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        model = VivNavModel(self._viv_navcol, parent=self, columns=self.columns)
        self.setModel(model)
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
        raise NotImplementedError("LocationViews must override vivAddLocation")

class VQVivStringsView(VQVivLocView):

    columns = ('Address','String')
    loctypes = (LOC_STRING, LOC_UNI)
    window_title = 'Strings'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        s = self.vw.readMemory(lva, lsize)
        if ltype == LOC_UNI:
            s = s.decode('utf-16le', 'ignore')
        else:
            s = s.decode('utf-8', 'ignore')
        self.vivAddRow(lva, '0x%.8x' % lva, repr(s))

class VQVivImportsView(VQVivLocView):

    columns = ('Address', 'Library', 'Function')
    loctypes = (LOC_IMPORT,)
    window_title = 'Imports'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        libname, funcname = linfo.split('.', 1)
        self.vivAddRow(lva, '0x%.8x' % lva, libname, funcname)

class VQVivStructsView(VQVivLocView):
    columns = ('Address', 'Structure', 'Loc Name')
    loctypes = (LOC_STRUCT,)
    window_title = 'Structures'

    def vivAddLocation(self, lva, lsize, ltype, linfo):
        sym = self.vw.getSymByAddr(lva)
        self.vivAddRow(lva, '0x%.8x' % lva, linfo, str(sym))

class VQVivExportsView(VQVivTreeView):

    window_title = 'Exports'
    columns = ('Address', 'File', 'Export')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.setModel( VivNavModel(self._viv_navcol, self, columns=self.columns) )
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

class VQVivFunctionsView(VQVivTreeView):

    _viv_navcol = 0
    window_title = 'Functions'
    columns = ('Name', 'Address', 'Size', 'Ref Count')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.setModel(VivNavModel(self._viv_navcol, self, columns=self.columns))
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
        size = self.vw.getFunctionMeta(fva, "Size", -1)
        funcname = self.vw.getName(fva)
        xcount = len(self.vw.getXrefsTo(fva))
        if fva in self._viv_va_nodes:
            self.vivSetData(fva, 0, funcname)
            self.vivSetData(fva, 1, '0x%.8x' % fva)
            self.vivSetData(fva, 2, size)
            self.vivSetData(fva, 3, xcount)
        else:
            self.vivAddRow(fva, funcname, '0x%.8x' % fva, size, xcount)

    def VWE_ADDXREF(self, vw, event, einfo):
        fromva, tova, rtype, rflag = einfo
        cnt = self.vivGetData(tova, 3)
        if cnt is None:
            return
        self.vivSetData(tova, 3, cnt + 1)

    def VWE_DELXREF(self, vw, event, einfo):
        fromva, tova, rtype, rflag = einfo
        cnt = self.vivGetData(tova, 3)
        if cnt is None:
            return
        self.vivSetData(tova, 3, cnt - 1)

    def VWE_SETFUNCMETA(self, vw, event, einfo):
        funcva, key, value = einfo
        if key == "Size":
            self.vivSetData(funcva, 2, value)

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
    if ptype is int:
        if -1024 < item < 1024:
            return str(item)
        elif vw.isValidPointer(item):
            return vw.reprPointer(item)
        else:
            return hex(item)

    elif ptype in (list, tuple):
        return reprComplex(vw, item) # recurse

    elif ptype is dict:
        return '{%s}' % ','.join(["%s:%s" % (reprSmart(vw,k), reprSmart(vw,v)) for k,v in item.items()])

    else:
        return repr(item)

def reprComplex(vw, item):
    retval = []
    for part in item:
        retval.append(reprSmart(vw, part))

    return ', '.join(retval)


vaset_reprHandlers = {
    VASET_ADDRESS: reprAddress,
    VASET_STRING:  reprString,
    VASET_INTEGER: reprIntLong,
    VASET_HEXTUP:  reprHextup,
    VASET_COMPLEX: reprComplex,
}

class VQVivVaSetView(VQVivTreeView):

    _viv_navcol = 0

    def __init__(self, vw, vwqgui, setname):
        self._va_setname = setname

        setdef = vw.getVaSetDef( setname )
        cols = [ cname for (cname,ctype) in setdef ]

        VQVivTreeView.__init__(self, vw, vwqgui)

        self.setModel( VivNavModel(self._viv_navcol, self, columns=cols) )
        self.vqLoad()
        self.vqSizeColumns()
        self.setWindowTitle('Va Set: %s' % setname)

    def VWE_SETVASETROW(self, vw, event, einfo):
        setname, row = einfo
        if setname == self._va_setname:
            va = row[0]
            self.vivAddRow(va, *self.reprRow(row))

    def vqLoad(self):
        setdef = self.vw.getVaSetDef(self._va_setname)
        rows = self.vw.getVaSetRows(self._va_setname)
        for row in rows:
            va = row[0]
            self.vivAddRow(va, *self.reprRow(row))

    def reprRow(self, row):
        row = [item for item in row]
        setdef = self.vw.getVaSetDef(self._va_setname)

        row[0] = hex(row[0])
        for idx in range(1, len(row)):
            item = row[idx]
            itype = setdef[idx][1]

            handler = vaset_reprHandlers.get(itype)

            if handler is None:
                row[idx] = repr(row[idx])
            else:
                row[idx] = handler(self.vw, item)

        return row

class VQXrefView(VQVivTreeView):

    _viv_navcol = 0

    def __init__(self, vw, vwqgui, xrefs=(), title='Xrefs'):

        self.window_title = title

        VQVivTreeView.__init__(self, vw, vwqgui)
        model = VivNavModel(self._viv_navcol, self, columns=('Xref From', 'Xref Type', 'Xref Flags', 'Func Name'))
        self.setModel(model)

        for fromva, tova, rtype, rflags in xrefs:
            fva = vw.getFunction(fromva)
            funcname = ''
            if fva is not None:
                funcname = vw.getName(fva)
            self.vivAddRow(fromva, '0x%.8x' % fromva, rtype, rflags, funcname)

        self.vqSizeColumns()

class VQVivNamesView(VQVivTreeView):

    _viv_navcol = 0
    window_title = 'Workspace Names'
    columns = ('Address', 'Name')

    def __init__(self, vw, vwqgui):
        VQVivTreeView.__init__(self, vw, vwqgui)
        self.setModel(VivNavModel(self._viv_navcol, self, columns=self.columns))
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
        if self.vivGetData(va, 0) is None:
            self.vivAddRow(va, '0x%.8x' % va, name)
        else:
            self.vivSetData(va, 1, name)
