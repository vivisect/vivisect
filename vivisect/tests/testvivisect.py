import io
import logging
import unittest

import envi

import vivisect
import vivisect.exc as v_exc
import vivisect.const as v_const
import vivisect.tools.graphutil as v_t_graphutil

import vivisect.tests.helpers as helpers


logger = logging.getLogger(__name__)


def glen(g):
    return len([x for x in g])


class VivisectTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.chgrp_vw = helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')
        cls.vdir_vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')
        cls.gcc_vw = helpers.getTestWorkspace('linux', 'amd64', 'gcc-7')

    def test_basic_apis(self):
        '''
        Test a bunch of the simpler workspace APIs
        '''
        vw = self.gcc_vw
        self.assertEqual(set(['Emulation Anomalies', 'EntryPoints', 'WeakSymbols', 'FileSymbols', 'SwitchCases', 'EmucodeFunctions', 'PointersFromFile', 'FuncWrappers', 'CodeFragments', 'DynamicBranches', 'Bookmarks', 'NoReturnCalls']), set(vw.getVaSetNames()))

        self.assertEqual((0x405d10, 5, 5, 0x20004), vw.getPrevLocation(0x405d15))

        self.assertEqual(None, vw.getPrevLocation(0x405c10, adjacent=True))
        self.assertEqual((0x405c09, 5, 5, 0x20009), vw.getPrevLocation(0x405c10, adjacent=False))
        self.assertEqual((0x449e10, 1, v_const.LOC_OP, envi.ARCH_AMD64), vw.getLocationByName('gcc_7.main'))

        # self.assertEqual(set([0x4357d9, 0x435849, 0x4358bd]), vw.getFunctionBlocks(0x4357d9))
        ans = set([0x468820, 0x46882f, 0x40aba1, 0x46883c, 0x40ab96, 0x46884e, 0x468838])
        for bva, bsize, bfunc in vw.getFunctionBlocks(0x00468820):
            self.assertIn(bva, ans)
            self.assertEqual(bfunc, 0x00468820)
        locs = [(4622364, 4, 0, None),
                (4622368, 1, 5, 131072),
                (4622369, 6, 5, 131072),
                (4622375, 2, 5, 131072),
                (4622377, 6, 5, 131112),
                (4622383, 5, 5, 131076),
                (4622388, 2, 5, 131072),
                (4622390, 2, 5, 131112),
                (4622392, 2, 5, 131072),
                (4622394, 1, 5, 131072),
                (4622395, 1, 5, 131089)]
        for loc in vw.getLocationRange(0x46881c, 32):
            self.assertIn(loc, locs)

        # even missing a bunch, there still should be more than 1000 here)
        self.assertTrue(len(vw.getLocations()) > 1000)

        # tuples are Name, Number of Locations, Size in bytes, Percentage of space
        ans = {0: ('Undefined', 0, 517666, 49),
               1: ('Num/Int', 271, 1724, 0),
               2: ('String', 4054, 153424, 14),
               3: ('Unicode', 0, 0, 0),
               4: ('Pointer', 5376, 43008, 4),
               5: ('Opcode', 79489, 323542, 30),
               6: ('Structure', 496, 11544, 1),
               7: ('Clsid', 0, 0, 0),
               8: ('VFTable', 0, 0, 0),
               9: ('Import Entry', 141, 1128, 0),
               10: ('Pad', 0, 0, 0)}
        dist = vw.getLocationDistribution()
        for loctype, locdist in dist.items():
            self.assertEqual(locdist, ans[loctype])

    def test_render(self):
        vw = self.gcc_vw
        cb = vw.getCodeBlock(0x0046ec30)
        rndr = vw.getRenderInfo(cb[v_const.CB_VA] - 0x20, cb[v_const.CB_SIZE] + 0x20)
        self.assertIsNotNone(rndr)
        locs, funcs, names, comments, extras = rndr

        locans = [(4647952, 2, 5, 131072),
                  (4647954, 1, 5, 131072),
                  (4647955, 2, 5, 131112),
                  (4647957, 5, 5, 131072),
                  (4647962, 3, 5, 131072),
                  (4647965, 2, 5, 131072),
                  (4647967, 5, 5, 131076),
                  (4647972, 3, 5, 131072),
                  (4647975, 1, 5, 131072),
                  (4647976, 1, 5, 131089),
                  (4647977, 7, 0, None),
                  (4647984, 2, 5, 131072),
                  (4647986, 1, 5, 131072),
                  (4647987, 2, 5, 131072),
                  (4647989, 1, 5, 131072),
                  (4647990, 3, 5, 131072),
                  (4647993, 4, 5, 131072),
                  (4647997, 4, 5, 131072),
                  (4648001, 5, 5, 131072),
                  (4648006, 6, 5, 131112)]

        ops = {4647952: 'test esi,esi',
               4647954: 'push rbx',
               4647955: 'jns 0x0046ec1a',
               4647957: 'mov esi,2',
               4647962: 'mov rbx,qword [rdi]',
               4647965: 'mov edi,esi',
               4647967: 'call 0x0046f3b0',
               4647972: 'mov byte [rbx + 59],al',
               4647975: 'pop rbx',
               4647976: 'ret ',
               4647984: 'push r14',
               4647986: 'push rbp',
               4647987: 'mov ebp,esi',
               4647989: 'push rbx',
               4647990: 'mov rsi,rdx',
               4647993: 'sub rsp,96',
               4647997: 'cmp r8d,11',
               4648001: 'mov qword [rsp + 16],rcx',
               4648006: 'jz 0x0041773f'}

        self.assertEqual(len(locans), len(locs))
        dcdd = 0
        for tupl in locs:
            self.assertIn(tupl, locans)
            if tupl[0] in ops:
                self.assertEqual(repr(vw.parseOpcode(tupl[0])), ops[tupl[0]])
                dcdd += 1
        self.assertEqual(dcdd, len(ops))
        self.assertEqual({0x46ec10: True, 0x46ec30: True}, funcs)
        self.assertEqual({0x46ec10: 'sub_0046ec10', 0x46ec30: 'sub_0046ec30'}, names)
        self.assertEqual({0x46ec1f: 'sub_0046f3b0(0x4156b00f,0x4156b00f,0x4156500f,0x4156300f,0x4156f00f,0x4157100f)'}, comments)

    def test_repr(self):
        vw = self.gcc_vw
        ans = [
            (5040784, "'Perform IPA Value Range Propagation.\\x00'"),
            (4853125, "'-fira-algorithm=\\x00'"),
            (5040824, "'-fira-algorithm=[CB|priority]\\tSet the used IRA algorithm.\\x00'"),
            (4853142, "'-fira-hoist-pressure\\x00'"),
            (4853163, "'-fira-loop-pressure\\x00'"),
            (4853183, "'-fira-region=\\x00'"),
            (5041032, "'-fira-region=[one|all|mixed]\\tSet regions for IRA.\\x00'"),
            (4853197, "'-fira-share-save-slots\\x00'"),
            (5041088, "'Share slots for saving different hard registers.\\x00'"),
            (4853220, "'-fira-share-spill-slots\\x00'"),
            (5041144, "'Share stack slots for spilled pseudo-registers.\\x00'"),
            (4853244, "'-fira-verbose=\\x00'"),
            (5041264, "'-fisolate-erroneous-paths-attribute\\x00'"),
            (7345392, '4 BYTES: 0 (0x0000)'),
            (7345376, '8 BYTES: 0 (0x00000000)'),
            (5122144, '16 BYTES: 21528975894082904090066538856997790465 (0x1032547698badcfeefcdab8967452301)'),
            (7346240, 'BYTE: 0 (0x0)'),
            (7331776, 'IMPORT: *.__pthread_key_create'),
            (7331784, 'IMPORT: *.__libc_start_main'),
            (7331792, 'IMPORT: *.calloc'),
            (7331800, 'IMPORT: *.__gmon_start__'),
            (7331808, 'IMPORT: *.stderr'),
            (7331864, 'IMPORT: *.__strcat_chk'),
            (7331872, 'IMPORT: *.__uflow'),
            (7331880, 'IMPORT: *.mkstemps'),
            (7331888, 'IMPORT: *.getenv'),
            (7331896, 'IMPORT: *.dl_iterate_phdr'),
            (7331904, 'IMPORT: *.__snprintf_chk'),
            (7331912, 'IMPORT: *.free'),
            (4697393, 'mov rdx,qword [rsp + 8]'),
            (4697398, 'jmp 0x0047ab49'),
            (4749920, 'mov qword [rdi + 152],rsi'),
            (4749927, 'ret '),
            (4698912, 'sub rsp,8'),
            (4698916, 'call 0x0047b310'),
            (4698921, 'mov rdi,rax'),
            (4698924, 'call 0x0047b2f0'),
            (4698929, 'cs: nop word [rax + rax]'),
            (4698939, 'nop dword [rax + rax]'),
            (4698944, 'test rdi,rdi'),
            (4698947, 'push rbx'),
            (4698948, 'jz 0x0047b361'),
            (4698950, 'mov rbx,rdi'),
            (4698953, 'call 0x0047a450'),
            (4698958, 'mov rax,0xb8b1aabcbcd4d500'),
        ]
        for va, disp in ans:
            self.assertEqual(disp, vw.reprVa(va))

    def test_naughty(self):
        '''
        Test us some error conditions
        '''
        vw = self.gcc_vw
        with self.assertRaises(v_exc.InvalidLocation):
            vw.delLocation(0x51515151)

        with self.assertRaises(v_exc.InvalidFunction):
            vw.setFunctionMeta(0xdeadbeef, 'monty', 'python')

        with self.assertRaises(v_exc.InvalidLocation):
            vw.getLocationByName(0xabad1dea)

    def test_basic_callers(self):
        vw = self.gcc_vw
        self.assertTrue(29000 < len(vw.getXrefs()))
        self.assertEqual(2, len(vw.getImportCallers('gcc_7.plt_calloc')))
        self.assertEqual(1, len(vw.getImportCallers('gcc_7.plt_ioctl')))
        # uck. TODO: symbolik switchcase
        # self.assertEqual(14, len(vw.getImportCallers('gcc_7.plt_exit')))

        #self.assertEqual(set([0x408de9, 0x408dfd, 0x435198, 0x43811d]),
        self.assertEqual(set([0x408de9, 0x408dfd, 0x435198]),
                         set(vw.getImportCallers(vw.getName(0x402d20))))
        self.assertEqual(set([0x4495de, 0x4678b1]), set(vw.getImportCallers(vw.getName(0x402d80))))

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
        cases = list(map(lambda k: k[1], self.chgrp_vw.getXrefsFrom(jmpop)))
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
            (0x8051930, 8, 2, 'literal\x00'),
            (0x8051938, 6, 2, 'shell\x00'),
            (0x805193e, 13, 2, 'shell-always\x00'),
            (0x805194b, 13, 2, 'shell-escape\x00'),
            (0x8051958, 20, 2, 'shell-escape-always\x00'),
            (0x805196c, 8, 2, 'c-maybe\x00'),
            (0x8051974, 8, 2, 'clocale\x00'),
        ]
        for lva, lsize, ltype, lstr in strlocs:
            loctup = self.chgrp_vw.getLocation(lva)
            self.assertEqual(loctup[0], lva)
            self.assertEqual(lsize, loctup[1])
            self.assertEqual(ltype, loctup[2])
            self.assertEqual(lstr, self.chgrp_vw.readMemory(lva, lsize))

        jmpop = 0x804c32b
        cases = list(map(lambda k: k[1], self.chgrp_vw.getXrefsFrom(jmpop)))
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
            # quotearg_buffer_restyled, the problem child
            # there should be 9 and an msfastcaller here, but meta registers are a nightmare
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

            self.assertEqual(capi[2], cconv)
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
        badva = 0x0805b6f2
        loctup = self.vdir_vw.getLocation(badva)
        self.assertEqual((134592163, 86, 2, None), loctup)

        strtbl = 0x805e75c
        loctup = self.vdir_vw.getLocation(strtbl)
        self.assertEqual(loctup, (strtbl, 4, 4, None))

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
            (0x804b00a, 0x804a210, 7),  # 0x8059b78
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
        self.assertTrue(vw.isFunction(0x8049650))
        self.assertTrue(vw.getFunction(0x0804a9a0), 0x0804a920)

    def test_viv_bigend(self):
        fd = io.StringIO(u'ABCDEFG')

        vw = vivisect.VivWorkspace()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.bigend = True
        vw.config.viv.parsers.blob.baseaddr = 0x22220000

        vw.loadFromFd(fd, fmtname='blob')

        self.assertEqual(vw.castPointer(0x22220000), 0x41424344)
        self.assertEqual(vw.parseNumber(0x22220000, 2), 0x4142)

    def test_posix_impapi(self):
        pass

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
        vw = self.gcc_vw
        # TODO: symbolik switchcase
        # g = v_t_graphutil.buildFunctionGraph(vw, 0x445db6)
        # longpath = [0x445db6, 0x445dc3, 0x445dd7, 0x445deb, 0x445dfc, 0x445e01, 0x445e0b, 0x445ddc, 0x445e11, 0x445e20, 0x445e2c, 0x445e30, 0x445e4b, 0x445e5b, 0x445e72, 0x445e85, 0x445e85, 0x445ea1, 0x445ea3, 0x445eae, 0x445ebb, 0x445df5, 0x445ec2]
        # path = next(v_t_graphutil.getLongPath(g))
        # self.assertEqual(longpath, map(lambda k: k[0], path))

        g = v_t_graphutil.buildFunctionGraph(vw, 0x405c10)
        longpath=[0x405c10, 0x405c48, 0x405ca6, 0x405cb0, 0x405cc3, 0x405c4e, 0x405c57, 0x405c5c, 0x405c6b, 0x405cd4, 0x405ce4, 0x405c80, 0x405c8c, 0x405cf6, 0x405c92]
        path = next(v_t_graphutil.getLongPath(g))
        path = map(lambda k: k[0], path)
        self.assertEqual(path, longpath)

    def test_graphutil_getcodepaths(self):
        '''
        In this function, order doesn't matter
        '''
        vw = self.gcc_vw
        g = v_t_graphutil.buildFunctionGraph(vw, 0x456190)
        paths = [
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x45621c, 0x456240, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x45621c, 0x40aa97, 0x4561ea, 0x4561ef, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x45621c, 0x40aa97, 0x4561ea, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x4561c2, 0x4561d0, 0x4561ea, 0x4561ef, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x4561c2, 0x4561d0, 0x4561ea, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x4561c2, 0x40aa85, 0x40aa8d, 0x4561d0, 0x4561ea, 0x4561ef, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x4561c2, 0x40aa85, 0x40aa8d, 0x4561d0, 0x4561ea, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x456216, 0x4561c2, 0x40aa85, 0x40aab9, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x45621c, 0x456240, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x45621c, 0x40aa97, 0x4561ea, 0x4561ef, 0x4561fa, 0x456242]),
            set([0x456190, 0x4561ba, 0x456202, 0x45621c, 0x40aa97, 0x4561ea, 0x4561fa, 0x456242]),
            set([0x456190, 0x456242]),
        ]

        pathcount = 0
        genr = v_t_graphutil.getCodePaths(g, loopcnt=0, maxpath=None)
        for path in genr:
            p = set(map(lambda k: k[0], path))
            self.assertIn(p, paths)
            pathcount += 1

        self.assertEqual(12, pathcount)

        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x0041a766))
        thruCnt = glen(v_t_graphutil.getCodePathsThru(g, 0x0041a766))
        self.assertEqual(2, thruCnt)
        thruCnt = glen(v_t_graphutil.getCodePathsThru(g, 0x0041a766, maxpath=1))
        self.assertEqual(1, thruCnt)

        # this will not be true for all examples, but for this function it is
        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x0041a77d))
        toCnt = glen(v_t_graphutil.getCodePathsTo(g, 0x0041a77d))
        self.assertEqual(2, toCnt)
        toCnt = glen(v_t_graphutil.getCodePathsTo(g, 0x0041a77d, maxpath=99))
        self.assertEqual(2, toCnt)

        g = v_t_graphutil.buildFunctionGraph(vw, vw.getFunction(0x004042eb))
        fromCnt = glen(v_t_graphutil.getCodePathsFrom(g, 0x004042eb))
        self.assertEqual(8, fromCnt)
        fromCnt = glen(v_t_graphutil.getCodePathsFrom(g, 0x004042eb, maxpath=3))
        self.assertEqual(3, fromCnt)

    def test_graphutil_getopsfrompath(self):
        vw = self.gcc_vw
        g = v_t_graphutil.buildFunctionGraph(vw, 0x414a2a)
        path = next(v_t_graphutil.getLongPath(g))

        ops = [
            'push r14',
            'push r13',
            'mov r13,rdx',
            'push r12',
            'push rbp',
            'mov r12,rsi',
            'push rbx',
            'mov rbx,rdi',
            'sar r12,3',
            'mov rbp,rsi',
            'mov edx,r12d',
            'mov r14d,ecx',
            'sub rsp,16',
            'mov rdi,qword [rdi + 48]',
            'mov qword [rsp + 8],rsi',
            'lea rsi,qword [rsp + 8]',
            'call 0x00414962',
            'cmp qword [rax],0',
            'jz 0x00414abc',
            'mov rdx,qword [rax + 8]',
            'mov rax,qword [rdx]',
            'cmp r13,rax',
            'jbe 0x00414a85',
            'mov edx,0x004d76b0',
            'mov esi,151',
            'mov edi,0x004d7534',
            'call 0x0041806c',
            'sub rax,r13',
            'test r14l,r14l',
            'mov qword [rdx],rax',
            'jz 0x00414abc',
            'mov rbx,qword [rbx + 48]',
            'lea rsi,qword [rsp + 8]',
            'xor ecx,ecx',
            'mov edx,r12d',
            'mov qword [rsp + 8],rbp',
            'mov rdi,rbx',
            'call 0x004154ec',
            'cmp qword [rax],0',
            'jz 0x00414abc',
            'mov qword [rax],1',
            'inc qword [rbx + 24]',
            'add rsp,16',
            'pop rbx',
            'pop rbp',
            'pop r12',
            'pop r13',
            'pop r14',
            'ret '
        ]
        self.assertEqual(ops, map(str, v_t_graphutil.getOpsFromPath(vw, g, path)))
