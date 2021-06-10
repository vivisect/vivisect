import envi.common as e_common

import vivisect.parsers as viv_parsers
import vstruct.defs.macho as vs_macho


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


def _loadMacho(vw, filebytes, filename=None, baseaddr=None):

    # We fake them to *much* higher than norm so pointer tests do better...
    if baseaddr is None:
        baseaddr = vw.config.viv.parsers.macho.baseaddr

    if filename is None:
        filename = 'macho_%.8x' % baseaddr  # FIXME more than one!

    # grab md5 and sha256 hashes before we modify the bytes
    fhash = viv_parsers.md5Bytes(filebytes)
    sha256 = viv_parsers.sha256Bytes(filebytes)

    # Check for the FAT binary magic...
    if e_common.hexify(filebytes[:4]) in ('cafebabe', 'bebafeca'):

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

    # Add the memory maps and segments from the macho definition
    for segname, rva, perms, segbytes in macho.getSegments():
        segbase = baseaddr + rva
        vw.addMemoryMap(segbase, perms, fname, segbytes)
        vw.addSegment(segbase, len(segbytes), segname, fname)

    # Add the library dependancies
    for libname in macho.getLibDeps():
        # FIXME hack....
        libname = libname.split('/')[-1]
        libname = libname.split('.')[0].lower()
        vw.addLibraryDependancy(libname)

    return fname


def parseMemory(vw, memobj, baseaddr):
    # TODO: implement
    pass
