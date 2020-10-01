import hashlib
import tempfile
import unittest

import vivisect
from vivisect.const import *


# Because u'foo' != 'foo' in python 2 and msgpack always unpacks to unicode :(
def normUnicode(event):
    prop = event[1]
    if isinstance(prop, unicode):
        prop = str(prop)
    elif isinstance(prop, tuple) or isinstance(prop, list):
        prop = [str(x) if isinstance(x, unicode) else x for x in prop]

    return (event[0], prop)

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

    def test_msgpack_idempotent(self):
        # test that what we put in, we can get out
        with tempfile.NamedTemporaryFile() as tmpf:
            vw = vivisect.VivWorkspace()
            vw.setMeta('StorageName', tmpf.name)
            vw.setMeta('StorageModule', 'vivisect.storage.mpfile')
            add_events(vw)
            vw.saveWorkspace()
            tmpf.flush()

            ovw = vivisect.VivWorkspace()
            ovw.setMeta('StorageModule', 'vivisect.storage.mpfile')
            # So this is a bit naughty, but just the act of creating a workspace
            # induces some events in to the workspace. Nothing crazy, just some va sets
            # so delete those so we can have a clean comparison
            ovw._event_list = []
            ovw.loadWorkspace(tmpf.name)

            old = vw.exportWorkspace()
            new = ovw.exportWorkspace()
            self.assertEqual(len(old), 35)
            self.assertEqual(len(new), 36)  # the last event is a setMeta made by loadWorkspace
            self.assertEqual(new[-1], (VWE_SETMETA, ('StorageName', tmpf.name)))
            for idx in range(len(old)):
                self.assertEqual(normUnicode(old[idx]), normUnicode(new[idx]))

    def test_msgpack_to_basicfile(self):
        # make sure we're on par with what the OG storage mechanism can do
        with tempfile.NamedTemporaryFile() as mpfile:
            with tempfile.NamedTemporaryFile() as basicfile:
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
                ogevt = ogvw.exportWorkspace()

                mvw = vivisect.VivWorkspace()
                mvw.setMeta('StorageModule', 'vivisect.storage.mpfile')
                mvw._event_list = []
                mvw.loadWorkspace(mpfile.name)
                mevt = mvw.exportWorkspace()
                self.assertEqual(len(mevt), 36)

                bvw = vivisect.VivWorkspace()
                bvw.setMeta('StorageModule', 'vivisect.storage.basicfile')
                bvw._event_list = []
                bvw.loadWorkspace(basicfile.name)
                bevt = bvw.exportWorkspace()
                self.assertEqual(len(bevt), 36)

                # the last three events are specific to the different storage modules
                for idx in range(len(mevt) - 3):
                    self.assertEqual(normUnicode(mevt[idx]), normUnicode(bevt[idx]))
                    self.assertEqual(normUnicode(ogevt[idx]), normUnicode(bevt[idx]))
