"""
The initial msp430 module.
"""
############
# Author: Don C. Weber
# Started: 05/23/2009
# 

# TODO:
#

import envi

import disasm

class Msp430Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "msp430", maxinst=4)
        self._arch_dis = disasm.Msp430Disasm()

    def archGetRegCtx(self):
        return regs.Msp430RegisterContext()

    def archGetBreakInstr(self):
        return '\xcc'

    def archGetNopInstr(self):
        return '\x90'

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        groups.append(regs.GeneralRegGroup)
        return groups

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        import emu
        return Msp430Emulator()

    def getArchDefaultCall(self):
        return 'msp430call'

