import struct
import binascii


class v_enum(object):
    def __init__(self):
        object.__setattr__(self, '_vs_reverseMap', {})

    def __setattr__(self, name, value):
        '''if duplicate values, last one wins!'''
        self._vs_reverseMap[value] = name
        return object.__setattr__(self, name, value)

    def vsReverseMapping(self, val, default=None):
        '''Maps an integer to its name. Returns default if not found'''
        return self._vs_reverseMap.get(val, default)


class v_bitmask(object):
    def __init__(self):
        object.__setattr__(self, "_vs_reverseMap", {})

    def __setattr__(self, name, value):
        self._vs_reverseMap[value] = name
        return object.__setattr__(self, name, value)

    def vsReverseMapping(self, val, default=None):
        '''Returns a list of names where apply the AND of the mask and val is non-zero'''
        return [v for k, v in self._vs_reverseMap.items() if (val & k) != 0]


class v_base(object):
    def __init__(self):
        self._vs_meta = {}

    def vsGetMeta(self, name, defval=None):
        return self._vs_meta.get(name, defval)

    def vsSetMeta(self, name, value):
        self._vs_meta[name] = value

    # Sub-classes (primitive base, or VStruct must have these
    def vsParse(self, bytes):
        return NotImplemented

    def vsCalculate(self):
        pass

    def vsIsPrim(self):
        return NotImplemented

    def vsGetTypeName(self):
        return NotImplemented


class v_prim(v_base):
    def __init__(self):
        v_base.__init__(self)
        # Used by base len(),vsGetFormat, etc...
        self._vs_value = None
        self._vs_length = None
        self._vs_fmt = None
        self._vs_align = None

    def vsIsPrim(self):
        return True

    def vsGetTypeName(self):
        return self.__class__.__name__

    def vsParse(self, bytes, offset=0):
        '''
        Parser for primitives which assumes we are calling parse directly.
        '''
        return NotImplemented

    def vsParseFd(self, fd):
        # Most primitives should be able to simply use this...
        fbytes = fd.read(self._vs_length)
        if len(fbytes) != self._vs_length:
            raise Exception('Not enough data in fd!')

        self.vsParse(fbytes)

    def vsEmit(self):
        '''
        Return the actual bytes which represent this field
        '''
        return NotImplemented

    def vsGetValue(self):
        '''
        Get the type specific value for this field.
        (Used by the structure dereference method to return
        a python native for the field by name)
        '''
        return self._vs_value

    def vsSetValue(self, value):
        '''
        Set the type specific value for this field.
        '''
        self._vs_value = value

    def vsSetLength(self, size):
        '''
        Set the length of this primitive type.  This may be used to
        dynamically update the length of string fields, etc...
        '''
        return NotImplemented

    def __repr__(self):
        return repr(self.vsGetValue())

    def __len__(self):
        return self._vs_length

    def __str__(self):
        return str(self.vsGetValue())

    def __hash__(self):
        return hash(self.vsGetValue())


num_fmts = {
    # big endian unsigned
    (True, 1): '>B',
    (True, 2): '>H',
    (True, 4): '>I',
    (True, 8): '>Q',

    # little endian unsigned
    (False, 1): '<B',
    (False, 2): '<H',
    (False, 4): '<I',
    (False, 8): '<Q',
}

signed_fmts = {
    # big endian signed
    (True, 1): '>b',
    (True, 2): '>h',
    (True, 4): '>i',
    (True, 8): '>q',

    # little endian signed
    (False, 1): '<b',
    (False, 2): '<h',
    (False, 4): '<i',
    (False, 8): '<q',
}


class v_number(v_prim):
    _vs_length = 1

    def __init__(self, value=0, bigend=False, enum=None):
        v_prim.__init__(self)
        self._vs_bigend = bigend
        self._vs_enum = enum
        self._vs_length = self.__class__._vs_length
        self._vs_fmt = num_fmts.get((bigend, self._vs_length))

        # TODO: could use envi.bits, but do we really want to dep on envi?
        self.maxval = (2 ** (8 * self._vs_length)) - 1
        self.vsSetValue(value)

    def vsGetValue(self):
        return self._vs_value

    def vsGetEnum(self):
        '''
        Get the v_enum instance used to interpret this number, or None if
          there are no associated enums.
        '''
        return self._vs_enum

    def vsParse(self, fbytes, offset=0):
        '''
        Parse the given numeric type from the given bytes
        '''
        sizeoff = offset + self._vs_length

        if self._vs_fmt is not None:
            b = fbytes[offset:sizeoff]
            self._vs_value = struct.unpack(self._vs_fmt, b)[0]

        else:
            r = []
            for i in range(self._vs_length):
                r.append(fbytes[offset + i])

            if not self._vs_bigend:
                r.reverse()

            self._vs_value = 0
            for x in r:
                self._vs_value = (self._vs_value << 8) + x

        return sizeoff

    def vsEmit(self):
        '''
        Emit the bytes for this numeric type
        '''
        if self._vs_fmt is not None:
            return struct.pack(self._vs_fmt, self._vs_value)

        r = []
        for i in range(self._vs_length):
            r.append((self._vs_value >> (i*8)) & 0xff)

        if self._vs_bigend:
            r.reverse()

        return bytes(r)

    def vsSetValue(self, value):
        self._vs_value = value & self.maxval

    def __int__(self):
        return int(self._vs_value)

    def __str__(self):
        v = self.vsGetValue()
        if self._vs_enum is not None:
            return str(self._vs_enum.vsReverseMapping(v, default=str(v)))
        return str(v)

    ##################################################################
    # Implement the number API
    def __add__(self, other):
        return int(self) + int(other)
    def __sub__(self, other):
        return int(self) - int(other)
    def __mul__(self, other):
        return int(self) * int(other)
    def __div__(self, other):
        return int(self) / int(other)
    def __floordiv__(self, other):
        return int(self) // int(other)

    def __mod__(self, other):
        return int(self) % int(other)
    def __divmod__(self, other):
        return divmod(int(self), int(other))
    def __pow__(self, other, modulo=None):
        return pow(int(self), int(other), modulo)
    def __lshift__(self, other):
        return int(self) << int(other)
    def __rshift__(self, other):
        return int(self) >> int(other)
    def __and__(self, other):
        return int(self) & int(other)
    def __xor__(self, other):
        return int(self) ^ int(other)
    def __or__(self, other):
        return int(self) | int(other)

    def __ge__(self, other):
        return int(self) >= int(other)
    def __le__(self, other):
        return int(self) <= int(other)
    def __gt__(self, other):
        return int(self) > int(other)
    def __lt__(self, other):
        return int(self) < int(other)
    def __eq__(self, other):
        return int(self) == int(other)

    # Operator swapped variants
    def __radd__(self, other): return int(other) + int(self)
    def __rsub__(self, other): return int(other) - int(self)
    def __rmul__(self, other): return int(other) * int(self)
    def __rdiv__(self, other): return int(other) / int(self)
    def __rfloordiv__(self, other): return int(other) // int(self)
    def __rmod__(self, other): return int(other) % int(self)
    def __rdivmod__(self, other): return divmod(int(other), int(self))
    def __rpow__(self, other, modulo=None): return pow(int(other), int(self), modulo)
    def __rlshift__(self, other): return int(other) << int(self)
    def __rrshift__(self, other): return int(other) >> int(self)
    def __rand__(self, other): return int(other) & int(self)
    def __rxor__(self, other): return int(other) ^ int(self)
    def __ror__(self, other): return int(other) | int(self)

    # Inplace variants
    def __iadd__(self, other):
        self.vsSetValue(self+other)
        return self
    def __isub__(self, other):
        self.vsSetValue(self - other)
        return self
    def __imul__(self, other):
        self.vsSetValue(self*other)
        return self
    def __idiv__(self, other):
        self.vsSetValue(self/other)
        return self
    def __ifloordiv__(self, other):
        self.vsSetValue(self // other)
        return self
    def __imod__(self, other):
        self.vsSetValue(self % other)
        return self
    def __ipow__(self, other, modulo=None):
        self.vsSetValue(pow(self, other, modulo))
        return self
    def __ilshift__(self, other):
        self.vsSetValue(self << other)
        return self
    def __irshift__(self, other):
        self.vsSetValue(self >> other)
        return self
    def __iand__(self, other):
        self.vsSetValue(self & other)
        return self
    def __ixor__(self, other):
        self.vsSetValue(self ^ other)
        return self
    def __ior__(self, other):
        self.vsSetValue(self | other)
        return self

    # operator helpers
    def __neg__(self):
        return -(int(self))
    def __pos__(self):
        return +(int(self))
    def __abs__(self):
        return abs(int(self))
    def __invert__(self):
        return ~(int(self))

    # index use helper
    def __index__(self):
        return int(self)

    # Print helpers
    def __hex__(self):
        return hex(int(self))
    def __oct__(self):
        return oct(int(self))


class v_snumber(v_number):
    _vs_length = 1

    def __init__(self, value=0, bigend=False, enum=None):
        smaxval = (2**((8 * self._vs_length)-1)) - 1
        self.smask = smaxval + 1

        v_number.__init__(self, value=value, bigend=bigend, enum=enum)
        self._vs_fmt = signed_fmts.get((bigend, self._vs_length))

    def vsSetValue(self, value):
        value = value & self.maxval
        if value & self.smask:
            value = value - self.maxval - 1

        self._vs_value = int(value)  # TODO

class v_uint8(v_number):
    _vs_builder = True
    _vs_length = 1

class v_uint16(v_number):
    _vs_builder = True
    _vs_length = 2

class v_uint24(v_number):
    _vs_builder = True
    _vs_length = 3

class v_uint32(v_number):
    _vs_builder = True
    _vs_length = 4

class v_uint64(v_number):
    _vs_builder = True
    _vs_length = 8

class v_int8(v_snumber):
    _vs_builder = True
    _vs_length = 1

class v_int16(v_snumber):
    _vs_builder = True
    _vs_length = 2

class v_int24(v_snumber):
    _vs_builder = True
    _vs_length = 3

class v_int32(v_snumber):
    _vs_builder = True
    _vs_length = 4

class v_int64(v_snumber):
    _vs_builder = True
    _vs_length = 8

pointersize = struct.calcsize('P')

class v_size_t(v_number):
    _vs_builder = True
    _vs_length = pointersize

    def __repr__(self):
        return "0x%.8x" % self._vs_value

class v_ptr(v_size_t):
    pass

class v_ptr32(v_ptr):
    _vs_builder = True
    _vs_length = 4

class v_ptr64(v_ptr):
    _vs_builder = True
    _vs_length = 8

float_fmts = {
    (True,4): '>f',
    (True,8): '>d',
    (False,4): '<f',
    (False,8): '<d',
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
        """
        Assure that the value is float() able for all numeric types.
        """
        self._vs_value = float(value)

    def vsGetValue(self):
        return self._vs_value

    def vsParse(self, fbytes, offset=0):
        '''
        Parse the given numeric type from the given bytes
        '''
        sizeoff = offset + self._vs_length

        if self._vs_fmt is not None:
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
        '''
        Emit the bytes for this numeric type
        '''
        if self._vs_fmt is not None:
            return struct.pack(self._vs_fmt, self._vs_value)

        r = []
        for i in range(self._vs_length):
            r.append( chr( (self._vs_value >> (i*8)) & 0xff) )

        if self._vs_bigend:
            r.reverse()

        return b''.join(r)

    def __int__(self):
        return int(self._vs_value)
    def __float__(self):
        return float(self._vs_value)

    def __add__(self, other): return float(self) + float(other)
    def __sub__(self, other): return float(self) - float(other)
    def __mul__(self, other): return float(self) * float(other)
    def __div__(self, other): return float(self) / float(other)
    def __floordiv__(self, other): return float(self) // float(other)
    def __mod__(self, other): return float(self) % float(other)
    def __divmod__(self, other): return divmod(float(self), float(other))
    def __pow__(self, other, modulo=None): return pow(float(self), float(other), modulo)
    def __lshift__(self, other): return float(self) << float(other)
    def __rshift__(self, other): return float(self) >> float(other)
    def __and__(self, other): return float(self) & float(other)
    def __xor__(self, other): return float(self) ^ float(other)
    def __or__(self, other): return float(self) | float(other)

    # Operator swapped variants
    def __radd__(self, other): return float(other) + float(self)
    def __rsub__(self, other): return float(other) - float(self)
    def __rmul__(self, other): return float(other) * float(self)
    def __rdiv__(self, other): return float(other) / float(self)
    def __rfloordiv__(self, other): return float(other) // float(self)
    def __rmod__(self, other): return float(other) % float(self)
    def __rdivmod__(self, other): return divmod(float(other), float(self))
    def __rpow__(self, other, modulo=None): return pow(float(other), float(self), modulo)
    def __rlshift__(self, other): return float(other) << float(self)
    def __rrshift__(self, other): return float(other) >> float(self)
    def __rand__(self, other): return float(other) & float(self)
    def __rxor__(self, other): return float(other) ^ float(self)
    def __ror__(self, other): return float(other) | float(self)

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
    def __neg__(self): return -(float(self))
    def __pos__(self): return +(float(self))
    def __abs__(self): return abs(float(self))
    def __invert__(self): return ~(float(self))

    # index use helper
    def __index__(self): return float(self)

    # Print helpers
    def __hex__(self): return hex(float(self))
    def __oct__(self): return oct(float(self))

class v_double(v_float):
    _vs_length = 8

class v_bytes(v_prim):

    '''
    v_bytes is used for fixed width byte fields.
    '''

    _vs_builder = True

    def __init__(self, size=0, vbytes=None):
        v_prim.__init__(self)
        if vbytes is None:
            vbytes = b'\x00' * size
        self._vs_length = len(vbytes)
        self._vs_value = vbytes
        self._vs_align = 1
        self._vs_fmt = '%ds' % self._vs_length

    def vsSetValue(self, val):
        if len(val) != self._vs_length:
            raise Exception('v_bytes field set to wrong length!')
        self._vs_value = val

    def vsParse(self, fbytes, offset=0):
        offend = offset + self._vs_length
        self._vs_value = fbytes[offset : offend]
        return offend

    def vsEmit(self):
        return self._vs_value

    def vsSetLength(self, size):
        size = int(size)
        self._vs_length = size
        self._vs_fmt = '%ds' % size
        # Either chop or expand my string...
        b = self._vs_value[:size]
        self._vs_value = b.ljust(size, b'\x00')

    def __repr__(self):
        return binascii.hexlify(self._vs_value).decode('utf-8')

class v_str(v_prim):
    '''
    A string placeholder class which will automagically return
    up to a null terminator (and will keep it's size by null
    padding when assigned to)
    '''

    _vs_builder = True

    def __init__(self, size=4, val=b''):
        v_prim.__init__(self)
        self._vs_length = size
        self._vs_fmt = '%ds' % size
        self._vs_value = val.ljust(size, b'\x00')
        self._vs_align = 1

    def vsParse(self, fbytes, offset=0):
        offend = offset + self._vs_length
        self._vs_value = fbytes[offset : offend]
        return offend

    def vsEmit(self):
        return self._vs_value

    def vsGetValue(self):
        s = self._vs_value.split(b'\x00')[0].decode('utf-8')
        return s

    def vsSetValue(self, val):
        if type(val) is str:
            val = val.encode('utf-8')
        self._vs_value = val.ljust(self._vs_length, b'\x00')

    def vsSetLength(self, size):
        size = int(size)
        self._vs_length = size
        self._vs_fmt = '%ds' % size
        # Either chop or expand my string...
        b = self._vs_value[:size]
        self._vs_value = b.ljust(size, b'\x00')

class v_zstr(v_prim):
    '''
    A string placeholder class which will automagically return
    up to a null terminator dynamically.
    '''

    _vs_builder = True

    def __init__(self, val=b'', align=1):
        v_prim.__init__(self)
        self._vs_align = align
        self.vsParse(val + b'\x00')

    def vsParse(self, fbytes, offset=0):
        nulloff = fbytes.find(b'\x00', offset)
        if nulloff == -1:
            raise Exception('v_zstr found no NULL terminator!')

        # align things correctly
        diff = self._vs_align - ((nulloff-offset) % self._vs_align)
        self._vs_align_pad = diff
        nulloff += diff

        self._vs_value = fbytes[offset : nulloff]
        self._vs_length = len(self._vs_value)
        return nulloff

    def vsParseFd(self, fd):
        ret = b''
        while not ret.endswith(b'\x00'):
            y = fd.read(1)
            if not y:
                raise Exception('v_zstr file ended before NULL')
            ret += y
        return self.vsParse(ret)

    def vsEmit(self):
        return self._vs_value

    def vsGetValue(self):
        return self._vs_value[:-self._vs_align_pad].decode('utf-8')

    def vsSetValue(self, val):
        # FIXME: just call vsParse?
        length = len(val)
        diff = self._vs_align - (length % self._vs_align)
        self._vs_value = val + b'\x00'*(diff)
        self._vs_length = len(self._vs_value)
        self._vs_align_pad = diff

    def vsSetLength(self, size):
        raise Exception('Cannot vsSetLength on v_zstr! (its dynamic)')

class v_wstr(v_str):
    '''
    Unicode variant of the above string class

    NOTE: the size paramater is in WCHARs!
    '''

    _vs_builder = True

    def __init__(self, size=4, encode='utf-16le', val=b''):
        v_str.__init__(self)
        b = val.ljust(size, b'\x00')
        self._vs_length = len(b)
        self._vs_value = b
        self._vs_encode = encode
        self._vs_align = 2

    def vsParse(self, fbytes, offset=0):
        offend = offset + self._vs_length
        self._vs_value = fbytes[offset : offend]
        return offend

    def vsEmit(self):
        return self._vs_value

    def vsSetValue(self, val):
        rbytes = val.encode(self._vs_encode)
        self._vs_value = rbytes.ljust(len(self), b'\x00')

    def vsGetValue(self):
        s = self._vs_value.decode(self._vs_encode, errors='replace')
        return s.split("\x00")[0]

class v_zwstr(v_str):
    '''
    Unicode variant of the above zstring class
    '''

    _vs_builder = True

    def __init__(self, encode='utf-16le', val=b'', align=2):
        v_str.__init__(self)
        self._vs_encode = encode
        self._vs_align = align
        self.vsParse(val + b'\x00\x00')

    def vsParse(self, fbytes, offset=0):
        nulloff = offset
        while nulloff < len(fbytes):
            nulloff = fbytes.find(b'\x00\x00', nulloff)
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

        #offend = offset + self._vs_length
        #self._vs_value = fbytes[offset : offend]
        #return offend

    def vsEmit(self):
        return self._vs_value

    def vsGetValue(self):
        cstr = self._vs_value.decode(self._vs_encode, errors='replace')
        return cstr.split('\x00')[0]

    def vsSetValue(self, val):
        #rbytes = val.encode(self._vs_encode)
        #self._vs_value = rbytes.ljust(len(self), '\x00')

        # FIXME: just call vsParse?
        rbytes = val.encode(self._vs_encode)
        length = len(rbytes)
        diff = self._vs_align - (length % self._vs_align)
        self._vs_value = rbytes + b'\x00' * (diff)
        self._vs_value = rbytes.ljust(len(self), b'\x00')
        self._vs_length = len(self._vs_value)
        self._vs_align_pad = diff

    def vsSetLength(self, size):
        raise Exception('Cannot vsSetLength on v_zwstr! (its dynamic)')

class GUID(v_prim):

    _vs_builder = True

    def __init__(self, guidstr=None):
        """
        Construct a new GUID primitive.  You may specify a GUID string in the
        constructor to populate initial values.
        """
        v_prim.__init__(self)
        self._vs_length = 16
        self._vs_value = '\x00' * 16
        self._vs_fmt = '16s'
        self._guid_fields = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if guidstr is not None:
            self._parseGuidStr(guidstr)

    def vsParse(self, fbytes, offset=0):
        offend = offset + self._vs_length
        self._guid_fields = struct.unpack("<IHH8B", fbytes[offset:offend])
        return offend

    def vsEmit(self):
        return struct.pack("<IHH8B", *self._guid_fields)

    def _parseGuidStr(self, gstr):
        gstr = gstr.replace('{', '')
        gstr = gstr.replace('}', '')
        gstr = gstr.replace('-', '')
        bytes = binascii.unhexlify(gstr)
        # Totally cheating... ;)
        self._guid_fields = struct.unpack('>IHH8B', bytes)

    def vsSetValue(self, guidstr):
        self._parseGuidStr(guidstr)

    def vsGetValue(self):
        return repr(self)

    def __repr__(self):
        base = "{%.8x-%.4x-%.4x-%.2x%.2x-%.2x%.2x%.2x%.2x%.2x%.2x}"
        return base  % self._guid_fields

