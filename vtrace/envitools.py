import sys
import logging
import argparse

import envi
import envi.memory as e_memory
import envi.archs.i386.regs as eair
import envi.archs.i386.opconst as e_i386const

import vtrace
import vtrace.util as vutil
import vtrace.snapshot as v_snapshot
import vtrace.platforms.base as v_base


logger = logging.getLogger(__name__)

class RegisterException(Exception):
    pass

class MemoryException(Exception):
    pass

class TargetAddrCalcException(Exception):
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


skip_mem_opcodes_by_arch = {
        'i386': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        'amd64': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        }


class LockstepEmulator:
    def __init__(self, trace):
        self.trace = trace
        self.emu = vutil.emuFromTrace(trace)    # this should set up the emulator
        self.arch = self.trace.getMeta("Architecture")

    def go(self):
        count = 0
        skip_mem_opcodes = skip_mem_opcodes_by_arch.get(self.arch, ())

        self.cmpRegs()
        while True:
            print("%4d  Lockstep: 0x%.8x" % (count, self.emu.getProgramCounter()), end='')
            try:
                pc = self.trace.getProgramCounter()
                op = self.emu.parseOpcode(pc)
                print("  %r  " % op, end='')

                # don't compare memory from these instruction results (error prone)
                skip_mem = False
                if op.opcode in skip_mem_opcodes:
                    skip_mem = True

                # store the current opcode addresses for comparison later (for when the 
                #  original register gets clobbered
                if not skip_mem:
                    self.grabMemAddrs(op)

                for oper in op.opers:
                    if skip_mem:
                        continue
                    print("(%r = %x)" % (oper.repr(op), oper.getOperValue(op, self.emu)), end='')

                self.trace.stepi()
                self.emu.stepi()
                count += 1

                if op.mnem == 'rdtsc':
                    self.syncRegsFromTrace()

                print("(eflags: 0x%x)" % self.trace.getRegisterByName('eflags'), end='')
                print("(eflags: 0x%x)" % self.emu.getRegisterByName('eflags'), end='')
                self.cmpRegs()

                if not skip_mem:
                    self.cmpMem(op)

            except RegisterException as msg:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                inp = sys.stdin.readline()
                if inp.startswith('s'):
                    self.syncRegsFromTrace()

            except MemoryException as msg:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                sys.stdin.readline()

            except envi.SegmentationViolation as msg:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                sys.stdin.readline()

            except Exception as msg:
                logger.warning("\t\tLockstep Error: %s" % msg, exc_info=1)
                return
            print('')

    def syncRegsFromTrace(self):
        rsnap = self.trace.getRegisterContext().getRegisterSnap()
        self.emu.setRegisterSnap(rsnap)

    def cmpRegs(self):
        ctx = self.trace.getRegisterContext()
        out = []
        for rname, idx in ctx.getRegisterNameIndexes():
            er = self.emu.getRegister(idx)
            tr = self.trace.getRegisterByName(rname)
            #tr = self.trace.getRegister(idx)
            # debug registers aren't really used much anymore...
            if er != tr and not rname.startswith('debug'):
                out.append("%s (trace: 0x%.8x) (emulated: 0x%.8x)" % (rname, tr, er))

        if len(out):
            raise RegisterException("REGISTER MISMATCH: %s" % '    '.join(out))

        return True

    def grabMemAddrs(self, op):
        '''
        Grab target addresses of opcode operands (before executing)
        for comparison of memory after execution.

        Also, compares the addresses calculated by Trace and EMU.
        '''
        self._tempaddrs = []
        for oper in op.opers:
            # check if we access memory # TODO: use read/write-logging instead
            if not oper.isDeref():
                continue

            taddr = oper.getOperAddr(op, self.trace) # use emu here?  it will likely fail the same either way? emu is faster?
            taddr_emu = oper.getOperAddr(op, self.emu) # use emu here?  it will likely fail the same either way? emu is faster?
            if taddr != taddr_emu:
                raise TargetAddrCalcException('TARGET ADDRESS CALCULATED DIFFERENTLY: 0x%x: %r   (%r: emu: 0x%x,  trace: 0x%x)'\
                        % (op.va, op, oper, taddr, taddr_emu))

            tsize = oper.tsize
            self._tempaddrs.append((taddr, tsize))

    def cmpMem(self, op):
        if len(self._tempaddrs) != len([oper for oper in op.opers if oper.isDeref()]):
            raise Exception("Tester Broken: _tempaddrs and len(deref operands) differ!")

        for taddr, tsize in self._tempaddrs:
            em = self.emu.readMemory(taddr, tsize)
            tm = self.trace.readMemory(taddr, tsize)
            # debug registers aren't really used much anymore...
            if em != tm:
                raise MemoryException("MEMORY MISMATCH: %s (trace: 0x%.8x) (emulated: 0x%.8x)" % (taddr, tm, em))

        return True




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
    emu = vutil.emuFromTrace(snap)
    lockStepEmulator(emu, t)


if __name__ == "__main__":
    # Copy this file out to the vtrace dir for testing and run as main
    sys.exit(main(sys.argv[1:]))
