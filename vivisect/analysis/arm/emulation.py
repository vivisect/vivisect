import sys

import vivisect
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor
import vivisect.analysis.generic.codeblocks as viv_cb

import envi
import envi.archs.arm as e_arm

from envi.archs.arm.regs import *
from envi.registers import RMETA_NMASK
from envi.archs.arm.const import *

from vivisect.const import *

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva, verbose=True):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.verbose = verbose
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
            #if self.verbose: print "tmode: %x    emu:  0x%x   flags: 0x%x \t %r" % (tmode, starteip, op.iflags, op)
            #if op == self.badop:
            if op in self.badops:
                raise Exception("Hit known BADOP at 0x%.8x %s" % (starteip, repr(op) ))

            viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

            loctup = emu.vw.getLocation(starteip)
            if loctup == None:
                # do we want to hand this off to makeCode?
                emu.vw.addLocation(starteip, len(op), vivisect.LOC_OP, op.iflags)

            elif loctup[0] != starteip:
                if self.verbose: print "ARG! emulation found opcode in a location at the wrong address (0x%x):  0x%x: %s" % (loctup[0], op.va, op)

            if op.iflags & envi.IF_RET:
                self.returns = True
                if len(op.opers):
                    if hasattr(op.opers, 'imm'):
                        self.retbytes = op.opers[0].imm

            # ARM gives us nice switchcase handling instructions
            ##### FIXME: wrap TB-handling into getBranches(emu) which is called by checkBranches during emulation
            if op.opcode in (INS_TBH, INS_TBB):
                if emu.vw.getVaSetRow('SwitchCases', op.va) == None:
                    base, tbl = analyzeTB(emu, op, starteip, self)
                    count = len(tbl)
                    self.switchcases += 1
                    emu.vw.setVaSetRow('SwitchCases', (op.va, op.va, count) )

            if op.opcode == INS_MOV:
                if len(op.opers) >= 2:
                    oper0 = op.opers[0]
                    oper1 = op.opers[1]

                    if isinstance(oper0, e_arm.ArmRegOper) and oper0.reg == REG_LR:
                        if isinstance(oper1, e_arm.ArmRegOper) and oper1.reg == REG_PC:
                            self.last_lr_pc = starteip

            if op.opcode == INS_BX:
                if starteip - self.last_lr_pc <= 4:
                    # this is a call.  the compiler updated lr
                    if self.verbose: print "CALL by mov lr, pc; bx <foo> at 0x%x" % starteip
                    ### DO SOMETHING??  identify new function like emucode.

            if op.iflags & envi.IF_BRANCH:
                try:
                    tgt = op.getOperValue(0, emu)

                    #if self.verbose: print "BRANCH: ", hex(tgt), hex(op.va), hex(op.va)

                    if tgt == op.va:
                        if self.verbose: print "+++++++++++++++ infinite loop +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                        if op.va not in self.infloops:
                            self.infloops.append(op.va)

                except Exception, e:
                    # FIXME: make raise Exception?
                    print "0x%x: ERROR: %s" % (op.va, e)

        except Exception, e:
            # FIXME: make raise Exception?
            print "0x%x: (%r)  ERROR: %s" % (op.va, op, e)
            sys.excepthook(*sys.exc_info())


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
    if ret == None:
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
            targc = (emumon.stackmax / 8) + 6
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
            else:
                argc = targc

        funcargs = [ ('int',archargname(i)) for i in xrange(argc) ]

    api = ('int',None,callconv,None,funcargs)
    vw.setFunctionApi(fva, api)
    return api

def analyzeFunction(vw, fva):
    #print( "= 0x%x viv.analysis.arm.emulation... =" % (fva))

    emu = vw.getEmulator()
    emumon = AnalysisMonitor(vw, fva)
    emu.setEmulationMonitor(emumon)

    loc = vw.getLocation(fva)
    if loc != None:
        lva, lsz, lt, lti = loc
        if lt == LOC_OP:
            if (lti & envi.ARCH_MASK) != envi.ARCH_ARMV7:
                emu.setFlag(PSR_T_bit, 1)
    else:
        print "NO LOCATION at FVA: 0x%x" % fva

    emu.runFunction(fva, maxhit=1)

    # Do we already have API info in meta?
    # NOTE: do *not* use getFunctionApi here, it will make one!
    api = vw.getFunctionMeta(fva, 'api')
    if api == None:
        api = buildFunctionApi(vw, fva, emu, emumon)

    rettype,retname,callconv,callname,callargs = api

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    if cc == None:
        return

    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in xrange( stcount ):

        vw.setFunctionLocal(fva, baseoff + ( i * 4 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)

    # handle infinite loops (actually, while 1;)

    # switch-cases may have updated codeflow.  reanalyze
    viv_cb.analyzeFunction(vw, fva)



# TODO: incorporate some of emucode's analysis but for function analysis... if it makes sense.


def analyzeTB(emu, op, starteip, amon):
    ######################### FIXME: ADD THIS TO getBranches(emu)
    ### DEBUGGING
    #raw_input("\n\n\nPRESS ENTER TO START TB: 0x%x" % op.va)
    print "\n\nTB at 0x%x" % starteip
    tsize = op.opers[0].tsize
    tbl = []
    basereg = op.opers[0].base_reg
    if basereg != REG_PC:
        base = emu.getRegister(basereg)
    else:
        base = op.opers[0].va

    print("\nbase: 0x%x" % base)
    val0 = emu.readMemValue(base, tsize)

    if val0 > 0x100 + base:
        print "ummmm.. Houston we got a problem.  first option is a long ways beyond BASE"

    va = base
    while va < base + val0:
        nextoff = emu.readMemValue(va, tsize) * 2
        print "0x%x: -> 0x%x" % (va, nextoff + base)
        if nextoff == 0:
            print "Terminating TB at 0-offset"
            break

        if nextoff > 0x500:
            print "Terminating TB at LARGE - offset  (may be too restrictive): 0x%x" % nextoff
            break

        loc = emu.vw.getLocation(va)
        if loc != None:
            print "Terminating TB at Location/Reference"
            print "%x, %d, %x, %r" % loc
            break

        tbl.append((va, nextoff))
        va += tsize
        #sys.stderr.write('.')

    print "%s: \n\t"%op.mnem + '\n\t'.join(['0x%x (0x%x)' % (x, base + x) for v,x in tbl])

    ###
    # for workspace emulation analysis, let's check the index register for sanity.
    idxreg = op.opers[0].offset_reg
    idx = emu.getRegister(idxreg)
    if idx > 0x40000000:
        emu.setRegister(idxreg, 0) # args handed in can be replaced with index 0

    jmptblbase = op.opers[0]._getOperBase(emu)
    jmptblval = emu.getOperAddr(op, 0)
    jmptbltgt = (emu.getOperValue(op, 0) * 2) + base
    print "0x%x: %r\njmptblbase: 0x%x\njmptblval:  0x%x\njmptbltgt:  0x%x" % (op.va, op, jmptblbase, jmptblval, jmptbltgt)
    #raw_input("PRESS ENTER TO CONTINUE")

    # make numbers and xrefs and names
    emu.vw.addXref(op.va, base, REF_DATA)

    case = 0
    for ova, nextoff in tbl:
        nexttgt = base + nextoff
        emu.vw.makeNumber(ova, 2)
        # check for loc first?
        emu.vw.makeCode(nexttgt)
        # check xrefs fist?
        emu.vw.addXref(op.va, nexttgt, REF_CODE)
        
        curname = emu.vw.getName(nexttgt)
        if curname == None:
            emu.vw.makeName(nexttgt, "case_%x_%x_%x" % (case, op.va, nexttgt))
        else:
            emu.vw.vprint("case_%x_%x_%x conflicts with existing name: %r" % (case, op.va, nexttgt, curname))
 
        case += 1

    return base, tbl

