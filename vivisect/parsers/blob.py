import envi
import vivisect
import vivisect.parsers as v_parsers
from vivisect.const import *


archcalls = {
    'i386':'cdecl',
    'amd64':'sysvamd64call',
    'arm':'armcall',
    'ppc':'ppccall',
    'vle':'ppccall',
    }

def parseFd(vw, fd, filename=None):
    fd.seek(0)
    arch = vw.config.viv.parsers.blob.arch
    bigend = vw.config.viv.parsers.blob.bigend
    baseaddr = vw.config.viv.parsers.blob.baseaddr
    try:
        envi.getArchModule(arch)
    except Exception, e:
        raise Exception('Blob loader *requires* arch option (-O viv.parsers.blob.arch="<archname>")')

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','unknown')
    vw.setMeta('Format','blob')

    vw.setMeta('bigend', bigend)
    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    bytez =  fd.read() 
    vw.addMemoryMap(baseaddr, 7, filename, bytez)
    vw.addSegment( baseaddr, len(bytez), '%.8x' % baseaddr, 'blob' )

def parseFile(vw, filename):

    arch = vw.config.viv.parsers.blob.arch
    bigend = vw.config.viv.parsers.blob.bigend
    baseaddr = vw.config.viv.parsers.blob.baseaddr

    try:
        envi.getArchModule(arch)
    except Exception, e:
        raise Exception('Blob loader *requires* arch option (-O viv.parsers.blob.arch="<archname>")')


    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','unknown')
    vw.setMeta('Format','blob')

    vw.setMeta('bigend', bigend)
    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    fname = vw.addFile(filename, baseaddr, v_parsers.md5File(filename))
    bytez =  file(filename, "rb").read()
    vw.addMemoryMap(baseaddr, 7, filename, bytez)
    vw.addSegment( baseaddr, len(bytez), '%.8x' % baseaddr, 'blob' )


def parseMemory(vw, memobj, baseaddr):
    va,size,perms,fname = memobj.getMemoryMap(baseaddr)
    if not fname:
        fname = 'map_%.8x' % baseaddr
    bytes = memobj.readMemory(va, size)
    fname = vw.addFile(fname, baseaddr, v_parsers.md5Bytes(bytes))
    vw.addMemoryMap(va, perms, fname, bytes)
    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

