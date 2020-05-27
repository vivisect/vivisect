"""
Home for the i386 emulation code.
"""
import struct

import envi
from envi.const import *
import envi.bits as e_bits
import envi.memory as e_mem

from envi.archs.i386.regs import *
from envi.archs.i386.disasm import *
from envi.archs.i386 import i386Module

def shiftMask(val, size):
    if size == 1:
        return (val & 0x1f) % 9
    elif size == 2:
        return (val & 0x1f) % 17
    elif size == 4:
        return val & 0x1f
    elif size == 8:
        return val & 0x3f
    else:
        raise Exception("shiftMask is broke in envi/intel.py")

# The indexes for the list of segments in the emulator
SEG_CS = 0
SEG_DS = 1
SEG_ES = 2
SEG_FS = 3
SEG_GS = 4
SEG_SS = 5

# The general purpose register indexes
# (for use in _emu_setGpReg / _emu_getGpReg)
# NOTE: These *must* stay in sync with i386regs first row.
GPR_A  = 0
GPR_C  = 1
GPR_D  = 2
GPR_B  = 3
GPR_SP = 4
GPR_BP = 5
GPR_SI = 6
GPR_DI = 7

class StdCall(envi.CallingConvention):
    arg_def = [(CC_STACK_INF, 4),]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_EAX)
    flags = CC_CALLEE_CLEANUP
    align = 4
    pad = 0

class Cdecl(StdCall):
    flags = CC_CALLER_CLEANUP

class ThisCall(envi.CallingConvention):
    arg_def = [(CC_REG, REG_ECX), (CC_STACK_INF, 4),]
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_EAX)
    flags = CC_CALLEE_CLEANUP
    align = 4
    pad = 0

class MsFastCall(ThisCall):
    arg_def = [(CC_REG, REG_ECX), (CC_REG, REG_EDX), (CC_STACK_INF, 4)]

class BFastCall(ThisCall):
    arg_def = [(CC_REG, REG_EAX), (CC_REG, REG_EDX), (CC_REG, REG_ECX),
                (CC_STACK_INF, 4)]

stdcall = StdCall()
thiscall = ThisCall()
cdecl = Cdecl()
msfastcall = MsFastCall()
bfastcall = BFastCall()

class IntelEmulator(i386RegisterContext, envi.Emulator):

    flagidx = REG_EFLAGS
    accumreg = { 1:REG_AL, 2:REG_AX, 4:REG_EAX }

    def __init__(self, archmod=None):
        # Set ourself up as an arch module *and* register context
        #i386Module.__init__(self)
        if archmod == None:
            archmod = i386Module()

        envi.Emulator.__init__(self, archmod=archmod)
        self.initEmuOpt('i386:reponce',False,'Set to True to short circuit rep prefix')

        for i in xrange(6):
            self.setSegmentInfo(i, 0, 0xffffffff)

        i386RegisterContext.__init__(self)

        # Add our known calling conventions
        self.addCallingConvention('stdcall', stdcall)
        self.addCallingConvention('thiscall', thiscall)
        self.addCallingConvention('cdecl', cdecl)
        self.addCallingConvention('msfastcall', msfastcall)
        self.addCallingConvention('bfastcall', bfastcall)

    def getSegmentIndex(self, op):
        # FIXME this needs to account for push/pop/etc
        if op.prefixes == 0:
            return SEG_DS
        if op.prefixes & PREFIX_ES:
            return SEG_ES
        elif op.prefixes & PREFIX_CS:
            return SEG_CS
        elif op.prefixes & PREFIX_SS:
            return SEG_SS
        elif op.prefixes & PREFIX_DS:
            return SEG_DS
        elif op.prefixes & PREFIX_FS:
            return SEG_FS
        elif op.prefixes & PREFIX_GS:
            return SEG_GS
        return SEG_DS

    def setFlag(self, which, state):
        flags = self.getRegister(self.flagidx)
        if state:
            flags |= which
        else:
            flags &= ~which
        self.setRegister(self.flagidx, flags)

    def getFlag(self, which):
        flags = self.getRegister(self.flagidx)
        return bool(flags & which)

    def readMemValue(self, addr, size):
        bytes = self.readMemory(addr, size)
        if bytes == None:
            return None
        #FIXME change this (and all uses of it) to passing in format...
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
        elif size == 16:
            nums = struct.unpack("<QQ", bytes)
            return nums[0] | (nums[1] << 64)
        elif size == 32:
            nums = struct.unpack("<QQQQ", bytes)
            return nums[0] | (nums[1] << 64) | (nums[2] << 128) | (nums[3] << 192)

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
        elif size == 16:
            mask = 0xffffffffffffffff
            nums = (value & mask, value >> 64)
            bytes = struct.pack("<QQ", *nums)
        elif size == 32:
            mask = 0xffffffffffffffff
            nums = (value & mask, (value >> 64)&mask, (value >> 128)&mask, (value >> 192)&mask)
            bytes = struct.pack("<QQQQ", *nums)
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

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        if op.va != None:
            self.setProgramCounter(op.va)

        meth = self.op_methods.get(op.mnem, None)
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)

        newpc = meth(op)
        if newpc != None:
            self.setProgramCounter(newpc)
            return

        if op.prefixes & PREFIX_REP:

            ecx = self.getRegister(REG_ECX) - 1
            self.setRegister(REG_ECX, ecx)

            if self.getEmuOpt('i386:reponce'):
                ecx = 0
                self.setRegister(REG_ECX,0)

            if ecx != 0:
                self.setProgramCounter(op.va)
                return

        pc = self.getProgramCounter()
        newpc = pc+op.size
        self.setProgramCounter(newpc)

    ###### Conditional Callbacks #####

    # NOTE: for ease of validation, these are in the same order as the Jcc
    # page in the intel manual.  However, duplicate conditions (be/na) are
    # reduced to their earliest (in the manual) form.

    def cond_a(self):
        return self.getFlag(EFLAGS_CF) == 0 and self.getFlag(EFLAGS_ZF) == 0

    def cond_ae(self):
        return self.getFlag(EFLAGS_CF) == 0

    def cond_b(self):
        return self.getFlag(EFLAGS_CF) == 1

    def cond_be(self):
        return self.getFlag(EFLAGS_CF) == 1 or self.getFlag(EFLAGS_ZF) == 1

    def cond_c(self):
        return self.getFlag(EFLAGS_CF) == 1

    def cond_ecxz(self):
        return self.getRegister(REG_ECX) == 0

    def cond_e(self):
        return self.getFlag(EFLAGS_ZF) == 1

    def cond_g(self):
        return self.getFlag(EFLAGS_ZF) == 0 and (self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF))

    def cond_ge(self):
        return self.getFlag(EFLAGS_SF) == self.getFlag(EFLAGS_OF)

    def cond_l(self):
        return self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF)

    def cond_le(self):
        return (self.getFlag(EFLAGS_SF) != self.getFlag(EFLAGS_OF) or
                (self.getFlag(EFLAGS_ZF) == 1))

    # Some duplicates
    cond_na = cond_be
    cond_nae = cond_b
    cond_nb = cond_ae
    cond_nbe = cond_a
    cond_nc = cond_ae

    def cond_ne(self):
        return self.getFlag(EFLAGS_ZF) == 0

    # A few more
    cond_ng = cond_le
    cond_nge = cond_l
    cond_nl = cond_ge
    cond_nle = cond_g

    def cond_no(self):
        return self.getFlag(EFLAGS_OF) == 0

    def cond_np(self):
        return self.getFlag(EFLAGS_PF) == 0

    def cond_ns(self):
        return self.getFlag(EFLAGS_SF) == 0

    cond_nz = cond_ne

    def cond_o(self):
        return self.getFlag(EFLAGS_OF) == 1

    def cond_p(self):
        return self.getFlag(EFLAGS_PF) == 1

    cond_pe = cond_p
    cond_po = cond_np

    def cond_s(self):
        return self.getFlag(EFLAGS_SF) == 1

    cond_z = cond_e

    # FROM OTHER INSTRUCTIONS
    cond_nc = cond_ae
    cond_nl = cond_ge

    ###### End Conditional Callbacks #####

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

    def integerSubtraction(self, op):
        """
        Do the core of integer subtraction but only *return* the
        resulting value rather than assigning it.
        (allows cmp and sub to use the same code)
        """
        # Src op gets sign extended to dst
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        # So we can either do a BUNCH of crazyness with xor and shifting to
        # get the necessary flags here, *or* we can just do both a signed and
        # unsigned sub and use the results.
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
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

        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry_sub(usrc, udst))
        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ures, dsize))
        self.setFlag(EFLAGS_ZF, not sres)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ures))

        return ures

    def logicalAnd(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        # sign-extend an immediate if needed
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        # Make sure everybody's on the same bit page.
        dst = e_bits.unsigned(dst, dsize)
        src = e_bits.unsigned(src, ssize)

        res = src & dst

        self.setFlag(EFLAGS_AF, 0) # AF is undefined, but it seems like it is zeroed
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        return res

    def doRepPrefix(self, meth, op):
        #FIXME check for opcode family valid to rep
        ret = None
        ecx = self.getRegister(REG_ECX)
        while ecx != 0:
            ret = meth(op)
            ecx -= 1
        self.setRegister(REG_ECX, 0)
        return ret

    def doRepzPrefix(self, meth, op):
        pass

    # Beginning of Instruction methods

    def i_adc(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        cf = 0
        if self.getFlag(EFLAGS_CF):
            cf = 1

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        sdst = e_bits.signed(dst, dsize)
        ssrc = e_bits.signed(src, ssize)

        if (isinstance(op.opers[1], i386ImmOper) and
            ssize < dsize):
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        #FIXME perhaps unify the add/adc flags/arith code
        res = dst + src + cf
        sres = sdst + ssrc + cf

        tsize = op.opers[0].tsize

        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(res, tsize))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, tsize))
        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))

        self.setOperValue(op, 0, res)

    def i_add(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        if dsize > ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        udst = e_bits.unsigned(dst, dsize)
        usrc = e_bits.unsigned(src, ssize)
        sdst = e_bits.signed(dst, dsize)
        ssrc = e_bits.signed(src, ssize)

        ures = udst + usrc
        sres = sdst + ssrc

        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ures))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
        self.setFlag(EFLAGS_ZF, not ures)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ures, dsize))
        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))

        self.setOperValue(op, 0, ures)

    def i_and(self, op):
        #FIXME 24 and 25 opcodes should *not* get sign-extended.
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)

    def i_arpl(self, op):
        v1 = self.getOperValue(op, 0)
        v2 = self.getOperValue(op, 1)

        # Mask off the rpl
        r1 = v1 & 3
        r2 = v2 & 3

        if r1 < r2: # If dest rpl < src rpl
            self.setFlag(EFLAGS_ZF, True)
            # Bump 2 bits off the bottom and add r2
            self.setOperValue(op, 0, ((v1 >> 2) << 2) | r2)
        else:
            self.setFlag(EFLAGS_ZF, False)

    def i_bswap(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        self.setOperValue(op, 0, e_bits.byteswap(val, tsize))

    def i_bsr(self, op):
        val = self.getOperValue(op, 0)

        if val == 0:
            # If the src is 0, set ZF and get out
            self.setFlag(EFLAGS_ZF, True)
            return

        self.setFlag(EFLAGS_ZF, False)

        tsize = op.opers[0].tsize
        rmax = (tsize*8) - 1
        while rmax >= 0:
            if val & (1<<rmax):
                self.setOperValue(op, 1, rmax)
                return
            rmax -= 1

    def doBitTest(self, op):
        val = self.getOperValue(op, 0)
        shift = self.getOperValue(op, 1)
        mask = 1 << shift
        self.setFlag(EFLAGS_CF, val & mask)
        # Return the source and mask for btc/btr
        return val,mask

    def i_bt(self, op):
        self.doBitTest(op)

    def i_btc(self, op):
        # bit test and toggle bit in source
        val, mask = self.doBitTest(op)
        self.setOperValue(op, 0, val ^ mask)

    def i_btr(self, op):
        # bit test (and clear in the source)
        val, mask = self.doBitTest(op)
        mask = e_bits.unsigned(~val, op.opers[0].tsize)
        self.setOperValue(op, 0, val & mask)

    def i_bts(self, op):
        # bit test (and set in the source)
        val, mask = self.doBitTest(op)
        self.setOperValue(op, 0, val | mask)

    def i_call(self, op):
        eip = self.getProgramCounter()
        saved = eip + op.size
        self.doPush(saved)

        return self.getOperValue(op, 0)

    def i_clc(self, op):
        self.setFlag(EFLAGS_CF, False)

    def i_cld(self, op):
        self.setFlag(EFLAGS_DF, False)

    def i_cli(self, op):
        self.setFlag(EFLAGS_IF, False)

    def i_cmc(self, op):
        # set the CF flag to its complement
        val = self.getFlag(EFLAGS_CF)
        self.setFlag(EFLAGS_CF, ~val)

    # We include all the possible CMOVcc names just in case somebody
    # gets hinkey with the disassembler.
    def i_cmova(self, op):
        if self.cond_a():    return self.i_mov(op)
    def i_cmovae(self, op):
        if self.cond_ae():   return self.i_mov(op)
    def i_cmovb(self, op):
        if self.cond_b():    return self.i_mov(op)
    def i_cmovbe(self, op):
        if self.cond_be():   return self.i_mov(op)
    def i_cmovc(self, op):
        if self.cond_c():    return self.i_mov(op)
    def i_cmovecxz(self, op):
        if self.cond_ecxz(): return self.i_mov(op)
    def i_cmove(self, op):
        if self.cond_e():    return self.i_mov(op)
    def i_cmovg(self, op):
        if self.cond_g():    return self.i_mov(op)
    def i_cmovge(self, op):
        if self.cond_ge():   return self.i_mov(op)
    def i_cmovl(self, op):
        if self.cond_l():    return self.i_mov(op)
    def i_cmovle(self, op):
        if self.cond_le():   return self.i_mov(op)
    i_cmovna = i_cmovbe
    i_cmovnae = i_cmovb
    i_cmovnb = i_cmovae
    i_cmovnbe = i_cmova
    i_cmovnc = i_cmovae
    def i_cmovne(self, op):
        if self.cond_ne():   return self.i_mov(op)
    i_cmovng = i_cmovle
    i_cmovnge = i_cmovl
    i_cmovnl = i_cmovge
    i_cmovnle = i_cmovg
    def i_cmovno(self, op):
        if self.cond_no():   return self.i_mov(op)
    def i_cmovnp(self, op):
        if self.cond_np():   return self.i_mov(op)
    def i_cmovns(self, op):
        if self.cond_ns():   return self.i_mov(op)
    i_cmovnz = i_cmovne
    def i_cmovo(self, op):
        if self.cond_o():    return self.i_mov(op)
    def i_cmovp(self, op):
        if self.cond_p():    return self.i_mov(op)
    i_cmovpe = i_cmovp
    i_cmovpo = i_cmovnp
    def i_cmovs(self, op):
        if self.cond_s():    return self.i_mov(op)
    i_cmovz = i_cmove

    def i_cmp(self, op):
        self.integerSubtraction(op)

    def doCmps(self, width):
        esi = self.getRegister(REG_ESI)
        edi = self.getRegister(REG_EDI)


        # FIXME che
        sval = self.readMemValue(esi, width)
        dval = self.readMemValue(edi, width)

        self.intSubBase(sval, dval, width, width)

        if self.getFlag(EFLAGS_ZF):
            if self.getFlag(EFLAGS_DF): # decrement
                esi -= width
                edi -= width
            else:
                esi += width
                edi += width
            self.setRegister(REG_ESI, esi)
            self.setRegister(REG_EDI, edi)

    def i_cmpsb(self, op):
        self.doCmps(1)

    def i_cmpsd(self, op):
        """
        Compare the dword pointed at by ds:esi to ds:edi.
        (if equal, update esi/edi by one acording to DF)
        """
        width = 4
        if op.prefixes & PREFIX_OP_SIZE:
            width = 2

        self.doCmps(width)

    def i_cmpxchg(self, op):
        tsize = op.opers[0].tsize
        areg = self.accumreg.get(op.opers[0].tsize)

        aval = self.getRegister(areg)
        tval = self.getOperValue(op, 0)
        vval = self.getOperValue(op, 1)

        self.intSubBase( aval, tval, tsize, tsize)

        if aval == tval:
            self.setOperValue(op, 0, vval)
        else:
            self.setRegister(areg, tval)

    def twoRegCompound(self, topreg, botreg, size):
        """
        Build a compound value where the value of the top reg is shifted and
        or'd with the value of the bot reg ( assuming they are size
        bytes in length).  The return is size * 2 wide (and unsigned).
        """
        top = e_bits.unsigned(self.getRegister(topreg), size)
        bot = e_bits.unsigned(self.getRegister(botreg), size)

        return ((top << (size *8)) | bot)

    def regsFromCompound(self, val, size):
        top = e_bits.unsigned(val >> (size * 8), size)
        bot = e_bits.unsigned(val, size)
        return (top, bot)

    def i_cmpxch8b(self, op):
        size = 4
        dsize = 8
        if op.prefixes & PREFIX_OP_SIZE:
            size = 2
            dsize = 4

        bignum = self.twoRegCompound(REG_EDX, REG_EAX, size)
        testnum = self.getOperValue(op, 0)
        if bignum == testnum:
            self.setFlag(EFLAGS_ZF, 1)
            resval = self.twoRegCompound(REG_ECX, REG_EBX, size)
            self.setOperValue(op, 0, resval)
        else:
            self.setFlag(EFLAGS_ZF, 0)
            edx,eax = self.regsFromCompound(testnum, dsize)
            self.setRegister(REG_EDX, edx)
            self.setRegister(REG_EAX, eax)

    def i_cdq(self, op):
        return self.i_cwd(op)

    def i_cpuid(self, op):
        eax = self.getRegister(REG_EAX)
        self.setRegister(REG_EAX, 0)
        self.setRegister(REG_EBX, 0)
        self.setRegister(REG_ECX, 0)
        self.setRegister(REG_EDX, 0)

    def i_cwd(self, op):
        #FIXME handle 16 bit variant
        eax = self.getRegister(REG_EAX)

        if e_bits.is_signed(eax, 4):
            self.setRegister(REG_EDX, 0xffffffff)
        else:
            self.setRegister(REG_EDX, 0)

    def i_cwde(self, op):
        # FIXME "cbw" 16 bit mode
        ax = self.getRegister(REG_AX)
        eax = e_bits.sign_extend(ax,2,4)
        self.setRegister(REG_EAX,eax)

    def i_dec(self, op):
        val = self.getOperValue(op, 0)
        uval = e_bits.unsigned(val, op.opers[0].tsize)
        if val == None:
            self.undefFlags()
            return
        val -= 1
        self.setOperValue(op, 0, val)
        #FIXME change over to integer subtraction

        self.setFlag(EFLAGS_OF, 0) #FIXME OF
        self.setFlag(EFLAGS_SF, e_bits.is_signed(val, op.opers[0].tsize))
        self.setFlag(EFLAGS_ZF, not val)
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry_sub(1, uval))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(val))

    def i_div(self, op):

        #FIXME this is probably broke
        oper = op.opers[0]
        val = self.getOperValue(op, 1)
        if val == 0: raise envi.DivideByZero(self)

        if oper.tsize == 1:
            ax = self.getRegister(REG_AX)
            quot = ax / val
            rem  = ax % val
            #if quot > 255:
                #FIXME stuff
                #print "FIXME: division exception"
            self.setRegister(REG_EAX, (quot << 8) + rem)

        elif oper.tsize == 4:
            #FIXME 16 bit over-ride
            eax = self.getRegister(REG_EAX)
            edx = self.getRegister(REG_EDX)
            tot = (edx << 32) + eax
            quot = tot / val
            rem = tot % val

            #if quot > 0xffffffff:
                #print "FIXME: division exception"

            self.setRegister(REG_EAX, quot)
            self.setRegister(REG_EDX, rem)

        elif oper.tsize == 8:
            rax = self.getRegisterByName("rax")
            rdx = self.getRegisterByName("rdx")
            tot = (rdx << 64) + rax
            quot = tot / val
            rem = tot % val

            if tot > (2**64)-1:
                raise Exception('division exception')

            self.setRegisterByName("rax", quot)
            self.setRegisterByName("rdx", rem)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_enter(self, op):
        locsize = self.getOperValue(op, 0)
        depth = self.getOperValue(op, 1)
        if depth != 0:
            raise envi.UnsupportedInstruction(self, op)

        esp = self.getRegister(REG_ESP)
        ebp = self.getRegister(REG_EBP)

        esp -= 4 # Room for the base pointer

        self.writeMemValue(esp, ebp, 4)
        self.setRegister(REG_EBP, esp)
        esp -= locsize
        self.setRegister(REG_ESP, esp)

    # FIXME a whole bunch of float instructions whose
    # processing is essentially ignored:
    def i_fldz(self, op):
        pass

    def i_fild(self, op):
        pass

    def i_fstp(self, op):
        pass

    def i_idiv(self, op):
        #FIXME this needs emulation testing!
        tsize = op.opers[0].tsize
        if tsize == 1:
            ax = self.getRegister(REG_AX)
            ax = e_bits.signed(ax, 2)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 1)
            if d == 0: raise envi.DivideByZero(self)
            q = ax / d
            r = ax % d
            res = ((r & 0xff) << 8) | (q & 0xff)
            self.setRegister(REG_AX, res)

        elif tsize == 2:
            val = self.twoRegCompound(REG_DX, REG_AX, 2)
            val = e_bits.signed(val, 4)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 2)
            if d == 0: raise envi.DivideByZero(self)
            q = val / d
            r = val % d

            self.setRegister(REG_AX, q)
            self.setRegister(REG_DX, r)

        elif tsize == 4:
            val = self.twoRegCompound(REG_EDX, REG_EAX, 4)
            val = e_bits.signed(val, 8)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 4)
            if d == 0: raise envi.DivideByZero(self)
            q = val / d
            r = val % d

            self.setRegister(REG_EAX, q)
            self.setRegister(REG_EDX, r)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_imul(self, op):
        #FIXME eflags
        # FIXME imul bugs
        ocount = len(op.opers)
        if ocount == 2:
            dst = self.getOperValue(op, 0)
            src = self.getOperValue(op, 1)
            dsize = op.opers[0].tsize
            ssize = op.opers[1].tsize

            # FIXME all these are taken care of in disasm now...
            if dsize > ssize:
                src = e_bits.sign_extend(src, ssize, dsize)
                ssize = dsize

            res = dst * src

            sof = e_bits.is_unsigned_carry(res, dsize)
            self.setFlag(EFLAGS_CF, sof)
            self.setFlag(EFLAGS_OF, sof)

            self.setOperValue(op, 0, res)

        elif ocount == 3:
            dst = self.getOperValue(op, 0)
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)

            dsize = op.opers[0].tsize
            ssize1 = op.opers[1].tsize
            ssize2 = op.opers[2].tsize

            if dsize > ssize2: # Only the last operand may be shorter imm
                src2 = e_bits.sign_extend(src2, ssize2, dsize)
                ssize2 = dsize

            res = src1 * src2

            sof = e_bits.is_unsigned_carry(res, dsize)
            self.setFlag(EFLAGS_CF, sof)
            self.setFlag(EFLAGS_OF, sof)

            self.setOperValue(op, 0, res)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_in(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_inc(self, op):
        size = op.opers[0].tsize
        val = self.getOperValue(op, 0)

        sval = e_bits.signed(val, size)
        sval += 1

        self.setOperValue(op, 0, sval)

        # Another arithmetic op where doing signed and unsigned is easier ;)

        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sval, size))
        self.setFlag(EFLAGS_SF, e_bits.is_signed(sval, size))
        self.setFlag(EFLAGS_ZF, not sval)
        self.setFlag(EFLAGS_AF, (sval & 0xf == 0))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(sval))

    def i_int(self, op):
        raise envi.UnsupportedInstruction(self, op)

    def i_int3(self, op):
        raise envi.BreakpointHit(self)

    def i_lea(self, op):
        base = self.getOperAddr(op, 1)
        self.setOperValue(op, 0, base)

    def decCounter(self):
        """
        A helper to decrement and return the counter
        """
        ecx = self.getRegister(REG_ECX)
        ecx -= 1
        self.setRegister(REG_ECX, ecx)
        return ecx

    def i_lodsb(self, op):
        esi = self.getRegister(REG_ESI)
        newal = self.readMemoryFormat(esi, "<B")[0]
        self.setRegister(REG_AL, newal)
        if not self.getFlag(EFLAGS_DF):
            esi += 1
        else:
            esi -= 1
        self.setRegister(REG_ESI, esi)
        
    def i_lodsd(self, op):
        esi = self.getRegister(REG_ESI)
        neweax = self.readMemoryFormat(esi, "<L")[0]
        #FIXME figgure out ADDR_SIZE vs OP_SIZE and which is which
        self.setRegister(REG_EAX, neweax)
        if not self.getFlag(EFLAGS_DF):
            esi += 4
        else:
            esi -= 4
        self.setRegister(REG_ESI, esi)

    def i_loop(self, op):
        if self.decCounter() != 0:
            return self.getOperValue(op, 0)

    def i_loopz(self, op):
        if self.decCounter() != 0 and self.cond_e():
            return self.getOperValue(op, 0)

    def i_loopnz(self, op):
        if self.decCounter() != 0 and self.cond_ne():
            return self.getOperValue(op, 0)

    i_loope = i_loopz
    i_loopne = i_loopnz

    def i_leave(self, op):
        ebp = self.getRegister(REG_EBP)
        self.setRegister(REG_ESP, ebp)
        self.setRegister(REG_EBP, self.doPop())

    def i_mov(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    i_movq = i_mov

    def i_movsb(self, op):
        esi = self.getRegister(REG_ESI)
        edi = self.getRegister(REG_EDI)
        bytes = self.readMemory(esi, 1)
        self.writeMemory(edi, bytes)
        if self.getFlag(EFLAGS_DF):
            self.setRegister(REG_ESI, esi-1)
            self.setRegister(REG_EDI, edi-1)
        else:
            self.setRegister(REG_ESI, esi+1)
            self.setRegister(REG_EDI, edi+1)

    def i_movsd(self, op):
        esi = self.getRegister(REG_ESI)
        edi = self.getRegister(REG_EDI)
        bytes = self.readMemory(esi, 4)
        self.writeMemory(edi, bytes)
        if self.getFlag(EFLAGS_DF):
            self.setRegister(REG_ESI, esi-4)
            self.setRegister(REG_EDI, edi-4)
        else:
            self.setRegister(REG_ESI, esi+4)
            self.setRegister(REG_EDI, edi+4)

    def i_movsx(self, op):
        osize = op.opers[1].tsize
        nsize = op.opers[0].tsize
        val = self.getOperValue(op, 1)
        val = e_bits.sign_extend(val, osize, nsize)
        self.setOperValue(op, 0, val)

    def i_movzx(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    def i_mul(self, op):
        #FIXME make sure these work right
        tsize = op.opers[0].tsize

        val = self.getOperValue(op, 0)

        # Return al/ax/eax as needed...
        a = self._emu_getGpReg(GPR_A, tsize)

        res = a * val

        if tsize == 1:
            self.setRegister(REG_AX, res)

        elif tsize == 2:
            d,a = self.regsFromCompound(res, tsize)
            self._emu_setGpReg(GPR_A, a, tsize)
            self._emu_setGpReg(GPR_D, d, tsize)

        # If the high order stuff was used, set CF/OF
        if res >> (tsize * 8):
            self.setFlag(EFLAGS_CF, True)
            self.setFlag(EFLAGS_OF, True)
        else:
            self.setFlag(EFLAGS_CF, False)
            self.setFlag(EFLAGS_OF, False)

    def _emu_setGpReg(self, reg, val, tsize):
        """
        Automagically map all general purpose register accesses
        to their tsize equiv.  Helps clean up a lot of code
        (and makes a nice place for AMD64 to hook ;) )
        """
        if tsize == 1:
            reg += 0x00080000
        elif tsize == 2:
            reg += 0x00100000
        self.setRegister(reg, value)

    def _emu_getGpReg(self, reg, tsize):
        """
        Automagically map all general purpose register accesses
        to their tsize equiv.  Helps clean up a lot of code
        (and makes a nice place for AMD64 to hook ;) )
        """
        if tsize == 1:
            reg += 0x00080000
        elif tsize == 2:
            reg += 0x00100000
        return self.getRegister(reg)

    def i_neg(self, op):
        tsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        res = 0 - val
        self.setOperValue(op, 0, res)

        self.setFlag(EFLAGS_CF, val != 0)
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, tsize))
        #FIXME how does neg cause/not cause a carry?
        self.setFlag(EFLAGS_AF, 0) # FIXME EFLAGS_AF

    def i_nop(self, op):
        pass

    def i_prefetch(self, op):
        pass

    def i_prefetchw(self, op):
        pass

    def i_not(self, op):
        val = self.getOperValue(op, 0)
        val ^= e_bits.u_maxes[op.opers[0].tsize]
        self.setOperValue(op, 0, val)

    def i_or(self, op):
        dst = self.getOperValue(op, 0)
        dsize = op.opers[0].tsize
        src = self.getOperValue(op, 1)
        ssize = op.opers[1].tsize

        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize

        res = dst | src
        self.setOperValue(op, 0, res)

        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))

    def i_pop(self, op):
        val = self.doPop()
        self.setOperValue(op, 0, val)

    def i_popad(self, op):
        #FIXME 16 bit?
        self.setRegister(REG_EDI, self.doPop())
        self.setRegister(REG_ESI, self.doPop())
        self.setRegister(REG_EBP, self.doPop())
        self.doPop() # skip one
        self.setRegister(REG_EBX, self.doPop())
        self.setRegister(REG_EDX, self.doPop())
        self.setRegister(REG_ECX, self.doPop())
        self.setRegister(REG_EAX, self.doPop())

    def i_popfd(self, op):
        eflags = self.doPop()
        self.setRegister(self.flagidx, eflags)

    def i_push(self, op):
        val = self.getOperValue(op, 0)
        if isinstance(op.opers[0], i386ImmOper):
            val = e_bits.sign_extend(val, op.opers[0].tsize, 4) #FIXME 64bit
        self.doPush(val)

    def i_pushad(self, op):
        tmp = self.getRegister(REG_ESP)
        self.doPush(self.getRegister(REG_EAX))
        self.doPush(self.getRegister(REG_ECX))
        self.doPush(self.getRegister(REG_EDX))
        self.doPush(self.getRegister(REG_EBX))
        self.doPush(tmp)
        self.doPush(self.getRegister(REG_EBP))
        self.doPush(self.getRegister(REG_ESI))
        self.doPush(self.getRegister(REG_EDI))

    def i_pushfd(self, op):
        eflags = self.getRegister(self.flagidx)
        self.doPush(eflags)

    def i_jmp(self, op):
        return self.getOperValue(op, 0)

    # We include all the possible Jcc names just in case somebody
    # gets hinkey with the disassembler.
    def i_ja(self, op):
        if self.cond_a():    return self.getOperValue(op, 0)
    def i_jae(self, op):
        if self.cond_ae():   return self.getOperValue(op, 0)
    def i_jb(self, op):
        if self.cond_b():    return self.getOperValue(op, 0)
    def i_jbe(self, op):
        if self.cond_be():   return self.getOperValue(op, 0)
    def i_jc(self, op):
        if self.cond_c():    return self.getOperValue(op, 0)
    def i_jecxz(self, op):
        if self.cond_ecxz(): return self.getOperValue(op, 0)
    def i_je(self, op):
        if self.cond_e():    return self.getOperValue(op, 0)
    def i_jg(self, op):
        if self.cond_g():    return self.getOperValue(op, 0)
    def i_jge(self, op):
        if self.cond_ge():   return self.getOperValue(op, 0)
    def i_jl(self, op):
        if self.cond_l():    return self.getOperValue(op, 0)
    def i_jle(self, op):
        if self.cond_le():   return self.getOperValue(op, 0)
    i_jna = i_jbe
    i_jnae = i_jb
    i_jnb = i_jae
    i_jnbe = i_ja
    i_jnc = i_jae
    def i_jne(self, op):
        if self.cond_ne():   return self.getOperValue(op, 0)
    i_jng = i_jle
    i_jnge = i_jl
    i_jnl = i_jge
    i_jnle = i_jg
    def i_jno(self, op):
        if self.cond_no():   return self.getOperValue(op, 0)
    def i_jnp(self, op):
        if self.cond_np():   return self.getOperValue(op, 0)
    def i_jns(self, op):
        if self.cond_ns():   return self.getOperValue(op, 0)
    i_jnz = i_jne
    def i_jo(self, op):
        if self.cond_o():    return self.getOperValue(op, 0)
    def i_jp(self, op):
        if self.cond_p():    return self.getOperValue(op, 0)
    i_jpe = i_jp
    i_jpo = i_jnp
    def i_js(self, op):
        if self.cond_s():    return self.getOperValue(op, 0)
    i_jz = i_je

    def i_rcl(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # Put that carry bit up there.
        if self.getFlag(EFLAGS_CF):
            dst = dst | (1 << (8 * dsize))

        # Add one to account for carry
        x = ((8*dsize) - src) + 1
        #FIXME is this the one that can end up negative?

        res = (dst << src) | (dst >> x)
        cf = (res >> (8*dsize)) & 1
        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        if src == 1:
            m1 = e_bits.msb(res, dsize)
            m2 = e_bits.msb(res << 1, dsize)
            self.setFlag(EFLAGS_OF, m1 ^ m2)

        self.setOperValue(op, 0, res)

    def i_rcr(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f
        # Put that carry bit up there.
        if self.getFlag(EFLAGS_CF):
            dst = dst | (1 << (8 * dsize))

        # Add one to account for carry
        x = ((8*dsize) - src) + 1

        res = (dst >> src) | (dst << x)
        cf = (res >> (8*dsize)) & 1
        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        if src == 1:
            m1 = e_bits.msb(res, dsize)
            m2 = e_bits.msb(res << 1, dsize)
            self.setFlag(EFLAGS_OF, m1 ^ m2)

        self.setOperValue(op, 0, res)

    def i_rdtsc(self, op):
        """
        Read the clock cycle counter into edx:eax
        """
        self.setRegister(REG_EDX, 0)
        self.setRegister(REG_EAX, 0x414141)

    def i_rol(self, op):
        dstSize = op.opers[0].tsize
        count = self.getOperValue(op, 1)
        tempCount = shiftMask(count, dstSize)

        if tempCount > 0: # Yeah, i know...weird. See the intel manual
            while tempCount:
                val = self.getOperValue(op, 0)
                tempCf = e_bits.msb(val, dstSize)
                self.setOperValue(op, 0, (val * 2) + tempCf)
                tempCount -= 1
            val = self.getOperValue(op, 0)
            self.setFlag(EFLAGS_CF, e_bits.lsb(val))
            if count == 1:
                val = self.getOperValue(op, 0)
                cf = self.getFlag(EFLAGS_CF)
                self.setFlag(EFLAGS_OF, e_bits.msb(val, dstSize) ^ cf)
            else:
                self.setFlag(EFLAGS_OF, False)
        
    def i_ror(self, op):
        dstSize = op.opers[0].tsize
        count = self.getOperValue(op, 1)
        tempCount = shiftMask(count, dstSize)

        if tempCount > 0: # Yeah, i know...weird. See the intel manual
            while tempCount:
                val = self.getOperValue(op, 0)
                tempCf = e_bits.lsb(val)
                self.setOperValue(op, 0, (val / 2) + (tempCf * (2 ** dstSize)))
                tempCount -= 1
            val = self.getOperValue(op, 0)
            self.setFlag(EFLAGS_CF, e_bits.msb(val, dstSize))
            if count == 1:
                val = self.getOperValue(op, 0)
                cf = self.getFlag(EFLAGS_CF)
                # FIXME: This may be broke...the manual is kinda flaky here
                self.setFlag(EFLAGS_OF, e_bits.msb(val, dstSize) ^ (e_bits.msb(val, dstSize) - 1))
            else:
                self.setFlag(EFLAGS_OF, False)

    def i_ret(self, op):
        ret = self.doPop()
        if len(op.opers):
            esp = self.getRegister(REG_ESP)
            ival = self.getOperValue(op, 0)
            self.setRegister(REG_ESP, esp+ival)
        return ret

    def i_sal(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        res = dst << src
        cf = (res >> 8*dsize) & 1

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, not e_bits.msb(res, dsize) == cf)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_sar(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        signed = e_bits.msb(dst, dsize)

        res = dst >> src
        cf = (dst >> (src-1)) & 1

        # If it was signed, we need to fill in all those bits we
        # shifted off with ones.
        if signed:
            x = (8*dsize) - src
            umax = e_bits.u_maxes[dsize]
            res |= (umax >> x) << x

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, False)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_shl(self, op):
        return self.i_sal(op)

    def i_shr(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        src = src & 0x1f

        # According to intel manual, if src == 0 eflags are not changed
        if src == 0:
            return

        res = dst >> src
        cf = (dst >> (src-1)) & 1

        res = e_bits.unsigned(res, dsize)

        self.setFlag(EFLAGS_CF, cf)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(res, dsize))
        self.setFlag(EFLAGS_ZF, not res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        if src == 1:
            self.setFlag(EFLAGS_OF, False)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setOperValue(op, 0, res)

    def i_shrd(self, op):
        dsize = op.opers[0].tsize
        bsize = dsize * 8
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        cnt = self.getOperValue(op, 2)

        cnt &= 0x1f # Reg gets masked down

        if cnt == 0:
            return

        if cnt > bsize:
            # result is "undfined"
            return

        res = dst >> cnt
        res |= src << (bsize - cnt)

        # We now have the bits masked into res, but it has become
        # wider than the original operand.

        # Ret is masked down to size
        ret = e_bits.unsigned(res, dsize)

        if cnt == 1: # Set OF on sign change
            dsign = e_bits.is_signed(dst, dsize)
            rsign = e_bits.is_signed(ret, dsize)
            self.setFlag(EFLAGS_OF, dsign != rsign)

        # set carry to last shifted bit
        self.setFlag(EFLAGS_CF, (res << bsize) & 1)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ret, dsize))
        self.setFlag(EFLAGS_ZF, not ret)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ret))

        self.setOperValue(op, 0, ret)

    def i_shld(self, op):
        dsize = op.opers[0].tsize
        bsize = dsize * 8
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        cnt = self.getOperValue(op, 2)

        cnt &= 0x1f # Reg gets masked down

        if cnt == 0:
            return

        if cnt > bsize:
            return

        res = dst << cnt
        res |= src >> (bsize - cnt)
        ret = e_bits.unsigned(res, dsize)

        if cnt == 1: # Set OF on sign change
            dsign = e_bits.is_signed(dst, dsize)
            rsign = e_bits.is_signed(ret, dsize)
            self.setFlag(EFLAGS_OF, dsign != rsign)

        # set carry to last shifted bit
        self.setFlag(EFLAGS_CF, (dst << (cnt-1)) & 1)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ret, dsize))
        self.setFlag(EFLAGS_ZF, not ret)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ret))

        self.setOperValue(op, 0, ret)

    def i_scasb(self, op):
        al = self.getRegister(REG_AL)
        edi = self.getRegister(REG_EDI)
        base,size = self._emu_segments[SEG_ES]
        memval = ord(self.readMemory(base+edi, 1))
        self.intSubBase(al, memval, 1, 1)
        if self.getFlag(EFLAGS_DF):
            edi -= 1
        else:
            edi += 1
        self.setRegister(REG_EDI, edi)

    def i_scasd(self, op):
        #FIXME probably need to handle oper prefix by hand here...
        eax = self.getRegister(REG_EAX)
        edi = self.getRegister(REG_EDI)
        base,size = self._emu_segments[SEG_ES]
        memval = struct.unpack("<L",self.readMemory(base+edi, 4))[0]
        self.intSubBase(eax, memval, 4, 4)
        if self.getFlag(EFLAGS_DF):
            edi -= 4
        else:
            edi += 4
        self.setRegister(REG_EDI, edi)

    def i_stosb(self, op):
        al = self.getRegister(REG_AL)
        edi = self.getRegister(REG_EDI)
        base,size = self._emu_segments[SEG_ES]
        self.writeMemory(base+edi, chr(al))
        if self.getFlag(EFLAGS_DF):
            edi -= 1
        else:
            edi += 1
        self.setRegister(REG_EDI, edi)

    def i_stosd(self, op):
        # FIXME REX.W makes this 64 bit...
        eax = self.getRegister(REG_EAX)
        edi = self.getRegister(REG_EDI)
        base,size = self._emu_segments[SEG_ES]
        self.writeMemory(base+edi, struct.pack("<L", eax))
        if self.getFlag(EFLAGS_DF):
            edi -= 4
        else:
            edi += 4
        self.setRegister(REG_EDI, edi)

    # We include all the possible SETcc names just in case somebody
    # gets hinkey with the disassembler.
    def i_seta(self, op):     self.setOperValue(op, 0, int(self.cond_a()))
    def i_setae(self, op):    self.setOperValue(op, 0, int(self.cond_ae()))
    def i_setb(self, op):     self.setOperValue(op, 0, int(self.cond_b()))
    def i_setbe(self, op):    self.setOperValue(op, 0, int(self.cond_be()))
    def i_setc(self, op):     self.setOperValue(op, 0, int(self.cond_c()))
    def i_setecxz(self, op):  self.setOperValue(op, 0, int(self.cond_ecxz()))
    def i_sete(self, op):     self.setOperValue(op, 0, int(self.cond_e()))
    def i_setg(self, op):     self.setOperValue(op, 0, int(self.cond_g()))
    def i_setge(self, op):    self.setOperValue(op, 0, int(self.cond_ge()))
    def i_setl(self, op):     self.setOperValue(op, 0, int(self.cond_l()))
    def i_setle(self, op):    self.setOperValue(op, 0, int(self.cond_le()))
    i_setna = i_setbe
    i_setnae = i_setb
    i_setnb = i_setae
    i_setnbe = i_seta
    i_setnc = i_setae
    def i_setne(self, op):    self.setOperValue(op, 0, int(self.cond_ne()))
    i_setng = i_setle
    i_setnge = i_setl
    i_setnl = i_setge
    i_setnle = i_setg
    def i_setno(self, op):    self.setOperValue(op, 0, int(self.cond_no()))
    def i_setnp(self, op):    self.setOperValue(op, 0, int(self.cond_np()))
    def i_setns(self, op):    self.setOperValue(op, 0, int(self.cond_ns()))
    i_setnz = i_setne
    def i_seto(self, op):     self.setOperValue(op, 0, int(self.cond_o()))
    def i_setp(self, op):     self.setOperValue(op, 0, int(self.cond_p()))
    i_setpe = i_setp
    i_setpo = i_setnp
    def i_sets(self, op):     self.setOperValue(op, 0, int(self.cond_s()))
    i_setz = i_sete

    def i_sbb(self, op):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        # Much like "integer subtraction" but we need
        # too add in the carry flag
        if src == None or dst == None:
            self.undefFlags()
            return None

        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        # Sign extend immediates where the sizes don't match
        if dsize != ssize:
            src = e_bits.sign_extend(src, ssize, dsize)
            ssize = dsize
        src += self.getFlag(EFLAGS_CF)
        res = self.intSubBase(src, dst, ssize, dsize)
        self.setOperValue(op, 0, res)

    # FIXME scas stuff goes here
    # FIXME conditional byte set goes here
    def i_stc(self, op):
        self.setFlag(EFLAGS_CF, True)

    def i_std(self, op):
        self.setFlag(EFLAGS_DF, True)

    def i_sti(self, op):
        self.setFlag(EFLAGS_IF, True)

    def i_sub(self, op):
        x = self.integerSubtraction(op)
        dsize = op.opers[0].tsize
        x = e_bits.unsigned(x, dsize)
        if x != None:
            self.setOperValue(op, 0, x)

    def i_syscall(self, op):
        # "platforms" must hook this, we just exist to "survive" it
        pass

    def i_test(self, op):
        self.logicalAnd(op)

    def i_wait(self, op):
        pass
        #print "i_wait() is a stub..."

    def i_xadd(self, op):
        val1 = self.getOperValue(op, 0)
        val2 = self.getOperValue(op, 1)
        temp = val1 + val2
        self.setOperValue(op, 1, val1)
        self.setOperValue(op, 0, temp)

    def i_xchg(self, op):
        temp = self.getOperValue(op, 0)
        self.setOperValue(op, 0, self.getOperValue(op, 1))
        self.setOperValue(op, 1, temp)

    def i_xor(self, op):
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        ret = src ^ dst

        self.setOperValue(op, 0, ret)

        self.setFlag(EFLAGS_CF, 0)
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ret, dsize))
        self.setFlag(EFLAGS_ZF, not ret)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ret))
        self.setFlag(EFLAGS_AF, False) # Undefined but actually cleared on amd64 X2

    def i_pxor(self, op):
        return self.i_xor(op)

    def i_lahf(self, op):
        self.setRegister(REG_AH, self.getRegister(REG_EFLAGS) & 0b11010101)
