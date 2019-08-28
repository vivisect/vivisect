
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

        nextseg = sva + ssize
        while sva < nextseg:
            if vw.getLocation(sva) is None:
                vw.makeFunction(sva)
                try:
                    analyzeFunction(vw, sva)
                except Exception as e:
                    logger.warn('0x%x: %r', sva, e)

            ltup = vw.getLocation(sva)

            if ltup is not None:
                sva += ltup[vivisect.L_SIZE]
            else:
                logger.warn('makeFunction(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1    # FIXME: add architectural "PLT_INSTRUCTION_INCREMENT" or something like it



MAX_OPS = 10


def analyzeFunction(vw, funcva):
    seg = vw.getSegment(funcva)
    if seg is None:
        return

    segva, segsize, segname, segfname = seg

    if segname not in (".plt", ".plt.got"):
        return

    logger.info('analysis of PLT function: 0x%x', funcva)
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
    #oper0 = op.opers[0]
    #opval = oper0.getOperAddr(op, emu)

    loctup = vw.getLocation(opval)
    fname = vw.getName(opval)

    if loctup is None:
        logger.warn("PLT: 0x%x - branch deref not defined: 0x%x", opva, opval)
        return

    if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT: # FIXME: Why are some AMD64 IMPORTS showing up as LOC_POINTERs?
        logger.warn("0x%x: (0x%x)  %r != %r (%r)" % (funcva, opval, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT, fname))
        return

    if fname is not None and fname.endswith('_%.8x' % opval):
        fname = fname[:-9]

    vw.makeFunctionThunk(funcva, "plt_" + fname)

