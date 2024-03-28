import struct

import envi
import envi.bits as e_bits
import envi.encoding as e_enc

from envi.archs.msp430 import Msp430Module
from envi.archs.msp430.regs import *
from envi.archs.msp430.const import *


class Msp430Call(envi.CallingConvention):
    arg_def = [(CC_REG, REG_R15), (CC_REG, REG_R14), (CC_REG, REG_R13), (CC_REG, REG_R12), (CC_STACK_INF, 2)]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_R15)
    flags = CC_CALLEE_CLEANUP
    align = 2
    pad = 0


msp430call = Msp430Call()

class Msp430Emulator(Msp430RegisterContext, envi.Emulator):

    def __init__(self, regarray=None):
        self.archmod = Msp430Module()

        envi.Emulator.__init__(self, self.archmod)
        Msp430RegisterContext.__init__(self)

        self._emu_segments = [(0, 0xffff)]
        self.addCallingConvention('msp430call', msp430call)

    def getArchModule(self):
        return self.archmod

    def setFlag(self, which, state):
        flags = self.getRegister(REG_SR)
        if flags is None:
            raise envi.PDEUndefinedFlag(self)

        if state:
            flags |= which
        else:
            flags &= ~which

        self.setRegister(REG_SR, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_SR)
        if flags is None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    def readMemValue(self, addr, size):
        bytez = self.readMemory(addr, size)
        if bytez is None:
            return None

        if len(bytez) != size:
            raise Exception("Wrong length read")

        if size == 1:
            return struct.unpack("B", bytez)[0]
        elif size == 2:
            return struct.unpack("<H", bytez)[0]
        else:
            raise Exception("Invalid size")

    def writeMemValue(self, addr, value, size):
        if size == 1:
            bytez = struct.pack("B",value & 0xff)
        elif size == 2:
            bytez = struct.pack("<H",value & 0xffff)
        else:
            raise Exception("Invalid size")

        self.writeMemory(addr, bytez)

    def executeOpcode(self, op):
        meth = self.op_methods.get(op.mnem, None)
        if meth is None:
            raise envi.UnsupportedInstruction(self, op)

        newpc = meth(op)
        if newpc is not None:
            self.setProgramCounter(newpc)
            return

        pc = self.getProgramCounter()
        newpc = pc + op.size
        self.setProgramCounter(newpc)

    def getOperSize(self, op):
        if op.iflags & IF_BYTE:
            size = BYTE
        else:
            size = WORD
        return size

    # Conditions
    def cond_c(self):
        return self.getFlag(SR_C) == 1

    def cond_e(self):
        return self.getFlag(SR_Z) == 1

    def cond_ge(self):
        return (self.getFlag(SR_N) ^ self.getFlag(SR_V)) == 0

    def cond_l(self):
        return (self.getFlag(SR_N) ^ self.getFlag(SR_V)) == 1

    def cond_n(self):
        return self.getFlag(SR_N) == 1

    def cond_nc(self):
        return self.getFlag(SR_C) == 0

    def cond_ne(self):
        return self.getFlag(SR_Z) == 0

    def relJump(self, op):
        return  self.getOperValue(op, 0)

    # Helpers
    def doPop(self, size):
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, size)
        self.setRegister(REG_SP, sp + WORD)
        return val

    def doPush(self, val, size):
        sp = self.getRegister(REG_SP) - WORD
        self.writeMemValue(sp, val, size)
        self.setRegister(REG_SP, sp)

    # res = a + b + carry
    def doAddC(self, a, b, carry, size):
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)

        sa = e_bits.signed(a, size)
        sb = e_bits.signed(b, size)

        ures = ua + ub + carry
        sres = sa + sb + carry
        res = e_bits.unsigned(ures, size)

        self.setFlag(SR_N, e_bits.msb(res, size))
        self.setFlag(SR_Z, res == 0)
        self.setFlag(SR_C, e_bits.is_unsigned_carry(ures, size))
        self.setFlag(SR_V, e_bits.is_signed_overflow(sres, size))

        return res

    def doDecAddC(self, a, b, carry, size):
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)

        int_a = e_enc.bcd_to_int(ua)
        int_b = e_enc.bcd_to_int(ub)
        int_res = int_a + int_b + carry

        bcd_res = e_enc.int_to_bcd(int_res)
        res = e_bits.unsigned(bcd_res, size)

        if size == BYTE:
            bcd_max = 99
        else:
            bcd_max = 9999

        self.setFlag(SR_N, e_bits.msb(res, size))
        self.setFlag(SR_Z, res == 0)
        self.setFlag(SR_C, 1 if int_res > bcd_max else 0)

        return res

    def doAnd(self, a, b, size):
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)

        res = ua & ub

        self.setFlag(SR_N, e_bits.msb(res, size))
        self.setFlag(SR_Z, res == 0)
        self.setFlag(SR_C, res != 0)
        self.setFlag(SR_V, 0)

        return res

    # res = a - b - 1 + carry (inverted carry result)
    def doSubC(self, a, b, carry, size):
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)

        sa = e_bits.signed(a, size)
        sb = e_bits.signed(b, size)

        ures = ua - ub - 1 + carry
        sres = sa - sb - 1 + carry
        res = e_bits.unsigned(ures, size)

        self.setFlag(SR_N, e_bits.msb(res, size))
        self.setFlag(SR_Z, res == 0)
        self.setFlag(SR_C, not e_bits.is_unsigned_carry(ures, size))
        self.setFlag(SR_V, e_bits.is_signed_overflow(sres, size))

        return res

    # Instructions
    def i_adc(self, op):
        dst = self.getOperValue(op, 0)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doAddC(0, dst, c, size)
        self.setOperValue(op, 0, res)

    def i_add(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        res = self.doAddC(src, dst, 0, size)
        self.setOperValue(op, 1, res)

    def i_addc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doAddC(src, dst, c, size)
        self.setOperValue(op, 1, res)

    def i_and(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        res = self.doAnd(src, dst, size)
        self.setOperValue(op, 1, res)

    def i_bic(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        usrc = e_bits.unsigned(~src, size)
        udst = e_bits.unsigned(dst, size)

        res = usrc & udst

        self.setOperValue(op, 1, res)

    def i_bis(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        usrc = e_bits.unsigned(src, size)
        udst = e_bits.unsigned(dst, size)

        res = usrc | udst

        self.setOperValue(op, 1, res)

    def i_bit(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        res = self.doAnd(src, dst, size)

        self.setOperValue(op, 1, res)

    def i_br(self, op):
        pc = self.getOperValue(op, 0)
        return pc

    def i_call(self, op):
        pc = self.getRegister(REG_PC)
        retaddr = pc + op.size
        self.doPush(retaddr, WORD)
        return self.getOperValue(op, 0)

    def i_clr(self, op):
        self.setOperValue(op, 0, 0)

    def i_clrc(self, op):
        self.setFlag(SR_C, 0)

    def i_clrn(self, op):
        self.setFlag(SR_N, 0)

    def i_clrz(self, op):
        self.setFlag(SR_Z, 0)

    def i_cmp(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        self.doSubC(dst, src, 1, size)

    def i_dadc(self, op):
        dst = self.getOperValue(op, 0)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doDecAddC(0, dst, c, size)
        self.setOperValue(op, 0, res)

    def i_dadd(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doDecAddC(src, dst, 0, size)
        self.setOperValue(op, 1, res)

    def i_dec(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        res = self.doSubC(dst, 1, 1, size)
        self.setOperValue(op, 0, res)

    def i_decd(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        res = self.doSubC(dst, 2, 1, size)
        self.setOperValue(op, 0, res)

    def i_dint(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_eint(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_inc(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        res = self.doAddC(1, dst, 0, size)
        self.setOperValue(op, 0, res)

    def i_incd(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        res = self.doAddC(2, dst, 0, size)
        self.setOperValue(op, 0, res)

    def i_inv(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        udst = e_bits.unsigned(dst, size)
        res = e_bits.unsigned(~dst, size)

        self.setFlag(SR_N, e_bits.msb(res, size))
        self.setFlag(SR_Z, res == 0)
        self.setFlag(SR_C, res != 0)
        self.setFlag(SR_V, e_bits.msb(udst, size))

        self.setOperValue(op, 0, res)

    def i_jc(self, op):
        if self.cond_c(): return self.relJump(op)
    i_jhs = i_jc

    def i_jeq(self, op):
        if self.cond_e(): return self.relJump(op)
    i_jz = i_jeq

    def i_jge(self, op):
        if self.cond_ge(): return self.relJump(op)

    def i_jl(self, op):
        if self.cond_l(): return self.relJump(op)

    def i_jmp(self, op):
        return self.relJump(op)

    def i_jn(self, op):
        if self.cond_n(): return self.relJump(op)

    def i_jnc(self, op):
        if self.cond_nc(): return self.relJump(op)
    i_jlo = i_jnc

    def i_jne(self, op):
        if self.cond_ne(): return self.relJump(op)
    i_jnz = i_jne

    def i_mov(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        res = e_bits.unsigned(src, size)
        self.setOperValue(op, 1, res)

    def i_nop(self, op):
        pass

    def i_pop(self, op):
        size = self.getOperSize(op)
        val = self.doPop(size)
        self.setOperValue(op, 0, val)

    def i_push(self, op):
        size = self.getOperSize(op)
        val = self.getOperValue(op, 0)
        self.doPush(val, size)

    def i_ret(self, op):
        pc = self.doPop(WORD)
        return pc

    def i_reti(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_rla(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        udst = e_bits.unsigned(dst, size)

        self.setFlag(SR_C, e_bits.msb(udst, size))
        res = udst << 1
        ures = e_bits.unsigned(res, size)

        if size == BYTE:
            val_min = 0x40
            val_max = 0xc0
        else:
            val_min = 0x4000
            val_max = 0xc000

        self.setFlag(SR_N, e_bits.msb(ures, size))
        self.setFlag(SR_Z, ures == 0)
        self.setFlag(SR_V, udst >= val_min and udst < val_max)

        self.setOperValue(op, 0, ures)

    def i_rlc(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        udst = e_bits.unsigned(dst, size)

        c = self.getFlag(SR_C)
        self.setFlag(SR_C, e_bits.msb(udst, size))
        res = (udst << 1) | c
        ures = e_bits.unsigned(res, size)

        if size == BYTE:
            val_min = 0x40
            val_max = 0xc0
        else:
            val_min = 0x4000
            val_max = 0xc000

        self.setFlag(SR_N, e_bits.msb(ures, size))
        self.setFlag(SR_Z, ures == 0)
        self.setFlag(SR_V, udst >= val_min and udst < val_max)

        self.setOperValue(op, 0, ures)

    def i_rra(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        udst = e_bits.unsigned(dst, size)

        shift = (size * 8) - 1
        res = (e_bits.msb(udst, size) << shift) | (udst>>1)
        ures = e_bits.unsigned(res, size)

        self.setFlag(SR_N, e_bits.msb(ures, size))
        self.setFlag(SR_Z, ures == 0)
        self.setFlag(SR_C, e_bits.lsb(udst))
        self.setFlag(SR_V, 0)

        self.setOperValue(op, 0, ures)

    def i_rrc(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        c = self.getFlag(SR_C)
        udst = e_bits.unsigned(dst, size)

        shift = (size * 8) - 1
        res = (c << shift) | (udst>>1)
        ures = e_bits.unsigned(res, size)

        self.setFlag(SR_N, e_bits.msb(ures, size))
        self.setFlag(SR_Z, ures == 0)
        self.setFlag(SR_C, e_bits.lsb(udst))
        self.setFlag(SR_V, 0)

        self.setOperValue(op, 0, ures)

    def i_sbc(self, op):
        dst = self.getOperValue(op, 0)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doSubC(dst, 0, c, size)
        self.setOperValue(op, 0, res)

    def i_setc(self, op):
        self.setFlag(SR_C, 1)

    def i_setn(self, op):
        self.setFlag(SR_N, 1)

    def i_setz(self, op):
        self.setFlag(SR_Z, 1)

    def i_sub(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        res = self.doSubC(dst, src, 1, size)
        self.setOperValue(op, 1, res)

    def i_subc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        c = self.getFlag(SR_C)

        size = self.getOperSize(op)

        res = self.doSubC(dst, src, c, size)
        self.setOperValue(op, 1, res)

    i_sbb = i_subc

    def i_swpb(self, op):
        dst = self.getOperValue(op, 0)

        udst = e_bits.unsigned(dst, WORD)

        res = ((udst&0xff) << 8) | ((udst&0xff00) >> 8)
        self.setOperValue(op, 0, res)

    def i_sxt(self, op):
        dst = self.getOperValue(op, 0)

        udst = e_bits.unsigned(dst, BYTE)

        smax = e_bits.s_maxes[BYTE]
        umax = e_bits.u_maxes[WORD]

        if udst > smax:
            ubits = smax ^ umax
            udst |= ubits

        self.setFlag(SR_N, e_bits.msb(udst, WORD))
        self.setFlag(SR_Z, dst == 0)
        self.setFlag(SR_C, dst != 0)
        self.setFlag(SR_V, 0)

        self.setOperValue(op, 0, udst)

    def i_tst(self, op):
        dst = self.getOperValue(op, 0)

        size = self.getOperSize(op)

        udst = e_bits.unsigned(dst, size)

        self.setFlag(SR_N, e_bits.msb(udst, size))
        self.setFlag(SR_Z, udst == 0)
        self.setFlag(SR_C, 1)
        self.setFlag(SR_V, 0)

    def i_xor(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        size = self.getOperSize(op)

        usrc = e_bits.unsigned(src, size)
        udst = e_bits.unsigned(dst, size)

        ures = usrc ^ udst

        self.setFlag(SR_N, e_bits.msb(ures, size))
        self.setFlag(SR_Z, ures == 0)
        self.setFlag(SR_C, ures != 0)
        self.setFlag(SR_V, e_bits.msb(usrc, size) and e_bits.msb(udst, size))

        self.setOperValue(op, 1, ures)
