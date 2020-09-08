'''
Some utilities for dealing with COFF .LIB files
'''

import binascii

import vstruct
from vstruct.defs.pe import *
from vstruct.primitives import *

IMAGE_ARCHIVE_START_SIZE             = 8
IMAGE_ARCHIVE_START                  = '!<arch>\n'
IMAGE_ARCHIVE_END                    = '`\n'
IMAGE_ARCHIVE_PAD                    = '\n'
IMAGE_ARCHIVE_LINKER_MEMBER          = '/               '
IMAGE_ARCHIVE_LONGNAMES_MEMBER       = '//              '

IMAGE_ARCHIVE_HEADER_SIZE           = 60

class IMAGE_ARCHIVE_MEMBER_HEADER(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Name       = v_str(size=16)
        self.Date       = v_str(size=12)
        self.UserID     = v_str(size=6)
        self.GroupID    = v_str(size=6)
        self.Mode       = v_str(size=8)
        self.Size       = v_str(size=10)
        self.EndHeader  = v_str(size=2)
        self.FileData   = vstruct.VStruct()

class IMAGE_ARCHIVE_MEMBER(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MemberHeader = IMAGE_ARCHIVE_MEMBER_HEADER()

    def vsParse(self, bytes, offset=0):
        off = vstruct.VStruct.vsParse(self, bytes, offset=offset)

        # Use the size that the header says we are...
        offset = offset + len(self.MemberHeader) + int( self.MemberHeader.Size )

        # two byte aligned
        if offset % 2:
            offset += 1

        return offset

class IMAGE_ARCHIVE_LINKER1(IMAGE_ARCHIVE_MEMBER):

    def __init__(self):
        IMAGE_ARCHIVE_MEMBER.__init__(self)
        self.NumberOfSymbols = v_uint32(bigend=True)
        self.SymbolOffsets = vstruct.VArray()
        self.SymbolNames = vstruct.VArray()

    def pcb_NumberOfSymbols(self):
        c = self.NumberOfSymbols
        self.SymbolOffsets = vstruct.VArray( elems=[ v_uint32(bigend=True) for i in range(c) ])
        self.SymbolNames = vstruct.VArray( elems=[ v_zstr() for i in range(c) ])

class IMAGE_ARCHIVE_LINKER2(IMAGE_ARCHIVE_MEMBER):

    def __init__(self):
        IMAGE_ARCHIVE_MEMBER.__init__(self)
        self.NumberOfMembers = v_uint32()
        self.MemberOffsets = vstruct.VArray()
        self.NumberOfSymbols = v_uint32()
        self.SymbolIndexes = vstruct.VArray()
        self.SymbolNames = vstruct.VArray()

    def pcb_NumberOfMembers(self):
        c = self.NumberOfMembers
        self.MemberOffsets = vstruct.VArray( elems=[ v_uint32() for i in range(c) ] )

    def pcb_NumberOfSymbols(self):
        c = self.NumberOfSymbols
        self.SymbolIndexes = vstruct.VArray( elems=[ v_uint16() for i in range(c) ])
        self.SymbolNames = vstruct.VArray( elems=[ v_zstr() for i in range(c) ])

IMPORT_SIG      = binascii.unhexlify('0000ffff')
IMPORT_CODE     = 0 # Executable code.
IMPORT_DATA     = 1 # Data.
IMPORT_CONST    = 2 # Specified as CONST in the .def file.

class IMAGE_ARCHIVE_IMPORT(IMAGE_ARCHIVE_MEMBER):

    def __init__(self):
        IMAGE_ARCHIVE_MEMBER.__init__(self)
        self.Sig1           = v_uint16()
        self.Sig2           = v_uint16()
        self.Version        = v_uint16()
        self.Machine        = v_uint16()
        self.DateTimeStamp  = v_uint32()
        self.SizeOfData     = v_uint32()
        self.Ordinal        = v_uint16()
        self.ImportFlags    = v_uint16()
        self.ImportName     = v_zstr()
        self.ImportLibName  = v_zstr()

class IMAGE_COFF_SYMBOL(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.u                  = vstruct.VUnion()
        self.u.Name             = v_str(size=8)
        self.u.lname            = vstruct.VStruct()
        self.u.lname.Zeros      = v_uint32()
        self.u.lname.Offset     = v_uint32()

        self.Value              = v_uint32()
        self.SectionNumber      = v_uint16()
        self.Type               = v_uint16()
        self.StorageClass       = v_uint8()
        self.NumberOfAuxSymbols = v_uint8()
        self.AuxSymbols         = vstruct.VArray()

    def pcb_NumberOfAuxSymbols(self):
        a = self.NumberOfAuxSymbols
        self.AuxSymbols = vstruct.VArray(elems=[ v_bytes(size=18) for i in range(a) ])

class IMAGE_ARCHIVE_COFF(IMAGE_ARCHIVE_MEMBER):

    def __init__(self, bigend=False):
        IMAGE_ARCHIVE_MEMBER.__init__(self)
        self.FileHeader = IMAGE_FILE_HEADER()
        self.SectionHeaders = vstruct.VArray()
        self.SectionData = v_bytes()
        self.SymbolTable = vstruct.VArray()

    def pcb_FileHeader(self):
        c = self.FileHeader.NumberOfSections
        self.SectionHeaders = vstruct.VArray(elems=[ IMAGE_SECTION_HEADER() for i in range(c) ])
        p = self.FileHeader.PointerToSymbolTable
        if p != 0:
            s = self.FileHeader.NumberOfSymbols
            p -= len(self.FileHeader)
            p -= len(self.SectionHeaders)
            self.vsGetField('SectionData').vsSetLength(p)
            self.SymbolTable = vstruct.VArray(elems=[IMAGE_COFF_SYMBOL() for i in range(s)])

class IMAGE_ARCHIVE(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Magic = v_bytes(vbytes=IMAGE_ARCHIVE_START)
        # A set of image archive names is first...
        self.ImageArchiveMembers = vstruct.VArray(elems=(IMAGE_ARCHIVE_LINKER1(), IMAGE_ARCHIVE_LINKER2()))
        #self.ImageArchiveMembers = vstruct.VArray()

    def vsParse(self, bytes, offset=0):
        blen = len(bytes)
        offset = self.vsGetField('Magic').vsParse(bytes, offset=offset)
        # Parse the "names" headers
        offset = self.vsGetField('ImageArchiveMembers').vsParse(bytes, offset=offset)

        while offset < blen:

            doff = offset + IMAGE_ARCHIVE_HEADER_SIZE

            if bytes.startswith(IMPORT_SIG, doff):
                memb = IMAGE_ARCHIVE_IMPORT()

            elif bytes.startswith('// ', offset):
                # Skip the depricated lib strings crap...
                memb = IMAGE_ARCHIVE_MEMBER()

            else:
                memb = IMAGE_ARCHIVE_COFF()

            offset = memb.vsParse(bytes, offset=offset)
            self.ImageArchiveMembers.vsAddElement(memb)

        return offset
