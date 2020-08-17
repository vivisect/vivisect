'''
Specialized breakpoints which identify dangerous calling
mechanisms and tag them.
'''
import logging

import envi.memory as e_mem
import vtrace.breakpoints as vt_breakpoints


logger = logging.getLogger(__name__)


def getStackArg(trace, argidx):
    '''
    Assuming we are at the instruction after
    a call, grab the stack argument at the specified
    index (skipping the saved instruction pointer).
    '''
    stack = trace.getStackCounter()
    fmt = '<P' + ('P' * (argidx+1))
    args = trace.readMemoryFormat(stack, fmt)
    return args[-1]


class SniperDynArgBreak(vt_breakpoints.Breakpoint):
    '''
    A breakpoint for use in determining if an API was called
    with a dynamic pointer.
    '''

    def __init__(self, symname, argidx):
        vt_breakpoints.Breakpoint.__init__(self, None, expression=symname)
        self.fastbreak = True
        self._argidx = argidx
        self._symname = symname

    def getName(self):
        return '%s argidx: %d' % (self._symname, self._argidx)

    def notify(self, event, trace):
        arg = getStackArg(trace, self._argidx)
        self.fastbreak = True
        if trace.probeMemory(arg, 1, e_mem.MM_WRITE):
            logger.info('SNIPER: %s TOOK DYNAMIC ARG IDX %d (0x%.8x)', self._symname, self._argidx, arg)
            self.fastbreak = False


class SniperArgValueBreak(vt_breakpoints.Breakpoint):
    '''
    A breakpoint for monitoring an API for being called with a particular
    value.
    '''
    def __init__(self, symname, argidx, argval):
        pass


def snipeDynArg(trace, symname, argidx):
    '''
    Construct a SnyperDynArgBreak and snap it in.
    '''
    bp = SniperDynArgBreak(symname, argidx)
    bpid = trace.addBreakpoint(bp)
    return bpid
