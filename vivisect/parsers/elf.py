import os
import struct
import logging

import Elf
import envi
import vivisect
import vivisect.parsers as v_parsers
import envi.bits as e_bits

from vivisect.const import *

from cStringIO import StringIO

logger = logging.getLogger(__name__)

# FIXME: TODO: Reorder, so that Dynamics Data is applied first... with optional ELF Section data afterwards (default to apply if not already there)
# FIXME: we're causing Functions and Code to happen... *before* any analysis modules are put into place.

def parseFile(vw, filename, baseaddr=None):
    fd = file(filename, 'rb')
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename, baseaddr=baseaddr)

def parseBytes(vw, bytes, baseaddr=None):
    fd = StringIO(bytes)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, baseaddr=baseaddr)

def parseFd(vw, fd, filename=None, baseaddr=None):
    fd.seek(0)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename, baseaddr=baseaddr)

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
                logger.warn("makeStringTable\t%r",e)
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
    Elf.EM_ARM_AARCH64:'aarch64',
}

archcalls = {
    'i386':'cdecl',
    'amd64':'sysvamd64call',
    'arm':'armcall',
}

def loadElfIntoWorkspace(vw, elf, filename=None, baseaddr=None):
    # analysis of discovered functions and data locations should be stored until the end of loading
    data_ptrs = []
    new_pointers = []
    new_functions = []

    arch = arch_names.get(elf.e_machine)
    if arch is None:
       raise Exception("Unsupported Architecture: %d\n", elf.e_machine)

    platform = elf.getPlatform()

    # setup needed platform/format
    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', platform)
    vw.setMeta('Format', 'elf')

    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    vw.addNoReturnApi("*.exit")
    vw.addNoReturnApi("*._exit")
    vw.addNoReturnApi("*.longjmp")
    vw.addNoReturnApi("*._setjmp")

    # Base addr is earliest section address rounded to pagesize
    # NOTE: This is only for prelink'd so's and exe's.  Make something for old style so.
    addbase = False
    if not elf.isPreLinked() and elf.isSharedObject():
        addbase = True
    if baseaddr is None:
        baseaddr = elf.getBaseAddress()

    #FIXME make filename come from dynamic's if present for shared object
    if filename is None:
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
            if pgm.p_memsz == 0:
                continue
            logger.info('Loading: %s', repr(pgm))
            bytez = elf.readAtOffset(pgm.p_offset, pgm.p_filesz)
            bytez += "\x00" * (pgm.p_memsz - pgm.p_filesz)
            pva = pgm.p_vaddr
            if addbase: pva += baseaddr
            vw.addMemoryMap(pva, pgm.p_flags & 0x7, fname, bytez) #FIXME perms
        else:
            logger.info('Skipping: %s', repr(pgm))

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
            new_functions.append(("init_function", sva))

        elif sname == ".init_array":
            # handle pseudo-fixups first: these pointers require base-addresses
            psize = vw.getPointerSize()
            pfmt = e_bits.le_fmt_chars[psize]   #FIXME: make Endian-aware (needs plumbing through ELF)
            secbytes = elf.readAtRva(sec.sh_addr, size)
            sh_addr = sec.sh_addr
            if addbase: sh_addr += baseaddr

            ptr_count = 0
            for off in range(0, size, psize):
                addr, = struct.unpack_from(pfmt, secbytes, off)
                if addbase: addr += baseaddr
                
                new_pointers.append((sh_addr + off, addr))
                vw.makeName(addr, "init_function_%d" % ptr_count, filelocal=True)
                vw.addXref(sh_addr + off, addr, REF_PTR)
                new_functions.append(("init_function", addr))
                ptr_count += 1

        elif sname == ".fini":
            vw.makeName(sva, "fini_function", filelocal=True)
            new_functions.append(("fini_function", sva))

        elif sname == ".fini_array":
            # handle pseudo-fixups first: these pointers require base-addresses
            psize = vw.getPointerSize()
            pfmt = e_bits.le_fmt_chars[psize]   #FIXME: make Endian-aware (needs plumbing through ELF)
            secbytes = elf.readAtRva(sec.sh_addr, size)
            sh_addr = sec.sh_addr
            if addbase: sh_addr += baseaddr

            ptr_count = 0
            for off in range(0, size, psize):
                addr, = struct.unpack_from(pfmt, secbytes, off)
                if addbase: addr += baseaddr
                
                new_pointers.append((sh_addr + off, addr))
                vw.makeName(addr, "fini_function_%d" % ptr_count, filelocal=True)
                vw.addXref(sec.sh_addr + off, addr, REF_PTR)
                new_functions.append(("fini_array entry", addr))
                ptr_count += 1

        elif sname == ".dynamic": # Imports
            makeDynamicTable(vw, sva, sva+size)

        # FIXME section names are optional, use dynamic info from .dynamic
        elif sname == ".dynstr": # String table for dynamics
            makeStringTable(vw, sva, sva+size)

        elif sname == ".dynsym":
            logger.debug("LINK\t%r",sec.sh_link)
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

    # get "Dynamics" based items, like NEEDED libraries (dependencies)
    for d in elf.getDynamics():
        if d.d_tag == Elf.DT_NEEDED:
            name = d.getName()
            name = name.split('.')[0].lower()
            vw.addLibraryDependancy(name)
        else:
            logger.debug("DYNAMIC DYNAMIC DYNAMIC\t%r",d)

    # Let pyelf do all the stupid string parsing...
    dsyms = elf.getDynSyms()
    relocs = elf.getRelocs()
    for r in relocs:
        rtype = Elf.getRelocType(r.r_info)
        rlva = r.r_offset
        if addbase: rlva += baseaddr
        try:
            # If it has a name, it's an externally
            # resolved "import" entry, otherwise, just a regular reloc
            name = r.getName()
            dmglname = demangle(name)
            logger.debug('relocs: 0x%x: %r', rlva, name)
            if arch in ('i386','amd64'):
                if name:
                    if rtype == Elf.R_386_JMP_SLOT:
                        vw.makeImport(rlva, "*", name)
                        vw.setComment(rlva, dmglname)

                    elif rtype == Elf.R_386_32:
                        pass

                    elif rtype == Elf.R_X86_64_GLOB_DAT:    # Elf.R_386_GLOB_DAT is same number
                        vw.makeImport(rlva, "*", name)
                        vw.setComment(rlva, dmglname)

                    else:
                        logging.info('unknown reloc type: %d %s (at %s)', rtype, name, hex(rlva))
                        

            if arch in ('arm', 'thumb', 'thumb16'):
                if rtype == Elf.R_ARM_JUMP_SLOT:
                    symidx = Elf.getRelocSymTabIndex(r.r_info)
                    sym = dsyms[symidx]

                    ptr = sym.st_value

                    #quick check to make sure we don't provide this symbol
                    if ptr:
                        logger.info('R_ARM_JUMP_SLOT: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        vw.addRelocation(rlva, vivisect.RTYPE_BASEOFF, ptr)
                        pname = "ptr_%s" % name
                        if vw.vaByName(pname) == None:
                            vw.makeName(rlva, pname)

                        if addbase: ptr += baseaddr
                        vw.makeName(ptr, name)
                        vw.setComment(ptr, dmglname)
                    else:
                        logger.info('R_ARM_JUMP_SLOT: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", name)
                        vw.setComment(rlva, dmglname)

                elif rtype == Elf.R_ARM_GLOB_DAT:
                    symidx = Elf.getRelocSymTabIndex(r.r_info)
                    sym = dsyms[symidx]
                    ptr = sym.st_value

                    #quick check to make sure we don't provide this symbol
                    if ptr:
                        logger.info('R_ARM_GLOB_DAT: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        vw.addRelocation(rlva, vivisect.RTYPE_BASEOFF, ptr)
                        pname = "ptr_%s" % name
                        if vw.vaByName(pname) == None:
                            vw.makeName(rlva, pname)

                        if addbase: ptr += baseaddr
                        vw.makeName(ptr, name)
                        vw.setComment(ptr, dmglname)
                    else:
                        logger.info('R_ARM_GLOB_DAT: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", name)
                        vw.setComment(rlva, dmglname)

                elif rtype == Elf.R_ARM_ABS32:
                    symidx = Elf.getRelocSymTabIndex(r.r_info)
                    sym = dsyms[symidx]
                    ptr = sym.st_value

                    if ptr:
                        logger.info('R_ARM_ABS32: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        vw.addRelocation(rlva, vivisect.RTYPE_BASEOFF, ptr)
                    else:
                        logger.info('R_ARM_ABS32: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", name)

                    vw.setComment(rlva, dmglname)

                elif rtype == Elf.R_ARM_RELATIVE:   # Adjust locations for the rebasing
                    ptr = vw.readMemoryPtr(rlva)
                    logger.info('R_ARM_RELATIVE: adding Relocation 0x%x -> 0x%x (name: %s) ', rlva, ptr, dmglname)
                    vw.addRelocation(rlva, vivisect.RTYPE_BASEOFF, ptr)
                    if len(name):
                        vw.makeName(rlva, name, makeuniq=True)
                        vw.setComment(rlva, dmglname)

                else:
                    logger.warn('unknown reloc type: %d %s (at %s)' % (rtype, name, hex(rlva)))

        except vivisect.InvalidLocation, e:
            logger.warn("NOTE\t%r",e)

    # process Dynamic Symbols
    for s in elf.getDynSyms():
        stype = s.getInfoType()
        sva = s.st_value

        if sva == 0:
            continue
        if addbase: sva += baseaddr
        if sva == 0:
            continue

        dmglname = demangle(s.name)
        logger.debug('dynsyms: 0x%x: %r', sva, dmglname)

        if stype == Elf.STT_FUNC or (stype == Elf.STT_GNU_IFUNC and arch in ('i386','amd64')):   # HACK: linux is what we're really after.
            try:
                new_functions.append(("DynSym: STT_FUNC", sva))
                vw.addExport(sva, EXP_FUNCTION, s.name, fname)
                vw.setComment(sva, dmglname)
            except Exception, e:
                vw.vprint('addExport Failure: (%s) %s' % (s.name, e))

        elif stype == Elf.STT_OBJECT:
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, s.name, fname)
                    vw.setComment(sva, dmglname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        elif stype == Elf.STT_HIOS:
            # So aparently Elf64 binaries on amd64 use HIOS and then
            # s.st_other cause that's what all the kewl kids are doing...
            sva = s.st_other
            if addbase: sva += baseaddr
            if vw.isValidPointer(sva):
                try:
                    new_functions.append(("DynSym: STT_HIOS", sva))
                    vw.addExport(sva, EXP_FUNCTION, s.name, fname)
                    vw.setComment(sva, dmglname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        elif stype == 14:# OMG WTF FUCK ALL THIS NONSENSE! FIXME
            sva = s.st_other
            if addbase: sva += baseaddr
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, s.name, fname)
                    vw.setComment(sva, dmglname)
                except Exception, e:
                    vw.vprint('WARNING: %s' % e)

        else:
            logger.debug("DYNSYM DYNSYM\t%r\t%r\t%r\t%r",s,s.getInfoType(),'other',hex(s.st_other))

    vw.addVaSet("FileSymbols", (("Name",VASET_STRING),("va",VASET_ADDRESS)))
    vw.addVaSet("WeakSymbols", (("Name",VASET_STRING),("va",VASET_ADDRESS)))

    # apply symbols to workspace (if any)
    impvas = [va for va,x,y,z in vw.getImports()]
    expvas = [va for va,x,y,z in vw.getExports()]
    for s in elf.getSymbols():
        sva = s.st_value
        logger.debug('symbol val: 0x%x\ttype: %r\tbind: %r\t name: %r',
                sva, 
                Elf.st_info_type.get(s.st_info, s.st_info),
                Elf.st_info_bind.get(s.st_other, s.st_other),
                s.name)

        if s.st_info == Elf.STT_FILE:
            vw.setVaSetRow('FileSymbols', (s.name, sva))
            continue
            
        if s.st_info == Elf.STT_NOTYPE:
            # mapping symbol
            if arch in ('arm', 'thumb', 'thumb16'):
                symname = s.getName()
                if addbase: sva += baseaddr
                if symname == '$a':
                    # ARM code
                    logger.info('mapping (NOTYPE) ARM symbol: 0x%x: %r',sva, s.name)
                    #vw.makeCode(sva)
                    new_functions.append(("Mapping Symbol: $a", sva))

                elif symname == '$t':
                    # Thumb code
                    logger.info('mapping (NOTYPE) Thumb symbol: 0x%x: %r',sva, s.name)
                    #vw.makeCode(sva)
                    new_functions.append(("Mapping Symbol: $t", sva + 1))

                elif symname == '$d':
                    # Data Items (eg. literal pool)
                    logger.info('mapping (NOTYPE) data symbol: 0x%x: %r',sva, s.name)
                    #vw.followPointer(sva)
                    data_ptrs.append(sva)


        # if the symbol has a value of 0, it is likely a relocation point which gets updated
        sname = normName(s.name)
        if sva == 0:
            for reloc in relocs:
                rname = normName(reloc.name)
                if rname == sname:
                    sva = reloc.r_offset
                    logger.info('sva==0, using relocation name: %x: %r', sva, rname)
                    break

        dmglname = demangle(sname)

        # TODO: make use of _ZTSN (typeinfo) and _ZTVN (vtable) entries if name demangles cleanly

        if addbase: sva += baseaddr
        if vw.isValidPointer(sva) and len(dmglname):
            try:
                if s.st_other == Elf.STB_WEAK:
                    logger.info('WEAK symbol: 0x%x: %r', sva, sname)
                    vw.setVaSetRow('WeakSymbols', (sname, sva))
                    dmglname = '__weak_' + dmglname

                if sva in impvas or sva in expvas:
                    imps = [imp for imp in vw.getImports() if imp[0] == sva]
                    exps = [exp for exp in vw.getExports() if exp[0] == sva]
                    logger.debug('skipping Symbol naming for existing Import/Export: 0x%x (%r) (%r) (%r)', sva, s.name, imps, exps)
                else:
                    vw.makeName(sva, dmglname, filelocal=True, makeuniq=True)

            except Exception, e:
                logger.warn("WARNING:\t%r",e)

        if s.st_info == Elf.STT_FUNC:
            new_functions.append(("STT_FUNC", sva))

    if addbase:
        eentry = baseaddr + elf.e_entry
    else:
        eentry = elf.e_entry

    if vw.isValidPointer(eentry):
        vw.addExport(eentry, EXP_FUNCTION, '__entry', fname)
        new_functions.append(("ELF Entry", eentry))
        
    if vw.isValidPointer(baseaddr):
        vw.makeStructure(baseaddr, "elf.Elf32")

    # do we add data_ptrs here?  ideally they would be marked out, but analyzed after all other analysis...
    # for now, ignore them.
    for cmnt, fva in new_functions:
        logger.info('adding function from ELF metadata: 0x%x (%s)', fva, cmnt)
        vw.makeFunction(fva)

    for va, tva in new_pointers:
        logger.info('adding pointer 0x%x -> 0x%x', va, tva)
    return fname

def normName(name):
    '''
    Normalize symbol names.  ie. drop the @@GOBBLEDEGOOK from the end
    '''
    atidx = name.find('@@')
    if atidx > -1:
        name = name[:atidx]
    return name

def demangle(name):
    '''
    Translate C++ mangled name back into the verbose C++ symbol name (with helpful type info)
    '''
    name = normName(name)

    try:
        import cxxfilt
        name = cxxfilt.demangle(name)
    except Exception, e:
        logger.debug('failed to demangle name (%r): %r', name, e)

    return name
