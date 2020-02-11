
from envi.archs.arm import *

import envi.archs.thumb16.disasm as th_disasm


class Thumb16Module(ArmModule):

    def __init__(self):
        self._arch_dis = th_disasm.Thumb16Disasm()
        ArmModule.__init__(self, name='thumb16')


class Thumb2Module(Thumb16Module):

    def __init__(self):
        self._arch_dis = th_disasm.Thumb2Disasm()
        ArmModule.__init__(self, name='thumb2')
