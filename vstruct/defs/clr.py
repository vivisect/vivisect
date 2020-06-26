import vstruct
from vstruct.primitives import *

class Module(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.Generation = v_uint16()
        self.Name = v_uint32()
        self.Mvid = v_uint32()
        self.EncId = v_uint32()
        self.EncBaseId = v_uint32()


class TypeRef(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.ResolutionScope = None  # What the fuck is this supposed to be?
        self.Name = v_uint32()
        self.Namespace = v_uint32()

class TypeDef(vstruct.VStruct):
    def __init__(self):
        pass
