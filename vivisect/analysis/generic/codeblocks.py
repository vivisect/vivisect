"""
A function analysis module that will find code blocks in
functions by flow and xrefs.  This is basically a mandatory
module which should be snapped in *very* early by parsers.

"""
import logging
import collections

import envi
import envi.common as e_cmn

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

            if loc is not None:
                lva, lsize, ltype, linfo = loc
            else:
                ltype = None

            # Get the instruction that has been parsed out for this location
            # already, or parse it for the first time now. If an instruction
            # has already been decoded in this block use the ARCH type from the
            # previous instruction, otherwise DEFAULT
            if op is not None:
                arch = op.iflags & envi.ARCH_MASK

            try:
                op = vw.parseOpcode(va, arch=arch)
            except Exception as e:
                logger.warning('Codeblock exception at 0x%x, breaking on error %s', va, e)

                # Save the block up until this location
                blocks[start] = va - start
                brefs.append((va, False))
                break

            if ltype == LOC_POINTER and op is not None:
                # pointer analysis mis-identified a pointer, but this is an
                # valid instruction so delete the pointer location and turn this
                # address into code.

                # This location used to be a pointer but we need to turn it into
                # a code block
                logger.log(e_cmn.MIRE, 'Changing address 0x%x from pointer to code', va)
                vw.delLocation(va)

                # Mark ltype as None so that this address is turned into an
                # instruction
                ltype = None

            if ltype is None and op is not None:
                # Now make this address an instruction and associate this
                # location with this function
                vw.makeCode(va, arch=arch, fva=funcva)

                loc = vw.getLocation(va)
                if loc is not None:
                    # Grab the new location values
                    lva, lsize, ltype, linfo = loc

            # If it's not an op, terminate
            if ltype != LOC_OP:
                blocks[start] = va - start
                brefs.append((va, False))
                break

            # Track the mnemonic
            mnem[op.mnem] += 1

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
                # If this is not a location yet, try to make it code and then
                # attach it to the function
                if vw.getLocation(bva) is None:
                    vw.makeCode(bva, arch=arch, fva=funcva)
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
