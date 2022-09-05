import unittest
import envi.registers as e_regs
import envi.archs.i386.regs as e_i386_regs


class EnviRegisterTest(unittest.TestCase):
    def test_envi_register_slicing(self):
        # we'll use the good ol' i386 registers for demonstrating metaregister slicing
        rctx = e_i386_regs.i386RegisterContext()
        rctx.setRegisterByName('ecx', 0x47145)                                                                                                                                                                     
        self.assertEqual

        self.assertEqual(rctx.getRegisterByName('ecx'), 0x47145)
        self.assertEqual(rctx.getRegisterByName('cx'), 0x7145)
        self.assertEqual(rctx.getRegisterByName('cl'), 0x45)
        self.assertEqual(rctx.getRegisterByName('ch'), 0x71)

        # write-slicing, oversized data
        rctx.setRegisterByName('ch', 0x47145)   # should chop the upper bits out to the correct size
        self.assertEqual(rctx.getRegisterByName('ecx'), 0x44545)
