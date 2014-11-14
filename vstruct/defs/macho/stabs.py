import vstruct

from vstruct.primitives import *
from vstruct.defs.macho.const import *

class nlist(vstruct.VStruct):
    '''
    A symbol table entry in a Mach-O binary is called an nlist.
    '''
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.n_strx     = v_uint32()    # index into the string table
        self.n_type     = v_uint8()     # type flag (see const...)
        self.n_sect     = v_uint8()     # section number or NO_SECT (index from 1...)
        self.n_desc     = v_uint16()    # desription (see const...)
        self.n_value    = v_uint32()    # value of this symbol (or stab offset)

class nlist64(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.n_strx     = v_uint32()
        self.n_type     = v_uint8()
        self.n_sect     = v_uint8()
        self.n_desc     = v_uint16()
        self.n_value    = v_uint64()

