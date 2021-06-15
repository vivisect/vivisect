'''
A package to contain all the extended functionality for platform specific
commands and modules.
'''

import os
import sys
import importlib
import traceback

__all__ = ['loadExtensions', 'windows', 'i386', 'darwin', 'amd64', 'gdbstub', 'arm', 'android', 'winkern']


def loadExtensions(vdb, trace):
    '''
    Actually load all known extensions here.
    '''
    plat = trace.getMeta('Platform').lower()
    arch = trace.getMeta('Architecture').lower()

    if plat in __all__:
        mod = __import__('vdb.extensions.%s' % plat, 0, 0, 1)
        mod.vdbExtension(vdb, trace)

    if arch in __all__:
        mod = __import__('vdb.extensions.%s' % arch, 0, 0, 1)
        mod.vdbExtension(vdb, trace)

    extdir = os.getenv('VDB_EXT_PATH')
    if extdir is None:
        extdir = os.path.abspath(os.path.join('vdb', 'ext'))

    for dirname in extdir.split(os.pathsep):

        if not os.path.isdir(dirname):
            vdb.vprint('Invalid VDB_EXT_PATH dir: %s' % dirname)
            continue

        # allow extensions to import from the extensions directory.
        if dirname not in sys.path:
            sys.path.append(dirname)

        for fname in os.listdir(dirname):
            modpath = os.path.join(dirname, fname)
            if os.path.isdir(modpath):
                modpath = os.path.join(modpath, '__init__.py')
                if not os.path.exists(modpath):
                    continue

            if not fname.endswith('.py') or fname == '__init__.py':
                continue

            try:
                # Build code objects from the module files
                spec = importlib.util.spec_from_file_location(fname, modpath)
                module = importlib.util.module_from_spec(spec)
                module.vdb = vdb
                module.__file__ = modpath
                spec.loader.exec_module(module)
                module.vdbExtension(vdb, trace)
                vdb.addExtension(fname, module)
            except Exception:
                vdb.vprint('VDB Extension Error: %s' % modpath)
                vdb.vprint(traceback.format_exc())
