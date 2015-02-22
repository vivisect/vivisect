import unittest
import vivisect.workspace as v_workspace

# NOTE: any tests which need files belong in vivtestfiles repo

class VivTests(unittest.TestCase):

    def test_vw_basic(self):
        vw = v_workspace.VivWorkspace()
        self.assertIsNotNone( vw.getVivConfig('ident') )

