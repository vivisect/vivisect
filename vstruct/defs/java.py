import vstruct

from vstruct.primitives import *


#const tag descriptions from wikipedia
#Tag byte    Additional bytes    Description of constant
#1   2+x bytes utf-8 string
#3   4 bytes Integer: a signed 32-bit two's complement number in big-endian format
#4   4 bytes Float: a 32-bit single-precision IEEE 754 floating-point number
#5   8 bytes Long: a signed 64-bit two's complement number in big-endian format (takes two slots in the constant pool table)
#6   8 bytes Double: a 64-bit double-precision IEEE 754 floating-point number (takes two slots in the constant pool table)
#7   2 bytes Class reference: an index within the constant pool to a UTF-8 string containing the fully qualified class name (in internal format)
#8   2 bytes String reference: an index within the constant pool to a UTF-8 string
#9   4 bytes Field reference: two indexes within the constant pool, the first pointing to a Class reference, the second to a Name and Type descriptor.
#10  4 bytes Method reference: two indexes within the constant pool, the first pointing to a Class reference, the second to a Name and Type descriptor.
#11  4 bytes Interface method reference: two indexes within the constant pool, the first pointing to a Class reference, the second to a Name and Type descriptor.
#12  4 bytes Name and type descriptor: two indexes to UTF-8 strings within the constant pool, the first representing a name (identifier) and the second a specially encoded type descriptor.

class ConstPoolStr(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size       = v_uint16(bigend=True)
        self.strbytes   = v_wstr(encode='utf8')

    def pcb_size(self):
        self.vsGetField('strbytes').vsSetLength( self.size )

tag_classes = {
    1:  ConstPoolStr,
    3:  v_uint32,
    4:  v_uint32,
    5:  v_uint64,
    6:  v_uint64,
    7:  v_uint16,
    8:  v_uint16,
    9:  v_uint32,
    10: v_uint32,
    11: v_uint32,
    12: v_uint32,
}

# Constant Tag Types
CONSTANT_Utf8               = 1
CONSTANT_Integer            = 3
CONSTANT_Float              = 4
CONSTANT_Long               = 5
CONSTANT_Double             = 6
CONSTANT_Class              = 7
CONSTANT_String             = 8
CONSTANT_Fieldref           = 9
CONSTANT_Methodref          = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_NameAndType        = 12
CONSTANT_MethodHandle       = 15
CONSTANT_MethodType         = 16
CONSTANT_InvokeDynamic      = 18

# Access Flags Values
ACC_PUBLIC      = 0x0001  # Declared public; may be accessed from outside its package.
ACC_PRIVATE     = 0x0002  # Declared private; usable only within the defining class.
ACC_PROTECTED   = 0x0004  # Declared protected; may be accessed within subclasses.
ACC_STATIC      = 0x0008  # Declared static.
ACC_FINAL       = 0x0010  # Declared final; never directly assigned to after object construction.
ACC_VOLATILE    = 0x0040  # Declared volatile; cannot be cached.
ACC_TRANSIENT   = 0x0080  # Declared transient; not written or read by a persistent object manager.
ACC_SYNTHETIC   = 0x1000  # Declared synthetic; not present in the source code.
ACC_ENUM        = 0x4000  # Declared as an element of an enum.

class ConstPoolInfo(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.tag    = v_uint8()
        self.data   = vstruct.VStruct()

    def pcb_tag(self):
        cls = tag_classes.get(self.tag)
        if cls is None:
            raise Exception('Unknown ConstPoolInfo Tag: %s' % self.tag )
        self.data.tagval = cls()

class AttributeInfo(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.attribute_name_index   = v_uint16(bigend=True)
        self.attribute_length       = v_uint32(bigend=True)
        self.attribute              = v_bytes()

    def pcb_attribute_length(self):
        self.vsGetField('attribute').vsSetLength( self.attribute_length )

class FieldInfo(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.access_flags       = v_uint16(bigend=True)
        self.name_index         = v_uint16(bigend=True)
        self.descriptor_index   = v_uint16(bigend=True)
        self.attributes_count   = v_uint16(bigend=True)
        self.attributes         = vstruct.VArray()

    def pcb_attributes_count(self):
        self.attributes.vsAddElements( self.attributes_count, AttributeInfo )

class MethodInfo(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.access_flags       = v_uint16(bigend=True)
        self.name_index         = v_uint16(bigend=True)
        self.descriptor_index   = v_uint16(bigend=True)
        self.attributes_count   = v_uint16(bigend=True)
        self.attributes         = vstruct.VArray()

    def pcb_attributes_count(self):
        self.attributes.vsAddElements( self.attributes_count, AttributeInfo )

class JavaClass(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic          = v_uint32(bigend=True)
        self.minor_versino  = v_uint16(bigend=True)
        self.major_version  = v_uint16(bigend=True)

        self.const_pool_cnt = v_uint16(bigend=True)
        self.const_pool     = vstruct.VArray()

        self.access_flags   = v_uint16(bigend=True)
        self.this_class     = v_uint16(bigend=True)
        self.super_class    = v_uint16(bigend=True)

        self.interface_cnt  = v_uint16(bigend=True)
        self.interfaces     = vstruct.VArray()

        self.fields_cnt     = v_uint16(bigend=True)
        self.fields         = vstruct.VArray()

        self.methods_cnt    = v_uint16(bigend=True)
        self.methods        = vstruct.VArray()

        self.attributes_cnt = v_uint16(bigend=True)
        self.attributes     = vstruct.VArray()

    def pcb_const_pool_cnt(self):
        # Count is off by one according to the spec
        self.const_pool.vsAddElements( self.const_pool_cnt - 1, ConstPoolInfo )

    def pcb_interface_cnt(self):
        for i in range( self.interface_cnt ):
            self.interfaces.vsAddElement( v_uint16( bigend=True ) )

    def pcb_fields_cnt(self):
        self.fields.vsAddElements( self.fields_cnt, FieldInfo )

    def pcb_methods_cnt(self):
        self.methods.vsAddElements( self.methods_cnt, MethodInfo )

    def pcb_attributes_cnt(self):
        self.attributes.vsAddElements( self.attributes_cnt, AttributeInfo )

    def getClassName(self):
        return self.const_pool[ self.this_class ].data.tagval.strbytes

    def getSuperClassName(self):
        return self.const_pool[ self.super_class ].data.tagval.strbytes

    def getClassFields(self):
        '''
        Get the fields defined by this class as a tuple of
        ( fieldname, fieldtype, attribs ) where attribs is a dict.
        '''
        ret = []
        for fname,fieldinfo in self.fields:

            fieldname = self.const_pool[ fieldinfo.name_index - 1 ].data.tagval.strbytes
            descname = self.const_pool[ fieldinfo.descriptor_index - 1 ].data.tagval.strbytes

            attrs = {}
            for afield, attrinfo in fieldinfo.attributes:
                attrname = self.const_pool[ attrinfo.attribute_name_index - 1 ].data.tagval.strbytes
                attrs[ attrname ] = attrinfo.attribute

            ret.append( (fieldname, descname, attrs) )
        return ret

    def getClassMethods(self):
        ret = []
        for fname,methinfo in self.methods:
            methname = self.const_pool[ methinfo.name_index - 1 ].data.tagval.strbytes
            attrs = {}
            for afield, attrinfo in methinfo.attributes:
                attrname = self.const_pool[ attrinfo.attribute_name_index - 1 ].data.tagval.strbytes
                attrs[ attrname ] = attrinfo.attribute
            ret.append( (methname, attrs) )
        return ret

    def getClassAttributes(self):
        attrs = {}
        for afield, attrinfo in self.attributes:
            attrname = self.const_pool[ attrinfo.attribute_name_index - 1 ].data.tagval.strbytes
            attrs[ attrname ] = attrinfo.attribute
        return attrs
