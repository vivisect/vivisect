'''
Dumps a PE in memory to disk.  Optionally specify the base address of an IAT to
rebuild. (use iatsearch command)

The dumped PE is not expected to be able to be run; however analysis tools
should properly handle the dumped PE.

Usage:
    script scripts\pedump.py <pe base address> <file to write pe to> [IAT base address]

Examples:
    script scripts\pedump.py msconfig dumped.exe 0x40e000
    (msconfig is a symbol that points to the base address of the PE)

    script scripts\pedump.py kernel32 dumpedk32.dll
'''

import PE
import vstruct

import pedump_classes as skel
reload(skel)

def walkIAT(start_of_iat):
    '''
    Takes IAT base address and builds 'chains' of import thunks.
    A chain is terminated when a null value is encountered.

    returns a list containing lists of tuples:
    [ [ (...), ... ], ... ]

    Each list is for a single thunk chain, which usually corresponds to a
    single library.

    The tuples contain:
    * symbol filename
    * symbol name
    * symbol value
    * virtual address
    * poi(virtual address)
    '''
    base_addr = trace.parseExpression(start_of_iat)
    base, size, perms, fname = trace.getMemoryMap(base_addr)

    iat_chains = []
    current_chain = []
    # TODO: assumes you are at base in memmap
    # xrange/range makes perf optimizations that doesn't work with 64bit
    # numbers with python 2.x. so...do it the non-pretty way.
    #for va in xrange(base_addr, base+size, trace.getPointerSize()):
    va = base
    while va < base + size:

        ptr = trace.parseExpression('poi(%s)' % (va))
        if ptr == 0:
            iat_chains.append(current_chain)
            current_chain = []
            va += trace.getPointerSize()
            continue

        sym = trace.getSymByAddr(ptr)
        if sym == None:
            print('no sym for this, not sure what lib this is for!?')
            # TODO: right now we break, but we need a smarter state machine
            # that can handle things we don't have symbols for.
            # (ie, if something that doesn't have a symbol hooks it)
            va += trace.getPointerSize()
            break

        tup = (sym.fname, sym.name, sym.value, va, ptr)
        current_chain.append(tup)
        va += trace.getPointerSize()

    if len(current_chain) > 0:
        iat_chains.append(current_chain)

    return iat_chains

def rebuildIAT(iatbase, is64bit):
    '''
    Given the base address of the iat, builds a new import section and header
    and returns them.
    '''
    iSection = skel.ImportSection(is64bit)
    chains = walkIAT(iatbase)
    for index, chain in enumerate(chains):
        # TODO: assume the 'name' of the library for this chain is the
        # first one in the list.  this is *not* correct.  we should check
        # all of the entries in the list and make a determination.
        if len(chain) == 0:
            # TODO: figure out why this happens
            continue
        dllname = chain[0][0] + '\x00'
        dllname = dllname.encode('ascii')
        print('adding imports for: {} with {} entries.'.format(dllname, len(chain)))
        iSection.addImportsForDLL(dllname, chain)

    # add the last NULL import directory table descriptor
    iatd = vstruct.getStructure('pe.IMAGE_IMPORT_DIRECTORY')
    iSection.ImportDirectoryTable.vsAddElement(iatd)

    return iSection

if len(argv) < 3:
    vprint(__doc__)
    raise Exception('you must specify 3 args')

pe_base = trace.parseExpression(argv[1])

p = PE.peFromMemoryObject(trace, pe_base)

is64bit = False
if trace.getMeta('Architecture') == 'amd64':
    is64bit = True

newpe = skel.DiskPE(is64bit)
newpe.dosHeader = p.IMAGE_DOS_HEADER

newpe.copyDosStubFrom(p)

newpe.ntHeaders = p.IMAGE_NT_HEADERS

# copy the section headers
for s in p.getSections():
    #if s.PointerToRawData == 0:
    #    db.vprint('PointerToRawData is 0, skipping: {}'.format(s.Name))
    #    continue
    newpe.sectionHeaders.vsAddElement(s)

# check if section alignment is less than the page size
# TODO: make arch indep
salign = newpe.ntHeaders.OptionalHeader.SectionAlignment
if salign < 0x1000:
    db.vprint('warning, salign less than page size: 0x{:x}'.format(salign))

# copy the section data
for s in p.getSections():
    #if s.PointerToRawData == 0:
    #    db.vprint('PointerToRawData is 0, skipping: {}'.format(s.Name))
    #    continue

    bytez = p.readAtRva(s.VirtualAddress, s.VirtualSize)
    new_s = skel.FixedSizeAlignedSection(len(bytez))
    new_s.vsParse(bytez)

    newpe.sections.vsAddElement(new_s)

# should we only do this if adding new import table?
newpe.clearDataDirectories()

if len(argv) > 3:
    section = rebuildIAT(argv[3], is64bit)

    iat_base = trace.parseExpression(argv[3])

    rva = iat_base - pe_base
    header = section.generateHeader(rva)

    tup = newpe.findCollidingSectionByHeader(header)
    if tup != None:
        index, cSection = tup
        db.vprint('found colliding section {}, moving to end'.format(cSection.Name))

        existingHeader = newpe.sectionHeaders[index]
        existingSection = newpe.sections[index]

        # update the VirtualAddress RVA so we aren't colliding anymore
        arva = newpe.findAvailableRVAForSection()
        existingHeader.VirtualAddress = arva

        newpe.sectionHeaders.vsAddElement(existingHeader)
        newpe.sections.vsAddElement(existingSection)

        # now do the replace
        db.vprint('replacing colliding section with new import table')
        newpe.replaceSection(index, section, header)

        newpe.importSectionIndex = index

    else:
        db.vprint('appending import section (no collision)')
        newpe.sectionHeaders.vsAddElement(header)
        newpe.sections.vsAddElement(section)

        numSections = len(newpe.sections._vs_fields)
        newpe.importSectionIndex = numSections - 1

newpe.vsCalculate()

with open(argv[2], 'wb') as f:
    bytez = newpe.vsEmit()
    f.write(bytez)

db.vprint('done.')
