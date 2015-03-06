'''
Unified binary executable file format module.

The BexFile class implements the concepts common to most
executable formats.  Individual formats will extend the API
and may implement additional APIs for retrieving format
specific information.
'''
import os
import hashlib
import traceback

from synapse.lib.apicache import ApiCache,cacheapi

class BexFile(ApiCache):
    '''
    BexFile base class from which individual format parsers extend.
    '''
    def __init__(self, fd, **kwargs):
        ApiCache.__init__(self)
        self._bex_fd = fd
        self._bex_info = kwargs
        self._bex_infodocs = {}
        self._bex_anomalies = []    # (ra,typ,info)

        #self._bex_info.setdefault('zeromap',None)

        self._bex_infodoc('raisoff','Set to True if ra=off for this bex')
        self._bex_infodoc('zeromap','The size of a 0 based region where ra == off')
        self._bex_infodoc('memsize','The size of the memory range required to load the BexFile')

    def anomaly(self, ra, atype, **info):
        '''
        Record that the binary file contains an anomaly or parser edge case.
        '''
        #print('bex anomaly: %s %s %r' % (ra,atype,info))
        self._bex_anomalies.append( (ra,atype,info) )

    def anomalies(self):
        '''
        Retrieve the list of (ra,type,info) anomaly tuples.

        Example:

            for ra,atype,ainfo in bex.anomalies():
                print('anomaly (%s) at ra: %d' % (rtype,ra))

        '''
        return list(self._bex_anomalies)

    def _bex_infodoc(self, name, doc):
        self._bex_infodocs[name] = doc

    @cacheapi
    def arch(self):
        '''
        Return the name of the architecture of the binary executable.
        '''
        return self._bex_arch()

    @cacheapi
    def format(self):
        '''
        Return the name of the binary executable format.

        Example:

            if bex.format() == 'elf':
                elfstuff(bex)

        '''
        return self._bex_format()

    @cacheapi
    def ptrsize(self):
        '''
        Return the size of a pointer for the binary executable.

        Example:

            if bex.ptrsize() == 8:
                print('64 bit binary!')

        '''
        return self._bex_ptrsize()

    @cacheapi
    def platform(self):
        '''
        Return the platform name for the binary executable.

        Example:

            if bex.platform() == 'linux':
                linuxstuff(bex)

        '''
        return self._bex_platform()

    @cacheapi
    def byteorder(self):
        '''
        Return "little" or "big" byteorder string ( for use with int.from_bytes )

        Example:

            if bex.byteorder() == 'little':
                stuff(bex)

        '''
        return self._bex_byteorder()

    @cacheapi
    def path(self):
        return self._bex_path()

    @cacheapi
    def info(self, name):
        '''
        Retrieve a value from the bex "extended info" dictionary.

        This is used to access format specific items such as PE headers.

        Example:

            if bex.format() == 'pe':
                nthdr = bex.info('pe:nt')
                ntstuff(nthdr)

        '''
        ret = self._bex_info.get(name)
        if ret != None:
            return ret

        methname = name.replace(':','_')
        cb = getattr(self, '_bex_info_%s' % methname, None)
        if cb == None:
            return None

        ret = cb()
        self._bex_info[name] = ret
        return ret

    def infodocs(self):
        '''
        Returns a list of (name,doc) tuples for the extended info available
        in this BexFile.
        '''
        return self._bex_infodocs.items()

    @cacheapi
    def baseaddr(self):
        '''
        Return the suggested base address from the executable file.
        ( or None if not present )
        '''
        return self._bex_baseaddr()

    @cacheapi
    def libname(self):
        '''
        Return a normalized "libname" for the bexfile.

        Where possible the libname is used to resolve dependancies
        between loaded files.  The names should be compatible with
        vtrace's "libnorm" concept.

        Example:

            if bex.libname() == 'kernel32':
                print('it claims to be kernel32.dll!')

        '''
        return self._bex_libname()

    @cacheapi
    def relocs(self):
        '''
        Retrieve a list of the relocation tuples for the executable file.
        Each reloc is returned as a tuple of ( rtype, ra, rinfo )

        Example:

            for ra,rtype,rinfo in bex.relocs():
                print("reloc at raddr: 0x%.8x" % ra)

        Reloc types:
        * 'ptr'   - adjustment of a pointer in memory

        Reloc info:
        * pre=True    - the reloc slot has requested base already ("prelinked")
        * size:<int>  - size of reloc slot in memory ( default: ptrsize() )

        '''
        return self._bex_relocs()

    @cacheapi
    def imports(self):
        '''
        Return a list of (ra,lib,func) tuples for the executable file.

        Example:

            for ra,lib,func in bex.imports():
                print('import slot at: %d lib: %s func: %s' % (ra,lib,func))
        '''
        return self._bex_imports()

    @cacheapi
    def exports(self):
        '''
        Return a list of (ra,name,etype) for the various exported entry points.

        Example:

            for ra,name,etype in bex.exports():
                dostuff(ra,name,etype)

        NOTE: for "etype" defs, see vivisect.workspace.VivWorkspace.addFileEntry
        '''
        return self._bex_exports()

    @cacheapi
    def memmaps(self):
        '''
        Return a list of (ra,perms,bytez) tuples for
        the memory maps defined in the executable file.  If the memory
        map is defined within the file, off is the offset within the
        file ( otherwise None )
        '''
        return self._bex_memmaps()

    @cacheapi
    def symbols(self):
        '''
        Return a list of (ra,size,name,info) tuples for the
        symbols defined in the executable file.

        Additional flags in info:
            * func=True     - a procedural entry point
            * code=True     - a code entry point
            * data=<type>   - a global variable

        ( possibly other platform specific details )

        NOTE: Info dictionary contents depend on type and format.
        '''
        return self._bex_symbols()

    @cacheapi
    def sections(self):
        '''
        Return a list of section tuples (ra,size,name) for the sections
        defined in an executable file.

        Example:
            for ra,size,name in b.sections():
                print("section raddr: 0x%.8x (%s)" % (ra,name))

        NOTE: "sections" are seperated from "memory maps" in the
              BexFile API to account for formats which define them
              differently.  In many instances, they may be equivalent.
        '''
        return self._bex_sections()

    @cacheapi
    def section(self, name):
        '''
        Return the symbol tuple (type,name,ra,info) or None for a section by name.

        Example:
            sectup = bex.section('.text')
            if sectup != None:
                print("has .text section!")
        '''
        for sec in self.sections():
            if sec[2] == name:
                return sec

    @cacheapi
    def bintype(self):
        '''
        Return a string representing the "type" of binary executable.
        The following types are valid:
            "exe"   - The file represents an exec-able process image
            "dyn"   - The file represents a dynamically loadable library.
            "unk"   - The file binary type is unknown (generally an error).

        For most purposes, embedded images such as firmware and bios
        should return "exe".

        Example:
            if bex.bintype() == "dyn":
                libstuff(bex)
        '''
        return self._bex_bintype()

    @cacheapi
    def ra2off(self, ra):
        '''
        Translate from a relative addr to a file offset based on memmaps.
        '''
        # bootstrap convenience for formats which map the beginning
        # of the file at bex.baseaddr() essentially making off==ra
        # while within the first page.
        if self.info('raisoff'):
            return ra

        zeromap = self.info('zeromap')
        if zeromap != None and ra < zeromap:
            return ra

        return self._bex_ra2off(ra)

    #@cacheapi
    #def off2ra(self, off):
        #'''
        ##Translate from a file offset to an ra based on memmaps.
        #'''
        #for addr,size,perms,foff in self.memmaps():
            #if foff != None and off >= foff and off <= (foff + size):
                #return addr + (off - foff)

    @cacheapi
    def probera(self, ra):
        off = self.ra2off(ra)
        return self.probeoff(off)

    @cacheapi
    def probeoff(self, off):
        return off < self.filesize()

    def struct(self, ra, cls, off=False):
        '''
        Construct a vstruct class and parse bytes at a relative addr.

        Example:

            foo = bex.struct( ra, FOO_STRUCT )
            if foo != None:
                stuff(foo)

        NOTE: if the addr is invalid ( or not long enough ) return None
        '''
        obj = cls()
        size = len(obj)

        if off:
            b = self.readAtOff(ra,size)
        else:
            b = self.readAtRaddr(ra,size)

        if b == None:
            return None

        obj.vsParse(b)
        return obj

    def structs(self, ra, size, cls, off=False):
        '''
        Yield structs parsed from the relative addr up to size.

        Example:

            for foo in bex.structs(ra, size, FOO_STRUCT):
                dostuff(foo)

        '''
        ramax = ra + size
        while ra < ramax:
            obj = self.struct(ra, cls, off=off)
            if obj == None:
                break

            yield ra,obj
            ra += len(obj)

    def readAtRaddr(self, ra, size, exact=True):
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
        self._bex_fd.seek(off)
        ret = self._bex_fd.read(size)
        if exact and len(ret) != size:
            return None

        return ret

    def asciiAtOff(self, off, size):
        return self.readAtOff(off,size,exact=False).split(b'\x00')[0].decode('ascii')

    def asciiAtRaddr(self, ra, size):
        '''
        Read an ascii string at the given relative address.

        Size is used as a *maximum* but strings may be returned which
        are shorter when a NULL is encountered or there are insufficient
        bytes.

        NOTE: in the event of a totally invalid ra, this returns ''
        '''
        return self.readAtRaddr(ra,size,exact=False).split(b'\x00')[0].decode('ascii')

    def ptrAtRaddr(self, ra):
        ptrsize = self.ptrsize()
        byteorder = self.byteorder()
        buf = self.readAtRaddr( ra, ptrsize, exact=True)
        if buf == None:
            return None
        return int.from_bytes(buf,byteorder=byteorder)

    #def _bex_ra2off(self, ra):
        #for addr,perms,mem in self.memmaps():
            #if off != None and ra >= addr and raddr <= (addr + size):
                #return off + (raddr-addr)

    @cacheapi
    def filesize(self):
        return self._bex_filesize()

    def _bex_filesize(self):
        self._bex_fd.seek(0,2)
        return self._bex_fd.tell()

    @cacheapi
    def md5(self):
        return self._bex_md5()

    def _bex_md5(self):
        self._bex_fd.seek(0)
        # no need to chunk considering...
        return hashlib.md5( self._bex_fd.read() ).digest()

    def _bex_path(self):
        return self._bex_fd.name

    def _bex_libname(self):
        path = self.path()
        if path == None:
            return None

        # best possible general case...
        base = os.path.basename( path )
        return base.lower().rsplit('.',1)[0]

    def _bex_ptrsize(self):
        return ptrsizes.get(self.arch())

    def _bex_bintype(self): return 'unk'
    def _bex_baseaddr(self): return None

    def _bex_relocs(self): return []            # [ (ra, type, info), ... ]
    def _bex_memmaps(self): return []           # [ (ra,perm,bytez), ... ]
    def _bex_symbols(self): return []           # [ (ra, size, name, info), ... ]
    def _bex_imports(self): return []           # [ (ra, lib, func), ... ]
    def _bex_sections(self): return []          # [ (ra, size, name), ... ]

    def _bex_arch(self): return None       # vivisect arch name
    def _bex_format(self): return None     # format name
    def _bex_platform(self): return None   # platform name for the binary
    def _bex_byteorder(self): return None  # int byte order

# a set of default pointer sizes
ptrsizes = {
    'arm':4,
    'i386':4,
    'amd64':8,
}

bexformats = {}
def addBexFormat(name,checker,parser):
    '''
    Register a new bex format with a "checker" and "parser" callbacks.

    checker(fd)
    parser(fd,**kwargs)
    '''
    bexformats[name] = (checker,parser)

class BexError(Exception):pass
class BexInvalidFormat(BexError):pass

def getBexFile(fd,**kwargs):
    '''
    Returns a BexFile object for the given fd.

    Example:
        import vivisect.lib.bexfile as v_bexfile

        fd = open('woot.exe','rb')
        bex = v_bexfile.getBexFile(fd)

        for map in bex.memmaps():
            dostuff(map)
    '''
    offset = fd.tell()

    fmt = kwargs.get('format')
    if fmt != None:
        checkparse = bexformats.get(fmt)
        if checkparse == None:
            raise BexInvalidFormat(fmt)
        checker,parser = checkparse
        return parser(fd,**kwargs)

    for name,(checker,parser) in bexformats.items():
        fd.seek(offset) # reset fd offset to where it started
        try:
            if not checker(fd):
                continue
        except Exception as e:
            traceback.print_exc()
            print('bex checker error (%s): %s' % (name,e))

        return parser(fd,**kwargs)
