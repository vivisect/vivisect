'''
More comprehensive tests. Not necessarily for correctness, but mostly so that
if things do change, we're aware of it.

Binaries used here should be smaller so analysis completes in a reasonable enough
timeframe (since we'll be doing full analysis)
'''
import os
import json
import logging
import unittest

import vivisect
import vivisect.tests.helpers as helpers

from vivisect.const import *


logger = logging.getLogger(__name__)

class StabilityTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.testfiles = (
            ('redxor.stability.json', ('linux', 'amd64', 'redxor.malware')),
            ('sudo.stability.json', ('linux', 'amd64', 'sudo')),
        )

    def _cmp_func(self, file, base, vw):
        fails = []
        # TODO: There's some instability in the 3rd element for certain codeblocks when
        # and function is jmp'd to by other functions. It's ont horrifically bad, but
        # determinism is nice, so hunt down a way to fix that
        for fva, (size, instcount, blocks) in base['functions'].items():
            fva = int(fva)
            newfva = vw.getFunction(fva)
            if not newfva:
                fails.append((fva, 'fva', 'New version not defined'))
            try:
                self.assertEqual(fva, newfva)
                self.assertEqual(size, vw.getFunctionMeta(fva, 'Size'))
                self.assertEqual(instcount, vw.getFunctionMeta(fva, 'InstructionCount'))
            except Exception as e:
                fails.append((fva, 'meta', str(e)))
                continue

        basefunc = set([int(x) for x in base['functions'].keys()])
        for fva in vw.getFunctions():
            if fva not in basefunc:
                fails.append((fva, 'fva', 'Old version not defined'))
                continue
            size, instcount, blocks = base['functions'][str(fva)]
            try:
                self.assertEqual(size, vw.getFunctionMeta(fva, 'Size'))
                self.assertEqual(instcount, vw.getFunctionMeta(fva, 'InstructionCount'))
            except Exception as e:
                fails.append((fva, 'meta', str(e)))
                continue

        if fails:
            for fva, sect, mesg in fails:
                logger.error('[ %s ] Test fail for 0x%.8x in section %s: %s' % (file, fva, sect, mesg))
            self.fail("Stability Function Tests Failed. See logs for details.")

    def _cmp_loc(self, file, name, base, new):
        baseonly = []
        newonly = []

        fixed = []
        for b in base:
            if type(b) is list:
                b = tuple(b)
            fixed.append(b)

        for loc in fixed:
            if loc not in new:
                baseonly.append(loc)

        for loc in new:
            if loc not in fixed:
                newonly.append(loc)

        if baseonly:
            self.fail("[%s : %s] Analysis removed some locations. Here's the ones that got removed: %s" % (file, name, baseonly))

        if newonly:
            self.fail("[%s : %s] Analysis added some locations. Here's the new ones: %s" % (file, name, newonly))

    def _get_strtype(self, base):
        retn = []
        for sloc in base:
            va, size, ltyp, subs = sloc
            nsubs = set()
            for sub in subs:
                nsubs.add(tuple(sub))
            retn.append((va, size, ltyp, nsubs))

        return retn

    def _compare(self, filename, base, vw):
        testhooks = {
            'entrypoints': (self._cmp_loc, vw.getEntryPoints()),

            'pointers': (self._cmp_loc, vw.getLocations(LOC_POINTER)),
            'strings': (self._cmp_loc, self._get_strtype(vw.getLocations(LOC_STRING))),
            'unicode': (self._cmp_loc, self._get_strtype(vw.getLocations(LOC_UNI))),
            'imports': (self._cmp_loc, vw.getImports()),
            'exports': (self._cmp_loc, vw.getExports()),
            'names': (self._cmp_loc, vw.getNames()),
            'xrefs': (self._cmp_loc, vw.getXrefs()),
            'relocations': (self._cmp_loc, vw.getRelocations()),
        }

        self._cmp_func(filename, base, vw)

        for name, (func, new) in testhooks.items():
            if name == 'strings' or name == 'unicode':
                basedata = self._get_strtype(base[name])
            else:
                basedata = base[name]
            func(filename, name, basedata, new)

    def test_features(self):
        dirn = os.path.dirname(__file__)
        for filename, binpath in self.testfiles:
            testpath = os.path.join(dirn, 'stabilitydata', filename)
            with open(testpath, mode='r', encoding='utf-8') as fd:
                base = json.load(fd)
            vw = helpers.getTestWorkspace(*binpath)
            self._compare(filename, base, vw)
