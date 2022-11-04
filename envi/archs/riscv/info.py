# RISC-V has a few different variants that are based on a few architecture
# constants
#
#   IALIGN:   instruction address alignment constraint
#   ILEN:     maximum instruction length
#   XLEN:     Size of base "x" (general purpose integer) registers
#   FLEN:     Size of floating point "f" registers (only some archs)
#
# These values are indicated by a combination of the RVXXYYYY description where
# XX is a number and the YYYY is one or more letters that indicate the supported
# instruction categories. Some examples:
#
# RV32I:
#   IALIGN = 32
#   ILEN   = 32
#   XLEN   = 32
#   FLEN   = N/A
#
# RV32IF:
#   IALIGN = 32
#   ILEN   = 32
#   XLEN   = 32
#   FLEN   = 32
#
# RV32ID:
#   IALIGN = 32
#   ILEN   = 32
#   XLEN   = 32
#   FLEN   = 64
#
# RV64IQC:
#   IALIGN = 16
#   ILEN   = 32
#   XLEN   = 64
#   FLEN   = 128
#
# Instruction opcodes are encoded where first 16-bit chunk encodes the size of
# the instruction.  This table is from from the RISC-V spec Section 1.5 "Base
# Instruction-Length Encoding"
# (https://github.com/riscv/riscv-isa-manual/releases/download/Ratified-IMAFDQC/riscv-spec-20191213.pdf

#   FEDCBA9876543210 | ILEN | notes
#   -----------------+------+----
#   xxxxxxxxxxxxxxaa |  16  | aa != 11
#   xxxxxxxxxxxbbb11 |  32  | bbb != 111
#   xxxxxxxxxx011111 |  48  |
#   xxxxxxxxx0111111 |  64  |
#   xnnnxxxxx1111111 |  80+ | (80 + 16*nnn)-bit (nnn != 111)
#   x111xxxxx1111111 | 192+ | Reserved for >= 192 bits

import re

from envi.archs.riscv.const import RISCV_CAT


__all__ = [
    'DEFAULT_RISCV_DESCR',
    'getRiscVCategories',
    'getRiscVNumGPRs',
    'getRiscVIALIGN',
    'getRiscVILEN',
    'getRiscVXLEN',
    'getRiscVFLEN',
]


DEFAULT_RISCV_DESCR = 'RV64GC'


# Valid RISC-V architecture size strings
_valid_xlen = [
    '32',
    '64',
    # '128', placeholder
]

_xlen_pat = r'((?:' + r')|(?:'.join(_valid_xlen) + r'))'
_cat_pat = r'(?:_?(' + r')|_?('.join(c.name for c in RISCV_CAT) + r'))+'
_arch_pat = re.compile(r'^RV%s%s$' % (_xlen_pat, _cat_pat))


def _getRiscVArchInfo(description):
    """
    Utility function to return a bit size value and a RISC-V category value
    based on an architecture description string such as "RV32GC".
    """
    match = _arch_pat.match(description)
    if match:
        # Return a single RISCV_CAT value that incorporates all of the category
        # flags
        cat = RISCV_CAT(sum(RISCV_CAT[o].value for o in match.groups()[1:] if o is not None))
        return (int(match.group(1)), cat)
    else:
        return None


def getRiscVCategories(description):
    """
    Utility function to return a RISC-V categories based on an architecture
    description string such as "RV32GC".
    """
    info = _getRiscVArchInfo(description)
    if info is not None:
        return info[1]
    else:
        return None


def getRiscVNumGPRs(description):
    """
    Utility function to determine how many GPRs there should be.  For all
    non-draft RISC-V variants this should be 32, but for RV32E it is 16.
    """
    if RISCV_CAT.E & getRiscVCategories(description):
        return 16
    else:
        return 32


def getRiscVIALIGN(description):
    """
    Utility function to return the IALIGN value for a RISC-V processor based on
    a description string.

    A RISC-V processor's instruction alignment is 32 bits for all variants
    unless the "C" (compressed) instruction category is supported, then it is 16
    """
    if RISCV_CAT.C & getRiscVCategories(description):
        return 16
    else:
        return 32


def getRiscVILEN(description):
    """
    Utility function to return the ILEN value for a RISC-V processor based on
    a description string.

    All RISC-V processors currently have a max ILEN of 32 bits.  Processors that
    support the "C" (compressed) instruction category also support 16-bit
    instructions but ILEN is the maximum valid instruction size.
    """
    return 32


def getRiscVXLEN(description):
    """
    Utility function to return the XLEN value for a RISC-V processor based on
    a description string.

    XLEN indicates the bit size of the general purpose registers, which is
    indicated by the "XX" number in a RVXXYYYY description string.
    """
    info = _getRiscVArchInfo(description)
    if info is not None:
        return info[0]
    else:
        return None


def getRiscVFLEN(description):
    """
    Utility function to return the FLEN value for a RISC-V processor based on
    a description string.
    """
    categories = getRiscVCategories(description)
    if RISCV_CAT.Q & categories:
        return 128
    elif RISCV_CAT.D & categories:
        return 64
    elif RISCV_CAT.F & categories:
        return 32
    else:
        return None
