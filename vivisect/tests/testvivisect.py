import unittest

from cStringIO import StringIO

import vivisect
import vivisect.tests.helpers as helpers


class VivisectTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create and analyze the workspace only once
        super(VivisectTest, cls).setUpClass()
        cls.elf_fn = helpers.getTestPath('linux', 'i386', 'chgrp.llvm')
        cls.elf_vw = vivisect.VivWorkspace()
        cls.elf_vw.loadFromFile(cls.elf_fn)
        cls.elf_vw.analyze()

    def test_consecutive_jump_table(self):
        primaryJumpOpVa = 0x804c9b6
        secondJumpOpVa = 0x804ca2b

        pfva = self.elf_vw.getFunction(primaryJumpOpVa)
        sfva = self.elf_vw.getFunction(secondJumpOpVa)
        self.assertEqual(pfva, sfva)
        self.assertTrue(pfva is not None)

        # 2 actual codeblocks and 1 xref to the jumptable itself
        prefs = self.elf_vw.getXrefsFrom(primaryJumpOpVa)
        self.assertEqual(len(prefs), 3)
        cmnt = self.elf_vw.getComment(0x804c9bd)
        self.assertEqual(cmnt, 'Other Case(s): 2, 6, 8, 11, 15, 20, 21, 34, 38, 40, 47')
        # 13 actual codeblocks and 1 xref to the jumptable itself
        srefs = self.elf_vw.getXrefsFrom(secondJumpOpVa)
        self.assertEqual(len(srefs), 14)
        cmnt = self.elf_vw.getComment(0x804ca4a)
        self.assertEqual(cmnt, 'Other Case(s): 41')

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
