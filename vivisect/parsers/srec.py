import envi
import vstruct.defs.srec as v_srec
import vivisect.parsers as v_parsers
from vivisect.const import *

import logging
logger = logging.getLogger(__name__)


archcalls = {
    'i386': 'cdecl',
    'amd64': 'sysvamd64call',
    'arm': 'armcall',
    'thumb': 'armcall',
    'thumb16': 'armcall',
}


def parseFile(vw, filename, baseaddr=None):

    arch = vw.config.viv.parsers.srec.arch
    if not arch:
        raise Exception('SRec loader *requires* arch option (-O viv.parsers.srec.arch=\\"<archname>\\")')

    envi.getArchModule(arch)

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', 'Unknown')
    vw.setMeta('Format', 'srec')

    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    offset = vw.config.viv.parsers.srec.offset
    if not offset:
        offset = 0
    vw.config.viv.parsers.srec.offset = 0

    srec = v_srec.SRecFile()
    with open(filename, 'rb') as f:
        shdr = f.read(offset)
        sbytes = f.read()
        if offset:
            logger.debug('skipping %d bytes: %r', offset, repr(shdr)[:300])

        fname = vw.addFile(filename, 0, v_parsers.md5Bytes(shdr + sbytes))
        vw.setFileMeta(fname, 'sha256', v_parsers.sha256Bytes(shdr + sbytes))

        srec.vsParse(sbytes)

        # calculate SREC-specific hash - only the fields copied into memory
        srdata = srec.vsEmit()
        vw.setFileMeta(fname, 'sha256_srec', v_parsers.sha256Bytes(srdata.encode('utf-8')))

        for eva in srec.getEntryPoints():
            if eva is not None:
                vw.addExport(eva, EXP_FUNCTION, '__entry', fname, makeuniq=True)
                logger.info('adding function from SREC metadata: 0x%x (_entry)', eva)
                vw.addEntryPoint(eva)

        for addr, perms, notused, bytes in srec.getMemoryMaps():
            vw.addMemoryMap(addr, perms, fname, bytes)
            vw.addSegment(addr, len(bytes), '%.8x' % addr, fname)


def parseMemory(vw, memobj, baseaddr):
    raise Exception('srec loader cannot parse memory!')
