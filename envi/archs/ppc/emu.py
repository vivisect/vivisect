# -*- coding: iso-8859-15 -*-

import sys

import envi
import envi.bits as e_bits
import envi.memory as e_mem

import math
import operator
import struct

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
    arg_def = [(CC_REG, REG_R3 + x) for x in range(8)]
    arg_def.append((CC_STACK_INF, 8))
    retaddr_def = (CC_STACK, 0)
    retval_def = (CC_REG, REG_R3)
    flags = CC_CALLEE_CLEANUP
    align = 4
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
    return (val & _ppc_bitmasks[psize][bit]) >> bit

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
    #print("getCarryBitAtX (%d): 0x%x  0x%x  (%d)" % (bit, a0b, a1b, results))
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
        print('TRAP 0x%08x: %r' % (op.va, op))

    def _sc(self, op):
        print('SC 0x%08x: %r' % (op.va, op))

    def _ehpriv(self, op):
        print('EHPRIV 0x%08x: %r' % (op.va, op))

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
            #print("setOEflags( 0x%x, 0x%x, 0x%x, 0x%x):  cm= 0x%x, cm1= 0x%x, ov= 0x%x" % (result, size, add0, add1, cm, cm1, ov))

        elif mode == OEMODE_ADDSUBNEG:
            cm = getCarryBitAtX((size*8), add0, add1)
            cm1 = getCarryBitAtX((size*8)-1, add0, add1)
            ov = cm != cm1
            #print("setOEflags( 0x%x, 0x%x, 0x%x, 0x%x):  cm= 0x%x, cm1= 0x%x, ov= 0x%x" % (result, size, add0, add1, cm, cm1, ov))

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

    # Beginning of Instruction methods

    ########################### NOP #############################

    def i_nop(self, op):
        pass

    ########################### Integer Select Instructions #############################

    def i_isel(self, op):
        # The 4th operand is which bit to check in the CR register, but using
        # the MSB as bit 0 because PPC. (use psize of 4 because the CR register
        # is always only 32 bits.
        cr_mask = BITMASK(op.opers[3].bit, psize=4)

        # Doesn't matter what the actual bit or CR is because the if the cr bit
        # is set in the CR then the use rA, otherwise use rB
        if self.getRegister(REG_CR) & cr_mask:
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

    def i_nor(self, op):
        src1 = self.getOperValue(op, 1)
        src2 = self.getOperValue(op, 2)
        result = COMPLEMENT(src1 | src2, self.psize)

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
        self.divd(op, oe=True)

    def i_divw(self, op):
        self.divd(op, opsize=4)

    def i_divwo(self, op):
        self.divd(op, opsize=4, oe=True)

    def i_divwu(self, op):
        self.divdu(op, opsize=4)

    def i_divwuo(self, op):
        self.divdu(op, opsize=4, oe=True)

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

    i_efsadd = i_fadds

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

    def i_fctid(self, op, fpsize=8, round=0): # "round" placholder object for when we determine how to do rounding
        frD = self.getOperValue(op, 0)
        frB = self.getOperValue(op, 1)

        if frB in FNAN_ALL_TUP:
            result = FDNZ
            self.setRegister(REG_FPSCR_VXCVI, 1)
            if frB in FNAN_SNAN_TUP:
                self.setRegister(REG_FPSCR_VXSAN, 1)
        else:
            result = int(self.decimal2float(frB)) # TODO how to do rounding? issue #87 (FPSCR[RN])
            if result > (2**63-1):
                result = 0x7FFF_FFFF_FFFF_FFFF
                self.setRegister(FPSCR_VXCVI, 1)

        self.setOperValue(op, 0, result)
        self.setFloatFlags(result, op.iflags, self.psize)
        if op.iflags & IF_RC: self.setFloatCr()

    def i_fctidz(self, op):
        self.i_fctid(op, round=1)

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
    i_lfs = _load_signed
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
#'INS_MCRXR' emulation method missing
#
#'INS_MFFS' emulation method missing
#'INS_MFOCRF' emulation method missing
#'INS_MFPMR' emulation method missing
#'INS_MFTB' emulation method missing
#'INS_MFTMR' emulation method missing
#'INS_MFVSCR' emulation method missing
#
#'INS_MTCR' emulation method missing
#'INS_MTCRF' emulation method missing
#'INS_MTDCR' emulation method missing
#'INS_MTFSB0' emulation method missing
#'INS_MTFSB1' emulation method missing
#'INS_MTFSF' emulation method missing
#'INS_MTFSFI' emulation method missing
#'INS_MTOCRF' emulation method missing
#'INS_MTPMR' emulation method missing
#'INS_MTTMR' emulation method missing
#'INS_MTVSCR' emulation method missing

    i_li = i_mov
    i_mr = i_mov

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
        n = self.getOperValue(op, 1)
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
                self.setFlags(result, so)

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
                self.setFlags(result, so)

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
            else:
                ov = 0
                so = self.getRegister(REG_SO)

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
