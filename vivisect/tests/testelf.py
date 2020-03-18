import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
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
            e = Elf.Elf(file(fn))
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
        for name, test_data, fn, e, vw in self.tests:
            logger.debug("testing %r (%r)...", name, fn)
            self.do_file(vw, test_data, name)

    def do_file(self, vw, data, fname):
        self.imports(vw, data, fname)
        self.exports(vw, data, fname)
        self.relocs(vw, data, fname)
        self.names(vw, data, fname)
        self.pltgot(vw, data, fname)
        self.debuginfosyms(vw, data, fname)

    def imports(self, vw, data, fname):
        # simple comparison to ensure same imports.  perhaps too simple.
        newimps = vw.getImports()
        newimps.sort()
        oldimps = data['imports']
        oldimps.sort()
        for oldimp in oldimps:
            self.assertIn(oldimp, newimps, msg='imports: missing: %r   (%r)' % (oldimp, fname))
        for newimp in newimps:
            self.assertIn(newimp, oldimps, msg='imports: new: %r   (%r)' % (newimp, fname))

    def exports(self, vw, data, fname):
        # simple comparison to ensure same exports.  perhaps too simple.
        newexps = vw.getExports()
        newexps.sort()
        oldexps = data['exports']
        oldexps.sort()
        for oldexp in oldexps:
            self.assertIn(oldexp, newexps, msg='exports: missing: %r   (%r)' % (oldexp, fname))
        for newexp in newexps:
            self.assertIn(newexp, oldexps, msg='exports:  new: %r   (%r)' % (newexp, fname))

    def relocs(self, vw, data, fname):
        # simple comparison to ensure same relocs.  perhaps too simple.
        newrels = vw.getRelocations()
        newrels.sort()
        oldrels = data['relocs']
        oldrels.sort()
        for oldrel in oldrels:
            self.assertIn(oldrel, newrels, msg='relocs: missing: %r   (%r)' % (oldrel, fname))
        for newrel in newrels:
            self.assertIn(newrel, oldrels, msg='relocs:  new: %r   (%r)' % (newrel, fname))


    def names(self, vw, data, fname):
        # simple comparison to ensure same workspace names.  perhaps too simple.
        newnames = vw.getNames()
        newnames.sort()
        oldnames = data['names']
        oldnames.sort()
        self.assertListEqual(newnames, newnames)
        for oldname in oldnames:
            if oldname[1].startswith('str_') or oldname[1].startswith('ptr_str_') \
                    or oldname[1].startswith('ptr_sub_') or oldname[1].startswith('sub_'):
                continue
            self.assertIn(oldname, newnames, msg='names: missing: %r   (%r)' % (oldname, fname))
        for newname in newnames:
            if newname[1].startswith('str_') or newname[1].startswith('ptr_str_') \
                    or newname[1].startswith('ptr_sub_') or newname[1].startswith('sub_'):
                continue
            self.assertIn(newname, oldnames, msg='names: new: %r   (%r)' % (newname, fname))

    def pltgot(self, vw, data, fname):
        for pltva, gotva in data['pltgot']:
            match = False
            for xfr, xto, xtype, xinfo in vw.getXrefsFrom(pltva):
                if xfr == pltva and xto == gotva:
                    match = True
            self.assertEqual((hex(pltva), match), (hex(pltva), True), msg='pltgot: %r' % fname)

    def debuginfosyms(self, vw, data, fname):
        # we don't currently parse debugging symbols.
        # while they are seldom in hard targets, this is a weakness we should correct.
        pass

    def test_minimal(self):
        for path in (('linux','amd64','static64.llvm.elf'), ('linux','i386','static32.llvm.elf')):
            logger.warn("======== %r ========", path)
            fn = helpers.getTestPath(*path)
            e = Elf.Elf(file(fn))
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)

