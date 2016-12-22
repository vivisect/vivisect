from envi.archs.arm import ArmModule

from . import disasm as th_disasm


class Thumb16Module(ArmModule):
    def __init__(self):
        ArmModule.__init__(self, name='thumb16')
        self._arch_dis = th_disasm.Thumb16Disasm()


class Thumb2Module(Thumb16Module):
    def __init__(self):
        ArmModule.__init__(self, name='thumb2')
        self._arch_dis = th_disasm.Thumb2Disasm()
