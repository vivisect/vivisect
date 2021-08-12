"""
Kenshoto's Elf parser

This package will let you use programatic ninja-fu
when trying to parse Elf binaries.  The API is based
around several objects representing constructs in the
Elf binary format.  The Elf object itself contains
parsed metadata and lists of things like section headers
and relocation entries.  Additionally, most of the
objects implement repr() in some form or another which
allows you a bunch of readelf-like functionality.

*Eventually* this API will allow you to modify Elf binaries
and spit them back out in working order (not complete, you
may notice some of the initial code).

Send bug reports to rakuyo or at1as in the issue tracker
"""

# Copyright (C) 2007 Invisigoth - See LICENSE file for details
import io
import logging

from stat import *
from Elf.elf_lookup import *
import vstruct
import vstruct.defs.elf as vs_elf

logger = logging.getLogger(__name__)


class ElfReloc:
    """
    Elf relocation entries consist mostly of "fixup" address which
    are taken care of by the loader at runtime.  Things like
    GOT entries, PLT jmp codes etc all have an Elf relocation
    entry.
    """

    def __init__(self):
        self.name = ""

    def __repr__(self):
        return "reloc: @%s %d %s" % (hex(self.r_offset), self.getType(), self.getName())

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def getType(self):
        return self.r_info & 0xff


class Elf32Reloc(ElfReloc, vs_elf.Elf32Reloc):
    def __init__(self, bigend=False):
        vs_elf.Elf32Reloc.__init__(self, bigend=bigend)
        ElfReloc.__init__(self)

    def getSymTabIndex(self):
        return self.r_info >> 8


class Elf32Reloca(ElfReloc, vs_elf.Elf32Reloca):
    def __init__(self, bigend=False):
        vs_elf.Elf32Reloca.__init__(self, bigend=bigend)
        ElfReloc.__init__(self)

    def getSymTabIndex(self):
        return self.r_info >> 8


class Elf64Reloc(ElfReloc, vs_elf.Elf64Reloc):
    def __init__(self, bigend=False):
        vs_elf.Elf64Reloc.__init__(self, bigend=bigend)
        ElfReloc.__init__(self)

    def getSymTabIndex(self):
        return self.r_info >> 32


class Elf64Reloca(ElfReloc, vs_elf.Elf64Reloca):
    def __init__(self, bigend=False):
        vs_elf.Elf64Reloca.__init__(self, bigend=bigend)
        ElfReloc.__init__(self)

    def getSymTabIndex(self):
        return self.r_info >> 32


class ElfDynamic:
    """
    An object to represent an Elf dynamic entry.
    (linker/loader directives)
    """
    has_string = [DT_NEEDED, DT_SONAME]

    def __init__(self, bytes=None):
        self.name = ""

    def __repr__(self):
        name = self.getName()
        if not name:
            name = hex(self.d_value)
        return "%s %s" % (name, self.getTypeName())

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getTypeName(self):
        return dt_types.get(self.d_tag, "Unknown: %s"%hex(self.d_tag))

class Elf32Dynamic(ElfDynamic, vs_elf.Elf32Dynamic):
    def __init__(self, bigend=False):
        vs_elf.Elf32Dynamic.__init__(self, bigend=bigend)
        ElfDynamic.__init__(self)

class Elf64Dynamic(ElfDynamic, vs_elf.Elf64Dynamic):
    def __init__(self, bigend=False):
        vs_elf.Elf64Dynamic.__init__(self, bigend=bigend)
        ElfDynamic.__init__(self)

class ElfSymbol:
    def __init__(self):
        self.name = ""

    def getInfoType(self):
        return self.st_info & 0xf

    def getInfoBind(self):
        return self.st_info >> 4

    def __cmp__(self, other):
        if self.st_value > other.st_value:
            return 1
        return -1

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def __repr__(self):
        return "0x%.8x %d %s" % (self.st_value, self.st_size, self.name)

class Elf32Symbol(ElfSymbol, vs_elf.Elf32Symbol):
    def __init__(self, bigend=False):
        vs_elf.Elf32Symbol.__init__(self, bigend=bigend)
        ElfSymbol.__init__(self)

class Elf64Symbol(ElfSymbol, vs_elf.Elf64Symbol):
    def __init__(self, bigend=False):
        vs_elf.Elf64Symbol.__init__(self, bigend=bigend)
        ElfSymbol.__init__(self)

class ElfPheader:
    def __init__(self):
        pass

    def getTypeName(self):
        return ph_types.get(self.p_type, "Unknown")

    def __repr__(self):
        return '[%35s] VMA: 0x%.8x  offset: %8d  memsize: %8d  align: %8d  (filesz: %8d)  flags: %x' % (
            self.getTypeName(),
            self.p_vaddr,
            self.p_offset,
            self.p_memsz,
            self.p_align,
            self.p_filesz,
            self.p_flags)

class Elf32Pheader(ElfPheader, vs_elf.Elf32Pheader):
    def __init__(self, bigend=False):
        vs_elf.Elf32Pheader.__init__(self, bigend=bigend)
        ElfPheader.__init__(self)

class Elf64Pheader(ElfPheader, vs_elf.Elf64Pheader):
    def __init__(self, bigend=False):
        vs_elf.Elf64Pheader.__init__(self, bigend=bigend)
        ElfPheader.__init__(self)

class ElfSection:
    def __init__(self):
        self.name = ''

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def __repr__(self):
        flags = [name for idx, name in sh_flags.items() if idx & self.sh_flags]

        return 'Elf Sec: [%20s] @0x%.8x (%8d) [ent/size: %8d/%8d] [align: %8d] [%s]' % (
                self.name,
                self.sh_addr,
                self.sh_offset,
                self.sh_entsize,
                self.sh_size,
                self.sh_addralign,
                'Flags: ' + ', '.join(flags))

class Elf32Section(ElfSection, vs_elf.Elf32Section):
    def __init__(self, bigend=False):
        vs_elf.Elf32Section.__init__(self, bigend=bigend)
        ElfSection.__init__(self)

class Elf64Section(ElfSection, vs_elf.Elf64Section):
    def __init__(self, bigend=False):
        vs_elf.Elf64Section.__init__(self, bigend=bigend)
        ElfSection.__init__(self)

class Elf(vs_elf.Elf32, vs_elf.Elf64):
    def __init__(self, fd, inmem=False):
        '''
        Parse data from 'fd' and create an Elf object.

        This process attempts to get as much information from DYNAMICS as
        possible, then adds in data from SECTIONS.
        '''

        # Grab a 32bit header to use to check for other
        # machine types...
        e = vs_elf.Elf32()
        fd.seek(0)
        bytes = fd.read(len(e))
        e.vsParse(bytes)

        # if e_data == 1, then 32 bit, if e_data == 2, 64bit
        bigend = (e.e_data == ELFDATA2MSB)

        #Parse 32bit header
        if e.e_class == ELFCLASS32:
            vs_elf.Elf32.__init__(self, bigend=bigend)
            self.bits = 32
            self.psize = 4

            self._cls_reloc  = Elf32Reloc
            self._cls_reloca = Elf32Reloca
            self._cls_symbol = Elf32Symbol
            self._cls_section = Elf32Section
        #Parse 64bit header
        elif e.e_class == ELFCLASS64:
            vs_elf.Elf64.__init__(self, bigend=bigend)
            self.bits = 64
            self.psize = 8

            self._cls_reloc  = Elf64Reloc
            self._cls_reloca = Elf64Reloca
            self._cls_symbol = Elf64Symbol
            self._cls_section = Elf64Section
        else:
            raise Exception('Unrecognized e_class: %d' % e.e_class)

        self.fd = fd
        self.inmem = inmem
        self.bigend = bigend

        bytes = self.readAtOffset(0, len(self))
        self.vsParse(bytes)

        if self.e_machine == EM_386:
            self.r_types = r_types_386
        elif self.e_machine == EM_X86_64:
            self.r_types = r_types_amd64
        else:
            self.r_types = {}

        self.pheaders = []
        self.sections = []
        self.secnames = {}
        self.symbols  = []
        self.relocs   = []
        self.relocvas = []
        self.symbols_by_name = {}
        self.symbols_by_addr = {}
        self.dynamics = []      # deprecated - 2019-10-21
        self.dynamic_symbols = []
        self.dynstrtabmeta = (None, None)
        self.dynstrtab = []
        self.dynsymtabct = None     # populated by _parseDynStrs()
        logger.info('self._parsePheaders')
        self._parsePheaders()
        logger.info('self._parseDynLinkInfo')
        self._parseDynLinkInfo()

        logger.info('self._parseSections')
        self._parseSections()
        logger.info('self._parseDynamicsFromSections')
        self._parseDynamicsFromSections()

        # load symbols and relocs from DYNAMICS
        logger.info('self._parseDynStrs')
        self._parseDynStrs()
        logger.info('self._parseDynSyms')
        self._parseDynSyms()
        logger.info('self._parseDynRelocs')
        self._parseDynRelocs()

        # load symbols and relocs from SECTIONS
        logger.info('self._parseDynSymsFromSections')
        self._parseDynSymsFromSections()
        logger.info('self._parseSectionSymbols')
        self._parseSectionSymbols()
        logger.info('self._parseSectionRelocs')
        self._parseSectionRelocs()
        logger.info('done parsing ELF')

    def __del__(self):
        try:
            self.fd.close()
        except:
            pass  # whatever. we're tearing down anyway

    def getFileBytes(self):
        '''
        Return the bytes of the file as they currently exist from the view of the file descriptor-like object

        But keeping in mind not to smash over the old location of the fd
        '''
        self.fd.flush()
        old = self.fd.tell()
        self.fd.seek(0)
        byts = self.fd.read()
        self.fd.seek(old)
        return byts

    def getRelocTypeName(self, rtype):
        '''
        Because relocation type names are decided based on the
        arch, only the Elf knows for sure...
        '''
        return self.r_types.get(rtype)

    def _parsePheaders(self):
        # Load up any program headers we find
        if self.e_phoff:
            pbase = self.e_phoff
            plen = self.e_phentsize
            for i in range(self.e_phnum):
                if self.bits == 32:
                    pgm = Elf32Pheader(bigend=self.bigend)
                elif self.bits == 64:
                    pgm = Elf64Pheader(bigend=self.bigend)
                else:
                    raise Exception('Platform not supported: %d' % (self.bits))

                bytes = self.readAtOffset(pbase, plen)
                pgm.vsParse(bytes)

                self.pheaders.append(pgm)
                pbase += plen

    def _parseSections(self):
        # Load up all the section headers
        if self.e_shoff:
            # Load up the sections
            sbase = self.e_shoff
            sec = self._cls_section(bigend=self.bigend)
            slen = self.e_shentsize
            if len(sec) != slen:
                raise Exception('Invalid Section Header Size: %d' % slen)

            secbytes = self.readAtOffset(sbase, self.e_shnum * slen)

            secs = sec * self.e_shnum
            vstruct.VArray(elems=secs).vsParse(secbytes, fast=True)

            self.sections.extend(secs)

            # Populate the section names
            strsec = self.sections[self.e_shstrndx]
            names = self.readAtOffset(strsec.sh_offset, strsec.sh_size)
            for sec in self.sections:
                name = names[sec.sh_name:].split(b"\x00")[0]
                if len(name) > 0:
                    name = name.decode('utf-8')
                    sec.setName(name)
                    self.secnames[name] = sec

    def getDynPHdr(self):
        '''
        Returns the "Dynamics" ProgramHeader
        '''
        phdr = None
        for phdr in self.getPheaders():
            if phdr.p_type == PT_DYNAMIC:
                return phdr
        return None

    def getDynBytes(self):
        '''
        Finds and returns the bytes from a Program Header of type PT_DYNAMIC
        '''
        phdr = self.getDynPHdr()
        if phdr is None:
            return None

        dynbytes = self.readAtOffset(phdr.p_offset, phdr.p_filesz)
        return dynbytes

    def _parseDynSymsFromSections(self):
        '''
        if by some strange chance, the DYNAMCS PHDR doesn't exist but we have this section...
        '''
        symtab = self.getSectionBytes('.dynsym')
        if symtab is None:
            return

        ssymtabva = self.getSection('.dynsym').sh_addr
        dsymtabva = self.dyns.get(DT_SYMTAB)
        if ssymtabva != dsymtabva:
            logger.info("Section headers and Dynamics disagree on Symbol Table: sec: 0x%x, dyn: 0x%x", ssymtabva, dsymtabva)

        # only parse the symbols that are not already accounted for.
        # symbols are ordered, so existence of index Y is always the same
        sym = self._cls_symbol(bigend=self.bigend)
        count = len(symtab) / len(sym)
        diff = count - len(self.dynamic_symbols)
        if diff == 0:
            return

        offset = len(self.dynamic_symbols) * len(sym)

        syms = sym * diff
        vstruct.VArray(elems=syms).vsParse(symtab[offset:], fast=True)

        logger.warning("_parseDynSymsFromSections:  current_count: %d\tdiff: %d\toffset: %d\t", count, diff, offset)
        for sym in syms:
            if not sym.st_name:
                continue
            name = self.getStrtabString(sym.st_name, ".dynstr")
            sym.setName(name)

            if sym in self.dynamic_symbols:
                continue
            self.dynamic_symbols.append(sym)

    def _parseDynamicsFromSections(self):
        '''
        if by some strange chance, the DYNAMCS PHDR doesn't exist but we have this section...
        '''
        dynbytes = self.getSectionBytes('.dynamic')
        while dynbytes:
            if self.bits == 32:
                dyn = Elf32Dynamic(bigend=self.bigend)
            elif self.bits == 64:
                dyn = Elf64Dynamic(bigend=self.bigend)
            else:
                raise Exception('Platform not supported: %d' % (self.bits))
            dyn.vsParse(dynbytes)

            if dyn.d_tag in Elf32Dynamic.has_string:
                name = self.getStrtabString(dyn.d_value, ".dynstr")
                dyn.setName(name)

            # don't add a second entry
            if dyn not in self.dynamics:
                logger.debug("dynamic: %r: 0x%x", dt_names.get(dyn.d_tag), dyn.d_value)
                self.dynamics.append(dyn)

            if dyn.d_tag == DT_NULL:  # Represents the end
                break
            dynbytes = dynbytes[len(dyn):]

    def _parseDynLinkInfo(self):
        '''
        Parse the Dynamics segment and populate both self.dynamics (legacy) and self.dyns
        This must be run before most Dynamic-data accessors like getDynStrtabString(),
        getDynSymTabInfo(), etc..
        '''
        self.dyns = {}
        dynbytes = self.getDynBytes()
        if dynbytes is None:
            return

        while dynbytes:
            if self.bits == 32:
                dyn = Elf32Dynamic(bigend=self.bigend)
            elif self.bits == 64:
                dyn = Elf64Dynamic(bigend=self.bigend)
            else:
                raise Exception('Platform not supported: %d' % (self.bits))

            dyn.vsParse(dynbytes)

            # dump the tag/value pairs into the "dyns" dictionary.  if multiples, create a tuple
            curdyn = self.dyns.get(dyn.d_tag)
            if curdyn is not None:
                self.dyns[dyn.d_tag] = (curdyn, dyn.d_value)
            else:
                self.dyns[dyn.d_tag] = dyn.d_value
            logger.debug('dynamic: %r: 0x%x', dt_names.get(dyn.d_tag), dyn.d_value)

            # DEPRECATED: storing info in both dyns{} and dynamics[].  
            # 2019-10-21:  dynamics will go away sometime in the future
            self.dynamics.append(dyn)
            if dyn.d_tag == DT_NULL: # Represents the end
                break
            dynbytes = dynbytes[len(dyn):]

    def _parseDynStrs(self):
        # setup STRTAB for string recovery:
        dynstrtab = self.dyns.get(DT_STRTAB)
        strsz = self.dyns.get(DT_STRSZ)
        if dynstrtab is None or strsz is None:
            logger.info('no dynamic string tableinfo found: DT_STRTAB: %r  DT_STRSZ: %r', dynstrtab, strsz)
            return

        if self.dynstrtabmeta != (None, None):
            curtab = self.dynstrtabmeta[0]
            logger.warning('wtf?  multiple dynamic string tables?  old: 0x%x  new: 0x%x', curtab, rva)

        strtabbytes = self.readAtRva(dynstrtab, strsz)

        self.dynstrtabmeta = (dynstrtab, strsz)
        self.dynstrtab = strtabbytes.split(b'\0')

        # since our string table should certainly end in '\0', we'll have an empty string
        # at the end.  since this array is used to determine the number of symbols, we
        # need to clean it up.
        if len(self.dynstrtab) and not len(self.dynstrtab[-1]):
            self.dynstrtab.pop()

        self.dynsymtabct = len(self.dynstrtab)  # cheat: there is a 1-to-1 relationship between symbols and strings in these tables
        # if "DT_SONAME" is within this string table, there are no symbols to match that or thereafter:
        soname = self.dyns.get(DT_SONAME)
        if soname is not None and soname != -1 and soname < strsz:
            dynsymstrs = strtabbytes[:soname].split(b'\0')
            self.dynsymtabct = len(dynsymstrs) - 1

        # setup names for the dynamics table entries
        for dyn in self.dynamics:
            if dyn.d_tag in Elf32Dynamic.has_string:
                name = self.getDynStrtabString(dyn.d_value)
                dyn.setName(name)

    def _parseDynSyms(self):
        '''
        Parses the Symbol Table and sets up Dynamic String Table
        Using Dynamics instead of ELF Sections

        This relies on the DYNAMICS section having DT_SYMTAB and DT_SYMENT

        Because ELF has no DT_SYMTABSZ, "symtabsz" as returned from
        getDynSymTabInfo() cannot be fully trusted.  Therefore, we run a few
        sanity heuristics.

        This is only a prep run to identify symbols.  If getDynSymbol() is
        called with an index not currently in dynamic_symbols, dynamic_symbols
        is expanded to fill the need (albeit, without these sanity checks, so
        be cautious).
        '''
        # fyi:  '.dynsym' section == DT_SYMTAB
        #       '.dynstr' section == DT_STRTAB

        # parse Dynamic Symbol Table
        if len(self.dynamic_symbols):
            logger.warning('_parseDynSyms() cannot run: dynamic_symbols is not empty')
            return

        symtabrva, symsz, symtabsz = self.getDynSymTabInfo()
        if symtabrva is None:
            return

        dsoff = 0
        while True:
            syment = self.readAtRva(symtabrva + dsoff, symsz)
            sym = self._cls_symbol(bigend=self.bigend)
            sym.vsParse(syment)
            if sym.st_info & 0xf not in st_info_type:
                break

            if sym.st_info >> 4 not in st_info_bind:
                break

            name = self.getDynStrtabString(sym.st_name)
            if name is None:
                break

            sym.setName(name)
            self.dynamic_symbols.append(sym)

            dsoff += symsz

    # FIXME: wrap in VERDEF and SYMINFO into the analysis.
    def _parseSectionSymbols(self):
        """
        Parse out the symbols that this elf binary has for us.
        """
        for sec in self.sections:
            if sec.sh_type == SHT_SYMTAB:
                sym = self._cls_symbol(bigend=self.bigend)
                symtab = self.readAtOffset(sec.sh_offset, sec.sh_size)

                count, remain = divmod(sec.sh_size, len(sym))
                syms = sym * count

                vstruct.VArray(elems=syms).vsParse(symtab, fast=True)

                for sym in syms:
                    if sym.st_name:
                        name = self.getStrtabString(sym.st_name, ".strtab")
                        sym.setName(name)
                    # logger.info('SHT_SYMTAB: %r', sym)

                    self.addSymbol(sym)

    def _parseDynRelocs(self):
        """
        Parse all the relocation entries out of Dyn table entries based at
        * REL
        * RELA
        * JMPREL
        """
        rel, relent, relsz = self.getDynRelInfo()
        if rel is not None:
            cls = self._cls_reloc
            self._doDynRelocs(rel, relsz, cls)

        rela, relaent, relasz = self.getDynRelaInfo()
        if rela is not None:
            cls = self._cls_reloca
            self._doDynRelocs(rela, relasz, cls)

        jmprel, pltrel, pltrelsz = self.getDynPltRelInfo()
        if jmprel is not None:
            cls = (self._cls_reloc, self._cls_reloca)[pltrel==DT_RELA]
            self._doDynRelocs(jmprel, pltrelsz, cls)

    def _doDynRelocs(self, rva, relsz, cls=None):
        syms = self.getDynSyms()

        if cls is None:
            cls = self._cls_reloc

        reloc = cls(bigend=self.bigend)
        relbytes = self.readAtRva(rva, relsz)
        count, remain = divmod(relsz, len(reloc))

        relocs = reloc * count
        vstruct.VArray(elems=relocs).vsParse(relbytes,fast=True)

        for reloc in relocs:
            index = reloc.getSymTabIndex()
            sym = self.getDynSymbol(index)
            if sym is not None:
                reloc.setName( sym.getName() )
            self.relocs.append(reloc)
            self.relocvas.append(reloc.r_offset)

    def _parseSectionRelocs(self):
        """
        Parse all the relocation entries out of any sections with
        sh_type == SHT_REL or SHT_RELA

        Ignores repeat relocs (ie. those already parsed from DYNAMICS)
        """
        # could it ever be interesting?  perhaps if dynamic relocs fail?
        rel, relent, relsz = self.getDynRelInfo()
        rela, relaent, relasz = self.getDynRelaInfo()
        jmprel, pltrel, pltrelsz = self.getDynPltRelInfo()
        dynrels = (rel, rela, jmprel)

        for sec in self.sections:
            if sec.sh_type not in (SHT_REL, SHT_RELA):
                continue

            if sec.sh_offset not in dynrels:
                logger.warning('_parseSectionRelocs: Reloc section differs from Dynamics: 0x%x', sec.sh_offset)

            reloccls = self._cls_reloc
            if sec.sh_type == SHT_RELA:
                reloccls = self._cls_reloca

            secbytes = self.readAtOffset(sec.sh_offset, sec.sh_size)
            reloc = reloccls(bigend=self.bigend)
            count, remain = divmod(len(secbytes), len(reloc))

            relocs = reloc * count
            vstruct.VArray(elems=relocs).vsParse(secbytes, fast=True)

            for reloc in relocs:
                index = reloc.getSymTabIndex()
                if index < len(self.dynamic_symbols):
                    sym = self.dynamic_symbols[index]
                    reloc.setName( sym.getName() )

                if reloc.r_offset in self.relocvas:
                    # FIXME: This line is hit sever tens of thousands of times during parsing
                    logger.debug('duplicate relocation (section): %s', reloc)
                    continue

                logger.info('section reloc: %s', reloc)
                self.relocs.append(reloc)
                self.relocvas.append(reloc.r_offset)

    def getBaseAddress(self):
        """
        For prelinked and main-exe elf binaries, return the
        value for the loaded base address...
        """
        shrd = self.isSharedObject()
        plnk = self.isPreLinked()

        # If it's a shared object and *not* prelinked,
        # we need to select a base address for it
        # FIXME find non-coliding addr in workspace
        if shrd and not plnk:
            return 0x02000000

        # Find the best base address from the list of
        # section addresses...
        base = None
        for pgm in self.getPheaders():

            if pgm.p_vaddr == 0:
                continue

            if base is None:
                base = pgm.p_vaddr
                continue

            if pgm.p_vaddr < base:
                base = pgm.p_vaddr

        if base is None:
            base = 0x20000000

        base &= 0xfffff000
        return base

    def readAtRva(self, rva, size):
        '''
        Calculate the file offset for the given RVA and
        read from it...
        '''
        return self.readAtOffset(self.rvaToOffset(rva), size)

    def rvaToOffset(self, rva):
        '''
        Convert an RVA for this ELF binary to a file offset.
        '''
        baseaddr = 0
        #if self.isPreLinked() or not self.isSharedObject():
        #if not self.isSharedObject():
            #logger.info('SUBTRACTING CALCULATED BASE')
            #baseaddr = self.getBaseAddress()

        for pgm in self.pheaders:
            if pgm.p_type != PT_LOAD:
                continue
            phrva = pgm.p_vaddr - baseaddr
            if rva < phrva:
                continue
            if rva >= phrva+pgm.p_memsz:
                continue
            # We are inside this pgrm header!
            rvaoff = rva - phrva
            return pgm.p_offset + rvaoff

        raise Exception(f"Couldn't convert rva: {rva} to a file offset")

    def readAtOffset(self, off, size):
        '''
        Read from the given file offset.
        '''
        self.fd.seek(off)
        return self.fd.read(size)

    def getEndian(self):
        '''
        Is architecture BigEndian?
        Returns True for MSB, False for LSB

        This works with Vivisect's definitions of ENDIAN_MSB/ENDIAN_LSB constants:
            (defined in envi/const.py)
            ENDIAN_LSB = 0
            ENDIAN_MSB = 1

        '''
        return self.e_data == ELFDATA2MSB

    def getDynRelInfo(self):
        '''
        Returns startva, size, and Entity size for any REL records
        '''
        rel = self.dyns.get(DT_REL)
        relent = self.dyns.get(DT_RELENT)
        relsz = self.dyns.get(DT_RELSZ)
        return rel, relent, relsz

    def getDynRelaInfo(self):
        '''
        Returns startva, size, and Entity size for any RELA records
        '''
        rela = self.dyns.get(DT_RELA)
        relaent = self.dyns.get(DT_RELAENT)
        relasz = self.dyns.get(DT_RELASZ)
        return rela, relaent, relasz

    def getDynPltRelInfo(self):
        '''
        Returns startva, size, and Entity size for any RELA records
        '''
        jmprel = self.dyns.get(DT_JMPREL)
        pltrel = self.dyns.get(DT_PLTREL)
        pltrelsz = self.dyns.get(DT_PLTRELSZ)
        return jmprel, pltrel, pltrelsz

    def getSection(self, secname):
        return self.secnames.get(secname, None)

    def getSections(self):
        """
        Return the array of sections for this Elf
        """
        return list(self.sections)

    def getSectionBytes(self, secname):
        sec = self.getSection(secname)
        if sec is None:
            return None
        return self.readAtOffset(sec.sh_offset, sec.sh_size)

    def getStrtabString(self, offset, section=".strtab"):
        sec = self.getSection(section)
        bytes = self.readAtOffset(sec.sh_offset, sec.sh_size)
        index = bytes.find(b"\x00", offset)
        return bytes[offset:index].decode('utf-8')

    def getNotes(self):
        '''
        Retrieve a list of the ElfNote vstructs from any
        sections of type SHT_NOTE.

        Example:
            for note in e.getNotes():
                print('%s : %d' % (e.name, e.ntype))
        '''
        for sec in self.getSections():
            if sec.sh_type != SHT_NOTE:
                continue

            try:
                notebytes = self.readAtOffset(sec.sh_offset, sec.sh_size)
                offset = 0
                notebyteslen = len(notebytes)
                while offset < notebyteslen:
                    note = vs_elf.ElfNote()
                    if notebyteslen - offset < len(note):
                        logger.warning("""\nNOTES section length mismatch!\n\t%s
                                       \tSection Bytes: %s\n\tStranded bytes: %s\n""",
                                sec, repr(notebytes), repr(notebytes[offset:]))
                        break

                    offset = note.vsParse(notebytes, offset=offset)
                    yield note
            except Exception as e:
                logger.warning('Elf.getNotes() Exception: %s', e)

    def getPlatform(self):
        '''
        Return a "best effort" platform guess (envi platform name).
        ( and platform specific details if any )

        Example:
            plat = e.getPlatform()
        '''
        for note in self.getNotes():
            if note.name == b'GNU\x00' and note.ntype == 1:
                desc0 = int(note.desc[0])
                return osnotes.get(desc0, 'unknown')

        if self.getSection('QNX_info'):
            return 'qnx'

        return 'unknown'

    def getDynamics(self):
        '''
        Return a list of the dynamics.
        '''
        return list(self.dynamics)

    def getDynSyms(self):
        '''
        Return a list of dynamic symbol objects.
        '''
        return self.dynamic_symbols

    def getRelocs(self):
        '''
        Get the list of relocations.
        '''
        return list(self.relocs)

    def isPreLinked(self):
        '''
        Returns True if the Elf binary is prelinked.
        '''
        for dyn in self.dynamics:
            if dyn.d_tag == DT_GNU_PRELINKED:
                return True
            if dyn.d_tag == DT_GNU_CONFLICTSZ:
                return True
        return False

    def isSharedObject(self):
        '''
        Returns true if the given Elf binary is a dynamically shared
        object.
        '''
        if self.e_type == ET_DYN:
            return True
        return False

    def isExecutable(self):
        '''
        Returns true if the given Elf binary is an executable file type.
        '''
        return self.e_type == ET_EXEC

    def __repr__(self, verbose=False):
        """
        Returns a string summary of this ELF.
        If (verbose) the summary will include Symbols, Relocs, Dynamics and Dynamic Symbol tables
        """
        mystr = 'Elf Binary:'
        mystr+= "\n= Intimate Details:"
        mystr+= "\n==Magic:\t\t\t\t%r"       % self.e_ident.decode('utf-8')
        mystr+= "\n==Type:\t\t\t\t\t"        + e_types.get(self.e_type)
        mystr+= "\n==Machine Arch:\t\t\t\t"  + e_machine_types.get(self.e_machine)
        mystr+= "\n==Version:\t\t\t\t%d"     % (self.e_version)
        mystr+= "\n==Entry:\t\t\t\t0x%.8x"      % (self.e_entry)
        mystr+= "\n==Program Headers(offset):\t\t%d (0x%x) bytes" % (self.e_phoff, self.e_phoff)
        mystr+= "\n==Section Headers(offset):\t\t%d (0x%x) bytes" % (self.e_shoff, self.e_shoff)
        mystr+= "\n==Flags:\t\t\t\t" + repr(self.e_flags) + " "
        mystr+= "\n==Elf Header Size:\t\t\t" + repr(self.e_ehsize) + " (" + hex(self.e_ehsize) + " bytes)"
        mystr+= "\n==Program Header Size:\t\t\t" + repr(self.e_phentsize) + " (" + hex(self.e_phentsize) + " bytes)"
        mystr+= "\n==Program Header Count:\t\t\t" + repr(self.e_phnum) + " (" + hex(self.e_phnum)+ ")"
        mystr+= "\n==Section Header Size:\t\t\t" + repr(self.e_shentsize) + " (" + hex(self.e_shentsize) + " bytes)"
        mystr+= "\n==Section Header Count:\t\t\t" + repr(self.e_shnum) + " (" + hex(self.e_shnum) + ")"
        mystr+= "\n==Section Header String Index\t\t" + repr(self.e_shstrndx) + " (" + hex(self.e_shstrndx) + " bytes)"

        mystr+= "\n\n= Sections:"
        for sec in self.sections:
            mystr+= "\n" + repr(sec)

        mystr+= "\n\n= Program Headers:"
        for ph in self.pheaders:
            mystr+= "\n" + repr(ph)

        return mystr

    def verbrepr(self):
        mystr = repr(self)

        mystr+= "\n\n= Symbols table:"
        for sym in self.symbols:
            mystr+= "\n"+repr(sym)

        mystr+= "\n\n= Relocation table:"
        for reloc in self.relocs:
            mystr+= "\n"+repr(reloc)

        mystr+= "\n\n= Dynamics table:"
        for dyn in self.dynamics:
            mystr+= "\n"+repr(dyn)

        mystr+= "\n\n= Dynamic Symbols table:"
        for dyn in self.dynamic_symbols:
            mystr+= "\n"+repr(dyn)

        return mystr

    def lookupSymbolName(self, name):
        """
        Lookup symbol entries in this elf binary by name.  The result is
        a long representing the address for the given symbol. Or None if
        it's not found.
        """
        return self.symbols_by_name.get(name, None)

    def lookupSymbolAddr(self, address):
        """
        lookup symbols from this elf binary by address.
        This returns the name for the given symbol or None for not found
        """
        return self.symbols_by_addr.get(address, None)

    def getPheaders(self):
        """
        Return a list of the program headers for this elf
        """
        return list(self.pheaders)

    def addSymbol(self, symbol):
        '''
        Add a symbol to the Symbols table, along with caching symbols_by_name and symbols_by_addr
        These symbols are from ELF Sections of type SHT_SYMTAB
        '''
        self.symbols.append(symbol)
        self.symbols_by_name[symbol.getName()] = symbol
        self.symbols_by_addr[symbol.st_value] = symbol

    def getSymbols(self):
        '''
        Returns discovered Symbols (from ELF Sections)
        '''
        return self.symbols

    def getDynSymbol(self, symidx):
        '''
        Returns the DT_SYMTAB entry at index "symidx".

        Checks self.dynamic_symbols first.
        If the index hasn't been loaded into self.dynamic_symbols, it is.
        '''
        symlen = len(self.dynamic_symbols)
        if symidx >= symlen:
            # dynamic_symbols is too small, grow
            logger.info('getDynSymbol(%d): expanding dynamic_symbols from %d', symidx, symlen)
            newspace = [self._getDynSymbol(x) for x in range(symlen, symidx + 1)]
            self.dynamic_symbols.extend(newspace)

        sym = self.dynamic_symbols[symidx]
        return sym

    def _getDynSymbol(self, symidx):
        '''
        Parse the Dynamics entries for SYMTAB and STRTAB, and return the
        symidx indexed symbol.
        '''
        symtabrva, symsz, symtabsz = self.getDynSymTabInfo()

        symrva = symtabrva + (symidx * symsz)
        # DON'T trust symtabsz.  it's often smaller than the '.dynsym' section
        # but, if we attempt to parse outside the binary, we'll throw an error.
        sym = self._cls_symbol(bigend=self.bigend)
        sym.vsParse(self.readAtRva(symrva, symsz))

        name = self.getDynStrtabString(sym.st_name)
        sym.setName(name)
        return sym

    def getDynStrTabInfo(self):
        return self.dynstrtabmeta

    def getDynSymTabInfo(self):
        '''
        Returns Symbol Table information (as obtained through Dynamics only)
        Assumes _parseDynSyms has run (populating self.dynstrtab)
        returns (symtabva, symbolsz, symtabsz)

        Because there is no DT_SYMTABSZ, we can't be certain how many dynamic
        symbols to expect.  Supposedly there is a 1:1 relationship between
        DynSyms and DynStrs, but that can be misleading.  Still, based on the
        number of DynStrs parsed in _parseDynStrs() we use that to roughly
        determine the number, which is estimated in _parseDynStrs()  and stored
        in self.dynsymtabct.  Perhaps this is horrible and should be stricken
        from the code.
        '''
        #FIXME: make this use both SECTION and PT_DYNAMICS versions...
        symtabva = self.dyns.get(DT_SYMTAB)
        if symtabva is None:
            return None, None, None

        symsz = self.dyns.get(DT_SYMENT)
        count = self.dynsymtabct
        symtabsz = count * symsz

        return symtabva, symsz, symtabsz

    def getDynStrtabString(self, stroff):
        '''
        Returns a string starting at stroff
        '''
        if self.dynstrtabmeta == (None, None):
            logger.info("no dyn strtabs!")
            return ''

        dynstrtabva, strsz = self.dynstrtabmeta
        strings = self.readAtRva(dynstrtabva, strsz)
        strend = strings.find(b'\0', stroff)
        if stroff > len(strings):
            return None

        return strings[stroff:strend].decode('utf-8')


def elfFromFileName(fname):
    return Elf(open(fname, 'rb'))


def elfFromBytes(fbytes):
    fd = io.BytesIO(fbytes)
    return Elf(fd)


def elfFromMemoryObject(memobj, baseaddr):
    fd = vstruct.MemObjFile(memobj, baseaddr)
    return Elf(fd)


def getRelocType(val):
    return val & 0xff


def getRelocSymTabIndex(val):
    return val >> 8
