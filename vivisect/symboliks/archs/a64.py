"""
AArch64 Symbolik Translator

This module provides symbolic translation for AArch64 (ARM64) instructions.
It converts AArch64 opcodes into symbolic effects that can be analyzed by
the Vivisect symboliks framework.
"""

import envi
import envi.bits as e_bits
import envi.archs.aarch64 as e_aarch64
import envi.archs.aarch64.disasm as e_a64_disasm
import envi.archs.aarch64.regs as e_a64_regs
import envi.archs.aarch64.const as e_a64_const

import vivisect.symboliks.analysis as vsym_analysis
import vivisect.symboliks.callconv as vsym_callconv
import vivisect.symboliks.translator as vsym_trans

from vivisect.const import *
from vivisect.symboliks.common import *


class A64SymbolikTranslator(vsym_trans.SymbolikTranslator):
    """
    Symbolik translator for AArch64 (ARM64) architecture.

    This translator converts AArch64 opcodes into symbolic effects that can
    be used for symbolic execution and analysis.
    """

    def __init__(self, vw):
        vsym_trans.SymbolikTranslator.__init__(self, vw)
        self._arch = e_aarch64.A64Module()
        self._psize = self._arch.getPointerSize()  # 8 bytes for AArch64
        self._reg_ctx = self._arch.archGetRegCtx()

        # Pre-compute size masks for common sizes
        self._sz_masks = {}
        for i in (0, 1, 2, 4, 8, 16, 32):
            self._sz_masks[i] = Const((2 ** (i * 8)) - 1, self._psize)
        
        # Add mappings for conditional branch mnemonics (b.eq, b.ne, etc.)
        # These have dots in their names which can't be Python method names
        cond_branches = [
            'b.eq', 'b.ne', 'b.cs', 'b.hs', 'b.cc', 'b.lo',
            'b.mi', 'b.pl', 'b.vs', 'b.vc', 'b.hi', 'b.ls',
            'b.ge', 'b.lt', 'b.gt', 'b.le', 'b.al', 'b.nv'
        ]
        for mnem in cond_branches:
            method_name = 'i_' + mnem.replace('.', '_')
            if hasattr(self, method_name):
                self._op_methods[mnem] = getattr(self, method_name)

    def getRegObj(self, regidx):
        """
        Get a symbolic object representing the value of a register.

        Handles meta-register translation (e.g., w0 -> x0 lower 32 bits).
        """
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth >> 3)

        # Handle meta registers (w0, h0, b0, etc.)
        if ridx != regidx:
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            metawidth = e_bits.u_maxes.index(mask)
            if lshift != 0:
                val = o_rshift(val, Const(lshift, metawidth), metawidth)
            val = o_and(val, Const(mask, metawidth), metawidth)

        return val

    def setRegObj(self, regidx, obj):
        """
        Set a register to a symbolic value.

        For 32-bit register writes (w registers), the upper 32 bits of the
        64-bit register are zeroed (per AArch64 specification).
        """
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth >> 3)

        # Handle meta registers
        if ridx != regidx:
            # Check if this is a 32-bit write (w register)
            # In AArch64, writing to a 32-bit register zeros the upper 32 bits
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)

            if mask == 0xffffffff and lshift == 0:
                # 32-bit write: zero-extends to 64 bits
                # Just write the value as the full register
                pass
            else:
                # Other meta registers: preserve other bits
                basemask = (2 ** rbitwidth) - 1
                finalmask = basemask ^ (mask << lshift)
                if lshift != 0:
                    obj <<= Const(lshift, rbitwidth >> 3)
                obj = obj | (val & Const(finalmask, rbitwidth >> 3))

        self.effSetVariable(rname, obj)

    def getRegByName(self, name):
        """Get a register's symbolic value by name."""
        regidx = self._reg_ctx.getRegisterIndex(name)
        return self.getRegObj(regidx)

    def setRegByName(self, name, obj):
        """Set a register's symbolic value by name."""
        regidx = self._reg_ctx.getRegisterIndex(name)
        self.setRegObj(regidx, obj)

    def getOperAddrObj(self, op, idx):
        """
        Get the symbolic address for a memory operand.

        Handles various AArch64 addressing modes:
        - [Xn, #imm]  - Register + immediate
        - [Xn, Xm]    - Register + register
        - [Xn, Xm, extend] - Register + extended register
        """
        oper = op.opers[idx]

        if isinstance(oper, e_a64_disasm.A64RegImmOffOper):
            # [Xn, #simm]
            basereg = oper.basereg
            base = Var(self._reg_ctx.getRegisterName(basereg), self._psize)
            if oper.simm != 0:
                base = o_add(base, Const(oper.simm, self._psize), self._psize)
            return base

        elif isinstance(oper, e_a64_disasm.A64RegRegOffOper):
            # [Xn, Xm{, extend {amount}}]
            basereg = oper.basereg
            base = Var(self._reg_ctx.getRegisterName(basereg), self._psize)

            offreg = oper.offreg
            offrname = self._reg_ctx.getRegisterName(offreg)
            offset = Var(offrname, self._psize)

            # Handle extension/shift
            if oper.extamt != 0:
                offset = o_lshift(offset, Const(oper.extamt, self._psize), self._psize)

            return o_add(base, offset, self._psize)

        elif isinstance(oper, e_a64_disasm.A64SveMemOper):
            # SVE memory operand
            base = Var(self._reg_ctx.getRegisterName(oper.basereg), self._psize)
            if hasattr(oper, 'offset') and oper.offset != 0:
                base = o_add(base, Const(oper.offset, self._psize), self._psize)
            return base

        raise Exception('Unknown operand type for getOperAddrObj: %s' % oper.__class__.__name__)

    def getOperObj(self, op, idx):
        """
        Get the symbolic value of an operand.

        Handles:
        - Register operands
        - Immediate operands
        - Memory (dereference) operands
        """
        oper = op.opers[idx]

        if oper.isReg():
            # Check for zero register (xzr/wzr)
            if isinstance(oper, e_a64_disasm.A64RegWithZROper):
                if (oper.reg & 0xffff) == e_a64_regs.REG_XZR:
                    return Const(0, oper.tsize)
            return self.getRegObj(oper.reg)

        elif oper.isDeref():
            addrsym = self.getOperAddrObj(op, idx)
            return self.effReadMemory(addrsym, Const(oper.tsize, self._psize))

        elif oper.isImmed():
            ret = oper.getOperValue(op, self)
            return Const(ret, self._psize)

        elif isinstance(oper, e_a64_disasm.A64BranchOper):
            # Branch target
            return Const(oper.getOperValue(op), self._psize)

        elif isinstance(oper, e_a64_disasm.A64RegExtOper):
            # Register with extension
            val = self.getRegObj(oper.reg)
            if oper.shift != 0:
                val = o_lshift(val, Const(oper.shift, self._psize), self._psize)
            return val

        elif isinstance(oper, e_a64_disasm.A64ShiftOper):
            # Shift operand - this is a register with optional shift
            # The register is stored in oper.reg
            val = self.getRegObj(oper.reg)
            # Apply shift if present
            if hasattr(oper, 'shval') and oper.shval != 0:
                shtype = oper.shtype if hasattr(oper, 'shtype') else e_a64_const.S_LSL
                shamt = Const(oper.shval, self._psize)
                if shtype == e_a64_const.S_LSL:
                    val = o_lshift(val, shamt, val.getWidth())
                elif shtype == e_a64_const.S_LSR:
                    val = o_rshift(val, shamt, val.getWidth())
                elif shtype == e_a64_const.S_ASR:
                    # Arithmetic shift right
                    val = o_rshift(val, shamt, val.getWidth())
                elif shtype == e_a64_const.S_ROR:
                    # Rotate right
                    bitwidth = val.getWidth() * 8
                    val = o_or(
                        o_rshift(val, shamt, val.getWidth()),
                        o_lshift(val, o_sub(Const(bitwidth, self._psize), shamt, self._psize), val.getWidth()),
                        val.getWidth()
                    )
            return val

        elif isinstance(oper, e_a64_disasm.A64CondOper):
            # Condition operand (for conditional instructions)
            return Const(oper.val, self._psize)

        raise Exception('Unknown operand class: %s' % oper.__class__.__name__)

    def setOperObj(self, op, idx, obj):
        """
        Set the operand to a symbolic value.
        """
        oper = op.opers[idx]

        if oper.isReg():
            # Check for zero register - writes are discarded
            if isinstance(oper, e_a64_disasm.A64RegWithZROper):
                if (oper.reg & 0xffff) == e_a64_regs.REG_XZR:
                    return  # Writes to zero register are discarded
            self.setRegObj(oper.reg, obj)
            return

        if oper.isDeref():
            addrsym = self.getOperAddrObj(op, idx)
            return self.effWriteMemory(addrsym, Const(oper.tsize, self._psize), obj)

        raise Exception('setOperObj failed for: %s' % oper.__class__.__name__)

    def _getOperSize(self, op, idx):
        """Get the size of an operand in bytes."""
        return op.opers[idx].tsize

    # ==========================================================================
    # Condition Flag Helpers
    # ==========================================================================
    #
    # AArch64 uses PSTATE flags (N, Z, C, V) which are set by flag-setting
    # instructions (ADDS, SUBS, ANDS, etc.) via effSetVariable().
    # 
    # Conditional branches then reference these flags via effConstrain()
    # (called automatically by translateOpcode() when i_* methods return
    # constraint tuples).
    #
    # The flow is:
    # 1. CMP/SUBS/etc. sets pstate_n, pstate_z, pstate_c, pstate_v via effSetVariable()
    # 2. B.EQ/B.NE/etc. returns constraint tuples referencing these flags
    # 3. translateOpcode() calls effConstrain() for each constraint tuple
    # ==========================================================================

    def _set_add_flags(self, v1, v2, result, dsize):
        """
        Set PSTATE flags for ADD operations using effSetVariable().
        
        These flags can later be referenced by conditional branches which
        will call effConstrain() via their return value.
        """
        zero = Const(0, self._psize)
        smax = e_bits.s_maxes[dsize]

        self.effSetVariable('pstate_n', lt(result, zero))
        self.effSetVariable('pstate_z', eq(result, zero))
        # Carry: unsigned overflow
        self.effSetVariable('pstate_c', gt(o_add(v1, v2, dsize * 2), Const(e_bits.u_maxes[dsize], self._psize)))
        # Overflow: signed overflow
        self.effSetVariable('pstate_v', gt(result, Const(smax, self._psize)))

    def _set_sub_flags(self, v1, v2, result, dsize):
        """
        Set PSTATE flags for SUB/CMP operations using effSetVariable().
        
        These flags can later be referenced by conditional branches which
        will call effConstrain() via their return value.
        """
        zero = Const(0, self._psize)

        self.effSetVariable('pstate_n', lt(result, zero))
        self.effSetVariable('pstate_z', eq(result, zero))
        # Carry: borrow (v1 >= v2)
        self.effSetVariable('pstate_c', ge(v1, v2))
        # Overflow
        self.effSetVariable('pstate_v', ne(
            lt(v1, v2),
            lt(result, zero)
        ))

    def _set_logic_flags(self, result, dsize):
        """
        Set PSTATE flags for logical operations using effSetVariable().
        
        Logical operations (AND, ORR, EOR, etc.) clear C and V flags.
        """
        zero = Const(0, self._psize)
        self.effSetVariable('pstate_n', lt(result, zero))
        self.effSetVariable('pstate_z', eq(result, zero))
        self.effSetVariable('pstate_c', Const(0, self._psize))
        self.effSetVariable('pstate_v', Const(0, self._psize))

    def _cond_check(self, cond):
        """
        Return a symbolic constraint based on the AArch64 condition code.
        
        These constraints are used by conditional branch instructions.
        When returned from an i_* method, the base class translateOpcode()
        will call effConstrain() for each (address, constraint) tuple to
        register the path constraints.
        
        AArch64 condition codes and their flag checks:
        - EQ: Z == 1 (equal)
        - NE: Z == 0 (not equal)  
        - CS/HS: C == 1 (carry set / unsigned higher or same)
        - CC/LO: C == 0 (carry clear / unsigned lower)
        - MI: N == 1 (minus / negative)
        - PL: N == 0 (plus / positive or zero)
        - VS: V == 1 (overflow set)
        - VC: V == 0 (overflow clear)
        - HI: C == 1 AND Z == 0 (unsigned higher)
        - LS: C == 0 OR Z == 1 (unsigned lower or same)
        - GE: N == V (signed greater or equal)
        - LT: N != V (signed less than)
        - GT: Z == 0 AND N == V (signed greater than)
        - LE: Z == 1 OR N != V (signed less or equal)
        - AL: always
        """
        # Reference the PSTATE flag variables
        # These are set by flag-setting instructions via effSetVariable()
        n = Var('pstate_n', self._psize)
        z = Var('pstate_z', self._psize)
        c = Var('pstate_c', self._psize)
        v = Var('pstate_v', self._psize)

        # Simple flag checks - use the flag variable directly or cnot()
        # This matches the i386 pattern of using Var('eflags_eq') directly
        if cond == e_a64_const.COND_EQ:
            return z  # Z flag set (pstate_z is a constraint that's true when Z=1)
        elif cond == e_a64_const.COND_NE:
            return cnot(z)  # Z flag clear
        elif cond == e_a64_const.COND_CS:  # HS (carry set)
            return c  # C flag set
        elif cond == e_a64_const.COND_CC:  # LO (carry clear)
            return cnot(c)  # C flag clear
        elif cond == e_a64_const.COND_MI:  # Negative
            return n  # N flag set
        elif cond == e_a64_const.COND_PL:  # Positive or zero
            return cnot(n)  # N flag clear
        elif cond == e_a64_const.COND_VS:  # Overflow
            return v  # V flag set
        elif cond == e_a64_const.COND_VC:  # No overflow
            return cnot(v)  # V flag clear
        # Compound conditions
        elif cond == e_a64_const.COND_HI:  # Unsigned higher (C=1 and Z=0)
            return o_and(c, cnot(z), self._psize)
        elif cond == e_a64_const.COND_LS:  # Unsigned lower or same (C=0 or Z=1)
            return o_or(cnot(c), z, self._psize)
        elif cond == e_a64_const.COND_GE:  # Signed greater or equal (N == V)
            return eq(n, v)
        elif cond == e_a64_const.COND_LT:  # Signed less than (N != V)
            return ne(n, v)
        elif cond == e_a64_const.COND_GT:  # Signed greater (Z=0 and N==V)
            return o_and(cnot(z), eq(n, v), self._psize)
        elif cond == e_a64_const.COND_LE:  # Signed less or equal (Z=1 or N!=V)
            return o_or(z, ne(n, v), self._psize)
        elif cond == e_a64_const.COND_AL:  # Always
            return Const(1, self._psize)
        elif cond == e_a64_const.COND_NV:  # Never (treated as always in AArch64)
            return Const(1, self._psize)

        raise Exception('Unknown condition code: %d' % cond)

    def _cond_jmp(self, op, cond):
        """
        Handle conditional branch instruction.
        
        Returns a tuple of (address, constraint) pairs. The base class
        translateOpcode() method iterates through these and calls 
        effConstrain(addr, constraint) for each to register the path
        constraints for symbolic analysis.
        
        The first tuple is the taken branch (target address, condition true).
        The second tuple is the fall-through (next instruction, condition false).
        """
        return ((self.getOperObj(op, 0), cond),
                (Const(op.va + len(op), self._psize), cnot(cond)))

    # ==========================================================================
    # Data Processing Instructions
    # ==========================================================================

    def i_add(self, op):
        """ADD/ADDS - Add (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_add(v1, v2, dsize)
        
        # Check if this is ADDS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_add_flags(v1, v2, result, dsize)
            
        self.setOperObj(op, 0, result)

    # ADDS is handled by i_add checking IF_PSR_S
    i_adds = i_add

    def i_adc(self, op):
        """ADC/ADCS - Add with carry (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        carry = Var('pstate_c', self._psize)
        result = o_add(o_add(v1, v2, dsize), carry, dsize)
        
        # Check if this is ADCS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_add_flags(v1, v2, result, dsize)
            
        self.setOperObj(op, 0, result)

    # ADCS is handled by i_adc checking IF_PSR_S
    i_adcs = i_adc

    def i_sub(self, op):
        """SUB/SUBS - Subtract (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_sub(v1, v2, dsize)
        
        # Check if this is SUBS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_sub_flags(v1, v2, result, dsize)
            
        self.setOperObj(op, 0, result)

    # SUBS is handled by i_sub checking IF_PSR_S
    i_subs = i_sub

    def i_sbc(self, op):
        """SBC/SBCS - Subtract with carry (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        carry = Var('pstate_c', self._psize)
        # SBC: result = v1 - v2 - NOT(carry)
        result = o_sub(o_sub(v1, v2, dsize), o_sub(Const(1, self._psize), carry, dsize), dsize)
        
        # Check if this is SBCS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_sub_flags(v1, v2, result, dsize)
            
        self.setOperObj(op, 0, result)

    # SBCS is handled by i_sbc checking IF_PSR_S
    i_sbcs = i_sbc

    def i_neg(self, op):
        """NEG/NEGS - Negate (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        zero = Const(0, dsize)
        result = o_sub(zero, v1, dsize)
        
        # Check if this is NEGS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_sub_flags(zero, v1, result, dsize)
            
        self.setOperObj(op, 0, result)

    # NEGS is handled by i_neg checking IF_PSR_S
    i_negs = i_neg

    def i_cmp(self, op):
        """CMP - Compare (SUBS with discarded result)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        result = o_sub(v1, v2, dsize)
        self._set_sub_flags(v1, v2, result, dsize)

    def i_cmn(self, op):
        """CMN - Compare negative (ADDS with discarded result)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        result = o_add(v1, v2, dsize)
        self._set_add_flags(v1, v2, result, dsize)

    def i_mul(self, op):
        """MUL - Multiply"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_mul(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_madd(self, op):
        """MADD - Multiply-add"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        v3 = self.getOperObj(op, 3)
        result = o_add(o_mul(v1, v2, dsize), v3, dsize)
        self.setOperObj(op, 0, result)

    def i_msub(self, op):
        """MSUB - Multiply-subtract"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        v3 = self.getOperObj(op, 3)
        result = o_sub(v3, o_mul(v1, v2, dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_mneg(self, op):
        """MNEG - Multiply-negate"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_sub(Const(0, dsize), o_mul(v1, v2, dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_sdiv(self, op):
        """SDIV - Signed divide"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_div(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_udiv(self, op):
        """UDIV - Unsigned divide"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_div(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # Logical Instructions
    # ==========================================================================

    def i_and(self, op):
        """AND/ANDS - Bitwise AND (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_and(v1, v2, dsize)
        
        # Check if this is ANDS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_logic_flags(result, dsize)
            
        self.setOperObj(op, 0, result)

    # ANDS is handled by i_and checking IF_PSR_S
    i_ands = i_and

    def i_bic(self, op):
        """BIC/BICS - Bitwise bit clear (AND NOT) (with optional flag setting)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        # BIC: v1 AND NOT v2
        not_v2 = o_xor(v2, Const(e_bits.u_maxes[dsize], dsize), dsize)
        result = o_and(v1, not_v2, dsize)
        
        # Check if this is BICS (sets flags)
        if op.iflags & e_a64_const.IF_PSR_S:
            self._set_logic_flags(result, dsize)
            
        self.setOperObj(op, 0, result)

    # BICS is handled by i_bic checking IF_PSR_S
    i_bics = i_bic

    def i_orr(self, op):
        """ORR - Bitwise OR"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_or(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_orn(self, op):
        """ORN - Bitwise OR NOT"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        not_v2 = o_xor(v2, Const(e_bits.u_maxes[dsize], dsize), dsize)
        result = o_or(v1, not_v2, dsize)
        self.setOperObj(op, 0, result)

    def i_eor(self, op):
        """EOR - Bitwise exclusive OR"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_xor(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_eon(self, op):
        """EON - Bitwise exclusive OR NOT"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        not_v2 = o_xor(v2, Const(e_bits.u_maxes[dsize], dsize), dsize)
        result = o_xor(v1, not_v2, dsize)
        self.setOperObj(op, 0, result)

    # Aliases for mnemonic variations used by the disassembler
    i_or = i_orr    # ORR is often disassembled as 'or'
    i_eo = i_eor    # EOR is often disassembled as 'eo'

    def i_mvn(self, op):
        """MVN - Bitwise NOT"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_xor(v1, Const(e_bits.u_maxes[dsize], dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_tst(self, op):
        """TST - Test bits (ANDS with discarded result)"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        result = o_and(v1, v2, dsize)
        self._set_logic_flags(result, dsize)

    # ==========================================================================
    # Shift and Rotate Instructions
    # ==========================================================================

    def i_lsl(self, op):
        """LSL - Logical shift left"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_lshift(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_lsr(self, op):
        """LSR - Logical shift right"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        result = o_rshift(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_asr(self, op):
        """ASR - Arithmetic shift right"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        # Note: ASR preserves sign bit - using right shift for now
        # Full implementation would need sign extension
        result = o_rshift(v1, v2, dsize)
        self.setOperObj(op, 0, result)

    def i_ror(self, op):
        """ROR - Rotate right"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        v2 = self.getOperObj(op, 2)
        bitwidth = dsize * 8
        # Rotate right: (v1 >> v2) | (v1 << (bitwidth - v2))
        result = o_or(
            o_rshift(v1, v2, dsize),
            o_lshift(v1, o_sub(Const(bitwidth, dsize), v2, dsize), dsize),
            dsize
        )
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # Move Instructions
    # ==========================================================================

    def i_mov(self, op):
        """MOV - Move (register)"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_movz(self, op):
        """MOVZ - Move with zero"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_movn(self, op):
        """MOVN - Move with NOT"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_xor(v1, Const(e_bits.u_maxes[dsize], dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_movk(self, op):
        """MOVK - Move with keep"""
        dsize = self._getOperSize(op, 0)
        dst = self.getOperObj(op, 0)
        imm = self.getOperObj(op, 1)

        # Get shift amount from the immediate operand
        oper = op.opers[1]
        shift = oper.shval if hasattr(oper, 'shval') else 0

        # Create mask for 16 bits at the shift position
        mask = Const(0xffff << shift, dsize)
        inv_mask = o_xor(mask, Const(e_bits.u_maxes[dsize], dsize), dsize)

        # Clear the target bits and insert the new value
        result = o_or(o_and(dst, inv_mask, dsize), imm, dsize)
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # Sign/Zero Extension Instructions
    # ==========================================================================

    def i_sxtb(self, op):
        """SXTB - Sign extend byte"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sextend(o_and(v1, Const(0xff, dsize), dsize), Const(dsize, self._psize))
        self.setOperObj(op, 0, result)

    def i_sxth(self, op):
        """SXTH - Sign extend halfword"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sextend(o_and(v1, Const(0xffff, dsize), dsize), Const(dsize, self._psize))
        self.setOperObj(op, 0, result)

    def i_sxtw(self, op):
        """SXTW - Sign extend word"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sextend(o_and(v1, Const(0xffffffff, dsize), dsize), Const(dsize, self._psize))
        self.setOperObj(op, 0, result)

    def i_uxtb(self, op):
        """UXTB - Zero extend byte"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_and(v1, Const(0xff, dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_uxth(self, op):
        """UXTH - Zero extend halfword"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_and(v1, Const(0xffff, dsize), dsize)
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # Bitfield Instructions
    # ==========================================================================

    def i_sbfx(self, op):
        """SBFX - Signed bitfield extract"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        lsb = self.getOperObj(op, 2)
        width = self.getOperObj(op, 3)
        # Extract and sign extend
        mask = o_sub(o_lshift(Const(1, dsize), width, dsize), Const(1, dsize), dsize)
        extracted = o_and(o_rshift(v1, lsb, dsize), mask, dsize)
        result = o_sextend(extracted, Const(dsize, self._psize))
        self.setOperObj(op, 0, result)

    def i_ubfx(self, op):
        """UBFX - Unsigned bitfield extract"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        lsb = self.getOperObj(op, 2)
        width = self.getOperObj(op, 3)
        mask = o_sub(o_lshift(Const(1, dsize), width, dsize), Const(1, dsize), dsize)
        result = o_and(o_rshift(v1, lsb, dsize), mask, dsize)
        self.setOperObj(op, 0, result)

    def i_bfi(self, op):
        """BFI - Bitfield insert"""
        dsize = self._getOperSize(op, 0)
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        lsb = self.getOperObj(op, 2)
        width = self.getOperObj(op, 3)

        # Create mask for the field
        mask = o_sub(o_lshift(Const(1, dsize), width, dsize), Const(1, dsize), dsize)
        shifted_mask = o_lshift(mask, lsb, dsize)
        inv_mask = o_xor(shifted_mask, Const(e_bits.u_maxes[dsize], dsize), dsize)

        # Insert the field
        result = o_or(
            o_and(dst, inv_mask, dsize),
            o_lshift(o_and(src, mask, dsize), lsb, dsize),
            dsize
        )
        self.setOperObj(op, 0, result)

    def i_bfxil(self, op):
        """BFXIL - Bitfield extract and insert low"""
        dsize = self._getOperSize(op, 0)
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        lsb = self.getOperObj(op, 2)
        width = self.getOperObj(op, 3)

        # Extract from source
        mask = o_sub(o_lshift(Const(1, dsize), width, dsize), Const(1, dsize), dsize)
        extracted = o_and(o_rshift(src, lsb, dsize), mask, dsize)

        # Insert into low bits of destination
        inv_mask = o_xor(mask, Const(e_bits.u_maxes[dsize], dsize), dsize)
        result = o_or(o_and(dst, inv_mask, dsize), extracted, dsize)
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # Load/Store Instructions
    # ==========================================================================

    def i_ldr(self, op):
        """LDR - Load register"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)
        self._handle_writeback(op, 1)

    def i_ldrb(self, op):
        """LDRB - Load register byte"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)
        self._handle_writeback(op, 1)

    def i_ldrh(self, op):
        """LDRH - Load register halfword"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)
        self._handle_writeback(op, 1)

    def i_ldrsb(self, op):
        """LDRSB - Load register signed byte"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sextend(v1, Const(dsize, self._psize))
        self.setOperObj(op, 0, result)
        self._handle_writeback(op, 1)

    def i_ldrsh(self, op):
        """LDRSH - Load register signed halfword"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sextend(v1, Const(dsize, self._psize))
        self.setOperObj(op, 0, result)
        self._handle_writeback(op, 1)

    def i_ldrsw(self, op):
        """LDRSW - Load register signed word"""
        v1 = self.getOperObj(op, 1)
        result = o_sextend(v1, Const(8, self._psize))
        self.setOperObj(op, 0, result)
        self._handle_writeback(op, 1)

    def i_ldp(self, op):
        """LDP - Load pair of registers"""
        dsize = self._getOperSize(op, 0)
        addr_oper = op.opers[2]

        addr = self.getOperAddrObj(op, 2)

        # Load first register
        val1 = self.effReadMemory(addr, Const(dsize, self._psize))
        self.setOperObj(op, 0, val1)

        # Load second register
        addr2 = o_add(addr, Const(dsize, self._psize), self._psize)
        val2 = self.effReadMemory(addr2, Const(dsize, self._psize))
        self.setOperObj(op, 1, val2)

        self._handle_writeback(op, 2)

    def i_str(self, op):
        """STR - Store register"""
        v1 = self.getOperObj(op, 0)
        self.setOperObj(op, 1, v1)
        self._handle_writeback(op, 1)

    def i_strb(self, op):
        """STRB - Store register byte"""
        v1 = self.getOperObj(op, 0)
        self.setOperObj(op, 1, v1)
        self._handle_writeback(op, 1)

    def i_strh(self, op):
        """STRH - Store register halfword"""
        v1 = self.getOperObj(op, 0)
        self.setOperObj(op, 1, v1)
        self._handle_writeback(op, 1)

    def i_stp(self, op):
        """STP - Store pair of registers"""
        dsize = self._getOperSize(op, 0)
        val1 = self.getOperObj(op, 0)
        val2 = self.getOperObj(op, 1)

        addr = self.getOperAddrObj(op, 2)

        # Store first register
        self.effWriteMemory(addr, Const(dsize, self._psize), val1)

        # Store second register
        addr2 = o_add(addr, Const(dsize, self._psize), self._psize)
        self.effWriteMemory(addr2, Const(dsize, self._psize), val2)

        self._handle_writeback(op, 2)

    def _handle_writeback(self, op, idx):
        """Handle pre/post-index writeback for load/store operations."""
        oper = op.opers[idx]
        if not hasattr(oper, 'mode'):
            return

        if oper.mode == e_a64_disasm.LDST_MODE_PREIDX:
            # Pre-indexed: base = base + offset (already calculated)
            if hasattr(oper, 'basereg'):
                basereg = oper.basereg
                new_addr = self.getOperAddrObj(op, idx)
                rname = self._reg_ctx.getRegisterName(basereg)
                self.effSetVariable(rname, new_addr)

        elif oper.mode == e_a64_disasm.LDST_MODE_POSTIDX:
            # Post-indexed: base = base + offset (after the access)
            if hasattr(oper, 'basereg'):
                basereg = oper.basereg
                base = Var(self._reg_ctx.getRegisterName(basereg), self._psize)
                offset = Const(oper.simm if hasattr(oper, 'simm') else 0, self._psize)
                new_addr = o_add(base, offset, self._psize)
                rname = self._reg_ctx.getRegisterName(basereg)
                self.effSetVariable(rname, new_addr)

    # ==========================================================================
    # Address Generation Instructions
    # ==========================================================================

    def i_adr(self, op):
        """ADR - Form PC-relative address"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_adrp(self, op):
        """ADRP - Form PC-relative address to 4KB page"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    # ==========================================================================
    # Branch Instructions
    # ==========================================================================

    def i_b(self, op):
        """B - Unconditional branch"""
        # Unconditional branches don't return constraints
        pass

    def i_bl(self, op):
        """BL - Branch with link"""
        # Save return address in LR (X30)
        ret_addr = Const(op.va + len(op), self._psize)
        self.effSetVariable('x30', ret_addr)
        self.effFofX(self.getOperObj(op, 0))

    def i_blr(self, op):
        """BLR - Branch with link to register"""
        ret_addr = Const(op.va + len(op), self._psize)
        self.effSetVariable('x30', ret_addr)
        targ = self.getOperObj(op, 0)
        self.effFofX(targ)

    def i_br(self, op):
        """BR - Branch to register"""
        pass

    def i_ret(self, op):
        """RET - Return from subroutine"""
        # Default return register is X30 (LR)
        pass

    # Conditional branches
    def _get_branch_cond_from_mnem(self, mnem):
        """Extract condition code from branch mnemonic."""
        # b.eq, b.ne, etc.
        cond_map = {
            'b.eq': e_a64_const.COND_EQ,
            'b.ne': e_a64_const.COND_NE,
            'b.cs': e_a64_const.COND_CS,
            'b.hs': e_a64_const.COND_CS,  # Alias
            'b.cc': e_a64_const.COND_CC,
            'b.lo': e_a64_const.COND_CC,  # Alias
            'b.mi': e_a64_const.COND_MI,
            'b.pl': e_a64_const.COND_PL,
            'b.vs': e_a64_const.COND_VS,
            'b.vc': e_a64_const.COND_VC,
            'b.hi': e_a64_const.COND_HI,
            'b.ls': e_a64_const.COND_LS,
            'b.ge': e_a64_const.COND_GE,
            'b.lt': e_a64_const.COND_LT,
            'b.gt': e_a64_const.COND_GT,
            'b.le': e_a64_const.COND_LE,
            'b.al': e_a64_const.COND_AL,
        }
        return cond_map.get(mnem.lower())

    # Implement each conditional branch
    def i_b_eq(self, op):
        """B.EQ - Branch if equal"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_EQ))

    def i_b_ne(self, op):
        """B.NE - Branch if not equal"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_NE))

    def i_b_cs(self, op):
        """B.CS - Branch if carry set"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_CS))

    i_b_hs = i_b_cs  # Alias

    def i_b_cc(self, op):
        """B.CC - Branch if carry clear"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_CC))

    i_b_lo = i_b_cc  # Alias

    def i_b_mi(self, op):
        """B.MI - Branch if minus/negative"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_MI))

    def i_b_pl(self, op):
        """B.PL - Branch if plus/positive or zero"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_PL))

    def i_b_vs(self, op):
        """B.VS - Branch if overflow set"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_VS))

    def i_b_vc(self, op):
        """B.VC - Branch if overflow clear"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_VC))

    def i_b_hi(self, op):
        """B.HI - Branch if unsigned higher"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_HI))

    def i_b_ls(self, op):
        """B.LS - Branch if unsigned lower or same"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_LS))

    def i_b_ge(self, op):
        """B.GE - Branch if signed greater or equal"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_GE))

    def i_b_lt(self, op):
        """B.LT - Branch if signed less than"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_LT))

    def i_b_gt(self, op):
        """B.GT - Branch if signed greater than"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_GT))

    def i_b_le(self, op):
        """B.LE - Branch if signed less or equal"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_LE))

    def i_b_al(self, op):
        """B.AL - Branch always"""
        return self._cond_jmp(op, self._cond_check(e_a64_const.COND_AL))

    def i_cbz(self, op):
        """CBZ - Compare and branch if zero"""
        v1 = self.getOperObj(op, 0)
        zero = Const(0, self._psize)
        cond = eq(v1, zero)
        # For CBZ, operand 0 is register to test, operand 1 is branch target
        return ((self.getOperObj(op, 1), cond),
                (Const(op.va + len(op), self._psize), cnot(cond)))

    def i_cbnz(self, op):
        """CBNZ - Compare and branch if not zero"""
        v1 = self.getOperObj(op, 0)
        zero = Const(0, self._psize)
        cond = ne(v1, zero)
        # For CBNZ, operand 0 is register to test, operand 1 is branch target
        return ((self.getOperObj(op, 1), cond),
                (Const(op.va + len(op), self._psize), cnot(cond)))

    def i_tbz(self, op):
        """TBZ - Test bit and branch if zero"""
        v1 = self.getOperObj(op, 0)
        bit = self.getOperObj(op, 1)
        mask = o_lshift(Const(1, self._psize), bit, self._psize)
        test = o_and(v1, mask, self._psize)
        cond = eq(test, Const(0, self._psize))
        # Target is operand 2 for TBZ
        return ((self.getOperObj(op, 2), cond),
                (Const(op.va + len(op), self._psize), cnot(cond)))

    def i_tbnz(self, op):
        """TBNZ - Test bit and branch if not zero"""
        v1 = self.getOperObj(op, 0)
        bit = self.getOperObj(op, 1)
        mask = o_lshift(Const(1, self._psize), bit, self._psize)
        test = o_and(v1, mask, self._psize)
        cond = ne(test, Const(0, self._psize))
        return ((self.getOperObj(op, 2), cond),
                (Const(op.va + len(op), self._psize), cnot(cond)))

    # ==========================================================================
    # Conditional Select Instructions
    # ==========================================================================

    def i_csel(self, op):
        """CSEL - Conditional select"""
        # CSEL Xd, Xn, Xm, cond: Xd = cond ? Xn : Xm
        # For now, we just set Xd = Xn (simplified)
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_csinc(self, op):
        """CSINC - Conditional select increment"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_csinv(self, op):
        """CSINV - Conditional select invert"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_csneg(self, op):
        """CSNEG - Conditional select negate"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_cset(self, op):
        """CSET - Conditional set"""
        # CSET Xd, cond: Xd = cond ? 1 : 0
        self.setOperObj(op, 0, Const(1, self._getOperSize(op, 0)))

    def i_csetm(self, op):
        """CSETM - Conditional set mask"""
        # CSETM Xd, cond: Xd = cond ? -1 : 0
        dsize = self._getOperSize(op, 0)
        self.setOperObj(op, 0, Const(e_bits.u_maxes[dsize], dsize))

    def i_cinc(self, op):
        """CINC - Conditional increment"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_add(v1, Const(1, dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_cinv(self, op):
        """CINV - Conditional invert"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_xor(v1, Const(e_bits.u_maxes[dsize], dsize), dsize)
        self.setOperObj(op, 0, result)

    def i_cneg(self, op):
        """CNEG - Conditional negate"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        result = o_sub(Const(0, dsize), v1, dsize)
        self.setOperObj(op, 0, result)

    # ==========================================================================
    # System Instructions
    # ==========================================================================

    def i_nop(self, op):
        """NOP - No operation"""
        pass

    def i_svc(self, op):
        """SVC - Supervisor call"""
        # System call - log as function call
        imm = self.getOperObj(op, 0)
        self.effFofX(imm)

    def i_brk(self, op):
        """BRK - Breakpoint"""
        pass

    def i_hlt(self, op):
        """HLT - Halt"""
        pass

    def i_mrs(self, op):
        """MRS - Move from system register"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_msr(self, op):
        """MSR - Move to system register"""
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    # ==========================================================================
    # Data Synchronization and Memory Barriers
    # ==========================================================================

    def i_dmb(self, op):
        """DMB - Data memory barrier"""
        pass

    def i_dsb(self, op):
        """DSB - Data synchronization barrier"""
        pass

    def i_isb(self, op):
        """ISB - Instruction synchronization barrier"""
        pass

    # ==========================================================================
    # Reverse Instructions
    # ==========================================================================

    def i_rev(self, op):
        """REV - Reverse bytes"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        # Byte reversal - simplified for now
        self.setOperObj(op, 0, v1)

    def i_rev16(self, op):
        """REV16 - Reverse bytes in halfwords"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    def i_rev32(self, op):
        """REV32 - Reverse bytes in words"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)

    # ==========================================================================
    # Count Leading/Trailing Zeros/Ones
    # ==========================================================================

    def i_clz(self, op):
        """CLZ - Count leading zeros"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        # CLZ is complex to express symbolically - use a placeholder
        self.setOperObj(op, 0, Call(Const(0, self._psize), dsize, [v1]))

    def i_cls(self, op):
        """CLS - Count leading sign bits"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, Call(Const(0, self._psize), dsize, [v1]))

    def i_rbit(self, op):
        """RBIT - Reverse bits"""
        dsize = self._getOperSize(op, 0)
        v1 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v1)


# ==========================================================================
# Symbolik Analysis Support Classes
# ==========================================================================

class A64ArgDefSymEmu(vsym_callconv.ArgDefSymEmu):
    """Argument definition symbolic emulator for AArch64."""
    __xlator__ = A64SymbolikTranslator


class A64CallSym(vsym_callconv.SymbolikCallingConvention):
    """AArch64 calling convention for symbolic analysis."""
    __argdefemu__ = A64ArgDefSymEmu


class A64SymFuncEmu(vsym_analysis.SymbolikFunctionEmulator):
    """Symbolic function emulator for AArch64."""
    __width__ = 8

    def __init__(self, vw, *args, initial_sp=0xbfbff000, xlator=None):
        vsym_analysis.SymbolikFunctionEmulator.__init__(self, vw, *args, xlator=xlator)
        self.setStackBase(0xbfbff000, 16384)
        self.addCallingConvention('a64call', A64CallSym(xlator))

    def getStackCounter(self):
        return self.getSymVariable('sp')

    def setStackCounter(self, symobj):
        self.setSymVariable('sp', symobj)


class A64SymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    """Symbolic analysis context for AArch64."""
    __xlator__ = A64SymbolikTranslator
    __emu__ = A64SymFuncEmu
