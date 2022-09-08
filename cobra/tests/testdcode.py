import unittest
import contextlib

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
