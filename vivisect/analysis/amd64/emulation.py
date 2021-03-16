import vivisect.exc as v_exc
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.amd64 as e_amd64

from vivisect.const import *

import vivisect.analysis.generic.switchcase as vag_switch

regops = set(['cmp', 'sub'])

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.addDynamicBranchHandler(vag_switch.analyzeJmp)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()

    def prehook(self, emu, op, starteip):

        if op in self.badops:
            raise v_exc.BadOpBytes(op.va)

        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        if op.iflags & envi.IF_RET:
            if len(op.opers):
                self.retbytes = op.opers[0].imm

##### FIXME: this should be all done through the calling convention
sysvamd64argnames = {
    0: ('rdi', e_amd64.REG_RDI),
    1: ('rsi', e_amd64.REG_RSI),
    2: ('rdx', e_amd64.REG_RDX),
    3: ('rcx', e_amd64.REG_RCX),
    4: ('r8',  e_amd64.REG_R8),
    5: ('r9',  e_amd64.REG_R9),
}


msx64argnames = {
    0: ('rcx', e_amd64.REG_RCX),
    1: ('rdx', e_amd64.REG_RDX),
    2: ('r8',  e_amd64.REG_R8),
    3: ('r9',  e_amd64.REG_R9),
}


arch_bindings = {
    'msx64call': msx64argnames,
    'sysvamd64call': sysvamd64argnames,
    None: [],
}


def getName(names, idx):
    ret = names.get(idx)
    if ret is None:
        name = 'arg%d' % idx
    else:
        name, idx = ret
    return name


def buildFunctionApi(vw, fva, emu, emumon):
    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    argnames = arch_bindings.get(callconv)
    undefregs = set(emu.getUninitRegUse())

    for argnum in range(len(argnames), 0, -1):
        argname, argid = argnames[argnum-1]
        if argid in undefregs:
            argc = argnum
            break

    if callconv == 'msx64call':
        # For msx64call there's the shadow space..
        if emumon.stackmax >= 40:
            targc = (emumon.stackmax >> 3) - 1
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
            else:
                argc = targc

        # Add the shadow space "locals"
        vw.setFunctionLocal(fva, 8,  LSYM_NAME, ('void *', 'shadow0'))
        vw.setFunctionLocal(fva, 16, LSYM_NAME, ('void *', 'shadow1'))
        vw.setFunctionLocal(fva, 24, LSYM_NAME, ('void *', 'shadow2'))
        vw.setFunctionLocal(fva, 32, LSYM_NAME, ('void *', 'shadow3'))

    elif callconv == 'sysvamd64call':
        if emumon.stackmax > 0:
            targc = (emumon.stackmax >> 3) + 6
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
            else:
                argc = targc

    funcargs = [('int', getName(argnames, i)) for i in range(argc)]
    api = ('int', None, callconv, None, funcargs)
    vw.setFunctionApi(fva, api)
    return api


def analyzeFunction(vw, fva):

    emu = vw.getEmulator()
    emumon = AnalysisMonitor(vw, fva)

    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)

    # Do we already have API info in meta?
    # NOTE: do *not* use getFunctionApi here, it will make one!
    api = vw.getFunctionMeta(fva, 'api')
    if api is None:
        api = buildFunctionApi(vw, fva, emu, emumon)

    rettype, retname, callconv, callname, callargs = api

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in range(stcount):
        vw.setFunctionLocal(fva, baseoff + (i * 8), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)
