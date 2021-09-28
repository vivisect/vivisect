# This implementation is not complete. It should serve as a starting point for
# writing the glue-code between Vivisect and the GDB client stub code. 

import envi
import vtrace
import vtrace.platforms.base as v_base
import vtrace.platforms.gdbstub as gdbstub
import vtrace.platforms.gdb_reg_fmts as gdb_reg_fmts

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
                    port)

    def _getRegFmt(self, arch, server):
        """
        """
        reg_fmt = None
        if server == 'qemu_gdb':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_QEMU_X86_64_REG
            else:
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))
        elif server == 'gdbserver':
            if arch == 'amd64':
                reg_fmt = gdb_reg_fmts.GDB_USER_X86_64_REG
            else:
                raise Exception('Debugging %s with %s not currently supported' % 
                        (arch, server))
        else:
            raise Exception('Unknown GDB server type: %s' % server)

        return reg_fmt

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


