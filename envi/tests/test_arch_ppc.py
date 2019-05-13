
import vivisect
import envi.archs.ppc
import unittest

class PpcInstructionSet(unittest.TestCase):
    def getVivEnv(self, arch='ppc'):
        vw = vivisect.VivWorkspace()
        vw.setMeta("Architecture", arch)
        vw.addMemoryMap(0, 7, 'firmware', '\xff' * 16384*1024)
        vw.addMemoryMap(0xbfb00000, 7, 'firmware', '\xfe' * 16384*1024)

        emu = vw.getEmulator()
        emu.setMeta('forrealz', True)
        emu.logread = emu.logwrite = True

        sctx = vs_anal.getSymbolikAnalysisContext(vw)
        return vw, emu, sctx

    def test_envi_ppcvle_disasm(self):
        test_pass = 0

        vw, emu, sctx = self.getVivEnv('vle')
        
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

        vw, emu, sctx = self.getVivEnv('ppc')

        import ppc64_instructions
        for test_bytes, result_instr in ppc64_instructions.instructions:
            op = vw.arch.archParseOpcode(test_bytes.decode('hex'), 0, va)
            op_str = repr(op).strip()
            if op_str == result_instr:
                test_pass += 1
            self.assertEqual(result_instr, op_str, '{}: {} != {}'.format(test_bytes, result_instr, op_str))

        self.assertEqual(test_pass, len(ppc64_instructions.instructions))

    def test_MASK_and_ROTL32(self):
        import envi.archs.ppc.emu as eape
        import vivisect.symboliks.archs.ppc as vsap

        for x in range(64):
            for y in range(64):
                #mask = 
                emumask = eape.MASK(x, y)

                symmask = vsap.MASK(vsap.Const(x, 8), vsap.Const(y, 8))
                #print hex(emumask), repr(symmask), symmask


                self.assertEqual(emumask, symmask.solve(), 'MASK({}, {}): {} != {}'.format(x, y, emumask, symmask.solve()))


