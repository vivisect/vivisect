import envi.archs.arm.archmod as e_arm
import envi.archs.thumb16.disasm as th_disasm


class Thumb16Module(e_arm.ArmModule):

    def __init__(self):
        self._arch_dis = th_disasm.Thumb16Disasm()
        e_arm.ArmModule.__init__(self, name='thumb16')


class Thumb2Module(Thumb16Module):

    def __init__(self):
        self._arch_dis = th_disasm.Thumb2Disasm()
        e_arm.ArmModule.__init__(self, name='thumb2')
