"""
A simple analysis module to detect import thunks.
"""

import vivisect.const as v_const


def analyzeFunction(vw, funcva):
    for fromva, tova, rtype, rflags in vw.getXrefsFrom(funcva, v_const.REF_CODE):

        # You goin NOWHERE!
        loc = vw.getLocation(tova)
        if loc is None:
            continue

        # FIXME this could check for thunks to other known function pointers...

        va, size, ltype, linfo = loc
        if ltype != v_const.LOC_IMPORT:
            continue

        vw.makeFunctionThunk(funcva, linfo)
