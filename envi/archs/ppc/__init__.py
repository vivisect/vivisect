
from __future__ import annotations
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


def _getLSBSet(value):
    # turn into a binary string and then remove the leading 0b
    binvalstr = bin(value)[2:]
    for i, c in zip(range(len(binvalstr)), reversed(binvalstr)):
        if c == '1':
            return i
    return None


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

        # used to store VLE information
        # Default the alignment (page size) to be the entire valid memory range
        self._page_size = 2 ** mode
        self._page_mask = 0
        self._vle_pages = {}

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

    def archGetBreakInstr(self):
        return '\x7f\xe0\x00\x08'   # this is incorrect for VLE

    def archGetNopInstr(self):
        return '\x60\x00\x00\x00'   # this is incorrect for VLE

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        general = ('general', general_regs)  # from regs.py
        groups.append(general)

        return groups

    def getPointerSize(self):
        return self.psize

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytez, offset=0, va=0):
        if self.isVle(va):
            return self._arch_vle_dis.disasm(bytez, offset, va)

        return self._arch_dis.disasm(bytez, offset, va)

    def getEmulator(self):
        return Ppc64EmbeddedEmulator()

    def setVleMaps(self, maps):
        '''
        takes a list/tuple of (baseaddr, size) to indicate VLE addresses.
        VLE is typically handled by the architecture per-page.  This method
        allows larger groups of memory to be flagged as VLE all at once.
        eg:
            ( (0x00004000, 0x00001000), (0x00005000, 0x00001000), )

        could easily also be written as:
            ( (0x00004000, 0x00002000), )
        '''
        # TODO: squash adjacent mapped regions where possible.

        # Use the mapped VLE addresses and sizes to determine a common page size
        lowest_set_lsbs = [self._page_size]
        lowest_set_lsbs += [_getLSBSet(addr) for addr, _ in maps]
        lowest_set_lsbs += [_getLSBSet(size) for _, size in maps]
        lsb = min(lowest_set_lsbs)

        # The LSB indicates the lowest bit position that can uniquely identify
        # each page, calculate a page size from that
        self._page_size = 1 << lsb

        # Get the original page address and size from the existing VLE maps.
        cur_maps = [entry for entry in self._vle_pages.values() if entry is not None]

        # Now merge the two lists and turn them into individual page entries and
        # create the new maps
        for addr, size in cur_maps + maps:
            # Add the original page address and size to the "root" entry, any
            # extra entries that must be created due to the common page size
            # will be set to None
            self._vle_pages[addr] = (addr, size)

            # Start at the next page
            for page_addr in range(addr+self._page_size, size, self._page_size):
                self._vle_pages[page_addr ] = None

        # Lastly re-calculate the page mask
        self._page_mask = e_bits.b_masks[self.getPointerSize() * 8] & ~e_bits.b_masks[lsb]

    def isVle(self, va):
        return bool(self._vle_pages.get(va & self._page_mask, False))

class Ppc32EmbeddedModule(Ppc64EmbeddedModule):
    def __init__(self, mode=32, archname='ppc32-embedded'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)

    def getEmulator(self):
        return Ppc32EmbeddedEmulator()

class PpcVleModule(Ppc32EmbeddedModule):
    def __init__(self, mode=32, archname='ppc-vle'):
        Ppc32EmbeddedModule.__init__(self, mode=mode, archname=archname)
        self._arch_dis = vle.VleDisasm()

    def isVle(self, va):
        return True

    def archParseOpcode(self, bytez, offset=0, va=0):
        return self._arch_dis.disasm(bytez, offset, va)

    def archGetBreakInstr(self):
        return '\x7f\xe0\x00\x08'   # this is incorrect for VLE

    def archGetNopInstr(self):
        return '\x60\x00\x00\x00'   # this is incorrect for VLE

    def getEmulator(self):
        return PpcVleEmulator()

class Ppc64ServerModule(Ppc64EmbeddedModule):
    def __init__(self, mode=64, archname='ppc-server'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)
        if self.psize == 8:
            self._arch_dis = Ppc64ServerDisasm()
        else:
            self._arch_dis = Ppc32ServerDisasm()

    def isVle(self, va):
        return False

    def archParseOpcode(self, bytez, offset=0, va=0):
        return self._arch_dis.disasm(bytez, offset, va)

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

    def getEmulator(self):
        return Ppc64ServerEmulator()

class Ppc32ServerModule(Ppc64ServerModule):
    def __init__(self, mode=32, archname='ppc32-server'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)

    def getEmulator(self):
        return Ppc32ServerEmulator()

class PpcDesktopModule(Ppc64ServerModule):
    # for now, treat desktop like server
    pass

# NOTE: This one must be after the definition of PpcModule
from envi.archs.ppc.emu import *

