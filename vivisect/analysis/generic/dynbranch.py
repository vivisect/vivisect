'''
Analysis module that attempts to deal with dynamic branches to discover new jump tables and functions
'''

import vivisect.const as vc
import vivisect.symboliks.analysis as vsa

# TODO: If a call is to an arg, and there's only one caller of the function, should we pseudo-inline
# that function (or try to symbolikally resolve the arguments and determine what the value there should be?


'''
General idea:
* symbolikally execute up to the dynamic branch
* if the value isn't discrete (like it's the result of an arg or something),

For both calls and jmps:
we need to deal with imports(They'll just show up as Var("import name")

To figure out:
* What if there are multiple paths to the dynamic branch (and there will be)
'''
def handleDynBranch(vw, va):
    # get the register we're dynamically branching off of
    op = vw.parseOpcode(va)
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
    # call eax
    # vtables?
    # lea eax, label
    # call [eax]
    # call [addr]
    def gatherPointers(path, cur, vw):
        if cur.symtype == vc.SYMT_CONST:
            if vw.isValidPointer(cur.value):
                pointers.append(cur.value)

    target = op.opers[0].repr(None)
    # For both calls and other branches, what if there's multiple operations that lead to the final result?
    # The called/jumped value could be a straight calculated value,
    # or it could be a pointer to a table of values
    # what about import calls?
    # discovered calls to exit process and abort and what not?
    # vtables?
    if dynbranch.efftype == vc.EFFTYPE_CALLFUNC:
        if str(dynbranch.funcsym) == target:
            # No effects were dragged through, so no point in trying to resolve further
            return False
        dynbranch.funcsym.walkTree(gatherPointers, ctx=vw)
    else:
        # if we're not a call, we need to hunt for the last set to the branch register
        if str(dynbranch.symobj) == target:
            return False
        dynbranch.symobj.walkTree(gatherPointers, ctx=vw)

    return
    # we could have already sectioned off this codeblock into it's own function if this is just a branch
    # and not a call
    # does a deref on a global memory address that we don't know if it's been written
    # to count as a dynamic branch?
    for ptr in pointers:
        # here is where we need to deal with things like tables, invalid jumps, etc
        print("wat")


def analyze(vw):
    return
    dynbranches = vw.getVaSetRows('DynamicBranches')
    for va, reprop, bflags in dynbranches:
        xrefs = vw.getXrefsFrom(va)
        if len(xrefs) == 0:
            handleDynBranch(vw, va)


if __name__ == '__main__':
    import sys
    import vivisect.tests.helpers as helpers
    vw = helpers.getTestWorkspace('windows', 'i386', 'openssl.exe')
    import pdb
    pdb.set_trace()
    handleDynBranch(vw, 0x459c12)
