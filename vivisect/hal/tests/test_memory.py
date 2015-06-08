import unittest
import vivisect.hal.memory as v_memory

from vertex.lib.common import tufo

class MemoryTest(unittest.TestCase):

    def dork_memory_cache(self):
        mem = v_memory.Memory()
        mem.initMemoryMap(0x41410000, 16384)

        cache = v_memory.MemoryCache(mem)
        self.assertEqual(cache.readMemory(0x41410041, 30), b'B' * 30)

        cache.writeMemory(0x41410041, b'V')

        self.assertEqual(cache.readMemory(0x41410040, 3), b'BVB')
        self.assertTrue(cache.isDirtyPage(0x41410040))
        self.assertEqual(mem.readMemory(0x41410040, 3), b'BBB')
        # Test a cross page read
        self.assertEqual(mem.readMemory(0x41410000 + (cache.pagesize - 2), 4), b'BBBB')

    def dork_mem_cache_clear(self):
        mem = v_memory.Memory()
        mem.initMemoryMap(0x41410000, 16384)

        cache = v_memory.MemoryCache(mem)

        self.assertEqual(cache.readMemory(0x41410041, 30), b'B' * 30)
        self.assertEqual( len(cache.getMemoryMaps()), 1 )

        sizes = cache.getCacheSizes()

        self.assertEqual( sizes['maps'], 1 )
        self.assertEqual( sizes['pages'], 1 )
        self.assertEqual( sizes['dirty'], 0 )
        self.assertEqual( sizes['pagesize'], 4096 )

        cache.writeMemory(0x41410041, b'V')

        self.assertEqual( cache.getCacheSizes()['dirty'], 1 )

        cache.clearCache()

        sizes = cache.getCacheSizes()
        self.assertEqual( sizes['maps'], 0 )
        self.assertEqual( sizes['pages'], 0 )
        self.assertEqual( sizes['dirty'], 0 )
        self.assertEqual( sizes['pagesize'], 4096 )

    def test_mem_copyonwrite(self):

        buf = bytearray(b'A'*8192)
        cow = v_memory.CopyOnWrite(buf, pagesize=4096)

        self.assertEqual( cow[0], buf[0] )

        cow[4090:4100] = b'V'*100

        self.assertEqual( cow[4090:4100], b'V'*10 )
        self.assertEqual( cow[4095:4105], b'V' * 5 + b'A' * 5 )

        self.assertEqual( buf[4090:4100], b'A'*10 )

    def test_mem_alloc(self):

        mem = v_memory.Memory()

        mmap = mem.allocMemory(4096, addr=0x42420000 )
        self.assertEqual( mem.readMemory( 0x42420002, 1), b'\x00')

        mmap = mem.allocMemory(4096, addr=0x41410000, init=b'V' * 4096)
        self.assertEqual( mem.readMemory( 0x41410002, 1), b'V')

        self.assertEqual( len( mem.getMemoryMaps() ), 2 )


        #self.assertEqual( mem.getMemoryMap( 0x41410002 )[1].get('size'), 4096 )

    def test_mem_free(self):

        mem = v_memory.Memory()
        mmap = mem.allocMemory(4096, addr=0xbffff000)

        self.assertEqual( len( mem.getMemoryMaps() ), 1 )
        self.assertIsNotNone( mem.getMemoryMap( 0xbffff001 ) )
        self.assertRaises( v_memory.MemInvalidAddr, mem.freeMemory, 0x41414141 )

        mem.freeMemory( mmap[0] )

        self.assertEqual( len( mem.getMemoryMaps() ), 0 )
        self.assertIsNone( mem.getMemoryMap( 0xbffff001 ) )
        self.assertRaises( v_memory.MemInvalidAddr, mem.freeMemory, 0xbffff000 )

    def test_mem_probe(self):

        mem = v_memory.Memory()
        mem.initMemoryMap(0x41410000, 4096, perm=v_memory.MM_RW)

        self.assertTrue( mem.probeMemory( 0x41410001, v_memory.MM_READ, size=1) )
        self.assertTrue( mem.probeMemory( 0x41410001, v_memory.MM_WRITE, size=30) )
        self.assertFalse( mem.probeMemory( 0x41410001, v_memory.MM_EXEC, size=10) )

    def test_mem_probe_xmap(self):
        mem = v_memory.Memory()
        mem.initMemoryMap(0x41410000, 0x10000, perm=v_memory.MM_RX)
        mem.initMemoryMap(0x41420000, 0x10000, perm=v_memory.MM_WX)

        self.assertTrue( mem.probeMemory( 0x4141ffff, v_memory.MM_EXEC, size=2) )
        self.assertFalse( mem.probeMemory( 0x4141ffff, v_memory.MM_READ, size=2) )
        self.assertFalse( mem.probeMemory( 0x4141ffff, v_memory.MM_WRITE, size=2) )

    def test_mem_snap_restore(self):

        mem = v_memory.Memory()
        mmap = mem.initMemoryMap(0x41410000, 4096, init=b'A' * 4096)

        addr = mmap[0]
        mem.writeMemory( addr + 10, b'B' )

        snap = mem.getMemorySnap()

        mem.writeMemory( addr + 10, b'C' )

        self.assertEqual( mem.readMemory( addr + 10, 1), b'C' )

        mem.setMemorySnap( snap )

        self.assertEqual( mem.readMemory( addr + 10, 1), b'B' )

    #def test_mem_dirty(self):
