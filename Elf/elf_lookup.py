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
EM_MSP430 = 105
EM_ARM_AARCH64 = 183
EM_ALPHA = 0x9026

# There are plenty more of these to
# fill in, but...  this is all I need
# for now...
e_machine_32 =  (
                EM_386,
                EM_PPC,
                EM_ARM,
                )
e_machine_64 =  (
                EM_PPC64,
                EM_SPARCV9,
                EM_X86_64,
                EM_ARM_AARCH64,
                )
                
ELFCLASSNONE = 0
ELFCLASS32 = 1 # 32-bit object file
ELFCLASS64 = 2 # 64-bit object file

ELFDATANONE = 0
ELFDATA2LSB = 1
ELFDATA2MSB = 2

e_machine_types = {
    EM_NONE:"No machine",
    EM_M32:"AT&T WE 32100",
    EM_SPARC:"SUN SPARC",
    EM_386:"Intel 80386",
    EM_68K:"Motorola m68k family",
    EM_88K:"Motorola m88k family",
    EM_860:"Intel 80860",
    EM_MIPS:"MIPS R3000 big-endian",
    EM_S370:"IBM System/370",
    EM_MIPS_RS3_LE:"MIPS R3000 little-endian",
    EM_PARISC:"HPPA",
    EM_VPP500:"Fujitsu VPP500",
    EM_SPARC32PLUS:"Suns v8plus",
    EM_960:"Intel 80960",
    EM_PPC:"PowerPC",
    EM_PPC64:"PowerPC 64-bit",
    EM_S390:"IBM S390",
    EM_V800:"NEC V800 series",
    EM_FR20:"Fujitsu FR20",
    EM_RH32:"TRW RH-32",
    EM_RCE:"Motorola RCE",
    EM_ARM:"ARM",
    EM_FAKE_ALPHA:"Digital Alpha",
    EM_SH:"Hitachi SH",
    EM_SPARCV9:"SPARC v9 64-bit",
    EM_TRICORE:"Siemens Tricore",
    EM_ARC:"Argonaut RISC Core",
    EM_H8_300:"Hitachi H8/300",
    EM_H8_300H:"Hitachi H8/300H",
    EM_H8S:"Hitachi H8S",
    EM_H8_500:"Hitachi H8/500",
    EM_IA_64:"Intel Merced",
    EM_MIPS_X:"Stanford MIPS-X",
    EM_COLDFIRE:"Motorola Coldfire",
    EM_68HC12:"Motorola M68HC12",
    EM_MMA:"Fujitsu MMA Multimedia",
    EM_PCP:"Siemens PCP",
    EM_NCPU:"Sony nCPU embeeded RISC",
    EM_NDR1:"Denso NDR1 microprocessor",
    EM_STARCORE:"Motorola Start*Core processor",
    EM_ME16:"Toyota ME16 processor",
    EM_ST100:"STMicroelectronic ST100 processor",
    EM_TINYJ:"Advanced Logic Corp. Tinyj",
    EM_X86_64:"AMD x86-64 architecture",
    EM_PDSP:"Sony DSP Processor",
    EM_FX66:"Siemens FX66 microcontroller",
    EM_ST9PLUS:"STMicroelectronics ST9+ 8/16 mc",
    EM_ST7:"STmicroelectronics ST7 8 bit mc",
    EM_68HC16:"Motorola MC68HC16 microcontroller",
    EM_68HC11:"Motorola MC68HC11 microcontroller",
    EM_68HC08:"Motorola MC68HC08 microcontroller",
    EM_68HC05:"Motorola MC68HC05 microcontroller",
    EM_SVX:"Silicon Graphics SVx",
    EM_ST19:"STMicroelectronics ST19 8 bit mc",
    EM_VAX:"Digital VAX",
    EM_CRIS:"Axis Communications 32-bit embedded processor",
    EM_JAVELIN:"Infineon Technologies 32-bit embedded processor",
    EM_FIREPATH:"Element 14 64-bit DSP Processor",
    EM_ZSP:"LSI Logic 16-bit DSP Processor",
    EM_MMIX:"Donald Knuths educational 64-bit processor",
    EM_HUANY:"Harvard University machine-independent object files",
    EM_PRISM:"SiTera Prism",
    EM_AVR:"Atmel AVR 8-bit microcontroller",
    EM_FR30:"Fujitsu FR30",
    EM_D10V:"Mitsubishi D10V",
    EM_D30V:"Mitsubishi D30V",
    EM_V850:"NEC v850",
    EM_M32R:"Mitsubishi M32R",
    EM_MN10300:"Matsushita MN10300",
    EM_MN10200:"Matsushita MN10200",
    EM_PJ:"picoJava",
    EM_OPENRISC:"OpenRISC 32-bit embedded processor",
    EM_ARC_A5:"ARC Cores Tangent-A5",
    EM_XTENSA:"Tensilica Xtensa Architecture",
    EM_NUM:"",
    EM_ARM_AARCH64:"ARM aarch64",
    EM_ALPHA:"",
}

ET_NONE = 0
ET_REL = 1
ET_EXEC = 2
ET_DYN = 3
ET_CORE = 4
ET_NUM = 5
ET_LOOS = 0xfe00
ET_HIOS = 0xfeff
ET_LOPROC = 0xff00
ET_HIPROC = 0xffff

e_types = {
    ET_NONE:"No file type",
    ET_REL:"Relocatable file",
    ET_EXEC:"Executable file",
    ET_DYN:"Shared object file",
    ET_CORE:"Core file",
    ET_NUM:"Number of defined types",
    ET_LOOS:"OS-specific range start",
    ET_HIOS:"OS-specific range end",
    ET_LOPROC:"Processor-specific range start",
    ET_HIPROC:"Processor-specific range end",
}

EV_NONE = 0
EV_CURRENT = 1
EV_NUM = 2

e_versions = {
    EV_NONE:"Invalid ELF version",
    EV_CURRENT:"Current version",
    EV_NUM:"",
}

R_68K_NONE = 0
R_68K_32 = 1
R_68K_16 = 2
R_68K_8 = 3
R_68K_PC32 = 4
R_68K_PC16 = 5
R_68K_PC8 = 6
R_68K_GOT32 = 7
R_68K_GOT16 = 8
R_68K_GOT8 = 9
R_68K_GOT32O = 10
R_68K_GOT16O = 11
R_68K_GOT8O = 12
R_68K_PLT32 = 13
R_68K_PLT16 = 14
R_68K_PLT8 = 15
R_68K_PLT32O = 16
R_68K_PLT16O = 17
R_68K_PLT8O = 18
R_68K_COPY = 19
R_68K_GLOB_DAT = 20
R_68K_JMP_SLOT = 21
R_68K_RELATIVE = 22

e_flags_68k = {
    R_68K_NONE:"No reloc",
    R_68K_32:"Direct 32 bit",
    R_68K_16:"Direct 16 bit",
    R_68K_8:"Direct 8 bit",
    R_68K_PC32:"PC relative 32 bit",
    R_68K_PC16:"PC relative 16 bit",
    R_68K_PC8:"PC relative 8 bit",
    R_68K_GOT32:"32 bit PC relative GOT entry",
    R_68K_GOT16:"16 bit PC relative GOT entry",
    R_68K_GOT8:"8 bit PC relative GOT entry",
    R_68K_GOT32O:"32 bit GOT offset",
    R_68K_GOT16O:"16 bit GOT offset",
    R_68K_GOT8O:"8 bit GOT offset",
    R_68K_PLT32:"32 bit PC relative PLT address",
    R_68K_PLT16:"16 bit PC relative PLT address",
    R_68K_PLT8:"8 bit PC relative PLT address",
    R_68K_PLT32O:"32 bit PLT offset",
    R_68K_PLT16O:"16 bit PLT offset",
    R_68K_PLT8O:"8 bit PLT offset",
    R_68K_COPY:"Copy symbol at runtime",
    R_68K_GLOB_DAT:"Create GOT entry",
    R_68K_JMP_SLOT:"Create PLT entry",
    R_68K_RELATIVE:"Adjust by program base",
}

R_ARM_NONE          = 0   # No reloc */
R_ARM_PC24          = 1   # PC relative 26 bit branch */
R_ARM_ABS32         = 2   # Direct 32 bit  */
R_ARM_REL32         = 3   # PC relative 32 bit */
R_ARM_PC13          = 4
R_ARM_LDR_PC_G0     = 4   # also 4
R_ARM_ABS16         = 5   # Direct 16 bit */
R_ARM_ABS12         = 6   # Direct 12 bit */
R_ARM_THM_ABS5      = 7
R_ARM_ABS8          = 8   # Direct 8 bit */
R_ARM_SBREL32       = 9
R_ARM_THM_PC22      = 10
R_ARM_THM_PC8       = 11
R_ARM_AMP_VCALL9    = 12
R_ARM_BREL_ADJ      = 12  # also 12
R_ARM_SWI24         = 13
R_ARM_TLS_DESC      = 13  # also 13
R_ARM_THM_SWI8      = 14
R_ARM_XPC25         = 15
R_ARM_THM_XPC22     = 16
R_ARM_TLS_DTPMOD32  = 17  # ID of module containing symbol */
R_ARM_TLS_DTPOFF32  = 18  # Offset in TLS block */
R_ARM_TLS_TPOFF32   = 19  # Offset in static TLS block */
R_ARM_COPY          = 20  # Copy symbol at runtime */
R_ARM_GLOB_DAT      = 21  # Create GOT entry */
R_ARM_JUMP_SLOT     = 22  # Create PLT entry */
R_ARM_RELATIVE      = 23  # Adjust by program base */
R_ARM_GOTOFF        = 24  # 32 bit offset to GOT */
R_ARM_GOTPC         = 25  # 32 bit PC relative offset to GOT */
R_ARM_GOT32         = 26  # 32 bit GOT entry */
R_ARM_PLT32         = 27  # 32 bit PLT address */
R_ARM_CALL          = 28
R_ARM_JUMP24        = 29
R_ARM_THM_JUMP24        = 30
R_ARM_BASE_ABS          = 31
R_ARM_ALU_PCREL_7_0     = 32
R_ARM_ALU_PCREL_15_8    = 33
R_ARM_ALU_PCREL_23_15   = 34
R_ARM_LDR_SBREL_11_0    = 35
R_ARM_ALU_SBREL_19_12   = 36
R_ARM_ALU_SBREL_27_20   = 37
R_ARM_GNU_VTENTRY   = 100
R_ARM_GNU_VTINHERIT = 101
R_ARM_THM_PC11      = 102 # thumb unconditional branch */
R_ARM_THM_PC9       = 103 # thumb conditional branch */
R_ARM_TLS_GD32      = 104 # PC-rel 32 bit for global dynamic thread local data */
R_ARM_TLS_LDM32     = 105 # PC-rel 32 bit for local dynamic thread local data */
R_ARM_TLS_LDO32     = 106 # 32 bit offset relative to TLS block */
R_ARM_TLS_IE32      = 107 # PC-rel 32 bit for GOT entry of static TLS block offset */
R_ARM_TLS_LE32      = 108 # 32 bit offset relative to static TLS block */
R_ARM_IRELATIVE     = 160
R_ARM_RXPC25        = 249
R_ARM_RSBREL32      = 250
R_ARM_THM_RPC22     = 251
R_ARM_RREL32        = 252
R_ARM_RABS22        = 253
R_ARM_RPC24         = 254
R_ARM_RBASE         = 255

R_ARMCLASS_DATA = 0
R_ARMCLASS_ARM = 1
R_ARMCLASS_THUMB16 = 2
R_ARMCLASS_THUMB32 = 3
R_ARMCLASS_MISC = 4

r_armclasses = [
        (R_ARM_ABS32,
            R_ARM_REL32,
            R_ARM_ABS16,
            R_ARM_ABS8,
            R_ARM_SBREL32,
            R_ARM_BREL_ADJ,
            R_ARM_TLS_DESC,
            R_ARM_TLS_DTPMOD32,
            R_ARM_TLS_DTPOFF32,
            R_ARM_TLS_TPOFF32,
            R_ARM_GLOB_DAT,
            R_ARM_JUMP_SLOT,
            R_ARM_RELATIVE,
            R_ARM_GOTOFF,
            R_ARM_GOTPC,
            R_ARM_GOT32,
            R_ARM_IRELATIVE,
            ),
        (
            R_ARM_PC24,
            R_ARM_LDR_PC_G0,
            R_ARM_ABS12,
            R_ARM_PLT32,
            R_ARM_CALL,
            R_ARM_JUMP24,
            R_ARM_LDR_SBREL_11_0,
            R_ARM_ALU_SBREL_19_12,
            R_ARM_ALU_SBREL_27_20,
            ),
        (
            R_ARM_THM_ABS5,
            R_ARM_THM_PC8,
            ),
        (
            R_ARM_THM_PC22,
            R_ARM_THM_JUMP24,
            ),
        (
            R_ARM_NONE,
            R_ARM_COPY,
            ),
        ]








R_386_NONE = 0
R_386_32 = 1
R_386_PC32 = 2
R_386_GOT32 = 3
R_386_PLT32 = 4
R_386_COPY = 5
R_386_GLOB_DAT = 6
R_386_JMP_SLOT = 7
R_386_RELATIVE = 8
R_386_GOTOFF = 9
R_386_GOTPC = 10
R_386_32PLT = 11
R_386_TLS_TPOFF = 14
R_386_TLS_IE = 15
R_386_TLS_GOTIE = 16
R_386_TLS_LE = 17
R_386_TLS_GD = 18
R_386_TLS_LDM = 19
R_386_16 = 20
R_386_PC16 = 21
R_386_8 = 22
R_386_PC8 = 23
R_386_TLS_GD_32 = 24
R_386_TLS_GD_PUSH = 25
R_386_TLS_GD_CALL = 26
R_386_TLS_GD_POP = 27
R_386_TLS_LDM_32 = 28
R_386_TLS_LDM_PUSH = 29
R_386_TLS_LDM_CALL = 30
R_386_TLS_LDM_POP = 31
R_386_TLS_LDO_32 = 32
R_386_TLS_IE_32 = 33
R_386_TLS_LE_32 = 34
R_386_TLS_DTPMOD32 = 35
R_386_TLS_DTPOFF32 = 36
R_386_TLS_TPOFF32 = 37

r_types_386 = {
    R_386_NONE:"No reloc",
    R_386_32:"Direct 32 bit",
    R_386_PC32:"PC relative 32 bit",
    R_386_GOT32:"32 bit GOT entry",
    R_386_PLT32:"32 bit PLT address",
    R_386_COPY:"Copy symbol at runtime",
    R_386_GLOB_DAT:"Create GOT entry",
    R_386_JMP_SLOT:"Create PLT entry",
    R_386_RELATIVE:"Adjust by program base",
    R_386_GOTOFF:"32 bit offset to GOT",
    R_386_GOTPC:"32 bit PC relative offset to GOT",
    R_386_32PLT:"",
    R_386_TLS_TPOFF:"Offset in static TLS block",
    R_386_TLS_IE:"Address of GOT entry for static",
    R_386_TLS_GOTIE:"GOT entry for static TLS",
    R_386_TLS_LE:"Offset relative to static",
    R_386_TLS_GD:"Direct 32 bit for GNU version",
    R_386_TLS_LDM:"Direct 32 bit for GNU version",
    R_386_16:"",
    R_386_PC16:"",
    R_386_8:"",
    R_386_PC8:"",
    R_386_TLS_GD_32:"Direct 32 bit for general",
    R_386_TLS_GD_PUSH:"Tag for pushl in GD TLS code",
    R_386_TLS_GD_CALL:"Relocation for call",
    R_386_TLS_GD_POP:"Tag for popl in GD TLS code",
    R_386_TLS_LDM_32:"Direct 32 bit for local",
    R_386_TLS_LDM_PUSH:"Tag for pushl in LDM TLS code",
    R_386_TLS_LDM_CALL:"Relocation for call",
    R_386_TLS_LDM_POP:"Tag for popl in LDM TLS code",
    R_386_TLS_LDO_32:"Offset relative to TLS block",
    R_386_TLS_IE_32:"GOT entry for negated static",
    R_386_TLS_LE_32:"Negated offset relative to",
    R_386_TLS_DTPMOD32:"ID of module containing symbol",
    R_386_TLS_DTPOFF32:"Offset in TLS block",
    R_386_TLS_TPOFF32:"Negated offset in static TLS block",
}

R_X86_64_NONE        = 0
R_X86_64_64          = 1
R_X86_64_PC32        = 2
R_X86_64_GOT32       = 3
R_X86_64_PLT32       = 4
R_X86_64_COPY        = 5
R_X86_64_GLOB_DAT    = 6
R_X86_64_JUMP_SLOT   = 7
R_X86_64_RELATIVE    = 8
R_X86_64_GOTPCREL    = 9
R_X86_64_32          = 10
R_X86_64_32S         = 11
R_X86_64_16          = 12
R_X86_64_PC16        = 13
R_X86_64_8           = 14
R_X86_64_PC8         = 15
R_X86_64_DTPMOD64    = 16
R_X86_64_DTPOFF64    = 17
R_X86_64_TPOFF64     = 18
R_X86_64_TLSGD       = 19
R_X86_64_TLSLD       = 20
R_X86_64_DTPOFF32    = 21
R_X86_64_GOTTPOFF    = 22
R_X86_64_TPOFF32     = 23
R_X86_64_NUM         = 24
R_X86_64_GOTOFF64    = 25
R_X86_64_GOTPC32     = 26
R_X86_64_GOT64       = 27
R_X86_64_GOTPCREL64  = 28
R_X86_64_GOTPC64     = 29
R_X86_64_GOTPLT64    = 30
R_X86_64_PLTOFF64    = 31
R_X86_64_SIZE32      = 32
R_X86_64_SIZE64      = 33
R_X86_64_GOTPC32_TLSDESC = 34
R_X86_64_TLSDESC_CALL = 35
R_X86_64_TLSDESC     = 36
R_X86_64_IRELATIVE   = 37


r_types_amd64 = {
    R_X86_64_NONE       :'No reloc',
    R_X86_64_64         :'Direct 64 bit ',
    R_X86_64_PC32       :'PC relative 32 bit signed',
    R_X86_64_GOT32      :'32 bit GOT entry',
    R_X86_64_PLT32      :'32 bit PLT address',
    R_X86_64_COPY       :'Copy symbol at runtime',
    R_X86_64_GLOB_DAT   :'Create GOT entry',
    R_X86_64_JUMP_SLOT  :'Create PLT entry',
    R_X86_64_RELATIVE   :'Adjust by program base',
    R_X86_64_GOTPCREL   :'32 bit signed PC relative offset to GOT',
    R_X86_64_32         :'Direct 32 bit zero extended',
    R_X86_64_32S        :'Direct 32 bit sign extended',
    R_X86_64_16         :'Direct 16 bit zero extended',
    R_X86_64_PC16       :'16 bit sign extended pc relative',
    R_X86_64_8          :'Direct 8 bit sign extended ',
    R_X86_64_PC8        :'8 bit sign extended pc relative',
    R_X86_64_DTPMOD64   :'ID of module containing symbol',
    R_X86_64_DTPOFF64   :'Offset in modules TLS block',
    R_X86_64_TPOFF64    :'Offset in initial TLS block',
    R_X86_64_TLSGD      :'32 bit signed PC relative offset to two GOT entries for GD symbol',
    R_X86_64_TLSLD      :'32 bit signed PC relative offset to two GOT entries for LD symbol',
    R_X86_64_DTPOFF32   :'Offset in TLS block',
    R_X86_64_GOTTPOFF   :'32 bit signed PC relative offset to GOT entry for IE symbol',
    R_X86_64_TPOFF32    :'Offset in initial TLS block',
    R_X86_64_GOTOFF64   :'64 bit offset to GOT',
    R_X86_64_GOTPC32    :'32 bit signed pc relative offset to GOT',
    R_X86_64_GOT64      :'64-bit GOT entry offset',
    R_X86_64_GOTPCREL64 :'64-bit PC relative offset to GOT entry',
    R_X86_64_GOTPC64    :'64-bit PC relative offset to GOT',
    R_X86_64_GOTPLT64   :'like GOT64, says PLT entry needed',
    R_X86_64_PLTOFF64   :'64-bit GOT relative offset to PLT entry',
    R_X86_64_SIZE32     :'Size of symbol plus 32-bit addend',
    R_X86_64_SIZE64     :'Size of symbol plus 64-bit addend',
    R_X86_64_GOTPC32_TLSDESC :'GOT offset for TLS descriptor. ',
    R_X86_64_TLSDESC_CALL :'Marker for call through TLS descriptor. ',
    R_X86_64_TLSDESC    :'TLS descriptor. ',
    R_X86_64_IRELATIVE  :'Adjust indirectly by program base',
}

## Define e_flags to 386
SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_HASH = 5
SHT_DYNAMIC = 6
SHT_NOTE = 7
SHT_NOBITS = 8
SHT_REL = 9
SHT_SHLIB = 10
SHT_DYNSYM = 11
SHT_INIT_ARRAY = 14
SHT_FINI_ARRAY = 15
SHT_PREINIT_ARRAY = 16
SHT_GROUP = 17
SHT_SYMTAB_SHNDX = 18
SHT_LOOS = 0x60000000
SHT_GNU_LIBLIST = 0x6ffffff7
SHT_CHECKSUM = 0x6ffffff8
SHT_LOSUNW = 0x6ffffffa
SHT_GNU_verdef = 0x6ffffffd
SHT_GNU_verneed = 0x6ffffffe
SHT_GNU_versym = 0x6fffffff
SHT_HISUNW = 0x6fffffff
SHT_HIOS = 0x6fffffff
SHT_LOPROC = 0x70000000
SHT_HIPROC = 0x7fffffff
SHT_LOUSER = 0x80000000
SHT_HIUSER = 0x8fffffff

sht_lookup ={y: x for x, y in globals().items() if x.startswith("SHT_")}

sh_type = {
    SHT_NULL:"Section header table entry unused",
    SHT_PROGBITS:"Program data",
    SHT_SYMTAB:"Symbol table",
    SHT_STRTAB:"String table",
    SHT_RELA:"Relocation entries with addends",
    SHT_HASH:"Symbol hash table",
    SHT_DYNAMIC:"Dynamic linking information",
    SHT_NOTE:"Notes",
    SHT_NOBITS:"Program space with no data (bss)",
    SHT_REL:"Relocation entries, no addends",
    SHT_SHLIB:"Reserved",
    SHT_DYNSYM:"Dynamic linker symbol table",
    SHT_INIT_ARRAY:"Array of constructors",
    SHT_FINI_ARRAY:"Array of destructors",
    SHT_PREINIT_ARRAY:"Array of pre-constructors",
    SHT_GROUP:"Section group",
    SHT_SYMTAB_SHNDX:"Extended section indeces",
    SHT_LOOS:"Start OS-specific",
    SHT_GNU_LIBLIST:"Prelink library list",
    SHT_CHECKSUM:"Checksum for DSO content.",
    SHT_LOSUNW:"Sun-specific low bound.",
    SHT_GNU_verdef:"Version definition section.",
    SHT_GNU_verneed:"Version needs section.",
    SHT_GNU_versym:"Version symbol table.",
    SHT_HISUNW:"Sun-specific high bound.",
    SHT_HIOS:"End OS-specific type",
    SHT_LOPROC:"Start of processor-specific",
    SHT_HIPROC:"End of processor-specific",
    SHT_LOUSER:"Start of application-specific",
    SHT_HIUSER:"End of application-specific",
}

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

STB_LOCAL = 0
STB_GLOBAL = 1
STB_WEAK = 2
STB_LOOS = 10
STB_HIOS = 12
STB_LOPROC = 13
STB_HIPROC = 15

stb_lookup ={y: x for x, y in globals().items() if x.startswith("STB_")}

st_info_bind = {
    STB_LOCAL:"Local symbol",
    STB_GLOBAL:"Global symbol",
    STB_WEAK:"Weak symbol",
    STB_LOOS:"Start of OS-specific",
    STB_HIOS:"End of OS-specific",
    STB_LOPROC:"Start of processor-specific",
    STB_HIPROC:"End of processor-specific",
}

STT_NOTYPE = 0
STT_OBJECT = 1
STT_FUNC = 2
STT_SECTION = 3
STT_FILE = 4
STT_COMMON = 5
STT_TLS = 6
STT_LOOS = 10
STT_MDOS = 11  # there's only one that isn't HI or LO...
STT_HIOS = 12
STT_LOPROC = 13
STT_MDPROC = 14
STT_HIPROC = 15

STT_GNU_IFUNC = 10

stt_lookup ={y: x for x, y in globals().items() if x.startswith("STT_")}

st_info_type = {
    STT_NOTYPE:"Symbol type is unspecified",
    STT_OBJECT:"Symbol is a data object",
    STT_FUNC:"Symbol is a code object",
    STT_SECTION:"Symbol associated with a section",
    STT_FILE:"Symbol's name is file name",
    STT_COMMON:"Symbol is a common data object",
    STT_TLS:"Symbol is thread-local data",
    STT_LOOS:"Start of OS-specific",
    STT_MDOS:"Middle of OS-specific",
    STT_HIOS:"End of OS-specific",
    STT_LOPROC:"Start of processor-specific",
    STT_MDPROC:"Middle of processor-specific",
    STT_HIPROC:"End of processor-specific",
}

STV_DEFAULT     = 0
STV_INTERNAL    = 1
STV_HIDDEN      = 2
STV_PROTECTED   = 3

stv_lookup ={y: x for x, y in globals().items() if x.startswith("STV_")}

st_other_visibility = {
    STV_DEFAULT:"Symbol visibility specified by binding type",
    STV_INTERNAL:"Symbol visibility is reserved",
    STV_HIDDEN:"Symbol is not visible to other objects",
    STV_PROTECTED:"Symbol is visible by other objects, but cannot be preempted"
}

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

DF_ORIGIN =         0x00000001        
DF_SYMBOLIC =       0x00000002        
DF_TEXTREL =        0x00000004        
DF_BIND_NOW =       0x00000008        
DF_STATIC_TLS =     0x00000010        

df_names = { v:k for k,v in globals().items() if k.startswith('DF_')}

df_types = {
    DF_ORIGIN: 'Object may use DF_ORIGIN',
    DF_SYMBOLIC: 'Symbol resolutions starts here',
    DF_TEXTREL: 'Object contains text relocations',
    DF_BIND_NOW: 'No lazy binding for this object',
    DF_STATIC_TLS: 'Module uses the static TLS model',
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

# GNU .note.ABI-tag
osnotes = {
    0:'linux',
    1:'gnu',
    2:'solaris',
    3:'freebsd',
}
