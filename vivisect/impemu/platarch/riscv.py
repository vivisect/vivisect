import envi.archs.riscv.emu as e_RiscVe
import vivisect.impemu.emulator as v_i_emulator

class RiscVWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_RiscVe.RiscVEmulator):

    taintregs = [ x for x in range(10, 18) ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_RiscVe.RiscVEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)