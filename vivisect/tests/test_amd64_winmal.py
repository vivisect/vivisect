import unittest

import vivisect.const as v_const
import vivisect.tests.helpers as helpers


class Amd64Malwaretest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.razy = helpers.getTestWorkspace('windows', 'amd64', 'razy.exe')

    def test_jumptables(self):
        # for razy, normal
        jmpVa = 0x14008d974
        # Dict of Tuples of (Xref Addr, VA Name, Codeblock size)
        codeRefs = {
           0x14008d976: ('case0_14008d974', 7),
           0x14008d97d: ('case1_14008d974', 7),
           0x14008d984: ('case2_14008d974', 7),
           0x14008d98b: ('case3_14008d974', 7),
           0x14008d992: ('case4_14008d974', 7),
           0x14008d999: ('case5_14008d974', 7),
           0x14008d9a0: ('case6_14008d974', 7),
           0x14008d9a7: ('case7_14008d974', 7),
           0x14008d9ae: ('case8_14008d974', 7),
           0x14008d9b5: ('case9_14008d974', 7),
           0x14008d9bc: ('case10_14008d974', 7),
           0x14008d9c3: ('case11_14008d974', 7),
           0x14008d9ca: ('case12_14008d974', 7),
           0x14008d9d1: ('case13_14008d974', 7),
           0x14008d9d8: ('case14_14008d974', 5),
        }

        xrefs = self.razy.getXrefsFrom(jmpVa, rtype=v_const.REF_CODE)
        for xrfrom, xrto, xrtype, xrflags in xrefs:
            self.assertIn(xrto, codeRefs)

            name, cbsz = codeRefs.pop(xrto)
            self.assertEqual(name, self.razy.getName(xrto))

            cb = self.razy.getCodeBlock(xrto)
            self.assertEqual(xrto, cb[0])
            self.assertEqual(cbsz, cb[1])
            self.assertEqual(0x14008d930, cb[2])

        self.assertEqual(len(codeRefs), 0)

        # TODO: More here
