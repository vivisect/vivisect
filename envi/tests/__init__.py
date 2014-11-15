import envi
import platform
import unittest

def skip(*skips):
    arch = envi.getCurrentArch()
    plat = platform.system().lower()

    cur = set([arch,plat])
    skips = set(skips)

    def skipfunc(f):
        has = cur & skips
        if not has:
            return f

        def doskip(*args, **kwargs):
            raise unittest.SkipTest('Skipped For: %s' % (repr(has),))

        return doskip

    return skipfunc

