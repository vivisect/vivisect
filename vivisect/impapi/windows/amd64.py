# APIs for Windows 64-bit.  Each library has its own file of APIs, and
# they are collected into a single dictionary here.  The separate files
# are hard-coded into this module.  Each is expected to return
# a dictionary named "api_defs_64".
#
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          where arglist type is one of ['int', 'void *']
#                arglist name is one of [None, 'funcptr', 'obj', 'ptr']


apitypes = {
    # NTDLL
    'DWORD':        'unsigned int',
    'HANDLE':       'DWORD',
    'LIBHANDLE':    'HANDLE',
    'HEAP':         'HANDLE',
}


api = {}

import vivisect.impapi.windows.ntdll_64 as mNt
api.update(mNt.api_defs_64)

import vivisect.impapi.windows.kernel_64 as mKer
api.update(mKer.api_defs_64)

import vivisect.impapi.windows.advapi_64 as mAdv
api.update(mAdv.api_defs_64)

import vivisect.impapi.windows.gdi_64 as mGdi
api.update(mGdi.api_defs_64)

import vivisect.impapi.windows.ole_64 as mOle
api.update(mOle.api_defs_64)

import vivisect.impapi.windows.user_64 as mUser
api.update(mUser.api_defs_64)

import vivisect.impapi.windows.rpcrt4_64 as mRpc
api.update(mRpc.api_defs_64)

import vivisect.impapi.windows.msvcrt_64 as mCrt
api.update(mCrt.api_defs_64)

# There is no 64-bit msvcr70 or msvcr71.

import vivisect.impapi.windows.msvcr80_64 as mCr80
api.update(mCr80.api_defs_64)

import vivisect.impapi.windows.msvcr90_64 as mCr90
api.update(mCr90.api_defs_64)

import vivisect.impapi.windows.msvcr100_64 as mCr100
api.update(mCr100.api_defs_64)

import vivisect.impapi.windows.msvcr110_64 as mCr110
api.update(mCr110.api_defs_64)

import vivisect.impapi.windows.msvcr120_64 as mCr120
api.update(mCr120.api_defs_64)

import vivisect.impapi.windows.ws2plus_64 as mWs2
api.update(mWs2.api_defs_64)

import vivisect.impapi.windows.shell_64 as mShl
api.update(mShl.api_defs_64)
