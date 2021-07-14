import os
import hashlib
import tempfile
import unittest

import vivisect
from vivisect.const import *


def add_events(vw):
    # Call some APIs to populate the event list.
    # Coherency is not the objective. Just get some events in there.
    filehash = hashlib.md5(b'testfile').hexdigest()
    vw.addFile('testfile', 0x1000, filehash)
    vw.setMeta('Architecture', 'i386')
    vw.setMeta('Format', 'pe')
    vw.addMemoryMap(0x1000, 7, 'testfile', b'\x00' * 0x9000)
    vw.addLocation(0x2000, 4, 4, tinfo='fakeptr')
    vw.addLocation(0x3000, 16, 6, tinfo='oogieboogie')
    vw.addLocation(0x4000, 3, 5)
    vw.addLocation(0x5000, 3, 5)
    vw.addLocation(0x6000, 3, 5)
    vw.delLocation(0x4000)
    vw.addXref(0x4000, 0x3000, 1)
    vw.addXref(0x5000, 0x3000, 1)
    vw.delXref((0x5000, 0x3000, 1, 0))
    vw.setMeta('foo', 'bar')
    vw.setFileMeta('testfile', 'neato', 'burrito')
    vw.addVaSet('EmptySet', (('va', VASET_ADDRESS),))
    vw.delVaSet('FuncWrappers')
    vw.setComment(0x2000, 'test comment')
    vw.addExport(0x7000, EXP_FUNCTION, 'kernel32.YoThisExportFake', 'testfile')


class StorageTests(unittest.TestCase):

    def setUp(self):
        '''
        So on windows, you can't double open a temporary file (results in a fun "Permission Denied"
        exception). So instead, we setup a temporary file here and delete it in tearDown so that
        we don't maintain an open file descriptor to the temporary file
        '''
        self.tmpf = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        self.tmpf.close()
        os.unlink(self.tmpf.name)

    def test_msgpack_idempotent(self):
        # test that what we put in, we can get out
        vw = vivisect.VivWorkspace()
        vw.setMeta('StorageName', self.tmpf.name)
        vw.setMeta('StorageModule', 'vivisect.storage.mpfile')
        add_events(vw)
        vw.saveWorkspace()
        self.tmpf.flush()

        ovw = vivisect.VivWorkspace()
        ovw.setMeta('StorageModule', 'vivisect.storage.mpfile')
        # So this is a bit naughty, but just the act of creating a workspace
        # induces some events in to the workspace. Nothing crazy, just some va sets
        # so delete those so we can have a clean comparison
        ovw._event_list = []
        ovw.loadWorkspace(self.tmpf.name)

        old = list(vw.exportWorkspace())
        new = list(ovw.exportWorkspace())
        self.assertEqual(len(old), 35)
        self.assertEqual(len(new), 36)  # the last event is a setMeta made by loadWorkspace
        self.assertEqual(new[-1], (VWE_SETMETA, ('StorageName', self.tmpf.name)))
        for idx in range(len(old)):
            self.assertEqual(old[idx], new[idx])

    def test_msgpack_to_basicfile(self):
        # make sure we're on par with what the OG storage mechanism can do
        mpfile = tempfile.NamedTemporaryFile(delete=False)
        basicfile = tempfile.NamedTemporaryFile(delete=False)

        try:
            ogvw = vivisect.VivWorkspace()
            add_events(ogvw)
            ogvw.setMeta('StorageName', mpfile.name)
            ogvw.setMeta('StorageModule', 'vivisect.storage.mpfile')
            ogvw.saveWorkspace()
            # Get rid of those last two meta sets so that the two new workspaces should be
            # the same save for the last meta set
            ogvw._event_list.pop()
            ogvw._event_list.pop()
            ogvw.setMeta('StorageName', basicfile.name)
            ogvw.setMeta('StorageModule', 'vivisect.storage.basicfile')
            ogvw.saveWorkspace()
            ogevt = list(ogvw.exportWorkspace())

            mvw = vivisect.VivWorkspace()
            mvw.setMeta('StorageModule', 'vivisect.storage.mpfile')
            mvw._event_list = []
            mvw.loadWorkspace(mpfile.name)
            mevt = list(mvw.exportWorkspace())
            self.assertEqual(len(mevt), 36)

            bvw = vivisect.VivWorkspace()
            bvw.setMeta('StorageModule', 'vivisect.storage.basicfile')
            bvw._event_list = []
            bvw.loadWorkspace(basicfile.name)
            bevt = list(bvw.exportWorkspace())
            self.assertEqual(len(bevt), 36)

            # the last three events are specific to the different storage modules
            for idx in range(len(mevt) - 3):
                self.assertEqual(mevt[idx], bevt[idx])
                self.assertEqual(ogevt[idx], bevt[idx])
        finally:
            mpfile.close()
            basicfile.close()
            os.unlink(mpfile.name)
            os.unlink(basicfile.name)
