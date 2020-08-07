# -*- coding: iso-8859-15 -*-

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

'''
PowerPC Emulation code.  most of this code is written based on the information from the 
EREF, Rev. 1 (EIS 2.1)  
(aka EREF_RM.pdf from http://cache.freescale.com/files/32bit/doc/ref_manual/EREF_RM.pdf)

that documentation is specific, and generally good, with one Major exception:  
    they think that 0 is the Most Significant Bit!

this convention flies in the face of most other architecture reference manuals, and the
way that the authors of this module themselves, think of bit numbering for instructions.
therefore, some places may seem a little confusing if compared to the EREF.

MASK and ROTL32 have specifically been coded to allow the emulated instructions to map 
directly to the EREF docs execution pseudocode.
'''

class PpcCall(envi.CallingConvention):
    '''
    PowerPC Calling Convention.  
    '''
    arg_def = [(CC_REG, REG_R3 + x) for x in range(8)]
    arg_def.append((CC_STACK_INF, 8))
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_R3)
    flags = CC_CALLEE_CLEANUP
    align = 4
    pad = 0

ppccall = PpcCall()

OPER_SRC = 1
OPER_DST = 0


class Trap(Exception):
    pass

def MASK(b, e):
    '''
    helper to create masks.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    if e < b:
        delta = b - e - 1
        real_shift = 63 - b + 1
        mask = e_bits.bu_maxes[delta] << real_shift
        mask ^= 0xffffffffffffffff
        return mask

    delta = e - b + 1
    real_shift = 63 - e
    return e_bits.bu_maxes[delta] << (real_shift)

def ROTL32(x, y, psize=8):
    '''
    helper to rotate left, 32-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    tmp = x >> (32-y)
    x |= (x<<32)
    return ((x << y) | tmp) & e_bits.u_maxes[psize]
    
def ROTL64(x, y, psize=8):
    '''
    helper to rotate left, 64-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    tmp = x >> (64-y)
    return ((x << y) | tmp) & e_bits.u_maxes[psize]
    
def getCarryBitAtX(bit, add0, add1):
    '''
    return the carry bit at bit x.
    '''
    a0b = (add0 & e_bits.b_masks[bit])
    a1b = (add1 & e_bits.b_masks[bit])
    results = (a0b + a1b) >> (bit)
    #print "getCarryBitAtX (%d): 0x%x  0x%x  (%d)" % (bit, a0b, a1b, results)
    return results

class PpcAbstractEmulator(envi.Emulator):

    def __init__(self, archmod=None, psize=8):
        self.psize = psize
        envi.Emulator.__init__(self, archmod=archmod)
                
        self.addCallingConvention("ppccall", ppccall)

        self.spr_read_handlers = {
        }
        self.spr_write_handlers = {
            REG_L1CSR1: self._swh_L1CSR1,
        }


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

    def _populateOpMethods(self):
        for name in dir(self):
            if name.startswith("i_"):
                self.op_methods[name[2:]] = getattr(self, name)
                # add in the "." suffix because instrs which have RC set are handled in same func
                self.op_methods[name[2:] + "."] = getattr(self, name)

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

    ########################### Flag Helpers #############################
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

    def getXERflags(self):
        '''
        get a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        xer = self.getRegister(REG_XER)
        xer >>= 29
        xer &= 0x7
        return xer

    def setXERflags(self, flags):
        '''
        set XER flags
            SO
            OV
            CA
        '''
        xer = self.getRegister(REG_XER)
        xer & 0x1fffffff
        xer |= (flags << 29)
        self.setRegister(REG_XER, xer)

    def setFlags(self, result, crnum=0, SO=None):
        '''
        easy way to set the flags, reusable by many different instructions
        '''
        result = e_bits.signed(result, self.psize)
        flags = 0
        if result > 0:
            flags |= FLAGS_GT
        elif result < 0:
            flags |= FLAGS_LT
        else:
            flags |= FLAGS_EQ

        if SO == None:
            SO = self.getRegister(REG_SO)
        
        #print "0 setFlags( 0x%x, 0x%x)" % (result, flags)
        flags |= (SO << FLAGS_SO_bitnum)
        #print "1 setFlags( 0x%x, 0x%x)" % (result, flags)

        self.setCr(crnum, flags)

    def trap(self, op):
        raise Trap('0x%x: %r' % (op.va, op))
        # FIXME: if this is used for software permission transition (like a kernel call), 
        #   this approach may need to be rethought

    # Beginning of Instruction methods
    def i_nop(self, op):
        pass

    ########################### Metric shit-ton of Branch Instructions #############################
    def i_b(self, op):
        '''
        Branch!  no frills.
        '''
        val = self.getOperValue(op, OPER_DST)
        return val

    def i_bl(self, op):
        '''
        branch with link, the basic CALL instruction
        '''
        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 0)

    def i_blr(self, op):
        '''
        blr is actually "ret"
        '''
        return self.getRegister(REG_LR)

    def i_bctrl(self, op):
        nextva = op.va + len(op)
        ctr  = self.getRegister(REG_CTR)
        self.setRegister(REG_LR, nextva)
        return ctr


    # conditional branches....
    def i_bc(self, op, aa=False, lk=False, tgtreg=None):
        bo = self.getOperValue(op, 0)
        bi = self.getOperValue(op, 1)
        nextva = op.va + len(op)
        ctr = self.getRegister(REG_CTR)
        cr = self.getRegister(REG_CR)

        # if we provide a tgtreg, it's an  instruction-inherent register (eg. bclr)
        if tgtreg is None:
            tgt = self.getOperValue(op, 2)
        else:
            tgt = self.getRegister(tgtreg)

        bo_0 = bo & 0x10
        bo_1 = bo & 0x8
        bo_2 = bo & 0x4
        bo_3 = bo & 0x2
        crmask = 1 << (32 - bi)

        # if tgtreg is REG_CTR, we can't decrement it...
        if not bo_2 and tgtreg != REG_CTR:
            ctr -= 1
            self.setRegister(REG_CTR, ctr)

        # ctr_ok ← BO2 | ((CTRm:63 ≠ 0) ⊕ BO3)
        ctr_ok = bool(bo_2)
        if not ctr_ok:
            if (ctr & e_bits.u_maxes[self.psize]) != 0 and not bo_3: ctr_ok = True
            elif (not (ctr & e_bits.u_maxes[self.psize]) != 0) and bo_3: ctr_ok = True

        # cond_ok = BO0 | (CRBI+32 ≡ BO1)
        cond_ok = bo_0 or (bool(cr & crmask) == bool(bo_1))

        # always update LR, regardless of the conditions.  odd.
        if lk:
            self.setRegister(REG_LR, nextva)

        # if we don't meet the requirements, bail
        if not (ctr_ok and cond_ok):
            return

        # if we meet the required conditions:
        if not aa:  # if *not* ABSOLUTE address
            tgt += nextva

        return tgt

    def i_bca(self, op):
        return self.i_bc(op, aa=True)

    def i_bcl(self, op):
        return self.i_bc(op, lk=True)

    def i_bcla(self, op):
        return self.i_bc(op, aa=True, lk=True)

    def i_bclr(self, op):
        return self.i_bc(op, aa=True, lk=True, tgtreg=REG_LR)

    def i_bcctr(self, op):
        return self.i_bc(op, aa=True, lk=True, tgtreg=REG_CTR)

    # bc breakdowns:  decrement, zero/not-zero, true/false, w/link, etc...
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
        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        return self.getOperValue(op, 0)

    def i_bdz(self, op):
        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        return self.getOperValue(op, 0)

    # with link...
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

        self.setRegister(REG_LR, op.va + 4)
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

        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 1)

    def i_bfl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if self.getOperValue(op, 0):
            return

        self.setRegister(REG_LR, op.va + 4)
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

        self.setRegister(REG_LR, op.va + 4)
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

        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 1)
           
    def i_btl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        if not self.getOperValue(op, 0):
            return

        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdnzl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 1)

    def i_bdzl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        self.setRegister(REG_LR, op.va + 4)
        return self.getOperValue(op, 1)


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
        if self.getOperValue(op, 0):
            return

        return self.getRegister(REG_LR)

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
        if not self.getOperValue(op, 0):
            return

        return self.getRegister(REG_LR)

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

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt
           
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

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt

    def i_bflrl(self, op):
        if self.getOperValue(op, 0):
            return

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt

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

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt
           
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

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt
           
    def i_btlrl(self, op):
        if not self.getOperValue(op, 0):
            return

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt

    def i_bdnzlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr == 0:
            return

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt

    def i_bdzlrl(self, op):
        if len(op.opers) != 2:
            print("%s doesn't have 2 opers: %r" % (op.mnem, op.opers))

        ctr = self.getRegister(REG_CTR)
        ctr -= 1
        self.setRegister(REG_CTR, ctr)
        if ctr != 0:
            return

        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt


    def i_blrl(self, op):
        tgt = self.getRegister(REG_LR)
        self.setRegister(REG_LR, op.va + 4)
        return tgt

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

    def i_msync(self, op):
        print "msync call: %r" % op

    ######################## arithmetic instructions ##########################
    def i_cmpwi(self, op, L=0): # FIXME: we may be able to simply use i_cmpw for this...
        # signed comparison for cmpi and cmp
        if len(op.opers) == 3:
            cridx = op.opers[0].field
            raidx = 1
            rbidx = 2
        else:
            cridx = 0
            raidx = 0
            rbidx = 1

        rA = self.getOperValue(op, raidx)
        if L==0:
            a = e_bits.signed(rA & 0xffffffff, 4)
        else:
            a = rA

        b = e_bits.signed(self.getOperValue(op, rbidx), 2)
        SO = self.getRegister(REG_SO)

        if a < b:
            c = 8
        elif a > b:
            c = 4
        else:
            c = 2

        self.setCr(cridx, c|SO)

    def i_cmpw(self, op, L=0):
        # signed comparison for cmpli and cmpl
        if len(op.opers) == 3:
            cridx = op.opers[0].field
            raidx = 1
            rbidx = 2
        else:
            cridx = 0
            raidx = 0
            rbidx = 1

        rA = self.getOperValue(op, raidx)
        rB = self.getOperValue(op, rbidx)
        dsize = op.opers[raidx].tsize
        ssize = op.opers[rbidx].tsize

        if L==0:
            a = e_bits.signed(rA, dsize)
            b = e_bits.signed(rB, ssize)
        else:
            a = e_bits.signed(rA, 8)
            b = e_bits.signed(rB, 8)
        SO = self.getRegister(REG_SO)

        if a < b:
            c = 8
        elif a > b:
            c = 4
        else:
            c = 2

        #print "cmpw: %r  %x  %x  %x" % (cridx, a, b, c)
        self.setCr(cridx, c|SO)

    def i_cmplw(self, op, L=0):
        # unsigned comparison for cmpli and cmpl
        if len(op.opers) == 3:
            cridx = op.opers[0].field
            raidx = 1
            rbidx = 2
        else:
            cridx = 0
            raidx = 0
            rbidx = 1

        rA = self.getOperValue(op, raidx)
        rB = self.getOperValue(op, rbidx)
        dsize = op.opers[raidx].tsize
        ssize = op.opers[rbidx].tsize

        if L==0:
            a = e_bits.unsigned(rA, dsize)
            b = e_bits.unsigned(rB, ssize)
        else:
            a = rA
            b = rB
        SO = self.getRegister(REG_SO)

        if a < b:
            c = 8
        elif a > b:
            c = 4
        else:
            c = 2

        self.setCr(cridx, c|SO)

    i_cmplwi = i_cmplw

    def i_cmpdi(self, op):
        return self.i_cmpwi(op, L=1)

    def i_cmpd(self, op):
        return self.i_cmpw(op, L=1)

    def i_cmpld(self, op):
        return self.i_cmplw(op, L=1)

    def i_cmpldi(self, op):
        return self.i_cmplwi(op, L=1)


    def setCA(self, result):
        '''
        CA flag is always set for addic, subfic, addc, subfc, adde, subfe, addme, subfme, addze, subfze
        '''
        mode = self.getPointerSize() * 8
        ca = bool(result >> mode)
        #print "setCA(0x%x):  %r" % (result, ca)
        self.setRegister(REG_CA, ca)


    def setOEflags(self, result, size, add0, add1, mode=OEMODE_ADDSUBNEG):
        #https://devblogs.microsoft.com/oldnewthing/20180808-00/?p=99445

        # OV = (carrym ^ carrym+1) 
        if mode == OEMODE_LEGACY:
            cm = getCarryBitAtX((size*8), add0, add1)
            cm1 = getCarryBitAtX((size*8)-1, add0, add1)
            ov = cm != cm1
            #print "setOEflags( 0x%x, 0x%x, 0x%x, 0x%x):  cm= 0x%x, cm1= 0x%x, ov= 0x%x" % (result, size, add0, add1, cm, cm1, ov)

        elif mode == OEMODE_ADDSUBNEG:
            cm = getCarryBitAtX((size*8), add0, add1)
            cm1 = getCarryBitAtX((size*8)-1, add0, add1)
            ov = cm != cm1
            #print "setOEflags( 0x%x, 0x%x, 0x%x, 0x%x):  cm= 0x%x, cm1= 0x%x, ov= 0x%x" % (result, size, add0, add1, cm, cm1, ov)

        else:
            # for mul/div, ov is set if the result cannot be contained in 64bits
            ov = bool(result >> 64)


        #SO = SO | (carrym ^ carrym+1) 
        so = self.getRegister(REG_SO)
        so |= ov

        self.setRegister(REG_SO, so)
        self.setRegister(REG_OV, ov)

    def i_add(self, op, oe=False):
        '''
        add
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        uresult = src1 + src2

        src2 = e_bits.signed(src2, 2)
        result = src1 + src2
        
        self.setCA(uresult)
        self.setOperValue(op, 0, result)
        if oe: self.setOEflags(result, self.psize, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addo(self, op):
        return self.i_add(op, oe=True)

    def i_addc(self, op, oe=False):
        '''
        add
        '''
        s2size = op.opers[2].tsize
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        uresult = src1 + src2

        src2 = e_bits.signed(src2, s2size)
        result = src1 + src2
        
        self.setOperValue(op, 0, result)
        self.setCA(uresult)
        if oe: self.setOEflags(uresult, self.psize, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addco(self, op):
        return self.i_addc(op, oe=True)

    def i_adde(self, op, oe=False):
        ra = self.getOperValue(op, 1)
        rb = self.getOperValue(op, 2)
        ca = self.getRegister(REG_CA)

        result = ra + rb + ca

        self.setCA(result)
        if oe: self.setOEflags(result, self.psize, ra, rb + ca)
        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperValue(op, 0, result)

    def i_addeo(self, op):
        return self.i_adde(op, oe=True)

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
        uresult = src1 + src2

        src2 = e_bits.signed(src2, 2)
        result = src1 + src2

        self.setCA(uresult)
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addme(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = 0xffffffffffffffff
        ca = self.getRegister(REG_CA)
        result = src1 + src2 + ca

        self.setOperValue(op, 0, result)

        self.setCA(result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_addmeo(self, op):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = 0xffffffffffffffff
        result = src1 + src2
        carry = e_bits.is_signed_carry(result, 8, src1)

        self.setOperValue(op, 0, result)

        self.setRegister(REG_CA, carry)
        self.setOEflags(result, 4, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result, 0)

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

        SO = self.getRegister(REG_SO)
        sum31 = ((result >> 32) & 1)
        sum32 = ((result >> 31) & 1) 
        OV = sum31 ^ sum32
        if OV:
            if sum31: 
                result = 0xffffffff80000000
            else:
                result = 0x7fffffff
            SO |= OV

        self.setOperValue(op, 0, result)
        self.setFlags(result, 0, SO)
  
    def i_and(self, op):
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2)
        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        result = (src0 & src1)

        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_andi = i_and

    def i_andis(self, op):
        '''
        and immediate shifted
        '''
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2) # FIXME: move signedness here instead of at decode
        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        src2 <<= 16

        result = src0 & src1
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_andc(self, op):
        '''
        and "complement"
        '''
        ssize = op.opers[1].tsize
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2) ^ e_bits.u_maxes[ssize]
        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        result = (src0 & src1)

        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_or(self, op):
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2)
        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        result = (src0 | src1)
        
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_ori = i_or

    def i_oris(self, op):
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2)
        src1 <<= 16

        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        self.setOperValue(op, 0, (src0 | src1))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_orc(self, op):
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2)
        src1 = -src

        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        self.setOperValue(op, 0, (src0 | src1))
        if op.iflags & IF_RC: self.setFlags(result, 0)

    ########################## LOAD/STORE INSTRUCTIONS ################################
    # lbz and lbzu access memory directly from operand[1]
    def i_lbz(self, op):
        op.opers[1].tsize = 1
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
        src = self.getOperValue(op, 1)
        src += e_bits.signed(self.getOperValue(op, 2), 2)
        val = self.readMemValue(src, 1)
        self.setOperValue(op, 0, val)

    def i_lbzux(self, op):
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
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

    def i_lwzu(self, op):
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
    
    def i_stb(self, op, size=1):
        op.opers[1].tsize = size
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)

    def i_sth(self, op):
        return self.i_stb(op, size=2)

    def i_stw(self, op):
        return self.i_stb(op, size=4)

    def i_std(self, op):
        return self.i_stb(op, size=8)
  

    def i_stbu(self, op, size=1):
        op.opers[1].tsize = size
        src = self.getOperValue(op, 0)
        self.setOperValue(op, 1, src)
        # the u stands for "update"... ie. write-back
        op.opers[1].updateReg(self)
    
    def i_sthu(self, op):
        return self.i_stb(op, size=2)
    
    def i_stwu(self, op):
        return self.i_stb(op, size=4)

    def i_stdu(self, op):
        return self.i_stb(op, size=8)


    def i_stbx(self, op, size=1):
        val = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        src += self.getOperValue(op, 2)
        self.writeMemValue(src, val, size)
        self.setOperValue(op, 1, src)

    def i_sthx(self, op):
        return self.i_stbx(op, size=2)

    def i_stwx(self, op):
        return self.i_stbx(op, size=4)

    def i_stdx(self, op):
        return self.i_stbx(op, size=8)
   
    

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

    def i_mfmsr(self, op):
        src = self.getRegister(REG_MSR) & 0xffffffff
        self.setOperValue(op, 0, src)

    def i_mtmsr(self, op):
        src = self.getOperValue(op, 0) & 0xffffffff
        self.setRegister(REG_MSR, src)

    def i_mfspr(self, op):
        spr = op.opers[1].reg
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)

        spr_read_hdlr = self.spr_read_handlers.get(spr)
        if spr_read_hdlr is not None:
            spr_read_hdlr(op)

    def i_mtspr(self, op):
        spr = op.opers[0].reg
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        
        spr_write_hdlr = self.spr_write_handlers.get(spr)
        if spr_write_hdlr is not None:
            spr_write_hdlr(op)

    def _swh_L1CSR1(self, op):
        spr = self.getOperValue(op, 0)
        # clear DCINV (invalidate cache)
        spr &= 0xffffffffd
        self.setOperValue(op, 0, spr)

    i_li = i_movfrom
    i_mr = i_movfrom

    def i_lis(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, (src<<16))
        # technically this is incorrect, but since we disassemble wrong, we emulate wrong.
        #self.setOperValue(op, 0, (src))

    def i_rlwimi(self, op):
        n = self.getOperValue(op, 2) & 0x1f
        b = self.getOperValue(op, 3) + 32
        e = self.getOperValue(op, 4) + 32
        ra = self.getOperValue(op, 0)

        r = ROTL32(self.getOperValue(op, 1), n)
        k = MASK(b, e)

        result = (r & k) | (ra & ~k)

        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        
    def i_rlwnm(self, op):
        n = self.getOperValue(op, 2) & 0x1f
        b = self.getOperValue(op, 3) + 32
        e = self.getOperValue(op, 4) + 32
        ra = self.getOperValue(op, 0)

        r = ROTL32(self.getOperValue(op, 1), n)
        k = MASK(b, e)

        result = r & k
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    i_rlwinm = i_rlwnm

    def i_rlwinm_old(self, op):
        rs = self.getOperValue(op, 1)
        sh = self.getOperValue(op, 2)
        mb = self.getOperValue(op, 3)
        me = self.getOperValue(op, 4)

        r = (rs << sh) | (rs >> (32-sh))
        numbits = me - mb
        k = e_bits.bu_masks[numbits] << mb

        result = r & k
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_srawi(self, op, size=4):
        rs = self.getOperValue(op, 1)
        n = self.getOperValue(op, 2) & 0x1f
        k = MASK(n+32, 63)
        r = ROTL32(rs, 64-n)
        s = (0, e_bits.u_maxes[4])[bool(rs & 0x80000000)]

        result = (r & k) | (s & ~k)

        self.setOperValue(op, 0, result)

        carry = bool(s and ((r & ~k)))
        self.setRegister(REG_CA, carry)
        
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_sraw(self, op, size=4):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)

        n = rb & 0x1f
        r = ROTL32(rs, 64-n)
        if bool(rb & 0x20):
            k = 0
        else:
            k = MASK(n+32, 63)
        s = (0, e_bits.u_maxes[4])[bool(rs & 0x80000000)]

        result = (r & k) | (s & ~k)

        carry = bool(s and ((r & ~k)))
        self.setRegister(REG_CA, carry)
        
        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperValue(op, 0, result)


    def i_srw(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)

        n = rb & 0x1f
        r = ROTL32(rs, 64-n)
        if bool(rb & 0x20):
            k = 0
        else:
            k = MASK(n+32, 63)

        result = r & k

        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperValue(op, 0, result)
        print "srw: rb: %x  rs: %x  result: %x" % (rb, rs, result)

    def i_slw(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)

        n = rb & 0x1f
        r = ROTL32(rs, n)
        if bool(rb & 0x20):
            k = 0
        else:
            k = MASK(n+32, 63)

        result = r & k

        if op.iflags & IF_RC: self.setFlags(result, 0)
        self.setOperValue(op, 0, result)
        print "slw: rb: %x  rs: %x  result: %x" % (rb, rs, result)

    def i_lha(self, op):
        src = e_bits.signed(self.getOperValue(op, 1), 2)
        self.setOperValue(op, 0, src & 0xffffffffffffffff)
        

    def i_twi(self, op):
        TO = self.getOperValue(op, 0)
        rA = self.getOperValue(op, 1)
        asize = op.opers[1].tsize
        SIMM = self.getOperValue(op, 2)

        if TO & 1 and e_bits.signed(rA, asize) < e_bits.signed(SIMM, 2):
            #TRAP
            self.trap(op)
        if TO & 2 and e_bits.signed(rA, asize) > e_bits.signed(SIMM, 2):
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
        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getRegister(REG_SO)
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegister(REG_SO, so)
            self.setRegister(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperValue(op, 0, prod & e_bits.u_maxes[size])


    def i_mullw(self, op, size=4, oe=False):
        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getRegister(REG_SO)
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegister(REG_SO, so)
            self.setRegister(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperValue(op, 0, prod)

    def i_mullwo(self, op):
        return self.i_mullw(oe=True)

    def i_mulli(self, op):
        dsize = op.opers[0].tsize
        s1size = op.opers[1].tsize
        src1 = e_bits.signed(self.getOperValue(op, 1), s1size)
        src2 = e_bits.signed(self.getOperValue(op, 2), 2)

        result = (src1 * src2) & e_bits.u_maxes[dsize]

        self.setOperValue(op, 0, result)

    def i_divw(self, op, oe=False):
        dividend = e_bits.signed(self.getOperValue(op, 1), 4)
        divisor = e_bits.signed(self.getOperValue(op, 2), 4)
        
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

        so = self.getRegister(REG_SO)
        if oe:
            so |= ov
            self.setRegister(REG_OV, ov)
            self.setRegister(REG_SO, so)

        if op.iflags & IF_RC: 
            if self.psize == 8:
                self.setRegister(REG_CR0, so)
            else:
                self.setFlags(result, so)

        self.setOperValue(op, 0, quotient)

    def i_divwu(self, op, oe=False):
        dividend = self.getOperValue(op, 1)
        divisor = self.getOperValue(op, 2)
        
        if divisor == 0:
            quotient = 0xffffffff
            ov = 1

        else:
            quotient = dividend / divisor

            ov = 0

        so = self.getRegister(REG_SO)
        if oe:
            so |= ov
            self.setRegister(REG_OV, ov)
            self.setRegister(REG_SO, so)

        if op.iflags & IF_RC: 
            if self.psize == 8:
                self.setRegister(REG_CR0, so)
            else:
                self.setFlags(result, so)

        self.setOperValue(op, 0, quotient)

    def i_divwuo(self, op):
        return self.i_divwu(op, oe=True)

    def i_mfcr(self, op):
        cr = self.getRegister(REG_CR)
        self.setOperValue(op, 0, cr & 0xffffffff)


    def _base_sub(self, op, oeflags=False, setcarry=False, addone=1, size=4):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        ra = self.getOperValue(op, 1)
        rb = self.getOperValue(op, 2)

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + rb + addone
        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)
        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])
        
        if oeflags: self.setOEflags(result, size, ra, rb+1)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        if setcarry:
            carry = bool(result & (e_bits.u_maxes[dsize] + 1))
            self.setRegister(REG_CA, carry)

    def i_subf(self, op):
        result = self._base_sub(op)

    def i_subfo(self, op):
        result = self._base_sub(op, oeflags=True)

    def i_subfb(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        bsize = op.opers[2].tsize

        ra = e_bits.sign_extend(self.getOperValue(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, size)

        rb = e_bits.sign_extend(self.getOperValue(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]
        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])
        
        if op.iflags & IF_RC: self.setFlags(result, 0)

    def i_subfbss(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        bsize = op.opers[2].tsize

        ra = e_bits.sign_extend(self.getOperValue(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, 1)

        rb = e_bits.sign_extend(self.getOperValue(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]

        # flag magic
        so = self.getRegister(REG_SO)
        sum55 = (result>>(size*8))&1
        sum56 = (result>>(size*8-1))&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov
        
        self.setRegister(REG_OV, ov)
        self.setRegister(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, 0, SO=so)

        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfbu(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize

        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]     # EXTZ... zero-extended
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, 1)

        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size] 

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size] 
        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

        if op.iflags & IF_RC: self.setFlags(result, 0)  # FIXME: bit-size correctness

    def i_subfbus(self, op, size=1):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize

        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]    # EXTZ... zero-extended
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, 1)

        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size] 

        # flag magic
        so = self.getRegister(REG_SO)
        sum55 = (result>>8)&1
        sum56 = (result>>7)&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov
        
        self.setRegister(REG_OV, ov)
        self.setRegister(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, 0, SO=so)

        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfc(self, op, oeflags=False):
        self._base_sub(op, oeflags=False, setcarry=True)

    def i_subfco(self, op):
        self._base_sub(op, oeflags=True, setcarry=True)

    def i_subfe(self, op):
        addone = self.getRegister(REG_CA)
        self._base_sub(op, oeflags=False, setcarry=True, addone=addone)

    def i_subfeo(self, op):
        addone = self.getRegister(REG_CA)
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
        ra = self.getOperValue(op, 1)
        simm = e_bits.signed(self.getOperValue(op, 2), immsize)

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + simm + 1
        ures = result & e_bits.u_maxes[dsize]
        
        carry = bool(result & (e_bits.u_maxes[dsize] + 1))
        self.setRegister(REG_CA, carry)

    def _subme(self, op, size=4, addone=1, oeflags=False):
        dsize = op.opers[0].tsize
        asize = op.opers[1].tsize
        ra = self.getOperValue(op, 1)
        rb = 0xffffffffffffffff

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + rb + addone
        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)
        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])
        
        if oeflags: self.setOEflags(result, size, ra, rb+1)
        if op.iflags & IF_RC: self.setFlags(result, 0)

        carry = bool(result & (e_bits.u_maxes[dsize] + 1))
        self.setRegister(REG_CA, carry)

    def i_subfme(self, op, size=4, addone=1):
        ca = self.getRegister(REG_CA)
        self._subme(op, size, ca)

    def i_subfmeo(self, op, size=4, addone=1):
        ca = self.getRegister(REG_CA)
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
        ra = self.getOperValue(op, 1)
        result = ~ra + 1

        if oe:
            if self.psize == 4 and ra & 0xffffffff == 0x80000000:
                ov = 1
                so = ov
                self.setRegister(REG_OV, ov)
                self.setRegister(REG_SO, so)

            elif self.psize == 8 and ra == 0x8000000000000000:
                ov = 1
                so = ov
                self.setRegister(REG_OV, ov)
                self.setRegister(REG_SO, so)
            else:
                ov = 0
                so = self.getRegister(REG_SO)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperValue(op, 0, result)

    def i_nego(self, op):
        return self.i_neg(op, oe=True)

    def i_wrteei(self, op):
        print "Write MSR External Enable"

    i_wrtee = i_wrteei

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

class Ppc64ServerEmulator(Ppc64RegisterContext, Ppc64ServerModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=Ppc64ServerModule(), psize=psize)
        Ppc64RegisterContext.__init__(self)
        Ppc64ServerModule.__init__(self)

class Ppc32ServerEmulator(Ppc32RegisterContext, Ppc32ServerModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, psize=4):
        PpcAbstractEmulator.__init__(self, archmod=Ppc32ServerModule(), psize=psize)
        Ppc32RegisterContext.__init__(self)
        Ppc32ServerModule.__init__(self)

class PpcVleEmulator(Ppc64RegisterContext, PpcVleModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=PpcVleModule(), psize=psize)
        Ppc64RegisterContext.__init__(self)
        PpcVleModule.__init__(self)

class Ppc64EmbeddedEmulator(Ppc64RegisterContext, Ppc64EmbeddedModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=Ppc64EmbeddedModule(), psize=psize)
        Ppc64RegisterContext.__init__(self)
        Ppc64EmbeddedModule.__init__(self)

class Ppc32EmbeddedEmulator(Ppc32RegisterContext, Ppc32EmbeddedModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=Ppc32EmbeddedModule(), psize=psize)
        Ppc32RegisterContext.__init__(self)
        Ppc32EmbeddedModule.__init__(self)

'''
In [2]: mnems = {}

In [3]: for lva, lsz, ltype, ltinfo in vw.getLocations(vivisect.LOC_OP):
   ...:     op = vw.parseOpcode(lva)
   ...:     mnems[op.mnem] = mnems.get(op.mnem, 0) + 1
   ...:     

In [5]: dist = [(y, x) for x,y in mnems.items()]

In [7]: dist.sort()

In [8]: dist
Out[8]: 
[(1, 'add.'),
 (1, 'addic'),
 (1, 'addme'),
 (1, 'and.'),
 (1, 'andis.'),
 (1, 'blrl'),
 (1, 'divw'),
 (1, 'isync'),
 (1, 'lhzu'),
 (1, 'sync'),
 (2, 'addic.'),
 (2, 'lha'),
 (2, 'mtmsr'),
 (2, 'rlwnm'),
 (2, 'stwux'),
 (3, 'bctr'),
 (3, 'extsh.'),
 (3, 'not'),
 (3, 'sraw'),
 (3, 'subfc'),
 (3, 'subfe'),
 (4, 'extsh'),
 (4, 'iseleq'),
 (4, 'sthu'),
 (4, 'subf.'),
 (5, 'bflr'),
 (5, 'lbzu'),
 (5, 'mulhwu'),

    (5, 'sc'),
 (5, 'srawi.'),
 (6, 'andc'),
 (7, 'addc'),
 (7, 'adde'),
 (7, 'stbx'),
 (8, 'btlr'),
 (8, 'neg'),
 (9, 'andi.'),
 (9, 'mfmsr'),
 (9, 'subfic'),
 (10, 'nop'),
 (11, 'lwzu'),

 (11, 'srw'),
 (13, 'lbzx'),
 (13, 'slw'),
 (15, 'mullw'),

 (16, 'bctrl'),

 (17, 'divwu'),
 (17, 'or.'),
 (18, 'stbu'),
 (21, 'oris'),
 (21, 'rlwimi'),

 (26, 'srawi'),
 (32, 'addis'),
 (48, 'sthx'),
 (50, 'lmw'),

 (50, 'stwx'),
 (50, 'subf'),
 (51, 'stmw'),

 (55, 'and'),
 (55, 'cmpli'),
 (62, 'lhzx'),
 (100, 'lwzx'),
 (125, 'mulli'),
 (136, 'or'),
 (141, 'stwu'),
 (154, 'rlwinm.'),
 (157, 'mfspr'),
 (162, 'mtspr'),
 (172, 'blr'),
 (190, 'cmp'),
 (192, 'lbz'),
 (204, 'cmpl'),
 (231, 'stb'),
 (276, 'add'),
 (341, 'mr'),
 (380, 'b'),
 (387, 'bl'),
 (448, 'ori'),
 (627, 'bf'),
 (639, 'cmpi'),
 (641, 'bt'),
 (649, 'lhz'),
 (656, 'sth'),
 (889, 'lis'),
 (960, 'rlwinm'),
 (1033, 'addi'),
 (1188, 'li'),
 (1204, 'lwz'),
 (1389, 'stw')]

'''
