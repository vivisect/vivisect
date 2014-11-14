import vstruct
from vstruct.primitives import *

EI_NIDENT = 4
EI_PADLEN = 7

class Elf32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.e_ident       = v_bytes(EI_NIDENT)
        self.e_class       = v_uint8()
        self.e_data        = v_uint8()
        self.e_fileversion = v_uint8()
        self.e_osabi       = v_uint8()
        self.e_abiversio   = v_uint8()
        self.e_pad         = v_bytes(EI_PADLEN)
        self.e_type        = v_uint16()
        self.e_machine     = v_uint16()
        self.e_version     = v_uint32()
        self.e_entry       = v_uint32()
        self.e_phoff       = v_uint32()
        self.e_shoff       = v_uint32()
        self.e_flags       = v_uint32()
        self.e_ehsize      = v_uint16()
        self.e_phentsize   = v_uint16()
        self.e_phnum       = v_uint16()
        self.e_shentsize   = v_uint16()
        self.e_shnum       = v_uint16()
        self.e_shstrndx    = v_uint16()

class Elf32Section(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.sh_name      = v_uint32()
        self.sh_type      = v_uint32()
        self.sh_flags     = v_uint32()
        self.sh_addr      = v_uint32()
        self.sh_offset    = v_uint32()
        self.sh_size      = v_uint32()
        self.sh_link      = v_uint32()
        self.sh_info      = v_uint32()
        self.sh_addralign = v_uint32()
        self.sh_entsize = v_uint32()

class Elf32Pheader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.p_type   = v_uint32()
        self.p_offset = v_uint32()
        self.p_vaddr  = v_uint32()
        self.p_paddr  = v_uint32()
        self.p_filesz = v_uint32()
        self.p_memsz  = v_uint32()
        self.p_flags  = v_uint32()
        self.p_align  = v_uint32()

class Elf32Reloc(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.r_offset = v_ptr32()
        self.r_info   = v_uint32()

class Elf32Reloca(Elf32Reloc):
    def __init__(self):
        Elf32Reloc.__init__(self)
        self.r_addend = v_uint32()

class Elf32Symbol(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.st_name  = v_uint32()
        self.st_value = v_uint32()
        self.st_size  = v_uint32()
        self.st_info  = v_uint8()
        self.st_other = v_uint8()
        self.st_shndx = v_uint16()

class Elf32Dynamic(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.d_tag   = v_uint32()
        self.d_value = v_uint32()


class Elf64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.e_ident       = v_bytes(EI_NIDENT)
        self.e_class       = v_uint8()
        self.e_data        = v_uint8()
        self.e_fileversion = v_uint8()
        self.e_osabi       = v_uint8()
        self.e_abiversio   = v_uint8()
        self.e_pad         = v_bytes(EI_PADLEN)
        self.e_type        = v_uint16()
        self.e_machine     = v_uint16()
        self.e_version     = v_uint32()
        self.e_entry       = v_uint64()
        self.e_phoff       = v_uint64()
        self.e_shoff       = v_uint64()
        self.e_flags       = v_uint32()
        self.e_ehsize      = v_uint16()
        self.e_phentsize   = v_uint16()
        self.e_phnum       = v_uint16()
        self.e_shentsize   = v_uint16()
        self.e_shnum       = v_uint16()
        self.e_shstrndx    = v_uint16()

class Elf64Section(Elf32Section):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.sh_name      = v_uint32()
        self.sh_type      = v_uint32()
        self.sh_flags     = v_uint64()
        self.sh_addr      = v_uint64()
        self.sh_offset    = v_uint64()
        self.sh_size      = v_uint64()
        self.sh_link      = v_uint32()
        self.sh_info      = v_uint32()
        self.sh_addralign = v_uint64()
        self.sh_entsize   = v_uint64()

class Elf64Pheader(Elf32Pheader):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.p_type   = v_uint32()
        self.p_flags  = v_uint32()
        self.p_offset = v_uint64()
        self.p_vaddr  = v_uint64()
        self.p_paddr  = v_uint64()
        self.p_filesz = v_uint64()
        self.p_memsz  = v_uint64()
        self.p_align  = v_uint64()


class Elf64Reloc(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.r_offset = v_ptr64()
        self.r_info   = v_uint64()

class Elf64Reloca(Elf64Reloc):
    def __init__(self):
        #Elf64Reloc.__init__(self)
        vstruct.VStruct.__init__(self)
        self.r_offset = v_uint64()
        self.r_info   = v_uint64()
        self.r_addend = v_uint64()

class Elf64Symbol(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.st_name  = v_uint32()
        self.st_info  = v_uint8()
        self.st_other = v_uint8()
        self.st_shndx = v_uint16()
        self.st_value = v_uint64()
        self.st_size  = v_uint64()

class Elf64Dynamic(Elf32Dynamic):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.d_tag   = v_uint64()
        self.d_value = v_uint64()

class ElfNote(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.namesz = v_uint32()
        self.descsz = v_uint32()
        self.ntype  = v_uint32()
        self.name   = v_bytes()
        self.desc   = vstruct.VArray()

    def pcb_namesz(self):
        self['name'].vsSetLength( self.namesz )

    def pcb_descsz(self):
        elems = [ v_uint32() for i in xrange(self.descsz / 4) ]
        self.desc = vstruct.VArray(elems=elems)

