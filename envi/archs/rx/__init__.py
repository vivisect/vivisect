"""
rxv2 module
"""
import envi

from envi.archs.rx import regs
from envi.archs.rx import const
from envi.archs.rx import disasm

class RxModule(envi.ArchitectureModule):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "rx", maxinst=4)
        self._arch_dis = disasm.RxDisasm()
        self._regGrps.update({
            'general': [r[0] for r in regs.registers_info],
        })

    def archGetRegCtx(self):
        return regs.RxRegisterContext()

    def archGetNopInstr(self):
        return '\x03'

    def getPointerSize(self):
        return 4

    def pointerString(self, va):
        return '0x{:04x}'.format(va)

    def archParseOpcode(self, bytes, offset=0, va=0, extra=None):
        return self._arch_dis.disasm(bytes, offset, va)

    def getEmulator(self):
        return emu.RxEmulator()

    def getArchDefaultCall(self):
        return 'rxcall'

# NOTE: This one must be after the definition of RxModule
from . import emu
