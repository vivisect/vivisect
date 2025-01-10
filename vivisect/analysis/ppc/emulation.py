import sys
import bisect
import operator

import vivisect
import vivisect.exc as viv_exc
import vivisect.const as viv_const
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.ppc as e_ppc

from vivisect.const import *

import logging
logger = logging.getLogger(__name__)

ppcargnames = [
    ('arg0', e_ppc.REG_R3),
    ('arg1', e_ppc.REG_R4),
    ('arg2', e_ppc.REG_R5),
    ('arg3', e_ppc.REG_R6),
    ('arg4', e_ppc.REG_R7),
    ('arg5', e_ppc.REG_R8),
    ('arg6', e_ppc.REG_R9),
    ('arg7', e_ppc.REG_R10),
]

# Mapping of IVORx registers to exception comment strings and function name
# patterns
IVOR_MAP = {
    'IVOR0':  'CRITICAL_INPUT_HANDLER_%.8x',
    'IVOR1':  'MACHINE_CHECK_HANDLER_%.8x',
    'IVOR2':  'DATA_STORAGE_HANDLER_%.8x',
    'IVOR3':  'INSTRUCTION_STORAGE_HANDLER_%.8x',
    'IVOR4':  'EXTERNAL_INPUT_HANDLER_%.8x',
    'IVOR5':  'ALIGNMENT_HANDLER_%.8x',
    'IVOR6':  'PROGRAM_HANDLER_%.8x',
    'IVOR7':  'FP_UNAVAIL_HANDLER_%.8x',
    'IVOR8':  'SYSTEM_CALL_HANDLER_%.8x',
    'IVOR9':  'AP_UNAVAIL_HANDLER_%.8x',
    'IVOR10': 'DECREMENTER_HANDLER_%.8x',
    'IVOR11': 'TIMER_HANDLER_%.8x',
    'IVOR12': 'WATCHDOG_TIMER_HANDLER_%.8x',
    'IVOR13': 'DTLB_ERROR_HANDLER_%.8x',
    'IVOR14': 'ITLB_ERROR_HANDLER_%.8x',
    'IVOR15': 'DEBUG_HANDLER_%.8x',
    'IVOR32': 'SPE_APU_UNAVAIL_HANDLER_%.8x',
    'IVOR33': 'EFP_DATA_HANDLER_%.8x',
    'IVOR34': 'EFP_ROUND_HANDLER_%.8x',
    'IVOR35': 'PERFORMANCE_MONITOR_HANDLER_%.8x',
    'IVOR36': 'DOORBELL_HANDLER_%.8x',
    'IVOR37': 'DOORBELL_CRITICAL_HANDLER_%.8x',
    'IVOR38': 'GUEST_DOORBELL_HANDLER_%.8x',
    'IVOR39': 'GUEST_DOORBELL_CRITICAL_HANDLER_%.8x',
    'IVOR40': 'HYPERCALL_HANDLER_%.8x',
    'IVOR41': 'HYPERVISOR_PRIV_HANDLER_%.8x',
    'IVOR42': 'LRAT_ERROR_HANDLER_%.8x',
}

IVPR_MASK  = 0xFFFF0000
IVORx_MASK = 0x0000FFF0


# Goals:
# * Analyze and Annotate Calling Convention data
# * Annotate Read/Writes of ctr and registers

class PpcAnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()
        self.spr_reads = []
        self.spr_writes = []
        self.tlb_writes = []

    def prehook(self, emu, op, starteip):
        if op in self.badops:
            raise viv_exc.BadOpBytes(op.va)
        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

    def posthook(self, emu, op, starteip):
        viv_monitor.AnalysisMonitor.posthook(self, emu, op, starteip)

        # Look for SPR reads and writes, except for LR (and CTR?)
        if op.mnem == 'mfspr' and op.opers[1].reg != e_ppc.REG_LR:
            sprname = op.opers[1].repr(op)
            value = emu.getOperValue(op, 1)
            self.spr_reads.append((op.va, sprname, value))

        elif op.mnem == 'mtspr' and op.opers[0].reg != e_ppc.REG_LR:
            sprname = op.opers[0].repr(op)
            value = emu.getOperValue(op, 0)
            self.spr_writes.append((op.va, sprname, value))

        elif op.mnem == 'tlbwe':
            # Read the MAS0-3 SPR values right now and those are the values that
            # will be written to the MMU
            mas0 = emu.getRegister(e_ppc.REG_MAS0)
            mas1 = emu.getRegister(e_ppc.REG_MAS1)
            mas2 = emu.getRegister(e_ppc.REG_MAS2)
            mas3 = emu.getRegister(e_ppc.REG_MAS3)
            self.tlb_writes.append((op.va, mas0, mas1, mas2, mas3))

    def addAnalysisResults(self, vw, emu):
        viv_monitor.AnalysisMonitor.addAnalysisResults(self, vw, emu)

        for row in self.spr_reads:
            vw.setVaSetRow('PpcSprReads', row)
        for row in self.spr_writes:
            vw.setVaSetRow('PpcSprWrites', row)
        for row in self.tlb_writes:
            vw.setVaSetRow('PpcTlbWrites', row)

        # If there was an IVPR write, get any IVORx SPRs written in this
        # function and log these as possible exception handlers, if the target
        # addresses register as a valid function make an XREF from the
        #   mtspr IVOR?, r?
        # instruction to the exception handler
        #
        # We aren't checking code paths here so it's a little stupid, but it's
        # less trouble this way because it doesn't cause weird code path
        # deviations.
        for _, reg, ivpr_value in self.spr_writes:
            if reg == 'IVPR':
                base = ivpr_value & IVPR_MASK

                for ivor_name, namefmt in IVOR_MAP.items():
                    for va, ivor_reg, ivor_value in self.spr_writes:
                        if ivor_reg == ivor_name:
                            eva = base | (ivor_value & IVORx_MASK)
                            logger.debug('Looking for possible exception handler @ 0x%x', eva)
                            if vw.isProbablyCode(eva):
                                vw.addEntryPoint(eva)
                                funcname = namefmt % eva
                                vw.makeName(eva, funcname)
                                vw.setComment(va, funcname)

    def checkAddDataXref(self, vw, va, val, discrete, tsize):
        # For PPC data XREFS are only added through load/store instructions
        # which are tracked using the logread/logwrite feature
        pass


def ppcname(idx):
    if idx >= len(ppcargnames):
        name = 'arg%d' % idx
    else:
        name = ppcargnames[idx][0]
    return name


def buildFunctionApi(vw, fva, emu, emumon):

    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    undefregs = set(emu.getUninitRegUse())

    for argnum, (_, argreg) in reversed(list(enumerate(ppcargnames))):
        if argreg not in undefregs:
            argc = argnum
            break

    # Standard PPC calling convention will store the LR @ 4(<original r1>), any stack
    # parameters will be loaded from offsets higher than that.  Note: Previous function/stack frame
    # stores the *previous* stack pointer at *our* 0(r1).  Strange, but true.
    if emumon.stackmax > emu.getPointerSize():
        stack_args = (emumon.stackmax - emu.getPointerSize()) // emu.getPointerSize()
        if stack_args > 40:
            emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
        else:
            argc += stack_args

    funcargs = [ ('int',ppcname(i)) for i in range(argc) ]

    api = ('int',None,callconv,None,funcargs)
    vw.setFunctionApi(fva, api)
    return api


def analyzeFunction(vw, fva):
    emu = vw.getEmulator(logread=True, logwrite=True)
    emumon = PpcAnalysisMonitor(vw, fva)

    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)

    # grab all reads/writes and comment (symhint??) and drop data xref for every
    # read or write that is not a taint or stack read/write
    for pc, va, size in emu.getPathProp('readlog'):
        if emu.getVivTaint(va) is None and emu.getStackOffset(va) is None:
            vw.addXref(pc, va, REF_DATA)

    for pc, va, data in emu.getPathProp('writelog'):
        if emu.getVivTaint(va) is None and emu.getStackOffset(va) is None:
            vw.addXref(pc, va, REF_DATA)

    # Do we already have API info in meta?
    # NOTE: do *not* use getFunctionApi here, it will make one!
    api = vw.getFunctionMeta(fva, 'api')
    if api == None:
        api = buildFunctionApi(vw, fva, emu, emumon)

    rettype,retname,callconv,callname,callargs = api

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in range(stcount):
        vw.setFunctionLocal(fva, baseoff + ( i * 8 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)
