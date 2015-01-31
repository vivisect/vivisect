import time
import socket
import unittest
import threading

import synapse.lib.socket as s_socket

class SocketTest(unittest.TestCase):

    def test_socket_basic(self):
        s1,s2 = socket.socketpair()

        sock1 = s_socket.Socket(s1)
        sock2 = s_socket.Socket(s2)

        testdata = {}
        def onsent(evt,evtinfo):
            testdata['datasent'] = True

        def onrecvd(evt,evtinfo):
            testdata['datarecvd'] = True

        sock1.synAddHandler('datasent',onsent)
        sock1.synAddHandler('datarecvd',onrecvd)

        sock1.sendall(b'asdf')
        self.assertEqual( sock2.recvall(4), b'asdf')

        sock2.sendall(b'qwer')
        self.assertEqual( sock1.recvall(4), b'qwer')

        self.assertTrue(testdata.get('datasent'))
        self.assertTrue(testdata.get('datarecvd'))

        sock1.close()
        sock2.close()

    def test_socket_server(self):

        evtshut = threading.Event()
        evtsrvshut = threading.Event()
        testdata = {}
        def onmsg(evt,evtinfo):
            testdata['msg'] = evtinfo.get('msg')
            evtinfo['sock'].sendall(b'qwer')

        def onshut(evt,evtinfo):
            testdata['shut'] = True
            evtshut.set()

        def srvshut(evt,evtinfo):
            testdata['srvshut'] = True
            evtsrvshut.set()

        srv = s_socket.Server(('127.0.0.1',0))
        srv.synAddHandler('sockmsg',onmsg)
        srv.synAddHandler('sockshut',onshut)
        srv.synAddHandler('shutdown',srvshut)

        sockaddr = srv.synRunServer()

        sock = s_socket.Socket()
        sock.connect(sockaddr)
        sock.emit('woot')

        qwer = sock.recvall(4)

        sock.close()

        if not evtshut.wait(1):
            raise Exception('evtshut timeout!')

        self.assertEqual(qwer,b'qwer')

        srv.synShutDown()

        if not evtsrvshut.wait(1):
            raise Exception('evtsrvshut timeout!')

        self.assertEqual(testdata.get('msg'),'woot')
        self.assertTrue(testdata.get('shut'))
        self.assertTrue(testdata.get('srvshut'))

