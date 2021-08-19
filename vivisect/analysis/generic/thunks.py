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

    General idea is that most function thunks (and not functions that just jump
    to a new function and never return) are usually one codeblock big. They do some
    setup, then jump/call/branch to a new place (and not just fall through).

    So we run through all the functions we know about, filter down to only the ones
    of a single codeblock. If the last instruction in it isn't a call or a branch, skip
    it.

    If we can then resolve where that branch/call is going to, set the new thing as a
    function thunk to it's target, and set the current function as a thunk.

    There is a slight catch in that there are certain functions we don't want to call
    makeFunctionThunk on (since that overrides the old name), since we may have already
    received a real name for it, so in that case, just set the metadata for it being
    a thunk and move on.
    '''
    for fva in vw.getFunctions():
        # Skip things that are already thunks
        if vw.isFunctionThunk(fva):
            continue

        blocks = vw.getFunctionBlocks(fva)
        if len(blocks) != 1:
            continue

        block = vw.getCodeBlock(fva)
        va = block[0] + block[1] - 1

        loc = vw.getLocation(va)
        if not loc:
            continue

        op = vw.parseOpcode(loc[0])
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
