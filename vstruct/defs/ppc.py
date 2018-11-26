
import vstruct
from vstruct.primitives import *

class RCHW(vstruct.VStruct):
    '''
    Identifies the flags and pointer for bootstrap
    '''
    def __init__(self, bigend=True):
        vstruct.VStruct.__init__(self)
        self.flags                   = v_uint8(bigend=bigend)
        self.SIGNATURE               = v_uint8(bigend=bigend)
        self.padding                 = v_uint16(bigend=bigend)
        self.entry_point             = v_ptr32(bigend=bigend)

