'''
Specialized breakpoints which identify dangerous calling
mechanisms and tag them.
'''
import envi.memory as e_mem
import vtrace.breakpoints as vt_breakpoints

def getArg(trace, argidx):
    '''
    Assuming we are at the instruction after
    a call, grab the argument at the specified
    index (skipping the saved instruction pointer).
    '''
    cc = detect_cc(trace)    
    args = cc.getCallArgs(trace, argidx)
    return args[-1]

def detect_cc(trace):
    '''
	Autodetect the calling convention based on
	the current architecture and platform
	'''
    cc_dict = {('i386' ,'windows') : 'stdcall',
               ('i386' ,'linux')   : 'stdcall',
               ('amd64','windows') : 'msx64call',
               ('amd64','linux')   : 'sysvamd64call', 
              }
		   
    arch_plat = (trace.getMeta("Architecture"), trace.getMeta("Platform"))
	
    return trace.getEmulator().getCallingConvention(cc_dict[arch_plat])

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
        return "%s argidx: %d" % (self._symname, self._argidx)

    def notify(self, event, trace):
        arg = getArg(trace, self._argidx)
        self.fastbreak = True
        if trace.probeMemory(arg, 1, e_mem.MM_WRITE):
            print("SNIPER: %s TOOK DYNAMIC ARG IDX %d (0x%.8x)" % (self._symname, self._argidx, arg))
            self.fastbreak = False

class SniperArgValueBreak(vt_breakpoints.Breakpoint):
    '''
    A breakpoint for monitoring an API for being called with a particular
    value.
    '''
    def __init__(self, symname, argidx, argval):
        vt_breakpoints.Breakpoint.__init__(self, None, expression=symname)
        self.fastbreak = True
        self._argval = argval
        self._argidx = argidx
        self._symname = symname
		
    def notify(self, event, trace):
        arg = getArg(trace, self._argidx)
        self.fastbreak = True
        if(arg == self._argval):
            print("SNIPER: %s TOOK VALUE (0x%.8x) FOR ARG IDX %d" % (self._symname, arg, self._argidx))
            self.fastbreak = False

def snipeDynArg(trace, symname, argidx):
    '''
    Construct a SnyperDynArgBreak and snap it in.
    '''
    bp = SniperDynArgBreak(symname, argidx)
    bpid = trace.addBreakpoint(bp)
    return bpid
	
def snipeArgValue(trace, symname, argidx, argval):
    '''
    Construct a SnyperArgValueBreak and snap it in.
    '''
    bp = SniperArgValueBreak(symname, argidx, argval)
    bpid = trace.addBreakpoint(bp)
    return bpid
