import logging

import envi.archs.amd64 as e_amd64
import vivisect.impemu.emulator as v_i_emulator

logger = logging.getLogger(__name__)
########################################################################
#
# NOTE: For each architecture we intend to do workspace emulation on,
#       extend an emulator to allow any of the needed tweaks (rep prefix
#       etc).
# NOTE: ARCH UPDATE

logger = logging.getLogger(__name__)
non_use_mnems = ('push', )


class Amd64WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_amd64.Amd64Emulator):

    taintregs = [
        e_amd64.REG_RAX, e_amd64.REG_RCX, e_amd64.REG_RDX,
        e_amd64.REG_RBX, e_amd64.REG_RBP, e_amd64.REG_RSI,
        e_amd64.REG_RDI, e_amd64.REG_R8,  e_amd64.REG_R9,
    ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_amd64.Amd64Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setEmuOpt('i386:reponce', True)

    def getRegister(self, index):
        """
        Return the current value of the specified register index.
        """
        value = e_amd64.Amd64Emulator.getRegister(self, index)

        if self.op is None:
            return value

        # this is broken, but works enough to keep for now.  if we
        # run into new 64-bit calling conventions, we may need to fix
        # this.
        if index not in self.taintregs:
            return value

        if self.isRegUse(self.op, index):
            self._useVirtAddr(value)
        return value

    def isRegUse(self, op, ridx):
        '''
        determines if the sequence of uses(get/setRegister) is a register 'use'.
        '''
        # conditions that indicate 'usage':
        # * 'normal usage'
        #   read from a register with *no* previous writes/sets to that register

        # conditions that do *not* indicate 'usage':
        # * 'register initialization', ie xor rax, rax, mov rax, 0, etc
        # * 'save/restore of register', ie push/pop

        # blacklist of mnems that do *not* indicate a 'use'

        # if first item is a set, then this is *not* an arg(register) use
        # (reg initialization)
        if op.mnem == 'xor' and op.opers[0] == op.opers[1]:
            # xor register initialization
            return False

        else:
            # if op mnem is in blacklist, it's not a use either
            for nonuse_mnem in non_use_mnems:
                if nonuse_mnem in repr(op):
                    return False

        return True
