'''
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
'''
import logging
import collections

import envi
import vivisect
import envi.common as e_cmn
import envi.archs.i386 as e_i386

logger = logging.getLogger(__name__)

MAGIC_PLT_SIZE = 16


def analyze(vw):
    """
    Do simple linear disassembly of the .plt section if present.
    Make functions
    """
    if vw.getMeta('Platform') == 'qnx':
        logger.warning('skipping initial PLT section analysis for QNX binary.')
        return

    for sva, ssize in getPLTs(vw):
        analyzePLT(vw, sva, ssize)


def getGOTByFilename(vw, filename):
    '''
    Returns GOT location for the filename specified.

    First checks through Sections (vw.getSegments), then through Dynamics.
    If the two clash, Dynamics wins.

    Linux binaries tend to have both Sections and Dynamics entries
    OpenBSD is only Sections.
    QNX has only Dynamics.
    '''
    gottup = vw.getFileMeta(filename, 'GOT')
    if gottup is not None:
        return gottup

    gotva = None
    gotsize = None
    for va, size, name, fname in vw.getSegments():
        if name == '.got.plt' and fname == filename:
            gotva = va
            gotsize = size

        elif name == ".got" and fname == filename and gotva is None:
            # for some reason, if '.got.plt' is present, it's the "right one"
            gotva = va
            gotsize = size

    # pull GOT info from Dynamics
    fdyns = vw.getFileMeta(filename, 'ELF_DYNAMICS')
    if fdyns is not None:
        FGOT = fdyns.get('DT_PLTGOT')
        if FGOT is not None:
            # be sure to add the imgbase to FGOT if required
            if vw.getFileMeta(filename, 'addbase'):
                imgbase = vw.getFileMeta(filename, 'imagebase')
                logger.debug('Adding Imagebase: 0x%x', imgbase)
                FGOT += imgbase

            if FGOT != gotva and None not in (FGOT, gotva):
                logger.warning("Dynamics and Sections have different GOT entries: S:0x%x D:0x%x. using Dynamics", gotva, FGOT)

            # since Dynamics don't store the GOT size, just use to the end of the memory map
            mmva, mmsz, mmperm, mmname = vw.getMemoryMap(FGOT)
            gotva = FGOT
            moffset = gotva - mmva
            gotsize = mmsz - moffset

    vw.setFileMeta(filename, 'GOT', (gotva, gotsize))
    return gotva, gotsize

def getGOTs(vw):
    out = collections.defaultdict(set)

    gotva = None
    gotsize = None
    for va, size, name, fname in vw.getSegments():
        if name in ('.got.plt', '.got'):
            out[fname].add((va, size))

    # pull GOT info from Dynamics
    for filename in vw.getFiles():
        fdyns = vw.getFileMeta(filename, 'ELF_DYNAMICS')
        if fdyns is not None:
            FGOT = fdyns.get('DT_PLTGOT')
            if FGOT is not None:
                # be sure to add the imgbase to FGOT if required
                if vw.getFileMeta(filename, 'addbase'):
                    imgbase = vw.getFileMeta(filename, 'imagebase')
                    #logger.debug('Adding Imagebase: 0x%x', imgbase)
                    FGOT += imgbase

                flist = out[filename]

                skip = False
                for va, size in flist:
                    if FGOT == va:
                        skip = True

                if skip:
                    continue

                # since Dynamics don't store the GOT size, just use to the end of the memory map
                mmva, mmsz, mmperm, mmname = vw.getMemoryMap(FGOT)
                gotva = FGOT
                moffset = gotva - mmva
                gotsize = mmsz - moffset
                flist.add((gotva, gotsize))
    return out

def getPLTs(vw):
    plts = []
    # Thought:  This is DT_PLTGOT, although each ELF will/may have their own DT_PLTGOT.
    for va, size, name, fname in vw.getSegments():
        if name.startswith(".plt") or name == '.rela.plt':
            plts.append((va, size))

    # pull GOT info from Dynamics
    for fname in vw.getFiles():
        fdyns = vw.getFileMeta(fname, 'ELF_DYNAMICS')
        if fdyns is not None:
            FGOT = fdyns.get('DT_JMPREL')
            FGOTSZ = fdyns.get('DT_PLTRELSZ')
            if vw.getFileMeta(fname, 'addbase'):
                imgbase = vw.getFileMeta(fname, 'imagebase')
                logger.debug('Adding Imagebase: 0x%x', imgbase)
                FGOT += imgbase

            newish = True
            for pltva, pltsize in plts:
                if FGOT == pltva:
                    newish = False
            if newish and FGOT and FGOTSZ:
                plts.append((FGOT, FGOTSZ))

    return plts


def analyzePLT(vw, ssva, ssize):
    try:
        '''
        analyze an entire section designated as "PLT" or "PLTGOT"
        '''
        emu = None
        sva = ssva
        nextseg = sva + ssize
        gotva, gotsize = getGOTByFilename(vw, vw.getFileByVa(ssva))

        ###### make code for every opcode in PLT
        # make and parse opcodes.  keep track of unconditional branches
        branchvas = []

        # drag an emulator along to calculate branches, if available
        try:
            emu = vw.getEmulator()
            emu.setRegister(e_i386.REG_EBX, gotva)  # every emulator will have a 4th register, and if it's not used, no harm done.
        except Exception as e:
            logger.debug("no emulator available: %r", e, exc_info=1)
            return

        while sva < nextseg:
            logger.debug('analyzePLT(0x%x, 0x%x) first pass:  sva: 0x%x   nextseg: 0x%x', ssva, ssize, sva, nextseg)
            if vw.getLocation(sva) is None:
                logger.debug('making code: 0x%x', sva)
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

                        branchvas.append((op.va, realplt, tbrva, op))

                    # after analyzing the situation, emulate the opcode
                    emu.executeOpcode(op)

                sva += lsz
                logger.debug('incrementing to next va: 0x%x', sva)
            else:
                logger.warning('makeCode(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1

    except Exception as e:
        logger.error('analyzePLT(0x%x, %r): %s', ssva, ssize, str(e))



MAX_OPS = 10

def analyzeFunction(vw, funcva):
    # check to make sure we're in the PLT
    plts = getPLTs(vw)
    isplt = False
    for pltva, pltsz in plts:
        if pltva <= funcva <= (pltva + pltsz):
            isplt = True
            segva = pltva
            segsize = pltsz
            break

    # if we're not 
    if not isplt:
        logger.log(e_cmn.SHITE, '0x%x: not part of a .plt section', funcva)
        return

    logger.info('analyzing PLT function: 0x%x', funcva)
    # start off spinning up an emulator to track through the PLT entry
    # slight hack, but we don't currently know if thunk_bx exists
    fname = vw.getFileByVa(funcva)
    gotva, gotsize = getGOTByFilename(vw, fname)

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
            logger.log(e_cmn.SHITE, "0x%x: %r", opva, op)
            count += 1
    except Exception as e:
        logger.warning('failure analyzing PLT func 0x%x: %r', funcva, e)
        return

    # we've reached the branch instruction or we've gone through too many opcodes
    if op.iflags & envi.IF_BRANCH == 0:
        logger.warning("PLT: 0x%x - Could not find a branch!", funcva)
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
                logger.warning("0x%x: (0x%x) not LOC_IMPORT or LOC_POINTER?? by BR_DEREF %r", funcva, opval, loctup)

        else:
            # check the taint tracker to determine if it's an import (the opval value is pointless if it is)
            taint = emu.getVivTaint(opval)
            if taint is not None:
                # if it is an import taint
                taintva, ttype, loctup = taint
                if ttype != 'import':
                    logger.warning('getBranches(): returned a Taint which is *not* an import: %r', taint)
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
                        logger.warning("PLT: 0x%x - branch deref not defined: (opval is None!)", opva)
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
        logger.warning('0x%x: FAIL: could not resolve name for 0x%x.  Skipping.', funcva, opval)
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









sections versus dynamics:
In [79]: x+=1; print '======================================\n' + vws[x].metadata['StorageName']; ed=vws[x].filemeta.values()[0]['ELF_DYNAMICS']; print hex(ed['DT_JMPREL']), hex(ed['DT_PLTRELSZ']), hex(ed['DT_PLTGOT']); es[x].sections
======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/amd64/ls.viv
0x4015f8 0x9d8 0x618fe8
Out[79]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [             .interp] @0x00400238 (     568)  ent/size:        0/      28  align:        1,
 Elf Sec: [       .note.ABI-tag] @0x00400254 (     596)  ent/size:        0/      32  align:        4,
 Elf Sec: [  .note.gnu.build-id] @0x00400274 (     628)  ent/size:        0/      36  align:        4,
 Elf Sec: [           .gnu.hash] @0x00400298 (     664)  ent/size:        0/     104  align:        8,
 Elf Sec: [             .dynsym] @0x00400300 (     768)  ent/size:       24/    2904  align:        8,
 Elf Sec: [             .dynstr] @0x00400e58 (    3672)  ent/size:        0/    1361  align:        1,
 Elf Sec: [        .gnu.version] @0x004013aa (    5034)  ent/size:        2/     242  align:        2,
 Elf Sec: [      .gnu.version_r] @0x004014a0 (    5280)  ent/size:        0/     176  align:        8,
 Elf Sec: [           .rela.dyn] @0x00401550 (    5456)  ent/size:       24/     168  align:        8,
 
 Elf Sec: [           .rela.plt] @0x004015f8 (    5624)  ent/size:       24/    2520  align:        8,
 
 Elf Sec: [               .init] @0x00401fd0 (    8144)  ent/size:        0/      24  align:        4,
 Elf Sec: [                .plt] @0x00401ff0 (    8176)  ent/size:       16/    1696  align:       16,
 Elf Sec: [               .text] @0x00402690 (    9872)  ent/size:        0/   61800  align:       16,
 Elf Sec: [               .fini] @0x004117f8 (   71672)  ent/size:        0/      14  align:        4,
 Elf Sec: [             .rodata] @0x00411820 (   71712)  ent/size:        0/   20339  align:       32,
 Elf Sec: [       .eh_frame_hdr] @0x00416794 (   92052)  ent/size:        0/    1732  align:        4,
 Elf Sec: [           .eh_frame] @0x00416e58 (   93784)  ent/size:        0/    7988  align:        8,
 Elf Sec: [              .ctors] @0x00618df0 (  101872)  ent/size:        0/      16  align:        8,
 Elf Sec: [              .dtors] @0x00618e00 (  101888)  ent/size:        0/      16  align:        8,
 Elf Sec: [                .jcr] @0x00618e10 (  101904)  ent/size:        0/       8  align:        8,
 Elf Sec: [            .dynamic] @0x00618e18 (  101912)  ent/size:       16/     448  align:        8,
 Elf Sec: [                .got] @0x00618fd8 (  102360)  ent/size:        8/      16  align:        8,
 
 Elf Sec: [            .got.plt] @0x00618fe8 (  102376)  ent/size:        8/     864  align:        8,
 
 Elf Sec: [               .data] @0x00619360 (  103264)  ent/size:        0/     528  align:       32,
 Elf Sec: [                .bss] @0x00619580 (  103792)  ent/size:        0/    3424  align:       32,
 Elf Sec: [      .gnu_debuglink] @0x00000000 (  103792)  ent/size:        0/       8  align:        1,
 Elf Sec: [           .shstrtab] @0x00000000 (  103800)  ent/size:        0/     244  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/amd64/chown.viv
0x1648 0x6f0 0x20fd68
Out[80]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [             .interp] @0x00000238 (     568)  ent/size:        0/      28  align:        1,
 Elf Sec: [       .note.ABI-tag] @0x00000254 (     596)  ent/size:        0/      32  align:        4,
 Elf Sec: [  .note.gnu.build-id] @0x00000274 (     628)  ent/size:        0/      36  align:        4,
 Elf Sec: [           .gnu.hash] @0x00000298 (     664)  ent/size:        0/     184  align:        8,
 Elf Sec: [             .dynsym] @0x00000350 (     848)  ent/size:       24/    2448  align:        8,
 Elf Sec: [             .dynstr] @0x00000ce0 (    3296)  ent/size:        0/    1108  align:        1,
 Elf Sec: [        .gnu.version] @0x00001134 (    4404)  ent/size:        2/     204  align:        2,
 Elf Sec: [      .gnu.version_r] @0x00001200 (    4608)  ent/size:        0/     112  align:        8,
 Elf Sec: [           .rela.dyn] @0x00001270 (    4720)  ent/size:       24/     984  align:        8,
 
 Elf Sec: [           .rela.plt] @0x00001648 (    5704)  ent/size:       24/    1776  align:        8,
 
 Elf Sec: [               .init] @0x00001d38 (    7480)  ent/size:        0/      23  align:        4,
 Elf Sec: [                .plt] @0x00001d50 (    7504)  ent/size:       16/    1200  align:       16,
 Elf Sec: [            .plt.got] @0x00002200 (    8704)  ent/size:        8/      16  align:        8,
 Elf Sec: [               .text] @0x00002210 (    8720)  ent/size:        0/   36473  align:       16,
 Elf Sec: [               .fini] @0x0000b08c (   45196)  ent/size:        0/       9  align:        4,
 Elf Sec: [             .rodata] @0x0000b0a0 (   45216)  ent/size:        0/    7114  align:       32,
 Elf Sec: [       .eh_frame_hdr] @0x0000cc6c (   52332)  ent/size:        0/    1196  align:        4,
 Elf Sec: [           .eh_frame] @0x0000d118 (   53528)  ent/size:        0/    6216  align:        8,
 Elf Sec: [         .init_array] @0x0020f950 (   63824)  ent/size:        8/       8  align:        8,
 Elf Sec: [         .fini_array] @0x0020f958 (   63832)  ent/size:        8/       8  align:        8,
 Elf Sec: [        .data.rel.ro] @0x0020f960 (   63840)  ent/size:        0/     536  align:       32,
 Elf Sec: [            .dynamic] @0x0020fb78 (   64376)  ent/size:       16/     496  align:        8,
 
 Elf Sec: [                .got] @0x0020fd68 (   64872)  ent/size:        8/     664  align:        8,
 
 Elf Sec: [               .data] @0x00210000 (   65536)  ent/size:        0/     128  align:       32,
 Elf Sec: [                .bss] @0x00210080 (   65664)  ent/size:        0/     456  align:       32,
 Elf Sec: [      .gnu_debuglink] @0x00000000 (   65664)  ent/size:        0/      52  align:        4,
 Elf Sec: [           .shstrtab] @0x00000000 (   65716)  ent/size:        0/     257  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/amd64/libc-2.27.so.viv
0x20b78 0x450 0x3eb000
Out[81]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [  .note.gnu.build-id] @0x00000270 (     624)  ent/size:        0/      36  align:        4,
 Elf Sec: [       .note.ABI-tag] @0x00000294 (     660)  ent/size:        0/      32  align:        4,
 Elf Sec: [           .gnu.hash] @0x000002b8 (     696)  ent/size:        0/   15408  align:        8,
 Elf Sec: [             .dynsym] @0x00003ee8 (   16104)  ent/size:       24/   56040  align:        8,
 Elf Sec: [             .dynstr] @0x000119d0 (   72144)  ent/size:        0/   24286  align:        1,
 Elf Sec: [        .gnu.version] @0x000178ae (   96430)  ent/size:        2/    4670  align:        2,
 Elf Sec: [      .gnu.version_d] @0x00018af0 (  101104)  ent/size:        0/    1028  align:        8,
 Elf Sec: [      .gnu.version_r] @0x00018ef8 (  102136)  ent/size:        0/      48  align:        8,
 Elf Sec: [           .rela.dyn] @0x00018f28 (  102184)  ent/size:       24/   31824  align:        8,
 
 Elf Sec: [           .rela.plt] @0x00020b78 (  134008)  ent/size:       24/    1104  align:        8,
 
 Elf Sec: [                .plt] @0x00020fd0 (  135120)  ent/size:       16/     752  align:       16,
 Elf Sec: [            .plt.got] @0x000212c0 (  135872)  ent/size:        8/      16  align:        8,
 Elf Sec: [               .text] @0x000212d0 (  135888)  ent/size:        0/ 1542508  align:       16,
 Elf Sec: [   __libc_freeres_fn] @0x00199c40 ( 1678400)  ent/size:        0/    6271  align:       16,
 Elf Sec: [__libc_thread_freeres_fn] @0x0019b4c0 ( 1684672)  ent/size:        0/    5058  align:       16,
 Elf Sec: [             .rodata] @0x0019c8a0 ( 1689760)  ent/size:        0/  136360  align:       32,
 Elf Sec: [       .stapsdt.base] @0x001bdd48 ( 1826120)  ent/size:        0/       1  align:        1,
 Elf Sec: [             .interp] @0x001bdd50 ( 1826128)  ent/size:        0/      28  align:       16,
 Elf Sec: [       .eh_frame_hdr] @0x001bdd6c ( 1826156)  ent/size:        0/   23004  align:        4,
 Elf Sec: [           .eh_frame] @0x001c3748 ( 1849160)  ent/size:        0/  129624  align:        8,
 Elf Sec: [   .gcc_except_table] @0x001e31a0 ( 1978784)  ent/size:        0/    1169  align:        1,
 Elf Sec: [               .hash] @0x001e3638 ( 1979960)  ent/size:        4/   13416  align:        8,
 Elf Sec: [              .tdata] @0x003e7620 ( 1996320)  ent/size:        0/      16  align:        8,
 Elf Sec: [               .tbss] @0x003e7630 ( 1996336)  ent/size:        0/     128  align:        8,
 Elf Sec: [         .init_array] @0x003e7630 ( 1996336)  ent/size:        8/       8  align:        8,
 Elf Sec: [   __libc_subfreeres] @0x003e7638 ( 1996344)  ent/size:        0/     256  align:        8,
 Elf Sec: [       __libc_atexit] @0x003e7738 ( 1996600)  ent/size:        0/       8  align:        8,
 Elf Sec: [__libc_thread_subfreeres] @0x003e7740 ( 1996608)  ent/size:        0/      32  align:        8,
 Elf Sec: [   __libc_IO_vtables] @0x003e7760 ( 1996640)  ent/size:        0/    3432  align:       32,
 Elf Sec: [        .data.rel.ro] @0x003e84e0 ( 2000096)  ent/size:        0/    9888  align:       32,
 Elf Sec: [            .dynamic] @0x003eab80 ( 2009984)  ent/size:       16/     480  align:        8,
 Elf Sec: [                .got] @0x003ead60 ( 2010464)  ent/size:        8/     656  align:        8,
 
 Elf Sec: [            .got.plt] @0x003eb000 ( 2011136)  ent/size:        8/     392  align:        8,
 
 Elf Sec: [               .data] @0x003eb1a0 ( 2011552)  ent/size:        0/    5824  align:       32,
 Elf Sec: [                .bss] @0x003ec860 ( 2017376)  ent/size:        0/   17024  align:       32,
 Elf Sec: [       .note.stapsdt] @0x00000000 ( 2017376)  ent/size:        0/    4896  align:        4,
 Elf Sec: [.gnu.warning.sigstack] @0x00000000 ( 2022272)  ent/size:        0/      77  align:       32,
 Elf Sec: [.gnu.warning.sigreturn] @0x00000000 ( 2022368)  ent/size:        0/      50  align:       32,
 Elf Sec: [.gnu.warning.siggetmask] @0x00000000 ( 2022432)  ent/size:        0/      57  align:       32,
 Elf Sec: [ .gnu.warning.tmpnam] @0x00000000 ( 2022496)  ent/size:        0/      55  align:       32,
 Elf Sec: [.gnu.warning.tmpnam_r] @0x00000000 ( 2022560)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.tempnam] @0x00000000 ( 2022624)  ent/size:        0/      56  align:       32,
 Elf Sec: [.gnu.warning.sys_errlist] @0x00000000 ( 2022688)  ent/size:        0/      68  align:       32,
 Elf Sec: [.gnu.warning.sys_nerr] @0x00000000 ( 2022784)  ent/size:        0/      65  align:       32,
 Elf Sec: [   .gnu.warning.gets] @0x00000000 ( 2022880)  ent/size:        0/      57  align:       32,
 Elf Sec: [  .gnu.warning.getpw] @0x00000000 ( 2022944)  ent/size:        0/      58  align:       32,
 Elf Sec: [.gnu.warning.re_max_failures] @0x00000000 ( 2023008)  ent/size:        0/      61  align:       32,
 Elf Sec: [ .gnu.warning.lchmod] @0x00000000 ( 2023072)  ent/size:        0/      47  align:       32,
 Elf Sec: [ .gnu.warning.llseek] @0x00000000 ( 2023136)  ent/size:        0/      63  align:       32,
 Elf Sec: [  .gnu.warning.getwd] @0x00000000 ( 2023200)  ent/size:        0/     122  align:       32,
 Elf Sec: [   .gnu.warning.sstk] @0x00000000 ( 2023328)  ent/size:        0/      45  align:       32,
 Elf Sec: [ .gnu.warning.revoke] @0x00000000 ( 2023392)  ent/size:        0/      47  align:       32,
 Elf Sec: [ .gnu.warning.mktemp] @0x00000000 ( 2023456)  ent/size:        0/      68  align:       32,
 Elf Sec: [   .gnu.warning.gtty] @0x00000000 ( 2023552)  ent/size:        0/      45  align:       32,
 Elf Sec: [   .gnu.warning.stty] @0x00000000 ( 2023616)  ent/size:        0/      45  align:       32,
 Elf Sec: [.gnu.warning.chflags] @0x00000000 ( 2023680)  ent/size:        0/      48  align:       32,
 Elf Sec: [.gnu.warning.fchflags] @0x00000000 ( 2023744)  ent/size:        0/      49  align:       32,
 Elf Sec: [.gnu.warning.__compat_bdflush] @0x00000000 ( 2023808)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.__gets_chk] @0x00000000 ( 2023872)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_space] @0x00000000 ( 2023936)  ent/size:        0/      60  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_init] @0x00000000 ( 2024000)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_append] @0x00000000 ( 2024064)  ent/size:        0/      61  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_alloc] @0x00000000 ( 2024128)  ent/size:        0/      60  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_next] @0x00000000 ( 2024192)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_find] @0x00000000 ( 2024256)  ent/size:        0/      59  align:       32,
 Elf Sec: [ .gnu.warning.getmsg] @0x00000000 ( 2024320)  ent/size:        0/      47  align:       32,
 Elf Sec: [ .gnu.warning.putmsg] @0x00000000 ( 2024384)  ent/size:        0/      47  align:       32,
 Elf Sec: [.gnu.warning.fattach] @0x00000000 ( 2024448)  ent/size:        0/      48  align:       32,
 Elf Sec: [.gnu.warning.fdetach] @0x00000000 ( 2024512)  ent/size:        0/      48  align:       32,
 Elf Sec: [.gnu.warning.setlogin] @0x00000000 ( 2024576)  ent/size:        0/      49  align:       32,
 Elf Sec: [      .gnu_debuglink] @0x00000000 ( 2024628)  ent/size:        0/      20  align:        4,
 Elf Sec: [           .shstrtab] @0x00000000 ( 2024648)  ent/size:        0/    1223  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/amd64/libstdc++.so.6.0.25.viv
0x83788 0x4cf8 0x382000
Out[82]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [  .note.gnu.build-id] @0x00000200 (     512)  ent/size:        0/      36  align:        4,
 Elf Sec: [           .gnu.hash] @0x00000228 (     552)  ent/size:        0/   33808  align:        8,
 Elf Sec: [             .dynsym] @0x00008638 (   34360)  ent/size:       24/  132552  align:        8,
 Elf Sec: [             .dynstr] @0x00028c00 (  166912)  ent/size:        0/  266143  align:        1,
 Elf Sec: [        .gnu.version] @0x00069ba0 (  433056)  ent/size:        2/   11046  align:        2,
 Elf Sec: [      .gnu.version_d] @0x0006c6c8 (  444104)  ent/size:        0/    1292  align:        8,
 Elf Sec: [      .gnu.version_r] @0x0006cbd8 (  445400)  ent/size:        0/     272  align:        8,
 Elf Sec: [           .rela.dyn] @0x0006cce8 (  445672)  ent/size:       24/   92832  align:        8,
 
 Elf Sec: [           .rela.plt] @0x00083788 (  538504)  ent/size:       24/   19704  align:        8,
 
 Elf Sec: [               .init] @0x00088480 (  558208)  ent/size:        0/      23  align:        4,
 Elf Sec: [                .plt] @0x000884a0 (  558240)  ent/size:       16/   13152  align:       16,
 Elf Sec: [            .plt.got] @0x0008b800 (  571392)  ent/size:        0/     184  align:        8,
 Elf Sec: [               .text] @0x0008b8c0 (  571584)  ent/size:        0/  719065  align:       16,
 Elf Sec: [               .fini] @0x0013b19c ( 1290652)  ent/size:        0/       9  align:        4,
 Elf Sec: [             .rodata] @0x0013b1c0 ( 1290688)  ent/size:        0/   33432  align:       32,
 Elf Sec: [       .stapsdt.base] @0x00143458 ( 1324120)  ent/size:        0/       1  align:        1,
 Elf Sec: [       .eh_frame_hdr] @0x0014345c ( 1324124)  ent/size:        0/   30524  align:        4,
 Elf Sec: [           .eh_frame] @0x0014ab98 ( 1354648)  ent/size:        0/  160388  align:        8,
 Elf Sec: [   .gcc_except_table] @0x00171e1c ( 1515036)  ent/size:        0/   25478  align:        4,
 Elf Sec: [               .tbss] @0x00378338 ( 1540920)  ent/size:        0/      32  align:        8,
 Elf Sec: [         .init_array] @0x00378338 ( 1540920)  ent/size:        8/      88  align:        8,
 Elf Sec: [         .fini_array] @0x00378390 ( 1541008)  ent/size:        8/       8  align:        8,
 Elf Sec: [                .jcr] @0x00378398 ( 1541016)  ent/size:        0/       8  align:        8,
 Elf Sec: [        .data.rel.ro] @0x003783a0 ( 1541024)  ent/size:        0/   35240  align:       32,
 Elf Sec: [            .dynamic] @0x00380d48 ( 1576264)  ent/size:       16/     544  align:        8,
 Elf Sec: [                .got] @0x00380f68 ( 1576808)  ent/size:        8/    4248  align:        8,

 Elf Sec: [            .got.plt] @0x00382000 ( 1581056)  ent/size:        8/    6592  align:        8,
 
 Elf Sec: [               .data] @0x003839c0 ( 1587648)  ent/size:        0/     376  align:       32,
 Elf Sec: [                .bss] @0x00383b40 ( 1588024)  ent/size:        0/   14112  align:       32,
 Elf Sec: [       .note.stapsdt] @0x00000000 ( 1588024)  ent/size:        0/     236  align:        4,
 Elf Sec: [      .gnu_debuglink] @0x00000000 ( 1588260)  ent/size:        0/      52  align:        1,
 Elf Sec: [           .shstrtab] @0x00000000 ( 1588312)  ent/size:        0/     316  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/amd64/static64.llvm.elf.viv
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
/home/atlas/bin/vw in <module>()
----> 1 x+=1; print '======================================\n' + vws[x].metadata['StorageName']; ed=vws[x].filemeta.values()[0]['ELF_DYNAMICS']; print hex(ed['DT_JMPREL']), hex(ed['DT_PLTRELSZ']), hex(ed['DT_PLTGOT']); es[x].sections

KeyError: 'DT_JMPREL'
### Static files don't do Dynamics

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/i386/static32.llvm.elf.viv
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
/home/atlas/bin/vw in <module>()
----> 1 x+=1; print '======================================\n' + vws[x].metadata['StorageName']; ed=vws[x].filemeta.values()[0]['ELF_DYNAMICS']; print hex(ed['DT_JMPREL']), hex(ed['DT_PLTRELSZ']), hex(ed['DT_PLTGOT']); es[x].sections

KeyError: 'DT_JMPREL'
### Static files don't do Dynamics

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/i386/libc-2.13.so.viv
0x16b38 0x40 0x158ff4
Out[85]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [  .note.gnu.build-id] @0x00000174 (     372)  ent/size:        0/      36  align:        4,
 Elf Sec: [       .note.ABI-tag] @0x00000198 (     408)  ent/size:        0/      32  align:        4,
 Elf Sec: [           .gnu.hash] @0x000001b8 (     440)  ent/size:        4/   15416  align:        4,
 Elf Sec: [             .dynsym] @0x00003df0 (   15856)  ent/size:       16/   37376  align:        4,
 Elf Sec: [             .dynstr] @0x0000cff0 (   53232)  ent/size:        0/   23245  align:        1,
 Elf Sec: [        .gnu.version] @0x00012abe (   76478)  ent/size:        2/    4672  align:        2,
 Elf Sec: [      .gnu.version_d] @0x00013d00 (   81152)  ent/size:        0/     984  align:        4,
 Elf Sec: [      .gnu.version_r] @0x000140d8 (   82136)  ent/size:        0/      64  align:        4,
 Elf Sec: [            .rel.dyn] @0x00014118 (   82200)  ent/size:        8/   10784  align:        4,
 
 Elf Sec: [            .rel.plt] @0x00016b38 (   92984)  ent/size:        8/      64  align:        4,
 
 Elf Sec: [                .plt] @0x00016b78 (   93048)  ent/size:        4/     144  align:        4,
 Elf Sec: [               .text] @0x00016c10 (   93200)  ent/size:        0/ 1083604  align:       16,
 Elf Sec: [   __libc_freeres_fn] @0x0011f4f0 ( 1176816)  ent/size:        0/    4040  align:       16,
 Elf Sec: [__libc_thread_freeres_fn] @0x001204c0 ( 1180864)  ent/size:        0/     386  align:       16,
 Elf Sec: [             .rodata] @0x00120660 ( 1181280)  ent/size:        0/  112648  align:       32,
 Elf Sec: [             .interp] @0x0013be68 ( 1293928)  ent/size:        0/      19  align:        1,
 Elf Sec: [       .eh_frame_hdr] @0x0013be7c ( 1293948)  ent/size:        0/   13116  align:        4,
 Elf Sec: [           .eh_frame] @0x0013f1b8 ( 1307064)  ent/size:        0/   78516  align:        4,
 Elf Sec: [   .gcc_except_table] @0x0015246c ( 1385580)  ent/size:        0/    1473  align:        1,
 Elf Sec: [               .hash] @0x00152a30 ( 1387056)  ent/size:        4/   13444  align:        4,
 Elf Sec: [              .tdata] @0x001571c8 ( 1401288)  ent/size:        0/       8  align:        4,
 Elf Sec: [               .tbss] @0x001571d0 ( 1401296)  ent/size:        0/      56  align:        4,
 Elf Sec: [         .fini_array] @0x001571d0 ( 1401296)  ent/size:        0/       4  align:        4,
 Elf Sec: [              .ctors] @0x001571d4 ( 1401300)  ent/size:        0/      20  align:        4,
 Elf Sec: [              .dtors] @0x001571e8 ( 1401320)  ent/size:        0/       8  align:        4,
 Elf Sec: [   __libc_subfreeres] @0x001571f0 ( 1401328)  ent/size:        0/     112  align:        4,
 Elf Sec: [       __libc_atexit] @0x00157260 ( 1401440)  ent/size:        0/       4  align:        4,
 Elf Sec: [__libc_thread_subfreeres] @0x00157264 ( 1401444)  ent/size:        0/      12  align:        4,
 Elf Sec: [        .data.rel.ro] @0x00157280 ( 1401472)  ent/size:        0/    6908  align:       32,
 Elf Sec: [            .dynamic] @0x00158d7c ( 1408380)  ent/size:        8/     240  align:        4,
 Elf Sec: [                .got] @0x00158e6c ( 1408620)  ent/size:        4/     372  align:        4,
 
 Elf Sec: [            .got.plt] @0x00158ff4 ( 1409012)  ent/size:        4/      44  align:        4,
 
 Elf Sec: [               .data] @0x00159020 ( 1409056)  ent/size:        0/    2428  align:       32,
 Elf Sec: [                .bss] @0x001599a0 ( 1411484)  ent/size:        0/   12392  align:       32,
 Elf Sec: [.gnu.warning.sigstack] @0x00000000 ( 1411488)  ent/size:        0/      77  align:       32,
 Elf Sec: [.gnu.warning.sigreturn] @0x00000000 ( 1411584)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.siggetmask] @0x00000000 ( 1411648)  ent/size:        0/      57  align:       32,
 Elf Sec: [ .gnu.warning.tmpnam] @0x00000000 ( 1411712)  ent/size:        0/      55  align:       32,
 Elf Sec: [.gnu.warning.tmpnam_r] @0x00000000 ( 1411776)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.tempnam] @0x00000000 ( 1411840)  ent/size:        0/      56  align:       32,
 Elf Sec: [.gnu.warning.sys_errlist] @0x00000000 ( 1411904)  ent/size:        0/      68  align:       32,
 Elf Sec: [.gnu.warning.sys_nerr] @0x00000000 ( 1412000)  ent/size:        0/      65  align:       32,
 Elf Sec: [   .gnu.warning.gets] @0x00000000 ( 1412096)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.__memset_zero_constant_len_parameter] @0x00000000 ( 1412153)  ent/size:        0/     184  align:        1,
 Elf Sec: [  .gnu.warning.getpw] @0x00000000 ( 1412352)  ent/size:        0/      58  align:       32,
 Elf Sec: [.gnu.warning.re_max_failures] @0x00000000 ( 1412416)  ent/size:        0/      61  align:       32,
 Elf Sec: [.gnu.warning.setlogin] @0x00000000 ( 1412480)  ent/size:        0/      58  align:       32,
 Elf Sec: [  .gnu.warning.getwd] @0x00000000 ( 1412544)  ent/size:        0/     122  align:       32,
 Elf Sec: [ .gnu.warning.lchmod] @0x00000000 ( 1412672)  ent/size:        0/      56  align:       32,
 Elf Sec: [   .gnu.warning.sstk] @0x00000000 ( 1412736)  ent/size:        0/      54  align:       32,
 Elf Sec: [ .gnu.warning.mktemp] @0x00000000 ( 1412800)  ent/size:        0/      68  align:       32,
 Elf Sec: [   .gnu.warning.gtty] @0x00000000 ( 1412896)  ent/size:        0/      54  align:       32,
 Elf Sec: [   .gnu.warning.stty] @0x00000000 ( 1412960)  ent/size:        0/      54  align:       32,
 Elf Sec: [.gnu.warning.chflags] @0x00000000 ( 1413024)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.fchflags] @0x00000000 ( 1413088)  ent/size:        0/      58  align:       32,
 Elf Sec: [ .gnu.warning.revoke] @0x00000000 ( 1413152)  ent/size:        0/      56  align:       32,
 Elf Sec: [ .gnu.warning.llseek] @0x00000000 ( 1413216)  ent/size:        0/      63  align:       32,
 Elf Sec: [.gnu.warning.__gets_chk] @0x00000000 ( 1413280)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_space] @0x00000000 ( 1413344)  ent/size:        0/      60  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_init] @0x00000000 ( 1413408)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_append] @0x00000000 ( 1413472)  ent/size:        0/      61  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_alloc] @0x00000000 ( 1413536)  ent/size:        0/      60  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_next] @0x00000000 ( 1413600)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.inet6_option_find] @0x00000000 ( 1413664)  ent/size:        0/      59  align:       32,
 Elf Sec: [.gnu.warning.fattach] @0x00000000 ( 1413728)  ent/size:        0/      57  align:       32,
 Elf Sec: [.gnu.warning.fdetach] @0x00000000 ( 1413792)  ent/size:        0/      57  align:       32,
 Elf Sec: [      .gnu_debuglink] @0x00000000 ( 1413849)  ent/size:        0/      20  align:        1,
 Elf Sec: [           .shstrtab] @0x00000000 ( 1413869)  ent/size:        0/    1165  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/i386/libstdc++.so.6.0.25.viv
0x69470 0x1a10 0x182000
Out[86]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [  .note.gnu.build-id] @0x00000134 (     308)  ent/size:        0/      36  align:        4,
 Elf Sec: [           .gnu.hash] @0x00000158 (     344)  ent/size:        4/   33608  align:        4,
 Elf Sec: [             .dynsym] @0x000084a0 (   33952)  ent/size:       16/   87920  align:        4,
 Elf Sec: [             .dynstr] @0x0001dc10 (  121872)  ent/size:        0/  265462  align:        1,
 Elf Sec: [        .gnu.version] @0x0005e906 (  387334)  ent/size:        2/   10990  align:        2,
 Elf Sec: [      .gnu.version_d] @0x000613f4 (  398324)  ent/size:        0/    1436  align:        4,
 Elf Sec: [      .gnu.version_r] @0x00061990 (  399760)  ent/size:        0/     336  align:        4,
 Elf Sec: [            .rel.dyn] @0x00061ae0 (  400096)  ent/size:        8/   31120  align:        4,
 
 Elf Sec: [            .rel.plt] @0x00069470 (  431216)  ent/size:        8/    6672  align:        4,
 
 Elf Sec: [               .init] @0x0006ae80 (  437888)  ent/size:        0/      35  align:        4,
 Elf Sec: [                .plt] @0x0006aeb0 (  437936)  ent/size:        4/   13360  align:       16,
 Elf Sec: [            .plt.got] @0x0006e2e0 (  451296)  ent/size:        8/     184  align:        8,
 Elf Sec: [               .text] @0x0006e3a0 (  451488)  ent/size:        0/  776532  align:       16,
 Elf Sec: [               .fini] @0x0012bcf4 ( 1228020)  ent/size:        0/      20  align:        4,
 Elf Sec: [             .rodata] @0x0012bd20 ( 1228064)  ent/size:        0/   30436  align:       32,
 Elf Sec: [       .stapsdt.base] @0x00133404 ( 1258500)  ent/size:        0/       1  align:        1,
 Elf Sec: [       .eh_frame_hdr] @0x00133408 ( 1258504)  ent/size:        0/   32580  align:        4,
 Elf Sec: [           .eh_frame] @0x0013b34c ( 1291084)  ent/size:        0/  236468  align:        4,
 Elf Sec: [   .gcc_except_table] @0x00174f00 ( 1527552)  ent/size:        0/   27108  align:        4,
 Elf Sec: [               .tbss] @0x0017ceb0 ( 1556144)  ent/size:        0/      16  align:        4,
 Elf Sec: [         .init_array] @0x0017ceb0 ( 1556144)  ent/size:        4/      44  align:        4,
 Elf Sec: [         .fini_array] @0x0017cedc ( 1556188)  ent/size:        4/       4  align:        4,
 Elf Sec: [        .data.rel.ro] @0x0017cee0 ( 1556192)  ent/size:        0/   18276  align:       32,
 Elf Sec: [            .dynamic] @0x00181644 ( 1574468)  ent/size:        8/     272  align:        4,
 Elf Sec: [                .got] @0x00181754 ( 1574740)  ent/size:        4/    2196  align:        4,
 
 Elf Sec: [            .got.plt] @0x00182000 ( 1576960)  ent/size:        4/    3348  align:        4,
 
 Elf Sec: [               .data] @0x00182d20 ( 1580320)  ent/size:        0/     204  align:       32,
 Elf Sec: [                .bss] @0x00182e00 ( 1580524)  ent/size:        0/    8760  align:       32,
 Elf Sec: [       .note.stapsdt] @0x00000000 ( 1580524)  ent/size:        0/     192  align:        4,
 Elf Sec: [      .gnu_debuglink] @0x00000000 ( 1580716)  ent/size:        0/      52  align:        4,
 Elf Sec: [           .shstrtab] @0x00000000 ( 1580768)  ent/size:        0/     309  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//linux/arm/sh.viv
0xaca8 0x928 0x49490
Out[87]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [             .interp] @0x000080d4 (     212)  ent/size:        0/      19  align:        1,
 Elf Sec: [               .hash] @0x000080e8 (     232)  ent/size:        4/    2392  align:        4,
 Elf Sec: [             .dynsym] @0x00008a40 (    2624)  ent/size:       16/    5328  align:        4,
 Elf Sec: [             .dynstr] @0x00009f10 (    7952)  ent/size:        0/    2692  align:        1,
 Elf Sec: [        .gnu.version] @0x0000a994 (   10644)  ent/size:        2/     666  align:        2,
 Elf Sec: [      .gnu.version_r] @0x0000ac30 (   11312)  ent/size:        0/      64  align:        4,
 Elf Sec: [            .rel.dyn] @0x0000ac70 (   11376)  ent/size:        8/      56  align:        4,
 
 Elf Sec: [            .rel.plt] @0x0000aca8 (   11432)  ent/size:        8/    2344  align:        4,
 
 Elf Sec: [               .init] @0x0000b5d0 (   13776)  ent/size:        0/      20  align:        4,
 Elf Sec: [                .plt] @0x0000b5e4 (   13796)  ent/size:        4/    3536  align:        4,
 Elf Sec: [               .text] @0x0000c3b8 (   17336)  ent/size:        0/  175376  align:        8,
 Elf Sec: [               .fini] @0x000370c8 (  192712)  ent/size:        0/      16  align:        4,
 Elf Sec: [             .rodata] @0x000370d8 (  192728)  ent/size:        0/   41656  align:        4,
 Elf Sec: [           .eh_frame] @0x00041390 (  234384)  ent/size:        0/       4  align:        4,
 Elf Sec: [         .init_array] @0x00049394 (  234388)  ent/size:        0/       4  align:        4,
 Elf Sec: [         .fini_array] @0x00049398 (  234392)  ent/size:        0/       4  align:        4,
 Elf Sec: [                .jcr] @0x0004939c (  234396)  ent/size:        0/       4  align:        4,
 Elf Sec: [            .dynamic] @0x000493a0 (  234400)  ent/size:        8/     240  align:        4,
 
 Elf Sec: [                .got] @0x00049490 (  234640)  ent/size:        4/    1192  align:        4,
 
 Elf Sec: [               .data] @0x00049938 (  235832)  ent/size:        0/    1136  align:        4,
 Elf Sec: [                .bss] @0x00049da8 (  236968)  ent/size:        0/   27032  align:        8,
 Elf Sec: [     .ARM.attributes] @0x00000000 (  236968)  ent/size:        0/      16  align:        1,
 Elf Sec: [           .shstrtab] @0x00000000 (  236984)  ent/size:        0/     193  align:        1]

======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//qnx/arm/ksh.viv
0x102d5c 0x7d8 0x146a10
Out[88]: 
[Elf Sec: [                    ] @0x00000000 (       0)  ent/size:        0/       0  align:        0,
 Elf Sec: [            QNX_info] @0x00000000 (  288368)  ent/size:        0/     147  align:        0,
 Elf Sec: [           .shstrtab] @0x00000000 (  288515)  ent/size:        0/      20  align:        1]
### QNX doesn't "do" Sections.


======================================
/home/atlas/hacking/git/atlas0fd00m/vivtestfiles//openbsd/ls.amd64.viv
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
/home/atlas/bin/vw in <module>()
----> 1 x+=1; print '======================================\n' + vws[x].metadata['StorageName']; ed=vws[x].filemeta.values()[0]['ELF_DYNAMICS']; print hex(ed['DT_JMPREL']), hex(ed['DT_PLTRELSZ']), hex(ed['DT_PLTGOT']); es[x].sections

KeyError: 'DT_JMPREL'
### OpenBSD doesn't "do" Dynamics.


'''
