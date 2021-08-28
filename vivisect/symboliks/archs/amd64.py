import hashlib

import envi
import envi.archs.amd64 as e_amd64

from vivisect.symboliks.common import *
import vivisect.symboliks.archs.i386 as vsym_i386
import vivisect.symboliks.analysis as vsym_analysis
import vivisect.symboliks.callconv as vsym_callconv
from envi.archs.amd64.vmcslookup import VMCS_NAMES

class VMCS_Field(Var):
    def __init__(self, offset, width):
        SymbolikBase.__init__(self)
        self.offset = offset
        self.width = width

    def __repr__(self):
        return 'VMCS_Field(%s,width=%d)' % (self.offset, self.width)

    def __str__(self):
        if self._strval:
            return self._strval

        if not self.offset.isDiscrete():
            return 'VMCS::%s' % self.offset

        self._strval = 'VMCS_%s' % VMCS_NAMES.get(self.offset.solve())
        return self._strval

    def _solve(self, emu=None):
        name = 'vmcs%s' % self.offset

        if emu is not None:
            name += emu.getRandomSeed()

        return int(hashlib.md5(name).hexdigest()[:self.width*2], 16)

    def update(self, emu):
        offset = self.offset.update(emu=emu)
        return VMCS_Field(offset, width=self.width)

    def _reduce(self, emu=None):
        self.offset._reduce(emu=emu)
        return self

    def getWidth(self):
        return self.width

    def isDiscrete(self, emu=None):
        return False


class Amd64SymbolikTranslator(vsym_i386.IntelSymbolikTranslator):
    __arch__ = e_amd64.Amd64Module
    __ip__ = 'rip'  # we could use regctx.getRegisterName if we want.
    __sp__ = 'rsp'  # we could use regctx.getRegisterName if we want.
    __bp__ = 'rbp'  # we could use regctx.getRegisterName if we want.
    __srcp__ = 'rsi'
    __destp__ = 'rdi'

    def setRegObj(self, regidx, obj):
        ridx = regidx & 0xffff
        rname = self._reg_ctx.getRegisterName(ridx)
        rbitwidth = self._reg_ctx.getRegisterWidth(ridx)
        val = Var(rname, rbitwidth >> 3)

        # Translate to native if needed...
        if ridx != regidx:
            # 64 bit mode setting to 32bit regs, 0-extends to 64 bits
            if regidx == ridx | e_amd64.RMETA_LOW32:
                val = Var(rname, 8)
            else:
                # we cannot call _xlateToNativReg since we'd pass in a symbolik
                # object that would trigger an or operation; the code in envi
                # obviously is NOT symboliks aware (2nd op in | operation is NOT
                # a symbolik); so we do it manually here since we are symbolik
                # aware.
                # obj = self._reg_ctx._xlateToNativeReg(regidx, obj)
                basemask = (2**rbitwidth) - 1
                rreg, lshift, mask = self._reg_ctx.getMetaRegInfo(regidx)
                # cut hole in mask
                finalmask = basemask ^ (mask << lshift)
                if lshift != 0:
                    obj <<= Const(lshift, rbitwidth >> 3)

                obj = obj | (val & Const(finalmask, rbitwidth >> 3))

        self.effSetVariable(rname, obj)

    def getOperAddrObj(self, op, idx):
        oper = op.opers[idx]
        if isinstance(oper, e_amd64.Amd64RipRelOper):
            return Const(op.va + len(op) + oper.imm, 8)

        return vsym_i386.IntelSymbolikTranslator.getOperAddrObj(self, op, idx)

    def getOperObj(self, op, idx):
        oper = op.opers[idx]
        if isinstance(oper, e_amd64.Amd64RipRelOper):
            return Mem(Const(op.va + len(op) + oper.imm, 8), Const(oper.tsize, 8))

        return vsym_i386.IntelSymbolikTranslator.getOperObj(self, op, idx)

    # TODO: support callf and all that nonsense

    def i_pextrd_q(self, op):
        self.i_pextrb(op, width=op.opers[0].tsize)

    def i_movsxd(self, op):
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        v2 = o_sextend(self.getOperObj(op, 1), Const(dsize, self._psize))
        self.setOperObj(op, 0, v2)

    def _div(self, op, isInvalid=None):
        oper = op.opers[0]
        denom = self.getOperObj(op, 0)
        if denom == 0:
            # TODO: make effect
            raise envi.DivideByZero('AMD64 Divide by zero')

        if isInvalid is None:
            limit = (2 ** (oper.tsize * 8)) - 1
            isInvalid = lambda val: val > limit

        if oper.tsize == 8:
            rax = Var('rax', self._psize)
            rdx = Var('rdx', self._psize)
            num = (rdx << Const(64, self._psize)) | rax
            temp = num / denom
            if temp.isDiscrete() and isInvalid(temp):
                # TODO: make effect
                raise envi.DivideError('AMD64 i_div #DE')

            self.effSetVariable('rax', temp)
            self.effSetVariable('rdx', num % denom)

            return

        return vsym_i386.IntelSymbolikTranslator._div(self, op, isInvalid=isInvalid)

    def i_div(self, op):
        return self._div(op)

    def i_jecxz(self, op):
        return vsym_i386.IntelSymbolikTranslator.i_jecxz(self, op)

    def i_jrcxz(self, op):
        return self._cond_jmp(op, eq(Var('rcx', self._psize), Const(0, self._psize)))

    def i_pushfd(self, op):
        sp = self.getRegObj(self._reg_ctx._rctx_spindex)
        sr = self.getRegObj(self._reg_ctx._rctx_srindex)
        self.effSetVariable(self.__sp__, sp - Const(8, self._psize))
        self.effWriteMemory(Var(self.__sp__, self._psize), Const(8, self._psize), sr)

    def i_vmread(self, op):
        vmcsoff = self.getOperObj(op, 1)
        self.setOperObj(op, 0, LookupVar("VMCS", vmcsoff, VMCS_NAMES, vmcsoff.getWidth()))

    # FIXME CATASTROPHIC THIS CONTAINS BRANCHING LOGIC STATE!
    # FOR NOW WE JUST DO IT WITHOUT ANY CONDITIONAL (see i386.i_cmpxchg)
    i_cmova = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovae = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnb = i_cmovae

    i_cmovb = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovbe = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovna = i_cmovbe
    i_cmovnae = i_cmovb

    i_cmovc = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnc = vsym_i386.IntelSymbolikTranslator.i_mov

    i_cmove = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovne = vsym_i386.IntelSymbolikTranslator.i_mov

    i_cmovg = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovge = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnle = i_cmovg
    i_cmovnl = i_cmovge

    i_cmovl = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovle = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnge = i_cmovl
    i_cmovng = i_cmovle

    i_cmovo = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovno = vsym_i386.IntelSymbolikTranslator.i_mov

    i_cmovp = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovpe = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnp = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovnpe = vsym_i386.IntelSymbolikTranslator.i_mov

    i_cmovs = vsym_i386.IntelSymbolikTranslator.i_mov
    i_cmovns = vsym_i386.IntelSymbolikTranslator.i_mov

    i_cmovz = i_cmove
    i_cmovnz = i_cmovne

    def i_movsq(self, op):
        return self._movs(op, width=8)

    def i_stosq(self, op):
        return self._stos(op, width=8)

    def i_cmpsq(self, op):
        return self._cmps(op, width=8)

class Amd64ArgDefSymEmu(vsym_i386.ArgDefSymEmu):
    __xlator__ = Amd64SymbolikTranslator

class MSx64CallSym(vsym_callconv.SymbolikCallingConvention, e_amd64.MSx64Call):
    __argdefemu__ = Amd64ArgDefSymEmu

class SysVAmd64CallSym(vsym_callconv.SymbolikCallingConvention, e_amd64.SysVAmd64Call):
    __argdefemu__ = Amd64ArgDefSymEmu

msx64callsym = MSx64CallSym()
sysvamd64callsym = SysVAmd64CallSym()

class Amd64SymFuncEmu(vsym_analysis.SymbolikFunctionEmulator):
    __width__ = 8

    def __init__(self, vw, initial_sp=0xbfbff000):
        vsym_analysis.SymbolikFunctionEmulator.__init__(self, vw)
        self.setStackBase(0xbfbff000, 16384)
        self.addCallingConvention('sysvamd64call', SysVAmd64CallSym())
        self.addCallingConvention('msx64call', msx64callsym)

    def getStackCounter(self):
        return self.getSymVariable('rsp')

    def setStackCounter(self, symobj):
        self.setSymVariable('rsp', symobj)

class Amd64SymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = Amd64SymbolikTranslator
    __emu__ = Amd64SymFuncEmu
