import envi.archs.h8.emu as h8_emu
import envi.archs.h8.regs as h8_regs
import vivisect.impemu.emulator as v_i_emulator


class H8WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, h8_emu.H8Emulator):

    taintregs = [h8_regs.REG_ER0, h8_regs.REG_ER1, h8_regs.REG_ER2]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        h8_emu.H8Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)
