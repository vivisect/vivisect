import os
import unittest
import functools

import vivisect.cli as v_cli


class MockVw(object):
    def __init__(self, *args, **kwargs):
        self.psize = 4
        self._locs = {}

    def _addLocation(self, va, size, ltype, tinfo):
        self._locs[va] = (va, size, ltype, tinfo)

    def getLocation(self, va):
        return self._locs.get(va, None)

    def getPointerSize(self):
        return self.psize


def getTestBytes(*paths):
    testdir = os.getenv('VIVTESTFILES')
    if not testdir:
        raise unittest.SkipTest('VIVTESTFILES env var not found!')
    testdir = os.path.abspath(testdir)
    fpath = os.path.join(testdir, *paths)
    with open(fpath, 'rb') as fd:
        return fd.read()


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


@functools.lru_cache()
def getTestWorkspace(*paths, vw=None):
    testdir = os.getenv('VIVTESTFILES')
    if not testdir:
        raise unittest.SkipTest('VIVTESTFILES env var not found!')

    testdir = os.path.abspath(testdir)
    fpath = os.path.join(testdir, *paths)

    if not vw:
        vw = v_cli.VivCli()
        vw.config.viv.analysis.symswitchcase.timeout_secs = 30


    vw.loadFromFile(fpath)
    vw.analyze()
    return vw

def getTestWorkspace_nocache(*paths, vw=None):
    testdir = os.getenv('VIVTESTFILES')
    if not testdir:
        raise unittest.SkipTest('VIVTESTFILES env var not found!')

    testdir = os.path.abspath(testdir)
    fpath = os.path.join(testdir, *paths)

    if not vw:
        vw = v_cli.VivCli()
        vw.config.viv.analysis.symswitchcase.timeout_secs = 30


    vw.loadFromFile(fpath)
    vw.analyze()
    return vw
