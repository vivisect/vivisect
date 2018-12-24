import sys

import envi
import envi.bits as e_bits
import envi.memory as e_mem

import copy
import struct

from envi import *
from regs import *
from const import *
from disasm import *
from envi.archs.ppc import *


MCU_START       = 0x0000
IV_EXT0         = 0x0003
IV_TIMER0       = 0x000b
IV_EXT1         = 0x0013
IV_TIMER1       = 0x001b
INTVECTOR_4     = 0x0023


class PpcCall(envi.CallingConvention):
    '''
    Does not have shadow space like MSx64.
    '''
    arg_def = [(CC_REG, REG_R3 + x) for x in range(7)]
    arg_def.append((CC_STACK_INF, 8))
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_R3)
    flags = CC_CALLEE_CLEANUP
    align = 4
    pad = 0

ppccall = PpcCall()

OPER_SRC = 1
OPER_DST = 0


class PpcEmulator(PpcModule, PpcRegisterContext, envi.Emulator):

    def __init__(self, archmod=None):
        if archmod == None:
            archmod = PpcModule()
        envi.Emulator.__init__(self, archmod=archmod)
                
        PpcRegisterContext.__init__(self)
        PpcModule.__init__(self)

        self.addCallingConvention("ppccall", ppccall)

    
    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(REG_FLAGS)
        # On PDE, assume we're setting enough flags...
        if flags ==  None:
            flags = 0

        if state:
            flags |= (1<<which)
        else:
            flags &= ~(1<<which)
        self.setRegister(REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_FLAGS)
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & (1<<which))

    def makeOpcode(self, bytes, offset=0, va=0):
        """
        Parse a sequence of bytes out into an envi.Opcode instance.
        """
        return self._arch_dis.disasm(bytes, offset, va)

    #def makeOpcode(self, pc):
    #    map = self._mem_bytelookup.get(pc & self._mem_mask)
    #    if map == None:
    #        raise envi.SegmentationViolation(pc)
    #    mapva, mperm, mapbytes = map
    #    if not mperm & e_mem.MM_READ:
    #        raise envi.SegmentationViolation(pc)
    #    offset = pc - mapva
    #    return self._arch_dis.disasm(mapbytes, offset, pc)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)

        x = meth(op)
        if x != None:
            self.setProgramCounter(x)
        else:
            pc = self.getProgramCounter()
            pc += op.size
            self.setProgramCounter(pc)

    ####################### Helper Functions ###########################
    def doPush(self, val):
        psize = self.getPointerSize()
        sp = self.getRegister(REG_SP)
        sp += psize
        self.writeMemValue(sp, val, psize)
        self.setRegister(REG_SP, sp)

    def doPop(self):
        psize = self.getPointerSize()
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, psize)
        sp -= psize
        self.setRegister(REG_SP, sp)
        return val

    def logicalAnd(self, op):
        dst = op.opers[OPER_DST].getOperValue(op, self)
        src = op.opers[OPER_SRC].getOperValue(op, self)

        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        dsize = op.opers[OPER_DST].tsize
        ssize = op.opers[OPER_SRC].tsize

        # sign-extend an immediate if needed
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        # Make sure everybody's on the same bit page.
        dst = e_bits.unsigned(dst, dsize)
        src = e_bits.unsigned(src, ssize)

        res = src & dst

        # FIXME:  SET FLAGS IN CR0 and CR1 and XER?
        raise Exception(' FIXME:  SET FLAGS IN CR0 and CR1 and XER?')
        self.setFlag(EFLAGS_AF, 0) # AF is undefined, but it seems like it is zeroed
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        return res

    # Beginning of Instruction methods
    def i_nop(self, op):
        pass

    ########################### Metric shit-ton of Branch Instructions #############################
    def i_b(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_blr(self, op):
        '''
        blr is actually "ret"
        '''
        return self.getRegister(REG_LR)

    # conditional branches....
    def i_bc(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bca(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bcl(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bcla(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bclr(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bcctr(self, op):
        val = op.opers[OPER_DST].getOperValue(op, self)
        return val

    def i_bdnzf(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_bdzf(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bf(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bdnzt(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_bdzt(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_bt(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bdnz(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        return self.getOperValue(op, 1)

    def i_bdz(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        return self.getOperValue(op, 1)


    def i_bdnzfl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_bdzfl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bfl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdnztl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_bdztl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_btl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdnzl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdzl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)


    def i_bl(self, op):
        self.doPush(op.va + 4)
        return self.getOperValue(op, 0)

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
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_bdzflr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bflr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bdnztlr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_bdztlr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)
           
    def i_btlr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if not self.getOperValue(op, 0):
            return

        return self.getOperValue(op, 1)

    def i_bdnzlr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        return self.getOperValue(op, 1)

    def i_bdzlr(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        return self.getOperValue(op, 1)


    def i_bdnzflrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_bdzflrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bflrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdnztlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_bdztlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_btlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if not self.getOperValue(op, 0):
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdnzlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdzlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        self.doPush(op.va + 4)
        return self.getOperValue(op, 1)


    def i_blrl(self, op):
        self.doPush(op.va + 4)
        return self.getOperValue(op, 0)

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
        print "sync call: %r" % op

    def i_isync(self, op):
        print "isync call: %r" % op

    ######################## arithmetic instructions ##########################
    def i_cmpi(self, op):
        L = self.getOperValue(op, 1)
        rA = self.getOperValue(op, 2)
        if L==0:
            a = e_bits.signed(rA & 0xffffffff, 4)
        else:
            a = rA
        b = e_bits.signed(self.getOperValue(op, 3), 2)

        if a < b:
            c = 8
        elif a > b:
            c = 4
        else:
            c = 2
        # FIXME: what's SO? (it's the 1 bit)

        self.setOperValue(op, 0, c)
        #print "TESTME: cmpi bit setting of the appropriate CR register"

    def setOEFlags(self, results):
        print('addo: make OE flag updates')

    def i_add(self, op):
        '''
        add
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 2)
        result = src1 + src2
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_addo(self, op):
        '''
        add
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 2)
        result = src1 + src2
        self.setOperValue(op, 0, result)
        self.setOEFlags(results)
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_addc(self, op):
        '''
        add
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 2)
        result = src1 + src2
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_addco(self, op):
        '''
        add
        '''
        src1 = self.getopervalue(op, 1)
        src2 = self.getopervalue(op, 2) # fixme: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 2)
        carry = self.getRegister(REG_CA)
        
        result = src1 + src2 + carry
        self.setopervalue(op, 0, result)

        self.setOEFlags(results)
        if op.iflags & if_rc: self.setflags(results, 0)


    def i_addi(self, op):
        '''
        add immediate
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 2)
        result = src1 + src2
        self.setOperValue(op, 0, result)

    def i_addis(self, op):
        '''
        add immediate shifted
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 <<= 16
        src2 = e_bits.signed(src2, 4)

        result = src1 + src2
        self.setOperValue(op, 0, result)

    def i_addic(self, op):
        '''
        add immediate carry
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        carry = e_bits.is_signed_carry((src1 + src2), 8, src1)
        src2 = e_bits.signed(src2, 2)
        result = src1 + src2

        self.setOperValue(op, 0, result)
        self.setRegister(REG_CA, carry)
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_addme(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = 0xffffffffffffffff
        carry = e_bits.is_signed_carry((src1 + src2), 8, src1)
        result = src1 + src2

        self.setOperValue(op, 0, result)
        self.setRegister(REG_CA, carry)
        #OV = (carrym ^ carrym+1)   # FIXME::::  NEED TO UNDERSTAND THIS ONE....
        #SO = SO | (carrym ^ carrym+1) 
        if op.iflags & IF_RC: self.setFlags(results, 0, SO=SO)

    def i_addmeo(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = 0xffffffffffffffff
        carry = e_bits.is_signed_carry((src1 + src2), 8, src1)
        result = src1 + src2

        self.setOperValue(op, 0, result)
        self.setRegister(REG_CA, carry)
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_addw(self, op):
        '''
        add word
        '''
        src1 = self.getOperValue(op, 1)
        src1 = e_bits.signed(src1, 4)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 4)
        result = e_bits.signed(src1 + src2, 4)
        self.setOperValue(op, 0, result)
   
    def i_addwss(self, op):
        '''
        add word
        '''
        src1 = self.getOperValue(op, 1)
        src1 = e_bits.signed(src1, 4)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        src2 = e_bits.signed(src2, 4)
        result = e_bits.signed(src1 + src2, 4)

        SO = None
        sum31 = ((result >> 32) & 1)
        sum32 = ((result >> 31) & 1) 
        OV = sum31 ^ sum32
        if OV:
            if sum31: 
                result = 0xffffffff80000000
            else:
                result = 0x7fffffff
            SO = self.getSO() | OV

        self.setOperValue(op, 0, result)
        self.setFlags(results, 0, SO)
   
    def i_or(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        self.setOperValue(op, 0, (dst | src))
        if op.iflags & IF_RC: self.setFlags(results, 0)

    i_ori = i_or

    def i_oris(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        src <<= 16

        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        self.setOperValue(op, 0, (dst | src))
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def i_orc(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        src = -src

        # PDE
        if dst == None or src == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        self.setOperValue(op, 0, (dst | src))
        if op.iflags & IF_RC: self.setFlags(results, 0)

    def getCr(self, crnum):
        '''
        get a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        cr = self.getRegister(REG_CR)
        return (cr >> ((7-crnum) * 4)) & 0xf

    def setCr(self, crnum, flags):
        '''
        set a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        cr = self.getRegister(REG_CR)
        cr &= (cr_mask[crnum])
        cr |= (flags << ((7-crnum) * 4))
        self.setRegister(REG_CR, cr)

    def setFlags(self, result, crnum=0, SO=None):
        '''
        easy way to set the flags, reusable by many different instructions
        '''
        flags = 0
        if result > 0:
            flags |= FLAGS_GT
        elif result < 0:
            flags |= FLAGS_LT
        else:
            flags |= FLAGS_EQ

        if SO == None:
            SO = bool(self.getCr(crnum) & FLAGS_SO)
        
        flags |= (SO << FLAGS_SO_bitnum)

        self.setCr(crnum, flags)

    def getSOflag(self, crnum=0):
        cr = self.getCr(crnum)
        return cr >> FLAGS_SO_bitnum



    ########################## LOAD/STORE INSTRUCTIONS ################################
    # lbz and lbzu access memory directly from operand[1]
    def i_lbz(self, op):
        op.opers[1].tsize = 1
        if op.opers[0].reg == 0:
            src = 0
        else:
            src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_lbzu(self, op):
        op.opers[1].tsize = 1
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lbze = i_lbz
    i_lbzue = i_lbzu

    # lbzx and lbzux load an address by adding operand[1] and operand[2]
    def i_lbzx(self, op):
        op.opers[1].tsize = 1
        src = self.getOperValue(op, 1)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 1)
        self.setOperValue(op, 0, val)

    def i_lbzux(self, op):
        op.opers[1].tsize = 1
        src = self.getOperValue(op, 1)
        src += self.getOperValue(op, 2)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 1)
        self.setOperValue(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lbzxe = i_lbzx
    i_lbzuxe = i_lbzux

    # lhz and lhzu access memory directly from operand[1]
    def i_lhz(self, op):
        op.opers[1].tsize = 2
        if op.opers[0].reg == 0:
            src = 0
        else:
            src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_lhzu(self, op):
        op.opers[1].tsize = 2
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lhze = i_lhz
    i_lhzue = i_lhzu

    # lhzx and lhzux load an address by adding operand[1] and operand[2]
    def i_lhzx(self, op):
        src = self.getOperValue(op, 1)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 2)
        self.setOperValue(op, 0, val)

    def i_lhzux(self, op):
        src = self.getOperValue(op, 1)
        src += self.getOperValue(op, 2)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 2)
        self.setOperValue(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lhzxe = i_lhzx
    i_lhzuxe = i_lhzux


    # lwz and lwzu access memory directly from operand[1]
    def i_lwz(self, op):
        op.opers[1].tsize = 4
        if op.opers[0].reg == 0:
            src = 0
        else:
            src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_lwzu(self, op):
        op.opers[1].tsize = 4
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lwze = i_lwz
    i_lwzue = i_lwzu

    # lwzx and lwzux load an address by adding operand[1] and operand[2]
    def i_lwzx(self, op):
        src = self.getOperValue(op, 1)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 4)
        self.setOperValue(op, 0, val)

    def i_lwzux(self, op):
        src = self.getOperValue(op, 1)
        src += self.getOperValue(op, 2)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 4)
        self.setOperValue(op, 0, val)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)

    i_lwzxe = i_lwzx
    i_lwzuxe = i_lwzux


    def i_lmw(self, op):
        op.opers[1].tsize = 4
        startreg = op.opers[0].reg
        regcnt = 32-startreg

        startaddr = self.getOperAddr(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            word = self.readMemValue(startaddr + offset, 4)
            self.setRegister(regidx, word)
            offset += 4

    def i_stmw(self, op):
        op.opers[1].tsize = 4
        startreg = op.opers[0].reg
        regcnt = 32-startreg

        startaddr = self.getOperAddr(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            word = self.getRegister(regidx)
            self.writeMemValue(startaddr + offset, word & 0xffffffff, 4)
            offset += 4
    
    def i_stb(self, op):
        op.opers[1].tsize = 1
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
   
    def i_stbu(self, op):
        op.opers[1].tsize = 1
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)
    
    def i_sth(self, op):
        op.opers[1].tsize = 2
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
   
    def i_sthu(self, op):
        op.opers[1].tsize = 2
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)
    
    def i_stw(self, op):
        op.opers[1].tsize = 4
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
   
    def i_stwu(self, op):
        op.opers[1].tsize = 4
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)
    
    def i_movfrom(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_mov(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_mflr(self, op):
        src = self.getRegister(REG_LR)
        self.setOperValue(op, 0, src)

    def i_mtlr(self, op):
        src = self.getOperValue(op, 0)
        self.setRegister(REG_LR, src)

    def i_mfspr(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_mtspr(self, op):
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    i_li = i_movfrom
    i_mr = i_movfrom

    def i_lis(self, op):
        src = self.getOperValue(op, 1)
        #self.setOperValue(op, 0, (src<<16))
        # technically this is incorrect, but since we disassemble wrong, we emulate wrong.
        self.setOperValue(op, 0, (src))


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

    '''
    i_se_bclri                         rX,UI5
    i_se_bgeni                         rX,UI5
    i_se_bmaski                        rX,UI5
    i_se_bseti                         rX,UI5
    i_se_btsti                         rX,UI5
    i_e_cmpli instructions, or CR0 for the se_cmpl, e_cmp16i, e_cmph16i, e_cmphl16i, e_cmpl16i, se_cmp,
    i_se_cmph, se_cmphl, se_cmpi, and se_cmpli instructions, is set to reflect the result of the comparison. The
    i_e_cmp16i                             rA,SI
    i_e_cmpi                   crD32,rA,SCI8
    i_se_cmp                              rX,rY
    i_se_cmpi                           rX,UI5
    i_e_cmph                        crD,rA,rB
    i_se_cmph                            rX,rY
    i_e_cmph16i                           rA,SI
    i_e_cmphl                       crD,rA,rB
    i_se_cmphl                           rX,rY
    i_e_cmphl16i                         rA,UI
    i_e_cmpl16i                           rA,UI
    i_e_cmpli                  crD32,rA,SCI8
    i_se_cmpl                             rX,rY
    i_se_cmpli                      rX,OIMM
    i_se_cmph, se_cmphl, se_cmpi, and se_cmpli instructions, is set to reflect the result of the comparison. The
    i_e_cmph                        crD,rA,rB
    i_se_cmph                            rX,rY
    i_e_cmph16i                           rA,SI
    i_e_cmphl                       crD,rA,rB
    i_se_cmphl                           rX,rY
    i_e_cmphl16i                         rA,UI
    i_e_crnand               crbD,crbA,crbB
    i_e_crnor               crbD,crbA,crbB
    i_e_cror                 crbD,crbA,crbB
    i_e_crorc               crbD,crbA,crbB
    i_e_cror                 crbD,crbA,crbB
    i_e_crorc               crbD,crbA,crbB
    i_e_crxor                crbD,crbA,crbB
    i_se_illegal
    i_se_illegal is used to request an illegal instruction exception. A program interrupt is generated. The contents
    i_se_isync
    i_se_isync instruction have been performed.
    i_e_lmw                         rD,D8(rA)
    i_e_lwz                           rD,D(rA)                                                             (D-mode)
    i_se_lwz                       rZ,SD4(rX)                                                            (SD4-mode)
    i_e_lwzu                         rD,D8(rA)                                                            (D8-mode)
    i_e_mcrf                          crD,crS
    i_se_mfar                         rX,arY
    i_se_mfctr                             rX
    i_se_mflr                              rX
    i_se_mr                             rX,rY
    i_se_mtar                         arX,rY
    i_se_mtctr                             rX
    i_se_mtlr                              rX
    i_se_rfci
    i_se_rfi
    i_e_rlw                           rA,rS,rB                                                               (Rc = 0)
    i_e_rlw.                          rA,rS,rB                                                               (Rc = 1)
    i_e_rlwi                          rA,rS,SH                                                               (Rc = 0)
    i_e_rlwi.                         rA,rS,SH                                                               (Rc = 1)
    i_e_rlwimi             rA,rS,SH,MB,ME
    i_e_rlwinm              rA,rS,SH,MB,ME
    i_e_rlwimi             rA,rS,SH,MB,ME
    i_e_rlwinm              rA,rS,SH,MB,ME
    i_se_sc provides the same functionality as sc without the LEV field. se_rfi, se_rfci, se_rfdi, and se_rfmci
    i_se_sc
    i_se_sc is used to request a system service. A system call interrupt is generated. The contents of the MSR
    i_e_stmw                        rS,D8(rA)                                                               (D8-mode)
    i_se_sub                            rX,rY
    i_se_subf                           rX,rY
    i_e_subfic                    rD,rA,SCI8                                                                  (Rc = 0)
    i_e_subfic.                   rD,rA,SCI8                                                                  (Rc = 1)
    i_se_subi                       rX,OIMM                                                                 (Rc = 0)
    i_se_subi.                      rX,OIMM                                                                 (Rc = 1)
    '''


"""
import envi.archs.ppc as e_ppc
import envi.memory as e_m

t_arch = e_ppc.PpcModule()
e = t_arch.getEmulator()
m = e_m.MemoryObject()
e.setMemoryObject(m)
m.addMemoryMap(0x0000,0777,"memmap1", "\xff"*1024)

"""

