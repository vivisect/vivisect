import os
import struct

from cStringIO import StringIO

import vstruct
import vstruct.defs.pe as vs_pe

import ordlookup

IMAGE_DLLCHARACTERISTICS_RESERVED_1      = 1
IMAGE_DLLCHARACTERISTICS_RESERVED_2      = 2
IMAGE_DLLCHARACTERISTICS_RESERVED_4      = 4
IMAGE_DLLCHARACTERISTICS_RESERVED_8      = 8
IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE    = 0x0040 # The DLL can be relocated at load time.
IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY = 0x0080 # Code integrity checks are forced. If you set this flag and a section contains only uninitialized data, set the PointerToRawData member of IMAGE_SECTION_HEADER for that section to zero; otherwise, the image will fail to load because the digital signature cannot be verified.
IMAGE_DLLCHARACTERISTICS_NX_COMPAT       = 0x0100 # The image is compatible with data execution prevention (DEP).
IMAGE_DLLCHARACTERISTICS_NO_ISOLATION    = 0x0200 # The image is isolation aware, but should not be isolated.
IMAGE_DLLCHARACTERISTICS_NO_SEH          = 0x0400 # The image does not use structured exception handling (SEH). No handlers can be called in this image.
IMAGE_DLLCHARACTERISTICS_NO_BIND         = 0x0800 # Do not bind the image.
IMAGE_DLLCHARACTERISTICS_RESERVED_1000   = 0x1000 # Reserved
IMAGE_DLLCHARACTERISTICS_WDM_DRIVER      = 0x2000 # A WDM driver.
IMAGE_DLLCHARACTERISTICS_RESERVED_4000   = 0x4000 # Reserved
IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE  = 0x8000

IMAGE_SUBSYSTEM_UNKNOWN             = 0 #Unknown subsystem.
IMAGE_SUBSYSTEM_NATIVE              = 1 #No subsystem required (device drivers and native system processes).
IMAGE_SUBSYSTEM_WINDOWS_GUI         = 2 #Windows graphical user interface (GUI) subsystem.
IMAGE_SUBSYSTEM_WINDOWS_CUI         = 3 #Windows character-mode user interface (CUI) subsystem.
IMAGE_SUBSYSTEM_OS2_CUI             = 5 #OS/2 CUI subsystem.
IMAGE_SUBSYSTEM_POSIX_CUI           = 7 #POSIX CUI subsystem.
IMAGE_SUBSYSTEM_WINDOWS_CE_GUI      = 9 #Windows CE system.
IMAGE_SUBSYSTEM_EFI_APPLICATION     = 10 #Extensible Firmware Interface (EFI) application.
IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER     = 11 #EFI driver with boot services.
IMAGE_SUBSYSTEM_EFI_RUNTIME_DRIVER  = 12 #EFI driver with run-time services.
IMAGE_SUBSYSTEM_EFI_ROM             = 13 #EFI ROM image.
IMAGE_SUBSYSTEM_XBOX                = 14 #Xbox system.
IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION    = 16 #Boot application.

IMAGE_FILE_MACHINE_I386  = 0x014c
IMAGE_FILE_MACHINE_IA64  = 0x0200
IMAGE_FILE_MACHINE_AMD64 = 0x8664

machine_names = {
    IMAGE_FILE_MACHINE_I386: 'i386',
    IMAGE_FILE_MACHINE_IA64: 'ia64',
    IMAGE_FILE_MACHINE_AMD64: 'amd64',
}

IMAGE_REL_BASED_ABSOLUTE              = 0
IMAGE_REL_BASED_HIGH                  = 1
IMAGE_REL_BASED_LOW                   = 2
IMAGE_REL_BASED_HIGHLOW               = 3
IMAGE_REL_BASED_HIGHADJ               = 4
IMAGE_REL_BASED_MIPS_JMPADDR          = 5
IMAGE_REL_BASED_IA64_IMM64            = 9
IMAGE_REL_BASED_DIR64                 = 10

IMAGE_DIRECTORY_ENTRY_EXPORT          =0   # Export Directory
IMAGE_DIRECTORY_ENTRY_IMPORT          =1   # Import Directory
IMAGE_DIRECTORY_ENTRY_RESOURCE        =2   # Resource Directory
IMAGE_DIRECTORY_ENTRY_EXCEPTION       =3   # Exception Directory
IMAGE_DIRECTORY_ENTRY_SECURITY        =4   # Security Directory
IMAGE_DIRECTORY_ENTRY_BASERELOC       =5   # Base Relocation Table
IMAGE_DIRECTORY_ENTRY_DEBUG           =6   # Debug Directory
IMAGE_DIRECTORY_ENTRY_COPYRIGHT       =7   # (X86 usage)
IMAGE_DIRECTORY_ENTRY_ARCHITECTURE    =7   # Architecture Specific Data
IMAGE_DIRECTORY_ENTRY_GLOBALPTR       =8   # RVA of GP
IMAGE_DIRECTORY_ENTRY_TLS             =9   # TLS Directory
IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG    =10   # Load Configuration Directory
IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT   =11   # Bound Import Directory in headers
IMAGE_DIRECTORY_ENTRY_IAT            =12   # Import Address Table
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT   =13   # Delay Load Import Descriptors
IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR =14   # COM Runtime descriptor

IMAGE_DEBUG_TYPE_UNKNOWN          =0
IMAGE_DEBUG_TYPE_COFF             =1
IMAGE_DEBUG_TYPE_CODEVIEW         =2
IMAGE_DEBUG_TYPE_FPO              =3
IMAGE_DEBUG_TYPE_MISC             =4
IMAGE_DEBUG_TYPE_EXCEPTION        =5
IMAGE_DEBUG_TYPE_FIXUP            =6
IMAGE_DEBUG_TYPE_OMAP_TO_SRC      =7
IMAGE_DEBUG_TYPE_OMAP_FROM_SRC    =8
IMAGE_DEBUG_TYPE_BORLAND          =9
IMAGE_DEBUG_TYPE_RESERVED10       =10
IMAGE_DEBUG_TYPE_CLSID            =11

IMAGE_SCN_CNT_CODE                  = 0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA      = 0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA    = 0x00000080
IMAGE_SCN_LNK_OTHER                 = 0x00000100
IMAGE_SCN_LNK_INFO                  = 0x00000200
IMAGE_SCN_LNK_REMOVE                = 0x00000800
IMAGE_SCN_LNK_COMDAT                = 0x00001000
IMAGE_SCN_MEM_FARDATA               = 0x00008000
IMAGE_SCN_MEM_PURGEABLE             = 0x00020000
IMAGE_SCN_MEM_16BIT                 = 0x00020000
IMAGE_SCN_MEM_LOCKED                = 0x00040000
IMAGE_SCN_MEM_PRELOAD               = 0x00080000
IMAGE_SCN_ALIGN_1BYTES              = 0x00100000
IMAGE_SCN_ALIGN_2BYTES              = 0x00200000
IMAGE_SCN_ALIGN_4BYTES              = 0x00300000
IMAGE_SCN_ALIGN_8BYTES              = 0x00400000
IMAGE_SCN_ALIGN_16BYTES             = 0x00500000
IMAGE_SCN_ALIGN_32BYTES             = 0x00600000
IMAGE_SCN_ALIGN_64BYTES             = 0x00700000
IMAGE_SCN_ALIGN_128BYTES            = 0x00800000
IMAGE_SCN_ALIGN_256BYTES            = 0x00900000
IMAGE_SCN_ALIGN_512BYTES            = 0x00A00000
IMAGE_SCN_ALIGN_1024BYTES           = 0x00B00000
IMAGE_SCN_ALIGN_2048BYTES           = 0x00C00000
IMAGE_SCN_ALIGN_4096BYTES           = 0x00D00000
IMAGE_SCN_ALIGN_8192BYTES           = 0x00E00000
IMAGE_SCN_ALIGN_MASK                = 0x00F00000
IMAGE_SCN_LNK_NRELOC_OVFL           = 0x01000000
IMAGE_SCN_MEM_DISCARDABLE           = 0x02000000
IMAGE_SCN_MEM_NOT_CACHED            = 0x04000000
IMAGE_SCN_MEM_NOT_PAGED             = 0x08000000
IMAGE_SCN_MEM_SHARED                = 0x10000000
IMAGE_SCN_MEM_EXECUTE               = 0x20000000
IMAGE_SCN_MEM_READ                  = 0x40000000
IMAGE_SCN_MEM_WRITE                 = 0x80000000

# Flags for the UNWIND_INFO flags field from
# RUNTIME_FUNCTION defs
UNW_FLAG_NHANDLER   = 0x0
UNW_FLAG_EHANDLER   = 0x1
UNW_FLAG_UHANDLER   = 0x2
UNW_FLAG_CHAININFO  = 0x4

# Resource Types
RT_CURSOR           = 1
RT_BITMAP           = 2
RT_ICON             = 3
RT_MENU             = 4
RT_DIALOG           = 5
RT_STRING           = 6
RT_FONTDIR          = 7
RT_FONT             = 8
RT_ACCELERATOR      = 9
RT_RCDATA           = 10
RT_MESSAGETABLE     = 11
RT_GROUP_CURSOR     = 12
RT_GROUP_ICON       = 14
RT_VERSION          = 16
RT_DLGINCLUDE       = 17
RT_PLUGPLAY         = 19
RT_VXD              = 20
RT_ANICURSOR        = 21
RT_ANIICON          = 22
RT_HTML             = 23
RT_MANIFEST         = 24

class VS_VERSIONINFO:
    '''
    A simple (read-only) VS_VERSIONINFO parser
    '''
    def __init__(self, bytes):
        self._version_info = {}
        self._parseBytes(bytes)

    def getVersionValue(self, key, default=None):
        '''
        Retrieve a key from the VS_VERSIONINFO data.

        Example: vs.getVersionValue('FileVersion')
        '''
        return self._version_info.get(key, default)

    def getVersionKeys(self):
        '''
        Return a list of the keys in this VS_VERSIONINFO struct.

        Example: for keyname in vs.getVersionKeys(): print keyname
        '''
        return self._version_info.keys()

    def getVersionItems(self):
        '''
        Return dictionary style key,val tuples for the version keys
        in this VS_VERSIONINFO structure.

        Example: for vskey,vsdata in vs.getVersionItems(): print vskey,vsdata
        '''
        return self._version_info.items()

    def _parseBytes(self, bytes):
        offset = 0
        mysize, valsize, vstype = struct.unpack('<HHH', bytes[:6])
        offset += 6
        offset, vinfosig = self._eatStringAndAlign(bytes, offset)
        if vinfosig != 'VS_VERSION_INFO':
            Exception('Invalid VS_VERSION_INFO signature!: %s' % repr(vinfosig))

        if valsize and valsize >= len(vs_pe.VS_FIXEDFILEINFO()):
            ffinfo = vs_pe.VS_FIXEDFILEINFO()
            ffinfo.vsParse(bytes[offset:offset+valsize])

        offset += valsize
        offmod = offset % 4
        if offmod:
            offset += (4 - offmod)

        xmax = min(mysize, len(bytes))
        i = 0
        while offset < xmax and i < 2:
            offset = self._stringFileInfo(bytes, offset)
            i += 1

    def _eatStringAndAlign(self, bytes, offset):
        ret = ''
        blen = len(bytes)
        while bytes[offset:offset+2] != '\x00\x00':
            ret += bytes[offset:offset+2]
            offset += 2
            if offset >= blen:
                break
        # Add 2 for the null terminator
        offset += 2
        offmod = offset % 4
        if offmod:
            offset += (4 - offmod)
        return offset, ret.decode('utf-16le')

    def _stringFileInfo(self, bytes, offset):
        xoffset = offset
        mysize, valsize, valtype = struct.unpack('<HHH', bytes[xoffset:xoffset+6])
        xoffset += 6
        xoffset, sigstr = self._eatStringAndAlign(bytes, xoffset)
        #if sigstr not in ('VarFileInfo','StringFileInfo'):
            #raise Exception('Invalid StringFileInfo Key!: %s' % repr(sigstr))

        xmax = offset + mysize

        if sigstr == 'StringFileInfo':
            while xoffset < xmax:
                xoffset = self._stringTable(bytes, xoffset, mysize - (xoffset-offset))

        elif sigstr == 'VarFileInfo':
            while xoffset < xmax:
                xoffset = self._varTable(bytes, xoffset, mysize - (xoffset-offset))

        xmod = xoffset % 4
        if xmod:
            xoffset += (4 - xmod)

        return xoffset

    def _varTable(self, bytes, offset, size):
        xmax = offset + size
        xoffset = offset
        mysize, valsize, valtype = struct.unpack('<HHH', bytes[xoffset:xoffset+6])
        xoffset += 6
        xoffset, varname = self._eatStringAndAlign(bytes, xoffset)
        if xoffset + 4 > len(bytes):
            return offset+size
        varval = struct.unpack('<I', bytes[xoffset:xoffset+4])[0]
        xoffset += 4
        self._version_info[varname] = varval
        return offset + size

    def _stringTable(self, bytes, offset, size):
        xmax = offset + size
        xoffset = offset
        mysize, valsize, valtype = struct.unpack('<HHH', bytes[offset:offset+6])
        xoffset += 6
        xoffset, hexcpage = self._eatStringAndAlign(bytes, xoffset)
        while xoffset < xmax:
            xoffset = self._stringData(bytes, xoffset)
            if xoffset == -1:
                break

            xmod = xoffset % 4
            if xmod:
                xoffset += (4 - xmod)
        return offset + size

    def _stringData(self, bytes, offset):
        '''
        Parse out a "String" structure...
        '''
        xoffset = offset
        mysize, valsize, stype = struct.unpack('<HHH', bytes[offset:offset+6])

        if mysize == 0:
            return -1 

        xoffset += 6
        xoffset, strkey = self._eatStringAndAlign(bytes, xoffset)

        # valsize is in words...
        valsize *= 2
        value = bytes[xoffset : xoffset + valsize ]

        # Do utf16le decode if we're "textual data"
        if stype == 1:
            value = value.decode('utf-16le','ignore')
            value = value.split('\x00')[0]

        #print 'VALSIZE',valsize,'MYSIZE',mysize
        #print 'Key: ->%s<-, ->%s<-' % (strkey,repr(value))
        self._version_info[strkey] = value

        # No matter what we parse, believe the headers...
        return offset + mysize

class ResourceDirectory:
    '''
    Resources are sorted into a hierarchy which begins with
    "type" and then "name/id" which still points to another
    directory entry which has 1 child (id 1033) with data.
    '''
    def __init__(self, nameid=None):
        self._rsrc_data = []
        self._rsrc_nameid = nameid
        self._rsrc_subdirs = {}

    def addRsrcDirectory(self, nameid):
        r = ResourceDirectory(nameid=nameid)
        self._rsrc_subdirs[nameid] = r
        return r

    def addRsrcData(self, rva, size, langinfo):
        self._rsrc_data.append( (rva, size, langinfo) )

    def getDirById(self, name_id):
        return self._rsrc_subdirs.get(name_id)

    def getResourceDef(self, restype, name_id):
        '''
        This should *only* be called on the root node!
        '''
        typedir = self._rsrc_subdirs.get(restype)
        if typedir == None:
            return None

        datadir = typedir._rsrc_subdirs.get(name_id)
        if datadir == None:
            return None

        if len(datadir._rsrc_data) == 0:
            return None

        # The first entry in the datadir's data is the one
        return datadir._rsrc_data[0]

    def getDataEntries(self):
        return self._rsrc_data

class PE(object):

    def __init__(self, fd, inmem=False):
        """
        Construct a PE object.  use inmem=True if you are
        using a MemObjFile or other "memory like" image.
        """
        object.__init__(self)
        self.inmem = inmem
        self.filesize = None

        if not inmem:
            fd.seek(0, os.SEEK_END)
            self.filesize = fd.tell()
            fd.seek(0)

        self.fd = fd

        self.pe32p = False
        self.psize = 4
        self.high_bit_mask = 0x80000000

        self.IMAGE_DOS_HEADER = vstruct.getStructure("pe.IMAGE_DOS_HEADER")
        dosbytes = self.readAtOffset(0, len(self.IMAGE_DOS_HEADER))
        self.IMAGE_DOS_HEADER.vsParse(dosbytes)

        nt = self.readStructAtOffset(self.IMAGE_DOS_HEADER.e_lfanew,
                                "pe.IMAGE_NT_HEADERS")

        # Parse in a default 32 bit, and then check for 64...
        if nt.FileHeader.Machine in [ IMAGE_FILE_MACHINE_AMD64, IMAGE_FILE_MACHINE_IA64 ]:
            nt = self.readStructAtOffset(self.IMAGE_DOS_HEADER.e_lfanew,
                                "pe.IMAGE_NT_HEADERS64")
            self.pe32p = True
            self.psize = 8
            self.high_bit_mask = 0x8000000000000000

        self.IMAGE_NT_HEADERS = nt

    def getPdataEntries(self):
        sec = self.getSectionByName('.pdata')
        if sec == None:
            return ()
        ret = []
        rbytes = self.readAtRva(sec.VirtualAddress, sec.VirtualSize)
        while len(rbytes):
            f = vs_pe.IMAGE_RUNTIME_FUNCTION_ENTRY()
            f.vsParse(rbytes)
            rbytes = rbytes[len(f):]
            ret.append(f)
        return ret

    def getDllName(self):
        '''
        Return the "dll name" from the Name field of the IMAGE_EXPORT_DIRECTORY
        if one is present.  If not, return None.
        '''
        if self.IMAGE_EXPORT_DIRECTORY != None:
            rawname = self.readAtRva(self.IMAGE_EXPORT_DIRECTORY.Name, 32)
            return rawname.split('\x00')[0]
        return None

    def getImports(self):
        """
        Return the list of import tuples for this PE.  The tuples
        are in the format (rva, libname, funcname).
        """
        return self.imports

    def getExports(self):

        """
        Return the list of exports in this PE.  The list contains
        tuples in the format; (rva, ord, name).
        """
        return self.exports

    def getForwarders(self):
        """
        [ (rva, name, forwardname), ... ]
        """
        return self.forwarders

    def getSections(self):
        return self.sections
         
    def rvaToOffset(self, rva):
        if self.inmem:
            return rva
        for s in self.sections:
            sbase = s.VirtualAddress
            ssize = max(s.SizeOfRawData, s.VirtualSize)
            if rva >= sbase and rva < sbase+ssize:
                return s.PointerToRawData + (rva - sbase)
        return 0

    def offsetToRva(self, offset):
        if self.inmem:
            return offset 

        for s in self.sections:
            sbase = s.PointerToRawData
            ssize = s.SizeOfRawData
            if sbase <= offset and offset < sbase + ssize:
                return offset - s.PointerToRawData + s.VirtualAddress
        return 0



    def getSectionByName(self, name):
        for s in self.getSections():
            if s.Name.split("\x00", 1)[0] == name:
                return s
        return None

    def readStructAtRva(self, rva, structname, check=False):
        s = vstruct.getStructure(structname)
        slen = len(s)
        if check and not self.checkRva(rva, size=slen):
            return None
        bytes = self.readAtRva(rva, len(s))
        if not bytes:
            return None

        s.vsParse(bytes)
        return s

    def readStructAtOffset(self, offset, structname):
        s = vstruct.getStructure(structname)
        sbytes = self.readAtOffset(offset, len(s))
        if not sbytes:
            return None

        s.vsParse(sbytes)
        return s

    def getDataDirectory(self, idx):
        return self.IMAGE_NT_HEADERS.OptionalHeader.DataDirectory[idx]

    def getResourceDef(self, rtype, name_id):
        '''
        Get the (rva, size, (codepage,langid,sublangid)) tuple for the specified
        resource type/id combination.  Returns None if not found.
        '''
        return self.ResourceRoot.getResourceDef(rtype, name_id)

    def getResources(self):
        '''
        Get the (rtype, nameid, (rva, size, (codepage,langid,sublangid))) tuples for each
        resource in the PE.
        '''
        ret = []
        for rtype,subdir in self.ResourceRoot._rsrc_subdirs.items():
            for nameid, subsubdir in subdir._rsrc_subdirs.items():
                ret.append( (rtype, nameid, subsubdir._rsrc_data[0]) )
        return ret

    def readResource(self, rtype, name_id):
        '''
        Return the bytes which define the specified resource.  Returns
        None if not found.
        '''
        rsdef = self.getResourceDef(rtype, name_id)
        if rsdef == None:
            return None
        rsrva, rssize, rscpage = rsdef
        return self.readAtRva(rsrva, rssize)

    def getPdbPath(self):
        '''
        Parse and return the Pdb path from the Code View 4.0 data
        specified by the IMAGE_DEBUG_DIRECTORY strucutre, or None
        if a pdb path is not present.
        '''
        ddir = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_DEBUG)
        drva = ddir.VirtualAddress
        dsize = ddir.Size
        d = self.readStructAtRva(drva, 'pe.IMAGE_DEBUG_DIRECTORY', check=True)
        if d == None:
            return None

        if d.Type != IMAGE_DEBUG_TYPE_CODEVIEW:
            return None

        if not self.checkRva(d.AddressOfRawData, size=d.SizeOfData):
            return None

        cv = vs_pe.CV_INFO_PDB70()
        cv.vsParse( self.readAtRva(d.AddressOfRawData, d.SizeOfData))
        if cv.CvSignature != 0x53445352:
            return None

        return cv.PdbFileName

    def getVS_VERSIONINFO(self):
        '''
        Get a VS_VERSIONINFO object for this PE.
        (returns None if version resource is not found)
        '''
        vbytes = self.readResource(RT_VERSION, 1)
        if vbytes == None:
            return None
        return VS_VERSIONINFO(vbytes)

    def parseResources(self):

        self.ResourceRoot = ResourceDirectory()

        # RP BUG FIX - Binaries can have a .rsrc section it doesn't mean that the .rsrc section contains the resource data we think it does
        # validate .rsrc == RESOURCE Section by checking data directory entries...
        dresc = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_RESOURCE)
        if not dresc.VirtualAddress:
            return

        done = {}
        rsrc_todo = [ (dresc.VirtualAddress, self.ResourceRoot), ]

        while len(rsrc_todo):
            rsrva, rsdirobj = rsrc_todo.pop()
            rsdir = self.readStructAtRva( rsrva, 'pe.IMAGE_RESOURCE_DIRECTORY', check=True )
            if rsdir == None:
                continue

            totcount = rsdir.NumberOfIdEntries + rsdir.NumberOfNamedEntries
            # check if our to do is too many, limit borrowed from pefile
            if totcount > 4096:
                continue
            
            offset = len(rsdir)
            for i in xrange(totcount):
                dentrva = rsrva + offset

                dirent = self.readStructAtRva( dentrva, 'pe.IMAGE_RESOURCE_DIRECTORY_ENTRY', check=True )
                if dirent == None:
                    break

                # We use name/id interchangably in the python dict...
                name_id = None
                if dirent.Name & 0x80000000: # If high bit is set, it's a string!
                    namerva = dresc.VirtualAddress + (dirent.Name & 0x7fffffff)
                    namelen_bytes = self.readAtRva(namerva, 2)
                    if not namelen_bytes:
                        continue
                    namelen = struct.unpack('<H', namelen_bytes)[0]
                    name_id = self.readAtRva(namerva + 2, namelen * 2).decode('utf-16le', 'ignore')
                    if not name_id:
                        name_id = dirent.Name

                else:
                    name_id = dirent.Name
                
                # if OffsetToData & IMAGE_RESOURCE_DATA_IS_DIRECTORY then we have another directory
                if dirent.OffsetToData & 0x80000000:
                    # This points to a subdirectory
                    subdir = rsdirobj.addRsrcDirectory(name_id)
                    doffset = dirent.OffsetToData & 0x7fffffff
                    drva = dresc.VirtualAddress + doffset
                    # XXX - prevent infinite loop by making sure the RVA isnt in our list to visit
                    # and we aren't currently examining it.
                    if doffset and rsrva !=  drva and not done.get(drva):
                        rsrc_todo.append( (drva, subdir) )
                        done[drva] = 1

                else:
                    subdata = self.readStructAtRva( dresc.VirtualAddress + dirent.OffsetToData, 'pe.IMAGE_RESOURCE_DATA_ENTRY')
                    # RP BUG FIX - sanity check the subdata
                    if subdata and self.checkRva(subdata.OffsetToData, size=subdata.Size):
                        langid = name_id & 0x3ff
                        sublangid = name_id >> 10
                        langinfo = (subdata.CodePage, langid, sublangid )
                        rsdirobj.addRsrcData(subdata.OffsetToData, subdata.Size, langinfo )

                    #print 'Data %s : 0x%.8x (%d)' % (name_id, sec.VirtualAddress + subdata.OffsetToData, subdata.Size)
                    #print repr(self.readAtRva(subdata.OffsetToData, min(subdata.Size, 40) ))

                offset += len(dirent)
                #print dirent.tree()

    def parseSections(self):

        self.sections = []
        off = self.IMAGE_DOS_HEADER.e_lfanew + len(self.IMAGE_NT_HEADERS)

        secsize = len(vstruct.getStructure("pe.IMAGE_SECTION_HEADER"))

        sbytes = self.readAtOffset(off, secsize * self.IMAGE_NT_HEADERS.FileHeader.NumberOfSections)
        while sbytes:
            s = vstruct.getStructure("pe.IMAGE_SECTION_HEADER")
            s.vsParse(sbytes[:secsize])
            self.sections.append(s)
            sbytes = sbytes[secsize:]

    def readRvaFormat(self, fmt, rva):
        size = struct.calcsize(fmt)
        fbytes = self.readAtRva(rva, size)
        return struct.unpack(fmt, fbytes)

    def readAtRva(self, rva, size, shortok=False):
        offset = self.rvaToOffset(rva)
        return self.readAtOffset(offset, size, shortok)

    def readAtOffset(self, offset, size, shortok=False):
        ret = ""
        self.fd.seek(offset)
        while len(ret) != size:
            rlen = size - len(ret)
            x = self.fd.read(rlen)
            if x == "":
                if not shortok:
                    return None
                return ret
            ret += x
        return ret

    def parseLoadConfig(self):
        self.IMAGE_LOAD_CONFIG = None
        cdir = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG)
        rva = cdir.VirtualAddress
        # RP BUG FIX - validate config directory
        if self.checkRva(rva, size=cdir.Size):
            self.IMAGE_LOAD_CONFIG = self.readStructAtRva(rva, "pe.IMAGE_LOAD_CONFIG_DIRECTORY")

    def readPointerAtOffset(self, off):
        fmt = "<L"
        if self.psize == 8:
            fmt = "<Q"
        return struct.unpack(fmt, self.readAtOffset(off, self.psize))[0]

    def readPointerAtRva(self, rva):
        off = self.rvaToOffset(rva)
        return self.readPointerAtOffset(off)

    def getMaxRva(self):
        return self.IMAGE_NT_HEADERS.OptionalHeader.SizeOfImage

    def checkRva(self, rva, size=None):
        '''
        Make sure an RVA falls inside the valid mapped range
        for the file.  (also make sure it's not 0...)
        '''
        if rva == 0:
            return False

        isize = self.getMaxRva()

        if rva > isize:
            #raise Exception('too high! %d > %d' % (rva, isize))
            return False

        if size != None and (rva + size) > isize:
            #raise Exception('too big! %d > %d' % (rva+size, isize))
            return False
        
        return True

    def readStringAtRva(self, rva, maxsize=None):
        ret = ''
        while True:
            if maxsize and maxsize <= len(ret):
                break
            x = self.readAtRva(rva, 1)
            if x == '\x00' or x == None:
                break
            ret += x
            rva += 1
        return ret
        
    def parseImports(self):
        self.imports = []

        idir = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_IMPORT)

        # RP BUG FIX - invalid IAT entry will point of range of file
        irva = idir.VirtualAddress
        x = self.readStructAtRva(irva, 'pe.IMAGE_IMPORT_DIRECTORY', check=True)
        if x == None:
            return

        isize = len(x)
        
        while self.checkRva(x.Name):

            # RP BUG FIX - we can't assume that we have 256 bytes to read
            libname = self.readStringAtRva(x.Name, maxsize=256)
            idx = 0

            imp_by_name = x.OriginalFirstThunk
            if imp_by_name == 0:
                imp_by_name = x.FirstThunk

            if not self.checkRva(imp_by_name):
                break
                
            while True:

                arrayoff = self.psize * idx
                if self.filesize != None and arrayoff > self.filesize:
                    self.imports = [] # we probably put grabage in  here..
                    return

                ibn_rva = self.readPointerAtRva(imp_by_name+arrayoff)
                if ibn_rva == 0:
                    break

                if ibn_rva & self.high_bit_mask:
                    funcname = ordlookup.ordLookup(libname, ibn_rva & 0x7fffffff)

                else:
                    # RP BUG FIX - we can't use this API on this call because we can have binaries that put their import table
                    # right at the end of the file, statically saying the imported function name is 128 will cause use to potentially
                    # over run our read and traceback...

                    diff = self.getMaxRva() - ibn_rva - 2
                    ibn = vstruct.getStructure("pe.IMAGE_IMPORT_BY_NAME")
                    ibn.vsGetField('Name').vsSetLength( min(diff, 128) )
                    bytes = self.readAtRva(ibn_rva, len(ibn), shortok=True)
                    if not bytes:
                        break
                    try: 
                        ibn.vsParse(bytes)
                    except:
                        idx+=1
                        continue

                    funcname = ibn.Name

                self.imports.append((x.FirstThunk+arrayoff,libname,funcname))

                idx += 1
                
            irva += isize

            # RP BUG FIX - if the import table is at the end of the file we can't count on the ending to be null
            if not self.checkRva(irva, size=isize):
                break

            x.vsParse(self.readAtRva(irva, isize))

    def getRelocations(self):
        """
        Return the list of RVA base-relocations in this PE.
        """
        return self.relocations

    def parseRelocations(self):
        self.relocations = []
        edir = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_BASERELOC)
        rva = edir.VirtualAddress
        rsize = edir.Size
        
        # RP BUG FIX - don't watn to read past the end of the file
        if not self.checkRva(rva):
            return
        
        reloff = self.rvaToOffset(rva)
        relbytes = self.readAtOffset(reloff, rsize)
        

        while relbytes:
            pageva, chunksize = struct.unpack("<LL", relbytes[:8])
            relcnt = (chunksize - 8) / 2
            
            # RP BUG FIX - when the reloc section has no fixups but the directory exists..
            if not chunksize or not pageva:
                return
            # RP BUG FIX - sometimes the chunksize is invalid we do a quick check to make sure we dont overrun the buffer
            if chunksize > len(relbytes):
                return
            
            
            rels = struct.unpack("<%dH" % relcnt, relbytes[8:chunksize])
            for r in rels:
                rtype = r >> 12
                roff  = r & 0xfff
                self.relocations.append((pageva+roff, rtype))
            relbytes = relbytes[chunksize:]

    def getExportName(self):
        '''
        Return the name of this file acording to it's export entry.
        (if there are no exports, return None)

        '''
        e = self.IMAGE_EXPORT_DIRECTORY
        if e == None:
            return None

        return self.readAtRva(e.Name, 128).split('\x00')[0]

    def parseExports(self):

        # Initialize our required locals.
        self.exports = []
        self.forwarders = []
        self.IMAGE_EXPORT_DIRECTORY = None

        edir = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_EXPORT)
        poff = self.rvaToOffset(edir.VirtualAddress)

        if poff == 0: # No exports...
            return

        self.IMAGE_EXPORT_DIRECTORY = self.readStructAtOffset(poff, "pe.IMAGE_EXPORT_DIRECTORY")
        if not self.IMAGE_EXPORT_DIRECTORY:
            return

        funcoff = self.rvaToOffset(self.IMAGE_EXPORT_DIRECTORY.AddressOfFunctions)
        funcsize = 4 * self.IMAGE_EXPORT_DIRECTORY.NumberOfFunctions
        nameoff = self.rvaToOffset(self.IMAGE_EXPORT_DIRECTORY.AddressOfNames)
        namesize = 4 * self.IMAGE_EXPORT_DIRECTORY.NumberOfNames
        ordoff = self.rvaToOffset(self.IMAGE_EXPORT_DIRECTORY.AddressOfOrdinals)
        ordsize = 2 * self.IMAGE_EXPORT_DIRECTORY.NumberOfNames
        
        
        # RP BUG FIX - sanity check the exports before reading
        if not funcoff or not ordoff and not nameoff or funcsize > 0x7FFF:
            self.IMAGE_EXPORT_DIRECTORY = None
            return
    
        funcbytes = self.readAtOffset(funcoff, funcsize)

        namebytes = self.readAtOffset(nameoff, namesize)

        ordbytes = self.readAtOffset(ordoff, ordsize)

        funclist = struct.unpack("%dI" % (len(funcbytes) / 4), funcbytes)
        namelist = struct.unpack("%dI" % (len(namebytes) / 4), namebytes)
        ordlist = struct.unpack("%dH" % (len(ordbytes) / 2), ordbytes)

        #for i in range(len(funclist)):
        for i in range(len(namelist)):

            ord = ordlist[i]
            nameoff = self.rvaToOffset(namelist[i])
            if ord > len(funclist):
                self.IMAGE_EXPORT_DIRECTORY = None
                return

            funcoff = funclist[ord]
            ffoff = self.rvaToOffset(funcoff)

            name = None

            if nameoff != 0:
                name = self.readAtOffset(nameoff, 256, shortok=True).split("\x00", 1)[0]
            else:
                name = "ord_%.4x" % ord

            # RP BUG FIX - Export forwarding range check is done using RVA's 
            if funcoff >= edir.VirtualAddress and funcoff < edir.VirtualAddress + edir.Size:
                fwdname = self.readAtRva(funcoff, 260, shortok=True).split("\x00", 1)[0]
                self.forwarders.append((funclist[ord],name,fwdname))
            else:
                self.exports.append((funclist[ord], ord, name))

    def getSignature(self):
        '''
        Returns the SignatureEntry vstruct if the pe has an embedded
        certificate, None if the magic bytes are NOT set in the security
        directory entry AND the size of the signature entry is less than 0.
        '''
        ds = self.getDataDirectory(IMAGE_DIRECTORY_ENTRY_SECURITY)

        va = ds.VirtualAddress
        size = ds.Size
        if size <= 0:
            return None

        bytez = self.readAtOffset(va, size)
        if not bytez:
            return None

        se = vstruct.getStructure('pe.SignatureEntry')
        se.vsParse(bytez)

        if se.magic != "\x00\x02\x02\x00":
            return None

        return se

    def getSignCertInfo(self):

        sig = self.getSignature()

        if sig == None:
            return ()

        # Runtime import these so they are optional dependancies
        import pyasn1.type.univ
        import pyasn1.type.namedtype
        import pyasn1.codec.der.decoder
        import pyasn1.codec.der.encoder
        import pyasn1_modules.rfc2315

        substrate = sig.pkcs7
        contentInfo, rest = pyasn1.codec.der.decoder.decode(substrate, asn1Spec=pyasn1_modules.rfc2315.ContentInfo())

        if rest: substrate = substrate[:-len(rest)]

        contentType = contentInfo.getComponentByName('contentType')

        contentInfoMap = {
            (1, 2, 840, 113549, 1, 7, 1): pyasn1_modules.rfc2315.Data(),
            (1, 2, 840, 113549, 1, 7, 2): pyasn1_modules.rfc2315.SignedData(),
            (1, 2, 840, 113549, 1, 7, 3): pyasn1_modules.rfc2315.EnvelopedData(),
            (1, 2, 840, 113549, 1, 7, 4): pyasn1_modules.rfc2315.SignedAndEnvelopedData(),
            (1, 2, 840, 113549, 1, 7, 5): pyasn1_modules.rfc2315.DigestedData(),
            (1, 2, 840, 113549, 1, 7, 6): pyasn1_modules.rfc2315.EncryptedData()
            }

        seqTypeMap = {

            (2,5,4,3):          'CN',
            (2,5,4,7):          'L',
            (2,5,4,10):         'O',
            (2,5,4,11):         'OU',
            (1,2,840,113549,1,9,1): 'E',
            (2,5,4,6):          'C',
            (2,5,4,8):          'ST',
            (2,5,4,9):          'STREET',
            (2,5,4,12):         'TITLE',
            (2,5,4,42):         'G',
            (2,5,4,43):         'I',
            (2,5,4,4):          'SN',
            (0,9,2342,19200300,100,1,25):   'DC',
        }

        content, _ = pyasn1.codec.der.decoder.decode(
            contentInfo.getComponentByName('content'),
            asn1Spec=contentInfoMap[contentType]
            )

        a = content.getComponentByName('certificates')

        certs = []
        for i in a:

            cbytes = pyasn1.codec.der.encoder.encode( i['certificate'] )

            iparts = []
            for rdnsequence in i["certificate"]["tbsCertificate"]["issuer"]:
                for rdn in rdnsequence:
                    rtype = rdn[0]["type"]
                    rvalue = rdn[0]["value"][2:]
                    iparts.append('%s=%s' % ( seqTypeMap.get( rtype, 'UNK'), rvalue))

            issuer = ','.join( iparts )

            sparts = []
            for rdnsequence in i["certificate"]["tbsCertificate"]["subject"]:
                for rdn in rdnsequence:
                    rtype = rdn[0]["type"]
                    rvalue = rdn[0]["value"][2:]
                    sparts.append('%s=%s' % ( seqTypeMap.get( rtype, 'UNK'), rvalue))

            subject = ','.join(sparts)

            serial = int(i["certificate"]["tbsCertificate"]["serialNumber"])

            cert = { 'subject':subject, 'issuer':issuer, 'serial':serial, 'bytes':cbytes }
            certs.append( cert )

        return certs

    def __getattr__(self, name):
        """
        Use a getattr over-ride to allow "on demand" parsing of particular sections.
        """
        if name == "exports":
            self.parseExports()
            return self.exports

        elif name == "IMAGE_IMPORT_DIRECTORY":
            self.parseImports()
            return self.IMAGE_IMPORT_DIRECTORY

        elif name == "imports":
            self.parseImports()
            return self.imports

        elif name == "IMAGE_EXPORT_DIRECTORY":
            self.parseExports()
            return self.IMAGE_EXPORT_DIRECTORY

        elif name == "forwarders":
            self.parseExports()
            return self.forwarders

        elif name == "sections":
            self.parseSections()
            return self.sections

        elif name == "ResourceRoot":
            self.parseResources()
            return self.ResourceRoot

        elif name == "relocations":
            self.parseRelocations()
            return self.relocations

        elif name == "IMAGE_LOAD_CONFIG":
            self.parseLoadConfig()
            return self.IMAGE_LOAD_CONFIG

        else:
            raise AttributeError


class MemObjFile:
    """
    A file like object that wraps a MemoryObject (envi) compatable
    object with a file-like object where seek == VA.
    """

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

def peFromMemoryObject(memobj, baseaddr):
    fd = MemObjFile(memobj, baseaddr)
    return PE(fd, inmem=True)

def peFromFileName(fname):
    """
    Utility helper that assures that the file is opened in 
    binary mode which is required for proper functioning.
    """
    f = file(fname, "rb")
    return PE(f)

def peFromBytes(fbytes):
    fd = StringIO(fbytes)
    return PE(fd)

