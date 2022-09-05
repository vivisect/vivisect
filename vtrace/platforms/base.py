"""
Tracer Platform Base
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import os
import queue
import logging
import platform
import traceback
import threading

import vtrace
import envi.const as e_const
import envi.threads as e_threads
import envi.symstore.resolver as e_sym_resolv

import vstruct.builder as vs_builder

logger = logging.getLogger(__name__)

class TracerBase(vtrace.Notifier):
    """
    The basis for a tracer's internals.  All platformFoo/archFoo
    functions are defaulted, and internal state is initialized.
    Additionally, a number of internal utilities are housed here.
    """
    def __init__(self):
        """
        The routine to initialize a tracer's initial internal state.  This
        is used by the initial creation routines, AND on attaches/executes
        to re-fresh the state of the tracer.
        WARNING: This will erase all metadata/symbols (modes/notifiers are kept)
        """
        vtrace.Notifier.__init__(self)

        self.pid = 0  # Attached pid (also used to know if attached)
        self.exited = False
        self.breakpoints = {}
        self.newbreaks = []
        self.bpbyid = {}
        self.bpid = 0
        self.curbp = None
        self.bplock = threading.Lock()
        self.deferred = []
        self.running = False
        self.runagain = False
        self.attached = False
        # A cache for memory maps and fd listings
        self.mapcache = None
        self.thread = None  # our proxy thread...
        self.threadcache = None
        self.fds = None
        self.signal_ignores = []
        self.localvars = {}

        # Set if we are RunForever until a thread exit...
        self._join_thread = None
        self._break_after_bp = True     # Do we stop on the instruction *after* the bp?
        self._bp_saved = {}             # Store the saved bytes from breakpoint mem writes

        self.symcache = None            # Set by setSymCachePath()
        self.vsbuilder = vs_builder.VStructBuilder()

        self.psize = self.getPointerSize() # From the envi arch mod...

        # Track which libraries are parsed, and their
        # normame to full path mappings
        self.libloaded = {} # True if the library has been loaded already
        self.libpaths = {}  # normname->filename and filename->normname lookup

        # Set up some globally expected metadata
        self.setMeta('PendingSignal', None)
        self.setMeta('SignalInfo', None)
        self.setMeta("IgnoredSignals", [])
        self.setMeta("LibraryBases", {})  # name -> base address mappings for binaries
        self.setMeta("LibraryPaths", {})  # base -> path mappings for binaries
        self.setMeta("ThreadId", 0)  # If you *can* have a thread id put it here
        self.setMeta("BadMaps", [])  # Maps like [vvar] on linux that we can't read from normally
        plat = platform.system().lower()
        rel  = platform.release().lower()
        self.setMeta("Platform", plat)
        self.setMeta("Release", rel)

        # Use this if we are *expecting* a break
        # which is caused by us (so we remove the
        # SIGBREAK from pending_signal
        self.setMeta("ShouldBreak", False)

    def nextBpId(self):
        self.bplock.acquire()
        x = self.bpid
        self.bpid += 1
        self.bplock.release()
        return x

    def _justAttached(self, pid):
        # Used by the top level Trace after platform routines
        self.pid = pid
        self.attached = True
        self.breakpoints = {}
        self.bpbyid = {}
        self.setMeta("PendingSignal", None)
        self.setMeta("ExitCode", 0)
        self.exited = False

    def getResolverForFile(self, filename):
        res = self.resbynorm.get(filename, None)
        if res:
            return res
        res = self.resbyfile.get(filename, None)
        if res:
            return res
        return None

    def steploop(self):
        """
        Continue stepi'ing in a loop until shouldRunAgain()
        returns false (like RunForever mode or something)
        """
        if self.getMode("NonBlocking", False):
            e_threads.firethread(self.doStepLoop)()
        else:
            self.doStepLoop()

    def doStepLoop(self):
        go = True
        while go:
            self.stepi()
            go = self.shouldRunAgain()

    def _doRun(self):
        # Exists to avoid recursion from loop in doWait

        fastbreak = False
        if self.curbp:
            fastbreak = self.curbp.fastbreak

        # If we are on a breakpoint, and it's a fastbreak
        # we don't want to fire a "continue" event.
        if not fastbreak:
            self.fireNotifiers(vtrace.NOTIFY_CONTINUE)

        # Step past a breakpoint if we are on one.
        self._checkForBreakpoint()

        # Throw down and activate breakpoints...
        if not fastbreak:
            self._activBreakpoints()

        self.runagain = False
        self._syncRegs()    # Must be basically last...
        self.platformContinue()

        self.running = True
        self.setMeta("PendingSignal", None)

    def wait(self):
        """
        Wait for the trace target to have
        something happen...   If the trace is in
        NonBlocking mode, this will fire a thread
        to wait for you and return control immediately.
        """
        if self.getMode("NonBlocking"):
            e_threads.firethread(self._doWait)()
            return
        self._doWait()

    def _doWait(self):
        doit = True
        while doit:
            # A wrapper method for wait() and the wait thread to use
            self.setMeta('SignalInfo', None)
            self.setMeta('PendingSignal', None)
            event = self.platformWait()
            self.running = False
            self.platformProcessEvent(event)
            doit = self.shouldRunAgain()
            if doit:
                self._doRun()

    def _fireSignal(self, signo, siginfo=None):
        self.setMeta('PendingSignal', signo)
        self.setMeta('SignalInfo', siginfo)
        self.fireNotifiers(vtrace.NOTIFY_SIGNAL)

    def _fireExit(self, ecode):
        self.setMeta('ExitCode', ecode)
        self.fireNotifiers(vtrace.NOTIFY_EXIT)

    def _fireExitThread(self, threadid, ecode):
        self.setMeta('ExitThread', threadid)
        self.setMeta('ExitCode', ecode)
        self.fireNotifiers(vtrace.NOTIFY_EXIT_THREAD)

    def _clearBreakpoints(self):
        '''
        Cleanup all breakpoints (if the current bp is "fastbreak" this routine
        will not be called...
        '''
        for bp in self.breakpoints.values():
            if bp.active:
                # only effects active breaks
                bp.deactivate(self)

    def _activBreakpoints(self):

        """
        Run through the breakpoints and setup
        the ones that are enabled.

        NOTE: This should *not* get called when continuing
        from a fastbreak...
        """

        # Resolve deferred breaks
        for bp in self.deferred:
            addr = bp.resolveAddress(self)
            if addr is not None:
                self.deferred.remove(bp)
                self.breakpoints[addr] = bp

        for bp in self.breakpoints.values():
            if bp.isEnabled():
                bp.activate(self)

    def _syncRegs(self):
        """
        Sync the reg-cache into the target process
        """
        if self.regcache is not None:
            for tid, ctx in self.regcache.items():
                if ctx.isDirty():
                    self.platformSetRegCtx(tid, ctx)
        self.regcache = None

    def _cacheRegs(self, threadid):
        """
        Make sure the reg-cache is populated
        """
        if self.regcache is None:
            self.regcache = {}
        ret = self.regcache.get(threadid)
        if ret is None:
            ret = self.platformGetRegCtx(threadid)
            ret.setIsDirty(False)
            self.regcache[threadid] = ret
        return ret

    def _checkForBreakpoint(self):
        """
        Check to see if we've landed on a breakpoint, and if so
        deactivate and step us past it.

        WARNING: Unfortunatly, cause this is used immidiatly before
        a call to run/wait, we must block briefly even for the GUI
        """
        # Steal a reference because the step should
        # clear curbp...
        bp = self.curbp
        if bp is not None and bp.isEnabled():
            if bp.active:
                bp.deactivate(self)
            orig = self.getMode("FastStep")
            self.setMode("FastStep", True)
            self.stepi()
            self.setMode("FastStep", orig)
            bp.activate(self)

        self.curbp = None

    def shouldRunAgain(self):
        """
        A unified place for the test as to weather this trace
        should be told to run again after reaching some stopping
        condition.
        """
        if not self.attached:
            return False

        if self.exited:
            return False

        if self.getMode("RunForever"):
            return True

        if self.runagain:
            return True

        return False

    def __repr__(self):
        run = "stopped"
        exe = "None"
        if self.isRunning():
            run = "running"
        elif self.exited:
            run = "exited"
        exe = self.getMeta("ExeName")
        return "[%d]\t- %s <%s>" % (self.pid, exe, run)

    def initMode(self, name, value, descr):
        """
        Initialize a mode, this should ONLY be called
        during setup routines for the trace!  It determines
        the available mode setings.
        """
        self.modes[name] = bool(value)
        self.modedocs[name] = descr

    def release(self):
        """
        Do cleanup when we're done.  This is mostly necessary
        because of the thread proxy holding a reference to this
        tracer...  We need to let him die off and try to get
        garbage collected.
        """
        if self.thread:
            self.thread.go = False

    def _cleanupResources(self):
        self._tellThreadExit()

    def _tellThreadExit(self):
        if self.thread is not None:
            self.thread.queue.put(None)
            self.thread.join(timeout=2)
            self.thread = None

    def __del__(self):
        if not self._released:
            logger.warning('Warning! tracer del w/o release()!')

    def fireTracerThread(self):
        # Fire the threadwrap proxy thread for this tracer
        # (if it hasnt been fired...)
        if self.thread is None:
            self.thread = TracerThread()

    def fireNotifiers(self, event):
        '''
        Fire the registered notifiers for the NOTIFY_* event.
        '''
        if event == vtrace.NOTIFY_SIGNAL:
            signo = self.getCurrentSignal()
            if signo in self.getMeta('IgnoredSignals', []):
                logger.debug('Ignoring %s', signo)
                self.runAgain()
                return

        alllist = self.getNotifiers(vtrace.NOTIFY_ALL)
        nlist = self.getNotifiers(event)

        trace = self
        # if the trace has a proxy it's notifiers
        # need that, cause we can't be pickled ;)
        if self.proxy:
            trace = self.proxy

        # First we notify ourself....
        self.handleEvent(event, self)

        # The "NOTIFY_ALL" guys get priority
        for notifier in alllist:
            try:
                notifier.handleEvent(event, trace)
            except:
                logger.error('Notifier exception for %s', notifier)
                logger.error(traceback.format_exc())

        for notifier in nlist:
            try:
                notifier.handleEvent(event, trace)
            except:
                logger.error('Notifier exception for %s', notifier)
                logger.error(traceback.format_exc())

    def _fireStep(self):
        if self.getMode('FastStep', False):
            return
        self.fireNotifiers(vtrace.NOTIFY_STEP)

    def _fireBreakpoint(self, bp):

        self.curbp = bp
        bp.deactivate(self)

        try:
            bp.notify(vtrace.NOTIFY_BREAK, self)
        except Exception as msg:
            logger.error("Breakpoint Exception 0x%.8x : %s", bp.address, msg)
            logger.error(traceback.format_exc())

        # "stealthbreak" bp's do not NOTIFY *or* run again
        if bp.stealthbreak:
            # No notifiers *and* no run-again
            return

        # Neither "stealth" nor "fast" breaks trigger notifiers
        if not bp.fastbreak and not bp.stealthbreak:
            self.fireNotifiers(vtrace.NOTIFY_BREAK)

        # "fast" breaks automatically continue execution
        if bp.fastbreak:
            self.runagain = True

    def checkPageWatchpoints(self):
        """
        Check if the given memory fault was part of a valid
        MapWatchpoint.
        """
        faultaddr,faultperm = self.platformGetMemFault()

        # FIXME this is some AWESOME but intel specific nonsense
        if faultaddr is None:
            return False
        faultpage = faultaddr & 0xfffff000

        wp = self.breakpoints.get(faultpage, None)
        if wp is None:
            return False

        self._fireBreakpoint(wp)

        return True

    def checkWatchpoints(self):
        # Check for hardware watchpoints
        waddr = self.archCheckWatchpoints()
        if waddr is not None:
            wp = self.breakpoints.get(waddr, None)
            if wp:
                self._fireBreakpoint(wp)
                return True

    def checkBreakpoints(self):
        """
        This is mostly for systems (like linux) where you can't tell
        the difference between some SIGSTOP/SIGBREAK conditions and
        an actual breakpoint instruction.

        This method will return true if either the breakpoint
        subsystem or the sendBreak (via ShouldBreak meta) is true
        (and it will have handled firing events for the bp)
        """
        pc = self.getProgramCounter()
        if self._break_after_bp:
            bi = self.archGetBreakInstr()
            pc -= len(bi)

        bp = self.breakpoints.get(pc, None)

        if bp:
            addr = bp.getAddress()
            if self._break_after_bp:
                # Step back one instruction to account break
                self.setProgramCounter(addr)
            self._fireBreakpoint(bp)
            return True

        if self.getMeta("ShouldBreak"):
            self.setMeta("ShouldBreak", False)
            self.fireNotifiers(vtrace.NOTIFY_BREAK)
            return True

        return False

    def notify(self, event, trace):
        '''
        We are frequently a notifier for ourselves, so we can do things
        like handle events on attach and on break in a unified fashion.
        '''
        self.threadcache = None
        self.mapcache = None
        self.fds = None
        self.running = False

        if event in self.auto_continue:
            self.runAgain()

        # For thread exits, make sure the tid
        # isn't in 
        if event == vtrace.NOTIFY_EXIT_THREAD:
            tid = self.getMeta("ThreadId")
            self.sus_threads.pop(tid, None)
            # Check if this is a thread we were waiting on.
            if tid == self._join_thread:
                self._join_thread = None
                # Turn off the RunForever in joinThread()
                self.setMode('RunForever', False)
                # Either way, we don't want to run again...
                self.runAgain(False)

        # Do the stuff we do for detach/exit or
        # cleanup breaks etc...
        if event == vtrace.NOTIFY_ATTACH:
            pass

        elif event == vtrace.NOTIFY_DETACH:
            for tid in self.sus_threads.keys():
                self.resumeThread(tid)
            self._clearBreakpoints()

        elif event == vtrace.NOTIFY_EXIT:
            self.setMode("RunForever", False)
            self.exited = True
            self.attached = False

        elif event == vtrace.NOTIFY_CONTINUE:
            self.runagain = False

        else:
            self._clearBreakpoints()

    def delLibraryBase(self, baseaddr):

        libname = self.getMeta("LibraryPaths").get(baseaddr, "unknown")
        normname = self.normFileName(libname)

        self.setMeta("LatestLibrary", libname)
        self.setMeta("LatestLibraryNorm", normname)

        self.fireNotifiers(vtrace.NOTIFY_UNLOAD_LIBRARY)

        self.getMeta("LibraryBases").pop(normname, None)
        self.getMeta("LibraryPaths").pop(baseaddr, None)

        self.delSymByName(normname)

    def addLibraryBase(self, libname, address, always=False):
        """
        This should be used *at load time* to setup the library
        event metadata.

        This *must* be called from a context where it's safe to
        fire notifiers, because it will fire a notifier to alert
        about a LOAD_LIBRARY. (This means *not* from inside another
        notifer)
        """

        self.setMeta("LatestLibrary", None)
        self.setMeta("LatestLibraryNorm", None)

        normname = self.normFileName(libname)
        if self.getSymByName(normname) is not None:
            normname = "%s_%.8x" % (normname, address)

        self.getMeta("LibraryPaths")[address] = libname
        self.getMeta("LibraryBases")[normname] = address
        self.setMeta("LatestLibrary", libname)
        self.setMeta("LatestLibraryNorm", normname)

        # Only actually do library work with a file or force
        if os.path.exists(libname) or always:

            width = self.arch.getPointerSize()
            sym = e_sym_resolv.FileSymbol(normname, address, 0, width=width)
            sym.casesens = self.casesens
            self.addSymbol(sym)

        self.libpaths[normname] = libname
        self.fireNotifiers(vtrace.NOTIFY_LOAD_LIBRARY)

    def normFileName(self, libname):
        basename = os.path.basename(libname)
        return basename.split(".")[0].split("-")[0].lower()

    def _findLibraryMaps(self, magic, always=False):
        # A utility for platforms which lack library load
        # notification through the operating system
        bmaps = self.getMeta("BadMaps", [])
        done = {}
        mlen = len(magic)

        for addr, size, perms, fname in self.getMemoryMaps():
            if not fname:
                continue

            if done.get(fname):
                continue

            if fname in bmaps:
                continue
            try:

                if self.readMemory(addr, mlen) == magic:
                    done[fname] = True
                    self.addLibraryBase(fname, addr, always=always)

            except Exception as e:
                logger.warning('findLibraryMaps(0x%x, %d, %s, %s) hit exception: %s', addr, size, perms, fname, e)

    def _loadBinaryNorm(self, normname):
        if not self.libloaded.get(normname, False):
            fname = self.libpaths.get(normname)
            if fname is not None:
                self._loadBinary(fname)
                return True
        return False

    def _loadBinary(self, filename):
        """
        Check if a filename has yet to be parsed.  If it has NOT
        been parsed, parse it and return True, otherwise, return False
        """
        normname = self.normFileName(filename)
        if not self.libloaded.get(normname, False):
            address = self.getMeta("LibraryBases").get(normname)
            if address is None:
                return False

            self.platformParseBinary(filename, address, normname)
            self.libloaded[normname] = True
            return True
        return False

    def _simpleCreateThreads(self):
        '''
        Fire a thread event for each of the current threads.
        (for use by tracers which don't get help from the OS)
        '''
        initid = self.getMeta('ThreadId')
        for tid in self.platformGetThreads().keys():
            self.setMeta('ThreadId', tid)
            self.fireNotifiers(vtrace.NOTIFY_CREATE_THREAD)
        self.setMeta('ThreadId', initid)

#######################################################################
#
# NOTE: all platform/arch defaults are populated here.
#
    def platformGetThreads(self):
        """
        Return a dictionary of <threadid>:<tinfo> pairs where tinfo is either
        the stack top, or the teb for win32
        """
        raise Exception("Platform must implement platformGetThreads()")

    def platformSelectThread(self, thrid):
        """
        Platform implementers are encouraged to use the metadata field "ThreadId"
        as the identifier (int) for which thread has "focus".  Additionally, the
        field "StoppedThreadId" should be used in instances (like win32) where you
        must specify the ORIGINALLY STOPPED thread-id in the continue.
        """
        self.setMeta("ThreadId", thrid)

    def platformSuspendThread(self, thrid):
        raise Exception("Platform must implement platformSuspendThread()")

    def platformResumeThread(self, thrid):
        raise Exception("Platform must implement platformResumeThread()")

    def platformInjectThread(self, pc, arg=0):
        raise Exception("Platform must implement platformInjectThread()")

    def platformKill(self):
        raise Exception("Platform must implement platformKill()")

    def platformExec(self, cmdline):
        """
        Platform exec will execute the process specified in cmdline
        and return the PID
        """
        raise Exception("Platmform must implement platformExec")

    def platformInjectSo(self, filename):
        raise Exception("Platform must implement injectso()")

    def platformGetFds(self):
        """
        Return what getFds() wants for this particular platform
        """
        raise Exception("Platform must implement platformGetFds()")

    def platformGetSignal(self):
        '''
        Return the currently posted exception/signal....
        '''
        # Default to the thing they all should do...
        return self.getMeta('PendingSignal', None)

    def platformSetSignal(self, sig=None):
        '''
        Set the current signal to deliver to the process on cont.
        (Use None for no signal delivery.
        '''
        self.setMeta('PendingSignal', sig)

    def platformGetMaps(self):
        """
        Return a list of the memory maps where each element has
        the following structure:
        (address, length, perms, file="")
        NOTE: By Default this list is available as Trace.maps
        because the default implementation attempts to populate
        them on every break/stop/etc...
        """
        raise Exception("Platform must implement GetMaps")

    def platformPs(self):
        """
        Actually return a list of tuples in the format
        (pid, name) for this platform
        """
        raise Exception("Platform must implement Ps")

    def archGetStackTrace(self):
        raise Exception("Architecure must implement argGetStackTrace()!")

    def archAddWatchpoint(self, address, size=4, perms="rw"):
        """
        Add a watchpoint for the given address.  Raise if the platform
        doesn't support, or too many are active...
        """
        raise Exception("Architecture doesn't implement watchpoints!")

    def archRemWatchpoint(self, address):
        raise Exception("Architecture doesn't implement watchpoints!")

    def archCheckWatchpoints(self):
        """
        If the current register state indicates that a watchpoint was hit,
        return the address of the watchpoint and clear the event.  Otherwise
        return None
        """
        pass

    def archActivBreakpoint(self, addr):
        '''
        Default implementation simply uses archGetBreakInstr() and writes it
        to memory ( and saves off the old bytes ).
        '''
        b = self.archGetBreakInstr()
        self._bp_saved[ addr ] = self.readMemory( addr, len(b) )
        self.writeMemory( addr, b )

    def archClearBreakpoint(self, addr):
        b = self._bp_saved.pop( addr )
        self.writeMemory( addr, b )

    def archGetRegCtx(self):
        """
        Return a new empty envi.registers.RegisterContext object for this
        trace.
        """
        raise Exception("Platform must implement archGetRegCtx()")

    def getStackTrace(self):
        """
        Return a list of the stack frames for this process
        (currently Intel/ebp based only).  Each element of the
        "frames list" consists of another list which is (eip,ebp)
        """
        raise Exception("Platform must implement getStackTrace()")

    def getExe(self):
        """
        Get the full path to the main executable for this
        *attached* Trace
        """
        return self.getMeta("ExeName","Unknown")

    def platformAttach(self, pid):
        """
        Actually carry out attaching to a target process.  Like
        platformStepi this is expected to be ATOMIC and not return
        until a complete attach.
        """
        raise Exception("Platform must implement platformAttach()")

    def platformContinue(self):
        raise Exception("Platform must implement platformContinue()")

    def platformDetach(self):
        """
        Actually perform the detach for this type
        """
        raise Exception("Platform must implement platformDetach()")

    def platformStepi(self):
        """
        PlatformStepi should be ATOMIC, meaning it gets called, and
        by the time it returns, you're one step further.  This is completely
        regardless of blocking/nonblocking/whatever.
        """
        raise Exception("Platform must implement platformStepi!")

    def platformCall(self, address, args, convention=None):
        """
        Platform call takes an address, and an array of args
        (string types will be mapped and located for you)

        platformCall is expected to return a dicionary of the
        current register values at the point where the call
        has returned...
        """
        raise Exception("Platform must implement platformCall")

    def platformGetRegCtx(self, threadid):
        raise Exception("Platform must implement platformGetRegCtx!")

    def platformSetRegCtx(self, threadid, ctx):
        raise Exception("Platform must implement platformSetRegCtx!")

    def platformProtectMemory(self, va, size, perms):
        raise Exception("Plaform does not implement protect memory")

    def platformAllocateMemory(self, size, perms=e_const.MM_RWX, suggestaddr=0):
        raise Exception("Plaform does not implement allocate memory")

    def platformReadMemory(self, address, size):
        raise Exception("Platform must implement platformReadMemory!")

    def platformWriteMemory(self, address, bytes):
        raise Exception("Platform must implement platformWriteMemory!")

    def platformGetMemFault(self):
        """
        Return the addr of the current memory fault
        or None
        """
        #NOTE: This is used by the PageWatchpoint subsystem
        # (and is still considered experimental)
        return None,None

    def platformWait(self):
        """
        Wait for something interesting to occur and return a
        *platform specific* representation of what happened.

        This will then be passed to the platformProcessEvent()
        method which will be responsible for doing things like
        firing notifiers.  Because the platformWait() method needs
        to be commonly @threadwrap and you can't fire notifiers
        from within a threadwrapped function...
        """
        raise Exception("Platform must implement platformWait!")

    def platformProcessEvent(self, event):
        """
        This method processes the event data provided by platformWait()

        This method is responsible for firing ALL notifiers *except*:

        vtrace.NOTIFY_CONTINUE - This is handled by the run api (and isn't the result of an event)
        """
        raise Exception("Platform must implement platformProcessEvent")

    def platformOpenFile(self, filename):
        # Open a file for reading
        # TODO: make contextmanager
        return open(filename, 'rb')

    def platformReadFile(self, path):
        '''
        Abstract away reading file bytes to allow wire/remote cases.
        '''
        with open(path, 'rb') as f:
            bytez = f.read()
        return bytez

    def platformListDir(self, path):
        return os.listdir(path)

    def platformParseBinary(self, filename, baseaddr, normname):
        """
        Platforms must parse the given binary file and load any symbols
        into the internal SymbolResolver using self.addSymbol()
        """
        raise Exception("Platform must implement platformParseBinary")

    def platformRelease(self):
        '''
        Called back on release.
        '''
        pass

def threadwrap(func):
    def trfunc(self, *args, **kwargs):
        if threading.currentThread().__class__ == TracerThread:
            return func(self, *args, **kwargs)
        # Proxy the call through a single thread
        q = queue.Queue()
        # FIXME change calling convention!
        args = (self, ) + args
        self.thread.queue.put((func, args, kwargs, q))
        ret = q.get()
        if issubclass(ret.__class__, Exception):
            raise ret
        return ret
    return trfunc

class TracerThread(threading.Thread):
    """
    Ok... so here's the catch... most debug APIs do *not* allow
    one thread to do the attach and another to do continue and another
    to do wait... they just dont.  So there.  I have to make a thread
    per-tracer (on most platforms) and proxy requests (for *some* trace
    API methods) to it for actual execution.  SUCK!

    However, this lets async things like GUIs and threaded things like
    cobra not have to be aware of which one is allowed and not allowed
    to make particular calls and on what platforms...  YAY!
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.setDaemon(True)
        self.start()

    def run(self):
        """
        Run in a circle getting requests from our queue and
        executing them based on the thread.
        """
        while True:
            try:
                qobj = self.queue.get()
                if qobj is None:
                    break
                meth, args, kwargs, queue = qobj
                try:
                    queue.put(meth(*args, **kwargs))
                except Exception as e:
                    queue.put(e)
                    logger.warning(traceback.format_exc())
                    continue
            except Exception:
                logger.warning(traceback.format_exc())
