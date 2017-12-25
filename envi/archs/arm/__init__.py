
"""
The initial arm module.


FIXME:
    00000000:0x00002494  f001ec3a         blx sub_00003d0c    ;sub_00003d0c()
    00000000:0x00002498  f001ec44         blx sub_00003d24    ;UnknownApi()     ** Why doesn't this go?

    Make infinite loop VASET

    00000000:0x00002b64  fafffe4a         blx loc_00002495    ;UnknownApi()     ** Why doesn't this go?
    00000000:0x00002b68  00    ;Emu Anomaly: InvalidInstruction("extra_load_store: invalid Rt argument 'f7ff0800' at 0x2b70",)


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

    def archGetRegCtx(self):
        return ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")
        return

    def archGetNopInstr(self):
        return '\x00'

    def archGetBadOps(self):
        oplist = [ self.archParseOpcode(badop,0,0) for badop in self._arch_badopbytes ]
        oplist.extend([ self.archParseOpcode(badop,0,1) for badop in self._arch_badopbytes ])
        return oplist
 
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
        return va, {}

    def archModifyXrefAddr(self, tova, reftype, rflags):
        if tova & 1:
            return tova & -2, reftype, rflags
        return tova, reftype, rflags

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
        
    def archGetRegCtx(self):
        return ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception ("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")
        return

    def archGetNopInstr(self):
        return '\x00'
 
    def archGetBadOps(self):
        oplist = [ self.archParseOpcode(badop,0,0) for badop in self._arch_badopbytes ]
        oplist.extend([ self.archParseOpcode(badop,0,1) for badop in self._arch_badopbytes ])
        return oplist

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
        return ArmEmulator()

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)

    def archModifyFuncAddr(self, va, info):
        if va & 1:
            return va & -2, {'arch' : envi.ARCH_THUMB}
        return va, {}

    def archModifyXrefAddr(self, tova, reftype, rflags):
        if tova & 1:
            return tova & -2, reftype, rflags
        return tova, reftype, rflags


from envi.archs.arm.emu import *
