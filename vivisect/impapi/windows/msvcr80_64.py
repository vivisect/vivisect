# APIs for Windows 64-bit MSVC 2005 runtime library (msvcr80).
# Built as a delta from the 32-bit version.
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']

# List the normalized name of any 32-bit functions to omit.
api_32_omits = [
    'msvcr80.??2@yapaxi@z',
    'msvcr80.??_u@yapaxi@z',
    'msvcr80.??3@yaxpax@z',
    'msvcr80.??_v@yaxpax@z'
]

# Define any functions specific to 64-bit.
api_64_adds = {
    'msvcr80.??2@yapeax_k@z':( 'int', None, 'msx64call', 'msvcr80.??2@YAPEAX_K@Z', (('int', None),) ),
    'msvcr80.??_u@yapeax_k@z':( 'int', None, 'msx64call', 'msvcr80.??_U@YAPEAX_K@Z', (('int', None),) ),
    'msvcr80.??3@yaxpeax@z':( 'void', None, 'msx64call', 'msvcr80.??3@YAXPEAX@Z', (('void *', 'ptr'),) ),
    'msvcr80.??_v@yaxpeax@z':( 'void', None, 'msx64call', 'msvcr80.??_V@YAXPEAX@Z', (('void *', 'ptr'),) ),
    }


# Build from the 32-bit API, skipping omits, changing the calling convention,
# and adding any specific 64-bit functions.
api_defs_64 = {}

import vivisect.impapi.windows.msvcr80_32 as m32
for normname, (rtype, rname, cconv, cname, cargs) in m32.api_defs.items():
    if normname in api_32_omits:
        continue
    api_defs_64[normname] = (rtype, rname, 'msx64call', cname, cargs)
api_defs_64.update(api_64_adds)
