import unittest

from cStringIO import StringIO

import vivisect
import vivisect.tests.helpers as helpers


class VivisectTest(unittest.TestCase):

    def test_consecutive_jump_table(self):
        vw = helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')

        primaryJumpOpVa = 0x804c9b6
        secondJumpOpVa = 0x804ca2b

        pfva = vw.getFunction(primaryJumpOpVa)
        sfva = vw.getFunction(secondJumpOpVa)
        self.assertEqual(pfva, sfva)
        self.assertTrue(pfva is not None)

        # 2 actual codeblocks and 1 xref to the jumptable itself
        prefs = vw.getXrefsFrom(primaryJumpOpVa)
        self.assertEqual(len(prefs), 3)
        cmnt = vw.getComment(0x804c9bd)
        self.assertEqual(cmnt, 'Other Case(s): 2, 6, 8, 11, 15, 20, 21, 34, 38, 40, 47')
        # 13 actual codeblocks and 1 xref to the jumptable itself
        srefs = vw.getXrefsFrom(secondJumpOpVa)
        self.assertEqual(len(srefs), 14)
        cmnt = vw.getComment(0x804ca4a)
        self.assertEqual(cmnt, 'Other Case(s): 41')

    def test_consecutive_jump_table_diff_func(self):
        vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')
        jumptabl = [
            0x8059718,
            0x8059b68,
            0x8059b78,
            0x8059b90,
            0x8059ba4,
            0x8059bb8,
            0x8059d9c,
            0x8059e30,
            0x8059fac
        ]

        # list of tuples of (xref addr, func addr, number of xrefs from xref addr)
        ans = [
            (0x804a468, 0x804a210, 62),
            (0x804ad21, 0x804a210, 5),
            (0x804b00a, 0x804a210, 7),  # 0x8059b78
            (0x804beee, 0x804bee0, 6),
            (0x804d1c9, 0x804d1a0, 6),
            (0x804d28f, 0x804d1a0, 15),  # 0x8059bb8
            (0x804d1e7, 0x804d1a0, 6),
            (0x804d95b, 0x804d820, 3),
            (0x804fd01, 0x804fc70, 9)  # 0x8059fac
        ]

        for i, tablva in enumerate(jumptabl):
            refva = vw.getXrefsTo(tablva)
            self.assertEqual(len(refva), 1)
            refva = refva[0]
            func = vw.getFunction(refva[0])
            refs = vw.getXrefsFrom(refva[0])
            test = ans[i]
            self.assertEqual(refva[0], test[0])
            self.assertEqual(func, test[1])
            self.assertEqual(len(refs), test[2])

    def test_viv_bigend(self):
        fd = StringIO('ABCDEFG')

        vw = vivisect.VivWorkspace()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.bigend = True
        vw.config.viv.parsers.blob.baseaddr = 0x22220000

        vw.loadFromFd(fd, fmtname='blob')

        self.assertEqual(vw.castPointer(0x22220000), 0x41424344)
        self.assertEqual(vw.parseNumber(0x22220000, 2), 0x4142)

    def test_posix_impapi(self):
        pass
