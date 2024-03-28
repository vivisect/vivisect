'''
Code for hooking import address tables by making them invalid
pointers and catching the exceptions...
'''
import PE
import vtrace
import vtrace.watchpoints as vt_watchpoints

class IatHook(vt_watchpoints.Watchpoint):
    '''
    Abuse the PageWatch subsystem to allow function pointers to be
    frob'd to create breakpoint like behavior.
    '''

    newptr = 0xfbfbf000

    def __init__(self, ptraddr, iatname):
        fakeptr = IatHook.newptr
        IatHook.newptr += 4096 # FIXME race... sigh...

        vt_watchpoints.Watchpoint.__init__(self, fakeptr)
        self.ptraddr = ptraddr
        self.fakeptr = fakeptr
        self.iatname = iatname
        self.origptr = None

    def getName(self):
        #bname = Breakpoint.getName(self)
        return self.iatname

    def resolveAddr(self, trace, addr):
        pass

    def activate(self, trace):
        if self.origptr is None:
            self.origptr = trace.readMemoryFormat(self.ptraddr, '<P')[0]
        trace.writeMemoryFormat(self.ptraddr, '<P', self.fakeptr)

    def deactivate(self, trace):
        if self.origptr is not None:
            trace.writeMemoryFormat(self.ptraddr, '<P', self.origptr)

    def notify(self, event, trace):
        # We have to fake out the program counter...
        trace.setProgramCounter(self.origptr)
        trace.setCurrentSignal(None)
        return vt_watchpoints.Watchpoint.notify(self, event, trace)


def hookIat(trace, libname, implib='*', impfunc='*', fast=False):
    '''
    Hook the IAT with special "breakpoint" like objects which
    handle the memory access errors and document the calls...
    Set fast=True for them to be "Fastbreak" breakpoints.

    This returns a list of (name, bpid) tuples...

    Example:
        for impname, bpid in hookIat(t, 'ws2_32')
            t.setBreakpointCode(bpid, codestr)
            ...
    '''
    ret = []
    baseaddr = trace.parseExpression(libname)
    pe = PE.peFromMemoryObject(trace, baseaddr)
    origs = {}

    implib = implib.lower()
    impfunc = impfunc.lower()

    for rva, ilib, ifunc in pe.getImports():
        ilib = ilib.lower().replace('.dll', '')

        if ilib != implib and implib != '*':
            continue

        if ifunc.lower() != impfunc and impfunc!='*':
            continue

        iatname = '%s.%s.%s' % (libname, ilib, ifunc)
        wp = IatHook(baseaddr + rva, iatname)
        wp.fastbreak = fast
        bpid = trace.addBreakpoint(wp)
        ret.append( (iatname, bpid) )

    return ret
