import itertools
import traceback

import vqt.tree as vq_tree
import vqt.saveable as vq_save
import envi.qt.memory as e_q_memory
import envi.qt.memcanvas as e_q_memcanvas
import vivisect.tools.graphutil as viv_graph
import vivisect.symboliks.common as viv_sym_common
import vivisect.symboliks.effects as viv_sym_effects
import vivisect.symboliks.analysis as viv_sym_analysis
import vivisect.symboliks.expression as viv_sym_expression

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from vqt.main import *
from vqt.basics import *
from vivisect.const import *


class VivSymbolikPathsModel(vq_tree.VQTreeModel):
    columns = ('Path', 'Effect Count')


class VivSymbolikPathsView(vq_tree.VQTreeView):

    pathSelected = QtCore.pyqtSignal(object, object)

    def __init__(self, vw, parent=None):
        vq_tree.VQTreeView.__init__(self, parent=parent)
        self.setModel(VivSymbolikPathsModel(parent=self))

    def loadSymbolikPaths(self, paths):
        cnt = 0
        model = VivSymbolikPathsModel(parent=self)
        for i, (emu, effects) in enumerate(paths):
            model.append((str(i), len(effects), emu, effects))
            cnt += 1
        self.setModel(model)
        return cnt

    def selectionChanged(self, selected, unselected):

        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            rowdata = index.internalPointer().rowdata
            emu = rowdata[-2]
            path = rowdata[-1]
            self.pathSelected.emit(emu, path)


class VivSymbolikFuncPane(e_q_memory.EnviNavMixin, vq_save.SaveableWidget, QWidget):

    viewidx = itertools.count()

    def __init__(self, vw, parent=None):
        self.vw = vw
        self.fva = None
        self.vwgui = vw.getVivGui()

        self.curemu = None
        self.cureffects = None

        self.symctx = viv_sym_analysis.getSymbolikAnalysisContext(vw, consolve=True)
        self.symexpr = viv_sym_expression.SymbolikExpressionParser(defwidth=vw.psize)

        if self.symctx is None:
            raise Exception('No Symboliks For: %s (yet)' % vw.getMeta('Architecture'))

        QWidget.__init__(self, parent=parent)
        e_q_memory.EnviNavMixin.__init__(self)
        self.setEnviNavName('Symboliks%d' % next(self.viewidx))

        self.exprtext = QLineEdit(parent=self)
        self.constraintext = QLineEdit(parent=self)
        self.alleffs = QCheckBox('all effects', parent=self)
        self.alleffs.stateChanged.connect(self.rendSymbolikPath)

        self.loop_count = QSpinBox(parent=self)
        looplabel = QLabel("Max Loops:", parent=self)

        self.pathview = VivSymbolikPathsView(vw, parent=self)
        self.pathview.setFixedHeight(100)
        self.memcanvas = e_q_memcanvas.VQMemoryCanvas(vw, syms=vw, parent=self)

        self.pathview.pathSelected.connect(self.symPathSelected)
        self.exprtext.returnPressed.connect(self.renderSymbolikPaths)
        self.constraintext.returnPressed.connect(self.renderSymbolikPaths)

        fvalabel = QLabel("Function VA:", parent=self)
        inccblabel = QLabel("Must Include VA:", parent=self)
        navbox = HBox(fvalabel, self.exprtext, inccblabel, self.constraintext, looplabel, self.loop_count, self.alleffs)

        mainbox = VBox()
        mainbox.addLayout(navbox)
        mainbox.addWidget(self.pathview)
        mainbox.addWidget(self.memcanvas)
        self.setLayout(mainbox)
        self.updateWindowTitle()

    def updateWindowTitle(self):
        ename = self.getEnviNavName()
        expr = str(self.exprtext.text())
        self.setWindowTitle('%s: %s' % (ename, expr))

    def enviNavGoto(self, expr, sizeexpr=None):
        self.exprtext.setText(expr)
        self.renderSymbolikPaths()
        self.updateWindowTitle()

    def vqGetSaveState(self):
        return {'expr': str(self.exprtext.text())}

    def vqSetSaveState(self, state):
        self.exprtext.setText(state.get('expr', ''))
        self.renderSymbolikPaths()

    def renderSymbolikPaths(self):
        try:

            self.memcanvas.clearCanvas()
            exprtxt = str(self.exprtext.text())
            if not exprtxt:
                return

            exprparts = exprtxt.split(';')
            expr = exprparts[0]

            preeff = []
            precons = []
            for e in exprparts[1:]:
                s = self.symexpr.parseExpression(e)

                if isinstance(s, viv_sym_common.Constraint):
                    precons.append(s)
                    continue

                if isinstance(s, viv_sym_effects.SymbolikEffect):
                    preeff.append(s)
                    continue

                raise Exception('Unhandled Symbolik Expression: %s' % e)

            self.symctx.setSymPreEffects(preeff)
            self.symctx.setSymPreConstraints(precons)

            va = self.vw.parseExpression(expr)
            self.fva = self.vw.getFunction(va)
            if self.fva is None:
                raise Exception('QTSymboliks: Invalid Address: 0x%.8x' % va)

            # check the constraints
            # FIXME: add ability to page through more than just the first 100 paths.  requires 
            #   storing the codegraph and codepaths
            codepaths = None
            codegraph = self.symctx.getSymbolikGraph(self.fva)
            cexpr = str(self.constraintext.text())
            if cexpr:
                cva = self.vw.parseExpression(cexpr)
                ccb = self.vw.getCodeBlock(cva)

                if ccb is not None and ccb in self.vw.getFunctionBlocks(self.fva):
                    loopcnt = self.loop_count.value()
                    codepaths = viv_graph.getCodePathsThru(codegraph, ccb[0], loopcnt=loopcnt)
                    paths = self.symctx.getSymbolikPaths(self.fva, paths=codepaths, graph=codegraph, maxpath=100)

            if codepaths is None:
                loopcnt = self.loop_count.value()
                paths = self.symctx.walkSymbolikPaths(self.fva, maxpath=100, loopcnt=loopcnt)

            if not self.pathview.loadSymbolikPaths(paths):
                self.memcanvas.addText('No valid symbolik paths found for %s' % expr)

        except Exception as e:
            self.memcanvas.addText('ERROR: %s' % e)
            self.memcanvas.addText(traceback.format_exception(*sys.exc_info()))

    def addVivNames(self, path, symobj, ctx):
        emu, symctx = ctx

        width = emu.__width__ # FIXME factory thing?

        if isinstance(symobj, viv_sym_common.Const):
            loc = self.vw.getLocation(symobj.value)
            if loc and loc[2] == LOC_STRING:
                s = repr(self.vw.readMemory(loc[0], loc[1]))
                s = '"%s"' % s[1:-1]
                return viv_sym_common.Var(s, width)

            if emu.isLocalMemory(symobj):
                offset = emu.getLocalOffset(symobj)
                # ltype,lname = self.vw.getFunctionLocal( self.fva, offset )
                flocal = self.vw.getFunctionLocal(self.fva, offset)
                if flocal is None:
                    flocal = ('int', 'local%d' % abs(offset))

                ltype, lname = flocal
                symobj.ptrname = lname

                return symobj

            if loc and loc[2] == LOC_UNI:
                buf = self.vw.readMemory(loc[0], loc[1])
                return viv_sym_common.Var('L"%s"' % buf.decode('utf-16le', 'ignore'), width)

            name = self.vw.getName(symobj.value)
            if name is not None:
                symobj = viv_sym_common.Var(name, width)

        return symobj

    def symPathSelected(self, emu, effects):
        self.curemu = emu
        self.cureffects = effects
        try:
            self.rendSymbolikPath()
        except Exception as e:
            import sys
            sys.excepthook(*sys.exc_info())

    def rendSymbolikPath(self, *args, **kwargs):
        '''
        Render the events from the currently selected emu/events.
        NOTE: args/kwargs syntax to allow arbitrary slot use
        '''
        emu = self.curemu
        effects = self.cureffects

        alleff = self.alleffs.checkState() == QtCore.Qt.Checked

        self.memcanvas.clearCanvas()
        colormap = {}
        for effect in effects:

            colormap[effect.va] = 'yellow'

            effect.reduce(emu)

            if alleff:
                effect.walkTree(self.addVivNames, ctx=(emu, self.symctx))
                self.memcanvas.addVaText('0x%.8x: ' % effect.va, effect.va)
                effect.render(self.memcanvas, vw=self.vw)
                self.memcanvas.addText('\n')
                continue

            if effect.efftype in (EFFTYPE_CONSTRAIN, EFFTYPE_CALLFUNC):
                effect.walkTree(self.addVivNames, ctx=(emu, self.symctx))
                self.memcanvas.addVaText('0x%.8x: ' % effect.va, effect.va)
                effect.render(self.memcanvas, vw=self.vw)
                self.memcanvas.addText( '\n' )
                continue

            if effect.efftype == EFFTYPE_WRITEMEM:
                if not emu.isLocalMemory(effect.symaddr):
                    effect.walkTree(self.addVivNames, ctx=(emu, self.symctx))
                    self.memcanvas.addVaText('0x%.8x: ' % effect.va, effect.va)
                    effect.render(self.memcanvas, vw=self.vw)
                    self.memcanvas.addText('\n')
                continue

        vqtevent('viv:colormap', colormap)

        retsym = emu.getFunctionReturn()
        retsym = retsym.reduce()

        self.memcanvas.addText('RETURNS: %s\n' % retsym)
