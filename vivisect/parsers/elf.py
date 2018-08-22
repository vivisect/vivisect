import os
import struct

import Elf
import vivisect
import vivisect.parsers as v_parsers

from vivisect.const import *

from cStringIO import StringIO

def parseFile(vw, filename):
    fd = file(filename, 'rb')
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename)

def parseBytes(vw, bytes):
    fd = StringIO(bytes)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf)

def parseFd(vw, fd, filename=None):
    fd.seek(0)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename)

def parseMemory(vw, memobj, baseaddr):
    raise Exception('FIXME implement parseMemory for elf!')

def makeStringTable(vw, va, maxva):

    while va < maxva:
        if vw.readMemory(va, 1) == "\x00":
            va += 1
            continue
        else:
            try:
                if vw.isLocation(va):
                    return
                l = vw.makeString(va)
                va += l[vivisect.L_SIZE]
            except Exception, e:
                print "makeStringTable",e
                return

def makeSymbolTable(vw, va, maxva):
    ret = []
    sname = 'elf.Elf%dSymbol' % (vw.getPointerSize() * 8)
    while va < maxva:
        s = vw.makeStructure(va, sname)
        ret.append(s)
        va += len(s)
    return ret

def makeDynamicTable(vw, va, maxva):
    ret = []
    while va < maxva:
        s = vw.makeStructure(va, "elf.Elf32Dynamic")
        ret.append(s)
        dtag = s.d_tag
        dtype = Elf.dt_types.get(dtag, "Unknown Dynamic Type")
        vw.setComment(va, dtype)
        va += len(s)
        if dtag == Elf.DT_NULL:
            break
    return ret

def makeRelocTable(vw, va, maxva, addbase, baseaddr):
    while va < maxva:
        s = vw.makeStructure(va, "elf.Elf32Reloc")
        tname = Elf.r_types_386.get(Elf.getRelocType(s.r_info), "Unknown Type")
        vw.setComment(va, tname)
        va += len(s)

arch_names = {
    Elf.EM_ARM:'arm',
    Elf.EM_386:'i386',
    Elf.EM_X86_64:'amd64',
    Elf.EM_MSP430:'msp430',
}

archcalls = {
    'i386':'cdecl',
    'amd64':'sysvamd64call',
    'arm':'armcall',
}

def loadElfIntoWorkspace(vw, elf, filename=None):

    arch = arch_names.get(elf.e_machine)
    if arch == None:
       raise Exception("Unsupported Architecture: %d\n", elf.e_machine)

    platform = elf.getPlatform()

    # setup needed platform/format
    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', platform)
    vw.setMeta('Format', 'elf')

    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    vw.addNoReturnApi("*.exit")

    # Base addr is earliest section address rounded to pagesize
    # NOTE: This is only for prelink'd so's and exe's.  Make something for old style so.
    addbase = False
    if not elf.isPreLinked() and elf.isSharedObject():
        addbase = True
    baseaddr = elf.getBaseAddress()

    #FIXME make filename come from dynamic's if present for shared object
    if filename == None:
        filename = "elf_%.8x" % baseaddr

    fhash = "unknown hash"
    if os.path.exists(filename):
        fhash = v_parsers.md5File(filename)

    fname = vw.addFile(filename.lower(), baseaddr, fhash)

    strtabs = {}
    secnames = []
    for sec in elf.getSections():
        secnames.append(sec.getName())

    pgms = elf.getPheaders()
    secs = elf.getSections()

    for pgm in pgms:
        if pgm.p_type == Elf.PT_LOAD:
            if vw.verbose: vw.vprint('Loading: %s' % (repr(pgm)))
            bytez = elf.readAtOffset(pgm.p_offset, pgm.p_filesz)
            bytez += "\x00" * (pgm.p_memsz - pgm.p_filesz)
            pva = pgm.p_vaddr
            if addbase: pva += baseaddr
            vw.addMemoryMap(pva, pgm.p_flags & 0x7, fname, bytez) #FIXME perms
        else:
            if vw.verbose: vw.vprint('Skipping: %s' % repr(pgm))

    if len(pgms) == 0:
        # fall back to loading sections as best we can...
        if vw.verbose: vw.vprint('elf: no program headers found!')

        maps = [ [s.sh_offset,s.sh_size] for s in secs if s.sh_offset and s.sh_size ]
        maps.sort()

        merged = []
        for i in xrange(len(maps)):

            if merged and maps[i][0] == (merged[-1][0] + merged[-1][1]):
                merged[-1][1] += maps[i][1]
                continue

            merged.append( maps[i] )

        baseaddr = 0x05000000
        for offset,size in merged:
            bytez = elf.readAtOffset(offset,size)
            vw.addMemoryMap(baseaddr + offset, 0x7, fname, bytez)

        for sec in secs:
            if sec.sh_offset and sec.sh_size:
                sec.sh_addr = baseaddr + sec.sh_offset

    # First add all section definitions so we have them
    for sec in secs:
        sname = sec.getName()
        size = sec.sh_size
        if sec.sh_addr == 0:
            continue # Skip non-memory mapped sections

        sva = sec.sh_addr
        if addbase: sva += baseaddr

        vw.addSegment(sva, size, sname, fname)

    # Now trigger section specific analysis
    for sec in secs:
        #FIXME dup code here...
        sname = sec.getName()
        size = sec.sh_size
        if sec.sh_addr == 0:
            continue # Skip non-memory mapped sections

        sva = sec.sh_addr
        if addbase: sva += baseaddr

        if sname == ".interp":
            vw.makeString(sva)

        elif sname == ".init":
            vw.makeName(sva, "init_function", filelocal=True)
            vw.addEntryPoint(sva)

        elif sname == ".fini":
            vw.makeName(sva, "fini_function", filelocal=True)
            vw.addEntryPoint(sva)

        elif sname == ".dynamic": # Imports
            makeDynamicTable(vw, sva, sva+size)

        # FIXME section names are optional, use dynamic info from .dynamic
        elif sname == ".dynstr": # String table for dynamics
            makeStringTable(vw, sva, sva+size)

        elif sname == ".dynsym":
            #print "LINK",sec.sh_link
            for s in makeSymbolTable(vw, sva, sva+size):
                pass
                #print "########################.dynsym",s

        # If the section is really a string table, do it
        if sec.sh_type == Elf.SHT_STRTAB:
            makeStringTable(vw, sva, sva+size)

        elif sec.sh_type == Elf.SHT_SYMTAB:
            makeSymbolTable(vw, sva, sva+size)

        elif sec.sh_type == Elf.SHT_REL:
            makeRelocTable(vw, sva, sva+size, addbase, baseaddr)

        if sec.sh_flags & Elf.SHF_STRINGS:
            makeStringTable(vw, sva, sva+size)

    # Let pyelf do all the stupid string parsing...
    for r in elf.getRelocs():
        rtype = Elf.getRelocType(r.r_info)
        rlva = r.r_offset
        if addbase: rlva += baseaddr
        try:
            # If it has a name, it's an externally
            # resolved "import" entry, otherwise, just a regular reloc
            name = decode(r.getName())
            if arch in ('i386','amd64') and name:
                if rtype == Elf.R_386_JMP_SLOT:
                    vw.makeImport(rlva, "*", name)

                # FIXME elf has conflicting names for 2 relocs?
                #elif rtype == Elf.R_386_GLOB_DAT:
                    #vw.makeImport(rlva, "*", name)

                elif rtype == Elf.R_386_32:
                    pass

                elif rtype == Elf.R_X86_64_GLOB_DAT:
                    vw.makeImport(rlva, "*", name)

                else:
                    vw.verbprint('unknown reloc type: %d %s (at %s)' % (rtype, name, hex(rlva)))
                    

            if arch == 'arm' and name:
                if rtype == Elf.R_ARM_JUMP_SLOT:
                    vw.makeImport(rlva, "*", name)

                else:
                    vw.verbprint('unknown reloc type: %d %s (at %s)' % (rtype, name, hex(rlva)))

        except vivisect.InvalidLocation, e:
            print "NOTE",e

    for s in elf.getDynSyms():
        stype = s.getInfoType()
        sva = s.st_value
        if sva == 0:
            continue
        if addbase: sva += baseaddr

        decodedname = decode(s.name)
        sname = pyfriendlyName(decodedname)

        if stype == Elf.STT_FUNC or (stype == Elf.STT_GNU_IFUNC and arch in ('i386','amd64')):   # HACK: linux is what we're really after.
            try:
                vw.addExport(sva, EXP_FUNCTION, sname, fname)
                vw.addEntryPoint(sva)
                if decodedname != sname:  vw.setComment(sva, decodedname)
            except Exception, e:
                vw.vprint('addExport Failure: %s' % e)

        elif stype == Elf.STT_OBJECT:
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, sname, fname)
                    if decodedname != sname:  vw.setComment(sva, decodedname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        elif stype == Elf.STT_HIOS:
            # So aparently Elf64 binaries on amd64 use HIOS and then
            # s.st_other cause that's what all the kewl kids are doing...
            sva = s.st_other
            if addbase: sva += baseaddr
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_FUNCTION, sname, fname)
                    vw.addEntryPoint(sva)
                    if decodedname != sname:  vw.setComment(sva, decodedname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        elif stype == 14:# OMG WTF FUCK ALL THIS NONSENSE! FIXME
            # So aparently Elf64 binaries on amd64 use HIOS and then
            # s.st_other cause that's what all the kewl kids are doing...
            sva = s.st_other
            if addbase: sva += baseaddr
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, sname, fname)
                    if decodedname != sname:  vw.setComment(sva, decodedname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        else:
            pass
            #print "DYNSYM DYNSYM",repr(s),s.getInfoType(),'other',hex(s.st_other)

    for d in elf.getDynamics():
        if d.d_tag == Elf.DT_NEEDED:
            name = d.getName()
            name = name.split('.')[0].lower()
            vw.addLibraryDependancy(name)
        else:
            pass
            #print "DYNAMIC DYNAMIC DYNAMIC",d


    for s in elf.getSymbols():
        sva = s.st_value

        # if the symbol has a value of 0, it is likely a relocation point which gets updated
        sname = normName(s.name)
        if sva == 0:
            for reloc in relocs:
                rname = normName(reloc.name)
                if rname == sname:
                    sva = reloc.r_offset
                    break

        origname = sname
        decodedname = decode(sname)
        sname = pyfriendlyName(decodedname)

        if addbase: sva += baseaddr
        if decodedname != sname:  vw.setComment(sva, decodedname)
        if vw.isValidPointer(sva) and len(sname):
            try:
                vw.makeName(sva, sname, filelocal=True)
            except Exception, e:
                print "WARNING:",e

    if addbase:
        eentry = baseaddr + elf.e_entry
    else:
        eentry = elf.e_entry

    if vw.isValidPointer(eentry):
        vw.addExport(eentry, EXP_FUNCTION, '__entry', fname)
        vw.addEntryPoint(eentry)
        
    if vw.isValidPointer(baseaddr):
        vw.makeStructure(baseaddr, "elf.Elf32")

    return fname

def normName(name):
    '''
    Normalize symbol names.  ie. drop the @@GOBBLEDEGOOK from the end
    '''
    atidx = name.find('@@')
    if atidx > -1:
        name = name[:atidx]
    return name

import string
chars_ok = string.letters + string.digits + '_'# + ':'# + '~'
chars_cok = ("%$#*<>~")

def pyfriendlyName(name):
    '''
    Convert a C++ name into a Python-Friendly name (ie. name could become a variable in the 
    Python environment)
    '''
    out = []
    normname = os.path.basename(name)

    lastcok = False
    chars = list(normname)

    for i in xrange(len(chars)):
        if chars[i] not in chars_ok:
            if chars[i] in chars_cok:
                x = "%.2X" % ord(chars[i])
                out.append(x)
                if not lastcok:
                    # prepend on front
                    out.insert(i, '_')

                lastcok = True

            else:
                out.append('_')
                lastcok = False

        else:
            if lastcok:
                # if last was a 'cok' and this is just ok...
                out.append('_')
            out.append(chars[i])

            lastcok = False

    normname = ''.join(out)
    return normname

def decode(name):
    '''
    Translate C++ mangled name back into the verbose C++ symbol name (with helpful type info)
    '''
    name = normName(name)

    try:
        import cxxfilt
        name = cxxfilt.demangle(name)
    except:
        pass

    return name
