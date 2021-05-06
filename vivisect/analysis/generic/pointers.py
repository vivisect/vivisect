"""
generic workspace analysis module to seek through the undiscovered
country looking for pointers to interesting things.

in a previous life, this analysis code lived inside VivWorkspace.analyze()
"""
import sys
import logging
from vivisect.const import RTYPE_BASEPTR, LOC_POINTER, L_LTYPE

logger = logging.getLogger(__name__)

def analyze(vw):

    logger.info('...analyzing pointers.')

    done = []

    # Let's analyze Relocations we know are pointers
    for rva, rtype in vw.reloc_by_va.items():
        if rtype != RTYPE_BASEPTR:
            continue

        for xfr, xto, xtype, xinfo in vw.getXrefsFrom(rva):
            logger.debug('pointer(1): 0x%x -> 0x%x', xfr, xto)
            vw.analyzePointer(xto)
            done.append((xfr, xto))

    # Now, we'll analyze the pointers placed by the file wrapper (ELF, PE, MACHO, etc...)
    for pva, tva, fname, pname in vw.getVaSetRows('PointersFromFile'):
        if vw.getLocation(pva) is None:
            if tva is None:
                logger.debug('making pointer(2) 0x%x (%r)', pva, pname)
            else:
                logger.debug('making pointer(2) 0x%x -> 0x%x (%r)', pva, tva, pname)
            vw.makePointer(pva, tva, follow=True)
            done.append((pva, tva))

    for lva, lsz, lt, li in vw.getLocations(LOC_POINTER):
        tva = vw.readMemoryPtr(lva)
        if not vw.isValidPointer(tva):
            continue

        if vw.getLocation(tva) is not None:
            # event if it's a pointer, we may not have made a name for it
            if vw.getName(lva) is None:
                done.append((lva, tva))
            continue

        logger.debug('following previously discovered pointer 0x%x -> 0x%x', lva, tva)
        try:
            logger.debug('pointer(3): 0x%x -> 0x%x', lva, tva)
            vw.followPointer(tva)
            done.append((lva, tva))
        except Exception as e:
            logger.error('followPointer() failed for 0x%.8x (pval: 0x%.8x) (err: %s)', lva, tva, e)

    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            logger.debug('pointer(4): 0x%x -> 0x%x', addr, pval)
            vw.makePointer(addr, follow=True)
            done.append((addr, pval))
        except Exception as e:
            logger.error('makePointer() failed for 0x%.8x (pval: 0x%.8x) (err: %s)', addr, pval, e)

    # Now let's see what these guys should be named (if anything)
    for _, _ in done:
        for ptr, tgt in done:
            try:
                pname = vw.getName(ptr)
                if pname is not None:
                    logger.debug('skipping renaming of ptr 0x%x (currently: %r)', ptr, pname)
                    continue

                loc = vw.getLocation(ptr)
                if loc is not None and loc[L_LTYPE] != LOC_POINTER:
                    logger.debug('skipping naming of 0x%x (no longer a pointer: %s)', ptr, vw.reprLocation(loc))
                    continue
                tgtname = vw.getName(tgt)
                if tgtname is not None:
                    name = vw._addNamePrefix(tgtname, tgt, 'ptr', '_') + '_%.8x' % ptr
                    logger.debug('0x%x: adding name prefix: %r  (%r)', tgt, tgtname, name)
                    vw.makeName(ptr, name)
                else:
                    logger.debug('0x%x: Skipping naming due to no target name' % tgt)
            except Exception as e:
                logger.error('naming failed (0x%x -> 0x%x), (err: %s)', ptr, tgt, e)
                sys.excepthook(*sys.exc_info())
