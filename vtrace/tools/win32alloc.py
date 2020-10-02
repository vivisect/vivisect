'''
A module with some cute toys for monitoring allocations.
'''

import vtrace

import envi.archs.i386 as e_i386


class ReturnBreak(vtrace.Breakpoint):
    def __init__(self, addr, chsize, chflags):
        vtrace.Breakpoint.__init__(self, addr)
        self.fastbreak = True
        self._chsize = chsize
        self._chflags = chflags

    def notify(self, event, trace):
        eax = trace.getRegister(e_i386.REG_EAX)
        a = trace.getMeta('HeapAllocs')
        a.append((self.address, eax, self._chsize, self._chflags))
        trace.runAgain()


class RtlAllocateHeapBreak(vtrace.Breakpoint):

    def __init__(self, addr):
        vtrace.Breakpoint.__init__(self, addr)
        self.fastbreak = True

    def notify(self, event, trace):

        sp = trace.getStackCounter()
        (saved_eip,
         heap,
         flags,
         size) = trace.readMemoryFormat(sp, '<4P')

        if trace.getBreakpointByAddr(saved_eip) is None:
            bp = ReturnBreak(saved_eip, size, flags)
            trace.addBreakpoint(bp)

        trace.runAgain()


def watchHeapAllocs(trace):
    '''
    Add a breakpoint to ntdll.RtlAllocateHeap to watch for
    allocations and track who made them...
    '''
    clearHeapAllocs(trace)
    addr = trace.parseExpression('ntdll.RtlAllocateHeap')
    bp = RtlAllocateHeapBreak(addr)
    trace.addBreakpoint(bp)


def clearHeapAllocs(trace):
    trace.setMeta('HeapAllocs', [])


def getHeapAllocs(trace):
    '''
    Return a list of (caller_eip, heap_chunk, size, flags) tuples
    '''
    return trace.getMeta('HeapAllocs', [])
