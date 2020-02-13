import envi.archs.i386.emu as e_i386_emu
import envi.archs.i386.regs as e_i386_regs
import vivisect.impemu.emulator as v_i_emulator


class i386WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_i386_emu.IntelEmulator):

    taintregs = [
        e_i386_regs.REG_EAX,
        e_i386_regs.REG_ECX,
        e_i386_regs.REG_EDX,
        e_i386_regs.REG_EBX,
        e_i386_regs.REG_EBP,
        e_i386_regs.REG_ESI,
        e_i386_regs.REG_EDI,
    ]

    def __init__(self, vw, logwrite=False, logread=False):
        e_i386_emu.IntelEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        self.setEmuOpt('i386:reponce', True)
