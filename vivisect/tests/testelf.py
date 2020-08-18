import logging
import unittest

import envi
logger = logging.getLogger(__name__)

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

data = (
        ("linux_amd64_ls", linux_amd64_ls_data.ls_data, ('linux', 'amd64', 'ls'), ),
        ("linux_amd64_chown", linux_amd64_chown_data.chown_data, ('linux', 'amd64', 'chown'),),
        ("linux_amd64_libc", linux_amd64_libc_2_27_data.libc_data, ('linux', 'amd64', 'libc-2.27.so'),),
        ("linux_amd64_libstdc", linux_amd64_libstdc_data.libstdc_data, ('linux', 'amd64', 'libstdc++.so.6.0.25'),),
        #("linux_amd64_static", linux_amd64_static_data.static64_data, ('linux', 'amd64', 'static64.llvm.elf'),),
        ("linux_i386_libc", linux_i386_libc_2_13_data.libc_data, ('linux', 'i386', 'libc-2.13.so'),),
        ("linux_i386_libstdc", linux_i386_libstdc_data.libstdc_data, ('linux', 'i386', 'libstdc++.so.6.0.25'),),
        #("linux_i386_static", linux_i386_static_data.static32_data, ('linux', 'i386', 'static32.llvm.elf'),),
        ("linux_arm_sh", linux_arm_sh_data.sh_data, ('linux', 'arm', 'sh'),),
        ("qnx_arm_ksh", qnx_arm_ksh_data.ksh_data, ('qnx', 'arm', 'ksh'),),
        ("openbsd_amd64_ls", openbsd_amd64_ls_data.ls_amd64_data, ('openbsd', 'ls.amd64'),),
        )

logger = logging.getLogger(__name__)


class ELFTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(ELFTests, cls).setUpClass()

        cls.tests = []
        for test in data:
            name, test_data, path = test
            logger.warn("======== %r ========", name)
            fn = helpers.getTestPath(*path)
            e = Elf.Elf(open(fn))
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)
            #vw.analyze()
            vae.analyze(vw)
            vagr.analyze(vw)
            vaeep.analyze(vw)
            vagp.analyze(vw)

            cls.tests.append((name, test_data, fn, e, vw))

        cls.maxDiff = None

    def test_files(self):
        results = []
        for name, test_data, fn, e, vw in self.tests:
            logger.debug("testing %r (%r)...", name, fn)
            retval = self.do_file(vw, test_data, name)
            results.append(retval)

        failed = False
        for fidx, tres in enumerate(results):
            for testname, testdata in tres.items():
                if testdata != (0, 0):
                    failed = True
                    fname = data[fidx][0]
                    failed_old, failed_new = testdata
                    logger.error('%s:  %s: missing: %r   new: %r (%r)', fname, testname, failed_old, failed_new, fname)

        self.assertEqual(failed, False, msg="ELF Tests Failed (see error log)")


    def do_file(self, vw, data, fname):
        '''
        hand off testing to the individual test functions and return the collection of results
        '''
        results = {}
        results['imports'] = self.imports(vw, data, fname)
        results['exports'] = self.exports(vw, data, fname)
        results['relocs'] = self.relocs(vw, data, fname)
        results['names'] = self.names(vw, data, fname)
        results['pltgot'] = self.pltgot(vw, data, fname)
        results['debugsyms'] = self.debuginfosyms(vw, data, fname)
        return results

    def imports(self, vw, data, fname):
        # simple comparison to ensure same imports
        newimps = vw.getImports()
        newimps.sort()
        oldimps = data['imports']
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
                logger.warn("imports: o: %-50s\tn: %s" % (oldimp, equiv))
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
                logger.warn("imports: o: %-50s\tn: %s" % (equiv, newimp))
            done.append(va)

        return failed_old, failed_new

    def exports(self, vw, data, fname):
        # simple comparison to ensure same exports
        newexps = vw.getExports()
        newexps.sort()
        oldexps = data['exports']
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
                logger.warn("exp: o: %-80s\tn: %s" % (oldexp, equiv))

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
                logger.warn("exp: o: %-80s\tn: %s" % (equiv, newexp))

        return failed_old, failed_new

    def relocs(self, vw, data, fname):
        # simple comparison to ensure same relocs
        newrels = vw.getRelocations()
        newrels.sort()
        oldrels = data['relocs']
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
                logger.warn("rel: o: %-80s\tn: %s" % (oldrel, equiv))
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
                logger.warn("rel: o: %-80s\tn: %s" % (equiv, newname))
            done.append(va)

        return failed_old, failed_new


    def names(self, vw, data, fname):
        # comparison to ensure same workspace names

        # filter out a lot of noise not likely to be indicative of ELF bugs.
        newnames = [ntup for ntup in vw.getNames() if not (
                ntup[1].startswith('str_') or
                ntup[1].startswith('ptr_str_') or
                ntup[1].startswith('ptr_sub_') or
                ntup[1].startswith('sub_'))]

        newnames.sort()
        oldnames = data['names']
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
                logger.warn("name: o: %-80s\tn: %s" % (oldname, equiv))

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
                logger.warn("name: o: %-80s\tn: %s" % (equiv, newname))

        return failed_old, failed_new

    def pltgot(self, vw, data, fname):
        for pltva, gotva in data['pltgot']:
            match = False
            for xfr, xto, xtype, xinfo in vw.getXrefsFrom(pltva):
                if xfr == pltva and xto == gotva:
                    match = True

        return 0,0

    def debuginfosyms(self, vw, data, fname):
        # we don't currently parse debugging symbols.
        # while they are seldom in hard targets, this is a weakness we should correct.
        return 0,0

    def test_minimal(self):
        for path in (('linux','amd64','static64.llvm.elf'), ('linux','i386','static32.llvm.elf')):
            logger.warn("======== %r ========", path)
            fn = helpers.getTestPath(*path)
            e = Elf.Elf(open(fn, 'rb'))
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)

