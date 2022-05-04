import os
import sys
import time
import tempfile
import unittest
import threading
import multiprocessing as mp

import vivisect
import vivisect.const as v_const
import vivisect.tests.helpers as helpers
import vivisect.remote.server as v_r_server


def runServer(name, port):
    dirn = os.path.dirname(name)
    testfile = helpers.getTestPath('windows', 'amd64', 'firefox.exe')

    # load the file in so we get some workspace events, but not so many to make
    # this test take forever
    vw = vivisect.VivWorkspace()
    vw.loadFromFile(testfile)
    vw.setMeta('StorageName', name)
    vw.saveWorkspace()

    v_r_server.runMainServer(dirn, port)


class VivisectRemoteTests(unittest.TestCase):
    '''
    So...what would be fun is basically a chain of remote workspaces all tied in interesting
    configurations.
    '''
    def test_basic(self):
        testfile = helpers.getTestPath('windows', 'amd64', 'firefox.exe')
        good = vivisect.VivWorkspace()
        good.loadFromFile(testfile)

        host = 'localhost'
        port = 0x4097
        with tempfile.TemporaryDirectory() as tmpd:
            tmpf = tempfile.NamedTemporaryFile(dir=tmpd, delete=False)
            try:
                proc = mp.Process(target=runServer, args=(tmpf.name, port,))
                proc.daemon = True
                proc.start()

                # give the other process time to spin up
                time.sleep(0.5)

                # So...yea. The server could not be up yet, but I'm not waiting a million years to
                # wait for it.
                retry = 0
                conn = False
                while retry < 5:
                    try:
                        server = v_r_server.connectToServer(host, port)
                        conn = True
                        break
                    except:
                        retry += 1
                        time.sleep(0.2)

                if not conn:
                    self.fail('Could not connect to %s:%s' % (host, port))

                wslist = server.listWorkspaces()
                self.assertEqual(len(wslist), 1)
                self.assertEqual(server.getServerVersion(), 20130820)

                rmtvw = v_r_server.getServerWorkspace(server, wslist[0])
                rmtvw2 = v_r_server.getServerWorkspace(server, wslist[0])
                # So the consumption of events from the server is *also* threaded, so I've got to do some blocking
                # to get us to wait on things
                retry = 0
                while retry < 5:
                    locs = rmtvw2.getLocations()
                    if len(locs) > 1388:
                        break

                    retry += 1
                    time.sleep(0.3)
                    sys.stderr.write('%d' % retry)

                self.assertEqual(len(rmtvw2.getLocations()), 1389)
                self.assertEqual(set(rmtvw2.getLocations()), set(good.getLocations()))
                self.assertEqual(set(rmtvw2.getXrefs()), set(good.getXrefs()))

                # test some of the follow-the-leader framework
                testuuid = 'uuid_of_my_dearest_friend_1'
                # first just create a leader session:
                rmtvw.iAmLeader(testuuid, "atlas' moving castle")

                retry = 0
                while retry < 5:
                    # only one session, so we'll run this once - local
                    ldrsess = rmtvw2.getLeaderSessions().get(testuuid)
                    if ldrsess is not None:
                        break

                    retry += 1
                    time.sleep(.1)
                    sys.stderr.write('%d' % retry)

                (user, fname) = ldrsess
                self.assertEqual(fname, "atlas' moving castle")

                # now let's move around a bit
                rmtvw.followTheLeader(testuuid, '0x31337')
                retry = 0
                while retry < 5:
                    # only one session, so we'll run this once - local
                    ldrloc = rmtvw2.getLeaderLoc(testuuid)
                    if ldrloc is not None:
                        break

                    retry += 1
                    time.sleep(.1)
                    sys.stderr.write('%d' % retry)

                self.assertEqual(ldrloc, '0x31337')

                # now let's rename things
                rmtvw.modifyLeaderSession(testuuid, 'rakuy0', "rakuy0's moving castle")
                retry = 0
                while retry < 5:
                    # only one session, so we'll run this once - local
                    ldrsess = list(rmtvw2.getLeaderSessions().items())[0]
                    uuid, (user, fname) = ldrsess
                    if user == 'rakuy0':
                        break

                    retry += 1
                    time.sleep(.1)
                    sys.stderr.write('%d' % retry)

                self.assertEqual(uuid, testuuid)
                self.assertEqual(user, 'rakuy0')
                self.assertEqual(fname, "rakuy0's moving castle")

                self.assertEqual(rmtvw2.getLeaderInfo(testuuid), ('rakuy0', "rakuy0's moving castle"))


                try:
                    rmtvw.server = None
                    rmtvw2.server = None

                    q = rmtvw.chan_lookup.get(rmtvw.rchan)
                    if q:
                        # So it's not reeeealy auto analysis fini, but it's a good enough stand-in to get
                        # the server thread to shutdown cleaner
                        q.puts((v_const.VWE_AUTOANALFIN, None))

                    proc.terminate()
                    proc.close()
                except:
                    pass
            finally:
                tmpf.close()
                os.unlink(tmpf.name)
