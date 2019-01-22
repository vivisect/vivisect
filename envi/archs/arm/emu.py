"""
The initial arm module.
"""

import sys
import struct
import logging
import threading

import envi
import envi.bits as e_bits
from envi.const import *
from envi.archs.arm.regs import *
from envi.archs.arm import ArmModule
from envi.archs.arm.disasm import ArmRegOper, ArmRegShiftImmOper, ArmImmOper

logger = logging.getLogger(__name__)

# CPU state (memory, regs inc SPSRs and banked registers)
# CPU mode  (User, FIQ, IRQ, supervisor, Abort, Undefined, System)
# 
# instruction code
# exception handler code
# FIXME: SPSR handling is not certain.  

# calling conventions
class ArmArchitectureProcedureCall(envi.CallingConvention):
    arg_def = [(CC_REG, REG_R0), (CC_REG, REG_R1), (CC_REG, REG_R2),
                (CC_REG, REG_R3), (CC_STACK_INF, 4),]
    retaddr_def = (CC_REG, REG_R14)
    retval_def = (CC_REG, REG_R0)
    flags = CC_CALLEE_CLEANUP
    align = 8
    pad = 0

aapcs = ArmArchitectureProcedureCall()

class CoProcEmulator:       # useful for prototyping, but should be subclassed
    def __init__(self, ident):
        self.ident = ident

    def stc(self, parms):
        logger.info("CoProcEmu(%s): stc(%r)", self.ident, parms)
    def ldc(self, parms):
        logger.info("CoProcEmu(%s): ldc(%r)", self.ident, parms)
    def cdp(self, parms):
        logger.info("CoProcEmu(%s): cdp(%r)", self.ident, parms)
    def mcr(self, parms):
        logger.info("CoProcEmu(%s): mcr(%r)", self.ident, parms)
    def mcrr(self, parms):
        logger.info("CoProcEmu(%s): mcrr(%r)", self.ident, parms)
    def mrc(self, parms):
        logger.info("CoProcEmu(%s): mrc(%r)", self.ident, parms)
    def mrrc(self, parms):
        logger.info("CoProcEmu(%s): mrrc(%r)", self.ident, parms)


def _getRegIdx(idx, mode):
    if idx >= MAX_REGS:
        return idx
    ridx = idx + (mode*REGS_PER_MODE)  # account for different banks of registers
    ridx = reg_table[ridx]  # magic pointers allowing overlapping banks of registers
    return ridx


ZC_bits = PSR_Z_bit | PSR_C_bit
NC_bits = PSR_N_bit | PSR_C_bit
NZ_bits = PSR_N_bit | PSR_Z_bit
NV_bits = PSR_N_bit | PSR_V_bit


def c0000(flags):   # EQ
    return flags & PSR_Z_bit

def c0001(flags):   # NE
    return flags & PSR_Z_bit == 0

def c0010(flags):   # CS
    return flags & PSR_C_bit

def c0011(flags):   # CC
    return flags & PSR_C_bit == 0

def c0100(flags):   # MI
    return flags & PSR_N_bit

def c0101(flags):   # PL
    return flags & PSR_N_bit == 0

def c0110(flags):   # VS
    return flags & PSR_V_bit

def c0111(flags):   # VC
    return flags & PSR_V_bit == 0

def c1000(flags):   # HI
    return (flags & ZC_bits) == PSR_C_bit   # C set and Z clear

def c1001(flags):   # LS
    #return (flags & NZ_bits) in (0, PSR_Z_bit, ZC_bits) # C clear or Z set
    return (flags & PSR_C_bit == 0) or (flags & PSR_Z_bit) # C clear or Z set

def c1010(flags):   # GE
    return (flags & NV_bits) in (0, NV_bits)    # N == V

def c1011(flags):   # LT
    return (flags & NV_bits) in (PSR_V_bit, PSR_N_bit)    # N != V

def c1100(flags):   # GT
    return (flags & PSR_Z_bit) == 0 and (flags & NV_bits) in (0, NV_bits)   # Z==0, N==V

def c1101(flags):   # LE
    return (flags & PSR_Z_bit) or (flags & NV_bits) in (PSR_V_bit, PSR_N_bit)         # Z==1 or N!=V (basically, "not c1100")


conditionals = [
        c0000,
        c0001,
        c0010,
        c0011,
        c0100,
        c0101,
        c0110,
        c0111,
        c1000,
        c1001,
        c1010,
        c1011,
        c1100,
        c1101,
        ]

top_bits_32 = [(e_bits.u_maxes[4] ^ ((e_bits.u_maxes[4]>>x))) for x in range(4*8)]

LSB_FMT = [0, 'B', '<H', 0, '<I', 0, 0, 0, '<Q',]
MSB_FMT = [0, 'B', '>H', 0, '>I', 0, 0, 0, '>Q',]
LSB_FMT_SIGNED = [0, 'b', '<h', 0, '<i', 0, 0, 0, '<q',]
MSB_FMT_SIGNED = [0, 'b', '>h', 0, '>i', 0, 0, 0, '>q',]

class ArmEmulator(ArmRegisterContext, envi.Emulator):

    def __init__(self):
        # if-then placeholders
        self.itva = None
        self.itflags = None
        self.itcount = None

        # for memory exclusive access:
        self.mem_access_lock = threading.Lock()

        # FIXME: this should be None's, and added in for each real coproc... but this will work for now.
        self.coprocs = [CoProcEmulator(x) for x in xrange(16)]       
        self.int_handlers = [self.default_int_handler for x in range(100)]

        seglist = [ (0,0xffffffff) for x in xrange(6) ]
        envi.Emulator.__init__(self, ArmModule())

        ArmRegisterContext.__init__(self)

        self.addCallingConvention("armcall", aapcs)

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getCPSR()
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setCPSR(flags)

    def setFpFlag(self, which, state):
        flags = self.getFPSCR()
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setCPSR(flags)

    def getFlag(self, which):          # FIXME: CPSR?
        #if (flags_reg == None):
        #    flags_reg = proc_modes[self.getProcMode()][5]
        #flags = self.getRegister(flags_reg)
        flags = self.getCPSR()
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    def readMemValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length At 0x%.8x (va: 0x%.8x wanted %d got %d)" % (self.getProgramCounter(),addr, size, len(bytes)))

        endian_fmt = (LSB_FMT, MSB_FMT)[self.getEndian()]
        return struct.unpack(endian_fmt[size], bytes)[0]

    def writeMemValue(self, addr, value, size):
        endian_fmt = (LSB_FMT, MSB_FMT)[self.getEndian()]
        mask = e_bits.u_maxes[size]
        bytes = struct.pack(endian_fmt[size], (value & mask))
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length At 0x%.8x (va: 0x%.8x wanted %d got %d)" % (self.getProgramCounter(),addr, size, len(bytes)))

        endian_fmt = (LSB_FMT_SIGNED, MSB_FMT_SIGNED)[self.getEndian()]
        return struct.unpack(endian_fmt[size], bytes)[0]

    def parseOpcode(self, va, arch=envi.ARCH_DEFAULT):
        '''
        Parse an opcode from the specified virtual address.

        Example: op = m.parseOpcode(0x7c773803)

        note: differs from the IMemory interface by checking loclist
        '''
        if arch == envi.ARCH_DEFAULT:
            tmode = self.getFlag(PSR_T_bit)
            arch = (envi.ARCH_ARMV7, envi.ARCH_THUMB)[tmode]

        off, b = self.getByteDef(va)
        return self.imem_archs[ (arch & envi.ARCH_MASK) >> 16 ].archParseOpcode(b, off, va)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        try:
            self.setMeta('forrealz', True)
            x = None
            skip = False
        
            # IT block handling
            if self.itcount:
                self.itcount -= 1

                if not (self.itmask & 1):
                    skip = True
                self.itmask >>= 1

            # standard conditional handling
            condval = (op.prefixes >= 0xe)

            if not condval:
                condcheck = conditionals[op.prefixes]
                condval = condcheck(self.getRegister(REG_FLAGS))

            # the actual execution... if we're supposed to.
            if condval and not skip:
                meth = self.op_methods.get(op.mnem, None)
                if meth == None:
                    raise envi.UnsupportedInstruction(self, op)

                # executing opcode now...
                x = meth(op)

            # returned None, so the instruction hasn't directly changed PC
            if x == None:
                pc = self.getProgramCounter()
                x = pc+op.size

            self.setProgramCounter(x)
        finally:
            self.setMeta('forrealz', False)

    def doPush(self, val):
        esp = self.getRegister(REG_SP)
        esp -= 4
        self.writeMemValue(esp, val, 4)
        self.setRegister(REG_SP, esp)

    def doPop(self):
        esp = self.getRegister(REG_SP)
        val = self.readMemValue(esp, 4)
        self.setRegister(REG_SP, esp+4)
        return val

    def getProcMode(self):
        '''
        get current ARM processor mode.  see proc_modes (const.py)
        '''
        return self._rctx_vals[REG_CPSR] & 0x1f     # obfuscated for speed.  could call getCPSR but it's not as fast

    def getCPSR(self):
        '''
        return the Current Program Status Register.
        '''
        return self._rctx_vals[REG_CPSR]

    def getFPSCR(self):
        '''
        return the Current Floating Point Status/Control Register.
        '''
        return self._rctx_vals[REG_FPSCR]

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
        psr = self._rctx_vals[REG_CPSR] & (~mask) | (psr & mask)
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
        """
        Return the current value of the specified register index.
        """
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
        """
        Set a register value by index.
        """
        if mode == None:
            mode = self.getProcMode() & 0xf
        else:
            mode &= 0xf

        self._rctx_dirty = True

        idx = (index & 0xffff)
        ridx = _getRegIdx(idx, mode)

        if idx == index:    # not a metaregister
            self._rctx_vals[ridx] = (value & self._rctx_masks[ridx])      # FIXME: hack.  should look up index in proc_modes dict?
            return

        # If we get here, it's a meta register index.
        # NOTE: offset/width are in bits...
        offset = (index >> 24) & 0xff
        width  = (index >> 16) & 0xff

        #FIXME is it faster to generate or look thses up?
        mask = (2**width)-1
        mask = mask << offset

        # NOTE: basewidth is in *bits*
        basewidth = self._rctx_widths[ridx]
        basemask  = (2**basewidth)-1

        # cut a whole in basemask at the size/offset of mask
        finalmask = basemask ^ mask

        curval = self._rctx_vals[ridx]

        self._rctx_vals[ridx] = (curval & finalmask) | (value << offset)

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

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

        ures = e_bits.unsigned(udst + usrc + carry, tsize)
        sres = e_bits.signed(sdst + ssrc + carry, tsize)
        result = ures & 0x7fffffff

        newcarry = (ures != result)
        #newcarry = (udst >= usrc)
        overflow = (sres != result)

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

        if Sflag:
            curmode = self.getProcMode() 
            if rd == 15:
                if(curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, tsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, tsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, tsize))

        return ures

    def logicalAnd(self, op):
        opercnt = len(op.opers)

        if opercnt == 3:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)

        # PDE
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        res = src1 & src2

        if op.iflags & IF_PSR_S:
            self.setFlag(PSR_N_bit, 0)
            self.setFlag(PSR_Z_bit, not res)
            self.setFlag(PSR_C_bit, 0)
            self.setFlag(PSR_V_bit, 0)
        return res

    def interrupt(self, val):
        if val >= len(self.int_handlers):
            logger.critical("FIXME: Interrupt Handler %x is not handled", val)

        handler = self.int_handlers[val]
        handler(val)

    def default_int_handler(self, val):
        logger.warn("DEFAULT INTERRUPT HANDLER for Interrupt %d (called at 0x%x)", val, self.getProgramCounter())
        logger.warn("Stack Dump:")
        sp = self.getStackCounter()
        for x in range(16):
            logger.warn("\t0x%x:\t0x%x", sp, self.readMemValue(sp, self.psize))
            sp += self.psize

    def i_and(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)
        
    def i_orr(self, op):
        tsize = op.opers[0].tsize
        if len(op.opers) == 3:
            val1 = self.getOperValue(op, 1)
            val2 = self.getOperValue(op, 2)
        else:
            val1 = self.getOperValue(op, 0)
            val2 = self.getOperValue(op, 1)
        val = val1 | val2
        self.setOperValue(op, 0, val)

        Sflag = op.iflags & IF_PSR_S
        if Sflag:
            self.setFlag(PSR_N_bit, e_bits.is_signed(val, tsize))
            self.setFlag(PSR_Z_bit, not val)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(val, tsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(val, tsize))
        
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
            if op.opers[0].reg < REGS_VECTOR_BASE_IDX:
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

                if op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass

        elif len(op.opers) == 2:
            for reg in range(regcnt):
                #frac_bits = 64 - op.opers[1].val

                if op.simdflags & IFS_F32_S32:
                    pass
                elif op.simdflags & IFS_F32_U32:
                    pass
                elif op.simdflags & IFS_S32_F32:
                    pass
                elif op.simdflags & IFS_U32_F32:
                    pass
                elif op.simdflags & IFS_F64_S32:
                    pass
                elif op.simdflags & IFS_F64_U32:
                    pass
                elif op.simdflags & IFS_S32_F64:
                    pass
                elif op.simdflags & IFS_U32_F64:
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
            return newpc

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
        try:
            self.mem_access_lock.acquire()
            return self.i_ldr(op)
        finally:
            self.mem_access_lock.release()

    def i_strex(self, op):
        try:
            self.mem_access_lock.acquire()
            return self.i_str(op)
        finally:
            self.mem_access_lock.release()

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
    i_itet =  i_it
    i_itte =  i_it
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
        val |= (addit<<lsb)

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
        
        #FIXME PDE and flags
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        usrc1 = e_bits.unsigned(src1, dsize)
        usrc2 = e_bits.unsigned(src2, dsize)
        ssrc1 = e_bits.signed(src1, dsize)
        ssrc2 = e_bits.signed(src2, dsize)

        ures = usrc1 + usrc2
        sres = ssrc1 + ssrc2


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
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, dsize))

    def i_adc(self, op):
        if len(op.opers) == 3:
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
        else:
            src1 = self.getOperValue(op, 0)
            src2 = self.getOperValue(op, 1)
        
        #FIXME PDE and flags
        if src1 == None or src2 == None:
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
        self.setRegister(REG_LR, self.getRegister(REG_PC) + len(op))
        return self.getOperValue(op, 0)

    def i_bx(self, op):
        target = self.getOperValue(op, 0)
        self.setFlag(PSR_T_bit, target & 1)
        return target & -2

    def i_blx(self, op):
        self.setRegister(REG_LR, self.getRegister(REG_PC) + len(op))
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
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        usrc1 = e_bits.unsigned(src1, dsize)
        usrc2 = e_bits.unsigned(src2, dsize)
        ssrc1 = e_bits.signed(src1, dsize)
        ssrc2 = e_bits.signed(src2, dsize)

        ures = usrc2 - usrc1
        sres = ssrc2 - ssrc1


        self.setOperValue(op, 0, ures)

        curmode = self.getProcMode() 
        if op.iflags & IF_PSR_S:
            if op.opers[0].reg == 15:
                if (curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, dsize))

    def i_rsb(self, op):
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        res = self.intSubBase(src2, src1, Sflag, op.opers[0].reg)
        self.setOperValue(op, 0, res)

    def i_rsc(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S
        Carry = self.getFlag(PSR_C_bit)

        mask = e_bits.u_maxes[op.opers[1].tsize]
        res = self.AddWithCarry(src2, mask ^ src1, Carry, Sflag, op.opers[0].reg)

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

        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        res = self.intSubBase(src1, src2, Sflag, op.opers[0].reg)
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
        if src1 == None or src2 == None:
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
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(ures, dsize))

    def i_cmp(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        Sflag = op.iflags & IF_PSR_S

        origeflags = self.getRegister(REG_CPSR)

        res2 = self.AddWithCarry(src1, 0xffffffff^src2, 1, Sflag, op.opers[0].reg)
        #eflags2 = self.getRegister(REG_CPSR)

        #self.setRegister(REG_CPSR, origeflags)
        #res = self.intSubBase(src1, src2, Sflag, op.opers[0].reg)
        #eflags1 = self.getRegister(REG_CPSR)

        #if res != res2 or eflags1 != eflags2:
        #    print "==== uhoh: intSubBase and AddWithCarry methods differ!: 0x%x:  %s    %x ? %x  (%x / %x ? %x) "  %\
        #            (op.va, op, res, res2, origeflags, eflags1, eflags2)

    def i_cmn(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        Sflag = op.iflags & IF_PSR_S

        origeflags = self.getRegister(REG_CPSR)

        res2 = self.AddWithCarry(src1, src2, 0, Sflag, op.opers[0].reg)
        eflags2 = self.getRegister(REG_CPSR)

        self.setRegister(REG_CPSR, origeflags)
        res = self.intSubBase(src1, src2, Sflag, op.opers[0].reg)
        #eflags1 = self.getRegister(REG_CPSR)

        #if res != res2 or eflags1 != eflags2:
        #    print "==== uhoh: intSubBase and AddWithCarry methods differ!: 0x%x:  %s    %x ? %x  (%x / %x ? %x) "  %\
        #            (op.va, op, res, res2, origeflags, eflags1, eflags2)

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
            imm5 = self.getOperValue(op, 2)

        else:
            src = self.getOperValue(op, 0)
            imm5 = self.getOperValue(op, 1)

        shift = (32, imm5)[bool(imm5)]
        val = src >> shift
        carry = (src >> (shift-1)) & 1
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
            imm5 = self.getOperValue(op, 2)

        else:
            src = self.getOperValue(op, 0)
            srclen = op.opers[0].tsize
            imm5 = self.getOperValue(op, 1)

        shift = (32, imm5)[bool(imm5)]
        if e_bits.is_signed(src, srclen):
            val = (src >> shift) | top_bits_32[shift]
        else:
            val = (src >> shift)

        carry = (src >> (shift-1)) & 1
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
            if loc != None:
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


opcode_dist = \
[('and', 4083),#
 ('stm', 1120),#
 ('ldr', 1064),#
 ('add', 917),#
 ('stc', 859),#
 ('str', 770),#
 ('bl', 725),#
 ('ldm', 641),#
 ('b', 472),#
 ('ldc', 469),#
 ('tst', 419),#
 ('rsb', 196),#
 ('eor', 180),#
 ('mul', 159),
 ('swi', 128),
 ('sub', 110),#
 ('adc', 96),
 ('cdp', 74),#
 ('orr', 66),
 ('cmn', 59),
 ('mcr', 55),#
 ('stc2', 54),
 ('ldc2', 52),
 ('mrc', 49),#
 ('mvn', 47),
 ('rsc', 46),
 ('teq', 45),
 ('cmp', 41),
 ('sbc', 40),
 ('mov', 35),#
 ('bic', 34),
 ('mcr2', 29),#
 ('mrc2', 28),#
 ('swp', 28),
 ('mcrr', 21),#
 ('mrrc', 20),#
 ('usada8', 20),
 ('qadd', 13),
 ('mrrc2', 10),#
 ('add16', 9),
 ('mla', 9),
 ('mcrr2', 7),#
 ('uqsub16', 6),
 ('uqadd16', 5),
 ('sub16', 5),
 ('umull', 4),
 ('uq', 3),
 ('smlsdx', 3),
 ('uhsub16', 3),
 ('uqsubaddx', 3),
 ('qdsub', 2),
 ('subaddx', 2),
 ('uqadd8', 2),
 ('ssat', 2),
 ('uqaddsubx', 2),
 ('smull', 2),
 ('blx', 2),
 ('smlal', 2),
 ('shsub16', 1),
 ('', 1),
 ('smlsd', 1),
 ('pkhbt', 1),
 ('revsh', 1),
 ('qadd16', 1),
 ('uqsub8', 1),
 ('ssub16', 1),
 ('usad8', 1),
 ('uadd16', 1),
 ('smladx', 1),
 ('swpb', 1),
 ('smlaldx', 1),
 ('usat', 1),
 ('umlal', 1),
 ('rev16', 1),
 ('sadd16', 1),
 ('sel', 1),
 ('sub8', 1),
 ('pkhtb', 1),
 ('umaal', 1),
 ('addsubx', 1),
 ('add8', 1),
 ('smlad', 1),
 ('sxtb', 1),
 ('sadd8', 1)]


'''
A2.3.1 Writing to the PC
    In ARMv7, many data-processing instructions can write to the PC. Writes to the PC are handled as follows:
        * In Thumb state, the following 16-bit Thumb instruction encodings branch to the value written to the PC:
            - encoding T2 of ADD (register, Thumb) on page A8-308
            - encoding T1 of MOV (register, Thumb) on page A8-484.
            The value written to the PC is forced to be halfword-aligned by ignoring its least significant bit, treating that
            bit as being 0.
        * The B, BL, CBNZ, CBZ, CHKA, HB, HBL, HBLP, HBP, TBB, and TBH instructions remain in the same instruction set state
            and branch to the value written to the PC.
            The definition of each of these instructions ensures that the value written to the PC is correctly aligned for
            the current instruction set state.
        * The BLX (immediate) instruction switches between ARM and Thumb states and branches to the value written
            to the PC. Its definition ensures that the value written to the PC is correctly aligned for the new instruction
            set state.
        * The following instructions write a value to the PC, treating that value as an interworking address to branch
            to, with low-order bits that determine the new instruction set state:
                - BLX (register), BX, and BXJ
                - LDR instructions with <Rt> equal to the PC
                - POP and all forms of LDM except LDM (exception return), when the register list includes the PC
                - in ARM state only, ADC, ADD, ADR, AND, ASR (immediate), BIC, EOR, LSL (immediate), LSR (immediate), MOV,
                    MVN, ORR, ROR (immediate), RRX, RSB, RSC, SBC, and SUB instructions with <Rd> equal to the PC and without
                    flag-setting specified.
            For details of how an interworking address specifies the new instruction set state and instruction address, see
            Pseudocode details of operations on ARM core registers on page A2-47.
            Note
                - The register-shifted register instructions, that are available only in the ARM instruction set and are
                    summarized inData-processing (register-shifted register) on page A5-196, cannot write to the PC.
                - The LDR, POP, and LDM instructions first have interworking branch behavior in ARMv5T.
                - The instructions listed as having interworking branch behavior in ARM state only first have this
                    behavior in ARMv7.
                In the cases where later versions of the architecture introduce interworking branch behavior, the behavior in
                earlier architecture versions is a branch that remains in the same instruction set state. For more information,
                see:
                    - Interworking on page AppxL-2453, for ARMv6
                    - Interworking on page AppxO-2539, for ARMv5 and ARMv4.
        * Some instructions are treated as exception return instructions, and write both the PC and the CPSR. For more
            information, including which instructions are exception return instructions, see Exception return on
            page B1-1191.
        * Some instructions cause an exception, and the exception handler address is written to the PC as part of the
            exception entry. Similarly, in ThumbEE state, an instruction that fails its null check causes the address of the
            null check handler to be written to the PC, see Null checking on page A9-1111.

'''

