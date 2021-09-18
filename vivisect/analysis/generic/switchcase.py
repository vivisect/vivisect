'''
Analysis plugin for supporting WorkspaceEmulators during analysis pass.
Finds and connects Switch Cases, most specifically from Microsoft.
'''

import envi
import envi.archs.i386 as e_i386
import envi.const as e_const

import vivisect.const as v_const
import vivisect.analysis.generic.codeblocks as vagc

import logging

logger = logging.getLogger(__name__)


def analyzeJmp(amod, emu, op, starteip):
    '''
    Top level logic
    '''
    vw = emu.vw
    ctx = getSwitchBase(vw, op, starteip, emu)
    if ctx is not None:
        tova, scale = ctx
        fva = vw.getFunction(starteip)
        vw.makePointer(tova, follow=False)
        vw.makeJumpTable(op, tova, rebase=True, psize=scale)
        # so the codeblocks this jumptable points to aren't proper locations...yet.
        # let's fix that up and kick off codeblock analysis to make the codeblocks
        for xrfrom, xrto, xrtype, xrflags in vw.getXrefsFrom(op.va, rtype=v_const.REF_CODE):
            vw.makeCode(xrto, fva=fva)
        vagc.analyzeFunction(vw, fva)


def getRealRegIdx(emu, regidx):
    return emu.getRegisterIndex(emu.getRealRegisterNameByIdx(regidx))


def findOp(vw, emu, startOp, mnem, regidx=None):
    cb = vw.getCodeBlock(startOp.va)
    backLoc = vw.getLocation(startOp.va - 1)
    while backLoc is not None and vw.getCodeBlock(backLoc[v_const.L_VA]) == cb:
        backOp = vw.parseOpcode(backLoc[0])
        if len(backOp.opers):
            oper = backOp.opers[0]
            if backOp.mnem == mnem:
                if regidx is not None:
                    if oper.isReg() and getRealRegIdx(emu, oper.reg) == regidx:
                        return backOp
                else:
                    return backOp
        backLoc = vw.getLocation(backLoc[0] - 1)


def scanUp(vw, emu, startva, regidx, valu):
    cb = vw.getCodeBlock(startva)
    loc = vw.getLocation(startva)
    while loc is not None and vw.getCodeBlock(loc[v_const.L_VA]) == cb:
        op = vw.parseOpcode(loc[0])
        if len(op.opers) > 1 and op.opers[0].isReg() and getRealRegIdx(emu, op.opers[0].reg) == regidx:
            if valu == emu.getOperValue(op, 1):
                return True
        loc = vw.getLocation(loc[0] - 1)

    return False


def getSwitchBase(vw, op, vajmp, emu=None):
    if not (op.iflags & envi.IF_BRANCH):
        return

    filename = vw.getMemoryMap(vajmp)[3]
    imgbase = vw.getFileMeta(filename, 'imagebase')

    if not op.opers[0].isReg():
        return

    reg = op.opers[0].reg
    if reg & e_const.RMETA_NMASK != reg:
        reg = getRealRegIdx(emu, reg)

    # Search up instructions until we get to the actual assignment of our
    # jump register, which should be an add in 64 bit town
    addOp = findOp(vw, emu, op, 'add', reg)
    if addOp is None:
        return

    regbase = addOp.getOperValue(1, emu)
    if regbase != imgbase:
        # just in case let's check a few more instructions up, because the first register could be
        # being used as the base instead (which means the second register is being used as the selector)
        if not scanUp(vw, emu, addOp.va, reg, imgbase):
            logger.info("0x%x: reg != imagebase (0x%x != 0x%x)" % (op.va, regbase, imgbase))
            return

    # Now find the instruction before the add that does the actual mov
    movOp = findOp(vw, emu, addOp, 'mov', reg)
    if movOp is None:
        # try the other one just in case
        reg = getRealRegIdx(emu, addOp.opers[1].reg)
        movOp = findOp(vw, emu, addOp, 'mov', reg)
        if movOp is None:
            return

    # TODO: Want a more arch-independent way of doing this
    arrayOper = movOp.opers[1]
    if not isinstance(arrayOper, e_i386.i386SibOper):
        logger.info("0x%x: arrayOper is not an i386SibOper: %s" % (op.va, repr(arrayOper)))
        return

    if arrayOper.scale % 4 != 0:
        logger.info("0x%x: arrayoper scale is wrong: (%d mod 4 != 0)" % (op.va, arrayOper.scale))
        return

    scale = arrayOper.scale
    disp = arrayOper.disp
    tova = disp + imgbase

    # now check for the byte array before that. this one is optional. first two are not.
    # but honestly, not a whole lot to do here other than make an xref
    indirOp = findOp(vw, emu, movOp, 'movzx', None)
    if indirOp is not None:
        if len(indirOp.opers):
            oper = indirOp.opers[1]
            if isinstance(oper, e_i386.i386SibOper) and oper.scale == 1:
                logger.info("0x%.8x (i:0x%.8x): Double deref (hitting a byte array offset into the offset-array)" % (vajmp, indirOp.va))
                indirVa = oper.disp + imgbase
                vw.addLocation(indirVa, 1, v_const.LOC_NUMBER, "DerefTable")
                vw.addXref(indirOp.va, indirVa, v_const.REF_DATA)

    return (tova, scale)


if 'vw' in globals():
    vw = globals()['vw']
    vw.vprint("Starting Switchcase Module...")
    for va, reprOp, flags in vw.getVaSetRows('DynamicBranches'):
        op = vw.parseOpcode(va)
        if op is None:
            vw.vprint("Cannot analyze none op at 0x%x" % va)
            continue
        analyzeJmp(None, vw.getEmulator(), op, va)  # it doesn't use archmod anyway
    vw.vprint("Switchcase Done")
