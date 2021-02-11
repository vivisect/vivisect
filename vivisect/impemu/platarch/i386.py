import envi.archs.i386 as e_i386
import vivisect.impemu.emulator as v_i_emulator

from envi.const import RMETA_NMASK

non_use_mnems = ('push', )


class i386WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_i386.IntelEmulator):

    taintregs = [
        e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX,
        e_i386.REG_EBX, e_i386.REG_EBP, e_i386.REG_ESI,
        e_i386.REG_EDI,
    ]

    def __init__(self, vw, **kwargs):
        '''
        Please see the base emulator class in vivisect/impemu/emulator.py for the parameters
        that can be passed through kwargs
        '''
        e_i386.IntelEmulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, **kwargs)
        self.setEmuOpt('i386:reponce', True)

    def getRegister(self, index):
        rval = value = e_i386.IntelEmulator.getRegister(self, index)

        if self.op is None:
            return value

        ridx = index
        if self.isMetaRegister(index):
            ridx = index & RMETA_NMASK
            # use the value of the real register (not the meta register) for _useVirtAddr
            # but ultimately return the meta register value
            rval = e_i386.IntelEmulator.getRegister(self, ridx)

        if ridx not in self.taintregs:
            return value

        if self.isRegUse(self.op, ridx):
            self._useVirtAddr(rval)

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
            if op.mnem in non_use_mnems:
                return False

        return True
