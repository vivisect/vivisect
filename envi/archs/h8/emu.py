"""
The H8 Emulator module.
"""

import struct

import emu
import envi
from envi.archs.h8 import H8Module
from envi.archs.h8.regs import *

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

        self.mode = CPUSTATE_RESET
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

    def processInterrupt_2140(self, intval=0):
        '''
        interrupt processing done according to H8/300 standards.  subclass and modify this function 
        if the desired behavior differs.
        supports: advanced and normal modes
        '''
        print("Interrupt Handler: 0x%x" % intval)

        addr = 0

        if self.advanced:
            if intval != 0:
                val = (self.getRegister(REG_CCR) << 24) | self.getRegister(REG_CCR)
                self.doPush(val, 4)

                addr = (intval * 4) + 0xc

            isrAddr = self.readMemortPtr(addr)
        else:
            if intval != 0:
                val = self.getRegister(REG_CCR)
                val |= (val << 8)
                self.doPush(val, 2)
                self.doPush(self.getProgramCounter())

                addr = (intval * 2) + 6
            
            isrAddr = self.readMemoryPtr(addr)

        return isrAddr

    def processInterrupt(self, intval=0):
        '''
        interrupt processing done according to H8/300 standards.  subclass and modify this function 
        if the desired behavior differs.
        supports: advanced and normal modes
        '''
        print("Interrupt Handler: 0x%x" % intval)

        addr = 0

        if self.advanced:
            if intval != 0:
                self.doPush(self.getRegister(REG_CCR))
                self.doPush(self.getRegister(REG_CCR))
                self.doPush(self.getProgramCounter())

                addr = (intval * 4) + 0xa

            isrAddr = self.readMemortPtr(addr)
        else:
            if intval != 0:
                self.doPush(self.getRegister(REG_CCR))
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
        print >>sys.stderr,"executed instruction, returned: %s"%x

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
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        return self.intSubBase(src1, src2)

    def intSubBase(self, src1, src2):
        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.


        ssize = op.opers[0].tsize
        dsize = op.opers[1].tsize

        usrc = e_bits.unsigned(src1, ssize)
        udst = e_bits.unsigned(src2, dsize)

        ssrc = e_bits.signed(src1, ssize)
        sdst = e_bits.signed(src2, dsize)

        ures = udst - usrc
        sres = sdst - ssrc

        self.setFlag(CCR_H, e_bits.is_signed_half_carry(ures, dsize))
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
            self.setOperValue(op, 0, None)
            return

        res = src1 & src2

        return res

    def i_and(self, op):
        res = self.logicalAnd(op)
        self.setOperValue(op, 1, res)
       
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
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

        self.setFlags(CCR_C, val)

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
        pc = self.getProgramRegister() + disp
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
        start_address = self.getOperValue(op,0)
        reglist = self.getOperValue(op,1)

        addr = start_address
        for reg in reglist:
            val = self.getRegister(reg)

    def i_ldm(self, op):
        start_address = self.getOperValue(op,0)
        reglist = self.getOperValue(op,1)

        addr = start_address
        for reg in reglist:
            regval = self.readMemValue(addr, 4)
            self.setRegister(reg, regval)

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
        if op.opers[0].reg == REG_PC:
            return val

    def integerAddition(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        #FIXME PDE and flags
        if src == None:
            self.undefFlags()
            self.setOperValue(op, 0, None)
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

        self.setOperValue(op, 0, ures)

        # FIXME: test and validate
        self.setFlag(CCR_H, e_bits.is_signed_half_carry(sres, dsize, sdst))
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, dsize))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, dsize))

    def i_adds(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        self.setOperValue(op, 0, ures)

    def i_addx(self, op):
        (ssize, dsize, sres, ures, sdst, udst) = self.integerAddition(op)

        C = self.getFlag(CCR_C)
        sres += C
        ures += C

        self.setOperValue(op, 0, ures)

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

        addval = daa_add.get(C, H, upop, loop)
        ures = addval + oper

        self.setOperValue(op, 0, ures)

        self.setFlag(CCR_N, e_bits.is_signed(ures, 1))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, 1))

    def i_das(self, op):
        pass
    def i_dec(self, op):
        pass

    def i_jmp(self, op):
        return self.getOperValue(op, 0)

    def i_sub(self, op):
        # Src op gets sign extended to dst
        #FIXME account for same operand with zero result for PDE
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        Sflag = op.iflags & IF_CCR_S

        if src1 == None or src2 == None:
            self.undefFlags()
            return None

        res = self.intSubBase(src1, src2)
        self.setOperValue(op, 0, res)

    def i_xor(self, op):
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

        self.setFlag(CCR_C, e_bits.is_unsigned_carry(ures, 4))
        self.setFlag(CCR_Z, not ures)
        self.setFlag(CCR_N, e_bits.is_signed(ures, 4))
        self.setFlag(CCR_V, e_bits.is_signed_overflow(sres, 4))

    def i_nop(self, op):
        pass
    '''
    def i_divxu(self, op):
        pass
    def i_eepmov(self, op):
        pass
    def i_inc(self, op):
        pass
    def i_ldc(self, op):
        pass
    def i_movfpe(self, op):
        pass
    def i_movtpe(self, op):
        pass
    def i_mulxu(self, op):
        pass
    def i_neg(self, op):
        pass
    def i_not(self, op):
        pass
    def i_or(self, op):
        pass
    def i_orc(self, op):
        pass
    def i_pop(self, op):
        pass
    def i_push(self, op):
        pass
    def i_rotl(self, op):
        pass
    def i_rotr(self, op):
        pass
    def i_rotxl(self, op):
        pass
    def i_rotxr(self, op):
        pass
    def i_rte(self, op):
        pass
    def i_rts(self, op):
        pass
    def i_shal(self, op):
        pass
    def i_shar(self, op):
        pass
    def i_shll(self, op):
        pass
    def i_shlr(self, op):
        pass
    def i_sleep(self, op):
        pass
    def i_str(self, op):
        pass
    def i_subs(self, op):
        pass
    def i_subx(self, op):
        pass
    def i_xorc(self, op):
        pass
    '''

bcd_add = {}
for x in range(0xa):
    for y in range(0xa):
        bcd_add[(0,0,(x,y))] = 0

    for y in range(4):
        bcd_add[(0,1,(x,y))] = 0x6

for x in range(9):
    for y in range(0xa, 0x10):
        bcd_add[(0,0,(x,y))] = 0x6

for x in range(0xa, 0x10):
    for y in range(0xa):
        bcd_add[(0,0,(x,y))] = 0x60

    for y in range(4):
        bcd_add[(0,1,(x,y))] = 0x66

for x in range(9, 0x10):
    for y in range(0xa, 0x10):
        bcd_add[(0,0,(x,y))] = 0x66

for x in range(3):
    for y in range(0xa):
        bcd_add[(1,0,(x,y))] = 0x60

    for y in range(0xa, 0x10):
        bcd_add[(1,0,(x,y))] = 0x66

for x in range(4):
    for y in range(4):
        bcd_add[(1,1,(x,y))] = 0x66

