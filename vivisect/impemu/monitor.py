import envi
import envi.exc as e_exc
import envi.bits as e_bits

import logging

from vivisect.const import *

logger = logging.getLogger(__name__)
BRANCH_FLAGS = envi.IF_BRANCH | envi.IF_CALL


class EmulationMonitor:
    """
    Emulation monitors may be passed into functions like
    runFunction() to track and hook the emulator.
    """
    def __init__(self):
        # FIXME make this a dict and re-plumb for VaSet
        self.emuanom = []  # A list of emulation anomalies (in va,msg tuples)
        self.retvals = []  # A list of the return values seen

    def logAnomaly(self, emu, va, msg):
        self.emuanom.append((va, msg))

    def getAnomalies(self):
        return list(self.emuanom)

    def prehook(self, emu, op, starteip):
        """
        This monitor hook gets called back prior to the execution of
        each instruction in the emulator.
        """
        pass

    def posthook(self, emu, op, endeip):
        """
        This monitor hook gets called back following the execution of
        each instruction in the emulator. During this callback, the
        emulator's curpath variable remains on the previous instruction.
        """
        pass

    def apicall(self, emu, op, pc, api, argv):
        '''
        This monitor hook gets called when the workspace emulator has
        encountered a call to another subroutine.  The API definition
        ( see vivisect/impapi ) as well as the parsed arguments are
        provided.

        Return a value other than None to to set the return value for
        the called API.
        '''
        pass

class AnalysisMonitor(EmulationMonitor):
    '''
    A shared class for the various arch emulation implementations
    which contains utility functions for some standard enumeration.
    '''
    def __init__(self, vw, fva):
        EmulationMonitor.__init__(self)
        self.vw = vw
        self.fva = fva
        self.onceop = {}
        self.stackmax = 0
        self.stackargs = {}
        self.operrefs = []
        self.callcomments = []
        self._dynamic_branch_handlers = []

    def addAnalysisResults(self, vw, emu):
        '''
        Do any post-run annotation that the base analysis emulator knows
        how to do...
        '''
        # Add emulation anomalies
        for row in self.getAnomalies():
            va, msg = row
            vw.setVaSetRow("Emulation Anomalies", row)
            vw.setComment(va, 'Emu Anomaly: %s' % (msg,), check=True)

        # Go through the evaluated dereference operands and add operand refs
        deltadone = {}
        for va, idx, val, tsize, spdelta, discrete in self.operrefs:
            if spdelta:
                vw.addFref(self.fva, va, idx, spdelta)

                if deltadone.get(spdelta):
                    continue

                deltadone[spdelta] = True
                if spdelta <= 0:  # add function locals
                    vw.setFunctionLocal(self.fva, spdelta, LSYM_NAME, ('int','local%d' % abs(spdelta)))

                continue

            # Only infer things about the workspace based on discrete operands
            if vw.isValidPointer(val) and discrete:
                vw.addXref(va, val, REF_DATA)
                if vw.getLocation(val) is not None:
                    continue

                vw.guessDataPointer(val, tsize)

        for va, callname, argv in self.callcomments:
            reprargs = [emu.reprVivValue(val) for val in argv]
            self.vw.setComment(va, '%s(%s)' % (callname, ','.join(reprargs)))
            cva = self.vw.vaByName(callname)
            if cva:
                self.vw.addXref(va, cva, REF_CODE, envi.BR_PROC)

    def addDynamicBranchHandler(self, cb):
        '''
        Add a callback handler for dynamic branches the code-flow resolver
        doesn't know what to do with
        '''
        if cb in self._dynamic_branch_handlers:
            raise Exception("Already have this handler (%s) for dynamic branches" % repr(cb))

        self._dynamic_branch_handlers.append(cb)

    def logAnomaly(self, emu, eip, msg):
        self.vw.vprint("EmuAnom: 0x%.8x (f:0x%.8x) %s" % (eip, self.fva, msg))
        return EmulationMonitor.logAnomaly(self, self, eip, msg)

    def prehook(self, emu, op, starteip):

        if not self.onceop.get(starteip):
            self.onceop[starteip] = True
            for i, o in enumerate(op.opers):
                if o.isDeref():
                    discrete = o.isDiscrete()
                    operva = o.getOperAddr(op, emu)
                    # keep track of the max here, but save it for later too...
                    stackoff = emu.getStackOffset(operva)
                    if stackoff and stackoff >= 0:
                        self.stackmax = max(self.stackmax, stackoff)
                        self.stackargs[stackoff] = True

                    self.operrefs.append((starteip, i, operva, o.tsize, stackoff, discrete))

        if op.iflags & BRANCH_FLAGS:
            oper = op.opers[0]
            if oper.isDeref() or oper.isReg():
                for cb in self._dynamic_branch_handlers:
                    try:
                        cb(self, emu, op, starteip)
                    except Exception as e:
                        logger.exception('error with dyn branch handler (%s) (%s)', cb, e)

    def apicall(self, emu, op, pc, api, argv):
        rettype, retname, convname, callname, callargs = api
        if self.vw.getComment(op.va) is None:
            if callname is None:
                callname = self.vw.getName(pc)

            self.callcomments.append((op.va, callname, argv))

        # Record uninitialized register use
        for i, arg in enumerate(argv):

            # Check for taints first because it's faster...
            taint = emu.getVivTaint(arg)
            if taint:
                tva, ttype, tinfo = taint
                if ttype == 'uninitreg':
                    emu.logUninitRegUse(tinfo)
                continue

            # Lets see if the API def has type info for us...
            if self.vw.isValidPointer(arg):
                argtype, argname = callargs[i]
                self.vw.setComment(arg, argtype, check=True)
                if not self.vw.isLocation(arg):
                    if argname == 'funcptr':
                        logger.debug('discovered new function: 0x%x', arg)
                        self.vw.makeFunction(arg)

                    # FIXME make an API for this? ( the name parsing )
                    # Normalize and guess about the structure...
                    typeguess = argtype.strip().strip('*').split()
                    if typeguess[0] == 'struct' and len(typeguess) >= 2:
                        vs = self.vw.getStructure(arg, typeguess[1])
                        if vs is not None:
                            self.vw.makeStructure(arg, typeguess[1], vs=vs)

                continue

        # From here down, we are only checking for instances where the
        # emulator detected a call, and managed to resolve some code flow
        # that we failed to recognize statically...
        if pc == self.fva:
            self.vw.setFunctionMeta(self.fva, 'Recursive', True)
            return

        if self.vw.isFunction(pc):
            return

        # Ditch "call 0" constructs...
        if pc == op.va + len(op):
            return

        if not self.vw.isExecutable(pc):
            return

        # WOOT - we have found a runtime resolved function!
        self.vw.vprint('0x%.8x: Emulation Found 0x%.8x (from func: 0x%.8x) via %s' % (op.va, pc, self.fva, repr(op)))
        self.vw.makeFunction(pc, arch=op.iflags & envi.ARCH_MASK)
        self.vw.addXref(op.va, pc, REF_CODE, envi.BR_PROC)
