"""
The envi architecture module for the AMD 64 platform.
"""
import struct

import envi
from envi.const import *
import envi.bits as e_bits
import envi.registers as e_reg
import envi.archs.i386 as e_i386

from envi.archs.amd64.regs import *
from envi.archs.amd64.disasm import *

# NOTE: The REX prefixes don't end up with displayed names
# NOTE: the REX prefix must be the *last* non escape (0f) prefix

# EMU NOTES:
# In 64 bit mode, all 32 bit dest regs get 0 extended into the rest of the bits
# In 64 bit mode, all 8/16 bit accesses do NOT modify the upper bits
# In 64 bit mode, all near branches, and implicit RSP (push pop) use RIP even w/o REX
# In 64 bit mode, if mod/rm is mod=0 and r/m is 5, it's RIP relative IMM32

class Amd64Module(e_i386.i386Module):

    def __init__(self):
        envi.ArchitectureModule.__init__(self, "amd64")
        self._arch_dis = Amd64Disasm()

    def archGetRegCtx(self):
        return Amd64RegisterContext()

    def archGetRegisterGroups(self):
        groups = envi.ArchitectureModule.archGetRegisterGroups(self)
        general = ('general', ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp',
                                'rsp', 'rip', 'r8', 'r9', 'r10', 'r11', 'r12',
                                'r13', 'r14', 'r15'], )

        groups.append(general)

        # compilers use the following regs to stick the module baseaddr in for 
        # switchcase code
        switch_mapbase = ('switch_mapbase', [ 'rdi','rsi', 'r8', 'r9', 'r10' ],)
        groups.append(switch_mapbase)
        return groups

    def getPointerSize(self):
        return 8

    def pointerString(self, va):
        return "0x%.8x" % va

    def getEmulator(self):
        return Amd64Emulator()

class MSx64Call(envi.CallingConvention):
    '''
    Has space for 4 homing parameters.
    TODO: this is a compiler option.  We should have another convention if
    this is not specified.
    '''
    arg_def = [(CC_REG, REG_RCX), (CC_REG, REG_RDX), (CC_REG, REG_R8),
                (CC_REG, REG_R9), (CC_STACK_INF, 8*4+8),]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_RAX)
    flags = CC_CALLER_CLEANUP
    align = 8
    pad = 8*4

class SysVAmd64Call(envi.CallingConvention):
    '''
    Does not have shadow space like MSx64.
    '''
    arg_def = [(CC_REG, REG_RDI), (CC_REG, REG_RSI), (CC_REG, REG_RDX),
                (CC_REG, REG_RCX), (CC_REG, REG_R8), (CC_REG, REG_R9),
                    (CC_STACK_INF, 8),]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_RAX)
    flags = CC_CALLEE_CLEANUP
    align = 8
    pad = 0

class SysVAmd64SystemCall(SysVAmd64Call):
    '''
    For system calls, R10 is used instead of RCX.
    '''
    arg_def = [(CC_REG, REG_RDI), (CC_REG, REG_RSI), (CC_REG, REG_RDX),
                (CC_REG, REG_R10), (CC_REG, REG_R8), (CC_REG, REG_R9),
                (CC_STACK_INF, 8),]

sysvamd64call = SysVAmd64Call()
sysvamd64systemcall = SysVAmd64SystemCall()
msx64call = MSx64Call()

class Amd64Emulator(Amd64RegisterContext, e_i386.IntelEmulator):

    flagidx = REG_EFLAGS
    accumreg = { 1:REG_AL, 2:REG_AX, 4:REG_EAX, 8:REG_RAX }

    def __init__(self):

        archmod = Amd64Module()
        e_i386.IntelEmulator.__init__(self, archmod=archmod)
        # The above sets up the intel reg context, so we smash over it
        Amd64RegisterContext.__init__(self)
        # For the format calls in reading memory
        self.imem_psize = 8

        self.addCallingConvention("sysvamd64call", sysvamd64call)
        self.addCallingConvention("sysvamd64systemcall", sysvamd64systemcall)
        self.addCallingConvention("msx64call", msx64call)

    def doPush(self, val):
        rsp = self.getRegister(REG_RSP)
        rsp -= 8
        self.writeMemValue(rsp, val, 8)
        self.setRegister(REG_RSP, rsp)

    def doPop(self):
        rsp = self.getRegister(REG_RSP)
        val = self.readMemValue(rsp, 8)
        self.setRegister(REG_RSP, rsp+8)
        return val

    def i_movsxd(self, op):
        val = self.getOperValue(op, 1)
        val = e_bits.sign_extend(val, 4, 8)
        self.setOperValue(op, 0, val)

    # these are movs, some deal with caching, which we don't currently care about
    i_movaps = e_i386.IntelEmulator.i_mov
    i_movapd = e_i386.IntelEmulator.i_mov
    i_movups = e_i386.IntelEmulator.i_mov
    i_movupd = e_i386.IntelEmulator.i_mov
    i_movnti = e_i386.IntelEmulator.i_mov
    i_movntpd = e_i386.IntelEmulator.i_mov
    i_movntps = e_i386.IntelEmulator.i_mov
    i_movntdq = e_i386.IntelEmulator.i_mov
    i_movntdqa = e_i386.IntelEmulator.i_mov
