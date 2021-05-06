import logging

import vivisect
import vivisect.exc as v_exc
import vivisect.impemu.monitor as viv_monitor
import vivisect.analysis.generic.codeblocks as viv_cb

import envi
import envi.archs.arm as e_arm

from envi.archs.arm.regs import *
from envi.archs.arm.const import *

from vivisect.const import *

logger = logging.getLogger(__name__)


class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva, verbose=True):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()
        self.last_lr_pc = 0
        self.strictops = False
        self.returns = False
        self.infloops = []
        self.switchcases = 0

    def prehook(self, emu, op, starteip):

        try:
            tmode = emu.getFlag(PSR_T_bit)
            self.last_tmode = tmode
            if op in self.badops:
                emu.stopEmu()
                raise v_exc.BadOpBytes(op.va)

            viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

            loctup = emu.vw.getLocation(starteip)
            if loctup is None:
                # logger.debug("emulation: prehook: new LOC_OP  fva: 0x%x     starteip: 0x%x  flags: 0x%x", self.fva, starteip, op.iflags)
                arch = (envi.ARCH_ARMV7, envi.ARCH_THUMB)[(starteip & 1) | tmode]
                emu.vw.makeCode(starteip & -2, arch=arch)

            elif loctup[2] != LOC_OP:
                logger.info("ARG! emulation found opcode in an existing NON-OPCODE location  (0x%x):  0x%x: %s", loctup[0], op.va, op)
                emu.stopEmu()

            elif loctup[0] != starteip:
                logger.info("ARG! emulation found opcode in a location at the wrong address (0x%x):  0x%x: %s", loctup[0], op.va, op)
                emu.stopEmu()

            if op.iflags & envi.IF_RET:
                self.returns = True
                if len(op.opers):
                    if hasattr(op.opers, 'imm'):
                        self.retbytes = op.opers[0].imm

            # ARM gives us nice switchcase handling instructions
            # FIXME: wrap TB-handling into getBranches(emu) which is called by checkBranches during emulation
            if op.opcode in (INS_TBH, INS_TBB):
                if emu.vw.getVaSetRow('SwitchCases', op.va) is None:
                    base, tbl = analyzeTB(emu, op, starteip, self)
                    if None not in (base, tbl):
                        count = len(tbl)
                        self.switchcases += 1
                        emu.vw.setVaSetRow('SwitchCases', (op.va, op.va, count))

            elif op.opcode == INS_MOV:
                if len(op.opers) >= 2:
                    oper0 = op.opers[0]
                    oper1 = op.opers[1]

                    if isinstance(oper0, e_arm.ArmRegOper) and oper0.reg == REG_LR:
                        if isinstance(oper1, e_arm.ArmRegOper) and oper1.reg == REG_PC:
                            self.last_lr_pc = starteip

            elif op.opcode == INS_BX:
                if starteip - self.last_lr_pc <= 4:
                    # this is a call.  the compiler updated lr
                    logger.info("CALL by mov lr, pc; bx <foo> at 0x%x", starteip)
                    tgtva = op.opers[-1].getOperValue(op)
                    self.vw.makeFunction(tgtva)

            elif op.opcode == INS_ADD and op.opers[0].reg == REG_PC:
                # simple branch code
                if emu.vw.getVaSetRow('SwitchCases', op.va) is None:
                    base, tbl = analyzeADDPC(emu, op, starteip, self)
                    if None not in (base, tbl):
                        count = len(tbl)
                        self.switchcases += 1
                        emu.vw.setVaSetRow('SwitchCases', (op.va, op.va, count))

            elif op.opcode == INS_SUB and isinstance(op.opers[0], e_arm.ArmRegOper) and op.opers[0].reg == REG_PC:
                # simple branch code
                if emu.vw.getVaSetRow('SwitchCases', op.va) is None:
                    base, tbl = analyzeSUBPC(emu, op, starteip, self)
                    if None not in (base, tbl):
                        count = len(tbl)
                        self.switchcases += 1
                        emu.vw.setVaSetRow('SwitchCases', (op.va, op.va, count))

            if op.iflags & envi.IF_BRANCH:
                try:
                    tgt = op.getOperValue(0, emu)

                    if tgt == op.va:
                        logger.info("0x%x: +++++++++++++++ infinite loop +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", op.va)
                        if op.va not in self.infloops:
                            self.infloops.append(op.va)
                            if 'InfiniteLoops' not in self.vw.getVaSetNames():
                                self.vw.addVaSet('InfiniteLoops', (('va', vivisect.VASET_ADDRESS, 'function', vivisect.VASET_STRING)))
                            self.vw.setVaSetRow('InfiniteLoops', (op.va, self.fva))

                except Exception as e:
                    self.logAnomaly(emu, self.fva, "0x%x: (%r) ERROR: %s" % (op.va, op, e))
                    logger.info("0x%x: (%r) ERROR: %s", op.va, op, e)

        except v_exc.BadOpBytes:
            raise

        except Exception as e:
            self.logAnomaly(emu, self.fva, "0x%x: (%r) ERROR: %s" % (op.va, op, e))
            logger.warning("0x%x: (%r)  ERROR: %s", op.va, op, e)

    def posthook(self, emu, op, starteip):
        if op.opcode == INS_BLX:
            emu.setFlag(PSR_T_bit, self.last_tmode)


argnames = {
    0: ('r0', 0),
    1: ('r1', 1),
    2: ('r2', 2),
    3: ('r3', 3),
}


def archargname(idx):
    ret = argnames.get(idx)
    if ret is None:
        name = 'arg%d' % idx
    else:
        name, idx = ret
    return name


def buildFunctionApi(vw, fva, emu, emumon):
    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    undefregs = set(emu.getUninitRegUse())

    for argnum in range(len(argnames), 0, -1):
        argname, argid = argnames[argnum-1]
        if argid in undefregs:
            argc = argnum
            break

    if callconv == 'armcall':
        if emumon.stackmax > 0:
            targc = (emumon.stackmax >> 3) + 6
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
            else:
                argc = targc

        funcargs = [('int', archargname(i)) for i in range(argc)]

    api = ('int', None, callconv, None, funcargs)
    vw.setFunctionApi(fva, api)
    return api


def analyzeFunction(vw, fva):
    emu = vw.getEmulator()
    emumon = AnalysisMonitor(vw, fva)
    emu.setEmulationMonitor(emumon)

    loc = vw.getLocation(fva)
    if loc is not None:
        lva, lsz, lt, lti = loc
        if lt == LOC_OP:
            if (lti & envi.ARCH_MASK) != envi.ARCH_ARMV7:
                emu.setFlag(PSR_T_bit, 1)
    else:
        logger.warning("NO LOCATION at FVA: 0x%x", fva)

    emu.runFunction(fva, maxhit=1)

    # Do we already have API info in meta?
    # NOTE: do *not* use getFunctionApi here, it will make one!
    api = vw.getFunctionMeta(fva, 'api')
    if api is None:
        api = buildFunctionApi(vw, fva, emu, emumon)

    rettype,retname,callconv,callname,callargs = api

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    if cc is None:
        return

    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in range(stcount):

        vw.setFunctionLocal(fva, baseoff + ( i * 4 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)

    # handle infinite loops (actually, while 1;)

    # switch-cases may have updated codeflow.  reanalyze
    viv_cb.analyzeFunction(vw, fva)
    # logger.debug("-- Arm EMU fmod: 0x%x" % fva)



# TODO: incorporate some of emucode's analysis but for function analysis... if it makes sense.


def analyzeTB(emu, op, starteip, amon):
    ######################### FIXME: ADD THIS TO getBranches(emu)
    ### DEBUGGING
    #raw_input("\n\n\nPRESS ENTER TO START TB: 0x%x" % op.va)
    logger.debug("\n\nTB at 0x%x", starteip)
    tsize = op.opers[0].tsize
    tbl = []
    basereg = op.opers[0].base_reg
    if basereg != REG_PC:
        base = emu.getRegister(basereg)
    else:
        base = op.opers[0].va

    logger.debug("\nbase: 0x%x", base)
    val0 = emu.readMemValue(base, tsize)

    if val0 > 0x100 + base:
        logger.debug("ummmm.. Houston we got a problem.  first option is a long ways beyond BASE")

    va = base
    while va < base + val0:
        nextoff = emu.readMemValue(va, tsize) * 2
        logger.debug("0x%x: -> 0x%x", va, nextoff + base)
        if nextoff == 0:
            logging.debug("Terminating TB at 0-offset")
            break

        if nextoff > 0x500:
            logging.debug("Terminating TB at LARGE - offset  (may be too restrictive): 0x%x", nextoff)
            break

        loc = emu.vw.getLocation(va)
        if loc is not None:
            logger.debug("Terminating TB at Location/Reference")
            logger.debug("%x, %d, %x, %r", loc)
            break

        tbl.append((va, nextoff))
        va += tsize

    logger.debug("%s: \n\t", op.mnem + '\n\t'.join(['0x%x (0x%x)' % (x, base + x) for v,x in tbl]))

    ###
    # for workspace emulation analysis, let's check the index register for sanity.
    idxreg = op.opers[0].offset_reg
    idx = emu.getRegister(idxreg)
    if idx > 0x40000000:
        emu.setRegister(idxreg, 0) # args handed in can be replaced with index 0

    jmptblbase = op.opers[0]._getOperBase(emu)
    jmptblval = emu.getOperAddr(op, 0)
    jmptbltgt = (emu.getOperValue(op, 0) * 2) + base
    logger.debug("0x%x: %r\njmptblbase: 0x%x\njmptblval:  0x%x\njmptbltgt:  0x%x", op.va, op, jmptblbase, jmptblval, jmptbltgt)
    #raw_input("PRESS ENTER TO CONTINUE")

    # make numbers and xrefs and names
    emu.vw.addXref(op.va, base, REF_DATA)
    emu.vw.makeName(op.va, 'br_tbl_%x' % op.va)

    case = 0
    for ova, nextoff in tbl:
        nexttgt = base + nextoff
        emu.vw.makeNumber(ova, 2)
        # check for loc first?
        if nexttgt & 1:
            nexttgt &= -2
            arch = envi.ARCH_THUMB
        else:
            arch = envi.ARCH_ARMV7

        emu.vw.makeCode(nexttgt, arch=arch)
        # check xrefs fist?
        emu.vw.addXref(op.va, nexttgt, REF_CODE)

        curname = emu.vw.getName(nexttgt)
        if curname is None:
            emu.vw.makeName(nexttgt, "case_%x_%x_%x" % (case, op.va, nexttgt))
        else:
            emu.vw.vprint("case_%x_%x_%x conflicts with existing name: %r" % (case, op.va, nexttgt, curname))
 
        case += 1

    return base, tbl

def analyzeADDPC(emu, op, starteip, emumon):
    count = None

    reg = op.opers[-1].reg
    cb = emu.vw.getCodeBlock(op.va)
    if cb is None:
        return None, None

    cbva, cbsz, cbfva = cb
    off = 0
    while off < cbsz:
        top = emu.vw.parseOpcode(cbva+off)
        if top.opcode == INS_CMP:
            # make sure this is a comparison for this register. 
            # the comparison should be the size of the switch-case
            for opidx in range(len(top.opers)):
                oper = top.opers[opidx]
                if isinstance(oper, e_arm.ArmRegOper):
                    if oper.reg != reg:
                        continue

                    #logger.debug("cmp op: ", top)
                    cntoidx = (1,0)[opidx]
                    cntoper = top.opers[cntoidx]
                    #logger.debug("cntoper: %d, %r  %r" % (cntoidx, cntoper, vars(cntoper)))
                    count = cntoper.getOperValue(top, emu)
                    #logger.debug("count = ", count)

        off += len(top)

    if not count or count is None or count > 10000:
        return None, None

    #logger.debug("Making ADDPC SwitchCase (count=%d):" % count)
    # wire up the switch-cases, name each one, etc...
    tbl = []
    for x in range(count):
        base = op.opers[-2].getOperValue(op, emu)
        base_reg = op.opers[-1].reg
        emu.setRegister(base_reg, x)
        idx = op.opers[-1].getOperValue(op, emu)
        nexttgt = base + idx
        #logger.debug("x=%x, base=%x, idx=%x (%x)  %r %r  %d" % (x,base,idx, nexttgt, op, op.opers, emu.getRegister(op.opers[-1].reg)))
        tbl.append((base+idx, x))
        emu.vw.makeCode(nexttgt)
        emu.vw.addXref(starteip, nexttgt, REF_CODE)

        curname = emu.vw.getName(nexttgt)
        if curname is None:
            emu.vw.makeName(nexttgt, "case_%x_%x_%x" % (x, starteip, nexttgt))
        else:
            emu.vw.vprint("case_%x_%x_%x conflicts with existing name: %r" % (x, starteip, nexttgt, curname))
 

    return base, tbl


def analyzeSUBPC(emu, op, starteip, emumon):
    count = None

    cb = emu.vw.getCodeBlock(op.va)
    if cb is None:
        return None, None

    off = 0
    reg = op.opers[1].reg
    cbva, cbsz, cbfva = cb
    while off < cbsz:
        top = emu.vw.parseOpcode(cbva+off)
        if top.opcode == INS_CMP:
            # make sure this is a comparison for this register. 
            # the comparison should be the size of the switch-case
            for opidx in range(len(top.opers)):
                oper = top.opers[opidx]
                if isinstance(oper, e_arm.ArmRegOper):
                    if oper.reg != reg:
                        continue

                    #logger.debug("cmp op: ", top)
                    cntoidx = (1,0)[opidx]
                    cntoper = top.opers[cntoidx]
                    #logger.debug("cntoper: %d, %r  %r" % (cntoidx, cntoper, vars(cntoper)))
                    count = cntoper.getOperValue(top, emu)
                    #logger.debug("count = ", count)

        off += len(top)

    if not count or count is None or count > 10000:
        return None, None

    #logger.debug("Making SUBPC SwitchCase (count=%d):" % count)
    # wire up the switch-cases, name each one, etc...
    tbl = []

    base = op.opers[-2].getOperValue(op, emu)
    base_reg = op.opers[1].reg

    for x in range(count):
        emu.setRegister(base_reg, x)
        idx = op.opers[-1].getOperValue(op, emu)
        nexttgt = base - idx
        #logger.debug("x=%x, base=%x, idx=%x (%x)  %r %r  %d" % (x,base,idx, nexttgt, op, op.opers, emu.getRegister(op.opers[-1].reg)))
        tbl.append((base+idx, x))
        emu.vw.makeCode(nexttgt)
        emu.vw.addXref(starteip, nexttgt, REF_CODE)

        curname = emu.vw.getName(nexttgt)
        if curname is None:
            emu.vw.makeName(nexttgt, "case_%x_%x_%x" % (x, starteip, nexttgt))
        else:
            emu.vw.vprint("case_%x_%x_%x conflicts with existing name: %r" % (x, starteip, nexttgt, curname))

    return base, tbl
