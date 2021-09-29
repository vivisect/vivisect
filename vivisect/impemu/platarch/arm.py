import logging

import envi
import envi.archs.arm as e_arm
from envi.archs.arm.regs import *

import vivisect.exc as v_exc
import vivisect.impemu.emulator as v_i_emulator

import visgraph.pathcore as vg_path

logger = logging.getLogger(__name__)


class ArmWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_arm.ArmEmulator):

    taintregs = [x for x in range(13)]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_arm.ArmEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setMemArchitecture(envi.ARCH_ARMV7)

    def setThumbMode(self, thumb=1):
        e_arm.ArmEmulator.setThumbMode(self, thumb)

    def setArmMode(self, arm=1):
        e_arm.ArmEmulator.setArmMode(self, arm)

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        '''
        Caching version.

        We can make an opcode *faster* with the workspace because of
        getByteDef etc... use it.

        Made for ARM, because envi.Emulator doesn't understand the Thumb flag
        '''
        if arch == envi.ARCH_DEFAULT:
            tmode = self.getFlag(PSR_T_bit)
            arch = (envi.ARCH_ARMV7, envi.ARCH_THUMB)[tmode]

        return self.vw.parseOpcode(va, arch=arch)

    def stepi(self):
        # NOTE: when we step, we *always* want to be stepping over calls
        # (and possibly import emulate them)
        starteip = self.getProgramCounter()

        # parse out an opcode
        tmode = self.getFlag(PSR_T_bit)
        # logger.debug("tmode: %x", tmode)
        op = self.parseOpcode(starteip | tmode)
        if self.emumon:
            self.emumon.prehook(self, op, starteip)

        # Execute the opcode
        self.executeOpcode(op)
        vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

        endeip = self.getProgramCounter()

        if self.emumon:
            self.emumon.posthook(self, op, endeip)

        if not self.checkCall(starteip, endeip, op):
            self.checkBranches(starteip, endeip, op)

    def _prep(self, funcva, tmode=None):
        if tmode is not None:
            # we're forcing thumb or arm mode... update the flag
            self.setFlag(PSR_T_bit, tmode)
            logger.debug("funcva thumb==%d  (forced):  0x%x", tmode, funcva)

        elif funcva & 3:
            # if the va isn't 4-byte aligned, it's gotta be thumb
            self.setFlag(PSR_T_bit, 1)
            funcva &= -2
            logger.debug("funcva is THUMB(addr):  0x%x", funcva)

        else:
            loc = self.vw.getLocation(funcva)
            if loc is not None:
                # if we have a opcode location, use it's iflags to determine mode
                lva, lsz, lt, lti = loc
                if (lti & envi.ARCH_MASK) == envi.ARCH_THUMB:
                    self.setFlag(PSR_T_bit, 1)
                    logger.debug("funcva is THUMB(loc):  0x%x", funcva)
                else:
                    logger.debug("funcva is ARM(loc):  0x%x", funcva)

            else:
                # otherwise, let's use some heuristics to guess.
                armthumb = 0
                armop  = None
                thumbop = None
                try:
                    thumbop = self.parseOpcode(funcva | 1)
                    armthumb -= 1
                    if thumbop.mnem == 'push':
                        armthumb -= 5
                    elif thumbop.mnem == 'ldr':
                        armthumb -= 2

                except InvalidInstruction as e:
                    logger.debug("  heuristics: decoding ARM: %r", e)


                try:
                    armop = self.parseOpcode(funcva)
                    armthumb += 1
                    if armop.mnem == 'push':
                        armthumb += 5
                    elif armop.mnem == 'ldr':
                        armthumb += 2

                except InvalidInstruction as e:
                    logger.debug("  heuristics: decoding THUMB: %r", e)


                if armop is None and thumbop is None:
                    # we didn't have a single push in either direction
                    logger.warning("TOTAL FAILURE TO DETERMINE THUMB MODE")
                    raise Exception("Neither architecture parsed the first opcode")

                elif armthumb < 0:
                        self.setFlag(PSR_T_bit, 1)
                        logger.debug("ArmWorkspaceEmulator: Heuristically Determined funcva is THUMB:  0x%x", funcva)
                else:
                    self.setFlag(PSR_T_bit, 0)
                    logger.debug("ArmWorkspaceEmulator: Heuristically Determined funcva is ARM:  0x%x", funcva)


        self.funcva = funcva
        return funcva


    def runFunction(self, funcva, stopva=None, maxhit=None, maxloop=None, tmode=None):
        """
        This is a utility function specific to WorkspaceEmulation (and impemu) that
        will emulate, but only inside the given function.  You may specify a stopva
        to return once that location is hit.
        """
        logger.debug('=== emu.runFunction(0x%x, stopva=%r, maxhit=%r, maxloop=%r, tmode=%r)', funcva, stopva, maxhit, maxloop, tmode)
        funcva = self._prep(funcva, tmode)


        # Let the current (should be base also) path know where we are starting
        vg_path.setNodeProp(self.curpath, 'bva', funcva)

        hits = {}
        todo = [(funcva, self.getEmuSnap(), self.path)]
        vw = self.vw    # Save a dereference many many times

        while len(todo):
            va, esnap, self.curpath = todo.pop()

            self.setEmuSnap(esnap)

            self.setProgramCounter(va)
            tmode = self.getFlag(PSR_T_bit)

            # Check if we are beyond our loop max...
            if maxloop is not None:
                lcount = vg_path.getPathLoopCount(self.curpath, 'bva', va)
                if lcount > maxloop:
                    continue

            while True:

                starteip = self.getProgramCounter()

                if not vw.isValidPointer(starteip):
                    break

                if starteip == stopva:
                    return

                # Check straight hit count...
                if maxhit is not None:
                    h = hits.get(starteip, 0)
                    h += 1
                    if h > maxhit:
                        break
                    hits[starteip] = h

                # If we ran out of path (branches that went
                # somewhere that we couldn't follow?
                if self.curpath is None:
                    break

                try:

                    # FIXME unify with stepi code...
                    op = self.parseOpcode(starteip | tmode)

                    self.op = op
                    if self.emumon:
                        try:
                            self.emumon.prehook(self, op, starteip)
                        except v_exc.BadOpBytes as e:
                            logger.debug(repr(e))
                            break
                        except Exception as e:
                            logger.log(self._log_level, "funcva: 0x%x opva: 0x%x:  %r   (%r) (in emumon prehook: %r)", funcva, starteip, op, e, self.emumon)

                        if self.emustop:
                            return

                    # Execute the opcode
                    self.executeOpcode(op)
                    vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

                    endeip = self.getProgramCounter()

                    if self.emumon:
                        try:
                            self.emumon.posthook(self, op, endeip)
                        except Exception as e:
                            logger.log(self._log_level, "funcva: 0x%x opva: 0x%x:  %r   (%r) (in emumon posthook: %r)", funcva, starteip, op, e, self.emumon)
                        if self.emustop:
                            return

                    iscall = self.checkCall(starteip, endeip, op)
                    if self.emustop:
                        return

                    # If it wasn't a call, check for branches, if so, add them to
                    # the todo list and go around again...
                    if not iscall:
                        blist = self.checkBranches(starteip, endeip, op)
                        if len(blist):
                            # pc in the snap will be wrong, but over-ridden at restore
                            esnap = self.getEmuSnap()
                            for bva, bpath in blist:
                                todo.append((bva, esnap, bpath))
                            break

                    else:
                        # check if we've blx'd to a different thumb state.  if so,
                        # be sure to return to the original tmode before continuing emulation pass
                        newtmode = self.getFlag(PSR_T_bit)
                        if newtmode != tmode:
                            self.setFlag(PSR_T_bit, tmode)

                    # If we enounter a procedure exit, it doesn't
                    # matter what EIP is, we're done here.
                    if op.iflags & envi.IF_RET:
                        vg_path.setNodeProp(self.curpath, 'cleanret', True)
                        break

                except envi.UnsupportedInstruction as e:
                    if self.strictops:
                        logger.debug('runFunction breaking after unsupported instruction: 0x%08x %s', e.op.va, e.op.mnem)
                        raise e
                    else:
                        logger.debug('runFunction continuing after unsupported instruction: 0x%08x %s', e.op.va, e.op.mnem)
                        self.setProgramCounter(e.op.va+ e.op.size)
                except Exception as e:
                    if self.emumon is not None:
                        self.emumon.logAnomaly(self, starteip, str(e))
                    logger.debug('runFunction breaking after exception (fva: 0x%x): %s', funcva, e)
                    break # If we exc during execution, this branch is dead.

class ThumbWorkspaceEmulator(ArmWorkspaceEmulator):
    def __init__(self, vw, **kwargs):
        ArmWorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setThumbMode()
        self.setMemArchitecture(envi.ARCH_THUMB)

    def runFunction(self, funcva, stopva=None, maxhit=None, maxloop=None, tmode=None):
        return ArmWorkspaceEmulator.runFunction(self, funcva, stopva, maxhit, maxloop, tmode=1)

class Thumb16WorkspaceEmulator(ArmWorkspaceEmulator):
    def __init__(self, vw, **kwargs):
        ArmWorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setThumbMode()
        self.setMemArchitecture(envi.ARCH_THUMB16)

    def runFunction(self, funcva, stopva=None, maxhit=None, maxloop=None, tmode=None):
        return ArmWorkspaceEmulator.runFunction(self, funcva, stopva, maxhit, maxloop, tmode=1)
'''
st0len gratuitously from wikipedia:

    ARM[edit]
    The standard ARM calling convention allocates the 16 ARM registers as:
    r15 is the program counter.
    r14 is the link register. (The BL instruction, used in a subroutine call, stores the return address in this register).
    r13 is the stack pointer. (The Push/Pop instructions in "Thumb" operating mode use this register only).
    r12 is the Intra-Procedure-call scratch register.
    r4 to r11: used to hold local variables.
    r0 to r3: used to hold argument values passed to a subroutine, and also hold results returned from a subroutine.

    If the type of value returned is too large to fit in r0 to r3, or whose size cannot be determined statically at compile time, then the caller must allocate space for that value at run time, and pass a pointer to that space in r0.

    Subroutines must preserve the contents of r4 to r11 and the stack pointer. (Perhaps by saving them to the stack in the function prologue, then using them as scratch space, then restoring them from the stack in the function epilogue). In particular, subroutines that call other subroutines *must* save the return address in the link register r14 to the stack before calling those other subroutines. However, such subroutines do not need to return that value to r14-they merely need to load that value into r15, the program counter, to return.

    The ARM stack is full-descending.[3]

    This calling convention causes a "typical" ARM subroutine to
    * In the prolog, push r4 to r11 to the stack, and push the return address in r14, to the stack. (This can be done with a single STM instruction).
    * copy any passed arguments (in r0 to r3) to the local scratch registers (r4 to r11).
    * allocate other local variables to the remaining local scratch registers (r4 to r11).
    * do calculations and call other subroutines as necessary using BL, assuming r0 to r3, r12 and r14 will not be preserved.
    * put the result in r0
    * In the epilog, pull r4 to r11 from the stack, and pulls the return address to the program counter r15. (This can be done with a single LDM instruction).
'''
