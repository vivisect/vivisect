'''
The pre-made windows structure defs (extracted from pdb syms)
'''

# TODO: This belongs *not* in an init module
import envi
import ctypes
import platform


def isSysWow64():
    k32 = ctypes.windll.kernel32
    if not hasattr(k32, 'IsWow64Process'):
        return False
    ret = ctypes.c_ulong(0)
    myproc = ctypes.c_size_t(-1)
    if not k32.IsWow64Process(myproc, ctypes.addressof(ret)):
        return False
    return bool(ret.value)


def getCurrentDef(normname):
    bname, wver, stuff, whichkern = platform.win32_ver()
    wvertup = wver.split('.')
    arch = envi.getCurrentArch()
    if isSysWow64():
        arch = 'wow64'

    modname = 'vstruct.defs.windows.win_%s_%s_%s.%s' % (wvertup[0], wvertup[1], arch, normname)

    try:
        mod = __import__(modname, {}, {}, 1)
    except ImportError:
        mod = None

    if mod is None:
        modname = 'vstruct.defs.windows.win_%s_%s_%s.%s' % (6, 3, arch, normname)

    try:
        mod = __import__(modname, {}, {}, 1)
    except ImportError:
        mod = None

    return mod
