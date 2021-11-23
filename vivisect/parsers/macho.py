import logging

import envi.common as e_common

import vivisect.parsers as viv_parsers
import vstruct.defs.macho as vs_macho

logger = logging.getLogger(__name__)


def parseFile(vw, filename, baseaddr=None):
    with open(filename, 'rb') as f:
        fbytes = f.read()
    return _loadMacho(vw, fbytes, filename=filename, baseaddr=baseaddr)


def parseBytes(vw, filebytes, baseaddr=None):
    return _loadMacho(vw, filebytes, baseaddr=baseaddr)


archcalls = {
    'i386': 'cdecl',
    'amd64': 'sysvamd64call',
    'arm': 'armcall',
    'thumb': 'armcall',
    'thumb16': 'armcall',
}

'''
The various magic byte strings are as follows:
cefaedfe: Mach-O Little Endian (32-bit)
cffaedfe: Mach-O Little Endian (64-bit)
feedface: Mach-O Big Endian (32-bit)
feedfacf: Mach-O Big Endian (64-bit)
cafebabe: Universal Binary Big Endian. These fat binaries are archives that can include binaries for multiple architectures, but typically contain PowerPC and Intel x86.
'''

def checkFatMagicAndTrunc(vw, filebytes):
    archhdr = None
    fatarch = vw.config.viv.parsers.macho.fatarch

    archlist = []

    offset = 0
    fat = vs_macho.fat_header()
    offset = fat.vsParse(filebytes, offset=offset)
    for i in range(fat.nfat_arch):
        ar = vs_macho.fat_arch()
        offset = ar.vsParse(filebytes, offset=offset)
        archname = vs_macho.mach_cpu_names.get(ar.cputype)
        if archname == fatarch:
            archhdr = ar
            break
        archlist.append((archname, ar))

    if not archhdr:
        # If we don't have a specified arch, exception!
        vw.vprint('Mach-O Fat Binary Architectures:')
        for archname, ar in archlist:
            vw.vprint('0x%.8x 0x%.8x %s' % (ar.offset, ar.size, archname))
        raise Exception('Mach-O Fat Binary: Please specify arch with -O viv.parsers.macho.fatarch="<archname>"')

    filebytes = filebytes[archhdr.offset:archhdr.offset+archhdr.size]

    return filebytes

def _loadMacho(vw, filebytes, filename=None, baseaddr=None):

    # We fake them to *much* higher than norm so pointer tests do better...
    if baseaddr is None:
        baseaddr = vw.config.viv.parsers.macho.baseaddr

    if filename is None:
        filename = 'macho_%.8x' % baseaddr  # FIXME more than one!

    # find the lowest loadable address, then get an offset so we can apply it later
    fakebase, size = getMemoryBaseAndSize(vw, filename)
    offset = baseaddr - fakebase
    logger.debug("address offset: 0x%x" % offset)

    # grab md5 and sha256 hashes before we modify the bytes
    fhash = viv_parsers.md5Bytes(filebytes)
    sha256 = viv_parsers.sha256Bytes(filebytes)

    hdr = e_common.hexify(filebytes[:4])

    # Check for the FAT binary magic...
    if hdr in ('cafebabe', 'bebafeca'):
        filebytes = checkFatMagicAndTrunc(vw, filebytes)

    # Instantiate the parser wrapper and parse bytes
    macho = vs_macho.mach_o()
    macho.vsParse(filebytes)

    arch = vs_macho.mach_cpu_names.get(macho.mach_header.cputype)
    if arch is None:
        raise Exception('Unknown MACH-O arch: %.8x' % macho.mach_header.cputype)

    # Setup arch/plat/fmt
    vw.setMeta('Architecture', arch)
    vw.setMeta("Platform", "Darwin")
    vw.setMeta("Format", "macho")

    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    # Add the file entry
    fname = vw.addFile(filename, baseaddr, fhash)
    vw.setFileMeta(fname, 'sha256', sha256)

    logger.debug("loading memory maps...")
    # Add the memory maps and segments from the macho definition
    for segname, rva, perms, segbytes in macho.getSegments():
        logger.debug("map: %r rva:0x%x perms:0x%x len: 0x%x", segname, rva, perms, len(segbytes))
        segbase = rva + offset  # not baseaddr, since it already has baseaddr applied
        vw.addMemoryMap(segbase, perms, fname, segbytes)
        vw.addSegment(segbase, len(segbytes), segname, fname)

    # Add the library dependancies
    for libname in macho.getLibDeps():
        logger.debug("deplib: %r", libname)
        # FIXME hack....
        libname = libname.split(b'/')[-1]
        libname = libname.split(b'.')[0].lower()
        vw.addLibraryDependancy(libname)

    logger.debug("memoryMaps: \n%r", '\n'.join(["0x%x, 0x%x, 0x%x, %r" % (w,x,y,z) for w,x,y,z in vw.getMemoryMaps()]))
    # Add Mach-O structures
    structinfo, cmdinfo = macho.getStructureInfo()
    for sname, va in structinfo:
        try:
            logger.debug("Applying struct %r at 0x%x", sname, va+offset)
            vw.makeStructure(va + offset, sname)
        except Exception as e:
            print("Error: %r" % e)

    for va, cmdname in cmdinfo:
        vw.makeName(va, "macho_" + cmdname)


    for soff, va in macho.getEntryPoints():
        va += baseaddr
        if vw.isValidPointer(va):
            vw.addEntryPoint(va)

        ptr = baseaddr + soff
        logger.debug("adding entrypoint: 0x%x (off: 0x%x/0x%x)", va, ptr, soff) 
        vw.makePointer(ptr, follow=False)

    return fname


def parseMemory(vw, memobj, baseaddr):
    # TODO: implement
    pass


def getMemoryBaseAndSize(vw, filename, baseaddr=None):
    '''
    Returns the default baseaddr and memory size required to load the file
    '''
    if baseaddr is None:
        baseaddr = vw.config.viv.parsers.macho.baseaddr

    with open(filename, 'rb') as f:
        filebytes = f.read()

    macho = vs_macho.mach_o()
    macho.vsParse(filebytes)

    memmaps = macho.getSegments()
    baseaddr = 0xffffffffffffffffffffffff
    topmem = 0

    for mname, mapva, mperms, mbytes in memmaps:
        if mapva < baseaddr:
            baseaddr = mapva
        endva = mapva + len(mbytes)
        if endva > topmem:
            topmem = endva

    size = topmem - baseaddr
    logger.debug("getMemoryBaseAndSize() => 0x%x:0x%x", baseaddr, size)
    return baseaddr, size
