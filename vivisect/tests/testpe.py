import unittest

import PE
import vivisect.cli as viv_cli
import vivisect.const as viv_con
import vivisect.tests.helpers as helpers


class PETests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(PETests, cls).setUpClass()
        cls.psexec_fn = helpers.getTestPath('windows', 'i386', 'PsExec.exe')
        cls.vw_psexec = viv_cli.VivCli()
        cls.vw_psexec.loadFromFile(cls.psexec_fn)
        cls.vw_psexec.analyze()

    def test_function_disasm(self):
        disasm = [
            (0x4028e0, 1, 'push ebp'),
            (0x4028e1, 2, 'mov ebp,esp'),
            (0x4028e3, 3, 'sub esp,8'),
            (0x4028e6, 1, 'push esi'),
            (0x4028e7, 3, 'mov esi,dword [ebp + 8]'),
            (0x4028ea, 1, 'push edi'),
            (0x4028eb, 2, 'push 64'),
            (0x4028ed, 1, 'push esi'),
            (0x4028ee, 6, 'call dword [0x0041a168]'),
            (0x4028f4, 5, 'push 0x00420944'),
            (0x4028f9, 5, 'push 0x0042095c'),
            (0x4028fe, 6, 'call dword [0x0041a178]'),
            (0x402904, 1, 'push eax'),
            (0x402905, 6, 'call dword [0x0041a18c]'),
            (0x40290b, 2, 'mov edi,eax'),
            (0x40290d, 2, 'test edi,edi'),
            (0x40290f, 2, 'jz 0x00402935'),
        ]

        cbva = 0x4028e0
        self.assertEquals(self.vw_psexec.getFunction(cbva), cbva)
        for (va, size, inst) in disasm:
            lva, lsize, ltype, linfo = self.vw_psexec.getLocation(cbva)
            op = self.vw_psexec.parseOpcode(lva)
            self.assertEquals(ltype, viv_con.LOC_OP)
            self.assertEquals(size, lsize)
            self.assertEquals(str(op), inst)
            cbva += size

    def test_export_by_name(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_name.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEquals(len(export_list), 2, "expecting 2 exported functions")
        self.assertEquals(export_list[0][1], 0, "exported function with ordinal 0 not found")
        self.assertEquals(export_list[0][2], "Func1", "exported function with name 'Func1' not found")
        self.assertEquals(export_list[1][1], 1, "exported function with ordinal 1 not found")
        self.assertEquals(export_list[1][2], "Func2", "exported function with name 'Func2' not found")

    def test_export_by_ordinal_base_01(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_01.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEquals(len(export_list), 2, "expecting 2 exported functions")
        self.assertEquals(export_list[0][1], 1, "exported function with ordinal 1 not found")
        self.assertEquals(export_list[1][1], 2, "exported function with ordinal 2 not found")

    def test_export_by_ordinal_base_45(self):
        file_path = helpers.getTestPath('windows', 'i386', 'export_by_ordinal_base_45.dll')
        pe = PE.peFromFileName(file_path)
        export_list = pe.getExports()
        self.assertEquals(len(export_list), 2, "expecting 2 exported functions")
        self.assertEquals(export_list[0][1], 45, "exported function with ordinal 45 not found")
        self.assertEquals(export_list[1][1], 55, "exported function with ordinal 55 not found")

    def test_pe_metainfo(self):
        self.assertEquals(self.vw_psexec.getMeta('Architecture'), 'i386')
        self.assertEquals(self.vw_psexec.getMeta('DefaultCall'), 'cdecl')
        self.assertEquals(self.vw_psexec.getMeta('Format'), 'pe')
        self.assertEquals(self.vw_psexec.getMeta('Platform'), 'windows')
        self.assertEquals(self.vw_psexec.getMeta('StorageModule'), 'vivisect.storage.basicfile')
        self.assertEquals(self.vw_psexec.getMeta('StorageName'), self.psexec_fn + '.viv')

        self.assertEquals(len(self.vw_psexec.getMeta('NoReturnApis')), 5)
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.exitprocess'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.exitthread'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['kernel32.fatalexit'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['ntdll.rtlexituserthread'])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApis']['ntoskrnl.kebugcheckex'])

        self.assertEquals(len(self.vw_psexec.getMeta('NoReturnApisVa')), 2)
        self.assertTrue(self.vw_psexec.metadata['NoReturnApisVa'][4301248])
        self.assertTrue(self.vw_psexec.metadata['NoReturnApisVa'][4301300])

    def test_string_locations(self):
        strRefs = self.vw_psexec.getLocations(ltype=viv_con.LOC_STRING)
        uniRefs = self.vw_psexec.getLocations(ltype=viv_con.LOC_UNI)
        # self.assertEquals(len(strRefs), )
        # self.assertEquals(len(uniRefs), )

    def test_pointer_locations(self):
        pass
