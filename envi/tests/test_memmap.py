import unittest

import envi.exc as e_exc
import envi.const as e_const
import envi.memory as e_memory

class Memory(unittest.TestCase):
    def setUp(self):
        self.mem = e_memory.MemoryObject()

    def test_getMaxReadSize(self):
        mmaps = [(0,  e_const.MM_READ, None, 0x1000 * b'\x41'),
                 (0x1000, e_const.MM_READ, None, 0x500 * b'\x42'),
                 # gap
                 (0x2000, e_const.MM_READ, None, 0x100 * b'\x43'),
                 (0x2100, e_const.MM_NONE, None, 0x1000 * b'\x44'),
                 (0x3100, e_const.MM_READ, None, 0x200 * b'\x45')]

        # reverse the list just to make sure we aren't making assumptions
        # about ascending order.
        mmaps = reversed(mmaps)
        for mmap in mmaps:
            self.mem.addMemoryMap(*mmap)

        # (va, known max read size)
        answers = [(0, 0x1500),  # across contiguous maps
                   (0x1000, 0x500),  # an entire map
                   (0x2100, 0),  # va inside map without MM_READ
                   (0x2000, 0x100),  # borders map without MM_READ
                   (10, 0x1500-10),  # offsets inside single maps
                   (0x1001, 0x4ff),
                   (0x2050, 0x2100-0x2000-0x50),
                   (0x2150, 0),
                   (0xffff, 0),  # last va in map
                   (0x2fff, 0),  # last va in map
                   (0x123456789, 0)]  # no mans land.

        for va, answer in answers:
            size = self.mem.getMaxReadSize(va)

            self.assertEqual(answer, size)

    def test_cohesive_mmaps(self):
        mmaps = [
                (0x2000, e_const.MM_READ_WRITE, None, 0x100 * b'\x43'),
                (0x2100, e_const.MM_RWX, None, 0x1000 * b'\x44'),
                (0x3100, e_const.MM_READ_WRITE, None, 0x200 * b'\x45'),
                ]

        # reverse the list just to make sure we aren't making assumptions
        # about ascending order.
        mmaps = reversed(mmaps)
        for mmap in mmaps:
            self.mem.addMemoryMap(*mmap)

        # test writing 
        self.mem.writeMemory(0x20f0, b'@' * 0x20)
        self.assertEqual(self.mem.readMemory(0x20f0, 0x10), b'@'*0x10)
        self.assertEqual(self.mem.readMemory(0x2100, 0x10), b'@'*0x10)

        # test reading
        self.assertEqual(self.mem.readMemory(0x20f0, 0x20), b'@'*0x20)

    def test_cross_map_failure(self):
        mmaps = [
                (0x2000, e_const.MM_READ, None, 0x100 * b'\x43'),
                (0x2100, e_const.MM_RWX, None, 0x100 * b'\x44'),
                (0x2200, e_const.MM_WRITE, None, 0x100 * b'\x45'),
                (0x2300, e_const.MM_READ, None, 0x100 * b'\x46'),
                ]

        # reverse the list just to make sure we aren't making assumptions
        # about ascending order.  alternately, we could make addMemoryMap
        # sort them every time.
        mmaps = reversed(mmaps)
        for mmap in mmaps:
            self.mem.addMemoryMap(*mmap)

        # test write failure
        self.assertRaises(e_exc.SegmentationViolation, self.mem.writeMemory, 0x2100, b'@' * 0x220)
        self.assertEqual(self.mem.readMemory(0x2100, 0x100), b"@" * 0x100)
        self.assertEqual(self.mem.readMemory(0x2300, 0x100), b"\x46" * 0x100)

        # test read failure
        self.assertRaises(e_exc.SegmentationViolation, self.mem.readMemory, 0x20f0, 0x200)
