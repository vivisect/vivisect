import logging
import vivisect

from . import elfplt

logger = logging.getLogger(__name__)

def analyze(vw):
    try:
        logger.info('ELFPLT late-analysis')

        for pltva, pltsz in elfplt.getPLTs(vw):
            logger.debug("PLT Section:  0x%x:%d", pltva, pltsz)
            # find functions currently defined in this PLT
            curplts = []
            for fva in vw.getFunctions():
                if pltva <= fva < (pltva+pltsz) and fva not in curplts:
                    logger.debug("PLT Function: 0x%x", fva)
                    curplts.append(fva)

            # now figure out the distance from function start to the GOT xref:
            heur = {}
            for fva in curplts:
                fsz = vw.getFunctionMeta(fva, 'Size')
                gotva, gotsz = elfplt.getGOT(vw, fva)

                offset = 0
                while offset < fsz:
                    locva, lsz, ltype, ltinfo = vw.getLocation(fva + offset)
                    xrefsfrom = vw.getXrefsFrom(locva)
                    for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                        if gotva <= xrto < gotva+gotsz:
                            offcnt = heur.get(offset, 0)
                            heur[offset] = offcnt + 1

                    offset += lsz

            if not len(heur):
                continue

            logger.debug("GOT/size: 0x%x/0x%x", gotva, gotsz)
            # if we have what we need... scroll through all the non-functioned area
            # looking for GOT-xrefs
            offbycnt = [(cnt, off) for off, cnt in heur.items()]
            offbycnt.sort(reverse=True)
            logger.debug("PLT Segment Data: %r", vw.getSegment(pltva))
            cnt, realoff = offbycnt[0]

            # now roll through the PLT space and look for GOT-references from 
            # locations that aren't in a function
            offset = 0
            while offset < pltsz:
                locva, lsz, ltype, ltinfo = vw.getLocation(pltva + offset)

                xrefsfrom = vw.getXrefsFrom(locva)
                logger.debug("loc: 0x%x   xrefs: %r", locva, xrefsfrom)
                toGOT = False
                for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                    if gotva <= xrto < gotva+gotsz:
                        # make sure we're pointing at a valid import
                        toloc = vw.getLocation(xrto)
                        if toloc is None:
                            continue

                        tlva, tlsz, tltype, tlinfo = toloc
                        if tltype != vivisect.LOC_IMPORT:
                            continue

                        toGOT = True

                if toGOT:
                    # we have an xref into the GOT and no function.  go!
                    funcstartva = locva - realoff
                    if vw.getFunction(locva) != funcstartva:
                        logger.debug("New PLT Function: 0x%x (GOT jmp: 0x%x)" % (funcstartva, locva))
                    vw.makeFunction(funcstartva)

                offset += lsz

            #import envi.interactive as ei; ei.dbg_interact(locals(), globals())

    except Exception as e:
        import sys
        sys.excepthook(*sys.exc_info())

