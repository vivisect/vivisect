import time
import socket
import unittest
import threading

import synapse.server as s_server
import synapse.lib.socket as s_socket
import synapse.event.dist as s_evtdist

class SocketTest(unittest.TestCase):

    def test_socket_basic(self):
        s1,s2 = s_socket.socketpair()

        sock1 = s_socket.Socket(s1)
        sock2 = s_socket.Socket(s2)

        testdata = {}
        def onsent(event):
            testdata['datasent'] = True

        def onrecvd(event):
            testdata['datarecvd'] = True

        sock1.on('sock:tx',onsent)
        sock1.on('sock:rx',onrecvd)

        sock1.sendall(b'asdf')
        self.assertEqual( sock2.recvall(4), b'asdf')

        sock2.sendall(b'qwer')
        self.assertEqual( sock1.recvall(4), b'qwer')

        self.assertTrue(testdata.get('datasent'))
        self.assertTrue(testdata.get('datarecvd'))

        sock1.close()
        sock2.close()

    def test_socket_server_pool(self):
        srv = s_server.SynServer(('127.0.0.1',0), pool=10)
        self._runServUnit(srv)

    def test_socket_server_threads(self):
        srv = s_server.SynServer(('127.0.0.1',0))
        self._runServUnit(srv)

    def _runServUnit(self, srv):
        evtshut = threading.Event()
        evtsrvshut = threading.Event()
        testdata = {}

        def onwoot(sock,msg):
            testdata['msg'] = msg[0]
            sock.firemsg('qwer')

        def onshut(event):
            testdata['shut'] = True
            evtshut.set()

        def srvshut(event):
            testdata['srvshut'] = True
            evtsrvshut.set()

        def onconn(event):
            testdata['conn'] = True

        srv.synServOn('sock:shut',onshut)
        srv.synServOn('serv:shut',srvshut)
        srv.synServOn('sock:conn',onconn)
        srv.synServMeth('woot', onwoot)

        sockaddr = srv.synRunServer()

        sock = s_socket.Socket()
        sock.connect(sockaddr)
        sock.firemsg('woot')

        qwer = sock.recvmsg()[0]

        sock.close()

        if not evtshut.wait(1):
            raise Exception('evtshut timeout!')

        self.assertEqual(qwer,'qwer')

        srv.synFiniServer()

        if not evtsrvshut.wait(1):
            raise Exception('evtsrvshut timeout!')

        self.assertEqual(testdata.get('msg'),'woot')
        self.assertTrue(testdata.get('shut'))
        self.assertTrue(testdata.get('conn'))
        self.assertTrue(testdata.get('srvshut'))

    def test_socket_plex(self):

        e = threading.Event()
        def sockmsg(event):
            e.set()

        def sockshut(event):
            e.set()

        plex = s_socket.Plex()
        plex.on('sock:msg', sockmsg)
        plex.on('sock:shut', sockshut)

        s1,s2 = s_socket.socketpair()

        plex.wrap(s2)

        #plex.addPlexSock(s2)

        sock = s_socket.Socket(s1)

        sock.sendmsg( 'foo' )
        if not e.wait(1):
            raise Exception('timeout on sock:msg')

        e.clear()

        sock.teardown()
        if not e.wait(1):
            raise Exception('timeout on sock:shut')

        plex.fini()

    def test_socket_plex_listen(self):

        e = threading.Event()
        def onconn(event):
            e.set()

        def onmsg(event):
            e.set()

        def onshut(event):
            e.set()

        plex = s_socket.Plex()
        plex.on('sock:conn', onconn)
        plex.on('sock:msg', onmsg)
        plex.on('sock:shut', onshut)

        host,port = plex.listen()

        sock = s_socket.connect('127.0.0.1',port)

        if not e.wait(1):
            raise Exception('waiting sock:conn')

        e.clear()

        sock.sendmsg('woot')
        if not e.wait(1):
            raise Exception('waiting sock:msg')

        e.clear()

        sock.teardown()
        if not e.wait(1):
            raise Exception('waiting sock:shut')

        plex.fini()
