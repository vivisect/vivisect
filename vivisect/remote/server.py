import os
import sys
import cobra
import queue
import logging
import argparse
import threading

import cobra.dcode

import envi.common as e_common
import envi.threads as e_threads

import vivisect.cli as v_cli
import vivisect.parsers as v_parsers
import vivisect.storage.basicfile as viv_basicfile

from vivisect.const import *

logger = logging.getLogger(__name__)

viv_port = 0x4074

viv_s_ip = '224.56.56.56'
viv_s_port = 26998

timeo_wait = 10
timeo_sock = 30
timeo_aban = 120   # 2 minute timeout for abandon

# This should *only* rev when they're truly incompatible
server_version = 20130820

class BadChannel(Exception):
    def __repr__(self):
        return "Bad Channel: %r" % Exception.__repr__(self)

class VivServerClient:
    '''
    Implement "glue" methods for the vivisect workspace client to
    talk to the server...
    '''
    def __init__(self, vw, server, wsname):
        self.vw = vw
        self.chanid = None
        self.wsname = wsname
        self.server = server
        self.eoffset = 0
        self.q = queue.Queue()  # The actual local Q we deliver to

    @e_threads.firethread
    def _eatServerEvents(self):
        while True:
            for event in self.server.getNextEvents(self.chanid):
                self.q.put(event)

    def vprint(self, msg):
        return self.server.vprint(msg)

    def _fireEvent(self, event, einfo, local=False, skip=None):
        try:
            retval = self.server._fireEvent(self.chanid, event, einfo, local=local, skip=skip)
        except BadChannel as bce:
            logger.warning('Bad Channel: %r.  Creating a new channel.' % bce)
            self.createEventChannel()

    def createEventChannel(self):
        self.chanid = self.server.createEventChannel(self.wsname)
        self._eatServerEvents()
        return self.chanid

    def exportWorkspace(self):
        # Retrieve the big initial list of viv events
        return self.server.getNextEvents(self.chanid)

    def waitForEvent(self, chanid, timeout=None):
        return self.q.get(timeout=timeout)

    def getLeaderLocations(self):
        try:
            return self.server.getLeaderLocations(self.wsname)
        except Exception as e:
            logger.warning("error in getLeaderLocations(): %r (is server up to date?)" % e)
            return {}

    def getLeaderSessions(self):
        try:
            return self.server.getLeaderSessions(self.wsname)
        except Exception as e:
            logger.warning("error in getLeaderSessions(): %r (is server up to date?)" % e)
            return {}


class VivClientChannel:
    '''
    Store data about each channel (ie. comms between client and server)
    For the most part this is one-directional comms, but this object stores
    details about the channel (and the client attached to it)
    '''
    def __init__(self, ws, events=[], chanid=None):
        if chanid:
            self.id = chanid
        else:
            self.id = e_common.hexify(os.urandom(16))

        self.ws = ws
        self.q = e_threads.ChunkQueue(items=events)
        self.chanleaders = []
        self.oldchan = True

class VivServerWorkspace:
    '''
    Store data about the workspaces provided by this server.
    '''
    def __init__(self, wspath):
        self.lock = threading.Lock()
        self.path = wspath
        self.events = []
        self.users = {}
        self.leaders = {}
        self.leaderloc = {}

    def registerChannel(self, chanobj):
        '''
        Add the channel's event queue to the Workspace's "users" dict
        '''
        self.users[chanobj.id] = chanobj.q

    def deregisterChannel(self, chanobj):
        '''
        Remove the channel's event queue from Workspace's "users" dict
        '''
        self.deregisterChannelById(chanobj.id)

    def deregisterChannelById(self, chanid):
        '''
        Deregister by id, without a whole VivClientChannel object
        '''
        self.users.pop(chanid, None)


class VivServer:

    def __init__(self, dirname=''):
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

        for chanid in list(self.chandict.keys()):
            chanobj = self.chandict.get(chanid)
            # NOTE: double check because we're lock free...
            if chanobj is None:
                continue

            if chanobj.q.abandoned(timeo_aban):
                self.cleanupChannel(chanobj.id)

    @e_threads.maintthread(30)
    def _saveWorkspaceThread(self):
        for ws in self.wsdict.values():
            if ws.events:
                nowevents = ws.events
                with ws.lock:
                    ws.events = []  # start a new events list...

                viv_basicfile.vivEventsAppendFile(ws.path, nowevents)

    def _req_wsinfo(self, wsname):
        ws = self.wsdict.get(wsname)
        if ws is None:
            raise Exception('Invalid Workspace Name: %s' % wsname)
        return ws

    def listWorkspaces(self):
        '''
        Get a list of the workspaces this server is willing to share.
        '''
        return list(self.wsdict.keys())

    def addNewWorkspace(self, wsname, events):
        wspath = os.path.join(self.path, wsname)
        wspath = os.path.realpath(wspath)
        if not wspath.startswith(self.path):
            raise Exception('Nice try liberty... ;)')

        if os.path.exists(wspath):
            raise Exception('Workspace %s already exists!' % wsname)

        wsdir = os.path.dirname(wspath)
        if not os.path.isdir(wsdir):
            os.makedirs(wsdir, 0o750)

        viv_basicfile.vivEventsToFile(wspath, events)
        ws = VivServerWorkspace(wspath)
        self.wsdict[wsname] = ws

    def _loadWorkspaces(self):

        # First, ditch any that are missing
        for wsname in self.wsdict.keys():
            ws = self.wsdict.get(wsname)
            if not os.path.isfile(ws.path):
                self.wsdict.pop(wsname, None)

        for dirname, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                wspath = os.path.join(dirname, filename)
                wsname = os.path.relpath(wspath, self.path)

                if not os.path.isfile(wspath):
                    continue

                with open(wspath, 'rb') as f:
                    ext = f.read(6)

                if not ext:
                    continue

                if not v_parsers.guessFormat(ext) in ('viv', 'mpviv'):
                    continue

                ws = self.wsdict.get(wsname)
                if ws is None:
                    # Initialize the workspace info tuple
                    lock = threading.Lock()
                    ws = VivServerWorkspace(wspath)
                    logger.debug('loaded: %s', wsname)
                    self.wsdict[wsname] = ws

    def getNextEvents(self, chanid):
        chanobj = self.chandict.get(chanid)
        if chanobj is None:
            raise BadChannel('Invalid Channel: %s' % chanid)
        return chanobj.q.get(timeout=timeo_wait)

    # All APIs from here down are basically mirrors of the workspace APIs
    # used with remote workspaces, with a prepended chanid first argument

    def _fireEvent(self, chanid, event, einfo, local=False, skip=None):
      try:  
        #print("_fireEvent: %r %r %r %r %r" % (chanid, event, einfo, local, skip))

        if chanid in self.chandict:
            chanobj = self.chandict.get(chanid)
            #lock, fpath, pevents, users, leaders, leaderloc = chanobj.wsinfo
            ws = chanobj.ws
            chanobj.oldclient = False

        elif chanid in self.wsdict:
            # DEPRECATED: this is for backwards compat.  use only the chandict code one year from today, 5/10/2022.
            wsname = chanid
            ws = self._req_wsinfo(wsname)
            #lock, fpath, pevents, users, _, _ = wsinfo
            # cheat for older clients... they don't get all the follow-the-leader goodness until they upgrade
            chanobj = VivClientChannel(ws)
            chanobj.chanleaders = []
            ws.leaders = {}
            ws.leaderloc = {}

        else:
            raise BadChannel("BAD CHANNEL: _fireEvent: %r %r %r %r %r" % (chanid, event, einfo, local, skip))

        evtup = (event, einfo)
        with ws.lock:
            # Transient events do not get saved
            if not event & VTE_MASK:
                ws.events.append(evtup)

            else:
                vtevent = event ^ VTE_MASK
                if vtevent == VTE_FOLLOWME:
                    pass

                elif vtevent == VTE_IAMLEADER:
                    logger.info("VTE_IAMLEADER: %r" % repr(evtup))
                    uuid, user, fname, locexpr = einfo
                    ws.leaders[uuid] = (user, fname)
                    ws.leaderloc[uuid] = locexpr
                    chanobj.chanleaders.append(uuid)

                elif vtevent == VTE_FOLLOWME:
                    logger.info("VTE_FOLLOWME: %r" % repr(evtup))
                    uuid, expr = einfo
                    ws.leaderloc[uuid] = expr

                elif vtevent == VTE_KILLLEADER:
                    logger.info("VTE_KILLLEADER: %r" % repr(evtup))
                    uuid = einfo
                    ws.leaders.pop(uuid, None)
                    ws.leaderloc.pop(uuid, None)

                elif vtevent == VTE_MODLEADER:
                    logger.info("VTE_MODLEADER: %r" % repr(evtup))
                    uuid, user, fname = einfo
                    ws.leaders[uuid] = (user, fname)


            # SPEED HACK
            [q.append(evtup) for chanid, q in ws.users.items() if chanid != skip]

        return None
      except Exception as e:
          logger.warning('EXCEPTION: %r', e, exc_info=1)

    def createEventChannel(self, wsname):
        logger.info("Creating new channel for %s...", wsname)
        ws = self._req_wsinfo(wsname)

        #lock, fpath, pevents, users, leaders, leaderloc = wsinfo
        with ws.lock:
            events = []
            events.extend(viv_basicfile.vivEventsFromFile(ws.path))
            logger.debug('... initial event list size: %d', len(events))
            events.extend(ws.events)
            logger.debug('... updated event list size: %d', len(events))

            # Channels and Workspaces are interlinked.
            chanobj = VivClientChannel(ws, events)
            ws.registerChannel(chanobj)
            self.chandict[chanobj.id] = chanobj

        return chanobj.id

    def getLeaderLocations(self, wsname):
        ws = self._req_wsinfo(wsname)
        #lock, path, events, users, leaders, leaderloc = wsinfo
        return dict(ws.leaderloc)

    def getLeaderSessions(self, wsname):
        ws = self._req_wsinfo(wsname)
        #lock, path, events, users, leaders, leaderloc = wsinfo
        return dict(ws.leaders)

    def cleanupChannel(self, chanid):
        chanobj = self.chandict.get(chanid, None)
        if chanobj is None:
            logger.warning("Attempting to clean up nonexistent channel: %r" % chanid)
            return

        # Remove all channels originating from this channel
        for uuid in chanobj.chanleaders:
            self._fireEvent(chanid, VTE_KILLLEADER | VTE_MASK, uuid)

        # Remove from the workspace clients
        #lock, fpath, pevents, users, leaders, leaderloc = chanobj.wsinfo
        ws = chanobj.ws
        with ws.lock:
            userinfo = ws.deregisterChannelById(chanid)

        # Remove from our chandict
        self.chandict.pop(chanid, None)


def getServerWorkspace(server, wsname):
    vw = v_cli.VivCli()
    cliproxy = VivServerClient(vw, server, wsname)
    vw.initWorkspaceClient(cliproxy)
    return vw


def connectToServer(hostname, port=viv_port):
    builder = cobra.initSocketBuilder(hostname, port)
    builder.setTimeout(timeo_sock)
    server = cobra.CobraProxy("cobra://%s:%d/VivServer" % (hostname, port), msgpack=True)
    version = server.getServerVersion()
    if version != server_version:
        raise Exception('Incompatible Server: his ver: %d our ver: %d' % (version, server_version))
    return server


def runMainServer(dirname='', port=viv_port, ipython=False):
    vsrv = VivServer(dirname=dirname)
    daemon = cobra.CobraDaemon(port=port, msgpack=True)
    daemon.recvtimeout = timeo_sock
    daemon.shareObject(vsrv, 'VivServer')

    if ipython:
        # fire off ipython in a thread.  stdin/out/err used.
        # very helpful for debugging
        import envi.interactive as ei
        t = threading.Thread(target=ei.dbg_interact, args=(locals(), globals()), daemon=True)
        t.start()

    daemon.serve_forever()


def setup():
    ap = argparse.ArgumentParser('Start a vivisect server to share workspaces')
    ap.add_argument('dirn', help='A directory full of *.viv files to share')
    ap.add_argument('--port', '-p', type=int, default=viv_port,
                    help='The port to start server on (defaults to %d)' % viv_port)
    ap.add_argument('-v', '--verbose', dest='verbose', default=2, action='count',
                    help='Enable verbose mode (multiples matter: -vvvv)')
    ap.add_argument('-I', '--ipython', default=False, action='store_true',
                    help='Drop to an interactive python shell after loading')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    vdir = os.path.abspath(opts.dirn)
    if not os.path.isdir(vdir):
        logger.error('%s is not a valid directory!', vdir)
        return -1

    # setup logging
    verbose = min(opts.verbose, len(e_common.LOG_LEVELS)-1)
    level = e_common.LOG_LEVELS[verbose]
    e_common.initLogging(logger, level=level)

    print(f'Server starting (port: {opts.port}) for path: {vdir}')
    runMainServer(vdir, opts.port, opts.ipython)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
