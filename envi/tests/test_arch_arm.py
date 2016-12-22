import unittest
import imp

class ArmInstructionSet(unittest.TestCase):
    def test_msr(self):
        # test the MSR instruction
        import envi.archs.arm as e_arm;imp.reload(e_arm)
        am=e_arm.ArmModule()
        op = am.archParseOpcode('d3f021e3'.decode('hex'))
        self.assertEqual('msr CPSR_c, #0xd3', repr(op))
