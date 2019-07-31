import logging
import unittest

import Elf
import vivisect.cli as viv_cli
import vivisect.tests.helpers as helpers
import vivisect.analysis.elf.elfplt as vaeep
import vivisect.analysis.generic.pointers as vagp

from vivisect.tests import linux_amd64_ls_data
from vivisect.tests import linux_amd64_chown_data
from vivisect.tests import linux_amd64_libc_2_27_data
from vivisect.tests import linux_amd64_libstdc_data
from vivisect.tests import linux_i386_libc_2_13_data
from vivisect.tests import linux_i386_libstdc_data
from vivisect.tests import linux_arm_sh_data
from vivisect.tests import qnx_arm_ksh_data
from vivisect.tests import openbsd_amd64_ls_data

data = (("linux_amd64_ls", linux_amd64_ls_data.ls_data, ('linux', 'amd64', 'ls'), ),
        ("linux_amd64_chown", linux_amd64_chown_data.chown_data, ('linux', 'amd64', 'chown'),),
        ("linux_amd64_libc", linux_amd64_libc_2_27_data.libc_data, ('linux', 'amd64', 'libc-2.27.so'),),
        ("linux_amd64_libstdc", linux_amd64_libstdc_data.libstdc_data, ('linux', 'amd64', 'libstdc++.so.6.0.25'),),
        ("linux_i386_libc", linux_i386_libc_2_13_data.libc_data, ('linux', 'i386', 'libc-2.13.so'),),
        ("linux_i386_libstdc", linux_i386_libstdc_data.libstdc_data, ('linux', 'i386', 'libstdc++.so.6.0.25'),),
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
            fn = helpers.getTestPath(*path)
            e = Elf.Elf(file(fn))
            vw = viv_cli.VivCli()
            vw.loadFromFile(fn)
            vw.analyze()
            #vaeep.analyze(vw)
            #vagp.analyze(vw)

            cls.tests.append((name, test_data, fn, e, vw))

        cls.maxDiff = None

    def test_files(self):
        for name, test_data, fn, e, vw in self.tests:
            logger.debug("testing %r (%r)...", name, fn)
            self.do_file(vw, test_data)

    def do_file(self, vw, data):
        self.imports(vw, data)
        self.exports(vw, data)
        self.relocs(vw, data)
        self.names(vw, data)
        self.pltgot(vw, data)
        self.debuginfosyms(vw, data)

    def imports(self, vw, data):
        # simple comparison to ensure same imports.  perhaps too simple.
        newimps = vw.getImports()
        newimps.sort()
        oldimps = data['imports']
        oldimps.sort()
        self.assertListEqual(newimps, oldimps)

    def exports(self, vw, data):
        # simple comparison to ensure same exports.  perhaps too simple.
        newexps = vw.getExports()
        newexps.sort()
        oldexps = data['exports']
        oldexps.sort()
        self.assertListEqual(newexps, oldexps)

    def relocs(self, vw, data):
        # simple comparison to ensure same relocs.  perhaps too simple.
        newrels = vw.getRelocations()
        newrels.sort()
        oldrels = data['relocs']
        oldrels.sort()
        self.assertListEqual(newrels, newrels)

    def names(self, vw, data):
        # simple comparison to ensure same workspace names.  perhaps too simple.
        newnames = vw.getRelocations()
        newnames.sort()
        oldnames = data['names']
        oldnames.sort()
        self.assertListEqual(newnames, newnames)

    def pltgot(self, vw, data):
        for pltva, gotva in data['pltgot']:
            match = False
            for xfr, xto, xtype, xinfo in vw.getXrefsFrom(pltva):
                if xfr == pltva and xto == gotva:
                    match = True
            self.assertEqual((hex(pltva), match), (hex(pltva), True))

    def debuginfosyms(self, vw, data):
        # we don't currently parse debugging symbols.
        # while they are seldom in hard targets, this is a weakness we should correct.
        pass


