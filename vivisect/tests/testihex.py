import logging
import unittest

import vivisect.cli as viv_cli
import vivisect.tests.helpers as helpers

logger = logging.getLogger(__name__)

path = ('raw', 'msp430', 'blink.hex')


class IHexTests(unittest.TestCase):

    def test_ihex(self):
        fn = helpers.getTestPath(*path)
        vw = viv_cli.VivCli()
        vw.config.viv.parsers.ihex.arch = 'msp430'
        vw.loadFromFile(fn)

        vw.makeFunction(0x4000)

        self.assertEqual(vw.getFunction(0x4000), 0x4000)
        self.assertEqual(vw.getFunction(0x4050), 0x4000)
        self.assertEqual(vw.getFunction(0x4060), 0x405e)
        self.assertEqual(vw.getFunction(0x4068), 0x405e)
