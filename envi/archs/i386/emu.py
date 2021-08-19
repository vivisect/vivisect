"""
Home for the i386 emulation code.
"""
import struct
import operator

import envi
from envi.const import *
import envi.exc as e_exc
import envi.bits as e_bits

from envi.archs.i386.opconst import PREFIX_REX_W
from envi.archs.i386.regs import *
from envi.archs.i386.disasm import *
from envi.archs.i386 import i386Module


def shiftMask(val, size):
    if size == 1:
        return (val & 0x1f) % 8
    elif size == 2:
        return (val & 0x1f) % 16
    elif size == 4:
        return val & 0x1f
    elif size == 8:
        return val & 0x3f
    else:
        raise Exception("shiftMask is broke in envi/arch/i386/emu.py")

def shiftMaskRC(val, size):
    if size == 1:
        return (val & 0x1f) % 9     # RCL and RCR only
    elif size == 2:
        return (val & 0x1f) % 17    # RCL and RCR only
    elif size == 4:
        return val & 0x1f
    elif size == 8:
        return val & 0x3f
    else:
        raise Exception("shiftMask is broke in envi/arch/i386/emu.py")


def yieldPacked(valu, size, subsize):
    '''
    For the fun SIMD instructions like psrld, chunk the valu into <subsize> sections
    and return those shifted down
    '''
    mask = e_bits.u_maxes[subsize]

    for i in range(int(size/subsize)):
        sub = valu >> (i * subsize)
        yield (sub & mask)


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

class ThisCall_Caller(ThisCall):
    flags = CC_CALLER_CLEANUP
class MsFastCall_Caller(MsFastCall):
    flags = CC_CALLER_CLEANUP
class BFastCall_Caller(BFastCall):
    flags = CC_CALLER_CLEANUP

stdcall = StdCall()
cdecl = Cdecl()
thiscall = ThisCall()
msfastcall = MsFastCall()
bfastcall = BFastCall()

thiscall_caller = ThisCall_Caller()
msfastcall_caller = MsFastCall_Caller()
bfastcall_caller = BFastCall_Caller()


class IntelEmulator(i386RegisterContext, envi.Emulator):

    flagidx = REG_EFLAGS
    accumreg = { 1:REG_AL, 2:REG_AX, 4:REG_EAX }
    def __init__(self, archmod=None):
        self.__rep_prefix_handlers__ = {
            PREFIX_REP: self.doRepzPrefix,
            PREFIX_REPZ: self.doRepzPrefix,
            PREFIX_REPNZ: self.doRepnzPrefix,
            PREFIX_REP_SIMD: self.doRepSIMDPrefix,
        }

        # Set ourself up as an arch module *and* register context
        #i386Module.__init__(self)
        if archmod is None:
            archmod = i386Module()

        envi.Emulator.__init__(self, archmod=archmod)
        self.initEmuOpt('i386:reponce', False, 'Set to True to short circuit rep prefix')

        for i in range(6):
            self.setSegmentInfo(i, 0, 0xffffffff)

        i386RegisterContext.__init__(self)

        # Add our known calling conventions
        self.addCallingConvention('stdcall', stdcall)
        self.addCallingConvention('cdecl', cdecl)
        self.addCallingConvention('thiscall', thiscall)
        self.addCallingConvention('msfastcall', msfastcall)
        self.addCallingConvention('bfastcall', bfastcall)

        self.addCallingConvention('thiscall_caller', thiscall_caller)
        self.addCallingConvention('msfastcall_caller', msfastcall_caller)
        self.addCallingConvention('bfastcall_caller', bfastcall_caller)

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
        if bytes is None:
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
        if bytes is None:
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
        if op.va is not None:
            self.setProgramCounter(op.va)

        meth = self.op_methods.get(op.mnem, None)
        if meth is None:
            raise e_exc.UnsupportedInstruction(self, op)

        rep_prefix = op.prefixes & PREFIX_REP_MASK
        if rep_prefix and not self.getEmuOpt('i386:reponce'):
            # REP instructions (REP/REPNZ/REPZ/REPSIMD) get their own handlers
            handler = self.__rep_prefix_handlers__.get(rep_prefix)
            newpc = handler(meth, op)

        else:
            newpc = meth(op)

        if newpc is not None:
            self.setProgramCounter(newpc)
            return

        pc = self.getProgramCounter()
        newpc = pc+op.size
        self.setProgramCounter(newpc)

    ###### Repeat Prefix Handlers

    def doRepzPrefix(emu, meth, op):
        '''
        Handle REP and REPZ prefixes (which are basically the same, but used for 
        different instructions.

        ZF starts off being set. 
        Then the instruction is repeated and ECX decremented until either
        ECX reaches 0 or the ZF is cleared.
        '''
        if op.mnem.startswith('nop'):
            return

        ecx = emu.getRegister(REG_ECX)
        emu.setFlag(EFLAGS_ZF, 1)

        ret = None
        while ecx and emu.getFlag(EFLAGS_ZF):
            ret = meth(op)
            ecx -= 1
            emu.setRegister(REG_ECX, ecx)
        return ret

    def doRepnzPrefix(emu, meth, op):
        '''
        Handle REPNZ prefix.

        ZF starts off being cleared. 
        Then the instruction is repeated and ECX decremented until either
        ECX reaches 0 or the ZF is set.
        '''
        ecx = emu.getRegister(REG_ECX)
        emu.setFlag(EFLAGS_ZF, 0)

        ret = None
        while ecx and not emu.getFlag(EFLAGS_ZF):
            ret = meth(op)
            ecx -= 1
            emu.setRegister(REG_ECX, ecx)
        return ret


    def doRepSIMDPrefix(emu, meth, op):
        # TODO
        raise Exception("doRepSIMDPrefix() not implemented.  Fix and retry.")

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

    def doPush(self, val, size=4):
        esp = self.getRegister(REG_ESP)
        esp -= size
        self.writeMemValue(esp, val, size)
        self.setRegister(REG_ESP, esp)

    def doPop(self, size=4):
        esp = self.getRegister(REG_ESP)
        val = self.readMemValue(esp, size)
        self.setRegister(REG_ESP, esp+size)
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

    # Beginning of Instruction methods

    def i_adc(self, op, isDX=False):
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

        if isDX:
            self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(res, tsize))
        else:
            self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(res, tsize))
            self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
            self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
            self.setFlag(EFLAGS_ZF, not res)
            self.setFlag(EFLAGS_SF, e_bits.is_signed(res, tsize))
            self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))

        self.setOperValue(op, 0, res)

    def i_adcx(self, op):
        self.i_adc(op, isDX=True)

    def i_add(self, op, isDOX=False):
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

        if isDOX:
            cf = self.getFlag(EFLAGS_CF)
            ures = ures + cf

        self.setFlag(EFLAGS_CF, e_bits.is_unsigned_carry(ures, dsize))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(ures))
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(src, dst))
        self.setFlag(EFLAGS_ZF, not ures)
        self.setFlag(EFLAGS_SF, e_bits.is_signed(ures, dsize))
        self.setFlag(EFLAGS_OF, e_bits.is_signed_overflow(sres, dsize))

        self.setOperValue(op, 0, ures)

    def i_adox(self, op):
        self.i_add(op, isDOX=True)

    def i_paddb(self, op, width=1, off=0):
        tsize = op.opers[0].tsize
        src1 = self.getOperValue(op, off)
        src2 = self.getOperValue(op, off+1)
        res = 0
        mask = e_bits.u_maxes[width]
        valus = zip(yieldPacked(src1, tsize, width),
                    yieldPacked(src2, tsize, width))
        for idx, (lft, rgt) in enumerate(valus):
            s = (lft + rgt) & mask
            res |= s << (idx * (8 * width))

    def i_paddw(self, op):
        self.i_paddb(op, width=2)

    def i_paddd(self, op):
        self.i_paddb(op, width=4)

    def i_paddq(self, op):
        self.i_paddb(op, width=8)

    def i_vpaddb(self, op):
        self.i_paddb(op, off=1)

    def i_vpaddw(self, op):
        self.i_paddb(op, width=2, off=1)

    def i_vpaddd(self, op):
        self.i_paddb(op, width=4, off=1)

    def i_vpaddq(self, op):
        self.i_paddb(op, width=8, off=1)

    def i_bsf(self, op):
        src = self.getOperValue(op, 1)
        if src == 0:
            self.setFlag(EFLAGS_ZF, 1)
            return
        else:
            self.setFlag(EFLAGS_ZF, 0)
        res = 0
        indx = 0
        while src != 0:
            if src & 0x1:
                res = indx
                break
            src >>= 1
            indx += 1
        self.setOperValue(op, 0, res)
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        self.setFlag(EFLAGS_SF, 0)
        self.setFlag(EFLAGS_OF, 0)
        self.setFlag(EFLAGS_CF, 0)

    def i_and(self, op):
        #FIXME 24 and 25 opcodes should *not* get sign-extended.
        res = self.logicalAnd(op)
        self.setOperValue(op, 0, res)

    def _ands(self, op, off=0):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        res = dst & src

    def i_andsd(self, op):
        self._ands(op)

    i_andss = i_andsd
    i_andps = i_andsd
    i_andpd = i_andsd

    def i_vandsd(self, op):
        self._ands(op, off=1)

    i_vandss = i_vandsd
    i_vandps = i_vandsd
    i_vandpd = i_vandsd

    def i_arpl(self, op):
        v1 = self.getOperValue(op, 0)
        v2 = self.getOperValue(op, 1)

        # Mask off the rpl
        r1 = v1 & 3
        r2 = v2 & 3

        if r1 < r2: # If dest rpl < src rpl
            self.setFlag(EFLAGS_ZF, 1)
            # Bump 2 bits off the bottom and add r2
            self.setOperValue(op, 0, ((v1 >> 2) << 2) | r2)
        else:
            self.setFlag(EFLAGS_ZF, 0)

    def i_bswap(self, op):
        val = self.getOperValue(op, 0)
        tsize = op.opers[0].tsize
        self.setOperValue(op, 0, e_bits.byteswap(val, tsize))

    def i_bsr(self, op):
        val = self.getOperValue(op, 1)
        eflags = self.getRegister(REG_EFLAGS)
        eflags &= 0x00044602        # undocumented, empirical from i9 - do we want to move to main emulator?
                                    # the flags that are carried through are:
                                    # DF, IF, NT, AC and the always-0's and always-1's are enforced
        self.setRegister(REG_EFLAGS, eflags)

        if val == 0:
            # If the src is 0, set ZF and get out
            self.setFlag(EFLAGS_ZF, 1)

            # PF and OF are undocumented, but proven on 32-bit VBox/i9
            self.setFlag(EFLAGS_PF, 1)
            self.setFlag(EFLAGS_OF, 0)
            return

        self.setFlag(EFLAGS_ZF, 0)

        tsize = op.opers[0].tsize
        rmax = (tsize*8) - 1
        while rmax >= 0:
            if val & (1<<rmax):
                # undocumented PF change, but 32-bit VMox on i9 says so
                self.setFlag(EFLAGS_PF, e_bits.is_parity(rmax))
                self.setOperValue(op, 0, rmax)
                return
            rmax -= 1

    def doBitTest(self, op):
        dsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        shift = self.getOperValue(op, 1)
        shift %= (dsize << 3)
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
        mask = e_bits.unsigned(~mask, op.opers[0].tsize)
        self.setOperValue(op, 0, val & mask)

    def i_bts(self, op):
        # bit test (and set in the source)
        val, mask = self.doBitTest(op)
        self.setOperValue(op, 0, val | mask)

    def i_call(self, op):
        eip = self.getProgramCounter()
        saved = eip + op.size
        nextva = self.getOperValue(op, 0)
        self.doPush(saved)

        return nextva

    def i_clc(self, op):
        self.setFlag(EFLAGS_CF, 0)

    def i_cld(self, op):
        self.setFlag(EFLAGS_DF, 0)

    def i_cli(self, op):
        self.setFlag(EFLAGS_IF, 0)

    def i_cmc(self, op):
        # set the CF flag to its complement
        val = self.getFlag(EFLAGS_CF)
        self.setFlag(EFLAGS_CF, not val)

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

        return ((top << (size * 8)) | bot)

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
        if val is None:
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

        dsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        if val == 0:
            raise e_exc.DivideByZero(self)

        if dsize == 1:
            ax = self.getRegister(REG_AX)
            quot = int(ax / val)
            rem  = ax % val
            #if quot > 255:
                #"FIXME: division exception"
            self.setRegister(REG_EAX, (quot << 8) + rem)

        elif dsize == 2:
            ax = self.getRegister(REG_AX)
            dx = self.getRegister(REG_DX)
            tot = (dx << 16) + ax
            quot = int(tot / val)
            rem = tot % val

            self.setRegister(REG_AX, quot)
            self.setRegister(REG_DX, rem)

        elif dsize == 4:
            eax = self.getRegister(REG_EAX)
            edx = self.getRegister(REG_EDX)
            tot = (edx << 32) + eax
            quot = int(tot / val)
            rem = tot % val

            #if quot > 0xffffffff:
                #"FIXME: division exception"

            self.setRegister(REG_EAX, quot)
            self.setRegister(REG_EDX, rem)

        elif dsize == 8:
            rax = self.getRegisterByName("rax")
            rdx = self.getRegisterByName("rdx")
            tot = (rdx << 64) + rax
            quot = int(tot / val)
            rem = tot % val

            if tot > (2**64)-1:
                mesg = '0x%.8x: division exception on %s' % (op.va, str(op))
                raise e_exc.DivideError(self, msg=mesg)

            self.setRegisterByName("rax", quot)
            self.setRegisterByName("rdx", rem)

        else:
            raise e_exc.UnsupportedInstruction(self, op)

    def i_enter(self, op):
        locsize = self.getOperValue(op, 0)
        depth = self.getOperValue(op, 1)
        if depth != 0:
            raise e_exc.UnsupportedInstruction(self, op)

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

    def i_fld(self, op):
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
            if d == 0:
                raise e_exc.DivideByZero(self)
            q = ax // d
            r = ax % d
            res = ((r & 0xff) << 8) | (q & 0xff)
            self.setRegister(REG_AX, res)

        elif tsize == 2:
            val = self.twoRegCompound(REG_DX, REG_AX, 2)
            val = e_bits.signed(val, 4)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 2)
            if d == 0:
                raise e_exc.DivideByZero(self)
            q = val // d
            r = val % d

            self.setRegister(REG_AX, q)
            self.setRegister(REG_DX, r)

        elif tsize == 4:
            val = self.twoRegCompound(REG_EDX, REG_EAX, 4)
            val = e_bits.signed(val, 8)
            d = self.getOperValue(op, 0)
            d = e_bits.signed(d, 4)
            if d == 0:
                raise e_exc.DivideByZero(self)
            q = val // d
            r = val % d

            self.setRegister(REG_EAX, q)
            self.setRegister(REG_EDX, r)

        else:
            raise envi.UnsupportedInstruction(self, op)

    def i_imul(self, op):
        ocount = len(op.opers)
        if ocount == 1:
            dsize = op.opers[0].tsize
            a = e_bits.signed(self._emu_getGpReg(GPR_A, dsize), dsize)
            mult = e_bits.signed(self.getOperValue(op, 0), dsize)
            res = a * mult

            if dsize == 1:
                self.setRegister(REG_AX, res)
            else:
                d, a = self.regsFromCompound(res, dsize)
                self._emu_setGpReg(GPR_A, a, dsize)
                self._emu_setGpReg(GPR_D, d, dsize)

            sof = e_bits.is_unsigned_carry(res, dsize)
            self.setFlag(EFLAGS_CF, sof)
            self.setFlag(EFLAGS_OF, sof)

        elif ocount == 2:
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
            raise e_exc.UnsupportedInstruction(self, op)

        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))
        self.setFlag(EFLAGS_SF, 0)  # technically undefined in the manual, but zero'd on core-i7

    def i_in(self, op):
        raise e_exc.UnsupportedInstruction(self, op)

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

    def i_ud0(self, op):
        raise e_exc.BadOpcode(op)
    i_ud1 = i_ud0
    i_ud2 = i_ud0

    def i_int(self, op):
        raise e_exc.BreakpointHit(self)

    def i_int1(self, op):
        raise e_exc.BreakpointHit(self)

    def i_int3(self, op):
        raise e_exc.BreakpointHit(self)

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

    i_movsxd = i_movsx

    def i_movzx(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)

    i_movd  = i_mov
    i_movd_q = i_mov
    i_vmovd_q = i_mov
    i_movdqu = i_mov
    i_vmovdqu = i_mov
    i_movdqa = i_mov
    i_vmovdqa = i_mov
    i_movaps = i_mov
    i_vmovaps = i_mov
    i_movapd = i_mov
    i_vmovapd = i_mov
    i_movups = i_mov
    i_vmovups = i_mov
    i_movupd = i_mov
    i_vmovupd = i_mov
    i_movnti = i_mov
    i_movntpd = i_mov
    i_vmovntpd = i_mov
    i_movntps = i_mov
    i_vmovntps = i_mov
    i_movntdq = i_mov
    i_vmovntdq = i_mov
    i_movntdqa = i_mov
    i_vmovntdqa = i_mov

    def i_movlps(self, op):
        if op.opers[0].isReg():
            mask = e_bits.u_maxes[8]
            dst = self.getRegisterByName(self.getRealRegisterNameByIdx(op.opers[0].reg)) & (~mask)
            src = self.getOperValue(op, 1)
            self.setOperValue(op, 0, dst | (src & mask))
        else:
            self.i_mov(op)

    def i_movhps(self, op, off=0):
        mask = e_bits.u_maxes[8]
        lvalu = self.getOperValue(op, off)
        self.setOperValue(op, 0, lvalu & mask)

    i_movlpd = i_movlps
    i_movhpd = i_movhps

    def i_vmovlps(self, op):
        if op.opers[0].isReg():
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
            mask = e_bits.u_maxes[8]
            res = ((src1 & mask) << 64) | (src2 & mask)
            self.setOperValue(op, 0, res)
        else:
            self.i_mov(op)

    def i_vmovhps(self, op):
        if op.opers[0].isReg():
            src1 = self.getOperValue(op, 1)
            src2 = self.getOperValue(op, 2)
            mask = e_bits.u_maxes[8]
            res = (src1 & mask) | ((src2 & mask) << 64)
            self.setOperValue(op, 0, res)
        else:
            self.i_mov(op)

    i_vmovlpd = i_vmovlps
    i_vmovhpd = i_vmovhps

    def i_movss(self, op, off=0):
        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)

        if op.opers[off].isReg() and op.opers[off+1].isReg():
            mask = 0x000000000000000000000000FFFFFFFF
            dst &= ~mask
            dst |= src & mask
        else:
            # so technically we're supposed to zero out the upper ymm bits
            mask = 0xFFFFFFFFFFFFFFFFFFFFFFFF00000000
            dst &= ~mask
            dst | src & 0xFFFFFFFF

        self.setOperValue(op, 0, dst)

    def i_vmovss(self, op):
        self.i_movss(op, off=1)

    def i_mul(self, op):
        #FIXME make sure these work right
        tsize = op.opers[0].tsize

        val = self.getOperValue(op, 0)

        # Return al/ax/eax as needed...
        a = self._emu_getGpReg(GPR_A, tsize)

        res = a * val

        if tsize == 1:
            self.setRegister(REG_AX, res)

        elif tsize in (2, 4, 8):
            d, a = self.regsFromCompound(res, tsize)
            self._emu_setGpReg(GPR_A, a, tsize)
            self._emu_setGpReg(GPR_D, d, tsize)
        else:
            mesg = "i_mul called with invalid size of %d" % tsize
            raise e_exc.MultipleError(self, msg=mesg)

        # If the high order stuff was used, set CF/OF
        if res >> (tsize * 8):
            self.setFlag(EFLAGS_CF, 1)
            self.setFlag(EFLAGS_OF, 1)
        else:
            self.setFlag(EFLAGS_CF, 0)
            self.setFlag(EFLAGS_OF, 0)

    def _muls(self, op, off=0):
        opA = self.getOperValue(op, off)
        opB = self.getOperValue(op, off+1)
        res = opA * opB
        self.setOperValue(op, 0, res)

    def i_mulsd(self, op):
        self._muls(op)

    i_mulss = i_mulsd
    #i_mulps = i_mulsd
    #i_mulpd = i_mulsd

    def i_vmulsd(self, op):
        self._muls(op, 1)

    i_vmulss = i_vmulsd
    #i_vmulps = i_vmulsd
    #i_vmulpd = i_vmulsd

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
        self.setRegister(reg, val)

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
        self.setFlag(EFLAGS_AF, e_bits.is_aux_carry(val, res))
        self.setFlag(EFLAGS_PF, e_bits.is_parity_byte(res))

    def i_nop(self, op):
        pass
    i_lfence = i_nop
    i_clflush = i_nop
    i_prefetch = i_nop
    i_prefetchw = i_nop

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
        val = self.doPop(size=op.opers[0].tsize)
        self.setOperValue(op, 0, val)

    def i_popad(self, op):
        # FIXME 16 bit?
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
        tsize = op.opers[0].tsize
        val = self.getOperValue(op, 0)
        if isinstance(op.opers[0], i386ImmOper):
            val = e_bits.sign_extend(val, self.getPointerSize(), 4)
        self.doPush(val, tsize)

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
        # some flags are not pushed:
        eflags &= 0xfffcffff
        eflags |= EFLAGS_TF # trap flag??  seen in the wild.
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

        src = shiftMaskRC(src, dsize)

        # Put that carry bit up there.
        if self.getFlag(EFLAGS_CF):
            dst = dst | (1 << (8 * dsize))

        # Add one to account for carry
        x = ((8*dsize) - src) + 1

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

        src = shiftMaskRC(src, dsize)

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
                self.setFlag(EFLAGS_OF, 0)

    def i_ror(self, op):
        dstSize = op.opers[0].tsize
        count = self.getOperValue(op, 1)
        realcount = shiftMask(count, dstSize)
        tempCount = realcount
        bitlen = dstSize * 8

        if tempCount > 0: # Yeah, i know...weird. See the intel manual
            while tempCount:
                val = self.getOperValue(op, 0)
                tempCf = e_bits.lsb(val)
                self.setOperValue(op, 0, (val >> 1) + (tempCf * (2 ** (bitlen-1))))
                tempCount -= 1

            val = self.getOperValue(op, 0)
            self.setFlag(EFLAGS_CF, e_bits.msb(val, dstSize))

            if realcount:
                cf = self.getFlag(EFLAGS_CF)
                self.setFlag(EFLAGS_OF, bool(e_bits.msb(val, dstSize) ^ e_bits.msb_minus_one(val, dstSize)))

    def i_ret(self, op):
        ret = self.doPop()
        if len(op.opers):
            esp = self.getRegister(REG_ESP)
            ival = self.getOperValue(op, 0)
            self.setRegister(REG_ESP, esp+ival)
        return ret

    def i_bound(self, op):
        if self.psize == 8:
            raise e_exc.UnsupportedInstruction(self, op)    # this instruction is invalid in 64-bit mode

        bsize = op.opers[1].tsize // 2  # target is two numbers
        aidx = e_bits.signed(self.getOperValue(op, 0), self.psize)
        bounds = self.getOperValue(op, 1)
        lowbound = bounds & e_bits.u_maxes[bsize]
        hibound = bounds >> (bsize << 3)    # bsize * 8, but faster

        if lowbound <= aidx <= hibound:
            return

        raise e_exc.BoundRangeExceededException(op.va, op, aidx, lowbound, hibound)

    def i_sal(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        if op.prefixes & PREFIX_REX_W:
            src = src & 0x3f
        else:
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

        self.setFlag(EFLAGS_AF, 0) # Undefined, but zero'd on core-i9 (perhaps only some of the time??!?)

        self.setOperValue(op, 0, res)

    def i_sar(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        if op.prefixes & PREFIX_REX_W:
            src = src & 0x3f
        else:
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
            self.setFlag(EFLAGS_OF, 0)
        else:
            self.setFlag(EFLAGS_OF, 0) # Undefined, but zero'd on core2 duo

        self.setFlag(EFLAGS_AF, 0) # not specified, but zero'd on core-i9 (perhaps only some of the time??!?)

        self.setOperValue(op, 0, res)

    def i_shl(self, op):
        return self.i_sal(op)

    def i_shr(self, op):
        dsize = op.opers[0].tsize
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)

        if op.prefixes & PREFIX_REX_W:  # IA manual states "if 64-bit mode and using REX.W"
            src = src & 0x3f
        else:
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
            self.setFlag(EFLAGS_OF, e_bits.msb(dst, dsize))
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

    def i_shlx(self, op):
        base = self.getOperValue(op, 1)
        shft = self.getOperValue(op, 2)
        base <<= shft
        self.setOperValue(op, 0, base)

    def i_shrx(self, op):
        base = self.getOperValue(op, 1)
        shft = self.getOperValue(op, 2)
        base >>= shft
        self.setOperValue(op, 0, base)

    def i_sarx(self, op):
        base = self.getOperValue(op, 1)
        shft = self.getOperValue(op, 2)

        dsize = op.opers[1].tsize
        msb = e_bits.msb(res, dsize)

        base >>= shft
        if msb:
            # propagate the MSB down
            for i in range(shft):
                base |= (2 ** (32-shft))

        self.setOperValue(op, 0, base)

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
        self.writeMemory(base+edi, bytes(al))
        if self.getFlag(EFLAGS_DF):
            edi -= 1
        else:
            edi += 1
        self.setRegister(REG_EDI, edi)

    def i_stosw(self, op):
        ax = self.getRegister(REG_AX)
        edi = self.getRegister(REG_EDI)
        base,size = self._emu_segments[SEG_ES]
        self.writeMemory(base+edi, struct.pack("<H", ax))
        if self.getFlag(EFLAGS_DF):
            edi -= 2
        else:
            edi += 2
        self.setRegister(REG_EDI, edi)

    def i_stosd(self, op):
        if op.prefixes & PREFIX_REX_W:
            eax = self.getRegister(REG_RAX)
            edi = self.getRegister(REG_RDI)
            step = 8
        else:
            eax = self.getRegister(REG_EAX)
            edi = self.getRegister(REG_EDI)
            step = 4

        base, size = self._emu_segments[SEG_ES]
        self.writeMemory(base+edi, struct.pack("<L", eax))
        if self.getFlag(EFLAGS_DF):
            edi -= step
        else:
            edi += step

        if op.prefixes & PREFIX_REX_W:
            self.setRegister(REG_RDI, edi)
        else:
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
        if src is None or dst is None:
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
        self.setFlag(EFLAGS_CF, 1)

    def i_std(self, op):
        self.setFlag(EFLAGS_DF, 1)

    def i_sti(self, op):
        self.setFlag(EFLAGS_IF, 1)

    def i_sub(self, op):
        x = self.integerSubtraction(op)
        dsize = op.opers[0].tsize
        x = e_bits.unsigned(x, dsize)
        if x is not None:
            self.setOperValue(op, 0, x)

    def i_syscall(self, op):
        # "platforms" must hook this, we just exist to "survive" it
        pass

    def i_test(self, op):
        self.logicalAnd(op)

    def i_wait(self, op):
        pass
        # XXX: "i_wait() is a stub..."

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
        self.setFlag(EFLAGS_AF, 0) # Undefined but actually cleared on amd64 X2

    def i_xorps(self, op, off=0):
        opA = self.getOperValue(op, off)
        opB = self.getOperValue(op, off+1)

        res = opA ^ opB

        self.setOperValue(op, 0, res)
    i_xorpd = i_xorps

    def i_vxorps(self, op):
        self.i_xorps(op, off=1)
    i_vxorpd = i_vxorps

    def i_pxor(self, op):
        self.i_xorps(op)

    def i_vpxor(self, op):
        self.i_xorps(op, off=1)

    def i_orps(self, op, off=0):
        opA = self.getOperValue(op, off)
        opB = self.getOperValue(op, off+1)

        res = opA | opB

        self.setOperValue(op, 0, res)
    i_orpd = i_orps

    def i_vorps(self, op):
        self.i_orps(op, off=1)
    i_vorpd = i_vorps

    def i_por(self, op):
        # TODO: 128 bit non-vex doesn't modify upper ymm bits
        self.i_orps(op)

    def i_vpor(self, op):
        self.i_orps(op, off=1)

    def _psrl(self, op, off=0):
        value = self.getOperValue(op, off)
        imm = self.getOperValue(op, off+1)
        if imm > 15:
            return self.setOperValue(op, 0, 0)

        res = value >> (imm*8)
        self.setOperValue(op, 0, res)

    def _simdshift(self, op, shiftfunc, width, off):
        res = 0
        valu = self.getOperValue(op, off)
        tsize = op.opers[off].tsize
        shift = self.getOperValue(op, off+1)
        mask = e_bits.u_maxes[width]
        for idx, valu in enumerate(yieldPacked(valu, tsize, width)):
            valu = shiftfunc(valu, shift) & mask
            res |= valu << (idx * 8 * width)

        self.setOperValue(op, 0, res)

    # right shifts
    def i_psrlw(self, op):
        self._simdshift(op, operator.rshift, 2, 0)

    def i_psrld(self, op):
        self._simdshift(op, operator.rshift, 4, 0)

    def i_psrlq(self, op):
        self._simdshift(op, operator.rshift, 8, 0)

    def i_psrldq(self, op):
        self._simdshift(op, operator.rshift, 16, 0)

    # vex right shifts
    def i_vpsrlw(self, op):
        self._simdshift(op, operator.rshift, 2, 1)

    def i_vpsrld(self, op):
        self._simdshift(op, operator.rshift, 4, 1)

    def i_vpsrlq(self, op):
        self._simdshift(op, operator.rshift, 8, 1)

    def i_vpsrldq(self, op):
        self._simdshift(op, operator.rshift, 16, 1)

    # left shifts
    def i_psllw(self, op):
        self._simdshift(op, operator.lshift, 2, 0)

    def i_pslld(self, op):
        self._simdshift(op, operator.lshift, 4, 0)

    def i_psllq(self, op):
        self._simdshift(op, operator.lshift, 8, 0)

    def i_pslldq(self, op):
        self._simdshift(op, operator.lshift, 16, 0)

    # vex left shifts
    def i_vpsllw(self, op):
        self._simdshift(op, operator.lshift, 2, 1)

    def i_vpslld(self, op):
        self._simdshift(op, operator.lshift, 4, 1)

    def i_vpsllq(self, op):
        self._simdshift(op, operator.lshift, 8, 1)

    def i_vpslldq(self, op):
        self._simdshift(op, operator.lshift, 16, 1)

    def i_pshufb(self, op, off=0):
        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off)
        res = 0

        if op.opers[0].tsize == 8:
            mask = 0x07
        else:
            mask = 0x0F

        for i in range(op.opers[0].tsize):
            shfl = src & (1 << ((i * 8) + 7))
            if shfl:
                s = 0
            else:
                indx = (src >> (i * 8)) & mask
                s = (src >> (indx * 8)) & 0xFF
            res |= (s << (i * 8))

        self.setOperValue(op, 0, res)

    def i_vpshufb(self, op):
        self.i_pshufb(op, off=1)

    def i_pshufd(self, op, bwidth=32):
        mask = e_bits.u_maxes[4]
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        order = self.getOperValue(op, 2)
        res = 0

        # lower portion, 128 / 32 = 4
        for i in range(4):
            indx = (order >> (2 * i)) & 0x3
            res |= ((src >> (indx * bwidth)) & mask) << (i * bwidth)

        # only comes into play when using the ymm registers
        if op.opers[0].tsize == 32:
            src >>= 128
            for i in range(4):
                indx = (order >> (2 * i)) & 0x3
                res |= ((src >> (indx * bwidth)) & mask) << ((i * bwidth) + 128)

        self.setOperValue(op, 0, res)

    i_vpshufd = i_pshufd

    def i_pshufw(self, op):
        mask = e_bits.u_maxes[2]
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        order = self.getOperValue(op, 2)
        res = 0
        for i in range(4):
            indx = (order >> (2*i)) & 3
            valu = (src >> (indx & 16)) & mask
            res |= valu << (i * 16)

        self.setOperValue(op, 0, res)

    def i_pshuflw(self, op, offset=0):
        mask = e_bits.u_maxes[2] << offset
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        order = self.getOperValue(op, 2)
        clear = e_bits.u_maxes[8] << (64 - offset)
        res = src & clear

        for i in range(4):
            indx = (order >> (2*i)) & 0x3
            valu = ((src >> (indx * 16)) >> offset) & mask
            res |= valu << ((i * 16) + offset)

        if op.opers[0].tsize == 32:
            src >>= 128
            res |= (src & clear) << 128
            for i in range(4):
                indx = (order >> (2 * i)) & 0x3
                valu = ((src >> (indx * 16)) >> offset) & mask
                res |= valu << ((i * 16) + 128 + offset)

        self.setOperValue(op, 0, res)

    i_vpshuflw = i_pshuflw

    def i_pshufhw(self, op):
        self.i_pshuflw(op, offset=64)
    i_vpshufhw = i_pshufhw

    def _interleave_low(self, dst, src, tsize, width, limit):
        res = 0
        values = zip(yieldPacked(dst, tsize, width),
                     yieldPacked(src, tsize, width))

        mask = e_bits.u_maxes[width]
        consumed = 0
        for i, (dst, src) in enumerate(values):
            res |= dst << (width*i)
            res |= src << (width * (i+1))
            consumed += 2 * width
            if consumed >= limit:
                break

        return res

    def _interleave_high(self, dst, src, tsize, width, limit):
        consumed = 0
        res = 0
        values = zip(yieldPacked(dst, tsize, width),
                     yieldPacked(src, tsize, width))
        values = list(values)
        values = values[(len(values) >> 1):]
        for i, (dst, src) in enumerate(values):
            res |= dst << (8 * width * i)
            res |= src << (8 * width * (i + 1))
            consumed += 2 * width
            if consumed >= limit:
                break
        return res


    def i_punpcklbw(self, op, width=1, off=0, override=False):
        name = self.getRealRegisterNameByIdx(op.opers[0].reg)
        realreg = self.getRegisterByName(name)

        mask = ~e_bits.u_maxes[width]
        valu = realreg & mask

        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)
        tsize = op.opers[0].tsize
        res = self._interleave_low(dst, src, op.opers[0].tsize, width, op.opers[0].tsize)

        # manual says to leave the upper bits of the ymm regs alone
        if not override:
            res |= valu

        self.setOperValue(op, 0, res)

    def i_punpcklwd(self, op):
        # interleave words
        self.i_punpcklbw(op, width=2)

    def i_punpckldq(self, op):
        # interleave dwords
        self.i_punpcklbw(op, width=4)

    def i_punpcklqdq(self, op):
        # interleave qwords
        self.i_punpcklbw(op, width=8)

    def i_punpckhbw(self, op, width=1, off=0, override=False):
        name = self.getRealRegisterNameByIdx(op.opers[0].reg)
        realreg = self.getRegisterByName(name)

        mask = ~e_bits.u_maxes[width]
        valu = realreg & mask

        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)
        tsize = op.opers[0].tsize
        res = self._interleave_high(dst, src, op.opers[0].tsize, width, op.opers[0].tsize)

        # manual says to leave the lower bits of the ymm regs alone
        if not override:
            res |= valu
        self.setOperValue(op, 0, res)

    def i_punpckhwd(self, op):
        self.i_punpckhbw(op, width=2)

    def i_punpckhdq(self, op):
        self.i_punpckhbw(op, width=4)

    def i_punpckhqdq(self, op):
        self.i_punpckhbw(op, width=8)

    def i_vpunpcklbw(self, op, width=1):
        tsize = op.opers[0].tsize
        if tsize == 16:
            self.i_punpcklbw(op, width=width, off=1, override=True)
        elif tsize == 32:
            # TODO
            pass
    def i_vpunpcklwd(self, op):
        self.i_vpunpcklbw(op, width=2)
    def i_vpunpckldq(self, op):
        self.i_vpunpcklbw(op, width=4)
    def i_vpunpcklqdq(self, op):
        self.i_vpunpcklbw(op, width=8)

    def i_vpunpckhbw(self, op, width=1):
        tsize = op.opers[0].tsize
        if tsize == 16:
            self.i_punpckhbw(op, width=width, off=1, override=True)
        elif tsize == 32:
            # TODO
            pass
    def i_vpunpckhwd(self, op):
        self.i_vpunpckhbw(self, op, width=2)
    def i_vpunpckhdq(self, op):
        self.i_vpunpckhbw(self, op, width=4)
    def i_vpunpckhqdq(self, op):
        self.i_vpunpckhbw(self, op, width=8)

    def _simdcmpr(self, op, cmpr, width, off):
        res = 0
        dest = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)
        packed = zip(yieldPacked(dest, op.opers[off].tsize, width),
                     yieldPacked(src, op.opers[off+1].tsize, width))

        eql = e_bits.u_maxes[width]
        for idx, (lft, rgt) in enumerate(packed):
            valu = cmpr(lft, rgt)
            res |= valu << (8 * width * idx)
        self.setOperValue(op, 0, res)

    def i_pcmpeqb(self, op, width=1, off=0):
        res = 0
        dest = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)
        packed = zip(yieldPacked(dest, op.opers[off].tsize, width),
                     yieldPacked(src, op.opers[off+1].tsize, width))

        eql = e_bits.u_maxes[width]
        for idx, (lft, rgt) in enumerate(packed):
            if lft == rgt:
                cmp = eql
            else:
                cmp = 0
            res |= cmp << (width * idx)
        self.setOperValue(op, 0, res)

    def i_por(self, op, off=0):
        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)

        res = src | dst

        self.setOperValue(op, 0, res)

    def i_pcmpeqw(self, op):
        self.i_pcmpeqb(op, width=2, off=0)
    def i_pcmpeqd(self, op):
        self.i_pcmpeqb(op, width=4, off=0)
    def i_pcmpeqq(self, op):
        self.i_pcmpeqb(op, width=8, off=0)

    def i_vpcmpeqw(self, op):
        self.i_pcmpeqb(op, off=1)
    def i_vpcmpeqw(self, op):
        self.i_pcmpeqb(op, width=2, off=1)
    def i_vpcmpeqd(self, op):
        self.i_pcmpeqb(op, width=4, off=1)
    def i_vpcmpeqq(self, op):
        self.i_pcmpeqb(op, width=8, off=1)

    def i_pminsb(self, op, width=1, off=0):
        def cmpr(a, b):
            return e_bits.unsigned(min(e_bits.signed(a, width), e_bits.signed(b, width)), width)
        self._simdcmpr(op, cmpr, width, off)

    def i_pminsw(self, op):
        self.i_pminsb(op, width=2)
    def i_pminsd(self, op):
        self.i_pminsb(op, width=4)
    def i_pminsq(self, op):
        self.i_pminsb(op, width=8)

    def i_vpminsb(self, op):
        self.i_pminsb(op, width=1, off=1)
    def i_vpminsw(self, op):
        self.i_pminsb(op, width=2, off=1)
    def i_vpminsd(self, op):
        self.i_pminsb(op, width=4, off=1)
    def i_vpminsq(self, op):
        self.i_pminsb(op, width=8, off=1)

    def i_pmaxsb(self, op, width=1, off=0):
        def cmpr(a, b):
            return e_bits.unsigned(max(e_bits.signed(a, width), e_bits.signed(b, width)), width)
        self._simdcmpr(op, cmpr, width, off)

    def i_pmaxsw(self, op):
        self.i_pmaxsb(op, width=2, off=0)
    def i_pmaxsd(self, op):
        self.i_pmaxsb(op, width=4, off=0)
    def i_pmaxsq(self, op):
        self.i_pmaxsb(op, width=8, off=0)

    def i_vpmaxsb(self, op):
        self.i_pmaxsb(op, off=1)
    def i_vpmaxsw(self, op):
        self.i_pmaxsb(op, width=2, off=1)
    def i_vpmaxsd(self, op):
        self.i_pmaxsb(op, width=4, off=1)
    def i_vpmaxsq(self, op):
        self.i_pmaxsb(op, width=8, off=1)

    def i_pmovmskb(self, op):
        res = 0
        src = self.getOperValue(op, 1)
        dsize = op.opers[0].tsize
        ssize = op.opers[1].tsize

        if dsize < 4:
            raise envi.UnsupportedInstruction(self, op)
        for i in range(ssize >> 3):
            res |= (src & (1 << (7 + i*8))) << i
        self.setOperValue(op, 0, res)

    i_vpmovmskb = i_pmovmskb

    def i_lahf(self, op):
        self.setRegister(REG_AH, self.getRegister(REG_EFLAGS) & 0b11010101)

    def i_sahf(self, op):
        self.setRegister(REG_EFLAGS, (self.getRegister(REG_AH) & 0b11010101) | 0b00100000)

    def i_pinsrb(self, op, width=1):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        select = self.getOperValue(op, 2)
        mask = e_bits.u_maxes[width]
        bitwidth = width * 8
        if width == 1:
            select &= 0xF
            src &= 0xFF
        elif width == 2:
            select &= 0x7
        elif width == 4:
            select &= 0x3
        elif width == 8:
            select &= 1

        mask <<= bitwidth * select
        tmp = (src << (select * bitwidth)) & mask
        dst = dst &  (~mask) | tmp
        self.setOperValue(op, 0, dst)

    def i_pinsrw(self, op):
        self.i_pinsrb(op, width=2)

    def i_pinsrd(self, op):
        self.i_pinsrb(op, width=4)

    # psubq and variants
    def i_psubb(self, op, width=1, off=0):
        tsize = op.opers[0].tsize
        src1 = self.getOperValue(op, off)
        src2 = self.getOperValue(op, off + 1)
        res = 0
        mask = e_bits.u_maxes[width]

        valus = zip(yieldPacked(src1, tsize, width),
                    yieldPacked(src1, tsize, width))

        for idx, (lft, rgt) in enumerate(valus):
            s = (lft - rgt) & mask
            res |= s << (idx * 8 * width)

        self.setOperValue(op, 0, res)

    def i_psubw(self, op):
        self.i_psubb(op, width=2)

    def i_psubd(self, op):
        self.i_psubb(op, width=4)

    def i_psubq(self, op):
        self.i_psubb(op, width=8)

    def i_vpsubb(self, op):
        self.i_psubb(op, width=1, off=1)
    def i_vpsubw(self, op):
        self.i_psubb(op, width=2, off=1)
    def i_vpsubd(self, op):
        self.i_psubb(op, width=4, off=1)
    def i_vpsubq(self, op):
        self.i_psubb(op, width=8, off=1)

    # signed variants of the above
    def i_psubsb(self, op, width=1, off=0):
        '''
        like i_psubb, but with an extra fun check for saturation!
        '''
        tsize = op.opers[0].tsize
        src1 = self.getOperValue(op, off)
        src2 = self.getOperValue(op, off + 1)
        res = 0
        mask = e_bits.u_maxes[width]
        bitwidth = width * 8
        valus = zip(yieldPacked(src1, tsize, width),
                    yieldPacked(src1, tsize, width))

        shigh = e_bits.signed((2 ** (bitwidth - 1)) - 1, width)
        slow = e_bits.signed((2 ** (bitwidth - 1)), width)
        for idx, (lft, rgt) in enumerate(valus):
            s = lft - rgt
            if s > shigh:
                s = shigh
            elif s < slow:
                s = slow
            res |= s << (idx * bitwidth)

    def i_psubsw(self, op):
        self.i_psubsb(op, width=2)

    def i_psubsd(self, op):
        self.i_psubsb(op, width=4)

    def i_psubsq(self, op):
        self.i_psubsb(op, width=8)

    def i_vpsubsb(self, op):
        self.i_psubsb(op, width=1, off=1)

    def i_vpsubsw(self, op):
        self.i_psubsb(op, width=2, off=1)

    def i_vpsubsd(self, op):
        self.i_psubsb(op, width=4, off=1)

    def i_vpsubsq(self, op):
        self.i_psubsb(op, width=8, off=1)

    def i_pand(self, op, off=0):
        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)

        ret = dst & src

        self.setOperValue(op, 0, ret)

    def i_pandn(self, op, off=0):
        dst = self.getOperValue(op, off)
        src = self.getOperValue(op, off+1)

        ret = (~dst) & src

        self.setOperValue(op, 0, ret)

    def i_vpand(self, op):
        self.i_pand(op, off=1)

    def i_vpandn(self, op):
        self.i_pandn(op, off=1)

    def i_pextrb(self, op, width=1):
        dst = self.getOperValue(op, 0)
        src = self.getOperValue(op, 1)
        sel = self.getOperValue(op, 2)

        src = (src >> (sel*width*8)) & e_bits.u_maxes[width]
        # clear the bits only on pextrb
        if width != 1:
            dst = dst & (~e_bits.u_maxes[width])
            src |= dst
        self.setOperValue(op, 0, src)

    def i_pextrw(self, op):
        self.i_pextrb(op, width=2)

    def i_pextrd(self, op):
        self.i_pextrb(op, width=4)
