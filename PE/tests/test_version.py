import os
import unittest

import PE
import vivisect.tests.vivbins as vivbins

vs_version = {
'CompanyName': u'Microsoft Corporation',
'FileDescription': u'Windows NET Device Class Co-Installer for Wireless WAN',
'FileVersion': u'08.01.02.00 (win7_rtm.090713-1255)',
'InternalName': u'wwaninst.dll',
'LegalCopyright': u'\xa9 Microsoft Corporation. All rights reserved.',
'OriginalFilename': u'wwaninst.dll',
'ProductName': u'Microsoft\xae Windows\xae Operating System',
'ProductVersion': u'08.01.02.00',
'Translation': 78644233,
}


class PEResourceTest(unittest.TestCase):

    @vivbins.require
    def test_pe_vsersion(self):
        fpath = os.path.join('test_pe','bins','wwaninst.dll')
        pe = PE.peFromFileName(fpath)
        vs = pe.getVS_VERSIONINFO()
        self.assertIsNotNone(vs)
        keys = vs.getVersionKeys()
        self.assertEqual(len(keys), len(vs_version))
        for key in vs.getVersionKeys():
            self.assertEqual(vs_version.get(key), vs.getVersionValue(key))

    def test_export_by_name(self):
        fpath = os.path.join('bins','export_by_name.dll')
        pe = PE.peFromFileName(fpath)
        exportlist = pe.getExports()
        self.assertEquals(len(exportlist), 2, "expecting 2 exported functions")
        self.assertEquals(exportlist[0][1], 0, "exported function with ordinal 0 not found")
        self.assertEquals(exportlist[0][2], "Func1", "exported function with name 'Func1' not found")
        self.assertEquals(exportlist[1][1], 1, "exported function with ordinal 1 not found")
        self.assertEquals(exportlist[1][2], "Func2", "exported function with name 'Func2' not found")

    def test_export_by_ordinal_base_01(self):
        fpath = os.path.join('bins','export_by_ordinal_base_01.dll')
        pe = PE.peFromFileName(fpath)
        exportlist = pe.getExports()
        self.assertEquals(len(exportlist), 2, "expecting 2 exported functions")
        self.assertEquals(exportlist[0][1], 1, "exported function with ordinal 1 not found")
        self.assertEquals(exportlist[1][1], 2, "exported function with ordinal 2 not found")

    def test_export_by_ordinal_base_45(self):
        fpath = os.path.join('bins','export_by_ordinal_base_45.dll')
        pe = PE.peFromFileName(fpath)
        exportlist = pe.getExports()
        self.assertEquals(len(exportlist), 2, "expecting 2 exported functions")
        self.assertEquals(exportlist[0][1], 45, "exported function with ordinal 45 not found")
        self.assertEquals(exportlist[1][1], 55, "exported function with ordinal 55 not found")
