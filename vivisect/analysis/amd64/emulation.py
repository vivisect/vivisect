import sys

import vivisect
import vivisect.impemu as viv_imp
import vivisect.impemu.monitor as viv_monitor

import envi
import envi.archs.amd64 as e_amd64
from envi.registers import RMETA_NMASK

from vivisect.const import *

import vivisect.analysis.generic.switchcase as vag_switch

class AnalysisMonitor(viv_monitor.AnalysisMonitor):

    def __init__(self, vw, fva):    # most of this can be abstracted out to the the architecture modules
        viv_monitor.AnalysisMonitor.__init__(self, vw, fva)
        self.addDynamicBranchHandler(vag_switch.analyzeJmp)
        self.retbytes = None
        self.badop = vw.arch.archParseOpcode("\x00\x00\x00\x00\x00")    # badop can be a string value attached to the archmod

    def prehook(self, emu, op, starteip):

        if op == self.badop:
            raise Exception("Hit known BADOP at 0x%.8x %s" % (starteip, repr(op) ))

        viv_monitor.AnalysisMonitor.prehook(self, emu, op, starteip)

        if op.iflags & envi.IF_RET:         # this should be a call to isRet, because not all architectures are so simple
            if len(op.opers):
                self.retbytes = op.opers[0].imm

def buildFunctionApi(vw, fva, emu, emumon):     # function is architecture specific, not ok to be wrapped into cconv class although some of it can be more cconv-specific
    '''
    Builds the function API:
    * argc - number of arguments
    * cc   - determines calling convention
    '''
    argc = 0
    funcargs = []
    callconv = vw.getMeta('DefaultCall')
    cc = emu.getCallingConvention(callconv)
    argnames = cc.getCallRegArgInfo(emu)
    undefregs = set(emu.getUninitRegUse())

    # determine number of register args
    for argnum in range(len(argnames), 0, -1):
        #argname, argid = argnames[argnum-1]
        argtype, argname, argid = argnames[argnum-1]
        if argid in undefregs:
            argc = argnum
            break

    # calculate the stack argument space used
    if emumon.stackmax > cc.pad:
        # stack delta - padding (shadow space, etc)
        stackargspace = emumon.stackmax - cc.pad# - cc.align
        targc = cc.getNumRegArgs(emu, MAX_ARGS) + (stackargspace / 8)

        if targc > MAX_ARGS:
            emumon.logAnomaly(emu, fva, 'Crazy Stack Offset Touched: 0x%.8x' % emumon.stackmax)
        else:
            argc = targc

    if callconv == 'msx64call':
        # For msx64call there's the shadow space..
        # Add the shadow space "locals"
        vw.setFunctionLocal(fva, 8,  LSYM_NAME, ('void *','shadow0'))
        vw.setFunctionLocal(fva, 16, LSYM_NAME, ('void *','shadow1'))
        vw.setFunctionLocal(fva, 24, LSYM_NAME, ('void *','shadow2'))
        vw.setFunctionLocal(fva, 32, LSYM_NAME, ('void *','shadow3'))

    elif callconv == 'sysvamd64call':
        pass

    funcargs = [ ('int',aname) for atype, aname, aindoff in cc.getCallArgInfo(emu, argc) ]

    api = ('int',None,callconv,None,funcargs)
    vw.setFunctionApi(fva, api)
    return api

def analyzeFunction(vw, fva):   # this can by mostly made arch-independent and placed in one class (AnalysisMonitor??)
    '''
    Determine function API and updates workspace with specifics
    * Calling convention
    * Argument count
    * Stack Locals
    '''
    # setup emulator and analysis module and run it
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

    # set the function locals/args - stores info for workspace-prettification, 
    #       eg. "[ebp + arg1]" instead of "[ebp + 12]"
    argc = len(callargs)
    cc = emu.getCallingConvention(callconv)
    stcount = cc.getNumStackArgs(emu, argc)
    stackidx = argc - stcount
    baseoff = cc.getStackArgOffset(emu, argc)

    # Register our stack args as function locals
    for i in xrange( stcount ):
        
        vw.setFunctionLocal(fva, baseoff + ( i * cc.align ), LSYM_FARG, i+stackidx)
        pass

    emumon.addAnalysisResults(vw, emu)

