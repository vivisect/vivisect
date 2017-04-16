import os
import unittest
import vivisect
import helpers

def require(f):
    def skipit(*args, **kwargs):
        raise unittest.SkipTest('VIVTESTFILES env var...')

    if os.getenv('VIVTESTFILES') == None:
        return skipit

    return f

def getTestWorkspace(fname, analyze=True):
    fpath = helpers.getTestPath(fname)

    vw = vivisect.VivWorkspace()
    vw.loadFromFile(fpath)
    if analyze:
        vw.analyze()
    return vw

def getAnsWorkspace(fname):
    fpath = helpers.getTestPath("%s.viv" % fname)

    vw = vivisect.VivWorkspace()
    vw.loadWorkspace(fpath)
    return vw

