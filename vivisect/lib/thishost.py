'''
Functions for normalizing platform/architecture detection.
'''
import ctypes
from ctypes.util import find_library

def getHostInfo():

    ret = {}
    ret['ptrsize'] = ctypes.sizeof( ctypes.c_void_p )

    if getattr(ctypes,'windll',None):
        ret['platform'] = 'windows'
        return ret

    libc = ctypes.CDLL( find_library('c') )
    if getattr(libc,'mach_vm_read',None):

        ret['platform'] = 'darwin'

        namelen = 256
        class utsname(ctypes.Structure):
            _fields_ = [
                ('sysname',  ctypes.c_char * namelen),
                ('nodename', ctypes.c_char * namelen),
                ('release',  ctypes.c_char * namelen),
                ('version',  ctypes.c_char * namelen),
                ('machine',  ctypes.c_char * namelen),
            ]

        u = utsname()
        libc.uname( ctypes.byref(u) )

        verstr = u.release.decode('ascii')
        ret['version'] = tuple([ int(p) for p in verstr.split('.') ])

        macarchs = {'x86_64':'amd64','i386':'i386'}

        machstr = u.machine.decode('ascii')
        ret['arch'] = macarchs.get(machstr)

        return ret

    return ret

hostinfo = getHostInfo()
locals().update( hostinfo )

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
