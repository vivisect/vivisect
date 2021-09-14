import os
import re
import sys
import shlex
import pprint
import signal
import logging
import binascii
import threading
import traceback
from queue import Queue
from collections import defaultdict, UserDict

from cmd import *
from struct import *
from getopt import getopt

import vtrace
import vtrace.util as v_util
import vtrace.snapshot as vs_snap
import vtrace.notifiers as v_notif

import vdb
import vdb.stalker as v_stalker
import vdb.extensions as v_ext

import envi
import envi.cli as e_cli
import envi.bits as e_bits
import envi.common as e_common
import envi.config as e_config
import envi.memory as e_memory
import envi.symstore.resolver as e_resolv

import vstruct.primitives as vs_prims


logger = logging.getLogger(__name__)
vdb.basepath = vdb.__path__[0] + '/'

class VdbLookup(UserDict):
    '''
    Used for lookups by key or value.
    '''
    def __init__(self, initdict=None):
        UserDict.__init__(self)
        if initdict is None:
            return

        for key, val in initdict.items():
            self.__setitem__(self, key, val)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        UserDict.__setitem__(self, item, key)

class ScriptThread(threading.Thread):
    def __init__(self, cobj, locals):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.cobj = cobj
        self.locals = locals

    def run(self):
        try:
            exec(self.cobj, self.locals)
        except Exception as e:
            logger.warning('Script Error: %s', e)

def setupBreakOnEntry(trace):
    '''
    Sets a one time breakpoint at the __entry symbol. Removes itself as a
    notifier after a single NOTIFY_BREAK event.
    '''
    exefile = trace.normFileName(trace.getExe())
    exesym = trace.getSymByName(exefile)
    if exesym is not None:
        entrySym = exesym.getSymByName('__entry')
        if entrySym is not None:
            entrySymExpr = '%s.__entry' % (exefile,)
            otb = vtrace.OneTimeBreak(None, expression=entrySymExpr)
            trace.addBreakpoint(otb)

class VdbTrace:
    """
    Used to hand thing that need a persistant reference to a trace
    when using vdb to manage tracers.
    """
    def __init__(self, db):
        self.db = db

    def attach(self, pid):
        # Create a new tracer for the debugger and attach.
        trace = self.db.newTrace()
        trace.attach(pid)

    # Take over all notifier registration
    def registerNotifier(self, event, notif):
        self.db.registerNotifier(event, notif)

    def deregisterNotifier(self, event, notif):
        self.db.deregisterNotifier(event, notif)

    #FIXME should we add modes to this?

    def selectThread(self, threadid):
        #FIXME perhaps a thread selected LOCAL event?
        trace = self.db.getTrace()
        trace.selectThread(threadid)
        self.db.fireLocalNotifiers(vtrace.NOTIFY_BREAK, trace)

    def __getattr__(self, name):
        return getattr(self.db.getTrace(), name)

defconfig = {

    'vdb':{
        'BreakOnEntry':False,
        'BreakOnMain':False,

        'SymbolCacheActive':True,
        'SymbolCachePath':e_config.gethomedir('.envi','symcache'),

        'KillOnQuit': False,
    },

    'cli':{
        'verbose':False,
        'aliases': {
            '<f1>':'stepi',
            '<f2>':'go -I 1',
            '<f5>':'go',
        }
    },

}

docconfig = {
    'vdb':{
        'BreakOnMain':'Should the debugger break on main() if known?',
        'BreakOnEntry':'Should the debugger break on the entry to the main module? (only works if you exec (and not attach to) the process)',

        'SymbolCacheActive':'Should we cache symbols for subsequent loads?',
        'SymbolCachePaths':'Path elements ( ; seperated) to search/cache symbols (filepath,cobra)',
    }
}

class WrapExcThread(threading.Thread):
    '''
    Places the return value or exception information into a queue that can
    be checked by the caller.
    If the method calls exit(), then nothing will be in the queue.
    '''
    def __init__(self, target=None, args=tuple(), kwargs={}):
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            retval = self.target(*self.args, **self.kwargs)
            self.queue.put((retval,))
        except Exception as e:
            tb = traceback.format_exc()
            self.queue.put((e, tb))

class Vdb(e_cli.EnviMutableCli, v_notif.Notifier, v_util.TraceManager):
    '''
    A VDB object is a debugger object which may be used to embed full
    debugger like functionality into a python application.  The
    Vdb object contains a CLI impelementation which extends envi.cli>
    '''

    def __init__(self, trace=None):
        v_notif.Notifier.__init__(self)
        v_util.TraceManager.__init__(self)

        self._extensions = {}
        self._ext_ctxmenu_hooks = {}

        if trace is None:
            trace = vtrace.getTrace()

        arch = trace.getMeta('Architecture')
        self.arch = envi.getArchModule(arch)

        self.bpcmds = {}
        self.waitlib = None
        self.difftracks = {}

        self.runcache = {}
        self.runcachectors = {}

        self.server = None
        self.autoscript = None

        self.runagain = False           # A one-time thing for the cli
        self.windows_jit_event = None

        # We hang on to an opcode renderer instance
        self.opcoderend = None

        # If a VdbGui instance is present it will set this.
        self.gui = None

        self.setMode('NonBlocking', True)

        self.manageTrace(trace)
        self.registerNotifier(vtrace.NOTIFY_ALL, self)

        # FIXME if config verbose
        #self.registerNotifier(vtrace.NOTIFY_ALL, vtrace.VerboseNotifier())

        self.vdbhome = e_config.gethomedir('.vdb')

        # Load up the config
        cfgfile = os.path.join(self.vdbhome, 'vdb.json')
        self.config = e_config.EnviConfig(filename=cfgfile, defaults=defconfig)

        self.setupSignalLookups()

        # Ok... from here down we're handing everybody the crazy
        # on-demand-resolved trace object.
        trace = vdb.VdbTrace(self)
        e_cli.EnviMutableCli.__init__(self, trace, self.config, symobj=trace)

        self.prompt = 'vdb > '
        self.banner = 'Welcome To VDB!\n'
        self.addScriptPathEnvVar('VDB_SCRIPT_PATH')

        self.loadDefaultRenderers(trace)
        self.loadExtensions(trace)

    def addCtxMenuHook(self, name, handler):
        '''
        Extensions can add Context Menu hooks to modify the menu as they wish.
        This would most often happen from the Extension's vivExtension() init function.
        see vivisect.qt.ctxmenu for more details

        handler should have the following prototype (inc. example code):


        from vqt.common import ACT
        def myExtCtxMenuHandler(vw, menu):
            toymenu = menu.addMenu('myToys')
            toymenu.addAction('Voodoo Wizbang ZeroDay Finder Thingy', ACT(doCoolShit, vw, va))

        Currently, this should live in a loaded module, not in your Viv Extension's main py file.
        '''
        self._ext_ctxmenu_hooks[name] = handler

    def delCtxMenuHook(self, name):
        '''
        Remove a context-menu hook that has been installed by an extension
        '''
        self._ext_ctxmenu_hooks.pop(name, None)

    def addExtension(self, name, extmod):
        '''
        Add extension module to a list of extensions.
        This keeps a list of installed extension modules, with the added value
        of keeping the loaded module in memory.
        '''
        self._extensions[name] = extmod

    def delExtension(self, name):
        '''
        Remove's extension module from the list of extensions.
        '''
        self._extensions.pop(name, None)

    def addRunCacheCtor(self, name, ctor):
        '''
        Add a "run cache constructor" which will be used if a RunCacheVar
        is requested that is not currently cached.  *All* RunCacheVar
        entries are flushed automagically on run...

        ( Allows db caching of critical structs likely to be parsed
          more than once by extensions )
        '''
        self.runcachectors[name] = ctor

    def getRunCacheVar(self, cname):
        '''
        Retrieve a variable from the vdb "runcache".  If not currently
        cached, the object will be constructed and added to the cache
        so that future references are fast.
        '''
        ret = self.runcache.get(cname)
        if ret is None:
            ret = self.runcachectors.get(cname)(self)
            self.runcache[cname] = ret
        return ret

    def loadDefaultRenderers(self, trace):
        import envi.memcanvas.renderers as e_render
        import vdb.renderers as v_rend
        # FIXME check endianness
        self.canvas.addRenderer("bytes", e_render.ByteRend())
        self.canvas.addRenderer("u_int_16", e_render.ShortRend())
        self.canvas.addRenderer("u_int_32", e_render.LongRend())
        self.canvas.addRenderer("u_int_64", e_render.QuadRend())
        self.opcoderend = v_rend.OpcodeRenderer(self.trace)
        self.canvas.addRenderer("asm", self.opcoderend)

        stackrend = v_rend.StackRenderer(self.trace)
        self.canvas.addRenderer('Stack View', stackrend)
        drend = v_rend.DerefRenderer(self.trace)
        self.canvas.addRenderer("Deref View", drend)
        srend = v_rend.SymbolRenderer(self.trace)
        self.canvas.addRenderer('Symbols View', srend)

        for arch in envi.getArchModules():
            if arch is None: # The "empty" default...
                continue
            archid = arch.getArchId()
            archname = arch.getArchName()

            archrend = v_rend.OpcodeRenderer( self.trace, arch=archid)
            self.canvas.addRenderer('asm - %s' % archname, archrend)

    def verror(self, msg, addnl=True):
        if addnl:
            msg += "\n"
        sys.stderr.write(msg)

    def fatalError(self, exception):
        '''
        Used for platform exceptions.  This indicates something in the
        underlying platform failed and continuing to debug is probably not a
        good idea.
        '''
        self.vprint('%s: %s' % ('FATAL ERROR (you probably should restart session', exception))

    def vdbUIEvent(self, event, einfo=None):
        '''
        Fire a UI event (mostly used by the GUI to force refresh)

        Do *not* fire this API in a tight loop, rather, fire once when
        changes are complete.

        NOTE: Events should only be created for notification on
              events *not* already emitted by the tracer.
        '''
        if self.gui is not None:
            self.gui.vdbUIEvent(event, einfo)

    def loadExtensions(self, trace):
        """
        Load up any extensions which are relevant for the current tracer's
        platform/arch/etc...
        """
        v_ext.loadExtensions(self, trace)

    def getTrace(self):
        return self.trace

    def newTrace(self):
        """
        Generate a new trace for this vdb instance.  This fixes many of
        the new attach/exec data munging issues because tracer re-use is
        *very* sketchy...
        """
        oldtrace = self.getTrace()
        if oldtrace.isRunning():
            oldtrace.sendBreak()
        if oldtrace.isAttached():
            oldtrace.detach()

        self.trace = oldtrace.buildNewTrace()
        oldtrace.release()

        self.bpcmds = {}
        self.manageTrace(self.trace)
        return self.trace

    def setupSignalLookups(self):
        self.siglookup = VdbLookup()

        self.siglookup[0] = 'None'

        for name in dir(signal):
            if name[:3] == 'SIG' and '_' not in name:
                self.siglookup[name] = getattr(signal, name)

    def getSignal(self, sig):
        """
        If given an int, return the name, for a name, return the int ;)
        """
        return self.siglookup.get(sig,None)

    def parseExpression(self, exprstr):
        return self.trace.parseExpression(exprstr)

    def getExpressionLocals(self):
        trace = vdb.VdbTrace(self)
        r = vtrace.VtraceExpressionLocals(trace)
        r['db'] = self
        r['vprint'] = self.vprint
        return r

    def reprPointer(self, address):
        """
        Return a string representing the best known name for
        the given address
        """
        if not address:
            return "NULL"

        # Do we have a symbol?
        sym = self.trace.getSymByAddr(address, exact=False)
        if sym is not None:
            return "%s + %d" % (repr(sym),address-int(sym))

        # Check if it's a thread's stack
        for tid,tinfo in self.trace.getThreads().items():
            ctx = self.trace.getRegisterContext(tid)
            sp = ctx.getStackCounter()

            smap = self.trace.getMemoryMap(sp)
            if not smap:
                continue

            stack,size,perms,fname = smap
            if address >= stack and address < (stack+size):
                off = address - sp
                op = "+"
                if off < 0:
                    op = "-"
                off = abs(off)
                return "tid:%d sp%s%s (stack)" % (tid,op,off)

        map = self.trace.getMemoryMap(address)
        if map:
            return map[3]

        return "Who knows?!?!!?"

    def notify(self, event, trace):

        pid = trace.getPid()
        tid = trace.getCurrentThread()

        # Any kind of event resets the runcache
        self.runcache = {}

        if event == vtrace.NOTIFY_ATTACH:
            self.vprint("Attached to : %d" % pid)
            self.waitlib = None
            self.difftracks = {}

            if self.windows_jit_event:
                trace._winJitEvent(self.windows_jit_event)
                self.windows_jit_event = None

            # Initialize the tracer's symbol cache path
            if self.config.vdb.SymbolCacheActive:
                trace.setSymCachePath(self.config.vdb.SymbolCachePath)

            # only respect BreakOnEntry if we exec'd something
            if self.config.vdb.BreakOnEntry and trace.hasMeta('ExecCommand'):
                self.runagain = True # skip initial break

            if self.autoscript:
                self.do_script(self.autoscript)

        elif event == vtrace.NOTIFY_CONTINUE:
            pass

        elif event == vtrace.NOTIFY_STEP:
            pass

        elif event == vtrace.NOTIFY_DETACH:
            self.difftracks = {}
            self.vprint("Detached from %d" % pid)

        elif event == vtrace.NOTIFY_SIGNAL:
            # FIXME move all this code into a bolt on notifier!
            thr = trace.getCurrentThread()
            signo = trace.getCurrentSignal()

            self.vprint("Process Recieved Signal %d (0x%.8x) (Thread: %d (0x%.8x))" % (signo, signo, thr, thr))

            faddr,fperm = trace.getMemoryFault()
            if faddr is not None:
                accstr = e_memory.getPermName(fperm)
                self.vprint('Memory Fault: addr: 0x%.8x perm: %s' % (faddr, accstr))

        elif event == vtrace.NOTIFY_BREAK:
            trace.setMeta('PendingBreak', False)
            bp = trace.getCurrentBreakpoint()
            if bp:
                self.vprint("Thread: %d Hit Break: %s" % (tid, repr(bp)))
                cmdstr = self.bpcmds.get(bp.id, None)
                if cmdstr is not None:
                    self.onecmd(cmdstr)

            else:
                self.vprint("Thread: %d NOTIFY_BREAK" % tid)

                if self.runagain: # One-time run-again behavior (for cli option)
                    if self.config.vdb.BreakOnEntry:
                        setupBreakOnEntry(trace)

                    trace.runAgain()
                    self.runagain = False

        elif event == vtrace.NOTIFY_EXIT:
            ecode = trace.getMeta('ExitCode')
            self.vprint("PID %d exited: %d (0x%.8x)" % (pid,ecode,ecode))

        elif event == vtrace.NOTIFY_LOAD_LIBRARY:
            self.vprint("Loading Binary: %s" % trace.getMeta("LatestLibrary",None))
            if self.waitlib is not None:
                normname = trace.getMeta('LatestLibraryNorm', None)
                if self.waitlib == normname:
                    self.waitlib = None
                    trace.runAgain(False)

        elif event == vtrace.NOTIFY_UNLOAD_LIBRARY:
            self.vprint("Unloading Binary: %s" % trace.getMeta("LatestLibrary",None))

        elif event == vtrace.NOTIFY_CREATE_THREAD:
            self.vprint("New Thread: %d" % tid)

        elif event == vtrace.NOTIFY_EXIT_THREAD:
            ecode = trace.getMeta("ExitCode", 0)
            self.vprint("Exit Thread: %d (ecode: 0x%.8x (%d))" % (tid,ecode,ecode))

        elif event == vtrace.NOTIFY_DEBUG_PRINT:
            s = "<unknown>"
            win32 = trace.getMeta("Win32Event", None)
            if win32:
                s = win32.get("DebugString", "<unknown>")
            self.vprint("DEBUG PRINT: %s" % s)

        else:
            self.vprint('unhandled event: %d' % event)

    ###################################################################
    #
    # All CLI extension commands start here
    #

    # FIXME this is duplicate, but... PUNT...
    def do_writemem(self, args):
        """
        Over-write some memory in the target address space.
        Usage: writemem [options] <addr expression> <string>
        -X    The specified string is in hex (ie 414141 = AAA)
        -U    The specified string needs to be unicode in mem (AAA -> 410041004100)
        """
        dohex = False
        douni = False

        try:
            argv = e_cli.splitargs(args)
            opts,args = getopt(argv, "XU")
        except:
            return self.do_help("writemem")

        if len(args) != 2:
            return self.do_help("writemem")

        for opt,optarg in opts:
            if opt == "-X":
                dohex = True
            elif opt == "-U":
                douni = True

        exprstr, memstr = args
        if dohex:
            memstr = binascii.unhexlify(memstr)
        if douni:
            memstr = ("\x00".join(memstr)) + "\x00"

        addr = self.parseExpression(exprstr)
        self.memobj.writeMemory(addr, memstr)
        self.vdbUIEvent('vdb:writemem', (addr,memstr))

    def do_vstruct(self, line):
        """
        List the available structure modules and optionally
        structure definitions from a particular module in the
        current vstruct.

        Usage: vstruct [modname]
        """
        if len(line) == 0:
            self.vprint("\nVStruct Namespaces:")
            plist = self.trace.getStructNames()
        else:
            self.vprint("\nKnown Structures (from %s):" % line)
            plist = self.trace.getStructNames(namespace=line)

        plist.sort()
        for n in plist:
            self.vprint(str(n))

        self.vprint("\n")

    def do_dis(self, line):
        """
        Print out the opcodes for a given address expression

        Usage: dis <address expression> [<size expression>]
        """

        argv = e_cli.splitargs(line)

        size = 20
        argc = len(argv)
        if argc == 0:
            addr = self.trace.getProgramCounter()
        else:
            addr = self.parseExpression(argv[0])

        if argc > 1:
            size = self.parseExpression(argv[1])

        self.vprint("Dissassembly:")
        self.canvas.renderMemory(addr, size, rend=self.opcoderend)

    def do_var(self, line):
        """
        Set a variable in the expression parsing context.  This allows
        for scratchspace names (python compatable names) to be used in
        expressions.

        Usage: var <name> <addr_expression>

        NOTE: The address expression *must* resolve at the time you set it.
        """
        t = self.trace

        if len(line):
            argv = e_cli.splitargs(line)
            if len(argv) == 1:
                return self.do_help("var")
            name = argv[0]
            expr = " ".join(argv[1:])
            addr = t.parseExpression(expr)
            t.setVariable(name, addr)

        varz = t.getVariables()
        self.vprint("Current Variables:")
        if not varz:
            self.vprint("None.")
        else:
            vnames = varz.keys()
            vnames.sort()
            for n in vnames:
                val = varz.get(n)
                if isinstance(val, int):
                    self.vprint("%20s = 0x%.8x" % (n, val))
                else:
                    rstr = repr(val)
                    if len(rstr) > 30:
                        rstr = rstr[:30] + '...'
                    self.vprint("%20s = %s" % (n, rstr))

    def do_alloc(self, args):
        """
        Allocate a chunk of memory in the target process.  It will be
        allocated with rwx permissions.

        Usage: alloc <size expr>
        """
        if len(args) == 0:
            return self.do_help("alloc")
        t = self.trace
        #argv = e_cli.splitargs(args)
        try:
            size = t.parseExpression(args)
            base = t.allocateMemory(size)
            self.vprint("Allocated %d bytes at: 0x%.8x" % (size, base))
        except Exception as e:
            logger.error(traceback.format_exc())
            self.vprint("Allocation Error: %s" % e)

    def do_autoscript(self, line):
        '''
        Tell vdb to run a python script on every process attach.

        Usage: autoscript <scriptfile>|clear
        '''
        argv = e_cli.splitargs(line)
        if len(argv) != 1:
            self.vprint('Current Autoscript: %s' % self.autoscript)
            return

        if argv[0] == 'clear':
            self.vprint('clearing autoscript: %s' % self.autoscript)
            return

        if not os.path.isfile(argv[0]):
            self.vprint('Error: %s is not a valid file' % argv[0])
            return

        self.autoscript = argv[0]

    def do_memload(self, line):
        '''
        Load a file into memory. (straight mapping, no parsing)

        Usage: memload <filename>
        '''
        argv = e_cli.splitargs(line)
        if len(argv) != 1:
            return self.do_help('memload')

        fname = argv[0]
        if not os.path.isfile(fname):
            self.vprint('Invalid File: %s' % fname)
            return

        with open(fname, 'rb') as f:
            fbytes = f.read()
        memva = self.trace.allocateMemory(len(fbytes))
        self.trace.writeMemory(memva, fbytes)

        self.vprint('Loaded At: 0x%.8x (%d bytes)' % (memva, len(fbytes)))

    def do_struct(self, line):
        '''
        Show and optionally apply a vstruct definition to memory.
        Use the 'vstruct' command to find and display a structure of interest.

        Usage: struct <vstruct name> [memory expression]
        '''
        argv = shlex.split(line)
        if len(argv) not in (1, 2):
            return self.do_help('struct')

        clsname = argv[0]
        expr = None
        va = None
        if len(argv) == 2:
            expr = argv[1]
            va = self.trace.parseExpression(expr)

        sinfo = self.trace.getStruct(clsname, va=va)
        if sinfo is None:
            self.vprint('%s not found.' % clsname)
            return

        # yuck.
        if len(argv) == 1:
            va = 0

        stree = sinfo.tree(va=va)
        self.vprint(stree)

    def do_signal(self, args):
        """
        Show the current pending signal/exception code.

        Usage: signal
        """
        # FIXME -i do NOT pass the signal on to the target process.
        t = self.trace
        t.requireAttached()
        cursig = t.getCurrentSignal()
        if cursig is None:
            self.vprint('No Pending Signals/Exceptions!')
        else:
            self.vprint("Current signal: %d (0x%.8x)" % (cursig, cursig))

    def do_snapshot(self, line):
        """
        Take a process snapshot of the current (stopped) trace and
        save it to the specified file.

        Usage: snapshot <filename>
        """
        if len(line) == 0:
            return self.do_help("snapshot")
        alist = e_cli.splitargs(line)
        if len(alist) != 1:
            return self.do_help("snapshot")

        t = self.trace
        t.requireAttached()
        self.vprint("Taking Snapshot...")
        snap = vs_snap.takeSnapshot(t)
        self.vprint("Saving To File")
        snap.saveToFile(alist[0])
        self.vprint("Done")
        snap.release()

    def do_ignore(self, args):
        """
        Add the specified signal id (exception id for windows) to the ignored
        signals list for the current trace.  This will make the smallest possible
        performance impact for that particular signal but will also not alert
        you that it has occured.

        Usage: ignore [options] [-c | <sigcode>...]
        -d - Remove the specified signal codes.
        -c - Include the *current* signal in the sigcode list
        -C - Clear the list of ignored signals

        Example: ignore -c # Ignore the currently posted signal
                 ignore -d 0x80000001 # Remove 0x80000001 from the ignores
        """
        argv = e_cli.splitargs(args)
        try:
            opts,args = getopt(argv, 'Ccd')
        except Exception as e:
            return self.do_help('ignore')

        remove = False
        sigs = []

        for opt,optarg in opts:
            if opt == '-c':
                sig = self.trace.getCurrentSignal()
                if sig is None:
                    self.vprint('No current signal to ignore!')
                    return
                sigs.append(sig)
            elif opt == '-C':
                self.vprint('Clearing ignore list...')
                self.trace.setMeta('IgnoredSignals', [])
            elif opt == '-d':
                remove = True

        for arg in args:
            sigs.append(self.trace.parseExpression(arg))

        for sig in sigs:
            if remove:
                self.vprint('Removing: 0x%.8x' % sig)
                self.trace.delIgnoreSignal(sig)
            else:
                self.vprint('Adding: 0x%.8x' % sig)
                self.trace.addIgnoreSignal(sig)

        ilist = self.trace.getMeta("IgnoredSignals")
        self.vprint("Currently Ignored Signals/Exceptions:")
        for x in ilist:
            self.vprint("0x%.8x (%d)" % (x, x))

    def do_exec(self, cmd):
        """
        Execute a program with the given command line and
        attach to it.
        Usage: exec </some/where and some args>
        """
        t = self.newTrace()
        t.execute(cmd)

    def do_threads(self, line):
        """
        List the current threads in the target process or select
        the current thread context for the target tracer.
        Usage: threads [thread id]
        """
        self.trace.requireNotRunning()
        if self.trace.isRunning():
            self.vprint("Can't list threads while running!")
            return

        if len(line) > 0:
            thrid = int(line, 0)
            self.trace.selectThread(thrid)
            self.vdbUIEvent('vdb:setthread', thrid)

        self.vprint("Current Threads:")
        self.vprint("[thrid] [thrinfo]  [pc]")

        curtid = self.trace.getMeta("ThreadId")
        for tid, tinfo in self.trace.getThreads().items():
            a = " "
            if tid == curtid:
                a = "*"

            sus = ""
            if self.trace.isThreadSuspended(tid):
                sus = "(suspended)"
            ctx = self.trace.getRegisterContext(tid)
            pc = ctx.getProgramCounter()
            self.vprint("%s%6d 0x%.8x 0x%.8x %s" % (a, tid, tinfo, pc, sus))

    def do_suspend(self, line):
        """
        Suspend a thread.

        Usage: suspend <-A | <tid>[ <tid>...]>
        """
        argv = e_cli.splitargs(line)
        try:
            opts,args = getopt(argv, "A")
        except Exception as e:
            return self.do_help("suspend")

        for opt,optarg in opts:
            if opt == "-A":
                # hehe...
                args = [str(tid) for tid in self.trace.getThreads().keys()]

        if not len(args):
            return self.do_help("suspend")

        for arg in args:
            tid = int(arg)
            self.trace.suspendThread(tid)
            self.vprint("Suspended Thread: %d" % tid)

    def do_restart(self, line):
        '''
        Restart the current process.

        Usage: restart

        NOTE: This only works if the process was exec'd to begin with!

        TODO: Plumb options for persisting bp's etc...
        '''
        t = self.trace
        cmdline = t.getMeta('ExecCommand')
        if cmdline is None:
            self.vprint('This trace was not fired with exec! (cannot restart)')
            return

        if t.isRunning():
            t.setMode("RunForever", False)
            t.sendBreak()

        if t.isAttached():
            t.kill()

        t = self.newTrace()
        t.execute(cmdline)

    def do_resume(self, line):
        """
        Resume a thread.

        Usage: resume <-A | <tid>[ <tid>...]>
        """
        argv = e_cli.splitargs(line)
        try:
            opts,args = getopt(argv, "A")
        except Exception as e:
            return self.do_help("suspend")

        for opt,optarg in opts:
            if opt == "-A":
                # hehe...
                args = [str(tid) for tid in self.trace.getThreads().keys()]

        if not len(args):
            return self.do_help("resume")

        for arg in args:
            tid = int(arg)
            self.trace.resumeThread(tid)
            self.vprint("Resumed Thread: %d" % tid)

    #def do_inject(self, line):

    def do_mode(self, args):
        """
        Set modes in the tracers...
        mode Foo=True/False
        """
        if args:
            mode,val = args.split("=")
            newmode = eval(val)
            self.setMode(mode, newmode)
        else:
            for key,val in self.trace.modes.items():
                self.vprint("%s -> %d" % (key,val))

    def do_reg(self, args):
        """
        Show the current register values.  Additionally, you may specify
        name=<expression> to set a register

        Usage: reg [regname=vtrace_expression]
        """
        if len(args):

            if args.find("=") == -1:
                return self.do_help("reg")

            regname,expr = args.split("=", 1)
            val = self.trace.parseExpression(expr)
            self.trace.setRegisterByName(regname, val)
            self.vprint("%s = 0x%.8x" % (regname, val))
            self.vdbUIEvent('vdb:setregs')
            return

        regs = self.trace.getRegisters()
        rnames = list(regs.keys())
        rnames.sort()
        final = []
        for r in rnames:
            # Capitol names are used for reg vals that we don't want to see
            # (by default)
            if r.lower() != r:
                continue
            val = regs.get(r)
            vstr = e_bits.hex(val, 4)
            final.append(("%12s:0x%.8x (%d)" % (r,val,val)))
        self.columnize(final)

    def complete_reg(self, text, line, bigidx, endidx):

        if '=' in line:
            return []

        regs = self.trace.getRegisters().keys()
        if not text:
            return regs

        if text in regs:
            return [ text + '=' ]

        return [ i for i in regs if i.startswith(text) ]

    def do_stepi(self, line):
        """
        Single step the target tracer.
        Usage: stepi [ options ]

        -A <addr>  - Step to <addr>
        -B         - Step past the next branch instruction
        -C <count> - Step <count> instructions
        -R         - Step to return from this function
        -V         - Show operand values during single step (verbose!)
        -U         - Remainder of args is "step until" expression (stop on True)
        -Q         - Do not output to canvas
        """
        t = self.trace
        argv = e_cli.splitargs(line)
        try:
            opts,args = getopt(argv, "A:BC:RVUQ")
        except Exception as e:
            return self.do_help("stepi")

        until = None
        count = None
        taddr = None
        toret = False
        tobrn = False
        showop = False
        quiet = False

        for opt, optarg in opts:

            if opt == '-A':
                taddr = t.parseExpression(optarg)

            elif opt == '-B':
                tobrn = True

            elif opt == '-C':
                count = t.parseExpression(optarg)

            elif opt == '-R':
                toret = True

            elif opt == '-V':
                showop = True

            elif opt == '-U':
                until = ' '.join(args)

            elif opt == '-Q':
                quiet = True

        if ( count is None 
             and taddr is None
             and until is None
             and toret == False 
             and tobrn == False):
            count = 1

        oldmode = self.getMode('FastStep')
        self.setMode('FastStep', True)

        hits = 0
        depth = 0
        try:
            while True:

                pc = t.getProgramCounter()

                try:
                    if pc == taddr:
                        break

                    op = t.parseOpcode(pc)

                    sym = t.getSymByAddr(pc)

                    if sym is not None and not quiet:
                        self.canvas.addVaText(repr(sym), pc)
                        self.canvas.addText(':\n')

                    if not quiet:
                        self.canvas.addText('  ' * max(depth,0))
                        self.canvas.addVaText('0x%.8x' % pc, pc)
                        self.canvas.addText(':  ')
                        op.render(self.canvas)

                    # these options are really mutually exclusive
                    if showop and not quiet:
                        self.canvas.addText(' ; ')
                        for oper in op.opers:
                            try:
                                val = oper.getOperValue(op, emu=t)
                                self.canvas.addText('0x%.8x ' % val)
                            except Exception as e:
                                self.canvas.addText(str(e))

                    if not quiet:
                        self.canvas.addText('\n')

                    if op.iflags & envi.IF_CALL:
                        depth += 1

                    elif op.iflags & envi.IF_RET:
                        depth -= 1
                except Exception as e:
                    print("[E@0x%x] %r" % (pc, e))


                tid = t.getCurrentThread()

                t.stepi()

                if until and t.parseExpression(until):
                    break

                # If we get an event from a different thread, get out!
                if t.getCurrentThread() != tid:
                    break

                # Break out if we have returned from the current function
                if toret and depth < 0:
                    break

                if depth < 0:
                    depth = 0

                hits += 1

                # If we have passed a conditional branch...
                if tobrn == True and hits != 0:

                    if op.iflags & envi.IF_CALL:
                        break

                    if op.iflags & envi.IF_RET:
                        break

                    getout = False
                    for bva, bflags in op.getBranches():
                        if bflags & envi.BR_COND:
                            getout = True
                            break
                    if getout:
                        break


                if count is not None and hits >= count:
                    break

                if t.getCurrentSignal() is not None:
                    break

                if t.getMeta('PendingSignal'):
                    break

        finally:
            self.setMode('FastStep', oldmode)
            # We ate all the events, tell things we have updated...
            t.fireNotifiers(vtrace.NOTIFY_STEP)

    def do_stepo(self, line):
        '''
        Step over current instruction.
        Executes the current instruction unless it is a procedure call.
        If it is a procedure call, sets a breakpoint on the instruction after
        the call.
        '''
        op = self.trace.parseOpcode(self.trace.getProgramCounter())
        if not op.isCall():
            self.trace.stepi()
        else:
            # should we make this like stepout?
            bp = vtrace.breakpoints.OneTimeBreak(op.va + op.size)
            self.trace.addBreakpoint(bp)
            self.trace.run()

    def do_stepout(self, line):
        '''
        Step out of the current function. (stepi or stepover until return)
        Single step (stepping over procedure calls) until a return
        instruction. Breaks on the return instruction.

        Usage: stepout [options]
        -V  verbose, print step instructions. (much slower)
        '''
        args = shlex.split(line)
        verbose = False
        if len(args) not in (0, 1):
            return self.do_help('stepout')

        if len(args) == 1:
            if '-V' != args[0]:
                return self.do_help('stepout')
            verbose = True

        nb = self.trace.getMode('NonBlocking')
        self.trace.setMode('NonBlocking', False)

        fs = self.trace.getMode('FastStep')
        self.trace.setMode('FastStep', True)

        tid = self.trace.getCurrentThread()
        waitva = None
        try:
            while True:
                op = self.trace.parseOpcode(self.trace.getProgramCounter())
                if op.isReturn():
                    break

                if self.trace.getCurrentSignal() is not None:
                    self.vprint('do_stepout: received signal, stopping')
                    break

                if self.trace.getMeta('PendingSignal'):
                    self.vprint('do_stepout: pending signal, stopping')
                    break

                if self.trace.getCurrentThread() != tid:
                    self.vprint('do_stepout: event from different thread, stopping')
                    break

                if op.isCall():
                    waitva = op.va + op.size
                    self.trace.run(until=waitva)

                    continue

                if verbose:
                    self.do_stepi('')
                else:
                    self.trace.stepi()

        except Exception as e:
            self.vprint('do_stepout: exception %s, stopping' % (str(e)))
        finally:
            self.trace.setMode('NonBlocking', nb)
            self.trace.setMode('FastStep', fs)

            # make sure waitva is gone
            bpid = self.trace.getBreakpointByAddr(waitva)
            if bpid is not None:
                self.trace.removeBreakpoint(bpid)

            self.trace.fireNotifiers(vtrace.NOTIFY_STEP)

    def do_go(self, line):
        '''
        Continue the target tracer.
        -I go icount linear instructions forward (step over style)
        -U go *out* of fcount frames (step out style)
        <until addr> go until explicit address

        Usage: go [-U <fcount> | -I <icount> | <until addr expression>]
        '''
        until = None
        icount = None
        fcount = None

        argv = e_cli.splitargs(line)
        try:
            opts, args = getopt(argv, 'U:I:')
        except:
            return self.do_help('go')

        for opt, optarg in opts:
            if opt == '-U':
                if len(optarg) == 0: return self.do_help('go')
                fcount = self.trace.parseExpression(optarg)
            elif opt == '-I':
                if len(optarg) == 0: return self.do_help('go')
                icount = self.trace.parseExpression(optarg)

        if icount is not None:
            addr = self.trace.getProgramCounter()
            for i in range(icount):
                addr += len(self.trace.parseOpcode(addr))

            until = addr

        elif fcount is not None:
            until = self.trace.getStackTrace()[fcount][0]

        elif len(args):
            until = self.trace.parseExpression(' '.join(args))

        if not until:
            self.vprint("Running Tracer (use 'break' to stop it)")

        self.trace.run(until=until)

    def do_gui(self, line):
        '''
        Attempt to spawn the VDB gui.
        '''
        if self.gui is not None:
            self.vprint('Gui already running!')
            return

        import vqt.main as vq_main
        import vdb.qt.main as vdb_q_main
        import vqt.colors as vq_colors

        vq_main.startup(css=vq_colors.qt_matrix)
        qgui = vdb_q_main.VdbWindow(self)
        qgui.show()

        vq_main.main()

    def do_waitlib(self, line):
        '''
        Run the target process until the specified library
        (by normalized name such as 'kernel32' or 'libc')
        is loaded.  Disable waiting with -D.

        Usage: waitlib [ -D | <libname> ]
        '''
        t = self.trace
        pid = t.getPid()

        t.requireAttached()

        argv = e_cli.splitargs(line)
        try:
            opts,args = getopt(argv, "D")
        except:
            return self.do_help("waitlib")

        for opt, optarg in opts:
            if opt == '-D':
                self.vprint('Disabling Wait On: %s' % self.waitlib)
                self.waitlib = None
                return

        if len(args) != 1:
            return self.do_help('waitlib')

        libname = args[0]

        if t.getMeta('LibraryBases').get(libname) is not None:
            self.vprint('Library Already Loaded: %s' % libname)
            return

        self.vprint('Setting Waitlib: %s' % libname)
        self.waitlib = libname

    def do_server(self, port):
        """
        Start a vtrace server on the local box.  If the server
        is already running, show which processes are being remotely
        debugged.

        Usage: server
        """
        if port:
            vtrace.port = int(port)

        if self.server is None:
            self.vprint('Starting vtrace server!')
            self.server = vtrace.startVtraceServer()
            return

        self.vprint('Displaying remotely debugged traces:')
        shared = [ t for (n,t) in self.server.getSharedObjects() if isinstance(t, vtrace.Trace) ]
        if not shared:
            self.vprint('None.')
            return

        for t in shared:

            if not t.isAttached():
                continue

            runmsg = 'stopped'
            if t.isRunning():
                runmsg = 'running'

            pid = t.getPid()
            name = t.getMeta('ExeName', 'Unknown')
            self.vprint('%6d %.8s - %s' % (pid, runmsg, name))

    def do_syms(self, line):
        '''
        List symbols for loaded libraries. Use 'lm' to see loaded libraries.
        -s <regex> a regular expression (case insensitive search)
        <libname> the library name

        Usage: syms [-s <regex>] [<libname> ...]

        Usage: show all symbols for library foobar
                syms foobar

        Usage: show specific symbols for library foobar and bazfaz
                syms -s .*?barfoo.* foobar bazfaz

        Usage: shows specific symbols in any library
                syms -s .*?barfoo.*
        '''
        argv = shlex.split(line)
        if len(argv) < 1:
            return self.do_help('syms')

        rgx = None
        if '-s' in argv:
            idx = argv.index('-s')
            argv.pop(idx)
            rgx = argv.pop(idx)

        s = set(argv)
        libs = self.trace.getNormalizedLibNames()
        if len(s) > 0:
            libs = [lib for lib in libs if lib in s]

        if len(libs) == 0 and rgx is None:
            self.vprint('invalid library names: %s' % argv)
            return self.do_help('syms')

        for lib in sorted(libs):
            for sym in self.trace.getSymsForFile(lib):
                r = repr(sym)

                if rgx is not None:
                    match = re.search(rgx, r, re.IGNORECASE)
                    if match is None:
                        continue

                self.vprint('0x%.8x %s' % (sym.value, r))

    def do_call(self, line):
        """
        Allows a C-like syntax for calling functions inside
        the target process (from his context).
        Example: call printf("yermom %d", 10)
        """
        self.trace.requireAttached()
        ind = line.index("(")
        if ind == -1:
            raise Exception('ERROR - call wants c-style syntax: ie call printf("yermom")')
        funcaddr = self.trace.parseExpression(line[:ind])

        try:
            args = eval(line[ind:])
        except:
            raise Exception('ERROR - call wants c-style syntax: ie call printf("yermom")')

        self.vprint("calling %s -> 0x%.8x" % (line[:ind], funcaddr))
        self.trace.call(funcaddr, args)

    def do_bestname(self, args):
        """
        Return the "best name" string for an address.

        Usage: bestname <vtrace expression>
        """
        if len(args) == 0:
            return self.do_help("bestname")
        addr = self.trace.parseExpression(args)
        self.vprint(self.reprPointer(addr))

    def do_EOF(self, string):
        '''
        Prints how to exit VDB (use quit).
        '''
        self.vprint("No.. this is NOT a python interpreter... use quit ;)")

    def do_quit(self, args):
        """
        Quit VDB and terminate the process.

        use "quit force" to hard-force a quit regardless of everything.
        """

        if args == 'force':
            print('Quitting by force!')
            os._exit(0)

        try:
            if self.trace.isRunning():
                self.trace.setMode('RunForever', False)
                self.trace.sendBreak()

            if self.trace.isAttached():
                if self.config.vdb.KillOnQuit:
                    self.trace.kill()
                else:
                    self.trace.detach()

            self.vprint('Exiting...')
            e_cli.EnviMutableCli.do_quit(self, args)

            self.trace.release()

        except Exception as e:
            import traceback
            self.vprint(traceback.format_exc())
            self.vprint('Exception during quit (may need: quit force): %s' % e)

    def do_detach(self, line):
        '''
        Detach from the current tracer.

        Detaching using -k terminates the process on detach.

        Usage: detach [-k]
        '''
        self.trace.requireAttached()

        argv = e_cli.splitargs(line)
        if '-k' in argv:
            self.trace.kill()
            if not self.trace.isRunning():
                self.trace.run()
        else:
            if self.trace.isRunning():
                self.trace.setMode("RunForever", False)
                self.trace.sendBreak()
            self.trace.detach()

    def do_attach(self, args):
        """
        Attach to a process by PID or by process name.  In
        the event of more than one process by a given name,
        attach to the last (most recently created) one in
        the list.

        Usage: attach [<pid>,<name>]

        NOTE: This is *not* a regular expression.  The given
        string must be found as a substring of the process
        name...
        """
        pid = None
        try:
            pid = int(args)
        except ValueError:

            for mypid, pname in self.trace.ps():
                if pname.find(args) != -1:
                    pid = mypid

        if pid is None:
            return self.do_help('attach')

        self.vprint("Attaching to %d" % pid)
        self.newTrace().attach(pid)

    def complete_attach(self, text, line, begidx, endidx):
        procs = self.trace.ps()
        pidlist = [ str(x) for x,y in procs ]
        proclist = [ y for x,y in procs ]
        if not text:
            return proclist
        if text.isdigit():
            return [ i for i in pidlist if i.startswith(text) ]

        return [ i for i in proclist if i.find(text) != -1 ]

    def do_autocont(self, line):
        """
        Manipulate the auto-continue behavior for the trace.  This
        will cause particular event types to automagically continue
        execution.

        Usage: autocont [event name]
        """
        argv = e_cli.splitargs(line)
        acnames = ["attach",
                   "signal",
                   "break",
                   "loadlib",
                   "unloadlib",
                   "createthread",
                   "exitthread",
                   "dbgprint"]

        acvals = [ vtrace.NOTIFY_ATTACH,
                   vtrace.NOTIFY_SIGNAL,
                   vtrace.NOTIFY_BREAK,
                   vtrace.NOTIFY_LOAD_LIBRARY,
                   vtrace.NOTIFY_UNLOAD_LIBRARY,
                   vtrace.NOTIFY_CREATE_THREAD,
                   vtrace.NOTIFY_EXIT_THREAD,
                   vtrace.NOTIFY_DEBUG_PRINT]

        c = self.trace.getAutoContinueList()

        if len(line):
            try:
                index = acnames.index(line)
            except ValueError:
                self.vprint("Unknown event name: %s" % line)
                return
            sig = acvals[index]
            if sig in c:
                self.trace.disableAutoContinue(sig)
                c.remove(sig)
            else:
                self.trace.enableAutoContinue(sig)
                c.append(sig)

        self.vprint("Auto Continue Status:")
        for i in range(len(acnames)):
            name = acnames[i]
            sig = acvals[i]
            acont = False
            if sig in c:
                acont = True
            self.vprint("%s %s" % (name.rjust(14),repr(acont)))

        self.vdbUIEvent('vdb:setautocont')

    def do_bt(self, line):
        """
        Show a stack backtrace for the currently selected thread.

        Usage: bt
        """
        self.vprint("      [   PC   ] [ Frame  ] [ Location ]")
        idx = 0
        for pc,frame in self.trace.getStackTrace():
            self.vprint("[%3d] 0x%.8x 0x%.8x %s" % (idx,pc,frame,self.reprPointer(pc)))
            idx += 1

    def do_lm(self, args):
        """
        Show the loaded libraries and their base addresses.

        Usage: lm [libname]
        """
        bases = self.trace.getMeta("LibraryBases")
        paths = self.trace.getMeta("LibraryPaths")
        if len(args):
            base = bases.get(args)
            path = paths.get(base, "unknown")
            if base is None:
                self.vprint("Library %s is not found!" % args)
            else:
                self.vprint("0x%.8x - %s %s" % (base, args, path))
        else:
            self.vprint("Loaded Libraries:")
            names = self.trace.getNormalizedLibNames()
            names.sort()
            names = e_cli.columnstr(names)
            for libname in names:
                base = bases.get(libname.strip(), -1)
                path = paths.get(base, "unknown")
                self.vprint("0x%.8x - %.30s %s" % (base, libname, path))

    def do_guid(self, line):
        """
        Parse and display a Global Unique Identifier (GUID) from memory
        (eventually, use GUID db to lookup the name/meaning of the GUID).

        Usage: guid <addr_exp>
        """
        self.trace.requireNotRunning()
        if not line:
            return self.do_help("guid")

        addr = self.parseExpression(line)
        guid = vs_prims.GUID()
        bytes = self.trace.readMemory(addr, len(guid))
        guid.vsSetValue(bytes)
        self.vprint("GUID 0x%.8x %s" % (addr, repr(guid)))

    def do_bpfile(self, line):
        """
        Set the python code for a breakpoint from the contents
        of a file.

        Usage: bpfile <bpid> <filename>
        """
        argv = e_cli.splitargs(line)
        if len(argv) != 2:
            return self.do_help("bpfile")

        bpid = int(argv[0])
        with open(argv[1], 'rU') as f:
            pycode = f.read()

        self.trace.setBreakpointCode(bpid, pycode)

    def do_bpedit(self, line):
        """
        Manipulcate the python code that will be run for a given
        breakpoint by ID.  (Also the way to view the code).

        Usage: bpedit <id> ["optionally new code"]

        NOTE: Your code must be surrounded by "s and may not
        contain any "s
        """
        argv = e_cli.splitargs(line)
        if len(argv) == 0:
            return self.do_help("bpedit")
        bpid = int(argv[0])

        if len(argv) == 2:
            self.trace.setBreakpointCode(bpid, argv[1])

        pystr = self.trace.getBreakpointCode(bpid)
        self.vprint("[%d] Breakpoint code: %s" % (bpid,pystr))

    def do_bp(self, line):
        """
        Show, add,  and enable/disable breakpoints
        USAGE: bp [-d <addr>] [-a <addr>] [-o <addr>] [[-c pycode] <address> [vdb cmds]]
        -C - Clear All Breakpoints
        -c "py code" - Set the breakpoint code to the given python string
        -d <id> - Disable Breakpoint
        -e <id> - Enable Breakpoint
        -r <id> - Remove Breakpoint
        -o <addr> - Create a OneTimeBreak
        -L <libname> - Add bp's to all functions in <libname>
        -F <filename> - Load bpcode from file
        -W perms:size - Set a hardware Watchpoint with perms/size (ie -W rw:4)
        -f - Make added breakpoints from this command into "fastbreaks"
        -S <libname>:<regex> - Add bp's to all matching funcs in <libname>

        <address>... - Create Breakpoint

        [vdb cmds].. - (optional) vdb cli comand to run on BP hit (seperate
                       multiple commands with ;; )

        NOTE: -c adds python code to the breakpoint.  The python code will
            be run with the following objects mapped into it's namespace
            automagically:
                vtrace  - the vtrace package
                trace   - the tracer
                bp      - the breakpoint object
        """
        self.trace.requireNotRunning()

        argv = e_cli.splitargs(line)
        try:
            opts,args = getopt(argv, "fF:e:d:o:r:L:Cc:S:W:")
        except Exception as e:
            return self.do_help('bp')

        pycode = None
        wpargs = None
        fastbreak = False
        libsearch = None

        for opt,optarg in opts:
            if opt == "-e":
                self.trace.setBreakpointEnabled(eval(optarg), True)

            elif opt == "-c":
                pycode = optarg
                test = compile(pycode, "test","exec")

            elif opt == "-F":
                with open(optarg, 'rU') as f:
                    pycode = f.read()

            elif opt == '-f':
                fastbreak = True

            elif opt == "-r":
                self.bpcmds.pop(int(optarg), None)
                self.trace.removeBreakpoint(int(optarg))
                self.vdbUIEvent('vdb:delbreak', int(optarg))

            elif opt == "-C":
                for bp in self.trace.getBreakpoints():
                    self.bpcmds.pop(bp.id, None)
                    self.trace.removeBreakpoint(bp.id)
                    self.vdbUIEvent('vdb:delbreak', bp.id)

            elif opt == "-d":
                self.trace.setBreakpointEnabled(eval(optarg), False)

            elif opt == "-o":
                bpid = self.trace.addBreakpoint(vtrace.OneTimeBreak(None, expression=optarg))
                self.vdbUIEvent('vdb:addbreak', bpid)

            elif opt == "-L":
                for sym in self.trace.getSymsForFile(optarg):
                    if not isinstance(sym, e_resolv.FunctionSymbol):
                        continue
                    try:
                        bp = vtrace.Breakpoint(None, expression=str(sym))
                        bp.setBreakpointCode(pycode)
                        bpid = self.trace.addBreakpoint(bp)
                        self.vdbUIEvent('vdb:addbreak', bpid)
                        self.vprint("Added: %s" % str(sym))
                    except Exception as msg:
                        self.vprint("WARNING: %s" % str(msg))

            elif opt == "-W":
                wpargs = optarg.split(":")

            elif opt == '-S':
                libname, regex = optarg.split(':')

                try:
                    for sym in self.trace.searchSymbols(regex, libname=libname):

                        symstr = str(sym)
                        symval = int(sym)
                        if self.trace.getBreakpointByAddr(symval) is not None:
                            self.vprint('Duplicate (0x%.8x) %s' % (symval, symstr))
                            continue
                        bp = vtrace.Breakpoint(None, expression=symstr)
                        self.trace.addBreakpoint(bp)
                        self.vprint('Added: %s' % symstr)

                except re.error:
                    self.vprint('Invalid Regular Expression: %s' % regex)
                    return

        cmdstr = None
        if len(args) > 1:
            cmdstr = ' '.join(args[1:])

        if len(args) >= 1:
            arg = args[0]

            if wpargs is not None:
                size = int(wpargs[1])
                bp = vtrace.Watchpoint(None, expression=arg, size=size, perms=wpargs[0])
            else:
                bp = vtrace.Breakpoint(None, expression=arg)

            bp.setBreakpointCode(pycode)
            bp.fastbreak = fastbreak
            bpid = self.trace.addBreakpoint(bp)
            self.vdbUIEvent('vdb:addbreak', bpid)
            if cmdstr:
                self.bpcmds[bpid] = cmdstr.replace(';;', '&&')

        self.vprint(" [ Breakpoints ]")
        for bp in self.trace.getBreakpoints():
            self._print_bp(bp)

    def _print_bp(self, bp):
        cmdstr = self.bpcmds.get(bp.id, '')
        self.vprint("%s enabled: %s fast: %s %s" % (bp, bp.isEnabled(), bp.fastbreak, cmdstr))

    def do_fds(self, args):
        """
        Show all the open Handles/FileDescriptors for the target process.
        The "typecode" shown in []'s is the vtrace typecode for that kind of
        fd/handle.

        Usage: fds
        """
        self.trace.requireAttached()
        for id,fdtype,fname in self.trace.getFds():
            self.vprint("0x%.8x [%d] %s" % (id,fdtype,fname))

    def do_ps(self, args):
        """
        Show the current process list.

        Usage: ps
        """
        self.vprint("[Pid]\t[ Name ]")
        for ps in self.trace.ps():
            self.vprint("%s\t%s" % (ps[0],ps[1]))

    def do_break(self, args):
        """
        Send the break signal to the target tracer to stop
        it's execution.

        Usage: break
        """
        if self.trace.getMeta('PendingBreak'):
            self.vprint('Break already sent...')
            return
        self.trace.setMeta('PendingBreak', True)
        self.trace.setMode("RunForever", False)
        self.trace.sendBreak()

    def do_meta(self, line):
        """
        Show the metadata for the current trace.

        Usage: meta
        """
        argv = e_cli.splitargs(line)
        if argv:
            for name in argv:
                mval = self.trace.getMeta(name)
                self.vprint('%s: %r' % (name, mval))
        else:
            meta = self.trace.metadata
            x = pprint.pformat(meta)
            self.vprint(x)

    def do_memdiff(self, line):
        """
        Save and compare snapshots of memory to enumerate changes.

        Usage: memdiff [options]
        -C             Clear all current memory diff snapshots.
        -A <va:size>   Add the given virtual address to the list.
        -M <va>        Add the entire memory map which contains VA to the list.
        -D             Compare currently tracked memory with the target process
                       and show any differences.
        """
        argv = e_cli.splitargs(line)
        opts,args = getopt(argv, "A:CDM:")

        if len(opts) == 0:
            return self.do_help('memdiff')

        self.trace.requireNotRunning()

        for opt,optarg in opts:

            if opt == "-A":
                if optarg.find(':') == -1:
                    return self.do_help('memdiff')

                vastr,sizestr = optarg.split(':')
                va = self.parseExpression(vastr)
                size = self.parseExpression(sizestr)
                bytez = self.trace.readMemory(va,size)
                self.difftracks[va] = bytez

            elif opt == '-C':
                self.difftracks = {}

            elif opt == '-D':
                difs = self._getDiffs()
                if len(difs) == 0:
                    self.vprint('No Differences!')
                else:
                    for va,thenbytes,nowbytes in difs:
                        self.vprint('0x%.8x: %s %s' % (va,
                                                       e_common.hexify(thenbytes),
                                                       e_common.hexify(nowbytes)))

            elif opt == '-M':
                va = self.parseExpression(optarg)
                mmap = self.trace.getMemoryMap(va)
                if mmap is None:
                    self.vprint('No Memory Map At: 0x%.8x' % va)
                    return
                mva,msize,mperm,mfile = mmap
                bytez = self.trace.readMemory(mva, msize)
                self.difftracks[mva] = bytez


    def _getDiffs(self):

        ret = []
        for va, bytez in self.difftracks.items():
            nowbytez = self.trace.readMemory(va, len(bytez))

            i = 0
            while i < len(bytez):
                thendiff = ""
                nowdiff = ""
                iva = va+i
                while (i < len(bytez) and
                            bytez[i] != nowbytez[i]):
                    thendiff += bytez[i]
                    nowdiff += nowbytez[i]
                    i += 1

                if thendiff:
                    ret.append((iva, thendiff, nowdiff))
                    continue

                i += 1

        return ret

    def do_dope(self, line):
        '''
        Cli interface to the "stack doping" api inside recon.  *BETA*

        (Basically, set all un-initialized stack memory to V's to tease
        out uninitialized stack bugs)

        Usage: dope [ options ]
        -E  Enable automagic thread stack doping on all continue events
        -D  Disable automagic thread stack doping on all continue events
        -A  Dope all current thread stacks
        '''
        import vdb.recon.dopestack as vr_dopestack

        argv = e_cli.splitargs(line)

        if len(argv) == 0:
            return self.do_help('dope')

        opts,args = getopt(argv, 'ADE')

        if len(opts) == 0:
            return self.do_help('dope')

        for opt, optarg in opts:

            if opt == '-A':
                self.vprint('Doping all thread stacks...')
                vr_dopestack.dopeAllThreadStacks(self.trace)
                self.vprint('...complete!')

            elif opt == '-D':
                self.vprint('Disabling thread doping...')
                vr_dopestack.disableEventDoping(self.trace)
                self.vprint('...complete!')

            elif opt == '-E':
                self.vprint('Enabling thread doping on CONTINUE events...')
                vr_dopestack.enableEventDoping(self.trace)
                self.vprint('...complete!')


    def do_recon(self, line):
        '''
        Cli front end to the vdb recon subsystem which allows runtime
        analysis of known API calls.

        Usage: recon [options]
        -A <sym_expr>:<recon_fmt> - Add a recon breakpoint with the given format
        -C - Clear the current list of recon breakpoint hits.
        -H - Print the current list of recon breakpoint hits.
        -Q - Toggle "quiet" mode which prints nothing on bp hits.
        -S <sym_expr>:<argidx> - Add a sniper break for arg index

        NOTE: A "recon format" is a special format sequence which tells the
              recon subsystem how to present the argument data for a given
              breakpoint hit.

        Recon Format:
        C - A character
        I - A decimal integer
        P - A pointer (display symbol if possible)
        S - An ascii string (up to 260 chars)
        U - A unicode string (up to 260 chars)
        X - A hex number

        '''
        import vdb.recon as v_recon
        import vdb.recon.sniper as v_sniper
        argv = e_cli.splitargs(line)

        if len(argv) == 0:
            return self.do_help('recon')

        if self.trace.getMeta('Architecture') != 'i386':
            self.vprint('FIXME: recon only works on i386 right now...')
            return

        opts,args = getopt(argv, 'A:CHQS:')
        for opt, optarg in opts:
            if opt == '-A':
                symname, reconfmt = optarg.split(':', 1)
                v_recon.addReconBreak(self.trace, symname, reconfmt)

            elif opt == '-C':
                v_recon.clearReconHits(self.trace)

            elif opt == '-H':
                self.vprint('Recon Hits:')
                hits = v_recon.getReconHits(self.trace)
                for hit in hits:
                    thrid, savedeip, symname, args, argrep = hit
                    argstr = '(%s)' % ', '.join(argrep)
                    self.vprint('[%6d] 0x%.8x %s%s' % (thrid, savedeip, symname, argstr))
                self.vprint('%d total hits' % len(hits))

            elif opt == '-Q':
                newval = not self.trace.getMeta('recon_quiet', False)
                self.trace.setMeta('recon_quiet', newval)
                self.vprint('Recon Quiet: %s' % newval)

            elif opt == '-S':
                symname, idxstr = optarg.split(':')
                argidx = self.trace.parseExpression(idxstr)
                v_sniper.snipeDynArg(self.trace, symname, argidx)

    def do_stalker(self, line):
        '''
        Cli front end to the VDB code coverage subsystem. FIXME MORE DOCS!

        Usage: stalker [options]
        -C                  - Cleanup stalker breaks and hit info
        -c                  - Clear the current hits (so you can make more ;)
        -E <addr_expr>      - Add the specified entry point for tracking
        -H                  - Show the current hits
        -L <lib>:<regex>    - Add stalker breaks to all matching library symbols
        -R                  - Reset all breakpoints to enabled and clear hit info
        '''

        argv = e_cli.splitargs(line)

        if len(argv) == 0:
            return self.do_help('stalker')

        try:
            opts,args = getopt(argv, 'cCE:HIL:R')
        except Exception as e:
            return self.do_help('stalker')

        trace = self.trace
        for opt, optarg in opts:
            if opt == '-c':
                v_stalker.clearStalkerHits(trace)
                self.vprint('Clearing Stalker Hits...')

            elif opt == '-C':
                v_stalker.clearStalkerBreaks(trace)
                v_stalker.clearStalkerHits(trace)
                self.vprint('Cleaning up stalker breaks and hits')


            elif opt == '-E':
                addr = trace.parseExpression(optarg)
                v_stalker.addStalkerEntry(trace, addr)
                self.vprint('Added 0x%.8x' % addr)

            elif opt == '-H':
                self.vprint('Current Stalker Hits:')
                for hitva in v_stalker.getStalkerHits(trace):
                    self.vprint('0x%.8x' % hitva)

            elif opt == '-L':
                libname, regex = optarg.split(':', 1)
                for sym in trace.searchSymbols(regex, libname=libname):
                    v_stalker.addStalkerEntry(trace, int(sym))
                    self.vprint('Stalking %s' % str(sym))

            elif opt == '-R':
                self.vprint('Resetting all breaks and hit info')
                v_stalker.clearStalkerHits(trace)
                v_stalker.resetStalkerBreaks(trace)

    def do_status(self, line):
        '''
        Print out the status of the debugger / trace...
        '''
        t = self.getTrace()
        if not t.isAttached():
            self.vprint('Trace Not Attached...')
            return

        runmsg = 'stopped'
        if t.isRunning():
            runmsg = 'running'
        pid = t.getPid()
        self.vprint('Attached to pid: %d (%s)' % (pid, runmsg))

    def _getFirstLine(self, line):
        '''
        Returns the first non-empty line in a (potentially) empty or
        multiline string.  An empty line is returned for a None string or
        if all lines are empty.
        '''
        if line is None:
            return ''

        lines = line.split('\n')
        lines = [line.strip() for line in lines]

        for line in lines:
            if line != '':
                return line
        return ''

    def _getCommandHelp(self):
        '''
        Returns a list of command name, doc first line, and doc string tuples.
        (sorted by command name)
        We'll need this later anyway when we implement our own groups of
        commands.
        '''
        # commands can be docstrings or have help_<cmd> methods.
        HELP_DOCS = 0 # help docstring
        HELP_FUNC = 1 # help function (precedence over docstring)
        cmds = defaultdict(list)
        for name in dir(self):

            if name.startswith('help_'):
                hstr = getattr(self, name)()
                cmds[name[5:]].append( (HELP_FUNC, hstr) )

            elif name.startswith('do_'):
                hstr = getattr(self, name).__doc__
                cmds[name[3:]].append( (HELP_DOCS, hstr) )

            else:
                pass

        rcmds = []
        for cname, clist in cmds.items():
            if len(clist) > 2:
                raise Exception('how do we handle inherited overridden help')

            # find the right help string.
            # pull out HELP_FUNC if it exists, otherwise use HELP_DOCS
            if len(clist) == 2:
                chelp = max(clist, key=lambda x: x[0])[1].strip()
            else:
                chelp = clist[0][1].strip()

            # maybe change to first line or first sentence in line?
            fline = self._getFirstLine(chelp)

            rcmds.append( (cname, fline, chelp) )

        rcmds.sort()
        return rcmds

    def do_help(self, line):
        '''
        Prints a list of commands and further help depending on the options.

        Usage: help [options] [string]
        Usage: ? [options] [string]

        no opts/args    prints all commands
        <command>       help for the command
        -s              one line of help for each command
        -s <string>     one line of help per command for commands that contain
                        string
        -k <string>     all help per command for commands that contain <string>
        '''
        argv = shlex.split(line)
        if len(argv) == 0:
            return e_cli.EnviMutableCli.do_help(self, line)

        if argv[0] not in ('-k', '-s'):
            return e_cli.EnviMutableCli.do_help(self, line)

        # this gets a tad messy.
        if argv[0] == '-s' and len(argv) == 1:
            ctups = self._getCommandHelp()
            for ctup in ctups:
                self.vprint('%15s: %s' % (ctup[0], ctup[1]))

        elif argv[0] == '-s' and len(argv) == 2:
            ctups = self._getCommandHelp()
            for ctup in ctups:
                if (argv[1] in ctup[0]) or (argv[1] in ctup[2]):
                    self.vprint('%s: %s' % (ctup[0], ctup[1]))

        elif argv[0] == '-k' and len(argv) == 2:
            ctups = self._getCommandHelp()
            for ctup in ctups:
                if (argv[1] in ctup[0]) or (argv[1] in ctup[2]):
                    self.vprint('> help %s\n' % ctup[0])
                    self.vprint('        %s\n' % ctup[2])
        else:
            self.vprint(self.do_help.__doc__)

    def FIXME_do_remote(self, line):
        """
        Act as a remote debugging client to the server running on
        the specified host/ip.

        Usage: remote <host>
        """
        vtrace.remote = line
        # FIXME how do we re-init the debugger?

    # Some helper functions for tab completion
    def _complete_libname(self, text, line, begidx, endidx):
        libnames = self.trace.getNormalizedLibNames()
        if not text:
            return libnames
        return [ i for i in libnames if i.startswith( text ) ]

##############################################################################
# The following are touched during the release process by bump2version.
# You should have no reason to modify these yourself
version = (1, 0, 4)
verstring = '.'.join([str(x) for x in version])
commit = ''
