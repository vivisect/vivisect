
"""
A simple analysis module to detect import thunks.
"""

import envi
import vivisect

def analyzeFunction(vw, funcva):

    for fromva, tova, rtype, rflags in vw.getXrefsFrom(funcva, vivisect.REF_CODE):

        # You goin NOWHERE!
        loc = vw.getLocation(tova)
        if loc == None:
            continue

        # FIXME this could check for thunks to other known function pointers...

        va, size, ltype, linfo = loc
        if ltype != vivisect.LOC_IMPORT:
            continue

        vw.makeFunctionThunk(funcva, linfo)

