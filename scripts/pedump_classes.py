'''
Classes that support the pedump command.
'''
import vstruct
import vstruct.primitives as p

# data directory indexes
IMPORT_TABLE_INDEX = 1
DEBUG_TABLE_INDEX = 6
BOUND_IMPORT_TABLE_INDEX = 11
DELAY_LOAD_IMPORT_TABLE_INDEX = 13

class DiskPE(vstruct.VStruct):
    '''
    Represents a PE we write out to disk.

    Accepts a single boolean argument for whether this is a PE32 or PE32+
    executable.
    '''
    def __init__(self, ispe32p):
        vstruct.VStruct.__init__(self)

        self.pe32p = ispe32p

        self.dosHeader = vstruct.VStruct()
        self.msdosStub = vstruct.VStruct()

        # TODO: we assume e_lfanew correctly points at this with no padding.
        self.ntHeaders = vstruct.VStruct()

        self.sectionHeaders = vstruct.VArray()

        self.padding1 = vstruct.VStruct()

        self.sections = vstruct.VArray()

        self.importSectionIndex = None

    def copyDosStubFrom(self, tpe):
        '''
        Copies the ms-dos stub from a vstruct PE object.
        PE obj is not a vstruct object, so can't use vsGetOffset.
        '''
        stub_len = tpe.IMAGE_DOS_HEADER.e_lfanew - len(tpe.IMAGE_DOS_HEADER)
        stub_bytes = tpe.readAtOffset(len(tpe.IMAGE_DOS_HEADER), stub_len)
        self.msdosStub = p.v_bytes(vbytes=stub_bytes)

    def clearDataDirectories(self):
        '''
        Clears some data directories we don't handle right now.
        '''
        for ddindex in (DEBUG_TABLE_INDEX, BOUND_IMPORT_TABLE_INDEX, DELAY_LOAD_IMPORT_TABLE_INDEX):
            dd = self.ntHeaders.OptionalHeader.DataDirectory[ddindex]
            dd.VirtualAddress = 0
            dd.Size = 0

    def getImportTableDataDir(self):
        '''
        Gets the import table data directory vstruct.
        '''
        return self.ntHeaders.OptionalHeader.DataDirectory[IMPORT_TABLE_INDEX]

    def setImportTableDataDir(self, rva, size):
        '''
        Sets the RVA and size for the import data directory.
        '''
        itdd = self.getImportTableDataDir()
        itdd.VirtualAddress = rva
        itdd.Size = size

    def updateImportTableDataDir(self, index):
        '''
        Updates the import table data directory using the section header RVA
        and calculating the size of the import directory table.
        '''
        rva_base = self.sectionHeaders[index].VirtualAddress

        section = self.sections[index]
        offset_imp_dtable = section.vsGetOffset('ImportDirectoryTable')

        rva = rva_base + offset_imp_dtable
        size = len(self.sections[index].ImportDirectoryTable)

        self.setImportTableDataDir(rva, size)

    def replaceSection(self, section_index, new_section, new_sheader):
        '''
        Uses the section_index argument to directly replace the vstruct
        objects in the sectionHeader and sections VArrays.
        '''
        # TODO: make section header optional
        self.sectionHeaders.vsSetField('%d' % section_index, new_sheader)
        self.sections.vsSetField('%d' % section_index, new_section)

    def findCollidingSectionByHeader(self, sheader):
        '''
        Finds sections that overlap/collide with the RVA in the section header
        passed in.

        Returns the section/sectionheader index and the vstruct section.
        '''
        rva = sheader.VirtualAddress
        retval = self.findCollidingSectionWithRVA(rva)

        return retval

    def updateFileOffsetForSectionByIndex(self, index):
        '''
        Updates the PointerToRawData value in the section header that
        corresponds to the section location at the specified index.
        '''
        sectionsBaseOffset = self.vsGetOffset('sections')
        sectionOffset = self.sections.vsGetOffset('%s' % index)
        fileOffset = sectionsBaseOffset + sectionOffset

        self.sectionHeaders[index].PointerToRawData = fileOffset
        # this doesn't really belong here since we can resize in vsCalculate
        # TODO
        #self.sections[index].SizeOfRawData = len(self.sections[index])

    def findCollidingSectionWithRVA(self, rva):
        '''
        Uses a RVA relative to the base virtual address of the image.
        Determines if the RVA resides in a section; if so returns the
        index of the section and the section.
        '''
        for index, section in self.sectionHeaders:
            baseva = self.ntHeaders.OptionalHeader.ImageBase
            startva = baseva + section.VirtualAddress
            endva = startva + section.VirtualSize

            va = baseva + rva
            if va >= startva and va < endva:
                return int(index), section

        return None

    def findAvailableRVAForSection(self):
        '''
        Finds an unused RVA to place in a section header
        VirtualAddress member.
        '''
        highest_va_tup = None
        for sindex, section in self.sectionHeaders:
            rva = section.VirtualAddress
            size = section.VirtualSize

            if highest_va_tup == None or rva > highest_va_tup[0]:
                highest_va_tup = (rva, size)

        next_rva = highest_va_tup[0] + size

        return next_rva

    def vsCalculate(self):
        # add padding between sections headers and section contents
        # so our sections are file aligned according to the OptionalHeader
        falign = self.ntHeaders.OptionalHeader.FileAlignment

        sizeBeforeHeaders = len(self.dosHeader) + len(self.msdosStub) + len(self.ntHeaders) + len(self.sectionHeaders)
        numToPad = getPaddingForAlignment(sizeBeforeHeaders, falign)
        self.padding1 = p.v_bytes(vbytes='\x00' * numToPad)

        # add padding to each section so we are file aligned
        for sindex, section in self.sections:
            rva = self.sectionHeaders[int(sindex)].VirtualAddress
            section.vsCalculate(rva, falign)

        # we may have changed the sizes of sections, so update the headers
        # for each section for both file and virtual alignment
        # we don't have to worry about enlarging sections to the virtual
        # alignment since thats once we are running. (ie, not on disk)
        for index, (vsname, s) in enumerate(self.sectionHeaders):

            sectionsBaseOffset = self.vsGetOffset('sections')
            sectionOffset = self.sections.vsGetOffset('%s' % vsname)
            fileOffset = sectionsBaseOffset + sectionOffset

            section = self.sections[index]
            self.sectionHeaders[index].PointerToRawData = fileOffset
            self.sectionHeaders[index].SizeOfRawData = len(section)

            # TODO: we may need to do this and then make a call to see
            # if any sections collide with the new values.
            salign = self.ntHeaders.OptionalHeader.SectionAlignment
            numAlign = getPaddingForAlignment(len(section), salign)
            virtualSize = len(section) + numAlign
            self.sectionHeaders[index].VirtualSize = virtualSize

        # update data directory location information for imports
        isi = self.importSectionIndex
        if isi != None:
            rva = self.sectionHeaders[isi].VirtualAddress
            self.sections[isi].vsCalculate(rva, falign)
            self.updateImportTableDataDir(isi)

        # update the image size and number of sections
        self.ntHeaders.OptionalHeader.SizeOfImage = len(self)
        numSections = len(self.sections._vs_fields)
        self.ntHeaders.FileHeader.NumberOfSections = numSections
        #self.ntHeaders.OptionalHeader.SizeOfHeaders =

def getPaddingForAlignment(size, alignment):
    rmd = size % alignment
    if rmd == 0:
        return 0

    num = alignment - rmd

    return num

class AlignedSection(vstruct.VStruct):
    '''
    Adds bytes to the 'padding' field in a vstruct so a structure can be
    aligned to a multiple of an arbitrary value.
    '''
    def __init__(self, abyte='\x00'):
        vstruct.VStruct.__init__(self)

        # specifies what padding byte you want to use.
        self.abyte = abyte

        # classes that derive from this must have the following line in order
        # for alignment fixes.
        # self.padding = vstruct.VStruct()

    def vsCalculate(self, falign):
        '''
        Pads a section out to a multiple of falign.
        '''
        clen = len(self)
        numPadding = getPaddingForAlignment(clen, falign)

        if numPadding == 0:
            return

        padded_bytes = self.abyte * numPadding
        self.padding = p.v_bytes(vbytes=padded_bytes)

class FixedSizeAlignedSection(AlignedSection):
    '''
    Holds data for a section that you do not intend to modify or model.
    '''
    def __init__(self, length):
        AlignedSection.__init__(self)

        self.contents = p.v_bytes(size=length)

    def vsCalculate(self, rva, falign):
        super(FixedSizeAlignedSection, self).vsCalculate(falign)

class ImportSection(AlignedSection):
    '''
    Holds data for an import section.
    '''
    def __init__(self, is64bit):
        AlignedSection.__init__(self)

        self.is64bit = is64bit

        self.ImportAddressTable = vstruct.VArray()

        self.ImportFunctionNames = vstruct.VArray()

        self.numberOfDlls = 0
        self.ImportDLLNames = vstruct.VArray()

        self.ImportDirectoryTable = vstruct.VArray()

        self.padding = vstruct.VStruct()

    def addImportsForDLL(self, dllname, importList):
        '''
        TODO: dllname must be ascii and null term, check!
        '''
        name = p.v_bytes(vbytes=dllname)
        self.ImportDLLNames.vsAddElement(name)

        d = vstruct.getStructure('pe.IMAGE_IMPORT_DIRECTORY')
        d.ForwarderChain = 0xFFFFFFFF
        d.TimeDateStamp = 0xFFFFFFFF
        self.ImportDirectoryTable.vsAddElement(d)

        if self.is64bit == True:
            itd = IMAGE_THUNK_DATA64(dllname)
        else:
            itd = IMAGE_THUNK_DATA32(dllname)

        for symfname, symname, symval, va, entry in importList:

            # add a placeholder in the thunk that we replace later
            itd.addEntry(0xdeadbeef)

            name = symname.encode('ascii').split('.')[-1] + '\x00'
            # if the name has an odd length, we need to add one <F12>
            # so it's on a word boundary
            # we should think about doing this in a vsCalculate.
            if len(name) % 2 == 1:
                name += '\x00'

            n = IMAGE_IMPORT_NAME()
            n.Hint = 0x0
            n.Name = p.v_bytes(vbytes=name)

            self.ImportFunctionNames.vsAddElement(n)

        # add NULL terminating record for thunk chain
        itd.addEntry(0x0)

        self.ImportAddressTable.vsAddElement(itd)

        # this is NOT required for any reason we do this for easing index'd
        # lookups, essentially it's a big HACK TODO: we can fix this by making
        # more vstructs. (this would also get rid of numberOfDlls)
        self.ImportFunctionNames.vsAddElement(IMAGE_IMPORT_NAME())

        self.numberOfDlls += 1

    def getThunkOffsetForLib(self, libname):
        '''
        Looks for the library name in the thunk array and calculates the offset
        from the beginning of all of the thunks.

        Returns the offset for only the first match.
        '''
        for vsname, thunk in self.ImportAddressTable:
            if thunk.libname == libname:
                offset = self.ImportAddressTable.vsGetOffset('%s' % vsname)
                return offset

        return None

    def vsCalculate(self, rva, falign):
        '''
        Allows the section to update anything that relies on knowing the
        RVA of the section.
        '''

        # set the rvas for the name's in the directory table
        si = len(vstruct.getStructure('pe.IMAGE_IMPORT_DIRECTORY'))
        for index in xrange(0, self.numberOfDlls):
            dllNamesOffset = self.vsGetOffset('ImportDLLNames')
            nameOffset = self.ImportDLLNames.vsGetOffset('%d' % index)

            name_rva = rva + dllNamesOffset + nameOffset
            self.ImportDirectoryTable[index].Name = name_rva

            hackName = self.ImportDLLNames[index]
            hackA = hackName.vsEmit().decode('ascii')
            offset = self.getThunkOffsetForLib(hackA)

            self.ImportDirectoryTable[index].FirstThunk = rva + offset
            #self.ImportDirectoryTable[index].OriginalFirstThunk = thunkRVA
            # TODO: HINT must be aligned on word boundary, so if odd length
            # need to add a byte. added this somewhere else for now.

        # set the import by name RVAs
        total = 0 # tracks where in the thunk array we are (per dll)
        for sindex, thunk in self.ImportAddressTable:

            offset = total
            for index, (name, thunkEntry) in enumerate(thunk.entries):

                # if last one in thunk is NULL, we are done and do NOT want to
                # update the value.
                if thunkEntry == 0:
                    total += 1
                    continue

                importFuncNamesOffset = self.vsGetOffset('ImportFunctionNames')
                offf = index + offset
                funcNameOffset = self.ImportFunctionNames.vsGetOffset('%d' %offf)

                func_name_rva = rva + importFuncNamesOffset + funcNameOffset
                thunk.setEntry(index, func_name_rva)
                total += 1

        super(ImportSection, self).vsCalculate(falign)

    def generateHeader(self, rva, name='.idata'):
        '''
        Generates a section header for this section.
        Make sure you call vsCalculate before calling this method or your
        sizes may be wrong due to section alignment.
        '''
        h = vstruct.getStructure('pe.IMAGE_SECTION_HEADER')
        h.Name = name
        h.Characteristics = 0xE0000020 # code | rwx
        h.VirtualAddress = rva
        h.VirtualSize = len(self)
        h.SizeOfRawData = len(self)

        return h

class IMAGE_THUNK_DATA32(vstruct.VStruct):
    def __init__(self, libname):
        vstruct.VStruct.__init__(self)

        self.libname = libname

        self.entries = vstruct.VArray()

    def addEntry(self, address):
        self.entries.vsAddElement(p.v_uint32(address))

    def setEntry(self, index, address):
        self.entries.vsSetField('%d' % index, address)

class IMAGE_THUNK_DATA64(IMAGE_THUNK_DATA32):
    def addEntry(self, address):
        self.entries.vsAddElement(p.v_uint64(address))

class IMAGE_IMPORT_NAME(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.Hint = p.v_uint16()
        self.Name = vstruct.VStruct()
