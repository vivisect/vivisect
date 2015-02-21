'''
A file full of bit twidling helpers
'''
import binascii

MAX_WORD = 16 # usually no more than 8, 16 is for SIMD register support

# doing this in 2 parts prevents negative shifting...
tempbits = [ 1 << i for i in range(8*MAX_WORD+1) ]
signbits = [ t >> 1 for t in tempbits ]

def initmask(bits):
    return (1<<bits)-1

# bit width masks 
bitmasks = [ initmask(i) for i in range(MAX_WORD*8) ]

def bitmask(value,bits):
    '''
    Mask an integer down to a given number of bits ( unsigned ).
    '''
    return value & bitmasks[bits]

def shrmask(x,shr,bits):
    return bitmask(x >> shr, bits)

def signext(value, bits, newbits):
    '''
    Sign extend value from bits to newbits in width.

    Example:
        x = 0xffff
        y = signext(x,16,32) # y is now 0xffffffff
    '''
    value = signed(value,bits)
    return value & bitmasks[newbits]

def unsigned(value,bits):
    '''
    Returns value masked to ensure an unsigned value of bits width.

    Example:
        x = -1
        y = unsigned(x,8) # y is now 0xff
    '''
    return value & bitmasks[bits]

def signed(value,bits):
    '''
    Returns a (possibly negative) python int by signed interpretation.

    Example:
        x = 0xffffff
        y = signed(x,24) # y is now -1
    '''
    # normalize to unsigned width first
    mask = bitmasks[bits]
    value = value & mask
    if value & signbits[bits]:
        value = ( value - mask ) - 1
    return value

# actual parity bit counting routine
def _parity(val):
    s = 0
    while val:
        s ^= val & 1
        val = val >> 1
    return (not s)

# pre-computed parity values for all bytes
parity_table = []
for i in range(256):
    parity_table.append(_parity(i))

def parity(val):
    '''
    Calculate the "parity" value for an integer.
    '''
    if val < 256:
        return parity_table[val]
    return _parity(val)

def h2b(h):
    '''
    Convert a hex *string* into binary *bytes*.

    Example:
        h2b('41414141') # returns b'AAAA'
    '''
    return binascii.unhexlify( h.encode('ascii') )

def b2h(b):
    '''
    Convert binary *bytes* into a hex *string*.

    Example:
        x = b'some binary data'
        print('hex bytes: %s' % (b2h(x),))
    '''
    return binascii.hexlify(b).decode('ascii')

def bits2int(binstr):
    '''
    Decode a binary string of 1/0's into a python number
    '''
    return int(binstr,2)

def int2bits(x,size):
    '''
    Convert a python integer to a bit string ( and pad to size )
    '''
    return bin(x)[2:].rjust(size,'0')

def hex2bits(s):
    '''
    Convert a hex string into a bits string.

    hex2bits('88') # returns '1000000010000000'
    '''
    return ''.join([ bin(x)[2:].rjust(8,'0') for x in h2b(s) ])

def bits2bytes(bitstr):
    '''
    Decode a binary string of 1/0's into python bytes
    bits2bytes('0100000101000001') # returns b'AA'
    '''
    i = int(bitstr,2)
    return i.to_bytes( len(bitstr) // 8, byteorder='big' )

def bytes2int(buf,byteorder='little'):
    return int.from_bytes(buf,byteorder=byteorder)

def bytes2bits(b):
    return ''.join([ bin(x)[2:].rjust(8,'0') for x in b ])

def bitfields(maskstr):
    '''
    Parse contiguous chars from a bitmask string as field defs.

    Example:
        bitfields('aaaabbcd') # returns ( ('a',4),('b',2),('c',1),('d',1) )
    '''
    off = 0
    fields = []
    masklen = len(maskstr)
    while off < masklen:
        x = 0
        c = maskstr[off]
        while off+x < len(maskstr) and maskstr[off+x] == c:
            x += 1
        fields.append( (c,x) )
        off += x
    return fields

def bitparser(maskstr):
    '''
    Generate a parser for extracting bit fields from bytes.
    '''
    bitlen = len(maskstr)
    byteslen = bitlen // 8

    bitoff = 0
    namedfields = []

    for c,x in bitfields(maskstr):
        if c not in ('1','0','.'):
            namedfields.append( ((bitlen-bitoff) - x, x, c)) 
        bitoff += x

    def parsemask(b,offset=0):
        fullint = int.from_bytes(b[offset:offset+byteslen],byteorder='big')
        return dict([ (n,shrmask(fullint,s,b)) for (s,b,n) in namedfields ])

    return parsemask

def iterbytes(intvals,size=1,byteorder='big'):
    '''
    Iterate a set of int values yielding bytes for each.
    '''
    for x in intvals:
        yield x.to_bytes(size,byteorder=byteorder)

