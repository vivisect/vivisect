import logging
import unittest

import vivisect
import envi.exc as e_exc

import vivisect.tests.utils as v_t_utils

from envi.const import *


logger = logging.getLogger(__name__)


class VivMemoryTest(v_t_utils.VivTest):
    @classmethod
    def setUpClass(cls):
        cls.vw = vivisect.VivWorkspace()
        cls.vw.addMemoryMap(0x1000, MM_EXEC|MM_READ|MM_WRITE, 'foo1', b'A'*0x1000)
        cls.vw.addMemoryMap(0x2000, MM_EXEC|MM_READ, 'foo2', b'B'*0x1000)
        cls.vw.addMemoryMap(0x3000, MM_READ, 'foo3', b'C'*0x1000)
        cls.vw.addMemoryMap(0x4100, MM_READ, 'foo4', b'C'*0x1000)

    def test_memory_fails(self):
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x1000, 0x3000, MM_EXEC|MM_READ|MM_WRITE)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x3000, 0x1000, MM_EXEC|MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x1000, 0x4000, MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x3000, 0x1001, MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x3000, 0x1200, MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x400, 0x1000, MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x100, 0x3ff0, MM_READ)
        with self.assertRaises(e_exc.SegmentationViolation):
            self.vw._reqProbeMem(0x3000, 0xff0, MM_READ|MM_WRITE)

    def test_memory_success(self):
        self.vw._reqProbeMem(0x1f00, 0x300,  MM_EXEC|MM_READ)
        self.vw._reqProbeMem(0x1000, 0x2000, MM_EXEC|MM_READ)
        self.vw._reqProbeMem(0x1000, 0x3000, MM_READ)
        self.vw._reqProbeMem(0x3000, 0x1000, MM_READ)

