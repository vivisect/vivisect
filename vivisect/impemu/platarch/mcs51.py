import envi.archs.mcs51.emu as e_mcs51
import vivisect.impemu.emulator as v_i_emulator
import envi.archs.mcs51.const as m51const

from envi.const import RMETA_NMASK

non_use_opcodes = (m51const.INS_PUSH, )


class Mcs51WorkspaceEmulator(v_i_emulator.WorkspaceEmulator, e_mcs51.Mcs51Emulator):

    taintregs = [x for x in range(13)]

    def __init__(self, vw, logwrite=False, logread=False):
        e_mcs51.Mcs51Emulator.__init__(self)
        v_i_emulator.WorkspaceEmulator.__init__(self, vw, logwrite=logwrite, logread=logread)

    def getRegister(self, index):
        rval = value = e_mcs51.Mcs51Emulator.getRegister(self, index)

        if self.op is None:
            return value

        ridx = index
        if self.isMetaRegister(index):
            ridx = index & RMETA_NMASK
            # use the value of the real register (not the meta register) for _useVirtAddr
            # but ultimately return the meta register value
            rval = e_mcs51.Mcs51Emulator.getRegister(self, ridx)

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

        # blacklist of opcodes that do *not* indicate a 'use'

        # if first item is a set, then this is *not* an arg(register) use
        # (reg initialization)
        if op.opcode == m51const.INS_XOR and op.opers[0] == op.opers[1]:
            # xor register initialization
            return False

        else:
            # if op opcodes is in blacklist, it's not a use either
            if op.opcode in non_use_opcodes:
                return False

        return True

