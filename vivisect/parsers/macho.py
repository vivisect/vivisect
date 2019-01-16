import os

import vivisect.parsers as viv_parsers
import vstruct.defs.macho as vs_macho
import vivisect.analysis.i386 as viv_a_i386

def parseFile(vw, filename):
    fbytes = file(filename, 'rb').read()
    return _loadMacho(vw, fbytes, filename=filename)

def parseBytes(vw, filebytes):
    return _loadMacho(vw, filebytes)

archcalls = {
    'i386':'cdecl',
    'amd64':'sysvamd64call',
    'arm':'armcall',
    'thumb':'armcall',
    'thumb16':'armcall',
}

def _loadMacho(vw, filebytes, filename=None):

    # We fake them to *much* higher than norm so pointer tests do better...
    baseaddr = vw.config.viv.parsers.macho.baseaddr

    if filename == None:
        filename = 'macho_%.8x' % baseaddr # FIXME more than one!

    # Check for the FAT binary magic...
    if filebytes[:4].encode('hex') in ('cafebabe', 'bebafeca'):

        archhdr = None
        fatarch = vw.config.viv.parsers.macho.fatarch

        archlist = []

        offset = 0
        fat = vs_macho.fat_header()
        offset = fat.vsParse(filebytes, offset=offset)
        for i in xrange(fat.nfat_arch):
            ar = vs_macho.fat_arch()
            offset = ar.vsParse(filebytes, offset=offset)
            archname = vs_macho.mach_cpu_names.get(ar.cputype)
            if archname == fatarch:
                archhdr = ar
                break
            archlist.append((archname,ar))

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
    if arch == None:
        raise Exception('Unknown MACH-O arch: %.8x' % macho.mach_header.cputype)

    # Setup arch/plat/fmt
    vw.setMeta('Architecture', arch)
    vw.setMeta("Platform", "Darwin")
    vw.setMeta("Format", "macho")

    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    # Add the file entry
    hash = "unknown hash"
    if os.path.exists(filename):
        hash = viv_parsers.md5File(filename)

    fname = vw.addFile(filename, baseaddr, hash)

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
    pass

