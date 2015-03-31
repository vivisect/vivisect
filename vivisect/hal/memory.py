'''
Vivisect machine abstraction for memory interfaces.
'''
import synapse.event.dist as s_evtdist
import vivisect.lib.pagelook as v_pagelook

from vertex.lib.common import tufo

# Memory Map Permission Flags
MM_NONE     = 0x0
MM_EXEC     = 0x1
MM_WRITE    = 0x2
MM_READ     = 0x4
MM_SHARED   = 0x08

MM_RW = MM_READ | MM_WRITE
MM_RX  = MM_READ | MM_EXEC
MM_WX  = MM_WRITE | MM_EXEC
MM_RWX = MM_READ | MM_WRITE | MM_EXEC

class MemPermsError(Exception):pass
class MemInvalidAddr(Exception):pass

#pnames = ['No Access', 'Execute', 'Write', None, 'Read']
#def getPermName(perm):
    #'''
    #Return the human readable name for a *single* memory
    #perm enumeration value.
    #'''
    #return pnames[perm]

permstrs = [
  ('rwx', MM_RWX),('r--', MM_READ),('-w-', MM_WRITE), ('--x', MM_EXEC),
  ('rw-', MM_RW), ('r-x', MM_RX), ('-wx', MM_WX),
  ('--x', MM_EXEC), ('---', MM_NONE),
]

repr2perm = { a.replace('-',''):b for (a,b) in permstrs }
perm2repr = { b:a for (a,b) in permstrs }

def reprPerms(mask):
    return perm2repr.get(mask,'???')

def parsePerms(pstr):
    return repr2perm.get(pstr,0)

class PageCache:

    def __init__(self, pagesize=4096):
        self.pages = {}
        self.pagesize = pagesize

        self.offmask =  pagesize - 1
        self.pagemask = ~ ( pagesize - 1 )

    def _load_page(self, addr):
        raise Exception('PageCache._load_page')

    def __len__(self):
        raise Exception('PageCache.__len__')

    def _get_page(self, addr):
        page = self.pages.get(addr)
        if page == None:
            page = self._load_page(addr)
            self.pages[addr] = page

        return page

    def _iter_bases(self, off, end):
        # yield base,off,size tuples
        while off < end:
            choff = off & self.offmask
            chbase = off & self.pagemask
            chsize = min( end - off, self.pagesize - choff)

            yield chbase,choff,chsize
            off += chsize

    def _get_slice_bounds(self, item):
        off = item.start

        if off == None:
            off = 0

        end = item.stop
        if end == None:
            end = len(self)

        return off,end

    def _cache_peek(self, addr, size):
        ret = b''
        for base,off,size in self._iter_bases(addr,addr + size):
            page = self._get_page(base)
            ret += page[off:off+size]

        return ret

    def _cache_poke(self, addr, byts):
        valuoff = 0
        for base,off,size in self._iter_bases(addr,addr + len(byts)):
            page = self._get_page(base)
            page[off:off+size] = valu[valuoff:valuoff+size]
            valuoff += size

        return

    def __getitem__(self, item):

        if isinstance(item,slice):
            start,end = self._get_slice_bounds(item)

            ret = b''
            for base,off,size in self._iter_bases(start,end):
                page = self._get_page(base)
                ret += page[off:off+size]

            return ret

        off = item & self.offmask
        base = item & self.pagemask
        page = self._get_page(base)

        return page[off]

    def __setitem__(self, item, valu):

        if isinstance(item, slice):
            start,end = self._get_slice_bounds(item)
            end = min( start + len(valu), end )

            valuoff = 0
            for base,off,size in self._iter_bases(start,end):
                page = self._get_page(base)
                page[off:off+size] = valu[valuoff:valuoff+size]
                valuoff += size

            return

        off = item & self.offmask
        base = item & self.pagemask
        page = self._get_page(base)

        page[off] = valu


class CopyOnWrite(PageCache):
    '''
    Implements a page-oriented copy-on-write buffer-like object wrapper.
    '''
    def __init__(self, buf, pagesize=4096):
        self.realbuf = buf
        PageCache.__init__(self)

    def __len__(self):
        return len(self.realbuf)

    def _load_page(self, addr):
        return self.realbuf[addr:addr + self.pagesize]

class Memory(s_evtdist.EventDist):

    def __init__(self, pagesize=4096, **info):
        s_evtdist.EventDist.__init__(self)

        self._mem_maps = {}
        self._mem_info = info
        self._mem_bytes = {}

        self._mem_pagelook = v_pagelook.PageLook(pagesize=pagesize)

        self._mem_dirty = {}
        self._mem_pagesize = pagesize
        self._mem_pagemask = ~ (pagesize - 1)

    def free(self, addr):
        '''
        Free/Release the memory map with the given base addr.

        Example:

            mem.free( addr )

        '''

        return self._mem_free(addr)

    def alloc(self, size, perm=MM_RWX, addr=None, **info):
        '''
        Allocate a new memory map within the Memory object and return the map.

        Example:

            wantaddr = 0x41414141

            mmap = mem.alloc(4096, addr=wantaddr)

            print('alloc at: 0x%.8x' % ( mmap[0],) )


        Notes:

            * addr is a *suggestion*, the allocator may rebase
            * addr may be re-based to return a page aligned addr
            * size may be modified to return a page aligned size

            Pass the following optional info for special initialization:

            * init=<bytes>  ( bytes to initialize the memory map )
            * mbuf=<mbuf>   ( a pre-cooked bytearray or buffer interface )

        '''
        if addr != None:
            addr &= self._mem_pagemask

        off = size % self._mem_pagesize
        if off != 0:
            size += ( self._mem_pagesize - off )

        mmap = self._mem_alloc(size, perm=perm, addr=addr, **info)

        self._init_mmap(mmap)
        return mmap

    def peek(self, addr, size):
        '''
        Read memory bytes at addr for size bytes.

        Example:

            byts = m.peek(0x41414141, 20)

        '''
        byts = self._mem_peek(addr,size)
        self.fire('mem:peek', mem=self, addr=addr, size=size, byts=byts)
        return byts

    def pages(self, addr, size):
        '''
        Yield each of the page base addresses for a given address range.

        Example:

            for addr in mem.pages(0x41414141, 128):
                pagething(addr)

        '''
        maxaddr = addr + size
        pageaddr = addr & self._mem_pagemask

        while pageaddr < maxaddr:
            yield pageaddr
            pageaddr += self._mem_pagesize

    def poke(self, addr, byts):
        '''
        Write bytes to memory at addr.

        Example:

            m.poke(0x41414141, b'VISI')

        '''
        size = len(byts)
        self._mem_dirtify(addr,size)

        curval = self.peek(addr,size)
        self.fire('mem:poke', mem=self, addr=addr, byts=byts, curval=curval)
        return self._mem_poke(addr,byts)

    def flush(self):
        '''
        For each currenly "dirty" page yield (addr,bytes) tuple and clear.

        Example:

            for addr,byts in mem.flush():
                stuff(addr,byts)

            # no more dirty pages!

        '''
        pages = self._mem_dirty.keys()
        for addr in pages:
            byts = self.peek(addr, self.pagesize)
            yield addr,byts
            self._mem_dirty.pop(addr)

    def probe(self, addr, size, perm):
        '''
        Probe a memory range to check permissions.

        Example:

            if m.probe(0x41414141, 20, MM_WRITE):
                m.poke( 0x41414141, b'V' * 20 )

        '''
        #self.fire('mem:probe', addr=addr, size=size, perm=perm)
        return self._mem_probe(addr,size,perm)

    def protect(self, addr, size, perm=MM_RWX):
        '''
        Change the memory permissions for the given range.

        Example:

            m.protect(0x41410000,4096,MM_RWX)

        '''
        self.fire('mem:protect', mem=self, addr=addr, size=size, perm=perm)
        return self._mem_protect(addr,size,perm)

    def mmaps(self):
        '''
        Retrieve a list of mmap tufos (addr,info).

        Example:

            for mmap in m.mmaps():
                addr = mmap[0]
                size = mmap[1].get('size')

                print('mem map: 0x%.8x (%d)' % (addr, size))

        Notes:

            ( mmap info convention )
            * perm = MM_XXX permissions const
            * path = <path> ( for file backed memory maps or None )
            * name = <name> ( for named memory maps and humon display )
            * init = <bytes> ( initial memory map state if given to ctor )

        '''
        return self._mem_mmaps()

    def mmap(self, addr):
        '''
        Return the memory map tuple which contains addr or None.

        Example:

            mmap = m.mmap(addr)
            if mmap != None:
                addr = mmap[0]
                print('map at: 0x%.8x' % (addr,))

        '''
        return self._mem_mmap(addr)

    def mbuf(self, addr):
        '''
        Retrieve an (off,bytes) tuple for the given memory address.

        Example:

            off,mbuf = m.mbuf(addr)

        Notes:

            * this is an optimization routine for consuming memory

        '''
        mmap = self.mmap(addr)
        if mmap == None:
            return None

        mbuf = mmap[1].get('mbuf')
        return addr - mmap[0], mbuf

    def snapshot(self):
        '''
        Return an opaque "snapshot" object to be restored with restore()

        Example:

            snap = mem.snapshot()

            mem.poke(0x41410000, b'VISI')

            mem.restore(snap)

            # poke has been reverted

        Notes:

            * snpashot does not support save/restore across uses of alloc()/free()
            * snapshot *does* save/restore 

        '''
        # what we really do is wrap each mbuf with a copy on write
        snap = { 'mmaps':{} }
        for mmap in self.mmaps():

            addr = mmap[0]
            mbuf = mmap[1].get('mbuf')

            snap['mmaps'][addr] = {'mbuf':mbuf}

            mmap[1]['mbuf'] = CopyOnWrite(mbuf)

        snap['dirty'] = dict( self._mem_dirty )

        self.fire('mem:snapshot', mem=self, snap=snap)
        return snap

    def restore(self, snap):
        '''
        Restore a previous memory state captured with snapshot()

        Example:

            see snapshot()

        '''
        for addr,info in snap['mmaps'].items():
            mmap = self.mmap(addr)
            mmap[1].update( info )

        self._mem_dirty = snap.get('dirty')
        self.fire('mem:restore', mem=self, snap=snap)

    def _mem_poke(self, addr, byts):
        mmap = self.mmap(addr)
        if mmap == None:
            return None

        mbuf = mmap[1].get('mbuf')

        off = addr - mmap[0]
        mbuf[off:] = byts
        return len(byts)

    def _mem_peek(self, addr, size):
        mmap = self.mmap(addr)
        if mmap == None:
            return None

        mbuf = mmap[1].get('mbuf')

        off = addr - mmap[0]
        return mbuf[off:off+size]

    def _mem_dirtify(self, addr, size):
        for page in self.pages(addr,size):
            self._mem_dirty[page] = True

    def _mem_mmaps(self):
        return self._mem_maps.values()

    def _mem_probe(self, addr, size, perm):

        addrmax = addr + size
        while addr < addrmax:
            # a default mmap based impl
            mmap = self.mmap(addr)
            if mmap == None:
                return False

            if perm & mmap[1].get('perm') != perm:
                return False

            addr = mmap[0] + mmap[1].get('size')

        return True

    def _mem_mmap(self, addr):
        return self._mem_pagelook.get(addr)

    def _mem_alloc(self, size, perm=MM_RWX, addr=None, **info):

        if addr == None:
            addr = 0

        # FIXME addr + size check
        while self.mmap(addr) != None:
            addr += 4096 # FIXME pagesize

        return tufo(addr, perm=perm, size=size, **info)

    def _mem_free(self, addr):
        mmap = self.mmap(addr)
        if mmap == None:
            raise MemInvalidAddr(addr)

        if mmap[0] != addr:
            raise MemInvalidAddr(addr)

        self._fini_mmap(mmap)
        return mmap


    def _init_mmap(self, mmap):
        addr = mmap[0]

        size = mmap[1].get('size')
        init = mmap[1].get('init')
        mbuf = mmap[1].get('mbuf')

        mmap[1].setdefault('perm', MM_RWX)

        # a few initialization precedents...
        if mbuf == None and init != None:
            mbuf = bytearray(init)
            mmap[1]['mbuf'] = mbuf

        if size == None and mbuf != None:
            size = len(mbuf)
            mmap[1]['size'] = size

        if size == None:
            raise Exception('mmap *must* have size or init or mbuf!')

        if mbuf == None:
            mbuf = bytearray(b'\x00' * size)
            mmap[1]['mbuf'] = mbuf

        self._mem_maps[ addr ] = mmap

        # let a subclass disable this behavior by initializing
        # to None...
        if self._mem_pagelook != None:
            self._mem_pagelook.put( addr, size, mmap )

        self.fire('mem:map:init', mem=self, mmap=mmap)

    def _fini_mmap(self, mmap):
        addr = mmap[0]
        size = mmap[1].get('size')

        self._mem_maps.pop( addr, None)
        self._mem_pagelook.pop(addr,size)

        self.fire('mem:map:fini', mem=self, mmap=mmap)
