import vtrace.tests as vt_tests

breakpoints = {
    'windows': 'ntdll.NtTerminateProcess',
    'linux': 'libc.exit',
    'freebsd': 'libc.exit',
}


class VtraceExpressionTest(vt_tests.VtraceProcessTest):
    def test_vtrace_sym(self):
        plat = self.trace.getMeta('Platform')
        symname = breakpoints.get(plat)
        entry = self.trace.parseExpression(symname)
        addEntry = self.trace.parseExpression(symname + " + 5")
        self.assertTrue(entry + 5 == addEntry)

    def test_baselib(self):
        plat = self.trace.getMeta('Platform')
        libname = breakpoints.get(plat).split('.')[0]
        entry = self.trace.parseExpression(libname)
        addEntry = self.trace.parseExpression(libname + " + 5")
        # grab a symbol in the library and compare offsets against that?
        self.assertTrue(entry + 5 == addEntry)
