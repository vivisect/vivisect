"""
The initial arm module.
"""

import envi
import envi.archs.arm.emu as e_arm_emu
import envi.archs.arm.regs as e_arm_regs
import envi.archs.arm.disasm as e_arm_disasm


class ArmModule(envi.ArchitectureModule):

    def __init__(self, name='armv6'):
        import envi.archs.thumb16.disasm as eatd
        # these are required for setEndian() which is called from ArchitectureModule.__init__()
        self._arch_dis = e_arm_disasm.ArmDisasm()
        self._arch_thumb_dis = eatd.Thumb2Disasm()

        envi.ArchitectureModule.__init__(self, name, maxinst=4)
        self._arch_reg = self.archGetRegCtx()

    def archGetRegCtx(self):
        return e_arm_regs.ArmRegisterContext()

    def archGetBreakInstr(self):
        raise Exception("weird... what are you trying to do here?  ARM has a complex breakpoint instruction")

    def archGetNopInstr(self):
        return '\x00'

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return "0x%.8x" % va

    def archParseOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        if va & 3:
            return self._arch_thumb_dis.disasm(bytes, offset, va)

        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return e_arm_emu.ArmEmulator()

    def setEndian(self, endian):
        self._endian = endian
        self._arch_dis.setEndian(endian)
        self._arch_thumb_dis.setEndian(endian)

    def archModifyFuncAddr(self, va, info):
        if va & 1:
            return va & -2, {'arch': envi.ARCH_THUMB2}
        return va, {}

    def archModifyXrefAddr(self, tova, reftype, rflags):
        if tova & 1:
            return tova & -2, reftype, rflags
        return tova, reftype, rflags
