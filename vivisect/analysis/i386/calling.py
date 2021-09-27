
"""
An i386 specific function analysis module that is designed to
attempt to detect the calling convention.
"""
import collections

import vivisect.impemu.monitor as viv_imp_monitor

import vivisect.exc as v_exc
from vivisect.const import *

import vivisect.analysis.generic.switchcase as vag_switch

import envi.archs.i386 as e_i386
import envi.archs.i386.opconst as e_i386const

regcalls = {
    (e_i386.REG_ECX,):               ('thiscall', 1),
    (e_i386.REG_EAX,):               ('bfastcall', 1),
    (e_i386.REG_EAX, e_i386.REG_EDX): ('bfastcall', 2),
    (e_i386.REG_ECX, e_i386.REG_EDX): ('msfastcall', 2),
    (e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX): ('bfastcall', 3),
}

# Arrange the same data for a name lookup

empty = collections.defaultdict(lambda x: ('int','arg%d' % x))
argnames = {
    'thiscall':     {0: ('void *','ecx'),},
    'msfastcall':   {0: ('int','ecx'), 1: ('int','edx')},
    'bfastcall':    {0: ('int','eax'), 1: ('int','edx'), 2: ('int','ecx'),},
}

def argcname(callconv, idx):
    ret = argnames.get(callconv,empty).get(idx)
    if ret is None:
        ret = ('int','arg%d' % idx)
    return ret

class AnalysisMonitor(viv_imp_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_imp_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.endstack = None
        self.addDynamicBranchHandler(vag_switch.analyzeJmp)
        self.badops = vw.arch.archGetBadOps()

    def prehook(self, emu, op, starteip):
        if op in self.badops:
            raise v_exc.BadOpBytes(op.va)

        viv_imp_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        if op.opcode == e_i386const.INS_LEA:    # x86 only
            i = 1
            o = op.opers[i]
            discrete = o.isDiscrete()
            operva = o.getOperAddr(op, emu)
            # keep track of the max here, but save it for later too...
            stackoff = emu.getStackOffset(operva)
            if stackoff and stackoff >= 0:
                self.stackmax = max(self.stackmax, stackoff)
                self.stackargs[stackoff] = True

            self.operrefs.append((starteip, i, operva, o.tsize, stackoff, discrete))


        # Do return related stuff before we execute the opcode
        if op.isReturn():
            self.endstack = emu.getStackCounter()
            if len(op.opers):
                self.retbytes = op.opers[0].imm


def buildFunctionApi(vw, fva, emu, emumon, stkstart):
    # More than 40 args?  no way...
    argc = stackargs = (int(emumon.stackmax) >> 2)
    if argc > 40:
        emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
        argc = 0

    callconv = "cdecl"  # Default to cdecl
    # see if we have stdcall return bytes
    if emumon.retbytes is not None:
        callconv = "stdcall"
        argc = emumon.retbytes >> 2

    stackidx = 0  # arg index of first *stack* arg

    # Log registers we used but didn't init
    # but don't take into account ebp and esp
    emu.uninit_use.pop(e_i386.REG_ESP, None)
    emu.uninit_use.pop(e_i386.REG_EBP, None)
    undefkeys = list(emu.uninit_use.keys())
    undefkeys.sort()

    undeflen = len(undefkeys)
    if undeflen:
        regcall = regcalls.get(tuple(undefkeys))
        if regcall is not None:
            callconv, addargc = regcall
            argc += addargc

        vw.setFunctionMeta(fva, "UndefRegUse", undefkeys)

    # if we're callee cleanup, make sure we *actually* clean up our space
    # otherwise, revert us to caller cleanup
    if emumon.endstack:
        stkoff = (emumon.endstack - stkstart) >> 2
        if callconv in argnames:
            # do our stack args line up with what we cleaned up?
            if abs(stkoff) != stackargs:
                # we're probably caller cleanup then
                callconv = callconv + '_caller'

    if argc > 64:
        callconv = 'unkcall'
        argc = 0
    # Add argument indexes to our argument names
    funcargs = [ argcname(callconv, i) for i in range(argc) ]
    api = ('int',None,callconv,None,funcargs)

    vw.setFunctionApi(fva, api)
    return api

def analyzeFunction(vw, fva):

    emu = vw.getEmulator()
    emumon = AnalysisMonitor(vw, fva)

    stkstart = emu.getStackCounter()
    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)

    # Do we already have API info in meta?
    # NOTE: do *not* use getFunctionApi here, it will make one!
    api = vw.getFunctionMeta(fva, 'api')
    if api is None:
        api = buildFunctionApi(vw, fva, emu, emumon, stkstart)

    rettype,retname,callconv,callname,callargs = api
    if callconv == 'unkcall':
        return

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in range(stcount):
        vw.setFunctionLocal(fva, baseoff + ( i * 4 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)
