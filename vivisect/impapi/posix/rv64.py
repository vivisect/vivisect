import vivisect.impapi.posix.i386 as _p386

apitypes = {
    'DWORD':        'unsigned int',
    'HANDLE':       'unsigned long',
}

# The default RISC-V 64-bit ABI
api = {symbol: (a[0], a[1], 'lp64d', a[3], a[4]) for symbol, a in p386.api.items()}
