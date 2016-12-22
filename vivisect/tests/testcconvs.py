import unittest

import envi
import vivisect
import vivisect.codegraph as codegraph
import vivisect.tests.samplecode as samplecode
from vivisect.const import *

import vivisect.tests.vivbins as vivbins

# fsize, fva, cconvname, argdefs, comparisons
bins_w32 = [
    # kernel32.dll 32bit version 5.1.2600.5781
    (53, 0x7c82d9cd, 'stdcall', [('int', 'arg0')], ((0xc, 0, 'local8'), (0x10, 0, 'arg0'))),
    (53, 0x7c861fcc, 'thiscall', [('void *', 'ecx'), ('int', 'arg1')], ((0x19, 0, 'arg1'), (0x1f, 0, 'local8'))),
    (59, 0x7c80df44, 'cdecl', [('int', 'arg0'), ('int', 'arg1'), ('int', 'arg2'), ('int', 'arg3'), ('int', 'arg4')],
     ((0, 1, 'arg0'), (0x12, 1, 'arg4'))),
    (300, 0x7c820799, 'msfastcall',
     [('int', 'ecx'), ('int', 'edx'), ('int', 'arg2'), ('int', 'arg3'), ('int', 'arg4'), ('int', 'arg5')],
     ((8, 1, 'arg5'), (0x22, 1, 'local12'))),
    # missing bfastcall example
]

bins_w64 = [
    # testexe_amd64.exe
    (714, 0x1400071ec, 'msx64call',
     [('int', 'rcx'), ('int', 'rdx'), ('int', 'r8'), ('int', 'r9'), ('int', 'arg4'), ('int', 'arg5'), ('int', 'arg6'),
      ('int', 'arg7')], ((0x1b, 0, 'shadow2'), (0x29, 0, 'local48'), (0x2d, 1, 'arg4'))),
]

bins_p64 = [
    (2668, 0x02008320, 'sysvamd64call',
     [('int', 'rdi'), ('int', 'rsi'), ('int', 'rdx'), ('int', 'rcx'), ('int', 'r8'), ('int', 'r9'), ('int', 'arg6'),
      ('int', 'arg7')], ((0x14, 0, 'local80'), (0x19, 1, 'arg7'))),
]


class CconvTest(unittest.TestCase):
    def do_checks(self, vw, binslist):
        for numargs, fva, cconv, argdefs, comparison in binslist:
            vw.makeFunction(fva)
            api = vw.getFunctionApi(fva)
            rettype, none, icconv, fname, args = api
            self.assertEqual(icconv, cconv)
            self.assertEqual(argdefs, args)

            for off, idx, cmpname in comparison:
                testval = vw.getSymHint(fva + off, idx)
                op = vw.parseOpcode(fva + off)
                oprepr = "0x%x: %s" % (op.va, op)
                # print testval
                self.assertEqual((cmpname, oprepr), (testval, oprepr))

    @vivbins.require
    def test_cconv_kernel32_32bit(self):
        vw = vivbins.getTestWorkspace('test_kernel32_32bit-5.1.2600.5781.dll', analyze=False)
        self.do_checks(vw, bins_w32)

    @vivbins.require
    def test_cconv_ms64bit(self):
        vw = vivbins.getTestWorkspace('testexe_amd64.exe', analyze=False)
        self.do_checks(vw, bins_w64)

    @vivbins.require
    def test_cconv_sysvamd64bit(self):
        vw = vivbins.getTestWorkspace('test_elf_amd64', analyze=False)
        self.do_checks(vw, bins_p64)
