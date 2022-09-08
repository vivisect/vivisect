import unittest

import cobra
import cobra.auth as c_auth
import cobra.auth.shadowfile as c_auth_shadow

import cobra.tests as c_tests

class CobraBasicTest(unittest.TestCase):

    #def setUp(self):
        #pass

    #def tearDown(self):
        #pass

    def test_cobra_proxy(self):

        testobj = c_tests.TestObject()

        daemon = cobra.CobraDaemon(port=60600)
        objname = daemon.shareObject( testobj )
        daemon.fireThread()

        t = cobra.CobraProxy('cobra://localhost:60600/%s' % objname)
        c_tests.accessTestObject( t )

        daemon.stopServer()

    def test_cobra_msgpack(self):

        try:
            import msgpack
        except ImportError:
            self.skipTest('No msgpack installed!')

        testobj = c_tests.TestObject()

        daemon = cobra.CobraDaemon(port=60610, msgpack=True)
        objname = daemon.shareObject( testobj )
        daemon.fireThread()

        t = cobra.CobraProxy('cobra://localhost:60610/%s?msgpack=1' % objname)
        c_tests.accessTestObject( t )
        daemon.stopServer()

    def test_cobra_authentication(self):

        testobj = c_tests.TestObject()

        daemon = cobra.CobraDaemon(port=60601)
        daemon.setAuthModule( c_auth.CobraAuthenticator() )
        daemon.fireThread()

        objname = daemon.shareObject( testobj )

        # Lets fail because of no-auth first
        try:
            p = cobra.CobraProxy('cobra://localhost:60601/%s' % objname)
            raise Exception('Allowed un-authd connection!')
        except cobra.CobraAuthException as e:
            pass

        # Now fail with wrong auth
        try:
            p = cobra.CobraProxy('cobra://localhost:60601/%s' % objname, authinfo={})
            raise Exception('Allowed bad-auth connection!')
        except cobra.CobraAuthException as e:
            pass

        # Now lets succeed
        authinfo = { 'user':'invisigoth', 'passwd':'secret' }
        t = cobra.CobraProxy('cobra://localhost:60601/%s' % objname, authinfo=authinfo)
        c_tests.accessTestObject( t )

        daemon.stopServer()

    def test_cobra_shadowauth(self):
        testobj = c_tests.TestObject()

        daemon = cobra.CobraDaemon(port=60602)
        shadowfile = c_tests.testFileName('shadowpass.txt')
        authmod = c_auth_shadow.ShadowFileAuth( shadowfile )
        daemon.setAuthModule( authmod )

        daemon.fireThread()

        objname = daemon.shareObject( testobj )

        # Now lets succeed
        authinfo = { 'user':'invisigoth', 'passwd':'secret' }
        t = cobra.CobraProxy('cobra://localhost:60602/%s' % objname, authinfo=authinfo)
        c_tests.accessTestObject(t)
        self.assertEqual( t.getUser(), 'invisigoth')
        daemon.stopServer()

    def test_cobra_refcount(self):

        testobj = c_tests.TestObject()

        daemon = cobra.CobraDaemon(port=60660)
        objname = daemon.shareObject( testobj, doref=True )
        daemon.fireThread()

        with cobra.CobraProxy('cobra://localhost:60660/%s' % objname) as t:
            c_tests.accessTestObject( t )

        self.assertIsNone( daemon.getSharedObject( objname ) )
        daemon.stopServer()

    #def test_cobra_ssl(self):
    #def test_cobra_ssl_clientcert(self):

if __name__ == '__main__':
    unittest.main()

