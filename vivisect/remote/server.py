import os
import sys
import time
import cobra
import Queue
import optparse
import threading

import vivisect
import vivisect.cli as viv_cli
import vivisect.storage.basicfile as viv_basicfile

import cobra.dcode
import envi.threads as e_threads

from vivisect.const import *

viv_port = 0x4074

viv_s_ip = '224.56.56.56'
viv_s_port = 26998

timeo_wait  = 10
timeo_sock  = 30
timeo_aban  = 120   # 2 minute timeout for abandon

# This should *only* rev when they're truly incompatible
server_version = 20130820

class VivServerClient:
    '''
    Implement "glue" methods for the vivisect workspace client to
    talk to the server...
    '''
    def __init__(self, vw, server, wsname):
        self.vw = vw
        self.chan = None
        self.wsname = wsname
        self.server = server
        self.eoffset = 0
        self.q = Queue.Queue()  # The actual local Q we deliver to

    @e_threads.firethread
    def _eatServerEvents(self):
        while True:
            for event in self.server.getNextEvents(self.chan):
                self.q.put(event)

    def vprint(self, msg):
        return self.server.vprint(msg)

    def _fireEvent(self, event, einfo, local=False, skip=None):
        return self.server._fireEvent(self.wsname, event, einfo, local=local, skip=skip)

    def createEventChannel(self):
        self.chan = self.server.createEventChannel(self.wsname)
        self._eatServerEvents()
        return self.chan

    def exportWorkspace(self):
        # Retrieve the big initial list of viv events
        return self.server.getNextEvents(self.chan)

    def waitForEvent(self, chan):
        return self.q.get()

class VivServer:

    def __init__(self, dirname=""):
        self.path = os.path.abspath(dirname)

        self.wsdict = {}
        self.chandict = {}
        self.wslock = threading.Lock()

        self._loadWorkspaces()
        self._maintThread()
        self._saveWorkspaceThread()

    def vprint(self, msg):
        print(msg)

    def getServerVersion(self):
        return server_version

    @e_threads.maintthread(1)
    def _maintThread(self):

        for chan in self.chandict.keys():
            chaninfo = self.chandict.get(chan)
            # NOTE: double check because we're lock free...
            if chaninfo == None:
                continue

            wsinfo,queue = chaninfo
            if queue.abandoned(timeo_aban):
                # Remove from our chandict
                self.chandict.pop(chan, None)
                # Remove from the workspace clients
                lock, fpath, pevents, users = wsinfo
                with lock:
                    users.pop(chan,None)

    @e_threads.maintthread(30)
    def _saveWorkspaceThread(self):
        for wsinfo in self.wsdict.values():
            lock,path,events,users = wsinfo
            if events:
                with lock:
                    wsinfo[2] = []  # start a new events list...

                viv_basicfile.vivEventsAppendFile(path, events)
                
    def _req_wsinfo(self, wsname):
        wsinfo = self.wsdict.get(wsname)
        if wsinfo == None:
            raise Exception('Invalid Workspace Name: %s' % wsname)
        return wsinfo

    def listWorkspaces(self):
        '''
        Get a list of the workspaces this server is willing to share.
        '''
        return self.wsdict.keys()

    def addNewWorkspace(self, wsname, events):
        wspath = os.path.join(self.path, wsname)
        wspath = os.path.realpath(wspath)
        if not wspath.startswith(self.path):
            raise Exception('Nice try liberty... ;)')

        if os.path.exists(wspath):
            raise Exception('Workspace %s already exists!' % wsname)

        wsdir = os.path.dirname(wspath)
        if not os.path.isdir(wsdir):
            os.makedirs(wsdir, 0750)

        viv_basicfile.vivEventsToFile(wspath, events)
        wsinfo = [ threading.Lock(), wspath, [], {} ]
        self.wsdict[wsname] = wsinfo

    def _loadWorkspaces(self):

        # First, ditch any that are missing
        for wsname in self.wsdict.keys():
            wsinfo = self.wsdict.get(wsname)
            if not os.path.isfile(wsinfo[1]):
                self.wsdict.pop(wsname, None)

        def checkWorkspaceDir(arg, dirname, filenames):

            for filename in filenames:
                wspath = os.path.join(dirname,filename)
                wsname = os.path.relpath(wspath, self.path)

                if not os.path.isfile(wspath):
                    continue

                if not file(wspath,'rb').read(3) == 'VIV':
                    continue

                wsinfo = self.wsdict.get(wsname)
                if wsinfo == None:
                    # Initialize the workspace info tuple
                    lock = threading.Lock()
                    wsinfo = [ lock, wspath, [], {} ]
                    print('loaded: %s' % wsname)
                    self.wsdict[wsname] = wsinfo

        os.path.walk(self.path, checkWorkspaceDir, None)

    def getNextEvents(self, chan):
        chaninfo = self.chandict.get(chan)
        if chaninfo == None:
            raise Exception('Invalid Channel: %s' % chan)
        return chaninfo[1].get(timeout=timeo_wait)

    # All APIs from here down are basically mirrors of the workspace APIs
    # used with remote workspaces, with a prepended wsname first argument

    def _fireEvent(self, wsname, event, einfo, local=False, skip=None):
        lock, fpath, pevents, users = self._req_wsinfo(wsname)
        evtup = (event,einfo)
        with lock:
            # Transient events do not get saved
            if not event & VTE_MASK:
                pevents.append(evtup)
            # SPEED HACK
            [ q.append(evtup) for (chan,q) in users.items() if chan != skip ]

    def createEventChannel(self, wsname):
        wsinfo = self._req_wsinfo(wsname)
        chan = os.urandom(16).encode('hex')

        lock, fpath, pevents, users = wsinfo
        with lock:
            events = []
            events.extend( viv_basicfile.vivEventsFromFile( fpath ) )
            events.extend(pevents)
            # These must reference the same actual list object...
            queue = e_threads.ChunkQueue(items=events)
            users[chan] = queue
            self.chandict[chan] = [ wsinfo, queue ]

        return chan

def getServerWorkspace(server, wsname):
    vw = vivisect.cli.VivCli()
    cliproxy = VivServerClient(vw, server, wsname)
    vw.initWorkspaceClient( cliproxy )
    return vw

def connectToServer(hostname):
    builder = cobra.initSocketBuilder(hostname,viv_port)
    builder.setTimeout(timeo_sock)
    server = cobra.CobraProxy("cobra://%s:%d/VivServer" %  (hostname,viv_port), msgpack=True)
    version = server.getServerVersion()
    if version != server_version:
        raise Exception('Incompatible Server: his ver: %d our ver: %d' % (version, server_version))
    return server

def runMainServer(dirname=''):
    s = VivServer(dirname=dirname)
    daemon = cobra.CobraDaemon(port=viv_port, msgpack=True)
    daemon.recvtimeout = timeo_sock
    daemon.shareObject(s, 'VivServer')
    daemon.serve_forever()

def usage():
    print 'Usage: python -m vivisect.tools.server <vivdir>'
    print ''
    print 'NOTE: vivdir is simply a directory full of viv files to share'
    sys.exit(0)

if __name__ == '__main__':
    
    parser = optparse.OptionParser(usage='python -m vivisect.remote.server <vivdir>')
    options, argv = parser.parse_args()

    if len(argv) != 1:
        usage()

    vivdir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(vivdir):
        usage()

    print('Server Starting (port:%d)' % (viv_port,))
    runMainServer(vivdir)

