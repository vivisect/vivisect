'''
The stalker subsystem is a breakpoint based coverage tool
'''

import vtrace

import envi
import envi.memory as e_mem
import envi.codeflow as e_codeflow


class StalkerCodeFlow(e_codeflow.CodeFlowContext):

    def __init__(self, trace):
        e_codeflow.CodeFlowContext.__init__(self, trace, persist=True, recurse=False)
        self.trace = trace
        self.setupBreakLists(None)

    def setupBreakLists(self, mmap):
        self.mmap = mmap
        self.bplist = []   # Block Breaks
        self.sbreaks = []  # Stalker Breaks
        self.scbreaks = []  # Callbreaks

    def _cb_opcode(self, va, op, branches):

        ret = []
        for br, bflags in branches:

            if bflags & envi.BR_DEREF and br is not None:
                bflags &= ~envi.BR_DEREF # Mask it back out...
                if not self.trace.probeMemory(br, 1, e_mem.MM_READ):
                    continue

                br = self.trace.readMemoryFormat(br, '<P')[0]

            # Skip branches to other maps...
            if br is not None and self.trace.getMemoryMap(br) != self.mmap:
                continue

            ret.append((br, bflags))

            # Procedural branches to regs etc must be marked
            # Otherwise, add another breakpoint like us
            if bflags & envi.BR_PROC:
                if br is None:
                    self.scbreaks.append(op.va)
                else:
                    self.sbreaks.append(br)
                continue

            if br is None:
                self.scbreaks.append(op.va)
                continue

            # Conditional branches always create new blocks...
            if bflags & envi.BR_COND:
                self.bplist.append(br)
                continue

            # Even non-conditional jmp's will create new blocks for now...
            if br != op.va + len(op):
                self.bplist.append(br)
                continue

        return ret


class StalkerBreak(vtrace.Breakpoint):

    '''
    Stalker breakpoints are added to function entry points
    to trigger code-flow analysis and subsequent block breakpoint
    addition.
    '''

    def __init__(self, address, expression=None):
        vtrace.Breakpoint.__init__(self, address, expression=expression)
        self.fastbreak = True
        self.mymap = None

    def resolvedaddr(self, trace, address):
        vtrace.Breakpoint.resolvedaddr(self, trace, address)
        self.mymap = trace.getMemoryMap(address)

    def notify(self, event, trace):
        self.trace = trace

        # Get out of the way
        self.enabled = False

        breaks = trace.getMeta('StalkerBreaks')
        h = trace.getMeta('StalkerHits')
        h.append(self.address)

        cf = trace.getMeta('StalkerCodeFlow')
        if cf is None:
            cf = StalkerCodeFlow(trace)
            trace.setMeta('StalkerCodeFlow', cf)

        cf.setupBreakLists(self.mymap)
        cf.addCodeFlow(self.address)

        for va in cf.bplist:
            if breaks.get(va):
                continue
            breaks[va] = True
            b = StalkerBlockBreak(va)
            trace.addBreakpoint(b)

        for va in cf.sbreaks:
            if breaks.get(va):
                continue
            breaks[va] = True
            b = StalkerBreak(va)
            trace.addBreakpoint(b)

        for va in cf.scbreaks:
            if breaks.get(va):
                continue
            breaks[va] = True
            b = StalkerDynBreak(va)
            trace.addBreakpoint(b)


class StalkerBlockBreak(vtrace.Breakpoint):
    '''
    A breakpoint object which is put on codeblock boundaries
    to track hits.
    '''

    def __init__(self, address, expression=None):
        vtrace.Breakpoint.__init__(self, address, expression=expression)
        self.fastbreak = True

    def notify(self, event, trace):
        h = trace.getMeta('StalkerHits')
        h.append(self.address)
        self.enabled = False
        trace.runAgain()


class StalkerDynBreak(vtrace.Breakpoint):

    '''
    A breakpoint which is placed on dynamic branches to track
    code flow across them.
    '''

    def __init__(self, address, expression=None):
        vtrace.Breakpoint.__init__(self, address, expression=expression)
        self.fastbreak = True
        self.mymap = None
        self.lasthit = None
        self.lastcnt = 0

    def resolvedaddr(self, trace, address):
        vtrace.Breakpoint.resolvedaddr(self, trace, address)
        self.mymap = trace.getMemoryMap(address)

    def notify(self, event, trace):

        trace.runAgain()

        op = trace.parseOpcode(self.address)
        # Where is the call going?
        dva = op.getOperValue(0, emu=trace)

        if self.lasthit == dva:
            self.lastcnt += 1
        else:
            self.lasthit = dva
            self.lastcnt = 0

        if trace.getMemoryMap(dva) == self.mymap:
            addStalkerEntry(trace, dva)

        if self.lastcnt > 10:  # FIXME what should this be??!?!
            self.lasthit = None
            self.lastcnt = 0
            self.enabled = False


def initStalker(trace):
    if trace.getMeta('StalkerBreaks') is None:
        trace.setMeta('StalkerBreaks', {})
        trace.setMeta('StalkerHits', [])


def clearStalkerHits(trace):
    '''
    Clear the stalker hit list for the given trace
    '''
    initStalker(trace)
    trace.setMeta('StalkerHits', [])


def getStalkerHits(trace):
    '''
    Retrieve the list of blocks hit in the current stalker
    '''
    initStalker(trace)
    return trace.getMeta('StalkerHits', [])


def clearStalkerBreaks(trace):
    '''
    Cleanup all stalker breaks and metadata
    '''
    initStalker(trace)
    breaks = trace.getMeta('StalkerBreaks', {})
    trace.setMeta('StalkerCodeFlow', None)
    bpaddrs = list(breaks.keys())
    for va in bpaddrs:
        bp = trace.getBreakpointByAddr(va)
        if bp is not None:
            trace.removeBreakpoint(bp.id)
        breaks.pop(va, None)


def resetStalkerBreaks(trace):
    '''
    Re-enable all previously hit stalker breakpoints.
    '''
    initStalker(trace)
    breaks = trace.getMeta('StalkerBreaks', {})
    bpaddrs = list(breaks.keys())
    trace.fb_bp_done = False  # FIXME HACK
    for va in bpaddrs:
        bp = trace.getBreakpointByAddr(va)
        if bp is not None:
            trace.setBreakpointEnabled(bp.id, enabled=True)


def addStalkerEntry(trace, va):
    '''
    Add stalker coverage beginning with the specified entry point
    '''
    initStalker(trace)
    b = trace.getMeta('StalkerBreaks')
    if b.get(va):
        return
    bp = StalkerBreak(va)
    trace.addBreakpoint(bp)
    b[va] = True
