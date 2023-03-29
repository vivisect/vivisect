# APIs for Windows 32-bit.  Each library has its own file of APIs, and
# they are collected into a single dictionary here.  The separate files
# are hard-coded into this module.  Each is expected to return
# a dictionary named "api_defs".
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

import vivisect.impapi.windows.ntdll_32 as mNt
api.update(mNt.api_defs)

import vivisect.impapi.windows.kernel_32 as mKer
api.update(mKer.api_defs)

import vivisect.impapi.windows.advapi_32 as mAdv
api.update(mAdv.api_defs)

import vivisect.impapi.windows.gdi_32 as mGdi
api.update(mGdi.api_defs)

import vivisect.impapi.windows.ole_32 as mOle
api.update(mOle.api_defs)

import vivisect.impapi.windows.user_32 as mUser
api.update(mUser.api_defs)

import vivisect.impapi.windows.rpcrt4_32 as mRpc
api.update(mRpc.api_defs)

import vivisect.impapi.windows.msvcrt_32 as mCrt
api.update(mCrt.api_defs)

import vivisect.impapi.windows.msvcr71_32 as mCr71
api.update(mCr71.api_defs)

import vivisect.impapi.windows.msvcr80_32 as mCr80
api.update(mCr80.api_defs)

import vivisect.impapi.windows.msvcr90_32 as mCr90
api.update(mCr90.api_defs)

import vivisect.impapi.windows.msvcr100_32 as mCr100
api.update(mCr100.api_defs)

import vivisect.impapi.windows.msvcr110_32 as mCr110
api.update(mCr110.api_defs)

import vivisect.impapi.windows.msvcr120_32 as mCr120
api.update(mCr120.api_defs)

import vivisect.impapi.windows.ws2plus_32 as mWs2
api.update(mWs2.api_defs)

import vivisect.impapi.windows.shell_32 as mShl
api.update(mShl.api_defs)
