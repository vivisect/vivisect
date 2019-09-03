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

    done = []

    # Let's analyze Relocations we know are pointers
    for rva, rtype in vw.reloc_by_va.items():
        if rtype != RTYPE_BASEPTR:
            continue

        for xfr, xto, xtype, xinfo in vw.getXrefsFrom(rva):
            vw.analyzePointer(xto)
            done.append((xfr, xto))
            logger.info('pointer(1): 0x%x -> 0x%x', xfr, xto)

    # Now, we'll analyze the pointers placed by the file wrapper (ELF, PE, MACHO, etc...)
    for pva, tva, fname, pname in vw.getVaSetRows('PointersFromFile'):
        if vw.getLocation(pva) is None:
            if tva is None:
                logger.info('making pointer 0x%x (%r)', pva, pname)
            else:
                logger.info('making pointer 0x%x -> 0x%x (%r)', pva, tva, pname)
            vw.makePointer(pva, tva, follow=True)
            done.append((pva, tva))
            logger.info('pointer(2): 0x%x -> 0x%x', pva, tva)

    for lva, lsz, lt, li in vw.getLocations(LOC_POINTER):
        tva = vw.readMemoryPtr(lva)
        if not vw.isValidPointer(tva):
            continue

        if vw.getLocation(tva) is not None:
            continue

        logger.info('following previously discovered pointer 0x%x -> 0x%x', lva, tva)
        try:
            vw.followPointer(tva)
            done.append((lva, tva))
            logger.info('pointer(3): 0x%x -> 0x%x', lva, tva)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (lva, tva))


    # Now, lets find likely free-hanging pointers
    for addr, pval in vw.findPointers():
        if vw.isDeadData(pval):
            continue
        try:
            vw.followPointer(pval)
            done.append((addr, pval))
            logger.info('pointer(4): 0x%x -> 0x%x', addr, pval)
        except Exception:
            if vw.verbose:
                vw.vprint("followPointer() failed for 0x%.8x (pval: 0x%.8x)" % (addr, pval))

    # Now let's see what these guys should be named (if anything)
    for ptr, tgt in done:
        pname = vw.getName(ptr)
        if pname is not None:
            logger.info('skipping renaming of 0x%x (%r)', ptr, pname)
            continue

        tgtname = vw.getName(tgt)
        if tgtname is not None:
            name = _addNamePrefix(vw, tgtname, tgt, 'ptr', '_') + '_%.8x' % ptr
            logger.info('   name(0x%x): %r  (%r)', tgt, tgtname, name)
            vw.makeName(ptr, name)


def _getNameParts(vw, name, va):
    fpart = None
    npart = name
    vapart = None
    fname = vw.getFileByVa(va)
    vastr = '_%.8x' % va

    if name.startswith(fname + '.'):
        fpart, npart = name.split('.', 1)
    elif name.startswith('*.'):
        skip, npart = name.split('.', 1)

    if npart.endswith(vastr) and not npart == 'sub' + vastr:
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
        name = fpart + '.' + joinstr.join([prefix, npart]) + '_%s' % vapart
    logger.debug('addNamePrefix: %r %r %r -> %r', fpart, npart, vapart, name)
    return name
