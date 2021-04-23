'''
One day we might replace this/add to this with a side by side lockstepper with some other emulator,
but for now, this is both faster to make and vastly more self-contained (which is nice)
'''
import binascii
import unittest

import envi

'''
Tuples are (Opcode Bytes, Register Setup, Stack Setup, Postconditions)
Where:
* Opcode Bytes
    * Bytes making up the instrucion
* Register Setup
    * Prepopulate register with specific values before running the instruction tests
      running the emulator
* Stack Setup
    * Any values that should be pushed onto the stack.
      Keyed by offset from esp.
* Post Registers
    * The assertions on registers memory once the emulator has been run.
      Keyed by register name.
* Post Stack
    * The assertions on registers/stack memory once the emulator has been run.
      Keyed by offset from esp.

Leave Register Setup and/or Stack Setup to take the defaults
'''

DEFREG = 0x00BADB1D
STACKBASE = 0x80

i386Tests = [
    # mov ebx, 47
    ('bb2f000000', {}, {}, {'ebx': 47}, {}),
    # bsr ecx, edx
    ('0FBDCA', {'ecx': 0x47}, {}, {'ecx': 23}, {}),
    # push word [esp+2]
    ('66ff742402', {}, {0: b'\xCD\xFE\x89\x43'}, {'esp': STACKBASE-2}, {0: b'\x89\x43'}),
    # push [esp]
    ('FF3424', {}, {0: b'\x01\x02\x03\x04'}, {'esp': STACKBASE-4}, {4: b'\x01\x02\x03\x04'}),
    # add byte [ecx],al
    ('0001', {'ecx': 0x80, 'eax': 57}, {0: b'\x15\x00\x00\x00'}, {}, {0: b'\x4e\x00\x00\x00'}),
    # sub edx, ecx
    ('29ca', {'edx': 0xf9e7cd45, 'ecx': 0xbfcdef00}, {}, {'edx': 0x3a19de45}, {}),
    # mul edx
    ('f7e2', {'eax': 0x47b3, 'edx': 0x898937}, {}, {'eax': 0x85393275, 'edx': 0x26}, {}),
    # div ax
    ('66f7f0', {'eax': 48, 'edx': 1}, {}, {'eax': 1366, 'edx': 16}, {}),
]


class IntelEmulatorTests(unittest.TestCase):
    def setEmuDefaults(self, emu):
        for name in emu.getRegisterNames():
            emu.setRegisterByName(name, DEFREG)
        emu.addMemoryMap(0, 6, "[stack]", b'\xAB' * 0x100)
        emu.setStackCounter(STACKBASE)
        emu.setRegisterByname('eflags', 0)

    def run_emulator_tests(self, arch, tests):
        emu = arch.getEmulator()
        self.setEmuDefaults(emu)
        for opbytes, sreg, sstack, preg, pstack in tests:
            try:
                op = arch.archParseOpcode(binascii.unhexlify(opbytes), 0, 0x40)
            except envi.InvalidInstruction:
                self.fail('Failed to parse opcode bytes: %s' % opbytes)

            with emu.snap():
                # do the required setup
                for name, valu in sreg.items():
                    emu.setRegisterByName(name, valu)

                for offset, valu in sstack.items():
                    sp = emu.getStackCounter()
                    valu = emu.writeMemory(sp + offset, valu)

                # run the emulator instruction
                emu.executeOpcode(op)

                # test both the registers and stack values
                for name, valu in preg.items():
                    reg = emu.getRegisterByName(name)
                    self.assertEqual(reg, valu, msg='Given != Got for %s' % opbytes)

                for offset, valu in pstack.items():
                    sp = emu.getStackCounter()
                    mem = emu.readMemory(sp + offset, len(valu))
                    self.assertEqual(mem, valu)

    def test_i386_emulator(self):
        arch = envi.getArchModule('i386')
        self.run_emulator_tests(arch, i386Tests)
