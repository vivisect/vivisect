import io
import unittest

import vivisect
import vivisect.tests.helpers as helpers


class VivisectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chgrp_vw = helpers.getTestWorkspace('linux', 'i386', 'chgrp.llvm')
        cls.vdir_vw = helpers.getTestWorkspace('linux', 'i386', 'vdir.llvm')

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
