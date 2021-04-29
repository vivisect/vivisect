'''
One day we might replace this/add to this with a side by side lockstepper with some other emulator,
but for now, this is both faster to make and vastly more self-contained (which is nice)
'''
import binascii
import unittest

import envi
import envi.expression as e_expr

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
      Keyed by an expression that's evaluated by the envi.expression.evaluate method
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
    # push 0x12345678
    {'bytes': '6878563412',
     'setup': ({}, {}),
     'tests': ({'esp': STACKBASE-4}, {'esp': b'\x78\x56\x34\x12'})},
    # push fs
    {'bytes': '0fa0',
     'setup': ({'fs': 0xBAD1}, {}),
     'tests': ({}, {'esp': b'\xD1\xBA'})},
    # mov ebx, 47
    {'bytes': 'bb2f000000',
     'setup': ({}, {}),
     'tests': ({'ebx': 47}, {})},
    # bsr ecx, edx
    {'bytes': '0FBDCA',
     'setup': ({'ecx': 0x47}, {}),
     'tests': ({'ecx': 23}, {})},
    # push word [esp+2]
    {'bytes': '66ff742402',
     'setup': ({}, {'esp': b'\xCD\xFE\x89\x43'}),
     'tests': ({'esp': STACKBASE-2}, {'esp': b'\x89\x43'})},
    # push [esp]
    {'bytes': 'FF3424',
     'setup': ({}, {'esp': b'\x01\x02\x03\x04'}),
     'tests': ({'esp': STACKBASE-4}, {'esp+4': b'\x01\x02\x03\x04'})},
    # add byte [ecx],al
    {'bytes': '0001',
     'setup': ({'ecx': 0x80, 'eax': 57}, {'esp': b'\x15\x00\x00\x00'}),
     'tests': ({}, {'esp': b'\x4e\x00\x00\x00'})},
    # sub edx, ecx
    {'bytes': '29ca',
     'setup': ({'edx': 0xf9e7cd45, 'ecx': 0xbfcdef00}, {}),
     'tests': ({'edx': 0x3a19de45, 'eflags': 0}, {})},
    # mul edx
    {'bytes': 'f7e2',
     'setup': ({'eax': 0x47b3, 'edx': 0x898937}, {}),
     'tests': ({'eax': 0x85393275, 'edx': 0x26}, {})},
    # div ax
    {'bytes': '66f7f0',
     'setup': ({'eax': 48, 'edx': 1}, {}),
     'tests': ({'eax': 1366, 'edx': 16}, {})},
    # rol eax, 4
    {'bytes': 'c1c004',
     'setup': ({'eax': 5}, {}),
     'tests': ({'eax': 80}, {})},
    # rol eax, 8
    {'bytes': 'c1c008',
     'setup': ({'eax': 0xABCD0000}, {}),
     'tests': ({'eax': 0xCD0000AB, 'eflags': 1}, {})},
    # ror eax, 5
    {'bytes': 'c1c805',
     'setup': ({'eax': 0x79}, {}),
     'tests': ({'eax': 0xc8000003, 'eflags': 1}, {})},
    # ror eax, cl
    {'bytes': 'd3c8',
     'setup': ({'eax': 0x79, 'cl': 1}, {}),
     'tests': ({'eax': 0x8000003c, 'eflags': 0x801}, {})},
    # btr ecx, 17
    {'bytes': '0fbaf111',
     'setup': ({'ecx': 0xF002000F}, {}),
     'tests': ({'eflags': 1, 'ecx': 0xF000000F}, {})},
]


class IntelEmulatorTests(unittest.TestCase):
    def setEmuDefaults(self, emu):
        for name in emu.getRegisterNames():
            emu.setRegisterByName(name, DEFREG)
        emu.addMemoryMap(0, 6, "[stack]", b'\xAB' * 0x100)
        emu.setStackCounter(STACKBASE)
        emu.setRegisterByName('eflags', 0)

    def run_emulator_tests(self, arch, tests):
        emu = arch.getEmulator()
        self.setEmuDefaults(emu)
        for test in tests:
            byts = test['bytes']
            try:
                op = arch.archParseOpcode(binascii.unhexlify(byts), 0, 0x40)
            except envi.InvalidInstruction:
                self.fail('Failed to parse opcode bytes: %s' % byts)

            with emu.snap():
                # do any required setup
                for name, valu in test['setup'][0].items():
                    emu.setRegisterByName(name, valu)

                for expr, valu in test['setup'][1].items():
                    addr = e_expr.evaluate(expr, emu.getRegisters())
                    valu = emu.writeMemory(addr, valu)

                # run the emulator instruction
                emu.executeOpcode(op)

                # test both the registers and stack values
                for name, valu in test['tests'][0].items():
                    reg = emu.getRegisterByName(name)
                    self.assertEqual(reg, valu, msg='Given != Got for %s (%s)' % (byts, str(op)))

                for expr, valu in test['tests'][1].items():
                    addr = e_expr.evaluate(expr, emu.getRegisters())
                    mem = emu.readMemory(addr, len(valu))
                    self.assertEqual(mem, valu)

    def test_i386_emulator(self):
        arch = envi.getArchModule('i386')
        self.run_emulator_tests(arch, i386Tests)
