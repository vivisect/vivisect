import unittest

import synapse.server as s_server
import synapse.client as s_client
import synapse.lib.socket as s_socket

class SynTest(unittest.TestCase):

    def getCliSrv(self):
        srv = s_server.SynServer(('127.0.0.1',0))
        sockaddr = srv.synRunServer()
        cli = s_client.SynClient(sockaddr)
        return cli,srv

    def test_synapse_basics(self):
        cli,srv = self.getCliSrv()
        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('time') )

        cli.synFini()
        srv.synFiniServer()

    def test_synapse_reconnect(self):
        cli,srv = self.getCliSrv()

        data = {'conn':0}
        def onconn(event):
            data['conn'] += 1

        srv.synServOn('sock:conn', onconn)

        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('time') )

        # reach in and squish the socket
        cli._syn_sock.close()

        # ping again...
        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('time') )

        self.assertEqual( data.get('conn'), 2 )

        cli.synFini()
        srv.synFiniServer()

        self.assertRaises( s_socket.SocketClosed, cli._synFireTrans, 'syn:ping' )

    def test_synapse_sockper(self):
        cli,srv = self.getCliSrv()
        cli.synSetInfo('sockper', True)

        data = {'conn':0}
        def onconn(event):
            data['conn'] += 1

        srv.synServOn('sock:conn', onconn)

        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('rtt') )

        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('rtt') )

        msg = cli.synPingServ()
        self.assertIsNotNone( msg[1].get('rtt') )

        self.assertEqual( data.get('conn'), 3 )

        cli.synFini()
        srv.synFiniServer()

    def test_synapse_proxy(self):

        srv = s_server.SynServer(('127.0.0.1',0))
        sockaddr = srv.synRunServer()

        data = {}
        class Foo():

            def foobar(self, x):
                data['foo'] = x
                return 30

            def bazfaz(self):
                noway + nohow

        foo = Foo()
        srv.synShareObj(foo,'foo')

        proxy = s_client.SynProxy( sockaddr, 'foo' )

        self.assertEqual( proxy.foobar('gronk'), 30 )
        self.assertEqual( data.get('foo'), 'gronk' )

        self.assertRaisesRegex( s_client.SynRemoteException, 'noway', proxy.bazfaz )
