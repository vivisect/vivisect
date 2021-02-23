import binascii

from vstruct import VStruct
from vstruct.primitives import *

class v_bits(v_number):

    def __init__(self, width):
        v_number.__init__(self)
        self._vs_bitwidth = int(width)

    def vsSetValue(self, value):
        '''
        override base because we are not using the min or max val.
        '''
        self._vs_value = value

    def vsSetBitWidth(self, width):
        self._vs_bitwidth = width

class VBitField(VStruct):
    '''
    A VStruct *like* field which may contain v_bits
    children.  To all VStruct related operations, we are
    a primitive, but we do have internal structure.

    Example:
        see vstruct/defs/swf.py

    NOTE: this object will pad itself to byte aligned bounds
    '''
    def __init__(self):
        VStruct.__init__(self)

    def vsIsPrim(self):
        return True

    def vsAddField(self, name, value):
        if not isinstance(value, v_bits):
            raise Exception('VBitField *must* use v_bits() kids!')
        return VStruct.vsAddField(self, name, value)

    def vsGetPrintInfo(self, offset=0, indent=0, top=True):
        ret = []
        if top:
            ret.append((offset, indent, self._vs_name, self))

        indent += 1
        bitoff = 0
        for fname,field in self.vsGetFields():
            # use vsSetBitWidth(0) to disable fields
            if field._vs_bitwidth == 0:
                continue
            bitname = '%s[%d:%d]' % (fname,bitoff,bitoff + field._vs_bitwidth)
            ret.append( (offset, indent, bitname, field) )
            bitoff += field._vs_bitwidth

        return ret

    def __len__(self):
        bits = sum([ f._vs_bitwidth for (n,f) in self.vsGetFields() ])
        bittobyte,bitoff = divmod(bits,8)
        if bitoff:
            bittobyte += 1
        return bittobyte

    def vsParse(self, bytez, offset=0):
        bitoff = 0

        for fname,field in self.vsGetFields():

            # use vsSetBitWidth(0) to disable fields
            if field._vs_bitwidth == 0:
                continue

            # adjust forward from last fields bits % 8
            startbyte,startbit = divmod(bitoff,8)
            #offset += bittobyte

            endbyte,endbit = divmod(bitoff + field._vs_bitwidth, 8)
            # if we have an endbit remainder, we need to grab
            # an additional byte...
            endround = 0
            endshift = 0
            if endbit:
                endshift = (8-endbit)
                endround = 1

            fieldbytes = bytez[offset + startbyte:offset+endbyte+endround]
            rawint = int(binascii.hexlify(fieldbytes), 16)
            if endshift:
            #if bitshift:
                rawint >>= endshift

            rawint &= (2**field._vs_bitwidth)-1
            field.vsSetValue(rawint)
            bitoff += field._vs_bitwidth

            self._vsFireCallbacks(fname)

        offbytes,offbits = divmod(bitoff,8)
        offset += offbytes
        # mop up any remaining bits int a byte boundary
        if offbits:
            offset += 1

        return offset

    def vsEmit(self):
        valu = 0
        width = 0

        for name,field in self.vsGetFields():
                width += field._vs_bitwidth
                valu = ( valu << field._vs_bitwidth ) | field._vs_value
        bytelen,bitrem = divmod(width,8)
        if bitrem:
            bytelen += 1
            valu <<= ( 8 - bitrem )

        return binascii.unhexlify(('%.' + str(bytelen*2) + 'x') % valu)
