import unittest
import vivisect

import logging
import envi.common as e_common
import vivisect.tests.helpers as helpers

from vivisect.tests.switchdata import *

logger = logging.getLogger(__name__)
#e_common.initLogging(logger, 7)

class SwitchTest(unittest.TestCase):
    def test_amd64_ms_switch_0(self):
        base = 0x400000     # looks for reg at 0x3fb120
        fva = base + 0x4ee0
        vw = genMsSwitchWorkspace(MS_MAPS, base)
        vw.setMeta('DefaultCall', 'msx64call')
        vw.makeFunction(fva)
        funcblocks = vw.getFunctionBlocks(fva)
        funcblocks.sort()

        logger.debug("\n\n%s blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_ms_0))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(cbs_ms_0, vw.getFunctionBlocks(fva))
        self.assertEqual(5, len(vw.getXrefsFrom(base+0x11257)))

    def test_libc_switch_0(self):
        vw = genLinuxSwitchWorkspace(LIBC_MAPS, 0x500000)
        vw.makeFunction(0x500000)
        funcblocks = vw.getFunctionBlocks(0x500000)
        funcblocks.sort()

        logger.debug("\n\n%s blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs_libc_0))
        logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
        self.assertEqual(cbs_libc_0, vw.getFunctionBlocks(0x500000))

    def test_amd64_walker_switch_0(self):
        vw = genLinuxSwitchWorkspace(WALKER_MAPS, 0x5ff3a0, arch='amd64')
        vw.makeFunction(0x600000)
        funcblocks = set(vw.getFunctionBlocks(0x600000))

        self.assertEqual(cbs_walker_0, funcblocks)

    def test_amd64_ls_switch(self):
        self.maxDiff = None
        vw = helpers.getTestWorkspace('linux', 'amd64', 'ls')

        '''
        .text:0x00404072  loc_00404072: [9 XREFS]
        .text:0x00404072  8d42ff           lea eax,dword [rdx - 1]
        .text:0x00404075  83f805           cmp eax,5
        .text:0x00404078  0f87d7e6ffff     ja loc_00402755
        .text:0x0040407e  ff24c5e8294100   jmp qword [ptr_sub_0040438d_004129e8 + rax * 8]
        '''
        '''
        .text:0x0040295a  e8a1f8ffff       call ls.plt_getopt_long    ;ls.plt_getopt_long()
        .text:0x0040295f  83f8ff           cmp eax,0xffffffff
        .text:0x00402962  0f8463060000     jz loc_00402fcb
        .text:0x00402968  0583000000       add eax,131
        .text:0x0040296d  3d12010000       cmp eax,274
        .text:0x00402972  760c             jbe switch_00402980

        .text:0x00402974  case_-83to-53_-51to-43_-3E_-39to-38_-36_-34to-33_-2Dto-2C_-2A_-28to-23_-1E_-19_-Ato-4_402974: [218 XREFS]
        .text:0x00402974  bf02000000       mov edi,2
        .text:0x00402979  e8626b0000       call sub_004094e0    ;sub_004094e0(2)
        .text:0x0040297e  6690             nop 
        .text:0x00402980  switch_00402980: [1 XREFS]
        .text:0x00402980  ff24c550214100   jmp qword [ptr_sub_00402be5_00412150 + rax * 8]    ;lower: 0x-83, upper: 0xc
        '''
        '''
        .text:0x00404874  loc_00404874: [1 XREFS]
        .text:0x00404874  410fb608         movzx ecx,byte [r8]
        .text:0x00404878  80f978           cmp cl,120
        .text:0x0040487b  7623             jbe loc_004048a0

        .text:0x004048a0  loc_004048a0: [1 XREFS]
        .text:0x004048a0  440fb6d9         movzx r11d,cl
        .text:0x004048a4  switch_004048a4: [0 XREFS]
        .text:0x004048a4  42ff24dd601d4100 jmp qword [ptr_case_0_40495d_00411d60 + r11 * 8]    ;lower: 0x0, upper: 0x78
        '''
        _do_test(self, vw, jmpva=0x402980, fva=0x402690, cbs=cbs_amd64_ls_402980, xrefcnt=57)
        _do_test(self, vw, jmpva=0x4048a4, fva=0x404740, cbs=cbs_amd64_ls_4048a4, xrefcnt=14)
        _do_test(self, vw, jmpva=0x40d57f, fva=0x40d840, cbs=cbs_amd64_ls_40d57f, xrefcnt=11)
        _do_test(self, vw, jmpva=0x410300, fva=0x4101a0, cbs=cbs_amd64_ls_410300, xrefcnt=10)
        # doesn't work correctly here:
        #_do_test(self, vw, jmpva=0x40407e, fva=0x404223, cbs=cbs_amd64_ls_40407e, xrefcnt=0)

    def test_amd64_chown_switch(self):
        self.maxDiff = None
        vw = helpers.getTestWorkspace('linux', 'amd64', 'chown')

        '''
        .text:0x020045b9  488d0d087e0000   lea rcx,qword [rip + $loc_0200c3c8]
        .text:0x020045c0  0fb6d3           movzx edx,bl
        .text:0x020045c3  48630491         movsxd rax,dword [rcx + rdx * 4]
        .text:0x020045c7  4801c8           add rax,rcx
        .text:0x020045ca  ffe0             jmp rax
        '''
        _do_test(self, vw, jmpva=0x20045ca, fva=0x02004050, cbs=cbs_amd64_chown_2004050, xrefcnt=17)

    def test_i386_static32_switch(self):
        self.maxDiff = None
        vw = helpers.getTestWorkspace('linux', 'i386', 'static32.llvm.elf')

        '''
        .text:0x0805eec0  81f980000000     cmp ecx,128
        .text:0x0805eec6  7318             jnc loc_0805eee0
        .text:0x0805eec8  e8b398feff       call static32_llvm.__weak___x86.get_pc_thunk.bx    ;static32_llvm.__weak___x86.get_pc_thunk.bx()
        .text:0x0805eecd  81c31beb0400     add ebx,0x0004eb1b
        .text:0x0805eed3  031c8b           add ebx,dword [ebx + ecx * 4]
        .text:0x0805eed6  01ca             add edx,ecx
        .text:0x0805eed8  switch_0805eed8: [0 XREFS]
        .text:0x0805eed8  ffe3             jmp ebx    ;lower: 0x20, upper: 0x7f
        '''
        _do_test(self, vw, jmpva=0x805eed8, fva=0x805edc0, cbs=cbs_i386_static_805edc0, xrefcnt=96)
        _do_test(self, vw, jmpva=0x80621da, fva=0x80621a0, cbs=cbs_i386_static_80621a0, xrefcnt=7)
        _do_test(self, vw, jmpva=0x808db0a, fva=0x808dc28, cbs=cbs_i386_static_808dc28, xrefcnt=9)
        _do_test(self, vw, jmpva=0x80a6954, fva=0x80a6920, cbs=cbs_i386_static_80a6920, xrefcnt=7)


    def test_i386_ld_switch(self):
        self.maxDiff = None
        vw = helpers.getTestWorkspace('linux', 'i386', 'ld-2.31.so')
        vw.analyze()

        cur_switches = [x for x, y, z in vw.getVaSetRows('SwitchCases')]
        cur_switches.sort()
        ld_switches.sort()
        for ld_switch in ld_switches:
            self.assertIn(ld_switch, cur_switches)

        '''
        .text:0x0200214c  loc_0200214c: [5 XREFS]
        .text:0x0200214c  8b55d0           mov edx,dword [ebp + local52]
        .text:0x0200214f  83ea06           sub edx,6
        .text:0x02002152  83fa23           cmp edx,35
        .text:0x02002155  7749             ja case_Eto13_15to28_2A_2Cto2E_20021a0
        .text:0x02002157  8b84970030ffff   mov eax,dword [edi + edx * 4 + -53248]
        .text:0x0200215e  01f8             add eax,edi
        .text:0x02002160  switch_02002160: [0 XREFS]
        .text:0x02002160  3effe0           ds: jmp eax    ;lower: 0xc, upper: 0x2f

        '''
        _do_test(self, vw, jmpva=0x2002160, fva=0x2001dd0, cbs=cbs_i386_ld_2002160, xrefcnt=6)
        #_do_test(self, vw, jmpva=0x80621da, fva=0x80621a0, cbs=cbs_i386_static_80621a0, xrefcnt=7)
        #_do_test(self, vw, jmpva=0x808db0a, fva=0x808dc28, cbs=cbs_i386_static_808dc28, xrefcnt=9)
        #_do_test(self, vw, jmpva=0x80a6954, fva=0x80a6920, cbs=cbs_i386_static_80a6920, xrefcnt=7)




def _do_test(self, vw, jmpva, fva, cbs, xrefcnt):
    vw.makeFunction(fva)
    funcblocks = vw.getFunctionBlocks(fva)
    funcblocks.sort()
    cbs.sort()
    logger.debug("\n\n%s (3) blocks:\n\t%r\n\t%r" % (self, funcblocks, cbs))
    logger.debug("switches: %r" % vw.getVaSetRows('SwitchCases') )
    self.assertEqual(cbs, funcblocks)
    self.assertEqual(xrefcnt, len(vw.getXrefsFrom(jmpva)))


