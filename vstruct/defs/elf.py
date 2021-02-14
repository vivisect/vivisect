import vstruct
from vstruct.primitives import *

EI_NIDENT = 4
EI_PADLEN = 7

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

class Elf32Section(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf32Pheader(vstruct.VStruct):
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

class Elf32Reloc(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf32Reloca(Elf32Reloc):
    def __init__(self, bigend=False):
        Elf32Reloc.__init__(self)
        self.r_addend = v_uint32(bigend=bigend)

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

class Elf32Symbol(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf32Dynamic(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf64Section(Elf32Section):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf64Pheader(Elf32Pheader):
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


class Elf64Reloc(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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

class Elf64Reloca(Elf64Reloc):
    def __init__(self, bigend=False):
        #Elf64Reloc.__init__(self)
        vstruct.VStruct.__init__(self)
        self.r_offset = v_uint64(bigend=bigend)
        self.r_info   = v_uint64(bigend=bigend)
        self.r_addend = v_uint64(bigend=bigend)

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

class Elf64Symbol(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
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
