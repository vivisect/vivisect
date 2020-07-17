
import vstruct
from vstruct.primitives import *

GIF_F_HAS_CMAP  = 0x80
GIF_F_BPP_MASK  = 0x07

GIF_IMG_SEP     = ','

class GIF_FILE_HEADER(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic      = v_bytes(size=6)
        self.width      = v_uint16()
        self.height     = v_uint16()
        self.flags      = v_uint8()
        self.bgcolor    = v_uint8()
        self.zero       = v_uint8()

class RGB(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.red    = v_uint8()
        self.green  = v_uint8()
        self.blue   = v_uint8()

class GIF_IMAGE_DESCRIPTOR(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.sep        = v_uint8()
        self.img_left   = v_uint16()
        self.img_top    = v_uint16()
        self.img_width  = v_uint16()
        self.img_height = v_uint16()
        self.flags      = v_uing8()

class GIF8XA(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)

    def isValidGif(self):
        if self.header.magic not in ('GIF87a', 'GIF89a'):
            return False
        if self.header.zero != 0:
            return False

    def vsParse(self, bytes, offset):


        # FIXME this is not functional yet...

        self.vsClearFields()
        self.header = GIF_FILE_HEADER()
        offset = self.header.vsParse(bytes, offset)

        # Do we have a global color table?
        if self.header.flags & GIF_F_HAS_CMAP:
            bits_per_pixel = (self.header.flags & GIF_F_BPP_MASK) + 1
            self.gct = vstruct.VStruct()
            for i in range(2**bits_per_pixel):
                self.gct.vsAddField('color%d' % i, RGB())

            offset = self.gct.vsParse(bytes, offset)

        self.images = vstruct.VStruct()

        imgidx = 0
        while bytes[offset] == GIF_IMG_SEP:
            img = vstruct.VStruct()

            img.descriptor = GIF_IMAGE_DESCRIPTOR()
            offset = img.descriptor.vsParse(bytes, offset)

            if img.descriptor.flags & GIF_F_HAS_CMAP:
                bits_per_pixel = (img.descriptor.flags & GIF_F_BPP_MASK) + 1
                img.cmap = vstruct.VStruct()

                for i in range(2**bits_per_pixel):
                    img.cmap.vsAddField('color%d' % i, RGB())

                offset = img.cmap.vsParse(bytes, offset)

