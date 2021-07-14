import envi
import envi.archs.ppc as e_ppc
import vivisect.impemu.emulator as v_i_emulator

class Ppc64EmbeddedWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_ppc.Ppc64EmbeddedEmulator):

    def __init__(self, vw, logwrite=False, logread=False):
        self.taintregs = [ x for x in range(13) ]
        self.taintregs.append(e_ppc.REG_LR)

        e_ppc.Ppc64EmbeddedEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        # use VivWorkspace's VLE configuration info
        
    def parseOpcode(self, va, arch=envi.ARCH_PPC_E64):
        return self.vw.parseOpcode(va, arch=arch)

class Ppc32EmbeddedWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_ppc.Ppc32EmbeddedEmulator):

    def __init__(self, vw, logwrite=False, logread=False):
        self.taintregs = [ x for x in range(13) ]
        self.taintregs.append(e_ppc.REG_LR)

        e_ppc.Ppc32EmbeddedEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        # use VivWorkspace's VLE configuration info
        
    def parseOpcode(self, va, arch=envi.ARCH_PPC_E32):
        return self.vw.parseOpcode(va, arch=arch)


class PpcVleWorkspaceEmulator(Ppc64EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_PPCVLE):
        return self.vw.parseOpcode(va, arch=arch)

class Ppc64ServerWorkspaceEmulator(Ppc64EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_PPC_S64):
        return self.vw.parseOpcode(va, arch=arch)

class Ppc32ServerWorkspaceEmulator(Ppc32EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_PPC_S32):
        return self.vw.parseOpcode(va, arch=arch)
