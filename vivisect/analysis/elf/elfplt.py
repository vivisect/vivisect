
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

        branchvas = []
        while sva < nextseg:
            if vw.getLocation(sva) is None:
                logger.info('making code: 0x%x', sva)
                try:
                    vw.makeCode(sva)
                except Exception as e:
                    logger.warn('0x%x: exception: %r', sva, e)

            ltup = vw.getLocation(sva)

            if ltup is not None:
                op = vw.parseOpcode(ltup[vivisect.L_VA])
                if op.iflags & envi.IF_BRANCH and \
                        not op.iflags & envi.IF_COND and \
                        not op.opers[-1].getOperValue(op) == ssva:
                    branchvas.append(op.va)

                sva += ltup[vivisect.L_SIZE]
                logger.debug('incrementing to next va: 0x%x', sva)
            else:
                logger.warn('makeCode(0x%x) failed to make a location (probably failed instruction decode)!  incrementing instruction pointer by 1 to continue PLT analysis <fingers crossed>', sva)
                sva += 1


        if not len(branchvas):
            return

        # heuristically determine PLT entry size
        heur = {}
        lastva = ssva
        for vidx in range(1, len(branchvas)):
            bva = branchvas[vidx]
            delta = bva - lastva
            lastva = bva
            heur[delta] = heur.get(delta, 0) + 1

        heurlist = [(y, x) for x, y in  heur.items()]
        heurlist.sort()

        plt_size = heurlist[-1][1]
        logger.debug('plt_size: 0x%x\n%r', plt_size, heurlist)

        # now get start of first real PLT entry
        bridx = 0
        brlen = len(branchvas)
        while bridx < brlen - 1:
            firstbr = branchvas[bridx]
            if branchvas[bridx+1] - firstbr == plt_size:
                break
            bridx += 1

        firstva = firstbr - plt_size + 4 # size of ARM opcode
        logger.debug('plt first entry: 0x%x\n%r', firstva, [hex(x) for x in branchvas])

        if bridx != 0:
            logger.debug('First function in PLT is not a PLT entry.  Found Lazy Loader Trampoline.')
            vw.makeName(ssva, 'LazyLoaderTrampoline', filelocal=True)

        # scroll through arbitrary length functions and make functions
        for sva in range(firstva, nextseg, plt_size):
            logger.info('making PLT function: 0x%x', sva)
            vw.makeFunction(sva)
            analyzeFunction(vw, sva)


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
            logger.warn('0x%x: not part of ".plt" or ".plt.got"', funcva)
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

    branches = op.getBranches(emu)
    if len(branches) != 1:
        logger.warn('getBranches() returns anomolous results: 0x%x: %r   (result: %r)',
                op.va, op, branches)
        return

    # get opval (the target of the jump, or the taint) and opref (the reference used to find it)
    opref = op.opers[-1].getOperAddr(op, emu)  # HACK: this assumes the target is the last operand!
    opval, brflags = branches[0]
    if opval is None:
        logger.warn("getBranches():  opval is None!:  op = %r     branches = %r", op, branches)
    else:
        logger.debug('getBranches():  ref: 0x%x  brflags: 0x%x', opval, brflags)

    # add the xref to whatever location referenced (assuming the opref hack worked)
    if vw.isValidPointer(opref):
        logger.debug('reference 0x%x is valid, adding Xref', opref)
        vw.addXref(op.va, opref, vivisect.REF_DATA)

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
        logger.debug('0x%x: LOC_IMPORT: 0x%x:  %r', opva, lva, funcname)
        
    else:
        # instead of a taint (which *should* indicate an IMPORT), we have real pointer.
        loctup = vw.getLocation(opval)
        # check the location type
        if loctup is None:
            if opval is None:
                logger.warn("PLT: 0x%x - branch deref not defined: (opval is None!)", opva)
                return
            else:
                logger.warn("PLT: 0x%x - making function at location 0x%x", opva, opval)
                vw.makeFunction(opval)

        # in case the architecture cares about the function address...
        aopval, aflags = vw.arch.archModifyFuncAddr(opval, {})
        funcname = vw.getName(aopval)
        if funcname is None:
            funcname = vw.getName(opval)

        if vw.getFunction(aopval) is None:
            logger.debug("0x%x: code does not exist at 0x%x.  calling makeFunction()", funcva, aopval)
            vw.makeFunction(aopval, arch=aflags['arch'])

        # this "thunk" actually calls something in the workspace, that exists as a function...
        logger.info('0x%x points to real code (0x%x: %r)', funcva, opval, funcname)
        vw.addXref(op.va, aopval, vivisect.REF_CODE)
        vw.setVaSetRow('FuncWrappers', (funcva, opval))


        #if loctup[vivisect.L_LTYPE] == vivisect.LOC_POINTER:  # Some AMD64 PLT entries point at nameless relocations that point internally
        #    tgtva = loctup[vivisect.L_VA]
        #    ptrva = vw.readMemoryPtr(tgtva)
        #    ptrname = vw.getName(ptrva)
        #    logger.info("PLT->PTR 0x%x: (0x%x)  -> 0x%x -> 0x%x (%r)" % (funcva, opval, tgtva, ptrva, ptrname))
        #    if vw.isValidPointer(ptrva):
        #        if funcname is None:
        #            funcname = vw._addNamePrefix(ptrname, ptrva, 'ptr', '_')

        #elif loctup[vivisect.L_LTYPE] == vivisect.LOC_IMPORT:
        if loctup[vivisect.L_LTYPE] == vivisect.LOC_IMPORT:
            logger.warn("0x%x: (0x%x) FAIL: dest is LOC_IMPORT but missed taint for %r", funcva, opval, funcname)
            return

        elif loctup[vivisect.L_LTYPE] == vivisect.LOC_OP:
            logger.debug("0x%x: succeeded finding LOC_OP at the end of the rainbow! (%r)", funcva, funcname)

        if vw.getFunction(opval) == segva:
            # this is a lazy-link/load function, calling the first entry in the PLT
            logger.debug('skipping lazy-loader function: 0x%x (calls 0x%x)', funcva, opval)
            return

    # if we can't resolve a name, don't make it a thunk
    if funcname is None:
        logger.warn('0x%x: FAIL: could not resolve name for 0x%x.  Skipping.', funcva, opval)
        return

    # trim up the name
    if funcname.startswith('*.'):
        funcname = funcname[2:]
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


