import sys

import vivisect
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.amd64 as e_amd64
from envi.registers import RMETA_NMASK

from vivisect.const import *

regops = set(['cmp','sub'])

BRANCH_FLAGS = envi.IF_BRANCH | envi.IF_CALL
class AnalysisMonitor(viv_monitor.AnalysisMonitor):
    _cb_indirect_branch = []

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
                self.retbytes = op.opers[0].imm
        
        elif op.iflags & BRANCH_FLAGS:
            oper = op.opers[0]
            if oper.isDeref() or oper.isReg():
                # do we want to check for the current pc being invalid?
                # no, what if we magically end up in real space?
                for cb in self._cb_indirect_branch:
                    try:
                        cb(self, emu, op, starteip)
                    except:
                        sys.excepthook(*sys.exc_info())

    def registerIndirectBranchCallback(self, cb):
        self._cb_indirect_branch.append(cb)

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

def sysvamd64name(idx):
    ret = sysvamd64argnames.get(idx)
    if ret == None:
        name = 'arg%d' % idx
    else:
        name, idx = ret
    return name

def msx64name(idx):
    ret = msx64argnames.get(idx)
    if ret == None:
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
            #argc += ((emumon.stackmax - 40) / 8)
            targc = (emumon.stackmax / 8) - 1
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
                #argc = 0
            else:
                argc = targc

        # Add the shadow space "locals"
        vw.setFunctionLocal(fva, 8,  LSYM_NAME, ('void *','shadow0'))
        vw.setFunctionLocal(fva, 16, LSYM_NAME, ('void *','shadow1'))
        vw.setFunctionLocal(fva, 24, LSYM_NAME, ('void *','shadow2'))
        vw.setFunctionLocal(fva, 32, LSYM_NAME, ('void *','shadow3'))

        funcargs = [ ('int',msx64name(i)) for i in xrange(argc) ]

    elif callconv == 'sysvamd64call':
        if emumon.stackmax > 0:
            targc = (emumon.stackmax / 8) + 6
            if targc > 40:
                emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
                #argc = 0
            else:
                argc = targc

        funcargs = [ ('int',sysvamd64name(i)) for i in xrange(argc) ]

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

    # Register our stack args as function locals
    for i in xrange( argc ):
        if i < stackidx:
            continue

        vw.setFunctionLocal(fva, 4 + ( i * 8 ), LSYM_FARG, i)

    emumon.addAnalysisResults(vw, emu)

