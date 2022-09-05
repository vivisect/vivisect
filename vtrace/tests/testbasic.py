import os
import unittest
import vtrace.tests as vt_tests


class VtraceBasicTest(vt_tests.VtraceProcessTest):

    breakpoints = {
        'windows': 'ntdll.NtTerminateProcess',
        'linux': 'libc.exit',
        'freebsd': 'libc.exit',
    }

    def test_vtrace_getregisters(self):
        self.assertTrue(self.trace.getProgramCounter())
        self.assertTrue(self.trace.getStackCounter())
        self.assertTrue(self.trace.getRegisters())
        self.runUntilExit()

    def test_vtrace_setregisters(self):
        pc = self.trace.getProgramCounter()
        sp = self.trace.getStackCounter()
        regs = self.trace.getRegisters()
        self.trace.setStackCounter(sp)
        self.trace.setProgramCounter(pc)
        self.trace.setRegisters(regs)
        self.runUntilExit()

    def test_vtrace_breakpoint(self):
        plat = self.trace.getMeta('Platform')
        symname = self.breakpoints.get(plat)
        if symname is None:
            raise unittest.SkipTest('no platform breakpoint: %s' % plat)

        pycode = 'trace.setMeta("testbphit", 1)'
        bpid = self.trace.addBreakByExpr(symname)
        self.trace.setBreakpointCode(bpid, pycode)
        self.runUntilExit()

        bp = self.trace.getBreakpoint(bpid)
        self.assertTrue(bp.address is not None)
        self.assertTrue(self.trace.getMeta('testbphit'))

    def test_vtrace_exename(self):
        exename = self.trace.getExe()
        self.assertTrue(os.path.isfile(exename))
        self.assertTrue(exename.lower().find('python') != -1)

    def test_vtrace_mmaps(self):
        pymapfound = False
        for va, size, perms, fname in self.trace.getMemoryMaps():
            if fname.lower().find('python') != -1:
                pymapfound = True
                break
        self.assertTrue(pymapfound)


# All of the above "simple" tests should also work in the "exec" case
class VtraceBasicExecTest(VtraceBasicTest, vt_tests.VtraceExecTest):
    breakpoints = {
        'windows': 'ntdll.NtTerminateProcess',
        'linux': 'ld.malloc',
        'freebsd': 'ld._rtld_thread_init',
    }
