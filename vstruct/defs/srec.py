'''
Parser objects for the SRECORD file format.
'''
import binascii

import vstruct
from vstruct.primitives import *

S0_HEADER = 0
S1_DATA = 1
S2_DATA = 2
S3_DATA = 3
S4_RESERVED = 4
S5_COUNT = 5
S6_COUNT = 6
S7_STARTADDR = 7
S8_STARTADDR = 8
S9_STARTADDR = 9


class SRecChunk(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.startcode      = v_str(1)
        self.recordtype     = v_str(1)
        self.bytecount      = v_str(2)
        self.address        = v_str(4)
        self.data           = v_str(0)
        self.csum           = v_str(2)

    def pcb_bytecount(self):
        dsize = int(self.bytecount, 16) 
        dsize -= int(len(self.vsGetField('address')) // 2)
        dsize -= 1  # csum
        self.vsGetField('data').vsSetLength( 2 * dsize )

    def pcb_recordtype(self):
        rtype = int(self.recordtype, 16)
        if rtype in (S1_DATA, S9_STARTADDR):
            self.vsGetField('address').vsSetLength(4)
        elif rtype in (S2_DATA, S8_STARTADDR):
            self.vsGetField('address').vsSetLength(6)
        elif rtype in (S3_DATA, S7_STARTADDR):
            self.vsGetField('address').vsSetLength(8)

    def getAddress(self):
        '''
        Parse the address field and return the int type.
        '''
        return int( self.address, 16 )

    def getData(self):
        '''
        Return the binary data payload for this chunk.
        '''
        return binascii.unhexlify(self.data)

class SRecFile(vstruct.VArray):

    def vsParse(self, bytes, offset=0):

        lines = bytes[offset:].splitlines()

        for line in lines:
            offset += 1 # there is an eaten newline for each
            if not line:
                continue

            c = SRecChunk()
            c.vsParse( line )
            offset += len( c )

            self.vsAddElement( c )

            #if int(c.recordtype, 16) in (S7_STARTADDR, S8_STARTADDR, S9_STARTADDR):
            #    break

        return offset

    def getEntryPoint(self):
        '''
        If a 32bit linear start address is defined for this file,
        return it.  Returns None if the 32bit entry point extension
        is not present.
        '''
        for fname, chunk in self:
            ctype = int( chunk.recordtype, 16 )
            if ctype in (S7_STARTADDR, S8_STARTADDR, S9_STARTADDR):
                return int( chunk.address, 16 )

    def getMemoryMaps(self):
        '''
        Retrieve a set of memory maps defined by this hex file.

        Memory maps are returned as a list of
        ( va, perms, fname, bytes ) tuples.
        '''
        import envi.memory as e_mem

        # Get all the binary parts....
        memparts = []

        for fname, chunk in self:

            ctype = int( chunk.recordtype, 16 )
            print fname, chunk.tree(), ctype

            if ctype in (S1_DATA, S2_DATA, S3_DATA):
                addr = chunk.getAddress()
                memparts.append( (addr, chunk.getData()) )
                continue

            elif ctype in (S7_STARTADDR, S8_STARTADDR, S9_STARTADDR):
                continue

            elif ctype in (S5_COUNT, S6_COUNT):
                continue

            elif ctype == S0_HEADER:
                print("HEADER: %r" % chunk.data)
                continue

            raise Exception('Unhandled SREC chunk: %s' % chunk.recordtype)

        memparts.sort()

        maps = []
        for addr, bytes in memparts:
            # is this the next contiguous chunk?
            if maps and addr == ( maps[-1][0] + len(maps[-1][3]) ):
                maps[-1][3] += bytes
            else:
                maps.append( [ addr, e_mem.MM_RWX, '', bytes ] )

        return maps

