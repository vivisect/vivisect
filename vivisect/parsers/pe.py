import logging
from io import BytesIO

import PE
import PE.carve as pe_carve

import vstruct
import vivisect
import vivisect.exc as v_exc
import vivisect.parsers as v_parsers
# Steal symbol parsing from vtrace
import vtrace  # needed only for setting the logging level
import vtrace.platforms.win32 as vt_win32

import envi.exc as e_exc
import envi.const as e_const
import envi.symstore.symcache as e_symcache

from vivisect.const import *

logger = logging.getLogger(__name__)

for mod in (PE, vtrace):
    olog = logging.getLogger(mod.__name__)
    olog.setLevel(logger.getEffectiveLevel())

# PE Machine field values
# 0x14d   Intel i860
# 0x14c   Intel I386 (same ID used for 486 and 586)
# 0x162   MIPS R3000
# 0x166   MIPS R4000
# 0x183   DEC Alpha AXP


def align(v, alignment):
    remainder = v % alignment
    if remainder == 0:
        return v
    else:
        return v + (alignment - remainder)


def parseFile(vw, filename, baseaddr=None):
    pe = PE.PE(open(filename, "rb"))
    return loadPeIntoWorkspace(vw, pe, filename=filename, baseaddr=baseaddr)


def parseBytes(vw, bytes, baseaddr=None):
    fd = BytesIO(bytes)
    fd.seek(0)
    pe = PE.PE(fd)
    return loadPeIntoWorkspace(vw, pe, baseaddr=baseaddr)


def parseMemory(vw, memobj, base):
    pe = PE.peFromMemoryObject(memobj, base)
    # FIXME does the PE's load address get fixedup on rebase?
    return loadPeIntoWorkspace(vw, pe, filename=None)


def parseFd(vw, fd, filename=None, baseaddr=None):
    fd.seek(0)
    pe = PE.PE(fd)
    return loadPeIntoWorkspace(vw, pe, filename=filename, baseaddr=baseaddr)


arch_names = {
    PE.IMAGE_FILE_MACHINE_I386: 'i386',
    PE.IMAGE_FILE_MACHINE_AMD64: 'amd64',
    PE.IMAGE_FILE_MACHINE_ARM: 'arm',
    # DEV: uncomment this line to enable the arch (prolly not going to happen until AArch64 gets finished)
    # PE.IMAGE_FILE_MACHINE_ARM64: 'arm64',
    PE.IMAGE_FILE_MACHINE_ARMNT: 'thumb',
    PE.IMAGE_FILE_MACHINE_THUMB: 'thumb16',
}

archcalls = {
    'i386': 'cdecl',
    'amd64': 'msx64call',
    'arm': 'armcall',
    'thumb': 'armcall',
    'thumb16': 'armcall',
}

# map PE relocation types to vivisect types where possible
relmap = {
    PE.IMAGE_REL_BASED_HIGHLOW: vivisect.RTYPE_BASEOFF,
    PE.IMAGE_REL_BASED_DIR64: vivisect.RTYPE_BASEOFF,
}


def loadPeIntoWorkspace(vw, pe, filename=None, baseaddr=None):

    mach = pe.IMAGE_NT_HEADERS.FileHeader.Machine

    arch = arch_names.get(mach)
    if arch is None:
        raise v_exc.InvalidArchitecture("PE", hex(mach))

    vw.setMeta('Architecture', arch)
    vw.setMeta('Format', 'pe')
    vw.parsedbin = pe
    byts = pe.getFileBytes()
    vw.setMeta('FileBytes', v_parsers.compressBytes(byts))

    platform = 'windows'

    # Drivers are platform "winkern" so impapi etc works
    subsys = pe.IMAGE_NT_HEADERS.OptionalHeader.Subsystem
    if subsys == PE.IMAGE_SUBSYSTEM_NATIVE:
        platform = 'winkern'

    vw.setMeta('Platform', platform)

    vw.setMeta('DefaultCall', archcalls.get(arch, 'unknown'))

    # Set ourselves up for extended windows binary analysis

    if baseaddr is None:
        baseaddr = pe.IMAGE_NT_HEADERS.OptionalHeader.ImageBase
    entry = pe.IMAGE_NT_HEADERS.OptionalHeader.AddressOfEntryPoint + baseaddr
    entryrva = entry - baseaddr

    codebase = pe.IMAGE_NT_HEADERS.OptionalHeader.BaseOfCode
    codesize = pe.IMAGE_NT_HEADERS.OptionalHeader.SizeOfCode
    codervamax = codebase+codesize

    # grab the file bytes for hashing
    pe.fd.seek(0)
    fhash = v_parsers.md5Bytes(byts)
    sha256 = v_parsers.sha256Bytes(byts)

    fvivname = filename
    # This will help linkers with files that are re-named
    dllname = pe.getDllName()
    if dllname:
        fvivname = dllname

    if fvivname is None:
        fvivname = fhash

    # create the file and store md5 and sha256 hashes
    fname = vw.addFile(fvivname.lower(), baseaddr, fhash)
    vw.setFileMeta(fname, 'sha256', sha256)

    symhash = e_symcache.symCacheHashFromPe(pe)
    vw.setFileMeta(fname, 'SymbolCacheHash', symhash)

    # Add file version info if VS_VERSIONINFO has it
    try:
        vs = pe.getVS_VERSIONINFO()
    except Exception as e:
        vs = None
        vw.vprint('Failed to load version info resource due to %s' % (repr(e),))
    if vs is not None:
        vsver = vs.getVersionValue('FileVersion')
        if vsver is not None and len(vsver):
            # add check to split seeing samples with spaces and nothing else..
            parts = vsver.split()
            if len(parts):
                vsver = vsver.split()[0]
                vw.setFileMeta(fname, 'Version', vsver)

    # Setup some va sets used by windows analysis modules
    vw.addVaSet("Library Loads", (("Address", VASET_ADDRESS), ("Library", VASET_STRING)))
    vw.addVaSet('pe:ordinals', (('Address', VASET_ADDRESS), ('Ordinal', VASET_INTEGER)))
    vw.addVaSet('DelayImports', (('Address', VASET_ADDRESS), ('DelayImport', VASET_STRING)))

    # SizeOfHeaders spoofable...
    curr_offset = pe.IMAGE_DOS_HEADER.e_lfanew + len(pe.IMAGE_NT_HEADERS)

    secsize = len(vstruct.getStructure("pe.IMAGE_SECTION_HEADER"))

    sec_offset = pe.IMAGE_DOS_HEADER.e_lfanew + 4 + len(pe.IMAGE_NT_HEADERS.FileHeader) + pe.IMAGE_NT_HEADERS.FileHeader.SizeOfOptionalHeader 

    if sec_offset != curr_offset:
        header_size = sec_offset + pe.IMAGE_NT_HEADERS.FileHeader.NumberOfSections * secsize
    else:
        header_size = pe.IMAGE_DOS_HEADER.e_lfanew + len(pe.IMAGE_NT_HEADERS) + pe.IMAGE_NT_HEADERS.FileHeader.NumberOfSections * secsize

    # Add the first page mapped in from the PE header.
    header = pe.readAtOffset(0, header_size)

    if not header:
        raise v_exc.CorruptPeFile("truncated PE header")

    secalign = pe.IMAGE_NT_HEADERS.OptionalHeader.SectionAlignment
    filealign = pe.IMAGE_NT_HEADERS.OptionalHeader.FileAlignment
    subsys_majver = pe.IMAGE_NT_HEADERS.OptionalHeader.MajorSubsystemVersion
    subsys_minver = pe.IMAGE_NT_HEADERS.OptionalHeader.MinorSubsystemVersion

    if secalign == 0:
        raise v_exc.CorruptPeFile("section alignment is zero")

    secrem = len(header) % secalign
    if secrem != 0:
        header += b'\x00' * (secalign - secrem)

    vw.addMemoryMap(baseaddr, e_const.MM_READ, fname, header)
    vw.addSegment(baseaddr, len(header), "PE_Header", fname)

    hstruct = vw.makeStructure(baseaddr, "pe.IMAGE_DOS_HEADER")
    magicaddr = hstruct.e_lfanew
    if vw.readMemory(baseaddr + magicaddr, 2) != b"PE":
        raise Exception("We only support PE exe's")

    if not vw.isLocation(baseaddr + magicaddr):
        padloc = vw.makePad(baseaddr + magicaddr, 4)

    ifhdr_va = baseaddr + magicaddr + 4
    ifstruct = vw.makeStructure(ifhdr_va, "pe.IMAGE_FILE_HEADER")
    ohstruct = vw.makeStructure(ifhdr_va + len(ifstruct), "pe.IMAGE_OPTIONAL_HEADER")
    nxcompat = ohstruct.DllCharacteristics & PE.IMAGE_DLLCHARACTERISTICS_NX_COMPAT

    # get resource data directory
    ddir = pe.getDataDirectory(PE.IMAGE_DIRECTORY_ENTRY_RESOURCE)
    loadrsrc = vw.config.viv.parsers.pe.loadresources
    carvepes = vw.config.viv.parsers.pe.carvepes

    deaddirs = [PE.IMAGE_DIRECTORY_ENTRY_EXPORT,
                PE.IMAGE_DIRECTORY_ENTRY_IMPORT,
                PE.IMAGE_DIRECTORY_ENTRY_RESOURCE,
                PE.IMAGE_DIRECTORY_ENTRY_EXCEPTION,
                PE.IMAGE_DIRECTORY_ENTRY_SECURITY,
                PE.IMAGE_DIRECTORY_ENTRY_BASERELOC,
                PE.IMAGE_DIRECTORY_ENTRY_DEBUG,
                PE.IMAGE_DIRECTORY_ENTRY_COPYRIGHT,
                PE.IMAGE_DIRECTORY_ENTRY_ARCHITECTURE,
                PE.IMAGE_DIRECTORY_ENTRY_GLOBALPTR,
                PE.IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG,
                PE.IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT,
                PE.IMAGE_DIRECTORY_ENTRY_IAT,
                PE.IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT,
                PE.IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR]
    deadvas = [ddir.VirtualAddress]
    for datadir in deaddirs:
        d = pe.getDataDirectory(datadir)
        if d.VirtualAddress:
            deadvas.append(d.VirtualAddress)

    for idx, sec in enumerate(pe.sections):
        mapflags = 0
        offset = sec.vsGetMeta("Offset", None)
        if offset:
            addr = baseaddr + offset
            vw.makeStructure(addr, 'pe.IMAGE_SECTION_HEADER')
        chars = sec.Characteristics
        if chars & PE.IMAGE_SCN_MEM_READ:
            mapflags |= e_const.MM_READ

            isrsrc = (sec.VirtualAddress == ddir.VirtualAddress)
            if isrsrc and not loadrsrc:
                continue

            # If it's for an older system, just about anything
            # is executable...
            # However, there is the DLLCHARACTERISTICS NXCOMPAT flag to take into account,
            # which works with the OS to prevent certain pages of memory from achieving 
            # execution unless they're marked with the execute bit
            # so we can't just blindly mark these as executable quite yet.
            if not nxcompat:
                if not vw.config.viv.parsers.pe.nx and subsys_majver < 6 and not isrsrc:
                    mapflags |= e_const.MM_EXEC

        if chars & PE.IMAGE_SCN_MEM_READ:
            mapflags |= e_const.MM_READ
        if chars & PE.IMAGE_SCN_MEM_WRITE:
            mapflags |= e_const.MM_WRITE
        if chars & PE.IMAGE_SCN_MEM_EXECUTE:
            mapflags |= e_const.MM_EXEC
        if chars & PE.IMAGE_SCN_CNT_CODE:
            mapflags |= e_const.MM_EXEC

        secrva = sec.VirtualAddress
        secvsize = sec.VirtualSize
        secfsize = sec.SizeOfRawData
        secbase = secrva + baseaddr
        secname = sec.Name.strip("\x00")
        secrvamax = secrva + secvsize

        # If the section is part of BaseOfCode->SizeOfCode
        # force execute perms...
        if secrva >= codebase and secrva < codervamax:
            mapflags |= e_const.MM_EXEC

        # If the entry point is in this section, force execute
        # permissions.
        if secrva <= entryrva and entryrva < secrvamax:
            mapflags |= e_const.MM_EXEC

        if not nxcompat:
            if not vw.config.viv.parsers.pe.nx and subsys_majver < 6 and mapflags & e_const.MM_READ:
                mapflags |= e_const.MM_EXEC

        if sec.VirtualSize == 0 or sec.SizeOfRawData == 0:
            if idx+1 >= len(pe.sections):
                continue
            # fill the gap with null bytes..
            nsec = pe.sections[idx+1]
            nbase = nsec.VirtualAddress + baseaddr

            plen = nbase - secbase
            readsize = sec.SizeOfRawData if sec.SizeOfRawData < sec.VirtualSize else sec.VirtualSize
            secoff = pe.rvaToOffset(secrva)
            secbytes = pe.readAtOffset(secoff, readsize)
            secbytes += b'\x00' * plen
            vw.addMemoryMap(secbase, mapflags, fname, secbytes)
            vw.addSegment(secbase, len(secbytes), secname, fname)

            # Mark dead data on resource and import data directories
            if sec.VirtualAddress in deadvas:
                vw.markDeadData(secbase, secbase+len(secbytes))

            #FIXME create a mask for this
            if not (chars & PE.IMAGE_SCN_CNT_CODE) and not (chars & PE.IMAGE_SCN_MEM_EXECUTE) and not (chars & PE.IMAGE_SCN_MEM_WRITE):
                vw.markDeadData(secbase, secbase+len(secbytes))
            continue

        # if SizeOfRawData is greater than VirtualSize we'll end up using VS in our read..
        if sec.SizeOfRawData < sec.VirtualSize:
            if sec.SizeOfRawData > pe.filesize:
                continue

        plen = sec.VirtualSize - sec.SizeOfRawData

        try:
            # According to http://code.google.com/p/corkami/wiki/PE#section_table if SizeOfRawData is larger than VirtualSize, VS is used..
            readsize = sec.SizeOfRawData if sec.SizeOfRawData < sec.VirtualSize else sec.VirtualSize

            # align the read to the FileAlignment
            readsize = align(readsize, filealign)

            secoff = pe.rvaToOffset(secrva)
            secbytes = pe.readAtOffset(secoff, readsize, shortok=True)
            slen = len(secbytes)
            if slen != readsize:
                logger.warning("Section at offset 0x%x should have 0x%x bytes, but we only got 0x%x bytes", secoff, readsize, slen)

            if slen != align(sec.VirtualSize, secalign):
                # pad the section up to next the SectionAlignment
                secbytes += b'\x00' * (align(sec.VirtualSize, secalign) - slen)

            slen = len(secbytes)
            vw.addMemoryMap(secbase, mapflags, fname, secbytes)
            vw.addSegment(secbase, slen, secname, fname)

            # Mark dead data on resource and import data directories
            if sec.VirtualAddress in deadvas:
                vw.markDeadData(secbase, secbase+len(secbytes))

            # FIXME create a mask for this
            if not (chars & PE.IMAGE_SCN_CNT_CODE) and not (chars & PE.IMAGE_SCN_MEM_EXECUTE) and not (chars & PE.IMAGE_SCN_MEM_WRITE):
                vw.markDeadData(secbase, secbase+len(secbytes))

        except Exception as e:
            logger.warning("Error Loading Section (%s size:%d rva:%.8x offset: %d): %s", secname, secfsize, secrva, secoff, e)

    vw.addExport(entry, EXP_FUNCTION, '__entry', fname)
    vw.addEntryPoint(entry)

    # store the actual reloc section virtual address
    reloc_va = pe.getDataDirectory(PE.IMAGE_DIRECTORY_ENTRY_BASERELOC).VirtualAddress
    if reloc_va:
        reloc_va += baseaddr
    vw.setFileMeta(fname, "reloc_va", reloc_va)

    for rva, rtype in pe.getRelocations():

        # map PE reloc to VIV reloc ( or dont... )
        vtype = relmap.get(rtype)
        if vtype is None:
            logger.info('Skipping PE Relocation type: %d at %d (no handler)', rtype, rva)
            continue

        try:
            mapoffset = vw.readMemoryPtr(rva + baseaddr) - baseaddr
        except:
            # the target adderss of the relocation is not accessible.
            # for example, it's not mapped, or split across sections, etc.
            # technically, the PE is corrupt.
            # by continuing on here, we are a bit more robust (but maybe incorrect)
            # than the Windows loader.
            #
            # discussed in:
            # https://github.com/vivisect/vivisect/issues/346
            logger.warning('Skipping invalid PE relocation: %d', rva)
            continue
        else:
            vw.addRelocation(rva + baseaddr, vtype, mapoffset)

    for rva, lname, iname in pe.getImports():
        if vw.probeMemory(rva + baseaddr, 4, e_const.MM_READ):
            vw.makeImport(rva + baseaddr, lname, iname)

    for rva, lname, iname in pe.getDelayImports():
        if vw.probeMemory(rva + baseaddr, 4, e_const.MM_READ):
            vw.makeImport(rva + baseaddr, lname, iname)
            if lname != '*':
                lname = vw.normFileName(lname)
            vw.setVaSetRow('DelayImports', (rva + baseaddr, lname + '.' + iname))

    # Tell vivisect about ntdll functions that don't exit...
    vw.addNoReturnApi("ntdll.RtlExitUserThread")
    vw.addNoReturnApi("kernel32.ExitProcess")
    vw.addNoReturnApi("kernel32.ExitThread")
    vw.addNoReturnApi("kernel32.FatalExit")
    vw.addNoReturnApiRegex(r"^msvcr.*\._CxxThrowException$")
    vw.addNoReturnApiRegex(r"^msvcr.*\.abort$")
    vw.addNoReturnApiRegex(r"^msvcr.*\.exit$")
    vw.addNoReturnApiRegex(r"^msvcr.*\._exit$")
    vw.addNoReturnApiRegex(r"^msvcr.*\.quick_exit$")
    vw.addNoReturnApiRegex(r"^api_ms_win_crt_runtime_.*\._invalid_parameter_noinfo_noreturn$")
    vw.addNoReturnApiRegex(r"^api_ms_win_crt_runtime_.*\.exit$")
    vw.addNoReturnApiRegex(r"^api_ms_win_crt_runtime_.*\._exit$")
    # https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/invalid-parameter-functions?view=vs-2019
    # TODO: Again, there's a couple in there that have conditional termination that we should check for
    #vw.addNoReturnApiRegex("vcruntime140.__std_terminate")
    # TODO: we should add abort and terminate on the conditions that there are no signal handlers
    # registered
    # https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/cexit-c-exit?view=vs-2019
    # vw.addNoReturnApiRegex("^msvcr.*\._cexit$")
    # vw.addNoReturnApiRegex("^msvcr.*\._c_exit$")
    vw.addNoReturnApi("ntoskrnl.KeBugCheckEx")


    exports = pe.getExports()
    for rva, ord, name in exports:
        eva = rva + baseaddr

        # Functions exported by ordinal only have no name
        if not name:
            name = "Ordinal_" + str(ord)

        try:
            vw.setVaSetRow('pe:ordinals', (eva, ord))
            vw.addExport(eva, EXP_UNTYPED, name, fname)
            if vw.probeMemory(eva, 1, e_const.MM_EXEC):
                vw.addEntryPoint(eva)
        except Exception as e:
            vw.vprint('addExport Failed: %s.%s (0x%.8x): %s' % (fname, name, eva, e))

    # Save off the ordinals...
    vw.setFileMeta(fname, 'ordinals', exports)

    fwds = pe.getForwarders()
    for rva, name, forwardname in fwds:
        vw.makeName(rva+baseaddr, "forwarder_%s.%s" % (fname, name))
        vw.makeString(rva+baseaddr)

    vw.setFileMeta(fname, 'forwarders', fwds)

    # Check For SafeSEH list...
    if pe.IMAGE_LOAD_CONFIG is not None:

        vw.setFileMeta(fname, "SafeSEH", True)

        va = pe.IMAGE_LOAD_CONFIG.SEHandlerTable
        if va != 0:
            vw.makeName(va, "%s.SEHandlerTable" % fname)
            count = pe.IMAGE_LOAD_CONFIG.SEHandlerCount
            # RP BUG FIX - sanity check the count
            if count * 4 < pe.filesize and vw.isValidPointer(va):
                # XXX - CHEAP HACK for some reason we have binaries still thorwing issues.. 

                try:
                    # Just cheat and use the workspace with memory maps in it already
                    for h in vw.readMemoryFormat(va, "<%dP" % count):
                        sehva = baseaddr + h
                        vw.addEntryPoint(sehva)
                        #vw.hintFunction(sehva, meta={'SafeSEH':True})
                except:
                    vw.vprint("SEHandlerTable parse error")

    # Last but not least, see if we have symbol support and use it if we do
    if vt_win32.dbghelp and filename:

        s = vt_win32.Win32SymbolParser(-1, filename, baseaddr)

        # We don't want exports or whatever because we already have them
        s.symopts |= vt_win32.SYMOPT_EXACT_SYMBOLS
        s.parse()

        # Add names for any symbols which are missing them
        for symname, symva, size, flags in s.symbols:

            if not vw.isValidPointer(symva):
                continue

            try:

                if vw.getName(symva) is None:
                    vw.makeName(symva, symname, filelocal=True)

            except Exception as e:
                vw.vprint("Symbol Load Error: %s" % e)

        # Also, lets set the locals/args name hints if we found any
        vw.setFileMeta(fname, 'PELocalHints', s._sym_locals)

    # if it has an EXCEPTION directory parse if it has the pdata
    edir = pe.getDataDirectory(PE.IMAGE_DIRECTORY_ENTRY_EXCEPTION)
    if edir.VirtualAddress and arch == 'amd64':
        va = edir.VirtualAddress + baseaddr
        vamax = va + edir.Size
        while va < vamax:
            try:
                f = vw.makeStructure(va, 'pe.IMAGE_RUNTIME_FUNCTION_ENTRY')
            except e_exc.SegmentationViolation as e:
                logger.warning('Invalid exception entry at 0x%x (error: %s)' % (va, str(e)))
                break

            if not vw.isValidPointer(baseaddr + f.UnwindInfoAddress):
                break

            # FIXME UNWIND_INFO *requires* DWORD alignment, how is it enforced?
            fva = f.BeginAddress + baseaddr
            uiva = baseaddr + f.UnwindInfoAddress
            # Possible method 1...
            #uiva = baseaddr + (f.UnwindInfoAddress & 0xfffffffc )

            # Possible method 2...
            #uirem = f.UnwindInfoAddress % 4
            #if uirem:
                #uiva += ( 4 - uirem )
            uinfo = vw.getStructure(uiva, 'pe.UNWIND_INFO')
            ver = uinfo.VerFlags & 0x7
            if ver != 1:
                vw.vprint('Unwind Info Version: %d (bailing on .pdata)' % ver)
                break

            flags = uinfo.VerFlags >> 3
            # Check if it's a function *block* rather than a function *entry*
            if not (flags & PE.UNW_FLAG_CHAININFO):
                vw.addEntryPoint(fva)

            va += len(f)

    # auto-mark embedded PEs as "dead data" to prevent code flow...
    if carvepes:
        pe.fd.seek(0)
        fbytes = pe.fd.read()
        for offset, i in pe_carve.carve(fbytes, 1):
            # Found a sub-pe!
            subpe = pe_carve.CarvedPE(fbytes, offset, [i])
            pebytes = subpe.readAtOffset(0, subpe.getFileSize())
            rva = pe.offsetToRva(offset) + baseaddr
            vw.markDeadData(rva, rva+len(pebytes))

    return fname
