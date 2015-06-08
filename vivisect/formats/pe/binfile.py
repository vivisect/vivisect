import vivisect.lib.bits as v_bits
import vivisect.lib.binfile as v_binfile

from vertex.lib.common import tufo
from vivisect.hal.memory import MM_READ, MM_WRITE, MM_EXEC
from vivisect.vstruct.types import *

from vivisect.formats.pe.const import *

class IMAGE_BASE_RELOCATION(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        self.VirtualAddress = uint32()
        self.SizeOfBlock    = uint32()
        #self.blocks         = VArray()

        #self.vsOnset('SizeOfBlock',self._slot_blocksize)

    #def _slot_blocksize(self):
        ##self.blocks.vsClear()
        #for i in range( self.SizeOfBlock / 4 ):
            #self.blocks[i] = uint32()

class IMAGE_DATA_DIRECTORY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.VirtualAddress = uint32()
        self.Size           = uint32()

class IMAGE_DOS_HEADER(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.e_magic    = vbytes(2)
        self.e_cblp     = uint16()
        self.e_cp       = uint16()
        self.e_crlc     = uint16()
        self.e_cparhdr  = uint16()
        self.e_minalloc = uint16()
        self.e_maxalloc = uint16()
        self.e_ss       = uint16()
        self.e_sp       = uint16()
        self.e_csum     = uint16()
        self.e_ip       = uint16()
        self.e_cs       = uint16()
        self.e_lfarlc   = uint16()
        self.e_ovno     = uint16()
        self.e_res      = VArray([uint16() for i in range(4)])
        self.e_oemid    = uint16()
        self.e_oeminfo  = uint16()
        self.e_res2     = VArray([uint16() for i in range(10)])
        self.e_lfanew   = uint32()

class IMAGE_EXPORT_DIRECTORY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Characteristics    = uint32()
        self.TimeDateStamp      = uint32()
        self.MajorVersion       = uint16()
        self.MinorVersion       = uint16()
        self.Name               = uint32()
        self.Base               = uint32()
        self.NumberOfFunctions  = uint32()
        self.NumberOfNames      = uint32()
        self.AddressOfFunctions = uint32()
        self.AddressOfNames     = uint32()
        self.AddressOfOrdinals  = uint32()

class IMAGE_DEBUG_DIRECTORY(VStruct):
    def __init__(self):
      VStruct.__init__(self)
      self.Characteristics  = uint32()
      self.TimeDateStamp    = uint32()
      self.MajorVersion     = uint16()
      self.MinorVersion     = uint16()
      self.Type             = uint32()
      self.SizeOfData       = uint32()
      self.AddressOfRawData = uint32()
      self.PointerToRawData = uint32()

class CV_INFO_PDB70(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.CvSignature    = uint32()
        self.Signature      = GUID()
        self.Age            = uint32()
        self.PdbFileName    = cstr(260)

    #def vsParse(self, bytez, offset=0):
        #bsize = len(bytez) - offset
        #self.vsGetField('PdbFileName').vsSetLength( bsize - 24 )
        #return VStruct.vsParse(self, bytez, offset=offset)

class IMAGE_FILE_HEADER(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Machine              = uint16()
        self.NumberOfSections     = uint16()
        self.TimeDateStamp        = uint32()
        self.PointerToSymbolTable = uint32()
        self.NumberOfSymbols      = uint32()
        self.SizeOfOptionalHeader = uint16()
        self.Characteristics      = uint16()

class IMAGE_IMPORT_DIRECTORY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.OriginalFirstThunk = uint32()
        self.TimeDateStamp      = uint32()
        self.ForwarderChain     = uint32()
        self.Name               = uint32()
        self.FirstThunk         = uint32()

class IMAGE_IMPORT_BY_NAME(VStruct):
    def __init__(self, namelen=128):
        VStruct.__init__(self)
        self.Hint   = uint16()
        self.Name   = zstr(size=namelen)

class IMAGE_LOAD_CONFIG_DIRECTORY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Size                          = uint32()
        self.TimeDateStamp                 = uint32()
        self.MajorVersion                  = uint16()
        self.MinorVersion                  = uint16()
        self.GlobalFlagsClear              = uint32()
        self.GlobalFlagsSet                = uint32()
        self.CriticalSectionDefaultTimeout = uint32()
        self.DeCommitFreeBlockThreshold    = uint32()
        self.DeCommitTotalFreeThreshold    = uint32()
        self.LockPrefixTable               = uint32()
        self.MaximumAllocationSize         = uint32()
        self.VirtualMemoryThreshold        = uint32()
        self.ProcessHeapFlags              = uint32()
        self.ProcessAffinityMask           = uint32()
        self.CSDVersion                    = uint16()
        self.Reserved1                     = uint16()
        self.EditList                      = uint32()
        self.SecurityCookie                = uint32()
        self.SEHandlerTable                = uint32()
        self.SEHandlerCount                = uint32()

class IMAGE_NT_HEADERS(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Signature      = vbytes(4)
        self.FileHeader     = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER()

class IMAGE_NT_HEADERS64(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Signature      = vbytes(4)
        self.FileHeader     = IMAGE_FILE_HEADER()
        self.OptionalHeader = IMAGE_OPTIONAL_HEADER64()

class IMAGE_OPTIONAL_HEADER(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Magic                       = vbytes(2)
        self.MajorLinkerVersion          = uint8()
        self.MinorLinkerVersion          = uint8()
        self.SizeOfCode                  = uint32()
        self.SizeOfInitializedData       = uint32()
        self.SizeOfUninitializedData     = uint32()
        self.AddressOfEntryPoint         = uint32()
        self.BaseOfCode                  = uint32()
        self.BaseOfData                  = uint32()
        self.ImageBase                   = uint32()
        self.SectionAlignment            = uint32()
        self.FileAlignment               = uint32()
        self.MajorOperatingSystemVersion = uint16()
        self.MinorOperatingSystemVersion = uint16()
        self.MajorImageVersion           = uint16()
        self.MinorImageVersion           = uint16()
        self.MajorSubsystemVersion       = uint16()
        self.MinorSubsystemVersion       = uint16()
        self.Win32VersionValue           = uint32()
        self.SizeOfImage                 = uint32()
        self.SizeOfHeaders               = uint32()
        self.CheckSum                    = uint32()
        self.Subsystem                   = uint16()
        self.DllCharacteristics          = uint16()
        self.SizeOfStackReserve          = uint32()
        self.SizeOfStackCommit           = uint32()
        self.SizeOfHeapReserve           = uint32()
        self.SizeOfHeapCommit            = uint32()
        self.LoaderFlags                 = uint32()
        self.NumberOfRvaAndSizes         = uint32()
        self.DataDirectory               = VArray([IMAGE_DATA_DIRECTORY() for i in range(16)])

class IMAGE_OPTIONAL_HEADER64(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Magic                       = vbytes(2)
        self.MajorLinkerVersion          = uint8()
        self.MinorLinkerVersion          = uint8()
        self.SizeOfCode                  = uint32()
        self.SizeOfInitializedData       = uint32()
        self.SizeOfUninitializedData     = uint32()
        self.AddressOfEntryPoint         = uint32()
        self.BaseOfCode                  = uint32()
        self.ImageBase                   = uint64()
        self.SectionAlignment            = uint32()
        self.FileAlignment               = uint32()
        self.MajorOperatingSystemVersion = uint16()
        self.MinorOperatingSystemVersion = uint16()
        self.MajorImageVersion           = uint16()
        self.MinorImageVersion           = uint16()
        self.MajorSubsystemVersion       = uint16()
        self.MinorSubsystemVersion       = uint16()
        self.Win32VersionValue           = uint32()
        self.SizeOfImage                 = uint32()
        self.SizeOfHeaders               = uint32()
        self.CheckSum                    = uint32()
        self.Subsystem                   = uint16()
        self.DllCharacteristics          = uint16()
        self.SizeOfStackReserve          = uint64()
        self.SizeOfStackCommit           = uint64()
        self.SizeOfHeapReserve           = uint64()
        self.SizeOfHeapCommit            = uint64()
        self.LoaderFlags                 = uint32()
        self.NumberOfRvaAndSizes         = uint32()
        self.DataDirectory               = VArray([IMAGE_DATA_DIRECTORY() for i in range(16)])

class IMAGE_RESOURCE_DIRECTORY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Characteristics      = uint32()
        self.TimeDateStamp        = uint32()
        self.MajorVersion         = uint16()
        self.MinorVersion         = uint16()
        self.NumberOfNamedEntries = uint16()
        self.NumberOfIdEntries    = uint16()

class IMAGE_RESOURCE_DIRECTORY_ENTRY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Name           = uint32()
        self.OffsetToData   = uint32()

class IMAGE_RESOURCE_DATA_ENTRY(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.OffsetToData   = uint32()
        self.Size           = uint32()
        self.CodePage       = uint32()
        self.Reserved       = uint32()

class VS_FIXEDFILEINFO(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.Signature          = uint32()
        self.StrucVersion       = uint32()
        self.FileVersionMS      = uint32()
        self.FileVersionLS      = uint32()
        self.ProductVersionMS   = uint32()
        self.ProductVersionLS   = uint32()
        self.FileFlagsMask      = uint32()
        self.FileFlags          = uint32()
        self.FileOS             = uint32()
        self.FileType           = uint32()
        self.FileSubtype        = uint32()
        self.FileDateMS         = uint32()
        self.FileDateLS         = uint32()

class IMAGE_SECTION_HEADER(VStruct):

    def __init__(self):
        VStruct.__init__(self)
        self.Name                 = cstr(8)
        self.VirtualSize          = uint32()
        self.VirtualAddress       = uint32()
        self.SizeOfRawData        = uint32()
        self.PointerToRawData     = uint32()
        self.PointerToRelocations = uint32()
        self.PointerToLineNumbers = uint32()
        self.NumberOfRelocations  = uint16()
        self.NumberOfLineNumbers  = uint16()
        self.Characteristics      = uint32()

secsize = len(IMAGE_SECTION_HEADER())

class IMAGE_RUNTIME_FUNCTION_ENTRY(VStruct):
    """
    Used in the .pdata section of a PE32+ for all non
    leaf functions.
    """
    def __init__(self):
        VStruct.__init__(self)
        self.BeginAddress = uint32()
        self.EndAddress = uint32()
        self.UnwindInfoAddress = uint32()

class UNWIND_INFO(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.VerFlags       = uint8()
        self.SizeOfProlog   = uint8()
        self.CountOfCodes   = uint8()
        self.FrameRegister  = uint8()

class SignatureEntry(VStruct):

    def __init__(self):
        VStruct.__init__(self)

        self.size = int32(bigend=False)

        # should always be 0x00020200
        self.magic = vbytes(size=4)
        self.pkcs7 = vbytes()

    def pcb_size(self):
        size = self.size
        self.vsGetField('pkcs7').vsSetLength(size)

scnperms = (
    (IMAGE_SCN_MEM_READ,    MM_READ),
    (IMAGE_SCN_MEM_WRITE,   MM_WRITE),
    (IMAGE_SCN_MEM_EXECUTE, MM_EXEC),
    (IMAGE_SCN_CNT_CODE,    MM_EXEC),
)

archmap = {
    IMAGE_FILE_MACHINE_I386:'i386',
    IMAGE_FILE_MACHINE_IA64:'ia64',
    IMAGE_FILE_MACHINE_AMD64:'amd64',
}

ptrmap = {
    IMAGE_FILE_MACHINE_I386:4,
    IMAGE_FILE_MACHINE_IA64:8,
    IMAGE_FILE_MACHINE_AMD64:8,
}

class PeBinFile(v_binfile.BinFile):

    def __init__(self, fd, **info):
        info.setdefault('zeromap',4096)
        v_binfile.BinFile.__init__(self, fd, **info)

        self.info.addKeyCtor('pe:nt', self._getNtHeader )
        self.info.addKeyCtor('pe:dos', self._getDosHeader )
        self.info.addKeyCtor('pe:datadirs', self._getDataDirs )

        self.info.addKeyCtor('pe:relocs', self._getPeRelocs )
        self.info.addKeyCtor('pe:imports', self._getPeImports )
        self.info.addKeyCtor('pe:exports', self._getPeExports )
        self.info.addKeyCtor('pe:pdata', self._getPData )
        self.info.addKeyCtor('pe:highmask', self._getHighMask )

        self.info.addKeyCtor('pe:pdbpath', self._getPdbPath )

        #self._bin_infodoc('pe:dos','An IMAGE_DOS_HEADER vstruct object')
        #self._bin_infodoc('pe:nt','An IMAGE_NT_HEADERS(64) vstruct object')
        #self._bin_infodoc('pe:sections','A list of IMAGE_SECTION_HEADERS vstruct objects')
        #self._bin_infodoc('pe:imports','A list of IMAGE_IMPORT_DIRECTORY vstruct objects')
        #self._bin_infodoc('pe:exports','A tuple of (exports,forwards)')
        #self._bin_infodoc('pe:datadirs','A list of IMAGE_DATA_DIRECTORY vstruct objects')
        #self._bin_infodoc('pe:pdbpath','The PdbFileName from IMAGE_DEBUG_DIRECTORY (or None)')
        #self._bin_infodoc('pe:pdata','A list of (ra,IMAGE_RUNTIME_FUNCTION_ENTRY,UNWIND_INFO) tuples')

    def _getSections(self):

        nthdr = self.getInfo('pe:nt')
        doshdr = self.getInfo('pe:dos')

        ret = []

        count = nthdr.FileHeader.NumberOfSections
        size = count * secsize

        ra = doshdr.e_lfanew + len(nthdr)
        headers = list(self.getStructs(self.ra2off(ra), size, IMAGE_SECTION_HEADER))

        for hra,hdr in headers:
            name = hdr.Name
            size = hdr.VirtualSize
            ret.append( (hdr.VirtualAddress, size, name, {'header':hdr}) )

        return ret

    def _bin_ra2off(self, ra):
        for addr,size,name,info in self.getSections():
            if v_bits.within(ra, addr, size):
                hdr = info.get('header')
                return hdr.PointerToRawData + (ra - addr)

    def _getImports(self):
        # normalize lib names for the outer api
        ret = []
        for ra,lib,func in self.getInfo('pe:imports'):
            libname = lib.lower()
            if libname[-4:] in ('.dll','.sys','.ocx','.exe'):
                libname = libname[:-4]
            ret.append( (ra,libname,func) )
        return ret

    def _getBinType(self):
        if self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_EXPORT):
            return 'dyn'
        return 'exe'

    def getPeDataDir(self, idx, minsize=None):
        '''
        Retrieve and validate a PE data directory by index.
        Optionally specify a minimum size for the data directory.

        Example:

            edir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_EXPORT)

        '''
        dirent = self.getInfo('pe:datadirs')[idx]
        if not dirent.VirtualAddress:
            return None

        if not dirent.Size:
            return None

        if minsize != None and dirent.Size < minsize:
            return None

        return dirent

    def _getPeImports(self):
        ret = []

        impdir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_IMPORT)
        if impdir == None:
            return ()

        highmask = self.getInfo('pe:highmask')

        ra = impdir.VirtualAddress
        size = impdir.Size

        for ra,imp in self.getStructs(self.ra2off(ra),size,IMAGE_IMPORT_DIRECTORY):

            if not imp.Name:
                break

            libname = self.ascii(self.ra2off(imp.Name), 256)
            if not libname:
                break

            byname = imp.OriginalFirstThunk
            if byname == 0:
                byname = imp.FirstThunk

            funcs = []
            while True:
                ptr = self.ptrAtRa(byname)
                if not ptr:
                    break

                # check for ords
                if ptr & highmask:
                    # FIXME ordlookup!
                    ret.append( (byva, libname, 'ord%d' % (ptr & 0x7fffffff)) )
                    continue

                byn = IMAGE_IMPORT_BY_NAME()
                buf = self.readAtRa(ptr, 130)
                if not buf:
                    break

                byn.vsParse(buf)
                ret.append( (byname, libname, byn.Name) )

                byname += self.getPtrSize()

        return ret
            
    def _getPdbPath(self):
        return 'FIXME'

    def _getExports(self):

        ret = []

        ra = self.getInfo('pe:nt').OptionalHeader.AddressOfEntryPoint
        if ra:
            ret.append( (ra,'__entry','func') )

        # FIXME need a forwarders test!
        exps,fwds = self.getInfo('pe:exports')
        for ra,name,ordinal in exps:
            ret.append( (ra,name,'unkn') )

        # "pdata" entries are basically exported functions
        # with no names...
        for ra,ent,unwind in self.getInfo('pe:pdata'):
            flags = unwind.VerFlags >> 3
            # FIXME ported from legacy code, revisit
            if not flags & UNW_FLAG_CHAININFO:
                ret.append( (ent.BeginAddress, None, 'func') )

        return ret

    def _getRelocs(self):
        # translate PE relocs to viv relocs
        ret = []
        # FIXME check on sizing of different relocs
        for ra,rtype in self.getInfo('pe:relocs'):

            # ordered by likelyhood
            if rtype == IMAGE_REL_BASED_HIGHLOW:
                ret.append( (ra,'ptr',{'pre':True,'size':4}) )
                continue

            if rtype == IMAGE_REL_BASED_DIR64:
                ret.append( (ra,'ptr',{'pre':True,'size':8}) )
                continue

            if rtype == IMAGE_REL_BASED_ABSOLUTE:
                continue

            if rtype == IMAGE_REL_BASED_LOW:
                ret.append( (ra,'ptr',{'pre':True,'size':2}) )
                continue

            if rtype in (IMAGE_REL_BASED_HIGH, IMAGE_REL_BASED_HIGHADJ):
                ret.append( (ra,'ptr',{'pre':True,'size':2,'shr':16}) )
                continue

            self.addAnomaly('unknown reloc type: %d' % (rtype,), ra=ra, rtype=rtype)

        return ret

    def _getPeRelocs(self):

        rdir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_BASERELOC)
        if rdir == None:
            return()

        ra = rdir.VirtualAddress
        size = rdir.Size

        rmax = ra + size

        ret = []

        # iterate the variably sized IMAGE_BASE_RELOCATION blocks
        blk = self.getStruct(self.ra2off(ra), IMAGE_BASE_RELOCATION)
        while blk != None and ra < rmax:

            if not blk.VirtualAddress:
                break

            if not blk.SizeOfBlock:
                break

            cls = varray(blk.SizeOfBlock // 4, uint16)
            blocks = self.getStruct(self.ra2off(ra + len(blk)), cls)
            if blocks == None:
                break

            for i,typoff in blocks:
                typoff = int(typoff)
                typ = typoff >> 12
                off = typoff & 0xfff

                ret.append( ( blk.VirtualAddress + off, typ ) )

            ra += blk.SizeOfBlock
            blk = self.getStruct(self.ra2off(ra),IMAGE_BASE_RELOCATION)

        return ret

    def _getLibName(self):
        edir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_EXPORT)
        if edir == None:
            return None

        exp = self.getStruct(self.ra2off(edir.VirtualAddress),IMAGE_EXPORT_DIRECTORY)
        if exp == None:
            return None

        dllname = self.ascii( self.ra2off(exp.Name), 32)
        if dllname == None:
            return None

        dllname = dllname.lower()
        if dllname[-4:] in ('.exe','.dll','.sys','.ocx'):
            dllname = dllname[:-4]

        return dllname

    def _getPeExports(self):

        edir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_EXPORT)
        if edir == None:
            return (),()

        exp = self.getStruct(self.ra2off(edir.VirtualAddress), IMAGE_EXPORT_DIRECTORY)
        if exp == None:
            return (),()

        ExpArray32 = varray(exp.NumberOfFunctions,uint32)
        ExpArray16 = varray(exp.NumberOfFunctions,uint16)

        funcs = self.getStruct(self.ra2off(exp.AddressOfFunctions), ExpArray32)
        if funcs == None:
            return (),()

        names = self.getStruct(self.ra2off(exp.AddressOfNames), ExpArray32)
        if names == None:
            return (),()

        ords  = self.getStruct(self.ra2off(exp.AddressOfOrdinals), ExpArray16)
        if ords == None:
            return (),()

        exps = []
        fwds = []

        for i in range(exp.NumberOfFunctions):

            o = int(ords[i])
            ra = int(names[o])
            func = int(funcs[o])

            if ra:
                name = self.ascii(self.ra2off(ra),256)
            else:
                name = 'ord_%.4x' % o

            if v_bits.within(func,edir.VirtualAddress,edir.Size):
                fwdname = self.ascii(self.ra2off(func),256)
                fwds.append( (func,name,fwdname) )
                continue

            exps.append( (func, name, o) )

        return exps,fwds

    def _getBaseAddr(self):
        return self.getInfo('pe:nt').OptionalHeader.ImageBase

    def _getMemoryMaps(self):
        ret = []

        nthdr = self.getInfo('pe:nt')
        major = nthdr.OptionalHeader.MajorSubsystemVersion
        #minor = nthdr.OptionalHeader.MinorSubsystemVersion

        # the PE header gets mapped at off=0/ra=0
        init = self.readAtOff(0,4096,exact=False).ljust(4096,b'\x00')
        ret.append( tufo(0, perm=MM_READ, init=init) )

        for sec in self.getSections():

            hdr = sec[3].get('header')

            ra      = hdr.VirtualAddress
            rsize   = hdr.VirtualSize
            fsize   = hdr.SizeOfRawData

            perm = 0

            ch = hdr.Characteristics
            for scn,scnperm in scnperms:
                if ch & scn:
                    perm |= scnperm

            if major < 6: # FIXME and not resource!
                perm |= MM_EXEC # may not be NX prior to 6

            size = min(rsize,fsize)
            init = self.readAtRa(ra,size).ljust(rsize,b'\x00')
            ret.append( tufo(ra, perm=perm, init=init) )

        return ret

    def _getDosHeader(self):
        doshdr = IMAGE_DOS_HEADER()
        doshdr.vsParse( self.readAtOff(0,len(doshdr)) )
        return doshdr

    def _getNtHeader(self):
        nthdr = IMAGE_NT_HEADERS()

        doshdr = self.getInfo('pe:dos')
        nthdr.vsParse( self.readAtOff( doshdr.e_lfanew, len(nthdr) ) )

        if nthdr.FileHeader.Machine in ( IMAGE_FILE_MACHINE_AMD64, IMAGE_FILE_MACHINE_IA64 ):
            nthdr = IMAGE_NT_HEADERS64()
            nthdr.vsParse( self.readAtOff( doshdr.e_lfanew, len(nthdr) ) )

        return nthdr

    def _getDataDirs(self):
        return [ field for name,field in self.getInfo('pe:nt').OptionalHeader.DataDirectory ]

    def _getArch(self):
        return archmap.get( self.getInfo('pe:nt').FileHeader.Machine )

    def _getFormat(self):
        return 'pe'

    def _getPlatform(self):
        return 'windows'

    def _getByteOrder(self):
        return 'little'

    def _getHighMask(self):
        return v_bits.signbits[ self.getPtrSize() * 8 ]

    def _getPData(self):

        if not self.getArch() == 'amd64':
            return ()

        exdir = self.getPeDataDir(IMAGE_DIRECTORY_ENTRY_EXCEPTION)
        if exdir == None:
            return()

        ra = exdir.VirtualAddress
        size = exdir.Size

        ret = []
        for ra,ent in self.getStructs( self.ra2off(ra) ,size,IMAGE_RUNTIME_FUNCTION_ENTRY):
            unwind = self.getStruct( self.ra2off(ent.UnwindInfoAddress), UNWIND_INFO)
            if unwind == None:
                continue

            # flags version info can only be 1 currently
            if unwind.VerFlags & 0x7 != 1:
                break

            #yield ra,ent,unwind
            ret.append( (ra, ent, unwind) )

        return ret

    @staticmethod
    def isMyFormat(byts):

        dos = IMAGE_DOS_HEADER()
        dos.vsParse(byts)

        if dos.e_magic != b'MZ':
            return False

        lfanew = dos.e_lfanew
        if byts[ lfanew : lfanew + 2 ] != b'PE':
            return False

        return True

v_binfile.addBinFormat('pe',PeBinFile)
