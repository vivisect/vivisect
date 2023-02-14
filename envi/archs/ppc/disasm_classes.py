import envi
import envi.bits as e_bits
import envi.symstore.resolver as e_resolv

from envi import IF_NOFALL, IF_BRANCH, IF_CALL, IF_RET, IF_PRIV, IF_COND

import struct

from .regs import *
from .const import *
from .bits import BITMASK, COMPLEMENT


def addrToName(mcanv, va):
    sym = mcanv.syms.getSymByAddr(va)
    if sym is not None:
        return repr(sym)
    return "0x%.8x" % va


def addIntToCanv(mcanv, op, idx, value):
    hint = mcanv.syms.getSymHint(op.va, idx)
    if hint is not None:
        if mcanv.mem.isValidPointer(value):
            mcanv.addVaText(hint, value)
        else:
            mcanv.addNameText(hint)
    elif mcanv.mem.isValidPointer(value):
        name = addrToName(mcanv, value)
        mcanv.addVaText(name, value)
    else:
        mcanv.addNameText(hex(value))


def addTgtAddrToCanv(mcanv, op, idx, value):
    """
    Utility function to add an address that is executable to the canvas.
    Because this is known to be an executable address the pointer check is not
    performed.
    """
    hint = mcanv.syms.getSymHint(op.va, idx)
    if hint is not None:
        mcanv.addNameText(hint)
    else:
        name = addrToName(mcanv, value)
        mcanv.addVaText(name, value)


# Branch target helpers
IF_BRANCHCC = (IF_BRANCH | IF_COND)
IF_CALLCC = (IF_CALL | IF_COND)

BCTR_INSTR = (
    INS_BCCTR, INS_BCCTRL,
    INS_BCTR, INS_BCTRL,
    INS_BEQCTR, INS_BEQCTRL,
    INS_BGECTR, INS_BGECTRL,
    INS_BGTCTR, INS_BGTCTRL,
    INS_BGTCTR, INS_BGTCTRL,
    INS_BLECTR, INS_BLECTRL,
    INS_BLTCTR, INS_BLTCTRL,
    INS_BNECTR, INS_BNECTRL,
    INS_BNSCTR, INS_BNSCTRL,
    INS_BSOCTR, INS_BSOCTRL,
)

BLR_INSTR = (
    INS_BCLR,     INS_BCLRL,
    INS_BDNZEQLR, INS_BDNZEQLRL,
    INS_BDNZGELR, INS_BDNZGELRL,
    INS_BDNZGTLR, INS_BDNZGTLRL,
    INS_BDNZLELR, INS_BDNZLELRL,
    INS_BDNZLR,   INS_BDNZLRL,
    INS_BDNZLTLR, INS_BDNZLTLRL,
    INS_BDNZNELR, INS_BDNZNELRL,
    INS_BDNZNSLR, INS_BDNZNSLRL,
    INS_BDNZSOLR, INS_BDNZSOLRL,
    INS_BDZEQLR,  INS_BDZEQLRL,
    INS_BDZGELR,  INS_BDZGELRL,
    INS_BDZGTLR,  INS_BDZGTLRL,
    INS_BDZLELR,  INS_BDZLELRL,
    INS_BDZLR,    INS_BDZLRL,
    INS_BDZLTLR,  INS_BDZLTLRL,
    INS_BDZNELR,  INS_BDZNELRL,
    INS_BDZNSLR,  INS_BDZNSLRL,
    INS_BDZSOLR,  INS_BDZSOLRL,
    INS_BEQLR,    INS_BEQLRL,
    INS_BGELR,    INS_BGELRL,
    INS_BGTLR,    INS_BGTLRL,
    INS_BLELR,    INS_BLELRL,
    INS_BLR,      INS_BLRL,
    INS_BLTLR,    INS_BLTLRL,
    INS_BNELR,    INS_BNELRL,
    INS_BNSLR,    INS_BNSLRL,
    INS_BSOLR,    INS_BSOLRL,
)


class PpcOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, size, operands, iflags=0):
        super(PpcOpcode, self).__init__(va, opcode, mnem, 0, size, operands, iflags)

    def getBranches(self, emu=None):
        ret = []

        # To start with we have no flags.
        flags = 0
        addb = False

        # If we are a conditional branch, even our fallthrough
        # case is conditional...
        if (self.iflags & IF_BRANCHCC) == IF_BRANCHCC:
            flags |= envi.BR_COND
            addb = True
        elif self.iflags & IF_BRANCH:
            addb = True

        # If we can fall through, reflect that...
        if not self.iflags & envi.IF_NOFALL and not self.iflags & envi.IF_CALL:
           ret.append((self.va + self.size, flags|envi.BR_FALL))

        # Check for a call...
        if (self.iflags & IF_CALLCC) == IF_CALLCC:
            flags |= (envi.BR_PROC | envi.BR_COND)
            addb = True
        elif self.iflags & IF_CALL:
            flags |= envi.BR_PROC
            addb = True

        if addb:
            # In PowerPC the CTR and LR registers can be used as branch targets,
            # for those instructions we need an emulator to retrieve the correct
            # branch target.
            if self.opcode in BCTR_INSTR:
                if emu is None:
                    tova = None
                else:
                    tova = emu.getRegister(REG_CTR)
            elif self.opcode in BLR_INSTR:
                if emu is None:
                    tova = None
                else:
                    tova = emu.getRegister(REG_LR)
            else:
                # For all other branches the last operand is the branch target
                # The operand already handles relative vs immediate offsets and
                # that doesn't need to be checked here.
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
        for i in range(imax):
            oper = self.opers[i]
            oper.render(mcanv, self, i)
            if i != lasti:
                mcanv.addText(",")


class PpcRegOper(envi.RegisterOper):
    '''
    Register operand for full access to all registers (as opposed to PpcERegOper
    which only accesses the low 32 bits of the first 32 GPRs (r0-r31).

    Base class for all register operands
    '''

    def __init__(self, reg, va=0, oflags=0):
        self.va = va
        self.reg = reg
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def involvesPC(self):
        return False

    def isDeref(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None

    def getOperValue(self, op, emu=None):
        if emu == None:
            return None

        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None

        emu.setRegister(self.reg, val)

    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText(rname, typename='registers')

    def repr(self, op):
        return ppc_regs[self.reg][0]

    def getWidth(self, emu):
        return emu.getRegisterWidth(self.reg) >> 3

# SPR register types
class PpcDCRegOper(PpcRegOper):
    def __init__(self, reg, va=0, oflags=0):
        PpcRegOper.__init__(self, reg + REG_OFFSET_DCR, va=va, oflags=oflags)


class PpcPMRegOper(PpcRegOper):
    def __init__(self, reg, va=0, oflags=0):
        PpcRegOper.__init__(self, reg + REG_OFFSET_PMR, va=va, oflags=oflags)


# XER (1), LR (8), and CTR (9) are in lower case to keep GDB happy, if the SPR 
# number is one of those then capitalize the name for. All SPRs that have a 
# number 10 or above should not have their name modified.
SPR_UPPER_NAME = {
    1 + REG_OFFSET_SPR: 'XER',
    8 + REG_OFFSET_SPR: 'LR',
    9 + REG_OFFSET_SPR: 'CTR',
}


class PpcSPRegOper(PpcRegOper):
    def __init__(self, reg, va=0, oflags=0):
        PpcRegOper.__init__(self, reg + REG_OFFSET_SPR, va=va, oflags=oflags)
        self._sprname = None

    def repr(self, op):
        if self._sprname is None:
            # Check if the SPR number indicates that the name needs to be 
            # capitalized or left alone.
            rname = ppc_regs[self.reg][0]
            self._sprname = SPR_UPPER_NAME.get(self.reg, rname)

        return self._sprname


class PpcTMRegOper(PpcRegOper):
    def __init__(self, reg, va=0, oflags=0):
        PpcRegOper.__init__(self, reg + REG_OFFSET_TMR, va=va, oflags=oflags)


class PpcTBRegOper(PpcRegOper):
    def __init__(self, reg, va=0, oflags=0):
        PpcRegOper.__init__(self, reg + REG_OFFSET_TBR, va=va, oflags=oflags)


class PpcERegOper(PpcRegOper):
    '''
    Book E and VLE (particularly the e200z7 core) has a really weird access
    mechanism for 32-bit cores, where regular PPC BookE and VLE instructions
    access only the lower 32-bits of the otherwise 64-bit GPRs.  This class
    takes that into account, so it should be assigned to all BookE and VLE
    instructions, whereas the raw PpcRegOper should be used by SPE (CAT_SP).
    '''
    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va  # FIXME: is this modified?  or do we need to att # to this?

        if emu == None:
            return None

        regval = emu.getRegister(self.reg)

        if self.reg < 32:
            size = emu.psize
            regval &= e_bits.u_maxes[size]

        return regval


    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return None

        if self.reg < 32:
            mask = e_bits.u_maxes[emu.psize]
            val &= mask

        emu.setRegister(self.reg, val)

    def getWidth(self, emu):
        if self.reg < 32 and emu.psize == 4:
            return 4

        return emu.getRegisterWidth(self.reg) >> 3


class PpcFRegOper(PpcRegOper):
    ''' Floating Point register operand.'''
    def __init__(self, reg, va=0):
        reg += REG_OFFSET_FLOAT
        super(PpcFRegOper, self).__init__(reg, va)

vector_fmt_chars_int = { 1: 'B', 2: 'H', 4: 'I', 8: 'Q' }
vector_fmt_chars_flt = { 4: 'f', 8: 'd' }


class PpcVRegOper(PpcRegOper):
    ''' Vector register operand.'''
    def __init__(self, reg, va=0, elemsize=1, signed=False, floating=False):
        reg += REG_OFFSET_VECTOR
        self.elemsize = elemsize
        self.elemcount = 16 // elemsize
        self.signed = signed
        self.floating = floating

        if elemsize != 16 and not floating:
            fmt_char = vector_fmt_chars_int[elemsize]
            if signed:  # the equivalent signed format characters are lowercase
                fmt_char = fmt_char.lower()
            self.fmt = f">{self.elemcount}{fmt_char}"
        elif floating:
            fmt_char = vector_fmt_chars_flt[elemsize]
            self.fmt = f">{self.elemcount}{fmt_char}"
        else:
            self.fmt = None

        super(PpcVRegOper, self).__init__(reg, va)

    def getValues(self, op, emu=None):
        if emu is None:
            return None

        if self.fmt is None:
            return [self.getOperValue(op, emu)]

        reg = emu.getRegister(self.reg)
        reg_bytes = struct.pack('>2Q', reg >> 64, reg & 0xffffffffffffffff)
        return struct.unpack(self.fmt, reg_bytes)

    def setValues(self, op, emu=None, vals=None):
        if emu is None:
            return None

        if self.fmt is None:
            return self.setOperValue(op, emu, *vals)

        # Ensure our values will fit before we try and pack them
        if self.signed:
            vals = [e_bits.signed(x, self.elemsize) for x in vals]

        val_bytes = struct.pack(self.fmt, *vals)
        val_left, val_right = struct.unpack('>2Q', val_bytes)
        val = (val_left << 64) | (val_right & 0xffffffffffffffff)
        emu.setRegister(self.reg, val)

class PpcSPEVRegOper(PpcRegOper):
    ''' SPE Vector register operand. '''
    def __init__(self, reg, va=0, elemsize=1, signed=False, floating=False):
        # reg += REG_OFFSET_VECTOR
        self.elemsize = elemsize
        self.elemcount = 8 // elemsize
        self.signed = signed
        self.floating = floating

        if elemsize != 8 and not floating:
            fmt_char = vector_fmt_chars_int[elemsize]
            if signed:  # the equivalent signed format characters are lowercase
                fmt_char = fmt_char.lower()
            self.fmt = f">{self.elemcount}{fmt_char}"
        elif floating:
            fmt_char = vector_fmt_chars_flt[elemsize]
            self.fmt = f">{self.elemcount}{fmt_char}"
        else:
            self.fmt = None

        super(PpcSPEVRegOper, self).__init__(reg, va)

    def getValues(self, op, emu=None):
        if emu is None:
            return None

        if self.fmt is None:
            return [self.getOperValue(op, emu)]

        reg = emu.getRegister(self.reg)
        reg_bytes = struct.pack('>Q', reg)
        return struct.unpack(self.fmt, reg_bytes)

    def setValues(self, op, emu=None, vals=None):
        if emu is None:
            return None

        if self.fmt is None:
            return self.setOperValue(op, emu, *vals)

        # Ensure our values will fit before we try and pack them
        if self.signed:
            vals = [e_bits.signed(x, self.elemsize) for x in vals]

        val_bytes = struct.pack(self.fmt, *vals)
        val = struct.unpack('>Q', val_bytes)[0]
        emu.setRegister(self.reg, val)


class PpcCRegOper(PpcRegOper):
    ''' CR register operand field.'''
    def __init__(self, field, va=0):
        reg = REG_CR
        super(PpcCRegOper, self).__init__(reg, va)
        self.field = field

    def getWidth(self, emu):
        '''
        We cheat a little here, since the actual width is 4 bits...
        '''
        return 1

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.oflags != oper.oflags:
            return False
        if self.reg != oper.reg:
            return False
        if self.field != oper.field:
            return False
        return True

    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText(rname, name='CR', typename='cregisters')

    def repr(self, op):
        return 'cr' + str(self.field)

    def getOperValue(self, op, emu=None):
        if emu == None:
            return

        return emu.getCr(self.field)

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return

        emu.setCr(val & 0xf, self.field)


CRBITS = ('lt', 'gt', 'eq', 'so')


class PpcCBRegOper(PpcRegOper):
    ''' CR register bit operand.'''
    def __init__(self, bit, va=0):
        reg = REG_CR
        super(PpcCBRegOper, self).__init__(reg, va)
        self.bit = bit
        self.bitidx = 31 - bit  # stupid NXP numbering

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self.reg != other.reg:
            return False
        if self.bit != other.bit:
            return False
        return True

    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText(rname, name='CR', typename='cregisters')

    def repr(self, op, simple=True):
        creg = self.bit // 4
        coff = self.bit % 4
        if creg or not simple:
            return "cr%d.%s" % (creg, CRBITS[coff])
        else:
            return "%s" % (CRBITS[coff])

    def getOperValue(self, op, emu=None):
        if emu == None:
            return

        cr = emu.getRegister(self.reg)
        crb = (cr >> self.bitidx) & 1
        return crb

    def setOperValue(self, op, emu=None, val=None):
        if emu == None:
            return

        bitmask = BITMASK(self.bit, psize=4)
        inverted_mask = COMPLEMENT(bitmask, size=4)

        # Grab the CR, AND with mask to clear the bit in question,
        # then OR to set it to val
        cr = emu.getRegister(self.reg)
        cr &= inverted_mask
        crb = ((val & 1) << self.bitidx) & bitmask
        cr |= crb

        emu.setRegister(REG_CR, cr)


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

    def setOperValue(self, op, emu=None, val=None):
        return None

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        addIntToCanv(mcanv, op, idx, value)

    def repr(self, op):
        return hex(self.getOperValue(op))

    def getWidth(self, emu):
        return emu.psize

class PpcSImmOper(PpcImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0, bits=5):
        val = e_bits.bsigned(val, bits)
        super(PpcSImmOper, self).__init__(val, va)

class PpcSImm5Oper(PpcSImmOper):
    ''' Signed Immediate operand bit 5. '''
    def __init__(self, val, va=0):
        super(PpcSImm5Oper, self).__init__(val, va, 5)

class PpcSImm12Oper(PpcSImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0):
        super(PpcSImm12Oper, self).__init__(val, va, 12)

class PpcSImm16Oper(PpcSImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0):
        super(PpcSImm16Oper, self).__init__(val, va, 16)

class PpcSImm20Oper(PpcSImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0):
        super(PpcSImm20Oper, self).__init__(val, va, 20)

class PpcSImm3Oper(PpcSImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0):
        val = e_bits.signed(val * 4, 2)
        super(PpcSImm3Oper, self).__init__(val, va)

class PpcSImm32Oper(PpcSImmOper):
    ''' Signed Immediate operand. '''
    def __init__(self, val, va=0):
        super(PpcSImm32Oper, self).__init__(val, va, 32)

class PpcUImmOper(PpcImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        super(PpcUImmOper, self).__init__(val, va)

class PpcUImm1Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        val *= 8
        super(PpcUImm1Oper, self).__init__(val, va)

class PpcUImm2Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        val *= 2
        super(PpcUImm2Oper, self).__init__(val, va)

class PpcUImm3Oper(PpcUImmOper):
    ''' Unsigned Immediate operand. '''
    def __init__(self, val, va=0):
        val *= 4
        super(PpcUImm3Oper, self).__init__(val, va)


class PpcMemOper(envi.DerefOper):
    '''
    immediate offset memory operand.
    0xOFFSET(base_reg)
    '''
    def __init__(self, base_reg, offset, va, tsize=4):
        self.base_reg = base_reg
        self.offset = e_bits.signed(offset, 2)
        self.tsize = tsize
        self.va = va

    def __eq__(self, oper):
        return isinstance(oper, self.__class__) \
            and self.base_reg == oper.base_reg \
            and self.offset == oper.offset

    def _get_offset(self, emu=None):
        return self.offset

    def _get_base_reg(self, emu=None):
        # if rA == 0, constant 0 is used instead of r0
        return 0 if self.base_reg == 0 else emu.getRegister(self.base_reg)

    def involvesPC(self):
        return False

    def isDeref(self):
        return True

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()][self.tsize]
        val &= e_bits.u_maxes[self.tsize]
        emu.writeMemoryFormat(addr, fmt, val)

    def getOperValue(self, op, emu=None):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()][self.tsize]
        ret, = emu.readMemoryFormat(addr, fmt)
        return ret

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None

        return (self._get_base_reg(emu) + self._get_offset(emu)) & e_bits.u_maxes[emu.psize]

    def updateReg(self, op, emu, addr=None):
        if self.base_reg == 0:
            raise envi.InvalidInstruction(mesg='Cannot update base register when rA == 0')

        if addr is None:
            addr = self.getOperAddr(op, emu)

        emu.setRegister(self.base_reg, addr)

    def updateRegObj(self, emu):
        if self.base_reg == 0:
            raise envi.InvalidInstruction(mesg='Cannot update base register when rA == 0')

        import vivisect.symboliks.common as vs_common
        rval = emu.getRegObj(self.base_reg) + vs_common.Const(self._get_offset(emu), emu.psize)
        emu.setRegObj(self.base_reg, rval)

    def render(self, mcanv, op, idx):
        # First add the offset
        offset = self._get_offset()
        addIntToCanv(mcanv, op, idx, offset)

        # Now add the base register (if it is not r0)
        if self.base_reg != 0:
            mcanv.addText('(')
            mcanv.addNameText(ppc_regs[self.base_reg][0], typename='registers')
            mcanv.addText(')')

    def repr(self, op):
        off_str = hex(self._get_offset())
        if self.base_reg == 0:
            return off_str
        else:
            base_reg = ppc_regs[self.base_reg][0]
            return off_str + '(' + base_reg + ')'

    def getWidth(self, emu):
        return self.tsize


class PpcSEMemOper(PpcMemOper):
    '''
    Just like a normal PpcMemOper but the base register is allowed to be r0
    '''
    def _get_base_reg(self, emu=None):
        return emu.getRegister(self.base_reg)

    def updateReg(self, op, emu, addr=None):
        if addr is None:
            addr = self.getOperAddr(op, emu)

        emu.setRegister(self.base_reg, addr)

    def updateRegObj(self, emu):
        import vivisect.symboliks.common as vs_common
        rval = emu.getRegObj(self.base_reg) + vs_common.Const(self._get_offset(emu), emu.psize)
        emu.setRegObj(self.base_reg, rval)

    def render(self, mcanv, op, idx):
        '''
        On the SE load/store instructions, a base address value of 0 does not
        represent a constant 0
        '''
        # First add the offset
        offset = self._get_offset()
        addIntToCanv(mcanv, op, idx, offset)

        # Now add the base register (allowed to be r0)
        mcanv.addText('(')
        mcanv.addNameText(ppc_regs[self.base_reg][0], typename='registers')
        mcanv.addText(')')

    def repr(self, op):
        '''
        On the SE load/store instructions, a base address value of 0 does not
        represent a constant 0
        '''
        return hex(self._get_offset()) + '(' + ppc_regs[self.base_reg][0] + ')'


class PpcIndexedMemOper(PpcMemOper):
    '''
    register offset memory operand.
    offset_reg(base_reg)
    '''
    def __init__(self, base_reg, offset_reg, va, tsize=4):
        self.base_reg = base_reg
        self.offset = offset_reg  # keeping offset as name so eq stays the same
        self.tsize = tsize
        self.va = va

    def _get_offset(self, emu=None):
        if emu is None:
            return None

        return emu.getRegister(self.offset)

    def updateRegObj(self, emu):
        if self.base_reg == 0:
            raise envi.InvalidInstruction(mesg='Cannot update base register when rA == 0')

        rval = emu.getRegObj(self.base_reg) + emu.getRegObj(self.offset)
        emu.setRegObj(self.base_reg, rval)

    def render(self, mcanv, op, idx):
        if self.base_reg == 0:
            mcanv.addNameText('0')
        else:
            mcanv.addNameText(ppc_regs[self.base_reg][0], typename='registers')

        mcanv.addText(',')
        mcanv.addNameText(ppc_regs[self.offset][0], typename='registers')

    def repr(self, op):
        offset_reg = ppc_regs[self.offset][0]

        if self.base_reg == 0:
            return '0x0,' + offset_reg
        else:
            base_reg = ppc_regs[self.base_reg][0]
            return base_reg + ',' + offset_reg


class PpcJmpRelOper(PpcImmOper):
    """
    PC/va relative target address for branches
    """
    def __init__(self, val, va):
        self.va = va
        self.val = val

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.getOperValue(None) != oper.getOperValue(None):
            return False
        return True

    def involvesPC(self):
        return True

    def getOperValue(self, op, emu=None):
        return self.va + self.val

    def render(self, mcanv, op, idx):
        value = self.getOperValue(op)
        addTgtAddrToCanv(mcanv, op, idx, value)


class PpcJmpAbsOper(PpcJmpRelOper):
    """
    absolute target address for branches
    """
    def __init__(self, val):
        self.val = val

    def __eq__(self, oper):
        # Explicitly check if the items being compared are PpcJmpRelOper
        # objects, we want (I think?) relative and absolute jump addresses that
        # have the same value to be considered equal.  Using PpcJmpRelOper in
        # this comparison will evaluate to true for the both relative and
        # absolute jump operand objects.
        if not isinstance(oper, PpcJmpRelOper):
            return False
        if self.getOperValue(None) != oper.getOperValue(None):
            return False
        return True

    def involvesPC(self):
        return False

    def getOperValue(self, op, emu=None):
        return self.val


fields = (None, 'c', 'x', 'cx', 's', 'cs', 'xs', 'cxs',  'f', 'fc', 'fx', 'fcx', 'fs', 'fcs', 'fxs', 'fcxs')


OPERCLASSES = {
    FIELD_BD : PpcSImm3Oper,
    FIELD_BH : PpcImmOper,
    FIELD_BI : PpcCBRegOper,
    FIELD_BO : PpcImmOper,
    FIELD_CRM : PpcImmOper,
    FIELD_CT : PpcImmOper,
    FIELD_D : PpcSImm16Oper,
    FIELD_DCRN0_4 : PpcImmOper,
    FIELD_DCRN5_9 : PpcImmOper,
    FIELD_DCTL : PpcImmOper,
    FIELD_DE : PpcSImm12Oper,
    FIELD_DS : PpcSImm3Oper,
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
    FIELD_SIMM : PpcSImmOper,
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
    FIELD_crBI : PpcCRegOper,
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
    FIELD_rA : PpcERegOper,
    FIELD_sA : PpcSPEVRegOper,
    FIELD_rB : PpcERegOper,
    FIELD_sB : PpcSPEVRegOper,
    FIELD_rC : PpcERegOper,
    FIELD_sC : PpcSPEVRegOper,
    FIELD_rD : PpcERegOper,
    FIELD_sD : PpcSPEVRegOper,
    FIELD_rS : PpcERegOper,
    FIELD_sS : PpcSPEVRegOper,
    FIELD_sh0 : PpcImmOper,
    FIELD_sh1_5 : PpcImmOper,
    FIELD_vA : PpcVRegOper,
    FIELD_vB : PpcVRegOper,
    FIELD_vC : PpcVRegOper,
    FIELD_vD : PpcVRegOper,
    FIELD_vS : PpcVRegOper,
}
