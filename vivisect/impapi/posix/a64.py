import vivisect.impapi.posix.i386 as p386

apitypes = {
    'DWORD':        'unsigned int',
    'HANDLE':       'unsigned long',
        }

api = {symbol: (a[0], a[1], 'a64call', a[3], a[4]) for symbol, a in p386.api.items()}
