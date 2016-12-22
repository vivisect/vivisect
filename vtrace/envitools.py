import sys
import traceback

import envi
import envi.archs.i386 as e_i386 # FIXME This should NOT have to be here

class RegisterException(Exception):
    pass

def cmpRegs(emu, trace):
    for idx,name in reg_map:
        er = emu.getRegister(idx)
        tr = trace.getRegisterByName(name)
        if er != tr:
            raise RegisterException("REGISTER MISMATCH: %s 0x%.8x 0x%.8x" % (name, tr, er))
    return True

def emuFromTrace(trace):
    '''
    Produce an envi emulator for this tracer object.
    '''
    arch = trace.getMeta('Architecture')
    amod = envi.getArchModule(arch)
    emu = amod.getEmulator()

    # could use {get,set}MemorySnap if trace inherited from MemoryObject
    for va, size, perms, fname in trace.getMemoryMaps():
        try:
            bytez = trace.readMemory(va, size)
            emu.addMemoryMap(va, perms, fname, bytez)
        except vtrace.PlatformException:
            print(('failed to map: 0x{:x} into emu'.format(va, size)))
            continue

    rsnap = trace.getRegisterContext().getRegisterSnap()
    emu.setRegisterSnap(rsnap)

    if trace.getMeta('Platform') == 'windows':
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
            print("Lockstep Error: %s: %s" % (repr(op),msg))
            setRegs(emu, trace)
            sys.stdin.readline()
        except Exception as msg:
            traceback.print_exc()
            print("Lockstep Error: %s" % msg)
            return

import vtrace
import vtrace.platforms.base as v_base

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
        return {1:0xffff0000,}

    def platformGetFds(self):
        return [] #FIXME perhaps tie this into magic?

    def getStackTrace(self):
        # FIXME i386...
        return [(self.emu.getProgramCounter(), 0), (0,0)]

    def platformDetach(self):
        pass

def main():
    import vtrace
    sym = sys.argv[1]
    pid = int(sys.argv[2])
    t = vtrace.getTrace()
    t.attach(pid)
    symaddr = t.parseExpression(sym)
    t.addBreakpoint(vtrace.Breakpoint(symaddr))
    while t.getProgramCounter() != symaddr:
        t.run()
    snap = t.takeSnapshot()
    #snap.saveToFile("woot.snap") # You may open in vdb to follow along
    emu = emulatorFromTrace(snap)
    lockStepEmulator(emu, t)

if __name__ == "__main__":
    # Copy this file out to the vtrace dir for testing and run as main
    main()

