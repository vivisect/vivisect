# -*- coding: utf8 -*-
# Version: 5.2
# Architecture: i386
# CompanyName: Microsoft Corporation
# FileDescription: Multi-User Win32 Driver
# FileVersion: 5.2.3790.5019 (srv03_sp2_gdr.120613-0334)
# InternalName: win32k.sys
# LegalCopyright:  Microsoft Corporation. All rights reserved.
# OriginalFilename: win32k.sys
# ProductName: Microsoft Windows Operating System
# ProductVersion: 5.2.3790.5019
# Translation: 78644233
import vstruct
from vstruct.primitives import *

DEVICE_RELATION_TYPE = v_enum()
DEVICE_RELATION_TYPE.BusRelations = 0
DEVICE_RELATION_TYPE.EjectionRelations = 1
DEVICE_RELATION_TYPE.PowerRelations = 2
DEVICE_RELATION_TYPE.RemovalRelations = 3
DEVICE_RELATION_TYPE.TargetDeviceRelation = 4
DEVICE_RELATION_TYPE.SingleBusRelations = 5


IO_ALLOCATION_ACTION = v_enum()
IO_ALLOCATION_ACTION.KeepObject = 1
IO_ALLOCATION_ACTION.DeallocateObject = 2
IO_ALLOCATION_ACTION.DeallocateObjectKeepRegisters = 3


BUS_QUERY_ID_TYPE = v_enum()
BUS_QUERY_ID_TYPE.BusQueryDeviceID = 0
BUS_QUERY_ID_TYPE.BusQueryHardwareIDs = 1
BUS_QUERY_ID_TYPE.BusQueryCompatibleIDs = 2
BUS_QUERY_ID_TYPE.BusQueryInstanceID = 3
BUS_QUERY_ID_TYPE.BusQueryDeviceSerialNumber = 4


DEVICE_POWER_STATE = v_enum()
DEVICE_POWER_STATE.PowerDeviceUnspecified = 0
DEVICE_POWER_STATE.PowerDeviceD0 = 1
DEVICE_POWER_STATE.PowerDeviceD1 = 2
DEVICE_POWER_STATE.PowerDeviceD2 = 3
DEVICE_POWER_STATE.PowerDeviceD3 = 4
DEVICE_POWER_STATE.PowerDeviceMaximum = 5


KSPIN_LOCK_QUEUE_NUMBER = v_enum()
KSPIN_LOCK_QUEUE_NUMBER.LockQueueDispatcherLock = 0
KSPIN_LOCK_QUEUE_NUMBER.LockQueueUnusedSpare1 = 1
KSPIN_LOCK_QUEUE_NUMBER.LockQueuePfnLock = 2
KSPIN_LOCK_QUEUE_NUMBER.LockQueueSystemSpaceLock = 3
KSPIN_LOCK_QUEUE_NUMBER.LockQueueVacbLock = 4
KSPIN_LOCK_QUEUE_NUMBER.LockQueueMasterLock = 5
KSPIN_LOCK_QUEUE_NUMBER.LockQueueNonPagedPoolLock = 6
KSPIN_LOCK_QUEUE_NUMBER.LockQueueIoCancelLock = 7
KSPIN_LOCK_QUEUE_NUMBER.LockQueueWorkQueueLock = 8
KSPIN_LOCK_QUEUE_NUMBER.LockQueueIoVpbLock = 9
KSPIN_LOCK_QUEUE_NUMBER.LockQueueIoDatabaseLock = 10
KSPIN_LOCK_QUEUE_NUMBER.LockQueueIoCompletionLock = 11
KSPIN_LOCK_QUEUE_NUMBER.LockQueueNtfsStructLock = 12
KSPIN_LOCK_QUEUE_NUMBER.LockQueueAfdWorkQueueLock = 13
KSPIN_LOCK_QUEUE_NUMBER.LockQueueBcbLock = 14
KSPIN_LOCK_QUEUE_NUMBER.LockQueueMmNonPagedPoolLock = 15
KSPIN_LOCK_QUEUE_NUMBER.LockQueueUnusedSpare16 = 16
KSPIN_LOCK_QUEUE_NUMBER.LockQueueTimerTableLock = 17
KSPIN_LOCK_QUEUE_NUMBER.LockQueueMaximumLock = 33


FSINFOCLASS = v_enum()
FSINFOCLASS.FileFsVolumeInformation = 1
FSINFOCLASS.FileFsLabelInformation = 2
FSINFOCLASS.FileFsSizeInformation = 3
FSINFOCLASS.FileFsDeviceInformation = 4
FSINFOCLASS.FileFsAttributeInformation = 5
FSINFOCLASS.FileFsControlInformation = 6
FSINFOCLASS.FileFsFullSizeInformation = 7
FSINFOCLASS.FileFsObjectIdInformation = 8
FSINFOCLASS.FileFsDriverPathInformation = 9
FSINFOCLASS.FileFsMaximumInformation = 10


GDIObjType = v_enum()
GDIObjType.GDIObjType_DEF_TYPE = 0
GDIObjType.GDIObjType_DC_TYPE = 1
GDIObjType.GDIObjType_UNUSED1_TYPE = 2
GDIObjType.GDIObjType_UNUSED2_TYPE = 3
GDIObjType.GDIObjType_RGN_TYPE = 4
GDIObjType.GDIObjType_SURF_TYPE = 5
GDIObjType.GDIObjType_CLIENTOBJ_TYPE = 6
GDIObjType.GDIObjType_PATH_TYPE = 7
GDIObjType.GDIObjType_PAL_TYPE = 8
GDIObjType.GDIObjType_ICMLCS_TYPE = 9
GDIObjType.GDIObjType_LFONT_TYPE = 10
GDIObjType.GDIObjType_RFONT_TYPE = 11
GDIObjType.GDIObjType_PFE_TYPE = 12
GDIObjType.GDIObjType_PFT_TYPE = 13
GDIObjType.GDIObjType_ICMCXF_TYPE = 14
GDIObjType.GDIObjType_SPRITE_TYPE = 15
GDIObjType.GDIObjType_BRUSH_TYPE = 16
GDIObjType.GDIObjType_UMPD_TYPE = 17
GDIObjType.GDIObjType_UNUSED4_TYPE = 18
GDIObjType.GDIObjType_SPACE_TYPE = 19
GDIObjType.GDIObjType_UNUSED5_TYPE = 20
GDIObjType.GDIObjType_META_TYPE = 21
GDIObjType.GDIObjType_EFSTATE_TYPE = 22
GDIObjType.GDIObjType_BMFD_TYPE = 23
GDIObjType.GDIObjType_VTFD_TYPE = 24
GDIObjType.GDIObjType_TTFD_TYPE = 25
GDIObjType.GDIObjType_RC_TYPE = 26
GDIObjType.GDIObjType_TEMP_TYPE = 27
GDIObjType.GDIObjType_DRVOBJ_TYPE = 28
GDIObjType.GDIObjType_DCIOBJ_TYPE = 29
GDIObjType.GDIObjType_SPOOL_TYPE = 30
GDIObjType.GDIObjType_MAX_TYPE = 30
GDIObjType.GDIObjTypeTotal = 31


POOL_TYPE = v_enum()
POOL_TYPE.NonPagedPool = 0
POOL_TYPE.PagedPool = 1
POOL_TYPE.NonPagedPoolMustSucceed = 2
POOL_TYPE.DontUseThisType = 3
POOL_TYPE.NonPagedPoolCacheAligned = 4
POOL_TYPE.PagedPoolCacheAligned = 5
POOL_TYPE.NonPagedPoolCacheAlignedMustS = 6
POOL_TYPE.MaxPoolType = 7
POOL_TYPE.NonPagedPoolSession = 32
POOL_TYPE.PagedPoolSession = 33
POOL_TYPE.NonPagedPoolMustSucceedSession = 34
POOL_TYPE.DontUseThisTypeSession = 35
POOL_TYPE.NonPagedPoolCacheAlignedSession = 36
POOL_TYPE.PagedPoolCacheAlignedSession = 37
POOL_TYPE.NonPagedPoolCacheAlignedMustSSession = 38


MODE = v_enum()
MODE.KernelMode = 0
MODE.UserMode = 1
MODE.MaximumMode = 2


OB_OPEN_REASON = v_enum()
OB_OPEN_REASON.ObCreateHandle = 0
OB_OPEN_REASON.ObOpenHandle = 1
OB_OPEN_REASON.ObDuplicateHandle = 2
OB_OPEN_REASON.ObInheritHandle = 3
OB_OPEN_REASON.ObMaxOpenReason = 4


DEVICE_TEXT_TYPE = v_enum()
DEVICE_TEXT_TYPE.DeviceTextDescription = 0
DEVICE_TEXT_TYPE.DeviceTextLocationInformation = 1


POWER_STATE_TYPE = v_enum()
POWER_STATE_TYPE.SystemPowerState = 0
POWER_STATE_TYPE.DevicePowerState = 1


FILE_INFORMATION_CLASS = v_enum()
FILE_INFORMATION_CLASS.FileDirectoryInformation = 1
FILE_INFORMATION_CLASS.FileFullDirectoryInformation = 2
FILE_INFORMATION_CLASS.FileBothDirectoryInformation = 3
FILE_INFORMATION_CLASS.FileBasicInformation = 4
FILE_INFORMATION_CLASS.FileStandardInformation = 5
FILE_INFORMATION_CLASS.FileInternalInformation = 6
FILE_INFORMATION_CLASS.FileEaInformation = 7
FILE_INFORMATION_CLASS.FileAccessInformation = 8
FILE_INFORMATION_CLASS.FileNameInformation = 9
FILE_INFORMATION_CLASS.FileRenameInformation = 10
FILE_INFORMATION_CLASS.FileLinkInformation = 11
FILE_INFORMATION_CLASS.FileNamesInformation = 12
FILE_INFORMATION_CLASS.FileDispositionInformation = 13
FILE_INFORMATION_CLASS.FilePositionInformation = 14
FILE_INFORMATION_CLASS.FileFullEaInformation = 15
FILE_INFORMATION_CLASS.FileModeInformation = 16
FILE_INFORMATION_CLASS.FileAlignmentInformation = 17
FILE_INFORMATION_CLASS.FileAllInformation = 18
FILE_INFORMATION_CLASS.FileAllocationInformation = 19
FILE_INFORMATION_CLASS.FileEndOfFileInformation = 20
FILE_INFORMATION_CLASS.FileAlternateNameInformation = 21
FILE_INFORMATION_CLASS.FileStreamInformation = 22
FILE_INFORMATION_CLASS.FilePipeInformation = 23
FILE_INFORMATION_CLASS.FilePipeLocalInformation = 24
FILE_INFORMATION_CLASS.FilePipeRemoteInformation = 25
FILE_INFORMATION_CLASS.FileMailslotQueryInformation = 26
FILE_INFORMATION_CLASS.FileMailslotSetInformation = 27
FILE_INFORMATION_CLASS.FileCompressionInformation = 28
FILE_INFORMATION_CLASS.FileObjectIdInformation = 29
FILE_INFORMATION_CLASS.FileCompletionInformation = 30
FILE_INFORMATION_CLASS.FileMoveClusterInformation = 31
FILE_INFORMATION_CLASS.FileQuotaInformation = 32
FILE_INFORMATION_CLASS.FileReparsePointInformation = 33
FILE_INFORMATION_CLASS.FileNetworkOpenInformation = 34
FILE_INFORMATION_CLASS.FileAttributeTagInformation = 35
FILE_INFORMATION_CLASS.FileTrackingInformation = 36
FILE_INFORMATION_CLASS.FileIdBothDirectoryInformation = 37
FILE_INFORMATION_CLASS.FileIdFullDirectoryInformation = 38
FILE_INFORMATION_CLASS.FileValidDataLengthInformation = 39
FILE_INFORMATION_CLASS.FileShortNameInformation = 40
FILE_INFORMATION_CLASS.FileIoCompletionNotificationInformation = 41
FILE_INFORMATION_CLASS.FileMaximumInformation = 42


GDILoObjType = v_enum()
GDILoObjType.GDILoObjType_LO_BRUSH_TYPE = 1048576
GDILoObjType.GDILoObjType_LO_DC_TYPE = 65536
GDILoObjType.GDILoObjType_LO_BITMAP_TYPE = 327680
GDILoObjType.GDILoObjType_LO_PALETTE_TYPE = 524288
GDILoObjType.GDILoObjType_LO_FONT_TYPE = 655360
GDILoObjType.GDILoObjType_LO_REGION_TYPE = 262144
GDILoObjType.GDILoObjType_LO_ICMLCS_TYPE = 589824
GDILoObjType.GDILoObjType_LO_CLIENTOBJ_TYPE = 393216
GDILoObjType.GDILoObjType_LO_ALTDC_TYPE = 2162688
GDILoObjType.GDILoObjType_LO_PEN_TYPE = 3145728
GDILoObjType.GDILoObjType_LO_EXTPEN_TYPE = 5242880
GDILoObjType.GDILoObjType_LO_DIBSECTION_TYPE = 2424832
GDILoObjType.GDILoObjType_LO_METAFILE16_TYPE = 2490368
GDILoObjType.GDILoObjType_LO_METAFILE_TYPE = 4587520
GDILoObjType.GDILoObjType_LO_METADC16_TYPE = 6684672


SECURITY_OPERATION_CODE = v_enum()
SECURITY_OPERATION_CODE.SetSecurityDescriptor = 0
SECURITY_OPERATION_CODE.QuerySecurityDescriptor = 1
SECURITY_OPERATION_CODE.DeleteSecurityDescriptor = 2
SECURITY_OPERATION_CODE.AssignSecurityDescriptor = 3


SECURITY_IMPERSONATION_LEVEL = v_enum()
SECURITY_IMPERSONATION_LEVEL.SecurityAnonymous = 0
SECURITY_IMPERSONATION_LEVEL.SecurityIdentification = 1
SECURITY_IMPERSONATION_LEVEL.SecurityImpersonation = 2
SECURITY_IMPERSONATION_LEVEL.SecurityDelegation = 3


DEVICE_USAGE_NOTIFICATION_TYPE = v_enum()
DEVICE_USAGE_NOTIFICATION_TYPE.DeviceUsageTypeUndefined = 0
DEVICE_USAGE_NOTIFICATION_TYPE.DeviceUsageTypePaging = 1
DEVICE_USAGE_NOTIFICATION_TYPE.DeviceUsageTypeHibernation = 2
DEVICE_USAGE_NOTIFICATION_TYPE.DeviceUsageTypeDumpFile = 3


INTERFACE_TYPE = v_enum()
INTERFACE_TYPE.InterfaceTypeUndefined = -1
INTERFACE_TYPE.Internal = 0
INTERFACE_TYPE.Isa = 1
INTERFACE_TYPE.Eisa = 2
INTERFACE_TYPE.MicroChannel = 3
INTERFACE_TYPE.TurboChannel = 4
INTERFACE_TYPE.PCIBus = 5
INTERFACE_TYPE.VMEBus = 6
INTERFACE_TYPE.NuBus = 7
INTERFACE_TYPE.PCMCIABus = 8
INTERFACE_TYPE.CBus = 9
INTERFACE_TYPE.MPIBus = 10
INTERFACE_TYPE.MPSABus = 11
INTERFACE_TYPE.ProcessorInternal = 12
INTERFACE_TYPE.InternalPowerBus = 13
INTERFACE_TYPE.PNPISABus = 14
INTERFACE_TYPE.PNPBus = 15
INTERFACE_TYPE.MaximumInterfaceType = 16


MEMORY_TYPE = v_enum()
MEMORY_TYPE.MemoryExceptionBlock = 0
MEMORY_TYPE.MemorySystemBlock = 1
MEMORY_TYPE.MemoryFree = 2
MEMORY_TYPE.MemoryBad = 3
MEMORY_TYPE.MemoryLoadedProgram = 4
MEMORY_TYPE.MemoryFirmwareTemporary = 5
MEMORY_TYPE.MemoryFirmwarePermanent = 6
MEMORY_TYPE.MemoryFreeContiguous = 7
MEMORY_TYPE.MemorySpecialMemory = 8
MEMORY_TYPE.MemoryMaximum = 9


ReplacesCorHdrNumericDefines = v_enum()
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_ILONLY = 1
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_32BITREQUIRED = 2
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_IL_LIBRARY = 4
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_STRONGNAMESIGNED = 8
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_TRACKDEBUGDATA = 65536
ReplacesCorHdrNumericDefines.COR_VERSION_MAJOR_V2 = 2
ReplacesCorHdrNumericDefines.COR_VERSION_MAJOR = 2
ReplacesCorHdrNumericDefines.COR_VERSION_MINOR = 0
ReplacesCorHdrNumericDefines.COR_DELETED_NAME_LENGTH = 8
ReplacesCorHdrNumericDefines.COR_VTABLEGAP_NAME_LENGTH = 8
ReplacesCorHdrNumericDefines.NATIVE_TYPE_MAX_CB = 1
ReplacesCorHdrNumericDefines.COR_ILMETHOD_SECT_SMALL_MAX_DATASIZE = 255
ReplacesCorHdrNumericDefines.IMAGE_COR_MIH_METHODRVA = 1
ReplacesCorHdrNumericDefines.IMAGE_COR_MIH_EHRVA = 2
ReplacesCorHdrNumericDefines.IMAGE_COR_MIH_BASICBLOCK = 8
ReplacesCorHdrNumericDefines.COR_VTABLE_32BIT = 1
ReplacesCorHdrNumericDefines.COR_VTABLE_64BIT = 2
ReplacesCorHdrNumericDefines.COR_VTABLE_FROM_UNMANAGED = 4
ReplacesCorHdrNumericDefines.COR_VTABLE_CALL_MOST_DERIVED = 16
ReplacesCorHdrNumericDefines.IMAGE_COR_EATJ_THUNK_SIZE = 32
ReplacesCorHdrNumericDefines.MAX_CLASS_NAME = 1024
ReplacesCorHdrNumericDefines.MAX_PACKAGE_NAME = 1024


EX_POOL_PRIORITY = v_enum()
EX_POOL_PRIORITY.LowPoolPriority = 0
EX_POOL_PRIORITY.LowPoolPrioritySpecialPoolOverrun = 8
EX_POOL_PRIORITY.LowPoolPrioritySpecialPoolUnderrun = 9
EX_POOL_PRIORITY.NormalPoolPriority = 16
EX_POOL_PRIORITY.NormalPoolPrioritySpecialPoolOverrun = 24
EX_POOL_PRIORITY.NormalPoolPrioritySpecialPoolUnderrun = 25
EX_POOL_PRIORITY.HighPoolPriority = 32
EX_POOL_PRIORITY.HighPoolPrioritySpecialPoolOverrun = 40
EX_POOL_PRIORITY.HighPoolPrioritySpecialPoolUnderrun = 41


SYSTEM_POWER_STATE = v_enum()
SYSTEM_POWER_STATE.PowerSystemUnspecified = 0
SYSTEM_POWER_STATE.PowerSystemWorking = 1
SYSTEM_POWER_STATE.PowerSystemSleeping1 = 2
SYSTEM_POWER_STATE.PowerSystemSleeping2 = 3
SYSTEM_POWER_STATE.PowerSystemSleeping3 = 4
SYSTEM_POWER_STATE.PowerSystemHibernate = 5
SYSTEM_POWER_STATE.PowerSystemShutdown = 6
SYSTEM_POWER_STATE.PowerSystemMaximum = 7


MEMORY_CACHING_TYPE_ORIG = v_enum()
MEMORY_CACHING_TYPE_ORIG.MmFrameBufferCached = 2


POWER_ACTION = v_enum()
POWER_ACTION.PowerActionNone = 0
POWER_ACTION.PowerActionReserved = 1
POWER_ACTION.PowerActionSleep = 2
POWER_ACTION.PowerActionHibernate = 3
POWER_ACTION.PowerActionShutdown = 4
POWER_ACTION.PowerActionShutdownReset = 5
POWER_ACTION.PowerActionShutdownOff = 6
POWER_ACTION.PowerActionWarmEject = 7


class OBJECT_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.RootDirectory = v_ptr32()
        self.ObjectName = v_ptr32()
        self.Attributes = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.SecurityQualityOfService = v_ptr32()


class tagWin32AllocStats(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwMaxMem = v_uint32()
        self.dwCrtMem = v_uint32()
        self.dwMaxAlloc = v_uint32()
        self.dwCrtAlloc = v_uint32()
        self.pHead = v_ptr32()


class CM_FULL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.PartialResourceList = CM_PARTIAL_RESOURCE_LIST()


class FAST_IO_DISPATCH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfFastIoDispatch = v_uint32()
        self.FastIoCheckIfPossible = v_ptr32()
        self.FastIoRead = v_ptr32()
        self.FastIoWrite = v_ptr32()
        self.FastIoQueryBasicInfo = v_ptr32()
        self.FastIoQueryStandardInfo = v_ptr32()
        self.FastIoLock = v_ptr32()
        self.FastIoUnlockSingle = v_ptr32()
        self.FastIoUnlockAll = v_ptr32()
        self.FastIoUnlockAllByKey = v_ptr32()
        self.FastIoDeviceControl = v_ptr32()
        self.AcquireFileForNtCreateSection = v_ptr32()
        self.ReleaseFileForNtCreateSection = v_ptr32()
        self.FastIoDetachDevice = v_ptr32()
        self.FastIoQueryNetworkOpenInfo = v_ptr32()
        self.AcquireForModWrite = v_ptr32()
        self.MdlRead = v_ptr32()
        self.MdlReadComplete = v_ptr32()
        self.PrepareMdlWrite = v_ptr32()
        self.MdlWriteComplete = v_ptr32()
        self.FastIoReadCompressed = v_ptr32()
        self.FastIoWriteCompressed = v_ptr32()
        self.MdlReadCompleteCompressed = v_ptr32()
        self.MdlWriteCompleteCompressed = v_ptr32()
        self.FastIoQueryOpen = v_ptr32()
        self.ReleaseForModWrite = v_ptr32()
        self.AcquireForCcFlush = v_ptr32()
        self.ReleaseForCcFlush = v_ptr32()


class SECTION_OBJECT_POINTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSectionObject = v_ptr32()
        self.SharedCacheMap = v_ptr32()
        self.ImageSectionObject = v_ptr32()


class tagWin32PoolHead(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.pPrev = v_ptr32()
        self.pNext = v_ptr32()
        self.pTrace = v_ptr32()


class LARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class IMAGE_FILE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Machine = v_uint16()
        self.NumberOfSections = v_uint16()
        self.TimeDateStamp = v_uint32()
        self.PointerToSymbolTable = v_uint32()
        self.NumberOfSymbols = v_uint32()
        self.SizeOfOptionalHeader = v_uint16()
        self.Characteristics = v_uint16()


class IO_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Option = v_uint8()
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Spare1 = v_uint8()
        self.Flags = v_uint16()
        self.Spare2 = v_uint16()
        self.u = IO_RESOURCE_DESCRIPTOR()


class EX_PUSH_LOCK_CACHE_AWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locks = vstruct.VArray([ v_ptr32() for i in xrange(1) ])


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class DEVICE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.FileHeader = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()


class IMAGE_OPTIONAL_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic = v_uint16()
        self.MajorLinkerVersion = v_uint8()
        self.MinorLinkerVersion = v_uint8()
        self.SizeOfCode = v_uint32()
        self.SizeOfInitializedData = v_uint32()
        self.SizeOfUninitializedData = v_uint32()
        self.AddressOfEntryPoint = v_uint32()
        self.BaseOfCode = v_uint32()
        self.BaseOfData = v_uint32()
        self.ImageBase = v_uint32()
        self.SectionAlignment = v_uint32()
        self.FileAlignment = v_uint32()
        self.MajorOperatingSystemVersion = v_uint16()
        self.MinorOperatingSystemVersion = v_uint16()
        self.MajorImageVersion = v_uint16()
        self.MinorImageVersion = v_uint16()
        self.MajorSubsystemVersion = v_uint16()
        self.MinorSubsystemVersion = v_uint16()
        self.Win32VersionValue = v_uint32()
        self.SizeOfImage = v_uint32()
        self.SizeOfHeaders = v_uint32()
        self.CheckSum = v_uint32()
        self.Subsystem = v_uint16()
        self.DllCharacteristics = v_uint16()
        self.SizeOfStackReserve = v_uint32()
        self.SizeOfStackCommit = v_uint32()
        self.SizeOfHeapReserve = v_uint32()
        self.SizeOfHeapCommit = v_uint32()
        self.LoaderFlags = v_uint32()
        self.NumberOfRvaAndSizes = v_uint32()
        self.DataDirectory = vstruct.VArray([ IMAGE_DATA_DIRECTORY() for i in xrange(16) ])


class OWNER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwnerCount = v_uint32()


class ETHREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class FAST_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Gate = KEVENT()
        self.OldIrql = v_uint32()


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class IO_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Port = IO_RESOURCE_DESCRIPTOR()


class SECURITY_SUBJECT_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientToken = v_ptr32()
        self.ImpersonationLevel = v_uint32()
        self.PrimaryToken = v_ptr32()
        self.ProcessAuditId = v_ptr32()


class KDEVICE_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceListHead = LIST_ENTRY()
        self.Lock = v_uint32()
        self.Busy = v_uint8()
        self._pad0014 = v_bytes(size=3)


class ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.einfo = EINFO()
        self.ObjectOwner = OBJECTOWNER()
        self.FullUnique = v_uint16()
        self.Objt = v_uint8()
        self.Flags = v_uint8()
        self.pUser = v_ptr32()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.CurrentStackLocation = v_ptr32()


class CM_PARTIAL_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Revision = v_uint16()
        self.Count = v_uint32()
        self.PartialDescriptors = vstruct.VArray([ CM_PARTIAL_RESOURCE_DESCRIPTOR() for i in xrange(1) ])


class IO_SECURITY_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityQos = v_ptr32()
        self.AccessState = v_ptr32()
        self.DesiredAccess = v_uint32()
        self.FullCreateOptions = v_uint32()


class LUID_AND_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Luid = LUID()
        self.Attributes = v_uint32()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceQueueEntry = KDEVICE_QUEUE_ENTRY()
        self.Thread = v_ptr32()
        self.AuxiliaryBuffer = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.CurrentStackLocation = v_ptr32()
        self.OriginalFileObject = v_ptr32()


class DEVICE_CAPABILITIES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.DeviceD1 = v_uint32()
        self.Address = v_uint32()
        self.UINumber = v_uint32()
        self.DeviceState = vstruct.VArray([ DEVICE_POWER_STATE() for i in xrange(7) ])
        self.SystemWake = v_uint32()
        self.DeviceWake = v_uint32()
        self.D1Latency = v_uint32()
        self.D2Latency = v_uint32()
        self.D3Latency = v_uint32()


class INTERFACE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Context = v_ptr32()
        self.InterfaceReference = v_ptr32()
        self.InterfaceDereference = v_ptr32()


class SLIST_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Alignment = v_uint64()


class KTHREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReplaceIfExists = v_uint8()
        self.AdvanceOnly = v_uint8()
        self._pad0004 = v_bytes(size=2)


class IO_STATUS_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Status = v_uint32()


class IMAGE_DATA_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_uint32()
        self.Size = v_uint32()


class FILE_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceObject = v_ptr32()
        self.Vpb = v_ptr32()
        self.FsContext = v_ptr32()
        self.FsContext2 = v_ptr32()
        self.SectionObjectPointer = v_ptr32()
        self.PrivateCacheMap = v_ptr32()
        self.FinalStatus = v_uint32()
        self.RelatedFileObject = v_ptr32()
        self.LockOperation = v_uint8()
        self.DeletePending = v_uint8()
        self.ReadAccess = v_uint8()
        self.WriteAccess = v_uint8()
        self.DeleteAccess = v_uint8()
        self.SharedRead = v_uint8()
        self.SharedWrite = v_uint8()
        self.SharedDelete = v_uint8()
        self.Flags = v_uint32()
        self.FileName = UNICODE_STRING()
        self.CurrentByteOffset = LARGE_INTEGER()
        self.Waiters = v_uint32()
        self.Busy = v_uint32()
        self.LastLock = v_ptr32()
        self.Lock = KEVENT()
        self.Event = KEVENT()
        self.CompletionContext = v_ptr32()


class ERESOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemResourcesList = LIST_ENTRY()
        self.OwnerTable = v_ptr32()
        self.ActiveCount = v_uint16()
        self.Flag = v_uint16()
        self.SharedWaiters = v_ptr32()
        self.ExclusiveWaiters = v_ptr32()
        self.OwnerThreads = vstruct.VArray([ OWNER_ENTRY() for i in xrange(2) ])
        self.ContentionCount = v_uint32()
        self.NumberOfSharedWaiters = v_uint16()
        self.NumberOfExclusiveWaiters = v_uint16()
        self.Address = v_ptr32()
        self.SpinLock = v_uint32()


class FILE_NETWORK_OPEN_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CreationTime = LARGE_INTEGER()
        self.LastAccessTime = LARGE_INTEGER()
        self.LastWriteTime = LARGE_INTEGER()
        self.ChangeTime = LARGE_INTEGER()
        self.AllocationSize = LARGE_INTEGER()
        self.EndOfFile = LARGE_INTEGER()
        self.FileAttributes = v_uint32()
        self._pad0038 = v_bytes(size=4)


class GENERAL_LOOKASIDE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LastAllocateMisses = v_uint32()


class OBJECTOWNER_S(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = v_uint32()


class OBJECT_HANDLE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleAttributes = v_uint32()
        self.GrantedAccess = v_uint32()


class tagVSTATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.fl = v_uint32()
        self.bSystemStable = v_uint32()
        self.ulRandomSeed = v_uint32()
        self.ulFailureMask = v_uint32()
        self.ulDebugLevel = v_uint32()
        self.hsemPoolTracker = v_ptr32()
        self.lePoolTrackerHead = LIST_ENTRY()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Overlay = IRP()
        self._pad0030 = v_bytes(size=8)


class INITIAL_PRIVILEGE_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PrivilegeCount = v_uint32()
        self.Control = v_uint32()
        self.Privilege = vstruct.VArray([ LUID_AND_ATTRIBUTES() for i in xrange(3) ])


class GENERAL_LOOKASIDE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = SLIST_HEADER()
        self.Depth = v_uint16()
        self.MaximumDepth = v_uint16()
        self.TotalAllocates = v_uint32()
        self.AllocateMisses = v_uint32()
        self.TotalFrees = v_uint32()
        self.FreeMisses = v_uint32()
        self.Type = v_uint32()
        self.Tag = v_uint32()
        self.Size = v_uint32()
        self.Allocate = v_ptr32()
        self.Free = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.LastTotalAllocates = v_uint32()
        self.LastAllocateMisses = v_uint32()
        self.Future = vstruct.VArray([ v_uint32() for i in xrange(2) ])


class ULARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Generic = CM_PARTIAL_RESOURCE_DESCRIPTOR()


class OBJECT_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashBuckets = vstruct.VArray([ v_ptr32() for i in xrange(37) ])
        self.Lock = EX_PUSH_LOCK()
        self.DeviceMap = v_ptr32()
        self.SessionId = v_uint32()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Inserted = v_uint8()


class DEVOBJ_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceObject = v_ptr32()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CurrentStackLocation = v_ptr32()


class POWER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemState = v_uint32()


class UNICODE_STRING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.MaximumLength = v_uint16()
        self.Buffer = v_ptr32()


class GDIHandleBitFields(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Index = v_uint32()


class ACCESS_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OperationID = LUID()
        self.SecurityEvaluated = v_uint8()
        self.GenerateAudit = v_uint8()
        self.GenerateOnClose = v_uint8()
        self.PrivilegesAllocated = v_uint8()
        self.Flags = v_uint32()
        self.RemainingDesiredAccess = v_uint32()
        self.PreviouslyGrantedAccess = v_uint32()
        self.OriginalDesiredAccess = v_uint32()
        self.SubjectSecurityContext = SECURITY_SUBJECT_CONTEXT()
        self.SecurityDescriptor = v_ptr32()
        self.AuxData = v_ptr32()
        self.Privileges = ACCESS_STATE()
        self.AuditPrivileges = v_uint8()
        self._pad0064 = v_bytes(size=3)
        self.ObjectName = UNICODE_STRING()
        self.ObjectTypeName = UNICODE_STRING()


class OBJECT_DIRECTORY_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class FILE_STANDARD_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocationSize = LARGE_INTEGER()
        self.EndOfFile = LARGE_INTEGER()
        self.NumberOfLinks = v_uint32()
        self.DeletePending = v_uint8()
        self.Directory = v_uint8()
        self._pad0018 = v_bytes(size=2)


class KAPC(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.SpareByte0 = v_uint8()
        self.Size = v_uint8()
        self.SpareByte1 = v_uint8()
        self.SpareLong0 = v_uint32()
        self.Thread = v_ptr32()
        self.ApcListEntry = LIST_ENTRY()
        self.KernelRoutine = v_ptr32()
        self.RundownRoutine = v_ptr32()
        self.NormalRoutine = v_ptr32()
        self.NormalContext = v_ptr32()
        self.SystemArgument1 = v_ptr32()
        self.SystemArgument2 = v_ptr32()
        self.ApcStateIndex = v_uint8()
        self.ApcMode = v_uint8()
        self.Inserted = v_uint8()
        self._pad0030 = v_bytes(size=1)


class WAIT_CONTEXT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WaitQueueEntry = KDEVICE_QUEUE_ENTRY()
        self.DeviceRoutine = v_ptr32()
        self.DeviceContext = v_ptr32()
        self.NumberOfMapRegisters = v_uint32()
        self.DeviceObject = v_ptr32()
        self.CurrentIrp = v_ptr32()
        self.BufferChainingDpc = v_ptr32()


class OBJECT_HEADER_NAME_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Directory = v_ptr32()
        self.Name = UNICODE_STRING()
        self.QueryReferences = v_uint32()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Absolute = v_uint8()
        self.Size = v_uint8()
        self.Inserted = v_uint8()


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class MDL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Size = v_uint16()
        self.MdlFlags = v_uint16()
        self.Process = v_ptr32()
        self.MappedSystemVa = v_ptr32()
        self.StartVa = v_ptr32()
        self.ByteCount = v_uint32()
        self.ByteOffset = v_uint32()


class W32THREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.pEThread = v_ptr32()
        self.RefCount = v_uint32()
        self.ptlW32 = v_ptr32()
        self.pgdiDcattr = v_ptr32()
        self.pgdiBrushAttr = v_ptr32()
        self.pUMPDObjs = v_ptr32()
        self.pUMPDHeap = v_ptr32()
        self.pUMPDObj = v_ptr32()
        self.GdiTmpAllocList = LIST_ENTRY()


class KDPC(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Importance = v_uint8()
        self.Number = v_uint8()
        self.Expedite = v_uint8()
        self.DpcListEntry = LIST_ENTRY()
        self.DeferredRoutine = v_ptr32()
        self.DeferredContext = v_ptr32()
        self.SystemArgument1 = v_ptr32()
        self.SystemArgument2 = v_ptr32()
        self.DpcData = v_ptr32()


class OWNER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwnerThread = v_uint32()
        self.OwnerCount = v_uint32()


class KEVENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class KSEMAPHORE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.Limit = v_uint32()


class PAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = FAST_MUTEX()


class OBJECT_TYPE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mutex = ERESOURCE()
        self.TypeList = LIST_ENTRY()
        self.Name = UNICODE_STRING()
        self.DefaultObject = v_ptr32()
        self.Index = v_uint32()
        self.TotalNumberOfObjects = v_uint32()
        self.TotalNumberOfHandles = v_uint32()
        self.HighWaterNumberOfObjects = v_uint32()
        self.HighWaterNumberOfHandles = v_uint32()
        self.TypeInfo = OBJECT_TYPE_INITIALIZER()
        self.Key = v_uint32()
        self.ObjectLocks = vstruct.VArray([ ERESOURCE() for i in xrange(4) ])


class DEVICE_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self._pad0028 = v_bytes(size=32)


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Absolute = v_uint8()
        self.Size = v_uint8()
        self.Inserted = v_uint8()
        self.SignalState = v_uint32()
        self.WaitListHead = LIST_ENTRY()


class QUAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UseThisFieldToCopy = v_uint64()


class HOBJ(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.unused = v_uint32()


class IO_TIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class OBJECT_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ObjectCreateInfo = v_ptr32()


class OBJECT_TYPE_INITIALIZER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.UseDefaultObject = v_uint8()
        self.CaseInsensitive = v_uint8()
        self.InvalidAttributes = v_uint32()
        self.GenericMapping = GENERIC_MAPPING()
        self.ValidAccessMask = v_uint32()
        self.SecurityRequired = v_uint8()
        self.MaintainHandleCount = v_uint8()
        self.MaintainTypeList = v_uint8()
        self._pad0020 = v_bytes(size=1)
        self.PoolType = v_uint32()
        self.DefaultPagedPoolCharge = v_uint32()
        self.DefaultNonPagedPoolCharge = v_uint32()
        self.DumpProcedure = v_ptr32()
        self.OpenProcedure = v_ptr32()
        self.CloseProcedure = v_ptr32()
        self.DeleteProcedure = v_ptr32()
        self.ParseProcedure = v_ptr32()
        self.SecurityProcedure = v_ptr32()
        self.QueryNameProcedure = v_ptr32()
        self.OkayToCloseProcedure = v_ptr32()


class SCSI_REQUEST_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReplaceIfExists = v_uint8()
        self.AdvanceOnly = v_uint8()


class FILE_BASIC_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CreationTime = LARGE_INTEGER()
        self.LastAccessTime = LARGE_INTEGER()
        self.LastWriteTime = LARGE_INTEGER()
        self.ChangeTime = LARGE_INTEGER()
        self.FileAttributes = v_uint32()
        self._pad0028 = v_bytes(size=4)


class DEVICE_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.ReferenceCount = v_uint32()
        self.DriverObject = v_ptr32()
        self.NextDevice = v_ptr32()
        self.AttachedDevice = v_ptr32()
        self.CurrentIrp = v_ptr32()
        self.Timer = v_ptr32()
        self.Flags = v_uint32()
        self.Characteristics = v_uint32()
        self.Vpb = v_ptr32()
        self.DeviceExtension = v_ptr32()
        self.DeviceType = v_uint32()
        self.StackSize = v_uint8()
        self._pad0034 = v_bytes(size=3)
        self.Queue = DEVICE_OBJECT()
        self.AlignmentRequirement = v_uint32()
        self.DeviceQueue = KDEVICE_QUEUE()
        self.Dpc = KDPC()
        self.ActiveThreadCount = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.DeviceLock = KEVENT()
        self.SectorSize = v_uint16()
        self.Spare1 = v_uint16()
        self.DeviceObjectExtension = v_ptr32()
        self.Reserved = v_ptr32()


class LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_ptr32()
        self.Blink = v_ptr32()


class EINFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.pobj = v_ptr32()


class SECURITY_QUALITY_OF_SERVICE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.ImpersonationLevel = v_uint32()
        self.ContextTrackingMode = v_uint8()
        self.EffectiveOnly = v_uint8()
        self._pad000c = v_bytes(size=2)


class COMPRESSED_DATA_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CompressionFormatAndEngine = v_uint16()
        self.CompressionUnitShift = v_uint8()
        self.ChunkShift = v_uint8()
        self.ClusterShift = v_uint8()
        self.Reserved = v_uint8()
        self.NumberOfChunks = v_uint16()
        self.CompressedChunkSizes = vstruct.VArray([ v_uint32() for i in xrange(1) ])


class BASEOBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.hHmgr = v_ptr32()
        self.ulShareCount = v_uint32()
        self.cExclusiveLock = v_uint16()
        self.BaseFlags = v_uint16()
        self.Tid = v_ptr32()


class OBJECT_CREATE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class HSEMAPHORE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.unused = v_uint32()


class LUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Create = IO_STACK_LOCATION()


class OBJECT_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PointerCount = v_uint32()
        self.HandleCount = v_uint32()
        self.Type = v_ptr32()
        self.NameInfoOffset = v_uint8()
        self.HandleInfoOffset = v_uint8()
        self.QuotaInfoOffset = v_uint8()
        self.Flags = v_uint8()
        self.ObjectCreateInfo = v_ptr32()
        self.SecurityDescriptor = v_ptr32()
        self.Body = QUAD()


class LARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class tagPOOLRECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExtraData = v_ptr32()
        self.size = v_uint32()
        self.trace = vstruct.VArray([ v_ptr32() for i in xrange(6) ])


class QUAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UseThisFieldToCopy = v_uint64()


class GUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data1 = v_uint32()
        self.Data2 = v_uint16()
        self.Data3 = v_uint16()
        self.Data4 = vstruct.VArray([ v_uint8() for i in xrange(8) ])


class OBJECT_DUMP_CONTROL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Stream = v_ptr32()
        self.Detail = v_uint32()


class NPAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = v_uint32()
        self._pad0050 = v_bytes(size=4)


class ULARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class OBJECTOWNER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Share = OBJECTOWNER_S()


class ACCESS_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InitialPrivilegeSet = INITIAL_PRIVILEGE_SET()


class TL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.next = v_ptr32()
        self.pobj = v_ptr32()
        self.pfnFree = v_ptr32()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()


class VPB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.Flags = v_uint16()
        self.VolumeLabelLength = v_uint16()
        self.DeviceObject = v_ptr32()
        self.RealDevice = v_ptr32()
        self.SerialNumber = v_uint32()
        self.ReferenceCount = v_uint32()
        self.VolumeLabel = vstruct.VArray([ v_uint16() for i in xrange(32) ])


class ERESOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Address = v_ptr32()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorFunction = v_uint8()
        self.MinorFunction = v_uint8()
        self.Flags = v_uint8()
        self.Control = v_uint8()
        self.Parameters = IO_STACK_LOCATION()
        self.DeviceObject = v_ptr32()
        self.FileObject = v_ptr32()
        self.CompletionRoutine = v_ptr32()
        self.Context = v_ptr32()


class IO_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Priority = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class GENERIC_MAPPING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.GenericRead = v_uint32()
        self.GenericWrite = v_uint32()
        self.GenericExecute = v_uint32()
        self.GenericAll = v_uint32()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.MdlAddress = v_ptr32()
        self.Flags = v_uint32()
        self.AssociatedIrp = IRP()
        self.ThreadListEntry = LIST_ENTRY()
        self.IoStatus = IO_STATUS_BLOCK()
        self.RequestorMode = v_uint8()
        self.PendingReturned = v_uint8()
        self.StackCount = v_uint8()
        self.CurrentLocation = v_uint8()
        self.Cancel = v_uint8()
        self.CancelIrql = v_uint8()
        self.ApcEnvironment = v_uint8()
        self.AllocationFlags = v_uint8()
        self.UserIosb = v_ptr32()
        self.UserEvent = v_ptr32()
        self.Overlay = IRP()
        self.CancelRoutine = v_ptr32()
        self.UserBuffer = v_ptr32()
        self.Tail = IRP()


class OBJECT_NAME_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name = UNICODE_STRING()


class IO_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Revision = v_uint16()
        self.Count = v_uint32()
        self.Descriptors = vstruct.VArray([ IO_RESOURCE_DESCRIPTOR() for i in xrange(1) ])


class DRIVER_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceObject = v_ptr32()
        self.Flags = v_uint32()
        self.DriverStart = v_ptr32()
        self.DriverSize = v_uint32()
        self.DriverSection = v_ptr32()
        self.DriverExtension = v_ptr32()
        self.DriverName = UNICODE_STRING()
        self.HardwareDatabase = v_ptr32()
        self.FastIoDispatch = v_ptr32()
        self.DriverInit = v_ptr32()
        self.DriverStartIo = v_ptr32()
        self.DriverUnload = v_ptr32()
        self.MajorFunction = vstruct.VArray([ v_ptr32() for i in xrange(28) ])


class IO_STATUS_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Status = v_uint32()
        self.Information = v_uint32()


class PRIVILEGE_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PrivilegeCount = v_uint32()
        self.Control = v_uint32()
        self.Privilege = vstruct.VArray([ LUID_AND_ATTRIBUTES() for i in xrange(1) ])


class CM_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.List = vstruct.VArray([ CM_FULL_RESOURCE_DESCRIPTOR() for i in xrange(1) ])


class EPROCESS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class LIST_ENTRY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()
        self.Blink = v_uint32()


class tagVERIFIERTRACKHDR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.list = LIST_ENTRY()
        self.ulSize = v_uint32()
        self.ulTag = v_uint32()


class SINGLE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()


class POWER_SEQUENCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SequenceD1 = v_uint32()
        self.SequenceD2 = v_uint32()
        self.SequenceD3 = v_uint32()


class IO_COMPLETION_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Port = v_ptr32()
        self.Key = v_ptr32()


class DRIVER_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DriverObject = v_ptr32()
        self.AddDevice = v_ptr32()
        self.Count = v_uint32()
        self.ServiceKeyName = UNICODE_STRING()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Absolute = v_uint8()
        self.Size = v_uint8()
        self.Inserted = v_uint8()


class KDEVICE_QUEUE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceListEntry = LIST_ENTRY()
        self.SortKey = v_uint32()
        self.Inserted = v_uint8()
        self._pad0010 = v_bytes(size=3)


class LIST_ENTRY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint64()
        self.Blink = v_uint64()


class IO_RESOURCE_REQUIREMENTS_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListSize = v_uint32()
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.SlotNumber = v_uint32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in xrange(3) ])
        self.AlternativeLists = v_uint32()
        self.List = vstruct.VArray([ IO_RESOURCE_LIST() for i in xrange(1) ])


class SLIST_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = SINGLE_LIST_ENTRY()
        self.Depth = v_uint16()
        self.Sequence = v_uint16()


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Flags = v_uint16()
        self.u = CM_PARTIAL_RESOURCE_DESCRIPTOR()



