import unittest

import envi.exc as e_exc
import envi.memory as e_mem
import envi.const as e_const


class EnviMemoryTest(unittest.TestCase):

    def test_envi_memory_cache(self):
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0x41410000, e_const.MM_RWX, 'stack', b'B'*16384)

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
        mem.addMemoryMap(0x41410000, e_const.MM_RWX, 'test', b'\0'*1024)
        self.assertEqual(mem.readMemory(0x41410041, 4), b'\0\0\0\0')
        mem.writeMemory(0x41410041, b'foo')
        self.assertEqual(mem.readMemory(0x41410041, 4), b'foo\0')

        mem.delMemoryMap(0x41410000)

        # these next two tests *must* fail.  not failing would be the failure.
        self.assertRaises(e_exc.SegmentationViolation, mem.readMemory, 0x41410041, 4)
        self.assertRaises(e_exc.SegmentationViolation, mem.writeMemory, 0x41410041, b'foobar')

    def test_allocator(self):
        mem = e_mem.MemoryObject()
        mem.addMemoryMap(0x41410000, e_const.MM_RWX, 'test', b'\0'*1024)
        newmapva1 = mem.findFreeMemoryBlock(1024000)
        self.assertGreater(newmapva1, 0)

        newmapva2 = mem.allocateMemory(1024000, name='test2')
        self.assertEqual(newmapva2, newmapva1)
        self.assertEqual(newmapva2, mem.getMemoryMap(newmapva2)[0])
        self.assertEqual(b'\x00\x00\x00\x00', mem.readMemory(newmapva2, 4))

        newmapva3 = mem.allocateMemory(1024000, name='test3', fill=b'@')
        self.assertNotEqual(newmapva3, newmapva2)
        self.assertEqual(b'@@@@', mem.readMemory(newmapva3, 4))

        newmapva4 = mem.allocateMemory(1024000, suggestaddr=0x41410000, name='test4', fill=b'@')
        self.assertNotEqual(0x41410000, newmapva4)

        newmapva5 = mem.allocateMemory(1024000, perms=e_const.MM_READ, suggestaddr=0x41410000, name='test4', fill=b'@')
        with self.assertRaises(e_exc.SegmentationViolation):
            mem.writeMemory(newmapva5, "foobarbaz")

        # test to fail!  completely cheating here.
        mem.imem_psize=4
        mem._map_defs.append([0x1000, 0xffffff00, (0x1000, 0xffffff00-0x1000, 0x7, 'honkymomma'), b''])

        with self.assertRaises(e_exc.NoValidFreeMemoryFound):
            failmap = mem.allocateMemory(0x100000)


