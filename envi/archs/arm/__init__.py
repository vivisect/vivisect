
"""
The initial arm module.
"""

import envi

from envi.archs.arm.regs import *
from envi.archs.arm.disasm import *

class ArmModule(envi.ArchitectureModule):

    def __init__(self, name='ARMv7A'):
        import envi.archs.thumb16.disasm as eatd
        # these are required for setEndian() which is called from ArchitectureModule.__init__()
        self._arch_dis = ArmDisasm()
        self._arch_dis.setArchMask(name)
        self._arch_thumb_dis = eatd.ThumbDisasm()

        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()

        # pre-generate this list
        self.badoplist = [self.archParseOpcode(badop, 0, 0) for badop in self._arch_badopbytes]
        self.badoplist.extend([self.archParseOpcode(badop, 0, 1) for badop in self._arch_badopbytes])

    def archGetRegCtx(self):
        return ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")

    def archGetNopInstr(self):
        return (b'\x00\x00\x60\xe3', b'\xe3\x60\x00\x00')[self._endian]   #FIXME: this is only ARM mode.  this arch mod should cover both.  the ENVI architecture doesn't support this model yet.

    def archGetBadOps(self):
        return self.badoplist

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        if va & 3:
            offset &= -2
            va &= -2

            return self._arch_thumb_dis.disasm(bytes, offset, va)

        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return ArmEmulator()

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)
        self._arch_thumb_dis.setEndian(endian)

    def archModifyFuncAddr(self, va, info):
        if va & 1:
            return va & -2, {'arch' : envi.ARCH_THUMB}
        return va, info

    def archModifyXrefAddr(self, tova, reftype, rflags):
        if tova & 1:
            return tova & -2, reftype, rflags
        return tova, reftype, rflags

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)

        groups.append(('general', arm_regs))

        # compilers use the following regs to stick the module baseaddr in for 
        # switchcase code
        switch_mapbase = ('switch_mapbase', [ 'r0', 'r1', 'r2', 'r3',],)   # FIXME: limited sampleset.  this list could be longer
        groups.append(switch_mapbase)
        return groups

    def archGetPointerAlignment(self):
        return 4


class ThumbModule(envi.ArchitectureModule):
    '''
    This architecture module will *not* shift to ARM mode.  Evar.
    '''

    def __init__(self, name='thumb'):
        import envi.archs.thumb16.disasm as eatd
        # this is required for setEndian() which is called from ArchitectureModule.__init__()
        self._arch_dis = eatd.ThumbDisasm(doModeSwitch=False)

        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()
        #armVersion mask should be set here if needed

        # pre-generating bad-ops list
        self.badoplist = [ self.archParseOpcode(badop,0,0) for badop in self._arch_badopbytes ]
        self.badoplist.extend([ self.archParseOpcode(badop,0,1) for badop in self._arch_badopbytes ])

    def archGetRegCtx(self):
        return ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")

    def archGetNopInstr(self):
        return (b'\xc0\x46', b'\x46\xc0')[self._endian]

    def archGetBadOps(self):
        return self.badoplist

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        va &= -2
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        emu = ArmEmulator()
        emu.setThumbMode()
        return emu

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)

    def archModifyFuncAddr(self, va, info):
        if va & 1:
            return va & -2, {'arch' : envi.ARCH_THUMB}
        return va, info

    def archModifyXrefAddr(self, tova, reftype, rflags):
        if tova & 1:
            return tova & -2, reftype, rflags
        return tova, reftype, rflags

    def archGetPointerAlignment(self):
        return 4


from envi.archs.arm.emu import *
