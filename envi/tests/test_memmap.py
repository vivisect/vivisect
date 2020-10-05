import unittest

import envi.memory

class Memory(unittest.TestCase):
    def setUp(self):
        self.mem = envi.memory.MemoryObject()

    def test_getMaxReadSize(self):
        mmaps = [(0,  envi.memory.MM_READ, None, 0x1000 * b'\x41'),
                 (0x1000, envi.memory.MM_READ, None, 0x500 * b'\x42'),
                 # gap
                 (0x2000, envi.memory.MM_READ, None, 0x100 * b'\x43'),
                 (0x2100, envi.memory.MM_NONE, None, 0x1000 * b'\x44'),
                 (0x3100, envi.memory.MM_READ, None, 0x200 * b'\x45')]

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
