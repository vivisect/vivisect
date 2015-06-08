'''
Unified binary executable file format module.

The BinFile class implements the concepts common to most
executable formats.  Individual formats will extend the API
and may implement additional APIs for retrieving format
specific information.
'''
import os
import hashlib
import traceback
import collections

from synapse.lib.apicache import ApiCache,cacheapi

class BinDict(collections.defaultdict):

    def __init__(self, info=None):
        collections.defaultdict.__init__(self)
        if info != None:
            self.update(info)

        self.ctors = {}

    def addKeyCtor(self, name, ctor):
        self.ctors[name] = ctor

    def form(self, name):
        return self[name]

    def cog(self, key):
        '''
        construct or get
        '''
        return self[key]

    def __missing__(self, key):
        meth = self.ctors.get(key)
        if meth != None:
            ret = meth()
            self[key] = ret
            return ret

class BinFile(ApiCache):
    '''
    BinFile base class from which individual format parsers extend.
    '''
    def __init__(self, byts, **info):

        ApiCache.__init__(self)

        self.byts = byts
        self.info = BinDict(info)
        self.infodocs = {}
        self.anomalies = []    # (ra,typ,info)

        self.secbyname = {}

        self.setInfoDoc('raisoff','Set to True if ra=off for this binary')
        self.setInfoDoc('zeromap','The size of a 0 based region where ra == off')

    @staticmethod
    def isMyFormat(byts):
        '''
        Check if the bytes are a file of our binary format.

        Notes:

            * this is used by BinFile implementors to hint the file parser.

        '''
        return False

    def addAnomaly(self, msg, **info):
        '''
        Record that the binary file contains an anomaly or parser edge case.

        Example:

            if bf.foo < 10:
                bf.addAnomaly('foo is < 10', ra=ra, foo=bf.foo)

        Notes:
            * it is good form to include either ra or off

        '''
        self.anomalies.append( (msg,info) )

    def getAnomalies(self):
        '''
        Retrieve a list of the parser anomalies or edge cases.

        Example:

            for msg,info in bf.getAnomalies():
                print('msg: %s' % (msg,))

        '''
        return list(self.anomalies)

    def setInfoDoc(self, name, doc):
        self.infodocs[name] = doc

    def getArch(self):
        '''
        Return the name of the architecture of the binary executable.

        Example:

            arch = bf.getArch()

        '''
        return self._getArch()

    def getFormat(self):
        '''
        Return the name of the binary executable format.

        Example:

            if bf.getFormat() == 'elf':
                elfstuff(bf)

        '''
        return self._getFormat()

    def getPtrSize(self):
        '''
        Return the size of a pointer for the binary executable.

        Example:

            if bf.getPtrSize() == 8:
                print('64 bit binary!')

        '''
        return self._getPtrSize()

    def getPlatform(self):
        '''
        Return the platform name for the binary executable.

        Example:

            if bf.getPlatform() == 'linux':
                linuxstuff(bf)

        '''
        return self._getPlatform()

    def getByteOrder(self):
        '''
        Return "little" or "big" byteorder string ( for use with int.from_bytes )

        Example:

            if bf.getByteOrder() == 'little':
                stuff(bf)

        '''
        return self._getByteOrder()

    def getInfo(self, name):
        '''
        Retrieve a value from the binary "extended info" dictionary.

        This is used to access format specific items such as PE headers.

        Example:

            if bf.getFormat() == 'pe':
                nthdr = bf.getInfo('pe:nt')
                ntstuff(nthdr)

        '''
        return self.info.cog(name)

    def getInfoDocs(self):
        '''
        Returns a list of (name,doc) tuples for the extended info available
        in this BinFile.
        '''
        return self.infodocs.items()

    def getBaseAddr(self):
        '''
        Return the suggested base address from the executable file.
        ( or None if not present )

        Example:

            addr = bf.getBaseAddr()
            if addr != None:
                print('base addr: 0x%.8x' % (addr,))

        '''
        return self._getBaseAddr()

    @cacheapi
    def getLibName(self):
        '''
        Return a normalized "libname" for the binfile.

        Where possible the libname is used to resolve dependancies
        between loaded files.  The names should be compatible with
        vtrace's "libnorm" concept.

        Example:

            if bf.getLibName() == 'kernel32':
                print('it claims to be kernel32.dll!')

        '''
        return self._getLibName()

    @cacheapi
    def getRelocs(self):
        '''
        Retrieve a list of the relocation tuples for the executable file.
        Each reloc is returned as a tuple of ( rtype, ra, rinfo )

        Example:

            for ra,rtype,rinfo in bf.getRelocs():
                print("reloc at raddr: 0x%.8x" % ra)

        Reloc types:
        * 'ptr'   - adjustment of a pointer in memory

        Reloc info:
        * pre=True    - the reloc slot has requested base already ("prelinked")
        * size:<int>  - size of reloc slot in memory ( default: getPtrSize() )

        '''
        return self._getRelocs()

    @cacheapi
    def getImports(self):
        '''
        Return a list of (ra,lib,func) tuples for the executable file.

        Example:

            for ra,lib,func in bf.getImports():
                print('import slot at: %d lib: %s func: %s' % (ra,lib,func))
        '''
        return self._getImports()

    @cacheapi
    def getExports(self):
        '''
        Return a list of (ra,name,etype) for the various exported entry points.

        Example:

            for ra,name,etype in bf.getExports():
                dostuff(ra,name,etype)

        NOTE: for "etype" defs, see vivisect.workspace.VivWorkspace.addFileEntry
        '''
        return self._getExports()

    @cacheapi
    def getMemoryMaps(self):
        '''
        Return a list of (ra,info) tuples for the memory maps defined in the file.

        Example:

            base = bf.baseaddr()
            for mmap in bf.getMemoryMaps():
                print('map at: 0x%.8x' % ( base + map[0], ))

        Notes:

            * info convention matches vivisect.hal.memory

        '''
        return self._getMemoryMaps()

    @cacheapi
    def getSymbols(self):
        '''
        Return a list of (ra,info) tuples for the
        symbols defined in the executable file.

        Additional flags in info:
            * name=<name>   - name of the symbol
            * size=<int>    - size of the symbol
            * func=True     - a procedural entry point
            * code=True     - a code entry point
            * data=<type>   - a global variable

        ( possibly other platform specific details )

        NOTE: Info dictionary contents depend on type and format.
        '''
        return self._getSymbols()

    @cacheapi
    def getSections(self):
        '''
        Return a list of tuples (ra,size,name,info) for the sections.

        Example:
            for addr,size,name,info in b.getSections():
                print('section: ra: 0x%.8x (%s)' % (addr, name))

        NOTE: "sections" are seperated from "memory maps" in the
              BinFile API to account for formats which define them
              differently.  In many instances, they may be equivalent.
        '''
        secs = self._getSections()
        for sec in secs:
            self.secbyname[ sec[2] ] = sec
        return secs

    def getSectionByName(self, name):
        '''
        Return a section tuple (ra,size,name,info) by name or None.

        Example:

            sec = b.getSectionByName('.text')
            if sec != None:
                dostuff(sec)

        '''
        # make sure sections are loaded/cached
        self.getSections()
        return self.secbyname.get(name)

    def getBinType(self):
        '''
        Return a string representing the "type" of binary executable.
        The following types are valid:
            "exe"   - The file represents an exec-able process image
            "dyn"   - The file represents a dynamically loadable library.
            "unk"   - The file binary type is unknown (generally an error).

        For most purposes, embedded images such as firmware and bios
        should return "exe".

        Example:

            if bf.getBinType() == "dyn":
                libstuff(bf)

        '''
        return self._getBinType()

    @cacheapi
    def ra2off(self, ra):
        '''
        Translate from a relative addr to a file offset based on mmaps.
        '''
        # bootstrap convenience for formats which map the beginning
        # of the file at bf.baseaddr() essentially making off==ra
        # while within the first page.
        if self.getInfo('raisoff'):
            return ra

        zeromap = self.getInfo('zeromap')
        if zeromap != None and ra < zeromap:
            return ra

        return self._bin_ra2off(ra)

    @cacheapi
    def off2ra(self, off):
        '''
        #Translate from a file offset to an ra based on mmaps.
        '''
        for mmap in self.getMemoryMaps():
            foff = mmap[1].get('fileoff')
            if foff == None:
                continue

            size = mmap[1].get('filesize')
            if not size:
                continue

            if off < foff:
                continue

            if off > foff + size:
                continue

            return mmap[0] + (off - foff)

    @cacheapi
    def probera(self, ra):
        off = self.ra2off(ra)
        return self.probeoff(off)

    @cacheapi
    def probeoff(self, off):
        return off < self.filesize()

    def getStruct(self, off, ctor):
        '''
        Construct a vstruct class and parse bytes from a file offset.

        Example:

            foo = bf.getStruct( off, FOO_STRUCT )
            if foo != None:
                stuff(foo)

        Notes:

            * if the offset is invalid ( or None ) returns None
              ( allows lazy x.getStruct( x.ra2off(y), FOO ) w/o check )

        '''
        if off == None:
            return None

        vs = ctor()
        vs.vsParse(self.byts, offset=off)

        return vs

    def getStructs(self, ra, size, cls, off=False):
        '''
        Yield structs parsed from the relative addr up to size.

        Example:

            for foo in bf.getStructs(ra, size, FOO_STRUCT):
                dostuff(foo)

        '''
        ramax = ra + size
        while ra < ramax:
            obj = self.getStruct(ra, cls)
            if obj == None:
                break

            yield ra,obj
            ra += len(obj)

    def readAtRa(self, ra, size, exact=True):
        '''
        Read from the underlying file by translating a relative address.
        '''
        off = self.ra2off(ra)
        if off == None:
            return None

        return self.readAtOff(off,size)

    def readAtOff(self, off, size, exact=True):
        '''
        Read from the underlying file at the given offset.

        NOTE: similarly to file.read(), the bytes read from the file
              may fall short of "size" without triggering an error.
        '''
        ret = self.byts[off:off+size]
        if exact and len(ret) != size:
            return None

        return ret

    def asciiAtOff(self, off, maxsize):
        '''
        Read a (possibly NULL terminated) ascii string from a file offset.


        Example:

            s = bf.asciiAtOff(off, 256)

        Notes:

            * This API is short read safe

        '''
        byts = self.byts[off:off+maxsize]
        return byts.split(b'\x00',1)[0].decode('ascii')

    def ascii(self, off, maxsize):
        if off == None:
            return None
        return self.asciiAtOff(off, maxsize)

    def getBytes(self):
        '''
        Return a reference to the bytes for this file.

        Example:

            byts = bf.getBytes()

        '''
        return self.byts

    def asciiAtRa(self, ra, maxsize):
        '''
        Read an ascii string at the given relative address.

        Size is used as a *maximum* but strings may be returned which
        are shorter when a NULL is encountered or there are insufficient
        bytes.

        NOTE: in the event of a totally invalid ra, this returns ''
        '''
        off = self.ra2off(ra)
        return self.asciiAtOff(off, maxsize)

    def ptrAtRa(self, ra):
        '''
        Read and decode a pointer from a relative address.


        Example:

            ptr = bf.ptrAtRa(addr)

        '''
        ptrsize = self.getPtrSize()
        byteorder = self.getByteOrder()
        buf = self.readAtRa( ra, ptrsize, exact=True)
        if buf == None:
            return None
        return int.from_bytes(buf,byteorder=byteorder)

    @cacheapi
    def getSize(self):
        '''
        Retrieve the size of the binary executable file.
        '''
        return self._getSize()

    @cacheapi
    def getMd5(self):
        return self._getMd5()

    def _getSize(self):
        return len(self.byts)

    def _getMd5(self):
        return hashlib.md5( self.byts ).digest()

    @cacheapi
    def _getLibName(self):
        return 'unknown'

    def _getPtrSize(self):
        return ptrsizes.get(self.getArch())

    @cacheapi
    def _bin_ra2off(self, ra):
        for addr,size,perm,info in self.getMemoryMaps():

            if ra < addr:
                continue

            if ra > (addr + size):
                continue

            fileoff = info.get('fileoff')
            if fileoff == None:
                return None

            return fileoff + ( ra - addr )

    def _getBinType(self): return 'unk'
    def _getBaseAddr(self): return None

    def _getRelocs(self): return []            # [ (ra, type, info), ... ]
    def _getExports(self): return []            # (ra, name, info), ... ]
    def _getMemoryMaps(self): return []           # [ (ra,info), ... ]
    def _getSymbols(self): return []           # [ (ra, size, name, info), ... ]
    def _getImports(self): return []           # [ (ra, lib, func), ... ]
    def _getSections(self): return []          # [ (ra, size, name), ... ]

    def _getArch(self): return None       # vivisect arch name
    def _getFormat(self): return None     # format name
    def _getPlatform(self): return None   # platform name for the binary
    def _getByteOrder(self): return None  # int byte order

# a set of default pointer sizes
ptrsizes = {
    'arm':4,
    'i386':4,
    'amd64':8,
}

binformats = {}
def addBinFormat(name,binclass):
    '''
    Register a new bin format with a "checker" and "parser" callbacks.

    checker(byts)
    parser(byts,**info)
    '''
    binformats[name] = binclass

class BinError(Exception):pass
class BinInvalidFormat(BinError):pass

def getBinFile(byts, **info):
    '''
    Returns a BinFile object for the given bytes.

    Example:

        import vivisect.lib.binfile as v_binfile

        byts = open('woot.exe','rb')
        bf = v_binfile.getFile(byts)

        for map in bf.getMemoryMaps():
            dostuff(map)

    Notes:

        * Use MemBytes or FileBytes for partial reads

    '''
    fmt = info.get('format')
    if fmt != None:
        bincls = binformats.get(fmt)
        if bincls == None:
            raise BinInvalidFormat(fmt)

        return bincls(byts,**info)

    for name,bincls in binformats.items():
        try:

            if not bincls.isMyFormat(byts):
                continue

        except Exception as e:
            traceback.print_exc()
            print('bin isMyFormat error (%s): %s' % (name,e))

        return bincls(byts,**info)
