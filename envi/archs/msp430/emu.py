import struct

import envi
import envi.bits as e_bits
import envi.archs.msp430 as e_msp430
import envi.archs.msp430.regs as e_msp430regs

from const import *

class Msp430Call(envi.CallingConvention):
    #arg_def = [(CC_STACK_INF, 4),]
    #retaddr_def = (CC_STACK, 0)
    #retval_def = (CC_REG, REG_EAX)
    flags = CC_CALLEE_CLEANUP
    align = 2
    pad = 0

msp430call = Msp430Call()

class Msp430Emulator(e_msp430regs.Msp430RegisterContext, envi.Emulator):

    def __init__(self, regarray=None):
        self.archmod = e_msp430.Msp430Module()

        envi.Emulator.__init__(self, self.archmod)
        e_msp430regs.Msp430RegisterContext.__init__(self)

        self._emu_segments = [ (0, 0xffff), ]
        self.addCallingConvention('msp430call', msp430call)

    def getArchModule(self):
        return self.archmod

    def makeOpcode(self, pc):
        bytes = self.readMemory(pc,6)
        return self.arch.makeOpcode(bytes)

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)
        # msp430 does not have prefixes....for now, I guess
        #if op.prefixes & PREFIX_REP:
            #x = self.doRepPrefix(meth, op)
        #else:
            #x = meth(op)
        x = meth(op)
        if x == None:
            pc = self.getProgramCounter()
            x = pc+ len(op)
        self.setProgramCounter(x)

    def readMemValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        #FIXME change this (and all uses of it) to passing in format...
        if len(bytes) != size:
            raise Exception("Read Gave Wrong Length")
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
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        if size == 1:
            return struct.unpack("b", bytes)[0]
        elif size == 2:
            return struct.unpack("<h", bytes)[0]
        elif size == 4:
            return struct.unpack("<l", bytes)[0]

    def setFlag(self, which, state):
        flags = self.getRegister(REG_SR)
        if flags ==  None:
            flags = 0

        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(REG_SR, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_SR)
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & which)

    # Conditions
    def cond_ne(self):
        return self.getFlag(REG_SR_Z) == 0

    def cond_e(self):
        return self.getFlag(REG_SR_Z) == 1

    def cond_nc(self):
        return self.getFlag(REG_SR_C) == 0

    def cond_c(self):
        return self.getFlag(REG_SR_C) == 1

    def cond_n(self):
        return self.getFlag(REG_SR_N) == 0

    def cond_ge(self):
        return self.getFlag(REG_SR_Z) == 0 and self.getFlag(REG_SR_N) == 0

    def cond_l(self):
        return self.getFlag(REG_SR_Z) == 0 and self.getFlag(REG_SR_N) == 1

    def relJump(self, op):
        return  self.getOperValue(op, 0)

    def doPush(self, val):
        sp = self.getRegister(REG_SP)
        sp -= 2
        self.writeMemValue(sp, val, 2)
        self.setRegister(REG_SP, sp)

    def doPop(self):
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, 2)
        self.setRegister(REG_SP, esp+2)
        return val

    # Instruction Helpers
    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """

        src = self.getOperValue(op,0)
        dst = self.getOperValue(op,1)

        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.
        if op.iflags & IF_BYTE:
            dsize = BYTE
            ssize = BYTE
        else:
            dsize = WORD
            ssize = WORD
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        return self.intSubBase(src, dst, ssize, dsize)

    def intSubBase(self, src, dst, ssize, dsize):

        usrc = e_bits.unsigned(src, ssize)
        udst = e_bits.unsigned(dst, dsize)

        ssrc = e_bits.signed(src, ssize)
        sdst = e_bits.signed(dst, dsize)

        ures = udst - usrc
        sres = sdst - ssrc

        #print "dsize/ssize: %d %d" % (dsize, ssize)
        #print "unsigned: %d %d %d" % (usrc, udst, ures)
        #print "signed: %d %d %d" % (ssrc, sdst, sres)

        """
        http://cnx.org/content/m23497/latest/
        Bit         Description
        8   V   Overflow bit.V = 1 -> Result of an arithmetic operation overflows the signed-variable range.
        2   N   Negative flag.N = 1 -> result of a byte or word operation is negative.
        1   Z   Zero flag.Z = 1 -> result of a byte or word operation is 0.
        0   C   Carry flag.C = 1 -> result of a byte or word operation produced a carry.

        REG_SR_C        = 1 << 0  # Carry bit
        REG_SR_Z         = 1 << 1
        REG_SR_N         = 1 << 2
        REG_SR_V         = 1 << 8 
        """

        #print "ures: %x   udst: %x   usrc: %x"% (ures, udst, usrc)
        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(sres, dsize))
        self.setFlag(REG_SR_Z, not sres)
        self.setFlag(REG_SR_N, sres < 0)
        #self.setFlag(REG_SR_C, e_bits.is_aux_carry(usrc, udst))
        self.setFlag(REG_SR_C, e_bits.is_unsigned_carry(ures, dsize))

        return ures

    # Instructions
    def i_cmp(self, op):
        self.integerSubtraction(op)

    def i_mov(self, op):
        val = self.getOperValue(op, 0)
        self.setOperValue(op, 1, val)

    def i_br(self, op):
        pc = self.getOperValue(op, 0)
        return pc

    def i_ret(self, op):
        pc = self.doPop()
        return pc

    def i_reti(self, op):
        sr = self.doPop()
        self.setRegister(REG_SR,sr)
        pc = self.doPop()
        return pc
        
    def i_call(self, op):
        pc = self.getRegister(REG_PC)
        self.doPush(pc)

        newpc = self.getOperValue(op, 0)
        return newpc

    def i_inc(self, op):
        if op.iflags & IF_BYTE:
            size = BYTE
        size = WORD
        #size = op.opers[0].tsize
        val = self.getOperValue(op, 0)

        sval = e_bits.signed(val, size)
        sval += 1

        self.setOperValue(op, 0, sval)

        # Another arithmetic op where doing signed and unsigned is easier ;)

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(sval, size))
        self.setFlag(REG_SR_Z, not sval)
        self.setFlag(REG_SR_N, sval < 0)
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(val, 1))


    # Jumps
    def i_jmp(self, op):
        return self.relJump(op)

    # We include all the possible Jcc names just in case somebody
    # gets hinkey with the disassembler.
    def i_jne(self, op):
        if self.cond_ne():   return self.relJump(op)
    i_jnz = i_jne
    def i_jeq(self, op):
        if self.cond_e():    return self.relJump(op)
    i_jz = i_jeq
    def i_jnc(self, op):
        if self.cond_nc():   return self.relJump(op)
    i_jlo = i_jnc
    def i_jc(self, op):
        if self.cond_c():    return self.relJump(op)
    i_jhs = i_jc
    def i_jn(self, op):
        if self.cond_n():    return self.relJump(op)
    def i_jge(self, op):
        if self.cond_ge():   return self.relJump(op)
    def i_jl(self, op):
        if self.cond_l():    return self.relJump(op)

    def i_sub(self, op):
        x = self.integerSubtraction(op)
        if x != None:
            self.setOperValue(op, 0, x)

    def i_bit(self, op):
        bit = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        val = dst & bit
        size = 2
        if op.iflags & IF_BYTE:
            size = 1

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(val, size))
        self.setFlag(REG_SR_Z, not val)
        self.setFlag(REG_SR_N, val < 0)
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(val, 1))


    def i_bis(self, op):
        bit = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)

        dst |= bit
        self.setOperValue(op, 1, dst)

    def i_pop(self, op):
        val = self.doPop()
        self.setOperValue(op, 0, val)

    def i_push(self, op):
        val = self.getOperValue(op, 0)
        self.doPush(val)
    
    def i_and(self, op):
        src = self.getOperValue(op, 0)
        dst = self.getOperValue(op, 1)
        uval = dst&src

        self.setOperValue(op, 1, uval)
        osize = op.opers[1].tsize

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(uval, osize))
        self.setFlag(REG_SR_Z, not uval)
        self.setFlag(REG_SR_N, uval > e_bits.s_maxes[osize])
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(uval, 1))

    def i_tst(self, op):
        dsize = 2
        if op.iflags & IF_BYTE:
            dsize = 1
        dst = self.getOperValue(op, 0)
        self.intSubBase(0, dst, dsize, dsize)
        
    def i_rra(self, op):
        oper = self.getOperValue(op, 0)
        osize = op.opers[0].tsize   # tsize needs to be correct!
        print "op: %s   tsize: %s" % (op, osize)

        shift = (osize*8)-1
        uval = ((oper&1)<<shift  | oper>>1)
        self.setOperValue(op, 0, uval)

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(uval, osize))
        self.setFlag(REG_SR_Z, not uval)
        self.setFlag(REG_SR_N, uval > e_bits.s_maxes[osize])
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(uval, 1))

    def i_rrc(self, op):
        oper = self.getOperValue(op, 0)
        osize = op.opers[0].tsize   # tsize needs to be correct!
        print "op: %s   tsize: %s" % (op, osize)
        c = self.getFlag(REG_SR_C)

        self.setFlag(REG_SR_C, oper&1)

        shift = (osize*8)-1
        uval = (c<<shift  | oper>>1)
        self.setOperValue(op, 0, uval)

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(uval, osize))
        self.setFlag(REG_SR_Z, not uval)
        self.setFlag(REG_SR_N, uval > e_bits.s_maxes[osize])
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(uval, 1))

    def i_sxt(self, op):
        oper = self.getOperValue(op, 0)
        osize = 1 # must be for msp430 to sign extend

        smax = e_bits.s_maxes[osize]
        umax = e_bits.u_maxes[2]
        if oper > smax:
            ubits = smax ^ (umax-1)
            oper |= ubits

        self.setOperValue(op, 0, oper)

        self.setFlag(REG_SR_V, e_bits.is_signed_overflow(oper, osize))
        self.setFlag(REG_SR_Z, not oper)
        self.setFlag(REG_SR_N, oper > e_bits.s_maxes[osize])
        self.setFlag(REG_SR_C, e_bits.is_aux_carry(oper, 1))

    def i_dec(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        ures = self.intSubBase(1, val, tsize, tsize)

        self.setOperValue(op, 0, ures)

    def i_decd(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        ures = self.intSubBase(2, val, tsize, tsize)
        #print val, ures, tsize

        self.setOperValue(op, 0, ures)

    def i_inc(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        ures = self.intSubBase(-1, val, tsize, tsize)

        self.setOperValue(op, 0, ures)

    def i_incd(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        ures = self.intSubBase(-2, val, tsize, tsize)

        self.setOperValue(op, 0, ures)

