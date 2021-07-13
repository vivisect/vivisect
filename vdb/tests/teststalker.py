import vdb.stalker as v_stalker
import vtrace.tests as vt_tests

breakpoints = {
    'windows': 'ntdll.NtTerminateProcess',
    'linux': 'libc.exit',
    'freebsd': 'libc.exit',
}


class VdbStalkerTest(vt_tests.VtraceProcessTest):

    def test_vdb_stalker(self):
        plat = self.trace.getMeta('Platform')
        symname = breakpoints.get(plat)
        entry = self.trace.parseExpression(symname)
        v_stalker.addStalkerEntry(self.trace, entry)

        self.runUntilExit()
        self.assertTrue(len(v_stalker.getStalkerHits(self.trace)) >= 2)
