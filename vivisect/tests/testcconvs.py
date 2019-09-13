import unittest

import vivisect.tests.helpers as helpers


class CallConvTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lvw = helpers.getTestWorkspace('linux', 'i386', 'cconv.elf')

    def test_linux_regparm_3(self):
        fva = 0x080483e0
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'bfastcall')
        self.assertEqual(len(args), 3)
        self.assertIn(('int', 'eax'), args)
        self.assertIn(('int', 'edx'), args)
        self.assertIn(('int', 'ecx'), args)

        fva = 0x08048470
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'bfastcall')
        self.assertEqual(len(args), 3)
        self.assertIn(('int', 'eax'), args)
        self.assertIn(('int', 'edx'), args)
        self.assertIn(('int', 'ecx'), args)

    def test_linux_regparm_2(self):
        fva = 0x08048430
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'bfastcall')
        self.assertEqual(len(args), 2)
        self.assertIn(('int', 'eax'), args)
        self.assertIn(('int', 'edx'), args)

    def test_linux_fastcall(self):
        fva = 0x08048580
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'fastcall')
        self.assertEqual(len(args), 2)
        self.assertIn(('int', 'ecx'), args)
        self.assertIn(('int', 'edx'), args)

    def test_linux_stdcall(self):
        fva = 0x08048500
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'stdcall')
        self.assertEqual(len(args), 2)
        self.assertIn(('int', 'arg0'), args)
        self.assertIn(('int', 'arg1'), args)

    def test_linux_cdecl(self):
        fva = 0x08048540
        rettype, retname, callconv, funcname, args = self.lvw.getFunctionMeta(fva, 'api')
        self.assertEqual(callconv, 'cdecl')
        self.assertEqual(len(args), 1)
        self.assertEqual(('int', 'arg0'), args[0])
