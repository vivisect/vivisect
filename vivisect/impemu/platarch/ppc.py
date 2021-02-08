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
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op == None:
            op = envi.Emulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op

        return op

class Ppc32EmbeddedWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_ppc.Ppc32EmbeddedEmulator):

    def __init__(self, vw, logwrite=False, logread=False):
        self.taintregs = [ x for x in range(13) ]
        self.taintregs.append(e_ppc.REG_LR)

        e_ppc.Ppc32EmbeddedEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        # use VivWorkspace's VLE configuration info
        
    def parseOpcode(self, va, arch=envi.ARCH_PPC_E32):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op == None:
            op = envi.Emulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op

        return op




class PpcVleWorkspaceEmulator(Ppc64EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op == None:
            op = self.vw.parseOpcode(va, arch=envi.ARCH_PPCVLE)
            self.opcache[va] = op

        return op

class Ppc64ServerWorkspaceEmulator(Ppc64EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_PPC_S64):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op == None:
            op = self.vw.parseOpcode(va, arch=arch)
            self.opcache[va] = op

        return op
class Ppc32ServerWorkspaceEmulator(Ppc32EmbeddedWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_PPC_S32):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        op = self.opcache.get(va)
        if op == None:
            op = self.vw.parseOpcode(va, arch=arch)
            self.opcache[va] = op

        return op
