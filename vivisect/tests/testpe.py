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

    def test_emulation_vaset(self):
        vw = self.vw_psexec
        funcs = set([4281345, 4259207, 4221834, 4289292, 4280642, 4287725, 4293008, 4199824, 4221844, 4282646, 4280472, 4280730, 4268701, 4221854, 4221727, 4290211, 4282788, 4221864, 4221737, 4293319, 4294188, 4221874, 4259229, 4294064, 4284338, 4221747, 4291252, 4290121, 4289976, 4289721, 4239035, 4221757, 4289086, 4293695, 4291392, 4290370, 4221767, 4289993, 4281548, 4288719, 4293840, 4221777, 4259282, 4290228, 4287692, 4259158, 4282944, 4285732, 4221787, 4241818, 4291296, 4290145, 4198480, 4280554, 4280685, 4198864, 4221807, 4281584, 4290929, 4282482, 4287859, 4259060, 4269557, 4293495, 4289528, 4221690, 4288749, 4208512, 4209088, 4208800, 4211088, 4209120, 4209376, 4211616, 4209504, 4216112, 4209600, 4208992, 4210848, 4206416, 4206032, 4221654, 4233944, 4221660, 4207328, 4209632, 4213200, 4221666, 4231139, 4221797, 4221672, 4210288, 4209328])
        for fva in funcs:
            self.assertEquals(fva, vw.getFunction(fva))

        # if we reorder analysis passes or new ones, this might change, and that's okay.
        # this is more designed to be a smoke test that we actually get a populated vaset
        emufuncs = vw.getVaSet('EmucodeFunctions')
        self.assertTrue(len(emufuncs) > 0)
        e = set(emufuncs.keys())
        f = set(funcs)
        self.assertTrue(f.intersection(e) == f)
