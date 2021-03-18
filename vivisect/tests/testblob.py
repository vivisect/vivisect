import logging
import unittest

import Elf
import envi
import vivisect.cli as viv_cli
import vivisect.tests.helpers as helpers

logger = logging.getLogger(__name__)

path = ('raw', 'arm', 'dummy.blob')


class BlobTests(unittest.TestCase):

    def test_blob(self):
        fn = helpers.getTestPath(*path)
        vw = viv_cli.VivCli()
        vw.config.viv.parsers.blob.arch = 'arm'
        vw.config.viv.parsers.blob.baseaddr = 0x200000
        vw.loadFromFile(fn)

        vw.makeFunction(0x200001)
        vw.makeFunction(0x200008)

        self.assertEqual(vw.getFunction(0x200007), 0x200000)
        self.assertEqual(vw.getFunction(0x200018), 0x200008)

