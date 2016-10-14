import envi.archs.i386 as e_i386
import vivisect.impemu.emulator as v_i_emulator

class i386WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_i386.IntelEmulator):

    taintregs = [ 
        e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX,
        e_i386.REG_EBX, e_i386.REG_EBP, e_i386.REG_ESI,
        e_i386.REG_EDI,
    ]

    def __init__(self, vw, logwrite=False, logread=False, taintbyte='A'):
        e_i386.IntelEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread, taintbyte=taintbyte)
        self.setEmuOpt('i386:reponce',True)
