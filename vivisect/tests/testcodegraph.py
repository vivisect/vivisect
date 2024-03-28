import logging
import unittest

import vivisect.codegraph as v_codegraph
import vivisect.tests.helpers as helpers

logger = logging.getLogger(__name__)

class GraphCoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vw = helpers.getTestWorkspace('windows', 'amd64', 'firefox.exe')

    def test_vivisect_codegraph_firefox(self):
        fva = 0x1400041a0
        cg = v_codegraph.FuncBlockGraph(self.vw, fva)
        # TODO: add 0x140020920 as a test once the jump table stuff gets fixed
        # LauncherMain in the firefox source code:
        cg.addEntryPoint(fva)
        self.assertTrue(cg.isCodeBlockNode(fva))
        self.assertFalse(cg.isCodeBlockNode(fva + 1))
        cb = cg.getCodeBlockNode(fva)
        self.assertEqual(cg.getCodeBlockBounds(cb), (fva, 110))
        self.assertIsNotNone(cg.getNodeByVa(0x140004213))
        self.assertEqual(len(cg.nodevas), self.vw.getFunctionMeta(fva, 'InstructionCount'))

        # LaunchUnelevated.cpp, GetMediumIntegrityToken
        fva = 0x140004020
        cg = v_codegraph.FuncBlockGraph(self.vw, fva)
        self.assertEqual(len(cg.nodevas), self.vw.getFunctionMeta(fva, 'InstructionCount'))
        self.assertEqual(len(cg.nodes), 11)
        self.assertEqual(len(cg.nodes), self.vw.getFunctionMeta(fva, 'BlockCount'))
        codeblocks = [
            0x140004020,
            0x1400040f3,
            0x14000406d,
            0x14000413d,
            0x14000409c,
            0x14000416e,
            0x1400040d4,
            0x1400040db,
            0x1400040de,
            0x1400040e8,
            0x14000411f,
        ]
        for c in codeblocks:
            self.assertTrue(cg.isCodeBlockNode(c))
