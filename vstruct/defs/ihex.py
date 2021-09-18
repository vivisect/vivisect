'''
Parser objects for the Intel Hex file format.
'''
import binascii

import envi.const as e_const

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
        self.startcode      = v_str(1)
        self.bytecount      = v_str(2)
        self.address        = v_str(4)
        self.recordtype     = v_str(2)
        self.data           = v_str(0)
        self.csum           = v_str(2)

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
        return binascii.unhexlify(self.data)

class IHexFile(vstruct.VArray):

    def vsParse(self, bytes, offset=0):

        lines = bytes[offset:].splitlines()

        for line in lines:
            offset += 1 # there is an eaten newline for each
            if not line:
                continue

            try:
                c = IHexChunk()
                c.vsParse( line )
                offset += len( c )

                self.vsAddElement( c )
            except Exception as e:
                logger.warning("Exception parsing: %r", e)

            if int(c.recordtype, 16) == IHEX_REC_EOF:
                break

        return offset

    def vsEmit(self, fast=False):
        """
        Get back the byte sequence associated with this structure.
        """
        if fast:
            if self._vs_fastfields is None:
                self._vsInitFastFields()
            ffvals = [ ff.vsGetValue() for ff in self._vs_fastfields ]
            return struct.pack(self._vs_fastfmt, *ffvals)

        ret = b''
        for fname, fobj in self.vsGetFields():
            ret += fobj.vsEmit() + b'\r\n'
        return ret.decode('utf-8')


    def getEntryPoints(self):
        '''
        If a 32bit linear start address is defined for this file,
        return it.  Returns None if the 32bit entry point extension
        is not present.
        '''
        evas = []
        for fname, chunk in self:
            ctype = int( chunk.recordtype, 16 )

            if ctype == IHEX_REC_STARTLINADDR:
                evas.append(int( chunk.data, 16 ))

            elif ctype == IHEX_REC_STARTSEG:
                startcs = int( chunk.data, 16 ) >> 16
                startip = int( chunk.data, 16 ) & 0xffff
                evas.append((startcs << 4) | startip)

        return evas

    def getMemoryMaps(self):
        '''
        Retrieve a set of memory maps defined by this hex file.

        Memory maps are returned as a list of
        ( va, perms, fname, bytes ) tuples.
        '''
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

            if ctype == IHEX_REC_STARTSEG:
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
                maps.append( [ addr, e_const.MM_RWX, '', bytes ] )

        return maps
