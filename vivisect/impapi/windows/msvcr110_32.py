# APIs for Windows 32-bit MSVC 2012 runtime library (msvcr110).
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']
#
# The subset of functions defined below accounts for 80% of observed calls.

api_defs = {
    'msvcr110.??2@yapaxi@z':( 'int', None, 'cdecl', 'msvcr110.??2@YAPAXI@Z', (('int', None),) ),
    'msvcr110.??_u@yapaxi@z':( 'int', None, 'cdecl', 'msvcr110.??_U@YAPAXI@Z', (('int', None),) ),
    'msvcr110.??3@yaxpax@z':( 'void', None, 'cdecl', 'msvcr110.??3@YAXPAX@Z', (('void *', 'ptr'),) ),
    'msvcr110.??_v@yaxpax@z':( 'void', None, 'cdecl', 'msvcr110.??_V@YAXPAX@Z', (('void *', 'ptr'),) ),

    'msvcr110._cxxthrowexception':( 'void', None, 'stdcall', 'msvcr110._CxxThrowException', (('void *', 'ptr'), ('int', None)) ),
    'msvcr110.__iob_func':( 'int', None, 'cdecl', 'msvcr110.__iob_func', () ),
    'msvcr110._invalid_parameter_noinfo':( 'void', None, 'cdecl', 'msvcr110._invalid_parameter_noinfo', () ),
    'msvcr110._errno':( 'int', None, 'cdecl', 'msvcr110._errno', () ),

    'msvcr110._exit':( 'int', None, 'cdecl', 'msvcr110._exit', (('int', None),) ),
    'msvcr110.abort':( 'int', None, 'cdecl', 'msvcr110.abort', () ),
    'msvcr110.exit':( 'int', None, 'cdecl', 'msvcr110.exit', (('int', None),) ),
    'msvcr110.quick_exit':( 'int', None, 'cdecl', 'msvcr110.quick_exit', (('int', None),) ),

    'msvcr110.calloc':( 'int', None, 'cdecl', 'msvcr110.calloc', (('int', None), ('int', None)) ),
    'msvcr110.malloc':( 'int', None, 'cdecl', 'msvcr110.malloc', (('int', None),) ),
    'msvcr110.free':( 'void', None, 'cdecl', 'msvcr110.free', (('void *', 'ptr'),) ),

    'msvcr110.memcmp':( 'int', None, 'cdecl', 'msvcr110.memcmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.memcpy':( 'int', None, 'cdecl', 'msvcr110.memcpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.memmove':( 'int', None, 'cdecl', 'msvcr110.memmove', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.memmove_s':( 'int', None, 'cdecl', 'msvcr110.memmove_s', (('void *', 'ptr'), ('int', None), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.memset':( 'int', None, 'cdecl', 'msvcr110.memset', (('void *', 'ptr'), ('int', None), ('int', None)) ),

    'msvcr110._snprintf':( 'int', None, 'cdecl', 'msvcr110._snprintf', (('int', None), ('int', None), ('int', None)) ),
    'msvcr110._swprintf':( 'int', None, 'cdecl', 'msvcr110._snprintf', (('int', None), ('int', None), ('int', None), ('int', None)) ),
    'msvcr110.fprintf':( 'int', None, 'cdecl', 'msvcr110.fprintf', (('void *', 'ptr'), ('int', None)) ),
    'msvcr110.sprintf':( 'int', None, 'cdecl', 'msvcr110.sprintf', (('int', None), ('int', None)) ),
    'msvcr110.printf':( 'int', None, 'cdecl', 'msvcr110.printf', (('int', None),) ),

    'msvcr110._stricmp':( 'int', None, 'cdecl', 'msvcr110._stricmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr110.strchr':( 'int', None, 'cdecl', 'msvcr110.strchr', (('void *', 'ptr'), ('int', None)) ),
    'msvcr110.strcmp':( 'int', None, 'cdecl', 'msvcr110.strcmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr110.strcpy':( 'int', None, 'cdecl', 'msvcr110.strcpy', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr110.strlen':( 'int', None, 'cdecl', 'msvcr110.strlen', (('void *', 'ptr'),) ),
    'msvcr110.strncmp':( 'int', None, 'cdecl', 'msvcr110.strncmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.strncpy':( 'int', None, 'cdecl', 'msvcr110.strncpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr110.strstr':( 'int', None, 'cdecl', 'msvcr110.strstr', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr110._wcsicmp':( 'int', None, 'cdecl', 'msvcr110._wcsicmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr110.wcslen':( 'int', None, 'cdecl', 'msvcr110.wcslen', (('void *', 'ptr'),) ),
    'msvcr110.wcsrchr':( 'int', None, 'cdecl', 'msvcr110.wcsrchr', (('void *', 'ptr'), ('int', None)) ),

    'msvcr110._time64':( 'int', None, 'cdecl', 'msvcr110._time64', (('void *', 'ptr'),) ),
    'msvcr110.atoi':( 'int', None, 'cdecl', 'msvcr110.atoi', (('void *', 'ptr'),) ),
    'msvcr110.getenv':( 'int', None, 'cdecl', 'msvcr110.getenv', (('void *', 'ptr'),) ),
    'msvcr110.fclose':( 'int', None, 'cdecl', 'msvcr110.fclose', (('void *', 'ptr'),) ),
    'msvcr110.bsearch':( 'int', None, 'cdecl', 'msvcr110.bsearch', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None), ('int', None), ('void *', 'funcptr')) )
    }
