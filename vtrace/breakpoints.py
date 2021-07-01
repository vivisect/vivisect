"""
Breakpoint Objects
"""

# Copyright (C) 2007 Invisigoth - See LICENSE file for details

import time
import logging
from collections import defaultdict

import vtrace


logger = logging.getLogger(__name__)

class Breakpoint:
    """
    Breakpoints in Vtrace are platform independant objects that
    use the underlying trace objects to get things like the
    program counter and the break instruction.  As long as
    platforms are completely implemented, all breakpoint
    objects should be portable.
    """

    bpcodeobj = {} # Cache compiled code objects on the class def

    def __init__(self, address, expression=None):
        self.resonce = False
        self.address = address
        self.enabled = True
        self.active = False
        self.fastbreak = False      # no NOTIFY_BREAK, autocont, no NOTIFY_CONTINUE
        self.stealthbreak = False   # no NOTIFY_BREAK

        self.id = -1
        self.vte = None
        self.bpcode = None
        if expression:
            self.vte = expression

    def getAddress(self):
        """
        This will return the address for this breakpoint.  If the return'd
        address is None, this is a deferred breakpoint which needs to have
        resolveAddress() called to attempt to set the address.
        """
        return self.address

    def getId(self):
        return self.id

    def getName(self):
        if self.vte:
            return str(self.vte)
        return "0x%.8x" % self.address

    def __repr__(self):
        if self.address is None:
            addr = "unresolved"
        else:
            addr = "0x%.8x" % self.address
        return "[%d] %s %s: %s" % (self.id, addr, self.__class__.__name__, self.getName())

    def inittrace(self, trace):
        '''
        A callback to do housekeeping at the time the breakpoint is
        added to the tracer object.  This should be used instead of activate
        for initialization time infoz to save on time per activate call...
        '''
        pass

    def activate(self, trace):

        if not self.active:
            trace.archActivBreakpoint(self.address)
            self.active = True

    def deactivate(self, trace):

        if self.active:
            trace.archClearBreakpoint(self.address)
            self.active = False

    def resolvedaddr(self, trace, addr):
        '''
        An initialization callback which will be executed when the
        actual address for this breakpoint has been resolved.
        '''

    def resolveAddress(self, trace):
        """
        Try to resolve the address for this break.  If this is a statically
        addressed break, just return the address.  If it has an "expression"
        use that to resolve the address...
        """
        if self.address is None and self.vte:
            try:
                self.address = trace.parseExpression(self.vte)
            except Exception as e:
                logger.warning('Failed to resolve breakpoint address for expression: %s', self.vte)
                logger.warning('Error:', exc_info=1)
                self.address = None

        # If we resolved, lets get our saved code...
        if self.address is not None and not self.resonce:
            self.resonce = True
            self.resolvedaddr(trace, self.address)

        return self.address

    def isEnabled(self):
        """
        Is this breakpoint "enabled"?
        """
        return self.enabled

    def setEnabled(self, enabled=True):
        """
        Set this breakpoints "enabled" status
        """
        self.enabled = enabled

    def setBreakpointCode(self, pystr):
        """
        Use this method to set custom python code to run when this
        breakpoint gets hit.  The code will have the following objects
        mapped into it's namespace when run:
            trace - the tracer
            vtrace - the vtrace module
            bp - the breakpoint
        """
        self.bpcode = pystr
        Breakpoint.bpcodeobj.pop(self.id, None)

    def getBreakpointCode(self):
        """
        Return the current python string that will be run when this break is hit.
        """
        return self.bpcode

    def notify(self, event, trace):
        """
        Breakpoints may also extend and implement "notify" which will be
        called whenever they are hit.  If you want to continue the ability
        for this breakpoint to have bpcode, you must call this method from
        your override.
        """
        if self.bpcode is not None:
            cobj = Breakpoint.bpcodeobj.get(self.id, None)
            if cobj is None:
                fname = "BP:%d (0x%.8x)" % (self.id, self.address)
                cobj = compile(self.bpcode, fname, "exec")
                Breakpoint.bpcodeobj[self.id] = cobj

            d = vtrace.VtraceExpressionLocals(trace)
            d['bp'] = self
            exec(cobj, None, d)

class TrackerBreak(Breakpoint):
    """
    A breakpoint which will record how many times it was hit
    (by the address it was at) as metadata for the tracer.
    """
    def notify(self, event, trace):
        tb = trace.getMeta("TrackerBreak", None)
        if tb is None:
            tb = {}
        trace.setMeta("TrackerBreak", tb)
        tb[self.address] = (tb.get(self.address, 0) + 1)
        Breakpoint.notify(self, event, trace)

class OneTimeBreak(Breakpoint):
    """
    This type of breakpoint is exclusivly for marking
    and code-coverage stuff.  It removes itself.
    (most frequently used with a continued trace)
    """
    def notify(self, event, trace):
        trace.removeBreakpoint(self.id)
        Breakpoint.notify(self, event, trace)

class StopRunForeverBreak(Breakpoint):
    """
    This breakpoint will turn off RunForever mode
    on the tracer object when hit.  it's a good way
    to let things run on and on processing exceptions
    but stop when you get to this one thing.
    """
    def notify(self, event, trace):
        trace.setMode("RunForever", False)
        Breakpoint.notify(self, event, trace)

class StopAndRemoveBreak(Breakpoint):
    """
    When hit, take the tracer out of run-forever mode and
    remove this breakpoint.
    """
    def notify(self, event, trace):
        trace.setMode("RunForever", False)
        trace.removeBreakpoint(self.id)
        Breakpoint.notify(self, event, trace)

class CallBreak(Breakpoint):
    """
    A special breakpoint which will restore process
    state (registers in particular) when it gets hit.
    This is primarily used by the call method inside
    the trace object to restore original state
    after a successful "call" method call.

    Additionally, the endregs dict will be filled in
    with the regs at the time it was hit and kept until
    we get garbage collected...
    """
    def __init__(self, address, saved_regs):
        Breakpoint.__init__(self, address)
        self.endregs = None # Filled in when we get hit
        self.saved_regs = saved_regs

    def notify(self, event, trace):
        self.endregs = trace.getRegisters()
        trace.removeBreakpoint(self.id)
        trace.setRegisters(self.saved_regs)
        trace.setMeta("PendingSignal", None)

class SnapshotBreak(Breakpoint):
    """
    A special breakpoint type which will produce vtrace snapshots
    for the target process when hit.  The snapshots will be saved
    to a default name of <exename>-<timestamp>.vsnap.  This is not
    recommended for use in heavily hit breakpoints as taking a
    snapshot is processor intensive.
    """
    def notify(self, event, trace):
        exe = trace.getExe()
        snap = trace.takeSnapshot()
        snap.saveToFile("%s-%d.vsnap" % (exe, time.time()))
        Breakpoint.notify(self, event, trace)

class NiceBreakpoint(Breakpoint):
    '''
    Calls the underlying breakpoint constructor with the correct constructor
    automagically by checking the type you passed in (int vs other).
    '''
    def __init__(self, expr, *args, **kwargs):
        if isinstance(expr, int):
            vtrace.Breakpoint.__init__(self, expr, *args, **kwargs)
        else:
            vtrace.Breakpoint.__init__(self, None, expression=expr, *args, **kwargs)

def addHook(trace, expr, pre_callback, post_callback=None, cc=None, argc=None):
    '''
    Adds the specified pre and post callbacks to the specified expression.
    '''
    hbp = HookBreakpoint(expr, callingconv=cc, argc=argc)
    addr = hbp.resolveAddress(trace)

    # does a hook bp already exist in the deferred or active bplist?
    ret_bp = None
    if addr is None:
        for dbp in trace.deferred:
            if dbp.getName() == expr:
                ret_bp = dbp
                break
    else:
        ret_bp = trace.getBreakpointByAddr(addr)

    if ret_bp is None:
        # add a new bp, one does not exist at this location already
        trace.addBreakpoint(hbp)
        ret_bp = hbp
    elif not isinstance(ret_bp, HookBreakpoint):
        raise Exception('cannot add this hook, non-HookBreakpoint bp at this location')

    ret_bp.addPreHook(pre_callback)

    if post_callback is not None:
        ret_bp.addPostHook(post_callback)

class HookBreakpoint(NiceBreakpoint):
    '''
    A special breakpoint that allows pre/post handlers to be registered on a
    bp for a function.  Pre-handlers are executed at the time of the break.
    Post-handlers are implemented as a seperate breakpoint placed at the
    return address. (as read at the time of entry to the function, this does
    not handle things that manually mess with the return address within the
    function)

    Handlers are executed one at a time in an ordered sequence. Execution
    continues without breaking to the user.

    The prototype for pre hook callback handlers is:
    def prehook(event, trace, ret_addr, args, callconv)
    event - the event
    trace - trace object
    ret_addr - the return address (if calling convention is known)
    args - the function arguments (if calling convention is known)
    callconv - the calling convention object

    The prototype for post hook callback handlers is the same.
    def posthook(event, trace, saved_ret_addr, saved_args, callconv)
    '''
    def __init__(self, expr, callingconv=None, argc=None):
        vtrace.NiceBreakpoint.__init__(self, expr)

        self.fastbreak = True

        self.prehooks = []
        self.posthooks = []

        self.cc = callingconv
        self.argc = argc

        # holds call information by thread id
        # { tid : (ret addr, (arg0, arg1, ...) ), ... }
        self.callinfo = defaultdict(list)

        self.error_cb = self.defaultErrorHandler

    def defaultErrorHandler(self, hook_cb_name, stre):
        logger.error('Pre hook callback "%s" exception: %s', hook_cb_name, stre)

    def resolvedaddr(self, trace, addr):
        '''
        When we get resolved, lookup in impapi the calling convention and other
        details about the function.  Do not do this if we were explicitly told
        what to do.
        '''
        # told explicitly what to do, don't go look anything up
        if self.cc is not None and self.argc is not None:
            return

        # TODO: move this out of here after we move impapi to a top-level
        # package.
        import vivisect.impapi as viv_impapi
        # this code also exists in win32stealth, we should put this somewhere
        # common
        platform = trace.getMeta('Platform')
        arch = trace.getMeta('Architecture')
        self.impapi = viv_impapi.getImportApi(platform, arch)
        cc = self.impapi.getImpApiCallConv(self.vte)
        emu = vtrace.getEmu(trace)
        self.cc = emu.getCallingConvention(cc)
        apiargs = self.impapi.getImpApiArgs(self.vte)
        if apiargs is not None:
            self.argc = len(apiargs)

    def addPreHook(self, callback):
        self.prehooks.append(callback)

    def addPostHook(self, callback):
        self.posthooks.append(callback)

    def runPreHookCallbacks(self, hook_cbs, event, trace, ret_addr, args):
        for hook_cb in hook_cbs:
            try:
                hook_cb(event, trace, ret_addr, args, self.cc)
            except Exception as e:
                self.defaultErrorHandler(hook_cb, str(e))

    def notify(self, event, trace):
        ret_addr = None
        args = None
        if self.cc is not None:
            ret_addr = self.cc.getReturnAddress(trace)
            args = self.cc.getCallArgs(trace, self.argc)

            self.callinfo[trace.getCurrentThread()] = (ret_addr, args)

        # setup a PostHookBreakpoint on where we are headed to (if one is not
        # already there) we can't do this if we don't know the calling conv
        # information.
        if ret_addr is not None:
            ret_bp = trace.getBreakpointByAddr(ret_addr)
            if ret_bp is None:
                ret_bp = PostHookBreakpoint(ret_addr, self)
                trace.addBreakpoint(ret_bp)

            if not isinstance(ret_bp, PostHookBreakpoint):
                raise Exception('cannot add PostHookBreakpoint, another type of bp exists at this location')

        self.runPreHookCallbacks(self.prehooks, event, trace, ret_addr, args)


class PostHookBreakpoint(NiceBreakpoint):

    def __init__(self, expr, parent_hook_bp):
        vtrace.NiceBreakpoint.__init__(self, expr)
        self.parent = parent_hook_bp
        self.fastbreak = True

    def runPostHookCallbacks(self, event, trace, saved_ret_addr, saved_args):
        for hook_cb in self.parent.posthooks:
            try:
                hook_cb(event, trace, saved_ret_addr, saved_args, self.parent.cc)
            except Exception as e:
                logger.error('Post hook callback "%s" exception: %s', hook_cb, e)

    def notify(self, event, trace):
        tup = self.parent.callinfo.get(trace.getCurrentThread(), None)
        if tup is None:
            return

        ret_addr, args = tup

        self.runPostHookCallbacks(event, trace, ret_addr, args)
