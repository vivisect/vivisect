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
        self.q = queue.Queue()  # The actual local Q we deliver to

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

    def waitForEvent(self, chan, timeout=None):
        return self.q.get(timeout=timeout)


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

        for chan in self.chandict.keys():
            chaninfo = self.chandict.get(chan)
            # NOTE: double check because we're lock free...
            if chaninfo is None:
                continue

            wsinfo, queue = chaninfo
            if queue.abandoned(timeo_aban):
                # Remove from our chandict
                self.chandict.pop(chan, None)
                # Remove from the workspace clients
                lock, fpath, pevents, users = wsinfo
                with lock:
                    users.pop(chan, None)

    @e_threads.maintthread(30)
    def _saveWorkspaceThread(self):
        for wsinfo in self.wsdict.values():
            lock, path, events, users = wsinfo
            if events:
                with lock:
                    wsinfo[2] = []  # start a new events list...

                viv_basicfile.vivEventsAppendFile(path, events)

    def _req_wsinfo(self, wsname):
        wsinfo = self.wsdict.get(wsname)
        if wsinfo is None:
            raise Exception('Invalid Workspace Name: %s' % wsname)
        return wsinfo

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
        wsinfo = [threading.Lock(), wspath, [], {}]
        self.wsdict[wsname] = wsinfo

    def _loadWorkspaces(self):

        # First, ditch any that are missing
        for wsname in self.wsdict.keys():
            wsinfo = self.wsdict.get(wsname)
            if not os.path.isfile(wsinfo[1]):
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

                wsinfo = self.wsdict.get(wsname)
                if wsinfo is None:
                    # Initialize the workspace info tuple
                    lock = threading.Lock()
                    wsinfo = [lock, wspath, [], {}]
                    logger.debug('loaded: %s', wsname)
                    self.wsdict[wsname] = wsinfo

    def getNextEvents(self, chan):
        chaninfo = self.chandict.get(chan)
        if chaninfo is None:
            raise Exception('Invalid Channel: %s' % chan)
        return chaninfo[1].get(timeout=timeo_wait)

    # All APIs from here down are basically mirrors of the workspace APIs
    # used with remote workspaces, with a prepended wsname first argument

    def _fireEvent(self, wsname, event, einfo, local=False, skip=None):
        lock, fpath, pevents, users = self._req_wsinfo(wsname)
        evtup = (event, einfo)
        with lock:
            # Transient events do not get saved
            if not event & VTE_MASK:
                pevents.append(evtup)
            # SPEED HACK
            [q.append(evtup) for (chan, q) in users.items() if chan != skip]

    def createEventChannel(self, wsname):
        wsinfo = self._req_wsinfo(wsname)
        chan = e_common.hexify(os.urandom(16))

        lock, fpath, pevents, users = wsinfo
        with lock:
            events = []
            events.extend(viv_basicfile.vivEventsFromFile(fpath))
            events.extend(pevents)
            # These must reference the same actual list object...
            queue = e_threads.ChunkQueue(items=events)
            users[chan] = queue
            self.chandict[chan] = [wsinfo, queue]

        return chan


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


def runMainServer(dirname='', port=viv_port):
    s = VivServer(dirname=dirname)
    daemon = cobra.CobraDaemon(port=port, msgpack=True)
    daemon.recvtimeout = timeo_sock
    daemon.shareObject(s, 'VivServer')
    daemon.serve_forever()


def setup():
    ap = argparse.ArgumentParser('Start a vivisect server to share workspaces')
    ap.add_argument('dirn', help='A directory full of *.viv files to share')
    ap.add_argument('--port', '-p', type=int, default=viv_port,
                    help='The port to start server on (defaults to %d)' % viv_port)
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    vdir = os.path.abspath(opts.dirn)
    if not os.path.isdir(vdir):
        logger.error('%s is not a valid directory!', vdir)
        return -1

    print(f'Server starting (port: {viv_port})')
    runMainServer(vdir, opts.port)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
