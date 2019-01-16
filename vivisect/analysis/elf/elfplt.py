
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
"""

import vivisect
import envi
import envi.archs.i386 as e_i386
import envi.archs.i386.opcode86 as opcode86

def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    """
    for sva,ssize,sname,sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue

        nextva = sva + ssize
        while sva < nextva:
            vw.makeCode(sva)
            ltup = vw.getLocation(sva)
            sva += ltup[vivisect.L_SIZE]

def analyzeFunction(vw, funcva):
    seg = vw.getSegment(funcva)
    if seg == None:
        return

    segva, segsize, segname, segfname = seg

    if segname not in (".plt", ".plt.got"):
        return

    op = vw.parseOpcode(funcva)
    if op.iflags & envi.IF_BRANCH == 0:
        return

    oper0 = op.opers[0]
    opval = oper0.getOperAddr(op, None)

    loctup = vw.getLocation(opval)

    if loctup == None:
        return

    if loctup[vivisect.L_LTYPE] != vivisect.LOC_IMPORT: # FIXME: Why are some AMD64 IMPORTS showing up as LOC_POINTERs?
        vw.vprint("0x%x: %r != %r" % (funcva, loctup[vivisect.L_LTYPE], vivisect.LOC_IMPORT))
        return

    fname = vw.getName(opval)
    vw.makeName(funcva, "plt_%s" % fname, filelocal=True)
    vw.makeFunctionThunk(funcva, fname)

