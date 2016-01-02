import unittest

import vivisect
from envi.tests.msp430 import iadc, iadd, iaddc, iand, ibic, ibis, ibit, ibr
from envi.tests.msp430 import icall, iclr, iclrc, iclrn, iclrz, icmp, idadc
from envi.tests.msp430 import idadd, idec, idecd, iinc

class msp430InstructionSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.longMessage=True

        cls.CODE_VA = 0x4400
        cls.DATA_VA = 0x1000
        cls.MEMSIZE = 0xffff

        cls._vw = vivisect.VivWorkspace()
        cls._vw.setMeta('Architecture', 'msp430')
        cls._vw.setMeta('Platform', 'unknown')
        cls._vw.setMeta('Format', 'blob')
        cls._vw.addMemoryMap(0, 0x7, 'mem', "\x00"*cls.MEMSIZE)
        cls._emu = cls._vw.getEmulator()

    def doTest(self, test_name, init_state, final_state):
        # Reset memory
        self._emu.writeMemory(0, "\x00"*self.MEMSIZE)

        # Init registers, status flags and memory
        for reg, val in init_state['regs']:
            self._emu.setRegister(reg, val)

        for flag, state in init_state['flags']:
            self._emu.setFlag(flag, state)

        init_code = init_state['code'].decode('hex')
        init_data = init_state['data'].decode('hex')

        self._emu.writeMemory(self.CODE_VA, init_code)
        self._emu.writeMemory(self.DATA_VA, init_data)

        # Emulate instruction
        self._emu.setProgramCounter(self.CODE_VA)
        op = self._vw.arch.archParseOpcode(init_code, 0, self.CODE_VA)
        self._emu.executeOpcode(op)

        # Check final state
        for reg, want in final_state['regs']:
            val = self._emu.getRegister(reg)
            self.assertEqual(val, want, '{} - regs ({})'.format(test_name, reg))

        for flag, want in final_state['flags']:
            val = self._emu.getFlag(flag)
            self.assertEqual(val, want, '{} - flags ({})'.format(test_name, flag))

        want = final_state['code'].decode('hex')
        code = self._emu.readMemory(self.CODE_VA, len(want))
        self.assertEqual(code, want, test_name + ' - code')

        want = final_state['data'].decode('hex')
        data = self._emu.readMemory(self.DATA_VA, len(want))
        self.assertEqual(data, want, test_name + ' - data')

    def test_envi_msp430_adc(self):
        for name, init, final in iadc.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_add(self):
        for name, init, final in iadd.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_addc(self):
        for name, init, final in iaddc.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_and(self):
        for name, init, final in iand.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_bic(self):
        for name, init, final in ibic.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_bis(self):
        for name, init, final in ibis.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_bit(self):
        for name, init, final in ibit.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_br(self):
        for name, init, final in ibr.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_call(self):
        for name, init, final in icall.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_clr(self):
        for name, init, final in iclr.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_clrc(self):
        for name, init, final in iclrc.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_clrn(self):
        for name, init, final in iclrn.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_clrz(self):
        for name, init, final in iclrz.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_cmp(self):
        for name, init, final in icmp.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_dadc(self):
        for name, init, final in idadc.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_dadd(self):
        for name, init, final in idadd.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_dec(self):
        for name, init, final in idec.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_decd(self):
        for name, init, final in idecd.checks:
            self.doTest(name, init, final)

    def test_envi_msp430_dint(self):
        # Not implemented
        pass

    def test_envi_msp430_eint(self):
        # Not implemented
        pass

    def test_envi_msp430_inc(self):
        for name, init, final in iinc.checks:
            self.doTest(name, init, final)
