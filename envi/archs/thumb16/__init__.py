
from envi.archs.arm import *

import disasm as th_disasm

class Thumb16Module(ArmModule):

    def __init__(self):
        self._arch_dis = th_disasm.Thumb16Disasm()
        ArmModule.__init__(self, name='thumb16')


class ThumbModule(Thumb16Module):

    def __init__(self):
        self._arch_dis = th_disasm.ThumbDisasm()
        ArmModule.__init__(self, name='thumb')


