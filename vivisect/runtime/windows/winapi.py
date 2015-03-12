import ctypes

from vivisect.plats.windows.winnt import *

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

