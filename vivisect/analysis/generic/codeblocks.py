"""
A function analysis module that will find code blocks in
functions by flow and xrefs.  This is basically a mandatory
module which should be snapped in *very* early by parsers.

"""
import logging
import collections

import envi

from vivisect.const import REF_CODE, LOC_POINTER, LOC_OP

logger = logging.getLogger(__name__)

def analyzeFunction(vw, funcva):
    blocks = {}
    done = {}
    mnem = collections.defaultdict(int)
    todo = [funcva, ]
    brefs = []
    size = 0
    opcount = 0
    while len(todo):

        start = todo.pop()

        # If we've hit code we've already done, keep going.
        if done.get(start):
            continue

        done[start] = True
        blocks[start] = 0
        brefs.append((start, True))

        va = start
        op = None
        arch = envi.ARCH_DEFAULT

        # Walk forward through instructions until a branch edge
        while True:
            loc = vw.getLocation(va)

            # If it's not a location, terminate
            if loc is None:
                blocks[start] = va - start
                brefs.append((va, False))
                break

            lva, lsize, ltype, linfo = loc

            if ltype == LOC_POINTER:
                # pointer analysis mis-identified a pointer,
                # so clear and re-analyze instructions.

                vw.delLocation(lva)

                # assume we're adding a valid instruction, which is most likely.
                if op is not None:
                    arch = op.iflags & envi.ARCH_MASK

                vw.makeCode(va, arch=arch, fva=funcva)

                loc = vw.getLocation(va)
                if loc is None:
                    blocks[start] = va - start
                    brefs.append((va, False))
                    break

                lva, lsize, ltype, linfo = loc

            # If it's not an op, terminate
            if ltype != LOC_OP:
                blocks[start] = va - start
                brefs.append((va, False))
                break

            try:
                op = vw.parseOpcode(va)
                mnem[op.mnem] += 1
            except Exception as e:
                logger.warning('Codeblock bad opcode at 0x%x, breaking on error %s', va, e)
                break
            size += lsize
            opcount += 1
            nextva = va + lsize

            # For each of our code xrefs, create a new target.
            branch = False
            xrefs = vw.getXrefsFrom(va, REF_CODE)
            for fromva, tova, rtype, rflags in xrefs:
                # We don't handle procedural branches here...
                if rflags & envi.BR_PROC:
                    continue

                # For now, we'll skip jmp [import] thunks...
                if rflags & envi.BR_DEREF:
                    continue

                branch = True
                todo.append(tova)

            # If it doesn't fall through, terminate (at nextva)
            if linfo & envi.IF_NOFALL:
                blocks[start] = nextva - start
                brefs.append((nextva, False))
                break

            # If we hit a branch, we are the end of a block...
            if branch:
                blocks[start] = nextva - start
                todo.append(nextva)
                break

            if vw.getXrefsTo(nextva, REF_CODE):
                blocks[start] = nextva - start
                todo.append(nextva)
                break

            va = nextva

    oldblocks = {va: size for (va, size, fva) in vw.getFunctionBlocks(funcva)}
    # we now have an ordered list of block references!
    brefs.sort()
    brefs.reverse()
    bcnt = 0
    while len(brefs):
        bva, isbegin = brefs.pop()
        if not isbegin:
            continue

        if len(brefs) == 0:
            break

        # So we don't add a codeblock if we're re-analyzing a function
        # (like during dynamic branch analysis)
        try:
            bsize = blocks[bva]
            tmpcb = vw.getCodeBlock(bva)
            # sometimes codeblocks can be deleted if owned by multiple functions
            if bva not in oldblocks or tmpcb is None:
                vw.addCodeBlock(bva, bsize, funcva)
            elif bsize != oldblocks[bva]:
                vw.delCodeBlock(bva)
                vw.addCodeBlock(bva, bsize, funcva)
            bcnt += 1
        except Exception as e:
            logger.warning('Codeblock analysis for 0x%.8x hit exception: %s', funcva, e)
            break

    vw.setFunctionMeta(funcva, 'Size', size)
    vw.setFunctionMeta(funcva, 'BlockCount', bcnt)
    vw.setFunctionMeta(funcva, 'InstructionCount', opcount)
    vw.setFunctionMeta(funcva, 'MnemDist', dict(mnem))
