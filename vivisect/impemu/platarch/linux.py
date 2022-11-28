import envi.exc as e_exc
import envi.archs.i386 as e_i386
import envi.archs.amd64 as e_amd64

import vivisect.impemu.emulator as v_i_emulator
import vivisect.impemu.platarch.i386 as v_i_i386
import vivisect.impemu.platarch.amd64 as v_i_amd64

from vivisect.impemu.emulator import imphook

class Linuxi386Emulator(v_i_i386.i386WorkspaceEmulator):
    def __init__(self, vw, **kwargs):
        v_i_i386.i386WorkspaceEmulator.__init__(self, vw, **kwargs)

    def i_int(self, op):
        syscall = op.getOperValue(0)
        if syscall != 0x80:
            raise e_exc.BreakpointHit(self)

        reg = self.getRegister(e_i386.REG_EAX)
        if reg == 1:
            self.stopEmu()

class LinuxAmd64Emulator(v_i_amd64.Amd64WorkspaceEmulator):
    def __init__(self, vw, **kwargs):
        v_i_amd64.Amd64WorkspaceEmulator.__init__(self, vw, **kwargs)

    def i_syscall(self, op):
        # TODO: there is a long list of >300 functions we'd need to deal with here
        # some of which would exit
        pass
