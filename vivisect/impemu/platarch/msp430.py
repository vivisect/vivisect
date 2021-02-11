import envi.archs.msp430.emu as e_msp430e
import vivisect.impemu.emulator as v_i_emulator

class Msp430WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_msp430e.Msp430Emulator):

    taintregs = [ x for x in range(2, 16) ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_msp430e.Msp430Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)

'''
st0len gratuitously from mspgcc:
    Function calling conventions

    Fixed argument lists

    Function arguments are allocated left to right. They are assigned from r15 to r12. If more parameters are passed than will fit in the registers, the rest are passed on the stack. This should be avoided since the code takes a performance hit when using variables residing on the stack.

    Variable argument lists

    Parameters passed to functions that have a variable argument list (printf, scanf, etc.) are all passed on the stack. Any char parameters are extended to ints.

    Return values

    The various functions types return the results as follows:

    char, int and pointer functions return their values r15

    long and float functions return their values in r15:r14

    long long functions return their values r15:r14:r13:r12

    If the returned value wider than 64 bits, it is returned in memory. The first 'hidden' argument to such a function call will be a memory address. All other arguments will be allocated in the usual way, from r14.
    '''
