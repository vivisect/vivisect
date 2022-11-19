'''
Intel 32-bit Architecture
'''
import envi

from envi.archs.i386.regs import *
from envi.archs.i386.disasm import *

import envi.archs.i386.opconst as opconst

class i386Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'i386')
        self._arch_dis = i386Disasm()

    def initRegGroups(self):
        envi.ArchitectureModule.initRegGroups(self)
        self._regGrps.update({'general': ['eax', 'ecx', 'edx', 'ebx', 'esi', 'edi',
                                'ebp', 'esp', 'eip'] })

    def archModifyOp(self, op, plat):
        # linux-x86 specific. it's a syscall (except in the case of exit...)
        if op.opcode == opconst.INS_TRAP:
            # if we're on linux-i386, this is how they do syscalls, otherwise, it's a trap
            if op.getOperValue(0) == 0x80 and plat != 'linux':
                op.iflags |= opconst.IF_NOFALL

    def archGetRegCtx(self):
        return i386RegisterContext()

    def archGetBreakInstr(self):
        return b'\xcc'

    def archGetNopInstr(self):
        return b'\x90'

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return IntelEmulator()

# NOTE: This one must be after the definition of i386Module
from envi.archs.i386.emu import *
