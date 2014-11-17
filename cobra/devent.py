'''
Cobra Distributed Event subsystem.
'''
import json
import time
import Queue
import socket
import struct
import itertools
import threading
import collections

import envi.threads as e_threads

class CobraEventCore:

    def __init__(self):
        self._ce_chanids = itertools.count()
        self._ce_fireq = e_threads.ChunkQueue()

        self._ce_chans = []
        self._ce_handlers = collections.defaultdict(list)
        self._ce_upstreams = []
        self._ce_mcastport = None
        self._ce_mcasthost = None
        self._ce_ecastsock = None
        self._ce_chanlookup = {}

        self._ce_firethr = self._fireFireThread()

    def finiEventCore(self):
        self._ce_fireq.shutdown()
        self._ce_firethr.join()

    @e_threads.firethread
    def _fireFireThread(self):
        for args,kwargs in self._ce_fireq:
            try:
                self._fireEvent(*args, **kwargs)
            except Exception, e:
                print('fireFireThread _fireEventError: %s' % e)

    @e_threads.maintthread(3)
    def cullAbandonedChannels(self, abtime):
        [ self.finiEventChannel(q.chanid) for q in self._ce_chans if q.abandoned(abtime) ]

    def initEventChannel(self, qmax=0):
        '''
        Create a new channel id and allocate an
        event Queue.
        '''
        chanid = self._ce_chanids.next()
        q = e_threads.ChunkQueue()
        q.chanid = chanid # monkey patch the chanid to the q
        self._ce_chans.append( q )
        self._ce_chanlookup[ chanid ] = q
        return chanid

    def finiEventChannel(self, chanid):
        '''
        Close the specified event channel by adding a
        (None,None) event and removing the channel's
        Queue object.
        '''
        q = self._ce_chanlookup.pop( chanid )
        q.put((None,None))
        self._ce_chans.remove( q )

    def finiEventChannels(self):
        '''
        Close down all event channels by adding a (None,None)
        event and removing the event Q from the datastructs.
        '''
        for upstream,upchan in self._ce_upstreams:
            try:
                upstream.finiEventChannel(upchan)
            except Exception, e:
                print('upstream error: %r %s' % (upstream,e))
        [ self.finiEventChannel( chanid ) for chanid in self._ce_chanlookup.keys() ]

    def getNextEventsForChan(self, chanid, timeout=None):
        '''
        Get the next event for a previously initialized
        event channel.  If "timeout" is specified, the
        call will return None after the timeout interval.
        Each returned event is a tuple of ( eventname, eventinfo ).

        When the channel returns (None, None) it has closed.
        '''
        q = self._ce_chanlookup.get( chanid )
        if q == None:
            return None
        return q.get(timeout=timeout)

    def fireEvent(self, *args, **kwargs):
        '''
        Fire an event into the event distribution system.
        ( see _fireEvent for arg defs, we proxy all fire events through 1 thread )

        NOTE: an event coming down from an upstream will *not*
              be propigated upward to *any* upstreams.
        '''
        self._ce_fireq.put( (args,kwargs) )

    def _fireEvent(self, event, einfo, upstream=True, skip=None, chans=None):
        etup = (event,einfo)
        # Speed hack
        if chans != None:
            [ q.put( etup ) for q in self._ce_chans if q.chanid in chans ]
        else:
            [ q.put( etup ) for q in self._ce_chans if q.chanid != skip ]

        if self._ce_ecastsock:
            self._ce_ecastsock.sendto( json.dumps( etup ), (self._ce_mcasthost, self._ce_mcastport))

        for handler in self._ce_handlers[event]:
            try:
                handler(event,einfo)
            except Exception, e:
                print('handler error(%r): %s' % (event,e))

        if upstream:
            for upstream,upchan in self._ce_upstreams:
                try:
                    upstream.fireEvent(event, einfo, skip=upchan)
                except Exception, e:
                    print('upstream error: %r %s' % (upstream,e))

    def addEventHandler(self, event, callback):
        '''
        Add a local handler which will be called on fireEvent() for
        the specified event type.  The callback uses the following
        convention:
            callback(event, einfo)
        '''
        self._ce_handlers[event].append(callback)

    def delEventHandler(self, event, callback):
        '''
        Remove a previously added event handler for the given event
        type.
        '''
        self._ce_handlers[event].remove(callback)

    @e_threads.firethread
    def addEventUpstream(self, evtcore, qmax=0, timeout=5):
        '''
        Add another eventcore obejct as an "upstream" eventer to this
        one.  We will propigate local events upward to him, as well as
        recieve all his events ( minus our own ).
        '''
        chan = evtcore.initEventChannel(qmax=qmax)
        corechan = [evtcore, chan]
        self._ce_upstreams.append( corechan )
        while True:
            try:
                events = evtcore.getNextEventsForChan( chan, timeout=5 )
            except Exception, e:
                print('addEventUpstream Error: %s' % e)
                time.sleep(1)
                # grab a new channel...
                chan = evtcore.initEventChannel(qmax=qmax)
                corechan[1] = chan
                continue
            # channel closed..
            if events == None:
                return


            try:
                [ self.fireEvent(event,einfo,upstream=False) for (event,einfo) in events ]
            except Exception, e:
                print('addEventUpstream fireEvent Error: %s' % e)
                time.sleep(1)

    def addEventCallback(self, callback, qmax=0, firethread=True):
        '''
        Create a new event channel and fire a thread which
        listens for events and hands them off to the function
        "callback"

        def mycallback(event, einfo):
            dostuff()

        evt = CobraEventCore()
        evt.addEventCallback( mycallback )

        NOTE: This API is *not* cobra proxy call safe.
        '''
        if firethread:
            thr = threading.Thread(target=self.addEventCallback, args=(callback, qmax, False))
            thr.setDaemon(True)
            thr.start()
            return

        chanid = self.initEventChannel(qmax=qmax)
        q = self._ce_chanlookup.get( chanid )
        while True:

            for event,einfo in q.get(timeout=5):

                if event == None:
                    break

                try:
                    callback(event,einfo)
                except Exception, e:
                    print('Event Callback Exception (chan: %d): %s' % (chanid,e))

    def setEventCast(self, mcast='224.56.56.56', port=45654, bind='0.0.0.0'):
        '''
        Tie this CobraEventCore to any others which share the same multicast
        ip and port.  This basically creates a ( udp "unreliable" ) "bus" on
        which events are serialized using json.
        '''
        # Setup a UDP casting socket
        self._ce_mcastport = port
        self._ce_mcasthost = mcast
        self._ce_ecastsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ce_ecastsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._ce_ecastsock.bind((bind,port))

        # Join the multicast IP
        mreq = struct.pack("4sL", socket.inet_aton(mcast), socket.INADDR_ANY)
        self._ce_ecastsock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        thr = threading.Thread(target=self._runSocketListener)
        thr.setDaemon(True)
        thr.start()

    def _runSocketListener(self):
        sock = self._ce_ecastsock
        while True:
            sockdata,sockaddr = sock.recvfrom(4096)
            etup = json.loads(sockdata)
            [ q.put( etup ) for q in self._ce_chans ]

if __name__ == '__main__':

    ecore0 = CobraEventCore()

    ecore1 = CobraEventCore()
    ecore1.addEventUpstream(ecore0)

    #ecore.setEventCast(bind='192.168.1.2')
    #ecore.setEventCast(bind='192.168.1.117')

    def wootback(event,einfo):
        print 'wootback',event,einfo

    #ecore0.addEventHandler('foo', wootback)
    #ecore1.addEventHandler('foo', wootback)

    chan0 = ecore0.initEventChannel()
    chan1 = ecore1.initEventChannel()
    print('Channel: %d' % chan1)

    # both channels should get exactly one copy of these
    ecore0.fireEvent('foo',('some','foo','info'))
    ecore1.fireEvent('bar',('some','bar','info'))

    import time; time.sleep(1)
    while True:
        print 'GOT0',ecore0.getNextEventsForChan( chan0, timeout=2 )
        print 'GOT1',ecore1.getNextEventsForChan( chan1, timeout=2 )

