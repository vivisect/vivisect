
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.

This analysis module attempts to be platform- and architecture-agnostic.  
Different conpilers make that more or less difficult.  We're jumping over 
numerous hurdles to get accuracy everywhere without having different 
analysis modules for each achitecture and compiler.

First of all, we start out by attempting to analyze all PLT sections
(.plt and .plt.got) before any other code is run.  This requires us to
attempt to lay down Code locations all the way through the section.
Some architectures place pointers in the section which are referenced
by code in earlier functions, as a "literal pool."  

We start off analysis by identifying all the Unconditional Branches which
don't point to the beginning of the section.  Lazy loading typically ends 
up with some tricks of code places a value for the function in a given 
register, and branching to a trampoline function at the beginning of the 
section, which then branches to the LIBC dynamic loader.  The other 
Unconditional Branches should jump into the actual function, pointed to
by the GOT entry for each function.  
Oh, by the way, not all PLT functions are for external Imports.  Some 
compile flags wrap local functions with a PLT/GOT pair as well.

ANYWAY!  We start of identifying all the Unconditional Branches, and flagging 
each with whether they are "Real PLT" branches or some Lazy Loader Trampoline
thing.  
We then attempt to determine how large each PLT function is.  This means, how
far before the Branch is the start of the PLT entry.  The reason is, we know
precisely where the Branches are.  We *don't* know (before analyzing the rest 
of the codebase) what will actually be called.  

In order to identify the start of the function, we determine if there is a
Trampoline, and if so, skip to the next "RealPLT" branch.  Then we work 
backward until we run into another unconditional branch, a NOP, a non-location,
or the start of the section.  That helps us determine where the functions all 
start in relation to the branch, giving us "plt_size".

We use a heuristic calculating how many distances there are, and choose
the most common distance to determine the plt_distance, or the distance between 
the start (and the branch) of each PLT entry.

Armed with plt_distance and plt_size, we then determine where each PLT entry 
begins, and make those Functions, and analysis continues from there.


"""
import logging
import vivisect
import envi
import envi.archs.i386 as e_i386

logger = logging.getLogger(__name__)

MAGIC_PLT_SIZE = 16

def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    Make functions 
    """
    for sva, ssize, sname, sfname in vw.getSegments():
        if sname not in (".plt", ".plt.got"):
            continue
        analyzePLT(vw, sva, ssize)

gots = {}
def getGOT(vw, fileva):
    '''
    Returns GOT location for the file which contains the address fileva.

    First checks through Sections (vw.getSegments), then through Dynamics.
    If the two clash, Dynamics wins.

    Linux binaries tend to have both Sections and Dynamics entries
    OpenBSD is only Sections.
    QNX has only Dynamics.
    '''
    global gots
    filename = vw.getFileByVa(fileva)

    gottup = gots.get(filename)
    if gottup is not None:
        return gottup

    for va, size, name, fname in vw.getSegments():
        if name == ".got" and fname == filename:
            gotva = va
            gotsize = size
            break

    # pull GOT info from Dynamics
    fdyns = vw.getFileMeta(filename, 'ELF_DYNAMICS')
    if fdyns is not None:
        FGOT = fdyns.get('DT_PLTGOT')
        if vw.getFileMeta(filename, 'addbase'):
            imgbase = vw.getFileMeta(filename, 'imagebase')
            logger.debug('Adding Imagebase: 0x%x', imgbase)
            FGOT += imgbase
        if gotva is not None:
            if gotva != FGOT:
                logger.warn("Dynamics and Sections have different GOT entries: S:0x%x D:0x%x. using Dynamics", gotva, FGOT)
                # since Dynamics don't store the GOT size, just use to the end of the memory map
                mmva, mmsz, mmperm, mmname = vw.getMemoryMap(FGOT)
                moffset = gotva - mmva
                gotsize = mmsz - moffset
            gotva = FGOT

    gots[filename] = (gotva, gotsize)
    return gotva, gotsize

def getPLTs(vw):
    plts = []
    pltva = None
    # Thought:  This is DT_PLTGOT, although each ELF will/may have their own DT_PLTGOT.
    for va, size, name, fname in vw.getSegments():
        if name.startswith(".plt"):
            pltva = va
            pltsize = size
            plts.append((pltva, pltsize))
            break

    # pull GOT info from Dynamics
    for fname in vw.getFiles():
        fdyns = vw.getFileMeta(fname, 'ELF_DYNAMICS')
        if fdyns is not None:
            FGOT = fdyns.get('DT_PLTREL')
            newish = True
            for pltva, pltsize in plts:
                if FGOT == pltva:
                    newish = False
            if newish:
                plts.append((FGOT, None))

    return gots

def analyzePLT(vw, ssva, ssize):
    try:
        ''' 
        analyze an entire section designated as "PLT" or "PLTGOT"
        '''
        emu = None
        sva = ssva
        nextseg = sva + ssize
        trampbr = None
        has_tramp = False
        gotva, gotsize = getGOT(vw, ssva)

        ###### make code for every opcode in PLT
        # make and parse opcodes.  keep track of unconditional branches
        branchvas = []

        # drag an emulator along to calculate branches, if available
        try:
            emu = vw.getEmulator()
            emu.setRegister(e_i386.REG_EBX, gotva)  # every emulator will have a 4th register, and if it's not used, no harm done.
        except Exception as e:
            logger.debug("no emulator available: %r", e)

        while sva < nextseg:
            logger.debug('analyzePLT(0x%x, 0x%x) first pass:  sva: 0x%x   nextseg: 0x%x', ssva, ssize, sva, nextseg)
            if vw.getLocation(sva) is None:
                logger.info('making code: 0x%x', sva)
                try:
                    vw.makeCode(sva)
                except Exception:
                    logger.exception('0x%x: exception', sva)

            ltup = vw.getLocation(sva)

            # ltup should *always* be a location, unless something broke.  however, fail gracefully :)
            if ltup is not None:
                lva, lsz, ltype, ltinfo = ltup
                # if the location is an Opcode, check for branch info
                if ltype == vivisect.LOC_OP:
                    op = vw.parseOpcode(lva)
                    emu.setProgramCounter(lva)
                    if op.iflags & envi.IF_BRANCH and \
                            not op.iflags & envi.IF_COND:

                        # we grab all unconditional branches, and tag them.
                        # some compilers pepper conditional branches between 
                        # PLT entries, for lazy-loading tricks.  We skip those.

                        # quickly, check the branch target is not the section 
                        # start address.
                        tbrva = op.opers[-1].getOperValue(op, emu=emu)
                        tbrref = op.opers[-1].getOperAddr(op, emu=emu)
                        realplt = not bool(tbrva == ssva)

                        # since the above check will "fail open", refine check if True
                        if realplt:
                            loc = vw.getLocation(tbrref)
                            tgt_seg = vw.getSegment(tbrref)

                            # if the location referenced by this address doesn't exist,
                            # it's not an IMPORT
                            if loc is None:
                                realplt = False

                            # if target is in the ELF Section with a name starting with ".got" 
                            # OR that the target address is after the DT_PLTGOT entry (
                            elif tgt_seg is not None:
                                tsegva, tsegsz, tsegname, tsegfile = tgt_seg
                                # see if the target address segment is GOT, but 
                                # also don't let it be the first entry, which is the LazyLoader
                                if not (tsegname.startswith('.got') and tsegva != lva):
                                    logger.debug("0x%x: tbrref not in GOT (segment)", tbrref)
                                    realplt = False

                            else:
                                taintaddr = emu.getVivTaint(tbrref)
                                taintval = emu.getVivTaint(tbrva)

                                if taintaddr is not None:
                                    taintva, ttype, loctup = taintaddr
                                    if ttype != 'import':
                                        logger.debug("0x%x: is not an import taint! (%r, %r)", taintva, ttype, loctup)
                                        realplt = False

                                elif not vw.isValidPointer(tbrref):
                                    logger.debug("0x%x: tbrref is not valid pointer!", tbrref)
                                    realplt = False

                                else:
                                    fname = vw.getFileByVa(tbrref)
                                    if fname is not None:
                                        fdyns = vw.getFileMeta(fname, 'ELF_DYNAMICS')
                                        if fdyns is not None:
                                            FGOT = fdyns.get('DT_PLTGOT')
                                            if FGOT is not None and tbrref <= FGOT:
                                                logger.debug("0x%x: tbrref not in GOT (DT_PLTGOT)", tbrref)
                                                realplt = False

                        if not realplt:
                            has_tramp = True
                            logger.debug("HAS_TRAMP!")

                        branchvas.append((op.va, realplt, tbrva, op))

                    # after analyzing the situation, emulate the opcode
                    emu.executeOpcode(op)

                sva += lsz
                logger.debug('incrementing to next va: 0x%x', sva)
            else:
                logger.warn('makeCode(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1

        if not len(branchvas):
            return

        # plt entries have:
        #   a distance between starts/finish 
        #   a size
        # they are not the same.

        if has_tramp:
            # find the tramp's branch
            trampbr = ssva
            loc = vw.getLocation(trampbr)
            while loc is not None and (loc[vivisect.L_TINFO] & envi.IF_BRANCH == 0):
                lva, lsz, ltype, ltinfo = loc
                trampbr += lsz
                loc = vw.getLocation(trampbr)

            # set our branchva list straight.  trampoline is *not* a realplt.
            if branchvas[0][0] == trampbr:
                branchvas[0] = (trampbr, False, branchvas[0][2], branchvas[0][3])
            else:
                logger.debug("has_tramp: trampbr: 0x%x    branchvas[0][0]: 0x%x -> 0x%x", trampbr, branchvas[0][0], branchvas[0][2])

        ###### heuristically determine PLT entry size and distance
        heur = {}
        lastva = ssva
        # first determine distance between GOT branches:
        for vidx in range(1, len(branchvas)):
            bva, realplt, brtgt, bop = branchvas[vidx]
            if not realplt:
                continue

            delta = bva - lastva
            lastva = bva
            heur[delta] = heur.get(delta, 0) + 1

        heurlist = [(y, x) for x, y in heur.items()]
        heurlist.sort()

        # there should be only one heuristic
        if len(heurlist) > 1:
            logger.warn("heuristics have more than one tracked branch: investigate!  PLT analysis may be wrong (%r)", heurlist)

        # distance should be the greatest value.
        if len(heurlist):
            plt_distance = heurlist[-1][1]
            logger.debug('plt_distance : 0x%x\n%r', plt_distance, heurlist)
        else:
            # if we don't have a heurlist, this shouldn't matter:
            plt_distance = 16
            logger.debug('plt_distance (fallback): 0x%x', plt_distance)


        ###### now determine plt_size (basically, how far to backup from the branch to find the start of function
        # *don't* use the first entry, because the trampoline is often oddly sized...
        logger.debug('finding plt_size...')
        plt_size = 0
        # let's start at the end, since with or without a tramp, we have to have *one* good one, 
        # or we just don't care.
        bridx = len(branchvas)-1

        brva, realplt, brtgtva, op = branchvas[bridx]
        while brva != trampbr and not realplt:
            bridx -= 1
            brva, realplt, brtgtva, op = branchvas[bridx]

        # start off pointing at the branch location which bounces through GOT.
        loc = vw.getLocation(brva)

        # get the arch-dependent list of badops and the nop instruction bytes
        badops = vw.arch.archGetBadOps()
        nopbytes = vw.arch.archGetNopInstr()

        # we're searching *backwards* for a point where either we hit:
        #  * another branch/NO_FALL (ie. lazy-loader) or
        #  * non-Opcode (eg. literal pool)
        #  * or a NOP
        # bounded to what we know is the distance between PLT branches
        loc = vw.getLocation(loc[vivisect.L_VA] - 1)
        while loc is not None and \
                plt_size <= plt_distance:
            # first we back up one location
            lva, lsz, ltype, ltinfo = loc

            # if we run past the beginning of the PLT section, we're done.
            if lva < ssva:
                break

            if ltype != vivisect.LOC_OP:
                # we've run into a non-opcode location: bail!
                break

            if ltinfo & envi.IF_BRANCH:
                # we've hit another branch instruction.  stop!
                break

            op = vw.parseOpcode(lva)
            if op.mnem == 'nop' or vw.readMemory(lva, len(nopbytes)) == nopbytes:
                # we've run into inter-plt padding - curse you, gcc!
                break

            if op in badops:
                # we've run into a "bad opcode" like \x00\x00 or \xff\xff...
                break
            
            # if we get through all those checks, the previous location is part
            # of the PLT function.
            plt_size += lsz
            loc = vw.getLocation(loc[vivisect.L_VA] - 1)

        logger.debug('plt_size : 0x%x', plt_size)
        ###### now get start of first real PLT entry
        bridx = 0
        logger.debug("reusing existing bridx: %r (0x%x, %r)", bridx, branchvas[bridx][0], branchvas[bridx][1])
        brlen = len(branchvas)
        logger.debug('plt branchvas: %r', [(hex(x), y, z, a) for x, y, z, a in branchvas])

        if has_tramp:
            logger.debug('First function in PLT is not a PLT entry.  Found Lazy Loader Trampoline.')
            vw.makeName(ssva, 'LazyLoaderTrampoline', filelocal=True, makeuniq=True)

        # scroll through arbitrary length functions and make functions
        for brva, realplt, brtgtva, op in branchvas:
            if not realplt:
                continue
            sva = brva - plt_size
            logger.info('making PLT function: 0x%x', sva)
            vw.makeFunction(sva)

    except Exception as e:
        logger.exception('analyzePLT(0x%x, 0x%x)', ssva, ssize)

MAX_OPS = 10


def analyzeFunction(vw, funcva):
    # check to make sure we're in the PLT
    seg = vw.getSegment(funcva)
    if seg is None:
        logger.info('not analyzing 0x%x: no segment found', funcva)
        return
    else:
        segva, segsize, segname, segfname = seg

        if segname not in (".plt", ".plt.got"):
            logger.debug('0x%x: not part of ".plt" or ".plt.got"', funcva)
            return

    logger.info('analyzing PLT function: 0x%x', funcva)
    # start off spinning up an emulator to track through the PLT entry
    # slight hack, but we don't currently know if thunk_bx exists
    fname = vw.getFileByVa(funcva)
    gotva, gotsize = getGOT(vw, funcva)

    # all architectures should at least have some minimal emulator
    emu = vw.getEmulator()
    emu.setRegister(e_i386.REG_EBX, gotva)  # every emulator will have a 4th register, and if it's not used, no harm done.

    # roll through instructions looking for a branch (pretty quickly)
    count = 0
    opva = funcva
    try:
        op = vw.parseOpcode(opva)
        while count < MAX_OPS and op.iflags & envi.IF_BRANCH == 0:
            emu.executeOpcode(op)
            opva += len(op)
            op = vw.parseOpcode(opva)
            logging.debug("0x%x: %r", opva, op)
            count += 1
    except Exception as e:
        logger.warn('failure analyzing PLT func 0x%x: %r', funcva, e)
        return

    # we've reached the branch instruction or we've gone through too many opcodes
    if op.iflags & envi.IF_BRANCH == 0:
        logger.warn("PLT: 0x%x - Could not find a branch!", funcva)
        return

    # cycle through the opcode's "branches" to make connections and look for funcname.
    # BR_DEREF - the address in opval is a pointer, not code
    # BR_FALL  - the address is the next instruction (should never happen here)
    funcname = None
    branches = op.getBranches(emu)
    logger.debug("getBranches returned: %r", branches)

    for opval, brflags in branches:
        if opval is None:
            logger.info("getBranches():  opval is None!:  op = %r     branches = %r", op, branches)
        else:
            logger.debug('getBranches():  ref: 0x%x  brflags: 0x%x', opval, brflags)

        loctup = vw.getLocation(opval)

        # if BR_DEREF, this is a pointer
        if brflags & envi.BR_DEREF:
            if loctup is None:              ###### TODO: CHECK HERE FOR TAINT VALUE!
                taintval = emu.getVivTaint(opval)
                taintrepr = emu.reprVivTaint(taintval)
                logger.exception('0x%x: opval=0x%x: brflags is BR_DEREF, but loctup is None.  Don\'t know what to do. skipping.%r %r', op.va, opval, taintval, taintrepr)
                continue

            lva, lsz, ltype, ltinfo = loctup
            opref = opval
            # add the xref to whatever location referenced (assuming the opref hack worked)
            if vw.isValidPointer(opref):
                logger.debug('reference 0x%x is valid, adding Xref', opref)
                vw.addXref(op.va, opref, vivisect.REF_DATA)

            if ltype == vivisect.LOC_IMPORT:
                # import locations store the name as ltinfo
                funcname = ltinfo
                logger.debug("0x%x: (0x%x) LOC_IMPORT by BR_DEREF %r", funcva, opval, funcname)

            elif ltype == vivisect.LOC_POINTER:
                # we have a deref to a pointer.
                funcname = vw.getName(ltinfo)
                logger.debug("0x%x: (0x%x->0x%x) LOC_POINTER by BR_DEREF %r", funcva, opval, ltinfo, funcname)
            else:
                logger.warn("0x%x: (0x%x) not LOC_IMPORT or LOC_POINTER?? by BR_DEREF %r", funcva, opval, loctup)

        else:
            # check the taint tracker to determine if it's an import (the opval value is pointless if it is)
            taint = emu.getVivTaint(opval)
            if taint is not None:
                # if it is an import taint
                taintva, ttype, loctup = taint
                if ttype != 'import':
                    logger.warn('getBranches(): returned a Taint which is *not* an import: %r', taint)
                    return

                lva, lsz, ltype, ltinfo = loctup
                funcname = ltinfo
                logger.debug('0x%x: LOC_IMPORT (emu-taint): 0x%x:  %r', opva, lva, funcname)

            else:
                # instead of a taint (which *should* indicate an IMPORT), we have real pointer.
                # check the location type
                if not vw.isValidPointer(opval):
                    logger.info("PLT: opval=0x%x - not a valid pointer... skipping", opval)
                    continue

                if loctup is None:
                    if opval is None:
                        logger.warn("PLT: 0x%x - branch deref not defined: (opval is None!)", opva)
                        return
                    else:
                        aopval, aflags = vw.arch.archModifyFuncAddr(opval, {'arch': envi.ARCH_DEFAULT})
                        logger.info("PLT: 0x%x - making function at location 0x%x", opva, aopval)
                        vw.makeFunction(aopval, arch=aflags['arch'])
                        loctup = vw.getLocation(opval)

                lva, lsz, ltype, ltinfo = loctup

                # in case the architecture cares about the function address...
                aopval, aflags = vw.arch.archModifyFuncAddr(opval, {'arch': envi.ARCH_DEFAULT})
                funcname = vw.getName(aopval)
                if funcname is None:
                    funcname = vw.getName(opval)

                # sort through the location types and adjust accordingly
                if ltype == vivisect.LOC_IMPORT:
                    logger.info("0x%x: (0x%x) dest is LOC_IMPORT but missed taint for %r", funcva, opval, funcname)
                    # import locations store the name as ltinfo
                    funcname = ltinfo

                elif ltype == vivisect.LOC_OP:
                    logger.debug("0x%x: succeeded finding LOC_OP at the end of the rainbow! (%r)", funcva, funcname)
                    if vw.getFunction(aopval) is None:
                        logger.debug("0x%x: code does not exist at 0x%x.  calling makeFunction()", funcva, aopval)
                        vw.makeFunction(aopval, arch=aflags['arch'])

                    # this "thunk" actually calls something in the workspace, that exists as a function...
                    logger.info('0x%x points to real code (0x%x: %r)', funcva, opval, funcname)
                    vw.addXref(op.va, aopval, vivisect.REF_CODE)
                    vw.setVaSetRow('FuncWrappers', (funcva, opval))

                elif ltype == vivisect.LOC_POINTER:
                    logger.info("0x%x: (0x%x) dest is LOC_POINTER -> 0x%x", funcva, opval, ltinfo)
                    funcname = ltinfo


            if vw.getFunction(opval) == segva:
                # this is a lazy-link/load function, calling the first entry in the PLT
                logger.debug('skipping lazy-loader function: 0x%x (calls 0x%x)', funcva, opval)
                return

    # now make the thunk with appropriate naming
    # if we can't resolve a name, don't make it a thunk
    if funcname is None:
        logger.warn('0x%x: FAIL: could not resolve name for 0x%x.  Skipping.', funcva, opval)
        return

    # trim up the name
    if funcname.startswith('*.'):
        funcname = funcname[2:]

    # if filelocal for the target symbol, strip off the filename
    if funcname.startswith(fname + "."):
        funcname = funcname[len(fname)+1:]

    # trim off any address at the end
    if funcname.endswith('_%.8x' % opval):
        funcname = funcname[:-9]

    logger.info('makeFunctionThunk(0x%x, "plt_%s")', funcva, funcname)
    vw.makeFunctionThunk(funcva, "plt_" + funcname, addVa=False, filelocal=True)

'''
def printPLTs(vw):
    for seg in vw.getSegments():
        if seg[2] in ('.plt', '.plt.got'):
            print seg[2]
            vwdis(vw, seg[0], 10)

linux/i386/vdir:
.plt
0x80494c0:                        ff3504100608  push dword [0x08061004]
0x80494c6:                        ff2508100608  jmp dword [0x08061008]
0x80494cc:                                0000  add byte [eax],al
0x80494ce:                                0000  add byte [eax],al
0x80494d0:                        ff250c100608  jmp dword [0x0806100c]
0x80494d6:                          6800000000  push 0
0x80494db:                          e9e0ffffff  jmp 0x080494c0
0x80494e0:                        ff2510100608  jmp dword [0x08061010]
0x80494e6:                          6808000000  push 8
0x80494eb:                          e9d0ffffff  jmp 0x080494c0
.plt.got
0x8049b60:                        ff25fc0f0608  jmp dword [0x08060ffc]
0x8049b66:                                6690  nop
0x8049b68:                                0000  add byte [eax],al
0x8049b6a:                                0000  add byte [eax],al
0x8049b6c:                                0000  add byte [eax],al
0x8049b6e:                                0000  add byte [eax],al

linux/ie86/chgrp:
.plt
0x8048d90:                        ff3504400508  push dword [0x08054004]
0x8048d96:                        ff2508400508  jmp dword [0x08054008]
0x8048d9c:                                0000  add byte [eax],al
0x8048d9e:                                0000  add byte [eax],al
0x8048da0:                        ff250c400508  jmp dword [0x0805400c]
0x8048da6:                          6800000000  push 0
0x8048dab:                          e9e0ffffff  jmp 0x08048d90
0x8048db0:                        ff2510400508  jmp dword [0x08054010]
0x8048db6:                          6808000000  push 8
0x8048dbb:                          e9d0ffffff  jmp 0x08048d90
.plt.got
0x80491d0:                        ff25fc3f0508  jmp dword [0x08053ffc]
0x80491d6:                                6690  nop 
0x80491d8:                                0000  add byte [eax],al
0x80491da:                                0000  add byte [eax],al


linux/i386/libc-2.13.so:
.plt
0x2016b78:                        ffb304000000  push dword [ebx + 4]
0x2016b7e:                        ffa308000000  jmp dword [ebx + 8]
0x2016b84:                                0000  add byte [eax],al
0x2016b86:                                0000  add byte [eax],al
0x2016b88:                        ffa30c000000  jmp dword [ebx + 12]
0x2016b8e:                          6800000000  push 0
0x2016b93:                          e9e0ffffff  jmp 0x02016b78
0x2016b98:                        ffa310000000  jmp dword [ebx + 16]
0x2016b9e:                          6808000000  push 8
0x2016ba3:                          e9d0ffffff  jmp 0x02016b78


linux/i386/libstdc++.so.6.0.25.viv
.plt
0x206aeb0:                        ffb304000000  push dword [ebx + 4]
0x206aeb6:                        ffa308000000  jmp dword [ebx + 8]
0x206aebc:                                0000  add byte [eax],al
0x206aebe:                                0000  add byte [eax],al
0x206aec0:                        ffa30c000000  jmp dword [ebx + 12]
0x206aec6:                          6800000000  push 0
0x206aecb:                          e9e0ffffff  jmp 0x0206aeb0
0x206aed0:                        ffa310000000  jmp dword [ebx + 16]
0x206aed6:                          6808000000  push 8
0x206aedb:                          e9d0ffffff  jmp 0x0206aeb0
.plt.got
0x206e2e0:                        ffa3b4f7ffff  jmp dword [ebx - 2124]
0x206e2e6:                                6690  nop
0x206e2e8:                        ffa3c8f7ffff  jmp dword [ebx - 2104]
0x206e2ee:                                6690  nop
0x206e2f0:                        ffa334f8ffff  jmp dword [ebx - 1996]
0x206e2f6:                                6690  nop
0x206e2f8:                        ffa34cf8ffff  jmp dword [ebx - 1972]
0x206e2fe:                                6690  nop
0x206e300:                        ffa35cf8ffff  jmp dword [ebx - 1956]
0x206e306:                                6690  nop

linux/libstdc++.so.6.viv
.plt
0x2058cc0:                        ff3542432900  push qword [rip + 2704194]
0x2058cc6:                        ff2544432900  jmp qword [rip + 2704196]
0x2058ccc:                            0f1f4000  nop dword [rax]
0x2058cd0:                        ff2542432900  jmp qword [rip + 2704194]
0x2058cd6:                          6800000000  push 0
0x2058cdb:                          e9e0ffffff  jmp 0x02058cc0
0x2058ce0:                        ff253a432900  jmp qword [rip + 2704186]
0x2058ce6:                          6801000000  push 1
0x2058ceb:                          e9d0ffffff  jmp 0x02058cc0
0x2058cf0:                        ff2532432900  jmp qword [rip + 2704178]

linux/i386/static32.llvm.elf.viv
.plt
0x80481c8:                        ff250cb00d08  jmp dword [0x080db00c]
0x80481ce:                                6690  nop
0x80481d0:                        ff2510b00d08  jmp dword [0x080db010]
0x80481d6:                                6690  nop
0x80481d8:                        ff2514b00d08  jmp dword [0x080db014]
0x80481de:                                6690  nop
0x80481e0:                        ff2518b00d08  jmp dword [0x080db018]
0x80481e6:                                6690  nop
0x80481e8:                        ff251cb00d08  jmp dword [0x080db01c]
0x80481ee:                                6690  nop

linux/arm/sh.viv
.plt
0xb5e4:                       04e02de5  push lr
0xb5e8:                       04e09fe5  ldr lr, [#0xb5f4]
0xb5ec:                       0ee08fe0  add lr, pc, lr
0xb5f0:                       08f0bee5  ldr pc, [lr, #0x8]!
0xb5f4:                       9cde0300  muleq r3, r12, lr
0xb5f8:                       00c68fe2  adr r12, 0x0000b600
0xb5fc:                       3dca8ce2  add r12, r12, #0x3d000
0xb600:                       9cfebce5  ldr pc, [r12, #0xe9c]!
0xb604:                       00c68fe2  adr r12, 0x0000b60c
0xb608:                       3dca8ce2  add r12, r12, #0x3d000

linux/amd64/ls.viv
.plt
0x401ff0:                         ff35fa6f2100  push qword [rip + 2191354]
0x401ff6:                         ff25fc6f2100  jmp qword [rip + 2191356]
0x401ffc:                             0f1f4000  nop dword [rax]
0x402000:                         ff25fa6f2100  jmp qword [rip + 2191354]
0x402006:                           6800000000  push 0
0x40200b:                           e9e0ffffff  jmp 0x00401ff0
0x402010:                         ff25f26f2100  jmp qword [rip + 2191346]
0x402016:                           6801000000  push 1
0x40201b:                           e9d0ffffff  jmp 0x00401ff0
0x402020:                         ff25ea6f2100  jmp qword [rip + 2191338]

linux/amd64/libc-2.27-oldstyle.so
.plt
0x2020fd0:                        ff3532a03c00  push qword [rip + 3973170]
0x2020fd6:                        ff2534a03c00  jmp qword [rip + 3973172]
0x2020fdc:                            0f1f4000  nop dword [rax]
0x2020fe0:                        ff2532a03c00  jmp qword [rip + 3973170]
0x2020fe6:                          682d000000  push 45
0x2020feb:                          e9e0ffffff  jmp 0x02020fd0
0x2020ff0:                        ff252aa03c00  jmp qword [rip + 3973162]
0x2020ff6:                          682c000000  push 44
0x2020ffb:                          e9d0ffffff  jmp 0x02020fd0
0x2021000:                        ff2522a03c00  jmp qword [rip + 3973154]
.plt.got
0x20212c0:                        ff256a9b3c00  jmp qword [rip + 3971946]
0x20212c6:                                6690  nop
0x20212c8:                        ff25ca9c3c00  jmp qword [rip + 3972298]
0x20212ce:                                6690  nop
0x20212d0:                                  55  push rbp
0x20212d1:                                  53  push rbx
0x20212d2:                      488d3d0d251900  lea rdi,qword [rip + 1647885]
0x20212d9:                          be02000080  mov esi,0x80000002
0x20212de:                            4883ec08  sub rsp,8
0x20212e2:                          e869511400  call 0x02166450

linux/amd64/libstdc++.so.6.0.25.viv
.plt
0x20884a0:                        ff35629b2f00  push qword [rip + 3119970]
0x20884a6:                        ff25649b2f00  jmp qword [rip + 3119972]
0x20884ac:                            0f1f4000  nop dword [rax]
0x20884b0:                        ff25629b2f00  jmp qword [rip + 3119970]
0x20884b6:                          6800000000  push 0
0x20884bb:                          e9e0ffffff  jmp 0x020884a0
0x20884c0:                        ff255a9b2f00  jmp qword [rip + 3119962]
0x20884c6:                          6801000000  push 1
0x20884cb:                          e9d0ffffff  jmp 0x020884a0
0x20884d0:                        ff25529b2f00  jmp qword [rip + 3119954]
.plt.got
0x208b800:                        ff2542582f00  jmp qword [rip + 3102786]
0x208b806:                                6690  nop
0x208b808:                        ff254a582f00  jmp qword [rip + 3102794]
0x208b80e:                                6690  nop
0x208b810:                        ff2512592f00  jmp qword [rip + 3102994]
0x208b816:                                6690  nop
0x208b818:                        ff253a592f00  jmp qword [rip + 3103034]
0x208b81e:                                6690  nop
0x208b820:                        ff255a592f00  jmp qword [rip + 3103066]
0x208b826:                                6690  nop

linux/amd64/static64.llvm.elf.viv
.plt
0x400428:                         ff25eaab2b00  jmp qword [rip + 2862058]
0x40042e:                                 6690  nop
0x400430:                         ff25eaab2b00  jmp qword [rip + 2862058]
0x400436:                                 6690  nop
0x400438:                         ff25eaab2b00  jmp qword [rip + 2862058]
0x40043e:                                 6690  nop
0x400440:                         ff25eaab2b00  jmp qword [rip + 2862058]
0x400446:                                 6690  nop
0x400448:                         ff25eaab2b00  jmp qword [rip + 2862058]
0x40044e:                                 6690  nop

linux/amd64/libc-2.27.so.viv
.plt
0x2020fd0:                        ff3532a03c00  push qword [rip + 3973170]
0x2020fd6:                        ff2534a03c00  jmp qword [rip + 3973172]
0x2020fdc:                            0f1f4000  nop dword [rax]
0x2020fe0:                        ff2532a03c00  jmp qword [rip + 3973170]
0x2020fe6:                          682d000000  push 45
0x2020feb:                          e9e0ffffff  jmp 0x02020fd0
0x2020ff0:                        ff252aa03c00  jmp qword [rip + 3973162]
0x2020ff6:                          682c000000  push 44
0x2020ffb:                          e9d0ffffff  jmp 0x02020fd0
0x2021000:                        ff2522a03c00  jmp qword [rip + 3973154]
.plt.got
0x20212c0:                        ff256a9b3c00  jmp qword [rip + 3971946]
0x20212c6:                                6690  nop
0x20212c8:                        ff25ca9c3c00  jmp qword [rip + 3972298]
0x20212ce:                                6690  nop
0x20212d0:                                  55  push rbp
0x20212d1:                                  53  push rbx
0x20212d2:                      488d3d0d251900  lea rdi,qword [rip + 1647885]
0x20212d9:                          be02000080  mov esi,0x80000002
0x20212de:                            4883ec08  sub rsp,8
0x20212e2:                          e869511400  call 0x02166450

linux/amd64/chown.viv
.plt
0x2001d50:                        ff351ae02000  push qword [rip + 2154522]
0x2001d56:                        ff251ce02000  jmp qword [rip + 2154524]
0x2001d5c:                            0f1f4000  nop dword [rax]
0x2001d60:                        ff251ae02000  jmp qword [rip + 2154522]
0x2001d66:                          6800000000  push 0
0x2001d6b:                          e9e0ffffff  jmp 0x02001d50
0x2001d70:                        ff2512e02000  jmp qword [rip + 2154514]
0x2001d76:                          6801000000  push 1
0x2001d7b:                          e9d0ffffff  jmp 0x02001d50
0x2001d80:                        ff250ae02000  jmp qword [rip + 2154506]
.plt.got
0x2002200:                        ff25cadd2000  jmp qword [rip + 2153930]
0x2002206:                                6690  nop
0x2002208:                        ff25eadd2000  jmp qword [rip + 2153962]
0x200220e:                                6690  nop
0x2002210:                                4157  push r15
0x2002212:                                4156  push r14
0x2002214:                              4531f6  xor r14d,r14d
0x2002217:                                4155  push r13
0x2002219:                                4154  push r12
0x200221b:                        41bdffffffff  mov r13d,0xffffffff

openbsd/ls.amd64.viv

qnx/arm/ksh.viv


'''
