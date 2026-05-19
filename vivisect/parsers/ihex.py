import logging

import envi
import vstruct.defs.ihex as v_ihex

import vivisect.const as v_const
import vivisect.parsers as v_parsers

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

    # figure out if there's an offset into the file we need to skip
    offset = vw.config.viv.parsers.ihex.offset
    if not offset:
        offset = 0
    # TODO: why are we overriding a config option here?
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
        vw.setFileMeta(fname, 'sha256_ihex', v_parsers.sha256Bytes(ihdata))

        for eva in ihex.getEntryPoints():
            if eva is not None:
                vw.addExport(eva, v_const.EXP_FUNCTION, '__entry', fname, makeuniq=True)
                logger.info('adding function from IHEX metadata: 0x%x (_entry)', eva)
                vw.addEntryPoint(eva)

        for addr, perms, _, byts in ihex.getMemoryMaps():
            vw.addMemoryMap(addr, perms, fname, byts)
            vw.addSegment(addr, len(byts), '%.8x' % addr, fname)


def parseMemory(vw, memobj, baseaddr):
    raise NotImplementedError('ihex loader cannot parse memory!')


def getMemBaseAndSize(vw, ihex, baseaddr=None):
    '''
    Returns the default baseaddr and memory size required to load the file
    '''
    savebase = baseaddr

    memmaps = ihex.getMemoryMaps()
    baseaddr = 0xffffffffffffffffffffffff
    topmem = 0

    for mapva, mperms, mname, mbytes in memmaps:
        baseaddr = min(baseaddr, mapva)
        endva = mapva + len(mbytes)
        topmem = max(topmem, endva)

    size = topmem - baseaddr
    if savebase:
        # if we provided a baseaddr, override what the file wants
        baseaddr = savebase

    return baseaddr, size
