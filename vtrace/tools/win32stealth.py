import vtrace
import vstruct
import vivisect.impapi as viv_impapi

class StealthBreak(vtrace.Breakpoint):
    '''
    Base class that can be extended by other classes to bypass anti-debugging
    checks.
    '''
    def __init__(self, sym=None):
        vtrace.Breakpoint.__init__(self, None, expression=sym)
        self.fastbreak = True

        self.bpid = None
        self.ispatched = False
        self.name = None

        self.impapi = None
        self.cc = None
        self.argc = None

    def isPatched(self):
        return self.ispatched

    def getName(self):
        return self.name

    def enablePatch(self, trace):
        if not self.isPatched():
            self.bpid = trace.addBreakpoint(self)
            self.ispatched = True

    def disablePatch(self, trace):
        if self.isPatched():
            trace.removeBreakpoint(self.bpid)
            self.ispatched = False
            self.bpid = None

    def notify(self, event, trace):
        if self.impapi is not None:
            # cached
            return

        self.impapi = viv_impapi.getImportApi(trace.getMeta('Platform'), trace.getMeta('Architecture'))
        cc = self.impapi.getImpApiCallConv(self.vte)
        emu = vtrace.getEmu(trace)
        self.cc = emu.getCallingConvention(cc)
        self.argc = len(self.impapi.getImpApiArgs(self.vte))

class StealthPeb(StealthBreak):
    '''
    Disables the "BeingDebugged" and "NtGlobalFlag" flags in the PEB.
    Also modifies heap flags that indicate debugging.
    '''
    def __init__(self):
        self.patched = False
        self.savedForceFlags = None
        self.savedNtGlobalFlags = None
        self.name = 'Peb'

    def isPatched(self):
        return self.patched

    def writeBeingDebugged(self, trace, val):
        peb = trace.parseExpression('peb')
        ps = vstruct.getStructure('win32.PEB')
        off = ps.vsGetOffset('BeingDebugged')
        trace.writeMemoryFormat(peb+off, '<B', val)
        #TODO Save off the old peb so we can fix it when we want to break
        #trace.setMeta("Win32StealthPeb", val)

    def writeProcessHeapFlags(self, trace, val):
        pebaddr = trace.parseExpression('peb')
        peb = trace.getStruct('win32.PEB', pebaddr)
        structHeap = trace.getStruct('win32.HEAP', peb.ProcessHeap)
        self.savedForceFlags = structHeap.ForceFlags
        structHeap.ForceFlags = val
        trace.writeMemory(peb.ProcessHeap, structHeap.vsEmit())

    def writeNtGlobalFlag(self, trace, val):
        pebaddr = trace.parseExpression('peb')
        peb = trace.getStruct('win32.PEB', pebaddr)
        self.savedNtGlobalFlags = peb.NtGlobalFlag
        peb.NtGlobalFlag = val
        trace.writeMemory(pebaddr, peb.vsEmit())

    def enablePatch(self, trace):
        trace.requireNotRunning()
        self.patched = True
        self.writeBeingDebugged(trace, 0)
        self.writeProcessHeapFlags(trace, 0)
        self.writeNtGlobalFlag(trace, 0)

    def disablePatch(self, trace):
        trace.requireNotRunning()
        self.patched = False
        self.writeBeingDebugged(trace, 1)
        self.writeProcessHeapFlags(trace, self.savedForceFlags)
        self.writeNtGlobalFlag(trace, self.savedNtGlobalFlags)

class StealthCheckRemoteDebuggerPresent(StealthBreak):
    '''
    Forces the "CheckRemoteDebuggerPresent" API to indicate that the process
    is not being debugged.
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'CheckRemoteDebuggerPresent'

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        handle, outbool = self.cc.getCallArgs(trace, self.argc)
        trace.writeMemoryFormat(outbool, '<P', 0)
        self.cc.execCallReturn(trace, 1, self.argc)

        trace.runAgain()

class StealthGetTickCount(StealthBreak):
    '''
    Returns a static tickcount in case the application checks time deltas
    between instructions.
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'GetTickCount'
        self.tickReturn = 0xdeadbeef

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        self.cc.execCallReturn(trace, self.tickReturn, self.argc)
        self.tickReturn += 1

        trace.runAgain()

class StealthOutputDebugString(StealthBreak):
    '''
    Forces the OutputDebugString API to return 1.
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'OutputDebugString'

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        self.cc.execCallReturn(trace, 1, self.argc)

        trace.runAgain()

class StealthZwClose(StealthBreak):
    '''
    When called with a invalid handle (-1) the malware will simply return so
    an exception is not thrown when a debugger is attached.
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'ZwClose'

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        handle = self.cc.getCallArgs(trace, self.argc)
        if handle == -1:
            self.cc.execCallReturn(trace, 0, self.argc)

        trace.runAgain()

class StealthZwSetInformationThread(StealthBreak):
    '''
    When ZwSetInformationThread is called with ThreadHideFromDebugger, just
    return in case threads try to detach from the debugger.
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'ZwSetInformationThread'

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        handle, threadInfoClass, threadInfo, threadInfoLen = self.cc.getCallArgs(trace, self.argc)
        # ThreadHideFromDebugger = 0x11
        if threadInfoClass == 0x11:
            # If ThreadHideFromDebugger is passed, fake it
            trace.writeMemoryFormat(threadInfo, '<P', 0)
            self.cc.execCallReturn(trace, 0, self.argc)

        trace.runAgain()

class StealthZwQueryInformationProcess(StealthBreak):
    '''
    Forces ZwQueryInformationProcess to return success when passed
    "ProcessDebugPort"
    '''
    def __init__(self, sym):
        StealthBreak.__init__(self, sym)
        self.name = 'ZwQueryInformationProcess'

    def notify(self, event, trace):
        StealthBreak.notify(self, event, trace)
        handle, procInfoClass, procInfo, procInfoLen, retLen = self.cc.getCallArgs(trace, self.argc)
        # ProcessDebugPort = 7
        if procInfoClass == 7:
            # If ProcessDebugPort is passed, fake it out by setting
            # ProcessInformation to zero
            trace.writeMemoryFormat(procInfo, '<P', 0)
            trace.writeMemoryFormat(retLen, '<P', procInfoLen)
            self.cc.execCallReturn(trace, 0, self.argc)

        trace.runAgain()

def stealthInit(trace):
    objs = []
    objs.append(StealthPeb())
    objs.append(StealthCheckRemoteDebuggerPresent('kernel32.CheckRemoteDebuggerPresent'))
    objs.append(StealthGetTickCount('kernel32.GetTickCount'))
    objs.append(StealthZwClose('ntdll.ZwClose'))
    objs.append(StealthZwSetInformationThread('ntdll.ZwSetInformationThread'))
    objs.append(StealthOutputDebugString('kernel32.OutputDebugStringA'))
    objs.append(StealthZwQueryInformationProcess('ntdll.ZwQueryInformationProcess'))

    trace.setMeta('Win32Stealth', objs)

def getStatus(trace):
    statList = []
    if not trace.getMeta('Win32Stealth'):
       stealthInit(trace)

    stealthObjs = trace.getMeta('Win32Stealth')
    for inst in stealthObjs:
        statList.append((inst.name, inst.isPatched()))

    return statList

def enableAllStealth(trace):
    if not trace.getMeta('Win32Stealth'):
       stealthInit(trace)

    stealthObjs = trace.getMeta('Win32Stealth')
    for inst in stealthObjs:
        inst.enablePatch(trace)

def disableAllStealth(trace):
    if not trace.getMeta('Win32Stealth'):
       stealthInit(trace)

    stealthObjs = trace.getMeta('Win32Stealth')
    for inst in stealthObjs:
        inst.disablePatch(trace)

def stealthify(trace, name):
    if not trace.getMeta('Win32Stealth'):
       stealthInit(trace)

    stealthObjs = trace.getMeta('Win32Stealth')
    for inst in stealthObjs:
        if inst.getName().lower() == name:
            inst.enablePatch(trace)

def unstealthify(trace, name):
    if not trace.getMeta('Win32Stealth'):
       stealthInit(trace)

    stealthObjs = trace.getMeta('Win32Stealth')
    for inst in stealthObjs:
        if inst.getName().lower() == name:
            inst.disablePatch(trace)
