"""
The initial arm module.
"""

import sys
import struct

import envi
import envi.bits as e_bits
from envi.const import *
from envi.archs.arm.regs import *
from envi.archs.arm import ArmModule

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
    def __init__(self):
        pass

    def stc(self, parms):
        print >>sys.stderr,"CoProcEmu: stc(%s)"%repr(parms)
    def ldc(self, parms):
        print >>sys.stderr,"CoProcEmu: ldc(%s)"%repr(parms)
    def cdp(self, parms):
        print >>sys.stderr,"CoProcEmu: cdp(%s)"%repr(parms)
    def mcr(self, parms):
        print >>sys.stderr,"CoProcEmu: mcr(%s)"%repr(parms)
    def mcrr(self, parms):
        print >>sys.stderr,"CoProcEmu: mcrr(%s)"%repr(parms)
    def mrc(self, parms):
        print >>sys.stderr,"CoProcEmu: mrc(%s)"%repr(parms)
    def mrrc(self, parms):
        print >>sys.stderr,"CoProcEmu: mrrc(%s)"%repr(parms)


def _getRegIdx(idx, mode):
    if idx >= MAX_REGS:
        return idx
    ridx = idx + (mode*17)  # account for different banks of registers
    ridx = reg_table[ridx]  # magic pointers allowing overlapping banks of registers
    return ridx

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

class ArmEmulator(ArmModule, ArmRegisterContext, envi.Emulator):

    def __init__(self):
        ArmModule.__init__(self)

        # FIXME: this should be None's, and added in for each real coproc... but this will work for now.
        self.coprocs = [CoProcEmulator() for x in xrange(16)]       

        seglist = [ (0,0xffffffff) for x in xrange(6) ]
        envi.Emulator.__init__(self, ArmModule())

        ArmRegisterContext.__init__(self)

        self.addCallingConvention("Arm Arch Procedure Call", aapcs)

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
        #FIXME change this (and all uses of it) to passing in format...
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length At 0x%.8x (va: 0x%.8x wanted %d got %d)" % (self.getProgramCounter(),addr, size, len(bytes)))
        if size == 1:
            return struct.unpack("B", bytes)[0]
        elif size == 2:
            return struct.unpack("<H", bytes)[0]
        elif size == 4:
            return struct.unpack("<I", bytes)[0]
        elif size == 8:
            return struct.unpack("<Q", bytes)[0]

    def writeMemValue(self, addr, value, size):
        #FIXME change this (and all uses of it) to passing in format...
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        if size == 1:
            bytes = struct.pack("B",value & 0xff)
        elif size == 2:
            bytes = struct.pack("<H",value & 0xffff)
        elif size == 4:
            bytes = struct.pack("<I", value & 0xffffffff)
        elif size == 8:
            bytes = struct.pack("<Q", value & 0xffffffffffffffff)
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack("b", bytes)[0]
        elif size == 2:
            return struct.unpack("<h", bytes)[0]
        elif size == 4:
            return struct.unpack("<l", bytes)[0]

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        x = None
        if op.prefixes >= 0xe or conditionals[op.prefixes](self.getRegister(REG_FLAGS)>>28):
            meth = self.op_methods.get(op.mnem, None)
            if meth == None:
                raise envi.UnsupportedInstruction(self, op)
            x = meth(op)

        if x == None:
            pc = self.getProgramCounter()
            x = pc+op.size

        self.setProgramCounter(x)

    def doPush(self, val):
        esp = self.getRegister(REG_ESP)
        esp -= 4
        self.writeMemValue(esp, val, 4)
        self.setRegister(REG_ESP, esp)

    def doPop(self):
        esp = self.getRegister(REG_ESP)
        val = self.readMemValue(esp, 4)
        self.setRegister(REG_ESP, esp+4)
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

    def setCPSR(self, psr, mask=0xffffffff):
        '''
        set the CPSR for the current ARM processor mode
        '''
        psr = self._rctx_vals[REG_CPSR] & (~mask) | (psr & mask)
        self._rctx_vals[REG_CPSR] = psr

    def getSPSR(self, mode):
        '''
        get the SPSR for the given ARM processor mode
        '''
        ridx = _getRegIdx(REG_SPSR, mode)
        return self._rctx_vals[ridx]

    def setSPSR(self, mode, psr, mask=0xffffffff):
        '''
        set the SPSR for the given ARM processor mode
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

    def i_and(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)
        
    def i_stm(self, op):
        srcreg = op.opers[0].reg
        addr = self.getOperValue(op,0)
        regvals = self.getOperValue(op, 1)
        regmask = op.opers[1].val
        pc = self.getRegister(REG_PC)       # store for later check

        print "stm"
        addr = self.getRegister(srcreg)
        for val in regvals:
            print hex(val), hex(op.iflags), hex(IF_DAIB_B), hex(IF_DAIB_I)
            if op.iflags & IF_DAIB_B == IF_DAIB_B:
                print "DAIB_B!?!?"
                if op.iflags & IF_DAIB_I == IF_DAIB_I:
                    addr += 4
                else:
                    addr -= 4
                self.writeMemValue(addr, val, 4)
            else:
                print "%x -> [%x]" % (val, addr)
                self.writeMemValue(addr, val, 4)
                if op.iflags & IF_DAIB_I == IF_DAIB_I:
                    addr += 4
                else:
                    addr -= 4

        if op.opers[0].oflags & OF_W:
            self.setRegister(srcreg,addr)
        #FIXME: add "shared memory" functionality?  prolly just in strex which will be handled in i_strex
        # is the following necessary?  
        newpc = self.getRegister(REG_PC)    # check whether pc has changed
        if pc != newpc:
            print "PC HAS CHANGED!  THIS CODE IS WORTHWHILE!"
            return newpc

    i_stmia = i_stm


    def i_ldm(self, op):
        srcreg = op.opers[0].reg
        addr = self.getOperValue(op,0)
        #regmask = self.getOperValue(op,1)
        regmask = op.opers[1].val
        pc = self.getRegister(REG_PC)       # store for later check

        for reg in xrange(16):
            if (1<<reg) & regmask:
                if op.iflags & IF_DAIB_B == IF_DAIB_B:
                    if op.iflags & IF_DAIB_I == IF_DAIB_I:
                        addr += 4
                    else:
                        addr -= 4
                    regval = self.readMemValue(addr, 4)
                    self.setRegister(reg, regval)
                else:
                    regval = self.readMemValue(addr, 4)
                    self.setRegister(reg, regval)
                    if op.iflags & IF_DAIB_I == IF_DAIB_I:
                        addr += 4
                    else:
                        addr -= 4
        if op.opers[0].oflags & OF_W:
            self.setRegister(srcreg,addr)
        #FIXME: add "shared memory" functionality?  prolly just in ldrex which will be handled in i_ldrex
        # is the following necessary?  
        newpc = self.getRegister(REG_PC)    # check whether pc has changed
        if pc != newpc:
            return newpc

    i_ldmia = i_ldm

    def i_ldr(self, op):
        # hint: covers ldr, ldrb, ldrbt, ldrd, ldrh, ldrsh, ldrsb, ldrt   (any instr where the syntax is ldr{condition}stuff)
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
        if op.opers[0].reg == REG_PC:
            return val

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    '''def i_adr(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    def i_msr(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
'''
    i_msr = i_mov
    i_adr = i_mov

    def i_str(self, op):
        # hint: covers str, strb, strbt, strd, strh, strsh, strsb, strt   (any instr where the syntax is str{condition}stuff)
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

    def i_add(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        
        #FIXME PDE and flags
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
        #self.setFlag(PSR_V_bit, e_bits.is_signed_overflow(sres, dsize))
        
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
        #FIXME account for same operand with zero result for PDE
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
        #FIXME account for same operand with zero result for PDE
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
        
        #FIXME PDE and flags
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

