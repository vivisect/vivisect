'''
Connect any Exports we have to Imports we may also have 
(most useful for multiple file workspaces)
'''
import logging
logger = logging.getLogger(__name__)

from vivisect import LOC_OP, REF_CODE

def analyze(vw):
    """
    Look for any "imported" symbols that are satisfied by current exports.
    Wire up the connection.

    Currently this is simply a pointer write at the location of the Import.
    If this behavior is ever insufficient, we'll want to track the special
    nature through the Export/Import events.
    """
    logger.info('linking Imports with Exports')
    # store old setting and set _supervisor mode (so we can write wherever
    # we want, regardless of permissions)
    with vw.getAdminRights():
        for iva, isz, itype, isym in vw.getImports():
            impfname, impsym = isym.split('.', 1)
            for eva, num, esym, efname in vw.getExports():
                if impsym != esym:
                    continue

                if impfname not in (efname, '*'):
                    continue

                if vw.isFunctionThunk(eva):
                    logger.info("Skipping Exported Thunk")
                    continue

                # file and symbol name match.  apply the magic.
                # do we ever *not* write in the full address at the import site?
                logger.debug("connecting Import 0x%x -> Export 0x%x (%r)", iva, eva, isym)
                vw.writeMemoryPtr(iva, eva)

                # remove the LOC_IMPORT and make it a Pointer instead
                vw.delLocation(iva)
                vw.makePointer(iva, follow=False) # don't follow, it'll be analyzed later?

                # store the former Import in a VaSet
                vw.setVaSetRow('ResolvedImports', (iva, isym, eva))

                # check if any xrefs to the import are branches and make code-xrefs for them
                for xrfr, xrto, xrt, xrflags in vw.getXrefsTo(iva):
                    loc = vw.getLocation(xrfr)
                    if not loc:
                        continue

                    lva, lsz, ltype, ltinfo = loc
                    if ltype != LOC_OP:
                        logger.warning("XREF not from an Opcode: 0x%x -> 0x%x  (%r)", lva, eva, loc)
                        continue

                    vw.addXref(lva, eva, REF_CODE)
                    logger.debug("addXref(0x%x -> 0x%x)", lva, eva)

