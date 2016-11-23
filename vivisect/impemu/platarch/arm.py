import envi.archs.arm as e_arm
import vivisect.impemu.emulator as v_i_emulator

class ArmWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_arm.ArmEmulator):

    taintregs = [ x for x in range(13) ]

    def __init__(self, vw, logwrite=False, logread=False):
        e_arm.ArmEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)

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
