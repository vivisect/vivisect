import ctypes
from ctypes.util import find_library

libc = ctypes.CDLL( find_library('c') )

namelen = 256
class utsname(ctypes.Structure):
    _fields_ = (
        ('sysname',  ctypes.c_char * namelen),
        ('nodename', ctypes.c_char * namelen),
        ('release',  ctypes.c_char * namelen),
        ('version',  ctypes.c_char * namelen),
        ('machine',  ctypes.c_char * namelen),
    )

def uname():
    u = utsname()
    libc.uname( ctypes.byref(u) )
    return u

macarchs = {'x86_64':'amd64','i386':'i386'}

def getHostInfo():
    '''
    Retrieve info for vivisect.lib.thishost.
    '''
    ret = {'platform':'darwin'}

    u = uname()

    verstr = u.release.decode('ascii')
    ret['version'] = tuple([ int(p) for p in verstr.split('.') ])

    machstr = u.machine.decode('ascii')
    ret['arch'] = macarchs.get(machstr)

    return ret
