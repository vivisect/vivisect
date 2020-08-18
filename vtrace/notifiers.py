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
import logging
import traceback

import vtrace


logger = logging.getLogger(__name__)


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
        logger.info("Got event: %d from pid %d", event, trace.getPid())


class VerboseNotifier(Notifier):
    def notify(self, event, trace):
        logger.info("PID %d - ThreadID (%d) got", trace.getPid(), trace.getMeta("ThreadId"))
        if event == vtrace.NOTIFY_ALL:
            ("WTF, how did we get a vtrace.NOTIFY_ALL event?!?!")
        elif event == vtrace.NOTIFY_SIGNAL:
            signo = trace.getCurrentSignal()
            ("vtrace.NOTIFY_SIGNAL %d (0x%08x)" % (signo, signo))
            if trace.getMeta("Platform") == "windows":
                logger.info(repr(trace.getMeta("Win32Event")))
        elif event == vtrace.NOTIFY_BREAK:
            logger.info("vtrace.NOTIFY_BREAK")
            logger.info("\tIP: 0x%08x", trace.getProgramCounter())
        elif event == vtrace.NOTIFY_SYSCALL:
            logger.info("vtrace.NOTIFY_SYSCALL")
        elif event == vtrace.NOTIFY_CONTINUE:
            logger.info("vtrace.NOTIFY_CONTINUE")
        elif event == vtrace.NOTIFY_EXIT:
            logger.info("vtrace.NOTIFY_EXIT")
            logger.info("\tExitCode: %d", trace.getMeta("ExitCode"))
        elif event == vtrace.NOTIFY_ATTACH:
            logger.info("vtrace.NOTIFY_ATTACH")
        elif event == vtrace.NOTIFY_DETACH:
            logger.info("vtrace.NOTIFY_DETACH")
        elif event == vtrace.NOTIFY_LOAD_LIBRARY:
            logger.info("vtrace.NOTIFY_LOAD_LIBRARY")
            logger.info("\tLoaded library %s", trace.getMeta('LatestLibrary'))
        elif event == vtrace.NOTIFY_UNLOAD_LIBRARY:
            logger.info("vtrace.NOTIFY_UNLOAD_LIBRARY")
        elif event == vtrace.NOTIFY_CREATE_THREAD:
            logger.info("vtrace.NOTIFY_CREATE_THREAD")
            logger.info("\tNew thread - ThreadID: %d", trace.getMeta("ThreadId"))
        elif event == vtrace.NOTIFY_EXIT_THREAD:
            logger.info("vtrace.NOTIFY_EXIT_THREAD")
            logger.info("Thread exited - ThreadID: %d", trace.getMeta("ExitThread", -1))
        elif event == vtrace.NOTIFY_STEP:
            logger.info("vtrace.NOTIFY_STEP")
        else:
            logger.warning("Unhandled vtrace event type of: %d", event)


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
            except Exception:
                logger.error("Exception in notifier:\n%s", traceback.format_exc())

        nlist = self.notifiers.get(event, [])
        for notifier in nlist:
            try:
                notifier.handleEvent(event, trace)
            except Exception:
                logger.error("Exception in notifier:\n%s", traceback.format_exc())

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
