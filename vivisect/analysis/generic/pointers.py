"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
"""
from vivisect.const import RTYPE_BASEPTR

def analyze(vw):

    if vw.verbose:
        vw.vprint('...analyzing pointers.')

    # Let's analyze and Relocations we know are pointers
    for rva, rtype in vw.reloc_by_va.items():
        if rtype != RTYPE_BASEPTR:
            continue

        for xfr, xto, xtype in vw.getXrefsFrom(rva):
            vw.analyzePointer(xto)

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            vw.followPointer(pval)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (addr, pval))
