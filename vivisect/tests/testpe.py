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
