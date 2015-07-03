'''
Vivisect machine abstraction for memory interfaces.
'''
import re

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

pnames = ['No Access', 'Execute', 'Write', None, 'Read']
def getPermName(perm):
    '''
    Return the human readable name for a *single* memory
    perm enumeration value.
    '''
    return pnames[perm]

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
    """
    This is the interface spec (and a few helper utils)
    for the unified memory object interface.

    NOTE: If your actual underlying memory format is such
    that over-riding anything (like isValidPointer!) can
    be faster than the default implementation, DO IT!
    """
    def readMemory(self, addr, size):
        """
        Read memory from the specified virtual address for size bytes
        and return it as a python string.

        Example: mem.readMemory(0x41414141, 20) -> "A..."
        """
        raise ImplementMe

    def writeMemory(self, addr, bytez):
        """
        Write the given bytes to the specified virtual address.

        Example: mem.writeMemory(0x41414141, "VISI")
        """
        raise ImplementMe

    def protectMemory(self, addr, size, perms):
        """
        Change the protections for the given memory map. On most platforms
        the addr/size *must* exactly match an existing memory map.
        """
        raise ImplementMe

    def probeMemory(self, addr, size, perm):
        """
        Check to be sure that the given virtual address and size
        is contained within one memory map, and check that the
        perms are contained within the permission bits
        for the memory map. (MM_READ | MM_WRITE | MM_EXEC | ...)

        Example probeMemory(0x41414141, 20, MM_WRITE)
        (check if the memory for 20 bytes at 0x41414141 is writable)
        """
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

    def allocateMemory(self, size, perms=MM_RWX, suggestaddr=0):
        return self._mem_alloc(size, perms=perms, suggestaddr=suggestaddr)

    def addMemoryMap(self, mapaddr, perms, fname, bytez):
        return self._mem_addmap(mapaddr,perms,fname,bytez)

    def getMemoryMaps(self):
        return self._mem_getmaps()

    def getMemoryMap(self, addr):
        '''
        Return a tuple of mapaddr,size,perms,filename for the memory
        map which contains the specified address (or None).
        '''
        return self._mem_getmap(addr)

    def _mem_getmap(self, addr):
        for mapaddr,size,perms,mname in self.getMemoryMaps():
            if addr >= mapaddr and addr < (mapaddr+size):
                return (mapaddr,size,perms,mname)
        return None

    def searchMemory(self, needle, regex=False):
        """
        A quick cheater way to searchMemoryRange() for each
        of the current memory maps.
        """
        results = []
        for addr,size,perm,fname in self.getMemoryMaps():
            try:
                results.extend(self.searchMemoryRange(needle, addr, size, regex=regex))
            except:
                pass # Some platforms dont let debuggers read non-readable mem

        return results

    def searchMemoryRange(self, needle, address, size, regex=False):
        """
        Search the specified memory range (address -> size)
        for the string needle.   Return a list of addresses
        where the match occurs.
        """
        results = []
        memory = self.readMemory(address, size)
        if regex:
            for match in re.finditer(needle, memory):
                off = match.start()
                results.append(address+off)
        else:
            offset = 0
            while offset < size:
                loc = memory.find(needle, offset)
                if loc == -1: # No more to be found ;)
                    break
                results.append(address+loc)
                offset = loc+len(needle) # Skip one past our matcher

        return results

class MemoryCache(IMemory):
    '''
    Create a "copy on write" memory cache for another memory object.
    '''
    def __init__(self, mem, pagesize=4096):
        self.pagesize = pagesize # must be binary multiplicative
        self.pagemask = ~ (self.pagesize - 1)
        self._cacheSet(mem)

    def _cacheSet(self, mem):
        self.mem = mem
        self._cacheClear()

    def _cacheClear(self):
        self.pagecache = {}
        self.pagedirty = {}

    def _cachePage(self, addr):
        return self.mem.readMemory(addr, self.pagesize)

    def getMemoryMap(self, addr):
        return self.mem.getMemoryMap(addr)

    def getMemoryMaps(self, addr):
        return self.mem.getMemoryMaps(addr)

    def readMemory(self, addr, size):
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

    def writeMemory(self, addr, bytez):

        while len(bytez):
            pageaddr = addr & self.pagemask
            pageoff = addr - pageaddr
            chunksize = min(self.pagesize, len(bytez))

            page = self.pagecache.get(pageaddr)
            if page == None:
                page = self.mem.readMemory(pageaddr, self.pagesize)
                self.pagecache[pageaddr] = page

            self.pagedirty[pageaddr] = True
            page = page[:pageoff] + bytez[:chunksize] + page[pageoff+chunksize:]
            self.pagecache[pageaddr] = page

            addr += chunksize
            bytez = bytez[chunksize:]

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

class Memory(IMemory):

    def __init__(self):
        IMemory.__init__(self)
        self._map_defs = []

    def addMemoryMap(self, addr, perms, fname, bytez):
        '''
        Add a memory map to this object...
        '''
        msize = len(bytez)
        mmap = (addr, msize, perms, fname)
        hlpr = [addr, addr+msize, mmap, bytez]
        self._map_defs.append(hlpr)
        return

    def getMemoryMap(self, addr):
        """
        Get the addr,size,perms,fname tuple for this memory map
        """
        for maddr, mmaxaddr, mmap, mbytes in self._map_defs:
            if addr >= maddr and addr < mmaxaddr:
                return mmap
        return None

    def getMemoryMaps(self):
        '''
        Return a list if (mapaddr,mapsize,mapperms,mapfile) tuples.
        '''
        return [ mmap for maddr, mmaxaddr, mmap, mbytes in self._map_defs ]

    def readMemory(self, addr, size):
        '''
        Read memory bytes by address.
        '''
        for maddr, mmaxaddr, mmap, mbytes in self._map_defs:
            if addr >= maddr and addr < mmaxaddr:
                maddr, msize, mperms, mfname = mmap
                if not mperms & MM_READ:
                    raise MemPermsError()
                offset = addr - maddr
                return mbytes[offset:offset+size]
        raise MemInvalidAddr()

    def writeMemory(self, addr, bytez):
        '''
        Write memory bytes by address.
        '''
        for mapdef in self._map_defs:
            maddr, mmaxaddr, mmap, mbytes = mapdef
            if addr >= maddr and addr < mmaxaddr:
                maddr, msize, mperms, mfname = mmap
                if not mperms & MM_WRITE:
                    raise MemPermsError()
                offset = addr - maddr
                mapdef[3] = mbytes[:offset] + bytez + mbytes[offset+len(bytez):]
                return

        raise MemInvalidAddr()

    def getBytesDef(self, addr):
        '''
        Retrieve an (offset,bytez) tuple for the given address.
        '''
        for mapdef in self._map_defs:
            maddr, mmaxaddr, mmap, mbytes = mapdef
            if addr >= maddr and addr < mmaxaddr:
                offset = addr - maddr
                return (offset, mbytes)
        raise MemInvalidAddr()

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
