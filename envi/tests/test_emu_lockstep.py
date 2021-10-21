import types
import unittest
import vtrace.tests as vt_tests
from vtrace.envitools import Lockstepper

import envi
import envi.memory as e_mem
import envi.archs.i386 as e_i386

undefs = {
    'amd64': {
        ('or', 'eflags'): e_i386.EFLAGS_AF,
        ('imul', 'eflags'): e_i386.EFLAGS_AF | e_i386.EFLAGS_ZF,
        ('shr', 'eflags'): e_i386.EFLAGS_AF,
        ('shl', 'eflags'): e_i386.EFLAGS_AF,
    },
    'i386': {
        ('or', 'eflags'): e_i386.EFLAGS_AF,
        ('imul', 'eflags'): e_i386.EFLAGS_AF,
        ('shr', 'eflags'): e_i386.EFLAGS_AF,
        ('shl', 'eflags'): e_i386.EFLAGS_AF,
    }
}


def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
    '''
    Monkey patching the emulator's actual getByteDef because the emu._map_defs isn't
    populated and populating it via just ripping through all the actual memory maps
    leads to a bunch of partial read errors that I don't feel like dealing with right now.
    '''
    byts = self.readMemory(va, 16)
    return self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(byts, 0, va)


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
