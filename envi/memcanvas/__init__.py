'''
The envi.memcanvas module is the home of the base MemoryRenderer object and
MemoryCanvas objects.
'''

import sys
import logging
import functools
import traceback

import envi.symstore.resolver as e_resolv

logger = logging.getLogger(__name__)

class MemoryRenderer(object):
    """
    A top level object for all memory renderers
    """

    def rendSymbol(self, mcanv, va):
        """
        If there is a symbolic name for the current va, print it...
        """
        sym = mcanv.syms.getSymByAddr(va)
        if sym is not None:
            mcanv.addVaText("%s:\n" % repr(sym), va)

    def rendVa(self, mcanv, va):
        tag = mcanv.getVaTag(va)
        mcanv.addText("%.8x:" % va, tag=tag)

    def rendChars(self, mcanv, bytez):
        for b in bytez:
            bstr = "%.2x" % b
            if b < 0x20 or b > 0x7e:
                b = "."
            else:
                b = chr(b)
            mcanv.addNameText(b, bstr)

    def render(self, mcanv, va):
        """
        Render one "unit" and return the size you ate.
        mcanv will be a MemoryCanvas extender and va
        is the virtual address you are expected to render.
        """
        raise Exception("Implement render!")


class MemoryCanvas(object):
    """
    A memory canvas is a place where the textual representation
    of memory will be displayed. The methods implemented here show
    how a memory canvas which simply prints would be implemented.
    """
    def __init__(self, mem=None, syms=None):
        if mem is None:
            raise Exception("MemoryCanvas must include mem args")
        if syms is None:
            syms = e_resolv.SymbolResolver()
        self.mem = mem
        self.syms = syms
        self.currend = None
        self.renderers = {}
        self._canv_scrolled = False
        self._canv_navcallback = None

        # A few things for tracking renders.
        self._canv_beginva = None
        self._canv_endva = None
        self._canv_rendvas = []

    def setScrolledCanvas(self, scroll):
        self._canv_scrolled = scroll

    def write(self, msg):
        # So a canvas can act like simple standard out
        self.addText(msg)

    def setNavCallback(self, callback):
        '''
        Set a navigation "callback" that will be called with
        a memory expression as it's first argument anytime the
        canvas receives user input which desires nav...
        '''
        self._canv_navcallback = callback

    def addRenderer(self, name, rend):
        self.renderers[name] = rend
        self.currend = rend

    def getRenderer(self, name):
        return self.renderers.get(name)

    def getRendererNames(self):
        ret = list(self.renderers.keys())
        ret.sort()
        return ret

    def setRenderer(self, name):
        rend = self.renderers.get(name)
        if rend is None:
            raise Exception("Unknown renderer: %s" % name)
        self.currend = rend

    def getTag(self, typename):
        """
        Retrieve a non-named tag (doesn't highlight or do
        anything particularly special, but allows color
        by typename).
        """
        return None

    def getNameTag(self, name, typename='name'):
        """
        Retrieve a "tag" object for a name.  "Name" tags will
        (if possible) be highlighted in the rendered interface
        """
        return None  # No highlighting in plain text

    def getVaTag(self, va):
        """
        Retrieve a tag object suitable for showing that the text
        added with this tag should link through to the specified
        virtual address in the memory canvas.
        """
        return None  # No linking in plain text

    def addText(self, text, tag=None):
        """
        Add text to the canvas with a specified tag.

        NOTE: Implementors should probably check _canv_scrolled to
        decide if they should scroll to the end of the view...
        """
        sys.stdout.write(text)

    def addNameText(self, text, name=None, typename='name'):
        if name is None:
            name = bytes([ord(x) for x in text])
        else:
            name = bytes([ord(x) for x in name])
        tag = self.getNameTag(name, typename=typename)
        self.addText(text, tag=tag)

    def addVaText(self, text, va):
        tag = self.getVaTag(va)
        self.addText(text, tag=tag)

    def render(self, va, size, rend=None):
        raise Exception('Deprecated!  use renderMemory!')

    def clearCanvas(self, cb=None):
        if cb is not None:
            cb(None)

    def _beginRenderMemory(self, va, size, rend):
        pass

    def _endRenderMemory(self, va, size, rend, cb=None):
        if cb is not None:
            cb(None)

    def _beginRenderVa(self, va):
        pass

    def _endRenderVa(self, va):
        pass

    def _beginUpdateVas(self, valist):
        raise Exception("Default canvas can't update!")

    def _endUpdateVas(self):
        pass

    def _beginRenderAppend(self):
        raise Exception("Default canvas can't append!")

    def _endRenderAppend(self):
        pass

    def _beginRenderPrepend(self):
        raise Exception("Default canvas can't prepend!")

    def _endRenderPrepend(self):
        pass

    def _isRendered(self, va, maxva):
        '''
        Returns true if any part of the current render overlaps
        with the specified region.
        '''
        if self._canv_beginva is None:
            return False

        if self._canv_endva is None:
            return False

        if va > self._canv_endva:
            return False

        if maxva < self._canv_beginva:
            return False

        return True

    def _loc_helper(self, va):
        '''
        allows subclassess to make the starting VA make more contextual sense.
        '''
        return (va, 0)

    def renderMemoryUpdate(self, va, size, init=None, fini=None):

        maxva = va + size
        if not self._isRendered(va, maxva):
            return

        # Find the index of the first and last change
        iend = None
        ibegin = None
        for i, (rendva, rendsize) in enumerate(self._canv_rendvas):

            if ibegin is None and va <= rendva:
                ibegin = i

            if iend is None and maxva <= rendva:
                iend = i

            if ibegin is not None and iend is not None:
                break

        saved_last = self._canv_rendvas[iend:]
        saved_first = self._canv_rendvas[:ibegin]
        updatedvas = self._canv_rendvas[ibegin:iend]

        # We must actually start rendering from the beginning
        # of the first updated VA index
        startva = updatedvas[0][0]
        endva = self._canv_endva
        if saved_last:
            endva = saved_last[0][0]

        newrendvas = []

        self._beginUpdateVas(updatedvas, init)
        try:

            while startva < endva:
                self._beginRenderVa(startva)
                rsize = self.currend.render(self, startva)
                newrendvas.append((startva, rsize))
                self._endRenderVa(startva)
                startva += rsize

        except Exception:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va), s))

        self._canv_rendvas = saved_first + newrendvas + saved_last

        self._endUpdateVas(fini)

    def renderMemoryPrepend(self, size, cb=None):
        firstva, firstsize = self._canv_rendvas[0]

        va, szdiff = self._loc_helper(firstva - size)
        size += szdiff

        self._beginRenderPrepend()

        savedrendvas = self._canv_rendvas
        self._canv_rendvas = []
        self._canv_beginva = va

        rend = self.currend

        try:

            while va < firstva:
                self._beginRenderVa(va)
                rsize = rend.render(self, va)
                self._canv_rendvas.append((va, rsize))
                self._endRenderVa(va)
                va += rsize

            self._canv_rendvas.extend(savedrendvas)

        except Exception:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va), s))

        self._endRenderPrepend(cb)

    def renderMemoryAppend(self, size, cb=None):
        lastva, lastsize = self._canv_rendvas[-1]

        va = lastva + lastsize

        self._beginRenderAppend()

        rend = self.currend
        try:
            maxva = va + size
            while va < maxva:
                self._beginRenderVa(va)
                rsize = rend.render(self, va)
                self._canv_rendvas.append((va, rsize))
                self._endRenderVa(va)
                va += rsize

            self._canv_endva = maxva

        except Exception:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va), s))

        self._endRenderAppend(cb)

    def _canvasCleared(self, cb, data):
        va = self._canv_beginva
        maxva = self._canv_endva
        size = maxva - va
        rend = self.currend
        # A callback for "bulk" rendering (let the canvas cache...)
        self._beginRenderMemory(va, size, rend)
        try:
            maxva = va + size
            while va < maxva:

                self._beginRenderVa(va)
                try:
                    rsize = rend.render(self, va)
                    self._canv_rendvas.append((va, rsize))
                    self._endRenderVa(va)
                    va += rsize
                except Exception as e:
                    logger.error(traceback.format_exc())
                    self.addText("\nRender Exception At %s: %s\n" % (hex(va), str(e)))
                    self._endRenderVa(va)
                    break

        except Exception as e:
            self.addText("\nException At %s: %s\n" % (hex(va), str(e)))

        # Canvas callback for render completion (or error...)
        self._endRenderMemory(va, size, rend, cb)

    def renderMemory(self, va, size, rend=None, cb=None):
        # Set our canvas render tracking variables.
        self._canv_beginva = va
        self._canv_endva = va + size
        self._canv_rendvas = []
        if rend is None:
            rend = self.currend
        self.currend = rend

        clearcb = functools.partial(self._canvasCleared, cb)
        # if this is not a "scrolled" canvas, clear it.
        if not self._canv_scrolled:
            self.clearCanvas(clearcb)
        else:
            clearcb(None)


class StringMemoryCanvas(MemoryCanvas):

    def __init__(self, mem, syms=None):
        MemoryCanvas.__init__(self, mem, syms=syms)
        self.strval = ''

        # we perform manual clearing of the canvas.
        # we don't want it cleared every renderMemory call.
        self.setScrolledCanvas(True)

    def clearCanvas(self, cb=None):
        self.strval = ''

    def addText(self, text, tag=None):
        self.strval += text

    def __str__(self):
        return self.strval


class CanvasMethodProxy(object):
    '''
    Target for teecanvas.
    '''
    def __init__(self, canvases, name):
        self.canvases = canvases
        self.name = name

    def __call__(self, *args, **kwargs):
        for canvas in self.canvases:
            attr = getattr(canvas, self.name)
            attr(*args, **kwargs)


class TeeCanvas(object):
    '''
    Replaces the canvas on an object (temporarily) with a proxy canvas that
    forwards requests to other canvases.

    Example usage:
    with TeeCanvas(self, (self.canvas, canvas2)) as tc:
        self.onecmd(command)
    '''
    def __init__(self, target, canvases):
        self.target = target
        self.ocanvas = None
        self.canvases = canvases

    def __getattr__(self, name):
        return CanvasMethodProxy(self.canvases, name)

    def __enter__(self):
        '''
        replace the canvas of the target with ourselves.
        '''
        self.ocanvas = self.target.canvas
        self.target.canvas = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        restore the canvas of the target.
        '''
        self.target.canvas = self.ocanvas
