'''
A package to contain all the extended functionality for platform specific
commands and modules.
'''

import os
import imp
import sys
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

    for dirname in extdir.split(';'):

        if not os.path.isdir(dirname):
            vdb.vprint('Invalid VDB_EXT_PATH dir: %s' % dirname)
            continue

        # allow extensions to import from the extensions directory.
        if dirname not in sys.path:
            sys.path.append(dirname)

        for fname in os.listdir(dirname):
            if not fname.endswith('.py') or fname == '__init__.py':
                continue

            modname = os.path.splitext(fname)[0]

            # Build code objects from the module files
            mod = imp.new_module('vdb.ext.%s' % modname)
            sys.modules['vdb.ext.%s' % modname] = mod
            filepath = os.path.join(dirname, fname)
            with open(filepath, 'r') as fd:
                filebytes = fd.read()
                mod.__file__ = filepath
                try:
                    exec(filebytes, mod.__dict__)
                    mod.vdbExtension(vdb, trace)
                    vdb.addExtension(filepath, mod)
                except Exception:
                    vdb.vprint(traceback.format_exc())
                    vdb.vprint('Extension Error: %s' % filepath)
