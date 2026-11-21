import struct

import envi
import envi.bits as e_bits

from envi.archs.rx import RxModule
from envi.archs.rx.regs import *
from envi.archs.rx.const import *


class RxCall(envi.CallingConvention):
    '''
    RX calling convention.

    The RX ABI passes arguments in registers r1-r4, then on the stack.
    The return value is in r1.  The return address is pushed onto the
    stack by the caller (via bsr/jsr).  The stack is 32-bit aligned.
    '''
    arg_def = [(CC_REG, REG_R1), (CC_REG, REG_R2), (CC_REG, REG_R3), (CC_REG, REG_R4), (CC_STACK_INF, 4)]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_R1)
    flags = CC_CALLEE_CLEANUP
    align = 4
    pad = 0


rxcall = RxCall()


class RxEmulator(RxRegisterContext, envi.Emulator):

    def __init__(self, regarray=None):
        self.archmod = RxModule()

        envi.Emulator.__init__(self, self.archmod)
        RxRegisterContext.__init__(self)

        self._emu_segments = [(0, 0xffff)]
        self.addCallingConvention('rxcall', rxcall)

    def getArchModule(self):
        return self.archmod

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

    # ------------------------------------------------------------------
    # PSW flag helpers — RX uses C, Z, S, O (not N/V)
    # ------------------------------------------------------------------
    def setFlag(self, which, state):
        flags = self.getRegister(REG_PSW)
        if flags is None:
            raise envi.PDEUndefinedFlag(self)
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(REG_PSW, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_PSW)
        if flags is None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    # Convenience properties for the 4 ALU flags
    @property
    def C(self):
        return self.getFlag(PSW_C)

    @property
    def Z(self):
        return self.getFlag(PSW_Z)

    @property
    def S(self):
        return self.getFlag(PSW_S)

    @property
    def O(self):
        return self.getFlag(PSW_O)

    # ------------------------------------------------------------------
    # Memory helpers — RX is 32-bit, little-endian, supports B/W/L
    # ------------------------------------------------------------------
    def readMemValue(self, addr, size):
        bytez = self.readMemory(addr, size)
        if bytez is None:
            return None
        if len(bytez) != size:
            raise Exception("Wrong length read at 0x%x (wanted %d got %d)" % (addr, size, len(bytez)))
        return e_bits.parsebytes(bytez, 0, size, False, self.getEndian())

    def writeMemValue(self, addr, value, size):
        mask = e_bits.u_maxes[size]
        bytez = e_bits.buildbytes(value & mask, size, self.getEndian())
        self.writeMemory(addr, bytez)

    # ------------------------------------------------------------------
    # Operand size — RX supports .b (1), .w (2), .l (4)
    # ------------------------------------------------------------------
    def getOperSize(self, op):
        if op.iflags & IF_BYTE:
            return 1
        elif op.iflags & IF_WORD:
            return 2
        elif op.iflags & IF_LONG:
            return 4
        elif op.iflags & IF_UWORD:
            return 2
        # Default to 4 bytes (32-bit) for RX
        return 4

    # ------------------------------------------------------------------
    # Core ALU helpers
    # ------------------------------------------------------------------
    def doAdd(self, a, b, size):
        '''Return a + b with flag updates. C, Z, S, O set per RX spec.'''
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)
        sa = e_bits.signed(a, size)
        sb = e_bits.signed(b, size)

        ures = ua + ub
        sres = sa + sb
        res = e_bits.unsigned(ures, size)

        self.setFlag(PSW_C, e_bits.is_unsigned_carry(ures, size))
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, e_bits.is_signed_overflow(sres, size))
        return res

    def doSub(self, a, b, size):
        '''Return a - b with flag updates. C = NOT borrow (RX convention).'''
        ua = e_bits.unsigned(a, size)
        ub = e_bits.unsigned(b, size)
        sa = e_bits.signed(a, size)
        sb = e_bits.signed(b, size)

        ures = ua - ub
        sres = sa - sb
        res = e_bits.unsigned(ures, size)

        self.setFlag(PSW_C, not e_bits.is_unsigned_carry(ures, size))
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, e_bits.is_signed_overflow(sres, size))
        return res

    def doLogic(self, res, size):
        '''Update flags for logical operations. C=0, V=0 per RX spec.'''
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_C, 0)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        return res

    # ------------------------------------------------------------------
    # Stack helpers — 32-bit stack
    # ------------------------------------------------------------------
    def doPop(self, size=4):
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, size)
        self.setRegister(REG_SP, sp + 4)
        return val

    def doPush(self, val, size=4):
        sp = self.getRegister(REG_SP) - 4
        self.writeMemValue(sp, val, size)
        self.setRegister(REG_SP, sp)

    # ------------------------------------------------------------------
    # Condition codes (for branches, SCCND, BMCND)
    # Order matches BMCND/SCCND tables in const.py:
    #   z, nz, geu, ltu, gtu, leu, pz, n, ge, lt, gt, le, o, no
    # ------------------------------------------------------------------
    def evalCond(self, cd):
        if cd == 0:   # z
            return self.Z
        elif cd == 1: # nz
            return not self.Z
        elif cd == 2: # geu (unsigned >=)
            return self.C
        elif cd == 3: # ltu (unsigned <)
            return not self.C
        elif cd == 4: # gtu (unsigned >)
            return (not self.Z) and self.C
        elif cd == 5: # leu (unsigned <=)
            return self.Z or (not self.C)
        elif cd == 6: # pz (positive or zero)
            return not self.S
        elif cd == 7: # n (negative)
            return self.S
        elif cd == 8: # ge (signed >=)
            return self.S == self.O
        elif cd == 9: # lt (signed <)
            return self.S != self.O
        elif cd == 10: # gt (signed >)
            return (not self.Z) and (self.S == self.O)
        elif cd == 11: # le (signed <=)
            return self.Z or (self.S != self.O)
        elif cd == 12: # o (overflow)
            return self.O
        elif cd == 13: # no (no overflow)
            return not self.O
        raise Exception("Unknown condition code: %d" % cd)

    def relJump(self, op):
        return self.getOperValue(op, 0)

    # ------------------------------------------------------------------
    # Instruction implementations
    # ------------------------------------------------------------------
    def i_abs(self, op):
        # abs rd  or  abs rs, rd
        if len(op.opers) == 1:
            val = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            sval = e_bits.signed(val, size)
            res = -sval if sval < 0 else sval
            res = e_bits.unsigned(res, size)
            self.setFlag(PSW_Z, res == 0)
            self.setFlag(PSW_S, e_bits.msb(res, size))
            self.setFlag(PSW_O, 0)
            self.setOperValue(op, 0, res)
        else:
            src = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            sval = e_bits.signed(src, size)
            res = -sval if sval < 0 else sval
            res = e_bits.unsigned(res, size)
            self.setFlag(PSW_Z, res == 0)
            self.setFlag(PSW_S, e_bits.msb(res, size))
            self.setFlag(PSW_O, 0)
            self.setOperValue(op, 1, res)

    def i_adc(self, op):
        dst = self.getOperValue(op, 1)
        c = 1 if self.C else 0
        size = self.getOperSize(op)
        res = self.doAdd(dst, c, size)
        self.setOperValue(op, 1, res)

    def i_add(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        res = self.doAdd(dst, src, size)
        self.setOperValue(op, 1, res)

    def i_and(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        res = self.doLogic(src & dst, size)
        self.setOperValue(op, 1, res)

    def i_bclr(self, op):
        # bclr #imm, rd  or  bclr rs, [rd+dsp]
        if len(op.opers) == 2:
            bitno = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            size = getattr(op.opers[1], 'tsize', 1) or 1
            mask = e_bits.u_maxes[size]
            res = val & mask & ~(1 << bitno)
            self.setOperValue(op, 1, res)

    # BMCND — conditional bit set/clear
    def _bmcnd(self, op, cd):
        bitno = self.getOperValue(op, 0)
        val = self.getOperValue(op, 1)
        size = 1  # BMCND always operates on a byte
        mask = e_bits.u_maxes[size]
        if self.evalCond(cd):
            res = (val & mask) | (1 << bitno)
        else:
            res = (val & mask) & ~(1 << bitno)
        self.setOperValue(op, 1, res)

    def i_bmz(self, op):   self._bmcnd(op, 0)
    def i_bmnz(self, op):  self._bmcnd(op, 1)
    def i_bmgeu(self, op): self._bmcnd(op, 2)
    def i_bmltu(self, op): self._bmcnd(op, 3)
    def i_bmgtu(self, op): self._bmcnd(op, 4)
    def i_bmleu(self, op): self._bmcnd(op, 5)
    def i_bmpz(self, op):  self._bmcnd(op, 6)
    def i_bmn(self, op):   self._bmcnd(op, 7)
    def i_bmge(self, op):  self._bmcnd(op, 8)
    def i_bmlt(self, op):  self._bmcnd(op, 9)
    def i_bmgt(self, op):  self._bmcnd(op, 10)
    def i_bmle(self, op):  self._bmcnd(op, 11)
    def i_bmo(self, op):   self._bmcnd(op, 12)
    def i_bmno(self, op):  self._bmcnd(op, 13)

    def i_bmcnd(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_bnot(self, op):
        # bnot #imm, [rd+dsp]  or  bnot rs, [rd+dsp]
        if len(op.opers) == 2:
            bitno = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            size = 1
            mask = e_bits.u_maxes[size]
            res = (val & mask) ^ (1 << bitno)
            self.setOperValue(op, 1, res)

    def i_bra(self, op):
        return self.relJump(op)

    def i_brk(self, op):
        raise envi.BreakpointHit(self, op)

    def i_bset(self, op):
        if len(op.opers) == 2:
            bitno = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            size = getattr(op.opers[1], 'tsize', 1) or 1
            mask = e_bits.u_maxes[size]
            res = (val & mask) | (1 << bitno)
            self.setOperValue(op, 1, res)

    def i_bsr(self, op):
        pc = self.getRegister(REG_PC)
        retaddr = pc + op.size
        self.doPush(retaddr, 4)
        return self.relJump(op)

    def i_btst(self, op):
        if len(op.opers) == 2:
            bitno = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            bit = (val >> bitno) & 1
            self.setFlag(PSW_Z, not bit)
            self.setFlag(PSW_S, 0)
            self.setFlag(PSW_O, 0)

    # Conditional branches
    def i_bz(self, op):
        if self.Z: return self.relJump(op)

    def i_bnz(self, op):
        if not self.Z: return self.relJump(op)

    def i_bgeu(self, op):
        if self.C: return self.relJump(op)

    def i_bltu(self, op):
        if not self.C: return self.relJump(op)

    def i_bgtu(self, op):
        if (not self.Z) and self.C: return self.relJump(op)

    def i_bleu(self, op):
        if self.Z or (not self.C): return self.relJump(op)

    def i_bpz(self, op):
        if not self.S: return self.relJump(op)

    def i_bn(self, op):
        if self.S: return self.relJump(op)

    def i_bge(self, op):
        if self.S == self.O: return self.relJump(op)

    def i_blt(self, op):
        if self.S != self.O: return self.relJump(op)

    def i_bgt(self, op):
        if (not self.Z) and (self.S == self.O): return self.relJump(op)

    def i_ble(self, op):
        if self.Z or (self.S != self.O): return self.relJump(op)

    def i_bo(self, op):
        if self.O: return self.relJump(op)

    def i_bno(self, op):
        if not self.O: return self.relJump(op)

    def i_clrpsw(self, op):
        # clrpsw cb — clear a bit in PSW
        # The CB operand's flag field gives the bit position
        bitno = op.opers[0].flag
        self.setFlag(1 << bitno, 0)

    def i_cmp(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        self.doSub(dst, src, size)

    def i_div(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        if src == 0:
            self.setFlag(PSW_O, 1)
            return
        sdst = e_bits.signed(dst, size)
        ssrc = e_bits.signed(src, size)
        q = int(sdst / ssrc)  # truncate toward zero (C convention)
        res = e_bits.unsigned(q, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_divu(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        if src == 0:
            self.setFlag(PSW_O, 1)
            return
        udst = e_bits.unsigned(dst, size)
        usrc = e_bits.unsigned(src, size)
        q = udst // usrc
        res = e_bits.unsigned(q, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_emaca(self, op):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        acc_idx = op.opers[2].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc += srs * srs2
        self.setRegister(REG_ACC0 + acc_idx, acc & 0xFFFFFFFFFFFF)

    def i_emsba(self, op):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        acc_idx = op.opers[2].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc -= srs * srs2
        self.setRegister(REG_ACC0 + acc_idx, acc & 0xFFFFFFFFFFFF)

    def i_emul(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        ssrc = e_bits.signed(src, size)
        sdst = e_bits.signed(dst, size)
        res = ssrc * sdst
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_emula(self, op):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        acc_idx = op.opers[2].reg - REG_ACC0
        self.setRegister(REG_ACC0 + acc_idx, (srs * srs2) & 0xFFFFFFFFFFFF)

    def i_emulu(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        usrc = e_bits.unsigned(src, size)
        udst = e_bits.unsigned(dst, size)
        res = usrc * udst
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_int(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_itof(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        sval = e_bits.signed(src, size)
        fval = float(sval)
        res = struct.unpack('<I', struct.pack('<f', fval))[0]
        self.setOperValue(op, 1, res)

    def i_jmp(self, op):
        return self.getOperValue(op, 0)

    def i_jsr(self, op):
        pc = self.getRegister(REG_PC)
        retaddr = pc + op.size
        self.doPush(retaddr, 4)
        return self.getOperValue(op, 0)

    def _mac(self, op, part):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        if part == 'hi':
            prod = (srs >> 16) * (srs2 >> 16)
        elif part == 'lo':
            prod = (srs & 0xFFFF) * (srs2 & 0xFFFF)
        elif part == 'lh':
            prod = (srs & 0xFFFF) * (srs2 >> 16)
        else:
            prod = srs * srs2
        acc_idx = op.opers[2].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc += prod
        self.setRegister(REG_ACC0 + acc_idx, acc & 0xFFFFFFFFFFFF)

    def i_machi(self, op): self._mac(op, 'hi')
    def i_maclh(self, op): self._mac(op, 'lh')
    def i_maclo(self, op): self._mac(op, 'lo')

    def _msb(self, op, part):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        if part == 'hi':
            prod = (srs >> 16) * (srs2 >> 16)
        elif part == 'lo':
            prod = (srs & 0xFFFF) * (srs2 & 0xFFFF)
        elif part == 'lh':
            prod = (srs & 0xFFFF) * (srs2 >> 16)
        else:
            prod = srs * srs2
        acc_idx = op.opers[2].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc -= prod
        self.setRegister(REG_ACC0 + acc_idx, acc & 0xFFFFFFFFFFFF)

    def i_msbhi(self, op): self._msb(op, 'hi')
    def i_msblh(self, op): self._msb(op, 'lh')
    def i_msblo(self, op): self._msb(op, 'lo')

    def _mul_part(self, op, part):
        rs = self.getOperValue(op, 0)
        rs2 = self.getOperValue(op, 1)
        srs = e_bits.signed(rs, 4)
        srs2 = e_bits.signed(rs2, 4)
        if part == 'hi':
            prod = (srs >> 16) * (srs2 >> 16)
        elif part == 'lo':
            prod = (srs & 0xFFFF) * (srs2 & 0xFFFF)
        elif part == 'lh':
            prod = (srs & 0xFFFF) * (srs2 >> 16)
        else:
            prod = srs * srs2
        acc_idx = op.opers[2].reg - REG_ACC0
        self.setRegister(REG_ACC0 + acc_idx, prod & 0xFFFFFFFFFFFF)

    def i_mulhi(self, op): self._mul_part(op, 'hi')
    def i_mullh(self, op): self._mul_part(op, 'lh')
    def i_mullo(self, op): self._mul_part(op, 'lo')

    def i_max(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        ssrc = e_bits.signed(src, size)
        sdst = e_bits.signed(dst, size)
        res = ssrc if ssrc > sdst else sdst
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_min(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        ssrc = e_bits.signed(src, size)
        sdst = e_bits.signed(dst, size)
        res = ssrc if ssrc < sdst else sdst
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_mov(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        res = e_bits.unsigned(src, size) if src is not None else None
        self.setOperValue(op, len(op.opers) - 1, res)

    def i_movco(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_movli(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_movu(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        res = e_bits.unsigned(src, size) if src is not None else None
        self.setOperValue(op, len(op.opers) - 1, res)

    def i_mul(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        ssrc = e_bits.signed(src, size)
        sdst = e_bits.signed(dst, size)
        res = ssrc * sdst
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 1, res)

    def i_mvfacgu(self, op):
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        res = (acc >> 32) & 0xFFFF
        self.setOperValue(op, 2, res)

    def i_mvfachi(self, op):
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        res = (acc >> 16) & 0xFFFFFFFF
        self.setOperValue(op, 2, res)

    def i_mvfaclo(self, op):
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        res = acc & 0xFFFFFFFF
        self.setOperValue(op, 2, res)

    def i_mvfacmi(self, op):
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        res = (acc >> 16) & 0xFFFFFFFF
        self.setOperValue(op, 2, res)

    def i_mvfc(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_mvtacgu(self, op):
        src = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc = (acc & 0xFFFFFFFF) | ((src & 0xFFFF) << 32)
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_mvtachi(self, op):
        src = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc = (acc & 0xFFFFFFFF) | ((src & 0xFFFF) << 16)
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_mvtaclo(self, op):
        src = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        acc = (acc & 0xFFFFFFFF0000) | (src & 0xFFFFFFFF)
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_mvtc(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_mvtipl(self, op):
        imm = self.getOperValue(op, 0)
        self.setRegister(REG_IPL, imm & 0xF)

    def i_neg(self, op):
        if len(op.opers) == 1:
            val = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            res = self.doSub(0, val, size)
            self.setOperValue(op, 0, res)
        else:
            src = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            res = self.doSub(0, src, size)
            self.setOperValue(op, 1, res)

    def i_nop(self, op):
        pass

    def i_not(self, op):
        if len(op.opers) == 1:
            val = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            res = self.doLogic(~val, size)
            self.setOperValue(op, 0, res)
        else:
            src = self.getOperValue(op, 0)
            size = self.getOperSize(op)
            res = self.doLogic(~src, size)
            self.setOperValue(op, 1, res)

    def i_or(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        res = self.doLogic(src | dst, size)
        self.setOperValue(op, 1, res)

    def i_pop(self, op):
        val = self.doPop(4)
        self.setOperValue(op, 0, val)

    def i_popc(self, op):
        val = self.doPop(4)
        self.setOperValue(op, 0, val)

    def i_popm(self, op):
        rd = op.opers[0].reg
        rd2 = op.opers[1].reg
        for reg in range(rd2, rd - 1, -1):
            val = self.doPop(4)
            self.setRegister(reg, val)

    def i_push(self, op):
        size = self.getOperSize(op)
        val = self.getOperValue(op, 0)
        self.doPush(val, size)

    def i_pushc(self, op):
        val = self.getOperValue(op, 0)
        self.doPush(val, 4)

    def i_pushm(self, op):
        rs = op.opers[0].reg
        rs2 = op.opers[1].reg
        for reg in range(rs2, rs - 1, -1):
            val = self.getRegister(reg)
            self.doPush(val, 4)

    def i_racl(self, op):
        imm = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        shift = imm + 1
        acc = ((acc << shift) | (acc >> (48 - shift))) & 0xFFFFFFFFFFFF
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_racw(self, op):
        imm = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        shift = imm + 1
        acc = (acc << shift) & 0xFFFFFFFFFFFF
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_rdacl(self, op):
        imm = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        shift = imm + 1
        acc = ((acc >> shift) | (acc << (48 - shift))) & 0xFFFFFFFFFFFF
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_rdacw(self, op):
        imm = self.getOperValue(op, 0)
        acc_idx = op.opers[1].reg - REG_ACC0
        acc = self.getRegister(REG_ACC0 + acc_idx)
        shift = imm + 1
        acc = (acc >> shift) & 0xFFFFFFFFFFFF
        self.setRegister(REG_ACC0 + acc_idx, acc)

    def i_revl(self, op):
        src = self.getOperValue(op, 0)
        res = struct.unpack('<I', struct.pack('>I', src & 0xFFFFFFFF))[0]
        self.setOperValue(op, 1, res)

    def i_revw(self, op):
        src = self.getOperValue(op, 0)
        lo = ((src & 0xFF00) >> 8) | ((src & 0xFF) << 8)
        hi = ((src & 0xFF000000) >> 8) | ((src & 0x00FF0000) << 8)
        res = hi | lo
        self.setOperValue(op, 1, res)

    def i_rmpa(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_rolc(self, op):
        val = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        c = 1 if self.C else 0
        uval = e_bits.unsigned(val, size)
        msb = e_bits.msb(uval, size)
        res = ((uval << 1) | c) & e_bits.u_maxes[size]
        self.setFlag(PSW_C, msb)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 0, res)

    def i_rorc(self, op):
        val = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        c = 1 if self.C else 0
        uval = e_bits.unsigned(val, size)
        lsb = uval & 1
        shift = (size * 8) - 1
        res = (c << shift) | (uval >> 1)
        res = res & e_bits.u_maxes[size]
        self.setFlag(PSW_C, lsb)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, 0, res)

    def i_rotl(self, op):
        if len(op.opers) == 2:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 1
        else:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 0)
            dst_idx = 0
        size = self.getOperSize(op)
        uval = e_bits.unsigned(val, size)
        bits = size * 8
        shift = shift % bits
        if shift == 0:
            res = uval
        else:
            res = ((uval << shift) | (uval >> (bits - shift))) & e_bits.u_maxes[size]
        carry = (res >> (bits - 1)) & 1
        self.setFlag(PSW_C, carry)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, dst_idx, res)

    def i_rotr(self, op):
        if len(op.opers) == 2:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 1
        else:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 0)
            dst_idx = 0
        size = self.getOperSize(op)
        uval = e_bits.unsigned(val, size)
        bits = size * 8
        shift = shift % bits
        if shift == 0:
            res = uval
        else:
            res = ((uval >> shift) | (uval << (bits - shift))) & e_bits.u_maxes[size]
        carry = res & 1
        self.setFlag(PSW_C, carry)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, dst_idx, res)

    def i_round(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        fval = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        ival = int(round(fval))
        res = e_bits.unsigned(ival, size)
        self.setOperValue(op, 1, res)

    def i_rte(self, op):
        pc = self.doPop(4)
        psw = self.doPop(4)
        self.setRegister(REG_PSW, psw)
        return pc

    def i_rtfi(self, op):
        pc = self.doPop(4)
        psw = self.doPop(4)
        self.setRegister(REG_PSW, psw)
        return pc

    def i_rts(self, op):
        pc = self.doPop(4)
        return pc

    def i_rtsd(self, op):
        imm = self.getOperValue(op, 0)
        if len(op.opers) == 3:
            rd = op.opers[1].reg
            rd2 = op.opers[2].reg
            for reg in range(rd2, rd - 1, -1):
                val = self.doPop(4)
                self.setRegister(reg, val)
        sp = self.getRegister(REG_SP)
        self.setRegister(REG_SP, sp + imm)
        pc = self.doPop(4)
        return pc

    def i_sat(self, op):
        val = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        if self.O:
            if self.S:
                res = e_bits.u_maxes[size] // 2 + 1  # most negative
            else:
                res = e_bits.s_maxes[size]  # most positive
        else:
            res = val
        self.setOperValue(op, 0, res)

    def i_satr(self, op):
        pass

    def i_sbb(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        borrow = 0 if self.C else 1
        res = self.doSub(dst, src + borrow, size)
        self.setOperValue(op, 1, res)

    # SCCND — set rd to 1/0 based on condition
    def _sccnd(self, op, cd):
        size = self.getOperSize(op)
        res = 1 if self.evalCond(cd) else 0
        res = e_bits.unsigned(res, size)
        self.setOperValue(op, 0, res)

    def i_scz(self, op):   self._sccnd(op, 0)
    def i_scnz(self, op):  self._sccnd(op, 1)
    def i_scgeu(self, op): self._sccnd(op, 2)
    def i_scltu(self, op): self._sccnd(op, 3)
    def i_scgtu(self, op): self._sccnd(op, 4)
    def i_scleu(self, op): self._sccnd(op, 5)
    def i_scpz(self, op):  self._sccnd(op, 6)
    def i_scn(self, op):   self._sccnd(op, 7)
    def i_scge(self, op):  self._sccnd(op, 8)
    def i_sclt(self, op):  self._sccnd(op, 9)
    def i_scgt(self, op):  self._sccnd(op, 10)
    def i_scle(self, op):  self._sccnd(op, 11)
    def i_sco(self, op):   self._sccnd(op, 12)
    def i_scno(self, op):  self._sccnd(op, 13)

    def i_sccnd(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_scmpu(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_setpsw(self, op):
        bitno = op.opers[0].flag
        self.setFlag(1 << bitno, 1)

    def i_shar(self, op):
        if len(op.opers) == 2:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 1
        elif len(op.opers) == 3:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 2
        else:
            return
        size = self.getOperSize(op)
        uval = e_bits.unsigned(val, size)
        sval = e_bits.signed(val, size)
        carry = (uval >> (shift - 1)) & 1 if shift > 0 else 0
        res = sval >> shift
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_C, carry)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, dst_idx, res)

    def i_shll(self, op):
        if len(op.opers) == 2:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 1
        elif len(op.opers) == 3:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 2
        else:
            return
        size = self.getOperSize(op)
        uval = e_bits.unsigned(val, size)
        bits = size * 8
        if shift >= bits:
            carry = 0
            res = 0
        else:
            carry = (uval >> (bits - shift)) & 1
            res = (uval << shift) & e_bits.u_maxes[size]
        self.setFlag(PSW_C, carry)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, dst_idx, res)

    def i_shlr(self, op):
        if len(op.opers) == 2:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 1
        elif len(op.opers) == 3:
            shift = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dst_idx = 2
        else:
            return
        size = self.getOperSize(op)
        uval = e_bits.unsigned(val, size)
        carry = (uval >> (shift - 1)) & 1 if shift > 0 else 0
        res = uval >> shift
        res = e_bits.unsigned(res, size)
        self.setFlag(PSW_C, carry)
        self.setFlag(PSW_Z, res == 0)
        self.setFlag(PSW_S, e_bits.msb(res, size))
        self.setFlag(PSW_O, 0)
        self.setOperValue(op, dst_idx, res)

    # String instructions — stubs (require register-pointer iteration)
    def i_smovb(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_smovf(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_smovu(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_sstr(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_suntil(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_swhile(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_stz(self, op):
        if self.Z:
            src = self.getOperValue(op, 0)
            self.setOperValue(op, 1, src)

    def i_stnz(self, op):
        if not self.Z:
            src = self.getOperValue(op, 0)
            self.setOperValue(op, 1, src)

    def i_sub(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        res = self.doSub(dst, src, size)
        self.setOperValue(op, 1, res)

    def i_tst(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        self.doLogic(src & dst, size)

    def i_utof(self, op):
        src = self.getOperValue(op, 0)
        size = self.getOperSize(op)
        uval = e_bits.unsigned(src, size)
        fval = float(uval)
        res = struct.unpack('<I', struct.pack('<f', fval))[0]
        self.setOperValue(op, 1, res)

    def i_wait(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_xchg(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        self.setOperValue(op, 0, dst)
        self.setOperValue(op, 1, src)
        size = self.getOperSize(op)
        self.doLogic(src & dst, size)

    def i_xor(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        size = self.getOperSize(op)
        res = self.doLogic(src ^ dst, size)
        self.setOperValue(op, 1, res)

    # Floating-point instructions
    def i_fadd(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        fdst = struct.unpack('<f', struct.pack('<I', dst & 0xFFFFFFFF))[0]
        res = struct.unpack('<I', struct.pack('<f', fsrc + fdst))[0]
        self.setOperValue(op, 1, res)

    def i_fsub(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        fdst = struct.unpack('<f', struct.pack('<I', dst & 0xFFFFFFFF))[0]
        res = struct.unpack('<I', struct.pack('<f', fdst - fsrc))[0]
        self.setOperValue(op, 1, res)

    def i_fmul(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        fdst = struct.unpack('<f', struct.pack('<I', dst & 0xFFFFFFFF))[0]
        res = struct.unpack('<I', struct.pack('<f', fsrc * fdst))[0]
        self.setOperValue(op, 1, res)

    def i_fdiv(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        fdst = struct.unpack('<f', struct.pack('<I', dst & 0xFFFFFFFF))[0]
        if fsrc == 0.0:
            res = 0
        else:
            res = struct.unpack('<I', struct.pack('<f', fdst / fsrc))[0]
        self.setOperValue(op, 1, res)

    def i_fsqrt(self, op):
        src = self.getOperValue(op, 0)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        import math
        if fsrc < 0:
            res = 0
        else:
            res = struct.unpack('<I', struct.pack('<f', math.sqrt(fsrc)))[0]
        self.setOperValue(op, 1, res)

    def i_fcmp(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        fdst = struct.unpack('<f', struct.pack('<I', dst & 0xFFFFFFFF))[0]
        self.setFlag(PSW_O, 0)
        if fdst > fsrc:
            self.setFlag(PSW_Z, 0)
            self.setFlag(PSW_S, 0)
        elif fdst < fsrc:
            self.setFlag(PSW_Z, 0)
            self.setFlag(PSW_S, 1)
        else:
            self.setFlag(PSW_Z, 1)
            self.setFlag(PSW_S, 0)

    def i_ftoi(self, op):
        src = self.getOperValue(op, 0)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        ival = int(fsrc)  # truncate toward zero
        res = e_bits.unsigned(ival, 4)
        self.setOperValue(op, 1, res)

    def i_ftou(self, op):
        src = self.getOperValue(op, 0)
        fsrc = struct.unpack('<f', struct.pack('<I', src & 0xFFFFFFFF))[0]
        ival = int(fsrc)  # truncate toward zero
        if ival < 0:
            ival = 0
        res = e_bits.unsigned(ival, 4)
        self.setOperValue(op, 1, res)