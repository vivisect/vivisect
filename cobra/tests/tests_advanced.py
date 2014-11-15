import multiprocessing
import os
import shutil
import struct
import sys
import tempfile
import time
import types
import unittest
if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

import msgpack

import cobra
import cobra.dcode

class CobraMixinTests(unittest.TestCase):
    def test_sslmixin_req(self):
        with self.assertRaisesRegex(Exception, 'required args'):
            cobra.SslCobraMixin()

    def test_sslmixin_req1(self):
        with self.assertRaisesRegex(Exception, 'required args'):
            cobra.SslCobraMixin(sslcrt='foo')

    def test_sslmixin_pass(self):
        with tempfile.NamedTemporaryFile() as crtfile, tempfile.NamedTemporaryFile() as keyfile, tempfile.NamedTemporaryFile() as cafile:
            cobra.SslCobraMixin(sslcrt=crtfile.name, sslkey=keyfile.name, sslca=cafile.name)

    def ftest_ssl_msgpack_cobra(self):
        with tempfile.NamedTemporaryFile() as crtfile, tempfile.NamedTemporaryFile() as keyfile, tempfile.NamedTemporaryFile() as cafile:
            cobra.SslMsgpackWlCobraDaemon(sslcrt=crtfile.name, sslkey=keyfile.name, sslca=cafile.name)

class CobraSetupMixin(object):
    def __init__(self, dclass):
        self.dclass = dclass

    def setUp(self):
        cobra.startCobraServer(dclass=self.dclass)

        class Foo(object):
            def __init__(self):
                self.foo = 123

            def bar(self):
                self.baz = types.MethodType(Foo.faz, self)
                return 'foobar'

            @cobra.public
            def faz(self):
                return 'faz'

        cobra.daemon.shareObject(Foo(), name='Foo')

        self.cp = cobra.CobraProxy('cobra://{}:{}/{}?msgpack={}'.format('localhost', cobra.COBRA_PORT, 'Foo', 1))

    def tearDown(self):
        cobra.daemon.stopServer()
        cobra.daemon = None

class CobraWhitelistTests(CobraSetupMixin, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        CobraSetupMixin.__init__(self, cobra.MsgpackWlCobraDaemon)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_whitelisted_call(self):
        value = self.cp.faz()
        self.assertEqual(value, 'faz')

    def test_whitelist_fail_call(self):
        '''
        tests that we cant access methods added at a later time.
        '''
        # call cp.bar() directly, cobra wont do this properly since it thinks
        # it's an attribute due to not coming back in the HELLO.
        name = b'Foo'
        CALL = 1
        bytez = msgpack.dumps( ('bar', [], {}), use_bin_type=True )
        hdr = struct.pack('<III', CALL, len(name), len(bytez))

        with self.cp._cobra_getsock() as csock:
            sock = csock.socket
            sock.sendall(hdr + name + bytez)
            print(sock.recv(1024))

    def test_whitelist_fail_getattr(self):
        '''
        tests that we cant get attributes.
        '''
        # this will attempt to do a getattr on bar since it should *not* be
        # included as part of hello response due to whitelisting.
        # in this case, it's not serializable if allowed to go through anyway.
        with self.assertRaisesRegex(Exception, 'object has no attribute'):
            a = self.cp.bar()

        with self.assertRaisesRegex(Exception, 'object has no attribute'):
            a = self.cp.foo

    def test_whitelist_fail_setattr(self):
        '''
        tests that we cant set attributes.
        '''
        with self.assertRaisesRegex(Exception, 'object has no attribute'):
            self.cp.bar = 123

class CobraNoWhitelistTests(CobraSetupMixin, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        CobraSetupMixin.__init__(self, cobra.MsgpackCobraDaemon)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_call(self):
        # test public call
        self.cp.faz()

        # test 'non-public' call
        self.cp.bar()

    def test_getattr(self):
        self.assertEqual(self.cp.foo, 123)

    def test_setattr(self):
        self.cp.foobar = 123
        self.assertEqual(self.cp.foobar, 123)

class DcodeTests(unittest.TestCase):
    def test_enableServer_nodaemon(self):
        cobra.dcode.enableDcodeServer()

        self.assertIsNotNone(cobra.daemon.shared.get('DcodeServer'))

        cobra.daemon.stopServer()
        cobra.daemon = None

    def test_addDcode_dups(self):
        # cant call this due to using pickle by default since we cant pass
        # msgpack=True down through, so create daemon manually.
        #cobra.dcode.enableDcodeServer()
        daemon = cobra.startCobraServer(dclass=cobra.MsgpackCobraDaemon)
        cobra.dcode.enableDcodeServer(daemon=daemon)

        saved_mpath = list(sys.meta_path)
        for i in range(5):
            cobra.dcode.addDcodeServer('localhost', msgpack=True)

        self.assertEqual(len(saved_mpath), len(sys.meta_path) - 1)

        cobra.daemon.stopServer()
        cobra.daemon = None

    def test_dcode_test_builtin(self):
        daemon = cobra.startCobraServer(dclass=cobra.MsgpackCobraDaemon)
        cobra.dcode.enableDcodeServer(daemon=daemon)

        cobra.dcode.addDcodeServer('localhost', msgpack=True)

        # test known/builtin.  this should check to make sure we didnt request
        # this remote, and that no previous test loaded this already.
        import sqlite3

        daemon.stopServer()
        cobra.daemon = None

    def test_dcode_test_local(self):
        daemon = cobra.startCobraServer(dclass=cobra.MsgpackCobraDaemon)
        cobra.dcode.enableDcodeServer(daemon=daemon)

        cobra.dcode.addDcodeServer('localhost', msgpack=True)

        # test known/builtin.  this should check to make sure we didnt request
        # this remote, and that no previous test loaded this already.
        try:
            os.makedirs(r'foo\bar\baz')
            with open(r'foo\__init__.py', 'wb') as f:
                pass

            with open(r'foo\bar\__init__.py', 'wb') as f:
                pass

            with open(r'foo\bar\baz\__init__.py', 'wb') as f:
                pass

            with open(r'foo\bar\baz\faz.py', 'wb') as f:
                f.write(b'print(\'foo\')')

            import foo.bar.baz.faz
        finally:
            shutil.rmtree('foo')
            cobra.daemon.stopServer()
            cobra.daemon = None

    def test_dcode_test_remote_found(self):
        cobra.dcode.delAllDcodeServers()
        p = multiprocessing.Process(target=startCobraD)
        p.start()

        try:
            cobra.dcode.addDcodeServer('localhost', msgpack=True)
            import abcdefg

        finally:
            p.terminate()
            p.join()

    def test_dcode_test_remote_not_found(self):
        p = multiprocessing.Process(target=startCobraD)
        p.start()

        try:
            cobra.dcode.addDcodeServer('localhost', msgpack=True)

            with self.assertRaisesRegex(ImportError, 'No module named'):
                import abcdefgh

        finally:
            p.terminate()
            p.join()

def startCobraD():
    '''
    target for starting cobra daemon in seperate process.
    '''
    import cobra
    daemon = cobra.startCobraServer(dclass=cobra.MsgpackCobraDaemon)
    cobra.dcode.enableDcodeServer(daemon=daemon)

    with tempfile.NamedTemporaryFile(delete=False) as f:
        ddir = os.path.dirname(f.name)
        sys.path.append(ddir)
        with open(os.path.join(ddir, 'abcdefg.py'), 'wb') as f:
            f.write(b'print(\'foo\')')

            daemon.addDcodePath(ddir)

    while True:
        time.sleep(10)
