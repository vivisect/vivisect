"""
Cobra integration for remote debugging
"""
# Copyright (C) 2007 Invisigoth - See LICENSE file for details

import logging

import vtrace
import cobra


logger = logging.getLogger(__name__)
callback_daemon = None


def getTracerFactory():
    """
    Return a TracerFactory proxy object from the remote server
    """
    return cobra.CobraProxy("cobra://%s:%d/TracerFactory" % (vtrace.remote, vtrace.port))


class TraceProxyFactory:
    """
    A "factory" object for creating tracers and
    wrapping them up in a proxy instance to the
    *local* server.  This object is shared out
    via the pyro server for vtrace clients.
    """
    def getTrace(self):
        trace = vtrace.getTrace()
        host, port = cobra.getLocalInfo()
        unique = vtrace.cobra_daemon.shareObject(trace)
        trace.proxy = cobra.CobraProxy("cobra://%s:%d/%s" % (host, port, unique))
        return unique

    def releaseTrace(self, proxy):
        """
        When a remote system is done with a trace
        and wants the server to clean him up, hand
        the proxy object to this.
        """
        t = vtrace.cobra_daemon.unshareObject(proxy.__dict__.get("__cobra_name", None))
        if t is not None:
            t.release()


class RemoteTrace(cobra.CobraProxy):

    def __init__(self, *args, **kwargs):
        cobra.CobraProxy.__init__(self, *args, **kwargs)
        self.__dict__['_remote_released'] = False

    def isRemote(self):
        return True

    def buildNewTrace(self):
        return getRemoteTrace()

    def release(self):
        self.__dict__['_remote_released'] = True
        getTracerFactory().releaseTrace(self)

    def __del__(self):
        if not self.__dict__['_remote_released']:
            logger.warning('RemoteTrace del w/o release()!')


def getCallbackProxy(trace, notifier):
    """
    Get a proxy object to reference *notifier* from the
    perspective of *trace*.  The trace is specified so
    we may check on our side of the connected socket to
    give him the best possible ip address...
    """
    global callback_daemon
    port = getCallbackPort()
    host, nothing = trace._cobra_getsock().getSockName()
    unique = callback_daemon.getSharedName(notifier)
    if unique is None:
        unique = callback_daemon.shareObject(notifier)
    return cobra.CobraProxy("cobra://%s:%d/%s" % (host, port, unique))


def getCallbackPort():
    """
    If necessary, start a callback daemon.  Return the
    ephemeral port it was bound on.
    """
    global callback_daemon
    if callback_daemon is None:
        callback_daemon = cobra.CobraDaemon(port=0)
        callback_daemon.fireThread()
    return callback_daemon.port


def startCobraDaemon():
    if vtrace.cobra_daemon is None:
        vtrace.cobra_daemon = cobra.CobraDaemon(port=vtrace.port)
        vtrace.cobra_daemon.fireThread()


def getRemoteTrace():
    factory = getTracerFactory()
    unique = factory.getTrace()
    return RemoteTrace("cobra://%s:%d/%s" % (vtrace.remote, vtrace.port, unique))


def releaseRemoteTrace(proxy):
    getTracerFactory().releaseTrace(proxy)


def startVtraceServer():
    """
    Fire up the pyro server and share out our
    "trace factory"
    """
    startCobraDaemon()
    factory = TraceProxyFactory()
    vtrace.cobra_daemon.shareObject(factory, "TracerFactory")
    return vtrace.cobra_daemon
