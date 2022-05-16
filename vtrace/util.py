# Copyright (C) 2007 Invisigoth - See LICENSE file for details

import vtrace
import vtrace.notifiers as v_notifiers
import vtrace.rmi as v_rmi


class TraceManager:
    """
    A trace-manager is a utility class to extend from when you may be dealing
    with multiple tracer objects.  It allows for persistant mode settings and
    persistent metadata as well as bundling a DistributedNotifier.  You may also
    extend from this to get auto-magic remote stuff for your managed traces.
    """
    def __init__(self, trace=None):
        self.trace = trace
        self.dnotif = v_notifiers.DistributedNotifier()
        self.modes = {}  # See docs for trace modes
        self.metadata = {}  # Like traces, but persistant

    def manageTrace(self, trace):
        """
        Set all the modes/meta/notifiers in this trace for management
        by this TraceManager.
        """
        self.trace = trace
        if vtrace.remote:
            trace.registerNotifier(vtrace.NOTIFY_ALL, v_rmi.getCallbackProxy(trace, self.dnotif))
        else:
            trace.registerNotifier(vtrace.NOTIFY_ALL, self.dnotif)

        for name, val in self.modes.items():
            trace.setMode(name, val)

        for name, val in self.metadata.items():
            trace.setMeta(name, val)

    def unManageTrace(self, trace):
        """
        Untie this trace manager from the trace.
        """
        if vtrace.remote:
            trace.deregisterNotifier(vtrace.NOTIFY_ALL, v_rmi.getCallbackProxy(trace, self.dnotif))
        else:
            trace.deregisterNotifier(vtrace.NOTIFY_ALL, self.dnotif)

    def setMode(self, name, value):
        if self.trace is not None:
            self.trace.setMode(name, value)
        self.modes[name] = value

    def getMode(self, name, default=False):
        if self.trace is not None:
            return self.trace.getMode(name, default)
        return self.modes.get(name, default)

    def setMeta(self, name, value):
        if self.trace is not None:
            self.trace.setMeta(name, value)
        self.metadata[name] = value

    def getMeta(self, name, default=None):
        if self.trace is not None:
            return self.trace.getMeta(name, default)
        return self.metadata.get(name, default)

    def registerNotifier(self, event, notif):
        self.dnotif.registerNotifier(event, notif)

    def deregisterNotifier(self, event, notif):
        self.dnotif.deregisterNotifier(event, notif)

    def fireLocalNotifiers(self, event, trace):
        """
        Deliver a local event to the DistributedNotifier managing
        the traces. (used to locally bump notifiers)
        """
        self.dnotif.notify(event, trace)
