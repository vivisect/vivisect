import os
import unittest
import contextlib
import subprocess

import cobra
import cobra.dcode
import cobra.remoteapp


class Foo:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self):
        return self.x + self.y

    def mult(self):
        return self.x * self.y

    def pow(self):
        return self.x ** self.y


@contextlib.contextmanager
def getDcodeDmon():
    dmon = cobra.CobraDaemon(host='localhost', port=41923, msgpack=True)
    dmon.fireThread()
    cobra.dcode.enableDcodeServer(daemon=dmon)
    name = cobra.remoteapp.shareRemoteApp('cobra.testclient', appsrv=Foo(3, 4), daemon=dmon)
    yield (name, dmon)
    dmon.unshareObject(name)


def buildCobra(host, port, name):
    builder = cobra.initSocketBuilder(host, port)
    builder.setTimeout(5)
    return cobra.CobraProxy('cobra://%s:%s/%s?msgpack=1' % (host, port, name))


class CobraDcodeTest(unittest.TestCase):

    def test_cobra_dcode(self):
        with getDcodeDmon() as (name, dmon):
            # dmon.fireThread()
            srv = buildCobra(dmon.host, dmon.port, name)
            self.assertEqual(srv.add(), 7)
            self.assertEqual(srv.mult(), 12)
            self.assertEqual(srv.pow(), 81)


    def test_dcode_remotecode(self):
        '''
        This test can be confusing, because we're using Dcode to access the
        local machine, not a remote one.

        First, we setup a dcode server with a special base path of "cobra".
        This makes the contents of Vivisect's `cobra` directory accessible
        as a top-level.

        Next, we connect to the the Dcode server with the unittest process
        and import dcode from the "remote" cobra path offered by Dcode.
        
        Assertion is just a constant from the remote cobra module
        '''

        # setup server-side with special path: importing "cobra" as the base,
        # so anything in that directory becomes top-level, eg. cobra.dcode can
        # be imported as "import dcode")
        p = subprocess.Popen("python3 -m cobra.dcode -P 12347 cobra".split(' '),
                executable='python3', stdin=subprocess.PIPE)

        # setup client-side
        cobra.dcode.addDcodeServer('localhost', 12347)

        # this doesn't exist in the local PYTHONPATH, but should come from the Dcode server
        import dcode    # through Dcode, this is accessing cobra.dcode

        # now we'll test the constant COBRA_CALL (which we get through Dcode)
        self.assertEqual(dcode.cobra.COBRA_CALL, 1)

        # cleanup
        p.kill()

