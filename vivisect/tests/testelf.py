import time
import logging
import unittest

import Elf
import vivisect.cli as viv_cli
import vivisect.tests.helpers as helpers
import vivisect.analysis.elf as vae
import vivisect.analysis.elf.elfplt as vaeep
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
    for mod in vae, vagr, vaeep, vagp:
        try:
            mod.analyze(vw)
        except Exception as e:
            import traceback
            logging.warning("ERROR in analysis module: (%r): %r", mod, e)
            logging.warning(traceback.format_exc())


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

        failed = 0
        for fidx, tres in enumerate(results):
            for testname, testdata in tres.items():
                if testdata != (0, 0):
                    failed += testdata[0] + testdata[1]
                    fname = self.data[fidx][0]
                    failed_old, failed_new = testdata
                    logger.error('%s:  %s: missing: %r   new: %r (%r)', fname, testname, failed_old, failed_new, fname)

        self.assertEqual(failed, 0, msg="ELF Tests Failed (see error log)")


    def do_file(self, vw, test_data, name):
        '''
        hand off testing to the individual test functions and return the collection of results
        '''
        results = {}
        results['imports'] = self.imports(vw, test_data)
        results['exports'] = self.exports(vw, test_data)
        results['relocs'] = self.relocs(vw, test_data)
        results['names'] = self.names(vw, test_data)
        results['pltgot'] = self.pltgot(vw, test_data)
        results['debugsyms'] = self.debuginfosyms(vw, test_data)
        return results

    def imports(self, vw, test_data):
        # simple comparison to ensure same imports
        newimps = vw.getImports()
        newimps.sort()
        oldimps = test_data['imports']
        oldimps.sort()

        failed_new = 0
        failed_old = 0
        done = []
        for oldimp in oldimps:
            va = oldimp[0]
            equiv = None
            for newimp in newimps:
                if newimp[0] == va:
                    equiv = newimp
                    break
            if oldimp != equiv:
                failed_old += 1
                logger.warning("imports: o: %-50s\tn: %s" % (oldimp, equiv))
            done.append(va)

        for newimp in newimps:
            va = newimp[0]
            if va in done:
                continue

            equiv = None
            for oldimp in oldimps:
                if oldimp[0] == va:
                    equiv = oldimp
                    break
            if newimp != equiv:
                failed_new += 1
                logger.warning("imports: o: %-50s\tn: %s" % (equiv, newimp))
            done.append(va)

        return failed_old, failed_new

    def exports(self, vw, test_data):
        # simple comparison to ensure same exports
        newexps = vw.getExports()
        newexps.sort()
        oldexps = test_data['exports']
        oldexps.sort()

        # warning: there may be multiple exports for each VA.
        # perhaps move to checking "names"
        failed_new = 0
        failed_old = 0
        done = []
        for oldexp in oldexps:
            va = oldexp[0]
            equiv = None
            done.append(va)

            if oldexp in newexps:
                continue

            for newexp in newexps:
                if newexp[0] == va:
                    equiv = newexp
                    break
            if oldexp != equiv:
                failed_old += 1
                logger.warning("exp: o: %-80s\tn: %s" % (oldexp, equiv))

        for newexp in newexps:
            va = newexp[0]
            if va in done:
                continue

            equiv = None
            done.append(va)

            # simple check
            if newexp in oldexps:
                continue

            # comprehensive check
            for oldexp in oldexps:
                if oldexp[0] == va:
                    equiv = oldexp
                    break
            if newexp != equiv:
                failed_new += 1
                logger.warning("exp: o: %-80s\tn: %s" % (equiv, newexp))

        return failed_old, failed_new

    def relocs(self, vw, test_data):
        # simple comparison to ensure same relocs
        newrels = vw.getRelocations()
        newrels.sort()
        oldrels = test_data['relocs']
        oldrels.sort()

        failed_new = 0
        failed_old = 0
        done = []
        for oldrel in oldrels:
            va = oldrel[1]
            equiv = None
            for newrel in newrels:
                if newrel[1] == va:
                    equiv = newrel
                    break
            if oldrel != equiv:
                failed_old += 1
                logger.warning("rel: o: %-80s\tn: %s" % (oldrel, equiv))
            done.append(va)

        for newrel in newrels:
            va = newrel[1]
            if va in done:
                continue

            equiv = None
            for oldrel in oldrels:
                if oldrel[1] == va:
                    equiv = oldrel
                    break
            if newrel != equiv:
                failed_new += 1
                logger.warning("rel: o: %-80s\tn: %s" % (equiv, newrel))
            done.append(va)

        return failed_old, failed_new


    def names(self, vw, test_data):
        # comparison to ensure same workspace names

        # filter out a lot of noise not likely to be indicative of ELF bugs.
        newnames = [ntup for ntup in genNames(vw.getNames(), vw.getFiles())]
        oldnames = test_data['names']
        oldnames.sort()

        failed_new = 0
        failed_old = 0
        done = []
        for oldname in oldnames:
            va = oldname[0]
            equiv = None
            done.append(va)

            for newname in newnames:
                if newname[0] == va:
                    equiv = newname
                    break
            if oldname != equiv:
                failed_old += 1
                logger.error("name: o: %-80s\tn: %s" % (oldname, equiv))

        for newname in newnames:
            va = newname[0]
            if va in done:
                continue

            equiv = None
            done.append(va)

            for oldname in oldnames:
                if oldname[0] == va:
                    equiv = oldname
                    break
            if newname != equiv:
                failed_new += 1
                logger.error("name: o: %-80s\tn: %s" % (equiv, newname))

        return failed_old, failed_new

    def pltgot(self, vw, test_data):
        for pltva, gotva in test_data['pltgot']:
            match = False
            for xfr, xto, xtype, xinfo in vw.getXrefsFrom(pltva):
                if xfr == pltva and xto == gotva:
                    match = True

        return 0, 0

    def debuginfosyms(self, vw, test_data):
        # we don't currently parse debugging symbols.
        # while they are seldom in hard targets, this is a weakness we should correct.
        return 0, 0

    def DISABLEtest_minimal(self):
        '''
        Until we've got soe decent tests for this, all this does is prolong the test time
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
