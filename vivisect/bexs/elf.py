import vivisect.lib.bits as v_bits
import vivisect.lib.bexfile as v_bexfile

from vivisect.hal.memory import MM_READ, MM_WRITE, MM_EXEC
from vivisect.vstruct.types import *

EI_NIDENT = 4
EI_PADLEN = 7

## EM enumeration definitions
EM_NONE = 0
EM_M32 = 1
EM_SPARC = 2
EM_386 = 3
EM_68K = 4
EM_88K = 5
EM_860 = 7
EM_MIPS = 8
EM_S370 = 9
EM_MIPS_RS3_LE = 10
EM_PARISC = 15
EM_VPP500 = 17
EM_SPARC32PLUS = 18
EM_960 = 19
EM_PPC = 20
EM_PPC64 = 21
EM_S390 = 22
EM_V800 = 36
EM_FR20 = 37
EM_RH32 = 38
EM_RCE = 39
EM_ARM = 40
EM_FAKE_ALPHA = 41
EM_SH = 42
EM_SPARCV9 = 43
EM_TRICORE = 44
EM_ARC = 45
EM_H8_300 = 46
EM_H8_300H = 47
EM_H8S = 48
EM_H8_500 = 49
EM_IA_64 = 50
EM_MIPS_X = 51
EM_COLDFIRE = 52
EM_68HC12 = 53
EM_MMA = 54
EM_PCP = 55
EM_NCPU = 56
EM_NDR1 = 57
EM_STARCORE = 58
EM_ME16 = 59
EM_ST100 = 60
EM_TINYJ = 61
EM_X86_64 = 62
EM_PDSP = 63
EM_FX66 = 66
EM_ST9PLUS = 67
EM_ST7 = 68
EM_68HC16 = 69
EM_68HC11 = 70
EM_68HC08 = 71
EM_68HC05 = 72
EM_SVX = 73
EM_ST19 = 74
EM_VAX = 75
EM_CRIS = 76
EM_JAVELIN = 77
EM_FIREPATH = 78
EM_ZSP = 79
EM_MMIX = 80
EM_HUANY = 81
EM_PRISM = 82
EM_AVR = 83
EM_FR30 = 84
EM_D10V = 85
EM_D30V = 86
EM_V850 = 87
EM_M32R = 88
EM_MN10300 = 89
EM_MN10200 = 90
EM_PJ = 91
EM_OPENRISC = 92
EM_ARC_A5 = 93
EM_XTENSA = 94
EM_NUM = 95
EM_ALPHA = 0x9026

e_machine_64 =  ( EM_X86_64, )

e_machine_arch = {
    EM_ARM:'arm',
    EM_386:'i386',
    EM_X86_64:'amd64',
}

e_machine_order = {
    EM_ARM:'little',
    EM_386:'little',
    EM_X86_64:'little',
}

###############################################
# elf types
ET_NONE = 0
ET_REL  = 1
ET_EXEC = 2
ET_DYN  = 3
ET_CORE = 4
ET_NUM  = 5

ET_LOOS     = 0xfe00
ET_HIOS     = 0xfeff
ET_LOPROC   = 0xff00
ET_HIPROC   = 0xffff

###############################################
# program header types
PT_NULL     = 0
PT_LOAD     = 1
PT_DYNAMIC  = 2
PT_INTERP   = 3
PT_NOTE     = 4
PT_SHLIB    = 5
PT_PHDR     = 6
PT_TLS      = 7
PT_NUM      = 8

PT_LOOS         = 0x60000000
PT_GNU_EH_FRAME = 0x6474e550
PT_GNU_STACK    = 0x6474e551
PT_GNU_RELRO    = 0x6474e552
PT_LOSUNW       = 0x6ffffffa
PT_SUNWBSS      = 0x6ffffffa
PT_SUNWSTACK    = 0x6ffffffb
PT_HISUNW       = 0x6fffffff
PT_HIOS         = 0x6fffffff
PT_LOPROC       = 0x70000000
PT_HIPROC       = 0x7fffffff

###############################################
# dynamic header types
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
DT_INIT_ARRAY       = 25
DT_FINI_ARRAY       = 26
DT_INIT_ARRAYSZ     = 27
DT_FINI_ARRAYSZ     = 28
DT_RUNPATH          = 29
DT_FLAGS            = 30
DT_ENCODING         = 32
DT_PREINIT_ARRAY    = 32
DT_PREINIT_ARRAYSZ  = 33
DT_NUM              = 34
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

###############################################

class Elf32(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.e_ident       = vbytes(EI_NIDENT)
        self.e_class       = uint8()
        self.e_data        = uint8()
        self.e_fileversion = uint8()
        self.e_osabi       = uint8()
        self.e_abiversio   = uint8()
        self.e_pad         = vbytes(EI_PADLEN)
        self.e_type        = uint16()
        self.e_machine     = uint16()
        self.e_version     = uint32()
        self.e_entry       = uint32()
        self.e_phoff       = uint32()
        self.e_shoff       = uint32()
        self.e_flags       = uint32()
        self.e_ehsize      = uint16()
        self.e_phentsize   = uint16()
        self.e_phnum       = uint16()
        self.e_shentsize   = uint16()
        self.e_shnum       = uint16()
        self.e_shstrndx    = uint16()

class Elf32Section(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.sh_name      = uint32()
        self.sh_type      = uint32()
        self.sh_flags     = uint32()
        self.sh_addr      = uint32()
        self.sh_offset    = uint32()
        self.sh_size      = uint32()
        self.sh_link      = uint32()
        self.sh_info      = uint32()
        self.sh_addralign = uint32()
        self.sh_entsize = uint32()

class Elf32Pheader(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.p_type   = uint32()
        self.p_offset = uint32()
        self.p_vaddr  = uint32()
        self.p_paddr  = uint32()
        self.p_filesz = uint32()
        self.p_memsz  = uint32()
        self.p_flags  = uint32()
        self.p_align  = uint32()

class Elf32Reloc(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.r_offset = ptr32()
        self.r_info   = uint32()

class Elf32Reloca(Elf32Reloc):
    def __init__(self):
        Elf32Reloc.__init__(self)
        self.r_addend = uint32()

class Elf32Symbol(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.st_name  = uint32()
        self.st_value = uint32()
        self.st_size  = uint32()
        self.st_info  = uint8()
        self.st_other = uint8()
        self.st_shndx = uint16()

class Elf32Dynamic(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.d_tag   = uint32()
        self.d_value = uint32()
        self._dyn_name = None

    def getDynName(self):
        return self._dyn_name

    def setDynName(self, name):
        self._dyn_name = name

class Elf64(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.e_ident       = vbytes(EI_NIDENT)
        self.e_class       = uint8()
        self.e_data        = uint8()
        self.e_fileversion = uint8()
        self.e_osabi       = uint8()
        self.e_abiversio   = uint8()
        self.e_pad         = vbytes(EI_PADLEN)
        self.e_type        = uint16()
        self.e_machine     = uint16()
        self.e_version     = uint32()
        self.e_entry       = uint64()
        self.e_phoff       = uint64()
        self.e_shoff       = uint64()
        self.e_flags       = uint32()
        self.e_ehsize      = uint16()
        self.e_phentsize   = uint16()
        self.e_phnum       = uint16()
        self.e_shentsize   = uint16()
        self.e_shnum       = uint16()
        self.e_shstrndx    = uint16()

class Elf64Section(Elf32Section):
    def __init__(self):
        VStruct.__init__(self)
        self.sh_name      = uint32()
        self.sh_type      = uint32()
        self.sh_flags     = uint64()
        self.sh_addr      = uint64()
        self.sh_offset    = uint64()
        self.sh_size      = uint64()
        self.sh_link      = uint32()
        self.sh_info      = uint32()
        self.sh_addralign = uint64()
        self.sh_entsize   = uint64()

class Elf64Pheader(Elf32Pheader):
    def __init__(self):
        VStruct.__init__(self)
        self.p_type   = uint32()
        self.p_flags  = uint32()
        self.p_offset = uint64()
        self.p_vaddr  = uint64()
        self.p_paddr  = uint64()
        self.p_filesz = uint64()
        self.p_memsz  = uint64()
        self.p_align  = uint64()


class Elf64Reloc(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.r_offset = ptr64()
        self.r_info   = uint64()

class Elf64Reloca(Elf64Reloc):
    def __init__(self):
        #Elf64Reloc.__init__(self)
        VStruct.__init__(self)
        self.r_offset = uint64()
        self.r_info   = uint64()
        self.r_addend = uint64()

class Elf64Symbol(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.st_name  = uint32()
        self.st_info  = uint8()
        self.st_other = uint8()
        self.st_shndx = uint16()
        self.st_value = uint64()
        self.st_size  = uint64()

class Elf64Dynamic(Elf32Dynamic):
    def __init__(self):
        VStruct.__init__(self)
        self.d_tag   = uint64()
        self.d_value = uint64()

class ElfNote(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        self.namesz = uint32()
        self.descsz = uint32()
        self.ntype  = uint32()
        self.name   = vbytes()
        self.desc   = VArray()

    #def pcb_namesz(self):
        #self['name'].vsSetLength( self.namesz )

    #def pcb_descsz(self):
        #elems = [ uint32() for i in xrange(self.descsz / 4) ]
        #self.desc = VArray(elems=elems)

class ElfBexFile(v_bexfile.BexFile):

    def __init__(self, fd, **info):
        info.setdefault('zeromap',4096)
        v_bexfile.BexFile.__init__(self, fd, **info)

    def _bex_arch(self):
        elf = self.info('elf:header')
        return e_machine_arch.get(elf.e_machine)

    def _bex_format(self):
        return 'elf'

    def _bex_ptrsize(self):
        elf = self.info('elf:header')
        if elf.e_machine in e_machine_64:
            return 8
        return 4

    def _bex_byteorder(self):
        elf = self.info('elf:header')
        return e_machine_order.get(elf.e_machine)

    def _bex_bintype(self):
        elf = self.info('elf:header')
        if elf.e_type == ET_DYN:
            return 'dyn'
        if elf.e_type == ET_EXEC:
            return 'exe'
        return 'unk'

    def _bex_baseaddr(self):

        addr = None
        for off,pgm in self.info('elf:pheaders'):
            if not pgm.p_vaddr:
                continue

            if addr == None:
                addr = pgm.p_vaddr
                continue

            addr = min(addr,pgm.p_vaddr)

        # if we didn't get one, make one up
        if addr == None:
            addr = 0x20000000

        return addr

    def _bex_sections(self):
        # return (ra,size,name) tuples
        elf = self.info('elf:header')
        strbase = elf.e_shstrndx

        secs = self.info('elf:sections')
        if not secs:
            return ()

        strsec = secs[ elf.e_shstrndx ][1]
        stroff = strsec.sh_offset

        ret =  []
        for off,sec in secs:
            name = self.asciiAtOff( stroff + sec.sh_name, 256 )
            ret.append( (sec.sh_addr,sec.sh_size,name) )

        return ret

    def _bex_info_elf_sections(self):
        elf = self.info('elf:header')
        if not elf.e_shoff:
            return ()

        cls = Elf32Section
        if self.ptrsize() == 8:
            cls = Elf64Section

        off = elf.e_shoff
        size = elf.e_shentsize * elf.e_shnum
        return list( self.structs(off,size,cls,off=True) )

    def _bex_info_elf_prelink(self):
        for off,dyn in self.info('elf:dynamics'):
            if dyn.d_tag == DT_GNU_PRELINKED:
                return True
            if dyn.d_tag == DT_GNU_CONFLICTSZ:
                return True
        return False

    def _bex_info_elf_dynsyms(self):

        sec = self.info('elf:secbyname').get('.dynsym')
        if sec == None:
            return ()

        if not sec.sh_off:
            return ()

        raise Exception('.dynsym!')

    def _bex_info_elf_dynamics(self):
        cls = Elf32Dynamic
        if self.ptrsize() == 8:
            cls = Elf64Dynamic

        sec = self.info('elf:secbyname').get('.dynamic')
        if not sec:
            return ()

        dyns = []
        for off,dyn in self.structs(sec.sh_offset,sec.sh_size,cls,off=True):

            if dyn.d_tag == DT_NULL:
                break

            if dyn.d_tag in (DT_NEEDED,DT_SONAME):
                name = self._elf_strtab(dyn.d_value,'.dynstr')
                dyn.setDynName(name)

            dyns.append( (off,dyn) )

        return dyns

    def _bex_info_elf_secbyname(self):
        elf = self.info('elf:header')
        strbase = elf.e_shstrndx

        secs = self.info('elf:sections')
        if not secs:
            return ()

        strsec = secs[ elf.e_shstrndx ][1]
        stroff = strsec.sh_offset

        ret =  {}
        for off,sec in secs:
            name = self.asciiAtOff( stroff + sec.sh_name, 256 )
            ret[name] = sec

        return ret

    def _elf_strtab(self, off, sec):
        sec = self.info('elf:secbyname').get(sec)
        if not sec:
            return None
        return self.asciiAtOff( sec.sh_offset + off, sec.sh_size )

    def _bex_memmaps(self):
        ret = []
        for off,pgm in self.info('elf:pheaders'):

            if pgm.p_type != PT_LOAD:
                continue

            mem = self.readAtOff(pgm.p_offset, pgm.p_filesz)
            mem = mem.rjust(pgm.p_memsz,b'\x00')

            ret.append( (pgm.p_vaddr, pgm.p_flags & 0x7, mem) )

        return ret

    def _bex_info_elf_pheaders(self):
        pcls = Elf32Pheader
        if self.ptrsize() == 8:
            pcls = Elf64Pheader

        elf = self.info('elf:header')

        off = elf.e_phoff
        size = elf.e_phnum * elf.e_phentsize
        return list( self.structs(off, size, pcls, off=True) )

    def _bex_info_elf_header(self):
        elf = self.struct(0,Elf32)
        if elf.e_machine in e_machine_64:
            elf = self.struct(0,Elf64)
        return elf

def isElfFd(fd):
    if fd.read(4) == b'\x7fELF':
        return True

v_bexfile.addBexFormat('elf',isElfFd,ElfBexFile)
