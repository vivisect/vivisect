
import vstruct
import vstruct.defs.inet as vs_inet

from vstruct.primitives import *

PCAP_LINKTYPE_ETHER     = 1
PCAP_LINKTYPE_RAW       = 101

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

def iterPcapFileName(filename, reuse=False):
    fd = file(filename, 'rb')
    for x in iterPcapFile(fd, reuse=reuse):
        yield x
    
def iterPcapFile(fd, reuse=False):

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

        #print eII.tree()
        if not reuse:
            ipv4 = vs_inet.IPv4()

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
            pass
            #print 'UNHANDLED IP PROTOCOL: %d' % ipv4.proto

