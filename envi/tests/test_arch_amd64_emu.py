import envi
import envi.tests.test_arch_i386_emu as i386etest

amd64Tests = [
    # idiv rdi
    {'bytes': '48f7ff',
     'setup': ({'rax': 0xffffffffffffffe2, 'rdx': 0xffffffffffffffff}, {}),
     'tests': ({'rax': 0, 'rdx': 0xffffffffffffffe2}, {})},
]

class Amd64EmulatorTests(i386etest.i386EmulatorTests):
    def test_amd64_emulator(self):
        arch = envi.getArchModule('amd64')
        self.run_emulator_tests(arch, amd64Tests)
