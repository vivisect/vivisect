import unittest

import vivisect

import vivisect.analysis.i386.golang as x86_go
import vivisect.analysis.amd64.golang as x64_go

import vivisect.tests.helpers as helpers


def loadGoBin(*path):
    '''
    We don't need full analysis on the go binaries to complete the tests
    '''
    vw = vivisect.VivWorkspace()
    path = helpers.getTestPath(*path)
    vw.loadFromFile(path)
    for ep in vw.getEntryPoints():
        vw.makeFunction(ep)
    return vw


class GolangTest(unittest.TestCase):
    '''
    Tests to verify that the GO runtime_main is discovered as a function.
    The tests succeed only if golang extended analysis is used:
    vivisect/analysis/amd64/golang.py and vivisect/analysis/i386/golang.py.
    '''
    def test_PE32(self):
        vw = loadGoBin('windows', 'i386', 'GO_hello_PE32.exe')
        x86_go.analyze(vw)
        assert vw.isFunction(0x428880)

    def test_PE32_stripped(self):
        vw = loadGoBin('windows', 'i386', 'GO_hello_PE32_stripped.exe')
        x86_go.analyze(vw)
        assert vw.isFunction(0x428880)

    def test_PE32_findcase(self):
        vw = loadGoBin('windows', 'i386', 'GO_find2case_PE32.exe')
        x86_go.analyze(vw)
        assert vw.isFunction(0x424e10)

    def test_PE64(self):
        vw = loadGoBin('windows', 'amd64', 'GO_hello_PE64.exe')
        x64_go.analyze(vw)
        assert vw.isFunction(0x42dc00)
