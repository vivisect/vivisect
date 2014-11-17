"""
A file full of bit twidling helpers
"""

import struct

MAX_WORD = 16 # usually no more than 8, 16 is for SIMD register support

# Masks to use for unsigned anding to size
u_maxes = [ (2 ** (8*i)) - 1 for i in range(MAX_WORD+1) ]
u_maxes[0] = 0 # powers of 0 are 1, but we need 0
bu_maxes = [ (2 ** (i)) - 1 for i in range(8*MAX_WORD+1) ]

# Masks of just the sign bit for different sizes
sign_bits = [ (2 ** (8*i)) >> 1 for i in range(MAX_WORD+1) ]
sign_bits[0] = 0 # powers of 0 are 1, but we need 0
bsign_bits = [ (2 ** i)>>1 for i in range(8*MAX_WORD+1) ]

# Max *signed* masks (all but top bit )
s_maxes = [ u_maxes[i] ^ sign_bits[i] for i in range(len(u_maxes))]
s_maxes[0] = 0

# bit width masks 
b_masks = [ (2**i)-1 for i in range(MAX_WORD*8) ]
b_masks[0] = 0

def unsigned(value, size):
    """
    Make a value unsigned based on it's size.
    """
    return value & u_maxes[size]

def signed(value, size):
    """
    Make a value signed based on it's size.
    """
    x = unsigned(value, size)
    if x & sign_bits[size]:
        x = (x - u_maxes[size]) - 1
    return x

def is_signed(value, size):
    x = unsigned(value, size)
    return bool(x & sign_bits[size])

def sign_extend(value, cursize, newsize):
    """
    Take a value and extend it's size filling
    in the space with the value of the high 
    order bit.
    """
    x = unsigned(value, cursize)
    if cursize != newsize:
        # Test for signed w/o the call
        if x & sign_bits[cursize]:
            delta = newsize - cursize
            highbits = u_maxes[delta]
            x |= highbits << (8*cursize)
    return x

def bsign_extend(value, cursize, newsize):
    x = value
    if cursize != newsize:
        if x & bsign_bits[cursize]:
            delta = newsize - cursize
            highbits = bu_maxes[delta]
            x |= highbits << (cursize)
    return x
  
def is_parity(val):
    s = 0
    while val:
        s ^= val & 1
        val = val >> 1
    return (not s)

parity_table = []
for i in range(256):
    parity_table.append(is_parity(i))

def is_parity_byte(bval):
    """
    An "optimized" parity checker that looks up the index.
    """
    return parity_table[bval & 0xff]

def lsb(value):
    return value & 0x1

def msb(value, size):
    if value & sign_bits[size]:
        return 1
    return 0

def is_signed_overflow(value, size):
    smax = s_maxes[size]
    if value > smax:
        return True
    if value < -smax:
        return True
    return False

def is_unsigned_carry(value, size):
    umax = u_maxes[size]
    if value > umax:
        return True
    elif value < 0:
        return True
    return False

def is_aux_carry(src, dst):
    return (dst & 0xf) + (src & 0xf) > 15

def is_aux_carry_sub(src, dst):
    return src & 0xf > dst & 0xf

le_fmt_chars = (None,"B","<H",None,"<I",None,None,None,"<Q")
be_fmt_chars = (None,"B",">H",None,">I",None,None,None,">Q")
def parsebytes(bytes, offset, size, sign=False, bigend=False):
    """
    Mostly for pulling immediates out of strings...
    """
    if size > 8:
        return slowparsebytes(bytes, offset, size, sign=sign, bigend=bigend)
    if bigend:
        f = be_fmt_chars[size]
    else:
        f = le_fmt_chars[size]
    if f == None:
        return slowparsebytes(bytes, offset, size, sign=sign, bigend=bigend)
    d = bytes[offset:offset+size]
    x = struct.unpack(f, d)[0]
    if sign:
        x = signed(x, size)
    return x

def slowparsebytes(bytes, offset, size, sign=False, bigend=False):
    if bigend:
        begin = offset
        inc = 1
    else:
        begin = offset + (size-1)
        inc = -1

    ret = 0
    ioff = 0
    for x in range(size):
        ret = ret << 8
        ret |= ord(bytes[begin+ioff])
        ioff += inc
    if sign:
        ret = signed(ret, size)
    return ret

def buildbytes(value, size, bigend=False):
    value = unsigned(value, size)
    if bigend:
        f = be_fmt_chars[size]
    else:
        f = le_fmt_chars[size]
    if f == None:
        raise Exception("envi.bits.buildbytes needs slowbuildbytes")
    return struct.pack(f, value)

def byteswap(value, size):
    ret = 0
    for i in range(size):
        ret |= (value >> (8*i)) & 0xff
        ret = ret << 8
    return ret

hex_fmt = {
    0:'0x%.1x',
    1:"0x%.2x",
    2:"0x%.4x",
    4:"0x%.8x",
    8:"0x%.16x",
}

def intwidth(val):
    if val < 0:
        val = abs(val)
    ret = 0
    while val:
        ret += 1
        val = val >> 8
    return ret

def hex(value, size=None):
    if size == None:
        size = intwidth(value)

    fmt = hex_fmt.get(size)
    if fmt != None:
        return fmt % value

    x = []
    while value:
        x.append('%.2x' % (value & 0xff))
        value = value >> 8
    x.reverse()
    return '0x%.s' % ''.join(x)


    return hex_fmt.get(size) % value

def binrepr(intval, bitwidth=None):
    '''
    Return a string of one's and zero's for the given value.
    '''
    ret = []
    while intval:
        ret.append(str(intval & 0x1))
        intval >>= 1
    ret.reverse()
    binstr = ''.join(ret)
    if bitwidth != None:
        binstr = binstr.rjust(bitwidth, '0')
    return binstr

def binary(binstr):
    '''
    Decode a binary string of 1/0's into a python number
    '''
    return int(binstr,2)

def binbytes(binstr):
    '''
    Decode a binary string of 1/0's into a python binary
    string.
    '''
    if len(binstr) % 8 != 0:
        raise Exception('Byte padded binary strings only for now!')
    bytes = ''
    while binstr:
        bytes += chr( binary(binstr[:8]) )
        binstr = binstr[8:]
    return bytes

def parsebits(bytes, offset, bitoff, bitsize):
    '''
    Parse bitsize bits from the bit offset bitoff beginning
    at offset bytes.

    Example: 
    '''
    val = 0
    cnt = 0
    while cnt < bitsize:

        addbit = bitoff + cnt
        addoff = offset + (addbit / 8)

        modoff = addbit % 8

        o = ord(bytes[addoff])
        val = (val << 1) + ((o >> (7 - modoff)) & 1)

        cnt += 1

    return val

def masktest(s):
    '''
    Specify a bit mask with the following syntax:
    '110100xxx00xx' to return a tester callback which will
    determine if an integer value meets the mask.

    example:
        opcode = 0x4388e234
        if masktest('1011xxxx0000')(opcode):
            print 'MATCHED!'

    NOTE: For performance reasons, it is recommeneded that
    masktest be used to initialize a static list of tests
    that are re-used rather than reconstructed.
    '''
    maskin = binary( s.replace('0','1').replace('x','0') )
    matchval = binary( s.replace('x','0') )
    def domask(testval):
        return testval & maskin == matchval
    return domask

#if __name__ == '__main__':
    #print hex(parsebits('\x0f\x00', 0, 4, 8))
    #print hex(parsebits('\x0f\x0f', 0, 4, 12))
    #print hex(parsebits('\x0f\x0f\xf0', 1, 4, 4))

