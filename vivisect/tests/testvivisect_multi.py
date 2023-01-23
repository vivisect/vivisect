import logging
import unittest
import vivisect.tests.helpers as helpers
import vivisect.tests.utils as v_t_utils


logger = logging.getLogger(__name__)


class VivisectMultiFileTest(v_t_utils.VivTest):
    def test_multiple_i386(self):
        '''
        Note: because we're using a non-relocatable executable (vdir.llvm) and relocating it, this
        will unfortunately throw a lot of ugly exceptions, because there are hard-coded addresses
        in the instructions themselves, which are relocations because the file isn't "relocatable"

        We only test the things which should work because they are made available for relocation
        through the ELF metadata.
        '''
        vw = helpers.getTestWorkspace_nocache('linux', 'i386', 'chgrp.llvm')
        vw = helpers.getTestWorkspace_nocache('linux', 'i386', 'vdir.llvm', vw=vw)
        vw = helpers.getTestWorkspace_nocache('linux', 'i386', 'ld-2.31.so', vw=vw)

        # test memory maps are not overlapping
        for mmap1 in vw.getMemoryMaps():
            for mmap2 in vw.getMemoryMaps():
                if mmap1 == mmap2:
                    continue

                mmva1, mmsz1, mmp1, mmnm1 = mmap1
                mmva2, mmsz2, mmp2, mmnm2 = mmap2
                self.assertFalse(mmva1 <= mmva2 < (mmva1 + mmsz1))
                self.assertFalse(mmva2 <= mmva1 < (mmva2 + mmsz2))

        # test __entry values
        vdir = vw.parseExpression('vdir')
        chgrp = vw.parseExpression('chgrp')
        ld_2_31 = vw.parseExpression('ld_2_31')

        vdir_entry = vw.parseExpression('vdir.__entry')
        chgrp_entry = vw.parseExpression('chgrp.__entry')
        ld_2_31_entry = vw.parseExpression('ld_2_31.__entry')

        self.assertEqual(vdir_entry-vdir, 7024)
        self.assertEqual(chgrp_entry-chgrp, 4576)
        self.assertEqual(ld_2_31_entry-ld_2_31, 4384)

        # test main functions
        vdir_main = vw.parseExpression('vdir.main')
        chgrp_main = vw.parseExpression('chgrp.main')

        self.assertEqual(vdir_main-vdir, 7312)
        self.assertEqual(chgrp_main-chgrp, 5712)

        # test PLT functions
        vdir_plt_names = [(va,name) for va,name in vw.getNames() if 'vdir.plt_' in name]
        chgrp_plt_names = [(va,name) for va,name in vw.getNames() if 'chgrp.plt_' in name]
        ld_2_31_plt_names = [(va,name) for va,name in vw.getNames() if 'ld_2_31.plt_' in name]
        self.assertEqual(len(vdir_plt_names), 0)    # can't expect PLT analysis to work for a binary not intended to be relocated.  
        self.assertEqual(len(chgrp_plt_names), 70)  # this is more than we get when loading chgrp on it's own!?
        self.assertEqual(len(ld_2_31_plt_names), 8)

        ## now just poke at one or two in each proggy
        ### chgrp __gmon_start__
        got_gmon_start = vw.parseExpression('chgrp+0xbffc')
        plt_gmon_start = vw.parseExpression('chgrp+0x11d0')
        self.assertIn('*.__gmon_start___', vw.getName(got_gmon_start))
        self.assertIn('plt___gmon_start__', vw.getName(plt_gmon_start))
        self.assertIn((plt_gmon_start, got_gmon_start, 2, 0), vw.getXrefsFrom(plt_gmon_start))

        ### chgrp __assert_fail
        got_gmon_start = vw.parseExpression('chgrp+0xbffc')
        plt_gmon_start = vw.parseExpression('chgrp+0x11d0')
        self.assertIn('*.__gmon_start___', vw.getName(got_gmon_start))
        self.assertIn('plt___gmon_start__', vw.getName(plt_gmon_start))
        self.assertIn((plt_gmon_start, got_gmon_start, 2, 0), vw.getXrefsFrom(plt_gmon_start))

        # test exports
        for exp in vw.getExports():
            eva, etype, esym, efile = exp
            mmap = vw.getMemoryMap(eva)
            self.assertEqual(mmap[3], efile, msg="Failed: %r  for %r" % (exp, mmap))

        # test GOT locations
        vdir_main = vw.parseExpression('vdir.main')
        chgrp_main = vw.parseExpression('chgrp.main')

        self.assertEqual(vdir_main-vdir, 7312)
        self.assertEqual(chgrp_main-chgrp, 5712)

        # test Relocs
        self.assertIn(('ld_2_31', 179948, 2, 135749, 4), vw.getRelocations())
        rel0 = vw.parseExpression('ld_2_31 + 179948')
        ptr0 = vw.parseExpression('ld_2_31 + 135749')
        self.assertIn((rel0, ptr0, 3, 0), vw.getXrefsFrom(rel0))


        # test Sections
        for seg in vw.getSegments():
            if seg[2] == '.text':
                if seg[3] == 'vdir':
                    self.assertEqual(7024, seg[0] - vw.parseExpression('vdir'))
                if seg[3] == 'chgrp':
                    self.assertEqual(4576, seg[0] - vw.parseExpression('chgrp'))
                if seg[3] == 'ld_2_31':
                    self.assertEqual(4352, seg[0] - vw.parseExpression('ld_2_31'))
