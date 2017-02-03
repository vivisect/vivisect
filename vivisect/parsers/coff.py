import re
import StringIO
import struct
import logging

import envi
import envi.memory as e_mem
import PE.coff as coff_parser
from vivisect.const import EXP_FUNCTION


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
logger.addHandler(logging.StreamHandler())

defcalls = {
    'i386': 'cdecl',
    'amd64': 'msx64call',
}


def parseFile(vw, filename):
    coff = coff_parser.parse_file(open(filename, "rb"))
    return loadCoffIntoWorkspace(vw, coff, filename)


def parseBytes(vw, bytes):
    fd = StringIO.StringIO(bytes)
    fd.seek(0)
    coff = coff_parser.parse_file(fd)
    return loadCoffIntoWorkspace(vw, coff)


def parseFd(vw, fd, filename=None):
    fd.seek(0)
    coff = coff_parser.parse_file(fd)
    return loadCoffIntoWorkspace(vw, coff, filename=filename)


def loadCoffIntoWorkspace(vw, coff, filename=None):
    machine_type = coff['MachineType']
    if machine_type == 'IMAGE_FILE_MACHINE_I386':
        arch = 'i386'
    elif machine_type == 'IMAGE_FILE_MACHINE_AMD64':
        arch = 'amd64'
    elif machine_type == 'IMAGE_FILE_MACHINE_ARM':
        arch = 'arm'
    else:
        raise TypeError('coff loader is x86/x64 only')

    vw.setMeta('Architecture', arch)
    vw.setMeta('Format', 'pe')
    vw.setMeta('Platform', 'windows')

    baseaddr = 0x40000
    vw.config.viv.parsers.blob.arch = arch
    vw.config.viv.parsers.blob.bigend = False
    vw.config.viv.parsers.blob.baseaddr = baseaddr

    defcall = defcalls.get(arch)
    if defcall:
        vw.setMeta("DefaultCall", defcall)

    fvivname = filename
    if fvivname is None:
        fvivname = "coff_%.8x" % baseaddr

    fhash = "unknown hash"
    # if os.path.exists(filename):
    #    fhash = v_parsers.md5File(filename)

    fname = vw.addFile(fvivname.lower(), baseaddr, fhash)

    # symhash = e_symcache.symCacheHashFromPe(pe)
    # vw.setFileMeta(fname, 'SymbolCacheHash', symhash)

    # Setup some va sets used by windows analysis modules
    # vw.addVaSet("Library Loads", (("Address", VASET_ADDRESS),("Library", VASET_STRING)))
    # vw.addVaSet('pe:ordinals', (('Address', VASET_ADDRESS),('Ordinal',VASET_INTEGER)))

    section_to_base = dict()
    next_free_addr = vw.config.viv.parsers.blob.baseaddr

    idx = 0
    for sec in coff['Sections']:
        idx += 1  # first section is 1, not 0
        mapflags = 0

        chars = sec['Characteristics']
        if 'IMAGE_SCN_MEM_READ' in chars:
            mapflags |= e_mem.MM_READ
        if 'IMAGE_SCN_MEM_EXECUTE' in chars:
            mapflags |= e_mem.MM_EXEC
        if 'IMAGE_SCN_MEM_WRITE' in chars:
            mapflags |= e_mem.MM_WRITE

        align = 1
        for char in chars:
            m = re.match('IMAGE_SCN_ALIGN_([\d]+)BYTES', char)
            if m:
                align = int(m.group(1))
                break

        assert sec['VirtualAddress'] == 0
        secbytes = sec['SectionData']
        seclength = sec['SizeOfRawData']
        if secbytes is None:
            secbytes = b'\x00' * seclength
        else:
            assert len(sec['SectionData']) == sec['SizeOfRawData']

        if len(secbytes) == 0:
            logger.info('skipping load of empty section')

        secname = '{}_{}'.format(sec['Name'], idx)
        secbase = ((next_free_addr + align - 1) / align) * align
        sec_end = secbase + seclength

        try:
            vw.addMemoryMap(secbase, mapflags, fname, secbytes)
            # print 'mapped 0x%x len 0x%x align %d' % (secbase, len(secbytes), align)
            vw.addSegment(secbase, seclength, secname, fname)
            section_to_base[idx] = secbase
            next_free_addr = sec_end
        except Exception as e:
            print("Error Loading Section (%s): %s" % (secname, e))

    external_symbols = list()
    symbol_to_addr = dict()  # index by [symbol_section][symbol_name] -> addr
    for idx in section_to_base.keys():
        symbol_to_addr[idx] = dict()

    for sym in coff['Symbols'].values():
        sym_sec = sym['SectionNumber']
        if sym_sec == 0xffff:  # IMAGE_SYM_ABSOLUTE
            continue
        elif sym_sec == 0xfffe:  # IMAGE_SYM_DEBUG
            continue
        elif sym_sec == 0:  # IMAGE_SYM_UNDEFINED
            external_symbols.append(sym)
        else:
            if sym_sec not in section_to_base:
                print('sym_sec {} not present'.format(sym_sec))
                continue
            sym_addr = section_to_base[sym_sec] + sym['Value']

            if sym['Name'] in symbol_to_addr[sym_sec]:
                logger.warn('multiple definition of {}'.format(sym['Name']))
            else:
                symbol_to_addr[sym_sec][sym['Name']] = sym_addr

    # we add a pseudo section containing each external symbol
    ptr_size = envi.getArchModule(arch).getPointerSize()
    seclength = len(external_symbols) * ptr_size
    secbase = ((next_free_addr + ptr_size - 1) / ptr_size) * ptr_size
    mapflags = e_mem.MM_READ
    vw.addMemoryMap(secbase, mapflags, fname, b'\x00' * seclength)
    vw.addSegment(secbase, seclength, 'extrn', fname)
    symbol_to_addr[0] = dict()
    for idx, sym in enumerate(external_symbols):
        name = sym['Name']
        addr = secbase + ptr_size * idx
        assert name not in symbol_to_addr
        symbol_to_addr[0][name] = addr
        vw.makeImport(addr, '*', name)
        # print 'adding %s at %x' % (name, addr)

    # apply the relocations
    idx = 0
    for sec in coff['Sections']:
        idx += 1
        for reloc in sec['Relocations']:
            reloc_addr = section_to_base[idx] + reloc['VirtualAddress']
            reloc_type = reloc['Type']
            sym_idx = reloc['SymbolTableIndex']
            sym = coff['Symbols'][sym_idx]
            sym_sec = sym['SectionNumber']
            sym_name = sym['Name']
            assert sym_name == reloc['SymbolName']

            if reloc_type not in ('IMAGE_REL_I386_REL32',
                                  'IMAGE_REL_I386_DIR32',
                                  'IMAGE_REL_AMD64_REL32',
                                  'IMAGE_REL_AMD64_ADDR32NB'):
                info = 'unsupported reloc {}'.format(reloc_type)
                logger.info(info)
                continue

            to_sym_addr = symbol_to_addr[sym_sec][sym_name]
            if reloc_type == 'IMAGE_REL_I386_REL32' or \
               reloc_type == 'IMAGE_REL_AMD64_REL32':
                mem = vw.readMemory(reloc_addr, 4)
                prev_val = struct.unpack('<I', mem)[0]
                if prev_val != 0:
                    logger.info('prev addr != 0, verify me')

                new_val = prev_val + to_sym_addr - reloc_addr - 4
                new_val %= 2**32
                mem_update = struct.pack('<I', new_val)
                # print 'relocating addr %x to %x' % (reloc_addr, new_val)
                vw.writeMemory(reloc_addr, mem_update, check_perms=False)
                # read = vw.readMemory(reloc_addr, 4)
                # print 'read %x' % struct.unpack('<I', read)[0]

            elif reloc_type == 'IMAGE_REL_I386_DIR32' or \
                    reloc_type == 'IMAGE_REL_AMD64_ADDR32NB':
                mem_update = struct.pack('<I', to_sym_addr)
                # print 'relocating addr %x to %x' % (reloc_addr, to_sym_addr)
                vw.writeMemory(reloc_addr, mem_update, check_perms=False)
                # read = vw.readMemory(reloc_addr, 4)
                # print 'read %x' % struct.unpack('<I', read)[0]

            # {'IMAGE_REL_I386_SECTION', 'IMAGE_REL_I386_SECREL'}

    # add entry point for each function and exports for each exported function
    for sym in coff['Symbols'].values():
        if sym['ComplexType'] != 'IMAGE_SYM_DTYPE_FUNCTION':
            continue
        if sym['SectionNumber'] in (0, 0xfffe, 0xffff):
            continue

        sym_name = sym['Name']
        sym_sec = sym['SectionNumber']
        sym_addr = symbol_to_addr[sym_sec][sym_name]
        vw.addEntryPoint(sym_addr)

        assert vw.probeMemory(sym_addr, 1, e_mem.MM_EXEC)
        if sym['StorageClass'] == 'IMAGE_SYM_CLASS_EXTERNAL':
            # print 'exporting %s at %d' % (sym_name, sym_addr)
            vw.addExport(sym_addr, EXP_FUNCTION, sym_name, fname)
        vw.makeName(sym_addr, sym_name, filelocal=False)

    '''
    added_addrs = set()
    added_symbols = set()
    for addr, size, function, module in vw.getExports():
        # TODO check what happens if exported by ordinal
        vw.makeName(addr, function, filelocal=False)
        added_addrs.add(addr)
        added_symbols.add(function)

    # makeName for label information
    for sym_sec, symbols in symbol_to_addr.iteritems():
        for name, addr in symbols.iteritems():
            if name in added_symbols or addr in added_addrs:
                # print('symbols {} already added, skipping'.format(name))
                continue
            added_addrs.add(addr)
            added_symbols.add(name)
            vw.makeName(addr, name, filelocal=False)
            # print('makeName %s 0x%x' % (name, addr))
    '''

    return fname


if __name__ == '__main__':
    import sys
    import vivisect.cli as viv_cli
    vw = viv_cli.VivCli()
    filename = sys.argv[1]
    coff = coff_parser.parse_file(open(filename, "rb"))
    result = parseFile(vw, filename)
    import code
    code.interact(local=locals())
