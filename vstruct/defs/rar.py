import os
import sys
import binascii

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

SFX_MODMAX  = 1024000 # one meg
RAR4_SIGNATURE = binascii.unhexlify('526172211a0700')
RAR5_SIGNATURE = binascii.unhexlify('526172211a070100')

def getRarOffset(fd):
    cur = fd.tell()
    head = fd.read(SFX_MODMAX * 2)
    fd.seek(cur)

    offset = head.find(RAR5_SIGNATURE)
    if offset != -1:
        return ( (5,0,0), offset + 8 )

    offset = head.find(RAR4_SIGNATURE)
    if offset != -1:
        return ( (4,0,0), offset + 7 )

    return None

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

SIZE_SALT30        = 8
SIZE_SALT50        = 16
SIZE_IV            = 16

CRYPT_NONE         = 0
CRYPT_RAR13        = 1
CRYPT_RAR15        = 2
CRYPT_RAR20        = 3
CRYPT_RAR30        = 4
CRYPT_RAR50        = 5

CRYPT_BLOCKSIZE    = 16

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

#class Rar4BaseBlock

class Rar4Block(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)

        self.HEAD_CRC       = v_uint16()
        self.HEAD_TYPE      = v_uint8()
        self.HEAD_FLAGS     = v_uint16()
        self.HEAD_SIZE      = v_uint16()
        self.HEAD_DATA      = vstruct.VStruct()

class MAIN_HEADER(Rar4Block):
    def __init__(self):
        Rar4Block.__init__(self)
        self.HEAD_DATA.HighPosAv    = v_uint16()
        self.HEAD_DATA.PosAV        = v_uint32()
        if self.HEAD_FLAGS & MHD_ENCRYPTVER:
            self.HEAD_DATA.EncryptVer   = v_uint8()

class FILE_HEADER(Rar4Block):
    def __init__(self):
        Rar4Block.__init__(self)
        self.HEAD_DATA.PackSize     = v_uint32()
        self.HEAD_DATA.UnpSize      = v_uint32()
        self.HEAD_DATA.HostOs       = v_uint8()
        self.HEAD_DATA.FileCrc      = v_uint32()
        self.HEAD_DATA.FileTime     = v_uint32()
        self.HEAD_DATA.UnpVer       = v_uint8()
        self.HEAD_DATA.Method       = v_uint8()
        self.HEAD_DATA.NameSize     = v_uint16()
        self.HEAD_DATA.FileAttr     = v_uint32()

        if self.HEAD_FLAGS & LHD_LARGE:
            self.HEAD_DATA.HighPackSize = v_uint32()
            self.HEAD_DATA.HighUnpSize  = v_uint32()

        filename = v_str()
        self.HEAD_DATA.FileName     = filename

        if self.HEAD_FLAGS & LHD_SALT:
            self.HEAD_DATA.Salt     = v_bytes(size=8)

        if self.HEAD_FLAGS & LHD_EXTTIME:
            raise Exception("FIXME supprort LHD_EXTTIME")

        def setFileNameSize(x):
            filename.vsSetLength( self.HEAD_DATA.NameSize )

        self.HEAD_DATA.vsAddParseCallback('NameSize',setFileNameSize)

        #self.HEAD_PAD       = vstruct.VStruct()

        #self.ADD_SIZE       = v_uint32()
        #self.BLOCK_DATA     = vstruct.VStruct()
        #self._known_block   = False

    #def pcb_HEAD_DATA(self):
        #remain = len(self) % 16
        #if remain:
            #self.HEAD_PAD.pad = v_bytes(size=16-remain)

    #def pcb_HEAD_SIZE(self):

        #if self.HEAD_TYPE == MAIN_HEAD:
            #self.HEAD_DATA.HighPosAv    = v_uint16()
            #self.HEAD_DATA.PosAV        = v_uint32()
            #if self.HEAD_FLAGS & MHD_ENCRYPTVER:
                #self.HEAD_DATA.EncryptVer   = v_uint8()
            #return

        #if self.HEAD_TYPE == FILE_HEAD:
            #self.HEAD_DATA.PackSize     = v_uint32()
            #self.HEAD_DATA.UnpSize      = v_uint32()
            #self.HEAD_DATA.HostOs       = v_uint8()
            #self.HEAD_DATA.FileCrc      = v_uint32()
            #self.HEAD_DATA.FileTime     = v_uint32()
            #self.HEAD_DATA.UnpVer       = v_uint8()
            #self.HEAD_DATA.Method       = v_uint8()
            #self.HEAD_DATA.NameSize     = v_uint16()
            #self.HEAD_DATA.FileAttr     = v_uint32()

            #if self.HEAD_FLAGS & LHD_LARGE:
                #self.HEAD_DATA.HighPackSize = v_uint32()
                #self.HEAD_DATA.HighUnpSize  = v_uint32()

            #filename = v_str()
            #self.HEAD_DATA.FileName     = filename

            #if self.HEAD_FLAGS & LHD_SALT:
                #self.HEAD_DATA.Salt     = v_bytes(size=8)

            #if self.HEAD_FLAGS & LHD_EXTTIME:
                #raise Exception("FIXME supprort LHD_EXTTIME")

            #def setFileNameSize(x):
                #filename.vsSetLength( self.HEAD_DATA.NameSize )

            #self.HEAD_DATA.vsAddParseCallback('NameSize',setFileNameSize)
            #return

            #self.HEAD_DATA.NameSize     = v_uint32()
            #self.HEAD_DATA.NameSize     = v_uint32()

            #if not self.HEAD_FLAGS & MHD_ENCRYPTVER:
                #self.BLOCK_DATA.EncryptVer = vstruct.VStruct()

    #def pcb_HEAD_FLAGS(self):
        ## a proto callback for the header
        #if self.HEAD_FLAGS & LONG_BLOCK:
            #self.ADD_SIZE = v_uint32()
        #else:
            #self.ADD_SIZE = vstruct.VStruct()

        #if self.HEAD_TYPE == MAIN_HEAD and self.HEAD_FLAGS & MHD_PASSWORD:
                #self.BLOCK_DATA.Salt = v_bytes(size=8)

    #def pcb_ADD_SIZE(self):

        # first things first, needs salt?
        #if self.HEAD_FLAGS & MHD_PASSWORD:
            #self.BLOCK_DATA.Salt = v_bytes(size=8)

        #hsize = 7
        #totsize = self.HEAD_SIZE
#
        #if not isinstance(self.ADD_SIZE, vstruct.VStruct):
            #hsize += 4
            #totsize += self.ADD_SIZE

        # We will *now* use TYPE to find out our chunk guts
        #if not self._known_block:
            #self.BLOCK_DATA = v_bytes(totsize - hsize)

import hashlib
rounds = 0x40000
roundsdiv = rounds / 16
#iblist = [ struct.pack('<I',i)[:3] for i in range(rounds) ]

def initIvKey30(passwd,salt):
    aesiv = [None] * 16
    aeskey = [None] * 16

    passb = passwd.encode('utf-16le')
    initkey = passb + salt

    sha1hash = hashlib.sha1()
    #sha1hash = rarsha()
    # crazy russian awesomeness/paranoia
    for i in range(rounds): # srsly?!?! fscking russians ;)
        sha1hash.update(initkey)
        ib = struct.pack('<I',i)
        sha1hash.update( ib[:3] )
        #sha1hash.update( iblist[i] )

        if i % roundsdiv == 0:
            digest = sha1hash.digest()
            #digest = sha1hash.done()
            aesiv[ i / roundsdiv ] = digest[-1]

    endswap = struct.unpack_from('<4I', sha1hash.digest())
    aeskey  = struct.pack('>4I', *endswap)
    #digest = sha1hash.digest()
    #for i in range(4):
        #for j in range(4):
            #aeskey[ (i*4) + j ] = chr( (digest[i] >> (j*8)) & 0xff )

    return ''.join(aesiv), aeskey

def aesInit(iv,key):
    from Crypto.Cipher import AES
    return AES.new(key, AES.MODE_CBC, iv)

class NoRarFd(Exception):pass
class MissingRarSig(Exception):pass
class PasswordRequired(Exception):pass

rar4blocks = {
    FILE_HEAD:FILE_HEADER,
}
class Rar:
    def __init__(self, fd=None):

        self.fd = None
        self.aes = None
        self.salt = None
        self.offset = None
        self.trybuf = None
        self.clearbuf = ''
        self.version = None
        self.mainhead = None


        if fd is not None:
            self.parseRarHeader(fd)

    def parseRarHeader(self, fd):

        veroff = getRarOffset(fd)
        if veroff is None:
            raise MissingRarSig()

        self.fd = fd
        self.version = veroff[0]
        self.offset = veroff[1]

        self.fd.seek(self.offset)
        self.mainhead = MAIN_HEADER()
        self.mainhead.vsParseFd( self.fd )

        if self.mainhead.HEAD_FLAGS & MHD_PASSWORD:
            self.salt = self.fd.read( SIZE_SALT30 )

    def _req_fd(self):
        if self.fd is None:
            raise NoRarFd()

    def tryFilePasswd(self, passwd):
        '''
        Check the passwd agains the next encrypted header
        ( which should be of type FILE_HEAD )
        '''
        if self.trybuf is None:
            curloc = self.fd.tell()
            self.trybuf = self.fd.read(16)
            self.fd.seek(curloc)

        iv,key = initIvKey30(passwd,self.salt)
        aes = aesInit(iv,key)
        clearbuf = aes.decrypt(self.trybuf)
        crc,ctype,cflags,csize = struct.unpack_from('<HBHH', clearbuf)
        return ctype == FILE_HEAD

    def setFilePasswd(self, passwd):
        '''
        Used to set the file-wide password for decryption.
        '''
        iv,key = initIvKey30(passwd,self.salt)
        self.aes = aesInit(iv,key)

    def read(self, size):
        if self.aes is None:
            return self.fd.read(size)

        while len(self.clearbuf) < size:
            crypted = self.fd.read(4096)
            self.clearbuf += self.aes.decrypt(crypted)

        ret = self.clearbuf[:size]
        self.clearbuf = self.clearbuf[size:]
        return ret

    #def read(self, size):
        #buf = self.fd.read(size)
        #if self.aes is not None:
            #buf = self.aes.decrypt(buf)
        #return buf

    def iterRar4Files(self):

        if self.salt is not None and self.aes is None:
            raise PasswordRequired()

        while True:
            hdr = self.read(7)
            crc,ctype,cflags,csize = struct.unpack('<HBHH', hdr)
            body = self.read(csize - 7)

            rar4 = Rar4Block()
            rar4.vsParse( hdr )

            #if self.salt is not None:
                #remain = csize % 16
                #if remain:
                    #pad = self.read( 16 - remain )
                    #logger.info('PAD %s', binascii.hexlify(pad))

            cls = rar4blocks.get(rar4.HEAD_TYPE)
            if cls is not None:
                rar4 = cls()
                rar4.vsParse(hdr+body)

            logger.info(rar4.tree())
            sys.stdin.readline()

            #if ctype == MAIN_HEAD and cflags & MHD_PASSWORD:
                #if passwd is None:
                    #raise PasswordRequired()

                #salt30 = fd.read(SIZE_SALT30)
                #iv,key = initIvKey(passwd,salt)
                #self.aes = aesInit(iv,key)
                #break

            if ctype == ENDARC_HEAD:
                break

        #self.HEAD_CRC       = v_uint16()
        #self.HEAD_TYPE      = v_uint8()
        #self.HEAD_FLAGS     = v_uint16()
        #self.HEAD_SIZE      = v_uint16()

def main():
    # TODO: Does this even work anymore?

    offset = 0
    with open(sys.argv[1], 'rb') as fd:
        testpass = sys.argv[2]

        rar = Rar()
        rar.parseRarHeader(fd)
        rar.mainhead.tree()

        #logger.info("FAIL TEST",rar.tryFilePasswd('asdf'))
        #logger.info("PASS TEST",rar.tryFilePasswd(testpass))

        rar.setFilePasswd(testpass)
        rar.iterRar4Files()
        #for x in rar.iterRar4Chunks():
            #print x
        return

        buf = fd.read(1024000)

        offset = 0

        rar4 = Rar4Block()
        offset = rar4.vsParse(buf,offset=offset)
        print(rar4.tree())

        salt = buf[offset:offset+SIZE_SALT30]
        print('SALT %s' % binascii.hexlify(salt))
        offset += SIZE_SALT30

        iv,key = initIvKey30(testpass,salt)
        #print('IV %s' % binascii.hexlify(iv))
        #print('KEY %s' % binascii.hexlify(key))
        aes = aesInit(iv,key)
        #print(binascii.hexlify(aes.decrypt(buf[offset:offset+64])))
        x = aes.decrypt(buf[offset:offset+64])

        rar4 = Rar4Block()
        rar4.vsParse(x)
        #offset = rar4.vsParse(buf,offset=offset)
        print(rar4.tree())

        #while offset < len(b):
            #r = RarBlock()
            #newoff = r.vsParse(b, offset=offset)
            #print 'CRC',r.HEAD_CRC,r.HEAD_TYPE
            #print r.tree(va=offset)

            #offset = newoff

if __name__ == '__main__':
    sys.exit(main())

