import os
import unittest
import vivisect

def require(f):
    def skipit(*args, **kwargs):
        raise unittest.SkipTest('VIVBINS env var...')

    if os.getenv('VIVBINS') == None:
        return skipit

    return f

def getTestWorkspace(fname, analyze=True):
    path = os.getenv('VIVBINS') 
    fpath = os.path.join(path,fname)

    if path == '1':
        fpath = os.path.join('test_vivisect','bins',fname)

    vw = vivisect.VivWorkspace()
    vw.loadFromFile(fpath)
    if analyze:
        vw.analyze()
    return vw

def getAnsWorkspace(fname):
    path = os.getenv('VIVBINS') 
    fpath = os.path.join(path,"%s.viv" % fname)

    if path == '1':
        fpath = os.path.join('test_vivisect','bins','%s.viv' % fname)

    vw = vivisect.VivWorkspace()
    vw.loadWorkspace(fpath)
    return vw

