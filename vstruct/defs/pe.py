
import vstruct
from vstruct.primitives import *

class IMAGE_BASE_RELOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_uint32()
        self.SizeOfBlock    = v_uint32()

class IMAGE_DATA_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_uint32()
        self.Size           = v_uint32()

class IMAGE_DOS_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.e_magic    = v_uint16()
        self.e_cblp     = v_uint16()
        self.e_cp       = v_uint16()
        self.e_crlc     = v_uint16()
        self.e_cparhdr  = v_uint16()
        self.e_minalloc = v_uint16()
        self.e_maxalloc = v_uint16()
        self.e_ss       = v_uint16()
        self.e_sp       = v_uint16()
        self.e_csum     = v_uint16()
        self.e_ip       = v_uint16()
        self.e_cs       = v_uint16()
        self.e_lfarlc   = v_uint16()
        self.e_ovno     = v_uint16()
        self.e_res      = vstruct.VArray([v_uint16() for i in range(4)])
        self.e_oemid    = v_uint16()
        self.e_oeminfo  = v_uint16()
        self.e_res2     = vstruct.VArray([v_uint16() for i in range(10)])
        self.e_lfanew   = v_uint32()

class IMAGE_EXPORT_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Characteristics    = v_uint32()
        self.TimeDateStamp      = v_uint32()
        self.MajorVersion       = v_uint16()
        self.MinorVersion       = v_uint16()
        self.Name               = v_uint32()
        self.Base               = v_uint32()
        self.NumberOfFunctions  = v_uint32()
        self.NumberOfNames      = v_uint32()
        self.AddressOfFunctions = v_uint32()
        self.AddressOfNames     = v_uint32()
        self.AddressOfOrdinals  = v_uint32()

class IMAGE_DEBUG_DIRECTORY(vstruct.VStruct):
    def __init__(self):
      vstruct.VStruct.__init__(self)
      self.Characteristics = v_uint32()
      self.TimeDateStamp   = v_uint32()
      self.MajorVersion    = v_uint16()
      self.MinorVersion    = v_uint16()
      self.Type            = v_uint32()
      self.SizeOfData      = v_uint32()
      self.AddressOfRawData= v_uint32()
      self.PointerToRawData= v_uint32()

class CV_INFO_PDB70(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CvSignature    = v_uint32()
        self.Signature      = GUID()
        self.Age            = v_uint32()
        self.PdbFileName    = v_str(260)

    def vsParse(self, bytez, offset=0):
        bsize = len(bytez) - offset
        self.vsGetField('PdbFileName').vsSetLength( bsize - 24 )
        return vstruct.VStruct.vsParse(self, bytez, offset=offset)

class IMAGE_FILE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Machine              = v_uint16()
        self.NumberOfSections     = v_uint16()
        self.TimeDateStamp        = v_uint32()
        self.PointerToSymbolTable = v_uint32()
        self.NumberOfSymbols      = v_uint32()
        self.SizeOfOptionalHeader = v_uint16()
        self.Characteristics      = v_uint16()

class IMAGE_IMPORT_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OriginalFirstThunk = v_uint32()
        self.TimeDateStamp      = v_uint32()
        self.ForwarderChain     = v_uint32()
        self.Name               = v_uint32()
        self.FirstThunk         = v_uint32()

class IMAGE_IMPORT_BY_NAME(vstruct.VStruct):
    def __init__(self, namelen=128):
        vstruct.VStruct.__init__(self)
        self.Hint   = v_uint16()
        self.Name   = v_str(size=namelen)

class IMAGE_LOAD_CONFIG_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size                          = v_uint32()
        self.TimeDateStamp                 = v_uint32()
        self.MajorVersion                  = v_uint16()
        self.MinorVersion                  = v_uint16()
        self.GlobalFlagsClear              = v_uint32()
        self.GlobalFlagsSet                = v_uint32()
        self.CriticalSectionDefaultTimeout = v_uint32()
        self.DeCommitFreeBlockThreshold    = v_uint32()
        self.DeCommitTotalFreeThreshold    = v_uint32()
        self.LockPrefixTable               = v_uint32()
        self.MaximumAllocationSize         = v_uint32()
        self.VirtualMemoryThreshold        = v_uint32()
        self.ProcessHeapFlags              = v_uint32()
        self.ProcessAffinityMask           = v_uint32()
        self.CSDVersion                    = v_uint16()
        self.Reserved1                     = v_uint16()
        self.EditList                      = v_uint32()
        self.SecurityCookie                = v_uint32()
        self.SEHandlerTable                = v_uint32()
        self.SEHandlerCount                = v_uint32()

class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature      = v_bytes(4)
        self.FileHeader     = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()

class IMAGE_NT_HEADERS64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature      = v_bytes(4)
        self.FileHeader     = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER64()

class IMAGE_OPTIONAL_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic                       = v_bytes(2)
        self.MajorLinkerVersion          = v_uint8()
        self.MinorLinkerVersion          = v_uint8()
        self.SizeOfCode                  = v_uint32()
        self.SizeOfInitializedData       = v_uint32()
        self.SizeOfUninitializedData     = v_uint32()
        self.AddressOfEntryPoint         = v_uint32()
        self.BaseOfCode                  = v_uint32()
        self.BaseOfData                  = v_uint32()
        self.ImageBase                   = v_uint32()
        self.SectionAlignment            = v_uint32()
        self.FileAlignment               = v_uint32()
        self.MajorOperatingSystemVersion = v_uint16()
        self.MinorOperatingSystemVersion = v_uint16()
        self.MajorImageVersion           = v_uint16()
        self.MinorImageVersion           = v_uint16()
        self.MajorSubsystemVersion       = v_uint16()
        self.MinorSubsystemVersion       = v_uint16()
        self.Win32VersionValue           = v_uint32()
        self.SizeOfImage                 = v_uint32()
        self.SizeOfHeaders               = v_uint32()
        self.CheckSum                    = v_uint32()
        self.Subsystem                   = v_uint16()
        self.DllCharacteristics          = v_uint16()
        self.SizeOfStackReserve          = v_uint32()
        self.SizeOfStackCommit           = v_uint32()
        self.SizeOfHeapReserve           = v_uint32()
        self.SizeOfHeapCommit            = v_uint32()
        self.LoaderFlags                 = v_uint32()
        self.NumberOfRvaAndSizes         = v_uint32()
        self.DataDirectory               = vstruct.VArray([IMAGE_DATA_DIRECTORY() for i in range(16)])

class IMAGE_OPTIONAL_HEADER64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic                       = v_bytes(2)
        self.MajorLinkerVersion          = v_uint8()
        self.MinorLinkerVersion          = v_uint8()
        self.SizeOfCode                  = v_uint32()
        self.SizeOfInitializedData       = v_uint32()
        self.SizeOfUninitializedData     = v_uint32()
        self.AddressOfEntryPoint         = v_uint32()
        self.BaseOfCode                  = v_uint32()
        self.ImageBase                   = v_uint64()
        self.SectionAlignment            = v_uint32()
        self.FileAlignment               = v_uint32()
        self.MajorOperatingSystemVersion = v_uint16()
        self.MinorOperatingSystemVersion = v_uint16()
        self.MajorImageVersion           = v_uint16()
        self.MinorImageVersion           = v_uint16()
        self.MajorSubsystemVersion       = v_uint16()
        self.MinorSubsystemVersion       = v_uint16()
        self.Win32VersionValue           = v_uint32()
        self.SizeOfImage                 = v_uint32()
        self.SizeOfHeaders               = v_uint32()
        self.CheckSum                    = v_uint32()
        self.Subsystem                   = v_uint16()
        self.DllCharacteristics          = v_uint16()
        self.SizeOfStackReserve          = v_uint64()
        self.SizeOfStackCommit           = v_uint64()
        self.SizeOfHeapReserve           = v_uint64()
        self.SizeOfHeapCommit            = v_uint64()
        self.LoaderFlags                 = v_uint32()
        self.NumberOfRvaAndSizes         = v_uint32()
        self.DataDirectory               = vstruct.VArray([IMAGE_DATA_DIRECTORY() for i in range(16)])

class IMAGE_RESOURCE_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Characteristics      = v_uint32()
        self.TimeDateStamp        = v_uint32()
        self.MajorVersion         = v_uint16()
        self.MinorVersion         = v_uint16()
        self.NumberOfNamedEntries = v_uint16()
        self.NumberOfIdEntries    = v_uint16()

class IMAGE_RESOURCE_DIRECTORY_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name           = v_uint32()
        self.OffsetToData   = v_uint32()

class IMAGE_RESOURCE_DATA_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OffsetToData   = v_uint32()
        self.Size           = v_uint32()
        self.CodePage       = v_uint32()
        self.Reserved       = v_uint32()

class VS_FIXEDFILEINFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature          = v_uint32()
        self.StrucVersion       = v_uint32()
        self.FileVersionMS      = v_uint32()
        self.FileVersionLS      = v_uint32()
        self.ProductVersionMS   = v_uint32()
        self.ProductVersionLS   = v_uint32()
        self.FileFlagsMask      = v_uint32()
        self.FileFlags          = v_uint32()
        self.FileOS             = v_uint32()
        self.FileType           = v_uint32()
        self.FileSubtype        = v_uint32()
        self.FileDateMS         = v_uint32()
        self.FileDateLS         = v_uint32()

class IMAGE_SECTION_HEADER(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name                 = v_str(8)
        self.VirtualSize          = v_uint32()
        self.VirtualAddress       = v_uint32()
        self.SizeOfRawData        = v_uint32()
        self.PointerToRawData     = v_uint32()
        self.PointerToRelocations = v_uint32()
        self.PointerToLineNumbers = v_uint32()
        self.NumberOfRelocations  = v_uint16()
        self.NumberOfLineNumbers  = v_uint16()
        self.Characteristics      = v_uint32()


class IMAGE_RUNTIME_FUNCTION_ENTRY(vstruct.VStruct):
    """
    Used in the .pdata section of a PE32+ for all non
    leaf functions.
    """
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BeginAddress = v_uint32()
        self.EndAddress = v_uint32()
        self.UnwindInfoAddress = v_uint32()

class UNWIND_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VerFlags       = v_uint8()
        self.SizeOfProlog   = v_uint8()
        self.CountOfCodes   = v_uint8()
        self.FrameRegister  = v_uint8()

class SignatureEntry(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.size = v_int32(bigend=False)

        # should always be 0x00020200
        self.magic = v_bytes(size=4)

        self.pkcs7 = v_bytes()

    def pcb_size(self):
        size = self.size
        self.vsGetField('pkcs7').vsSetLength(size)


# https://github.com/dotnet/coreclr/blob/master/src/inc/corhdr.h#L208
# Pointed to by one of the data directory entries in the PE header
class IMAGE_COR20_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HeaderSize = v_uint32()
        self.MajorRuntimeVersion = v_uint16()
        self.MinorRuntimeVersion = v_uint16()

        self.Metadata = IMAGE_DATA_DIRECTORY()

        self.Flags = v_uint32()

        # If COMIMAGE_FLAGS_NATIVE_ENTRYPOINT is not set, EntryPointToken represents a managed entrypoint.
        # If COMIMAGE_FLAGS_NATIVE_ENTRYPOINT is set, EntryPointRVA represents an RVA to a native entrypoint
        self.EntryPoint = v_uint32()

        # This is the blob of managed resources. Fetched using code:AssemblyNative.GetResource and
        # code:PEFile.GetResource and accessible from managed code from
        # System.Assembly.GetManifestResourceStream.  The meta data has a table that maps names to 
        # offsets into this blob, so logically the blob is a set of resources.
        self.Resources = IMAGE_DATA_DIRECTORY()
        self.StrongNameSignature = IMAGE_DATA_DIRECTORY()
        self.CodeManagerTable = IMAGE_DATA_DIRECTORY()  # Deprecated apparently
        # Used for manged codee that has unmaanaged code inside it (or exports methods as unmanaged entry points)
        self.VTableFixups = IMAGE_DATA_DIRECTORY()
        self.ExportAddressTableJumps = IMAGE_DATA_DIRECTORY()
        # null for ordinary IL images. In NGEN images it points at a code:CORCOMPILE_HEADER structure.
        # In Ready2Run images it points to a READYTORUN_HEADER.
        # TODO: ALso support all the ready2run stuff
        self.ManagerNativeHeader = IMAGE_DATA_DIRECTORY()


class IMAGE_COR_ILMETHOD_SECT_SMALL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Kind = v_uint8()
        self.DataSize = v_uint8()


class IMAGE_COR_ILMETHOD_SECT_FAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Kind = v_uint8()
        self.DataSize = v_uint24()

class IMAGE_COR_ILMETHOD_SECT_EH_CLAUSE_FAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()  # TODO: So this is actually an enum, so is 32 right?
        self.TryOffset = v_uint32()
        self.TryLength = v_uint32()
        self.HandlerOffset = v_uint32()
        self.HandlerLength = v_uint32()

        self.TokenOffset = v_uint32()  # Union of ClassToken and FilterOffset


class IMAGE_COR_ILMETHOD_SECT_EH_FAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SectFast = IMAGE_COR_ILMETHOD_SECT_FAT()
        # TODO: Who sets this exception handler clause length?
        self.Clauses = vstruct.VArray([])  # This is an array of IMAGE_COR_ILMETHOD_SECT_EH_CLAUSE_FAT


class IMAGE_COR_ILMETHOD_SECT_EH_CLAUSE_SMALL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.TryOffset = v_uint16()
        self.TryLength = v_uint8()
        self.HandlerOffset = v_uint16()
        self.HandlerLength = v_uint8()
        self.TokenOffset = v_uint32()  # Union of ClassToken and FilterOffset


class IMAGE_COR_ILMETHOD_SECT_EH_SMALL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SectSmall = IMAGE_COR_ILMETHOD_SECT_SMALL()
        self.Reserved = v_uint16()
        # TODO: Who sets this exception handler clause length?
        self.Clauses = vstruct.VArray([])  # This is an array of IMAGE_COR_ILMETHOD_SECT_EH_CLAUSE_SMALL


class IMAGE_COR_ILMETHOD_TINY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags_CodeSize = v_uint8()


class IMAGE_COR_ILMETHOD_FAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        # So this is a bitfield where 12 of it is flags and 4 of it is the Size
        self.FlagNSize = v_uint16()
        self.MaxStack = v_uint16()
        self.CodeSize = v_uint32()
        self.LocVarSigTok = v_uint32()


class IMAGE_COR_VTABLEFIXUP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Rva = v_uint32()
        self.Count = v_uint16()
        self.Type = v_uint16()


class METADATA_SIGNATURE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.ExtraData = v_uint32()
        self.VersionStringLen = v_uint32()
        self.VersionString = v_str(32)  # WAG

    def pcb_VersionStringLen(self):
        vslen = self.vsGetField('VersionStringLen')
        self.vsGetField('VersionString').vsSetLength(vslen)


class METADATA_STORAGE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint8()  # should be set to 0
        self.Pad = v_uint8()
        self.NumberOfStreams = v_uint16()


class METADATA_STREAM_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.Size = v_uint32()
        self.RCName = v_str(32)

    def pcb_RCName(self):
        rclen = len(self.RCName) + 1  # +1 for the null terminator
        self.vsGetField("RCName").vsSetLength(rclen)


# https://github.com/dotnet/runtime/blob/master/src/coreclr/src/md/inc/metamodel.h#L238
class METADATA_TABLE_STREAM_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Reserved = v_uint32()
        self.MajorVersion = v_uint8()
        self.MinorVersion = v_uint8()
        self.Heap = v_uint8()
        self.Rid = v_uint8()
        self.MaskValid = v_uint64()
        self.Sorted = v_uint64()


# https://github.com/dotnet/runtime/blob/master/src/coreclr/src/inc/metamodelpub.h
class METADATA_TABLE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pointer = v_uint32()
        self.NumberColumns = v_uint8()
        self.IndexOfKey = v_uint8()
        self.SizeOfRecord = v_uint16()


class METADATA_TABLE_DESCRIPTOR64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pointer = v_uint64()
        self.NumberColumns = v_uint8()
        self.IndexOfKey = v_uint8()
        self.SizeOfRecord = v_uint16()


class METADATA_TABLE_COLUMN_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.ColumnOffset = v_uint8()
        self.ColumnSize = v_uint8()


class COR_FIELD_OFFSET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ridOfField = self.v_uint32()
        self.ulOffset = self.v_uint32()
