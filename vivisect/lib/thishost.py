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
    for key,val in reqinfo.items():
        cur = hostinfo.get(key)
        if cur != val:
            raise Exception('thishost: %s=%s required (is: %s=%s)' % (key,val,key,cur))

def check(**reqinfo):
    for key,val in reqinfo.items():
        cur = hostinfo.get(key)
        if cur != val:
            return False
    return True
