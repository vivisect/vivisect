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
        fpath = os.path.join('test_pe', 'bins', 'wwaninst.dll')
        pe = PE.peFromFileName(fpath)
        vs = pe.getVS_VERSIONINFO()
        self.assertIsNotNone(vs)
        keys = vs.getVersionKeys()
        self.assertEqual(len(keys), len(vs_version))
        for key in vs.getVersionKeys():
            self.assertEqual(vs_version.get(key), vs.getVersionValue(key))
