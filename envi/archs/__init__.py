"""
The new top level home for all the envi architecture modules.
"""
import os
import sys
import binascii

import envi.common as e_common


def dismain(d):
    '''
    Easy utility for implementing stand-alone disassembler utils...
    '''

    # TODO: this belongs as a standalone utility, not in an __init__ file
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'rb') as f:
            b = f.read()
    else:
        b = binascii.unhexlify(sys.argv[1])

    offset = 0
    va = 0x41414141
    while offset < len(b):
        op = d.disasm(b, offset, va+offset)
        print('0x%.8x %s %s' % (va+offset, e_common.hexify(b[offset:offset+len(op)]).ljust(16), repr(op)))
        offset += len(op)
