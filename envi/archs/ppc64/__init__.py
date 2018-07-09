
import envi
import envi.bits as e_bits

import copy
import struct
import traceback

from envi.archs.ppc.regs import *
from envi.archs.ppc.disasm import *

class PpcModule(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'ppc')
        self._arch_dis = PpcDisasm()

    def archGetRegCtx(self):
        return PpcRegisterContext()

    def archGetBreakInstr(self):
        raise Exception("IMPLEMENT ME")
        return '\xcc'

    def archGetNopInstr(self):
        raise Exception("IMPLEMENT ME")
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

# NOTE: This one must be after the definition of PpcModule
from envi.archs.ppc.emu import *

