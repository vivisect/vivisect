import sys

import envi
import envi.bits as e_bits
import envi.archs.ppc as e_ppc
import envi.registers as e_registers

import vivisect.symboliks.analysis as vsym_analysis
import vivisect.symboliks.callconv as vsym_callconv
import vivisect.symboliks.emulator as vsym_emulator
import vivisect.symboliks.translator as vsym_trans

from envi.archs.ppc.const import *

from vivisect.const import *
from vivisect.symboliks.common import *
from vivisect.symboliks.archs.i386 import ArgDefSymEmu

from envi.archs.ppc.regs import * 

# a list of conditionals as pertain to the BI operand for conditional branches
conds = [crfld.replace('_','.').lower() for crfld, reg, boff, bsz, desc in e_ppc.statmetas if reg == e_ppc.REG_CR]

def MASK(b, e, psize=8):
    '''
    helper to create masks.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    #print("MASK( %r, %r )" % (b, e))
    delta = e - b + Const(1, psize)
    if delta.isDiscrete():
        e = e.solve()
        b = b.solve()
        if e < b:
            # b is greater than e, so we chop out the e/b bits and invert the mask
            delta = b - e - 1
            real_shift = 63 - b + 1
            #print(real_shift, delta)
            mask = e_bits.bu_maxes[delta] << real_shift
            mask ^= 0xffffffffffffffff
        else:
            # b is less than/equal to e, so we do normal mask
            delta = e - b + 1
            real_shift = 63 - e
            #print(real_shift, delta)
            mask = e_bits.bu_maxes[delta] << real_shift
        return Const(mask, psize)
    
    sym_shift = Const(63, psize) - e
    mask = (Const(1, psize) << delta) - Const(1, psize)
    return mask << (sym_shift)

def ROTL32(x, y, psize=8):
    '''
    helper to rotate left, 32-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    tmp = (x>>(Const(32, 8)-y))
    x |= (x<<Const(32, 8))
    x <<= y
    x |= tmp
    x &= Const(e_bits.u_maxes[psize], 8)
    return x
    
def ROTL64(x, y, psize=8):
    '''
    helper to rotate left, 32-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    tmp = (x>>(Const(64, 8)-y))
    x <<= y
    x |= tmp
    x &= Const(e_bits.u_maxes[psize], 8)
    return x
    
class PpcSymbolikTranslator(vsym_trans.SymbolikTranslator):
    '''
    Common parent for ppc32 and ppc64.  Make sure you define:
    __arch__, __ip__, __sp__, __srcp__, __destp__

    Symbolik representations that are 'agnostic' to 32 or 64-bit belong here.
    '''
    def __init__(self, vw):
        vsym_trans.SymbolikTranslator.__init__(self, vw)
        self._arch = self.__arch__()
        self._psize = self._arch.getPointerSize()
        self._reg_ctx = self._arch.archGetRegCtx()

    def translateOpcode(self, op):
        return vsym_trans.SymbolikTranslator.translateOpcode(self, op)

    def getRegObj(self, regidx):
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth / 8 )

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
        val = Var(rname, rbitwidth / 8 )

        # Translate to native if needed...
        if ridx != regidx:
            # we cannot call _xlateToNativReg since we'd pass in a symbolik
            # object that would trigger an or operation; the code in envi
            # obviously is NOT symboliks aware (2nd op in | operation is NOT
            # a symbolik); so we do it manually here since we are symbolik
            # aware.
            #obj = self._reg_ctx._xlateToNativeReg(regidx, obj)
            basemask = (2**rbitwidth) - 1
            rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
            # cut hole in mask
            finalmask = basemask ^ (mask << lshift)
            if lshift != 0:
                obj <<= Const(lshift, rbitwidth / 8)

            obj = obj | (val & Const(finalmask, rbitwidth / 8))

        self.effSetVariable(rname, obj)

    def getFlagObj(self, regidx):
        ridx = regidx & 0xffff
        rbase = self._reg_ctx.getRegisterName(ridx)
        rflag = self._reg_ctx.getRegisterName(regidx)

        rname = ('%s.%s' % (rbase, rflag)).lower()
        return Var(rname, 1)


    def setFlagObj(self, regidx, obj):
        ridx = regidx & 0xffff
        rbase = self._reg_ctx.getRegisterName(ridx)
        rflag = self._reg_ctx.getRegisterName(regidx)

        rname = ('%s.%s' % (rbase, rflag)).lower()

        self.effSetVariable(rname, obj)

    def getOperAddrObj(self, op, idx):
        oper = op.opers[idx]
        #seg = getSegmentSymbol(op)

        if isinstance(oper, e_ppc.PpcMemOper):
            reg = Var(self._reg_ctx.getRegisterName(oper.base_reg), oper.tsize)
            if oper.offset == 0:
                base = reg
            if oper.offset > 0:
                base = o_add(reg, Const(oper.offset, self._psize), self._psize)
            if oper.offset < 0:
                base = o_sub(reg, Const(abs(oper.offset), self._psize), self._psize)

            #if seg:
            #    return o_add(seg, base, self._psize)

            return base

    def getOperObj(self, op, idx):
        '''
        Translate the specified operand to a symbol compatible with
        the symbolic translation system.
        '''

        # FIXME: !!! CR and XER bits not accessed correctly
        oper = op.opers[idx]
        if oper.isReg():
            # CHECK FOR PARTS OF CR and XER
            if oper.reg == REG_CR:
                return Var(oper.repr(op, simple=False), 1)

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
            # CHECK FOR PARTS OF CR and XER
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


    def i_b(self, op):
        tgt = self.getOperObj(op, 0)
        if not tgt.isDiscrete():
            # indirect jmp... table!

            return [( Const(tgt, self._psize), eq(tgt, Const(tva, self._psize)) ) for fr,tva,tp,flag in self.vw.getXrefsFrom(op.va) if tp == REF_CODE]


    def i_blr(self, op):
        '''
        blr is actually "ret"
        '''
        self.effSetVariable(self.__ip__, Var('LR', self._psize))
        #return [ self.getRegObj(REG_LR), ]

    def i_bctrl(self, op):
        targ = Var('CTR', self._psize)
        self.effFofX(targ)


    # conditional branches....
    def _cond_jmp(self, op, aa=0, lk=0, tgtreg=None):
        # get the conditional...
        bi = op.getOperObj(1)
        condflag = conds[bi]
        cond = Var(condflag, 1)

        # setup the target symbol
        if tgtreg is None:
            # target is the bd * 4
            bd = op.getOperObj(2) << 2

            # if not "absolute", add cur va
            if aa == 0:
                bd += op.va

            # tgtsym is a constant
            tgtsym = Const(bd, self._psize)

        else:
            # tgtsym is a Reg:
            tgtsym = Var(tgtreg, self._psize)

        # Construct the tuple for the conditional jump
        if lk:
            self.setRegObj(REG_LR, Const(op.va + len(op), self._psize))

        return (
                ( tgtsym, cond ),
                ( Const(op.va + len(op), self._psize), cnot(cond)), 
               )

    def i_bc(self, op, aa=0, lk=0):
        return self._cond_jmp(op, aa=0, lk=0)

    def i_bca(self, op):
        return self._cond_jmp(op, aa=1, lk=0)

    def i_bcl(self, op):
        return self._cond_jmp(op, aa=0, lk=1)

    def i_bcla(self, op):
        return self._cond_jmp(op, aa=1, lk=1)

    def i_bclr(self, op):
        return self._cond_jmp(op, aa=1, lk=1, tgtreg='LR')

    def i_bcctr(self, op):
        return self._cond_jmp(op, aa=1, lk=1, tgtreg='ctr')

    def i_bdnzf(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdzf(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bf(self, op):
        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = testbit
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzt(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdzt(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bt(self, op):
        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = testbit
        print(op, repr(tgtva), repr(constraint))
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
            )

    def i_bdnz(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        tgtva = self.getOperObj(op, 1)
        constraint = ne(ctr, Const(0, self._psize))
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdz(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        tgtva = self.getOperObj(op, 1)
        constraint = eq(ctr, Const(0, self._psize))
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzfl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdzfl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bfl(self, op):
        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnztl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdztl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_btl(self, op):
        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = testbit
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = self.getOperObj(op, 0)
        tgtva = self.getOperObj(op, 1)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdzl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        tgtva = self.getOperObj(op, 1)
        constraint = eq(ctr, Const(0, self._psize)) 
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bl(self, op):
        self.setRegObj(REG_LR, Const(op.va+len(op), self._psize))
        # For now, calling means finding which of our symbols go in
        # and logging what comes out.
        targ = self.getOperObj(op, 0)
        self.effFofX(targ)
        return 

    i_bdnzfa = i_bdnzf
    i_bdzfa = i_bdzf
    i_bfa = i_bf
    i_bdnzta = i_bdnzt
    i_bdzta = i_bdzt
    i_bta = i_bt
    i_bdnza = i_bdnz
    i_bdza = i_bdz
    i_bla = i_bl

    i_bdnzfla = i_bdnzfl
    i_bdzfla = i_bdzfl
    i_bfla = i_bfl
    i_bdnztla = i_bdnztl
    i_bdztla = i_bdztl
    i_btla = i_btl
    i_bdnzla = i_bdnzl
    i_bdzla = i_bdzl

    ##### LR branches
    def i_bdnzflr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdzflr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bflr(self, op):
        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = testbit
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
    def i_bdnztlr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdztlr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_btlr(self, op):
        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = testbit
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzlr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)
        
        tgtva = self.getRegObj(REG_LR)
        constraint = ne(ctr, Const(0, self._psize))
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdzlr(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        tgtva = self.getRegObj(REG_LR)
        constraint = eq(ctr, Const(0, self._psize))
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzflrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdzflrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)

        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bflrl(self, op):
        testbit = cnot(self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = testbit
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_bdnztlrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)
        
        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(ne(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdztlrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)
        
        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = o_and(eq(ctr, Const(0, self._psize)) , testbit)
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )
           
    def i_btlrl(self, op):
        testbit = (self.getOperObj(op, 0))
        tgtva = self.getRegObj(REG_LR)
        constraint = testbit
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdnzlrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)
        
        tgtva = self.getRegObj(REG_LR)
        constraint = ne(ctr, Const(0, self._psize))
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_bdzlrl(self, op):
        ctr = self.getRegObj(REG_CTR)
        ctr -= 1
        self.setRegObj(REG_CTR, ctr)
        
        tgtva = self.getRegObj(REG_LR)
        constraint = eq(ctr, Const(0, self._psize))
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return (
                ( tgtva, constraint), 
                ( Const(op.va + len(op), self._psize), cnot(constraint))
                )

    def i_blrl(self, op):
        tgtva = self.getRegObj(REG_LR)
        constraint = eq(ctr, Const(0, self._psize))
        print("FIXME: PPC Symboliks bd...l must update the graph ")
        return [
                ( tgtva, constraint), 
                ]


    i_bdnzfa = i_bdnzflr
    i_bdzfa = i_bdzflr
    i_bfa = i_bflr
    i_bdnzta = i_bdnztlr
    i_bdzta = i_bdztlr
    i_bta = i_btlr
    i_bdnza = i_bdnzlr
    i_bdza = i_bdzlr
    i_bla = i_blrl

    i_bdnzfla = i_bdnzfl
    i_bdzfla = i_bdzfl
    i_bfla = i_bfl
    i_bdnztla = i_bdnztl
    i_bdztla = i_bdztl
    i_btla = i_btl
    i_bdnzla = i_bdnzl
    i_bdzla = i_bdzl

    def i_sync(self, op):
        self.effSetVariable('sync', Const(op.va, self._psize))

    def i_isync(self, op):
        self.effSetVariable('isync', Const(op.va, self._psize))

    ######################## arithmetic instructions ##########################
    def i_cmpw(self, op, L=0): # L != l.  l means logical, L means LONG
        # signed comparison for cmpli and cmpl
        if len(op.opers) == 3:
            croff = op.opers[0].field * 4
            raidx = 1
            rbidx = 2
        else:
            croff = 0
            raidx = 0
            rbidx = 1

        rA = self.getOperObj(op, raidx)
        rB = self.getOperObj(op, rbidx)
        dsize = op.opers[raidx].tsize
        ssize = op.opers[rbidx].tsize

        if L==0:
            a = o_sextend(rA, Const(self._psize, self._psize))
            b = o_sextend(rB, Const(self._psize, self._psize))
        else:
            a = rA
            b = rB
        SO = self.getFlagObj(REG_SO)

        # setting the flags...
        self.effSetVariable(conds[croff + 0], lt(a, b))
        self.effSetVariable(conds[croff + 1], gt(a, b))
        self.effSetVariable(conds[croff + 2], eq(a, b))
        self.effSetVariable(conds[croff + 3], SO)

    i_cmpwi = i_cmpw

    def i_cmplw(self, op, L=0): # L != l.  l means logical, L means LONG
        # unsigned comparison for cmpli and cmpl
        if len(op.opers) == 3:
            croff = op.opers[0].field * 4
            raidx = 1
            rbidx = 2
        else:
            croff = 0
            raidx = 0
            rbidx = 1

        rA = self.getOperObj(op, raidx)
        rB = self.getOperObj(op, rbidx)
        dsize = op.opers[raidx].tsize
        ssize = op.opers[rbidx].tsize

        if L==0:    # hmmm... is this even a thing with symboliks?? - dsize should be correct in decoding ( #TESTME: !)
            a = rA
            b = rB
        else:
            a = rA
            b = rB
        SO = self.getFlagObj(REG_SO) 

        # setting the flags...
        self.effSetVariable(conds[croff + 0], gt(a, b))
        self.effSetVariable(conds[croff + 1], lt(a, b))
        self.effSetVariable(conds[croff + 2], eq(a, b))
        self.effSetVariable(conds[croff + 3], SO)

    i_cmplwi = i_cmplw

    def i_cmpdi(self, op):
        return self.i_cmpwi(op, L=1)

    def i_cmpd(self, op):
        return self.i_cmpw(op, L=1)

    def i_cmpld(self, op):
        return self.i_cmplw(op, L=1)

    def i_cmpldi(self, op):
        return self.i_cmplwi(op, L=1)


    #===============        #SYMBOLIKSIZE!
    def getCarryBitAtX(bit, result, add0, add1):
        '''
        return the carry bit at bit x.
        algorithm: check the next higher bit for result and add0+add1.  
            if they ==, carry is 0  
            if they !=, carry is 1
        '''
        bit += 1
        rb = (result >> bit) & 1
        a0b = (add0 >> bit) & 1
        a1b = (add1 >> bit) & 1
        return rb != (a0b + a1b)

    def setOEflags(self, result, size, add0, add1):
        cm = getCarryBitAtX(size*8, result, add0, add1)
        cm1 = getCarryBitAtX(size*8+1, result, add0, add1)
        ov = cm ^ cm1

        so |= ov

        self.setFlagObj(REG_SO, so)
        self.setFlagObj(REG_OV, ov)

    def setFlags(self, result, crf=0, so=None, size=8):
        croff = crf * 4

        b = Const(0, self._psize)
        
        if so == None:
            so = self.getFlagObj(REG_SO) 

        # setting the flags...
        self.effSetVariable(conds[croff + 0], lt(result, b))
        self.effSetVariable(conds[croff + 1], gt(result, b))
        self.effSetVariable(conds[croff + 2], eq(result, b))

    ######################## arithmetic instructions ##########################
    def i_add(self, op, oe=False):
        '''
        add
        '''
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2)
        src2 = o_sextend(src2, Const(self._psize, self._psize))
        result = src1 + src2
        self.setOperObj(op, 0, result)
        if oe: self.setOEFlags(result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addo(self, op):
        return self.i_add(op, oe=True)

    def i_addc(self, op, oe=False):
        '''
        add
        '''
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2) # FIXME: move signedness here instead of at decode
        src2 = o_sextend(src2, Const(self._psize, self._psize))

        result = src1 + src2
        
        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)
        if oe: self.setOEFlags(result)

    def i_addco(self, op):
        return self.i_addc(op, oe=True)

    def i_adde(self, op, oe=False):
        ra = self.getOperObj(op, 1)
        rb = self.getOperObj(op, 2)
        ca = Var('ca', 1)

        bplus = rb + ca
        result = ra + bplus

        if oe: self.setOEflags(result, self.psize, ra, bplus)
        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperObj(op, 0, result)

    def i_addeo(self, op):
        return self.i_adde(op, oe=True)

    i_addi = i_add

    def i_addis(self, op):
        '''
        add immediate shifted
        '''
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2)
        src2 <<= Const(16, self._psize)
        src2 = o_sextend(src2, Const(self._psize, self._psize))

        result = src1 + src2
        self.setOperObj(op, 0, result)

    def i_addic(self, op):
        '''
        add immediate carry
        update flags (if IF_RC)
        '''
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2)
        src2 = o_sextend(src2, Const(self._psize, self._psize))
        result = src1 + src2

        self.setOperObj(op, 0, result)
        self.setFlagObj(REG_CA, gt(src2, src1))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addme(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperObj(op, 1)
        src2 = 0xffffffffffffffff
        result = src1 + src2

        self.setOperObj(op, 0, result)

        self.setFlagObj(REG_CA, gt(src2, src1))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addmeo(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperObj(op, 1)
        src2 = Const(0xffffffffffffffff, 8)
        result = src1 + src2

        self.setOperObj(op, 0, result)

        self.setFlagObj(REG_CA, gt(src2, src1))
        self.setOEflags(result, 4, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addw(self, op):
        '''
        add word
        '''
        src1 = self.getOperObj(op, 1)
        src1 = o_sextend(src1, Const(self._psize, self._psize))
        src2 = self.getOperObj(op, 2)
        src2 = o_sextend(src2, Const(self._psize, self._psize))
        result = src1 + src2
        self.setOperObj(op, 0, result)
   
    def i_addwss(self, op):
        '''
        add word
        '''
        src1 = self.getOperObj(op, 1)
        src1 = o_sextend(src1, self._psize)
        src2 = self.getOperObj(op, 2)
        src2 = o_sextend(src2, self._psize)
        result = src1 + src2

        SO = self.getFlagObj(REG_SO)
        sum31 = ((result >> Const(32, self._psize)) & Const(1, self._psize))
        sum32 = ((result >> Const(31, self._psize)) & Const(1, self._psize)) 
        OV = sum31 ^ sum32
        if OV:
            if sum31: 
                result = Const(0x80000000, 4)
            else:
                result = Const(0x7fffffff, 4)
            SO = SO | OV

        self.setOperObj(op, 0, result)
        self.setFlags(result, 0, SO)
  
    def i_and(self, op):
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        result = (dst & src)

        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_andi = i_and

    def i_andis(self, op):
        '''
        and immediate shifted
        '''
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2) # FIXME: move signedness here instead of at decode
        src2 <<= Const(16, self._psize)

        result = src1 & src2
        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_andc(self, op):
        '''
        and "complement"
        '''
        ssize = op.opers[1].tsize
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1) ^ e_bits.u_maxes[ssize]
        
        result = (dst & src)

        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_or(self, op):
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)

        result = (dst | src)
        
        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_ori = i_or

    def i_oris(self, op):
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        src <<= Const(16, self._psize)

        self.setOperObj(op, 0, (dst | src))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_orc(self, op):
        dst = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        src = -src

        self.setOperObj(op, 0, (dst | src))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    ########################## LOAD/STORE INSTRUCTIONS ################################
    # lbz and lbzu access memory directly from operand[1]
    def i_lbz(self, op):
        op.opers[1].tsize = 1
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    def i_lbzu(self, op):
        op.opers[1].tsize = 1
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lbze = i_lbz
    i_lbzue = i_lbzu

    # lbzx and lbzux load an address by adding operand[1] and operand[2]
    def i_lbzx(self, op):
        op.opers[1].tsize = 1
        src = self.getOperObj(op, 1)
        src += self.getOperObj(op, 2)
        val = self.effReadMemory(src, Const(1, self._psize))
        self.setOperObj(op, 0, val)

    def i_lbzux(self, op):
        op.opers[1].tsize = 1
        src = self.getOperObj(op, 1)
        src += self.getOperObj(op, 2)
        val = self.effReadMemory(src, Const(1, self._psize))
        self.setOperObj(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lbzxe = i_lbzx
    i_lbzuxe = i_lbzux

    # lhz and lhzu access memory directly from operand[1]
    def i_lhz(self, op):
        op.opers[1].tsize = 2
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    def i_lhzu(self, op):
        op.opers[1].tsize = 2
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lhze = i_lhz
    i_lhzue = i_lhzu

    # lhzx and lhzux load an address by adding operand[1] and operand[2]
    def i_lhzx(self, op):
        src = self.getOperObj(op, 1)
        src += o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))
        val = self.effReadMemory(src, Const(2, self._psize))
        self.setOperObj(op, 0, val)

    def i_lhzux(self, op):
        src = self.getOperObj(op, 1)
        src += self.getOperObj(op, 2)
        src += o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))
        val = self.effReadMemory(src, Const(2, self._psize))
        self.setOperObj(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lhzxe = i_lhzx
    i_lhzuxe = i_lhzux


    # lwz and lwzu access memory directly from operand[1]
    def i_lwz(self, op):
        op.opers[1].tsize = 4
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    def i_lwzu(self, op):
        op.opers[1].tsize = 4
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lwze = i_lwz
    i_lwzue = i_lwzu

    # lwzx and lwzux load an address by adding operand[1] and operand[2]
    def i_lwzx(self, op):
        src = self.getOperObj(op, 1)
        src += o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))
        val = self.effReadMemory(src, Const(4, self._psize))
        self.setOperObj(op, 0, val)

    def i_lwzux(self, op):
        src = self.getOperObj(op, 1)
        src += self.getOperObj(op, 2)
        src += o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))
        val = self.effReadMemory(src, Const(4, self._psize))
        self.setOperObj(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)

    i_lwzxe = i_lwzx
    i_lwzuxe = i_lwzux


    def i_lmw(self, op):
        startreg = op.opers[0].reg
        regcnt = 32-startreg

        startaddr = self.getOperAddrObj(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            addrsym = startaddr + Const(offset, self._psize)
            word = self.effReadMemory(addrsym, Const(4, self._psize))
            self.setRegObj(regidx, word)
            offset += 4

    def i_stmw(self, op):
        op.opers[1].tsize = 4
        startreg = op.opers[0].reg
        regcnt = 32-startreg

        startaddr = self.getOperAddrObj(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            word = self.getRegObj(regidx)
            addrsym = startaddr + Const(offset, self._psize)
            self.effWriteMemory(addrsym, Const(4, self._psize), word)
            offset += 4
    
    def i_stb(self, op, size=1):
        op.opers[1].tsize = size
        src = self.getOperObj(op, 0)
        self.setOperObj(op, 1, src)
   
    def i_sth(self, op):
        return self.i_stb(op, size=2)

    def i_stw(self, op):
        return self.i_stb(op, size=4)

    def i_std(self, op):
        return self.i_stb(op, size=8)


    def i_stbu(self, op, size=1):
        op.opers[1].tsize = size
        src = self.getOperObj(op, 0)
        self.setOperObj(op, 1, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateRegObj(self)
    
    def i_sthu(self, op):
        return self.i_stbu(op, size=2)

    def i_stwu(self, op):
        return self.i_stbu(op, size=4)

    def i_stdu(self, op):
        return self.i_stbu(op, size=8)


    def i_stbx(self, op, size=1):
        val = self.getOperObj(op, 0)
        src = self.getOperObj(op, 1)
        src += self.getOperObj(op, 2)
        self.effWriteMemory(src, Const(size, self._psize), val)
        self.setOperObj(op, 1, src)

    def i_sthx(self, op):
        return self.i_stbx(op, size=2)

    def i_stwx(self, op):
        return self.i_stbx(op, size=4)

    def i_stdx(self, op):
        return self.i_stbx(op, size=8)

    # mov instructions
    def i_movfrom(self, op):
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    def i_mov(self, op):
        src = self.getOperObj(op, 0)
        self.setOperObj(op, 1, src)

    def i_mflr(self, op):
        src = self.getRegObj(REG_LR)
        self.setOperObj(op, 0, src)

    def i_mtlr(self, op):
        src = self.getOperObj(op, 0)
        self.setRegObj(REG_LR, src)

    def i_mfmsr(self, op):
        src = self.getRegObj(REG_MSR)# & Const(0xffffffff, self._psize)
        self.setOperObj(op, 0, src)

    def i_mtmsr(self, op):
        src = self.getOperObj(op, 0) & Const(0xffffffff, self._psize)
        self.setRegObj(REG_MSR, src)

    def i_mfspr(self, op):
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    def i_mtspr(self, op):
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, src)

    i_li = i_movfrom
    i_mr = i_movfrom

    def i_lis(self, op):
        src = self.getOperObj(op, 1)
        self.setOperObj(op, 0, (src<<Const(16, self._psize)))

    def i_rlwimi(self, op):
        n = self.getOperObj(op, 2) & Const(0x1f, self._psize)
        b = self.getOperObj(op, 3) + Const(32, self._psize)
        e = self.getOperObj(op, 4) + Const(32, self._psize)
        ra = self.getOperObj(op, 0)

        r = ROTL32(self.getOperObj(op, 1), n)
        k = MASK(b, e)

        result = (r & k) | (ra & cnot(k))

        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        
    def i_rlwnm(self, op):
        n = self.getOperObj(op, 2) & Const(0x1f, self._psize)
        b = self.getOperObj(op, 3) + Const(32, self._psize)
        e = self.getOperObj(op, 4) + Const(32, self._psize)
        ra = self.getOperObj(op, 0)

        r = ROTL32(self.getOperObj(op, 1), n)
        k = MASK(b, e)

        result = r & k
        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_rlwinm = i_rlwnm

    def i_rlwinm_old(self, op):
        rs = self.getOperObj(op, 1)
        sh = self.getOperObj(op, 2)
        mb = self.getOperObj(op, 3)
        me = self.getOperObj(op, 4)

        r = (rs << sh) | (rs >> (Const(32, self._psize) - sh))
        numbits = me - mb
        k = e_bits.bu_masks[numbits] << mb

        result = r & k
        self.setOperObj(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_srawi(self, op, size=4):
        rs = self.getOperValue(op, 1)
        n = self.getOperObj(op, 2) & Const(0x1f, self._psize)   # FIXME: is the &... necessary for symboliks?

        k = MASK(n+Const(32, self._psize), Const(63, self._psize))
        r = ROTL32(rs, Const(64, self._psize)-n)

        # symbolikally generate the signed mask (based on bit 31)
        s = (rs >> Const(31, self._psize)) & Const(1, self._psize)
        s *= Const(0xffffffff, self._psize)

        notk = cnot(k)
        result = (r & k) | (s & notk)

        self.setOperObj(op, 0, result)

        carry = o_and(s, ((r & notk)))
        self.setFlagObj(REG_CA, carry)
        
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_sraw(self, op, size=4):
        '''
        shift right algebraic word
        '''
        # this shit has no resemblance to the docs... but the docs are wonky symbolikcally.  
        # this should mean the same thing, and have significantly reduced "added" effects.
        rb = self.getOperObj(op, 2)
        rs = self.getOperObj(op, 1)

        n = rb & Const(0x1f, self._psize)
        r = rs >> n
        signbits = MASK(Const(0, self._psize), n + Const(32, self._psize))

        s = o_and(rb >> Const(32, self._psize), Const(1, self._psize), self._psize)

        result = r | (s * signbits)

        self.setOperObj(op, 0, result)

        carry = o_and((s << n) - Const(1, 8), (r & MASK(Const(63, 8) - n, Const(63, 8))), 8)
        self.setFlagObj(REG_CA, carry)
        
        if op.iflags & IF_RC: self.setFlags(result, 0, size=size)


    #===== NEEDS WORK ==========
    def i_srw(self, op):
        rb = self.getOperObj(op, 2)
        rs = self.getOperObj(op, 1)

        n = rb & Const(0x3f, self._psize)

        result = rs >> n

        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperObj(op, 0, result)
        print("srw: rb: %x  rs: %x  result: %x" % (rb, rs, result))

    def i_srd(self, op):
        rb = self.getOperObj(op, 2)
        rs = self.getOperObj(op, 1)

        n = rb & Const(0x7f, self._psize)

        result = rs >> n

        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperObj(op, 0, result)

    def i_slw(self, op):
        rb = self.getOperObj(op, 2)
        rs = self.getOperObj(op, 1)

        n = rb & Const(0x1f, self._psize)

        result = (rs << n) & Const(0xffffffff, self._psize)

        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperObj(op, 0, result)

    def i_lha(self, op):
        src = o_sextend(self.getOperObj(op, 1), Const(self._psize, self._psize))
        self.setOperObj(op, 0, src & 0xffffffffffffffff)
        

    def i_twi(self, op):
        TO = self.getOperObj(op, 0)
        rA = self.getOperObj(op, 1)
        asize = op.opers[1].tsize
        SIMM = self.getOperObj(op, 2)

        if TO & 1 and o_sextend(rA, Const(self._psize, self._psize)) < o_sextend(SIMM, Const(self._psize, self._psize)):
            #TRAP
            self.trap(op)
        if TO & 2 and o_sextend(rA, Const(self._psize, self._psize)) > o_sextend(SIMM, Const(self._psize, self._psize)):
            #TRAP
            self.trap(op)
        if TO & 4 and rA == SIMM:
            #TRAP
            self.trap(op)
        if TO & 8 and rA > SIMM:
            #TRAP
            self.trap(op)
        if TO & 10 and rA > SIMM:
            #TRAP
            self.trap(op)

    def i_mulld(self, op, size=8):
        ra = self.getOperObj(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperObj(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getFlagObj(REG_SO) 
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegObj(REG_SO, so)
            self.setRegObj(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperObj(op, 0, prod & e_bits.u_maxes[size])


    def i_mullw(self, op, size=4, oe=False):
        ra = self.getOperObj(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperObj(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getFlagObj(REG_SO) 
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegObj(REG_SO, so)
            self.setRegObj(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperObj(op, 0, prod)

    def i_mullwo(self, op):
        return self.i_mullw(oe=True)

    def i_mulli(self, op):
        dsize = op.opers[0].tsize
        s1size = op.opers[1].tsize
        src1 = o_sextend(self.getOperObj(op, 1), Const(self._psize, self._psize))
        src2 = o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))

        result = (src1 * src2) & Const(e_bits.u_maxes[dsize], self._psize)

        self.setOperObj(op, 0, result)

    def i_divw(self, op, oe=False):
        dividend = o_sextend(self.getOperObj(op, 1), Const(self._psize, self._psize))
        divisor = o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))
        
        if (dividend == -0x80000000 and divisor == -1):
            quotient = 0x7fffffff

        elif divisor == 0:
            if divisor >= 0:
                quotient = 0x7fffffff
            elif divisor < 0:
                quotient = 0x80000000

            ov = 1

        else:
            quotient = dividend / divisor
            ov = 0

        so = self.getFlagObj(REG_SO) 
        if oe:
            so |= ov
            self.setRegObj(REG_OV, ov)
            self.setRegObj(REG_SO, so)

        if op.iflags & IF_RC: 
            if self.psize == 8:
                self.setRegObj(REG_CR0, so)
            else:
                self.setFlags(result, so)

        self.setOperObj(op, 0, quotient)

    def i_divwu(self, op, oe=False):
        dividend = self.getOperObj(op, 1)
        divisor = self.getOperObj(op, 2)
        
        if divisor == 0:
            quotient = 0xffffffff
            ov = 1

        else:
            quotient = dividend / divisor

            ov = 0

        so = self.getFlagObj(REG_SO) 
        if oe:
            so |= ov
            self.setRegObj(REG_OV, ov)
            self.setRegObj(REG_SO, so)

        if op.iflags & IF_RC: 
            if self.psize == 8:
                self.setRegObj(REG_CR0, so)
            else:
                self.setFlags(result, so)

        self.setOperObj(op, 0, quotient)

    def i_divwuo(self, op):
        return self.i_divwu(op, oe=True)

    def i_mfcr(self, op):
        cr = self.getRegObj(REG_CR)
        self.setOperObj(op, 0, cr & 0xffffffff)


    def _base_sub(self, op, oeflags=False, setcarry=False, addone=1, size=4):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        ra = self.getOperObj(op, 1)
        rb = self.getOperObj(op, 2)

        ra ^= Const(e_bits.u_maxes[asize], self._psize) # 1's complement
        result = ra + rb + addone
        ures = result & Const(e_bits.u_maxes[dsize], self._psize)
        sres = o_sextend(ures, Const(self._psize, self._psize))
        self.setOperObj(op, 0, sres & Const(e_bits.u_maxes[dsize]. self._psize))
        
        if oeflags: self.setOEflags(result, size, ra, rb+1)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        if setcarry:
            carry = ne(result >> Const(dsize * 8, self._psize), Const(0,8))
            self.setFlagObj(REG_CA, carry)

    def i_subf(self, op):
        result = self._base_sub(op)

    def i_subfo(self, op):
        result = self._base_sub(op, oeflags=True)

    def i_subfb(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        bsize = op.opers[2].tsize

        ra = e_bits.sign_extend(self.getOperObj(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = o_sextend(ra, Const(self._psize, self._psize))

        rb = e_bits.sign_extend(self.getOperObj(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]
        self.setOperObj(op, 0, ures & e_bits.u_maxes[dsize])
        
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_subfbss(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        bsize = op.opers[2].tsize

        ra = e_bits.sign_extend(self.getOperObj(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = o_sextend(ra, Const(self._psize, self._psize))

        rb = e_bits.sign_extend(self.getOperObj(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]

        # flag magic
        so = self.getFlagObj(REG_SO) 
        sum55 = (result>>(size*8))&1
        sum56 = (result>>(size*8-1))&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov
        
        self.setRegObj(REG_OV, ov)
        self.setRegObj(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, 0, SO=so)

        self.setOperObj(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfbu(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize

        ra = self.getOperObj(op, 1) & e_bits.u_maxes[size]     # EXTZ... zero-extended
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = o_sextend(ra, Const(self._psize, self._psize))

        rb = self.getOperObj(op, 2) & e_bits.u_maxes[size] 

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size] 
        self.setOperObj(op, 0, ures & e_bits.u_maxes[dsize])

        if op.iflags & IF_RC: self.setFlags(result, 0)  # FIXME: bit-size correctness

    def i_subfbus(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize

        ra = self.getOperObj(op, 1) & e_bits.u_maxes[size]    # EXTZ... zero-extended
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = o_sextend(ra, Const(self._psize, self._psize))

        rb = self.getOperObj(op, 2) & e_bits.u_maxes[size]

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size] 

        # flag magic
        so = self.getFlagObj(REG_SO) 
        sum55 = (result>>8)&1
        sum56 = (result>>7)&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov
        
        self.setRegObj(REG_OV, ov)
        self.setRegObj(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, 0, SO=so)

        self.setOperObj(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfc(self, op, oeflags=False):
        self._base_sub(op, oeflags=False, setcarry=True)

    def i_subfco(self, op):
        self._base_sub(op, oeflags=True, setcarry=True)

    def i_subfe(self, op):
        addone = Var('ca', 1)
        self._base_sub(op, oeflags=False, setcarry=True, addone=addone)

    def i_subfeo(self, op):
        addone = Var('ca', 1)
        self._base_sub(op, oeflags=True, setcarry=True, addone=addone)

    def i_subfh(self, op):
        self.i_subfb(op, 2)

    def i_subfhss(self, op):
        self.i_subfbss(op, 2)

    def i_subfhu(self, op):
        self.i_subfbu(op, 2)

    def i_subfhus(self, op):
        self.i_subfbus(op, 2)

    def i_subfic(self, op):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        immsize = 16
        ra = self.getOperObj(op, 1)
        simm = o_sextend(self.getOperObj(op, 2), Const(self._psize, self._psize))

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + simm + 1
        ures = result & e_bits.u_maxes[dsize]
        
        carry = bool(result & (e_bits.u_maxes[dsize] + 1))
        self.setFlagObj(REG_CA, carry)

    def _subme(self, op, size=4, addone=1, oeflags=False):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        ra = self.getOperObj(op, 1)
        rb = 0xffffffffffffffff

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + rb + addone
        ures = result & e_bits.u_maxes[dsize]
        sres = o_sextend(ures, Const(self._psize, self._psize))
        self.setOperObj(op, 0, sres & e_bits.u_maxes[dsize])
        
        if oeflags: self.setOEflags(result, size, ra, rb+1)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        carry = bool(result & (e_bits.u_maxes[dsize] + 1))
        self.setFlagObj(REG_CA, carry)

    def i_subfme(self, op, size=4, addone=1):
        ca = Var('ca', 1)
        self._subme(op, size, ca)

    def i_subfmeo(self, op, size=4, addone=1):
        ca = Var('ca', 1)
        self._subme(op, size, ca, oeflags=True)

    def i_subfw(self, op):
        self.i_subfb(op, 4)

    def i_subfwss(self, op):
        self.i_subfbss(op, 4)

    def i_subfwu(self, op):
        self.i_subfbu(op, 4)

    def i_subfwus(self, op):
        self.i_subfbus(op, 4)


    # VLE instructions
    i_e_li = i_li
    i_e_lis = i_lis
    i_se_mflr = i_mflr
    i_se_mtlr = i_mtlr
    i_e_stwu = i_stwu
    i_e_stmw = i_stmw
    i_e_lmw = i_lmw
    i_se_mr = i_mr
    i_se_or = i_or
    i_e_ori = i_ori
    i_e_or2i = i_ori
    i_e_or2is = i_oris

    def i_neg(self, op, oe=False):
        ra = self.getOperObj(op, 1)
        result = ~ra + 1

        if oe:
            if self.psize == 4 and ra & 0xffffffff == 0x80000000:
                ov = 1
                so = ov
                self.setRegObj(REG_OV, ov)
                self.setRegObj(REG_SO, so)

            elif self.psize == 8 and ra == 0x8000000000000000:
                ov = 1
                so = ov
                self.setRegObj(REG_OV, ov)
                self.setRegObj(REG_SO, so)
            else:
                ov = 0
                so = self.getFlagObj(REG_SO) 

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperObj(op, 0, result)

    def i_nego(self, op):
        return self.i_neg(op, oe=True)

flagvars = []
for cr in range(8):
    for flag in ('lt', 'gt', 'eq', 'so'):
        flagvars.append('cr%d_%s' % (cr, flag))


# SymbolikTranslators
class Ppc32EmbeddedSymbolikTranslator(PpcSymbolikTranslator):
    psize = 4
    __arch__ = e_ppc.Ppc32EmbeddedModule
    __ip__ = 'pc' # we could use regctx.getRegObjName if we want.
    __sp__ = 'sp' # we could use regctx.getRegObjName if we want.

class Ppc64EmbeddedSymbolikTranslator(PpcSymbolikTranslator):
    psize = 8
    __arch__ = e_ppc.Ppc64EmbeddedModule
    __ip__ = 'pc' # we could use regctx.getRegObjName if we want.
    __sp__ = 'sp' # we could use regctx.getRegObjName if we want.

class PpcVleSymbolikTranslator(Ppc64EmbeddedSymbolikTranslator):
    __arch__ = e_ppc.PpcVleModule

class Ppc32ServerSymbolikTranslator(PpcSymbolikTranslator):
    psize = 4
    __arch__ = e_ppc.Ppc32ServerModule
    __ip__ = 'pc' # we could use regctx.getRegObjName if we want.
    __sp__ = 'sp' # we could use regctx.getRegObjName if we want.

class Ppc64ServerSymbolikTranslator(PpcSymbolikTranslator):
    psize = 8
    __arch__ = e_ppc.Ppc64ServerModule
    __ip__ = 'pc' # we could use regctx.getRegObjName if we want.
    __sp__ = 'sp' # we could use regctx.getRegObjName if we want.


# ArgDefSymEmus
class Ppc32EmbeddedArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = Ppc32EmbeddedSymbolikTranslator

class Ppc64EmbeddedArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = Ppc64EmbeddedSymbolikTranslator

class Ppc32ServerArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = Ppc32ServerSymbolikTranslator

class Ppc64ServerArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = Ppc64ServerSymbolikTranslator


# SymCallingConvs
class Ppc32EmbeddedSymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = Ppc32EmbeddedArgDefSymEmu

class Ppc64EmbeddedSymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = Ppc64EmbeddedArgDefSymEmu

class Ppc32ServerSymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = Ppc32ServerArgDefSymEmu

class Ppc64ServerSymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = Ppc64ServerArgDefSymEmu


# Call impls
class Ppc32EmbeddedCall(Ppc32EmbeddedSymCallingConv, e_ppc.PpcCall):
    pass

class Ppc64EmbeddedCall(Ppc64EmbeddedSymCallingConv, e_ppc.PpcCall):
    pass

class Ppc32ServerCall(Ppc32ServerSymCallingConv, e_ppc.PpcCall):
    pass

class Ppc64ServerCall(Ppc64ServerSymCallingConv, e_ppc.PpcCall):
    pass

class PpcSymFuncEmu(vsym_analysis.SymbolikFunctionEmulator):

    __width__ = None
    __cconv__ = None

    def __init__(self, vw):
        vsym_analysis.SymbolikFunctionEmulator.__init__(self, vw)
        self.setStackBase(0xbfbff000, 16384)

        self.addCallingConvention('ppccall', self.__cconv__)
        # FIXME possibly decide this by platform/format?
        self.addCallingConvention(None, self.__cconv__)

        #self.addFunctionCallback('ntdll.eh_prolog', self._eh_prolog)
        #self.addFunctionCallback('ntdll.seh3_prolog', self._seh3_prolog)
        #self.addFunctionCallback('ntdll.seh3_epilog', self._seh3_epilog)
        #self.addFunctionCallback('ntdll._alloca_probe', self.alloca_probe)

    def getStackCounter(self):
        return self.getSymVariable('sp')

    def setStackCounter(self, symobj):
        self.setSymVariable('sp', symobj)

    '''
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
        emu.writeSymMemory(esp, Var('eh_ffffffff',4))
        esp -= Const(4, 4)
        emu.writeSymMemory(esp, eax)
        esp -= Const(4, 4)
        emu.writeSymMemory(esp, Var('eh_c0c0c0c0',4))
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
            emu.setStackSize( stacksize + stackadd )

        emu.setSymVariable('esp', esp-eax)
        #if eax < 0x1000:
            #eax -= Const(4, self.__width__)
            #emu.setSymVariable('esp', esp-eax)
        #else:
            #while eax > 0x1000:
                #eax -= Const(0x1000, self.__width__)
                #emu.setSymVariable('esp', esp-Const(0x1000, self.__width__))
                #esp -= Const(0x1000, self.__width__)
            #emu.setSymVariable('esp', esp-eax)

    def _seh3_prolog(self, emu, fname, argv):

        scopetable, localsize = argv
        esp = emu.getSymVariable('esp')

        emu.writeSymMemory(esp + Const(4, self.__width__),  emu.getSymVariable('ebp'))
        emu.writeSymMemory(esp, scopetable)
        emu.writeSymMemory(esp - Const(4, self.__width__), Var('ntdll.seh3_handler', 4))     # push
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
        return emu.getSymVariable('eax') '''


class Ppc32EmbeddedSymFuncEmu(PpcSymFuncEmu):
    __width__ = 4
    __cconv__ = Ppc32EmbeddedCall()

class Ppc64EmbeddedSymFuncEmu(PpcSymFuncEmu):
    __width__ = 8
    __cconv__ = Ppc64EmbeddedCall()

class Ppc32ServerSymFuncEmu(PpcSymFuncEmu):
    __width__ = 4
    __cconv__ = Ppc32ServerCall()

class Ppc64ServerSymFuncEmu(PpcSymFuncEmu):
    __width__ = 8
    __cconv__ = Ppc64ServerCall()


class Ppc32EmbeddedSymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = Ppc32EmbeddedSymbolikTranslator
    __emu__ = Ppc32EmbeddedSymFuncEmu

class Ppc64EmbeddedSymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = Ppc64EmbeddedSymbolikTranslator
    __emu__ = Ppc64EmbeddedSymFuncEmu

class PpcVleSymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = PpcVleSymbolikTranslator
    __emu__ = Ppc32EmbeddedSymFuncEmu

class Ppc32ServerSymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = Ppc32ServerSymbolikTranslator
    __emu__ = Ppc32ServerSymFuncEmu

class Ppc64ServerSymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = Ppc64ServerSymbolikTranslator
    __emu__ = Ppc64ServerSymFuncEmu
