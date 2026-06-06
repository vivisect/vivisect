import binascii
import unittest

import envi

instrs = [
    ('nop', '00', '',  ''),
    ('12', '', '', '')
]

class Z80InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("z80")
    def test_envi_z80_instrs(self):
        for name, byts, reprOp, renderOp in instrs:
            op = self._arch.archParseOpcode(binascii.unhexlify(byts), 0, 0x400)
            print(name, byts, repr(op))
