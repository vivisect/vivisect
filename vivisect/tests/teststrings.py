import logging

import vivisect

import vivisect.tests.utils as v_t_utils

from envi.const import MM_READ


logger = logging.getLogger(__name__)


class VivStringsTest(v_t_utils.VivTest):
    @classmethod
    def setUpClass(cls):
        cls.vw = vivisect.VivWorkspace()
        # ; segment "mem":
        # 0x1000: 00 00 00 00 ...
        # 0x1010: 00 00 00 00 ...
        # ...
        # 0x10F0: 00 00 00 00 ...
        # 0x1100: 41 41 41 41 ...  ; string "AAAA..." at 0x1100
        # ...
        # 0x11F0: 41 41 41 41 ...
        # 0x1200: 00 00 00 00 ...
        # ...
        # 0x1FF0: 00 00 00 00 ...
        mem = (b"\x00" * 0x100) + (b"A" * 0x100) + (b"\x00" * 0xE00)
        cls.vw.addMemoryMap(0x1000, MM_READ, 'mem', mem)

    def test_overlapping_strings(self):
        """demonstrate string detection works with overlapping strings"""
        self.vw.makeString(0x1100)

        # string is 0x100 "A" characters and a trailing NULL byte,
        # so 0x101 total size.
        self.eq(self.vw.detectString(0x1100), 0x101)

        # naturally, the overlapping substrings should have
        # sizes smaller than the string at 0x1100.
        for i in range(0x100):
            self.eq(self.vw.detectString(0x1100 + i), 0x101 - i)
