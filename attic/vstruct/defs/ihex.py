
'''
Parser objects for the Intel Hex file format.
'''
import vstruct
from vstruct.primitives import *

IHEX_REC_DATA           = 0
IHEX_REC_EOF            = 1
IHEX_REC_EXSEG          = 2 # Extended Segment Address Records
IHEX_REC_STARTSEG       = 3 # The beginning code segment value
IHEX_REC_EXLINADDR      = 4 # Extended Linear Address Records
IHEX_REC_STARTLINADDR   = 5 # 32bit entry point

class IHexChunk(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.startcode      = v_bytes(1)
        self.bytecount      = v_bytes(2)
        self.address        = v_bytes(4)
        self.recordtype     = v_bytes(2)
        self.data           = v_bytes(0)
        self.csum           = v_bytes(2)

    def pcb_bytecount(self):
        dsize = int(self.bytecount, 16)
        self.vsGetField('data').vsSetLength( 2 * dsize )

    def getAddress(self):
        '''
        Parse the address field and return the int type.
        '''
        return int( self.address, 16 )

    def getData(self):
        '''
        Return the binary data payload for this chunk.
        '''
        return self.data.decode('hex')

class IHexFile(vstruct.VArray):

    def vsParse(self, bytes, offset=0):

        lines = bytes[offset:].splitlines()

        for line in lines:
            offset += 1 # there is an eaten newline for each
            if not line:
                continue

            c = IHexChunk()
            c.vsParse( line )
            offset += len( c )

            self.vsAddElement( c )

            if int(c.recordtype, 16) == IHEX_REC_EOF:
                break

        return offset

    def getEntryPoint(self):
        '''
        If a 32bit linear start address is defined for this file,
        return it.  Returns None if the 32bit entry point extension
        is not present.
        '''
        for fname, chunk in self:
            ctype = int( chunk.recordtype, 16 )
            if ctype == IHEX_REC_STARTLINADDR:
                return int( chunk.data, 16 )

    def getMemoryMaps(self):
        '''
        Retrieve a set of memory maps defined by this hex file.

        Memory maps are returned as a list of
        ( va, perms, fname, bytes ) tuples.
        '''
        import envi.memory as e_mem

        # Get all the binary parts....
        baseaddr = 0
        memparts = []

        for fname, chunk in self:

            ctype = int( chunk.recordtype, 16 )

            if ctype == IHEX_REC_DATA:
                addr = chunk.getAddress() + baseaddr
                memparts.append( (addr, chunk.getData()) )
                continue

            if ctype == IHEX_REC_EXSEG:
                baseaddr = int( chunk.data, 16 ) << 4
                continue

            if ctype == IHEX_REC_EXLINADDR:
                baseaddr = int( chunk.data, 16 ) << 16
                continue

            if ctype == IHEX_REC_EOF:
                break

            raise Exception('Unhandled IHEX chunk: %s' % chunk.recordtype)

        memparts.sort()

        maps = []
        for addr, bytes in memparts:
            # is this the next contiguous chunk?
            if maps and addr == ( maps[-1][0] + len(maps[-1][3]) ):
                maps[-1][3] += bytes
            else:
                maps.append( [ addr, e_mem.MM_RWX, '', bytes ] )

        return maps

if __name__ == '__main__':

    example = '''
:020000021000EC
:10C20000E0A5E6F6FDFFE0AEE00FE6FCFDFFE6FD93
:10C21000FFFFF6F50EFE4B66F2FA0CFEF2F40EFE90
:10C22000F04EF05FF06CF07DCA0050C2F086F097DF
:10C23000F04AF054BCF5204830592D02E018BB03F9
:020000020000FC
:04000000FA00000200
:00000001FF
'''
    example1 = '''
:10001300AC12AD13AE10AF1112002F8E0E8F0F2244
:10000300E50B250DF509E50A350CF5081200132259
:03000000020023D8
:0C002300787FE4F6D8FD7581130200031D
:10002F00EFF88DF0A4FFEDC5F0CEA42EFEEC88F016
:04003F00A42EFE22CB
:00000001FF
'''
    example2 = '''
:10010000214601360121470136007EFE09D2190140
:100110002146017EB7C20001FF5F16002148011988
:10012000194E79234623965778239EDA3F01B2CAA7
:100130003F0156702B5E712B722B732146013421C7
:00000001FF
asdf
    '''

    example3 = '''
:100000003C932014BBE0AD7A3EAC4D261FB267A4F2
:100010008121F4C2D641A503B6038C9932A36EBCEC
:10002000D204306AE84404FCE8C7452DE0BE3160E4
:100030005CC6E94D3F4E62765AC237EAD3C2895157
:0200000400F00A
:10000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00
:020000040030CA
:1000000000270F0F0083F500FFC0FFE0FF400000C5
:020000040020DA
:080000000102030405060708D4
:00000001FF
'''

    import sys
    h = IHexFile()
    h.vsParse( file(sys.argv[1], 'rb').read() )
    #print h.tree()

    for addr,perms,fname,bytes in h.getMemoryMaps():
        print '0x%.8x: %r' % ( addr, bytes )

    print h.getEntryPoint()
