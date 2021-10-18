import types
import unittest
import vtrace.tests as vt_tests

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


class LockStepper:

    def __init__(self, trace):

        self.trace = trace

        self.archname = trace.getMeta('Architecture')
        self.arch = envi.getArchModule(self.archname)

        self.emu = self.arch.getEmulator()
        self.memcache = e_mem.MemoryCache(self.trace)

        plat = trace.getMeta('Platform')

        # gotta setup fs at least...
        if plat == 'windows' and self.archname in ('i386', 'amd64'):
            # so 32 and 64 bit are flipped. In x86-land FS:[0] points to the TIB. On x64, it's GS:[0] that points to the
            # TEB
            tid = trace.getCurrentThread()
            tinfo = trace.getThreads().get(tid)
            if self.archname == 'i386':
                self.emu.setSegmentInfo(e_i386.SEG_FS, tinfo, 0xffffffff)
            elif self.archname == 'amd64':
                self.emu.setSegmentInfo(e_i386.SEG_GS, tinfo, 0xffffffff)

        # Monkey patch the emulator's read methods
        self.emu.readMemory = self.memcache.readMemory
        self.emu.writeMemory = self.memcache.writeMemory
        self.emu.getMemoryMap = self.memcache.getMemoryMap
        self.emu.getMemoryMaps = self.memcache.getMemoryMaps
        self.emu.parseOpcode = parseOpcode.__get__(self.emu)

        regctx = trace.getRegisterContext()
        self.emu.setRegisterSnap(regctx.getRegisterSnap())

    def stepi(self, count=1):
        for i in range(count):
            emupc = self.emu.getProgramCounter()
            tracepc = self.trace.getProgramCounter()

            op1 = self.emu.parseOpcode(emupc)

            op2 = self.trace.parseOpcode(tracepc)

            try:
                self.trace.stepi()
            except Exception as e:
                raise Exception('Trace Exception: %s on %s' % (e, repr(op2)))

            try:
                self.emu.stepi()
            except Exception as e:
                raise Exception('Emu Exception: %s on %s' % (e, repr(op1)))

            self.cmpregs(op1, op2)
            self.cmppages(op1, op2)

    def cmpregs(self, emuop, traceop):
        emuregs = self.emu.getRegisters()
        traceregs = self.trace.getRegisters()
        for regname, regval in emuregs.items():
            traceval = traceregs.get(regname)
            mask = undefs.get(self.archname).get((emuop.mnem, regname))
            if mask is not None:
                self.emu.setRegisterByName(regname, traceval)
                regval &= ~mask
                traceval &= ~mask

            if traceval != regval:
                raise Exception('LockStep: emu 0x%.8x %s %s=0x%.8x | trace 0x%.8x %s %s=0x%.8x' % (emuop.va, repr(emuop), regname, regval, traceop.va, repr(traceop), regname, traceval))

    def cmppages(self, emuop, traceop):
        for va, bytez in self.memcache.getDirtyPages():
            tbytez = self.trace.readMemory(va, len(bytez))
            diffs = e_mem.memdiff(bytez, tbytez)
            if diffs:
                diffstr = ','.join(['0x%.8x: %d' % (va+offset, size) for offset, size in diffs])
                raise Exception('LockStep: emu 0x%.8x %s | trace 0x%.8x %s | DIFFS: %s' % (emuop.va, repr(emuop), traceop.va, repr(traceop), diffstr))
        self.memcache.clearDirtyPages()


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
