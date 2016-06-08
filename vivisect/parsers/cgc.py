import elf as elfmod
from elf import *

def parseFile(vw, filename):
    fd = file(filename, 'rb')
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename)

def parseBytes(vw, bytes):
    fd = StringIO(bytes)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf)

def parseFd(vw, fd, filename=None):
    fd.seek(0)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename)

def loadElfIntoWorkspace(vw, elf, filename=None, arch=None, platform=None, filefmt='elf'):
    retval = elfmod.loadElfIntoWorkspace(vw, elf, filename, arch, platform='decree', filefmt='cgc')
    vw.addNoReturnApi("*._terminate")
    return retval

