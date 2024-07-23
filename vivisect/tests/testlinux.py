import logging
import unittest

import envi

import vivisect
import vivisect.const as v_const

import vivisect.tests.helpers as helpers
import vivisect.tests.utils as v_t_utils

class LinuxTests(v_t_utils.VivTest):

    def test_linux_x86_syscall(self):
        vw = helpers.getTestWorkspace('linux', 'i386', 'syscalls.elf')
        # address of the main function
        fva = 0x02001190
        self.eq(fva, vw.getFunction(fva))
        cb = vw.getCodeBlock(fva)
        loc = vw.getLocation(cb[0] + cb[1] - 1)
        self.eq(loc[0], 0x20011ab)
        self.eq(loc[1], 2)
        self.eq(loc[2], v_const.LOC_OP)
        self.eq(loc[3], envi.ARCH_I386 | envi.IF_PRIV)
        op = vw.parseOpcode(loc[0])
        self.eq(repr(op), 'int 128')
        self.eq(True, vw.isNoReturnVa(loc[0]))
