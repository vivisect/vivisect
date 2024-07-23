# APIs for Windows 32-bit MSVC 2008 runtime library (msvcr90).
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']
#
# The subset of functions defined below accounts for 80% of observed calls.

api_defs = {
    'msvcr90.??2@yapaxi@z':( 'int', None, 'cdecl', 'msvcr90.??2@YAPAXI@Z', (('int', None),) ),
    'msvcr90.??_u@yapaxi@z':( 'int', None, 'cdecl', 'msvcr90.??_U@YAPAXI@Z', (('int', None),) ),
    'msvcr90.??3@yaxpax@z':( 'void', None, 'cdecl', 'msvcr90.??3@YAXPAX@Z', (('void *', 'ptr'),) ),
    'msvcr90.??_v@yaxpax@z':( 'void', None, 'cdecl', 'msvcr90.??_V@YAXPAX@Z', (('void *', 'ptr'),) ),

    'msvcr90._cxxthrowexception':( 'void', None, 'stdcall', 'msvcr90._CxxThrowException', (('void *', 'ptr'), ('int', None)) ),
    'msvcr90.__iob_func':( 'int', None, 'cdecl', 'msvcr90.__iob_func', () ),
    'msvcr90._invalid_parameter_noinfo':( 'void', None, 'cdecl', 'msvcr90._invalid_parameter_noinfo', () ),
    'msvcr90._encode_pointer':( 'int', None, 'cdecl', 'msvcr90._encode_pointer', (('int', None),) ),
    'msvcr90._errno':( 'int', None, 'cdecl', 'msvcr90._errno', () ),

    'msvcr90._exit':( 'int', None, 'cdecl', 'msvcr90._exit', (('int', None),) ),
    'msvcr90.abort':( 'int', None, 'cdecl', 'msvcr90.abort', () ),
    'msvcr90.exit':( 'int', None, 'cdecl', 'msvcr90.exit', (('int', None),) ),
    'msvcr90.quick_exit':( 'int', None, 'cdecl', 'msvcr90.quick_exit', (('int', None),) ),

    'msvcr90.calloc':( 'int', None, 'cdecl', 'msvcr90.calloc', (('int', None), ('int', None)) ),
    'msvcr90.malloc':( 'int', None, 'cdecl', 'msvcr90.malloc', (('int', None),) ),
    'msvcr90.free':( 'void', None, 'cdecl', 'msvcr90.free', (('void *', 'ptr'),) ),

    'msvcr90.memcmp':( 'int', None, 'cdecl', 'msvcr90.memcmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.memcpy':( 'int', None, 'cdecl', 'msvcr90.memcpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.memmove':( 'int', None, 'cdecl', 'msvcr90.memmove', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.memmove_s':( 'int', None, 'cdecl', 'msvcr90.memmove_s', (('void *', 'ptr'), ('int', None), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.memset':( 'int', None, 'cdecl', 'msvcr90.memset', (('void *', 'ptr'), ('int', None), ('int', None)) ),

    'msvcr90._snprintf':( 'int', None, 'cdecl', 'msvcr90._snprintf', (('int', None), ('int', None), ('int', None)) ),
    'msvcr90._swprintf':( 'int', None, 'cdecl', 'msvcr90._snprintf', (('int', None), ('int', None), ('int', None), ('int', None)) ),
    'msvcr90.fprintf':( 'int', None, 'cdecl', 'msvcr90.fprintf', (('void *', 'ptr'), ('int', None)) ),
    'msvcr90.sprintf':( 'int', None, 'cdecl', 'msvcr90.sprintf', (('int', None), ('int', None)) ),
    'msvcr90.printf':( 'int', None, 'cdecl', 'msvcr90.printf', (('int', None),) ),

    'msvcr90._stricmp':( 'int', None, 'cdecl', 'msvcr90._stricmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr90.strchr':( 'int', None, 'cdecl', 'msvcr90.strchr', (('void *', 'ptr'), ('int', None)) ),
    'msvcr90.strcmp':( 'int', None, 'cdecl', 'msvcr90.strcmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr90.strcpy':( 'int', None, 'cdecl', 'msvcr90.strcpy', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr90.strlen':( 'int', None, 'cdecl', 'msvcr90.strlen', (('void *', 'ptr'),) ),
    'msvcr90.strncmp':( 'int', None, 'cdecl', 'msvcr90.strncmp', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.strncpy':( 'int', None, 'cdecl', 'msvcr90.strncpy', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'msvcr90.strstr':( 'int', None, 'cdecl', 'msvcr90.strstr', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr90._wcsicmp':( 'int', None, 'cdecl', 'msvcr90._wcsicmp', (('void *', 'ptr'), ('void *', 'ptr')) ),
    'msvcr90.wcslen':( 'int', None, 'cdecl', 'msvcr90.wcslen', (('void *', 'ptr'),) ),
    'msvcr90.wcsrchr':( 'int', None, 'cdecl', 'msvcr90.wcsrchr', (('void *', 'ptr'), ('int', None)) ),

    'msvcr90._time64':( 'int', None, 'cdecl', 'msvcr90._time64', (('void *', 'ptr'),) ),
    'msvcr90.atoi':( 'int', None, 'cdecl', 'msvcr90.atoi', (('void *', 'ptr'),) ),
    'msvcr90.getenv':( 'int', None, 'cdecl', 'msvcr90.getenv', (('void *', 'ptr'),) ),
    'msvcr90.fclose':( 'int', None, 'cdecl', 'msvcr90.fclose', (('void *', 'ptr'),) ),
    'msvcr90.bsearch':( 'int', None, 'cdecl', 'msvcr90.bsearch', (('void *', 'ptr'), ('void *', 'ptr'), ('int', None), ('int', None), ('void *', 'funcptr')) )
}
