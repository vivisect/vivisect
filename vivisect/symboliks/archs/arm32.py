import sys

import envi
import envi.bits as e_bits
import envi.registers as e_registers
import envi.archs.arm as e_arm

import vivisect.symboliks.analysis as vsym_analysis
import vivisect.symboliks.callconv as vsym_callconv
import vivisect.symboliks.emulator as vsym_emulator
import vivisect.symboliks.translator as vsym_trans

from vivisect.const import *
from vivisect.symboliks.common import *
from vivisect.symboliks.constraints import *

# FIXME: move this arch-independent code...
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
        # FIXME: psize and endian correctness here!
        if not fmt.startswith('<') and not fmt.endswith('P'):
            raise Exception('we dont handle this format string')

        if isinstance(va, int) or isinstance(va, long):
            va = Const(va, self.xlator._psize)

        if len(fmt) == 2:
            return Mem(va, Const(self.xlator._psize, self.xlator._psize))

        args = []
        num = int(fmt[1:fmt.index('P')])
        for i in xrange(num):
            args.append(Mem(va, Const(self.xlator._psize, self.xlator._psize)))
            va += Const(self.xlator._psize, self.xlator._psize)

        return args

class A32SymbolikTranslator(vsym_trans.SymbolikTranslator):
    '''
    '''
    __arch__ = e_arm.ArmModule
    __ip__ = 'pc'
    __sp__ = 'sp'
    #__srcp__ = ''  # ARM doesn't really have these constructs
    #__destp__ = ''
    def __init__(self, vw):
        vsym_trans.SymbolikTranslator.__init__(self, vw)
        self._arch = vw.arch
        self._psize = self._arch.getPointerSize()
        self._reg_ctx = self._arch.archGetRegCtx()

    def setFlag(self, flagname, state):
        self.effSetVariable(flagname, state)
        
    def getFlag(self, flagname):
        return self.effGetVariable(flagname)
        
    ### move upstream to SymbolikTranslator
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

    ### move upstream to SymbolikTranslator?
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

    def getOperAddrObj(self, op, idx):
        '''
        Returns a Tuple!

        (symOperAddrObj,  (reg, newupdate))

        The second part of the tuple is because sometimes ARM updates a register *after*
        the address is used.  This second component should be None if nothing needs to 
        be done for updates.

        This allows the caller to decide whether updates need to be done... and apply 
        the effects at the appropriate time in the event stream, but leaving the operand
        responsible for the calculation/etc...
        '''
        oper = op.opers[idx]
        return oper.getOperAddrObj(op, self)

    def getOperObj(self, op, idx):
        '''
        Translate the specified operand to a symbol compatible with
        the symbolic translation system.

        Returns a tuple: (OperObj, AfterEffs)
        where:
            OperObj is the symbolic operand
            AfterEffs is a list of effects which may be applied after this
                    this allows for ARM's Post-Indexed processing, etc...
                    None by default
        '''
        oper = op.opers[idx]
        if oper.isReg():
            return (self.getRegObj(oper.reg), None)

        elif oper.isDeref():
            addrsym, aftereffs = self.getOperAddrObj(op, idx)
            return self.effReadMemory(addrsym, Const(oper.tsize, self._psize))

        elif oper.isImmed():
            ret = oper.getOperValue(op, self)
            return (Const(ret, self._psize), None)

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
    
    def doPush(self, val):
        sp = self.getRegObj(REG_SP)
        sp -= Const(4, 4)
        self.setRegObj(REG_SP, sp)
        self.writeMemObj(sp, val, Const(4, 4))

    def doPop(self):
        sp = self.getRegObj(REG_SP)
        self.setRegObj(REG_SP, sp+Const(4, 4))
        val = self.readMemObj(sp, Const(4, 4))
        return val

    """
    def getProcMode(self):
        '''
        get current ARM processor mode.  see proc_modes (const.py)
        '''
        return self._rctx_vals[REG_CPSR] & 0x1f     # obfuscated for speed.  could call getCPSR but it's not as fast

    def getCPSR(self):
        '''
        return the Current Program Status Register.
        '''
        return Var('cpsr', 4)
        #return self._rctx_vals[REG_CPSR]

    def getFPSCR(self):
        '''
        return the Current Floating Point Status/Control Register.
        '''
        return Var('fpscr', 4)
        #return self._rctx_vals[REG_FPSCR]

    def getAPSR(self):
        '''
        return the Current Program Status Register.
        '''
        apsr = self.getCPSR() & REG_APSR_MASK
        return apsr

    def setCPSR(self, psr, mask=0xffffffff):
        '''
        set the CPSR for the current ARM processor mode
        '''
        
        psr = self._rctx_vals[REG_CPSR] & (~mask) | (psr & mask)
        self._rctx_vals[REG_CPSR] = psr

    def setAPSR(self, psr):
        '''
        set the CPSR for the current ARM processor mode
        '''
        self.setCPSR(psr, mask=0xffff0000)

    def getSPSR(self, mode):
        '''
        get the SPSR for the given ARM processor mode
        '''
        ridx = _getRegIdx(REG_OFFSET_CPSR, mode)
        return self._rctx_vals[ridx]

    def setSPSR(self, mode, psr, mask=0xffffffff):
        '''
        set the SPSR for the given ARM processor mode
        '''
        ridx = _getRegIdx(REG_OFFSET_CPSR, mode)
        psr = self._rctx_vals[ridx] & (~mask) | (psr & mask)
        self._rctx_vals[ridx] = psr

    def setProcMode(self, mode):
        '''
        set the current processor mode.  stored in CPSR
        '''
        # write current psr to the saved psr register for target mode
        # but not for USR or SYS modes, which don't have their own SPSR
        if mode not in (PM_usr, PM_sys):
            curSPSRidx = proc_modes[mode]
            self._rctx_vals[curSPSRidx] = self.getCPSR()

        # set current processor mode
        cpsr = self._rctx_vals[REG_CPSR] & 0xffffffe0
        self._rctx_vals[REG_CPSR] = cpsr | mode

    def getRegister(self, index, mode=None):
        '''
        Return the current value of the specified register index.
        '''
        if mode == None:
            mode = self.getProcMode() & 0xf
        else:
            mode &= 0xf

        idx = (index & 0xffff)
        ridx = _getRegIdx(idx, mode)
        if idx == index:
            return self._rctx_vals[ridx]

        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = (2**width)-1
        return (self._rctx_vals[ridx] >> offset) & mask

    def setRegister(self, index, value, mode=None):
        '''
        Set a register value by index.
        '''
        if mode == None:
            mode = self.getProcMode() & 0xf
        else:
            mode &= 0xf

        self._rctx_dirty = True

        # the raw index (in case index is a metaregister)
        idx = (index & 0xffff)

        # we only keep separate register banks per mode for general registers, not vectors
        if idx >= REGS_VECTOR_TABLE_IDX:
            ridx = idx
        else:
            ridx = _getRegIdx(idx, mode)

        if idx == index:    # not a metaregister
            if value.width != self._rctx_widths[ridx]:
                raise Exception('crap')
            
            self.effSetVariable(rname, value)
            #self._rctx_vals[ridx] = (value & self._rctx_masks[ridx])      # FIXME: hack.  should look up index in proc_modes dict?
            return

        # If we get here, it's a meta register index.
        # NOTE: offset/width are in bits...
        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        mask = e_bits.b_masks[width]
        mask = mask << offset

        # NOTE: basewidth is in *bits*
        basewidth = self._rctx_widths[ridx]
        basemask  = (2**basewidth)-1

        # cut a whole in basemask at the size/offset of mask
        finalmask = basemask ^ mask

        curval = self._rctx_vals[ridx]

        self._rctx_vals[ridx] = (curval & finalmask) | (value << offset)
        self.effSetVariable(rname, value)

    def integerSubtraction(self, op):
        '''
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        '''
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        src1 = self.getOperObj(op, 1)
        src2 = self.getOperObj(op, 2)
        Sflag = op.iflags & IF_PSR_S

        return self.intSubBase(src1, src2, Sflag)

    def AddWithCarry(self, src1, src2, carry=0, Sflag=0, rd=0, tsize=4):
        '''////AddWithCarry()
        ==============
        (bits(N), bit, bit) AddWithCarry(bits(N) x, bits(N) y, bit carry_in)
            unsigned_sum = UInt(x) + UInt(y) + UInt(carry_in);
            signed_sum = SInt(x) + SInt(y) + UInt(carry_in);

            result = unsigned_sum<N-1:0>; // same value as signed_sum<N-1:0>

            carry_out = if UInt(result) == unsigned_sum then '0' else '1';
            overflow = if SInt(result) == signed_sum then '0' else '1';

            return (result, carry_out, overflow);

        An important property of the AddWithCarry() function is that if:
        (result, carry_out, overflow) = AddWithCarry(x, NOT(y), carry_in)
        then:

        * if carry_in == '1', then result == x-y with:
            overflow == '1' if signed overflow occurred during the subtraction
            carry_out == '1' if unsigned borrow did not occur during the subtraction, that is, if x >= y
       
        * if carry_in == '0', then result == x-y-1 with:
            overflow == '1' if signed overflow occurred during the subtraction
            carry_out == '1' if unsigned borrow did not occur during the subtraction, that is, if x > y.


        Together, these mean that the carry_in and carry_out bits in AddWithCarry() calls can act as NOT borrow flags for
        subtractions as well as carry flags for additions.
        (@ we don't retrn carry-out and overflow, but set the flags here)
        '''
        udst = e_bits.unsigned(src1, tsize)
        usrc = e_bits.unsigned(src2, tsize)

        sdst = e_bits.signed(src1, tsize)
        ssrc = e_bits.signed(src2, tsize)

        ures = udst + usrc + carry
        sres = sdst + ssrc + carry
        result = ures & 0xffffffff

        newcarry = (ures != result)
        overflow = e_bits.signed(result, tsize) != sres

        #print "====================="
        #print hex(udst), hex(usrc), hex(ures), hex(result)
        #print hex(sdst), hex(ssrc), hex(sres)
        #print e_bits.is_signed(result, tsize), not result, newcarry, overflow
        #print "ures:", ures, hex(ures), " sres:", sres, hex(sres), " result:", result, hex(result), " signed(result):", e_bits.signed(result, 4), hex(e_bits.signed(result, 4)), "  C/V:",newcarry, overflow

        if Sflag:
            curmode = self.getProcMode()
            if rd == 15:
                if(curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            else:
                self.setFlag(PSR_N_bit, e_bits.is_signed(result, tsize))
                self.setFlag(PSR_Z_bit, not result)
                self.setFlag(PSR_C_bit, newcarry)
                self.setFlag(PSR_V_bit, overflow)

        return result

    def intSubBase(self, src1, src2, Sflag=0, rd=0, tsize=4):
        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.

        udst = e_bits.unsigned(src1, tsize)
        usrc = e_bits.unsigned(src2, tsize)

        sdst = e_bits.signed(src1, tsize)
        ssrc = e_bits.signed(src2, tsize)

        ures = udst - usrc
        sres = sdst - ssrc
        result = ures & 0xffffffff

        newcarry = (ures != result)
        overflow = (e_bits.signed(result, 4) != sres)

        if Sflag:
            curmode = self.getProcMode()
            if rd == 15:
                if(curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, tsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_C_bit, newcarry)
            self.setFlag(PSR_V_bit, overflow)

        return ures
    """
    def logicalAnd(self, op):
        opercnt = len(op.opers)

        if opercnt == 3:
            src1 = self.getOperObj(op, 1)
            src2 = self.getOperObj(op, 2)
        else:
            src1 = self.getOperObj(op, 0)
            src2 = self.getOperObj(op, 1)

        res = src1 & src2

        if op.iflags & IF_PSR_S:     # FIXME: convert to gt, lt, eq, sf
            self.setFlag(PSR_N_bit, Const(0, 1))
            self.setFlag(PSR_Z_bit, not res)
            self.setFlag(PSR_C_bit, Const(0, 1))
            self.setFlag(PSR_V_bit, Const(0, 1))
        return res

    def interrupt(self, val):
        '''
        If we run into an interrupt, what do we do?  Handles can be snapped in and used as function calls
        '''
        if val >= len(self.int_handlers):
            logger.critical("FIXME: Interrupt Handler %x is not handled", val)

        handler = self.int_handlers[val]
        handler(val)

    def default_int_handler(self, val):
        logger.warn("DEFAULT INTERRUPT HANDLER for Interrupt %d (called at 0x%x)", val, self.getProgramCounter())

    def i_and(self, op):
        res = self.logicalAnd(op)
        self.setOperObj(op, 0, res)
       
    def i_orr(self, op):
        tsize = op.opers[0].tsize
        if len(op.opers) == 3:
            val1 = self.getOperObj(op, 1)
            val2 = self.getOperObj(op, 2)
        else:
            val1 = self.getOperObj(op, 0)
            val2 = self.getOperObj(op, 1)
        val = val1 | val2
        self.setOperObj(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            #self.setFlag(PSR_N_bit, e_bits.is_signed(val, tsize))
            #self.setFlag(PSR_Z_bit, not val)
            #self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(val, tsize))
            #self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(val, tsize))
            self.effSetVariable('eflags_gt', gt(v1, v2))
            self.effSetVariable('eflags_lt', lt(v1, v2))
            self.effSetVariable('eflags_of', Const(0, self._psize))
            self.effSetVariable('eflags_cf', Const(0, self._psize))
            self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 | v2 < 0
            self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0
            self.setOperObj(op, 0, obj)
       
    def i_stm(self, op):
        if len(op.opers) == 2:
            srcreg = op.opers[0].reg
            addr = self.getOperValue(op,0)
            regvals = self.getOperValue(op, 1)

            updatereg = op.opers[0].oflags & OF_W
            flags = op.iflags
        else:
            srcreg = REG_SP
            addr = self.getStackCounter()
            oper = op.opers[0]
            if isinstance(oper, ArmRegOper):
                regvals = [ self.getOperValue(op, 0) ]
            else:
                regvals = self.getOperValue(op, 0)

            updatereg = 1
            flags = IF_DAIB_B

        pc = self.getRegister(REG_PC)       # store for later check

        addr = self.getRegister(srcreg)
        numregs = len(regvals)
        for vidx in range(numregs):
            if flags & IF_DAIB_B == IF_DAIB_B:
                if flags & IF_DAIB_I == IF_DAIB_I:
                    addr += 4
                    val = regvals[vidx]
                else:
                    addr -= 4
                    val = regvals[numregs-vidx-1]
                self.writeMemValue(addr, val, 4)
            else:
                if flags & IF_DAIB_I == IF_DAIB_I:
                    val = regvals[vidx]
                else:
                    val = regvals[numregs-vidx-1]

                self.writeMemValue(addr, val, 4)

                if flags & IF_DAIB_I == IF_DAIB_I:
                    addr += 4
                else:
                    addr -= 4

        if updatereg:
            self.setRegister(srcreg,addr)
        #FIXME: add "shared memory" functionality?  prolly just in strex which will be handled in i_strex
        # is the following necessary? 
        newpc = self.getRegister(REG_PC)    # check whether pc has changed
        if pc != newpc:
            return newpc

    i_stmia = i_stm
    i_push = i_stmia

    def i_vpush(self, op):
        oper = op.opers[0]
        tsize = oper.getRegSize()
        reglist = oper.getOperValue(op, self)

        for reg in reglist:
            sp = self.getRegister(REG_SP)
            sp -= tsize
            self.writeMemValue(sp, reg, tsize)
            self.setRegister(REG_SP, sp)

    def i_vpop(self, op):
        oper = op.opers[0]
        tsize = oper.getRegSize()

        reglist = []
        for ridx in range(oper.getRegCount()):
            sp = self.getRegister(REG_SP)
            val = self.readMemValue(sp, 4)
            reglist.append(val)
            self.setRegister(REG_SP, sp+4)

        oper.setOperValue(op, reglist, self)

    def i_vldm(self, op):
        if len(op.opers) == 2:
            srcreg = op.opers[0].reg
            updatereg = op.opers[0].oflags & OF_W
            addr = self.getOperValue(op,0)
            flags = op.iflags
        else:
            srcreg = REG_SP
            updatereg = 1
            addr = self.getStackCounter()
            flags = IF_DAIB_I

        pc = self.getRegister(REG_PC)       # store for later check
       
        # set up
        reglistoper = op.opers[1]
        count = reglistoper.getRegCount()
        size  = reglistoper.getRegSize()

        # do multiples based on base and count.  unlike ldm, these must be consecutive
        if flags & IF_DAIB_I == IF_DAIB_I:
            for reg in xrange(count):
                regval = self.readMemValue(addr, size)
                self.setRegister(reg, regval)
                addr += size
        else:
            for reg in xrange(count-1, -1, -1):
                addr -= size
                regval = self.readMemValue(addr, size)
                self.setRegister(reg, regval)

        if updatereg:
            self.setRegister(srcreg,addr)
        #FIXME: add "shared memory" functionality?  prolly just in ldrex which will be handled in i_ldrex
        # is the following necessary? 
        newpc = self.getRegister(REG_PC)    # check whether pc has changed
        if pc != newpc:
            self.setThumbMode(newpc & 1)
            return newpc

    def i_vmov(self, op):
        if len(op.opers) == 2:
            src = self.getOperValue(op, 1)
            if isinstance(op.opers[1], ArmImmOper):
                # immediate version copies immediate into each element (Q=2 elements, D=1)
                srcsz = op.opers[1].size
                logger.warn("0x%x vmov: immediate: %x (%d bytes)", op.va, src, srcsz)
                # change src to fill all vectors with immediate

            # vreg to vreg: 1 to 1 copy
            # core reg to vreg
            # vret to core reg
            # core reg to single
            self.setOperValue(op, 0, src)

        elif len(op.opers) == 3:
            # 2 core reg to double
            # move between two ARM Core regs and one dblword extension reg
            if op.opers[0].reg < REGS_VECTOR_TABLE_IDX:
                # dest is core regs
                src = self.getOperValue(op, 2)
                self.setOperValue(op, 0, (src & 0xffffffff))
                self.setOperValue(op, 1, (src >> 32))
            else:
                # dest is extension reg
                src = self.getOperValue(op, 1)
                src2 = self.getOperValue(op, 2)
                src |= (int(src2) << 32)
                self.setOperValue(op, 0, src)

        elif len(op.opers) == 4:
            # 2 core reg to 2 singles
            src1 = self.getOperValue(op, 2)
            src2 = self.getOperValue(op, 3)
            self.setOperValue(op, 0, src1)
            self.setOperValue(op, 1, src2)

        else:
            raise Exception("0x%x:  %r   Something went wrong... opers = %r " % (op.va, op, op.opers))
           

    def i_vstr(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_vcmp(self, op):
        try:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
            val = src2 - src1
            logger.debug("vcmpe %r  %r  %r", src1, src2, val)
            fpsrc = self.getRegister(REG_FPSCR)

            # taken from VFCompare() from arch ref manual p80
            if src1 == src2:
                n, z, c, v = 0, 1, 1, 0
            elif src1 < src2:
                n, z, c, v = 1, 0, 0, 0
            else:
                n, z, c, v = 0, 0, 1, 0

            self.setFpFlag(PSR_N_bit, n)
            self.setFpFlag(PSR_Z_bit, z)
            self.setFpFlag(PSR_C_bit, c)
            self.setFpFlag(PSR_V_bit, v)
        except Exception, e:
            logger.warn("vcmp exception: %r", e)

    def i_vcmpe(self, op):
        try:
            size = (4,8)[bool(op.iflags & IFS_F64)]

            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
               
            val = src2 - src1
               
            logger.debug("vcmpe %r %r  %r  %r", op, src1, src2, val)
            fpsrc = self.getRegister(REG_FPSCR)

            # taken from VFCompare() from arch ref manual p80
            if src1 == src2:
                n, z, c, v = 0, 1, 1, 0
            elif src1 < src2:
                n, z, c, v = 1, 0, 0, 0
            else:
                n, z, c, v = 0, 0, 1, 0

            self.setFpFlag(PSR_N_bit, n)
            self.setFpFlag(PSR_Z_bit, z)
            self.setFpFlag(PSR_C_bit, c)
            self.setFpFlag(PSR_V_bit, v)
        except Exception, e:
            logger.warn("vcmpe exception: %r" % e)

    def i_vcvt(self, op):
        logger.warn('%r\t%r', op, op.opers)
        logger.warn("complete implementing vcvt")
        width = op.opers[0].getWidth()
        regcnt = width / 4

        raise Exception("IMPLEMENT ME: i_vcvt")
        if len(op.opers) == 3:
            for reg in range(regcnt):
                #frac_bits = 64 - op.opers[2].val
                # pA8_870
                if op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass

                # pA8_872
                elif op.simdflags & IFS_U16_F32:
                    pass
                elif op.simdflags & IFS_S16_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U16_F64:
                    pass
                elif op.simdflags & IFS_S16_F64:
                    pass
                elif op.simdflags & IFS_U32_F64:
                    pass
                elif op.simdflags & IFS_S32_F64:
                    pass

                elif op.simdflags & IFS_F32_U16:
                    pass                      
                elif op.simdflags & IFS_F32_S16:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass
                elif op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F64_U16:
                    pass
                elif op.simdflags & IFS_F64_S16:
                    pass
                elif op.simdflags & IFS_F64_U32:
                    pass
                elif op.simdflags & IFS_F64_S32:
                    pass

        elif len(op.opers) == 2:
            for reg in range(regcnt):
                #frac_bits = 64 - op.opers[1].val
                # pA8_866
                if op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass

                # pA8-868
                elif op.simdflags & IFS_F64_S32:
                    pass
                elif op.simdflags & IFS_F64_U32:
                    pass
                elif op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass

                elif op.simdflags & IFS_S32_F64:
                    pass
                elif op.simdflags & IFS_U32_F64:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass

                # pA8-874
                elif op.simdflags & IFS_F64_F32:
                    pass
                elif op.simdflags & IFS_F32_F64:
                    pass

                # pA8-876
                elif op.simdflags & IFS_F16_F32:
                    pass
                elif op.simdflags & IFS_F32_F16:
                    pass
        else:
            raise Exception("i_vcvt with strange number of opers: %r" % op.opers)

    i_vcvtr = i_vcvt

    def i_ldm(self, op):
        if len(op.opers) == 2:
            srcreg = op.opers[0].reg
            addr = self.getOperValue(op,0)
            regmask = op.opers[1].val
            updatereg = op.opers[0].oflags & OF_W
            flags = op.iflags
        else:
            srcreg = REG_SP
            addr = self.getStackCounter()
            oper = op.opers[0]
            if isinstance(oper, ArmRegOper):
                regmask = (1<<oper.reg)

            else:
                regmask = op.opers[0].val
            updatereg = 1
            flags = IF_DAIB_I

        pc = self.getRegister(REG_PC)       # store for later check

        if flags & IF_DAIB_I == IF_DAIB_I:
            for reg in xrange(16):
                if (1<<reg) & regmask:
                    regval = self.readMemValue(addr, 4)
                    self.setRegister(reg, regval)
                    addr += 4
        else:
            for reg in xrange(15, -1, -1):
                if (1<<reg) & regmask:
                    addr -= 4
                    regval = self.readMemValue(addr, 4)
                    self.setRegister(reg, regval)

        if updatereg:
            self.setRegister(srcreg,addr)
        #FIXME: add "shared memory" functionality?  prolly just in ldrex which will be handled in i_ldrex
        # is t  he following necessary? 
        newpc = self.getRegister(REG_PC)    # check whether pc has changed
        if pc != newpc:
            self.setThumbMode(newpc & 1)
            return newpc & -2

    i_ldmia = i_ldm
    i_pop = i_ldmia


    def setThumbMode(self, thumb=1):
        self.setFlag(PSR_T_bit, thumb)

    def setArmMode(self, arm=1):
        self.setFlag(PSR_T_bit, not arm)

    def i_ldr(self, op):
        # hint: covers ldr, ldrb, ldrbt, ldrd, ldrh, ldrsh, ldrsb, ldrt   (any instr where the syntax is ldr{condition}stuff)
        # need to check that t variants only allow non-priveleged access (ldrt, ldrht etc)
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
        if op.opers[0].reg == REG_PC:
            self.setThumbMode(val & 1)
            return val & -2

    i_ldrb = i_ldr
    i_ldrbt = i_ldr
    i_ldrd = i_ldr
    i_ldrh = i_ldr
    i_ldrht = i_ldr
    i_ldrsh = i_ldr
    i_ldrsb = i_ldr
    i_ldrt = i_ldr

    def i_ldrex(self, op):
        with self.mem_access_lock:
            return self.i_ldr(op)

    def i_strex(self, op):
        with self.mem_access_lock:
            return self.i_str(op)

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

        if op.iflags & IF_PSR_S:
            dsize = op.opers[0].tsize
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)

        if op.iflags & envi.IF_RET:
            self.setThumbMode(val & 1)
            return val & -2

        dest = op.opers[0]
        if isinstance(dest, ArmRegOper) and dest.reg == REG_PC:
            self.setThumbMode(val & 1)
            return val & -2

    def i_movt(self, op):
        base = self.getOperValue(op, 0) & 0xffff
        val = self.getOperValue(op, 1) << 16
        self.setOperValue(op, 0, base | val)

    def i_movw(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    i_msr = i_mov
    i_adr = i_mov

    def i_vmsr(self, op):
        if len(op.opers) == 1:
            val = self.getOperValue(op, 0)
        else:
            val = self.getOperValue(op, 1)

        self.setRegister(REG_FPSCR, val)
           
    def i_mrs(self, op):
        val = self.getAPSR()
        self.setOperValue(op, 0, val)

    def i_vmrs(self, op):
        src = self.getRegister(REG_FPSCR)

        if op.opers[0].reg != 15:
            self.setOperValue(op, 0, src)
        else:
            apsr = self.getAPSR() & 0x0fffffff
            apsr |= (src | 0xf0000000)
            self.setOperValue(op, 0, apsr)

    i_vldr = i_mov


    # TESTME: IT functionality
    def i_it(self, op):
        if self.itcount:
            raise Exception("IT block within an IT block!")

        self.itcount, self.ittype, self.itmask = op.opers[0].getCondData()
        condcheck = conditionals[self.ittype]
        self.itva = op.va

    i_ite = i_it
    i_itt = i_it
    i_itee = i_it
    i_itet = i_it
    i_itte = i_it
    i_ittt = i_it
    i_iteee = i_it
    i_iteet = i_it
    i_itete = i_it
    i_itett = i_it
    i_ittee = i_it
    i_ittet = i_it
    i_ittte = i_it
    i_itttt = i_it
          
    def i_bfi(self, op):
        lsb = self.getOperValue(op, 2)
        width = self.getOperValue(op, 3)
        mask = e_bits.b_masks[width]

        addit = self.getOperValue(op, 1) & mask

        mask <<= lsb
        val = self.getOperValue(op, 0) & ~mask
        val |= (addit << lsb)

        self.setOperValue(op, 0, val)

    def i_bfc(self, op):
        lsb = self.getOperValue(op, 1)
        width = self.getOperValue(op, 2)
        mask = e_bits.b_masks[width] << lsb
        mask ^= 0xffffffff

        val = self.getOperValue(op, 0)
        val &= mask

        self.setOperValue(op, 0, val)

    def i_clz(self, op):
        oper = self.getOperValue(op, 1)
        bsize = op.opers[1].tsize * 8
        lzcnt = 0
        for x in range(bsize):
            if oper & 0x80000000:
                break
            lzcnt += 1
            oper <<= 1

        self.setOperValue(op, 0, lzcnt)

    def i_mvn(self, op):
        val = self.getOperValue(op, 1)
        val ^= 0xffffffff
        self.setOperValue(op, 0, val)

    def i_str(self, op):
        # hint: covers str, strb, strbt, strd, strh, strsh, strsb, strt   (any instr where the syntax is str{condition}stuff)
        # need to check that t variants only allow non-priveleged access (strt, strht etc)
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

    i_strh = i_str
    i_strb = i_str
    i_strbt = i_str
    i_strd = i_str
    i_strh = i_str
    i_strsh = i_str
    i_strsb = i_str
    i_strt = i_str

    def i_add(self, op):
        if len(op.opers) == 3:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
       
        dsize = op.opers[0].tsize
        reg = op.opers[0].reg
        Sflag = op.iflags & IF_PSR_S

        ures = self.AddWithCarry(src1, src2, 0, Sflag, rd=reg, tsize=dsize)
        self.setOperValue(op, 0, ures)
       
        #FIXME PDE and flags
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

    def i_adc(self, op):
        if len(op.opers) == 3:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
       
        #FIXME PDE and flags
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

       
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        Carry = self.getFlag(PSR_C_bit)
        Sflag = op.iflags & IF_PSR_S
        ures = self.AddWithCarry(src1, src2, Carry, Sflag, op.opers[0].reg)

        self.setOperValue(op, 0, ures)

    def i_b(self, op):
        '''
        conditional branches (eg. bne) will be handled here. they are all CONDITIONAL 'b'
        '''
        return self.getOperValue(op, 0)

    def i_bl(self, op):
        tmode = self.getFlag(PSR_T_bit)
        retva = (self.getRegister(REG_PC) + len(op)) | tmode
        self.setRegister(REG_LR, retva)
        return self.getOperValue(op, 0)

    def i_bx(self, op):
        target = self.getOperValue(op, 0)
        self.setFlag(PSR_T_bit, target & 1)
        return target & -2

    def i_blx(self, op):
        tmode = self.getFlag(PSR_T_bit)
        retva = (self.getRegister(REG_PC) + len(op)) | tmode
        self.setRegister(REG_LR, retva)

        target = self.getOperValue(op, 0)
        self.setFlag(PSR_T_bit, target & 1)
        return target & -2

    def i_svc(self, op):
        svc = self.getOperValue(op, 0)
        logger.warn("Service 0x%x called at 0x%x", svc, op.va)

    def i_tst(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ures = src1 & src2

        self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
        self.setFlag(PSR_Z_bit, (0,1)[ures==0])
        self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
       
    def i_teq(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ures = src1 ^ src2

        self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
        self.setFlag(PSR_Z_bit, not ures)
        oper = op.opers[1]
        if isinstance(oper, ArmRegShiftImmOper):
            if oper.shimm == 0:
                return
            logger.critical('FIXME: TEQ - do different shift types for Carry flag')
            # FIXME: make the operands handle a ThumbExpandImm_C (for immediate) or Shift_C (for RegShiftImm), etc...
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
       
    def i_rsb(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
       
        #FIXME PDE and flags
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        Sflag = op.iflags & IF_PSR_S
        Carry = 1
        dsize = op.opers[0].tsize
        reg = op.opers[0].reg

        mask = e_bits.u_maxes[dsize]
        res = self.AddWithCarry(mask ^ src1, src2, Carry, Sflag, reg, dsize)

        self.setOperValue(op, 0, res)

    def i_rsc(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        #FIXME PDE and flags
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        Sflag = op.iflags & IF_PSR_S
        Carry = self.getFlag(PSR_C_bit)
        dsize = op.opers[0].tsize
        reg = op.opers[0].reg

        mask = e_bits.u_maxes[dsize]
        res = self.AddWithCarry(src2, mask ^ src1, Carry, Sflag, reg, dsize)

        self.setOperValue(op, 0, res)

    def i_sub(self, op):
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        if len(op.opers) > 2:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        reg = op.opers[0].reg
        Sflag = op.iflags & IF_PSR_S
        mask = e_bits.u_maxes[op.opers[1].tsize]

        if src1 is None or src2 is None:
            self.undefFlags()
            return None

        res = self.AddWithCarry(src1, mask ^ src2, 1, Sflag, rd=reg, tsize=dsize)
        self.setOperValue(op, 0, res)

    i_subs = i_sub

    def i_sbc(self, op):
        # Src op gets sign extended to dst
        if len(op.opers) > 2:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)

        Sflag = op.iflags & IF_PSR_S
        Carry = self.getFlag(PSR_C_bit)

        mask = e_bits.u_maxes[op.opers[1].tsize]
        res = self.AddWithCarry(src1, mask ^ src2, Carry, Sflag, op.opers[0].reg)

        self.setOperValue(op, 0, res)

    def i_eor(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
       
        #FIXME PDE and flags
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        usrc1 = e_bits.unsigned(src1, dsize)
        usrc2 = e_bits.unsigned(src2, dsize)

        ures = usrc1 ^ usrc2

        self.setOperValue(op, 0, ures)

        curmode = self.getProcMode()
        if op.iflags & IF_PSR_S:
            if op.opers[0].reg == 15:
                if (curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")

            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(ures, dsize))

    def i_cmp(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        dsize = op.opers[0].tsize
        reg = op.opers[0].reg
        Sflag = 1
        mask = e_bits.u_maxes[dsize]

        #print 'cmp', hex(src1), hex(src2)
        res2 = self.AddWithCarry(src1, mask^src2, 1, Sflag, rd=reg, tsize=dsize)

    def i_cmn(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        dsize = op.opers[0].tsize
        reg = op.opers[0].reg
        Sflag = 1

        #print 'cmn', hex(src1), hex(src2)
        res2 = self.AddWithCarry(src1, src2, carry=0, Sflag=Sflag, rd=reg, tsize=dsize)

    i_cmps = i_cmp

    def i_uxth(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    i_uxtb = i_uxth

    def i_uxtah(self, op):
        val = self.getOperValue(op, 2)
        val += self.getOperValue(op, 1)

        self.setOperValue(op, 0, val)

    i_uxtab = i_uxtah

    def i_sxth(self, op):
        slen = op.opers[1].tsize
        dlen = op.opers[0].tsize

        val = self.getOperValue(op, 1)
        val = e_bits.sign_extend(val, slen, dlen)
        self.setOperValue(op, 0, val)

    i_sxtb = i_sxth

    def i_sxtah(self, op):
        slen = op.opers[2].tsize
        dlen = op.opers[0].tsize

        val = self.getOperValue(op, 2)
        val = e_bits.sign_extend(val, slen, dlen)
        val += self.getOperValue(op, 1)

        self.setOperValue(op, 0, val)

    i_sxtab = i_sxtah

    def i_bic(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            val = self.getOperValue(op, 1)
            const = self.getOperValue(op, 2)
        else:
            val = self.getOperValue(op, 0)
            const = self.getOperValue(op, 1)

        val &= ~const
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S # FIXME: IF_PSR_S???
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(val, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(val, dsize))

    def i_swi(self, op):
        # this causes a software interrupt.  we need a good way to handle interrupts
        self.interrupt(op.opers[0].val)

    def i_mul(self, op):
        dsize = op.opers[0].tsize
        Rn = self.getOperValue(op, 1)
        if len(op.opers) == 3:
            Rm = self.getOperValue(op, 2)
        else:
            Rm = self.getOperValue(op, 0)
        val = Rn * Rm
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(val, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(val, dsize))

    def i_lsl(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src = self.getOperValue(op, 1)
            imm5 = self.getOperValue(op, 2)

        else:
            src = self.getOperValue(op, 0)
            imm5 = self.getOperValue(op, 1)

        val = src << imm5
        carry = (val >> 32) & 1
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, carry)

    def i_lsr(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src = self.getOperValue(op, 1)
            shval = self.getOperValue(op, 2) & 0xff

        else:
            src = self.getOperValue(op, 0)
            shval = self.getOperValue(op, 1) & 0xff

        if shval:
            val = src >> shval
            carry = (src >> (shval-1)) & 1
        else:
            val = src
            carry = 0

        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, carry)

    def i_asr(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src = self.getOperValue(op, 1)
            srclen = op.opers[1].tsize
            shval = self.getOperValue(op, 2) & 0xff

        else:
            src = self.getOperValue(op, 0)
            srclen = op.opers[0].tsize
            shval = self.getOperValue(op, 1) & 0xff

        if shval:
            if e_bits.is_signed(src, srclen):
                val = (src >> shval) | top_bits_32[shval]
            else:
                val = (src >> shval)
            carry = (src >> (shval-1)) & 1
        else:
            val = src
            carry = 0

        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, carry)

    def i_ror(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src = self.getOperValue(op, 1)
            imm5 = self.getOperValue(op, 2) & 0b11111

        else:
            src = self.getOperValue(op, 0)
            imm5 = self.getOperValue(op, 1) & 0b11111

        val = ((src >> imm5) | (src << 32-imm5)) & 0xffffffff
        carry = (val >> 31) & 1
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, carry)

    def i_rrx(self, op):
        dsize = op.opers[0].tsize
        if len(op.opers) == 3:
            src = self.getOperValue(op, 1)
            imm5 = self.getOperValue(op, 2)

        else:
            src = self.getOperValue(op, 0)
            imm5 = self.getOperValue(op, 1)

        carry_in = self.getFlag(PSR_C_bit)

        val = (carry_in<<31) | (src >> 1)
        carry = src & 1
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, dsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, carry)


    def i_cbz(self, op):
        regval = op.getOperValue(0)
        imm32 = op.getOperValue(1)
        if not regval:
            return imm32

    def i_cbnz(self, op):
        regval = op.getOperValue(0)
        imm32 = op.getOperValue(1)
        if regval:
            return imm32

    def i_smulbb(self, op):
        oper1 = self.getOperValue(op, 1) & 0xffff
        oper2 = self.getOperValue(op, 2) & 0xffff

        s1 = e_bits.signed(oper1 & 0xffff, 2)
        s2 = e_bits.signed(oper2 & 0xffff, 2)

        result = s1 * s2

        self.setOperValue(op, 0, result)

    def i_smultb(self, op):
        oper1 = self.getOperValue(op, 1) & 0xffff
        oper2 = self.getOperValue(op, 2) & 0xffff

        s1 = e_bits.signed(oper1 >> 16, 2)
        s2 = e_bits.signed(oper2 & 0xffff, 2)

        result = s1 * s2

        self.setOperValue(op, 0, result)

    def i_smulbt(self, op):
        oper1 = self.getOperValue(op, 1) & 0xffff
        oper2 = self.getOperValue(op, 2) & 0xffff

        s1 = e_bits.signed(oper1 & 0xffff, 2)
        s2 = e_bits.signed(oper2 >> 16, 2)

        result = s1 * s2

        self.setOperValue(op, 0, result)

    def i_smultt(self, op):
        oper1 = self.getOperValue(op, 1) & 0xffff
        oper2 = self.getOperValue(op, 2) & 0xffff

        s1 = e_bits.signed(oper1 >>16, 2)
        s2 = e_bits.signed(oper2 >>16, 2)

        result = s1 * s2

        self.setOperValue(op, 0, result)

    def i_tbb(self, op):
        # TBB and TBH both come here.
        ### DEBUGGING
        #raw_input("ArmEmulator:  TBB")
        tsize = op.opers[0].tsize
        tbl = []
        '''
        base = op.opers[0].getOperValue(op, self)
        val0 = self.readMemValue(base, 4)
        if val0 > 0x100 + base:
            print "ummmm.. Houston we got a problem.  first option is a long ways beyond BASE"

        va = base
        while va < val0:
            tbl.append(self.readMemValue(va, 4))
            va += tsize

        print "tbb: \n\t" + '\n'.join([hex(x) for x in tbl])

        ###
        jmptblval = self.getOperAddr(op, 0)
        jmptbltgt = self.getOperValue(op, 0) + base
        print "0x%x: 0x%r\njmptblval: 0x%x\njmptbltgt: 0x%x" % (op.va, op, jmptblval, jmptbltgt)
        raw_input("PRESS ENTER TO CONTINUE")
        return jmptbltgt
        '''
        emu = self
        basereg = op.opers[0].base_reg
        if basereg != REG_PC:
            base = emu.getRegister(basereg)
        else:
            base = op.opers[0].va
            logger.debug("TB base = 0%x", base)

        #base = op.opers[0].getOperValue(op, emu)
        logger.debug("base: 0x%x" % base)
        val0 = emu.readMemValue(base, tsize)

        if val0 > 0x200 + base:
            logger.warn("ummmm.. Houston we got a problem.  first option is a long ways beyond BASE")

        va = base
        while va < base + val0:
            nexttgt = emu.readMemValue(va, tsize) * 2
            logger.debug("0x%x: -> 0x%x", va, nexttgt + base)
            if nexttgt == 0:
                logger.warn("Terminating TB at 0-offset")
                break

            if nexttgt > 0x500:
                logger.warn("Terminating TB at LARGE - offset  (may be too restrictive): 0x%x", nexttgt)
                break

            loc = emu.vw.getLocation(va)
            if loc is not None:
                logger.warn("Terminating TB at Location/Reference")
                logger.warn("%x, %d, %x, %r", loc)
                break

            tbl.append(nexttgt)
            va += tsize

        logger.debug("%s: \n\t"%op.mnem + '\n\t'.join([hex(x+base) for x in tbl]))

        ###
        # for workspace emulation analysis, let's check the index register for sanity.
        idxreg = op.opers[0].offset_reg
        idx = emu.getRegister(idxreg)
        if idx > 0x40000000:
            emu.setRegister(idxreg, 0) # args handed in can be replaced with index 0

        jmptblbase = op.opers[0]._getOperBase(emu)
        jmptblval = emu.getOperAddr(op, 0)
        jmptbltgt = (emu.getOperValue(op, 0) * 2) + base
        logger.debug("0x%x: 0x%r\njmptblbase: 0x%x\njmptblval:  0x%x\njmptbltgt:  0x%x", op.va, op, jmptblbase, jmptblval, jmptbltgt)
        #raw_input("PRESS ENTER TO CONTINUE")
        return jmptbltgt

    i_tbh = i_tbb

    def i_ubfx(self, op):
        src = self.getOperValue(op, 1)
        lsb = self.getOperValue(op, 2)
        width = self.getOperValue(op, 3)
        mask = (1 << width) - 1

        val = (src>>lsb) & mask

        self.setOperValue(op, 0, val)


    def i_umull(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu", op.va, op)
    def i_umlal(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu", op.va, op)
    def i_smull(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu", op.va, op)
    def i_umull(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu", op.va, op)
    def i_umull(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu", op.va, op)

    def i_mla(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        src3 = self.getOperValue(op, 3)

        val = (src1 * src2 + src3) & 0xffffffff

        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, 4))
            self.setFlag(PSR_Z_bit, not val)





    def i_cps(self, op):
        logger.warn("CPS: 0x%x  %r" % (op.va, op))

    def i_pld2(self, op):
        logger.warn("FIXME: 0x%x: %s - in emu" % (op.va, op))

    def _getCoProc(self, cpnum):
        if cpnum > 15:
            raise Exception("Emu error: Attempting to access coproc %d (max: 15)" % cpnum)

        coproc = self.coprocs[cpnum]
        return coproc


    # Coprocessor Instructions
    def i_stc(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.stc(op.opers)

    def i_ldc(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.ldc(op.opers)

    def i_cdp(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.cdp(op.opers)

    def i_mrc(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.mrc(op.opers)

    def i_mrrc(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.mrrc(op.opers)

    def i_mcr(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.mrrc(op.opers)

    def i_mcrr(self, op):
        cpnum = op.opers[0].val
        coproc = self._getCoProc(cpnum)
        coproc.mcrr(op.opers)

    def i_nop(self, op):
        pass

    i_dmb = i_nop
    i_dsb = i_nop
    i_isb = i_nop

    
        ############################################## WORK IN PROGRESS ###############################

    """
        elif isinstance(oper, e_arm.i386RegMemOper):
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
"""
    def __get_dest_maxes(self, op):
        tsize = op.opers[0].tsize
        smax = e_bits.s_maxes[tsize]
        umax = e_bits.u_maxes[tsize]
        return smax, umax

    def i_adc(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        # FIXME this is wrong!
        #if self.getFlag(EFLAGS_CF):
        #    v2 = v2 + 1

        #self.effSetVariable('eflags_zf', eq(add, Const(0)))
        self.setOperObj(op, 0, v1 + v2)

    def i_add(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        dsize = op.opers[0].tsize
        dmax  = e_bits.s_maxes[dsize]
        ssize = op.opers[1].tsize

        smax, umax = self.__get_dest_maxes(op)

        add = o_add(v1, v2, dsize)
        self.setOperObj(op, 0, add)

        #self.effSetVariable('eflags_gt', gt(v1, v2))
        #self.effSetVariable('eflags_lt', lt(v1, v2))
        #self.effSetVariable('eflags_sf', lt(v1, v2))
        #self.effSetVariable('eflags_eq', eq(v1+v2, 0))

    def i_and(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        obj = o_and(v1, v2, v1.getWidth())

        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0

        self.setOperObj(op, 0, obj)

    def i_bt(self, op):
        ''' 
        selects a bit in a bit string
        '''
        bit_base = self.getOperObj(op, 0)
        bit = self.getOperObj(op, 1)
        # if bit >= bit_base.getWidth()*8: throw a fit.

        val = (bit_base >> bit) & Const(1, 1)
        self.effSetVariable('eflags_cf', (eq(val, Const(1,1))))
        self.effSetVariable('eflags_gt', (eq(val, Const(0,1))))
        self.effSetVariable('eflags_lt', (ne(val, Const(0,1))))
        self.effSetVariable('eflags_sf', (ne(val, Const(0,1))))
        self.effSetVariable('eflags_eq', (eq(val, Const(0,1))))

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
        self.effSetVariable('eflags_cf', gt(v2, v1)) #
        self.effSetVariable('eflags_gt', gt(v1, v2)) # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2)) # v1 - v2 == 0 :: v1 == v2

    def i_dec(self, op):
        v1 = self.getOperObj(op, 0)
        one = Const(1, self._psize)

        sub = o_sub(v1, one, v1.getWidth())

        self.effSetVariable('eflags_gt', gt(v1, one)) # v1 - 1 > 0 :: v1 > 1
        self.effSetVariable('eflags_lt', lt(v1, one)) # v1 - 1 < 0 :: v1 < 1
        self.effSetVariable('eflags_sf', lt(v1, one)) # v1 - 1 < 0 :: v1 < 1
        self.effSetVariable('eflags_eq', eq(v1, one)) # v1 - 1 == 0 :: v1 == 1

        self.setOperObj(op, 0, sub)

    def i_div(self, op):
        oper = op.opers[0]
        divbase = self.getOperObj(op, 1)

        if oper.tsize == 1:
            # TODO: this is broken
            ax = self._reg_ctx._xlateToNativeReg(e_i386.REG_AX, Var('eax', self._psize))
            quot = ax / divbase
            rem  = ax % divbase
            # TODO: this is broken
            self.effSetVariable('eax', (quot << 8) + rem)

        elif oper.tsize == 2:
            raise Exception("16 bit divide needs help!")

        elif oper.tsize == 4:
            eax = Var('eax', self._psize)
            edx = Var('edx', self._psize)

            #FIXME 16 bit over-ride
            tot = (edx << Const(32, self._psize)) + eax
            quot = tot / divbase
            rem = tot % divbase
            self.effSetVariable('eax', quot)
            self.effSetVariable('edx', rem)
            #FIXME maybe we need a "check exception" effect?

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

        #print "FIXME: IMUL FLAGS only valid for POSITIVE results"
        f = gt(res, Const(e_bits.s_maxes[dsize/2], dsize))
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

        f = gt(res, Const(e_bits.u_maxes[dsize/2], dsize))
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
        return self._cond_jmp(op, cnot(Var('eflags_lt', self._psize)))

    def i_jc(self, op):
        return self._cond_jmp(op, Var('eflags_cf', self._psize))

    def i_je(self, op):
        return self._cond_jmp(op, Var('eflags_eq', self._psize))

    def _cond_jmp(self, op, cond):
        # Construct the tuple for the conditional jump
        return (
                ( self.getOperObj(op, 0), cond ),
                ( Const(op.va + len(op), self._psize), cnot(cond)), 
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

            return [( Const(tva, self._psize), eq(tgt, Const(tva, self._psize)) ) for fr,tva,tp,flag in self.vw.getXrefsFrom(op.va) if tp == REF_CODE]

    def i_jne(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_eq', self._psize)))

    i_jng = i_jle
    i_jnge = i_jl
    i_jnl = i_jge
    i_jnle = i_jg

    #def i_jno(self, op):
        #if self.cond_no():   return self.getOperValue(op, 0)

    #def i_jnp(self, op):
        #if self.cond_np():   return self.getOperValue(op, 0)

    def i_jns(self, op):
        return self._cond_jmp(op, cnot(Var('eflags_sf', self._psize)))

    i_jnz = i_jne

    #def i_jo(self, op):
        #if self.cond_o():    return self.getOperValue(op, 0)

    #def i_jp(self, op):
        #if self.cond_p():    return self.getOperValue(op, 0)

    #i_jpe = i_jp
    #i_jpo = i_jnp

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
        #if self.getFlag(EFLAGS_DF):
            #esi -= 4
            #edi -= 4

        #else:
            #esi += 4
            #edi += 4
        #print 'FIXME how to handle DF bit?'

        self.effSetVariable(self.__srcp__, si + Const(4, self._psize))
        self.effSetVariable(self.__destp__, di + Const(4, self._psize))

    def i_movsx(self, op):
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        v2 = o_sextend( self.getOperObj(op,1), Const(ssize, self._psize))
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
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 | v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0
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
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0
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
        self.effSetVariable('eflags_sf', lt(res, Const(0, self._psize))) # v1 | v2 < 0
        self.effSetVariable('eflags_eq', eq(res, Const(0, self._psize))) # v1 & v2 == 0

        self.setOperObj(op, 0, res)

    def i_sbb(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_sub(v1, v2, v1.getWidth()) # FIXME borrow!
        self.effSetVariable('eflags_gt', gt(v1, v2)) # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2)) # v1 - v2 == 0 :: v1 == v2
        self.setOperObj(op, 0, v1 - v2)

    def i_setnz(self, op):
        # FIXME
        self.setOperObj(op, 0, Const(1, self._psize)) #cnot(Var('eflags_eq', self._psize)))

    def i_setz(self, op):
        # FIXME
        self.setOperObj(op, 0, Const(0, self._psize)) #Var('eflags_eq', self._psize))

    def i_shl(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        #if v2.isDiscrete() and v2.solve() > 0xff:
            #v2 = v2 & 0xff

        # No effect (not even flags) if shift is 0
        #if v2.solve() == 0:
            #return

        self.setOperObj(op, 0, v1 << v2)

        u = UNK(v1, v2) # COP OUT FOR NOW...
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', u)
        self.effSetVariable('eflags_eq', u)

    def i_shr(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        #if v2.isDiscrete() and v2.solve() > 0xff:
            #v2 = v2 & 0xff

        self.setOperObj(op, 0, v1 >> v2)

        u = UNK(v1, v2) # COP OUT FOR NOW...
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
        self.effSetVariable('eflags_gt', gt(v1, v2)) # v1 - v2 > 0 :: v1 > v2
        self.effSetVariable('eflags_lt', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_sf', lt(v1, v2)) # v1 - v2 < 0 :: v1 < v2
        self.effSetVariable('eflags_eq', eq(v1, v2)) # v1 - v2 == 0 :: v1 == v2
        self.setOperObj(op, 0, obj)

    def i_test(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_and(v1, v2, v1.getWidth())
        u = UNK(v1, v2)

        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', lt(obj, Const(0, self._psize))) # ( SF != OF ) ( OF is cleared )

        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0

    def i_xadd(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        res = o_add(v1, v2, v1.getWidth())
        self.setOperObj(op, 0, res)
        self.setOperObj(op, 1, v1)
        #self.effSetVariable('eflags_gt', gt(v1, v2))
        #self.effSetVariable('eflags_lt', lt(v1, v2))
        #self.effSetVariable('eflags_sf', lt(v1, v2))
        #self.effSetVariable('eflags_eq', eq(v1+v2, 0))

    def i_xor(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        obj = o_xor(v1, v2, v1.getWidth())
        u = UNK(v1, v2)
        self.effSetVariable('eflags_gt', u)
        self.effSetVariable('eflags_lt', u)
        self.effSetVariable('eflags_sf', lt(obj, Const(0, self._psize))) # v1 & v2 < 0
        self.effSetVariable('eflags_eq', eq(obj, Const(0, self._psize))) # v1 & v2 == 0
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
        self.effSetVariable(self.__sp__, o_add(Var(self.__sp__, self._psize), Const(self._psize, self._psize), self._psize))

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
            val = oper << Const(bitsize-bitnum, self._psize)
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

#class i386SymbolikTranslator(IntelSymbolikTranslator):
    #__arch__ = e_i386.i386Module
    #__ip__ = 'eip' # we could use regctx.getRegisterName if we want.
    #__sp__ = 'esp' # we could use regctx.getRegisterName if we want.
    #__bp__ = 'ebp' # we could use regctx.getRegisterName if we want.
    #__srcp__ = 'esi'
    #__destp__ = 'edi'


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
        self.effSetVariable('bp', Mem(esp + Const(8, self._psize), Const(4, self._psize)))
        self.effSetVariable('ebx', Mem(esp + Const(16, self._psize), Const(4, self._psize)))
        self.effSetVariable('edx', Mem(esp + Const(20, self._psize), Const(4, self._psize)))
        self.effSetVariable('ecx', Mem(esp + Const(24, self._psize), Const(4, self._psize)))
        self.effSetVariable('eax', Mem(esp + Const(28, self._psize), Const(4, self._psize)))
        self.effSetVariable('esp', esp + Const(32, self._psize))

    def i_ror(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)
        self.setOperObj(op, 0, ((v1 >> v2) | (v1 << ( Const(op.opers[0].tsize*8, self._psize) - v2))))

        # XXX - set cf flag with last bit moved

    def i_rol(self, op):
        v1 = self.getOperObj(op, 0)
        v2 = self.getOperObj(op, 1)

        self.setOperObj(op, 0, ((v1 << v2) | (v1 >> ( Const(op.opers[0].tsize*8, self._psize) - v2))))
        # XXX - set cf flag with last bit moved

    def i_stosd(self, op):
        #eax = self.getRegObj(e_i386.REG_EAX)
        #edi = self.getRegObj(e_i386.REG_EDI)
        # FIXME omg segments in symboliks?
        #base,size = self.segments[SEG_ES]
        di = Var(self.__destp__, self._psize)
        self.effWriteMemory(di, Const(self._psize, self._psize), Var('eax', self._psize))
        # FIXME flags?
        #if self.getFlag(e_i386.EFLAGS_DF):
            #edi -= 4
        #else:
            #edi += 4
        #print 'FIXME DF IN stosd'
        di += Const(4, self._psize)
        self.effSetVariable(self.__destp__, di)

class A32ArgDefSymEmu(ArgDefSymEmu):
    __xlator__ = A32SymbolikTranslator

class A32SymCallingConv(vsym_callconv.SymbolikCallingConvention):
    __argdefemu__ = A32ArgDefSymEmu

class ArmCall(A32SymCallingConv, e_arm.ArmArchitectureProcedureCall):
    pass

class A32SymFuncEmu(vsym_analysis.SymbolikFunctionEmulator):

    __width__ = 4

    #def __init__(self, vw, initial_sp=0xbfbff000):
    def __init__(self, vw):
        vsym_analysis.SymbolikFunctionEmulator.__init__(self, vw)
        self.setStackBase(0xbfbff000, 16384)

        self.addCallingConvention('armcall', ArmCall())
        # FIXME possibly decide this by platform/format?
        self.addCallingConvention(None, ArmCall())

        #self.addFunctionCallback('ntdll.eh_prolog', self._eh_prolog)
        #self.addFunctionCallback('ntdll.seh3_prolog', self._seh3_prolog)
        #self.addFunctionCallback('ntdll.seh3_epilog', self._seh3_epilog)
        #self.addFunctionCallback('ntdll._alloca_probe', self.alloca_probe)

        #self.writeSymMemory( Mem(Var('fs') + 292, 4)

    def getStackCounter(self):
        return self.getSymVariable('sp')

    def setStackCounter(self, symobj):
        self.setSymVariable('sp', symobj)

    def _eh_prolog(self, emu, fname, argv):
        
        # swap out [ sp ] (saved eip) to bp
        # and set bp to current sp (std frame)
        bp = emu.getSymVariable('bp')
        sp = emu.getSymVariable('sp')
        eax = emu.getSymVariable('eax')
        emu.writeSymMemory(sp, bp)
        emu.setSymVariable('bp', sp)

        # now carry out 3 symbolik pushes
        sp -= Const(4, 4)
        emu.writeSymMemory(sp, Var('eh_ffffffff',4))
        sp -= Const(4, 4)
        emu.writeSymMemory(sp, eax)
        sp -= Const(4, 4)
        emu.writeSymMemory(sp, Var('eh_c0c0c0c0',4))
        self.setSymVariable('sp', sp)

        return eax

    def alloca_probe(self, emu, fname, argv):
        sp = emu.getSymVariable('sp')
        eax = emu.getSymVariable('eax')
        # Update the stack size if eax is discrete
        if eax.isDiscrete(emu=emu):
            stackadd = eax.solve(emu=emu)
            stackadd += 4096 - (stackadd % 4096)
            stacksize = emu.getStackSize()
            emu.setStackSize( stacksize + stackadd )

        emu.setSymVariable('sp', sp-eax)
        #if eax < 0x1000:
            #eax -= Const(4, self.__width__)
            #emu.setSymVariable('sp', sp-eax)
        #else:
            #while eax > 0x1000:
                #eax -= Const(0x1000, self.__width__)
                #emu.setSymVariable('sp', sp-Const(0x1000, self.__width__))
                #sp -= Const(0x1000, self.__width__)
            #emu.setSymVariable('sp', sp-eax)

    def _seh3_prolog(self, emu, fname, argv):

        scopetable, localsize = argv
        sp = emu.getSymVariable('sp')

        emu.writeSymMemory(sp + Const(4, self.__width__),  emu.getSymVariable('bp'))
        emu.writeSymMemory(sp, scopetable)
        emu.writeSymMemory(sp - Const(4, self.__width__), Var('ntdll.seh3_handler', 4))     # push
        emu.writeSymMemory(sp - Const(8, self.__width__), Var('saved_seh3_scopetable', 4))  # push
        emu.writeSymMemory(sp - Const(12, self.__width__), emu.getSymVariable('ebx'))
        emu.writeSymMemory(sp - Const(16, self.__width__), emu.getSymVariable('esi'))
        emu.writeSymMemory(sp - Const(20, self.__width__), emu.getSymVariable('edi'))
        emu.setSymVariable('sp', (sp - Const(20, self.__width__)) - localsize)
        emu.setSymVariable('bp', (sp + Const(4, self.__width__)))

        return scopetable

    def _seh3_epilog(self, emu, fname, argv):
        edi = emu.getSymVariable('edi')
        esi = emu.getSymVariable('esi')
        ebx = emu.getSymVariable('ebx')

        sp = emu.getSymVariable('sp')
        # FIXME do seh restore...
        emu.setSymVariable('edi', edi)
        emu.setSymVariable('esi', esi)
        emu.setSymVariable('ebx', ebx)
        bp = emu.getSymVariable('bp')
        savedbp = emu.readSymMemory(bp, Const(4, self.__width__))
        emu.setSymVariable('bp', savedbp)
        emu.setSymVariable('sp', bp + Const(4, self.__width__))
        return emu.getSymVariable('eax')

class A32SymbolikAnalysisContext(vsym_analysis.SymbolikAnalysisContext):
    __xlator__ = A32SymbolikTranslator
    __emu__ = A32SymFuncEmu
