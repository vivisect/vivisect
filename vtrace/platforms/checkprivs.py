import os
from ctypes import *

if os.name == 'nt':
    from ctypes.wintypes import *

    TOKEN_QUERY = 8
    TOKEN_ADJUST_PRIVILEGES = 32

    def ErrorIfZero(handle):
        if handle == 0:
            raise WinError()
        else:
            return handle
        
    class LUID(Structure):
        _fields_ = (('LowPart', DWORD),
                    ('HighPart', LONG))
        @property
        def value(self):
            return ctypes.c_longlong.from_buffer(self).value

        @value.setter
        def value(self, v):
            ctypes.c_longlong.from_buffer(self).value = v
            
    class TOKEN_PRIVILEGES( Structure ):
        _fields_ = [
                ('PrivilegeCount',  c_uint),
                ('Luid',            LUID),
                ('Attributes',      c_uint) ]

    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess

    OpenProcessToken = windll.advapi32.OpenProcessToken
    OpenProcessToken.argtypes = [
        c_int,      # HANDLE ProcessHandle
        c_uint,     # DWORD DesiredAccess
        c_void_p ]  # PHANDLE TokenHandle
    OpenProcessToken.restype = ErrorIfZero

    AdjustTokenPrivileges = windll.advapi32.AdjustTokenPrivileges
    AdjustTokenPrivileges.argtypes = [
        c_int,      # HANDLE TokenHandle
        c_int,      # BOOL DisableAllPrivileges
        c_void_p,   # PTOKEN_PRIVILEGES NewState
        c_uint,     # DWORD BufferLength
        c_void_p,   # PTOKEN_PRIVILEGES PreviousState
        c_void_p ]  # PDWORD ReturnLength
    AdjustTokenPrivileges.restype = ErrorIfZero

    LookupPrivilegeValue = windll.advapi32.LookupPrivilegeValueA
    LookupPrivilegeValue.argtypes = [
    c_char_p,   # LPCTSTR lpSystemName
    c_char_p,   # LPCTSTR lpName
    c_void_p ]  # PLUID lpLuid
    LookupPrivilegeValue.restype = ErrorIfZero


    from . import winadmin
    print("Checking Admin Privs")
    if not winadmin.isUserAdmin():
        print("Nope!")
        winadmin.runAsAdmin()
            
    def ElevatePrivs():
        # do the work
        access_token = c_int(0)
        privileges = TOKEN_PRIVILEGES()

        OpenProcessToken( -1, TOKEN_QUERY | TOKEN_ADJUST_PRIVILEGES, byref(access_token) )
        #OpenProcessToken( GetCurrentProcess(), TOKEN_QUERY | TOKEN_ADJUST_PRIVILEGES, byref(access_token) )
        access_token = access_token.value
        LookupPrivilegeValue( None, "SeDebugPrivilege", byref(privileges.Luid) )
        privileges.PrivilegeCount = 1
        privileges.Attributes = 2
        AdjustTokenPrivileges(
                access_token,
                0,
                byref(privileges),
                0,
                None,
                None )
        CloseHandle( access_token )

