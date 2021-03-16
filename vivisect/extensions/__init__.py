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
import logging
import importlib
import traceback

logger = logging.getLogger(__name__)

def earlyExtensions(vw):
    logger.debug('earlyLoad')
    for mname, mod in vw.getExtensions():
        try:
            if not hasattr(mod, 'earlyLoad'):
                logger.debug('earlyLoad: %r (no earlyLoad() function)', mod)
                continue

            logger.debug('earlyLoad: %r', mod)
            mod.earlyLoad(vw)

        except Exception as e:
            logger.warning(traceback.format_exc())
            logger.warning('Extension Error (load:%r): %s' % (mod, e))


def preFileLoadExtensions(vw, fname, bytez, fd):
    logger.debug('preFileLoad')
    for mname, mod in vw.getExtensions():
        try:
            if not hasattr(mod, 'preFileLoadHook'):
                logger.debug('preFileLoad: %r (no preFileLoadHook() function)', mod)
                continue

            logger.debug('preFileLoad: %r', mod)
            mod.preFileLoadHook(vw, fname, bytez, fd)

        except Exception as e:
            logger.warning(traceback.format_exc())
            logger.warning('Extension Error (load:%r): %s' % (mod, e))


def loadExtensions(vw, vwgui):
    logger.debug('loadExtensions')
    for mname, mod in vw.getExtensions():
        logger.debug('loadExtensions %r', mod)
        try:
            if not hasattr(mod, 'vivExtension'):
                logger.debug('loadExtensions: %r (no vivExtension() function)', mod)
                continue

            mod.vivExtension(vw, vwgui)

        except Exception as e:
            logger.warning(traceback.format_exc())
            logger.warning('Extension Error (load:%r): %s' % (mod, e))

def importExtensions(vw):
    extdir = os.getenv('VIV_EXT_PATH')

    if extdir is None:
        return

    logger.info('importExtensions: VIV_EXT_PATH == %r', extdir)
    for dirname in extdir.split(os.pathsep):
        logger.info('importExtensions: %r', dirname)

        if not os.path.isdir(dirname):
            logger.warning('Invalid VIV_EXT_PATH dir: %s', dirname)
            continue

        if dirname not in sys.path:
            sys.path.append(dirname)

        for fname in os.listdir(dirname):
            modpath = os.path.join(dirname, fname)
            # dig into first level of directories and exec the __init__.py
            if os.path.isdir(modpath):
                modname = fname
                modpath = os.path.join(modpath, '__init__.py')
                if not os.path.exists(modpath):
                    continue

            # otherwise, run all the .py files in the VIV_EXT_PATH dir
            elif not modpath.endswith('.py'):
                continue

            else:
                # it's a .py file
                modname = fname[:-3]

            try:
                logger.info('importExtensions: %s', modpath)
                # Build code objects from the module files
                spec = importlib.util.spec_from_file_location(fname, modpath)
                module = importlib.util.module_from_spec(spec)
                module.vw = vw
                spec.loader.exec_module(module)

                vw.addExtension(fname, module)

            except Exception as e:
                logger.warning(traceback.format_exc())
                logger.warning('Extension Error (load:%r): %s' % (modpath, e))

