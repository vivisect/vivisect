# This implementation is not complete. It should serve as a starting point for
# writing the glue-code between Vivisect and the GDB client stub code. 

import envi
import vtrace
import vtrace.platforms.base as v_base
import vtrace.platforms.gdbstub as gdbstub
import vtrace.platforms.gdb_reg_fmts as gdb_reg_fmts

import logging
import xml.etree.ElementTree as xmlET
from vtrace.platforms.signals import *

logger = logging.getLogger(__name__)
#import envi.common as ecmn
#ecmn.initLogging(logger, logging.DEBUG)

exit_types = (b'X', b'W')


class GdbStubMixin(gdbstub.GdbClientStub):
    """
    This class serves as the translation layer between Vivisect and GDB.
    """

    def __init__(self, arch_name, host, port, server, psize=8, endian=False):
        gdbstub.GdbClientStub.__init__(self, arch_name, psize, endian,
                                       self._getRegFmt(arch_name, server),
                                       host, port, server)

        self.ctx = envi.getArchModule(arch_name).archGetRegCtx()
        self._rctx_pcindex = self.ctx._rctx_pcindex
        self._rctx_spindex = self.ctx._rctx_spindex

        self._gdb_filemagic = None
        self.stepping = False
        self.breaking = False


    def _getRegFmt(self, arch, server):
        """
        This needs to be updatable after gdbAttach()
        """
        logger.debug("arch=%r\tserver=%r", arch, server)
        reg_fmt = None
        if server == 'qemu':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.QEMU_X86_64_REG
            elif arch == 'ppc32':
                reg_fmt = gdb_reg_fmts.QEMU_PPC64_REG
            elif arch in ('arm', 'armv7', 'arm32', 'a32'):
                reg_fmt = gdb_reg_fmts.GDBSERVER_A32_REG
            else:
                logger.warning('Debugging %s with %s not currently supported' % 
                        (arch, server))
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))

        elif server == 'gdbserver':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_USER_X86_64_REG
            elif arch in ('ppc32', 'ppc64'):
                reg_fmt = gdb_reg_fmts.QEMU_PPC64_REG
            elif arch in ('arm', 'armv7', 'arm32', 'a32'):
                reg_fmt = gdb_reg_fmts.GDBSERVER_A32_REG
            else:
                logger.warning('Debugging %s with %s not currently supported' % 
                        (arch, server))
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))

        elif server == 'serverstub':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_USER_X86_64_REG
            elif arch in ('ppc32', 'ppc64'):
                reg_fmt = gdb_reg_fmts.QEMU_PPC64_REG
            elif arch in ('arm', 'armv7', 'arm32', 'a32'):
                reg_fmt = gdb_reg_fmts.GDBSERVER_A32_REG
            else:
                logger.warning('Debugging %s with %s not currently supported' % 
                        (arch, server))
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))

        else:
            logger.warning("Unknown GDB server type: %s" % server)
            raise Exception('Unknown GDB server type: %s' % server)

        return reg_fmt

    def _gdbJustAttached(self):
        '''
        '''
        logger.info("attempting to pull register metadata from GDB Server")
        self._gdb_reg_fmt = self._processTargetMeta()

        # Because we've updated the register format using the server config, 
        # update the internal parsing formats and index maps
        self._genRegPktFmt()
        self._updateEnviGdbIdxMap()

    def setGdbArchitecture(self, gdbarch):
        envi.stealArchMethods(self, self._arch)
        print("ARCH: %r" % self.arch)
        self.ctx = self.arch.archGetRegCtx()
        self._rctx_pcindex = self.ctx._rctx_pcindex
        self._rctx_spindex = self.ctx._rctx_spindex

    def platformGetRegCtx(self, tid):
        """
        Get all registers from target
        """
        rvals = self.gdbGetRegisters()

        for reg_name in rvals.keys():
            reg_val = rvals[reg_name]
            # The list of registers known by Vtrace and the list of registers 
            # known by GDB are not the same. Until these lists are unified, 
            # we have to accept that GDB may send/request information about 
            # a register that is not know to Vtrace. This is not an issue in 
            # GdbClientStub when updating registers, since we first request 
            # register state from the client, then apply our updates to that 
            # state. Added local register caching will require a solution to 
            # this problem, however.
            try:
                self.ctx.setRegisterByName(reg_name, reg_val)
            except envi.exc.InvalidRegisterName:
                # Vtrace expects control register names to be 'ctrlN', whereas 
                # GDB expects 'crN.'
                if "cr" in reg_name:
                    reg_name = 'ctrl%s' % reg_name[2:]
                else:
                    pass

        return self.ctx

    def platformSetRegCtx(self, tid, ctx=None):
        """
        """
        if ctx:
            self.ctx = ctx
        updates = {}
        regs = self.ctx.getRegisters()
        for reg_name in regs:
            updates[reg_name] = self.ctx.getRegisterByName(reg_name)

        self.gdbSetRegisters(updates)

    def platformReadMemory(self, addr, size):
        """
        """
        return self.gdbReadMem(addr, size)

    def platformWriteMemory(self, addr, mbytes):
        """
        """
        self.gdbWriteMem(addr, mbytes)

    def platformStepi(self):
        """
        """
        self.stepping = True
        self.gdbStepi(processResp=False)

    def platformAttach(self):
        """
        """
        self.gdbAttach()
        self.attaching = True

        while True:
            pkt = self._msgExchange(b'?')
            if not len(pkt):
                raise Exception('Attach Response Error!')

            resp = int(pkt[1:3], 16) 
            if resp == 0:
                import time
                time.sleep(0.1)
                self.platformSendBreak()
                pkt = self._msgExchange(b'?')

            break

        self._msgExchange(b'?', False)

    def platformDetach(self):
        """
        """
        self.gdbDetach()

    def platformWait(self):
        """
        Wait for an event
        """
        # TODO: rework event model to have a background thread constantly processing received pkts
        while True:
            pkt = self._recvResponse()
            if pkt.startswith(b'O'):
                continue

            break
        return pkt

    def platformContinue(self):
        """
        Send "Continue" to target
        """
        sig = self.getCurrentSignal()
        self.gdbContinue(sig)

    def platformSendBreak(self):
        """
        """
        if not self.attaching:
            self.breaking = True
        res = self.gdbSendBreak()

    def platformKill(self):
        """
        Kill the target process
        """
        return self.gdbKill()

    def platformPs(self):
        """
        Process List on target (which we hard-code for compliance)
        """
        return (1, 'GdbServer Stuf')

    def platformGetThreads(self):
        """
        """
        return {tid:tid for tid in self.gdbGetThreadInfo()}

    def platformSelectThread(self, threadid):
        """
        Select the thread to interact with.  Uses "Hg" as the gdb-stub command.
        """
        res = self.gdbSelectThread(threadid)
        TracerBase.platformSelectThread(threadid)
        return res

    def platformProcessEvent(self, event):
        """
        Handle target system events, wire up to VDB events
        """
        logger.debug('EVENT ->%s<-', str(event))

        if len(event) == 0:
            self.setMeta('ExitCode', 0xffffffff)
            self.fireNotifiers(vtrace.NOTIFY_EXIT)
            self._gdb_sock.shutdown(2)
            self._gdb_sock = None
            import gc
            gc.collect()
            return

        atype = event[0:1]
        signo = int(event[1:3], 16)

        # Is this a thread-specific signal?
        if atype == b'T':
            logger.debug('Signal: %s', str(signo))

            dictbytes = event[3:]

            evdict = {}
            for kvstr in dictbytes.split(b';'):
                if not kvstr:
                    break
                key, val = kvstr.split(b':', 1)
                evdict[key.lower()] = val

            # did we get a specific thread?
            tidstr = evdict.get('thread')
            if tidstr is not None:
                tid = int(tidstr, 16)
                self.setMeta('ThreadId', tid)

            else:
                logger.warning("We should ask for the current thread here!")

        elif atype == b'S':
            pass

        elif atype in exit_types:
            # Fire an exit event and GTFO!
            self._fireExit(signo)

        else:
            logger.warning("Unhandled Gdb Server Event: %s", str(event))

        # if self.attaching and signo in trap_sigs:
        if self.attaching:
            self.attaching = False
            self._gdbJustAttached()
            self._gdbLoadLibraries()
            self._gdbCreateThreads()

        elif self.breaking and signo in trap_sigs:
            self.breaking = False
            self.fireNotifiers(vtrace.NOTIFY_BREAK)

        # Process the signal and decide what to do....
        elif signo == SIGTRAP:

            # Traps on posix systems are a little complicated
            if self.stepping:
                #FIXME: try out was single step thing for intel
                self.stepping = False
                self.fireNotifiers(vtrace.NOTIFY_STEP)

            elif self.checkBreakpoints():
                return

            else:
                self._fireSignal(signo)

        else:
            self._fireSignal(signo)

    def _gdbCreateThreads(self):
        initid = self.getMeta('ThreadId')
        for tid in self.platformGetThreads().keys():
            self.setMeta('ThreadId', tid)
            self.fireNotifiers(vtrace.NOTIFY_CREATE_THREAD)
        self.setMeta('ThreadId', initid)

    def _gdbSetRegisterInfo(self, fmt, names):
        """
        Used by the Trace implementations to tell the gdb 
        stub code hot o unpack the register buf
        """
        # for now... perhaps we'll use this later to automatically update from the target....
        pass

    def _gdbLoadLibraries(self):
        if self._gdb_filemagic:
            self._findLibraryMaps(self._gdb_filemagic, always=True)


class GdbStubTrace(
        GdbStubMixin,
        vtrace.Trace,
        v_base.TracerBase):

    def __init__(self, archname, host, port, server, psize=8, bigend=False):
        """
        """
        vtrace.Trace.__init__(self, archname = archname)
        v_base.TracerBase.__init__(self)
        GdbStubMixin.__init__(self, archname, host, port, server, psize, bigend)

if __name__ == '__main__':
    gs = GdbStubTrace('amd64', 'localhost', 1234, 'gdbserver')
    gs.platformAttach()
    #ctx = gs.platformGetRegCtx(1)
    #gs.platformSetRegCtx(1, ctx)
    print("Before: %d" % gs.platformReadMemory(0xb0755555550000, 4))
    gs.platformWriteMemory(0xb0755555550000, 0xdeadbeef)
    print("After: %d" % gs.platformReadMemory(0xb0755555550000, 4))
    gs.platformDetach()
    #print(ctx)


