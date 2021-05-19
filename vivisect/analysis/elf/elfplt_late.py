import logging
import vivisect

from . import elfplt

logger = logging.getLogger(__name__)

def analyze(vw):
    logger.info('ELFPLT late-analysis')

    for pltva, pltsz in elfplt.getPLTs(vw):
        try:
            analyzePLT(vw, pltva, pltsz)

        except Exception as e:
            import sys
            sys.excepthook(*sys.exc_info())


def analyzePLT(vw, pltva, pltsz):
    logger.info("PLT Section:  0x%x:%d", pltva, pltsz)

    # find functions currently defined in this PLT
    curplts = []
    for fva in vw.getFunctions():
        if pltva <= fva < (pltva+pltsz) and fva not in curplts:
            logger.debug("existing PLT Function: 0x%x", fva)
            curplts.append(fva)

    curplts.sort()

    # now figure out the distance from function start to the GOT xref 
    # and between PLT functions
    lastva = pltva
    jmpheur = {}
    distanceheur = {}
    for fva in curplts:
        fsz = vw.getFunctionMeta(fva, 'Size')
        gotva, gotsz = elfplt.getGOT(vw, fva)

        offset = 0
        while offset < fsz:
            locva, lsz, ltype, ltinfo = vw.getLocation(fva + offset)
            xrefsfrom = vw.getXrefsFrom(locva)
            for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                if gotva <= xrto < gotva+gotsz:
                    offcnt = jmpheur.get(offset, 0)
                    jmpheur[offset] = offcnt + 1

            offset += lsz

        # capture distance between functions
        delta = fva - lastva
        distanceheur[delta] = distanceheur.get(delta, 0) + 1
        lastva = fva


    # GOT-XREF-Offset method
    if not len(jmpheur):
        logging.info("skipping analyzePLT(0x%x, 0x%x): no existing functions found", pltva, pltsz)

    else:
        # this seems to work for many PLT's, but only if the xref is identifiable 
        # without function analysis.  it fails on i386-pic code which uses ebx 
        # (which is handed into the call as a base address)
        logger.debug("GOT/size: 0x%x/0x%x", gotva, gotsz)

        # if we have what we need... scroll through all the non-functioned area
        # looking for GOT-xrefs
        offbycnt = [(cnt, off) for off, cnt in jmpheur.items()]
        offbycnt.sort(reverse=True)
        logger.debug("PLT Segment Data: %r", vw.getSegment(pltva))
        cnt, realoff = offbycnt[0]

        # now roll through the PLT space and look for GOT-references from 
        # locations that aren't in a function
        logger.warning("... analysis mode 1: GOT-XREF Offset")
        offset = 0
        while offset < pltsz:
            locva, lsz, ltype, ltinfo = vw.getLocation(pltva + offset)

            xrefsfrom = vw.getXrefsFrom(locva)
            toGOT = False
            for xrfr, xrto, xrtype, xrtinfo in xrefsfrom:
                if isGOT(vw, xrto):
                    # make sure we're pointing at a valid import
                    toloc = vw.getLocation(xrto)
                    if toloc is None:
                        continue

                    tlva, tlsz, tltype, tlinfo = toloc
                    if tltype not in (vivisect.LOC_POINTER, vivisect.LOC_IMPORT):
                        continue

                    toGOT = True

            logger.debug("loc: 0x%x   xrefs: %r (toGOT: %r)", locva, xrefsfrom, toGOT)
            if toGOT:
                # we have an xref into the GOT and no function.  go!
                funcstartva = locva - realoff
                if vw.getFunction(locva) != funcstartva:
                    logger.debug("New PLT Function: 0x%x (GOT jmp: 0x%x)" % (funcstartva, locva))

                    # if our intended location is not currently part of a PLT function, make it one
                    curfuncva = vw.getFunction(funcstartva)
                    if curfuncva is None or not isPLT(vw, curfuncva):
                        vw.makeFunction(funcstartva)
                    else:
                        logger.warning("attempting to make function at 0x%x, which is already a member of 0x%x",
                                funcstartva, vw.getFunction(funcstartva))

            offset += lsz


    # PLT-Func-Distance method
    if not len(distanceheur):
        logging.info("skipping analyzePLT(0x%x, 0x%x): no existing functions found", pltva, pltsz)

    else:
        ######## Now let's attempt to identify the smallest common distance between functions
        # what's the smallest distance between functions that
        logger.warning("... analysis mode 2: PLT-Func-Distance")
        curpltcnt = len(curplts)
        minimumbar = 1 + (curpltcnt // 100)

        # cull the heard.  our winner wants to be at least greater than one entry
        for delta, count in list(distanceheur.items()):
            if count < minimumbar:
                distanceheur.pop(delta)

            elif delta == 0:  # can't have 0.  skip the first PLT function
                distanceheur.pop(delta)

        workdist = list(distanceheur.items())
        workdist.sort()
        logger.warning(workdist)

        # first entry should be our guy...
        funcdist = workdist[0][0]
        logger.warning("funcdist: 0x%x", funcdist)

        # find starting point of two curplts this distance apart
        for idx in range(1, len(curplts)):
            if curplts[idx] - curplts[idx-1] == funcdist:
                break

        startidx = idx

        tmpva = curplts[idx]
        logger.debug("... backwards from... 0x%x", tmpva)
        op = vw.parseOpcode(tmpva)
        stdmnem = op.mnem
        # start there and go backwards
        while tmpva > pltva:
            logger.warn("tmpva: 0x%x", tmpva)
            # check if already in a PLT function
            curfunc = vw.getFunction(tmpva)
            if curfunc is not None and (curfunc == tmpva or isPLT(vw, curfunc)):
                #logger.debug('skip 0x%x: already function', tmpva)
                tmpva -= funcdist 
                continue

            # check if there's enough room for an even additional one beyond this (ie. the initial entry in the plt is slightly larger than a normal entry
            leftovers = tmpva - funcdist - pltva
            if leftovers != 0 and leftovers < funcdist:
                logger.debug('skip 0x%x: too close to beginning of PLT', tmpva)
                tmpva -= funcdist 
                continue
            
            # if standard start of plt mnemonic is different...
            op = vw.parseOpcode(tmpva)
            if op.mnem != stdmnem:
                logger.debug('skip 0x%x: WRONG MNEM! (is %r   should be: %r)', tmpva, op.mnem, stdmnem)
                tmpva -= funcdist 
                continue

            logger.info("New PLT Function! 0x%x", tmpva)
            vw.makeFunction(tmpva)

            tmpva -= funcdist 

        # now we go to the end of the PLT!
        tmpva = curplts[idx]
        logger.debug("... forwards from... 0x%x", tmpva)
        endva = pltva + pltsz
        while tmpva < endva:
            logger.warn("tmpva: 0x%x", tmpva)
            # check if already in a PLT function
            curfunc = vw.getFunction(tmpva)
            if curfunc is not None and (curfunc == tmpva or isPLT(vw, curfunc)):
                #logger.debug('skip 0x%x: already function', tmpva)
                tmpva += funcdist 
                continue

            # if standard start of plt mnemonic is different...
            op = vw.parseOpcode(tmpva)
            if op.mnem != stdmnem:
                logger.debug('skip 0x%x: WRONG MNEM! (is %r   should be: %r)', tmpva, op.mnem, stdmnem)
                tmpva += funcdist 
                continue

            logger.info("New PLT Function! 0x%x", tmpva)
            vw.makeFunction(tmpva)

            tmpva += funcdist 

        logger.warning("elfplt_late (done): pltva: 0x%x, %d", pltva, pltsz)
        #if input("PRESS ENTER (i for interactive)").startswith('i'):
        #    import envi.interactive as ei; ei.dbg_interact(locals(), globals())

def isGOT(vw, va):
    fname = vw.getFileByVa(va)
    gots = elfplt.getGOTs(vw)

    for gotva, gotsz in gots.get(fname):
        if gotva <= va < gotva+gotsz:
            return True

    return False

def isPLT(vw, va):
    plts = elfplt.getPLTs(vw)

    for pltva, pltsz in plts:
        if pltva <= va < pltva+pltsz:
            return True

    return False

