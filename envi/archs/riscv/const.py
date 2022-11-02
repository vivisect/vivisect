import enum
from collections import namedtuple

from envi.archs.riscv.const_gen import *


__all__ = [
    # Defined in this file
    'RISCV_CAT',
    'RM_NAMES',
    'FLOAT_CONSTS',
    'SIZE_FLAGS',
    'SIZE_CONSTS',

    # Defined in const_gen
    'RISCV_FORM',
    'RISCV_FIELD',
    'RISCV_INS',
    'RISCV_IF',
    'RISCV_OF',
    'RiscVInsCat',
    'RiscVIns',
    'RiscVField',
    'RiscVImmField',
    'RiscVMemField',
    'RiscVMemSPField',
    'RiscVFieldArgs',
]


class RISCV_CAT(enum.IntFlag):
    """
    RISC-V Instruction categories

    This enumeration helps map the architecture name to the instruction
    categories.  The specific values don't really matter here but in general
    each nibble denotes a "type" of instruction category because I felt like
    organizing them in that way.

    Architecture Types:
      I           integer (base)
      M           multiply & divide instructions
      A           atomic memory & inter-processor sync instructions
      S           supervisor instructions

      F           single-precision floating-point
      D           double-precision floating-point
      Q           quad-precision floating-point

      C           compressed (VLE/16-bit instructions)
      H           hypervisor

      Zicsr       control and status register instructions
      Zifencei    instruction-fetch fence
      Zihintpause PAUSE encoding of FENCE and specific meanings
      Zihintntl   non-temporal locality hints
      Zfh         half-precision floating point
      Zfhmin      half-precision floating point
      Zfinx       floating point in integer registers
      Zdinx       floating point in integer registers
      Zhinx       floating point in integer registers
      Zhinxmin    floating point in integer registers
      Zfa         aditional floating-point instructions
      Zmmul       multiplication subset of M extension

      Zicntr      base counters and timers
      Zihpm       hardware performance counters

      G           IMAFD,Zicsr,Zifencei

      Svnapot     NAPOT translation contiguity
      Svpbmt      page-based memory types
      Svinval     fine-grained address translation cache invalidation

    Placeholder categories
      E           embedded, only 16 "x" register

      L           decimal floating-point
      B           bit manipulation
      J           dynamically translated languages
      T           transactional memory
      P           packed-SIMD
      V           vector

      Zam         misaligned atomics
      Ztso        total store ordering

      Smrnmi      resumable non-maskable interrupts

    All instruction categories that are just placeholders and do not represent
    valid instructions that can be disassembled and emulated by this envi
    module are defined with a leading '_'.
    """
    # Base Functionality
    I           = 1 << 0
    M           = 1 << 1
    A           = 1 << 2
    S           = 1 << 3

    # Floating point
    F           = 1 << 8
    D           = 1 << 9
    Q           = 1 << 10
    L           = 1 << 11  # draft

    # "other" (mostly placeholders)
    C           = 1 << 16
    H           = 1 << 17
    E           = 1 << 18  # draft
    B           = 1 << 19  # draft
    J           = 1 << 20  # draft
    T           = 1 << 21  # draft
    P           = 1 << 22  # draft
    V           = 1 << 23  # draft

    # "Z" categories
    Zicsr       = 1 << 32
    Zifencei    = 1 << 33
    Zihintpause = 1 << 34
    Zihintntl   = 1 << 35  # draft
    Zam         = 1 << 36  # draft
    Zfh         = 1 << 38
    Zfhmin      = 1 << 39
    Zfinx       = 1 << 40
    Zdinx       = 1 << 41
    Zhinx       = 1 << 42
    Zhinxmin    = 1 << 43
    Zfa         = 1 << 44  # draft
    Ztso        = 1 << 45  # frozen
    Zicntr      = 1 << 46  # draft
    Zihpm       = 1 << 47  # draft

    # Supervisor extensions
    Svnapot     = 1 << 48
    Svpbmt      = 1 << 49
    Svinval     = 1 << 50
    Smrnmi      = 1 << 51  # draft

    # Convenience Names
    G        = I | M | A | F | D | Zicsr | Zifencei

    def __contains__(self, item):
        return self.value & int(item) == self.value


# A mapping of rounding modes to strings for printing
RM_NAMES = {
    0b000: 'rne',
    0b001: 'rtz',
    0b010: 'rdn',
    0b011: 'rup',
    0b100: 'rmm',
    0b111: 'dyn',
}


FloatConsts = namedtuple('FloatConsts', [
    'sign', 'emask', 'eoff', 'ebits', 'fmask', 'fdiv', 'fbits',
    'inf', 'snan', 'qnan'])

# Table of conversion constants to go to and from floating point:
#   - SIGN mask
#   - EXPONENT mask
#   - EXPONENT offset
#   - EXPONENT bits
#   - FRACTIONAL mask
#   - FRACTIONAL divisor
#   - FRACTIONAL bits
#   - Infinity
#   - SNaN
#   - QNaN
FLOAT_CONSTS = {
    # IEEE754 half precision (5 bit exp)
    RISCV_OF.HALFWORD: FloatConsts(
        0x8000,
        0x7C00,
        -14,
        5,
        0x03FF,
        2**10,
        10,
        (0x7C00, 0xFC00),
        (0x7E01, 0xFE01),
        (0x7C01, 0xFC01),
    ),

    # IEEE754 single precision (8 bit exp)
    RISCV_OF.WORD: FloatConsts(
        0x8000_0000,
        0x7F80_0000,
        127,
        8,
        0x007F_FFFF,
        2**23,
        23,
        (0x7F80_0000, 0xFF80_0000),
        (0x7FC0_0001, 0xFFC0_0001),
        (0x7F80_0001, 0xFF80_0001),
    ),

    # IEEE754 double precision (11 bit exp)
    RISCV_OF.DOUBLEWORD: FloatConsts(
        0x8000_0000_0000_0000,
        0x7FF0_0000_0000_0000,
        1023,
        11,
        0x000F_FFFF_FFFF_FFFF,
        2**52,
        52,
        (0x7FF0_0000_0000_0000, 0xFFF0_0000_0000_0000),
        (0x7FF8_0000_0000_0001, 0xFFF8_0000_0000_0001),
        (0x7FF0_0000_0000_0001, 0xFFF0_0000_0000_0001),
    ),

    # IEEE754 quad precision (15 bit exp)
    RISCV_OF.QUADWORD: FloatConsts(
        0x8000_0000_0000_0000_0000_0000_0000_0000,
        0x7FFF_0000_0000_0000_0000_0000_0000_0000,
        16382,
        15,
        0x0000_FFFF_FFFF_FFFF_FFFF_FFFF_FFFF_FFFF,
        2**112,
        112,
        (0x7FFF_0000_0000_0000_0000_0000_0000_0000,
         0xFFFF_0000_0000_0000_0000_0000_0000_0000),
        (0x7FFF_8000_0000_0000_0000_0000_0000_0001,
         0xFFFF_8000_0000_0000_0000_0000_0000_0001),
        (0x7FFF_0000_0000_0000_0000_0000_0000_0001,
         0xFFFF_0000_0000_0000_0000_0000_0000_0001),
    ),
}

SIZE_FLAGS = RISCV_OF.BYTE | RISCV_OF.HALFWORD | RISCV_OF.WORD | RISCV_OF.DOUBLEWORD | RISCV_OF.QUADWORD

# size flag to bytes lookup table
SIZE_CONSTS = {
    RISCV_OF.BYTE:       1,
    RISCV_OF.HALFWORD:   2,
    RISCV_OF.WORD:       4,
    RISCV_OF.DOUBLEWORD: 8,
    RISCV_OF.QUADWORD:   16,
}
