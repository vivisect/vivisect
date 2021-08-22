"""
A package for any of the vivisect workspace renderers.
"""
import string
import logging
import urllib.parse

from vivisect.const import *

import vstruct.primitives as vs_prims

import envi.common as e_common
import envi.memcanvas as e_canvas


logger = logging.getLogger(__name__)


class WorkspaceRenderer(e_canvas.MemoryRenderer):
    def __init__(self, vw):
        self.vw = vw

        # Some tweakables...
        self._show_segment = True
        self._show_address = True
        self._show_opbytes = True

    def render(self, mcanv, va):

        loc = self.vw.getLocation(va)
        if loc is None:
            loc = (va, 1, LOC_UNDEF, None)

        lva, lsize, ltype, tinfo = loc

        extra = None
        name = self.vw.getName(lva)
        cmnt = self.vw.getComment(lva)
        func = self.vw.isFunction(lva)

        if ltype == LOC_OP:
            extra = self.vw.parseOpcode(lva, tinfo)

        elif ltype == LOC_STRUCT:
            extra = self.vw.getStructure(lva, tinfo)

        self.renderLocation(mcanv, loc, name, func, cmnt, extra)
        return lsize

    def renderLocation(self, mcanv, loc, name, isfunc, cmnt, extra):
        """
        Actually render a given VA to the given text buffer.

        If there is *any* function to optimize, this is it... it renders EVERYTHING...
        """
        lva, lsize, ltype, tinfo = loc

        vatag = mcanv.getVaTag(lva)
        cmnttag = mcanv.getTag("comment")

        seg = self.vw.getSegment(lva)
        segname = "map" if seg is None else seg[SEG_NAME]

        vastr = self.vw.arch.pointerString(lva)
        linepre = "%s:%s  " % (segname, vastr)

        xrefs = self.vw.getXrefsTo(lva)

        xrcount = len(xrefs)

        if seg is not None and self._show_segment:
            segva, segsize, segname, segfname = seg
            if segva == lva:
                mcanv.addText(linepre, tag=vatag)
                mcanv.addText("Segment: %s (%d bytes) FIXME PERMS\n" % (segname, segsize))

        if isfunc:
            mcanv.addText(linepre, tag=vatag)
            mcanv.addText('\n')

            mcanv.addText(linepre, tag=vatag)
            mcanv.addText("FUNC: ")

            api = self.vw.getFunctionApi(lva)
            rtype, rname, convname, apiname, apiargs = api
            mcanv.addNameText(rtype)
            mcanv.addText(' ')
            mcanv.addNameText(convname)
            mcanv.addText(' ')
            mcanv.addText(name, tag=vatag)

            mcanv.addText("( ")
            for typename, argname in apiargs:
                mcanv.addNameText(typename)
                mcanv.addText(' ')
                mcanv.addNameText(argname)
                mcanv.addText(', ')

            mcanv.addText(")")

            # FIXME color code and get args parsing goin on
            mcanv.addText(" ")
            xrtag = mcanv.getTag("xrefs")
            mcanv.addText("[%d XREFS]\n" % xrcount, tag=xrtag)

            mcanv.addText(linepre, tag=vatag)
            mcanv.addText('\n')

            mcanv.addText(linepre, tag=vatag)

            mcanv.addText('Stack Variables: (offset from initial top of stack)\n')

            funclocals = self.vw.getFunctionLocals(lva)
            funclocals.sort()
            funclocals.reverse()

            for _, spdelta, _, _ in funclocals:
                # Make the workspace do the resolving for us
                typename, varname = self.vw.getFunctionLocal(lva, spdelta)
                mcanv.addText(linepre, tag=vatag)
                mcanv.addText('        ')
                mcanv.addText('%4d: ' % spdelta)
                mcanv.addNameText(typename)
                mcanv.addText(' ')
                mcanv.addNameText(varname)
                mcanv.addText('\n')

            mcanv.addText(linepre, tag=vatag)
            mcanv.addText('\n')

        elif xrcount > 0 or name is not None:
            mcanv.addText(linepre, tag=vatag)
            if name is None:
                name = "loc_%.8x" % lva
            mcanv.addText(urllib.parse.quote_plus(name), tag=vatag)
            mcanv.addText(": ")
            xrtag = mcanv.getTag("xrefs")
            mcanv.addText('[%d XREFS]\n' % xrcount, tag=xrtag)

        if ltype == LOC_OP:
            mcanv.addText(linepre, tag=vatag)
            opbytes = mcanv.mem.readMemory(lva, lsize)
            mcanv.addText(e_common.hexify(opbytes[:8]).ljust(17))

            # extra is the opcode object
            try:
                extra.render(mcanv)
            except Exception as e:
                mcanv.addText("Opcode Render Failed: %s (%s)\n" % (repr(extra), str(e)))

            if cmnt is not None:
                mcanv.addText("    ;%s" % cmnt, tag=cmnttag)

            mcanv.addText("\n")

        elif ltype == LOC_STRUCT:

            for soff, sind, sname, sobj in extra.vsGetPrintInfo():

                sva = lva + soff

                if soff != 0:
                    vastr = self.vw.arch.pointerString(sva)
                    linepre = '%s:%s  ' % (segname, vastr)
                    vatag = mcanv.getVaTag(sva)

                mcanv.addText(linepre, tag=vatag)

                totag = None
                if isinstance(sobj, vs_prims.v_ptr):
                    stova = int(sobj)
                    stoname = self.vw.getName(stova)
                    if stoname is None:
                        stoname = repr(sobj)
                    if self.vw.isValidPointer(stova):
                        totag = mcanv.getVaTag(stova)

                # Insert the field name (and indent)
                mcanv.addText("  "*sind)
                mcanv.addNameText(sname)
                mcanv.addText(": ")

                # Insert the sobj info (if it's a primitive)
                if isinstance(sobj, vs_prims.v_prim):
                    if totag is not None:
                        mcanv.addText(stoname, tag=totag)
                    else:
                        mcanv.addText(repr(sobj))

                if soff != 0:
                    xrefs = self.vw.getXrefsTo(sva)
                    if len(xrefs):
                        xrtag = mcanv.getTag("xrefs")
                        mcanv.addText("[%d XREFS]" % len(xrefs), tag=xrtag)

                # Handle the comment if present
                cmnt = self.vw.getComment(sva)
                if cmnt is not None:
                    mcanv.addText("    ;%s" % cmnt, tag=cmnttag)

                mcanv.addText("\n")

        elif ltype == LOC_POINTER:

            fromva, tova, rtype, rflags = self.vw.getXrefsFrom(lva)[0]  # FIXME hardcoded one

            mcanv.addText(linepre, tag=vatag)
            mcanv.addNameText("ptr: ")

            totag = mcanv.getVaTag(tova)
            pstr = self.vw.arch.pointerString(tova)

            mcanv.addText(pstr, tag=totag)

            name = self.vw.getName(tova)
            if name is None:
                name = "loc_%.8x" % tova  # FIXME 64bit

            mcanv.addText(" (")
            mcanv.addText(name, tag=totag)
            mcanv.addText(")")
            if cmnt is not None:
                mcanv.addText("    ;%s" % cmnt, tag=cmnttag)
            mcanv.addText("\n")

        elif ltype == LOC_UNDEF:

            mcanv.addText(linepre, vatag)
            offset, bytez = self.vw.getByteDef(lva)
            b = bytez[offset:offset+1]
            mcanv.addNameText(b.hex(), typename="undefined")

            try:
                b = b.decode('utf-8')
                if b in string.printable:
                    mcanv.addText('    %s' % repr(b), tag=cmnttag)
            except:
                # if we don't decode correctly, don't print it.
                pass

            if cmnt is not None:
                mcanv.addText('    ;%s' % cmnt, tag=cmnttag)

            mcanv.addText("\n")

        elif ltype == LOC_IMPORT:

            mcanv.addText(linepre, vatag)
            tva = self.vw.vaByName(tinfo)
            mcanv.addText('IMPORT: ')
            if tva is not None:
                mcanv.addVaText(tinfo, tva)
            else:
                mcanv.addText(tinfo)

            if cmnt is not None:
                mcanv.addText("    ;%s" % cmnt, tag=cmnttag)

            mcanv.addText("\n")

        else:
            tagname = loc_type_names.get(ltype, None)
            if tagname is None:
                tagname = "location"

            ltag = mcanv.getTag(tagname)
            cdone = False
            for line in self.vw.reprLocation(loc).split("\n"):
                mcanv.addText(linepre, tag=vatag)
                mcanv.addText(line, ltag)
                if not cdone:
                    cdone = True
                    if cmnt is not None:
                        mcanv.addText("    ;%s" % cmnt, tag=cmnttag)
                mcanv.addText("\n")
