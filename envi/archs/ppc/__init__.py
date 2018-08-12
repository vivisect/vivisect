
import envi
import envi.bits as e_bits

import copy
import struct
import traceback

from envi.archs.ppc.regs import *
from envi.archs.ppc.disasm import *
import vle


class PpcModule(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'ppc')
        self.maps = tuple()
        self._arch_dis = PpcDisasm()
        self._arch_vle_dis = vle.VleDisasm()

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
        
        general = ('general', general_regs)  # from regs.py
        groups.append(general)
        
        return groups

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        #print offset, hex(va), self.isVle(va), self.maps
        if self.isVle(va):
            print "isVle"
            return self._arch_vle_dis.disasm(bytes, offset, va)

        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return IntelEmulator()

    def setVleMaps(self, maps):
        '''
        takes a list/tuple of (baseaddr, inverse_mask) to indicate VLE addresses.
        VLE is typically handled by the architecture per-page.  this method allows larger groups of memory to be flagged as VLE all at once.
        eg:
            ( (0x00004000, 0xfffff000), (0x00005000, 0xfffff000), )

                could easily also be written as:

            ( (0x00004000, 0xffffe000), )

        '''
        self.maps = maps

    def isVle(self, va):
        for bva, mask in self.maps:
            if (va & mask) == bva:
                return True
        return False

class VleModule(PpcModule):
    def __init__(self):
        envi.ArchitectureModule.__init__(self, 'vle')
        self._arch_dis = vle.VleDisasm()
        
    def isVle(self, va):
        return True

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

# NOTE: This one must be after the definition of PpcModule
from envi.archs.ppc.emu import *

