'''
Utilities for generating "archetecture independant" ASTs.
'''
from vivisect.const import *
from vivisect.symboliks.common import *

def wipeAstArch(symctx, symobjs, emu=None, wipeva=False):
    '''
    Given a symbolik analysis context, modify a set of
    symbolik states to be "arch independant" while
    maintaining register context awareness in a "portable"
    way...

    Goals:

        Given:
          ( arg0 + ecx ) * ( ebx + ebx )

        modify the AST such that register selection and
        order do *not* effect the solve values such that:

        == ( arg0 + ebx ) * ( ecx + ecx )
        != ( arg0 + ecx ) * ( ebx + ecx )
        != ( arg0 + ecx ) * ( ebx + eax )

        *while* maintaining the order independance of all
        appropriate operators.

        Result:
          ( arg0 + reg0 ) * ( reg1 + reg1 )

          NOTE: the key here is that "order" of regN generation
                is stable across symbolik states generated with
                different "order of occurance" of register access.

          ( ie, still == ( edx + edx ) * ( ecx + arg0 ) )

    Specify wipeva=True to similarly "replace" all virtual addresses
    within the AST.
    '''
    archemu = symctx.vw.getCachedEmu('sym:archind')

    # step one, create symid->reg mapping and replace all
    # sym vars that are regs with a constant value

    # for constants to map new symobj id -> oldsym
    idtova = {}
    # for registers to map new symobj id -> oldsym
    idtoold = {}

    # a tree walker to frob reg vars
    def normast(path, oldsym, ctx):
        # are we wipping away consts?
        if wipeva and oldsym.symtype == SYMT_CONST:
            if symctx.vw.isValidPointer(oldsym.value):
                # check for function thunks
                if symctx.vw.isFunction(oldsym.value):
                    api = symctx.vw.getFunctionMeta(oldsym.value, 'Thunk')
                    if api:
                        return Var(api, width=symctx.vw.psize)

                newobj = Var('piva_global',4)
                idtova[newobj._sym_id] = oldsym
                return newobj

        if oldsym.symtype != SYMT_VAR:
            return None

        # check if this is a register
        if archemu.getRegisterIndex(oldsym.name) is None:
            return None

        # do *not* change the var name below.  it's value is
        # intrinsic to the comparibility of results over time
        newobj = Var('archindreg', 4)  # norm all to 4...

        idtoold[newobj._sym_id] = oldsym
        return newobj

    # frob regs
    symobjs = [s.walkTree(normast) for s in symobjs]
    # force the solver cache to populate
    [s.solve(emu=emu) for s in symobjs]
    # retrieve all "position hashes" or whatever...
    vapos = []
    sympos = []

    def gatherpos(path, symobj, ctx):
        if idtova.get(symobj._sym_id) is not None:
            poshash = 'va:' + (':'.join(['%.8x' % s.solve(emu=emu) for s in path]))
            vapos.append((poshash, symobj._sym_id))
            return

        if idtoold.get(symobj._sym_id) is not None:
            poshash = 'sym:' + (':'.join(['%.8x' % s.solve(emu=emu) for s in path]))
            sympos.append((poshash, symobj._sym_id))
            return

    [s.walkTree(gatherpos) for s in symobjs]

    # sort them by the "order stabilized" "position hashes"
    vapos.sort()
    sympos.sort()

    # generate the variable mapping
    indregs = {}
    for poshash, symid in sympos:
        origreg = idtoold.get(symid).name
        indreg = indregs.get(origreg)
        if indreg is None:
            # do *not* modify this register name convention
            # (all previously calcualated results are only
            # comparable while these are the same. Additionally,
            # having the number "early" in the string, helps
            # spread the entropy further... (python hash)
            indreg = '%dindreg' % len(indregs)
            indregs[origreg] = indreg

    indvas = {}
    # Narchindva
    basename = "%darchindva"
    idx = 0
    for poshash, symid in vapos:
        origva = idtova.get(symid).value
        indva = indvas.get(origva)
        if indva is None:
            indva = basename % idx
            indvas[origva] = indva
            idx += 1

    # re-build the tree with the new "ind reg" vars
    def makeind(path, symobj, ctx):
        oldsym = idtoold.get(symobj._sym_id)
        if oldsym is not None:
            return Var(indregs.get(oldsym.name), 4)

        oldsym = idtova.get(symobj._sym_id)
        if oldsym is not None:
            obj = Var(indvas.get(oldsym.value), 4)
            ploc = symctx.vw.getLocation(oldsym.value)
            if ploc:
                va, size, ltype, tinfo = ploc
                if ltype == LOC_STRING or ltype == LOC_UNI:
                    obj._str_repr = symctx.vw.reprLocation(ploc)
            return obj
    symobjs = [s.walkTree(makeind) for s in symobjs]
    return symobjs
