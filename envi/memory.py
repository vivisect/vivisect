import re
import struct

import envi
import envi.exc as e_exc
import envi.bits as e_bits

from envi.const import *
"""
A module containing memory utilities and the definition of the
memory access API used by all vtoys trace/emulators/workspaces.
"""

def getPermName(perm):
    '''
    Return the human readable name for a *single* memory
    perm enumeration value.
    '''
    return pnames[perm]


def reprPerms(mask):
    plist = ['-', '-', '-', '-']
    if mask & MM_SHARED:
        plist[0] = 's'
    if mask & MM_READ:
        plist[1] = 'r'
    if mask & MM_WRITE:
        plist[2] = 'w'
    if mask & MM_EXEC:
        plist[3] = 'x'

    return "".join(plist)


def parsePerms(pstr):
    ret = 0
    if pstr.find('s') != -1:
        ret |= MM_SHARED
    if pstr.find('r') != -1:
        ret |= MM_READ
    if pstr.find('w') != -1:
        ret |= MM_WRITE
    if pstr.find('x') != -1:
        ret |= MM_EXEC
    return ret


class IMemory:
    """
    This is the interface spec (and a few helper utils)
    for the unified memory object interface.

    NOTE: If your actual underlying memory format is such
    that over-riding anything (like isValidPointer!) can
    be faster than the default implementation, DO IT!
    """

    def __init__(self, arch=None):
        self.imem_psize = struct.calcsize('P')
        self.imem_archs = envi.getArchModules()
        if arch is not None:
            self.setMemArchitecture(arch)

    def setMemArchitecture(self, arch):
        '''
        Set the hardware architecture for the current memory object.
        ( this controls things like pointer size, and opcode decoding )

        Example:
            import envi
            mem.setMemArchitecture(envi.ARCH_I386)
        '''
        archmod = self.imem_archs[arch >> 16]
        self.imem_archs[envi.ARCH_DEFAULT] = archmod
        self.imem_psize = archmod.getPointerSize()

    def getMemArchModule(self, arch=envi.ARCH_DEFAULT):
        '''
        Get a reference to the default arch module for the memory object.
        '''
        return self.imem_archs[arch >> 16]

    def getPointerSize(self):
        return self.imem_psize

    def readMemory(self, va, size):
        """
        Read memory from the specified virtual address for size bytes
        and return it as a python string.

        Example: mem.readMemory(0x41414141, 20) -> "A..."
        """
        raise Exception("must implement readMemory!")

    def writeMemory(self, va, bytes):
        """
        Write the given bytes to the specified virtual address.

        Example: mem.writeMemory(0x41414141, "VISI")
        """
        raise Exception("must implement writeMemory!")

    def protectMemory(self, va, size, perms):
        """
        Change the protections for the given memory map. On most platforms
        the va/size *must* exactly match an existing memory map.
        """
        raise Exception("must implement protectMemory!")

    def probeMemory(self, va, size, perm):
        """
        Check to be sure that the given virtual address and size
        is contained within one memory map, and check that the
        perms are contained within the permission bits
        for the memory map. (MM_READ | MM_WRITE | MM_EXEC | ...)

        Example probeMemory(0x41414141, 20, envi.memory.MM_WRITE)
        (check if the memory for 20 bytes at 0x41414141 is writable)
        """
        mmap = self.getMemoryMap(va)
        if mmap is None:
            return False
        mapva, mapsize, mapperm, mapfile = mmap
        mapend = mapva+mapsize
        if va+size > mapend:
            return False
        if mapperm & perm != perm:
            return False
        return True

    def allocateMemory(self, size, perms=MM_RWX, suggestaddr=0):
        raise Exception("must implement allocateMemory!")

    def addMemoryMap(self, mapva, perms, fname, bytes):
        raise Exception("must implement addMemoryMap!")

    def getMemoryMaps(self):
        raise Exception("must implement getMemoryMaps!")

    # Mostly helpers from here down...
    def readMemoryFormat(self, va, fmt):
        # Somehow, pointers are "signed" when they
        # get chopped up by python's struct package
        if self.imem_psize == 2:
            fmt = fmt.replace("P", "H")
        elif self.imem_psize == 4:
            fmt = fmt.replace("P", "I")
        elif self.imem_psize == 8:
            fmt = fmt.replace("P", "Q")

        size = struct.calcsize(fmt)
        bytez = self.readMemory(va, size)
        return struct.unpack(fmt, bytez)

    def getSegmentInfo(self, id):
        return (0, 0xffffffff)

    def readMemValue(self, addr, size):
        '''
        Read a number from memory of the given size.
        '''
        # FIXME: use getBytesDef (and implement a dummy wrapper in VTrace for getBytesDef)
        bytes = self.readMemory(addr, size)
        if bytes is None:
            return None

        # FIXME change this (and all uses of it) to passing in format...
        if len(bytes) != size:
            raise Exception("Read gave wrong length at va: 0x%.8x (wanted %d got %d)" % (addr, size, len(bytes)))

        return e_bits.parsebytes(bytes, 0, size, False, self.getEndian())

    def readMemoryPtr(self, va):
        '''
        Read a pointer from memory at the specified address.

        Example:
            ptr = t.readMemoryPtr(addr)
        '''
        return self.readMemValue(va, self.imem_psize)

    def writeMemoryFormat(self, va, fmt, *args):
        '''
        Write a python format sequence of variables out to memory after
        serializing using struct pack...

        Example:
            trace.writeMemoryFormat(va, '<PBB', 10, 30, 99)
        '''
        if self.imem_psize == 4:
            fmt = fmt.replace("P", "I")
        elif self.imem_psize == 8:
            fmt = fmt.replace("P", "Q")
        mbytes = struct.pack(fmt, *args)
        self.writeMemory(va, mbytes)

    def writeMemValue(self, addr, val, size):
        '''
        Write a number from memory of the given size.
        '''
        bytez = e_bits.buildbytes(val, size, self.getEndian())
        return self.writeMemory(addr, bytez)

    def writeMemoryPtr(self, va, val):
        '''
        Write a pointer to memory at the specified address.

        Example:
            ptr = t.writeMemoryPtr(addr, val)
        '''
        return self.writeMemValue(va, val, self.imem_psize)

    def getMemoryMap(self, va):
        '''
        Return a tuple of mapva,size,perms,filename for the memory
        map which contains the specified address (or None).
        '''
        if va is None:
            return None
        for mapva, size, perms, mname in self.getMemoryMaps():
            if mapva <= va < (mapva + size):
                return (mapva, size, perms, mname)
        return None

    def isValidPointer(self, va):
        return self.getMemoryMap(va) is not None

    def getMaxReadSize(self, va):
        '''
        Return the number of contiguous bytes that can be read from the
        specified va.
        '''
        nread = 0

        mmap = self.getMemoryMap(va)
        while mmap is not None:
            mapva, size, perms, mname = mmap
            if not (perms & MM_READ):
                break

            nread += (mapva + size) - (va + nread)
            mmap = self.getMemoryMap(va + nread)

        return nread

    def isReadable(self, va):
        maptup = self.getMemoryMap(va)
        if maptup is None:
            return False
        return bool(maptup[2] & MM_READ)

    def isWriteable(self, va):
        maptup = self.getMemoryMap(va)
        if maptup is None:
            return False
        return bool(maptup[2] & MM_WRITE)

    def isExecutable(self, va):
        maptup = self.getMemoryMap(va)
        if maptup is None:
            return False
        return bool(maptup[2] & MM_EXEC)

    def isShared(self, va):
        maptup = self.getMemoryMap(va)
        if maptup is None:
            return False
        return bool(maptup[2] & MM_SHARED)

    def searchMemory(self, needle, regex=False):
        """
        A quick cheater way to searchMemoryRange() for each
        of the current memory maps.
        """
        results = []
        for va, size, perm, fname in self.getMemoryMaps():
            try:
                results.extend(self.searchMemoryRange(needle, va, size, regex=regex))
            except:
                pass  # Some platforms dont let debuggers read non-readable mem

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
                if loc == -1:  # No more to be found ;)
                    break
                results.append(address+loc)
                offset = loc + len(needle)  # Skip one past our matcher

        return results

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        '''
        Parse an opcode from the specified virtual address.

        Example: op = m.parseOpcode(0x7c773803)
        '''
        b = self.readMemory(va, 16)
        return self.imem_archs[arch >> 16].archParseOpcode(b, 0, va)


class MemoryCache(IMemory):
    '''
    An object which acts like "copy on write" cache for another memory
    object.
    '''
    def __init__(self, mem, pagesize=4096):
        self.mem = mem
        self.pagesize = pagesize  # must be binary multiplicative
        self.pagemask = ~(self.pagesize - 1)
        self.pagecache = {}
        self.pagedirty = {}

        # Steal a few methods from our parent object
        self.getMemoryMap = mem.getMemoryMap
        self.getMemoryMaps = mem.getMemoryMaps

    def _cachePage(self, va):
        return self.mem.readMemory(va, self.pagesize)

    def readMemory(self, va, size):
        ret = b''
        while size:
            pageva = va & self.pagemask
            pageoff = va - pageva
            chunksize = min(self.pagesize - pageoff, size)
            page = self.pagecache.get(pageva)
            if page is None:
                page = self.mem.readMemory(pageva, self.pagesize)
                self.pagecache[pageva] = page
            ret += page[pageoff:pageoff + chunksize]

            va += chunksize
            size -= chunksize

        return ret

    def writeMemory(self, va, bytez):

        while len(bytez):
            pageva = va & self.pagemask
            pageoff = va - pageva
            chunksize = min(self.pagesize, len(bytez))

            page = self.pagecache.get(pageva)
            if page is None:
                page = self.mem.readMemory(pageva, self.pagesize)
                self.pagecache[pageva] = page

            self.pagedirty[pageva] = True
            page = page[:pageoff] + bytez[:chunksize] + page[pageoff+chunksize:]
            self.pagecache[pageva] = page

            va += chunksize
            bytez = bytez[chunksize:]

    def clearDirtyPages(self):
        '''
        Clear the "dirty cache" allowing tracking of writes *since* this call.
        '''
        self.pagedirty.clear()

    def isDirtyPage(self, va):
        '''
        Return True if the given page is currently "dirty" according to the cache.
        '''
        return self.pagedirty.get(va & self.pagemask, False)

    def getDirtyPages(self):
        '''
        Returns a list of dirty pages as (pageva, pagebytez) tuples.
        '''
        return [(va, self.pagecache.get(va)) for va in self.pagedirty.keys()]

    #def syncDirtyPages(self):
        #'''
        #Write all of the "dirty" pages back to the underlying memory object.
        #'''


class MemoryObject(IMemory):

    def __init__(self, arch=None):
        """
        Take a set of memory maps (va, perms, fname, bytes) and put them in
        a sparse space finder. You may specify your own page-size to optimize
        the search for an architecture.
        """
        IMemory.__init__(self, arch=arch)
        self._map_defs = []
        self._supervisor = False

    def allocateMemory(self, size, perms=MM_RWX, suggestaddr=0x1000, name='', fill=b'\0'):
        '''
        Find a free block of memory (no maps exist) and allocate a new map
        Uses findFreeMemoryBlock()
        '''
        baseva = self.findFreeMemoryBlock(size, suggestaddr)
        self.addMemoryMap(baseva, perms, name, fill*size)
        return baseva

    def findFreeMemoryBlock(self, size, suggestaddr=0x1000, MIN_MEM_ADDR = 0x1000):
        '''
        Find a block of memory in the address-space of the correct size which 
        doesn't overlap any existing maps.  Attempts to offer the map starting
        at suggestaddr.  If not possible, scans the rest of the address-space
        until it finds a suitable location or loops twice(ie. no gap large 
        enough to accommodate a map of this size exists.

        DOES NOT ALLOCATE.  see allocateMemory() if you want the map created
        '''
        baseva = None
        looped = False

        tmpva = suggestaddr
        maxaddr = (1 << (8 * self.imem_psize)) - 1

        while baseva is None:
            # if we roll into illegal memory, start over at page 2.  skip 0.
            if tmpva > maxaddr:
                if looped:
                    raise e_exc.NoValidFreeMemoryFound(size)

                looped = True
                tmpva = MIN_MEM_ADDR

            # check potential map for any overlap
            good = True
            tmpendva = tmpva + size - 1
            for mmva, mmsz, mmperm, mmname in self.getMemoryMaps():
                mmendva = mmva + mmsz - 1
                if tmpva <= mmva < tmpendva or \
                        tmpva <= mmendva < tmpendva or \
                        mmva <= tmpva < mmendva or \
                        mmva <= tmpendva < mmendva:

                    # we ran into a memory map.  adjust.
                    good = False
                    tmpva = mmendva
                    tmpva += PAGE_NMASK
                    tmpva &= PAGE_MASK
                    break

            if good:
                baseva = tmpva

        return baseva

    def addMemoryMap(self, va, perms, fname, bytez):
        '''
        Add a memory map to this object...
        '''
        msize = len(bytez)
        mmap = (va, msize, perms, fname)
        hlpr = [va, va+msize, mmap, bytez]
        self._map_defs.append(hlpr)
        return

    def delMemoryMap(self, mapva):
        '''
        Delete a memory map from this object...
        '''
        for midx, (mva, mmaxva, mmap, mbytes) in enumerate(self._map_defs):
            if mva == mapva:
                return self._map_defs.pop(midx)

        raise e_exc.MapNotFoundException(mapva)

    def getMemorySnap(self):
        '''
        Take a memory snapshot which may be restored later.

        Example: snap = mem.getMemorySnap()
        '''
        return [list(mdef) for mdef in self._map_defs]

    def setMemorySnap(self, snap):
        '''
        Restore a previously saved memory snapshot.

        Example: mem.setMemorySnap(snap)
        '''
        self._map_defs = [list(md) for md in snap]

    def getMemoryMap(self, va):
        """
        Get the va,size,perms,fname tuple for this memory map
        """
        if va is None:
            return None
        for mva, mmaxva, mmap, mbytes in self._map_defs:
            if mva <= va < mmaxva:
                return mmap
        return None

    def getMemoryMaps(self):
        return [mmap for mva, mmaxva, mmap, mbytes in self._map_defs]

    def readMemory(self, va, size):
        '''
        Read memory from maps stored in memory maps.
        '''
        for mva, mmaxva, mmap, mbytes in self._map_defs:
            if mva <= va < mmaxva:
                mva, msize, mperms, mfname = mmap
                if not mperms & MM_READ:
                    raise envi.SegmentationViolation(va)
                offset = va - mva
                return mbytes[offset:offset+size]
        raise envi.SegmentationViolation(va)

    def writeMemory(self, va, bytes):
        for mapdef in self._map_defs:
            mva, mmaxva, mmap, mbytes = mapdef
            if mva <= va < mmaxva:
                mva, msize, mperms, mfname = mmap
                if not (mperms & MM_WRITE or self._supervisor):
                    raise envi.SegmentationViolation(va)
                offset = va - mva
                mapdef[3] = mbytes[:offset] + bytes + mbytes[offset+len(bytes):]
                return

        raise envi.SegmentationViolation(va)

    def getByteDef(self, va):
        """
        An optimized routine which returns the existing
        segment bytes sequence without creating a new
        string object *AND* an offset of va into the
        buffer.  Used internally for optimized memory
        handling.  Returns (offset, bytes)
        """
        for mapdef in self._map_defs:
            mva, mmaxva, mmap, mbytes = mapdef
            if mva <= va < mmaxva:
                offset = va - mva
                return (offset, mbytes)
        raise envi.SegmentationViolation(va)

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        '''
        Parse an opcode from the specified virtual address.

        Example: op = m.parseOpcode(0x7c773803)
        '''
        off, b = self.getByteDef(va)
        return self.imem_archs[(arch & envi.ARCH_MASK) >> 16].archParseOpcode(b, off, va)

    def readMemString(self, va, maxlen=0xfffffff):
        '''
        Returns a C-style string from memory.  Stops at Memory Map boundaries, or the first NULL (\x00) byte.
        '''

        for mva, mmaxva, mmap, mbytes in self._map_defs:
            if mva <= va < mmaxva:
                mva, msize, mperms, mfname = mmap
                if not mperms & MM_READ:
                    raise envi.SegmentationViolation(va)
                offset = va - mva

                # now find the end of the string based on either \x00, maxlen, or end of map
                end = mbytes.find(b'\x00', offset)

                left = end - offset
                if end == -1:
                    # couldn't find the NULL byte
                    mend = offset + maxlen
                    cstr = mbytes[offset:mend]
                else:
                    # couldn't find the NULL byte go to the end of the map or maxlen
                    mend = offset + (maxlen, left)[left < maxlen]
                    cstr = mbytes[offset:mend]
                return cstr

        raise envi.SegmentationViolation(va)


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

    def write(self, bytes):
        self.memobj.writeMemory(self.offset, bytes)
        self.offset += len(bytes)


def memdiff(bytes1, bytes2):
    '''
    Return a list of (offset, size) tuples showing any memory
    differences between the given bytes.
    '''
    # Quick/Optimized case...
    if bytes1 == bytes2:
        return []

    size = len(bytes1)
    if size != len(bytes2):
        raise Exception('memdiff *requires* same size bytes')
    ret = []
    offset = 0
    while offset < size:
        if bytes1[offset] != bytes2[offset]:
            beginoff = offset
            # Gather up all the difference bytes.
            while (offset < size and bytes1[offset] != bytes2[offset]):
                offset += 1
            ret.append((beginoff, offset-beginoff))
        offset += 1
    return ret
