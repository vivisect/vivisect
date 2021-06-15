import unittest

import envi.exc as e_exc
import envi.memory as e_mem


class EnviMemoryTest(unittest.TestCase):

    def test_envi_memory_cache(self):
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0x41410000, e_mem.MM_RWX, 'stack', b'B'*16384)

        cache = e_mem.MemoryCache(mem)
        self.assertEqual(cache.readMemory(0x41410041, 30), b'B' * 30)

        cache.writeMemory(0x41410041, b'V')

        self.assertEqual(cache.readMemory(0x41410040, 3), b'BVB')
        self.assertTrue(cache.isDirtyPage(0x41410040))
        self.assertEqual(mem.readMemory(0x41410040, 3), b'BBB')
        # Test a cross page read
        self.assertEqual(mem.readMemory(0x41410000 + (cache.pagesize - 2), 4), b'BBBB')

    def test_add_and_delMemoryMap(self):
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0x41410000, e_mem.MM_RWX, 'test', b'\0'*1024)
        self.assertEqual(mem.readMemory(0x41410041, 4), b'\0\0\0\0')
        mem.writeMemory(0x41410041, b'foo')
        self.assertEqual(mem.readMemory(0x41410041, 4), b'foo\0')

        mem.delMemoryMap(0x41410000)

        # these next two tests *must* fail.  not failing would be the failure.
        try:
            mem.readMemory(0x41410041, 4)
            self.assertEqual("Failed to Delete Map (can read)", True)

        except e_exc.SegmentationViolation:
            pass

        try:
            mem.writeMemory(0x41410041, b'foobar')
            self.assertEqual("Failed to Delete Map (can write)", True)

        except e_exc.SegmentationViolation:
            pass
