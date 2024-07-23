# APIs for Windows 32-bit MSVC 2005 runtime library (msvcr80).
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']
#
# The subset of functions defined below accounts for 80% of observed calls.

api_defs = {
    'msvcr80.??2@yapaxi@z':( 'int', None, 'cdecl', 'msvcr80.??2@YAPAXI@Z', (('int', None),) ),
    'msvcr80.??_u@yapaxi@z':( 'int', None, 'cdecl', 'msvcr80.??_U@YAPAXI@Z', (('int', None),) ),
    'msvcr80.??3@yaxpax@z':( 'void', None, 'cdecl', 'msvcr80.??3@YAXPAX@Z', (('void *', 'ptr'),) ),
    'msvcr80.??_v@yaxpax@z':( 'void', None, 'cdecl', 'msvcr80.??_V@YAXPAX@Z', (('void *', 'ptr'),) ),

    'msvcr80._cxxthrowexception':( 'void', None, 'stdcall', 'msvcr80._CxxThrowException', (('void *', 'ptr'), ('int', None)) ),
    'msvcr80.__iob_func':( 'int', None, 'cdecl', 'msvcr80.__iob_func', () ),
    'msvcr80._invalid_parameter_noinfo':( 'void', None, 'cdecl', 'msvcr80._invalid_parameter_noinfo', () ),
    'msvcr80._encode_pointer':( 'int', None, 'cdecl', 'msvcr80._encode_pointer', (('int', None),) ),
    'msvcr80._errno':( 'int', None, 'cdecl', 'msvcr80._errno', () ),

    'msvcr80._exit':( 'int', None, 'cdecl', 'msvcr80._exit', (('int', None),) ),
    'msvcr80.abort':( 'int', None, 'cdecl', 'msvcr80.abort', () ),
    'msvcr80.exit':( 'int', None, 'cdecl', 'msvcr80.exit', (('int', None),) ),
    'msvcr80.quick_exit':( 'int', None, 'cdecl', 'msvcr80.quick_exit', (('int', None),) ),

    'msvcr80.calloc':( 'int', None, 'cdecl', 'msvcr80.calloc', (('int', None), ('int', None)) ),
    'msvcr80.malloc':( 'int', None, 'cdecl', 'msvcr80.malloc', (('int', None),) ),
    'msvcr80.free':( 'void', None, 'cdecl', 'msvcr80.free', (('void *', 'ptr'),) ),

    'msvcr80.memcmp':( 'int', None, 'cdecl', 'msvcr80.memcmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.memcpy':( 'int', None, 'cdecl', 'msvcr80.memcpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.memmove':( 'int', None, 'cdecl', 'msvcr80.memmove', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.memmove_s':( 'int', None, 'cdecl', 'msvcr80.memmove_s', (('void *', 'ptr'), ('int', None), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.memset':( 'int', None, 'cdecl', 'msvcr80.memset', (('void *', 'ptr'), ('int', None), ('int', None)) ),

    'msvcr80._snprintf':( 'int', None, 'cdecl', 'msvcr80._snprintf', (('int', None), ('int', None), ('int', None)) ),
    'msvcr80._swprintf':( 'int', None, 'cdecl', 'msvcr80._snprintf', (('int', None), ('int', None), ('int', None), ('int', None)) ),
    'msvcr80.fprintf':( 'int', None, 'cdecl', 'msvcr80.fprintf', (('void *', 'ptr'), ('int', None)) ),
    'msvcr80.sprintf':( 'int', None, 'cdecl', 'msvcr80.sprintf', (('int', None), ('int', None)) ),
    'msvcr80.printf':( 'int', None, 'cdecl', 'msvcr80.printf', (('int', None),) ),

    'msvcr80._stricmp':( 'int', None, 'cdecl', 'msvcr80._stricmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr80.strchr':( 'int', None, 'cdecl', 'msvcr80.strchr', (('void *', 'ptr'), ('int', None)) ),
    'msvcr80.strcmp':( 'int', None, 'cdecl', 'msvcr80.strcmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr80.strcpy':( 'int', None, 'cdecl', 'msvcr80.strcpy', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr80.strlen':( 'int', None, 'cdecl', 'msvcr80.strlen', (('void *', 'ptr'),) ),
    'msvcr80.strncmp':( 'int', None, 'cdecl', 'msvcr80.strncmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.strncpy':( 'int', None, 'cdecl', 'msvcr80.strncpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr80.strstr':( 'int', None, 'cdecl', 'msvcr80.strstr', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr80._wcsicmp':( 'int', None, 'cdecl', 'msvcr80._wcsicmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr80.wcslen':( 'int', None, 'cdecl', 'msvcr80.wcslen', (('void *', 'ptr'),) ),
    'msvcr80.wcsrchr':( 'int', None, 'cdecl', 'msvcr80.wcsrchr', (('void *', 'ptr'), ('int', None)) ),

    'msvcr80._time64':( 'int', None, 'cdecl', 'msvcr80._time64', (('void *', 'ptr'),) ),
    'msvcr80.atoi':( 'int', None, 'cdecl', 'msvcr80.atoi', (('void *', 'ptr'),) ),
    'msvcr80.getenv':( 'int', None, 'cdecl', 'msvcr80.getenv', (('void *', 'ptr'),) ),
    'msvcr80.fclose':( 'int', None, 'cdecl', 'msvcr80.fclose', (('void *', 'ptr'),) ),
    'msvcr80.bsearch':( 'int', None, 'cdecl', 'msvcr80.bsearch', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None), ('int', None), ('void *', 'funcptr')) )
}
