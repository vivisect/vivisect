import sys
import unittest

import vivisect.lib.thishost as v_thishost
import vivisect.debug.debugger as v_debugger
import vivisect.runtime.tests.helpers as v_helpers

@unittest.skipUnless( v_thishost.check(platform='windows'), 'platform!=windows')
class WindowsTest(unittest.TestCase, v_helpers.DebugTestHelper):

    def test_windows_debug_api(self):
        dbg = v_debugger.getDebugger()
        explors = [ p for p in dbg.getProcessList() if p.getProcInfo('name') == 'explorer.exe' ]
        self.assertEqual( len(explors), 1 )

    def test_windows_debug_exec_fail(self):
        dbg = v_debugger.getDebugger()
        self.assertRaises(FileNotFoundError, dbg.exec, 'doesnotexist.exe')

    def test_windows_debug_exec(self):
        dbg = v_debugger.getDebugger()
        trace = dbg.exec( sys.executable )
        self.assertEqual( len( trace.threads() ), 1 )
        trace.kill()

    def test_windows_debug_exec_libs(self):
        dbg = v_debugger.getDebugger()
        trace = dbg.exec( sys.executable )
        self.assertIsNotNone( trace.getLibByName('kernel32') )
        trace.kill()

