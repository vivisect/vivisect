import envi.archs.ppc as e_ppc
import vivisect.impemu.emulator as v_i_emulator

class PpcWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_ppc.PpcEmulator):

    def __init__(self, vw, logwrite=False, logread=False):
        self.taintregs = [ x for x in range(13) ]
        self.taintregs.append(e_ppc.REG_LR)

        e_ppc.PpcEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)



