'''
Functions for normalizing platform/architecture detection.
'''
import struct
import platform

def arch():
    p = plat()
    # FIXME per-platform arch detection

plat_xlate = {
    'microsoft':'windows',
}
def plat():
    '''
    Returns a normalized platform name.

    Currently detected platforms:

    * windows
    * darwin
    * linux

    # FIXME
    # freebsd
    # solaris
    '''
    plat = platform.system().lower()
    return plat_xlate.get(plat,plat)
