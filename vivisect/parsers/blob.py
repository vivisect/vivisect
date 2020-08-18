import envi
import vivisect.exc as v_exc
import vivisect.parsers as v_parsers
from vivisect.const import *


archcalls = {
    'i386': 'cdecl',
    'amd64': 'sysvamd64call',
    'arm': 'armcall',
    'thumb': 'armcall',
    'thumb16': 'armcall',
}


def parseFd(vw, fd, filename=None, baseaddr=None):
    fd.seek(0)
    arch = vw.config.viv.parsers.blob.arch
    bigend = vw.config.viv.parsers.blob.bigend
    if baseaddr is None:
        baseaddr = vw.config.viv.parsers.blob.baseaddr
    try:
        envi.getArchModule(arch)
    except Exception:
        raise v_exc.BlobArchException()

    if filename is None:
        filename = 'blob_%.8x' % baseaddr

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', 'unknown')
    vw.setMeta('Format', 'blob')

    vw.setMeta('bigend', bigend)
    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    bytez = fd.read()
    vw.addMemoryMap(baseaddr, 7, filename, bytez)
    vw.addSegment(baseaddr, len(bytez), '%.8x' % baseaddr, 'blob')
    fname = vw.addFile(filename, baseaddr, v_parsers.md5Bytes(bytez))
    vw.setFileMeta(fname, 'sha256', v_parsers.sha256Bytes(bytez))

def parseFile(vw, filename, baseaddr=None):

    arch = vw.config.viv.parsers.blob.arch
    bigend = vw.config.viv.parsers.blob.bigend
    if baseaddr is None:
        baseaddr = vw.config.viv.parsers.blob.baseaddr

    try:
        envi.getArchModule(arch)
    except Exception:
        raise v_exc.BlobArchException()

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', 'unknown')
    vw.setMeta('Format', 'blob')

    vw.setMeta('bigend', bigend)
    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    with open(filename, 'rb') as f:
        bytez = f.read()
    fname = vw.addFile(filename, baseaddr, v_parsers.md5File(filename))
    vw.setFileMeta(fname, 'sha256', v_parsers.sha256Bytes(bytez))
    vw.addMemoryMap(baseaddr, 7, filename, bytez)
    vw.addSegment(baseaddr, len(bytez), '%.8x' % baseaddr, 'blob')


def parseMemory(vw, memobj, baseaddr):
    va, size, perms, fname = memobj.getMemoryMap(baseaddr)
    if not fname:
        fname = 'map_%.8x' % baseaddr

    bytez = memobj.readMemory(va, size)
    fname = vw.addFile(fname, baseaddr, v_parsers.md5Bytes(bytez))
    vw.setFileMeta(fname, 'sha256', v_parsers.sha256Bytes(bytez))
    vw.addMemoryMap(va, perms, fname, bytez)
    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))
