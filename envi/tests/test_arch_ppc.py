import sys
import unittest
import vivisect
import envi.archs.ppc
import vivisect.symboliks.analysis as vs_anal

MARGIN_OF_ERROR = 200

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
            try:
                op = vw.arch.archParseOpcode(test_bytes.decode('hex'), 0)
                op_str = repr(op).strip()
                if op_str == result_instr:
                    test_pass += 1
                if result_instr != op_str:
                    print ('{}: ours: {} != {}'.format(test_bytes, op_str, result_instr))
            except Exception, e:
                print ('ERROR: {}: {}'.format(test_bytes, result_instr))
                sys.excepthook(*sys.exc_info())

        print "test_envi_ppcvle_disasm: %d of %d successes" % (test_pass, len(ppc_vle_instructions.instructions))
        self.assertAlmostEqual(test_pass, len(ppc_vle_instructions.instructions), delta=MARGIN_OF_ERROR)

    def test_envi_ppc64_disasm(self):
        test_pass = 0

        vw, emu, sctx = self.getVivEnv('ppc64')

        import ppc64_instructions
        for test_bytes, result_instr in ppc64_instructions.instructions:
            try:
                op = vw.arch.archParseOpcode(test_bytes.decode('hex'), 0)
                op_str = repr(op).strip()
                if op_str == result_instr:
                    test_pass += 1
                if result_instr != op_str:
                    print ('{}: ours: {} != {}'.format(test_bytes, op_str, result_instr))
            except Exception, e:
                print ('ERROR: {}: {}'.format(test_bytes, result_instr))
                sys.excepthook(*sys.exc_info())

        print "test_envi_ppc64_disasm: %d of %d successes" % (test_pass, len(ppc64_instructions.instructions))
        self.assertAlmostEqual(test_pass, len(ppc64_instructions.instructions), delta=MARGIN_OF_ERROR)

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

        for y in range(32):
            emurot32 = eape.ROTL32(0x31337040, y)
            symrot32 = vsap.ROTL32(vsap.Const(0x31337040, 8), vsap.Const(y, 8))
            self.assertEqual(emurot32, symrot32.solve(), 'ROTL32(0x31337040, {}): {} != {}   {}'.format(y, hex(emurot32), hex(symrot32.solve()), symrot32))

        for y in range(64):
            emurot64 = eape.ROTL64(0x31337040, y)
            symrot64 = vsap.ROTL64(vsap.Const(0x31337040, 8), vsap.Const(y, 8))
            self.assertEqual(emurot64, symrot64.solve(), 'ROTL64(0x31337040, {}): {} != {}   {}'.format(y, hex(emurot64), hex(symrot64.solve()), symrot64))

