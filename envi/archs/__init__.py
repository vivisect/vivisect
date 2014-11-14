"""
The new top level home for all the envi architecture modules.
"""
import os
import sys

def dismain(d):
    '''
    Easy utility for implementing stand-alone disassembler utils...
    '''

    if os.path.isfile( sys.argv[1] ):
        b = file(sys.argv[1], 'rb').read()
    else:
        b = sys.argv[1].decode('hex')

    offset = 0
    va = 0x41414141
    while offset < len(b):
        op = d.disasm(b, offset, va+offset)
        print '0x%.8x %s %s' % (va+offset, b[offset:offset+len(op)].encode('hex').ljust(16), repr(op))
        offset += len(op)
