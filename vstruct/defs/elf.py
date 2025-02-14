import vstruct
from vstruct.primitives import *
from vstruct.defs.constants.elf import *

DT_NULL     = 0
DT_NEEDED   = 1
DT_PLTRELSZ = 2
DT_PLTGOT   = 3
DT_HASH     = 4
DT_STRTAB   = 5
DT_SYMTAB   = 6
DT_RELA     = 7
DT_RELASZ   = 8
DT_RELAENT  = 9
DT_STRSZ    = 10
DT_SYMENT   = 11
DT_INIT     = 12
DT_FINI     = 13
DT_SONAME   = 14
DT_RPATH    = 15
DT_SYMBOLIC = 16
DT_REL      = 17
DT_RELSZ    = 18
DT_RELENT   = 19
DT_PLTREL   = 20
DT_DEBUG    = 21
DT_TEXTREL  = 22
DT_JMPREL   = 23
DT_BIND_NOW = 24
DT_INIT_ARRAY   = 25
DT_FINI_ARRAY   = 26
DT_INIT_ARRAYSZ = 27
DT_FINI_ARRAYSZ = 28
DT_RUNPATH  = 29
DT_FLAGS    = 30
DT_ENCODING = 32
DT_PREINIT_ARRAY = 32
DT_PREINIT_ARRAYSZ = 33
DT_NUM      = 34
DT_GNU_PRELINKED    = 0x6ffffdf5
DT_GNU_CONFLICTSZ   = 0x6ffffdf6
DT_GNU_LIBLISTSZ    = 0x6ffffdf7
DT_CHECKSUM         = 0x6ffffdf8
DT_PLTPADSZ         = 0x6ffffdf9
DT_MOVEENT          = 0x6ffffdfa
DT_MOVESZ           = 0x6ffffdfb
DT_FEATURE_1        = 0x6ffffdfc
DT_POSFLAG_1        = 0x6ffffdfd
DT_SYMINSZ          = 0x6ffffdfe
DT_SYMINENT         = 0x6ffffdff
DT_GNU_HASH         = 0x6ffffef5
DT_TLSDESC_PLT      = 0x6ffffef6
DT_TLSDESC_GOT      = 0x6ffffef7
DT_GNU_CONFLICT     = 0x6ffffef8
DT_GNU_LIBLIST      = 0x6ffffef9
DT_CONFIG           = 0x6ffffefa
DT_DEPAUDIT         = 0x6ffffefb
DT_AUDIT            = 0x6ffffefc
DT_PLTPAD           = 0x6ffffefd
DT_MOVETAB          = 0x6ffffefe
DT_SYMINFO          = 0x6ffffeff
DT_VERSYM           = 0x6ffffff0
DT_RELACOUNT        = 0x6ffffff9
DT_RELCOUNT         = 0x6ffffffa
DT_FLAGS_1          = 0x6ffffffb
DT_VERDEF           = 0x6ffffffc
DT_VERDEFNUM        = 0x6ffffffd
DT_VERNEED          = 0x6ffffffe
DT_VERNEEDNUM       = 0x6fffffff
DT_AUXILIARY        = 0x7ffffffd
DT_FILTER           = 0x7fffffff
DT_LOOS             = 0x6000000d
DT_HIOS             = 0x6ffff000
DT_LOPROC           = 0x70000000
DT_HIPROC           = 0x7fffffff
#DT_PROCNUM  = DT_MIPS_NUM

dt_names = { v:k for k,v in globals().items() if k.startswith('DT_')}

dt_types = {
    DT_NULL     : "Marks end of dynamic section ",
    DT_NEEDED   : "Name of needed library ",
    DT_PLTRELSZ : "Size in bytes of PLT relocs ",
    DT_PLTGOT   : "Processor defined value ",
    DT_HASH     : "Address of symbol hash table ",
    DT_STRTAB   : "Address of string table ",
    DT_SYMTAB   : "Address of symbol table ",
    DT_RELA     : "Address of Rela relocs ",
    DT_RELASZ   : "Total size of Rela relocs ",
    DT_RELAENT  : "Size of one Rela reloc ",
    DT_STRSZ    : "Size of string table ",
    DT_SYMENT   : "Size of one symbol table entry ",
    DT_INIT     : "Address of init function ",
    DT_FINI     : "Address of termination function ",
    DT_SONAME   : "Name of shared object ",
    DT_RPATH    : "Library search path (deprecated) ",
    DT_SYMBOLIC : "Start symbol search here ",
    DT_REL      : "Address of Rel relocs ",
    DT_RELSZ    : "Total size of Rel relocs ",
    DT_RELENT   : "Size of one Rel reloc ",
    DT_PLTREL   : "Type of reloc in PLT ",
    DT_DEBUG    : "For debugging; unspecified ",
    DT_TEXTREL  : "Reloc might modify .text ",
    DT_JMPREL   : "Address of PLT relocs ",
    DT_BIND_NOW : "Process relocations of object ",
    DT_INIT_ARRAY   : "Array with addresses of init fct ",
    DT_FINI_ARRAY   : "Array with addresses of fini fct ",
    DT_INIT_ARRAYSZ : "Size in bytes of DT_INIT_ARRAY ",
    DT_FINI_ARRAYSZ : "Size in bytes of DT_FINI_ARRAY ",
    DT_RUNPATH  : "Library search path ",
    DT_FLAGS    : "Flags for the object being loaded ",
    DT_FLAGS_1  : "Flags (auxiliary) for the object being loaded ",
    DT_ENCODING : "Start of encoded range ",
    DT_PREINIT_ARRAY : "Array with addresses of preinit fct",
    DT_PREINIT_ARRAYSZ : "size in bytes of DT_PREINIT_ARRAY ",
    DT_NUM      : "Number used ",
    DT_LOOS     : "Start of OS-specific ",
    DT_HIOS     : "End of OS-specific ",
    DT_LOPROC   : "Start of processor-specific ",
    DT_HIPROC   : "End of processor-specific ",
    DT_VERDEF   : "Version Definition Offset ",
    DT_VERDEFNUM: "Version Definition Structure Count ",
    DT_VERNEED  : "Required Version Offset ",
    DT_VERNEEDNUM: "Required Version Structure Count ",
    DT_VERSYM   : "Address of Version Section"
    #DT_PROCNUM  : "Most used by any processor ",
}

class Elf32(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.e_ident       = v_bytes(EI_NIDENT)
        self.e_class       = v_uint8()
        self.e_data        = v_uint8()
        self.e_fileversion = v_uint8()
        self.e_osabi       = v_uint8()
        self.e_abiversio   = v_uint8()
        self.e_pad         = v_bytes(EI_PADLEN)
        self.e_type        = v_uint16(bigend=bigend)
        self.e_machine     = v_uint16(bigend=bigend)
        self.e_version     = v_uint32(bigend=bigend)
        self.e_entry       = v_uint32(bigend=bigend)
        self.e_phoff       = v_uint32(bigend=bigend)
        self.e_shoff       = v_uint32(bigend=bigend)
        self.e_flags       = v_uint32(bigend=bigend)
        self.e_ehsize      = v_uint16(bigend=bigend)
        self.e_phentsize   = v_uint16(bigend=bigend)
        self.e_phnum       = v_uint16(bigend=bigend)
        self.e_shentsize   = v_uint16(bigend=bigend)
        self.e_shnum       = v_uint16(bigend=bigend)
        self.e_shstrndx    = v_uint16(bigend=bigend)

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

class Elf32Section(ElfSection, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfSection.__init__(self)
        self.sh_name      = v_uint32(bigend=bigend)
        self.sh_type      = v_uint32(bigend=bigend)
        self.sh_flags     = v_uint32(bigend=bigend)
        self.sh_addr      = v_uint32(bigend=bigend)
        self.sh_offset    = v_uint32(bigend=bigend)
        self.sh_size      = v_uint32(bigend=bigend)
        self.sh_link      = v_uint32(bigend=bigend)
        self.sh_info      = v_uint32(bigend=bigend)
        self.sh_addralign = v_uint32(bigend=bigend)
        self.sh_entsize   = v_uint32(bigend=bigend)

class ElfPheader:
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

class Elf32Pheader(ElfPheader, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.p_type   = v_uint32(bigend=bigend)
        self.p_offset = v_uint32(bigend=bigend)
        self.p_vaddr  = v_uint32(bigend=bigend)
        self.p_paddr  = v_uint32(bigend=bigend)
        self.p_filesz = v_uint32(bigend=bigend)
        self.p_memsz  = v_uint32(bigend=bigend)
        self.p_flags  = v_uint32(bigend=bigend)
        self.p_align  = v_uint32(bigend=bigend)

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

class Elf32Reloc(ElfReloc, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfReloc.__init__(self)
        self.r_offset = v_ptr32(bigend=bigend)
        self.r_info   = v_uint32(bigend=bigend)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.r_offset != other.r_offset:
            return False
        if self.r_info != other.r_info:
            return False
        return True

    def getSymTabIndex(self):
        return self.r_info >> 8

class Elf32Reloca(Elf32Reloc):
    def __init__(self, bigend=False):
        Elf32Reloc.__init__(self)
        self.r_addend = v_int32(bigend=bigend)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.r_offset != other.r_offset:
            return False
        if self.r_info != other.r_info:
            return False
        if self.r_addend != other.r_addend:
            return False
        return True

class ElfSymbol:
    def __init__(self):
        self.name = ""

    def getInfoType(self):
        return self.st_info & 0xf

    def getInfoBind(self):
        return self.st_info >> 4

    def getVisibility(self):
        return self.st_other & 0x3

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

class Elf32Symbol(ElfSymbol, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfSymbol.__init__(self)
        self.st_name  = v_uint32(bigend=bigend)
        self.st_value = v_uint32(bigend=bigend)
        self.st_size  = v_uint32(bigend=bigend)
        self.st_info  = v_uint8()
        self.st_other = v_uint8()
        self.st_shndx = v_uint16(bigend=bigend)

    def __eq__(self, other):
        if self.st_value != other.st_value:
            return False
        if self.st_name != other.st_name:
            return False
        if self.st_size != other.st_size:
            return False
        if self.st_info != other.st_info:
            return False
        if self.st_other != other.st_other:
            return False
        if self.st_shndx != other.st_shndx:
            return False
        return True

class ElfDynamic:
    """
    An object to represent an Elf dynamic entry.
    (linker/loader directives)
    """

    def __init__(self):
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
        return dt_types.get(self.d_tag, "Unknown: %s" % hex(self.d_tag))

class Elf32Dynamic(ElfDynamic, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfDynamic.__init__(self)
        self.d_tag   = v_uint32(bigend=bigend)
        self.d_value = v_uint32(bigend=bigend)

    def __eq__(self, other):
        if self.d_tag != other.d_tag:
            return False
        if self.d_value != other.d_value:
            return False
        return True

class Elf64(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.e_ident       = v_bytes(EI_NIDENT)
        self.e_class       = v_uint8()
        self.e_data        = v_uint8()
        self.e_fileversion = v_uint8()
        self.e_osabi       = v_uint8()
        self.e_abiversio   = v_uint8()
        self.e_pad         = v_bytes(EI_PADLEN)
        self.e_type        = v_uint16(bigend=bigend)
        self.e_machine     = v_uint16(bigend=bigend)
        self.e_version     = v_uint32(bigend=bigend)
        self.e_entry       = v_uint64(bigend=bigend)
        self.e_phoff       = v_uint64(bigend=bigend)
        self.e_shoff       = v_uint64(bigend=bigend)
        self.e_flags       = v_uint32(bigend=bigend)
        self.e_ehsize      = v_uint16(bigend=bigend)
        self.e_phentsize   = v_uint16(bigend=bigend)
        self.e_phnum       = v_uint16(bigend=bigend)
        self.e_shentsize   = v_uint16(bigend=bigend)
        self.e_shnum       = v_uint16(bigend=bigend)
        self.e_shstrndx    = v_uint16(bigend=bigend)

class Elf64Section(ElfSection, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfSection.__init__(self)
        self.sh_name      = v_uint32(bigend=bigend)
        self.sh_type      = v_uint32(bigend=bigend)
        self.sh_flags     = v_uint64(bigend=bigend)
        self.sh_addr      = v_uint64(bigend=bigend)
        self.sh_offset    = v_uint64(bigend=bigend)
        self.sh_size      = v_uint64(bigend=bigend)
        self.sh_link      = v_uint32(bigend=bigend)
        self.sh_info      = v_uint32(bigend=bigend)
        self.sh_addralign = v_uint64(bigend=bigend)
        self.sh_entsize   = v_uint64(bigend=bigend)

class Elf64Pheader(ElfPheader, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.p_type   = v_uint32(bigend=bigend)
        self.p_flags  = v_uint32(bigend=bigend)
        self.p_offset = v_uint64(bigend=bigend)
        self.p_vaddr  = v_uint64(bigend=bigend)
        self.p_paddr  = v_uint64(bigend=bigend)
        self.p_filesz = v_uint64(bigend=bigend)
        self.p_memsz  = v_uint64(bigend=bigend)
        self.p_align  = v_uint64(bigend=bigend)

class Elf64Reloc(ElfReloc, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfReloc.__init__(self)
        self.r_offset = v_ptr64(bigend=bigend)
        self.r_info   = v_uint64(bigend=bigend)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.r_offset != other.r_offset:
            return False
        if self.r_info != other.r_info:
            return False
        return True

    def getSymTabIndex(self):
        return self.r_info >> 32

class Elf64Reloca(Elf64Reloc):
    def __init__(self, bigend=False):
        Elf64Reloc.__init__(self)
        self.r_addend = v_int64(bigend=bigend)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.r_offset != other.r_offset:
            return False
        if self.r_info != other.r_info:
            return False
        if self.r_addend != other.r_addend:
            return False
        return True

class Elf64Symbol(ElfSymbol, vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfSymbol.__init__(self)
        self.st_name  = v_uint32(bigend=bigend)
        self.st_info  = v_uint8()
        self.st_other = v_uint8()
        self.st_shndx = v_uint16(bigend=bigend)
        self.st_value = v_uint64(bigend=bigend)
        self.st_size  = v_uint64(bigend=bigend)

    def __eq__(self, other):
        if self.st_value != other.st_value:
            return False
        if self.st_name != other.st_name:
            return False
        if self.st_size != other.st_size:
            return False
        if self.st_info != other.st_info:
            return False
        if self.st_other != other.st_other:
            return False
        if self.st_shndx != other.st_shndx:
            return False
        return True

class Elf64Dynamic(Elf32Dynamic):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        ElfDynamic.__init__(self)
        self.d_tag   = v_uint64(bigend=bigend)
        self.d_value = v_uint64(bigend=bigend)

class ElfNote(vstruct.VStruct):

    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.namesz = v_uint32(bigend=bigend)
        self.descsz = v_uint32(bigend=bigend)
        self.ntype  = v_uint32(bigend=bigend)
        self.name   = v_bytes()
        self.desc   = vstruct.VArray()

    def pcb_namesz(self):
        # padded to 4 byte alignment
        namesz = ((self.namesz +3) >> 2) << 2
        self['name'].vsSetLength( namesz )

    def pcb_descsz(self):
        # padded to 4 byte alignment
        descct = ((self.descsz +3) >> 2)
        elems = [ v_uint32() for i in range(descct) ]
        self.desc = vstruct.VArray(elems=elems)
