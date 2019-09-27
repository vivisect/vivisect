'''
Analysis module that attempts to deal with dynamic branches to discover new jump tables and functions
'''

import vivisect.const as vc
import vivisect.symboliks.analysis as vsa
import vivisect.symboliks.common as vsc


def handleDynBranch(vw, va):
    # get the register we're dynamically branching off of
    op = vw.parseOpcode(va)
    fva = vw.getFunction(op.va)
    cbva = vw.getCodeBlock(va)

    # Symbolikally emulate inside of this codeblock only
    sym_ctx = vsa.getSymbolikAnalysisContext(vw)
    sym_path = sym_ctx.getSymbolikPaths(fva, paths=[[(cbva[0], None)]])
    emu, effects = sym_path.next()
    # I don't care about anything after the `call <reg>` or `jmp <reg>`
    # TODO: don't just filter the ones before the branch, also stop on calls
    effects = filter(lambda k: k.va <= op.va, effects)
    dynbranch = effects[-1]

    # No symbolik effects were dragged through inside this codeblock, so we still look like a `call eax`
    pointers = []
    def gatherPointers(path, cur, vw):
        if cur.symtype == vc.SYMT_CONST:
            if vw.isValidPointer(cur.value):
                pointers.append(cur.value)
    import pdb
    pdb.set_trace()
    target = op.opers[0].repr(None)
    # For both calls and other branches, what if there's multiple operations that lead to the final result?
    # And for both of them, it could be an calculated value, or it could be a pointer to a series of tables
    if dynbranch.efftype == vc.EFFTYPE_CALLFUNC:
        if str(dynbranch.funcsym) == target:
            # No effects were dragged through, so no point in trying to resolve further
            return False
        dynbranch.funcsym.walkTree(gatherPointers, ctx=vw)
    else:
        # if we're not a call, we need to hunt for the last set to the branch register
        sets = filter(lambda k: k.efftype == vc.EFFTYPE_SETVAR, effects)
        if not sets:
            return False
        breg = filter(lambda k: k.varname == target, sets)
        if not breg:
            return False
        lastset = breg[-1]

    import pdb
    pdb.set_trace()

    print("Done!")


def analyze(vw):
    dynbranches = vw.getVaSetRows('DynamicBranches')

    # db is tuple of (va, str of mnem, bflags of opcode)
    for va, reprop, bflags in dynbranches:
        handleDynBranch(vw, va)
