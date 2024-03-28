# -*- coding: utf8 -*-
# Version: 5.2
# Architecture: i386
# CompanyName: Microsoft Corporation
# FileDescription: NT Layer DLL
# FileVersion: 5.2.3790.4937 (srv03_sp2_gdr.111121-0236)
# InternalName: ntdll.dll
# LegalCopyright:  Microsoft Corporation. All rights reserved.
# OriginalFilename: ntdll.dll
# ProductName: Microsoft Windows Operating System
# ProductVersion: 5.2.3790.4937
# Translation: 78644233
import vstruct
from vstruct.primitives import *

REG_NOTIFY_CLASS = v_enum()
REG_NOTIFY_CLASS.RegNtDeleteKey = 0
REG_NOTIFY_CLASS.RegNtPreDeleteKey = 0
REG_NOTIFY_CLASS.RegNtSetValueKey = 1
REG_NOTIFY_CLASS.RegNtPreSetValueKey = 1
REG_NOTIFY_CLASS.RegNtDeleteValueKey = 2
REG_NOTIFY_CLASS.RegNtPreDeleteValueKey = 2
REG_NOTIFY_CLASS.RegNtSetInformationKey = 3
REG_NOTIFY_CLASS.RegNtPreSetInformationKey = 3
REG_NOTIFY_CLASS.RegNtRenameKey = 4
REG_NOTIFY_CLASS.RegNtPreRenameKey = 4
REG_NOTIFY_CLASS.RegNtEnumerateKey = 5
REG_NOTIFY_CLASS.RegNtPreEnumerateKey = 5
REG_NOTIFY_CLASS.RegNtEnumerateValueKey = 6
REG_NOTIFY_CLASS.RegNtPreEnumerateValueKey = 6
REG_NOTIFY_CLASS.RegNtQueryKey = 7
REG_NOTIFY_CLASS.RegNtPreQueryKey = 7
REG_NOTIFY_CLASS.RegNtQueryValueKey = 8
REG_NOTIFY_CLASS.RegNtPreQueryValueKey = 8
REG_NOTIFY_CLASS.RegNtQueryMultipleValueKey = 9
REG_NOTIFY_CLASS.RegNtPreQueryMultipleValueKey = 9
REG_NOTIFY_CLASS.RegNtPreCreateKey = 10
REG_NOTIFY_CLASS.RegNtPostCreateKey = 11
REG_NOTIFY_CLASS.RegNtPreOpenKey = 12
REG_NOTIFY_CLASS.RegNtPostOpenKey = 13
REG_NOTIFY_CLASS.RegNtKeyHandleClose = 14
REG_NOTIFY_CLASS.RegNtPreKeyHandleClose = 14
REG_NOTIFY_CLASS.RegNtPostDeleteKey = 15
REG_NOTIFY_CLASS.RegNtPostSetValueKey = 16
REG_NOTIFY_CLASS.RegNtPostDeleteValueKey = 17
REG_NOTIFY_CLASS.RegNtPostSetInformationKey = 18
REG_NOTIFY_CLASS.RegNtPostRenameKey = 19
REG_NOTIFY_CLASS.RegNtPostEnumerateKey = 20
REG_NOTIFY_CLASS.RegNtPostEnumerateValueKey = 21
REG_NOTIFY_CLASS.RegNtPostQueryKey = 22
REG_NOTIFY_CLASS.RegNtPostQueryValueKey = 23
REG_NOTIFY_CLASS.RegNtPostQueryMultipleValueKey = 24
REG_NOTIFY_CLASS.RegNtPostKeyHandleClose = 25
REG_NOTIFY_CLASS.RegNtPreCreateKeyEx = 26
REG_NOTIFY_CLASS.RegNtPostCreateKeyEx = 27
REG_NOTIFY_CLASS.RegNtPreOpenKeyEx = 28
REG_NOTIFY_CLASS.RegNtPostOpenKeyEx = 29


DEVICE_RELATION_TYPE = v_enum()
DEVICE_RELATION_TYPE.BusRelations = 0
DEVICE_RELATION_TYPE.EjectionRelations = 1
DEVICE_RELATION_TYPE.PowerRelations = 2
DEVICE_RELATION_TYPE.RemovalRelations = 3
DEVICE_RELATION_TYPE.TargetDeviceRelation = 4
DEVICE_RELATION_TYPE.SingleBusRelations = 5


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


BUS_QUERY_ID_TYPE = v_enum()
BUS_QUERY_ID_TYPE.BusQueryDeviceID = 0
BUS_QUERY_ID_TYPE.BusQueryHardwareIDs = 1
BUS_QUERY_ID_TYPE.BusQueryCompatibleIDs = 2
BUS_QUERY_ID_TYPE.BusQueryInstanceID = 3
BUS_QUERY_ID_TYPE.BusQueryDeviceSerialNumber = 4


MMSYSTEM_PTE_POOL_TYPE = v_enum()
MMSYSTEM_PTE_POOL_TYPE.SystemPteSpace = 0
MMSYSTEM_PTE_POOL_TYPE.NonPagedPoolExpansion = 1
MMSYSTEM_PTE_POOL_TYPE.MaximumPtePoolTypes = 2


KOBJECTS = v_enum()
KOBJECTS.EventNotificationObject = 0
KOBJECTS.EventSynchronizationObject = 1
KOBJECTS.MutantObject = 2
KOBJECTS.ProcessObject = 3
KOBJECTS.QueueObject = 4
KOBJECTS.SemaphoreObject = 5
KOBJECTS.ThreadObject = 6
KOBJECTS.GateObject = 7
KOBJECTS.TimerNotificationObject = 8
KOBJECTS.TimerSynchronizationObject = 9
KOBJECTS.Spare2Object = 10
KOBJECTS.Spare3Object = 11
KOBJECTS.Spare4Object = 12
KOBJECTS.Spare5Object = 13
KOBJECTS.Spare6Object = 14
KOBJECTS.Spare7Object = 15
KOBJECTS.Spare8Object = 16
KOBJECTS.Spare9Object = 17
KOBJECTS.ApcObject = 18
KOBJECTS.DpcObject = 19
KOBJECTS.DeviceQueueObject = 20
KOBJECTS.EventPairObject = 21
KOBJECTS.InterruptObject = 22
KOBJECTS.ProfileObject = 23
KOBJECTS.ThreadedDpcObject = 24
KOBJECTS.MaximumKernelObject = 25


NT_PRODUCT_TYPE = v_enum()
NT_PRODUCT_TYPE.NtProductWinNt = 1
NT_PRODUCT_TYPE.NtProductLanManNt = 2
NT_PRODUCT_TYPE.NtProductServer = 3


DEVICE_POWER_STATE = v_enum()
DEVICE_POWER_STATE.PowerDeviceUnspecified = 0
DEVICE_POWER_STATE.PowerDeviceD0 = 1
DEVICE_POWER_STATE.PowerDeviceD1 = 2
DEVICE_POWER_STATE.PowerDeviceD2 = 3
DEVICE_POWER_STATE.PowerDeviceD3 = 4
DEVICE_POWER_STATE.PowerDeviceMaximum = 5


RTL_GENERIC_COMPARE_RESULTS = v_enum()
RTL_GENERIC_COMPARE_RESULTS.GenericLessThan = 0
RTL_GENERIC_COMPARE_RESULTS.GenericGreaterThan = 1
RTL_GENERIC_COMPARE_RESULTS.GenericEqual = 2


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


FS_FILTER_SECTION_SYNC_TYPE = v_enum()
FS_FILTER_SECTION_SYNC_TYPE.SyncTypeOther = 0
FS_FILTER_SECTION_SYNC_TYPE.SyncTypeCreateSection = 1


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


LSA_FOREST_TRUST_RECORD_TYPE = v_enum()
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustTopLevelName = 0
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustTopLevelNameEx = 1
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustDomainInfo = 2
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustRecordTypeLast = 2


IO_ALLOCATION_ACTION = v_enum()
IO_ALLOCATION_ACTION.KeepObject = 1
IO_ALLOCATION_ACTION.DeallocateObject = 2
IO_ALLOCATION_ACTION.DeallocateObjectKeepRegisters = 3


EXCEPTION_DISPOSITION = v_enum()
EXCEPTION_DISPOSITION.ExceptionContinueExecution = 0
EXCEPTION_DISPOSITION.ExceptionContinueSearch = 1
EXCEPTION_DISPOSITION.ExceptionNestedException = 2
EXCEPTION_DISPOSITION.ExceptionCollidedUnwind = 3


SECURITY_IMPERSONATION_LEVEL = v_enum()
SECURITY_IMPERSONATION_LEVEL.SecurityAnonymous = 0
SECURITY_IMPERSONATION_LEVEL.SecurityIdentification = 1
SECURITY_IMPERSONATION_LEVEL.SecurityImpersonation = 2
SECURITY_IMPERSONATION_LEVEL.SecurityDelegation = 3


PF_SCENARIO_TYPE = v_enum()
PF_SCENARIO_TYPE.PfApplicationLaunchScenarioType = 0
PF_SCENARIO_TYPE.PfSystemBootScenarioType = 1
PF_SCENARIO_TYPE.PfMaxScenarioType = 2


SECURITY_OPERATION_CODE = v_enum()
SECURITY_OPERATION_CODE.SetSecurityDescriptor = 0
SECURITY_OPERATION_CODE.QuerySecurityDescriptor = 1
SECURITY_OPERATION_CODE.DeleteSecurityDescriptor = 2
SECURITY_OPERATION_CODE.AssignSecurityDescriptor = 3


PP_NPAGED_LOOKASIDE_NUMBER = v_enum()
PP_NPAGED_LOOKASIDE_NUMBER.LookasideSmallIrpList = 0
PP_NPAGED_LOOKASIDE_NUMBER.LookasideLargeIrpList = 1
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMdlList = 2
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCreateInfoList = 3
PP_NPAGED_LOOKASIDE_NUMBER.LookasideNameBufferList = 4
PP_NPAGED_LOOKASIDE_NUMBER.LookasideTwilightList = 5
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCompletionList = 6
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMaximumList = 7


KDPC_IMPORTANCE = v_enum()
KDPC_IMPORTANCE.LowImportance = 0
KDPC_IMPORTANCE.MediumImportance = 1
KDPC_IMPORTANCE.HighImportance = 2


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


ALTERNATIVE_ARCHITECTURE_TYPE = v_enum()
ALTERNATIVE_ARCHITECTURE_TYPE.StandardDesign = 0
ALTERNATIVE_ARCHITECTURE_TYPE.NEC98x86 = 1
ALTERNATIVE_ARCHITECTURE_TYPE.EndAlternatives = 2


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


PS_QUOTA_TYPE = v_enum()
PS_QUOTA_TYPE.PsNonPagedPool = 0
PS_QUOTA_TYPE.PsPagedPool = 1
PS_QUOTA_TYPE.PsPageFile = 2
PS_QUOTA_TYPE.PsQuotaTypes = 3


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


class KEXECUTE_OPTIONS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExecuteDisable = v_uint8()


class MM_AVL_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BalancedRoot = MMADDRESS_NODE()
        self.DepthOfTree = v_uint32()
        self.NodeHint = v_ptr32()
        self.NodeFreeHint = v_ptr32()


class KPRCB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinorVersion = v_uint16()
        self.MajorVersion = v_uint16()
        self.CurrentThread = v_ptr32()
        self.NextThread = v_ptr32()
        self.IdleThread = v_ptr32()
        self.Number = v_uint8()
        self.Reserved = v_uint8()
        self.BuildType = v_uint16()
        self.SetMember = v_uint32()
        self.CpuType = v_uint8()
        self.CpuID = v_uint8()
        self.CpuStep = v_uint16()
        self.ProcessorState = KPROCESSOR_STATE()
        self.KernelReserved = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.HalReserved = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.PrcbPad0 = vstruct.VArray([ v_uint8() for i in range(92) ])
        self.LockQueue = vstruct.VArray([ KSPIN_LOCK_QUEUE() for i in range(33) ])
        self.NpxThread = v_ptr32()
        self.InterruptCount = v_uint32()
        self.KernelTime = v_uint32()
        self.UserTime = v_uint32()
        self.DpcTime = v_uint32()
        self.DebugDpcTime = v_uint32()
        self.InterruptTime = v_uint32()
        self.AdjustDpcThreshold = v_uint32()
        self.PageColor = v_uint32()
        self.SkipTick = v_uint8()
        self.DebuggerSavedIRQL = v_uint8()
        self.NodeColor = v_uint8()
        self.Spare1 = v_uint8()
        self.NodeShiftedColor = v_uint32()
        self.ParentNode = v_ptr32()
        self.MultiThreadProcessorSet = v_uint32()
        self.MultiThreadSetMaster = v_ptr32()
        self.SecondaryColorMask = v_uint32()
        self.Sleeping = v_uint32()
        self.CcFastReadNoWait = v_uint32()
        self.CcFastReadWait = v_uint32()
        self.CcFastReadNotPossible = v_uint32()
        self.CcCopyReadNoWait = v_uint32()
        self.CcCopyReadWait = v_uint32()
        self.CcCopyReadNoWaitMiss = v_uint32()
        self.KeAlignmentFixupCount = v_uint32()
        self.SpareCounter0 = v_uint32()
        self.KeDcacheFlushCount = v_uint32()
        self.KeExceptionDispatchCount = v_uint32()
        self.KeFirstLevelTbFills = v_uint32()
        self.KeFloatingEmulationCount = v_uint32()
        self.KeIcacheFlushCount = v_uint32()
        self.KeSecondLevelTbFills = v_uint32()
        self.KeSystemCalls = v_uint32()
        self.IoReadOperationCount = v_uint32()
        self.IoWriteOperationCount = v_uint32()
        self.IoOtherOperationCount = v_uint32()
        self.IoReadTransferCount = LARGE_INTEGER()
        self.IoWriteTransferCount = LARGE_INTEGER()
        self.IoOtherTransferCount = LARGE_INTEGER()
        self.SpareCounter1 = vstruct.VArray([ v_uint32() for i in range(8) ])
        self.PPLookasideList = vstruct.VArray([ PP_LOOKASIDE_LIST() for i in range(16) ])
        self.PPNPagedLookasideList = vstruct.VArray([ PP_LOOKASIDE_LIST() for i in range(32) ])
        self.PPPagedLookasideList = vstruct.VArray([ PP_LOOKASIDE_LIST() for i in range(32) ])
        self.PacketBarrier = v_uint32()
        self.ReverseStall = v_uint32()
        self.IpiFrame = v_ptr32()
        self.PrcbPad2 = vstruct.VArray([ v_uint8() for i in range(52) ])
        self.CurrentPacket = vstruct.VArray([ v_ptr32() for i in range(3) ])
        self.TargetSet = v_uint32()
        self.WorkerRoutine = v_ptr32()
        self.IpiFrozen = v_uint32()
        self.PrcbPad3 = vstruct.VArray([ v_uint8() for i in range(40) ])
        self.RequestSummary = v_uint32()
        self.SignalDone = v_ptr32()
        self.PrcbPad4 = vstruct.VArray([ v_uint8() for i in range(56) ])
        self.DpcData = vstruct.VArray([ KDPC_DATA() for i in range(2) ])
        self.DpcStack = v_ptr32()
        self.MaximumDpcQueueDepth = v_uint32()
        self.DpcRequestRate = v_uint32()
        self.MinimumDpcRate = v_uint32()
        self.DpcInterruptRequested = v_uint8()
        self.DpcThreadRequested = v_uint8()
        self.DpcRoutineActive = v_uint8()
        self.DpcThreadActive = v_uint8()
        self.PrcbLock = v_uint32()
        self.DpcLastCount = v_uint32()
        self.TimerHand = v_uint32()
        self.TimerRequest = v_uint32()
        self.DpcThread = v_ptr32()
        self.DpcEvent = KEVENT()
        self.ThreadDpcEnable = v_uint8()
        self.QuantumEnd = v_uint8()
        self.PrcbPad50 = v_uint8()
        self.IdleSchedule = v_uint8()
        self.DpcSetEventRequest = v_uint32()
        self.PrcbPad5 = vstruct.VArray([ v_uint8() for i in range(18) ])
        self._pad099c = v_bytes(size=2)
        self.TickOffset = v_uint32()
        self.CallDpc = KDPC()
        self.PrcbPad7 = vstruct.VArray([ v_uint32() for i in range(8) ])
        self.WaitListHead = LIST_ENTRY()
        self.ReadySummary = v_uint32()
        self.QueueIndex = v_uint32()
        self.DispatcherReadyListHead = vstruct.VArray([ LIST_ENTRY() for i in range(32) ])
        self.DeferredReadyListHead = SINGLE_LIST_ENTRY()
        self.PrcbPad72 = vstruct.VArray([ v_uint32() for i in range(11) ])
        self.ChainedInterruptList = v_ptr32()
        self.LookasideIrpFloat = v_uint32()
        self.MmPageFaultCount = v_uint32()
        self.MmCopyOnWriteCount = v_uint32()
        self.MmTransitionCount = v_uint32()
        self.MmCacheTransitionCount = v_uint32()
        self.MmDemandZeroCount = v_uint32()
        self.MmPageReadCount = v_uint32()
        self.MmPageReadIoCount = v_uint32()
        self.MmCacheReadCount = v_uint32()
        self.MmCacheIoCount = v_uint32()
        self.MmDirtyPagesWriteCount = v_uint32()
        self.MmDirtyWriteIoCount = v_uint32()
        self.MmMappedPagesWriteCount = v_uint32()
        self.MmMappedWriteIoCount = v_uint32()
        self.SpareFields0 = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.VendorString = vstruct.VArray([ v_uint8() for i in range(13) ])
        self.InitialApicId = v_uint8()
        self.LogicalProcessorsPerPhysicalProcessor = v_uint8()
        self._pad0b70 = v_bytes(size=1)
        self.MHz = v_uint32()
        self.FeatureBits = v_uint32()
        self.UpdateSignature = LARGE_INTEGER()
        self.IsrTime = v_uint64()
        self.SpareField1 = v_uint64()
        self.NpxSaveArea = FX_SAVE_AREA()
        self.PowerState = PROCESSOR_POWER_STATE()


class _unnamed_6182(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = v_uint8()


class OBJECT_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.RootDirectory = v_ptr32()
        self.ObjectName = v_ptr32()
        self.Attributes = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.SecurityQualityOfService = v_ptr32()


class IO_COUNTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReadOperationCount = v_uint64()
        self.WriteOperationCount = v_uint64()
        self.OtherOperationCount = v_uint64()
        self.ReadTransferCount = v_uint64()
        self.WriteTransferCount = v_uint64()
        self.OtherTransferCount = v_uint64()


class KSYSTEM_TIME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.High1Time = v_uint32()
        self.High2Time = v_uint32()


class CM_FULL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.PartialResourceList = CM_PARTIAL_RESOURCE_LIST()


class EXCEPTION_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_ptr32()
        self.ExceptionAddress = v_ptr32()
        self.NumberParameters = v_uint32()
        self.ExceptionInformation = vstruct.VArray([ v_uint32() for i in range(15) ])


class _unnamed_6019(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileName = v_ptr32()
        self.FileInformationClass = v_uint32()
        self.FileIndex = v_uint32()


class _unnamed_4917(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Balance = v_uint32()


class PS_JOB_TOKEN_FILTER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CapturedSidCount = v_uint32()
        self.CapturedSids = v_ptr32()
        self.CapturedSidsLength = v_uint32()
        self.CapturedGroupCount = v_uint32()
        self.CapturedGroups = v_ptr32()
        self.CapturedGroupsLength = v_uint32()
        self.CapturedPrivilegeCount = v_uint32()
        self.CapturedPrivileges = v_ptr32()
        self.CapturedPrivilegesLength = v_uint32()


class _unnamed_6056(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FsInformationClass = v_uint32()


class KSPIN_LOCK_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Lock = v_ptr32()


class _unnamed_6043(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()


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


class FS_FILTER_CALLBACKS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfFsFilterCallbacks = v_uint32()
        self.Reserved = v_uint32()
        self.PreAcquireForSectionSynchronization = v_ptr32()
        self.PostAcquireForSectionSynchronization = v_ptr32()
        self.PreReleaseForSectionSynchronization = v_ptr32()
        self.PostReleaseForSectionSynchronization = v_ptr32()
        self.PreAcquireForCcFlush = v_ptr32()
        self.PostAcquireForCcFlush = v_ptr32()
        self.PreReleaseForCcFlush = v_ptr32()
        self.PostReleaseForCcFlush = v_ptr32()
        self.PreAcquireForModifiedPageWriter = v_ptr32()
        self.PostAcquireForModifiedPageWriter = v_ptr32()
        self.PreReleaseForModifiedPageWriter = v_ptr32()
        self.PostReleaseForModifiedPageWriter = v_ptr32()


class _unnamed_6203(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InPath = v_uint8()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.Type = v_uint32()


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
        self.u = _unnamed_6407()


class EX_PUSH_LOCK_CACHE_AWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locks = vstruct.VArray([ v_ptr32() for i in range(32) ])


class MMWSL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class KTSS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Backlink = v_uint16()
        self.Reserved0 = v_uint16()
        self.Esp0 = v_uint32()
        self.Ss0 = v_uint16()
        self.Reserved1 = v_uint16()
        self.NotUsed1 = vstruct.VArray([ v_uint32() for i in range(4) ])
        self.CR3 = v_uint32()
        self.Eip = v_uint32()
        self.EFlags = v_uint32()
        self.Eax = v_uint32()
        self.Ecx = v_uint32()
        self.Edx = v_uint32()
        self.Ebx = v_uint32()
        self.Esp = v_uint32()
        self.Ebp = v_uint32()
        self.Esi = v_uint32()
        self.Edi = v_uint32()
        self.Es = v_uint16()
        self.Reserved2 = v_uint16()
        self.Cs = v_uint16()
        self.Reserved3 = v_uint16()
        self.Ss = v_uint16()
        self.Reserved4 = v_uint16()
        self.Ds = v_uint16()
        self.Reserved5 = v_uint16()
        self.Fs = v_uint16()
        self.Reserved6 = v_uint16()
        self.Gs = v_uint16()
        self.Reserved7 = v_uint16()
        self.LDT = v_uint16()
        self.Reserved8 = v_uint16()
        self.Flags = v_uint16()
        self.IoMapBase = v_uint16()
        self.IoMaps = vstruct.VArray([ KiIoAccessMap() for i in range(1) ])
        self.IntDirectionMap = vstruct.VArray([ v_uint8() for i in range(32) ])


class CURDIR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DosPath = UNICODE_STRING()
        self.Handle = v_ptr32()


class RTL_TRACE_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic = v_uint32()
        self.Count = v_uint32()
        self.Size = v_uint32()
        self.UserCount = v_uint32()
        self.UserSize = v_uint32()
        self.UserContext = v_ptr32()
        self.Next = v_ptr32()
        self.Trace = v_ptr32()


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
        self.DataDirectory = vstruct.VArray([ IMAGE_DATA_DIRECTORY() for i in range(16) ])


class SCSI_REQUEST_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class _unnamed_5269(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UserApcRoutine = v_ptr32()
        self.UserApcContext = v_ptr32()


class ETHREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Tcb = KTHREAD()
        self.CreateTime = LARGE_INTEGER()
        self.ExitTime = LARGE_INTEGER()
        self.ExitStatus = v_uint32()
        self.PostBlockList = LIST_ENTRY()
        self.TerminationPort = v_ptr32()
        self.ActiveTimerListLock = v_uint32()
        self.ActiveTimerListHead = LIST_ENTRY()
        self.Cid = CLIENT_ID()
        self.LpcReplySemaphore = KSEMAPHORE()
        self.LpcReplyMessage = v_ptr32()
        self.ImpersonationInfo = v_ptr32()
        self.IrpList = LIST_ENTRY()
        self.TopLevelIrp = v_uint32()
        self.DeviceToVerify = v_ptr32()
        self.ThreadsProcess = v_ptr32()
        self.StartAddress = v_ptr32()
        self.Win32StartAddress = v_ptr32()
        self.ThreadListEntry = LIST_ENTRY()
        self.RundownProtect = EX_RUNDOWN_REF()
        self.ThreadLock = EX_PUSH_LOCK()
        self.LpcReplyMessageId = v_uint32()
        self.ReadClusterSize = v_uint32()
        self.GrantedAccess = v_uint32()
        self.CrossThreadFlags = v_uint32()
        self.SameThreadPassiveFlags = v_uint32()
        self.SameThreadApcFlags = v_uint32()
        self.ForwardClusterOnly = v_uint8()
        self.DisablePageFaultClustering = v_uint8()
        self.ActiveFaultCount = v_uint8()
        self._pad0250 = v_bytes(size=1)


class PEB_LDR_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Initialized = v_uint8()
        self._pad0008 = v_bytes(size=3)
        self.SsHandle = v_ptr32()
        self.InLoadOrderModuleList = LIST_ENTRY()
        self.InMemoryOrderModuleList = LIST_ENTRY()
        self.InInitializationOrderModuleList = LIST_ENTRY()
        self.EntryInProgress = v_ptr32()


class PERFINFO_GROUPMASK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Masks = vstruct.VArray([ v_uint32() for i in range(8) ])


class EPROCESS_QUOTA_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Usage = v_uint32()
        self.Limit = v_uint32()
        self.Peak = v_uint32()
        self.Return = v_uint32()


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
        self.VolumeLabel = vstruct.VArray([ v_uint16() for i in range(32) ])


class HEAP_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.PreviousSize = v_uint16()
        self.SmallTagIndex = v_uint8()
        self.Flags = v_uint8()
        self.UnusedBytes = v_uint8()
        self.SegmentIndex = v_uint8()


class _unnamed_6357(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SyncType = v_uint32()
        self.PageProtection = v_uint32()


class _unnamed_6356(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ResourceToRelease = v_ptr32()


class RTL_CRITICAL_SECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DebugInfo = v_ptr32()
        self.LockCount = v_uint32()
        self.RecursionCount = v_uint32()
        self.OwningThread = v_ptr32()
        self.LockSemaphore = v_ptr32()
        self.SpinCount = v_uint32()


class _unnamed_6215(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerState = v_uint32()


class _unnamed_6407(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Port = _unnamed_6416()


class _unnamed_6059(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.FsControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


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


class _unnamed_5083(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AsynchronousParameters = _unnamed_5269()


class _unnamed_5080(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MasterIrp = v_ptr32()


class _unnamed_5084(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Overlay = _unnamed_5322()
        self._pad0030 = v_bytes(size=8)


class _unnamed_6358(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()
        self.Argument5 = v_ptr32()


class FLOATING_SAVE_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlWord = v_uint32()
        self.StatusWord = v_uint32()
        self.TagWord = v_uint32()
        self.ErrorOffset = v_uint32()
        self.ErrorSelector = v_uint32()
        self.DataOffset = v_uint32()
        self.DataSelector = v_uint32()
        self.RegisterArea = vstruct.VArray([ v_uint8() for i in range(80) ])
        self.Cr0NpxState = v_uint32()


class DPH_HEAP_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.pNextAlloc = v_ptr32()
        self._pad0010 = v_bytes(size=12)
        self.pUserAllocation = v_ptr32()
        self.pVirtualBlock = v_ptr32()
        self.nVirtualBlockSize = v_uint32()
        self.nVirtualAccessSize = v_uint32()
        self.nUserRequestedSize = v_uint32()
        self.nUserActualSize = v_uint32()
        self.UserValue = v_ptr32()
        self.UserFlags = v_uint32()
        self.StackTrace = v_ptr32()
        self.AdjacencyEntry = LIST_ENTRY()
        self.pVirtualRegion = v_ptr32()


class KQUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.EntryListHead = LIST_ENTRY()
        self.CurrentCount = v_uint32()
        self.MaximumCount = v_uint32()
        self.ThreadListHead = LIST_ENTRY()


class RTL_TRACE_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic = v_uint32()
        self.Database = v_ptr32()
        self.NextSegment = v_ptr32()
        self.TotalSize = v_uint32()
        self.SegmentStart = v_ptr32()
        self.SegmentEnd = v_ptr32()
        self.SegmentFree = v_ptr32()


class _unnamed_3538(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FnArea = FNSAVE_FORMAT()
        self._pad0208 = v_bytes(size=412)


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


class TERMINATION_PORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Port = v_ptr32()


class _unnamed_6434(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Priority = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class _unnamed_6485(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length = v_uint32()


class CM_PARTIAL_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Revision = v_uint16()
        self.Count = v_uint32()
        self.PartialDescriptors = vstruct.VArray([ CM_PARTIAL_RESOURCE_DESCRIPTOR() for i in range(1) ])


class IO_CLIENT_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextExtension = v_ptr32()
        self.ClientIdentificationAddress = v_ptr32()


class INITIAL_PRIVILEGE_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PrivilegeCount = v_uint32()
        self.Control = v_uint32()
        self.Privilege = vstruct.VArray([ LUID_AND_ATTRIBUTES() for i in range(3) ])


class HANDLE_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TableCode = v_uint32()
        self.QuotaProcess = v_ptr32()
        self.UniqueProcessId = v_ptr32()
        self.HandleTableLock = vstruct.VArray([ EX_PUSH_LOCK() for i in range(4) ])
        self.HandleTableList = LIST_ENTRY()
        self.HandleContentionEvent = EX_PUSH_LOCK()
        self.DebugInfo = v_ptr32()
        self.ExtraInfoPages = v_uint32()
        self.FirstFree = v_uint32()
        self.LastFree = v_uint32()
        self.NextHandleNeedingPool = v_uint32()
        self.HandleCount = v_uint32()
        self.Flags = v_uint32()


class INTERFACE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Context = v_ptr32()
        self.InterfaceReference = v_ptr32()
        self.InterfaceDereference = v_ptr32()


class OBJECT_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashBuckets = vstruct.VArray([ v_ptr32() for i in range(37) ])
        self.Lock = EX_PUSH_LOCK()
        self.DeviceMap = v_ptr32()
        self.SessionId = v_uint32()


class OBJECT_HEADER_QUOTA_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PagedPoolCharge = v_uint32()
        self.NonPagedPoolCharge = v_uint32()
        self.SecurityDescriptorCharge = v_uint32()
        self.ExclusiveProcess = v_ptr32()


class HEAP_UNCOMMMTTED_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Address = v_uint32()
        self.Size = v_uint32()
        self.filler = v_uint32()


class KTHREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.MutantListHead = LIST_ENTRY()
        self.InitialStack = v_ptr32()
        self.StackLimit = v_ptr32()
        self.KernelStack = v_ptr32()
        self.ThreadLock = v_uint32()
        self.ApcState = KAPC_STATE()
        self.NextProcessor = v_uint8()
        self.DeferredProcessor = v_uint8()
        self.AdjustReason = v_uint8()
        self.AdjustIncrement = v_uint8()
        self.ApcQueueLock = v_uint32()
        self.ContextSwitches = v_uint32()
        self.State = v_uint8()
        self.NpxState = v_uint8()
        self.WaitIrql = v_uint8()
        self.WaitMode = v_uint8()
        self.WaitStatus = v_uint32()
        self.WaitBlockList = v_ptr32()
        self.Alertable = v_uint8()
        self.WaitNext = v_uint8()
        self.WaitReason = v_uint8()
        self.Priority = v_uint8()
        self.EnableStackSwap = v_uint8()
        self.SwapBusy = v_uint8()
        self.Alerted = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.WaitListEntry = LIST_ENTRY()
        self.Queue = v_ptr32()
        self.WaitTime = v_uint32()
        self.KernelApcDisable = v_uint16()
        self.SpecialApcDisable = v_uint16()
        self.Teb = v_ptr32()
        self.Timer = KTIMER()
        self.AutoAlignment = v_uint32()
        self._pad00a8 = v_bytes(size=4)
        self.WaitBlock = vstruct.VArray([ KWAIT_BLOCK() for i in range(4) ])
        self.QueueListEntry = LIST_ENTRY()
        self.TrapFrame = v_ptr32()
        self.CallbackStack = v_ptr32()
        self.ServiceTable = v_ptr32()
        self.ApcStateIndex = v_uint8()
        self.IdealProcessor = v_uint8()
        self.Preempted = v_uint8()
        self.ProcessReadyQueue = v_uint8()
        self.KernelStackResident = v_uint8()
        self.BasePriority = v_uint8()
        self.PriorityDecrement = v_uint8()
        self.Saturation = v_uint8()
        self.UserAffinity = v_uint32()
        self.Process = v_ptr32()
        self.Affinity = v_uint32()
        self.ApcStatePointer = vstruct.VArray([ v_ptr32() for i in range(2) ])
        self.SavedApcState = KAPC_STATE()
        self.SuspendCount = v_uint8()
        self.UserIdealProcessor = v_uint8()
        self.CalloutActive = v_uint8()
        self.Iopl = v_uint8()
        self.Win32Thread = v_ptr32()
        self.StackBase = v_ptr32()
        self.SuspendApc = KAPC()
        self.UserTime = v_uint32()
        self.SuspendSemaphore = KSEMAPHORE()
        self.SListFaultCount = v_uint32()
        self.ThreadListEntry = LIST_ENTRY()
        self.SListFaultAddress = v_ptr32()
        self._pad01b8 = v_bytes(size=4)


class PP_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.P = v_ptr32()
        self.L = v_ptr32()


class EX_RUNDOWN_REF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()


class IMAGE_DATA_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_uint32()
        self.Size = v_uint32()


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


class _unnamed_5965(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


class PROCESSOR_IDLE_TIMES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartTime = v_uint64()
        self.EndTime = v_uint64()
        self.IdleHandlerReserved = vstruct.VArray([ v_uint32() for i in range(4) ])


class KWAIT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WaitListEntry = LIST_ENTRY()
        self.Thread = v_ptr32()
        self.Object = v_ptr32()
        self.NextWaitBlock = v_ptr32()
        self.WaitKey = v_uint16()
        self.WaitType = v_uint8()
        self.SpareByte = v_uint8()


class KPROCESS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.ProfileListHead = LIST_ENTRY()
        self.DirectoryTableBase = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.LdtDescriptor = KGDTENTRY()
        self.Int21Descriptor = KIDTENTRY()
        self.IopmOffset = v_uint16()
        self.Iopl = v_uint8()
        self.Unused = v_uint8()
        self.ActiveProcessors = v_uint32()
        self.KernelTime = v_uint32()
        self.UserTime = v_uint32()
        self.ReadyListHead = LIST_ENTRY()
        self.SwapListEntry = SINGLE_LIST_ENTRY()
        self.VdmTrapcHandler = v_ptr32()
        self.ThreadListHead = LIST_ENTRY()
        self.ProcessLock = v_uint32()
        self.Affinity = v_uint32()
        self.AutoAlignment = v_uint32()
        self.BasePriority = v_uint8()
        self.QuantumReset = v_uint8()
        self.State = v_uint8()
        self.ThreadSeed = v_uint8()
        self.PowerState = v_uint8()
        self.IdealNode = v_uint8()
        self.Visited = v_uint8()
        self.Flags = KEXECUTE_OPTIONS()
        self.StackCount = v_uint32()
        self.ProcessListEntry = LIST_ENTRY()


class DEVICE_OBJECT_POWER_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ContextFlags = v_uint32()
        self.Dr0 = v_uint32()
        self.Dr1 = v_uint32()
        self.Dr2 = v_uint32()
        self.Dr3 = v_uint32()
        self.Dr6 = v_uint32()
        self.Dr7 = v_uint32()
        self.FloatSave = FLOATING_SAVE_AREA()
        self.SegGs = v_uint32()
        self.SegFs = v_uint32()
        self.SegEs = v_uint32()
        self.SegDs = v_uint32()
        self.Edi = v_uint32()
        self.Esi = v_uint32()
        self.Ebx = v_uint32()
        self.Edx = v_uint32()
        self.Ecx = v_uint32()
        self.Eax = v_uint32()
        self.Ebp = v_uint32()
        self.Eip = v_uint32()
        self.SegCs = v_uint32()
        self.EFlags = v_uint32()
        self.Esp = v_uint32()
        self.SegSs = v_uint32()
        self.ExtendedRegisters = vstruct.VArray([ v_uint8() for i in range(512) ])


class EX_FAST_REF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Object = v_ptr32()


class ACTIVATION_CONTEXT_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class _unnamed_6024(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.CompletionFilter = v_uint32()


class _unnamed_6027(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()


class ERESOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemResourcesList = LIST_ENTRY()
        self.OwnerTable = v_ptr32()
        self.ActiveCount = v_uint16()
        self.Flag = v_uint16()
        self.SharedWaiters = v_ptr32()
        self.ExclusiveWaiters = v_ptr32()
        self.OwnerThreads = vstruct.VArray([ OWNER_ENTRY() for i in range(2) ])
        self.ContentionCount = v_uint32()
        self.NumberOfSharedWaiters = v_uint16()
        self.NumberOfExclusiveWaiters = v_uint16()
        self.Address = v_ptr32()
        self.SpinLock = v_uint32()


class _unnamed_6221(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerSequence = v_ptr32()


class KGUARDED_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Gate = KGATE()
        self.KernelApcDisable = v_uint16()
        self.SpecialApcDisable = v_uint16()


class _unnamed_5322(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceQueueEntry = KDEVICE_QUEUE_ENTRY()
        self.Thread = v_ptr32()
        self.AuxiliaryBuffer = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.CurrentStackLocation = v_ptr32()
        self.OriginalFileObject = v_ptr32()


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


class DPH_HEAP_ROOT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.HeapFlags = v_uint32()
        self.HeapCritSect = v_ptr32()
        self.nRemoteLockAcquired = v_uint32()
        self.pVirtualStorageListHead = v_ptr32()
        self.pVirtualStorageListTail = v_ptr32()
        self.nVirtualStorageRanges = v_uint32()
        self.nVirtualStorageBytes = v_uint32()
        self.BusyNodesTable = RTL_AVL_TABLE()
        self.NodeToAllocate = v_ptr32()
        self.nBusyAllocations = v_uint32()
        self.nBusyAllocationBytesCommitted = v_uint32()
        self.pFreeAllocationListHead = v_ptr32()
        self.pFreeAllocationListTail = v_ptr32()
        self.nFreeAllocations = v_uint32()
        self.nFreeAllocationBytesCommitted = v_uint32()
        self.AvailableAllocationHead = LIST_ENTRY()
        self.nAvailableAllocations = v_uint32()
        self.nAvailableAllocationBytesCommitted = v_uint32()
        self.pUnusedNodeListHead = v_ptr32()
        self.pUnusedNodeListTail = v_ptr32()
        self.nUnusedNodes = v_uint32()
        self.nBusyAllocationBytesAccessible = v_uint32()
        self.pNodePoolListHead = v_ptr32()
        self.pNodePoolListTail = v_ptr32()
        self.nNodePools = v_uint32()
        self.nNodePoolBytes = v_uint32()
        self.NextHeap = LIST_ENTRY()
        self.ExtraFlags = v_uint32()
        self.Seed = v_uint32()
        self.NormalHeap = v_ptr32()
        self.CreateStackTrace = v_ptr32()
        self.FirstThread = v_ptr32()


class _unnamed_6174(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoResourceRequirementList = v_ptr32()


class RTL_ACTIVATION_CONTEXT_STACK_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Previous = v_ptr32()
        self.ActivationContext = v_ptr32()
        self.Flags = v_uint32()


class TEB_ACTIVE_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.Previous = v_ptr32()
        self.Context = v_ptr32()


class _unnamed_5937(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.FileAttributes = v_uint16()
        self.ShareAccess = v_uint16()
        self.EaLength = v_uint32()


class OBJECT_HANDLE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleAttributes = v_uint32()
        self.GrantedAccess = v_uint32()


class RTL_DRIVE_LETTER_CURDIR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Length = v_uint16()
        self.TimeStamp = v_uint32()
        self.DosPath = STRING()


class DEVICE_CAPABILITIES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.DeviceD1 = v_uint32()
        self.Address = v_uint32()
        self.UINumber = v_uint32()
        self.DeviceState = vstruct.VArray([ DEVICE_POWER_STATE() for i in range(7) ])
        self.SystemWake = v_uint32()
        self.DeviceWake = v_uint32()
        self.D1Latency = v_uint32()
        self.D2Latency = v_uint32()
        self.D3Latency = v_uint32()


class _unnamed_6500(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class HEAP_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = _unnamed_4885()


class RTL_BALANCED_LINKS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Parent = v_ptr32()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.Balance = v_uint8()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(3) ])


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
        self.Future = vstruct.VArray([ v_uint32() for i in range(2) ])
        self._pad0080 = v_bytes(size=56)


class RTL_AVL_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BalancedRoot = RTL_BALANCED_LINKS()
        self.OrderedPointer = v_ptr32()
        self.WhichOrderedElement = v_uint32()
        self.NumberGenericTableElements = v_uint32()
        self.DepthOfTree = v_uint32()
        self.RestartKey = v_ptr32()
        self.DeleteCount = v_uint32()
        self.CompareRoutine = v_ptr32()
        self.AllocateRoutine = v_ptr32()
        self.FreeRoutine = v_ptr32()
        self.TableContext = v_ptr32()


class OBJECT_HEADER_HANDLE_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleCountDataBase = v_ptr32()
        self._pad0008 = v_bytes(size=4)


class _unnamed_5972(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class RTL_TRACE_DATABASE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic = v_uint32()
        self.Flags = v_uint32()
        self.Tag = v_uint32()
        self.SegmentList = v_ptr32()
        self.MaximumSize = v_uint32()
        self.CurrentSize = v_uint32()
        self.Owner = v_ptr32()
        self.Lock = RTL_CRITICAL_SECTION()
        self.NoOfBuckets = v_uint32()
        self.Buckets = v_ptr32()
        self.HashFunction = v_ptr32()
        self.NoOfTraces = v_uint32()
        self.NoOfHits = v_uint32()
        self.HashCounter = vstruct.VArray([ v_uint32() for i in range(16) ])


class ULARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_4885(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CriticalSection = RTL_CRITICAL_SECTION()
        self._pad0038 = v_bytes(size=32)


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class _unnamed_6038(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.EaList = v_ptr32()
        self.EaListLength = v_uint32()
        self.EaIndex = v_uint32()


class _unnamed_6239(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemContext = v_uint32()
        self.Type = v_uint32()
        self.State = POWER_STATE()
        self.ShutdownType = v_uint32()


class OBJECT_DIRECTORY_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ChainLink = v_ptr32()
        self.Object = v_ptr32()
        self.HashValue = v_uint32()


class SLIST_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Alignment = v_uint64()


class FXSAVE_FORMAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlWord = v_uint16()
        self.StatusWord = v_uint16()
        self.TagWord = v_uint16()
        self.ErrorOpcode = v_uint16()
        self.ErrorOffset = v_uint32()
        self.ErrorSelector = v_uint32()
        self.DataOffset = v_uint32()
        self.DataSelector = v_uint32()
        self.MXCsr = v_uint32()
        self.MXCsrMask = v_uint32()
        self.RegisterArea = vstruct.VArray([ v_uint8() for i in range(128) ])
        self.Reserved3 = vstruct.VArray([ v_uint8() for i in range(128) ])
        self.Reserved4 = vstruct.VArray([ v_uint8() for i in range(224) ])
        self.Align16Byte = vstruct.VArray([ v_uint8() for i in range(8) ])


class _unnamed_6030(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()
        self.FileObject = v_ptr32()
        self.ReplaceIfExists = v_uint8()
        self.AdvanceOnly = v_uint8()
        self._pad0010 = v_bytes(size=2)


class OWNER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwnerThread = v_uint32()
        self.OwnerCount = v_uint32()


class DPH_BLOCK_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartStamp = v_uint32()
        self.Heap = v_ptr32()
        self.RequestedSize = v_uint32()
        self.ActualSize = v_uint32()
        self.FreeQueue = LIST_ENTRY()
        self.StackTrace = v_ptr32()
        self.EndStamp = v_uint32()


class DEVOBJ_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceObject = v_ptr32()
        self.PowerFlags = v_uint32()
        self.Dope = v_ptr32()
        self.ExtensionFlags = v_uint32()
        self.DeviceNode = v_ptr32()
        self.AttachedTo = v_ptr32()
        self.StartIoCount = v_uint32()
        self.StartIoKey = v_uint32()
        self.StartIoFlags = v_uint32()
        self.Vpb = v_ptr32()


class PROCESSOR_PERF_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PercentFrequency = v_uint8()
        self.MinCapacity = v_uint8()
        self.Power = v_uint16()
        self.IncreaseLevel = v_uint8()
        self.DecreaseLevel = v_uint8()
        self.Flags = v_uint16()
        self.IncreaseTime = v_uint32()
        self.DecreaseTime = v_uint32()
        self.IncreaseCount = v_uint32()
        self.DecreaseCount = v_uint32()
        self.PerformanceTime = v_uint64()


class KPCR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NtTib = NT_TIB()
        self.SelfPcr = v_ptr32()
        self.Prcb = v_ptr32()
        self.Irql = v_uint8()
        self._pad0028 = v_bytes(size=3)
        self.IRR = v_uint32()
        self.IrrActive = v_uint32()
        self.IDR = v_uint32()
        self.KdVersionBlock = v_ptr32()
        self.IDT = v_ptr32()
        self.GDT = v_ptr32()
        self.TSS = v_ptr32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.SetMember = v_uint32()
        self.StallScaleFactor = v_uint32()
        self.SpareUnused = v_uint8()
        self.Number = v_uint8()
        self.Spare0 = v_uint8()
        self.SecondLevelCacheAssociativity = v_uint8()
        self.VdmAlert = v_uint32()
        self.KernelReserved = vstruct.VArray([ v_uint32() for i in range(14) ])
        self.SecondLevelCacheSize = v_uint32()
        self.HalReserved = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.InterruptMode = v_uint32()
        self.Spare1 = v_uint8()
        self._pad00dc = v_bytes(size=3)
        self.KernelReserved2 = vstruct.VArray([ v_uint32() for i in range(17) ])
        self.PrcbData = KPRCB()


class KGDTENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LimitLow = v_uint16()
        self.BaseLow = v_uint16()
        self.HighWord = _unnamed_3661()


class NAMED_PIPE_CREATE_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NamedPipeType = v_uint32()
        self.ReadMode = v_uint32()
        self.CompletionMode = v_uint32()
        self.MaximumInstances = v_uint32()
        self.InboundQuota = v_uint32()
        self.OutboundQuota = v_uint32()
        self.DefaultTimeout = LARGE_INTEGER()
        self.TimeoutSpecified = v_uint8()
        self._pad0028 = v_bytes(size=7)


class _unnamed_5232(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint32()


class NT_TIB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionList = v_ptr32()
        self.StackBase = v_ptr32()
        self.StackLimit = v_ptr32()
        self.SubSystemTib = v_ptr32()
        self.FiberData = v_ptr32()
        self.ArbitraryUserPointer = v_ptr32()
        self.Self = v_ptr32()


class HEAP_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = HEAP_ENTRY()
        self.Signature = v_uint32()
        self.Flags = v_uint32()
        self.Heap = v_ptr32()
        self.LargestUnCommittedRange = v_uint32()
        self.BaseAddress = v_ptr32()
        self.NumberOfPages = v_uint32()
        self.FirstEntry = v_ptr32()
        self.LastValidEntry = v_ptr32()
        self.NumberOfUnCommittedPages = v_uint32()
        self.NumberOfUnCommittedRanges = v_uint32()
        self.UnCommittedRanges = v_ptr32()
        self.AllocatorBackTraceIndex = v_uint16()
        self.Reserved = v_uint16()
        self.LastEntryInSegment = v_ptr32()


class _unnamed_6488(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint32()
        self.Vector = v_uint32()
        self.Affinity = v_uint32()


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


class TEB_ACTIVE_FRAME_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.FrameName = v_ptr32()


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
        self.MajorFunction = vstruct.VArray([ v_ptr32() for i in range(28) ])


class KTRAP_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DbgEbp = v_uint32()
        self.DbgEip = v_uint32()
        self.DbgArgMark = v_uint32()
        self.DbgArgPointer = v_uint32()
        self.TempSegCs = v_uint32()
        self.TempEsp = v_uint32()
        self.Dr0 = v_uint32()
        self.Dr1 = v_uint32()
        self.Dr2 = v_uint32()
        self.Dr3 = v_uint32()
        self.Dr6 = v_uint32()
        self.Dr7 = v_uint32()
        self.SegGs = v_uint32()
        self.SegEs = v_uint32()
        self.SegDs = v_uint32()
        self.Edx = v_uint32()
        self.Ecx = v_uint32()
        self.Eax = v_uint32()
        self.PreviousPreviousMode = v_uint32()
        self.ExceptionList = v_ptr32()
        self.SegFs = v_uint32()
        self.Edi = v_uint32()
        self.Esi = v_uint32()
        self.Ebx = v_uint32()
        self.Ebp = v_uint32()
        self.ErrCode = v_uint32()
        self.Eip = v_uint32()
        self.SegCs = v_uint32()
        self.EFlags = v_uint32()
        self.HardwareEsp = v_uint32()
        self.HardwareSegSs = v_uint32()
        self.V86Es = v_uint32()
        self.V86Ds = v_uint32()
        self.V86Fs = v_uint32()
        self.V86Gs = v_uint32()


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
        self.Privileges = _unnamed_4953()
        self.AuditPrivileges = v_uint8()
        self._pad0064 = v_bytes(size=3)
        self.ObjectName = UNICODE_STRING()
        self.ObjectTypeName = UNICODE_STRING()


class EJOB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Event = KEVENT()
        self.JobLinks = LIST_ENTRY()
        self.ProcessListHead = LIST_ENTRY()
        self.JobLock = ERESOURCE()
        self.TotalUserTime = LARGE_INTEGER()
        self.TotalKernelTime = LARGE_INTEGER()
        self.ThisPeriodTotalUserTime = LARGE_INTEGER()
        self.ThisPeriodTotalKernelTime = LARGE_INTEGER()
        self.TotalPageFaultCount = v_uint32()
        self.TotalProcesses = v_uint32()
        self.ActiveProcesses = v_uint32()
        self.TotalTerminatedProcesses = v_uint32()
        self.PerProcessUserTimeLimit = LARGE_INTEGER()
        self.PerJobUserTimeLimit = LARGE_INTEGER()
        self.LimitFlags = v_uint32()
        self.MinimumWorkingSetSize = v_uint32()
        self.MaximumWorkingSetSize = v_uint32()
        self.ActiveProcessLimit = v_uint32()
        self.Affinity = v_uint32()
        self.PriorityClass = v_uint8()
        self._pad00b0 = v_bytes(size=3)
        self.UIRestrictionsClass = v_uint32()
        self.SecurityLimitFlags = v_uint32()
        self.Token = v_ptr32()
        self.Filter = v_ptr32()
        self.EndOfJobTimeAction = v_uint32()
        self.CompletionPort = v_ptr32()
        self.CompletionKey = v_ptr32()
        self.SessionId = v_uint32()
        self.SchedulingClass = v_uint32()
        self._pad00d8 = v_bytes(size=4)
        self.ReadOperationCount = v_uint64()
        self.WriteOperationCount = v_uint64()
        self.OtherOperationCount = v_uint64()
        self.ReadTransferCount = v_uint64()
        self.WriteTransferCount = v_uint64()
        self.OtherTransferCount = v_uint64()
        self.IoInfo = IO_COUNTERS()
        self.ProcessMemoryLimit = v_uint32()
        self.JobMemoryLimit = v_uint32()
        self.PeakProcessMemoryUsed = v_uint32()
        self.PeakJobMemoryUsed = v_uint32()
        self.CurrentJobMemoryUsed = v_uint32()
        self.MemoryLimitsLock = KGUARDED_MUTEX()
        self.JobSetLinks = LIST_ENTRY()
        self.MemberLevel = v_uint32()
        self.JobFlags = v_uint32()
        self._pad0180 = v_bytes(size=4)


class FILE_STANDARD_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocationSize = LARGE_INTEGER()
        self.EndOfFile = LARGE_INTEGER()
        self.NumberOfLinks = v_uint32()
        self.DeletePending = v_uint8()
        self.Directory = v_uint8()
        self._pad0018 = v_bytes(size=2)


class LDR_DATA_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InLoadOrderLinks = LIST_ENTRY()
        self.InMemoryOrderLinks = LIST_ENTRY()
        self.InInitializationOrderLinks = LIST_ENTRY()
        self.DllBase = v_ptr32()
        self.EntryPoint = v_ptr32()
        self.SizeOfImage = v_uint32()
        self.FullDllName = UNICODE_STRING()
        self.BaseDllName = UNICODE_STRING()
        self.Flags = v_uint32()
        self.LoadCount = v_uint16()
        self.TlsIndex = v_uint16()
        self.HashLinks = LIST_ENTRY()
        self.TimeDateStamp = v_uint32()
        self.EntryPointActivationContext = v_ptr32()
        self.PatchInformation = v_ptr32()


class EPROCESS_QUOTA_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.QuotaEntry = vstruct.VArray([ EPROCESS_QUOTA_ENTRY() for i in range(3) ])
        self.QuotaList = LIST_ENTRY()
        self.ReferenceCount = v_uint32()
        self.ProcessCount = v_uint32()


class _unnamed_6249(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatedResources = v_ptr32()
        self.AllocatedResourcesTranslated = v_ptr32()


class HANDLE_TRACE_DEBUG_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.RefCount = v_uint32()
        self.TableSize = v_uint32()
        self.BitMaskFlags = v_uint32()
        self.CloseCompactionLock = FAST_MUTEX()
        self.CurrentStackIndex = v_uint32()
        self.TraceDb = vstruct.VArray([ HANDLE_TRACE_DB_ENTRY() for i in range(1) ])


class GDI_TEB_BATCH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.HDC = v_uint32()
        self.Buffer = vstruct.VArray([ v_uint32() for i in range(310) ])


class KPROCESSOR_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ContextFrame = CONTEXT()
        self.SpecialRegisters = KSPECIAL_REGISTERS()


class KiIoAccessMap(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DirectionMap = vstruct.VArray([ v_uint8() for i in range(32) ])
        self.IoMap = vstruct.VArray([ v_uint8() for i in range(8196) ])


class LIST_ENTRY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint64()
        self.Blink = v_uint64()


class _unnamed_6177(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WhichSpace = v_uint32()
        self.Buffer = v_ptr32()
        self.Offset = v_uint32()
        self.Length = v_uint32()


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


class PEB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InheritedAddressSpace = v_uint8()
        self.ReadImageFileExecOptions = v_uint8()
        self.BeingDebugged = v_uint8()
        self.BitField = v_uint8()
        self.Mutant = v_ptr32()
        self.ImageBaseAddress = v_ptr32()
        self.Ldr = v_ptr32()
        self.ProcessParameters = v_ptr32()
        self.SubSystemData = v_ptr32()
        self.ProcessHeap = v_ptr32()
        self.FastPebLock = v_ptr32()
        self.AtlThunkSListPtr = v_ptr32()
        self.SparePtr2 = v_ptr32()
        self.EnvironmentUpdateCount = v_uint32()
        self.KernelCallbackTable = v_ptr32()
        self.SystemReserved = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.SpareUlong = v_uint32()
        self.FreeList = v_ptr32()
        self.TlsExpansionCounter = v_uint32()
        self.TlsBitmap = v_ptr32()
        self.TlsBitmapBits = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.ReadOnlySharedMemoryBase = v_ptr32()
        self.ReadOnlySharedMemoryHeap = v_ptr32()
        self.ReadOnlyStaticServerData = v_ptr32()
        self.AnsiCodePageData = v_ptr32()
        self.OemCodePageData = v_ptr32()
        self.UnicodeCaseTableData = v_ptr32()
        self.NumberOfProcessors = v_uint32()
        self.NtGlobalFlag = v_uint32()
        self._pad0070 = v_bytes(size=4)
        self.CriticalSectionTimeout = LARGE_INTEGER()
        self.HeapSegmentReserve = v_uint32()
        self.HeapSegmentCommit = v_uint32()
        self.HeapDeCommitTotalFreeThreshold = v_uint32()
        self.HeapDeCommitFreeBlockThreshold = v_uint32()
        self.NumberOfHeaps = v_uint32()
        self.MaximumNumberOfHeaps = v_uint32()
        self.ProcessHeaps = v_ptr32()
        self.GdiSharedHandleTable = v_ptr32()
        self.ProcessStarterHelper = v_ptr32()
        self.GdiDCAttributeList = v_uint32()
        self.LoaderLock = v_ptr32()
        self.OSMajorVersion = v_uint32()
        self.OSMinorVersion = v_uint32()
        self.OSBuildNumber = v_uint16()
        self.OSCSDVersion = v_uint16()
        self.OSPlatformId = v_uint32()
        self.ImageSubsystem = v_uint32()
        self.ImageSubsystemMajorVersion = v_uint32()
        self.ImageSubsystemMinorVersion = v_uint32()
        self.ImageProcessAffinityMask = v_uint32()
        self.GdiHandleBuffer = vstruct.VArray([ v_uint32() for i in range(34) ])
        self.PostProcessInitRoutine = v_ptr32()
        self.TlsExpansionBitmap = v_ptr32()
        self.TlsExpansionBitmapBits = vstruct.VArray([ v_uint32() for i in range(32) ])
        self.SessionId = v_uint32()
        self.AppCompatFlags = ULARGE_INTEGER()
        self.AppCompatFlagsUser = ULARGE_INTEGER()
        self.pShimData = v_ptr32()
        self.AppCompatInfo = v_ptr32()
        self.CSDVersion = UNICODE_STRING()
        self.ActivationContextData = v_ptr32()
        self.ProcessAssemblyStorageMap = v_ptr32()
        self.SystemDefaultActivationContextData = v_ptr32()
        self.SystemAssemblyStorageMap = v_ptr32()
        self.MinimumStackCommit = v_uint32()
        self.FlsCallback = v_ptr32()
        self.FlsListHead = LIST_ENTRY()
        self.FlsBitmap = v_ptr32()
        self.FlsBitmapBits = vstruct.VArray([ v_uint32() for i in range(4) ])
        self.FlsHighIndex = v_uint32()


class SE_AUDIT_PROCESS_CREATION_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ImageFileName = v_ptr32()


class ACTIVATION_CONTEXT_STACK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ActiveFrame = v_ptr32()
        self.FrameListCache = LIST_ENTRY()
        self.Flags = v_uint32()
        self.NextCookieSequenceNumber = v_uint32()
        self.StackId = v_uint32()


class PROCESS_WS_WATCH_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FaultingPc = v_ptr32()
        self.FaultingVa = v_ptr32()


class SID_IDENTIFIER_AUTHORITY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Value = vstruct.VArray([ v_uint8() for i in range(6) ])


class SECTION_OBJECT_POINTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSectionObject = v_ptr32()
        self.SharedCacheMap = v_ptr32()
        self.ImageSectionObject = v_ptr32()


class STACK_TRACE_DATABASE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CriticalSection = RTL_CRITICAL_SECTION()
        self._pad0038 = v_bytes(size=32)
        self.Reserved = vstruct.VArray([ v_ptr32() for i in range(3) ])
        self.PreCommitted = v_uint8()
        self.DumpInProgress = v_uint8()
        self._pad0048 = v_bytes(size=2)
        self.CommitBase = v_ptr32()
        self.CurrentLowerCommitLimit = v_ptr32()
        self.CurrentUpperCommitLimit = v_ptr32()
        self.NextFreeLowerMemory = v_ptr32()
        self.NextFreeUpperMemory = v_ptr32()
        self.NumberOfEntriesLookedUp = v_uint32()
        self.NumberOfEntriesAdded = v_uint32()
        self.EntryIndexArray = v_ptr32()
        self.NumberOfBuckets = v_uint32()
        self.Buckets = vstruct.VArray([ v_ptr32() for i in range(1) ])


class HEAP_UCR_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.ReservedSize = v_uint32()
        self.CommittedSize = v_uint32()
        self.filler = v_uint32()


class _unnamed_4953(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InitialPrivilegeSet = INITIAL_PRIVILEGE_SET()


class EPROCESS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pcb = KPROCESS()
        self.ProcessLock = EX_PUSH_LOCK()
        self._pad0080 = v_bytes(size=4)
        self.CreateTime = LARGE_INTEGER()
        self.ExitTime = LARGE_INTEGER()
        self.RundownProtect = EX_RUNDOWN_REF()
        self.UniqueProcessId = v_ptr32()
        self.ActiveProcessLinks = LIST_ENTRY()
        self.QuotaUsage = vstruct.VArray([ v_uint32() for i in range(3) ])
        self.QuotaPeak = vstruct.VArray([ v_uint32() for i in range(3) ])
        self.CommitCharge = v_uint32()
        self.PeakVirtualSize = v_uint32()
        self.VirtualSize = v_uint32()
        self.SessionProcessLinks = LIST_ENTRY()
        self.DebugPort = v_ptr32()
        self.ExceptionPort = v_ptr32()
        self.ObjectTable = v_ptr32()
        self.Token = EX_FAST_REF()
        self.WorkingSetPage = v_uint32()
        self.AddressCreationLock = KGUARDED_MUTEX()
        self.HyperSpaceLock = v_uint32()
        self.ForkInProgress = v_ptr32()
        self.HardwareTrigger = v_uint32()
        self.PhysicalVadRoot = v_ptr32()
        self.CloneRoot = v_ptr32()
        self.NumberOfPrivatePages = v_uint32()
        self.NumberOfLockedPages = v_uint32()
        self.Win32Process = v_ptr32()
        self.Job = v_ptr32()
        self.SectionObject = v_ptr32()
        self.SectionBaseAddress = v_ptr32()
        self.QuotaBlock = v_ptr32()
        self.WorkingSetWatch = v_ptr32()
        self.Win32WindowStation = v_ptr32()
        self.InheritedFromUniqueProcessId = v_ptr32()
        self.LdtInformation = v_ptr32()
        self.VadFreeHint = v_ptr32()
        self.VdmObjects = v_ptr32()
        self.DeviceMap = v_ptr32()
        self.Spare0 = vstruct.VArray([ v_ptr32() for i in range(3) ])
        self.PageDirectoryPte = HARDWARE_PTE_X86()
        self._pad0160 = v_bytes(size=4)
        self.Session = v_ptr32()
        self.ImageFileName = vstruct.VArray([ v_uint8() for i in range(16) ])
        self.JobLinks = LIST_ENTRY()
        self.LockedPagesList = v_ptr32()
        self.ThreadListHead = LIST_ENTRY()
        self.SecurityPort = v_ptr32()
        self.PaeTop = v_ptr32()
        self.ActiveThreads = v_uint32()
        self.GrantedAccess = v_uint32()
        self.DefaultHardErrorProcessing = v_uint32()
        self.LastThreadExitStatus = v_uint32()
        self.Peb = v_ptr32()
        self.PrefetchTrace = EX_FAST_REF()
        self.ReadOperationCount = LARGE_INTEGER()
        self.WriteOperationCount = LARGE_INTEGER()
        self.OtherOperationCount = LARGE_INTEGER()
        self.ReadTransferCount = LARGE_INTEGER()
        self.WriteTransferCount = LARGE_INTEGER()
        self.OtherTransferCount = LARGE_INTEGER()
        self.CommitChargeLimit = v_uint32()
        self.CommitChargePeak = v_uint32()
        self.AweInfo = v_ptr32()
        self.SeAuditProcessCreationInfo = SE_AUDIT_PROCESS_CREATION_INFO()
        self.Vm = MMSUPPORT()
        self.MmProcessLinks = LIST_ENTRY()
        self.ModifiedPageCount = v_uint32()
        self.JobStatus = v_uint32()
        self.Flags = v_uint32()
        self.ExitStatus = v_uint32()
        self.NextPageColor = v_uint16()
        self.SubSystemMinorVersion = v_uint8()
        self.SubSystemMajorVersion = v_uint8()
        self.PriorityClass = v_uint8()
        self._pad0250 = v_bytes(size=3)
        self.VadRoot = MM_AVL_TABLE()
        self.Cookie = v_uint32()
        self._pad0278 = v_bytes(size=4)


class TEB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NtTib = NT_TIB()
        self.EnvironmentPointer = v_ptr32()
        self.ClientId = CLIENT_ID()
        self.ActiveRpcHandle = v_ptr32()
        self.ThreadLocalStoragePointer = v_ptr32()
        self.ProcessEnvironmentBlock = v_ptr32()
        self.LastErrorValue = v_uint32()
        self.CountOfOwnedCriticalSections = v_uint32()
        self.CsrClientThread = v_ptr32()
        self.Win32ThreadInfo = v_ptr32()
        self.User32Reserved = vstruct.VArray([ v_uint32() for i in range(26) ])
        self.UserReserved = vstruct.VArray([ v_uint32() for i in range(5) ])
        self.WOW32Reserved = v_ptr32()
        self.CurrentLocale = v_uint32()
        self.FpSoftwareStatusRegister = v_uint32()
        self.SystemReserved1 = vstruct.VArray([ v_ptr32() for i in range(54) ])
        self.ExceptionCode = v_uint32()
        self.ActivationContextStackPointer = v_ptr32()
        self.SpareBytes1 = vstruct.VArray([ v_uint8() for i in range(40) ])
        self.GdiTebBatch = GDI_TEB_BATCH()
        self.RealClientId = CLIENT_ID()
        self.GdiCachedProcessHandle = v_ptr32()
        self.GdiClientPID = v_uint32()
        self.GdiClientTID = v_uint32()
        self.GdiThreadLocalInfo = v_ptr32()
        self.Win32ClientInfo = vstruct.VArray([ v_uint32() for i in range(62) ])
        self.glDispatchTable = vstruct.VArray([ v_ptr32() for i in range(233) ])
        self.glReserved1 = vstruct.VArray([ v_uint32() for i in range(29) ])
        self.glReserved2 = v_ptr32()
        self.glSectionInfo = v_ptr32()
        self.glSection = v_ptr32()
        self.glTable = v_ptr32()
        self.glCurrentRC = v_ptr32()
        self.glContext = v_ptr32()
        self.LastStatusValue = v_uint32()
        self.StaticUnicodeString = UNICODE_STRING()
        self.StaticUnicodeBuffer = vstruct.VArray([ v_uint16() for i in range(261) ])
        self._pad0e0c = v_bytes(size=2)
        self.DeallocationStack = v_ptr32()
        self.TlsSlots = vstruct.VArray([ v_ptr32() for i in range(64) ])
        self.TlsLinks = LIST_ENTRY()
        self.Vdm = v_ptr32()
        self.ReservedForNtRpc = v_ptr32()
        self.DbgSsReserved = vstruct.VArray([ v_ptr32() for i in range(2) ])
        self.HardErrorMode = v_uint32()
        self.Instrumentation = vstruct.VArray([ v_ptr32() for i in range(14) ])
        self.SubProcessTag = v_ptr32()
        self.EtwTraceData = v_ptr32()
        self.WinSockData = v_ptr32()
        self.GdiBatchCount = v_uint32()
        self.InDbgPrint = v_uint8()
        self.FreeStackOnTermination = v_uint8()
        self.HasFiberData = v_uint8()
        self.IdealProcessor = v_uint8()
        self.GuaranteedStackBytes = v_uint32()
        self.ReservedForPerf = v_ptr32()
        self.ReservedForOle = v_ptr32()
        self.WaitingOnLoaderLock = v_uint32()
        self.SparePointer1 = v_uint32()
        self.SoftPatchPtr1 = v_uint32()
        self.SoftPatchPtr2 = v_uint32()
        self.TlsExpansionSlots = v_ptr32()
        self.ImpersonationLocale = v_uint32()
        self.IsImpersonating = v_uint32()
        self.NlsCache = v_ptr32()
        self.pShimData = v_ptr32()
        self.HeapVirtualAffinity = v_uint32()
        self.CurrentTransactionHandle = v_ptr32()
        self.ActiveFrame = v_ptr32()
        self.FlsData = v_ptr32()
        self.SafeThunkCall = v_uint8()
        self.BooleanSpare = vstruct.VArray([ v_uint8() for i in range(3) ])


class _unnamed_6084(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Srb = v_ptr32()


class _unnamed_5227(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint8()
        self.Flags1 = v_uint8()
        self.Flags2 = v_uint8()
        self.BaseHi = v_uint8()


class QUAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UseThisFieldToCopy = v_uint64()


class _unnamed_6080(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Vpb = v_ptr32()
        self.DeviceObject = v_ptr32()


class LIST_ENTRY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()
        self.Blink = v_uint32()


class SID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint8()
        self.SubAuthorityCount = v_uint8()
        self.IdentifierAuthority = SID_IDENTIFIER_AUTHORITY()
        self.SubAuthority = vstruct.VArray([ v_uint32() for i in range(1) ])


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


class _unnamed_6416(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Alignment = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


class ACTIVATION_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class KEVENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class KSEMAPHORE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.Limit = v_uint32()


class _unnamed_5953(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


class MMADDRESS_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_4917()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()


class RTL_CRITICAL_SECTION_DEBUG(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.CreatorBackTraceIndex = v_uint16()
        self.CriticalSection = v_ptr32()
        self.ProcessLocksList = LIST_ENTRY()
        self.EntryCount = v_uint32()
        self.ContentionCount = v_uint32()
        self.Spare = vstruct.VArray([ v_uint32() for i in range(2) ])


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
        self.ObjectLocks = vstruct.VArray([ ERESOURCE() for i in range(4) ])


class SID_AND_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Sid = v_ptr32()
        self.Attributes = v_uint32()


class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.FileHeader = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()


class IO_RESOURCE_REQUIREMENTS_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListSize = v_uint32()
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.SlotNumber = v_uint32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(3) ])
        self.AlternativeLists = v_uint32()
        self.List = vstruct.VArray([ IO_RESOURCE_LIST() for i in range(1) ])


class _unnamed_6258(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Absolute = v_uint8()
        self.Size = v_uint8()
        self.Inserted = v_uint8()
        self.SignalState = v_uint32()
        self.WaitListHead = LIST_ENTRY()


class OBJECT_HANDLE_COUNT_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Process = v_ptr32()
        self.HandleCount = v_uint32()


class _unnamed_4829(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FreeListsInUseTerminate = v_uint16()


class _unnamed_4828(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FreeListsInUseUlong = vstruct.VArray([ v_uint32() for i in range(4) ])


class _unnamed_6160(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Capabilities = v_ptr32()


class _unnamed_6253(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ProviderId = v_uint32()
        self.DataPath = v_ptr32()
        self.BufferSize = v_uint32()
        self.Buffer = v_ptr32()


class OBJECT_HANDLE_COUNT_DATABASE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CountEntries = v_uint32()
        self.HandleCountEntries = vstruct.VArray([ OBJECT_HANDLE_COUNT_ENTRY() for i in range(1) ])


class IO_TIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.TimerFlag = v_uint16()
        self.TimerList = LIST_ENTRY()
        self.TimerRoutine = v_ptr32()
        self.Context = v_ptr32()
        self.DeviceObject = v_ptr32()


class _unnamed_3121(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class ASSEMBLY_STORAGE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class MMSUPPORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WorkingSetExpansionLinks = LIST_ENTRY()
        self.LastTrimTime = LARGE_INTEGER()
        self.Flags = MMSUPPORT_FLAGS()
        self.PageFaultCount = v_uint32()
        self.PeakWorkingSetSize = v_uint32()
        self.GrowthSinceLastEstimate = v_uint32()
        self.MinimumWorkingSetSize = v_uint32()
        self.MaximumWorkingSetSize = v_uint32()
        self.VmWorkingSetList = v_ptr32()
        self.Claim = v_uint32()
        self.NextEstimationSlot = v_uint32()
        self.NextAgingSlot = v_uint32()
        self.EstimatedAvailable = v_uint32()
        self.WorkingSetSize = v_uint32()
        self.WorkingSetMutex = EX_PUSH_LOCK()
        self._pad0048 = v_bytes(size=4)


class PROCESSOR_POWER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IdleFunction = v_ptr32()
        self.Idle0KernelTimeLimit = v_uint32()
        self.Idle0LastTime = v_uint32()
        self.IdleHandlers = v_ptr32()
        self.IdleState = v_ptr32()
        self.IdleHandlersCount = v_uint32()
        self.LastCheck = v_uint64()
        self.IdleTimes = PROCESSOR_IDLE_TIMES()
        self.IdleTime1 = v_uint32()
        self.PromotionCheck = v_uint32()
        self.IdleTime2 = v_uint32()
        self.CurrentThrottle = v_uint8()
        self.ThermalThrottleLimit = v_uint8()
        self.CurrentThrottleIndex = v_uint8()
        self.ThermalThrottleIndex = v_uint8()
        self.LastKernelUserTime = v_uint32()
        self.LastIdleThreadKernelTime = v_uint32()
        self.PackageIdleStartTime = v_uint32()
        self.PackageIdleTime = v_uint32()
        self.DebugCount = v_uint32()
        self.LastSysTime = v_uint32()
        self.TotalIdleStateTime = vstruct.VArray([ v_uint64() for i in range(3) ])
        self.TotalIdleTransitions = vstruct.VArray([ v_uint32() for i in range(3) ])
        self._pad0090 = v_bytes(size=4)
        self.PreviousC3StateTime = v_uint64()
        self.KneeThrottleIndex = v_uint8()
        self.ThrottleLimitIndex = v_uint8()
        self.PerfStatesCount = v_uint8()
        self.ProcessorMinThrottle = v_uint8()
        self.ProcessorMaxThrottle = v_uint8()
        self.EnableIdleAccounting = v_uint8()
        self.LastC3Percentage = v_uint8()
        self.LastAdjustedBusyPercentage = v_uint8()
        self.PromotionCount = v_uint32()
        self.DemotionCount = v_uint32()
        self.ErrorCount = v_uint32()
        self.RetryCount = v_uint32()
        self.Flags = v_uint32()
        self._pad00b8 = v_bytes(size=4)
        self.PerfCounterFrequency = LARGE_INTEGER()
        self.PerfTickCount = v_uint32()
        self._pad00c8 = v_bytes(size=4)
        self.PerfTimer = KTIMER()
        self.PerfDpc = KDPC()
        self.PerfStates = v_ptr32()
        self.PerfSetThrottle = v_ptr32()
        self.LastC3KernelUserTime = v_uint32()
        self.LastPackageIdleTime = v_uint32()


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


class _unnamed_6092(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.StartSid = v_ptr32()
        self.SidList = v_ptr32()
        self.SidListLength = v_uint32()


class KGATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pad = v_uint16()
        self.Limit = v_uint16()
        self.Base = v_uint32()


class HEAP_PSEUDO_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()


class MMSUPPORT_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SessionSpace = v_uint8()
        self.MemoryPriority = v_uint8()
        self.GrowWsleHash = v_uint16()


class _unnamed_3661(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Bytes = _unnamed_5227()


class EXCEPTION_REGISTRATION_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Handler = v_ptr32()


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
        self.Queue = _unnamed_4074()
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
        self.CompressedChunkSizes = vstruct.VArray([ v_uint32() for i in range(1) ])


class PEB_FREE_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Size = v_uint32()


class KTIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.DueTime = ULARGE_INTEGER()
        self.TimerListEntry = LIST_ENTRY()
        self.Dpc = v_ptr32()
        self.Period = v_uint32()


class OBJECT_CREATE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Attributes = v_uint32()
        self.RootDirectory = v_ptr32()
        self.ParseContext = v_ptr32()
        self.ProbeMode = v_uint8()
        self._pad0010 = v_bytes(size=3)
        self.PagedPoolCharge = v_uint32()
        self.NonPagedPoolCharge = v_uint32()
        self.SecurityDescriptorCharge = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.SecurityQos = v_ptr32()
        self.SecurityQualityOfService = SECURITY_QUALITY_OF_SERVICE()


class OBJECT_HEADER_CREATOR_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TypeList = LIST_ENTRY()
        self.CreatorUniqueProcess = v_ptr32()
        self.CreatorBackTraceIndex = v_uint16()
        self.Reserved = v_uint16()


class PAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = FAST_MUTEX()
        self._pad00c0 = v_bytes(size=32)


class EX_PUSH_LOCK_WAIT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WakeGate = KGATE()
        self.Next = v_ptr32()
        self.Last = v_ptr32()
        self.Previous = v_ptr32()
        self.ShareCount = v_uint32()
        self.Flags = v_uint32()
        self._pad0030 = v_bytes(size=12)


class LUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class DEVICE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DosDevicesDirectory = v_ptr32()
        self.GlobalDosDevicesDirectory = v_ptr32()
        self.ReferenceCount = v_uint32()
        self.DriveMap = v_uint32()
        self.DriveType = vstruct.VArray([ v_uint8() for i in range(32) ])


class _unnamed_6195(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceTextType = v_uint32()
        self.LocaleId = v_uint32()


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


class _unnamed_6190(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IdType = v_uint32()


class CLIENT_ID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UniqueProcess = v_ptr32()
        self.UniqueThread = v_ptr32()


class NPAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = v_uint32()
        self._pad00c0 = v_bytes(size=60)


class RTL_STACK_TRACE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashChain = v_ptr32()
        self.TraceCount = v_uint32()
        self.Index = v_uint16()
        self.Depth = v_uint16()
        self.BackTrace = vstruct.VArray([ v_ptr32() for i in range(32) ])


class OBJECT_DUMP_CONTROL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Stream = v_ptr32()
        self.Detail = v_uint32()


class _unnamed_6064(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_ptr32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class GUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data1 = v_uint32()
        self.Data2 = v_uint16()
        self.Data3 = v_uint16()
        self.Data4 = vstruct.VArray([ v_uint8() for i in range(8) ])


class _unnamed_6119(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_ptr32()
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Interface = v_ptr32()
        self.InterfaceSpecificData = v_ptr32()


class HANDLE_TRACE_DB_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientId = CLIENT_ID()
        self.Handle = v_ptr32()
        self.Type = v_uint32()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(16) ])


class KAPC_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ApcListHead = vstruct.VArray([ LIST_ENTRY() for i in range(2) ])
        self.Process = v_ptr32()
        self.KernelApcInProgress = v_uint8()
        self.KernelApcPending = v_uint8()
        self.UserApcPending = v_uint8()
        self._pad0018 = v_bytes(size=1)


class _unnamed_4074(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self._pad0028 = v_bytes(size=32)


class _unnamed_6069(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.IoControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


class PS_IMPERSONATION_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Token = v_ptr32()
        self.CopyOnOpen = v_uint8()
        self.EffectiveOnly = v_uint8()
        self._pad0008 = v_bytes(size=2)
        self.ImpersonationLevel = v_uint32()


class _unnamed_3185(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class FAST_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Gate = KEVENT()
        self.OldIrql = v_uint32()


class KDPC_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DpcListHead = LIST_ENTRY()
        self.DpcLock = v_uint32()
        self.DpcQueueDepth = v_uint32()
        self.DpcCount = v_uint32()


class KIDTENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint16()
        self.Selector = v_uint16()
        self.Access = v_uint16()
        self.ExtendedOffset = v_uint16()


class HARDWARE_PTE_X86(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class _unnamed_5286(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Create = _unnamed_5937()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorFunction = v_uint8()
        self.MinorFunction = v_uint8()
        self.Flags = v_uint8()
        self.Control = v_uint8()
        self.Parameters = _unnamed_5286()
        self.DeviceObject = v_ptr32()
        self.FileObject = v_ptr32()
        self.CompletionRoutine = v_ptr32()
        self.Context = v_ptr32()


class HEAP_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()
        self.TagIndex = v_uint16()
        self.CreatorBackTraceIndex = v_uint16()
        self.TagName = vstruct.VArray([ v_uint16() for i in range(24) ])


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


class STRING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.MaximumLength = v_uint16()
        self.Buffer = v_ptr32()


class KNODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeadStackList = SLIST_HEADER()
        self.PfnDereferenceSListHead = SLIST_HEADER()
        self.ProcessorMask = v_uint32()
        self.Color = v_uint8()
        self.Seed = v_uint8()
        self.NodeNumber = v_uint8()
        self.Flags = flags()
        self.MmShiftedColor = v_uint32()
        self.FreeCount = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.PfnDeferredList = v_ptr32()
        self._pad0040 = v_bytes(size=24)


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
        self.AssociatedIrp = _unnamed_5080()
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
        self.Overlay = _unnamed_5083()
        self.CancelRoutine = v_ptr32()
        self.UserBuffer = v_ptr32()
        self.Tail = _unnamed_5084()


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
        self.Descriptors = vstruct.VArray([ IO_RESOURCE_DESCRIPTOR() for i in range(1) ])


class KUSER_SHARED_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TickCountLowDeprecated = v_uint32()
        self.TickCountMultiplier = v_uint32()
        self.InterruptTime = KSYSTEM_TIME()
        self.SystemTime = KSYSTEM_TIME()
        self.TimeZoneBias = KSYSTEM_TIME()
        self.ImageNumberLow = v_uint16()
        self.ImageNumberHigh = v_uint16()
        self.NtSystemRoot = vstruct.VArray([ v_uint16() for i in range(260) ])
        self.MaxStackTraceDepth = v_uint32()
        self.CryptoExponent = v_uint32()
        self.TimeZoneId = v_uint32()
        self.LargePageMinimum = v_uint32()
        self.Reserved2 = vstruct.VArray([ v_uint32() for i in range(7) ])
        self.NtProductType = v_uint32()
        self.ProductTypeIsValid = v_uint8()
        self._pad026c = v_bytes(size=3)
        self.NtMajorVersion = v_uint32()
        self.NtMinorVersion = v_uint32()
        self.ProcessorFeatures = vstruct.VArray([ v_uint8() for i in range(64) ])
        self.Reserved1 = v_uint32()
        self.Reserved3 = v_uint32()
        self.TimeSlip = v_uint32()
        self.AlternativeArchitecture = v_uint32()
        self._pad02c8 = v_bytes(size=4)
        self.SystemExpirationDate = LARGE_INTEGER()
        self.SuiteMask = v_uint32()
        self.KdDebuggerEnabled = v_uint8()
        self.NXSupportPolicy = v_uint8()
        self._pad02d8 = v_bytes(size=2)
        self.ActiveConsoleId = v_uint32()
        self.DismountCount = v_uint32()
        self.ComPlusPackage = v_uint32()
        self.LastSystemRITEventTickCount = v_uint32()
        self.NumberOfPhysicalPages = v_uint32()
        self.SafeBootMode = v_uint8()
        self._pad02f0 = v_bytes(size=3)
        self.TraceLogging = v_uint32()
        self._pad02f8 = v_bytes(size=4)
        self.TestRetInstruction = v_uint64()
        self.SystemCall = v_uint32()
        self.SystemCallReturn = v_uint32()
        self.SystemCallPad = vstruct.VArray([ v_uint64() for i in range(3) ])
        self.TickCount = KSYSTEM_TIME()
        self._pad0330 = v_bytes(size=4)
        self.Cookie = v_uint32()
        self.Wow64SharedInformation = vstruct.VArray([ v_uint32() for i in range(16) ])
        self._pad0378 = v_bytes(size=4)


class _unnamed_6496(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint32()
        self.Length = v_uint32()
        self.Reserved = v_uint32()


class FNSAVE_FORMAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlWord = v_uint32()
        self.StatusWord = v_uint32()
        self.TagWord = v_uint32()
        self.ErrorOffset = v_uint32()
        self.ErrorSelector = v_uint32()
        self.DataOffset = v_uint32()
        self.DataSelector = v_uint32()
        self.RegisterArea = vstruct.VArray([ v_uint8() for i in range(80) ])


class KSPECIAL_REGISTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Cr0 = v_uint32()
        self.Cr2 = v_uint32()
        self.Cr3 = v_uint32()
        self.Cr4 = v_uint32()
        self.KernelDr0 = v_uint32()
        self.KernelDr1 = v_uint32()
        self.KernelDr2 = v_uint32()
        self.KernelDr3 = v_uint32()
        self.KernelDr6 = v_uint32()
        self.KernelDr7 = v_uint32()
        self.Gdtr = DESCRIPTOR()
        self.Idtr = DESCRIPTOR()
        self.Tr = v_uint16()
        self.Ldtr = v_uint16()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(6) ])


class _unnamed_6424(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumChannel = v_uint32()
        self.MaximumChannel = v_uint32()


class _unnamed_6427(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data = vstruct.VArray([ v_uint32() for i in range(3) ])


class _unnamed_6421(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumVector = v_uint32()
        self.MaximumVector = v_uint32()


class FS_FILTER_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AcquireForModifiedPageWriter = _unnamed_6355()
        self._pad0014 = v_bytes(size=12)


class HEAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = HEAP_ENTRY()
        self.Signature = v_uint32()
        self.Flags = v_uint32()
        self.ForceFlags = v_uint32()
        self.VirtualMemoryThreshold = v_uint32()
        self.SegmentReserve = v_uint32()
        self.SegmentCommit = v_uint32()
        self.DeCommitFreeBlockThreshold = v_uint32()
        self.DeCommitTotalFreeThreshold = v_uint32()
        self.TotalFreeSize = v_uint32()
        self.MaximumAllocationSize = v_uint32()
        self.ProcessHeapsListIndex = v_uint16()
        self.HeaderValidateLength = v_uint16()
        self.HeaderValidateCopy = v_ptr32()
        self.NextAvailableTagIndex = v_uint16()
        self.MaximumTagIndex = v_uint16()
        self.TagEntries = v_ptr32()
        self.UCRSegments = v_ptr32()
        self.UnusedUnCommittedRanges = v_ptr32()
        self.AlignRound = v_uint32()
        self.AlignMask = v_uint32()
        self.VirtualAllocdBlocks = LIST_ENTRY()
        self.Segments = vstruct.VArray([ v_ptr32() for i in range(64) ])
        self.u = _unnamed_4828()
        self.u2 = _unnamed_4829()
        self.AllocatorBackTraceIndex = v_uint16()
        self.NonDedicatedListLength = v_uint32()
        self.LargeBlocksIndex = v_ptr32()
        self.PseudoTagEntries = v_ptr32()
        self.FreeLists = vstruct.VArray([ LIST_ENTRY() for i in range(128) ])
        self.LockVariable = v_ptr32()
        self.CommitRoutine = v_ptr32()
        self.FrontEndHeap = v_ptr32()
        self.FrontHeapLockCount = v_uint16()
        self.FrontEndHeapType = v_uint8()
        self.LastSegmentIndex = v_uint8()


class MAILSLOT_CREATE_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MailslotQuota = v_uint32()
        self.MaximumMessageSize = v_uint32()
        self.ReadTimeout = LARGE_INTEGER()
        self.TimeoutSpecified = v_uint8()
        self._pad0018 = v_bytes(size=7)


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
        self.Privilege = vstruct.VArray([ LUID_AND_ATTRIBUTES() for i in range(1) ])


class CM_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.List = vstruct.VArray([ CM_FULL_RESOURCE_DESCRIPTOR() for i in range(1) ])


class _unnamed_6429(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.MinBusNumber = v_uint32()
        self.MaxBusNumber = v_uint32()
        self.Reserved = v_uint32()


class RTL_USER_PROCESS_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MaximumLength = v_uint32()
        self.Length = v_uint32()
        self.Flags = v_uint32()
        self.DebugFlags = v_uint32()
        self.ConsoleHandle = v_ptr32()
        self.ConsoleFlags = v_uint32()
        self.StandardInput = v_ptr32()
        self.StandardOutput = v_ptr32()
        self.StandardError = v_ptr32()
        self.CurrentDirectory = CURDIR()
        self.DllPath = UNICODE_STRING()
        self.ImagePathName = UNICODE_STRING()
        self.CommandLine = UNICODE_STRING()
        self.Environment = v_ptr32()
        self.StartingX = v_uint32()
        self.StartingY = v_uint32()
        self.CountX = v_uint32()
        self.CountY = v_uint32()
        self.CountCharsX = v_uint32()
        self.CountCharsY = v_uint32()
        self.FillAttribute = v_uint32()
        self.WindowFlags = v_uint32()
        self.ShowWindowFlags = v_uint32()
        self.WindowTitle = UNICODE_STRING()
        self.DesktopInfo = UNICODE_STRING()
        self.ShellInfo = UNICODE_STRING()
        self.RuntimeData = UNICODE_STRING()
        self.CurrentDirectores = vstruct.VArray([ RTL_DRIVE_LETTER_CURDIR() for i in range(32) ])


class FILE_GET_QUOTA_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextEntryOffset = v_uint32()
        self.SidLength = v_uint32()
        self.Sid = SID()


class _unnamed_6077(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.SecurityDescriptor = v_ptr32()


class _unnamed_6074(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.Length = v_uint32()


class SINGLE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()


class _unnamed_6492(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Channel = v_uint32()
        self.Port = v_uint32()
        self.Reserved1 = v_uint32()


class FX_SAVE_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.U = _unnamed_3538()
        self.NpxSavedCpu = v_uint32()
        self.Cr0NpxState = v_uint32()


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


class FS_FILTER_CALLBACK_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfFsFilterCallbackData = v_uint32()
        self.Operation = v_uint8()
        self.Reserved = v_uint8()
        self._pad0008 = v_bytes(size=2)
        self.DeviceObject = v_ptr32()
        self.FileObject = v_ptr32()
        self.Parameters = FS_FILTER_PARAMETERS()


class _unnamed_6105(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()


class DRIVER_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DriverObject = v_ptr32()
        self.AddDevice = v_ptr32()
        self.Count = v_uint32()
        self.ServiceKeyName = UNICODE_STRING()
        self.ClientDriverExtension = v_ptr32()
        self.FsFilterCallbacks = v_ptr32()


class _unnamed_6355(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EndingOffset = v_ptr32()
        self.ResourceToRelease = v_ptr32()


class KDEVICE_QUEUE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceListEntry = LIST_ENTRY()
        self.SortKey = v_uint32()
        self.Inserted = v_uint8()
        self._pad0010 = v_bytes(size=3)


class flags(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Removable = v_uint8()


class PAGEFAULT_HISTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CurrentIndex = v_uint32()
        self.MaxIndex = v_uint32()
        self.SpinLock = v_uint32()
        self.Reserved = v_ptr32()
        self.WatchInfo = vstruct.VArray([ PROCESS_WS_WATCH_INFORMATION() for i in range(1) ])


class _unnamed_6483(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Generic = _unnamed_6485()


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Flags = v_uint16()
        self.u = _unnamed_6483()



