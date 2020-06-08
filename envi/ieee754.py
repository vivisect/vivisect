import math
import envi.exc as e_exc

# tuples of (Exponent bitlen, Exponent Bias)
ieee754_formats = {
    16:  (5, 0xF),
    32:  (8, 0x7F),
    64:  (11, 0x3FF),
    80:  (15, 0x3FFF),  # non-implicit j bit
    # At least on intel, don't go beyond 80 bits (even that's suspect)
    # because floating point errors
    # just compound so mother trucking hard that it errors out into oblivion
    # 128: (15, 0x3FFF),
}


def float_decode(valu, bsize):
    '''
    https://software.intel.com/sites/default/files/managed/ae/01/floating-point-reference-sheet.pdf
    '''
    exp_len, exp_bias = ieee754_formats[bsize]

    loc = bsize - 1
    sign = (valu & (1 << loc)) >> loc

    loc -= exp_len
    mask = (2**exp_len) - 1
    exponent = (valu & (mask << loc)) >> loc

    if bsize == 80:  # BECAUSE INTEL HAS TO BE OH SO SPECIAL
        jbit_len = 1
        integer = (valu & (1 << (loc-1))) >> (loc-1)
    else:
        jbit_len = 0
        integer = 1 if exponent != 0 else 0

    frac_len = bsize - jbit_len - exp_len - 1
    mask = (2**frac_len) - 1
    fraction = valu & mask
    m = integer + (fraction / (2.0**frac_len))

    if exponent == 0:
        # denormal
        if fraction != 0:
            return ((-1)**sign) * m * (2**(1-exp_bias))
        else:
            return 0
    elif 1 <= exponent < ((2**exp_len) - 1):
        # normal
        return ((-1)**sign) * m * (2**(exponent-exp_bias))
    else:
        # various forms of infinity or NaN
        # The kind of NaN does matter
        highbit = (fraction & (1 << (frac_len-1))) >> (frac_len-1)
        if fraction == 0:
            raise e_exc.InvalidOperand(valu)
        elif highbit == 1:
            raise e_exc.SignalNaN()
        else:
            raise e_exc.QuietNaN()


def float_encode(valu, bsize):
    exp_len, exp_bias = ieee754_formats[bsize]

    # sign bit
    encoded = 1 if valu < 0 else 0
    if valu < 0:
        valu *= -1
        encoded = 1
    else:
        encoded = 0

    # find the exponent
    exponent = 0
    if valu >= 2:
        while valu >= 2:
            valu /= 2
            exponent += 1
    elif valu < 1:
        while valu < 1:
            valu *= 2
            exponent -= 1

    mask = (2**exp_len) - 1
    exponent += exp_bias
    exponent &= mask
    encoded <<= exp_len

    encoded |= exponent

    if bsize == 80:
        jbit_len = 1
        jbit = 1 if exponent != 0 else 0
        encoded <<= 1
        encoded |= jbit
    else:
        # the jbit is hidden in normal reprs of iee754
        jbit_len = 0

    valu %= 1

    frac_len = bsize - jbit_len - exp_len - 1
    for i in range(frac_len):
        encoded <<= 1
        valu *= 2
        if valu > 1:
            valu %= 1
            encoded |= 1
    return encoded
