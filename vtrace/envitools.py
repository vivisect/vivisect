import sys
import logging
import argparse

import envi
import envi.memory as e_mem
import envi.archs.i386.opconst as e_i386const

import vtrace
import vtrace.exc as v_exc
import vtrace.util as vutil
import vtrace.snapshot as v_snapshot
import vtrace.platforms.base as v_base


logger = logging.getLogger(__name__)


def cmpRegs(emu, trace):
    ctx = trace.getRegisterContext()
    for rname, idx in ctx.getRegisterNameIndexes():
        er = emu.getRegister(idx)
        tr = trace.getRegisterByName(rname)
        # debug registers aren't really used much anymore...
        if er != tr and not rname.startswith('debug'):
            raise v_exc.RegisterException("REGISTER MISMATCH: %s (trace: 0x%.8x) (emulated: 0x%.8x)" % (rname, tr, er))
    return True


skip_mem_opcodes_by_arch = {
        'i386': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        'amd64': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        }


class LockStepMonitor:
    '''
    This is an abstract class intended to be subclassed for different purposes

    Each callback should return True or False for whether the LockStepper
    should continue or fail
    '''
    def _cb_opcode_pre(self, lstep):
        '''
        Called before *each* instruction is executed.
        This (and _post) are outliers, where nothing actually went wrong.

        These callbacks are for use of analysis context only.
        '''
        return True

    def _cb_opcode_post(self, lstep):
        '''
        Called after *each* instruction is executed.
        This (and _pre) are outliers, where nothing actually went wrong.

        These callbacks are for use of analysis context only.
        '''
        return True

    def _cb_branch_failure(self, lstep, tracepc, emupc):
        '''
        Called when the Emulator and Tracer think the ProgramCounter should
        be different things.
        '''
        return False

    def _cb_decode_failure(self, lstep, traceop, emuop):
        '''
        Called when the Emulator and Tracer decode the next instruction should
        be different things.
        '''
        return False

    def _cb_register_failure(self, lstep, traceregs, emuregs):
        '''
        Called when the Register Context differs between the Emu and Tracer
        '''
        return False

    def _cb_memory_failure(self, lstep, va_diffs):
        '''
        Called when Memory differences are detected between the Emu and Tracer
        '''
        return False

    def _cb_trace_exc(self, lstep, exc):
        '''
        Called when Tracer.stepi() throws exceptions
        '''
        return False

    def _cb_emu_exc(self, lstep, exc):
        '''
        Called when Emu.stepi() throws exceptions
        '''
        return False

    def _cb_unknown_exception(self, lstep, exc):
        '''
        Called when we haven't prepared for this kind of exception!
        '''
        return False

class LockStepper:
    '''
    LockStepper is used for comparing execution of an emulator to execution of 
    a debug trace.  An emulator copy is created of the debug trace, where 
    memory and registers are duplicated.  
    '''
    def __init__(self, trace, fail_handler=None):

        self.trace = trace
        if fail_handler:
            self.fail_handler = fail_handler
        else:
            self.fail_handler = LockStepMonitor()

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

        self.syncRegsFromTrace()

    def syncRegsFromTrace(self):
        '''
        Syncronizes the Register Context from the Trace to the Emulator
        '''
        regctx = self.trace.getRegisterContext()
        self.emu.setRegisterSnap(regctx.getRegisterSnap())

    def syncMemFromTrace(self):
        '''
        Syncronizes the MemoryMaps from the Trace to the Emulator
        (in reality, it clears the differences tracked)
        '''
        self.memcache.pagedirty = {}
        self.memcache.pagecache = {}

    def stepi(self, count=1):
        '''
        Execute/Emulate one instruction and compare memory/registers

        If issues are discovered, 
        '''
        cont = True
        for i in range(count):
            if not cont:
                break

            try:
                if not self.callback_handler._cb_opcode_pre(self):
                    break

                # get and compare Program Counter for both
                emupc = self.emu.getProgramCounter()
                tracepc = self.trace.getProgramCounter()
                if emupc != tracepc:
                    if not self.fail_handler._cb_branch_failure(self, tracepc, emupc):
                        break

                op1 = self.emu.parseOpcode(emupc)
                op2 = self.trace.parseOpcode(tracepc)
                if op1 != op2:
                    if not self.fail_handler._cb_decode_failure(self, op1, op2):
                        break

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

            except v_exc.RegisterException as e:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                cond = self.cbhandler._cb_register_failure(self)

            except v_exc.MemoryException as e:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                cond = self.cbhandler._cb_memory_failure(self)

            except Exception as e:
                logger.warning("\t\tLockstep Error: %s" % e, exc_info=1)
                if self.fail_handler:
                    cont = self.fail_handler._cb_unknown_exception(self, exc)

            finally:
                if not self.cbhandler._cb_opcode_post(self):
                    break

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
                raise v_exc.RegisterException('LockStep: emu 0x%.8x %s %s=0x%.8x | trace 0x%.8x %s %s=0x%.8x' % (emuop.va, repr(emuop), regname, regval, traceop.va, repr(traceop), regname, traceval))

    def cmppages(self, emuop, traceop):
        for va, bytez in self.memcache.getDirtyPages():
            tbytez = self.trace.readMemory(va, len(bytez))
            diffs = e_mem.memdiff(bytez, tbytez)
            if diffs:
                diffstr = ','.join(['0x%.8x: %d' % (va+offset, size) for offset, size in diffs])
                raise v_exc.MemoryException('LockStep: emu 0x%.8x %s | trace 0x%.8x %s | DIFFS: %s' % (emuop.va, repr(emuop), traceop.va, repr(traceop), diffstr))
        self.memcache.clearDirtyPages()


def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
    '''
    Monkey patching the emulator's actual getByteDef because the emu._map_defs isn't
    populated and populating it via just ripping through all the actual memory maps
    leads to a bunch of partial read errors that I don't feel like dealing with right now.
    '''
    byts = self.readMemory(va, 16)
    return self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(byts, 0, va)




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

            except v_exc.RegisterException as msg:
                logger.warning("    \tError: %s: %s" % (repr(op), msg))
                inp = sys.stdin.readline()
                if inp.startswith('s'):
                    self.syncRegsFromTrace()

            except v_exc.MemoryException as msg:
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
            raise v_exc.RegisterException("REGISTER MISMATCH: %s" % '    '.join(out))

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
                raise v_exc.TargetAddrCalcException('TARGET ADDRESS CALCULATED DIFFERENTLY: 0x%x: %r   (%r: emu: 0x%x,  trace: 0x%x)'\
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
                raise v_exc.MemoryException("MEMORY MISMATCH: %s (trace: 0x%.8x) (emulated: 0x%.8x)" % (taddr, tm, em))

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
        except v_exc.RegisterException as msg:
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
