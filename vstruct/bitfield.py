import envi.bits as ebits
from vstruct import VStruct
from vstruct.primitives import *

class v_bits(v_number):

    def __init__(self, width):
        v_number.__init__(self)
        self._vs_bitwidth = width

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
            #print 'BYTE BIT OFF',byteoff,bitoff,(
            #offset += bittobyte

            endbyte,endbit = divmod(bitoff + field._vs_bitwidth,8)
            # if we have an endbit remainder, we need to grab
            # an additional byte...
            endround = 0
            endshift = 0
            if endbit:
                endshift = (8-endbit)
                endround = 1

            fieldbytes = bytez[offset + startbyte:offset+endbyte+endround]
            rawint = int( fieldbytes.encode('hex'), 16)
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
        out = [ 0 for x in range(len(self)) ]
        offset = 0
        bitoff = 0
        curbyte = 0

        for fname,field in self.vsGetFields():

            # use vsSetBitWidth(0) to disable fields
            if field._vs_bitwidth == 0:
                continue

            # adjust forward from last fields bits % 8
            startbyte,startbit = divmod(bitoff,8)
            endbyte,endbit = divmod(bitoff + field._vs_bitwidth,8)
            
            # if we have an endbit remainder, we need to grab
            # an additional byte...
            endround = 0
            endshift = 0
            if endbit:
                endshift = (8-endbit)
                endround = 1

            nibbitoff = 0
            if endbyte != startbyte:
                bitlen = 8 - startbit
                # split the operation
                for b in range(startbyte, endbyte):
                    nibbly = (field._vs_value >> (field._vs_bitwidth - nibbitoff - bitlen)) & 0xff
                    out[b] |= nibbly

                    nibbitoff += bitlen
                    bitlen = 8
                bitlen = endbit
            else:
                bitlen = endbit - startbit

            if endbit:
                mask = (1<<(bitlen)) - 1
                nibbly = (field._vs_value & mask) << (endshift)
                out[endbyte] |= nibbly

            bitoff += field._vs_bitwidth

        offbytes,offbits = divmod(bitoff,8)
        offset += offbytes

        # mop up any remaining bits int a byte boundary
        if offbits:
            offset += 1

        return ''.join([chr(x) for x in out])

