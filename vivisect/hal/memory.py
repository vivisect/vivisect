'''
Vivisect machine abstraction for memory interfaces.
'''

import vivisect.lib.pagelook as v_pagelook

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

disp2bits = { a.replace('-',''):b for (a,b) in permstrs }
bits2disp = { b:a for (a,b) in permstrs }

def reprPerms(mask):
    return bits2disp.get(mask,'???')

def parsePerms(pstr):
    return disp2bits.get(pstr,0)

class ImplementMe(Exception):pass

class IMemory:

    def readMemory(self, addr, size):
        '''
        Read memory bytes at addr for size bytes.

        Example:

            m.readMemory(0x41414141, 20) -> "A..."

        '''
        return self._mem_read(addr,size)

    def writeMemory(self, addr, mem):
        '''
        Write bytes to memory at addr.

        Example:

            m.writeMemory(0x41414141, b"VISI")

        '''
        return self._mem_write(addr, mem)

    def protectMemory(self, addr, size, perms):
        '''
        Change the memory permissions for the given range.

        Example:

            m.protectMemory(0x41410000,4096,MM_RWX)

        '''
        return self._mem_protect(addr,size,perms)

    def probeMemory(self, addr, size, perm):
        '''
        Probe a memory range to check permissions.

        Example:

            m.probeMemory(0x41414141, 20, MM_WRITE)

        '''
        return self._mem_probe(addr,size,perm)

    def allocMemory(self, size, perms=MM_RWX, suggestaddr=0):
        '''
        Allocate and protect a segment of memory.

        Returns the address of the newly allocated memory range
        or None if the Memory instance doesn't support alloc.

        Example:

            ptr = m.allocMemory( 4096, perms=MM_RWX )
            if ptr != None:
                m.writeMemory(ptr, b'VISI')

        '''
        return self._mem_alloc(size, perms=perms, suggestaddr=suggestaddr)

    def getMemoryMaps(self):
        '''
        Retrieve a list of (addr,size,perm,info) tuples.

        Example:

            for addr,size,perm,info in m.getMemoryMaps():

        '''
        return self._mem_getmaps()

    def getMemoryMap(self, addr):
        '''
        Return the memory map tuple which contains addr or None.

        Example:

            map = m.getMemoryMap(addr)
            if map != None:
                addr,size,perm,info = map
                print('map at: 0x%.8x' % (addr,))

        '''
        return self._mem_getmap(addr)

    def _mem_getmaps(self):
        return ()

    def _mem_probe(self, addr, size, perm):
        # a default memmap based impl
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            return False
        mapaddr, mapsize, mapperm, mapfile = mmap
        mapend = mapaddr+mapsize
        if addr+size >= mapend:
            return False
        if mapperm & perm != perm:
            return False
        return True


    def _mem_getmap(self, addr):
        # default memmap based impl
        for mapaddr,size,perms,mname in self.getMemoryMaps():
            if addr >= mapaddr and addr < (mapaddr+size):
                return (mapaddr,size,perms,mname)
        return None

class MemoryCache(IMemory):
    '''
    Create a "copy on write" memory cache for another memory object.
    '''
    def __init__(self, mem, pagesize=4096):
        self.mem = mem
        self.pagesize = pagesize # must be binary multiplicative
        self.pagemask = ~ (self.pagesize - 1)
        self.pagecache = {}
        self.pagedirty = {}

        self.mapcache = None

    def _cachePage(self, addr):
        return self.mem.readMemory(addr, self.pagesize)

    def _mem_getmaps(self):
        if self.mapcache == None:
            self.mapcache = self.mem.getMemoryMaps()
        return self.mapcache

    def _mem_getmap(self, addr):
        return self.mem.getMemoryMap(addr)

    def _mem_read(self, addr, size):
        ret = b''
        while size:
            pageaddr = addr & self.pagemask
            pageoff = addr - pageaddr
            chunksize = min( self.pagesize - pageoff, size )
            page = self.pagecache.get( pageaddr )
            # FIXME optimize to read an ideal sized chunk
            if page == None:
                page = self.mem.readMemory(pageaddr, self.pagesize)
                self.pagecache[pageaddr] = page
            ret += page[ pageoff : pageoff + chunksize ]

            addr += chunksize
            size -= chunksize

        return ret

    def _mem_write(self, addr, mem):

        while len(mem):
            pageaddr = addr & self.pagemask
            pageoff = addr - pageaddr
            chunksize = min(self.pagesize, len(mem))

            page = self.pagecache.get(pageaddr)
            if page == None:
                page = self.mem.readMemory(pageaddr, self.pagesize)
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
            self.mem.writeMemory(addr,page)

class Memory(IMemory):

    def __init__(self):
        IMemory.__init__(self)
        self._mem_maps = []
        self._mem_bytes = {}
        self._mem_pagelook = v_pagelook.PageLook()

    def addMemoryMap(self, addr, perms, info, mem):
        '''
        Add a memory map to the Mmu.
        '''
        self._mem_bytes[addr] = bytearray(mem)

        mmap = (addr,len(mem),perms,info)

        self._mem_maps.append( mmap )
        self._mem_pagelook.put( addr, len(mem), mmap )

        return mmap

    def _mem_getmaps(self):
        return self._mem_maps

    def _mem_getmap(self, addr):
        return self._mem_pagelook.get(addr)

    def _mem_read(self, addr, size):
        mmap = self._mem_pagelook.get(addr)
        if mmap == None:
            raise MemInvalidAddr()

        maddr,msize,mperms,minfo = mmap
        if not mperms & MM_READ:
            raise MemPermsError()

        off = addr - maddr
        mem = self._mem_bytes.get(maddr)
        return mem[off:off+size]

    def _mem_write(self, addr, mem):
        mmap = self._mem_pagelook.get(addr)
        if mmap == None:
            raise MemInvalidAddr()

        maddr,msize,mperms,minfo = mmap
        if not mperms & MM_WRITE:
            raise MemPermsError()

        off = addr - maddr

        mapmem = self._mem_bytes.get(maddr)
        mapmem[off:] = mem

    def getBytesDef(self, addr):
        '''
        Retrieve an (offset,bytez) tuple for the given address.
        '''
        mmap = self._mem_pagelook.get(addr)
        if mmap == None:
            raise MemInvalidAddr()

        off = addr - mmap[0]
        mem = self._mem_bytes.get(mmap[0])
        return (off,mem)

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
        ret = self.memobj.readMemory(self.offset, size)
        self.offset += size
        return ret

    def write(self, bytez):
        self.memobj.writeMemory(self.offset, bytez)
        self.offset += len(bytez)
