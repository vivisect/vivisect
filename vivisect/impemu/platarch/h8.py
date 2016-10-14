import envi.archs.h8 as e_h8
import vivisect.impemu.emulator as v_i_emulator

class H8WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_h8.H8Emulator):

    taintregs = [ 
        e_h8.REG_ER0, e_h8.REG_ER1, e_h8.REG_ER2,
    ]

    def __init__(self, vw, logwrite=False, logread=False, taintbyte='A'):
        e_h8.H8Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread, taintbyte=taintbyte)

