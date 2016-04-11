import envi
import envi.archs.arm as e_arm
import vivisect.impemu.emulator as v_i_emulator

import visgraph.pathcore as vg_path
from envi.archs.arm.regs import *

class ArmWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_arm.ArmEmulator):

    taintregs = [ x for x in range(13) ]

    def __init__(self, vw, logwrite=False, logread=False):
        e_arm.ArmEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        self.setMemArchitecture(envi.ARCH_ARMV7)

    def runFunction(self, funcva, stopva=None, maxhit=None, maxloop=None, tmode=None):
        """
        This is a utility function specific to WorkspaceEmulation (and impemu) that
        will emulate, but only inside the given function.  You may specify a stopva
        to return once that location is hit.
        """

        if tmode != None:
            # we're forcing thumb or arm mode... update the flag
            self.setFlag(PSR_T_bit, tmode)

        self.funcva = funcva

        # Let the current (should be base also) path know where we are starting
        vg_path.setNodeProp(self.curpath, 'bva', funcva)

        hits = {}
        todo = [(funcva,self.getEmuSnap(),self.path),]
        vw = self.vw # Save a dereference many many times

        while len(todo):
          #try:  

            va,esnap,self.curpath = todo.pop()

            self.setEmuSnap(esnap)

            self.setProgramCounter(va)

            # Check if we are beyond our loop max...
            if maxloop != None:
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
                if maxhit != None:
                    h = hits.get(starteip, 0)
                    h += 1
                    if h > maxhit:
                        break
                    hits[starteip] = h

                # If we ran out of path (branches that went
                # somewhere that we couldn't follow?
                if self.curpath == None:
                    break

                try:

                    tmode = self.getFlag(PSR_T_bit)
                    # FIXME unify with stepi code...
                    op = self.parseOpcode(starteip | tmode)

                    self.op = op
                    if self.emumon:

                        self.emumon.prehook(self, op, starteip)

                        if self.emustop:
                            return 

                    # Execute the opcode
                    self.executeOpcode(op)
                    vg_path.getNodeProp(self.curpath, 'valist').append(starteip)

                    endeip = self.getProgramCounter()

                    if self.emumon:
                        self.emumon.posthook(self, op, endeip)
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
                            for bva,bpath in blist:
                                todo.append((bva, esnap, bpath))
                            break

                    # If we enounter a procedure exit, it doesn't
                    # matter what EIP is, we're done here.
                    if op.iflags & envi.IF_RET:
                        vg_path.setNodeProp(self.curpath, 'cleanret', True)
                        break
                except envi.UnsupportedInstruction, e:
                    if self.strictops:
                        break
                    else:
                        print 'runFunction continuing after unsupported instruction: 0x%08x %s' % (e.op.va, e.op.mnem)
                        self.setProgramCounter(e.op.va+ e.op.size)
                except Exception, e:
                    #traceback.print_exc()
                    if self.emumon != None:
                        self.emumon.logAnomaly(self, starteip, str(e))

                    break # If we exc during execution, this branch is dead.
          #except:
          #    sys.excepthook(*sys.exc_info())

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
