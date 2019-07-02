
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
    """
    for sva, ssize, sname, sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue

        nextva = sva + ssize
        while sva < nextva:
            vw.makeCode(sva)
            ltup = vw.getLocation(sva)
            sva += ltup[vivisect.L_SIZE]


MAX_OPS = 10


def analyzeFunction(vw, funcva):
    seg = vw.getSegment(funcva)
    if seg is None:
        return

    segva, segsize, segname, segfname = seg

    if segname not in (".plt", ".plt.got"):
        return

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
    oper0 = op.opers[0]
    opval = oper0.getOperAddr(op, emu)

    loctup = vw.getLocation(opval)

    if loctup is None:
        logger.warn("PLT: 0x%x - branch deref not defined: 0x%x", opva, opval)
        return

    if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT: # FIXME: Why are some AMD64 IMPORTS showing up as LOC_POINTERs?
        vw.vprint("0x%x: %r != %r" % (funcva, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT))
        return

    fname = vw.getName(opval)
    if fname.endswith('_%.8x' % opval):
        fname = fname[:-9]
    #vw.makeName(funcva, "plt_%s" % fname, filelocal=True)
    vw.makeFunctionThunk(funcva, "plt_" + fname)

