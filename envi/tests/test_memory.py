import unittest

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
