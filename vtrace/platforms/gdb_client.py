# This implementation is not complete. It should serve as a starting point for
# writing the glue-code between Vivisect and the GDB client stub code. 

import envi
import vtrace
import vtrace.platforms.base as v_base
import vtrace.platforms.gdbstub as gdbstub
import vtrace.platforms.gdb_reg_fmts as gdb_reg_fmts

import xml.etree.ElementTree as xmlET

class GdbStubMixin(gdbstub.GdbClientStub):
    """
    This class serves as the translation layer between Vivisect and GDB.
    """

    def __init__(self, arch_name, host, port, server):
        gdbstub.GdbClientStub.__init__(self, 
                    arch_name,
                    64, #TODO: pointer size in bits,
                    True, #TODO, endianness,
                    self._getRegFmt(arch_name, server), #TODO: reg formats,
                    host,
                    port,
                    server)

    def _getRegFmt(self, arch, server):
        """
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

    def _genRegFmtFromTarget(self):
        '''
        pull target.xml (and supporting xi resources) from target and generate
        a register file from that (updates self._gdb_reg_fmt)
        '''
        outregs = []
        localTypes = {}

        # get target.xml
        target = self._getAndParseTargetXml()

        # parse target.xml
        nextridx = 0
        for elem in target:
            if elem.tag == 'architecture':
                self.gdbSetArch(elem.text)     # powerpc:vle

            elif elem.tag == 'feature':
                featurename = elem.name
                for featelem in elem:
                    # this is where the "reg", "flags", and "vector" and other things are
                    fattr = featattrib
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

        # extract target.xml data into list of tuples: (regname, bitsize, regindex)

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
        """
        rvals = self.gdbGetRegisters()
        
        ctx = self.arch.archGetRegCtx()
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
                ctx.setRegisterByName(reg_name, reg_val)
            except envi.exc.InvalidRegisterName:
                # Vtrace expects control register names to be 'ctrlN', whereas 
                # GDB expects 'crN.'
                if "cr" in reg_name:
                    reg_name = 'ctrl%s' % reg_name[2:]
                else:
                    pass

        return ctx

    def platformSetRegCtx(self, tid, ctx):
        """
        """
        updates = {}
        regs = ctx.getRegisters()
        for reg_name in regs:
            updates[reg_name] = ctx.getRegisterByName(reg_name)

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
        self.gdbStepi()

    def platformAttach(self, pid):
        """
        """
        self.gdbAttach()

    def platformDetach(self):
        """
        """
        self.gdbDetach()

    def platformContinue(self):
        """
        """
        self.gdbContinue()

class GdbStubTrace(
        vtrace.Trace,
        GdbStubMixin,
        v_base.TracerBase):

    def __init__(self, archname, host, port, server):
        """
        """
        envi.stealArchMethods(self, archname)
        vtrace.Trace.__init__(self, archname = archname)
        v_base.TracerBase.__init__(self)
        GdbStubMixin.__init__(self, archname, host, port, server)

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


