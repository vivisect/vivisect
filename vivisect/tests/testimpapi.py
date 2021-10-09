import unittest

import vivisect.impapi as viv_impapi

class ImpApiTest(unittest.TestCase):

    #def setUp(self):
        #pass

    #def tearDown(self):
        #pass

    def test_impapi_windows(self):
        imp = viv_impapi.getImportApi('windows','i386')
        self.assertEqual( imp.getImpApiCallConv('ntdll.RtlAllocateHeap'), 'stdcall')

        imp = viv_impapi.getImportApi('windows','arm')
        self.assertEqual( imp.getImpApiCallConv('ntdll.RtlAllocateHeap'), 'armcall')

    #def test_impapi_posix(self):
        #imp = viv_impapi.getImpApi('windows','i386')

    def test_impapi_winkern(self):
        imp = viv_impapi.getImportApi('winkern','i386')
        self.assertEqual( imp.getImpApiCallConv('ntoskrnl.ObReferenceObjectByHandle'), 'stdcall')

        imp = viv_impapi.getImportApi('winkern','arm')
        self.assertEqual( imp.getImpApiCallConv('ntoskrnl.ObReferenceObjectByHandle'), 'armcall')

