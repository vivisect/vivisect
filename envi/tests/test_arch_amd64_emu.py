import envi
import envi.tests.test_arch_i386_emu as i386etest

amd64Tests = [
    # idiv rdi
    {'bytes': '48f7ff',
     'setup': ({'rax': 0xffffffffffffffe2, 'rdx': 0xffffffffffffffff}, {}),
     'tests': ({'rax': 0, 'rdx': 0xffffffffffffffe2}, {})},
    # div eax with 32-bit args
    {'bytes': 'f7f0',
     'setup': ({'rax': 48, 'rdx': 1}, {}),
     'tests': ({'rax': 89478486, 'rdx': 16}, {})},
    # div rax with 64-bit args
    {'bytes': '48f7f0',
     'setup': ({'rax': 48, 'rdx': 1}, {}),
     'tests': ({'rax': 384307168202282326, 'rdx': 16}, {})},
]

class Amd64EmulatorTests(i386etest.i386EmulatorTests):
    def test_amd64_emulator(self):
        arch = envi.getArchModule('amd64')
        self.run_emulator_tests(arch, amd64Tests)
