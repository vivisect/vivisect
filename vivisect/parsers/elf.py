import struct
import logging
import traceback
import collections

import Elf
import Elf.elf_lookup as elf_lookup

import envi.bits as e_bits
import envi.const as e_const

import vivisect
import vivisect.parsers as v_parsers

from vivisect.const import *

from io import BytesIO


logger = logging.getLogger(__name__)

# FIXME: So this is terrible, but until we unite everything under one package
# namespace to rule them all, we need this to avoid a stupid amount of logspam
# but we can't just force things under
elog = logging.getLogger(Elf.__name__)
elog.setLevel(logger.getEffectiveLevel())


def parseFile(vw, filename, baseaddr=None):
    fd = open(filename, 'rb')
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename, baseaddr=baseaddr)

def parseBytes(vw, bytes, baseaddr=None):
    fd = BytesIO(bytes)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, baseaddr=baseaddr)

def parseFd(vw, fd, filename=None, baseaddr=None):
    fd.seek(0)
    elf = Elf.Elf(fd)
    return loadElfIntoWorkspace(vw, elf, filename=filename, baseaddr=baseaddr)

def parseMemory(vw, memobj, baseaddr):
    raise Exception('FIXME implement parseMemory for elf!')

def getMemBaseAndSize(vw, elf, baseaddr=None):
    '''
    Returns the default baseaddr and memory size required to load the file
    '''
    savebase = baseaddr

    memmaps = getMemoryMapInfo(elf)
    baseaddr = 0xffffffffffffffffffffffff
    topmem = 0

    for mapva, mperms, mname, mbytes, malign in memmaps:
        if mapva < baseaddr:
            baseaddr = mapva & -e_const.PAGE_SIZE   # align to page-size
        endva = mapva + len(mbytes)
        if endva > topmem:
            topmem = endva

    size = topmem - baseaddr

    if baseaddr == 0 and not elf.isRelocatable():
        baseaddr = vw.config.viv.parsers.elf.baseaddr
        
    if savebase:
        # if we provided a baseaddr, override what the file wants
        baseaddr = savebase
        
    return baseaddr, size



def getMemoryMapInfo(elf, fname=None, baseaddr=None):
    '''
    Gets the default baseaddr and memory map information
    All the information necessary to add memory maps (or get overall size info)
    '''
    memmaps = []

    addbase, baseoff, baseaddr = getAddBaseAddr(elf, baseaddr)

    pgms = elf.getPheaders()
    for pgm in pgms:
        if pgm.p_type == Elf.PT_LOAD:
            if pgm.p_memsz == 0:
                continue
            logger.info('Loading: %s', pgm)
            bytez = elf.readAtOffset(pgm.p_offset, pgm.p_filesz)
            bytez += b'\x00' * (pgm.p_memsz - pgm.p_filesz)
            pva = pgm.p_vaddr
            pva += baseoff
            memmaps.append((pva, pgm.p_flags & 0x7, fname, bytez, e_const.PAGE_SIZE))
        else:
            logger.info('Skipping: %s', pgm)

    if len(pgms) == 0:
        # NOTE: among other file types, Linux Kernel modules have no program headers
        secs = elf.getSections()
        # fall back to loading sections as best we can...
        logger.info('elf: no program headers found! (in %r)', fname)

        maps = [ [s.sh_offset,s.sh_size,s.sh_addralign] for s in secs if s.sh_offset and s.sh_size ]
        maps.sort()

        merged = []
        for i in range(len(maps)):

            if merged and maps[i][0] == (merged[-1][0] + merged[-1][1]):
                merged[-1][1] += maps[i][1]
                continue

            merged.append( maps[i] )

        for offset,size,align in merged:
            bytez = elf.readAtOffset(offset,size)
            memmaps.append((baseaddr + offset, 0x7, fname, bytez, align))

        for sec in secs:
            if sec.sh_offset and sec.sh_size:
                sec.sh_addr = baseaddr + sec.sh_offset

    return memmaps



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
            except Exception as e:
                logger.warning("makeStringTable\t%r", e)
                return

def makeSymbolTable(vw, va, maxva):
    ret = []
    sname = 'elf.Elf%dSymbol' % (vw.getPointerSize() * 8)
    while va < maxva:
        s = vw.makeStructure(va, sname)
        ret.append(s)
        va += len(s)
    return ret

def makeDynamicTable(vw, va, maxva, baseoff=0):
    logger.debug("0x%x -> 0x%x", va, maxva)
    ret = []
    sname = 'elf.Elf%dDynamic' % (vw.getPointerSize() * 8)
    while va < maxva:
        s = vw.makeStructure(va, sname)
        ret.append(s)
        dtag = s.d_tag
        dtype = Elf.dt_types.get(dtag, "Unknown Dynamic Type")
        vw.setComment(va, dtype)
        va += len(s)
        if dtag == Elf.DT_NULL:
            break
    return ret

def makeRelocTable(vw, va, maxva, baseoff, addend=False):
    if addend:
        sname = 'elf.Elf%dReloca' % (vw.getPointerSize() * 8)
    else:
        sname = 'elf.Elf%dReloc' % (vw.getPointerSize() * 8)

    while va < maxva:
        s = vw.makeStructure(va, sname)
        tname = Elf.r_types_386.get(Elf.getRelocType(s.r_info), "Unknown Type")
        vw.setComment(va, tname)
        va += len(s)

def makeFunctionTable(elf, vw, tbladdr, size, tblname, funcs, ptrs, baseoff=0):
    logger.debug('makeFunctionTable(tbladdr=0x%x, size=0x%x, tblname=%r,  baseoff=0x%x)', tbladdr, size, tblname, baseoff)
    psize = vw.getPointerSize()
    fmtgrps = e_bits.fmt_chars[vw.getEndian()]
    pfmt = fmtgrps[psize]
    secbytes = elf.readAtRva(tbladdr, size)
    tbladdr += baseoff

    ptr_count = 0
    for off in range(0, size, psize):
        addr, = struct.unpack_from(pfmt, secbytes, off)
        addr += baseoff

        nstub = tblname + "_%d"
        pname = nstub % ptr_count

        vw.makeName(addr, pname, filelocal=True, makeuniq=True)
        ptrs.append((tbladdr + off, addr, pname))
        funcs.append((pname, addr))
        ptr_count += 1


arch_names = {
    Elf.EM_ARM: 'arm',
    Elf.EM_386: 'i386',
    Elf.EM_X86_64: 'amd64',
    Elf.EM_MSP430: 'msp430',
}

archcalls = {
    'i386': 'cdecl',
    'amd64': 'sysvamd64call',
    'arm': 'armcall',
    'thumb': 'armcall',
    'thumb16': 'armcall',
}

def getAddBaseAddr(elf, baseaddr=None):
    '''
    # NOTE: This is only for prelink'd so's and exe's.  Make something for old style so.
    '''
    baseoff = 0
    logger.debug("baseaddr: %r\tbaseoff: 0x%x", baseaddr, baseoff)
    elfbaseaddr = elf.getBaseAddress()
    if baseaddr is None:
        baseaddr = elfbaseaddr

    if not elf.isPreLinked() and elf.isSharedObject():
        addbase = True
        baseoff = baseaddr

    elif elf.isRelocatable():
        addbase = True
        baseoff = 0

    else:
        addbase = False
        baseoff = baseaddr - elfbaseaddr

    logger.debug("baseaddr: %r\tbaseoff: 0x%x", baseaddr, baseoff)
    return addbase, baseoff, baseaddr

def loadElfIntoWorkspace(vw, elf, filename=None, baseaddr=None):
    # analysis of discovered functions and data locations should be stored until the end of loading
    logger.info("loadElfIntoWorkspace(filename=%r, baseaddr: %r", filename, baseaddr)
    data_ptrs = []
    new_pointers = []
    new_functions = []

    # get baseaddr and size, then make sure we have a good baseaddr
    filebaseaddr, size = getMemBaseAndSize(vw, elf, baseaddr=baseaddr)
    if baseaddr is None:
        baseaddr = filebaseaddr

    logger.debug('initial file baseva: 0x%x  size: 0x%x', baseaddr, size)
    baseaddr = vw.findFreeMemoryBlock(size, baseaddr)
    logger.debug("loading %r (size: 0x%x) at 0x%x", filename, size, baseaddr)

    arch = arch_names.get(elf.e_machine)
    if arch is None:
       raise Exception("Unsupported Architecture: %d\n", elf.e_machine)

    platform = elf.getPlatform()

    # setup needed platform/format
    vw.setMeta('Architecture', arch)
    vw.setMeta('Platform', platform)
    vw.setMeta('Format', 'elf')
    vw.parsedbin = elf
    # Treat the event system veeery carefully
    byts = elf.getFileBytes()
    vw.setMeta('FileBytes', v_parsers.compressBytes(byts))

    vw.setMeta('DefaultCall', archcalls.get(arch,'unknown'))

    vw.addNoReturnApi("*.abort")
    vw.addNoReturnApi("*.exit")
    vw.addNoReturnApi("*._exit")
    vw.addNoReturnApi("*.longjmp")
    vw.addNoReturnApi("*._setjmp")
    vw.addNoReturnApi("*.j__ZSt9terminatev")
    vw.addNoReturnApi("*.std::terminate(void)")
    vw.addNoReturnApi("*.__assert_fail")
    vw.addNoReturnApi("*.__stack_chk_fail")
    vw.addNoReturnApi("*.pthread_exit")
    vw.addNoReturnApi("*.longjmp")

    # for VivWorkspace, MSB==1, LSB==0... which is the same as True/False for Big-Endian
    vw.setEndian(elf.getEndian())

    # Base addr is earliest section address rounded to pagesize
    # Some ELF's require adding the baseaddr to most/all later addresses
    addbase, baseoff, baseaddr = getAddBaseAddr(elf, baseaddr)
    logger.debug("Loading ELF into workspace: addbase: %r, baseoff: 0x%x, baseaddr: 0x%x", addbase, baseoff, baseaddr)

    elf.fd.seek(0)
    md5hash = v_parsers.md5Bytes(byts)
    sha256 = v_parsers.sha256Bytes(byts)

    if filename is None:
        # see if dynamics DT_SONAME holds a name for us
        for dyn in elf.getDynamics():
            if dyn.d_tag == Elf.DT_SONAME:
                filename = dyn.getName()

        # if all else fails, fallback
        if filename is None:
            filename = "elf_%.8x" % baseaddr

    fname = vw.addFile(filename.lower(), baseaddr, md5hash)
    vw.setFileMeta(fname, 'sha256', sha256)
    vw.setFileMeta(fname, 'relro', getRelRo(elf))
    vw.setFileMeta(fname, 'canaries', hasStackCanaries(vw))
    vw.setFileMeta(fname, 'nx', hasNX(elf))
    vw.setFileMeta(fname, 'pie', hasPIE(elf))
    vw.setFileMeta(fname, 'rpath', hasRPATH(elf))
    vw.setFileMeta(fname, 'runpath', hasRUNPATH(elf))
    vw.setFileMeta(fname, 'stripped', isStripped(elf))

    secnames = []
    for sec in elf.getSections():
        secnames.append(sec.getName())

    secs = elf.getSections()

    for mmapva, mmperms, mfname, mbytez, malign in getMemoryMapInfo(elf, fname, baseaddr):
        logger.debug("vw.addMemoryMap(0x%x, 0x%x, %r, 0x%x, 0x%x)", mmapva, mmperms, mfname, len(mbytez), malign)
        vw.addMemoryMap(mmapva, mmperms, mfname, mbytez, malign)

    # First add all section definitions so we have them
    for sec in secs:
        sname = sec.getName()
        size = sec.sh_size
        if sec.sh_addr == 0:
            continue # Skip non-memory mapped sections

        sva = sec.sh_addr
        sva += baseoff

        vw.addSegment(sva, size, sname, fname)

    # since getFileByVa is based on segments, and ELF Sections seldom cover all the
    # loadable memory space.... we'll add PT_LOAD Program Headers, only at the
    # end.  If we add them first, they're always the matching segments.  At the 
    # end, they make more of a default segment
    pcount = 0
    if vw.getFileByVa(baseaddr) is None:
        for phdr in elf.getPheaders():
            if phdr.p_type != Elf.PT_LOAD:
                continue

            sva = phdr.p_vaddr
            sva += baseoff

            vw.addSegment(sva, phdr.p_memsz, 'PHDR%d' % pcount, fname)
            pcount += 1

    # load information from dynamics:
    f_init = elf.dyns.get(Elf.DT_INIT)
    if f_init is not None:
        f_init += baseoff
        vw.makeName(f_init, "init_function", filelocal=True, makeuniq=True)
        vw.addEntryPoint(f_init)

    f_fini = elf.dyns.get(Elf.DT_FINI)
    if f_fini is not None:
        f_fini += baseoff
        vw.makeName(f_fini, "fini_function", filelocal=True, makeuniq=True)
        vw.addEntryPoint(f_fini)

    f_inita = elf.dyns.get(Elf.DT_INIT_ARRAY)
    if f_inita is not None:
        f_initasz = elf.dyns.get(Elf.DT_INIT_ARRAYSZ)
        makeFunctionTable(elf, vw, f_inita, f_initasz, 'init_array', new_functions, new_pointers, baseoff)

    f_finia = elf.dyns.get(Elf.DT_FINI_ARRAY)
    if f_finia is not None:
        f_finiasz = elf.dyns.get(Elf.DT_FINI_ARRAYSZ)
        makeFunctionTable(elf, vw, f_finia, f_finiasz, 'fini_array', new_functions, new_pointers, baseoff)

    f_preinita = elf.dyns.get(Elf.DT_PREINIT_ARRAY)
    if f_preinita is not None:
        f_preinitasz = elf.dyns.get(Elf.DT_PREINIT_ARRAY)
        makeFunctionTable(elf, vw, f_preinita, f_preinitasz, 'preinit_array', new_functions, new_pointers, baseoff)

    # dynamic table
    phdr = elf.getDynPHdr()     # this is the Program Header which points at the DYNAMICS table, not the other way around.
    if phdr is not None:
        sva, size = phdr.p_vaddr, phdr.p_memsz
        sva += baseoff     # getDynInfo returns (offset, filesz)
        makeDynamicTable(vw, sva, sva+size, baseoff)
        # if there's no Dynamics PHDR, don't bother trying to parse it from Sections.  It doesn't exist.

    # dynstr table
    sva, size = elf.getDynStrTabInfo()
    if sva is not None:
        sva += baseoff
        makeStringTable(vw, sva, sva+size)

    # dynsyms table
    sva, symsz, size = elf.getDynSymTabInfo()
    if sva is not None:
        sva += baseoff
        logger.debug("making DynSym table: 0x%x secsize: 0x%x entsize: 0x%x", sva, size, symsz)
        [s for s in makeSymbolTable(vw, sva, sva+size)]

    # Now trigger section specific analysis
    # Test to make sure Dynamics info is king.  Sections info should not overwrite Dynamics
    for sec in secs:
        sname = sec.getName()
        size = sec.sh_size
        if sec.sh_addr == 0:
            continue # Skip non-memory mapped sections

        sva = sec.sh_addr
        sva += baseoff

        # if we've already defined a location at this address, skip it. (eg. DYNAMICS)
        if vw.getLocation(sva) == sva:
            continue

        if sname == ".interp":
            vw.makeString(sva)

        elif sname == ".init":
            init_tup = ("init_function", sva)
            if init_tup not in new_functions:
                vw.makeName(sva, "init_function", filelocal=True, makeuniq=True)
                new_functions.append(init_tup)

        elif sname == ".init_array":
            makeFunctionTable(elf, vw, sec.sh_addr, size, 'init_function', new_functions, new_pointers, baseoff)

        elif sname == ".fini":
            fini_tup = ("fini_function", sva)
            if fini_tup not in new_functions:
                vw.makeName(sva, "fini_function", filelocal=True, makeuniq=True)
                new_functions.append(fini_tup)

        elif sname == ".fini_array":
            makeFunctionTable(elf, vw, sec.sh_addr, size, 'fini_function', new_functions, new_pointers, baseoff)

        elif sname == ".dynamic":  # Imports
            makeDynamicTable(vw, sva, sva+size, baseoff)

        elif sname == ".dynstr":  # String table for dynamics
            makeStringTable(vw, sva, sva+size)

        elif sname == ".dynsym":
            [s for s in makeSymbolTable(vw, sva, sva+size)]

        # If the section is really a string table, do it
        if sec.sh_type == Elf.SHT_STRTAB:
            makeStringTable(vw, sva, sva+size)

        elif sec.sh_type == Elf.SHT_SYMTAB:
            makeSymbolTable(vw, sva, sva+size)

        elif sec.sh_type == Elf.SHT_REL:
            makeRelocTable(vw, sva, sva+size, baseoff)

        elif sec.sh_type == Elf.SHT_RELA:
            makeRelocTable(vw, sva, sva+size, baseoff, addend=True)

        if sec.sh_flags & Elf.SHF_STRINGS:
            makeStringTable(vw, sva, sva+size)

    # get "Dynamics" based items, like NEEDED libraries (dependencies)
    elfmeta = {}
    for d in elf.getDynamics():
        if d.d_tag == Elf.DT_NEEDED:
            name = d.getName()
            name = name.split('.')[0].lower()
            vw.addLibraryDependancy(name)
        else:
            logger.debug("DYNAMIC:\t%r", d)
        
        dval = d.d_value
        if d.d_tag in Elf.dt_rebase and addbase:
            dval += baseoff

        elfmeta[Elf.dt_names.get(d.d_tag)] = dval

    # TODO: create a VaSet instead? setMeta allows more free-form info,
    # but isn't currently accessible from the gui
    vw.setFileMeta(fname, 'ELF_DYNAMICS', elfmeta)
    vw.setFileMeta(fname, 'addbase', addbase)
    vw.setFileMeta(fname, 'baseoff', baseoff)

    # applyRelocs is specifically prior to "process Dynamic Symbols" because Dynamics-only symbols
    # (ie. not using Section Headers) may not get all the symbols.  Some ELF's simply list too
    # small a space using SYMTAB and SYMTABSZ
    postfix = applyRelocs(elf, vw, addbase, baseoff)

    # process Dynamic Symbols - this must happen *after* relocations, which can expand the size of this
    for s in elf.getDynSyms():
        stype = s.getInfoType()
        sva = s.st_value

        if sva == 0:
            continue

        sva += baseoff
        if sva == 0:
            continue

        dmglname = demangle(s.name)

        if stype == Elf.STT_FUNC or \
                (stype == Elf.STT_GNU_IFUNC and arch in ('i386', 'amd64')):   # HACK: linux is what we're really after.
            try:
                new_functions.append(("DynSym: STT_FUNC", sva))
                vw.addExport(sva, EXP_FUNCTION, dmglname, fname, makeuniq=True)
                vw.setComment(sva, s.name)
            except Exception as e:
                vw.vprint('addExport Failure: (%s) %s' % (s.name, e))

        elif stype == Elf.STT_OBJECT:
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, dmglname, fname, makeuniq=True)
                    vw.setComment(sva, s.name)
                except Exception:
                    vw.vprint('STT_OBJECT Warning: %s' % traceback.format_exc())

        elif stype == Elf.STT_HIOS:
            # So aparently Elf64 binaries on amd64 use HIOS and then
            # s.st_other cause that's what all the kewl kids are doing...
            sva = s.st_other
            sva += baseoff
            if vw.isValidPointer(sva):
                try:
                    new_functions.append(("DynSym: STT_HIOS", sva))
                    vw.addExport(sva, EXP_FUNCTION, dmglname, fname, makeuniq=True)
                    vw.setComment(sva, s.name)
                except Exception:
                    vw.vprint('STT_HIOS Warning:\n%s' % traceback.format_exc())

        elif stype == Elf.STT_MDPROC:    # there's only one that isn't HI or LO...
            sva = s.st_other
            sva += baseoff
            if vw.isValidPointer(sva):
                try:
                    vw.addExport(sva, EXP_DATA, dmglname, fname, makeuniq=True)
                    vw.setComment(sva, s.name)
                except Exception:
                    vw.vprint('STT_MDPROC Warning:\n%s' % traceback.format_exc())

        else:
            logger.debug("DYNSYM:\t%r\t%r\t%r\t%r", s, s.getInfoType(), 'other', hex(s.st_other))

        if dmglname in postfix:
            for rlva, addend in postfix[dmglname]:
                vw.addRelocation(rlva, RTYPE_BASEPTR, sva + addend - baseoff)

    vaSetNames = vw.getVaSetNames()
    if not 'FileSymbols' in vaSetNames:
        vw.addVaSet("FileSymbols", (("Name", VASET_STRING), ("va", VASET_ADDRESS)))
    if not 'WeakSymbols' in vaSetNames:
        vw.addVaSet("WeakSymbols", (("Name", VASET_STRING), ("va", VASET_ADDRESS)))

    # apply symbols to workspace (if any)
    relocs = [r for idx, r in elf.getRelocs()]
    impvas = [va for va, x, y, z in vw.getImports()]
    expvas = [va for va, x, y, z in vw.getExports()]
    for s in elf.getSymbols():
        sva = s.st_value
        shndx = s.st_shndx
        if elf.isRelocatable():
            if shndx == elf_lookup.SHN_ABS:
                pass
            elif shndx in elf_lookup.shn_special_section_indices:
                # TODO: We should do things with SHN_ABS
                pass
            else:
                section = elf.getSectionByIndex(shndx)
                if section:
                    sva += section.sh_addr

        dmglname = demangle(s.name)
        logger.debug('symbol val: 0x%x\ttype: %r\tbind: %r\t name: %r', sva,
                                                                        Elf.st_info_type.get(s.getInfoType(), s.st_info),
                                                                        Elf.st_info_bind.get(s.getInfoBind(), s.st_other),
                                                                        s.name)

        symtype = s.getInfoType()
        if symtype == Elf.STT_FILE:
            vw.setVaSetRow('FileSymbols', (dmglname, sva))
            continue

        elif symtype == Elf.STT_NOTYPE:
            # mapping symbol
            if arch in ('arm', 'thumb', 'thumb16'):
                symname = s.getName()
                sva += baseoff
                if symname == '$a':
                    # ARM code
                    logger.info('mapping (NOTYPE) ARM symbol: 0x%x: %r', sva, dmglname)
                    new_functions.append(("Mapping Symbol: $a", sva))

                elif symname == '$t':
                    # Thumb code
                    logger.info('mapping (NOTYPE) Thumb symbol: 0x%x: %r', sva, dmglname)
                    new_functions.append(("Mapping Symbol: $t", sva + 1))

                elif symname == '$d':
                    # Data Items (eg. literal pool)
                    logger.info('mapping (NOTYPE) data symbol: 0x%x: %r', sva, dmglname)
                    data_ptrs.append(sva)
        elif symtype == Elf.STT_OBJECT:
            symname = s.getName()
            sva += baseoff
            if symname:
                vw.makeName(sva, symname, filelocal=True, makeuniq=True)
                valu = vw.readMemoryPtr(sva)
                if not vw.isValidPointer(valu) and s.st_size == vw.psize:
                    vw.makePointer(sva, follow=False)
                else:
                    '''
                    Most of this is replicated in makePointer with follow=True. We specifically don't use that,
                    since that kicks off a bunch of other analysis that isn't safe to run yet (it blows up in
                    fun ways), but we still want these locations made first, so that other analysis modules know
                    to not monkey with these and so I can set sizes and what not.
                    And while ugly, this does cover a couple nice use cases like pointer tables/arrays of pointers being present.
                    '''
                    if not valu:
                        # do a double check to make sure we can even make a pointer this large
                        # because some relocations like __FRAME_END__ might end up short
                        psize = vw.getPointerSize()
                        byts = vw.readMemory(sva, psize)
                        if len(byts) == psize:
                            new_pointers.append((sva, valu, symname))
                    elif vw.isProbablyUnicode(sva):
                        vw.makeUnicode(sva, size=s.st_size)
                    elif vw.isProbablyString(sva):
                        vw.makeString(sva, size=s.st_size)
                    elif s.st_size % vw.getPointerSize() == 0 and s.st_size >= vw.getPointerSize():
                        # so it could be something silly like an array
                        for addr in range(sva, sva+s.st_size, vw.psize):
                            valu = vw.readMemoryPtr(addr)
                            if vw.isValidPointer(valu):
                                new_pointers.append((addr, valu, symname))
                    else:
                        vw.makeNumber(sva, size=s.st_size)

        # if the symbol has a value of 0, it is likely a relocation point which gets updated
        sname = demangle(s.name)
        if sva == 0:
            for reloc in relocs:
                rname = demangle(reloc.name)
                if rname == sname:
                    sva = reloc.r_offset
                    logger.info('sva==0, using relocation name: %x: %r', sva, rname)
                    break

        dmglname = demangle(sname)

        # TODO: make use of _ZTSN (typeinfo) and _ZTVN (vtable) entries if name demangles cleanly

        sva += baseoff
        if vw.isValidPointer(sva) and len(dmglname):
            try:
                if s.getInfoBind() == Elf.STB_WEAK:
                    logger.info('WEAK symbol: 0x%x: %r', sva, sname)
                    vw.setVaSetRow('WeakSymbols', (sname, sva))
                    dmglname = '__weak_' + dmglname

                if sva in impvas or sva in expvas:
                    imps = [imp for imp in vw.getImports() if imp[0] == sva]
                    exps = [exp for exp in vw.getExports() if exp[0] == sva]
                    logger.debug('skipping Symbol naming for existing Import/Export: 0x%x (%r) (%r) (%r)', sva, s.name, imps, exps)
                else:
                    vw.makeName(sva, dmglname, filelocal=True, makeuniq=True)

            except Exception as e:
                logger.warning("%s" % str(e))

        if s.getInfoType() == Elf.STT_FUNC:
            new_functions.append(("STT_FUNC", sva))

    eentry = baseoff + elf.e_entry

    if vw.isValidPointer(eentry):
        vw.addExport(eentry, EXP_FUNCTION, '__entry', fname)
        new_functions.append(("ELF Entry", eentry))

    if vw.isValidPointer(baseaddr):
        sname = 'elf.Elf%d' % (vw.getPointerSize() * 8)
        vw.makeStructure(baseaddr, sname)

    # mark all the entry points for analysis later
    for cmnt, fva in new_functions:
        logger.info('adding function from ELF metadata: 0x%x (%s)', fva, cmnt)
        vw.addEntryPoint(fva)   # addEntryPoint queue's code analysis for later in the analysis pass

    # mark all the pointers for analysis later
    for va, tva, pname in new_pointers:
        logger.info('adding pointer 0x%x -> 0x%x', va, tva)
        vw.setVaSetRow('PointersFromFile', (va, tva, fname, pname))

    return fname


def applyRelocs(elf, vw, addbase=False, baseoff=0):
    '''
    process relocations / strings (relocs use Dynamic Symbols)
    '''
    postfix = collections.defaultdict(list)
    arch = arch_names.get(elf.e_machine)
    othr = None
    for secidx, r in elf.getRelocs():
        rtype = r.getType()
        rlva = r.r_offset
        if elf.isRelocatable():
            container = elf.getSectionByIndex(secidx)
            if container.sh_flags & elf_lookup.SHF_INFO_LINK:
                othr = elf.getSectionByIndex(container.sh_info)
                if othr:
                    rlva += othr.sh_addr

        rlva += baseoff

        try:
            # If it has a name, it's an externally resolved "import" entry,
            # otherwise, just a regular reloc
            name = r.getName()
            dmglname = demangle(name)
            logger.debug('relocs: 0x%x: %s (%s)', rlva, dmglname, name)
            if arch in ('i386', 'amd64'):
                if name:
                    #if dmglname == 
                    if rtype == Elf.R_X86_64_IRELATIVE:
                        # before making import, let's fix up the pointer as a BASEPTR Relocation
                        ptr = r.r_addend
                        rloc = vw.addRelocation(rlva, RTYPE_BASEPTR, ptr)
                        if rloc:
                            logger.info('Reloc: R_X86_64_IRELATIVE 0x%x', rlva)

                    if rtype in (Elf.R_386_JMP_SLOT, Elf.R_X86_64_GLOB_DAT, Elf.R_X86_64_IRELATIVE):
                        logger.info('Reloc: making Import 0x%x (name: %s/%s) ', rlva, name, dmglname)
                        vw.makeImport(rlva, "*", dmglname)
                        vw.setComment(rlva, name)

                    elif rtype == Elf.R_386_COPY:  # Also covers X86_64_COPY
                        # the linker is responsible for filling these in so we probably won't have these
                        vw.addRelocation(rlva, RTYPE_BASERELOC, 0)

                    elif rtype == Elf.R_386_32:  # Also covers X86_64_64
                        # a direct punch in plus an addend
                        # but things like libstc++ use this type for vtables in the rel.dyn
                        # section without actually specifying an addend
                        postfix[dmglname].append((rlva, getattr(r, 'r_addend', 0)))

                    else:
                        logger.warning('unknown reloc type: %d %s (at %s)', rtype, name, hex(rlva))
                        logger.info(r.tree())

                else:
                    if rtype == Elf.R_386_RELATIVE: # R_X86_64_RELATIVE is the same number
                        ptr = vw.readMemoryPtr(rlva)
                        logger.info('R_386_RELATIVE: adding Relocation 0x%x -> 0x%x (name: %s) ', rlva, ptr, dmglname)
                        vw.addRelocation(rlva, RTYPE_BASEPTR, ptr)

                    elif arch == 'amd64' and rtype == Elf.R_X86_64_32S:
                        # the same as R_386_32 except we don't always get a name.
                        ptr = r.r_addend
                        symbol = elf.getSymbols()[r.getSymTabIndex()]
                        valu = symbol.st_value
                        if symbol.getInfoType() == elf_lookup.STT_SECTION:
                            ref = elf.getSectionByIndex(symbol.st_shndx)
                            if ref:
                                valu = ref.sh_addr
                        vw.addRelocation(rlva, RTYPE_BASEOFF, data=symbol.st_value + ptr, size=4)

                    elif rtype == Elf.R_X86_64_IRELATIVE:
                        # first make it a relocation that is based on the imagebase
                        ptr = r.r_addend
                        logger.info('R_X86_64_IRELATIVE: adding Relocation 0x%x -> 0x%x (name: %r %r) ', rlva, ptr, name, dmglname)
                        rloc = vw.addRelocation(rlva, RTYPE_BASEPTR, ptr)
                        if rloc is not None:
                            continue

                        # next get the target and find a name, since the reloc itself doesn't have one
                        tgt = vw.readMemoryPtr(rlva)
                        tgtname = vw.getName(tgt)
                        if tgtname is not None:
                            logger.info('   name(0x%x): %r', tgt, tgtname)
                            fn, symname = tgtname.split('.', 1)
                            logger.info('Reloc: making Import 0x%x (name: %s.%s) ', rlva, fn, symname)
                            vw.makeImport(rlva, fn, symname)
                    # TODO: This isn't strictly wrong, but does induce graph building errors
                    #elif rtype == Elf.R_X86_64_PLT32:
                    #    # plt + addend- secoff
                    #    addend = r.r_addend
                    #    plt = elf.getSection('.plt')
                    #    if plt:
                    #        addend += plt.sh_addr
                    #    if othr:
                    #        addend -= othr.sh_addr
                    #    vw.addRelocation(rlva, RTYPE_BASEPTR, data=addend, size=4)
                    elif rtype == Elf.R_X86_64_TPOFF64:
                        pass
                    elif rtype == Elf.R_386_TLS_DTPMOD32:
                        pass
                    else:
                        logger.warning('unknown reloc type: %d %s (at %s)', rtype, name, hex(rlva))
                        logger.warning(r.tree())


            if arch in ('arm', 'thumb', 'thumb16'):
                # ARM REL entries require an addend that could be stored as a 
                # number or an instruction!
                import envi.archs.arm.const as eaac
                if r.vsHasField('addend'):
                    # this is a RELA object, bringing its own addend field!
                    addend = r.addend
                else:
                    # otherwise, we have to check the stored value for number or instruction
                    # if it's an instruction, we have to use the immediate value and then 
                    # figure out if it's negative based on the instruction!
                    try:
                        temp = vw.readMemoryPtr(rlva)
                        if rtype in Elf.r_armclasses[Elf.R_ARMCLASS_DATA] or rtype in Elf.r_armclasses[Elf.R_ARMCLASS_MISC]:
                            # relocation points to a DATA or MISCELLANEOUS location
                            addend = temp
                        else:
                            # relocation points to a CODE location (ARM, THUMB16, THUMB32)
                            op = vw.parseOpcode(rlva)
                            for oper in op.opers:
                                if hasattr(oper, 'val'):
                                    addend = oper.val
                                    break

                                elif hasattr(oper, 'offset'):
                                    addend = oper.offset
                                    break

                            lastoper = op.opers[-1]
                            if op.mnem.startswith('sub') or \
                                    op.mnem in ('ldr', 'str') and \
                                    hasattr(lastoper, 'pubwl') and \
                                    not (lastoper.pubwl & eaac.PUxWL_ADD):
                                        addend = -addend
                    except Exception as e:
                        logger.exception("ELF: Reloc Addend determination: %s", e)
                        addend = temp

                logger.debug('addend: 0x%x', addend)

                if rtype == Elf.R_ARM_JUMP_SLOT:
                    symidx = r.getSymTabIndex()
                    sym = elf.getDynSymbol(symidx)
                    ptr = sym.st_value

                    # quick check to make sure we don't provide this symbol
                    # some toolchains like to point the GOT back at it's PLT entry
                    # that does *not* mean it's not an IMPORT
                    if ptr and not isPLT(vw, ptr):
                        logger.info('R_ARM_JUMP_SLOT: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        # even if addRelocation fails, still make the name, same thing down in GLOB_DAT
                        if addbase:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASEPTR, ptr)
                        else:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASERELOC, ptr)
                        pname = "ptr_%s_%.8x" % (name, rlva)
                        if vw.vaByName(pname) is None:
                            vw.makeName(rlva, pname)

                        # name the target as well
                        ptr += baseoff
                        # normalize thumb addresses
                        ptr &= -2
                        vw.makeName(ptr, name)
                        vw.setComment(ptr, dmglname)

                    else:
                        logger.info('R_ARM_JUMP_SLOT: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", dmglname)
                        vw.setComment(rlva, name)

                elif rtype == Elf.R_ARM_GLOB_DAT:
                    symidx = r.getSymTabIndex()
                    sym = elf.getDynSymbol(symidx)
                    ptr = sym.st_value

                    if ptr:
                        logger.info('R_ARM_GLOB_DAT: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        if addbase:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASEPTR, ptr)
                        else:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASERELOC, ptr)
                        pname = "ptr_%s" % name

                        if vw.vaByName(pname) is None:
                            vw.makeName(rlva, pname)

                        ptr += baseoff
                        vw.makeImport(ptr, "*", dmglname)
                        vw.setComment(ptr, name)

                    else:
                        logger.info('R_ARM_GLOB_DAT: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", dmglname)
                        vw.setComment(rlva, name)

                elif rtype == Elf.R_ARM_ABS32:
                    symidx = r.getSymTabIndex()
                    sym = elf.getDynSymbol(symidx)
                    ptr = sym.st_value

                    if ptr:
                        logger.info('R_ARM_ABS32: adding Relocation 0x%x -> 0x%x (%s) ', rlva, ptr, dmglname)
                        vw.addRelocation(rlva, vivisect.RTYPE_BASEPTR, ptr)
                        pname = "ptr_%s" % name
                        if vw.vaByName(pname) is None and len(name):
                            vw.makeName(rlva, pname)

                    else:
                        logger.info('R_ARM_ABS32: adding Import 0x%x (%s) ', rlva, dmglname)
                        vw.makeImport(rlva, "*", dmglname)
                        vw.setComment(rlva, name)

                    vw.setComment(rlva, dmglname)

                elif rtype == Elf.R_ARM_RELATIVE:   # Adjust locations for the rebasing
                    ptr = vw.readMemoryPtr(rlva)
                    logger.info('R_ARM_RELATIVE: adding Relocation 0x%x -> 0x%x (name: %s) ', rlva, ptr, dmglname)
                    vw.addRelocation(rlva, vivisect.RTYPE_BASEPTR, ptr)
                    if len(name):
                        vw.makeName(rlva, dmglname, makeuniq=True)
                        vw.setComment(rlva, name)

                elif rtype == Elf.R_ARM_COPY:
                    pass

                else:
                    logger.warning('unknown reloc type: %d %s (at %s)', rtype, name, hex(rlva))
                    logger.info(r.tree())

        except vivisect.InvalidLocation as e:
            logger.warning("NOTE\t%r", e)

    return postfix

def isPLT(vw, va):
    '''
    Do a decent check to see if this va is in a PLT section
    '''
    seg = vw.getSegment(va)
    if seg is None:
        return False
    if seg[2].startswith('.plt'):
        return True
    return False

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
    except Exception as e:
        logger.debug('failed to demangle name (%r): %r', name, e)

    return name

def getRelRo(elf):
    status = 0
    for phdr in elf.getPheaders():
        if phdr.p_type == Elf.PT_GNU_RELRO:
            status = 1
            break

    if status:
        for dyn in elf.getDynamics():
            if dyn.d_tag == Elf.DT_FLAGS:
                if dyn.d_value == Elf.DF_BIND_NOW:
                    status = 2

    return ('NONE', 'Partial', 'FULL')[status]

def hasStackCanaries(vw):
    '''
    Check through imports looking for __stack_chk_fail
    '''
    for impva, impsz, imptype, impname in vw.getImports():
        if impname == '*.__stack_chk_fail':
            return True

    return False

def hasNX(elf):
    '''
    Check through ELF Pheaders
    '''
    for phdr in elf.getPheaders():
        if phdr.p_type == Elf.PT_GNU_STACK:
            if phdr.p_flags == 6:
                return True

    return False

def hasPIE(elf):
    '''
    Check through ELF Headers and Dynamics
    '''
    if elf.e_type == Elf.ET_DYN:
        if elf.dyns.get(Elf.DT_DEBUG) is not None:
            return True
        return "DSO"

    return False

def hasRPATH(elf):
    '''
    Check through ELF Dynamics
    '''
    if elf.dyns.get(Elf.DT_RPATH) is not None:
        return True

    return False

def hasRUNPATH(elf):
    '''
    Check through ELF Dynamics
    '''
    if elf.dyns.get(Elf.DT_RUNPATH) is not None:
        return True

    return False

def isStripped(elf):
    '''
    Check through ELF Symbols
    '''
    if len(elf.getSymbols()) == 0:
        return True

    return False


'''
Base Offsets are complicated, so let's break them down a bit.

Base Offsets originally refered to whether to add a base address to values to come up with a virtual address.
Variations of ELFs that regularly cause problems/differences:
    * Shared Objects
    * Kernel Modules / Object files
    * Prelinked SO's and EXEs

Accesses which are impacted by these addresses/offsets:
    * Pointer to Program Headers
    * Pointer to Section Headers
    * Program Headers
    * Sections
    * Dynamics Table
    * Dynamics Entries (see dt_rebase for existing list which require adding base offsets)
    Via either Sections or Dynamics:
        * String Table(s)
        * Symbol Table(s)
        * Relocs Table(s)
        * GOT
        * PLT
        * INIT / FINI
        * INIT_ARRAY / FINI_ARRAY / PREINIT_ARRAY
        * ???  Dwarf?

If a file isn't intended for relocation, this can cause problems because:
    * Pointers can be hard-coded into the instructions themselves
    * ELF headers/Dynamics can not understand the relocatable parts

    
'''
