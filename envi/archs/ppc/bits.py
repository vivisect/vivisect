import envi.bits as e_bits

# Static generation of which bit should be set according to the PPC
# documentation for 32 and 64 bit values
_ppc64_bitmasks = tuple(0x8000_0000_0000_0000 >> i for i in range(64))
_ppc32_bitmasks = tuple(0x8000_0000 >> i for i in range(32))
_ppc_bitmasks = (None, None, None, None, _ppc32_bitmasks, None, None, None, _ppc64_bitmasks,)

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


def COMPLEMENT(val, size):
    '''
    1's complement of the value
    '''
    return val ^ e_bits.u_maxes[size]
