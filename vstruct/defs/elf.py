import vstruct
from vstruct.primitives import *
from vstruct.defs.constants.elf import *

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
