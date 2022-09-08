
"""
Cobra's built in clustering framework
"""

import gc
import sys
import time
import struct
import socket
import logging
import traceback
import threading
import subprocess
import multiprocessing
import urllib.request as url_req

import cobra
from . import dcode

logger = logging.getLogger(__name__)

queen_port = 32124

cluster_port = 32123
cluster_ip = "224.69.69.69"

sub_cmd = """
import cobra.cluster
cobra.cluster.getAndDoWork("%s", docode=%s)
"""

class InvalidInProgWorkId(Exception):
    def __init__(self, workid):
        Exception.__init__(self, "Work ID %d is not valid" % workid)
        self.workid = workid

class ClusterWork(object):
    """
    Extend this object to create your own work units.  Do it in
    a proper module (and not __main__ to be able to use this
    in conjunction with cobra.dcode).
    """
    def __init__(self, timeout=None):
        object.__init__(self)
        self.id = None # Set by adding to the server
        self.server = None # Set by ClusterClient
        self.starttime = 0
        self.endtime = 0 # Both are set by worker before and after work()
        self.timeout = timeout
        self.touchtime = None
        self.excinfo = None # Will be exception traceback on work unit fail.

    def touch(self): # heh...
        """
        Update the internal "touch time" which is used by the timeout
        subsystem to see if this work unit has gone too long without
        making progress...
        """
        self.touchtime = time.time()

    def isTimedOut(self):
        """
        Check if this work unit is timed out.
        """
        if self.timeout is None:
            return False
        if self.touchtime is None:
            return False
        if self.endtime != 0:
            return False
        return (self.touchtime + self.timeout) < time.time()

    def work(self):
        """
        Actually do the work associated with this work object.
        """
        for i in range(10):
            self.setCompletion(i*10)
            self.setStatus("Sleeping: %d" % i)
            time.sleep(1)

    def done(self):
        """
        This is called back on the server once a work unit
        is complete and returned.
        """
        pass

    def setCompletion(self, percent):
        """
        Work units may call this whenever they like to
        tell the server how far along their work they are.
        """
        self.touch()
        self.server.setWorkCompletion(self.id, percent)

    def setStatus(self, status):
        """
        Work units may call this to inform the server of
        their status.
        """
        self.touch()
        self.server.setWorkStatus(self.id, status)

    def openSharedFile(self, filename):
        '''
        A helper API to open a file like object on the server.

        Example:
            fd = self.openSharedFile('/foo/bar/baz')
            fbytes = fd.read()

        NOTE: The server must use shareFileToWorkers().
        '''
        uri = self.server.openSharedFile( filename )
        return cobra.CobraProxy(uri)

    def getServerObject(self, objname):
        '''
        Get a CobraProxy for an object shared by the ClusterServer (eg. a VivWorkspace)
        '''
        uri = self.server.getServerObjectUri(objname)
        proxy = cobra.CobraProxy(uri, timeout=60, retrymax=3)
        return proxy

class ClusterCallback:
    """
    Place one of these in the ClusterServer to get synchronous
    event information about what's going on in the cluster server.
    (mostly for the GUI).
    """

    def workAdded(self, server, work):
        pass
    def workGotten(self, server, work):
        pass
    def workStatus(self, server, workid, status):
        pass
    def workCompletion(self, server, workid, completion):
        pass
    def workDone(self, server, work):
        pass
    def workFailed(self, server, work):
        pass
    def workTimeout(self, server, work):
        pass
    def workCanceled(self, server, work):
        pass

class VerboseCallback(ClusterCallback):
    # This is mostly for testing...
    def workAdded(self, server, work):
        logger.debug("WORK ADDED: %d", work.id)

    def workGotten(self, server, work):
        logger.debug("WORK GOTTEN: %d", work.id)

    def workStatus(self, server, workid, status):
        logger.debug("WORK STATUS: (%d) %s", (workid, status))

    def workCompletion(self, server, workid, completion):
        logger.debug("WORK COMPLETION: (%d) %d%%", workid, completion)

    def workDone(self, server, work):
        logger.debug("WORK DONE: %d", work.id)

    def workFailed(self, server, work):
        logger.debug("WORK FAILED: %d", work.id)

    def workTimeout(self, server, work):
        logger.debug("WORK TIMEOUT: %d", work.id)

    def workCanceled(self, server, work):
        logger.debug("WORK CANCELED %d", work.id)

import collections

class ClusterServer:

    def __init__(self, name, maxsize=None, docode=False, bindsrc="", cobrad=None):
        """
        The cluster server is the core of the code that manages work units.

        Arguments:
            maxsize - How big should the work queue be before add blocks
            docode  - Should we also be a dcode server?
            bindsrc - Should we bind a src IP for our multicast announcements?
            cobrad  - Should we use an existing cobra daemon to share our objects?
        """
        self.go = True
        self.name = name
        self.queens = []
        self.nextwid = 0
        self.inprog = {}
        self.sharedfiles = {}
        self.maxsize = maxsize
        self.queue = collections.deque()
        self.qcond = threading.Condition()
        self.widiter = iter(range(999999999))

        # Initialize a cobra daemon if needed
        if cobrad is None:
            cobrad = cobra.CobraDaemon(host="", port=0)
        self.cobrad = cobrad
        self.cobraname = self.cobrad.shareObject(self)

        # Setup our transmission socket
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendsock.bind((bindsrc, 0))

        # Set this to a ClusterCallback extension if
        # you want notifications.
        self.callback = None

        if docode:
            dcode.enableDcodeServer(daemon=self.cobrad)

        # Fire the timeout monitor thread...
        thr = threading.Thread(target=self.timerThread)
        thr.setDaemon(True)
        thr.start()

    def addClusterQueen(self, queenhost):
        '''
        Inform the ClusterServer about the presence of a ClusterQueen instance
        on the given host.  When the ClusterServer begins to announce work,
        he will do so in "infrastructure mode" and ask any set queens for help.
        '''
        queen = cobra.CobraProxy('cobra://%s:%d/ClusterQueen' % (queenhost, queen_port))
        self.queens.append( queen )

    def shareFileToWorkers(self, filename):
        '''
        Add a file to the list of files which are "shared" to worker clients.
        This allows workers to access a file from the server.

        Example:
            s.shareFileToWorkers('/path/to/file')

        NOTE: Workers may use the openSharedFile() API to access them.
        '''
        self.sharedfiles[filename] = True

    def openSharedFile(self, filename):
        '''
        Return a URI for an open file decriptor for the specified filename.

        NOTE: use openSharedFile() method on work unit to get back a proxy.
        '''
        if not self.sharedfiles.get(filename):
            raise Exception('File %s is not shared!')

        fd = open(filename, 'rb')

        cname = self.cobrad.shareObject(fd, doref=True)
        host,port = cobra.getLocalInfo()

        uri = 'cobra://%s:%d/%s' % (host, port, cname)
        return uri

    def getServerInfo(self): 
        '''
        Return server host/port information
        '''
        return cobra.getLocalInfo() 

    def getServerObjectUri(self, objname):
        '''
        Returns a Cobra URI to access a given object by name.
        Useful for ClusterWork objects to access shared resources.
        '''
        host, port = self.getServerInfo()
        return 'cobra://%s:%d/%s' % (host, port, objname)

    def __touchWork(self, workid):
        # Used to both validate an inprog workid *and*
        # update it's timestamp for the timeout thread
        work = self.inprog.get(workid, None)
        if work is None:
            raise InvalidInProgWorkId(workid)
        work.touch()

    def __cleanWork(self, workid):
        # Used by done/timeout/etc to clea up an in
        # progress work unit
        return self.inprog.pop(workid, None)

    def timerThread(self):
        # Internal function to monitor work unit time
        while self.go:
            try:
                for id,work in self.inprog.items():
                    if work.isTimedOut():
                        self.timeoutWork(work)

            except Exception as e:
                logger.info("ClusterTimer: %s", e)

            time.sleep(2)

    def shutdownServer(self):
        self.go = False

    def announceWork(self):
        """
        Announce to our multicast cluster peers that we have work
        to do! (Or use a queen to proxy to them...)
        """
        if self.queens:
            for q in self.queens:
                try:
                    q.proxyAnnounceWork(self.name, self.cobraname, self.cobrad.port)
                except Exception as e:
                    logger.warning('Queen Error: %s', e)

        else:
            buf = "cobra:%s:%s:%d" % (self.name, self.cobraname, self.cobrad.port)
            self.sendsock.sendto(buf.encode('utf-8'), (cluster_ip, cluster_port))

    def runServer(self, firethread=False):

        if firethread:
            thr = threading.Thread(target=self.runServer)
            thr.setDaemon(True)
            thr.start()

        else:
            self.cobrad.fireThread()
            while self.go:

                if len(self.queue):
                    self.announceWork()

                time.sleep(2)

    def inQueueCount(self):
        """
        How long is the current work unit queue.
        """
        return len(self.queue)

    def inProgressCount(self):
        """
        How many work units are in progress?
        """
        return len(self.inprog)

    def addWork(self, work):
        """
        Add a work object to the ClusterServer.  This 
        """
        if not isinstance(work, ClusterWork):
            raise Exception("%s is not a ClusterWork extension!")

        # If this work has no ID, give it one
        if work.id is None:
            work.id = next(self.widiter)

        self.qcond.acquire()
        if self.maxsize is not None:
            while len(self.queue) >= self.maxsize:
                self.qcond.wait()
        self.queue.append(work)
        self.qcond.release()

        if self.callback:
            self.callback.workAdded(self, work)

    def getWork(self):

        self.qcond.acquire()

        try:
            ret = self.queue.popleft()
        except IndexError:
            self.qcond.release()
            return None

        self.qcond.notifyAll()
        self.qcond.release()

        self.inprog[ret.id] = ret
        self.__touchWork(ret.id)

        if self.callback:
            self.callback.workGotten(self, ret)

        return ret


    def doneWork(self, work):
        """
        Used by the clients to report work as done.
        """
        self.__cleanWork(work.id)

        work.done()
        if self.callback:
            self.callback.workDone(self, work)

    def timeoutWork(self, work):
        """
        This method may be over-ridden to handle
        work units that time our for whatever reason.
        """
        self.__cleanWork(work.id)
        if self.callback:
            self.callback.workTimeout(self, work)

    def failWork(self, work):
        """
        This is called for a work unit that is in a failed state.  This is most
        commonly that the work() method has raised an exception.
        """
        self.__cleanWork(work.id)
        if self.callback:
            self.callback.workFailed(self, work)

    def cancelAllWork(self, inprog=True):
        """
        Cancel all of the currently pending work units.  You may
        specify inprog=False to cancel all *queued* work units
        but allow inprogress work units to complete.
        """
        self.qcond.acquire()
        qlist = list(self.queue)
        self.queue.clear()

        if inprog:
            p = self.inprog
            self.inprog = {}
            qlist.extend(p.values())

        self.qcond.notifyAll()
        self.qcond.release()

        if self.callback:
            for w in qlist:
                self.callback.workCanceled(self, w)
        
    def cancelWork(self, workid):
        """
        Cancel a work unit by ID.
        """
        cwork = self.__cleanWork(workid)

        # Remove it from the work queue
        # (if we didn't find in inprog)
        if cwork is None:
            self.qcond.acquire()
            qlist = list(self.queue)
            self.queue.clear()
            for work in qlist:
                if work.id != workid:
                    self.queue.append(work)
                else:
                    cwork = work

            self.qcond.notifyAll()
            self.qcond.release()

        if cwork is None:
            return

        if self.callback:
            self.callback.workCanceled(self, cwork)

    def setWorkStatus(self, workid, status):
        """
        Set the humon readable status for the given work unit.
        """
        self.__touchWork(workid)
        if self.callback:
            self.callback.workStatus(self, workid, status)

    def setWorkCompletion(self, workid, percent):
        """
        Set the percentage completion status for this work unit.
        """
        self.__touchWork(workid)
        if self.callback:
            self.callback.workCompletion(self, workid, percent)

class ClusterClient:

    """
    Listen for our name (or any name if name=="*") on the cobra cluster
    multicast address and if we find a server in need, go help.

    maxwidth is the number of work units to do in parallel
    docode will enable code sharing with the server
    """

    def __init__(self, name, maxwidth=multiprocessing.cpu_count(), docode=False):
        self.go = True
        self.name = name
        self.width = 0
        self.maxwidth = maxwidth
        self.docode = docode

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("",cluster_port))
        mreq = struct.pack(b"4sL", socket.inet_aton(cluster_ip), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def processWork(self):
        """
        Runs handing out work up to maxwidth until self.go == False.
        """
        while self.go:
            
            buf, sockaddr = self.sock.recvfrom(4096)
            if self.width >= self.maxwidth:
                continue

            # make it a string again..
            buf = buf.decode('utf-8')

            server, svrport = sockaddr

            if not buf.startswith("cobra"):
                continue

            info = buf.split(":")

            ilen = len(info)
            if ilen == 4:
                cc,name,cobject,portstr = info
            elif ilen == 5:
                cc,name,cobject,portstr,server = info
            else:
                continue

            if (self.name != name) and (self.name != "*"):
                logger.debug("skipping work, not me...(%r != %r)", name, self.name)
                continue

            port = int(portstr)

            uri = "%s://%s:%d/%s" % (cc,server,port,cobject)
            self.fireRunner(uri)

    def fireRunner(self, uri):
        thr = threading.Thread(target=self.threadForker, args=(uri,))
        thr.setDaemon(True)
        thr.start()

    def threadForker(self, uri):
        self.width += 1
        cmd = sub_cmd % (uri, self.docode)
        try:
            sub = subprocess.Popen([sys.executable, '-c', cmd], stdin=subprocess.PIPE)
            sub.wait()
        finally:
            self.width -= 1

class ClusterQueen:

    def __init__(self, ifip, recast=True):

        # Setup our transmission socket
        self.sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendsock.bind((ifip, 0))

        # FIXME TODO make her optionally a multicast listener that re-broadcasts
        # to her subjects...

    def proxyAnnounceWork(self, name, cobraname, port):
        """
        Send out a multicast announcement to our subjects to go help
        a cluster server.
        """
        # Get the host IP from the connection information
        host, x = cobra.getCallerInfo()
        buf = "cobra:%s:%s:%d:%s" % (name, cobraname, port, host)
        self.sendsock.sendto(buf.encode('utf-8'), (cluster_ip, cluster_port))

def getHostPortFromUri(uri):
    """
    Take the server URI and pull out the
    host and port for use in building the
    dcode uri.
    """
    x = url_req.Request(uri)
    port = None
    hparts = x.host.split(":")
    host = hparts[0]
    if len(hparts):
        port = int(hparts[1])
    return host,port

def workThread(server, work):
    try:
        work.server = server
        work.starttime = time.time()
        work.touch()
        work.work()
        work.endtime = time.time()
        work.server = None
        server.doneWork(work)

    except InvalidInProgWorkId: # the work was canceled
        pass # Nothing to do, the server already knows

    except Exception:
        # Tell the server that the work unit failed
        formatted = traceback.format_exc()
        work.excinfo = formatted
        logger.error(formatted)
        server.failWork(work)

def runAndWaitWork(server, work):

    work.touch()
    thr = threading.Thread(target=workThread, args=(server, work))
    thr.setDaemon(True)
    thr.start()

    # Wait around for done or timeout
    while True:
        if work.isTimedOut():
            break

        # If the thread is done, lets get out.
        if not thr.isAlive():
            break

        # If our parent, or some thread closes stdin,
        # time to pack up and go.
        if sys.stdin.closed:
            break

        time.sleep(2)

def getAndDoWork(uri, docode=False):

    # If we wanna use dcode, set it up
    logger.debug("getAndDoWork: uri=", uri)
    try:
        if docode:
            host,port = getHostPortFromUri(uri)
            cobra.dcode.addDcodeServer(host, port=port)

        # Use a cobra proxy with timeout/maxretry so we
        # don't hang forever if the server goes away
        proxy = cobra.CobraProxy(uri, timeout=60, retrymax=3)

        work = proxy.getWork()
        # If we got work, do it.
        if work is not None:
            runAndWaitWork(proxy, work)

    except Exception:
        logger.error(traceback.format_exc())

    # Any way it goes we wanna exit now.  Work units may have
    # spun up non-daemon threads, so lets GTFO.
    gc.collect() # Try to call destructors
    sys.exit(0)  # GTFO

