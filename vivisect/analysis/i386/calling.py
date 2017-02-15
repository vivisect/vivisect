
"""
An i386 specific function analysis module that is designed to
attempt to detect the calling convention.
"""
import collections

import vivisect
import vivisect.impemu.monitor as viv_imp_monitor

from vivisect.const import *

import visgraph.pathcore as vg_path

import envi
import envi.archs.i386 as e_i386
import envi.archs.i386.opcode86 as opcode86

regcalls = {
    (e_i386.REG_ECX,):               ('thiscall',1),
    (e_i386.REG_EAX,):               ('bfastcall',1),
    (e_i386.REG_EAX,e_i386.REG_EDX): ('bfastcall',2),
    (e_i386.REG_ECX,e_i386.REG_EDX): ('msfastcall',2),
    (e_i386.REG_EAX, e_i386.REG_ECX, e_i386.REG_EDX):('bfastcall',3),
}

# Arange the same data for a name lookup

empty = collections.defaultdict(lambda x: ('int','arg%d' % x))
argnames = {
    'thiscall':     {0:('void *','ecx'),},
    'msfastcall':   {0:('int','ecx'),1:('int','edx')},
    'bfastcall':    {0:('int','eax'),1:('int','edx'),2:('int','ecx'),},
}

def argcname(callconv, idx):
    ret = argnames.get(callconv,empty).get(idx)
    if ret == None:
        ret = ('int','arg%d' % idx)
    return ret

class AnalysisMonitor(viv_imp_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_imp_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()

    def prehook(self, emu, op, starteip):
        if op in self.badops:
            raise Exception("Hit known BADOP at 0x%.8x %s" % (starteip, repr(op) ))

        viv_imp_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        # Do return related stuff before we execute the opcode
        if op.iflags & envi.IF_RET:
            if len(op.opers):
                self.retbytes = op.opers[0].imm

def buildFunctionApi(vw, fva, emu, emumon):
    # More than 40 args?  no way...
    argc = (int(emumon.stackmax) / 4)
    if argc > 40:
        emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
        argc = 0

    callconv = "cdecl" # Default to cdecl
    # see if we have stdcall return bytes
    if emumon.retbytes != None:
        callconv = "stdcall"
        argc = emumon.retbytes / 4


    stackidx = 0 # arg index of first *stack* arg

    # Log registers we used by didn't init
    undefkeys = emu.uninit_use.keys()
    undefkeys.sort()

    undeflen = len(undefkeys)
    if undeflen:
        regcall = regcalls.get( tuple(undefkeys) )
        if regcall != None:
            callconv, addargc = regcall
            argc += addargc

        vw.setFunctionMeta(fva, "UndefRegUse", undefkeys)

    if argc > 64:
        callconv = 'unkcall' 
        argc = 0
    # Add argument indexes to our argument names
    funcargs = [ argcname(callconv, i) for i in xrange(argc) ]
    api = ('int',None,callconv,None,funcargs)

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
    if api == None:
        api = buildFunctionApi(vw, fva, emu, emumon)

    rettype,retname,callconv,callname,callargs = api
    if callconv == 'unkcall':
        return

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in xrange( stcount ):

        vw.setFunctionLocal(fva, baseoff + ( i * 4 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)

