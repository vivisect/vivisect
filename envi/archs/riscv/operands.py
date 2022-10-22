import envi
import envi.bits as e_bits
from envi.archs.riscv.regs import riscv_regs, REG_PC, REG_SP
from envi.archs.riscv.const import RISCV_OF, CSR_REGISTER_METAS, CSR_REGISTER_NAMES


__all__ = [
    'RiscVOpcode',
    'RiscVRegOper',
    'RiscVCRegOper',
    'RiscVCSRRegOper',
    'RiscVMemOper',
    'RiscVMemSPOper',
    'RiscVImmOper',
    'RiscVRMOper',
]


IF_CALLCC = (envi.IF_CALL | envi.IF_COND)


def _operand_shift(value, shift):
    try:
        return value >> shift
    except ValueError:
        return value << abs(shift)


def _operand_value(value, bits, oflags):
    if oflags & RISCV_OF.UNSIGNED:
            return value
    elif oflags & RISCV_OF.SIGNED:
            if value & e_bits.bsign_bits[bits]:
                return -((~value + 1) & e_bits.b_masks[bits])
            else:
                return value
    else:
        raise envi.InvalidInstruction(mesg='Invalid instruction flags: 0x%x' % oflags)


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

        elif (self.iflags & envi.IF_CALLCC) == envi.IF_CALLCC:
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
        self.va = va
        self.reg = _operand_shift(ival & args.mask, args.shift)
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
        return self.reg == REG_PC

    def getWidth(self, emu):
        return emu.getRegisterWidth(self.reg) // 8

    def getOperValue(self, op, emu=None):
        if self.reg == REG_PC:
            return self.va

        if emu is None:
            return None
        return emu.getRegister(self.reg)

    def setOperValue(self, op, emu=None, val=None):
        if emu is None:
            return
        emu.setRegister(self.reg, val)

    def getOperAddr(self, op, emu=None):
        return None

    #returns content intended to be printed to screen
    def repr(self, op):
        return riscv_regs.getRegisterName(self.reg)

    #displays the values on the vivisect canvas gui
    def render(self, mcanv, op, idx):
        rname = self.repr(op)
        mcanv.addNameText(rname, typename='registers')


class RiscVCRegOper(RiscVRegOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, oflags)
        # To convert the compressed register values to real registers add 8
        self.reg += 8


class RiscVCSRRegOper(RiscVRegOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        super().__init__(ival, bits, args, va, oflags)
        # The register number in the instruction is a CSR meta regsiter
        self.csr_reg = self.reg
        # Get the real Meta register value
        self.reg = CSR_REGISTER_METAS.get(self.csr_reg)

    def repr(self, op):
        return CSR_REGISTER_NAMES.get(self.csr_reg, 'invalid')


class RiscVMemOper(envi.DerefOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        # The args for MemOper is a tuple of: base register args and a list of
        # imm args
        base_reg_args, imm_args = args
        self.base_reg = _operand_shift(ival & base_reg_args.mask, base_reg_args.shift)

        value = sum(_operand_shift(ival & a.mask, a.shift) for a in imm_args)
        self.offset = _operand_value(value, bits, oflags)

        self.va = va
        self.oflags = oflags
        self._set_tsize()

    def _set_tsize(self):
        # TODO: we can probably speed this up
        if self.oflags & RISCV_OF.BYTE:
            self.tsize = 1
        elif self.oflags & RISCV_OF.HALFWORD:
            self.tsize = 2
        elif self.oflags & RISCV_OF.WORD:
            self.tsize = 4
        elif self.oflags & RISCV_OF.DOUBLEWORD:
            self.tsize = 8
        elif self.oflags & RISCV_OF.QUADWORD:
            self.tsize = 16
        else:
            raise envi.InvalidInstruction(mesg='Invalid instruction flags for memory access: 0x%x' % self.oflags)

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
        self.offset = _operand_value(value, bits, oflags)

        self.va = va
        self.oflags = oflags
        self._set_tsize()


class RiscVImmOper(envi.ImmedOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        # RiscV immediate values can be split up in many weird ways, so the args
        # are a list of RiscVFieldArgs values
        value = sum(_operand_shift(ival & a.mask, a.shift) for a in args)
        self.val = _operand_value(value, bits, oflags)
        self.va = va
        self.oflags = oflags

    def __eq__(self, oper):
        if not isinstance(oper, self.__class__):
            return False
        if self.val != oper.val:
            return False
        if self.oflags != oper.oflags:
            return False
        return True

    def getOperValue(self, op, emu=None):
        return self.val

    #Rework to calculate #of BYTES, not bits
    def getWidth(self, emu):
        return emu.getPointerSize()

    #returns content intended to be printed to screen
    def repr(self, op):
        return hex(self.val)

    #displays the values on the canvas
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

    #no def involvesPC needed correct?
    def involvesPC(self):
        return False

    def getOperAddr(self):
        return None

    def setOperValue(self):
        pass


class RiscVRMOper(RiscVImmOper):
    def __init__(self, ival, bits, args, va=0, oflags=0):
        self.va = va
        self.val = _operand_shift(ival & args.mask, args.shift)
        self.oflags = oflags

    def repr(self, op):
        return RM_NAMES.get(self.val, 'inv')
