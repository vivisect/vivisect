# -*- coding: utf8 -*-
# Version: 5.2
# Architecture: i386
# CompanyName: Microsoft Corporation
# FileDescription: NT Kernel & System
# FileVersion: 5.2.3790.4998 (srv03_sp2_gdr.120503-0334)
# InternalName: ntkrnlmp.exe
# LegalCopyright:  Microsoft Corporation. All rights reserved.
# OriginalFilename: ntkrnlmp.exe
# ProductName: Microsoft Windows Operating System
# ProductVersion: 5.2.3790.4998
# Translation: 78644233
import vstruct
from vstruct.primitives import *

POLICY_AUDIT_EVENT_TYPE = v_enum()
POLICY_AUDIT_EVENT_TYPE.AuditCategorySystem = 0
POLICY_AUDIT_EVENT_TYPE.AuditCategoryLogon = 1
POLICY_AUDIT_EVENT_TYPE.AuditCategoryObjectAccess = 2
POLICY_AUDIT_EVENT_TYPE.AuditCategoryPrivilegeUse = 3
POLICY_AUDIT_EVENT_TYPE.AuditCategoryDetailedTracking = 4
POLICY_AUDIT_EVENT_TYPE.AuditCategoryPolicyChange = 5
POLICY_AUDIT_EVENT_TYPE.AuditCategoryAccountManagement = 6
POLICY_AUDIT_EVENT_TYPE.AuditCategoryDirectoryServiceAccess = 7
POLICY_AUDIT_EVENT_TYPE.AuditCategoryAccountLogon = 8


ARBITER_REQUEST_SOURCE = v_enum()
ARBITER_REQUEST_SOURCE.ArbiterRequestUndefined = -1
ARBITER_REQUEST_SOURCE.ArbiterRequestLegacyReported = 0
ARBITER_REQUEST_SOURCE.ArbiterRequestHalReported = 1
ARBITER_REQUEST_SOURCE.ArbiterRequestLegacyAssigned = 2
ARBITER_REQUEST_SOURCE.ArbiterRequestPnpDetected = 3
ARBITER_REQUEST_SOURCE.ArbiterRequestPnpEnumerated = 4


WOW64_SHARED_INFORMATION = v_enum()
WOW64_SHARED_INFORMATION.SharedNtdll32LdrInitializeThunk = 0
WOW64_SHARED_INFORMATION.SharedNtdll32KiUserExceptionDispatcher = 1
WOW64_SHARED_INFORMATION.SharedNtdll32KiUserApcDispatcher = 2
WOW64_SHARED_INFORMATION.SharedNtdll32KiUserCallbackDispatcher = 3
WOW64_SHARED_INFORMATION.SharedNtdll32LdrHotPatchRoutine = 4
WOW64_SHARED_INFORMATION.SharedNtdll32ExpInterlockedPopEntrySListFault = 5
WOW64_SHARED_INFORMATION.SharedNtdll32ExpInterlockedPopEntrySListResume = 6
WOW64_SHARED_INFORMATION.SharedNtdll32ExpInterlockedPopEntrySListEnd = 7
WOW64_SHARED_INFORMATION.SharedNtdll32Reserved2 = 8
WOW64_SHARED_INFORMATION.Wow64SharedPageEntriesCount = 9


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


KDPC_IMPORTANCE = v_enum()
KDPC_IMPORTANCE.LowImportance = 0
KDPC_IMPORTANCE.MediumImportance = 1
KDPC_IMPORTANCE.HighImportance = 2


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


MMSYSTEM_PTE_POOL_TYPE = v_enum()
MMSYSTEM_PTE_POOL_TYPE.SystemPteSpace = 0
MMSYSTEM_PTE_POOL_TYPE.NonPagedPoolExpansion = 1
MMSYSTEM_PTE_POOL_TYPE.MaximumPtePoolTypes = 2


POP_POLICY_DEVICE_TYPE = v_enum()
POP_POLICY_DEVICE_TYPE.PolicyDeviceSystemButton = 0
POP_POLICY_DEVICE_TYPE.PolicyDeviceThermalZone = 1
POP_POLICY_DEVICE_TYPE.PolicyDeviceBattery = 2
POP_POLICY_DEVICE_TYPE.PolicyInitiatePowerActionAPI = 3
POP_POLICY_DEVICE_TYPE.PolicySetPowerStateAPI = 4
POP_POLICY_DEVICE_TYPE.PolicyImmediateDozeS4 = 5
POP_POLICY_DEVICE_TYPE.PolicySystemIdle = 6


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


PF_SCENARIO_TYPE = v_enum()
PF_SCENARIO_TYPE.PfApplicationLaunchScenarioType = 0
PF_SCENARIO_TYPE.PfSystemBootScenarioType = 1
PF_SCENARIO_TYPE.PfMaxScenarioType = 2


TOKEN_TYPE = v_enum()
TOKEN_TYPE.TokenPrimary = 1
TOKEN_TYPE.TokenImpersonation = 2


VI_DEADLOCK_RESOURCE_TYPE = v_enum()
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockUnknown = 0
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockMutex = 1
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockMutexAbandoned = 2
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockFastMutex = 3
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockFastMutexUnsafe = 4
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockSpinLock = 5
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockQueuedSpinLock = 6
VI_DEADLOCK_RESOURCE_TYPE.VfDeadlockTypeMaximum = 7


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


ARBITER_ACTION = v_enum()
ARBITER_ACTION.ArbiterActionTestAllocation = 0
ARBITER_ACTION.ArbiterActionRetestAllocation = 1
ARBITER_ACTION.ArbiterActionCommitAllocation = 2
ARBITER_ACTION.ArbiterActionRollbackAllocation = 3
ARBITER_ACTION.ArbiterActionQueryAllocatedResources = 4
ARBITER_ACTION.ArbiterActionWriteReservedResources = 5
ARBITER_ACTION.ArbiterActionQueryConflict = 6
ARBITER_ACTION.ArbiterActionQueryArbitrate = 7
ARBITER_ACTION.ArbiterActionAddReserved = 8
ARBITER_ACTION.ArbiterActionBootAllocation = 9


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


PCI_DISPATCH_STYLE = v_enum()
PCI_DISPATCH_STYLE.IRP_COMPLETE = 0
PCI_DISPATCH_STYLE.IRP_DOWNWARD = 1
PCI_DISPATCH_STYLE.IRP_UPWARD = 2
PCI_DISPATCH_STYLE.IRP_DISPATCH = 3


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


PNP_DEVNODE_STATE = v_enum()
PNP_DEVNODE_STATE.DeviceNodeUnspecified = 768
PNP_DEVNODE_STATE.DeviceNodeUninitialized = 769
PNP_DEVNODE_STATE.DeviceNodeInitialized = 770
PNP_DEVNODE_STATE.DeviceNodeDriversAdded = 771
PNP_DEVNODE_STATE.DeviceNodeResourcesAssigned = 772
PNP_DEVNODE_STATE.DeviceNodeStartPending = 773
PNP_DEVNODE_STATE.DeviceNodeStartCompletion = 774
PNP_DEVNODE_STATE.DeviceNodeStartPostWork = 775
PNP_DEVNODE_STATE.DeviceNodeStarted = 776
PNP_DEVNODE_STATE.DeviceNodeQueryStopped = 777
PNP_DEVNODE_STATE.DeviceNodeStopped = 778
PNP_DEVNODE_STATE.DeviceNodeRestartCompletion = 779
PNP_DEVNODE_STATE.DeviceNodeEnumeratePending = 780
PNP_DEVNODE_STATE.DeviceNodeEnumerateCompletion = 781
PNP_DEVNODE_STATE.DeviceNodeAwaitingQueuedDeletion = 782
PNP_DEVNODE_STATE.DeviceNodeAwaitingQueuedRemoval = 783
PNP_DEVNODE_STATE.DeviceNodeQueryRemoved = 784
PNP_DEVNODE_STATE.DeviceNodeRemovePendingCloses = 785
PNP_DEVNODE_STATE.DeviceNodeRemoved = 786
PNP_DEVNODE_STATE.DeviceNodeDeletePendingCloses = 787
PNP_DEVNODE_STATE.DeviceNodeDeleted = 788
PNP_DEVNODE_STATE.MaxDeviceNodeState = 789


DEVICE_TEXT_TYPE = v_enum()
DEVICE_TEXT_TYPE.DeviceTextDescription = 0
DEVICE_TEXT_TYPE.DeviceTextLocationInformation = 1


POWER_STATE_TYPE = v_enum()
POWER_STATE_TYPE.SystemPowerState = 0
POWER_STATE_TYPE.DevicePowerState = 1


BUS_DATA_TYPE = v_enum()
BUS_DATA_TYPE.ConfigurationSpaceUndefined = -1
BUS_DATA_TYPE.Cmos = 0
BUS_DATA_TYPE.EisaConfiguration = 1
BUS_DATA_TYPE.Pos = 2
BUS_DATA_TYPE.CbusConfiguration = 3
BUS_DATA_TYPE.PCIConfiguration = 4
BUS_DATA_TYPE.VMEConfiguration = 5
BUS_DATA_TYPE.NuBusConfiguration = 6
BUS_DATA_TYPE.PCMCIAConfiguration = 7
BUS_DATA_TYPE.MPIConfiguration = 8
BUS_DATA_TYPE.MPSAConfiguration = 9
BUS_DATA_TYPE.PNPISAConfiguration = 10
BUS_DATA_TYPE.SgiInternalConfiguration = 11
BUS_DATA_TYPE.MaximumBusDataType = 12


LSA_FOREST_TRUST_RECORD_TYPE = v_enum()
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustTopLevelName = 0
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustTopLevelNameEx = 1
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustDomainInfo = 2
LSA_FOREST_TRUST_RECORD_TYPE.ForestTrustRecordTypeLast = 2


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


EXCEPTION_DISPOSITION = v_enum()
EXCEPTION_DISPOSITION.ExceptionContinueExecution = 0
EXCEPTION_DISPOSITION.ExceptionContinueSearch = 1
EXCEPTION_DISPOSITION.ExceptionNestedException = 2
EXCEPTION_DISPOSITION.ExceptionCollidedUnwind = 3


PNP_VETO_TYPE = v_enum()
PNP_VETO_TYPE.PNP_VetoTypeUnknown = 0
PNP_VETO_TYPE.PNP_VetoLegacyDevice = 1
PNP_VETO_TYPE.PNP_VetoPendingClose = 2
PNP_VETO_TYPE.PNP_VetoWindowsApp = 3
PNP_VETO_TYPE.PNP_VetoWindowsService = 4
PNP_VETO_TYPE.PNP_VetoOutstandingOpen = 5
PNP_VETO_TYPE.PNP_VetoDevice = 6
PNP_VETO_TYPE.PNP_VetoDriver = 7
PNP_VETO_TYPE.PNP_VetoIllegalDeviceRequest = 8
PNP_VETO_TYPE.PNP_VetoInsufficientPower = 9
PNP_VETO_TYPE.PNP_VetoNonDisableable = 10
PNP_VETO_TYPE.PNP_VetoLegacyDriver = 11
PNP_VETO_TYPE.PNP_VetoInsufficientRights = 12


PCI_SIGNATURE = v_enum()
PCI_SIGNATURE.PciPdoExtensionType = 1768116272
PCI_SIGNATURE.PciFdoExtensionType = 1768116273
PCI_SIGNATURE.PciArb_Io = 1768116274
PCI_SIGNATURE.PciArb_Memory = 1768116275
PCI_SIGNATURE.PciArb_Interrupt = 1768116276
PCI_SIGNATURE.PciArb_BusNumber = 1768116277
PCI_SIGNATURE.PciTrans_Interrupt = 1768116278
PCI_SIGNATURE.PciInterface_BusHandler = 1768116279
PCI_SIGNATURE.PciInterface_IntRouteHandler = 1768116280
PCI_SIGNATURE.PciInterface_PciCb = 1768116281
PCI_SIGNATURE.PciInterface_LegacyDeviceDetection = 1768116282
PCI_SIGNATURE.PciInterface_PmeHandler = 1768116283
PCI_SIGNATURE.PciInterface_DevicePresent = 1768116284
PCI_SIGNATURE.PciInterface_NativeIde = 1768116285
PCI_SIGNATURE.PciInterface_Location = 1768116286
PCI_SIGNATURE.PciInterface_AgpTarget = 1768116287


SECURITY_OPERATION_CODE = v_enum()
SECURITY_OPERATION_CODE.SetSecurityDescriptor = 0
SECURITY_OPERATION_CODE.QuerySecurityDescriptor = 1
SECURITY_OPERATION_CODE.DeleteSecurityDescriptor = 2
SECURITY_OPERATION_CODE.AssignSecurityDescriptor = 3


KTHREAD_STATE = v_enum()
KTHREAD_STATE.Initialized = 0
KTHREAD_STATE.Ready = 1
KTHREAD_STATE.Running = 2
KTHREAD_STATE.Standby = 3
KTHREAD_STATE.Terminated = 4
KTHREAD_STATE.Waiting = 5
KTHREAD_STATE.Transition = 6
KTHREAD_STATE.DeferredReady = 7
KTHREAD_STATE.GateWait = 8


PP_NPAGED_LOOKASIDE_NUMBER = v_enum()
PP_NPAGED_LOOKASIDE_NUMBER.LookasideSmallIrpList = 0
PP_NPAGED_LOOKASIDE_NUMBER.LookasideLargeIrpList = 1
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMdlList = 2
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCreateInfoList = 3
PP_NPAGED_LOOKASIDE_NUMBER.LookasideNameBufferList = 4
PP_NPAGED_LOOKASIDE_NUMBER.LookasideTwilightList = 5
PP_NPAGED_LOOKASIDE_NUMBER.LookasideCompletionList = 6
PP_NPAGED_LOOKASIDE_NUMBER.LookasideMaximumList = 7


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


PROXY_CLASS = v_enum()
PROXY_CLASS.ProxyFull = 0
PROXY_CLASS.ProxyService = 1
PROXY_CLASS.ProxyTree = 2
PROXY_CLASS.ProxyDirectory = 3


WAIT_TYPE = v_enum()
WAIT_TYPE.WaitAll = 0
WAIT_TYPE.WaitAny = 1


PLUGPLAY_EVENT_CATEGORY = v_enum()
PLUGPLAY_EVENT_CATEGORY.HardwareProfileChangeEvent = 0
PLUGPLAY_EVENT_CATEGORY.TargetDeviceChangeEvent = 1
PLUGPLAY_EVENT_CATEGORY.DeviceClassChangeEvent = 2
PLUGPLAY_EVENT_CATEGORY.CustomDeviceEvent = 3
PLUGPLAY_EVENT_CATEGORY.DeviceInstallEvent = 4
PLUGPLAY_EVENT_CATEGORY.DeviceArrivalEvent = 5
PLUGPLAY_EVENT_CATEGORY.PowerEvent = 6
PLUGPLAY_EVENT_CATEGORY.VetoEvent = 7
PLUGPLAY_EVENT_CATEGORY.BlockedDriverEvent = 8
PLUGPLAY_EVENT_CATEGORY.InvalidIDEvent = 9
PLUGPLAY_EVENT_CATEGORY.MaxPlugEventCategory = 10


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


MMLISTS = v_enum()
MMLISTS.ZeroedPageList = 0
MMLISTS.FreePageList = 1
MMLISTS.StandbyPageList = 2
MMLISTS.ModifiedPageList = 3
MMLISTS.ModifiedNoWritePageList = 4
MMLISTS.BadPageList = 5
MMLISTS.ActiveAndValid = 6
MMLISTS.TransitionPage = 7


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


ARBITER_RESULT = v_enum()
ARBITER_RESULT.ArbiterResultUndefined = -1
ARBITER_RESULT.ArbiterResultSuccess = 0
ARBITER_RESULT.ArbiterResultExternalConflict = 1
ARBITER_RESULT.ArbiterResultNullRequest = 2


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


MI_PFN_CACHE_ATTRIBUTE = v_enum()
MI_PFN_CACHE_ATTRIBUTE.MiNonCached = 0
MI_PFN_CACHE_ATTRIBUTE.MiCached = 1
MI_PFN_CACHE_ATTRIBUTE.MiWriteCombined = 2
MI_PFN_CACHE_ATTRIBUTE.MiNotMapped = 3


POWER_ACTION = v_enum()
POWER_ACTION.PowerActionNone = 0
POWER_ACTION.PowerActionReserved = 1
POWER_ACTION.PowerActionSleep = 2
POWER_ACTION.PowerActionHibernate = 3
POWER_ACTION.PowerActionShutdown = 4
POWER_ACTION.PowerActionShutdownReset = 5
POWER_ACTION.PowerActionShutdownOff = 6
POWER_ACTION.PowerActionWarmEject = 7


KINTERRUPT_MODE = v_enum()
KINTERRUPT_MODE.LevelSensitive = 0
KINTERRUPT_MODE.Latched = 1


PROFILE_STATUS = v_enum()
PROFILE_STATUS.DOCK_NOTDOCKDEVICE = 0
PROFILE_STATUS.DOCK_QUIESCENT = 1
PROFILE_STATUS.DOCK_ARRIVING = 2
PROFILE_STATUS.DOCK_DEPARTING = 3
PROFILE_STATUS.DOCK_EJECTIRP_COMPLETED = 4


MEMORY_CACHING_TYPE = v_enum()
MEMORY_CACHING_TYPE.MmNonCached = 0
MEMORY_CACHING_TYPE.MmCached = 1
MEMORY_CACHING_TYPE.MmWriteCombined = 2
MEMORY_CACHING_TYPE.MmHardwareCoherentCached = 3
MEMORY_CACHING_TYPE.MmNonCachedUnordered = 4
MEMORY_CACHING_TYPE.MmUSWCCached = 5
MEMORY_CACHING_TYPE.MmMaximumCacheType = 6


class KEXECUTE_OPTIONS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExecuteDisable = v_uint8()


class PCI_PMC(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint8()
        self.Support = PM_SUPPORT()


class _unnamed_17257(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FsInformationClass = v_uint32()


class SEGMENT_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseAddress = v_ptr32()
        self.TotalNumberOfPtes = v_uint32()
        self.SizeOfSegment = LARGE_INTEGER()
        self.NonExtendedPtes = v_uint32()
        self.ImageCommitment = v_uint32()
        self.ControlArea = v_ptr32()
        self.Subsection = v_ptr32()
        self.LargeControlArea = v_ptr32()
        self.MmSectionFlags = v_ptr32()
        self.MmSubSectionFlags = v_ptr32()
        self._pad0030 = v_bytes(size=4)


class DUAL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Map = v_ptr32()
        self.SmallDir = v_ptr32()
        self.Guard = v_uint32()
        self.FreeDisplay = vstruct.VArray([ FREE_DISPLAY() for i in range(24) ])
        self.FreeSummary = v_uint32()
        self.FreeBins = LIST_ENTRY()


class SID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint8()
        self.SubAuthorityCount = v_uint8()
        self.IdentifierAuthority = SID_IDENTIFIER_AUTHORITY()
        self.SubAuthority = vstruct.VArray([ v_uint32() for i in range(1) ])


class MMPTE_HARDWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class PCI_FUNCTION_RESOURCES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Limit = vstruct.VArray([ IO_RESOURCE_DESCRIPTOR() for i in range(7) ])
        self.Current = vstruct.VArray([ CM_PARTIAL_RESOURCE_DESCRIPTOR() for i in range(7) ])


class DBGKD_SET_SPECIAL_CALL64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SpecialCall = v_uint64()


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


class DBGKD_GET_INTERNAL_BREAKPOINT32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakpointAddress = v_uint32()
        self.Flags = v_uint32()
        self.Calls = v_uint32()
        self.MaxCallsPerPeriod = v_uint32()
        self.MinInstructions = v_uint32()
        self.MaxInstructions = v_uint32()
        self.TotalInstructions = v_uint32()


class _unnamed_14551(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AsynchronousParameters = _unnamed_16030()


class DBGKD_MANIPULATE_STATE32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ApiNumber = v_uint32()
        self.ProcessorLevel = v_uint16()
        self.Processor = v_uint16()
        self.ReturnStatus = v_uint32()
        self.u = _unnamed_13310()


class PROCESSOR_POWER_POLICY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint32()
        self.DynamicThrottle = v_uint8()
        self.Spare = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.DisableCStates = v_uint32()
        self.PolicyCount = v_uint32()
        self.Policy = vstruct.VArray([ PROCESSOR_POWER_POLICY_INFO() for i in range(3) ])


class PERFINFO_GROUPMASK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Masks = vstruct.VArray([ v_uint32() for i in range(8) ])


class HARDWARE_PTE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class HANDLE_TABLE_ENTRY_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AuditMask = v_uint32()


class DBGKD_WRITE_MEMORY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TargetBaseAddress = v_uint32()
        self.TransferCount = v_uint32()
        self.ActualBytesWritten = v_uint32()


class _unnamed_12848(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReferenceCount = v_uint16()
        self.ShortFlags = v_uint16()


class PCI_INTERFACE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_ptr32()
        self.MinSize = v_uint16()
        self.MinVersion = v_uint16()
        self.MaxVersion = v_uint16()
        self.Flags = v_uint16()
        self.ReferenceCount = v_uint32()
        self.Signature = v_uint32()
        self.Constructor = v_ptr32()
        self.Initializer = v_ptr32()


class _unnamed_17493(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.DataInfoOffset = v_uint16()


class MMWSLENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class _unnamed_17225(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.CompletionFilter = v_uint32()


class _unnamed_17220(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileName = v_ptr32()
        self.FileInformationClass = v_uint32()
        self.FileIndex = v_uint32()


class _unnamed_15834(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint32()


class CM_PARTIAL_RESOURCE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Revision = v_uint16()
        self.Count = v_uint32()
        self.PartialDescriptors = vstruct.VArray([ CM_PARTIAL_RESOURCE_DESCRIPTOR() for i in range(1) ])


class _unnamed_17797(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClassGuid = GUID()
        self.SymbolicLinkName = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0014 = v_bytes(size=2)


class DBGKD_RESTORE_BREAKPOINT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakPointHandle = v_uint32()


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


class RTL_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint64()
        self.End = v_uint64()
        self.UserData = v_ptr32()
        self.Owner = v_ptr32()
        self.Attributes = v_uint8()
        self.Flags = v_uint8()
        self._pad0020 = v_bytes(size=6)


class HEAP_FREE_ENTRY_EXTRA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TagIndex = v_uint16()
        self.FreeBackTraceIndex = v_uint16()


class EXCEPTION_RECORD64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_uint64()
        self.ExceptionAddress = v_uint64()
        self.NumberParameters = v_uint32()
        self.unusedAlignment = v_uint32()
        self.ExceptionInformation = vstruct.VArray([ v_uint64() for i in range(15) ])


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
        self.IdleCount = v_uint32()
        self.ConservationIdleTime = v_uint32()
        self.PerformanceIdleTime = v_uint32()
        self.DeviceObject = v_ptr32()
        self.IdleList = LIST_ENTRY()
        self.DeviceType = v_uint8()
        self._pad001c = v_bytes(size=3)
        self.State = v_uint32()
        self.NotifySourceList = LIST_ENTRY()
        self.NotifyTargetList = LIST_ENTRY()
        self.PowerChannelSummary = POWER_CHANNEL_SUMMARY()
        self.Volume = LIST_ENTRY()


class MMPTE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class HEAP_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()
        self.TagIndex = v_uint16()
        self.CreatorBackTraceIndex = v_uint16()
        self.TagName = vstruct.VArray([ v_uint16() for i in range(24) ])


class _unnamed_11694(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FnArea = FNSAVE_FORMAT()
        self._pad0208 = v_bytes(size=412)


class VI_POOL_ENTRY_INUSE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_ptr32()
        self.CallingAddress = v_ptr32()
        self.NumberOfBytes = v_uint32()
        self.Tag = v_uint32()


class HEAP_LOOKASIDE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = SLIST_HEADER()
        self.Depth = v_uint16()
        self.MaximumDepth = v_uint16()
        self.TotalAllocates = v_uint32()
        self.AllocateMisses = v_uint32()
        self.TotalFrees = v_uint32()
        self.FreeMisses = v_uint32()
        self.LastTotalAllocates = v_uint32()
        self.LastAllocateMisses = v_uint32()
        self.Counters = vstruct.VArray([ v_uint32() for i in range(2) ])
        self._pad0030 = v_bytes(size=4)


class MMPTE_TRANSITION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class RTL_ACTIVATION_CONTEXT_STACK_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Previous = v_ptr32()
        self.ActivationContext = v_ptr32()
        self.Flags = v_uint32()


class OBJECT_HANDLE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleAttributes = v_uint32()
        self.GrantedAccess = v_uint32()


class KTIMER_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = LIST_ENTRY()
        self.Time = ULARGE_INTEGER()


class _unnamed_17138(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.FileAttributes = v_uint16()
        self.ShareAccess = v_uint16()
        self.EaLength = v_uint32()


class _unnamed_13514(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FreeListsInUseUlong = vstruct.VArray([ v_uint32() for i in range(4) ])


class _unnamed_13515(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FreeListsInUseTerminate = v_uint16()


class _unnamed_16030(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UserApcRoutine = v_ptr32()
        self.UserApcContext = v_ptr32()


class _unnamed_12742(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Long = v_uint32()


class OWNER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwnerThread = v_uint32()
        self.OwnerCount = v_uint32()


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


class ARBITER_ALLOCATION_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint64()
        self.End = v_uint64()
        self.CurrentMinimum = v_uint64()
        self.CurrentMaximum = v_uint64()
        self.Entry = v_ptr32()
        self.CurrentAlternative = v_ptr32()
        self.AlternativeCount = v_uint32()
        self.Alternatives = v_ptr32()
        self.Flags = v_uint16()
        self.RangeAttributes = v_uint8()
        self.RangeAvailableAttributes = v_uint8()
        self.WorkSpace = v_uint32()


class DBGKD_SET_INTERNAL_BREAKPOINT64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakpointAddress = v_uint64()
        self.Flags = v_uint32()
        self._pad0010 = v_bytes(size=4)


class _unnamed_12948(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFlags = v_uint32()


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
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(2) ])


class PI_BUS_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.NumberCSNs = v_uint8()
        self._pad0008 = v_bytes(size=3)
        self.ReadDataPort = v_ptr32()
        self.DataPortMapped = v_uint8()
        self._pad0010 = v_bytes(size=3)
        self.AddressPort = v_ptr32()
        self.AddrPortMapped = v_uint8()
        self._pad0018 = v_bytes(size=3)
        self.CommandPort = v_ptr32()
        self.CmdPortMapped = v_uint8()
        self._pad0020 = v_bytes(size=3)
        self.NextSlotNumber = v_uint32()
        self.DeviceList = SINGLE_LIST_ENTRY()
        self.CardList = SINGLE_LIST_ENTRY()
        self.PhysicalBusDevice = v_ptr32()
        self.FunctionalBusDevice = v_ptr32()
        self.AttachedDevice = v_ptr32()
        self.BusNumber = v_uint32()
        self.SystemPowerState = v_uint32()
        self.DevicePowerState = v_uint32()


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


class _unnamed_17749(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ArbitrationList = v_ptr32()


class IO_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Option = v_uint8()
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Spare1 = v_uint8()
        self.Flags = v_uint16()
        self.Spare2 = v_uint16()
        self.u = _unnamed_15817()


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
        self.Privileges = _unnamed_15445()
        self.AuditPrivileges = v_uint8()
        self._pad0064 = v_bytes(size=3)
        self.ObjectName = UNICODE_STRING()
        self.ObjectTypeName = UNICODE_STRING()


class DBGKD_SWITCH_PARTITION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Partition = v_uint32()


class FILE_STANDARD_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocationSize = LARGE_INTEGER()
        self.EndOfFile = LARGE_INTEGER()
        self.NumberOfLinks = v_uint32()
        self.DeletePending = v_uint8()
        self.Directory = v_uint8()
        self._pad0018 = v_bytes(size=2)


class AMD64_DBGKD_CONTROL_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TraceFlag = v_uint32()
        self.Dr7 = v_uint64()
        self.CurrentSymbolStart = v_uint64()
        self.CurrentSymbolEnd = v_uint64()


class _unnamed_14838(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CellData = CELL_DATA()


class POOL_BLOCK_HEAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = POOL_HEADER()
        self.List = LIST_ENTRY()


class DBGKD_SET_SPECIAL_CALL32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SpecialCall = v_uint32()


class SYSTEM_POWER_LEVEL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Enable = v_uint8()
        self.Spare = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.BatteryLevel = v_uint32()
        self.PowerPolicy = POWER_ACTION_POLICY()
        self.MinSystemState = v_uint32()


class DBGKD_LOAD_SYMBOLS32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PathNameLength = v_uint32()
        self.BaseOfDll = v_uint32()
        self.ProcessId = v_uint32()
        self.CheckSum = v_uint32()
        self.SizeOfImage = v_uint32()
        self.UnloadSymbols = v_uint8()
        self._pad0018 = v_bytes(size=3)


class DBGKM_EXCEPTION32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionRecord = EXCEPTION_RECORD32()
        self.FirstChance = v_uint32()


class PAGEFAULT_HISTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CurrentIndex = v_uint32()
        self.MaxIndex = v_uint32()
        self.SpinLock = v_uint32()
        self.Reserved = v_ptr32()
        self.WatchInfo = vstruct.VArray([ PROCESS_WS_WATCH_INFORMATION() for i in range(1) ])


class _unnamed_16105(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PhysicalAddress = v_uint32()


class HMAP_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BlockAddress = v_uint32()
        self.BinAddress = v_uint32()
        self.CmView = v_ptr32()
        self.MemAlloc = v_uint32()


class WNODE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BufferSize = v_uint32()
        self.ProviderId = v_uint32()
        self.HistoricalContext = v_uint64()
        self.CountLost = v_uint32()
        self._pad0018 = v_bytes(size=4)
        self.Guid = GUID()
        self.ClientContext = v_uint32()
        self.Flags = v_uint32()


class PROCESS_WS_WATCH_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FaultingPc = v_ptr32()
        self.FaultingVa = v_ptr32()


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


class CM_INDEX_HINT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.HashKey = vstruct.VArray([ v_uint32() for i in range(1) ])


class SEP_AUDIT_POLICY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PolicyElements = SEP_AUDIT_POLICY_CATEGORIES()


class MMPTE_SOFTWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class IO_TIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.TimerFlag = v_uint16()
        self.TimerList = LIST_ENTRY()
        self.TimerRoutine = v_ptr32()
        self.Context = v_ptr32()
        self.DeviceObject = v_ptr32()


class _unnamed_15925(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint32()
        self.Vector = v_uint32()
        self.Affinity = v_uint32()


class MM_SESSION_SPACE_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Initialized = v_uint32()


class _unnamed_15922(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = LARGE_INTEGER()
        self.Length = v_uint32()


class PO_MEMORY_RANGE_ARRAY_LINK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.NextTable = v_uint32()
        self.CheckSum = v_uint32()
        self.EntryCount = v_uint32()


class _unnamed_17260(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.FsControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


class _unnamed_17618(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceNumber = v_uint32()


class _unnamed_17348(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoResourceRequirementList = v_ptr32()


class _unnamed_17265(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_ptr32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class _unnamed_17345(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Capabilities = v_ptr32()


class EVENT_COUNTER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = SINGLE_LIST_ENTRY()
        self.RefCount = v_uint32()
        self.Event = KEVENT()


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


class _unnamed_17615(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Mbr = _unnamed_17839()
        self._pad0010 = v_bytes(size=8)


class EX_WORK_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WorkerQueue = KQUEUE()
        self.DynamicThreadCount = v_uint32()
        self.WorkItemsProcessed = v_uint32()
        self.WorkItemsProcessedLastPass = v_uint32()
        self.QueueDepthLastPass = v_uint32()
        self.Info = EX_QUEUE_WORKER_INFO()


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


class VACB_LEVEL_REFERENCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Reference = v_uint32()
        self.SpecialReference = v_uint32()


class HEAP_ENTRY_EXTRA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatorBackTraceIndex = v_uint16()
        self.TagIndex = v_uint16()
        self.Settable = v_uint32()


class POP_DEVICE_SYS_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IrpMinor = v_uint8()
        self._pad0004 = v_bytes(size=3)
        self.SystemState = v_uint32()
        self.Event = KEVENT()
        self.SpinLock = v_uint32()
        self.Thread = v_ptr32()
        self.GetNewDeviceList = v_uint8()
        self._pad0024 = v_bytes(size=3)
        self.Order = PO_DEVICE_NOTIFY_ORDER()
        self.Status = v_uint32()
        self.FailedDevice = v_ptr32()
        self.Waking = v_uint8()
        self.Cancelled = v_uint8()
        self.IgnoreErrors = v_uint8()
        self.IgnoreNotImplemented = v_uint8()
        self.WaitAny = v_uint8()
        self.WaitAll = v_uint8()
        self._pad027c = v_bytes(size=2)
        self.PresentIrpQueue = LIST_ENTRY()
        self.Head = POP_DEVICE_POWER_IRP()
        self.PowerIrpState = vstruct.VArray([ POP_DEVICE_POWER_IRP() for i in range(20) ])


class SECURITY_TOKEN_AUDIT_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.GrantMask = v_uint32()
        self.DenyMask = v_uint32()


class VI_DEADLOCK_RESOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()
        self.NodeCount = v_uint32()
        self.ResourceAddress = v_ptr32()
        self.ThreadOwner = v_ptr32()
        self.ResourceList = LIST_ENTRY()
        self.HashChainList = LIST_ENTRY()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(8) ])
        self.LastAcquireTrace = vstruct.VArray([ v_ptr32() for i in range(8) ])
        self.LastReleaseTrace = vstruct.VArray([ v_ptr32() for i in range(8) ])


class HEAP_PSEUDO_TAG_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Allocs = v_uint32()
        self.Frees = v_uint32()
        self.Size = v_uint32()


class CM_KEY_REFERENCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.KeyCell = v_uint32()
        self.KeyHive = v_ptr32()


class MMSECTION_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BeingDeleted = v_uint32()


class DBGKD_GET_INTERNAL_BREAKPOINT64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakpointAddress = v_uint64()
        self.Flags = v_uint32()
        self.Calls = v_uint32()
        self.MaxCallsPerPeriod = v_uint32()
        self.MinInstructions = v_uint32()
        self.MaxInstructions = v_uint32()
        self.TotalInstructions = v_uint32()


class _unnamed_17293(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.StartSid = v_ptr32()
        self.SidList = v_ptr32()
        self.SidListLength = v_uint32()


class PROCESSOR_POWER_POLICY_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TimeCheck = v_uint32()
        self.DemoteLimit = v_uint32()
        self.PromoteLimit = v_uint32()
        self.DemotePercent = v_uint8()
        self.PromotePercent = v_uint8()
        self.Spare = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.AllowDemotion = v_uint32()


class _unnamed_15929(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Channel = v_uint32()
        self.Port = v_uint32()
        self.Reserved1 = v_uint32()


class POP_POWER_ACTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Updates = v_uint8()
        self.State = v_uint8()
        self.Shutdown = v_uint8()
        self._pad0004 = v_bytes(size=1)
        self.Action = v_uint32()
        self.LightestState = v_uint32()
        self.Flags = v_uint32()
        self.Status = v_uint32()
        self.IrpMinor = v_uint8()
        self._pad0018 = v_bytes(size=3)
        self.SystemState = v_uint32()
        self.NextSystemState = v_uint32()
        self.ShutdownBugCode = v_ptr32()
        self.DevState = v_ptr32()
        self.HiberContext = v_ptr32()
        self.LastWakeState = v_uint32()
        self.WakeTime = v_uint64()
        self.SleepTime = v_uint64()


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
        self.KernelStackReference = v_uint32()
        self._pad0258 = v_bytes(size=4)


class PO_NOTIFY_ORDER_LEVEL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LevelReady = KEVENT()
        self.DeviceCount = v_uint32()
        self.ActiveCount = v_uint32()
        self.WaitSleep = LIST_ENTRY()
        self.ReadySleep = LIST_ENTRY()
        self.Pending = LIST_ENTRY()
        self.Complete = LIST_ENTRY()
        self.ReadyS0 = LIST_ENTRY()
        self.WaitS0 = LIST_ENTRY()


class RTL_BITMAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SizeOfBitMap = v_uint32()
        self.Buffer = v_ptr32()


class LARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class IA64_DBGKD_CONTROL_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Continue = v_uint32()
        self.CurrentSymbolStart = v_uint64()
        self.CurrentSymbolEnd = v_uint64()


class _unnamed_17465(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Priority = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class NPAGED_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.L = GENERAL_LOOKASIDE()
        self.Lock__ObsoleteButDoNotDelete = v_uint32()
        self._pad00c0 = v_bytes(size=60)


class _unnamed_17460(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.MinBusNumber = v_uint32()
        self.MaxBusNumber = v_uint32()
        self.Reserved = v_uint32()


class GUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data1 = v_uint32()
        self.Data2 = v_uint16()
        self.Data3 = v_uint16()
        self.Data4 = vstruct.VArray([ v_uint8() for i in range(8) ])


class BITMAP_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Links = LIST_ENTRY()
        self.BasePage = v_uint64()
        self.FirstDirtyPage = v_uint32()
        self.LastDirtyPage = v_uint32()
        self.DirtyPages = v_uint32()
        self.Bitmap = v_ptr32()


class KLOCK_QUEUE_HANDLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LockQueue = KSPIN_LOCK_QUEUE()
        self.OldIrql = v_uint8()
        self._pad000c = v_bytes(size=3)


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


class WMI_BUFFER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Free = v_uint32()


class PP_LOOKASIDE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.P = v_ptr32()
        self.L = v_ptr32()


class SEP_LOGON_SESSION_REFERENCES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.LogonId = LUID()
        self.ReferenceCount = v_uint32()
        self.Flags = v_uint32()
        self.pDeviceMap = v_ptr32()


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


class MMFREE_POOL_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.List = LIST_ENTRY()
        self.Size = v_uint32()
        self.Signature = v_uint32()
        self.Owner = v_ptr32()


class PRIVATE_CACHE_MAP_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DontUse = v_uint32()


class FS_FILTER_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AcquireForModifiedPageWriter = _unnamed_17952()
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
        self.u = _unnamed_13514()
        self.u2 = _unnamed_13515()
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


class HANDLE_TRACE_DEBUG_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.RefCount = v_uint32()
        self.TableSize = v_uint32()
        self.BitMaskFlags = v_uint32()
        self.CloseCompactionLock = FAST_MUTEX()
        self.CurrentStackIndex = v_uint32()
        self.TraceDb = vstruct.VArray([ HANDLE_TRACE_DB_ENTRY() for i in range(1) ])


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


class _unnamed_15817(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Port = _unnamed_17449()


class PHYSICAL_MEMORY_RUN(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BasePage = v_uint32()
        self.PageCount = v_uint32()


class CM_KEY_BODY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()
        self.KeyControlBlock = v_ptr32()
        self.NotifyBlock = v_ptr32()
        self.ProcessID = v_ptr32()
        self.Callers = v_uint32()
        self.CallerAddress = vstruct.VArray([ v_ptr32() for i in range(10) ])
        self.KeyBodyList = LIST_ENTRY()


class KMUTANT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.MutantListEntry = LIST_ENTRY()
        self.OwnerThread = v_ptr32()
        self.Abandoned = v_uint8()
        self.ApcDisable = v_uint8()
        self._pad0020 = v_bytes(size=2)


class FX_SAVE_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.U = _unnamed_11694()
        self.NpxSavedCpu = v_uint32()
        self.Cr0NpxState = v_uint32()


class POWER_SEQUENCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SequenceD1 = v_uint32()
        self.SequenceD2 = v_uint32()
        self.SequenceD3 = v_uint32()


class _unnamed_12907(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFlags = v_uint32()


class KTIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.DueTime = ULARGE_INTEGER()
        self.TimerListEntry = LIST_ENTRY()
        self.Dpc = v_ptr32()
        self.Period = v_uint32()


class MM_PAGED_POOL_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PagedPoolAllocationMap = v_ptr32()
        self.EndOfPagedPoolBitmap = v_ptr32()
        self.FirstPteForPagedPool = v_ptr32()
        self.LastPteForPagedPool = v_ptr32()
        self.NextPdeForPagedPoolExpansion = v_ptr32()
        self.PagedPoolHint = v_uint32()
        self.PagedPoolCommit = v_uint32()
        self.AllocatedPagedPool = v_uint32()


class HIVE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name = v_ptr32()
        self.BaseName = v_ptr32()
        self.CmHive = v_ptr32()
        self.HHiveFlags = v_uint32()
        self.CmHiveFlags = v_uint32()
        self.CmHive2 = v_ptr32()
        self.ThreadFinished = v_uint8()
        self.ThreadStarted = v_uint8()
        self.Allocate = v_uint8()
        self._pad001c = v_bytes(size=1)


class CM_PARTIAL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.ShareDisposition = v_uint8()
        self.Flags = v_uint16()
        self.u = _unnamed_15282()


class RTLP_RANGE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint64()
        self.End = v_uint64()
        self.Allocated = _unnamed_15784()
        self.Attributes = v_uint8()
        self.PublicFlags = v_uint8()
        self.PrivateFlags = v_uint16()
        self.ListEntry = LIST_ENTRY()
        self._pad0028 = v_bytes(size=4)


class _unnamed_17763(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReserveDevice = v_ptr32()


class _unnamed_17228(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()


class OBJECT_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.RootDirectory = v_ptr32()
        self.ObjectName = v_ptr32()
        self.Attributes = v_uint32()
        self.SecurityDescriptor = v_ptr32()
        self.SecurityQualityOfService = v_ptr32()


class CM_VIEW_OF_FILE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LRUViewList = LIST_ENTRY()
        self.PinViewList = LIST_ENTRY()
        self.FileOffset = v_uint32()
        self.Size = v_uint32()
        self.ViewAddress = v_ptr32()
        self.Bcb = v_ptr32()
        self.UseCount = v_uint32()


class CM_FULL_RESOURCE_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.PartialResourceList = CM_PARTIAL_RESOURCE_LIST()


class _unnamed_17166(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


class DBGKD_GET_VERSION64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.ProtocolVersion = v_uint8()
        self.KdSecondaryVersion = v_uint8()
        self.Flags = v_uint16()
        self.MachineType = v_uint16()
        self.MaxPacketType = v_uint8()
        self.MaxStateChange = v_uint8()
        self.MaxManipulate = v_uint8()
        self.Simulation = v_uint8()
        self.Unused = vstruct.VArray([ v_uint16() for i in range(1) ])
        self.KernBase = v_uint64()
        self.PsLoadedModuleList = v_uint64()
        self.DebuggerDataList = v_uint64()


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


class CM_KEY_CONTROL_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.RefCount = v_uint32()
        self.ExtFlags = v_uint32()
        self.KeyHash = CM_KEY_HASH()
        self.ParentKcb = v_ptr32()
        self.NameBlock = v_ptr32()
        self.CachedSecurity = v_ptr32()
        self.ValueCache = CACHED_CHILD_LIST()
        self.IndexHint = v_ptr32()
        self.KeyBodyListHead = LIST_ENTRY()
        self.KeyBodyArray = vstruct.VArray([ v_ptr32() for i in range(4) ])
        self.DelayCloseEntry = v_ptr32()
        self._pad0050 = v_bytes(size=4)
        self.KcbLastWriteTime = LARGE_INTEGER()
        self.KcbMaxNameLen = v_uint16()
        self.KcbMaxValueNameLen = v_uint16()
        self.KcbMaxValueDataLen = v_uint32()
        self.KcbUserFlags = v_uint32()
        self._pad0068 = v_bytes(size=4)


class MMVAD_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CommitCharge = v_uint32()


class MMWSL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FirstFree = v_uint32()
        self.FirstDynamic = v_uint32()
        self.LastEntry = v_uint32()
        self.NextSlot = v_uint32()
        self.Wsle = v_ptr32()
        self.LastInitializedWsle = v_uint32()
        self.NonDirectCount = v_uint32()
        self.HashTable = v_ptr32()
        self.HashTableSize = v_uint32()
        self.NumberOfCommittedPageTables = v_uint32()
        self.HashTableStart = v_ptr32()
        self.HighestPermittedHashAddress = v_ptr32()
        self.NumberOfImageWaiters = v_uint32()
        self.VadBitMapHint = v_uint32()
        self.UsedPageTableEntries = vstruct.VArray([ v_uint16() for i in range(768) ])
        self.CommittedPageTables = vstruct.VArray([ v_uint32() for i in range(24) ])


class POP_THERMAL_ZONE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Link = LIST_ENTRY()
        self.State = v_uint8()
        self.Flags = v_uint8()
        self.Mode = v_uint8()
        self.PendingMode = v_uint8()
        self.ActivePoint = v_uint8()
        self.PendingActivePoint = v_uint8()
        self._pad0010 = v_bytes(size=2)
        self.Throttle = v_uint32()
        self._pad0018 = v_bytes(size=4)
        self.LastTime = v_uint64()
        self.SampleRate = v_uint32()
        self.LastTemp = v_uint32()
        self.PassiveTimer = KTIMER()
        self.PassiveDpc = KDPC()
        self.OverThrottled = POP_ACTION_TRIGGER()
        self.Irp = v_ptr32()
        self.Info = THERMAL_INFORMATION()
        self._pad00d0 = v_bytes(size=4)


class CALL_HASH_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.CallersAddress = v_ptr32()
        self.CallersCaller = v_ptr32()
        self.CallCount = v_uint32()


class SUPPORTED_RANGES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint16()
        self.Sorted = v_uint8()
        self.Reserved = v_uint8()
        self.NoIO = v_uint32()
        self.IO = SUPPORTED_RANGE()
        self.NoMemory = v_uint32()
        self._pad0030 = v_bytes(size=4)
        self.Memory = SUPPORTED_RANGE()
        self.NoPrefetchMemory = v_uint32()
        self._pad0058 = v_bytes(size=4)
        self.PrefetchMemory = SUPPORTED_RANGE()
        self.NoDma = v_uint32()
        self._pad0080 = v_bytes(size=4)
        self.Dma = SUPPORTED_RANGE()


class WORK_QUEUE_ITEM(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.List = LIST_ENTRY()
        self.WorkerRoutine = v_ptr32()
        self.Parameter = v_ptr32()


class EPROCESS_QUOTA_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Usage = v_uint32()
        self.Limit = v_uint32()
        self.Peak = v_uint32()
        self.Return = v_uint32()


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


class POWER_ACTION_POLICY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Action = v_uint32()
        self.Flags = v_uint32()
        self.EventCode = v_uint32()


class RTL_CRITICAL_SECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DebugInfo = v_ptr32()
        self.LockCount = v_uint32()
        self.RecursionCount = v_uint32()
        self.OwningThread = v_ptr32()
        self.LockSemaphore = v_ptr32()
        self.SpinCount = v_uint32()


class DBGKM_EXCEPTION64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionRecord = EXCEPTION_RECORD64()
        self.FirstChance = v_uint32()
        self._pad00a0 = v_bytes(size=4)


class _unnamed_17306(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()


class KSYSTEM_TIME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.High1Time = v_uint32()
        self.High2Time = v_uint32()


class _unnamed_17308(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InterfaceType = v_ptr32()
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Interface = v_ptr32()
        self.InterfaceSpecificData = v_ptr32()


class SEGMENT_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TotalNumberOfPtes4132 = v_uint32()


class ACL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AclRevision = v_uint8()
        self.Sbz1 = v_uint8()
        self.AclSize = v_uint16()
        self.AceCount = v_uint16()
        self.Sbz2 = v_uint16()


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


class WMI_LOGGER_MODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SequentialFile = v_uint32()


class KQUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.EntryListHead = LIST_ENTRY()
        self.CurrentCount = v_uint32()
        self.MaximumCount = v_uint32()
        self.ThreadListHead = LIST_ENTRY()


class POOL_TRACKER_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Key = v_uint32()
        self.NonPagedAllocs = v_uint32()
        self.NonPagedFrees = v_uint32()
        self.NonPagedBytes = v_uint32()
        self.PagedAllocs = v_uint32()
        self.PagedFrees = v_uint32()
        self.PagedBytes = v_uint32()


class SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlArea = v_ptr32()
        self.TotalNumberOfPtes = v_uint32()
        self.NonExtendedPtes = v_uint32()
        self.Spare0 = v_uint32()
        self.SizeOfSegment = v_uint64()
        self.SegmentPteTemplate = MMPTE()
        self.NumberOfCommittedPages = v_uint32()
        self.ExtendInfo = v_ptr32()
        self.SegmentFlags = SEGMENT_FLAGS()
        self.BasedAddress = v_ptr32()
        self.u1 = _unnamed_14191()
        self.u2 = _unnamed_14192()
        self.PrototypePte = v_ptr32()
        self.ThePtes = vstruct.VArray([ MMPTE() for i in range(1) ])
        self._pad0040 = v_bytes(size=4)


class LUID_AND_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Luid = LUID()
        self.Attributes = v_uint32()


class iobuf(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ptr = v_ptr32()
        self.cnt = v_uint32()
        self.base = v_ptr32()
        self.flag = v_uint32()
        self.file = v_uint32()
        self.charbuf = v_uint32()
        self.bufsiz = v_uint32()
        self.tmpfname = v_ptr32()


class MMMOD_WRITER_MDL_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Links = LIST_ENTRY()
        self.WriteOffset = LARGE_INTEGER()
        self.u = _unnamed_13029()
        self.Irp = v_ptr32()
        self.LastPageToWrite = v_uint32()
        self.PagingListHead = v_ptr32()
        self.CurrentList = v_ptr32()
        self.PagingFile = v_ptr32()
        self.File = v_ptr32()
        self.ControlArea = v_ptr32()
        self.FileResource = v_ptr32()
        self.IssueTime = LARGE_INTEGER()
        self.Mdl = MDL()
        self.Page = vstruct.VArray([ v_uint32() for i in range(1) ])


class _unnamed_17392(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemContext = v_uint32()
        self.Type = v_uint32()
        self.State = POWER_STATE()
        self.ShutdownType = v_uint32()


class CACHED_CHILD_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.ValueList = v_uint32()


class _unnamed_17397(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatedResources = v_ptr32()
        self.AllocatedResourcesTranslated = v_ptr32()


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


class _unnamed_15746(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Spare = vstruct.VArray([ v_uint8() for i in range(4) ])


class ADAPTER_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class _unnamed_12875(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFlags = v_uint32()


class _unnamed_17239(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.EaList = v_ptr32()
        self.EaListLength = v_uint32()
        self.EaIndex = v_uint32()


class _unnamed_11341(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_12873(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Balance = v_uint32()


class _unnamed_12878(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFlags2 = v_uint32()


class DBGKD_GET_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Unused = v_uint32()


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


class _unnamed_15693(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.bits = _unnamed_17618()


class GENERIC_MAPPING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.GenericRead = v_uint32()
        self.GenericWrite = v_uint32()
        self.GenericExecute = v_uint32()
        self.GenericAll = v_uint32()


class DEVICE_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Sibling = v_ptr32()
        self.Child = v_ptr32()
        self.Parent = v_ptr32()
        self.LastChild = v_ptr32()
        self.Level = v_uint32()
        self.Notify = v_ptr32()
        self.State = v_uint32()
        self.PreviousState = v_uint32()
        self.StateHistory = vstruct.VArray([ PNP_DEVNODE_STATE() for i in range(20) ])
        self.StateHistoryEntry = v_uint32()
        self.CompletionStatus = v_uint32()
        self.PendingIrp = v_ptr32()
        self.Flags = v_uint32()
        self.UserFlags = v_uint32()
        self.Problem = v_uint32()
        self.PhysicalDeviceObject = v_ptr32()
        self.ResourceList = v_ptr32()
        self.ResourceListTranslated = v_ptr32()
        self.InstancePath = UNICODE_STRING()
        self.ServiceName = UNICODE_STRING()
        self.DuplicatePDO = v_ptr32()
        self.ResourceRequirements = v_ptr32()
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.ChildInterfaceType = v_uint32()
        self.ChildBusNumber = v_uint32()
        self.ChildBusTypeIndex = v_uint16()
        self.RemovalPolicy = v_uint8()
        self.HardwareRemovalPolicy = v_uint8()
        self.TargetDeviceNotify = LIST_ENTRY()
        self.DeviceArbiterList = LIST_ENTRY()
        self.DeviceTranslatorList = LIST_ENTRY()
        self.NoTranslatorMask = v_uint16()
        self.QueryTranslatorMask = v_uint16()
        self.NoArbiterMask = v_uint16()
        self.QueryArbiterMask = v_uint16()
        self.OverUsed1 = _unnamed_14491()
        self.OverUsed2 = _unnamed_14492()
        self.BootResources = v_ptr32()
        self.CapabilityFlags = v_uint32()
        self.DockInfo = _unnamed_14493()
        self.DisableableDepends = v_uint32()
        self.PendedSetInterfaceState = LIST_ENTRY()
        self.LegacyBusListEntry = LIST_ENTRY()
        self.DriverUnloadRetryCount = v_uint32()
        self.PreviousParent = v_ptr32()
        self.DeletedChildren = v_uint32()


class IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.MdlAddress = v_ptr32()
        self.Flags = v_uint32()
        self.AssociatedIrp = _unnamed_14548()
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
        self.Overlay = _unnamed_14551()
        self.CancelRoutine = v_ptr32()
        self.UserBuffer = v_ptr32()
        self.Tail = _unnamed_14554()


class _unnamed_14669(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LongFlags = v_uint32()


class RTL_ATOM_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.CriticalSection = RTL_CRITICAL_SECTION()
        self.RtlHandleTable = RTL_HANDLE_TABLE()
        self.NumberOfBuckets = v_uint32()
        self.Buckets = vstruct.VArray([ v_ptr32() for i in range(1) ])


class OBJECT_HEADER_HANDLE_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HandleCountDataBase = v_ptr32()
        self._pad0008 = v_bytes(size=4)


class ACTIVATION_CONTEXT_STACK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ActiveFrame = v_ptr32()
        self.FrameListCache = LIST_ENTRY()
        self.Flags = v_uint32()
        self.NextCookieSequenceNumber = v_uint32()
        self.StackId = v_uint32()


class IMAGE_ROM_OPTIONAL_HEADER(vstruct.VStruct):
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
        self.BaseOfBss = v_uint32()
        self.GprMask = v_uint32()
        self.CprMask = vstruct.VArray([ v_uint32() for i in range(4) ])
        self.GpValue = v_uint32()


class HEAP_FREE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.PreviousSize = v_uint16()
        self.SmallTagIndex = v_uint8()
        self.Flags = v_uint8()
        self.UnusedBytes = v_uint8()
        self.SegmentIndex = v_uint8()
        self.FreeList = LIST_ENTRY()


class _unnamed_15914(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.type0 = PCI_HEADER_TYPE_0()


class _unnamed_12231(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self._pad0028 = v_bytes(size=32)


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


class DBGKD_READ_MEMORY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TargetBaseAddress = v_uint64()
        self.TransferCount = v_uint32()
        self.ActualBytesRead = v_uint32()


class PO_MEMORY_IMAGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.Version = v_uint32()
        self.CheckSum = v_uint32()
        self.LengthSelf = v_uint32()
        self.PageSelf = v_uint32()
        self.PageSize = v_uint32()
        self.ImageType = v_uint32()
        self._pad0020 = v_bytes(size=4)
        self.SystemTime = LARGE_INTEGER()
        self.InterruptTime = v_uint64()
        self.FeatureFlags = v_uint32()
        self.HiberFlags = v_uint8()
        self.spare = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.NoHiberPtes = v_uint32()
        self.HiberVa = v_uint32()
        self.HiberPte = LARGE_INTEGER()
        self.NoFreePages = v_uint32()
        self.FreeMapCheck = v_uint32()
        self.WakeCheck = v_uint32()
        self.TotalPages = v_uint32()
        self.FirstTablePage = v_uint32()
        self.LastFilePage = v_uint32()
        self.PerfInfo = PO_HIBER_PERF()


class HHIVE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.GetCellRoutine = v_ptr32()
        self.ReleaseCellRoutine = v_ptr32()
        self.Allocate = v_ptr32()
        self.Free = v_ptr32()
        self.FileSetSize = v_ptr32()
        self.FileWrite = v_ptr32()
        self.FileRead = v_ptr32()
        self.FileFlush = v_ptr32()
        self.BaseBlock = v_ptr32()
        self.DirtyVector = RTL_BITMAP()
        self.DirtyCount = v_uint32()
        self.DirtyAlloc = v_uint32()
        self.BaseBlockAlloc = v_uint32()
        self.Cluster = v_uint32()
        self.Flat = v_uint8()
        self.ReadOnly = v_uint8()
        self.Log = v_uint8()
        self.DirtyFlag = v_uint8()
        self.HiveFlags = v_uint32()
        self.LogSize = v_uint32()
        self.RefreshCount = v_uint32()
        self.StorageTypeCount = v_uint32()
        self.Version = v_uint32()
        self.Storage = vstruct.VArray([ DUAL() for i in range(2) ])


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


class OBJECT_SYMBOLIC_LINK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CreationTime = LARGE_INTEGER()
        self.LinkTarget = UNICODE_STRING()
        self.LinkTargetRemaining = UNICODE_STRING()
        self.LinkTargetObject = v_ptr32()
        self.DosDeviceDriveIndex = v_uint32()


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


class DBGKD_READ_WRITE_IO_EXTENDED64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.AddressSpace = v_uint32()
        self.IoAddress = v_uint64()
        self.DataValue = v_uint32()
        self._pad0020 = v_bytes(size=4)


class IO_STATUS_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Status = v_uint32()
        self.Information = v_uint32()


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


class FILE_GET_QUOTA_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextEntryOffset = v_uint32()
        self.SidLength = v_uint32()
        self.Sid = SID()


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


class POOL_TRACKER_BIG_PAGES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Va = v_ptr32()
        self.Key = v_uint32()
        self.NumberOfPages = v_uint32()
        self.QuotaObject = v_ptr32()


class _unnamed_14492(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextResourceDeviceNode = v_ptr32()


class SID_IDENTIFIER_AUTHORITY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Value = vstruct.VArray([ v_uint8() for i in range(6) ])


class RTL_RANGE_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = LIST_ENTRY()
        self.Flags = v_uint32()
        self.Count = v_uint32()
        self.Stamp = v_uint32()


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
        self.PageDirectoryPte = HARDWARE_PTE()
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


class LARGE_CONTROL_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Segment = v_ptr32()
        self.DereferenceList = LIST_ENTRY()
        self.NumberOfSectionReferences = v_uint32()
        self.NumberOfPfnReferences = v_uint32()
        self.NumberOfMappedViews = v_uint32()
        self.NumberOfSystemCacheViews = v_uint32()
        self.NumberOfUserReferences = v_uint32()
        self.u = _unnamed_12907()
        self.FilePointer = v_ptr32()
        self.WaitingForDeletion = v_ptr32()
        self.ModifiedWriteCount = v_uint16()
        self.FlushInProgressCount = v_uint16()
        self.WritableUserReferences = v_uint32()
        self.QuadwordPad = v_uint32()
        self.StartingFrame = v_uint32()
        self.UserGlobalList = LIST_ENTRY()
        self.SessionId = v_uint32()


class VI_POOL_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PageHeader = VI_POOL_PAGE_HEADER()
        self._pad0010 = v_bytes(size=4)


class POOL_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PreviousSize = v_uint16()
        self.BlockSize = v_uint16()
        self.PoolTag = v_uint32()


class SHARED_CACHE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NodeTypeCode = v_uint16()
        self.NodeByteSize = v_uint16()
        self.OpenCount = v_uint32()
        self.FileSize = LARGE_INTEGER()
        self.BcbList = LIST_ENTRY()
        self.SectionSize = LARGE_INTEGER()
        self.ValidDataLength = LARGE_INTEGER()
        self.ValidDataGoal = LARGE_INTEGER()
        self.InitialVacbs = vstruct.VArray([ v_ptr32() for i in range(4) ])
        self.Vacbs = v_ptr32()
        self.FileObject = v_ptr32()
        self.ActiveVacb = v_ptr32()
        self.NeedToZero = v_ptr32()
        self.ActivePage = v_uint32()
        self.NeedToZeroPage = v_uint32()
        self.ActiveVacbSpinLock = v_uint32()
        self.VacbActiveCount = v_uint32()
        self.DirtyPages = v_uint32()
        self.SharedCacheMapLinks = LIST_ENTRY()
        self.Flags = v_uint32()
        self.Status = v_uint32()
        self.Mbcb = v_ptr32()
        self.Section = v_ptr32()
        self.CreateEvent = v_ptr32()
        self.WaitOnActiveCount = v_ptr32()
        self.PagesToWrite = v_uint32()
        self.BeyondLastFlush = v_uint64()
        self.Callbacks = v_ptr32()
        self.LazyWriteContext = v_ptr32()
        self.PrivateList = LIST_ENTRY()
        self.LogHandle = v_ptr32()
        self.FlushToLsnRoutine = v_ptr32()
        self.DirtyPageThreshold = v_uint32()
        self.LazyWritePassCount = v_uint32()
        self.UninitializeEvent = v_ptr32()
        self.NeedToZeroVacb = v_ptr32()
        self.BcbSpinLock = v_uint32()
        self.Reserved = v_ptr32()
        self.Event = KEVENT()
        self.VacbPushLock = EX_PUSH_LOCK()
        self._pad00d8 = v_bytes(size=4)
        self.PrivateCacheMap = PRIVATE_CACHE_MAP()
        self.WriteBehindWorkQueueEntry = v_ptr32()
        self._pad0138 = v_bytes(size=4)


class TRACE_ENABLE_FLAG_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint16()
        self.Length = v_uint8()
        self.Flag = v_uint8()


class MI_VERIFIER_POOL_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VerifierPoolEntry = v_ptr32()


class ACTIVATION_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class MMBANKED_SECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BasePhysicalPage = v_uint32()
        self.BasedPte = v_ptr32()
        self.BankSize = v_uint32()
        self.BankShift = v_uint32()
        self.BankedRoutine = v_ptr32()
        self.Context = v_ptr32()
        self.CurrentMappedPte = v_ptr32()
        self.BankTemplate = vstruct.VArray([ MMPTE() for i in range(1) ])


class PCI_POWER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CurrentSystemState = v_uint32()
        self.CurrentDeviceState = v_uint32()
        self.SystemWakeLevel = v_uint32()
        self.DeviceWakeLevel = v_uint32()
        self.SystemStateMapping = vstruct.VArray([ DEVICE_POWER_STATE() for i in range(7) ])
        self.WaitWakeIrp = v_ptr32()
        self.SavedCancelRoutine = v_ptr32()
        self.Paging = v_uint32()
        self.Hibernate = v_uint32()
        self.CrashDump = v_uint32()


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


class PNP_DEVICE_EVENT_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.Argument = v_uint32()
        self.CallerEvent = v_ptr32()
        self.Callback = v_ptr32()
        self.Context = v_ptr32()
        self.VetoType = v_ptr32()
        self.VetoName = v_ptr32()
        self.Data = PLUGPLAY_EVENT_BLOCK()


class ARBITER_CONFLICT_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OwningObject = v_ptr32()
        self._pad0008 = v_bytes(size=4)
        self.Start = v_uint64()
        self.End = v_uint64()


class _unnamed_17751(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocatedResources = v_ptr32()


class SID_AND_ATTRIBUTES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Sid = v_ptr32()
        self.Attributes = v_uint32()


class _unnamed_15468(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.List = LIST_ENTRY()


class MMVAD_FLAGS2(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FileOffset = v_uint32()


class TOKEN(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TokenSource = TOKEN_SOURCE()
        self.TokenId = LUID()
        self.AuthenticationId = LUID()
        self.ParentTokenId = LUID()
        self.ExpirationTime = LARGE_INTEGER()
        self.TokenLock = v_ptr32()
        self._pad0038 = v_bytes(size=4)
        self.AuditPolicy = SEP_AUDIT_POLICY()
        self.ModifiedId = LUID()
        self.SessionId = v_uint32()
        self.UserAndGroupCount = v_uint32()
        self.RestrictedSidCount = v_uint32()
        self.PrivilegeCount = v_uint32()
        self.VariableLength = v_uint32()
        self.DynamicCharged = v_uint32()
        self.DynamicAvailable = v_uint32()
        self.DefaultOwnerIndex = v_uint32()
        self.UserAndGroups = v_ptr32()
        self.RestrictedSids = v_ptr32()
        self.PrimaryGroup = v_ptr32()
        self.Privileges = v_ptr32()
        self.DynamicPart = v_ptr32()
        self.DefaultDacl = v_ptr32()
        self.TokenType = v_uint32()
        self.ImpersonationLevel = v_uint32()
        self.TokenFlags = v_uint8()
        self.TokenInUse = v_uint8()
        self._pad008c = v_bytes(size=2)
        self.ProxyData = v_ptr32()
        self.AuditData = v_ptr32()
        self.LogonSession = v_ptr32()
        self.OriginatingLogonSession = LUID()
        self.VariablePart = v_uint32()
        self._pad00a8 = v_bytes(size=4)


class MMCOLOR_TABLES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()
        self.Blink = v_ptr32()
        self.Count = v_uint32()


class DISPATCHER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint8()
        self.Absolute = v_uint8()
        self.Size = v_uint8()
        self.Inserted = v_uint8()
        self.SignalState = v_uint32()
        self.WaitListHead = LIST_ENTRY()


class DBGKD_READ_WRITE_IO64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoAddress = v_uint64()
        self.DataSize = v_uint32()
        self.DataValue = v_uint32()


class _unnamed_16050(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceQueueEntry = KDEVICE_QUEUE_ENTRY()
        self.Thread = v_ptr32()
        self.AuxiliaryBuffer = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.CurrentStackLocation = v_ptr32()
        self.OriginalFileObject = v_ptr32()


class _unnamed_13571(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CriticalSection = RTL_CRITICAL_SECTION()
        self._pad0038 = v_bytes(size=32)


class ASSEMBLY_STORAGE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


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


class SECURITY_CLIENT_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityQos = SECURITY_QUALITY_OF_SERVICE()
        self.ClientToken = v_ptr32()
        self.DirectlyAccessClientToken = v_uint8()
        self.DirectAccessEffectiveOnly = v_uint8()
        self.ServerIsRemote = v_uint8()
        self._pad0014 = v_bytes(size=1)
        self.ClientTokenControl = TOKEN_CONTROL()


class DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Pad = v_uint16()
        self.Limit = v_uint16()
        self.Base = v_uint32()


class DBGKD_MANIPULATE_STATE64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ApiNumber = v_uint32()
        self.ProcessorLevel = v_uint16()
        self.Processor = v_uint16()
        self.ReturnStatus = v_uint32()
        self._pad0010 = v_bytes(size=4)
        self.u = _unnamed_13218()


class LPCP_PORT_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NonPagedPortQueue = v_ptr32()
        self.Semaphore = v_ptr32()
        self.ReceiveHead = LIST_ENTRY()


class DBGKD_LOAD_SYMBOLS64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PathNameLength = v_uint32()
        self._pad0008 = v_bytes(size=4)
        self.BaseOfDll = v_uint64()
        self.ProcessId = v_uint64()
        self.CheckSum = v_uint32()
        self.SizeOfImage = v_uint32()
        self.UnloadSymbols = v_uint8()
        self._pad0028 = v_bytes(size=7)


class CACHE_UNINITIALIZE_EVENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Event = KEVENT()


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


class KGATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class CMHIVE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Hive = HHIVE()
        self.FileHandles = vstruct.VArray([ v_ptr32() for i in range(3) ])
        self.NotifyList = LIST_ENTRY()
        self.HiveList = LIST_ENTRY()
        self.HiveLock = EX_PUSH_LOCK()
        self.ViewLock = v_ptr32()
        self.WriterLock = EX_PUSH_LOCK()
        self.FlusherLock = EX_PUSH_LOCK()
        self.SecurityLock = EX_PUSH_LOCK()
        self.LRUViewListHead = LIST_ENTRY()
        self.PinViewListHead = LIST_ENTRY()
        self.FileObject = v_ptr32()
        self.FileFullPath = UNICODE_STRING()
        self.FileUserName = UNICODE_STRING()
        self.MappedViews = v_uint16()
        self.PinnedViews = v_uint16()
        self.UseCount = v_uint32()
        self.SecurityCount = v_uint32()
        self.SecurityCacheSize = v_uint32()
        self.SecurityHitHint = v_uint32()
        self.SecurityCache = v_ptr32()
        self.SecurityHash = vstruct.VArray([ LIST_ENTRY() for i in range(64) ])
        self.UnloadEvent = v_ptr32()
        self.RootKcb = v_ptr32()
        self.Frozen = v_uint8()
        self._pad0548 = v_bytes(size=3)
        self.UnloadWorkItem = v_ptr32()
        self.GrowOnlyMode = v_uint8()
        self._pad0550 = v_bytes(size=3)
        self.GrowOffset = v_uint32()
        self.KcbConvertListHead = LIST_ENTRY()
        self.KnodeConvertListHead = LIST_ENTRY()
        self.CellRemapArray = v_ptr32()
        self.Flags = v_uint32()
        self.TrustClassEntry = LIST_ENTRY()
        self.FlushCount = v_uint32()
        self.CreatorOwner = v_ptr32()


class POP_SHUTDOWN_BUG_CHECK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Code = v_uint32()
        self.Parameter1 = v_uint32()
        self.Parameter2 = v_uint32()
        self.Parameter3 = v_uint32()
        self.Parameter4 = v_uint32()


class SECTION_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartingVa = v_ptr32()
        self.EndingVa = v_ptr32()
        self.Parent = v_ptr32()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.Segment = v_ptr32()


class LUID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_17270(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OutputBufferLength = v_uint32()
        self.InputBufferLength = v_uint32()
        self.IoControlCode = v_uint32()
        self.Type3InputBuffer = v_ptr32()


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


class PCI_MN_DISPATCH_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DispatchStyle = v_uint32()
        self.DispatchFunction = v_ptr32()


class _unnamed_17275(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.Length = v_uint32()


class PCI_HEADER_TYPE_2(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SocketRegistersBaseAddress = v_uint32()
        self.CapabilitiesPtr = v_uint8()
        self.Reserved = v_uint8()
        self.SecondaryStatus = v_uint16()
        self.PrimaryBus = v_uint8()
        self.SecondaryBus = v_uint8()
        self.SubordinateBus = v_uint8()
        self.SecondaryLatency = v_uint8()
        self.Range = vstruct.VArray([ _unnamed_16653() for i in range(4) ])
        self.InterruptLine = v_uint8()
        self.InterruptPin = v_uint8()
        self.BridgeControl = v_uint16()


class PCI_HEADER_TYPE_1(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseAddresses = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.PrimaryBus = v_uint8()
        self.SecondaryBus = v_uint8()
        self.SubordinateBus = v_uint8()
        self.SecondaryLatency = v_uint8()
        self.IOBase = v_uint8()
        self.IOLimit = v_uint8()
        self.SecondaryStatus = v_uint16()
        self.MemoryBase = v_uint16()
        self.MemoryLimit = v_uint16()
        self.PrefetchBase = v_uint16()
        self.PrefetchLimit = v_uint16()
        self.PrefetchBaseUpper32 = v_uint32()
        self.PrefetchLimitUpper32 = v_uint32()
        self.IOBaseUpper16 = v_uint16()
        self.IOLimitUpper16 = v_uint16()
        self.CapabilitiesPtr = v_uint8()
        self.Reserved1 = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.ROMBaseAddress = v_uint32()
        self.InterruptLine = v_uint8()
        self.InterruptPin = v_uint8()
        self.BridgeControl = v_uint16()


class PCI_HEADER_TYPE_0(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseAddresses = vstruct.VArray([ v_uint32() for i in range(6) ])
        self.CIS = v_uint32()
        self.SubVendorID = v_uint16()
        self.SubSystemID = v_uint16()
        self.ROMBaseAddress = v_uint32()
        self.CapabilitiesPtr = v_uint8()
        self.Reserved1 = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.Reserved2 = v_uint32()
        self.InterruptLine = v_uint8()
        self.InterruptPin = v_uint8()
        self.MinimumGrant = v_uint8()
        self.MaximumLatency = v_uint8()


class _unnamed_17278(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityInformation = v_uint32()
        self.SecurityDescriptor = v_ptr32()


class _unnamed_17376(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InPath = v_uint8()
        self.Reserved = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.Type = v_uint32()


class OBJECT_DUMP_CONTROL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Stream = v_ptr32()
        self.Detail = v_uint32()


class CACHE_MANAGER_CALLBACKS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AcquireForLazyWrite = v_ptr32()
        self.ReleaseFromLazyWrite = v_ptr32()
        self.AcquireForReadAhead = v_ptr32()
        self.ReleaseFromReadAhead = v_ptr32()


class DBGKD_CONTINUE2(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ContinueStatus = v_uint32()
        self.ControlSet = X86_DBGKD_CONTROL_SET()
        self._pad0020 = v_bytes(size=12)


class HANDLE_TRACE_DB_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientId = CLIENT_ID()
        self.Handle = v_ptr32()
        self.Type = v_uint32()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(16) ])


class ACTIVATION_CONTEXT_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class LPCP_NONPAGED_PORT_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Semaphore = KSEMAPHORE()
        self.BackPointer = v_ptr32()


class DEVICE_RELATIONS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Objects = vstruct.VArray([ v_ptr32() for i in range(1) ])


class BATTERY_REPORTING_SCALE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Granularity = v_uint32()
        self.Capacity = v_uint32()


class MMPAGING_FILE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint32()
        self.MaximumSize = v_uint32()
        self.MinimumSize = v_uint32()
        self.FreeSpace = v_uint32()
        self.CurrentUsage = v_uint32()
        self.PeakUsage = v_uint32()
        self.HighestPage = v_uint32()
        self.File = v_ptr32()
        self.Entry = vstruct.VArray([ v_ptr32() for i in range(2) ])
        self.PageFileName = UNICODE_STRING()
        self.Bitmap = v_ptr32()
        self.PageFileNumber = v_uint32()
        self.FileHandle = v_ptr32()


class STRING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.MaximumLength = v_uint16()
        self.Buffer = v_ptr32()


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


class _unnamed_11277(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class _unnamed_12829(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EntireFrame = v_uint32()


class _unnamed_12828(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReferenceCount = v_uint16()
        self.e1 = MMPFNENTRY()


class CMP_OFFSET_ARRAY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FileOffset = v_uint32()
        self.DataBuffer = v_ptr32()
        self.DataLength = v_uint32()


class _unnamed_12825(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()


class VI_DEADLOCK_GLOBALS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Nodes = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.Resources = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.Threads = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.TimeAcquire = v_uint64()
        self.TimeRelease = v_uint64()
        self.BytesAllocated = v_uint32()
        self.ResourceDatabase = v_ptr32()
        self.ThreadDatabase = v_ptr32()
        self.AllocationFailures = v_uint32()
        self.NodesTrimmedBasedOnAge = v_uint32()
        self.NodesTrimmedBasedOnCount = v_uint32()
        self.NodesSearched = v_uint32()
        self.MaxNodesSearched = v_uint32()
        self.SequenceNumber = v_uint32()
        self.RecursionDepthLimit = v_uint32()
        self.SearchedNodesLimit = v_uint32()
        self.DepthLimitHits = v_uint32()
        self.SearchLimitHits = v_uint32()
        self.ABC_ACB_Skipped = v_uint32()
        self.OutOfOrderReleases = v_uint32()
        self.NodesReleasedOutOfOrder = v_uint32()
        self.TotalReleases = v_uint32()
        self.RootNodesDeleted = v_uint32()
        self.ForgetHistoryCounter = v_uint32()
        self.PoolTrimCounter = v_uint32()
        self.FreeResourceList = LIST_ENTRY()
        self.FreeThreadList = LIST_ENTRY()
        self.FreeNodeList = LIST_ENTRY()
        self.FreeResourceCount = v_uint32()
        self.FreeThreadCount = v_uint32()
        self.FreeNodeCount = v_uint32()
        self.Instigator = v_ptr32()
        self.NumberOfParticipants = v_uint32()
        self.Participant = vstruct.VArray([ v_ptr32() for i in range(32) ])
        self.CacheReductionInProgress = v_uint32()


class LIST_ENTRY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint32()
        self.Blink = v_uint32()


class MMWSLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_14703()


class DBGKD_BREAKPOINTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakPointCount = v_uint32()
        self.ContinueStatus = v_uint32()


class PCI_COMMON_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.ExtensionType = v_uint32()
        self.IrpDispatchTable = v_ptr32()
        self.DeviceState = v_uint8()
        self.TentativeNextState = v_uint8()
        self._pad0010 = v_bytes(size=2)
        self.SecondaryExtLock = KEVENT()


class PCI_SECONDARY_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.List = SINGLE_LIST_ENTRY()
        self.ExtensionType = v_uint32()
        self.Destructor = v_ptr32()


class DBGKD_QUERY_MEMORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Address = v_uint64()
        self.Reserved = v_uint64()
        self.AddressSpace = v_uint32()
        self.Flags = v_uint32()


class MMVAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_12873()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()
        self.u = _unnamed_12875()
        self.ControlArea = v_ptr32()
        self.FirstPrototypePte = v_ptr32()
        self.LastContiguousPte = v_ptr32()
        self.u2 = _unnamed_12878()


class KDEVICE_QUEUE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceListEntry = LIST_ENTRY()
        self.SortKey = v_uint32()
        self.Inserted = v_uint8()
        self._pad0010 = v_bytes(size=3)


class MMPTE_SUBSECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class MMVIEW(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = v_uint32()
        self.ControlArea = v_ptr32()


class PO_DEVICE_NOTIFY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Link = LIST_ENTRY()
        self.TargetDevice = v_ptr32()
        self.WakeNeeded = v_uint8()
        self.OrderLevel = v_uint8()
        self._pad0010 = v_bytes(size=2)
        self.DeviceObject = v_ptr32()
        self.Node = v_ptr32()
        self.DeviceName = v_ptr32()
        self.DriverName = v_ptr32()
        self.ChildCount = v_uint32()
        self.ActiveChild = v_uint32()


class HMAP_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Directory = vstruct.VArray([ v_ptr32() for i in range(1024) ])


class _unnamed_16470(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TestAllocation = _unnamed_17744()
        self._pad0010 = v_bytes(size=4)


class OBJECT_HEADER_QUOTA_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PagedPoolCharge = v_uint32()
        self.NonPagedPoolCharge = v_uint32()
        self.SecurityDescriptorCharge = v_uint32()
        self.ExclusiveProcess = v_ptr32()


class HEAP_STOP_ON_VALUES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.AllocAddress = v_uint32()
        self.AllocTag = HEAP_STOP_ON_TAG()
        self.ReAllocAddress = v_uint32()
        self.ReAllocTag = HEAP_STOP_ON_TAG()
        self.FreeAddress = v_uint32()
        self.FreeTag = HEAP_STOP_ON_TAG()


class WMI_BUFFER_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Wnode = WNODE_HEADER()
        self.Offset = v_uint32()
        self.BufferFlag = v_uint16()
        self.BufferType = v_uint16()
        self.InstanceGuid = GUID()


class RTL_HANDLE_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()


class ARBITER_ALTERNATIVE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Minimum = v_uint64()
        self.Maximum = v_uint64()
        self.Length = v_uint32()
        self.Alignment = v_uint32()
        self.Priority = v_uint32()
        self.Flags = v_uint32()
        self.Descriptor = v_ptr32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(3) ])


class QUAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UseThisFieldToCopy = v_uint64()


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


class HMAP_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Table = vstruct.VArray([ HMAP_ENTRY() for i in range(512) ])


class KSPIN_LOCK_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Lock = v_ptr32()


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


class HANDLE_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Object = v_ptr32()
        self.GrantedAccess = v_uint32()


class _unnamed_17405(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()


class EX_PUSH_LOCK_CACHE_AWARE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locks = vstruct.VArray([ v_ptr32() for i in range(32) ])


class _unnamed_17400(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ProviderId = v_uint32()
        self.DataPath = v_ptr32()
        self.BufferSize = v_uint32()
        self.Buffer = v_ptr32()


class CLIENT_ID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UniqueProcess = v_ptr32()
        self.UniqueThread = v_ptr32()


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


class MMVAD_LONG(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_12873()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()
        self.u = _unnamed_12875()
        self.ControlArea = v_ptr32()
        self.FirstPrototypePte = v_ptr32()
        self.LastContiguousPte = v_ptr32()
        self.u2 = _unnamed_12878()
        self.u3 = _unnamed_15468()
        self.u4 = _unnamed_15469()


class SUBSECTION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ControlArea = v_ptr32()
        self.u = _unnamed_12948()
        self.StartingSector = v_uint32()
        self.NumberOfFullSectors = v_uint32()
        self.SubsectionBase = v_ptr32()
        self.UnusedPtes = v_uint32()
        self.PtesInSubsection = v_uint32()
        self.NextSubsection = v_ptr32()


class MBCB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NodeTypeCode = v_uint16()
        self.NodeIsInZone = v_uint16()
        self.PagesToWrite = v_uint32()
        self.DirtyPages = v_uint32()
        self.Reserved = v_uint32()
        self.BitmapRanges = LIST_ENTRY()
        self.ResumeWritePage = v_uint64()
        self.BitmapRange1 = BITMAP_RANGE()
        self.BitmapRange2 = BITMAP_RANGE()
        self.BitmapRange3 = BITMAP_RANGE()


class FAST_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Gate = KEVENT()
        self.OldIrql = v_uint32()


class MM_SESSION_SPACE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.GlobalVirtualAddress = v_ptr32()
        self.ReferenceCount = v_uint32()
        self.u = _unnamed_14669()
        self.SessionId = v_uint32()
        self.ProcessList = LIST_ENTRY()
        self.LastProcessSwappedOutTime = LARGE_INTEGER()
        self.SessionPageDirectoryIndex = v_uint32()
        self.NonPagablePages = v_uint32()
        self.CommittedPages = v_uint32()
        self.PagedPoolStart = v_ptr32()
        self.PagedPoolEnd = v_ptr32()
        self.PagedPoolBasePde = v_ptr32()
        self.Color = v_uint32()
        self.ResidentProcessCount = v_uint32()
        self.SessionPoolAllocationFailures = vstruct.VArray([ v_uint32() for i in range(4) ])
        self.ImageList = LIST_ENTRY()
        self.LocaleId = v_uint32()
        self.AttachCount = v_uint32()
        self.AttachEvent = KEVENT()
        self.LastProcess = v_ptr32()
        self.ProcessReferenceToSession = v_uint32()
        self.WsListEntry = LIST_ENTRY()
        self.Lookaside = vstruct.VArray([ GENERAL_LOOKASIDE() for i in range(26) ])
        self.Session = MMSESSION()
        self.PagedPoolMutex = KGUARDED_MUTEX()
        self.PagedPoolInfo = MM_PAGED_POOL_INFO()
        self.Vm = MMSUPPORT()
        self.Wsle = v_ptr32()
        self.Win32KDriverUnload = v_ptr32()
        self.PagedPool = POOL_DESCRIPTOR()
        self.PageTables = v_ptr32()
        self.ImageLoadingCount = v_uint32()
        self._pad1ec0 = v_bytes(size=56)


class CM_NAME_CONTROL_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Compressed = v_uint8()
        self._pad0002 = v_bytes(size=1)
        self.RefCount = v_uint16()
        self.NameHash = CM_NAME_HASH()


class _unnamed_17154(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SecurityContext = v_ptr32()
        self.Options = v_uint32()
        self.Reserved = v_uint16()
        self.ShareAccess = v_uint16()
        self.Parameters = v_ptr32()


class KDEVICE_QUEUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.DeviceListHead = LIST_ENTRY()
        self.Lock = v_uint32()
        self.Busy = v_uint8()
        self._pad0014 = v_bytes(size=3)


class _unnamed_13029(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoStatus = IO_STATUS_BLOCK()


class IO_COUNTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReadOperationCount = v_uint64()
        self.WriteOperationCount = v_uint64()
        self.OtherOperationCount = v_uint64()
        self.ReadTransferCount = v_uint64()
        self.WriteTransferCount = v_uint64()
        self.OtherTransferCount = v_uint64()


class PCI_BUS_INTERFACE_STANDARD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Context = v_ptr32()
        self.InterfaceReference = v_ptr32()
        self.InterfaceDereference = v_ptr32()
        self.ReadConfig = v_ptr32()
        self.WriteConfig = v_ptr32()
        self.PinToLine = v_ptr32()
        self.LineToPin = v_ptr32()


class PORT_MESSAGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_16830()
        self.u2 = _unnamed_16831()
        self.ClientId = CLIENT_ID()
        self.MessageId = v_uint32()
        self.ClientViewSize = v_uint32()


class PCI_COMMON_CONFIG(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VendorID = v_uint16()
        self.DeviceID = v_uint16()
        self.Command = v_uint16()
        self.Status = v_uint16()
        self.RevisionID = v_uint8()
        self.ProgIf = v_uint8()
        self.SubClass = v_uint8()
        self.BaseClass = v_uint8()
        self.CacheLineSize = v_uint8()
        self.LatencyTimer = v_uint8()
        self.HeaderType = v_uint8()
        self.BIST = v_uint8()
        self.u = _unnamed_15914()
        self.DeviceSpecific = vstruct.VArray([ v_uint8() for i in range(192) ])


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


class PCI_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Atom = v_uint32()
        self.OldIrql = v_uint8()
        self._pad0008 = v_bytes(size=3)


class POOL_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PoolType = v_uint32()
        self.PoolIndex = v_uint32()
        self.RunningAllocs = v_uint32()
        self.RunningDeAllocs = v_uint32()
        self.TotalPages = v_uint32()
        self.TotalBigPages = v_uint32()
        self.Threshold = v_uint32()
        self.LockAddress = v_ptr32()
        self.PendingFrees = v_ptr32()
        self.PendingFreeDepth = v_uint32()
        self.TotalBytes = v_uint32()
        self.Spare0 = v_uint32()
        self.ListHeads = vstruct.VArray([ LIST_ENTRY() for i in range(512) ])


class DBGKD_QUERY_SPECIAL_CALLS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfSpecialCalls = v_uint32()


class HEAP_UNCOMMMTTED_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.Address = v_uint32()
        self.Size = v_uint32()
        self.filler = v_uint32()


class DUMP_STACK_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Init = DUMP_INITIALIZATION_CONTEXT()
        self.PartitionOffset = LARGE_INTEGER()
        self.DumpPointers = v_ptr32()
        self.PointersLength = v_uint32()
        self.ModulePrefix = v_ptr32()
        self.DriverList = LIST_ENTRY()
        self.InitMsg = STRING()
        self.ProgMsg = STRING()
        self.DoneMsg = STRING()
        self.FileObject = v_ptr32()
        self.UsageType = v_uint32()
        self._pad00b0 = v_bytes(size=4)


class _unnamed_17842(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DiskId = GUID()


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


class DBGKD_READ_WRITE_IO32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.IoAddress = v_uint32()
        self.DataValue = v_uint32()


class POP_HIBER_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WriteToFile = v_uint8()
        self.ReserveLoaderMemory = v_uint8()
        self.ReserveFreeMemory = v_uint8()
        self.VerifyOnWake = v_uint8()
        self.Reset = v_uint8()
        self.HiberFlags = v_uint8()
        self.LinkFile = v_uint8()
        self._pad0008 = v_bytes(size=1)
        self.LinkFileHandle = v_ptr32()
        self.Lock = v_uint32()
        self.MapFrozen = v_uint8()
        self._pad0014 = v_bytes(size=3)
        self.MemoryMap = RTL_BITMAP()
        self.ClonedRanges = LIST_ENTRY()
        self.ClonedRangeCount = v_uint32()
        self.NextCloneRange = v_ptr32()
        self.NextPreserve = v_uint32()
        self.LoaderMdl = v_ptr32()
        self.Clones = v_ptr32()
        self.NextClone = v_ptr32()
        self.NoClones = v_uint32()
        self.Spares = v_ptr32()
        self._pad0048 = v_bytes(size=4)
        self.PagesOut = v_uint64()
        self.IoPage = v_ptr32()
        self.CurrentMcb = v_ptr32()
        self.DumpStack = v_ptr32()
        self.WakeState = v_ptr32()
        self.NoRanges = v_uint32()
        self.HiberVa = v_uint32()
        self.HiberPte = LARGE_INTEGER()
        self.Status = v_uint32()
        self.MemoryImage = v_ptr32()
        self.TableHead = v_ptr32()
        self.CompressionWorkspace = v_ptr32()
        self.CompressedWriteBuffer = v_ptr32()
        self.PerformanceStats = v_ptr32()
        self.CompressionBlock = v_ptr32()
        self.DmaIO = v_ptr32()
        self.TemporaryHeap = v_ptr32()
        self._pad0098 = v_bytes(size=4)
        self.PerfInfo = PO_HIBER_PERF()


class RTL_HANDLE_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MaximumNumberOfHandles = v_uint32()
        self.SizeOfHandleTableEntry = v_uint32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.FreeHandles = v_ptr32()
        self.CommittedHandles = v_ptr32()
        self.UnCommittedHandles = v_ptr32()
        self.MaxReservedHandles = v_ptr32()


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


class TOKEN_CONTROL(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TokenId = LUID()
        self.AuthenticationId = LUID()
        self.ModifiedId = LUID()
        self.TokenSource = TOKEN_SOURCE()


class _unnamed_16653(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Base = v_uint32()
        self.Limit = v_uint32()


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


class HEAP_USERDATA_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SFreeListEntry = SINGLE_LIST_ENTRY()
        self.HeapHandle = v_ptr32()
        self.SizeIndex = v_uint32()
        self.Signature = v_uint32()


class _unnamed_14554(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Overlay = _unnamed_16050()
        self._pad0030 = v_bytes(size=8)


class _unnamed_17839(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.CheckSum = v_uint32()


class RTL_DRIVE_LETTER_CURDIR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint16()
        self.Length = v_uint16()
        self.TimeStamp = v_uint32()
        self.DosPath = STRING()


class _unnamed_17380(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerState = v_uint32()


class _unnamed_17386(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerSequence = v_ptr32()


class _unnamed_15731(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Acquired = v_uint8()
        self.CacheLineSize = v_uint8()
        self.LatencyTimer = v_uint8()
        self.EnablePERR = v_uint8()
        self.EnableSERR = v_uint8()


class TEB_ACTIVE_FRAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flags = v_uint32()
        self.Previous = v_ptr32()
        self.Context = v_ptr32()


class ETIMER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.KeTimer = KTIMER()
        self.TimerApc = KAPC()
        self.TimerDpc = KDPC()
        self.ActiveTimerListEntry = LIST_ENTRY()
        self.Lock = v_uint32()
        self.Period = v_uint32()
        self.ApcAssociated = v_uint8()
        self.WakeTimer = v_uint8()
        self._pad008c = v_bytes(size=2)
        self.WakeTimerListEntry = LIST_ENTRY()
        self._pad0098 = v_bytes(size=4)


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


class FREE_DISPLAY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.RealVectorSize = v_uint32()
        self.Display = RTL_BITMAP()


class PHYSICAL_MEMORY_DESCRIPTOR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NumberOfRuns = v_uint32()
        self.NumberOfPages = v_uint32()
        self.Run = vstruct.VArray([ PHYSICAL_MEMORY_RUN() for i in range(1) ])


class ARBITER_ORDERING_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint16()
        self.Maximum = v_uint16()
        self.Orderings = v_ptr32()


class OBJECT_DIRECTORY_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ChainLink = v_ptr32()
        self.Object = v_ptr32()
        self.HashValue = v_uint32()


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


class ARBITER_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListEntry = LIST_ENTRY()
        self.AlternativeCount = v_uint32()
        self.Alternatives = v_ptr32()
        self.PhysicalDeviceObject = v_ptr32()
        self.RequestSource = v_uint32()
        self.Flags = v_uint32()
        self.WorkSpace = v_uint32()
        self.InterfaceType = v_uint32()
        self.SlotNumber = v_uint32()
        self.BusNumber = v_uint32()
        self.Assignment = v_ptr32()
        self.SelectedAlternative = v_ptr32()
        self.Result = v_uint32()


class _unnamed_14491(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LegacyDeviceNode = v_ptr32()


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


class _unnamed_16831(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.s2 = _unnamed_17493()


class KGDTENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LimitLow = v_uint16()
        self.BaseLow = v_uint16()
        self.HighWord = _unnamed_11817()


class MMPFNENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Modified = v_uint16()


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


class ULARGE_INTEGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.LowPart = v_uint32()
        self.HighPart = v_uint32()


class UNICODE_STRING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint16()
        self.MaximumLength = v_uint16()
        self.Buffer = v_ptr32()


class CELL_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u = u()


class MMSESSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemSpaceViewLock = KGUARDED_MUTEX()
        self.SystemSpaceViewLockPointer = v_ptr32()
        self.SystemSpaceViewStart = v_ptr32()
        self.SystemSpaceViewTable = v_ptr32()
        self.SystemSpaceHashSize = v_uint32()
        self.SystemSpaceHashEntries = v_uint32()
        self.SystemSpaceHashKey = v_uint32()
        self.BitmapFailures = v_uint32()
        self.SystemSpaceBitMap = v_ptr32()


class _unnamed_13218(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReadMemory = DBGKD_READ_MEMORY64()
        self._pad0028 = v_bytes(size=24)


class EPROCESS_QUOTA_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.QuotaEntry = vstruct.VArray([ EPROCESS_QUOTA_ENTRY() for i in range(3) ])
        self.QuotaList = LIST_ENTRY()
        self.ReferenceCount = v_uint32()
        self.ProcessCount = v_uint32()


class CM_KEY_HASH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ConvKey = v_uint32()
        self.NextHash = v_ptr32()
        self.KeyHive = v_ptr32()
        self.KeyCell = v_uint32()


class BUS_HANDLER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Version = v_uint32()
        self.InterfaceType = v_uint32()
        self.ConfigurationType = v_uint32()
        self.BusNumber = v_uint32()
        self.DeviceObject = v_ptr32()
        self.ParentHandler = v_ptr32()
        self.BusData = v_ptr32()
        self.DeviceControlExtensionSize = v_uint32()
        self.BusAddresses = v_ptr32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(4) ])
        self.GetBusData = v_ptr32()
        self.SetBusData = v_ptr32()
        self.AdjustResourceList = v_ptr32()
        self.AssignSlotResources = v_ptr32()
        self.GetInterruptVector = v_ptr32()
        self.TranslateBusAddress = v_ptr32()
        self.Spare1 = v_ptr32()
        self.Spare2 = v_ptr32()
        self.Spare3 = v_ptr32()
        self.Spare4 = v_ptr32()
        self.Spare5 = v_ptr32()
        self.Spare6 = v_ptr32()
        self.Spare7 = v_ptr32()
        self.Spare8 = v_ptr32()


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


class DBGKD_ANY_CONTROL_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.X86ControlSet = X86_DBGKD_CONTROL_SET()
        self._pad001c = v_bytes(size=12)


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


class _unnamed_15829(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseMid = v_uint8()
        self.Flags1 = v_uint8()
        self.Flags2 = v_uint8()
        self.BaseHi = v_uint8()


class HBASE_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.Sequence1 = v_uint32()
        self.Sequence2 = v_uint32()
        self.TimeStamp = LARGE_INTEGER()
        self.Major = v_uint32()
        self.Minor = v_uint32()
        self.Type = v_uint32()
        self.Format = v_uint32()
        self.RootCell = v_uint32()
        self.Length = v_uint32()
        self.Cluster = v_uint32()
        self.FileName = vstruct.VArray([ v_uint8() for i in range(64) ])
        self.Reserved1 = vstruct.VArray([ v_uint32() for i in range(99) ])
        self.CheckSum = v_uint32()
        self.Reserved2 = vstruct.VArray([ v_uint32() for i in range(894) ])
        self.BootType = v_uint32()
        self.BootRecover = v_uint32()


class _unnamed_17449(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Alignment = v_uint32()
        self.MinimumAddress = LARGE_INTEGER()
        self.MaximumAddress = LARGE_INTEGER()


class BUS_EXTENSION_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.BusExtension = v_ptr32()


class DBGKD_GET_SET_BUS_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BusDataType = v_uint32()
        self.BusNumber = v_uint32()
        self.SlotNumber = v_uint32()
        self.Offset = v_uint32()
        self.Length = v_uint32()


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


class KEVENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()


class KSEMAPHORE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = DISPATCHER_HEADER()
        self.Limit = v_uint32()


class PCI_ARBITER_INSTANCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = PCI_SECONDARY_EXTENSION()
        self.Interface = v_ptr32()
        self.BusFdoExtension = v_ptr32()
        self.InstanceName = vstruct.VArray([ v_uint16() for i in range(24) ])
        self.CommonInstance = ARBITER_INSTANCE()


class PI_RESOURCE_ARBITER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceArbiterList = LIST_ENTRY()
        self.ResourceType = v_uint8()
        self._pad000c = v_bytes(size=3)
        self.ArbiterInterface = v_ptr32()
        self.Level = v_uint32()
        self.ResourceList = LIST_ENTRY()
        self.BestResourceList = LIST_ENTRY()
        self.BestConfig = LIST_ENTRY()
        self.ActiveArbiterList = LIST_ENTRY()
        self.State = v_uint8()
        self.ResourcesChanged = v_uint8()
        self._pad0038 = v_bytes(size=2)


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


class _unnamed_16830(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.s1 = _unnamed_17488()


class DBGKD_SET_INTERNAL_BREAKPOINT32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakpointAddress = v_uint32()
        self.Flags = v_uint32()


class DBGKD_CONTINUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ContinueStatus = v_uint32()


class POOL_HACKER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Header = POOL_HEADER()
        self.Contents = vstruct.VArray([ v_uint32() for i in range(8) ])


class _unnamed_17755(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PhysicalDeviceObject = v_ptr32()
        self.ConflictingResource = v_ptr32()
        self.ConflictCount = v_ptr32()
        self.Conflicts = v_ptr32()


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


class PO_HIBER_PERF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IoTicks = v_uint64()
        self.InitTicks = v_uint64()
        self.CopyTicks = v_uint64()
        self.StartCount = v_uint64()
        self.ElapsedTime = v_uint32()
        self.IoTime = v_uint32()
        self.CopyTime = v_uint32()
        self.InitTime = v_uint32()
        self.PagesWritten = v_uint32()
        self.PagesProcessed = v_uint32()
        self.BytesCopied = v_uint32()
        self.DumpCount = v_uint32()
        self.FileRuns = v_uint32()
        self._pad0048 = v_bytes(size=4)


class DEFERRED_WRITE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NodeTypeCode = v_uint16()
        self.NodeByteSize = v_uint16()
        self.FileObject = v_ptr32()
        self.BytesToWrite = v_uint32()
        self.DeferredWriteLinks = LIST_ENTRY()
        self.Event = v_ptr32()
        self.PostRoutine = v_ptr32()
        self.Context1 = v_ptr32()
        self.Context2 = v_ptr32()
        self.LimitModifiedPages = v_uint8()
        self._pad0028 = v_bytes(size=3)


class ARBITER_INSTANCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.MutexEvent = v_ptr32()
        self.Name = v_ptr32()
        self.ResourceType = v_uint32()
        self.Allocation = v_ptr32()
        self.PossibleAllocation = v_ptr32()
        self.OrderingList = ARBITER_ORDERING_LIST()
        self.ReservedList = ARBITER_ORDERING_LIST()
        self.ReferenceCount = v_uint32()
        self.Interface = v_ptr32()
        self.AllocationStackMaxSize = v_uint32()
        self.AllocationStack = v_ptr32()
        self.UnpackRequirement = v_ptr32()
        self.PackResource = v_ptr32()
        self.UnpackResource = v_ptr32()
        self.ScoreRequirement = v_ptr32()
        self.TestAllocation = v_ptr32()
        self.RetestAllocation = v_ptr32()
        self.CommitAllocation = v_ptr32()
        self.RollbackAllocation = v_ptr32()
        self.BootAllocation = v_ptr32()
        self.QueryArbitrate = v_ptr32()
        self.QueryConflict = v_ptr32()
        self.AddReserved = v_ptr32()
        self.StartArbiter = v_ptr32()
        self.PreprocessEntry = v_ptr32()
        self.AllocateEntry = v_ptr32()
        self.GetNextAllocationRange = v_ptr32()
        self.FindSuitableRange = v_ptr32()
        self.AddAllocation = v_ptr32()
        self.BacktrackAllocation = v_ptr32()
        self.OverrideConflict = v_ptr32()
        self.TransactionInProgress = v_uint8()
        self._pad008c = v_bytes(size=3)
        self.Extension = v_ptr32()
        self.BusDeviceObject = v_ptr32()
        self.ConflictCallbackContext = v_ptr32()
        self.ConflictCallback = v_ptr32()


class MMMOD_WRITER_LISTHEAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = LIST_ENTRY()
        self.Event = KEVENT()


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


class POP_IDLE_HANDLER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Latency = v_uint32()
        self.TimeCheck = v_uint32()
        self.DemoteLimit = v_uint32()
        self.PromoteLimit = v_uint32()
        self.PromoteCount = v_uint32()
        self.Demote = v_uint8()
        self.Promote = v_uint8()
        self.PromotePercent = v_uint8()
        self.DemotePercent = v_uint8()
        self.State = v_uint8()
        self.Spare = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.IdleFunction = v_ptr32()


class MMSUPPORT_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SessionSpace = v_uint8()
        self.MemoryPriority = v_uint8()
        self.GrowWsleHash = v_uint16()


class HEAP_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = _unnamed_13571()


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


class PLUGPLAY_EVENT_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EventGuid = GUID()
        self.EventCategory = v_uint32()
        self.Result = v_ptr32()
        self.Flags = v_uint32()
        self.TotalSize = v_uint32()
        self.DeviceObject = v_ptr32()
        self.u = _unnamed_16891()


class LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_ptr32()
        self.Blink = v_ptr32()


class CM_KEY_SECURITY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint16()
        self.Reserved = v_uint16()
        self.Flink = v_uint32()
        self.Blink = v_uint32()
        self.ReferenceCount = v_uint32()
        self.DescriptorLength = v_uint32()
        self.Descriptor = SECURITY_DESCRIPTOR_RELATIVE()


class _unnamed_17802(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceId = vstruct.VArray([ v_uint16() for i in range(1) ])


class _unnamed_17800(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceIds = vstruct.VArray([ v_uint16() for i in range(1) ])


class _unnamed_17807(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Notification = v_ptr32()


class _unnamed_17804(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NotificationStructure = v_ptr32()
        self.DeviceIds = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0008 = v_bytes(size=2)


class POP_ACTION_TRIGGER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint32()
        self.Flags = v_uint8()
        self.Spare = vstruct.VArray([ v_uint8() for i in range(3) ])
        self.Battery = _unnamed_14990()


class _unnamed_17809(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NotificationCode = v_uint32()
        self.NotificationData = v_uint32()


class _unnamed_17744(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ArbitrationList = v_ptr32()
        self.AllocateFromCount = v_uint32()
        self.AllocateFrom = v_ptr32()


class DEVICE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DosDevicesDirectory = v_ptr32()
        self.GlobalDosDevicesDirectory = v_ptr32()
        self.ReferenceCount = v_uint32()
        self.DriveMap = v_uint32()
        self.DriveType = vstruct.VArray([ v_uint8() for i in range(32) ])


class CONTROL_AREA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Segment = v_ptr32()
        self.DereferenceList = LIST_ENTRY()
        self.NumberOfSectionReferences = v_uint32()
        self.NumberOfPfnReferences = v_uint32()
        self.NumberOfMappedViews = v_uint32()
        self.NumberOfSystemCacheViews = v_uint32()
        self.NumberOfUserReferences = v_uint32()
        self.u = _unnamed_12907()
        self.FilePointer = v_ptr32()
        self.WaitingForDeletion = v_ptr32()
        self.ModifiedWriteCount = v_uint16()
        self.FlushInProgressCount = v_uint16()
        self.WritableUserReferences = v_uint32()
        self.QuadwordPad = v_uint32()


class SEP_AUDIT_POLICY_OVERLAY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PolicyBits = v_uint64()


class _unnamed_16047(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Create = _unnamed_17138()


class _unnamed_13409(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.FileOffset = LARGE_INTEGER()


class KAPC_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ApcListHead = vstruct.VArray([ LIST_ENTRY() for i in range(2) ])
        self.Process = v_ptr32()
        self.KernelApcInProgress = v_uint8()
        self.KernelApcPending = v_uint8()
        self.UserApcPending = v_uint8()
        self._pad0018 = v_bytes(size=1)


class MMVAD_SHORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_12873()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()
        self.u = _unnamed_12875()


class DBGKD_GET_VERSION32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.ProtocolVersion = v_uint16()
        self.Flags = v_uint16()
        self.KernBase = v_uint32()
        self.PsLoadedModuleList = v_uint32()
        self.MachineType = v_uint16()
        self.ThCallbackStack = v_uint16()
        self.NextCallback = v_uint16()
        self.FramePointer = v_uint16()
        self.KiCallUserMode = v_uint32()
        self.KeUserCallbackDispatcher = v_uint32()
        self.BreakpointWithStatus = v_uint32()
        self.DebuggerDataList = v_uint32()


class CM_CELL_REMAP_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.OldCell = v_uint32()
        self.NewCell = v_uint32()


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


class PO_MEMORY_RANGE_ARRAY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Range = PO_MEMORY_RANGE_ARRAY_RANGE()


class POWER_STATE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SystemState = v_uint32()


class SYSTEM_POWER_POLICY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint32()
        self.PowerButton = POWER_ACTION_POLICY()
        self.SleepButton = POWER_ACTION_POLICY()
        self.LidClose = POWER_ACTION_POLICY()
        self.LidOpenWake = v_uint32()
        self.Reserved = v_uint32()
        self.Idle = POWER_ACTION_POLICY()
        self.IdleTimeout = v_uint32()
        self.IdleSensitivity = v_uint8()
        self.DynamicThrottle = v_uint8()
        self.Spare2 = vstruct.VArray([ v_uint8() for i in range(2) ])
        self.MinSleep = v_uint32()
        self.MaxSleep = v_uint32()
        self.ReducedLatencySleep = v_uint32()
        self.WinLogonFlags = v_uint32()
        self.Spare3 = v_uint32()
        self.DozeS4Timeout = v_uint32()
        self.BroadcastCapacityResolution = v_uint32()
        self.DischargePolicy = vstruct.VArray([ SYSTEM_POWER_LEVEL() for i in range(4) ])
        self.VideoTimeout = v_uint32()
        self.VideoDimDisplay = v_uint8()
        self._pad00c8 = v_bytes(size=3)
        self.VideoReserved = vstruct.VArray([ v_uint32() for i in range(3) ])
        self.SpindownTimeout = v_uint32()
        self.OptimizeForPower = v_uint8()
        self.FanThrottleTolerance = v_uint8()
        self.ForcedThrottle = v_uint8()
        self.MinThrottle = v_uint8()
        self.OverThrottled = POWER_ACTION_POLICY()


class _unnamed_17244(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()


class MMADDRESS_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.StartVpn = v_uint32()
        self.EndVpn = v_uint32()


class _unnamed_17363(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.IdType = v_uint32()


class KINTERRUPT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Type = v_uint16()
        self.Size = v_uint16()
        self.InterruptListEntry = LIST_ENTRY()
        self.ServiceRoutine = v_ptr32()
        self.ServiceContext = v_ptr32()
        self.SpinLock = v_uint32()
        self.TickCount = v_uint32()
        self.ActualLock = v_ptr32()
        self.DispatchAddress = v_ptr32()
        self.Vector = v_uint32()
        self.Irql = v_uint8()
        self.SynchronizeIrql = v_uint8()
        self.FloatingSave = v_uint8()
        self.Connected = v_uint8()
        self.Number = v_uint8()
        self.ShareVector = v_uint8()
        self._pad0030 = v_bytes(size=2)
        self.Mode = v_uint32()
        self.ServiceCount = v_uint32()
        self.DispatchCount = v_uint32()
        self.DispatchCode = vstruct.VArray([ v_uint32() for i in range(106) ])


class SECURITY_DESCRIPTOR_RELATIVE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Revision = v_uint8()
        self.Sbz1 = v_uint8()
        self.Control = v_uint16()
        self.Owner = v_uint32()
        self.Group = v_uint32()
        self.Sacl = v_uint32()
        self.Dacl = v_uint32()


class DUMP_INITIALIZATION_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Reserved = v_uint32()
        self.MemoryBlock = v_ptr32()
        self.CommonBuffer = vstruct.VArray([ v_ptr32() for i in range(2) ])
        self._pad0018 = v_bytes(size=4)
        self.PhysicalAddress = vstruct.VArray([ LARGE_INTEGER() for i in range(2) ])
        self.StallRoutine = v_ptr32()
        self.OpenRoutine = v_ptr32()
        self.WriteRoutine = v_ptr32()
        self.FinishRoutine = v_ptr32()
        self.AdapterObject = v_ptr32()
        self.MappedRegisterBase = v_ptr32()
        self.PortConfiguration = v_ptr32()
        self.CrashDump = v_uint8()
        self._pad0048 = v_bytes(size=3)
        self.MaximumTransferSize = v_uint32()
        self.CommonBufferSize = v_uint32()
        self.TargetAddress = v_ptr32()
        self.WritePendingRoutine = v_ptr32()
        self.PartitionStyle = v_uint32()
        self.DiskInfo = _unnamed_17615()
        self._pad0070 = v_bytes(size=4)


class _unnamed_14493(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DockStatus = v_uint32()
        self.ListEntry = LIST_ENTRY()
        self.SerialNumber = v_ptr32()


class _unnamed_13310(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReadMemory = DBGKD_READ_MEMORY32()
        self._pad0028 = v_bytes(size=28)


class _unnamed_17368(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceTextType = v_uint32()
        self.LocaleId = v_uint32()


class OBJECT_HANDLE_COUNT_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Process = v_ptr32()
        self.HandleCount = v_uint32()


class _unnamed_15469(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Banked = v_ptr32()


class _unnamed_15785(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = LIST_ENTRY()


class _unnamed_15784(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UserData = v_ptr32()
        self.Owner = v_ptr32()


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


class TOKEN_SOURCE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SourceName = vstruct.VArray([ v_uint8() for i in range(8) ])
        self.SourceIdentifier = LUID()


class MMPFN(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_12825()
        self.PteAddress = v_ptr32()
        self.u2 = _unnamed_12827()
        self.u3 = _unnamed_12828()
        self.OriginalPte = MMPTE()
        self.u4 = _unnamed_12829()


class _unnamed_14548(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MasterIrp = v_ptr32()


class flags(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Removable = v_uint8()


class DBGKD_SEARCH_MEMORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SearchAddress = v_uint64()
        self.SearchLength = v_uint64()
        self.PatternLength = v_uint32()
        self._pad0018 = v_bytes(size=4)


class PM_SUPPORT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Rsvd2 = v_uint8()


class _unnamed_16891(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DeviceClass = _unnamed_17797()


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


class HEAP_VIRTUAL_ALLOC_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = LIST_ENTRY()
        self.ExtraStuff = HEAP_ENTRY_EXTRA()
        self.CommitSize = v_uint32()
        self.ReserveSize = v_uint32()
        self.BusyBlock = HEAP_ENTRY()


class VI_DEADLOCK_THREAD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Thread = v_ptr32()
        self.CurrentSpinNode = v_ptr32()
        self.CurrentOtherNode = v_ptr32()
        self.ListEntry = LIST_ENTRY()
        self.NodeCount = v_uint32()
        self.PagingCount = v_uint32()


class SUPPORTED_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.SystemAddressSpace = v_uint32()
        self.SystemBase = v_uint64()
        self.Base = v_uint64()
        self.Limit = v_uint64()


class ARBITER_PARAMETERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Parameters = _unnamed_16470()


class EXCEPTION_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_ptr32()
        self.ExceptionAddress = v_ptr32()
        self.NumberParameters = v_uint32()
        self.ExceptionInformation = vstruct.VArray([ v_uint32() for i in range(15) ])


class MMPTE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u = _unnamed_12742()


class VI_DEADLOCK_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Parent = v_ptr32()
        self.ChildrenList = LIST_ENTRY()
        self.SiblingsList = LIST_ENTRY()
        self.ResourceList = LIST_ENTRY()
        self.Root = v_ptr32()
        self.ThreadEntry = v_ptr32()
        self.Active = v_uint32()
        self.StackTrace = vstruct.VArray([ v_ptr32() for i in range(8) ])
        self.ParentStackTrace = vstruct.VArray([ v_ptr32() for i in range(8) ])


class _unnamed_17488(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataLength = v_uint16()
        self.TotalLength = v_uint16()


class HEAP_STOP_ON_TAG(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HeapAndTagIndex = v_uint32()


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


class CM_KEY_INDEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint16()
        self.Count = v_uint16()
        self.List = vstruct.VArray([ v_uint32() for i in range(1) ])


class CM_CACHED_VALUE_INDEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CellIndex = v_uint32()
        self.Data = _unnamed_14838()


class IMAGE_DEBUG_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Characteristics = v_uint32()
        self.TimeDateStamp = v_uint32()
        self.MajorVersion = v_uint16()
        self.MinorVersion = v_uint16()
        self.Type = v_uint32()
        self.SizeOfData = v_uint32()
        self.AddressOfRawData = v_uint32()
        self.PointerToRawData = v_uint32()


class SYSPTES_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ListHead = LIST_ENTRY()
        self.Count = v_uint32()


class DBGKD_READ_WRITE_IO_EXTENDED32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.InterfaceType = v_uint32()
        self.BusNumber = v_uint32()
        self.AddressSpace = v_uint32()
        self.IoAddress = v_uint32()
        self.DataValue = v_uint32()


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


class _unnamed_15445(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InitialPrivilegeSet = INITIAL_PRIVILEGE_SET()


class DBGKD_WRITE_BREAKPOINT64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakPointAddress = v_uint64()
        self.BreakPointHandle = v_uint32()
        self._pad0010 = v_bytes(size=4)


class IMAGE_NT_HEADERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.FileHeader = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()


class HEAP_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.PreviousSize = v_uint16()
        self.SmallTagIndex = v_uint8()
        self.Flags = v_uint8()
        self.UnusedBytes = v_uint8()
        self.SegmentIndex = v_uint8()


class PNP_DEVICE_EVENT_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Status = v_uint32()
        self.EventQueueMutex = KMUTANT()
        self.Lock = KGUARDED_MUTEX()
        self.List = LIST_ENTRY()


class SECURITY_SUBJECT_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ClientToken = v_ptr32()
        self.ImpersonationLevel = v_uint32()
        self.PrimaryToken = v_ptr32()
        self.ProcessAuditId = v_ptr32()


class X86_DBGKD_CONTROL_SET(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TraceFlag = v_uint32()
        self.Dr7 = v_uint32()
        self.CurrentSymbolStart = v_uint32()
        self.CurrentSymbolEnd = v_uint32()


class _unnamed_15282(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Generic = _unnamed_15922()


class MI_VERIFIER_DRIVER_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Links = LIST_ENTRY()
        self.Loads = v_uint32()
        self.Unloads = v_uint32()
        self.BaseName = UNICODE_STRING()
        self.StartAddress = v_ptr32()
        self.EndAddress = v_ptr32()
        self.Flags = v_uint32()
        self.Signature = v_uint32()
        self.PoolPageHeaders = SLIST_HEADER()
        self.PoolTrackers = SLIST_HEADER()
        self.CurrentPagedPoolAllocations = v_uint32()
        self.CurrentNonPagedPoolAllocations = v_uint32()
        self.PeakPagedPoolAllocations = v_uint32()
        self.PeakNonPagedPoolAllocations = v_uint32()
        self.PagedBytes = v_uint32()
        self.NonPagedBytes = v_uint32()
        self.PeakPagedBytes = v_uint32()
        self.PeakNonPagedBytes = v_uint32()


class PO_MEMORY_RANGE_ARRAY_RANGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PageNo = v_uint32()
        self.StartPage = v_uint32()
        self.EndPage = v_uint32()
        self.CheckSum = v_uint32()


class GDI_TEB_BATCH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Offset = v_uint32()
        self.HDC = v_uint32()
        self.Buffer = vstruct.VArray([ v_uint32() for i in range(310) ])


class WMI_CLIENT_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ProcessorNumber = v_uint8()
        self.Alignment = v_uint8()
        self.LoggerId = v_uint16()


class MMSUBSECTION_FLAGS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ReadOnly = v_uint32()


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


class WMI_LOGGER_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BufferSpinLock = v_uint32()
        self._pad0008 = v_bytes(size=4)
        self.StartTime = LARGE_INTEGER()
        self.LogFileHandle = v_ptr32()
        self.LoggerSemaphore = KSEMAPHORE()
        self.LoggerThread = v_ptr32()
        self.LoggerEvent = KEVENT()
        self.FlushEvent = KEVENT()
        self.LoggerStatus = v_uint32()
        self.LoggerId = v_uint32()
        self.BuffersAvailable = v_uint32()
        self.UsePerfClock = v_uint32()
        self.WriteFailureLimit = v_uint32()
        self.BuffersDirty = v_uint32()
        self.BuffersInUse = v_uint32()
        self.SwitchingInProgress = v_uint32()
        self._pad0070 = v_bytes(size=4)
        self.FreeList = SLIST_HEADER()
        self.FlushList = SLIST_HEADER()
        self.WaitList = SLIST_HEADER()
        self.GlobalList = SLIST_HEADER()
        self.ProcessorBuffers = v_ptr32()
        self.LoggerName = UNICODE_STRING()
        self.LogFileName = UNICODE_STRING()
        self.LogFilePattern = UNICODE_STRING()
        self.NewLogFileName = UNICODE_STRING()
        self.EndPageMarker = v_ptr32()
        self.CollectionOn = v_uint32()
        self.KernelTraceOn = v_uint32()
        self.PerfLogInTransition = v_uint32()
        self.RequestFlag = v_uint32()
        self.EnableFlags = v_uint32()
        self.MaximumFileSize = v_uint32()
        self.LoggerMode = v_uint32()
        self.Wow = v_uint32()
        self.LastFlushedBuffer = v_uint32()
        self.RefCount = v_uint32()
        self.FlushTimer = v_uint32()
        self._pad00e8 = v_bytes(size=4)
        self.FirstBufferOffset = LARGE_INTEGER()
        self.ByteOffset = LARGE_INTEGER()
        self.BufferAgeLimit = LARGE_INTEGER()
        self.MaximumBuffers = v_uint32()
        self.MinimumBuffers = v_uint32()
        self.EventsLost = v_uint32()
        self.BuffersWritten = v_uint32()
        self.LogBuffersLost = v_uint32()
        self.RealTimeBuffersLost = v_uint32()
        self.BufferSize = v_uint32()
        self.NumberOfBuffers = v_uint32()
        self.SequencePtr = v_ptr32()
        self.InstanceGuid = GUID()
        self.LoggerHeader = v_ptr32()
        self.GetCpuClock = v_ptr32()
        self.ClientSecurityContext = SECURITY_CLIENT_CONTEXT()
        self.LoggerExtension = v_ptr32()
        self.ReleaseQueue = v_uint32()
        self.EnableFlagExtension = TRACE_ENABLE_FLAG_EXTENSION()
        self.LocalSequence = v_uint32()
        self.MaximumIrql = v_uint32()
        self.EnableFlagArray = v_ptr32()
        self.LoggerMutex = KMUTANT()
        self.MutexCount = v_uint32()
        self.FileCounter = v_uint32()
        self.BufferCallback = v_ptr32()
        self.CallbackContext = v_ptr32()
        self.PoolType = v_uint32()
        self._pad01c8 = v_bytes(size=4)
        self.ReferenceSystemTime = LARGE_INTEGER()
        self.ReferenceTimeStamp = LARGE_INTEGER()


class DBGKD_READ_WRITE_MSR(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Msr = v_uint32()
        self.DataValueLow = v_uint32()
        self.DataValueHigh = v_uint32()


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


class MMWSLE_HASH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Key = v_ptr32()
        self.Index = v_uint32()


class SECTION_IMAGE_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TransferAddress = v_ptr32()
        self.ZeroBits = v_uint32()
        self.MaximumStackSize = v_uint32()
        self.CommittedStackSize = v_uint32()
        self.SubSystemType = v_uint32()
        self.SubSystemMinorVersion = v_uint16()
        self.SubSystemMajorVersion = v_uint16()
        self.GpValue = v_uint32()
        self.ImageCharacteristics = v_uint16()
        self.DllCharacteristics = v_uint16()
        self.Machine = v_uint16()
        self.ImageContainsCode = v_uint8()
        self.Spare1 = v_uint8()
        self.LoaderFlags = v_uint32()
        self.ImageFileSize = v_uint32()
        self.Reserved = vstruct.VArray([ v_uint32() for i in range(1) ])


class HEAP_SUBSEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Bucket = v_ptr32()
        self.UserBlocks = v_ptr32()
        self.AggregateExchg = INTERLOCK_SEQ()
        self.BlockSize = v_uint16()
        self.FreeThreshold = v_uint16()
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
        self.OwnerThreads = vstruct.VArray([ OWNER_ENTRY() for i in range(2) ])
        self.ContentionCount = v_uint32()
        self.NumberOfSharedWaiters = v_uint16()
        self.NumberOfExclusiveWaiters = v_uint16()
        self.Address = v_ptr32()
        self.SpinLock = v_uint32()


class KGUARDED_MUTEX(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.Owner = v_ptr32()
        self.Contention = v_uint32()
        self.Gate = KGATE()
        self.KernelApcDisable = v_uint16()
        self.SpecialApcDisable = v_uint16()


class DBGKD_SET_CONTEXT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ContextFlags = v_uint32()


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


class RTL_ATOM_TABLE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashLink = v_ptr32()
        self.HandleIndex = v_uint16()
        self.Atom = v_uint16()
        self.ReferenceCount = v_uint16()
        self.Flags = v_uint8()
        self.NameLength = v_uint8()
        self.Name = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0010 = v_bytes(size=2)


class CHILD_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.List = v_uint32()


class _unnamed_17281(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Vpb = v_ptr32()
        self.DeviceObject = v_ptr32()


class _unnamed_17285(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Srb = v_ptr32()


class PCI_MJ_DISPATCH_TABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PnpIrpMaximumMinorFunction = v_uint32()
        self.PnpIrpDispatchTable = v_ptr32()
        self.PowerIrpMaximumMinorFunction = v_uint32()
        self.PowerIrpDispatchTable = v_ptr32()
        self.SystemControlIrpDispatchStyle = v_uint32()
        self.SystemControlIrpDispatchFunction = v_ptr32()
        self.OtherIrpDispatchStyle = v_uint32()
        self.OtherIrpDispatchFunction = v_ptr32()


class EX_PUSH_LOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Locked = v_uint32()


class ARBITER_INTERFACE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.Version = v_uint16()
        self.Context = v_ptr32()
        self.InterfaceReference = v_ptr32()
        self.InterfaceDereference = v_ptr32()
        self.ArbiterHandler = v_ptr32()
        self.Flags = v_uint32()


class OBJECT_DIRECTORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HashBuckets = vstruct.VArray([ v_ptr32() for i in range(37) ])
        self.Lock = EX_PUSH_LOCK()
        self.DeviceMap = v_ptr32()
        self.SessionId = v_uint32()


class _unnamed_14191(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ImageCommitment = v_uint32()


class _unnamed_14192(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ImageInformation = v_ptr32()


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


class POP_DEVICE_POWER_IRP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Free = SINGLE_LIST_ENTRY()
        self.Irp = v_ptr32()
        self.Notify = v_ptr32()
        self.Pending = LIST_ENTRY()
        self.Complete = LIST_ENTRY()
        self.Abort = LIST_ENTRY()
        self.Failed = LIST_ENTRY()


class _unnamed_15747(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PrimaryBus = v_uint8()
        self.SecondaryBus = v_uint8()
        self.SubordinateBus = v_uint8()
        self.SubtractiveDecode = v_uint8()


class PRIVATE_CACHE_MAP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NodeTypeCode = v_uint16()
        self._pad0004 = v_bytes(size=2)
        self.ReadAheadMask = v_uint32()
        self.FileObject = v_ptr32()
        self._pad0010 = v_bytes(size=4)
        self.FileOffset1 = LARGE_INTEGER()
        self.BeyondLastByte1 = LARGE_INTEGER()
        self.FileOffset2 = LARGE_INTEGER()
        self.BeyondLastByte2 = LARGE_INTEGER()
        self.ReadAheadOffset = vstruct.VArray([ LARGE_INTEGER() for i in range(2) ])
        self.ReadAheadLength = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.ReadAheadSpinLock = v_uint32()
        self.PrivateLinks = LIST_ENTRY()
        self._pad0058 = v_bytes(size=4)


class SEP_AUDIT_POLICY_CATEGORIES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.System = v_uint32()
        self.AccountLogon = v_uint32()


class IMAGE_SECTION_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name = vstruct.VArray([ v_uint8() for i in range(8) ])
        self.Misc = _unnamed_16105()
        self.VirtualAddress = v_uint32()
        self.SizeOfRawData = v_uint32()
        self.PointerToRawData = v_uint32()
        self.PointerToRelocations = v_uint32()
        self.PointerToLinenumbers = v_uint32()
        self.NumberOfRelocations = v_uint16()
        self.NumberOfLinenumbers = v_uint16()
        self.Characteristics = v_uint32()


class PO_DEVICE_NOTIFY_ORDER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DevNodeSequence = v_uint32()
        self.WarmEjectPdoPointer = v_ptr32()
        self.OrderLevel = vstruct.VArray([ PO_NOTIFY_ORDER_LEVEL() for i in range(8) ])


class _unnamed_12827(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Blink = v_uint32()


class DBGKD_WRITE_MEMORY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TargetBaseAddress = v_uint64()
        self.TransferCount = v_uint32()
        self.ActualBytesWritten = v_uint32()


class LIST_ENTRY64(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_uint64()
        self.Blink = v_uint64()


class VACB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BaseAddress = v_ptr32()
        self.SharedCacheMap = v_ptr32()
        self.Overlay = _unnamed_13409()
        self.LruList = LIST_ENTRY()


class _unnamed_17355(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Lock = v_uint8()


class CM_KEY_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint16()
        self.Flags = v_uint16()
        self.LastWriteTime = LARGE_INTEGER()
        self.Spare = v_uint32()
        self.Parent = v_uint32()
        self.SubKeyCounts = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.SubKeyLists = vstruct.VArray([ v_uint32() for i in range(2) ])
        self.ValueList = CHILD_LIST()
        self.Security = v_uint32()
        self.Class = v_uint32()
        self.MaxNameLen = v_uint32()
        self.MaxClassLen = v_uint32()
        self.MaxValueNameLen = v_uint32()
        self.MaxValueDataLen = v_uint32()
        self.WorkVar = v_uint32()
        self.NameLength = v_uint16()
        self.ClassLength = v_uint16()
        self.Name = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0050 = v_bytes(size=2)


class CM_KEY_VALUE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint16()
        self.NameLength = v_uint16()
        self.DataLength = v_uint32()
        self.Data = v_uint32()
        self.Type = v_uint32()
        self.Flags = v_uint16()
        self.Spare = v_uint16()
        self.Name = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0018 = v_bytes(size=2)


class _unnamed_17350(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.WhichSpace = v_uint32()
        self.Buffer = v_ptr32()
        self.Offset = v_uint32()
        self.Length = v_uint32()


class SE_AUDIT_PROCESS_CREATION_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ImageFileName = v_ptr32()


class _unnamed_14990(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Level = v_uint32()


class SECURITY_TOKEN_PROXY_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.ProxyClass = v_uint32()
        self.PathInfo = UNICODE_STRING()
        self.ContainerMask = v_uint32()
        self.ObjectMask = v_uint32()


class HEAP_UCR_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.ReservedSize = v_uint32()
        self.CommittedSize = v_uint32()
        self.filler = v_uint32()


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


class EX_RUNDOWN_REF(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()


class CM_NOTIFY_BLOCK(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HiveList = LIST_ENTRY()
        self.PostList = LIST_ENTRY()
        self.KeyControlBlock = v_ptr32()
        self.KeyBody = v_ptr32()
        self.Filter = v_uint32()
        self.SubjectContext = SECURITY_SUBJECT_CONTEXT()


class MMPTE_PROTOTYPE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Valid = v_uint32()


class PCI_HEADER_TYPE_DEPENDENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.type0 = _unnamed_15746()


class CM_BIG_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint16()
        self.Count = v_uint16()
        self.List = v_uint32()


class VI_POOL_PAGE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.NextPage = v_ptr32()
        self.VerifierEntry = v_ptr32()
        self.Signature = v_uint32()


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


class DBGKD_FILL_MEMORY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Address = v_uint64()
        self.Length = v_uint32()
        self.Flags = v_uint16()
        self.PatternLength = v_uint16()


class CM_KEY_SECURITY_CACHE_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Cell = v_uint32()
        self.CachedSecurity = v_ptr32()


class MMADDRESS_NODE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u1 = _unnamed_12931()
        self.LeftChild = v_ptr32()
        self.RightChild = v_ptr32()
        self.StartingVpn = v_uint32()
        self.EndingVpn = v_uint32()


class ARBITER_ORDERING(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint64()
        self.End = v_uint64()


class _unnamed_15933(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Data = vstruct.VArray([ v_uint32() for i in range(3) ])


class EXCEPTION_RECORD32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_uint32()
        self.ExceptionAddress = v_uint32()
        self.NumberParameters = v_uint32()
        self.ExceptionInformation = vstruct.VArray([ v_uint32() for i in range(15) ])


class _unnamed_15935(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Start = v_uint32()
        self.Length = v_uint32()
        self.Reserved = v_uint32()


class DBGKD_READ_MEMORY32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TargetBaseAddress = v_uint32()
        self.TransferCount = v_uint32()
        self.ActualBytesRead = v_uint32()


class _unnamed_15939(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.DataSize = v_uint32()
        self.Reserved1 = v_uint32()
        self.Reserved2 = v_uint32()


class OBJECT_HANDLE_COUNT_DATABASE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CountEntries = v_uint32()
        self.HandleCountEntries = vstruct.VArray([ OBJECT_HANDLE_COUNT_ENTRY() for i in range(1) ])


class LPCP_PORT_OBJECT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ConnectionPort = v_ptr32()
        self.ConnectedPort = v_ptr32()
        self.MsgQueue = LPCP_PORT_QUEUE()
        self.Creator = CLIENT_ID()
        self.ClientSectionBase = v_ptr32()
        self.ServerSectionBase = v_ptr32()
        self.PortContext = v_ptr32()
        self.ClientThread = v_ptr32()
        self.SecurityQos = SECURITY_QUALITY_OF_SERVICE()
        self.StaticSecurity = SECURITY_CLIENT_CONTEXT()
        self.LpcReplyChainHead = LIST_ENTRY()
        self.LpcDataInfoChainHead = LIST_ENTRY()
        self.ServerProcess = v_ptr32()
        self.MaxMessageLength = v_uint16()
        self.MaxConnectionInfoLength = v_uint16()
        self.Flags = v_uint32()
        self.WaitEvent = KEVENT()


class _unnamed_17454(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumVector = v_uint32()
        self.MaximumVector = v_uint32()


class _unnamed_17457(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MinimumChannel = v_uint32()
        self.MaximumChannel = v_uint32()


class CALL_PERFORMANCE_DATA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SpinLock = v_uint32()
        self.HashTable = vstruct.VArray([ LIST_ENTRY() for i in range(64) ])


class EXCEPTION_POINTERS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionRecord = v_ptr32()
        self.ContextRecord = v_ptr32()


class CM_KEY_SECURITY_CACHE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Cell = v_uint32()
        self.ConvKey = v_uint32()
        self.List = LIST_ENTRY()
        self.DescriptorLength = v_uint32()
        self.RealRefCount = v_uint32()
        self.Descriptor = SECURITY_DESCRIPTOR_RELATIVE()


class POP_TRIGGER_WAIT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Event = KEVENT()
        self.Status = v_uint32()
        self.Link = LIST_ENTRY()
        self.Trigger = v_ptr32()


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
        self.Queue = _unnamed_12231()
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


class PCI_SLOT_NUMBER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.u = _unnamed_15693()


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


class CM_NAME_HASH(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ConvKey = v_uint32()
        self.NextHash = v_ptr32()
        self.NameLength = v_uint16()
        self.Name = vstruct.VArray([ v_uint16() for i in range(1) ])


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


class LPCP_MESSAGE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = LIST_ENTRY()
        self.SenderPort = v_ptr32()
        self.RepliedToThread = v_ptr32()
        self.PortContext = v_ptr32()
        self._pad0018 = v_bytes(size=4)
        self.Request = PORT_MESSAGE()


class EX_QUEUE_WORKER_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.QueueDisabled = v_uint32()


class _unnamed_11817(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Bytes = _unnamed_15829()


class PCI_FDO_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.List = SINGLE_LIST_ENTRY()
        self.ExtensionType = v_uint32()
        self.IrpDispatchTable = v_ptr32()
        self.DeviceState = v_uint8()
        self.TentativeNextState = v_uint8()
        self._pad0010 = v_bytes(size=2)
        self.SecondaryExtLock = KEVENT()
        self.PhysicalDeviceObject = v_ptr32()
        self.FunctionalDeviceObject = v_ptr32()
        self.AttachedDeviceObject = v_ptr32()
        self.ChildListLock = KEVENT()
        self.ChildPdoList = v_ptr32()
        self.BusRootFdoExtension = v_ptr32()
        self.ParentFdoExtension = v_ptr32()
        self.ChildBridgePdoList = v_ptr32()
        self.PciBusInterface = v_ptr32()
        self.MaxSubordinateBus = v_uint8()
        self._pad0054 = v_bytes(size=3)
        self.BusHandler = v_ptr32()
        self.BaseBus = v_uint8()
        self.Fake = v_uint8()
        self.ChildDelete = v_uint8()
        self.Scanned = v_uint8()
        self.ArbitersInitialized = v_uint8()
        self.BrokenVideoHackApplied = v_uint8()
        self.Hibernated = v_uint8()
        self._pad0060 = v_bytes(size=1)
        self.PowerState = PCI_POWER_STATE()
        self.SecondaryExtension = SINGLE_LIST_ENTRY()
        self.ChildWaitWakeCount = v_uint32()
        self.PreservedConfig = v_ptr32()
        self.Lock = PCI_LOCK()
        self.HotPlugParameters = _unnamed_15731()
        self._pad00bc = v_bytes(size=3)
        self.BusHackFlags = v_uint32()


class _unnamed_17231(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.FileInformationClass = v_uint32()
        self.FileObject = v_ptr32()
        self.ReplaceIfExists = v_uint8()
        self.AdvanceOnly = v_uint8()
        self._pad0010 = v_bytes(size=2)


class PS_IMPERSONATION_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Token = v_ptr32()
        self.CopyOnOpen = v_uint8()
        self.EffectiveOnly = v_uint8()
        self._pad0008 = v_bytes(size=2)
        self.ImpersonationLevel = v_uint32()


class _unnamed_12931(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Balance = v_uint32()


class DBGKD_WRITE_BREAKPOINT32(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BreakPointAddress = v_uint32()
        self.BreakPointHandle = v_uint32()


class MMPFNLIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Total = v_uint32()
        self.ListName = v_uint32()
        self.Flink = v_uint32()
        self.Blink = v_uint32()


class MMPTE_FLUSH_LIST(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Count = v_uint32()
        self.FlushVa = vstruct.VArray([ v_ptr32() for i in range(33) ])


class SINGLE_LIST_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()


class IO_STACK_LOCATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MajorFunction = v_uint8()
        self.MinorFunction = v_uint8()
        self.Flags = v_uint8()
        self.Control = v_uint8()
        self.Parameters = _unnamed_16047()
        self.DeviceObject = v_ptr32()
        self.FileObject = v_ptr32()
        self.CompletionRoutine = v_ptr32()
        self.Context = v_ptr32()


class PCI_PDO_EXTENSION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Next = v_ptr32()
        self.ExtensionType = v_uint32()
        self.IrpDispatchTable = v_ptr32()
        self.DeviceState = v_uint8()
        self.TentativeNextState = v_uint8()
        self._pad0010 = v_bytes(size=2)
        self.SecondaryExtLock = KEVENT()
        self.Slot = PCI_SLOT_NUMBER()
        self.PhysicalDeviceObject = v_ptr32()
        self.ParentFdoExtension = v_ptr32()
        self.SecondaryExtension = SINGLE_LIST_ENTRY()
        self.BusInterfaceReferenceCount = v_uint32()
        self.AgpInterfaceReferenceCount = v_uint32()
        self.VendorId = v_uint16()
        self.DeviceId = v_uint16()
        self.SubsystemVendorId = v_uint16()
        self.SubsystemId = v_uint16()
        self.RevisionId = v_uint8()
        self.ProgIf = v_uint8()
        self.SubClass = v_uint8()
        self.BaseClass = v_uint8()
        self.AdditionalResourceCount = v_uint8()
        self.AdjustedInterruptLine = v_uint8()
        self.InterruptPin = v_uint8()
        self.RawInterruptLine = v_uint8()
        self.CapabilitiesPtr = v_uint8()
        self.SavedLatencyTimer = v_uint8()
        self.SavedCacheLineSize = v_uint8()
        self.HeaderType = v_uint8()
        self.NotPresent = v_uint8()
        self.ReportedMissing = v_uint8()
        self.ExpectedWritebackFailure = v_uint8()
        self.NoTouchPmeEnable = v_uint8()
        self.LegacyDriver = v_uint8()
        self.UpdateHardware = v_uint8()
        self.MovedDevice = v_uint8()
        self.DisablePowerDown = v_uint8()
        self.NeedsHotPlugConfiguration = v_uint8()
        self.IDEInNativeMode = v_uint8()
        self.BIOSAllowsIDESwitchToNativeMode = v_uint8()
        self.IoSpaceUnderNativeIdeControl = v_uint8()
        self.OnDebugPath = v_uint8()
        self.IoSpaceNotRequired = v_uint8()
        self._pad005c = v_bytes(size=2)
        self.PowerState = PCI_POWER_STATE()
        self.Dependent = PCI_HEADER_TYPE_DEPENDENT()
        self.HackFlags = v_uint64()
        self.Resources = v_ptr32()
        self.BridgeFdoExtension = v_ptr32()
        self.NextBridge = v_ptr32()
        self.NextHashEntry = v_ptr32()
        self.Lock = PCI_LOCK()
        self.PowerCapabilities = PCI_PMC()
        self.TargetAgpCapabilityId = v_uint8()
        self._pad00c4 = v_bytes(size=1)
        self.CommandEnables = v_uint16()
        self.InitialCommand = v_uint16()


class _unnamed_17812(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VetoType = v_uint32()
        self.DeviceIdVetoNameBuffer = vstruct.VArray([ v_uint16() for i in range(1) ])
        self._pad0008 = v_bytes(size=2)


class _unnamed_17815(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.BlockedDriverGuid = GUID()


class _unnamed_17817(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ParentId = vstruct.VArray([ v_uint16() for i in range(1) ])


class _unnamed_17952(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EndingOffset = v_ptr32()
        self.ResourceToRelease = v_ptr32()


class _unnamed_17953(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ResourceToRelease = v_ptr32()


class _unnamed_17954(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.SyncType = v_uint32()
        self.PageProtection = v_uint32()


class _unnamed_17955(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Argument1 = v_ptr32()
        self.Argument2 = v_ptr32()
        self.Argument3 = v_ptr32()
        self.Argument4 = v_ptr32()
        self.Argument5 = v_ptr32()


class _unnamed_17173(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Length = v_uint32()
        self.Key = v_uint32()
        self.ByteOffset = LARGE_INTEGER()


class SYSTEM_POWER_CAPABILITIES(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.PowerButtonPresent = v_uint8()
        self.SleepButtonPresent = v_uint8()
        self.LidPresent = v_uint8()
        self.SystemS1 = v_uint8()
        self.SystemS2 = v_uint8()
        self.SystemS3 = v_uint8()
        self.SystemS4 = v_uint8()
        self.SystemS5 = v_uint8()
        self.HiberFilePresent = v_uint8()
        self.FullWake = v_uint8()
        self.VideoDimPresent = v_uint8()
        self.ApmPresent = v_uint8()
        self.UpsPresent = v_uint8()
        self.ThermalControl = v_uint8()
        self.ProcessorThrottle = v_uint8()
        self.ProcessorMinThrottle = v_uint8()
        self.ProcessorMaxThrottle = v_uint8()
        self.spare2 = vstruct.VArray([ v_uint8() for i in range(4) ])
        self.DiskSpinDown = v_uint8()
        self.spare3 = vstruct.VArray([ v_uint8() for i in range(8) ])
        self.SystemBatteriesPresent = v_uint8()
        self.BatteriesAreShortTerm = v_uint8()
        self.BatteryScale = vstruct.VArray([ BATTERY_REPORTING_SCALE() for i in range(3) ])
        self.AcOnLineWake = v_uint32()
        self.SoftLidWake = v_uint32()
        self.RtcWake = v_uint32()
        self.MinDeviceWakeState = v_uint32()
        self.DefaultLowLatencyWake = v_uint32()


class THERMAL_INFORMATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ThermalStamp = v_uint32()
        self.ThermalConstant1 = v_uint32()
        self.ThermalConstant2 = v_uint32()
        self.Processors = v_uint32()
        self.SamplingPeriod = v_uint32()
        self.CurrentTemperature = v_uint32()
        self.PassiveTripPoint = v_uint32()
        self.CriticalTripPoint = v_uint32()
        self.ActiveTripPointCount = v_uint8()
        self._pad0024 = v_bytes(size=3)
        self.ActiveTripPoint = vstruct.VArray([ v_uint32() for i in range(10) ])


class MMEXTEND_INFO(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CommittedSize = v_uint64()
        self.ReferenceCount = v_uint32()
        self._pad0010 = v_bytes(size=4)


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


class u(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.KeyNode = CM_KEY_NODE()


class _unnamed_14703(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.VirtualAddress = v_ptr32()


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


class POWER_CHANNEL_SUMMARY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Signature = v_uint32()
        self.TotalCount = v_uint32()
        self.D0Count = v_uint32()
        self.NotifyList = LIST_ENTRY()



