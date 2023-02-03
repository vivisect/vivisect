# APIs for Windows 32-bit MSVC 2013 runtime library (msvcr120).
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']
#
# The subset of functions defined below accounts for 80% of observed calls.

api_defs = {
    'msvcr120.??2@yapaxi@z':( 'int', None, 'cdecl', 'msvcr120.??2@YAPAXI@Z', (('int', None),) ),
    'msvcr120.??_u@yapaxi@z':( 'int', None, 'cdecl', 'msvcr120.??_U@YAPAXI@Z', (('int', None),) ),
    'msvcr120.??3@yaxpax@z':( 'void', None, 'cdecl', 'msvcr120.??3@YAXPAX@Z', (('void *', 'ptr'),) ),
    'msvcr120.??_v@yaxpax@z':( 'void', None, 'cdecl', 'msvcr120.??_V@YAXPAX@Z', (('void *', 'ptr'),) ),

    'msvcr120._cxxthrowexception':( 'void', None, 'stdcall', 'msvcr120._CxxThrowException', (('void *', 'ptr'), ('int', None)) ),
    'msvcr120.__iob_func':( 'int', None, 'cdecl', 'msvcr120.__iob_func', () ),
    'msvcr120._invalid_parameter_noinfo':( 'void', None, 'cdecl', 'msvcr120._invalid_parameter_noinfo', () ),
    'msvcr120._errno':( 'int', None, 'cdecl', 'msvcr120._errno', () ),

    'msvcr120._exit':( 'int', None, 'cdecl', 'msvcr120._exit', (('int', None),) ),
    'msvcr120.abort':( 'int', None, 'cdecl', 'msvcr120.abort', () ),
    'msvcr120.exit':( 'int', None, 'cdecl', 'msvcr120.exit', (('int', None),) ),
    'msvcr120.quick_exit':( 'int', None, 'cdecl', 'msvcr120.quick_exit', (('int', None),) ),

    'msvcr120.calloc':( 'int', None, 'cdecl', 'msvcr120.calloc', (('int', None), ('int', None)) ),
    'msvcr120.malloc':( 'int', None, 'cdecl', 'msvcr120.malloc', (('int', None),) ),
    'msvcr120.free':( 'void', None, 'cdecl', 'msvcr120.free', (('void *', 'ptr'),) ),

    'msvcr120.memcmp':( 'int', None, 'cdecl', 'msvcr120.memcmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.memcpy':( 'int', None, 'cdecl', 'msvcr120.memcpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.memmove':( 'int', None, 'cdecl', 'msvcr120.memmove', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.memmove_s':( 'int', None, 'cdecl', 'msvcr120.memmove_s', (('void *', 'ptr'), ('int', None), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.memset':( 'int', None, 'cdecl', 'msvcr120.memset', (('void *', 'ptr'), ('int', None), ('int', None)) ),

    'msvcr120._snprintf':( 'int', None, 'cdecl', 'msvcr120._snprintf', (('int', None), ('int', None), ('int', None)) ),
    'msvcr120._swprintf':( 'int', None, 'cdecl', 'msvcr120._snprintf', (('int', None), ('int', None), ('int', None), ('int', None)) ),
    'msvcr120.fprintf':( 'int', None, 'cdecl', 'msvcr120.fprintf', (('void *', 'ptr'), ('int', None)) ),
    'msvcr120.sprintf':( 'int', None, 'cdecl', 'msvcr120.sprintf', (('int', None), ('int', None)) ),
    'msvcr120.printf':( 'int', None, 'cdecl', 'msvcr120.printf', (('int', None),) ),

    'msvcr120._stricmp':( 'int', None, 'cdecl', 'msvcr120._stricmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr120.strchr':( 'int', None, 'cdecl', 'msvcr120.strchr', (('void *', 'ptr'), ('int', None)) ),
    'msvcr120.strcmp':( 'int', None, 'cdecl', 'msvcr120.strcmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr120.strcpy':( 'int', None, 'cdecl', 'msvcr120.strcpy', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr120.strlen':( 'int', None, 'cdecl', 'msvcr120.strlen', (('void *', 'ptr'),) ),
    'msvcr120.strncmp':( 'int', None, 'cdecl', 'msvcr120.strncmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.strncpy':( 'int', None, 'cdecl', 'msvcr120.strncpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr120.strstr':( 'int', None, 'cdecl', 'msvcr120.strstr', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr120._wcsicmp':( 'int', None, 'cdecl', 'msvcr120._wcsicmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr120.wcslen':( 'int', None, 'cdecl', 'msvcr120.wcslen', (('void *', 'ptr'),) ),
    'msvcr120.wcsrchr':( 'int', None, 'cdecl', 'msvcr120.wcsrchr', (('void *', 'ptr'), ('int', None)) ),

    'msvcr120._time64':( 'int', None, 'cdecl', 'msvcr120._time64', (('void *', 'ptr'),) ),
    'msvcr120.atoi':( 'int', None, 'cdecl', 'msvcr120.atoi', (('void *', 'ptr'),) ),
    'msvcr120.getenv':( 'int', None, 'cdecl', 'msvcr120.getenv', (('void *', 'ptr'),) ),
    'msvcr120.fclose':( 'int', None, 'cdecl', 'msvcr120.fclose', (('void *', 'ptr'),) ),
    'msvcr120.bsearch':( 'int', None, 'cdecl', 'msvcr120.bsearch', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None), ('int', None), ('void *', 'funcptr')) )
    }
