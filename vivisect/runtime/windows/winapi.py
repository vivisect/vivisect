import ctypes

NULL    = 0
BYTE    = ctypes.c_ubyte
BOOL    = ctypes.c_ulong
WORD    = ctypes.c_ushort
DWORD   = ctypes.c_ulong
QWORD   = ctypes.c_ulonglong
WCHAR   = ctypes.c_wchar
LPVOID  = ctypes.c_size_t
HANDLE  = LPVOID
SIZE_T  = LPVOID
DWORD_PTR   = ctypes.c_size_t

PCHAR   = ctypes.c_char_p

INFINITE = 0xffffffff
EXCEPTION_MAXIMUM_PARAMETERS = 15

# Debug Event Types
EXCEPTION_DEBUG_EVENT       =1
CREATE_THREAD_DEBUG_EVENT   =2
CREATE_PROCESS_DEBUG_EVENT  =3
EXIT_THREAD_DEBUG_EVENT     =4
EXIT_PROCESS_DEBUG_EVENT    =5
LOAD_DLL_DEBUG_EVENT        =6
UNLOAD_DLL_DEBUG_EVENT      =7
OUTPUT_DEBUG_STRING_EVENT   =8
RIP_EVENT                   =9

# Symbol Flags
SYMFLAG_VALUEPRESENT     = 0x00000001
SYMFLAG_REGISTER         = 0x00000008
SYMFLAG_REGREL           = 0x00000010
SYMFLAG_FRAMEREL         = 0x00000020
SYMFLAG_PARAMETER        = 0x00000040
SYMFLAG_LOCAL            = 0x00000080
SYMFLAG_CONSTANT         = 0x00000100
SYMFLAG_EXPORT           = 0x00000200
SYMFLAG_FORWARDER        = 0x00000400
SYMFLAG_FUNCTION         = 0x00000800
SYMFLAG_VIRTUAL          = 0x00001000
SYMFLAG_THUNK            = 0x00002000
SYMFLAG_TLSREL           = 0x00004000

# Symbol Resolution Options
SYMOPT_CASE_INSENSITIVE         = 0x00000001
SYMOPT_UNDNAME                  = 0x00000002
SYMOPT_DEFERRED_LOADS           = 0x00000004
SYMOPT_NO_CPP                   = 0x00000008
SYMOPT_LOAD_LINES               = 0x00000010
SYMOPT_OMAP_FIND_NEAREST        = 0x00000020
SYMOPT_LOAD_ANYTHING            = 0x00000040
SYMOPT_IGNORE_CVREC             = 0x00000080
SYMOPT_NO_UNQUALIFIED_LOADS     = 0x00000100
SYMOPT_FAIL_CRITICAL_ERRORS     = 0x00000200
SYMOPT_EXACT_SYMBOLS            = 0x00000400
SYMOPT_ALLOW_ABSOLUTE_SYMBOLS   = 0x00000800
SYMOPT_IGNORE_NT_SYMPATH        = 0x00001000
SYMOPT_INCLUDE_32BIT_MODULES    = 0x00002000
SYMOPT_PUBLICS_ONLY             = 0x00004000
SYMOPT_NO_PUBLICS               = 0x00008000
SYMOPT_AUTO_PUBLICS             = 0x00010000
SYMOPT_NO_IMAGE_SEARCH          = 0x00020000
SYMOPT_SECURE                   = 0x00040000
SYMOPT_NO_PROMPTS               = 0x00080000
SYMOPT_OVERWRITE                = 0x00100000
SYMOPT_DEBUG                    = 0x80000000

# Exception Types
EXCEPTION_WAIT_0                  = 0x00000000
EXCEPTION_ABANDONED_WAIT_0        = 0x00000080
EXCEPTION_USER_APC                = 0x000000c0
EXCEPTION_TIMEOUT                 = 0x00000102
EXCEPTION_PENDING                 = 0x00000103
DBG_EXCEPTION_HANDLED             = 0x00010001
DBG_CONTINUE                      = 0x00010002
EXCEPTION_SEGMENT_NOTIFICATION    = 0x40000005
DBG_TERMINATE_THREAD              = 0x40010003
DBG_TERMINATE_PROCESS             = 0x40010004
DBG_CONTROL_C                     = 0x40010005
DBG_CONTROL_BREAK                 = 0x40010008
DBG_COMMAND_EXCEPTION             = 0x40010009
EXCEPTION_GUARD_PAGE_VIOLATION       = 0x80000001
EXCEPTION_DATATYPE_MISALIGNMENT      = 0x80000002
EXCEPTION_BREAKPOINT                 = 0x80000003
STATUS_WX86_BREAKPOINT               = 0x4000001f
EXCEPTION_SINGLE_STEP                = 0x80000004
STATUS_WX86_SINGLE_STEP              = 0x4000001e
DBG_EXCEPTION_NOT_HANDLED            = 0x80010001
STATUS_BUFFER_OVERFLOW               = 0x80000005
STATUS_SUCCESS                       = 0x00000000
STATUS_INFO_LENGTH_MISMATCH          = 0xc0000004
EXCEPTION_ACCESS_VIOLATION           = 0xc0000005
EXCEPTION_IN_PAGE_ERROR              = 0xc0000006
EXCEPTION_INVALID_HANDLE             = 0xc0000008
EXCEPTION_NO_MEMORY                  = 0xc0000017
EXCEPTION_ILLEGAL_INSTRUCTION        = 0xc000001d
EXCEPTION_NONCONTINUABLE_EXCEPTION   = 0xc0000025
EXCEPTION_INVALID_DISPOSITION        = 0xc0000026
EXCEPTION_ARRAY_BOUNDS_EXCEEDED      = 0xc000008c
EXCEPTION_FLOAT_DENORMAL_OPERAND     = 0xc000008D
EXCEPTION_FLOAT_DIVIDE_BY_ZERO       = 0xc000008e
EXCEPTION_FLOAT_INEXACT_RESULT       = 0xc000008f
EXCEPTION_FLOAT_INVALID_OPERATION    = 0xc0000090
EXCEPTION_FLOAT_OVERFLOW             = 0xc0000091
EXCEPTION_FLOAT_STACK_CHECK          = 0xc0000092
EXCEPTION_FLOAT_UNDERFLOW            = 0xc0000093
EXCEPTION_INTEGER_DIVIDE_BY_ZERO     = 0xc0000094
EXCEPTION_INTEGER_OVERFLOW           = 0xc0000095
EXCEPTION_PRIVILEGED_INSTRUCTION     = 0xc0000096
EXCEPTION_STACK_OVERFLOW             = 0xc00000fd
EXCEPTION_CONTROL_C_EXIT             = 0xc000013a
EXCEPTION_FLOAT_MULTIPLE_FAULTS      = 0xc00002b4
EXCEPTION_FLOAT_MULTIPLE_TRAPS       = 0xc00002b5
EXCEPTION_REG_NAT_CONSUMPTION        = 0xc00002c9

# Context Info
CONTEXT_i386    = 0x00010000    # this assumes that i386 and
CONTEXT_i486    = 0x00010000    # i486 have identical context records
CONTEXT_AMD64   = 0x00100000    # For amd x64...

CONTEXT_CONTROL         = 0x00000001 # SS:SP, CS:IP, FLAGS, BP
CONTEXT_INTEGER         = 0x00000002 # AX, BX, CX, DX, SI, DI
CONTEXT_SEGMENTS        = 0x00000004 # DS, ES, FS, GS
CONTEXT_FLOATING_POINT  = 0x00000008 # 387 state
CONTEXT_DEBUG_REGISTERS = 0x00000010 # DB 0-3,6,7
CONTEXT_EXTENDED_REGISTERS  = 0x00000020 # cpu specific extensions
CONTEXT_FULL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS)
CONTEXT_ALL = (CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS | CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS | CONTEXT_EXTENDED_REGISTERS)


# Thread Permissions
THREAD_ALL_ACCESS   = 0x001f03ff
PROCESS_ALL_ACCESS  = 0x001f0fff

# NtQueryInformationProcess classes
ProcessBasicInformation     = 0
ProcessDebugPort            = 7
ProcessWow64Information     = 26
ProcessImageFileName        = 27
ProcessBreakOnTermination   = 29

# Memory Permissions
PAGE_NOACCESS           = 0x01
PAGE_READONLY           = 0x02
PAGE_READWRITE          = 0x04
PAGE_WRITECOPY          = 0x08
PAGE_EXECUTE            = 0x10
PAGE_EXECUTE_READ       = 0x20
PAGE_EXECUTE_READWRITE  = 0x40
PAGE_EXECUTE_WRITECOPY  = 0x80
PAGE_GUARD              = 0x100
PAGE_NOCACHE            = 0x200
PAGE_WRITECOMBINE       = 0x400

SE_PRIVILEGE_ENABLED    = 0x00000002
TOKEN_ADJUST_PRIVILEGES = 0x00000020
TOKEN_QUERY             = 0x00000008
dbgprivdone = False

# TOKEN_INFORMATION_CLASS
TokenUser                   = 1
TokenGroups                 = 2
TokenPrivileges             = 3
TokenOwner                  = 4
TokenPrimaryGroup           = 5
TokenDefaultDacl            = 6
TokenSource                 = 7
TokenType                   = 8
TokenImpersonationLevel     = 9
TokenStatistics             = 10
TokenRestrictedSids         = 11
TokenSessionId              = 12
TokenGroupsAndPrivileges    = 13
TokenSessionReference       = 14
TokenSandBoxInert           = 15
TokenAuditPolicy            = 16
TokenOrigin                 = 17
TokenElevationType          = 18
TokenLinkedToken            = 19
TokenElevation              = 20
TokenHasRestrictions        = 21
TokenAccessInformation      = 22
TokenVirtualizationAllowed  = 23
TokenVirtualizationEnabled  = 24
TokenIntegrityLevel         = 25
TokenUIAccess               = 26
TokenMandatoryPolicy        = 27
TokenLogonSid               = 28
MaxTokenInfoClass           = 29

# TOKEN_ELEVATION_TYPE
TokenElevationTypeDefault   = 1
TokenElevationTypeFull      = 2
TokenElevationTypeLimited   = 3

# FIXME maybe this goes in plats?
PROCESSOR_ARCHITECTURE_INTEL            = 0
PROCESSOR_ARCHITECTURE_MIPS             = 1
PROCESSOR_ARCHITECTURE_ALPHA            = 2
PROCESSOR_ARCHITECTURE_PPC              = 3
PROCESSOR_ARCHITECTURE_SHX              = 4
PROCESSOR_ARCHITECTURE_ARM              = 5
PROCESSOR_ARCHITECTURE_IA64             = 6
PROCESSOR_ARCHITECTURE_ALPHA64          = 7
PROCESSOR_ARCHITECTURE_MSIL             = 8
PROCESSOR_ARCHITECTURE_AMD64            = 9
PROCESSOR_ARCHITECTURE_IA32_ON_WIN64    = 10
PROCESSOR_ARCHITECTURE_UNKNOWN          = 0xFFFF

ntdll = ctypes.windll.ntdll
psapi = ctypes.windll.psapi
advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32

kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE
kernel32.CreateProcessA.argtypes = [LPVOID, PCHAR, LPVOID, LPVOID, ctypes.c_uint, DWORD, LPVOID, LPVOID, LPVOID, LPVOID]
kernel32.ReadProcessMemory.argtypes = [HANDLE, LPVOID, LPVOID, SIZE_T, LPVOID]
kernel32.WriteProcessMemory.argtypes = [HANDLE, LPVOID, PCHAR, SIZE_T, LPVOID]
kernel32.GetThreadContext.argtypes = [HANDLE, LPVOID]
kernel32.SetThreadContext.argtypes = [HANDLE, LPVOID]
kernel32.CreateRemoteThread.argtypes = [HANDLE, LPVOID, SIZE_T, LPVOID, LPVOID, DWORD, LPVOID]
kernel32.SuspendThread.argtypes = [HANDLE,]
kernel32.ResumeThread.argtypes = [HANDLE,]
kernel32.VirtualQueryEx.argtypes = [HANDLE, LPVOID, LPVOID, SIZE_T]
kernel32.DebugBreakProcess.argtypes = [HANDLE,]
kernel32.CloseHandle.argtypes = [HANDLE,]
kernel32.GetLogicalDriveStringsA.argtypes = [DWORD, LPVOID]
kernel32.TerminateProcess.argtypes = [HANDLE, DWORD]
kernel32.VirtualProtectEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, LPVOID]
kernel32.VirtualAllocEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, DWORD]
kernel32.VirtualAllocEx.restype = LPVOID
kernel32.VirtualFreeEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD]
kernel32.DuplicateHandle.argtypes = [HANDLE, HANDLE, HANDLE, LPVOID, DWORD, DWORD, DWORD]
kernel32.SetEvent.argtypes = [HANDLE, ]
kernel32.FormatMessageW.argtypes = [DWORD, LPVOID, DWORD, DWORD, LPVOID, DWORD, LPVOID]

IsWow64Process = getattr(kernel32, 'IsWow64Process', None)
if IsWow64Process != None:
    IsWow64Process.argtypes = [HANDLE, LPVOID]


psapi.GetModuleFileNameExW.argtypes = [HANDLE, HANDLE, LPVOID, DWORD]
psapi.GetMappedFileNameW.argtypes = [HANDLE, LPVOID, LPVOID, DWORD]
psapi.EnumProcesses.argtypes = [LPVOID, DWORD, LPVOID]
psapi.EnumProcesses.restype = BOOL
psapi.EnumProcessModules.argtypes = [ HANDLE, LPVOID, DWORD, LPVOID ]
psapi.EnumProcessModules.restype = BOOL

ntdll.NtQuerySystemInformation.argtypes = [DWORD, LPVOID, DWORD, LPVOID]
ntdll.NtQueryObject.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID]
ntdll.NtQueryObject.restype = DWORD
ntdll.NtQueryInformationProcess.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID]
ntdll.NtSystemDebugControl.restype = SIZE_T
ntdll.NtQueryInformationProcess.argtypes = [ HANDLE, DWORD, LPVOID, DWORD, LPVOID ]
#ntdll.NtQueryInformationProcess.restype = NTSTATUS

advapi32.LookupPrivilegeValueA.argtypes = [LPVOID, PCHAR, LPVOID]
advapi32.OpenProcessToken.argtypes = [HANDLE, DWORD, HANDLE]
advapi32.AdjustTokenPrivileges.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID, LPVOID]
advapi32.OpenSCManagerA.argtypes = [ LPVOID, LPVOID, DWORD ]
advapi32.OpenSCManagerA.restype = HANDLE
advapi32.EnumServicesStatusExW.argtypes = [ HANDLE,
                                            LPVOID,
                                            DWORD,
                                            DWORD,
                                            LPVOID,
                                            DWORD,
                                            LPVOID,
                                            LPVOID,
                                            LPVOID,
                                            LPVOID ]
advapi32.EnumServicesStatusExW.restype = BOOL
advapi32.CloseServiceHandle.argtypes = [ HANDLE, ]
advapi32.CloseServiceHandle.restype = BOOL
advapi32.GetTokenInformation.argtypes = [HANDLE, DWORD, LPVOID, DWORD, LPVOID]
advapi32.GetTokenInformation.restype = BOOL

class OSVERSIONINFO(ctypes.Structure):
    _fields_ = (
        ('dwOsVersionInfoSize',DWORD),
        ('dwMajorVersion',DWORD),
        ('dwMinorVersion',DWORD),
        ('dwBuildNumber',DWORD),
        ('dwPlatformId',DWORD),
        ('szCSDVersion', WCHAR * 128),
    )

class SYSTEM_INFO(ctypes.Structure):
    _fields_ = (
        ('wProcessorArchitecture',WORD),
        ('wReserved',WORD),
        ('dwPageSize',DWORD),
        ('lpMinimunApplicationAddress',LPVOID),
        ('lpMaximumApplicationAddress',LPVOID),
        ('dwActiveProcessorMask',DWORD_PTR),
        ('dwNumberOfProcessors',DWORD),
        ('dwProcessorType',DWORD),
        ('dwAllocationGranularity',DWORD),
        ('wProcessorLevel',WORD),
        ('wProcessorRevision',WORD),
    )

class PROCESS_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = (
        ('Reserved1',LPVOID),
        ('PebBaseAddress',LPVOID),
        ('Res1',LPVOID),
        ('Res2',LPVOID),
        ('UniqueProcessId',DWORD_PTR),
        ('Res3',LPVOID),
    )

def GetVersionEx():
    '''
    Use kernel32.GetVersionExW to populate and return OSVERSIONINFO()
    '''
    info = OSVERSIONINFO()
    info.dwOsVersionInfoSize = ctypes.sizeof(OSVERSIONINFO)
    if not kernel32.GetVersionExW( ctypes.byref( info ) ):
        raise ctypes.WinError()
    return info

def GetSystemInfo():
    '''
    Use kernel32.GetSystemInfo to populate and return SYSTEM_INFO()
    '''
    info = SYSTEM_INFO()
    kernel32.GetSystemInfo( ctypes.byref( info ) )
    return info

