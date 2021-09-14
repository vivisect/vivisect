import unittest

import vivisect.reports as v_reports
import vivisect.tests.helpers as helpers


class ReportsTest(unittest.TestCase):
    '''
    Test each of the base report modules.
    '''
    @classmethod
    def setUpClass(cls):
        cls.vw = helpers.getTestWorkspace('windows', 'i386', 'helloworld.exe')

    def test_overlap(self):
        cols, retn = v_reports.runReportModule(self.vw, 'vivisect.reports.overlaplocs')
        self.assertEqual(cols, (("Overlap Size",   int),
                                ("This Location",  str),
                                ("Other Location", str)))

        self.assertGreater(len(retn), 0)
        for va, meta in retn.items():
            size, baserepr, othrrepr = meta
            self.assertGreater(size, 0)
            self.assertNotEqual(baserepr, '')
            self.assertNotEqual(othrrepr, '')

    def test_undef(self):
        cols, retn = v_reports.runReportModule(self.vw, 'vivisect.reports.undeftargets')
        self.assertEqual(cols, (("Bytes", str),
                                ("Name", str)))

        self.assertGreater(len(retn), 0)
        for va, undef in retn.items():
            byts, mesg = undef
            self.assertIsNone(self.vw.getLocation(va))
            self.assertGreater(len(byts), 0)
            self.assertGreater(len(mesg), 0)

    def test_locationdist(self):
        cols, retn = v_reports.runReportModule(self.vw, 'vivisect.reports.locationdist')
        self.assertEqual(cols, (("Location Type", str),
                                ("Instance Count", int),
                                ("Size (bytes)", int),
                                ("Size (percent)", int)))

        self.assertEqual(retn, self.vw.getLocationDistribution())

    def test_funcomp(self):
        cols, retn = v_reports.runReportModule(self.vw, 'vivisect.reports.funccomplexity')
        self.assertEqual(cols, (("Code Blocks", int),
                                ("Mnem Dist", int)))
        vw = self.vw

        self.assertGreater(len(retn), 0)
        for fva, comp in retn.items():
            blks, mdist = comp
            self.assertEqual(blks, len(vw.getFunctionBlocks(fva)))
            self.assertEqual(mdist, vw.getFunctionMeta(fva, 'MnemDist', -1))
