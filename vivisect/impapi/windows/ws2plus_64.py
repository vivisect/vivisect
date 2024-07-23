# APIs for Windows 64-bit libraries ws2_32, mswsock, wsock32, and wininet.
# Built as a delta from the 32-bit version.
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']

# List the normalized name of any 32-bit functions to omit.
api_32_omits = []

# Define any functions specific to 64-bit.
api_64_adds = {
    }


# Build from the 32-bit API, skipping omits, changing the calling convention,
# and adding any specific 64-bit functions.
api_defs_64 = {}

import vivisect.impapi.windows.ws2plus_32 as m32
for normname, (rtype, rname, cconv, cname, cargs) in m32.api_defs.items():
    if normname in api_32_omits:
        continue
    api_defs_64[normname] = (rtype, rname, 'msx64call', cname, cargs)
api_defs_64.update(api_64_adds)
