"""
The envi architecture module for the AMD 64 platform.
"""

import envi
import envi.archs.amd64.emu as emu
import envi.archs.amd64.regs as regs
import envi.archs.amd64.disasm as disasm
import envi.archs.i386.archmod as e_i386_archmod

# NOTE: The REX prefixes don't end up with displayed names
# NOTE: the REX prefix must be the *last* non escape (0f) prefix

# EMU NOTES:
# In 64 bit mode, all 32 bit dest regs get 0 extended into the rest of the bits
# In 64 bit mode, all 8/16 bit accesses do NOT modify the upper bits
# In 64 bit mode, all near branches, and implicit RSP (push pop) use RIP even w/o REX
# In 64 bit mode, if mod/rm is mod=0 and r/m is 5, it's RIP relative IMM32


class Amd64Module(e_i386_archmod.i386Module):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "amd64")
        self._arch_dis = disasm.Amd64Disasm()

    def archGetRegCtx(self):
        return regs.Amd64RegisterContext()

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)
        general = ('general', ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp',
                               'rsp', 'rip', 'r8', 'r9', 'r10', 'r11', 'r12',
                               'r13', 'r14', 'r15'], )

        groups.append(general)
        return groups

    def getPointerSize(self):
        return 8

    def pointerString(self, va):
        return "0x%.8x" % va

    def getEmulator(self):
        return emu.Amd64Emulator()
