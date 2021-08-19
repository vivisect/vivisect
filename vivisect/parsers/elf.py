import struct
import logging
import traceback
import collections

import Elf

import envi.bits as e_bits

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

def makeDynamicTable(vw, va, maxva):
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

def makeRelocTable(vw, va, maxva, addbase, baseaddr, addend=False):
    if addend:
        sname = 'elf.Elf%dReloca' % (vw.getPointerSize() * 8)
    else:
        sname = 'elf.Elf%dReloc' % (vw.getPointerSize() * 8)

    while va < maxva:
        s = vw.makeStructure(va, sname)
        tname = Elf.r_types_386.get(Elf.getRelocType(s.r_info), "Unknown Type")
        vw.setComment(va, tname)
        va += len(s)

def makeFunctionTable(elf, vw, tbladdr, size, tblname, funcs, ptrs, baseaddr=0, addbase=False):
    logger.debug('makeFunctionTable(tbladdr=0x%x, size=0x%x, tblname=%r,  baseaddr=0x%x)', tbladdr, size, tblname, baseaddr)
    psize = vw.getPointerSize()
    fmtgrps = e_bits.fmt_chars[vw.getEndian()]
    pfmt = fmtgrps[psize]
    secbytes = elf.readAtRva(tbladdr, size)
    if addbase:
        tbladdr += baseaddr

    ptr_count = 0
    for off in range(0, size, psize):
        addr, = struct.unpack_from(pfmt, secbytes, off)
        if addbase:
            addr += baseaddr

        nstub = tblname + "_%d"
        pname = nstub % ptr_count

        vw.makeName(addr, pname, filelocal=True)
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

    # for VivWorkspace, MSB==1, LSB==0... which is the same as True/False
    vw.setEndian(elf.getEndian())

    # Base addr is earliest section address rounded to pagesize
    # NOTE: This is only for prelink'd so's and exe's.  Make something for old style so.
    addbase = False
    if not elf.isPreLinked() and elf.isSharedObject():
        addbase = True
    if baseaddr is None:
        baseaddr = elf.getBaseAddress()

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

    pgms = elf.getPheaders()
    secs = elf.getSections()

    for pgm in pgms:
        if pgm.p_type == Elf.PT_LOAD:
            if pgm.p_memsz == 0:
                continue
            logger.info('Loading: %s', pgm)
            bytez = elf.readAtOffset(pgm.p_offset, pgm.p_filesz)
            bytez += b"\x00" * (pgm.p_memsz - pgm.p_filesz)
            pva = pgm.p_vaddr
            if addbase:
                pva += baseaddr
            vw.addMemoryMap(pva, pgm.p_flags & 0x7, fname, bytez)
        else:
            logger.info('Skipping: %s', pgm)

    if len(pgms) == 0:
        # fall back to loading sections as best we can...
        vw.vprint('elf: no program headers found!')

        maps = [ [s.sh_offset,s.sh_size] for s in secs if s.sh_offset and s.sh_size ]
        maps.sort()

        merged = []
        for i in range(len(maps)):

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
        if addbase:
            sva += baseaddr

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
            if addbase:
                sva += baseaddr

            vw.addSegment(sva, phdr.p_memsz, 'PHDR%d' % pcount, fname)
            pcount += 1

    # load information from dynamics:
    f_init = elf.dyns.get(Elf.DT_INIT)
    if f_init is not None:
        if addbase:
            f_init += baseaddr
        vw.makeName(f_init, "init_function", filelocal=True)
        vw.addEntryPoint(f_init)

    f_fini = elf.dyns.get(Elf.DT_FINI)
    if f_fini is not None:
        if addbase:
            f_fini += baseaddr
        vw.makeName(f_fini, "fini_function", filelocal=True)
        vw.addEntryPoint(f_fini)

    f_inita = elf.dyns.get(Elf.DT_INIT_ARRAY)
    if f_inita is not None:
        f_initasz = elf.dyns.get(Elf.DT_INIT_ARRAYSZ)
        makeFunctionTable(elf, vw, f_inita, f_initasz, 'init_array', new_functions, new_pointers, baseaddr, addbase)

    f_finia = elf.dyns.get(Elf.DT_FINI_ARRAY)
    if f_finia is not None:
        f_finiasz = elf.dyns.get(Elf.DT_FINI_ARRAYSZ)
        makeFunctionTable(elf, vw, f_finia, f_finiasz, 'fini_array', new_functions, new_pointers, baseaddr, addbase)

    f_preinita = elf.dyns.get(Elf.DT_PREINIT_ARRAY)
    if f_preinita is not None:
        f_preinitasz = elf.dyns.get(Elf.DT_PREINIT_ARRAY)
        makeFunctionTable(elf, vw, f_preinita, f_preinitasz, 'preinit_array', new_functions, new_pointers, baseaddr, addbase)

    # dynamic table
    phdr = elf.getDynPHdr()    # file offset?
    if phdr is not None:
        sva, size = phdr.p_vaddr, phdr.p_memsz
        if addbase:
            sva += baseaddr     # getDynInfo returns (offset, filesz)
        makeDynamicTable(vw, sva, sva+size)
        # if there's no Dynamics PHDR, don't bother trying to parse it from Sections.  It doesn't exist.

    # dynstr table
    sva, size = elf.getDynStrTabInfo()
    if sva is not None:
        if addbase:
            sva += baseaddr
        makeStringTable(vw, sva, sva+size)

    # dynsyms table
    sva, symsz, size = elf.getDynSymTabInfo()
    if sva is not None:
        if addbase:
            sva += baseaddr
        [s for s in makeSymbolTable(vw, sva, sva+size)]

    # Now trigger section specific analysis
    # Test to make sure Dynamics info is king.  Sections info should not overwrite Dynamics
    for sec in secs:
        sname = sec.getName()
        size = sec.sh_size
        if sec.sh_addr == 0:
            continue # Skip non-memory mapped sections

        sva = sec.sh_addr
        if addbase:
            sva += baseaddr

        # if we've already defined a location at this address, skip it. (eg. DYNAMICS)
        if vw.getLocation(sva) == sva:
            continue

        if sname == ".interp":
            vw.makeString(sva)

        elif sname == ".init":
            vw.makeName(sva, "init_function", filelocal=True)
            new_functions.append(("init_function", sva))

        elif sname == ".init_array":
            makeFunctionTable(elf, vw, sec.sh_addr, size, 'init_function', new_functions, new_pointers, baseaddr, addbase)

        elif sname == ".fini":
            vw.makeName(sva, "fini_function", filelocal=True)
            new_functions.append(("fini_function", sva))

        elif sname == ".fini_array":
            makeFunctionTable(elf, vw, sec.sh_addr, size, 'fini_function', new_functions, new_pointers, baseaddr, addbase)

        elif sname == ".dynamic":  # Imports
            makeDynamicTable(vw, sva, sva+size)

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
            makeRelocTable(vw, sva, sva+size, addbase, baseaddr)

        elif sec.sh_type == Elf.SHT_RELA:
            makeRelocTable(vw, sva, sva+size, addbase, baseaddr, addend=True)

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

        elfmeta[Elf.dt_names.get(d.d_tag)] = d.d_value

    # TODO: create a VaSet instead? setMeta allows more free-form info,
    # but isn't currently accessible from the gui
    vw.setFileMeta(fname, 'ELF_DYNAMICS', elfmeta)
    vw.setFileMeta(fname, 'addbase', addbase)

    # applyRelocs is specifically prior to "process Dynamic Symbols" because Dynamics-only symbols
    # (ie. not using Section Headers) may not get all the symbols.  Some ELF's simply list too
    # small a space using SYMTAB and SYMTABSZ
    postfix = applyRelocs(elf, vw, addbase, baseaddr)

    # process Dynamic Symbols - this must happen *after* relocations, which can expand the size of this
    for s in elf.getDynSyms():
        stype = s.getInfoType()
        sva = s.st_value

        if sva == 0:
            continue
        if addbase:
            sva += baseaddr
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
            if addbase:
                sva += baseaddr
            if vw.isValidPointer(sva):
                try:
                    new_functions.append(("DynSym: STT_HIOS", sva))
                    vw.addExport(sva, EXP_FUNCTION, dmglname, fname, makeuniq=True)
                    vw.setComment(sva, s.name)
                except Exception:
                    vw.vprint('STT_HIOS Warning:\n%s' % traceback.format_exc())

        elif stype == Elf.STT_MDPROC:    # there's only one that isn't HI or LO...
            sva = s.st_other
            if addbase:
                sva += baseaddr
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
                if addbase:
                    vw.addRelocation(rlva, RTYPE_BASEPTR, sva + addend - baseaddr)
                else:
                    vw.addRelocation(rlva, RTYPE_BASEPTR, sva + addend)

    vw.addVaSet("FileSymbols", (("Name", VASET_STRING), ("va", VASET_ADDRESS)))
    vw.addVaSet("WeakSymbols", (("Name", VASET_STRING), ("va", VASET_ADDRESS)))

    # apply symbols to workspace (if any)
    relocs = elf.getRelocs()
    impvas = [va for va, x, y, z in vw.getImports()]
    expvas = [va for va, x, y, z in vw.getExports()]
    for s in elf.getSymbols():
        sva = s.st_value
        dmglname = demangle(s.name)

        logger.debug('symbol val: 0x%x\ttype: %r\tbind: %r\t name: %r', sva,
                                                                        Elf.st_info_type.get(s.st_info, s.st_info),
                                                                        Elf.st_info_bind.get(s.st_other, s.st_other),
                                                                        s.name)

        if s.getInfoType() == Elf.STT_FILE:
            vw.setVaSetRow('FileSymbols', (dmglname, sva))
            continue

        elif s.getInfoType() == Elf.STT_NOTYPE:
            # mapping symbol
            if arch in ('arm', 'thumb', 'thumb16'):
                symname = s.getName()
                if addbase:
                    sva += baseaddr
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
        elif s.getInfoType() == Elf.STT_OBJECT:
            symname = s.getName()
            if addbase:
                sva += baseaddr
            if symname:
                vw.makeName(sva, symname, filelocal=True, makeuniq=True)
                valu = vw.readMemoryPtr(sva)
                if not vw.isValidPointer(valu) and s.st_size == vw.psize:
                    vw.makePointer(sva, follow=False)
                else:
                    '''
                    Most of this is replicated in makePointer with follow=True. We specifically don't use that, since that kicks off a bunch of other analysis that isn't safe to run yet (it blows up in fun ways), but we still want these locations made first, so that other analysis modules know to not monkey with these and so I can set sizes and what not. 
                    while ugly, this does cover a couple nice use cases like pointer tables/arrays of pointers being present.
                    '''
                    if not valu:
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

        if addbase:
            sva += baseaddr
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


def applyRelocs(elf, vw, addbase=False, baseaddr=0):
    '''
    process relocations / strings (relocs use Dynamic Symbols)
    '''
    postfix = collections.defaultdict(list)
    arch = arch_names.get(elf.e_machine)
    relocs = elf.getRelocs()
    logger.debug("reloc len: %d", len(relocs))
    for r in relocs:
        rtype = Elf.getRelocType(r.r_info)
        rlva = r.r_offset
        if addbase:
            rlva += baseaddr
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
                        vw.addRelocation(rlva, RTYPE_BASEPTR, ptr)
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

                    elif rtype == Elf.R_X86_64_IRELATIVE:
                        # first make it a relocation that is based on the imagebase
                        ptr = r.r_addend
                        logger.info('R_X86_64_IRELATIVE: adding Relocation 0x%x -> 0x%x (name: %r %r) ', rlva, ptr, name, dmglname)
                        vw.addRelocation(rlva, RTYPE_BASEPTR, ptr)

                        # next get the target and find a name, since the reloc itself doesn't have one
                        tgt = vw.readMemoryPtr(rlva)
                        tgtname = vw.getName(tgt)
                        if tgtname is not None:
                            logger.info('   name(0x%x): %r', tgt, tgtname)
                            fn, symname = tgtname.split('.', 1)
                            logger.info('Reloc: making Import 0x%x (name: %s.%s) ', rlva, fn, symname)
                            vw.makeImport(rlva, fn, symname)

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
                        if addbase:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASEPTR, ptr)
                        else:
                            vw.addRelocation(rlva, vivisect.RTYPE_BASERELOC, ptr)
                        pname = "ptr_%s_%.8x" % (name, rlva)
                        if vw.vaByName(pname) is None:
                            vw.makeName(rlva, pname)

                        # name the target as well
                        if addbase:
                            ptr += baseaddr
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

                        if addbase:
                            ptr += baseaddr
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
