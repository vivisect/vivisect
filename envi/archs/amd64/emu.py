import envi
import envi.archs.i386.emu as e_i386_emu
import envi.archs.amd64.regs as e_amd64_regs

from envi.const import CC_STACK_INF, CC_REG, CC_STACK, CC_CALLEE_CLEANUP, CC_CALLER_CLEANUP
from envi.archs.amd64.regs import *


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
               (CC_STACK_INF, 8)]


sysvamd64call = SysVAmd64Call()
sysvamd64systemcall = SysVAmd64SystemCall()
msx64call = MSx64Call()


class Amd64Emulator(e_amd64_regs.Amd64RegisterContext, e_i386_emu.IntelEmulator):
    flagidx = REG_EFLAGS
    accumreg = {
        1: REG_AL,
        2: REG_AX,
        4: REG_EAX,
        8: REG_RAX
    }

    def __init__(self):

        e_i386.IntelEmulator.__init__(self, archid=envi.ARCH_AMD64)
        # The above sets up the intel reg context, so we smash over it
        e_amd64_regs.Amd64RegisterContext.__init__(self)
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
    i_movaps = e_i386_emu.IntelEmulator.i_mov
    i_movapd = e_i386_emu.IntelEmulator.i_mov
    i_movups = e_i386_emu.IntelEmulator.i_mov
    i_movupd = e_i386_emu.IntelEmulator.i_mov
    i_movnti = e_i386_emu.IntelEmulator.i_mov
    i_movntpd = e_i386_emu.IntelEmulator.i_mov
    i_movntps = e_i386_emu.IntelEmulator.i_mov
    i_movntdq = e_i386_emu.IntelEmulator.i_mov
    i_movntdqa = e_i386_emu.IntelEmulator.i_mov
