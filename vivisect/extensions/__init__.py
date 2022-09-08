'''
Extensions for vivisect may be implemented as python
modules which contain the function "vivExtension".

All ";" seperated directories listed in the VIV_EXT_PATH
environment variable will be searched for ".py" python
modules which implement "vivExtension"

The module's vivExtension function takes a vivisect workspace
(vw) and an vivisect gui reference (if present).
'''

import os
import sys
import importlib
import traceback


def loadExtensions(vw, vwgui):

    extdir = os.getenv('VIV_EXT_PATH')

    if extdir is None:
        # if user hasn't overridden the Extension Path, use the built-in default
        extdir = os.sep.join([vw.vivhome, 'plugins'])

    for dirname in extdir.split(os.pathsep):

        if not os.path.isdir(dirname):
            vw.vprint('Invalid VIV_EXT_PATH dir: %s' % dirname)
            continue

        if dirname not in sys.path:
            sys.path.append(dirname)

        for fname in os.listdir(dirname):
            modpath = os.path.join(dirname, fname)
            # dig into first level of directories and exec the __init__.py
            if os.path.isdir(modpath):
                modpath = os.path.join(modpath, '__init__.py')
                if not os.path.exists(modpath):
                    continue

            # otherwise, run all the .py files in the VIV_EXT_PATH dir
            elif not modpath.endswith('.py'):
                continue

            try:
                # Build code objects from the module files
                spec = importlib.util.spec_from_file_location(fname, modpath)
                module = importlib.util.module_from_spec(spec)
                module.vw = vw
                spec.loader.exec_module(module)

                module.vivExtension(vw, vwgui)
                vw.addExtension(fname, module)
            except Exception:
                vw.vprint('Extension Error: %s' % modpath)
                vw.vprint(traceback.format_exc())
