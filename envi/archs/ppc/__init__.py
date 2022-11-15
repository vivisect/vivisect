
from __future__ import annotations
import envi
import envi.bits as e_bits
import envi.const as e_const

import copy
import struct
import traceback

import envi.archs.ppc.regs as eapr
import envi.archs.ppc.disasm as eapd
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
    binvalstr = format(value, 'b')
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
            self._arch_dis = eapd.Ppc64EmbeddedDisasm()
        else:
            self._arch_dis = eapd.Ppc32EmbeddedDisasm()
        self._arch_vle_dis = vle.VleDisasm()

        # used to store VLE information
        # Default the alignment (page size) to the default envi PAGE_SIZE
        self._page_size = e_const.PAGE_SIZE
        self._page_mask = 0
        self._vle_pages = {}

    def getPpcVleInfoSnap(self):
        snap = self._page_size, self._page_mask, self._vle_pages
        return snap

    def setPpcVleInfoSnap(self, snap):
        self._page_size, self._page_mask, self._vle_pages = snap

    def getEmuSnap(self):
        """
        Return the data needed to "snapshot" this emulator.  For PPC we need to
        include the PPC VLE memory map info here.
        """
        regs = self.getRegisterSnap()
        mem = self.getMemorySnap()
        vleinfo = self.getPpcVleInfoSnap()
        return regs,mem,vleinfo

    def setEmuSnap(self, snap):
        regs,mem,vleinfo = snap
        self.setRegisterSnap(regs)
        self.setMemorySnap(mem)
        self.setPpcVleInfoSnap(vleinfo)

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

    def archGetBreakInstr(self):
        # BOOKE:        dnh     4C00018C
        # VLE 32bit:    e_dnh   7C0000C2
        # VLE 16bit:    se_dnh  000F
        return '\x4C\x00\x01\x8C'

    def archGetNopInstr(self):
        # BOOKE:        nop (ori 0,0,0)     60000000
        # VLE 32bit:    e_nop (e_ori 0,0,0) 1800D000
        # VLE 16bit:    se_nop (se_or 0,0)  4400
        return '\x60\x00\x00\x00'

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        groups['general'] = regs_general
        groups['altivec'] = regs_altivec
        groups['fpu'] = regs_fpu
        groups['spe'] = regs_spe
        groups['spr'] = regs_spr
        groups['vsx'] = regs_vsx

        return groups

    def getPointerSize(self):
        return self.psize

    def pointerString(self, va):
        return '0x%.8x' % va

    def archParseOpcode(self, bytez, offset=0, va=0, extra=None):
        if self.isVle(va):
            return self._arch_vle_dis.disasm(bytez, offset, va)

        return self._arch_dis.disasm(bytez, offset, va)

    def getEmulator(self):
        emu = Ppc64EmbeddedEmulator()
        vleinfo = self.getPpcVleInfoSnap()
        emu.setPpcVleInfoSnap(vleinfo)
        return emu

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
        # Handle a few different map input styles
        if isinstance(maps, dict):
            vlemaps = [e[:2] for e in maps.values() if (len(e) == 2) or (len(e) == 3 and e[2])]
        else:
            vlemaps = [e[:2] for e in maps if (len(e) == 2) or (len(e) == 3 and e[2])]

        # Use the mapped VLE addresses and sizes to determine a common page size
        lowest_set_lsbs = [_getLSBSet(self._page_size)] + \
                [_getLSBSet(addr) for addr, _ in vlemaps] + \
                [_getLSBSet(size) for _, size in vlemaps]
        lsb = min(lowest_set_lsbs)

        # The LSB indicates the lowest bit position that can uniquely identify
        # each page, calculate a page size from that
        self._page_size = 1 << lsb

        for addr, size in vlemaps:
            # Add the original page address and size to the "root" entry, any
            # extra entries that must be created due to the common page size
            # will be set to None
            self._vle_pages[addr] = (addr, size)

            # Start at the next page
            for page_addr in range(addr+self._page_size, addr+size, self._page_size):
                self._vle_pages[page_addr ] = None

        # Lastly re-calculate the page mask
        self._page_mask = e_bits.b_masks[self.getPointerSize() * 8] & ~e_bits.b_masks[lsb]

    def isVle(self, va):
        page_base_addr = va & self._page_mask
        return page_base_addr in self._vle_pages

    def archModifyFuncAddr(self, va, info):
        if self.isVle(va):
            return va, {'arch' : envi.ARCH_PPCVLE}
        return va, info

    def archModifyXrefAddr(self, tova, reftype, rflags):
        # The ref type and flags do not need to change regardless of if tova is
        # in a VLE page or not
        return tova, reftype, rflags


class Ppc32EmbeddedModule(Ppc64EmbeddedModule):
    def __init__(self, mode=32, archname='ppc32-embedded'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)

    def getEmulator(self):
        emu = Ppc32EmbeddedEmulator()
        vleinfo = self.getPpcVleInfoSnap()
        emu.setPpcVleInfoSnap(vleinfo)
        return emu

class PpcVleModule(Ppc32EmbeddedModule):
    def __init__(self, mode=32, archname='ppc-vle'):
        Ppc32EmbeddedModule.__init__(self, mode=mode, archname=archname)
        self._arch_dis = vle.VleDisasm()

    def isVle(self, va):
        return True

    def archParseOpcode(self, bytez, offset=0, va=0, extra=None):
        return self._arch_dis.disasm(bytez, offset, va)

    def archGetBreakInstr(self):
        # BOOKE:        dnh     4C00018C
        # VLE 32bit:    e_dnh   7C0000C2
        # VLE 16bit:    se_dnh  000F
        return '\x7C\x00\x00\xC2'

    def archGetNopInstr(self):
        # BOOKE:        nop (ori 0,0,0)     60000000
        # VLE 32bit:    e_nop (e_ori 0,0,0) 1800D000
        # VLE 16bit:    se_nop (se_or 0,0)  4400
        return '\x44\x00'

    def getEmulator(self):
        emu = PpcVleEmulator()
        vleinfo = self.getPpcVleInfoSnap()
        emu.setPpcVleInfoSnap(vleinfo)
        return emu

class Ppc64ServerModule(Ppc64EmbeddedModule):
    def __init__(self, mode=64, archname='ppc-server'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)
        if self.psize == 8:
            self._arch_dis = eapd.Ppc64ServerDisasm()
        else:
            self._arch_dis = eapd.Ppc32ServerDisasm()

    def isVle(self, va):
        return False

    def archParseOpcode(self, bytez, offset=0, va=0, extra=None):
        return self._arch_dis.disasm(bytez, offset, va)

    def archGetRegCtx(self):
        return Ppc64RegisterContext()

    def getEmulator(self):
        emu = Ppc64ServerEmulator()
        vleinfo = self.getPpcVleInfoSnap()
        emu.setPpcVleInfoSnap(vleinfo)
        return emu

class Ppc32ServerModule(Ppc64ServerModule):
    def __init__(self, mode=32, archname='ppc32-server'):
        Ppc64EmbeddedModule.__init__(self, mode=mode, archname=archname)

    def getEmulator(self):
        emu = Ppc32ServerEmulator()
        vleinfo = self.getPpcVleInfoSnap()
        emu.setPpcVleInfoSnap(vleinfo)
        return emu

class PpcDesktopModule(Ppc64ServerModule):
    # for now, treat desktop like server
    pass

# NOTE: This one must be after the definition of PpcModule
from envi.archs.ppc.emu import *

