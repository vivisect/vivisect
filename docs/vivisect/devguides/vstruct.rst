.. _vstruct:

Structure Parsing
#################

Parsing a series of contiguous bytes into a single structure is a common task in binary analysis. To facilitate easier parsing and present a unified API throughout the vivisect/vdb codebase, vivisect also contains the vstruct module, which is an API for automatically parsing out bytes into python objects.

Typical usage of a vstruct structure definition is instantiating an instance of a vstruct object, pointing it at a set of bytes, and voila, you should have a fully populated structure. So something like this works::

    >>> import vstruct.defs.pe as vs_pe
    >>> byts = b'.data\x00\x00\x00\x01\xc0\x00\x00\xcd\xab\x00\x00\xaa\xaa\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3<\x0f\x00\x00\x00\x00\x00'
    >>> header = vs_pe.IMAGE_SECTION_HEADER()
    >>> header.vsParse(byts)

Now, in the interest of full honesty, those bytes weren't actually handcrafted. In addition to structure parsing, vstruct classes can also just emit the bytes that comprise them. So in reality, I generated those bytes like so::
    
    >>> header = vs_pe.IMAGE_SECTION_HEADER()
    >>> header.vsSetField('VirtualSize', 0xC001)
    >>> header.vsSetField('VirtualAddress', 0xABCD)
    >>> header.vsSetField('SizeOfRawData', 0xAAAA)
    >>> header.vsSetField('PointerToRawData', 0xffff)
    >>> header.vsSetField('NumberOfLineNumbers', 15)
    >>> header.vsSetField('NumberOfRelocations', 867539)
    >>> print(header.vsEmit())
    b'.data\x00\x00\x00\x01\xc0\x00\x00\xcd\xab\x00\x00\xaa\xaa\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3<\x0f\x00\x00\x00\x00\x00'


Creating a VStruct
==================

All vstruct classes derive from the base VStruct class like so::

    import vstruct 
    class IMAGE_FILE_HEADER(vstruct.VStruct):
        vstruct.VStruct.__init__(self)

which mostly just sets up a lot of the backing macinery that a vstruct class needs. From there, you can add other
properties, all of which need to be derived from other vstructs or be vstruct primives such as `v_uint16`, such as::

    import vstruct 
    from vstruct.primitives import *
    class IMAGE_FILE_HEADER(vstruct.VStruct):
        def __init__(self):
            vstruct.VStruct.__init__(self)
            self.Machine              = v_uint16()
            self.NumberOfSections     = v_uint16()
            self.TimeDateStamp        = v_uint32()
            self.PointerToSymbolTable = v_uint32()
            self.NumberOfSymbols      = v_uint32()
            self.SizeOfOptionalHeader = v_uint16()
            self.Characteristics      = v_uint16()

More Flexible Data
==================

Sometimes protocols aren't always so straightforward. Sometimes strings aren't always zero terminated, sometimes one field implies the existence (or non-existence) of another depending on the value.

To help with this, vstruct provides an in-band callback mechanism for each of the properties on the vstruct-derived classes. As each field is populated into the vstruct instance, any callback matching the name of the field is run in the order that the callbacks were added.

There are two ways to add parsing callbacks. The first (and simplest) is a method on your custom vstruct class that matches the form "pcb_<fieldname>".

If you need more than one callback when a VStruct property is set, you'll need to resort to the `vsAddParseCallback` method on an `instance` of your vstruct class, which allows for an arbitrary number of callbacks to be defined for a property::

    import vstruct
    from vstruct.primitives import *
    class Header(vstruct.VStruct):
        def __init__(self):
            vstruct.VStruct.__init__(self)
            self.size = v_int32()
            self.byts = v_bytes()

        def pcb_size(self):
            vs.vsSetField('size', olds * 2)

    def sizemod(vs):
        size = vs.vsGetField('size')
        vs.vsGetField('byts').vsSetLength(size)

    inst = Header()
    inst.vsAddParseCallback('size', sizemod)
    with open('mybytes.bin', 'rb') as fd:
        inst.vsparse(fd.read())

The above example demonstrates a relatively common use case of the custom callbacks, first parsing some field representing the size of the following fields, and then retrieving the bytes of those subsequent fields.

As one final note, between the `pcb_<fieldname>` method and the `vsAddParseCallback` way of adding callbacks, the `pcb_<fieldname>` runs before any callbacks defined by `vsAddParseCallback`, and then the callbacks added by `vsAddParseCallback` are run in the order they were added.

More Flexible VStructs
======================

VStruct was designed to be flexible when parsing binary structures. Some binary formats (such as DWARF) would be extraordinarily difficult to produce all the possible class definitions. So instead, what we can is instantiate an empty base VStruct class, and then dynamically add in properties::

    import vstruct
    import vstruct.defs.pe
    import vstruct.primitives
    vs = vstruct.VStruct()
    vs.vsAddField('field_name', vstruct.primitives.v_uint8())
    vs.vsAddField('second_field', vstruct.primitives.v_uint32())
    vs.vsAddField('complex_field', vstruct.defs.pe.IMAGE_FILE_HEADER())
    # Nah, really didn't mean that first field
    vs.vsDelField('field_name')

    with open('mybytes.bin', 'rb') as fd:
        vs.vsParse(fd.read())

Though a lot of this is quite wordy. We can slim that down to something like this::

    import vstruct
    import vstruct.defs.pe
    import vstruct.primitives
    vs = vstruct.VStruct()
    vs.MyCoolField = vstruct.primitives.v_uint8()
    vs.ASecondField = vstruct.primitives.v_uint32()
    vs.ComplexField = vstruct.defs.pe.IMAGE_FILE_HEADER()
    with open('mybytes.bin', 'rb') as fd:
        vs.vsParse(fd.read())
