import time
import logging
import platform
import unittest

import Elf
import vivisect.cli as viv_cli
import vivisect.tests.helpers as helpers
import vivisect.analysis.elf as vae
import vivisect.analysis.elf.elfplt as vaeep
import vivisect.analysis.elf.elfplt_late as vaeepl
import vivisect.analysis.generic.pointers as vagp
import vivisect.analysis.generic.relocations as vagr

from vivisect.tests import linux_amd64_ls_data
from vivisect.tests import linux_amd64_chown_data
from vivisect.tests import linux_amd64_libc_2_27_data
from vivisect.tests import linux_amd64_libstdc_data
from vivisect.tests import linux_i386_libc_2_13_data
from vivisect.tests import linux_i386_libstdc_data
from vivisect.tests import linux_arm_sh_data
from vivisect.tests import qnx_arm_ksh_data
from vivisect.tests import openbsd_amd64_ls_data

logger = logging.getLogger(__name__)


def do_analyze(vw):
    for mod in vae, vagr, vaeep, vagp, vaeepl:
        try:
            mod.analyze(vw)
        except Exception as e:
            import traceback
            logging.warning("ERROR in analysis module: (%r): %r", mod, e, exc_info=1)

comparators = {
    'names': lambda x, y: x[0] == y[0],
    'imports': lambda x, y: x[:3] == y[:3],
    'exports': lambda x, y: x[:1] == y[:1] and x[3] == y[3],
}

class ELFTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.data = (
            # ("linux_amd64_ls", linux_amd64_ls_data.ls_data, ('linux', 'amd64', 'ls'), ),
            ("linux_amd64_chown", linux_amd64_chown_data.chown_data, ('linux', 'amd64', 'chown'),),
            ("linux_amd64_libc", linux_amd64_libc_2_27_data.libc_data, ('linux', 'amd64', 'libc-2.27.so'),),
            # ("linux_amd64_libstdc", linux_amd64_libstdc_data.libstdc_data, ('linux', 'amd64', 'libstdc++.so.6.0.25'),),
            # ("linux_amd64_static", linux_amd64_static_data.static64_data, ('linux', 'amd64', 'static64.llvm.elf'),),

            # while i386 libc is a good test, it takes likel 3 minutes to analyze, which is instane
            # ("linux_i386_libc", linux_i386_libc_2_13_data.libc_data, ('linux', 'i386', 'libc-2.13.so'),),
            ("linux_i386_libstdc", linux_i386_libstdc_data.libstdc_data, ('linux', 'i386', 'libstdc++.so.6.0.25'),),
            # ("linux_i386_static", linux_i386_static_data.static32_data, ('linux', 'i386', 'static32.llvm.elf'),),
            ("linux_arm_sh", linux_arm_sh_data.sh_data, ('linux', 'arm', 'sh'),),
            ("qnx_arm_ksh", qnx_arm_ksh_data.ksh_data, ('qnx', 'arm', 'ksh'),),
            ("openbsd_amd64_ls", openbsd_amd64_ls_data.ls_amd64_data, ('openbsd', 'ls.amd64'),),
            )

    def test_files(self):
        results = []
        for name, test_data, path in self.data:
            logger.warning("======== %r ========", name)
            start = time.time()
            fn = helpers.getTestPath(*path)
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)

            do_analyze(vw)

            logger.debug("testing %r (%r)...", name, fn)
            retval = self.do_file(vw, test_data, name)
            results.append(retval)
            durn = time.time() - start
            logger.warning(f'============= {name} took {durn} seconds ===============')

            self.do_check_elfplt(vw)

        failed = 0
        for fidx, tres in enumerate(results):
            for testname, testdata in tres.items():
                if testdata != (0, 0):
                    failed += testdata[0] + testdata[1]
                    fname = self.data[fidx][0]
                    failed_old, failed_new = testdata
                    logger.error('%s:  %s: missing: %r   new: %r (%r)', fname, testname, failed_old, failed_new, fname)

        self.assertEqual(failed, 0, msg="ELF Tests Failed (see error log)")
   
    def do_check_elfplt(self, vw):
        # Test ELFPLT entries to be uniform and all functions created
        for pltva, pltsz in vaeep.getPLTs(vw):
            # first get all the known functions that are in this PLT section
            curplts = []
            for fva in vw.getFunctions():
                if pltva <= fva < (pltva+pltsz) and fva not in curplts:
                    logger.info("PLT Function: 0x%x", fva)
                    curplts.append(fva)
            logger.info("%r", curplts)

            logger.info("curplts length: %d", len(curplts))
            if not len(curplts):
                logger.warning('skipping...')
                continue

            # accumulate the distances between PLT functions
            heur = {}
            last = pltva
            curplts.sort()
            for va in curplts:
                delta = va - last
                last = va
                
                logger.info("PLTVA: 0x%x  va: 0x%x   delta: 0x%x", pltva, va, delta)
                if delta == 0:
                    # it's the first entry, skip
                    continue

                dcnt = heur.get(delta, 0)
                heur[delta] = dcnt + 1

            # check if the first entry is odd-sized and chuck it if so
            if len(curplts) > 1:
                firstdelta = curplts[1] - curplts[0]
                if heur.get(firstdelta) == 1:
                    # it's a lone wolf, an aberration.  KILL IT!
                    heur.pop(firstdelta)

            # assert that there should be only one size between functions
            self.assertLessEqual(len(heur), 1, "More than one heuristic for %r: %r" % (vw.getMeta('StorageName'), heur))

    def check_vw_data(self, testname, baseline, observed, indx):
        observed.sort()
        baseline.sort()

        oldfail = 0
        newfail = 0
        done = set()

        # So this portion is because on windows, there's no good python equivalent for cxxfilt that I
        # can find. So we have to skip the portions of the tests that rely on decoding the names
        cmpr = lambda x, y: x == y
        if platform.system().lower() == 'windows' and testname in comparators:
            cmpr = comparators[testname]

        for base in baseline:
            va = base[indx]
            equiv = None
            done.add(va)

            if base in observed:
                continue

            for obs in observed:
                if obs[indx] == va:
                    equiv = obs
                    break

            if not equiv or not cmpr(base, equiv):
                oldfail += 1
                logger.warning("%s: o: %-80s\tn: %s" % (testname, base, equiv))

        for obs in observed:
            va = obs[indx]
            if va in done:
                continue

            equiv = None
            done.add(va)

            if obs in baseline:
                continue

            for base in baseline:
                if base[indx] == va:
                    equiv = base
                    break
            if not equiv or not cmpr(obs, equiv):
                newfail += 1
                logger.warning("%s: o: %-80s\tn: %s" % (testname, equiv, obs))

        return oldfail, newfail

    def do_file(self, vw, test_data, name):
        '''
        hand off testing to the individual test functions and return the collection of results
        '''
        results = {}
        results['imports'] = self.check_vw_data('imports', test_data['imports'], vw.getImports(), 0)
        results['exports'] = self.check_vw_data('exports', test_data['exports'], vw.getExports(), 0)
        results['relocs']  = self.check_vw_data('relocs', test_data['relocs'], vw.getRelocations(), 1)

        testnames = [ntup for ntup in genNames(vw.getNames(), vw.getFiles())]
        results['names']   = self.check_vw_data('names', test_data['names'], testnames, 0)
        # pltgot needs actual assertions
        # results['pltgot'] = self.pltgot(vw, test_data)
        return results

    def pltgot(self, vw, test_data):
        for pltva, gotva in test_data['pltgot']:
            match = False
            for xfr, xto, xtype, xinfo in vw.getXrefsFrom(pltva):
                if xfr == pltva and xto == gotva:
                    match = True

        return 0, 0

    def DISABLEtest_minimal(self):
        '''
        Until we've got some decent tests for this, all this does is prolong the test time
        '''
        for path in (('linux','amd64','static64.llvm.elf'), ('linux','i386','static32.llvm.elf')):
            logger.warning("======== %r ========", path)
            fn = helpers.getTestPath(*path)
            e = Elf.Elf(open(fn, 'rb'))
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)

name_prefix_skips = [   # (prefix, MustHavePtrPrefix),
        ('str_', False),
        ('switch_', False),
        ('case_', False),
        ('sub_', False),
        ('ptr_', False),
        ('plt_', True),
        ]

def genNames(names, fnames):
    '''
    generate a list of (va, name) tuples, sorted by va
    skipping any with prefixes
    '''
    names.sort()
    for va, name in names:
        skip = False
        #logger.warning('(%r) testing %r:', fname, name)
        # scratch variable to find if it's undesireable
        testname = name

        for fname in fnames:
            if testname.startswith('%s.'%fname):
                testname = testname[len(fname)+1:]

        # some names can get crazy pointy like "ptr_ptr_ptr_plt_..."
        pointy = False
        while testname.startswith('ptr_'):
            pointy = True
            testname = testname[4:]

        for prefix, mustptr in name_prefix_skips:
            if testname.startswith(prefix):
                if mustptr and not pointy:
                    continue
                skip = True

        if skip:
            logger.debug('   SKIP!:  %.30r      %.30r   %r', name, testname, fname)
            continue
        logger.debug('   not skip!:  %.30r      %.30r   %r', name, testname, fname)

        yield va, name
