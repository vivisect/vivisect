import envi
import vivisect
import vivisect.parsers as v_parsers
from vivisect.const import *

class BlobArchException(Exception):
    def __str__(self):
        out = [ 'Blob loader *requires* valid arch option (-O viv.parsers.blob.arch="<archname>")\n    ' ]
        out.append('\n    '.join(envi.getArchNames()))
        return ''.join(out)


def parseFd(vw, fd, filename=None):
    fd.seek(0)
    arch = vw.config.viv.parsers.blob.arch
    bigend = vw.config.viv.parsers.blob.bigend
    baseaddr = vw.config.viv.parsers.blob.baseaddr
    try:
        envi.getArchModule(arch)
    except Exception, e:
        raise BlobArchException()

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','unknown')
    vw.setMeta('Format','blob')

    vw.setMeta('bigend', bigend)

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
        raise BlobArchException()


    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','unknown')
    vw.setMeta('Format','blob')

    vw.setMeta('bigend', bigend)

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

