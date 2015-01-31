import io
import time
import socket
import unittest
import threading

import synapse.event.dist as s_eventdist
import synapse.event.store as s_eventstore

class EventStoreTest(unittest.TestCase):

    def _run_store(self, evtstore):
        d1 = s_eventdist.EventDist()
        evtstore.synLoadAndStore(d1)

        d1.synFireEvent('woot',{'woot':'woot','bytes':b'woot'})
        d1.synShutDown()

        testdata = {}
        def onwoot(evt,evtinfo):
            testdata.update(evtinfo)

        d2 = s_eventdist.EventDist()
        d2.synAddHandler('woot',onwoot)

        evtstore.synLoadAndStore(d2)
        self.assertEqual(testdata.get('woot'),'woot')
        self.assertEqual(testdata.get('bytes'),b'woot')

    def test_event_store_mem(self):
        s = s_eventstore.EventMemStore()
        self._run_store(s)

    def test_event_store_fd(self):
        fd = io.BytesIO()
        s = s_eventstore.EventFdStore(fd)
        self._run_store(s)

    def test_event_store_sock(self):
        s1,s2 = socket.socketpair()

        d1 = s_eventdist.EventDist()
        d2 = s_eventdist.EventDist()

        evtwoot = threading.Event()
        testdata = {}
        def onwoot(evt,evtinfo):
            testdata['woot'] = True
            evtwoot.set()

        d2.synAddHandler('woot',onwoot)

        stor1 = s_eventstore.EventSockStore(s1)
        stor2 = s_eventstore.EventSockStore(s2)

        th1 = stor1.synLoadEvents(d1,fire=True)
        th2 = stor2.synLoadEvents(d2,fire=True)

        stor1.synStoreEvents(d1)
        stor2.synStoreEvents(d2)

        d1.synFireEvent('woot',{'woot':'woot'})

        if not evtwoot.wait(1):
            raise Exception('evtwoot timeout!')

        d1.synShutDown()
