# APIs for Windows 32-bit libraries shell_32.
# Format:  rettype, retname, callconv, exactname, arglist(type, name)
#          arglist type is one of ['int', 'void *']
#          arglist name is one of [None, 'funcptr', 'obj', 'ptr']

api_defs = {
    'shell32.commandlinetoargvw':( 'int', None, 'stdcall', 'shell32.CommandLineToArgW', (('void *', 'ptr'), ('int', None)) ),
    'shell32.shellexecutea':( 'int', None, 'stdcall', 'shell32.ShellExecuteA', (('int', None), ('void *', 'ptr'), ('void *', 'ptr'), ('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'shell32.shellexecutew':( 'int', None, 'stdcall', 'shell32.ShellExecuteW', (('int', None), ('void *', 'ptr'), ('void *', 'ptr'), ('void *', 'ptr'), ('void *', 'ptr'), ('int', None)) ),
    'shell32.shellexecuteexa':( 'int', None, 'stdcall', 'shell32.ShellExecuteExA', (('void *', 'ptr'),) ),
    'shell32.shellexecuteexw':( 'int', None, 'stdcall', 'shell32.ShellExecuteExW', (('void *', 'ptr'),) ),
    'shell32.shfileoperationa':( 'int', None, 'stdcall', 'shell32.SHFileOperationA', (('void *', 'ptr'),) ),
    'shell32.shfileoperationw':( 'int', None, 'stdcall', 'shell32.SHFileOperationW', (('void *', 'ptr'),) ),
    'shell32.shgetfolderpatha':( 'int', None, 'stdcall', 'shell32.SHGetFolderPathA', (('int', None), ('int', None), ('int', None), ('int', None), ('void *', 'ptr')) ),
    'shell32.shgetfolderpathw':( 'int', None, 'stdcall', 'shell32.SHGetFolderPathW', (('int', None), ('int', None), ('int', None), ('int', None), ('void *', 'ptr')) ),
    'shell32.shgetspecialfolderpatha':( 'int', None, 'stdcall', 'shell32.SHGetSpecialFolderPathA', (('int', None), ('void *', 'ptr'), ('int', None), ('int', None)) ),
    'shell32.shgetspecialfolderpathw':( 'int', None, 'stdcall', 'shell32.SHGetSpecialFolderPathW', (('int', None), ('void *', 'ptr'), ('int', None), ('int', None)) ),
    }
