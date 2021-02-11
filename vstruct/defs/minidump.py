import logging

import vstruct
from vstruct.primitives import *

class MiniDumpString(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()

    def pcb_Length(self):
        self.Buffer = v_zwstr()

class VS_FixedFileInfo(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.StrucVersion = v_uint32()
        self.FileVersionMS = v_uint32()
        self.FileVersionLS = v_uint32()
        self.ProductVersionMS = v_uint32()
        self.ProductVersionLS = v_uint32()
        self.FileFlagsMask = v_uint32()
        self.FileFlags = v_uint32()
        self.FileOS = v_uint32()
        self.FileType = v_uint32()
        self.FileSubType = v_uint32()
        self.FileDateMS = v_uint32()
        self.FileDateLS = v_uint32()

class MiniDumpLocationDescriptor(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.RVA = v_uint32()

class MiniDumpMemoryDescriptor(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartOfMemoryPage = v_uint64()
        self.Memory = MiniDumpLocationDescriptor()

class MiniDumpMemoryDescriptor64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartOfMemoryRange = v_uint64()
        self.DataSize = v_uint64()

class MiniDumpLastReservedStream(vstruct.VStruct):
    '''
    Stream Type: 0xffff
        LastReservedStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)

class MiniDumpJavaScriptDataStream(vstruct.VStruct):
    '''
    Stream Type 20:
        JavaScriptDataStream
        Defined in DbgHelp.h _MINIDUMP_STREAM_TYPE struct, no other reference
    '''
    # TODO: not implemented
    def __init__(self):
        vstruct.VStruct.__init__(self)

class MiniDumpTokenInfoHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TokenSize = v_uint32()
        self.TokenId = v_uint32()
        self.TokenHandle = v_uint64()

    def pcb_TokenHandle(self):
        # inclusive length counter, subtract len of header size
        if self.TokenSize < len(MiniDumpTokenInfoHeader()):
            raise Exception('unexpected token size')

        self.Token = v_bytes(self.TokenSize - len(MiniDumpTokenInfoHeader()))

class MiniDumpTokenInfoListStream(vstruct.VStruct):
    '''
    Stream Type 19:
        TokenStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TokenListSize = v_uint32()
        self.TokenListEntries = v_uint32()
        self.ListHeaderSize = v_uint32()
        self.ElementHeaderSize = v_uint32()

    def pcb_ElementHeaderSize(self):
        self.Entries = vstruct.VArray([MiniDumpTokenInfoHeader() for i in range(self.TokenListEntries)])

AVRF_MAX_TRACES = 32

class AvrfBacktraceInformation(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Depth = v_uint32()
        self.Index = v_uint32()
        self.ReturnAddresses = vstruct.VArray([v_uint64() for i in range(AVRF_MAX_TRACES)])

class AvrfHandleOperationList(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Handle = v_uint64()
        self.ProcessId = v_uint32()
        self.ThreadId = v_uint32()
        self.OperationType = v_uint32()
        self.Spare0 = v_uint32()
        self.BackTraceInformation = AvrfBacktraceInformation()

class MiniDumpHandleOperationListStream(vstruct.VStruct):
    '''
    Stream Type 18:
        HandleOperationListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader = v_uint32()
        self.SizeOfEntry = v_uint32()
        self.NumberOfEntries = v_uint32()
        self.Reserved = v_uint32()

    def pcb_Reserved(self):
        self.Entries = vstruct.VArray([AvrfHandleOperationList() for i in range(self.NumberOfEntries)])

class MiniDumpThreadInfo(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ThreadId = v_uint32()
        self.DumpFlags = v_uint32()
        self.DumpErro = v_uint32()
        self.ExitStatus = v_uint32()
        self.CreateTime = v_uint64()
        self.ExitTime = v_uint64()
        self.KernelTime = v_uint64()
        self.UserTime = v_uint64()
        self.StartAddress = v_uint64()
        self.Affinity = v_uint64()

class MiniDumpThreadInfoListStream(vstruct.VStruct):
    '''
    Stream Type 17:
        ThreadInfoListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader = v_uint32()
        self.SizeOfEntry = v_uint32()
        self.NumberOfEntries = v_uint32()

    def pcb_NumberOfEntries(self):
        self.ThreadInfo = vstruct.VArray([MiniDumpThreadInfo() for i in range(self.NumberOfEntries)])

class MiniDumpMemoryInfo(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseAddress = v_uint64()
        self.AllocationBase = v_uint64()
        self.AllocationProtect = v_uint32()
        self.__alignment = v_uint32()
        self.RegionSize = v_uint64()
        self.State = v_uint32()
        self.Protect = v_uint32()
        self.Type = v_uint32()
        self.__alignment2 = v_uint32()

class MiniDumpMemoryInfoListStream(vstruct.VStruct):
    '''
    Stream Type 16:
        MemoryInfoListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader       = v_uint32()
        self.SizeOfEntry        = v_uint32()
        self.NumberOfEntries    = v_uint64()

    def pcb_NumberOfEntries(self):
        self.Entries            = vstruct.VArray([MiniDumpMemoryInfo() for i in range(self.NumberOfEntries)])

class MiniDumpMiscInfo2Stream(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfInfo = v_uint32()
        self.Flags1 = v_uint32()
        self.ProcessId = v_uint32()
        self.ProcessCreateTime = v_uint32()
        self.ProcessUserTime = v_uint32()
        self.ProcessKernelTime = v_uint32()
        self.ProcessorMaxMhz = v_uint32()
        self.ProcessorCurrentMhz = v_uint32()
        self.ProcessorMhzLimit = v_uint32()
        self.ProcessorMaxIdleState = v_uint32()
        self.ProcessorCurrentIdleState = v_uint32()

class MiniDumpMiscInfoStream(vstruct.VStruct):
    '''
    Stream Type 15:
        MiscInfoStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfInfo = v_uint32()
        self.Flags1 = v_uint32()
        self.ProcessId = v_uint32()
        self.ProcessCreateTime = v_uint32()
        self.ProcessUserTime = v_uint32()
        self.ProcessKernelTime = v_uint32()

class MiniDumpUnloadedModule(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseOfImage = v_uint64()
        self.SizeOfImage = v_uint32()
        self.CheckSum = v_uint32()
        self.TimeDateStamp = v_uint32()
        # TODO: RVA to MINIDUMP_STRING
        self.ModuleNameRVA = v_uint32()

class MiniDumpUnloadedModuleListStream(vstruct.VStruct):
    '''
    Stream Type 14:
        UnloadedModuleListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader = v_uint32()
        self.SizeOfEntry = v_uint32()
        self.NumberOfEntries = v_uint32()

    def pcb_NumberOfEntries(self):
        self.Entries = vstruct.VArray([MiniDumpUnloadedModule() for i in range(self.NumberOfEntries)])

class MiniDumpFunctionTableDescriptor(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumAddress = v_uint64()
        self.MaximumAddress = v_uint64()
        self.BaseAddress = v_uint64()
        self.EntryCount = v_uint32()
        self.SizeOfAlignPad = v_uint32()

    # TODO: unfinished

class MiniDumpFunctionTableStream(vstruct.VStruct):
    '''
    Stream Type 13:
        FunctionTableStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader = v_uint32()
        self.SizeOfDescriptor = v_uint32()
        self.SizeOfNativeDescriptor = v_uint32()
        self.SizeOfFunctionEntry = v_uint32()
        self.NumberOfDescriptors = v_uint32()
        self.SizeOfAlignPad = v_uint32()

    def pcb_SizeOfAlignPad(self):
        self.Padding = v_bytes(self.SizeOfAlignPad)

class MiniDumpHandleObjectInformation(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextInfoRva = v_uint32()
        self.InfoType = v_uint32()
        self.SizeOfInfo = v_uint32()

    def pcb_SizeOfInfo(self):
        self.Information = v_bytes(self.SizeOfInfo)

class MiniDumpHandleDescriptor2(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Handle = v_uint64()
        # TODO: RVA to MINIDUMP_STRING
        self.TypeNameRva = v_uint32()
        # TODO: RVA to MINIDUMP_STRING
        self.ObjectNameRva = v_uint32()
        self.Attributes = v_uint32()
        self.GrantedAccess = v_uint32()
        self.HandleCount = v_uint32()
        self.PointerCount = v_uint32()
        # TODO: RVA to MINIDUMP_HANDLE_OBJECT_INFORMATION
        self.ObjectInfoRva = v_uint32()
        self.Reserved0 = v_uint32()

class MiniDumpHandleDescriptor(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Handle = v_uint32()
        # TODO: RVA to MINIDUMP_STRING
        self.TypeNameRva = v_uint32()
        # TODO: RVA to MINIDUMP_STRING
        self.ObjectNameRva = v_uint32()
        self.Attributes = v_uint32()
        self.GrantedAccess = v_uint32()
        self.HandleCount = v_uint32()
        self.PointerCount = v_uint32()

class MiniDumpHandleDataStream(vstruct.VStruct):
    '''
    Stream Type 12:
        HandleDataStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfHeader = v_uint32()
        self.SizeOfDescriptor = v_uint32()
        self.NumberOfDescriptors = v_uint32()
        self.Reserved = v_uint32()

    def pcb_Reserved(self):
        if self.SizeOfDescriptor == 32:     # Handle Descriptor
            self.Descriptors = vstruct.VArray([MiniDumpHandleDescriptor() for i in range(self.NumberOfDescriptors)])
        elif self.SizeOfDescriptor == 40:   # Handle Descriptor 2
            self.Descriptors = vstruct.VArray([MiniDumpHandleDescriptor2() for i in range(self.NumberOfDescriptors)])
        else:                               # Handle Descriptor Unknown
            raise Exception('unknown Handle Descriptor version')

class MiniDumpCommentStreamW(vstruct.VStruct):
    '''
    Stream Type 11:
        CommentStreamW
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CommentW = v_zwstr()

class MiniDumpCommentStreamA(vstruct.VStruct):
    '''
    Stream Type 10:
        CommentStreamA
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CommentA = v_zstr()

class MiniDumpMemory64ListStream(vstruct.VStruct):
    '''
    Stream Type 9:
        MemoryList64Stream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfMemoryRanges = v_uint64()
        self.BaseRva = v_uint64()

    def pcb_BaseRva(self):
        self.MemoryRanges =  vstruct.VArray([MiniDumpMemoryDescriptor64() for i in range(self.NumberOfMemoryRanges)])

class MiniDumpThreadEx(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ThreadId = v_uint32()
        self.SuspendCount = v_uint32()
        self.PriorityClass = v_uint32()
        self.Priority = v_uint32()
        self.Teb = v_uint64()
        self.Stack = MiniDumpMemoryDescriptor()
        self.ThreadContext = MiniDumpLocationDescriptor()
        self.BackingStore = MiniDumpMemoryDescriptor()

class MiniDumpThreadExListStream(vstruct.VStruct):
    '''
    Stream Type 8:
        ThreadExListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfThreads = v_uint32()

    def pcb_NumberOfThread(self):
        self.Threads = vstruct.VArray([MiniDumpThreadEx() for i in range(self.NumberOfThreads)])

class MiniDumpSystemInfoStream(vstruct.VStruct):
    '''
    Stream Type 7:
        SystemInfoStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ProcessorArchitecture = v_uint16()
        self.ProcessorLevel = v_uint16()
        self.ProcessorRevision = v_uint16()
        self.Reserved = v_uint16()
        self.MajorVersion = v_uint32()
        self.MinorVersion = v_uint32()
        self.BuildNumber = v_uint32()
        self.PlatformId = v_uint32()
        self.CSDVersionRSA = v_uint32()
        self.Reserved1 = v_uint32()
        self.CpuInfo1 = v_uint32()
        self.CpuInfo2 = v_uint32()
        self.CpuInfo3 = v_uint32()
        self.CpuInfo4 = v_uint32()
        self.CpuInfo5 = v_uint32()
        self.CpuInfo6 = v_uint32()

EXCEPTION_MAXIMUM_PARAMETERS = 15

class MiniDumpException(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_uint64()
        self.ExceptionAddress = v_uint64()
        self.NumberParameters = v_uint32()
        self.__unusedAlignment = v_uint32()
        self.ExecptionInformation = vstruct.VArray([v_uint64() for i in range(EXCEPTION_MAXIMUM_PARAMETERS)])

class MiniDumpExceptionStream(vstruct.VStruct):
    '''
    Stream Type 6:
        ExceptionStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ThreadId = v_uint32()
        self.__aligntment = v_uint32()
        self.ExceptionRecored = MiniDumpException()
        self.ThreadContext = MiniDumpLocationDescriptor()

class MiniDumpMemoryListStream(vstruct.VStruct):
    '''
    Stream Type 5
        MemoryListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfMemoryRanges = v_uint32()

    def pcb_NumberOfMemoryRanges(self):
        self.MemoryRanges = vstruct.VArray([MiniDumpMemoryDescriptor() for i in range(self.NumberOfMemoryRanges)])

class MiniDumpModule(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseOfImage = v_uint64()
        self.SizeOfImage = v_uint32()
        self.CheckSum = v_uint32()
        self.TimeDateStamp = v_uint32()
        # TODO: RVA to MINIDUMP_STRING
        self.ModuleNameRva = v_uint32()
        self.VersionInfo = VS_FixedFileInfo()
        self.CvRecord = MiniDumpLocationDescriptor()
        self.MiscRecord = MiniDumpLocationDescriptor()
        self.Reserved1 = v_uint64()
        self.Reserved2 = v_uint64()

class MiniDumpModuleListStream(vstruct.VStruct):
    '''
    Stream Type 4
        ModuleListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfModules = v_uint32()

    def pcb_NumberOfModules(self):
        self.Modules = vstruct.VArray([MiniDumpModule() for i in range(self.NumberOfModules)])

class MiniDumpThread(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ThreadId = v_uint32()
        self.SuspendCount = v_uint32()
        self.PriorityClass = v_uint32()
        self.Priority = v_uint32()
        self.Teb = v_uint64()
        self.Stack = MiniDumpMemoryDescriptor()
        self.ThreadContext = MiniDumpLocationDescriptor()

class MiniDumpThreadListStream(vstruct.VStruct):
    '''
    Stream Type 3:
        ThreadListStream
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfThreads = v_uint32()
        self.Threads = MiniDumpThread()

class MiniDumpReservedStream1(vstruct.VStruct):
    '''
    Stream Type 2:
        ReservedStream1 - Reserved, do not use this value
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)

class MiniDumpReservedStream0(vstruct.VStruct):
    '''
    Stream Type 1:
        ReservedStream0 - Reserved, do not use this value
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)

class MiniDumpUnusedStream(vstruct.VStruct):
    '''
    Stream Type 0:
        UnusedStream - Reserved, do not use this value
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)

class MiniDumpDirectory(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StreamType = v_uint32()
        self.Location = MiniDumpLocationDescriptor()

class MiniDumpHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.Version = v_uint32()
        self.NumberOfStreams = v_uint32()
        self.StreamDirectoryRVA = v_uint32()
        self.Checksum = v_uint32()
        self.Resv_TimeDateStamp = v_uint32()
        self.Flags = v_uint64()

    def pcb_Flags(self):
        self.Directory = vstruct.VArray([MiniDumpDirectory() for i in range(self.NumberOfStreams)])

streamsDict = { 0: MiniDumpUnusedStream,
                1: MiniDumpReservedStream0,
                2: MiniDumpReservedStream1,
                3: MiniDumpThreadListStream,
                4: MiniDumpModuleListStream,
                5: MiniDumpMemoryListStream,
                6: MiniDumpExceptionStream,
                7: MiniDumpSystemInfoStream,
                8: MiniDumpThreadExListStream,
                9: MiniDumpMemory64ListStream,
                10: MiniDumpCommentStreamA,
                11: MiniDumpCommentStreamW,
                12: MiniDumpHandleDataStream,
                13: MiniDumpFunctionTableStream,
                14: MiniDumpUnloadedModuleListStream,
                15: MiniDumpMiscInfoStream,
                16: MiniDumpMemoryInfoListStream,
                17: MiniDumpThreadInfoListStream,
                18: MiniDumpHandleOperationListStream,
                19: MiniDumpTokenInfoListStream,
                20: MiniDumpJavaScriptDataStream,
                0xFFFF: MiniDumpLastReservedStream,
            }

class MiniDump(object):
    def __init__(self, bytez):
        self.bytez = bytez
        self.header = MiniDumpHeader()
        self.header.vsParse(bytez)

        for idx, header in self.header.Directory:
            # check if streamtype is in our dict of known types
            if header.StreamType in streamsDict:
                sclass = streamsDict[header.StreamType]
                soffset = header.Location.RVA

                # assumption there will be one instance of a stream in minidump
                stream = vars(self)[sclass.__name__] = sclass()
                stream.vsParse(bytez, offset=soffset)
            else:
                logging.info('Unknown stream type of %d', header.StreamType)

    def tree(self):
        txt = []
        txt.append(self.header.tree())
        for idx, header in self.header.Directory:
            # check if streamtype is in our dict of known types
            if header.StreamType in streamsDict:
                sclass = streamsDict[header.StreamType]
                txt.append(vars(self)[sclass.__name__].tree())

        return ''.join(txt)

    def getModuleNameByAddr(self, addr):
        for idx, mod in self.MiniDumpModuleListStream.Modules:
            if addr == mod.BaseOfImage:
                mname = MiniDumpString()
                mname.vsParse(self.bytez, offset=mod.ModuleNameRva)
                return mname.Buffer

    def getMemoryMaps(self):
        maps = []
        # check if stream has been parsed, if not, possibly an incomplete minidump
        if not hasattr(self, 'MiniDumpMemoryInfoListStream'):
            raise Exception('MiniDumpMemoryInfoListStream does not exist. Dump file may not include full memory dump.')

        for idx, entry in self.MiniDumpMemoryInfoListStream.Entries:
            mname =  self.getModuleNameByAddr(entry.AllocationBase)
            if mname is None:
                mname = 'Module Name Not Found'

            maps.append((entry.BaseAddress, entry.RegionSize, entry.Protect, mname))
        return maps

    def readMemory(self, addr, size):
        # check if stream has been parsed, if not, possibly an incomplete minidump
        if not hasattr(self, 'MiniDumpMemory64ListStream'):
            raise Exception('MiniDumpMemory64ListStream does not exist. Dump file may not include full memory dump.')

        offset = self.MiniDumpMemory64ListStream.BaseRva
        for idx, mrange in self.MiniDumpMemory64ListStream.MemoryRanges:
            if addr == mrange.StartOfMemoryRange:
                return self.bytez[offset:offset+size]

            offset += mrange.DataSize

def parseFromBytes(bytez):
    return MiniDump(bytez)

def parseFromFname(fname):
    with open(fname, 'rb') as f:
        bytez = f.read()

    return parseFromBytes(bytez)
