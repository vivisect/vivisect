
# FIXME this is named wrong!

import vstruct
from vstruct.primitives import *

MAX_PATH = 260

class CLIENT_ID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.UniqueProcess = v_ptr32()
        self.UniqueThread = v_ptr32()

class EXCEPTION_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionCode = v_uint32()
        self.ExceptionFlags = v_uint32()
        self.ExceptionRecord = v_ptr32()
        self.ExceptionAddress = v_ptr32()
        self.NumberParameters = v_uint32()

class EXCEPTION_REGISTRATION(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.prev = v_ptr32()
        self.handler = v_ptr32()

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
        self.VirtualAllocBlocks = ListEntry()
        self.Segments = vstruct.VArray([v_uint32() for i in range(64)])
        self.u = vstruct.VArray([v_uint8() for i in range(16)])
        self.u2 = vstruct.VArray([v_uint8() for i in range(2)])
        self.AllocatorBackTraceIndex = v_uint16()
        self.NonDedicatedListLength = v_uint32()
        self.LargeBlocksIndex = v_ptr32()
        self.PseudoTagEntries = v_ptr32()
        self.FreeLists = vstruct.VArray([ListEntry() for i in range(128)])
        self.LockVariable = v_uint32()
        self.CommitRoutine = v_ptr32()
        self.FrontEndHeap = v_ptr32()
        self.FrontEndHeapLockCount = v_uint16()
        self.FrontEndHeapType = v_uint8()
        self.LastSegmentIndex = v_uint8()

class HEAP_SEGMENT(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Entry = HEAP_ENTRY()
        self.SegmentSignature = v_uint32()
        self.SegmentFlags = v_uint32()
        self.Heap = v_ptr32()
        self.LargestUncommitedRange = v_uint32()
        self.BaseAddress = v_ptr32()
        self.NumberOfPages = v_uint32()
        self.FirstEntry = v_ptr32()
        self.LastValidEntry = v_ptr32()
        self.NumberOfUnCommittedPages = v_uint32()
        self.NumberOfUnCommittedRanges = v_uint32()
        self.UncommittedRanges = v_ptr32()
        self.SegmentAllocatorBackTraceIndex = v_uint16()
        self.Reserved = v_uint16()
        self.LastEntryInSegment = v_ptr32()

class HEAP_ENTRY(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Size = v_uint16()
        self.PrevSize = v_uint16()
        self.SegmentIndex = v_uint8()
        self.Flags = v_uint8()
        self.Unused = v_uint8()
        self.TagIndex = v_uint8()

class ListEntry(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Flink = v_ptr32()
        self.Blink = v_ptr32()

class NT_TIB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ExceptionList = v_ptr32()
        self.StackBase = v_ptr32()
        self.StackLimit = v_ptr32()
        self.SubSystemTib = v_ptr32()
        self.FiberData = v_ptr32()
        #x.Version = v_ptr32() # This is a union field
        self.ArbitraryUserPtr = v_ptr32()
        self.Self = v_ptr32()

class PEB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.InheritedAddressSpace = v_uint8()
        self.ReadImageFileExecOptions = v_uint8()
        self.BeingDebugged = v_uint8()
        self.SpareBool = v_uint8()
        self.Mutant = v_ptr32()
        self.ImageBaseAddress = v_ptr32()
        self.Ldr = v_ptr32()
        self.ProcessParameters = v_ptr32()
        self.SubSystemData = v_ptr32()
        self.ProcessHeap = v_ptr32()
        self.FastPebLock = v_ptr32()
        self.FastPebLockRoutine = v_ptr32()
        self.FastPebUnlockRoutine = v_ptr32()
        self.EnvironmentUpdateCount = v_uint32()
        self.KernelCallbackTable = v_ptr32()
        self.SystemReserved = v_uint32()
        self.AtlThunkSListPtr32 = v_ptr32()
        self.FreeList = v_ptr32()
        self.TlsExpansionCounter = v_uint32()
        self.TlsBitmap = v_ptr32()
        self.TlsBitmapBits = vstruct.VArray([v_uint32() for i in range(2)])
        self.ReadOnlySharedMemoryBase = v_ptr32()
        self.ReadOnlySharedMemoryHeap = v_ptr32()
        self.ReadOnlyStaticServerData = v_ptr32()
        self.AnsiCodePageData = v_ptr32()
        self.OemCodePageData = v_ptr32()
        self.UnicodeCaseTableData = v_ptr32()
        self.NumberOfProcessors = v_uint32()
        self.NtGlobalFlag = v_uint64()
        self.CriticalSectionTimeout = v_uint64()
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
        self.GdiHandleBuffer = vstruct.VArray([v_ptr32() for i in range(34)])
        self.PostProcessInitRoutine = v_ptr32()
        self.TlsExpansionBitmap = v_ptr32()
        self.TlsExpansionBitmapBits = vstruct.VArray([v_uint32() for i in range(32)])
        self.SessionId = v_uint32()
        self.AppCompatFlags = v_uint64()
        self.AppCompatFlagsUser = v_uint64()
        self.pShimData = v_ptr32()
        self.AppCompatInfo = v_ptr32()
        self.CSDVersion = v_ptr32()
        self.UNKNOWN = v_uint32()
        self.ActivationContextData = v_ptr32()
        self.ProcessAssemblyStorageMap = v_ptr32()
        self.SystemDefaultActivationContextData = v_ptr32()
        self.SystemAssemblyStorageMap = v_ptr32()
        self.MinimumStackCommit = v_uint32()

class SEH3_SCOPETABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.EnclosingLevel = v_int32()
        self.FilterFunction = v_ptr32()
        self.HandlerFunction = v_ptr32()

class SEH4_SCOPETABLE(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.GSCookieOffset = v_int32()
        self.GSCookieXOROffset = v_int32()
        self.EHCookieOffset = v_int32()
        self.EHCookieXOROffset = v_int32()
        self.EnclosingLevel = v_int32()
        self.FilterFunction = v_ptr32()
        self.HandlerFunction = v_ptr32()

class TEB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.TIB = NT_TIB()
        self.EnvironmentPointer = v_ptr32()
        self.ClientId = CLIENT_ID()
        self.ActiveRpcHandle = v_ptr32()
        self.ThreadLocalStorage = v_ptr32()
        self.ProcessEnvironmentBlock = v_ptr32()
        self.LastErrorValue = v_uint32()
        self.CountOfOwnedCriticalSections = v_uint32()
        self.CsrClientThread = v_ptr32()
        self.Win32ThreadInfo = v_ptr32()
        self.User32Reserved = vstruct.VArray([v_uint32() for i in range(26)])
        self.UserReserved = vstruct.VArray([v_uint32() for i in range(5)])
        self.WOW32Reserved = v_ptr32()
        self.CurrentLocale = v_uint32()
        self.FpSoftwareStatusRegister = v_uint32()

class CLSID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.uuid = GUID()

class IID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.uuid = GUID()

class SYSTEMTIME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.wYear = v_uint16()
        self.wMonth = v_uint16()
        self.wDayOfWeek = v_uint16()
        self.wDay = v_uint16()
        self.wHour = v_uint16()
        self.wMinute = v_uint16()
        self.wSecond = v_uint16()
        self.wMilliseconds = v_uint16()

    def __str__(self):
        #no timezone info
        return '%04d-%02d-%02d %02d:%02d:%02d.%d' % (self.wYear, self.wMonth, self.wDay, self.wHour, self.wMinute, self.wSecond, self.wMilliseconds)

class OSVERSIONINFOEXA(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwOSVersionInfoSize    = v_uint32() 
        self.dwMajorVersion         = v_uint32()
        self.dwMinorVersion         = v_uint32()
        self.dwBuildNumber          = v_uint32()
        self.dwPlatformId           = v_uint32()
        self.szCSDVersion           = v_str(128)
        self.wServicePackMajor      = v_uint16()
        self.wServicePackMinor      = v_uint16()
        self.wSuiteMask             = v_uint16()
        self.wProductType           = v_uint8()
        self.wReserved              = v_uint8()

class OSVERSIONINFOEXW(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwOSVersionInfoSize    = v_uint32() 
        self.dwMajorVersion         = v_uint32()
        self.dwMinorVersion         = v_uint32()
        self.dwBuildNumber          = v_uint32()
        self.dwPlatformId           = v_uint32()
        self.szCSDVersion           = v_wstr(128)
        self.wServicePackMajor      = v_uint16()
        self.wServicePackMinor      = v_uint16()
        self.wSuiteMask             = v_uint16()
        self.wProductType           = v_uint8()
        self.wReserved              = v_uint8()

class SERVICE_STATUS(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwServiceType          = v_uint32()
        self.dwCurrentState         = v_uint32()
        self.dwControlsAccepted     = v_uint32()
        self.dwWin32ExitCode        = v_uint32()
        self.dwServiceSpecificExitCode = v_uint32()
        self.dwCheckPoint           = v_uint32()
        self.dwWaitHint             = v_uint32()

class KEY_EVENT_RECORD(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.bKeyDown               = v_uint32()
        self.wRepeatCount           = v_uint16()
        self.wVirtualKeyCode        = v_uint16()
        self.wVirtualScanCode       = v_uint16()
        self.unicodeChar            = v_uint16()
        self.dwControlKeyState      = v_uint32()

class WIN32_FIND_DATAW(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwFileAttributes       = v_uint32()
        self.ftCreationTime         = v_uint64()
        self.ftLastAccessTime       = v_uint64()
        self.ftLastWriteTime        = v_uint64()
        self.nFileSizeHigh          = v_uint32()
        self.nFileSizeLow           = v_uint32()
        self.dwReserved0            = v_uint32()
        self.dwReserved1            = v_uint32()
        self.cFileName              = v_wstr(MAX_PATH)
        self.cAlternateFileName     = v_wstr(14)

class MIB_TCPROW(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwState                = v_uint32()
        self.dwLocalAddr            = v_uint32()
        self.dwLocalPort            = v_uint32()
        self.dwRemoteAddr           = v_uint32()
        self.dwRemotePort           = v_uint32()

class MIB_UDPROW_OWNER_PID(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwLocalAddr            = v_uint32()
        self.dwLocalPort            = v_uint32()
        self.dwOwningPid            = v_uint32()


DRIVE_TYPE = v_enum()
DRIVE_TYPE.UNKNOWN              = 0
DRIVE_TYPE.NO_ROOT_DIR          = 1
DRIVE_TYPE.REMOVABLE            = 2
DRIVE_TYPE.FIXED                = 3
DRIVE_TYPE.REMOTE               = 4
DRIVE_TYPE.CDROM                = 5
DRIVE_TYPE.RAMDISK              = 6

#INPUT_RECORD_SIZE               = 0x20
#WINDOW_BUFFER_SIZE_EVENT        = 0x04
# EventType for INPUT_RECORD struct
INPUT_RECORD_EVENT_TYPE = v_enum()
INPUT_RECORD_EVENT_TYPE.KEY_EVENT      = 0x01
INPUT_RECORD_EVENT_TYPE.FOCUS_EVENT    = 0x10
INPUT_RECORD_EVENT_TYPE.MENU_EVENT     = 0x08
INPUT_RECORD_EVENT_TYPE.MOUSE_EVENT    = 0x02

FILE_OPERATION = v_enum()
FILE_OPERATION.FO_MOVE          = 0x0001
FILE_OPERATION.FO_COPY          = 0x0002
FILE_OPERATION.FO_DELETE        = 0x0003
FILE_OPERATION.FO_RENAME        = 0x0004

KEY_EVENT = v_bitmask()
KEY_EVENT.CAPSLOCK_ON           = 0x0080
KEY_EVENT.ENHANCED_KEY          = 0x0100
KEY_EVENT.LEFT_ALT_PRESSED      = 0x0002
KEY_EVENT.LEFT_CTRL_PRESSED     = 0x0008
KEY_EVENT.NUMLOCK_ON            = 0x0020
KEY_EVENT.RIGHT_ALT_PRESSED     = 0x0001
KEY_EVENT.RIGHT_CTRL_PRESSED    = 0x0004
KEY_EVENT.SCROLLLOCK_ON         = 0x0040
KEY_EVENT.SHIFT_PRESSED         = 0x0010

MIB_TCP_STATE = v_enum()
MIB_TCP_STATE.CLOSED            = 1
MIB_TCP_STATE.LISTEN            = 2
MIB_TCP_STATE.SYN_SENT          = 3
MIB_TCP_STATE.SYN_RCVD          = 4
MIB_TCP_STATE.ESTAB             = 5
MIB_TCP_STATE.FIN_WAIT1         = 6
MIB_TCP_STATE.FIN_WAIT2         = 7
MIB_TCP_STATE.CLOSE_WAIT        = 8
MIB_TCP_STATE.CLOSING           = 9
MIB_TCP_STATE.LAST_ACK          = 10
MIB_TCP_STATE.TIME_WAIT         = 11
MIB_TCP_STATE.DELETE_TCB        = 12


SERVICE_STATE = v_enum()
SERVICE_STATE.CONTINUE_PENDING = 0x00000005
SERVICE_STATE.PAUSE_PENDING    = 0x00000006
SERVICE_STATE.PAUSED           = 0x00000007
SERVICE_STATE.RUNNING          = 0x00000004
SERVICE_STATE.START_PENDING    = 0x00000002
SERVICE_STATE.STOP_PENDING     = 0x00000003
SERVICE_STATE.STOPPED          = 0x00000001

SERVICE_START_TYPE = v_enum()
SERVICE_START_TYPE.AUTO_START   = 0x00000002
SERVICE_START_TYPE.BOOT_START   = 0x00000000
SERVICE_START_TYPE.DEMAND_START = 0x00000003
SERVICE_START_TYPE.DISABLED     = 0x00000004
SERVICE_START_TYPE.SYSTEM_START = 0x00000001

SERVICE_CONTROL = v_enum()
SERVICE_CONTROL.STOP            = 0x00000001
SERVICE_CONTROL.PAUSE           = 0x00000002
SERVICE_CONTROL.CONTINUE        = 0x00000003
SERVICE_CONTROL.START           = 0x00088888  #Fake SERVICE_CONTROL value to include start here

SERVICE_TYPE = v_bitmask()
SERVICE_TYPE.FILE_SYSTEM_DRIVER  =  0x00000002
SERVICE_TYPE.KERNEL_DRIVER       =  0x00000001
SERVICE_TYPE.WIN32_OWN_PROCESS   =  0x00000010
SERVICE_TYPE.WIN32_SHARE_PROCESS =  0x00000020
SERVICE_TYPE.INTERACTIVE_PROCESS =  0x00000100

HKEY_REGISTRY = v_enum()
HKEY_REGISTRY.HKEY_CLASSES_ROOT        =  0x80000000
HKEY_REGISTRY.HKEY_CURRENT_USER        =  0x80000001
HKEY_REGISTRY.HKEY_LOCAL_MACHINE       =  0x80000002
HKEY_REGISTRY.HKEY_USERS               =  0x80000003
HKEY_REGISTRY.HKEY_PERFORMANCE_DATA    =  0x80000004
HKEY_REGISTRY.HKEY_PERFORMANCE_TEXT    =  0x80000050
HKEY_REGISTRY.HKEY_PERFORMANCE_NLSTEXT =  0x80000060
HKEY_REGISTRY.HKEY_CURRENT_CONFIG      =  0x80000005
HKEY_REGISTRY.HKEY_DYN_DATA            = 0x80000006

REG_TYPE = v_enum()
REG_TYPE.REG_NONE                        = 0
REG_TYPE.REG_SZ                          = 1
REG_TYPE.REG_EXPAND_SZ                   = 2
REG_TYPE.REG_BINARY                      = 3
REG_TYPE.REG_DWORD                       = 4
REG_TYPE.REG_DWORD_BIG_ENDIAN            = 5
REG_TYPE.REG_LINK                        = 6
REG_TYPE.REG_MULTI_SZ                    = 7
REG_TYPE.REG_RESOURCE_LIST               = 8
REG_TYPE.REG_FULL_RESOURCE_DESCRIPTOR    = 9
REG_TYPE.REG_RESOURCE_REQUIREMENTS_LIST  = 10
REG_TYPE.REG_QWORD                       = 11

FILE_ATTRIBUTE = v_bitmask()
FILE_ATTRIBUTE.READONLY             = 0x00000001  
FILE_ATTRIBUTE.HIDDEN               = 0x00000002  
FILE_ATTRIBUTE.SYSTEM               = 0x00000004  
FILE_ATTRIBUTE.DIRECTORY            = 0x00000010  
FILE_ATTRIBUTE.ARCHIVE              = 0x00000020  
FILE_ATTRIBUTE.DEVICE               = 0x00000040  
FILE_ATTRIBUTE.NORMAL               = 0x00000080  
FILE_ATTRIBUTE.TEMPORARY            = 0x00000100  
FILE_ATTRIBUTE.SPARSE_FILE          = 0x00000200  
FILE_ATTRIBUTE.REPARSE_POINT        = 0x00000400  
FILE_ATTRIBUTE.COMPRESSED           = 0x00000800  
FILE_ATTRIBUTE.OFFLINE              = 0x00001000  
FILE_ATTRIBUTE.NOT_CONTENT_INDEXED  = 0x00002000  
FILE_ATTRIBUTE.ENCRYPTED            = 0x00004000  
#INVALID_FILE_ATTRIBUTES             = 0xffffffff

WNET_RESOURCE_SCOPE = v_enum()
WNET_RESOURCE_SCOPE.RESOURCE_CONNECTED  = 0x00000001
WNET_RESOURCE_SCOPE.RESOURCE_GLOBALNET  = 0x00000002
WNET_RESOURCE_SCOPE.RESOURCE_REMEMBERED = 0x00000003
WNET_RESOURCE_SCOPE.RESOURCE_RECENT     = 0x00000004
WNET_RESOURCE_SCOPE.RESOURCE_CONTEXT    = 0x00000005


WNET_RESOURCE_TYPE = v_enum()
WNET_RESOURCE_TYPE.ANY        = 0x00000000
WNET_RESOURCE_TYPE.DISK       = 0x00000001
WNET_RESOURCE_TYPE.PRINT      = 0x00000002
WNET_RESOURCE_TYPE.RESERVED   = 0x00000008
WNET_RESOURCE_TYPE.UNKNOWN    = 0xFFFFFFFF


WNET_RESOURCEDISPLAYTYPE = v_enum()
WNET_RESOURCEDISPLAYTYPE.GENERIC        = 0x00000000
WNET_RESOURCEDISPLAYTYPE.DOMAIN         = 0x00000001
WNET_RESOURCEDISPLAYTYPE.SERVER         = 0x00000002
WNET_RESOURCEDISPLAYTYPE.SHARE          = 0x00000003
WNET_RESOURCEDISPLAYTYPE.FILE           = 0x00000004
WNET_RESOURCEDISPLAYTYPE.GROUP          = 0x00000005
WNET_RESOURCEDISPLAYTYPE.NETWORK        = 0x00000006
WNET_RESOURCEDISPLAYTYPE.ROOT           = 0x00000007
WNET_RESOURCEDISPLAYTYPE.SHAREADMIN     = 0x00000008
WNET_RESOURCEDISPLAYTYPE.DIRECTORY      = 0x00000009
WNET_RESOURCEDISPLAYTYPE.TREE           = 0x0000000A
WNET_RESOURCEDISPLAYTYPE.NDSCONTAINER   = 0x0000000B

EXIT_WINDOWS = v_bitmask()
EXIT_WINDOWS.HYBRID_SHUTDOWN  = 0x00400000 
EXIT_WINDOWS.LOGOFF           = 0 
EXIT_WINDOWS.POWEROFF         = 0x00000008 
EXIT_WINDOWS.REBOOT           = 0x00000002 
EXIT_WINDOWS.RESTARTAPPS      = 0x00000040 
EXIT_WINDOWS.SHUTDOWN         = 0x00000001 
EXIT_WINDOWS.FORCE            = 0x00000004 
EXIT_WINDOWS.FORCEIFHUNG      = 0x00000010 

WTS_CHANGE_EVENT = v_enum()
WTS_CHANGE_EVENT.WTS_CONSOLE_CONNECT             = 0x1
WTS_CHANGE_EVENT.WTS_CONSOLE_DISCONNECT          = 0x2
WTS_CHANGE_EVENT.WTS_REMOTE_CONNECT              = 0x3
WTS_CHANGE_EVENT.WTS_REMOTE_DISCONNECT           = 0x4
WTS_CHANGE_EVENT.WTS_SESSION_LOGON               = 0x5
WTS_CHANGE_EVENT.WTS_SESSION_LOGOFF              = 0x6
WTS_CHANGE_EVENT.WTS_SESSION_LOCK                = 0x7
WTS_CHANGE_EVENT.WTS_SESSION_UNLOCK              = 0x8
WTS_CHANGE_EVENT.WTS_SESSION_REMOTE_CONTROL      = 0x9
WTS_CHANGE_EVENT.WTS_SESSION_CREATE              = 0xA
WTS_CHANGE_EVENT.WTS_SESSION_TERMINATE           = 0xB

# each entry is the (vkey_name, mappable_base, shift_modified)
# if the key is non printable, None is used
# if there is no shift-modifier, None is used
VIRTUAL_KEY_CODE = v_enum()
VIRTUAL_KEY_CODE.VK_LBUTTON     = 0x01
VIRTUAL_KEY_CODE.VK_RBUTTON     = 0x02
VIRTUAL_KEY_CODE.VK_CANCEL      = 0x03
VIRTUAL_KEY_CODE.VK_MBUTTON     = 0x04
VIRTUAL_KEY_CODE.VK_XBUTTON1    = 0x05
VIRTUAL_KEY_CODE.VK_XBUTTON2    = 0x06
# 0x07: Undefined
VIRTUAL_KEY_CODE.VK_BACK        = 0x08
VIRTUAL_KEY_CODE.VK_TAB         = 0x09
# 0x0a-0x0b: Reserved
VIRTUAL_KEY_CODE.VK_CLEAR       = 0x0c
VIRTUAL_KEY_CODE.VK_RETURN      = 0x0d
# 0x0e-0x0f: Undefined
VIRTUAL_KEY_CODE.VK_SHIFT       = 0x10
VIRTUAL_KEY_CODE.VK_CONTROL     = 0x11
VIRTUAL_KEY_CODE.VK_MENU        = 0x12
VIRTUAL_KEY_CODE.VK_PAUSE       = 0x13
VIRTUAL_KEY_CODE.VK_CAPITAL     = 0x14
VIRTUAL_KEY_CODE.VK_HANGUEL     = 0x15
VIRTUAL_KEY_CODE.VK_HANGUL      = 0x15
VIRTUAL_KEY_CODE.VK_KANA        = 0x15
# 0x16: undefined
VIRTUAL_KEY_CODE.VK_JUNJA       = 0x17
VIRTUAL_KEY_CODE.VK_FINAL       = 0x18
VIRTUAL_KEY_CODE.VK_HANJA       = 0x19
VIRTUAL_KEY_CODE.VK_KANJI       = 0x19
# 0x1a: undefined
VIRTUAL_KEY_CODE.VK_ESCAPE      = 0x1b
VIRTUAL_KEY_CODE.VK_CONVERT     = 0x1c
VIRTUAL_KEY_CODE.VK_NONCONVERT  = 0x1d
VIRTUAL_KEY_CODE.VK_ACCEPT      = 0x1e
VIRTUAL_KEY_CODE.VK_MODECHANGE  = 0x1f
VIRTUAL_KEY_CODE.VK_SPACE       = 0x20
VIRTUAL_KEY_CODE.VK_PRIOR       = 0x21
VIRTUAL_KEY_CODE.VK_NEXT        = 0x22
VIRTUAL_KEY_CODE.VK_END         = 0x23
VIRTUAL_KEY_CODE.VK_HOME        = 0x24
VIRTUAL_KEY_CODE.VK_LEFT        = 0x25
VIRTUAL_KEY_CODE.VK_UP          = 0x26
VIRTUAL_KEY_CODE.VK_RIGHT       = 0x27
VIRTUAL_KEY_CODE.VK_DOWN        = 0x28
VIRTUAL_KEY_CODE.VK_SELECT      = 0x29
VIRTUAL_KEY_CODE.VK_PRINT       = 0x2a
VIRTUAL_KEY_CODE.VK_EXECUTE     = 0x2b
VIRTUAL_KEY_CODE.VK_SNAPSHOT    = 0x2c
VIRTUAL_KEY_CODE.VK_INSERT      = 0x2d
VIRTUAL_KEY_CODE.VK_DELETE      = 0x2e
VIRTUAL_KEY_CODE.VK_HELP        = 0x2f
VIRTUAL_KEY_CODE.VK_0           = 0x30
VIRTUAL_KEY_CODE.VK_1           = 0x31
VIRTUAL_KEY_CODE.VK_2           = 0x32
VIRTUAL_KEY_CODE.VK_3           = 0x33
VIRTUAL_KEY_CODE.VK_4           = 0x34
VIRTUAL_KEY_CODE.VK_5           = 0x35
VIRTUAL_KEY_CODE.VK_6           = 0x36
VIRTUAL_KEY_CODE.VK_7           = 0x37
VIRTUAL_KEY_CODE.VK_8           = 0x38
VIRTUAL_KEY_CODE.VK_9           = 0x39
# 0x3a-0x40: undefinded
VIRTUAL_KEY_CODE.VK_A           = 0x41
VIRTUAL_KEY_CODE.VK_B           = 0x42
VIRTUAL_KEY_CODE.VK_C           = 0x43
VIRTUAL_KEY_CODE.VK_D           = 0x44
VIRTUAL_KEY_CODE.VK_E           = 0x45
VIRTUAL_KEY_CODE.VK_F           = 0x46
VIRTUAL_KEY_CODE.VK_G           = 0x47
VIRTUAL_KEY_CODE.VK_H           = 0x48
VIRTUAL_KEY_CODE.VK_I           = 0x49
VIRTUAL_KEY_CODE.VK_J           = 0x4a
VIRTUAL_KEY_CODE.VK_K           = 0x4b
VIRTUAL_KEY_CODE.VK_L           = 0x4c
VIRTUAL_KEY_CODE.VK_M           = 0x4d
VIRTUAL_KEY_CODE.VK_N           = 0x4e
VIRTUAL_KEY_CODE.VK_O           = 0x4f
VIRTUAL_KEY_CODE.VK_P           = 0x50
VIRTUAL_KEY_CODE.VK_Q           = 0x51
VIRTUAL_KEY_CODE.VK_R           = 0x52
VIRTUAL_KEY_CODE.VK_S           = 0x53
VIRTUAL_KEY_CODE.VK_T           = 0x54
VIRTUAL_KEY_CODE.VK_U           = 0x55
VIRTUAL_KEY_CODE.VK_V           = 0x56
VIRTUAL_KEY_CODE.VK_W           = 0x57
VIRTUAL_KEY_CODE.VK_X           = 0x58
VIRTUAL_KEY_CODE.VK_Y           = 0x59
VIRTUAL_KEY_CODE.VK_Z           = 0x5a
VIRTUAL_KEY_CODE.VK_LWIN        = 0x5b
VIRTUAL_KEY_CODE.VK_RWIN        = 0x5c
VIRTUAL_KEY_CODE.VK_APPS        = 0x5d
# 0x5e reserved
VIRTUAL_KEY_CODE.VK_SLEEP       = 0x5f
VIRTUAL_KEY_CODE.VK_NUMPAD0     = 0x60
VIRTUAL_KEY_CODE.VK_NUMPAD1     = 0x61
VIRTUAL_KEY_CODE.VK_NUMPAD2     = 0x62
VIRTUAL_KEY_CODE.VK_NUMPAD3     = 0x63
VIRTUAL_KEY_CODE.VK_NUMPAD4     = 0x64
VIRTUAL_KEY_CODE.VK_NUMPAD5     = 0x65
VIRTUAL_KEY_CODE.VK_NUMPAD6     = 0x66
VIRTUAL_KEY_CODE.VK_NUMPAD7     = 0x67
VIRTUAL_KEY_CODE.VK_NUMPAD8     = 0x68
VIRTUAL_KEY_CODE.VK_NUMPAD9     = 0x69
VIRTUAL_KEY_CODE.VK_MULTIPLY    = 0x6a
VIRTUAL_KEY_CODE.VK_ADD         = 0x6b
VIRTUAL_KEY_CODE.VK_SEPARATOR   = 0x6c
VIRTUAL_KEY_CODE.VK_SUBTRACT    = 0x6d
VIRTUAL_KEY_CODE.VK_DECIMAL     = 0x6e
VIRTUAL_KEY_CODE.VK_DIVIDE      = 0x6f
VIRTUAL_KEY_CODE.VK_F1          = 0x70
VIRTUAL_KEY_CODE.VK_F2          = 0x71
VIRTUAL_KEY_CODE.VK_F3          = 0x72
VIRTUAL_KEY_CODE.VK_F4          = 0x73
VIRTUAL_KEY_CODE.VK_F5          = 0x74
VIRTUAL_KEY_CODE.VK_F6          = 0x75
VIRTUAL_KEY_CODE.VK_F7          = 0x76
VIRTUAL_KEY_CODE.VK_F8          = 0x77
VIRTUAL_KEY_CODE.VK_F9          = 0x78
VIRTUAL_KEY_CODE.VK_F10         = 0x79
VIRTUAL_KEY_CODE.VK_F11         = 0x7a
VIRTUAL_KEY_CODE.VK_F12         = 0x7b
VIRTUAL_KEY_CODE.VK_F13         = 0x7c
VIRTUAL_KEY_CODE.VK_F14         = 0x7d
VIRTUAL_KEY_CODE.VK_F15         = 0x7e
VIRTUAL_KEY_CODE.VK_F16         = 0x7f
VIRTUAL_KEY_CODE.VK_F17         = 0x80
VIRTUAL_KEY_CODE.VK_F18         = 0x81
VIRTUAL_KEY_CODE.VK_F19         = 0x82
VIRTUAL_KEY_CODE.VK_F20         = 0x83
VIRTUAL_KEY_CODE.VK_F21         = 0x84
VIRTUAL_KEY_CODE.VK_F22         = 0x85
VIRTUAL_KEY_CODE.VK_F23         = 0x86
VIRTUAL_KEY_CODE.VK_F24         = 0x87
# 0x88-0x8f: unassigned
VIRTUAL_KEY_CODE.VK_NUMLOCK     = 0x90
VIRTUAL_KEY_CODE.VK_SCROLL      = 0x91
# 0x92-0x96: OEM specific
# 0x97-0x9f: unassigned
VIRTUAL_KEY_CODE.VK_LSHIFT      = 0xa0
VIRTUAL_KEY_CODE.VK_RSHIFT      = 0xa1
VIRTUAL_KEY_CODE.VK_LCONTROL    = 0xa2
VIRTUAL_KEY_CODE.VK_RCONTROL    = 0xa3
VIRTUAL_KEY_CODE.VK_LMENU       = 0xa4
VIRTUAL_KEY_CODE.VK_RMENU       = 0xa5
VIRTUAL_KEY_CODE.VK_BROWSER_BACK = 0xa6
VIRTUAL_KEY_CODE.VK_BROWSER_FORWARD = 0xa7
VIRTUAL_KEY_CODE.VK_BROWSER_REFRESH = 0xa8
VIRTUAL_KEY_CODE.VK_BROWSER_STOP = 0xa9
VIRTUAL_KEY_CODE.VK_BROWSER_SEARCH = 0xaa
VIRTUAL_KEY_CODE.VK_BROWSER_FAVORITES = 0xab
VIRTUAL_KEY_CODE.VK_BROWSER_HOME = 0xac
VIRTUAL_KEY_CODE.VK_VOLUME_MUTE = 0xad
VIRTUAL_KEY_CODE.VK_VOLUME_DOWN = 0xae
VIRTUAL_KEY_CODE.VK_VOLUME_UP   = 0xaf
VIRTUAL_KEY_CODE.VK_MEDIA_NEXT_TRACK = 0xb0
VIRTUAL_KEY_CODE.VK_MEDIA_PREV_TRACK = 0xb1
VIRTUAL_KEY_CODE.VK_MEDIA_STOP  = 0xb2
VIRTUAL_KEY_CODE.VK_MEDIA_PLAY_PAUSE = 0xb3
VIRTUAL_KEY_CODE.VK_LAUNCH_MAIL = 0xb4
VIRTUAL_KEY_CODE.VK_LAUNCH_MEDIA_SELECT = 0xb5
VIRTUAL_KEY_CODE.VK_LAUNCH_APP1 = 0xb6
VIRTUAL_KEY_CODE.VK_LAUNCH_APP2 = 0xb7
# 0xb8-0xb9: reserved
VIRTUAL_KEY_CODE.VK_OEM_1       = 0xba
VIRTUAL_KEY_CODE.VK_OEM_PLUS    = 0xbb
VIRTUAL_KEY_CODE.VK_OEM_COMMA   = 0xbc
VIRTUAL_KEY_CODE.VK_OEM_MINUS   = 0xbd
VIRTUAL_KEY_CODE.VK_OEM_PERIOD  = 0xbe
VIRTUAL_KEY_CODE.VK_OEM_2       = 0xbf
VIRTUAL_KEY_CODE.VK_OEM_3       = 0xc0
# 0xc1-0xd7: reserved
# 0xd8-0xda: unassigned
VIRTUAL_KEY_CODE.VK_OEM_4       = 0xdb
VIRTUAL_KEY_CODE.VK_OEM_5       = 0xdc
VIRTUAL_KEY_CODE.VK_OEM_6       = 0xdd
VIRTUAL_KEY_CODE.VK_OEM_7       = 0xde
VIRTUAL_KEY_CODE.VK_OEM_8       = 0xdf
# 0xe0: reserved
# 0xe1: OEM specific
VIRTUAL_KEY_CODE.VK_OEM_102     = 0xe2
# 0xe3-0xe4: OEM specific
VIRTUAL_KEY_CODE.VK_PROCESSKEY  = 0xe5
# 0xe6: OEM specific
VIRTUAL_KEY_CODE.VK_PACKET      = 0xe7
# 0xe8: unassigned
# 0xe9-0xf5: OEM specific
VIRTUAL_KEY_CODE.VK_ATTN        = 0xf6
VIRTUAL_KEY_CODE.VK_CRSEL       = 0xf7
VIRTUAL_KEY_CODE.VK_EXSEL       = 0xf8
VIRTUAL_KEY_CODE.VK_EREOF       = 0xf9
VIRTUAL_KEY_CODE.VK_PLAY        = 0xfa
VIRTUAL_KEY_CODE.VK_ZOOM        = 0xfb
VIRTUAL_KEY_CODE.VK_NONAME      = 0xfc
VIRTUAL_KEY_CODE.VK_PA1         = 0xfd
VIRTUAL_KEY_CODE.VK_OEM_CLEAR   = 0xfe

#printable keys for US keyboard 
# tuples of (base, shift-modified)
VIRTUAL_KEY_CODE_US_MAPPING = {
    VIRTUAL_KEY_CODE.VK_RETURN  : ('\n', '\n'),
    VIRTUAL_KEY_CODE.VK_SPACE   : (' ', ' '),
    VIRTUAL_KEY_CODE.VK_0       : ('0', ')'),
    VIRTUAL_KEY_CODE.VK_1       : ('1', '!'),
    VIRTUAL_KEY_CODE.VK_2       : ('2', '@'),
    VIRTUAL_KEY_CODE.VK_3       : ('3', '#'),
    VIRTUAL_KEY_CODE.VK_4       : ('4', '$'),
    VIRTUAL_KEY_CODE.VK_5       : ('5', '%'),
    VIRTUAL_KEY_CODE.VK_6       : ('6', '^'),
    VIRTUAL_KEY_CODE.VK_7       : ('7', '&'),
    VIRTUAL_KEY_CODE.VK_8       : ('8', '*'),
    VIRTUAL_KEY_CODE.VK_9       : ('9', '('),
    VIRTUAL_KEY_CODE.VK_OEM_1   : (';', ':'),
    VIRTUAL_KEY_CODE.VK_OEM_PLUS    : ('=', '+'),
    VIRTUAL_KEY_CODE.VK_OEM_COMMA   : (',', '<'),
    VIRTUAL_KEY_CODE.VK_OEM_MINUS   : ('-', '_'),
    VIRTUAL_KEY_CODE.VK_OEM_PERIOD  : ('.', '>'),
    VIRTUAL_KEY_CODE.VK_OEM_2   : ('/', '?'),
    VIRTUAL_KEY_CODE.VK_OEM_3   : ('`', '~'),
    VIRTUAL_KEY_CODE.VK_OEM_4   : ('[', '{'),
    VIRTUAL_KEY_CODE.VK_OEM_5   : ('\\', '|'),
    VIRTUAL_KEY_CODE.VK_OEM_6   : (']', '}'),
    VIRTUAL_KEY_CODE.VK_OEM_7   : ("'", '"'),
    VIRTUAL_KEY_CODE.VK_OEM_8   : ('!', None), #section symbol &sect;
    VIRTUAL_KEY_CODE.VK_A       : ('a', 'A'),
    VIRTUAL_KEY_CODE.VK_B       : ('b', 'B'),
    VIRTUAL_KEY_CODE.VK_C       : ('c', 'C'),
    VIRTUAL_KEY_CODE.VK_D       : ('d', 'D'),
    VIRTUAL_KEY_CODE.VK_E       : ('e', 'E'),
    VIRTUAL_KEY_CODE.VK_F       : ('f', 'F'),
    VIRTUAL_KEY_CODE.VK_G       : ('g', 'G'),
    VIRTUAL_KEY_CODE.VK_H       : ('h', 'H'),
    VIRTUAL_KEY_CODE.VK_I       : ('i', 'I'),
    VIRTUAL_KEY_CODE.VK_J       : ('j', 'J'),
    VIRTUAL_KEY_CODE.VK_K       : ('k', 'K'),
    VIRTUAL_KEY_CODE.VK_L       : ('l', 'L'),
    VIRTUAL_KEY_CODE.VK_M       : ('m', 'M'),
    VIRTUAL_KEY_CODE.VK_N       : ('n', 'N'),
    VIRTUAL_KEY_CODE.VK_O       : ('o', 'O'),
    VIRTUAL_KEY_CODE.VK_P       : ('p', 'P'),
    VIRTUAL_KEY_CODE.VK_Q       : ('q', 'Q'),
    VIRTUAL_KEY_CODE.VK_R       : ('r', 'R'),
    VIRTUAL_KEY_CODE.VK_S       : ('s', 'S'),
    VIRTUAL_KEY_CODE.VK_T       : ('t', 'T'),
    VIRTUAL_KEY_CODE.VK_U       : ('u', 'U'),
    VIRTUAL_KEY_CODE.VK_V       : ('v', 'V'),
    VIRTUAL_KEY_CODE.VK_W       : ('w', 'W'),
    VIRTUAL_KEY_CODE.VK_X       : ('x', 'X'),
    VIRTUAL_KEY_CODE.VK_Y       : ('y', 'Y'),
    VIRTUAL_KEY_CODE.VK_Z       : ('z', 'Z'),
}

