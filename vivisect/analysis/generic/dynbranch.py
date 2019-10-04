'''
General idea:
* symbolikally execute up to the dynamic branch
* if the value isn't discrete (like it's the result of an arg or something),

To figure out:
* What if there are multiple paths to the dynamic branch (and there will be)

We're typically fairly good at dragging through functions, except in the case of the results of
another function (cross function solving a super hairy problem that is out of scope for this),
so this will probably just deal with dynamic branches (set a reg in one instruction,
and then jmp off the value of that register later)
'''

import envi
import vivisect.const as vc
import vivisect.symboliks.analysis as vsa


def handleDynBranch(vw, va):
    # get the register we're dynamically branching off of
    op = vw.parseOpcode(va)
    if not op.iflags & envi.IF_BRANCH:
        return False
    fva = vw.getFunction(op.va)

    # TODO: Translate only inside this code block? Would be a nice perf upgrade
    # Symbolikally emulate inside of this codeblock only
    sym_ctx = vsa.getSymbolikAnalysisContext(vw)
    sym_path = sym_ctx.getSymbolikPathsTo(fva, va)
    emu, effects = sym_path.next()
    # I don't care about anything after the `call <reg>` or `jmp <reg>`
    # TODO: don't just filter the ones before the branch, also stop on calls
    effects = filter(lambda k: k.va <= op.va, effects)
    dynbranch = effects[-1]

    # No symbolik effects were dragged through inside this codeblock, so we still look like a `call eax`
    pointers = []

    # jmp eax
    # jmp [eax]
    # vtables?
    def gatherPointers(path, cur, vw):
        if cur.symtype == vc.SYMT_CONST:
            if vw.isValidPointer(cur.value):
                pointers.append(cur.value)

    target = op.opers[0].repr(None)

    if str(dynbranch.symobj) == str(target):
        return False
    dynbranch.symobj.walkTree(gatherPointers, ctx=vw)

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
