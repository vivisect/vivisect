import os
import imp
import logging
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

logger = logging.getLogger(__name__)


def earlyExtensions(vw):
    logger.debug('earlyLoad')
    for mod in extensions:
        if not hasattr(mod, 'earlyLoad'):
            logger.debug('earlyLoad: %r (no earlyLoad() function)', mod)
            continue

        logger.debug('earlyLoad: %r', mod)
        try:
            mod.earlyLoad(vw)
        except Exception, e:
            vw.vprint(traceback.format_exc())
            vw.vprint('Extension Error (early): %s' % filepath)


def loadExtensions(vw, vwgui):
    logger.debug('loadExtensions')
    for mod in extensions:
        logger.debug('loadExtensionsL %r', mod)
        try:
            mod.vivExtension(vw, vwgui)
        except Exception, e:
            vw.vprint(traceback.format_exc())
            vw.vprint('Extension Error: %s' % filepath)

extensions = []
def impExtensions():
    global extensions
    extdir = os.getenv('VIV_EXT_PATH')

    if extdir is None:
        return

    logger.info('impExtensions: VIV_EXT_PATH == %r', extdir)
    for dirname in extdir.split(';'):
        logger.info('impExtensions: %r', dirname)

        if not os.path.isdir(dirname):
            logger.warn('Invalid VIV_EXT_PATH dir: %s' % dirname)
            continue

        for fname in os.listdir(dirname):

            if not fname.endswith('.py'):
                continue

            logger.info('impExtensions: %s/%s', dirname, fname)
            # Build code objects from the module files
            mod = imp.new_module('viv_ext')
            filepath = os.path.join(dirname, fname)
            filebytes = file(filepath, 'r').read()
            mod.__file__ = filepath
            try:
                exec filebytes in mod.__dict__
                extensions.append(mod)
                
            except Exception as e:
                logger.warn(traceback.format_exc())
                logger.warn('Extension Error (load:%r): %s' % (filepath, e))

impExtensions()
logger.info("EXTENSIONS: %s", repr(extensions))
