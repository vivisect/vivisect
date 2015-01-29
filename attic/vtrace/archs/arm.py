import envi.archs.arm as e_arm

class ArmMixin(e_arm.ArmModule, e_arm.ArmRegisterContext):

    def __init__(self):
        e_arm.ArmModule.__init__(self)
        e_arm.ArmRegisterContext.__init__(self)

    def archGetStackTrace(self):
        pc = self.getProgramCounter()
        sp = self.getStackCounter()
        return [ (pc,sp), ]
