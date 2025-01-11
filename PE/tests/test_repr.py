import os
import unittest

import PE

def getTestPath(*paths):
    '''
    Return the join'd path to a file in the vivtestfiles repo
    by using the environment variable "VIVTESTFILES"

    ( raises SkipTest if env var is not present )
    '''
    testdir = os.getenv('VIVTESTFILES')
    if not testdir:
        raise unittest.SkipTest('VIVTESTFILES env var not found!')
    testdir = os.path.abspath(testdir)
    return os.path.join(testdir, *paths)

class PEResourceTests(unittest.TestCase):

    def test_repr(self):
        path = getTestPath('windows','amd64','dbghelp.dll')
        pe = PE.peFromFileName(path)
        pe_repr = repr(pe)

        self.assertIn("DllName: 'dbghelp.dll'", pe_repr)
        self.assertIn("PDB Path: 'dbghelp.pdb'", pe_repr)
        self.assertIn("00000000 (08)   Name: .rsrc", pe_repr)
        self.assertIn("00000048 (02)     MajorSubsystemVersion: 0x00000005 (5)", pe_repr)


