import sys

import vivisect
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.arm as e_arm
from envi.registers import RMETA_NMASK

from vivisect.const import *

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.retbytes = None
        self.badop = vw.arch.archParseOpcode("\x00\x00\x00\x00\x00")

    def prehook(self, emu, op, starteip):

        if op == self.badop:
            raise Exception("Hit known BADOP at 0x%.8x %s" % (starteip, repr(op) ))

        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        if op.iflags & envi.IF_RET:
            if len(op.opers):
                if hasattr(op.opers, 'imm'):
                    self.retbytes = op.opers[0].imm
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

    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in xrange( stcount ):

        vw.setFunctionLocal(fva, baseoff + ( i * 4 ), LSYM_FARG, i+stackidx)

    emumon.addAnalysisResults(vw, emu)

# TODO: incorporate some of emucode's analysis but for function analysis... if it makes sense.
