import binascii
import unittest

import vivisect
from envi.tests.msp430 import iadc, iadd, iaddc, iand, ibic, ibis, ibit, ibr
from envi.tests.msp430 import icall, iclr, iclrc, iclrn, iclrz, icmp, idadc
from envi.tests.msp430 import idadd, idec, idecd, iinc, iincd, iinv, ijumps
from envi.tests.msp430 import imov, inop, ipop, ipush, iret, irla, irlc, irra
from envi.tests.msp430 import irrc, isbc, isetc, isetn, isetz, isub, isubc
from envi.tests.msp430 import iswpb, isxt, itst, ixor

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
        cls._vw.addMemoryMap(0, 0x7, 'mem', b'\x00' * cls.MEMSIZE)
        cls._emu = cls._vw.getEmulator()

    def doTest(self, test_name, init_state, final_state):
        # Reset memory
        self._emu.writeMemory(0, b"\x00" * self.MEMSIZE)

        # Init registers, status flags and memory
        for reg, val in init_state['regs']:
            self._emu.setRegister(reg, val)

        for flag, state in init_state['flags']:
            self._emu.setFlag(flag, state)

        init_code = binascii.unhexlify(init_state['code'])
        init_data = binascii.unhexlify(init_state['data'])

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

        want = binascii.unhexlify(final_state['code'])
        code = self._emu.readMemory(self.CODE_VA, len(want))
        self.assertEqual(code, want, test_name + ' - code')

        want = binascii.unhexlify(final_state['data'])
        data = self._emu.readMemory(self.DATA_VA, len(want))
        self.assertEqual(data, want, test_name + ' - data')

    def iterChecks(self, checks):
        for name, init, final in checks:
            self.doTest(name, init, final)

    def test_envi_msp430_adc(self):
        self.iterChecks(iadc.checks)

    def test_envi_msp430_add(self):
        self.iterChecks(iadd.checks)

    def test_envi_msp430_addc(self):
        self.iterChecks(iaddc.checks)

    def test_envi_msp430_and(self):
        self.iterChecks(iand.checks)

    def test_envi_msp430_bic(self):
        self.iterChecks(ibic.checks)

    def test_envi_msp430_bis(self):
        self.iterChecks(ibis.checks)

    def test_envi_msp430_bit(self):
        self.iterChecks(ibit.checks)

    def test_envi_msp430_br(self):
        self.iterChecks(ibr.checks)

    def test_envi_msp430_call(self):
        self.iterChecks(icall.checks)

    def test_envi_msp430_clr(self):
        self.iterChecks(iclr.checks)

    def test_envi_msp430_clrc(self):
        self.iterChecks(iclrc.checks)

    def test_envi_msp430_clrn(self):
        self.iterChecks(iclrn.checks)

    def test_envi_msp430_clrz(self):
        self.iterChecks(iclrz.checks)

    def test_envi_msp430_cmp(self):
        self.iterChecks(icmp.checks)

    def test_envi_msp430_dadc(self):
        self.iterChecks(idadc.checks)

    def test_envi_msp430_dadd(self):
        self.iterChecks(idadd.checks)

    def test_envi_msp430_dec(self):
        self.iterChecks(idec.checks)

    def test_envi_msp430_decd(self):
        self.iterChecks(idecd.checks)

    def test_envi_msp430_dint(self):
        # Not implemented
        pass

    def test_envi_msp430_eint(self):
        # Not implemented
        pass

    def test_envi_msp430_inc(self):
        self.iterChecks(iinc.checks)

    def test_envi_msp430_incd(self):
        self.iterChecks(iincd.checks)

    def test_envi_msp430_inv(self):
        self.iterChecks(iinv.checks)

    def test_envi_msp430_jumps(self):
        self.iterChecks(ijumps.checks)

    def test_envi_msp430_mov(self):
        self.iterChecks(imov.checks)

    def test_envi_msp430_nop(self):
        self.iterChecks(inop.checks)

    def test_envi_msp430_pop(self):
        self.iterChecks(ipop.checks)

    def test_envi_msp430_push(self):
        self.iterChecks(ipush.checks)

    def test_envi_msp430_ret(self):
        self.iterChecks(iret.checks)

    def test_envi_msp430_reti(self):
        # Not implemented
        pass

    def test_envi_msp430_rla(self):
        self.iterChecks(irla.checks)

    def test_envi_msp430_rlc(self):
        self.iterChecks(irlc.checks)

    def test_envi_msp430_rra(self):
        self.iterChecks(irra.checks)

    def test_envi_msp430_rrc(self):
        self.iterChecks(irrc.checks)

    def test_envi_msp430_sbc(self):
        self.iterChecks(isbc.checks)

    def test_envi_msp430_setc(self):
        self.iterChecks(isetc.checks)

    def test_envi_msp430_setn(self):
        self.iterChecks(isetn.checks)

    def test_envi_msp430_setz(self):
        self.iterChecks(isetz.checks)

    def test_envi_msp430_sub(self):
        self.iterChecks(isub.checks)

    def test_envi_msp430_subc(self):
        self.iterChecks(isubc.checks)

    def test_envi_msp430_swpb(self):
        self.iterChecks(iswpb.checks)

    def test_envi_msp430_sxt(self):
        self.iterChecks(isxt.checks)

    def test_envi_msp430_tst(self):
        self.iterChecks(itst.checks)

    def test_envi_msp430_xor(self):
        self.iterChecks(ixor.checks)
