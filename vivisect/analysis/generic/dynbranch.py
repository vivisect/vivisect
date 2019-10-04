'''
General idea:
* symbolikally execute up to the dynamic branch
* if the value isn't discrete (like it's the result of an arg or something),

We're typically fairly good at dragging through dynamic function calls, except in the case of the results of
another function (cross function solving a super hairy problem that is out of scope for this),
so this will probably just deal with dynamic branches (set a reg in one instruction,
and then jmp off the value of that register later)
'''

import envi
import vivisect.const as vc
import vivisect.symboliks.analysis as vsa


def getLongestLine(vw, g, va, blim=25):
    '''
    From the codeblock that holds this va, traverse *up* the graph till we get to a codeblock that has
    multiple xrefs to it.

    This ultimately exists because it's very possible to start to analyze a function that hits a path
    explosion, and determining at what point we cut off analysis is a mess. So only analyze the longest
    straight line path up a chain of codeblocks
    '''
    fva = vw.getFunction(va)
    cbva, cbsize, cbfunc = vw.getCodeBlock(va)
    node = g.getNode(cbva)
    refs = g.getRefsTo(node)
    chain = [(cbva, None)]

    while len(refs) == 1 and cbfunc == fva and len(chain) < blim:
        eid, fromva, tova, _ = refs[0]
        cbva, _, cbfunc = vw.getCodeBlock(fromva)

        node = g.getNode(cbva)
        refs = g.getRefsTo(node)

        chain.pop()
        chain += [(tova, eid), (fromva, None)]
    chain.reverse()

    return chain


def handleDynBranch(vw, va):
    op = vw.parseOpcode(va)
    if not op.iflags & envi.IF_BRANCH:
        return False

    fva = vw.getFunction(op.va)
    sym_ctx = vsa.getSymbolikAnalysisContext(vw)
    g = sym_ctx.getSymbolikGraph(fva)
    chain = getLongestLine(vw, g, va)
    target = op.opers[0].repr(None)
    emu, effects = sym_ctx.getSymbolikPaths(fva, graph=g, paths=[chain]).next()

    # No symbolik effects were dragged through inside this codeblock, so we still look like a `call eax`
    symvar = emu.getSymVariable(str(target))
    if str(symvar) == str(target):
        return

    pointers = []

    def gatherPointers(path, cur, vw):
        if cur.symtype == vc.SYMT_CONST:
            if vw.isValidPointer(cur.value):
                pointers.append(cur.value)

    symvar.walkTree(gatherPointers, ctx=vw)

    # we could have already sectioned off this codeblock into it's own function if this is just a branch
    # and not a call
    # does a deref on a global memory address that we don't know if it's been written
    # to count as a dynamic branch?
    for ptr in pointers:
        # So this is not guaranteed to be a table. It could just be a direct pointer
        # to a new codeblock
        newloc = vw.castPointer(ptr)
        # if our pointer leads us to another pointer, we probably are at a jump table
        if vw.isValidPointer(newloc):
            vw.makeJumpTable(op, ptr)
        else:
            vw.addXref(op.va, ptr, vc.REF_PTR)

        for xrfrom, xrto, xrtype, xinfo in vw.getXrefsFrom(op.va):
            if xrto == ptr:
                continue
            vw.makeCode(xrto)

    for name, fmod in vw.fmods.items():
        fmod.analyzeFunction(vw, fva)


def analyze(vw):
    dynbranches = vw.getVaSetRows('DynamicBranches')
    for va, reprop, bflags in dynbranches:
        xrefs = vw.getXrefsFrom(va)
        if len(xrefs) == 0:
            handleDynBranch(vw, va)
