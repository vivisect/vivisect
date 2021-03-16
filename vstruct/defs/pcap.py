import logging

import vstruct
import vstruct.defs.inet as vs_inet

from vstruct.primitives import *

logger = logging.getLogger(__name__)

PCAP_LINKTYPE_ETHER     = 1
PCAP_LINKTYPE_RAW       = 101
PCAP_LINKTYPE_LINUX_SLL = 113
PCAP_DLT_RAW            = 12

PCAPNG_BOM              = 0x1A2B3C4D
OPT_ENDOFOPT            = 0
OPT_COMMENT             = 1

#PCAPNG_BLOCKTYPE_SECTION_HEADER options
OPT_SHB_HARDWARE        = 2
OPT_SHB_OS              = 3
OPT_SHB_USERAPPL        = 4

#PCAPNG_INTERFACE_DESCRIPTION_BLOCK options
OPT_IF_NAME             = 2
OPT_IF_DESCRIPTION      = 3
OPT_IF_IPV4ADDR         = 4
OPT_IF_IPV6ADDR         = 5
OPT_IF_MACADDR          = 6
OPT_IF_EUIADDR          = 7
OPT_IF_SPEED            = 8
OPT_IF_TSRESOL          = 9
OPT_IF_TZONE            = 10
OPT_IF_FILTER           = 11
OPT_IF_OS               = 12
OPT_IF_FCSLEN           = 13
OPT_IF_TSOFFSET         = 14

# options for PCAPNG_ENHANCED_PACKET_BLOCK
OPT_EPB_FLAGS           = 2
OPT_EPB_HASH            = 3
OPT_EPB_DROPCOUNT       = 4

# values used in the blocktype field
PCAPNG_BLOCKTYPE_INTERFACE_DESCRIPTION      = 0x00000001
PCAPNG_BLOCKTYPE_PACKET                     = 0x00000002
PCAPNG_BLOCKTYPE_SIMPLE_PACKET              = 0x00000003
PCAPNG_BLOCKTYPE_NAME_RESOLUTION            = 0x00000004
PCAPNG_BLOCKTYPE_INTERFACE_STATS            = 0x00000005
PCAPNG_BLOCKTYPE_ENHANCED_PACKET            = 0x00000006
PCAPNG_BLOCKTYPE_SECTION_HEADER             = 0x0a0d0d0a

def pad4bytes(size):
    if (size % 4) == 0:
        return size
    return size + (4 -( size % 4))

class PCAP_FILE_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.magic      = v_uint32()
        self.vers_maj   = v_uint16()
        self.vers_min   = v_uint16()
        self.thiszone   = v_uint32()
        self.sigfigs    = v_uint32()
        self.snaplen    = v_uint32()
        self.linktype   = v_uint32()

class PCAP_PACKET_HEADER(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.tvsec      = v_uint32()
        self.tvusec     = v_uint32()
        self.caplen     = v_uint32()
        self.len        = v_uint32()

class PCAPNG_GENERIC_BLOCK_HEADER(vstruct.VStruct):
    '''
    Used to read the block type & size when parsing the file
    '''
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.blocktype      = v_uint32(bigend=bigend)
        self.blocksize      = v_uint32(bigend=bigend)

class PCAPNG_BLOCK_PARENT(vstruct.VStruct):
    '''
    Used to inherit the weird parsing style where there's variable length
    options at the end, followed by the duplicate block total length
    '''
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        #non-vstruct field, set during checking BOM
        self.bigend         = False

    def vsParse(self, bytez, offset=0):
        startoff = offset
        roff = vstruct.VStruct.vsParse(self, bytez, offset=offset)
        #(blocksize-4): because we still need the trailing blocksize2
        # apparently blocks can completely omit the options list and not
        # even have the OPT_ENDOFOPT entry
        while (roff < len(bytez)) and ((roff-startoff) < (self.blocksize-4)):
            opt = PCAPNG_OPTION(bigend=self.bigend)
            roff = opt.vsParse(bytez, roff)
            if opt.code == OPT_ENDOFOPT:
                break
            self.options.vsAddElement(opt)
        # append trailing blocksize2
        bs2 = v_uint32(bigend=self.bigend)
        self.vsAddField('blocksize2', bs2)
        roff = bs2.vsParse(bytez, roff)
        #pad, plus we skip
        return pad4bytes(roff)


class PCAPNG_SECTION_HEADER_BLOCK(PCAPNG_BLOCK_PARENT):
    def __init__(self, bigend=False):
        PCAPNG_BLOCK_PARENT.__init__(self, bigend)
        self.blocktype      = v_uint32(bigend=bigend)
        self.blocksize      = v_uint32(bigend=bigend)
        self.bom            = v_uint32(bigend=bigend)
        self.vers_maj       = v_uint16(bigend=bigend)
        self.vers_min       = v_uint16(bigend=bigend)
        self.sectionsize    = v_uint64(bigend=bigend)
        self.options        = vstruct.VArray([])
        #blocksize2: dynamcally added in vsParse()
        #self.blocksize2     = v_uint32(bigend=bigend)

    def pcb_bom(self):
        bom = self.vsGetField('bom')
        if  self.bom == PCAPNG_BOM:
            #if it matches, then the endian of bom is correct
            self.bigend = bom._vs_bigend
        else:
            self.bigend = not bom._vs_bigend

class PCAPNG_OPTION(vstruct.VStruct):
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.code           = v_uint16(bigend=bigend)
        self.optsize        = v_uint16(bigend=bigend)
        self.bytes          = v_bytes(0)

    def pcb_optsize(self):
        size = pad4bytes(self.optsize)
        self.vsGetField('bytes').vsSetLength(size)

class PCAPNG_INTERFACE_DESCRIPTION_BLOCK(PCAPNG_BLOCK_PARENT):
    def __init__(self, bigend=False):
        PCAPNG_BLOCK_PARENT.__init__(self, bigend)
        self.blocktype      = v_uint32(bigend=bigend)
        self.blocksize      = v_uint32(bigend=bigend)
        self.linktype       = v_uint16(bigend=bigend)
        self.reserved       = v_uint16(bigend=bigend)
        self.snaplen        = v_uint32(bigend=bigend)
        self.options        = vstruct.VArray([])
        #blocksize2: dynamcally added in vsParse()
        #self.blocksize2     = v_uint32(bigend=bigend)

    def vsParse(self, bytez, offset=0):
        '''
        We need the tsresol value to adjust timestamp values, so pull it
        out here
        '''
        ret = PCAPNG_BLOCK_PARENT.vsParse(self, bytez, offset=0)
        self.tsresol = None
        #default offset is 0
        self.tsoffset = 0
        #sys.stderr.write('PCAPNG_INTERFACE_DESCRIPTION_BLOCK: searching options')
        for i, opt in self.options:
            if opt.code == OPT_IF_TSRESOL:
                self.tsresol = ord(opt.bytes[0])
                #sys.stderr.write('Got tsresol: 0x%x\n' % self.tsresol)
            elif opt.code == OPT_IF_TSOFFSET:
                fmt = '<Q'
                if self.bigend:
                    fmt = '>Q'
                self.tsoffset = struct.unpack_from(fmt, opt.bytes)[0]
                #sys.stderr.write('Got tsoffset: 0x%x\n' % self.tsoffset)
        return ret

class PCAPNG_ENHANCED_PACKET_BLOCK(PCAPNG_BLOCK_PARENT):
    def __init__(self, bigend=False):
        PCAPNG_BLOCK_PARENT.__init__(self, bigend)
        self.blocktype      = v_uint32(bigend=bigend)
        self.blocksize      = v_uint32(bigend=bigend)
        self.interfaceid    = v_uint32(bigend=bigend)
        self.tstamphi       = v_uint32(bigend=bigend)
        self.tstamplow      = v_uint32(bigend=bigend)
        self.caplen         = v_uint32(bigend=bigend)
        self.packetlen      = v_uint32(bigend=bigend)
        self.data           = v_bytes(0)
        self.options        = vstruct.VArray([])
        #blocksize2: dynamcally added in vsParse()
        #self.blocksize2     = v_uint32(bigend=bigend)

    def pcb_caplen(self):
        size = pad4bytes(self.caplen)
        self.vsGetField('data').vsSetLength(size)

    def setPcapTimestamp(self, idb):
        '''
        Adds a libpcap compatible tvsec and tvusec fields, based on the pcapng timestamp
        '''
        #orange left off here
        self.snaplen = idb.snaplen

        tstamp = (self.tstamphi << 32) | self.tstamplow
        scale = 1000000
        if idb.tsresol is None:
            #if not set, capture assumes 10e-6 resolution
            pass
        elif (0x80 & idb.tsresol) == 0:
            # remaining bits are resolution, to a negative power of 10
            scale = 10**(idb.tsresol & 0x7f)
        else:
            # remaining bits are resolution, to a negative power of 2
            scale = 1 << (idb.tsresol & 0x7f)

        self.tvsec = (tstamp / scale) + idb.tsoffset
        self.tvusec = tstamp % scale


class PCAPNG_SIMPLE_PACKET_BLOCK(vstruct.VStruct):
    '''
    Note: no variable length options fields, so inheriting from vstruct directly
    '''
    def __init__(self, bigend=False):
        vstruct.VStruct.__init__(self)
        self.blocktype      = v_uint32(bigend=bigend)
        self.blocksize      = v_uint32(bigend=bigend)
        self.packetlen      = v_uint32(bigend=bigend)
        self.data           = v_bytes(0)
        self.blocksize2     = v_uint32(bigend=bigend)

    def pcb_blocksize(self):
        self.caplen = pad4bytes(self.blocksize - 16)
        self.vsGetField('data').vsSetLength(self.caplen)

    def setPcapTimestamp(self, idb):
        #no timestamp in this type of block :(
        self.tvsec = idb.tsoffset
        self.tvusec = 0

def iterPcapFileName(filename, reuse=False):
    with open(filename, 'rb') as fd:
        for x in iterPcapFile(fd, reuse=reuse):
            yield x

def iterPcapFile(fd, reuse=False):
    '''
    Figure out if it's a tcpdump format, or pcapng
    '''
    h = PCAP_FILE_HEADER()
    b = fd.read(len(h))
    h.vsParse(b, fast=True)
    fd.seek(0)
    if h.magic == PCAPNG_BLOCKTYPE_SECTION_HEADER:
        return _iterPcapNgFile(fd, reuse)
    return _iterPcapFile(fd, reuse)

def _iterPcapFile(fd, reuse=False):

    h = PCAP_FILE_HEADER()
    b = fd.read(len(h))
    h.vsParse(b, fast=True)

    linktype = h.linktype

    if linktype not in (PCAP_LINKTYPE_ETHER, PCAP_LINKTYPE_RAW):
        raise Exception('PCAP Link Type %d Not Supported Yet!' % linktype)

    pkt = PCAP_PACKET_HEADER()
    eII = vs_inet.ETHERII()

    pktsize = len(pkt)
    eIIsize = len(eII)

    ipv4 = vs_inet.IPv4()
    ipv4size = 20
    tcp_hdr = vs_inet.TCP()
    udp_hdr = vs_inet.UDP()
    icmp_hdr = vs_inet.ICMP()

    go = True
    while go:

        hdr = fd.read(pktsize)
        if len(hdr) != pktsize:
            break

        pkt.vsParse(hdr, fast=True)

        b = fd.read(pkt.caplen)

        offset = 0

        if linktype == PCAP_LINKTYPE_ETHER:

            if len(b) < eIIsize:
                continue

            eII.vsParse(b, 0, fast=True)

            # No support for non-ip protocol yet...
            if eII.etype not in (vs_inet.ETH_P_IP,vs_inet.ETH_P_VLAN):
                continue

            offset += eIIsize

            if eII.etype == vs_inet.ETH_P_VLAN:
                offset +=  4

        elif linktype == PCAP_LINKTYPE_RAW:
            pass

        if not reuse:
            ipv4 = vs_inet.IPv4()

        if (len(b) - offset) < ipv4size:
            continue

        ipv4.vsParse(b, offset, fast=True)

        # Make b *only* the IP datagram bytes...
        b = b[offset:offset+ipv4.totlen]

        offset = 0
        offset += len(ipv4)
        tsize = len(b) - offset

        if ipv4.proto == vs_inet.IPPROTO_TCP:

            if tsize < 20:
                continue

            if not reuse:
                tcp_hdr = vs_inet.TCP()

            tcp_hdr.vsParse(b, offset, fast=True)
            offset += len(tcp_hdr)
            pdata = b[offset:]

            yield pkt,ipv4,tcp_hdr,pdata

        elif ipv4.proto == vs_inet.IPPROTO_UDP:

            if tsize < 8:
                continue

            if not reuse:
                udp_hdr = vs_inet.UDP()

            udp_hdr.vsParse(b, offset, fast=True)
            offset += len(udp_hdr)
            pdata = b[offset:]

            yield pkt,ipv4,udp_hdr,pdata

        elif ipv4.proto == vs_inet.IPPROTO_ICMP:
            if tsize < 4:
                continue

            if not reuse:
                icmp_hdr = vs_inet.ICMP()

            icmp_hdr.vsParse(b, offset, fast=True)
            offset += len(icmp_hdr)
            pdata = b[offset:]

            yield pkt,ipv4,icmp_hdr,pdata

        else:
            logger.warning('UNHANDLED IP PROTOCOL: %d', ipv4.proto)


def _iterPcapNgFile(fd, reuse=False):
    header = PCAPNG_GENERIC_BLOCK_HEADER()
    ifaceidx = 0
    ifacedict = {}
    roff = 0
    bigend = False
    curroff = fd.tell()
    b0 = fd.read(len(header))
    fd.seek(curroff)
    while len(b0) == len(header):
        header.vsParse(b0, fast=True)
        body = fd.read(header.blocksize)
        if header.blocktype == PCAPNG_BLOCKTYPE_SECTION_HEADER:
            shb = PCAPNG_SECTION_HEADER_BLOCK()
            roff = shb.vsParse(body)
            bigend = shb.bigend
            #reset interface stuff since we're in a new section
            ifaceidx = 0
            ifacedict = {}
        elif header.blocktype == PCAPNG_BLOCKTYPE_INTERFACE_DESCRIPTION:
            idb = PCAPNG_INTERFACE_DESCRIPTION_BLOCK(bigend)
            roff = idb.vsParse(body)
            #save off the interface for later reference
            ifacedict[ifaceidx] = idb
            ifaceidx += 1
        elif header.blocktype == PCAPNG_BLOCKTYPE_SIMPLE_PACKET:
            spb = PCAPNG_SIMPLE_PACKET_BLOCK(bigend)
            roff = spb.vsParse(body)
            tup = _parsePcapngPacketBytes(iface.linktype, spb)
            if tup is not None:
                #if it is None, just fall through & read next block
                yield tup
        elif header.blocktype == PCAPNG_BLOCKTYPE_ENHANCED_PACKET:
            epb = PCAPNG_ENHANCED_PACKET_BLOCK(bigend)
            roff = epb.vsParse(body)
            iface = ifacedict.get(epb.interfaceid)
            epb.setPcapTimestamp(iface)
            tup = _parsePcapngPacketBytes(iface.linktype, epb)
            if tup is not None:
                #if tup is None, just fall through & read next block
                yield tup

            #TODO: other blocks needed?
            #PCAPNG_BLOCKTYPE_PACKET (obsolete)
            #PCAPNG_BLOCKTYPE_NAME_RESOLUTION:
            #PCAPNG_BLOCKTYPE_INTERFACE_STATS:
        else:
            logger.warning('Unknown block type: 0x%08x: 0x%08x 0x%08x bytes', roff, header.blocktype, header.blocksize)
        curroff = fd.tell()
        b0 = fd.read(len(header))
        fd.seek(curroff)

def _parsePcapngPacketBytes(linktype, pkt):
    '''
    pkt is either a parsed PCAPNG_SIMPLE_PACKET_BLOCK or PCAPNG_ENHANCED_PACKET_BLOCK
    On success Returns tuple (pcapng_pkt, ipv4_vstruct, transport_vstruc, pdata)
    Returns None if the packet can't be parsed
    '''
    if linktype not in (PCAP_LINKTYPE_ETHER, PCAP_LINKTYPE_RAW):
        raise Exception('PCAP Link Type %d Not Supported Yet!' % linktype)

    #pkt = PCAP_PACKET_HEADER()
    eII = vs_inet.ETHERII()
    eIIsize = len(eII)

    offset = 0
    if linktype == PCAP_LINKTYPE_ETHER:
        if len(pkt.data) < eIIsize:
            return None
        eII.vsParse(pkt.data, 0, fast=True)
        # No support for non-ip protocol yet...
        if eII.etype not in (vs_inet.ETH_P_IP,vs_inet.ETH_P_VLAN):
            return None
        offset += eIIsize
        if eII.etype == vs_inet.ETH_P_VLAN:
            offset +=  4
    elif linktype == PCAP_LINKTYPE_RAW:
        pass

    ipv4 = vs_inet.IPv4()
    if (len(pkt.data) - offset) < len(ipv4):
        return None
    ipv4.vsParse(pkt.data, offset, fast=True)

    # Make b *only* the IP datagram bytes...
    b = pkt.data[offset:offset+ipv4.totlen]

    offset = 0
    offset += len(ipv4)
    tsize = len(b) - offset

    if ipv4.proto == vs_inet.IPPROTO_TCP:
        if tsize < 20:
            return None
        tcp_hdr = vs_inet.TCP()
        tcp_hdr.vsParse(b, offset, fast=True)
        offset += len(tcp_hdr)
        pdata = b[offset:]
        return pkt,ipv4,tcp_hdr,pdata
    elif ipv4.proto == vs_inet.IPPROTO_UDP:
        if tsize < 8:
            return None
        udp_hdr = vs_inet.UDP()
        udp_hdr.vsParse(b, offset, fast=True)
        offset += len(udp_hdr)
        pdata = b[offset:]
        return pkt,ipv4,udp_hdr,pdata
    elif ipv4.proto == vs_inet.IPPROTO_ICMP:
        if tsize < 4:
            return None
        icmp_hdr = vs_inet.ICMP()
        icmp_hdr.vsParse(b, offset, fast=True)
        offset += len(icmp_hdr)
        pdata = b[offset:]
        return pkt,ipv4,icmp_hdr,pdata
    else:
        logger.warning('UNHANDLED IP PROTOCOL: %d', ipv4.proto)
    return None
