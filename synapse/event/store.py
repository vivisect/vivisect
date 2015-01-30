'''
Classes which implement synapse event storage.
'''
import msgpack
import threading

import synapse.lib.common as s_common
import synapse.lib.socket as s_socket
import synapse.lib.threads as s_threads

class EventStore:

    def __init__(self):
        self.thr = None

    def __iter__(self):
        pass

    def append(self, evt, evtinfo):
        pass

    def synShutDown(self):
        pass

    def synLoadAndStore(self, evtdist, fire=False):
        '''
        Fire all events from this storage into evtdist and
        begin saving subsequent events *to* this storage.
        '''
        if fire:
            self.thr = s_threads.fireWorkThread(self.synLoadAndStore,evtdist,fire=False)
            return

        [ evtdist.synFireEvent(evt,evtinfo) for evt,evtinfo in self ]
        evtdist.synAddHandler('*',self.append)

    def synLoadEvents(self, evtdist, fire=False):
        '''
        Load events from this EventStore into the given EventDist.
        '''
        if fire:
            return s_threads.fireWorkThread(self.synLoadEvents,evtdist,fire=False)
        [ evtdist.synFireEvent(evt,evtinfo) for evt,evtinfo in self ]

    def synStoreEvents(self, evtdist):
        '''
        Register this EventStore to recieve and archive events from evtdist.
        '''
        evtdist.synAddHandler('*',self.append)

class EventFdStore(EventStore):
    '''
    An EventStore backed by a file like object.
    '''
    def __init__(self, fd):
        EventStore.__init__(self)

        self.fd = fd
        self.lock = threading.Lock()

    def __iter__(self):
        with self.lock:
            s = self.fd.tell()
            self.fd.seek(0)
            for e in msgpack.Unpacker(self.fd,use_list=False,encoding='utf8'):
                yield e
            self.fd.seek(s)

    def append(self, evt, evtinfo):
        with self.lock:
            b = msgpack.packb( (evt,evtinfo), use_bin_type=True)
            self.fd.write(b)

class EventMemStore(EventStore):
    '''
    An EventStore backed by an in-memory list.
    '''
    def __init__(self):
        EventStore.__init__(self)
        self.events = []

    def append(self, evt, evtinfo):
        self.events.append( (evt,evtinfo) )

    def __iter__(self):
        for e in self.events:
            yield e

class EventSockStore(EventStore):
    '''
    An EventStore backed by a socket stream
    '''
    def __init__(self, sock):
        EventStore.__init__(self)
        self.sock = sock

    def __iter__(self):
        unpack = msgpack.Unpacker(use_list=False,encoding='utf8')
        while True:
            buf = self.sock.recv(102400)
            if not buf:
                return

            unpack.feed(buf)
            for e in unpack:
                yield e

    def append(self, evt, evtinfo):
        if evt == '$':
            self.sock.teardown()
            return
        self.sock.sendall( msgpack.packb((evt,evtinfo), use_bin_type=True) )

