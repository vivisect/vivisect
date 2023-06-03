
# Fat Defines...
FAT_MAGIC = 0xcafebabe
FAT_CIGAM = 0xbebafeca   # NXSwapLong(FAT_MAGIC)
FAT_MAGIC_64 = 0xcafebabf
FAT_CIGAM_64 = 0xbfbafeca

FAT_DEFINES = (FAT_MAGIC, FAT_CIGAM, FAT_MAGIC_64, FAT_CIGAM_64)
FAT_64 = (FAT_MAGIC_64, FAT_CIGAM_64)

MH_MAGIC                  = 0xfeedface #  the mach magic number 
MH_CIGAM                  = 0xcefaedfe #  NXSwapInt(MH_MAGIC) 
MH_MAGIC_64               = 0xfeedfacf #  the 64-bit mach magic number 
MH_CIGAM_64               = 0xcffaedfe #  NXSwapInt(MH_MAGIC_64) 
MH_OBJECT                 = 0x1 #  relocatable object file 
MH_EXECUTE                = 0x2 #  demand paged executable file 
MH_FVMLIB                 = 0x3 #  fixed VM shared library file 
MH_CORE                   = 0x4 #  core file 
MH_PRELOAD                = 0x5 #  preloaded executable file 
MH_DYLIB                  = 0x6 #  dynamically bound shared library 
MH_DYLINKER               = 0x7 #  dynamic link editor 
MH_BUNDLE                 = 0x8 #  dynamically bound bundle file 
MH_DYLIB_STUB             = 0x9 #  shared library stub for static 
MH_DSYM                   = 0xa #  companion file with only debug 
MH_NOUNDEFS               = 0x1 #  the object file has no undefinedreferences 
MH_INCRLINK               = 0x2 #  the object file is the output of anincremental link against a base fileand can't be link edited again 
MH_DYLDLINK               = 0x4 #  the object file is input for thedynamic linker and can't be staticlylink edited again 
MH_BINDATLOAD             = 0x8 #  the object file's undefinedreferences are bound by the dynamic linker when loaded. 
MH_PREBOUND               = 0x10 #  the file has its dynamic undefinedreferences prebound. 
MH_SPLIT_SEGS             = 0x20 #  the file has its read-only andread-write segments split 
MH_LAZY_INIT              = 0x40 #  the shared library init routine isto be run lazily via catching memoryfaults to its writeable segments(obsolete) 
MH_TWOLEVEL               = 0x80 #  the image is using two-level namespace bindings 
MH_FORCE_FLAT             = 0x100 #  the executable is forcing all imagesto use flat name space bindings 
MH_NOMULTIDEFS            = 0x200 #  this umbrella guarantees no multipledefintions of symbols in itssub-images so the two-level namespacehints can always be used. 
MH_NOFIXPREBINDING        = 0x400 #  do not have dyld notify theprebinding agent about thisexecutable 
MH_PREBINDABLE            = 0x800 #  the binary is not prebound but canhave its prebinding redone. only usedwhen MH_PREBOUND is not set. 
MH_ALLMODSBOUND           = 0x1000 #  this binary binds toall two-level namespace modules ofits dependent libraries. only usedwhen MH_PREBINDABLE and MH_TWOLEVELare both set. 
MH_CANONICAL              = 0x4000 #  the binary has been canonicalizedvia the unprebind operation 
MH_WEAK_DEFINES           = 0x8000 #  the final linked image containsexternal weak symbols 
MH_BINDS_TO_WEAK          = 0x10000 #  the final linked image usesweak symbols 
MH_ROOT_SAFE              = 0x40000 #  When this bit is set, the binarydeclares it is safe for use inprocesses with uid zero 
MH_SETUID_SAFE            = 0x80000 #  When this bit is set, the binarydeclares it is safe for use inprocesses when issetugid() is true 
MH_NO_REEXPORTED_DYLIBS   = 0x100000 #  When this bit is set on a dylib,the static linker does not need toexamine dependent dylibs to seeif any are re-exported 
MH_PIE                    = 0x200000 #  When this bit is set, the OS willload the main executable at arandom address. Only used inMH_EXECUTE filetypes. 

# Constants for the cmd field of all load commands, the type
LC_REQ_DYLD               = 0x80000000 #  When this bit is set, the OS will load the main executable at a random address. Only used in MH_EXECUTE filetypes. 
LC_SEGMENT                = 0x1 #  segment of this file to be mapped 
LC_SYMTAB                 = 0x2 #  link-edit stab symbol table info 
LC_SYMSEG                 = 0x3 #  link-edit gdb symbol table info (obsolete) 
LC_THREAD                 = 0x4 #  thread 
LC_UNIXTHREAD             = 0x5 #  unix thread (includes a stack) 
LC_LOADFVMLIB             = 0x6 #  load a specified fixed VM shared library 
LC_IDFVMLIB               = 0x7 #  fixed VM shared library identification 
LC_IDENT                  = 0x8 #  object identification info (obsolete) 
LC_FVMFILE                = 0x9 #  fixed VM file inclusion (internal use) 
LC_PREPAGE                = 0xa #  prepage command (internal use) 
LC_DYSYMTAB               = 0xb #  dynamic link-edit symbol table info 
LC_LOAD_DYLIB             = 0xc #  load a dynamically linked shared library 
LC_ID_DYLIB               = 0xd #  dynamically linked shared lib ident 
LC_LOAD_DYLINKER          = 0xe #  load a dynamic linker 
LC_ID_DYLINKER            = 0xf #  dynamic linker identification 
LC_PREBOUND_DYLIB         = 0x10 #  modules prebound for a dynamically linked shared library
LC_ROUTINES               = 0x11 #  image routines 
LC_SUB_FRAMEWORK          = 0x12 #  sub framework 
LC_SUB_UMBRELLA           = 0x13 #  sub umbrella 
LC_SUB_CLIENT             = 0x14 #  sub client 
LC_SUB_LIBRARY            = 0x15 #  sub library 
LC_TWOLEVEL_HINTS         = 0x16 #  two-level namespace lookup hints 
LC_PREBIND_CKSUM          = 0x17 #  prebind checksum 
LC_LOAD_WEAK_DYLIB        = (0x18 | LC_REQ_DYLD)  # load a dynamically linked shared library that is allowed to be missing (all symbols are weak imported).
LC_SEGMENT_64             = 0x19 #  64-bit segment of this file to bemapped 
LC_ROUTINES_64            = 0x1a #  64-bit image routines 
LC_UUID                   = 0x1b #  the uuid 
LC_RPATH                  = (0x1c | LC_REQ_DYLD)  # runpath additions
LC_CODE_SIGNATURE         = 0x1d #  local of code signature 
LC_SEGMENT_SPLIT_INFO     = 0x1e #  local of info to split segments 
LC_REEXPORT_DYLIB         = (0x1f | LC_REQ_DYLD)  # load and re-export dylib
LC_LAZY_LOAD_DYLIB        = 0x20 #  delay load of dylib until first use 
LC_ENCRYPTION_INFO        = 0x21 #  encrypted segment information 
LC_DYLD_INFO              = 0x22 #  compressed dyld information
LC_DYLD_INFO_ONLY         = (0x22 | LC_REQ_DYLD)  # compressed dyld information only
LC_LOAD_UPWARD_DYLIB      = (0x23 | LC_REQ_DYLD)  # load upward dylib
LC_VERSION_MIN_MACOSX     = 0x24  # build for MacOSX min OS version
LC_VERSION_MIN_IPHONEOS   = 0x25  # build for iPhoneOS min OS version
LC_FUNCTION_STARTS        = 0x26  # compressed table of function start addresses
LC_DYLD_ENVIRONMENT       = 0x27  # string for dyld to treat like environment variable
LC_MAIN                   = (0x28 | LC_REQ_DYLD)  # replacement for LC_UNIXTHREAD
LC_DATA_IN_CODE           = 0x29  # table of non-instructions in __text
LC_SOURCE_VERSION         = 0x2A  # source version used to build binary
LC_DYLIB_CODE_SIGN_DRS    = 0x2B  # Code signing DRs copied from linked dylibs

SG_HIGHVM                 = 0x1 #  the file contents for this segment is for the high part of the VM space, the low part is zero filled (for stacks in core files) 
SG_FVMLIB                 = 0x2 #  this segment is the VM that is allocated by a fixed VM library, for overlap checking in the link editor 
SG_NORELOC                = 0x4 #  this segment has nothing that was relocated in it and nothing relocated to it, that is it maybe safely replaced without relocation
SG_PROTECTED_VERSION_1    = 0x8 #  This segment is protected. If the segment starts at file offset 0, the first page of the segment is not protected. All other pages of the segment are protected. 


SECTION_TYPE              = 0x000000ff #  256 section types 
SECTION_ATTRIBUTES        = 0xffffff00 #  24 section attributes 
S_REGULAR                 = 0x0 #  regular section 
S_ZEROFILL                = 0x1 #  zero fill on demand section 
S_CSTRING_LITERALS        = 0x2 #  section with only literal C strings
S_4BYTE_LITERALS          = 0x3 #  section with only 4 byte literals 
S_8BYTE_LITERALS          = 0x4 #  section with only 8 byte literals 
S_LITERAL_POINTERS        = 0x5 #  section with only pointers to literals
S_NON_LAZY_SYMBOL_POINTERS = 0x6 #  section with only non-lazy symbol pointers 
S_LAZY_SYMBOL_POINTERS    = 0x7 #  section with only lazy symbol pointers 
S_SYMBOL_STUBS            = 0x8 #  section with only symbol stubs, byte size of stub in the reserved2 field 
S_MOD_INIT_FUNC_POINTERS  = 0x9 #  section with only function pointers for initialization
S_MOD_TERM_FUNC_POINTERS  = 0xa #  section with only function pointers for termination 
S_COALESCED               = 0xb #  section contains symbols that are to be coalesced 
S_GB_ZEROFILL             = 0xc #  zero fill on demand section (that can be larger than 4gigabytes) 
S_INTERPOSING             = 0xd #  section with only pairs offunction pointers for interposing 
S_16BYTE_LITERALS         = 0xe #  section with only 16 byte literals 
S_DTRACE_DOF              = 0xf #  section contains DTrace Object Format 
S_LAZY_DYLIB_SYMBOL_POINTERS = 0x10 #  section with only lazysymbol pointers to lazyloaded dylibs 
SECTION_ATTRIBUTES_USR    = 0xff000000 #  User setable attributes 
S_ATTR_PURE_INSTRUCTIONS  = 0x80000000 #  section contains only true machine instructions 
S_ATTR_NO_TOC             = 0x40000000 #  section contains coalesced symbols that are not to bein a ranlib table of contents 
S_ATTR_STRIP_STATIC_SYMS  = 0x20000000 #  ok to strip static symbolsin this section in files with the MH_DYLDLINK flag 
S_ATTR_NO_DEAD_STRIP      = 0x10000000 #  no dead stripping 
S_ATTR_LIVE_SUPPORT       = 0x08000000 #  blocks are live if they reference live blocks 
S_ATTR_SELF_MODIFYING_CODE = 0x04000000 #  Used with i386 code stubs written on by dyld 
S_ATTR_DEBUG              = 0x02000000 #  a debug section 
SECTION_ATTRIBUTES_SYS    = 0x00ffff00 #  system setable attributes 
S_ATTR_SOME_INSTRUCTIONS  = 0x00000400 #  section contains some machine instructions 
S_ATTR_EXT_RELOC          = 0x00000200 #  section has external relocation entries 
S_ATTR_LOC_RELOC          = 0x00000100 #  section has local relocation entries 
INDIRECT_SYMBOL_LOCAL     = 0x80000000 #  section has local relocation entries 
INDIRECT_SYMBOL_ABS       = 0x40000000 #  section has local relocation entries 

CPU_ARCH_MASK = 0xff000000
CPU_ARCH_ABI64 = 0x01000000
CPU_ARCH_ABI64_32 = 0x02000000

CPU_TYPE_ANY        = -1
CPU_TYPE_VAX        = 1
CPU_TYPE_MC680      = 6
CPU_TYPE_X86        = 7
CPU_TYPE_X86_64     = CPU_TYPE_X86 | CPU_ARCH_ABI64
CPU_TYPE_MIPS       = 8
CPU_TYPE_MC98000    = 10
CPU_TYPE_HPPA       = 11
CPU_TYPE_ARM        = 12
CPU_TYPE_ARM64      = CPU_TYPE_ARM | CPU_ARCH_ABI64
CPU_TYPE_ARM64_32   = CPU_TYPE_ARM | CPU_ARCH_ABI64_32
CPU_TYPE_MC88000    = 13
CPU_TYPE_SPARC      = 14
CPU_TYPE_I860       = 15
CPU_TYPE_ALPHA      = 16
CPU_TYPE_POWERPC    = 18
CPU_TYPE_POWERPC64  = CPU_TYPE_POWERPC | CPU_ARCH_ABI64

mach_cpu_names = {
    CPU_TYPE_VAX        : 'vax',
    CPU_TYPE_MC680      : 'mc680',
    CPU_TYPE_X86        : 'i386',
    CPU_TYPE_X86_64     : 'amd64',
    CPU_TYPE_MIPS       : 'mips',
    CPU_TYPE_MC98000    : 'mc98000',
    CPU_TYPE_HPPA       : 'hppa',
    CPU_TYPE_ARM        : 'arm',
    CPU_TYPE_ARM64      : 'arm64',
    CPU_TYPE_ARM64_32   : 'arm64_32',
    CPU_TYPE_MC88000    : 'mc88000',
    CPU_TYPE_SPARC      : 'sparc',
    CPU_TYPE_I860       : 'i860',
    CPU_TYPE_ALPHA      : 'alpha',
    CPU_TYPE_POWERPC    : 'powerpc',
    CPU_TYPE_POWERPC64  : 'powerpc64',
}

# Symbol types
N_GSYM      = 0x20      # global symbol:                name,,NO_SECT,type,0
N_FNAME     = 0x22      # procedure name (f77 kludge):  name,,NO_SECT,0,0
N_FUN       = 0x24      # procedure:                    name,,n_sect,linenumber,address
N_STSYM     = 0x26      # static symbol:                name,,n_sect,type,address
N_LCSYM     = 0x28      # .lcomm symbol:                name,,n_sect,type,address
N_BNSYM     = 0x2e      # begin nsect sym:              0,,n_sect,0,address
N_PC        = 0x30      # global pascal symbol:         name,,NO_SECT,subtype,line
N_OPT       = 0x3c      # emitted with gcc2_compile and in gcc source
N_RSYM      = 0x40      # register sym:                 name,,NO_SECT,type,register
N_SLINE     = 0x44      # src line:                     0,,n_sect,linenumber,address
N_ENSYM     = 0x4e      # end nsect sym:                0,,n_sect,0,address
N_SSYM      = 0x60      # struct elt:                   name,,NO_SECT,type,struct_offset
N_SO        = 0x64      # source file name:             name,,n_sect,0,address
N_LSYM      = 0x80      # local sym:                    name,,NO_SECT,type,offset
N_BINCL     = 0x82      # include file beginning:       name,,NO_SECT,0,sum
N_SOL       = 0x84      # #included file name:          name,,n_sect,0,address
N_PARAMS    = 0x86      # compiler parameters:          name,,NO_SECT,0,0
N_VERSION   = 0x88      # compiler version:             name,,NO_SECT,0,0
N_OLEVEL    = 0x8A      # compiler -O level:            name,,NO_SECT,0,0
N_PSYM      = 0xA0      # parameter:                    name,,NO_SECT,type,offset
N_EINCL     = 0xA2      # include file end:             name,,NO_SECT,0,0
N_ENTRY     = 0xA4      # alternate entry:              name,,n_sect,linenumber,address
N_LBRAC     = 0xC0      # left bracket:                 0,,NO_SECT,nesting level,address
N_EXCL      = 0xC2      # deleted include file:         name,,NO_SECT,0,sum
N_RBRAC     = 0xE0      # right bracket:                0,,NO_SECT,nesting level,address
N_BCOMM     = 0xE2      # begin common:                 name,,NO_SECT,0,0
N_ECOMM     = 0xE4      # end common:                   name,,n_sect,0,0
N_ECOML     = 0xE8      # end common (local name):      0,,n_sect,0,address
N_LENG      = 0xFE      # second stab entry with length information

# The n_type field really contains four fields:
#	unsigned char N_STAB:3,
#		      N_PEXT:1,
#		      N_TYPE:3,
#		      N_EXT:1;

N_STAB  = 0xe0  # if any of these bits set, a symbolic debugging entry
N_PEXT  = 0x10  # private external symbol bit
N_TYPE  = 0x0e  # mask for the type bits
N_EXT   = 0x01  # external symbol bit, set for external symbols

# Values for N_TYPE bits of the n_type field.
N_UNDF   = 0x0 # undefined, n_sect == NO_SECT
N_ABS    = 0x2 # absolute, n_sect == NO_SECT
N_SECT   = 0xe # defined in section number n_sect
N_PBUD   = 0xc # prebound undefined (defined in a dylib)
N_INDR   = 0xa # indirect

ENDIAN_LSB = 0
ENDIAN_MSB = 1



DICE_KIND_DATA              = 0x0001  # L$start$data$...  label
DICE_KIND_JUMP_TABLE8       = 0x0002  # L$start$jt8$...   label
DICE_KIND_JUMP_TABLE16      = 0x0003  # L$start$jt16$...  label
DICE_KIND_JUMP_TABLE32      = 0x0004  # L$start$jt32$...  label
DICE_KIND_ABS_JUMP_TABLE32  = 0x0005  # L$start$jta32$... label

CSMAGIC_REQUIREMENT = 0xfade0c00  # single Requirement blob
CSMAGIC_REQUIREMENTS = 0xfade0c01 # Requirements vector (internal requirements)
CSMAGIC_CODEDIRECTORY = 0xfade0c02      # CodeDirectory blob
CSMAGIC_EMBEDDED_SIGNATURE = 0xfade0cc0 # embedded form of signature data
CSMAGIC_EMBEDDED_SIGNATURE_OLD = 0xfade0b02 # XXX */
CSMAGIC_EMBEDDED_ENTITLEMENTS = 0xfade7171  # embedded entitlements
CSMAGIC_DETACHED_SIGNATURE = 0xfade0cc1 # multi-arch collection of embedded signatures
CSMAGIC_BLOBWRAPPER = 0xfade0b01 # CMS Signature, among other things

CS_SUPPORTSSCATTER = 0x20100
CS_SUPPORTSTEAMID = 0x20200
CS_SUPPORTSCODELIMIT64 = 0x20300
CS_SUPPORTSEXECSEG = 0x20400
CS_SUPPORTSRUNTIME = 0x20500
CS_SUPPORTSLINKAGE = 0x20600

CSSLOT_CODEDIRECTORY = 0 # slot index for CodeDirectory
CSSLOT_INFOSLOT = 1
CSSLOT_REQUIREMENTS = 2
CSSLOT_RESOURCEDIR = 3
CSSLOT_APPLICATION = 4
CSSLOT_ENTITLEMENTS = 5
CSSLOT_REP_SPECIFIC = 6
CSSLOT_ENTITLEMENTS_DER = 7

CSSLOT_ALTERNATE_CODEDIRECTORIES =  0x1000
CSSLOT_ALTERNATE_CODEDIRECTORIES_MAX = 5

CSSLOT_CMS_SIGNATURE = 0x10000
CSSLOT_IDENTIFICATIONSLOT = 0x10001
CSSLOT_TICKETSLOT = 0x10002

CSSLOT_ALTERNATE_CODEDIRECTORIES = 0x1000 # first alternate CodeDirectory, if any
CSSLOT_ALTERNATE_CODEDIRECTORY_MAX = 5 # max number of alternate CD slots
CSSLOT_ALTERNATE_CODEDIRECTORY_LIMIT = CSSLOT_ALTERNATE_CODEDIRECTORIES + CSSLOT_ALTERNATE_CODEDIRECTORY_MAX # one past the last

CSSLOT_SIGNATURESLOT = 0x10000 # CMS Signature
CSSLOT_IDENTIFICATIONSLOT = 0x10001
CSSLOT_TICKETSLOT = 0x10002

CSTYPE_INDEX_REQUIREMENTS = 0x00000002 # compat with amf
CSTYPE_INDEX_ENTITLEMENTS = 0x00000005 # compat with amfi

CS_HASHTYPE_SHA1 = 1
CS_HASHTYPE_SHA256 = 2
CS_HASHTYPE_SHA256_TRUNCATED = 3
CS_HASHTYPE_SHA384 = 4
CS_HASHTYPE_SHA512 = 5

CS_SHA1_LEN = 20
CS_SHA256_LEN = 32
CS_SHA256_TRUNCATED_LEN = 20

CS_CDHASH_LEN = 20    # always - larger hashes are truncated
CS_HASH_MAX_SIZE = 48 # max size of the hash we'll support

# From LLVM:
# Currently only to support Legacy VPN plugins, and Mac App Store
# but intended to replace all the various platform code, dev code etc. bits.
CS_SIGNER_TYPE_UNKNOWN = 0
CS_SIGNER_TYPE_LEGACYVPN = 5
CS_SIGNER_TYPE_MAC_APP_STORE = 6

CS_SUPPL_SIGNER_TYPE_UNKNOWN = 0
CS_SUPPL_SIGNER_TYPE_TRUSTCACHE = 7
CS_SUPPL_SIGNER_TYPE_LOCAL = 8
