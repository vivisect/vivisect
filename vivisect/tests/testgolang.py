import unittest

import vivisect
import vivisect.tests.helpers as helpers


class GolangTest(unittest.TestCase):
    '''
    Tests verify that the GO runtime_main is discovered as a function.
    The tests succeed only if golang exteneded analysis is used:
    vivisect/analysis/amd64/golang.py and vivisect/analysis/i386/golang.py.
    '''
    @classmethod
    def setUpClass(cls):
        pass

    def test_PE32(self):
        vw = helpers.getTestWorkspace('windows', 'i386', 'GO_hello_PE32.exe')
        assert vw.isFunction(0x428880)

    def test_PE32_stripped(self):
        vw = helpers.getTestWorkspace('windows', 'i386', 'GO_hello_PE32_stripped.exe')
        assert vw.isFunction(0x428880)
        
    def test_PE32_findcase(self):
        vw = helpers.getTestWorkspace('windows', 'i386', 'GO_find2case_PE32.exe')
        assert vw.isFunction(0x424e10)
        
    def test_PE64(self):
        vw = helpers.getTestWorkspace('windows', 'amd64', 'GO_hello_PE64.exe')
        assert vw.isFunction(0x42dc00)
