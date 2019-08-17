'''
The envi.memcanvas module is the home of the base MemoryRenderer object and
MemoryCanvas objects.
'''

import sys
import traceback

import envi
import envi.memory as e_mem
import envi.symstore.resolver as e_resolv

class MemoryRenderer(object):
    """
    A top level object for all memory renderers
    """

    def rendSymbol(self, mcanv, va):
        """
        If there is a symbolic name for the current va, print it...
        """
        sym = mcanv.syms.getSymByAddr(va)
        if sym != None:
            mcanv.addVaText("%s:\n" % repr(sym), va)

    def rendVa(self, mcanv, va):
        tag = mcanv.getVaTag(va)
        mcanv.addText("%.8x:" % va, tag=tag)

    def rendChars(self, mcanv, bytez):
        for b in bytez:
            val = ord(b)
            bstr = "%.2x" % val
            if val < 0x20 or val > 0x7e:
                b = "."
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
        canvas recieves user input which desires nav...
        '''
        self._canv_navcallback = callback

    def getEndian(self):
        '''
        returns the endianness setting of the mem object
        '''
        return self.mem.getEndian()

    def setEndian(self, bigend):
        '''
        envi.ENDIAN_LSB or envi.ENDIAN_MSB
        passes the value to the mem.setEndian() accessor
        '''
        self.mem.setEndian(bigend)

    def addRenderer(self, name, rend):
        self.renderers[name] = rend
        self.currend = rend

    def getRenderer(self, name):
        return self.renderers.get(name)

    def getRendererNames(self):
        ret = self.renderers.keys()
        ret.sort()
        return ret

    def setRenderer(self, name):
        rend = self.renderers.get(name)
        if rend == None:
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
        return None # No highlighting in plain text

    def getVaTag(self, va):
        """
        Retrieve a tag object suitable for showing that the text
        added with this tag should link through to the specified
        virtual address in the memory canvas.
        """
        return None # No linking in plain text

    def addText(self, text, tag=None):
        """
        Add text to the canvas with a specified tag.

        NOTE: Implementors should probably check _canv_scrolled to
        decide if they should scroll to the end of the view...
        """
        if sys.stdout.encoding:
            text = text.encode(sys.stdout.encoding, 'replace')
        sys.stdout.write(text)

    def addNameText(self, text, name=None, typename='name'):
        if name == None:
            name = text.encode('hex')
        tag = self.getNameTag(name, typename=typename)
        self.addText(text, tag=tag)

    def addVaText(self, text, va):
        tag = self.getVaTag(va)
        self.addText(text, tag=tag)

    def render(self, va, size, rend=None):
        raise Exception('Depricated!  use renderMemory!')

    def clearCanvas(self):
        pass

    def _beginRenderMemory(self, va, size, rend):
        pass

    def _endRenderMemory(self, va, size, rend):
        pass

    def _beginRenderVa(self, va):
        pass

    def _endRenderVa(self, va):
        pass

    def _beginUpdateVas(self, valist):
        raise Exception('Default canvas cant update!')

    def _endUpdateVas(self):
        pass

    def _beginRenderAppend(self):
        raise Exception('Default canvas cant append!')

    def _endRenderAppend(self):
        pass

    def _beginRenderPrepend(self):
        raise Exception('Default canvas cant prepend!')

    def _endRenderPrepend(self):
        pass

    def _isRendered(self, va, maxva):
        '''
        Returns true if any part of the current render overlaps
        with the specified region.
        '''
        if self._canv_beginva == None:
            return False

        if self._canv_endva == None:
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

    def renderMemoryUpdate(self, va, size):
        #print "renderMemoryUpdate(0x%x, 0x%x)" % (va, size)

        maxva = va + size
        if not self._isRendered(va, maxva):
            return

        # Find the index of the first and last change
        iend = None
        ibegin = None
        for i,(rendva,rendsize) in enumerate(self._canv_rendvas):

            if ibegin == None and va <= rendva:
                ibegin = i

            if iend == None and maxva <= rendva:
                iend = i

            if ibegin != None and iend != None:
                break

        #if ibegin == None or iend == None:
            #print " ibegin or iend == None.  we need more va's in _canv_rendvas?"

        saved_last  = self._canv_rendvas[iend:]
        saved_first = self._canv_rendvas[:ibegin]
        updatedvas  = self._canv_rendvas[ibegin:iend]
        # print 'IBEGIN',hex(ibegin)
        # print 'IEND',hex(iend)
        # print 'FIRST',repr([hex(va) for va in saved_first])
        # print 'UPDATED',repr([hex(va) for va in updatedvas])
        # print 'LAST',repr([hex(va) for va in saved_last])

        # We must actually start rendering from the beginning
        # of the first updated VA index
        #if startva
        if not len(updatedvas):
            print "returning because no updatedvas: %x/%x" % (va, size)
            return self.renderMemory(va, size)

        startva = updatedvas[0][0]
        endva = self._canv_endva
        if saved_last:
            endva = saved_last[0][0]

        newrendvas = []

        self._beginUpdateVas(updatedvas)
        try:

            while startva < endva:
                self._beginRenderVa(startva)
                rsize = self.currend.render(self, startva)
                newrendvas.append((startva,rsize))
                self._endRenderVa(startva)
                startva += rsize

        except Exception as e:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va),s))

        self._canv_rendvas = saved_first + newrendvas + saved_last

        self._endUpdateVas()

    def renderMemoryPrepend(self, size):
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
                self._canv_rendvas.append((va,rsize))
                self._endRenderVa(va)
                va += rsize

            self._canv_rendvas.extend(savedrendvas)

        except Exception as e:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va),s))

        self._endRenderPrepend()

    def renderMemoryAppend(self, size):
        lastva, lastsize = self._canv_rendvas[-1]

        va = lastva + lastsize

        self._beginRenderAppend()

        rend = self.currend
        try:
            maxva = va + size
            while va < maxva:
                self._beginRenderVa(va)
                rsize = rend.render(self, va)
                self._canv_rendvas.append((va,rsize))
                self._endRenderVa(va)
                va += rsize

            self._canv_endva = maxva

        except Exception as e:
            s = traceback.format_exc()
            self.addText("\nException At %s: %s\n" % (hex(va),s))

        self._endRenderAppend()

    def renderMemory(self, va, size, rend=None):

        # if this is not a "scrolled" canvas, clear it.
        if not self._canv_scrolled:
            self.clearCanvas()

        if rend == None:
            rend = self.currend

        self.currend = rend

        # Set our canvas render tracking variables.
        self._canv_beginva = va
        self._canv_endva = va + size
        self._canv_rendvas = []

        # A callback for "bulk" rendering (let the canvas cache...)
        self._beginRenderMemory(va, size, rend)
        try:
            maxva = va + size
            while va < maxva:

                self._beginRenderVa(va)
                try:
                    rsize = rend.render(self, va)
                    self._canv_rendvas.append((va,rsize))
                    self._endRenderVa(va)
                    va += rsize
                except Exception as e:
                    traceback.print_exc()
                    self.addText("\nRender Exception At %s: %s\n" % (hex(va),e))
                    self._endRenderVa(va)
                    break

        except Exception as e:
            self.addText("\nException At %s: %s\n" % (hex(va),e))

        # Canvas callback for render completion (or error...)
        self._endRenderMemory(va, size, rend)

class StringMemoryCanvas(MemoryCanvas):

    def __init__(self, mem, syms=None):
        MemoryCanvas.__init__(self, mem, syms=syms)
        self.strval = ''

        # we perform manual clearing of the canvas.
        # we don't want it cleared every renderMemory call.
        self.setScrolledCanvas(True)

    def clearCanvas(self):
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
