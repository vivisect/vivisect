import os
import time
import tempfile
import unittest
import threading

import vivisect
import vivisect.tests.helpers as helpers
import vivisect.remote.server as v_r_server


class VivisectRemoteTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.tmpf = tempfile.NamedTemporaryFile()
        self.testfile = helpers.getTestPath('windows', 'amd64', 'firefox.exe')

        # load the file in so we get some workspace events, but not so many to make
        # this test take forever
        self.vw = vivisect.VivWorkspace()
        self.vw.loadFromFile(self.testfile)
        self.vw.setMeta('StorageName', self.tmpf.name)
        self.vw.saveWorkspace()

    def __del__(self):
        self.tmpf.close()

    def test_basic(self):
        dirn = os.path.dirname(self.tmpf.name)
        host = '0.0.0.0'
        port = 0x4097
        thr = threading.Thread(target=v_r_server.runMainServer, args=(dirn, port))
        thr.daemon = True
        thr.start()

        server = v_r_server.connectToServer(host, port)
        wslist = server.listWorkspaces()
