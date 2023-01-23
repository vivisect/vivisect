import os
import unittest
import vtrace.tests as vt_tests


class VtraceSymbolTest(vt_tests.VtraceProcessTest):

    def test_symbol(self):
        symlist = self.trace.getSymList()
        # currently there are 6355, but we don't care about exactness, just that
        # it's a largish number
        self.assertGreater(len(symlist), 1000)
        sym0 = symlist[0]

        symPyRevType = self.trace.getSymByName('PyReversed_Type')
        self.assertIsNotNone(symPyRevType)
        self.assertIn(symPyRevType.fname, ('python', 'python3', 'python2', 'libpython3'))
        self.assertEqual(symPyRevType.name, 'PyReversed_Type')
        self.assertAlmostEqual(symPyRevType.size, 0x1a0, delta=20)

        symPyRevT2 = self.trace.getSymByAddr(symPyRevType.value)
        self.assertEqual(symPyRevType, symPyRevT2)


