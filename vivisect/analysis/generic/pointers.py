"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
"""
import logging
from vivisect.const import RTYPE_BASEPTR, LOC_POINTER

logger = logging.getLogger(__name__)

def analyze(vw):

    if vw.verbose:
        vw.vprint('...analyzing pointers.')

    # Let's analyze and Relocations we know are pointers
    for rva, rtype in vw.reloc_by_va.items():
        if rtype != RTYPE_BASEPTR:
            continue

        for xfr, xto, xtype, xinfo in vw.getXrefsFrom(rva):
            vw.analyzePointer(xto)

    # Now, we'll analyze the pointers placed by the file wrapper (ELF, PE, MACHO, etc...)
    for pva, tva, pname in vw.getVaSetRows('PointersFromFile'):
        if vw.getLocation(pva) is None:
            if tva is None:
                logger.info('making pointer 0x%x (%r)', pva, pname)
            else:
                logger.info('making pointer 0x%x -> 0x%x (%r)', pva, tva, pname)
            vw.makePointer(pva, tva, follow=True)

    for lva, lsz, lt, li in vw.getLocations(LOC_POINTER):
        tva = vw.readMemoryPtr(lva)
        if not vw.isValidPointer(tva):
            continue

        if vw.getLocation(tva) is not None:
            continue

        logger.info('following previously discovered pointer 0x%x -> 0x%x', lva, tva)
        try:
            vw.followPointer(tva)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (lva, tva))


    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            vw.followPointer(pval)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (addr, pval))
