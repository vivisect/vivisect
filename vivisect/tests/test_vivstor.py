import shutil
import unittest
import tempfile

import vivisect.vivstor as v_vivstor

class VivStorTest(unittest.TestCase):

    def test_vivstor_dirlock(self):

        dirname = tempfile.mkdtemp()

        try:

            lock1 = v_vivstor.VivDirLock(dirname)
            lock2 = v_vivstor.VivDirLock(dirname, timeout=0.1)

            with lock1:
                self.assertFalse( lock2.acquire() )

        finally:
            shutil.rmtree( dirname )

