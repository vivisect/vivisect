"""
Vtrace Debugger Framework

Vtrace is a *mostly* native python debugging framework which
can be used to quickly write programatic debuggers and research
tools.

I'm not known for writting great docs...  but the code should
be pretty straight forward...

This has been in use for many years privately, but is nowhere
*near* free of bugs...  idiosyncracies abound.

==== Werd =====================================================

Blah blah blah... many more docs to come.

Brought to you by kenshoto.  e-mail invisigoth.

Greetz:
    h1kari - eeeeeooorrrmmm  CHKCHKCHKCHKCHKCHKCHK
    Ghetto - wizoo... to the tizoot.
    atlas - *whew* finally...  no more teasing...
    beatle/dnm - come out and play yo!
    The Kenshoto Gophers.
    Blackhats Everywhere.

"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import re
import code
import time
import types
import logging
import platform

import envi
import envi.bits as e_bits
import envi.memory as e_mem
import envi.registers as e_reg
import envi.expression as e_expr
import envi.symstore.resolver as e_resolv
import envi.symstore.symcache as e_symcache

import vstruct
from vtrace.const import *

logger = logging.getLogger(__name__)
remote = None       # If set, we're a vtrace client (set to serverhost)
cobra_daemon = None
port = 0x5656
verbose = False

# File Descriptor / Handle Types
FD_UNKNOWN = 0 # Unknown or we don't have a type for it
FD_FILE = 1
FD_SOCKET = 2
FD_PIPE = 3
FD_LOCK = 4   # Win32 Mutant/Lock/Semaphore
FD_EVENT = 5  # Win32 Event/KeyedEvent
FD_THREAD = 6 # Win32 Thread
FD_REGKEY = 7 # Win32 Registry Key

# Vtrace Symbol Types
SYM_MISC = -1
SYM_GLOBAL = 0 # Global (mostly vars)
SYM_LOCAL = 1 # Locals
SYM_FUNCTION = 2 # Functions
SYM_SECTION = 3 # Binary section
SYM_META = 4 # Info that we enumerate

# Vtrace Symbol Offsets
VSYM_NAME = 0
VSYM_ADDR = 1
VSYM_SIZE = 2
VSYM_TYPE = 3
VSYM_FILE = 4

from vtrace.rmi import *
from vtrace.notifiers import *
from vtrace.breakpoints import *
from vtrace.watchpoints import *
import vtrace.util as v_util

class PlatformException(Exception):
    """
    A universal way to represent a failure in the
    platform layer for this tracer.  platformFoo methods
    should raise this rather than allowing their platform
    specific exception types (which don't likely pickle, or
    are not cross platform)
    """
    pass

class AccessViolation(Exception):
    """
    An exception which is raised on bad-touch to memory
    """
    def __init__(self, va, perm=0):
        self.va = va
        self.perm = perm
        Exception.__init__(self, "AccessViolation at 0x%.8x (%d)" % (va, perm))

class Trace(e_mem.IMemory, e_reg.RegisterContext, e_resolv.SymbolResolver, object):
    """
    The main tracer object.  A trace instance is dynamically generated using
    this and *many* potential mixin classes.  However, API users should *not*
    worry about the methods that come from the mixins...  Everything that is
    *meant* to be used from the API is contained and documented here.
    """
    def __init__(self, archname=None):
        # For the crazy thread-call-proxy-thing
        # (must come first for __getattribute__
        self.requires_thread = {}
        self.proxymeth = None  # FIXME hack for now...
        self._released = False

        # The universal place for all modes
        # that might be platform dependant...
        self.modes = {}
        self.modedocs = {}
        self.notifiers = {}
        self.namecache = []

        # For all transient data (if notifiers want
        # to track stuff per-trace
        self.metadata = {}

        self.initMode("RunForever", False, "Run until RunForever = False")
        self.initMode("NonBlocking", False, "A call to wait() fires a thread to wait *for* you")
        self.initMode("ThreadProxy", True, "Proxy necessary requests through a single thread (can deadlock...)")
        self.initMode("SingleStep", False, "All calls to run() actually just step.  This allows RunForever + SingleStep to step forever ;)")
        self.initMode("FastStep", False, "All stepi() will NOT generate a step event")

        self.regcache = None
        self.regcachedirty = False
        self.sus_threads = {}   # A dictionary of suspended threads

        # Set if we're a server and this trace is proxied
        self.proxy = None

        # Set us up with an envi arch module
        # FIXME eventually we should just inherit one...
        if archname is None:
            archname = envi.getCurrentArch()

        arch = envi.getArchByName(archname)
        self.setMeta('Architecture', archname)
        self.arch = envi.getArchModule(name=archname)

        e_resolv.SymbolResolver.__init__(self, width=self.arch.getPointerSize())
        e_mem.IMemory.__init__(self, arch=arch)
        e_reg.RegisterContext.__init__(self)

        # Add event numbers to here for auto-continue
        self.auto_continue = [NOTIFY_LOAD_LIBRARY, NOTIFY_CREATE_THREAD, NOTIFY_UNLOAD_LIBRARY, NOTIFY_EXIT_THREAD, NOTIFY_DEBUG_PRINT]

    def execute(self, cmdline):
        """
        Start a new process and debug it
        """
        if self.isAttached():
            raise Exception("ERROR - Tracer must first be detached before you can execute()")

        pid = self.platformExec(cmdline)
        self._justAttached(pid)
        self.setMeta('ExecCommand', cmdline)
        self.wait()

    def parseOpcodes(self, num, va=None):
        '''
        Returns next num of linear disasm'd opcodes objects.  Optionally pass
        a va to start there instead of the current program counter.
        '''
        if num <= 0:
            raise Exception('you must specify a positive number of opcodes')

        if va is None:
            va = self.getProgramCounter()

        ops = []
        for i in range(0, num):
            op = self.parseOpcode(va)
            ops.append(op)
            va += op.size

        return ops

    def getCurrentSignal(self):
        '''
        Retrieve the current signal/exception posted to the process.
        If there are no pending signals/exceptions the API will return
        None.  For POSIX systems, this will be a traditional POSIX signal.
        For Windows systems it will be a current exception code (if any).

        Example: sig = trace.getCurrentSignal()
        '''
        return self.platformGetSignal()

    def setCurrentSignal(self, sig=None):
        '''
        Set the currently pending signal for delivery to the target process on
        continue.  This is intended for use by programs wishing the mask or
        change the delivery of exceptions on a NOTIFY_SIGNAL event.

        Example:  trace.setCurrentSignal(None)
        '''
        return self.platformSetSignal(sig)

    def addIgnoreSignal(self, code, address=0):
        """
        By adding an IgnoreSignal you tell the tracer object to
        supress the notification of a particular type of signal.
        In POSIX, these are regular signals, in Win32, these
        are exception codes.  This is mostly useful in RunForever
        mode because you still need the process to begin running again.
        (these may be viewed/modified by the metadata key "IgnoredSignals")
        FIXME: make address do something.
        """
        self.getMeta("IgnoredSignals").append(code)

    def delIgnoreSignal(self, code, address=0):
        """
        See addIgnoreSignal for a description of signal ignoring.
        This removes an ignored signal and re-enables it's delivery.
        """
        self.getMeta("IgnoredSignals").remove(code)

    def attach(self, pid):
        """
        Attach to a new process ID.
        """
        if self.isAttached():
            self.detach()

        try:
            self.platformAttach(pid)
            self._justAttached(pid)
            self.wait()
        except Exception as msg:
            raise PlatformException(str(msg))

    def stepi(self):
        """
        Single step the target process ONE instruction (and do
        NOT activate breakpoints for the one step). Also, we
        don't deliver pending signals for the single step...
        Use the mode FastStep to allow/suppress notifier callbacks on step
        """
        self.requireNotRunning()

        # Since we don't go through the normal run/wait
        # code, we have a little house-keeping to do...
        self.curbp = None

        self._syncRegs()
        self.platformStepi()
        event = self.platformWait()
        self.platformProcessEvent(event)

    def run(self, until=None):
        """
        Allow the traced target to continue execution.  (Depending on the mode
        "Blocking" this will either block until an event, or return immediately)
        Additionally, the argument until may be used to cause execution to
        continue until the specified address is reached (internally uses and
        removes a breakpoint).
        """
        self.requireAttached()
        self.requireNotRunning()
        self.requireNotExited()

        if self.getMode("SingleStep", False):
            self.steploop()

        else:
            if until is not None:
                self.setMode("RunForever", True)
                self.addBreakpoint(StopAndRemoveBreak(until))

            self._doRun()
            self.wait()

    def runAgain(self, val=True):
        """
        The runAgain() method may be used from inside a notifier
        (Notifier, Breakpoint, Watchpoint, etc...) to inform the trace
        that once event processing is complete, it should continue
        running the trace.
        """
        self.runagain = val

    def kill(self):
        """
        Kill the target process for this trace (will result in process
        exit and fire appropriate notifiers)
        """
        self.requireAttached()
        self.requireNotExited()
        self.platformKill()
        self.attached = False

    def detach(self):
        '''
        Detach from the currently attached process.
        '''
        self.requireNotRunning()
        self.fireNotifiers(NOTIFY_DETACH)
        self._syncRegs()
        self.platformDetach()
        self.attached = False
        self.pid = 0
        self.mapcache = None

    def release(self):
        '''
        Release resources for this tracer.  This API should be called
        once you are done with the trace.
        '''
        if not self._released:
            self._released = True
            if self.attached:
                self.detach()
            self._cleanupResources()
            self.platformRelease()

    def getPid(self):
        """
        Return the pid for this Trace
        """
        return self.pid

    def getNormalizedLibNames(self):
        """
        Symbols are stored internally based off of
        "normalized" library names.  This method returns
        the list of normalized names for the loaded libraries.

        (probably only useful for writing symbol browsers...)
        """
        return list(self.getMeta("LibraryBases").keys())

    def getSymsForFile(self, libname):
        """
        Return the entire symbol list for the specified
        normalized library name.  The list is returned as
        "symtup" tuples of (va,size,name,type,fname).
        """
        self._loadBinaryNorm(libname)
        sym = self.getSymByName(libname)
        if sym is None:
            raise Exception('Invalid Library Name: %s' % libname)
        return sym.getSymList()

    def getNames(self):
        if not self.namecache:
            names = []
            for lib in self.getNormalizedLibNames():
                for sym in self.getSymsForFile(lib):
                    names.append((sym.value, str(sym)))
            self.namecache = sorted(names, key=lambda n: len(n[1]), reverse=True)
        return self.namecache

    def getSymByAddr(self, addr, exact=True):
        """
        Return an envi Symbol object for an address.
        Use exact=False to get the nearest previous match.
        """
        # NOTE: Override this from envi.SymbolResolver to do on-demand
        # file parsing.

        r = e_resolv.SymbolResolver.getSymByAddr(self, addr, exact=exact)
        if r is not None:
            return r

        # See if we need to parse the file.
        mmap = self.getMemoryMap(addr)
        if mmap is None:
            return None

        va, size, perms, fname = mmap

        if not self._loadBinary(fname):
            return None

        # Take a second shot after parsing
        return e_resolv.SymbolResolver.getSymByAddr(self, addr, exact=exact)

    def getSymByAddrThunkAware(self, va):
        '''
        TODO: DO NOT USE THIS FUNCTION, GOING AWAY.
        getBestSymEtc? depth / aggressiveness?

        for the given va:
        1. attempt to get the sym by using getSymByAddr
        2. if 1 fails, check the target of the branch for a sym.

        returns a tuple (sym, is_thunk).  sym is None if no sym is found.
        '''
        sym = self.getSymByAddr(va)
        if sym is not None:
            return str(sym), False

        try:
            op = self.parseOpcode(va)
            for tva, tflags in op.getTargets(emu=self):
                if tva is None:
                    continue

                sym = self.getSymByAddr(tva)
                if sym is not None:
                    return str(sym), True

        except Exception as e:
            # getTargets->readMemory error on bva
            logger.warning('getSymByAddrThunkAware: %s', e)

        return None, False

    def getSymByName(self, name):
        """
        Return an envi.Symbol object for the given name (or None)
        """
        self._loadBinaryNorm(name)
        return e_resolv.SymbolResolver.getSymByName(self, name)

    def setSymCachePath(self, path):
        '''
        Set the symbol cache path for the tracer.

        The "path" syntax is a ; seperated list of either directories
        or cobra URIs which implement the SymbolCache interface.

        Example:
            trace.setSymCachePath('/home/invisigoth/.envi/symcache;cobra://symbols.com/SymbolCache')

        NOTE: vdb automatically handles this with a config option
        '''
        self.symcache = e_symcache.SymbolCachePath(path)

    def searchSymbols(self, regex, libname=None):
        '''
        Search for symbols which match the given regular expression.  Specify
        libname as the "normalized" library name to only search the specified
        lib.

        Example:  for sym in trace.searchSymbols('.*CreateFile.*', 'kernel32'):
        '''
        reobj = re.compile(regex)
        if libname is not None:
            libs = [libname, ]
        else:
            libs = self.getNormalizedLibNames()

        ret = []
        for lname in libs:
            for sym in self.getSymsForFile(lname):
                symstr = str(sym)
                if reobj.match(symstr):
                    ret.append(sym)
        return ret

    def getRegisterContext(self, threadid=None):
        """
        Retrieve the envi.registers.RegisterContext object for the
        specified thread.  Use this API to iterate over threads
        register values without setting the global tracer thread context.
        """
        if threadid is None:
            threadid = self.getMeta("ThreadId")
        return self._cacheRegs(threadid)

#######################################################################
#
# We mirror the RegisterContext API using our own thread index based
# cache.  These APIs must stay in sync with envi.registers.RegisterContext
# NOTE: for now we only need to over-ride get/setRegister because all the
# higher level APIs call them.
#

    def getRegister(self, idx):
        ctx = self.getRegisterContext()
        return ctx.getRegister(idx)

    def setRegister(self, idx, value):
        ctx = self.getRegisterContext()
        ctx.setRegister(idx, value)

#######################################################################

    def allocateMemory(self, size, perms=e_mem.MM_RWX, suggestaddr=0):
        """
        Allocate a chunk of memory inside the target process' address
        space.  Memory wil be mapped rwx unless otherwise specified with
        perms=envi.memory.MM_FOO values. Optionally you may *suggest* an address
        to the allocator, but there is no guarentee.  Returns the mapped
        memory address.
        """
        self.requireNotRunning()
        self.mapcache = None # We may have a new memory map
        return self.platformAllocateMemory(size, perms=perms, suggestaddr=suggestaddr)

    def protectMemory(self, va, size, perms):
        """
        Change the page protections on the specified region of memory.
        See envi.memory for perms values.
        """
        self.requireNotRunning()
        self.mapcache = None # We may have new memory protections
        return self.platformProtectMemory(va, size, perms)

    def readMemory(self, address, size):
        """
        Read memory from address.  Areas that are NOT valid memory will be read
        back as \x00s (this probably goes in a mixin soon)
        """
        self.requireNotRunning()
        return self.platformReadMemory(int(address), int(size))

    def writeMemory(self, address, bytez):
        """
        Write the given bytes to the address in the current trace.
        """
        self.requireNotRunning()
        self.platformWriteMemory(int(address), bytez)

    def searchMemory(self, needle, regex=False):
        """
        Search all of process memory for a sequence of bytes.
        """
        ret = e_mem.IMemory.searchMemory(self, needle, regex=regex)
        self.setMeta('search', ret)
        self.setVariable('search', ret)
        return ret

    def searchMemoryRange(self, needle, address, size, regex=False):
        """
        Search a memory range for the specified sequence of bytes
        """
        ret = e_mem.IMemory.searchMemoryRange(self, needle, address, size, regex=regex)
        self.setMeta('search', ret)
        self.setVariable('search', ret)
        return ret

    def setMeta(self, name, value):
        """
        Set some metadata.  Metadata is a clean way for
        arbitrary trace consumers (and notifiers) to present
        and track additional information in trace objects.

        Any modules which use this *should* initialize them
        on attach (so when they get re-used they're clean)

        Some examples of metadata used:
        ShouldBreak - We're expecting a non-signal related break
        ExitCode - The int() exit code  (if exited)
        PendingSignal - The current signal

        """
        self.metadata[name] = value

    def getMeta(self, name, default=None):
        """
        Get some metadata.  Metadata is a clean way for
        arbitrary trace consumers (and notifiers) to present
        and track additional information in trace objects.

        If you specify a default and the key doesn't exist, not
        not only will the default be returned, but the key will
        be set to the default specified.
        """
        if default is not None:
            if name not in self.metadata:
                self.metadata[name] = default
        return self.metadata.get(name, None)

    def hasMeta(self, name):
        """
        Check to see if a metadata key exists... Mostly un-necessary
        as getMeta() with a default will set the key to the default
        if non-existant.
        """
        return name in self.metadata

    def getMode(self, name, default=False):
        """
        Get the value for a mode setting allowing
        for a clean default...
        """
        return self.modes.get(name, default)

    def setMode(self, name, value):
        """
        Set a mode setting...  This is ONLY valid
        if that mode has been iniitialized with
        initMode(name, value).  Otherwise, it's an
        unsupported mode for this platform ;)  cute huh?
        This way, platform sections can cleanly setmodes
        and such.
        """
        if name not in self.modes:
            raise Exception("Mode %s not supported on this platform" % name)
        self.modes[name] = bool(value)

    def injectso(self, filename):
        """
        Inject a shared object into the target of the trace.  So, on windows
        this is easy with InjectDll and on *nix... it's.. fugly...

        NOTE: This method will likely cause the trace to run.  Do not call from
              within a notifier!
        """
        self.requireNotRunning()
        self.platformInjectSo(filename)

    def ps(self):
        """
        Return a list of proccesses which are currently running on the
        system.
        (pid, name)
        """
        return self.platformPs()

    def addBreakByExpr(self, symname, fastbreak=False):
        '''
        Add a breakpoint by resolving an expression.  This will create
        the Breakpoint object for you and add it to the trace.  It
        returns the newly created breakpoint id.

        Optionally, set fastbreak=True to have the breakpoint behave in
        "fast break" mode which automatically continues execution and does
        not fire notifiers for the breakpoint.

        Example: trace.addBreakByExpr('kernel32.CreateFileA + ecx')
        '''
        bp = Breakpoint(None, expression=symname)
        bp.fastbreak = fastbreak
        return self.addBreakpoint(bp)

    def addBreakByAddr(self, va, fastbreak=False):
        '''
        Add a breakpoint by address.  This will create the Breakpoint
        object for you and add it to the trace.  It returns the newly
        created breakpoint id.

        Optionally, set fastbreak=True to have the breakpoint behave in
        "fast break" mode which automatically continues execution and does
        not fire notifiers for the breakpoint.

        Example: trace.addBreakByAddr(0x7c770308)
        '''
        bp = Breakpoint(va)
        bp.fastbreak = fastbreak
        return self.addBreakpoint(bp)

    def addBreakpoint(self, breakpoint):
        """
        Add a breakpoint/watchpoint to the trace.  The "breakpoint" argument
        is a vtrace Breakpoint/Watchpoint object or something that extends it.

        To add a basic breakpoint use:
        trace.addBreakpoint(vtrace.Breakpoint(address))

        NOTE: expression breakpoints do *not* get evaluated in fastbreak mode

        This will return the internal ID given to the new breakpoint
        """
        breakpoint.inittrace(self)

        breakpoint.id = self.nextBpId()
        addr = breakpoint.resolveAddress(self)

        if addr is None:
            self.bpbyid[breakpoint.id] = breakpoint
            self.deferred.append(breakpoint)
            return breakpoint.id

        if addr in self.breakpoints:
            raise Exception("ERROR: Duplicate break for address 0x%.8x" % addr)

        self.bpbyid[breakpoint.id] = breakpoint
        self.breakpoints[addr] = breakpoint

        # fastbreaks are always active... (except when they're not...)
        if breakpoint.fastbreak:
            breakpoint.activate(self)

        return breakpoint.id

    def removeBreakpoint(self, id):
        """
        Remove the breakpoint with the specified ID
        """
        self.requireAttached()
        bp = self.bpbyid.pop(id, None)
        if bp is not None:
            bp.deactivate(self)
            if bp in self.deferred:
                self.deferred.remove(bp)
            else:
                self.breakpoints.pop(bp.address, None)

            # If the bp is also curbp, set curbp to None
            if self.curbp == bp:
                self.curbp = None

        # Remove cached breakpoint code
        Breakpoint.bpcodeobj.pop(id, None)

    def getCurrentBreakpoint(self):
        """
        Return the current breakpoint otherwise None
        """
        return self.curbp

    def getBreakpoint(self, id):
        """
        Return a reference to the breakpoint with the requested ID.

        NOTE: NEVER set locals or use things like setBreakpointCode()
        method on return'd breakpoint objects as they may be remote
        and would then be *coppies* of the bp objects. (use the trace's
        setBreakpointCode() instead).
        """
        return self.bpbyid.get(id)

    def getBreakpointByAddr(self, va):
        '''
        Return the breakpoint object (or None) for a given virtual address.
        '''
        return self.breakpoints.get(va)

    def getBreakpoints(self):
        """
        Return a list of the current breakpoints.
        """
        return list(self.bpbyid.values())

    def getBreakpointEnabled(self, bpid):
        """
        An accessor method for returning if a breakpoint is
        currently enabled.
        NOTE: code which wants to be remote-safe should use this
        """
        bp = self.getBreakpoint(bpid)
        if bp is None:
            raise Exception("Breakpoint %d Not Found" % bpid)
        return bp.isEnabled()

    def setBreakpointEnabled(self, bpid, enabled=True):
        """
        An accessor method for setting a breakpoint enabled/disabled.

        NOTE: code which wants to be remote-safe should use this
        """
        bp = self.getBreakpoint(bpid)
        if bp is None:
            raise Exception("Breakpoint %d Not Found" % bpid)
        if not enabled: # To catch the "disable" of fastbreaks...
            bp.deactivate(self)
        return bp.setEnabled(enabled)

    def setBreakpointCode(self, bpid, pystr):
        """
        Because breakpoints are potentially on the remote debugger
        and code is not pickleable in python, special access methods
        which takes strings of python code are necessary for the
        vdb interface to quick script breakpoint code.  Use this method
        to set the python code for this breakpoint.
        """
        bp = self.getBreakpoint(bpid)
        if bp is None:
            raise Exception("Breakpoint %d Not Found" % bpid)
        bp.setBreakpointCode(pystr)

    def getBreakpointCode(self, bpid):
        """
        Return the python string of user specified code that will run
        when this breakpoint is hit.
        """
        bp = self.getBreakpoint(bpid)
        if bp is not None:
            return bp.getBreakpointCode()
        return None

    def call(self, address, args, convention=None):
        """
        Setup the "stack" and call the target address with the following
        arguments.  If the argument is a string or a buffer, copy that into
        memory and hand in the argument.

        The current state of ALL registers are returned as a dictionary at the
        end of the call...

        Additionally, a "convention" string may be specified that the underlying
        platform may be able to interpret...
        """
        self.requireNotRunning()
        return self.platformCall(address, args, convention)

    def registerNotifier(self, event, notifier):
        """
        Register a notifier who will be called for various
        events.  See NOTIFY_* constants for handler hooks.
        """
        nlist = self.notifiers.get(event, None)
        if nlist:
            nlist.append(notifier)
        else:
            nlist = []
            nlist.append(notifier)
            self.notifiers[event] = nlist

    def deregisterNotifier(self, event, notifier):
        nlist = self.notifiers.get(event, [])
        if notifier in nlist:
            nlist.remove(notifier)

    def getNotifiers(self, event):
        return self.notifiers.get(event, [])

    def requireNotExited(self):
        '''
        Call in a method that requires the trace to have not exited.
        '''
        if self.exited:
            raise Exception('ERROR - Request invalid for trace which exited')

    def requireNotRunning(self):
        '''
        Call in a method that requires the debugger the be attached and not
        running.
        '''
        self.requireAttached()
        if self.isRunning():
            raise Exception('ERROR - trace is running; use "break" before running the specified command')

    def requireAttached(self):
        '''
        Call in a method that requires the debugger to be attached.
        '''
        if not self.attached:
            raise Exception('ERROR - attach to a process first')

    def getFds(self):
        """
        Get a list of (fd, type, bestname) pairs.  This is MOSTLY useful
        for HUMON consumtion...  or giving HUMONs consumption...
        """
        self.requireNotRunning()
        if not self.fds:
            self.fds = self.platformGetFds()
        return self.fds

    def getMemoryMaps(self):
        """
        Return a list of the currently mapped memory for the target
        process.  This is acomplished by calling the platform's
        platformGetMaps() mixin method.  This will also cache the
        results until CONTINUE.  The format is (addr, len, perms, file).
        """
        self.requireNotRunning()
        if not self.mapcache:
            self.mapcache = self.platformGetMaps()
        return self.mapcache

    def getMemoryFault(self):
        '''
        If the most receent event is a memory access error, this API will
        return a tuple of (<addr>, <perm>) on supported platforms.  Otherwise,
        a (None, None) will result.

        Example:
        import envi.memory as e_mem
        vaddr, vperm = trace.getMemoryFault()
        if vaddr is not None:
            print('Memory Fault At: 0x%.8x (perm: %d)' % (vaddr, vperm))
        '''
        return self.platformGetMemFault()

    def isAttached(self):
        '''
        Return true or false if this trace's target processing is attached.
        '''
        return self.attached

    def isRunning(self):
        '''
        Return true or false if this trace's target process is running.
        '''
        return self.running

    def hasExited(self):
        '''
        Return true or false if this trace's target process has exited.
        '''
        return self.exited

    def isRemote(self):
        '''
        Return true or false if this trace's target process is a CobraProxy
        object to a trace on another system.
        '''
        return False

    def enableAutoContinue(self, event):
        """
        Put the tracer object in to AutoContinue mode
        for the specified event.  To make all events
        continue running see RunForever mode in setMode().
        """
        if event not in self.auto_continue:
            self.auto_continue.append(event)

    def disableAutoContinue(self, event):
        """
        Disable Auto Continue for the specified
        event.
        """
        if event in self.auto_continue:
            self.auto_continue.remove(event)

    def getAutoContinueList(self):
        """
        Retrieve the list of vtrace notification events
        that will be auto-continued.
        """
        return list(self.auto_continue)

    def parseExpression(self, expression):
        """
        Parse a python expression with many useful helpers mapped
        into the execution namespace.

        Example: trace.parseExpression("ispoi(ecx+ntdll.RtlAllocateHeap)")
        """
        vlocs = VtraceExpressionLocals(self)
        return int(e_expr.evaluate(expression, vlocs))

    def sendBreak(self):
        """
        Send an asynchronous break signal to the target process.
        This is only valid if the target is actually running...
        """
        self.requireAttached()
        self.setMode("RunForever", False)
        self.setMeta("ShouldBreak", True)
        self.platformSendBreak()
        time.sleep(0.01)
        # If we're non-blocking, we gotta wait...
        if self.getMode("NonBlocking", True):
            while self.isRunning():
                time.sleep(0.01)

    def getStackTrace(self):
        """
        Returns a list of (instruction pointer, stack frame) tuples.
        If stack tracing results in an error, the error entry will
        be (-1, -1).  Otherwise most platforms end up with 0, 0 as
        the top stack frame
        """
        # FIXME thread id argument!
        return self.archGetStackTrace()

    def getThreads(self):
        """
        Get a dictionary of <threadid>:<tinfo> pairs where
        tinfo is platform dependant, but is typically either
        the top of the stack for that thread, or the TEB on
        win32
        """
        if not self.threadcache:
            self.threadcache = self.platformGetThreads()
        return self.threadcache

    def getCurrentThread(self):
        '''
        Return the thread id of the currently selected thread.
        '''
        return self.getMeta('ThreadId')

    def selectThread(self, threadid):
        """
        Set the "current thread" context to the given thread id.
        (For example stack traces and register values will depend
        on the current thread context).  By default the thread
        responsible for an "interesting event" is selected.
        """
        if threadid not in self.getThreads():
            raise Exception("ERROR: Invalid threadid chosen: %d" % threadid)
        self.requireNotRunning()
        self.platformSelectThread(threadid)
        self.setMeta("ThreadId", threadid)

    def isThreadSuspended(self, threadid):
        """
        Used to determine if a thread is suspended.
        """
        return self.sus_threads.get(threadid, False)

    def suspendThread(self, threadid):
        """
        Suspend a thread by ID.  This will mean that on continuing
        the trace, the suspended thread will not be scheduled.
        """
        self.requireNotRunning()
        if self.sus_threads.get(threadid):
            raise Exception("The specified thread is already suspended")
        if threadid not in self.getThreads().keys():
            raise Exception("There is no thread %d!" % threadid)
        self.platformSuspendThread(threadid)
        self.sus_threads[threadid] = True

    def resumeThread(self, threadid):
        """
        Resume a suspended thread.
        """
        self.requireNotRunning()
        if not self.sus_threads.get(threadid):
            raise Exception("The specified thread is not suspended")
        self.platformResumeThread(threadid)
        self.sus_threads.pop(threadid)

    def injectThread(self, pc):
        """
        Create a new thread inside the target process.  This thread
        will begin execution on the next process run().
        """
        self.requireNotRunning()
        #self.platformInjectThread(pc)
        pass

    def joinThread(self, threadid):
        '''
        Run the trace in a loop until the specified thread exits.
        '''
        self.setMode('RunForever', True)
        self._join_thread = threadid
        # Temporarily make run/wait blocking
        nb = self.getMode('NonBlocking')
        self.setMode('NonBlocking', False)
        self.run()
        self.setMode('NonBlocking', nb)

    def getStructNames(self, namespace=None):
        '''
        This method returns either the structure names, or
        the structure namespaces that the target tracer is aware
        of.  If "namespace" is specified, it is structures within
        that namespace, otherwise it is "known namespaces"

        Example: namespaces = trace.getStructNames()
                 ntdll_structs = trace.getStructNames(namespace='ntdll')
        '''
        if namespace:
            return self.vsbuilder.getVStructNames(namespace=namespace)
        return self.vsbuilder.getVStructNamespaceNames()

    def getStruct(self, sname, va=None):
        """
        Retrieve a vstruct structure optionally populated with memory from
        the specified address.  Returns a standard vstruct object.
        """
        # Check if we need to parse symbols for a library
        libbase = sname.split('.')[0]
        self._loadBinaryNorm(libbase)

        if self.vsbuilder.hasVStructNamespace(libbase):
            vs = self.vsbuilder.buildVStruct(sname)

        # FIXME this is deprecated and should die...
        else:
            vs = vstruct.getStructure(sname)

        if vs is None:
            return None

        if va is None:
            return vs

        bytez = self.readMemory(va, len(vs))
        vs.vsParse(bytez)
        return vs

    def setVariable(self, name, value):
        """
        Set a named variable in the trace which may be used in
        subsequent VtraceExpressions.

        Example:
        trace.setVariable("whereiam", trace.getProgramCounter())
        """
        self.localvars[name] = value

    def getVariable(self, name):
        """
        Get the value of a previously set variable name.
        (or None on not found)
        """
        return self.localvars.get(name)

    def getVariables(self):
        """
        Get the dictionary of named variables.
        """
        return dict(self.localvars)

    def hex(self, value):
        """
        Much like the python hex routine, except this will automatically
        pad the value's string length out to pointer width.
        """
        width = self.arch.getPointerSize()
        return e_bits.hex(value, width)

    def buildNewTrace(self):
        '''
        Build a new/clean trace "like" this one.  For platforms where a
        special trace was handed in, this allows initialization of a new one.
        For most implementations, this is very simple....

        Example:
            if need_another_trace:
                newt = trace.buildNewTrace()
        '''
        return self.__class__()

class TraceGroup(Notifier, v_util.TraceManager):
    """
    Encapsulate several traces, run them, and continue to
    handle their event notifications.
    """
    def __init__(self):
        Notifier.__init__(self)
        v_util.TraceManager.__init__(self)
        self.traces = {}
        self.go = True # A little ghetto switch for those who read the source

        # We are a notify all notifier by default
        self.registerNotifier(NOTIFY_ALL, self)

        self.setMode("NonBlocking", True)

    def setMeta(self, name, value):
        """
        A trace group's setMeta function will set "persistant" metadata
        which will be added again to any trace on attach.  Additionally,
        setting metadata on a tracegroup will cause all current traces
        to get the update as well....
        """
        v_util.TraceManager.setMeta(self, name, value)
        for trace in self.traces.values():
            trace.setMeta(name, value)

    def setMode(self, name, value):
        v_util.TraceManager.setMode(self, name, value)
        for trace in self.getTraces():
            trace.setMode(name, value)

    def detachAll(self):
        """
        Detach from ALL the currently targetd processes
        """
        for trace in self.traces.values():
            try:
                if trace.isRunning():
                    trace.sendBreak()
                trace.detach()
            except:
                pass

    def run(self):
        """
        Our run method  is a little different than a traditional
        trace. It will *never* block.
        """
        if len(self.traces.keys()) == 0:
            raise Exception("ERROR - can't run() with no traces!")

        for trace in self.traces.values():

            if trace.exited:
                self.traces.pop(trace.pid)
                trace.detach()
                continue

            if not trace.isRunning():
                trace.run()

    def execTrace(self, cmdline):
        trace = getTrace()
        self._initTrace(trace)
        trace.execute(cmdline)
        self.traces[trace.getPid()] = trace
        return trace

    def addTrace(self, proc):
        """
        Add a new tracer to this group the "proc" argument
        may be either an int for a pid (which we will attach
        to) or an already attached (and broken) tracer object.
        """
        if isinstance(proc, int):
            trace = getTrace()
            self._initTrace(trace)
            self.traces[proc] = trace
            try:
                trace.attach(proc)
            except:
                self.delTrace(proc)
                raise

        else:  # Hopefully a tracer object... if not.. you're dumb.
            trace = proc
            self._initTrace(trace)
            self.traces[trace.getPid()] = trace

        return trace

    def getTrace(self):
        '''
        Similar to vtrace.getTrace(), but also init's
        the trace for being managed by a TraceGroup.

        Example:
            tg = TraceGroup()
            t = tg.getTrace()
            t....
        '''
        t = getTrace()
        self.addTrace(t)
        return t

    def _initTrace(self, trace):
        """
         - INTERNAL -
        Setup a tracer object to be ready for being in this
        trace group (setup modes and notifiers).  Only addTrace()
        and execTrace() probably need to be aware of this.
        """
        self.manageTrace(trace)

    def delTrace(self, pid):
        """
        Remove a trace from the current TraceGroup
        """
        trace = self.traces.pop(pid, None)
        self.unManageTrace(trace)

    def getTraces(self):
        """
        Return a list of the current traces
        """
        return list(self.traces.values())

    def getTraceByPid(self, pid):
        """
        Return the the trace for process PID if we're
        already attached.  Return None if not.
        """
        return self.traces.get(pid, None)

    def notify(self, event, trace):
        # Remove this trace, and free it
        # on the server if present
        if event == NOTIFY_EXIT:
            self.delTrace(trace.getPid())

class VtraceExpressionLocals(e_expr.MemoryExpressionLocals):
    """
    A class which serves as the namespace dictionary during the
    evaluation of an expression on a tracer.
    """
    def __init__(self, trace):
        e_expr.MemoryExpressionLocals.__init__(self, trace, symobj=trace)
        self.trace = trace
        self.update({
            'trace': trace,
            'vtrace': vtrace
        })
        self.update({
            'frame': self.frame,
            'teb': self.teb,
            'bp': self.bp,
            'meta': self.meta,
            'go': self.go,
        })

    def __getitem__(self, name):

        # Check registers
        if self.trace.isAttached() and not self.trace.isRunning():

            regs = self.trace.getRegisters()
            r = regs.get(name, None)
            if r is not None:
                return r

        # Check local variables
        locs = self.trace.getVariables()
        r = locs.get(name, None)
        if r is not None:
            return r

        # Check the loaded libraries
        for lib in self.trace.getNormalizedLibNames():
            for sym in self.trace.getSymsForFile(lib):
                if str(sym) == name:
                    return sym

        return e_expr.MemoryExpressionLocals.__getitem__(self, name)

    def go(self):
        '''
        A shortcut for trace.runAgain() which may be used in
        breakpoint code (or similar even processors) to begin
        execution again after event processing...
        '''
        self.trace.runAgain()

    def frame(self, index):
        """
        Return the address of the saved base pointer for
        the specified frame.

        Usage: frame(<index>)
        """
        stack = self.trace.getStackTrace()
        return stack[index][1]

    def teb(self, threadnum=None):
        """
        The expression teb(threadid) will return whatever the
        platform stores as the int for threadid.  In the case
        of windows, this is the TEB, others may be the thread
        stack base or whatever.  If threadid is left out, it
        uses the threadid of the current thread context.
        """
        if threadnum is None:
            # Get the thread ID of the current Thread Context
            threadnum = self.trace.getMeta("ThreadId")

        teb = self.trace.getThreads().get(threadnum, None)
        if teb is None:
            raise Exception("ERROR - Unknown Thread Id %d" % threadnum)

        return teb

    def bp(self, bpid):
        """
        The expression bp(0) returns the resolved address of the given
        breakpoint
        """
        bp = self.trace.getBreakpoint(bpid)
        if bp is None:
            raise Exception("Unknown Breakpoint ID: %d" % bpid)
        return bp.resolveAddress(self.trace)

    def meta(self, name):
        """
        An expression friendly (terse) way to get trace metadata
        (equiv to trace.getMeta(name))

        Example: meta("foo")
        """
        return self.trace.getMeta(name)

def reqTargOpt(opts, targ, opt, valstr='<value>'):
    val = opts.get( opt )
    if val is None:
        raise Exception('Target "%s" requires option: %s=%s' % (targ, opt, valstr))
    return val

def getTrace(target=None, **kwargs):
    """
    Return a tracer object appropriate for this platform.
    This is the function you will use to get a tracer object
    with the appropriate ancestry for your host.

    ex. mytrace = vtrace.getTrace()


    NOTE: Use the release() method on the tracer once debugging
          is complete.  This releases the tracer thread and allows
          garbage collection to function correctly.

    Some specialized tracers may be constructed by specifying the "target"
    name from one of the following list.  Additionally, each "specialized"
    tracer may require additional kwargs (which are listed).


    Examples:
        # A tracer for *this* os
        t = vtrace.getTrace()

        # A tracer for the gdbstub debugging a vmware 32bit hypervisor
        t = vtrace.getTrace(target='vmware32', host='localhost', port=8832)

    Targets:

    Alpha Targets:

    vmware32    -
        host=<host>     ( probably 'localhost' )
        port=<port>     ( probably 8832 )

    """
    if target == 'gdbserver':

        host = reqTargOpt(kwargs, 'gdbserver', 'host', '<host>')
        port = reqTargOpt(kwargs, 'gdbserver', 'port', '<port>')
        arch = reqTargOpt(kwargs, 'gdbserver', 'arch', '<i386|amd64|arm>')
        plat = reqTargOpt(kwargs, 'gdbserver', 'plat', '<windows|linux>')

        if arch not in ('i386', 'amd64', 'arm'):
            raise Exception('Invalid arch specified for "gdbserver" target: %s' % arch)

        if plat not in ('windows', 'linux'):
            raise Exception('Invalid plat specified for "gdbserver" target: %s' % plat)

    if target == 'vmware32':

        import vtrace.platforms.vmware as vt_vmware

        host = reqTargOpt(kwargs, 'vmware32', 'host', '<host>')
        port = int( reqTargOpt(kwargs, 'vmware32', 'port', '<port>') )

        plat = 'windows'

        #plat = reqTargOpt(kwargs, 'vmware32', 'plat', '<windows|linux>')
        #if plat not in ('windows', 'linux'):
            #raise Exception('Invalid plat specified for "vmware32" target: %s' % plat)

        return vt_vmware.VMWare32WindowsTrace( host=host, port=port )

    if remote: #We have a remote server!
        return getRemoteTrace()

    # From here down, we're trying to build a trace for *this* platform!

    os_name = platform.system().lower() # Like "linux", "darwin","windows"
    arch = envi.getCurrentArch()

    if os_name == "linux":
        import vtrace.platforms.linux as v_linux
        if arch == "amd64":
            return v_linux.LinuxAmd64Trace()

        elif arch == "i386":
            return v_linux.Linuxi386Trace()

        # Keep separate just in case
        elif arch == "armv7l":
            return v_linux.LinuxArmTrace()

        elif arch == "armv6l":
            return v_linux.LinuxArmTrace()

        else:
            raise Exception("Sorry, no linux support for %s" % arch)

    elif os_name == "freebsd":

        import vtrace.platforms.freebsd as v_freebsd

        if arch == "i386":
            return v_freebsd.FreeBSDi386Trace()

        elif arch == "amd64":
            return v_freebsd.FreeBSDAmd64Trace()

        else:
            raise Exception("Sorry, no FreeBSD support for %s" % arch)

    elif os_name == "sunos5":
        raise Exception("Solaris needs porting!")
        #import vtrace.platforms.posix as v_posix
        #import vtrace.platforms.solaris as v_solaris
        #ilist.append(v_posix.PosixMixin)
        #if arch == "i386":
            #import vtrace.archs.intel as v_intel
            #ilist.append(v_intel.i386Mixin)
            #ilist.append(v_solaris.SolarisMixin)
            #ilist.append(v_solaris.Solarisi386Mixin)

    elif os_name == "darwin":

        #if 9 not in os.getgroups():
            #print 'You MUST be in the procmod group....'
            #print 'Use: sudo dscl . append /Groups/procmod GroupMembership invisigoth'
            #print '(put your username in there unless you want to put me in too... ;)'
            #raise Exception('procmod group membership required')
        if os.getuid() != 0:
            logger.error('For NOW you *must* be root.  There are some crazy MACH perms...')
            raise Exception('You must be root for now (on OSX)....')

        logger.warning('Also... the darwin port is not even REMOTELY working yet.  Solid progress though...')

        #'sudo dscl . append /Groups/procmod GroupMembership invisigoth'
        #'sudo dscl . read /Groups/procmod GroupMembership'
        import vtrace.platforms.darwin as v_darwin
        if arch == 'i386':
            return v_darwin.Darwini386Trace()
        elif arch == 'amd64':
            return v_darwin.DarwinAmd64Trace()
        else:
            raise Exception('Darwin not supported on %s (only i386...)' % arch)

    elif os_name in ['microsoft', 'windows']:

        import vtrace.platforms.win32 as v_win32

        if arch == "i386":
            return v_win32.Windowsi386Trace()

        elif arch == "amd64":
            return v_win32.WindowsAmd64Trace()

        else:
            raise Exception("Windows with arch %s is not supported!" % arch)

    else:

        raise Exception("ERROR - OS %s not supported yet" % os_name)

def interact(pid=0, server=None, trace=None):

    """
    Just a cute and dirty way to get a tracer attached to a pid
    and get a python interpreter instance out of it.
    """

    global remote
    remote = server

    if trace is None:
        trace = getTrace()
        if pid:
            trace.attach(pid)

    mylocals = {}
    mylocals["trace"] = trace

    code.interact(local=mylocals)

def getEmu(trace, arch=envi.ARCH_DEFAULT):
    '''
    See comment for emulator from trace (in envitools); does not set any
    registers or mem.

    TODO: this really belongs in envitools, or somewhere else, but putting it
    in envitools causes a circular import problem due to the TraceEmulator.
    '''
    if arch == envi.ARCH_DEFAULT:
        arch_name = trace.getMeta('Architecture')
    else:
        arch_name = envi.getArchById(trace.arch)

    arch_mod = envi.getArchModule(arch_name)
    emu = arch_mod.getEmulator()
    return emu
