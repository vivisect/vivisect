"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
"""
import logging
from vivisect.const import RTYPE_BASEPTR, LOC_POINTER

logger = logging.getLogger(__name__)

def analyze(vw):

    logger.info('...analyzing pointers.')

    done = {}

    # Let's analyze Relocations we know are pointers
    for rva, rtype in vw.reloc_by_va.items():
        if rtype != RTYPE_BASEPTR:
            continue

        for xfr, xto, xtype, xinfo in vw.getXrefsFrom(rva):
            logger.debug('pointer(1): 0x%x -> 0x%x', xfr, xto)
            vw.analyzePointer(xto)
            if vw.isLocType(xfr, LOC_POINTER):
                done[xfr] = xto

    # Now, we'll analyze the pointers placed by the file wrapper (ELF, PE, MACHO, etc...)
    for pva, tva, fname, pname in vw.getVaSetRows('PointersFromFile'):
        if vw.getLocation(pva) is None:
            if tva is None:
                logger.debug('making pointer(2) 0x%x (%r)', pva, pname)
            else:
                logger.debug('making pointer(2) 0x%x -> 0x%x (%r)', pva, tva, pname)
            vw.makePointer(pva, tva, follow=True)
            done[pva] = tva

    for lva, lsz, lt, li in vw.getLocations(LOC_POINTER):
        tva = vw.readMemoryPtr(lva)
        if not vw.isValidPointer(tva):
            continue

        if vw.getLocation(tva) is not None:
            # event if it's a pointer, we may not have made a name for it
            if vw.getName(lva) is None:
                done[lva] = tva
            continue

        logger.debug('following previously discovered pointer 0x%x -> 0x%x', lva, tva)
        try:
            logger.debug('pointer(3): 0x%x -> 0x%x', lva, tva)
            vw.followPointer(tva)
            done[lva] = tva
        except Exception as e:
            logger.error('followPointer() failed for 0x%.8x (pval: 0x%.8x) (err: %s)', lva, tva, e)

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            logger.debug('pointer(4): 0x%x -> 0x%x', addr, pval)
            vw.makePointer(addr, follow=True)
            done[addr] = pval
        except Exception as e:
            logger.error('makePointer() failed for 0x%.8x (pval: 0x%.8x) (err: %s)', addr, pval, e)

    refs = {v: k for k, v in done.items()}
    while refs:
        tgt, ptr = refs.popitem()
        while ptr:
            pname = vw.getName(ptr)
            if pname:
                break
            if not vw.isLocType(ptr, LOC_POINTER):
                break

            tgtname = vw.getName(tgt)
            if tgtname:
                name = vw._addNamePrefix(tgtname, tgt, 'ptr', '_') + '_%.8x' % ptr
                logger.debug('0x%x: adding name prefix: %r  (%r)', tgt, tgtname, name)
                vw.makeName(ptr, name)
                tgt = ptr
                ptr = refs.pop(tgt, None)
            else:
                ptr = None
