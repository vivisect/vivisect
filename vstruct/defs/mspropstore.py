import logging

from enum import IntEnum

import vstruct

from vstruct.primitives import *

logger = logging.getLogger(__name__)

class UnicodeString(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.length = v_uint32()  # size represents the number of 16-bit unicode characters

    def pcb_length(self):
        if self.length > 0:
            numbytes = 2 * self.length
            self.valu = v_wstr(size=numbytes)
            numpad = ((numbytes + 3) & ~0x3) - numbytes
            self.padding = v_bytes(size=numpad)

class FileTime(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.dwLowDateTime = v_uint32()
        self.dwHighDateTime  = v_uint32()

class Blob(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()

    def pcb_size(self):
        self.data = v_bytes(size=self.size)

class CodePageString(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self, unicode=False)
        self.size = v_uint32()
        if unicode:
            self.characters = v_wstr(size=2*self.size)
        else:
            self.characters = v_str(size=self.size)

class VersionedStream(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.guid = GUID()
        self.name = CodePageString()

class ClipboardData(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.size = v_uint32()
        self.format = v_uint32()

    def pcb_format(self):
        numbytes = (self.size + 3) & ~0x3
        self.data = v_bytes(size=numbytes)

class Decimal(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.reserved = v_uint16()
        self.scale = v_uint8()
        self.sign = v_uint8()
        self.high32 = v_uint32()
        self.low64 = v_uint64()

class ArrayDimension(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.indexOff = v_uint32()

class ArrayHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.type = v_uint32()
        self.numDim = v_uint32()

        self.dimensions = vstruct.VArray()

    def pcb_numDim(self):
        for i in range(self.numDim):
            self.dimensions.vsAddElement(ArrayDimension())

class PropertyType(IntEnum):
    VT_EMPTY = 0x0000
    VT_NULL = 0x0001
    VT_I2 = 0x0002
    VT_I4 = 0x0003
    VT_R4 = 0x0004
    VT_R8 = 0x0005
    VT_CY = 0x0006
    VT_DATE = 0x0007
    VT_BSTR = 0x0008

    VT_ERROR = 0x000A
    VT_BOOL = 0x000B

    VT_DECIMAL = 0x000E
    VT_I1 = 0x0010
    VT_UI1 = 0x0011
    VT_UI2 = 0x0012
    VT_UI4 = 0x0013
    VT_I8 = 0x0014
    VT_UI8 = 0x0015
    VT_INT = 0x0016
    VT_UINT = 0x0017
    VT_LPSTR = 0x001E
    VT_LPWSTR = 0x001F

    VT_FILETIME = 0x0040
    VT_BLOB = 0x0041
    VT_STREAM = 0x0042
    VT_STORAGE = 0x0043
    VT_STREAMED_OBJECT = 0x0044
    VT_STORED_OBJECT = 0x0045
    VT_BLOB_OBJECT = 0x0046
    VT_CF = 0x0047
    VT_CLSID = 0x0048
    VT_VERSIONED_STREAM = 0x0049

    # These are special. They're modifiers to the above
    VT_VECTOR = 0x1000
    VT_ARRAY = 0x2000

    # VECTOR. See MS-OLEPS Section 2.15 for why there are gaps because this list
    # is *not* equivalent to just OR-ing the above items with VT_VECTOR
    VT_VECTOR_I2 = VT_VECTOR | VT_I2
    VT_VECTOR_I4 = VT_VECTOR | VT_I4
    VT_VECTOR_R4 = VT_VECTOR | VT_R4
    VT_VECTOR_R8 = VT_VECTOR | VT_R8
    VT_VECTOR_CY = VT_VECTOR | VT_CY
    VT_VECTOR_DATE = VT_VECTOR | VT_DATE
    VT_VECTOR_BSTR = VT_VECTOR | VT_BSTR
    VT_VECTOR_ERROR = VT_VECTOR | VT_ERROR
    VT_VECTOR_BOOL = VT_VECTOR | VT_BOOL

    VT_VECTOR_VARIANT = VT_VECTOR | 0x000C

    VT_VECTOR_I1 = VT_VECTOR | VT_I1
    VT_VECTOR_UI1 = VT_VECTOR | VT_UI1
    VT_VECTOR_UI2 = VT_VECTOR | VT_UI2
    VT_VECTOR_UI4 = VT_VECTOR | VT_UI4
    VT_VECTOR_I8 = VT_VECTOR | VT_I8
    VT_VECTOR_UI8 = VT_VECTOR | VT_UI8
    VT_VECTOR_LPSTR = VT_VECTOR | VT_LPSTR
    VT_VECTOR_LPWSTR = VT_VECTOR | VT_LPWSTR

    VT_VECTOR_FILETIME = VT_VECTOR | VT_FILETIME
    VT_VECTOR_CF = VT_VECTOR | VT_CF
    VT_VECTOR_CLSID = VT_VECTOR | VT_CLSID

    # Similar to VECTOR. There are gaps, so see Section 2.15
    VT_ARRAY_I2 = VT_ARRAY | VT_I2
    VT_ARRAY_I4 = VT_ARRAY | VT_I4
    VT_ARRAY_R4 = VT_ARRAY | VT_R4
    VT_ARRAY_R8 = VT_ARRAY | VT_R8
    VT_ARRAY_CY = VT_ARRAY | VT_CY
    VT_ARRAY_DATE = VT_ARRAY | VT_DATE
    VT_ARRAY_BSTR = VT_ARRAY | VT_BSTR
    VT_ARRAY_ERROR = VT_ARRAY | VT_ERROR
    VT_ARRAY_BOOL = VT_ARRAY | VT_BOOL

    VT_ARRAY_VARIANT = VT_ARRAY | 0x000C

    VT_ARRAY_DECIMAL = VT_ARRAY | VT_DECIMAL
    VT_ARRAY_I1 = VT_ARRAY | VT_I1
    VT_ARRAY_UI1 = VT_ARRAY | VT_UI1
    VT_ARRAY_UI2 = VT_ARRAY | VT_UI2
    VT_ARRAY_UI4 = VT_ARRAY | VT_UI4
    VT_ARRAY_INT = VT_ARRAY | VT_INT
    VT_ARRAY_UINT = VT_ARRAY | VT_UINT


class TypedPropertyValue(vstruct.VStruct):
    # See MS-OLEPS for the MS definintion of this (Specifically section 2.15)
    def __init__(self, unicode=False):
        vstruct.VStruct.__init__(self)

        self.typeid = v_uint16()
        self.padding = v_uint16()

        self.unicode = unicode

        # self.vectorheader = None
        # self.arrayheader = None
        # self.valu = None
        # self.pad = None

    def pcb_typeid(self):

        if self.typeid & PropertyType.VT_VECTOR:
            self.vectorheader = v_uint32()
        elif self.typeid & PropertyType.VT_ARRAY:
            logger.warning('ArrayHeaders are not yet fully supported')
            #self.arrayheader = ArrayHeader()
        else:
            valu, pad = self._getTypeValu(self.typeid)
            self.valu = valu
            if pad:
                self.pad = pad

    def pcb_vectorheader(self):
        self.valu = vstruct.VArray()
        for i in range(self.vectorheader):
            if self.typeid == PropertyType.VT_VECTOR_VARIANT:
                valu = TypedPropertyValue(unicode=self.unicode)
            else:
                valu, _ = self._getTypeValu(self.typeid)

            self.valu.vsAddElement(valu)

        # there's a couple vector ones we've gotta pad to get a total amount of space that's
        # a multiple of 4
        if self.typeid == PropertyType.VT_VECTOR_I2:
            size = 2
        elif self.typeid == PropertyType.VT_VECTOR_UI2:
            size = 2
        elif self.typeid == PropertyType.VT_VECTOR_BOOL:
            size = 2
        elif self.typeid == PropertyType.VT_VECTOR_I1:
            size = 1
        elif self.typeid == PropertyType.VT_VECTOR_UI1:
            size = 1
        else:
            return

        nxt = ((size * self.vectorheader) + 3) & ~0x3
        self.pad = v_bytes(size=nxt - (size * self.vectorheader))

    def _getTypeValu(self, typeid):
        valu = None
        pad = None
        match typeid:
            case PropertyType.VT_I2:
                valu = v_int16()
                pad = v_uint16()
            case PropertyType.VT_I4:
                valu = v_int32()
            case PropertyType.VT_R4:
                valu = v_float()
            case PropertyType.VT_R8:
                valu = v_double()
            case PropertyType.VT_CY:
                valu = v_uint64()
            case PropertyType.VT_DATE:
                valu = v_double()
            case PropertyType.VT_BSTR:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_ERROR:
                valu = v_uint32()
            case PropertyType.VT_BOOL:
                valu = v_uint16()
            case PropertyType.VT_DECIMAL:
                valu = Decimal()
            case PropertyType.VT_I1:
                valu = v_int8()
            case PropertyType.VT_UI1:
                valu = v_uint8()
            case PropertyType.VT_UI2:
                valu = v_uint16()
            case PropertyType.VT_UI4:
                valu = v_uint32()
            case PropertyType.VT_I8:
                valu = v_int64()
            case PropertyType.VT_UI8:
                valu = v_uint64()
            case PropertyType.VT_INT:
                valu = v_int32()
            case PropertyType.VT_UINT:
                valu = v_uint32()
            case PropertyType.VT_LPSTR:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_LPWSTR:
                valu = UnicodeString()
            case PropertyType.VT_FILETIME:
                valu = FileTime()
            case PropertyType.VT_BLOB:
                valu = Blob()
            case PropertyType.VT_STREAM:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_STORAGE:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_STREAMED_OBJECT:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_STORED_OBJECT:
                valu = CodePageString(unicode=self.unicode)
            case PropertyType.VT_BLOB_OBJECT:
                valu = Blob()
            case PropertyType.VT_CF:
                valu = ClipboardData()
            case PropertyType.VT_CLSID:
                valu = GUID()
            case PropertyType.VT_VERSIONED_STREAM:
                valu = VersionedStream()

        return valu, pad

class StringPropertyValue(vstruct.VStruct):
    # All strings specified by this structure are unicode
    # See MS-PROPSTORE
    def __init__(self, unicode=False):
        vstruct.VStruct.__init__(self)
        self.unicode = unicode
        self.size = v_uint32()
        self.namesize = v_uint32()

    def pcb_namesize(self):
        if self.size > 0:
            self.reserved = v_uint8()

            self.name = v_zwstr()

            self.valu = TypedPropertyValue(unicode=self.unicode)

class IntegerPropertyValue(vstruct.VStruct):
    def __init__(self, unicode=False):
        vstruct.VStruct.__init__(self)
        self.unicode = unicode
        self.size = v_uint32()
        self.id = v_uint32()

    def pcb_id(self):
        if self.size > 0:
            self.reserved = v_uint8()

            self.valu = TypedPropertyValue(unicode=self.unicode)

STRING_PROP_GUID = '{D5CDD505-2E9C-101B-9397-08002B2CF9AE}'
# This is what MS calls it, but we could use a better name
class PropertyStorage(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()

    def pcb_size(self):
        # A size of 0 indicates we're done
        if self.size != 0:
            self.version = v_uint32()
            self.formatid = GUID()
            self.propvalues = vstruct.VArray()

    def vsParse(self, bytes, offset=0):
        # parse the base stuff and check if we've got anything
        retoff = vstruct.VStruct.vsParse(self, bytes, offset=offset)
        if self.size == 0:
            return len(self) + offset

        ctor = StringPropertyValue if self.formatid == STRING_PROP_GUID else IntegerPropertyValue

        # parse until a propvalu comes back with a *value size* of 0
        step = len(self)
        unicode = False
        while True:
            elem = None
            if self.formatid == STRING_PROP_GUID:
                elem = StringPropertyValue()
                elem.vsParse(bytes[(offset+step):])
            else:
                elem = IntegerPropertyValue()
                elem.vsParse(bytes[(offset+step):])

                if elem.id == 0x1 and (elem.valu.valu == 1200 or elem.valu.valu == 1201):
                    unicode = True

            self.propvalues.vsAddElement(elem)
            step += elem.size
            if elem.size == 0:
                break

        return len(self) + offset
