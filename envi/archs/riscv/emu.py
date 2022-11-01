from envi import *
from envi.archs.riscv.regs import *
from envi.archs.riscv.const import *
from envi.archs.riscv.disasm import *
from envi.archs.riscv.info import *

from envi.archs.riscv import RiscVModule


__all__ = [
    'RiscVCall',
    'RiscVAbstractEmulator',
    'RiscVEmulator',
]



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
        self.psize = self.xlen // 8
        super().__init__(archmod=archmod)
        self.setEndian(endian)
        self.addCallingConvention("riscvcall", RiscVCall)


class RiscVEmulator(RiscVRegisterContext, RiscVModule, RiscVAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_LSB, description=None):
        RiscVModule.__init__(self, endian=endian, description=description)
        RiscVAbstractEmulator.__init__(self, archmod=self, endian=endian, description=description)
        RiscVRegisterContext.__init__(self, description)

    """
    def i_lui(self, op):
    def i_auipc(self, op):
    def i_jal(self, op):
    def i_jalr(self, op):
    def i_beq(self, op):
    def i_bne(self, op):
    def i_blt(self, op):
    def i_bge(self, op):
    def i_bltu(self, op):
    def i_bgeu(self, op):
    def i_lb(self, op):
    def i_lh(self, op):
    def i_lw(self, op):
    def i_lbu(self, op):
    def i_lhu(self, op):
    def i_sb(self, op):
    def i_sh(self, op):
    def i_sw(self, op):
    def i_addi(self, op):
    def i_slti(self, op):
    def i_sltiu(self, op):
    def i_xori(self, op):
    def i_ori(self, op):
    def i_andi(self, op):
    def i_slli(self, op):
    def i_srli(self, op):
    def i_srai(self, op):
    def i_add(self, op):
    def i_sub(self, op):
    def i_sll(self, op):
    def i_slt(self, op):
    def i_sltu(self, op):
    def i_xor(self, op):
    def i_srl(self, op):
    def i_sra(self, op):
    def i_or(self, op):
    def i_and(self, op):
    def i_fence(self, op):
    def i_fence.tso(self, op):
    def i_pause(self, op):
    def i_ecall(self, op):
    def i_ebreak(self, op):
    def i_j(self, op):
    def i_jr(self, op):
    def i_sret(self, op):
    def i_mret(self, op):
    def i_mnret(self, op):
    def i_wfi(self, op):
    def i_sfence.vma(self, op):
    def i_hfence.vvma(self, op):
    def i_hfence.gvma(self, op):
    def i_hlv.b(self, op):
    def i_hlv.bu(self, op):
    def i_hlv.h(self, op):
    def i_hlv.hu(self, op):
    def i_hlv.w(self, op):
    def i_hlvx.hu(self, op):
    def i_hlvx.wu(self, op):
    def i_hsv.b(self, op):
    def i_hsv.h(self, op):
    def i_hsv.w(self, op):
    def i_hlv.wu(self, op):
    def i_hlv.d(self, op):
    def i_hsv.d(self, op):
    def i_sinval.vma(self, op):
    def i_sfence.w.inval(self, op):
    def i_sfence.inval.ir(self, op):
    def i_hinval.vvma(self, op):
    def i_hinval.gvma(self, op):
    def i_lwu(self, op):
    def i_ld(self, op):
    def i_sd(self, op):
    def i_addiw(self, op):
    def i_slliw(self, op):
    def i_srliw(self, op):
    def i_sraiw(self, op):
    def i_addw(self, op):
    def i_subw(self, op):
    def i_sllw(self, op):
    def i_srlw(self, op):
    def i_sraw(self, op):
    def i_fence.i(self, op):
    def i_csrrw(self, op):
    def i_csrrs(self, op):
    def i_csrrc(self, op):
    def i_csrrwi(self, op):
    def i_csrrsi(self, op):
    def i_csrrci(self, op):
    def i_mul(self, op):
    def i_mulh(self, op):
    def i_mulhsu(self, op):
    def i_mulhu(self, op):
    def i_div(self, op):
    def i_divu(self, op):
    def i_rem(self, op):
    def i_remu(self, op):
    def i_mulw(self, op):
    def i_divw(self, op):
    def i_divuw(self, op):
    def i_remw(self, op):
    def i_remuw(self, op):
    def i_lr.w.aq(self, op):
    def i_lr.w.rl(self, op):
    def i_lr.w.aq.rl(self, op):
    def i_lr.w(self, op):
    def i_sc.w.aq(self, op):
    def i_sc.w.rl(self, op):
    def i_sc.w.aq.rl(self, op):
    def i_sc.w(self, op):
    def i_amoswap.w.aq(self, op):
    def i_amoswap.w.rl(self, op):
    def i_amoswap.w.aq.rl(self, op):
    def i_amoswap.w(self, op):
    def i_amoadd.w.aq(self, op):
    def i_amoadd.w.rl(self, op):
    def i_amoadd.w.aq.rl(self, op):
    def i_amoadd.w(self, op):
    def i_amoxor.w.aq(self, op):
    def i_amoxor.w.rl(self, op):
    def i_amoxor.w.aq.rl(self, op):
    def i_amoxor.w(self, op):
    def i_amoand.w.aq(self, op):
    def i_amoand.w.rl(self, op):
    def i_amoand.w.aq.rl(self, op):
    def i_amoand.w(self, op):
    def i_amoor.w.aq(self, op):
    def i_amoor.w.rl(self, op):
    def i_amoor.w.aq.rl(self, op):
    def i_amoor.w(self, op):
    def i_amomin.w.aq(self, op):
    def i_amomin.w.rl(self, op):
    def i_amomin.w.aq.rl(self, op):
    def i_amomin.w(self, op):
    def i_amomax.w.aq(self, op):
    def i_amomax.w.rl(self, op):
    def i_amomax.w.aq.rl(self, op):
    def i_amomax.w(self, op):
    def i_amominu.w.aq(self, op):
    def i_amominu.w.rl(self, op):
    def i_amominu.w.aq.rl(self, op):
    def i_amominu.w(self, op):
    def i_amomaxu.w.aq(self, op):
    def i_amomaxu.w.rl(self, op):
    def i_amomaxu.w.aq.rl(self, op):
    def i_amomaxu.w(self, op):
    def i_lr.d.aq(self, op):
    def i_lr.d.rl(self, op):
    def i_lr.d.aq.rl(self, op):
    def i_lr.d(self, op):
    def i_sc.d.aq(self, op):
    def i_sc.d.rl(self, op):
    def i_sc.d.aq.rl(self, op):
    def i_sc.d(self, op):
    def i_amoswap.d.aq(self, op):
    def i_amoswap.d.rl(self, op):
    def i_amoswap.d.aq.rl(self, op):
    def i_amoswap.d(self, op):
    def i_amoadd.d.aq(self, op):
    def i_amoadd.d.rl(self, op):
    def i_amoadd.d.aq.rl(self, op):
    def i_amoadd.d(self, op):
    def i_amoxor.d.aq(self, op):
    def i_amoxor.d.rl(self, op):
    def i_amoxor.d.aq.rl(self, op):
    def i_amoxor.d(self, op):
    def i_amoand.d.aq(self, op):
    def i_amoand.d.rl(self, op):
    def i_amoand.d.aq.rl(self, op):
    def i_amoand.d(self, op):
    def i_amoor.d.aq(self, op):
    def i_amoor.d.rl(self, op):
    def i_amoor.d.aq.rl(self, op):
    def i_amoor.d(self, op):
    def i_amomin.d.aq(self, op):
    def i_amomin.d.rl(self, op):
    def i_amomin.d.aq.rl(self, op):
    def i_amomin.d(self, op):
    def i_amomax.d.aq(self, op):
    def i_amomax.d.rl(self, op):
    def i_amomax.d.aq.rl(self, op):
    def i_amomax.d(self, op):
    def i_amominu.d.aq(self, op):
    def i_amominu.d.rl(self, op):
    def i_amominu.d.aq.rl(self, op):
    def i_amominu.d(self, op):
    def i_amomaxu.d.aq(self, op):
    def i_amomaxu.d.rl(self, op):
    def i_amomaxu.d.aq.rl(self, op):
    def i_amomaxu.d(self, op):
    def i_flw(self, op):
    def i_fsw(self, op):
    def i_fmadd.s(self, op):
    def i_fmsub.s(self, op):
    def i_fnmsub.s(self, op):
    def i_fnmadd.s(self, op):
    def i_fadd.s(self, op):
    def i_fsub.s(self, op):
    def i_fmul.s(self, op):
    def i_fdiv.s(self, op):
    def i_fsqrt.s(self, op):
    def i_fsgnj.s(self, op):
    def i_fsgnjn.s(self, op):
    def i_fsgnjx.s(self, op):
    def i_fmin.s(self, op):
    def i_fmax.s(self, op):
    def i_fcvt.w.s(self, op):
    def i_fcvt.wu.s(self, op):
    def i_fmv.x.w(self, op):
    def i_feq.s(self, op):
    def i_flt.s(self, op):
    def i_fle.s(self, op):
    def i_fclass.s(self, op):
    def i_fcvt.s.w(self, op):
    def i_fcvt.s.wu(self, op):
    def i_fmv.w.x(self, op):
    def i_fcvt.l.s(self, op):
    def i_fcvt.lu.s(self, op):
    def i_fcvt.s.l(self, op):
    def i_fcvt.s.lu(self, op):
    def i_fld(self, op):
    def i_fsd(self, op):
    def i_fmadd.d(self, op):
    def i_fmsub.d(self, op):
    def i_fnmsub.d(self, op):
    def i_fnmadd.d(self, op):
    def i_fadd.d(self, op):
    def i_fsub.d(self, op):
    def i_fmul.d(self, op):
    def i_fdiv.d(self, op):
    def i_fsqrt.d(self, op):
    def i_fsgnj.d(self, op):
    def i_fsgnjn.d(self, op):
    def i_fsgnjx.d(self, op):
    def i_fmin.d(self, op):
    def i_fmax.d(self, op):
    def i_fcvt.s.d(self, op):
    def i_fcvt.d.s(self, op):
    def i_feq.d(self, op):
    def i_flt.d(self, op):
    def i_fle.d(self, op):
    def i_fclass.d(self, op):
    def i_fcvt.w.d(self, op):
    def i_fcvt.wu.d(self, op):
    def i_fcvt.d.w(self, op):
    def i_fcvt.d.wu(self, op):
    def i_fcvt.l.d(self, op):
    def i_fcvt.lu.d(self, op):
    def i_fmv.x.d(self, op):
    def i_fcvt.d.l(self, op):
    def i_fcvt.d.lu(self, op):
    def i_fmv.d.x(self, op):
    def i_flq(self, op):
    def i_fsq(self, op):
    def i_fmadd.q(self, op):
    def i_fmsub.q(self, op):
    def i_fnmsub.q(self, op):
    def i_fnmadd.q(self, op):
    def i_fadd.q(self, op):
    def i_fsub.q(self, op):
    def i_fmul.q(self, op):
    def i_fdiv.q(self, op):
    def i_fsqrt.q(self, op):
    def i_fsgnj.q(self, op):
    def i_fsgnjn.q(self, op):
    def i_fsgnjx.q(self, op):
    def i_fmin.q(self, op):
    def i_fmax.q(self, op):
    def i_fcvt.s.q(self, op):
    def i_fcvt.q.s(self, op):
    def i_fcvt.d.q(self, op):
    def i_fcvt.q.d(self, op):
    def i_feq.q(self, op):
    def i_flt.q(self, op):
    def i_fle.q(self, op):
    def i_fclass.q(self, op):
    def i_fcvt.w.q(self, op):
    def i_fcvt.wu.q(self, op):
    def i_fcvt.q.w(self, op):
    def i_fcvt.q.wu(self, op):
    def i_fcvt.l.q(self, op):
    def i_fcvt.lu.q(self, op):
    def i_fcvt.q.l(self, op):
    def i_fcvt.q.lu(self, op):
    def i_flh(self, op):
    def i_fsh(self, op):
    def i_fmadd.h(self, op):
    def i_fmsub.h(self, op):
    def i_fnmsub.h(self, op):
    def i_fnmadd.h(self, op):
    def i_fadd.h(self, op):
    def i_fsub.h(self, op):
    def i_fmul.h(self, op):
    def i_fdiv.h(self, op):
    def i_fsqrt.h(self, op):
    def i_fsgnj.h(self, op):
    def i_fsgnjn.h(self, op):
    def i_fsgnjx.h(self, op):
    def i_fmin.h(self, op):
    def i_fmax.h(self, op):
    def i_fcvt.s.h(self, op):
    def i_fcvt.h.s(self, op):
    def i_fcvt.d.h(self, op):
    def i_fcvt.h.d(self, op):
    def i_fcvt.q.h(self, op):
    def i_fcvt.h.q(self, op):
    def i_feq.h(self, op):
    def i_flt.h(self, op):
    def i_fle.h(self, op):
    def i_fclass.h(self, op):
    def i_fcvt.w.h(self, op):
    def i_fcvt.wu.h(self, op):
    def i_fmv.x.h(self, op):
    def i_fcvt.h.w(self, op):
    def i_fcvt.h.wu(self, op):
    def i_fmv.h.x(self, op):
    def i_fcvt.l.h(self, op):
    def i_fcvt.lu.h(self, op):
    def i_fcvt.h.l(self, op):
    def i_fcvt.h.lu(self, op):
    def i_addi4spn(self, op):
    def i_fld(self, op):
    def i_lw(self, op):
    def i_flw(self, op):
    def i_fsd(self, op):
    def i_sw(self, op):
    def i_fsw(self, op):
    def i_nop(self, op):
    def i_addi(self, op):
    def i_jal(self, op):
    def i_li(self, op):
    def i_addi16sp(self, op):
    def i_lui(self, op):
    def i_srli(self, op):
    def i_srai(self, op):
    def i_andi(self, op):
    def i_sub(self, op):
    def i_xor(self, op):
    def i_or(self, op):
    def i_and(self, op):
    def i_subw(self, op):
    def i_addw(self, op):
    def i_j(self, op):
    def i_beqz(self, op):
    def i_bnez(self, op):
    def i_slli(self, op):
    def i_fldsp(self, op):
    def i_lwsp(self, op):
    def i_flwsp(self, op):
    def i_jr(self, op):
    def i_mv(self, op):
    def i_ebreak(self, op):
    def i_jalr(self, op):
    def i_add(self, op):
    def i_fsdsp(self, op):
    def i_swsp(self, op):
    def i_fswsp(self, op):
    def i_ld(self, op):
    def i_sd(self, op):
    def i_addiw(self, op):
    def i_ldsp(self, op):
    def i_sdsp(self, op):
    def i_lq(self, op):
    def i_sq(self, op):
    def i_lqsp(self, op):
    def i_sqsp(self, op):
    def i_(self, op):
    """
