import envi
import envi.archs.ppc as e_ppc
import vivisect.impemu.emulator as v_i_emulator

class PpcWorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_ppc.PpcEmulator):

    def __init__(self, vw, logwrite=False, logread=False):
        self.taintregs = [ x for x in range(13) ]
        self.taintregs.append(e_ppc.REG_LR)

        e_ppc.PpcEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)
        
        # use VivWorkspace's VLE configuration info
        
    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
	# We can make an opcode *faster* with the workspace because of
	# getByteDef etc... use it.
	op = self.opcache.get(va)
	if op == None:
	    op = envi.Emulator.parseOpcode(self, va, arch=arch)
	    self.opcache[va] = op

	return op





class VleWorkspaceEmulator(PpcWorkspaceEmulator):
    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
	# We can make an opcode *faster* with the workspace because of
	# getByteDef etc... use it.
	op = self.opcache.get(va)
	if op == None:
	    op = self.vw.parseOpcode(va, arch=envi.ARCH_VLE)
	    self.opcache[va] = op

	return op
