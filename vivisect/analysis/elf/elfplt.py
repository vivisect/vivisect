
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
"""
import logging
import vivisect
import envi
import envi.archs.i386 as e_i386

logger = logging.getLogger(__name__)


def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    Make functions 
    """
    for sva, ssize, sname, sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue

        # make the first function as the dyn linker helper func, then skip 16 bytes #FIXME: JANKY
        vw.makeFunction(sva)
        sva += 0x10

        nextseg = sva + ssize
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



MAX_OPS = 10


def analyzeFunction(vw, funcva):
    logger.info('analyzeFunction(vw, 0x%x)', funcva)

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
                if ptrname.startswith(segfname+'.'):
                    fpart, npart = ptrname.split('.', 1)
                    funcname = '%s.ptr_%r' % (fpart, npart)
                    logger.info('.0  %r  / %r  / %r', fpart, npart, funcname)
                else:
                    if fpart == '*':
                        fpart, npart = ptrname.split('.', 1)
                        logger.info('.1  %r  / %r  / %r', fpart, npart, funcname)
                        funcname = npart
                    funcname = 'ptr_%r' % ptrname
                    logger.info('.2  %r', funcname)

    elif loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT:
        logger.warn("0x%x: (0x%x)  %r != %r (%r)" % (funcva, opval, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT, funcname))
        return

    if funcname is not None and funcname.endswith('_%.8x' % opval):
        funcname = funcname[:-9]

    logger.info('makeFunctionThunk(0x%x, "plt_%s")', funcva, funcname)
    vw.makeFunctionThunk(funcva, "plt_" + funcname)
