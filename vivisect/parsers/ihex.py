import envi
import vstruct.defs.ihex as v_ihex
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

    arch = vw.config.viv.parsers.ihex.arch
    if not arch:
        raise Exception('IHex loader *requires* arch option (-O viv.parsers.ihex.arch=\\"<archname>\\")')

    envi.getArchModule(arch)

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', 'Unknown')
    vw.setMeta('Format', 'ihex')

    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    offset = vw.config.viv.parsers.ihex.offset
    if not offset:
        offset = 0
    vw.config.viv.parsers.ihex.offset = 0

    # might we make use of baseaddr, even though it's an IHEX?  for now, no.
    ihex = v_ihex.IHexFile()
    with open(filename, 'rb') as f:
        shdr = f.read(offset)
        sbytes = f.read()
        if offset:
            logger.debug('skipping %d bytes: %r', offset, repr(shdr)[:300])

        fname = vw.addFile(filename, 0, v_parsers.md5Bytes(shdr + sbytes))
        vw.setFileMeta(fname, 'sha256', v_parsers.sha256Bytes(shdr + sbytes))

        ihex.vsParse(sbytes)

        # calculate IHEX-specific hash - only the fields copied into memory
        ihdata = ihex.vsEmit()
        vw.setFileMeta(fname, 'sha256_ihex', v_parsers.sha256Bytes(ihdata.encode('utf-8')))

        for eva in ihex.getEntryPoints():
            if eva is not None:
                vw.addExport(eva, EXP_FUNCTION, '__entry', fname, makeuniq=True)
                logger.info('adding function from IHEX metadata: 0x%x (_entry)', eva)
                vw.addEntryPoint(eva)

        for addr, perms, notused, bytes in ihex.getMemoryMaps():
            vw.addMemoryMap(addr, perms, fname, bytes)
            vw.addSegment(addr, len(bytes), '%.8x' % addr, fname)


def parseMemory(vw, memobj, baseaddr):
    raise Exception('ihex loader cannot parse memory!')
