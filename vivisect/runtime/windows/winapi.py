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

kernel32 = ctypes.windll.kernel32

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
