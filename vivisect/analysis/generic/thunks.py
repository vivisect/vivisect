import envi
import vivisect.const as v_const


def analyzeFunction(vw, funcva):
    '''
    Quick n' dirty to find import thunks.
    '''
    for fromva, tova, rtype, rflags in vw.getXrefsFrom(funcva, v_const.REF_CODE):

        # You goin NOWHERE!
        loc = vw.getLocation(tova)
        if loc is None:
            continue

        va, size, ltype, linfo = loc
        if ltype != v_const.LOC_IMPORT:
            continue

        vw.makeFunctionThunk(funcva, linfo)


def analyze(vw):
    '''
    Find function thunks that point to other function that aren't imports
    '''
    for fva in vw.getFunctions():
        # Skip things that are already thunks
        if vw.isFunctionThunk(fva):
            continue

        op = vw.parseOpcode(fva)
        if not op.iflags & envi.IF_BRANCH and not op.iflags & envi.IF_CALL:
            continue

        branches = op.getBranches()
        if len(branches) != 1:
            continue

        bva, bflags = branches[0]
        if not vw.isFunction(bva):
            continue

        if bflags & envi.BR_FALL:
            continue

        va, size, ltype, linfo = vw.getLocation(fva)
        tname = vw.getName(bva)
        oldname = vw.getName(fva)

        # mark it as a function thunk, but if it has an actual name (like xcharalloc in
        # chgrp), don't override the actual, given name
        if oldname == 'sub_0%x' % va:
            vw.makeFunctionThunk(fva, tname)
        else:
            vw.setFunctionMeta(fva, 'Thunk', tname)
