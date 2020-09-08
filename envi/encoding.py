"""
Helpers for several encodings.
"""

def int_to_bcd(val):
    if val < 0:
        raise ValueError("negative value")

    mult = 1
    res = 0
    while val > 0:
        res += mult * (val % 10)
        mult *= 16
        val /= 10
        val = int(val)

    return res

def bcd_to_int(val, strict=False):
    if val < 0:
        raise ValueError("negative value")

    mult = 1
    res = 0
    while val > 0:
        nibble = val & 0xf
        if strict and nibble > 9:
            raise ValueError("invalid bcd value")

        res += nibble * mult
        mult *= 10
        val >>= 4

    return res
