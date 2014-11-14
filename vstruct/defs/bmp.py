import vstruct
from vstruct.primitives import *

class BITMAPINFOHEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.biSize             = v_uint32()
        self.biWidth            = v_int32()
        self.biHeight           = v_int32()
        self.biPlanes           = v_uint16()
        self.biBitCount         = v_uint16()
        self.biCompression      = v_uint32()
        self.biSizeImage        = v_uint32()
        self.biXPelsPerMeter    = v_int32()
        self.biYPelsPerMeter    = v_int32()
        self.biClrUser          = v_uint32()
        self.biClrImportant     = v_uint32()



