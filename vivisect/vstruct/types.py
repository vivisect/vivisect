import io
import codecs

from . import bases as vs_bases

# NOTE: keep this namespace super clean so it's safe to
#       use this via "from vstruct.types import *"

'''
VStruct types module contains a standard set of working field types
for use in building VStruct definitions.
'''

class VStruct(vs_bases.v_base,object):
    '''
    Base class for all structure definitions.

    The VStruct class facilitates structure definition, parsing, and emiting
    by allowing users to define fields with specific types.  Once defined, VStruct
    based structure classes are capable of automagically parsing data structure
    hierarchies as well as emiting bytes.

    Example:

        class woot(VStruct):

            def __init__(self):
                self.x = int8()
                self.y = uint32()
                self.z = vbytes(6)

        w = woot()
        w.vsParse( bytebuffer )

        # we may now access the structure fields directly from our
        # object which will return proper pythonic types for the
        # field accesses:

        print('x: %d y: %d' % (w.x, w.y))

        # additionally, we may set pre-defined fields using python types
        w.y = 90

        # and re-serialize the newly modified structure back to bytes
        w.vsEmit()
    '''

    def __init__(self, align=0):
        vs_bases.v_base.__init__(self)
        self._vs_isprim = False

        self._vs_fields = {}
        self._vs_fieldorder = []

    def vsEmit(self):
        '''
        Return bytes for the current values in the structure definition.
        '''
        fd = io.BytesIO()
        for off,prim in self.vsPrims():
            fd.seek(off)
            fd.write( prim.vsEmit() )
        fd.seek(0)
        return fd.read()

    def vsParse(self, buf, offset=0, writeback=False):
        '''
        Parse the given python bytes into structure values.
        '''
        retoff = offset
        for off,prim in self.vsPrims():
            retoff = prim.vsParse(buf, offset=offset+off, writeback=writeback)
        self._fire_onset()
        return retoff

    def _vs_prims(self):
        # recursive primitive *yielder* ( allows resizing while yielding )
        for name in self._vs_fieldorder:
            field = self._vs_fields.get(name)
            # for non-primitives, "recurse"
            if not field._vs_isprim:
                for f in field._vs_prims():
                    yield f

                continue

            yield field

    def vsPrims(self):
        '''
        Yield (offset,field) tuples for each contained primitive

        NOTE: this is implemented as a yield generator to allow resizing
        '''
        offset = 0
        for prim in self._vs_prims():
            # FIXME do alignment here
            yield (offset,prim)
            offset += prim.vsSize()

    def vsSize(self):
        '''
        Returns the current size of the structure in bytes.
        '''
        prims = list( self.vsPrims() )
        if not prims:
            return 0
        off,field = prims[-1]
        return off + field.vsSize()

    def _prim_getval(self):
        return self

    def __getattr__(self, name):
        ret = self._vs_fields.get(name)
        if ret != None:
            return ret._prim_getval()
        return super(VStruct,self).__getattr__(name)

    def __setattr__(self, name, valu):
        if name.startswith('_vs_'):
            return super(VStruct,self).__setattr__(name,valu)

        if isinstance(valu,vs_bases.v_base):
            field = self._vs_fields.get(name)
            if field == None:
                self._vs_fieldorder.append(name)
            self._vs_fields[name] = valu
            return

        field = self._vs_fields.get(name)
        if field != None:
            field._prim_setval( valu )
            return

        return super(VStruct,self).__setattr__(name,valu)

    def __getitem__(self, name):
        return self._vs_fields.get(name)

    def __setitem__(self, name, valu):
        field = self._vs_fields.get(name)

        if isinstance(valu,vs_bases.v_base):
            self._vs_fields[name] = valu
            if field == None:
                self._vs_fieldorder.append( name )

            return

        if field == None:
            raise Exception('Undefined Field: %s' % name)

        field._prim_setval( valu )


class vbytes(vs_bases.v_prim):
    def __init__(self, size=0):
        vs_bases.v_prim.__init__(self, size=size, valu=b'')

    def _prim_emit(self, x):
        return x

    def _prim_norm(self, x):
        return bytes(x)

    def _prim_parse(self, bytez, offset):
        return bytes( bytez[offset:offset + self.vsSize() ] )

class cstr(vs_bases.v_prim):
    r'''
    Fixed byte width string type.

    Assignments will be NULL padded to match size.

    Example:

        class woot(VStruct):
            def __init__(self):
                self.x = cstr(8)

        w = woot()
        w.x = 'hi'

        w.vsEmit() # emit's 8 bytes

    '''
    def __init__(self, size=0, valu='', encoding='utf8'):
        self._vs_encoding = encoding
        vs_bases.v_prim.__init__(self,size=size,valu=valu)

    def _prim_emit(self, x):
        return x.encode( self._vs_encoding ).ljust( self.vsSize(), b'\x00' )

    def _prim_norm(self, x):
        buf = x.encode( self._vs_encoding )
        return buf[:self.vsSize()].decode( self._vs_encoding )

    def _prim_parse(self, bytez, offset):
        buf = bytez[offset:offset + self.vsSize()]
        return buf.decode( self._vs_encoding ).split('\x00')[0]

class zstr(vs_bases.v_prim):
    r'''
    A dynamically sized ( NULL terminated ) string type.

    Parsing bytes will dynamically resize the object to the first NULL.

    Example:
        class woot(VStruct):
            def __init__(self):
                self.x = zstr()
                self.y = uint16()

        w = woot()
        w.vsParse(b'this is some text\x00\x03\x00')

        print(w.y) # prints 3

        # assignment auto NULL pads
        w = woot()
        w.x = 'hi there'
        w.y = 0x4141

        w.vsEmit() # emits b'hi there\x00AA'
    '''
    def __init__(self, size=0, valu='', encoding='utf8'):
        self._vs_encoding = encoding
        vs_bases.v_prim.__init__(self, size=size, valu=valu)

    def vsSize(self):
        # make sure we've parsed
        self._prim_getval()
        return self._vs_size

    def _prim_norm(self, x):
        buf = (x + '\x00').encode( self._vs_encoding )
        self.vsResize( len(buf) )
        return x

    def _prim_emit(self, x):
        return (x + '\x00').encode( self._vs_encoding )

    def _prim_parse(self, bytez, offset):
        chars = []
        yinfo = {'size':0}
        # a semi-hack until python's bytes.iterbytes() exists...
        def yieldb():
            for i in range(len(bytez) - offset):
                yinfo['size'] += 1
                yield bytez[offset+i:offset+i+1]

        # not exactly a model of efficiency...
        for c in codecs.iterdecode(yieldb(), self._vs_encoding):
            if ord(c) == 0:
                break
            chars.append(c)

        self.vsResize( yinfo['size'] )
        return ''.join(chars)

class int8(vs_bases.v_int):
    '''
    Signed 8 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=1, endian=endian, signed=True)

class int16(vs_bases.v_int):
    '''
    Signed 16 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=2, endian=endian, signed=True)

class int32(vs_bases.v_int):
    '''
    Signed 32 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=4, endian=endian, signed=True)

class int64(vs_bases.v_int):
    '''
    Signed 64 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=8, endian=endian, signed=True)

class uint8(vs_bases.v_int):
    '''
    Unsigned 8 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=1, endian=endian)

class uint16(vs_bases.v_int):
    '''
    Unsigned 16 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=2, endian=endian)

class uint32(vs_bases.v_int):
    '''
    Unsigned 32 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=4, endian=endian)

class uint64(vs_bases.v_int):
    '''
    Unsigned 64 bit integer type
    '''
    def __init__(self, valu=0, endian='little'):
        vs_bases.v_int.__init__(self, valu=valu, size=8, endian=endian)

