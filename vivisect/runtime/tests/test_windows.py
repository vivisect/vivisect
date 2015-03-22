import sys
import unittest

import vivisect.debug.api as v_dbgapi
import vivisect.lib.thishost as v_thishost
import vivisect.runtime.tests.helpers as v_helpers

@unittest.skipUnless( v_thishost.check(platform='windows'), 'platform!=windows')
class WindowsTest(unittest.TestCase, v_helpers.DebugTestHelper):

    def test_windows_debug_api(self):
        dbg = v_dbgapi.getDebugApi()
        explors = [ p for p in dbg.ps() if p.info('name') == 'explorer.exe' ]
        self.assertEqual( len(explors), 1 )

    def test_windows_debug_exec_fail(self):
        dbg = v_dbgapi.getDebugApi()
        self.assertRaises(FileNotFoundError, dbg.exec, 'doesnotexist.exe')

    def test_windows_debug_exec(self):
        dbg = v_dbgapi.getDebugApi()
        trace = dbg.exec( sys.executable )
        self.assertEqual( len( trace.threads() ), 1 )
        trace.kill()

