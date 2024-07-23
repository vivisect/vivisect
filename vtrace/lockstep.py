import sys
import logging
import argparse

import envi
import envi.memory as e_mem
import envi.archs.i386 as e_i386
import envi.archs.i386.opconst as e_i386const

import vtrace
import vtrace.exc as v_exc
import vtrace.util as vutil
import vtrace.snapshot as v_snapshot
import vtrace.platforms.base as v_base


logger = logging.getLogger(__name__)

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

skip_mem_opcodes_by_arch = {
        'i386': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        'amd64': (e_i386const.INS_NOP, e_i386const.INS_LEA),
        }

resync_reg_opcodes_by_arch = {
        'i386': (e_i386const.INS_RDTSC, e_i386const.INS_SYSCALL),
        'amd64': (e_i386const.INS_RDTSC, e_i386const.INS_SYSCALL),
        }


###### LockStepper and LockStepMonitor
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

    def _cb_register_failure(self, lstep, exc):
        '''
        Called when the Register Context differs between the Emu and Tracer
        '''
        return False

    def _cb_memory_failure(self, lstep, exc):
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

    def _cb_segv(self):
        '''
        Called when a SegmentationViolation is thrown
        '''
        return False


class InteractiveLSMon(LockStepMonitor):
    '''
    This is a LockStepMonitor intended for Interactive LockStep Emulation

    It will prompt after certain failures, allowing the user to inspect issues
    and fix them with context.  After Register differences, user can type "s" 
    to resync the registers from the tdebug race.
    '''
    def __init__(self, arch):
        self.count = 0
        self.skip_mem_opcodes = skip_mem_opcodes_by_arch.get(arch)

    def _cb_opcode_pre(self, lstep):
        self.count += 1
        print("\n%4d  Lockstep: 0x%.8x  %-20r" % (self.count, lstep.emu.getProgramCounter(), lstep.op1), end='')
        op = lstep.op1
        for oper in op.opers:
            if op.opcode in self.skip_mem_opcodes:
                continue
            print("(%r = %x)" % (oper.repr(op), oper.getOperValue(op, lstep.emu)), end='')

        return True

    def _cb_opcode_post(self, lstep):
        print("(flags: 0x%x)" % lstep.trace.getStatusRegister(), end='')
        print("(flags: 0x%x)" % lstep.emu.getStatusRegister(), end='')
        return True

    def _cb_register_failure(self, lstep, exc):
        inp = input('"s" to reSync registers from trace to emu')
        if inp.startswith('s'):
            lstep.syncRegsFromTrace()
        return True

    def _cb_memory_failure(self, lstep, exc):
        inp = input('Memory Failure: "Enter" to continue')
        return True

    def _cb_segv(self):
        inp = input('Segmentation Violation: "Enter" to continue')
        return True


class LockStepper:
    '''
    LockStepper is used for comparing execution of an emulator to execution of 
    a debug trace.  An emulator copy is created of the debug trace, where 
    memory and registers are duplicated.  
    '''
    def __init__(self, trace, cbhandler=None):

        self.trace = trace
        if cbhandler:
            self.cbhandler = cbhandler
        else:
            self.cbhandler = LockStepMonitor()

        self.archname = trace.getMeta('Architecture')
        self.arch = envi.getArchModule(self.archname)

        self.emu = self.arch.getEmulator()
        self.memcache = e_mem.MemoryCache(self.trace)

        plat = trace.getMeta('Platform')
        self.resync_reg_opcodes = resync_reg_opcodes_by_arch.get(self.archname, ())

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

        If issues are discovered, and if a callback handler has been registered,
        appropriate callbacks are triggered on that cbhandler.
        
        For example:
        cbhandler._cb_branch_failure
        cbhandler._cb_decode_failure
        cbhandler._cb_opcode_pre
        cbhandler._cb_register_failure
        cbhandler._cb_memory_failure
        cbhandler._cb_segv
        cbhandler._cb_unknown_exception
        '''
        cont = True
        for i in range(count):
            if not cont:
                break

            try:
                # get and compare Program Counter for both
                emupc = self.emu.getProgramCounter()
                tracepc = self.trace.getProgramCounter()
                if emupc != tracepc:
                    if not self.cbhandler._cb_branch_failure(self, tracepc, emupc):
                        break

                self.op1 = self.emu.parseOpcode(emupc)
                self.op2 = self.trace.parseOpcode(tracepc)
                if self.op1 != self.op2:
                    if not self.cbhandler._cb_decode_failure(self, self.op1, self.op2):
                        break

                if not self.cbhandler._cb_opcode_pre(self):
                    break

                try:
                    self.trace.stepi()

                except Exception as e:
                    raise Exception('Trace Exception: %s on %s' % (e, repr(self.op2)))

                try:
                    self.emu.stepi()

                except Exception as e:
                    raise Exception('Emu Exception: %s on %s' % (e, repr(self.op1)))

                self.cmpregs()
                self.cmppages()

            except v_exc.RegisterException as exc:
                logger.warning("    \tError: %s: %s" % (repr(self.op1), exc))
                cont = self.cbhandler._cb_register_failure(self, exc)

            except v_exc.MemoryException as exc:
                logger.warning("    \tError: %s: %s" % (repr(self.op1), exc))
                cont = self.cbhandler._cb_memory_failure(self, exc)

            except envi.SegmentationViolation as exc:
                logger.warning("    \tError: %s: %s" % (repr(self.op1), exc))
                cont = self.cbhandler._cb_segv(self)

            except Exception as exc:
                logger.warning("\t\tLockstep Error: %s" % exc, exc_info=1)
                if self.cbhandler:
                    cont = self.cbhandler._cb_unknown_exception(self, exc)

            finally:
                cont = cont and self.cbhandler._cb_opcode_post(self)

        logger.warning("done.")

    def cmpregs(self):
        if self.op1.opcode in self.resync_reg_opcodes:
            logger.info("Resynching Registers: %r" % self.op1)
            self.syncRegsFromTrace()
            return

        badregs = []
        emuregs = self.emu.getRegisters()
        traceregs = self.trace.getRegisters()
        for regname, regval in emuregs.items():
            traceval = traceregs.get(regname)
            mask = undefs.get(self.archname).get((self.op1.mnem, regname))
            if mask is not None:
                self.emu.setRegisterByName(regname, traceval)
                regval &= ~mask
                traceval &= ~mask

            if traceval != regval:
                badregs.append("%s (trace: 0x%.8x) (emulated: 0x%.8x)" % (regname, traceval, regval))
        
        if badregs:
            raise v_exc.RegisterException('LockStep: emu 0x%.8x %s %x | trace 0x%.8x %s: %r ' % (self.op1.va, repr(self.op1), self.op1.opcode, self.op2.va, repr(self.op2), '    '.join(badregs)), emuregs, traceregs)

    def cmppages(self):

        for va, bytez in self.memcache.getDirtyPages():
            tbytez = self.trace.readMemory(va, len(bytez))
            diffs = e_mem.memdiff(bytez, tbytez)
            if diffs:
                diffstr = ','.join(['0x%.8x: %d' % (va+offset, size) for offset, size in diffs])
                raise v_exc.MemoryException('LockStep: emu 0x%.8x %s | trace 0x%.8x %s | DIFFS: %s' % (self.op1.va, repr(self.op1), self.op2.va, repr(self.op2), diffstr))
        self.memcache.clearDirtyPages()

def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
    '''
    Monkey patching the emulator's actual getByteDef because the emu._map_defs isn't
    populated and populating it via just ripping through all the actual memory maps
    leads to a bunch of partial read errors that I don't feel like dealing with right now.
    '''
    byts = self.readMemory(va, 16)
    return self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(byts, 0, va)


###### TraceEmulator fusion magic
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

    def archGetRegCtx(self):
        return self.emu

    def archGetRegisterGroups(self):
        return self.arch.archGetRegisterGroups()

    def pointerString(self, val):
        return self.arch.pointerString(val)

    def getStackTrace(self):
        # FIXME i386...
        return [(self.emu.getProgramCounter(), 0), (0, 0)]

    def platformDetach(self):
        pass

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        return self.emu.parseOpcode(va, arch)


####### Command Line Support
def setup():
    ap = argparse.ArgumentParser('lockstep')
    ap.add_argument('--pid', type=int, help='PID of process to attach to (remember to have ptrace permissions)')
    ap.add_argument('--expr', type=str, help='Expression of an address to break the process on')
    ap.add_argument('--save', type=str, help='Save vtrace snapshot to the provided file')
    ap.add_argument('--args', type=str, help='Instead of attaching to a process, run this process with the given args')
    return ap


def main(argv):
    opts = setup().parse_args(argv)
    t = vtrace.getTrace()
    if opts.args:
        t.execute(opts.args)
    else:
        t.attach(opts.pid)

    if opts.expr:
        symaddr = t.parseExpression(opts.expr)
        t.addBreakpoint(vtrace.Breakpoint(symaddr))
        while t.getProgramCounter() != symaddr:
            t.run()
    if opts.save:
        # You may open this file in vdb to follow along
        snap = v_snapshot.takeSnapshot(t)
        snap.saveToFile(opts.save)

    arch = t.getArchName()
    lsmon = InteractiveLSMon(arch)
    lsr = LockStepper(t, lsmon)


    lsr.stepi(0xffffffff)


if __name__ == "__main__":
    # Copy this file out to the vtrace dir for testing and run as main
    sys.exit(main(sys.argv[1:]))
