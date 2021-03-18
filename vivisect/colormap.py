import vivisect.exc as viv_exc


class VivColorMap:
    '''
    An easier to use color map object.
    '''

    def __init__(self, vw):
        self.vw = vw
        self.cmap = {}

    def colorVa(self, va, color):
        '''
        Set the color for a particular virtual memory location
        when viewed with this color map.

        Example: m.colorVa(va, 'red')
        '''
        self.cmap[va] = color

    def colorBlock(self, va, color):
        '''
        Similar to colorVa(), but loops coloring all the virtual
        addresses in the given block.
        '''
        cbtup = self.vw.getCodeBlock(va)
        if cbtup is None:
            raise viv_exc.InvalidCodeBlock(va)

        cbva, cbsize, fva = cbtup
        for i in range(cbsize):
            self.cmap[cbva + i] = color

    def colorFunction(self, fva, color):
        '''
        Similar to colorVa(), but loops coloring all the virtual
        addresses in the given function.
        '''
        fva = self.vw.getFunction(fva)
        for cbva, cbsize, fva in self.vw.getFunctionBlocks(fva):
            for i in range(cbsize):
                self.cmap[cbva + i] = color

    def saveAs(self, name):
        '''
        Save the color map to the workspace with the given name.
        '''
        self.vw.addColorMap(name, dict(self.cmap))

    def setGuiMap(self):
        '''
        Set this as the display color map for the vivisect gui.  (obviously
        only works when GUI is running...)
        '''
        self.vw._viv_gui.setColorMap(self.cmap)

    def getColorDict(self):
        return dict(self.cmap)
