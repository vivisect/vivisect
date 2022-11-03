import math

from envi import *
from envi.archs.riscv.regs import *
from envi.archs.riscv.const import *
from envi.archs.riscv.disasm import *
from envi.archs.riscv.info import *

from envi.archs.riscv import RiscVModule

import logging
logger = logging.getLogger(__name__)


__all__ = [
    'RiscVCall',
    'RiscVAbstractEmulator',
    'RiscVEmulator',
]


class TrapException(envi.EnviException):
    def __init__(self, op):
        self.op = op
        super().__init__('Trap: %s' % op)


class AddressMisaligned(envi.InvalidAddress):
    def __init__(self, va):
        self.va = va
        super.__init__('Address Misaligned: 0x%x' % va)



class RiscVCall(envi.CallingConvention):
    '''
    RiscV Calling Convention.
    '''
    arg_def = [
        (CC_REG, REG_A0),
        (CC_REG, REG_A1),
        (CC_REG, REG_A2),
        (CC_REG, REG_A3),
        (CC_REG, REG_A4),
        (CC_REG, REG_A5),
        (CC_REG, REG_A6),
        (CC_REG, REG_A7),
    ]
    arg_def.append((CC_STACK_INF, 8))
    retaddr_def = (CC_REG, REG_RA)
    retval_def = [
        (CC_REG, REG_A0), (CC_REG, REG_A1)
    ]
    flags = CC_CALLEE_CLEANUP
    align = 16
    pad = 0


class RiscVAbstractEmulator(envi.Emulator):
    def __init__(self, archmod=None, endian=ENDIAN_LSB, description=None):
        if description is None:
            self.description = DEFAULT_RISCV_DESCR
        else:
            self.description = description
        self.xlen = getRiscVXLEN(self.description)
        self.ialign = getRiscVIALIGN(self.description)
        self.psize = self.xlen // 8
        super().__init__(archmod=archmod)
        self.setEndian(endian)
        self.addCallingConvention("riscvcall", RiscVCall)

    def populateOpMethods(self):
        # The instruction list is a sequential integer enumeration so the list
        # of emulation functions can be a list
        methods = [None] * len(RISCV_INS)

        # There should be an emulation function for each instruction
        for ins in RISCV_INS:
            method_name = 'i_%s' % ins.name.lower()
            try:
                methods[ins] = getattr(self, method_name)
            except AttributeError:
                logger.debug('missing emulation function %s for %s', method_name, ins)

        self.op_methods = tuple(methods)

    def executeOpcode(self, op):
        if not op.iflags & RISCV_IF.HINT:
            # If this op is a hint, don't execute it just move to the next
            # instruction
            logger.info('skipping HINT instruction %s', op)
            x = None
        else:
            meth = self.op_methods.get(op.opcode)
            if meth == None:
                raise envi.UnsupportedInstruction(self, op)
            x = meth(op)

        if x != None:
            self.setProgramCounter(x)
        else:
            pc = self.getProgramCounter()
            pc += op.size
            self.setProgramCounter(pc)

    # Instructions

    def i_nop(self, op):
        pass

    def i_auipc(self, op):
        self.setOperValue(op, 0, self.getProgramCounter() + self.getOperValue(op, 1))

    def i_li(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def i_c_mv(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def i_add(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) + self.getOperValue(op, 2))

    def i_c_add(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) + self.getOperValue(op, 1))

    def i_c_addi16sp(self, op):
        self.setRegister(REG_SP, self.getRegister(REG_SP) + self.getOperValue(op, 1))

    def i_c_addi4spn(self, op):
        self.setOperValue(op, 0, self.getRegister(REG_SP) + self.getOperValue(op, 1))

    def i_and(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) & self.getOperValue(op, 2))

    def i_c_and(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) & self.getOperValue(op, 1))

    def i_or(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) | self.getOperValue(op, 2))

    def i_c_or(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) | self.getOperValue(op, 1))

    def i_xor(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) ^ self.getOperValue(op, 2))

    def i_c_xor(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) ^ self.getOperValue(op, 1))

    def i_sl(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) ^ self.getOperValue(op, 2))

    def i_c_sl(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) ^ self.getOperValue(op, 1))

    def i_sr(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) ^ self.getOperValue(op, 2))

    def i_c_sr(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) ^ self.getOperValue(op, 1))

    def i_sub(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) - self.getOperValue(op, 2))

    def i_c_sub(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 0) - self.getOperValue(op, 1))

    def i_mul(self, op):
        # Store the lower XLEN-bits of the result (automatic based on register
        # operands)
        self.setOperValue(op, 0, self.getOperValue(op, 1) * self.getOperValue(op, 2))

    def i_mulh(self, op):
        # Store the upper XLEN-bits of the result
        result = self.getOperValue(op, 1) * self.getOperValue(op, 2)
        self.setOperValue(op, 0, result >> self.xlen)

    def i_div(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) // self.getOperValue(op, 2))

    def i_rem(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) % self.getOperValue(op, 2))

    def i_slt(self, op):
        if self.getOperValue(op, 0) < self.getOperValue(op, 1):
            self.setOperValue(op, 0, 1)
        else:
            self.setOperValue(op, 0, 0)

    def i_csrrw(self, op):
        if op.opers[0].reg == REG_ZERO:
            # Do nothing if the destination is X0
            return

        # CSR is the second param (oper 1)
        self.setOperValue(op, 0, self.getOperValue(op, 1))
        self.setOperValue(op, 1, self.getOperValue(op, 2))

    def i_csrrc(self, op):
        if op.opers[0].reg == REG_ZERO:
            # Do nothing if the destination is X0
            return

        # CSR is the second param (oper 1)
        value = self.getOperValue(op, 1)
        self.setOperValue(op, 0, value)

        # Clear the bits that are set in rs2
        mask = self.getOperValue(op, 2)
        self.setOperValue(op, 1, value & ~mask)

    def i_csrrs(self, op):
        if op.opers[0].reg == REG_ZERO:
            # Do nothing if the destination is X0
            return

        # CSR is the second param (oper 1)
        value = self.getOperValue(op, 1)
        self.setOperValue(op, 0, value)

        # set the bits that are set in rs2
        mask = self.getOperValue(op, 2)
        self.setOperValue(op, 1, value | mask)

    def i_load(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def i_store(self, op):
        self.setOperValue(op, 1, self.getOperValue(op, 0))

    def i_fmv(self, op):
        # Move the raw integer values from source to destination
        op.opers[0].setRaw(op, self, op.opers[1].getRaw(op, self))

    def i_fcvt(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def i_fsgnj(self, op):
        rs1_abs = op.opers[1].getAbs(op, self)
        rs2_sign = op.opers[2].getSign(op, self)
        op.opers[0].setRaw(op, self, rs2_sign | rs1_abs)

    def i_fsgnjn(self, op):
        rs1_abs = op.opers[1].getAbs(op, self)
        rs2_neg_sign = op.opers[2].getNegSign(op, self)
        op.opers[0].setRaw(op, self, rs2_sign | rs1_abs)

    def i_fsgnjx(self, op):
        rs1_abs = op.opers[1].getAbs(op, self)
        rs1_sign = op.opers[1].getSign(op, self)
        rs2_sign = op.opers[2].getSign(op, self)
        op.opers[0].setRaw(op, self, (rs1_sign ^ rs2_sign) | rs1_abs)

    def i_fadd(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) + self.getOperValue(op, 2))

    def i_fsub(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) - self.getOperValue(op, 2))

    def i_fmax(self, op):
        self.setOperValue(op, 0, max(self.getOperValue(op, 1), self.getOperValue(op, 2)))

    def i_fmin(self, op):
        self.setOperValue(op, 0, min(self.getOperValue(op, 1), self.getOperValue(op, 2)))

    def i_fmul(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) * self.getOperValue(op, 2))

    def i_fdiv(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) / self.getOperValue(op, 2))

    def i_fmadd(self, op):
        product = self.getOperValue(op, 1) * self.getOperValue(op, 2)
        self.setOperValue(op, 0, product + self.getOperValue(op, 3))

    def i_fnmadd(self, op):
        product = -(self.getOperValue(op, 1) * self.getOperValue(op, 2))
        self.setOperValue(op, 0, product - self.getOperValue(op, 3))

    def i_fmsub(self, op):
        product = self.getOperValue(op, 1) * self.getOperValue(op, 2)
        self.setOperValue(op, 0, product - self.getOperValue(op, 3))

    def i_fnmsub(self, op):
        product = -(self.getOperValue(op, 1) * self.getOperValue(op, 2))
        self.setOperValue(op, 0, product + self.getOperValue(op, 3))

    def i_fsqrt(self, op):
        self.setOperValue(op, 0, math.sqrt(self.getOperValue(op, 1)))

    def i_fclass(self, op):
        src = op.opers[1]
        if src.isInf(op, self):
            if src.isNeg(op, self):
                self.setOperValue(op, 0, 0)
            else:
                self.setOperValue(op, 0, 7)
        elif src.isZero(op, self):
            if src.isNeg(op, self):
                self.setOperValue(op, 0, 3)
            else:
                self.setOperValue(op, 0, 4)
        elif src.isSNaN(op, self):
            self.setOperValue(op, 0, 8)
        elif src.isQNaN(op, self):
            self.setOperValue(op, 0, 9)
        elif src.isSubnormal():
            if src.isNeg(op, self):
                self.setOperValue(op, 0, 2)
            else:
                self.setOperValue(op, 0, 5)
        else:
            # Normal number
            if src.isNeg(op, self):
                self.setOperValue(op, 0, 1)
            else:
                self.setOperValue(op, 0, 6)

    def i_feq(self, op):
        self.setOperValue(op, 0, bool(self.getOperValue(op, 1) == self.getOperValue(op, 2)))

    def i_fle(self, op):
        self.setOperValue(op, 0, bool(self.getOperValue(op, 1) <= self.getOperValue(op, 2)))

    def i_flt(self, op):
        self.setOperValue(op, 0, bool(self.getOperValue(op, 1) < self.getOperValue(op, 2)))

    def i_j(self, op):
        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_jr(self, op):
        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_jal(self, op):
        self.setOperValue(op, 1, self.getProgramCounter() + op.size)

        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_jalr(self, op):
        self.setOperValue(op, 1, self.getProgramCounter() + op.size)

        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_c_j(self, op):
        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_c_jr(self, op):
        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_c_jal(self, op):
        self.setRegister(REG_RA, self.getProgramCounter() + op.size)

        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_c_jalr(self, op):
        self.setRegister(REG_RA, self.getProgramCounter() + op.size)

        addr = self.getOperValue(op, 0)
        if addr % self.ialign != 0:
            raise AddressMisaligned(addr)
        return addr

    def i_beq(self, op):
        if self.getOperValue(op, 0) == self.getOperValue(op, 1):
            addr = self.getOperValue(op, 2)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_bne(self, op):
        if self.getOperValue(op, 0) != self.getOperValue(op, 1):
            addr = self.getOperValue(op, 2)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_bge(self, op):
        if self.getOperValue(op, 0) >= self.getOperValue(op, 1):
            addr = self.getOperValue(op, 2)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_blt(self, op):
        if self.getOperValue(op, 0) < self.getOperValue(op, 1):
            addr = self.getOperValue(op, 2)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_c_beqz(self, op):
        if self.getOperValue(op, 0) == 0:
            addr = self.getOperValue(op, 1)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_c_bnez(self, op):
        if self.getOperValue(op, 0) != 0:
            addr = self.getOperValue(op, 1)
            if addr % self.ialign != 0:
                raise AddressMisaligned(addr)
            return addr

    def i_fence(self, op):
        pass

    def i_fence_i(self, op):
        pass

    def i_fence_tso(self, op):
        pass

    def i_hfence_gvma(self, op):
        pass

    def i_hfence_vvma(self, op):
        pass

    def i_hinval_gvma(self, op):
        pass

    def i_hinval_vvma(self, op):
        pass

    def i_sfence_inval_ir(self, op):
        pass

    def i_sfence_vma(self, op):
        pass

    def i_sfence_w_inval(self, op):
        pass

    def i_sinval_vma(self, op):
        pass

    def i_pause(self, op):
        pass

    def i_mnret(self, op):
        # MNRET is an M-mode-only instruction that uses the values in mnepc and
        # mnstatus to return to the program counter, privilege mode, and
        # virtualization mode of the interrupted context. This instruction also
        # sets mnstatus.NMIE
        raise envi.ArchNotImplemented()

    def i_mret(self, op):
        raise TrapException(op)

    def i_sret(self, op):
        raise TrapException(op)

    def i_wfi(self, op):
        raise TrapException(op)

    def i_ecall(self, op):
        raise TrapException(op)

    def i_ebreak(self, op):
        raise envi.BreakpointHit()

    # AMO operations do:
    #   - load value from rs1 (operand 2)
    #   - place that into rd (operand 0)
    #   - Apply an operation on the value in the memory address referenced by
    #     rs1 using rs2
    #
    # For the purposes of emulation we will assume the "lock" is always properly
    # acquired and released.

    def i_amoadd(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, value + self.getOperValue(op, 1))

    def i_amoand(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, value & self.getOperValue(op, 1))

    def i_amoor(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, value | self.getOperValue(op, 1))

    def i_amoxor(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, value ^ self.getOperValue(op, 1))

    def i_amomax(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, max(value, self.getOperValue(op, 1)))

    def i_amomin(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, min(value, self.getOperValue(op, 1)))

    def i_amoswap(self, op):
        value = self.getOperValue(op, 2)
        self.setOperValue(op, 0, value)
        self.setOperValue(op, 2, self.getOperValue(op, 1))

    def i_lr(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def i_sc(self, op):
        # If SC succeeds, 0 is written to rd, if it fails 1 is written to rd.
        # For the purposes of emulation we always succeed
        self.setOperValue(op, 2, self.getOperValue(op, 1))
        self.setOperValue(op, 0, 0)


class RiscVEmulator(RiscVRegisterContext, RiscVModule, RiscVAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_LSB, description=None):
        RiscVModule.__init__(self, endian=endian, description=description)
        RiscVAbstractEmulator.__init__(self, archmod=self, endian=endian, description=description)
        RiscVRegisterContext.__init__(self, description)
