import unittest
import vivisect.hal.memory as v_memory

from vertex.lib.common import tufo

class MemoryTest(unittest.TestCase):

    def dork_memory_cache(self):
        mem = v_memory.Memory()
        mem.alloc(16384, addr=0x41410000)

        cache = v_memory.MemoryCache(mem)
        self.assertEqual(cache.peek(0x41410041, 30), b'B' * 30)

        cache.poke(0x41410041, b'V')

        self.assertEqual(cache.peek(0x41410040, 3), b'BVB')
        self.assertTrue(cache.isDirtyPage(0x41410040))
        self.assertEqual(mem.peek(0x41410040, 3), b'BBB')
        # Test a cross page read
        self.assertEqual(mem.peek(0x41410000 + (cache.pagesize - 2), 4), b'BBBB')

    def dork_mem_cache_clear(self):
        mem = v_memory.Memory()
        mem.alloc( 16384, addr=0x41410000 )

        cache = v_memory.MemoryCache(mem)

        self.assertEqual(cache.peek(0x41410041, 30), b'B' * 30)
        self.assertEqual( len(cache.getMemoryMaps()), 1 )

        sizes = cache.getCacheSizes()

        self.assertEqual( sizes['maps'], 1 )
        self.assertEqual( sizes['pages'], 1 )
        self.assertEqual( sizes['dirty'], 0 )
        self.assertEqual( sizes['pagesize'], 4096 )

        cache.poke(0x41410041, b'V')

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

        mmap = mem.alloc(4096, addr=0x42420000 )
        self.assertEqual( mem.peek( 0x42420002, 1), b'\x00')

        mmap = mem.alloc(4096, addr=0x41410000, init=b'V' * 4096)
        self.assertEqual( mem.peek( 0x41410002, 1), b'V')

        self.assertEqual( len( mem.mmaps() ), 2 )


        #self.assertEqual( mem.mmap( 0x41410002 )[1].get('size'), 4096 )

    def test_mem_free(self):

        mem = v_memory.Memory()
        mmap = mem.alloc(4096, addr=0xbffff000)

        self.assertEqual( len( mem.mmaps() ), 1 )
        self.assertIsNotNone( mem.mmap( 0xbffff001 ) )
        self.assertRaises( v_memory.MemInvalidAddr, mem.free, 0x41414141 )

        mem.free( 0xbffff000 )

        self.assertEqual( len( mem.mmaps() ), 0 )
        self.assertIsNone( mem.mmap( 0xbffff001 ) )
        self.assertRaises( v_memory.MemInvalidAddr, mem.free, 0xbffff000 )

    def test_mem_probe(self):

        mem = v_memory.Memory()
        mem.alloc(4096, addr=0x41410000, perm=v_memory.MM_RW)

        self.assertTrue( mem.probe( 0x41410001, 1, v_memory.MM_READ) )
        self.assertTrue( mem.probe( 0x41410001, 30, v_memory.MM_WRITE) )
        self.assertFalse( mem.probe( 0x41410001, 10, v_memory.MM_EXEC) )

    def test_mem_probe_xmap(self):
        mem = v_memory.Memory()
        mem.alloc(0xffff, addr=0x41410000, perm=v_memory.MM_RX)
        mem.alloc(0xffff, addr=0x41420000, perm=v_memory.MM_WX)

        self.assertTrue( mem.probe( 0x4141ffff, 2, v_memory.MM_EXEC) )
        self.assertFalse( mem.probe( 0x4141ffff, 2, v_memory.MM_READ) )
        self.assertFalse( mem.probe( 0x4141ffff, 2, v_memory.MM_WRITE) )


    def test_mem_snap_restore(self):

        mem = v_memory.Memory()
        mmap = mem.alloc(4096, init=b'A' * 4096)

        addr = mmap[0]
        mem.poke( addr + 10, b'B' )

        snap = mem.snapshot()

        mem.poke( addr + 10, b'C' )

        self.assertEqual( mem.peek( addr + 10, 1), b'C' )

        mem.restore( snap )

        self.assertEqual( mem.peek( addr + 10, 1), b'B' )

    #def test_mem_dirty(self):
