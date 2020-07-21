import logging
import unittest

import vivisect.codegraph as v_codegraph

logger = logging.getLogger(__name__)

class GraphCoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vw = helpers.getTestWorkspace('windows', 'amd64', 'firefox.exe')
        cls.vs.analyze()

    def test_vivisect_codegraph_func1(self):
        pass
