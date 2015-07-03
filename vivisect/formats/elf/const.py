# consts for elf parsing

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
# elf abi
e_osabi = {
    0x00:'sysv',
    0x01:'hpux',
    0x02:'netbsd',
    0x03:'linux',
    0x06:'solaris',
    0x07:'aix',
    0x08:'irix',
    0x09:'freebsd',
    0x0c:'openbsd',
    0x0d:'openvms',
}

ELF_NOTE_OS_LINUX       = 0
ELF_NOTE_OS_GNU         = 1
ELF_NOTE_OS_SOLARIS2    = 2
ELF_NOTE_OS_FREEBSD     = 3

gnu_osabi = {
    ELF_NOTE_OS_LINUX       :'linux',
    ELF_NOTE_OS_GNU         :'hurd',
    ELF_NOTE_OS_SOLARIS2    :'solaris',
    ELF_NOTE_OS_FREEBSD     :'freebsd',
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
