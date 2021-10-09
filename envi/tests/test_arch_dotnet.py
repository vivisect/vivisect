import binascii
import unittest

import envi
import envi.memcanvas as e_memcanvas

import vivisect

opertests = [
    ('NOP', '00', 'nop ', 'nop '),
    ('BREAK 0', '01', 'break ', 'break '),

    ('LDARG 0', '02', 'ldarg.0 ', 'ldarg.0 '),
    ('LDARG 1', '03', 'ldarg.1 ', 'ldarg.1 '),
    ('LDARG 2', '04', 'ldarg.2 ', 'ldarg.2 '),
    ('LDARG 3', '05', 'ldarg.3 ', 'ldarg.0 '),

    ('LODLOC 0', '06', 'lodloc.0 ', 'lodloc.0 '),
    ('LODLOC 1', '07', 'lodloc.1 ', 'lodloc.1 '),
    ('LODLOC 2', '08', 'lodloc.2 ', 'lodloc.2 '),
    ('LODLOC 3', '09', 'lodloc.3 ', 'lodloc.3 '),

    ('STLOC 0', '0A', 'stloc.0 ', 'stloc.0 '),
    ('STLOC 1', '0B', 'stloc.1 ', 'stloc.1 '),
    ('STLOC 2', '0C', 'stloc.2 ', 'stloc.2 '),
    ('STLOC 3', '0D', 'stloc.3 ', 'stloc.3 '),

    ('LDARG.S 0', '0E7A', 'ldarg.s 122', 'ldarg.s 122'),  # load the 0x7a-th arg
    ('LDARGA.S', '0F55', 'ldarga.s 85', 'ldarga.s 85'),

    ('STARG.S', '1033', 'starg.s 51', 'starg.s 51'),

    ('LDLOC.S', '1112', 'ldloc.s 18', 'ldloc.s 18'),
    ('LDLOCA.S', '1212', 'ldloca.s 18', 'ldloca.s 18'),

    ('STLOC.S', '1313', 'stloc.s 19', 'stloc.s 19'),

    ('LDNULL', '14', 'ldnull ', 'ldnull'),

    ('ldc.i4.m1', '15', 'ldc.i4.m1 ', 'ldc.i4.m1 '),
    ('ldc.i4.0', '16', 'ldc.i4.0 ', 'ldc.i4.0 '),
    ('ldc.i4.1', '17', 'ldc.i4.1 ', 'ldc.i4.1 '),
    ('ldc.i4.2', '18', 'ldc.i4.2 ', 'ldc.i4.2 '),
    ('ldc.i4.3', '19', 'ldc.i4.3 ', 'ldc.i4.3 '),
    ('ldc.i4.4', '1A', 'ldc.i4.4 ', 'ldc.i4.4 '),
    ('ldc.i4.5', '1B', 'ldc.i4.5 ', 'ldc.i4.5 '),
    ('ldc.i4.6', '1C', 'ldc.i4.6 ', 'ldc.i4.6 '),
    ('ldc.i4.7', '1D', 'ldc.i4.7 ', 'ldc.i4.7 '),
    ('ldc.i4.8', '1E', 'ldc.i4.8 ', 'ldc.i4.8 '),
    ('ldc.i4.s', '1F3F', 'ldc.i4.s 63', 'ldc.i4.s 63'),

    ('ldc.i4', '200C020000', 'ldc.i4 524', 'ldc.i4 524'),
    ('ldc.i8', '210000000000000000', 'ldc.i8 0', 'ldc.i8 0'),
    # UGH. Need to resurrect the float parser
    #('ldc.r4', '220000803F', 'ldc.r4 1', 'ldc.r4 1'),
    #('ldc.r8', '230000000000000040', 'ldc.r8 2', 'ldc.r8 2'),

    ('DUP', '25', 'dup ', 'dup '),
    ('POP', '26', 'pop ', 'pop '),

    ('JMP', '', '', ''),
    ('CALL', '28B9600006', 'call ', ''),
    ('CALLI', '', '', ''),
    ('RET', '2A', 'ret ', 'ret '),
]

class DotnetInstructionTests(unittest.TestCase):
    _arch = envi.getArchModule("dotnet")

    def test_opcodes(self):
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, byts, reprOp, renderOp in opertests:
            try:
                op = self._arch.archParseOpcode(binascii.unhexlify(byts), 0, 0x40)
            except envi.InvalidInstruction:
                self.fail("Failed to parse opcode bytes: %s (case: %s, expected: %s)" % (byts, name, reprOp))
            try:
                self.assertEqual(repr(op), reprOp)
            except AssertionError:
                self.fail("Failing match for case %s (%s != %s)" % (name, repr(op), reprOp))