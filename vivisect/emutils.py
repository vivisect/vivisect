import envi.exc as e_exc
import envi.memory as e_mem
import envi.const as e_const


class WorkspaceMemoryObject(e_mem.MemoryObject):
    # TODO: Nobody uses you?

    def __init__(self, vw, maps, nosegfault=False):
        self.vw = vw
        self.nosegfault = nosegfault
        e_mem.MemoryObject.__init__(self, maps)

    # FIXME make this copy on write from the workspace

    # TODO: the super defines readMemory with an _origVa, but this doesn't
    def readMemory(self, va, size):
        # TODO: We should probably just go with MemoryObject's readmemory
        # since that actually handles page boundaries
        if self.probeMemory(va, size, e_const.MM_READ):
            return e_mem.MemoryObject.readMemory(self, va, size)
        if self.vw.getSegment(va) is not None:
            return self.vw.readMemory(va, size)
        # We don't have it
        if self.nosegfault:
            return "A" * size
        raise e_exc.SegmentationViolation(va)
