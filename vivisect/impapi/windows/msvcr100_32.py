# APIs for Windows 32-bit MSVC 2010 runtime library (msvcr100).
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']
#
# The subset of functions defined below accounts for 80% of observed calls.

api_defs = {
    'msvcr100.??2@yapaxi@z':( 'int', None, 'cdecl', 'msvcr100.??2@YAPAXI@Z', (('int', None),) ),
    'msvcr100.??_u@yapaxi@z':( 'int', None, 'cdecl', 'msvcr100.??_U@YAPAXI@Z', (('int', None),) ),
    'msvcr100.??3@yaxpax@z':( 'void', None, 'cdecl', 'msvcr100.??3@YAXPAX@Z', (('void *', 'ptr'),) ),
    'msvcr100.??_v@yaxpax@z':( 'void', None, 'cdecl', 'msvcr100.??_V@YAXPAX@Z', (('void *', 'ptr'),) ),

    'msvcr100._cxxthrowexception':( 'void', None, 'stdcall', 'msvcr100._CxxThrowException', (('void *', 'ptr'), ('int', None)) ),
    'msvcr100.__iob_func':( 'int', None, 'cdecl', 'msvcr100.__iob_func', () ),
    'msvcr100._invalid_parameter_noinfo':( 'void', None, 'cdecl', 'msvcr100._invalid_parameter_noinfo', () ),
    'msvcr100._errno':( 'int', None, 'cdecl', 'msvcr100._errno', () ),

    'msvcr100._exit':( 'int', None, 'cdecl', 'msvcr100._exit', (('int', None),) ),
    'msvcr100.abort':( 'int', None, 'cdecl', 'msvcr100.abort', () ),
    'msvcr100.exit':( 'int', None, 'cdecl', 'msvcr100.exit', (('int', None),) ),
    'msvcr100.quick_exit':( 'int', None, 'cdecl', 'msvcr100.quick_exit', (('int', None),) ),

    'msvcr100.calloc':( 'int', None, 'cdecl', 'msvcr100.calloc', (('int', None), ('int', None)) ),
    'msvcr100.malloc':( 'int', None, 'cdecl', 'msvcr100.malloc', (('int', None),) ),
    'msvcr100.free':( 'void', None, 'cdecl', 'msvcr100.free', (('void *', 'ptr'),) ),

    'msvcr100.memcmp':( 'int', None, 'cdecl', 'msvcr100.memcmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.memcpy':( 'int', None, 'cdecl', 'msvcr100.memcpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.memmove':( 'int', None, 'cdecl', 'msvcr100.memmove', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.memmove_s':( 'int', None, 'cdecl', 'msvcr100.memmove_s', (('void *', 'ptr'), ('int', None), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.memset':( 'int', None, 'cdecl', 'msvcr100.memset', (('void *', 'ptr'), ('int', None), ('int', None)) ),

    'msvcr100._snprintf':( 'int', None, 'cdecl', 'msvcr100._snprintf', (('int', None), ('int', None), ('int', None)) ),
    'msvcr100._swprintf':( 'int', None, 'cdecl', 'msvcr100._snprintf', (('int', None), ('int', None), ('int', None), ('int', None)) ),
    'msvcr100.fprintf':( 'int', None, 'cdecl', 'msvcr100.fprintf', (('void *', 'ptr'), ('int', None)) ),
    'msvcr100.sprintf':( 'int', None, 'cdecl', 'msvcr100.sprintf', (('int', None), ('int', None)) ),
    'msvcr100.printf':( 'int', None, 'cdecl', 'msvcr100.printf', (('int', None),) ),

    'msvcr100._stricmp':( 'int', None, 'cdecl', 'msvcr100._stricmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr100.strchr':( 'int', None, 'cdecl', 'msvcr100.strchr', (('void *', 'ptr'), ('int', None)) ),
    'msvcr100.strcmp':( 'int', None, 'cdecl', 'msvcr100.strcmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr100.strcpy':( 'int', None, 'cdecl', 'msvcr100.strcpy', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr100.strlen':( 'int', None, 'cdecl', 'msvcr100.strlen', (('void *', 'ptr'),) ),
    'msvcr100.strncmp':( 'int', None, 'cdecl', 'msvcr100.strncmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.strncpy':( 'int', None, 'cdecl', 'msvcr100.strncpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr100.strstr':( 'int', None, 'cdecl', 'msvcr100.strstr', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr100._wcsicmp':( 'int', None, 'cdecl', 'msvcr100._wcsicmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr100.wcslen':( 'int', None, 'cdecl', 'msvcr100.wcslen', (('void *', 'ptr'),) ),
    'msvcr100.wcsrchr':( 'int', None, 'cdecl', 'msvcr100.wcsrchr', (('void *', 'ptr'), ('int', None)) ),

    'msvcr100._time64':( 'int', None, 'cdecl', 'msvcr100._time64', (('void *', 'ptr'),) ),
    'msvcr100.atoi':( 'int', None, 'cdecl', 'msvcr100.atoi', (('void *', 'ptr'),) ),
    'msvcr100.getenv':( 'int', None, 'cdecl', 'msvcr100.getenv', (('void *', 'ptr'),) ),
    'msvcr100.fclose':( 'int', None, 'cdecl', 'msvcr100.fclose', (('void *', 'ptr'),) ),
    'msvcr100.bsearch':( 'int', None, 'cdecl', 'msvcr100.bsearch', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None), ('int', None), ('void *', 'funcptr')) )
    }
