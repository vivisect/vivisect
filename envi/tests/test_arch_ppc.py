
import vivisect
import envi.archs.ppc
import unittest

class PpcInstructionSet(unittest.TestCase):
    def test_envi_ppcvle_disasm(self):
        test_pass = 0

        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "vle")
        va = 0x00000000
        vw.addMemoryMap(va, 7, 'firmware', '\xff' * 16384*1024)

        import ppc_vle_instructions
        for test_bytes, result_instr in ppc_vle_instructions.instructions:
            op = vw.arch.archParseOpcode(test_bytes.decode('hex'), 0, va)
            op_str = repr(op).strip()
            if op_str == result_instr:
                test_pass += 1
            self.assertEqual(result_instr, op_str, '{}: {} != {}'.format(test_bytes, result_instr, op_str))

        self.assertEqual(test_pass, len(ppc_vle_instructions.instructions))

    def test_envi_ppc64_disasm(self):
        test_pass = 0

        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", "ppc")
        va = 0x00000000
        vw.addMemoryMap(va, 7, 'firmware', '\xff' * 16384*1024)

        import ppc64_instructions
        for test_bytes, result_instr in ppc64_instructions.instructions:
            op = vw.arch.archParseOpcode(test_bytes.decode('hex'), 0, va)
            op_str = repr(op).strip()
            if op_str == result_instr:
                test_pass += 1
            self.assertEqual(result_instr, op_str, '{}: {} != {}'.format(test_bytes, result_instr, op_str))

        self.assertEqual(test_pass, len(ppc64_instructions.instructions))
