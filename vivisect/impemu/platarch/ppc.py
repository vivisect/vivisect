import envi
import envi.archs.ppc as e_ppc
import vivisect.impemu.emulator as v_i_emulator


class PpcWorkspaceEmulator(v_i_emulator.WorkspaceEmulator):

    taintregs = [x for x in range(13)] + [e_ppc.REG_LR]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)


class Ppc64EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)

    def parseOpcode(self, va, arch=envi.ARCH_PPC_E64):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        try:
            return self.opcache[va]
        except KeyError:
            op = e_ppc.Ppc64EmbeddedEmulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
            return op


class Ppc32EmbeddedWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32EmbeddedEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32EmbeddedEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)

    def parseOpcode(self, va, arch=envi.ARCH_PPC_E32):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        try:
            return self.opcache[va]
        except KeyError:
            op = e_ppc.Ppc32EmbeddedEmulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
            return op


class PpcVleWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.PpcVleEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.PpcVleEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)

    def parseOpcode(self, va, arch=envi.ARCH_PPCVLE):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        try:
            return self.opcache[va]
        except KeyError:
            op = e_ppc.PpcVleEmulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
            return op


class Ppc64ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc64ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc64ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)

    def parseOpcode(self, va, arch=envi.ARCH_PPC_S64):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        try:
            return self.opcache[va]
        except KeyError:
            op = e_ppc.Ppc64ServerEmulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
            return op


class Ppc32ServerWorkspaceEmulator(PpcWorkspaceEmulator, e_ppc.Ppc32ServerEmulator):
    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_ppc.Ppc32ServerEmulator.__init__(self)
        PpcWorkspaceEmulator.__init__(self, vw, **kwargs)

    def parseOpcode(self, va, arch=envi.ARCH_PPC_S32):
        # We can make an opcode *faster* with the workspace because of
        # getByteDef etc... use it.
        try:
            return self.opcache[va]
        except KeyError:
            op = e_ppc.Ppc32ServerEmulator.parseOpcode(self, va, arch=arch)
            self.opcache[va] = op
            return op
