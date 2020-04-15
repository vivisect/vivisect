
"""
If a "function" is in the plt it's a wrapper for something in the GOT.
Make that apparent.
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


def analyzePLT(vw, ssva, ssize):
        # make code for every opcode in PLT
        sva = ssva
        nextseg = sva + ssize

        trampbr = None
        has_tramp = False

        branchvas = []
        while sva < nextseg:
            if vw.getLocation(sva) is None:
                logger.info('making code: 0x%x', sva)
                try:
                    vw.makeCode(sva)
                except Exception as e:
                    logger.exception('0x%x: exception: %r', sva, e)

            ltup = vw.getLocation(sva)

            if ltup is not None:
                op = vw.parseOpcode(ltup[vivisect.L_VA])
                if op.iflags & envi.IF_BRANCH and \
                        not op.iflags & envi.IF_COND:

                    # we grab all unconditional branches, and tag them
                    realplt = not bool(op.opers[-1].getOperValue(op) == ssva)
                    if not realplt:
                        has_tramp = True

                    branchvas.append((op.va, realplt))

                sva += ltup[vivisect.L_SIZE]
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
                branchvas[0] = (trampbr, False)
            else:
                logger.debug("has_tramp: trampbr: 0x%x    branchvas[0][0]: 0x%x", trampbr, branchvas[0][0])

        # heuristically determine PLT entry size and distance
        heur = {}
        lastva = ssva
        # first determine distance between GOT branches:
        for vidx in range(1, len(branchvas)):
            bva, realplt = branchvas[vidx]
            if not realplt:
                continue

            delta = bva - lastva
            lastva = bva
            heur[delta] = heur.get(delta, 0) + 1

        heurlist = [(y, x) for x, y in heur.items()]
        heurlist.sort()

        # distance should be the greatest value.
        plt_distance = heurlist[-1][1]
        logger.debug('plt_distance : 0x%x\n%r', plt_distance, heurlist)

        # there should be only one heuristic
        if len(heurlist) > 1:
            logger.warn("heuristics have more than one tracked branch: investigate!  PLT analysis is likely to be wrong (%r)", heurlist)

        # now determine plt_size (basically, how far to backup from the branch to find the start of function
        # *don't* use the first entry, because the trampoline is often odd...
        plt_size = 0    # not including the branch instruction size?
        bridx = 1

        # if has_tramp, we need to skip two to make sure we're not analyzing the first real plt
        if has_tramp:    
            bridx += 1

        brva, realplt = branchvas[bridx]
        while brva != trampbr and not realplt:
            bridx += 1
            brva, realplt = branchvas[bridx]

        # start off pointing at the branch location which bounces through GOT.
        loc = vw.getLocation(brva)
        # grab the size of the plt branch instruction for our benefit
        pltbrsz = loc[vivisect.L_SIZE]

        # we're searching for a point where either we hit:
        #  * another branch/NO_FALL (ie. lazy-loader) or
        #  * non-Opcode (eg. literal pool)
        #  * or a NOP
        # bounded to what we know is the distance between PLT branches
        while loc is not None and \
                plt_size <= plt_distance:
            # first we back up one location
            loc = vw.getLocation(loc[vivisect.L_VA] - 1)
            lva, lsz, ltype, ltinfo = loc

            if ltype != vivisect.LOC_OP:
                # we've run into a non-opcode location: bail!
                break

            if ltinfo & envi.IF_BRANCH:
                # we've hit another branch instruction.  stop!
                break

            op = vw.parseOpcode(lva)
            if op.mnem == 'nop':    # should we let architectures set a "nop" iflag
                # we've run into inter-plt padding - curse you, i386 gcc!
                break

            plt_size += lsz

        # now get start of first real PLT entry
        bridx = 0
        brlen = len(branchvas)

        firstbr, realplt = branchvas[bridx]
        # roll through branches until we find one we like as the start of the real plts
        while bridx < brlen:
            firstbr, realplt = branchvas[bridx]
            if realplt:
                firstva = firstbr - plt_size
                prevloc = vw.getLocation(firstva - 1)
                if prevloc is None:
                    # perhaps this is ok?
                    logger.debug("NOT firstva: 0x%x - preceeded by loctup==None", firstva)
                    bridx += 1
                    continue
                plva, plsz, pltp, pltinfo = prevloc
                if pltp == vivisect.LOC_OP:
                    if pltinfo & envi.IF_NOFALL:
                        # the previous instruction is IF_NOFALL!  good.
                        logger.debug("firstva found: preceeded by IF_NOFALL")
                        break
                    op = vw.parseOpcode(plva)
                    if op.mnem == 'nop':
                        # ugly, but effective:
                        logger.debug("firstva found: preceeded by 'nop'")
                        break
                else:
                    # we've hit a non-LOC_OP... that seems like this is the start of func
                    logger.debug("firstva found: preceeded by non-LOC_OP")
                    break
            bridx += 1


        logger.debug('plt first entry: 0x%x\n%r', firstva, [(hex(x), y) for x, y in branchvas])

        if bridx != 0:
            logger.debug('First function in PLT is not a PLT entry.  Found Lazy Loader Trampoline.')
            vw.makeName(ssva, 'LazyLoaderTrampoline', filelocal=True)

        # scroll through arbitrary length functions and make functions
        for sva in range(firstva, nextseg, plt_distance):
            logger.info('making PLT function: 0x%x', sva)
            vw.makeFunction(sva)


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
    gotplt = None
    # Thought:  This is DT_PLTGOT, although each ELF will/may have their own DT_PLTGOT.
    for va, size, name, fname in vw.getSegments():
        if name == ".got.plt":
            gotplt = va
            break

    if gotplt is None:
        gotplt = -1

    # all architectures should at least have some minimal emulator
    emu = vw.getEmulator()
    emu.setRegister(e_i386.REG_EBX, gotplt)  # every emulator will have a 4th register, and if it's not used, no harm done.

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
            if loctup is None:
                logger.exception('0x%x: opval=0x%x: brflags is BR_DEREF, but loctup is None.  Don\'t know what to do. skipping.', op.va, opval)
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


def dbg_interact(lcls, gbls):
    intro = "Let's interact!"
    try:
        import IPython.Shell
        ipsh = IPython.Shell.IPShell(argv=[''], user_ns=lcls, user_global_ns=gbls)
        print(intro)
        ipsh.mainloop()

    except ImportError as e:
        try:
            from IPython.terminal.interactiveshell import TerminalInteractiveShell
            ipsh = TerminalInteractiveShell()
            ipsh.user_global_ns.update(gbls)
            ipsh.user_global_ns.update(lcls)
            ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!
            print(intro)
            ipsh.mainloop()
        except ImportError as e:
            try:
                from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell
                ipsh = TerminalInteractiveShell()
                ipsh.user_global_ns.update(gbls)
                ipsh.user_global_ns.update(lcls)
                ipsh.autocall = 2       # don't require parenthesis around *everything*.  be smart!

                print(intro)
                ipsh.mainloop()
            except ImportError, e:
                print(e)
                shell = code.InteractiveConsole(gbls)
                print(intro)
                shell.interact()


