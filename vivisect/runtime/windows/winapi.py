import ctypes

from vivisect.platforms.windows.winnt import *

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
PWCHAR  = ctypes.c_wchar_p

ntdll = ctypes.windll.ntdll
psapi = ctypes.windll.psapi
advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32

kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE
kernel32.CreateProcessW.argtypes = [LPVOID, PWCHAR, LPVOID, LPVOID, DWORD, DWORD, LPVOID, LPVOID, LPVOID, LPVOID]
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

psapi.GetModuleFileNameExW.argtypes = [HANDLE, HANDLE, PWCHAR, DWORD]
psapi.GetMappedFileNameW.argtypes = [HANDLE, LPVOID, PWCHAR, DWORD]
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

advapi32.LookupPrivilegeValueW.argtypes = [LPVOID, PWCHAR, LPVOID]
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

class LUID(ctypes.Structure):
    _fields_ = (
        ("LowPart", DWORD),
        ("HighPart", DWORD)
    )

class TOKEN_PRIVILEGES(ctypes.Structure):
    # only for single priv use
    _fields_ = (
        ('PrivilegeCount',      DWORD),
        ('Privilege',           LUID),
        ('PrivilegeAttribute',  DWORD),
    )

class SERVICE_STATUS_PROCESS(ctypes.Structure):
    _fields_ = [
            ('dwServiceType', DWORD),
            ('dwCurrentState', DWORD),
            ('dwControlsAccepted', DWORD),
            ('dwWin32ExitCode', DWORD),
            ('dwServiceSpecificExitCode',DWORD),
            ('dwCheckPoint', DWORD),
            ('dwWaitHint', DWORD),
            ('dwProcessId', DWORD),
            ('dwServiceFlags', DWORD)
    ]
            
class ENUM_SERVICE_STATUS_PROCESS(ctypes.Structure):
    _fields_ = [
            ('lpServiceName', PWCHAR),
            ('lpDisplayName', PWCHAR),
            ('ServiceStatusProcess', SERVICE_STATUS_PROCESS),
    ]

class EXCEPTION_RECORD(ctypes.Structure):
    _fields_ = (
        ('ExceptionCode',       DWORD),
        ('ExceptionFlags',      DWORD),
        ('ExceptionRecord',     LPVOID),
        ('ExceptionAddress',    LPVOID),
        ('NumberParameters',    DWORD),
        ('ExceptionInformation', LPVOID * EXCEPTION_MAXIMUM_PARAMETERS)
    )

class EXCEPTION_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('ExceptionRecord', EXCEPTION_RECORD),
        ('FirstChance',     DWORD)
    )

class CREATE_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('Thread',          HANDLE),
        ('ThreadLocalBase', LPVOID),
        ('StartAddress',    LPVOID)
    )

class CREATE_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('File', HANDLE),
        ('Process', HANDLE),
        ('Thread', HANDLE),
        ('BaseOfImage', LPVOID),
        ('DebugInfoFileOffset', DWORD),
        ('DebugInfoSize', DWORD),
        ('ThreadLocalBase', LPVOID),
        ('StartAddress', LPVOID),
        ('ImageName', LPVOID),
        ('Unicode', WORD),
    )

class EXIT_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('ExitCode', DWORD),
    )

class EXIT_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('ExitCode', DWORD),
    )

class LOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('File',                HANDLE),
        ('BaseOfDll',           LPVOID),
        ('DebugInfoFileOffset', DWORD),
        ('DebugInfoSize',       DWORD),
        ('ImageName',           LPVOID),
        ('Unicode',             WORD),
    )

class UNLOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = (
        ('BaseOfDll', LPVOID),
    )

class OUTPUT_DEBUG_STRING_INFO(ctypes.Structure):
    _fields_ = (
        ('DebugStringData',     LPVOID),
        ('Unicode',             WORD),
        ('DebugStringLength',   WORD),
    )

class RIP_INFO(ctypes.Structure):
    _fields_ = (
        ('Error',   DWORD),
        ('Type',    DWORD),
    )

class DBG_EVENT_UNION(ctypes.Union):
    _fields_ = ( 
        ('Exception',           EXCEPTION_DEBUG_INFO),
        ('CreateThread',        CREATE_THREAD_DEBUG_INFO),
        ('CreateProcessInfo',   CREATE_PROCESS_DEBUG_INFO),
        ('ExitThread',          EXIT_THREAD_DEBUG_INFO),
        ('ExitProcess',         EXIT_PROCESS_DEBUG_INFO),
        ('LoadDll',             LOAD_DLL_DEBUG_INFO),
        ('UnloadDll',           UNLOAD_DLL_DEBUG_INFO),
        ('DebugString',         OUTPUT_DEBUG_STRING_INFO),
        ('RipInfo',             RIP_INFO),
    )

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = (
        ('DebugEventCode',  DWORD),
        ('ProcessId',       DWORD),
        ('ThreadId',        DWORD),
        ('u',               DBG_EVENT_UNION),
    )

class FloatSavex86(ctypes.Structure):
    _fields_ = (
        ('ControlWord',     DWORD),
        ('StatusWord',      DWORD),
        ('TagWord',         DWORD),
        ('ErrorOffset',     DWORD),
        ('ErrorSelector',   DWORD),
        ('DataOffset',      DWORD),
        ('DataSelector',    DWORD),
        ('RegisterSave',    BYTE*80),
        ('Cr0NpxState',     DWORD),
    )

amd64regs = (
             'cs', 'ds', 'es', 'fs', 'gs', 'ss', 'eflags',
             'debug0', 'debug1', 'debug2', 'debug3', 'debug6', 'debug7',
             'rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi',
             'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'rip',
            )

class CONTEXTx64(ctypes.Structure):
    _fields_ = (

        ('P1Home',QWORD),
        ('P2Home',QWORD),
        ('P3Home',QWORD),
        ('P4Home',QWORD),
        ('P5Home',QWORD),
        ('P6Home',QWORD),

        ('ContextFlags', DWORD),
        ('MxCsr',DWORD),

        ('cs',WORD),
        ('ds',WORD),
        ('es',WORD),
        ('fs', WORD),
        ('gs',WORD),
        ('ss',WORD),
        ('eflags',DWORD),

        ('debug0',QWORD),
        ('debug1',QWORD),
        ('debug2',QWORD),
        ('debug3',QWORD),
        ('debug6',QWORD),
        ('debug7',QWORD),

        ('rax',QWORD),
        ('rcx',QWORD),
        ('rdx',QWORD),
        ('rbx',QWORD),
        ('rsp',QWORD),
        ('rbp',QWORD),
        ('rsi',QWORD),
        ('rdi',QWORD),
        ('r8',QWORD),
        ('r9',QWORD),
        ('r10',QWORD),
        ('r11',QWORD),
        ('r12',QWORD),
        ('r13',QWORD),
        ('r14',QWORD),
        ('r15',QWORD),
        ('rip',QWORD),

        ('foo',QWORD*200),
    )

    def initContextFlags(self):
        self.ContextFlags = (CONTEXT_AMD64 | CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS)

    def getRegDict(self):
        return { r:getattr(self,r,0) for r in amd64regs }

    def setRegDict(self, regdict):
        for name,ctype in self._fields_:
            val = regdict.get(name)
            if val != None:
                setattr(self, name, val)

# Used for xmm registers
class M128A(ctypes.Structure):
    _fields_ = (
            ('Low', QWORD),
            ('High', QWORD),
    )

class ExtendedXmmx86(ctypes.Structure):
    _fields_ = (
            ('Header', M128A * 2),
            ('Legacy', M128A * 8),
            ('_xmm0',   M128A),
            ('_xmm1',   M128A),
            ('_xmm2',   M128A),
            ('_xmm3',   M128A),
            ('_xmm4',   M128A),
            ('_xmm5',   M128A),
            ('_xmm6',   M128A),
            ('_xmm7',   M128A),
            ('Pad', BYTE * 224),
    )

class CONTEXTx86(ctypes.Structure):
    _fields_ = (
        ('ContextFlags', DWORD),
        ('debug0', DWORD),
        ('debug1', DWORD),
        ('debug2', DWORD),
        ('debug3', DWORD),
        ('debug6', DWORD),
        ('debug7', DWORD),
        ('FloatSave', FloatSavex86),
        ('gs', DWORD),
        ('fs', DWORD),
        ('es', DWORD),
        ('ds', DWORD),
        ('edi', DWORD),
        ('esi', DWORD),
        ('ebx', DWORD),
        ('edx', DWORD),
        ('ecx', DWORD),
        ('eax', DWORD),
        ('ebp', DWORD),
        ('eip', DWORD),
        ('cs', DWORD),
        ('eflags', DWORD),
        ('esp', DWORD),
        ('ss', DWORD),

        ('Extension', ExtendedXmmx86),

    )

    def initContextFlags():
        self.ContextFlags = (CONTEXT_i386 | 
                             CONTEXT_FULL | 
                             CONTEXT_DEBUG_REGISTERS |
                             CONTEXT_EXTENDED_REGISTERS)

    #def regPostProcess(self):
        #self.xmm0 = (self.Extension._xmm0.High << 8) + self.Extension._xmm0.Low
        #self.xmm1 = (self.Extension._xmm1.High << 8) + self.Extension._xmm1.Low
        #self.xmm2 = (self.Extension._xmm2.High << 8) + self.Extension._xmm2.Low
        #self.xmm3 = (self.Extension._xmm3.High << 8) + self.Extension._xmm3.Low
        #self.xmm4 = (self.Extension._xmm4.High << 8) + self.Extension._xmm4.Low
        #self.xmm5 = (self.Extension._xmm5.High << 8) + self.Extension._xmm5.Low
        #self.xmm6 = (self.Extension._xmm6.High << 8) + self.Extension._xmm6.Low
        #self.xmm7 = (self.Extension._xmm7.High << 8) + self.Extension._xmm7.Low


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = (
        ('BaseAddress',         SIZE_T),
        ('AllocationBase',      SIZE_T),
        ('AllocationProtect',   DWORD),
        ('RegionSize',          SIZE_T),
        ('State',               DWORD),
        ('Protect',             DWORD),
        ('Type',                DWORD),
    )


class STARTUPINFO(ctypes.Structure):
    _fields_ = (
        ('db',              DWORD),
        ('Reserved',        LPVOID),
        ('Desktop',         LPVOID),
        ('Title',           LPVOID),
        ('X',               DWORD),
        ('Y',               DWORD),
        ('XSize',           DWORD),
        ('YSize',           DWORD),
        ('XCountChars',     DWORD),
        ('YCountChars',     DWORD),
        ('FillAttribute',   DWORD),
        ('Flags',           DWORD),
        ('ShowWindow',      WORD),
        ('Reserved2',       WORD),
        ('Reserved3',       LPVOID),
        ('StdInput',        DWORD),
        ('StdOutput',       DWORD),
        ('StdError',        DWORD),
    )

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = (
        ('Process',     HANDLE),
        ('Thread',      HANDLE),
        ('ProcessId',   DWORD),
        ('ThreadId',    DWORD),
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

def getHostInfo():

    hostinfo = {'platform':'windows','format':'pe'}

    info = GetVersionEx()

    major = info.dwMajorVersion
    minor = info.dwMinorVersion
    build = info.dwBuildNumber
    hostinfo['version'] = ( major, minor, build )

    winarchs = {0:'i386',5:'arm',9:'amd64'}

    info = GetSystemInfo()
    hostinfo['arch'] = winarchs.get( info.wProcessorArchitecture )

    return hostinfo

def getDebugPrivileges():

    dbgluid = LUID()
    token = HANDLE(0)
    tokprivs = TOKEN_PRIVILEGES()

    if not advapi32.LookupPrivilegeValueW(0, 'seDebugPrivilege', ctypes.addressof(dbgluid)):
        print('lookup fail')
        return False

    if not advapi32.OpenProcessToken(-1, TOKEN_ADJUST_PRIVILEGES, ctypes.addressof(token)):
        print('open fail')
        return False

    tokprivs.PrivilegeCount = 1
    tokprivs.Privilege = dbgluid
    tokprivs.PrivilegeAttribute = SE_PRIVILEGE_ENABLED

    if not advapi32.AdjustTokenPrivileges(token, 0, ctypes.addressof(tokprivs), 0, 0, 0):
        print('adjust fail')
        kernel32.CloseHandle(token)
        return False

    kernel32.CloseHandle(token)
    return True
