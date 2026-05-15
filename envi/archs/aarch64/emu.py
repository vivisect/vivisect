"""
The initial aarch64 module.
"""

import sys
import struct
import logging

import envi
import envi.bits as e_bits
from envi.const import *
from envi.archs.aarch64.regs import *
from envi.archs.aarch64 import A64Module

logger = logging.getLogger(__name__)

# CPU state (memory, regs inc SPSRs and banked registers)
# CPU mode  (User, FIQ, IRQ, supervisor, Abort, Undefined, System)
# 
# instruction code
# exception handler code

# calling conventions

## NO FREAKING CLUE YET....
class A64Call(envi.CallingConvention):
    arg_def = [(CC_REG, REG_X0), (CC_REG, REG_X1), (CC_REG, REG_X2), (CC_REG, REG_X3), 
            (CC_REG, REG_X4), (CC_REG, REG_X5), (CC_REG, REG_X6), (CC_REG, REG_X7), 
            (CC_STACK_INF, 8),]
    retaddr_def = (CC_REG, REG_X30)
    retval_def = (CC_REG, REG_X0)
    flags = CC_CALLEE_CLEANUP
    align = 8
    pad = 0

a64call = A64Call()
###


class CoProcEmulator:       # useful for prototyping, but should be subclassed
    def __init__(self):
        pass

    def stc(self, parms):
        logger.info("CoProcEmu: stc(%r)", parms)
    def ldc(self, parms):
        logger.info("CoProcEmu: ldc(%r)", parms)
    def cdp(self, parms):
        logger.info("CoProcEmu: cdp(%r)", parms)
    def mcr(self, parms):
        logger.info("CoProcEmu: mcr(%r)", parms)
    def mcrr(self, parms):
        logger.info("CoProcEmu: mcrr(%r)", parms)
    def mrc(self, parms):
        logger.info("CoProcEmu: mrc(%r)", parms)
    def mrrc(self, parms):
        logger.info("CoProcEmu: mrrc(%r)", parms)


def _getRegIdx(idx, mode):
    '''
    Currently cheating and simply supporting only one mode and associated registers.
    '''
    if idx >= MAX_REGS:
        return idx

    ridx = idx
    #ridx = idx + (mode*17)  # account for different banks of registers
    #ridx = reg_table[ridx]  # magic pointers allowing overlapping banks of registers
    return ridx


# Conditional handlers based in bitfield.  Used for handling bitfields in an array
def c0000(flags):
    return flags & 4

def c0001(flags):
    return flags & 4 == 0

def c0010(flags):
    return flags & 2

def c0011(flags):
    return flags & 2 == 0

def c0100(flags):
    return flags & 8

def c0101(flags):
    return flags & 8 == 0

def c0110(flags):
    return flags & 1

def c0111(flags):
    return flags & 1 == 0

def c1000(flags):
    return (flags & 6) == 2

def c1001(flags):
    return (flags & c) in (0, 4, 6) # C clear or Z set

def c1010(flags):
    return (flags & 9) in (0, 9)    # N == V

def c1011(flags):
    return (flags & 9) in (1, 8)    # N != V

def c1100(flags):
    return (flags & 4) == 0 and (flags & 9) in (0, 9)   # Z==0, N==V

def c1101(flags):
    return (flags & 4) or (flags & 9) in (1, 8)         # Z==1 or N!=V (basically, "not c1100")


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

class A64Emulator(A64Module, A64RegisterContext, envi.Emulator):
    def __init__(self):
        A64Module.__init__(self)

        # FIXME: this should be None's, and added in for each real coproc... but this will work for now.
        self.coprocs = [CoProcEmulator() for x in range(16)]       

        seglist = [ (0,0xffffffff) for x in range(6) ]
        envi.Emulator.__init__(self, A64Module())

        A64RegisterContext.__init__(self)

        self.addCallingConvention("a64call", a64call)

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_EFLAGS, None)

    def setFlag(self, which, state):
        flags = self.getCPSR()
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setCPSR(flags)

    def getFlag(self, which):
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
        if size == 1:
            return struct.unpack(b"B", bytes)[0]
        elif size == 2:
            return struct.unpack(b"<H", bytes)[0]
        elif size == 4:
            return struct.unpack(b"<I", bytes)[0]
        elif size == 8:
            return struct.unpack(b"<Q", bytes)[0]

    def writeMemValue(self, addr, value, size):
        if size == 1:
            bytes = struct.pack(b"B",value & 0xff)
        elif size == 2:
            bytes = struct.pack(b"<H",value & 0xffff)
        elif size == 4:
            bytes = struct.pack(b"<I", value & 0xffffffff)
        elif size == 8:
            bytes = struct.pack(b"<Q", value & 0xffffffffffffffff)
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack(b"b", bytes)[0]
        elif size == 2:
            return struct.unpack(b"<h", bytes)[0]
        elif size == 4:
            return struct.unpack(b"<l", bytes)[0]

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        x = None
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)
        x = meth(op)

        if x == None:
            pc = self.getProgramCounter()
            x = pc+op.size

        self.setProgramCounter(x)

    def doPush(self, val):
        sp = self.getRegister(REG_SP)
        sp -= 8
        self.writeMemValue(sp, val, 8)
        self.setRegister(REG_SP, sp)

    def doPop(self):
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, 8)
        self.setRegister(REG_SP, sp+8)
        return val

    def getProcMode(self):
        '''
        get current AARCH64 processor mode.  see proc_modes (const.py)
        '''
        return self._rctx_vals[REG_CPSR] & 0x1f     # obfuscated for speed.  could call getCPSR but it's not as fast

    def getCPSR(self):
        '''
        return the Current Program Status Register.
        '''
        return self._rctx_vals[REG_CPSR]

    def setCPSR(self, psr, mask=0xffffffff):
        '''
        set the CPSR for the current AARCH64 processor mode
        '''
        psr = self._rctx_vals[REG_CPSR] & (~mask) | (psr & mask)
        self._rctx_vals[REG_CPSR] = psr

    def getSPSR(self, mode):
        '''
        get the SPSR for the given AARCH64 processor mode
        '''
        ridx = _getRegIdx(REG_SPSR, mode)
        return self._rctx_vals[ridx]

    def setSPSR(self, mode, psr, mask=0xffffffff):
        '''
        set the SPSR for the given AARCH64 processor mode
        '''
        ridx = _getRegIdx(PSR_Offset, mode)
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
            self._rctx_vals[ridx] = (value & self._rctx_masks[ridx])
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

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        return self.intSubBase(src1, src2, Sflag)

    def intSubBase(self, src1, src2, Sflag=0, rd=0):
        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.


        udst = e_bits.unsigned(src1, 4)
        usrc = e_bits.unsigned(src2, 4)

        sdst = e_bits.signed(src1, 4)
        ssrc = e_bits.signed(src2, 4)

        ures = udst - usrc
        sres = sdst - ssrc

        if Sflag:
            curmode = self.getProcMode() 
            if rd == 15:
                if(curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, 4))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_C_bit, not e_bits.is_unsigned_carry(ures, 4))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, 4))

        return ures

    def logicalAnd(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)

        # PDE
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        res = src1 & src2

        self.setFlag(PSR_N_bit, 0)
        self.setFlag(PSR_Z_bit, not res)
        self.setFlag(PSR_C_bit, 0)
        self.setFlag(PSR_V_bit, 0)
        return res

    def i_nop(self, op):
        return
        
    def i_and(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)
        
    def i_stp(self, op):
        dsize = op.opers[0].tsize
        val1 = self.getOperValue(op, 0)
        val2 = self.getOperValue(op, 1)
        baseaddr = self.getOperAddr(op, 2)
        self.writeMemValue(baseaddr, val1, dsize)
        self.writeMemValue(baseaddr + dsize, val2, dsize)


    def i_ldp(self, op):
        dsize = op.opers[0].tsize
        baseaddr = self.getOperAddr(op, 2)
        val1 = self.readMemValue(baseaddr, dsize)
        val2 = self.readMemValue(baseaddr + dsize, dsize)

        if op.opers[0].reg == REG_PC:
            return val1
        if op.opers[1].reg == REG_PC:
            return val2

    def i_ldr(self, op):
        # hint: covers ldr, ldrb, ldrbt, ldrd, ldrh, ldrsh, ldrsb, ldrt   (any instr where the syntax is ldr{condition}stuff)
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
        if op.opers[0].reg == REG_PC:
            return val

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    def i_movi(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    i_msr = i_mov
    i_adr = i_mov
    i_adrp = i_mov
    # confirm these next ones are ok
    i_movk = i_mov
    i_movz = i_mov

    def i_rev(self, op):
        # rev
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

    def i_str(self, op):
        # hint: covers str, strb, strbt, strd, strh, strsh, strsb, strt   (any instr where the syntax is str{condition}stuff)
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

    def i_add(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        s2size = op.opers[2].tsize

        usrc1 = e_bits.unsigned(src1, 4)
        usrc2 = e_bits.unsigned(src2, 4)
        ssrc1 = e_bits.signed(src1, 4)
        ssrc2 = e_bits.signed(src2, 4)

        ures = usrc1 + usrc2
        sres = ssrc1 + ssrc2


        self.setOperValue(op, 0, ures)

        curmode = self.getProcMode() 
        if op.iflags & IF_S:
            if op.opers[0].reg == 15 and (curmode != PM_sys and curmode != PM_usr):
                self.setCPSR(self.getSPSR(curmode))
            else:
                raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, dsize))

    def i_b(self, op):
        '''
        conditional branches (eg. bne) will be handled here
        '''
        return self.getOperValue(op, 0)

    i_br = i_b

    def i_bl(self, op):
        self.setRegister(REG_LR, self.getRegister(REG_PC))
        return self.getOperValue(op, 0)

    def i_tst(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ures = src1 & src2

        self.setFlag(PSR_N_bit, e_bits.is_signed(ures, dsize))
        self.setFlag(PSR_Z_bit, (0,1)[ures==0])
        self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, dsize))
        
    def i_rsb(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        s2size = op.opers[2].tsize

        usrc1 = e_bits.unsigned(src1, 4)
        usrc2 = e_bits.unsigned(src2, 4)
        ssrc1 = e_bits.signed(src1, 4)
        ssrc2 = e_bits.signed(src2, 4)

        ures = usrc2 - usrc1
        sres = ssrc2 - ssrc1


        self.setOperValue(op, 0, ures)

        curmode = self.getProcMode() 
        if op.iflags & IF_S:
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
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        res = self.intSubBase(src2, src1, Sflag, op.opers[0].reg)
        self.setOperValue(op, 0, res)

    def i_sub(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_PSR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        res = self.intSubBase(src1, src2, Sflag, op.opers[0].reg)
        self.setOperValue(op, 0, res)

    i_subs = i_sub

    def i_eor(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        usrc1 = e_bits.unsigned(src1, 4)
        usrc2 = e_bits.unsigned(src2, 4)

        ures = usrc1 ^ usrc2

        self.setOperValue(op, 0, ures)

        curmode = self.getProcMode() 
        if op.iflags & IF_S:
            if op.opers[0].reg == 15:
                if (curmode != PM_sys and curmode != PM_usr):
                    self.setCPSR(self.getSPSR(curmode))
                else:
                    raise Exception("Messed up opcode...  adding to r15 from PM_usr or PM_sys")
            self.setFlag(PSR_C_bit, e_bits.is_unsigned_carry(ures, 4))
            self.setFlag(PSR_Z_bit, not ures)
            self.setFlag(PSR_N_bit, e_bits.is_signed(ures, 4))
            self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, 4))

    def i_cmp(self, op):
        # Src op gets sign extended to dst
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        Sflag = op.iflags & IF_PSR_S

        res = self.intSubBase(src1, src2, Sflag, op.opers[0].reg)

    i_cmps = i_cmp


    # Coprocessor Instructions
    def i_stc(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.stc(op.opers)

    def i_ldc(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.ldc(op.opers)

    def i_cdp(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.cdp(op.opers)

    def i_mrc(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.mrc(op.opers)

    def i_mrrc(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.mrrc(op.opers)

    def i_mcr(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.mrrc(op.opers)

    def i_mcrr(self, op):
        cpnum = op.opers[0]
        coproc = self._getCoProc(cpnum)
        coproc.mcrr(op.opers)


