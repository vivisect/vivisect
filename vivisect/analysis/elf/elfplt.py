
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
"""
import logging
import vivisect
import envi
import envi.archs.i386 as e_i386

logger = logging.getLogger(__name__)

MAGIC_PLT_SIZE = 16

def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    Make functions 
    """
    print "=========== ELF PLT ANALYSIS MODULE START ============="
    for sva, ssize, sname, sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue
        '''
    for filename in vw.getFiles():
        dyns = vw.getFileMeta(filename, 'ELF_DYNAMICS')
        addbase = vw.getFileMeta(filename, 'addbase')
        imgbase = vw.getFileMeta(filename, 'imagebase')
        if dyns is None:
            logger.info('skipping file %r: no ELF_DYNAMICS info', filename)
            continue

        pltva = dyns.get('DT_JMPREL')
        pltsz = dyns.get('DT_PLTRELSZ')
        if pltva is None or pltsz is None:
            logger.info('skipping file %r: no PLT/SZ info (staticly-linked?)', filename)
            continue
        if addbase:
            pltva += imgbase
        nextseg = pltva + pltsz
        sva = pltva
    '''
        nextseg = sva + ssize
        # make code
        while sva < nextseg:
            if vw.getLocation(sva) is None:
                logger.info('making PLT function: 0x%x', sva)
                try:
                    vw.makeCode(sva)
                except Exception as e:
                    logger.warn('0x%x: exception: %r', sva, e)

            ltup = vw.getLocation(sva)

            if ltup is not None:
                sva += ltup[vivisect.L_SIZE]
                logger.debug('incrementing to next va: 0x%x', sva)
            else:
                logger.warn('makeCode(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1    # FIXME: add architectural "PLT_INSTRUCTION_INCREMENT" or something like it


        # scroll through arbitrary length functions and make functions
        for sva in range(sva, nextseg, MAGIC_PLT_SIZE):
            vw.makeFunction(sva)
            analyzeFunction(vw, sva)

    '''
    for sva, ssize, sname, sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue

        # make the first function as the dyn linker helper func, then skip 16 bytes #FIXME: JANKY
        vw.makeFunction(sva)
        nextseg = sva + ssize
        sva += 0x10

        while sva < nextseg:
            if vw.getLocation(sva) is None:
                logger.info('making PLT function: 0x%x', sva)
                vw.makeFunction(sva)
                try:
                    analyzeFunction(vw, sva)
                except Exception as e:
                    logger.warn('0x%x: exception: %r', sva, e)

            ltup = vw.getLocation(sva)

            if ltup is not None:
                sva += ltup[vivisect.L_SIZE]
                logger.debug('incrementing to next va: 0x%x', sva)
            else:
                logger.warn('makeFunction(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1    # FIXME: add architectural "PLT_INSTRUCTION_INCREMENT" or something like it
'''

MAX_OPS = 10


def analyzeFunction(vw, funcva):
    print "=========== ELF PLT FUNCTION ANALYSIS MODULE START ============="
    logger.warn('analyzeFunction(vw, 0x%x)', funcva)
    return

    seg = vw.getSegment(funcva)
    if seg is None:
        logger.info('not analyzing 0x%x: no segment found', funcva)
        return

    segva, segsize, segname, segfname = seg

    if segname not in (".plt", ".plt.got"):
        logger.info('not analyzing 0x%x: not part of ".plt" or ".plt.got"', funcva)
        return

    logger.info('analyzing PLT function: 0x%x', funcva)
    count = 0
    opva = funcva
    op = vw.parseOpcode(opva)
    while count < MAX_OPS and op.iflags & envi.IF_BRANCH == 0:
        opva += len(op)
        op = vw.parseOpcode(opva)

    if op.iflags & envi.IF_BRANCH == 0:
        logger.warn("PLT: 0x%x - Could not find a branch!", funcva)
        return

    # slight hack, but we don't currently know if thunk_bx exists
    gotplt = None
    for va, size, name, fname in vw.getSegments():
        if name == ".got.plt":
            gotplt = va
            break

    if gotplt is None:
        gotplt = -1

    # all architectures should at least have some minimal emulator
    emu = vw.getEmulator()
    emu.setRegister(e_i386.REG_EBX, gotplt)  # every emulator will have a 4th register, and if it's not used, no harm done.

    branches = op.getBranches(emu)
    if len(branches) != 1:
        logger.warn('getBranches() returns anomolous results: 0x%x: %r   (result: %r)',
                op.va, op, branches)
        return

    opval, brflags = branches[0]

    if vw.getFunction(opval) == opval:
        # this is a lazy-link/load function, calling the first entry in the PLT
        logger.info('0x%x is a non-thunk', funcva)
        return

    loctup = vw.getLocation(opval)
    funcname = vw.getName(opval)

    if loctup is None:
        logger.warn("PLT: 0x%x - branch deref not defined: 0x%x", opva, opval)
        return

    if loctup[vivisect.L_LTYPE] == vivisect.LOC_POINTER:  # Some AMD64 PLT entries point at nameless relocations that point internally
        tgtva = loctup[vivisect.L_VA]
        ptrva = vw.readMemoryPtr(tgtva)
        ptrname = vw.getName(ptrva)
        logger.info("PLT->PTR 0x%x: (0x%x)  -> 0x%x -> 0x%x (%r)" % (funcva, opval, tgtva, ptrva, ptrname))
        if vw.isValidPointer(ptrva):
            if funcname is None:
                funcname = _addNamePrefix(vw, ptrname, ptrva, 'ptr', '_')

    elif loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT:
        logger.warn("0x%x: (0x%x)  %r != %r (%r)" % (funcva, opval, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT, funcname))
        return

    if funcname is not None and funcname.endswith('_%.8x' % opval):
        funcname = funcname[:-9]

    logger.info('makeFunctionThunk(0x%x, "plt_%s")', funcva, funcname)
    vw.makeFunctionThunk(funcva, "plt_" + funcname)


def _getNameParts(vw, name, va):
    fpart = None
    npart = name
    vapart = None
    fname = vw.getFileByVa(va)
    if name.startswith(fname + '.'):
        fpart, npart = name.split('.', 1)
    elif name.startswith('*.'):
        skip, npart = name.split('.', 1)

    if npart.endswith('_%.8x' % va):
        npart, vapart = npart.rsplit('_', 1)

    return fpart, npart, vapart


def _addNamePrefix(vw, name, va, prefix, joinstr=''):
    fpart, npart, vapart = _getNameParts(vw, name, va)
    if fpart is None and vapart is None:
        name = joinstr.join([prefix, npart])

    elif vapart is None:
        name = fpart + '.' + joinstr.join([prefix, npart])

    elif fpart is None:
        name = joinstr.join([prefix, npart])

    else:
        name = fpart + '.' + joinstr.join([prefix, npart]) + '_' % vapart
    logger.debug('addNamePrefix: %r %r %r -> %r', fpart, npart, vapart, name)
    return name
