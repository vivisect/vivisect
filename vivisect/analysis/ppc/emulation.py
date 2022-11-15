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
    ('arg1', e_ppc.REG_R3),
    ('arg2', e_ppc.REG_R4),
    ('arg3', e_ppc.REG_R5),
    ('arg4', e_ppc.REG_R6),
    ('arg5', e_ppc.REG_R7),
    ('arg6', e_ppc.REG_R8),
    ('arg7', e_ppc.REG_R9),
    ('arg8', e_ppc.REG_R10),
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
        super().__init__(vw, fva)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()
        self.spr_reads = {}
        self.spr_writes = {}
        self.mmu_writes = []

    def prehook(self, emu, op, starteip):

        if op in self.badops:
            raise viv_exc.BadOpBytes(op.va)

        super().prehook(emu, op, starteip)

    def posthook(self, emu, op, starteip):
        super().posthook(emu, op, starteip)

        # Look for SPR reads and writes, except for LR (and CTR?)
        if op.mnem == 'mfspr' and len(op.opers) >= 2 and op.opers[1].reg != e_ppc.REG_LR:
            sprname = op.opers[1].repr(op)
            if sprname not in self.spr_reads:
                self.spr_reads[sprname] = []
            self.spr_reads[sprname].append(op.va)

        elif op.mnem == 'mtspr' and len(op.opers) >= 1 and op.opers[0].reg != e_ppc.REG_LR:
            sprname = op.opers[0].repr(op)
            value = emu.getOperValue(op, 1)
            if sprname not in self.spr_writes:
                self.spr_writes[sprname] = []
            self.spr_writes[sprname].append((op.va, value))

        elif op.mnem == 'tlbwe':
            # Read the MAS0-3 SPR values right now and those are the values that
            # will be written to the MMU
            mas0 = emu.getRegister(e_ppc.REG_MAS0)
            mas1 = emu.getRegister(e_ppc.REG_MAS1)
            mas2 = emu.getRegister(e_ppc.REG_MAS2)
            mas3 = emu.getRegister(e_ppc.REG_MAS3)
            self.mmu_writes.append((op.va, mas0, mas1, mas2, mas3))

    def addAnalysisResults(self, vw, emu):
        super().addAnalysisResults(vw, emu)

        # Add custom PPC VA Sets if any SPR reads/writes or TLB writes happened,
        # sort the entries to make it faster to find specific instruction in
        # future analysis modules.
        try:
            vaset = vw.getVaSet("ppc_spr_reads")
        except viv_exc.InvalidVaSet:
            vw.addVaSet("ppc_spr_reads", (("funcva", viv_const.VASET_ADDRESS), ("reads", viv_const.VASET_COMPLEX)))

        try:
            vaset = vw.getVaSet("ppc_spr_writes")
        except viv_exc.InvalidVaSet:
            vw.addVaSet("ppc_spr_writes", (("funcva", viv_const.VASET_ADDRESS), ("writes", viv_const.VASET_COMPLEX)))

        if self.spr_reads and vw.getVaSet('ppc_spr_reads'):
            vw.setVaSetRow('ppc_spr_reads', (self.fva, dict((k, sorted(v)) for k, v in self.spr_reads.items())))
        if self.spr_writes and vw.getVaSet('ppc_spr_writes'):
            vw.setVaSetRow('ppc_spr_writes', (self.fva, dict((k, sorted(v)) for k, v in self.spr_writes.items())))

        # If there was an IVPR write, get any IVORx SPRs written in this
        # function and log these as possible exception handlers, if the target
        # addresses register as a valid function make an XREF from the
        #   mtspr IVOR?, r?
        # instruction to the exception handler
        #
        # We aren't checking code paths here so it's a little stupid, but it's
        # less trouble this way because it doesn't cause weird code path
        # deviations.
        for _, ivpr_value in self.spr_writes.get('IVPR', []):
            base = ivpr_value & IVPR_MASK

            for ivor_name, namefmt in IVOR_MAP.items():
                for va, ivor_value in self.spr_writes.get(ivor_name, []):
                    eva = base | (ivor_value & IVORx_MASK)
                    logger.debug('Looking for possible exception handler @ 0x%x', eva)
                    if vw.isProbablyCode(eva):
                        vw.addEntryPoint(eva)
                        funcname = namefmt % eva
                        vw.makeName(eva, funcname)
                        vw.setComment(va, funcname)

    def checkAddDataXref(self, vw, va, val, discrete):
        # For PPC data XREFS are only added through load/store instructions
        # which are tracked using the logread/logwrite feature
        pass


def ppcname(idx):
    if idx >= len(ppcargnames):
        name = 'arg%d' % (len(ppcargnames) + idx)
    else:
        name = ppcargnames[idx][0]
    return name


def buildFunctionApi(vw, fva, emu, emumon):

    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    undefregs = set(emu.getUninitRegUse())

    for argnum, (_, argreg) in enumerate(ppcargnames):
        if argreg not in undefregs:
            argc = argnum
            break

    # Typical PPC stack will store the LR @ 4(<original r1>), any stack
    # parameters will be loaded from offsets higher than that.
    if emumon.stackmax > 4:
        stack_args = (emumon.stackmax-4) // emu.getPointerSize()
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
