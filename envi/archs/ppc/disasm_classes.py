import envi
import envi.bits as e_bits
import envi.symstore.resolver as e_resolv

from envi import IF_NOFALL, IF_BRANCH, IF_CALL, IF_RET, IF_PRIV, IF_COND

from regs import *
from const import *

def addrToName(mcanv, va):
    sym = getSymByAddr(mcanv.syms, va)
    if sym != None:
        return repr(sym)
    return "0x%.4x" % va

def getSymByAddr(self, addr, exact=True):
    '''
    local version for only 4-digit repr locations
    '''
    name = self.getName(addr)
    if name == None:
        if addr > 0xffff and self.isValidPointer(addr):
            name = "loc_%.4x" % addr

    if name != None:
        #FIXME fname
        #FIXME functions/segments/etc...
        return e_resolv.Symbol(name, addr, 0)


IF_CALLCC = (IF_CALL | IF_COND)

class PpcOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, size, operands, iflags=0):
        envi.Opcode.__init__(self, va, opcode, mnem, 0, size, operands, iflags)

    def getBranches(self, emu=None):
        ret = []

        # To start with we have no flags.
        flags = 0
        addb = False

        # If we are a conditional branch, even our fallthrough
        # case is conditional...
        #if self.iflags & (IF_BRANCH | IF_COND):
        if self.iflags & (IF_COND):
            flags |= envi.BR_COND
            addb = True

        # If we can fall through, reflect that...
        if not self.iflags & (envi.IF_NOFALL | envi.IF_RET | envi.IF_BRANCH) or self.iflags & envi.IF_COND:
            ret.append((self.va + self.size, flags|envi.BR_FALL))

        # In most architectures, if we have no operands, it has no
        # further branches...
        if len(self.opers) == 0:
            if self.iflags & envi.IF_CALL:
                ret.append((None, flags | envi.BR_PROC))
            return ret

        # Check for a call...
        if self.iflags & IF_CALL:
            flags |= envi.BR_PROC
            addb = True

        # A conditional call?  really?  what compiler did you use? ;)
        elif (self.iflags & IF_CALLCC) == IF_CALLCC:
            flags |= (envi.BR_PROC | envi.BR_COND)
            addb = True

        elif self.iflags & IF_BRANCH:
            addb = True

        if addb:
            oper = self.opers[-1]
            if oper.isDeref():
                flags |= envi.BR_DEREF
                tova = oper.getOperAddr(self, emu=emu)
            else:
                tova = oper.getOperValue(self, emu=emu)

            ret.append((tova, flags))

        return ret

    def render(self, mcanv):
        """
        Render this opcode to the specified memory canvas
        """
        if self.prefixes:
            pfx = self._getPrefixName(self.prefixes)
            if pfx:
                mcanv.addNameText("%s: " % pfx, pfx)

        mnem = self.mnem
        if self.iflags & IF_BRANCH_LIKELY:
            mnem += '+'
        elif self.iflags & IF_BRANCH_UNLIKELY:
            mnem += '-'
        mcanv.addNameText(mnem, self.mnem, typename="mnemonic")
        mcanv.addText(" ")

        # Allow each of our operands to render
        imax = len(self.opers)
        lasti = imax - 1
        for i in xrange(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")


class PpcRegOper(envi.RegisterOper):
    ''' register operand.'''

    def __init__(self, reg, va=0):
        self.va = va
        self.reg = reg
        

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        return True
    
    def involvesPC(self):
        return self.reg == 15

    def isDeref(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va  # FIXME: is this modified?  or do we need to att # to this?

        if emu == None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None
        emu.setRegister(self.reg, val)

    def render(self, mcanv, op, idx):
        rname = ppc_regs[self.reg][0]
        mcanv.addNameText(rname, typename='registers')


    def repr(self, op):
        rname = ppc_regs[self.reg][0]
        return rname

class PpcFRegOper(PpcRegOper):
    ''' Floating Point register operand.'''
    def __init__(self, reg, va=0):
        self.va = va
        self.reg = reg + REG_IDX_FP
        
class PpcVRegOper(PpcRegOper):
    ''' Vector register operand.'''
    def __init__(self, reg, va=0):
        self.va = va
        self.reg = reg      + REG_IDX_VECTOR
        
class PpcCRegOper(PpcRegOper):
    ''' CR register operand field.'''
    def __init__(self, field, va=0):
        self.va = va
        self.reg = REG_CR
        self.field = field
        
    def render(self, mcanv, op, idx):
        #rname = ppc_regs[self.reg][0]
        rname = "cr%d" % self.field
        mcanv.addNameText(rname, typename='cregisters')

    def repr(self, op):
        #rname = ppc_regs[self.reg][0]
        rname = "cr%d" % self.field
        return rname

    def getOperValue(self, op, emu=None):
        if emu == None:
            return

        cr = emu.getRegister(REG_CR)
        crb = (cr >> (self.field*4)) & 0xf
        return crb


CRBITS = ('lt', 'gt', 'eq', 'so')
class PpcCBRegOper(PpcRegOper):
    ''' CR register operand.'''
    def __init__(self, bit, va=0):
        self.va = va
        self.reg = REG_CR
        self.bit = bit
        
    def render(self, mcanv, op, idx):
        #rname = ppc_regs[self.reg][0]
        creg = self.bit / 4
        coff = self.bit % 4
        name = "cr%d" % (creg)
        rname = "cr%d.%s" % (creg, CRBITS[coff])
        mcanv.addNameText(rname, name=name, typename='cregisters')

    def repr(self, op):
        #rname = ppc_regs[self.reg][0]
        creg = self.bit / 4
        coff = self.bit % 4
        rname = "cr%d.%s" % (creg, CRBITS[coff])
        return rname

    def getOperValue(self, op, emu=None):
        if emu == None:
            return

        cr = emu.getRegister(self.reg)
        crb = (cr >> self.bit) & 1

        return crb

class PpcImmOper(envi.ImmedOper):
    ''' Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = val

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False

        if self.getOperValue(None) != oper.getOperValue(None):
            return False

        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def isDiscrete(self):
        return True

    def getOperAddr(self, op, emu=None):
        return None

    def getOperValue(self, op, emu=None):
        return self.val

    def render(self, mcanv, op, idx):
        value = self.val
        hint = mcanv.syms.getSymHint(op.va, idx)
        if hint != None:
            if mcanv.mem.isValidPointer(value):
                mcanv.addVaText(hint, value)
            else:
                mcanv.addNameText(hint)
        elif mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:

            if abs(self.val) >= 4096:
                mcanv.addNameText(hex(value))
            else:
                mcanv.addNameText(str(value))

    def repr(self, op):
        val = self.getOperValue(op)
        return '0x%x' % (val)

class PpcSImmOper(PpcImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0, bits=5):
        if val & (1<<(bits-1)):
            val |= (e_bits.b_masks[32-bits] << bits)

        self.val = e_bits.signed(val, 4)

class PpcSImm5Oper(PpcSImmOper):
    ''' Signed Immediate operand bit 5. '''
    def __init__(self, val, va=0):
        PpcSImmOper.__init__(self, val, va, 5)

class PpcSImm16Oper(PpcSImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        PpcSImmOper.__init__(self, val, va, 16)

class PpcUImmOper(PpcImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = val

class PpcUImm1Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = val * 8

class PpcUImm2Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = val * 2

class PpcUImm3Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = val * 4

class PpcSImm3Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        self.val = e_bits.signed(val * 4, 2)


class PpcMemOper(envi.DerefOper):
    ''' immediate offset memory operand.

    0xOFFSET (base_reg)

    '''
    def __init__(self, base_reg, offset, va, tsize=4):
        self.base_reg = base_reg
        self.offset = e_bits.signed(offset, 2)
        self.tsize = tsize
        self.va = va

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.base_reg != oper.base_reg:
            return False
        if self.offset != oper.offset:
            return False
        return True

    def involvesPC(self):
        return self.base_reg == REG_PC

    def isDeref(self):
        return True

    def setOperValue(self, op, emu=None, val=None):
        # can't survive without an emulator
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()][self.tsize]
        emu.writeMemoryFormat(addr, fmt, val)

    def getOperValue(self, op, emu=None):
        # can't survive without an emulator
        if emu == None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()][self.tsize]
        ret, = emu.readMemoryFormat(addr, fmt)
        return ret

    def getOperAddr(self, op, emu=None):
        # there are certain circumstances where we can survive without an emulator
        # if we don't have an emulator, we must be PC-based since we know it
        if self.base_reg == REG_PC:
            addr = self.va
        elif emu == None:
            return None
        else:
            addr = emu.getRegister(self.base_reg)

        addr += self.offset

        return addr

    def updateReg(self, emu):
        rval = emu.getRegister(self.base_reg)
        #print self.offset
        rval += self.offset
        emu.setRegister(self.base_reg, rval)


    def render(self, mcanv, op, idx):
        basereg = ppc_regs[self.base_reg][0]
        if self.base_reg == REG_PC:

            addr = self.getOperAddr(op, mcanv.mem)    # only works without an emulator because we've already verified base_reg is PC

            mcanv.addText('(')
            if mcanv.mem.isValidPointer(addr):
                name = addrToName(mcanv, addr)
                mcanv.addVaText(name, addr)
            else:
                mcanv.addVaText('#0x%.8x' % addr, addr)

            mcanv.addText(')')

            value = self.getOperValue(op, mcanv.mem)
            if value != None:
                mcanv.addText("\t; ")
                if mcanv.mem.isValidPointer(value):
                    name = addrToName(mcanv, value)
                    mcanv.addVaText(name, value)
                else:
                    mcanv.addNameText("0x%x" % value)

        else:
            mcanv.addNameText(hex(self.offset))

            mcanv.addText('(')
            mcanv.addNameText(basereg, typename='registers')
            mcanv.addText(')')

    def repr(self, op):
        basereg = ppc_regs[self.base_reg][0]
        if self.base_reg == REG_PC:
            addr = self.getOperAddr(op)    # only works without an emulator because we've already verified base_reg is PC

            tname = "(%s)" % hex(addr)
        else:
            tname = '%s(%s)' % (hex(self.offset), basereg)
        return tname

class PpcJmpOper(envi.RegisterOper):
    """
    PC + imm_offset

    PpcImmOper but for Branches, not a dereference. 
    """
    def __init__(self, val, va):
        self.va = va
        self.val = e_bits.signed(val, 4)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.va != oper.va:
            return False
        return True

    def involvesPC(self):
        return True

    def isDeref(self):
        return False

    def isDiscrete(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.va + self.val

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        if mcanv.mem.isValidPointer(value):
            name = addrToName(mcanv, value)
            mcanv.addVaText(name, value)
        else:
            mcanv.addVaText('0x%.8x' % value, value)

    def repr(self, op):
        targ = self.getOperValue(op)
        tname = "0x%.8x" % targ
        return tname

fields = (None, 'c', 'x', 'cx', 's', 'cs', 'xs', 'cxs',  'f', 'fc', 'fx', 'fcx', 'fs', 'fcs', 'fxs', 'fcxs')

class PpcCrOper(envi.RegisterOper):
    def __init__(self, val, va, mask=0xffffffff):
        self.mask = mask
        self.val = val

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        psr = emu.getRegister(REG_CR)
        return psr

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None

        psr = emu.getRegister(REG_CR)
        newpsr = psr & (~self.mask) | (val & self.mask)
        emu.setRegister(REG_CR)

        return newpsr

    def repr(self, op):
        #return "cr_" + fields[self.val]
        return "cr%u" % self.val

    def render(self, mcanv, op, idx):
        name = "cr%u" % self.val
        mcanv.addNameText(name, typename='cr')


OPERCLASSES = {
    FIELD_BD : PpcSImm3Oper,
    FIELD_BH : PpcImmOper,
    FIELD_BI : PpcCBRegOper,
    FIELD_BO : PpcImmOper,
    FIELD_CRM : PpcImmOper,
    FIELD_CT : PpcImmOper,
    FIELD_D : PpcImmOper,
    FIELD_DCRN0_4 : PpcImmOper,
    FIELD_DCRN5_9 : PpcImmOper,
    FIELD_DCTL : PpcImmOper,
    FIELD_DS : PpcImmOper,
    FIELD_DUI : PpcImmOper,
    FIELD_E : PpcImmOper,
    FIELD_FM : PpcImmOper,
    FIELD_IMM : PpcImmOper,
    FIELD_IU : PpcImmOper,
    FIELD_L : PpcImmOper,
    FIELD_LEV : PpcImmOper,
    FIELD_LI : PpcImmOper,
    FIELD_MB : PpcImmOper,
    FIELD_ME : PpcImmOper,
    FIELD_MO : PpcImmOper,
    FIELD_OC : PpcImmOper,
    FIELD_OU : PpcImmOper,
    FIELD_PMRN0_4 : PpcImmOper,
    FIELD_PMRN5_9 : PpcImmOper,
    FIELD_SA : PpcImmOper,
    FIELD_SH : PpcImmOper,
    FIELD_SIMM : PpcImmOper,
    FIELD_SIMM16 : PpcSImm16Oper,
    FIELD_SIMM5 : PpcSImm5Oper,
    FIELD_SPRN0_4 : PpcImmOper,
    FIELD_SPRN5_9 : PpcImmOper,
    FIELD_SS : PpcImmOper,
    FIELD_STRM : PpcImmOper,
    FIELD_T : PpcImmOper,
    FIELD_TBRN0_4 : PpcImmOper,
    FIELD_TBRN5_9 : PpcImmOper,
    FIELD_TH : PpcImmOper,
    FIELD_TMRN0_4 : PpcImmOper,
    FIELD_TMRN5_9 : PpcImmOper,
    FIELD_TO : PpcImmOper,
    FIELD_UIMM : PpcImmOper,
    FIELD_UIMM1 : PpcUImm1Oper,
    FIELD_UIMM2 : PpcUImm2Oper,
    FIELD_UIMM3 : PpcUImm3Oper,
    FIELD_W : PpcImmOper,
    FIELD_WC : PpcImmOper,
    FIELD_WH : PpcImmOper,
    FIELD_crD : PpcCRegOper,
    FIELD_crb : PpcCBRegOper,
    FIELD_crbA : PpcCBRegOper,
    FIELD_crbB : PpcCBRegOper,
    FIELD_crbC : PpcCBRegOper,
    FIELD_crbD : PpcCBRegOper,
    FIELD_crfD : PpcCRegOper,
    FIELD_crfS : PpcCRegOper,
    FIELD_frA : PpcFRegOper,
    FIELD_frB : PpcFRegOper,
    FIELD_frC : PpcFRegOper,
    FIELD_frD : PpcFRegOper,
    FIELD_frS : PpcFRegOper,
    FIELD_mb0 : PpcImmOper,
    FIELD_mb1_5 : PpcImmOper,
    FIELD_me0 : PpcImmOper,
    FIELD_me1_5 : PpcImmOper,
    FIELD_rA : PpcRegOper,
    FIELD_rB : PpcRegOper,
    FIELD_rC : PpcRegOper,
    FIELD_rD : PpcRegOper,
    FIELD_rS : PpcRegOper,
    FIELD_sh0 : PpcImmOper,
    FIELD_sh1_5 : PpcImmOper,
    FIELD_vA : PpcVRegOper,
    FIELD_vB : PpcVRegOper,
    FIELD_vC : PpcVRegOper,
    FIELD_vD : PpcVRegOper,
    FIELD_vS : PpcVRegOper,
}
