import vivisect.impapi.posix.i386 as _p386

apitypes = {
    'DWORD':        'unsigned int',
    'HANDLE':       'unsigned long',
}

# The default RISC-V 32-bit ABI
api = {symbol: (a[0], a[1], 'ilp32d', a[3], a[4]) for symbol, a in p386.api.items()}
