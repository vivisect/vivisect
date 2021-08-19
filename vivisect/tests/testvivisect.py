import io
import logging
import unittest

import envi
import envi.memory as e_memory

import vivisect
import vivisect.exc as v_exc
import vivisect.const as v_const
import vivisect.tools.graphutil as v_t_graphutil

import vivisect.tests.helpers as helpers


logger = logging.getLogger(__name__)


def glen(g):
    return len([x for x in g])


def isint(x):
    return type(x) is int


class VivisectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.firefox_vw = helpers.getTestWorkspace('windows', 'amd64', 'firefox.exe')
        cls.chgrp_vw = helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')
        cls.vdir_vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')

    def test_xrefs_types(self):
        '''
        Test that we have data consistency in xrefs
        '''
        for vw in [self.chgrp_vw, self.vdir_vw, self.firefox_vw]:
            for xfrom, xto, xtype, xflags in vw.getXrefs():
                self.assertEqual((xfrom, isint(xfrom)),
                                 (xfrom, True))
                self.assertEqual((xto, isint(xto)),
                                 (xto, True))
                self.assertEqual((xtype, isint(xtype)),
                                 (xtype, True))
                self.assertEqual((xflags, isint(xflags)),
                                 (xflags, True))

    def test_cli_search(self):
        '''
        Test that EnviCli.do_search works
        '''
        #TODO: make real tests with asserts
        self.chgrp_vw.do_search("-e utf-16le foo")
        self.chgrp_vw.do_search("-e utf-16le foo")
        self.chgrp_vw.do_search("-X 41414141")
        self.chgrp_vw.do_search("-E 0x41414141")
        self.chgrp_vw.do_search("-E 0x41414142")
        self.chgrp_vw.do_search("-r 0x4141.*42")
        self.chgrp_vw.do_search("-r 0x4141.*42 -c")
        self.chgrp_vw.do_search("-c -r qsort")
        self.chgrp_vw.do_search("-c -r qsort -R 0x8048000:0x200")
        self.chgrp_vw.do_search("-c -r qsort -R 0x8048000:0x2000")

    def test_cli_searchopcode(self):
        '''
        Test that VivCli.do_searchopcodes works
        '''
        #TODO: make real tests with asserts
        self.chgrp_vw.do_searchopcodes('foo')
        self.chgrp_vw.do_searchopcodes('-f 0x08050200 ret')
        self.chgrp_vw.do_searchopcodes('-c rol')
        self.chgrp_vw.do_searchopcodes('-o rol')
        self.chgrp_vw.do_searchopcodes('-t rol')
        self.chgrp_vw.do_searchopcodes('-M red rol')
        self.chgrp_vw.do_searchopcodes('-f 0x08050200 -R r.t')

    def test_loc_types(self):
        '''
        Test that we have data consistency in locations
        '''
        for vw in [self.chgrp_vw, self.vdir_vw, self.firefox_vw]:
            for lva, lsize, ltype, linfo in vw.getLocations():
                self.assertEqual((lva, isint(lva)),
                                 (lva, True))
                self.assertEqual((lsize, isint(lsize)),
                                 (lsize, True))
                self.assertEqual((ltype, isint(ltype)),
                                 (ltype, True))
                if linfo:
                    self.assertTrue(type(linfo) in (int, str, list))

    def test_vaset_populate(self):
        '''
        Make sure the the VASEts are populated in roughly the way we expect
        '''
        vw = self.vdir_vw
        ans = {
            'FileSymbols': [('', 0), ('filenamecat-lgpl.c', 0), ('gettime.c', 0),
                            ('areadlink-with-size.c', 0), ('filenamecat.c', 0), ('umaxtostr.c', 0),
                            ('close-stream.c', 0), ('filemode.c', 0), ('obstack.c', 0),
                            ('mbswidth.c', 0), ('imaxtostr.c', 0), ('mbsalign.c', 0),
                            ('time_rz.c', 0), ('fflush.c', 0), ('hash-triple.c', 0),
                            ('hard-locale.c', 0), ('se-selinux.c', 0), ('xstrtoul.c', 0),
                            ('mpsort.c', 0), ('version-etc-fsf.c', 0), ('xdectoumax.c', 0),
                            ('hash.c', 0), ('dirname-lgpl.c', 0), ('xgetcwd.c', 0),
                            ('quotearg.c', 0), ('hash-pjw.c', 0), ('closeout.c', 0),
                            ('progname.c', 0), ('localcharset.c', 0), ('basename-lgpl.c', 0),
                            ('ls.c', 0), ('human.c', 0), ('version-etc.c', 0),
                            ('nstrftime.c', 0), ('c-ctype.c', 0), ('xgethostname.c', 0),
                            ('c-strncasecmp.c', 0), ('xalloc-die.c', 0), ('xstrtol-error.c', 0),
                            ('crtstuff.c', 0), ('ls-vdir.c', 0), ('argmatch.c', 0),
                            ('xstrtoumax.c', 0), ('canonicalize.c', 0), ('stat-time.c', 0),
                            ('calloc.c', 0), ('file-set.c', 0), ('xmalloc.c', 0),
                            ('timespec.c', 0), ('fseeko.c', 0), ('file-has-acl.c', 0),
                            ('bitrotate.c', 0), ('idcache.c', 0), ('mbrtowc.c', 0),
                            ('dirname.c', 0), ('exitfail.c', 0), ('filevercmp.c', 0),
                            ('fclose.c', 0), ('version.c', 0), ('same.c', 0)],
            'DynamicBranches': [(134541059, 'call eax', 65537), (134555409, 'call dword [edi + 28]', 65541),
                                (134540947, 'call ebp', 65537), (134580376, 'call dword [ecx + 28]', 65541),
                                (134553117, 'call dword [ecx + 24]', 65541), (134540968, 'call ebp', 65537),
                                (134580408, 'call dword [ecx + 32]', 65541), (134554170, 'call eax', 65537),
                                (134519869, 'call edx', 65537), (134547907, 'call dword [esp + 52]', 65541),
                                (134555467, 'call dword [edi + 28]', 65541), (134554325, 'call dword [esi + 32]', 65541),
                                (134541400, 'call eax', 65537), (134561888, 'call eax', 65537),
                                (134562273, 'call dword [esp + 68]', 65541), (134583780, 'call dword [ebx + edi * 4 - 244]', 65541),
                                (134554213, 'call eax', 65537), (134541288, 'call eax', 65537),
                                (134553449, 'call edi', 65537), (134519792, 'call eax', 65537),
                                (134553075, 'call dword [ebx + 28]', 65541), (134540791, 'call dword [esp + 32]', 65541),
                                (134541176, 'call eax', 65537), (134562046, 'call dword [esp + 68]', 65541)],
            'NoReturnCalls': [(134573120,), (134524676,), (134577802,), (134582295,), (134551055,), (134525456,),
                              (134568495,), (134534039,), (134524568,), (134528303,), (134578863,), (134577311,),
                              (134549928,), (134544175,), (134553138,), (134572852,), (134580661,),
                              (134550582,), (134579529,), (134572857,), (134534204,), (134577471,), (134580544,),
                              (134568769,), (134546505,), (134578743,), (134553208,), (134555349,),
                              (134580057,), (134521306,), (134531547,), (134572084,), (134578576,), (134554727,),
                              (134576873,), (134580336,), (134521331,), (134550133,), (134521336,), (134529017,),
                              (134524668,), (134577049,), (134547258,), (134577158,), (134524356,), (134524581,),
                              (134576974,), (134576909,),
                              ],
            'Bookmarks': [],
            'SwitchCases': [],
            'thunk_bx': [(134519744,),
                         (134519715,)],
            'FuncWrappers': [(134517916, 134517946)],
            'Emulation Anomalies': [(134546338, 'DivideByZero at 0x80503a2'),
                                    (134544390, 'DivideByZero at 0x804fc06'),
                                    (134545954, 'DivideByZero at 0x8050222'),
                                    (134546126, 'DivideByZero at 0x80502ce')],
            'WeakSymbols': [('data_start', 0x80611b0),
                            ('program_invocation_name', 0x8061300),
                            ('program_invocation_short_name', 0x80612f0),
                            ('__gmon_start__', 0x8060ffc)],
            'PointersFromFile': [(134614800, 134519888, 'vdir', 'fini_function_0'),
                                 (134614796, 134519936, 'vdir', 'init_function_0'),
                                 (0x805a00c, 0x805d77c, 'vdir', 'long_options'),
                                 (0x805a01c, 0x805e7c9, 'vdir', 'long_options'),
                                 (0x805a02c, 0x805da20, 'vdir', 'long_options'),
                                 (0x805a03c, 0x805d6fa, 'vdir', 'long_options'),
                                 (0x805a04c, 0x805d700, 'vdir', 'long_options'),
                                 (0x805a05c, 0x805d70a, 'vdir', 'long_options'),
                                 (0x805a06c, 0x805d722, 'vdir', 'long_options'),
                                 (0x805a07c, 0x805d731, 'vdir', 'long_options'),
                                 (0x805a08c, 0x805d737, 'vdir', 'long_options'),
                                 (0x805a09c, 0x805d741, 'vdir', 'long_options'),
                                 (0x805a0ac, 0x805d751, 'vdir', 'long_options'),
                                 (0x805a0bc, 0x805d75a, 'vdir', 'long_options'),
                                 (0x805a0cc, 0x805d76d, 'vdir', 'long_options'),
                                 (0x805a0dc, 0x805d54a, 'vdir', 'long_options'),
                                 (0x805a0ec, 0x805d534, 'vdir', 'long_options'),
                                 (0x805a0fc, 0x805d775, 'vdir', 'long_options'),
                                 (0x805a10c, 0x805d780, 'vdir', 'long_options'),
                                 (0x805a11c, 0x805d78f, 'vdir', 'long_options'),
                                 (0x805a12c, 0x805d798, 'vdir', 'long_options'),
                                 (0x805a13c, 0x805d7a2, 'vdir', 'long_options'),
                                 (0x805a14c, 0x805d7a5, 'vdir', 'long_options'),
                                 (0x805a15c, 0x805d7be, 'vdir', 'long_options'),
                                 (0x805a16c, 0x805d7e6, 'vdir', 'long_options'),
                                 (0x805a17c, 0x805d7eb, 'vdir', 'long_options'),
                                 (0x805a18c, 0x805d585, 'vdir', 'long_options'),
                                 (0x805a19c, 0x805d7f2, 'vdir', 'long_options'),
                                 (0x805a1ac, 0x805d7fe, 'vdir', 'long_options'),
                                 (0x805a1bc, 0x805d806, 'vdir', 'long_options'),
                                 (0x805a1cc, 0x805d597, 'vdir', 'long_options'),
                                 (0x805a1dc, 0x805d811, 'vdir', 'long_options'),
                                 (0x805a1ec, 0x805d55f, 'vdir', 'long_options'),
                                 (0x805a1fc, 0x805d81b, 'vdir', 'long_options'),
                                 (0x805a20c, 0x805d551, 'vdir', 'long_options'),
                                 (0x805a21c, 0x805d82e, 'vdir', 'long_options'),
                                 (0x805a22c, 0x805d558, 'vdir', 'long_options'),
                                 (0x805a23c, 0x805d836, 'vdir', 'long_options'),
                                 (0x805a24c, 0x805d571, 'vdir', 'long_options'),
                                 (0x805a25c, 0x805d579, 'vdir', 'long_options'),
                                 (0x805a26c, 0x805d841, 'vdir', 'long_options'),
                                 (0x805a27c, 0x805d84c, 'vdir', 'long_options'),
                                 (0x805a28c, 0x805d854, 'vdir', 'long_options'),
                                 (0x805a29c, 0x805d85b, 'vdir', 'long_options'),
                                 (0x805a2ac, 0x805dae1, 'vdir', 'long_options'),
                                 (0x805a2e0, 0x805d860, 'vdir', 'sort_args'),
                                 (0x805a2e4, 0x805d558, 'vdir', 'sort_args'),
                                 (0x805a2e8, 0x805d54a, 'vdir', 'sort_args'),
                                 (0x805a2ec, 0x805d865, 'vdir', 'sort_args'),
                                 (0x805a2f0, 0x805dae1, 'vdir', 'sort_args'),
                                 (0x805a30c, 0x805d86f, 'vdir', 'time_args'),
                                 (0x805a310, 0x805d875, 'vdir', 'time_args'),
                                 (0x805a314, 0x805d87c, 'vdir', 'time_args'),
                                 (0x805a318, 0x805d880, 'vdir', 'time_args'),
                                 (0x805a31c, 0x805d886, 'vdir', 'time_args'),
                                 (0x805a324, 0x0, 'vdir', 'format_types'),
                                 (0x805a340, 0x805d88d, 'vdir', 'format_args'),
                                 (0x805a344, 0x805d895, 'vdir', 'format_args'),
                                 (0x805a348, 0x805d89a, 'vdir', 'format_args'),
                                 (0x805a34c, 0x805d8a1, 'vdir', 'format_args'),
                                 (0x805a350, 0x805d8ac, 'vdir', 'format_args'),
                                 (0x805a354, 0x805d8b3, 'vdir', 'format_args'),
                                 (0x805a358, 0x805d8bc, 'vdir', 'format_args'),
                                 (0x805a384, 0x805e7dd, 'vdir', 'when_args'),
                                 (0x805a388, 0x805d8ca, 'vdir', 'when_args'),
                                 (0x805a38c, 0x805d8ce, 'vdir', 'when_args'),
                                 (0x805a390, 0x805d8d4, 'vdir', 'when_args'),
                                 (0x805a394, 0x805d8da, 'vdir', 'when_args'),
                                 (0x805a398, 0x805d860, 'vdir', 'when_args'),
                                 (0x805a39c, 0x805d8dd, 'vdir', 'when_args'),
                                 (0x805a3a0, 0x805d8e5, 'vdir', 'when_args'),
                                 (0x805a3a4, 0x805d8e2, 'vdir', 'when_args'),
                                 (0x805a3ac, 0x0, 'vdir', 'indicator_style_types'),
                                 (0x805a3bc, 0x805d860, 'vdir', 'indicator_style_args'),
                                 (0x805a3c0, 0x805d8e9, 'vdir', 'indicator_style_args'),
                                 (0x805a3c4, 0x805d798, 'vdir', 'indicator_style_args'),
                                 (0x805a3c8, 0x805d78f, 'vdir', 'indicator_style_args'),
                                 (0x805a3d8, 0x805d566, 'vdir', 'time_style_args'),
                                 (0x805a3dc, 0x805d905, 'vdir', 'time_style_args'),
                                 (0x805a3e0, 0x805d90a, 'vdir', 'time_style_args'),
                                 (0x805a3e4, 0x805b6f2, 'vdir', 'time_style_args'),
                                 (0x805a3ec, 0x0, 'vdir', 'time_style_types'),
                                 (0x805a3fc, 0x805d987, 'vdir', 'indicator_name'),
                                 (0x805a400, 0x805d98a, 'vdir', 'indicator_name'),
                                 (0x805a404, 0x805d98d, 'vdir', 'indicator_name'),
                                 (0x805a408, 0x805d76a, 'vdir', 'indicator_name'),
                                 (0x805a40c, 0x805d8da, 'vdir', 'indicator_name'),
                                 (0x805a410, 0x805d990, 'vdir', 'indicator_name'),
                                 (0x805a414, 0x805d993, 'vdir', 'indicator_name'),
                                 (0x805a418, 0x805d996, 'vdir', 'indicator_name'),
                                 (0x805a41c, 0x805d999, 'vdir', 'indicator_name'),
                                 (0x805a420, 0x805d90b, 'vdir', 'indicator_name'),
                                 (0x805a424, 0x805d99c, 'vdir', 'indicator_name'),
                                 (0x805a428, 0x805d99f, 'vdir', 'indicator_name'),
                                 (0x805a42c, 0x805d9a2, 'vdir', 'indicator_name'),
                                 (0x805a430, 0x805d858, 'vdir', 'indicator_name'),
                                 (0x805a434, 0x805d9a5, 'vdir', 'indicator_name'),
                                 (0x805a438, 0x805d9a8, 'vdir', 'indicator_name'),
                                 (0x805a43c, 0x805d9ab, 'vdir', 'indicator_name'),
                                 (0x805a440, 0x805d9ae, 'vdir', 'indicator_name'),
                                 (0x805a444, 0x805d71f, 'vdir', 'indicator_name'),
                                 (0x805a448, 0x805d9b1, 'vdir', 'indicator_name'),
                                 (0x805a44c, 0x805d9b4, 'vdir', 'indicator_name'),
                                 (0x805a450, 0x805d9b7, 'vdir', 'indicator_name'),
                                 (0x805a454, 0x805d9ba, 'vdir', 'indicator_name'),
                                 (0x805a458, 0x805d9bd, 'vdir', 'indicator_name'),
                                 (0x805b524, 0x804e130, 'vdir', 'sort_functions'),
                                 (0x805b528, 0x804e150, 'vdir', 'sort_functions'),
                                 (0x805b52c, 0x804e1b0, 'vdir', 'sort_functions'),
                                 (0x805b530, 0x804e1d0, 'vdir', 'sort_functions'),
                                 (0x805b534, 0x804e230, 'vdir', 'sort_functions'),
                                 (0x805b538, 0x804e250, 'vdir', 'sort_functions'),
                                 (0x805b53c, 0x804e2b0, 'vdir', 'sort_functions'),
                                 (0x805b540, 0x804e2d0, 'vdir', 'sort_functions'),
                                 (0x805b544, 0x804e330, 'vdir', 'sort_functions'),
                                 (0x805b548, 0x804e350, 'vdir', 'sort_functions'),
                                 (0x805b54c, 0x804e3b0, 'vdir', 'sort_functions'),
                                 (0x805b550, 0x804e3d0, 'vdir', 'sort_functions'),
                                 (0x805b554, 0x804e430, 'vdir', 'sort_functions'),
                                 (0x805b558, 0x804e450, 'vdir', 'sort_functions'),
                                 (0x805b55c, 0x804e4b0, 'vdir', 'sort_functions'),
                                 (0x805b560, 0x804e4d0, 'vdir', 'sort_functions'),
                                 (0x805b564, 0x804e530, 'vdir', 'sort_functions'),
                                 (0x805b568, 0x804e550, 'vdir', 'sort_functions'),
                                 (0x805b56c, 0x804e5b0, 'vdir', 'sort_functions'),
                                 (0x805b570, 0x804e5d0, 'vdir', 'sort_functions'),
                                 (0x805b574, 0x804e630, 'vdir', 'sort_functions'),
                                 (0x805b578, 0x804e650, 'vdir', 'sort_functions'),
                                 (0x805b57c, 0x804e6b0, 'vdir', 'sort_functions'),
                                 (0x805b580, 0x804e6d0, 'vdir', 'sort_functions'),
                                 (0x805b584, 0x804e730, 'vdir', 'sort_functions'),
                                 (0x805b588, 0x804e740, 'vdir', 'sort_functions'),
                                 (0x805b58c, 0x804e790, 'vdir', 'sort_functions'),
                                 (0x805b590, 0x804e7a0, 'vdir', 'sort_functions'),
                                 (0x805b5a4, 0x804e7f0, 'vdir', 'sort_functions'),
                                 (0x805b5a8, 0x804e810, 'vdir', 'sort_functions'),
                                 (0x805b5ac, 0x804e870, 'vdir', 'sort_functions'),
                                 (0x805b5b0, 0x804e890, 'vdir', 'sort_functions'),
                                 (0x805b5b4, 0x804e8f0, 'vdir', 'sort_functions'),
                                 (0x805b5b8, 0x804e910, 'vdir', 'sort_functions'),
                                 (0x805b5bc, 0x804e970, 'vdir', 'sort_functions'),
                                 (0x805b5c0, 0x804e990, 'vdir', 'sort_functions'),
                                 (0x805b5c4, 0x804e9f0, 'vdir', 'sort_functions'),
                                 (0x805b5c8, 0x804ea10, 'vdir', 'sort_functions'),
                                 (0x805b5cc, 0x804ea70, 'vdir', 'sort_functions'),
                                 (0x805b5d0, 0x804ea90, 'vdir', 'sort_functions'),
                                 (0x805b5d4, 0x804eaf0, 'vdir', 'sort_functions'),
                                 (0x805b5d8, 0x804eb10, 'vdir', 'sort_functions'),
                                 (0x805b5dc, 0x804eb70, 'vdir', 'sort_functions'),
                                 (0x805b5e0, 0x804eb90, 'vdir', 'sort_functions'),
                                 (0x805b5e4, 0x804ebf0, 'vdir', 'sort_functions'),
                                 (0x805b5e8, 0x804ec10, 'vdir', 'sort_functions'),
                                 (0x805b5ec, 0x804ec70, 'vdir', 'sort_functions'),
                                 (0x805b5f0, 0x804ec90, 'vdir', 'sort_functions'),
                                 (0x805b5f4, 0x804ecf0, 'vdir', 'sort_functions'),
                                 (0x805b5f8, 0x804ed10, 'vdir', 'sort_functions'),
                                 (0x805b5fc, 0x804ed70, 'vdir', 'sort_functions'),
                                 (0x805b600, 0x804ed90, 'vdir', 'sort_functions'),
                                 (0x805e014, 0x0, 'vdir', 'default_tuning'),
                                 (0x805e050, 0x805d722, 'vdir', 'block_size_args'),
                                 (0x805e054, 0x805d7a2, 'vdir', 'block_size_args'),
                                 (0x805e75c, 0x805d7fe, 'vdir', 'quoting_style_args'),
                                 (0x805e760, 0x805e7b0, 'vdir', 'quoting_style_args'),
                                 (0x805e764, 0x805e7b6, 'vdir', 'quoting_style_args'),
                                 (0x805e768, 0x805e7c3, 'vdir', 'quoting_style_args'),
                                 (0x805e76c, 0x805e7d0, 'vdir', 'quoting_style_args'),
                                 (0x805e770, 0x805edb8, 'vdir', 'quoting_style_args'),
                                 (0x805e774, 0x805e7e4, 'vdir', 'quoting_style_args'),
                                 (0x805e778, 0x805e7c9, 'vdir', 'quoting_style_args'),
                                 (0x805e77c, 0x805b6f2, 'vdir', 'quoting_style_args'),
                                 (0x805e780, 0x805e7ec, 'vdir', 'quoting_style_args'),
                                 (0x805e788, 0x0, 'vdir', 'quoting_style_vals'),
                                 (0x805f3a0, 0x0, 'vdir', '__FRAME_END__'),
                                 (0x80611b4, 0x0, 'vdir', '__dso_handle'),
                                 (0x80611bc, 0x805b722, 'vdir', 'color_indicator'),
                                 (0x80611c4, 0x805dca1, 'vdir', 'color_indicator'),
                                 (0x80611d4, 0x805b789, 'vdir', 'color_indicator'),
                                 (0x80611ec, 0x805d420, 'vdir', 'color_indicator'),
                                 (0x80611f4, 0x805d426, 'vdir', 'color_indicator'),
                                 (0x80611fc, 0x805d435, 'vdir', 'color_indicator'),
                                 (0x8061204, 0x805d42c, 'vdir', 'color_indicator'),
                                 (0x806120c, 0x805d432, 'vdir', 'color_indicator'),
                                 (0x8061214, 0x805d432, 'vdir', 'color_indicator'),
                                 (0x806122c, 0x805d438, 'vdir', 'color_indicator'),
                                 (0x8061234, 0x805d42c, 'vdir', 'color_indicator'),
                                 (0x806123c, 0x805d43e, 'vdir', 'color_indicator'),
                                 (0x8061244, 0x805d444, 'vdir', 'color_indicator'),
                                 (0x806124c, 0x805d44a, 'vdir', 'color_indicator'),
                                 (0x8061254, 0x805d450, 'vdir', 'color_indicator'),
                                 (0x806125c, 0x805d456, 'vdir', 'color_indicator'),
                                 (0x8061264, 0x805d45c, 'vdir', 'color_indicator'),
                                 (0x8061274, 0x805d462, 'vdir', 'color_indicator'),
                                 (0x8061280, 0x805d8ef, 'vdir', 'long_time_format'),
                                 (0x8061284, 0x805d8f9, 'vdir', 'long_time_format'),
                                 (0x8061294, 0x805dd7b, 'vdir', 'Version'),
                                 (0x8061298, 0x8050730, 'vdir', 'argmatch_die'),
                                 (0x80612a0, 0x80612a8, 'vdir', 'slotvec'),
                                 (0x80612ac, 0x806231c, 'vdir', 'slotvec0'),
                                 (0x80612e0, 0x8058980, 'vdir', 'obstack_alloc_failed_handler'),
                                 (0x80612e4, 0x0, 'vdir', '__TMC_END__'),
                                 (0x806131c, 0x0, 'vdir', 'completed.7282'),
                                 (0x8061324, 0x0, 'vdir', 'print_dir_name'),
                                 (0x806132c, 0x0, 'vdir', 'current_time'),
                                 (0x8061334, 0x0, 'vdir', 'print_with_color'),
                                 (0x8061335, 0x0, 'vdir', 'directories_first'),
                                 (0x8061336, 0x0, 'vdir', 'check_symlink_mode'),
                                 (0x8061337, 0x0, 'vdir', 'color_symlink_as_referent'),
                                 (0x8061340, 0x0, 'vdir', 'immediate_dirs'),
                                 (0x8061348, 0x0, 'vdir', 'recursive'),
                                 (0x8061350, 0x0, 'vdir', 'dev_ino_obstack'),
                                 (0x8061384, 0x0, 'vdir', 'print_scontext'),
                                 (0x8061385, 0x0, 'vdir', 'print_block_size'),
                                 (0x8061386, 0x0, 'vdir', 'format_needs_stat'),
                                 (0x8061387, 0x0, 'vdir', 'format_needs_type'),
                                 (0x8061388, 0x0, 'vdir', 'dired'),
                                 (0x806138c, 0x0, 'vdir', 'dired_obstack'),
                                 (0x80613b8, 0x0, 'vdir', 'subdired_obstack'),
                                 (0x80613e4, 0x0, 'vdir', 'print_hyperlink'),
                                 (0x80613fc, 0x0, 'vdir', 'used_color'),
                                 (0x806140c, 0x0, 'vdir', 'RFC3986'),
                                 (0x806150c, 0x0, 'vdir', 'caught_signals'),
                                 (0x806158c, 0x0, 'vdir', 'qmark_funny_chars'),
                                 (0x8061594, 0x0, 'vdir', 'sort_reverse'),
                                 (0x8061595, 0x0, 'vdir', 'numeric_ids'),
                                 (0x8061596, 0x0, 'vdir', 'print_inode'),
                                 (0x80615ac, 0x0, 'vdir', 'print_owner'),
                                 (0x80615b8, 0x0, 'vdir', 'output_block_size'),
                                 (0x80615c0, 0x0, 'vdir', 'print_group'),
                                 (0x80615c1, 0x0, 'vdir', 'print_author'),
                                 (0x80615c8, 0x0, 'vdir', 'align_variable_outer_quotes'),
                                 (0x80615d0, 0x0, 'vdir', 'abformat'),
                                 (0x80621d0, 0x0, 'vdir', 'use_abformat'),
                                 (0x80621dc, 0x0, 'vdir', 'print_dir.first'),
                                 (0x80621dd, 0x0, 'vdir', 'cwd_some_quoted'),
                                 (0x80621e4, 0x0, 'vdir', 'any_has_acl'),
                                 (0x8062210, 0x0, 'vdir', 'has_capability_cache.unsupported_device'),
                                 (0x8062218, 0x0, 'vdir', 'getfilecon_cache.unsupported_device'),
                                 (0x8062220, 0x0, 'vdir', 'file_has_acl_cache.unsupported_device'),
                                 (0x806222c, 0x0, 'vdir', 'failed_strcoll'),
                                 (0x80622d4, 0x0, 'vdir', 'ignore_EPIPE'),
                                 (0x80622ec, 0x0, 'vdir', 'default_quoting_options'),
                                 (0x806231c, 0x0, 'vdir', 'slot0'),
                                 ],
            'EmucodeFunctions': [(134582272,), (134583808,), (134552688,), (134556176,), (134548256,), (134575648,),
                                 (134549936,), (134556208,), (134548240,), (134582048,), (134577216,), (134572896,),
                                 (134582304,), (134576528,), (134573136,), (134556288,), (134548224,), (134572128,),
                                 (134568720,), (134572928,), (134575264,), (134577264,), (134573440,), (134575520,),
                                 (134553152,), (134575232,), (134575296,), (134575760,), (134548128,), (134581872,),
                                 (134552608,), (134573232,), (134575488,), (134575744,), (134550208,), (134575904,),
                                 (134576000,), (134548432,), (134572096,), (134559872,), (134548176,), (134575728,),
                                 (134572864,), (134584016,), (134552576,), (134568688,), (134575456,), (134549968,),
                                 (134575712,), (134548144,), (134581952,), (134574848,), (134548352,), (134575184,),
                                 (134582032,), (134549952,), (134572320,), (134553392,), (134582576,), (134573600,),
                                 (134576720,), (134553312,), (134548272,), (134573856,), (134575424,), (134573792,),
                                 (134553568,), (134548304,), (134573408,), (134582160,), (134582416,), (134575392,),
                                 (134582128,), (134583712,), (134573568,), (134582144,), (134575680,), (134519728,),
                                 (134553488,), (134556128,), (134559504,), (134573472,), (134554096,), (134572464,),
                                 (134575616,), (134575872,), (134575552,), (134582112,), (134561824,), (134573264,),
                                 (134561232,), (134574816,), (134547936,), (134582096,), (134552448,), (134552560,),
                                 (134575584,), (134553216,), (134573760,), (134582064,), (134583824,), (134519952,),
                                 (134568352,), (134519472,), (134518848,), (134518128,), (134518112,), (134518736,),
                                 (134518304,), (134518512,), (134518480,), (134518576,), (134519376,), (134518000,),
                                 (134518672,), ]

        }

        for name, valist in ans.items():
            retn = vw.getVaSetRows(name)
            try:
                self.assertEqual(set(retn), set(valist))
            except Exception as e:
                mesg = f'On VaSet {name}, we failed due to: {str(e)}'
                self.fail(mesg)

        self.assertEqual(len(vw.getVaSetRows('CodeFragments')), 213)
        self.assertEqual(len(vw.getVaSetRows('EntryPoints')), 229)

    def test_basic_apis(self):
        '''
        Test a bunch of the simpler workspace APIs
        '''
        vw = self.firefox_vw
        self.assertIsNotNone(vw.parsedbin)
        self.assertEqual(set(['Emulation Anomalies', 'EntryPoints', 'SwitchCases', 'EmucodeFunctions', 'PointersFromFile', 'FuncWrappers', 'CodeFragments', 'DynamicBranches', 'Bookmarks', 'NoReturnCalls', 'DelayImports', 'Library Loads', 'pe:ordinals']), set(vw.getVaSetNames()))

        self.assertEqual((0x14001fa5a, 6, 10, None), vw.getPrevLocation(0x14001fa60))
        self.assertEqual((0x14001fa5a, 6, 10, None), vw.getPrevLocation(0x14001fa60, adjacent=True))

        self.assertEqual(None, vw.getPrevLocation(0x140051fe0, adjacent=True))
        self.assertEqual((0x140051fd0, 8, 9, 'kernel32.lstrlenW'), vw.getPrevLocation(0x140051fe0, adjacent=False))

        self.assertEqual((0x140048ea0, 4, v_const.LOC_OP, envi.ARCH_AMD64), vw.getLocationByName('firefox.__entry'))

        ans = set([5368714880, 5368714906, 5368714941, 5368714975, 5368714999, 5368715022, 5368715029, 5368715044, 5368715058, 5368715070])
        for bva, bsize, bfunc in vw.getFunctionBlocks(0x140001680):
            self.assertIn(bva, ans)
            self.assertEqual(bfunc, 0x140001680)
        locs = [(5368713520, 5, 5, 131072),
                (5368713525, 3, 5, 131072),
                (5368713528, 6, 5, 131076),
                (5368713534, 3, 5, 131072),
                (5368713537, 4, 5, 131072),
                (5368713541, 4, 5, 131072),
                (5368713545, 4, 5, 131072),
                (5368713549, 6, 5, 131076)]
        for loc in vw.getLocationRange(0x140001130, 32):
            self.assertIn(loc, locs)

        # even missing a bunch, there still should be more than 76k here)
        self.assertTrue(len(vw.getLocations()) > 76000)

        # tuples are Name, Number of Locations, Size in bytes, Percentage of space
        ans = {0: ('Undefined', 0, 70828, 18),
               1: ('Num/Int',   715, 3703, 0),
               2: ('String',    265, 6485, 1),
               3: ('Unicode',   174, 5596, 1),
               4: ('Pointer',   361, 2888, 0),
               5: ('Opcode',    72507, 279377, 71),
               6: ('Structure', 1018, 12740, 3),
               7: ('Clsid',     0, 0, 0),
               8: ('VFTable',   0, 0, 0),
               9: ('Import Entry', 370, 2960, 0),
               10: ('Pad',      865, 8639, 2)}
        dist = vw.getLocationDistribution()
        for loctype, locdist in dist.items():
            self.assertEqual(locdist, ans[loctype])

    def test_render(self):
        vw = self.firefox_vw
        cb = vw.getCodeBlock(0x1400017b0)
        rndr = vw.getRenderInfo(cb[v_const.CB_VA], cb[v_const.CB_SIZE])
        self.assertIsNotNone(rndr)
        locs, funcs, names, comments, extras = rndr

        locans = [(5368715184, 1, 5, 131072),
                  (5368715185, 1, 5, 131072),
                  (5368715186, 5, 5, 131072),
                  (5368715191, 5, 5, 131076),
                  (5368715196, 3, 5, 131072),
                  (5368715199, 3, 5, 131072),
                  (5368715202, 8, 5, 131072),
                  (5368715210, 8, 5, 131072),
                  (5368715218, 8, 5, 131072),
                  (5368715226, 7, 5, 131072),
                  (5368715233, 3, 5, 131072),
                  (5368715236, 8, 5, 131072),
                  (5368715244, 8, 5, 131072),
                  (5368715252, 5, 5, 131072),
                  (5368715257, 5, 5, 131076),
                  (5368715262, 3, 5, 131072),
                  (5368715265, 5, 5, 131072),
                  (5368715270, 5, 5, 131072),
                  (5368715275, 9, 5, 131072),
                  (5368715284, 8, 5, 131072),
                  (5368715292, 6, 5, 131072),
                  (5368715298, 3, 5, 131072),
                  (5368715301, 7, 5, 131072),
                  (5368715308, 6, 5, 131076),
                  (5368715314, 5, 5, 131072),
                  (5368715319, 5, 5, 131072),
                  (5368715324, 8, 5, 131072),
                  (5368715332, 5, 5, 131072),
                  (5368715337, 2, 5, 131072),
                  (5368715339, 3, 5, 131072),
                  (5368715342, 6, 5, 131072),
                  (5368715348, 6, 5, 131076),
                  (5368715354, 7, 5, 131072),
                  (5368715361, 6, 5, 131076),
                  (5368715367, 3, 5, 131072),
                  (5368715370, 2, 5, 131112)]

        ops = {5368715184: 'push rsi',
               5368715185: 'push rdi',
               5368715186: 'mov eax,0x00001848',
               5368715191: 'call 0x140048a10',
               5368715196: 'sub rsp,rax',
               5368715199: 'mov rsi,rcx',
               5368715202: 'mov qword [rsp + 6248],rdx',
               5368715210: 'mov qword [rsp + 6256],r8',
               5368715218: 'mov qword [rsp + 6264],r9',
               5368715226: 'mov rax,qword [rip + 346167]',
               5368715233: 'xor rax,rsp',
               5368715236: 'mov qword [rsp + 6208],rax',
               5368715244: 'lea rdi,qword [rsp + 6248]',
               5368715252: 'mov qword [rsp + 56],rdi',
               5368715257: 'call 0x140001a40',
               5368715262: 'mov rcx,qword [rax]',
               5368715265: 'mov qword [rsp + 48],rdi',
               5368715270: 'mov qword [rsp + 32],rsi',
               5368715275: 'mov qword [rsp + 40],0',
               5368715284: 'lea rsi,qword [rsp + 4160]',
               5368715292: 'mov r8d,2048',
               5368715298: 'mov rdx,rsi',
               5368715301: 'mov r9,0xffffffff',
               5368715308: 'call qword [rip + 329734]',
               5368715314: 'lea rax,qword [rsp + 64]',
               5368715319: 'mov qword [rsp + 32],rax',
               5368715324: 'mov dword [rsp + 40],2048',
               5368715332: 'mov ecx,0x0000fde9',
               5368715337: 'xor edx,edx',
               5368715339: 'mov r8,rsi',
               5368715342: 'mov r9d,0xffffffff',
               5368715348: 'call qword [rip + 329182]',
               5368715354: 'lea rcx,qword [rip + 316585]',
               5368715361: 'call qword [rip + 329129]',
               5368715367: 'test rax,rax',
               5368715370: 'jz 0x1400018a3'}

        self.assertEqual(len(locans), len(locs))
        dcdd = 0
        for tupl in locs:
            self.assertIn(tupl, locans)
            if tupl[0] in ops:
                self.assertEqual(repr(vw.parseOpcode(tupl[0])), ops[tupl[0]])
                dcdd += 1
        self.assertEqual(dcdd, len(ops))
        self.assertEqual({5368715184: True}, funcs)
        self.assertEqual({5368715184: 'sub_1400017b0'}, names)

    def test_repr(self):
        vw = self.firefox_vw
        ans = [
            (0x14004d57a, "'MessageBoxW'"),
            (0x14000183c, 'mov dword [rsp + 40],2048'),
            (0x14004ed0a, "u'user32.dll'"),
            (0x140051e10, 'IMPORT: kernel32.LoadLibraryW'),
            (0x140056880, '8 BYTES: 0 (0x00000000)'),
            (0x14004c9b8, "'nsBrowserApp main'"),
            (0xdeadbeef, 'None'),
        ]
        for va, disp in ans:
            self.assertEqual(disp, vw.reprVa(va))

    def test_naughty(self):
        '''
        Test us some error conditions
        '''
        vw = self.firefox_vw
        with self.assertRaises(v_exc.InvalidLocation):
            vw.delLocation(0x51515151)

        with self.assertRaises(v_exc.InvalidFunction):
            vw.setFunctionMeta(0xdeadbeef, 'monty', 'python')

        with self.assertRaises(v_exc.InvalidLocation):
            vw.getLocationByName(0xabad1dea)

    def test_basic_callers(self):
        vw = self.firefox_vw
        self.assertTrue(18000 < len(vw.getXrefs()))
        self.assertEqual(42, len(vw.getImportCallers('kernel32.GetProcAddress')))
        self.assertEqual(9, len(vw.getImportCallers('kernel32.LoadLibraryW')))

    def test_consecutive_jump_table(self):
        primaryJumpOpVa = 0x804c9b6
        secondJumpOpVa = 0x804ca2b

        pfva = self.chgrp_vw.getFunction(primaryJumpOpVa)
        sfva = self.chgrp_vw.getFunction(secondJumpOpVa)
        self.assertEqual(pfva, sfva)
        self.assertTrue(pfva is not None)

        # 2 actual codeblocks and 1 xref to the jumptable itself
        prefs = self.chgrp_vw.getXrefsFrom(primaryJumpOpVa)
        self.assertEqual(len(prefs), 3)
        cmnt = self.chgrp_vw.getComment(0x804c9bd)
        self.assertEqual(cmnt, 'Other Case(s): 2, 6, 8, 11, 15, 20, 21, 34, 38, 40, 47')

        cmnts = self.chgrp_vw.getComments()
        self.assertTrue(len(cmnts) > 1)

        # 13 actual codeblocks and 1 xref to the jumptable itself
        srefs = self.chgrp_vw.getXrefsFrom(secondJumpOpVa)
        self.assertEqual(len(srefs), 14)
        cmnt = self.chgrp_vw.getComment(0x804ca4a)
        self.assertEqual(cmnt, 'Other Case(s): 41')

    def test_jumptable_adjacent_strings(self):
        jmpop = 0x804abc7
        cases = [k[1] for k in self.chgrp_vw.getXrefsFrom(jmpop)]
        self.assertEqual(len(cases), 11)

        casevas = [
            0x804ac76,
            0x804ac88,
            0x804ac98,
            0x804ac86,
            0x804ac8a,
            0x804b671,
            0x804ac56,
            0x804acd6,
            0x804abce,
            0x804abf4,
            0x805162c
        ]
        self.assertEqual(casevas, cases)

        strlocs = [
            (0x8051930, 8, 2, b'literal\x00'),
            (0x8051938, 6, 2, b'shell\x00'),
            (0x805193e, 13, 2, b'shell-always\x00'),
            (0x805194b, 13, 2, b'shell-escape\x00'),
            (0x8051958, 20, 2, b'shell-escape-always\x00'),
            (0x805196c, 8, 2, b'c-maybe\x00'),
            (0x8051974, 8, 2, b'clocale\x00'),
        ]
        for lva, lsize, ltype, lstr in strlocs:
            loctup = self.chgrp_vw.getLocation(lva)
            self.assertEqual(loctup[0], lva)
            self.assertEqual(lsize, loctup[1])
            self.assertEqual(ltype, loctup[2])
            self.assertEqual(lstr, self.chgrp_vw.readMemory(lva, lsize))

        jmpop = 0x804c32b
        cases = [k[1] for k in self.chgrp_vw.getXrefsFrom(jmpop)]
        self.assertEqual(len(cases), 11)
        casevas = [
            0x0804c456,
            0x0804c332,
            0x0804c368,
            0x0804c37e,
            0x0804c394,
            0x0804c3aa,
            0x0804c3da,
            0x0804c3f0,
            0x0804c41f,
            0x0804c406,
            0x08051994
        ]
        self.assertEqual(casevas, cases)

    def test_chgrp_sections(self):
        '''
        Test that section information lines up with what we expect
        '''
        vw = self.chgrp_vw
        segments = set([
            (0x08048154, 0x000013, '.interp', 'chgrp'),
            (0x08048168, 0x000020, '.note.ABI-tag', 'chgrp'),
            (0x08048188, 0x00004c, '.gnu.hash', 'chgrp'),
            (0x080481d4, 0x0004e0, '.dynsym', 'chgrp'),
            (0x080486b4, 0x000343, '.dynstr', 'chgrp'),
            (0x080489f8, 0x00009c, '.gnu.version', 'chgrp'),
            (0x08048a94, 0x000080, '.gnu.version_r', 'chgrp'),
            (0x08048b14, 0x000038, '.rel.dyn', 'chgrp'),
            (0x08048b4c, 0x000218, '.rel.plt', 'chgrp'),
            (0x08048d64, 0x000023, '.init', 'chgrp'),
            (0x08048d90, 0x000440, '.plt', 'chgrp'),
            (0x080491d0, 0x000008, '.plt.got', 'chgrp'),
            (0x080491e0, 0x00745b, '.text', 'chgrp'),
            (0x0805063c, 0x000014, '.fini', 'chgrp'),
            (0x08050650, 0x001be6, '.rodata', 'chgrp'),
            (0x08052238, 0x00006c, '.eh_frame_hdr', 'chgrp'),
            (0x080522a4, 0x000284, '.eh_frame', 'chgrp'),
            (0x08053f0c, 0x000004, '.init_array', 'chgrp'),
            (0x08053f10, 0x000004, '.fini_array', 'chgrp'),
            (0x08053f14, 0x0000e8, '.dynamic', 'chgrp'),
            (0x08053ffc, 0x000004, '.got', 'chgrp'),
            (0x08054000, 0x000118, '.got.plt', 'chgrp'),
            (0x08054118, 0x000050, '.data', 'chgrp'),
            (0x08054170, 0x000184, '.bss', 'chgrp'),
            (0x08048000, 0x00a528, 'PHDR0', 'chgrp'),
            (0x08053f0c, 0x0003e8, 'PHDR1', 'chgrp')
        ])
        self.assertEqual(segments, set(vw.getSegments()))

    def test_chgrp_exports(self):
        '''
        Test that some fo the exports/names made by the elf parser
        aren't accidentally made into functions.
        '''
        vw = self.chgrp_vw
        exports = [
            # .rodata
            (0x08050650, 4, v_const.LOC_POINTER, 'chgrp._fp_hw'),
            (0x08050654, 4, v_const.LOC_POINTER, 'chgrp._IO_stdin_used'),

            # long options is really an array of pointers, but that isn't obvi
            # (0x08050748, 4, v_const.LOC_POINTER, 'chgrp.long_options'),
            #(0x08050850, 0x27, v_const.LOC_STRING, None),

            (0x8054170, 4, v_const.LOC_POINTER, 'chgrp.program_invocation_short_name@@GLIBC_2.0'),
            (0x8054178, 4, v_const.LOC_POINTER, 'chgrp.stderr@@GLIBC_2.0'),
            (0x8054180, 4, v_const.LOC_POINTER, 'chgrp.program_invocation_name@@GLIBC_2.0'),
            (0x8054190, 4, v_const.LOC_POINTER, 'chgrp.optind@@GLIBC_2.0'),
            (0x8054194, 4, v_const.LOC_POINTER, 'chgrp.stdout@@GLIBC_2.0'),
            (0x8054198, 4, v_const.LOC_POINTER, 'chgrp.optarg@@GLIBC_2.0'),
            (0x805419c, 1, v_const.LOC_NUMBER, 'chgrp.completed.7282'),

            # .data pointers/numbers
            (0x805411c, 4, v_const.LOC_POINTER, 'chgrp.__dso_handle'),
            (0x8054120, 4, v_const.LOC_POINTER, 'chgrp.Version'),
            (0x8054124, 4, v_const.LOC_POINTER, 'chgrp.exit_failure'),
            (0x8054128, 4, v_const.LOC_POINTER, 'chgrp.slotvec'),
            (0x805412c, 4, v_const.LOC_POINTER, 'chgrp.nslots'),
            (0x8054130, 8, v_const.LOC_NUMBER, 'chgrp.slotvec0'),  # this one kinda pulls double duty as both 4 and 8....
            # Another horrible little saved space of bytes for....well technically a struct, not that we
            # can easily detect that
            # (0x8054138, 4, v_const.LOC_POINTER, 'chgrp.quote_quoting_options'),
        ]

        for va, size, ltyp, name in exports:
            loc = vw.getLocation(va)
            try:
                self.assertIsNotNone(loc)
                self.assertEqual(loc[v_const.L_VA], va)
                self.assertEqual(loc[v_const.L_SIZE], size)
                self.assertEqual(loc[v_const.L_LTYPE], ltyp)
                self.assertEqual(vw.getName(loc[v_const.L_VA]), name)
            except:
                breakpoint()
                print('wat')

    def test_libfunc_meta_equality(self):
        '''
        both vdir and chgrp have a bunch of library functions in common, and while the addresses
        may be off, other information like # of blocks, # of xrefs from each block, etc. are the
        same
        '''
        vdir_fva = 0x8055bb0
        chgp_fva = 0x804ab30

        vmeta = self.vdir_vw.getFunctionMetaDict(vdir_fva)
        cmeta = self.chgrp_vw.getFunctionMetaDict(chgp_fva)

        self.assertEqual(vmeta['InstructionCount'], cmeta['InstructionCount'])
        self.assertEqual(vmeta['InstructionCount'], 868)

        self.assertEqual(vmeta['BlockCount'], cmeta['BlockCount'])
        self.assertEqual(vmeta['BlockCount'], 261)

        self.assertEqual(vmeta['Size'], cmeta['Size'])
        self.assertEqual(vmeta['Size'], 3154)  # or 877?

        self.assertEqual(vmeta['MnemDist'], cmeta['MnemDist'])

        self.assertEqual(vmeta['Recursive'], cmeta['Recursive'])
        self.assertTrue(vmeta['Recursive'])

    def test_callargs(self):
        answers = [
            (0x804f7f0, 0x8052560, 'cdecl', 3, 'hash_insert_if_absent'),
            (0x804aad0, 0x8055b50, 'cdecl', 5, 'quotearg_buffer'),
            # FIXME: and the problem child continue to suck.
            (0x804ab30, 0x8055bb0, 'cdecl', 7, 'quotearg_buffer_restyled'),
            (0x804b7c0, 0x8056840, 'cdecl', 3, 'quotearg_alloc'),
            (0x804b7e0, 0x8056860, 'cdecl', 4, 'quotearg_alloc_mem'),
            (0x804bc10, 0x8056c90, 'cdecl', 2, 'quotearg_style'),
            (0x804bbd0, 0x8056c50, 'cdecl', 4, 'quotearg_n_style_mem'),
            (0x804bce0, 0x8056d60, 'cdecl', 2, 'quotearg_char'),
            (0x804bc50, 0x8056cd0, 'cdecl', 3, 'quotearg_char_mem'),
            (0x804bae0, 0x8056b60, 'cdecl', 1, 'quotearg'),
            (0x804b930, 0x80569b0, 'cdecl', 2, 'quotearg_n'),
            (0x804bac0, 0x8056b40, 'cdecl', 3, 'quotearg_n_mem'),
            (0x804bd80, 0x8056e00, 'cdecl', 4, 'quotearg_n_custom'),
            (0x804bda0, 0x8056e20, 'cdecl', 5, 'quotearg_n_custom_mem'),
            (0x804be60, 0x8056ee0, 'cdecl', 4, 'quotearg_custom_mem'),
            (0x804be40, 0x8056ec0, 'cdecl', 3, 'quotearg_custom'),
            (0x804bc30, 0x8056cb0, 'cdecl', 3, 'quotearg_style_mem'),
            (0x804bb20, 0x8056ba0, 'cdecl', 3, 'quotearg_n_style'),
            (0x804bb00, 0x8056b80, 'cdecl', 2, 'quotearg_mem'),
            (0x804bd00, 0x8056d80, 'cdecl', 1, 'quotearg_colon'),
            (0x804bd20, 0x8056da0, 'cdecl', 2, 'quotearg_colon_mem'),
            (0x804bd40, 0x8056dc0, 'cdecl', 3, 'quotearg_n_style_colon'),
            (0x804b950, 0x80569d0, 'msfastcall_caller', 4, 'quotearg_n_options'),
            (0x804bee0, 0x8056f60, 'cdecl', 1, 'quote'),
            (0x804bec0, 0x8056f40, 'cdecl', 2, 'quote_n'),
            (0x804be80, 0x8056f00, 'cdecl', 3, 'quote_n_mem'),
            (0x804a7c0, 0x80511d0, 'cdecl', 0, 'close_stdout'),
            (0x804a920, 0x80559a0, 'cdecl', 1, 'set_program_name')
        ]
        for cfva, vfva, cconv, arglen, funcname in answers:
            capi = self.chgrp_vw.getFunctionMeta(cfva, 'api')
            vapi = self.vdir_vw.getFunctionMeta(vfva, 'api')
            self.assertIsNotNone(capi)
            self.assertIsNotNone(vapi)

            self.assertEqual(capi[2], cconv, f'{hex(cfva)}/{hex(vfva)} wanted cconv of {cconv}, got {capi[2]}')
            self.assertEqual(len(capi[4]), arglen)
            self.assertEqual(capi[2], vapi[2])
            self.assertEqual(capi[4], vapi[4])

            cname = self.chgrp_vw.getName(cfva)
            self.assertIsNotNone(cname)
            cname = cname.split('.')[-1]

            vname = self.vdir_vw.getName(vfva)
            self.assertIsNotNone(vname)
            vname = vname.split('.')[-1]

            self.assertEqual(cname, funcname)
            self.assertEqual(vname, cname)

        chgrp_spec = [
            # chgrp specific that I should test
            (0x8049c70, 'msfastcall_caller', 7, 'change_file_owner'),
            (0x80499f0, 'thiscall_caller', 1, 'parse_group'),
            (0x8049b60, 'cdecl', 7, 'chown_files'),
            (0x804a5a0, 'msfastcall_caller', 6, 'describe_change')
        ]

        vw = self.chgrp_vw
        for fva, cconv, arglen, funcname in chgrp_spec:
            self.assertEqual(fva, vw.getFunction(fva))
            api = vw.getFunctionMeta(fva, 'api')
            self.assertEqual(len(api[4]), arglen)
            self.assertEqual(api[2], cconv)

            name = vw.getName(fva)
            self.assertIsNotNone(name)
            name = name.split('.')[-1]
            self.assertEqual(name, funcname)

    def test_non_codeblock(self):
        '''
        So these VAs used to be recognized as codeblocks, which is not correct.
        <va> should be actually be a VA in the middle of a string
        <strtbl> should be a table of *string* pointers, not code block pointers
        '''
        vw = self.vdir_vw
        badva = 0x0805b6f2
        loctup = vw.getLocation(badva, range=False)
        self.assertEqual((134592163, 86, 2, [(134592242, 7)]), loctup)

        # this should directly reflect what's in src/ls.c for color_indicator
        strtbl = 0x805e75c
        loctup = vw.getLocation(strtbl)
        for idx, addr in enumerate(range(strtbl, strtbl + 40, 4)):
            self.assertEqual(vw.getLocation(addr), (addr, 4, 4, None))

    def test_consecutive_jump_table_diff_func(self):
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
            (0x804b00a, 0x804af40, 7),  # 0x8059b78
            (0x804beee, 0x804bee0, 6),
            (0x804d1c9, 0x804d1a0, 6),
            (0x804d28f, 0x804d1a0, 15),  # 0x8059bb8
            (0x804d1e7, 0x804d1a0, 6),
            (0x804d95b, 0x804d820, 3),
            (0x804fd01, 0x804fc70, 9)  # 0x8059fac
        ]

        for i, tablva in enumerate(jumptabl):
            refva = self.vdir_vw.getXrefsTo(tablva)
            self.assertEqual(len(refva), 1)
            refva = refva[0]
            func = self.vdir_vw.getFunction(refva[0])
            refs = self.vdir_vw.getXrefsFrom(refva[0])
            test = ans[i]
            self.assertEqual(refva[0], test[0])
            self.assertEqual(func, test[1])
            self.assertEqual(len(refs), test[2])

    def test_main(self):
        vw = self.chgrp_vw
        self.assertIsNotNone(vw.parsedbin)
        self.assertTrue(vw.isFunction(0x8049650))
        self.assertTrue(vw.getFunction(0x0804a9a0), 0x0804a920)

    def test_viv_bigend(self):
        fd = io.BytesIO(b'ABCDEFG')

        vw = vivisect.VivWorkspace()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.bigend = True
        vw.config.viv.parsers.blob.baseaddr = 0x22220000

        vw.loadFromFd(fd, fmtname='blob')

        self.assertEqual(vw.castPointer(0x22220000), 0x41424344)
        self.assertEqual(vw.parseNumber(0x22220000, 2), 0x4142)

    def test_substrings(self):
        vw = self.firefox_vw
        loc = vw.getLocation(5369027475)
        # real boy test
        self.assertEqual((5369027475, 121, 2, [(5369027482, 114)]), loc)
        rep = vw.readMemory(loc[0], loc[1]).decode('utf-8')
        self.assertEqual(rep, 'https://crash-reports.mozilla.com/submit?id={ec8030f7-c20a-464f-9b0e-13a3a9e97384}&version=78.0.2&buildid=20200708170202\x00')

        subloc = vw.getLocation(5369027585, range=True)
        self.assertEqual((5369027482, 114, 2, []), subloc)

        toploc = vw.getLocation(5369027585, range=False)
        self.assertEqual(toploc, loc)

        # make up some substrings
        base = 5369027475
        s = 'https://crash-reports.mozilla.com/submit?id={ec8030f7-c20a-464f-9b0e-13a3a9e97384}&version=78.0.2&buildid=20200708170202\x00'
        vw.delLocation(base)
        for i in range(1, len(s)):
            vw.makeString(base + len(s) - i)
        vw.makeString(base)
        for i in range(1, len(s)):
            loc = vw.getLocation(base + i, range=True)
            self.assertEqual(loc[0], base + i)
            self.assertEqual(loc[1], len(s) - i)
            self.assertEqual(loc[2], 2)
            self.assertEqual(loc[3], [])
        loc = vw.getLocation(base)
        self.assertTrue(len(loc[v_const.L_TINFO]), 15)
        vw.delLocation(base)
        # be a good citizen and clean up
        vw.makeString(base)

    def test_more_substrings(self):
        vw = self.firefox_vw
        va = 5369027475
        vw.delLocation(va)
        # assert it got deleted
        self.assertIsNone(vw.getLocation(va))

        # little string first
        vw.makeString(va + 7)
        loc = vw.getLocation(va + 7)
        self.assertEqual(loc, (va + 7, 114, 2, []))

        # make the outer string
        wat = vw.makeString(va)
        newloc = vw.getLocation(va)
        self.assertEqual(newloc, (va, 121, 2, [(va+7, 114)]))
        self.assertEqual(wat, newloc)

    def test_make_noname(self):
        vw = self.vdir_vw
        name = 'TheBinaryAnalysisPlantsCrave'
        va = 0x08058691
        vw.makeName(va, name)
        self.assertEqual(vw.getName(va), name)

        vw.makeName(va, None)
        self.assertIsNone(vw.getName(va))
        self.assertEqual(vw.getName(va, smart=True), 'vdir.rpl_mbrtowc+0x31')

        fva = 0x08058660
        oldname = vw.getName(fva)
        self.assertEqual(oldname, 'vdir.rpl_mbrtowc')
        vw.makeName(fva, None)
        noname = 'sub_0%x' % fva
        self.assertEqual(vw.getName(fva), None)
        self.assertEqual(vw.getName(fva, smart=True), noname)
        # set it back just in case
        vw.makeName(fva, oldname)

    def test_graphutil_longpath(self):
        '''
        order matters
        '''
        vw = self.firefox_vw
        g = v_t_graphutil.buildFunctionGraph(vw, 0x1400037c0)
        longpath = []
        longpath = [0x1400037c0, 0x14000382d, 0x1400038a4, 0x140003964, 0x140003994, 0x1400039cc, 0x1400039f6, 0x140003a29, 0x140003a59, 0x140003a83, 0x140003ab3, 0x140003b3b, 0x140003b3e, 0x140003ccd, 0x140003c3c, 0x140003c3f, 0x140003c4c, 0x140003c52, 0x140003c5f, 0x140003c65, 0x140003c72, 0x140003c78, 0x140003c85, 0x140003c8b, 0x140003c98, 0x140003c9e, 0x140003cab, 0x140003cb1, 0x140003cc2, 0x1400038fd, 0x14000390a, 0x140003910, 0x14000392b, 0x140003938, 0x14000393e]
        path = next(v_t_graphutil.getLongPath(g))
        path = [k[0] for k in path]
        self.assertEqual(path, longpath)

    def test_graphutil_getcodepaths(self):
        '''
        In this function, order doesn't matter
        '''
        vw = self.firefox_vw
        g = v_t_graphutil.buildFunctionGraph(vw, 0x140010e60)
        paths = [
            set([0x140010e60, 0x140010e6e, 0x140010e7a, 0x140010e7e, 0x140010e9a, 0x140010ea0]),
            set([0x140010e60, 0x140010e6e, 0x140010e7a, 0x140010e7e, 0x140010e9a, 0x140010ea0, 0x140010f02, 0x140010f13]),
            set([0x140010e60, 0x140010e6e, 0x140010e7a, 0x140010e7e, 0x140010f02, 0x140010f18]),
            set([0x140010e60, 0x140010e6e, 0x140010e7e, 0x140010e9a, 0x140010ea0, 0x140010ef2]),
            set([0x140010e60, 0x140010e6e, 0x140010e7e, 0x140010e9a, 0x140010ea0, 0x140010ef2, 0x140010f02, 0x140010f13]),
            set([0x140010e60, 0x140010e6e, 0x140010e7e, 0x140010ef2, 0x140010f02, 0x140010f18]),
            set([0x140010e60, 0x140010ea0]),
        ]

        pathcount = 0
        genr = v_t_graphutil.getCodePaths(g, loopcnt=0, maxpath=None)
        for path in genr:
            p = set([k[0] for k in path])
            self.assertIn(p, paths)
            pathcount += 1

        self.assertEqual(7, pathcount)

        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x1400110a0))
        thruCnt = glen(v_t_graphutil.getCodePathsThru(g, 0x1400110a0))
        self.assertEqual(21, thruCnt)
        thruCnt = glen(v_t_graphutil.getCodePathsThru(g, 0x1400110a0, maxpath=2))
        self.assertEqual(2, thruCnt)

        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x14001ead0))
        toCnt = glen(v_t_graphutil.getCodePathsTo(g, 0x14001ec2a))
        self.assertEqual(2, toCnt)
        toCnt = glen(v_t_graphutil.getCodePathsTo(g, 0x14001ec2a, maxpath=99))
        self.assertEqual(2, toCnt)


        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x1400019ab))
        fromCnt = glen(v_t_graphutil.getCodePathsFrom(g, 0x1400019ab))
        self.assertEqual(2, fromCnt)
        fromCnt = glen(v_t_graphutil.getCodePathsFrom(g, 0x1400019ab, maxpath=1))
        self.assertEqual(1, fromCnt)

    def test_graphutil_getopsfrompath(self):
        vw = self.firefox_vw
        g = v_t_graphutil.buildFunctionGraph(vw, 0x140048b84)
        path = next(v_t_graphutil.getLongPath(g))

        ops = [
            'push rbx',
            'push rsi',
            'push rdi',
            'sub rsp,64',
            'mov rbx,rcx',
            'call qword [rip + 36451]',
            'mov rsi,qword [rbx + 248]',
            'xor edi,edi',
            'xor r8d,r8d',
            'lea rdx,qword [rsp + 96]',
            'mov rcx,rsi',
            'call qword [rip + 36505]',
            'test rax,rax',
            'jz 0x140048bed',
            'and qword [rsp + 56],0',
            'lea rcx,qword [rsp + 104]',
            'mov rdx,qword [rsp + 96]',
            'mov r9,rax',
            'mov qword [rsp + 48],rcx',
            'mov r8,rsi',
            'lea rcx,qword [rsp + 112]',
            'mov qword [rsp + 40],rcx',
            'xor ecx,ecx',
            'mov qword [rsp + 32],rbx',
            'call qword [rip + 36514]',
            'inc edi', 'cmp edi,2',
            'jl 0x140048b9e',
            'add rsp,64',
            'pop rdi',
            'pop rsi',
            'pop rbx',
            'ret '
        ]
        self.assertEqual(ops, [str(op) for op in v_t_graphutil.getOpsFromPath(vw, g, path)])

    def test_graphutil_coverage(self):
        # FIXME: So fun anecdote for later, originally I wanted to use fva 0x804af40 (parse_ls_colors)
        # out of vdir for this test, but unfortunately, we detect the codeblock of that fva
        # as 0x804af09, which crosses function boundaries into the function decode_switches.
        # Reason being is that at VA 0x804af31, there's a call to error() with value 2 as the first
        # parameter, which according to the man page for error means it should quit out. We don't grab
        # that at codeflow time (because such things would require an emulator with knowledge of calling
        # conventions)
        # But that raises the question if makeFunction should split the codeblock
        # or if we ignore that and just let the CodeBlockGraph stuff do it all for us,
        # or if we should allow codeflow to carry an emulator with it.
        vw = self.vdir_vw
        fvas = [
            0x804c030,
            0x804ce40,
            0x804cec0,
            0x804d1a0,
        ]
        for fva in fvas:
            g = v_t_graphutil.buildFunctionGraph(vw, fva)  # print_dir
            hits = set()
            for path in v_t_graphutil.getCoveragePaths(g):
                for nid, edge in path:
                    hits.add(nid)

            self.assertEqual(len(hits), len(vw.getFunctionBlocks(fva)))
            for nid in hits:
                cb = vw.getCodeBlock(nid)
                self.assertEqual(nid, cb[0])
                self.assertEqual(fva, cb[2])

    def test_firefox_segments(self):
        vw = self.firefox_vw
        ans = {
            'PE_Header': (0x140000000, 0x1000, e_memory.MM_READ),
            '.text': (0x140001000, 0x49000, e_memory.MM_READ | e_memory.MM_EXEC),
            '.rdata': (0x14004a000, 0xc000, e_memory.MM_READ),
            '.data': (0x140056000, 0x3000, e_memory.MM_READ | e_memory.MM_WRITE),
            '.pdata': (0x140059000, 0x3000, e_memory.MM_READ),
            '.00cfg': (0x14005c000, 0x1000, e_memory.MM_READ),
            '.freestd': (0x14005d000, 0x1000, e_memory.MM_READ),
            '.tls': (0x14005e000, 0x1000, e_memory.MM_READ | e_memory.MM_WRITE),
            '.reloc': (0x140092000, 0x1000, e_memory.MM_READ),
        }
        for sva, ssize, sname, sfname in vw.getSegments():
            self.assertEqual(ans[sname][0], sva)
            self.assertEqual(ans[sname][1], ssize)
            self.assertEqual(sfname, 'firefox')

            mva, msize, flags, mfname = vw.getMemoryMap(sva)
            self.assertEqual(mva, sva)
            self.assertEqual(msize, ssize)
            self.assertEqual(flags, ans[sname][2])
            self.assertEqual(mfname, sfname)

    def test_opcache(self):
        vw = self.firefox_vw
        self.assertGreater(len(vw._op_cache), 0)
        vw.clearOpcache()
        self.assertEqual(len(vw._op_cache), 0)

        op = vw.parseOpcode(0x140010ef2, skipcache=True)
        self.assertEqual(str(op), 'mov rax,qword [rsi + 56]')
        self.assertEqual(len(vw._op_cache), 0)

        op = vw.parseOpcode(0x140010ef2)
        self.assertEqual(str(op), 'mov rax,qword [rsi + 56]')
        self.assertEqual(len(vw._op_cache), 1)

    def test_function_thunks(self):
        vw = self.firefox_vw

        thunks = set([fva for fva in vw.getFunctions() if vw.isFunctionThunk(fva)])
        impthunk = [0x140049920, 0x1400498a0, 0x140049ba0, 0x140049b10, 0x140049bb0, 0x140049c30, 0x140049b30,
                    0x140049ab0, 0x1400498b0, 0x140049830, 0x140049930, 0x140049a30, 0x1400497b0, 0x140049730,
                    0x140049bc0, 0x140049940, 0x1400498c0, 0x140049ac0, 0x140049c40, 0x140049a40, 0x1400497c0,
                    0x140049840, 0x14001d2c0, 0x140049740, 0x140049ad0, 0x140049850, 0x14001d050, 0x140049bd0,
                    0x140049950, 0x1400497d0, 0x1400498d0, 0x140049750, 0x140049c50, 0x140049b50, 0x140049ae0,
                    0x140049be0, 0x1400498e0, 0x140049860, 0x14000dde0, 0x140049b60, 0x1400497e0, 0x140049760,
                    0x140015c60, 0x140049af0, 0x1400499f0, 0x1400498f0, 0x1400496f0, 0x140049870, 0x1400497f0,
                    0x140049770, 0x140049bf0, 0x140049b80, 0x140049780, 0x140049a00, 0x140049900, 0x140049700,
                    0x140049800, 0x140049880, 0x140049c00, 0x140049b00, 0x140049a10, 0x140049790, 0x140049810,
                    0x140049a90, 0x140049710, 0x14001ef10, 0x140049890, 0x140049910, 0x140049b90, 0x140049c10,
                    0x140049b40, 0x140049aa0, 0x1400497a0, 0x140049720, 0x140049820, 0x140049a20]

        self.assertEqual(thunks, set(impthunk))
