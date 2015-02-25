'''
Functions for normalizing platform/architecture detection.
'''
import ctypes
from ctypes.util import find_library

hostinfo = {}

def require(**reqinfo):
    '''
    Require a given set of hostinfo values.

    Example:
        import vivisect.lib.thishost as v_thishost

        # this will raise an exception on platforms other
        # than linux.

        v_thishost.require(platform='linux')

    '''
    for key,val in reqinfo.items():
        cur = hostinfo.get(key)
        if cur != val:
            raise Exception('thishost: %s=%s required (is: %s=%s)' % (key,val,key,cur))

def check(**reqinfo):
    '''
    Check a set of values from the current hostinfo.

    Example:
        import vivisect.lib.thishost as v_thishost

        if v_thishost.check(platform='windows',arch='arm'):
            print('on a windows arm device!')
    '''
    for key,val in reqinfo.items():
        cur = hostinfo.get(key)
        if cur != val:
            return False
    return True

def initHostInfo():

    hostinfo['ptrsize'] = ctypes.sizeof( ctypes.c_void_p )

    if getattr(ctypes,'windll',None):
        hostinfo['platform'] = 'windows'

        import vivisect.runtime.windows.winapi as v_winapi
        info = v_winapi.GetVersionEx()

        major = info.dwMajorVersion
        minor = info.dwMinorVersion
        build = info.dwBuildNumber
        hostinfo['version'] = ( major, minor, build )

        winarchs = {0:'i386',5:'arm',9:'amd64'}

        info = v_winapi.GetSystemInfo()
        hostinfo['arch'] = winarchs.get( info.wProcessorArchitecture )

        return

    libc = ctypes.CDLL( find_library('c') )
    if getattr(libc,'mach_vm_read',None):

        import vivisect.runtime.darwin.macapi as v_macapi
        hostinfo.update( v_macapi.hostinfo() )

        return

initHostInfo()
