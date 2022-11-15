# -*- coding: iso-8859-15 -*-

import sys

import envi
import envi.bits as e_bits
import envi.memory as e_mem
import envi.common as e_common

import math
import operator
import struct
import math

from envi import *
from .regs import *
from .const import *
from .disasm import *
from .bits import *
from envi.archs.ppc import *


logger = logging.getLogger(__name__)

'''
PowerPC Emulation code.  most of this code is written based on the information from the
EREF, Rev. 1 (EIS 2.1)
(aka EREF_RM.pdf from http://cache.freescale.com/files/32bit/doc/ref_manual/EREF_RM.pdf)

that documentation is specific, and generally good, with one Major exception:
    they think that 0 is the Most Significant Bit!

this convention flies in the face of most other architecture reference manuals, and the
way that the authors of this module themselves, think of bit numbering for instructions.
therefore, some places may seem a little confusing if compared to the EREF.

MASK and ROTL have specifically been coded to allow the emulated instructions to map
directly to the EREF docs execution pseudocode.
'''

class PpcCall(envi.CallingConvention):
    '''
    PowerPC Calling Convention.
    '''

    # From the PPC ELF64ABI version 1.9 chapter 3.2.1:
    #
    # The 64-bit PowerPC Architecture provides 32 general purpose registers,
    # each 64 bits wide. In addition, the architecture provides 32
    # floating-point registers, each 64 bits wide, and several special purpose
    # registers. All of the integer, special purpose, and floating-point
    # registers are global to all functions in a running program. The
    # following table shows how the registers are used.
    #
    #   r0          Volatile register used in function prologs
    #   r1          Stack frame pointer
    #   r2          TOC pointer
    #   r3          Volatile parameter and return value register
    #   r4-r10      Volatile registers used for function parameters
    #   r11         Volatile register used in calls by pointer and as an
    #               environment pointer for languages which require one
    #   r12         Volatile register used for exception handling and glink code
    #   r13         Reserved for use as system thread ID
    #   r14-r31     Nonvolatile registers used for local variables
    #
    #   f0          Volatile scratch register
    #   f1-f4       Volatile floating point parameter and return value registers
    #   f5-f13      Volatile floating point parameter registers
    #   f14-f31     Nonvolatile registers
    #   LR          Link register (volatile)
    #   CTR         Loop counter register (volatile)
    #   XER         Fixed point exception register (volatile)
    #   FPSCR       Floating point status and control register (volatile)
    #
    #   CR0-CR1     Volatile condition code register fields
    #   CR2-CR4     Nonvolatile condition code register fields
    #   CR5-CR7     Volatile condition code register fields
    #
    # On processors with the VMX feature.
    #
    #   v0-v1       Volatile scratch registers
    #   v2-v13      Volatile vector parameters registers
    #   v14-v19     Volatile scratch registers
    #   v20-v31     Non-volatile registers
    #   vrsave      Non-volatile 32-bit register

    arg_def = [(CC_REG, REG_R3 + x) for x in range(8)]
    arg_def.append((CC_STACK_INF, 8))
    retaddr_def = (CC_REG, REG_LR)
    retval_def = (CC_REG, REG_R3)
    flags = CC_CALLEE_CLEANUP

    # Stack layout from the PPC ELF64ABI version 1.9 chapter 3.5.13.
    #
    #   High address
    #           +-> Back chain
    #           | Floating point register save area
    #           | General register save area
    #           | VRSAVE save word (32-bits)
    #           | Alignment padding (4 or 12 bytes)
    #           | Vector register save area (quadword aligned)
    #           | Local variable space
    #           | Parameter save area         (SP + 48)
    #           | TOC save area               (SP + 40) --+
    #           | link editor doubleword      (SP + 32)   |
    #           | compiler doubleword         (SP + 24)   |--stack frame header
    #           | LR save area                (SP + 16)   |
    #           | CR save area                (SP + 8)    |
    #   SP ---> +-- Back chain                (SP + 0)  --+
    #   Low address

    align = 16
    pad = 0

ppccall = PpcCall()

OPER_SRC = 1
OPER_DST = 0

# Static generation of which bit should be set according to the PPC
# documentation for 32 and 64 bit values
_ppc64_bitmasks = tuple(0x8000_0000_0000_0000 >> i for i in range(64))
_ppc32_bitmasks = tuple(0x8000_0000 >> i for i in range(32))
_ppc_bitmasks = (None, None, None, None, _ppc32_bitmasks, None, None, None, _ppc64_bitmasks)

def BITMASK(bit, psize=8):
    '''
    Return mask with bit b of 64 or 32 set using PPC numbering.

    Most PPC documentation uses 64-bit numbering regardless of whether or not
    the underlying architecture is 64 or 32 bits.
    '''
    return _ppc_bitmasks[psize][bit]

def BIT(val, bit, psize=8):
    '''
    Return value of specified bit provided in PPC numbering
    '''
    return (val & _ppc_bitmasks[psize][bit]) >> ((psize << 3) - bit - 1)

# Carry bit mask and shift the tuple values are:
#   1. CA mask
#   2. right shift value
MAX_PPC_WORD_RANGE = range(0, e_bits.MAX_WORD + 1)
_ppc_carry_masks = tuple(1 << (8*i) for i in MAX_PPC_WORD_RANGE)
_ppc_carry_shift = tuple(      8*i  for i in MAX_PPC_WORD_RANGE)

# Results for the "signed saturate" arithmetic operations depending on if the
# "CA" bit is set in the result.
_ppc_signed_saturate_min = tuple(e_bits.signed( ((2 ** (8*i)) >> 1),      i) for i in MAX_PPC_WORD_RANGE)
_ppc_signed_saturate_max = tuple(e_bits.signed((((2 ** (8*i)) >> 1) - 1), i) for i in MAX_PPC_WORD_RANGE)

# The value returned is based on the carry bit:
#   0 (no carry) means use the max value
#   1 (carry) means use the min value
_ppc_signed_saturate_results = (_ppc_signed_saturate_max, _ppc_signed_saturate_max)

def CARRY(val, size):
    '''
    Return the MSB+1 (CA) bit.  If your math uses negative values, this function might give incorrect information
    due to the fact that negative numbers have all sig bits set indefinitely and are not limited to the pointer size.
    If the result supplied to this function to check for carry has already been limited to the pointer size, Carry will
    never be detected.

    Don't use negative numbers in the math.

    '''
    ca_mask = _ppc_carry_masks[size]
    ca_shift = _ppc_carry_shift[size]
    ca = (val & ca_mask) >> ca_shift
    return ca

def SIGNED_SATURATE(val, size):
    '''
    Return the min or max value for a size depending on if the value exceeds
    the range specified by size (in bytes).

    e.g. for size 1, if val is > (2^7-1), or 127, then it gets clamped to 127
    '''
    saturated = False
    if val > _ppc_signed_saturate_max[size]:
        val = _ppc_signed_saturate_max[size]
        saturated = True
    elif val < _ppc_signed_saturate_min[size]:
        val = _ppc_signed_saturate_min[size]
        saturated = True

    return val, saturated

def UNSIGNED_SATURATE(val, size):
    '''
    Return the min or max value for a size depending on if the value exceeds
    the range specified by size (in bytes).

    e.g. for size 1, if val is > (2^8-1), or 255, then it gets clamped to 255
    '''
    saturated = False
    if val > e_bits.u_maxes[size]:
        val = e_bits.u_maxes[size]
        saturated = True
    elif val < 0:
        val = 0
        saturated = True

    return val, saturated

def SATURATE_SPE(ov, carry, sat_ovn, sat_ov, val):
    if ov:
        if carry:
            return sat_ovn
        else:
            return sat_ov
    return val


def COMPLEMENT(val, size):
    '''
    1's complement of the value
    '''
    return val ^ e_bits.u_maxes[size]

def MASK(b, e):
    '''
    helper to create masks.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!
    '''
    if e < b:
        delta = b - e - 1
        real_shift = 63 - b + 1
        mask = e_bits.bu_maxes[delta] << real_shift
        mask ^= 0xffffffffffffffff
        return mask

    delta = e - b + 1
    real_shift = 63 - e
    return e_bits.bu_maxes[delta] << (real_shift)

def MASK16(b, e):
    return MASK(b+48, e+48)

def MASK32(b, e):
    return MASK(b+32, e+32)

def EXTS(val, size=8, psize=8):
    '''
    The PowerPC manual uses EXTS() often to indicate sign extending, so
    this is a convenience function that calls envi.bits.sign_extend using
    a newsize of the native pointer size for the current architecture.
    '''
    return e_bits.sign_extend(val, size, psize)

def EXTS_BIT(val, newsize=8):
    '''
    Sign-extend a single bit to the given size, in bits.
    '''
    return (~((val & 0x1) - 1)) & MASK(64 - newsize, 63)

def EXTZ(val, size=8):
    '''
    The PowerPC manual uses EXTZ() often to indicate zero extending, so
    this is a convenience function that calls envi.bits.unsigned.
    '''
    return e_bits.unsigned(val, size)

def ROTL(val, rot, size):
    '''
    Rotate `val` left `rot` bits, around `size` bits.
    'val` must be between 0 and `size`-1
    `size` must be 8, 16, 32, 64, or 128

    Note: ROTL32() and ROTL64() were written specifically to implement as
    the PowerISA documentation describes, for traceability and
    troubleshooting, and remain for historical reasons.
    '''
    tmp = val >> (size - rot)
    return ((val << rot) | tmp) & e_bits.u_maxes[size // 8]

def ROTL32(x, y, psize=8):
    '''
    helper to rotate left, 32-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!

    Shift size must be 0-31 when using this function.
    '''
    tmp = x >> (32-y)
    x |= (x<<32)
    return ((x << y) | tmp) & e_bits.u_maxes[psize]

def ROTL64(x, y, psize=8):
    '''
    helper to rotate left, 64-bit stype.
    NOTE: THIS IS IN NXP's WARPED VIEW ON BIT NUMBERING!
    lsb = bit 63!!!

    Shift size must be 0-63 when using this function.
    '''
    tmp = x >> (64-y)
    return ((x << y) | tmp) & e_bits.u_maxes[psize]

def ROTR(val, rot, size):
    '''
    Rotate `val` right `rot` bits, around `size` bits.
    'val` must be between 0 and `size`-1
    `size` must be 8, 16, 32, 64, or 128
    '''
    tmp = val << (size - rot)
    return (tmp | (val >> rot)) & e_bits.u_maxes[size // 8]

def ONES_COMP(val, size):
    '''
    Helper function to use the size limited one's complement
    when dealing with signed numbers
    '''
    mask = e_bits.bu_maxes[size]
    return (val & mask) ^ mask

def getCarryBitAtX(bit, add0, add1):
    '''
    return the carry bit at bit x.
    '''
    a0b = (add0 & e_bits.b_masks[bit])
    a1b = (add1 & e_bits.b_masks[bit])
    results = (a0b + a1b) >> (bit)
    return results

def CLZ(x, psize=8):
    '''
    Count leading zeros, supports maximum of 64bit values.
    '''
    # Make sure that the input value does not have any bits set above the
    # maximum possible size for the byte size indicated
    x = x & e_bits.u_maxes[psize]

    if x == 0:
        return psize * 8

    n = 0
    # There is probably a better way to do this but this works
    if psize == 8:
        checks = (
            (32, 0xFFFF_FFFF_0000_0000),
            (16, 0x0000_0000_FFFF_0000),
            (8,  0x0000_0000_0000_FF00),
            (4,  0x0000_0000_0000_00F0),
            (2,  0x0000_0000_0000_000C),
            (1,  0x0000_0000_0000_0002),
        )
    elif psize == 4:
        checks = (
            (16, 0xFFFF_0000),
            (8,  0x0000_FF00),
            (4,  0x0000_00F0),
            (2,  0x0000_000C),
            (1,  0x0000_0002),
        )
    elif psize == 2:
        checks = (
            (8,  0xFF00),
            (4,  0x00F0),
            (2,  0x000C),
            (1,  0x0002),
        )
    elif psize == 1:
        checks = (
            (4,  0xF0),
            (2,  0x0C),
            (1,  0x02),
        )

    for shift, mask in checks:
        # # If the result after masking is 0 then there are at least "shift"
        # leading zeros.  If it is not zero then shift the number to the right
        # and do the next mask to try and identify how many leading zeros there
        # are.
        if x & mask == 0:
            n += shift
        else:
            x = x >> shift
    return n

def CLO(x, psize=8):
    '''
    Count leading ones, supports maximum of 64bit values.
    '''
    # Make sure that the input value does not have any bits set above the
    # maximum possible size for the byte size indicated
    x = x & e_bits.u_maxes[psize]

    n = 0
    for i in range(64 - (psize * 8), 64):
        mask = MASK(0, i)
        tester = e_bits.u_maxes[psize] & mask
        if (x & mask) == tester:
            n += 1
        else:
            break

    return n

# Conditional Branch BO and BI decoding utilities

def BO_UNCONDITIONAL(bo):
    return bool(bo & FLAGS_BO_CHECK_COND) and bool(bo & FLAGS_BO_DECREMENT)

def BO_DECREMENT(bo):
    return not bool(bo & FLAGS_BO_DECREMENT)

def BO_CTR_OK(bo, ctr):
    # For some reason the CTR == or != 0 bit is reversed from the desired value
    # of CTR.
    return bool(bo & FLAGS_BO_CHECK_CTR_ZERO) != bool(ctr)

def BO_CONDITIONAL(bo):
    return not bool(bo & FLAGS_BO_CHECK_COND)

def BO_COND_OK(bo, cond):
    # The cr argument is expected to be already masked with the correct bits, so
    # if it is 0 then the condition is false, otherwise the condition is true.
    #
    # If the BO_COND_MASK bit is set then the branch condition is met if the CR
    # condition is set
    return bool(bo & FLAGS_BO_COND) == bool(cond)

def BITREVERSE32(x):
    x = ((x & 0x55555555) << 1) | ((x & 0xAAAAAAAA) >> 1)
    x = ((x & 0x33333333) << 2) | ((x & 0xCCCCCCCC) >> 2)
    x = ((x & 0x0F0F0F0F) << 4) | ((x & 0xF0F0F0F0) >> 4)
    x = ((x & 0x00FF00FF) << 8) | ((x & 0xFF00FF00) >> 8)
    x = ((x & 0x0000FFFF) << 16) | ((x & 0xFFFF0000) >> 16)
    return x

class PpcAbstractEmulator(envi.Emulator):

    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=8):
        self.psize = psize
        super(PpcAbstractEmulator, self).__init__(archmod=archmod)
        self.setEndian(endian)

        self.addCallingConvention("ppccall", ppccall)

        self.spr_read_handlers = {
        }
        self.spr_write_handlers = {
        }

    # Special Register Access Handlers: SPRs often have ties to hardware things
    # which may want to be emulated
    def addSprReadHandler(self, reg, handler):
        '''
        Set a handler for any reads from any given SPR
        '''
        self.spr_read_handlers[reg] = handler

    def delSprReadHandler(self, reg):
        '''
        Remove a handler for any reads from any given SPR
        '''
        if reg in self.spr_read_handlers:
            return self.spr_read_handlers.pop(reg)

    def addSprWriteHandler(self, reg, handler):
        '''
        Set a handler for any writes to any given SPR
        '''
        self.spr_write_handlers[reg] = handler

    def delSprWriteHandler(self, reg):
        '''
        Remove a handler for any writes to any given SPR
        '''
        if reg in self.spr_write_handlers:
            return self.spr_write_handlers.pop(reg)

    def undefFlags(self):
        """
        Used in PDE.
        A flag setting operation has resulted in un-defined value.  Set
        the flags to un-defined as well.
        """
        self.setRegister(REG_FLAGS, None)

    def setFlag(self, which, state):
        flags = self.getRegister(REG_FLAGS)
        # On PDE, assume we're setting enough flags...
        if flags ==  None:
            flags = 0

        if state:
            flags |= (1<<which)
        else:
            flags &= ~(1<<which)
        self.setRegister(REG_FLAGS, flags)

    def getFlag(self, which):
        flags = self.getRegister(REG_FLAGS)
        if flags == None:
            raise envi.PDEUndefinedFlag(self)
        return bool(flags & (1<<which))

    def executeOpcode(self, op):
        # NOTE: If an opcode method returns
        #       other than None, that is the new eip
        meth = self.op_methods[op.opcode]
        if meth == None:
            raise envi.UnsupportedInstruction(self, op)

        x = meth(op)
        if x != None:
            self.setProgramCounter(x)
        else:
            pc = self.getProgramCounter()
            pc += op.size
            self.setProgramCounter(pc)

    def _populateOpMethods(self):
        # pre-allocate all of the methods to be invalid
        self.op_methods = [None] * inscounter
        from . import const as ppc_consts

        # TODO PRINTS ARE FOR DEBUGGING, REMOVE WHEN EMU IS DONE
        # Make a list of which INS_ is in which category
        instr_cat = {}
        for instr_list in instr_dict.values():
            for instr in instr_list:
                opcode = instr[2][1]
                cat = instr[2][3]

                if opcode not in instr_cat:
                    instr_cat[opcode] = cat

                elif opcode in instr_cat and instr_cat[opcode] != cat:
                    # This doesn't apply to FP and FP.R
                    if CAT_FP in (instr_cat[opcode], cat) and \
                            CAT_FP_R in (instr_cat[opcode], cat):
                                continue

                    opcodestr = next(a for a in dir(ppc_consts) \
                            if a.startswith('INS_') and \
                            opcode == getattr(ppc_consts, a))

                    oldcatstr =  next(a for a in dir(ppc_consts) \
                            if a.startswith('CAT_') and \
                            instr_cat[opcode] == getattr(ppc_consts, a))

                    newcatstr =  next(a for a in dir(ppc_consts) \
                            if a.startswith('CAT_') and \
                            cat == getattr(ppc_consts, a))

                    logger.warning("instruction CAT mismatch for %s(%x): %s(%x) != %s(%x)" % (opcodestr, opcode, oldcatstr, instr_cat[opcode], newcatstr, cat))

        # Now go through each instruction identified and find an emulation
        # function for it
        for name in dir(ppc_consts):
            if name.startswith("INS_"):
                opcode = getattr(ppc_consts, name)

                emu_method_name = 'i_' + name[4:].lower()
                if hasattr(self, emu_method_name):
                    self.op_methods[opcode] = getattr(self, emu_method_name)

    def _checkExtraOpMethods(self):
        assigned_methods = [f for f in self.op_methods if f is not None]
        for name in dir(self):
            if name.startswith("i_"):
                emu_method = getattr(self, name)
                if emu_method not in assigned_methods:
                    logger.warning("%r emulation method not assigned an opcode" % name)

    ####################### Placeholder Functions ###########################
    # These functions are expected to be overridden with core-specific behavior
    # when the abstract emulator is subclassed

    def _rfi(self, op):
        pass

    def _trap(self, op):
        logger.log(e_common.EMULOG, 'TRAP 0x%08x: %r', op.va, op)

    def _sc(self, op):
        logger.log(e_common.EMULOG, 'SC 0x%08x: %r', op.va, op)

    def _ehpriv(self, op):
        logger.log(e_common.EMULOG, 'EHPRIV 0x%08x: %r', op.va, op)

    def _wait(self, op):
        pass

    ####################### Helper Functions ###########################
    def doPush(self, val):
        psize = self.getPointerSize()
        sp = self.getRegister(REG_SP)
        sp += psize
        self.writeMemValue(sp, val, psize)
        self.setRegister(REG_SP, sp)

    def doPop(self):
        psize = self.getPointerSize()
        sp = self.getRegister(REG_SP)
        val = self.readMemValue(sp, psize)
        sp -= psize
        self.setRegister(REG_SP, sp)
        return val

    ########################### Flag Helpers #############################

    def getCr(self, crnum=0):
        '''
        get a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        cr = self.getRegister(REG_CR)
        return (cr >> ((7-crnum) * 4)) & 0xf

    def setCr(self, flags, crnum=0):
        '''
        set a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        cr = self.getRegister(REG_CR)
        cr &= (cr_mask[crnum])
        cr |= (flags << ((7-crnum) * 4))
        self.setRegister(REG_CR, cr)

    def setCMPFlags(self, flags, crnum=0):
        '''
        Update the LT/GT/EQ flags in the specified CR field
        '''
        cr = self.getRegister(REG_CR)
        cr &= (cr_cmp_mask[crnum])
        cr |= (flags << ((7-crnum) * 4))
        self.setRegister(REG_CR, cr)

    def getXERflags(self):
        '''
        get a particular cr# field
        CR is the control status register
        cr# is one of 8 status register fields within CR, cr0 being the most significant bits in CR
        '''
        xer = self.getRegister(REG_XER)
        flags = (xer & XERFLAGS_MASK) >> XERFLAGS_shift
        return flags

    def setXERflags(self, flags):
        '''
        set XER flags
            SO
            OV
            CA
        '''
        xer = self.getRegister(REG_XER)

        # Mask off the SO, OV, and CA bits
        xer &= 0x1fffffff

        # Now update with the new flags
        xer |= flags << XERFLAGS_shift
        self.setRegister(REG_XER, xer)

    def setOverflow(self, ov=1):
        '''
        set XER flags
            SO
            OV

        This utilty only updates the SO and OV flags without changing the CA flag.
        '''

        # note that the XERFLAGS_* constants are values that indicate the
        # position in the XER of the SO, OV, and CA flags, while the FLAGS_XER_*
        # constants are used to distinguish between the non-XER SO and the XER
        # SO bit positions.

        # Get the current value of SO
        xer = self.getRegister(REG_XER)
        so = xer & XERFLAGS_SO

        # Update SO with incoming OV value
        so |= ov << XERFLAGS_SO_bitnum

        # Save the changes back to XER
        xer = so | ov << XERFLAGS_OV_bitnum | (xer & 0x3fffffff)
        self.setRegister(REG_XER, xer)

    def setCA(self, result, opsize=None):
        '''
        Calculate carry and overflow
        CA flag is always set for addic, subfic, addc, subfc, adde, subfe, addme, subfme, addze, subfze
        '''
        if opsize is None:
            opsize = self.psize

        ca = CARRY(result, opsize)
        self.setRegister(REG_CA, ca)

    def setOEflags(self, result, size, add0, add1, mode=OEMODE_ADDSUBNEG):
        #https://devblogs.microsoft.com/oldnewthing/20180808-00/?p=99445

        # OV = (carrym ^ carrym+1)
        if mode == OEMODE_LEGACY:
            cm = getCarryBitAtX((size*8), add0, add1)
            cm1 = getCarryBitAtX((size*8)-1, add0, add1)
            ov = cm != cm1

        elif mode == OEMODE_ADDSUBNEG:
            cm = getCarryBitAtX((size*8), add0, add1)
            cm1 = getCarryBitAtX((size*8)-1, add0, add1)
            ov = cm != cm1

        else:
            # for mul/div, ov is set if the result cannot be contained in 64bits
            ov = bool(result >> 64)

        self.setOverflow(ov)

        # Return an indication of if overflow was detected
        return ov

    def setFlags(self, result, so=None, crnum=0, opsize=None):
        '''
        easy way to set the flags, reusable by many different instructions
        if SO is None, SO is pulled from the XER register (most often)

        from PowerISA 2.07:
            For all fixed-point instructions in which Rc=1, and for
            addic., andi., and andis., the first three bits of CR Field
            0 (bits 32:34 of the Condition Register) are set by
            signed comparison of the result to zero, and the fourth
            bit of CR Field 0 (bit 35 of the Condition Register) is
            copied from the SO field of the XER. “Result” here
            refers to the entire 64-bit value placed into the target
            register in 64-bit mode, and to bits 32:63 of the 64-bit
            value placed into the target register in 32-bit mode.

        '''
        if opsize is None:
            opsize = self.psize

        if e_bits.is_signed(result, opsize):
            flags = FLAGS_LT
        elif (result & e_bits.u_maxes[opsize]) == 0:
            flags = FLAGS_EQ
        else:
            flags = FLAGS_GT

        if so is None:
            # Get the current value of SO
            xer = self.getRegister(REG_XER)
            so = (xer & XERFLAGS_SO) >> XERFLAGS_SO_bitnum

        flags |= so << FLAGS_SO_bitnum

        self.setCr(flags, crnum)

    def setFloatFlags(self, result, iflags, fpsize):
        assert not isinstance(result, float)

        # See if any of the simple result class values match
        try:
            fflags = FP_FLAGS[fpsize][result]
        except KeyError:
            denormalized = (result & FP_EXP_MASK[fpsize]) == 0
            signed = bool(result & e_bits.sign_bits[fpsize])

            # Set the class based on if the value is normalized/denormalized and
            # the sign bit
            fflags = FP_ORDERED_FLAGS[denormalized][signed]

        # Mask the current C & FPCC bits out of the FPSCR register
        fpscr = self.getRegister(REG_FPSCR)
        fpscr &= ~FPSCRFLAGS_MASK

        # mix in the new flags
        fpscr |= fflags << FPSCRFLAGS_C_FPCC_shift

        self.setRegister(REG_FPSCR, fpscr)


        # Used like setFlags() but specifically for Float instructions that have [.] variants
    def setFloatCr(self):
        fpscr = self.getRegister(REG_FPSCR)
        val = (fpscr & FPSCR_FLOAT_RC_MASK) >> FPSCR_FLOAT_RC_SHIFT
        self.setCr(val, crnum=1)

    def float2decimal(self, value, fpsize=8):
        '''
        Used to convert a python floating point value into an integer
        representation that can be saved into the emulated registers.

        Some of the decimal/integer values produced by python (by calling the
        e_bits.floattodecimel function) do not match the values used on 64-bit
        PowerPC processors. This function handles converting between the
        standard python/envi.bits integer representations of floating point
        values and the values that should be produced to accurately emulate the
        results of PowerPC floating-point instructions.

        If the result should be a single-precision (32-bit) floating point
        value and this is a 64-bit system to convert the floating point value
        accurately it must be converted from a decimal/integer value to a
        double-precision (64-bit) floating point value first. Then mask off the
        lower 29 bits of the fractional portion. For some reason NXP PowerPCs do
        not use standard IEEE754 single-precision floating point
        representations.

        The python NaN values don't match those generated by a PowerPC, any NaN
        integer values need to be adjusted.
        '''
        # Use the emulator pointer size for converting floating point values
        # into their decimal/integer representations. Non-platform sized
        # floating point are handled later.

        float_value = e_bits.floattodecimel(value, fpsize, self.getEndian())

        # If the result is the python version of NaN convert it to the correct
        # PPC QNAN representation
        if self.psize == 8:
            if float_value == FP_DOUBLE_NEG_PYNAN:
                float_value = FP_DOUBLE_NEG_QNAN
            elif float_value == FP_DOUBLE_POS_PYNAN:
                float_value = FP_DOUBLE_POS_QNAN
            elif fpsize == 4:
                # If the float_value is not infinity or NaN and this is a single
                # precision value, mask off the lower 29 bits
                float_value &= PPC_64BIT_SINGLE_PRECISION_MASK
        else:
            if float_value == FP_SINGLE_NEG_PYNAN:
                float_value = FP_SINGLE_NEG_QNAN
            elif float_value == FP_SINGLE_POS_PYNAN:
                float_value = FP_SINGLE_POS_QNAN

        return float_value

    def decimal2float(self, value, fpsize=8):
        '''
        For converting from floating point to decimal there are no special steps
        required. The standard envi.bits.decimeltofloat() results match the
        values seen on a 64-bit NXP PowerPC, and python is able to accurately
        convert the values produced by the above float2decimal() function into
        floating point values without special checks.
        '''
        return e_bits.decimeltofloat(value, fpsize, self.getEndian())

        '''
        PPC stores single precision values as double precision values with the lower
        29 bits masked off.  The solution to this was to do all single precision operations
        as double precision and then mask off the results.  Rounding will have to be accounted for
        in the FPSCR and python math operations will have to be done in 32 bits.  Not sure how to
        make python do that though.
        '''

    def is_denorm16(self, value):
        exp = value & 0x7c00
        fract = value & 0x3ff

        if not exp and fract:
            denorm = True
        else:
            denorm = False
        return denorm

    def is_denorm32(self, value):
        exp = value & 0x7f800000
        fract = value & 0x7fffff

        if not exp and fract:
            denorm = True
        else:
            denorm = False
        return denorm

    def is_denorm64(self, value):
        exp = value & 0x7ff0000000000000
        fract = value & 0xfffffffffffff

        if not exp and fract:
            denorm = True
        else:
            denorm = False
        return denorm


    # Beginning of Instruction methods

    ########################### NOP #############################

    def i_nop(self, op):
        pass

    ########################### Integer Select Instructions #############################

    def i_isel(self, op):
        # The 4th operand is which bit to check in the CR register, but using
        # the MSB as bit 0 because PPC. (use psize of 4 because the CR register
        # is always only 32 bits.
        mask = BITMASK(op.opers[3].bit, psize=4)

        # Doesn't matter what the actual bit or CR is because the if the cr bit
        # is set in the CR then the use rA, otherwise use rB
        if self.getRegister(REG_CR) & mask:
            self.setOperValue(op, 0, self.getOperValue(op, 1))
        else:
            self.setOperValue(op, 0, self.getOperValue(op, 2))

    def i_isellt(self, op):
        # If the CR0 LT flag is set use rA, otherwise use rB
        if self.getCr(0) & FLAGS_LT:
            self.setOperValue(op, 0, self.getOperValue(op, 1))
        else:
            self.setOperValue(op, 0, self.getOperValue(op, 2))

    def i_iselgt(self, op):
        # If the CR0 GT flag is set use rA, otherwise use rB
        if self.getCr(0) & FLAGS_GT:
            self.setOperValue(op, 0, self.getOperValue(op, 1))
        else:
            self.setOperValue(op, 0, self.getOperValue(op, 2))

    def i_iseleq(self, op):
        # If the CR0 EQ flag is set use rA, otherwise use rB
        if self.getCr(0) & FLAGS_EQ:
            self.setOperValue(op, 0, self.getOperValue(op, 1))
        else:
            self.setOperValue(op, 0, self.getOperValue(op, 2))

    ########################### Metric shit-ton of Branch Instructions #############################

    def i_b(self, op):
        '''
        Branch!  no frills.
        '''
        return self.getOperValue(op, 0)

    def i_bl(self, op):
        '''
        branch with link, the basic CALL instruction
        '''
        self.setRegister(REG_LR, op.va + op.size)
        return self.getOperValue(op, 0)

    i_ba = i_b
    i_bla = i_bl

    def i_blr(self, op):
        '''
        blr is actually "ret"
        '''
        return self.getRegister(REG_LR)

    def i_blrl(self, op):
        nextva = op.va + op.size
        lr = self.getRegister(REG_LR)
        self.setRegister(REG_LR, nextva)
        return lr

    def i_bctr(self, op):
        ctr = self.getRegister(REG_CTR)
        return ctr

    def i_bctrl(self, op):
        nextva = op.va + op.size
        ctr = self.getRegister(REG_CTR)
        self.setRegister(REG_LR, nextva)
        return ctr


    # conditional branches....
    def _bc(self, op, tgt, lk=False):
        # always update LR, regardless of the conditions.  odd.
        if lk:
            nextva = op.va + op.size
            self.setRegister(REG_LR, nextva)

        bo = self.getOperValue(op, 0)

        if BO_UNCONDITIONAL(bo):
            return tgt

        if BO_DECREMENT(bo):
            # if tgt is REG_CTR, we can't decrement it...
            if tgt == REG_CTR:
                raise envi.BadOpcode(op)

            ctr = self.getRegister(REG_CTR) - 1
            self.setRegister(REG_CTR, ctr)

            # If CTR is decremented the branch condition depends on the value of
            # CTR
            ctr_ok = BO_CTR_OK(bo, ctr)
        else:
            # If the CTR is not being modified, the CTR condition is marked as
            # false because the branch can now only be taken if the standard
            # condition is met
            ctr_ok = False

        if BO_CONDITIONAL(bo):
            cond = self.getOperValue(op, 1)
            cond_ok = BO_COND_OK(bo, cond)
        else:
            # The normal condition is marked as false because the branch should
            # only be taken if the counter has the desired target value
            cond_ok = False

        # Branch should be taken if either the counter condition or the normal
        # condition are met
        if ctr_ok or cond_ok:
            return tgt
        else:
            return None

    def i_bc(self, op):
        tgt = self.getOperValue(op, 2)
        return self._bc(op, tgt)

    def i_bcl(self, op):
        tgt = self.getOperValue(op, 2)
        return self._bc(op, tgt, lk=True)

    # The simplified mnemonic branch instructions with the AA flag set don't
    # have separate instructions, but the base "b" and "bl" instructions must be
    # defined.
    i_bca = i_bc
    i_bcla = i_bcl

    def i_bclr(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc(op, tgt)

    def i_bclrl(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc(op, tgt, lk=True)

    def i_bcctr(self, op):
        tgt = self.getRegister(REG_CTR)
        return self._bc(op, tgt)

    def i_bcctrl(self, op):
        tgt = self.getRegister(REG_CTR)
        return self._bc(op, tgt, lk=True)

    ####### CR condition-only branches #######

    # utility for handling the simplified mnemonic branch instructions with
    # conditions but on CTR decrementing
    #
    # This is essentially the same as the _bc() function, except that the
    # information normally held in the BO and BI operands is split out into
    # parameters that must be supplied.  This allows this particular function to
    # support the conditional branch simplified mnemonics as efficiently as
    # possible.
    def _bc_simplified_cond_only(self, op, cond, tgt, lk=False):
        # always update LR, regardless of the conditions.  odd.
        if lk:
            nextva = op.va + op.size
            self.setRegister(REG_LR, nextva)

        # If the conditions are met return the target
        if cond:
            return tgt
        else:
            return None

    ## EQ ##

    def i_beq(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_EQ
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_beql(self, op):
        return self.i_beq(op, True)

    def i_beqctr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
        else:
            cond = self.getCr(0) & FLAGS_EQ
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_beqctrl(self, op):
        return self.i_beqctr(op, True)

    def i_beqlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
        else:
            cond = self.getCr(0) & FLAGS_EQ
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_beqlrl(self, op):
        return self.i_beqlr(op, True)

    ## GE ##
    # For BGE check if the LE flag is _not_ set

    def i_bge(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgel(self, op):
        return self.i_bge(op, True)

    def i_bgectr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgectrl(self, op):
        return self.i_bgectr(op, True)

    def i_bgelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgelrl(self, op):
        return self.i_bgelr(op, True)

    ## GT ##

    def i_bgt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_GT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_GT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgtl(self, op):
        return self.i_bgt(op, True)

    def i_bgtctr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_GT
        else:
            cond = self.getCr(0) & FLAGS_GT
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgtctrl(self, op):
        return self.i_bgtctr(op, True)

    def i_bgtlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_GT
        else:
            cond = self.getCr(0) & FLAGS_GT
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bgtlrl(self, op):
        return self.i_bgtlr(op, True)

    ## LE ##
    # For BLE check if the GT flag is _not_ set

    def i_ble(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_blel(self, op):
        return self.i_ble(op, True)

    def i_blectr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_blectrl(self, op):
        return self.i_blectr(op, True)

    def i_blelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_blelrl(self, op):
        return self.i_blelr(op, True)

    ## LT ##

    def i_blt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_LT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_LT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bltl(self, op):
        return self.i_blt(op, True)

    def i_bltctr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_LT
        else:
            cond = self.getCr(0) & FLAGS_LT
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bltctrl(self, op):
        return self.i_bltctr(op, True)

    def i_bltlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_LT
        else:
            cond = self.getCr(0) & FLAGS_LT
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bltlrl(self, op):
        return self.i_bltlr(op, True)

    ## NE ##
    # For BNE check if the EQ flag is _not_ set

    def i_bne(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnel(self, op):
        return self.i_bne(op, True)

    def i_bnectr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnectrl(self, op):
        return self.i_bnectr(op, True)

    def i_bnelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnelrl(self, op):
        return self.i_bnelr(op, True)

    ## NS ##
    # For BNS check if the SO flag is _not_ set

    def i_bns(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnsl(self, op):
        return self.i_bns(op, True)

    def i_bnsctr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnsctrl(self, op):
        return self.i_bnsctr(op, True)

    def i_bnslr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bnslrl(self, op):
        return self.i_bnslr(op, True)

    ## SO ##

    def i_bso(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_SO
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_SO
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bsol(self, op):
        return self.i_bso(op, True)

    def i_bsoctr(self, op, lk=False):
        tgt = self.getRegister(REG_CTR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_SO
        else:
            cond = self.getCr(0) & FLAGS_SO
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bsoctrl(self, op):
        return self.i_bsoctr(op, True)

    def i_bsolr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_SO
        else:
            cond = self.getCr(0) & FLAGS_SO
        return self._bc_simplified_cond_only(op, cond, tgt, lk)

    def i_bsolrl(self, op):
        return self.i_bsolr(op, True)

    ####### CTR decrementing-only branches #######
    # There are no bcctr instructions of this form because CTR cannot be the
    # branch target when it is being modified.

    def _bc_simplified_ctr_only(self, op, ctr_nz, tgt, lk=False):
        ctr = self.getRegister(REG_CTR) - 1
        self.setRegister(REG_CTR, ctr)

        # always update LR, regardless of the conditions.  odd.
        if lk:
            nextva = op.va + op.size
            self.setRegister(REG_LR, nextva)

        # If ctr_nz is True then branch if CTR is not zero
        # If ctr_nz is False then branch if CTR is zero
        if bool(ctr) == ctr_nz:
            return tgt
        else:
            return None

    # target is BD (first operand)

    def i_bdz(self, op):
        tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_only(op, False, tgt)

    def i_bdzl(self, op):
        tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_only(op, False, tgt, lk=True)

    def i_bdnz(self, op):
        tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_only(op, True, tgt)

    def i_bdnzl(self, op):
        tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_only(op, True, tgt, lk=True)

    ## target is LR

    def i_bdzlr(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc_simplified_ctr_only(op, False, tgt)

    def i_bdzlrl(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc_simplified_ctr_only(op, False, tgt, lk=True)

    def i_bdnzlr(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc_simplified_ctr_only(op, True, tgt)

    def i_bdnzlrl(self, op):
        tgt = self.getRegister(REG_LR)
        return self._bc_simplified_ctr_only(op, True, tgt, lk=True)

    ####### CTR decrementing and CR condition branches #######
    # There are no bcctr instructions of this form because CTR cannot be the
    # branch target when it is being modified.

    def _bc_simplified_ctr_and_cond(self, op, ctr_nz, cond, tgt, lk=False):
        ctr = self.getRegister(REG_CTR) - 1
        self.setRegister(REG_CTR, ctr)

        # always update LR, regardless of the conditions.  odd.
        if lk:
            nextva = op.va + op.size
            self.setRegister(REG_LR, nextva)

        # branch if ctr_nz is True and CTR is not zero OR the condition is met
        # branch if ctr_nz is False and CTR is zero OR the condition is met
        if bool(ctr) == ctr_nz or cond:
            return tgt
        else:
            return None

    ## EQ and CTR == 0 ##

    def i_bdzeq(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_EQ
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzeql(self, op):
        return self.i_bdzeq(op, True)

    def i_bdzeqlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
        else:
            cond = self.getCr(0) & FLAGS_EQ
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzeqlrl(self, op):
        return self.i_bdzeqlr(op, True)

    ## EQ and CTR != 0 ##

    def i_bdnzeq(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_EQ
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzeql(self, op):
        return self.i_bdnzeq(op, True)

    def i_bdnzeqlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_EQ
        else:
            cond = self.getCr(0) & FLAGS_EQ
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzeqlrl(self, op):
        return self.i_bdnzeqlr(op, True)

    ## GE and CTR == 0 ##
    # For BGE check if the LT flag is _not_ set

    def i_bdzge(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzgel(self, op):
        return self.i_bdzge(op, True)

    def i_bdzgelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzgelrl(self, op):
        return self.i_bdzgelr(op, True)

    ## GE and CTR != 0 ##

    def i_bdnzge(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzgel(self, op):
        return self.i_bdnzge(op, True)

    def i_bdnzgelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_LT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_LT) == 0
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzgelrl(self, op):
        return self.i_bdnzgelr(op, True)

    ## GT and CTR == 0 ##

    def i_bdzgt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_GT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_GT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzgtl(self, op):
        return self.i_bdzgt(op, True)

    def i_bdzgtlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_GT
        else:
            cond = self.getCr(0) & FLAGS_GT
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzgtlrl(self, op):
        return self.i_bdzgtlr(op, True)

    ## GT and CTR != 0 ##

    def i_bdnzgt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_GT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_GT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzgtl(self, op):
        return self.i_bdnzgt(op, True)

    def i_bdnzgtlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_GT
        else:
            cond = self.getCr(0) & FLAGS_GT
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzgtlrl(self, op):
        return self.i_bdnzgtlr(op, True)

    ## LE and CTR == 0 ##
    # For BLE check if the GT flag is _not_ set

    def i_bdzle(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzlel(self, op):
        return self.i_bdzle(op, True)

    def i_bdzlelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzlelrl(self, op):
        return self.i_bdzlelr(op, True)

    ## LE and CTR != 0 ##

    def i_bdnzle(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzlel(self, op):
        return self.i_bdnzle(op, True)

    def i_bdnzlelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_GT) == 0
        else:
            cond = (self.getCr(0) & FLAGS_GT) == 0
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzlelrl(self, op):
        return self.i_bdnzlelr(op, True)

    ## LT and CTR == 0 ##

    def i_bdzlt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_LT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_LT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzltl(self, op):
        return self.i_bdzlt(op, True)

    def i_bdzltlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_LT
        else:
            cond = self.getCr(0) & FLAGS_LT
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzltlrl(self, op):
        return self.i_bdzltlr(op, True)

    ## LT and CTR != 0 ##

    def i_bdnzlt(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_LT
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_LT
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzltl(self, op):
        return self.i_bdnzlt(op, True)

    def i_bdnzltlr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_LT
        else:
            cond = self.getCr(0) & FLAGS_LT
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzltlrl(self, op):
        return self.i_bdnzltlr(op, True)

    ## NE and CTR == 0 ##
    # For BNE check if the EQ flag is _not_ set

    def i_bdzne(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdznel(self, op):
        return self.i_bdzne(op, True)

    def i_bdznelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdznelrl(self, op):
        return self.i_bdznelr(op, True)

    ## NE and CTR != 0 ##

    def i_bdnzne(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnznel(self, op):
        return self.i_bdnzne(op, True)

    def i_bdnznelr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_EQ) == 0
        else:
            cond = (self.getCr(0) & FLAGS_EQ) == 0
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnznelrl(self, op):
        return self.i_bdnznelr(op, True)

    ## NS and CTR == 0 ##
    # For BNS check if the SO flag is _not_ set

    def i_bdzns(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdznsl(self, op):
        return self.i_bdzns(op, True)

    def i_bdznslr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdznslrl(self, op):
        return self.i_bdznslr(op, True)

    ## NS and CTR != 0 ##

    def i_bdnzns(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 1)
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnznsl(self, op):
        return self.i_bdnzns(op, True)

    def i_bdnznslr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = (self.getOperValue(op, 0) & FLAGS_SO) == 0
        else:
            cond = (self.getCr(0) & FLAGS_SO) == 0
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnznslrl(self, op):
        return self.i_bdnznslr(op, True)

    ## SO and CTR == 0 ##

    def i_bdzso(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_SO
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_SO
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzsol(self, op):
        return self.i_bdzso(op, True)

    def i_bdzsolr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_SO
        else:
            cond = self.getCr(0) & FLAGS_SO
        return self._bc_simplified_ctr_and_cond(op, False, cond, tgt, lk)

    def i_bdzsolrl(self, op):
        return self.i_bdzsolr(op, True)

    ## SO and CTR != 0 ##

    def i_bdnzso(self, op, lk=False):
        # If there are two operands then the first is the CR field to use
        if len(op.opers) == 2:
            cond = self.getOperValue(op, 0) & FLAGS_SO
            tgt = self.getOperValue(op, 1)
        else:
            cond = self.getCr(0) & FLAGS_SO
            tgt = self.getOperValue(op, 0)
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzsol(self, op):
        return self.i_bdnzso(op, True)

    def i_bdnzsolr(self, op, lk=False):
        tgt = self.getRegister(REG_LR)

        # If there is an operands then it is the CR field to use
        if len(op.opers) == 1:
            cond = self.getOperValue(op, 0) & FLAGS_SO
        else:
            cond = self.getCr(0) & FLAGS_SO
        return self._bc_simplified_ctr_and_cond(op, True, cond, tgt, lk)

    def i_bdnzsolrl(self, op):
        return self.i_bdnzsolr(op, True)

    ######################## compare instructions ##########################

    def i_cmpb(self, op):
        # operands: rS, rA, rB
        # Byte-by-byte comparison of rS and rB, if the bytes are equal then the
        # byte in rA is set to 0xFF, otherwise it is set to 0x00.
        ssize = op.opers[0].getWidth(self)
        masks_and_shifts = [(0xFF << i*8, i*8) for i in range(ssize)]

        rS = self.getOperValue(op, 0)
        rB = self.getOperValue(op, 2)

        result = sum(0xFF << s if (rS & m) == (rB & m) else 0 for m, s in masks_and_shifts)
        self.setOperValue(op, 1, result)

    def _cmp(self, op, crnum, a_opidx, b_opidx, opsize):
        # Sign extend the A and B (if necessary) values
        a = e_bits.signed(self.getOperValue(op, a_opidx), opsize)
        b = e_bits.signed(self.getOperValue(op, b_opidx), opsize)

        #c = a - b
        #self.setFlags(c, crnum=crnum)

        if a < b:
            flags = FLAGS_LT
        elif a > b:
            flags = FLAGS_GT
        else:
            flags = FLAGS_EQ

        # Get the current value of SO
        xer = self.getRegister(REG_XER)
        so = (xer & XERFLAGS_SO) >> XERFLAGS_SO_bitnum
        flags |= so << FLAGS_SO_bitnum

        self.setCr(flags, crnum)

    def _cmpl(self, op, crnum, a_opidx, b_opidx, opsize):
        a = e_bits.unsigned(self.getOperValue(op, a_opidx), opsize)
        b = e_bits.unsigned(self.getOperValue(op, b_opidx), opsize)

        #c = a - b
        #self.setFlags(c, crnum=crnum)

        if a < b:
            flags = FLAGS_LT
        elif a > b:
            flags = FLAGS_GT
        else:
            flags = FLAGS_EQ

        # Get the current value of SO
        xer = self.getRegister(REG_XER)
        so = (xer & XERFLAGS_SO) >> XERFLAGS_SO_bitnum
        flags |= so << FLAGS_SO_bitnum

        self.setCr(flags, crnum)

    def _cmp_simplified(self, op, opsize):
        if len(op.opers) == 2:
            # crfD is CR0
            crnum = 0

            # the "A" operand index is 0
            # the "B" operand index is 1
            a_opidx = 0
            b_opidx = 1
        else:
            crnum = op.opers[0].field

            # the "A" operand index is 1
            # the "B" operand index is 2
            a_opidx = 1
            b_opidx = 2
        self._cmp(op, crnum, a_opidx, b_opidx, opsize)

    def _cmpl_simplified(self, op, opsize):
        if len(op.opers) == 2:
            # crfD is CR0
            crnum = 0

            # the "A" operand index is 0
            # the "B" operand index is 1
            a_opidx = 0
            b_opidx = 1
        else:
            crnum = op.opers[0].field

            # the "A" operand index is 1
            # the "B" operand index is 2
            a_opidx = 1
            b_opidx = 2
        self._cmpl(op, crnum, a_opidx, b_opidx, opsize)

    def i_cmpw(self, op):
        self._cmp_simplified(op, opsize=4)

    i_cmpwi = i_cmpw

    def i_cmplw(self, op):
        self._cmpl_simplified(op, opsize=4)

    i_cmplwi = i_cmplw

    def i_cmpd(self, op):
        #if self.psize == 4:
        #    raise InvalidInstruction(mesg='Cannot execute "%r" on %s' % (op, self.getArchName()))
        self._cmp_simplified(op, opsize=8)

    i_cmpdi = i_cmpd

    def i_cmpld(self, op):
        #if self.psize == 4:
        #    raise InvalidInstruction(mesg='Cannot execute "%r" on %s' % (op, self.getArchName()))
        self._cmpl_simplified(op, opsize=8)

    i_cmpldi = i_cmpld

    def _cmp_base(self, op):
        # This non-simplified mnemonic form isn't really used, but it is a valid
        # instruction form so for the emulation call the correct simplified
        # mnemonic emulation function.

        # There are 3 possible operand lists for this instruction, if crfD is
        # 0 then it may be left off, if L is 0 then it can also be left off
        if len(op.opers) == 2:
            # crfD is CR0
            crnum = 0

            # L is 0
            l = 0

            # the "A" operand index is 0
            # the "B" operand index is 1
            a_opidx = 0
            b_opidx = 1
        elif len(op.opers) == 3:
            # the "A" operand index is 1
            # the "B" operand index is 2
            a_opidx = 1
            b_opidx = 2

            if isinstance(op.opers[0], PpcCRegOper):
                # first operand is the crnum
                crnum = op.opers[0].field
                l = 0
            else:
                # first operand is L
                crnum = 0
                l = self.getOperValue(op, 0)
        else:
            crnum = self.opers[0].field
            l = self.getOperValue(op, 1)

            # the "A" operand index is 1
            # the "B" operand index is 2
            a_opidx = 2
            b_opidx = 3

        if l == 0:
            opsize = 4
        else:
            opsize = 8

        return crnum, a_opidx, b_opidx, opsize

    def i_cmp(self, op):
        crnum, a_opidx, b_opidx, opsize = self._cmp_base(op)
        self._cmp(op, crnum, a_opidx, b_opidx, opsize=opsize)

    i_cmpi = i_cmp

    def i_e_cmph(self, op):
        self._cmp(op, op.opers[0].field, 1, 2, opsize=2)

    def i_cmpl(self, op):
        crnum, a_opidx, b_opidx, opsize = self._cmp_base(op)
        self._cmpl(op, crnum, a_opidx, b_opidx, opsize=opsize)

    def i_e_cmphl(self, op):
        self._cmpl(op, op.opers[0].field, 1, 2, opsize=2)

    i_cmpli = i_cmpl

    def i_e_cmp16i(self, op):
        op.opers[1].val = EXTS(op.opers[1].val, 2, 4)
        self._cmp(op, 0, 0, 1, opsize=4)

    def i_e_cmpl16i(self, op):
        op.opers[1].val = EXTZ(op.opers[1].val, 4)
        self._cmpl(op, 0, 0, 1, opsize=4)

    def i_e_cmph16i(self, op):
        self._cmp(op, 0, 0, 1, opsize=2)

    def i_e_cmphl16i(self, op):
        self._cmpl(op, 0, 0, 1, opsize=2)

    ######################## arithmetic instructions ##########################

    def i_add(self, op, oe=False):
        '''
        add
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 + src2

        if oe: self.setOEflags(result, self.psize, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)

    def i_addo(self, op):
        self.i_add(op, oe=True)

    def i_addb(self, op, opsize=1):
        '''
        add signed byte
        '''
        src1 = EXTS(self.getOperValue(op, 1), opsize)
        src2 = EXTS(self.getOperValue(op, 2), opsize)
        result = EXTS(src1 + src2)

        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)

    def i_addbss(self, op, opsize=1):
        '''
        add byte signed saturate
        '''
        src1 = EXTS(self.getOperValue(op, 1), opsize)
        src2 = EXTS(self.getOperValue(op, 2), opsize)
        result = src1 + src2

        if self.setOEflags(result, opsize, src1, src2):
            result = SIGNED_SATURATE(val, opsize)

        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)

    def i_addbu(self, op, opsize=1):
        '''
        add unsigned byte
        '''
        src1 = EXTZ(self.getOperValue(op, 1), opsize)
        src2 = EXTZ(self.getOperValue(op, 2), opsize)
        result = EXTZ(src1 + src2, opsize)

        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)

    def i_addbus(self, op, opsize=1):
        '''
        add byte unsigned saturate
        '''
        src1 = EXTZ(self.getOperValue(op, 1), opsize)
        src2 = EXTZ(self.getOperValue(op, 2), opsize)
        result = src1 + src2


        ov = int(result > e_bits.u_maxes[4])
        if ov:
            result = e_bits.u_maxes[opsize]

        self.setOverflow(ov)
        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)

    def i_addc(self, op, oe=False):
        '''
        add with carry
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 + src2

        if oe: self.setOEflags(result, self.psize, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)
        self.setCA(result)

    def i_addco(self, op):
        self.i_addc(op, oe=True)

    def i_adde(self, op, oe=False):
        ra = self.getOperValue(op, 1)
        rb = self.getOperValue(op, 2)
        ca = self.getRegister(REG_CA)
        result = ra + rb + ca

        if oe: self.setOEflags(result, self.psize, ra, rb + ca)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)
        self.setCA(result)

    def i_addeo(self, op):
        self.i_adde(op, oe=True)

    def i_addh(self, op):
        self.i_addb(op, opsize=2)

    def i_addhss(self, op):
        self.i_addbss(op, opsize=2)

    def i_addhu(self, op):
        self.i_addbu(op, opsize=2)

    def i_addhus(self, op):
        self.i_addbus(op, opsize=2)

    def i_addi(self, op):
        '''
        add immediate
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 + src2

        self.setOperValue(op, 0, result)

    def i_addic(self, op):
        '''
        add immediate carry
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 + src2

        if op.iflags & IF_RC: self.setFlags(result)

        self.setOperValue(op, 0, result)
        self.setCA(result)

    def i_addis(self, op):
        '''
        add immediate shifted
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) << 16
        result = src1 + src2

        self.setOperValue(op, 0, result)

    def i_addme(self, op, oe=False):
        '''
        add minus one extended
        update flags (if IF_RC)
        '''
        src1 = self.getOperValue(op, 1)
        ca = self.getRegister(REG_CA)
        src2 = 0xffff_ffff_ffff_ffff + ca
        result = src1 + src2

        if oe: self.setOEflags(result, self.psize, src1, src2)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)
        self.setCA(result)

    def i_addmeo(self, op):
        self.i_addme(op, oe=True)

    def i_addw(self, op):   # CAT_64
        self.i_addb(op, opsize=4)

    def i_addwss(self, op):  # CAT_64
        self.i_addbss(op, opsize=4)

    def i_addwu(self, op):   # CAT_64
        self.i_addbu(op, opsize=4)

    def i_addwus(self, op):   # CAT_64
        self.i_addbus(op, opsize=4)

    def i_addze(self, op, oe=False):
        src1 = self.getOperValue(op, 1)
        ca = self.getRegister(REG_CA)
        result = src1 + ca

        if oe: self.setOEflags(result, self.psize, src1, ca)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)
        self.setCA(result)

    def i_addzeo(self, op):
        self.i_addze(op, oe=True)

    def i_se_add(self, op, oe=False):
        '''
        add
        '''
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        result = src1 + src2

        self.setOperValue(op, 0, result)

    def i_e_add2i(self, op):
        reg = self.getOperValue(op, 0)
        imm = EXTS(self.getOperValue(op, 1), 2, 4)
        result = reg + imm
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_e_add2is(self, op):
        reg = self.getOperValue(op, 0)
        imm = self.getOperValue(op, 1) << 16
        self.setOperValue(op, 0, reg + imm)

    def i_se_not(self, op):
        result = ONES_COMP(self.getOperValue(op, 0), self.getRegisterWidth(REG_R0))
        self.setOperValue(op, 0, result)

    def i_and(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 & src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_se_and(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        result = src1 & src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_andc(self, op):
        '''
        and "complement"
        '''
        src1 = self.getOperValue(op, 1)
        src2 = COMPLEMENT(self.getOperValue(op, 2), self.psize)
        result = src1 & src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_se_andc(self, op):
        '''
        and "complement"
        '''
        src1 = self.getOperValue(op, 0)
        src2 = COMPLEMENT(self.getOperValue(op, 1), self.psize)
        result = src1 & src2

        self.setOperValue(op, 0, result)

    i_andi = i_and

    def i_e_and2i(self, op):
        reg = self.getOperValue(op, 0)
        imm = EXTZ(self.getOperValue(op, 1), 4)
        result = reg & imm
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_andis(self, op):
        '''
        and immediate shifted
        '''
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) << 16
        result = src1 & src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)


    def i_e_and2is(self, op):
        reg = self.getOperValue(op, 0)
        imm = self.getOperValue(op, 1) << 16
        result = reg & imm
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_nand(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = COMPLEMENT(src1 & src2, self.psize)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_not(self, op):
        '''
        simplified form of nor
        '''
        src1 = self.getOperValue(op, 1)
        result = COMPLEMENT(src1, self.psize)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_nor(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = COMPLEMENT(src1 | src2, self.psize)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_not(self, op):
        src = self.getOperValue(op, 1)
        result = COMPLEMENT(src, self.psize)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_or(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 | src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_se_or(self, op):
        src1 = self.getOperValue(op, 0)
        src2 = self.getOperValue(op, 1)
        result = src1 | src2

        self.setOperValue(op, 0, result)

    def i_orc(self, op):
        src0 = self.getOperValue(op, 1)
        src1 = COMPLEMENT(self.getOperValue(op, 2), self.psize)
        result = src0 | src1

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    i_ori = i_or

    def i_e_or2i(self, op):
        reg = self.getOperValue(op, 0)
        imm = EXTZ(self.getOperValue(op, 1), 4)
        self.setOperValue(op, 0, reg | imm)

    def i_oris(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) << 16
        result = src1 | src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_e_or2is(self, op):
        reg = self.getOperValue(op, 0)
        imm = self.getOperValue(op, 1) << 16
        self.setOperValue(op, 0, reg | imm)

    i_miso = i_nop

    def i_divd(self, op, opsize=8, oe=False):
        ra = self.getOperValue(op, 1)
        dividend = e_bits.signed(ra, opsize)
        rb = self.getOperValue(op, 2)
        divisor = e_bits.signed(rb, opsize)

        # integer division overflow check, do the divide by 0 check separately
        # from the overflow (0x8000... / -1) check because we can, and also
        # because that allows this function to be re-used for the divw
        # instructions

        if divisor == 0:
            if oe:
                ov = 1

            # Result is undefined, actual hardware passes '0' to ra register
            quotient = 0

        else:
            quotient = dividend // divisor

            # Now check if that operation would overflow the available register
            # size
            if ra == e_bits.sign_bits[opsize] and divisor == -1:
                if oe:
                    ov = 1
                # If the opsize is the current machine pointer size, set the
                # quotient to the "saturate" negative value, otherwise just
                # leave the quotient as-is.  This is for the divw instruction
                # divW has an opsize of 4
                if opsize == self.psize:
                    quotient = _ppc_signed_saturate_results[opsize][1]


            else:
                ov = 0
        if oe:
            self.setOverflow(ov)

        if op.iflags & IF_RC:
            self.setFlags(quotient)
            # if oe:
            #     self.setOverflow(ov)

        self.setOperValue(op, 0, quotient)

    def i_divdo(self, op):
        self.i_divd(op, oe=True)

    def i_divdu(self, op, opsize=8, oe=False):
        ra = self.getOperValue(op, 1)
        dividend = e_bits.unsigned(ra, opsize)
        rb = self.getOperValue(op, 1)
        divisor = e_bits.unsigned(rb, opsize)

        if divisor == 0:
            ov = 1
            # Result is undefined, use the "saturate" style values described in
            # the divwu instruction
            quotient = e_bits.u_maxes[opsize]
        else:
            ov = 0
            quotient = dividend // divisor

        if oe: self.setOverflow(ov)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, quotient)

    def i_divduo(self, op):
        self.i_divd(op, oe=True)

    def i_divwo(self, op):
        self.i_divd(op, opsize=4, oe=True)

    def i_divwe(self, op, oe=False):
        # This one gets weird
        ra = self.getOperValue(op, 1)
        dividend = e_bits.signed(ra, 4) << 32
        rb = self.getOperValue(op, 1)
        divisor = e_bits.signed(rb, 4)

        if divisor == 0:
            ov = 1
            # Result is undefined, use the "saturate" style values described in
            # the divw instruction
            signed = e_bits.is_signed(dividend, 4)
            quotient = _ppc_signed_saturate_results[4][signed]
        elif ra == e_bits.sign_bits[4] and divisor == -1:
            ov = 1
            quotient = _ppc_signed_saturate_results[4][1]
        else:
            quotient = dividend // divisor

            # Check if the quotient is too small or large for a valid 4-byte
            # value.
            signed = e_bits.is_signed(quotient, 8)
            msb = BIT(quotient, 33)
            if (signed and not msb) or (not signed and msb):
                ov = 1
                quotient = SIGNED_SATURATE(quotient, 4)

        if oe: self.setOverflow(ov)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, quotient)

    def i_divweo(self, op):
        self.i_divwe(op, oe=True)

    def i_divweu(self, op, oe=False):
        # This one gets weird
        ra = self.getOperValue(op, 1)
        dividend = e_bits.unsigned(ra, 4) << 32
        rb = self.getOperValue(op, 1)
        divisor = e_bits.unsigned(rb, 4)

        if divisor == 0:
            ov = 1
            quotient = e_bits.u_maxes[4]
        else:
            quotient = dividend // divisor

            # Do the unsigned saturate check for 4 bytes
            ov = int(quotient > e_bits.u_maxes[4])

            if ov:
                quotient = e_bits.u_maxes[4]

        if oe: self.setOverflow(ov)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, quotient)

    def i_divweuo(self, op):
        self.i_divweu(op, oe=True)

    ########################## FLOAT INSTRUCTIONS ################################

    # TODO: In theory MSR[FP] == 0 should cause a floating-point unavailable
    # interrupt, but when finding valid source we don't want that to happen.

    # Float Helper functions:

    def denorm(value):
        is_denorm = False
        if value & 0x7f000000 == False:
            if value & 0xffffff:
                is_denorm = True
        return is_denorm

    def CnvtI32ToFP32(v, signed, fractional):  # upper_lower will only ever be "low" with embedded
        result = 0
        if v == 0:
            result = 0
            self.setRegister(REG_SPEFSCR_FG, 0)
            self.setRegister(REG_SPEFSCR_FX, 0)
            return

        else:
            if signed == True:
                v_sign = v & 0x80000000
            if fractional == True:
                max_exp = 127
                if signed == False:
                    max_exp = 126
            else:
                max_exp = 0x9E

            sc = 0

            while (v & 0x80000000) == 0:
                v = v << 1
                sc = sc + 1
            v = v >> sc
            v = v & ~(v_sign)
            result = result | (max_exp - sc) << 23
            guard = (v & 800000) >> 23
            if v & 0x7f000000:
                sticky = 1
            else:
                sticky = 0
            self.setRegister(REG_SPEFSCR_FG, guard)
            self.setRegister(REG_SPEFSCR_FX, sticky)
            if guard | sticky:
                self.setRegister(REG_SPEFSCR_FINXS, 1)

            result = (v & 0x007FFFFF) | v_sign
            return result #rounding still needs tobe taken care of





    def i_fabs(self, op, fpsize=8):
        frB = self.getOperValue(op, 1)

        result = frB & ~e_bits.sign_bits[op.opers[0].getWidth(self)]

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fdiv(self, op, fpsize=8):
        frA = self.getOperValue(op, 1)
        frB = self.getOperValue(op, 2)

        dividend = self.decimal2float(frA)
        divisor = self.decimal2float(frB)

        if divisor == 0:
            self.setRegister(REG_FPSCR_FX, 1)
            self.setRegister(REG_FPSCR_ZX, 1)
            fresult = 0

        else:
            fresult = dividend / divisor

        result = self.float2decimal(fresult)

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)

        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fdivs(self,op):
        self.i_fdiv(op,fpsize=4)

    def i_fadd(self, op, fpsize=8):
        frA = self.getOperValue(op, 1)
        frB = self.getOperValue(op, 2)

        addend1 = self.decimal2float(frA)
        addend2 = self.decimal2float(frB)
        result = self.float2decimal(addend1 + addend2)

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fadds(self, op):
        self.i_fadd(op, fpsize=4)

    def i_fsub(self, op, fpsize=8):
        frA = self.getOperValue(op, 1)
        frB = self.getOperValue(op, 2)

        minuend = self.decimal2float(frA)
        subtrahend = self.decimal2float(frB)

        result = self.float2decimal(minuend - subtrahend)

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fsubs(self, op):
        self.i_fsub(op, fpsize=4)

    def i_fmadd(self, op, fpsize=8):
        frD = self.getOperValue(op, 0)
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)
        frB = self.getOperValue(op, 3)

        multiplier = self.decimal2float(frA)
        multiplicand = self.decimal2float(frC)
        addend = self.decimal2float(frB)

        result = self.float2decimal(((multiplier * multiplicand) + addend), fpsize=8)

        if fpsize == 4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fmadds(self, op):
        self.i_fmadd(op, fpsize=4)

    def i_fmsub(self, op, fpsize=8):
        frD = self.getOperValue(op, 0)
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)
        frB = self.getOperValue(op, 3)

        multiplier = self.decimal2float(frA)
        multiplicand = self.decimal2float(frC)
        subtrahend = self.decimal2float(frB)

        result = self.float2decimal(((multiplier * multiplicand) - subtrahend), fpsize=8)

        if fpsize == 4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fmsubs(self, op):
        self.i_fmsub(op, fpsize=4)

    def i_fmul(self, op, fpsize=8):
        frD = self.getOperValue(op, 0)
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)

        multiplier = self.decimal2float(frA)
        multiplicand = self.decimal2float(frC)

        fresult = (multiplier * multiplicand)

        result = self.float2decimal(fresult)

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fmuls(self, op):
        self.i_fmul(op, fpsize=4)

    def i_fnabs(self, op, fpsize=8):
        frB = self.getOperValue(op, 1)

        result = frB | e_bits.sign_bits[fpsize]

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fneg(self, op, fpsize=8):
        frB = self.getOperValue(op, 1)

        result = frB ^ 0x8000000000000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fnmadd(self, op, fpsize=8):
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)
        frB = self.getOperValue(op, 3)

        multiplier = self.decimal2float(frA)
        multiplicand = self.decimal2float(frC)
        addend1 = self.decimal2float(frB)

        result = self.float2decimal(-1 * ((multiplier * multiplicand) + addend1))

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fnmadds(self, op):
        self.i_fnmadd(op, fpsize=4)

    def i_fnmsub(self, op, fpsize=8):
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)
        frB = self.getOperValue(op, 3)

        multiplier = self.decimal2float(frA)
        multiplicand = self.decimal2float(frC)
        subtrahend = self.decimal2float(frB)

        result = self.float2decimal(-1 * ((multiplier * multiplicand) - subtrahend))

        if fpsize ==4:
            result = result & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fnmsubs(self, op):
        self.i_fnmsub(op, fpsize=4)

    def i_fmr(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_mffs(self, op, fpsize=8):
        self.setOperValue(op, 0, self.getRegister(REG_FPSCR))
        if op.iflags & IF_RC: self.setFloatCr()

    def i_mtfs(self, op, fpsize=8):
        self.setOperValue(op, 0, self.getRegister(REG_FPSCR))
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fcmpu(self, op):
        frA = self.getOperValue(op, 1)
        frB = self.getOperValue(op, 2)

        a = self.decimal2float(frA)
        b = self.decimal2float(frB)

        if (frA or frB) in FNAN_ALL_TUP:
            c = 0b0001
            if (frA or frB) in FNAN_SNAN_TUP:
                self.setRegister(REG_FPSCR_VXSNAN, 1)

        else:
            if a > b:
                c = 0b0100
            elif a < b:
                c = 0b1000
            else:
                c = 0b0010

        self.setRegister(REG_FPCC, c)
        self.setOperValue(op, 0, c)

    def i_fcmpo(self, op):
        frA = self.getOperValue(op, 1)
        frB = self.getOperValue(op, 2)

        a = self.decimal2float(frA)
        b = self.decimal2float(frB)

        if (frA or frB) in FNAN_ALL_TUP:
            c = 0b0001
            if (frA or frB) in FNAN_SNAN_TUP:
                self.setRegister(REG_FPSCR_VXSNAN, 1)
                if self.getRegister(REG_FPSCR_VE) == 0:
                    self.setRegister(REG_FPSCR_VXVC, 1)
            elif (frA or frB) in FNAN_QNAN_TUP:
                self.setRegister(REG_FPSCR_VXVC, 1)
        else:
            if a > b:
                c = 0b0100
            elif a < b:
                c = 0b1000
            else:
                c = 0b0010

        self.setRegister(REG_FPCC, c)
        self.setOperValue(op, 0, c)

    def i_fctid(self, op, fpsize=8, rn=None):
        # TODO how to do rounding? issue #87 (FPSCR[RN])
        if rn is None:
            rn = self.getRegister(REG_FPSCR_RN)

        frD = self.getOperValue(op, 0)
        frB = self.getOperValue(op, 1)

        if frB in FNAN_ALL_TUP:
            result = FDNZ
            self.setRegister(REG_FPSCR_VXCVI, 1)
            if frB in FNAN_SNAN_TUP:
                self.setRegister(REG_FPSCR_VXSAN, 1)
        else:
            result = int(self.decimal2float(frB))
            if result > (2**63-1):
                result = 0x7FFF_FFFF_FFFF_FFFF
                self.setRegister(FPSCR_VXCVI, 1)

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fctidz(self, op):
        self.i_fctid(op, rn=1)

    def i_fctiw(self, op):
        self.i_fctid(op, fpsize=4, rn=None)

    def i_fctiwz(self, op):
        self.i_fctiw(op, fpsize=4, rn=1)

    def i_fres(self, op, fpsize=8): # Math is wrong on this one.  Python does 64 bit math.
        frD = self.getOperValue(op, 0)
        frB = self.getOperValue(op, 1)

        result = e_bits.floattodecimel(1/e_bits.decimeltofloat(frB)) & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_frsp(self, op): # needs rounding work.  Issue #87 made with FPSCR
        frD = self.getOperValue(op, 0)
        frB = self.getOperValue(op, 1)

        result = self.decimal2float(self.float2decimal(frB)) & 0xffffffffe0000000

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fsel(self, op):
        frA = self.getOperValue(op, 1)
        frC = self.getOperValue(op, 2)
        frB = self.getOperValue(op, 3)

        if frA >= 0.0 and frA not in [FNAN_ALL_TUP]:
            result = frC
        else:
            result = frB

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()


    ########################## LOAD/STORE INSTRUCTIONS ################################

    def _load_signed(self, op, fpsize=8):
        self.setOperValue(op, 0, e_bits.signed(self.getOperValue(op, 1), op.opers[1].getWidth(self)))

    def _load_signed_update(self, op, fpsize=8):
        addr = self.getOperAddr(op, 1)
        self._load_signed(op)
        op.opers[1].updateReg(op, self, addr)

    def _load_unsigned(self, op, fpsize=8):
        self.setOperValue(op, 0, self.getOperValue(op, 1))

    def _load_unsigned_update(self, op, fpsize=8):
        addr = self.getOperAddr(op, 1)
        self._load_unsigned(op)
        op.opers[1].updateReg(op, self, addr)

    def _single_f_load(self, op):
        val = self.getOperValue(op, 1)
        fval = self.float2decimal(self.decimal2float(val, 4), self.psize)
        self.setOperValue(op, 0, fval)

    def _single_f_load_update(self, op):
        addr = self.getOperAddr(op, 1)
        val = self.getOperValue(op, 1)
        fval = self.float2decimal(self.decimal2float(val, 4), self.psize)
        op.opers[1].updateReg(op, self, addr)
        self.setOperValue(op, 0, fval)

    i_lha = _load_signed
    i_lwa = _load_signed
    i_lhax = _load_signed
    i_lwax = _load_signed

    i_lhau = _load_signed_update
    i_lhaux = _load_signed_update
    i_lwaux = _load_signed_update

    i_lbz = _load_unsigned
    i_lhz = _load_unsigned
    i_lwz = _load_unsigned
    i_ld = _load_unsigned
    i_lbzx = _load_unsigned
    i_lhzx = _load_unsigned
    i_lwzx = _load_unsigned
    i_ldx = _load_unsigned

    i_lbzu = _load_unsigned_update
    i_lhzu = _load_unsigned_update
    i_lwzu = _load_unsigned_update
    i_ldu = _load_unsigned_update
    i_lbzux = _load_unsigned_update
    i_lhzux = _load_unsigned_update
    i_lwzux = _load_unsigned_update
    i_ldux = _load_unsigned_update
    i_lfdux = _load_unsigned_update
    i_lfdu = _load_unsigned_update

    i_lfd = _load_signed
    i_lfddx = _load_signed
    i_lfdx = _load_signed

    i_lfdu = _load_signed_update
    i_lfdux = _load_signed_update

    i_lfs = _single_f_load
    i_lfsu = _single_f_load_update
    i_lfsux = _single_f_load_update
    i_lfsx = _single_f_load


    ####### load/store multiple words #######

    def i_lmw(self, op):
        op.opers[1].tsize = 4
        startreg = op.opers[0].reg

        startaddr = self.getOperAddr(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            word = self.readMemValue(startaddr + offset, 4)
            self.setRegister(regidx, word)
            offset += 4

    def i_stmw(self, op):
        op.opers[1].tsize = 4
        startreg = op.opers[0].reg

        startaddr = self.getOperAddr(op, 1)

        offset = 0
        for regidx in range(startreg, 32):
            word = self.getRegister(regidx)
            self.writeMemValue(startaddr + offset, word & 0xffffffff, 4)
            offset += 4

    def _load_volatile_list(self, op, regs):
        startaddr = self.getOperAddr(op, 0)
        for index, regidx in enumerate(regs):
            self.setRegister(regidx, self.readMemValue(startaddr + (index * 4), 4))

    def i_e_ldmvgprw(self, op): self._load_volatile_list(op, [0] + list(range(3, 13)))
    def i_e_ldmvsprw(self, op): self._load_volatile_list(op, (REG_CR, REG_LR, REG_CTR, REG_XER))
    def i_e_ldmvsrrw(self, op): self._load_volatile_list(op, (REG_SRR0, REG_SRR1))
    def i_e_ldmvcsrrw(self, op): self._load_volatile_list(op, (REG_CSRR0, REG_CSRR1))
    def i_e_ldmvdsrrw(self, op): self._load_volatile_list(op, (REG_DSRR0, REG_DSRR1))

    def _store_volatile_list(self, op, regs):
        startaddr = self.getOperAddr(op, 0)
        for index, regidx in enumerate(regs):
            self.writeMemValue(startaddr + (index * 4), self.getRegister(regidx) & 0xffffffff, 4)

    def i_e_stmvgprw(self, op): self._store_volatile_list(op, [0] + list(range(3, 13)))
    def i_e_stmvsprw(self, op): self._store_volatile_list(op, (REG_CR, REG_LR, REG_CTR, REG_XER))
    def i_e_stmvsrrw(self, op): self._store_volatile_list(op, (REG_SRR0, REG_SRR1))
    def i_e_stmvcsrrw(self, op): self._store_volatile_list(op, (REG_CSRR0, REG_CSRR1))
    def i_e_stmvdsrrw(self, op): self._store_volatile_list(op, (REG_DSRR0, REG_DSRR1))

    ####### Store #######

    def _store_signed(self, op):
        self.setOperValue(op, 1, self.getOperValue(op, 0))

    def _store_signed_update(self, op):
        self._store_signed(op)
        op.opers[1].updateReg(op, self)

    def i_stfiwx(self, op):
        self.setOperValue(op, 1, (self.getOperValue(op, 0) & 0xffffffff))

    def i_stfs(self, op):
        # Convert the value to be stored to a "PPC single precision float"
        frS = self.float2decimal(self.getOperValue(op, 0), fpsize=4)

        # Now convert this floating point value to an actual 32-bit single
        # precision value for storing into memory.
        value = e_bits.floattodecimel(frS, size=4, endian=self.getEndian())
        self.setOperValue(op, 1, value)

    def i_stfsu(self, op):
        self.i_stfs(op)
        op.opers[1].updateReg(op, self)

    i_stb = _store_signed
    i_sth = _store_signed
    i_stw = _store_signed
    i_std = _store_signed
    i_stbx = _store_signed
    i_sthx = _store_signed
    i_stwx = _store_signed
    i_stdx = _store_signed

    i_stbu = _store_signed_update
    i_sthu = _store_signed_update
    i_stwu = _store_signed_update
    i_stdu = _store_signed_update
    i_stbux = _store_signed_update
    i_sthux = _store_signed_update
    i_stwux = _store_signed_update
    i_stdux = _store_signed_update

    i_stfd = _store_signed
    i_stfddx = _store_signed
    i_stfdx = _store_signed

    i_stfdu = _store_signed_update
    i_stfdux = _store_signed_update

    i_stfddx = i_stfdx
    i_stfdepx = i_stfdx

    ########################## MOVE FROM/TO INSTRUCTIONS ################################

    def i_mov(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, src)
        if op.iflags & IF_RC: self.setFlags(src)

    def i_mfmsr(self, op):
        src = self.getRegister(REG_MSR)
        self.setOperValue(op, 0, src)

    def i_mtmsr(self, op):
        src = self.getOperValue(op, 0)
        self.setRegister(REG_MSR, src)

    def i_mfspr(self, op):
        '''
        Move From SPR
        If any Read Handlers have been added to this Emu, they will be called
        *after* reading the value.
        '''
        src = self.getOperValue(op, 1)

        spr = op.opers[1].reg
        spr_read_hdlr = self.spr_read_handlers.get(spr)
        if spr_read_hdlr is not None:
            hdlr_src = spr_read_hdlr(self, op)
            if hdlr_src is not None:
                src = hdlr_src

        self.setOperValue(op, 0, src)

    def i_mtspr(self, op):
        '''
        Move To SPR
        If any Write Handlers have been added to this Emu, they will be called
        *after* updating the value.
        '''
        src = self.getOperValue(op, 1)

        spr = op.opers[0].reg
        spr_write_hdlr = self.spr_write_handlers.get(spr)
        if spr_write_hdlr is not None:
            hdlr_src = spr_write_hdlr(self, op)
            if hdlr_src is not None:
                src = hdlr_src

        self.setOperValue(op, 0, src)

    ########################## Special case MT/F instructions ################################

    # The PMR, TMR, DCR, and TB read/write instructions just duplicate
    # what the mtspr/mfspr functions do

    i_mtpmr = i_mtspr
    i_mttmr = i_mtspr
    i_mtdcr = i_mtspr

    i_mftbu = i_mfspr
    i_mfpmr = i_mfspr
    i_mftmr = i_mfspr
    i_mfdcr = i_mfspr

    def i_mcrf(self, op):
        # Move one CR field to another
        crS = self.getOperValue(op, 1)
        self.setOperValue(op, 0, crS)

    def i_mtcrf(self, op):
        # Operand 1 is an 8-bit value where each bit indicates if a cr field is
        # moved from rS to the CR
        rS = self.getOperValue(op, 1)
        crm = self.getOperValue(op, 0)
        cr = self.getRegister(REG_CR)

        mask = sum(cr_mask[i] for i in range(8) if crm & envi.bits.b_masks[i])
        value = (cr & ~mask) | (rS & mask)

        self.setRegister(REG_CR, value)

    def i_mfcr(self, op):
        cr = self.getRegister(REG_CR)
        self.setOperValue(op, cr)

    def i_mtocrf(self, op):
        # The operand order is reversed from mtcrf, but otherwise it's the same.
        # In theory mtocrf/mfocrf are supposed to have only 1 CR field
        # specified, and the result is undefined if more than one field is
        # specified, but we can just support all of them.
        rS = self.getOperValue(op, 0)
        crm = self.getOperValue(op, 1)
        cr = self.getRegister(REG_CR)

        mask = sum(cr_mask[i] for i in range(8) if crm & envi.bits.b_masks[i])
        value = (cr & ~mask) | (rS & mask)

        self.setRegister(REG_CR, value)

    def i_mfocrf(self, op):
        rD = self.getOperValue(op, 0)
        crm = self.getOperValue(op, 1)
        cr = self.getRegister(REG_CR)

        mask = sum(cr_mask[i] for i in range(8) if crm & envi.bits.b_masks[i])
        value = (rD & ~mask) | (cr & mask)

        self.setOperValue(op, 0, value)

    def i_mcrxr(self, op):
        # Move XER[32-35] to crfD, and clear XER
        xer_flags = self.getXERflags()
        self.setOperValue(op, 0, xer_flags)
        self.setXERflags(0)

    def i_mtfsb0(self, op):
        crb = self.getOperValue(op, 0)
        # this only masks the lower 4 bytes of FPSCR
        mask = BITMASK(crb, psize=4)
        fpscr = self.getRegister(REG_FPSCR)
        value = fpscr & ~mask
        self.setRegister(REG_FPSCR, value)

        if op.iflags & IF_RC: self.setFloatCr()

    def i_mtfsb1(self, op):
        crb = self.getOperValue(op, 0)
        # this only masks the lower 4 bytes of FPSCR
        mask = BITMASK(crb, psize=4)
        fpscr = self.getRegister(REG_FPSCR)
        value = fpscr | mask
        self.setRegister(REG_FPSCR, value)

        if op.iflags & IF_RC: self.setFloatCr()

    def i_mtfsf(self, op):
        # Like mtcrf
        frB = self.getOperValue(op, 1)
        fm = self.getOperValue(op, 0)
        fpscr = self.getRegister(REG_FPSCR)

        mask = sum(cr_mask[i] for i in range(8) if fm & envi.bits.b_masks[i])
        value = (fpscr & ~mask) | (frB & mask)

        self.setRegister(REG_FPSCR, value)

        if op.iflags & IF_RC: self.setFloatCr()

    def i_mtfsfi(self, op):
        crfD = op.opers[0].field
        uimm = op.getOperValue(op, 2)
        fpscr = self.getRegister(REG_FPSCR)

        mask = cr_mask[crfD]
        value = (fpscr & ~mask) | ((uimm << ((7-crfD) * 4)) & mask)

        self.setRegister(REG_FPSCR, value)

        if op.iflags & IF_RC: self.setFloatCr()

    i_li = i_mov
    i_mr = i_mov

    ######################## TLB/MMU instructions ##########################

    i_tlbilx = i_nop
    i_tlbsync = i_nop
    i_tlbivax = i_nop
    i_tlbsx = i_nop
    i_tlbre = i_nop
    i_tlbwe = i_nop

    ######################## utility instructions ##########################

    def i_lis(self, op):
        src = self.getOperValue(op, 1)
        self.setOperValue(op, 0, (src<<16))
        # technically this is incorrect, but since we disassemble wrong, we emulate wrong.
        #self.setOperValue(op, 0, (src))

    def i_e_lis(self, op):
        self.setOperValue(op, 0, self.getOperValue(op, 1) << 16)

    def i_cntlzw(self, op):
        rs = self.getOperValue(op, 1)
        result = CLZ(rs, psize=4)
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_cntlzd(self, op):   # CAT_64
        rs = self.getOperValue(op, 1)
        result = CLZ(rs, psize=8)
        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result)

    ######################## rotate/shift instructions ##########################

    def i_rldcl(self, op):
        rb = self.getOperValue(op, 1)
        rs = self.getOperValue(op, 1)

        n = rb & 0x3f
        r = ROTL64(rs, n)
        b = self.getOperValue(op, 3)
        k = MASK(b, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rldcr(self, op):
        rb = self.getOperValue(op, 1)
        rs = self.getOperValue(op, 1)

        n = rb & 0x3f
        r = ROTL64(rs, n)
        e = self.getOperValue(op, 3)
        k = MASK(0, e)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rldic(self, op):
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2)
        r = ROTL64(rs, n)
        b = self.getOperValue(op, 3)
        k = MASK(b, ONES_COMP(n, 6))
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rldicl(self, op):
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2)
        r = ROTL64(rs, n)
        b = self.getOperValue(op, 3)
        k = MASK(b, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rldicr(self, op):
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2)
        r = ROTL64(rs, n)
        e = self.getOperValue(op, 3)
        k = MASK(0, e)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rldimi(self, op):
        ra = self.getOperValue(op, 0)
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2)
        r = ROTL64(rs, n)
        b = self.getOperValue(op, 3)
        k = MASK(b, ~n)
        result = (r & k) | (ra & ~k)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rlwimi(self, op):
        ra = self.getOperValue(op, 0)
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2) & 0x1f
        b = self.getOperValue(op, 3) + 32
        e = self.getOperValue(op, 4) + 32
        r = ROTL32(e_bits.unsigned(rs, 4), n)
        k = MASK(b, e)
        result = (r & k) | (ra & ~k)

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_rlwnm(self, op):
        rs = self.getOperValue(op, 1)

        n = self.getOperValue(op, 2) & 0x1f
        b = self.getOperValue(op, 3) + 32
        e = self.getOperValue(op, 4) + 32
        r = ROTL32(e_bits.unsigned(rs, 4), n)
        k = MASK(b, e)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    i_rlwinm = i_rlwnm

    def i_e_rlw(self, op):
        src = self.getOperValue(op, 1)
        rot = self.getOperValue(op, 2) & 0x1f
        result = ROTL32(e_bits.unsigned(src, 4), rot)
        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_sld(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)

        n = rb & 0x3f
        r = ROTL64(rs, n)
        k = 0 if rb & 0x40 else MASK(0, 63-n)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_slw(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)

        n = rb & 0x1f
        r = ROTL32(e_bits.unsigned(rs, 4), n)
        k = 0 if rb & 0x20 else MASK(32, 63-n)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_se_slw(self, op):
        rb = self.getOperValue(op, 1)
        rs = self.getOperValue(op, 0)

        n = rb & 0x1f
        r = ROTL32(e_bits.unsigned(rs, 4), n)
        k = 0 if rb & 0x20 else MASK(32, 63-n)
        result = r & k

        self.setOperValue(op, 0, result)

    def i_e_slwi(self, op):
        rb = self.getOperValue(op, 0)
        rs = self.getOperValue(op, 1)
        n = self.getOperValue(op, 2)

        r = ROTL32(e_bits.unsigned(rs, 4), n)
        k = 0 if rb & 0x20 else MASK(32, 63-n)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_srad(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        n = rb & 0x3f

        # Per testing on the real hardware:
        # - If bit 57 of rB is set, then the mask (k) is set to 0 and the result saved
        #   to rA will either be 0 (if rS is unsigned) or -1 (if rS is signed)
        # - If the value in rB is larger than 63, but bit 57 is not set (such as a value of 128)
        #   then bits 0:56 are just ignored and the mask is generated using bits 58:63.

        r = ROTL64(rs, 64-n)
        k = 0 if rb & 0x40 else MASK(n, 63)
        s = e_bits.is_signed(rs, 8)

        s_bits = (0, 0xFFFF_FFFF_FFFF_FFFF)[s]

        result = (r & k) | (s_bits & ~k)

        ca = s and bool(r & ~k)

        self.setRegister(REG_CA, ca)

        self.setOperValue(op, 0, result)

        if op.iflags & IF_RC: self.setFlags(result)

    def i_sradi(self, op):
        n = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        r = ROTL64(rs, 64-n)
        k = MASK(n, 63)
        s = e_bits.is_signed(rs, 8)
        s_bits = (0, 0xFFFF_FFFF_FFFF_FFFF)[s]

        result = (r & k) | (s_bits & ~k)

        if op.iflags & IF_RC: self.setFlags(result)

        ca = s and bool(r & ~k)

        self.setRegister(REG_CA, ca)
        self.setOperValue(op, 0, result)

    def i_sraw(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        n = rb & 0x1f
        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = 0 if rb & 0x20 else MASK(n+32, 63)
        s = e_bits.is_signed(rs, 4)
        s_bits = (0, 0xFFFF_FFFF_FFFF_FFFF)[s]

        result = (r & k) | (s_bits & ~k)

        if op.iflags & IF_RC: self.setFlags(result)

        ca = s and bool(r & ~k)

        self.setRegister(REG_CA, ca)
        self.setOperValue(op, 0, result)

    def i_srawi(self, op):
        n = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = MASK(n+32, 63)
        s = e_bits.is_signed(rs, 4)
        s_bits = (0, 0xFFFF_FFFF_FFFF_FFFF)[s]

        result = (r & k) | (s_bits & ~k)

        if op.iflags & IF_RC: self.setFlags(result)

        ca = s and bool(r & ~k)

        self.setRegister(REG_CA, ca)
        self.setOperValue(op, 0, result)

    def i_se_srawi(self, op):
        # Only use the lower 5 bits of the shift amount
        n = self.getOperValue(op, 1) & 0x1F
        rs = self.getOperValue(op, 0)
        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = MASK(n+32, 63)
        s = e_bits.is_signed(rs, 4)
        s_bits = (0, 0xFFFF_FFFF_FFFF_FFFF)[s]

        result = (r & k) | (s_bits & ~k)

        if op.iflags & IF_RC: self.setFlags(result)

        ca = s and bool(r & ~k)

        self.setRegister(REG_CA, ca)
        self.setOperValue(op, 0, result)

    i_se_sraw = i_se_srawi

    def i_srd(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        n = rb & 0x3f
        r = ROTL64(rs, 64-n)
        k = 0 if rb & 0x40 else MASK(n, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_srw(self, op):
        rb = self.getOperValue(op, 2)
        rs = self.getOperValue(op, 1)
        n = rb & 0x1f
        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = 0 if rb & 0x20 else MASK(n+32, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_se_srw(self, op):
        rb = self.getOperValue(op, 1)
        rs = self.getOperValue(op, 0)
        n = rb & 0x1f
        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = 0 if rb & 0x20 else MASK(n+32, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_e_srwi(self, op):
        rb = self.getOperValue(op, 0)
        rs = self.getOperValue(op, 1)
        n = self.getOperValue(op, 2)

        r = ROTL32(e_bits.unsigned(rs, 4), 32-n)
        k = 0 if rb & 0x20 else MASK(n+32, 63)
        result = r & k

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    ######################## arithmetic instructions ##########################

    def i_mulld(self, op, size=8):
        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getRegister(REG_SO)
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegister(REG_SO, so)
            self.setRegister(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(prod, so)
        self.setOperValue(op, 0, prod & e_bits.u_maxes[size])


    def i_mullw(self, op, size=4, oe=False):
        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        so = self.getRegister(REG_SO)
        if oe:
            ov = (prod & 0xffffffff80000000) not in (0, 0xffffffff80000000)
            so |= ov
            self.setRegister(REG_SO, so)
            self.setRegister(REG_OV, ov)

        if op.iflags & IF_RC: self.setFlags(prod, so)
        self.setOperValue(op, 0, prod)

    def i_mullwo(self, op):
        return self.i_mullw(oe=True)

    def i_mulli(self, op):
        dsize = op.opers[0].getWidth(self)
        s1size = op.opers[1].getWidth(self)
        src1 = e_bits.signed(self.getOperValue(op, 1), s1size)
        src2 = e_bits.signed(self.getOperValue(op, 2), 2)

        result = (src1 * src2) & e_bits.u_maxes[dsize]

        self.setOperValue(op, 0, result)

    def i_e_mull2i(self, op):
        reg = self.getOperValue(op, 0)
        imm = e_bits.signed(self.getOperValue(op, 1), op.opers[1].getWidth(self))

        result = (reg * imm) & e_bits.u_maxes[op.opers[0].getWidth(self)]

        self.setOperValue(op, 0, result)

    def i_se_mullw(self, op):
        ra = self.getOperValue(op, 0) & 0xFFFFFFFF
        rb = self.getOperValue(op, 1) & 0xFFFFFFFF
        prod = ra * rb
        self.setOperValue(op, 0, prod & 0xFFFFFFFF)

    def i_mulhw(self, op, size=4):
        ra = e_bits.signed(self.getOperValue(op, 1) & e_bits.u_maxes[size], size)
        rb = e_bits.signed(self.getOperValue(op, 2) & e_bits.u_maxes[size], size)
        prod = ra * rb

        if op.iflags & IF_RC: self.setFlags(prod)

        # Store the upper half of the product into the destination register
        self.setOperValue(op, 0, prod >> (size*8))

    def i_mulhwu(self, op, size=4):
        ra = self.getOperValue(op, 1) & e_bits.u_maxes[size]
        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]
        prod = ra * rb

        if op.iflags & IF_RC: self.setFlags(prod)

        # Store the upper half of the product into the destination register
        self.setOperValue(op, 0, prod >> (size*8))

    def i_divw(self, op, oe=False):
        dividend = e_bits.signed(self.getOperValue(op, 1), 4)
        divisor = e_bits.signed(self.getOperValue(op, 2), 4)

        if (dividend == -0x80000000 and divisor == -1):
            quotient = 0x7fffffff

        elif divisor == 0:
            if divisor >= 0:
                quotient = 0x7fffffff
            elif divisor < 0:
                quotient = 0x80000000

            ov = 1

        else:
            quotient = dividend // divisor
            ov = 0

        so = self.getRegister(REG_SO)
        if oe:
            so |= ov
            self.setRegister(REG_OV, ov)
            self.setRegister(REG_SO, so)

        if op.iflags & IF_RC:
            if self.psize == 8:
                self.setRegister(REG_CR0, so)
            else:
                self.setFlags(quotient, so)

        self.setOperValue(op, 0, quotient)

    def i_divwu(self, op, oe=False):
        dividend = self.getOperValue(op, 1)
        divisor = self.getOperValue(op, 2)

        if divisor == 0:
            quotient = 0xffffffff
            ov = 1

        else:
            quotient = dividend // divisor

            ov = 0

        so = self.getRegister(REG_SO)
        if oe:
            so |= ov
            self.setRegister(REG_OV, ov)
            self.setRegister(REG_SO, so)

        if op.iflags & IF_RC:
            if self.psize == 8:
                self.setRegister(REG_CR0, so)
            else:
                self.setFlags(quotient, so)

        self.setOperValue(op, 0, quotient)

    def i_divwuo(self, op):
        return self.i_divwu(op, oe=True)

    def i_mfcr(self, op):
        cr = self.getRegister(REG_CR)
        self.setOperValue(op, 0, cr & 0xffffffff)

    def i_se_mtctr(self, op):
        r = self.getOperValue(op, 0)
        self.setRegister(REG_CTR, r)

    def i_se_mfctr(self, op):
        ctr = self.getRegister(REG_CTR)
        self.setOperValue(op, 0, ctr)

    def i_se_mflr(self, op):
        lr = self.getRegister(REG_LR)
        self.setOperValue(op, 0, lr)

    def i_se_mtlr(self, op):
        lr = self.getOperValue(op, 0)
        self.setRegister(REG_LR, lr)

    def i_mcrfs(self, op):
        # This has weird side effects:
        #   - if MSR[FP] =0 0 raise FP unavailable interrupt
        #   - all exception bits copied from the FPSCR are cleared

        crS = self.getOperValue(op, 1)
        self.setOperValue(op, 0, crS)

    def _base_sub(self, op, oeflags=False, setcarry=False, addone=1, size=4):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)
        ra = self.getOperValue(op, 1)
        rb = self.getOperValue(op, 2)

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + rb + addone
        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)
        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])

        if setcarry: self.setCA(result)
        if oeflags: self.setOEflags(result, size, ra, rb + addone)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_se_sub(self, op):
        rx = self.getOperValue(op, 0)
        ry = self.getOperValue(op, 1)
        result = rx + (~ry+1)

        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_subf(self, op):
        result = self._base_sub(op)

    def i_subfo(self, op):
        result = self._base_sub(op, oeflags=True)

    def i_subfb(self, op, size=1):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)
        bsize = op.opers[2].getWidth(self)

        ra = e_bits.sign_extend(self.getOperValue(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, size)

        rb = e_bits.sign_extend(self.getOperValue(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]
        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

        if op.iflags & IF_RC: self.setFlags(result)

    def i_subfbss(self, op, size=1):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)
        bsize = op.opers[2].getWidth(self)

        ra = e_bits.sign_extend(self.getOperValue(op, 1), size, asize)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, 1)

        rb = e_bits.sign_extend(self.getOperValue(op, 2), size, bsize)

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[dsize]

        # flag magic
        so = self.getRegister(REG_SO)
        sum55 = (result>>(size*8))&1
        sum56 = (result>>(size*8-1))&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov

        self.setRegister(REG_OV, ov)
        self.setRegister(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, so)

        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfbu(self, op, size=1):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)

        ra = EXTZ(self.getOperValue(op, 1), size)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.unsigned(ra, 1)

        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size]
        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

        if op.iflags & IF_RC: self.setFlags(result)

    def i_subfbus(self, op, size=1):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)

        ra = EXTZ(self.getOperValue(op, 1), size)
        ra ^= e_bits.u_maxes[asize] # 1's complement
        ra = e_bits.signed(ra, 1)

        rb = self.getOperValue(op, 2) & e_bits.u_maxes[size]

        result = ra + rb + 1
        ures = result & e_bits.u_maxes[size]

        # flag magic
        so = self.getRegister(REG_SO)
        sum55 = (result>>8)&1
        sum56 = (result>>7)&1
        ov = sum55 ^ sum56
        if ov:
            if sum55:
                ures = e_bits.sign_extend(e_bits.s_maxes[size] + 1, size, 4)
            else:
                ures = e_bits.s_maxes[size]
        so |= ov

        self.setRegister(REG_OV, ov)
        self.setRegister(REG_SO, so)
        if op.iflags & IF_RC: self.setFlags(result, so)

        self.setOperValue(op, 0, ures & e_bits.u_maxes[dsize])

    def i_subfc(self, op, oeflags=False):
        self._base_sub(op, oeflags=False, setcarry=True)

    def i_subfco(self, op):
        self._base_sub(op, oeflags=True, setcarry=True)

    def i_subfe(self, op, oe=False):
        ca = self.getRegister(REG_CA)
        asize = op.opers[1].getWidth(self)

        ra = self.getOperValue(op, 1)
        ra ^= e_bits.u_maxes[asize]  # 1's complement
        rb = self.getOperValue(op, 2)

        result = ra + rb + ca

        self.setOperValue(op, 0, result)
        self.setCA(result)
        if oe: self.setOEflags(result, self.psize, ra, rb + ca)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_subfeo(self, op):
        self.i_subfe(op, oe=True)

    def i_subfh(self, op):
        self.i_subfb(op, 2)

    def i_subfhss(self, op):
        self.i_subfbss(op, 2)

    def i_subfhu(self, op):
        self.i_subfbu(op, 2)

    def i_subfhus(self, op):
        self.i_subfbus(op, 2)

    def i_subfic(self, op):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)
        immsize = 16
        ra = self.getOperValue(op, 1)
        simm = e_bits.signed(self.getOperValue(op, 2), immsize)

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + simm + 1
        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)
        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])

        if op.iflags & IF_RC: self.setFlags(result)
        self.setCA(result)

    def _subme(self, op, size=4, addone=1, oeflags=False):
        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)
        ra = self.getOperValue(op, 1)
        rb = 0xffffffffffffffff

        ra ^= e_bits.u_maxes[asize] # 1's complement
        result = ra + rb + addone
        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)
        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])

        self.setCA(result)
        if oeflags: self.setOEflags(result, size, ra + rb + addone)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_subfme(self, op, size=4, addone=1):
        ca = self.getRegister(REG_CA)
        self._subme(op, size, ca)

    def i_subfmeo(self, op, size=4, addone=1):
        ca = self.getRegister(REG_CA)
        self._subme(op, size, ca, oeflags=True)

    def i_subfw(self, op):
        self.i_subfb(op, 4)

    def i_subfwss(self, op):
        self.i_subfbss(op, 4)

    def i_subfwu(self, op):
        self.i_subfbu(op, 4)

    def i_subfwus(self, op):
        self.i_subfbus(op, 4)

    def i_subfze(self, op, oe=False):
        ca = self.getRegister(REG_CA)

        dsize = op.opers[0].getWidth(self)
        asize = op.opers[1].getWidth(self)

        ra = self.getOperValue(op, 1)
        ra ^= e_bits.u_maxes[asize] # 1's complement

        # 1's compliment of rA added to the CA flag
        result = ra + ca

        ures = result & e_bits.u_maxes[dsize]
        sres = e_bits.signed(ures, dsize)

        self.setOperValue(op, 0, sres & e_bits.u_maxes[dsize])
        self.setCA(result)
        if oe: self.setOEflags(result, size, ra, ca)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_subfzeo(self, op):
        self.i_subfze(op, oe=True)

    ##################### Embedded FP instructions #######################


    def i_efsdiv(self, op):
        a = self.getOperValue(op, 1)
        b = self.getOperValue(op, 2)
        rA = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        rB = e_bits.decimeltofloat(self.getOperValue(op, 2) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        # result is pmax based on whearher b is a pos or neg 0
        # defaults to a's sign if a is a nan
        result = None
        if b == 0 or b == 0x80000000:
            if a == 0x80000000 or (a in FNAN_NEG_TUP):
                result = FP_SINGLE_NEG_MAX
            elif a == 0 or (a in FNAN_POS_TUP):
                result = FP_SINGLE_POS_MAX
            elif b == 0:
                result = FP_SINGLE_POS_MAX
            elif b == 0x80000000:
                result = FP_SINGLE_NEG_MAX

        #had to specify that rB wasn't a 0 or else python would freak out
        elif (b != 0 or 0x80000000) and rB != 0:
            if a in FNAN_POS_TUP:
                result = FP_SINGLE_POS_MAX
            elif a in FNAN_NEG_TUP:
                result = FP_SINGLE_NEG_MAX
            elif (b  in FNAN_NEG_TUP) and a not in FNAN_NEG_TUP:
                result = FP_SINGLE_NEG_MAX
            elif (b in FNAN_POS_TUP) and a not in  FNAN_POS_TUP:
                result = FP_SINGLE_POS_MAX

        if result is None:
            try:
                result = e_bits.floattodecimel(rA / rB, size=4, endian=self.getEndian())
            except OverflowError:
                result = FP_SINGLE_POS_MAX
                self.setRegister(REG_SPEFSCR_FOVF, 1)
            except ZeroDivisionError:
                result = FP_SINGLE_POS_MAX
                #self.setRegister(REG_SPEFSCR_FINV, 1)
                self.setRegister(REG_SPEFSCR_FDBZ, 1)

        self.setOperValue(op,0, result)

    def i_efsabs(self,op):
            a = self.getOperValue(op, 1)

            result = a & ~e_bits.sign_bits[op.opers[0].getWidth(self)]

            #can't test in 32 bit mode presently as the unit tests are run
            # in 64 bit mode.

            if a in FNAN_ALL_TUP:
                result = a
                #there will have to be SPEFSCR Flag stuff that happens

            self.setOperValue(op,0,result)

    def i_efsadd(self, op):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # TODO: The e200z759C reference manual is contradictory, it says that
        # zero, NaN, Inf, or denormalized numbers result in no value being set
        # in the destination right after it specifies the following checks:
        if rA in FNAN_SINGLE_POS_TUP or rB in FNAN_SINGLE_POS_TUP:
            # Result is max positive
            self.setOperValue(op, 0, FP_SINGLE_POS_MAX)

        elif rA in FNAN_SINGLE_NEG_TUP or rB in FNAN_SINGLE_NEG_TUP:
            # Result is max negative
            self.setOperValue(op, 0, FP_SINGLE_NEG_MAX)

        else:
            float_A = e_bits.decimeltofloat(rA, size=4, endian=self.getEndian())
            float_B = e_bits.decimeltofloat(rB, size=4, endian=self.getEndian())

            try:
                result = e_bits.floattodecimel(float_A + float_B, size=4, endian=self.getEndian())
            except OverflowError:
                result = FP_SINGLE_POS_MAX
                self.setRegister(REG_SPEFSCR_FOVF, 1)

            self.setOperValue(op,0, result)

    def i_efscfh(self, op):
        # Convert from half precision to single
        f = self.getOperValue(op, 1) & 0xffff
        f_sign = (f & 0x8000) << 16
        f_exp = (f & 0x7c00) >> 10
        f_fract = f & 0x3ff

        if (f_exp == 0) and (f_fract == 0):
            result = f_sign
            self.setOperValue(op, 0, result)
            return
        elif f in FNAN_HALF_TUP and self.getRegister(REG_SPEFSCR_FINVE) == 0:
            self.setRegister(REG_SPEFSCR_FINV, 1)
            if f & 0x8000:
                result = FP_SINGLE_NEG_MAX
            else:
                result = FP_SINGLE_POS_MAX
            self.setOperValue(op, 0, result)
            return

        elif f in FNAN_HALF_TUP and self.getRegister(REG_SPEFSCR_FINVE) == 1:
            self.setRegister(REG_SPEFSCR_FGH, 0)
            self.setRegister(REG_SPEFSCR_FXH, 0)
            self.setRegister(REG_SPEFSCR_FG, 0)
            self.setRegister(REG_SPEFSCR_FX, 0)
            return

        elif self.is_denorm16(f):
            result = f_sign & 0x80000000
        else:
            sing_exp = ((f_exp - 15 + 127) << 23)
            result = f_sign | sing_exp | (f_fract << 13)

        self.setOperValue(op, 0, result)

    def i_efssub(self, op):
        a = self.getOperValue(op, 1)
        b = self.getOperValue(op, 2)
        rA = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        rB = e_bits.decimeltofloat(self.getOperValue(op, 2) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        try:
            result = e_bits.floattodecimel(rA - rB, size=4, endian=self.getEndian())
            if (a in FNAN_SINGLE_TUP) or (b in FNAN_SINGLE_TUP) or self.is_denorm32(a) or self.is_denorm32(b):
                self.setRegister(REG_SPEFSCR_FINV, 1)
                if a in FNAN_SINGLE_NEG_TUP or b in FNAN_SINGLE_NEG_TUP:
                    result = FP_SINGLE_NEG_MAX
                else:
                    # Must be positive
                    result = FP_SINGLE_POS_MAX
        except OverflowError:
            result = FP_SINGLE_POS_MAX
            self.setRegister(REG_SPEFSCR_FOVF, 1)

        self.setOperValue(op, 0, result)

    def i_efscfsf(self, op):
        bl = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        fraction = bl % 1
        result = e_bits.floattodecimel(fraction, size=4, endian=self.getEndian())

        self.setOperValue(op, 0, result)

    def i_efscfsi(self, op):
        bl = self.getOperValue(op, 1)
        fraction = bl % 1
        result = e_bits.floattodecimel(fraction, size=4, endian=self.getEndian())

        self.setOperValue(op, 0, result)

    def i_efscfuf(self, op):
        bl = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        fraction = bl % 1
        result = e_bits.floattodecimel(fraction, size=4, endian=self.getEndian())

        if result & 0x80000000:
            result = result & 0x7fffffff

        self.setOperValue(op, 0, result)

    def i_efscfui(self, op):
        bl = self.getOperValue(op, 1)
        fraction = bl % 1
        result = e_bits.floattodecimel(fraction, size=4, endian=self.getEndian())

        if result & 0x80000000:
            result = result & 0x7fffffff

        self.setOperValue(op, 0, result)

    def i_efscmpgt(self, op):
        crnum = op.opers[0].field
        al = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        bl = e_bits.decimeltofloat(self.getOperValue(op, 2) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        if al > bl:
            self.setOperValue(op, 0, 0b0100)
        else:
            self.setOperValue(op, 0, 0b0000)

    def i_efscmpeq(self, op):
        self.getOperValue(op, 1)
        al = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        bl = e_bits.decimeltofloat(self.getOperValue(op, 2) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        if al == bl:
            self.setOperValue(op, 0, 0b0010)
        else:
            self.setOperValue(op, 0, 0b0000)

    def i_efscmplt(self, op):
        al = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        bl = e_bits.decimeltofloat(self.getOperValue(op, 2) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        if al < bl:
            self.setOperValue(op, 0, 0b1000)
        else:
            self.setOperValue(op, 0, 0b0000)

    i_efststgt = i_efscmpgt
    i_efststeq = i_efscmpeq
    i_efststlt = i_efscmplt

    def i_efscth(self, op):
        f = self.getOperValue(op,1)

        f_sign = (f & 0x80000000)
        f_exp = (f & 0x7f800000) >> 23
        f_fract = f & 0x7FFFFF

        if (f_exp == 0) and (f_fract == 0):
            result = f_sign >> 16
            self.setOperValue(op, 0, result)
            return

        elif f in FNAN_SINGLE_TUP and self.getRegister(REG_SPEFSCR_FINVE) == 0:
                self.setRegister(REG_SPEFSCR_FINV, 1)

                result = f_sign >> 16

                self.setOperValue(op, 0, result)
                return

        elif f in FNAN_SINGLE_TUP and self.getRegister(REG_SPEFSCR_FINVE) == 1:
            self.setRegister(REG_SPEFSCR_FGH, 0)
            self.setRegister(REG_SPEFSCR_FXH, 0)
            self.setRegister(REG_SPEFSCR_FG, 0)
            self.setRegister(REG_SPEFSCR_FX, 0)
            result = self.getOperValue(op, 0)
            self.setOperValue(op, 0, result)

        elif self.is_denorm32(f):
            self.setRegister(REG_SPEFSCR_FINV, 1)
            result = f_sign >> 16

        else:
            unbias = f_exp - 127
            if unbias > 15:
                result = (f_sign >> 16) & 0xfbff # signed max 16 bit value
            elif unbias < -14:
                result = f_sign >> 16
                self.setRegister(REG_SPEFSCR_FUNF, 1)
            else:
                guard = f_fract & 0x200
                if f_fract & 0x3FFC00: #bits 11-22:
                    sticky = 1
                else:
                    sticky = 0
                result = (f_sign >> 16) | (f_exp << 10) | (f_fract & 0x1ff)
                self.setRegister(REG_SPEFSCR_FG, guard)
                self.setRegister(REG_SPEFSCR_FX, sticky)
                if guard or sticky:
                    self.setRegister(REG_SPEFSCR_FINXS, 1)

        self.setOperValue(op, 0, result)

    def i_efsctsf(self, op):
        f = self.getOperValue(op, 1)
        bl = e_bits.decimeltofloat(self.getOperValue(op, 1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        fraction = bl % 1
        f_sign = (f & 0x80000000)
        f_exp = (f & 0x7f800000) >> 23
        f_fract = f & 0x7FFFFF

        if is_denorm32(bl):
            if self.getRegister(REG_SPEFSCR_FINVE) == 1:
                return
            else:
                result = 0
                self.setRegister(REG_SPEFSCR_FINV, 1)
                self.setRegister(REG_SPEFSCR_FGH, 0)
                self.setRegister(REG_SPEFSCR_FXH, 0)
                self.setRegister(REG_SPEFSCR_FG, 0)
                self.setRegister(REG_SPEFSCR_FX, 0)
                self.setOperValue(op, 0, result)
                return
        elif f == 0 or f == 0x80000000:
            result = 0
            self.setOperValue(op, 0, result)
            return
        elif f_exp < 127:
            result = e_bits.floattodecimel(fraction, size=4, endian=self.getEndian())
            if f_sign:
                result = result | f_sign
            self.setOperValue(op, 0, result)
            return
        elif (f_exp == 127) and f_sign and f_fract == 0:
            result = 0x80000000
            self.setOperValue(op, 0, result)
            return
        elif f in FNAN_SINGLE_TUP:
            if self.getRegister(REG_SPEFSCR_FINVE) == 1:
                return
            else:
                result = 0
                self.setRegister(REG_SPEFSCR_FINV, 1)
                self.setRegister(REG_SPEFSCR_FGH, 0)
                self.setRegister(REG_SPEFSCR_FXH, 0)
                self.setRegister(REG_SPEFSCR_FG, 0)
                self.setRegister(REG_SPEFSCR_FX, 0)
                self.setOperValue(op, 0, result)
                return
        else:
            if f_sign:
                result = 0x80000000
            else:
                result = 0x7fffffff
        self.setOpervalue(op, 0, result)

    def i_efsctuiz(self, op):
        rB = self.getOperValue(op, 1) & 0xFFFFFFFF
        # Only lower 32 bits of destination are modified
        rD = self.getOperValue(op, 0) & 0xFFFFFFFF00000000
        if rB in (FP_SINGLE_NEG_PYNAN, FP_SINGLE_POS_PYNAN):
            result = rD
        else:
            value = e_bits.decimeltofloat(rB, size=4, endian=self.getEndian())
            if value < 0:
                result = rD
            else:
                result = (int(rB) & 0xFFFFFFFF) | rD
        self.setOperValue(op, 0, result)

    def i_efsctsiz(self, op):
        rB = self.getOperValue(op, 1) & 0xFFFFFFFF
        # Only lower 32 bits of destination are modified
        rD = self.getOperValue(op, 0) & 0xFFFFFFFF00000000

        if rB in (FP_SINGLE_NEG_PYNAN, FP_SINGLE_POS_PYNAN):
            result = rD
        else:
            value = e_bits.decimeltofloat(rB, size=4, endian=self.getEndian())
            result = (int(rB) & 0xFFFFFFFF) | rD

        self.setOperValue(op, 0, result)

    def i_efsneg(self, op):
        # Only the low element of rA is negated
        rA = self.getOperValue(op, 1) & 0xFFFFFFFF
        if rA & 0x00000000800000000:
            value = rA & 0x000000007FFFFFFF
        else:
            value = (rA & 0x00000000FFFFFFFF) | 0x00000000800000000
        # Only lower 32 bits of destination are modified
        rD = self.getOperValue(op, 0) & 0xFFFFFFFF00000000
        result = value | rD
        self.setOperValue(op, 0, result)

    def i_efsmadd(self, op): # incomplete.  doesn't match hardware 100%
        rA = self.getOperValue(op,1)
        rB = self.getOperValue(op,2)
        rD = self.getOperValue(op,0)
        RA = e_bits.decimeltofloat(self.getOperValue(op,1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        RB = e_bits.decimeltofloat(self.getOperValue(op,2) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        RD = e_bits.decimeltofloat(self.getOperValue(op,0) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        result = e_bits.floattodecimel(((RA * RB) + RD), size=4, endian=self.getEndian())

        if rA in (0, 0x80000000) or rB in (0, 0x80000000) or ((self.is_denorm32(rA) or self.is_denorm32(rB))):

            if self.is_denorm32(rA) or self.is_denorm32(rB) or self.is_denorm32(rD) or (rB in FNAN_SINGLE_TUP) or (rA in FNAN_SINGLE_TUP):
                self.setRegister(REG_SPEFSCR_FINV, 1)
                if self.is_denorm32(rA) or self.is_denorm32(rB) or self.is_denorm32(rD):
                    result = 0
            else:
                result = rD

            self.setOperValue(op, 0, result)
        else:
            self.setOperValue(op, 0, result)

    def i_efsmsub(self, op): # incomplete.  doesn't match hardware 100%
        rA = self.getOperValue(op,1)
        rB = self.getOperValue(op,2)
        rD = self.getOperValue(op,0)
        RA = e_bits.decimeltofloat(self.getOperValue(op,1) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        RB = e_bits.decimeltofloat(self.getOperValue(op,2) & 0xFFFFFFFF, size=4, endian=self.getEndian())
        RD = e_bits.decimeltofloat(self.getOperValue(op,0) & 0xFFFFFFFF, size=4, endian=self.getEndian())

        result = e_bits.floattodecimel(((RA * RB) - RD), size=4, endian=self.getEndian())

        if rA in (0, 0x80000000) or rB in (0, 0x80000000) or ((self.is_denorm32(rA) or self.is_denorm32(rB))):

            if self.is_denorm32(rA) or self.is_denorm32(rB) or self.is_denorm32(rD) or (rB in FNAN_SINGLE_TUP) or (rA in FNAN_SINGLE_TUP):
                self.setRegister(REG_SPEFSCR_FINV, 1)
                if self.is_denorm32(rA) or self.is_denorm32(rB) or self.is_denorm32(rD):
                    result = 0
            else:
                result = rD

            self.setOperValue(op, 0, result)
        else:
            self.setOperValue(op, 0, result)

    def i_efsmul(self, op): # incomplete.  doesn't match hardware 100%
        rA = self.getOperValue(op,1)
        rB = self.getOperValue(op,2)

        # TODO: The e200z759C reference manual is contradictory, it says that
        # zero, NaN, Inf, or denormalized numbers result in no value being set
        # in the destination right after it specifies the following checks:
        if self.is_denorm32(rA) or self.is_denorm32(rB) or \
                rA in F_SINGLE_ZERO_TUP or rB in F_SINGLE_ZERO_TUP:
            # Correct the sign on zero
            self.setOperValue(op, 0, FP_SINGLE_POS_ZERO)

        elif rA in FNAN_SINGLE_POS_TUP or rB in FNAN_SINGLE_POS_TUP:
            # Result is max positive
            self.setOperValue(op, 0, FP_SINGLE_POS_MAX)

        elif rA in FNAN_SINGLE_NEG_TUP or rB in FNAN_SINGLE_NEG_TUP:
            # Result is max negative
            self.setOperValue(op, 0, FP_SINGLE_NEG_MAX)

        else:
            float_A = e_bits.decimeltofloat(rA, size=4, endian=self.getEndian())
            float_B = e_bits.decimeltofloat(rB, size=4, endian=self.getEndian())

            try:
                result = e_bits.floattodecimel((float_A * float_B), size=4, endian=self.getEndian())
            except OverflowError:
                result = FP_SINGLE_POS_MAX
                self.setRegister(REG_SPEFSCR_FOVF, 1)

            self.setOperValue(op, 0, result)

    def i_efsnabs(self, op):
        rA = self.getOperValue(op, 1)

        result = rA | 0x80000000

        if rA in FNAN_SINGLE_TUP or self.is_denorm32(rA):
            self.setRegister(REG_SPEFSCR_FINV, 1)
            self.setRegister(REG_SPEFSCR_FGH, 0)
            self.setRegister(REG_SPEFSCR_FXH, 0)
            self.setRegister(REG_SPEFSCR_FG, 0)
            self.setRegister(REG_SPEFSCR_FX, 0)
        self.setOperValue(op, 0, result)

    ######################## cache instructions ##########################

    # these instructions don't have any effect on the emulation

    i_dcba = i_nop
    i_dcbal = i_nop
    i_dcbf = i_nop
    i_dcbfep = i_nop
    i_dcbi = i_nop
    i_dcblc = i_nop
    i_dcblq = i_nop
    i_dcbst = i_nop
    i_dcbstep = i_nop
    i_dcbt = i_nop
    i_dcbtep = i_nop
    i_dcbtls = i_nop
    i_dcbtst = i_nop
    i_dcbtstep = i_nop
    i_dcbtstls = i_nop
    i_dcbz = i_nop
    i_dcbzep = i_nop
    i_dcbzl = i_nop
    i_dcbzlep = i_nop

    ######################## sync instructions ##########################

    i_sync = i_nop
    i_isync = i_nop
    i_msync = i_nop
    i_esync = i_nop
    i_mbar = i_nop

    ######################## debug instructions ##########################

    # These instructions are valid but do nothing for now

    i_dnh = i_nop
    i_dni = i_nop

    ######################## interrupt instructions ##########################

    # These are instructions related to causing, or returning from interrupt
    # contexts

    def i_rfi(self, op):
        '''
        Return From Interrupt
        '''
        nextpc = self.getRegister(REG_SRR0)
        msr = self.getRegister(REG_SRR1)
        self.setRegister(REG_MSR, msr)

        # Do any core-specific RFI actions now
        self._rfi(op)

        return nextpc

    def i_rfci(self, op):
        '''
        Return From Critical Interrupt
        '''
        nextpc = self.getRegister(REG_CSRR0)
        msr = self.getRegister(REG_CSRR1)
        self.setRegister(REG_MSR, msr)

        # Do any core-specific RFI actions now
        self._rfi(op)

        return nextpc

    def i_rfdi(self, op):
        '''
        Return From Debug Interrupt
        '''
        nextpc = self.getRegister(REG_DSRR0)
        msr = self.getRegister(REG_DSRR1)
        self.setRegister(REG_MSR, msr)

        # Do any core-specific RFI actions now
        self._rfi(op)

        return nextpc

    def i_rfmci(self, op):
        '''
        Return From MachineCheck Interrupt
        '''
        nextpc = self.getRegister(REG_MCSRR0)
        msr = self.getRegister(REG_MCSRR1)
        self.setRegister(REG_MSR, msr)

        # Do any core-specific RFI actions now
        self._rfi(op)

        return nextpc

    i_se_rfi = i_rfi
    i_se_rfci = i_rfci
    i_se_rfdi = i_rfdi
    i_se_rfmci = i_rfmci

    ####### Unconditional Trap #######

    def i_trap(self, op):
        # core-specific trap handling
        self._trap(op)

    # The "unconditional" simplified mnemonics are defined in the PowerISA to
    # indicate unconditional-non "tw" instructions
    i_twui = i_trap
    i_tdu = i_trap
    i_tdui = i_trap

    ####### Generic (unsimplified) Conditional Trap #######

    def i_tw(self, op, asize=4, bsize=4):
        TO = self.getOperValue(op, 0)
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # Unsigned checks
        a = e_bits.unsigned(rA, size)
        b = e_bits.unsigned(rB, size)

        if TO & 0b00010 and a < b:
            self.i_trap(op)
        if TO & 0b00001 and a > b:
            self.i_trap(op)

        # Signed checks
        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if TO & 0b10000 and a < b:
            self.i_trap(op)
        if TO & 0b01000 and a > b:
            self.i_trap(op)
        if TO & 0b00100 and a == b:
            self.i_trap(op)

    def i_twi(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_tw(op, asize=4, bsize=2)

    def i_td(self, op):
        self.i_tw(op, asize=8, bsize=8)

    def i_tdi(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_tw(op, asize=8, bsize=2)

    ####### Simplified Trap if == #######

    def i_tweq(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a == b:
            self.i_trap(op)

    def i_tweqi(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_tweq(op, asize=4, bsize=2)

    def i_tdeq(self, op):
        self.i_tweq(op, asize=8, bsize=8)

    def i_tdeqi(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_tweq(op, asize=8, bsize=2)

    ####### Simplified Trap if != #######

    def i_twne(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a != b:
            self.i_trap(op)

    def i_twnei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twne(op, asize=4, bsize=2)

    def i_tdne(self, op):
        self.i_twne(op, asize=8, bsize=8)

    def i_tdnei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twne(op, asize=8, bsize=2)

    ####### Simplified Trap if >= #######

    def i_twge(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a >= b:
            self.i_trap(op)

    def i_twgei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twge(op, asize=4, bsize=2)

    def i_tdge(self, op):
        self.i_twge(op, asize=8, bsize=8)

    def i_tdgei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twge(op, asize=8, bsize=2)

    ####### Simplified Trap if > #######

    def i_twgt(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a > b:
            self.i_trap(op)

    def i_twgti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twgt(op, asize=4, bsize=2)

    def i_tdgt(self, op):
        self.i_twgt(op, asize=8, bsize=8)

    def i_tdgti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twgt(op, asize=8, bsize=2)

    ####### Simplified Trap if <= #######

    def i_twle(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a <= b:
            self.i_trap(op)

    def i_twlei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twle(op, asize=4, bsize=2)

    def i_tdle(self, op):
        self.i_twle(op, asize=8, bsize=8)

    def i_tdlei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twle(op, asize=8, bsize=2)

    ####### Simplified Trap if < #######

    def i_twlt(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        a = e_bits.signed(rA, size)
        b = e_bits.signed(rB, size)

        if a < b:
            self.i_trap(op)

    def i_twlti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlt(op, asize=4, bsize=2)

    def i_tdlt(self, op):
        self.i_twlt(op, asize=8, bsize=8)

    def i_tdlti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlt(op, asize=8, bsize=2)

    ####### Simplified Trap if (unsigned) >= #######

    def i_twlge(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # "Logical" (unsigned) comparison
        a = e_bits.unsigned(rA, size)
        b = e_bits.unsigned(rB, size)

        if a >= b:
            self.i_trap(op)

    def i_twlgei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlge(op, asize=4, bsize=2)

    def i_tdlge(self, op):
        self.i_twlge(op, asize=8, bsize=8)

    def i_tdlgei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlge(op, asize=8, bsize=2)

    ####### Simplified Trap if (unsigned) > #######

    def i_twlgt(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # "Logical" (unsigned) comparison
        a = e_bits.unsigned(rA, size)
        b = e_bits.unsigned(rB, size)

        if a > b:
            self.i_trap(op)

    def i_twlgti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlgt(op, asize=4, bsize=2)

    def i_tdlgt(self, op):
        self.i_twlgt(op, asize=8, bsize=8)

    def i_tdlgti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlgt(op, asize=8, bsize=2)

    ####### Simplified Trap if (unsigned) <= #######

    def i_twlle(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # "Logical" (unsigned) comparison
        a = e_bits.unsigned(rA, size)
        b = e_bits.unsigned(rB, size)

        if a <= b:
            self.i_trap(op)

    def i_twllei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlle(op, asize=4, bsize=2)

    def i_tdlle(self, op):
        self.i_twlle(op, asize=8, bsize=8)

    def i_tdllei(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twlle(op, asize=8, bsize=2)

    ####### Simplified Trap if (unsigned) < #######

    def i_twllt(self, op, asize=4, bsize=4):
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        # "Logical" (unsigned) comparison
        a = e_bits.unsigned(rA, size)
        b = e_bits.unsigned(rB, size)

        if a < b:
            self.i_trap(op)

    def i_twllti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twllt(op, asize=4, bsize=2)

    def i_tdllt(self, op):
        self.i_twllt(op, asize=8, bsize=8)

    def i_tdllti(self, op):
        # The "b" value is a 16-bit immediate value
        self.i_twllt(op, asize=8, bsize=2)

    # TODO: These are instructions that should move the code into a different
    # context

    def i_sc(self, op):
        # Do core-specific system call handling
        self._sc(op)
    i_se_sc = i_sc

    def i_ehpriv(self, op):
        # Do core-specific embedded hypervisor privilege handling
        self._ehpriv(op)

    def i_wait(self, op):
        # Do core-specific "wait" handling
        self._wait(op)

    ######################## misc instructions ##########################

    def i_bpermd(self, op):
        '''
        bit permute doubleword

        bpermd rA, rS, rB

        From the manual:
            If byte i of RS is less than 64, permuted bit i is set to the bit
            of RB specified by byte i of RS; otherwise permuted bit i is set
            to 0.
        '''
        rs = self.getOperValue(op, 1)
        rb = self.getOperValue(op, 2)

        # Turn rS into 8 bytes, make this big endian so we go MSB to LSB
        val_list = struct.pack('>Q', rs)

        # Now combine those values with a list of shift values to indicate which
        # bit (in sane numbering) in rA should be set
        shift_list = range(7, -1, -1)

        # Now smash all those bits together
        result = sum(BIT(rb, val) << shift \
                for shift, val in zip(shift_list, val_list) \
                if val < 64)

        self.setOperValue(op, 0, result)

    def i_se_bclri(self, op):
        rx = self.getOperValue(op, 0)
        a = self.getOperValue(op, 1)
        val = rx & ~BITMASK(a, self.psize)
        self.setOperValue(op, 0, val)

    def i_se_bseti(self, op):
        rx = self.getOperValue(op, 0)
        a = self.getOperValue(op, 1)
        val = rx | BITMASK(a, self.psize)
        self.setOperValue(op, 0, val)

    def i_se_btsti(self, op):
        rx = self.getOperValue(op, 0)
        a = self.getOperValue(op, 1)
        b = BITMASK(a, self.psize)
        c = rx & b
        d = bool(c)
        self.setFlags(d)

    def i_se_bgeni(self, op):
        a = self.getOperValue(op, 1)
        b = 0 | BITMASK(a, self.psize)

        self.setOperValue(op, 0, b)


    ######################## VLE instructions ##########################
    i_e_li = i_li
    i_e_stwu = i_stwu
    i_e_stmw = i_stmw
    i_e_lmw = i_lmw
    i_se_mr = i_mr
    i_e_ori = i_ori
    i_se_bl = i_bl
    i_e_bl = i_bl
    i_se_b = i_b
    i_e_b = i_b
    i_se_bc = i_bc
    i_e_bc = i_bc
    i_se_bcl = i_bcl
    i_e_bcl = i_bcl

    def i_neg(self, op, oe=False):
        ra = self.getOperValue(op, 1)
        result = ~ra + 1

        so = None
        if oe:
            if self.psize == 4 and ra & 0xffffffff == 0x80000000:
                ov = 1
                so = ov
                self.setRegister(REG_OV, ov)
                self.setRegister(REG_SO, so)

            elif self.psize == 8 and ra == 0x8000000000000000:
                ov = 1
                so = ov
                self.setRegister(REG_OV, ov)
                self.setRegister(REG_SO, so)

        if op.iflags & IF_RC: self.setFlags(result, so)
        self.setOperValue(op, 0, result)

    def i_se_neg(self, op, oe=False):
        ra = self.getOperValue(op, 0)
        result = ~ra + 1
        self.setOperValue(op, 0, result)

    def i_nego(self, op):
        return self.i_neg(op, oe=True)

    def i_wrteei(self, op):
        if self.getOperValue(op, 0):
            msr = self.getRegister(REG_MSR)
            self.setRegister(REG_MSR, msr | MSR_EE_MASK)
        else:
            msr = self.getRegister(REG_MSR)
            self.setRegister(REG_MSR, msr & ~MSR_EE_MASK)

    i_wrtee = i_wrteei

    def i_extsb(self, op, opsize=1):
        result = self.getOperValue(op, 1)
        results = e_bits.sign_extend(result, opsize, self.psize)
        if op.iflags & IF_RC: self.setFlags(results)
        self.setOperValue(op, 0, results)


    def i_se_extsb(self, op, opsize=1):
        result = self.getOperValue(op, 0)
        results = e_bits.sign_extend(result, opsize, self.psize)
        if op.iflags & IF_RC: self.setFlags(results)
        self.setOperValue(op, 0, results)

    def i_extsh(self, op):
        self.i_extsb(op, opsize=2)

    def i_se_extsh(self, op):
        self.i_se_extsb(op, opsize=2)

    def i_extsw(self, op):
        self.i_extsb(op, opsize=4)

    def i_extzb(self, op):
        rx = self.getOperValue(op, 0)
        a = rx & 0xFF
        self.setOperValue(op, 0, a)

    def i_extzh(self, op):
        rx = self.getOperValue(op, 0)
        a = rx & 0xFFFF
        self.setOperValue(op, 0, a)

    def i_xor(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = src1 ^ src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    i_xori = i_xor

    def i_xoris(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2) << 16
        result = src1 ^ src2

        if op.iflags & IF_RC: self.setFlags(result)
        self.setOperValue(op, 0, result)

    def i_eqv(self, op):
        # This is essengially an "nxor" instruction
        src0 = self.getOperValue(op, 1)
        src1 = self.getOperValue(op, 2)
        # PDE
        if src0 == None or src1 == None:
            self.undefFlags()
            op.opers[OPER_DST].setOperValue(op, self, None)
            return

        result = (src0 ^ src1)
        dsize = op.opers[0].getWidth(self)
        result ^= e_bits.u_maxes[dsize] # 1's complement of the result

        self.setOperValue(op, 0, result)
        if op.iflags & IF_RC: self.setFlags(result)

    def i_se_bmaski(self, op):
        a = self.getOperValue(op, 1)
        if a == 0:
            b = 0xffffffff
        else:
            b = envi.bits.b_masks[a]

        self.setOperValue(op, 0, b)

    # These condition register logical operations use CR source/dest
    # pseudo-registers, but otherwise is the same logic as the normal logical
    # counterparts
    i_cror = i_or
    i_crnor = i_nor
    i_crorc = i_orc
    i_crand = i_and
    i_crandc = i_andc
    i_crnand = i_nand
    i_crxor = i_xor
    i_creqv = i_eqv

    ## Vector Instructions

    # Helpers
    def modulo(self, val, bytelen):
        # More like a mask, but that's what this operation is in this context
        return val & e_bits.u_maxes[bytelen]

    def signed_saturate(self, val, bytelen):
        result, saturated = SIGNED_SATURATE(val, bytelen)
        if saturated:
            self.setRegister(REG_VSCR, 1)
        return result

    def unsigned_saturate(self, val, bytelen):
        result, saturated = UNSIGNED_SATURATE(val, bytelen)
        if saturated:
            self.setRegister(REG_VSCR, 1)
        return result

    def abs(self, val, bytelen):
        return abs(val)

    def arbitrary_pack(self, val, bytelen):
        return ((val & MASK32(7, 12)) >> 9) | ((val & MASK32(16, 20)) >> 6) | ((val & MASK32(24, 28)) >> 3)

    # Load
    # These are weird, the vector field they write into is based on the address
    # read from. Also, we don't use getOperValue() from the second operand
    # because the address we're accessing isn't the address it actually refers to.
    def lvx(self, op):
        elemsize = op.opers[0].elemsize
        addr = self.getOperAddr(op, 1) & ~(elemsize - 1)
        m = (addr & (16 - elemsize)) >> ((elemsize >> 1) & 0x3)
        result_vector = [0] * (op.opers[0].elemcount)
        result_vector[m] = self.readMemValue(addr, op.opers[1].tsize)
        op.opers[0].setValues(op, self, result_vector)

    i_lvebx = lvx
    i_lvehx = lvx
    i_lvewx = lvx
    i_lvx = lvx
    i_lvxl = lvx

    def lvex(self, op):
        addr = self.getOperAddr(op, 1) & ~(op.opers[0].elemsize - 1)
        m = (self.getRegister(op.opers[1].offset) & MASK(60, 63 - (op.opers[1].tsize >> 1))) >> (op.opers[1].tsize >> 1)
        result_vector = [0] * op.opers[0].elemcount
        result_vector[m] = self.readMemValue(addr, op.opers[1].tsize)
        op.opers[0].setValues(op, self, result_vector)

    i_lvexbx = lvex
    i_lvexhx = lvex
    i_lvexwx = lvex

    lvs_bytes = bytes([x for x in range(0, 0x20)])

    def i_lvsl(self, op):
        offset = self.getOperAddr(op, 1) & 0xf
        value = int.from_bytes(self.lvs_bytes[offset:offset+16], 'big')
        op.opers[0].setOperValue(op, self, value)

    def i_lvsr(self, op):
        offset = self.getOperAddr(op, 1) & 0xf
        value = int.from_bytes(self.lvs_bytes[16-offset:32-offset], 'big')
        op.opers[0].setOperValue(op, self, value)

    def i_lvsm(self, op):
        pivot = self.getOperAddr(op, 1) & 0xf
        op.opers[0].setValues(op, self, [0xff] * (16 - pivot) + [0] * pivot)

    def i_lvswx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        result = ROTL(self.readMemValue(addr, 16), pivot * 8, 128)
        self.setOperValue(op, 0, result)

    i_lvswxl = i_lvswx

    def i_lvtlx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        result = (self.readMemValue(addr, 16) << (pivot * 8))
        self.setOperValue(op, 0, result)

    i_lvtlxl = i_lvtlx

    def i_lvtrx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        result = (self.readMemValue(addr, 16) >> ((16 - pivot) * 8))
        self.setOperValue(op, 0, result)

    i_lvtrxl = i_lvtrx

    # TODO: MSR[SPV] == 0 should cause an AltiVec unavailable interrupt
    # interrupt, but we don't have that infrastructure yet.
    i_lvepx = lvx
    i_lvepxl = lvx

    # Store -- these are weird like Load above
    def stv_index(self, op, elemsize):
        addr = self.getOperAddr(op, 1) & ~(elemsize - 1)
        return (addr & (16 - elemsize)) >> ((elemsize >> 1) & 0x3)

    def stv_index_indexed(self, op, elemsize):
        return (self.getRegister(op.opers[1].offset) & MASK(60, 63 - (elemsize >> 1))) >> (elemsize >> 1)

    def stv(self, op, index_func):
        elemsize = op.opers[0].elemsize
        addr = self.getOperAddr(op, 1) & ~(elemsize - 1)
        m = index_func(op, elemsize)
        if elemsize == 16:
            value = self.getOperValue(op, 0).to_bytes(elemsize, 'big')
            self.writeMemory(addr, value)
        else:
            value = op.opers[0].getValues(op, self)[m]
            self.writeMemValue(addr, value, op.opers[1].tsize)

    def stvx(self, op):
        self.stv(op, self.stv_index)

    i_stvebx = stvx
    i_stvehx = stvx
    i_stvewx = stvx
    i_stvx = stvx
    i_stvxl = stvx

    def stvex(self, op):
        self.stv(op, self.stv_index_indexed)

    i_stvexbx = stvex
    i_stvexhx = stvex
    i_stvexwx = stvex

    def i_stvflx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        storelen = 16 - pivot
        values = op.opers[0].getValues(op, self)[0:storelen]
        for i, value in enumerate(values):
            self.writeMemValue(addr + pivot + i, value, 1)

    i_stvflxl = i_stvflx

    def i_stvfrx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        storelen = 16 - pivot
        values = op.opers[0].getValues(op, self)[storelen:]
        for i, value in enumerate(values):
            self.writeMemValue(addr + i, value, 1)

    i_stvfrxl = i_stvfrx

    def i_stvswx(self, op):
        addr = self.getOperAddr(op, 1) & ~0xf
        pivot = self.getOperAddr(op, 1) & 0xf
        result = ROTR(self.getOperValue(op, 0), pivot * 8, 128).to_bytes(16, 'big')
        self.writeMemory(addr, result)

    i_stvswxl = i_stvswx

    # TODO: MSR[SPV] == 0 should cause an AltiVec unavailable interrupt
    # interrupt, but we don't have that infrastructure yet.
    i_stvepx = stvx
    i_stvepxl = stvx

    # Permute
    def i_vperm(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)

        src = vA + vB
        for c in vC:
            result_vector.append(src[c & 0x1f])

        op.opers[0].setValues(op, self, result_vector)

    # Pack
    def vpk(self, op, func):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)

        for elem in vA + vB:
            result_vector.append(func(elem, op.opers[0].elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def i_vpkpx(self, op):
        self.vpk(op, self.arbitrary_pack)

    def vpksss(self, op):
        self.vpk(op, self.signed_saturate)

    i_vpkshss = vpksss
    i_vpkswss = vpksss

    def vpksus(self, op):
        self.vpk(op, self.unsigned_saturate)

    i_vpkshus = vpksus
    i_vpkswus = vpksus
    i_vpkuhus = vpksus
    i_vpkuwus = vpksus

    def vpkuum(self, op):
        self.vpk(op, self.modulo)

    i_vpkuhum = vpkuum
    i_vpkuwum = vpkuum

    # Unpack
    def vupkpx(self, op, elemslice):
        result_vector = []
        vB = op.opers[1].getValues(op, self)

        for b in vB[elemslice]:
            byte0 = EXTS_BIT((b & MASK16(0, 0)) >> 15, 8) << 24
            byte1 = (b & MASK32(17, 21)) << 6
            byte2 = (b & MASK32(22, 26)) << 3
            byte3 = (b & MASK32(27, 31))
            result_vector.append(byte0 | byte1 | byte2 | byte3)

        op.opers[0].setValues(op, self, result_vector)

    def i_vupkhpx(self, op):
        self.vupkpx(op, slice(0, 4))

    def i_vupklpx(self, op):
        self.vupkpx(op, slice(4, 8))

    def vupk(self, op, elemslice):
        result_vector = []
        vB = op.opers[1].getValues(op, self)
        for b in vB[elemslice]:
            result_vector.append(e_bits.sign_extend(b, op.opers[1].elemsize, op.opers[0].elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def vupkh(self, op):
        return self.vupk(op, slice(0, op.opers[0].elemcount))

    def vupkl(self, op):
        return self.vupk(op, slice(op.opers[0].elemcount, None))

    i_vupkhsb = vupkh
    i_vupkhsh = vupkh
    i_vupklsb = vupkl
    i_vupklsh = vupkl

    # Rotate
    def vrl(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        elemsize_bits = op.opers[1].elemsize << 3
        rotsize_mask = elemsize_bits - 1

        for a, b in zip(vA, vB):
            result_vector.append(ROTL(a, b & rotsize_mask, elemsize_bits))

        op.opers[0].setValues(op, self, result_vector)

    i_vrlb = vrl
    i_vrlh = vrl
    i_vrlw = vrl

    # Shift
    def i_vsl(self, op):
        shift = op.opers[2].getValues(op, self)[0] & 0x7
        op.opers[0].setOperValue(op, self, self.getOperValue(op, 1) << shift)

    def i_vsr(self, op):
        shift = op.opers[2].getValues(op, self)[0] & 0x7
        op.opers[0].setOperValue(op, self, self.getOperValue(op, 1) >> shift)

    def vslr(self, op, func):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        result_mask = e_bits.u_maxes[op.opers[1].elemsize]
        shift_mask = (op.opers[1].elemsize << 3) - 1

        for a, b in zip(vA, vB):
            result_vector.append(func(a, (b & shift_mask)) & result_mask)

        op.opers[0].setValues(op, self, result_vector)

    def vsl(self, op):
        self.vslr(op, operator.lshift)

    def vsr(self, op):
        self.vslr(op, operator.rshift)

    i_vslb = vsl
    i_vslh = vsl
    i_vslw = vsl
    i_vsrb = vsr
    i_vsrh = vsr
    i_vsrw = vsr
    i_vsrab = vsr
    i_vsrah = vsr
    i_vsraw = vsr

    def i_vsldoi(self, op):
        src = op.opers[1].getValues(op, self) + op.opers[2].getValues(op, self)
        index = self.getOperValue(op, 3)
        op.opers[0].setValues(op, self, src[index:index+16])

    def i_vslo(self, op):
        src = op.opers[1].getValues(op, self) + ((0,) * 16)
        index = (self.getOperValue(op, 2) & 0x78) >> 3
        op.opers[0].setValues(op, self, src[index:index+16])

    def i_vsro(self, op):
        src = ((0,) * 16) + op.opers[1].getValues(op, self)
        index = 16 - ((self.getOperValue(op, 2) & 0x78) >> 3)
        op.opers[0].setValues(op, self, src[index:index+16])

    # Vector Conditional Select
    def i_vsel(self, op):
        vA = self.getOperValue(op, 1)
        vB = self.getOperValue(op, 2)
        vC = self.getOperValue(op, 3)
        self.setOperValue(op, 0, (vB & vC) | (vA & ~vC))

    # Splat
    # Note that the UIMM field is 5 bits, but there are only enough potential
    # indicdes in vB for 2-4 bits. When running this on hardware, it's observed
    # that the most significant bit seems to be ignored, so this replicates
    # that behavior by masking it away.
    def vsplt(self, op):
        vB = op.opers[1].getValues(op, self)
        uimm = self.getOperValue(op, 2) & (op.opers[1].elemcount - 1)
        op.opers[0].setValues(op, self, [vB[uimm]] * op.opers[1].elemcount)

    i_vspltb = vsplt
    i_vsplth = vsplt
    i_vspltw = vsplt

    def vspltis(self, op):
        op.opers[0].setValues(op, self, [self.getOperValue(op, 1)] * op.opers[0].elemcount)

    i_vspltisb = vspltis
    i_vspltish = vspltis
    i_vspltisw = vspltis

    # Move

    # On Noisy, this ONLY impacts the two defined bits, NJ and SAT, regardless
    # of what's in the register's other bits. That behavior is left undefined
    # (explicitly) in the docs. We are going to follow that behavior here.
    def i_mfvscr(self, op):
        self.setOperValue(op, 0, self.getRegister(REG_VSCR) & 0x00010001)

    def i_mtvscr(self, op):
        self.setRegister(REG_VSCR, self.getOperValue(op, 0) & 0x00010001)

    def i_mviwsplt(self, op):
        rA_lower = self.getOperValue(op, 1) & MASK(32, 63)
        rB_lower = self.getOperValue(op, 2) & MASK(32, 63)
        op.opers[0].setValues(op, self, [rA_lower, rB_lower, rA_lower, rB_lower])

    def i_mvidsplt(self, op):
        op.opers[0].setValues(op, self, [self.getOperValue(op, 1), self.getOperValue(op, 2)])

    # Average
    def vavg(self, op):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        for elem1, elem2 in zip(a, b):
            result_vector.append((elem1 + elem2 + 1) >> 1)

        op.opers[0].setValues(op, self, result_vector)

    i_vavgsb = vavg
    i_vavgsh = vavg
    i_vavgsw = vavg
    i_vavgub = vavg
    i_vavguh = vavg
    i_vavguw = vavg

    # Add
    def vadd(self, op, func):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        for elem1, elem2 in zip(a, b):
            result_vector.append(func(elem1 + elem2, op.opers[1].elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def i_vaddubm(self, op):
        return self.vadd(op, self.modulo)

    i_vadduhm = i_vaddubm
    i_vadduwm = i_vaddubm

    def i_vaddubs(self, op):
        return self.vadd(op, self.unsigned_saturate)

    i_vadduhs = i_vaddubs
    i_vadduws = i_vaddubs

    def i_vaddcuw(self, op):
        return self.vadd(op, CARRY)

    def i_vaddsbs(self, op):
        return self.vadd(op, self.signed_saturate)

    i_vaddshs = i_vaddsbs
    i_vaddsws = i_vaddsbs

    def i_vaddfp(self, op):
        return self.vadd(op, lambda val, _: val)

    # Subtract
    def vsub(self, op, func):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        for elem1, elem2 in zip(a, b):
            result_vector.append(func(elem1 - elem2, op.opers[1].elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def i_vsubcuw(self, op):
        return self.vsub(op, lambda val, size: ~CARRY(val, size) & 0x1)

    def i_vsubsbs(self, op):
        return self.vsub(op, self.signed_saturate)

    i_vsubshs = i_vsubsbs
    i_vsubsws = i_vsubsbs

    def i_vsububm(self, op):
        return self.vsub(op, self.modulo)

    i_vsubuhm = i_vsububm
    i_vsubuwm = i_vsububm

    def i_vsububs(self, op):
        return self.vsub(op, self.unsigned_saturate)

    i_vsubuhs = i_vsububs
    i_vsubuws = i_vsububs

    def vabsdu(self, op):
        return self.vsub(op, self.abs)

    i_vabsdub = vabsdu
    i_vabsduh = vabsdu
    i_vabsduw = vabsdu

    def i_vsubfp(self, op):
        return self.vsub(op, lambda val, _: val)

    # Sum
    def i_vsumsws(self, op):
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)

        result = self.signed_saturate(sum(vA + (vB[3],)), 4)
        result_vector = [0, 0, 0, result]

        op.opers[0].setValues(op, self, result_vector)

    def i_vsum2sws(self, op):
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)

        result1 = self.signed_saturate(sum(vA[0:2] + (vB[1],)), 4)
        result2 = self.signed_saturate(sum(vA[2:4] + (vB[2],)), 4)
        result_vector = [0, result1, 0, result2]

        op.opers[0].setValues(op, self, result_vector)

    def vsum4(self, op, func):
        result_vector = []
        # We use groups of multiple vA for each vB
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)

        groupsize = op.opers[1].elemcount // 4
        vA_sums = [sum(vA[i:i + groupsize]) for i in range(0, len(vA), groupsize)]
        for a, b in zip(vA_sums, vB):
            result_vector.append(func(a + b, 4))

        op.opers[0].setValues(op, self, result_vector)

    def i_vsum4sbs(self, op):
        self.vsum4(op, self.signed_saturate)

    i_vsum4shs = i_vsum4sbs

    def i_vsum4ubs(self, op):
        self.vsum4(op, self.unsigned_saturate)

    # Logic
    def i_vandc(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = COMPLEMENT(self.getOperValue(op, 2), op.opers[2].getWidth(self))
        self.setOperValue(op, 0, src1 & src2)

    def i_vnor(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        self.setOperValue(op, 0, COMPLEMENT(src1 | src2, 16))

    i_vand = i_and
    i_vor = i_or
    i_vxor = i_xor

    # Integer comparison

    def vcmp(self, op, cmp):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        num_true = 0
        for elem1, elem2 in zip(a, b):
            if cmp(elem1, elem2):
                result_vector.append(e_bits.u_maxes[op.opers[1].elemsize])
                num_true += 1
            else:
                result_vector.append(0x00)

        if op.iflags & IF_RC:
            if num_true == len(a):
                self.setCr(0b1000, 6)
            elif num_true == 0:
                self.setCr(0b0010, 6)
            else:
                self.setCr(0b0000, 6)

        op.opers[0].setValues(op, self, result_vector)

    def vcmpgt(self, op):
        return self.vcmp(op, operator.gt)

    def vcmpeq(self, op):
        return self.vcmp(op, operator.eq)

    def vcmpge(self, op):
        return self.vcmp(op, operator.ge)

    i_vcmpequb = vcmpeq
    i_vcmpequh = vcmpeq
    i_vcmpequw = vcmpeq
    i_vcmpgtsb = vcmpgt
    i_vcmpgtsh = vcmpgt
    i_vcmpgtsw = vcmpgt
    i_vcmpgtub = vcmpgt
    i_vcmpgtuh = vcmpgt
    i_vcmpgtuw = vcmpgt

    # Floating-point comparison
    def i_vcmpbfp(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)

        in_bounds = True
        for a, b in zip(vA, vB):
            le = int(not (a <= b)) << 31
            ge = int(not (a >= -b)) << 30
            if le | ge != 0:
                in_bounds = False

            result_vector.append(le | ge)

        if op.iflags & IF_RC:
            cr6 = 0b0010 if in_bounds else 0b0000
            self.setCr(cr6, 6)

        op.opers[0].setValues(op, self, result_vector)

    i_vcmpeqfp = vcmpeq
    i_vcmpgefp = vcmpge
    i_vcmpgtfp = vcmpgt

    # Integer max

    def vminmax(self, op, cmp):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        for elem1, elem2 in zip(a, b):
            result_vector.append(elem1 if cmp(elem1, elem2) else elem2)

        op.opers[0].setValues(op, self, result_vector)

    def vmax(self, op):
        return self.vminmax(op, lambda a, b: a >= b)

    def vmin(self, op):
        return self.vminmax(op, lambda a, b: a < b)

    i_vmaxsb = vmax
    i_vmaxsh = vmax
    i_vmaxsw = vmax
    i_vmaxub = vmax
    i_vmaxuh = vmax
    i_vmaxuw = vmax
    i_vmaxfp = vmax
    i_vminsb = vmin
    i_vminsh = vmin
    i_vminsw = vmin
    i_vminub = vmin
    i_vminuh = vmin
    i_vminuw = vmin
    i_vminfp = vmin

    # Multiplication

    def i_vmladduhm(self, op):
        result_vector = []
        a = op.opers[1].getValues(op, self)
        b = op.opers[2].getValues(op, self)
        c = op.opers[3].getValues(op, self)
        for elem1, elem2, elem3 in zip(a, b, c):
            result_vector.append(((elem1 * elem2) + elem3) & 0xffff)

        op.opers[0].setValues(op, self, result_vector)

    def i_vmhaddshs(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)
        for a, b, c in zip(vA, vB, vC):
            prod = a * b
            result_vector.append(self.signed_saturate((prod >> 15) + c, 2))

        op.opers[0].setValues(op, self, result_vector)

    def i_vmhraddshs(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)
        for a, b, c in zip(vA, vB, vC):
            prod = (a * b) + 0x4000
            result_vector.append(self.signed_saturate((prod >> 15) + c, 2))

        op.opers[0].setValues(op, self, result_vector)

    def vmsum(self, op, func):
        result_vector = []
        # We use groups of multiple vA & vB for each vC
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)

        groupsize = op.opers[1].elemcount // 4
        vA_group = [vA[i:i + groupsize] for i in range(0, len(vA), groupsize)]
        vB_group = [vB[i:i + groupsize] for i in range(0, len(vB), groupsize)]
        for a_group, b_group, c in zip(vA_group, vB_group, vC):
            tmp = 0
            for a, b in zip(a_group, b_group):
                tmp += a * b

            result_vector.append(func(tmp + c, op.opers[3].elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def vmsum_modulo(self, op):
        self.vmsum(op, self.modulo)

    i_vmsummbm = vmsum_modulo
    i_vmsumshm = vmsum_modulo
    i_vmsumubm = vmsum_modulo
    i_vmsumuhm = vmsum_modulo

    def i_vmsumshs(self, op):
        self.vmsum(op, self.signed_saturate)

    def i_vmsumuhs(self, op):
        self.vmsum(op, self.unsigned_saturate)

    def vmul(self, op, start):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vA_subset = [vA[i] for i in range(start, len(vA), 2)]
        vB_subset = [vB[i] for i in range(start, len(vB), 2)]
        for a, b in zip(vA_subset, vB_subset):
            result_vector.append(a * b)

        op.opers[0].setValues(op, self, result_vector)

    def vmul_even(self, op):
        self.vmul(op, 0)

    def vmul_odd(self, op):
            self.vmul(op, 1)

    i_vmulesb = vmul_even
    i_vmulesh = vmul_even
    i_vmuleub = vmul_even
    i_vmuleuh = vmul_even
    i_vmulosb = vmul_odd
    i_vmulosh = vmul_odd
    i_vmuloub = vmul_odd
    i_vmulouh = vmul_odd

    def i_vmaddfp(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)
        for a, b, c in zip(vA, vB, vC):
            result_vector.append((a * c) + b)

        op.opers[0].setValues(op, self, result_vector)

    def i_vnmsubfp(self, op):
        result_vector = []
        vA = op.opers[1].getValues(op, self)
        vB = op.opers[2].getValues(op, self)
        vC = op.opers[3].getValues(op, self)
        for a, b, c in zip(vA, vB, vC):
            result_vector.append(-((a * c) - b))

        op.opers[0].setValues(op, self, result_vector)

    # Merging

    def vmrg(self, op, elemslice):
        result_vector = []
        a = op.opers[1].getValues(op, self)[elemslice]
        b = op.opers[2].getValues(op, self)[elemslice]
        for elem1, elem2 in zip(a, b):
            result_vector.extend([elem1, elem2])

        op.opers[0].setValues(op, self, result_vector)

    def vmrgh(self, op):
        return self.vmrg(op, slice(0, op.opers[1].elemcount // 2))

    def vmrgl(self, op):
        return self.vmrg(op, slice(op.opers[1].elemcount // 2, op.opers[1].elemcount))

    i_vmrghb = vmrgh
    i_vmrghh = vmrgh
    i_vmrghw = vmrgh
    i_vmrglb = vmrgl
    i_vmrglh = vmrgl
    i_vmrglw = vmrgl

    # Conversion
    def i_vcfsx(self, op):
        uimm = self.getOperValue(op, 2)
        vB = op.opers[1].getValues(op, self)
        result_vector = [b / (2**uimm) for b in vB]
        op.opers[0].setValues(op, self, result_vector)

    i_vcfux = i_vcfsx

    def i_vctsxs(self, op):
        uimm = self.getOperValue(op, 2)
        vB = op.opers[1].getValues(op, self)
        result_vector = [int(self.signed_saturate(b * (2**uimm), 4)) for b in vB]
        op.opers[0].setValues(op, self, result_vector)

    i_vctuxs = i_vctsxs

    # Floating-point rounding
    def vrfi(self, op, func):
        vB = op.opers[1].getValues(op, self)
        op.opers[0].setValues(op, self, [func(b) for b in vB])

    def i_vrfim(self, op):
        self.vrfi(op, math.floor)

    def i_vrfin(self, op):
        self.vrfi(op, round)

    def i_vrfip(self, op):
        self.vrfi(op, math.ceil)

    def i_vrfiz(self, op):
        self.vrfi(op, int)

    # Data stream stuff
    # We don't currently do anything with these
    i_dss = i_nop
    i_dssall = i_nop
    i_dst = i_nop
    i_dstst = i_nop
    i_dststt = i_nop
    i_dstt = i_nop

    ### SPE Instructions
    def i_evabs(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        for a in rA:
            result_vector.append(abs(a) if a != 0x80000000 else 0x80000000)

        op.opers[0].setValues(op, self, result_vector)

    def i_evaddiw(self, op):
        rB = op.opers[1].getValues(op, self)
        uimm = self.getOperValue(op, 2)
        result_vector = [self.modulo(b + uimm, op.opers[1].elemsize) for b in rB]
        op.opers[0].setValues(op, self, result_vector)

    i_evaddw = i_vadduwm

    def i_evcntlsw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        for a in rA:
            elemsize = op.opers[1].elemsize
            is_signed = e_bits.is_signed(a, op.opers[1].elemsize)
            leading_bits = CLO(a, elemsize) if is_signed else CLZ(a, elemsize)
            result_vector.append(leading_bits)

        op.opers[0].setValues(op, self, result_vector)

    def i_evcntlzw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        for a in rA:
            elemsize = op.opers[1].elemsize
            result_vector.append(CLZ(a, elemsize))

        op.opers[0].setValues(op, self, result_vector)

    def i_eveqv(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        result_vector = [e_bits.unsigned(~(a ^ b), op.opers[1].elemsize) for a, b in zip(rA, rB)]
        op.opers[0].setValues(op, self, result_vector)

    def i_evextsb(self, op, opsize=1):
        rA = op.opers[1].getValues(op, self)
        result_vector = [e_bits.sign_extend(a, opsize, op.opers[1].elemsize) for a in rA]
        op.opers[0].setValues(op, self, result_vector)

    def i_evextsh(self, op):
        self.i_evextsb(op, opsize=2)

    def i_evfsabs(self, op):
        rA = op.opers[1].getValues(op, self)
        op.opers[0].setValues(op, self, [abs(a) for a in rA])

    i_evfsadd = i_vaddfp

    i_evldd = _load_unsigned
    i_evlddx = _load_unsigned
    i_evlddepx = _load_unsigned
    i_evldh = _load_unsigned
    i_evldhx = _load_unsigned
    i_evldw = _load_unsigned
    i_evldwx = _load_unsigned

    def i_evlhhesplat(self, op):
        val = self.getOperValue(op, 1)
        op.opers[0].setValues(op, self, [val, 0, val, 0])

    i_evlhhesplatx = i_evlhhesplat

    def i_evlhhossplat(self, op):
        val = EXTS(self.getOperValue(op, 1), 2, 4)
        op.opers[0].setValues(op, self, [val, val])

    i_evlhhossplatx = i_evlhhossplat

    def i_evlhhousplat(self, op):
        val = self.getOperValue(op, 1)
        op.opers[0].setValues(op, self, [0, val, 0, val])

    i_evlhhousplatx = i_evlhhousplat

    def i_evlwhe(self, op):
        valh, vall = struct.unpack(">2H", struct.pack(">I", self.getOperValue(op, 1)))
        op.opers[0].setValues(op, self, [valh, 0, vall, 0])

    i_evlwhex = i_evlwhe

    def i_evlwhos(self, op):
        valh, vall = struct.unpack(">2h", struct.pack(">I", self.getOperValue(op, 1)))
        op.opers[0].setValues(op, self, [valh, vall])

    i_evlwhosx = i_evlwhos

    def i_evlwhou(self, op):
        valh, vall = struct.unpack(">2H", struct.pack(">I", self.getOperValue(op, 1)))
        op.opers[0].setValues(op, self, [valh, vall])

    i_evlwhoux = i_evlwhou

    def i_evlwhsplat(self, op):
        valh, vall = struct.unpack(">2H", struct.pack(">I", self.getOperValue(op, 1)))
        op.opers[0].setValues(op, self, [valh, valh, vall, vall])

    i_evlwhsplatx = i_evlwhsplat

    def i_evlwwsplat(self, op):
        val = self.getOperValue(op, 1)
        op.opers[0].setValues(op, self, [val, val])

    i_evlwwsplatx = i_evlwwsplat

    i_evmergehi = vmrgh
    i_evmergelo = vmrgl

    def i_evmergehilo(self, op):
        a = op.opers[1].getValues(op, self)[0]
        b = op.opers[2].getValues(op, self)[1]
        op.opers[0].setValues(op, self, [a, b])

    def i_evmergelohi(self, op):
        a = op.opers[1].getValues(op, self)[1]
        b = op.opers[2].getValues(op, self)[0]
        op.opers[0].setValues(op, self, [a, b])

    def i_evmra(self, op):
        val = self.getOperValue(op, 1)
        self.setOperValue(op, 0, val)
        self.setRegister(REG_ACC, val)

    def evaddacc(self, op, func):
        result_vector = []
        # Get ACC as an operand so we can use it like our vectors
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)

        rA = op.opers[1].getValues(op, self)
        accVals = accOper.getValues(op, self)

        result_vector = []
        for a, acc in zip(rA, accVals):
            result_vector.append(func(a + acc, rD.elemsize))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

    def i_evaddsmiaaw(self, op):
        self.evaddacc(op, self.modulo)

    i_evaddumiaaw = i_evaddsmiaaw

    def i_evaddssiaaw(self, op):
        self.evaddacc(op, self.signed_saturate)

    def i_evaddusiaaw(self, op):
        self.evaddacc(op, self.unsigned_saturate)

    # Multiply
    def evmhg(self, op, idx, main_func, secondary_func, fractional=False, acc=False):
        a = op.opers[1].getValues(op, self)[idx]
        b = op.opers[2].getValues(op, self)[idx]

        intermediate = a * b
        if fractional:
            intermediate <<= 1
        val = secondary_func(main_func(self.getRegister(REG_ACC), intermediate), 8)
        self.setOperValue(op, 0, val)
        if acc:
            self.setRegister(REG_ACC, val)

    def i_evmhegsmfaa(self, op):
        self.evmhg(op, 2, operator.add, self.modulo, fractional=True, acc=True)

    def i_evmhegsmfan(self, op):
        self.evmhg(op, 2, operator.sub, self.modulo, fractional=True, acc=True)

    def i_evmhegsmiaa(self, op):
        self.evmhg(op, 2, operator.add, self.modulo, acc=True)

    def i_evmhegsmian(self, op):
        self.evmhg(op, 2, operator.sub, self.modulo, acc=True)

    i_evmhegumiaa = i_evmhegsmiaa
    i_evmhegumian = i_evmhegsmian

    def i_evmhogsmfaa(self, op):
        self.evmhg(op, 3, operator.add, self.modulo, fractional=True, acc=True)

    def i_evmhogsmfan(self, op):
        self.evmhg(op, 3, operator.sub, self.modulo, fractional=True, acc=True)

    def i_evmhogsmiaa(self, op):
        self.evmhg(op, 3, operator.add, self.modulo, acc=True)

    def i_evmhogsmian(self, op):
        self.evmhg(op, 3, operator.sub, self.modulo, acc=True)

    i_evmhogumiaa = i_evmhogsmiaa
    i_evmhogumian = i_evmhogsmian

    def _second(self, a, b):
        return b

    def evmh(self, op, main_func, secondary_func, fractional=False, acc=False, even=True):
        idx = [0, 2] if even else [1, 3]
        rA = operator.itemgetter(idx[0], idx[1])(op.opers[1].getValues(op, self))
        rB = operator.itemgetter(idx[0], idx[1])(op.opers[2].getValues(op, self))
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []
        for a, b, c in zip(rA, rB, accVals):
            intermediate = a * b
            if fractional:
                intermediate <<= 1
            val = secondary_func(main_func(c, intermediate), 4)
            result_vector.append(val)

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

    def i_evmhesmf(self, op):
        self.evmh(op, self._second, self.modulo, fractional=True)

    def i_evmhesmfa(self, op):
        self.evmh(op, self._second, self.modulo, fractional=True, acc=True)

    def i_evmhesmfaaw(self, op):
        self.evmh(op, operator.add, self.modulo, fractional=True, acc=True)

    def i_evmhesmfanw(self, op):
        self.evmh(op, operator.sub, self.modulo, fractional=True, acc=True)

    def i_evmhesmi(self, op):
        self.evmh(op, self._second, self.modulo)

    def i_evmhesmia(self, op):
        self.evmh(op, self._second, self.modulo, acc=True)

    def i_evmhesmiaaw(self, op):
        self.evmh(op, operator.add, self.modulo, acc=True)

    def i_evmhesmianw(self, op):
        self.evmh(op, operator.sub, self.modulo, acc=True)

    i_evmheumi = i_evmhesmi
    i_evmheumia = i_evmhesmia
    i_evmheumiaaw = i_evmhesmiaaw
    i_evmheumianw = i_evmhesmianw

    def i_evmhosmf(self, op):
        self.evmh(op, self._second, self.modulo, fractional=True, even=False)

    def i_evmhosmfa(self, op):
        self.evmh(op, self._second, self.modulo, fractional=True, acc=True, even=False)

    def i_evmhosmfaaw(self, op):
        self.evmh(op, operator.add, self.modulo, fractional=True, acc=True, even=False)

    def i_evmhosmfanw(self, op):
        self.evmh(op, operator.sub, self.modulo, fractional=True, acc=True, even=False)

    def i_evmhosmi(self, op):
        self.evmh(op, self._second, self.modulo, even=False)

    def i_evmhosmia(self, op):
        self.evmh(op, self._second, self.modulo, acc=True, even=False)

    def i_evmhosmiaaw(self, op):
        self.evmh(op, operator.add, self.modulo, acc=True, even=False)

    def i_evmhosmianw(self, op):
        self.evmh(op, operator.sub, self.modulo, acc=True, even=False)

    i_evmhoumi = i_evmhosmi
    i_evmhoumia = i_evmhosmia
    i_evmhoumiaaw = i_evmhosmiaaw
    i_evmhoumianw = i_evmhosmianw

    def evmwh(self, op, main_func, secondary_func, fractional=False, acc=False):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []
        for a, b, c in zip(rA, rB, accVals):
            intermediate = a * b
            if fractional:
                intermediate <<= 1
            val = secondary_func(main_func(c, intermediate), 8)
            result_vector.append((val >> 32) & 0xffffffff)

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

    def i_evmwhsmf(self, op):
        self.evmwh(op, self._second, self.modulo, fractional=True)

    def i_evmwhsmfa(self, op):
        self.evmwh(op, self._second, self.modulo, fractional=True, acc=True)

    def i_evmwhsmi(self, op):
        self.evmwh(op, self._second, self.modulo)

    def i_evmwhsmia(self, op):
        self.evmwh(op, self._second, self.modulo, acc=True)

    i_evmwhumi = i_evmwhsmi
    i_evmwhumia = i_evmwhsmia

    def evmwl(self, op, main_func, secondary_func, fractional=False, acc=False):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []
        for a, b, c in zip(rA, rB, accVals):
            intermediate = a * b
            if fractional:
                intermediate <<= 1
            val = secondary_func(main_func(c, intermediate), 8)
            result_vector.append(val & 0xffffffff)

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

    def i_evmwlumi(self, op):
        self.evmwl(op, self._second, self.modulo)

    def i_evmwlumia(self, op):
        self.evmwl(op, self._second, self.modulo, acc=True)

    def i_evmwlsmiaaw(self, op):
        self.evmwl(op, operator.add, self.modulo, acc=True)

    def i_evmwlsmianw(self, op):
        self.evmwl(op, operator.sub, self.modulo, acc=True)

    i_evmwlumiaaw = i_evmwlsmiaaw
    i_evmwlumianw = i_evmwlsmianw

    def evmw(self, op, main_func, secondary_func, fractional=False, acc=False):
        rA = op.opers[1].getValues(op, self)[1]
        rB = op.opers[2].getValues(op, self)[1]
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVal = accOper.getValues(op, self)[0]

        intermediate = rA * rB
        if fractional:
            intermediate <<= 1
        val = secondary_func(main_func(accVal, intermediate), 8)
        result_vector = [val]

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

    def i_evmwsmf(self, op):
        self.evmw(op, self._second, self.modulo, fractional=True)

    def i_evmwsmfa(self, op):
        self.evmw(op, self._second, self.modulo, fractional=True, acc=True)

    def i_evmwsmfaa(self, op):
        self.evmw(op, operator.add, self.modulo, fractional=True, acc=True)

    def i_evmwsmfan(self, op):
        self.evmw(op, operator.sub, self.modulo, fractional=True, acc=True)

    def i_evmwsmi(self, op):
        self.evmw(op, self._second, self.modulo)

    def i_evmwsmia(self, op):
        self.evmw(op, self._second, self.modulo, acc=True)

    def i_evmwsmiaa(self, op):
        self.evmw(op, operator.add, self.modulo, acc=True)

    def i_evmwsmian(self, op):
        self.evmw(op, operator.sub, self.modulo, acc=True)

    i_evmwumi = i_evmwsmi
    i_evmwumia = i_evmwsmia
    i_evmwumiaa = i_evmwsmiaa
    i_evmwumian = i_evmwsmian

    def spefscr_set_overflow(self, val, low):
        reg_overflow = REG_SPEFSCR_OV if low else REG_SPEFSCR_OVH
        reg_summary = REG_SPEFSCR_SOV if low else REG_SPEFSCR_SOVH
        summary = self.getRegister(reg_summary)
        self.setRegister(reg_overflow, val)
        self.setRegister(reg_summary, val | summary)

    # Saturation is performed for SPE based on the initial parameters, not on the
    # results of the multiplication.
    def evmhs(self, op, fractional=False, acc=False, even=True):
        idx = [0, 2] if even else [1, 3]
        rA = operator.itemgetter(idx[0], idx[1])(op.opers[1].getValues(op, self))
        rB = operator.itemgetter(idx[0], idx[1])(op.opers[2].getValues(op, self))
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []
        idx = 0
        for a, b, c in zip(rA, rB, accVals):
            intermediate = a * b
            if fractional:
                intermediate <<= 1

            if e_bits.unsigned(a, 2) == 0x8000 and e_bits.unsigned(b, 2) == 0x8000:
                val = 0x7fffffff
                overflow = 1
            else:
                val = intermediate
                overflow = 0

            self.spefscr_set_overflow(overflow, idx)
            # val = secondary_func(main_func(c, intermediate), 4)
            result_vector.append(val)
            idx += 1

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

    def i_evmhessf(self, op):
        self.evmhs(op, fractional=True, acc=False, even=True)

    def i_evmhessfa(self, op):
        self.evmhs(op, fractional=True, acc=True, even=True)

    def i_evmhossf(self, op):
        self.evmhs(op, fractional=True, acc=False, even=False)

    def i_evmhossfa(self, op):
        self.evmhs(op, fractional=True, acc=True, even=False)

    def evmhsw(self, op, func, fractional=False, even=True):
        idx = [0, 2] if even else [1, 3]
        rA = operator.itemgetter(idx[0], idx[1])(op.opers[1].getValues(op, self))
        rB = operator.itemgetter(idx[0], idx[1])(op.opers[2].getValues(op, self))
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []

        # Based pretty closely on pseudocode in SPEPEM
        temp = rA[0] * rB[0]
        if fractional:
            temp <<= 1

        if e_bits.unsigned(rA[0], 2) == 0x8000 and e_bits.unsigned(rB[0], 2) == 0x8000:
            temp = 0x7fffffff
            multiply_overflow_high = 1
        else:
            multiply_overflow_high = 0

        temp = func(accVals[0], e_bits.signed(temp, 4))
        overflow_high = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(overflow_high, BIT(temp, 31), 0x80000000, 0x7fffffff, temp))

        temp = rA[1] * rB[1]
        if fractional:
            temp <<= 1

        if e_bits.unsigned(rA[1], 2) == 0x8000 and e_bits.unsigned(rB[1], 2) == 0x8000:
            temp = 0x7fffffff
            multiply_overflow_low = 1
        else:
            multiply_overflow_low = 0

        temp = func(accVals[1], e_bits.signed(temp, 4))
        overflow_low = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(overflow_low, BIT(temp, 31), 0x80000000, 0x7fffffff, temp))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(multiply_overflow_high | overflow_high, low=False)
        self.spefscr_set_overflow(multiply_overflow_low | overflow_low, low=True)

    def i_evmhessfaaw(self, op):
        self.evmhsw(op, operator.add, fractional=True, even=True)

    def i_evmhessfanw(self, op):
        self.evmhsw(op, operator.sub, fractional=True, even=True)

    def i_evmhossfaaw(self, op):
        self.evmhsw(op, operator.add, fractional=True, even=False)

    def i_evmhossfanw(self, op):
        self.evmhsw(op, operator.sub, fractional=True, even=False)

    def i_evmhessiaaw(self, op):
        self.evmhsw(op, operator.add, fractional=False, even=True)

    def i_evmhessianw(self, op):
        self.evmhsw(op, operator.sub, fractional=False, even=True)

    def i_evmhossiaaw(self, op):
        self.evmhsw(op, operator.add, fractional=False, even=False)

    def i_evmhossianw(self, op):
        self.evmhsw(op, operator.sub, fractional=False, even=False)

    def evmhuw(self, op, func, sat_val, even=True):
        idx = [0, 2] if even else [1, 3]
        rA = operator.itemgetter(idx[0], idx[1])(op.opers[1].getValues(op, self))
        rB = operator.itemgetter(idx[0], idx[1])(op.opers[2].getValues(op, self))
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []

        # Based pretty closely on pseudocode in SPEPEM
        temp = rA[0] * rB[0]
        temp = func(accVals[0], temp & 0xffffffff)
        overflow_high = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(overflow_high, 0, sat_val, sat_val, temp))

        temp = rA[1] * rB[1]

        temp = func(accVals[1], temp & 0xffffffff)
        overflow_low = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(overflow_low, 0, sat_val, sat_val, temp))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(overflow_high, low=False)
        self.spefscr_set_overflow(overflow_low, low=True)

    def i_evmheusiaaw(self, op):
        self.evmhuw(op, operator.add, 0xffffffff, even=True)

    def i_evmheusianw(self, op):
        self.evmhuw(op, operator.sub, 0x00000000, even=True)

    def i_evmhousiaaw(self, op):
        self.evmhuw(op, operator.add, 0xffffffff, even=False)

    def i_evmhousianw(self, op):
        self.evmhuw(op, operator.sub, 0x00000000, even=False)

    def evmwhs(self, op, func, fractional=False, acc=False):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)

        result_vector = []

        # Based pretty closely on pseudocode in SPEPEM
        temp = rA[0] * rB[0]
        if fractional:
            temp <<= 1

        if e_bits.unsigned(rA[0], 4) == 0x80000000 and e_bits.unsigned(rB[0], 4) == 0x80000000:
            temp = 0x7fffffff
            movh = 1
        else:
            temp = (temp >> 32) & 0xffffffff
            movh = 0
        result_vector.append(temp)

        temp = rA[1] * rB[1]
        if fractional:
            temp <<= 1

        if e_bits.unsigned(rA[1], 4) == 0x80000000 and e_bits.unsigned(rB[1], 4) == 0x80000000:
            temp = 0x7fffffff
            movl = 1
        else:
            temp = (temp >> 32) & 0xffffffff
            movl = 0
        result_vector.append(temp)

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(movh, low=False)
        self.spefscr_set_overflow(movl, low=True)

    def i_evmwhssf(self, op):
        self.evmwhs(op, None, fractional=True, acc=False)

    def i_evmwhssfa(self, op):
        self.evmwhs(op, None, fractional=True, acc=True)

    def evmwssf(self, op, fractional=False, acc=False):
        rA = op.opers[1].getValues(op, self)[1]
        rB = op.opers[2].getValues(op, self)[1]
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        # accVals = accOper.getValues(op, self)

        result_vector = []

        # Based pretty closely on pseudocode in SPEPEM
        temp = rA * rB
        if fractional:
            temp <<= 1

        if e_bits.unsigned(rA, 4) == 0x8000_0000 and e_bits.unsigned(rB, 4) == 0x8000_0000:
            temp = 0x7fff_ffff_ffff_ffff
            mov = 1
        else:
            mov = 0
        result_vector.append(temp)

        rD.setValues(op, self, result_vector)
        if acc:
            accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(0, low=False)
        self.spefscr_set_overflow(mov, low=True)

    def i_evmwssf(self, op):
        self.evmwssf(op, fractional=True, acc=False)

    def i_evmwssfa(self, op):
        self.evmwssf(op, fractional=True, acc=True)

    def evmwssfa(self, op, func):
        rA = op.opers[1].getValues(op, self)[1]
        rB = op.opers[2].getValues(op, self)[1]
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        # Based pretty closely on pseudocode in SPEPEM
        temp1 = (rA * rB) << 1
        if e_bits.unsigned(rA, 4) == 0x8000_0000 and e_bits.unsigned(rB, 4) == 0x8000_0000:
            temp2 = 0x7fff_ffff_ffff_ffff
            mov = 1
        else:
            temp2 = temp1 & 0xffff_ffff_ffff_ffff
            mov = 0

        # The SPEPEM explicitly states that saturation does NOT occur on this step,
        # but the hardware docs state the opposite. We're going with the hardware here.
        # Note that this could produce a 65-bit value, so we can't use BIT()
        temp3 = func(e_bits.signed(accVals[0], 8), e_bits.signed(temp2, 8))
        temp3_0 = (temp3 & 0x1_0000_0000_0000_0000) >> 64
        temp3_1 = (temp3 & 0x8000_0000_0000_0000) >> 63
        temp3_1_64 = temp3 & 0xffff_ffff_ffff_ffff
        ov = temp3_0 ^ temp3_1
        temp = SATURATE_SPE(ov, temp3_0, 0x8000_0000_0000_0000, 0x7fff_ffff_ffff_ffff, temp3_1_64)
        rD.setValues(op, self, [temp])
        accOper.setValues(op, self, [temp])

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(0, low=False)
        self.spefscr_set_overflow(ov | mov, low=True)

    def i_evmwssfaa(self, op):
        self.evmwssfa(op, operator.add)

    def i_evmwssfan(self, op):
        self.evmwssfa(op, operator.sub)

    def evmwls(self, op, func):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []

        temp = rA[0] * rB[0]
        temp = func(accVals[0], temp & 0xffff_ffff)
        ovh = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(ovh, BIT(temp, 31), 0x8000_0000, 0x7fff_ffff, temp & 0xffff_ffff))

        temp = rA[1] * rB[1]
        temp = func(accVals[1], temp & 0xffff_ffff)
        ovl = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(ovl, BIT(temp, 31), 0x8000_0000, 0x7fff_ffff, temp & 0xffff_ffff))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def i_evmwlssiaaw(self, op):
        self.evmwls(op, operator.add)

    def i_evmwlssianw(self, op):
        self.evmwls(op, operator.sub)

    def evmwlu(self, op, func, sat_val):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = []

        temp = rA[0] * rB[0]
        temp = func(accVals[0], temp & 0xffff_ffff)
        ovh = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(ovh, 0, sat_val, sat_val, temp & 0xffff_ffff))

        temp = rA[1] * rB[1]
        temp = func(accVals[1], temp & 0xffff_ffff)
        ovl = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(ovl, 0, sat_val, sat_val, temp & 0xffff_ffff))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

        # How these register bits are set are documented differently in the chip docs
        # and the SPEPEM. The hardware seems to do what the chip does, so we do that.
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def i_evmwlusiaaw(self, op):
        self.evmwlu(op, operator.add, 0xffff_ffff)

    def i_evmwlusianw(self, op):
        self.evmwlu(op, operator.sub, 0x0000_0000)

    def i_evdivws(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]

        dividendh = rA[0]
        dividendl = rA[1]
        divisorh = rB[0]
        divisorl = rB[1]

        ovh = 0
        ovl = 0
        result_vector = []

        if dividendh < 0 and divisorh == 0:
            result_vector.append(0x8000_0000)
            ovh = 1
        elif dividendh >= 0 and divisorh == 0:
            result_vector.append(0x7fff_ffff)
            ovh = 1
        elif dividendh == 0x8000_0000 and divisorh == 0xffff_ffff:
            result_vector.append(0x7fff_ffff)
            ovh = 1
        else:
            result_vector.append(dividendh // divisorh)

        if dividendl < 0 and divisorl == 0:
            result_vector.append(0x8000_0000)
            ovl = 1
        elif dividendl >= 0 and divisorl == 0:
            result_vector.append(0x7fff_ffff)
            ovl = 1
        elif dividendl == 0x8000_0000 and divisorl == 0xffff_ffff:
            result_vector.append(0x7fff_ffff)
            ovl = 1
        else:
            result_vector.append(dividendl // divisorl)

        rD.setValues(op, self, result_vector)
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def i_evdivwu(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        rD = op.opers[0]

        dividendh = rA[0]
        dividendl = rA[1]
        divisorh = rB[0]
        divisorl = rB[1]

        ovh = 0
        ovl = 0
        result_vector = []

        if divisorh == 0:
            result_vector.append(0xffff_ffff)
            ovh = 1
        else:
            result_vector.append(dividendh // divisorh)

        if divisorl == 0:
            result_vector.append(0xffff_ffff)
            ovl = 1
        else:
            result_vector.append(dividendl // divisorl)

        rD.setValues(op, self, result_vector)
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def evcmp(self, op, cmp):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)

        ch = cmp(rA[0], rB[0])
        cl = cmp(rA[1], rB[1])
        val = ch << 3 | cl << 2 | (ch | cl) << 1 | (ch & cl)
        self.setOperValue(op, 0, val)

    def i_evcmpeq(self, op):
        self.evcmp(op, operator.eq)

    def i_evcmpgts(self, op):
        self.evcmp(op, operator.gt)

    i_evcmpgtu = i_evcmpgts

    def i_evcmplts(self, op):
        self.evcmp(op, operator.lt)

    i_evcmpltu = i_evcmplts

    i_evand = i_and
    i_evandc = i_andc
    i_evnand = i_nand
    i_evnor = i_nor
    i_evor = i_or
    i_evorc = i_orc
    i_evxor = i_xor

    def i_evneg(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)

        if rA[0] == e_bits.unsigned(0x8000_0000, 4):
            result_vector.append(0x8000_0000)
        else:
            result_vector.append(~rA[0] + 1)

        if rA[1] == e_bits.unsigned(0x8000_0000, 4):
            result_vector.append(0x8000_0000)
        else:
            result_vector.append(~rA[1] + 1)

        op.opers[0].setValues(op, self, result_vector)

    def i_evrlw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        result_vector = [ROTL(rA[0], rB[0] & 0x1f, 32), ROTL(rA[1], rB[1] & 0x1f, 32)]
        op.opers[0].setValues(op, self, result_vector)

    def i_evrlwi(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        uimm = self.getOperValue(op, 2)
        result_vector = [ROTL(rA[0], uimm, 32), ROTL(rA[1], uimm, 32)]
        op.opers[0].setValues(op, self, result_vector)

    def i_evrndw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        result_vector = []
        result_vector.append((rA[0] + 0x8000) & 0xffff_0000)
        result_vector.append((rA[1] + 0x8000) & 0xffff_0000)
        op.opers[0].setValues(op, self, result_vector)

    def i_evsel(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        ch = (self.getOperValue(op, 3) & 0x8) >> 3
        cl = (self.getOperValue(op, 3) & 0x4) >> 2

        result_vector.append(rA[0] if ch else rB[0])
        result_vector.append(rA[1] if cl else rB[1])
        op.opers[0].setValues(op, self, result_vector)

    def i_evslw(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        nh = rB[0] & 0x3f
        nl = rB[1] & 0x3f
        result_vector = [(rA[0] << nh) & 0xffff_ffff, (rA[1] << nl) & 0xffff_ffff]
        op.opers[0].setValues(op, self, result_vector)

    def i_evslwi(self, op):
        rA = op.opers[1].getValues(op, self)
        n = self.getOperValue(op, 2)
        result_vector = [(rA[0] << n) & 0xffff_ffff, (rA[1] << n) & 0xffff_ffff]
        op.opers[0].setValues(op, self, result_vector)

    def i_evsrwis(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        n = self.getOperValue(op, 2)

        result_vector.append(rA[0] >> n)
        if rA[0] & 0x8000_0000:
            result_vector[0] |= ((1 << n) - 1) << (32 - n)

        result_vector.append(rA[1] >> n)
        if rA[1] & 0x8000_0000:
            result_vector[1] |= ((1 << n) - 1) << (32 - n)

        op.opers[0].setValues(op, self, result_vector)

    def i_evsrwiu(self, op):
        rA = op.opers[1].getValues(op, self)
        n = self.getOperValue(op, 2)
        op.opers[0].setValues(op, self, [rA[0] >> n, rA[1] >> n])

    def i_evsrws(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        nh = rB[0] & 0x3f
        nl = rB[1] & 0x3f

        result_vector.append(rA[0] >> nh)
        if rA[0] & 0x8000_0000:
            result_vector[0] |= ((1 << nh) - 1) << (32 - nh)

        result_vector.append(rA[1] >> nl)
        if rA[1] & 0x8000_0000:
            result_vector[1] |= ((1 << nl) - 1) << (32 - nl)

        op.opers[0].setValues(op, self, result_vector)

    def i_evsrwu(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        nh = rB[0] & 0x3f
        nl = rB[1] & 0x3f
        op.opers[0].setValues(op, self, [rA[0] >> nh, rA[1] >> nl])

    def i_evsubfsmiaaw(self, op):
        rA = op.opers[1].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        result_vector = [(accVals[0] - rA[0]) & 0xffff_ffff, (accVals[1] - rA[1]) & 0xffff_ffff]
        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)

    i_evsubfumiaaw = i_evsubfsmiaaw

    def i_evsubfssiaaw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        temp = accVals[0] - rA[0]
        ovh = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(ovh, BIT(temp, 31), 0x8000_0000, 0x7fff_ffff, temp & 0xffff_ffff))

        temp = accVals[1] - rA[1]
        ovl = BIT(temp, 31) ^ BIT(temp, 32)
        result_vector.append(SATURATE_SPE(ovl, BIT(temp, 31), 0x8000_0000, 0x7fff_ffff, temp & 0xffff_ffff))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def i_evsubfusiaaw(self, op):
        result_vector = []
        rA = op.opers[1].getValues(op, self)
        rD = op.opers[0]
        accOper = PpcSPEVRegOper(REG_ACC, rD.va, rD.elemsize, rD.signed, rD.floating)
        accVals = accOper.getValues(op, self)

        temp = accVals[0] - rA[0]
        ovh = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(ovh, BIT(temp, 31), 0x0, 0x0, temp & 0xffff_ffff))

        temp = accVals[1] - rA[1]
        ovl = BIT(temp, 31)
        result_vector.append(SATURATE_SPE(ovl, BIT(temp, 31), 0x0, 0x0, temp & 0xffff_ffff))

        rD.setValues(op, self, result_vector)
        accOper.setValues(op, self, result_vector)
        self.spefscr_set_overflow(ovh, low=False)
        self.spefscr_set_overflow(ovl, low=True)

    def i_evsubfw(self, op):
        rA = op.opers[1].getValues(op, self)
        rB = op.opers[2].getValues(op, self)
        op.opers[0].setValues(op, self, [(rB[0] - rA[0]) & 0xffff_ffff, (rB[1] - rA[1]) & 0xffff_ffff])

    def i_evsubifw(self, op):
        # SPE PEM says value is written to ACC, hardware docs do not. This follows hardware.
        uimm = self.getOperValue(op, 1)
        rB = op.opers[2].getValues(op, self)
        op.opers[0].setValues(op, self, [(rB[0] - uimm) & 0xffff_ffff, (rB[1] - uimm) & 0xffff_ffff])

    def i_evsplatfi(self, op):
        simm = self.getOperValue(op, 1)
        val = (simm << 27) & 0xffff_ffff
        op.opers[0].setValues(op, self, [val, val])

    def i_evsplati(self, op):
        simm = self.getOperValue(op, 1)
        op.opers[0].setValues(op, self, [simm, simm])

    i_evstdd = _store_signed
    i_evstddx = _store_signed
    i_evstddepx = _store_signed
    i_evstdh = _store_signed
    i_evstdw = _store_signed
    i_evstdhx = _store_signed
    i_evstdwx = _store_signed

    def evstw(self, op, offset):
        rS = op.opers[0].getValues(op, self)
        rA = self.getOperAddr(op, 1)
        width = op.opers[1].getWidth(self)

        for i in range(offset, len(rS), width):
            addr = rA + i - offset
            self.writeMemValue(addr, rS[i], width)

    def evstwe(self, op):
        self.evstw(op, 0)

    i_evstwhe = evstwe
    i_evstwhex = evstwe
    i_evstwwe = evstwe
    i_evstwwex = evstwe

    def evstwo(self, op):
        self.evstw(op, 1)

    i_evstwho = evstwo
    i_evstwhox = evstwo
    i_evstwwo = evstwo
    i_evstwwox = evstwo

    def i_brinc(self, op):
        # Note that this instruction is documented on the e200 to only operate on the
        # lower 32 bits of the register, so we take that into account in setting rD.
        n = 16  # Implementation-dependent value, but 16 for e200
        rD = self.getOperValue(op, 0)
        rA = self.getOperValue(op, 1)
        rB = self.getOperValue(op, 2)

        mask = rB & MASK(64 - n, 63)
        a = rA & MASK(64 - n, 63)
        d = BITREVERSE32(1 + (BITREVERSE32(a | ~mask)))

        rD_32_63 = (rA & MASK(32, 63 - n)) | (d & mask)
        val = (rD & MASK(0, 31)) | (rD_32_63 & MASK(32, 63))
        self.setOperValue(op, 0, val)


    '''
    i_se_bclri                         rX, UI5
    i_se_bgeni                         rX, UI5
    i_se_bmaski                        rX, UI5
    i_se_bseti                         rX, UI5
    i_se_btsti                         rX, UI5
    i_e_cmpli instructions, or CR0 for the se_cmpl, e_cmp16i, e_cmph16i, e_cmphl16i, e_cmpl16i, se_cmp,
    i_se_cmph, se_cmphl, se_cmpi, and se_cmpli instructions, is set to reflect the result of the comparison. The
    i_e_cmp16i                             rA, SI
    i_e_cmpi                   crD32, rA, SCI8
    i_se_cmp                              rX, rY
    i_se_cmpi                           rX, UI5
    i_e_cmph                        crD, rA, rB
    i_se_cmph                            rX, rY
    i_e_cmph16i                           rA, SI
    i_e_cmphl                       crD, rA, rB
    i_se_cmphl                           rX, rY
    i_e_cmphl16i                         rA, UI
    i_e_cmpl16i                           rA, UI
    i_e_cmpli                  crD32, rA, SCI8
    i_se_cmpl                             rX, rY
    i_se_cmpli                      rX, OIMM
    i_se_cmph, se_cmphl, se_cmpi, and se_cmpli instructions, is set to reflect the result of the comparison. The
    i_e_cmph                        crD, rA, rB
    i_se_cmph                            rX, rY
    i_e_cmph16i                           rA, SI
    i_e_cmphl                       crD, rA, rB
    i_se_cmphl                           rX, rY
    i_e_cmphl16i                         rA, UI
    i_e_crnand               crbD, crbA, crbB
    i_e_crnor               crbD, crbA, crbB
    i_e_cror                 crbD, crbA, crbB
    i_e_crorc               crbD, crbA, crbB
    i_e_cror                 crbD, crbA, crbB
    i_e_crorc               crbD, crbA, crbB
    i_e_crxor                crbD, crbA, crbB
    i_se_illegal
    i_se_illegal is used to request an illegal instruction exception. A program interrupt is generated. The contents
    i_se_isync
    i_se_isync instruction have been performed.
    i_e_lmw                         rD, D8(rA)
    i_e_lwz                           rD, D(rA)                                                             (D-mode)
    i_se_lwz                       rZ, SD4(rX)                                                            (SD4-mode)
    i_e_lwzu                         rD, D8(rA)                                                            (D8-mode)
    i_e_mcrf                          crD, crS
    i_se_mfar                         rX, arY
    i_se_mfctr                             rX
    i_se_mflr                              rX
    i_se_mr                             rX, rY
    i_se_mtar                         arX, rY
    i_se_mtctr                             rX
    i_se_mtlr                              rX
    i_se_rfci
    i_se_rfi
    i_e_rlw                           rA, rS, rB                                                               (Rc = 0)
    i_e_rlw.                          rA, rS, rB                                                               (Rc = 1)
    i_e_rlwi                          rA, rS, SH                                                               (Rc = 0)
    i_e_rlwi.                         rA, rS, SH                                                               (Rc = 1)
    i_e_rlwimi             rA, rS, SH, MB, ME
    i_e_rlwinm              rA, rS, SH, MB, ME
    i_e_rlwimi             rA, rS, SH, MB, ME
    i_e_rlwinm              rA, rS, SH, MB, ME
    i_se_sc provides the same functionality as sc without the LEV field. se_rfi, se_rfci, se_rfdi, and se_rfmci
    i_se_sc
    i_se_sc is used to request a system service. A system call interrupt is generated. The contents of the MSR
    i_e_stmw                        rS, D8(rA)                                                               (D8-mode)
    i_se_sub                            rX, rY
    i_se_subf                           rX, rY
    i_e_subfic                    rD, rA, SCI8                                                                  (Rc = 0)
    i_e_subfic.                   rD, rA, SCI8                                                                  (Rc = 1)
    i_se_subi                       rX, OIMM                                                                 (Rc = 0)
    i_se_subi.                      rX, OIMM                                                                 (Rc = 1)
    '''


"""
import envi.archs.ppc as e_ppc
import envi.memory as e_m

t_arch = e_ppc.PpcModule()
e = t_arch.getEmulator()
m = e_m.MemoryObject()
e.setMemoryObject(m)
m.addMemoryMap(0x0000, 0777, "memmap1", "\xff"*1024)

"""

class Ppc64ServerEmulator(Ppc64RegisterContext, Ppc64ServerModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=Ppc64ServerModule(), endian=endian, psize=psize)
        Ppc64RegisterContext.__init__(self)
        Ppc64ServerModule.__init__(self)

# 32-bit "server" versions of PowerPC are older PowerPC instructions which are
# 32-bit and have only 32-bit registers
class Ppc32ServerEmulator(Ppc32RegisterContext, Ppc32ServerModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=4):
        PpcAbstractEmulator.__init__(self, archmod=Ppc32ServerModule(), endian=endian, psize=psize)
        Ppc32RegisterContext.__init__(self)
        Ppc32ServerModule.__init__(self)

class PpcVleEmulator(Ppc64RegisterContext, PpcVleModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=4):
        PpcAbstractEmulator.__init__(self, archmod=PpcVleModule(), endian=endian, psize=psize)
        Ppc64RegisterContext.__init__(self)
        PpcVleModule.__init__(self)

class Ppc64EmbeddedEmulator(Ppc64RegisterContext, Ppc64EmbeddedModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=8):
        PpcAbstractEmulator.__init__(self, archmod=Ppc64EmbeddedModule(), endian=endian, psize=psize)
        Ppc64RegisterContext.__init__(self)
        Ppc64EmbeddedModule.__init__(self)

class Ppc32EmbeddedEmulator(Ppc64RegisterContext, Ppc32EmbeddedModule, PpcAbstractEmulator):
    def __init__(self, archmod=None, endian=ENDIAN_MSB, psize=4):
        PpcAbstractEmulator.__init__(self, archmod=Ppc32EmbeddedModule(), endian=endian, psize=psize)
        Ppc64RegisterContext.__init__(self)
        Ppc32EmbeddedModule.__init__(self)

'''
In [2]: mnems = {}

In [3]: for lva, lsz, ltype, ltinfo in vw.getLocations(vivisect.LOC_OP):
   ...:     op = vw.parseOpcode(lva)
   ...:     mnems[op.mnem] = mnems.get(op.mnem, 0) + 1
   ...:

In [5]: dist = [(y, x) for x, y in mnems.items()]

In [7]: dist.sort()

In [8]: dist
Out[8]:
[(1, 'add.'),
 (1, 'addic'),
 (1, 'addme'),
 (1, 'and.'),
 (1, 'andis.'),
 (1, 'blrl'),
 (1, 'divw'),
 (1, 'isync'),
 (1, 'lhzu'),
 (1, 'sync'),
 (2, 'addic.'),
 (2, 'lha'),
 (2, 'mtmsr'),
 (2, 'rlwnm'),
 (2, 'stwux'),
 (3, 'bctr'),
 (3, 'extsh.'),
 (3, 'not'),
 (3, 'sraw'),
 (3, 'subfc'),
 (3, 'subfe'),
 (4, 'extsh'),
 (4, 'iseleq'),
 (4, 'sthu'),
 (4, 'subf.'),
 (5, 'bflr'),
 (5, 'lbzu'),
 (5, 'mulhwu'),

    (5, 'sc'),
 (5, 'srawi.'),
 (6, 'andc'),
 (7, 'addc'),
 (7, 'adde'),
 (7, 'stbx'),
 (8, 'btlr'),
 (8, 'neg'),
 (9, 'andi.'),
 (9, 'mfmsr'),
 (9, 'subfic'),
 (10, 'nop'),
 (11, 'lwzu'),

 (11, 'srw'),
 (13, 'lbzx'),
 (13, 'slw'),
 (15, 'mullw'),

 (16, 'bctrl'),

 (17, 'divwu'),
 (17, 'or.'),
 (18, 'stbu'),
 (21, 'oris'),
 (21, 'rlwimi'),

 (26, 'srawi'),
 (32, 'addis'),
 (48, 'sthx'),
 (50, 'lmw'),

 (50, 'stwx'),
 (50, 'subf'),
 (51, 'stmw'),

 (55, 'and'),
 (55, 'cmpli'),
 (62, 'lhzx'),
 (100, 'lwzx'),
 (125, 'mulli'),
 (136, 'or'),
 (141, 'stwu'),
 (154, 'rlwinm.'),
 (157, 'mfspr'),
 (162, 'mtspr'),
 (172, 'blr'),
 (190, 'cmp'),
 (192, 'lbz'),
 (204, 'cmpl'),
 (231, 'stb'),
 (276, 'add'),
 (341, 'mr'),
 (380, 'b'),
 (387, 'bl'),
 (448, 'ori'),
 (627, 'bf'),
 (639, 'cmpi'),
 (641, 'bt'),
 (649, 'lhz'),
 (656, 'sth'),
 (889, 'lis'),
 (960, 'rlwinm'),
 (1033, 'addi'),
 (1188, 'li'),
 (1204, 'lwz'),
 (1389, 'stw')]

'''
