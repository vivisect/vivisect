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

MM_READ_WRITE = MM_READ | MM_WRITE
MM_READ_EXEC  =  MM_READ | MM_EXEC
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
  ('rwx',MM_RWX),('r--',MM_READ),('-w-',MM_WRITE),('--x',MM_EXEC),
  ('rw-',MM_READ_WRITE),('r-x',MM_READ_EXEC),('-wx',MM_WRITE | MM_EXEC),
  ('--x',MM_EXEC),('---',MM_NONE),
]

repr2perm = { a.replace('-',''):b for (a,b) in permstrs }
perm2repr = { b:a for (a,b) in permstrs }

def reprPerms(mask):
    return perm2repr.get(mask,'???')

def parsePerms(pstr):
    return repr2perm.get(pstr,0)

class ImplementMe(Exception):pass

class SparseBuf:

    '''
    Looks/smells/acts like a bytearray but is populated on-demand
    '''

    def __init__(self, onpage, pagesize=4096):
        self.pages = {}
        self.onpage = onpage

        self.pagesize = pagesize

        self.offmask = (pagesize - 1)
        self.pagemask = ~ self.offmask

    def _get_page(self, off):
        page = self.pages.get( off )
        if page == None:
            page = bytearray( self.onpage( off, self.pagesize ) )
            self.pages[off] = page
        return page

    def __getitem__(self, item):

        if isinstance(item,slice):

            off = item.start
            offmax = item.stop

            ret = b''
            while off < offmax:
                chunkoff = off & self.offmask
                chunkbase = off & self.pagemask
                chunksize = min( self.pagesize - chunkoff, offmax - off)

                page = self._get_page(chunkbase)

                ret += page[chunkoff:chunkoff + chunksize]
                off += chunksize

            return ret

        off = item & self.offmask
        base = item & self.pagemask
        return self._get_page(base)[off]

    def __setitem__(self, item, valu):

        if isinstance(item,slice):

            off = item.start

            stop = item.stop
            if stop == None:
                stop = off + len(valu)

            size = item.start - stop

            valoff = 0
            while off < stop:
                chunkoff = off & self.offmask
                chunkbase = off & self.pagemask
                chunksize = min( self.pagesize - chunkoff, size - valoff )

                page = self._get_page(chunkbase)
                page[chunkoff:chunkoff+chunksize] = valu[valoff:valoff+chunksize]

                off += chunksize
                valoff += chunksize

            return

        off = item & self.offmask
        base = item & self.pagemask
        self._get_page( base )[ off ] = valu

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
        mmap = self.mmap(addr)
        if mmap == None:
            raise MemInvalidAddr(addr)

        if mmap[0] != addr:
            raise MemInvalidAddr(addr)

        self._fini_mmap(mmap)
        return mmap

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

    def poke(self, addr, byts, force=False):
        '''
        Write bytes to memory at addr.

        Example:

            m.poke(0x41414141, b"VISI", force=True)

        Notes:

            * specify force=True to ignore mmap perms

        '''
        size = len(byts)
        #if not force and not self.probe(addr,size,MM_WWRITE):
            #raise MemPermsError()

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
        # a default mmap based impl
        mmap = self.mmap(addr)
        if mmap == None:
            return False

        mapsize = mmap[1].get('size')
        if addr + size > addr + mapsize:
            return False

        if perm & mmap[1].get('perm') != perm:
            return False

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
        self._mem_pagelook.put( addr, size, mmap )

        self.fire('mem:map:init', mem=self, mmap=mmap)

    def _fini_mmap(self, mmap):
        addr = mmap[0]
        size = mmap[1].get('size')

        self._mem_maps.pop( addr, None)
        self._mem_pagelook.pop(addr,size)

        self.fire('mem:map:fini', mem=self, mmap=mmap)

class MemoryCache(Memory):
    '''
    Create a "copy on write" memory cache for another memory object.
    '''
    def __init__(self, mem, pagesize=4096):
        Memory.__init__(self)
        self.mem = mem
        self.pagesize = pagesize # must be binary multiplicative
        self.pagemask = ~ (self.pagesize - 1)
        self.pagecache = {}
        self.pagedirty = {}

        self.mapcache = None

    def _cachePage(self, addr):
        return self.mem.peek(addr, self.pagesize)

    def _mem_mmaps(self):
        if self.mapcache == None:
            self.mapcache = self.mem.getMemoryMaps()
        return self.mapcache

    def _mem_mmap(self, addr):
        return self.mem.getMemoryMap(addr)

    def _mem_peek(self, addr, size):
        ret = b''
        while size:
            pageaddr = addr & self.pagemask
            pageoff = addr - pageaddr
            chunksize = min( self.pagesize - pageoff, size )
            page = self.pagecache.get( pageaddr )
            # FIXME optimize to read an ideal sized chunk
            if page == None:
                page = self.mem.peek(pageaddr, self.pagesize)
                self.pagecache[pageaddr] = page
            ret += page[ pageoff : pageoff + chunksize ]

            addr += chunksize
            size -= chunksize

        return ret

    def _mem_poke(self, addr, mem):

        while len(mem):
            pageaddr = addr & self.pagemask
            pageoff = addr - pageaddr
            chunksize = min(self.pagesize, len(mem))

            page = self.pagecache.get(pageaddr)
            if page == None:
                page = self.mem.peek(pageaddr, self.pagesize)
                self.pagecache[pageaddr] = page

            self.pagedirty[pageaddr] = True
            page = page[:pageoff] + mem[:chunksize] + page[pageoff+chunksize:]
            self.pagecache[pageaddr] = page

            addr += chunksize
            mem = mem[chunksize:]

    def clearCache(self):
        self.mapcache = None
        self.pagecache.clear()
        self.pagedirty.clear()

    def getCacheSizes(self):
        ret = {
            'pagesize':self.pagesize,
            'pages':len(self.pagecache),
            'dirty':len(self.pagedirty),
        }

        maps = 0
        if self.mapcache != None:
            maps = len(self.mapcache)

        ret['maps'] = maps
        return ret

    def clearDirtyPages(self):
        '''
        Clear the "dirty cache" allowing tracking of writes *since* this call.
        '''
        self.pagedirty.clear()

    def isDirtyPage(self, addr):
        '''
        Return True if the given page is currently "dirty" according to the cache.
        '''
        return self.pagedirty.get( addr & self.pagemask, False )

    def getDirtyPages(self):
        '''
        Returns a list of dirty pages as (pageaddr, pagebytez) tuples.
        '''
        return [ (addr, self.pagecache.get(addr)) for addr in self.pagedirty.keys() ]

    def syncDirtyPages(self):
        '''
        Push the cached "dirty" pages into the backing memory object.
        '''
        for addr,page in self.getDirtyPages():
            self.mem.poke(addr,page)

#class Memory(Memory):

    #def __init__(self):
        #IMemory.__init__(self)
        #self._mem_maps = []
        #self._mem_bytes = {}
        #self._mem_pagelook = v_pagelook.PageLook()

    #def addMemoryMap(self, addr, perms, info, mem):
        #'''
        #Add a memory map to the Memory object.
        #'''
        #self._mem_bytes[addr] = bytearray(mem)
#
        #mmap = (addr,len(mem),perms,info)
#
        #self._mem_maps.append( mmap )
        #self._mem_pagelook.put( addr, len(mem), mmap )
#
        #return mmap

    #def _mem_mmaps(self):
        #return self._mem_maps

    #def _mem_mmap(self, addr):
        #return self._mem_pagelook.get(addr)

    #def _mem_peek(self, addr, size):
        #mmap = self._mem_pagelook.get(addr)
        #if mmap == None:
            #raise MemInvalidAddr()

        #maddr,msize,mperms,minfo = mmap
        #if not mperms & MM_READ:
            #raise MemPermsError()
#
        #off = addr - maddr
        #mem = self._mem_bytes.get(maddr)
        #return mem[off:off+size]

    #def _mem_poke(self, addr, mem):
        #mmap = self._mem_pagelook.get(addr)
        #if mmap == None:
            #raise MemInvalidAddr()

        #maddr,msize,mperms,minfo = mmap
        #if not mperms & MM_WRITE:
            #raise MemPermsError()
#
        #off = addr - maddr

        #mapmem = self._mem_bytes.get(maddr)
        #mapmem[off:] = mem

    #def getBytesDef(self, addr):
        #'''
        #Retrieve an (offset,bytez) tuple for the given address.
        #'''
        #mmap = self._mem_pagelook.get(addr)
        #if mmap == None:
            #raise MemInvalidAddr()

        #off = addr - mmap[0]
        #mem = self._mem_bytes.get(mmap[0])
        #return (off,mem)

class MemoryFile:
    '''
    A file like object to wrap around a memory object.
    '''
    def __init__(self, memobj, baseaddr):
        self.baseaddr = baseaddr
        self.offset = baseaddr
        self.memobj = memobj

    def seek(self, offset):
        self.offset = self.baseaddr + offset

    def read(self, size):
        ret = self.memobj.peek(self.offset, size)
        self.offset += size
        return ret

    def write(self, bytez):
        self.memobj.poke(self.offset, bytez)
        self.offset += len(bytez)
