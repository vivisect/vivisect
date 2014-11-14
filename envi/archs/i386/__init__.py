import envi
import envi.bits as e_bits

#TODO
# f0 0f c7 4d 00 75 f0 5d 5b - this is NOT right in disasm

import copy
import struct
import traceback

# Gank in our bundled libdisassemble
import opcode86

from envi.archs.i386.regs import *
from envi.archs.i386.disasm import *

class i386Module(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'i386')
        self._arch_dis = i386Disasm()

    def archGetRegCtx(self):
        return i386RegisterContext()

    def archGetBreakInstr(self):
        return '\xcc'

    def archGetNopInstr(self):
        return '\x90'

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)
        general = ('general', ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi',
                                'ebp', 'esp', 'eip', ], )

        groups.append(general)
        return groups

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

