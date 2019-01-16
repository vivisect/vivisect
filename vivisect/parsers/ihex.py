import envi
import vivisect
import vstruct.defs.ihex as v_ihex
import vivisect.parsers as v_parsers

from vivisect.const import *

archcalls = {
    'i386':'cdecl',
    'amd64':'sysvamd64call',
    'arm':'armcall',
}

def parseFile(vw, filename):

    arch = vw.config.viv.parsers.ihex.arch
    if not arch:
        raise Exception('IHex loader *requires* arch option (-O viv.parsers.ihex.arch=\\"<archname>\\")')

    envi.getArchModule(arch)

    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform','Unknown')
    vw.setMeta('Format','ihex')

    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    fname = vw.addFile(filename, 0, v_parsers.md5File(filename))

    ihex = v_ihex.IHexFile()
    ihex.vsParse( file(filename, 'rb').read() )

    for addr, perms, notused, bytes in ihex.getMemoryMaps():
        vw.addMemoryMap( addr, perms, fname, bytes )
        vw.addSegment( addr, len(bytes), '%.8x' % addr, fname )

def parseMemory(vw, memobj, baseaddr):
    raise Exception('ihex loader cannot parse memory!')
