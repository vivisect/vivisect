import sys

import vivisect
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.ppc as e_ppc

from vivisect.const import *

ppcargnames = {
    0: ('r3', e_ppc.REG_R3),
    1: ('r4', e_ppc.REG_R4),
    2: ('r5', e_ppc.REG_R5),
    3: ('r6', e_ppc.REG_R6),
    4: ('r7', e_ppc.REG_R7),
    5: ('r8', e_ppc.REG_R8),
    6: ('r9', e_ppc.REG_R9),
    7: ('r10', e_ppc.REG_R10),
}

# Goals:
# * Analyze and Annotate Calling Convention data
# * Annotate Read/Writes of ctr and registers
# * Annotate Read/Writes of SPRs (VA Set?)

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.badops = vw.arch.archGetBadOps()

    def prehook(self, emu, op, starteip):

        if op in self.badops:
            raise Exception("Hit known BADOP at 0x%.8x %s" % (starteip, repr(op) ))

        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

def ppcname(idx):
    ret = ppcargnames.get(idx)
    if ret == None:
        name = 'arg%d' % idx
    else:
        name, idx = ret
    return name

def buildFunctionApi(vw, fva, emu, emumon):
    
    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    argnames = ppcargnames
    undefregs = set(emu.getUninitRegUse())

    for argnum in range(len(argnames), 0, -1):
        argname, argid = argnames[argnum-1]
        if argid in undefregs:
            argc = argnum
            break

    if emumon.stackmax > 0:
        targc = (emumon.stackmax // 8) + 6
        if targc > 40:
            emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
            #argc = 0
        else:
            argc = targc

    funcargs = [ ('int',ppcname(i)) for i in range(argc) ]

    api = ('int',None,callconv,None,funcargs)
    vw.setFunctionApi(fva, api)
    return api

def analyzeFunction(vw, fva):

    emu = vw.getEmulator(logread=True, logwrite=True)
    emumon = AnalysisMonitor(vw, fva)

    emu.setEmulationMonitor(emumon)
    emu.runFunction(fva, maxhit=1)

    # grab all reads/writes and comment (symhint??) and drop data xref
    reads, writes = getReadsAndWrites(emu.path)

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

    # read/writes

def getReadsAndWrites(path):
    return [], []

