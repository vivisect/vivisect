
IMAGE_DLLCHARACTERISTICS_RESERVED_1      = 1
IMAGE_DLLCHARACTERISTICS_RESERVED_2      = 2
IMAGE_DLLCHARACTERISTICS_RESERVED_4      = 4
IMAGE_DLLCHARACTERISTICS_RESERVED_8      = 8
IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE    = 0x0040 # The DLL can be relocated at load time.
IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY = 0x0080 # Code integrity checks are forced. If you set this flag and a section contains only uninitialized data, set the PointerToRawData member of IMAGE_SECTION_HEADER for that section to zero; otherwise, the image will fail to load because the digital signature cannot be verified.
IMAGE_DLLCHARACTERISTICS_NX_COMPAT       = 0x0100 # The image is compatible with data execution prevention (DEP).
IMAGE_DLLCHARACTERISTICS_NO_ISOLATION    = 0x0200 # The image is isolation aware, but should not be isolated.
IMAGE_DLLCHARACTERISTICS_NO_SEH          = 0x0400 # The image does not use structured exception handling (SEH). No handlers can be called in this image.
IMAGE_DLLCHARACTERISTICS_NO_BIND         = 0x0800 # Do not bind the image.
IMAGE_DLLCHARACTERISTICS_RESERVED_1000   = 0x1000 # Reserved
IMAGE_DLLCHARACTERISTICS_WDM_DRIVER      = 0x2000 # A WDM driver.
IMAGE_DLLCHARACTERISTICS_RESERVED_4000   = 0x4000 # Reserved
IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE  = 0x8000

IMAGE_SUBSYSTEM_UNKNOWN                     = 0 #Unknown subsystem.
IMAGE_SUBSYSTEM_NATIVE                      = 1 #No subsystem required (device drivers and native system processes).
IMAGE_SUBSYSTEM_WINDOWS_GUI                 = 2 #Windows graphical user interface (GUI) subsystem.
IMAGE_SUBSYSTEM_WINDOWS_CUI                 = 3 #Windows character-mode user interface (CUI) subsystem.
IMAGE_SUBSYSTEM_OS2_CUI                     = 5 #OS/2 CUI subsystem.
IMAGE_SUBSYSTEM_POSIX_CUI                   = 7 #POSIX CUI subsystem.
IMAGE_SUBSYSTEM_WINDOWS_CE_GUI              = 9 #Windows CE system.
IMAGE_SUBSYSTEM_EFI_APPLICATION             = 10 #Extensible Firmware Interface (EFI) application.
IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER     = 11 #EFI driver with boot services.
IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER          = 12 #EFI driver with run-time services.
IMAGE_SUBSYSTEM_EFI_ROM                     = 13 #EFI ROM image.
IMAGE_SUBSYSTEM_XBOX                        = 14 #Xbox system.
IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION    = 16 #Boot application.

IMAGE_FILE_MACHINE_I386  = 0x014c
IMAGE_FILE_MACHINE_IA64  = 0x0200
IMAGE_FILE_MACHINE_AMD64 = 0x8664

machine_names = {
    IMAGE_FILE_MACHINE_I386: 'i386',
    IMAGE_FILE_MACHINE_IA64: 'ia64',
    IMAGE_FILE_MACHINE_AMD64: 'amd64',
}

IMAGE_REL_BASED_ABSOLUTE              = 0
IMAGE_REL_BASED_HIGH                  = 1
IMAGE_REL_BASED_LOW                   = 2
IMAGE_REL_BASED_HIGHLOW               = 3
IMAGE_REL_BASED_HIGHADJ               = 4
IMAGE_REL_BASED_MIPS_JMPADDR          = 5
IMAGE_REL_BASED_IA64_IMM64            = 9
IMAGE_REL_BASED_DIR64                 = 10
IMAGE_REL_BASED_HIGH3ADJ              = 11

IMAGE_DIRECTORY_ENTRY_EXPORT            = 0   # Export Directory
IMAGE_DIRECTORY_ENTRY_IMPORT            = 1   # Import Directory
IMAGE_DIRECTORY_ENTRY_RESOURCE          = 2   # Resource Directory
IMAGE_DIRECTORY_ENTRY_EXCEPTION         = 3   # Exception Directory
IMAGE_DIRECTORY_ENTRY_SECURITY          = 4   # Security Directory
IMAGE_DIRECTORY_ENTRY_BASERELOC         = 5   # Base Relocation Table
IMAGE_DIRECTORY_ENTRY_DEBUG             = 6   # Debug Directory
IMAGE_DIRECTORY_ENTRY_COPYRIGHT         = 7   # (X86 usage)
IMAGE_DIRECTORY_ENTRY_ARCHITECTURE      = 7   # Architecture Specific Data
IMAGE_DIRECTORY_ENTRY_GLOBALPTR         = 8   # RVA of GP
IMAGE_DIRECTORY_ENTRY_TLS               = 9   # TLS Directory
IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG       = 10  # Load Configuration Directory
IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT      = 11  # Bound Import Directory in headers
IMAGE_DIRECTORY_ENTRY_IAT               = 12  # Import Address Table
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT      = 13  # Delay Load Import Descriptors
IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR    = 14  # COM Runtime descriptor

IMAGE_DEBUG_TYPE_UNKNOWN          = 0
IMAGE_DEBUG_TYPE_COFF             = 1
IMAGE_DEBUG_TYPE_CODEVIEW         = 2
IMAGE_DEBUG_TYPE_FPO              = 3
IMAGE_DEBUG_TYPE_MISC             = 4
IMAGE_DEBUG_TYPE_EXCEPTION        = 5
IMAGE_DEBUG_TYPE_FIXUP            = 6
IMAGE_DEBUG_TYPE_OMAP_TO_SRC      = 7
IMAGE_DEBUG_TYPE_OMAP_FROM_SRC    = 8
IMAGE_DEBUG_TYPE_BORLAND          = 9
IMAGE_DEBUG_TYPE_RESERVED10       = 10
IMAGE_DEBUG_TYPE_CLSID            = 11

IMAGE_SCN_CNT_CODE                  = 0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA      = 0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA    = 0x00000080
IMAGE_SCN_LNK_OTHER                 = 0x00000100
IMAGE_SCN_LNK_INFO                  = 0x00000200
IMAGE_SCN_LNK_REMOVE                = 0x00000800
IMAGE_SCN_LNK_COMDAT                = 0x00001000
IMAGE_SCN_MEM_FARDATA               = 0x00008000
IMAGE_SCN_MEM_PURGEABLE             = 0x00020000
IMAGE_SCN_MEM_16BIT                 = 0x00020000
IMAGE_SCN_MEM_LOCKED                = 0x00040000
IMAGE_SCN_MEM_PRELOAD               = 0x00080000
IMAGE_SCN_ALIGN_1BYTES              = 0x00100000
IMAGE_SCN_ALIGN_2BYTES              = 0x00200000
IMAGE_SCN_ALIGN_4BYTES              = 0x00300000
IMAGE_SCN_ALIGN_8BYTES              = 0x00400000
IMAGE_SCN_ALIGN_16BYTES             = 0x00500000
IMAGE_SCN_ALIGN_32BYTES             = 0x00600000
IMAGE_SCN_ALIGN_64BYTES             = 0x00700000
IMAGE_SCN_ALIGN_128BYTES            = 0x00800000
IMAGE_SCN_ALIGN_256BYTES            = 0x00900000
IMAGE_SCN_ALIGN_512BYTES            = 0x00A00000
IMAGE_SCN_ALIGN_1024BYTES           = 0x00B00000
IMAGE_SCN_ALIGN_2048BYTES           = 0x00C00000
IMAGE_SCN_ALIGN_4096BYTES           = 0x00D00000
IMAGE_SCN_ALIGN_8192BYTES           = 0x00E00000
IMAGE_SCN_ALIGN_MASK                = 0x00F00000
IMAGE_SCN_LNK_NRELOC_OVFL           = 0x01000000
IMAGE_SCN_MEM_DISCARDABLE           = 0x02000000
IMAGE_SCN_MEM_NOT_CACHED            = 0x04000000
IMAGE_SCN_MEM_NOT_PAGED             = 0x08000000
IMAGE_SCN_MEM_SHARED                = 0x10000000
IMAGE_SCN_MEM_EXECUTE               = 0x20000000
IMAGE_SCN_MEM_READ                  = 0x40000000
IMAGE_SCN_MEM_WRITE                 = 0x80000000

# Flags for the UNWIND_INFO flags field from
# RUNTIME_FUNCTION defs
UNW_FLAG_NHANDLER   = 0x0
UNW_FLAG_EHANDLER   = 0x1
UNW_FLAG_UHANDLER   = 0x2
UNW_FLAG_CHAININFO  = 0x4

# Resource Types
RT_CURSOR           = 1
RT_BITMAP           = 2
RT_ICON             = 3
RT_MENU             = 4
RT_DIALOG           = 5
RT_STRING           = 6
RT_FONTDIR          = 7
RT_FONT             = 8
RT_ACCELERATOR      = 9
RT_RCDATA           = 10
RT_MESSAGETABLE     = 11
RT_GROUP_CURSOR     = 12
RT_GROUP_ICON       = 14
RT_VERSION          = 16
RT_DLGINCLUDE       = 17
RT_PLUGPLAY         = 19
RT_VXD              = 20
RT_ANICURSOR        = 21
RT_ANIICON          = 22
RT_HTML             = 23
RT_MANIFEST         = 24

