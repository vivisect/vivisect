'''
A unified context menu builder for all address context clicks.
'''
from PyQt5.QtWidgets import QMenu

import envi
import envi.bits as e_bits
import envi.qt.memcanvas as e_q_memcanvas
import vivisect.analysis.generic.codeblocks as vagc

from vqt.common import *
from envi.threads import *
from vivisect.const import *


@firethread
def printEmuState(vw, fva, va):
    vw.vprint('Running emulator to: 0x%.8x' % (va,))
    emu = vw.getEmulator()

    stack = emu.getStackCounter()
    emu.runFunction(fva, stopva=va, maxhit=2)
    dstack = emu.getStackCounter() - stack

    vw.vprint("Showing Register/Magic State At: 0x%.8x" % va)
    vw.vprint('Stack Delta: %d' % dstack)

    # FIXME: this may not be as flexible as it could be, as we don't necessarily *have* to have a location...
    # though we certainly should.
    loc = vw.getLocation(va)
    if loc is None:
        vw.vprint("ARG! can't find location info for 0x%x" % va)
        return

    lva, lsz, ltype, tinfo = loc
    op = vw.parseOpcode(va, arch=tinfo)
    vw.canvas.addVaText("0x%.8x: " % va, va)
    op.render(vw.canvas)
    vw.canvas.addText("\n")
    for i in range(len(op.opers)):
        o = op.opers[i]
        o.render(vw.canvas, op, i)
        oaddr = o.getOperAddr(op, emu)
        if oaddr is not None:
            vw.canvas.addText(' [ 0x%x ] ' % oaddr)

        vw.canvas.addText(" = ")
        oval = o.getOperValue(op, emu)
        taint = emu.getVivTaint(oval)
        base = "0x%.8x (%d)" % (oval, oval)
        if taint is not None:
            base += '%s + %d' % (emu.reprVivTaint(taint), oval - taint[0])

        vw.vprint(base)

def buildContextMenu(vw, va=None, expr=None, menu=None, parent=None, nav=None):
    '''
    Return (optionally construct) a menu to use for handling a context click
    at the given virtual address or envi expression.

    Arguments:
    va      - virtual address of the context click
    expr    - expression to parse instead of va
    menu    - existing menu to add items to
    parent  - Qt parent
    nav     - the "local" EnviNavMixin instance
    '''
    if va is None:
        va = vw.parseExpression(expr)

    if expr is None:
        expr = '0x%.8x' % va

    if menu is None:
        menu = QMenu(parent=parent)

    menu.addAction('rename (n)', ACT(vw.getVivGui().setVaName, va))
    menu.addAction('comment (;)', ACT(vw.getVivGui().setVaComment, va))
    menu.addAction('print location', ACT(vw.getVivGui().getLocation, va))

    refsto = vw.getXrefsTo(va)
    refsfrom = vw.getXrefsFrom(va)

    if refsto:
        rtomenu = menu.addMenu('xrefs to')
        for fromva, tova, xrtype, xrflag in refsto:
            xloc = vw.getLocation(fromva)
            xexpr = '0x%.8x' % fromva
            xrepr = '0x%.8x: %s' % (fromva, vw.reprLocation(xloc))
            xfva = vw.getFunction(fromva)
            if xfva is not None:
                xrepr = '%s (%s)' % (xrepr, vw.getName(xfva))
            xmenu = rtomenu.addMenu(xrepr)
            if nav:
                xmenu.addAction('(this window)', ACT(nav.enviNavGoto, xexpr))
            e_q_memcanvas.initMemSendtoMenu(xexpr, xmenu)

    if refsfrom:
        rfrmenu = menu.addMenu('xrefs from')
        for fromva, tova, xrtype, xrflag in refsfrom:
            xloc = vw.getLocation(tova)
            xexpr = '0x%.8x' % tova
            xrepr = '0x%.8x: %s' % (tova, vw.reprLocation(xloc))
            xfva = vw.getFunction(tova)
            if xfva is not None:
                xrepr = '%s (%s)' % (xrepr, vw.getName(xfva))
            xmenu = rfrmenu.addMenu(xrepr)
            if nav:
                xmenu.addAction('(this window)', ACT(nav.enviNavGoto, xexpr))
            e_q_memcanvas.initMemSendtoMenu(xexpr, xmenu)

    fva = vw.getFunction(va)
    if fva is not None:
        funcmenu = menu.addMenu('function')
        funcname = vw.getName(fva)
        if nav:
            funcmenu.addAction(funcname[:80], ACT(nav.enviNavGoto, funcname))

        rtype, rname, cconv, cname, cargs = vw.getFunctionApi(fva)
        if cargs:
            argmenu = funcmenu.addMenu('args')
            for i, (atype, aname) in enumerate(cargs):
                act = ACT(vw.getVivGui().setFuncArgName, fva, i, atype, aname)
                argmenu.addAction(aname, act)

        funclocals = vw.getFunctionLocals(fva)
        if funclocals:
            funclocals.sort()
            funclocals.reverse()

            locmenu = funcmenu.addMenu('locals')

            for _, spdelta, ltype, linfo in funclocals:
                if spdelta > 0: # FIXME perhaps make this flexable based on cconv?
                    continue

                # Make the workspace do the resolving for us
                typename, varname = vw.getFunctionLocal(fva,spdelta)
                act = ACT(vw.getVivGui().setFuncLocalName, fva, spdelta, typename, varname)
                locmenu.addAction(varname, act)

        if fva != va:
            funcmenu.addAction('show emulator state', ACT(printEmuState, vw, fva, va))

        funcmenu.addAction('call graph', ACT(vw.getVivGui().showFuncCallGraph, fva))
        funcmenu.addAction('re-analyze codeblocks', ACT(vagc.analyzeFunction, vw, fva))
        if fva == va:
            # funcmenu.addAction('delete function', ACT(vw.delFunction, va))
            funcmenu.addAction('delete function', ACT(vw.getVivGui().delFunction, va))

    loc = vw.getLocation(va)
    if loc is None:
        makemenu = menu.addMenu('make')
        makemenu.addAction('code (c)', ACT(vw.makeCode, va))
        makemenu.addAction('function (f)', ACT(vw.makeFunction, va))
        makemenu.addAction('string (s)', ACT(vw.makeString,  va))
        makemenu.addAction('pointer (p)', ACT(vw.makePointer, va))
        makemenu.addAction('unicode (u)', ACT(vw.makeUnicode, va))
        makemenu.addAction('structure (S)', ACT(vw.getVivGui().makeStruct, va))

        nummenu = makemenu.addMenu('number')
        for size in (1, 2, 4, 8):
            nummenu.addAction("%d-bit (%d bytes)" % (size << 3, size), ACT(vw.makeNumber, va, size=size))

        archmenu = makemenu.addMenu('code (archs)')
        prevumenu = menu.addMenu('preview instruction')

        archs = [ (archname,archid) for (archid,archname) in envi.arch_names.items() ]
        archs.sort()
        for archname,archid in archs:
            if archname == 'default':
                continue
            archmenu.addAction(archname, ACT(vw.makeCode, va, arch=archid))
            prevumenu.addAction(archname, ACT(vw.previewCode, va, arch=archid))

    else:

        if loc[L_LTYPE] == LOC_OP:

            op = vw.parseOpcode(va, arch=loc[L_TINFO])
            for idx,oper in enumerate(op.opers):
                # Give the option to switch ('hint') that you want
                # the immediate operand displayed differently...
                if oper.isImmed():
                    val = oper.getOperValue(op)
                    hval = e_bits.hex(val)

                    cval = val
                    r = []
                    while cval:
                        r.append(chr(cval & 0xff))
                        cval = cval >> 8
                    cstr = repr(''.join(r))

                    immmenu = menu.addMenu('immediate')
                    # FIXME struct offsets?
                    immmenu.addAction('decimal (%d)' % val, ACT(vw.setSymHint, va, idx, str(val)))
                    immmenu.addAction('hex (%s)' % hval,    ACT(vw.setSymHint, va, idx, hval))
                    immmenu.addAction('chars (%s)' % cstr,  ACT(vw.setSymHint, va, idx, cstr))

                    names = vw.vsconsts.revLookup(val)
                    if names is not None:
                        for name in names:
                            immmenu.addAction(name, ACT(vw.setSymHint, va, idx, name))
            menu.addAction('make code xref->', ACT(vw.getVivGui().addVaXref, va))

        menu.addAction('bookmark (B)',   ACT(vw.getVivGui().addBookmark, va))
        menu.addAction('undefine (U)',   ACT(vw.delLocation, va))

    e_q_memcanvas.initMemSendtoMenu(expr, menu)

    # give any extensions a chance to play
    for extname, exthook in vw._ext_ctxmenu_hooks.items():
        logger.info('exthook: %r', exthook)
        exthook(vw, va, expr, menu, parent, nav)

    return menu
