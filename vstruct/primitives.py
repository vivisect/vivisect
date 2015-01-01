import struct

class v_enum:
    '''
    example:
        vs = p.v_enum()
        vs.FOO = 1
        val = vs.vsLookup('FOO')
    '''
    def __init__(self):
        object.__setattr__(self, '_vs_reverseMap', {})

    def __setattr__(self, name, value):
        '''
        if duplicate values, last one wins!
        '''
        self._vs_reverseMap[value] = name
        return object.__setattr__(self, name, value)

    def vsLookup(self, val, default=None):
        '''
        maps a value to its name. returns default if not found.
        '''
        return self._vs_reverseMap.get(val, default)

# TODO: this looks duplicate, fix
class v_bitmask:
    def __init__(self):
        object.__setattr__(self, '_vs_reverseMap', {})

    def __setattr__(self, name, value):
        self._vs_reverseMap[value] = name
        return object.__setattr__(self, name, value)

    def vsReverseMapping(self, val, default=None):
        '''
        returns a list of names where apply the AND of the mask and val is
        non-zero.
        '''
        return [ v for k,v in self._vs_reverseMap.items() if (val&k) != 0 ]

class v_base:
    def __init__(self):
        self._vs_meta = {}

    def vsGetTypeName(self):
        return self.__class__.__name__

    def vsSetMeta(self, name, value):
        self._vs_meta[name] = value

    def vsGetMeta(self, name, defval=None):
        return self._vs_meta.get(name, defval)

    def vsCalculate(self):
        pass

    def vsParse(self, bytez, offset=0):
        '''
        parses bytes.
        '''
        raise NotImplementedError()

    def vsIsPrim(self):
        raise NotImplementedError()

class v_prim(v_base):
    def __init__(self):
        v_base.__init__(self)

        self._vs_value = None
        self._vs_length = None

    def vsIsPrim(self):
        return True

    def vsParseFd(self, fd):
        '''
        parses a file-like object.
        '''
        bytez = fd.read(self._vs_length)
        if len(bytez) != self._vs_length:
            raise Exception('Not enough data in fd!')

        self.vsParse(bytez)

    def vsEmit(self):
        '''
        return the bytes that represent this field.
        '''
        raise NotImplementedError()

    def vsSetValue(self, value):
        '''
        set the type specific value for this field.
        '''
        self._vs_value = value

    def vsGetValue(self):
        '''
        get the type specific value for this field.
        (Used by the structure dereference method to return
        a python native for the field by name)
        '''
        return self._vs_value

    def vsSetLength(self, size):
        '''
        set the length of this primitive type.
        '''
        raise NotImplementedError()

    def __repr__(self):
        return repr(self.vsGetValue())

    def __str__(self):
        return str(self.vsGetValue())

    def __bytes__(self):
        return self.vsEmit()

    def __len__(self):
        return self._vs_length

num_fmts = {
    (True, 1):'>B',
    (True, 2):'>H',
    (True, 4):'>I',
    (True, 8):'>Q',
    (False, 1):'<B',
    (False, 2):'<H',
    (False, 4):'<I',
    (False, 8):'<Q',
}

class v_number(v_prim):
    _vs_length = 1

    def __init__(self, value=0, bigend=False):
        v_prim.__init__(self)

        self._vs_value = value
        self._vs_bigend = bigend
        self._vs_length = self.__class__._vs_length
        self._vs_fmt = num_fmts.get( (bigend, self._vs_length) )

        # TODO: could use envi.bits, but do we really want to dep on envi?
        self.maxval = (2**(8 * self._vs_length)) - 1

    def vsParse(self, bytez, offset=0):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        sizeoff = offset + self._vs_length

        if self._vs_fmt != None:
            b = bytez[offset:sizeoff]
            self._vs_value = struct.unpack(self._vs_fmt, b)[0]

        else:
            r = bytez[offset:offset + self._vs_length]

            if not self._vs_bigend:
                r = reversed(r)

            self._vs_value = 0
            for x in r:
                self._vs_value = (self._vs_value << 8) + x

        return sizeoff

    def vsEmit(self):
        if self._vs_fmt != None:
            return struct.pack(self._vs_fmt, self._vs_value)

        b = bytearray(self._vs_length)
        for idx in range(len(b)):
            b[idx] = (self._vs_value >> (idx*8)) & 0xff

        if self._vs_bigend:
            b.reverse()

        return bytes(b)

    def vsSetValue(self, value):
        self._vs_value = value & self.maxval

    # implement the number api
    # https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
    # https://docs.python.org/3/library/stdtypes.html#typesnumeric

    # binary arithmetic operations
    def __add__(self, other): return self + other
    def __sub__(self, other): return self - other
    def __mul__(self, other): return self * other
    def __truediv__(self, other): return self / other
    def __floordiv__(self, other): return self // other
    def __mod__(self, other): return self % other
    def __divmod__(self, other): return divmod(self, other)
    def __pow__(self, other, modulo=None): return pow(self, other, modulo)
    def __lshift__(self, other): return self << other
    def __rshift__(self, other): return self >> other
    def __and__(self, other): return self & other
    def __xor__(self, other): return self ^ other
    def __or__(self, other): return self | other

    # operations with swapped operands
    def __radd__(self, other): return self.__add__(other)
    def __rsub__(self, other): return self.__sub__(other)
    def __rmul__(self, other): return self.__mul__(other)
    def __rtruediv__(self, other): return self.__truediv__(other)
    def __rfloordiv__(self, other): return self.__floordiv__(other)
    def __rmod__(self, other): return self.__mod__(other)
    def __rdivmod__(self, other): return self.__divmod__(other)
    def __rpow__(self, other, modulo=None): return self.__pow__(other, modulo)
    def __rlshift__(self, other): return self.__lshift__(other)
    def __rrshift__(self, other): return self.__rshift__(other)
    def __rand__(self, other): return self.__and__(other)
    def __rxor__(self, other): return self.__xor__(other)
    def __ror__(self, other): return self.__ror__(other)

    # operations for in-place (modifying self)
    def __iadd__(self, other): self.vsSetValue(self + other); return self
    def __isub__(self, other): self.vsSetValue(self - other); return self
    def __imul__(self, other): self.vsSetValue(self * other); return self
    def __itruediv__(self, other): self.vsSetValue(self / other); return self
    def __ifloordiv__(self, other): self.vsSetValue(self // other); return self
    def __imod__(self, other): self.vsSetValue(self % other); return self
    def __ipow__(self, other, modulo=None): self.vsSetValue(pow(self, other, modulo)); return self
    def __ilshift__(self, other): self.vsSetValue(self << other); return self
    def __irshift__(self, other): self.vsSetValue(self >> other); return self
    def __iand__(self, other): self.vsSetValue(self & other); return self
    def __ixor__(self, other): self.vsSetValue(self ^ other); return self
    def __ior__(self, other): self.vsSetValue(self | other); return self

    # unary arithmetic operations
    def __neg__(self): return -self
    def __pos__(self): return +self
    def __abs__(self): return abs(self)
    def __invert__(self): return ~self

    # only implement the int() built-in (not complex, float, or round)
    def __int__(self):
        return int(self._vs_value)

    # numeric type to integer for index
    def __index__(self): return int(self)

class v_snumber(v_number):
    _vs_length = 1

    def __init__(self, value=0, bigend=False):
        v_number.__init__(self, value=value, bigend=bigend)

        # TODO: could use envi.bits, but do we really want to dep on envi?
        smaxval = (2**((8 * self._vs_length)-1)) - 1
        self.smask = smaxval + 1

    def vsSetValue(self, value):
        value = value & self.maxval
        if value & self.smask:
            value = value - self.maxval - 1

        self._vs_value = value

class v_uint8(v_number):
    _vs_length = 1

class v_uint16(v_number):
    _vs_length = 2

class v_uint24(v_number):
    _vs_length = 3

class v_uint32(v_number):
    _vs_length = 4

class v_uint64(v_number):
    _vs_length = 8

class v_int8(v_snumber):
    _vs_length = 1

class v_int16(v_snumber):
    _vs_length = 2

class v_int24(v_snumber):
    _vs_length = 3

class v_int32(v_snumber):
    _vs_length = 4

class v_int64(v_snumber):
    _vs_length = 8

pointersize = struct.calcsize('P')

class v_size_t(v_number):
    _vs_length = pointersize

    def __repr__(self):
        return '0x%.8x' % self._vs_value

class v_ptr(v_size_t):
    pass

class v_ptr32(v_ptr):
    _vs_length = 4

class v_ptr64(v_ptr):
    _vs_length = 8

float_fmts = {
    (True, 4):'>f',
    (True, 8):'>d',
    (False, 4):'<f',
    (False, 8):'<d',
}

class v_float(v_prim):
    _vs_length = 4

    def __init__(self, value=0.0, bigend=False):
        v_prim.__init__(self)
        self._vs_bigend = bigend
        self._vs_value = value
        self._vs_length = self.__class__._vs_length
        self._vs_fmt = float_fmts.get( (bigend, self._vs_length) )

    def vsSetValue(self, value):
        '''
        Assure that the value is float() able for all numeric types.
        '''
        self._vs_value = float(value)

    def vsGetValue(self):
        return self._vs_value

    def vsParse(self, fbytes, offset=0):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        sizeoff = offset + self._vs_length

        if self._vs_fmt != None:
            b = fbytes[ offset : sizeoff ]
            self._vs_value = struct.unpack(self._vs_fmt, b)[0]

        else:
            r = []
            for i in range(self._vs_length):
                r.append( ord( fbytes[ offset + i ] ) )

            if not self._vs_bigend:
                r.reverse()

            self._vs_value = 0
            for x in r:
                self._vs_value = (self._vs_value << 8) + x

        return sizeoff

    def vsEmit(self):
        if self._vs_fmt != None:
            return struct.pack(self._vs_fmt, self._vs_value)

        r = []
        for i in range(self._vs_length):
            r.append( chr( (self._vs_value >> (i*8)) & 0xff) )

        if self._vs_bigend:
            r.reverse()

        return ''.join(r)

    def __add__(self, other): return double(self) + double(other)
    def __sub__(self, other): return double(self) - double(other)
    def __mul__(self, other): return double(self) * double(other)
    def __div__(self, other): return double(self) / double(other)
    def __floordiv__(self, other): return double(self) // double(other)
    def __mod__(self, other): return double(self) % double(other)
    def __divmod__(self, other): return divmod(double(self), double(other))
    def __pow__(self, other, modulo=None): return pow(double(self), double(other), modulo)
    def __lshift__(self, other): return double(self) << double(other)
    def __rshift__(self, other): return double(self) >> double(other)
    def __and__(self, other): return double(self) & double(other)
    def __xor__(self, other): return double(self) ^ double(other)
    def __or__(self, other): return double(self) | double(other)

    # Operator swapped variants
    def __radd__(self, other): return double(other) + double(self)
    def __rsub__(self, other): return double(other) - double(self)
    def __rmul__(self, other): return double(other) * double(self)
    def __rdiv__(self, other): return double(other) / double(self)
    def __rfloordiv__(self, other): return double(other) // double(self)
    def __rmod__(self, other): return double(other) % double(self)
    def __rdivmod__(self, other): return divmod(double(other), double(self))
    def __rpow__(self, other, modulo=None): return pow(double(other), double(self), modulo)
    def __rlshift__(self, other): return double(other) << double(self)
    def __rrshift__(self, other): return double(other) >> double(self)
    def __rand__(self, other): return double(other) & double(self)
    def __rxor__(self, other): return double(other) ^ double(self)
    def __ror__(self, other): return double(other) | double(self)

    # Inplace variants
    def __iadd__(self, other): self.vsSetValue(self+other); return self
    def __isub__(self, other): self.vsSetValue(self - other); return self
    def __imul__(self, other): self.vsSetValue(self*other); return self
    def __idiv__(self, other): self.vsSetValue(self/other); return self
    def __ifloordiv__(self, other): self.vsSetValue(self // other); return self
    def __imod__(self, other): self.vsSetValue(self % other); return self
    def __ipow__(self, other, modulo=None): self.vsSetValue(pow(self, other, modulo)); return self
    def __ilshift__(self, other): self.vsSetValue(self << other); return self
    def __irshift__(self, other): self.vsSetValue(self >> other); return self
    def __iand__(self, other): self.vsSetValue(self & other); return self
    def __ixor__(self, other): self.vsSetValue(self ^ other); return self
    def __ior__(self, other): self.vsSetValue(self | other); return self

    # operator helpers
    def __neg__(self): return -(double(self))
    def __pos__(self): return +(double(self))
    def __abs__(self): return abs(double(self))
    def __invert__(self): return ~(double(self))

    def __int__(self):
        return int(self._vs_value)

    # index use helper
    def __index__(self): return double(self)

class v_double(v_float):
    _vs_length = 8

class v_smixin:
    def vsSetLength(self, size):
        if size < 0:
            raise Exception('lengths must be > 0')

        size = int(size)
        self._vs_length = int(size)
        self._vs_fmt = '{}s'.format(size)

        # chop or expand
        b = self._vs_value[:size]
        self._vs_value = b.ljust(size, self.fillbyte)

    def vsParse(self, bytez, offset=0):
        # TODO: put this in base and force caller to call?
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        offend = offset + self._vs_length
        self._vs_value = bytez[offset:offend]
        return offend

    def vsEmit(self):
        return self._vs_value

class v_bytes(v_smixin, v_prim):
    '''
    use v_bytes for fixed width byte fields.
    '''
    def __init__(self, size=0, bytez=None, fillbyte=b'\x00'):
        v_prim.__init__(self)
        v_smixin.__init__(self)

        if size != 0 and bytez != None:
            raise Exception('specify size or bytez, not both')

        if bytez == None:
            bytez = bytes(size)

        self.fillbyte = fillbyte
        self._vs_length = len(bytez)
        self._vs_align = 1
        self._vs_fmt = '{}s'.format(self._vs_length)

        self.vsSetValue(bytez)

    def vsSetValue(self, bytez):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        if len(bytez) != self._vs_length:
            raise Exception('v_bytes field set to wrong length!')

        self._vs_value = bytez

class v_str(v_smixin, v_prim):
    '''
    A string placeholder class that automagically returns up to a null
    terminator (and keeps it's size by null padding when assigned to)
    '''
    def __init__(self, size=4, val='', fillbyte='\x00'):
        v_prim.__init__(self)
        v_smixin.__init__(self)

        self.fillbyte = fillbyte
        self._vs_length = size
        self._vs_fmt = '{}s'.format(size)
        self._vs_value = val.ljust(size, self.fillbyte)
        self._vs_align = 1

    def vsSetValue(self, val):
        self._vs_value = val.ljust(self._vs_length, self.fillbyte)

    def vsGetValue(self):
        s = self._vs_value.split(self.fillbyte)[0]
        return s

class v_zstr(v_prim):
    '''
    A string placeholder class that automagically returns up to a null
    terminator dynamically.
    '''
    def __init__(self, val='', align=1):
        v_prim.__init__(self)

        self._vs_align = align
        self.vsParse(val + '\x00')

    def vsSetValue(self, val):
        # FIXME: just call vsParse?
        length = len(val)
        diff = self._vs_align - (length % self._vs_align)
        self._vs_value = val + '\x00'*(diff)
        self._vs_length = len(self._vs_value)
        self._vs_align_pad = diff

    def vsGetValue(self):
        return self._vs_value[:-self._vs_align_pad]

    def vsSetLength(self, size):
        raise Exception('Cannot vsSetLength on v_zstr! (its dynamic)')

    def vsParse(self, fbytes, offset=0):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        nulloff = fbytes.find('\x00', offset)
        if nulloff == -1:
            raise Exception('v_zstr found no NULL terminator!')

        # align things correctly
        diff = self._vs_align - ((nulloff-offset) % self._vs_align)
        self._vs_align_pad = diff
        nulloff += diff

        self._vs_value = fbytes[offset : nulloff]
        self._vs_length = len(self._vs_value)
        return nulloff

    def vsEmit(self):
        return self._vs_value

class v_wstr(v_str):
    '''
    Unicode variant of the above string class

    NOTE: the size paramater is in WCHARs!
    '''
    def __init__(self, size=4, encode='utf-16le', val=''):
        v_str.__init__(self)

        b = val.ljust(size, '\x00').encode(encode)
        self._vs_length = len(b)
        self._vs_value = b
        self._vs_encode = encode
        self._vs_align = 2

    def vsSetValue(self, val):
        rbytes = val.encode(self._vs_encode)
        self._vs_value = rbytes.ljust(len(self), '\x00')

    def vsGetValue(self):
        s = self._vs_value.decode(self._vs_encode)
        return s.split('\x00')[0]

class v_zwstr(v_str):
    '''
    Unicode variant of the above zstring class
    '''
    def __init__(self, encode='utf-16le', val='', align=2):
        v_str.__init__(self)

        self._vs_encode = encode
        self._vs_align = align
        self.vsParse(val+'\x00\x00')

    def vsSetValue(self, val):
        #rbytes = val.encode(self._vs_encode)
        #self._vs_value = rbytes.ljust(len(self), '\x00')

        # FIXME: just call vsParse?
        rbytes = val.encode(self._vs_encode)
        length = len(rbytes)
        diff = self._vs_align - (length % self._vs_align)
        self._vs_value = rbytes + '\x00'*(diff)
        self._vs_value = rbytes.ljust(len(self), '\x00')
        self._vs_length = len(self._vs_value)
        self._vs_align_pad = diff

    def vsGetValue(self):
        cstr = self._vs_value.decode(self._vs_encode)
        return cstr.split('\x00')[0]

    def vsSetLength(self, size):
        raise Exception('Cannot vsSetLength on v_zwstr! (its dynamic)')

    def vsParse(self, fbytes, offset=0):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        nulloff = offset
        while nulloff < len(fbytes):
            nulloff = fbytes.find('\x00\x00', nulloff)
            if nulloff == -1:
                raise Exception('v_wzstr found no NULL terminator!')
            #make sure that this is acutally the null word by checking if
            # the alignment is correct
            if ((nulloff-offset) % self._vs_align) == 0:
                #yes, found it
                break
            #advance nulloff by 1 & keep looking
            nulloff += 1

        # align things correctly
        diff = self._vs_align - ((nulloff-offset) % self._vs_align)
        self._vs_align_pad = diff
        nulloff += diff

        self._vs_value = fbytes[offset : nulloff]
        self._vs_length = len(self._vs_value)
        return nulloff

class GUID(v_prim):
    '''
    Construct a new GUID primitive.  You may specify a GUID string in the
    constructor to populate initial values.
    '''
    def __init__(self, guidstr=None):
        v_prim.__init__(self)
        self._vs_length = 16
        self._vs_value = '\x00' * 16
        self._vs_fmt = '16s'
        self._guid_fields = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if guidstr != None:
            self._parseGuidStr(guidstr)

    def vsSetValue(self, guidstr):
        self._parseGuidStr(guidstr)

    def vsGetValue(self):
        return repr(self)

    def vsParse(self, fbytes, offset=0):
        if not isinstance(bytez, bytes):
            raise Exception('pass object of type bytes')

        offend = offset + self._vs_length
        self._guid_fields = struct.unpack('<IHH8B', fbytes[offset:offend])
        return offend

    def vsEmit(self):
        return struck.pack('<IHH8B', *self._guid_fields)

    def _parseGuidStr(self, gstr):
        gstr = gstr.replace('{', '')
        gstr = gstr.replace('}', '')
        gstr = gstr.replace('-', '')
        bytez = gstr.decode('hex')
        # Totally cheating... ;)
        self._guid_fields = struct.unpack('>IHH8B', bytez)

    def __repr__(self):
        base = '{%.8x-%.4x-%.4x-%.2x%.2x-%.2x%.2x%.2x%.2x%.2x%.2x}'
        return base  % self._guid_fields
