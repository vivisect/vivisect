import unittest
import vivisect.lib.thishost as v_thishost

@unittest.skipUnless( v_thishost.check(platform='darwin'), 'platform!=darwin')
class DarwinRuntimeTest(unittest.TestCase):

    def test_runtime_darwin_basic(self):
        return
