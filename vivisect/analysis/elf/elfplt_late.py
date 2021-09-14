'''
Late-PLT analysis.

During codeflow analysis, we detect PLT entries organically (and consequently
*accurately*), but often not all of them.  This analysis module applies a few
different algorithms to identify the ones which were not discovered during
autoanalysis.

Formerly, we attempted to do this analysis before all other code analysis
but due to so many varieties of PLT creation by different compilers on
numerous hardware platforms and OSes, that method lead to many errors in PLT-
identification, often hampering vital parts of vulnerability-research tools.
We finally pulled the plug on preemptive analysis, in favor of letting auto-
analysis identify "truth" and then filling in the gaps.
'''


import logging
import vivisect
import envi.common as e_cmn

from . import elfplt

logger = logging.getLogger(__name__)

def analyze(vw):
    logger.info('ELFPLT late-analysis')

    for pltva, pltsz in elfplt.getPLTs(vw):
        try:
            analyzePLT(vw, pltva, pltsz)

        except Exception as e:
            logger.warning("Error in PLT-late analysis: %r", e, exc_info=True)


def analyzePLT(vw, pltva, pltsz):
    '''
    Analyze a specific PLT section (there are often more than one and they often
    different in format)

    We make use of two different algorithms for each.
    The first algorithm measures the distance from the start of known good PLT
    functions and the GOT-referencing branch.  The only weakness is that this
    method requires that the xref to the GOT is already identified (without
    throwing and emulator in there).

    The second algorithm measures the distance between known good PLT entries
    and then attempts to identify divisors (up to 16 splits) which would make
    more than one PLT function fit between them.  These attempted splits are
    validated using heuristics of the potential functions which would be created
    by the division.  PLT entries in the same PLT section are incredibly similar
    (not including the LazyLoader sometimes found at the beginning of a PLT)
    '''
    logger.info("PLT Section -  Address: 0x%x  Size: %d", pltva, pltsz)
    gotva = gotsz = None
    fname = vw.getFileByVa(pltva)

    # find functions currently defined in this PLT
    curpltset = set()
    for fva in vw.getFunctions():
        if pltva <= fva < (pltva+pltsz) and fva not in curpltset:
            logger.debug("existing PLT Function: 0x%x", fva)
            curpltset.add(fva)

    curplts = list(curpltset)
    curplts.sort()

    if len(curplts):    # make sure we have *any* functions
        # just make the first thing a function.  this should take care of any LazyLoader
        # or at the very least, the first PLT entry.  it should also keep us from backing
        # up too far during PLT-Func-Distance algorithm.
        logger.debug('analyzePLT(0x%x, 0x%x): making first location the PLT into a function', pltva, pltsz)
        vw.makeFunction(pltva)

    # now figure out the distance from function start to the GOT xref 
    # and between PLT functions
    lastva = pltva
    jmpheur = {}
    distanceheur = {}
    for fva in curplts:
        fsz = vw.getFunctionMeta(fva, 'Size')
        gotva, gotsz = elfplt.getGOTByFilename(vw, fname)

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

    if None not in (gotva, gotsz):
        logger.debug("GOT/size: 0x%x/0x%x", gotva, gotsz)

    # GOT-XREF-Offset method
    if len(jmpheur):
        fillPLTviaGOTXrefs(vw, jmpheur, pltva, pltsz)

    else:
        logging.info("analyzePLT(0x%x, 0x%x) skipping GOT-XREF-Offset method: no existing functions found", pltva, pltsz)

    # PLT-Func-Distance method
    if len(distanceheur):
        fillPLTGaps(vw, curplts, distanceheur, pltva, pltsz)

    else:
        logging.info("skipping analyzePLT(0x%x, 0x%x) (PLT-Func-Distance method): no existing functions found", pltva, pltsz)

    logger.info("elfplt_late (done): pltva: 0x%x, %d", pltva, pltsz)


def fillPLTviaGOTXrefs(vw, jmpheur, pltva, pltsz):
    '''
    This PLT-placement algorithm measures the distance from the start of known good
    PLT functions and the GOT-referencing branch.  The only weakness is that this
    method requires that the xref to the GOT is already identified (without
    throwing and emulator in there).

    This method seems to work for many PLT's, but only if the xref is identifiable
    without function analysis.  it fails on i386-pic code which uses ebx  (which
    is handed into the call as a base address)
    '''
    # if we have what we need... scroll through all the non-functioned area
    # looking for GOT-xrefs
    offbycnt = [(cnt, off) for off, cnt in jmpheur.items()]
    offbycnt.sort(reverse=True)
    logger.debug("PLT Segment Data: %r", vw.getSegment(pltva))
    cnt, realoff = offbycnt[0]

    # now roll through the PLT space and look for GOT-references from 
    # locations that aren't in a function
    logger.info("Scanning for Xrefs into the GOT to determine PLT function starts")
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
                logger.debug("New PLT Function: 0x%x (GOT jmp: 0x%x)", funcstartva, locva)

                # if our intended location is not currently part of a PLT function, make it one
                curfuncva = vw.getFunction(funcstartva)
                if curfuncva is None or not isPLT(vw, curfuncva):
                    vw.makeFunction(funcstartva)
                else:
                    logger.debug("attempting to make function at 0x%x, which is already a member of 0x%x",
                            funcstartva, vw.getFunction(funcstartva))

        offset += lsz


def fillPLTGaps(vw, curplts, distanceheur, pltva, pltsz):
    '''
    This PLT-placement algorithm measures the distance between known good PLT entries
    and then attempts to identify divisors (up to 16 splits) which would make
    more than one PLT function fit between them.  These attempted splits are
    validated using heuristics of the potential functions which would be created
    by the division.  PLT entries in the same PLT section are incredibly similar
    (not including the LazyLoader sometimes found at the beginning of a PLT)
    '''
    ######## let's attempt to identify the smallest common distance between functions
    # what's the smallest distance between functions that
    logger.info("Using known good PLT entries to fill in the rest of the PLT (based on gaps)")
    curpltcnt = len(curplts)
    minimumbar = 1 + (curpltcnt // 100)

    # cull the herd.  our winner wants to be at least greater than one entry
    for delta, count in list(distanceheur.items()):
        if count < minimumbar:
            distanceheur.pop(delta)

        elif delta == 0:  # can't have 0.  skip the first PLT function
            distanceheur.pop(delta)

    workdist = list(distanceheur.items())
    workdist.sort()

    if not len(workdist):
        logger.info('... bailing, no existing PLT functions in this section to compare to...')

    else:
        # first entry should be our guy...
        funcdist = workdist[0][0]
        logger.debug("funcdist: 0x%x", funcdist)

        idx = getGoodIndex(curplts, funcdist)
        fva = curplts[idx]

        ### magic check:  we are working off incomplete data... it's completely possible our
        # gap measurement is twice as big as it should be (or 3 times).  how to check is 
        # where the magic comes in...
        funcsz = vw.getFunctionMeta(fva, 'Size')
        for divisor in range(funcdist, 0, -1):
            logger.log(e_cmn.SHITE, 'attempting to divide funcdist (0x%x) by %d', funcdist, divisor)

            # does the gap between functions support splitting?
            if funcdist < (divisor * funcsz):
                logger.log(e_cmn.SHITE, '.. not big enough')
                continue

            newdist = funcdist // divisor
            # does the funcdist split evenly?
            if newdist * divisor != funcdist:
                logger.log(e_cmn.SHITE, ".. doesn't divide evenly(newdist: 0x%x  divisor: 0x%x   funcdist: 0x%x)", newdist, divisor, funcdist)
                continue

            # do the opcodes support this size split?
            if not compareFuncs(vw, fva, fva + newdist, funcsz):
                logger.log(e_cmn.SHITE, ".. functions don't match!")
                continue

            break

        # should end up dividing by 1 if not divisible
        if divisor > 1:
            logger.info("dividing our lowest function (0x%x) distance by %d", funcdist, divisor)
            funcdist //= divisor

        idx = getGoodIndex(curplts, funcdist)

        tmpva = curplts[idx]
        logger.debug("... backwards from... 0x%x", tmpva)
        op = vw.parseOpcode(tmpva)
        stdmnem = op.mnem
        # start there and go backwards
        while tmpva > pltva:
            logger.log(e_cmn.SHITE, "tmpva: 0x%x", tmpva)
            # check if already in a PLT function (ignore if it's part of some other func)
            curfunc = vw.getFunction(tmpva)
            if curfunc is not None and (curfunc == tmpva or isPLT(vw, curfunc)):
                #logger.debug('skip 0x%x: already function', tmpva)
                tmpva -= funcdist 
                continue

            # check if there's enough room for an even additional one beyond this 
            # (ie. the initial entry in the plt is slightly larger than a normal entry
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
            logger.log(e_cmn.SHITE, "tmpva: 0x%x", tmpva)
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

def isGOT(vw, va):
    '''
    Check a VA to see if it resides in one of this file's GOT sections
    (uses elfplt.getGOTs()
    '''
    fname = vw.getFileByVa(va)
    gots = elfplt.getGOTs(vw)

    for gotva, gotsz in gots.get(fname):
        if gotva <= va < gotva+gotsz:
            return True

    return False

def isPLT(vw, va):
    '''
    Check a VA to see if it resides in one of this workspace's PLT sections
    (uses elfplt.getPLTs()
    '''
    plts = elfplt.getPLTs(vw)

    for pltva, pltsz in plts:
        if pltva <= va < pltva+pltsz:
            return True

    return False

def getGoodIndex(curplts, funcdist):
    '''
    Roll through a list of PLT entires looking for two that are <funcdist> apart
    '''
    # find starting point of two curplts this distance apart
    for idx in range(1, len(curplts)):
        if curplts[idx] - curplts[idx-1] == funcdist:
            return idx

    return idx

def compareFuncs(vw, fva1, fva2, funcsz):
    '''
    Compare two potential PLT functions... make sure they share a similar pattern.
    They should be nearly identical
    '''
    offset = 0
    while offset < funcsz:
        va1 = fva1 + offset
        va2 = fva2 + offset

        loc1 = vw.getLocation(va1)
        # if loc1 hits a None bail out
        if loc1 is None:
            logger.log(e_cmn.SHITE, '... hit a None location in fva1')
            return False

        lva, lsz, ltype, ltinfo = loc1
        try:
            op1 = vw.parseOpcode(va1)
            op2 = vw.parseOpcode(va2)
       
            if op1.mnem != op2.mnem:
                logger.log(e_cmn.SHITE, "fva1 op mnem (%r) doesn't match fva2 (%r) at offset %d", op1.mnem, op2.mnem, offset)
                return False

            if len(op1.opers) != len(op2.opers):
                logger.log(e_cmn.SHITE, "fva1 op operlen (%r) doesn't match fva2 (%r) at offset %d", op1.opers, op2.opers, offset)
                return False

            for oidx in range(len(op1.opers)):
                oper1 = op1.opers[oidx]
                oper2 = op2.opers[oidx]

                if oper1.__class__ != oper2.__class__:
                    logger.log(e_cmn.SHITE, "fva1 op operclass (%r) doesn't match fva2 (%r) at offset %d", oper1, oper2, offset)
                    return False
                
        except Exception as e:
            # if it fails, we bails
            logger.debug('FAILURE comparing 0x%x and 0x%x: %r', fva1, fva2, e)
            return False

        offset += lsz

    return True

