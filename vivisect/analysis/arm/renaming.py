import envi
import vivisect

def analyze(vw):
    for fva in vw.getFunctions():
        analyzeFunction(vw, fva)

def analyzeFunction(vw, fva):
    fakename = vw.getName(fva+1)
    if fakename != None:
        vw.makeName(fva+1, None)
        vw.makeName(fva, fakename)

