import vivisect.impapi.posix.i386 as p386

apitypes = {
    'DWORD':        'unsigned int',
    'HANDLE':       'unsigned long',
        }

# FIXME: complete the libc import api call work and update this cleanly
api = {symbol: (a[0], a[1], 'sysvamd64call', a[3], a[4]) for symbol, a in p386.api.items()}
