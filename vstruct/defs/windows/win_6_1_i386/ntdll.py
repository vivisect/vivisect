# Version: 6.1
# Architecture: i386
import vstruct
from vstruct.primitives import *

KPROCESS_STATE = v_enum()
KPROCESS_STATE.ProcessInMemory = 0
KPROCESS_STATE.ProcessOutOfMemory = 1
KPROCESS_STATE.ProcessInTransition = 2
KPROCESS_STATE.ProcessOutTransition = 3
KPROCESS_STATE.ProcessInSwap = 4
KPROCESS_STATE.ProcessOutSwap = 5
KPROCESS_STATE.ProcessAllSwapStates = 6


WHEA_ERROR_SEVERITY = v_enum()
WHEA_ERROR_SEVERITY.WheaErrSevRecoverable = 0
WHEA_ERROR_SEVERITY.WheaErrSevFatal = 1
WHEA_ERROR_SEVERITY.WheaErrSevCorrected = 2
WHEA_ERROR_SEVERITY.WheaErrSevInformational = 3


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
REG_NOTIFY_CLASS.RegNtPreFlushKey = 30
REG_NOTIFY_CLASS.RegNtPostFlushKey = 31
REG_NOTIFY_CLASS.RegNtPreLoadKey = 32
REG_NOTIFY_CLASS.RegNtPostLoadKey = 33
REG_NOTIFY_CLASS.RegNtPreUnLoadKey = 34
REG_NOTIFY_CLASS.RegNtPostUnLoadKey = 35
REG_NOTIFY_CLASS.RegNtPreQueryKeySecurity = 36
REG_NOTIFY_CLASS.RegNtPostQueryKeySecurity = 37
REG_NOTIFY_CLASS.RegNtPreSetKeySecurity = 38
REG_NOTIFY_CLASS.RegNtPostSetKeySecurity = 39
REG_NOTIFY_CLASS.RegNtCallbackObjectContextCleanup = 40
REG_NOTIFY_CLASS.RegNtPreRestoreKey = 41
REG_NOTIFY_CLASS.RegNtPostRestoreKey = 42
REG_NOTIFY_CLASS.RegNtPreSaveKey = 43
REG_NOTIFY_CLASS.RegNtPostSaveKey = 44
REG_NOTIFY_CLASS.RegNtPreReplaceKey = 45
REG_NOTIFY_CLASS.RegNtPostReplaceKey = 46
REG_NOTIFY_CLASS.MaxRegNtNotifyClass = 47


DEVICE_RELATION_TYPE = v_enum()
DEVICE_RELATION_TYPE.BusRelations = 0
DEVICE_RELATION_TYPE.EjectionRelations = 1
DEVICE_RELATION_TYPE.PowerRelations = 2
DEVICE_RELATION_TYPE.RemovalRelations = 3
DEVICE_RELATION_TYPE.TargetDeviceRelation = 4
DEVICE_RELATION_TYPE.SingleBusRelations = 5
DEVICE_RELATION_TYPE.TransportRelations = 6


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
FILE_INFORMATION_CLASS.FileIoStatusBlockRangeInformation = 42
FILE_INFORMATION_CLASS.FileIoPriorityHintInformation = 43
FILE_INFORMATION_CLASS.FileSfioReserveInformation = 44
FILE_INFORMATION_CLASS.FileSfioVolumeInformation = 45
FILE_INFORMATION_CLASS.FileHardLinkInformation = 46
FILE_INFORMATION_CLASS.FileProcessIdsUsingFileInformation = 47
FILE_INFORMATION_CLASS.FileNormalizedNameInformation = 48
FILE_INFORMATION_CLASS.FileNetworkPhysicalNameInformation = 49
FILE_INFORMATION_CLASS.FileIdGlobalTxDirectoryInformation = 50
FILE_INFORMATION_CLASS.FileIsRemoteDeviceInformation = 51
FILE_INFORMATION_CLASS.FileAttributeCacheInformation = 52
FILE_INFORMATION_CLASS.FileNumaNodeInformation = 53
FILE_INFORMATION_CLASS.FileStandardLinkInformation = 54
FILE_INFORMATION_CLASS.FileRemoteProtocolInformation = 55
FILE_INFORMATION_CLASS.FileMaximumInformation = 56


ALTERNATIVE_ARCHITECTURE_TYPE = v_enum()
ALTERNATIVE_ARCHITECTURE_TYPE.StandardDesign = 0
ALTERNATIVE_ARCHITECTURE_TYPE.NEC98x86 = 1
ALTERNATIVE_ARCHITECTURE_TYPE.EndAlternatives = 2


BUS_QUERY_ID_TYPE = v_enum()
BUS_QUERY_ID_TYPE.BusQueryDeviceID = 0
BUS_QUERY_ID_TYPE.BusQueryHardwareIDs = 1
BUS_QUERY_ID_TYPE.BusQueryCompatibleIDs = 2
BUS_QUERY_ID_TYPE.BusQueryInstanceID = 3
BUS_QUERY_ID_TYPE.BusQueryDeviceSerialNumber = 4
BUS_QUERY_ID_TYPE.BusQueryContainerID = 5


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


WHEA_ERROR_SOURCE_TYPE = v_enum()
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeMCE = 0
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeCMC = 1
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeCPE = 2
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeNMI = 3
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypePCIe = 4
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeGeneric = 5
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeINIT = 6
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeBOOT = 7
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeSCIGeneric = 8
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeIPFMCA = 9
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeIPFCMC = 10
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeIPFCPE = 11
WHEA_ERROR_SOURCE_TYPE.WheaErrSrcTypeMax = 12


PROC_HYPERVISOR_STATE = v_enum()
PROC_HYPERVISOR_STATE.ProcHypervisorNone = 0
PROC_HYPERVISOR_STATE.ProcHypervisorPresent = 1
PROC_HYPERVISOR_STATE.ProcHypervisorPower = 2


RTL_GENERIC_COMPARE_RESULTS = v_enum()
RTL_GENERIC_COMPARE_RESULTS.GenericLessThan = 0
RTL_GENERIC_COMPARE_RESULTS.GenericGreaterThan = 1
RTL_GENERIC_COMPARE_RESULTS.GenericEqual = 2


KWAIT_BLOCK_STATE = v_enum()
KWAIT_BLOCK_STATE.WaitBlockBypassStart = 0
KWAIT_BLOCK_STATE.WaitBlockBypassComplete = 1
KWAIT_BLOCK_STATE.WaitBlockActive = 2
KWAIT_BLOCK_STATE.WaitBlockInactive = 3
KWAIT_BLOCK_STATE.WaitBlockAllStates = 4


WHEA_ERROR_TYPE = v_enum()
WHEA_ERROR_TYPE.WheaErrTypeProcessor = 0
WHEA_ERROR_TYPE.WheaErrTypeMemory = 1
WHEA_ERROR_TYPE.WheaErrTypePCIExpress = 2
WHEA_ERROR_TYPE.WheaErrTypeNMI = 3
WHEA_ERROR_TYPE.WheaErrTypePCIXBus = 4
WHEA_ERROR_TYPE.WheaErrTypePCIXDevice = 5
WHEA_ERROR_TYPE.WheaErrTypeGeneric = 6


PROCESSOR_CACHE_TYPE = v_enum()
PROCESSOR_CACHE_TYPE.CacheUnified = 0
PROCESSOR_CACHE_TYPE.CacheInstruction = 1
PROCESSOR_CACHE_TYPE.CacheData = 2
PROCESSOR_CACHE_TYPE.CacheTrace = 3


MCA_EXCEPTION_TYPE = v_enum()
MCA_EXCEPTION_TYPE.HAL_MCE_RECORD = 0
MCA_EXCEPTION_TYPE.HAL_MCA_RECORD = 1


EVENT_TYPE = v_enum()
EVENT_TYPE.NotificationEvent = 0
EVENT_TYPE.SynchronizationEvent = 1


KSPIN_LOCK_QUEUE_NUMBER = v_enum()
KSPIN_LOCK_QUEUE_NUMBER.LockQueueUnusedSpare0 = 0
KSPIN_LOCK_QUEUE_NUMBER.LockQueueExpansionLock = 1
KSPIN_LOCK_QUEUE_NUMBER.LockQueueUnusedSpare2 = 2
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
KSPIN_LOCK_QUEUE_NUMBER.LockQueueMaximumLock = 17


TP_CALLBACK_PRIORITY = v_enum()
TP_CALLBACK_PRIORITY.TP_CALLBACK_PRIORITY_HIGH = 0
TP_CALLBACK_PRIORITY.TP_CALLBACK_PRIORITY_NORMAL = 1
TP_CALLBACK_PRIORITY.TP_CALLBACK_PRIORITY_LOW = 2
TP_CALLBACK_PRIORITY.TP_CALLBACK_PRIORITY_INVALID = 3


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
FSINFOCLASS.FileFsVolumeFlagsInformation = 10
FSINFOCLASS.FileFsMaximumInformation = 11


WORKING_SET_TYPE = v_enum()
WORKING_SET_TYPE.WorkingSetTypeUser = 0
WORKING_SET_TYPE.WorkingSetTypeSession = 1
WORKING_SET_TYPE.WorkingSetTypeSystemTypes = 2
WORKING_SET_TYPE.WorkingSetTypeSystemCache = 2
WORKING_SET_TYPE.WorkingSetTypePagedPool = 3
WORKING_SET_TYPE.WorkingSetTypeSystemPtes = 4
WORKING_SET_TYPE.WorkingSetTypeMaximum = 5


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


IO_PRIORITY_HINT = v_enum()
IO_PRIORITY_HINT.IoPriorityVeryLow = 0
IO_PRIORITY_HINT.IoPriorityLow = 1
IO_PRIORITY_HINT.IoPriorityNormal = 2
IO_PRIORITY_HINT.IoPriorityHigh = 3
IO_PRIORITY_HINT.IoPriorityCritical = 4
IO_PRIORITY_HINT.MaxIoPriorityTypes = 5


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


HEAP_FAILURE_TYPE = v_enum()
HEAP_FAILURE_TYPE.heap_failure_internal = 0
HEAP_FAILURE_TYPE.heap_failure_unknown = 1
HEAP_FAILURE_TYPE.heap_failure_generic = 2
HEAP_FAILURE_TYPE.heap_failure_entry_corruption = 3
HEAP_FAILURE_TYPE.heap_failure_multiple_entries_corruption = 4
HEAP_FAILURE_TYPE.heap_failure_virtual_block_corruption = 5
HEAP_FAILURE_TYPE.heap_failure_buffer_overrun = 6
HEAP_FAILURE_TYPE.heap_failure_buffer_underrun = 7
HEAP_FAILURE_TYPE.heap_failure_block_not_busy = 8
HEAP_FAILURE_TYPE.heap_failure_invalid_argument = 9
HEAP_FAILURE_TYPE.heap_failure_usage_after_free = 10
HEAP_FAILURE_TYPE.heap_failure_cross_heap_operation = 11
HEAP_FAILURE_TYPE.heap_failure_freelists_corruption = 12
HEAP_FAILURE_TYPE.heap_failure_listentry_corruption = 13


DEVICE_TEXT_TYPE = v_enum()
DEVICE_TEXT_TYPE.DeviceTextDescription = 0
DEVICE_TEXT_TYPE.DeviceTextLocationInformation = 1


POWER_STATE_TYPE = v_enum()
POWER_STATE_TYPE.SystemPowerState = 0
POWER_STATE_TYPE.DevicePowerState = 1


IRQ_PRIORITY = v_enum()
IRQ_PRIORITY.IrqPriorityUndefined = 0
IRQ_PRIORITY.IrqPriorityLow = 1
IRQ_PRIORITY.IrqPriorityNormal = 2
IRQ_PRIORITY.IrqPriorityHigh = 3


KWAIT_STATE = v_enum()
KWAIT_STATE.WaitInProgress = 0
KWAIT_STATE.WaitCommitted = 1
KWAIT_STATE.WaitAborted = 2
KWAIT_STATE.MaximumWaitState = 3


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


SECURITY_OPERATION_CODE = v_enum()
SECURITY_OPERATION_CODE.SetSecurityDescriptor = 0
SECURITY_OPERATION_CODE.QuerySecurityDescriptor = 1
SECURITY_OPERATION_CODE.DeleteSecurityDescriptor = 2
SECURITY_OPERATION_CODE.AssignSecurityDescriptor = 3


PP_NPAGED_LOOKASIDE_NUMBER = v_enum()
PP_NPAGED_LOOKASIDE_NUMBER.LookasideSmallIrpList = 0
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMediumIrpList = 1
PP_NPAGED_LOOKASIDE_NUMBER.LookasideLargeIrpList = 2
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMdlList = 3
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCreateInfoList = 4
PP_NPAGED_LOOKASIDE_NUMBER.LookasideNameBufferList = 5
PP_NPAGED_LOOKASIDE_NUMBER.LookasideTwilightList = 6
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCompletionList = 7
PP_NPAGED_LOOKASIDE_NUMBER.LookasideScratchBufferList = 8
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMaximumList = 9


WHEA_ERROR_PACKET_DATA_FORMAT = v_enum()
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatIPFSalRecord = 0
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatXPFMCA = 1
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatMemory = 2
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatPCIExpress = 3
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatNMIPort = 4
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatPCIXBus = 5
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatPCIXDevice = 6
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatGeneric = 7
WHEA_ERROR_PACKET_DATA_FORMAT.WheaDataFormatMax = 8


FS_FILTER_STREAM_FO_NOTIFICATION_TYPE = v_enum()
FS_FILTER_STREAM_FO_NOTIFICATION_TYPE.NotifyTypeCreate = 0
FS_FILTER_STREAM_FO_NOTIFICATION_TYPE.NotifyTypeRetired = 1


DISPLAYCONFIG_SCANLINE_ORDERING = v_enum()
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_UNSPECIFIED = 0
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_PROGRESSIVE = 1
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED = 2
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED_UPPERFIELDFIRST = 2
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_INTERLACED_LOWERFIELDFIRST = 3
DISPLAYCONFIG_SCANLINE_ORDERING.DISPLAYCONFIG_SCANLINE_ORDERING_FORCE_UINT32 = -1


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
INTERFACE_TYPE.Vmcs = 16
INTERFACE_TYPE.MaximumInterfaceType = 17


PS_RESOURCE_TYPE = v_enum()
PS_RESOURCE_TYPE.PsResourceNonPagedPool = 0
PS_RESOURCE_TYPE.PsResourcePagedPool = 1
PS_RESOURCE_TYPE.PsResourcePageFile = 2
PS_RESOURCE_TYPE.PsResourceWorkingSet = 3
PS_RESOURCE_TYPE.PsResourceCpuRate = 4
PS_RESOURCE_TYPE.PsResourceMax = 5


MM_PAGE_ACCESS_TYPE = v_enum()
MM_PAGE_ACCESS_TYPE.MmPteAccessType = 0
MM_PAGE_ACCESS_TYPE.MmCcReadAheadType = 1
MM_PAGE_ACCESS_TYPE.MmPfnRepurposeType = 2
MM_PAGE_ACCESS_TYPE.MmMaximumPageAccessType = 3


PF_FILE_ACCESS_TYPE = v_enum()
PF_FILE_ACCESS_TYPE.PfFileAccessTypeRead = 0
PF_FILE_ACCESS_TYPE.PfFileAccessTypeWrite = 1
PF_FILE_ACCESS_TYPE.PfFileAccessTypeMax = 2


HARDWARE_COUNTER_TYPE = v_enum()
HARDWARE_COUNTER_TYPE.PMCCounter = 0
HARDWARE_COUNTER_TYPE.MaxHardwareCounterType = 1


ReplacesCorHdrNumericDefines = v_enum()
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_ILONLY = 1
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_32BITREQUIRED = 2
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_IL_LIBRARY = 4
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_STRONGNAMESIGNED = 8
ReplacesCorHdrNumericDefines.COMIMAGE_FLAGS_NATIVE_ENTRYPOINT = 16
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
ReplacesCorHdrNumericDefines.COR_VTABLE_FROM_UNMANAGED_RETAIN_APPDOMAIN = 8
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


class _unnamed_9072(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint32()


class IO_PRIORITY_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint32()
        self.ThreadPriority = v_uint32()
        self.PagePriority = v_uint32()
        self.IoPriority = v_uint32()


class SID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint8()
        self.SubAuthorityCount = v_uint8()
        self.IdentifierAuthority = SID_IDENTIFIER_AUTHORITY()
        self.SubAuthority = vstruct.VArray([ v_uint32() for i in range(1) ])


class WHEA_ERROR_PACKET_V2(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.Version = v_uint32()
        self.Length = v_uint32()
        self.Flags = WHEA_ERROR_PACKET_FLAGS()
        self.ErrorType = v_uint32()
        self.ErrorSeverity = v_uint32()
        self.ErrorSourceId = v_uint32()
        self.ErrorSourceType = v_uint32()
        self.NotifyType = GUID()
        self.Context = v_uint64()
        self.DataFormat = v_uint32()
        self.Reserved1 = v_uint32()
        self.DataOffset = v_uint32()
        self.DataLength = v_uint32()
        self.PshedDataOffset = v_uint32()
        self.PshedDataLength = v_uint32()


class GROUP_AFFINITY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mask = v_uint32()
        self.Group = v_uint16()
        self.Reserved = vstruct.VArray([ v_uint16() for i in range(3) ])


class _unnamed_8002(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()


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


class PERFINFO_GROUPMASK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Masks = vstruct.VArray([ v_uint32() for i in range(8) ])


class HANDLE_TABLE_ENTRY_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AuditMask = v_uint32()


class WHEA_ERROR_RECORD_SECTION_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SectionOffset = v_uint32()
        self.SectionLength = v_uint32()
        self.Revision = WHEA_REVISION()
        self.ValidBits = WHEA_ERROR_RECORD_SECTION_DESCRIPTOR_VALIDBITS()
        self.Reserved = v_uint8()
        self.Flags = WHEA_ERROR_RECORD_SECTION_DESCRIPTOR_FLAGS()
        self.SectionType = GUID()
        self.FRUId = GUID()
        self.SectionSeverity = v_uint32()
        self.FRUText = vstruct.VArray([ v_uint8() for i in range(20) ])


class PS_CPU_QUOTA_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.SessionId = v_uint32()
        self.CpuShareWeight = v_uint32()
        self.CapturedWeightData = PSP_CPU_SHARE_CAPTURED_WEIGHT_DATA()
        self.DuplicateInputMarker = v_uint32()
        self._pad0040 = v_bytes(size=36)
        self.CycleCredit = v_uint64()
        self.BlockCurrentGeneration = v_uint32()
        self.CpuCyclePercent = v_uint32()
        self.CyclesFinishedForCurrentGeneration = v_uint8()
        self._pad0080 = v_bytes(size=47)
        self.Cpu = vstruct.VArray([ PS_PER_CPU_QUOTA_CACHE_AWARE() for i in range(32) ])


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


class _unnamed_9787(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EndingOffset = v_ptr32()
        self.ResourceToRelease = v_ptr32()


class CM_PARTIAL_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Revision = v_uint16()
        self.Count = v_uint32()
        self.PartialDescriptors = vstruct.VArray([ CM_PARTIAL_RESOURCE_DESCRIPTOR() for i in range(1) ])


class _unnamed_9788(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ResourceToRelease = v_ptr32()


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


class _unnamed_5734(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFunction = v_uint32()


class _unnamed_5731(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()


class RTL_BALANCED_LINKS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Parent = v_ptr32()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.Balance = v_uint8()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(3) ])


class KPROCESS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.ProfileListHead = LIST_ENTRY()
        self.DirectoryTableBase = v_uint32()
        self.LdtDescriptor = KGDTENTRY()
        self.Int21Descriptor = KIDTENTRY()
        self.ThreadListHead = LIST_ENTRY()
        self.ProcessLock = v_uint32()
        self.Affinity = KAFFINITY_EX()
        self.ReadyListHead = LIST_ENTRY()
        self.SwapListEntry = SINGLE_LIST_ENTRY()
        self.ActiveProcessors = KAFFINITY_EX()
        self.AutoAlignment = v_uint32()
        self.BasePriority = v_uint8()
        self.QuantumReset = v_uint8()
        self.Visited = v_uint8()
        self.Unused3 = v_uint8()
        self.ThreadSeed = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.IdealNode = vstruct.VArray([ v_uint16() for i in range(1) ])
        self.IdealGlobalNode = v_uint16()
        self.Flags = KEXECUTE_OPTIONS()
        self.Unused1 = v_uint8()
        self.IopmOffset = v_uint16()
        self.Unused4 = v_uint32()
        self.StackCount = KSTACK_COUNT()
        self.ProcessListEntry = LIST_ENTRY()
        self.CycleTime = v_uint64()
        self.KernelTime = v_uint32()
        self.UserTime = v_uint32()
        self.VdmTrapcHandler = v_ptr32()
        self._pad0098 = v_bytes(size=4)


class DEVICE_OBJECT_POWER_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class _unnamed_7305(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self._pad0028 = v_bytes(size=32)


class _unnamed_7909(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.CompletionFilter = v_uint32()


class WHEA_ERROR_RECORD_SECTION_DESCRIPTOR_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Primary = v_uint32()


class TP_CALLBACK_ENVIRON_V3(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint32()
        self.Pool = v_ptr32()
        self.CleanupGroup = v_ptr32()
        self.CleanupGroupCancelCallback = v_ptr32()
        self.RaceDll = v_ptr32()
        self.ActivationContext = v_ptr32()
        self.FinalizationCallback = v_ptr32()
        self.u = _unnamed_5731()
        self.CallbackPriority = v_uint32()
        self.Size = v_uint32()


class _unnamed_7903(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileName = v_ptr32()
        self.FileInformationClass = v_uint32()
        self.FileIndex = v_uint32()


class WHEA_ERROR_PACKET_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PreviousError = v_uint32()


class ALPC_PROCESS_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = EX_PUSH_LOCK()
        self.ViewListHead = LIST_ENTRY()
        self.PagedPoolQuotaCache = v_uint32()


class OBJECT_HANDLE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleAttributes = v_uint32()
        self.GrantedAccess = v_uint32()


class HEAP_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = _unnamed_8613()


class KTIMER_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = v_uint32()
        self.Entry = LIST_ENTRY()
        self._pad0010 = v_bytes(size=4)
        self.Time = ULARGE_INTEGER()


class PS_CLIENT_SECURITY_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ImpersonationData = v_uint32()


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


class OWNER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwnerThread = v_uint32()
        self.IoPriorityBoosted = v_uint32()


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
        self.DependentList = LIST_ENTRY()
        self.ProviderList = LIST_ENTRY()


class HEAP_LOCAL_SEGMENT_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Hint = v_ptr32()
        self.ActiveSubsegment = v_ptr32()
        self.CachedItems = vstruct.VArray([ v_ptr32() for i in range(16) ])
        self.SListHeader = SLIST_HEADER()
        self.Counters = HEAP_BUCKET_COUNTERS()
        self.LocalData = v_ptr32()
        self.LastOpSequence = v_uint32()
        self.BucketIndex = v_uint16()
        self.LastUsed = v_uint16()
        self._pad0068 = v_bytes(size=4)


class HANDLE_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Object = v_ptr32()
        self.GrantedAccess = v_uint32()


class HEAP_COUNTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TotalMemoryReserved = v_uint32()
        self.TotalMemoryCommitted = v_uint32()
        self.TotalMemoryLargeUCR = v_uint32()
        self.TotalSizeInVirtualBlocks = v_uint32()
        self.TotalSegments = v_uint32()
        self.TotalUCRs = v_uint32()
        self.CommittOps = v_uint32()
        self.DeCommitOps = v_uint32()
        self.LockAcquires = v_uint32()
        self.LockCollisions = v_uint32()
        self.CommitRate = v_uint32()
        self.DecommittRate = v_uint32()
        self.CommitFailures = v_uint32()
        self.InBlockCommitFailures = v_uint32()
        self.CompactHeapCalls = v_uint32()
        self.CompactedUCRs = v_uint32()
        self.AllocAndFreeOps = v_uint32()
        self.InBlockDeccommits = v_uint32()
        self.InBlockDeccomitSize = v_uint32()
        self.HighWatermarkSize = v_uint32()
        self.LastPolledSize = v_uint32()


class MAILSLOT_CREATE_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MailslotQuota = v_uint32()
        self.MaximumMessageSize = v_uint32()
        self.ReadTimeout = LARGE_INTEGER()
        self.TimeoutSpecified = v_uint8()
        self._pad0018 = v_bytes(size=7)


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


class PPM_IDLE_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DomainMembers = KAFFINITY_EX()
        self.IdleCheck = v_ptr32()
        self.IdleHandler = v_ptr32()
        self.Context = v_ptr32()
        self.Latency = v_uint32()
        self.Power = v_uint32()
        self.TimeCheck = v_uint32()
        self.StateFlags = v_uint32()
        self.PromotePercent = v_uint8()
        self.DemotePercent = v_uint8()
        self.PromotePercentBase = v_uint8()
        self.DemotePercentBase = v_uint8()
        self.StateType = v_uint8()
        self._pad0030 = v_bytes(size=3)


class _unnamed_9730(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length40 = v_uint32()


class _unnamed_9733(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length48 = v_uint32()


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
        self.Privileges = _unnamed_7641()
        self.AuditPrivileges = v_uint8()
        self._pad0064 = v_bytes(size=3)
        self.ObjectName = UNICODE_STRING()
        self.ObjectTypeName = UNICODE_STRING()


class _unnamed_9736(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length64 = v_uint32()


class TP_CALLBACK_INSTANCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class PROC_IDLE_ACCOUNTING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StateCount = v_uint32()
        self.TotalTransitions = v_uint32()
        self.ResetCount = v_uint32()
        self._pad0010 = v_bytes(size=4)
        self.StartTime = v_uint64()
        self.BucketLimits = vstruct.VArray([ v_uint64() for i in range(16) ])
        self.State = vstruct.VArray([ PROC_IDLE_STATE_ACCOUNTING() for i in range(1) ])


class GDI_TEB_BATCH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.HDC = v_uint32()
        self.Buffer = vstruct.VArray([ v_uint32() for i in range(310) ])


class THREAD_PERFORMANCE_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.ProcessorNumber = PROCESSOR_NUMBER()
        self.ContextSwitches = v_uint32()
        self.HwCountersCount = v_uint32()
        self.UpdateCount = v_uint64()
        self.WaitReasonBitMap = v_uint64()
        self.HardwareCounters = v_uint64()
        self.CycleTime = COUNTER_READING()
        self.HwCounters = vstruct.VArray([ COUNTER_READING() for i in range(16) ])


class PAGEFAULT_HISTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class ECP_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class _unnamed_7641(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InitialPrivilegeSet = INITIAL_PRIVILEGE_SET()


class SECTION_OBJECT_POINTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSectionObject = v_ptr32()
        self.SharedCacheMap = v_ptr32()
        self.ImageSectionObject = v_ptr32()


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


class KTRAP_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DbgEbp = v_uint32()
        self.DbgEip = v_uint32()
        self.DbgArgMark = v_uint32()
        self.DbgArgPointer = v_uint32()
        self.TempSegCs = v_uint16()
        self.Logging = v_uint8()
        self.Reserved = v_uint8()
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


class MCI_ADDR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Address = v_uint32()
        self.Reserved = v_uint32()


class IO_TIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.TimerFlag = v_uint16()
        self.TimerList = LIST_ENTRY()
        self.TimerRoutine = v_ptr32()
        self.Context = v_ptr32()
        self.DeviceObject = v_ptr32()


class WHEA_REVISION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinorRevision = v_uint8()
        self.MajorRevision = v_uint8()


class _unnamed_10248(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumChannel = v_uint32()
        self.MaximumChannel = v_uint32()


class _unnamed_10241(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumVector = v_uint32()
        self.MaximumVector = v_uint32()
        self.AffinityPolicy = v_uint16()
        self.Group = v_uint16()
        self.PriorityPolicy = v_uint32()
        self.TargetedProcessors = v_uint32()


class TP_CLEANUP_GROUP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class PROC_IDLE_SNAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Time = v_uint64()
        self.Idle = v_uint64()


class _unnamed_7705(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MasterIrp = v_ptr32()


class SECURITY_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint8()
        self.Sbz1 = v_uint8()
        self.Control = v_uint16()
        self.Owner = v_ptr32()
        self.Group = v_ptr32()
        self.Sacl = v_ptr32()
        self.Dacl = v_ptr32()


class _unnamed_7708(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AsynchronousParameters = _unnamed_7723()


class OBJECT_TYPE_INITIALIZER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.ObjectTypeFlags = v_uint8()
        self._pad0004 = v_bytes(size=1)
        self.ObjectTypeCode = v_uint32()
        self.InvalidAttributes = v_uint32()
        self.GenericMapping = GENERIC_MAPPING()
        self.ValidAccessMask = v_uint32()
        self.RetainAccess = v_uint32()
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


class TP_DIRECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Callback = v_ptr32()
        self.NumaNode = v_uint32()
        self.IdealProcessor = v_uint8()
        self._pad000c = v_bytes(size=3)


class XSTATE_SAVE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Reserved1 = v_uint64()
        self.Reserved2 = v_uint32()
        self.Prev = v_ptr32()
        self.Reserved3 = v_ptr32()
        self.Thread = v_ptr32()
        self.Reserved4 = v_ptr32()
        self.Level = v_uint8()
        self._pad0020 = v_bytes(size=3)


class HEAP_ENTRY_EXTRA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatorBackTraceIndex = v_uint16()
        self.TagIndex = v_uint16()
        self.Settable = v_uint32()


class HEAP_PSEUDO_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()


class PAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = FAST_MUTEX()
        self._pad00c0 = v_bytes(size=32)


class LARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class NPAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = v_uint32()
        self._pad00c0 = v_bytes(size=60)


class _unnamed_5688(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_7823(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


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


class PP_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.P = v_ptr32()
        self.L = v_ptr32()


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
        self.AltArchitecturePad = vstruct.VArray([ v_uint32() for i in range(1) ])
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
        self.TscQpcData = v_uint8()
        self.TscQpcPad = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.SharedDataFlags = v_uint32()
        self.DataFlagsPad = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.TestRetInstruction = v_uint64()
        self.SystemCall = v_uint32()
        self.SystemCallReturn = v_uint32()
        self.SystemCallPad = vstruct.VArray([ v_uint64() for i in range(3) ])
        self.TickCount = KSYSTEM_TIME()
        self.TickCountPad = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.Cookie = v_uint32()
        self.CookiePad = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.ConsoleSessionForegroundProcessId = v_uint64()
        self.Wow64SharedInformation = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.UserModeGlobalLogger = vstruct.VArray([ v_uint16() for i in range(16) ])
        self.ImageFileExecutionOptions = v_uint32()
        self.LangGenerationCount = v_uint32()
        self.Reserved5 = v_uint64()
        self.InterruptTimeBias = v_uint64()
        self.TscQpcBias = v_uint64()
        self.ActiveProcessorCount = v_uint32()
        self.ActiveGroupCount = v_uint16()
        self.Reserved4 = v_uint16()
        self.AitSamplingValue = v_uint32()
        self.AppCompatFlag = v_uint32()
        self.SystemDllNativeRelocation = v_uint64()
        self.SystemDllWowRelocation = v_uint32()
        self.XStatePad = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.XState = XSTATE_CONFIGURATION()


class SYSTEM_POWER_STATE_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Reserved1 = v_uint32()


class FS_FILTER_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AcquireForModifiedPageWriter = _unnamed_9787()
        self._pad0014 = v_bytes(size=12)


class HEAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = HEAP_ENTRY()
        self.SegmentSignature = v_uint32()
        self.SegmentFlags = v_uint32()
        self.SegmentListEntry = LIST_ENTRY()
        self.Heap = v_ptr32()
        self.BaseAddress = v_ptr32()
        self.NumberOfPages = v_uint32()
        self.FirstEntry = v_ptr32()
        self.LastValidEntry = v_ptr32()
        self.NumberOfUnCommittedPages = v_uint32()
        self.NumberOfUnCommittedRanges = v_uint32()
        self.SegmentAllocatorBackTraceIndex = v_uint16()
        self.Reserved = v_uint16()
        self.UCRSegmentList = LIST_ENTRY()
        self.Flags = v_uint32()
        self.ForceFlags = v_uint32()
        self.CompatibilityFlags = v_uint32()
        self.EncodeFlagMask = v_uint32()
        self.Encoding = HEAP_ENTRY()
        self.PointerKey = v_uint32()
        self.Interceptor = v_uint32()
        self.VirtualMemoryThreshold = v_uint32()
        self.Signature = v_uint32()
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
        self.UCRList = LIST_ENTRY()
        self.AlignRound = v_uint32()
        self.AlignMask = v_uint32()
        self.VirtualAllocdBlocks = LIST_ENTRY()
        self.SegmentList = LIST_ENTRY()
        self.AllocatorBackTraceIndex = v_uint16()
        self._pad00b4 = v_bytes(size=2)
        self.NonDedicatedListLength = v_uint32()
        self.BlocksIndex = v_ptr32()
        self.UCRIndex = v_ptr32()
        self.PseudoTagEntries = v_ptr32()
        self.FreeLists = LIST_ENTRY()
        self.LockVariable = v_ptr32()
        self.CommitRoutine = v_ptr32()
        self.FrontEndHeap = v_ptr32()
        self.FrontHeapLockCount = v_uint16()
        self.FrontEndHeapType = v_uint8()
        self._pad00dc = v_bytes(size=1)
        self.Counters = HEAP_COUNTERS()
        self.TuningParameters = HEAP_TUNING_PARAMETERS()


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


class EPROCESS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pcb = KPROCESS()
        self.ProcessLock = EX_PUSH_LOCK()
        self._pad00a0 = v_bytes(size=4)
        self.CreateTime = LARGE_INTEGER()
        self.ExitTime = LARGE_INTEGER()
        self.RundownProtect = EX_RUNDOWN_REF()
        self.UniqueProcessId = v_ptr32()
        self.ActiveProcessLinks = LIST_ENTRY()
        self.ProcessQuotaUsage = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.ProcessQuotaPeak = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.CommitCharge = v_uint32()
        self.QuotaBlock = v_ptr32()
        self.CpuQuotaBlock = v_ptr32()
        self.PeakVirtualSize = v_uint32()
        self.VirtualSize = v_uint32()
        self.SessionProcessLinks = LIST_ENTRY()
        self.DebugPort = v_ptr32()
        self.ExceptionPortData = v_ptr32()
        self.ObjectTable = v_ptr32()
        self.Token = EX_FAST_REF()
        self.WorkingSetPage = v_uint32()
        self.AddressCreationLock = EX_PUSH_LOCK()
        self.RotateInProgress = v_ptr32()
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
        self.Cookie = v_uint32()
        self.Spare8 = v_uint32()
        self.WorkingSetWatch = v_ptr32()
        self.Win32WindowStation = v_ptr32()
        self.InheritedFromUniqueProcessId = v_ptr32()
        self.LdtInformation = v_ptr32()
        self.VdmObjects = v_ptr32()
        self.ConsoleHostProcess = v_uint32()
        self.DeviceMap = v_ptr32()
        self.EtwDataSource = v_ptr32()
        self.FreeTebHint = v_ptr32()
        self._pad0160 = v_bytes(size=4)
        self.PageDirectoryPte = HARDWARE_PTE_X86()
        self._pad0168 = v_bytes(size=4)
        self.Session = v_ptr32()
        self.ImageFileName = vstruct.VArray([ v_uint8() for i in range(15) ])
        self.PriorityClass = v_uint8()
        self.JobLinks = LIST_ENTRY()
        self.LockedPagesList = v_ptr32()
        self.ThreadListHead = LIST_ENTRY()
        self.SecurityPort = v_ptr32()
        self.PaeTop = v_ptr32()
        self.ActiveThreads = v_uint32()
        self.ImagePathHash = v_uint32()
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
        self.HighestUserAddress = v_ptr32()
        self.ModifiedPageCount = v_uint32()
        self.Flags2 = v_uint32()
        self.Flags = v_uint32()
        self.ExitStatus = v_uint32()
        self.VadRoot = MM_AVL_TABLE()
        self.AlpcContext = ALPC_PROCESS_CONTEXT()
        self.TimerResolutionLink = LIST_ENTRY()
        self.RequestedTimerResolution = v_uint32()
        self.ActiveThreadsHighWatermark = v_uint32()
        self.SmallestTimerResolution = v_uint32()
        self.TimerResolutionStackRecord = v_ptr32()


class TP_TASK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Callbacks = v_ptr32()
        self.NumaNode = v_uint32()
        self.IdealProcessor = v_uint8()
        self._pad000c = v_bytes(size=3)
        self.PostGuard = TP_NBQ_GUARD()
        self.NBQNode = v_ptr32()


class TEB_ACTIVE_FRAME_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.FrameName = v_ptr32()


class KTIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.DueTime = ULARGE_INTEGER()
        self.TimerListEntry = LIST_ENTRY()
        self.Dpc = v_ptr32()
        self.Period = v_uint32()


class _unnamed_7955(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.IoControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


class _unnamed_7950(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_ptr32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Flags = v_uint16()
        self.u = _unnamed_9480()


class _unnamed_8913(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FilePointerIndex = v_uint32()


class OBJECT_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.RootDirectory = v_ptr32()
        self.ObjectName = v_ptr32()
        self.Attributes = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.SecurityQualityOfService = v_ptr32()


class _unnamed_8084(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IdType = v_uint32()


class CM_FULL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.PartialResourceList = CM_PARTIAL_RESOURCE_LIST()


class KTIMER_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TimerExpiry = vstruct.VArray([ v_ptr32() for i in range(16) ])
        self.TimerEntries = vstruct.VArray([ KTIMER_TABLE_ENTRY() for i in range(256) ])


class _unnamed_8089(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceTextType = v_uint32()
        self.LocaleId = v_uint32()


class _unnamed_8162(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()


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


class RTL_DYNAMIC_HASH_TABLE_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ChainHead = v_ptr32()
        self.PrevLinkage = v_ptr32()
        self.Signature = v_uint32()


class MMWSL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class PROC_IDLE_STATE_ACCOUNTING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TotalTime = v_uint64()
        self.IdleTransitions = v_uint32()
        self.FailedTransitions = v_uint32()
        self.InvalidBucketIndex = v_uint32()
        self._pad0018 = v_bytes(size=4)
        self.MinTime = v_uint64()
        self.MaxTime = v_uint64()
        self.IdleTimeBuckets = vstruct.VArray([ PROC_IDLE_STATE_BUCKET() for i in range(16) ])


class _unnamed_9708(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Group = v_uint16()
        self.MessageCount = v_uint16()
        self.Vector = v_uint32()
        self.Affinity = v_uint32()


class _unnamed_9067(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint8()
        self.Flags1 = v_uint8()
        self.Flags2 = v_uint8()
        self.BaseHi = v_uint8()


class _unnamed_9700(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length = v_uint32()


class _unnamed_9703(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint16()
        self.Group = v_uint16()
        self.Vector = v_uint32()
        self.Affinity = v_uint32()


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


class RTL_CRITICAL_SECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DebugInfo = v_ptr32()
        self.LockCount = v_uint32()
        self.RecursionCount = v_uint32()
        self.OwningThread = v_ptr32()
        self.LockSemaphore = v_ptr32()
        self.SpinCount = v_uint32()


class KSYSTEM_TIME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.High1Time = v_uint32()
        self.High2Time = v_uint32()


class PROC_IDLE_STATE_BUCKET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TotalTime = v_uint64()
        self.MinTime = v_uint64()
        self.MaxTime = v_uint64()
        self.Count = v_uint32()
        self._pad0020 = v_bytes(size=4)


class RTL_STD_LIST_HEAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Lock = RTL_STACK_DATABASE_LOCK()


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


class _unnamed_7745(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Create = _unnamed_7807()


class LUID_AND_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Luid = LUID()
        self.Attributes = v_uint32()


class _unnamed_8011(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_ptr32()
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Interface = v_ptr32()
        self.InterfaceSpecificData = v_ptr32()


class HEAP_BUCKET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BlockUnits = v_uint16()
        self.SizeIndex = v_uint8()
        self.UseAffinity = v_uint8()


class _unnamed_9789(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SyncType = v_uint32()
        self.PageProtection = v_uint32()


class KTHREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.CycleTime = v_uint64()
        self.HighCycleTime = v_uint32()
        self._pad0020 = v_bytes(size=4)
        self.QuantumTarget = v_uint64()
        self.InitialStack = v_ptr32()
        self.StackLimit = v_ptr32()
        self.KernelStack = v_ptr32()
        self.ThreadLock = v_uint32()
        self.WaitRegister = KWAIT_STATUS_REGISTER()
        self.Running = v_uint8()
        self.Alerted = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.KernelStackResident = v_uint32()
        self.ApcState = KAPC_STATE()
        self.NextProcessor = v_uint32()
        self.DeferredProcessor = v_uint32()
        self.ApcQueueLock = v_uint32()
        self.ContextSwitches = v_uint32()
        self.State = v_uint8()
        self.NpxState = v_uint8()
        self.WaitIrql = v_uint8()
        self.WaitMode = v_uint8()
        self.WaitStatus = v_uint32()
        self.WaitBlockList = v_ptr32()
        self.WaitListEntry = LIST_ENTRY()
        self.Queue = v_ptr32()
        self.WaitTime = v_uint32()
        self.KernelApcDisable = v_uint16()
        self.SpecialApcDisable = v_uint16()
        self.Teb = v_ptr32()
        self._pad0090 = v_bytes(size=4)
        self.Timer = KTIMER()
        self.AutoAlignment = v_uint32()
        self.ServiceTable = v_ptr32()
        self.WaitBlock = vstruct.VArray([ KWAIT_BLOCK() for i in range(4) ])
        self.QueueListEntry = LIST_ENTRY()
        self.TrapFrame = v_ptr32()
        self.FirstArgument = v_ptr32()
        self.CallbackStack = v_ptr32()
        self.ApcStateIndex = v_uint8()
        self.BasePriority = v_uint8()
        self.PriorityDecrement = v_uint8()
        self.Preempted = v_uint8()
        self.AdjustReason = v_uint8()
        self.AdjustIncrement = v_uint8()
        self.PreviousMode = v_uint8()
        self.Saturation = v_uint8()
        self.SystemCallNumber = v_uint32()
        self.FreezeCount = v_uint32()
        self.UserAffinity = GROUP_AFFINITY()
        self.Process = v_ptr32()
        self.Affinity = GROUP_AFFINITY()
        self.IdealProcessor = v_uint32()
        self.UserIdealProcessor = v_uint32()
        self.ApcStatePointer = vstruct.VArray([ v_ptr32() for i in range(2) ])
        self.SavedApcState = KAPC_STATE()
        self.SuspendCount = v_uint8()
        self.Spare1 = v_uint8()
        self.OtherPlatformFill = v_uint8()
        self._pad018c = v_bytes(size=1)
        self.Win32Thread = v_ptr32()
        self.StackBase = v_ptr32()
        self.SuspendApc = KAPC()
        self.UserTime = v_uint32()
        self.SuspendSemaphore = KSEMAPHORE()
        self.SListFaultCount = v_uint32()
        self.ThreadListEntry = LIST_ENTRY()
        self.MutantListHead = LIST_ENTRY()
        self.SListFaultAddress = v_ptr32()
        self.ThreadCounters = v_ptr32()
        self.XStateSave = v_ptr32()
        self._pad0200 = v_bytes(size=4)


class _unnamed_8613(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CriticalSection = RTL_CRITICAL_SECTION()


class _unnamed_10231(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Alignment = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


class _unnamed_10260(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length40 = v_uint32()
        self.Alignment40 = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


class PROC_HISTORY_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Utility = v_uint16()
        self.Frequency = v_uint8()
        self.Reserved = v_uint8()


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


class _unnamed_9012(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BankNumber = v_uint8()
        self.Reserved2 = vstruct.VArray([ v_uint8() for i in range(7) ])
        self.Status = MCI_STATS()
        self.Address = MCI_ADDR()
        self.Misc = v_uint64()


class MCI_STATS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MciStats = _unnamed_9007()


class _unnamed_9019(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Address = v_uint64()
        self.Type = v_uint64()


class _unnamed_9790(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NotificationType = v_uint32()
        self.SafeToRecurse = v_uint8()
        self._pad0008 = v_bytes(size=3)


class _unnamed_9791(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()
        self.Argument5 = v_ptr32()


class PROC_PERF_LOAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BusyPercentage = v_uint8()
        self.FrequencyPercentage = v_uint8()


class AUX_ACCESS_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PrivilegesUsed = v_ptr32()
        self.GenericMapping = GENERIC_MAPPING()
        self.AccessesToAudit = v_uint32()
        self.MaximumAuditMask = v_uint32()
        self.TransactionId = GUID()
        self.NewSecurityDescriptor = v_ptr32()
        self.ExistingSecurityDescriptor = v_ptr32()
        self.ParentSecurityDescriptor = v_ptr32()
        self.DeRefSecurityDescriptor = v_ptr32()
        self.SDLock = v_ptr32()
        self.AccessReasons = ACCESS_REASONS()


class _unnamed_9496(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Balance = v_uint32()


class HEAP_LOCAL_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeletedSubSegments = SLIST_HEADER()
        self.CrtZone = v_ptr32()
        self.LowFragHeap = v_ptr32()
        self.Sequence = v_uint32()
        self._pad0018 = v_bytes(size=4)
        self.SegmentInfo = vstruct.VArray([ HEAP_LOCAL_SEGMENT_INFO() for i in range(128) ])


class _unnamed_5701(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


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


class PF_KERNEL_GLOBALS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AccessBufferAgeThreshold = v_uint64()
        self.AccessBufferRef = EX_RUNDOWN_REF()
        self.AccessBufferExistsEvent = KEVENT()
        self.AccessBufferMax = v_uint32()
        self.AccessBufferList = SLIST_HEADER()
        self.StreamSequenceNumber = v_uint32()
        self.Flags = v_uint32()
        self.ScenarioPrefetchCount = v_uint32()
        self._pad0040 = v_bytes(size=12)


class _unnamed_7912(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()


class _unnamed_7915(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()
        self.FileObject = v_ptr32()
        self.ReplaceIfExists = v_uint8()
        self.AdvanceOnly = v_uint8()
        self._pad0010 = v_bytes(size=2)


class EVENT_DATA_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Ptr = v_uint64()
        self.Size = v_uint32()
        self.Reserved = v_uint32()


class KDEVICE_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceListHead = LIST_ENTRY()
        self.Lock = v_uint32()
        self.Busy = v_uint8()
        self._pad0014 = v_bytes(size=3)


class IO_DRIVER_CREATE_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self._pad0004 = v_bytes(size=2)
        self.ExtraCreateParameter = v_ptr32()
        self.DeviceObjectHint = v_ptr32()
        self.TxnParameters = v_ptr32()


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
        self.MinimumWorkingSetSize = v_uint32()
        self.MaximumWorkingSetSize = v_uint32()
        self.LimitFlags = v_uint32()
        self.ActiveProcessLimit = v_uint32()
        self.Affinity = KAFFINITY_EX()
        self.PriorityClass = v_uint8()
        self._pad00b8 = v_bytes(size=3)
        self.AccessState = v_ptr32()
        self.UIRestrictionsClass = v_uint32()
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
        self.ProcessMemoryLimit = v_uint32()
        self.JobMemoryLimit = v_uint32()
        self.PeakProcessMemoryUsed = v_uint32()
        self.PeakJobMemoryUsed = v_uint32()
        self.CurrentJobMemoryUsed = v_uint64()
        self.MemoryLimitsLock = EX_PUSH_LOCK()
        self.JobSetLinks = LIST_ENTRY()
        self.MemberLevel = v_uint32()
        self.JobFlags = v_uint32()
        self._pad0138 = v_bytes(size=4)


class HANDLE_TRACE_DEBUG_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.RefCount = v_uint32()
        self.TableSize = v_uint32()
        self.BitMaskFlags = v_uint32()
        self.CloseCompactionLock = FAST_MUTEX()
        self.CurrentStackIndex = v_uint32()
        self.TraceDb = vstruct.VArray([ HANDLE_TRACE_DB_ENTRY() for i in range(1) ])


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


class RTL_STACK_DATABASE_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = RTL_SRWLOCK()


class SID_IDENTIFIER_AUTHORITY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Value = vstruct.VArray([ v_uint8() for i in range(6) ])


class XSTATE_FEATURE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.Size = v_uint32()


class WHEA_TIMESTAMP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Seconds = v_uint64()


class ACTIVATION_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class RTL_CRITICAL_SECTION_DEBUG(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.CreatorBackTraceIndex = v_uint16()
        self.CriticalSection = v_ptr32()
        self.ProcessLocksList = LIST_ENTRY()
        self.EntryCount = v_uint32()
        self.ContentionCount = v_uint32()
        self.Flags = v_uint32()
        self.CreatorBackTraceIndexHigh = v_uint16()
        self.SpareUSHORT = v_uint16()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.TimerControlFlags = v_uint8()
        self.ThreadControlFlags = v_uint8()
        self.TimerMiscFlags = v_uint8()
        self.SignalState = v_uint32()
        self.WaitListHead = LIST_ENTRY()


class _unnamed_8053(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Capabilities = v_ptr32()


class PROCESSOR_POWER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IdleStates = v_ptr32()
        self._pad0008 = v_bytes(size=4)
        self.IdleTimeLast = v_uint64()
        self.IdleTimeTotal = v_uint64()
        self.IdleTimeEntry = v_uint64()
        self.IdleAccounting = v_ptr32()
        self.Hypervisor = v_uint32()
        self.PerfHistoryTotal = v_uint32()
        self.ThermalConstraint = v_uint8()
        self.PerfHistoryCount = v_uint8()
        self.PerfHistorySlot = v_uint8()
        self.Reserved = v_uint8()
        self.LastSysTime = v_uint32()
        self.WmiDispatchPtr = v_uint32()
        self.WmiInterfaceEnabled = v_uint32()
        self._pad0040 = v_bytes(size=4)
        self.FFHThrottleStateInfo = PPM_FFH_THROTTLE_STATE_INFO()
        self.PerfActionDpc = KDPC()
        self.PerfActionMask = v_uint32()
        self._pad0088 = v_bytes(size=4)
        self.IdleCheck = PROC_IDLE_SNAP()
        self.PerfCheck = PROC_IDLE_SNAP()
        self.Domain = v_ptr32()
        self.PerfConstraint = v_ptr32()
        self.Load = v_ptr32()
        self.PerfHistory = v_ptr32()
        self.Utility = v_uint32()
        self.OverUtilizedHistory = v_uint32()
        self.AffinityCount = v_uint32()
        self.AffinityHistory = v_uint32()


class POWER_SEQUENCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SequenceD1 = v_uint32()
        self.SequenceD2 = v_uint32()
        self.SequenceD3 = v_uint32()


class _unnamed_8115(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerSequence = v_ptr32()


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


class JOB_ACCESS_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


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


class _unnamed_10270(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length64 = v_uint32()
        self.Alignment64 = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


class WHEA_ERROR_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = WHEA_ERROR_RECORD_HEADER()
        self.SectionDescriptor = vstruct.VArray([ WHEA_ERROR_RECORD_SECTION_DESCRIPTOR() for i in range(1) ])


class PS_PER_CPU_QUOTA_CACHE_AWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SortedListEntry = LIST_ENTRY()
        self.IdleOnlyListHead = LIST_ENTRY()
        self.CycleBaseAllowance = v_uint64()
        self.CyclesRemaining = v_uint64()
        self.CurrentGeneration = v_uint32()
        self._pad0040 = v_bytes(size=28)


class PROC_PERF_CONSTRAINT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Prcb = v_ptr32()
        self.PerfContext = v_uint32()
        self.PercentageCap = v_uint32()
        self.ThermalCap = v_uint32()
        self.TargetFrequency = v_uint32()
        self.AcumulatedFullFrequency = v_uint32()
        self.AcumulatedZeroFrequency = v_uint32()
        self.FrequencyHistoryTotal = v_uint32()
        self.AverageFrequency = v_uint32()


class LUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_7711(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Overlay = _unnamed_7784()
        self._pad0030 = v_bytes(size=8)


class CLIENT_ID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UniqueProcess = v_ptr32()
        self.UniqueThread = v_ptr32()


class RTL_STACK_TRACE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashChain = RTL_STD_LIST_ENTRY()
        self.TraceCount = v_uint16()
        self.IndexHigh = v_uint16()
        self.Index = v_uint16()
        self.Depth = v_uint16()
        self.BackTrace = vstruct.VArray([ v_ptr32() for i in range(32) ])


class OBJECT_DUMP_CONTROL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Stream = v_ptr32()
        self.Detail = v_uint32()


class HANDLE_TRACE_DB_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientId = CLIENT_ID()
        self.Handle = v_ptr32()
        self.Type = v_uint32()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(16) ])


class GENERAL_LOOKASIDE_POOL(vstruct.VStruct):
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
        self.AllocateEx = v_ptr32()
        self.FreeEx = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.LastTotalAllocates = v_uint32()
        self.LastAllocateMisses = v_uint32()
        self.Future = vstruct.VArray([ v_uint32() for i in range(2) ])


class HARDWARE_PTE_X86(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class RTL_SRWLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class HEAP_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()
        self.TagIndex = v_uint16()
        self.CreatorBackTraceIndex = v_uint16()
        self.TagName = vstruct.VArray([ v_uint16() for i in range(24) ])


class STRING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.MaximumLength = v_uint16()
        self.Buffer = v_ptr32()


class TP_POOL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class LIST_ENTRY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()
        self.Blink = v_uint32()


class SINGLE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()


class PPM_FFH_THROTTLE_STATE_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EnableLogging = v_uint8()
        self._pad0004 = v_bytes(size=3)
        self.MismatchCount = v_uint32()
        self.Initialized = v_uint8()
        self._pad0010 = v_bytes(size=7)
        self.LastValue = v_uint64()
        self.LastLogTickCount = LARGE_INTEGER()


class KDEVICE_QUEUE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceListEntry = LIST_ENTRY()
        self.SortKey = v_uint32()
        self.Inserted = v_uint8()
        self._pad0010 = v_bytes(size=3)


class CACHED_KSTACK_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SListHead = SLIST_HEADER()
        self.MinimumFree = v_uint32()
        self.Misses = v_uint32()
        self.MissesLast = v_uint32()
        self.Pad0 = v_uint32()


class HEAP_FAILURE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint32()
        self.StructureSize = v_uint32()
        self.FailureType = v_uint32()
        self.HeapAddress = v_ptr32()
        self.Address = v_ptr32()
        self.Param1 = v_ptr32()
        self.Param2 = v_ptr32()
        self.Param3 = v_ptr32()
        self.PreviousBlock = v_ptr32()
        self.NextBlock = v_ptr32()
        self.ExpectedEncodedEntry = HEAP_ENTRY()
        self.ExpectedDecodedEntry = HEAP_ENTRY()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(32) ])


class EX_FAST_REF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Object = v_ptr32()


class INTERLOCK_SEQ(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Depth = v_uint16()
        self.FreeEntryOffset = v_uint16()
        self.Sequence = v_uint32()


class KSPIN_LOCK_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Lock = v_ptr32()


class RTL_ACTIVATION_CONTEXT_STACK_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Previous = v_ptr32()
        self.ActivationContext = v_ptr32()
        self.Flags = v_uint32()


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


class MM_DRIVER_VERIFIER_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint32()
        self.RaiseIrqls = v_uint32()
        self.AcquireSpinLocks = v_uint32()
        self.SynchronizeExecutions = v_uint32()
        self.AllocationsAttempted = v_uint32()
        self.AllocationsSucceeded = v_uint32()
        self.AllocationsSucceededSpecialPool = v_uint32()
        self.AllocationsWithNoTag = v_uint32()
        self.TrimRequests = v_uint32()
        self.Trims = v_uint32()
        self.AllocationsFailed = v_uint32()
        self.AllocationsFailedDeliberately = v_uint32()
        self.Loads = v_uint32()
        self.Unloads = v_uint32()
        self.UnTrackedPool = v_uint32()
        self.UserTrims = v_uint32()
        self.CurrentPagedPoolAllocations = v_uint32()
        self.CurrentNonPagedPoolAllocations = v_uint32()
        self.PeakPagedPoolAllocations = v_uint32()
        self.PeakNonPagedPoolAllocations = v_uint32()
        self.PagedBytes = v_uint32()
        self.NonPagedBytes = v_uint32()
        self.PeakPagedBytes = v_uint32()
        self.PeakNonPagedBytes = v_uint32()
        self.BurstAllocationsFailedDeliberately = v_uint32()
        self.SessionTrims = v_uint32()
        self.OptionChanges = v_uint32()
        self.VerifyMode = v_uint32()
        self.PreviousBucketName = UNICODE_STRING()
        self.ActivityCounter = v_uint32()
        self.PreviousActivityCounter = v_uint32()
        self.WorkerTrimRequests = v_uint32()


class IO_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Option = v_uint8()
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Spare1 = v_uint8()
        self.Flags = v_uint16()
        self.Spare2 = v_uint16()
        self.u = _unnamed_9655()


class EX_PUSH_LOCK_CACHE_AWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locks = vstruct.VArray([ v_ptr32() for i in range(32) ])


class _unnamed_7963(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.SecurityDescriptor = v_ptr32()


class _unnamed_7960(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.Length = v_uint32()


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
        self.KeyedWaitSemaphore = KSEMAPHORE()
        self.ClientSecurity = PS_CLIENT_SECURITY_CONTEXT()
        self.IrpList = LIST_ENTRY()
        self.TopLevelIrp = v_uint32()
        self.DeviceToVerify = v_ptr32()
        self.CpuQuotaApc = v_ptr32()
        self.Win32StartAddress = v_ptr32()
        self.LegacyPowerObject = v_ptr32()
        self.ThreadListEntry = LIST_ENTRY()
        self.RundownProtect = EX_RUNDOWN_REF()
        self.ThreadLock = EX_PUSH_LOCK()
        self.ReadClusterSize = v_uint32()
        self.MmLockOrdering = v_uint32()
        self.CrossThreadFlags = v_uint32()
        self.SameThreadPassiveFlags = v_uint32()
        self.SameThreadApcFlags = v_uint32()
        self.CacheManagerActive = v_uint8()
        self.DisablePageFaultClustering = v_uint8()
        self.ActiveFaultCount = v_uint8()
        self.LockOrderState = v_uint8()
        self.AlpcMessageId = v_uint32()
        self.AlpcMessage = v_ptr32()
        self.AlpcWaitListEntry = LIST_ENTRY()
        self.CacheManagerCount = v_uint32()
        self.IoBoostCount = v_uint32()
        self.IrpListLock = v_uint32()
        self.ReservedForSynchTracking = v_ptr32()
        self.CmCallbackListHead = SINGLE_LIST_ENTRY()
        self._pad02b8 = v_bytes(size=4)


class ASSEMBLY_STORAGE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class FAST_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Event = KEVENT()
        self.OldIrql = v_uint32()


class WHEA_ERROR_RECORD_HEADER_VALIDBITS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PlatformId = v_uint32()


class _unnamed_8157(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ProviderId = v_uint32()
        self.DataPath = v_ptr32()
        self.BufferSize = v_uint32()
        self.Buffer = v_ptr32()


class _unnamed_8153(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatedResources = v_ptr32()
        self.AllocatedResourcesTranslated = v_ptr32()


class IO_SECURITY_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityQos = v_ptr32()
        self.AccessState = v_ptr32()
        self.DesiredAccess = v_uint32()
        self.FullCreateOptions = v_uint32()


class TERMINATION_PORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Port = v_ptr32()


class _unnamed_9303(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AsULONG = v_uint32()


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


class WHEA_ERROR_RECORD_HEADER_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Recovered = v_uint32()


class XSTATE_CONFIGURATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EnabledFeatures = v_uint64()
        self.Size = v_uint32()
        self.OptimizedSave = v_uint32()
        self.Features = vstruct.VArray([ XSTATE_FEATURE() for i in range(64) ])


class _unnamed_9713(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Raw = _unnamed_9708()


class _unnamed_9716(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Channel = v_uint32()
        self.Port = v_uint32()
        self.Reserved1 = v_uint32()


class KWAIT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WaitListEntry = LIST_ENTRY()
        self.Thread = v_ptr32()
        self.Object = v_ptr32()
        self.NextWaitBlock = v_ptr32()
        self.WaitKey = v_uint16()
        self.WaitType = v_uint8()
        self.BlockState = v_uint8()


class _unnamed_9655(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Port = _unnamed_10231()


class ACTIVATION_CONTEXT_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


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


class DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pad = v_uint16()
        self.Limit = v_uint16()
        self.Base = v_uint32()


class HEAP_USERDATA_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SFreeListEntry = SINGLE_LIST_ENTRY()
        self.Reserved = v_ptr32()
        self.SizeIndex = v_uint32()
        self.Signature = v_uint32()


class RTL_DRIVE_LETTER_CURDIR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Length = v_uint16()
        self.TimeStamp = v_uint32()
        self.DosPath = STRING()


class CACHE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint8()
        self.Associativity = v_uint8()
        self.LineSize = v_uint16()
        self.Size = v_uint32()
        self.Type = v_uint32()


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
        self.AllocateEx = v_ptr32()
        self.FreeEx = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.LastTotalAllocates = v_uint32()
        self.LastAllocateMisses = v_uint32()
        self.Future = vstruct.VArray([ v_uint32() for i in range(2) ])
        self._pad0080 = v_bytes(size=56)


class TEB_ACTIVE_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.Previous = v_ptr32()
        self.Context = v_ptr32()


class ULARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_9007(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.McaCod = v_uint16()
        self.MsCod = v_uint16()
        self.OtherInfo = v_uint32()


class _unnamed_9000(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mca = _unnamed_9012()


class _unnamed_7723(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UserApcRoutine = v_ptr32()
        self.UserApcContext = v_ptr32()


class KWAIT_STATUS_REGISTER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint8()


class KGDTENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LimitLow = v_uint16()
        self.BaseLow = v_uint16()
        self.HighWord = _unnamed_6512()


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


class RTL_STD_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()


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


class _unnamed_9480(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Generic = _unnamed_9700()


class HEAP_LIST_LOOKUP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExtendedLookup = v_ptr32()
        self.ArraySize = v_uint32()
        self.ExtraItem = v_uint32()
        self.ItemCount = v_uint32()
        self.OutOfRangeItems = v_uint32()
        self.BaseIndex = v_uint32()
        self.ListHead = v_ptr32()
        self.ListsInUseUlong = v_ptr32()
        self.ListHints = v_ptr32()


class EPROCESS_QUOTA_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class HEAP_DEBUGGING_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterceptorFunction = v_ptr32()
        self.InterceptorValue = v_uint16()
        self._pad0008 = v_bytes(size=2)
        self.ExtendedOptions = v_uint32()
        self.StackTraceDepth = v_uint32()
        self.MinTotalBlockSize = v_uint32()
        self.MaxTotalBlockSize = v_uint32()
        self.HeapLeakEnumerationRoutine = v_ptr32()


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
        self.IFEOKey = v_ptr32()
        self.CrossProcessFlags = v_uint32()
        self.KernelCallbackTable = v_ptr32()
        self.SystemReserved = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.AtlThunkSListPtr32 = v_uint32()
        self.ApiSetMap = v_ptr32()
        self.TlsExpansionCounter = v_uint32()
        self.TlsBitmap = v_ptr32()
        self.TlsBitmapBits = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.ReadOnlySharedMemoryBase = v_ptr32()
        self.HotpatchInformation = v_ptr32()
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
        self.ActiveProcessAffinityMask = v_uint32()
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
        self.WerRegistrationData = v_ptr32()
        self.WerShipAssertPtr = v_ptr32()
        self.pContextData = v_ptr32()
        self.pImageHeaderHash = v_ptr32()
        self.TracingFlags = v_uint32()
        self._pad0248 = v_bytes(size=4)


class _unnamed_7923(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.EaList = v_ptr32()
        self.EaListLength = v_uint32()
        self.EaIndex = v_uint32()


class STACK_TRACE_DATABASE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(56) ])
        self.Reserved2 = v_ptr32()
        self.PeakHashCollisionListLength = v_uint32()
        self.LowerMemoryStart = v_ptr32()
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
        self.NumberOfEntriesAllocated = v_uint32()
        self.NumberOfEntriesAvailable = v_uint32()
        self.NumberOfAllocationFailures = v_uint32()
        self._pad0078 = v_bytes(size=4)
        self.FreeLists = vstruct.VArray([ SLIST_HEADER() for i in range(32) ])
        self.NumberOfBuckets = v_uint32()
        self.Buckets = vstruct.VArray([ RTL_STD_LIST_HEAD() for i in range(1) ])
        self._pad0188 = v_bytes(size=4)


class _unnamed_7835(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


class _unnamed_7842(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class _unnamed_7928(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()


class KDPC(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Importance = v_uint8()
        self.Number = v_uint16()
        self.DpcListEntry = LIST_ENTRY()
        self.DeferredRoutine = v_ptr32()
        self.DeferredContext = v_ptr32()
        self.SystemArgument1 = v_ptr32()
        self.SystemArgument2 = v_ptr32()
        self.DpcData = v_ptr32()


class KEVENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class KSEMAPHORE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.Limit = v_uint32()


class MM_PAGE_ACCESS_INFO_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Link = SINGLE_LIST_ENTRY()
        self.Type = v_uint32()
        self.EmptySequenceNumber = v_uint32()
        self._pad0010 = v_bytes(size=4)
        self.CreateTime = v_uint64()
        self.EmptyTime = v_uint64()
        self.PageEntry = v_ptr32()
        self.FileEntry = v_ptr32()
        self.FirstFileEntry = v_ptr32()
        self.Process = v_ptr32()
        self.SessionId = v_uint32()
        self._pad0038 = v_bytes(size=4)


class OBJECT_TYPE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TypeList = LIST_ENTRY()
        self.Name = UNICODE_STRING()
        self.DefaultObject = v_ptr32()
        self.Index = v_uint8()
        self._pad0018 = v_bytes(size=3)
        self.TotalNumberOfObjects = v_uint32()
        self.TotalNumberOfHandles = v_uint32()
        self.HighWaterNumberOfObjects = v_uint32()
        self.HighWaterNumberOfHandles = v_uint32()
        self.TypeInfo = OBJECT_TYPE_INITIALIZER()
        self.TypeLock = EX_PUSH_LOCK()
        self.Key = v_uint32()
        self.CallbackList = LIST_ENTRY()


class HANDLE_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TableCode = v_uint32()
        self.QuotaProcess = v_ptr32()
        self.UniqueProcessId = v_ptr32()
        self.HandleLock = EX_PUSH_LOCK()
        self.HandleTableList = LIST_ENTRY()
        self.HandleContentionEvent = EX_PUSH_LOCK()
        self.DebugInfo = v_ptr32()
        self.ExtraInfoPages = v_uint32()
        self.Flags = v_uint32()
        self.FirstFreeHandle = v_uint32()
        self.LastFreeHandleEntry = v_ptr32()
        self.HandleCount = v_uint32()
        self.NextHandleNeedingPool = v_uint32()
        self.HandleCountHighWatermark = v_uint32()


class MMSUPPORT_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WorkingSetType = v_uint8()
        self.SessionMaster = v_uint8()
        self.MemoryPriority = v_uint8()
        self.WsleDeleted = v_uint8()


class PROC_PERF_DOMAIN(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Link = LIST_ENTRY()
        self.Master = v_ptr32()
        self.Members = KAFFINITY_EX()
        self.FeedbackHandler = v_ptr32()
        self.GetFFHThrottleState = v_ptr32()
        self.BoostPolicyHandler = v_ptr32()
        self.PerfSelectionHandler = v_ptr32()
        self.PerfHandler = v_ptr32()
        self.Processors = v_ptr32()
        self.PerfChangeTime = v_uint64()
        self.ProcessorCount = v_uint32()
        self.PreviousFrequencyMhz = v_uint32()
        self.CurrentFrequencyMhz = v_uint32()
        self.PreviousFrequency = v_uint32()
        self.CurrentFrequency = v_uint32()
        self.CurrentPerfContext = v_uint32()
        self.DesiredFrequency = v_uint32()
        self.MaxFrequency = v_uint32()
        self.MinPerfPercent = v_uint32()
        self.MinThrottlePercent = v_uint32()
        self.MaxPercent = v_uint32()
        self.MinPercent = v_uint32()
        self.ConstrainedMaxPercent = v_uint32()
        self.ConstrainedMinPercent = v_uint32()
        self.Coordination = v_uint8()
        self._pad0074 = v_bytes(size=3)
        self.PerfChangeIntervalCount = v_uint32()


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


class LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_ptr32()
        self.Blink = v_ptr32()


class M128A(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Low = v_uint64()
        self.High = v_uint64()


class RTL_DYNAMIC_HASH_TABLE_ENUMERATOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashEntry = RTL_DYNAMIC_HASH_TABLE_ENTRY()
        self.ChainHead = v_ptr32()
        self.BucketIndex = v_uint32()


class _unnamed_8067(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoResourceRequirementList = v_ptr32()


class GUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data1 = v_uint32()
        self.Data2 = v_uint16()
        self.Data3 = v_uint16()
        self.Data4 = vstruct.VArray([ v_uint8() for i in range(8) ])


class HEAP_UCR_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.SegmentEntry = LIST_ENTRY()
        self.Address = v_ptr32()
        self.Size = v_uint32()


class MCA_EXCEPTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VersionNumber = v_uint32()
        self.ExceptionType = v_uint32()
        self.TimeStamp = LARGE_INTEGER()
        self.ProcessorNumber = v_uint32()
        self.Reserved1 = v_uint32()
        self.u = _unnamed_9000()
        self.ExtCnt = v_uint32()
        self.Reserved3 = v_uint32()
        self.ExtReg = vstruct.VArray([ v_uint64() for i in range(24) ])


class PSP_CPU_QUOTA_APC(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class KAPC_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ApcListHead = vstruct.VArray([ LIST_ENTRY() for i in range(2) ])
        self.Process = v_ptr32()
        self.KernelApcInProgress = v_uint8()
        self.KernelApcPending = v_uint8()
        self.UserApcPending = v_uint8()
        self._pad0018 = v_bytes(size=1)


class COUNTER_READING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()
        self.Index = v_uint32()
        self.Start = v_uint64()
        self.Total = v_uint64()


class _unnamed_8109(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerState = v_uint32()


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


class XSAVE_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LegacyState = XSAVE_FORMAT()
        self.Header = XSAVE_AREA_HEADER()


class _unnamed_10265(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length48 = v_uint32()
        self.Alignment48 = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


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
        self.AssociatedIrp = _unnamed_7705()
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
        self.Overlay = _unnamed_7708()
        self.CancelRoutine = v_ptr32()
        self.UserBuffer = v_ptr32()
        self.Tail = _unnamed_7711()


class KTHREAD_COUNTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WaitReasonBitMap = v_uint64()
        self.UserData = v_ptr32()
        self.Flags = v_uint32()
        self.ContextSwitches = v_uint32()
        self._pad0018 = v_bytes(size=4)
        self.CycleTimeBias = v_uint64()
        self.HardwareCounters = v_uint64()
        self.HwCounter = vstruct.VArray([ COUNTER_READING() for i in range(16) ])


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


class FILE_GET_QUOTA_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextEntryOffset = v_uint32()
        self.SidLength = v_uint32()
        self.Sid = SID()


class KGATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


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
        self.ClientDriverExtension = v_ptr32()
        self.FsFilterCallbacks = v_ptr32()


class TP_NBQ_GUARD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.GuardLinks = LIST_ENTRY()
        self.Guards = vstruct.VArray([ v_ptr32() for i in range(2) ])


class flags(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Removable = v_uint8()


class MM_AVL_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BalancedRoot = MMADDRESS_NODE()
        self.DepthOfTree = v_uint32()
        self.NodeHint = v_ptr32()
        self.NodeFreeHint = v_ptr32()


class WHEA_PERSISTENCE_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint64()


class WHEA_ERROR_RECORD_SECTION_DESCRIPTOR_VALIDBITS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FRUId = v_uint8()


class EXCEPTION_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_ptr32()
        self.ExceptionAddress = v_ptr32()
        self.NumberParameters = v_uint32()
        self.ExceptionInformation = vstruct.VArray([ v_uint32() for i in range(15) ])


class PROCESSOR_NUMBER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Group = v_uint16()
        self.Number = v_uint8()
        self.Reserved = v_uint8()


class MM_PAGE_ACCESS_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = MM_PAGE_ACCESS_INFO_FLAGS()
        self.PointerProtoPte = v_ptr32()


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


class _unnamed_7807(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.FileAttributes = v_uint16()
        self.ShareAccess = v_uint16()
        self.EaLength = v_uint32()


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


class LFH_BLOCK_ZONE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.FreePointer = v_ptr32()
        self.Limit = v_ptr32()


class FILE_STANDARD_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocationSize = LARGE_INTEGER()
        self.EndOfFile = LARGE_INTEGER()
        self.NumberOfLinks = v_uint32()
        self.DeletePending = v_uint8()
        self.Directory = v_uint8()
        self._pad0018 = v_bytes(size=2)


class LFH_HEAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = RTL_CRITICAL_SECTION()
        self.SubSegmentZones = LIST_ENTRY()
        self.ZoneBlockSize = v_uint32()
        self.Heap = v_ptr32()
        self.SegmentChange = v_uint32()
        self.SegmentCreate = v_uint32()
        self.SegmentInsertInFree = v_uint32()
        self.SegmentDelete = v_uint32()
        self.CacheAllocs = v_uint32()
        self.CacheFrees = v_uint32()
        self.SizeInCache = v_uint32()
        self._pad0048 = v_bytes(size=4)
        self.RunInfo = HEAP_BUCKET_RUN_INFO()
        self.UserBlockCache = vstruct.VArray([ USER_MEMORY_CACHE_ENTRY() for i in range(12) ])
        self.Buckets = vstruct.VArray([ HEAP_BUCKET() for i in range(128) ])
        self.LocalData = vstruct.VArray([ HEAP_LOCAL_DATA() for i in range(1) ])


class _unnamed_7980(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Srb = v_ptr32()


class HEAP_BUCKET_RUN_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Bucket = v_uint32()
        self.RunLength = v_uint32()


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
        self.ShutdownInProgress = v_uint8()
        self._pad002c = v_bytes(size=3)
        self.ShutdownThreadId = v_ptr32()


class _unnamed_7988(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.StartSid = v_ptr32()
        self.SidList = v_ptr32()
        self.SidListLength = v_uint32()


class _unnamed_7942(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FsInformationClass = v_uint32()


class HEAP_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Flags = v_uint8()
        self.SmallTagIndex = v_uint8()
        self.PreviousSize = v_uint16()
        self.SegmentOffset = v_uint8()
        self.UnusedBytes = v_uint8()


class MM_PAGE_ACCESS_INFO_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.File = _unnamed_8913()


class SECURITY_SUBJECT_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientToken = v_ptr32()
        self.ImpersonationLevel = v_uint32()
        self.PrimaryToken = v_ptr32()
        self.ProcessAuditId = v_ptr32()


class _unnamed_7976(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Vpb = v_ptr32()
        self.DeviceObject = v_ptr32()


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
        self.IrpListLock = v_uint32()
        self.IrpList = LIST_ENTRY()
        self.FileObjectExtension = v_ptr32()


class PPM_IDLE_STATES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Flags = _unnamed_9303()
        self.TargetState = v_uint32()
        self.ActualState = v_uint32()
        self.OldState = v_uint32()
        self.NewlyUnparked = v_uint8()
        self._pad0018 = v_bytes(size=3)
        self.TargetProcessors = KAFFINITY_EX()
        self.State = vstruct.VArray([ PPM_IDLE_STATE() for i in range(1) ])


class _unnamed_8142(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemContext = v_uint32()
        self.Type = v_uint32()
        self.State = POWER_STATE()
        self.ShutdownType = v_uint32()


class HEAP_SUBSEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LocalInfo = v_ptr32()
        self.UserBlocks = v_ptr32()
        self.AggregateExchg = INTERLOCK_SEQ()
        self.BlockSize = v_uint16()
        self.Flags = v_uint16()
        self.BlockCount = v_uint16()
        self.SizeIndex = v_uint8()
        self.AffinityIndex = v_uint8()
        self.SFreeListEntry = SINGLE_LIST_ENTRY()
        self.Lock = v_uint32()


class ERESOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemResourcesList = LIST_ENTRY()
        self.OwnerTable = v_ptr32()
        self.ActiveCount = v_uint16()
        self.Flag = v_uint16()
        self.SharedWaiters = v_ptr32()
        self.ExclusiveWaiters = v_ptr32()
        self.OwnerEntry = OWNER_ENTRY()
        self.ActiveEntries = v_uint32()
        self.ContentionCount = v_uint32()
        self.NumberOfSharedWaiters = v_uint32()
        self.NumberOfExclusiveWaiters = v_uint32()
        self.Address = v_ptr32()
        self.SpinLock = v_uint32()


class ACCESS_REASONS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data = vstruct.VArray([ v_uint32() for i in range(32) ])


class TP_TASK_CALLBACKS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExecuteCallback = v_ptr32()
        self.Unposted = v_ptr32()


class _unnamed_9726(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class _unnamed_9722(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint32()
        self.Length = v_uint32()
        self.Reserved = v_uint32()


class _unnamed_9720(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data = vstruct.VArray([ v_uint32() for i in range(3) ])


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class XSTATE_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mask = v_uint64()
        self.Length = v_uint32()
        self.Reserved1 = v_uint32()
        self.Area = v_ptr32()
        self.Reserved2 = v_uint32()
        self.Buffer = v_ptr32()
        self.Reserved3 = v_uint32()


class HEAP_FREE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Flags = v_uint8()
        self.SmallTagIndex = v_uint8()
        self.PreviousSize = v_uint16()
        self.SegmentOffset = v_uint8()
        self.UnusedBytes = v_uint8()
        self.FreeList = LIST_ENTRY()


class KSTACK_COUNT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Value = v_uint32()


class MMSUPPORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WorkingSetMutex = EX_PUSH_LOCK()
        self.ExitGate = v_ptr32()
        self.AccessLog = v_ptr32()
        self.WorkingSetExpansionLinks = LIST_ENTRY()
        self.AgeDistribution = vstruct.VArray([ v_uint32() for i in range(7) ])
        self.MinimumWorkingSetSize = v_uint32()
        self.WorkingSetSize = v_uint32()
        self.WorkingSetPrivateSize = v_uint32()
        self.MaximumWorkingSetSize = v_uint32()
        self.ChargedWslePages = v_uint32()
        self.ActualWslePages = v_uint32()
        self.WorkingSetSizeOverhead = v_uint32()
        self.PeakWorkingSetSize = v_uint32()
        self.HardFaultCount = v_uint32()
        self.VmWorkingSetList = v_ptr32()
        self.NextPageColor = v_uint16()
        self.LastTrimStamp = v_uint16()
        self.PageFaultCount = v_uint32()
        self.RepurposeCount = v_uint32()
        self.Spare = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.Flags = MMSUPPORT_FLAGS()


class HEAP_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = HEAP_ENTRY()
        self.SegmentSignature = v_uint32()
        self.SegmentFlags = v_uint32()
        self.SegmentListEntry = LIST_ENTRY()
        self.Heap = v_ptr32()
        self.BaseAddress = v_ptr32()
        self.NumberOfPages = v_uint32()
        self.FirstEntry = v_ptr32()
        self.LastValidEntry = v_ptr32()
        self.NumberOfUnCommittedPages = v_uint32()
        self.NumberOfUnCommittedRanges = v_uint32()
        self.SegmentAllocatorBackTraceIndex = v_uint16()
        self.Reserved = v_uint16()
        self.UCRSegmentList = LIST_ENTRY()


class WHEA_ERROR_RECORD_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.Revision = WHEA_REVISION()
        self.SignatureEnd = v_uint32()
        self.SectionCount = v_uint16()
        self.Severity = v_uint32()
        self.ValidBits = WHEA_ERROR_RECORD_HEADER_VALIDBITS()
        self.Length = v_uint32()
        self.Timestamp = WHEA_TIMESTAMP()
        self.PlatformId = GUID()
        self.PartitionId = GUID()
        self.CreatorId = GUID()
        self.NotifyType = GUID()
        self.RecordId = v_uint64()
        self.Flags = WHEA_ERROR_RECORD_HEADER_FLAGS()
        self.PersistenceInfo = WHEA_PERSISTENCE_INFO()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(12) ])


class EVENT_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Id = v_uint16()
        self.Version = v_uint8()
        self.Channel = v_uint8()
        self.Level = v_uint8()
        self.Opcode = v_uint8()
        self.Task = v_uint16()
        self.Keyword = v_uint64()


class _unnamed_8914(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FilePointerIndex = v_uint32()


class _unnamed_10251(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.MinBusNumber = v_uint32()
        self.MaxBusNumber = v_uint32()
        self.Reserved = v_uint32()


class _unnamed_10256(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Priority = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class FLS_CALLBACK_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class ACL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AclRevision = v_uint8()
        self.Sbz1 = v_uint8()
        self.AclSize = v_uint16()
        self.AceCount = v_uint16()
        self.Sbz2 = v_uint16()


class LIST_ENTRY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint64()
        self.Blink = v_uint64()


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
        self.ForwarderLinks = LIST_ENTRY()
        self.ServiceTagLinks = LIST_ENTRY()
        self.StaticLinks = LIST_ENTRY()
        self.ContextInformation = v_ptr32()
        self.OriginalBase = v_uint32()
        self.LoadTime = LARGE_INTEGER()


class LOOKASIDE_LIST_EX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE_POOL()


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
        self.SpareBytes = vstruct.VArray([ v_uint8() for i in range(36) ])
        self.TxFsContext = v_uint32()
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
        self.Instrumentation = vstruct.VArray([ v_ptr32() for i in range(9) ])
        self.ActivityId = GUID()
        self.SubProcessTag = v_ptr32()
        self.EtwLocalData = v_ptr32()
        self.EtwTraceData = v_ptr32()
        self.WinSockData = v_ptr32()
        self.GdiBatchCount = v_uint32()
        self.CurrentIdealProcessor = PROCESSOR_NUMBER()
        self.GuaranteedStackBytes = v_uint32()
        self.ReservedForPerf = v_ptr32()
        self.ReservedForOle = v_ptr32()
        self.WaitingOnLoaderLock = v_uint32()
        self.SavedPriorityState = v_ptr32()
        self.SoftPatchPtr1 = v_uint32()
        self.ThreadPoolData = v_ptr32()
        self.TlsExpansionSlots = v_ptr32()
        self.MuiGeneration = v_uint32()
        self.IsImpersonating = v_uint32()
        self.NlsCache = v_ptr32()
        self.pShimData = v_ptr32()
        self.HeapVirtualAffinity = v_uint32()
        self.CurrentTransactionHandle = v_ptr32()
        self.ActiveFrame = v_ptr32()
        self.FlsData = v_ptr32()
        self.PreferredLanguages = v_ptr32()
        self.UserPrefLanguages = v_ptr32()
        self.MergedPrefLanguages = v_ptr32()
        self.MuiImpersonation = v_uint32()
        self.CrossTebFlags = v_uint16()
        self.SameTebFlags = v_uint16()
        self.TxnScopeEnterCallback = v_ptr32()
        self.TxnScopeExitCallback = v_ptr32()
        self.TxnScopeContext = v_ptr32()
        self.LockCount = v_uint32()
        self.SpareUlong0 = v_uint32()
        self.ResourceRetValue = v_ptr32()


class EX_RUNDOWN_REF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()


class XSAVE_FORMAT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlWord = v_uint16()
        self.StatusWord = v_uint16()
        self.TagWord = v_uint8()
        self.Reserved1 = v_uint8()
        self.ErrorOpcode = v_uint16()
        self.ErrorOffset = v_uint32()
        self.ErrorSelector = v_uint16()
        self.Reserved2 = v_uint16()
        self.DataOffset = v_uint32()
        self.DataSelector = v_uint16()
        self.Reserved3 = v_uint16()
        self.MxCsr = v_uint32()
        self.MxCsr_Mask = v_uint32()
        self.FloatRegisters = vstruct.VArray([ M128A() for i in range(8) ])
        self.XmmRegisters = vstruct.VArray([ M128A() for i in range(8) ])
        self.Reserved4 = vstruct.VArray([ v_uint8() for i in range(192) ])
        self.StackControl = vstruct.VArray([ v_uint32() for i in range(7) ])
        self.Cr0NpxState = v_uint32()


class PO_DIAG_STACK_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StackDepth = v_uint32()
        self.Stack = vstruct.VArray([ v_ptr32() for i in range(1) ])


class IMAGE_DOS_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.e_magic = v_uint16()
        self.e_cblp = v_uint16()
        self.e_cp = v_uint16()
        self.e_crlc = v_uint16()
        self.e_cparhdr = v_uint16()
        self.e_minalloc = v_uint16()
        self.e_maxalloc = v_uint16()
        self.e_ss = v_uint16()
        self.e_sp = v_uint16()
        self.e_csum = v_uint16()
        self.e_ip = v_uint16()
        self.e_cs = v_uint16()
        self.e_lfarlc = v_uint16()
        self.e_ovno = v_uint16()
        self.e_res = vstruct.VArray([ v_uint16() for i in range(4) ])
        self.e_oemid = v_uint16()
        self.e_oeminfo = v_uint16()
        self.e_res2 = vstruct.VArray([ v_uint16() for i in range(10) ])
        self.e_lfanew = v_uint32()


class RTL_DYNAMIC_HASH_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Linkage = LIST_ENTRY()
        self.Signature = v_uint32()


class MMADDRESS_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_9496()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()


class TXN_PARAMETER_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.TxFsContext = v_uint16()
        self.TransactionObject = v_ptr32()


class QUAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UseThisFieldToCopy = v_uint64()


class HEAP_TUNING_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CommittThresholdShift = v_uint32()
        self.MaxPreCommittThreshold = v_uint32()


class KPRCB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinorVersion = v_uint16()
        self.MajorVersion = v_uint16()
        self.CurrentThread = v_ptr32()
        self.NextThread = v_ptr32()
        self.IdleThread = v_ptr32()
        self.LegacyNumber = v_uint8()
        self.NestingLevel = v_uint8()
        self.BuildType = v_uint16()
        self.CpuType = v_uint8()
        self.CpuID = v_uint8()
        self.CpuStep = v_uint16()
        self.ProcessorState = KPROCESSOR_STATE()
        self.KernelReserved = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.HalReserved = vstruct.VArray([ v_uint32() for i in range(16) ])
        self.CFlushSize = v_uint32()
        self.CoresPerPhysicalProcessor = v_uint8()
        self.LogicalProcessorsPerCore = v_uint8()
        self.PrcbPad0 = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.MHz = v_uint32()
        self.CpuVendor = v_uint8()
        self.GroupIndex = v_uint8()
        self.Group = v_uint16()
        self.GroupSetMember = v_uint32()
        self.Number = v_uint32()
        self.PrcbPad1 = vstruct.VArray([ v_uint8() for i in range(72) ])
        self.LockQueue = vstruct.VArray([ KSPIN_LOCK_QUEUE() for i in range(17) ])
        self.NpxThread = v_ptr32()
        self.InterruptCount = v_uint32()
        self.KernelTime = v_uint32()
        self.UserTime = v_uint32()
        self.DpcTime = v_uint32()
        self.DpcTimeCount = v_uint32()
        self.InterruptTime = v_uint32()
        self.AdjustDpcThreshold = v_uint32()
        self.PageColor = v_uint32()
        self.DebuggerSavedIRQL = v_uint8()
        self.NodeColor = v_uint8()
        self.PrcbPad20 = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.NodeShiftedColor = v_uint32()
        self.ParentNode = v_ptr32()
        self.SecondaryColorMask = v_uint32()
        self.DpcTimeLimit = v_uint32()
        self.PrcbPad21 = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.CcFastReadNoWait = v_uint32()
        self.CcFastReadWait = v_uint32()
        self.CcFastReadNotPossible = v_uint32()
        self.CcCopyReadNoWait = v_uint32()
        self.CcCopyReadWait = v_uint32()
        self.CcCopyReadNoWaitMiss = v_uint32()
        self.MmSpinLockOrdering = v_uint32()
        self.IoReadOperationCount = v_uint32()
        self.IoWriteOperationCount = v_uint32()
        self.IoOtherOperationCount = v_uint32()
        self.IoReadTransferCount = LARGE_INTEGER()
        self.IoWriteTransferCount = LARGE_INTEGER()
        self.IoOtherTransferCount = LARGE_INTEGER()
        self.CcFastMdlReadNoWait = v_uint32()
        self.CcFastMdlReadWait = v_uint32()
        self.CcFastMdlReadNotPossible = v_uint32()
        self.CcMapDataNoWait = v_uint32()
        self.CcMapDataWait = v_uint32()
        self.CcPinMappedDataCount = v_uint32()
        self.CcPinReadNoWait = v_uint32()
        self.CcPinReadWait = v_uint32()
        self.CcMdlReadNoWait = v_uint32()
        self.CcMdlReadWait = v_uint32()
        self.CcLazyWriteHotSpots = v_uint32()
        self.CcLazyWriteIos = v_uint32()
        self.CcLazyWritePages = v_uint32()
        self.CcDataFlushes = v_uint32()
        self.CcDataPages = v_uint32()
        self.CcLostDelayedWrites = v_uint32()
        self.CcFastReadResourceMiss = v_uint32()
        self.CcCopyReadWaitMiss = v_uint32()
        self.CcFastMdlReadResourceMiss = v_uint32()
        self.CcMapDataNoWaitMiss = v_uint32()
        self.CcMapDataWaitMiss = v_uint32()
        self.CcPinReadNoWaitMiss = v_uint32()
        self.CcPinReadWaitMiss = v_uint32()
        self.CcMdlReadNoWaitMiss = v_uint32()
        self.CcMdlReadWaitMiss = v_uint32()
        self.CcReadAheadIos = v_uint32()
        self.KeAlignmentFixupCount = v_uint32()
        self.KeExceptionDispatchCount = v_uint32()
        self.KeSystemCalls = v_uint32()
        self.AvailableTime = v_uint32()
        self.PrcbPad22 = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.PPLookasideList = vstruct.VArray([ PP_LOOKASIDE_LIST() for i in range(16) ])
        self.PPNPagedLookasideList = vstruct.VArray([ GENERAL_LOOKASIDE_POOL() for i in range(32) ])
        self.PPPagedLookasideList = vstruct.VArray([ GENERAL_LOOKASIDE_POOL() for i in range(32) ])
        self.PacketBarrier = v_uint32()
        self.ReverseStall = v_uint32()
        self.IpiFrame = v_ptr32()
        self.PrcbPad3 = vstruct.VArray([ v_uint8() for i in range(52) ])
        self.CurrentPacket = vstruct.VArray([ v_ptr32() for i in range(3) ])
        self.TargetSet = v_uint32()
        self.WorkerRoutine = v_ptr32()
        self.IpiFrozen = v_uint32()
        self.PrcbPad4 = vstruct.VArray([ v_uint8() for i in range(40) ])
        self.RequestSummary = v_uint32()
        self.SignalDone = v_ptr32()
        self.PrcbPad50 = vstruct.VArray([ v_uint8() for i in range(56) ])
        self.DpcData = vstruct.VArray([ KDPC_DATA() for i in range(2) ])
        self.DpcStack = v_ptr32()
        self.MaximumDpcQueueDepth = v_uint32()
        self.DpcRequestRate = v_uint32()
        self.MinimumDpcRate = v_uint32()
        self.DpcLastCount = v_uint32()
        self.PrcbLock = v_uint32()
        self.DpcGate = KGATE()
        self.ThreadDpcEnable = v_uint8()
        self.QuantumEnd = v_uint8()
        self.DpcRoutineActive = v_uint8()
        self.IdleSchedule = v_uint8()
        self.DpcRequestSummary = v_uint32()
        self.TimerHand = v_uint32()
        self.LastTick = v_uint32()
        self.MasterOffset = v_uint32()
        self.PrcbPad41 = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.PeriodicCount = v_uint32()
        self.PeriodicBias = v_uint32()
        self._pad1958 = v_bytes(size=4)
        self.TickOffset = v_uint64()
        self.TimerTable = KTIMER_TABLE()
        self.CallDpc = KDPC()
        self.ClockKeepAlive = v_uint32()
        self.ClockCheckSlot = v_uint8()
        self.ClockPollCycle = v_uint8()
        self.PrcbPad6 = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.DpcWatchdogPeriod = v_uint32()
        self.DpcWatchdogCount = v_uint32()
        self.ThreadWatchdogPeriod = v_uint32()
        self.ThreadWatchdogCount = v_uint32()
        self.KeSpinLockOrdering = v_uint32()
        self.PrcbPad70 = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.WaitListHead = LIST_ENTRY()
        self.WaitLock = v_uint32()
        self.ReadySummary = v_uint32()
        self.QueueIndex = v_uint32()
        self.DeferredReadyListHead = SINGLE_LIST_ENTRY()
        self.StartCycles = v_uint64()
        self.CycleTime = v_uint64()
        self.HighCycleTime = v_uint32()
        self.PrcbPad71 = v_uint32()
        self.PrcbPad72 = vstruct.VArray([ v_uint64() for i in range(2) ])
        self.DispatcherReadyListHead = vstruct.VArray([ LIST_ENTRY() for i in range(32) ])
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
        self.CachedCommit = v_uint32()
        self.CachedResidentAvailable = v_uint32()
        self.HyperPte = v_ptr32()
        self.PrcbPad8 = vstruct.VArray([ v_uint8() for i in range(4) ])
        self.VendorString = vstruct.VArray([ v_uint8() for i in range(13) ])
        self.InitialApicId = v_uint8()
        self.LogicalProcessorsPerPhysicalProcessor = v_uint8()
        self.PrcbPad9 = vstruct.VArray([ v_uint8() for i in range(5) ])
        self.FeatureBits = v_uint32()
        self._pad3388 = v_bytes(size=4)
        self.UpdateSignature = LARGE_INTEGER()
        self.IsrTime = v_uint64()
        self.RuntimeAccumulation = v_uint64()
        self.PowerState = PROCESSOR_POWER_STATE()
        self.DpcWatchdogDpc = KDPC()
        self.DpcWatchdogTimer = KTIMER()
        self.WheaInfo = v_ptr32()
        self.EtwSupport = v_ptr32()
        self.InterruptObjectPool = SLIST_HEADER()
        self.HypercallPageList = SLIST_HEADER()
        self.HypercallPageVirtual = v_ptr32()
        self.VirtualApicAssist = v_ptr32()
        self.StatisticsPage = v_ptr32()
        self.RateControl = v_ptr32()
        self.Cache = vstruct.VArray([ CACHE_DESCRIPTOR() for i in range(5) ])
        self.CacheCount = v_uint32()
        self.CacheProcessorMask = vstruct.VArray([ v_uint32() for i in range(5) ])
        self.PackageProcessorSet = KAFFINITY_EX()
        self.PrcbPad91 = vstruct.VArray([ v_uint32() for i in range(1) ])
        self.CoreProcessorSet = v_uint32()
        self.TimerExpirationDpc = KDPC()
        self.SpinLockAcquireCount = v_uint32()
        self.SpinLockContentionCount = v_uint32()
        self.SpinLockSpinCount = v_uint32()
        self.IpiSendRequestBroadcastCount = v_uint32()
        self.IpiSendRequestRoutineCount = v_uint32()
        self.IpiSendSoftwareInterruptCount = v_uint32()
        self.ExInitializeResourceCount = v_uint32()
        self.ExReInitializeResourceCount = v_uint32()
        self.ExDeleteResourceCount = v_uint32()
        self.ExecutiveResourceAcquiresCount = v_uint32()
        self.ExecutiveResourceContentionsCount = v_uint32()
        self.ExecutiveResourceReleaseExclusiveCount = v_uint32()
        self.ExecutiveResourceReleaseSharedCount = v_uint32()
        self.ExecutiveResourceConvertsCount = v_uint32()
        self.ExAcqResExclusiveAttempts = v_uint32()
        self.ExAcqResExclusiveAcquiresExclusive = v_uint32()
        self.ExAcqResExclusiveAcquiresExclusiveRecursive = v_uint32()
        self.ExAcqResExclusiveWaits = v_uint32()
        self.ExAcqResExclusiveNotAcquires = v_uint32()
        self.ExAcqResSharedAttempts = v_uint32()
        self.ExAcqResSharedAcquiresExclusive = v_uint32()
        self.ExAcqResSharedAcquiresShared = v_uint32()
        self.ExAcqResSharedAcquiresSharedRecursive = v_uint32()
        self.ExAcqResSharedWaits = v_uint32()
        self.ExAcqResSharedNotAcquires = v_uint32()
        self.ExAcqResSharedStarveExclusiveAttempts = v_uint32()
        self.ExAcqResSharedStarveExclusiveAcquiresExclusive = v_uint32()
        self.ExAcqResSharedStarveExclusiveAcquiresShared = v_uint32()
        self.ExAcqResSharedStarveExclusiveAcquiresSharedRecursive = v_uint32()
        self.ExAcqResSharedStarveExclusiveWaits = v_uint32()
        self.ExAcqResSharedStarveExclusiveNotAcquires = v_uint32()
        self.ExAcqResSharedWaitForExclusiveAttempts = v_uint32()
        self.ExAcqResSharedWaitForExclusiveAcquiresExclusive = v_uint32()
        self.ExAcqResSharedWaitForExclusiveAcquiresShared = v_uint32()
        self.ExAcqResSharedWaitForExclusiveAcquiresSharedRecursive = v_uint32()
        self.ExAcqResSharedWaitForExclusiveWaits = v_uint32()
        self.ExAcqResSharedWaitForExclusiveNotAcquires = v_uint32()
        self.ExSetResOwnerPointerExclusive = v_uint32()
        self.ExSetResOwnerPointerSharedNew = v_uint32()
        self.ExSetResOwnerPointerSharedOld = v_uint32()
        self.ExTryToAcqExclusiveAttempts = v_uint32()
        self.ExTryToAcqExclusiveAcquires = v_uint32()
        self.ExBoostExclusiveOwner = v_uint32()
        self.ExBoostSharedOwners = v_uint32()
        self.ExEtwSynchTrackingNotificationsCount = v_uint32()
        self.ExEtwSynchTrackingNotificationsAccountedCount = v_uint32()
        self.Context = v_ptr32()
        self.ContextFlags = v_uint32()
        self.ExtendedState = v_ptr32()
        self._pad3628 = v_bytes(size=4)


class _unnamed_7784(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceQueueEntry = KDEVICE_QUEUE_ENTRY()
        self.Thread = v_ptr32()
        self.AuxiliaryBuffer = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.CurrentStackLocation = v_ptr32()
        self.OriginalFileObject = v_ptr32()


class RTL_DYNAMIC_HASH_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.Shift = v_uint32()
        self.TableSize = v_uint32()
        self.Pivot = v_uint32()
        self.DivisorMask = v_uint32()
        self.NumEntries = v_uint32()
        self.NonEmptyBuckets = v_uint32()
        self.NumEnumerators = v_uint32()
        self.Directory = v_ptr32()


class KAFFINITY_EX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint16()
        self.Size = v_uint16()
        self.Reserved = v_uint32()
        self.Bitmap = vstruct.VArray([ v_uint32() for i in range(1) ])


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
        self.Queue = _unnamed_7305()
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


class USER_MEMORY_CACHE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UserBlocks = SLIST_HEADER()
        self.AvailableBlocks = v_uint32()
        self._pad0010 = v_bytes(size=4)


class _unnamed_6512(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Bytes = _unnamed_9067()


class EX_PUSH_LOCK_WAIT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WakeEvent = KEVENT()
        self.Next = v_ptr32()
        self.Last = v_ptr32()
        self.Previous = v_ptr32()
        self.ShareCount = v_uint32()
        self.Flags = v_uint32()
        self._pad0030 = v_bytes(size=12)


class _unnamed_8097(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InPath = v_uint8()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.Type = v_uint32()


class _unnamed_7945(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.FsControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.FileHeader = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorFunction = v_uint8()
        self.MinorFunction = v_uint8()
        self.Flags = v_uint8()
        self.Control = v_uint8()
        self.Parameters = _unnamed_7745()
        self.DeviceObject = v_ptr32()
        self.FileObject = v_ptr32()
        self.CompletionRoutine = v_ptr32()
        self.Context = v_ptr32()


class KNODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PagedPoolSListHead = SLIST_HEADER()
        self.NonPagedPoolSListHead = vstruct.VArray([ SLIST_HEADER() for i in range(3) ])
        self.Affinity = GROUP_AFFINITY()
        self.ProximityId = v_uint32()
        self.NodeNumber = v_uint16()
        self.PrimaryNodeNumber = v_uint16()
        self.MaximumProcessors = v_uint8()
        self.Color = v_uint8()
        self.Flags = flags()
        self.NodePad0 = v_uint8()
        self.Seed = v_uint32()
        self.MmShiftedColor = v_uint32()
        self.FreeCount = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.CachedKernelStacks = CACHED_KSTACK_LIST()
        self.ParkLock = v_uint32()
        self.NodePad1 = v_uint32()
        self._pad0080 = v_bytes(size=24)


class XSAVE_AREA_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mask = v_uint64()
        self.Reserved = vstruct.VArray([ v_uint64() for i in range(7) ])


class PSP_CPU_SHARE_CAPTURED_WEIGHT_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CapturedCpuShareWeight = v_uint32()
        self.CapturedTotalWeight = v_uint32()


class _unnamed_8070(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WhichSpace = v_uint32()
        self.Buffer = v_ptr32()
        self.Offset = v_uint32()
        self.Length = v_uint32()


class _unnamed_8075(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = v_uint8()


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
        self.EnvironmentSize = v_uint32()
        self.EnvironmentVersion = v_uint32()


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


class HEAP_BUCKET_COUNTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TotalBlocks = v_uint32()
        self.SubSegmentCounts = v_uint32()



