import io
import time
import socket
import unittest
import threading

import synapse.lib.socket as s_socket
import synapse.event.dist as s_eventdist
import synapse.event.store as s_eventstore

class EventStoreTest(unittest.TestCase):

    def _run_store(self, evtstore):
        d1 = s_eventdist.EventDist()
        evtstore.synLoadAndStore(d1)

        d1.fire('woot', woot='woot', buf=b'woot')
        d1.fini()

        testdata = {}
        def onwoot(event):
            testdata.update(event[1])

        d2 = s_eventdist.EventDist()
        d2.on('woot',onwoot)

        evtstore.synLoadAndStore(d2)
        self.assertEqual(testdata.get('woot'),'woot')
        self.assertEqual(testdata.get('buf'),b'woot')

    def test_event_store_mem(self):
        s = s_eventstore.EventMemStore()
        self._run_store(s)

    def test_event_store_fd(self):
        fd = io.BytesIO()
        s = s_eventstore.EventFdStore(fd)
        self._run_store(s)

    def test_event_store_sock(self):
        s1,s2 = s_socket.socketpair()

        d1 = s_eventdist.EventDist()
        d2 = s_eventdist.EventDist()

        evtwoot = threading.Event()
        testdata = {}
        def onwoot(event):
            testdata['woot'] = True
            evtwoot.set()

        d2.on('woot',onwoot)

        stor1 = s_eventstore.EventSockStore(s1)
        stor2 = s_eventstore.EventSockStore(s2)

        th1 = stor1.synLoadEvents(d1,fire=True)
        th2 = stor2.synLoadEvents(d2,fire=True)

        stor1.synStoreEvents(d1)
        stor2.synStoreEvents(d2)

        d1.fire('woot', woot='woot')

        if not evtwoot.wait(1):
            raise Exception('evtwoot timeout!')

        d1.fini()
