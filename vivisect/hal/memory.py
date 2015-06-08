'''
Vivisect machine abstraction for memory interfaces.
'''
import synapse.event.dist as s_evtdist

import vivisect.lib.bits as v_bits
import vivisect.lib.pagelook as v_pagelook

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

    def _cache_read(self, addr, size):
        ret = b''
        for base,off,size in self._iter_bases(addr,addr + size):
            page = self._get_page(base)
            ret += page[off:off+size]

        return ret

    def _cache_write(self, addr, byts):
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

    Notes:

        * used by the memory snapshot interface

    '''
    def __init__(self, buf, pagesize=4096):
        self.realbuf = buf
        PageCache.__init__(self)

    def __len__(self):
        return len(self.realbuf)

    def _load_page(self, addr):
        return self.realbuf[addr:addr + self.pagesize]

class Memory(s_evtdist.EventDist):

    '''
    The top level vivisect Memory abstraction API.

    Notes:

        * mostly used as a mixin to Cpu and others

    '''

    def __init__(self, pagesize=4096, **info):
        s_evtdist.EventDist.__init__(self)

        info.setdefault('allocbase',0x22220000)

        self._mem_maps = {}
        self._mem_info = info
        self._mem_bytes = {}

        self._mem_pagelook = v_pagelook.PageLook(pagesize=pagesize)

        self._mem_dirty = {}
        self._mem_pagesize = pagesize
        self._mem_offmask = (pagesize - 1)
        self._mem_pagemask = ~ (pagesize - 1)

    def getMemInfo(self, name, default=None):
        '''
        Retrieve a value from the memory info dict.

        Example:

            foo = mem.getMemInfo('foo')

        Notes:

            allocbase=<int>     - The base addr for allocMemory to begin at

        '''
        return self._mem_info.get(name,default)

    def setMemInfo(self, name, valu):
        '''
        Set a value in the memory info dict.

        Example:

            mem.setMemInfo('foo',20)

        '''
        self._mem_info[name] = valu

    def freeMemory(self, addr):
        '''
        Free/Release the memory map with the given base addr.

        Example:

            mem.freeMemory( addr )

        '''
        return self._freeMemory(addr)

    def allocMemory(self, size, perm=MM_RWX, addr=None, **info):
        '''
        Allocate a new memory map within the Memory object and return the map.

        Example:

            wantaddr = 0x41414141

            mmap = mem.allocMemory(4096, addr=wantaddr)

            print('alloc at: 0x%.8x' % ( mmap[0],) )


        Notes:

            * addr is a *suggestion*, the allocator may rebase
            * addr may be re-based to return a page aligned addr
            * size may be modified to return a page aligned size
        '''
        if addr == None:
            addr = self._mem_info.get('allocbase')

        addr &= self._mem_pagemask

        # FIXME addr + size check
        while self.getMemoryMap(addr) != None:
            addr += self._mem_pagesize

        off = size % self._mem_pagesize
        if off != 0:
            size += ( self._mem_pagesize - off )

        return self._allocMemory(size, perm=perm, addr=addr, **info)

    def readMemory(self, addr, size):
        '''
        Read memory bytes at addr for size bytes.

        Example:

            byts = m.readMemory(0x41414141, 20)

        '''
        byts = self._readMemory(addr,size)
        self.fire('mem:read', addr=addr, size=size, byts=byts)
        return byts

    def getMemPages(self, addr, size):
        '''
        Yield each of the page base addresses for a given address range.

        Example:

            for addr in mem.getMemPages(0x41414141, 128):
                pagething(addr)

        '''
        maxaddr = addr + size
        pageaddr = addr & self._mem_pagemask

        while pageaddr < maxaddr:
            yield pageaddr
            pageaddr += self._mem_pagesize

    def writeMemory(self, addr, byts):
        '''
        Write bytes to memory at addr.

        Example:

            m.writeMemory(0x41414141, b'VISI')

        '''
        size = len(byts)
        self._mem_dirtify(addr,size)
        self.fire('mem:write', addr=addr, byts=byts)
        return self._writeMemory(addr,byts)

    def getDirtyPages(self, flush=False):
        '''
        For each currenly "dirty" page yield (addr,bytes) tuple and clear.

        Example:

            for addr,byts in mem.getDirtyPages():
                stuff(addr,byts)

            # no more dirty pages!

        '''
        pages = self._mem_dirty.keys()
        for addr in pages:
            byts = self.readMemory(addr, self._mem_pagesize)
            yield addr,byts
            if flush:
                self._mem_dirty.pop(addr)

    def probeMemory(self, addr, perm, size=1):
        '''
        Probe a memory range to check permissions.

        Example:

            if m.probeMemory(0x41414141, MM_WRITE, size=20):
                m.writeMemory( 0x41414141, b'V' * 20 )

        '''
        return self._probeMemory(addr,perm,size=size)

    def protectMemory(self, addr, size, perm=MM_RWX):
        '''
        Change the memory permissions for the given range.

        Example:

            m.protectMemory(0x41410000,4096,MM_RWX)

        '''
        self.fire('mem:protect', mem=self, addr=addr, size=size, perm=perm)
        return self._mem_protect(addr,size,perm)

    def getMemoryMaps(self):
        '''
        Retrieve a list of mmap tuples (addr,size,perm,info).

        Example:

            for addr,size,perm,info in m.getMemoryMaps():
                print('mem map: 0x%.8x (%d)' % (addr, size))

        Notes:

            ( mmap info convention )
            * path = <path> ( for file backed memory maps or None )
            * name = <name> ( for named memory maps and humon display )
            * init = <bytes> ( initial memory map state if given to ctor )

        '''
        return self._getMemoryMaps()

    def getMemoryMap(self, addr):
        '''
        Return the memory map tuple which contains addr or None.

        Example:

            mmap = m.getMemoryMap(addr)
            if mmap != None:
                addr = mmap[0]
                print('map at: 0x%.8x' % (addr,))

        '''
        return self._getMemoryMap(addr)

    def getMemBuf(self, addr):
        '''
        Retrieve an (off,bytes) tuple for the given memory address.

        Example:

            off,mbuf = m.getMemBuf(addr)

        Notes:

            * this is an optimization routine for consuming memory

        '''
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            return None

        mbuf = mmap[3].get('mbuf')
        return addr - mmap[0], mbuf

    def getMemorySnap(self):
        '''
        Return an opaque "snapshot" object to be restored with setMemorySnap()

        Example:

            snap = mem.getMemorySnap()

            mem.writeMemory(0x41410000, b'VISI')

            mem.setMemorySnap(snap)

            # writeMemory has been reverted

        Notes:

            * snpashot does not support save/restore across uses of allocMemory()/freeMemory()
            * snapshot *does* save/restore 

        '''
        # what we really do is wrap each mbuf with a copy on write
        snap = { 'mmaps':{} }
        for addr,size,perm,info in self.getMemoryMaps():

            mbuf = info.get('mbuf')
            snap['mmaps'][addr] = {'mbuf':mbuf}

            info['mbuf'] = CopyOnWrite(mbuf)

        snap['dirty'] = dict( self._mem_dirty )
        return snap

    def setMemorySnap(self, snap):
        '''
        Restore a previous memory state captured with getMemorySnap()

        Example:

            see getMemorySnap()

        '''
        [ self.getMemoryMap(addr)[3].update(info) for (addr,info) in snap['mmaps'].items() ]
        self._mem_dirty = snap.get('dirty')

    def initMemoryMap(self, addr, size, perm=MM_RWX, **info):
        '''
        Add a memory map at the specified addr.
        Optional arguments must include either size, init, or mbuf.

        Additional options:
        * init  - raw bytes to initialize the memory
        * mbuf  - memory buffer / bytearray to use directly

        Example:

            mmap = mem.initMemoryMap(0x41410000, 4096, perm=MM_RWX)

        '''
        mmap = (addr,size,perm,info)
        return self.addMemoryMap(mmap)

    def addMemoryMap(self, mmap):
        '''
        Add a memory map tuple (addr, size, perm, info).

        Notes:
            * casual users probably want initMemoryMap()

        Example:

            mmap = (0x41414141, 4096, MM_RWX, {})
            mem.addMemoryMap(mmap)

        '''
        addr,size,perm,info = mmap

        # check size for page alignment and update as needed
        rem = size % self._mem_pagesize
        if rem:
            size += ( self._mem_pagesize - rem )

        # ensure that init ( if present ) is padded to length
        init = info.get('init')
        if init != None and len(init) < size:
            info['init'] = init.ljust(size,b'\x00')

        return self._addMemoryMap( (addr,size,perm,info) )

    def delMemoryMap(self, mmap):
        '''
        Delete a memory map tuple (addr, size, perm, info).

        Example:

            mem.delMemoryMap(mmap)

        '''
        return self._delMemoryMap(mmap)

    # APIs from here down implement the "guts" and can be over-ridden

    def _writeMemory(self, addr, byts):
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            return None

        mbuf = mmap[3].get('mbuf')

        off = addr - mmap[0]
        mbuf[off:] = byts
        return len(byts)

    def _readMemory(self, addr, size):
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            return None

        mbuf = mmap[3].get('mbuf')

        off = addr - mmap[0]
        return mbuf[off:off+size]

    def _mem_dirtify(self, addr, size):
        for page in self.getMemPages(addr,size):
            self._mem_dirty[page] = True

    def _getMemoryMaps(self):
        return self._mem_maps.values()

    def _probeMemory(self, addr, perm, size=1):

        addrmax = addr + size
        while addr < addrmax:
            # a default mmap based impl
            mmap = self.getMemoryMap(addr)
            if mmap == None:
                return False

            if perm & mmap[2] != perm:
                return False

            addr = mmap[0] + mmap[1]

        return True

    def _getMemoryMap(self, addr):
        return self._mem_pagelook.get(addr)

    def _allocMemory(self, size, perm=MM_RWX, addr=None, **info):
        mmap = (addr,size,perm,info)
        return self.addMemoryMap(mmap)

    def _freeMemory(self, addr):
        mmap = self.getMemoryMap(addr)
        if mmap == None:
            raise MemInvalidAddr(addr)

        if mmap[0] != addr:
            raise MemInvalidAddr(addr)

        self.delMemoryMap(mmap)
        return mmap

    def _addMemoryMap(self, mmap):
        addr,size,perm,info = mmap

        mbuf = info.get('mbuf')

        # a few initialization precedents...
        if mbuf == None:
            init = info.get('init')
            if init == None:
                init = b'\x00' * size

            mbuf = bytearray(init)
            info['mbuf'] = mbuf

        self._mem_maps[ addr ] = mmap
        self._mem_pagelook.put( addr, size, mmap )

        self.fire('mem:mmap:add', mmap=mmap)
        return mmap

    def _delMemoryMap(self, mmap):
        addr,size,perm,info = mmap
        self._mem_maps.pop( addr, None)
        self._mem_pagelook.pop(addr,size)
        self.fire('mem:mmap:del', mmap=mmap)
