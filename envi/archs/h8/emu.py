"""
The H8 Emulator module.
"""

import sys
import struct

import emu
import envi
import envi.bits as e_bits
from envi.archs.h8 import H8Module
from envi.archs.h8.regs import *
from disasm import H8RegDirOper

# calling conventions
class H8ArchitectureProcedureCall(envi.CallingConvention):
    """
    Implement calling conventions for your arch.
    """
    def execCallReturn(self, emu, value, ccinfo=None):
        sp = emu.getRegister(REG_SP)
        pc = struct.unpack(">H", emu.readMemory(sp, 2))[0]
        sp += 2 # For the saved pc
        sp += (2 * argc) # Cleanup saved args

        emu.setRegister(REG_SP, sp)
        emu.setRegister(REG_R0, value)
        emu.setProgramCounter(pc)

    def getCallArgs(self, emu, count):
        return emu.getRegisters(0xf)  # r0-r3 are used to hand in parameters.  additional ph8s are stored and pointed to by r0

aapcs = H8ArchitectureProcedureCall()


CPUSTATE_RESET =    0
CPUSTATE_EXC =      1
CPUSTATE_EXEC =     2
CPUSTATE_BUS =      3
CPUSTATE_SLEEP =    4
CPUSTATE_SWSTDBY =  5
CPUSTATE_HWSTDBY =  6

class H8Emulator(H8Module, H8RegisterContext, envi.Emulator):
    IVT_RESET = 0

    def __init__(self, advanced=True):
        H8Module.__init__(self)
        envi.Emulator.__init__(self, self)
        H8RegisterContext.__init__(self)

        self.state = CPUSTATE_RESET
        self.ptrsz = 0

        seglist = [ (0,0xffffffff) for x in xrange(6) ]

        self.setAdvanced(advanced)
        self.addCallingConvention("H8 Arch Procedure Call", aapcs)

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
        va = emuProcessInterrupt_2140(intval)
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
                print("Ignoring maskable interrupt (CCR_I flag is set)")
                return

        print("Interrupt Handler: 0x%x" % intval)

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
        print("Interrupt Handler: 0x%x" % intval)

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
        self.setRegister(REG_EFLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(REG_FLAGS)
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_FLAGS)
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
            return struct.unpack("B", bytes)[0]
        elif size == 2:
            return struct.unpack(">H", bytes)[0]
        elif size == 4:
            return struct.unpack(">L", bytes)[0]
        elif size == 8:
            return struct.unpack(">Q", bytes)[0]

    def writeMemValue(self, addr, value, size):
        #FIXME change this (and all uses of it) to passing in format...
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        if size == 1:
            bytes = struct.pack("B",value & 0xff)
        elif size == 2:
            bytes = struct.pack(">H",value & 0xffff)
        elif size == 4:
            bytes = struct.pack(">L", value & 0xffffffff)
        elif size == 8:
            bytes = struct.pack(">Q", value & 0xffffffffffffffff)
        self.writeMemory(addr, bytes)

    def readMemSignedValue(self, addr, size):
        #FIXME: Remove byte check and possibly half-word check.  (possibly all but word?)
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack("b", bytes)[0]
        elif size == 2:
            return struct.unpack(">h", bytes)[0]
        elif size == 4:
            return struct.unpack(">l", bytes)[0]

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new pc
        x = None
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)
        x = meth(op)
        #print >>sys.stderr,"executed instruction, returned: %s"%x

        if x == None:
            pc = self.getProgramCounter()
            x = pc+op.size

        self.setProgramCounter(x)

    def doPush(self, val, inc=2, reg=REG_SP):
        sp = self.getRegister(reg)
        sp -= inc
        self.writeMemValue(sp, val, inc)
        self.setRegister(reg, sp)

    def doPop(self, inc=2, reg=REG_SP):
        sp = self.getRegister(reg)
        val = self.readMemValue(sp, inc)
        self.setRegister(reg, sp+inc)
        return val

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        if dst == None or src == None:
            self.undefFlags()
            return None

        return self.intSubBase(dst, dsize, src, ssize)

    def intSubBase(self, src1, dsize, src2, ssize):
        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.

        usrc = e_bits.unsigned(src1, ssize)
        udst = e_bits.unsigned(src2, dsize)

        ssrc = e_bits.signed(src1, ssize)
        sdst = e_bits.signed(src2, dsize)

        ures = udst - usrc
        sres = sdst - ssrc

        self.setFlag(CCR_H, e_bits.is_signed_half_carry(ures, dsize, udst))
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))

        return ures


    def logicalAnd(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)

        # PDE
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        res = src1 & src2

        return res

    def i_and(self, op):
        dsize = op.opers[1].tsize
        res = self.logicalAnd(op)
        self.setOperValue(op, 1, res)
       
        self.setFlag(CCR_Z, not res)
        self.setFlag(CCR_N, e_bits.is_signed(res, dsize))
        self.setFlag(CCR_V, 0)

    def i_andc(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 1, res)
       


    def i_band(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        val = self.getOperValue(op, 1)

        val >>= bit
        val &= C

        self.setFlag(CCR_C, val)

    def i_bra(self, op):
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_brn(self, op):
        pass

    def i_bhi(self, op):
        if not (self.getFlag(CCR_C) == 0 or self.getFlag(CCR_Z) == 0):  return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bls(self, op):
        if not (self.getFlag(CCR_C) or self.getFlag(CCR_Z)):    return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bhs(self, op):
        if self.getFlag(CCR_C):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_blo(self, op):
        if not self.getFlag(CCR_C):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bne(self, op):
        if self.getFlag(CCR_Z):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_beq(self, op):
        if not self.getFlag(CCR_Z):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bvc(self, op):
        if self.getFlag(CCR_V):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bvs(self, op):
        if not self.getFlag(CCR_V):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bpl(self, op):
        if self.getFlag(CCR_N):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bmi(self, op):
        if not self.getFlag(CCR_N):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bge(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if self.getFlag(CCR_V) != self.getFlag(CCR_N):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_blt(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if self.getFlag(CCR_V) == self.getFlag(CCR_N):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_bgt(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if (self.getFlag(CCR_V) != self.getFlag(CCR_N)) or self.getFlag(CCR_Z):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    def i_ble(self, op):    # FIXME: TEST.  these last 4 seem mixed up.
        if not ((self.getFlag(CCR_V) != self.getFlag(CCR_N)) and self.getFlag(CCR_Z)):     return
        nextva = self.getOperValue(op, 0)
        return nextva

    i_bt = i_bra
    i_bf = i_brn
    i_bcc = i_bhs
    i_bcs = i_blo


    def i_bclr(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1<<bit)
        self.setOperValue(op, 1, tgt)

    def i_biand(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C &= ~(tgt>>bit) & 1
        self.setFlag(CCR_C, C)

    def i_bild(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C = ~(tgt>>bit) & 1
        self.setFlag(CCR_C, C)

    def i_bior(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C |= ~(tgt>>bit) & 1
        self.setFlag(CCR_C, C)

    def i_bist(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1<<bit)
        tgt |= (C ^ 1) << bit
        self.setOperValue(op, 1, tgt)

    def i_bixor(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C ^= ~(tgt>>bit) & 1
        self.setFlag(CCR_C, C)

    def i_bld(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C = (tgt>>bit) & 1
        self.setFlag(CCR_C, C)
        
    def i_bnot(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt ^= (1<<bit)
        self.setOperValue(op, 1, tgt)

    def i_bor(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C |= (tgt>>bit) & 1
        self.setFlag(CCR_C, C)

    def i_bset(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt |= (1<<bit)
        self.setOperValue(op, 1, tgt)

    def i_bst(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        tgt &= ~(1<<bit)
        tgt |= C << bit
        self.setOperValue(op, 1, tgt)

    def i_btst(self, op):
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        Z = ((tgt>>bit) & 1) ^ 1
        self.setFlag(CCR_Z, Z)
        
    def i_bxor(self, op):
        C = self.getFlag(CCR_C)
        bit = self.getOperValue(op, 0)
        tgt = self.getOperValue(op, 1)

        C ^= (tgt>>bit) & 1
        self.setFlag(CCR_C, C)


    def i_cmp(self, op):
        self.integerSubtraction(op)

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
        reglist = self.getOperValue(op,0)

        for reg in reglist:
            val = self.getRegister(reg)
            op.opers[1].setOperValue(op, self, val)

    def i_ldm(self, op):
        reglist = self.getOperValue(op,1)

        for reg in reglist:
            regval = op.opers[0].getOperValue(op, self, mod=True)
            self.setRegister(reg, regval)

    def i_mov(self, op):
        ssize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, ssize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)

        if isinstance(op.opers[1], H8RegDirOper) and op.opers[1].reg == REG_PC:
            return val

    def integerAddition(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        #FIXME PDE and flags
        if src == None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        udst = e_bits.unsigned(dst, dsize)
        sdst = e_bits.signed(dst, dsize)

        usrc = e_bits.unsigned(src, dsize)
        ssrc = e_bits.signed(src, dsize)

        ures = usrc + udst
        sres = ssrc + sdst

        return (ssize, dsize, sres, ures, sdst, udst)

    def i_add(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        self.setOperValue(op, 1, ures)

        # FIXME: test and validate
        self.setFlag(CCR_H, e_bits.is_signed_half_carry(sres, dsize, sdst))
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))

    def i_adds(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        self.setOperValue(op, 1, ures)

    def i_addx(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        C = self.getFlag(CCR_C)
        sres += C
        ures += C

        self.setOperValue(op, 1, ures)

        # FIXME: test and validate  (same as i_add)
        self.setFlag(CCR_H, e_bits.is_signed_half_carry(sres, dsize, sdst))
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))



    def i_daa(self, op):
        oper = self.getOperValue(op, 0)
        upop = oper >> 4 & 0xf
        loop = oper & 0xf
        C = self.getFlag(CCR_C)
        H = self.getFlag(CCR_H)

        addtup = bcd_add.get((C, H, upop, loop))
        if addtup == None:
            print("DAA:  %x %x %x %x - addtup is None" % (C, H, upop, loop))
            return #FIXME: raise exception once figured out
        addval, resC = addtup
        ures = addval + oper

        self.setOperValue(op, 0, ures)

        self.setFlag(CCR_N, e_bits.is_signed(ures, 1))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_C, resC)

    def i_das(self, op):
        oper = self.getOperValue(op, 0)
        upop = oper >> 4 & 0xf
        loop = oper & 0xf
        C = self.getFlag(CCR_C)
        H = self.getFlag(CCR_H)

        addtup = bcd_sub.get((C, H, upop, loop))
        if addtup == None:
            print("DAS:  %x %x %x %x - addtup is None" % (C, H, upop, loop))
            return #FIXME: raise exception once figured out
        addval, resC = addtup
        ures = addval + oper

        self.setOperValue(op, 0, ures)

        self.setFlag(CCR_N, e_bits.is_signed(ures, 1))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_C, resC)       # this should always be what it was coming in

    def i_inc(self, op):
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

        ures = usrc + udst
        sres = ssrc + udst

        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))
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

        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))
        # V must be set if previous value was 0x80 (per docs, page 73 of H8/300)

        self.setOperValue(op, dstidx, ures)

    def i_jmp(self, op):
        return self.getOperValue(op, 0)

    def i_sub(self, op):
        # Src op gets sign extended to dst
        res = self.integerSubtraction(op)
        self.setOperValue(op, 1, res)

    def i_subs(self, op):
        # Src op gets sign extended to dst
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize
        src = e_bits.sign_extend(self.getOperValue(op, 0), ssize, self.ptrsz)
        dst = e_bits.sign_extend(self.getOperValue(op, 1), ssize, self.ptrsz)

        if src == None or dst == None:
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
        C = self.getFlag(CCR_C)

        if src == None or dst == None:
            self.undefFlags()
            return None

        res = self.intSubBase(dst, dsize, src + C, ssize)
        self.setOperValue(op, 1, res)

    def i_xor(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        
        #FIXME PDE and flags
        if src1 == None or src2 == None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        usrc1 = e_bits.unsigned(src1, 4)
        usrc2 = e_bits.unsigned(src2, 4)

        ures = usrc1 ^ usrc2

        self.setOperValue(op, 1, ures)

        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, 4))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, 4))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(ures, 4))

    def i_xorc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getStatusRegister()

        #FIXME PDE and flags
        if src == None:
            self.undefFlags()
            self.setOperValue(op, 1, None)
            return

        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        ures = src ^ dst

        self.setStatusRegister(ures)

    def i_nop(self, op):
        pass


    def i_divxu(self, op):
        divisor = self.getOperValue(op, 0)
        dividend = self.getOperValue(op, 1)

        quotient = dividend / divisor
        remainder = dividend % divisor

        rdval = (remainder << 8) | quotient

        self.setOperValue(op, 1, rdval)

        self.setFlag(CCR_Z, not quotient)
        self.setFlag(CCR_N, e_bits.is_signed(quotient, 4))

    def i_divxs(self, op):
        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        divisor = self.getOperValue(op, 0)
        dividend = self.getOperValue(op, 1)

        sdivisor = e_bits.signed(divisor, ssize)
        sdividend = e_bits.signed(dividend, dsize)
        
        quotient = sdividend / sdivisor
        remainder = sdividend % sdivisor

        rdval = (remainder << 8) | quotient

        self.setOperValue(op, 1, rdval)

        self.setFlag(CCR_Z, not quotient)
        self.setFlag(CCR_N, e_bits.is_signed(quotient, 4))

    def i_eepmov(self, op):
        if op.iflags & IF_W:
            delta = 2
            count = self.getRegisterByName('r4')
        elif op.iflags & IF_B:
            delta = 1
            count = self.getRegisterByName('r4l')

        src = self.getRegister(REG_ER5)
        dst = self.getRegister(REG_ER6)
        print("WARNING: EEPMOV instruction executed... 0x%x -> 0x%x (count=0x%x)" % (
            src, dst, count * delta))

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
        
        self.setFlag(CCR_H, e_bits.is_signed_half_carry(oper, dsize, oper))
        self.setFlag(CCR_N, e_bits.is_signed(oper, dsize))
        self.setFlag(CCR_Z, not oper)
        self.setFlag(CCR_V, e_bits.is_signed_overflow(oper, dsize))
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(oper, dsize))

    def i_not(self, op):
        dsize = op.opers[0].tsize
        oper = self.getOperValue(op, 0)
        #oper = e_bits.signed(oper, dsize)
        oper = e_bits.u_maxes[dsize] - oper
        self.setOperValue(op, 0, oper)
        
        self.setFlag(CCR_N, e_bits.is_signed(oper, dsize))
        self.setFlag(CCR_Z, not oper)
        self.setFlag(CCR_V, 0)

    def i_or(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        #FIXME PDE and flags
        if src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        ures = src | dst

        self.setOperValue(op, 1, ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_V, 0)

    def i_orc(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getStatusRegister()

        #FIXME PDE and flags
        if src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
            return

        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        ures = src | dst

        self.setStatusRegister(ures)

    def i_pop(self, op):
        dsize = op.opers[0].tsize
        val = self.doPop()
        self.setOperValue(op, 0, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)

    def i_push(self, op):
        dsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        self.doPush(val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)

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

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, C)

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
        C = (val >>(shbits-1)) & 1
        val |= (val<<(bits))
        val >>= shbits
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, C)

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

        C = self.getFlag(CCR_C)
        newC = (val >> (bits+1-shbits)) & 1
        val <<= shbits
        val |= (val >> (bits + 2))
        val |= (C << (shbits - 1))
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, newC)

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
        C = self.getFlag(CCR_C)
        newC = (val >> (shbits-1)) & 1
        val |= (val << (bits + 1))
        val |= (C << bits)
        val >>= shbits
        val &= e_bits.u_maxes[dsize]

        self.setOperValue(op, dstidx, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, newC)

    def i_rte(self, op):
        '''
        return from Interrupt Exception
        EXCLAMATION: stack layout for calls and ISRs differ between archs!
        '''
        print("Return from Interrupt Handler")

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

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, e_bits.is_signed_overflow(rawval, dsize))
        self.setFlag(CCR_C, C)

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

        print shbits, val, dsize
        max_mask = e_bits.u_maxes[dsize]
        signbits = ((-1&max_mask)<<((8*dsize)-shbits) & max_mask)
        S = val > e_bits.s_maxes[dsize]

        C = (val >> (shbits-1)) & 1
        val >>= shbits

        if S:
            val |= signbits

        self.setOperValue(op, dstidx, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, C)

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

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, C)

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

        bits = (dsize * 8) - 1

        C = (val >> (shbits-1)) & 1
        val >>= shbits

        self.setOperValue(op, dstidx, val)

        self.setFlag(CCR_N, e_bits.is_signed(val, dsize))
        self.setFlag(CCR_Z, not val)
        self.setFlag(CCR_V, 0)
        self.setFlag(CCR_C, C)

    def i_sleep(self, op):
        print("Entering Sleep Mode... waiting for an External Interrupt")
        self.state = CPUSTATE_SLEEP

    def i_str(self, op):
        ccr = self.getStatusRegister()
        self.setOperValue(op, 0, ccr)

    def i_tas(self, op):
        dsize = op.opers[0].tsize
        print dsize
        oper = self.getOperValue(op, 0)

        # do comparison and set flags
        self.intSubBase(oper, dsize, 0, dsize)
        oper |= 0x80

        self.setOperValue(op, 0, oper)

    def i_trapa(self, op):
        print("SW EXCEPTION:  %s" % op)
        #FIXME: processInterrupt()

bcd_add = {}
for x in range(0xa):
    for y in range(0xa):
        bcd_add[(0,0,(x,y))] = 0, 0

    for y in range(4):
        bcd_add[(0,1,(x,y))] = 0x6, 0

for x in range(9):
    for y in range(0xa, 0x10):
        bcd_add[(0,0,(x,y))] = 0x6, 0

for x in range(0xa, 0x10):
    for y in range(0xa):
        bcd_add[(0,0,(x,y))] = 0x60, 1

    for y in range(4):
        bcd_add[(0,1,(x,y))] = 0x66, 1

for x in range(9, 0x10):
    for y in range(0xa, 0x10):
        bcd_add[(0,0,(x,y))] = 0x66, 1

for x in range(3):
    for y in range(0xa):
        bcd_add[(1,0,(x,y))] = 0x60, 1

    for y in range(0xa, 0x10):
        bcd_add[(1,0,(x,y))] = 0x66, 1

for x in range(4):
    for y in range(4):
        bcd_add[(1,1,(x,y))] = 0x66, 1

bcd_sub = {}
for x in range(0xa):
    for y in range(0xa):
        bcd_sub[(0,0,(x,y))] = 0, 0

for x in range(0x9):
    for y in range(6, 0x10):
        bcd_sub[(0,1,(x,y))] = 0xfa, 0

for x in range(7, 0x10):
    for y in range(0xa):
        bcd_sub[(1,0,(x,y))] = 0xa0, 1

for x in range(6, 0x10):
    for y in range(6, 0x10):
        bcd_sub[(1,1,(x,y))] = 0x9a, 1

sign_ext_bits = {
        1: [((-1&0xff)<<(8-x) & 0xff) for x in range(8)],
        2: [],
        4: [],
        }
