'''
Unified binary executable file format module.

The BexFile class implements the concepts common to most
executable formats.  Individual formats will extend the API
and may implement additional APIs for retrieving format
specific information.
'''

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

        self._bex_infodoc('memsize','The size of the memory range required to load the BexFile')
        self._bex_infodoc('filesize','The size of the file provided for parsing')

    def _bex_infodoc(self, name, doc):
        self._bex_infodocs[name] = doc

    @cacheapi
    def info(self, name):
        '''
        Retrieve a value from the bex info dictionary.

        Info conventions:

        'architecture':<archname>   - the executable architecture
        'platform':<platname>       - the platform/os the bex is native to

        '''
        ret = self._bex_info.get(name)
        if ret != None:
            return ret

        cb = getattr(self,'_bex_info_%s' % name)
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
    def entry(self):
        '''
        Return the relative address of the entry point (or None).
        '''
        return self._bex_entry()

    @cacheapi
    def baseaddr(self):
        '''
        Return the suggested base address from the executable file.
        ( or None if not present )
        '''
        return self._bex_baseaddr()

    @cacheapi
    def relocs(self):
        '''
        Retrieve a list of the relocation tuples for the executable file.
        Each reloc is returned as a tuple of ( rtype, ra, rinfo )

        Example:

            for rtype,ra,rinfo in bex.relocs():
                print("reloc at raddr: 0x%.8x" % ra)
        '''
        return self._bex_relocs()

    @cacheapi
    def imports(self):
        '''
        Return a set of (ra,lib,func) tuples for the executable file.

        Example:

            for ra,lib,func in bex.imports():
                print('import slot at: %d lib: %s func: %s' % (ra,lib,func))
        '''
        return self._bex_imports()

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
        return self._bex_ra2off(ra)

    @cacheapi
    def off2ra(self, off):
        '''
        Translate from a file offset to an ra based on memmaps.
        '''
        for addr,size,perms,foff in self.memmaps():
            if foff != None and off >= foff and off <= (foff + size):
                return addr + (off - foff)

    @cacheapi
    def probera(self, ra):
        off = self.ra2off(ra)
        return self.probeoff(off)

    @cacheapi
    def probeoff(self, off):
        return off < self.info('filesize')

    def readAtRaddr(self, ra, size, exact=True):
        '''
        Read from the underlying file by translating a relative address.
        '''
        off = self.ra2off(ra)
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
        ptrsize = self.info('ptrsize')
        byteorder = self.info('byteorder')
        buf = self.readAtRaddr( ra, ptrsize, exact=True)
        if buf == None:
            return None
        return int.from_bytes(buf,byteorder=byteorder)

    def _bex_ra2off(self, ra):
        for addr,size,perms,off in self.memmaps():
            if off != None and ra >= addr and raddr <= (addr + size):
                return off + (raddr-addr)

    def _bex_info_filesize(self):
        self._bex_fd.seek(0,2)
        return self._bex_fd.tell()

    def _bex_entry(self): return None
    def _bex_bintype(self): raise implement('_bex_bintype')
    def _bex_baseaddr(self): return None

    def _bex_relocs(self): return []            # [ (ra, type, info), ... ]
    def _bex_memmaps(self): return []           # [ (ra,perm,bytez), ... ]
    def _bex_symbols(self): return []           # [ (ra, size, name, info), ... ]
    def _bex_imports(self): return []           # [ (ra, lib, func), ... ]
    def _bex_sections(self): return []          # [ (ra, size, name), ... ]

    def _bex_info_arch(self): return None       # return a vivisect arch name
    def _bex_info_ptrsize(self): return None    # return sizeof(void *)
    def _bex_info_byteorder(self): return None  # return int byte order

bexformats = {}
def addBexFormat(name,checker,parser):
    '''
    Register a new bex format with a "checker" and "parser" callbacks.

    checker(fd)
    parser(fd,**kwargs)
    '''
    bexformats[name] = (checker,parser)

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
    for name,(checker,parser) in bexformats.items():
        fd.seek(offset) # reset fd offset to where it started
        try:
            if not checker(fd):
                continue
        except Exception as e:
            traceback.print_exc()
            print('bex checker error (%s): %s' % (name,e))

        return parser(fd,**kwargs)
