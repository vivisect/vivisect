import traceback

import vivisect.lib.bits as v_bits

class v_base:
    '''
    Base class for all VStruct types
    '''
    def __init__(self):
        self._vs_onset = []
        self._vs_isprim = True

    def __len__(self):
        return self.vsSize()

    #def __bytes__(self):
        #return self.vsEmit()

    def vsOnset(self, callback, *args, **kwargs):
        '''
        Trigger a callback when the fields value is updated.

        NOTE: this callback is triggered during parse() as well
              as during value updates.
        '''
        self._vs_onset.append( (callback,args,kwargs) )
        return self

    def _fire_onset(self):
        for cb,args,kwargs in self._vs_onset:
            try:
                cb(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()

class v_prim(v_base):
    '''
    Base class for all vstruct primitive types
    '''
    def __init__(self, size=None, valu=None):
        v_base.__init__(self)
        self._vs_size = size
        self._vs_bits = size * 8
        self._vs_value = self._prim_norm(valu)
        self._vs_parent = None

        # on-demand field parsing
        self._vs_backoff = None
        self._vs_backbytes = None
        self._vs_writeback = False

    def vsParse(self, bytez, offset=0, writeback=False):
        '''
        Byte parsing method for VStruct primitives.
        '''
        self._vs_value = None
        self._vs_backoff = offset
        self._vs_backbytes = bytez
        self._vs_writeback = writeback
        retval = offset + self._vs_size
        self._fire_onset()
        return retval

    def vsSize(self):
        '''
        Return the size of the field.
        '''
        return self._vs_size

    def vsResize(self, size):
        '''
        Resizing callback which can dynamically change the size
        of a primitive.
        '''
        if isinstance(size,v_prim):
            size = size._prim_getval()
        self._vs_size = size

    def _prim_setval(self, newval):
        valu = self._prim_norm(newval)
        self._vs_value = valu

        # if requested, write changes back to bytearray
        if self._vs_writeback:
            buf = self._prim_emit(valu)
            self._vs_backbytes[ self._vs_backoff:self._vs_backoff + len(buf) ] = buf

        self._fire_onset()

    def _prim_getval(self):
        # trigger on-demand parsing if needed
        if self._vs_value == None and self._vs_backbytes != None:
            self._vs_value = self._prim_parse(self._vs_backbytes, self._vs_backoff)

        return self._vs_value

    def vsEmit(self):
        return self._prim_emit( self._prim_getval() )

    def _prim_norm(self, x):
        raise Exception('Implement Me')

    def _prim_emit(self, x):
        raise Exception('Implement Me')

    def _prim_parse(self, bytez, offset):
        raise Exception('Implement Me')

class v_int(v_prim):

    def __init__(self,valu=0,size=4,endian='little',signed=False):
        v_prim.__init__(self,valu=valu,size=size)
        self._vs_endian = endian
        self._vs_signed = signed

    def __int__(self):
        return self._prim_getval()

    def vsResize(self, size):
        self._vs_bits = size * 8
        return v_prim.vsResize(self,size)

    def _prim_emit(self,x):
        return x.to_bytes(self._vs_size,byteorder=self._vs_endian)

    def _prim_norm(self,x):
        return v_bits.bitmask(x,self._vs_bits)

    def _prim_parse(self, bytez, offset):
        return int.from_bytes(bytez[offset:offset+self._vs_size],byteorder=self._vs_endian,signed=self._vs_signed)
