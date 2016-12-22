"""
Vtrace notitifers base classes and examples

Vtrace supports the idea of callback notifiers which
get called whenever particular events occur in the target
process.  Notifiers may be registered to recieve a callback
on any of the vtrace.NOTIFY_FOO events from vtrace.  One notifier
*may* be registered with more than one trace, as the "notify"
method is passed a reference to the trace for which an event
has occured...

"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details

import vtrace
import traceback


class Notifier(object):
    """
    The top level example notifier...  Anything which registers
    itself for trace events or tracegroup events should implement
    the notify method as shown here.
    """

    def __init__(self):
        """
        All extenders *must* call this.  Mostly because all the
        goop necessary for the remote debugging stuff...
        (if notifier is instantiated on server, all is well, if it's
        on the client it needs a proxy...)
        """
        pass

    def handleEvent(self, event, trace):
        """
        An "internal" handler so if we need to do something
        from an API perspective before calling the notify method
        we can have a good "all at once" hook
        """
        self.notify(event, trace)

    def notify(self, event, trace):
        print("Got event: %d from pid %d" % (event, trace.getPid()))


class VerboseNotifier(Notifier):
    def notify(self, event, trace):
        print("PID %d - ThreadID (%d) got" % (trace.getPid(), trace.getMeta("ThreadId")), end=' ')
        if event == vtrace.NOTIFY_ALL:
            print("WTF, how did we get a vtrace.NOTIFY_ALL event?!?!")
        elif event == vtrace.NOTIFY_SIGNAL:
            signo = trace.getCurrentSignal()
            print(("vtrace.NOTIFY_SIGNAL %d (0x%08x)" % (signo, signo)))
            if trace.getMeta("Platform") == "windows":
                print((repr(trace.getMeta("Win32Event"))))
        elif event == vtrace.NOTIFY_BREAK:
            print("vtrace.NOTIFY_BREAK")
            print(("\tIP: 0x%08x" % trace.getProgramCounter()))
        elif event == vtrace.NOTIFY_SYSCALL:
            print("vtrace.NOTIFY_SYSCALL")
        elif event == vtrace.NOTIFY_CONTINUE:
            print("vtrace.NOTIFY_CONTINUE")
        elif event == vtrace.NOTIFY_EXIT:
            print("vtrace.NOTIFY_EXIT")
            print(("\tExitCode: %d" % trace.getMeta("ExitCode")))
        elif event == vtrace.NOTIFY_ATTACH:
            print("vtrace.NOTIFY_ATTACH")
        elif event == vtrace.NOTIFY_DETACH:
            print("vtrace.NOTIFY_DETACH")
        elif event == vtrace.NOTIFY_LOAD_LIBRARY:
            print("vtrace.NOTIFY_LOAD_LIBRARY")
            print(("\tLoaded library %s" % trace.getMeta('LatestLibrary')))
        elif event == vtrace.NOTIFY_UNLOAD_LIBRARY:
            print("vtrace.NOTIFY_UNLOAD_LIBRARY")
        elif event == vtrace.NOTIFY_CREATE_THREAD:
            print("vtrace.NOTIFY_CREATE_THREAD")
            print(("\tNew thread - ThreadID: %d" % trace.getMeta("ThreadId")))
        elif event == vtrace.NOTIFY_EXIT_THREAD:
            print("vtrace.NOTIFY_EXIT_THREAD")
            print(("Thread exited - ThreadID: %d" % trace.getMeta("ExitThread", -1)))
        elif event == vtrace.NOTIFY_STEP:
            print("vtrace.NOTIFY_STEP")
        else:
            print("vtrace.NOTIFY_WTF_HUH?")


class DistributedNotifier(Notifier):
    """
    A notifier which will distributed notifications out to
    locally registered notifiers so that remote tracer's notifier
    callbacks only require once across the wire.
    """

    # NOTE: once you turn on vtrace.NOTIFY_ALL it can't be turned back off yet.
    def __init__(self):
        Notifier.__init__(self)
        self.shared = False
        self.events = []
        self.notifiers = {}
        for i in range(vtrace.NOTIFY_MAX):
            self.notifiers[i] = []

    def getProxy(self, trace):
        host, nothing = cobra.getCobraSocket(trace).getLocalName()

    def notify(self, event, trace):
        self.fireNotifiers(event, trace)

    def fireNotifiers(self, event, trace):
        """
        Fire all our registerd local-notifiers
        """
        nlist = self.notifiers.get(vtrace.NOTIFY_ALL, [])
        for notifier in nlist:
            try:
                notifier.handleEvent(event, trace)
            except:
                print("ERROR - Exception in notifier:", traceback.format_exc())

        nlist = self.notifiers.get(event, [])
        for notifier in nlist:
            try:
                notifier.handleEvent(event, trace)
            except:
                print("ERROR - Exception in notifier:", traceback.format_exc())

    def registerNotifier(self, event, notif):
        """
        Register a sub-notifier to get the remote callback's via
        our local delivery.
        """
        nlist = self.notifiers.get(event)
        nlist.append(notif)

    def deregisterNotifier(self, event, notif):
        nlist = self.notifiers.get(event)
        nlist.remove(notif)
