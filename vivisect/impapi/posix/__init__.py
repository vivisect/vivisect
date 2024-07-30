
# Use the i386 API as the standard set of libc APIs
import vivisect.impapi.posix.i386 as _p386

apitypes = {
    'DWORD':        'unsigned int',
    'HANDLE':       'unsigned long',
}

def getGenericImpApi(arch):
    """
    Return a generic Posix IMPAPI.  This assumes that the Posix calling
    convention name is "<arch>call"
    """
    callconv = '%scall' % arch
    return {symbol: (a[0], a[1], callconv, a[3], a[4]) for symbol, a in _p386.api.items()}
