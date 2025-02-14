import envi.archs.riscv.emu as riscv_emu
import envi.archs.riscv.regs as riscv_regs
import vivisect.impemu.emulator as v_i_emulator


class RiscVWorkspaceEmulator(v_i_emulator.WorkspaceEmulator):
    # x10 - x17 are the argument registers
    taintregs = [
        riscv_regs.REG_A0, riscv_regs.REG_A1, riscv_regs.REG_A2, riscv_regs.REG_A3,
        riscv_regs.REG_A4, riscv_regs.REG_A5, riscv_regs.REG_A6, riscv_regs.REG_A7,
    ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)


class RiscV32WorkspaceEmulator(RiscVWorkspaceEmulator, riscv_emu.RiscV32Emulator):
    def __init__(self, vw, **kwargs):
        riscv_emu.RiscV32Emulator.__init__(self)
        RiscVWorkspaceEmulator.__init__(self, vw, **kwargs)


class RiscV64WorkspaceEmulator(RiscVWorkspaceEmulator, riscv_emu.RiscV64Emulator):
    def __init__(self, vw, **kwargs):
        riscv_emu.RiscV64Emulator.__init__(self)
        RiscVWorkspaceEmulator.__init__(self, vw, **kwargs)
