import types
import unittest
import vtrace.tests as vt_tests
from vtrace.lockstep import LockStepper



breakpoints = {
    ('windows', 'i386'): ('ntdll.RtlAllocateHeap', 500),
    ('windows', 'amd64'): ('ntdll.RtlAllocateHeap', 500),
    # 'linux': 'libc.exit',
    # 'freebsd': 'libc.exit',
}

class LockStepTest(vt_tests.VtraceProcessTest):

    def test_emu_lockstep(self):
        plat = self.trace.getMeta('Platform')
        arch = self.trace.getMeta('Architecture')

        stepinfo = breakpoints.get((plat, arch))
        if stepinfo is None:
            raise unittest.SkipTest('No Lockstep Break: %s %s' % (plat, arch))

        symname, stepcount = stepinfo
        untilva = self.trace.parseExpression(symname)

        # Just like runUntilExit()
        self.proc.stdin.write('testmod\n')
        self.proc.stdin.flush()
        self.trace.run(until=untilva)

        lock = LockStepper(self.trace)
        lock.stepi(stepcount)
