import sys
import argparse

import envi
import envi.memory as e_memory
import envi.archs.i386 as e_i386  # FIXME This should NOT have to be here

import vtrace
import vtrace.snapshot as v_snapshot
import vtrace.platforms.base as v_base


class RegisterException(Exception):
    pass


def cmpRegs(emu, trace):
    ctx = trace.getRegisterContext()
    for rname, idx in ctx.getRegisterNameIndexes():
        er = emu.getRegister(idx)
        tr = trace.getRegisterByName(rname)
        # debug registers aren't really used much anymore...
        if er != tr and not rname.startswith('debug'):
            raise RegisterException("REGISTER MISMATCH: %s (trace: 0x%.8x) (emulated: 0x%.8x)" % (rname, tr, er))
    return True


def emuFromTrace(trace):
    '''
    Produce an envi emulator for this tracer object.
    '''
    arch = trace.getMeta('Architecture')
    plat = trace.getMeta('Platform')
    amod = envi.getArchModule(arch)
    emu = amod.getEmulator()

    # could use {get,set}MemorySnap if trace inherited from MemoryObject
    for va, size, perms, fname in trace.getMemoryMaps():
        try:
            # So linux maps in a PROT_NONE page for efficient library sharing, so we have to take that into account
            if (not perms & e_memory.MM_READ):
                continue
            if plat == 'linux' and fname in ['[vvar]']:
                continue
            bytez = trace.readMemory(va, size)
            emu.addMemoryMap(va, perms, fname, bytez)
        except vtrace.PlatformException:
            print('failed to map: 0x{:x} into emu'.format(va, size))
            continue

    rsnap = trace.getRegisterContext().getRegisterSnap()
    emu.setRegisterSnap(rsnap)

    if plat == 'windows':
        emu.setSegmentInfo(e_i386.SEG_FS, trace.getThreads()[trace.getMeta('ThreadId')], 0xffffffff)

    return emu


def lockStepEmulator(emu, trace):
    while True:
        print("Lockstep: 0x%.8x" % emu.getProgramCounter())
        try:
            pc = emu.getProgramCounter()
            op = emu.parseOpcode(pc)
            trace.stepi()
            emu.stepi()
            cmpRegs(emu, trace)
        except RegisterException as msg:
            print("Lockstep Error: %s: %s" % (repr(op), msg))
            # setRegs(emu, trace)  # TODO: Where is this from?
            sys.stdin.readline()
        except Exception as msg:
            import traceback
            traceback.print_exc()
            print("Lockstep Error: %s" % msg)
            return


class TraceEmulator(vtrace.Trace, v_base.TracerBase):
    """
    Wrap an arbitrary emulator in a Tracer compatible API.
    """
    def __init__(self, emu):
        self.emu = emu
        archname = emu.vw.getMeta('Architecture')
        vtrace.Trace.__init__(self, archname)
        v_base.TracerBase.__init__(self)

        # Fake out being attached
        self.attached = True
        self.pid = 0x56

        self.setRegisterInfo(emu.getRegisterInfo())

    def getPointerSize(self):
        return self.emu.getPointerSize()

    def platformStepi(self):
        self.emu.stepi()

    def platformWait(self):
        # We only support single step events now
        return True

    def archGetRegCtx(self):
        return self.emu

    def platformGetRegCtx(self, threadid):
        return self.emu

    def platformSetRegCtx(self, threadid, ctx):
        self.setRegisterSnap(ctx.getRegisterSnap())

    def platformProcessEvent(self, event):
        self.fireNotifiers(vtrace.NOTIFY_STEP)

    def platformReadMemory(self, va, size):
        return self.emu.readMemory(va, size)

    def platformWriteMemory(self, va, bytes):
        return self.emu.writeMemory(va, bytes)

    def platformGetMaps(self):
        return self.emu.getMemoryMaps()

    def platformGetThreads(self):
        return {1: 0xffff0000}

    def platformGetFds(self):
        return []  # FIXME perhaps tie this into magic?

    def getStackTrace(self):
        # FIXME i386...
        return [(self.emu.getProgramCounter(), 0), (0, 0)]

    def platformDetach(self):
        pass


def setup():
    ap = argparse.ArgumentParser('lockstep')
    ap.add_argument('pid', type=int, help='PID of process to attach to (remember to have ptrace permissions)')
    ap.add_argument('expr', type=str, help='Expression of an address to break the process on')
    ap.add_argument('--save', type=str, help='Save vtrace snapshot to the provided file')
    ap.add_argument('--args', type=str, help='Instead of attaching to a process, run this process with the given args')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    t = vtrace.getTrace()
    t.attach(opts.pid)
    symaddr = t.parseExpression(opts.expr)
    t.addBreakpoint(vtrace.Breakpoint(symaddr))
    while t.getProgramCounter() != symaddr:
        t.run()
    snap = v_snapshot.takeSnapshot(t)
    if opts.save:
        # You may open this file in vdb to follow along
        snap.saveToFile(opts.save)
    emu = emuFromTrace(snap)
    lockStepEmulator(emu, t)


if __name__ == "__main__":
    # Copy this file out to the vtrace dir for testing and run as main
    sys.exit(main(sys.argv[1:]))
