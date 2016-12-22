import sys

import envi
import envi.bits as e_bits
import envi.registers as e_registers
import envi.archs.i386 as e_i386

import vivisect.symboliks.analysis as vsym_analysis
import vivisect.symboliks.callconv as vsym_callconv
import vivisect.symboliks.emulator as vsym_emulator
import vivisect.symboliks.translator as vsym_trans

from vivisect.const import *
from vivisect.symboliks.common import *
from vivisect.symboliks.constraints import *


def getSegmentSymbol(op):
    if op.prefixes & e_i386.PREFIX_CS:
        return Var('cs', 4)
    if op.prefixes & e_i386.PREFIX_SS:
        return Var('ss', 4)
    if op.prefixes & e_i386.PREFIX_DS:
        return Var('ds', 4)
    if op.prefixes & e_i386.PREFIX_ES:
        return Var('es', 4)
    if op.prefixes & e_i386.PREFIX_FS:
        return Var('fs', 4)
    if op.prefixes & e_i386.PREFIX_GS:
        return Var('gs', 4)


class ArgDefSymEmu(object):
    '''
    An emulator snapped in to return the symbolic representation of
    a calling convention arg definition.  This is used by getPreCallArgs when
    called by {get, set}SymbolikArgs.  This allows us to not have to
    re-implement cc argument parsing *again* for symbolics.
    '''

    def __init__(self):
        self.xlator = self.__xlator__(None)

    def getRegister(self, ridx):
        '''
        uses the translators method to return a symbolic object for a
        register index.
        '''
        return self.xlator.getRegObj(ridx)

    def getStackCounter(self):
        '''
        uses the translators register ctx to find the sp index and returns a
        symbolic object for the sp.
        '''
        return self.getRegister(self.xlator._reg_ctx._rctx_spindex)

    def setStackCounter(self, value):
        '''
        stubbed out so when we re-use deallocateCallSpace we don't get an
        exception.  we only use the delta returned by deallocateCallSpace; we
        don't care that it's setting the stack counter.
        '''
        pass

    def readMemoryFormat(self, va, fmt):
        # TODO: we assume psize and le, better way? must be...
        if not fmt.startswith('<') and not fmt.endswith('P'):
            raise Exception('we dont handle this format string')

        if isinstance(va, int) or isinstance(va, int):
            va = Const(va, self.xlator._psize)

        if len(fmt) == 2:
            return Mem(va, Const(self.xlator._psize, self.xlator._psize))

        args = []
        num = int(fmt[1:fmt.index('P')])
        for i in range(num):
            args.append(Mem(va, Const(self.xlator._psize, self.xlator._psize)))
            va += Const(self.xlator._psize, self.xlator._psize)

        return args


class IntelSymbolikTranslator(vsym_trans.SymbolikTranslator):
    '''
    Common parent for i386 and x64.  Make sure you define:
    __arch__, __ip__, __sp__, __srcp__, __destp__

    Symbolik representations that are 'agnostic' to 32 or 64-bit belong here.
    '''

    def __init__(self, vw):
        vsym_trans.SymbolikTranslator.__init__(self, vw)
        self._arch = self.__arch__()
        self._psize = self._arch.getPointerSize()
        self._reg_ctx = self._arch.archGetRegCtx()

    def getRegObj(self, regidx):
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth // 8)

        # Translate to meta if needed...
        if ridx != regidx:
            # we cannot call _xlateToMetaReg since we'd pass in a symbolik
            # object that would trigger an and operation; the code in envi
            # obviously is NOT symboliks aware (2nd op in & operation is NOT
            # a symbolik); so we do it manually here since we are symbolik
            # aware.
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            metawidth = e_bits.u_maxes.index(mask)
            if lshift != 0:
                val = o_rshift(val, Const(lshift, metawidth), metawidth)

            # We must be explicit about the width!
            val = o_and(val, Const(mask, metawidth), metawidth)

        return val

    def setRegObj(self, regidx, obj):
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth // 8)

        # Translate to native if needed...
        if ridx != regidx:
            # we cannot call _xlateToNativReg since we'd pass in a symbolik
            # object that would trigger an or operation; the code in envi
            # obviously is NOT symboliks aware (2nd op in | operation is NOT
            # a symbolik); so we do it manually here since we are symbolik
            # aware.
            # obj = self._reg_ctx._xlateToNativeReg(regidx, obj)
            basemask = (2 ** rbitwidth) - 1
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            # cut hole in mask
            finalmask = basemask ^ (mask << lshift)
            if lshift != 0:
                obj <<= Const(lshift, rbitwidth // 8)

            obj = obj | (val & Const(finalmask, rbitwidth // 8))

        self.effSetVariable(rname, obj)

    def getOperAddrObj(self, op, idx):
        oper = op.opers[idx]
        seg = getSegmentSymbol(op)

        if isinstance(oper, e_i386.i386RegMemOper):
            reg = Var(self._reg_ctx.getRegisterName(oper.reg), oper.tsize)
            if oper.disp == 0:
                base = reg
            if oper.disp > 0:
                base = o_add(reg, Const(oper.disp, self._psize), self._psize)
            if oper.disp < 0:
                base = o_sub(reg, Const(abs(oper.disp), self._psize), self._psize)

            if seg:
                return o_add(seg, base, self._psize)

            return base

        elif isinstance(oper, e_i386.i386SibOper):

            base = None
            if oper.imm != None:
                base = Const(oper.imm, self._psize)

            if oper.reg != None:
                robj = self.getRegObj(oper.reg)
                if base == None:
                    base = robj
                else:
                    base = o_add(base, robj, self._psize)

            # Base is set by here for sure!
            if oper.index != None:
                robj = self.getRegObj(oper.index)
                base = o_add(base, o_mul(robj, Const(oper.scale, self._psize), self._psize), self._psize)

            if oper.disp != None:
                if oper.disp > 0:
                    base = o_add(base, Const(oper.disp, self._psize), self._psize)
                else:
                    base = o_sub(base, Const(abs(oper.disp), self._psize), self._psize)

            if seg:
                return o_add(seg, base, self._psize)

            return base

        elif isinstance(oper, e_i386.i386ImmMemOper):
            # FIXME plumb more segment awareness!
            if seg:
                return o_add(seg, Const(oper.imm, self._psize), self._psize)

            return Const(oper.imm, self._psize)

    def getOperObj(self, op, idx):
        '''
        Translate the specified operand to a symbol compatible with
        the symbolic translation system.
        '''
        oper = op.opers[idx]
        if oper.isReg():
            return self.getRegObj(oper.reg)

        elif oper.isDeref():
            addrsym = self.getOperAddrObj(op, idx)
            return self.effReadMemory(addrsym, Const(oper.tsize, self._psize))

        elif oper.isImmed():
            ret = oper.getOperValue(op, self)
            return Const(ret, self._psize)

        raise Exception('Unknown operand class: %s' % oper.__class__.__name__)

    def setOperObj(self, op, idx, obj):
        '''
        Set the operand to the new symbolic object.
        '''
        oper = op.opers[idx]
        if oper.isReg():
            self.setRegObj(oper.reg, obj)
            return

        if oper.isDeref():
            addrsym = self.getOperAddrObj(op, idx)
            return self.effWriteMemory(addrsym, Const(oper.tsize, self._psize), obj)

        raise Exception('Umm..... really?')

    def __get_dest_maxes(self, op):
        tsize = op.opers[0].tsize
        smax = e_bits.s_maxes[tsize]
        umax = e_bits.u_maxes[tsize]
        return smax, umax

    def i_adc(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        # FIXME this is wrong!
        # if self.getFlag(EFLAGS_CF):
        #    v2 = v2 + 1

        # self.effSetVariable('eflags_zf', eq(add, Const(0)))
        self.setOperObj(op, 0, v1 + v2)

    def i_add(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        dsize = op.opers[0].tsize
        dmax = e_bits.s_maxes[dsize]
        ssize = op.opers[1].tsize

        smax, umax = self.__get_dest_maxes(op)

        add = o_add(v1, v2, dsize)
        self.setOperObj(op, 0, add)

        # self.effSetVariable('eflags_gt', gt(v1, v2))
        # self.effSetVariable('eflags_lt', lt(v1, v2))
        # self.effSetVariable('eflags_sf', lt(v1, v2))
        # self.effSetVariable('eflags_eq', eq(v1+v2, 0))

    def i_and(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        obj = o_and(v1, v2, v1.getWidth())

        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize)))  # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize)))  # v1 & v2 == 0

        self.setOperObj(op, 0, obj)

    def i_bt(self, op):
        ''' 
        selects a bit in a bit string
        '''
        bit_base = self.getOperObj(op, 0)
        bit = self.getOperObj(op, 1)
        # if bit >= bit_base.getWidth()*8: throw a fit.

        val = (bit_base >> bit) & Const(1, 1)
        self.effSetVariable('eflags_cf', (eq(val, Const(1, 1))))
        self.effSetVariable('eflags_gt', (eq(val, Const(0, 1))))
        self.effSetVariable('eflags_lt', (ne(val, Const(0, 1))))
        self.effSetVariable('eflags_sf', (ne(val, Const(0, 1))))
        self.effSetVariable('eflags_eq', (eq(val, Const(0, 1))))

    def i_call(self, op):
        # For now, calling means finding which of our symbols go in
        # and logging what comes out.
        targ = self.getOperObj(op, 0)
        self.effFofX(targ)
        return

    def i_cld(self, op):
        self.effSetVariable('eflags_df', Const(0, self._psize))

    def i_cmp(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        res = o_sub(v1, v2, v1.getWidth())
        self.effSetVariable('eflags_cf', gt(v2, v1))  #
        self.effSetVariable('eflags_gt', gt(v1, v2))  # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2))  # v1 - v2 == 0 :: v1 == v2

    def i_dec(self, op):
        v1 = self.getOperObj(op, 0)
        one = Const(1, self._psize)

        sub = o_sub(v1, one, v1.getWidth())

        self.effSetVariable('eflags_gt', gt(v1, one))  # v1 - 1 > 0 :: v1 > 1
        self.effSetVariable('eflags_lt', lt(v1, one))  # v1 - 1 < 0 :: v1 < 1
        self.effSetVariable('eflags_sf', lt(v1, one))  # v1 - 1 < 0 :: v1 < 1
        self.effSetVariable('eflags_eq', eq(v1, one))  # v1 - 1 == 0 :: v1 == 1

        self.setOperObj(op, 0, sub)

    def i_div(self, op):
        oper = op.opers[0]
        divbase = self.getOperObj(op, 1)

        if oper.tsize == 1:
            # TODO: this is broken
            ax = self._reg_ctx._xlateToNativeReg(e_i386.REG_AX, Var('eax', self._psize))
            quot = ax // divbase
            rem = ax % divbase
            # TODO: this is broken
            self.effSetVariable('eax', (quot << 8) + rem)

        elif oper.tsize == 2:
            raise Exception("16 bit divide needs help!")

        elif oper.tsize == 4:
            eax = Var('eax', self._psize)
            edx = Var('edx', self._psize)

            # FIXME 16 bit over-ride
            tot = (edx << Const(32, self._psize)) + eax
            quot = tot // divbase
            rem = tot % divbase
            self.effSetVariable('eax', quot)
            self.effSetVariable('edx', rem)
            # FIXME maybe we need a "check exception" effect?

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_hlt(self, op):
        # Nothing to do symbolically....
        pass

    def i_imul(self, op):
        ocount = len(op.opers)
        if ocount == 2:
            dst = self.getOperObj(op, 0)
            src = self.getOperObj(op, 1)
            dsize = op.opers[0].tsize
            res = dst * src
            self.setOperObj(op, 0, res)

        elif ocount == 3:
            dst = self.getOperObj(op, 0)
            src1 = self.getOperObj(op, 1)
            src2 = self.getOperObj(op, 2)
            dsize = op.opers[0].tsize
            res = src1 * src2
            self.setOperObj(op, 0, res)

        else:
            raise Exception("WTFO?  i_imul with no opers")

        # print "FIXME: IMUL FLAGS only valid for POSITIVE results"
        f = gt(res, Const(e_bits.s_maxes[dsize // 2], dsize))
        self.effSetVariable('eflags_cf', f)
        self.effSetVariable('eflags_of', f)

    def i_mul(self, op):
        ocount = len(op.opers)
        if ocount == 2:
            dst = self.getOperObj(op, 0)
            src = self.getOperObj(op, 1)
            dsize = op.opers[0].tsize
            res = dst * src
            self.setOperObj(op, 0, res)

        elif ocount == 3:
            dst = self.getOperObj(op, 0)
            src1 = self.getOperObj(op, 1)
            src2 = self.getOperObj(op, 2)
            res = src1 * src2
            self.setOperObj(op, 0, res)

        else:
            raise Exception("WTFO?  i_mul with no opers")

        f = gt(res, Const(e_bits.u_maxes[dsize // 2], dsize))
        self.effSetVariable('eflags_cf', f)
        self.effSetVariable('eflags_of', f)

    def i_inc(self, op):
        v1 = self.getOperObj(op, 0)
        obj = o_add(v1, Const(1, self._psize), v1.getWidth())
        u = UNK(obj, Const(1, self._psize))
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', u)
        self.effSetVariable('eflags_eq', u)
        self.setOperObj(op, 0, obj)

    def i_int3(self, op):
        # FIXME another "test for exception" effect vote!
        pass

    # We include all the possible Jcc names just in case somebody
    # gets hinkey with the disassembler.
    def i_ja(self, op):
        return self._cond_jmp(op, Var('eflags_gt', self._psize))

    def i_jae(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_lt', self._psize)))

    def i_jb(self, op):
        return self._cond_jmp(op, Var('eflags_lt', self._psize))

    def i_jbe(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_gt', self._psize)))

    def i_jc(self, op):
        return self._cond_jmp(op, Var('eflags_cf', self._psize))

    def i_je(self, op):
        return self._cond_jmp(op, Var('eflags_eq', self._psize))

    def _cond_jmp(self, op, cond):
        # Construct the tuple for the conditional jump
        return (
            (self.getOperObj(op, 0), cond),
            (Const(op.va + len(op), self._psize), cnot(cond)),
        )

    def i_jg(self, op):
        return self._cond_jmp(op, Var('eflags_gt', self._psize))

    def i_jge(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_lt', self._psize)))

    def i_jl(self, op):
        return self._cond_jmp(op, Var('eflags_lt', self._psize))

    def i_jle(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_gt', self._psize)))

    i_jna = i_jbe
    i_jnae = i_jb
    i_jnb = i_jae
    i_jnbe = i_ja
    i_jnc = i_jae

    def i_jmp(self, op):
        tgt = self.getOperObj(op, 0)
        if not tgt.isDiscrete():
            # indirect jmp... table!

            return [(Const(tva, self._psize), eq(tgt, Const(tva, self._psize))) for fr, tva, tp, flag in
                    self.vw.getXrefsFrom(op.va) if tp == REF_CODE]

    def i_jne(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_eq', self._psize)))

    i_jng = i_jle
    i_jnge = i_jl
    i_jnl = i_jge
    i_jnle = i_jg

    # def i_jno(self, op):
    # if self.cond_no():   return self.getOperValue(op, 0)

    # def i_jnp(self, op):
    # if self.cond_np():   return self.getOperValue(op, 0)

    def i_jns(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_sf', self._psize)))

    i_jnz = i_jne

    # def i_jo(self, op):
    # if self.cond_o():    return self.getOperValue(op, 0)

    # def i_jp(self, op):
    # if self.cond_p():    return self.getOperValue(op, 0)

    # i_jpe = i_jp
    # i_jpo = i_jnp

    def i_js(self, op):
        return self._cond_jmp(op, Var('eflags_sf', self._psize))

    def i_jecxz(self, op):
        return self._cond_jmp(op, cnot(Var('ecx', self._psize)))

    i_jz = i_je

    def i_lea(self, op):
        obj = self.getOperAddrObj(op, 1)
        self.setOperObj(op, 0, obj)

    def i_mov(self, op):
        o = self.getOperObj(op, 1)
        self.setOperObj(op, 0, o)

    i_movnti = i_mov

    def i_movq(self, op):
        o = self.getOperObj(op, 1)
        self.setOperObj(op, 0, o)

    def i_movsb(self, op):
        si = Var(self.__srcp__, self._psize)
        di = Var(self.__destp__, self._psize)
        mem = Mem(si, Const(1, self._psize))
        self.effWriteMemory(di, Const(1, self._psize), mem)
        self.effSetVariable(self.__srcp__, si + Const(1, self._psize))
        self.effSetVariable(self.__destp__, di + Const(1, self._psize))

    def i_movsd(self, op):
        si = Var(self.__srcp__, self._psize)
        di = Var(self.__destp__, self._psize)
        mem = Mem(si, Const(4, self._psize))
        self.effWriteMemory(di, Const(4, self._psize), mem)

        # FIXME *symbolic* flags!
        # if self.getFlag(EFLAGS_DF):
        # esi -= 4
        # edi -= 4

        # else:
        # esi += 4
        # edi += 4
        # print 'FIXME how to handle DF bit?'

        self.effSetVariable(self.__srcp__, si + Const(4, self._psize))
        self.effSetVariable(self.__destp__, di + Const(4, self._psize))

    def i_movsx(self, op):
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        v2 = o_sextend(self.getOperObj(op, 1), Const(ssize, self._psize))
        self.setOperObj(op, 0, v2)

    def i_movzx(self, op):
        v2 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, v2)

    def i_neg(self, op):
        obj = self.getOperObj(op, 0)
        width = obj.getWidth()
        self.setOperObj(op, 0, o_sub(Const(0, width), obj, width))

    def i_nop(self, op):
        pass

    def i_prefetch(self, op):
        pass

    def i_prefetchw(self, op):
        pass

    def i_not(self, op):
        v1 = self.getOperObj(op, 0)
        v1width = v1.getWidth()
        v1 ^= Const(e_bits.u_maxes[v1width], v1width)
        self.setOperObj(op, 0, v1)

    def i_or(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_or(v1, v2, v1.getWidth())
        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize)))  # v1 | v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize)))  # v1 & v2 == 0
        self.setOperObj(op, 0, obj)

    def i_push(self, op):
        v1 = self.getOperObj(op, 0)
        sp = self.getRegObj(self._reg_ctx._rctx_spindex)
        self.effSetVariable(self.__sp__, sp - Const(self._psize, self._psize))
        # NOTE: we do the write after the set, so there is no need
        # to write to sp - psize...
        self.effWriteMemory(Var(self.__sp__, self._psize), Const(self._psize, self._psize), v1)

    def i_pop(self, op):
        self.setOperObj(op, 0, Mem(Var(self.__sp__, self._psize), Const(self._psize, self._psize)))
        self.effSetVariable(self.__sp__, Var(self.__sp__, self._psize) + Const(self._psize, self._psize))

    def i_pxor(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_xor(v1, v2, v1.getWidth())
        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize)))  # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize)))  # v1 & v2 == 0
        self.setOperObj(op, 0, obj)

    def i_ret(self, op):
        self.effSetVariable(self.__ip__, Mem(Var(self.__sp__, self._psize), Const(self._psize, self._psize)))
        sp = Var(self.__sp__, self._psize)
        sp += Const(self._psize, self._psize)
        if len(op.opers):
            sp += self.getOperObj(op, 0)
        self.effSetVariable(self.__sp__, sp)

    def i_sar(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        # Arithmetic shifts are multiplies and divides!
        res = o_div(v1, o_pow(Const(2, self._psize), v2, self._psize), v1.getWidth())

        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(res, Const(0, self._psize)))  # v1 | v2 < 0
        self.effSetVariable('eflags_eq', eq(res, Const(0, self._psize)))  # v1 & v2 == 0

        self.setOperObj(op, 0, res)

    def i_sbb(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_sub(v1, v2, v1.getWidth())  # FIXME borrow!
        self.effSetVariable('eflags_gt', gt(v1, v2))  # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2))  # v1 - v2 == 0 :: v1 == v2
        self.setOperObj(op, 0, v1 - v2)

    def i_setnz(self, op):
        # FIXME
        self.setOperObj(op, 0, Const(1, self._psize))  # cnot(Var('eflags_eq', self._psize)))

    def i_setz(self, op):
        # FIXME
        self.setOperObj(op, 0, Const(0, self._psize))  # Var('eflags_eq', self._psize))

    def i_shl(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        # if v2.isDiscrete() and v2.solve() > 0xff:
        # v2 = v2 & 0xff

        # No effect (not even flags) if shift is 0
        # if v2.solve() == 0:
        # return

        self.setOperObj(op, 0, v1 << v2)

        u = UNK(v1, v2)  # COP OUT FOR NOW...
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', u)
        self.effSetVariable('eflags_eq', u)

    def i_shr(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        # if v2.isDiscrete() and v2.solve() > 0xff:
        # v2 = v2 & 0xff

        self.setOperObj(op, 0, v1 >> v2)

        u = UNK(v1, v2)  # COP OUT FOR NOW...
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', u)
        self.effSetVariable('eflags_eq', u)

    def i_std(self, op):
        self.effSetVariable('eflags_df', Const(1, self._psize))

    def i_sub(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_sub(v1, v2, v1.getWidth())
        self.effSetVariable('eflags_gt', gt(v1, v2))  # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2))  # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2))  # v1 - v2 == 0 :: v1 == v2
        self.setOperObj(op, 0, obj)

    def i_test(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_and(v1, v2, v1.getWidth())
        u = UNK(v1, v2)

        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', lt(obj, Const(0, self._psize)))  # ( SF != OF ) ( OF is cleared )

        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize)))  # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize)))  # v1 & v2 == 0

    def i_xadd(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        res = o_add(v1, v2, v1.getWidth())
        self.setOperObj(op, 0, res)
        self.setOperObj(op, 1, v1)
        # self.effSetVariable('eflags_gt', gt(v1, v2))
        # self.effSetVariable('eflags_lt', lt(v1, v2))
        # self.effSetVariable('eflags_sf', lt(v1, v2))
        # self.effSetVariable('eflags_eq', eq(v1+v2, 0))

    def i_xor(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_xor(v1, v2, v1.getWidth())
        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize)))  # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize)))  # v1 & v2 == 0
        self.setOperObj(op, 0, obj)

    def i_cmpxchg(self, op):

        # FIXME CATASTROPHIC THIS CONTAINS BRANCHING LOGIC STATE!
        # FOR NOW WE JUST DO IT WITHOUT ANY CONDITIONAL
        x = self.getOperObj(op, 0)
        y = self.getOperObj(op, 1)
        self.effSetVariable('i386_xchg_tmp', x)
        self.setOperObj(op, 0, y)
        self.setOperObj(op, 1, Var('i386_xchg_tmp', self._psize))

    def i_xchg(self, op):
        # NOTE: requires using temp var because each asignment occurs
        # seperately. (even though the API makes it look like you've
        # got your pwn copy... ;) )
        x = self.getOperObj(op, 0)
        y = self.getOperObj(op, 1)
        self.effSetVariable('i386_xchg_tmp', x)
        self.setOperObj(op, 0, y)
        self.setOperObj(op, 1, Var('i386_xchg_tmp', self._psize))

    def i_rdtsc(self, op):
        self.effSetVariable('eax', Var('TSC_HIGH', 4))
        self.effSetVariable('edx', Var('TSC_LOW', 4))

    def i_leave(self, op):
        self.effSetVariable(self.__sp__, Var(self.__bp__, self._psize))
        self.effSetVariable(self.__bp__, Mem(Var(self.__sp__, self._psize), Const(self._psize, self._psize)))
        self.effSetVariable(self.__sp__,
                            o_add(Var(self.__sp__, self._psize), Const(self._psize, self._psize), self._psize))

    def i_rol(self, op):
        oper = self.getOperObj(op, 0)
        opersize = oper.getWidth()
        bitsize = opersize * 8
        bit = self.getOperObj(op, 1)
        if bit.isDiscrete():
            bitnum = bit.solve()
            val = oper >> Const(bitsize - bitnum, self._psize)
        else:
            val = oper >> Const(bitsize, self._psize) - bit
        val |= (oper << bit)
        self.setOperObj(op, 0, val)

    def i_ror(self, op):
        oper = self.getOperObj(op, 0)
        opersize = oper.getWidth()
        bitsize = opersize * 8
        bit = self.getOperObj(op, 1)
        if bit.isDiscrete():
            bitnum = bit.solve()
            val = oper << Const(bitsize - bitnum, self._psize)
        else:
            val = oper << (Const(bitsize, self._psize) - bit)
        val |= (oper >> bit)
        self.setOperObj(op, 0, val)

    def i_movups(self, op):
        # lots of writing in the spec on different things about opersizes... 
        # but all seems to be a big mov.
        data = self.getOperObj(op, 1)
        self.setOperObj(op, 0, data)

    def i_movaps(self, op):
        # lots of writing in the spec on different things about opersizes... 
        # but all seems to be a big mov.
        data = self.getOperObj(op, 1)
        self.setOperObj(op, 0, data)


class i386SymbolikTranslator(IntelSymbolikTranslator):
    __arch__ = e_i386.i386Module
    __ip__ = 'eip'  # we could use regctx.getRegisterName if we want.
    __sp__ = 'esp'  # we could use regctx.getRegisterName if we want.
    __bp__ = 'ebp'  # we could use regctx.getRegisterName if we want.
    __srcp__ = 'esi'
    __destp__ = 'edi'

    def i_pushad(self, op):
        esp = self.getRegObj(e_i386.REG_ESP)
        self.effWriteMemory(esp - Const(4, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_EAX))
        self.effWriteMemory(esp - Const(8, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_ECX))
        self.effWriteMemory(esp - Const(12, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_EDX))
        self.effWriteMemory(esp - Const(16, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_EBX))
        self.effWriteMemory(esp - Const(20, self._psize), Const(4, self._psize), esp)
        self.effWriteMemory(esp - Const(24, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_EBP))
        self.effWriteMemory(esp - Const(28, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_ESI))
        self.effWriteMemory(esp - Const(32, self._psize), Const(4, self._psize), self.getRegObj(e_i386.REG_EDI))
        # FIXME re-order these!
        self.effSetVariable('esp', esp - Const(32, self._psize))

    def i_pushfd(self, op):
        esp = self.getRegObj(e_i386.REG_ESP)
        eflags = self.getRegObj(e_i386.REG_EFLAGS)
        self.effSetVariable('esp', esp - Const(4, self._psize))
        self.effWriteMemory(Var('esp', self._psize), Const(4, self._psize), eflags)

    def i_popad(self, op):
        esp = self.getRegObj(e_i386.REG_ESP)
        self.effSetVariable('edi', Mem(esp, Const(4, self._psize)))
        self.effSetVariable('esi', Mem(esp + Const(4, self._psize), Const(4, self._psize)))
        self.effSetVariable('ebp', Mem(esp + Const(8, self._psize), Const(4, self._psize)))
        self.effSetVariable('ebx', Mem(esp + Const(16, self._psize), Const(4, self._psize)))
        self.effSetVariable('edx', Mem(esp + Const(20, self._psize), Const(4, self._psize)))
        self.effSetVariable('ecx', Mem(esp + Const(24, self._psize), Const(4, self._psize)))
        self.effSetVariable('eax', Mem(esp + Const(28, self._psize), Const(4, self._psize)))
        self.effSetVariable('esp', esp + Const(32, self._psize))

    def i_ror(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, ((v1 >> v2) | (v1 << (Const(op.opers[0].tsize * 8, self._psize) - v2))))

        # XXX - set cf flag with last bit moved

    def i_rol(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        self.setOperObj(op, 0, ((v1 << v2) | (v1 >> (Const(op.opers[0].tsize * 8, self._psize) - v2))))
        # XXX - set cf flag with last bit moved

    def i_stosd(self, op):
        # eax = self.getRegObj(e_i386.REG_EAX)
        # edi = self.getRegObj(e_i386.REG_EDI)
        # FIXME omg segments in symboliks?
        # base,size = self.segments[SEG_ES]
        di = Var(self.__destp__, self._psize)
        self.effWriteMemory(di, Const(self._psize, self._psize), Var('eax', self._psize))
        # FIXME flags?
        # if self.getFlag(e_i386.EFLAGS_DF):
        # edi -= 4
        # else:
        # edi += 4
        # print 'FIXME DF IN stosd'
        di += Const(4, self._psize)
        self.effSetVariable(self.__destp__, di)


class i386ArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = i386SymbolikTranslator


class i386SymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = i386ArgDefSymEmu


class StdCall(i386SymCallingConv, e_i386.StdCall):
    pass


class Cdecl(i386SymCallingConv, e_i386.Cdecl):
    pass


class ThisCall(i386SymCallingConv, e_i386.ThisCall):
    pass


class MsFastCall(i386SymCallingConv, e_i386.MsFastCall):
    pass


class BFastCall(i386SymCallingConv, e_i386.BFastCall):
    pass


class i386SymFuncEmu(vsym_analysis.SymbolikFunctionEmulator):
    __width__ = 4

    # def __init__(self, vw, initial_sp=0xbfbff000):
    def __init__(self, vw):
        vsym_analysis.SymbolikFunctionEmulator.__init__(self, vw)
        self.setStackBase(0xbfbff000, 16384)

        self.addCallingConvention('cdecl', Cdecl())
        self.addCallingConvention('stdcall', StdCall())
        self.addCallingConvention('thiscall', ThisCall())
        self.addCallingConvention('bfastcall', BFastCall())
        self.addCallingConvention('msfastcall', MsFastCall())
        # FIXME possibly decide this by platform/format?
        self.addCallingConvention(None, Cdecl())

        self.addFunctionCallback('ntdll.eh_prolog', self._eh_prolog)
        self.addFunctionCallback('ntdll.seh3_prolog', self._seh3_prolog)
        self.addFunctionCallback('ntdll.seh3_epilog', self._seh3_epilog)
        self.addFunctionCallback('ntdll._alloca_probe', self.alloca_probe)

        # self.writeSymMemory( Mem(Var('fs') + 292, 4)

    def getStackCounter(self):
        return self.getSymVariable('esp')

    def setStackCounter(self, symobj):
        self.setSymVariable('esp', symobj)

    def _eh_prolog(self, emu, fname, argv):
        # swap out [ esp ] (saved eip) to ebp
        # and set ebp to current esp (std frame)
        ebp = emu.getSymVariable('ebp')
        esp = emu.getSymVariable('esp')
        eax = emu.getSymVariable('eax')
        emu.writeSymMemory(esp, ebp)
        emu.setSymVariable('ebp', esp)

        # now carry out 3 symbolik pushes
        esp -= Const(4, 4)
        emu.writeSymMemory(esp, Var('eh_ffffffff', 4))
        esp -= Const(4, 4)
        emu.writeSymMemory(esp, eax)
        esp -= Const(4, 4)
        emu.writeSymMemory(esp, Var('eh_c0c0c0c0', 4))
        self.setSymVariable('esp', esp)

        return eax

    def alloca_probe(self, emu, fname, argv):
        esp = emu.getSymVariable('esp')
        eax = emu.getSymVariable('eax')
        # Update the stack size if eax is discrete
        if eax.isDiscrete(emu=emu):
            stackadd = eax.solve(emu=emu)
            stackadd += 4096 - (stackadd % 4096)
            stacksize = emu.getStackSize()
            emu.setStackSize(stacksize + stackadd)

        emu.setSymVariable('esp', esp - eax)
        # if eax < 0x1000:
        # eax -= Const(4, self.__width__)
        # emu.setSymVariable('esp', esp-eax)
        # else:
        # while eax > 0x1000:
        # eax -= Const(0x1000, self.__width__)
        # emu.setSymVariable('esp', esp-Const(0x1000, self.__width__))
        # esp -= Const(0x1000, self.__width__)
        # emu.setSymVariable('esp', esp-eax)

    def _seh3_prolog(self, emu, fname, argv):
        scopetable, localsize = argv
        esp = emu.getSymVariable('esp')

        emu.writeSymMemory(esp + Const(4, self.__width__), emu.getSymVariable('ebp'))
        emu.writeSymMemory(esp, scopetable)
        emu.writeSymMemory(esp - Const(4, self.__width__), Var('ntdll.seh3_handler', 4))  # push
        emu.writeSymMemory(esp - Const(8, self.__width__), Var('saved_seh3_scopetable', 4))  # push
        emu.writeSymMemory(esp - Const(12, self.__width__), emu.getSymVariable('ebx'))
        emu.writeSymMemory(esp - Const(16, self.__width__), emu.getSymVariable('esi'))
        emu.writeSymMemory(esp - Const(20, self.__width__), emu.getSymVariable('edi'))
        emu.setSymVariable('esp', (esp - Const(20, self.__width__)) - localsize)
        emu.setSymVariable('ebp', (esp + Const(4, self.__width__)))

        return scopetable

    def _seh3_epilog(self, emu, fname, argv):
        edi = emu.getSymVariable('edi')
        esi = emu.getSymVariable('esi')
        ebx = emu.getSymVariable('ebx')

        esp = emu.getSymVariable('esp')
        # FIXME do seh restore...
        emu.setSymVariable('edi', edi)
        emu.setSymVariable('esi', esi)
        emu.setSymVariable('ebx', ebx)
        ebp = emu.getSymVariable('ebp')
        savedbp = emu.readSymMemory(ebp, Const(4, self.__width__))
        emu.setSymVariable('ebp', savedbp)
        emu.setSymVariable('esp', ebp + Const(4, self.__width__))
        return emu.getSymVariable('eax')


class i386SymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = i386SymbolikTranslator
    __emu__ = i386SymFuncEmu
