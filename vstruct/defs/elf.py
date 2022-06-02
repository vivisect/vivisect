import vstruct
from vstruct.primitives import *

EI_NIDENT = 4
EI_PADLEN = 7

SHF_WRITE = 1
SHF_ALLOC = 2
SHF_EXECINSTR = 4
SHF_MERGE = 16
SHF_STRINGS = 32
SHF_INFO_LINK = 64
SHF_LINK_ORDER = 128
SHF_OS_NONCONFORMING = 256
SHF_GROUP = 512
SHF_TLS = 1024
SHF_ORDERED = 1073741824
SHF_EXCLUDE = 2147483648

sh_flags = {
    SHF_WRITE:"Writable",
    SHF_ALLOC:"Occupies memory during execution",
    SHF_EXECINSTR:"Executable",
    SHF_MERGE:"Might be merged",
    SHF_STRINGS:"Contains nul-terminated strings",
    SHF_INFO_LINK:"`sh_info' contains SHT index",
    SHF_LINK_ORDER:"Preserve order after combining",
    SHF_OS_NONCONFORMING:"Non-standard OS specific",
    SHF_GROUP:"Section is member of a group.",
    SHF_TLS:"Section hold thread-local data.",
    SHF_ORDERED:"Special ordering",
    SHF_EXCLUDE:"Section is excluded",
}

PT_NULL     = 0
PT_LOAD     = 1
PT_DYNAMIC  = 2
PT_INTERP   = 3
PT_NOTE     = 4
PT_SHLIB    = 5
PT_PHDR     = 6
PT_TLS      = 7
PT_NUM      = 8
PT_LOOS     = 0x60000000
PT_GNU_EH_FRAME  = 0x6474e550
PT_GNU_STACK  = 0x6474e551
PT_GNU_RELRO  = 0x6474e552
PT_LOSUNW   = 0x6ffffffa
PT_SUNWBSS  = 0x6ffffffa
PT_SUNWSTACK = 0x6ffffffb
PT_HISUNW =  0x6fffffff
PT_HIOS   =  0x6fffffff
PT_LOPROC =  0x70000000
PT_HIPROC =  0x7fffffff

ph_types = {
    PT_NULL:"Program header table entry unused",
    PT_LOAD:"Loadable program segment",
    PT_DYNAMIC:"Dynamic linking information",
    PT_INTERP:"Program interpreter",
    PT_NOTE:"Auxiliary information",
    PT_SHLIB:"Reserved",
    PT_PHDR:"Entry for header table itself",
    PT_TLS:"Thread-local storage segment",
    PT_NUM:"Number of defined types",
    PT_LOOS:"Start of OS-specific",
    PT_GNU_EH_FRAME:"GCC .eh_frame_hdr segment",
    PT_GNU_STACK:"Indicates stack executability",
    PT_GNU_RELRO:"Read-only after relocation",
    PT_SUNWBSS:"Sun Specific segment",
    PT_SUNWSTACK:"Stack segment",
    PT_HIOS:"End of OS-specific",
    PT_LOPROC:"Start of processor-specific",
    PT_HIPROC:"End of processor-specific",
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
