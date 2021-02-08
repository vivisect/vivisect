
import envi
import envi.bits as e_bits

import copy
import struct
import traceback

from envi.archs.ppc.regs import *
from envi.archs.ppc.disasm import *
from . import vle

''' taken from the MCP850 ref manual (circa 2001)
3.2.1 Levels of the PowerPC Architecture
The PowerPC architecture is defined in three levels that correspond to three programming
environments, roughly described from the most general, user-level instruction set
environment, to the more specific, operating environment.

This layering of the architecture provides flexibility, allowing degrees of software
compatibility across a wide range of implementations. For example, an implementation
such as an embedded controller may support the user instruction set, whereas it may be
impractical for it to adhere to the memory management, exception, and cache models.

The three levels of the PowerPC architecture are defined as follows:

* PowerPC user instruction set architecture (UISA)-The UISA defines the level of
the architecture to which user-level (referred to as problem state in the architecture
specification) software should conform. The UISA defines the base user-level
instruction set, user-level registers, data types, the exception model as seen by user
programs, and the memory and programming models.

* PowerPC virtual environment architecture (VEA)-The VEA defines additional
user-level functionality that falls outside typical user-level software requirements.
The VEA describes the memory model for an environment in which multiple
devices can access memory, defines aspects of the cache model, defines cache
control instructions, and defines the time base facility from a user-level perspective.
Implementations that conform to the PowerPC VEA also adhere to the UISA, but
may not necessarily adhere to the OEA.

* PowerPC operating environment architecture (OEA)-The OEA defines
supervisor-level (referred to as privileged state in the architecture specification)
resources typically required by an operating system. The OEA defines the PowerPC
memory management model, supervisor-level registers, synchronization
requirements, and the exception model. The OEA also defines the time base feature
from a supervisor-level perspective.

Implementations that conform to the PowerPC OEA also conform to the PowerPC
UISA and VEA.

The MPC850 adheres to the OEA definition of the exception model and provides a
subset of the memory management model. It includes OEA-defined registers and
instructions for configuration and exception handling.

Implementations that adhere to the VEA level are guaranteed to adhere to the UISA level;
likewise, implementations that conform to the OEA level are also guaranteed to conform to
the UISA and the VEA levels. For a more detailed discussion of the characteristics of the
PowerPC architecture, see the Programming Environments Manual.
'''

class Ppc64EmbeddedModule(envi.ArchitectureModule):

    def __init__(self, mode=64, archname='ppc-embedded', endian=envi.ENDIAN_MSB):
        envi.ArchitectureModule.__init__(self, archname, endian=endian)
        self.mode = mode
        self.psize = mode//8
        self.maps = tuple()
        if self.psize == 8:
            self._arch_dis = Ppc64EmbeddedDisasm()
        else:
            self._arch_dis = Ppc32EmbeddedDisasm()
        self._arch_vle_dis = vle.VleDisasm()

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

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
        return self.psize

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        #print offset, hex(va), self.isVle(va), self.maps
        if self.isVle(va):
            #print "isVle"
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

class Ppc32EmbeddedModule(Ppc64EmbeddedModule):
    def __init__(self):
        Ppc64EmbeddedModule.__init__(self, mode=32, archname='ppc32-embedded')


class PpcVleModule(Ppc64EmbeddedModule):
    def __init__(self):
        Ppc64EmbeddedModule.__init__(self, mode=32, archname='ppc-vle')
        self._arch_dis = vle.VleDisasm()
        
    def isVle(self, va):
        return True

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

class Ppc64ServerModule(Ppc64EmbeddedModule):
    def __init__(self, mode=64, archname='ppc-server'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)
        if self.psize == 8:
            self._arch_dis = Ppc64ServerDisasm()
        else:
            self._arch_dis = Ppc32ServerDisasm()
        
    def isVle(self, va):
        return False

    def archParseOpcode(self, bytes, offset=0, va=0):
        return self._arch_dis.disasm(bytes, offset, va)

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

class Ppc32ServerModule(Ppc64ServerModule):
    def __init__(self):
        Ppc64ServerModule.__init__(self, mode=32, archname='ppc32-embedded')

class PpcDesktopModule(Ppc64ServerModule):
    # for now, treat desktop like server
    pass

# NOTE: This one must be after the definition of PpcModule
from envi.archs.ppc.emu import *

