import vstruct
from vstruct.primitives import *

#HEAD_TYPE_MARKER        = 0x72          #marker block
#HEAD_TYPE_ARCHIVE       = 0x73          #archive header
#HEAD_TYPE_FILE_HDR      = 0x74          #file header
#HEAD_TYPE_OLD_COMMENT   = 0x75          #old style comment header
#HEAD_TYPE_OLD_AUTH      = 0x76          #old style authenticity information
#HEAD_TYPE_OLD_SUBBLOCK  = 0x77          #old style subblock
#HEAD_TYPE_OLD_RECOVERY  = 0x78          #old style recovery record
#HEAD_TYPE_OLD_AUTH2     = 0x79          #old style authenticity information
#HEAD_TYPE_SUBBLOCK      = 0x7a          #subblock

# Header Types
MARK_HEAD       = 0x72
MAIN_HEAD       = 0x73
FILE_HEAD       = 0x74
COMM_HEAD       = 0x75
AV_HEAD         = 0x76
SUB_HEAD        = 0x77
PROTECT_HEAD    = 0x78
SIGN_HEAD       = 0x79
NEWSUB_HEAD     = 0x7a
ENDARC_HEAD     = 0x7b

# Main Header Flags
MHD_VOLUME          = 0x0001
MHD_COMMENT         = 0x0002
MHD_LOCK            = 0x0004
MHD_SOLID           = 0x0008
MHD_PACK_COMMENT    = 0x0010
MHD_AV              = 0x0020
MHD_PROTECT         = 0x0040
MHD_PASSWORD        = 0x0080    # The archive is password encrypted
MHD_FIRSTVOLUME     = 0x0100
MHD_ENCRYPTVER      = 0x0200

LHD_SPLIT_BEFORE   = 0x0001
LHD_SPLIT_AFTER    = 0x0002
LHD_PASSWORD       = 0x0004
LHD_COMMENT        = 0x0008
LHD_SOLID          = 0x0010
LHD_WINDOWMASK     = 0x00e0
LHD_WINDOW64       = 0x0000
LHD_WINDOW128      = 0x0020
LHD_WINDOW256      = 0x0040
LHD_WINDOW512      = 0x0060
LHD_WINDOW1024     = 0x0080
LHD_WINDOW2048     = 0x00a0
LHD_WINDOW4096     = 0x00c0
LHD_DIRECTORY      = 0x00e0
LHD_LARGE          = 0x0100
LHD_UNICODE        = 0x0200
LHD_SALT           = 0x0400
LHD_VERSION        = 0x0800
LHD_EXTTIME        = 0x1000
LHD_EXTFLAGS       = 0x2000

SKIP_IF_UNKNOWN    = 0x4000
LONG_BLOCK         = 0x8000

class RarChunkUnkn(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.CHUNK_BYTES = v_bytes()

class MainHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.HighPosAV  = v_uint16()
        self.PosAV      = v_uint32()
        self.EncryptVer = v_uint8()

class RarBlock(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.HEAD_CRC       = v_uint16()
        self.HEAD_TYPE      = v_uint8()
        self.HEAD_FLAGS     = v_uint16()
        self.HEAD_SIZE      = v_uint16()
        self.ADD_SIZE       = v_uint32()
        self.BLOCK_DATA     = vstruct.VStruct()
        self._known_block   = False

    def pcb_HEAD_TYPE(self):
        self._known_block = False

        if self.HEAD_TYPE == MAIN_HEAD:
            self._known_block = True
            self.BLOCK_DATA = MainHeader()

            if not self.HEAD_FLAGS & MHD_ENCRYPTVER:
                self.BLOCK_DATA.EncryptVer = vstruct.VStruct()

    def pcb_HEAD_FLAGS(self):
        # a proto callback for the header
        if self.HEAD_FLAGS & LONG_BLOCK:
            self.ADD_SIZE = v_uint32()
        else:
            self.ADD_SIZE = vstruct.VStruct()

        if self.HEAD_TYPE == MAIN_HEAD and self.HEAD_FLAGS & MHD_PASSWORD:
                self.BLOCK_DATA.Salt = v_bytes(size=8)

    def pcb_ADD_SIZE(self):
        hsize = 7
        totsize = self.HEAD_SIZE

        if not isinstance(self.ADD_SIZE, vstruct.VStruct):
            hsize += 4
            totsize += self.ADD_SIZE

        # We will *now* use TYPE to find out our chunk guts
        if not self._known_block:
            self.BLOCK_DATA = v_bytes(totsize - hsize)
        

if __name__ == '__main__':
    import sys

    offset = 0
    b = file(sys.argv[1], 'rb').read()

    while offset < len(b):
        r = RarBlock()
        newoff = r.vsParse(b, offset=offset)
        print r.tree(va=offset)

        offset = newoff
        
