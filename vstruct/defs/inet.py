'''
Datalink / Network / Transport layer headers
'''
import string
import socket
import struct

import vstruct
from vstruct.primitives import *

ETH_P_IP    = 0x0800
ETH_P_ARP   = 0x0806
ETH_P_IPv6  = 0x86dd
ETH_P_VLAN  = 0x8100

IPPROTO_ICMP    = 1
IPPROTO_TCP     = 6
IPPROTO_UDP     = 17
IPPROTO_IPV6    = 41
IPPROTO_GRE     = 47
IPPROTO_ICMP6   = 58

TCP_F_FIN  = 0x01
TCP_F_SYN  = 0x02
TCP_F_RST  = 0x04
TCP_F_PUSH = 0x08
TCP_F_ACK  = 0x10
TCP_F_URG  = 0x20
TCP_F_ECE  = 0x40
TCP_F_CWR  = 0x80

# Useful combinations...
TCP_F_SYNACK = (TCP_F_SYN | TCP_F_ACK)

ICMP_ECHOREPLY        =  0
ICMP_DEST_UNREACH     =  3
ICMP_SOURCE_QUENCH    =  4
ICMP_REDIRECT         =  5
ICMP_ECHO             =  8
ICMP_TIME_EXCEEDED    = 11
ICMP_PARAMETERPROB    = 12
ICMP_TIMESTAMP        = 13
ICMP_TIMESTAMPREPLY   = 14
ICMP_INFO_REQUEST     = 15
ICMP_INFO_REPLY       = 16
ICMP_ADDRESS          = 17
ICMP_ADDRESSREPLY     = 18


GREPROTO_PPTP = 0x880b

def reprIPv4Addr(addr):
    bytes = struct.pack('>I', addr)
    return socket.inet_ntoa(bytes)

def decIPv4Addr(addrstr):
    bytes = socket.inet_aton(addrstr)
    return struct.unpack('>I', bytes)[0]

def reprIPv6Addr(addr):
    return socket.inet_ntop(socket.AF_INET6, addr)

class IPv4Address(v_uint32):

    def __init__(self, value=0):
        v_uint32.__init__(self, value=value, bigend=True)

    def __repr__(self):
        bytes = struct.pack('>I', self._vs_value)
        return socket.inet_ntop(socket.AF_INET, bytes)

class IPv6Address(v_bytes):

    def __init__(self, value=0):
        v_bytes.__init__(self, size=16)

    def __repr__(self):
        return socket.inet_ntop(socket.AF_INET6, self._vs_value)

    def vsSetValue(self, val):
        if all(c in string.printable for c in val):
            val = socket.inet_pton(socket.AF_INET6, val)
        if len(val) != self._vs_length:
            raise Exception('v_bytes field set to wrong length!')
        self._vs_value = val

class ETHERII(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.destmac    = v_bytes(size=6)
        self.srcmac     = v_bytes(size=6)
        self.etype      = v_uint16(bigend=True)

    def vsParse(self, sbytes, offset=0, fast=False):
        if fast:
            return vstruct.VStruct.vsParse(self, sbytes, offset=offset, fast=fast)
        # If we end up with a vlan tag, reparse
        ret = vstruct.VStruct.vsParse(self, sbytes, offset=offset)
        if self.etype == ETH_P_VLAN:
            self.vsInsertField('vtag', v_uint16(bigend=True), 'etype')
            self.vsInsertField('vlan', v_uint16(bigend=True), 'etype')
            ret = vstruct.VStruct.vsParse(self, sbytes, offset=offset)
        return ret

class ETHERIIVLAN(ETHERII):
    def __init__(self):
        ETHERII.__init__(self)
        self.vsInsertField('vtag', v_uint16(bigend=True), 'etype')
        self.vsInsertField('vlan', v_uint16(bigend=True), 'etype')

class IPv4(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.veriphl    = v_uint8()
        self.tos        = v_uint8()
        self.totlen     = v_uint16(bigend=True)
        self.ipid       = v_uint16(bigend=True)
        self.flagfrag   = v_uint16(bigend=True)
        self.ttl        = v_uint8()
        self.proto      = v_uint8()
        self.cksum      = v_uint16(bigend=True)
        self.srcaddr    = IPv4Address()
        self.dstaddr    = IPv4Address()

    # Make our len over-ride
    def __len__(self):
        if self.veriphl == 0:
            return vstruct.VStruct.__len__(self)
        return (self.veriphl & 0x0f) * 4

class IPv6(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.verclsflowl= v_uint32(bigend=True)
        self.totlen     = v_uint16(bigend=True)
        self.nexthdr    = v_uint8()
        self.hoplimit   = v_uint8()
        self.srcaddr    = IPv6Address()
        self.dstaddr    = IPv6Address()

class TCP(vstruct.VStruct):

    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.srcport    = v_uint16(bigend=True)
        self.dstport    = v_uint16(bigend=True)
        self.sequence   = v_uint32(bigend=True)
        self.ackseq     = v_uint32(bigend=True)
        self.doff       = v_uint8()
        self.flags      = v_uint8()
        self.window     = v_uint16(bigend=True)
        self.checksum   = v_uint16(bigend=True)
        self.urgent     = v_uint16(bigend=True)

    def __len__(self):
        if self.doff == 0:
            return vstruct.VStruct.__len__(self)
        return self.doff >> 2

class UDP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.srcport    = v_uint16(bigend=True)
        self.dstport    = v_uint16(bigend=True)
        self.udplen     = v_uint16(bigend=True)
        self.checksum   = v_uint16(bigend=True)

class ICMP(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.type       = v_uint8()
        self.code       = v_uint8()
        self.checksum   = v_uint16(bigend=True)
        #union field starting at offset 4 not included here
