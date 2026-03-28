import os
import sys
import time
import cobra
import queue
import logging
import argparse
import threading

import cobra.dcode

import envi.config as e_config
import envi.common as e_common
import envi.threads as e_threads

import vivisect
import vivisect.cli as v_cli
import vivisect.parsers as v_parsers
import vivisect.storage.basicfile as viv_basicfile

from vivisect.const import *
from vivisect.defconfig import *

logger = logging.getLogger(__name__)

viv_port = 0x4074

viv_s_ip = '224.56.56.56'
viv_s_port = 26998

# DEFAULTS for non-configured use
timeout_wait = 10
timeout_sock = 50
timeout_aban = 120   # 2 minute timeout for abandon

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
        self._processlock = threading.Lock()
        self.eoffset = 0
        self.q = queue.Queue()  # The actual local Q we deliver to
        self._qtime = time.time()
        self._qcount = 0
        self._qcountfull = 0
        self._starttime = time.time()

    @e_threads.firethread
    def _eatServerEvents(self):
        while True:
            logger.debug("Starting a Workspace Event Processing run...")
            count = 0
            with self._processlock:
                for event in self.server.getNextEvents(self.chan):
                    count += 1
                    self.q.put(event)
            logger.debug("Workspace Event Processing run Complete. (%d events processed)", count)
            time.sleep(.01)

    def vprint(self, msg):
        return self.server.vprint(msg)

    def _fireEvent(self, event, einfo, local=False, skip=None):
        return self.server._fireEvent(self.chan, event, einfo, local=local, skip=skip)

    def createEventChannel(self):
        self.chan = self.server.createEventChannel(self.wsname)
        self._monitorEventQueuePerf()
        logger.debug("VivServerClient: Event Channel created, firing _eatServerEvents() in separate thread")
        self._eatServerEvents()
        logger.debug("Waiting for initial Workspace Events to finish processing")
        self.waitForCurEvents()
        logger.debug("Done processing initial Workspace Events, now back to our program")

        return self.chan

    def waitForCurEvents(self):
        '''
        Since _eatServerEvents() runs in its own thread, we just wait for it's
        _processlock to be released, signaling that it's done processing that
        batch of VivEvents.  We don't need to do anything with the lock, so 
        we just release the lock and return
        '''
        logger.debug("waiting for current Workspace Event run to complete...")
        with self._processlock:
            pass

    def exportWorkspace(self):
        # Retrieve the big initial list of viv events
        return self.server.getNextEvents(self.chan)

    @e_threads.firethread
    def _monitorEventQueuePerf(self):
        self._starttime = time.time()
        while True:
            qlen = -1
            try:
                time.sleep(1)
                q = self.q

                if q:
                    qlen = q.qsize()
                    if qlen % 100 == 1:
                        logger.debug("qlen: %d (%d/%d)", qlen, self._qcount, self._qcountfull)

                curtime = time.time()
                delta = curtime - self._qtime
                if delta > 1 and self._qcount:
                    self._qtime = curtime

                    self._qrate = self._qcount / delta
                    logger.info("Event Queue Rate: %d/sec (%d / %d)", self._qrate, delta, (self._qtime-self._starttime))
                    logger.debug("      qlen: %d (%d/%d)", qlen, self._qcount, self._qcountfull)

                    # reset counter
                    self._qcount = 0
            except:
                logger.warning("Problem in Monitor Thread", exc_info=1)


    def waitForEvent(self, chan, timeout=None):
        q = self.q
        qitem = q.get(timeout=timeout)
        self._qcount += 1
        self._qcountfull += 1
        return qitem

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


class VivServer:

    def __init__(self, dirname='', **kwargs):
        self.path = os.path.abspath(dirname)

        cfgdir = kwargs.get('confdir', None)
        if cfgdir:
            self.vivhome = os.path.abspath(cfgdir)
        else:
            self.vivhome = e_config.gethomedir(".viv", makedir=True)
        cfgpath = os.path.join(self.vivhome, 'viv.json')
        self.config = e_config.EnviConfig(filename=cfgpath, defaults=defconfig, docs=docconfig, autosave=True)

        self.timeout_wait = self.config.viv.remote.timeout_wait
        self.timeout_aban = self.config.viv.remote.timeout_aban
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

        for chan in list(self.chandict.keys()):
            chaninfo = self.chandict.get(chan)
            # NOTE: double check because we're lock free...
            if chaninfo is None:
                continue

            wsinfo, queue, chanleaders = chaninfo
            if queue.abandoned(self.timeout_aban):
                self.cleanupChannel(chan)

    @e_threads.maintthread(30)
    def _saveWorkspaceThread(self):
        for wsinfo in self.wsdict.values():
            lock, path, events, users, leaders, leaderloc = wsinfo
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
        wsinfo = [threading.Lock(), wspath, [], {}, {}, {}]
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
                    wsinfo = [lock, wspath, [], {}, {}, {}]
                    logger.debug('loaded: %s', wsname)
                    self.wsdict[wsname] = wsinfo

    def getNextEvents(self, chan):
        chaninfo = self.chandict.get(chan)
        if chaninfo is None:
            raise Exception('Invalid Channel: %s' % chan)
        logger.debug("getNextEvents(%r)", repr(chaninfo))
        return chaninfo[1].get(timeout=self.timeout_wait)

    # All APIs from here down are basically mirrors of the workspace APIs
    # used with remote workspaces, with a prepended chan first argument

    def _fireEvent(self, chan, event, einfo, local=False, skip=None):
        #print("_fireEvent: %r %r %r %r %r" % (chan, event, einfo, local, skip))

        if chan in self.chandict:
            wsinfo, q, chanleaders = self.chandict.get(chan)
            lock, fpath, pevents, users, leaders, leaderloc = wsinfo
            oldclient = False

        elif chan in self.wsdict:
            # DEPRECATED: this is for backwards compat.  use only the chandict code one year from today, 5/10/2022.
            wsname = chan
            wsinfo = self._req_wsinfo(wsname)
            lock, fpath, pevents, users, _, _ = wsinfo
            # cheat for older clients... they don't get all the follow-the-leader goodness until they upgrade
            chanleaders = []
            leaders = {}
            leaderloc = {}
            oldclient = True

        else:
            raise Exception("BAD CHANNEL: _fireEvent: %r %r %r %r %r" % (chan, event, einfo, local, skip))

        evtup = (event, einfo)
        with lock:
            # Transient events do not get saved
            if not event & VTE_MASK:
                pevents.append(evtup)

            else:
                vtevent = event ^ VTE_MASK
                if vtevent == VTE_FOLLOWME:
                    pass

                elif vtevent == VTE_IAMLEADER:
                    logger.info("VTE_IAMLEADER: %r" % repr(evtup))
                    uuid, user, fname, locexpr = einfo
                    leaders[uuid] = (user, fname)
                    leaderloc[uuid] = locexpr
                    chanleaders.append(uuid)

                elif vtevent == VTE_FOLLOWME:
                    logger.info("VTE_FOLLOWME: %r" % repr(evtup))
                    uuid, expr = einfo
                    leaderloc[uuid] = expr

                elif vtevent == VTE_KILLLEADER:
                    logger.info("VTE_KILLLEADER: %r" % repr(evtup))
                    uuid = einfo
                    leaders.pop(uuid, None)
                    leaderloc.pop(uuid, None)

                elif vtevent == VTE_MODLEADER:
                    logger.info("VTE_MODLEADER: %r" % repr(evtup))
                    uuid, user, fname = einfo
                    leaders[uuid] = (user, fname)


            # SPEED HACK
            [q.append(evtup) for chan, q in users.items() if chan != skip]

    def createEventChannel(self, wsname):
        wsinfo = self._req_wsinfo(wsname)
        chan = e_common.hexify(os.urandom(16))
        chunksize = self.config.viv.server.queue_chunksize

        # Load up the queue with events from the file, and current events
        lock, fpath, pevents, users, leaders, leaderloc = wsinfo

        with lock:
            # These must reference the same actual list object...
            queue = VivChunkQueue(chunksize=chunksize)
            users[chan] = queue
            chanleaders = []
            self.chandict[chan] = [wsinfo, queue, chanleaders]

            # add events after the channel is created.  that way the client can start pulling event groups immediately
            fileevts = viv_basicfile.vivEventsFromFile(fpath)
            fileevts.extend(pevents)
            # use this firethread function to add events while we return the channel
            queue.chunkedAddLargeEventList(fileevts)

        return chan

    def getLeaderLocations(self, wsname):
        wsinfo = self._req_wsinfo(wsname)
        lock, path, events, users, leaders, leaderloc = wsinfo
        return dict(leaderloc)

    def getLeaderSessions(self, wsname):
        wsinfo = self._req_wsinfo(wsname)
        lock, path, events, users, leaders, leaderloc = wsinfo
        return dict(leaders)

    def cleanupChannel(self, chan):
        chantup = self.chandict.get(chan, None)
        if chantup is None:
            logger.warning("Attempting to clean up nonexistent channel: %r" % chan)
            return

        # Remove all channels originating from this channel
        wsinfo, queue, chanleaders = chantup
        for uuid in chanleaders:
            self._fireEvent(chan, VTE_KILLLEADER | VTE_MASK, uuid)

        # Remove from the workspace clients
        lock, fpath, pevents, users, leaders, leaderloc = wsinfo
        with lock:
            userinfo = users.pop(chan, None)

        # Remove from our chandict
        self.chandict.pop(chan, None)

# TODO: queue events to a list...  after a few ms (or CHUNKSIZE reached), convert to a Dict/List and send it?

class VivChunkQueue(e_threads.ChunkQueue):
    '''
    Vivisect Event specific version of the ChunkQueue
    This ChunkQueue implements ChunkQueue helpers specifically designed to
    handle VivServer requirements, namely:
    1) Chunking Around VWE_ADDMMAP events to reduce delays between request to
        response
    2) Front-loading chunking of the initial file VivServer download. Again,
        this helps avoid timeouts while processing large workspaces.  With
        the addition of multi-library VivWorkspaces, this can be a *real*
        problem.  VivChunkQueue helps solve those problems
    3) Introduction of the Event Group, enabling the functionality required
        to do #2 efficiently.  Front-loading pre-analyzed groups of events
        speeds up loading dramatically
    '''
    def _get_items(self):
        '''
        Already has self.lock when called.
        '''
        if not len(self.items):
            return []

        # watch for event groups
        # "event groups" are a dict with a list stored at key 0.  this list is
        # then able to be shoved over the Cobra channel immediately, front-loading
        # any preparation, and drastically speeding up initial message glut on
        # workspace loading.
        if type(self.items[0]) == dict:
            evtgroup = self.items.pop(0)
            evts = evtgroup[0]
            logger.debug("_get_items: STORED EVENT GROUP of size %d (queue remaining: %d)", len(evts), len(self.items))
            return evts

        # handle events in "chunks"
        if self.chunksize:
            logger.debug('_get_items(): chunksize: %d', self.chunksize)

            # search for ADDMMAPs so we don't group two in one transmission
            # RAM and CPU utilization make larger workspaces time out otherwise
            # especially if there are multiple large memory maps (eg. multi-lib
            # workspaces)
            idx = None
            for idx in range(self.chunksize-1):
                # break if we reach the end of the event list
                if idx >= len(self.items):
                    break

                evtitem = self.items[idx]

                # search for Event Groups
                if type(evtitem) == dict:
                    # don't include this in the list!  kick out and let the
                    # "event group" section (above) handle this one
                    idx -= 1
                    break

                evtype, evtdata = evtitem
                # search for ADDMMAP events
                if evtype == vivisect.VWE_ADDMMAP:
                    break


            # idx+1 to grabs the last item identified (except for Event Groups)
            ret = self.items[:idx+1]

            numEaten = len(ret)
            # just rebuild the list - tried several options, this still won out
            self.items = self.items[numEaten:]

            numLeft = len(self.items)
            logger.debug('_get_items() - returning (%d eaten / %d left)', numEaten, numLeft)

        else:
            # if chunksize is 0 or None, go old-school and just shove it all in
            ret = self.items
            for idx, (evtype, evtdata) in enumerate(ret):
                # still want to only send one memory map at a time
                if evtype == vivisect.VWE_ADDMMAP:
                    ret = self.items[:idx+1]
                    break

            self.items = self.items[len(ret):]
            logger.debug("_get_items() - returning %d items (%d remaining)", len(ret), len(self.items))
        return ret

    @e_threads.firethread
    def chunkedAddLargeEventList(self, evts):
        '''
        Break up a large list of events into appropriately pre-sized chunks,
        allowing for high efficiency in serving them.  This is a @firethread
        function, meaning that it runs in its own thread, making it "fire-and-
        forget".
        '''
        evtcount = len(evts)
        idx = 0
        logger.debug("... adding %d events to the Queue", evtcount)
        while evtcount > 0:
            anchor = idx
            for count in range(self.chunksize):
                # pick and poke...
                evt = evts[idx]
                idx += 1
                evtcount -= 1
                if evtcount <10:
                    logger.debug("...evtcount==%d, idx==%d", evtcount, idx)
                if evtcount == 0:
                    # we don't want to clip the last entry
                    idx += 1
                    break


                # if it's a memory map, only include one per chunk
                if evt[0] == vivisect.VWE_ADDMMAP:
                    logger.debug(" (chopping after VWE_ADDMMAP)")
                    break

            # here is the list of events we're packaging up
            worklist = evts[anchor:idx]

            # we package the list in a dict, to differentiate between normal events and event groups
            workdict = {0 : worklist}

            # add this group to the Queue
            logger.debug("... appending %d event chunk to the Queue (%d:%d)", len(worklist), anchor, idx)
            self.append(workdict)



def getServerWorkspace(server, wsname):
    vw = v_cli.VivCli()
    logger.debug("Starting:  VivServerClient(%r, %r)", server, wsname)
    cliproxy = VivServerClient(vw, server, wsname)
    logger.debug("Starting:  vw.initWorkspaceClient()")
    vw.initWorkspaceClient(cliproxy)
    logger.debug("Complete:  vw.initWorkspaceClient()")
    return vw


def connectToServer(hostname, port=viv_port):
    builder = cobra.initSocketBuilder(hostname, port)
    builder.setTimeout(timeout_sock)
    server = cobra.CobraProxy("cobra://%s:%d/VivServer" % (hostname, port), msgpack=True)
    version = server.getServerVersion()
    if version != server_version:
        raise Exception('Incompatible Server: his ver: %d our ver: %d' % (version, server_version))
    return server


def runMainServer(dirname='', port=viv_port):
    s = VivServer(dirname=dirname)
    daemon = cobra.CobraDaemon(port=port, msgpack=True)
    daemon.recvtimeout = timeout_sock
    daemon.shareObject(s, 'VivServer')
    daemon.serve_forever()


def setup():
    ap = argparse.ArgumentParser('Start a vivisect server to share workspaces')
    ap.add_argument('dirn', help='A directory full of *.viv files to share')
    ap.add_argument('--port', '-p', type=int, default=viv_port,
                    help='The port to start server on (defaults to %d)' % viv_port)
    return ap


def main():
    opts = setup().parse_args()
    vdir = os.path.abspath(opts.dirn)
    if not os.path.isdir(vdir):
        logger.error('%s is not a valid directory!', vdir)
        return -1

    print(f'VivServer starting (port: {opts.port})')
    runMainServer(vdir, opts.port)


if __name__ == '__main__':
    sys.exit(main())
