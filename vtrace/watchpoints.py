"""
Watchpoint Objects
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import envi.const as e_const

from vtrace import *
from vtrace.breakpoints import *

class Watchpoint(Breakpoint):
    """
    The basic "break on access" watchpoint.  Extended from 
    Breakpoints and handled almost exactly the same way...
    """
    def __init__(self, addr, expression=None, size=4, perms="rw"):
        Breakpoint.__init__(self, addr, expression=expression)
        self.wpsize = size
        self.wpperms = perms

    def inittrace(self, trace):
        # No need to get a breakinstr
        pass

    def resolvedaddr(self, trace, addr):
        # We needn't save the memory at our addr...
        pass

    def getName(self):
        bname = Breakpoint.getName(self)
        return "%s (%s %d bytes)" % (bname, self.wpperms, self.wpsize)

    def activate(self, trace):
        trace.requireAttached()
        if not self.active:
            if self.address is not None:
                trace.archAddWatchpoint(self.address, size=self.wpsize, perms=self.wpperms)
                self.active = True
        return self.active

    def deactivate(self, trace):
        trace.requireAttached()
        if self.active:
            trace.archRemWatchpoint(self.address)
            self.active = False
        return self.active

class PageWatchpoint(Watchpoint):
    """
    A special "watchpoint" that uses memory permissions to
    watch for accesses to whole memory maps.  This *requires* OS
    help and only works on platforms which support:
    * platformProtectMemory()
    * signal/exceptions which denote the fault address on SEGV

    NOTE: These *must* be added page aligned
    """
    def __init__(self, addr, expression=None, size=4, watchread=False):
        Watchpoint.__init__(self, addr, expression=expression, size=size, perms='rw')
        self._orig_perms = None
        self._new_perms = e_const.MM_READ
        if watchread:
            self._new_perms = e_const.MM_NONE

    def resolvedaddr(self, trace, addr):
        self._orig_perms = trace.getMemoryMap(addr)[2]

    def notify(self, event, trace):
        pw = trace.getMeta('pagewatch')
        pc = trace.getProgramCounter()
        vaddr,vperm = trace.platformGetMemFault()
        pw.append((pc, vaddr, vperm))
        # Change to/from fastbreak on pagerun...
        self.fastbreak = trace.getMeta('pagerun')

    def getName(self):
        bname = Breakpoint.getName(self)
        return "%s (%s %d bytes)" % (bname, e_mem.reprPerms(self._new_perms), self.wpsize)

    def activate(self, trace):
        #trace.requireNotRunning()
        if not self.active:
            trace.protectMemory(self.address, self.wpsize, self._new_perms)
            self.active = True
        return self.active

    def deactivate(self, trace):
        #trace.requireNotRunning()
        if self.active:
            trace.protectMemory(self.address, self.wpsize, self._orig_perms)
            self.active = False
        return self.active
