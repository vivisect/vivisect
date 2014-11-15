import unittest

import vivisect
import vivisect.codegraph as codegraph
import vivisect.tests.samplecode as samplecode

class GraphCoreTest(unittest.TestCase):

    def test_vivisect_codegraph_func1(self):
        vw = vivisect.VivWorkspace()
        vw.setMeta('Architecture','i386')
        vw.addMemoryMap(0x41410000, 0xff, 'none', samplecode.func1)
        vw.makeFunction(0x41410000)

