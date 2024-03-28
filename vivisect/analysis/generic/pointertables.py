"""
A quick and dirty analysis pass looking for pointer arrays.  Pointers
in code regions are trixy because they might be immediate operands on
instructions.  However, if they are pointer-length aligned *and* back-to-back
they are probably really pointers...
"""

from vivisect.const import *


def handleArray(vw, plist):
    tlist = []

    for va, targ in plist:
        if vw.getLocation(va) is None:
            vw.makePointer(va)
        loctup = vw.getLocation(targ)
        if loctup is not None:
            ltype = loctup[L_LTYPE]
            if ltype not in tlist:
                tlist.append(ltype)

def analyze(vw):

    # FIXME this won't do anything on a second pass and it might be good if it did
    align = vw.arch.getPointerSize()
    rlen = vw.config.viv.analysis.pointertables.table_min_len

    plist = []
    for va, pval in vw.findPointers():

        if len(plist):

            lastva, lastptr = plist[-1]

            # If we maybe hit a pointer in the middle
            if lastva != va - align:
                nloc = vw.getLocation(lastva+align)
                while nloc is not None:
                    if nloc[L_LTYPE] != LOC_POINTER:
                        break
                    lva = nloc[L_VA]
                    plist.append((lva, vw.castPointer(lva)))
                    nloc = vw.getLocation(lva + nloc[L_SIZE])

            if lastva != va - align:
                if len(plist) > rlen:
                    handleArray(vw, plist)
                plist = []

        plist.append((va,pval))

    # Handle possible last plist
    if len(plist) > rlen:
        handleArray(vw, plist)
