import envi
import envi.bits as e_bits
from envi.archs.riscv.regs import riscv_regs, REG_SP, REG_ZERO
from envi.archs.riscv.regs_gen import csr_regs
from envi.archs.riscv.const import RISCV_OF, FLOAT_CONSTS, SIZE_FLAGS, SIZE_CONSTS


__all__ = [
    'RiscVOpcode',
    'RiscVRegOper',
    'RiscVFRegOper',
    'RiscVCSRRegOper',
    'RiscVMemOper',
    'RiscVMemSPOper',
    'RiscVJmpOper',
    'RiscVImmOper',
    'RiscVRelJmpOper',
    'RiscVRMOper',
    'RiscVOrderOper',
]


IF_CALLCC = (envi.IF_CALL | envi.IF_COND)


def _operand_shift(value, shift):
    try:
        return value >> shift
    except ValueError:
        return value << abs(shift)


def int_to_float(value, oflags):
    flags = oflags & SIZE_FLAGS
    info = FLOAT_CONSTS[flags]

    if value in info.inf:
        result = float('inf')
    elif value in info.snan or value in info.qnan:
        result = float('nan')
    else:
        exp = (value & info.emask) >> info.fbits
        frac = value & info.fmask
        result = (2**(exp-info.eoff)) * (1+(frac/info.fdiv))

    if value & info.sign:
        return -result
    else:
        return result


def _float_to_int_slow(value, info):
    # This will probably be horribly inefficient but is necessary for formats
    # not supported by the struct package
    int_part = int(value)

    # Drop the leading one from the integer component
    if int_part != 0:
        int_bits = format(value, 2)[1:]
        exp = len(int_bits)
    else:
        exp = None

    dec_part = value - int_part
    dec_bits = ''

    i = 0
    while dec_part:
        if exp is not None and i >= info.fbits - exp:
            break
        dec_part *= 2
        if dec_part >= 1:
            dec_bits += '1'
            dec_part -= 1.0
            if exp is None:
                exp = -i
        else:
            dec_bits += '0'
        i += 1

    if int_part == 0:
        # Remove any leading 0's
        bits = dec_bits[-exp:]

    # Pad the integer and decimal part out to the specified fractional bit width
    bits += '0' * (rem_bits - len(bits))

    if value < 0.0:
        return info.sign | ((info.eoff + exp) << info.fbits) | int(bits, 2)
    else:
        return ((info.eoff + exp) << info.fbits) | int(bits, 2)


def float_to_int(value, oflags):
    flags = oflags & SIZE_FLAGS
    info = FLOAT_CONSTS[flags]

    if value == 0.0:
        return 0
    elif value == float('inf'):
        return inf[0]
    elif value == -float('inf'):
        return inf[1]
    elif value == float('nan'):
        # Use the quiet NaN values
        return qnan[0]
    elif value == -float('nan'):
        # Use the quiet NaN values
        return qnan[1]

    # half, single, and double precision can be handled using the info returned
    # by the python float.hex() function
    if flags == RISCV_OF.QUADWORD:
        return _float_to_int_slow(value, info)

    # Drop the leading 0x1 and split the returned value on the 'p'
    frac_str, exp_str = abs(value).hex()[3:].split('p')
    frac = int(frac_str, 16)

    if flags == RISCV_OF.DOUBLEWORD:
        # The values returned by the hex() function can be used directly, just
        # shift the exponent value
        exp = int(exp_str, 10) << info.fbits
    else:
        # The bits must be truncated
        exp_value = int(exp_str, 10) - FLOAT_CONSTS[RISCV_OF.DOUBLEWORD].eoff
        exp = (exp_value + info.eoff) << info.fbits
        bits = format(int(frac_str, 16), 'b')[:info.fbits]
        frac = format(bits, 2)

    if value < 0.0:
        return info.sign | exp | frac
    else:
        return exp | frac


class RiscVOpcode(envi.Opcode):
    def __init__(self, va, opcode, mnem, size, opers, iflags=0):
        super().__init__(va, opcode, mnem, 0, size, opers, iflags)

    def getBranches(self, emu=None):
        ret = []

        flags = 0
        addb = False

        if self.iflags & (envi.IF_COND):
            flags |= envi.BR_COND
            addb = True

        if not self.iflags & (envi.IF_NOFALL | envi.IF_RET | envi.IF_BRANCH) or self.iflags & envi.IF_COND:
            ret.append((self.va + self.size, flags|envi.BR_FALL))

        if len(self.opers) == 0:
            if self.iflags & envi.IF_CALL:
                ret.append(None, flags | envi.BR_PROC)
            return ret

        if self.iflags & envi.IF_CALL:
            flags |= envi.BR_PROC
            addb = True

        elif (self.iflags & IF_CALLCC) == IF_CALLCC:
            flags |= (envi.BR_PROC | envi.BR_COND)
            addb = True

        elif self.iflags & envi.IF_BRANCH:
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

    def __repr__(self):
        """
        Over-riding the standard envi.Opcode.__repr__ to speed it up
        """
        return self.mnem + " " + ",".join(o.repr(self) for o in self.opers)

    def render(self):
        if self.prefixes:
            pfx = self._getPrefixName(self.prefixes)
            if pfx:
                mcanv.addNameText("%s: " % pfx, pfx)

        mnem = self.mnem
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


class RiscVRegOper(envi.RegisterOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        value = _operand_shift(ival & args.mask, args.shift)

        # Double check if there are any restrictions on this value
        if (oflags & RISCV_OF.NOT_ZERO and value == 0) or \
                (oflags & RISCV_OF.NOT_TWO and value == 2):
            raise envi.InvalidOperand(value)
        elif (oflags & RISCV_OF.HINT_ZERO and value == 0):
            self.hint = True
        else:
            self.hint = False

        self.va = va
        self.reg = value

        if oflags & RISCV_OF.CREG:
            self.reg += 8

        self.oflags = oflags
        self._set_tsize()

    def _set_tsize(self):
        # Because some instructions read less than the register size bytes from
        # the register
        self.tsize = SIZE_CONSTS.get(self.oflags & SIZE_FLAGS)

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.reg != oper.reg:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def involvesPC(self):
        # There is no directly referee cable PC register in RISC-V
        return False

    def getWidth(self, emu):
        return emu.getRegisterWidth(self.reg) // 8

    def getRaw(self, op, emu=None):
        if self.reg == REG_ZERO:
            return 0
        elif emu is None:
            return None

        value = emu.getRegister(self.reg)
        if self.tsize is not None:
            return e_bits.unsigned(value, self.tsize)
        else:
            return value

    def setRaw(self, op, emu=None, value=None):
        # Register X0 can't be written to
        if self.reg == REG_ZERO or emu is None:
            return
        if self.tsize is not None:
            value = e_bits.unsigned(value, self.tsize)
        emu.setRegister(self.reg, value)

    def getOperValue(self, op, emu=None):
        value = self.getRaw(op, emu)
        if value is None:
            return None

        if self.oflags & RISCV_OF.SIGNED:
            # tsize _must_ be set
            return e_bits.signed(value, self.tsize)
        else:
            return value

    def setOperValue(self, op, emu=None, value=None):
        if self.oflags & RISCV_OF.SIGNED:
            # tsize _must_ be set
            value = e_bits.signed(value, self.tsize)
        emu.setRaw(op, emu, value)

    def getOperAddr(self, op, emu=None):
        return None

    #returns content intended to be printed to screen
    def repr(self, op):
        return riscv_regs.getRegisterName(self.reg)

    #displays the values on the vivisect canvas gui
    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText(rname, typename='registers')


class RiscVFRegOper(RiscVRegOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, oflags)
        # Offset the value by the first floating point register
        self.reg += REG_F0

    def isZero(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) == 0

    def isNormal(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return bool(self.getRaw(self, op, emu) & FLOAT_CONSTS[flags].emask)

    def isSubnormal(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return not bool(self.getRaw(self, op, emu) & FLOAT_CONSTS[flags].emask)

    def isNeg(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return bool(self.getRaw(self, op, emu) & FLOAT_CONSTS[flags].sign)

    def isPos(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return not bool(self.getRaw(self, op, emu) & FLOAT_CONSTS[flags].sign)

    def isInf(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) in FLOAT_CONSTS[flags].inf

    def isSNaN(sele, op, emu):
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) in FLOAT_CONSTS[flags].snan

    def isQNaN(self, op, emu):
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) in FLOAT_CONSTS[flags].qnan

    def getSign(self, op, emu):
        """
        return only the sign bit
        """
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) & FLOAT_CONSTS[flags].sign

    def getNegSign(self, op, emu):
        """
        return the negated sign bit
        """
        flags = oflags & SIZE_FLAGS
        neg_sign = self.getRaw(self, op, emu) ^ FLOAT_CONSTS[flags].sign
        return neg_sign & FLOAT_CONSTS[flags].sign

    def getAbs(self, op, emu):
        """
        return the number without the sign bit
        """
        flags = oflags & SIZE_FLAGS
        return self.getRaw(self, op, emu) & ~FLOAT_CONSTS[flags].sign

    def getOperValue(self, op, emu=None):
        """
        Utility function to get the floating point representation of the value
        in this operand's register.
        """
        return int_to_float(self.getRaw(self, op, emu), self.oflags)

    def setOperValue(self, op, emu=None, val=None):
        """
        Utility function to set the value of this operand's register from a
        floating point value.
        """
        self.setRaw(self, op, emu, int_to_float(val, self.oflags))


class RiscVCSRRegOper(RiscVRegOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, va, oflags)

        # The register number in the instruction is a CSR meta regsiter
        self.csr_reg = self.reg

        # Get the internal envi register constant
        name = csr_regs.get(self.csr_reg)

        # This may be invalid
        self.reg = riscv_regs.getRegisterIndex(name)

    def addSystemRegister(self, emu):
        """
        Because the CSR registers are scraped from the documentation it's
        possible that disassembly may reference new or non-standard CSR numbers
        This function supports adding a non-standard CSR register to an
        emulator instance.
        """
        emu.addRegister(hex(self.csr_reg))

    def repr(self, op):
        return csr_regs.get(self.csr_reg, hex(self.csr_reg))


class RiscVMemOper(envi.DerefOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        # The args for MemOper is a tuple of: base register args and a list of
        # imm args
        base_reg_args, imm_args = args
        self.base_reg = _operand_shift(ival & base_reg_args.mask, base_reg_args.shift)

        value = sum(_operand_shift(ival & a.mask, a.shift) for a in imm_args)
        if oflags & RISCV_OF.UNSIGNED:
            self.offset = e_bits.bsigned(value, bits)
        else:
            self.offset = value

        self.va = va
        self.oflags = oflags

        self._set_tsize()

        # memory operands can't indicate hints
        self.hint = False

    def _set_tsize(self):
        self.tsize = SIZE_CONSTS.get(self.oflags & SIZE_FLAGS)

    def __eq__(self, oper):
        return isinstance(oper, self.__class__) \
            and self.base_reg == oper.base_reg \
            and self.offset == oper.offset

    def _get_offset(self, emu=None):
        return self.offset

    def _get_base_reg(self, emu=None):
        if emu is None:
            return None
        return emu.getRegister(self.base_reg)

    def involvesPC(self):
        return False

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()].get(self.tsize)
        if fmt is not None:
            val &= e_bits.u_maxes[self.tsize]
            emu.writeMemoryFormat(addr, fmt, val)
        elif self.tsize == 16:
            lower_val = val & e_bits.u_maxes[8]
            upper_val = (val >> 64) & e_bits.u_maxes[8]
            if emu.getEndian() == envi.ENDIAN_LSB:
                emu.writeMemoryFormat(addr, fmt, lower_val)
                emu.writeMemoryFormat(addr, fmt+8, upper_val)
            else:
                emu.writeMemoryFormat(addr, fmt+8, lower_val)
                emu.writeMemoryFormat(addr, fmt, upper_val)

    def getOperValue(self, op, emu=None):
        if emu is None:
            return None

        addr = self.getOperAddr(op, emu)

        fmt = e_bits.fmt_chars[emu.getEndian()].get(self.tsize)
        if fmt is not None:
            ret, = emu.readMemoryFormat(addr, fmt)
        elif self.tsize == 16:
            lower_val = val & e_bits.u_maxes[8]
            upper_val = (val >> 64) & e_bits.u_maxes[8]
            if emu.getEndian() == envi.ENDIAN_LSB:
                lower_val, = emu.readMemoryFormat(addr, fmt)
                upper_val, = emu.readMemoryFormat(addr, fmt+8)
            else:
                lower_val, = emu.readMemoryFormat(addr, fmt+8)
                upper_val, = emu.readMemoryFormat(addr, fmt)
            ret = upper_val << 64 | lower_val
        return ret

    def getOperAddr(self, op, emu=None):
        if emu is None:
            return None

        return (self._get_base_reg(emu) + self._get_offset(emu)) & e_bits.u_maxes[emu.psize]

    def updateReg(self, op, emu, addr=None):
        if addr is None:
            addr = self.getOperAddr(op, emu)
        emu.setRegister(self.base_reg, addr)

    def updateRegObj(self, emu):
        import vivisect.symboliks.common as vs_common
        rval = emu.getRegObj(self.base_reg) + vs_common.Const(self._get_offset(emu), emu.psize)
        emu.setRegObj(self.base_reg, rval)

    def render(self, mcanv, op, idx):
        mcanv.addNameText(hex(self._get_offset()))
        mcanv.addText('(')
        if self.base_reg == 0:
            mcanv.addNameText('0x0')
        else:
            base = riscv_regs.getRegisterName(self.base_reg)
            mcanv.addNameText(base, typename='registers')
        mcanv.addText(')')

    def repr(self, op):
        base = riscv_regs.getRegisterName(self.base_reg)
        return f'{hex(self._get_offset())}({base})'

    def getWidth(self, emu):
        return self.tsize


class RiscVMemSPOper(RiscVMemOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        # The SP memory operands always use the X2 (SP) register as the base reg
        self.base_reg = REG_SP

        value = sum(_operand_shift(ival & a.mask, a.shift) for a in args)
        if oflags & RISCV_OF.UNSIGNED:
            self.offset = e_bits.bsigned(value, bits)
        else:
            self.offset = value

        self.va = va
        self.oflags = oflags
        self._set_tsize()


class RiscVJmpOper(RiscVMemOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, va, oflags)

    def setRaw(self, op, emu=None, value=None):
        # The address can't be changed during runtime
        pass

    def setOperValue(self, op, emu=None, val=None):
        # The address can't be changed during runtime
        pass

    def getRaw(self, op, emu=None):
        # Return the calculated memory address
        return self.getOperAddr(op, emu)

    def getOperValue(self, op, emu=None):
        # Return the calculated memory address
        return self.getOperAddr(op, emu)


class RiscVImmOper(envi.ImmedOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        # RiscV immediate values can be split up in many weird ways, so the args
        # are a list of RiscVFieldArgs values
        value = sum(_operand_shift(ival & a.mask, a.shift) for a in args)

        # Double check if there are any restrictions on this value
        if (oflags & RISCV_OF.NOT_ZERO and value == 0) or \
                (oflags & RISCV_OF.NOT_TWO and value == 2):
            raise envi.InvalidOperand(value)

        if oflags & RISCV_OF.UNSIGNED:
            self.value = e_bits.bsigned(value, bits)
        else:
            self.value = value
        self.va = va
        self.oflags = oflags

        # immediate operands can't indicate hints
        self.hint = False

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.value != oper.value:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def getRaw(self, op, emu=None):
        return self.value

    def setRaw(self, op, emu=None, value=None):
        # Can't modify immediate operands
        pass

    def getOperValue(self, op, emu=None):
        return self.value

    def setOperValue(self, op, emu=None, value=None):
        # Can't modify immediate operands
        pass

    #Rework to calculate #of BYTES, not bits
    def getWidth(self, emu):
        return emu.getPointerSize()

    #returns content intended to be printed to screen
    def repr(self, op):
        return hex(self.value)

    #displays the values on the canvas
    def render(self, mcanv, op, idx):
        value = self.value
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

            if abs(self.value) >= 4096:
                mcanv.addNameText(hex(value))
            else:
                mcanv.addNameText(str(value))

    #no def involvesPC needed correct?
    def involvesPC(self):
        return False

    def getOperAddr(self, op, emu=None):
        return None


class RiscVRelJmpOper(RiscVImmOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, va, oflags)

        # Update the value to be PC relative
        self.value += va

    def involvesPC(self):
        return True


class RiscVRMOper(RiscVImmOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        self.va = va
        self.value = _operand_shift(ival & args.mask, args.shift)
        self.oflags = oflags

        # immediate operands can't indicate hints
        self.hint = False

    def repr(self, op):
        return RM_NAMES.get(self.value, 'inv')


class RiscVOrderOper(RiscVRMOper):
    def repr(self, op):
        return ORDER_NAMES.get(self.value, 'inv')
