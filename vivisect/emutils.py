import envi
import envi.memory as e_mem


class WorkspaceMemoryObject(e_mem.MemoryObject):

    def __init__(self, vw, maps, nosegfault=False):
        self.vw = vw
        self.nosegfault = nosegfault
        e_mem.MemoryObject.__init__(self, maps)

    # FIXME make this copy on write from the workspace

    def readMemory(self, va, size):
        if self.checkMemory(va):
            return e_mem.MemoryObject.readMemory(self, va, size)
        if self.vw.getSegment(va) is not None:
            return self.vw.readMemory(va, size)
        # We don't have it
        if self.nosegfault:
            return "A" * size
        raise envi.SegmentationViolation(va)
