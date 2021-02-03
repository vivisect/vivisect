"""
The H8 Emulator module.
"""

import struct
import logging

import envi
import envi.bits as e_bits
import envi.const as e_const
import envi.archs.h8.regs as h8_regs
import envi.archs.h8.const as h8_const

from envi.archs.h8 import H8Module
from envi.archs.h8.operands import H8RegDirOper


logger = logging.getLogger(__name__)

# bcd lookup table generation
bcd_add = {}
for x in range(0xa):
    for y in range(0xa):
        bcd_add[(0, 0, (x, y))] = 0, 0

    for y in range(4):
        bcd_add[(0, 1, (x, y))] = 0x6, 0

for x in range(9):
    for y in range(0xa, 0x10):
        bcd_add[(0, 0, (x, y))] = 0x6, 0

for x in range(0xa, 0x10):
    for y in range(0xa):
        bcd_add[(0, 0, (x, y))] = 0x60, 1

    for y in range(4):
        bcd_add[(0, 1, (x, y))] = 0x66, 1

for x in range(9, 0x10):
    for y in range(0xa, 0x10):
        bcd_add[(0, 0, (x, y))] = 0x66, 1

for x in range(3):
    for y in range(0xa):
        bcd_add[(1, 0, (x, y))] = 0x60, 1

    for y in range(0xa, 0x10):
        bcd_add[(1, 0, (x, y))] = 0x66, 1

for x in range(4):
    for y in range(4):
        bcd_add[(1, 1, (x, y))] = 0x66, 1

bcd_sub = {}
for x in range(0xa):
    for y in range(0xa):
        bcd_sub[(0, 0, (x, y))] = 0, 0

for x in range(0x9):
    for y in range(6, 0x10):
        bcd_sub[(0, 1, (x, y))] = 0xfa, 0

for x in range(7, 0x10):
    for y in range(0xa):
        bcd_sub[(1, 0, (x, y))] = 0xa0, 1

for x in range(6, 0x10):
    for y in range(6, 0x10):
        bcd_sub[(1, 1, (x, y))] = 0x9a, 1

sign_ext_bits = {
        1: [((-1 & 0xff) << (8 - x) & 0xff) for x in range(8)],
        2: [],
        4: [],
        }


# calling conventions
class H8CallAdv(envi.CallingConvention):
    """
    H8 architectures hand arguments between functions using

    reference: C_H8_User_Manual.pdf
    """
    arg_def = [(e_const.CC_REG, h8_regs.REG_ER0),
               (e_const.CC_REG, h8_regs.REG_ER1),
               (e_const.CC_REG, h8_regs.REG_ER2),
               (e_const.CC_STACK_INF, 4)]
    retaddr_def = (e_const.CC_STACK_INF, 0)
    retval_def = (e_const.CC_REG, h8_regs.REG_ER0), (e_const.CC_STACK_INF, 0)  # FIXME
    flags = e_const.CC_CALLEE_CLEANUP
    align = 2
    pad = 0

    def execCallReturn(self, emu, value, argc=None):
        sp = emu.getRegister(h8_regs.REG_SP)
        pc = struct.unpack('>H', emu.readMemory(sp, 2))[0]
        sp += 2  # For the saved pc
        sp += (2 * argc)  # Cleanup saved args

        emu.setRegister(h8_regs.REG_SP, sp)
        emu.setRegister(h8_regs.REG_R0, value)
        emu.setProgramCounter(pc)

    def getCallArgs(self, emu, count):
        # r0-r3 are used to hand in parameters.  additional ph8s are stored and pointed to by r0
        return emu.getRegister(0xf)


h8call = H8CallAdv()

CPUSTATE_RESET = 0
CPUSTATE_EXC = 1
CPUSTATE_EXEC = 2
CPUSTATE_BUS = 3
CPUSTATE_SLEEP = 4
CPUSTATE_SWSTDBY = 5
CPUSTATE_HWSTDBY = 6


class H8Emulator(H8Module, h8_regs.H8RegisterContext, envi.Emulator):
    IVT_RESET = 0

    def __init__(self, advanced=True):
        H8Module.__init__(self)
        envi.Emulator.__init__(self, self)
        h8_regs.H8RegisterContext.__init__(self)

        self.state = CPUSTATE_RESET
        self.ptrsz = 0

        # seglist = [(0,0xffffffff) for x in range(6)]

        self.setAdvanced(advanced)
        self.addCallingConvention("H8 Arch Procedure Call", h8call)

    def setAdvanced(self, advanced=True):
        self.advanced = advanced
        if advanced:
            self.ptrsz = 4
        else:
            self.ptrsz = 2

    def reset(self):
        '''
        triggers the reset interrupt
        '''
        if self.getProgramCounter() == 0:
            va = self.readMemoryPtr(self.IVT_RESET)
            self.setProgramCounter(va)

    def getPointerSize(self):
        return self.ptrsz

    def processInterrupt(self, intval=0):
        '''
        From outside the emulator, cause an interrupt to be handled.
        FIXME: wants to pause the run()/runFunction() thread, if any active
        '''
        va = self.emuProcessInterrupt_2140(intval)
        self.setProgramCounter(va)

    def emuProcessInterrupt_2140(self, intval=0):
        '''
        interrupt processing done according to H8/300 standards.  subclass and modify this function
        if the desired behavior differs.
        supports: advanced and normal modes
        '''
        if self.getFlag(CCR_I):
            # FIXME: check for NMI or RESET
            if intval != 0 and intval not in NMI_INTS:
                logger.info("Ignoring maskable interrupt (CCR_I flag is set)")
                return

        logger.info("Interrupt Handler: 0x%x", intval)

        addr = 0

        if self.advanced:
            if intval != 0:
                val = (self.getStatusRegister() << 24) | self.getStatusRegister()
                self.doPush(val, 4)

                addr = (intval * 4) + 0xc

            isrAddr = self.readMemortPtr(addr)
        else:
            if intval != 0:
                val = self.getStatusRegister()
                val |= (val << 8)
                self.doPush(val, 2)
                self.doPush(self.getProgramCounter())

                addr = (intval * 2) + 6

            isrAddr = self.readMemoryPtr(addr)

        return isrAddr

    def emuProcessInterrupt(self, intval=0):
        '''
        interrupt processing done according to H8/300 standards.  subclass and modify this function
        if the desired behavior differs.
        supports: advanced and normal modes
        '''
        logger.info("Interrupt Handler: 0x%x", intval)

        addr = 0

        if self.advanced:
            if intval != 0:
                self.doPush(self.getStatusRegister())
                self.doPush(self.getStatusRegister())
                self.doPush(self.getProgramCounter())

                addr = (intval * 4) + 0xa

            isrAddr = self.readMemortPtr(addr)
        else:
            if intval != 0:
                self.doPush(self.getStatusRegister())
                self.doPush(self.getProgramCounter())

                addr = (intval * 2) + 4

            isrAddr = self.readMemoryPtr(addr)

        return isrAddr

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(h8_const.REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(h8_const.REG_FLAGS)
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(h8_const.REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(h8_const.REG_FLAGS)
        if flags is None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new pc
        x = None
        meth = self.op_methods.get(op.mnem, None)
        if meth is None:
            raise envi.UnsupportedInstruction(self, op)
        x = meth(op)

        if x is None:
            pc = self.getProgramCounter()
            x = pc+op.size

        self.setProgramCounter(x)

    def doPush(self, val, inc=2, reg=h8_const.REG_SP):
        sp = self.getRegister(reg)
        sp -= inc
        self.writeMemValue(sp, val, inc)
        self.setRegister(reg, sp)

    def doPop(self, inc=2, reg=h8_const.REG_SP):
        sp = self.getRegister(reg)
        val = self.readMemValue(sp, inc)
        self.setRegister(reg, sp+inc)
        return val

    def i_and(self, op):
        dsize = op.opers[1].tsize
        res = self.logicalAnd(op)
        self.setOperValue(op, 1, res)

        self.setFlag(h8_regs.CCR_Z, not res)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(res, dsize))
        self.setFlag(h8_regs.CCR_V, 0)

    def i_andc(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 1, res)

    def i_band(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        val = self.getOperValue(op, 1)

        val >>= bit
        val &= C

        self.setFlag(h8_regs.CCR_C, val)

    def i_bra(self, op):
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_brn(self, op):
        pass

    def i_bhi(self, op):
        if not (self.getFlag(h8_regs.CCR_C) == 0 or self.getFlag(h8_regs.CCR_Z) == 0):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bls(self, op):
        if not (self.getFlag(h8_regs.CCR_C) or self.getFlag(h8_regs.CCR_Z)):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bhs(self, op):
        if self.getFlag(h8_regs.CCR_C):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_blo(self, op):
        if not self.getFlag(h8_regs.CCR_C):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bne(self, op):
        if self.getFlag(h8_regs.CCR_Z):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_beq(self, op):
        if not self.getFlag(h8_regs.CCR_Z):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bvc(self, op):
        if self.getFlag(h8_regs.CCR_V):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bvs(self, op):
        if not self.getFlag(h8_regs.CCR_V):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bpl(self, op):
        if self.getFlag(h8_regs.CCR_N):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bmi(self, op):
        if not self.getFlag(h8_regs.CCR_N):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bge(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if self.getFlag(h8_regs.CCR_V) != self.getFlag(h8_regs.CCR_N):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_blt(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if self.getFlag(h8_regs.CCR_V) == self.getFlag(h8_regs.CCR_N):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bgt(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if (self.getFlag(h8_regs.CCR_V) != self.getFlag(h8_regs.CCR_N)) or self.getFlag(h8_regs.CCR_Z):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_ble(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if not ((self.getFlag(h8_regs.CCR_V) != self.getFlag(h8_regs.CCR_N)) and self.getFlag(h8_regs.CCR_Z)):
            return
        nextva = self.getOperValue(op, 0)
        return nextva

    i_bt = i_bra
    i_bf = i_brn
    i_bcc = i_bhs
    i_bcs = i_blo

    def i_bclr(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1 << bit)
        self.setOperValue(op, 1, tgt)

    def i_biand(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C &= ~(tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bild(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C = ~(tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bior(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C |= ~(tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bist(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1 << bit)
        tgt |= (C ^ 1) << bit
        self.setOperValue(op, 1, tgt)

    def i_bixor(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C ^= ~(tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bld(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C = (tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bnot(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt ^= (1 << bit)
        self.setOperValue(op, 1, tgt)

    def i_bor(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C |= (tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_bset(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt |= (1 << bit)
        self.setOperValue(op, 1, tgt)

    def i_bst(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1 << bit)
        tgt |= C << bit
        self.setOperValue(op, 1, tgt)

    def i_btst(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        Z = ((tgt >> bit) & 1) ^ 1
        self.setFlag(h8_regs.CCR_Z, Z)

    def i_bxor(self, op):
        C = self.getFlag(h8_regs.CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C ^= (tgt >> bit) & 1
        self.setFlag(h8_regs.CCR_C, C)

    def i_cmp(self, op):
        flagtup = self.integerSubtraction(op)
        self.doFlags(flagtup)

    def i_bsr(self, op):
        nextva = self.getProgramCounter()

        if self.advanced:
            self.doPush(nextva, 4)
        else:
            self.doPush(nextva)

        disp = self.getOperValue(op, 0)
        pc = self.getProgramCounter() + disp
        return pc

    def i_jsr(self, op):
        nextva = self.getProgramCounter()

        if self.advanced:
            self.doPush(nextva, 4)
        else:
            self.doPush(nextva)

        ea = self.getOperValue(op, 0)
        return ea

    def i_stm(self, op):
        reglist = self.getOperValue(op, 0)

        for regval in reglist:
            op.opers[1].setOperValue(op, self, regval)

    def i_ldm(self, op):
        reglist = op.opers[1].getOperRegs(op)

        for reg in reglist:
            regval = op.opers[0].getOperValue(op, self, mod=True)
            self.setRegister(reg, regval)

    def i_mov(self, op):
        ssize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, ssize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)

        if isinstance(op.opers[1], H8RegDirOper) and op.opers[1].reg == h8_const.REG_PC:
            return val

    def i_add(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        self.setOperValue(op, 1, ures)

        # FIXME: test and validate
        self.setFlag(h8_regs.CCR_H, e_bits.is_signed_half_carry(sres, dsize, sdst))
        self.setFlag(h8_regs.CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(sres, dsize))

    def i_adds(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        self.setOperValue(op, 1, ures)

    def i_addx(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        C = self.getFlag(h8_regs.CCR_C)
        sres += C
        ures += C

        self.setOperValue(op, 1, ures)

        # FIXME: test and validate  (same as i_add)
        self.setFlag(h8_regs.CCR_H, e_bits.is_signed_half_carry(sres, dsize, sdst))
        self.setFlag(h8_regs.CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(sres, dsize))

    def i_daa(self, op):
        oper = self.getOperValue(op, 0)
        upop = oper >> 4 & 0xf
        loop = oper & 0xf
        C = self.getFlag(h8_regs.CCR_C)
        H = self.getFlag(h8_regs.CCR_H)

        addtup = bcd_add.get((C, H, upop, loop))
        if addtup is None:
            logger.debug("DAA:  %x %x %x %x - addtup is None", C, H, upop, loop)
            return  # FIXME: raise exception once figured out
        addval, resC = addtup
        ures = addval + oper

        self.setOperValue(op, 0, ures)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, 1))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_C, resC)

    def i_das(self, op):
        oper = self.getOperValue(op, 0)
        upop = oper >> 4 & 0xf
        loop = oper & 0xf
        C = self.getFlag(h8_regs.CCR_C)
        H = self.getFlag(h8_regs.CCR_H)

        addtup = bcd_sub.get((C, H, upop, loop))
        if addtup is None:
            logger.debug("DAS:  %x %x %x %x - addtup is None", C, H, upop, loop)
            # FIXME: raise exception once figured out
            return
        addval, resC = addtup
        ures = addval + oper

        self.setOperValue(op, 0, ures)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, 1))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_C, resC)       # this should always be what it was coming in

    def i_inc(self, op):
        dstidx = len(op.opers) - 1
        if dstidx == 1:
            ssize = op.opers[0].tsize
            dsize = op.opers[1].tsize
            src = self.getOperValue(op, 0)
            dst = self.getOperValue(op, 1)

            udst = e_bits.unsigned(dst, dsize)
            # TODO: What is sdst and why does it exist?
            # sdst = e_bits.signed(dst, dsize)
            usrc = e_bits.unsigned(src, ssize)
            ssrc = e_bits.signed(src, ssize)

        else:
            dsize = op.opers[0].tsize
            dst = self.getOperValue(op, 0)

            udst = e_bits.unsigned(dst, dsize)
            # sdst = e_bits.signed(dst, dsize)
            ssrc = usrc = 1

        ures = usrc + udst
        sres = ssrc + udst

        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(sres, dsize))
        # V must be set if previous value was 0x7f (per docs, page 78 of H8/300)

        self.setOperValue(op, dstidx, ures)

    def i_dec(self, op):
        dstidx = len(op.opers) - 1
        if dstidx == 1:
            ssize = op.opers[0].tsize
            dsize = op.opers[1].tsize
            src = self.getOperValue(op, 0)
            dst = self.getOperValue(op, 1)

            udst = e_bits.unsigned(dst, dsize)
            sdst = e_bits.signed(dst, dsize)
            usrc = e_bits.unsigned(src, ssize)
            ssrc = e_bits.signed(src, ssize)

        else:
            dsize = op.opers[0].tsize
            dst = self.getOperValue(op, 0)

            udst = e_bits.unsigned(dst, dsize)
            sdst = e_bits.signed(dst, dsize)
            ssrc = usrc = 1

        ures = udst - usrc
        sres = sdst - ssrc

        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(sres, dsize))
        # V must be set if previous value was 0x80 (per docs, page 73 of H8/300)

        self.setOperValue(op, dstidx, ures)

    def i_jmp(self, op):
        return self.getOperValue(op, 0)

    def i_sub(self, op):
        # Src op gets sign extended to dst
        flagtup = self.integerSubtraction(op)
        self.doFlags(flagtup)
        (ssize, dsize, sres, ures, sdst, udst) = flagtup
        self.setOperValue(op, 1, ures)

    def doFlags(self, flagtup):
        (ssize, dsize, sres, ures, sdst, udst) = flagtup

        self.setFlag(h8_regs.CCR_H, e_bits.is_signed_half_carry(ures, dsize, udst))
        self.setFlag(h8_regs.CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(sres, dsize))

    def i_subs(self, op):
        # Src op gets sign extended to dst
        ssize = op.opers[0].tsize
        # TODO: Why?
        # dsize = op.opers[1].tsize
        src = e_bits.sign_extend(self.getOperValue(op, 0), ssize, self.ptrsz)
        dst = e_bits.sign_extend(self.getOperValue(op, 1), ssize, self.ptrsz)

        if src is None or dst is None:
            self.undefFlags()
            return None

        res = src - dst
        self.setOperValue(op, 1, res)

    def i_subx(self, op):
        # Src op gets sign extended to dst
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize
        src = e_bits.sign_extend(self.getOperValue(op, 0), ssize, self.ptrsz)
        dst = e_bits.sign_extend(self.getOperValue(op, 1), dsize, self.ptrsz)
        C = self.getFlag(h8_regs.CCR_C)

        if src is None or dst is None:
            self.undefFlags()
            return None

        (ssize, dsize, sres, ures, sdst, udst) = self.intSubBase(dst, src + C, dsize, ssize)
        self.setOperValue(op, 1, ures)

    def i_xor(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        # FIXME PDE and flags
        if src1 is None or src2 is None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        usrc1 = e_bits.unsigned(src1, 4)
        usrc2 = e_bits.unsigned(src2, 4)

        ures = usrc1 ^ usrc2

        self.setOperValue(op, 1, ures)

        self.setFlag(h8_regs.CCR_C, e_bits.is_unsigned_carry(ures, 4))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, 4))
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(ures, 4))

    def i_xorc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getStatusRegister()

        # FIXME PDE and flags
        if src is None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        # TODO: WHY?
        # ssize = op.opers[0].tsize
        # dsize = op.opers[1].tsize

        ures = src ^ dst

        self.setStatusRegister(ures)

    def i_nop(self, op):
        pass

    def i_divxu(self, op):
        divisor = self.getOperValue(op, 0)
        dividend = self.getOperValue(op, 1)

        quotient = int(dividend / divisor)
        remainder = dividend % divisor

        rdval = (remainder << 8) | quotient

        self.setOperValue(op, 1, rdval)

        self.setFlag(h8_regs.CCR_Z, not quotient)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(quotient, 4))

    def i_divxs(self, op):
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        divisor = self.getOperValue(op, 0)
        dividend = self.getOperValue(op, 1)

        sdivisor = e_bits.signed(divisor, ssize)
        sdividend = e_bits.signed(dividend, dsize)

        quotient = int(sdividend / sdivisor)
        remainder = sdividend % sdivisor

        rdval = (remainder << 8) | quotient

        self.setOperValue(op, 1, rdval)

        self.setFlag(h8_regs.CCR_Z, not quotient)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(quotient, 4))

    def i_eepmov(self, op):
        if op.iflags & h8_const.IF_W:
            delta = 2
            count = self.getRegisterByName('r4')
        elif op.iflags & h8_const.IF_B:
            delta = 1
            count = self.getRegisterByName('r4l')

        src = self.getRegister(h8_regs.REG_ER5)
        dst = self.getRegister(h8_regs.REG_ER6)
        logger.info("WARNING: EEPMOV instruction executed... 0x%x -> 0x%x (count=0x%x)", src, dst, count * delta)

        for x in range(count):
            data = self.readMemValue(src, delta)
            self.writeMemValue(dst, data, delta)
            src += delta
            dst += delta
            # FIXME: NMI can interrupt, must be handled after the current read/write cycle

    def i_exts(self, op):
        pass

    def i_extu(self, op):
        pass

    def i_ldc(self, op):
        oper = self.getOperValue(op, 0)
        self.setStatusRegister(oper)

    def i_stc(self, op):
        oper = self.getStatusRegister()
        self.setOperValue(op, 1, oper)

    def i_movfpe(self, op):
        raise Exception("Implement MOVFPE emulator instruction with peripherals")

    def i_movtpe(self, op):
        raise Exception("Implement MOVTPE emulator instruction with peripherals")

    def i_mulxu(self, op):
        '''
        mul, extend as unsigned
        rs is 8 bits
        rd is 16 bits, but only uses the lower 8 bits for multiplicand
        product is then stored in 16-bit rd
        flags are not updated
        '''
        dsize = op.opers[1].tsize
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        ures = (dst * src)
        val = ures & e_bits.u_maxes[dsize]

        self.setOperValue(op, 1, val)

    def i_mulxs(self, op):
        '''
        mul, extend as signed
        rs is 8 bits
        rd is 16 bits, but only uses the lower 8 bits for multiplicand
        product is then stored in 16-bit rd
        flags are not updated
        '''
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        ssrc = e_bits.signed(src, ssize)
        sdst = e_bits.signed(dst, dsize)

        sres = (sdst * ssrc)
        val = sres & e_bits.u_maxes[dsize]

        self.setOperValue(op, 1, val)

    def i_neg(self, op):
        dsize = op.opers[0].tsize
        oper = self.getOperValue(op, 0)
        oper = e_bits.signed(oper, dsize)
        oper = -oper
        self.setOperValue(op, 0, oper)

        self.setFlag(h8_regs.CCR_H, e_bits.is_signed_half_carry(oper, dsize, oper))
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(oper, dsize))
        self.setFlag(h8_regs.CCR_Z, not oper)
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(oper, dsize))
        self.setFlag(h8_regs.CCR_C, e_bits.is_unsigned_carry(oper, dsize))

    def i_not(self, op):
        dsize = op.opers[0].tsize
        oper = self.getOperValue(op, 0)
        # oper = e_bits.signed(oper, dsize)
        oper = e_bits.u_maxes[dsize] - oper
        self.setOperValue(op, 0, oper)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(oper, dsize))
        self.setFlag(h8_regs.CCR_Z, not oper)
        self.setFlag(h8_regs.CCR_V, 0)

    def i_or(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        # FIXME PDE and flags
        if src is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        # TODO: WHY?
        # ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        ures = src | dst

        self.setOperValue(op, 1, ures)
        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(h8_regs.CCR_Z, not ures)
        self.setFlag(h8_regs.CCR_V, 0)

    def i_orc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getStatusRegister()

        # FIXME PDE and flags
        if src is None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        # TODO: WHY?
        # ssize = op.opers[0].tsize
        # dsize = op.opers[1].tsize

        ures = src | dst

        self.setStatusRegister(ures)

    def i_pop(self, op):
        dsize = op.opers[0].tsize
        val = self.doPop()
        self.setOperValue(op, 0, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)

    def i_push(self, op):
        dsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        self.doPush(val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)

    def i_rotl(self, op):
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8)
        val <<= shbits
        val |= (val >> bits)
        val &= e_bits.u_maxes[dsize]
        C = val & 1

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, C)

    def i_rotr(self, op):
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8)
        C = (val >> (shbits - 1)) & 1
        val |= (val << bits)
        val >>= shbits
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, C)

    def i_rotxl(self, op):
        '''
        rotate left, with extend Carry
        '''
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8) - 1

        C = self.getFlag(h8_regs.CCR_C)
        newC = (val >> (bits+1-shbits)) & 1
        val <<= shbits
        val |= (val >> (bits + 2))
        val |= (C << (shbits - 1))
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, newC)

    def i_rotxr(self, op):
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8)
        C = self.getFlag(h8_regs.CCR_C)
        newC = (val >> (shbits-1)) & 1
        val |= (val << (bits + 1))
        val |= (C << bits)
        val >>= shbits
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, newC)

    def i_rte(self, op):
        '''
        return from Interrupt Exception
        EXCLAMATION: stack layout for calls and ISRs differ between archs!
        '''
        logger.info("Return from Interrupt Handler")

        if self.advanced:
            pop = self.doPop(4)
            retAddr = pop & 0xffffff
            ccr = (pop >> 24) & 0xff
        else:
            ccr = self.doPop() & 0xff
            retAddr = self.doPop()

        self.setStatusRegister(ccr)
        return retAddr

    def i_rts(self, op):
        '''
        return from Subroutine
        EXCLAMATION: stack layout for calls and ISRs differ between archs!
        '''
        if self.advanced:
            pop = self.doPop(4)
            retAddr = pop & 0xffffff
        else:
            retAddr = self.doPop()

        return retAddr

    def i_shal(self, op):
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8)

        C = (val >> (bits - shbits)) & 1
        val <<= shbits
        rawval = val
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, e_bits.is_signed_overflow(rawval, dsize))
        self.setFlag(h8_regs.CCR_C, C)

    def i_shar(self, op):
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        logger.debug(repr((shbits, val, dsize)))
        max_mask = e_bits.u_maxes[dsize]
        signbits = ((-1 & max_mask) << ((8 * dsize) - shbits) & max_mask)
        S = val > e_bits.s_maxes[dsize]

        C = (val >> (shbits-1)) & 1
        val >>= shbits

        if S:
            val |= signbits

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, C)

    def i_shll(self, op):
        '''
        same as shal, except for handling of V
        '''
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        bits = (dsize * 8)

        C = (val >> (bits - shbits)) & 1
        val <<= shbits
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, C)

    def i_shlr(self, op):
        '''
        not the same as shar
        '''
        dstidx = len(op.opers) - 1
        if dstidx:
            shbits = self.getOperValue(op, 0)
            val = self.getOperValue(op, 1)
            dsize = op.opers[1].tsize
        else:
            shbits = 1
            val = self.getOperValue(op, 0)
            dsize = op.opers[0].tsize

        # bits = (dsize * 8) - 1

        C = (val >> (shbits-1)) & 1
        val >>= shbits

        self.setOperValue(op, dstidx, val)

        self.setFlag(h8_regs.CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(h8_regs.CCR_Z, not val)
        self.setFlag(h8_regs.CCR_V, 0)
        self.setFlag(h8_regs.CCR_C, C)

    def i_sleep(self, op):
        logger.info("Entering Sleep Mode... waiting for an External Interrupt")
        self.state = CPUSTATE_SLEEP

    def i_str(self, op):
        ccr = self.getStatusRegister()
        self.setOperValue(op, 0, ccr)

    def i_tas(self, op):
        dsize = op.opers[0].tsize
        logger.debug(repr(dsize))
        oper = self.getOperValue(op, 0)

        # do comparison and set flags
        flagtup = self.intSubBase(oper, 0, dsize, dsize)
        self.doFlags(flagtup)

        oper |= 0x80

        self.setOperValue(op, 0, oper)

    def i_trapa(self, op):
        logger.info("SW EXCEPTION:  %s", op)
        # FIXME: processInterrupt()
