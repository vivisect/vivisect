import unittest

import vivisect
from envi.archs.msp430.regs import *

checks = [
    (
        'NOP',
        { 'regs': [], 'flags': [], 'code': "0343", 'data': "" },
        { 'regs': [], 'flags': [], 'code': "0343", 'data': "" }
    ),
]

class msp430InstructionSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.longMessage=True

        cls.CODE_VA = 0
        cls.DATA_VA = 0x1000

        cls._vw = vivisect.VivWorkspace()
        cls._vw.setMeta('Architecture', 'msp430')
        cls._vw.setMeta('Platform', 'unknown')
        cls._vw.setMeta('Format', 'blob')
        cls._vw.addMemoryMap(cls.CODE_VA, 0x7, 'code', "\x00"*0x100)
        cls._vw.addMemoryMap(cls.DATA_VA, 0x7, 'data', "\x00"*0x100)
        cls._emu = cls._vw.getEmulator()

    def doTest(self, test_name, init_state, final_state):
        # Reset memory
        self._emu.writeMemory(self.CODE_VA, "\x00"*0x100)
        self._emu.writeMemory(self.DATA_VA, "\x00"*0x100)

        # Init registers, status flags and memory
        for reg, val in init_state['regs']:
            self._emu.setRegister(reg, val)

        for flag, state in init_state['flags']:
            self._emu.setFlag(flag, state)

        self._emu.writeMemory(self.CODE_VA, init_state['code'].decode('hex'))
        self._emu.writeMemory(self.DATA_VA, init_state['data'].decode('hex'))

        # Emulate instruction
        op = self._emu.parseOpcode(self.CODE_VA)
        self._emu.executeOpcode(op)

        # Check final state
        for reg, want in final_state['regs']:
            val = self._emu.getRegister(reg)
            self.assertEqual(val, want, test_name + ' - regs')

        for flag, want in final_state['flags']:
            val = self._emu.getFlag(flag)
            self.assertEqual(val, want, test_name + ' - flags')

        want = final_state['code'].decode('hex')
        data = self._emu.readMemory(self.CODE_VA, len(want))
        self.assertEqual(data, want, test_name + ' - code')

        want = final_state['data'].decode('hex')
        data = self._emu.readMemory(self.DATA_VA, len(want))
        self.assertEqual(data, want, test_name + ' - data')

    def test_envi_msp430(self):
        for name, init, final in checks:
            self.doTest(name, init, final)
