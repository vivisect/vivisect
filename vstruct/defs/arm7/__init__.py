
import vstruct
from vstruct.primitives import *

# Mapped at 0xe000e000 in arm7
class SCS(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.MasterControl           = v_uint32()
        self.InterruptControllerType = v_uint32()
        self.AuxiliaryControl        = v_uint32()
        self.ReservedSpace           = v_bytes(3320)
        self.CPUIDBase               = v_uint32()
        self.InterruptControlState   = v_uint32()
        self.VectorTableOffset       = v_uint32()
        self.AppInterr_ResetControl  = v_uint32()
        self.SystemControl           = v_uint32()
        self.ConfigurationControl    = v_uint32()
