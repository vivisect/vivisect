
"""
A function analysis module that will find code blocks in
functions by flow and xrefs.  This is basically a mandatory
module which should be snapped in *very* early by parsers.

"""

#FIXME this belongs in the core disassembler loop!
import sys
import envi
import vivisect
import collections

from vivisect.const import *

def analyzeFunction(vw, funcva):
    blocks = {}
    done = {}
    mnem = collections.defaultdict(int)
    todo = [ funcva, ]
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
        brefs.append( (start, True) )

        va = start

        # Walk forward through instructions until a branch edge
        while True:
            loc = vw.getLocation(va)

            # If it's not a location, terminate
            if loc is None:
                blocks[start] = va - start
                brefs.append((va, False))
                break

            lva,lsize,ltype,linfo = loc

            if ltype == LOC_POINTER:
                # pointer analysis mis-identified a pointer,
                # so clear and re-analyze instructions.

                vw.delLocation(lva)

                # assume we're adding a valid instruction, which is most likely.
                vw.makeCode(va)

                loc = vw.getLocation(va)
                if loc is None:
                    blocks[start] = va - start
                    brefs.append( (va, False) )
                    break

                lva,lsize,ltype,linfo = loc

            # If it's not an op, terminate
            if ltype != LOC_OP:
                blocks[start] = va - start
                brefs.append((va, False))
                break

            op = vw.parseOpcode(va)
            mnem[op.mnem] += 1
            size += lsize
            opcount += 1
            nextva = va+lsize

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
                todo.append(tova )

            # If it doesn't fall through, terminate (at nextva)
            if linfo & envi.IF_NOFALL:
                blocks[start] = nextva - start
                brefs.append( (nextva, False) )
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

        bsize = blocks[bva]
        vw.addCodeBlock(bva, bsize, funcva)
        bcnt += 1

    vw.setFunctionMeta(funcva, 'Size', size)
    vw.setFunctionMeta(funcva, 'BlockCount', bcnt)
    vw.setFunctionMeta(funcva, "InstructionCount", opcount)
    vw.setFunctionMeta(funcva, "MnemDist", mnem)
