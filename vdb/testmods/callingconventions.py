import struct
from contextlib import contextmanager

import envi.archs.i386 as e_i386
from envi.archs.i386.regs import *
import envi.archs.amd64 as e_amd64
from envi.archs.amd64.regs import *

import vdb.testmods as v_testmods


@contextmanager
def constantStackCounter(trace):
    '''
    Helper method that can be used to check that the stack counter has not
    changed after executing some block of operations.
    '''
    sp = trace.getStackCounter()
    yield
    assert(sp == trace.getStackCounter())


class i386StdCallCallingConventionTest(v_testmods.VtracePythonTest):
    modname = 'vdb.testmods.callingconventions'

    def __init__(self, argc):
        v_testmods.VtracePythonTest.__init__(self)
        self.argc = argc

    def checkMem(self, args, va):
        for index, arg in enumerate(args):
            arg_addr = va + index * self.psize
            read_arg = struct.unpack('<%s' % self.ssize, self.trace.readMemory(arg_addr, self.psize))[0]
            assert(read_arg == arg)

    def checkReturnAddress(self):
        sp = self.trace.getStackCounter()
        read_retaddr = struct.unpack('<%s' % self.ssize, self.trace.readMemory(sp, self.psize))[0]
        assert(read_retaddr == self.retaddr)

    def checkPreCallStackArgs(self, args, skipnum=0):
        sp = self.trace.getStackCounter()
        sp += self.psize * skipnum  # for easy x64 support of homing params
        self.checkMem(args, sp)

    def checkCallStackArgs(self, args, skipnum=0):
        sp = self.trace.getStackCounter()
        sp += self.psize  # skip ret addr
        sp += self.psize * skipnum  # for easy x64 support of homing params
        self.checkMem(args, sp)

    def checkRegisterArgs(self, reglist, args):
        argc_in_regs = min(len(reglist), len(self.args))
        for index in range(0, argc_in_regs):
            assert(args[index] == self.trace.getRegister(reglist[index]))

    def checkReadArgs(self, args, read_args):
        for index, read_arg in enumerate(read_args):
            assert(read_arg == args[index])

    def checkProgramCounter(self, expected_pc):
        actual_pc = self.trace.getProgramCounter()
        assert(actual_pc == expected_pc)

    def prepTest(self):
        v_testmods.VtracePythonTest.prepTest(self)

        self.psize = self.trace.getPointerSize()
        self.ssize = None
        if self.psize == 4:
            self.ssize = 'I'
        elif self.psize == 8:
            self.ssize = 'Q'
        else:
            raise Exception('unknown pointer size %d' % self.psize)

        self.cc = e_i386.StdCall()

        self.retaddr = 0xdeadbeef
        self.retval = 0x61616161

        # dynamically create the function arguments based on number
        # specified to constructor.
        start = 0x41
        self.args = []
        for i in range(0, self.argc):
            val = start+i
            bytez = val << 24 | val << 16 | val << 8 | val
            self.args.append(bytez)

    def runTest(self):
        self.testSetPreCallArgs()
        # getprecallargs depend on setPreCallArgs having been successful.
        self.testGetPreCallArgs()
        self.testSetCallArgs()
        # getcallargs depend on setCallArgs having been successful.
        self.testGetCallArgs()
        self.testSetCallArgsRet()
        self.testExecuteCall()
        # add test for setreturnvalue by itself.
        self.testExecCallReturn()
        self.testAllocate()

    def testSetPreCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setPreCallArgs(self.trace, self.args)

        self.checkPreCallStackArgs(self.args)

    def testGetPreCallArgs(self):
        args = self.cc.getPreCallArgs(self.trace, len(self.args))
        self.checkReadArgs(self.args, args)

    def testSetCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setCallArgs(self.trace, self.args)

        self.checkCallStackArgs(self.args)

    def testGetCallArgs(self):
        args = self.cc.getCallArgs(self.trace, len(self.args))
        self.checkReadArgs(self.args, args)

    def testSetCallArgsRet(self):
        with constantStackCounter(self.trace):
            self.cc.setCallArgsRet(self.trace, self.args, ra=self.retaddr)

        self.checkReturnAddress()
        self.checkCallStackArgs(self.args)

    def testExecuteCall(self):
        sp = self.trace.getStackCounter()

        # TODO: test with ra=None and args=None next.
        mem_addr = self.trace.allocateMemory(0x1000)
        self.cc.executeCall(self.trace, mem_addr, args=self.args, ra=self.retaddr)

        num_stackargs = self.cc.getNumStackArgs(self.trace, len(self.args))
        assert(sp - (4*num_stackargs)-4 == self.trace.getStackCounter())
        self.checkReturnAddress()
        self.checkCallStackArgs(self.args)
        self.checkProgramCounter(mem_addr)

    def testExecCallReturn(self):
        sp = self.trace.getStackCounter()
        self.cc.execCallReturn(self.trace, self.retval, len(self.args))
        assert(sp + (4*len(self.args)+4) == self.trace.getStackCounter())

        eax = self.trace.getRegister(REG_EAX)
        eip = self.trace.getRegister(REG_EIP)
        assert(eax == self.retval)
        assert(eip == self.retaddr)

    def testAllocate(self):
        sp = self.trace.getStackCounter()
        self.cc.allocateArgSpace(self.trace, len(self.args))
        assert(sp - 4*len(self.args) == self.trace.getStackCounter())

        sp = self.trace.getStackCounter()
        self.cc.allocateCallSpace(self.trace, len(self.args))
        assert(sp - 4*len(self.args)-4 == self.trace.getStackCounter())


class i386CdeclCallingConventionTest(i386StdCallCallingConventionTest):
    modname = 'vdb.testmods.callingconventions'

    def prepTest(self):
        i386StdCallCallingConventionTest.prepTest(self)
        self.cc = e_i386.Cdecl()

    def testExecCallReturn(self):
        sp = self.trace.getStackCounter()
        self.cc.execCallReturn(self.trace, self.retval, len(self.args))
        assert(sp + 4 == self.trace.getStackCounter())

        eax = self.trace.getRegister(REG_EAX)
        eip = self.trace.getRegister(REG_EIP)
        assert(eax == self.retval)
        assert(eip == self.retaddr)


class i386ThisCallCallingConventionTest(i386StdCallCallingConventionTest):

    def resetMemory(self):
        self.trace.setRegister(REG_ECX, 0xFFFFFFFF)

        sp = self.trace.getStackCounter()
        for i in range(0, len(self.args)*2):
            self.trace.writeMemory(sp+4*i, struct.pack('<I', 0xEEEEEEEE))

    def prepTest(self):
        i386StdCallCallingConventionTest.prepTest(self)
        self.cc = e_i386.ThisCall()

    def testSetPreCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setPreCallArgs(self.trace, self.args)

        if len(self.args) > 0:
            assert(self.args[0] == self.trace.getRegister(REG_ECX))

            self.checkPreCallStackArgs(self.args[1:])

    def testGetPreCallArgs(self):
        args = self.cc.getPreCallArgs(self.trace, len(self.args))
        if len(self.args) > 0:
            assert(args[0] == self.trace.getRegister(REG_ECX))
        self.checkReadArgs(self.args, args)

    def testSetCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setCallArgs(self.trace, self.args)

        if len(self.args) > 0:
            assert(self.args[0] == self.trace.getRegister(REG_ECX))

            self.checkCallStackArgs(self.args[1:])

    def testGetCallArgs(self):
        args = self.cc.getCallArgs(self.trace, len(self.args))
        if len(self.args) > 0:
            assert(args[0] == self.trace.getRegister(REG_ECX))
        self.checkReadArgs(self.args, args)

    def testSetCallArgsRet(self):
        self.resetMemory()

        with constantStackCounter(self.trace):
            self.cc.setCallArgsRet(self.trace, self.args, ra=self.retaddr)

        if len(self.args) > 0:
            assert(self.args[0] == self.trace.getRegister(REG_ECX))
            self.checkCallStackArgs(self.args[1:])

        self.checkReturnAddress()

    def testExecuteCall(self):
        # TODO: test with ra=None and args=None next.
        mem_addr = self.trace.allocateMemory(0x1000)
        self.cc.executeCall(self.trace, mem_addr, args=self.args, ra=self.retaddr)
        if len(self.args) > 0:
            assert(self.trace.getRegister(REG_ECX) == self.args[0])
            self.checkCallStackArgs(self.args[1:])

        # TODO: check amount stack increased by makes sense.
        self.checkReturnAddress()
        self.checkProgramCounter(mem_addr)

    def testExecCallReturn(self):
        self.resetMemory()
        # prereq is the return value set to known
        self.trace.writeMemory(self.trace.getStackCounter(), struct.pack('<I', self.retaddr))
        sp = self.trace.getStackCounter()
        self.cc.execCallReturn(self.trace, self.retval, len(self.args))
        if len(self.args) > 0:
            assert(sp + (4*(len(self.args)-1)+4) == self.trace.getStackCounter())
        else:
            assert(sp + 4 == self.trace.getStackCounter())

        eax = self.trace.getRegister(REG_EAX)
        eip = self.trace.getRegister(REG_EIP)
        assert(eax == self.retval)
        assert(eip == self.retaddr)

    def testAllocate(self):
        sp = self.trace.getStackCounter()
        self.cc.allocateArgSpace(self.trace, len(self.args))
        if len(self.args) > 0:
            assert(sp - 4*(len(self.args)-1) == self.trace.getStackCounter())
        else:
            assert(sp == self.trace.getStackCounter())

        sp = self.trace.getStackCounter()
        self.cc.allocateCallSpace(self.trace, len(self.args))
        if len(self.args) > 0:
            assert(sp - 4*(len(self.args)-1)-4 == self.trace.getStackCounter())
        else:
            assert(sp - 4 == self.trace.getStackCounter())

class i386MsFastCallCallingConventionTest(i386StdCallCallingConventionTest):

    def resetMemory(self):
        for i in self.reglist:
            self.trace.setRegister(i, 0xFFFFFFFF)

        sp = self.trace.getStackCounter()
        for i in range(0, len(self.args)*2):
            self.trace.writeMemory(sp+4*i, struct.pack('<I', 0xEEEEEEEE))

    def prepTest(self):
        i386StdCallCallingConventionTest.prepTest(self)
        self.cc = e_i386.MsFastCall()

        self.reglist = [REG_ECX, REG_EDX]

    def testSetPreCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setPreCallArgs(self.trace, self.args)

        if len(self.args) == 0:
            return

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkPreCallStackArgs(self.args[len(self.reglist):])

    def testGetPreCallArgs(self):
        args = self.cc.getPreCallArgs(self.trace, len(self.args))

        self.checkRegisterArgs(self.reglist, args)

        num_in_regs = len(self.reglist)
        self.checkReadArgs(self.args[num_in_regs:], args[num_in_regs:])

    def testSetCallArgs(self):
        with constantStackCounter(self.trace):
            self.cc.setCallArgs(self.trace, self.args)

        if len(self.args) == 0:
            return

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkCallStackArgs(self.args[len(self.reglist):])

    def testGetCallArgs(self):
        args = self.cc.getCallArgs(self.trace, len(self.args))

        self.checkRegisterArgs(self.reglist, args)

        num_in_regs = len(self.reglist)
        self.checkReadArgs(self.args[num_in_regs:], args[num_in_regs:])

    def testSetCallArgsRet(self):
        self.resetMemory()

        with constantStackCounter(self.trace):
            self.cc.setCallArgsRet(self.trace, self.args, ra=self.retaddr)

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkReturnAddress()
        num_in_regs = len(self.reglist)
        self.checkCallStackArgs(self.args[num_in_regs:])

    def testExecuteCall(self):
        # TODO: test with ra=None and args=None next.
        mem_addr = self.trace.allocateMemory(0x1000)
        self.cc.executeCall(self.trace, mem_addr, args=self.args, ra=self.retaddr)

        # TODO: check amount stack increased by makes sense.
        self.checkRegisterArgs(self.reglist, self.args)
        self.checkReturnAddress()
        num_in_regs = len(self.reglist)
        self.checkCallStackArgs(self.args[num_in_regs:])
        self.checkProgramCounter(mem_addr)

    def testExecCallReturn(self):
        self.resetMemory()
        # prereq is the return value set to known
        self.trace.writeMemory(self.trace.getStackCounter(), struct.pack('<%s' % self.ssize, self.retaddr))
        sp = self.trace.getStackCounter()
        self.cc.execCallReturn(self.trace, self.retval, len(self.args))

        num_in_registers = min(len(self.reglist), len(self.args))
        num_on_stack = len(self.args) - num_in_registers
        assert(num_on_stack >= 0)
        assert(sp + (self.psize*num_on_stack+self.psize) == self.trace.getStackCounter())

        eax = self.trace.getRegister(REG_EAX)
        ip = self.trace.getProgramCounter()
        assert(eax == self.retval)
        assert(ip == self.retaddr)

    def testAllocate(self):
        num_stackargs = self.cc.getNumStackArgs(self.trace, len(self.args))

        sp = self.trace.getStackCounter()
        self.cc.allocateArgSpace(self.trace, len(self.args))
        assert(sp - self.psize*num_stackargs == self.trace.getStackCounter())

        sp = self.trace.getStackCounter()
        self.cc.allocateCallSpace(self.trace, len(self.args))
        assert(sp - self.psize*num_stackargs-self.psize == self.trace.getStackCounter())

class i386BFastCallCallingConventionTest(i386MsFastCallCallingConventionTest):

    def prepTest(self):
        i386MsFastCallCallingConventionTest.prepTest(self)
        self.cc = e_i386.BFastCall()

        self.reglist = [REG_EAX, REG_EDX, REG_ECX]

class x64MSx64CallCallingConventionTest(i386MsFastCallCallingConventionTest):

    def resetMemory(self):
        for i in self.reglist:
            self.trace.setRegister(i, 0xFFFFFFFFFFFFFFFF)

        sp = self.trace.getStackCounter()
        # write a bunch
        for i in range(0, len(self.args)*2):
            self.trace.writeMemory(sp+8*i, struct.pack('<Q', 0xEEEEEEEEEEEEEEEE))

    def prepTest(self):
        i386MsFastCallCallingConventionTest.prepTest(self)
        self.cc = e_amd64.MSx64Call()
        self.reglist = [REG_RCX, REG_RDX, REG_R8, REG_R9]

    def testSetPreCallArgs(self):
        sp = self.trace.getStackCounter()
        with constantStackCounter(self.trace):
            self.cc.setPreCallArgs(self.trace, self.args)

        if len(self.args) == 0:
            return

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkPreCallStackArgs(self.args[len(self.reglist):], skipnum=4)

    def testSetCallArgs(self):
        sp = self.trace.getStackCounter()
        with constantStackCounter(self.trace):
            self.cc.setCallArgs(self.trace, self.args)

        if len(self.args) == 0:
            return

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkCallStackArgs(self.args[len(self.reglist):], skipnum=4)

    def testSetCallArgsRet(self):
        self.resetMemory()

        with constantStackCounter(self.trace):
            self.cc.setCallArgsRet(self.trace, self.args, ra=self.retaddr)

        self.checkRegisterArgs(self.reglist, self.args)
        self.checkReturnAddress()
        self.checkCallStackArgs(self.args[len(self.reglist):], skipnum=4)

    def testExecuteCall(self):
        # TODO: test with ra=None and args=None next.
        sp = self.trace.getStackCounter()
        mem_addr = self.trace.allocateMemory(0x1000)
        self.cc.executeCall(self.trace, mem_addr, args=self.args, ra=self.retaddr)

        # TODO: check amount stack increased by makes sense.
        self.checkRegisterArgs(self.reglist, self.args)
        num_in_regs = len(self.reglist)
        self.checkCallStackArgs(self.args[num_in_regs:], skipnum=4)
        self.checkReturnAddress()
        self.checkProgramCounter(mem_addr)

    def testAllocate(self):
        num_stackargs = self.cc.getNumStackArgs(self.trace, len(self.args))

        sp = self.trace.getStackCounter()
        self.cc.allocateArgSpace(self.trace, len(self.args))
        homing = 8*4
        assert(sp - homing - self.psize*num_stackargs == self.trace.getStackCounter())

        sp = self.trace.getStackCounter()
        self.cc.allocateCallSpace(self.trace, len(self.args))
        assert(sp - homing - self.psize*num_stackargs-self.psize == self.trace.getStackCounter())

    def testExecCallReturn(self):
        self.resetMemory()
        # prereq is the return value set to known
        self.trace.writeMemory(self.trace.getStackCounter(), struct.pack('<%s' % self.ssize, self.retaddr))
        sp = self.trace.getStackCounter()
        self.cc.execCallReturn(self.trace, self.retval, len(self.args))

        num_in_registers = min(len(self.reglist), len(self.args))
        # always have homing parameters
        num_on_stack = len(self.args)
        if len(self.args) < 4:
            num_on_stack = 4
        assert(num_on_stack >= 0)
        assert(sp + self.psize == self.trace.getStackCounter())

        eax = self.trace.getRegister(REG_RAX)
        ip = self.trace.getProgramCounter()
        assert(eax == self.retval)
        assert(ip == self.retaddr)

class SysVAmd64CallCallingConventionTest(i386MsFastCallCallingConventionTest):
    def resetMemory(self):
        for i in self.reglist:
            self.trace.setRegister(i, 0xFFFFFFFFFFFFFFFF)

        sp = self.trace.getStackCounter()
        # write a bunch
        for i in range(0, len(self.args)*2):
            self.trace.writeMemory(sp+8*i, struct.pack('<Q', 0xEEEEEEEEEEEEEEEE))

    def prepTest(self):
        i386MsFastCallCallingConventionTest.prepTest(self)
        self.cc = e_amd64.SysVAmd64Call()
        self.reglist = [REG_RDI, REG_RSI, REG_RDX, REG_RCX, REG_R8, REG_R9]

class SysVAmd64SystemCallCallingConventionTest(SysVAmd64CallCallingConventionTest):

    def prepTest(self):
        SysVAmd64CallCallingConventionTest.prepTest(self)
        self.cc = e_amd64.SysVAmd64SystemCall()
        self.reglist = [REG_RDI, REG_RSI, REG_RDX, REG_R10, REG_R8, REG_R9]

if __name__ == '__main__':
    import sys
    sys.exit(22)
