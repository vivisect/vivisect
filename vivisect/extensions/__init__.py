import os
import imp
import traceback

'''
Extensions for vivisect may be implemented as python
modules which contain the function "vivExtension".

All ";" seperated directories listed in the VIV_EXT_PATH
environment variable will be searched for ".py" python
modules which implement "vivExtension"

The module's vivExtension function takes a vivisect workspace
(vw) and an vivisect gui reference (if present).
'''

def loadExtensions( vw, vwgui ):

    extdir = os.getenv('VIV_EXT_PATH')

    if extdir == None:
        return

    for dirname in extdir.split(';'):

        if not os.path.isdir(dirname):
            vw.vprint('Invalid VIV_EXT_PATH dir: %s' % dirname)
            continue

        for fname in os.listdir(dirname):
            modpath = os.sep.join([dirname, fname])
            # dig into first level of directories and exec the __init__.py
            if os.path.isdir(modpath):
                modpath = os.sep.join([modpath, '__init__.py'])
                if not os.path.exists(modpath):
                    continue

            # otherwise, run all the .py files in the VIV_EXT_PATH dir
            if not modpath.endswith('.py'):
                continue

            # Build code objects from the module files
            mod = imp.new_module('viv_ext')
            filebytes = open( modpath, 'r' ).read()
            mod.__file__ = modpath
            try:
                exec filebytes in mod.__dict__
                mod.vivExtension(vw, vwgui)
            except Exception, e:
                vw.vprint( traceback.format_exc() )
                vw.vprint('Extension Error: %s' % modpath)

