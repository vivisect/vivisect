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
import envi.common as ecmn
ecmn.initLogging(logger, logging.DEBUG)

exit_types = (b'X', b'W')


class GdbStubMixin(gdbstub.GdbClientStub):
    """
    This class serves as the translation layer between Vivisect and GDB.
    """

    def __init__(self, arch_name, host, port, server, psize=8, endian=False):
        gdbstub.GdbClientStub.__init__(self, 
                    arch_name,
                    psize * 8, #TODO: pointer size in bits,
                    endian,
                    self._getRegFmt(arch_name, server), #TODO: reg formats,
                    host,
                    port,
                    server)

        self.ctx = self.arch.archGetRegCtx()
        self._rctx_pcindex = self.ctx._rctx_pcindex
        self._rctx_spindex = self.ctx._rctx_spindex

        self._gdb_filemagic = None
        self.stepping = False
        self.breaking = False


    def _getRegFmt(self, arch, server):
        """
        This needs to be updatable after gdbAttach()
        """
        reg_fmt = None
        if server == 'qemu_gdb':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_QEMU_X86_64_REG
            elif arch == 'ppc32':
                reg_fmt = gdb_reg_fmts.QEMU_PPC64_REG
            else:
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))

        elif server == 'gdbserver':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_USER_X86_64_REG
            elif arch in ('ppc32', 'ppc64'):
                reg_fmt = gdb_reg_fmts.QEMU_PPC64_REG
            else:
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))

        else:
            raise Exception('Unknown GDB server type: %s' % server)

        return reg_fmt

    def _gdbJustAttached(self):
        '''
        '''
        try:
            logger.info("attempting to pull register metadata from GDB Server")
            self._gdb_reg_fmt = self._processTargetMeta()

        except Exception as e:
            logger.warning("Exception reading registers dynamically: %r", e)

    def _setGdbArchitecture(self, gdbarch):
        '''
        GdbStubMixin version.  Calls GdbStub's version
        '''
        self.setGdbArchitecture(gdbarch)  # powerpc:vle - style
        envi.stealArchMethods(self, self._arch)   # self._arch should be updated in the prev call
        print("ARCH: %r" % self.arch)
        self.ctx = self.arch.archGetRegCtx()
        self._rctx_pcindex = self.ctx._rctx_pcindex
        self._rctx_spindex = self.ctx._rctx_spindex

    def _processTargetMeta(self):
        '''
        pull target.xml (and supporting xi resources) from target and generate
        a register file from that (updates self._gdb_reg_fmt)
        '''
        outregs = []
        localTypes = {}

        # get target.xml
        target = self._getAndParseTargetXml()

        # parse target.xml
        # extract target.xml data into list of tuples: (regname, bitsize, regindex)
        nextridx = 0
        for elem in target:
            if elem.tag == 'architecture':
                self._setGdbArchitecture(elem.text)

            elif elem.tag == 'feature':
                featurename = elem.get('name')
                for featelem in elem:
                    # this is where the "reg", "flags", and "vector" and other things are
                    fattr = featelem.attrib
                    if featelem.tag == 'reg':
                        rname = fattr['name']
                        rsz = int(fattr['bitsize'])
                        ridx = int(fattr.get('regnum', str(nextridx)))
                        # track, but continue after any regnum is set  ORDER COUNTS!
                        nextridx = ridx + 1

                        outregs.append((rname, rsz, ridx))

                    elif featelem.tag == 'flags':
                        pass
                    elif featelem.tag == 'union':
                        pass
                    elif featelem.tag == 'vector':
                        pass

        self._gdb_reg_fmt = outregs
        return outregs

    def _getAndParseTargetXml(self):
        '''In [17]: tgtxmlqemux86                                                                                                          
        Out[17]: b'<?xml version="1.0"?><!DOCTYPE target SYSTEM "gdb-target.dtd"><target><architecture>i386:x86-64</architecture><xi:include href="i386-64bit.xml"/></target>'

        In [18]: off=0; start=tgtxmlqemux86.find(b'<xi:include', off); stop = tgtxmlqemux86.find(b'/>', start); print(tgtxmlqemux86[star
            ...: t:stop])                                                                                                               
        b'<xi:include href="i386-64bit.xml"'

        In [19]: off=0; start=tgtxmlqemux86.find(b'<xi:include', off); stop = tgtxmlqemux86.find(b'/>', start); print(tgtxmlqemux86[star
            ...: t:stop])                                                                                                               
        b'<xi:include href="i386-64bit.xml"'

        In [20]: off=0; start=tgtxmlqemux86.find(b'<xi:include', off); stop = tgtxmlqemux86.find(b'/>', start); field = tgtxmlqemux86[st
            ...: art:stop+2]                                                                                                            

        In [21]: off=0; start=tgtxmlqemux86.find(b'<xi:include', off); stop = tgtxmlqemux86.find(b'/>', start); field = tgtxmlqemux86[st
            ...: art:stop+2]; field                                                                                                     
        Out[21]: b'<xi:include href="i386-64bit.xml"/>'

        In [22]: tgtx86 = tgtxmlqemux86[:start] + tgtxmlqemux86xi + tgtxmlqemux86[stop+2:]                                              

        In [23]: ET.fromstring(tgtx86)                                                                                                  
        Traceback (most recent call last):
        ParseError: XML or text declaration not at start of entity: line 1, column 110
        In [26]: tgtx86[110:200]
        Out[26]: b'<?xml version="1.0"?>\n<!-- Copyright (C) 2010-2017 Free Software Foundation, Inc.\n\n     Co'

        In [115]: feature0 = list(tgtx)[1]

        In [126]: list(feature0)[0]
        Out[126]: <Element 'reg' at 0x7f99fabb7310>

        In [127]: tmpreg = list(feature1)[0]

        In [128]: tmpreg.attrib
        Out[128]: {'bitsize': '32', 'name': 'DEC', 'regnum': '122'}

        In [129]: feature0
        Out[129]: <Element 'feature' at 0x7f9a18e9bcc0>

        In [130]: feature0.attrib
        Out[130]: {'name': 'org.gnu.gdb.power.core'}

        In [134]: feature0.attrib['name']
        Out[134]: 'org.gnu.gdb.power.core'

        '''
        # start off with the default
        targetXml = self.gdbGetFeatureFile(b'target.xml')

        # make the XI tags actually parse correctly. and parse
        targetXml = targetXml.replace(b"<xi:include ", b"<xi ")
        target = xmlET.XML(targetXml)

        ## tack the XI's into the target XML file
        # iterate through children looking for XI's.  currently we only support XI at the top level
        # any tags that are 'xi' will be replaced in the DOM by their linked feature file
        for eidx, elem in enumerate(target):
            if elem.tag != 'xi':
                continue

            newxmlurl = elem.attrib.get('href')
            newxml = self.gdbGetFeatureFile(newxmlurl.encode())
            new = xmlET.XML(newxml)
            # swap out the XI element with the new Element
            target[eidx] = new

        return target


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

    def platformAttach(self, pid):
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
            print("platformWait() ==> %r" % pkt)
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

    def _gdbSetArch(self, arch):
        reginfo

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
    gs.platformAttach(1)
    #ctx = gs.platformGetRegCtx(1)
    #gs.platformSetRegCtx(1, ctx)
    print("Before: %d" % gs.platformReadMemory(0xb0755555550000, 4))
    gs.platformWriteMemory(0xb0755555550000, 0xdeadbeef)
    print("After: %d" % gs.platformReadMemory(0xb0755555550000, 4))
    gs.platformDetach()
    #print(ctx)


