import unittest
import vivisect.hal.memory as v_memory

class MemoryTest(unittest.TestCase):

    def test_memory_cache(self):
        mem = v_memory.Memory()
        mem.addMemoryMap(0x41410000, v_memory.MM_RWX, 'stack', b'B'*16384)

        cache = v_memory.MemoryCache(mem)
        self.assertEqual(cache.readMemory(0x41410041, 30), b'B' * 30)

        cache.writeMemory(0x41410041, b'V')

        self.assertEqual(cache.readMemory(0x41410040, 3), b'BVB')
        self.assertTrue(cache.isDirtyPage(0x41410040))
        self.assertEqual(mem.readMemory(0x41410040, 3), b'BBB')
        # Test a cross page read
        self.assertEqual(mem.readMemory(0x41410000 + (cache.pagesize - 2), 4), b'BBBB')
